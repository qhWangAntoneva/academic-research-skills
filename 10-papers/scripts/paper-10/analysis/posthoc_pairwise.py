"""
Phase F-9 M4 — Post-hoc Pairwise Comparisons for Paper #10.

Computes:
1. Friedman test (already reported: chi2=247.6, p<0.0001)
2. Nemenyi post-hoc test (pairwise CD diagram)
3. Paired Wilcoxon signed-rank tests with Holm-Bonferroni correction
"""

import numpy as np
import pandas as pd
from scipy import stats
from itertools import combinations
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def load_results():
    """Load per-dataset results."""
    df = pd.read_csv(RESULTS_DIR / "per_dataset_results.csv")
    # Drop DUD Index
    drop_cols = [c for c in df.columns if "DUD" in c]
    df = df.drop(columns=drop_cols, errors="ignore")
    return df


def friedman_test(df):
    """Friedman test across all indices."""
    correct_cols = [c for c in df.columns if c.endswith("_correct")]
    idx_names = [c[:-8] for c in correct_cols]
    
    # Build matrix: datasets × indices (accuracy per dataset)
    data = df[correct_cols].values.astype(float)
    
    # Friedman test
    chi2, p = stats.friedmanchisquare(*[data[:, i] for i in range(data.shape[1])])
    return chi2, p, idx_names


def nemenyi_critical_difference(n_indices, n_datasets, alpha=0.05):
    """Approximate critical difference for Nemenyi test.
    
    Uses the table-based approximation from Demšar (2006).
    """
    # Studentized range q values for alpha=0.05 (approximate)
    # For large n_datasets, use the asymptotic formula
    q_alpha = {2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850,
               7: 2.949, 8: 3.031, 9: 3.102, 10: 3.164}
    
    q = q_alpha.get(n_indices, 3.164)  # Default for k>10
    cd = q * np.sqrt(n_indices * (n_indices + 1) / (6 * n_datasets))
    return cd


def wilcoxon_holm_bonferroni(df, alpha=0.05):
    """Paired Wilcoxon signed-rank tests with Holm-Bonferroni correction."""
    correct_cols = [c for c in df.columns if c.endswith("_correct")]
    idx_names = [c[:-8] for c in correct_cols]
    n = len(df)
    
    results = []
    for i, j in combinations(range(len(idx_names)), 2):
        col_i = correct_cols[i]
        col_j = correct_cols[j]
        
        diff = df[col_i].values.astype(float) - df[col_j].values.astype(float)
        
        # Skip if all differences are zero
        if np.all(diff == 0):
            continue
        
        # Wilcoxon signed-rank test
        try:
            stat, p_val = stats.wilcoxon(diff, alternative="two-sided")
        except ValueError:
            # All differences are zero
            continue
        
        mean_i = df[col_i].mean()
        mean_j = df[col_j].mean()
        
        results.append({
            "Index A": idx_names[i],
            "Index B": idx_names[j],
            "Mean A": mean_i,
            "Mean B": mean_j,
            "Mean Diff": mean_i - mean_j,
            "Wilcoxon stat": stat,
            "p-value": p_val,
        })
    
    if not results:
        return pd.DataFrame()
    
    results_df = pd.DataFrame(results)
    
    # Holm-Bonferroni correction
    results_df = results_df.sort_values("p-value").reset_index(drop=True)
    m = len(results_df)
    results_df["rank"] = range(1, m + 1)
    results_df["adjusted_alpha"] = alpha / (m - results_df["rank"] + 1)
    results_df["Significant"] = results_df["p-value"] < results_df["adjusted_alpha"]
    
    return results_df


def main():
    print("=" * 70)
    print("  M4: Post-hoc Pairwise Comparisons")
    print("=" * 70)
    
    df = load_results()
    
    # ── 1. Friedman Test ──
    print("\n── 1. Friedman Test ──")
    chi2, p, idx_names = friedman_test(df)
    print(f"  χ² = {chi2:.1f}, p = {p:.6f}")
    print(f"  Indices: {', '.join(idx_names)}")
    print(f"  Datasets: {len(df)}")
    
    # ── 2. Nemenyi Critical Difference ──
    print("\n── 2. Nemenyi Critical Difference ──")
    cd = nemenyi_critical_difference(len(idx_names), len(df))
    print(f"  CD(α=0.05, k={len(idx_names)}, N={len(df)}) = {cd:.3f}")
    
    # Compute mean rank of each index
    correct_cols = [c for c in df.columns if c.endswith("_correct")]
    means = {c[:-8]: df[c].mean() for c in correct_cols}
    sorted_indices = sorted(means.keys(), key=lambda x: means[x], reverse=True)
    
    print("\n  Mean accuracy ranking (best to worst):")
    for rank, idx in enumerate(sorted_indices, 1):
        print(f"    {rank:2d}. {idx:20s}: {means[idx]:.3f}")
    
    # ── 3. Paired Wilcoxon + Holm-Bonferroni ──
    print("\n── 3. Paired Wilcoxon Signed-Rank Tests (Holm-Bonferroni, α=0.05) ──")
    wilcox_df = wilcoxon_holm_bonferroni(df, alpha=0.05)
    
    if len(wilcox_df) > 0:
        sig = wilcox_df[wilcox_df["Significant"] == True]
        non_sig = wilcox_df[wilcox_df["Significant"] == False]
        
        print(f"\n  Significant pairs ({len(sig)}):")
        for _, row in sig.iterrows():
            direction = ">" if row["Mean Diff"] > 0 else "<"
            print(f"    {row['Index A']:20s} {direction} {row['Index B']:20s} "
                  f"(Δ={row['Mean Diff']:+.3f}, p={row['p-value']:.4f})")
        
        print(f"\n  Non-significant pairs ({len(non_sig)}):")
        for _, row in non_sig.head(10).iterrows():
            print(f"    {row['Index A']:20s} ≈ {row['Index B']:20s} "
                  f"(Δ={row['Mean Diff']:+.3f}, p={row['p-value']:.4f})")
        
        # CBV vs others
        print("\n── CBV vs Each Index ──")
        cbv_pairs = wilcox_df[
            (wilcox_df["Index A"] == "CBV") | (wilcox_df["Index B"] == "CBV")
        ]
        for _, row in cbv_pairs.iterrows():
            other = row["Index B"] if row["Index A"] == "CBV" else row["Index A"]
            diff = row["Mean Diff"] if row["Index A"] == "CBV" else -row["Mean Diff"]
            sig_mark = "*" if row["Significant"] else " "
            print(f"  CBV vs {other:20s}: Δ={diff:+.3f} {sig_mark} (p={row['p-value']:.4f})")
    
    # Save results
    output_path = RESULTS_DIR / "posthoc_pairwise.csv"
    wilcox_df.to_csv(output_path, index=False)
    print(f"\n  Saved to {output_path}")


if __name__ == "__main__":
    main()
