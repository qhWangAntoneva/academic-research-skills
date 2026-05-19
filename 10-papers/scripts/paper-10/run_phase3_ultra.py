"""Phase 3 ultra-reduced: 3 datasets, 3 indices, k_range=(2,5), skip silverman_test"""
import sys, os, time, warnings, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings('ignore')
os.environ['PYTHONUNBUFFERED'] = '1'

from sklearn.datasets import make_blobs, make_moons, load_iris
from sklearn.preprocessing import StandardScaler
from cbv.index import CBVIndex
from comparison.indices import silhouette_cvi, gap_cvi

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(R, exist_ok=True)
LOG = os.path.join(R, 'phase3_ultra.log')

def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f'{time.strftime("%H:%M:%S")} {msg}\n')
    print(msg, flush=True)

RS = 42
K_MIN, K_MAX = 2, 5

# CBV wrapper: fast mode (skip CI + silverman_test)
def fast_cbv_cbw(X, k_min=K_MIN, k_max=K_MAX):
    idx = CBVIndex(k_range=(k_min, k_max), n_boot=1, random_state=RS, fast=True)
    return idx.fit(X).predict()

# ── Datasets ──
datasets = []
X, y = make_blobs(200, 2, centers=3, cluster_std=0.8, random_state=RS); datasets.append((X, y, 'blobs_k3', 3))
X, y = make_moons(200, noise=0.05, random_state=RS); datasets.append((X, y, 'moons', 2))
X, y = load_iris(return_X_y=True); datasets.append((StandardScaler().fit_transform(X), y, 'iris', 3))

log(f'{len(datasets)} datasets loaded')

# ── Run ──
for X, y_true, name, k_true in datasets:
    log(f'[{name}] k_true={k_true} X={X.shape}')

    t0 = time.time()
    k_sil = silhouette_cvi(X, (K_MIN, K_MAX), RS)['k_hat']
    log(f'  Silhouette: {k_sil} ({"OK" if k_sil==k_true else "X"}) [{time.time()-t0:.1f}s]')

    t0 = time.time()
    k_gap = gap_cvi(X, (K_MIN, K_MAX), RS)['k_hat']
    log(f'  Gap: {k_gap} ({"OK" if k_gap==k_true else "X"}) [{time.time()-t0:.1f}s]')

    t0 = time.time()
    k_cbv = fast_cbv_cbw(X)
    log(f'  CBV: {k_cbv} ({"OK" if k_cbv==k_true else "X"}) [{time.time()-t0:.1f}s]')

log('\nDone!')
