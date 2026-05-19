"""Cluster validation index (CVI) wrappers for CBV comparison.

Provides 6 baseline CVIs + a unified wrapper class.
All indices follow the same interface:

    def index_func(X, k_range=(2, 20), random_state=42) -> dict
"""

import warnings
from functools import partial
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
from scipy.spatial.distance import cdist, pdist, squareform
from sklearn.cluster import KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)


# ---------------------------------------------------------------------------
# a. Silhouette Index
# ---------------------------------------------------------------------------

def silhouette_cvi(
    X: np.ndarray,
    k_range: Tuple[int, int] = (2, 20),
    random_state: int = 42,
) -> Dict:
    """Silhouette coefficient. Higher score = better clustering.

    Parameters
    ----------
    X : ndarray of shape (n_samples, n_features)
    k_range : tuple (min, max), default=(2, 20)
    random_state : int, default=42

    Returns
    -------
    dict with keys: k_hat, scores, best_score
    """
    k_min, k_max = k_range
    scores: List[Tuple[int, float]] = []

    for k in range(k_min, k_max + 1):
        if k >= X.shape[0]:
            continue
        labels = KMeans(n_clusters=k, n_init=3, random_state=random_state).fit_predict(X)
        unique = len(set(labels))
        if unique < 2:
            continue
        s = silhouette_score(X, labels)
        scores.append((k, s))

    if not scores:
        return {"k_hat": k_min, "scores": [], "best_score": None}

    best_k, best_score = max(scores, key=lambda x: x[1])
    return {"k_hat": best_k, "scores": scores, "best_score": best_score}


# ---------------------------------------------------------------------------
# b. Calinski-Harabasz Index (Variance Ratio Criterion)
# ---------------------------------------------------------------------------

def ch_cvi(
    X: np.ndarray,
    k_range: Tuple[int, int] = (2, 20),
    random_state: int = 42,
) -> Dict:
    """Calinski-Harabasz (CH) index. Higher score = better clustering.

    Parameters
    ----------
    X : ndarray of shape (n_samples, n_features)
    k_range : tuple (min, max), default=(2, 20)
    random_state : int, default=42

    Returns
    -------
    dict with keys: k_hat, scores, best_score
    """
    k_min, k_max = k_range
    scores: List[Tuple[int, float]] = []

    for k in range(k_min, k_max + 1):
        if k >= X.shape[0]:
            continue
        labels = KMeans(n_clusters=k, n_init=3, random_state=random_state).fit_predict(X)
        unique = len(set(labels))
        if unique < 2:
            continue
        s = calinski_harabasz_score(X, labels)
        scores.append((k, s))

    if not scores:
        return {"k_hat": k_min, "scores": [], "best_score": None}

    best_k, best_score = max(scores, key=lambda x: x[1])
    return {"k_hat": best_k, "scores": scores, "best_score": best_score}


# ---------------------------------------------------------------------------
# c. Davies-Bouldin Index
# ---------------------------------------------------------------------------

def db_cvi(
    X: np.ndarray,
    k_range: Tuple[int, int] = (2, 20),
    random_state: int = 42,
) -> Dict:
    """Davies-Bouldin index. **Lower** score = better clustering.

    Parameters
    ----------
    X : ndarray of shape (n_samples, n_features)
    k_range : tuple (min, max), default=(2, 20)
    random_state : int, default=42

    Returns
    -------
    dict with keys: k_hat, scores, best_score
    """
    k_min, k_max = k_range
    scores: List[Tuple[int, float]] = []

    for k in range(k_min, k_max + 1):
        if k >= X.shape[0]:
            continue
        labels = KMeans(n_clusters=k, n_init=3, random_state=random_state).fit_predict(X)
        unique = len(set(labels))
        if unique < 2:
            continue
        s = davies_bouldin_score(X, labels)
        scores.append((k, s))

    if not scores:
        return {"k_hat": k_min, "scores": [], "best_score": None}

    best_k, best_score = min(scores, key=lambda x: x[1])
    return {"k_hat": best_k, "scores": scores, "best_score": best_score}


# ---------------------------------------------------------------------------
# d. Gap Statistic
# ---------------------------------------------------------------------------

