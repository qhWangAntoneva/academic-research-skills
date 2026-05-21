#!/usr/bin/env python3
"""
Figure 3 -- CBV vs Silhouette Agreement Matrix (contingency heatmap)
=====================================================================
2 x 2 contingency table: Both correct, CBV only, Silhouette only, Both wrong.

Usage:
    uv run python figure3_agreement_matrix.py

Output:
    figure3_agreement_matrix.png (300 DPI)

LaTeX:
    \\begin{figure}[t]
        \\centering
        \\includegraphics[width=0.6\\textwidth]{figures/figure3_agreement_matrix.png}
        \\caption{Agreement Between CBV and Silhouette Across 31 Datasets}
        \\label{fig:agreement-matrix}
    \\end{figure}
"""

import csv
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# 1. Load data and classify
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS_CSV = os.path.join(BASE, "..", "results", "per_dataset_results.csv")

records: list[dict] = []
with open(RESULTS_CSV, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        records.append(row)

# Count categories: (CBV_correct, Silhouette_correct)
# (1,1) Both correct
# (1,0) CBV only correct
# (0,1) Silhouette only correct
# (0,0) Both wrong
both_correct = 0
cbv_only = 0
sil_only = 0
both_wrong = 0

for rec in records:
    cbv_c = int(rec["CBV_correct"])
    sil_c = int(rec["Silhouette_correct"])
    if cbv_c == 1 and sil_c == 1:
        both_correct += 1
    elif cbv_c == 1 and sil_c == 0:
        cbv_only += 1
    elif cbv_c == 0 and sil_c == 1:
        sil_only += 1
    else:
        both_wrong += 1

# Build 2x2 matrix
# Rows: CBV (correct / wrong)
# Cols: Silhouette (correct / wrong)
contingency = np.array([
    [both_correct, sil_only],   # CBV correct
    [cbv_only,     both_wrong],  # CBV wrong
])

total = contingency.sum()
row_labels = ["CBV Correct", "CBV Wrong"]
col_labels = ["Silhouette Correct", "Silhouette Wrong"]

# ---------------------------------------------------------------------------
# 2. Plot heatmap
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
})

fig, ax = plt.subplots(figsize=(5.5, 4.5))

# Color map: green tones for agreement, orange tones for disagreement
# Both correct -> green, Both wrong -> red, off-diagonal -> amber
cmap_colors = ["#009988", "#EE7733", "#EE7733", "#CC3311"]
cmap = matplotlib.colors.ListedColormap(cmap_colors)
bounds = [0, 1, 2, 3, 4]
norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

# We'll build a color grid manually
color_grid = np.zeros_like(contingency, dtype=float)
color_grid[0, 0] = 0  # both correct
color_grid[0, 1] = 1  # sil wrong, cbv correct -> amber
color_grid[1, 0] = 2  # cbv wrong, sil correct -> amber
color_grid[1, 1] = 3  # both wrong

im = ax.imshow(color_grid, cmap=cmap, norm=norm, aspect="auto")

# Annotate each cell with count + percentage
for r in range(2):
    for c in range(2):
        val = contingency[r, c]
        pct = val / total * 100
        text_color = "white" if val == both_correct or val == both_wrong else "black"
        ax.text(c, r, f"{val}\n({pct:.0f}%)", ha="center", va="center",
                fontsize=13, fontweight="bold", color=text_color)

# Labels
ax.set_xticks(range(2))
ax.set_yticks(range(2))
ax.set_xticklabels(col_labels, fontsize=9)
ax.set_yticklabels(row_labels, fontsize=9)
ax.set_xlabel("Silhouette", fontweight="bold")
ax.set_ylabel("CBV", fontweight="bold")

# APA 7 styling
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.7)
ax.spines["bottom"].set_linewidth(0.7)
ax.tick_params(axis="both", which="both", length=3)

ax.set_title("Figure 3. Agreement Between CBV and Silhouette\nAcross 31 Datasets",
             fontweight="bold", pad=12)

fig.text(0.5, -0.01,
         f"Note. Green = agreement; amber = disagreement; red = both wrong. "
         f"Total N = {total} datasets.",
         ha="center", fontsize=7.5, fontstyle="italic",
         transform=ax.transAxes)

plt.tight_layout()

out_path = os.path.join(BASE, "figure3_agreement_matrix.png")
fig.savefig(out_path, dpi=300, bbox_inches="tight")
print(f"Saved: {out_path}")
print(f"  Both correct: {both_correct}")
print(f"  CBV only:     {cbv_only}")
print(f"  Silhouette only: {sil_only}")
print(f"  Both wrong:   {both_wrong}")
plt.close(fig)
