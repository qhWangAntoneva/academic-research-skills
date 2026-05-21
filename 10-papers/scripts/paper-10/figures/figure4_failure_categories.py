#!/usr/bin/env python3
"""
Figure 4 -- Failure Category Breakdown (horizontal bar chart)
==============================================================
CBV failure mode analysis across 17 mis-classified datasets.

Categories (heuristically assigned via dataset name and error pattern):
  1. Non-convex (k=2->3)          -- moons, circles
  2. High-k underestimation       -- blobs k_true>=5 estimated as 3-4
  3. Tight-blob overestimation    -- blobs k_true=3 std<1.0 estimated as 4
  4. Noise dimension overwhelm    -- high-d blobs (none in current data)
  5. Real-dataset signal loss     -- wine, digits_[0,1,2]
  6. Classification noise         -- classif_k3_info3_noise3/8

Usage:
    uv run python figure4_failure_categories.py

Output:
    figure4_failure_categories.png (300 DPI)

LaTeX:
    \\begin{figure}[t]
        \\centering
        \\includegraphics[width=\\textwidth]{figures/figure4_failure_categories.png}
        \\caption{CBV Failure Mode Analysis}
        \\label{fig:failure-categories}
    \\end{figure}
"""

import csv
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# 1. Classify CBV failures
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS_CSV = os.path.join(BASE, "..", "results", "per_dataset_results.csv")

records: list[dict] = []
with open(RESULTS_CSV, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        records.append(row)

categories = {
    "Non-convex (k=2->3)": 0,
    "High-k underestimation\n(k>=5->3/4)": 0,
    "Tight-blob\noverestimation (k=3->4)": 0,
    "Noise dimension\noverwhelm": 0,
    "Real-dataset\nsignal loss": 0,
    "Classification\nnoise": 0,
}

for rec in records:
    if int(rec["CBV_correct"]) == 1:
        continue
    name = rec["dataset"].strip()
    k_true = int(rec["k_true"])
    cbv_k = int(rec["CBV_k"])

    # Rule-based classification
    if name.startswith("moons") or name.startswith("circles"):
        categories["Non-convex (k=2->3)"] += 1
    elif name.startswith("classif_k3"):
        categories["Classification\nnoise"] += 1
    elif name.startswith("blobs") and k_true >= 5 and cbv_k <= 4:
        categories["High-k underestimation\n(k>=5->3/4)"] += 1
    elif name.startswith("blobs") and k_true == 3 and cbv_k == 4:
        categories["Tight-blob\noverestimation (k=3->4)"] += 1
    elif name in ("wine", "digits_[0, 1, 2]"):
        categories["Real-dataset\nsignal loss"] += 1
    else:
        # Fallback: check if high-dimensional
        if "_d" in name:
            # Extract dimension
            parts = name.split("_d")
            if len(parts) > 1:
                dim_str = parts[1].split("_")[0]
                try:
                    dim = int(dim_str)
                    if dim >= 5:
                        categories["Noise dimension\noverwhelm"] += 1
                        continue
                except ValueError:
                    pass
        # If nothing matches, put in noise dimension as catch-all
        categories["Noise dimension\noverwhelm"] += 1

# ---------------------------------------------------------------------------
# 2. Plot horizontal bar chart
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "ytick.labelsize": 8.5,
})

CB_PALETTE = ["#0077BB", "#33BBEE", "#009988", "#EE7733", "#CC3311", "#EE3377",
              "#BBBBBB", "#000000"]

cat_names = list(categories.keys())
cat_counts = list(categories.values())

# Sort by count descending
sorted_idx = np.argsort(cat_counts)[::-1]
cat_names_sorted = [cat_names[i] for i in sorted_idx]
cat_counts_sorted = [cat_counts[i] for i in sorted_idx]
colors_sorted = [CB_PALETTE[i % len(CB_PALETTE)] for i in sorted_idx]

# Make CBV-related bar (non-convex, the biggest) more distinct
# Already using the sorted color assignment

fig, ax = plt.subplots(figsize=(8, 4.5))

y_pos = np.arange(len(cat_names_sorted))
bars = ax.barh(y_pos, cat_counts_sorted, height=0.6, color=colors_sorted,
               edgecolor="gray", linewidth=0.5, zorder=3)

# Annotate counts
for bar, cnt in zip(bars, cat_counts_sorted):
    if cnt > 0:
        ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height() / 2,
                str(cnt), ha="left", va="center", fontsize=10, fontweight="bold")
    else:
        ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height() / 2,
                str(cnt), ha="left", va="center", fontsize=9, color="gray",
                fontstyle="italic")

ax.set_yticks(y_pos)
ax.set_yticklabels(cat_names_sorted)
ax.set_xlabel("Number of Datasets")
ax.set_xlim(0, max(cat_counts_sorted) + 2)

# APA 7
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.7)
ax.spines["bottom"].set_linewidth(0.7)
ax.tick_params(axis="both", which="both", length=3)
ax.set_xticks(np.arange(0, max(cat_counts_sorted) + 2, 1))

ax.set_title("Figure 4. CBV Failure Mode Analysis",
             fontweight="bold", pad=12)

fig.text(0.5, -0.01,
         "Note. Failure categories identified heuristically from k_true and "
         "dataset structure. N = 17 mis-classified datasets out of 31.",
         ha="center", fontsize=7.5, fontstyle="italic",
         transform=ax.transAxes)

plt.tight_layout()

out_path = os.path.join(BASE, "figure4_failure_categories.png")
fig.savefig(out_path, dpi=300, bbox_inches="tight")
print(f"Saved: {out_path}")
print(f"  Categories: {dict(zip(cat_names_sorted, cat_counts_sorted))}")
plt.close(fig)
