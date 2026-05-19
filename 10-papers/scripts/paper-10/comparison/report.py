"""Results reporting for CBV comparison experiments.

Produces accuracy/rank tables, statistical tests, and figures.
"""

from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for headless runs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare


class ComparisonReport:
    """Generates comparison tables and figures from benchmark results.

    Parameters
    ----------
    results_df : pandas DataFrame
        From BenchmarkRunner.run_all(), expected columns:
        dataset, k_true, <index>_k, <index>_correct[, wall_time_<index>]
    """

    def __init__(self, results_df: pd.DataFrame):
        required = {"dataset", "k_true"}
        missing = required - set(results_df.columns)
        if missing:
            raise ValueError(f"results_df missing required columns: {missing}")
        self.df = results_df.copy()

        # Auto-detect index columns
        self.index_names: List[str] = sorted({
            col.rsplit("_", 1)[0]
            for col in self.df.columns
            if col.endswith("_k") and col != "k_true"
        })

    # ------------------------------------------------------------------
    # Table generation
    # ------------------------------------------------------------------

    def accuracy_table(self) -> pd.DataFrame:
        """Return DataFrame with accuracy (proportion correct) per index.

        "Correct" means the estimated k equals the true k.
        """
        rows: Dict[str, List[float]] = {}
        for idx_name in self.index_names:
            col = f"{idx_name}_correct"
            if col not in self.df.columns:
                continue
            rows[idx_name] = [self.df[col].mean()]
        return pd.DataFrame(rows, index=["Accuracy"]).T.sort_values(
            "Accuracy", ascending=False
        )

    def rank_table(self) -> pd.DataFrame:
        """Return DataFrame with rank per index per dataset, plus mean rank.

        Rank 1 = closest to k_true. Ties receive average rank.
        """
        rank_data: Dict[str, List] = {"dataset": self.df["dataset"].tolist()}
        for idx_name in self.index_names:
            col = f"{idx_name}_k"
            if col not in self.df.columns:
                continue
            # absolute error from k_true
            errors = (self.df[col] - self.df["k_true"]).abs().values
            # rank across indices for this dataset (ties averaged)
            rank_data[idx_name] = errors

        rank_df = pd.DataFrame(rank_data).set_index("dataset")
        # rank each row (lower error = rank 1)
        rank_df = rank_df.rank(axis=1, method="average")

        mean_rank = rank_df.mean().to_frame("mean_rank")
        mean_rank = mean_rank.sort_values("mean_rank")
        return mean_rank

    def friedman_test(self) -> Tuple[float, float]:
        """Perform Friedman test for significant differences among indices.

        Returns
        -------
        chi2 : float
        p_value : float
        """
        # Build matrix: rows = datasets, cols = indices, values = |k_hat - k_true|
        values: List[np.ndarray] = []
        for idx_name in self.index_names:
            col = f"{idx_name}_k"
            if col not in self.df.columns:
                continue
            errors = (self.df[col] - self.df["k_true"]).abs().values
            values.append(errors)

        if len(values) < 2:
            raise ValueError("Need at least 2 indices for Friedman test.")

        chi2, p_value = friedmanchisquare(*values)
        return float(chi2), float(p_value)

    def win_tie_loss_matrix(self) -> pd.DataFrame:
        """Pairwise win/tie/loss matrix.

        Cell (i, j) = number of datasets where index i beats index j
        (i.e., |k_hat_i - k_true| < |k_hat_j - k_true|).
        """
        n_idxs = len(self.index_names)
        matrix = pd.DataFrame(
            0,
            index=self.index_names,
            columns=self.index_names,
            dtype=int,
        )
        for i, idx_i in enumerate(self.index_names):
            col_i = f"{idx_i}_k"
            if col_i not in self.df.columns:
                continue
            err_i = (self.df[col_i] - self.df["k_true"]).abs()
            for j, idx_j in enumerate(self.index_names):
                if i == j:
                    matrix.loc[idx_i, idx_j] = 0
                    continue
                col_j = f"{idx_j}_k"
                if col_j not in self.df.columns:
                    continue
                err_j = (self.df[col_j] - self.df["k_true"]).abs()
                wins = int((err_i < err_j).sum())
                matrix.loc[idx_i, idx_j] = wins
        return matrix

    def computational_cost_table(self) -> pd.DataFrame:
        """Return DataFrame with mean wall time per index per dataset.

        Expects columns of the form: wall_time_<index_name>.
        If no such columns exist, returns an empty DataFrame.
        """
        time_cols = [c for c in self.df.columns if c.startswith("wall_time_")]
        if not time_cols:
            return pd.DataFrame()

        idx_map: Dict[str, str] = {}
        for tc in time_cols:
            idx_name = tc[len("wall_time_"):]
            idx_map[idx_name] = tc

        rows: Dict[str, List[float]] = {}
        for idx_name in self.index_names:
            if idx_name not in idx_map:
                continue
            rows[idx_name] = [self.df[idx_map[idx_name]].mean()]

        result = pd.DataFrame(rows, index=["Mean wall time (s)"]).T.sort_values(
            "Mean wall time (s)"
        )
        return result

    def to_latex(self) -> str:
        """Export accuracy and rank tables as LaTeX.

        Returns
        -------
        latex_str : str
        """
        acc = self.accuracy_table()
        rank = self.rank_table()

        lines = [
            r"\begin{table}[t]",
            r"\centering",
            r"\caption{CVI comparison: accuracy (proportion correct) and mean rank.}",
            r"\label{tab:cvi_comparison}",
            r"\begin{tabular}{lcc}",
            r"\toprule",
            r"Index & Accuracy & Mean Rank \\",
            r"\midrule",
        ]
        for idx_name in rank.index:
            acc_val = acc.loc[idx_name, "Accuracy"] if idx_name in acc.index else float("nan")
            rank_val = rank.loc[idx_name, "mean_rank"]
            lines.append(
                rf"{idx_name} & {acc_val:.3f} & {rank_val:.3f} \\"
            )
        lines.extend([
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
        ])
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------

    def plot_accuracy(self, save_path: Optional[str] = None) -> plt.Figure:
        """Grouped bar chart: accuracy per index.

        Parameters
        ----------
        save_path : str, optional
            If provided, save the figure to this path.

        Returns
        -------
        fig : matplotlib.figure.Figure
        """
        acc = self.accuracy_table()
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = plt.cm.Set2(np.linspace(0, 1, len(acc)))

        bars = ax.bar(
            range(len(acc)),
            acc["Accuracy"].values,
            color=colors,
            edgecolor="gray",
            width=0.6,
        )
        ax.set_xticks(range(len(acc)))
        ax.set_xticklabels(acc.index, rotation=30, ha="right")
        ax.set_ylabel("Accuracy (proportion correct)")
        ax.set_title("CVI Accuracy Comparison")
        ax.set_ylim(0, 1.0)
        ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5, label="Random (0.5)")
        ax.legend()

        # Value labels on bars
        for bar, val in zip(bars, acc["Accuracy"].values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{val:.3f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

        fig.tight_layout()
        if save_path is not None:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
        return fig

    def plot_rank_distribution(self, save_path: Optional[str] = None) -> plt.Figure:
        """Box plot of rank distributions across indices.

        Parameters
        ----------
        save_path : str, optional
            If provided, save the figure to this path.

        Returns
        -------
        fig : matplotlib.figure.Figure
        """
        rank_data: Dict[str, List] = {"dataset": self.df["dataset"].tolist()}
        for idx_name in self.index_names:
            col = f"{idx_name}_k"
            if col not in self.df.columns:
                continue
            errors = (self.df[col] - self.df["k_true"]).abs().values
            rank_data[idx_name] = errors

        rank_df = pd.DataFrame(rank_data).set_index("dataset")
        rank_df = rank_df.rank(axis=1, method="average")

        fig, ax = plt.subplots(figsize=(10, 5))
        positions = list(range(len(rank_df.columns)))
        bp = ax.boxplot(
            [rank_df[col].values for col in rank_df.columns],
            positions=positions,
            patch_artist=True,
            widths=0.5,
        )

        colors = plt.cm.Set2(np.linspace(0, 1, len(rank_df.columns)))
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)

        ax.set_xticks(positions)
        ax.set_xticklabels(rank_df.columns, rotation=30, ha="right")
        ax.set_ylabel("Rank (1 = best)")
        ax.set_title("CVI Rank Distribution Across Datasets")
        ax.invert_yaxis()  # rank 1 at top
        fig.tight_layout()

        if save_path is not None:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
        return fig
