"""
Phase F-9 C1 — Enhanced Complementarity Analysis for Paper #10.

Addresses Reviewer C1: "Quantify complementarity"
  1. OR-ensemble accuracy: accept CBV OR best-geometric as correct
  2. Jaccard coefficient between correct sets
  3. Per-dataset correct/incorrect binary matrix
  4. CBV vs Gap per-dataset scatter plot
  5. Complementarity index: (ensemble - best_single) / (oracle - best_single)
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Geometric CVI names (exclude CBV variants and DUD)
GEOMETRIC_INDICES = [
    "Silhouette", "CH Index", "Davies-Bouldin", "Gap Statistic",
    "Dunn Index", "Hartigan", "KL Index", "Jump Statistic", "McClain-Rao",
]


def load_results(seed: int = None) -> pd.DataFrame:
    """Load per-dataset results, optionally for a specific seed."""
    if seed is not None:
        path = RESULTS_DIR / f"results_seed_{seed}.csv"
    else:
        path = RESULTS_DIR / "per_dataset_results.csv"
    df = pd.read_csv(path)
    # Drop DUD Index columns if present
    drop_cols = [c for c in df.columns if "DUD" in c]
    df = df.drop(columns=drop_cols, errors="ignore")
    return df


def compute_oracle_accuracy(df: pd.DataFrame) -> float:
    """Oracle: at least one index is correct on each dataset."""
    correct_cols = [c for c in df.columns if c.endswith("_correct")]
    oracle = df[correct_cols].any(axis=1).mean()
    return float(oracle)


def compute_oracle_count(df: pd.DataFrame) -> int:
    """Number of datasets where at least one index is correct."""
    correct_cols = [c for c in df.columns if c.endswith("_correct")]
    return int(df[correct_cols].any(axis=1).sum())


def compute_ensemble_accuracy(df: pd.DataFrame, ensemble_indices: list) -> float:
    """OR-ensemble: correct if ANY index in the list is correct."""
    cols = [f"{idx}_correct" for idx in ensemble_indices
            if f"{idx}_correct" in df.columns]
    return float(df[cols].any(axis=1).mean())


def compute_jaccard(set_a: set, set_b: set) -> float:
    """Jaccard similarity coefficient."""
    if not set_a and not set_b:
        return 1.0
    return len(set_a & set_b) / len(set_a | set_b)


def compute_correct_sets(df: pd.DataFrame) -> dict:
    """For each index, the set of datasets where it is correct."""
    result = {}
    for col in df.columns:
        if col.endswith("_correct"):
            idx_name = col[:-8]  # remove "_correct"
            result[idx_name] = set(df.loc[df[col].astype(bool), "dataset"])
    return result


def compute_per_dataset_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Binary matrix: datasets × indices, 1=correct, 0=incorrect."""
    correct_cols = [c for c in df.columns if c.endswith("_correct")]
    matrix = df[["dataset", "k_true"]].copy()
    for col in correct_cols:
        idx_name = col[:-8]
        matrix[idx_name] = df[col].astype(int).values
    return matrix


def complementarity_index(ensemble_acc: float, best_single: float,
                          oracle_acc: float) -> float:
    """CI = (ensemble - best_single) / (oracle - best_single).
    CI=0 means no complementarity; CI=1 means full complementarity."""
    denom = oracle_acc - best_single
    if denom <= 0:
        return 0.0
    return (ensemble_acc - best_single) / denom


