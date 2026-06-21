from __future__ import annotations

from typing import Optional, Tuple
import numpy as np
from .index import CBVIndex


class CBVProjection:
    """CBV via random 2D projections.

    For high-dimensional data, CBV's per-dimension independence assumption
    can break down when dimensions are correlated. This variant projects
    the data onto multiple random 2D subspaces, runs CBV on each 2D
    projection, and aggregates the per-projection k estimates.

    Parameters
    ----------
    k_range : tuple (min, max), default=(2, 20)
        Range of candidate k values.
    n_projections : int, default=50
        Number of random 2D projections to draw.
    mode : str, default='threshold'
        CBV mode for each projection.
    h_crit_tolerance : float, default=1.3
        Tolerance for the threshold test.
    bandwidth_method : str, default='silverman'
        Reference bandwidth method.
    vote_method : str, default='mode'
        Aggregation method: 'mode' (majority vote) or 'weighted_mean'.
    random_state : int or None, default=None
        Seed for reproducibility.

    Attributes
    ----------
    k_hat_ : int
        Fused estimate across all projections.
    projection_votes_ : np.ndarray
        Per-projection k estimates (n_projections,).
    n_unique_views_ : int
        Number of distinct k values observed across projections.
    """
    def __init__(
        self,
        k_range: Tuple[int, int] = (2, 20),
        n_projections: int = 50,
        mode: str = "threshold",
        h_crit_tolerance: float = 1.3,
        bandwidth_method: str = "silverman",
        vote_method: str = "mode",
        random_state: Optional[int] = None,
    ) -> None:
        if k_range[0] < 2:
            raise ValueError("k_range[0] must be >= 2")
        if k_range[1] <= k_range[0]:
            raise ValueError("k_range[1] must be > k_range[0]")
        if n_projections < 1:
            raise ValueError("n_projections must be >= 1")

        self.k_range = k_range
        self.n_projections = n_projections
        self.mode = mode
        self.h_crit_tolerance = h_crit_tolerance
        self.bandwidth_method = bandwidth_method
        self.vote_method = vote_method
        self.random_state = random_state
        self.k_hat_: Optional[int] = None
        self.projection_votes_: Optional[np.ndarray] = None
        self.n_unique_views_: Optional[int] = None

    def fit(self, X: np.ndarray) -> "CBVProjection":
        """Fit CBVProjection to data X.

        Projects X onto n_projections random 2D subspaces,
        runs CBVIndex on each, and aggregates via majority vote or weighted mean.

        Parameters
        ----------
        X : np.ndarray of shape (n_samples, n_features)

        Returns
        -------
        self
        """
        X = np.asarray(X, dtype=np.float64)
        n_samples, n_features = X.shape

        if n_samples < 2:
            raise ValueError("X must have at least 2 samples")

        k_min, k_max = self.k_range
        rng = np.random.default_rng(self.random_state)

        votes = np.full(self.n_projections, fill_value=k_min, dtype=np.float64)

        for p in range(self.n_projections):
            # Random 2D projection: pick 2 random orthogonal directions
            if n_features >= 2:
                # Random rotation matrix (2 x n_features)
                A = rng.standard_normal((n_features, 2))
                Q, _ = np.linalg.qr(A)
                proj_matrix = Q[:, :2]  # n_features x 2
            else:
                # Already 1D or 2D
                proj_matrix = np.eye(n_features, 2)[:, :n_features]

            X_proj = X @ proj_matrix  # n_samples x 2

            # Skip if projection collapses to a line
            if np.ptp(X_proj[:, 0]) == 0 or np.ptp(X_proj[:, 1]) == 0:
                continue

            try:
                idx = CBVIndex(
                    k_range=self.k_range,
                    mode=self.mode,
                    h_crit_tolerance=self.h_crit_tolerance,
                    bandwidth_method=self.bandwidth_method,
                    vote_method="weighted_mean",
                    random_state=self.random_state,
                )
                idx.fit(X_proj)
                votes[p] = idx.predict()
            except Exception:
                pass  # keep default k_min

        self.projection_votes_ = votes

        # Aggregate
        if self.vote_method == "mode":
            # Majority vote
            unique, counts = np.unique(votes, return_counts=True)
            self.k_hat_ = int(unique[np.argmax(counts)])
        elif self.vote_method == "weighted_mean":
            self.k_hat_ = int(np.round(np.mean(votes)))
        else:
            raise ValueError(f"vote_method must be 'mode' or 'weighted_mean', got '{self.vote_method}'")

        self.k_hat_ = max(k_min, min(self.k_hat_, k_max))
        self.n_unique_views_ = len(np.unique(votes))

        return self

    def predict(self, X: Optional[np.ndarray] = None) -> int:
        """Return the estimated number of clusters."""
        if self.k_hat_ is None:
            raise RuntimeError("fit() must be called before predict()")
        return self.k_hat_
