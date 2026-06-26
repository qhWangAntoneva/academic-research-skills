"""
Bootstrap confidence intervals for CBV point estimates.
Runs CBV with bootstrap resampling on a representative subset.
"""
import sys, os, warnings, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from pathlib import Path
from benchmark import SyntheticDataGenerator, RealDataLoader
from cbv import CBVIndex

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'
LOG = RESULTS_DIR / 'cbv_bootstrap.log'

def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f'{time.strftime("%H:%M:%S")} {msg}\n')
    print(msg, flush=True)

log('=' * 60)
log('CBV Bootstrap Confidence Intervals')
log('=' * 60)

K_RANGE = (2, 10)
N_BOOT = 100

# Generate datasets
gen = SyntheticDataGenerator(random_state=42)
synthetic_suite = gen.generate_benchmark_suite()
loader = RealDataLoader()
real_suite = loader.load_all(include_seeds=True)
all_datasets = synthetic_suite + real_suite
log(f'Total datasets: {len(all_datasets)}')

# Select representative subset: one from each difficulty regime
subset_indices = [0, 1, 10, 13, 17, 23, 26, 29, 42, 43, 44, 50]  # easy, medium, hard, real
subset = [all_datasets[i] for i in subset_indices]
log(f'Subset size: {len(subset)} datasets for bootstrap analysis')

records = []
for ds_idx, ds in enumerate(subset):
    X = ds['X']
    k_true = ds.get('k_true', ds.get('y_true', None))
    if isinstance(k_true, (np.ndarray, list)):
        k_true = len(np.unique(k_true))
    ds_name = ds.get('name', f'ds_{subset_indices[ds_idx]}')
    n, d = X.shape

    # CBV on original data (threshold mode, matching benchmark)
    cbv = CBVIndex(k_range=K_RANGE, mode='threshold', h_crit_tolerance=1.3, random_state=42)
    cbv.fit(X)
    k_hat_orig = cbv.predict()

    # Bootstrap
    boot_k = []
    for b in range(N_BOOT):
        idx = np.random.choice(n, n, replace=True)
        X_boot = X[idx]
        try:
            cbv_b = CBVIndex(k_range=K_RANGE, mode='threshold', h_crit_tolerance=1.3, random_state=b)
            cbv_b.fit(X_boot)
            boot_k.append(cbv_b.predict())
        except Exception:
            continue

    boot_k = np.array(boot_k)
    ci_low = int(np.percentile(boot_k, 2.5))
    ci_high = int(np.percentile(boot_k, 97.5))
    ci_range = ci_high - ci_low

    records.append({
        'dataset': ds_name,
        'n': n,
        'd': d,
        'k_true': k_true,
        'k_hat': k_hat_orig,
        'ci_low': ci_low,
        'ci_high': ci_high,
        'ci_range': ci_range,
        'bootstrap_stable': int(ci_range <= 1),
    })
    log(f'  {ds_name}: k_true={k_true} k_hat={k_hat_orig} CI=[{ci_low},{ci_high}] range={ci_range}')

df = pd.DataFrame(records)
stable_pct = df['bootstrap_stable'].mean()
log(f'\nBootstrap stability (CI range <= 1): {stable_pct:.0%}')

out_path = RESULTS_DIR / 'cbv_bootstrap_ci.csv'
df.to_csv(out_path, index=False)
log(f'Saved to {out_path}')
log('Done.')
