"""
Bootstrap sequential test comparison — focused subset, faster.
Runs on 10 representative datasets with B=30 resamples.
"""
import sys, os, warnings, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from pathlib import Path
from benchmark import SyntheticDataGenerator, RealDataLoader
from cbv.index import CBVIndex
from critband import silverman_test

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'
LOG = RESULTS_DIR / 'bootstrap_test_comparison.log'

def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f'{time.strftime("%H:%M:%S")} {msg}\n')
    print(msg, flush=True)

log('=' * 60)
log('Bootstrap Sequential Test Comparison (10-dataset subset)')
log('=' * 60)

K_RANGE = (2, 10)
N_BOOT = 30
ALPHA = 0.05

# Generate all datasets, select subset
gen = SyntheticDataGenerator(random_state=42)
synthetic_suite = gen.generate_benchmark_suite()
loader = RealDataLoader()
real_suite = loader.load_all(include_seeds=True)
all_datasets = synthetic_suite + real_suite

# Representative subset: variety of difficulty regimes
subset_idx = [0, 3, 6, 16, 22, 34, 42, 46, 49, 51]
subset = [all_datasets[i] for i in subset_idx]
log(f'Full: {len(all_datasets)} datasets, Subset: {len(subset)} (selected for diversity)')

def bootstrap_select_k(X, k_range, n_boot=30, alpha=0.05, random_state=42):
    """Sequential mode detection via bootstrap Silverman test p-values."""
    k_min, k_max = k_range
    n_features = X.shape[1]
    vote = k_min
    rng = np.random.default_rng(random_state)

    for d in range(n_features):
        x_d = X[:, d]
        if np.ptp(x_d) == 0.0:
            continue

        dim_vote = k_min
        for k in range(k_min, k_max + 1):
            # Silverman test H0: density has at most (k-1) modes
            try:
                st = silverman_test(x_d, mod0=k - 1, n_resamples=n_boot, random_state=rng)
                p_val = st.p_value
            except Exception:
                break

            if p_val < alpha:
                # Reject H0: at least k modes exist
                dim_vote = k
            else:
                # Cannot reject H0: at most k-1 modes
                if k > k_min:
                    dim_vote = k - 1
                break

        # Update vote (use mode across dimensions)
        vote = max(vote, dim_vote)

    return max(k_min, min(vote, k_max))

def threshold_select_k(X, k_range, tolerance=1.3, random_state=42):
    cbv = CBVIndex(k_range=k_range, mode='threshold', h_crit_tolerance=tolerance,
                   random_state=random_state, n_boot=10, vote_method='weighted_mean')
    cbv.fit(X)
    return cbv.predict()

records = []
for ds_idx, ds in enumerate(subset):
    X = ds['X']
    k_true = ds.get('k_true', ds.get('y_true', None))
    if isinstance(k_true, (np.ndarray, list)):
        k_true = len(np.unique(k_true))
    ds_name = ds.get('name', f'dataset_{subset_idx[ds_idx]}')
    n, d = X.shape
    log(f'  [{ds_idx+1}/{len(subset)}] {ds_name} (n={n}, d={d})...')

    t0 = time.time()
    k_threshold = threshold_select_k(X, K_RANGE, tolerance=1.3, random_state=42)
    k_bootstrap = bootstrap_select_k(X, K_RANGE, n_boot=N_BOOT, alpha=ALPHA, random_state=42)
    elapsed = time.time() - t0

    records.append({
        'dataset': ds_name, 'n': n, 'd': d,
        'k_true': k_true, 'k_threshold': k_threshold, 'k_bootstrap': k_bootstrap,
        'threshold_correct': int(k_threshold == k_true),
        'bootstrap_correct': int(k_bootstrap == k_true),
        'agree': int(k_threshold == k_bootstrap),
    })
    log(f'    elapsed={elapsed:.0f}s k_true={k_true} threshold={k_threshold} bootstrap={k_bootstrap} agree={k_threshold==k_bootstrap}')

results = pd.DataFrame(records)
log(f'\n{"="*60}')
log(f'Results on {len(subset)} representative datasets:')
log(f'  Heuristic threshold accuracy: {results["threshold_correct"].mean():.0%}')
log(f'  Bootstrap sequential test accuracy: {results["bootstrap_correct"].mean():.0%}')
log(f'  Agreement: {results["agree"].mean():.0%}')
log(f'  Exact match sets: {(results["k_threshold"] == results["k_bootstrap"]).sum()}/{len(subset)}')

out_path = RESULTS_DIR / 'bootstrap_test_comparison.csv'
results.to_csv(out_path, index=False)
log(f'\nSaved to {out_path}')
log(f'\n{"="*60}')
log('Complete.')
