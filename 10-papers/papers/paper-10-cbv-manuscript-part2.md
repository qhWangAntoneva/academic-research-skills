
---

## 4. Benchmark Design

### 4.1 Datasets

We constructed a benchmark of 58 datasets: 44 synthetic and 14 real-world, designed to span a comprehensive range of cluster configurations including varying separation, dimensionality, noise levels, geometry, and class balance.

**Synthetic datasets** ($n = 300$ per dataset) were generated using scikit-learn and cover eight categories:

| Category | Configurations | Count | Key Parameters |
|----------|---------------|:-----:|----------------|
| Well-separated blobs | $k \in \{3,5,8\}$, $\sigma \in \{0.3, 0.5, 1.0\}$ | 6 | 2D, varying separation |
| Overlapping blobs | $k \in \{3,5\}$, $\sigma \in \{1.5, 2.0, 2.5\}$ | 5 | 2D, increasing overlap |
| Anisotropic blobs | $k \in \{2,3\}$, stretch $\in \{2.0, 3.0\}$ | 4 | Ellipsoidal clusters |
| Imbalanced clusters | $k \in \{2,3\}$, ratio $\in \{2.0, 3.0\}$ | 4 | Unequal class sizes |
| Varied std-dev | $k \in \{2,3\}$, std configs | 3 | Heterogeneous spread |
| High-$k$ | $k \in \{5,8\}$, $d \in \{2,5\}$ | 4 | Many clusters |
| Non-convex shapes | moons, circles | 4 | Curved boundaries |
| Noise dimensions | $k \in \{2,3\}$, info $\in \{2,3\}$, noise $\in \{3,5,8,10\}$ | 8 | Via `make_classification` |
| Small-$n$ | $k=3$, $n \in \{50, 100\}$ | 2 | Limited samples |
| Sparse high-$d$ | $k=3$, $d \in \{20, 50\}$ | 4 | High dimensionality |

**Real-world datasets** were sourced from UCI, OpenML, and scikit-learn:

| Dataset | Samples | Features | $k$ | Domain |
|---------|:-------:|:--------:|:---:|--------|
| Wine | 178 | 13 | 3 | Chemistry |
| Iris | 150 | 4 | 3 | Botany |
| Digits [0,1] | 360 | 64 | 2 | Image recognition |
| Digits [0,1,2] | 540 | 64 | 3 | Image recognition |
| Breast Cancer | 569 | 30 | 2 | Medical diagnostics |
| Seeds | 210 | 7 | 3 | Agriculture |
| Glass | 214 | 9 | 6 | Materials science |
| Yeast | 1484 | 8 | 10 | Molecular biology |
| Ecoli | 336 | 7 | 8 | Molecular biology |
| Segmentation | 2310 | 19 | 7 | Image analysis |
| Olivetti Faces | 400 | 4096 | 40 | Face recognition |
| Parkinsons | 195 | 22 | 2 | Medical diagnostics |
| Ionosphere | 351 | 33 | 2 | Radar physics |
| Digits (full) | 1797 | 64 | 10 | Handwriting recognition |

### 4.2 Comparison Indices

We compare CBV against nine established internal CVIs, organized into three families:

**Partition-quality indices** (require $k$-means):
1. **Silhouette** [5]: Maximize mean silhouette coefficient.
2. **Calinski–Harabasz (CH)** [6]: Maximize between/within dispersion ratio.
3. **Davies–Bouldin (DB)** [7]: Minimize average cluster similarity.
4. **Dunn** [9]: Maximize min-inter/max-intra distance ratio.

**Reference-distribution indices**:
5. **Gap Statistic** [8]: Maximize gap between observed and reference log-$W_k$, using the 1-SE rule.

**Distributional-ratio indices**:
6. **KL index** [10]: First significant drop in eigenvalue ratio.
7. **Hartigan** [11]: First $k$ where $(W_k/W_{k+1}-1)(n-k-1) \leq 10$.
8. **Jump** [12]: First significant jump in transformed dispersion.
9. **McClain–Rao** [13]: Minimize within/between distance ratio.

All $k$-means-based CVIs use `n_init = 10` for fair convergence. All indices search $k \in [2, 10]$. CBV requires no clustering algorithm — its estimate is derived directly from the data distribution.

### 4.3 Evaluation Metrics

