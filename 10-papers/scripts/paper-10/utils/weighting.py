from __future__ import annotations

from typing import Optional

import numpy as np
from critband import bimodality_strength, excess_mass


def multimodal_weight(
    x_d: np.ndarray,
    k_max: int = 10,
    method: str = "excess_mass",
) -> float:
    """
    Compute a multimodal weight for a single dimension.

    Unlike ``bimodality_strength`` (which only measures bimodality), this
    function weights dimensions by the number of modes detected, making it
    sensitive to higher-order multimodality.

    Parameters
    ----------
    x_d : np.ndarray of shape (n_samples,)
        1D data for a single dimension.
    k_max : int, default=10
        Maximum number of modes to consider.
    method : str, default='excess_mass'
        Weighting method:

        - ``'excess_mass'``: weight = min(1.0, n_modes / k_max).
          Directly proportional to the number of detected modes.
        - ``'bimodality_strength'``: legacy ``critband.bimodality_strength``
          score (only sensitive to bimodal vs unimodal).
        - ``'hybrid'``: geometric mean of excess_mass weight and
          bimodality strength.

    Returns
    -------
    float
        Weight in [0, 1].
    """
    if np.ptp(x_d) == 0.0:
        return 0.0

    if method == "bimodality_strength":
        try:
            bm = bimodality_strength(x_d)
            return float(bm.strength_score)
        except Exception:
            return 0.0

    # excess_mass mode: count modes directly
    try:
        em = excess_mass(x_d, n_modes_max=k_max, n_boot=0)
        n_modes = em.n_modes_estimated
        em_weight = min(1.0, n_modes / k_max)
    except Exception:
        em_weight = 0.0

    if method == "excess_mass":
        return em_weight

    # hybrid: geometric mean of excess_mass and bimodality strength
    if method == "hybrid":
        try:
            bm = bimodality_strength(x_d)
            bs = float(bm.strength_score)
        except Exception:
            bs = 0.0
        if em_weight > 0 and bs > 0:
            return float(np.sqrt(em_weight * bs))
        return max(em_weight, bs)

    raise ValueError(
        f"Unknown method '{method}'. "
        "Use 'excess_mass', 'bimodality_strength', or 'hybrid'."
    )


def compute_dimension_weights(
    X: np.ndarray,
    weight_method: str = "excess_mass",
    k_max: int = 10,
) -> np.ndarray:
    """
    Compute multimodal weights for each dimension.

    Parameters
    ----------
    X : np.ndarray of shape (n_samples, n_features)
        Input data.
    weight_method : str, default='excess_mass'
        Weighting method passed to :func:`multimodal_weight`.
    k_max : int, default=10
        Maximum number of modes (used by excess_mass method).

    Returns
    -------
    np.ndarray of shape (n_features,)
        Weight per dimension.
    """
    X = np.asarray(X, dtype=np.float64)
    n_features = X.shape[1]
    weights = np.zeros(n_features, dtype=np.float64)

    for d in range(n_features):
        weights[d] = multimodal_weight(
            X[:, d], k_max=k_max, method=weight_method
        )

    return weights


def weighted_k_vote(
    votes: np.ndarray,
    weights: np.ndarray,
    method: str = "weighted_mean",
) -> float:
    """
    Aggregate per-dimension k votes into a single estimate.

    Parameters
    ----------
    votes : np.ndarray
        Per-dimension k estimates.
    weights : np.ndarray
        Per-dimension weights.
    method : str, default='weighted_mean'
        Aggregation method.  One of:
        - ``'weighted_mean'`` : weighted arithmetic mean.
        - ``'median'`` : weighted median.
        - ``'mode'`` : unweighted mode (most common value).

    Returns
    -------
    float
        Aggregated k estimate.
    """
    if len(votes) == 0:
        return 2.0

    total_weight = float(np.sum(weights))

    if method == "weighted_mean":
        if total_weight <= 0.0:
            return float(np.median(votes))
        return float(np.average(votes, weights=weights))

    elif method == "median":
        # Weighted median
        if total_weight <= 0.0:
            return float(np.median(votes))
        order = np.argsort(votes)
        sorted_votes = votes[order]
        sorted_weights = weights[order]
        cumsum = np.cumsum(sorted_weights)
        cutoff = total_weight / 2.0
        idx = int(np.searchsorted(cumsum, cutoff))
        return float(sorted_votes[idx])

    elif method == "mode":
        # Unweighted mode
        unique, counts = np.unique(votes, return_counts=True)
        return float(unique[int(np.argmax(counts))])

    else:
        raise ValueError(
            f"Unknown method '{method}'. "
            "Use 'weighted_mean', 'median', or 'mode'."
        )
