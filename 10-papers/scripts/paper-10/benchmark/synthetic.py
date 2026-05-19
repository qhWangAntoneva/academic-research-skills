import numpy as np
from sklearn.datasets import make_blobs as sk_make_blobs
from sklearn.datasets import make_classification as sk_make_classification
from sklearn.datasets import make_moons as sk_make_moons
from sklearn.datasets import make_circles as sk_make_circles
from typing import Dict, List, Optional


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

        return datasets
