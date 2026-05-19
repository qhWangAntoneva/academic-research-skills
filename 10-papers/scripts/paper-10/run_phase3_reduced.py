"""Phase 3 (reduced): 6 datasets, 4 indices"""
import sys, os, time, warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings('ignore')
os.environ['PYTHONUNBUFFERED'] = '1'

import numpy as np
from sklearn.datasets import make_blobs, make_moons, make_classification, load_wine, load_iris
from sklearn.preprocessing import StandardScaler

from cbv import CBVIndex, CBVSpectral
from comparison.indices import silhouette_cvi, gap_cvi

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(R, exist_ok=True)
LOG = os.path.join(R, 'phase3_reduced.log')
RS = 42
KMIN, KMAX = 2, 8

def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f'{time.strftime("%H:%M:%S")} {msg}\n')
    print(msg, flush=True)

# ── Datasets ──
datasets = []
# 1. blobs 3 clusters
X, y = make_blobs(n_samples=200, n_features=2, centers=3, cluster_std=0.5, random_state=RS)
datasets.append((X, y, 'blobs_k3', 3))
# 2. blobs 8 clusters
X, y = make_blobs(n_samples=400, n_features=2, centers=8, cluster_std=0.5, random_state=RS)
datasets.append((X, y, 'blobs_k8', 8))
# 3. moons
X, y = make_moons(n_samples=200, noise=0.05, random_state=RS)
datasets.append((X, y, 'moons', 2))
# 4. classification with noise
X, y = make_classification(n_samples=300, n_features=10, n_informative=2, n_redundant=0, n_classes=2, random_state=RS)
datasets.append((X, y, 'noise_2sig+8noise', 2))
# 5. wine
X, y = load_wine(return_X_y=True)
X = StandardScaler().fit_transform(X)
datasets.append((X, y, 'wine', 3))
# 6. iris
X, y = load_iris(return_X_y=True)
datasets.append((X, y, 'iris', 3))

log(f'[DATASETS] {len(datasets)} loaded')

# ── Indices ──
indices = [
    ('Silhouette', lambda X, kmin=KMIN, kmax=KMAX, rs=RS: silhouette_cvi(X, (kmin, kmax), rs)['k_hat']),
    ('Gap',       lambda X, kmin=KMIN, kmax=KMAX, rs=RS: gap_cvi(X, (kmin, kmax), rs)['k_hat']),
    ('CBV',       lambda X, kmin=KMIN, kmax=KMAX, rs=RS: CBVIndex((kmin, kmax), n_boot=10, random_state=rs).fit(X).predict()),
    ('CBV-Spec',  lambda X, kmin=KMIN, kmax=KMAX, rs=RS: CBVSpectral((kmin, kmax), n_boot=10, n_components=5, random_state=rs).fit(X).predict()),
]

# ── Run ──
results = []
for X, y_true, name, k_true in datasets:
    log(f'  [{name}] k_true={k_true}, X={X.shape} ...')
    for idx_name, idx_fn in indices:
        t0 = time.time()
        try:
            k_hat = idx_fn(X)
        except Exception as e:
            k_hat = -1
            log(f'    {idx_name}: ERROR {e}')
        elapsed = time.time() - t0
        correct = 'OK' if k_hat == k_true else 'X'
        log(f'    {idx_name}: k_hat={k_hat} ({correct}) [{elapsed:.1f}s]')
        results.append({'dataset': name, 'k_true': k_true, 'index': idx_name, 'k_hat': k_hat, 'correct': correct, 'time_s': round(elapsed, 2)})

# ── Summary ──
import pandas as pd
df = pd.DataFrame(results)
csv_path = os.path.join(R, 'phase3_reduced.csv')
with open(csv_path, 'w', encoding='utf-8') as f:
    df.to_csv(f, index=False)
log(f'\nResults saved to {csv_path}')

pivot = df.pivot_table(index='dataset', columns='index', values='k_hat', aggfunc='first')
log('\n=== k_hat Matrix ===')
for line in pivot.to_string().split('\n'):
    log(line)

acc = df.groupby('index')['correct'].apply(lambda x: (x == 'OK').mean())
log('\n=== Accuracy ===')
for idx, a in acc.items():
    log(f'  {idx}: {a:.0%}')

log('\nPhase 3 (reduced) done.')
