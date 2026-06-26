"""
Bootstrap CBV benchmark — runs proper Silverman bootstrap sequential test
on a large benchmark subset (30+ datasets, d <= 20 for speed).
Reports accuracy comparison with heuristic threshold.
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
LOG = RESULTS_DIR / 'bootstrap_cbv_benchmark.log'

def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f'{time.strftime("%H:%M:%S")} {msg}\n')
    print(msg, flush=True)

log('=' * 60)
log('Bootstrap CBV Full Benchmark (d <= 20 subcorpus)')
log('=' * 60)

K_RANGE = (2, 10)
N_BOOT = 30
ALPHA = 0.05

# Generate all datasets
gen = SyntheticDataGenerator(random_state=42)
synthetic_suite = gen.generate_benchmark_suite()
loader = RealDataLoader()
real_suite = loader.load_all(include_seeds=True)
all_datasets = synthetic_suite + real_suite
log(f'Total pool: {len(all_datasets)} datasets')

# Filter to datasets where d <= 20 and n <= 1500 (feasible for bootstrap)
filtered = [(i, ds) for i, ds in enumerate(all_datasets)
            if ds['X'].shape[1] <= 20 and ds['X'].shape[0] <= 1500]
log(f'Feasible for bootstrap: {len(filtered)} datasets (d <= 20, n <= 1500)')

def bootstrap_select_k(X, k_range, n_boot=30, alpha=0.05, random_state=42):
    """Sequential mode detection via bootstrap Silverman test p-values."""
    k_min, k_max = k_range
    n_features = X.shape[1]
    votes = np.full(n_features, fill_value=k_min, dtype=np.float64)
    rng = np.random.default_rng(random_state)

    for d in range(n_features):
        x_d = X[:, d]
        if np.ptp(x_d) == 0.0:
            continue

        for k in range(k_min, k_max + 1):
            try:
                st = silverman_test(x_d, mod0=k - 1, n_resamples=n_boot, random_state=rng)
                p_val = st.p_value
            except Exception:
                votes[d] = float(k_min)
                break

            if p_val < alpha:
                votes[d] = float(k)
            else:
                if k > k_min:
                    votes[d] = float(k - 1)
                break

    valid = votes[votes > 0]
    if len(valid) == 0:
        return k_min
    k_hat = int(np.round(np.mean(valid)))
    return max(k_min, min(k_hat, k_max))

def threshold_select_k(X, k_range, tolerance=1.3, random_state=42):
    cbv = CBVIndex(k_range=k_range, mode='threshold', h_crit_tolerance=tolerance,
                   random_state=random_state, n_boot=10, vote_method='weighted_mean')
    cbv.fit(X)
    return cbv.predict()

records = []
n_total = len(filtered)

for ds_idx, (orig_idx, ds) in enumerate(filtered):
    X = ds['X']
    k_true = ds.get('k_true', ds.get('y_true', None))
    if isinstance(k_true, (np.ndarray, list)):
        k_true = len(np.unique(k_true))
    ds_name = ds.get('name', f'dataset_{orig_idx}')
    n, d = X.shape

    log(f'  [{ds_idx+1}/{n_total}] {ds_name} (n={n}, d={d})...')
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
    log(f'    k_true={k_true} threshold={k_threshold} bootstrap={k_bootstrap} ({elapsed:.0f}s)')

results = pd.DataFrame(records)

log(f'\n{"="*60}')
log(f'Results on {len(filtered)} feasible datasets:')
log(f'  Heuristic threshold: {results["threshold_correct"].mean():.1%}')
log(f'  Bootstrap sequential: {results["bootstrap_correct"].mean():.1%}')
log(f'  Agreement: {results["agree"].mean():.1%}')

# Breakdown by dataset type
synth = results[~results['dataset'].str.contains('wine|iris|digits|breast|seeds|glass|yeast|ecoli|seg|olivetti|parkinsons|ionosphere|segmentation')]
real = results[results['dataset'].str.contains('wine|iris|digits|breast|seeds|glass|yeast|ecoli|seg|olivetti|parkinsons|ionosphere|segmentation')]
log(f'\nBy type:')
log(f'  Synthetic ({len(synth)}): threshold={synth["threshold_correct"].mean():.1%} bootstrap={synth["bootstrap_correct"].mean():.1%}')
log(f'  Real ({len(real)}): threshold={real["threshold_correct"].mean():.1%} bootstrap={real["bootstrap_correct"].mean():.1%}')

# Save
out_path = RESULTS_DIR / 'bootstrap_cbv_results.csv'
results.to_csv(out_path, index=False)
log(f'\nSaved to {out_path}')

# Key numbers for the paper
log(f'\n{"="*60}')
log('KEY NUMBERS FOR MANUSCRIPT:')
log(f'  Bootstrap CBV accuracy: {results["bootstrap_correct"].mean():.1%}')
log(f'  Heuristic CBV accuracy: {results["threshold_correct"].mean():.1%}')
log(f'  Improvement: +{results["bootstrap_correct"].mean() - results["threshold_correct"].mean():.1%}')
log(f'  Agreement rate: {results["agree"].mean():.1%}')
log(f'  Sample size: {len(filtered)} datasets')

# Per-seed analysis (seed 42 only for now, but we can add more)
log(f'\n{"="*60}')
log('Complete.')
