from __future__ import annotations

from typing import Optional

import numpy as np
from sklearn.manifold import SpectralEmbedding

from .index import CBVIndex


class CBVSpectral(CBVIndex):
    """
    CBV-Spectral: applies spectral embedding (via sklearn SpectralEmbedding)
    before running CBV. Designed for non-convex cluster shapes.

    Parameters beyond CBVIndex
    ---------------------------
    n_components : int, default=10
        Embedded dimensionality.
    affinity : str, default='nearest_neighbors'
        Affinity parameter passed to SpectralEmbedding.

    See Also
    --------
    CBVIndex : Base class for CBV logic and parameter documentation.
    """

    def __init__(
        self,
        k_range=(2, 20),
        n_boot: int = 999,
        alpha: float = 0.05,
        random_state: Optional[int] = None,
        h_crit_tolerance: float = 1.3,
        mode: str = "threshold",
        bandwidth_method: str = "silverman",
        vote_method: str = "weighted_mean",
        n_components: int = 10,
        affinity: str = "nearest_neighbors",
        weight_method: str = "excess_mass",
    ) -> None:
        super().__init__(
            k_range=k_range,
            n_boot=n_boot,
            alpha=alpha,
            random_state=random_state,
            h_crit_tolerance=h_crit_tolerance,
            mode=mode,
            bandwidth_method=bandwidth_method,
            vote_method=vote_method,
            weight_method=weight_method,
        )
        self.n_components = n_components
        self.affinity = affinity
        self.k_hat_cbv_: Optional[int] = None

    def fit(self, X: np.ndarray) -> "CBVSpectral":
        """
        Fit CBVSpectral to data X.

        1. Run CBV on raw data (stored as ``k_hat_cbv_``).
        2. Apply spectral embedding to ``X``.
        3. Run CBV on the embedded representation (stored as ``k_hat_``).

        Parameters
        ----------
        X : np.ndarray of shape (n_samples, n_features)
            Input data.

        Returns
        -------
        self
        """
        X = np.asarray(X, dtype=np.float64)
        n_samples = X.shape[0]

        # 1. CBV on raw data for reference
        raw_estimator = CBVIndex(
            k_range=self.k_range,
            n_boot=self.n_boot,
            alpha=self.alpha,
            random_state=self.random_state,
            h_crit_tolerance=self.h_crit_tolerance,
            mode=self.mode,
            bandwidth_method=self.bandwidth_method,
            vote_method=self.vote_method,
        )
        raw_estimator.fit(X)
        self.k_hat_cbv_ = raw_estimator.k_hat_

        # 2. Spectral embedding
        n_components = min(self.n_components, n_samples - 1, X.shape[1])

        embedder = SpectralEmbedding(
            n_components=n_components,
            affinity=self.affinity,
            random_state=self.random_state,
        )
        X_embed = embedder.fit_transform(X)

        # 3. CBV on embedded representation
        super().fit(X_embed)

        return self
