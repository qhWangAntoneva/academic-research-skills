from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
from critband import (
    bimodality_strength,
    critical_bandwidth,
    silverman_bandwidth,
    silverman_test,
)
from utils.weighting import weighted_k_vote


class CBVIndex:
    """
    Critical Bandwidth Validation index for estimating the number of clusters.

    For each dimension of the data, the CBV index uses the critical bandwidth
    to determine how many modes (clusters) are supported by that dimension,
    then aggregates across dimensions using bimodality strength as weights.

    Parameters
    ----------
    k_range : tuple (min, max), default=(2, 20)
        Range of candidate k values to test.
    n_boot : int, default=999
        Number of bootstrap resamples for Silverman test.
    alpha : float, default=0.05
        Significance level for the Silverman test.
    random_state : int or None, default=None
        Random seed for reproducibility.
    h_crit_tolerance : float, default=1.1
        Multiplier on the Silverman bandwidth threshold. A value >1.0
        relaxes ``h_crit < tolerance * h_silver``, reducing false
        negatives when h_crit at the true k is slightly above h_silver.
    fast : bool, default=False
        If True, skip confidence-interval computation on
        ``critical_bandwidth`` and skip the Silverman test.
        Use for exploratory/benchmarking runs; use ``fast=False``
        for publication-quality results.
    vote_method : str, default='weighted_mean'
        Aggregation method for per-dimension k votes.
        One of ``'weighted_mean'``, ``'median'``, ``'mode'``.
        Passed through to ``weighted_k_vote()``.
    """

    def __init__(
        self,
        k_range: Tuple[int, int] = (2, 20),
        n_boot: int = 999,
        alpha: float = 0.05,
        random_state: Optional[int] = None,
        h_crit_tolerance: float = 1.1,
        fast: bool = False,
        vote_method: str = "weighted_mean",
    ) -> None:
        if k_range[0] < 2:
            raise ValueError("k_range[0] must be >= 2")
        if k_range[1] <= k_range[0]:
            raise ValueError("k_range[1] must be > k_range[0]")
        self.k_range = k_range
        self.n_boot = n_boot
        self.alpha = alpha
        self.random_state = random_state
        self.h_crit_tolerance = h_crit_tolerance
        self.fast = fast
        self.vote_method = vote_method
        self.k_hat_: Optional[int] = None
        self.dimension_votes_: Optional[np.ndarray] = None
        self.dimension_weights_: Optional[np.ndarray] = None
        self.p_values_: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray) -> "CBVIndex":
        """
        Fit the CBV index to data X.

        Parameters
        ----------
        X : np.ndarray of shape (n_samples, n_features)
            Input data.

        Returns
        -------
        self
        """
        X = np.asarray(X, dtype=np.float64)
        n_samples, n_features = X.shape

        if n_samples < 2:
            raise ValueError("X must have at least 2 samples")
        if n_features < 1:
            raise ValueError("X must have at least 1 feature")

        k_min, k_max = self.k_range
        votes = np.full(n_features, fill_value=k_min, dtype=np.float64)
        weights = np.zeros(n_features, dtype=np.float64)
        p_values = np.full(n_features, fill_value=np.nan, dtype=np.float64)
        rng = np.random.default_rng(self.random_state)

        for d in range(n_features):
            x_d = X[:, d]

            # Skip constant dimensions
            if np.ptp(x_d) == 0.0:
                weights[d] = 0.0
                continue

            # Reference bandwidth for "small h_crit" threshold
            h_silver = silverman_bandwidth(x_d)

            for k in range(k_min, k_max + 1):
                result = critical_bandwidth(x_d, k=k, return_ci=not self.fast)
                h_crit = result[0] if isinstance(result, tuple) else result
                converged = result[1] if isinstance(result, tuple) else (not self.fast)

                if converged and np.isfinite(h_crit) and h_crit < self.h_crit_tolerance * h_silver:
                    votes[d] = float(k)
                    break

            # Dimension weight: bimodality strength
            try:
                bm = bimodality_strength(x_d)
                weights[d] = bm.strength_score
            except Exception as e:
                print(f"WARNING: bimodality_strength failed for dim {d}: {e}")
                weights[d] = 0.0

            # Silverman test p-value (H0: data has at most k_min modes)
            if not self.fast:
                try:
                    st = silverman_test(
                        x_d,
                        n_resamples=self.n_boot,
                        mod0=k_min - 1,
                        alpha=self.alpha,
                        random_state=rng,
                    )
                    p_values[d] = st.p_value
                except Exception:
                    p_values[d] = np.nan

        self.dimension_votes_ = votes
        self.dimension_weights_ = weights
        self.p_values_ = p_values

        # Aggregate votes across dimensions using selected method
        k_hat = weighted_k_vote(votes, weights, method=self.vote_method)
        self.k_hat_ = int(np.floor(k_hat + 0.5))

        # Clamp to valid range
        self.k_hat_ = max(k_min, min(self.k_hat_, k_max))

        return self

    def predict(self, X: Optional[np.ndarray] = None) -> int:
        """
        Return the estimated number of clusters.

        Parameters
        ----------
        X : np.ndarray or None, default=None
            Ignored; kept for sklearn compatibility.

        Returns
        -------
        int
            Estimated number of clusters.
        """
        if self.k_hat_ is None:
            raise RuntimeError("fit() must be called before predict()")
        return self.k_hat_