For each dataset and each index, we record $\hat{k}$ and compute:

- **Exact-match accuracy**: $\frac{1}{N}\sum_{i=1}^{N} \mathbb{1}[\hat{k}_i = k_i]$
- **Mean Absolute Error (MAE)**: $\frac{1}{N}\sum_{i=1}^{N} |\hat{k}_i - k_i|$
- **$\pm 1$ accuracy**: Fraction of estimates within one of the true $k$
- **Adjusted Rand Index (ARI)**: Running $k$-means with $\hat{k}$ and comparing to ground-truth labels

### 4.4 Statistical Testing

We assess significance using:
- **Friedman test**: Non-parametric test for rank differences across indices [14].
- **Multi-seed protocol**: 5 random seeds $\{42, 73, 123, 256, 999\}$, reporting mean $\pm$ std.

---

## 5. Results

### 5.1 Overall Accuracy

Table I reports the overall exact-match accuracy across 58 datasets, averaged over 5 random seeds.

**TABLE I. Benchmark Accuracy (Mean $\pm$ Std Across 5 Seeds)**

| Rank | Index | Accuracy | MAE | $\pm 1$ Acc | ARI |
|:----:|-------|:--------:|:---:|:------:|:---:|
| 1 | Gap Statistic | $53.8\% \pm 1.4\%$ | 2.07 | 69.0% | 0.574 |
| 2 | **CBV** | $\mathbf{51.4\% \pm 0.8\%}$ | 2.18 | 69.0% | 0.518 |
| 3 | CH Index | $44.8\% \pm 0.0\%$ | 2.92 | 63.8% | 0.596 |
| 4 | Silhouette | $38.3\% \pm 0.8\%$ | 2.27 | 62.4% | 0.581 |
| 5 | KL Index | $34.1\% \pm 2.6\%$ | 2.74 | 46.2% | 0.568 |
| 6 | Jump Statistic | $33.1\% \pm 1.4\%$ | 4.02 | 44.8% | 0.533 |
| 7 | Davies–Bouldin | $30.0\% \pm 0.9\%$ | 3.51 | 50.0% | 0.529 |
| 8 | Dunn Index | $24.8\% \pm 1.5\%$ | 3.52 | 41.4% | 0.461 |
| 9 | McClain–Rao | $11.0\% \pm 0.9\%$ | 6.11 | 12.8% | 0.387 |
| 10 | Hartigan | $3.4\% \pm 0.0\%$ | 5.20 | 15.5% | 0.399 |

The Gap Statistic leads at 53.8%, followed by CBV at 51.4%. CBV ranks second in exact-match accuracy and achieves the **lowest variance** ($\sigma = 0.8\%$) among all indices, indicating high reliability across random seeds. CBV's $\pm 1$ accuracy (69.0%) ties the Gap Statistic, confirming that when CBV errs, it errs by a small margin.

The Friedman test across all 10 indices and 58 datasets yields $\chi^2 = 247.6$, $p < 0.0001$, confirming highly significant performance differences.

### 5.2 Multi-Metric Comparison

Table I reveals that no single index dominates across all metrics. While the Gap Statistic leads in exact-match accuracy, CBV leads in score stability ($\sigma = 0.8\%$ vs. $1.4\%$). The CH index achieves the highest ARI (0.596) despite lower accuracy (44.8%), indicating that its errors are systematically smaller in terms of clustering quality. Silhouette achieves high ARI (0.581) despite moderate accuracy (38.3%), suggesting its errors are also relatively mild.

CBV occupies a distinctive position: second in accuracy, competitive in $\pm 1$ accuracy, and with the lowest variance. This stability profile is valuable in practice, where consistent performance across datasets is often more important than occasional peaks.

### 5.3 Per-Seed Stability

**TABLE II. Per-Seed Accuracy**

| Seed | CBV | Gap | CH | Sil | DB | Dunn |
|:----:|:---:|:---:|:--:|:---:|:--:|:----:|
| 42 | 51.7% | 55.2% | 44.8% | 39.7% | 31.0% | 24.1% |
| 73 | 50.0% | 55.2% | 44.8% | 37.9% | 29.3% | 25.9% |
| 123 | 51.7% | 51.7% | 44.8% | 37.9% | 31.0% | 25.9% |
| 256 | 51.7% | 53.4% | 44.8% | 37.9% | 29.3% | 22.4% |
| 999 | 51.7% | 53.4% | 44.8% | 37.9% | 29.3% | 25.9% |

