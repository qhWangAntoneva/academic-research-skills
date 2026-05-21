"""
Phase C — Complementarity Analysis for CBV Benchmark (Paper #10).

Provides:
1. Pairwise agreement matrix (fraction of datasets where indices agree on k)
2. Disagreement profile (which datasets cause largest CBV-vs-other gaps)
3. Failure-pattern analysis (over/under-estimate bias per index)
4. CBV-unique success/failure sets
5. Heatmap figures for paper-ready output
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


class ComplementarityAnalysis:
    """Complementarity analysis for CBV benchmark results.

    Parameters
    ----------
    results_df : pd.DataFrame
        From BenchmarkRunner.run_all(), expected columns:
        dataset, k_true, <index>_k, <index>_correct
    exclude_indices : set of str, default={'DUD Index'}
        Indices to exclude from analysis.
    """

    EXCLUDED_DEFAULT = {"DUD Index"}

    def __init__(
        self,
        results_df: pd.DataFrame,
        exclude_indices: Optional[set] = None,
    ):
        required = {"dataset", "k_true"}
        missing = required - set(results_df.columns)
        if missing:
            raise ValueError(f"results_df missing required columns: {missing}")
        self.df = results_df.copy()
        self.exclude = exclude_indices or self.EXCLUDED_DEFAULT

        # Auto-detect index names from _k and _correct columns
        all_names: set = set()
        for col in self.df.columns:
            if col.endswith("_k") and col != "k_true":
                all_names.add(col[:-2])
        self.index_names = sorted(n for n in all_names if n not in self.exclude)

    # ── 1. Pairwise Agreement Matrix ──

    def pairwise_agreement_matrix(self) -> pd.DataFrame:
        """Fraction of datasets where each pair of indices selects the same k.

        Returns
        -------
        pd.DataFrame, symmetric, values in [0, 1].
        """
        n = len(self.index_names)
        matrix = pd.DataFrame(
            np.eye(n), index=self.index_names, columns=self.index_names,
        )

        for i, idx_i in enumerate(self.index_names):
            col_i = f"{idx_i}_k"
            if col_i not in self.df.columns:
                continue
            for j, idx_j in enumerate(self.index_names):
                if i == j:
                    continue
                col_j = f"{idx_j}_k"
                if col_j not in self.df.columns:
                    continue
                agreement = float(np.mean(self.df[col_i].values == self.df[col_j].values))
                matrix.loc[idx_i, idx_j] = agreement

        return matrix

    def plot_agreement_heatmap(
        self, save_path: Optional[str] = None
    ) -> plt.Figure:
        """Heatmap of pairwise agreement matrix."""
        matrix = self.pairwise_agreement_matrix()
        fig, ax = plt.subplots(figsize=(max(6, len(self.index_names) * 0.7),
                                        max(5, len(self.index_names) * 0.6)))

        sns.heatmap(
            matrix, annot=True, fmt=".2f", cmap="YlOrRd",
            vmin=0, vmax=1, ax=ax,
            cbar_kws={"label": "Agreement fraction"},
        )
        ax.set_title("Pairwise Agreement: Indices Select Same k")
        ax.set_xlabel("Index")
        ax.set_ylabel("Index")
        fig.tight_layout()

        if save_path is not None:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
        return fig

    # ── 2. Disagreement Profile ──

    def disagreement_profile(self, target_index: str = "CBV") -> pd.DataFrame:
        """For each dataset, identify which index disagrees most with target.

        Parameters
        ----------
        target_index : str, default='CBV'
            The reference index to measure disagreement from.

        Returns
        -------
        pd.DataFrame with columns: dataset, k_true, {target}_k, <each_index>_abs_diff
        """
        target_col = f"{target_index}_k"
        if target_col not in self.df.columns:
            raise ValueError(f"Target index '{target_index}' not found in results.")

        records: List[Dict] = []
        for _, row in self.df.iterrows():
            rec = {
                "dataset": row["dataset"],
                "k_true": row["k_true"],
                f"{target_index}_k": row[target_col],
            }
            for idx in self.index_names:
                if idx == target_index:
                    continue
                col = f"{idx}_k"
                if col in self.df.columns and row[col] >= 0:
                    rec[f"{idx}_abs_diff"] = abs(int(row[col]) - int(row[target_col]))
                else:
                    rec[f"{idx}_abs_diff"] = np.nan
            records.append(rec)

        return pd.DataFrame(records)

    def top_disagreement_datasets(
        self, target_index: str = "CBV", top_n: int = 10
    ) -> pd.DataFrame:
        """Datasets with largest average disagreement between target and all others."""
        profile = self.disagreement_profile(target_index)
        diff_cols = [c for c in profile.columns if c.endswith("_abs_diff")]

        profile["mean_disagreement"] = profile[diff_cols].mean(axis=1, skipna=True)
        profile = profile.sort_values("mean_disagreement", ascending=False)

        return profile.head(top_n)[
            ["dataset", "k_true", f"{target_index}_k", "mean_disagreement"]
        ]

    # ── 3. Failure-Pattern Analysis ──

    def failure_patterns(self) -> pd.DataFrame:
        """Characterize each index's bias and failure profile.

        Returns
        -------
        pd.DataFrame with columns:
            index, accuracy, bias (mean signed error > 0 = overestimate),
            std_error, over_count, under_count, high_k_count, k_5plus_fail_rate
        """
        records: List[Dict] = []
        for idx in self.index_names:
            k_col = f"{idx}_k"
            corr_col = f"{idx}_correct"
            if k_col not in self.df.columns:
                continue

            # Accuracy
            accuracy = float(self.df[corr_col].mean()) if corr_col in self.df.columns else np.nan

            # Signed error: k_hat - k_true
            signed_err = self.df[k_col].values - self.df["k_true"].values
            valid = signed_err >= -self.df["k_true"].values  # k_hat >= 0
            signed_err = signed_err[valid]

            if len(signed_err) == 0:
                continue

            bias = float(np.mean(signed_err))
            std_error = float(np.std(signed_err, ddof=1))
            over_count = int(np.sum(signed_err > 0))
            under_count = int(np.sum(signed_err < 0))

            # High-k failure rate (k_true >= 5)
            high_k_mask = self.df["k_true"].values >= 5
            if high_k_mask.sum() > 0:
                k5plus = high_k_mask[valid]
                high_k_fails = np.mean(signed_err[k5plus] != 0) if k5plus.sum() > 0 else np.nan
            else:
                high_k_fails = np.nan

            records.append({
                "index": idx,
                "accuracy": accuracy,
                "bias": bias,
                "std_error": std_error,
                "over_count": over_count,
                "under_count": under_count,
                "high_k_fail_rate": high_k_fails,
            })

        result = pd.DataFrame(records).sort_values("accuracy", ascending=False)
        return result

    def plot_failure_patterns(
        self, save_path: Optional[str] = None
    ) -> plt.Figure:
        """Bar chart: bias + over/under count per index."""
        patterns = self.failure_patterns()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Left: bias
        colors = ["green" if b < 0 else "red" for b in patterns["bias"]]
        ax1.bar(range(len(patterns)), patterns["bias"], color=colors, edgecolor="gray")
        ax1.axhline(y=0, color="black", linewidth=0.5)
        ax1.set_xticks(range(len(patterns)))
        ax1.set_xticklabels(patterns["index"].values, rotation=45, ha="right", fontsize=8)
        ax1.set_ylabel("Mean Signed Error (k_hat - k_true)")
        ax1.set_title("Estimation Bias by Index")

        # Right: over vs under count
        x = np.arange(len(patterns))
        width = 0.35
        ax2.bar(x - width / 2, patterns["over_count"], width,
                label="Overestimate", color="salmon", edgecolor="gray")
        ax2.bar(x + width / 2, patterns["under_count"], width,
                label="Underestimate", color="lightblue", edgecolor="gray")
        ax2.set_xticks(x)
        ax2.set_xticklabels(patterns["index"].values, rotation=45, ha="right", fontsize=8)
        ax2.set_ylabel("Count")
        ax2.set_title("Over vs Under Estimation")
        ax2.legend()

        fig.tight_layout()
        if save_path is not None:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
        return fig

    # ── 4. CBV-Unique Success/Failure Sets ──

    def unique_success_set(
        self, target_index: str = "CBV"
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Datasets where target is correct and all other indices are wrong (or vice versa).

        Parameters
        ----------
        target_index : str, default='CBV'
            The reference index.

        Returns
        -------
        (unique_success, unique_failure) : (pd.DataFrame, pd.DataFrame)
            unique_success: datasets where target is correct, all others wrong.
            unique_failure: datasets where target is wrong, all others correct.
        """
        target_k = f"{target_index}_k"
        target_corr = f"{target_index}_correct"
        if target_k not in self.df.columns:
            raise ValueError(f"Target index '{target_index}' not found.")

        other_correct_cols = [
            f"{idx}_correct" for idx in self.index_names
            if idx != target_index and f"{idx}_correct" in self.df.columns
        ]

        success_mask = self.df[target_corr].astype(bool).values
        others_wrong = (
            self.df[other_correct_cols].astype(bool).sum(axis=1).values == 0
        )
        unique_success = self.df[success_mask & others_wrong][
            ["dataset", "k_true", target_k]
        ].copy()

        failure_mask = ~self.df[target_corr].astype(bool).values
        others_all_correct = (
            self.df[other_correct_cols].astype(bool).sum(axis=1).values
            == len(other_correct_cols)
        )
        unique_failure = self.df[failure_mask & others_all_correct][
            ["dataset", "k_true", target_k]
        ].copy()

        return unique_success, unique_failure

    # ── 5. Summary Report ──

    def summary_report(self, target_index: str = "CBV") -> str:
        """Generate a text summary of the complementarity analysis.

        Returns
        -------
        str
        """
        lines: List[str] = []
        lines.append("=" * 60)
        lines.append(f"Complementarity Analysis — Target: {target_index}")
        lines.append("=" * 60)

        # Agreement with each other index
        matrix = self.pairwise_agreement_matrix()
        if target_index in matrix.index:
            lines.append(f"\nAgreement with {target_index}:")
            agreements = matrix.loc[target_index].drop(target_index).sort_values(ascending=False)
            for idx, val in agreements.items():
                lines.append(f"  {idx:20s}: {val:.2f}")

        # Failure patterns
        patterns = self.failure_patterns()
        lines.append("\nFailure Patterns:")
        for _, row in patterns.iterrows():
            lines.append(
                f"  {row['index']:20s}: acc={row['accuracy']:.3f}, "
                f"bias={row['bias']:+.2f}, "
                f"over={int(row['over_count']):d}/under={int(row['under_count']):d}"
            )

        # Unique success/failure
        success, failure = self.unique_success_set(target_index)
        lines.append(
            f"\n{target_index}-unique success sets: {len(success)} datasets"
        )
        if len(success) > 0:
            for _, row in success.iterrows():
                lines.append(f"  + {row['dataset']} (k_true={row['k_true']})")
        lines.append(
            f"{target_index}-unique failure sets (target wrong, all others right): "
            f"{len(failure)} datasets"
        )
        if len(failure) > 0:
            for _, row in failure.iterrows():
                lines.append(f"  - {row['dataset']} (k_true={row['k_true']})")

        # Top disagreements
        top = self.top_disagreement_datasets(target_index, top_n=5)
        lines.append(f"\nTop-5 datasets with largest disagreement:")
        for _, row in top.iterrows():
            lines.append(
                f"  {row['dataset']:40s}: k_true={row['k_true']}, "
                f"{target_index}_k={row[f'{target_index}_k']}, "
                f"mean_disagreement={row['mean_disagreement']:.1f}"
            )

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    def generate_all_plots(
        self, output_dir: str = "results"
    ) -> Dict[str, str]:
        """Generate all complementarity figures and save them.

        Parameters
        ----------
        output_dir : str
            Directory to save figures.

        Returns
        -------
        dict mapping figure name to file path.
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        saved: Dict[str, str] = {}

        # Agreement heatmap
        path = str(out / "agreement_heatmap.png")
        self.plot_agreement_heatmap(path)
        saved["agreement_heatmap"] = path

        # Failure patterns
        path = str(out / "failure_patterns.png")
        self.plot_failure_patterns(path)
        saved["failure_patterns"] = path

        return saved
