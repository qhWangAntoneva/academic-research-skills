"""
P1-1: Adaptive Tolerance Calibration Sweep

Sweeps h_crit_tolerance values using CBVIndex (no spectral embedding, fast)
across the benchmark suite to find empirically optimal tolerance parameters.

Usage:
    uv run python scripts/paper-10/calibration/tolerance_sweep.py
"""
import sys, os, warnings
os.environ['PYTHONWARNINGS'] = 'ignore'
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import time
from pathlib import Path

from cbv.index import CBVIndex
from benchmark import SyntheticDataGenerator, RealDataLoader

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

K_RANGE = (2, 10)
N_BOOT = 10


def build_datasets():
    gen = SyntheticDataGenerator(random_state=42)
    synthetic = gen.generate_benchmark_suite()
    loader = RealDataLoader()
    real = loader.load_all(include_seeds=True)
    return synthetic + real


def evaluate_cbvindex(datasets, tolerance, seed=42):
    """Run CBVIndex with given tolerance on all datasets. Return metrics."""
    n_total = len(datasets)
    correct = 0
    abs_errors = []
    plus1_correct = 0

    for ds in datasets:
        X = ds['X']
        k_true = ds['k_true']

        idx = CBVIndex(
            k_range=K_RANGE, n_boot=N_BOOT, random_state=seed,
            h_crit_tolerance=tolerance, mode='threshold',
            vote_method='weighted_mean',
        )
        try:
            idx.fit(X)
            k_hat = idx.predict()
        except Exception:
            k_hat = -1

        if k_hat == k_true:
            correct += 1
        err = abs(k_hat - k_true)
        abs_errors.append(err)
        if err <= 1:
            plus1_correct += 1

    accuracy = correct / n_total
    mae = float(np.mean(abs_errors))
    plus1_acc = plus1_correct / n_total
    return accuracy, mae, plus1_acc


def _eval_tolerance(args):
    """Wrapper for parallel job."""
    datasets, tol, seed = args
    warnings.filterwarnings('ignore')
    acc, mae, p1 = evaluate_cbvindex(datasets, tol, seed)
    return tol, acc, mae, p1


def main():
    log = lambda msg: print(f'[{time.strftime("%H:%M:%S")}] {msg}')

    log('=' * 60)
    log('P1-1: Adaptive Tolerance Calibration Sweep (CBVIndex, fast)')
    log('=' * 60)

    log('\n[1/4] Building datasets...')
    datasets = build_datasets()
    log(f'  Total: {len(datasets)}')

    log('\n[2/4] Global tolerance sweep...')
    tolerances = [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.5, 2.0, 3.0]

    try:
        from joblib import Parallel, delayed
        args = [(datasets, t, 42) for t in tolerances]
        results = Parallel(n_jobs=-1, verbose=10)(
            delayed(_eval_tolerance)(a) for a in args
        )
    except ImportError:
        results = [_eval_tolerance((datasets, t, 42)) for t in tolerances]

    rows = []
    for tol, acc, mae, p1 in results:
        rows.append({
            'tolerance': tol, 'mode': 'fixed',
            'accuracy': acc, 'mae': mae, 'plus1_acc': p1,
        })
        log(f'  tol={tol:.2f}: acc={acc:.1%}, MAE={mae:.3f}, ±1={p1:.1%}')

    log('\n[3/4] Dim-bucket analysis...')
    buckets = {}
    for ds in datasets:
        nf = ds['X'].shape[1]
        b = 'low(2-5)' if nf <= 5 else ('med(6-20)' if nf <= 20 else 'high(>20)')
        buckets.setdefault(b, []).append(ds)
    log(f'  Buckets: { {k: len(v) for k, v in buckets.items()} }')

    dim_args = []
    for bname, bds in buckets.items():
        for t in tolerances:
            dim_args.append((bds, t, 42))

    try:
        from joblib import Parallel, delayed
        dim_results = Parallel(n_jobs=-1, verbose=5)(
            delayed(_eval_tolerance)(a) for a in dim_args
        )
    except ImportError:
        dim_results = [_eval_tolerance(a) for a in dim_args]

    dim_rows = []
    idx = 0
    for bname, bds in buckets.items():
        n = len(bds)
        for t in tolerances:
            _, acc, mae, p1 = dim_results[idx]
            dim_rows.append({
                'bucket': bname, 'tolerance': t,
                'accuracy': acc, 'mae': mae, 'plus1_acc': p1, 'n_datasets': n,
            })
            idx += 1

    dim_df = pd.DataFrame(dim_rows)
    log('\n  Best per bucket:')
    for bname in sorted(buckets):
        sub = dim_df[dim_df['bucket'] == bname]
        best = sub.loc[sub['accuracy'].idxmax()]
        log(f'    {bname}: tol={best["tolerance"]:.2f}, acc={best["accuracy"]:.1%}, MAE={best["mae"]:.3f}')

    log('\n[4/4] Adaptive formula evaluation...')
    acc_adapt, mae_adapt, p1_adapt = evaluate_cbvindex(datasets, 1.1, 42)
    rows.append({
        'tolerance': -1, 'mode': 'adaptive_orig',
        'accuracy': acc_adapt, 'mae': mae_adapt, 'plus1_acc': p1_adapt,
    })
    log(f'  adaptive (current): acc={acc_adapt:.1%}, MAE={mae_adapt:.3f}, ±1={p1_adapt:.1%}')

    # ── Save ──
    df = pd.DataFrame(rows)
    path = RESULTS_DIR / 'tolerance_sweep_cbvindex.csv'
    with open(str(path), 'w', encoding='utf-8') as f:
        df.to_csv(f, index=False)
    log(f'\nSaved to {path}')

    dim_path = RESULTS_DIR / 'tolerance_sweep_dim_buckets.csv'
    with open(str(dim_path), 'w', encoding='utf-8') as f:
        dim_df.to_csv(f, index=False)

    # ── Summary ──
    fixed = df[df['mode'] == 'fixed'].sort_values('accuracy', ascending=False)
    log('\n' + '=' * 60)
    log('SUMMARY')
    log('=' * 60)
    log(f'Best fixed: tol={fixed.iloc[0]["tolerance"]:.2f}, '
        f'acc={fixed.iloc[0]["accuracy"]:.1%}, MAE={fixed.iloc[0]["mae"]:.3f}, '
        f'±1={fixed.iloc[0]["plus1_acc"]:.1%}')
    log(f'Adaptive:   acc={acc_adapt:.1%}, MAE={mae_adapt:.3f}, ±1={p1_adapt:.1%}')
    base = fixed[fixed['tolerance'] == 1.1]
    if len(base) > 0:
        log(f'Baseline:   tol=1.10, acc={base.iloc[0]["accuracy"]:.1%}, '
            f'MAE={base.iloc[0]["mae"]:.3f}, ±1={base.iloc[0]["plus1_acc"]:.1%}')


if __name__ == '__main__':
    main()