def _within_cluster_dispersion(X: np.ndarray, labels: np.ndarray) -> float:
    """Compute W_k: sum of pairwise squared distances within each cluster."""
    unique_labels = set(labels)
    Wk = 0.0
    for lbl in unique_labels:
        mask = labels == lbl
        cluster_points = X[mask]
        nk = cluster_points.shape[0]
        if nk <= 1:
            continue
        # W_k = (1 / (2 * n_k)) * sum_{i,j} ||x_i - x_j||^2
        pairwise_dist = pdist(cluster_points, metric="sqeuclidean")
        Wk += pairwise_dist.sum() / nk
    return Wk


def gap_cvi(
    X: np.ndarray,
    k_range: Tuple[int, int] = (2, 20),
    random_state: int = 42,
    B: int = 50,
    use_1se_rule: bool = True,
) -> Dict:
    """Gap statistic (Tibshirani et al. 2001).

    Parameters
    ----------
    X : ndarray of shape (n_samples, n_features)
    k_range : tuple (min, max), default=(2, 20)
    random_state : int, default=42
    B : int, default=50 — number of reference datasets
    use_1se_rule : bool, default=True
        If True, use the 1-standard-error rule (smallest k s.t.
        gap(k) >= gap(k+1) - s_{k+1}). Otherwise return k with max gap.

    Returns
    -------
    dict with keys: k_hat, scores (gap values), best_score
    """
    rng = np.random.RandomState(random_state)
    k_min, k_max = k_range
    n, d = X.shape

    feature_ranges = X.max(axis=0) - X.min(axis=0)

    log_Wks: List[float] = []
    gap_scores: List[float] = []
    s_k_list: List[float] = []

    for k in range(k_min, k_max + 1):
        if k >= n:
            continue

        labels = KMeans(n_clusters=k, n_init=3, random_state=random_state).fit_predict(X)
        log_Wk = np.log(_within_cluster_dispersion(X, labels))
        log_Wks.append(log_Wk)

        # Generate B reference datasets
        ref_log_W = np.zeros(B)
        for b in range(B):
            X_ref = rng.uniform(
                low=X.min(axis=0),
                high=X.max(axis=0),
                size=(n, d),
            )
            ref_labels = KMeans(n_clusters=k, n_init=3, random_state=random_state).fit_predict(X_ref)
            if len(set(ref_labels)) < 2:
                ref_log_W[b] = 0.0
            else:
                ref_log_W[b] = np.log(_within_cluster_dispersion(X_ref, ref_labels))

        # Since ref_log_W can be -inf for degenerate cases, filter them
        finite_mask = np.isfinite(ref_log_W)
        if finite_mask.sum() < 2:
            gap_scores.append(-np.inf)
            s_k_list.append(0.0)
            continue

        mean_ref = ref_log_W[finite_mask].mean()
        s_k = ref_log_W[finite_mask].std() * np.sqrt(1.0 + 1.0 / finite_mask.sum())
        gap = mean_ref - log_Wk
        gap_scores.append(gap)
        s_k_list.append(s_k)

    if not gap_scores:
        return {"k_hat": k_min, "scores": [], "best_score": None}

    ks = list(range(k_min, k_min + len(gap_scores)))

    if use_1se_rule:
        k_hat = k_min
        for i in range(len(gap_scores) - 1):
            if gap_scores[i] >= gap_scores[i + 1] - s_k_list[i + 1]:
                k_hat = ks[i]
                break
        else:
            k_hat = ks[-1]
    else:
        k_hat = ks[int(np.argmax(gap_scores))]

    best_score = max(gap_scores)

    return {
        "k_hat": k_hat,
        "scores": list(zip(ks, gap_scores)),
        "best_score": best_score,
    }


# ---------------------------------------------------------------------------
# e. Dunn Index
# ---------------------------------------------------------------------------

