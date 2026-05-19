# Paper 10: How Many Clusters Really? Critical Bandwidth as a Cluster Validation Index

> **Domain**: Machine Learning / Unsupervised Learning
> **Target Journal**: *Journal of Machine Learning Research*
> **Paper ID**: paper-10

---

## Research Protocol

### 1. Research Question

Can the critical bandwidth of feature distributions serve as a theoretically grounded internal cluster validation index that outperforms existing metrics at estimating the true number of clusters?

### 2. Protocol Steps

1. **Index development**: Define **CBV (Critical Bandwidth Validation)** index — aggregate per-dimension `critical_bandwidth()` weighted by `bimodality_strength()`
2. **Synthetic benchmark**: 30+ configurations (varied separation, anisotropy, noise dimensions, cluster count 2–8)
3. **Real-world benchmark**: 10+ labeled UCI datasets with known cluster structure
4. **Comparison**: CBV vs. silhouette, CH index, Davies-Bouldin, gap statistic, Dunn index, DUD
5. **Sensitivity analysis**: CBV stability under noise features, sample size variation, feature scaling, dimensionality
6. **Theoretical analysis**: Connection between Silverman's mode-counting and true cluster count

### 3. critband Functions

- `critical_bandwidth(x, k=2, return_ci=True)` — per-dimension base signal
- `bimodality_strength(x)` — aggregation weighting
- `excess_mass(x, n_boot=199)` — direct mode-count estimation across features
- `silverman_test(x, n_boot=999)` — statistical significance of modality

### 4. Data Sources

- scikit-learn synthetic: `make_blobs`, `make_classification`, `make_moons`, `make_circles`
- UCI Repository: archive.ics.uci.edu (wine, iris, digits, breast cancer, etc.)

### 5. Expected Challenges

- High dimensionality → curse of dimensionality affecting KDE
- Feature scaling dependency → standardization sensitivity analysis
- Negative space: non-convex clusters (moons, circles) not captured by modality
- Computational cost: many candidate k values → efficient implementation

### 6. Key References

**Must-cite (appear in every paper):**
- Zhang, R. & Wang, Q. (2026). critband: A Python Package for Critical Bandwidth Analysis of Multimodal Distributions. arXiv:2605.18686.
- critband v0.2.3 [Computer software]. https://pypi.org/project/critband/

**Track A — Cluster Validation Indices (Classic):**
- Rousseeuw, P.J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics*, 20, 53–65.
- Caliński, T. & Harabasz, J. (1974). A dendrite method for cluster analysis. *Communications in Statistics*, 3(1), 1–27.
- Tibshirani, R., Walther, G. & Hastie, T. (2001). Estimating the number of clusters in a data set via the gap statistic. *JRSS-B*, 63(2), 411–423.
- Davies, D.L. & Bouldin, D.W. (1979). A cluster separation measure. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 1(2), 224–227.
- Dunn, J.C. (1973). A fuzzy relative of the ISODATA process and its use in detecting compact well-separated clusters. *Journal of Cybernetics*, 3(3), 32–57.
- Liu, Y., Li, Z., Xiong, H., Gao, X. & Wu, J. (2010). Understanding and enhancement of internal clustering validation measures. *IEEE Transactions on Knowledge and Data Engineering*, 22(9), 1246–1260.
- Arbelaitz, O., Gurrutxaga, I., Muguerza, J., Pérez, J.M. & Perona, I. (2013). An extensive comparative study of cluster validity indices. *Pattern Recognition*, 46(1), 243–256.

**Track A — Recent / Competing CVIs:**
- CNMBI: Determining the Number of Clusters Using Center Pairwise Matching and Boundary Filtering (2026). arXiv:2603.26744.
- High-Dimensional BWDM: A Robust Nonparametric Clustering Validation Index for Large-Scale Data (2025). arXiv:2510.14145.
- A Bayesian Cluster Validity Index (2024). arXiv:2402.02162.
- A New Measure for Assessment of Clustering Based on Kernel Density Estimation (2022). arXiv:2201.02030.
- Comparing Clusterings and Numbers of Clusters by Aggregation of Calibrated CVI (2020). arXiv:2002.01822.
- Recovering the Number of Clusters in Data Sets with Noise Features Using Feature Rescaling Factors (2016). arXiv:1602.06989.

