from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from critband import critical_bandwidth, silverman_bandwidth, silverman_test

from .weighting import compute_dimension_weights, weighted_k_vote


def sequential_silverman(
    X: np.ndarray,
    k_range: Tuple[int, int] = (2, 20),
    alpha: float = 0.05,
    random_state: Optional[int] = None,
) -> Dict[str, object]:
    """
    Primary k-selection method using sequential Silverman tests.

    Tests each k sequentially using the Silverman multimodality test on each
    dimension, then aggregates across dimensions.

    Parameters
    ----------
    X : np.ndarray of shape (n_samples, n_features)
        Input data.
    k_range : tuple (min, max), default=(2, 20)
        Range of candidate k values to test.
    alpha : float, default=0.05
        Significance level for the Silverman test.
    random_state : int or None, default=None
        Random seed for reproducibility.

    Returns
    -------
    dict with keys:
        k_hat : int
            Estimated number of clusters.
        p_values : np.ndarray of shape (n_features, k_values)
            Per-dimension, per-k p-values.
        sequential_results : list
            Per-k consensus dicts from compute_weighted_consensus.
    """
    X = np.asarray(X, dtype=np.float64)
    n_features = X.shape[1]
    rng = np.random.default_rng(random_state)
    k_min, k_max = k_range
    k_values = np.arange(k_min, k_max + 1)
    weights = compute_dimension_weights(X)

    p_value_matrix = np.full((n_features, len(k_values)), np.nan, dtype=np.float64)

    for d in range(n_features):
        if np.ptp(X[:, d]) == 0.0:
            continue
        for j, k in enumerate(k_values):
            try:
                st = silverman_test(
                    X[:, d],
                    n_resamples=999,
                    mod0=k - 1,
                    alpha=alpha,
                    random_state=rng,
                )
                p_value_matrix[d, j] = st.p_value
            except Exception:
                p_value_matrix[d, j] = np.nan

    # For each k, decide whether enough dimensions "accept" H0 (p > alpha)
    sequential_results = []
    votes_per_k = []
    for j, k in enumerate(k_values):
        p_col = p_value_matrix[:, j]
        valid = ~np.isnan(p_col)
        if np.sum(valid) == 0:
            accept_ratio = 0.0
        else:
            accept_ratio = float(np.mean(p_col[valid] > alpha))
        sequential_results.append({"k": int(k), "accept_ratio": accept_ratio})
        if accept_ratio > 0.5:
            votes_per_k.append(int(k))

    k_hat = votes_per_k[-1] if votes_per_k else k_min

    return {
        "k_hat": int(k_hat),
        "p_values": p_value_matrix,
        "sequential_results": sequential_results,
    }


def elbow_scan(
    X: np.ndarray,
    k_range: Tuple[int, int] = (2, 20),
    n_clusters_range: Optional[List[int]] = None,
) -> Dict[str, object]:
    """
    Validation method: compute critical-bandwidth profiles and detect elbow.

    Scans across k values and computes summary statistics (mean critical
    bandwidth across dimensions) to identify the "elbow" where adding more
    clusters yields diminishing returns.

    Parameters
    ----------
    X : np.ndarray of shape (n_samples, n_features)
        Input data.
    k_range : tuple (min, max), default=(2, 20)
        Range of candidate k values to test.
    n_clusters_range : list of int or None, default=None
        Explicit list of k values to test (overrides k_range if provided).

    Returns
    -------
    dict with keys:
        elbow_k : int
            Estimated elbow point.
        h_crit_profile : np.ndarray of shape (n_k_values,)
            Mean critical bandwidth per k.
        converged_profile : np.ndarray of shape (n_k_values,)
            Fraction of dimensions where critical_bandwidth converged per k.
    """
    X = np.asarray(X, dtype=np.float64)
    n_features = X.shape[1]

    if n_clusters_range is not None:
        k_values = np.asarray(n_clusters_range, dtype=int)
    else:
        k_values = np.arange(k_range[0], k_range[1] + 1)

    h_crit_profile = np.full(len(k_values), np.nan, dtype=np.float64)
    converged_profile = np.full(len(k_values), np.nan, dtype=np.float64)

    for j, k in enumerate(k_values):
        h_vals = []
        conv_vals = []
        for d in range(n_features):
            x_d = X[:, d]
            if np.ptp(x_d) == 0.0:
                continue
            try:
                result = critical_bandwidth(x_d, k=int(k), return_ci=True)
                h_crit = result[0] if isinstance(result, tuple) else result
                converged = result[1] if isinstance(result, tuple) else False
                h_vals.append(h_crit)
                conv_vals.append(1.0 if converged else 0.0)
            except Exception:
                continue

        if h_vals:
            h_crit_profile[j] = float(np.mean(h_vals))
            converged_profile[j] = float(np.mean(conv_vals))

    # Detect elbow: point of maximum curvature on h_crit_profile
    valid = np.where(np.isfinite(h_crit_profile))[0]
    if len(valid) < 3:
        elbow_idx = 0
    else:
        h = h_crit_profile[valid]
        # Second-order differences as curvature proxy
        d2 = np.diff(h, n=2)
        if len(d2) > 0:
            elbow_idx = valid[1 + int(np.argmax(d2))]
        else:
            elbow_idx = valid[0]

    return {
        "elbow_k": int(k_values[elbow_idx]) if len(k_values) > 0 else k_values[0],
        "h_crit_profile": h_crit_profile,
        "converged_profile": converged_profile,
    }
