"""
Phase C: Full Benchmark — Paper #10 (CBV)

Runs all 11 CV indices on 44 synthetic + 15 real-world datasets.
Multi-seed protocol: [42, 73, 123, 256, 999] (P0-2).
Multi-metric evaluation: accuracy, MAE, ±1 accuracy, ARI (P0-3).
Saves results CSV + accuracy/rank plots to results/ directory.
"""
import sys, os, warnings, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings('ignore')
os.environ['PYTHONIOENCODING'] = 'utf-8'

import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

from cbv import CBVHybrid
from benchmark import SyntheticDataGenerator, RealDataLoader, BenchmarkRunner
from comparison import get_all_indices
from comparison.indices import KMEANS_N_INIT

RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Log to file instead of stdout to avoid buffering issues in background tasks
LOG = RESULTS_DIR / 'benchmark.log'
def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f'{time.strftime("%H:%M:%S")} {msg}\n')
    print(msg, flush=True)

log('=' * 60)
log('Phase 3: Full Benchmark — Paper #10 (CBV) — Multi-Seed + Multi-Metric')
log('=' * 60)

# ── 1. Build datasets ──
log('\n[1/4] Building datasets...')
gen = SyntheticDataGenerator(random_state=42)
synthetic_suite = gen.generate_benchmark_suite()
log(f'  Synthetic: {len(synthetic_suite)} datasets')

loader = RealDataLoader()
real_suite = loader.load_all(include_seeds=True)
log(f'  Real: {len(real_suite)} datasets')

all_datasets = synthetic_suite + real_suite
log(f'  Total: {len(all_datasets)} datasets')

# ── 2. Build indices ──
log('\n[2/4] Building indices...')
K_RANGE = (2, 10)
N_BOOT = 10  # threshold mode for benchmark; use bootstrap with 999 for publication
SEEDS = [42, 73, 123, 256, 999]
N_SEEDS = len(SEEDS)

class CBVAdapter:
    def __init__(self, k_range=K_RANGE, n_boot=N_BOOT, random_state=42):
        self.name = 'CBV'
        self.idx = CBVHybrid(
            k_range=k_range, n_boot=n_boot, random_state=random_state,
            mode='threshold', vote_method='mode', use_excess_mass=False,
        )
    def fit(self, X):
        self.idx.fit(X)
        return self
    def predict(self):
        return self.idx.predict()


# ── 3. Run benchmark (multi-seed) ──
log('\n[3/4] Running benchmark across seeds: %s' % SEEDS)
t0 = time.time()

all_seed_results = {}  # seed -> pd.DataFrame

for seed in SEEDS:
    log(f'\n  Seed {seed}...')
    indices = get_all_indices(k_range=K_RANGE, random_state=seed)
    indices.append(CBVAdapter(k_range=K_RANGE, n_boot=N_BOOT, random_state=seed))
    log(f'    {len(indices)} indices: {[i.name for i in indices]}')

    runner = BenchmarkRunner(indices, all_datasets, random_state=seed)
    results = runner.run_all(parallel=True, n_jobs=-1)
    all_seed_results[seed] = results
    log(f'    Results shape: {results.shape}')

elapsed = time.time() - t0
log(f'\n  All seeds completed in {elapsed:.1f}s')

# ── 4. Multi-seed metrics ──
log('\n[4/4] Computing metrics across seeds...')

EXCLUDED_INDICES = {'DUD Index'}
INDEX_NAMES = [n for n, _ in runner._resolved_indices]

def compute_ari(y_true, k_hat, X, seed=42):
    """Adjusted Rand Index: run KMeans(k_hat) and compare to ground-truth labels."""
    if k_hat < 2 or k_hat >= X.shape[0]:
        return np.nan
    try:
        labels = KMeans(n_clusters=int(k_hat), n_init=KMEANS_N_INIT, random_state=seed).fit_predict(X)
        return float(adjusted_rand_score(y_true, labels))
    except Exception:
        return np.nan


# Per-seed, per-index metrics
seeds_metrics = {}  # seed -> {index -> {accuracy, mae, acc_plus1, ari}}

for seed in SEEDS:
    res = all_seed_results[seed]
    k_trues = res['k_true'].values
    metrics_for_seed = {}

    for idx_name in INDEX_NAMES:
        k_col = f'{idx_name}_k'
        corr_col = f'{idx_name}_correct'
        if k_col not in res.columns:
            continue

        k_hats = res[k_col].values
        correct = res[corr_col].values if corr_col in res.columns else np.zeros(len(res))

        # Accuracy (exact match)
        accuracy = float(np.mean(correct))

        # MAE: mean absolute error (ignoring failed: k_hat < 0)
        mask_valid = k_hats >= 0
        if mask_valid.sum() > 0:
            mae = float(np.mean(np.abs(k_hats[mask_valid] - k_trues[mask_valid])))
            acc_plus1 = float(np.mean(np.abs(k_hats[mask_valid] - k_trues[mask_valid]) <= 1.0))
        else:
            mae = np.nan
            acc_plus1 = np.nan

        # ARI: run KMeans with k_hat per dataset
        aris = []
        for i, ds in enumerate(all_datasets):
            kh = k_hats[i]
            if kh >= 2 and 'y_true' in ds:
                aris.append(compute_ari(ds['y_true'], int(kh), ds['X'], seed=seed))
            else:
                aris.append(np.nan)
        ari = float(np.nanmean(aris)) if aris else np.nan

        metrics_for_seed[idx_name] = {
            'accuracy': accuracy,
            'mae': mae,
            'acc_plus1': acc_plus1,
            'ari': ari,
        }

    seeds_metrics[seed] = metrics_for_seed


