"""
Full 58-dataset bootstrap CI — fast mode for remaining datasets.
B=50 for small-n, B=20 for high-n or high-d to balance speed.
"""
import sys, os, warnings, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from pathlib import Path
from benchmark import SyntheticDataGenerator, RealDataLoader
from cbv.index import CBVIndex

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'
LOG = RESULTS_DIR / 'cbv_bootstrap_fast.log'

def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f'{time.strftime("%H:%M:%S")} {msg}\n')
    print(msg, flush=True)

log('=' * 60)
log('CBV Fast Bootstrap CI — 58 datasets (complete)')
log('=' * 60)

K_RANGE = (2, 10)

gen = SyntheticDataGenerator(random_state=42)
synthetic_suite = gen.generate_benchmark_suite()
loader = RealDataLoader()
real_suite = loader.load_all(include_seeds=True)
all_datasets = synthetic_suite + real_suite
log(f'Total: {len(all_datasets)} datasets')

records = []
n_total = len(all_datasets)

for ds_idx, ds in enumerate(all_datasets):
    X = ds['X']
    k_true = ds.get('k_true', ds.get('y_true', None))
    if isinstance(k_true, (np.ndarray, list)):
        k_true = len(np.unique(k_true))
    ds_name = ds.get('name', f'ds_{ds_idx}')
    n, d = X.shape

    # Adaptive bootstrap count: fewer for large/high-d datasets
    N_BOOT = 50 if n <= 400 and d <= 100 else 20

    log(f'  [{ds_idx+1}/{n_total}] {ds_name} (n={n}, d={d}, B={N_BOOT})...')
    t0 = time.time()

    # CBV on original
    cbv = CBVIndex(k_range=K_RANGE, mode='threshold', h_crit_tolerance=1.3, random_state=42, vote_method='weighted_mean')
    cbv.fit(X)
    k_hat_orig = cbv.predict()

    # Bootstrap
    boot_k = []
    for b in range(N_BOOT):
        rng = np.random.default_rng(b + 1000)
        idx = rng.choice(n, n, replace=True)
        X_boot = X[idx]
        try:
            cbv_b = CBVIndex(k_range=K_RANGE, mode='threshold', h_crit_tolerance=1.3, random_state=b, vote_method='weighted_mean')
            cbv_b.fit(X_boot)
            boot_k.append(cbv_b.predict())
        except Exception:
            continue

    elapsed = time.time() - t0
    boot_k = np.array(boot_k)
    ci_low = int(np.percentile(boot_k, 2.5))
    ci_high = int(np.percentile(boot_k, 97.5))
    ci_range = ci_high - ci_low
    stable = int(ci_range <= 1)

    log(f'    -> k_hat={k_hat_orig}, CI=[{ci_low},{ci_high}], range={ci_range}, stable={stable} ({elapsed:.0f}s)')

    records.append({
        'dataset': ds_name, 'n': n, 'd': d,
        'k_true': k_true, 'k_hat': k_hat_orig,
        'ci_low': ci_low, 'ci_high': ci_high,
        'ci_range': ci_range, 'bootstrap_stable': stable,
    })

df = pd.DataFrame(records)
stable_pct = df['bootstrap_stable'].mean()
mean_range = df['ci_range'].mean()

log(f'\n{"="*60}')
log(f'Full 58-dataset Bootstrap CI Results:')
log(f'  Bootstrap stability (CI range <= 1): {stable_pct:.1%}')
log(f'  Mean CI range: {mean_range:.2f}')

# Breakdowns
for cat, cond in [('k_true <= 4', df['k_true'] <= 4),
                   ('k_true >= 5', df['k_true'] >= 5),
                   ('d <= 10', df['d'] <= 10),
                   ('d > 10', df['d'] > 10),
                   ('n <= 300', df['n'] <= 300),
                   ('n > 300', df['n'] > 300)]:
    subset = df[cond]
    if len(subset) > 0:
        log(f'  {cat}: stable={subset["bootstrap_stable"].mean():.1%}, mean_range={subset["ci_range"].mean():.2f}')

out_path = RESULTS_DIR / 'cbv_bootstrap_full58.csv'
df.to_csv(out_path, index=False)
log(f'\nSaved to {out_path}')
log(f'{"="*60}')
log('Complete.')
