import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from sklearn.datasets import (
    load_wine,
    load_iris,
    load_digits,
    load_breast_cancer,
    fetch_olivetti_faces,
)
from sklearn.utils import Bunch


class RealDataLoader:
    """Loads real-world datasets with known ground-truth class labels.

    The class labels serve as proxy ground-truth cluster assignments for
    evaluating cluster-number estimation indices. For datasets with many
    classes (e.g., digits), a subset of classes may be used.
    """

    def __init__(self) -> None:
        self._cached: Dict[str, Dict] = {}

    def _build_entry(
        self,
        X: np.ndarray,
        y_true: np.ndarray,
        name: str,
        difficulty: str = "unknown",
    ) -> Dict:
        """Package a dataset array into the standard entry dict.

        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
        y_true : ndarray of shape (n_samples,)
        name : str
        difficulty : str
            One of 'easy', 'medium', 'hard', 'unknown'.

        Returns
        -------
        dict with keys 'X', 'y_true', 'name', 'n_samples', 'n_features',
        'k_true', 'difficulty'.
        """
        # Deduplicate rows to avoid degenerate cases with duplicate points
        X_clean, unique_idx = np.unique(X, axis=0, return_index=True)
        y_clean = y_true[unique_idx]
        k_true = int(len(np.unique(y_clean)))
        n_samples = X_clean.shape[0]
        n_features = X_clean.shape[1]
        return {
            "X": X_clean,
            "y_true": y_clean,
            "name": name,
            "n_samples": n_samples,
            "n_features": n_features,
            "k_true": k_true,
            "difficulty": difficulty,
        }

    def load_wine(self) -> Dict:
        """Load the Wine dataset (178 x 13, 3 classes).

        Returns
        -------
        dataset dict.
        """
        if "wine" in self._cached:
            return self._cached["wine"]
        bunch: Bunch = load_wine()
        entry = self._build_entry(bunch.data, bunch.target, "wine", "easy")
        self._cached["wine"] = entry
        return entry

    def load_iris(self) -> Dict:
        """Load the Iris dataset (150 x 4, 3 classes).

        Returns
        -------
        dataset dict.
        """
        if "iris" in self._cached:
            return self._cached["iris"]
        bunch: Bunch = load_iris()
        entry = self._build_entry(bunch.data, bunch.target, "iris", "easy")
        self._cached["iris"] = entry
        return entry

    def load_digits(
        self, subset_classes: Optional[List[int]] = None
    ) -> Dict:
        """Load a subset of the Digits dataset (1797 x 64, up to 10 classes).

        Parameters
        ----------
        subset_classes : list of int or None
            Classes to retain. If None, uses classes 0, 1 (binary subset for
            k-estimation sanity).

        Returns
        -------
        dataset dict with k_true = len(subset_classes).
        """
        cache_key = f"digits_{subset_classes}"
        if cache_key in self._cached:
            return self._cached[cache_key]

        if subset_classes is None:
            subset_classes = [0, 1]

        bunch: Bunch = load_digits()
        mask = np.isin(bunch.target, subset_classes)
        X_sub = bunch.data[mask]
        y_sub = bunch.target[mask]

        # Remap labels to 0..len(subset_classes)-1
        label_map = {old: new for new, old in enumerate(subset_classes)}
        y_remapped = np.array([label_map[val] for val in y_sub])

        diff = "medium" if len(subset_classes) <= 5 else "hard"
        entry = self._build_entry(X_sub, y_remapped, cache_key, diff)
        self._cached[cache_key] = entry
        return entry

    def load_breast_cancer(self) -> Dict:
        """Load the Breast Cancer Wisconsin dataset (569 x 30, 2 classes).

        Returns
        -------
        dataset dict.
        """
        if "breast_cancer" in self._cached:
            return self._cached["breast_cancer"]
        bunch: Bunch = load_breast_cancer()
        entry = self._build_entry(
            bunch.data, bunch.target, "breast_cancer", "medium"
        )
        self._cached["breast_cancer"] = entry
        return entry

    def load_seeds(
        self, url: Optional[str] = None
    ) -> Dict:
        """Load the Seeds dataset (210 x 7, 3 classes) from UCI or a local path.

        Attempts to download from the UCI repository. If the download fails,
        prints instructions for manual download.

        Parameters
        ----------
        url : str or None
            URL or local file path for the Seeds dataset CSV. Defaults to the
            UCI repository URL.

        Returns
        -------
        dataset dict.
        """
        cache_key = "seeds"
        if cache_key in self._cached:
            return self._cached[cache_key]

        if url is None:
            url = (
                "https://archive.ics.uci.edu/ml/machine-learning-databases/"
                "00236/seeds_dataset.txt"
            )

        column_names = [
            "area", "perimeter", "compactness",
            "length_kernel", "width_kernel", "asymmetry_coeff",
            "length_groove", "label",
        ]

        try:
            df = pd.read_csv(url, sep=r"\s+", header=None, names=column_names)
            X = df.iloc[:, :-1].values.astype(np.float64)
            y_true = df.iloc[:, -1].values.astype(np.int64)
            entry = self._build_entry(X, y_true, "seeds", "easy")
        except Exception as e:
            raise RuntimeError(
                f"Failed to load Seeds dataset from {url}. "
                f"Error: {e}\n"
                "Download manually from:\n"
                "  https://archive.ics.uci.edu/ml/machine-learning-databases/"
                "00236/seeds_dataset.txt\n"
                "and place it locally, then pass the local path via url=."
            ) from e

        self._cached[cache_key] = entry
        return entry

    # ── OpenML-based loaders (Phase C additions) ──

    def _load_openml_dataset(
        self,
        openml_id: int,
        name: str,
        target_column: Optional[str] = None,
        difficulty: str = "unknown",
        pca_components: Optional[int] = None,
    ) -> Dict:
        """Load a dataset from OpenML.

        Parameters
        ----------
        openml_id : int
            OpenML dataset ID.
        name : str
            Cache key and dataset name.
        target_column : str or None
            Name of the target column. If None, auto-detected.
        difficulty : str
            One of 'easy', 'medium', 'hard', 'unknown'.
        pca_components : int or None
            If set, reduce dimensionality via PCA before returning.

        Returns
        -------
        dataset dict.
        """
        cache_key = f"openml_{name}"
        if cache_key in self._cached:
            return self._cached[cache_key]

        try:
            from sklearn.datasets import fetch_openml
            from sklearn.preprocessing import LabelEncoder

            data = fetch_openml(data_id=openml_id, as_frame=True, parser='pandas')

            # If target_column specified and exists, use it directly
            if target_column is not None and target_column in data.frame.columns:
                y_true_raw = data.frame[target_column].values
                feature_cols = [c for c in data.frame.columns if c != target_column]
                X = data.frame[feature_cols].values.astype(np.float64)
            else:
                X = data.data.values.astype(np.float64)
                y_true_raw = data.target.values

            # Encode non-numeric targets
            le = LabelEncoder()
            y_true = le.fit_transform(y_true_raw.astype(str))
            y_true = y_true.astype(np.int64)

            # Clean NaN rows
            valid_rows = ~np.isnan(X).any(axis=1)
            X = X[valid_rows]
            y_true = y_true[valid_rows]

            # Remove constant features
            col_std = np.std(X, axis=0)
            X = X[:, col_std > 0]

            # PCA reduction if requested
            if pca_components is not None and X.shape[1] > pca_components:
                from sklearn.decomposition import PCA
                pca = PCA(n_components=pca_components, random_state=42)
                X = pca.fit_transform(X)

            entry = self._build_entry(X, y_true, name, difficulty)
        except Exception as e:
            print(f"WARNING: Cannot load {name} from OpenML ({openml_id}): {e}")
            entry = {
                "X": np.empty((0, 0)),
                "y_true": np.empty(0),
                "name": f"{name}_unavailable",
                "n_samples": 0,
                "n_features": 0,
                "k_true": 0,
                "difficulty": "unavailable",
            }

        self._cached[cache_key] = entry
        return entry

    def load_glass(self) -> Dict:
        """Load the Glass Identification dataset (214 x 9, 6 classes).

        Returns
        -------
        dataset dict.
        """
        return self._load_openml_dataset(
            41, "glass", target_column="Type", difficulty="medium"
        )

    def load_wine_quality(self) -> Dict:
        """Load the Wine Quality (white) dataset (4898 x 11, 7 classes).

        Returns
        -------
        dataset dict.
        """
        return self._load_openml_dataset(
            40491, "wine_quality", target_column="quality", difficulty="hard"
        )

    def load_yeast(self) -> Dict:
        """Load the Yeast dataset (1484 x 8, 10 classes).

        Returns
        -------
        dataset dict.
        """
        return self._load_openml_dataset(
            181, "yeast", target_column="Class", difficulty="hard"
        )

    def load_ecoli(self) -> Dict:
        """Load the Ecoli dataset (336 x 7, 8 classes).

        Returns
        -------
        dataset dict.
        """
        return self._load_openml_dataset(
            39, "ecoli", target_column="Class", difficulty="medium"
        )

    def load_segmentation(self) -> Dict:
        """Load the Image Segmentation dataset (2310 x 19, 7 classes).

        Returns
        -------
        dataset dict.
        """
        return self._load_openml_dataset(
            36, "segmentation", target_column="class", difficulty="medium"
        )

    def load_olivetti_faces(self) -> Dict:
        """Load the Olivetti Faces dataset (400 x 4096, 40 subjects).

        Applies PCA to 64 components to reduce dimensionality for
        k-estimation benchmarking.

        Returns
        -------
        dataset dict.
        """
        cache_key = "olivetti_faces"
        if cache_key in self._cached:
            return self._cached[cache_key]

        try:
            olivetti = fetch_olivetti_faces(shuffle=True, random_state=42)
            X = olivetti.data
            y_true = olivetti.target

            # PCA to 64 dimensions
            from sklearn.decomposition import PCA
            pca = PCA(n_components=64, random_state=42)
            X = pca.fit_transform(X)

            entry = self._build_entry(X, y_true, "olivetti_faces", "hard")
        except Exception as e:
            print(f"WARNING: Cannot load Olivetti Faces: {e}")
            entry = {
                "X": np.empty((0, 0)),
                "y_true": np.empty(0),
                "name": "olivetti_faces_unavailable",
                "n_samples": 0,
                "n_features": 0,
                "k_true": 0,
                "difficulty": "unavailable",
            }

        self._cached[cache_key] = entry
        return entry

    def load_parkinsons(self) -> Dict:
        """Load the Parkinsons dataset (195 x 22, 2 classes).

        Returns
        -------
        dataset dict.
        """
        return self._load_openml_dataset(
            1488, "parkinsons", target_column="class", difficulty="medium"
        )

    def load_ionosphere(self) -> Dict:
        """Load the Ionosphere dataset (351 x 34, 2 classes).

        Returns
        -------
        dataset dict.
        """
        return self._load_openml_dataset(
            59, "ionosphere", target_column="class", difficulty="medium"
        )

    def load_all(
        self, include_seeds: bool = True, seeds_url: Optional[str] = None,
        include_openml: bool = True,
    ) -> List[Dict]:
        """Load all available real-world datasets.

        Parameters
        ----------
        include_seeds : bool
            Whether to attempt loading the Seeds dataset (requires network or
            local file).
        seeds_url : str or None
            Passed through to load_seeds().
        include_openml : bool
            Whether to attempt loading Phase C OpenML datasets.

        Returns
        -------
        list of dataset dicts.
        """
        datasets = [
            self.load_wine(),
            self.load_iris(),
            self.load_digits(subset_classes=[0, 1]),
            self.load_digits(subset_classes=[0, 1, 2]),
            self.load_digits(subset_classes=list(range(10))),
            self.load_breast_cancer(),
        ]

        if include_seeds:
            try:
                datasets.append(self.load_seeds(url=seeds_url))
            except RuntimeError as e:
                print(f"WARNING: Skipping Seeds dataset. {e}")

        if include_openml:
            # Phase C additions (9 datasets, gracefully skip on failure)
            for loader_name in [
                "load_glass", "load_wine_quality", "load_yeast",
                "load_ecoli", "load_segmentation", "load_olivetti_faces",
                "load_parkinsons", "load_ionosphere",
            ]:
                entry = getattr(self, loader_name)()
                if entry.get("n_samples", 0) > 0:
                    datasets.append(entry)
                else:
                    print(f"WARNING: Skipping unavailable dataset: {loader_name}")

        return datasets

    def get_metadata(self) -> pd.DataFrame:
        """Return a summary DataFrame of all currently loaded datasets.

        To populate the cache, call the desired load_* methods first.

        Returns
        -------
        pd.DataFrame with columns: name, n_samples, n_features, k_true,
        difficulty.
        """
        if not self._cached:
            # Load defaults so metadata is meaningful even if called cold
            self.load_all(include_seeds=False)

        records = []
        for entry in self._cached.values():
            records.append(
                {
                    "name": entry["name"],
                    "n_samples": entry["n_samples"],
                    "n_features": entry["n_features"],
                    "k_true": entry["k_true"],
                    "difficulty": entry["difficulty"],
                }
            )

        df = pd.DataFrame(records)
        df = df.sort_values("name").reset_index(drop=True)
        return df