# ── 4a. Aggregate table: mean ± std across seeds ──
log('\nMulti-seed metrics (mean ± std across %d seeds):' % N_SEEDS)

metric_names = ['accuracy', 'mae', 'acc_plus1', 'ari']
metric_labels = {
    'accuracy': 'Accuracy',
    'mae': 'MAE',
    'acc_plus1': '±1 Acc',
    'ari': 'ARI',
}

agg_records = []
for idx_name in INDEX_NAMES:
    if idx_name in EXCLUDED_INDICES:
        continue
    row = {'index': idx_name}
    for m in metric_names:
        vals = [seeds_metrics[s][idx_name][m] for s in SEEDS if idx_name in seeds_metrics[s]]
        if len(vals) > 0 and not all(np.isnan(v) for v in vals):
            valid = [v for v in vals if not np.isnan(v)]
            if len(valid) > 0:
                row[f'{m}_mean'] = np.mean(valid)
                row[f'{m}_std'] = np.std(valid, ddof=1) if len(valid) > 1 else 0.0
            else:
                row[f'{m}_mean'] = np.nan
                row[f'{m}_std'] = np.nan
        else:
            row[f'{m}_mean'] = np.nan
            row[f'{m}_std'] = np.nan
    agg_records.append(row)

agg_df = pd.DataFrame(agg_records).sort_values('accuracy_mean', ascending=False)
log(agg_df.to_string(index=False))

# Save aggregated metrics
agg_path = RESULTS_DIR / 'metrics_multi_seed.csv'
with open(str(agg_path), 'w', encoding='utf-8') as f:
    agg_df.to_csv(f, index=False)
log(f'\n  Multi-seed metrics saved to {agg_path}')

# ── 4b. Per-seed accuracy table ──
log('\nPer-seed accuracy:')
acc_records = []
for seed in SEEDS:
    row = {'seed': seed}
    for idx_name in INDEX_NAMES:
        if idx_name in EXCLUDED_INDICES:
            continue
        row[idx_name] = seeds_metrics[seed][idx_name]['accuracy']
    acc_records.append(row)

per_seed_acc = pd.DataFrame(acc_records)
log(per_seed_acc.to_string(index=False))

per_seed_path = RESULTS_DIR / 'accuracy_per_seed.csv'
with open(str(per_seed_path), 'w', encoding='utf-8') as f:
    per_seed_acc.to_csv(f, index=False)

# ── 4c. Mean rank (last seed, for reference) ──
last_seed = SEEDS[-1]
last_runner = BenchmarkRunner(
    get_all_indices(k_range=K_RANGE, random_state=last_seed) + [CBVAdapter(k_range=K_RANGE, n_boot=N_BOOT, random_state=last_seed)],
    all_datasets, random_state=last_seed,
)
last_summary = last_runner.summarize_results(all_seed_results[last_seed])
mean_rank = last_summary['mean_rank']
mean_rank_main = mean_rank[~mean_rank.index.isin(EXCLUDED_INDICES)]
log('\nMean rank (1 = best) — last seed reference:')
log(str(mean_rank_main))

# Statistical tests
friedman = last_summary.get('friedman', None)
if friedman:
    stat, p_val = friedman
    log(f'\nFriedman test: chi2={stat:.3f}, p={p_val:.4f}')
    log('  → Significant (p < 0.05)' if p_val < 0.05 else '  → Not significant')

# ── 4d. Save all seed results ──
for seed in SEEDS:
    seed_csv = RESULTS_DIR / f'results_seed_{seed}.csv'
    with open(str(seed_csv), 'w', encoding='utf-8') as f:
        all_seed_results[seed].to_csv(f, index=False)

# Combined results (last seed for full detail)
combined_path = RESULTS_DIR / 'benchmark_results.csv'
with open(str(combined_path), 'w', encoding='utf-8') as f:
    all_seed_results[SEEDS[-1]].to_csv(f, index=False)

# ── 4e. Per-dataset detail (last seed) ──
detail_path = RESULTS_DIR / 'per_dataset_results.csv'
with open(str(detail_path), 'w', encoding='utf-8') as f:
    all_seed_results[SEEDS[-1]].to_csv(f, index=False)

# ── 4f. Plots (last seed) ──
log('\nGenerating plots (last seed)...')
last_runner.plot_accuracy_comparison(
    all_seed_results[last_seed],
    str(RESULTS_DIR / 'accuracy_comparison.png'),
)
last_runner.plot_rank_comparison(
    all_seed_results[last_seed],
    str(RESULTS_DIR / 'rank_comparison.png'),
)

log(f'\n{"=" * 60}')
log(f'Phase 3 complete. All outputs in: {RESULTS_DIR}')
log(f'  - metrics_multi_seed.csv     (mean±std across {N_SEEDS} seeds)')
log(f'  - accuracy_per_seed.csv      (per-seed accuracy breakdown)')
log(f'  - results_seed_*.csv         (per-seed raw results)')
log(f'  - benchmark_results.csv      (combined results)')
log(f'  - per_dataset_results.csv    (full detail)')
log(f'  - accuracy_comparison.png    (bar chart)')
log(f'  - rank_comparison.png        (box plot)')
log(f'{"=" * 60}')
