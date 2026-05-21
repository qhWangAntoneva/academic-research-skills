#!/usr/bin/env python3
"""
Figure 2 -- Rank Distribution (box plot)
=========================================
Box plot of rank distribution per CV index across all 31 datasets.
Lower rank = better (rank 1 = smallest |k_hat - k_true|).

Usage:
    uv run python figure2_rank_distribution.py

Output:
    figure2_rank_distribution.png (300 DPI)

LaTeX:
    \\begin{figure}[t]
        \\centering
        \\includegraphics[width=\\textwidth]{figures/figure2_rank_distribution.png}
        \\caption{Rank Distribution Across Datasets}
        \\label{fig:rank-dist}
    \\end{figure}
"""

import csv
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# 1. Load per-dataset results
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS_CSV = os.path.join(BASE, "..", "results", "per_dataset_results.csv")

# Indices to include (6, excluding DUD)
INDEX_COLS = [
    ("Gap Statistic",  "Gap Statistic_k",  "Gap Statistic_correct"),
    ("CH Index",       "CH Index_k",       "CH Index_correct"),
    ("Silhouette",     "Silhouette_k",     "Silhouette_correct"),
    ("CBV",            "CBV_k",            "CBV_correct"),
    ("Davies-Bouldin", "Davies-Bouldin_k", "Davies-Bouldin_correct"),
    ("Dunn Index",     "Dunn Index_k",     "Dunn Index_correct"),
]

records: list[dict] = []
with open(RESULTS_CSV, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        records.append(row)

# ---------------------------------------------------------------------------
# 2. Compute ranks per dataset
# ---------------------------------------------------------------------------
# For each dataset, compute |k_hat - k_true| for all 6 indices, then rank.
# Use fractional (average) ranking for ties: same error -> same rank (mean).
def rank_array(values):
    """Return fractional ranks (1=best)."""
    n = len(values)
    order = np.argsort(values)
    ranks = np.empty(n, dtype=float)
    i = 0
    while i < n:
        j = i
        while j < n and values[order[j]] == values[order[i]]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0   # average of tied positions
        for k in range(i, j):
            ranks[order[k]] = avg_rank
        i = j
    return ranks

index_names: list[str] = []
rank_matrix: list[list[float]] = []  # list of index -> list of ranks across datasets

for name, k_col, _ in INDEX_COLS:
    index_names.append(name)
    ranks_for_index = []
    for rec in records:
        k_true = int(rec["k_true"])
        k_est = int(rec[k_col])
        err = abs(k_est - k_true)
        ranks_for_index.append(err)  # store error first
    rank_matrix.append(ranks_for_index)

# Now compute per-dataset ranks
all_ranks: dict[str, list[float]] = {name: [] for name, _, _ in INDEX_COLS}
for i in range(len(records)):
    errors = []
    for name, k_col, _ in INDEX_COLS:
        k_true = int(records[i]["k_true"])
        k_est = int(records[i][k_col])
        errors.append(abs(k_est - k_true))
    ranks = rank_array(np.array(errors))
    for j, (name, _, _) in enumerate(INDEX_COLS):
        all_ranks[name].append(ranks[j])

# ---------------------------------------------------------------------------
# 3. Plot
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})

CB_PALETTE = ["#0077BB", "#33BBEE", "#009988", "#EE7733", "#CC3311", "#EE3377",
              "#BBBBBB", "#000000"]
box_colors = list(CB_PALETTE[:len(index_names)])
# Make CBV box black
for i, nm in enumerate(index_names):
    if nm == "CBV":
        box_colors[i] = "#000000"

fig, ax = plt.subplots(figsize=(8, 5))

data = [all_ranks[nm] for nm in index_names]

# Customize box properties
bp = ax.boxplot(data, tick_labels=index_names, patch_artist=True,
                widths=0.55, showmeans=True,
                meanprops=dict(marker="D", markerfacecolor="white",
                               markeredgecolor="black", markersize=6),
                medianprops=dict(color="black", linewidth=1.5),
                flierprops=dict(marker="o", markerfacecolor="gray",
                                markersize=4, markeredgecolor="gray",
                                alpha=0.6),
                whiskerprops=dict(linewidth=0.8),
                capprops=dict(linewidth=0.8),
                )

for patch, color in zip(bp["boxes"], box_colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.75)
    patch.set_edgecolor("gray")
    patch.set_linewidth(0.7)

# APA 7 styling
ax.set_ylabel("Rank (lower is better)")
ax.set_xticklabels(index_names, rotation=25, ha="right")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.7)
ax.spines["bottom"].set_linewidth(0.7)
ax.tick_params(axis="both", which="both", length=3)
ax.set_yticks(np.arange(1, 7, 1))

ax.set_title("Figure 2. Rank Distribution Across Datasets",
             fontweight="bold", pad=12)

fig.text(0.5, -0.01,
         "Note. Ranks computed by absolute error |k_hat - k_true|. "
         "Lower rank = better. Diamond = mean; solid line = median.",
         ha="center", fontsize=7.5, fontstyle="italic",
         transform=ax.transAxes)

plt.tight_layout()

out_path = os.path.join(BASE, "figure2_rank_distribution.png")
fig.savefig(out_path, dpi=300, bbox_inches="tight")
print(f"Saved: {out_path}")
plt.close(fig)
