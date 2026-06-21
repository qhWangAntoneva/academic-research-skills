"""
Phase D-1: P0-6 Correlated-Dimension Ablation Study — Paper #10 (CBV)

Tests CVI robustness when irrelevant dimensions are linear combinations
(correlated copies) of cluster-informative features.

Design: 10 conditions (5 n_corr × 2 corr_strength) × 5 fast indices.
Expected runtime: ~30s.
"""
import sys, os, warnings, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings('ignore')
os.environ['PYTHONIOENCODING'] = 'utf-8'

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.cluster import KMeans

from cbv import CBVHybrid
from comparison.indices import _within_cluster_dispersion

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

LOG = RESULTS_DIR / 'ablation_correlated_dims.log'
_log_initialized = False
def log(msg):
    global _log_initialized
    mode = 'w' if not _log_initialized else 'a'
    _log_initialized = True
    with open(LOG, mode, encoding='utf-8') as f:
        f.write(f'{time.strftime("%H:%M:%S")} {msg}\n')
    print(msg, flush=True)


def make_correlated_data(n_samples=300, n_informative=2, n_corr_per=5,
                         k_true=3, corr_strength=0.8, random_state=42):
    rng = np.random.RandomState(random_state)
    X_base, y = make_blobs(n_samples=n_samples, n_features=n_informative,
                           centers=k_true, cluster_std=1.0, random_state=random_state)
    n_corr = n_corr_per * n_informative
    X_corr = np.zeros((n_samples, n_corr))
    for i in range(n_informative):
        col = X_base[:, i]
        for j in range(n_corr_per):
            noise = rng.randn(n_samples) * col.std()
            X_corr[:, i * n_corr_per + j] = corr_strength * col + (1 - corr_strength) * noise
    return np.hstack([X_base, X_corr]), y


K_RANGE = (2, 10)
N_INIT = 10
K_TRUE = 3

def fit_cbv(X):
    idx = CBVHybrid(k_range=K_RANGE, n_boot=10, random_state=42,
                    mode='threshold', vote_method='mode', use_excess_mass=False)
    idx.fit(X); return idx.predict()

def fit_ch(X):
    bk, bs = 2, -1
    for k in range(K_RANGE[0], K_RANGE[1]+1):
        if k >= X.shape[0]: continue
        lab = KMeans(k, n_init=N_INIT, random_state=42).fit_predict(X)
        if len(set(lab)) < 2: continue
        s = calinski_harabasz_score(X, lab)
        if s > bs: bs, bk = s, k
    return bk

def fit_sil(X):
    bk, bs = 2, -1
    for k in range(K_RANGE[0], K_RANGE[1]+1):
        if k >= X.shape[0]: continue
        lab = KMeans(k, n_init=N_INIT, random_state=42).fit_predict(X)
        if len(set(lab)) < 2: continue
        s = silhouette_score(X, lab)
        if s > bs: bs, bk = s, k
    return bk

def fit_db(X):
    bk, bs = 2, np.inf
    for k in range(K_RANGE[0], K_RANGE[1]+1):
        if k >= X.shape[0]: continue
        lab = KMeans(k, n_init=N_INIT, random_state=42).fit_predict(X)
        if len(set(lab)) < 2: continue
        s = davies_bouldin_score(X, lab)
        if s < bs: bs, bk = s, k
    return bk

def fit_hartigan(X):
    W = {}
    for k in range(K_RANGE[0], K_RANGE[1]+1):
        if k >= X.shape[0]: continue
        lab = KMeans(k, n_init=N_INIT, random_state=42).fit_predict(X)
        if len(set(lab)) < 2: continue
        W[k] = _within_cluster_dispersion(X, lab)
    ks = sorted(W.keys())
    for i, k in enumerate(ks):
        if k == ks[-1]: continue
        Wk, Wk1 = W[k], W[k+1]
        if Wk1 == 0: continue
        h = (Wk / Wk1 - 1.0) * (X.shape[0] - k - 1)
        if h <= 10.0: return k
    return ks[-1] if ks else 2

INDICES = {'CBV': fit_cbv, 'CH': fit_ch, 'Silhouette': fit_sil,
           'Davies-Bouldin': fit_db, 'Hartigan': fit_hartigan}

# ── Ablation sweep ──
N_CORR_PER_LIST = [0, 2, 5, 10]  # per informative dim → total = n_informative * this
CORR_STRENGTHS = [0.0, 0.5, 0.9]

log('=' * 60)
log('Phase D-1: Correlated-Dimension Ablation Study (P0-6)')
log('=' * 60)

rows = []
for n_corr_per in N_CORR_PER_LIST:
    for cs in CORR_STRENGTHS:
        nc = n_corr_per * 2
        X, y = make_correlated_data(n_corr_per=n_corr_per, corr_strength=cs, random_state=42)
        row = {'n_corr_dims': nc, 'corr_strength': cs, 'n_features': X.shape[1], 'k_true': K_TRUE}
        for nm, fn in INDICES.items():
            try:
                kh = fn(X)
                row[f'{nm}_k'] = kh
                row[f'{nm}_correct'] = int(kh == K_TRUE)
                row[f'{nm}_mae'] = abs(kh - K_TRUE)
            except Exception:
                row[f'{nm}_k'] = -1; row[f'{nm}_correct'] = 0; row[f'{nm}_mae'] = np.nan
        rows.append(row)
        log(f'  n_corr={nc:2d} s={cs:.1f} → {X.shape[1]:2d} feats')

df = pd.DataFrame(rows)
out = RESULTS_DIR / 'ablation_correlated_dims.csv'
df.to_csv(str(out), index=False)
log(f'\nSaved → {out}')

# ── Summary ──
log('\n=== Accuracy by corr_strength (mean over n_corr_dims) ===')
for nm in INDICES:
    s = df.groupby('corr_strength')[f'{nm}_correct'].mean()
    log(f'  {nm:15s}: ' + '  '.join(f'{v:.1f}={a:.2f}' for v,a in s.items()))

log('\n=== Accuracy by n_corr_dims (mean over corr_strength) ===')
for nm in INDICES:
    s = df.groupby('n_corr_dims')[f'{nm}_correct'].mean()
    log(f'  {nm:15s}: ' + '  '.join(f'{n:2d}={a:.2f}' for n,a in s.items()))

log('\n=== MAE by corr_strength (mean over n_corr_dims) ===')
for nm in INDICES:
    s = df.groupby('corr_strength')[f'{nm}_mae'].mean()
    log(f'  {nm:15s}: ' + '  '.join(f'{v:.1f}={a:.2f}' for v,a in s.items()))

log('\n=== Degradation: s=0.9 vs s=0.0 ===')
for nm in INDICES:
    a0 = df[df.corr_strength==0.0][f'{nm}_correct'].mean()
    a9 = df[df.corr_strength==0.9][f'{nm}_correct'].mean()
    r = a9/a0 if a0>0 else float('nan')
    log(f'  {nm:15s}: {a0:.2f} → {a9:.2f}  (ratio={r:.2f})')

log(f'\nDone. Output: {out}')
