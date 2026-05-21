import numpy as np
from sklearn.datasets import make_blobs as sk_make_blobs
from sklearn.datasets import make_classification as sk_make_classification
from sklearn.datasets import make_moons as sk_make_moons
from sklearn.datasets import make_circles as sk_make_circles
from typing import Dict, List, Optional, Tuple


class SyntheticDataGenerator:
    """Generates synthetic datasets with known ground-truth cluster counts.

    Parameters
    ----------
    random_state : int, default=42
        Seed for reproducible dataset generation.
    """

    def __init__(self, random_state: int = 42) -> None:
        self.random_state = random_state

    def make_blobs(
        self,
        n_samples: int = 300,
        n_features: int = 2,
        n_clusters: int = 3,
        cluster_std: float = 1.0,
        center_box: tuple = (-10.0, 10.0),
        shuffle: bool = True,
        name: Optional[str] = None,
    ) -> Dict:
        """Generate isotropic Gaussian blobs with known cluster assignments.

        Parameters
        ----------
        n_samples : int
            Total number of samples.
        n_features : int
            Number of features.
        n_clusters : int
            Number of ground-truth clusters.
        cluster_std : float
            Standard deviation of each cluster.
        center_box : tuple of (float, float)
            Bounding box for cluster centers.
        shuffle : bool
            Whether to shuffle samples.
        name : str or None
            Custom dataset name; auto-generated if None.

        Returns
        -------
        dict with keys 'X', 'y_true', 'name', 'params'.
        """
        X, y_true = sk_make_blobs(
            n_samples=n_samples,
            n_features=n_features,
            centers=n_clusters,
            cluster_std=cluster_std,
            center_box=center_box,
            shuffle=shuffle,
            random_state=self.random_state,
        )

        if name is None:
            name = (
                f"blobs_k{n_clusters}_d{n_features}_std{cluster_std}"
            )

        params = {
            "n_samples": n_samples,
            "n_features": n_features,
            "n_clusters": n_clusters,
            "cluster_std": cluster_std,
            "generator": "make_blobs",
        }

        return {
            "X": X,
            "y_true": y_true,
            "name": name,
            "k_true": n_clusters,
            "n_samples": n_samples,
            "n_features": n_features,
            "params": params,
        }

    def make_classification(
        self,
        n_samples: int = 300,
        n_features: int = 5,
        n_informative: int = 2,
        n_redundant: int = 0,
        n_clusters_per_class: int = 1,
        n_classes: int = 2,
        flip_y: float = 0.01,
        name: Optional[str] = None,
    ) -> Dict:
        """Generate a classification dataset with noise dimensions.

        Useful for testing cluster-index robustness to irrelevant features.

        Parameters
        ----------
        n_samples : int
            Total number of samples.
        n_features : int
            Total number of features (informative + redundant + noise).
        n_informative : int
            Number of informative features.
        n_redundant : int
            Number of redundant (linear combination of informative) features.
        n_clusters_per_class : int
            Number of clusters per class.
        n_classes : int
            Number of classes (labels).
        flip_y : float
            Fraction of labels randomly flipped to inject noise.
        name : str or None
            Custom dataset name; auto-generated if None.

        Returns
        -------
        dict with keys 'X', 'y_true', 'name', 'params'.
        """
        n_noise = n_features - n_informative - n_redundant

        X, y_true = sk_make_classification(
            n_samples=n_samples,
            n_features=n_features,
            n_informative=n_informative,
            n_redundant=n_redundant,
            n_clusters_per_class=n_clusters_per_class,
            n_classes=n_classes,
            flip_y=flip_y,
            random_state=self.random_state,
        )

        if name is None:
            name = (
                f"classif_k{n_classes}"
                f"_info{n_informative}_noise{n_noise}"
            )

        params = {
            "n_samples": n_samples,
            "n_features": n_features,
            "n_informative": n_informative,
            "n_noise": n_noise,
            "n_clusters_per_class": n_clusters_per_class,
            "n_classes": n_classes,
            "generator": "make_classification",
        }

        return {
            "X": X,
            "y_true": y_true,
            "name": name,
            "k_true": n_classes,
            "n_samples": n_samples,
            "n_features": n_features,
            "params": params,
        }

    def make_moons(
        self,
        n_samples: int = 300,
        noise: float = 0.05,
        name: Optional[str] = None,
    ) -> Dict:
        """Generate two interleaving half-circles (non-convex shape).

        Parameters
        ----------
        n_samples : int
            Total number of samples.
        noise : float
            Standard deviation of Gaussian noise added to the data.
        name : str or None
            Custom dataset name; auto-generated if None.

        Returns
        -------
        dict with keys 'X', 'y_true', 'name', 'params'.
        """
        X, y_true = sk_make_moons(
            n_samples=n_samples,
            noise=noise,
            random_state=self.random_state,
        )

        if name is None:
            name = f"moons_noise{noise}"

        params = {
            "n_samples": n_samples,
            "noise": noise,
            "generator": "make_moons",
        }

        return {
            "X": X,
            "y_true": y_true,
            "name": name,
            "k_true": 2,
            "n_samples": n_samples,
            "n_features": 2,
            "params": params,
        }

    def make_circles(
        self,
        n_samples: int = 300,
        factor: float = 0.5,
        noise: float = 0.05,
        name: Optional[str] = None,
    ) -> Dict:
        """Generate two concentric circles (non-convex shape).

        Parameters
        ----------
        n_samples : int
            Total number of samples.
        factor : float
            Scale factor between inner and outer circle (0 < factor < 1).
        noise : float
            Standard deviation of Gaussian noise added to the data.
        name : str or None
            Custom dataset name; auto-generated if None.

        Returns
        -------
        dict with keys 'X', 'y_true', 'name', 'params'.
        """
        X, y_true = sk_make_circles(
            n_samples=n_samples,
            factor=factor,
            noise=noise,
            random_state=self.random_state,
        )

        if name is None:
            name = f"circles_factor{factor}_noise{noise}"

        params = {
            "n_samples": n_samples,
            "factor": factor,
            "noise": noise,
            "generator": "make_circles",
        }

        return {
            "X": X,
            "y_true": y_true,
            "name": name,
            "k_true": 2,
            "n_samples": n_samples,
            "n_features": 2,
            "params": params,
        }

    def make_anisotropic_blobs(
        self,
        n_samples: int = 300,
        n_features: int = 2,
        n_clusters: int = 3,
        stretch: float = 3.0,
        name: Optional[str] = None,
    ) -> Dict:
        """Generate elongated (anisotropic) Gaussian blobs.

        Creates isotropic blobs then applies a random rotation + stretch
        transformation, producing ellipsoidal clusters.

        Parameters
        ----------
        n_samples : int
            Total number of samples.
        n_features : int
            Number of features.
        n_clusters : int
            Number of ground-truth clusters.
        stretch : float
            Factor by which to stretch one axis relative to others.
        name : str or None
            Custom dataset name; auto-generated if None.

        Returns
        -------
        dict with keys 'X', 'y_true', 'name', 'params'.
        """
        rng = np.random.RandomState(self.random_state)

        # Generate isotropic blobs
        X, y_true = sk_make_blobs(
            n_samples=n_samples,
            n_features=n_features,
            centers=n_clusters,
            cluster_std=1.0,
            random_state=self.random_state,
        )

        # Build a random rotation matrix
        Q, _ = np.linalg.qr(rng.randn(n_features, n_features))

        # Scale vector: stretch first axis, keep others at 1
        s = np.ones(n_features)
        s[0] = stretch

        # Apply: X_stretched = X @ (Q * s)
        X = X @ (Q * s)

        if name is None:
            name = f"aniso_k{n_clusters}_d{n_features}_stretch{stretch}"

        params = {
            "n_samples": n_samples,
            "n_features": n_features,
            "n_clusters": n_clusters,
            "stretch": stretch,
            "generator": "make_anisotropic_blobs",
        }

        return {
            "X": X,
            "y_true": y_true,
            "name": name,
            "k_true": n_clusters,
            "n_samples": n_samples,
            "n_features": n_features,
            "params": params,
        }

    def make_varied_blobs(
        self,
        n_samples: int = 300,
        n_features: int = 2,
        n_clusters: int = 3,
        cluster_stds: Tuple[float, ...] = (0.5, 1.0, 2.0),
        name: Optional[str] = None,
    ) -> Dict:
        """Generate blobs with different standard deviations per cluster.

        Parameters
        ----------
        n_samples : int
            Total number of samples.
        n_features : int
            Number of features.
        n_clusters : int
            Number of ground-truth clusters.
        cluster_stds : tuple of float
            Standard deviation for each cluster. Length must equal n_clusters.
        name : str or None
            Custom dataset name; auto-generated if None.

        Returns
        -------
        dict with keys 'X', 'y_true', 'name', 'params'.
        """
        # Generate each cluster separately to allow per-cluster std
        X_list: List[np.ndarray] = []
        y_list: List[np.ndarray] = []
        centers = sk_make_blobs(
            n_samples=n_clusters, n_features=n_features,
            centers=n_clusters, random_state=self.random_state,
        )[0]

        samples_per_cluster = [n_samples // n_clusters] * n_clusters
        # Distribute remainder
        for i in range(n_samples % n_clusters):
            samples_per_cluster[i] += 1

        for i in range(n_clusters):
            Xi, yi = sk_make_blobs(
                n_samples=samples_per_cluster[i],
                n_features=n_features,
                centers=centers[i].reshape(1, -1),
                cluster_std=cluster_stds[i] if i < len(cluster_stds) else 1.0,
                random_state=self.random_state + i,
            )
            X_list.append(Xi)
            y_list.append(np.full(samples_per_cluster[i], i))

        X = np.vstack(X_list)
        y_true = np.concatenate(y_list)

        if name is None:
            std_str = "_".join(str(s) for s in cluster_stds)
            name = f"varied_k{n_clusters}_d{n_features}_stds{std_str}"

        params = {
            "n_samples": n_samples,
            "n_features": n_features,
            "n_clusters": n_clusters,
            "cluster_stds": list(cluster_stds),
            "generator": "make_varied_blobs",
        }

        return {
            "X": X,
            "y_true": y_true,
            "name": name,
            "k_true": n_clusters,
            "n_samples": n_samples,
            "n_features": n_features,
            "params": params,
        }

    def make_imbalanced_blobs(
        self,
        n_samples: int = 300,
        n_features: int = 2,
        n_clusters: int = 3,
        imbalance_ratio: float = 3.0,
        name: Optional[str] = None,
    ) -> Dict:
        """Generate blobs with imbalanced cluster sizes.

        Parameters
        ----------
        n_samples : int
            Total number of samples.
        n_features : int
            Number of features.
        n_clusters : int
            Number of ground-truth clusters.
        imbalance_ratio : float
            Ratio of largest to smallest cluster size.
        name : str or None
            Custom dataset name; auto-generated if None.

        Returns
        -------
        dict with keys 'X', 'y_true', 'name', 'params'.
        """
        # Geometric series of cluster sizes
        sizes = np.geomspace(imbalance_ratio, 1.0, n_clusters)
        sizes = sizes / sizes.sum() * n_samples
        sizes = np.round(sizes).astype(int)
        # Adjust to match total
        diff = n_samples - sizes.sum()
        sizes[-1] += diff

        centers = sk_make_blobs(
            n_samples=n_clusters, n_features=n_features,
            centers=n_clusters, random_state=self.random_state,
        )[0]

        X_list: List[np.ndarray] = []
        y_list: List[np.ndarray] = []
        for i in range(n_clusters):
            Xi, yi = sk_make_blobs(
                n_samples=max(sizes[i], 2),
                n_features=n_features,
                centers=centers[i].reshape(1, -1),
                cluster_std=1.0,
                random_state=self.random_state + i,
            )
            X_list.append(Xi)
            y_list.append(np.full(max(sizes[i], 2), i))

        X = np.vstack(X_list)
        y_true = np.concatenate(y_list)

        if name is None:
            name = f"imbal_k{n_clusters}_d{n_features}_ratio{imbalance_ratio}"

        params = {
            "n_samples": n_samples,
            "n_features": n_features,
            "n_clusters": n_clusters,
            "imbalance_ratio": imbalance_ratio,
            "generator": "make_imbalanced_blobs",
        }

        return {
            "X": X,
            "y_true": y_true,
            "name": name,
            "k_true": n_clusters,
            "n_samples": n_samples,
            "n_features": n_features,
            "params": params,
        }

    def generate_benchmark_suite(
        self, random_state: Optional[int] = None
    ) -> List[Dict]:
        """Generate a comprehensive benchmark suite of ~30+ synthetic datasets.

        Parameters
        ----------
        random_state : int or None
            Override the instance random_state for this call.

        Returns
        -------
        list of dataset dicts, each with keys 'X', 'y_true', 'name', 'params'.
        """
        if random_state is not None:
            self.random_state = random_state

        rng = self.random_state
        datasets: List[Dict] = []

        # ----- Well-separated blobs -----
        blobs_well_configs = [
            (3, 0.3),
            (3, 0.5),
            (3, 1.0),
            (5, 0.5),
            (5, 1.0),
            (8, 0.5),
        ]
        for n_clusters, std in blobs_well_configs:
            gen = SyntheticDataGenerator(random_state=rng)
            datasets.append(
                gen.make_blobs(
                    n_samples=300,
                    n_features=2,
                    n_clusters=n_clusters,
                    cluster_std=std,
                )
            )

        # ----- Overlapping blobs -----
        blobs_overlap_configs = [
            (3, 1.5),
            (3, 2.0),
            (3, 2.5),
            (5, 1.5),
            (5, 2.0),
        ]
        for n_clusters, std in blobs_overlap_configs:
            gen = SyntheticDataGenerator(random_state=rng)
            datasets.append(
                gen.make_blobs(
                    n_samples=300,
                    n_features=2,
                    n_clusters=n_clusters,
                    cluster_std=std,
                )
            )

        # ----- Noise dimensions (classification wrapper) -----
        noise_dim_configs = [
            (2, 2, 2),
            (2, 2, 5),
            (2, 2, 10),
            (3, 3, 3),
            (3, 3, 8),
        ]
        for n_informative, n_classes, n_noise in noise_dim_configs:
            n_features = n_informative + n_noise
            gen = SyntheticDataGenerator(random_state=rng)
            datasets.append(
                gen.make_classification(
                    n_samples=300,
                    n_features=n_features,
                    n_informative=n_informative,
                    n_redundant=0,
                    n_clusters_per_class=1,
                    n_classes=n_classes,
                )
            )

        # ----- Non-convex shapes -----
        moon_configs = [0.05, 0.1]
        circle_configs = [
            (0.3, 0.05),
            (0.3, 0.1),
            (0.5, 0.05),
            (0.5, 0.1),
        ]

        for noise in moon_configs:
            gen = SyntheticDataGenerator(random_state=rng)
            datasets.append(gen.make_moons(n_samples=300, noise=noise))

        for factor, noise in circle_configs:
            gen = SyntheticDataGenerator(random_state=rng)
            datasets.append(
                gen.make_circles(n_samples=300, factor=factor, noise=noise)
            )

        # ----- High-dimensional blobs -----
        hd_configs = [(5, 3), (30, 3), (50, 3)]
        for n_features, n_clusters in hd_configs:
            gen = SyntheticDataGenerator(random_state=rng)
            datasets.append(
                gen.make_blobs(
                    n_samples=300,
                    n_features=n_features,
                    n_clusters=n_clusters,
                    cluster_std=1.0,
                )
            )

        # ══════════════════════════════════════════════════════════════════
        # Phase C additions (+19 datasets)
        # ══════════════════════════════════════════════════════════════════

        # ----- Anisotropic blobs (3) -----
        aniso_configs = [
            (3, 3.0),
            (3, 5.0),
            (5, 3.0),
        ]
        for n_clusters, stretch in aniso_configs:
            gen = SyntheticDataGenerator(random_state=rng)
            datasets.append(
                gen.make_anisotropic_blobs(
                    n_samples=300, n_clusters=n_clusters, stretch=stretch,
                )
            )

        # ----- Imbalanced blobs (3) -----
        imbal_configs = [
            (3, 3.0),
            (3, 5.0),
            (5, 3.0),
        ]
        for n_clusters, ratio in imbal_configs:
            gen = SyntheticDataGenerator(random_state=rng)
            datasets.append(
                gen.make_imbalanced_blobs(
                    n_samples=300, n_clusters=n_clusters, imbalance_ratio=ratio,
                )
            )

        # ----- Varied-std blobs (3) -----
        varied_configs = [
            (3, (0.5, 1.5, 3.0)),
            (4, (0.5, 1.0, 2.0, 3.0)),
            (5, (0.3, 0.7, 1.5, 2.5, 4.0)),
        ]
        for n_clusters, stds in varied_configs:
            gen = SyntheticDataGenerator(random_state=rng)
            datasets.append(
                gen.make_varied_blobs(
                    n_samples=300, n_clusters=n_clusters, cluster_stds=stds,
                )
            )

        # ----- High-k blobs (3) — well-separated, k=10/12/15 -----
        highk_configs = [(10, 0.5), (12, 0.5), (15, 0.5)]
        for n_clusters, std in highk_configs:
            gen = SyntheticDataGenerator(random_state=rng)
            datasets.append(
                gen.make_blobs(
                    n_samples=600, n_features=2,
                    n_clusters=n_clusters, cluster_std=std,
                )
            )

        # ----- Sparse high-dim (3) — make_classification high noise -----
        sparse_configs = [
            (100, 3, 2),
            (100, 3, 5),
            (200, 5, 5),
        ]
        for n_features, n_classes, n_informative in sparse_configs:
            n_noise = n_features - n_informative
            gen = SyntheticDataGenerator(random_state=rng)
            datasets.append(
                gen.make_classification(
                    n_samples=300,
                    n_features=n_features,
                    n_informative=n_informative,
                    n_redundant=0,
                    n_clusters_per_class=1,
                    n_classes=n_classes,
                )
            )

        # ----- Non-convex shapes (2) — additional hard configurations -----
        gen = SyntheticDataGenerator(random_state=rng)
        datasets.append(
            gen.make_moons(n_samples=300, noise=0.15)
        )
        gen = SyntheticDataGenerator(random_state=rng)
        datasets.append(
            gen.make_circles(n_samples=300, factor=0.5, noise=0.15)
        )

        # ----- Small-n datasets (2) — test small-sample robustness -----
        for n_samples in [50, 100]:
            gen = SyntheticDataGenerator(random_state=rng)
            ds = gen.make_blobs(
                n_samples=n_samples,
                n_features=2,
                n_clusters=3,
                cluster_std=1.0,
            )
            # Override name to include sample size for uniqueness
            ds["name"] = f"smalln_k3_n{n_samples}"
            datasets.append(ds)

        return datasets
