"""
Phase 3: Full Benchmark — Paper #10 (CBV)

Runs all 7 CV indices on 25+ synthetic + 5 real-world datasets.
Saves results CSV + accuracy/rank plots to results/ directory.
"""
import sys, os, warnings, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings('ignore')
os.environ['PYTHONIOENCODING'] = 'utf-8'

import numpy as np
import pandas as pd
from pathlib import Path

from cbv import CBVHybrid
from benchmark import SyntheticDataGenerator, RealDataLoader, BenchmarkRunner
from comparison import get_all_indices

RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Log to file instead of stdout to avoid buffering issues in background tasks
LOG = RESULTS_DIR / 'benchmark.log'
def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f'{time.strftime("%H:%M:%S")} {msg}\n')
    print(msg, flush=True)

log('=' * 60)
log('Phase 3: Full Benchmark — Paper #10 (CBV)')
log('=' * 60)

# ── 1. Build datasets ──
log('\n[1/4] Building datasets...')
gen = SyntheticDataGenerator(random_state=42)
synthetic_suite = gen.generate_benchmark_suite()
log(f'  Synthetic: {len(synthetic_suite)} datasets')

loader = RealDataLoader()
real_suite = loader.load_all(include_seeds=True)  # Seeds now enabled
log(f'  Real: {len(real_suite)} datasets')

all_datasets = synthetic_suite + real_suite
log(f'  Total: {len(all_datasets)} datasets')

# ── 2. Build indices ──
log('\n[2/4] Building indices...')
K_RANGE = (2, 10)
N_BOOT = 10  # fast mode for benchmark; use 999 for publication

indices = get_all_indices(k_range=K_RANGE, random_state=42)

# Add CBVHybrid (replaces standalone CBVIndex — spectral fusion improves CBV accuracy)
class CBVAdapter:
    def __init__(self, k_range=K_RANGE, n_boot=N_BOOT, random_state=42):
        self.name = 'CBV'
        self.idx = CBVHybrid(k_range=k_range, n_boot=n_boot, random_state=random_state, fast=True, vote_method='mode', use_excess_mass=False)
    def fit(self, X):
        self.idx.fit(X)
        return self
    def predict(self):
        return self.idx.predict()

indices.append(CBVAdapter(k_range=K_RANGE, n_boot=N_BOOT, random_state=42))

log(f'  {len(indices)} indices: {[i.name for i in indices]}')

# ── 3. Run benchmark ──
log('\n[3/4] Running benchmark (all 7 indices, including DUD)...')
t0 = time.time()

runner = BenchmarkRunner(indices, all_datasets, random_state=42)
results = runner.run_all(parallel=True, n_jobs=-1)

elapsed = time.time() - t0
log(f'  Completed in {elapsed:.1f}s')
log(f'  Datasets: {len(results)}')
log(f'  Results shape: {results.shape}')

# Save raw results (all 7 indices — DUD included for reference)
results_path = RESULTS_DIR / 'benchmark_results.csv'
runner.save_results(results, str(results_path))

# ── 4. Summary & plots ──
log('\n[4/4] Generating summary...')
summary = runner.summarize_results(results)

# ── 4a. Main accuracy table (excluding DUD — not designed for k-estimation) ──
EXCLUDED_INDICES = {'DUD Index'}
acc = summary['accuracy']
acc_main = acc[~acc['index'].isin(EXCLUDED_INDICES)].copy()

log('\nAccuracy (fraction correct) — main (DUD excluded, see appendix):')
log(acc_main.to_string(index=False))

# Save main accuracy
acc_main_path = RESULTS_DIR / 'accuracy.csv'
with open(str(acc_main_path), 'w', encoding='utf-8') as f:
    acc_main.to_csv(f, index=False)
log(f'  Main accuracy saved to {acc_main_path}')

# ── 4b. Full accuracy table (including DUD for reference) ──
acc_full_path = RESULTS_DIR / 'accuracy_full.csv'
with open(str(acc_full_path), 'w', encoding='utf-8') as f:
    acc.to_csv(f, index=False)
log(f'  Full accuracy (incl. DUD) saved to {acc_full_path}')

# ── 4c. Mean rank (main) ──
mean_rank = summary['mean_rank']
mean_rank_main = mean_rank[~mean_rank.index.isin(EXCLUDED_INDICES)]
log('\nMean rank (1 = best) — main:')
log(str(mean_rank_main))

