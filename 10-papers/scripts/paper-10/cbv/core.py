from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from critband import bimodality_strength, critical_bandwidth, silverman_bandwidth


def per_dimension_votes(
    X: np.ndarray,
    k_min: int,
    k_max: int,
    h_crit_threshold: Optional[float] = None,
    h_crit_tolerance: float = 1.1,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute per-dimension k votes and bimodality-strength weights.

    For each dimension, iterates k from k_min to k_max and records the first
    k for which ``critical_bandwidth`` converges with ``h_crit`` smaller than
    ``tolerance * threshold`` (default threshold: Silverman rule-of-thumb
    bandwidth).

    Parameters
    ----------
    X : np.ndarray of shape (n_samples, n_features)
        Input data.
    k_min : int
        Minimum number of clusters / modes to test.
    k_max : int
        Maximum number of clusters / modes to test.
    h_crit_threshold : float or None, default=None
        Absolute threshold for ``h_crit``.  If None, uses the per-dimension
        Silverman bandwidth as the threshold.
    h_crit_tolerance : float, default=1.1
        Multiplier on ``threshold``. A value >1.0 relaxes the pass criterion
        ``h_crit < tolerance * threshold``, reducing false negatives when
        ``h_crit`` at the true k is slightly above the Silverman bandwidth.

    Returns
    -------
    votes : np.ndarray of shape (n_features,)
        Per-dimension k vote.
    weights : np.ndarray of shape (n_features,)
        Per-dimension bimodality-strength weight.
    """
    X = np.asarray(X, dtype=np.float64)
    n_features = X.shape[1]

    votes = np.full(n_features, fill_value=float(k_min), dtype=np.float64)
    weights = np.zeros(n_features, dtype=np.float64)

    for d in range(n_features):
        x_d = X[:, d]

        if np.ptp(x_d) == 0.0:
            continue

        threshold = (
            h_crit_threshold
            if h_crit_threshold is not None
            else silverman_bandwidth(x_d)
        )

        for k in range(k_min, k_max + 1):
            result = critical_bandwidth(
                x_d, k=k, return_ci=True
            )
            h_crit = result[0] if isinstance(result, tuple) else result
            converged = result[1] if isinstance(result, tuple) else False

            if converged and np.isfinite(h_crit) and h_crit < h_crit_tolerance * threshold:
                votes[d] = float(k)
                break

        try:
            bm = bimodality_strength(x_d)
            weights[d] = bm.strength_score
        except Exception as e:
            print(f"WARNING: bimodality_strength failed for dim {d}: {e}")
            weights[d] = 0.0

    return votes, weights


def aggregate_k(votes: np.ndarray, weights: np.ndarray) -> float:
    """
    Aggregate per-dimension votes into a single k estimate via weighted mean.

    Parameters
    ----------
    votes : np.ndarray
        Per-dimension k votes.
    weights : np.ndarray
        Per-dimension weights.

    Returns
    -------
    float
        Weighted average k estimate.
    """
    total_weight = float(np.sum(weights))
    if total_weight <= 0.0:
        return float(np.median(votes))
    return float(np.average(votes, weights=weights))


def compute_weighted_consensus(
    k_estimates: np.ndarray,
    weights: np.ndarray,
) -> Dict[str, object]:
    """
    Compute a weighted consensus from multiple k estimates.

    Parameters
    ----------
    k_estimates : np.ndarray
        Array of k estimates (one per dimension or per method).
    weights : np.ndarray
        Corresponding weights.

    Returns
    -------
    dict with keys:
        k_hat : float
            Weighted mean estimate.
        confidence : float
            Normalised weight sum (0 = no confidence, 1 = full).
        ambiguity_flag : bool
            True when multiple distinct k values have comparable support.
    """
    total_weight = float(np.sum(weights))

    if total_weight <= 0.0 or len(k_estimates) == 0:
        return {"k_hat": 0.0, "confidence": 0.0, "ambiguity_flag": True}

    k_hat = float(np.average(k_estimates, weights=weights))

    # Confidence: how concentrated the weight is on the most common k
    unique_ks, inverse = np.unique(k_estimates, return_inverse=True)
    weight_per_k = np.zeros_like(unique_ks, dtype=np.float64)
    for idx, w in zip(inverse, weights):
        weight_per_k[idx] += w
    top_two = np.sort(weight_per_k)[-2:] if len(weight_per_k) >= 2 else weight_per_k
    confidence = float(np.max(weight_per_k) / total_weight)

    # Ambiguity: top-two weights are close (within 20 %)
    ambiguity_flag = False
    if len(top_two) >= 2 and top_two[-1] > 0.0:
        ratio = top_two[-2] / top_two[-1]
        if ratio > 0.8:
            ambiguity_flag = True

    return {
        "k_hat": k_hat,
        "confidence": confidence,
        "ambiguity_flag": ambiguity_flag,
    }
