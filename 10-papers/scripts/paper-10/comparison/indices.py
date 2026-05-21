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

# All KMeans-based CVIs use n_init=10 for reliable convergence
# (sklearn default since v0.23). CBV is KMeans-free and unaffected.
KMEANS_N_INIT = 10


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
        labels = KMeans(n_clusters=k, n_init=KMEANS_N_INIT, random_state=random_state).fit_predict(X)
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
        labels = KMeans(n_clusters=k, n_init=KMEANS_N_INIT, random_state=random_state).fit_predict(X)
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
        labels = KMeans(n_clusters=k, n_init=KMEANS_N_INIT, random_state=random_state).fit_predict(X)
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

        labels = KMeans(n_clusters=k, n_init=KMEANS_N_INIT, random_state=random_state).fit_predict(X)
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
            ref_labels = KMeans(n_clusters=k, n_init=KMEANS_N_INIT, random_state=random_state).fit_predict(X_ref)
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
        labels = KMeans(n_clusters=k, n_init=KMEANS_N_INIT, random_state=random_state).fit_predict(X)
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
        labels = KMeans(n_clusters=k, n_init=KMEANS_N_INIT, random_state=random_state).fit_predict(X)
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
# g. Hartigan Index (Hartigan, 1975)
# ---------------------------------------------------------------------------

def hartigan_cvi(
    X: np.ndarray,
    k_range: Tuple[int, int] = (2, 20),
    random_state: int = 42,
) -> Dict:
    """Hartigan's index (Hartigan, 1975).

    Hartigan(k) = (W_k / W_{k+1} - 1) * (n - k - 1)

    Choose the smallest k where Hartigan(k) <= 10 (rule-of-thumb threshold
    from Hartigan's original paper).

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
    n = X.shape[0]

    # Compute W_k for each k
    W_vals: Dict[int, float] = {}
    for k in range(k_min, k_max + 1):
        if k >= n:
            continue
        labels = KMeans(n_clusters=k, n_init=KMEANS_N_INIT, random_state=random_state).fit_predict(X)
        unique = len(set(labels))
        if unique < 2:
            continue
        W_vals[k] = _within_cluster_dispersion(X, labels)

    # Compute Hartigan statistic
    ks = sorted(W_vals.keys())
    scores: List[Tuple[int, float]] = []
    for i, k in enumerate(ks):
        if k == ks[-1] or k >= n:
            continue
        W_k = W_vals.get(k)
        W_k1 = W_vals.get(k + 1)
        if W_k is None or W_k1 is None or W_k1 == 0:
            continue
        h = (W_k / W_k1 - 1.0) * (n - k - 1)
        scores.append((k, h))

    if not scores:
        return {"k_hat": k_min, "scores": [], "best_score": None}

    # First k where Hartigan <= 10
    k_hat = k_min
    for k, h in scores:
        if h <= 10.0:
            k_hat = k
            break
    else:
        k_hat = scores[-1][0]  # fallback to last computed k

    best_score = max(s[1] for s in scores)
    return {"k_hat": k_hat, "scores": scores, "best_score": best_score}


# ---------------------------------------------------------------------------
# h. KL Index (Krzanowski & Lai, 1988)
# ---------------------------------------------------------------------------

def kl_cvi(
    X: np.ndarray,
    k_range: Tuple[int, int] = (2, 20),
    random_state: int = 42,
) -> Dict:
    """Krzanowski-Lai index (Krzanowski & Lai, 1988).

    KL(k) = |Diff_k / Diff_{k+1}|
    where Diff_k = (k-1)^(2/d) * W_{k-1} - k^(2/d) * W_k

    Higher KL(k) indicates stronger support for k clusters.
    Requires k_range to span at least 4 values.

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
    n, d = X.shape

    # Compute W_k for each k
    W_vals: Dict[int, float] = {}
    for k in range(k_min - 1, k_max + 1):
        if k < 1 or k >= n:
            continue
        labels = KMeans(n_clusters=k, n_init=KMEANS_N_INIT, random_state=random_state).fit_predict(X)
        unique = len(set(labels))
        if unique < 2:
            continue
        W_vals[k] = _within_cluster_dispersion(X, labels)

    ks = sorted(W_vals.keys())

    # Compute Diff_k for k = k_min..k_max (need W_{k-1} and W_k)
    diffs: Dict[int, float] = {}
    for k in ks:
        if k < k_min:
            continue
        W_km1 = W_vals.get(k - 1)
        W_k = W_vals.get(k)
        if W_km1 is None or W_k is None:
            continue
        diff = (k - 1) ** (2.0 / d) * W_km1 - k ** (2.0 / d) * W_k
        diffs[k] = diff

    diff_ks = sorted(diffs.keys())

    # Compute KL(k) = |Diff_k / Diff_{k+1}|
    scores: List[Tuple[int, float]] = []
    for i, k in enumerate(diff_ks):
        if k == diff_ks[-1]:
            continue
        Diff_k = diffs.get(k)
        Diff_k1 = diffs.get(k + 1)
        if Diff_k is None or Diff_k1 is None or Diff_k1 == 0:
            continue
        kl_val = abs(Diff_k / Diff_k1)
        scores.append((k, kl_val))

    if not scores:
        return {"k_hat": k_min, "scores": [], "best_score": None}

    best_k, best_score = max(scores, key=lambda x: x[1])
    return {"k_hat": best_k, "scores": scores, "best_score": best_score}


