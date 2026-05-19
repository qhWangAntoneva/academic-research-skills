from __future__ import annotations

from typing import Optional

import numpy as np
from critband import bimodality_strength


def compute_dimension_weights(X: np.ndarray) -> np.ndarray:
    """
    Compute bimodality-strength weights for each dimension.

    Uses ``critband.bimodality_strength`` which returns a result with a
    ``.strength_score`` attribute (0 = unimodal / noise, higher = more
    structured).  Constant dimensions receive weight 0.

    Parameters
    ----------
    X : np.ndarray of shape (n_samples, n_features)
        Input data.

    Returns
    -------
    np.ndarray of shape (n_features,)
        Weight per dimension.
    """
    X = np.asarray(X, dtype=np.float64)
    n_features = X.shape[1]
    weights = np.zeros(n_features, dtype=np.float64)

    for d in range(n_features):
        x_d = X[:, d]
        if np.ptp(x_d) == 0.0:
            continue
        try:
            bm = bimodality_strength(x_d)
            weights[d] = bm.strength_score
        except Exception:
            weights[d] = 0.0

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