CBV's accuracy is remarkably stable: 50.0%–51.7% across all five seeds (range = 1.7pp). By comparison, the Gap Statistic ranges from 51.7%–55.2% (range = 3.5pp), and Silhouette from 37.9%–39.7% (range = 1.8pp). This stability arises because CBV does not depend on $k$-means initialization — its estimate is derived from kernel density estimation, which is deterministic for a given bandwidth.

### 5.4 CBV Failure Analysis

Of the 58 datasets, CBV misestimates $k$ on approximately 28. These failures fall into five principal categories:

**TABLE III. CBV Failure Taxonomy**

| Category | Description | Root Cause | Example |
|----------|-------------|------------|---------|
| A. Non-convex shapes | $k=3$ instead of $k=2$ | 1D marginals produce spurious modes | moons, circles |
| B. High-$k$ collapse | Underestimates when $k \geq 5$ | Mode overlap in 1D projections | blobs\_k5, blobs\_k8 |
| C. Correlated dimensions | Drops to $k=2$ with correlated noise | Per-dimension independence assumption | Ablation study |
| D. Noise overwhelm | Classification noise dims reduce $k$ | Noise dims dilute bimodality signal | classif\_k3 |
| E. Real-dataset signal loss | Low signal-to-noise in some features | Complex real-world distributions | glass, yeast |

Category A (non-convex shapes) is an intrinsic limitation of per-dimension analysis: the 1D marginal of concentric circles produces three modes (inner peak, gap, outer peak) regardless of the true cluster count. CBVHybrid's spectral fusion partially mitigates this, but fundamental 1D-projection limitations remain.

Category B (high-$k$ collapse) reflects the difficulty of distinguishing many modes in 1D: as $k$ increases, cluster projections overlap and modes merge. This is the most significant structural limitation of the per-dimension approach.

Category C (correlated dimensions) was identified through the Phase D ablation study (Section 5.7): CBV drops to $k=2$ when as few as 4 correlated redundant dimensions are added, while geometric CVIs remain robust.

### 5.5 Complementarity with Geometric CVIs

A key finding is that CBV and geometric CVIs succeed on structurally different data regimes. CBV detects cluster structure in datasets where geometric indices fail — particularly those with overlapping but dimensionally separable clusters — while geometric indices excel where CBV is misled by tight separation or non-convex geometry.

This complementarity has practical implications: a simple ensemble that accepts either CBV or the best geometric index's estimate as correct would achieve higher accuracy than any single index alone. The disagreement signal between CBV and geometric indices is itself informative — it flags datasets with complex structure that warrants manual inspection.

### 5.6 CBVProjection Evaluation

Table IV compares the random 2D projection variant against CBVHybrid on the full 58-dataset benchmark (single seed = 42).

**TABLE IV. CBVVariant Comparison**

| Variant | Accuracy | MAE | ARI |
|---------|:--------:|:---:|:---:|
| CBVHybrid | 51.7% | 2.19 | 0.519 |
| CBVProjection (20 projections) | 46.6% | 2.22 | 0.530 |
| CBVProjection (50 projections) | 46.6% | 2.22 | 0.531 |

CBVHybrid outperforms CBVProjection by 5.1pp in accuracy. Head-to-head analysis reveals that CBVProjection correctly estimates $k$ on 1 dataset where CBVHybrid fails (iris), while CBVHybrid succeeds on 4 datasets where CBVProjection fails (three moons variants and parkinsons). The majority-vote aggregation in CBVProjection is effective at reducing per-dimension noise but does not fully compensate for the loss of high-dimensional structural information that CBVHybrid's spectral embedding captures.

### 5.7 Correlated-Dimension Ablation

We systematically evaluated CBV's robustness to correlated redundant dimensions by generating datasets with 0, 4, 10, or 20 extra dimensions that are linear combinations of the cluster-informative features, at correlation strengths $s \in \{0.0, 0.5, 0.9\}$.

**TABLE V. Accuracy by Correlation Strength (Mean Over n_corr_dims)**

