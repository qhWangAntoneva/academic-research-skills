"""
P1-10: Weighting Scheme Sensitivity Analysis

Compares CBVHybrid accuracy across the three weight methods:
  - excess_mass (default)
  - bimodality_strength (legacy)
  - hybrid (geometric mean)

Usage:
    uv run python scripts/paper-10/calibration/weight_sensitivity.py
"""
import sys, os, warnings
os.environ['PYTHONWARNINGS'] = 'ignore'
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import time
from pathlib import Path

from cbv import CBVHybrid
from benchmark import SyntheticDataGenerator, RealDataLoader

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

K_RANGE = (2, 10)
N_BOOT = 10
SEED = 42
METHODS = ['excess_mass', 'bimodality_strength', 'hybrid']


def build_datasets():
    gen = SyntheticDataGenerator(random_state=SEED)
    synthetic = gen.generate_benchmark_suite()
    loader = RealDataLoader()
    real = loader.load_all(include_seeds=True)
    return synthetic + real


def evaluate(method, datasets):
    n = len(datasets)
    correct = 0
    abs_errors = []
    plus1 = 0

    for ds in datasets:
        X = ds['X']
        k_true = ds['k_true']
        cbv = CBVHybrid(
            k_range=K_RANGE, n_boot=N_BOOT, random_state=SEED,
            mode='threshold', vote_method='mode',
            use_excess_mass=False, adaptive_tolerance=False,
            weight_method=method,
        )
        try:
            cbv.fit(X)
            k_hat = cbv.predict()
        except Exception:
            k_hat = -1

        if k_hat == k_true:
            correct += 1
        err = abs(k_hat - k_true)
        abs_errors.append(err)
        if err <= 1:
            plus1 += 1

    return correct / n, float(np.mean(abs_errors)), plus1 / n


def main():
    log = lambda msg: print(f'[{time.strftime("%H:%M:%S")}] {msg}')

    log('=' * 60)
    log('P1-10: Weighting Scheme Sensitivity Analysis')
    log('=' * 60)

    log('\nBuilding datasets...')
    datasets = build_datasets()
    log(f'  Total: {len(datasets)}')

    log('\nRunning CBVHybrid with each weight method...')
    results = {}
    for method in METHODS:
        t0 = time.time()
        acc, mae, p1 = evaluate(method, datasets)
        elapsed = time.time() - t0
        results[method] = {'accuracy': acc, 'mae': mae, 'plus1_acc': p1}
        log(f'  {method:22s}: acc={acc:.1%}, MAE={mae:.3f}, ±1={p1:.1%} ({elapsed:.1f}s)')

    # Compute deltas vs bimodality_strength (legacy baseline)
    baseline = results['bimodality_strength']
    log('\nDelta vs bimodality_strength baseline:')
    for method in METHODS:
        if method == 'bimodality_strength':
            continue
        d_acc = results[method]['accuracy'] - baseline['accuracy']
        d_mae = results[method]['mae'] - baseline['mae']
        d_p1 = results[method]['plus1_acc'] - baseline['plus1_acc']
        log(f'  {method:22s}: Δacc={d_acc:+.1%}, ΔMAE={d_mae:+.3f}, Δ±1={d_p1:+.1%}')

    max_delta = max(
        abs(results[m]['accuracy'] - baseline['accuracy'])
        for m in METHODS if m != 'bimodality_strength'
    )
    log(f'\nMax accuracy difference: {max_delta:.1%}')
    if max_delta < 0.1:
        log('Verdict: Weighting method has minimal impact on CBV accuracy.')
    elif max_delta < 0.2:
        log('Verdict: Weighting method has moderate impact on CBV accuracy.')
    else:
        log('Verdict: Weighting method has substantial impact on CBV accuracy.')

    log('\n' + '=' * 60)


if __name__ == '__main__':
    main()
