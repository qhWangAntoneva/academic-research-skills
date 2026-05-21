#!/usr/bin/env python3
"""
Figure 1 -- Accuracy Comparison (bar chart)
=============================================
Benchmark accuracy comparison across 6 cluster validation indices.
DUD Index excluded as it is not designed for k-estimation.

Usage:
    uv run python figure1_accuracy_comparison.py

Output:
    figure1_accuracy_comparison.png (300 DPI)

LaTeX:
    \\begin{figure}[t]
        \\centering
        \\includegraphics[width=\\textwidth]{figures/figure1_accuracy_comparison.png}
        \\caption{Benchmark Accuracy Across Cluster Validation Indices}
        \\label{fig:accuracy-compare}
    \\end{figure}
"""

import csv
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
ACC_CSV = os.path.join(BASE, "..", "results", "accuracy.csv")

indices: list[str] = []
accuracies: list[float] = []

with open(ACC_CSV, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row["index"].strip()
        if name == "DUD Index":
            continue  # excluded
        indices.append(name)
        accuracies.append(float(row["accuracy"]))

# ---------------------------------------------------------------------------
# 2. Colorblind-safe palette
# ---------------------------------------------------------------------------
CB_PALETTE = ["#0077BB", "#33BBEE", "#009988", "#EE7733", "#CC3311", "#EE3377",
              "#BBBBBB", "#000000"]
# Assign a distinct colour for CBV
bar_colors = []
cbv_idx = None
for i, name in enumerate(indices):
    if name == "CBV":
        bar_colors.append("#000000")   # black for emphasis
        cbv_idx = i
    else:
        bar_colors.append(CB_PALETTE[i % len(CB_PALETTE)])

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

fig, ax = plt.subplots(figsize=(8, 5))

x = np.arange(len(indices))
width = 0.60

bars = ax.bar(x, accuracies, width, color=bar_colors, edgecolor="gray",
              linewidth=0.5, zorder=3)

# Annotate value above each bar
for bar, val in zip(bars, accuracies):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.015,
            f"{val:.3f}", ha="center", va="bottom", fontsize=8, fontweight="bold")

# Dashed reference line at CBV accuracy level
cbv_acc = accuracies[cbv_idx]
ax.axhline(y=cbv_acc, color="#EE7733", linestyle="--", linewidth=1.2,
           zorder=2)
ax.text(len(indices) - 0.2, cbv_acc + 0.01, f"CBV = {cbv_acc:.3f}",
        color="#EE7733", fontsize=8, ha="right", va="bottom",
        fontweight="bold")

# Axes styling (APA 7: no top/right spines)
ax.set_xticks(x)
ax.set_xticklabels(indices, rotation=25, ha="right")
ax.set_ylabel("Accuracy")
ax.set_ylim(0, 1.05)
ax.set_yticks(np.arange(0, 1.1, 0.1))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}"))

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.7)
ax.spines["bottom"].set_linewidth(0.7)
ax.tick_params(axis="both", which="both", length=3)

# Title and caption note
ax.set_title("Figure 1. Benchmark Accuracy Across Cluster Validation Indices",
             fontweight="bold", pad=12)

fig.text(0.5, -0.01,
         "Note. Based on 31 datasets (25 synthetic + 6 real). "
         "DUD Index excluded as it is not designed for k-estimation.",
         ha="center", fontsize=7.5, fontstyle="italic",
         transform=ax.transAxes)

plt.tight_layout()

out_path = os.path.join(BASE, "figure1_accuracy_comparison.png")
fig.savefig(out_path, dpi=300, bbox_inches="tight")
print(f"Saved: {out_path}")
plt.close(fig)
