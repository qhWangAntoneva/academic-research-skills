"""
GMM-BIC baseline for CBV benchmark.
Runs BIC-selected k on the 58-dataset benchmark.
Uses diag covariance for high-d data (d > 50) to avoid prohibitive compute.
"""
import sys, os, warnings, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.mixture import GaussianMixture
from benchmark import SyntheticDataGenerator, RealDataLoader

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'
LOG = RESULTS_DIR / 'gmm_bic_benchmark.log'

def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f'{time.strftime("%H:%M:%S")} {msg}\n')
    print(msg, flush=True)

log('=' * 60)
log('GMM-BIC Baseline Benchmark')
log('=' * 60)

K_RANGE = (2, 10)
SEEDS = [42, 73, 123, 256, 999]

# Generate datasets
gen = SyntheticDataGenerator(random_state=42)
synthetic_suite = gen.generate_benchmark_suite()
loader = RealDataLoader()
real_suite = loader.load_all(include_seeds=True)
all_datasets = synthetic_suite + real_suite
log(f'Datasets: {len(synthetic_suite)} synthetic + {len(real_suite)} real = {len(all_datasets)} total')

def gmm_bic_select_k(X, k_range, random_state=42):
    """Select k by minimizing BIC for GMM.

    Uses full covariance for low-d (d <= 50), diag for high-d (d > 50).
    """
    k_min, k_max = k_range
    best_k = k_min
    best_val = np.inf
    scores = []
    n_features = X.shape[1]
    n_samples = X.shape[0]

    # Choose covariance type based on dimensionality
    cov_type = 'full' if n_features <= 50 else 'diag'

    for k in range(k_min, k_max + 1):
        if k >= n_samples:
            continue
        if cov_type == 'full' and k > n_features:
            continue  # Full covariance needs k <= d for non-degenerate estimation
        try:
            gmm = GaussianMixture(
                n_components=k, covariance_type=cov_type,
                random_state=random_state, n_init=5,
                max_iter=300, reg_covar=1e-6
            )
            gmm.fit(X)
            val = gmm.bic(X)
            scores.append((k, val))
        except Exception as e:
            log(f'  k={k} failed (d={n_features}, cov={cov_type}): {str(e)[:80]}')
            continue

    if not scores:
        return k_min
    best_k, _ = min(scores, key=lambda x: x[1])
    return best_k

# Run benchmark
records = []
for seed in SEEDS:
    log(f'\nSeed {seed}...')
    n_datasets = len(all_datasets)

    for ds_idx, ds in enumerate(all_datasets):
        X = ds['X']
        k_true = ds.get('k_true', ds.get('y_true', None))
        if isinstance(k_true, (np.ndarray, list)):
            k_true = len(np.unique(k_true))

        if ds_idx % 10 == 0:
            log(f'  [{ds_idx+1}/{n_datasets}] {ds.get("name", f"ds_{ds_idx}")} (d={X.shape[1]}, n={X.shape[0]})')

        k_bic = gmm_bic_select_k(X, K_RANGE, seed)

        records.append({
            'dataset': ds.get('name', f'dataset_{ds_idx}'),
            'k_true': k_true,
            'seed': seed,
            'GMM_BIC': k_bic,
            'bic_correct': int(k_bic == k_true),
        })

    # Per-seed summary
    subset = pd.DataFrame([r for r in records if r['seed'] == seed])
    bic_acc = subset['bic_correct'].mean()
    log(f'  Seed {seed} complete: BIC accuracy = {bic_acc:.1%}')

results = pd.DataFrame(records)
log(f'\nResults shape: {results.shape}')

# Aggregate
agg = results.groupby('seed')['bic_correct'].mean()
log(f'\nAggregate across {len(SEEDS)} seeds:')
log(f'GMM-BIC: {agg.mean():.1%} ± {agg.std(ddof=1):.1%}')

# Comparison with existing CVIs
existing = pd.read_csv(RESULTS_DIR / 'accuracy_per_seed.csv')
log(f'\nComparison (mean accuracy across seeds):')
for col in existing.columns:
    if col == 'seed':
        continue
    log(f'  {col}: {existing[col].mean():.1%}')
log(f'  GMM-BIC: {agg.mean():.1%}')

# Save
out_path = RESULTS_DIR / 'gmm_bic_results.csv'
results.to_csv(out_path, index=False)
log(f'\nSaved to {out_path}')
log(f'\n{"=" * 60}')
log('GMM-BIC benchmark complete.')
