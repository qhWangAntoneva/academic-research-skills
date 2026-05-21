from __future__ import annotations

import warnings
from typing import Optional, Tuple

import numpy as np
from critband import (
    critical_bandwidth,
    silverman_bandwidth,
    silverman_test,
)
from utils.weighting import compute_dimension_weights, weighted_k_vote


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
        Only used when ``mode='bootstrap'``.
    alpha : float, default=0.05
        Significance level for the Silverman test.
    random_state : int or None, default=None
        Random seed for reproducibility.
    h_crit_tolerance : float, default=1.3
        Multiplier on the Silverman bandwidth threshold. A value >1.0
        relaxes ``h_crit < tolerance * h_silver``, reducing false
        negatives when h_crit at the true k is slightly above h_silver.
    mode : str, default='bootstrap'
        Operating mode for per-dimension mode detection.

        - ``'bootstrap'``: Full Silverman's bootstrap test (Silverman, 1981).
          Computes p-values via resampling from a calibrated null density.
          Provides Type I error control. **This is the proper statistical test.**

        - ``'threshold'``: Fast heuristic using a fixed threshold
          ``h_crit < tolerance * h_silver``. **This is NOT Silverman's test.**
          It provides no p-value and no Type I error control.
          Use for exploratory/benchmarking runs only.

    fast : bool, default=None
        Deprecated since v0.3.0. Use ``mode='threshold'`` instead.
        If ``True``, equivalent to ``mode='threshold'``.
        If ``False``, equivalent to ``mode='bootstrap'``.
    vote_method : str, default='weighted_mean'
        Aggregation method for per-dimension k votes.
        One of ``'weighted_mean'``, ``'median'``, ``'mode'``.
        Passed through to ``weighted_k_vote()``.
    weight_method : str, default='excess_mass'
        Dimension weighting method. One of:
        - ``'excess_mass'``: weight proportional to number of detected modes
        - ``'bimodality_strength'``: legacy bimodality-only weighting
        - ``'hybrid'``: geometric mean of excess_mass and bimodality_strength
        Passed through to ``compute_dimension_weights()``.
    """

    def __init__(
        self,
        k_range: Tuple[int, int] = (2, 20),
        n_boot: int = 999,
        alpha: float = 0.05,
        random_state: Optional[int] = None,
        h_crit_tolerance: float = 1.3,
        mode: str = "bootstrap",
        fast: Optional[bool] = None,
        vote_method: str = "weighted_mean",
        weight_method: str = "excess_mass",
    ) -> None:
        if k_range[0] < 2:
            raise ValueError("k_range[0] must be >= 2")
        if k_range[1] <= k_range[0]:
            raise ValueError("k_range[1] must be > k_range[0]")

        # Handle deprecated fast parameter
        if fast is not None:
            warnings.warn(
                "`fast` is deprecated since v0.3.0. Use `mode='threshold'` instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            self._mode = "threshold" if fast else "bootstrap"
        else:
            self._mode = mode

        if self._mode not in ("bootstrap", "threshold"):
            raise ValueError(f"mode must be 'bootstrap' or 'threshold', got '{mode}'")

        self.k_range = k_range
        self.n_boot = n_boot
        self.alpha = alpha
        self.random_state = random_state
        self.h_crit_tolerance = h_crit_tolerance
        self.vote_method = vote_method
        self.weight_method = weight_method
        self.k_hat_: Optional[int] = None
        self.dimension_votes_: Optional[np.ndarray] = None
        self.dimension_weights_: Optional[np.ndarray] = None
        self.p_values_: Optional[np.ndarray] = None

    @property
    def fast(self) -> bool:
        """Deprecated: use mode instead."""
        return self._mode == "threshold"

    @property
    def mode(self) -> str:
        """Current operating mode."""
        return self._mode

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

        is_threshold = (self._mode == "threshold")

        k_min, k_max = self.k_range
        votes = np.full(n_features, fill_value=k_min, dtype=np.float64)
        p_values = np.full(n_features, fill_value=np.nan, dtype=np.float64)
        rng = np.random.default_rng(self.random_state)

        for d in range(n_features):
            x_d = X[:, d]

            # Skip constant dimensions
            if np.ptp(x_d) == 0.0:
                continue

            # Reference bandwidth for "small h_crit" threshold
            h_silver = silverman_bandwidth(x_d)

            for k in range(k_min, k_max + 1):
                result = critical_bandwidth(x_d, k=k, return_ci=not is_threshold)
                h_crit = result[0] if isinstance(result, tuple) else result
                converged = result[1] if isinstance(result, tuple) else True

                if converged and np.isfinite(h_crit) and h_crit < self.h_crit_tolerance * h_silver:
                    votes[d] = float(k)
                    break

            # Silverman test p-value (H0: data has at most k_min modes)
            # Only computed in bootstrap mode — threshold mode is heuristic only
            if not is_threshold:
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

        # Dimension weights: computed in bulk using selected weight method
        weights = compute_dimension_weights(X, weight_method=self.weight_method, k_max=k_max)

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
