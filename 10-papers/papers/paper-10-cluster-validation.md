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
- k range: (2, 10), threshold mode (n_boot=10)
- Multi-seed protocol: [42, 73, 123, 256, 999] — mean ± std reported
- Metrics: Exact-match accuracy, MAE, ±1 accuracy, ARI
- Runtime: ~1500s (5 seeds, parallel n_jobs=-1)

**Multi-Seed, Multi-Metric Results (mean ± std across 5 seeds):**

| Index | Accuracy | MAE | ±1 Acc | ARI |
|-------|:--------:|:---:|:------:|:---:|
| Gap Statistic | 60.6% ± 3.5% | 1.10 ± 0.03 | 73.5% ± 1.4% | 0.607 ± 0.003 |
| CH Index | 54.8% ± 0.0% | 1.94 ± 0.09 | 74.2% ± 0.0% | 0.645 ± 0.003 |
| Silhouette | 45.8% ± 1.4% | 1.64 ± 0.12 | 65.2% ± 1.4% | 0.643 ± 0.006 |
| **CBV** | **43.9% ± 2.9%** | **0.79 ± 0.02** | **87.1% ± 0.0%** | **0.593 ± 0.011** |
| Davies-Bouldin | 32.3% ± 0.0% | 3.05 ± 0.17 | 51.6% ± 0.0% | 0.565 ± 0.002 |
| Dunn Index | 24.5% ± 1.8% | 2.70 ± 0.17 | 42.6% ± 1.4% | 0.512 ± 0.012 |

**Key Findings:**
- CBV achieves the **lowest MAE (0.79)** — when it misses k, it misses by less than any other index
- CBV achieves the **highest ±1 accuracy (87.1%)** — 13 points above the next best (CH at 74.2%)
- Exact-match accuracy (43.9%) is mid-pack but highly stable across seeds (std 2.9%)
- ARI (0.593) is competitive, trailing CH (0.645) and Silhouette (0.643)

**Statistical Significance (last seed reference):**
- Friedman test: chi²=101.60, p<0.0001 — indices differ significantly

**CBV Failure Categories (17/31 incorrect):**
- Non-convex shapes (moons, circles): CBV finds k=3 instead of k=2 — 6 failures
- High-k underestimation (k≥5 blobs): collapses to k=3-4 — 5 failures
- Low-noise blobs with k=3 (std 0.3, 0.5): CBV finds k=4 due to h_crit tolerance — 2 failures
- Real datasets (wine, digits[0,1,2]): low-dimensional signal not captured — 2 failures
- Classification noise (classif_k3_*): noise dimensions overwhelm — 2 failures

**Excess Mass Layer:** Implemented but requires n_boot≥50 for effective mode-counting; computationally prohibitive at full benchmark scale. Noted as future optimization.

### 8. Revision Status (Post-Peer Review)

The manuscript underwent a 5-reviewer panel peer review (2026-05-21) and received **Major Revision**. The full review is at `results/paper-10-peer-review-2026-05-21.md`. The revision proceeds through 6 phases:

| Phase | Description | Hours | Status |
|:-----:|-------------|:-----:|:------:|
| **A** | Quick Credibility Wins (mode rename, n_init, metrics, seeds) | 7.5 | ✅ Done |
| **B** | Methodology Hardening (tolerance calibration, multimodal weight) | 12 | **← Next** |
| **C** | Benchmark Expansion (new indices, more datasets) | 11 | Pending |
| **D** | Advanced Features (correlated ablation, SJ bandwidth, 2D proj) | 8 | Pending |
| **E** | Full Multi-Seed Benchmark | 4 | Pending |
| **F** | Manuscript Revision (narrative restructure, all sections) | 60+ | Pending |

**LaTeX conversion** (original Phase 7) deferred until after revision is accepted.

See `../roadmap-paper10-final.md` and `../handover.md` for detailed status.