def _dunn_index_for_labels(X: np.ndarray, labels: np.ndarray) -> float:
    """Compute Dunn index for a given label assignment.

    Dunn = min_intercluster_distance / max_intracluster_distance

    Uses sampling for large n to keep computation tractable.
    """
    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels)

    if n_clusters < 2:
        return 0.0

    cluster_points = {lbl: X[labels == lbl] for lbl in unique_labels}

    # max intracluster distance (diameter of largest cluster)
    max_diameter = 0.0
    for lbl, pts in cluster_points.items():
        if pts.shape[0] <= 1:
            continue
        # sample points if cluster is large
        if pts.shape[0] > 200:
            rng = np.random.RandomState(42)
            idx = rng.choice(pts.shape[0], size=200, replace=False)
            pts = pts[idx]
        pairwise = pdist(pts)
        if pairwise.size > 0:
            max_diameter = max(max_diameter, pairwise.max())

    if max_diameter == 0.0:
        return 0.0

    # min intercluster distance
    min_separation = np.inf
    cluster_labels = list(cluster_points.keys())
    for i in range(len(cluster_labels)):
        for j in range(i + 1, len(cluster_labels)):
            pts_i = cluster_points[cluster_labels[i]]
            pts_j = cluster_points[cluster_labels[j]]
            # sample if large
            if pts_i.shape[0] > 200:
                rng = np.random.RandomState(42)
                idx = rng.choice(pts_i.shape[0], size=200, replace=False)
                pts_i = pts_i[idx]
            if pts_j.shape[0] > 200:
                rng = np.random.RandomState(42)
                idx = rng.choice(pts_j.shape[0], size=200, replace=False)
                pts_j = pts_j[idx]
            dists = cdist(pts_i, pts_j)
            min_separation = min(min_separation, dists.min())

    if min_separation == np.inf:
        return 0.0

    return min_separation / max_diameter


def dunn_cvi(
    X: np.ndarray,
    k_range: Tuple[int, int] = (2, 20),
    random_state: int = 42,
) -> Dict:
    """Dunn index. Higher score = better clustering.

    Parameters
    ----------
    X : ndarray of shape (n_samples, n_features)
    k_range : tuple (min, max), default=(2, 20)
    random_state : int, default=42

    Returns
    -------
    dict with keys: k_hat, scores, best_score
    """
    k_min, k_max = k_range
    scores: List[Tuple[int, float]] = []

    for k in range(k_min, k_max + 1):
        if k >= X.shape[0]:
            continue
        labels = KMeans(n_clusters=k, n_init=3, random_state=random_state).fit_predict(X)
        unique = len(set(labels))
        if unique < 2:
            continue
        dunn = _dunn_index_for_labels(X, labels)
        scores.append((k, dunn))

    if not scores:
        return {"k_hat": k_min, "scores": [], "best_score": None}

    best_k, best_score = max(scores, key=lambda x: x[1])
    return {"k_hat": best_k, "scores": scores, "best_score": best_score}


# ---------------------------------------------------------------------------
# f. DUD Index (Distance-based, Liu et al. 2010)
# ---------------------------------------------------------------------------

def dud_cvi(
    X: np.ndarray,
    k_range: Tuple[int, int] = (2, 20),
    random_state: int = 42,
) -> Dict:
    """Distance-based DUD index (Liu et al. 2010).

    Computes a ratio of within-cluster compactness to between-cluster separation.
    Higher score = better clustering.

    Parameters
    ----------
    X : ndarray of shape (n_samples, n_features)
    k_range : tuple (min, max), default=(2, 20)
    random_state : int, default=42

    Returns
    -------
    dict with keys: k_hat, scores, best_score
    """
    k_min, k_max = k_range
    scores: List[Tuple[int, float]] = []
    n = X.shape[0]
    global_center = X.mean(axis=0)

    for k in range(k_min, k_max + 1):
        if k >= n:
            continue
        labels = KMeans(n_clusters=k, n_init=3, random_state=random_state).fit_predict(X)
        unique = len(set(labels))
        if unique < 2:
            continue

        # Within-cluster dispersion: mean distance to cluster center
        within_sum = 0.0
        between_sum = 0.0
        for lbl in np.unique(labels):
            mask = labels == lbl
            cluster_pts = X[mask]
            center = cluster_pts.mean(axis=0)
            # intra: mean distance to cluster center
            intra_dists = np.linalg.norm(cluster_pts - center, axis=1)
            within_sum += intra_dists.sum()
            # inter: distance from cluster center to global center, weighted by size
            inter_dist = np.linalg.norm(center - global_center)
            between_sum += cluster_pts.shape[0] * inter_dist

        # DUD = between / within (higher = better separated)
        if within_sum == 0:
            continue
        dud = between_sum / within_sum
        scores.append((k, dud))

    if not scores:
        return {"k_hat": k_min, "scores": [], "best_score": None}

    best_k, best_score = max(scores, key=lambda x: x[1])
    return {"k_hat": best_k, "scores": scores, "best_score": best_score}


