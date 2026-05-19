from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np
from sklearn.decomposition import PCA


def standardize(X: np.ndarray) -> np.ndarray:
    """
    Z-score standardize each feature (column) to zero mean and unit variance.

    Features with zero standard deviation are left as-is (not rescaled).

    Parameters
    ----------
    X : np.ndarray of shape (n_samples, n_features)
        Input data.

    Returns
    -------
    np.ndarray of shape (n_samples, n_features)
        Standardised data.
    """
    X = np.asarray(X, dtype=np.float64)
    mean = np.mean(X, axis=0)
    std = np.std(X, axis=0, ddof=0)
    std[std == 0.0] = 1.0  # avoid division by zero for constant features
    return (X - mean) / std


def pca_reduce(
    X: np.ndarray,
    n_components: Optional[int] = None,
    variance_threshold: Optional[float] = None,
) -> Tuple[np.ndarray, PCA]:
    """
    PCA dimensionality reduction.

    Either ``n_components`` or ``variance_threshold`` must be provided.  If
    both are given, ``n_components`` takes precedence.

    Parameters
    ----------
    X : np.ndarray of shape (n_samples, n_features)
        Input data.
    n_components : int or None, default=None
        Target number of principal components.
    variance_threshold : float or None, default=None
        Cumulative variance ratio to retain (e.g. 0.95 for 95 %).

    Returns
    -------
    X_reduced : np.ndarray of shape (n_samples, n_components)
        Transformed data.
    pca : PCA
        Fitted PCA object (useful for inspection / inverse transform).
    """
    X = np.asarray(X, dtype=np.float64)

    if n_components is not None:
        n = n_components
    elif variance_threshold is not None:
        # Fit full PCA first to determine the component count
        full_pca = PCA().fit(X)
        cumsum = np.cumsum(full_pca.explained_variance_ratio_)
        n = int(np.searchsorted(cumsum, variance_threshold) + 1)
        n = min(n, X.shape[1], X.shape[0])
    else:
        raise ValueError("Either n_components or variance_threshold must be provided")

    n = max(1, min(n, X.shape[1], X.shape[0]))
    pca = PCA(n_components=n)
    X_reduced = pca.fit_transform(X)
    return X_reduced, pca


# Mapping from issue name to (message, severity)
_ValidationIssue = Tuple[str, str]


def validate_data(X: np.ndarray) -> List[_ValidationIssue]:
    """
    Validate input data and return a list of issues found.

    Checks performed:
    - Presence of NaN or infinite values.
    - Constant features.
    - Number of samples relative to features.
    - Zero-variance overall.

    Parameters
    ----------
    X : np.ndarray of shape (n_samples, n_features)
        Input data to validate.

    Returns
    -------
    list of (issue, severity) tuples
        Each issue is ``(description, 'error' | 'warning')``.
    """
    X = np.asarray(X, dtype=np.float64)
    issues: List[_ValidationIssue] = []

    n_samples, n_features = X.shape

    if n_samples == 0 or n_features == 0:
        issues.append(("Empty array: zero samples or zero features.", "error"))
        return issues

    nan_mask = np.isnan(X)
    if np.any(nan_mask):
        n_nan = int(np.sum(nan_mask))
        issues.append(
            (f"Data contains {n_nan} NaN value(s).", "error")
        )

    inf_mask = np.isinf(X)
    if np.any(inf_mask):
        n_inf = int(np.sum(inf_mask))
        issues.append(
            (f"Data contains {n_inf} infinite value(s).", "error")
        )

    ptp = np.ptp(X, axis=0)
    n_constant = int(np.sum(ptp == 0.0))
    if n_constant > 0:
        issues.append(
            (f"{n_constant} feature(s) are constant.", "warning")
        )

    total_var = np.sum(np.var(X, axis=0, ddof=0))
    if total_var == 0.0:
        issues.append(
            ("Total variance is zero — all features are constant.", "error")
        )

    return issues
