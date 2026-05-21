from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from .index import CBVIndex
from .spectral import CBVSpectral
from critband import bimodality_strength, excess_mass
from utils.weighting import compute_dimension_weights


class CBVHybrid:
    """
    Hybrid CBV: fuses raw-feature and spectral-embedding dimension votes.

    Strategy
    --------
    1. Run :class:`CBVIndex` on raw features → per-dimension votes + weights.
    2. Run :class:`CBVSpectral` on spectral embedding → per-dimension votes + weights.
    3. Combine raw + spectral dimensions into a single pool.
    4. Compute **weighted mode**: the k with the highest total bimodality
       weight across all dimensions.

    Weighted mode naturally gives spectral dimensions influence proportional
    to their bimodality strength, preventing both domination (10 spectral dims
    vs 2 raw) and noise (low-bimodality dims contribute near zero).

    **Dimension pre-filtering** (Step 3): before any CBV computation,
    dimensions with bimodality strength below ``min_dim_weight`` are
    excluded.  This prevents truly uni-modal / noise dimensions from
    casting spurious votes in the mode aggregation.

    Parameters
    ----------
    k_range : tuple (min, max), default=(2, 20)
        Range of candidate k values to test.
    n_boot : int, default=999
        Number of bootstrap resamples for the Silverman test.
    alpha : float, default=0.05
        Significance level for the Silverman test.
    random_state : int or None, default=None
        Random seed for reproducibility.
    h_crit_tolerance : float, default=1.1
        Multiplier on the Silverman bandwidth threshold.
    mode : str, default='threshold'
        Operating mode: ``'threshold'`` (fast heuristic, no p-values) or
        ``'bootstrap'`` (full Silverman test with p-values).
    vote_method : str, default='mode'
        Aggregation method used internally by each sub-estimator.
    n_components : int, default=10
        Embedding dimensionality for spectral CBV.
    affinity : str, default='nearest_neighbors'
        Affinity parameter for SpectralEmbedding.
    min_dim_weight : float, default=0.15
        Minimum bimodality-strength threshold for dimension pre-filtering.
        Dimensions with strength below this value are excluded from CBV
        analysis.  Set to 0 to disable pre-filtering.
    use_excess_mass : bool, default=True
        If True, augment the combined vote pool with per-dimension
        ``excess_mass`` mode estimates.  Helps detect high-k structure
        that the sequential critical-bandwidth test misses.
    adaptive_tolerance : bool, default=True
        If True, compute ``h_crit_tolerance`` from data dimensionality
        instead of using the fixed value.  Tolerance increases with
        ``n_features`` to compensate for 1D projection collapse in
        high-dimensional spaces.

    Attributes
    ----------
    k_hat_ : int
        Fused estimate — weighted mode of combined raw + spectral votes.
    k_hat_raw_ : int
        Estimate from raw-feature CBV alone (pre-fusion).
    k_hat_spectral_ : int
        Estimate from spectral-embedding CBV alone (pre-fusion).
    raw_confidence_ : float
        Fraction of raw bimodality weight on the mode vote (0-1).
    spec_confidence_ : float
        Fraction of spectral bimodality weight on the mode vote (0-1).
    raw_votes_ : np.ndarray
        Per-dimension k votes from raw-feature CBV.
    raw_weights_ : np.ndarray
        Per-dimension bimodality weights from raw-feature CBV.
    spec_votes_ : np.ndarray
        Per-dimension k votes from spectral-embedding CBV.
    spec_weights_ : np.ndarray
        Per-dimension bimodality weights from spectral-embedding CBV.
    n_dims_filtered_ : int
        Number of dimensions removed by pre-filtering.
    dim_filter_mask_ : np.ndarray or None
        Boolean mask of kept dimensions (None if no filtering applied).
    """

    @staticmethod
    def _weighted_mode(votes: np.ndarray, weights: np.ndarray) -> float:
        """k with the highest total bimodality weight."""
        k_to_weight: dict[float, float] = {}
        for v, w in zip(votes, weights):
            k_to_weight[v] = k_to_weight.get(v, 0.0) + float(w)
        return max(k_to_weight, key=k_to_weight.get)  # type: ignore[arg-type]

    def __init__(
        self,
        k_range: Tuple[int, int] = (2, 20),
        n_boot: int = 999,
        alpha: float = 0.05,
        random_state: Optional[int] = None,
        h_crit_tolerance: float = 1.1,
        mode: str = "threshold",
        vote_method: str = "mode",
        n_components: int = 10,
        affinity: str = "nearest_neighbors",
        min_dim_weight: float = 0.15,
        use_excess_mass: bool = True,
        adaptive_tolerance: bool = True,
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
        self.mode = mode
        self.vote_method = vote_method
        self.n_components = n_components
        self.affinity = affinity
        self.min_dim_weight = min_dim_weight
        self.use_excess_mass = use_excess_mass
        self.adaptive_tolerance = adaptive_tolerance
        self.k_hat_: Optional[int] = None

    def fit(self, X: np.ndarray) -> "CBVHybrid":
        """
        Fit the hybrid CBV index to data X.

        Parameters
        ----------
        X : np.ndarray of shape (n_samples, n_features)
            Input data.

        Returns
        -------
        self
        """
        X = np.asarray(X, dtype=np.float64)
        k_min, k_max = self.k_range

        # 0. Dimension pre-filtering: exclude near-zero bimodality dims
        if self.min_dim_weight > 0.0:
            dim_weights = compute_dimension_weights(X)
            keep = dim_weights >= self.min_dim_weight
            if np.sum(keep) >= 2:  # need at least 2 dims for CBV
                X_fit = X[:, keep]
                self.n_dims_filtered_ = int(X.shape[1] - X_fit.shape[1])
                self.dim_filter_mask_ = keep
            else:
                X_fit = X
                self.n_dims_filtered_ = 0
                self.dim_filter_mask_ = None
        else:
            X_fit = X
            self.n_dims_filtered_ = 0
            self.dim_filter_mask_ = None

        # Step 5: Adaptive h_crit_tolerance — relax threshold for high-D data
        if self.adaptive_tolerance:
            n_features_eff = X_fit.shape[1]
            hct = 1.0 + 0.5 * (1.0 - np.exp(-n_features_eff / 15.0))
        else:
            hct = self.h_crit_tolerance

        # 1. Raw-feature CBV
        self.raw_index_ = CBVIndex(
            k_range=self.k_range,
            n_boot=self.n_boot,
            alpha=self.alpha,
            random_state=self.random_state,
            h_crit_tolerance=hct,
            mode=self.mode,
            vote_method=self.vote_method,
        )
        self.raw_index_.fit(X_fit)
        self.k_hat_raw_ = self.raw_index_.k_hat_
        self.raw_votes_ = self.raw_index_.dimension_votes_
        self.raw_weights_ = self.raw_index_.dimension_weights_

        # 2. Spectral-embedding CBV
        self.spec_index_ = CBVSpectral(
            k_range=self.k_range,
            n_boot=self.n_boot,
            alpha=self.alpha,
            random_state=self.random_state,
            h_crit_tolerance=hct,
            mode=self.mode,
            vote_method=self.vote_method,
            n_components=self.n_components,
            affinity=self.affinity,
        )
        self.spec_index_.fit(X_fit)
        self.k_hat_spectral_ = self.spec_index_.k_hat_
        self.spec_votes_ = self.spec_index_.dimension_votes_
        self.spec_weights_ = self.spec_index_.dimension_weights_

        # 3. Fuse: weighted mode over all raw + spectral + excess_mass dims
        #
        # Each dimension votes for k, weighted by its bimodality strength.
        # The k with the highest total weight across all views wins.
        # Step 4: excess_mass adds direct mode-count estimates per dimension,
        # helping detect high-k structure that sequential CBV misses.
        all_votes = np.concatenate([self.raw_votes_, self.spec_votes_])
        all_weights = np.concatenate([self.raw_weights_, self.spec_weights_])

        # Step 4: Excess Mass blend — direct mode-counting per dimension
        if self.use_excess_mass:
            nf = X_fit.shape[1]
            em_votes = np.full(nf, float(k_min), dtype=np.float64)
            em_weights = np.zeros(nf, dtype=np.float64)
            for d in range(nf):
                x_d = X_fit[:, d]
                if np.ptp(x_d) == 0.0:
                    continue
                try:
                    em = excess_mass(x_d, n_modes_max=k_max, n_boot=0)
                    nm = em.n_modes_estimated
                    if k_min <= nm <= k_max:
                        em_votes[d] = float(nm)
                except Exception:
                    pass
                try:
                    bm = bimodality_strength(x_d)
                    em_weights[d] = bm.strength_score
                except Exception:
                    em_weights[d] = 0.0
            self.em_votes_ = em_votes
            self.em_weights_ = em_weights
            all_votes = np.concatenate([all_votes, em_votes])
            all_weights = np.concatenate([all_weights, em_weights])
        self.k_hat_ = int(self._weighted_mode(all_votes, all_weights))

        # Diagnostic confidence per sub-view (weight share of the fused k)
        raw_k_weight = float(np.sum(self.raw_weights_[self.raw_votes_ == self.k_hat_]))
        raw_total = float(np.sum(self.raw_weights_))
        spec_k_weight = float(np.sum(self.spec_weights_[self.spec_votes_ == self.k_hat_]))
        spec_total = float(np.sum(self.spec_weights_))
        self.raw_confidence_ = raw_k_weight / raw_total if raw_total > 0 else 0.0
        self.spec_confidence_ = spec_k_weight / spec_total if spec_total > 0 else 0.0
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