# ---------------------------------------------------------------------------
# g. CVIWrapper — Unified interface
# ---------------------------------------------------------------------------

class CVIWrapper:
    """Wraps any CVI function into a sklearn-like interface.

    Parameters
    ----------
    func : callable
        The CVI function. Must accept (X, k_range, random_state) and return a dict
        with keys 'k_hat', 'scores', 'best_score'.
    name : str
        Display name for the index.
    k_range : tuple, default=(2, 20)
    random_state : int, default=42
    """

    def __init__(
        self,
        func: Callable,
        name: str,
        k_range: Tuple[int, int] = (2, 20),
        random_state: int = 42,
    ):
        self.func = func
        self.name = name
        self.k_range = k_range
        self.random_state = random_state
        self._result: Optional[Dict] = None

    def fit(self, X: np.ndarray) -> "CVIWrapper":
        """Run the CVI on data X. Stores result in self.k_hat_.

        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)

        Returns
        -------
        self
        """
        try:
            self._result = self.func(
                X,
                k_range=self.k_range,
                random_state=self.random_state,
            )
        except Exception as e:
            warnings.warn(f"{self.name} failed: {e}")
            self._result = {
                "k_hat": self.k_range[0],
                "scores": [],
                "best_score": None,
            }
        self.k_hat_ = self._result["k_hat"]
        return self

    def predict(self, X: Optional[np.ndarray] = None) -> int:
        """Return estimated number of clusters k.

        Parameters
        ----------
        X : ignored, present for API compatibility.

        Returns
        -------
        k_hat : int
        """
        if not hasattr(self, "k_hat_"):
            raise RuntimeError("CVIWrapper must be fitted before predict(). Call .fit(X) first.")
        return self.k_hat_

    def get_scores(self) -> List[Tuple[int, float]]:
        """Return list of (k, score) pairs.

        Returns
        -------
        scores : list of (int, float)
        """
        if self._result is None:
            raise RuntimeError("CVIWrapper must be fitted before get_scores(). Call .fit(X) first.")
        return self._result["scores"]

    def get_best_score(self) -> Optional[float]:
        """Return the best score value.

        Returns
        -------
        best_score : float or None
        """
        if self._result is None:
            raise RuntimeError("CVIWrapper must be fitted before get_best_score(). Call .fit(X) first.")
        return self._result["best_score"]

    def __repr__(self) -> str:
        return f"CVIWrapper({self.name}, k_range={self.k_range})"


# ---------------------------------------------------------------------------
# h. Factory function
# ---------------------------------------------------------------------------

def get_all_indices(
    k_range: Tuple[int, int] = (2, 20),
    random_state: int = 42,
) -> List[CVIWrapper]:
    """Return wrappers for all 6 baseline CVIs.

    CBV is intentionally excluded — it will be registered separately
    from its own module.

    Parameters
    ----------
    k_range : tuple (min, max), default=(2, 20)
    random_state : int, default=42

    Returns
    -------
    wrappers : list of CVIWrapper
    """
    return [
        CVIWrapper(silhouette_cvi, "Silhouette", k_range, random_state),
        CVIWrapper(ch_cvi, "CH Index", k_range, random_state),
        CVIWrapper(db_cvi, "Davies-Bouldin", k_range, random_state),
        CVIWrapper(gap_cvi, "Gap Statistic", k_range, random_state),
        CVIWrapper(dunn_cvi, "Dunn Index", k_range, random_state),
        CVIWrapper(dud_cvi, "DUD Index", k_range, random_state),
    ]