# ---------------------------------------------------------------------------
# i. Jump Statistic (Sugar & James, 2003)
# ---------------------------------------------------------------------------

def jump_cvi(
    X: np.ndarray,
    k_range: Tuple[int, int] = (2, 20),
    random_state: int = 42,
) -> Dict:
    """Jump statistic (Sugar & James, 2003).

    Uses the transformed distortion:
        J(k) = M_k^(-d/2) - M_{k-1}^(-d/2)
    where M_k = W_k / (n * d) is the mean squared error per dimension
    and d = number of features.

    The optimal k is where the "jump" in transformed distortion is largest.

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
    n, d = X.shape
    Y = d / 2.0  # transformation power

    # Compute distortion M_k for each k
    M_vals: Dict[int, float] = {}
    for k in range(k_min - 1, k_max + 1):
        if k < 1 or k >= n:
            continue
        labels = KMeans(n_clusters=k, n_init=KMEANS_N_INIT, random_state=random_state).fit_predict(X)
        unique = len(set(labels))
        if unique < 2:
            continue
        W_k = _within_cluster_dispersion(X, labels)
        M_vals[k] = W_k / (n * d)

    ks = sorted(M_vals.keys())

    # Compute J(k) for k = k_min..k_max
    scores: List[Tuple[int, float]] = []
    for k in ks:
        if k < k_min:
            continue
        M_k = M_vals.get(k)
        M_km1 = M_vals.get(k - 1)
        if M_k is None or M_km1 is None:
            continue
        if M_k <= 0 or M_km1 <= 0:
            continue
        jump_val = M_k ** (-Y) - M_km1 ** (-Y)
        if not np.isfinite(jump_val):
            continue
        scores.append((k, max(0.0, jump_val)))

    if not scores:
        return {"k_hat": k_min, "scores": [], "best_score": None}

    best_k, best_score = max(scores, key=lambda x: x[1])
    return {"k_hat": best_k, "scores": scores, "best_score": best_score}


# ---------------------------------------------------------------------------
# j. McClain-Rao Index (McClain & Rao, 1975)
# ---------------------------------------------------------------------------

def mcclain_rao_cvi(
    X: np.ndarray,
    k_range: Tuple[int, int] = (2, 20),
    random_state: int = 42,
) -> Dict:
    """McClain-Rao index (McClain & Rao, 1975).

    MR = mean_within_distance / mean_between_distance

    Lower values indicate better clustering (compact within, well-separated).

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
        labels = KMeans(n_clusters=k, n_init=KMEANS_N_INIT, random_state=random_state).fit_predict(X)
        unique_labels = np.unique(labels)
        if len(unique_labels) < 2:
            continue

        # Within-cluster pairwise distances
        within_dists = []
        between_dists = []

        cluster_points = {lbl: X[labels == lbl] for lbl in unique_labels}
        cluster_centers = {}
        for lbl, pts in cluster_points.items():
            cluster_centers[lbl] = pts.mean(axis=0)

        # Mean within-cluster distance
        for lbl, pts in cluster_points.items():
            if pts.shape[0] <= 1:
                continue
            pw = pdist(pts)
            within_dists.extend(pw.tolist())

        # Mean between-cluster distance (distance between cluster centers)
        lbls_list = list(unique_labels)
        for i in range(len(lbls_list)):
            for j in range(i + 1, len(lbls_list)):
                d = np.linalg.norm(cluster_centers[lbls_list[i]] - cluster_centers[lbls_list[j]])
                between_dists.append(d)

        if not within_dists or not between_dists:
            continue

        mean_within = np.mean(within_dists)
        mean_between = np.mean(between_dists)
        if mean_between == 0:
            continue

        mr = mean_within / mean_between
        scores.append((k, mr))

    if not scores:
        return {"k_hat": k_min, "scores": [], "best_score": None}

    best_k, _ = min(scores, key=lambda x: x[1])
    best_score = min(s[1] for s in scores)
    return {"k_hat": best_k, "scores": scores, "best_score": best_score}


# ---------------------------------------------------------------------------
# k. CVIWrapper — Unified interface
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
    """Return wrappers for all 10 baseline CVIs.

    CBV is intentionally excluded — it will be registered separately
    from its own module.
    DUD Index is excluded from most comparisons (monotonic, not designed
    for k-estimation) unless explicitly requested.

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
        CVIWrapper(hartigan_cvi, "Hartigan", k_range, random_state),
        CVIWrapper(kl_cvi, "KL Index", k_range, random_state),
        CVIWrapper(jump_cvi, "Jump Statistic", k_range, random_state),
        CVIWrapper(mcclain_rao_cvi, "McClain-Rao", k_range, random_state),
    ]