**Track B — Modality Testing (Foundational):**
- Silverman, B.W. (1981). Using kernel density estimates to investigate multimodality. *JRSS-B*, 43(1), 97–99.
- Silverman, B.W. (1986). *Density Estimation for Statistics and Data Analysis*. Chapman and Hall.
- Hartigan, J.A. & Hartigan, P.M. (1985). The Dip Test of Unimodality. *Annals of Statistics*, 13(1), 70–84.
- Müller, D.W. & Sawitzki, G. (1991). Excess Mass Estimates and Tests for Multimodality. *JASA*, 86(415), 738–746.

**Track B — Mode Clustering (Modality–Cluster Connection):**
- Chacón, J.E. (2014). A Comprehensive Approach to Mode Clustering. arXiv:1406.1780.
- Chacón, J.E. (2015). Risk Bounds for Mode Clustering. arXiv:1505.00482.
- Chacón, J.E. (2018). Analysis of a Mode Clustering Diagram. arXiv:1805.04187.
- Chen, Y., Genovese, C.R. & Wasserman, L. (2014). Clustering via Mode Seeking by Direct Estimation of the Gradient of a Log-Density. arXiv:1404.5028.
- Chen, Y., Genovese, C.R. & Wasserman, L. (2017). Mode-Seeking Clustering and Density Ridge Estimation via Direct Estimation of Density-Derivative-Ratios. arXiv:1707.01711.

**Theory / Methodology:**
- Hennig, C. (2015). What are true clusters? *Pattern Recognition Letters*, 64, 53–62.
- Von Luxburg, U., Williamson, R.C. & Guyon, I. (2012). Clustering: Science or art? *ICML Workshop on Unsupervised and Transfer Learning*.

### 7. Final Results

**Benchmark Configuration:**
- 31 datasets (25 synthetic + 6 real: wine, iris, digits[0,1], digits[0,1,2], breast cancer, seeds)
- 7 CV indices: Silhouette, CH Index, Davies-Bouldin, Gap Statistic, Dunn Index, DUD Index, CBV (CBVHybrid)
- k range: (2, 10), fast mode (n_boot=10), random_state=42
- Runtime: 248.1s (parallel, n_jobs=-1)

**Main Accuracy (DUD Index excluded — not designed for k-estimation):**

| Rank | Index | Accuracy | Correct/Total |
|:---:|-------|:--------:|:------------:|
| 1 | Gap Statistic | 64.5% | 20/31 |
| 2 | CH Index | 54.8% | 17/31 |
| 3 | **CBV** | **45.2%** | **14/31** |
| 3 | Silhouette | 45.2% | 14/31 |
| 5 | Davies-Bouldin | 32.3% | 10/31 |
| 6 | Dunn Index | 22.6% | 7/31 |

**Statistical Significance:**
- Friedman test: chi²=106.66, p<0.0001 — indices differ significantly
- Nemenyi post-hoc: CBV vs Silhouette: p=0.0116* (significant), CBV vs CH Index: p=0.0833 (trending)

**Mean Rank (lower is better):**
1. Silhouette: 2.13
2. CH Index: 2.48
3. Gap Statistic: 3.23
4. CBV: 4.00
5. Davies-Bouldin: 4.16
6. Dunn Index: 5.10

**CBV Failure Categories (17/31 incorrect):**
- Non-convex shapes (moons, circles): CBV finds k=3 instead of k=2 — 6 failures
- High-k underestimation (k≥5 blobs): collapses to k=3-4 — 5 failures
- Low-noise blobs with k=3 (std 0.3, 0.5): CBV finds k=4 due to h_crit tolerance — 2 failures
- Real datasets (wine, digits[0,1,2]): low-dimensional signal not captured — 2 failures
- Classification noise (classif_k3_*): noise dimensions overwhelm — 2 failures

**Excess Mass Layer:** Implemented but requires n_boot≥50 for effective mode-counting; computationally prohibitive at full benchmark scale. Noted as future optimization.

### 8. Next Steps

- [x] Phase 0: Configuration
- [x] Phase 1: Literature search (26 references identified, see §6)
- [x] **Phase 2: Architecture** — CBV Python class design + benchmark framework
  - [x] CBVIndex class (sklearn-compatible API)
  - [x] Core per-dimension k voting + bimodality weighting
  - [x] CBV-Spectral variant
  - [x] k selection: Sequential Silverman (primary) + elbow scan (validation)
  - [x] Benchmark runner (synthetic + UCI)
  - [x] Comparison wrappers (silhouette, CH, DB, gap, Dunn, DUD)
  - [x] Report generation (tables + figures)
- [x] Phase 3: Implementation + testing (final benchmark: 31 datasets, 248.1s, CBV 45.2%)
- [ ] **Phase 4: Manuscript draft** (academic-paper full mode)