# ── 4d. Statistical significance tests ──
friedman = summary.get('friedman', None)
if friedman:
    stat, p_val = friedman
    log(f'\nFriedman test (all indices): chi2={stat:.3f}, p={p_val:.4f}')
    if p_val < 0.05:
        log('  → Significant: indices differ in estimated ranks (p < 0.05)')
    else:
        log('  → Not significant: no evidence of rank differences')

# Nemenyi post-hoc
nemenyi = summary.get('nemenyi', None)
if nemenyi is not None:
    # Filter to main indices only
    nemenyi_main = nemenyi.loc[
        [i for i in nemenyi.index if i not in EXCLUDED_INDICES],
        [i for i in nemenyi.columns if i not in EXCLUDED_INDICES],
    ]
    log('\nNemenyi post-hoc p-values (main indices):')
    for i in nemenyi_main.index:
        for j in nemenyi_main.columns:
            if i < j:
                p = nemenyi_main.loc[i, j]
                star = ' *' if p < 0.05 else ''
                log(f'  {i} vs {j}: p={p:.4f}{star}')

# ── 4e. Plots (main indices only) ──
log('\nGenerating plots...')

# Re-rank excluding DUD for the rank plot
index_names = [name for name, _ in runner._resolved_indices]
main_idx_names = [n for n in index_names if n not in EXCLUDED_INDICES]
suffix_k = '_k'
k_cols = [f'{n}{suffix_k}' for n in main_idx_names]
k_cols = [c for c in k_cols if c in results.columns]
available_main = [c.replace(suffix_k, '') for c in k_cols]

# Manual rank computation for main indices only
rank_data = {}
for _, row in results.iterrows():
    k_true = row['k_true']
    scores = {}
    for idx_name in main_idx_names:
        col = f'{idx_name}{suffix_k}'
        k_hat = row[col]
        if k_hat < 0:
            abs_err = float('inf')
        else:
            abs_err = abs(int(k_hat) - int(k_true))
        scores[idx_name] = abs_err
    ranked = sorted(scores.items(), key=lambda x: x[1])
    for rank_pos, (idx_name, _) in enumerate(ranked, start=1):
        if idx_name not in rank_data:
            rank_data[idx_name] = []
        rank_data[idx_name].append(rank_pos)

rank_df_main = pd.DataFrame(rank_data)
runner.plot_accuracy_comparison(results, str(RESULTS_DIR / 'accuracy_comparison.png'))

# Custom rank plot for main indices
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(max(8, rank_df_main.shape[1] * 0.8), 5))
positions = np.arange(rank_df_main.shape[1])
bp = ax.boxplot(rank_df_main.values, positions=positions, patch_artist=True, showmeans=True,
                meanprops={'marker': 'D', 'markerfacecolor': 'red', 'markersize': 5})
colors = plt.cm.Set2(np.linspace(0, 1, rank_df_main.shape[1]))
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
ax.set_xlabel('Cluster Validity Index')
ax.set_ylabel('Rank (1 = best)')
ax.set_title('Rank Distribution Across Datasets (DUD Excluded)')
ax.set_xticks(positions)
ax.set_xticklabels(rank_df_main.columns, rotation=45, ha='right', fontsize=9)
ax.invert_yaxis()
fig.tight_layout()
rank_plot_path = RESULTS_DIR / 'rank_comparison.png'
fig.savefig(str(rank_plot_path), dpi=150, bbox_inches='tight')
plt.close(fig)
log(f'  Rank plot saved to {rank_plot_path}')

# ── 4f. Per-dataset detail ──
detail_path = RESULTS_DIR / 'per_dataset_results.csv'
with open(str(detail_path), 'w', encoding='utf-8') as f:
    results.to_csv(f, index=False)

log(f'\n{"=" * 60}')
log(f'Phase 3 complete. All outputs in: {RESULTS_DIR}')
log(f'  - benchmark_results.csv     (full results, all indices)')
log(f'  - per_dataset_results.csv    (full detail)')
log(f'  - accuracy.csv              (main accuracy, DUD excluded)')
log(f'  - accuracy_full.csv         (full accuracy, incl. DUD)')
log(f'  - accuracy_comparison.png   (bar chart)')
log(f'  - rank_comparison.png       (box plot, DUD excluded)')
log(f'{"=" * 60}')