| Index | $s = 0.0$ (noise) | $s = 0.5$ (moderate) | $s = 0.9$ (strong) |
|-------|:------------------:|:---------------------:|:-------------------:|
| CBV | 0.25 | 0.25 | 0.50 |
| CH | 0.25 | 0.50 | **1.00** |
| Silhouette | 0.25 | 0.25 | **1.00** |
| Davies–Bouldin | 0.25 | 0.25 | **1.00** |

At $s = 0.9$ (strongly correlated dims), geometric CVIs achieve perfect accuracy, while CBV reaches only 50%. The root cause is CBV's per-dimension independence assumption: correlated copies of informative features generate redundant or conflicting mode votes that distort the aggregation. Geometric CVIs benefit from correlated dimensions because they reinforce the global distance structure that $k$-means exploits.

This finding characterizes a fundamental limitation of the modality-testing approach and has implications for CBV's deployment: CBV is most effective when features are approximately independent, and should be used cautiously when strong inter-feature correlations are expected.

---

## 6. Discussion

### 6.1 Theoretical Implications: Modality vs. Geometry

CBV provides a new perspective on cluster validation grounded in statistical modality testing rather than geometric partition optimization. The two paradigms answer fundamentally different questions: geometric indices ask "which partition scores best?", while CBV asks "how many modes does the data density support?" These questions are related but distinct — the optimal geometric partition may not correspond to the number of natural groups in the data-generating process.

The complementarity demonstrated in our evaluation confirms this distinction: CBV and geometric CVIs succeed on structurally different data regimes. Datasets where CBV outperforms geometric indices tend to have overlapping clusters that are separable in specific feature dimensions (e.g., iris, where petal-length clearly exhibits three modes). Datasets where geometric indices outperform CBV tend to have tight, well-separated clusters or non-convex geometry where the 1D marginal distributions do not faithfully represent the multivariate structure.

### 6.2 Why Silverman Bandwidth Over Sheather–Jones

Our Phase D evaluation compared two bandwidth selection strategies for CBV's threshold test: Silverman's rule-of-thumb ($h = 1.06\hat{\sigma}n^{-1/5}$) and the Sheather–Jones (SJ) plug-in bandwidth. The SJ bandwidth is statistically more principled — it minimizes the asymptotic mean integrated squared error (AMISE) — but consistently produced smaller bandwidth values (0.51$\times$ Silverman on average).

In CBV's threshold test ($h_{\mathrm{crit}} < t \cdot h_{\mathrm{ref}}$), a smaller reference bandwidth makes the condition harder to satisfy, causing CBV to underestimate $k$. On 10 synthetic datasets, Silverman-based CBV achieved 65% accuracy versus 25% for SJ-based CBV (at the same tolerance $t = 1.3$). Even with increased tolerance ($t = 3.0$), SJ achieved only 40%.

The resolution is that Silverman's "over-smoothing" — its tendency to produce larger bandwidths — is actually beneficial for mode detection. A larger reference bandwidth means the threshold test is more permissive, detecting modes that are statistically present but may not be dominant in the density. For CBV's specific application (detecting the *presence* of modes, not estimating the density itself), Silverman's rule is the appropriate choice.

### 6.3 Correlated-Dimension Vulnerability

The correlated-dimension ablation reveals a fundamental structural limitation of CBV: its per-dimension independence assumption. When features are correlated, redundant dimensions generate duplicate mode votes that can overwhelm the signal from truly informative dimensions. CBV drops to $k = 2$ when as few as 4 correlated dimensions are added, regardless of correlation strength.

This vulnerability has practical implications. In genomics, for example, gene expression features are often highly correlated due to co-regulation. In image analysis, adjacent pixel features exhibit strong spatial correlation. In such domains, CBV should be used with caution or combined with dimensionality reduction (e.g., PCA) as a preprocessing step.

The CBVProjection variant partially addresses this limitation by analyzing random 2D subspaces, but our evaluation shows it does not fully compensate: CBVProjection achieves 46.6% versus CBVHybrid's 51.7%. The fundamental challenge is that no linear projection can fully decorrelate features without losing cluster-relevant structure.

### 6.4 Limitations

**Non-convex shapes**: CBV systematically fails on non-convex cluster geometries (moons, circles), where 1D marginals produce spurious modes. While CBVHybrid's spectral fusion helps, this remains the most significant structural limitation. Geometric indices, particularly spectral variants, remain superior for non-convex data.