def main():
    print("=" * 70)
    print("  C1 Enhanced Complementarity Analysis")
    print("=" * 70)

    # Load multi-seed aggregated results
    df_multi = load_results()  # per_dataset_results.csv (seed=42 default)
    
    # Also load all 5 seeds for cross-seed analysis
    seeds = [42, 73, 123, 256, 999]
    dfs = {}
    for s in seeds:
        try:
            dfs[s] = load_results(seed=s)
        except FileNotFoundError:
            pass

    # ── 1. Correct Sets ──
    correct = compute_correct_sets(df_multi)
    cbv_correct = correct.get("CBV", set())
    
    print("\n── Correct Set Sizes ──")
    for idx in sorted(correct.keys()):
        print(f"  {idx:20s}: {len(correct[idx]):3d} / {len(df_multi)} datasets")
    
    # ── 2. Jaccard Coefficients (CBV vs each geometric CVI) ──
    print("\n── Jaccard Coefficients (CBV vs Geometric CVIs) ──")
    jaccard_results = {}
    for idx in GEOMETRIC_INDICES:
        if idx in correct:
            j = compute_jaccard(cbv_correct, correct[idx])
            jaccard_results[idx] = j
            print(f"  CBV vs {idx:20s}: J = {j:.3f}")
    
    avg_jaccard = np.mean(list(jaccard_results.values()))
    print(f"\n  Mean Jaccard across geometric CVIs: {avg_jaccard:.3f}")
    
    # ── 3. OR-Ensemble Accuracies ──
    print("\n── OR-Ensemble Accuracies ──")
    
    # Best single geometric CVI
    best_geo = max(GEOMETRIC_INDICES,
                   key=lambda x: compute_ensemble_accuracy(df_multi, [x]))
    best_geo_acc = compute_ensemble_accuracy(df_multi, [best_geo])
    print(f"  Best single geometric: {best_geo} = {best_geo_acc:.4f}")
    
    # CBV alone
    cbv_acc = compute_ensemble_accuracy(df_multi, ["CBV"])
    print(f"  CBV alone:                    {cbv_acc:.4f}")
    
    # CBV + best geometric (pairwise ensemble)
    pair_acc = compute_ensemble_accuracy(df_multi, ["CBV", best_geo])
    print(f"  CBV + {best_geo:20s}:     {pair_acc:.4f}")
    
    # CBV + all geometric
    all_geo_acc = compute_ensemble_accuracy(df_multi, GEOMETRIC_INDICES)
    print(f"  All geometric only:           {all_geo_acc:.4f}")
    
    cbv_all_geo = compute_ensemble_accuracy(df_multi, ["CBV"] + GEOMETRIC_INDICES)
    print(f"  CBV + all geometric:          {cbv_all_geo:.4f}")
    
    # Oracle
    oracle_acc = compute_oracle_accuracy(df_multi)
    oracle_count = compute_oracle_count(df_multi)
    print(f"\n  Oracle (any correct):         {oracle_acc:.4f} ({oracle_count}/{len(df_multi)} datasets)")
    
    # Complementarity index
    ci_pair = complementarity_index(pair_acc, best_geo_acc, oracle_acc)
    ci_all = complementarity_index(cbv_all_geo, all_geo_acc, oracle_acc)
    print(f"\n  Complementarity Index (CBV+{best_geo}): {ci_pair:.3f}")
    print(f"  Complementarity Index (CBV+all):       {ci_all:.3f}")
    
    # ── 4. Per-Dataset Binary Matrix ──
    matrix = compute_per_dataset_matrix(df_multi)
    matrix_path = RESULTS_DIR / "complementarity_matrix.csv"
    matrix.to_csv(matrix_path, index=False)
    print(f"\n── Per-Dataset Matrix saved to {matrix_path} ──")
    
    # ── 5. Datasets where CBV is unique success ──
    print("\n── CBV-Unique Successes (CBV correct, all geometric wrong) ──")
    geo_correct_cols = [f"{g}_correct" for g in GEOMETRIC_INDICES
                        if f"{g}_correct" in df_multi.columns]
    any_geo_correct = df_multi[geo_correct_cols].any(axis=1)
    cbv_only = df_multi[df_multi["CBV_correct"].astype(bool) & ~any_geo_correct]
    for _, row in cbv_only.iterrows():
        print(f"  + {row['dataset']:45s} k_true={row['k_true']}")
    
    print(f"\n  Total CBV-unique successes: {len(cbv_only)}")
    
    # Datasets where all geometric correct but CBV wrong
    print("\n── Geometric-Only Successes (all geometric correct, CBV wrong) ──")
    cbv_wrong_all_geo = ~df_multi["CBV_correct"].astype(bool) & any_geo_correct
    geo_only = df_multi[cbv_wrong_all_geo]
    for _, row in geo_only.iterrows():
        print(f"  - {row['dataset']:45s} k_true={row['k_true']}")
    print(f"  Total geometric-only successes: {len(geo_only)}")
    
    # ── 6. Datasets where CBV correct AND at least one geometric correct ──
    both_correct = df_multi["CBV_correct"].astype(bool) & any_geo_correct
    both_count = int(both_correct.sum())
    print(f"\n── Both CBV and at least one geometric correct: {both_count} datasets ──")
    
    # ── 7. Cross-seed stability of complementarity ──
    print("\n── Cross-Seed Stability (OR-ensemble CBV+Gap) ──")
    for s, d in sorted(dfs.items()):
        ens_acc = compute_ensemble_accuracy(d, ["CBV", "Gap Statistic"])
        cbv_s = compute_ensemble_accuracy(d, ["CBV"])
        gap_s = compute_ensemble_accuracy(d, ["Gap Statistic"])
        oracle_s = compute_oracle_accuracy(d)
        ci_s = complementarity_index(ens_acc, max(cbv_s, gap_s), oracle_s)
        print(f"  Seed {s}: CBV={cbv_s:.3f} Gap={gap_s:.3f} "
              f"Ensemble={ens_acc:.3f} Oracle={oracle_s:.3f} CI={ci_s:.3f}")
    
    # ═══════════════════════════════════════════════════════════════
    # FIGURES
    # ═══════════════════════════════════════════════════════════════
    
    # Figure: CBV vs Gap scatter (per-dataset)
    fig, ax = plt.subplots(figsize=(7, 6))
    cbv_k = df_multi["CBV_k"].values
    gap_k = df_multi["Gap Statistic_k"].values
    k_true = df_multi["k_true"].values
    
    both_correct_mask = df_multi["CBV_correct"].astype(bool).values & \
                        df_multi["Gap Statistic_correct"].astype(bool).values
    cbv_only_mask = df_multi["CBV_correct"].astype(bool).values & \
                    ~df_multi["Gap Statistic_correct"].astype(bool).values
    gap_only_mask = ~df_multi["CBV_correct"].astype(bool).values & \
                    df_multi["Gap Statistic_correct"].astype(bool).values
    both_wrong_mask = ~df_multi["CBV_correct"].astype(bool).values & \
                      ~df_multi["Gap Statistic_correct"].astype(bool).values
    
    ax.scatter(cbv_k[both_correct_mask], gap_k[both_correct_mask],
               c="green", marker="o", s=40, alpha=0.7, label=f"Both correct ({both_correct_mask.sum()})")
    ax.scatter(cbv_k[cbv_only_mask], gap_k[cbv_only_mask],
               c="blue", marker="^", s=50, alpha=0.8, label=f"CBV only ({cbv_only_mask.sum()})")
    ax.scatter(cbv_k[gap_only_mask], gap_k[gap_only_mask],
               c="red", marker="v", s=50, alpha=0.8, label=f"Gap only ({gap_only_mask.sum()})")
    ax.scatter(cbv_k[both_wrong_mask], gap_k[both_wrong_mask],
               c="gray", marker="x", s=30, alpha=0.6, label=f"Both wrong ({both_wrong_mask.sum()})")
    
    # Diagonal line (perfect agreement)
    k_max = max(int(cbv_k.max()), int(gap_k.max()), int(k_true.max())) + 1
    ax.plot([0, k_max], [0, k_max], "k--", alpha=0.3, label="k(CBV) = k(Gap)")
    
    ax.set_xlabel("CBV Estimated k", fontsize=12)
    ax.set_ylabel("Gap Statistic Estimated k", fontsize=12)
    ax.set_title("CBV vs. Gap Statistic: Per-Dataset k Estimates", fontsize=13)
    ax.legend(fontsize=9, loc="upper left")
    ax.set_xlim(-0.5, k_max)
    ax.set_ylim(-0.5, k_max)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    scatter_path = FIGURES_DIR / "cbv_vs_gap_scatter.png"
    fig.savefig(scatter_path, dpi=150, bbox_inches="tight")
    print(f"\n── Saved: {scatter_path} ──")
    plt.close(fig)
    
    # Figure: Jaccard bar chart
    fig, ax = plt.subplots(figsize=(8, 4))
    idxs = sorted(jaccard_results.keys())
    vals = [jaccard_results[i] for i in idxs]
    colors = ["#2196F3" if v > avg_jaccard else "#FF9800" for v in vals]
    bars = ax.barh(idxs, vals, color=colors, edgecolor="gray")
    ax.axvline(x=avg_jaccard, color="red", linestyle="--", linewidth=1,
               label=f"Mean Jaccard = {avg_jaccard:.3f}")
    ax.set_xlabel("Jaccard Similarity of Correct Sets", fontsize=11)
    ax.set_title("CBV Complementarity: Jaccard Index vs. Geometric CVIs", fontsize=12)
    ax.legend(fontsize=9)
    ax.set_xlim(0, 1)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                f"{val:.3f}", va="center", fontsize=9)
    fig.tight_layout()
    jaccard_path = FIGURES_DIR / "jaccard_complementarity.png"
    fig.savefig(jaccard_path, dpi=150, bbox_inches="tight")
    print(f"── Saved: {jaccard_path} ──")
    plt.close(fig)
    
    # Figure: Correct/incorrect heatmap
    fig, ax = plt.subplots(figsize=(14, 12))
    # Sort by k_true then by dataset name
    matrix_sorted = matrix.sort_values(["k_true", "dataset"]).reset_index(drop=True)
    idx_cols = [c for c in matrix_sorted.columns if c not in ("dataset", "k_true")]
    heatmap_data = matrix_sorted[idx_cols].values
    im = ax.imshow(heatmap_data, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_yticks(range(len(matrix_sorted)))
    ax.set_yticklabels([f"{r['dataset']} (k={r['k_true']})"
                        for _, r in matrix_sorted.iterrows()], fontsize=6)
    ax.set_xticks(range(len(idx_cols)))
    ax.set_xticklabels(idx_cols, rotation=45, ha="right", fontsize=8)
    ax.set_title("Per-Dataset Correctness Matrix (green=correct, red=incorrect)", fontsize=11)
    cbar = fig.colorbar(im, ax=ax, shrink=0.6, label="Correct (1) / Incorrect (0)")
    fig.tight_layout()
    heatmap_path = FIGURES_DIR / "complementarity_heatmap.png"
    fig.savefig(heatmap_path, dpi=150, bbox_inches="tight")
    print(f"── Saved: {heatmap_path} ──")
    plt.close(fig)
    
    # ═══════════════════════════════════════════════════════════════
    # Summary for manuscript
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("  SUMMARY FOR MANUSCRIPT (§5.5)")
    print("=" * 70)
    print(f"""
  Jaccard(CBV, {best_geo}) = {jaccard_results.get(best_geo, 0):.3f}
  Mean Jaccard across 9 geometric CVIs = {avg_jaccard:.3f}
  
  OR-Ensemble (CBV + {best_geo}):
    Accuracy = {pair_acc:.1%}  (vs CBV {cbv_acc:.1%}, {best_geo} {best_geo_acc:.1%})
    Complementarity Index = {ci_pair:.3f}
  
  OR-Ensemble (CBV + all 9 geometric):
    Accuracy = {cbv_all_geo:.1%}  (vs best-geometric {all_geo_acc:.1%})
    Complementarity Index = {ci_all:.3f}
  
  Oracle (any index correct): {oracle_acc:.1%} ({oracle_count}/{len(df_multi)} datasets)
  
  CBV-unique successes: {len(cbv_only)} datasets
  Gap-unique successes: {len(geo_only)} datasets
  Both correct: {both_count} datasets
""")


if __name__ == "__main__":
    main()
