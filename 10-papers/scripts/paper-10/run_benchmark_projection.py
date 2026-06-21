"""
Phase E: CBVProjection Benchmark — compare projection CBV against other indices.

Runs CBVProjection on all datasets (single seed=42) and compares accuracy
against the existing CBVHybrid results from run_benchmark.py.
"""
import sys, os, warnings, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings('ignore')
os.environ['PYTHONIOENCODING'] = 'utf-8'

import numpy as np
import pandas as pd
from pathlib import Path
from benchmark import SyntheticDataGenerator, RealDataLoader

RESULTS_DIR = Path(__file__).parent / 'results'
LOG = RESULTS_DIR / 'benchmark_projection.log'
_log_initialized = False
def log(msg):
    global _log_initialized
    mode = 'w' if not _log_initialized else 'a'
    _log_initialized = True
    with open(LOG, mode, encoding='utf-8') as f:
        f.write(f'{time.strftime("%H:%M:%S")} {msg}\n')
    print(msg, flush=True)

log('=' * 60)
log('Phase E: CBVProjection Benchmark')
log('=' * 60)

# Build datasets
log('\n[1/3] Building datasets...')
gen = SyntheticDataGenerator(random_state=42)
synthetic = gen.generate_benchmark_suite()
loader = RealDataLoader()
real = loader.load_all(include_seeds=True)
all_datasets = synthetic + real
log(f'  Total: {len(all_datasets)} datasets')

# Run CBVProjection on all datasets
from cbv import CBVProjection, CBVHybrid
from comparison import get_all_indices
from comparison.indices import KMEANS_N_INIT
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

K_RANGE = (2, 10)
SEED = 42

# Build all indices including CBVProjection
indices_info = [
    ('CBVProjection_20', lambda: CBVProjection(k_range=K_RANGE, n_projections=20, random_state=SEED)),
    ('CBVProjection_50', lambda: CBVProjection(k_range=K_RANGE, n_projections=50, random_state=SEED)),
]

# Also run CBVHybrid for comparison
indices_info.append(('CBVHybrid', lambda: CBVHybrid(
    k_range=K_RANGE, n_boot=10, random_state=SEED,
    mode='threshold', vote_method='mode', use_excess_mass=False,
)))

log(f'\n[2/3] Running {len(indices_info)} index variants on {len(all_datasets)} datasets...')

def compute_ari(y_true, k_hat, X, seed=42):
    if k_hat < 2 or k_hat >= X.shape[0]:
        return np.nan
    try:
        labels = KMeans(n_clusters=int(k_hat), n_init=KMEANS_N_INIT, random_state=seed).fit_predict(X)
        return float(adjusted_rand_score(y_true, labels))
    except:
        return np.nan

results_rows = []
t0 = time.time()

for ds in all_datasets:
    X, y_true, k_true = ds['X'], ds['y_true'], ds['k_true']
    row = {'name': ds['name'], 'k_true': k_true, 'n_features': X.shape[1]}

    for idx_name, make_fn in indices_info:
        try:
            idx = make_fn()
            idx.fit(X)
            k_hat = idx.predict()
            row[f'{idx_name}_k'] = k_hat
            row[f'{idx_name}_correct'] = int(k_hat == k_true)
            row[f'{idx_name}_mae'] = abs(k_hat - k_true)
            row[f'{idx_name}_ari'] = compute_ari(y_true, k_hat, X, seed=SEED)
        except Exception as e:
            row[f'{idx_name}_k'] = -1
            row[f'{idx_name}_correct'] = 0
            row[f'{idx_name}_mae'] = np.nan
            row[f'{idx_name}_ari'] = np.nan

    results_rows.append(row)

elapsed = time.time() - t0
log(f'  Completed in {elapsed:.1f}s')

df = pd.DataFrame(results_rows)

# Save raw results
out_path = RESULTS_DIR / 'benchmark_projection_results.csv'
df.to_csv(str(out_path), index=False)
log(f'\nRaw results → {out_path}')

# ── Summary ──
log('\n' + '=' * 60)
log('Accuracy Summary')
log('=' * 60)

for idx_name, _ in indices_info:
    col = f'{idx_name}_correct'
    acc = df[col].mean()
    mae = df[f'{idx_name}_mae'].mean()
    ari = df[f'{idx_name}_ari'].mean()
    log(f'  {idx_name:20s}: acc={acc:.1%}  MAE={mae:.2f}  ARI={ari:.3f}')

# ── Head-to-head comparison ──
log('\n' + '=' * 60)
log('Head-to-Head: CBVProjection_20 vs CBVHybrid')
log('=' * 60)

both_correct = ((df['CBVProjection_20_correct'] == 1) & (df['CBVHybrid_correct'] == 1)).sum()
proj_only = ((df['CBVProjection_20_correct'] == 1) & (df['CBVHybrid_correct'] == 0)).sum()
hybrid_only = ((df['CBVProjection_20_correct'] == 0) & (df['CBVHybrid_correct'] == 1)).sum()
neither = ((df['CBVProjection_20_correct'] == 0) & (df['CBVHybrid_correct'] == 0)).sum()

log(f'  Both correct:       {both_correct}')
log(f'  Projection only:    {proj_only}')
log(f'  Hybrid only:        {hybrid_only}')
log(f'  Neither correct:    {neither}')

# Datasets where projection succeeds but hybrid fails
if proj_only > 0:
    proj_wins = df[(df['CBVProjection_20_correct'] == 1) & (df['CBVHybrid_correct'] == 0)]
    log(f'\n  Projection wins on:')
    for _, r in proj_wins.iterrows():
        log(f'    {r["name"]} (k_true={r["k_true"]}, proj_k={r["CBVProjection_20_k"]}, hybrid_k={r["CBVHybrid_k"]})')

# Datasets where hybrid succeeds but projection fails
if hybrid_only > 0:
    hybrid_wins = df[(df['CBVProjection_20_correct'] == 0) & (df['CBVHybrid_correct'] == 1)]
    log(f'\n  Hybrid wins on:')
    for _, r in hybrid_wins.iterrows():
        log(f'    {r["name"]} (k_true={r["k_true"]}, proj_k={r["CBVProjection_20_k"]}, hybrid_k={r["CBVHybrid_k"]})')

log(f'\n{"=" * 60}')
log(f'Phase E (Projection) complete. Output: {out_path}')
log(f'{"=" * 60}')