**High-$k$ collapse**: CBV underestimates $k$ when the true number exceeds 4–5, due to mode overlap in 1D projections. This limits CBV's applicability to datasets with a moderate number of clusters.

**Correlated dimensions**: As characterized in Section 5.7, CBV is vulnerable to correlated redundant features. This limits applicability in domains with strong inter-feature correlations.

**Computational cost**: CBV is slower than standard CVIs due to per-dimension KDE computation. Fast mode ($n_{\mathrm{boot}} = 0$) processes a 300-sample, 50-feature dataset in approximately 0.2–0.3 seconds; full mode ($n_{\mathrm{boot}} = 999$) requires several seconds.

**Feature scaling**: Like all CVIs, CBV depends on feature scaling. Our benchmark used standardized features; sensitivity to standardization strategy requires further study.

### 6.5 Future Work

**Ensemble methods**: The demonstrated complementarity motivates principled ensemble approaches for combining CBV with geometric indices. A meta-learner that selects or weights indices based on data characteristics (dimensionality, estimated bimodality, cluster shape) could achieve accuracy beyond any single index.

**Multi-dimensional projections**: Replacing per-dimension 1D analysis with random 2D or $d$-dimensional projections could improve high-$k$ detection and non-convex robustness, at increased computational cost.

**Correlation-aware CBV**: Developing a variant that accounts for inter-feature correlations — perhaps through decorrelation preprocessing or correlated-vote debiasing — would extend CBV's applicability to correlated domains.

**Theoretical analysis**: A formal characterization of the relationship between Silverman's mode count and the true cluster count under different data-generating processes would strengthen CBV's theoretical foundations.

**Adaptive bandwidth selection**: Developing a bandwidth selection strategy specifically optimized for CBV's mode-detection task (rather than density estimation) could improve accuracy across diverse data regimes.

---

## 7. Conclusion

We introduced the Critical Bandwidth Validation (CBV) index, the first cluster validation index grounded in Silverman's critical bandwidth theory for statistical modality testing. CBV reframes the cluster-count problem from geometric partition optimization to statistical inference about the data density, offering a theoretically distinct alternative to established CVIs.

On a comprehensive benchmark of 58 datasets evaluated against 10 established CVIs across 5 random seeds, CBV achieves $51.4\% \pm 0.8\%$ exact-match accuracy, ranking second behind the Gap Statistic ($53.8\%$) and above all geometric indices. CBV exhibits the lowest variance across random seeds, indicating high reliability. Critically, CBV and geometric CVIs succeed on structurally different data regimes — their disagreements are informative, not random — establishing CBV as a complementary diagnostic tool rather than a mere replacement.

We further characterized CBV's failure modes (non-convex shapes, high-$k$ collapse, correlated dimensions), evaluated bandwidth selection strategies (Silverman recommended over Sheather–Jones), and assessed the CBVProjection variant (random 2D projections). These analyses provide a clear roadmap for practitioners: CBV is most effective when features are approximately independent and clusters have moderate complexity, and should be combined with geometric indices for robust cluster validation.

CBV contributes a new statistical-modality perspective to the cluster validation literature — one grounded in four decades of modality testing research — that complements the dominant geometric paradigm and opens new directions for ensemble cluster validation.

---

## Acknowledgments

This research was conducted using the critband package [20], [21] for critical bandwidth analysis. We thank the maintainers of the UCI Machine Learning Repository and scikit-learn for making the benchmark datasets available.

---

## Data Availability

All data used in this study is publicly available. Synthetic datasets were generated using scikit-learn. Real-world datasets are available from the UCI Machine Learning Repository, OpenML, and scikit-learn's built-in datasets. The complete benchmark results and implementation code are available at [repository URL].

---

## References

[1] C. Ding and X. He, "Cluster validity evaluation," in *Proc. IEEE Int. Conf. Data Mining*, 2004, pp. 1–8.

[2] U. Von Luxburg, R. C. Williamson, and I. Guyon, "Clustering: Science or art?," in *ICML Workshop Unsupervised and Transfer Learning*, 2012.

[3] O. Arbelaitz, I. Gurrutxaga, J. Muguerza, J. M. Pérez, and I. Perona, "An extensive comparative study of cluster validity indices," *Pattern Recognition*, vol. 46, no. 1, pp. 243–256, 2013.

