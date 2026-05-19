import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare
from typing import Callable, Dict, List, Optional, Tuple
from pathlib import Path


class BenchmarkRunner:
    """Orchestrates benchmark execution of cluster-number indices on datasets.

    Parameters
    ----------
    cv_indices : list of (name, callable) pairs OR list of CVIWrapper objects
        Each entry must be either a ``(name, callable)`` tuple where callable
        takes X and returns k_hat, or an object with ``.name`` and
        ``.fit(X).predict()`` (e.g. CVIWrapper).
    datasets : list of dicts
        Each dict has keys 'X' (ndarray), 'y_true' (ndarray),
        'name' (str), 'k_true' (int).
    random_state : int, default=42
        Seed for reproducibility in downstream evaluation.
    results_dir : str or Path or None
        Directory to save result artifacts. Created if it does not exist.
    """

    def __init__(
        self,
        cv_indices: List,
        datasets: List[Dict],
        random_state: int = 42,
        results_dir: Optional[str] = None,
    ) -> None:
        self.cv_indices = cv_indices
        self.datasets = datasets
        self.random_state = random_state
        self.results_dir: Optional[Path] = None

        if results_dir is not None:
            self.results_dir = Path(results_dir)
            self.results_dir.mkdir(parents=True, exist_ok=True)

    @property
    def _resolved_indices(self) -> List[Tuple[str, Callable[[np.ndarray], int]]]:
        """Return cv_indices list with all entries normalised to (name, callable)."""
        return [self._resolve_index(idx) for idx in self.cv_indices]

    @staticmethod
    def _resolve_index(index):
        """Resolve a CV index to (name, callable) regardless of input type.

        Supports:
        - ``(name, callable)`` tuples (legacy format)
        - objects with ``.name`` and ``.fit`` + ``.predict()`` (CVIWrapper)
        """
        if isinstance(index, tuple):
            return index
        name = getattr(index, "name", "unknown")
        fn = lambda X, idx=index: idx.fit(X).predict()
        return name, fn

    def _evaluate_single(
        self,
        index_fn: Callable[[np.ndarray], int],
        X: np.ndarray,
        k_true: int,
    ) -> Tuple[int, bool]:
        """Run one index on one dataset with error handling.

        Parameters
        ----------
        index_fn : callable
            Takes X and returns k_hat.
        X : ndarray of shape (n_samples, n_features)
        k_true : int
            Ground-truth cluster count.

        Returns
        -------
        (k_hat, is_correct) tuple.
        """
        X_filtered = self._sanitize_input(X)

        if X_filtered.shape[1] == 0:
            return -1, False

        try:
            k_hat = index_fn(X_filtered)
        except Exception as e:
            print(
                f"WARNING: index callable failed with "
                f"{type(e).__name__}: {e} "
                f"(X shape = {X.shape})"
            )
            k_hat = -1

        is_correct = bool(k_hat == k_true)
        return k_hat, is_correct

    @staticmethod
    def _sanitize_input(X: np.ndarray) -> np.ndarray:
        """Remove constant features and rows with NaN from X."""
        row_mask = ~np.any(np.isnan(X), axis=1)
        X_no_nan = X[row_mask]

        if X_no_nan.shape[0] == 0:
            return X_no_nan

        col_std = np.std(X_no_nan, axis=0)
        non_const_mask = col_std > 0
        X_clean = X_no_nan[:, non_const_mask]
        return X_clean

    def run_all(
        self, parallel: bool = False, n_jobs: int = -1
    ) -> pd.DataFrame:
        """Run all CV indices on all datasets.

        Parameters
        ----------
        parallel : bool
            If True, use joblib for parallel execution.
        n_jobs : int
            Number of parallel jobs. Ignored when parallel=False.

        Returns
        -------
        pd.DataFrame with columns:
            dataset, k_true, <index_name>_k, <index_name>_correct
        """
        records: List[Dict] = []

        for ds in self.datasets:
            X = ds["X"]
            k_true = ds["k_true"]
            dataset_name = ds["name"]

            row: Dict = {"dataset": dataset_name, "k_true": k_true}

            if parallel:
                row = self._run_parallel(X, k_true, row, n_jobs)
            else:
                for idx_name, index_fn in self._resolved_indices:
                    k_hat, is_correct = self._evaluate_single(
                        index_fn, X, k_true
                    )
                    row[f"{idx_name}_k"] = k_hat
                    row[f"{idx_name}_correct"] = int(is_correct)

            records.append(row)

        results_df = pd.DataFrame(records)

        if self.results_dir is not None:
            default_path = self.results_dir / "benchmark_results.csv"
            self.save_results(results_df, str(default_path))

        return results_df

    def _run_parallel(
        self,
        X: np.ndarray,
        k_true: int,
        base_row: Dict,
        n_jobs: int,
    ) -> Dict:
        """Run all indices on a single dataset using joblib.

        Falls back to sequential if joblib is not installed.
        """
        try:
            from joblib import Parallel, delayed

            results = Parallel(n_jobs=n_jobs)(
                delayed(self._evaluate_single)(fn, X, k_true)
                for _, fn in self._resolved_indices
            )
            for (idx_name, _), (k_hat, is_correct) in zip(
                self._resolved_indices, results
            ):
                base_row[f"{idx_name}_k"] = k_hat
                base_row[f"{idx_name}_correct"] = int(is_correct)
        except ImportError:
            for idx_name, index_fn in self._resolved_indices:
                k_hat, is_correct = self._evaluate_single(
                    index_fn, X, k_true
                )
                base_row[f"{idx_name}_k"] = k_hat
                base_row[f"{idx_name}_correct"] = int(is_correct)

        return base_row

    def summarize_results(
        self, results_df: pd.DataFrame
    ) -> Dict:
        """Compute summary statistics from benchmark results.

        Parameters
        ----------
        results_df : pd.DataFrame
            Output of run_all().

        Returns
        -------
        dict with keys:
            'accuracy' : pd.DataFrame per-index accuracy
            'rank_per_dataset' : pd.DataFrame rank per index per dataset
            'mean_rank' : pd.Series mean rank across datasets
            'win_tie_loss' : pd.DataFrame win/tie/loss matrix
            'friedman' : (statistic, p_value) or None
            'nemenyi' : pd.DataFrame of post-hoc p-values or None
        """
        index_names = [name for name, _ in self._resolved_indices]
        suffix_correct = "_correct"

        acc_records: List[Dict] = []
        for idx_name in index_names:
            col = f"{idx_name}{suffix_correct}"
            if col not in results_df.columns:
                continue
            accuracy = results_df[col].mean()
            n_correct = results_df[col].sum()
            n_total = len(results_df)
            acc_records.append(
                {
                    "index": idx_name,
                    "accuracy": accuracy,
                    "n_correct": int(n_correct),
                    "n_total": n_total,
                }
            )
        accuracy_df = pd.DataFrame(acc_records).sort_values(
            "accuracy", ascending=False
        )

        # Rank per dataset (1 = closest to k_true)
        suffix_k = "_k"
        k_cols = [f"{name}{suffix_k}" for name in index_names]
        k_cols = [c for c in k_cols if c in results_df.columns]
        available_idx = [c.replace(suffix_k, "") for c in k_cols]

        rank_data = {}
        for _, row in results_df.iterrows():
            k_true = row["k_true"]
            scores: Dict[str, float] = {}
            for idx_name in available_idx:
                col = f"{idx_name}{suffix_k}"
                k_hat = row[col]
                if k_hat < 0:
                    abs_err = float("inf")
                else:
                    abs_err = abs(int(k_hat) - int(k_true))
                scores[idx_name] = abs_err

            ranked = sorted(scores.items(), key=lambda x: x[1])
            for rank_pos, (idx_name, _) in enumerate(ranked, start=1):
                if idx_name not in rank_data:
                    rank_data[idx_name] = []
                rank_data[idx_name].append(rank_pos)

        rank_df = pd.DataFrame(rank_data)

        # Mean rank
        mean_rank = rank_df.mean().sort_values()

        # Win / tie / loss matrix
        n_indices = len(available_idx)
        matrix = np.zeros((n_indices, n_indices), dtype=int)

        for _, row in results_df.iterrows():
            k_true = row["k_true"]
            errors = {}
            for idx_name in available_idx:
                col = f"{idx_name}{suffix_k}"
                k_hat = row[col]
                if k_hat >= 0:
                    errors[idx_name] = abs(int(k_hat) - int(k_true))
                else:
                    errors[idx_name] = float("inf")

            for i, idx_a in enumerate(available_idx):
                for j, idx_b in enumerate(available_idx):
                    if i == j:
                        continue
                    err_a = errors[idx_a]
                    err_b = errors[idx_b]
                    if err_a < err_b:
                        matrix[i, j] += 1

        win_tie_loss = pd.DataFrame(
            matrix,
            index=available_idx,
            columns=available_idx,
        )

        # ── Statistical significance: Friedman test ──
        friedman_result: Optional[Tuple[float, float]] = None
        nemenyi_result: Optional[pd.DataFrame] = None
        if rank_df.shape[1] >= 3 and rank_df.shape[0] > 1:
            try:
                # Friedman test on rank data
                stat, p_val = friedmanchisquare(*[rank_df[col].values for col in rank_df.columns])
                friedman_result = (float(stat), float(p_val))

                # Nemenyi post-hoc if Friedman is significant
                if p_val < 0.05:
                    try:
                        import scikit_posthocs as sp
                        nemenyi_result = sp.posthoc_nemenyi_friedman(rank_df.values)
                        nemenyi_result.columns = rank_df.columns
                        nemenyi_result.index = rank_df.columns
                    except ImportError:
                        pass
            except Exception:
                pass

        return {
            "accuracy": accuracy_df,
            "rank_per_dataset": rank_df,
            "mean_rank": mean_rank,
            "win_tie_loss": win_tie_loss,
            "friedman": friedman_result,
            "nemenyi": nemenyi_result,
        }

    def plot_accuracy_comparison(
        self,
        results_df: pd.DataFrame,
        save_path: Optional[str] = None,
    ) -> None:
        """Create a bar plot comparing accuracy across CV indices."""
        import matplotlib.pyplot as plt

        index_names = [name for name, _ in self._resolved_indices]
        suffix_correct = "_correct"

        means = []
        names_used: List[str] = []
        for idx_name in index_names:
            col = f"{idx_name}{suffix_correct}"
            if col not in results_df.columns:
                continue
            means.append(results_df[col].mean())
            names_used.append(idx_name)

        fig, ax = plt.subplots(figsize=(max(8, len(names_used) * 0.8), 5))
        bar_colors = plt.cm.Set2(
            np.linspace(0, 1, len(names_used))
        )

        x_pos = np.arange(len(names_used))
        bars = ax.bar(x_pos, means, color=bar_colors, edgecolor="gray")

        ax.set_xlabel("Cluster Validity Index")
        ax.set_ylabel("Accuracy (fraction correct)")
        ax.set_title("Benchmark Accuracy Comparison")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(names_used, rotation=45, ha="right", fontsize=9)
        ax.set_ylim(0, 1.05)

        for bar, val in zip(bars, means):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{val:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

        fig.tight_layout()

        if save_path is not None:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Accuracy plot saved to {save_path}")

        plt.close(fig)

    def plot_rank_comparison(
        self,
        results_df: pd.DataFrame,
        save_path: Optional[str] = None,
    ) -> None:
        """Create a box plot of ranks per CV index."""
        import matplotlib.pyplot as plt

        summary = self.summarize_results(results_df)
        rank_df: pd.DataFrame = summary["rank_per_dataset"]

        fig, ax = plt.subplots(figsize=(max(8, rank_df.shape[1] * 0.8), 5))

        positions = np.arange(rank_df.shape[1])
        bp = ax.boxplot(
            rank_df.values,
            positions=positions,
            patch_artist=True,
            showmeans=True,
            meanprops={
                "marker": "D",
                "markerfacecolor": "red",
                "markersize": 5,
            },
        )

        colors = plt.cm.Set2(np.linspace(0, 1, rank_df.shape[1]))
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)

        ax.set_xlabel("Cluster Validity Index")
        ax.set_ylabel("Rank (1 = best)")
        ax.set_title("Rank Distribution Across Datasets")
        ax.set_xticks(positions)
        ax.set_xticklabels(
            rank_df.columns, rotation=45, ha="right", fontsize=9
        )
        ax.invert_yaxis()

        fig.tight_layout()

        if save_path is not None:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Rank plot saved to {save_path}")

        plt.close(fig)

    def save_results(
        self, results_df: pd.DataFrame, filepath: str
    ) -> None:
        """Save benchmark results to a CSV file."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(str(path), "w", encoding="utf-8") as f:
            results_df.to_csv(f, index=False)
        print(f"Results saved to {path}")