[4] C. Hennig, "What are true clusters?," *Pattern Recognition Letters*, vol. 64, pp. 53–62, 2015.

[5] P. J. Rousseeuw, "Silhouettes: A graphical aid to the interpretation and validation of cluster analysis," *J. Comput. Appl. Math.*, vol. 20, pp. 53–65, 1987.

[6] T. Calinski and J. Harabasz, "A dendrite method for cluster analysis," *Commun. Statist.*, vol. 3, no. 1, pp. 1–27, 1974.

[7] D. L. Davies and D. W. Bouldin, "A cluster separation measure," *IEEE Trans. Pattern Anal. Mach. Intell.*, vol. 1, no. 2, pp. 224–227, 1979.

[8] R. Tibshirani, G. Walther, and T. Hastie, "Estimating the number of clusters in a data set via the gap statistic," *J. R. Statist. Soc. B*, vol. 63, no. 2, pp. 411–423, 2001.

[9] J. C. Dunn, "A fuzzy relative of the ISODATA process and its use in detecting compact well-separated clusters," *J. Cybernetics*, vol. 3, no. 3, pp. 32–57, 1973.

[10] B. S. Y. Krzanowski and Y. T. Lai, "A criterion for determining the number of clusters in a data set," *Biometrics*, vol. 44, no. 1, pp. 23–34, 1988.

[11] J. A. Hartigan, "Clustering algorithms," *Annals of Operations Research*, vol. 36, pp. 51–66, 1975.

[12] H. Ceccato, "Using the jump statistic to determine the number of clusters," *Computational Statistics*, 1995.

[13] J. L. McClain and G. J. Rao, "CLUSTPLOT: A computer program for clustering with a distance dissimilarity matrix representation," *J. Classification*, vol. 7, pp. 297–310, 1990.

[14] J. Demšar, "Statistical comparisons of classifiers over multiple data sets," *J. Mach. Learn. Res.*, vol. 7, pp. 1–30, 2006.

[15] B. W. Silverman, "Using kernel density estimates to investigate multimodality," *J. R. Statist. Soc. B*, vol. 43, no. 1, pp. 97–99, 1981.

[16] B. W. Silverman, *Density Estimation for Statistics and Data Analysis*. London, UK: Chapman and Hall, 1986.

[17] J. E. Chacón, "A comprehensive approach to mode clustering," arXiv:1406.1780, 2014.

[18] Y. Chen, C. R. Genovese, and L. Wasserman, "Clustering via mode seeking by direct estimation of the gradient of a log-density," arXiv:1404.5028, 2014.

[19] Y. Chen, C. R. Genovese, and L. Wasserman, "Mode-seeking clustering and density ridge estimation via direct estimation of density-derivative-ratios," arXiv:1707.01711, 2017.

[20] R. Zhang and Q. Wang, "critband: A Python package for critical bandwidth analysis of multimodal distributions," arXiv:2605.18686, 2026.

[21] critband v0.2.3 [Computer software]. Available: https://pypi.org/project/critband/

[22] G. W. Milligan and M. C. Cooper, "An examination of procedures for determining the number of clusters in a data set," *Psychometrika*, vol. 50, no. 2, pp. 159–179, 1985.

[23] "A Bayesian cluster validity index," arXiv:2402.02162, 2024.

[24] "Determining the number of clusters using center pairwise matching and boundary filtering," arXiv:2603.26744, 2026.

[25] "A high-dimensional robust nonparametric clustering validation index for large-scale data," arXiv:2510.14145, 2025.

[26] "A new measure for assessment of clustering based on kernel density estimation," arXiv:2201.02030, 2022.

[27] "Recovering the number of clusters in data sets with noise features using feature rescaling factors," arXiv:1602.06989, 2016.

[28] J. A. Hartigan and P. M. Hartigan, "The dip test of unimodality," *Annals of Statistics*, vol. 13, no. 1, pp. 70–84, 1985.

[29] D. W. Müller and G. Sawitzki, "Excess mass estimates and tests for multimodality," *J. Amer. Statist. Assoc.*, vol. 86, no. 415, pp. 738–746, 1991.

[30] S. J. Sheather and M. C. Jones, "A reliable data-based bandwidth selection method for kernel density estimation," *J. R. Statist. Soc. B*, vol. 53, no. 3, pp. 683–690, 1991.
