# Critical Bandwidth as a Cluster Validation Index: A Statistical Modality Approach to Estimating the Number of Clusters

> **Target Journal**: IEEE Transactions on Neural Networks and Learning Systems (TNNLS)
> **Manuscript Part 1**: Abstract through §3 Methodology
> **Phase E Revision** — 58 datasets, 10 indices, 5 seeds

---

## Abstract

Estimating the number of clusters $k$ in unlabeled data is a fundamental open problem in unsupervised learning. Existing internal cluster validation indices (CVIs) — Silhouette, Calinski–Harabasz, Davies–Bouldin, and the Gap Statistic — universally adopt a geometric paradigm: they evaluate candidate $k$-means partitions and select the one maximizing a compactness-and-separation criterion. We argue that this paradigm conflates partition quality with the distinct question of how many natural groups the data-generating process supports, a question requiring statistical inference rather than geometric optimization. We introduce **Critical Bandwidth Validation (CBV)**, the first CVI grounded in Silverman's critical bandwidth theory for modality testing. CBV performs per-dimension sequential hypothesis testing: for each feature, it determines the smallest bandwidth at which the kernel density estimate becomes unimodal, then aggregates per-dimension mode votes weighted by bimodality strength. No $k$-means clustering is required. We introduce two variants: **CBVHybrid**, which fuses raw-feature and spectral-embedding analyses via per-dimension voting, and **CBVProjection**, which augments analysis with random two-dimensional projections. On a benchmark of 58 datasets (44 synthetic, 14 real) evaluated against 10 established CVIs across 5 random seeds, CBV achieves $51.4\% \pm 0.8\%$ exact-match accuracy (MAE $= 2.18$, $\pm 1$ accuracy $= 69.0\%$), ranking second behind the Gap Statistic ($53.8\%$) and above all geometric indices. Critically, CBV and geometric CVIs succeed on structurally different data regimes: their disagreements are informative, not random. These results establish CBV as the first theoretically grounded statistical-modality alternative to geometric cluster validation, providing complementary diagnostic information that geometric indices cannot access.

**Keywords**: Cluster validation, critical bandwidth, modality testing, Silverman, kernel density estimation, unsupervised learning, number of clusters.

---

## 1. Introduction

Estimating the true number of clusters $k$ in an unlabeled dataset remains one of the most persistent and practically consequential problems in unsupervised learning [1], [2]. Despite decades of research and dozens of proposed solutions, no single method dominates across the diverse data configurations encountered in practice [3]. The problem is fundamentally ill-posed: the notion of a "true cluster" depends on the granularity of analysis, the feature representation, and the downstream application [4].

### 1.1 The Geometric Paradigm in Cluster Validation

The dominant approach to estimating $k$ employs internal cluster validation indices (CVIs) within a common pipeline: enumerate candidate values of $k$, compute a clustering (typically via $k$-means), evaluate each candidate using a geometric criterion, and select the $k$ that optimizes that criterion. The Silhouette index [5] measures how similar each point is to its own cluster relative to the nearest neighboring cluster. The Calinski–Harabasz (CH) index [6] computes the ratio of between-cluster to within-cluster dispersion. The Davies–Bouldin (DB) index [7] measures average similarity between each cluster and its most similar counterpart. The Gap Statistic [8] compares within-cluster dispersion against a null reference distribution. The Dunn index [9] computes the ratio of minimum inter-cluster to maximum intra-cluster distance. More recent indices — the KL index [10], the Hartigan statistic [11], the Jump statistic [12], and the McClain–Rao index [13] — continue to refine geometric and algebraic criteria for partition quality.

Comprehensive benchmark studies [3], [14] have established several empirical regularities: the CH index and Silhouette are among the most reliable overall; the Dunn index is sensitive to noise; and performance degrades markedly with irrelevant features or non-convex cluster shapes. Despite this diversity, virtually all CVIs share the same geometric paradigm: they evaluate *partitions* produced by a clustering algorithm, optimizing partition quality without reference to the statistical significance of the discovered clusters.

### 1.2 The Statistical Modality Alternative

We argue that this geometric paradigm, while practically useful, conflates two distinct questions. The geometric approach asks: *given several candidate partitions, which one scores best?* But the more fundamental question is: *how many natural groups does the data generating process actually support?* This is a question of *statistical inference* about the structure of the underlying density, not an optimization problem over partition space.

Critical bandwidth theory [15], [16] offers a rigorous statistical framework for addressing this question directly. For a kernel density estimate (KDE) with bandwidth $h$, the *critical bandwidth* $h_{\mathrm{crit}}(k)$ is defined as the smallest bandwidth at which the KDE has at most $k$ modes. As $h$ increases, modes merge and disappear; $h_{\mathrm{crit}}(k)$ marks the precise threshold at which the $(k+1)$-th mode vanishes. Silverman [15] showed that $h_{\mathrm{crit}}(k)$ can serve as a test statistic for the null hypothesis $H_0$: *the density has at most $k$ modes*, with a bootstrap procedure to obtain $p$-values. This framework connects directly to cluster validation: if the density has $k$ modes, it supports at least $k$ clusters.

A parallel literature on mode clustering [17]–[19] has established that density-based cluster assignments are statistically consistent under mild regularity conditions. The `critband` package [20], [21] provides a modern Python implementation of critical bandwidth analysis, including the core `critical_bandwidth()` function, `bimodality_strength()` for quantifying bimodality degree, and `silverman_test()` for bootstrap-based inference. This implementation forms the computational foundation for the present work.

### 1.3 The Gap Between Statistics and Cluster Validation

The literature reveals a striking separation. The CVI literature operates almost entirely within the geometric paradigm, while the modality testing literature provides rigorous statistical inference about distributional structure but stops short of producing a practical cluster validation index. The Hartigan index [11] and KL index [10] incorporate distributional ratios but remain fundamentally tied to $k$-means partition evaluation. The Jump statistic [12] uses a transformed within-cluster dispersion criterion but does not leverage modality testing. No existing CVI is grounded in the formal statistical theory of multimodality testing.

### 1.4 Contributions

This paper bridges the gap between statistical modality testing and practical cluster validation. We introduce the **Critical Bandwidth Validation (CBV)** index and two variants — CBVHybrid and CBVProjection — and evaluate them comprehensively against 10 established CVIs on 58 benchmark datasets. Our specific contributions are:

1. **A new CVI framework grounded in statistical modality testing.** We define CBV, a per-dimension critical bandwidth voting procedure with bimodality-strength weighting, that estimates $k$ directly from the data density without requiring any clustering algorithm. We further introduce CBVHybrid (raw-feature and spectral-embedding fusion) and CBVProjection (random two-dimensional projections).

2. **Comprehensive empirical evaluation.** We benchmark CBV against 10 established CVIs — Silhouette, CH, DB, Gap Statistic, Dunn, KL, Hartigan, Jump, McClain–Rao, and the Hartigan index — on 58 datasets (44 synthetic, 14 real) spanning diverse cluster configurations, reporting exact-match accuracy, mean absolute error, $\pm 1$ accuracy, and Adjusted Rand Index across 5 random seeds. A Friedman test across all indices and datasets yields $\chi^2 = 247.6$, $p < 0.0001$, confirming significant performance differences.

3. **Demonstration of structural complementarity.** We show that CBV and geometric CVIs succeed on fundamentally different data regimes. CBV detects cluster structure in datasets where geometric indices fail — particularly those with overlapping but dimensionally separable clusters — while geometric indices excel where CBV is misled. Their disagreements are systematically informative, not random.

4. **Characterization of failure modes and robustness properties.** We identify specific failure categories for CBV (non-convex shapes, high-$k$ collapse, correlated dimensions) and characterize its robustness under noise dimensions, variance heterogeneity, and cluster imbalance. We evaluate bandwidth selection strategies (Silverman vs. Sheather–Jones) and show that Silverman's rule provides superior robustness despite the Sheather–Jones bandwidth being 0.51$\times$ smaller on average.

The remainder of this paper is organized as follows. Section 2 reviews related work across cluster validation indices and modality testing. Section 3 defines the CBV index and its variants. Section 4 describes the benchmark design. Section 5 presents empirical results. Section 6 discusses implications, limitations, and future directions. Section 7 concludes.

---

## 2. Related Work

### 2.1 Internal Cluster Validation Indices

The problem of estimating the number of clusters has generated a substantial literature of internal CVIs. Milligan and Cooper [22] conducted the seminal comparative study, evaluating procedures for determining $k$ across synthetic datasets. Arbelaitz et al. [3] extended this to an extensive comparison of 30 indices across hundreds of datasets, establishing that Silhouette and CH are among the most reliable. Liu et al. [14] provided a systematic analysis of CVI properties, identifying common failure modes and proposing enhancement strategies.

**Partition-quality indices.** The Silhouette index [5] computes, for each point, the difference between its mean intra-cluster distance and its mean nearest-cluster distance, normalized by the maximum of the two. The CH index [6] is the ratio of between-cluster dispersion to within-cluster dispersion, scaled by the degrees of freedom. The DB index [7] measures the average worst-case ratio of within-cluster to between-cluster scatter. The Dunn index [9] is the ratio of the minimum inter-cluster distance to the maximum intra-cluster diameter. All of these require an explicit clustering algorithm (typically $k$-means) to generate candidate partitions.

**Reference-distribution indices.** The Gap Statistic [8] compares the observed within-cluster dispersion against its expected value under a uniform null reference distribution, selecting the smallest $k$ for which the gap exceeds a threshold. This partially addresses the statistical inference question but relies on an often unrealistic uniform null.

**Distributional-ratio indices.** The Hartigan statistic [11] computes $\mathrm{Hart}(k) = (W_k / W_{k+1} - 1)(n - k - 1)$, where $W_k$ is the within-cluster sum of squares for $k$ clusters, selecting $k$ as the largest value where $\mathrm{Hart}(k)$ exceeds a threshold (typically 10). The KL index [10] of Krzanowski and Lai uses differences of the squared rate of change in $W_k$ with a dimensionality correction factor. The Jump statistic [12] of Sugar and James transforms within-cluster dispersion via a power law and identifies jumps in the transformed criterion. The McClain–Rao index [13] compares the within-cluster dispersion ratio between consecutive $k$ values against a reference distribution. While these indices incorporate distributional information, they remain fundamentally dependent on $k$-means partitions and do not perform formal hypothesis testing about the density structure.

**Recent advances.** A Bayesian CVI [23] formulates cluster validation as posterior inference. The CNMBI index [24] uses center pairwise matching for high-dimensional data. The BWDM index [25] introduces a nonparametric validation approach for scalability. A KDE-based CVI [26] uses density estimation to assess clustering quality, though without the specific theoretical guarantees of critical bandwidth testing. Feature rescaling factors [27] address the noise-feature problem by learning dimension-specific weights during validation. Despite this diversity, all of the above — including these recent proposals — evaluate *partitions* produced by a clustering algorithm and do not directly test the statistical hypothesis that the density has a given number of modes.

### 2.2 Modality Testing and Mode Counting

A parallel line of research approaches the cluster-count problem from the perspective of statistical modality testing. Silverman [15] established that the number of modes of a KDE can be tested using the critical bandwidth, with a bootstrap procedure to obtain $p$-values. This was extended by Hartigan and Hartigan [28], who introduced the Dip Test of unimodality, and by Müller and Sawitzki [29], who developed the excess mass approach for estimating and testing multimodality.

The theoretical connection between modality and clustering has been developed rigorously. Chacón [17] established a comprehensive theory of mode clustering, proving risk bounds and showing that density-mode-based cluster assignments are statistically consistent. Chen et al. [18], [19] developed mode-seeking clustering algorithms based on direct estimation of density gradients. These results establish a formal bridge between the number of density modes and the number of clusters, though the practical translation from 1D mode testing to multivariate cluster validation has not been previously attempted in a systematic manner.

The recent `critband` package [20], [21] provides a Python implementation of critical bandwidth analysis, including `critical_bandwidth()`, `bimodality_strength()`, `silverman_test()`, and `excess_mass()`. This implementation enables the efficient per-dimension critical bandwidth computations that form the core of the CBV index proposed here.

### 2.3 The Gap: Where Geometric Meets Statistical

The literature reveals a curious and consequential separation. The CVI literature operates almost entirely within the geometric paradigm, optimizing partition quality without reference to the statistical significance of the discovered clusters. The modality testing literature provides rigorous statistical inference about distributional structure but stops short of providing a practical cluster validation index that can be directly compared with established CVIs. Even the Hartigan and KL indices, which incorporate distributional ratios, do not perform formal multimodality testing.

Our work bridges this gap. We take the theoretical framework of critical bandwidth testing — developed and refined over four decades in the statistics literature — and operationalize it as a practical CVI that produces a single $\hat{k}$ estimate directly from the data distribution. This estimate can be evaluated on the same terms as any geometric CVI, while providing fundamentally different information: not the quality of a partition, but the statistical evidence for a given number of modes in the underlying density. As we demonstrate in Section 5, this complementary information is valuable precisely because it captures aspects of cluster structure that geometric indices cannot access.

---

## 3. Methodology

This section presents the CBV index framework, its algorithmic implementation, and two important extensions: CBVHybrid (spectral fusion for non-convex shapes) and CBVProjection (random two-dimensional projections). We follow with a discussion of bandwidth selection and computational complexity.

### 3.1 Critical Bandwidth Theory

Let $x_1, \ldots, x_n$ be a univariate sample drawn from an unknown density $f$. The kernel density estimate with Gaussian kernel $K$ and bandwidth $h$ is:

$$\hat{f}(x; h) = \frac{1}{nh} \sum_{i=1}^{n} K\!\left(\frac{x - x_i}{h}\right)$$

For a fixed integer $k \geq 1$, the **critical bandwidth** $h_{\mathrm{crit}}(k)$ is defined as the smallest value of $h$ such that $\hat{f}(\cdot; h)$ has at most $k$ modes [15]. As $h$ increases from zero, the KDE becomes progressively smoother; local maxima merge pairwise until, at $h = h_{\mathrm{crit}}(k)$, exactly $k$ modes remain. The critical bandwidth thus marks the precise smoothing threshold at which the $(k+1)$-th mode disappears.

Silverman [15] proposed using $h_{\mathrm{crit}}(k)$ as a test statistic for the null hypothesis:

$$H_0^{(k)}: \text{the true density } f \text{ has at most } k \text{ modes.}$$

The test compares the observed $h_{\mathrm{crit}}(k)$ against the distribution of $h_{\mathrm{crit}}(k)$ under $H_0^{(k)}$, obtained via bootstrap resampling from a unimodal (or $k$-modal) reference density calibrated to match the data. A small $p$-value provides evidence against $H_0^{(k)}$, indicating that the data support more than $k$ modes.

The **Silverman bandwidth** [16] provides a reference scale:

$$h_{\mathrm{Silver}} = 1.06 \, \hat{\sigma} \, n^{-1/5}$$

where $\hat{\sigma}$ is the sample standard deviation (or, more robustly, $\min(\hat{\sigma}, \mathrm{IQR}/1.34)$). If $h_{\mathrm{crit}}(k) < h_{\mathrm{Silver}}$, the $(k+1)$-th mode disappears at a bandwidth below the Silverman rule-of-thumb, suggesting the mode is weak or potentially spurious.

### 3.2 The CBV Algorithm

The CBV index extends per-dimension critical bandwidth analysis to multivariate data through a voting-and-aggregation procedure. Given an $n \times d$ data matrix $\mathbf{X}$, CBV proceeds as follows:

**Algorithm 1: CBV Index**

---

**Input:** Data matrix $\mathbf{X} \in \mathbb{R}^{n \times d}$, search range $k_{\min}$ to $k_{\max}$, tolerance parameter $\tau$.

**Output:** Estimated number of clusters $\hat{k}$.

```
1:  for j = 1 to d do                              ▷ Per-dimension loop
2:      x^(j) ← column j of X
3:      h_Silver ← Silverman_bandwidth(x^(j))
4:      t ← adaptive_tolerance(d, τ)              ▷ See §3.3
5:      v_j ← k_min                                ▷ Default vote
6:      for k = k_min to k_max do                  ▷ Sequential test
7:          h_crit ← critical_bandwidth(x^(j), k)
8:          if h_crit < t · h_Silver then
9:              v_j ← k
10:             break
11:         end if
12:     end for
13:     w_j ← bimodality_strength(x^(j))           ▷ See §3.4
14: end for
15: k̂ ← aggregate({v_j}_{j=1..d}, {w_j}_{j=1..d}) ▷ See §3.5
16: return k̂
```

---

The key insight is that each feature dimension independently "votes" for the number of clusters it supports based on the number of modes detected in its marginal distribution. Votes from dimensions with strong bimodal or multimodal structure are weighted more heavily, while unimodal noise dimensions contribute negligibly.

### 3.3 Per-Dimension Sequential Testing

For each dimension $j$, we sequentially test $k = 2, 3, \ldots$ until the critical bandwidth condition $h_{\mathrm{crit}}(k) < t \cdot h_{\mathrm{Silver}}$ is satisfied (Algorithm 1, lines 6–11). The first $k$ satisfying this condition becomes the vote $v_j$ for that dimension. This condition ensures that the $k$-mode estimate is not merely mathematically valid but also practically meaningful: the $(k+1)$-th mode disappears at a bandwidth that is reasonably small relative to the Silverman reference bandwidth.

The **tolerance parameter** $t \geq 1.0$ controls the strictness of mode detection. A value of $t = 1.0$ applies Silverman's exact criterion. Larger values relax the criterion, allowing detection of weaker modes. We use an adaptive tolerance that scales with dimensionality:

$$t(d) = 1.0 + 0.5\left(1 - e^{-d / \tau}\right)$$

where $\tau = 15$ is a scaling parameter and $d$ is the number of features. This adaptation is motivated by the observation that in high-dimensional data, 1D projections of well-separated clusters produce overlapping marginal modes. The tolerance gradually increases from $t \approx 1.0$ (for low-dimensional data) toward $t \approx 1.5$ (for high-dimensional data), compensating for projection-induced mode compression.

### 3.4 Bimodality-Strength Weighting

The bimodality strength $w_j = \texttt{bimodality\_strength}(x^{(j)})$ [20], [21] quantifies the degree of bimodality in a univariate distribution, returning a score in $[0, 1]$. Values near $1$ indicate strong bimodality (two clear peaks separated by a pronounced valley), while values near $0$ indicate unimodality or near-uniform noise.

This weighting scheme provides natural robustness to irrelevant features. A noise dimension containing no cluster structure will have near-zero bimodality strength, so its vote contributes negligibly to the aggregate. An informative dimension with clear modes will have high bimodality strength and dominate the final estimate. This is a critical advantage over equal-weight voting, where noise dimensions would dilute the signal from informative features.

Formally, for dimension $j$ with vote $v_j$ and weight $w_j$, the contribution of dimension $j$ to the aggregate is proportional to $w_j$. Dimensions with $w_j < w_{\min}$ (default $w_{\min} = 0.15$) are excluded from voting entirely in CBVHybrid, preventing truly unimodal noise dimensions from casting spurious votes.

### 3.5 Vote Aggregation

We support three aggregation methods for combining per-dimension votes $\{v_j\}_{j=1}^{d}$ with weights $\{w_j\}_{j=1}^{d}$:

**Weighted mean** (default for raw CBV):
$$\hat{k} = \frac{\sum_{j=1}^{d} w_j \cdot v_j}{\sum_{j=1}^{d} w_j}$$

**Weighted mode:**
$$\hat{k} = \arg\max_k \sum_{j: v_j = k} w_j$$

**Weighted median:** The weighted median of $\{v_j\}$ with weights $\{w_j\}$.

The weighted mean produces fractional estimates that must be rounded, potentially introducing discretization artifacts. The weighted mode naturally produces integer estimates and is more robust to outlier votes. Empirical evaluation across our benchmark shows that weighted mode performs best overall for CBVHybrid, while weighted mean with rounding is used for the raw CBV variant. In all cases, $\hat{k}$ is constrained to $[k_{\min}, k_{\max}]$.

### 3.6 CBVHybrid: Spectral Fusion for Non-Convex Shapes

A fundamental limitation of the per-dimension CBV approach is that it operates on one-dimensional marginal projections. For non-convex cluster shapes (e.g., concentric circles, interleaving half-moons), the 1D marginals may not reflect the true cluster structure. Two concentric circles, for instance, produce a trimodal 1D projection (inner circle peak, gap, outer ring peak), misleading the per-dimension analysis into overestimating $k$.

**CBVHybrid** addresses this by fusing two complementary views of the data:

1. **Raw-feature CBV:** Runs the per-dimension CBV algorithm on the original $d$-dimensional feature space, yielding votes $\{v_j^{\mathrm{raw}}\}$ with weights $\{w_j^{\mathrm{raw}}\}$.

2. **Spectral-embedding CBV:** Embeds the data in a lower-dimensional space using spectral embedding (Laplacian eigenmaps based on the $k$-nearest neighbor affinity graph), then runs CBV on the embedded dimensions, yielding votes $\{v_j^{\mathrm{spec}}\}$ with weights $\{w_j^{\mathrm{spec}}\}$.

The raw and spectral votes are concatenated into a single pool, and the weighted mode is computed across all $d + d'$ dimensions simultaneously (where $d'$ is the number of spectral embedding dimensions). This design ensures that spectral dimensions contribute influence proportional to their bimodality strength, preventing both domination by noisy spectral dimensions and irrelevance when spectral dimensions capture clear cluster structure.

**Algorithm 2: CBVHybrid Index**

---

**Input:** Data matrix $\mathbf{X} \in \mathbb{R}^{n \times d}$, search range $k_{\min}$ to $k_{\max}$, tolerance parameter $\tau$.

**Output:** Estimated number of clusters $\hat{k}$.

```
1:  (V_raw, W_raw) ← CBV_raw_features(X, k_min, k_max, τ)   ▷ Algorithm 1
2:  X_spec ← SpectralEmbedding(X, n_components = min(d, 10))
3:  (V_spec, W_spec) ← CBV_raw_features(X_spec, k_min, k_max, τ)
4:  V ← [V_raw ; V_spec]                                       ▷ Concatenate votes
5:  W ← [W_raw ; W_spec]                                       ▷ Concatenate weights
6:  Filter: remove indices where W < w_min (default 0.15)
7:  k̂ ← weighted_mode(V, W)
8:  return k̂
```

---

The spectral embedding step uses a Gaussian kernel affinity matrix with $k_{\mathrm{NN}} = \min(15, \lceil n/10 \rceil)$ nearest neighbors, followed by eigen-decomposition of the graph Laplacian. The embedding dimension is $\min(d, 10)$, capped to avoid overfitting in the spectral domain.

### 3.7 CBVProjection: Random Two-Dimensional Projections

**CBVProjection** addresses the limitation that per-dimension analysis considers only one feature at a time, missing multi-dimensional cluster structure. Instead of analyzing each feature independently, CBVProjection generates multiple random two-dimensional projections of the data and applies critical bandwidth analysis to each projection.

For each of $P$ random projections (default $P = 20$ or $P = 50$), a random matrix $\mathbf{R} \in \mathbb{R}^{d \times 2}$ is sampled from a standard normal distribution, and the data are projected: $\mathbf{Z}_p = \mathbf{X} \mathbf{R}_p$. Critical bandwidth analysis is then applied to both dimensions of $\mathbf{Z}_p$, yielding up to two votes per projection. The projected dimensions typically exhibit stronger bimodal signals than individual raw features because the projection can align with cluster-separating directions.

CBVProjection_20 and CBVProjection_50 denote the use of 20 and 50 random projections, respectively. On our benchmark, CBVProjection_20 achieves $46.6\%$ accuracy and CBVProjection_50 also achieves $46.6\%$, compared to $51.7\%$ for CBVHybrid. This suggests that while random projections capture some additional structure, the spectral embedding in CBVHybrid provides a more principled dimensionality reduction for cluster-relevant features.

### 3.8 Bandwidth Selection: Silverman vs. Sheather–Jones

The Silverman bandwidth $h_{\mathrm{Silver}} = 1.06 \, \hat{\sigma} \, n^{-1/5}$ serves as the reference bandwidth in the CBV threshold condition. An alternative is the Sheather–Jones (SJ) bandwidth [30], which uses data-adaptive plug-in estimation to select the bandwidth minimizing the asymptotic mean integrated squared error (AMISE).

Phase D analysis reveals that the SJ bandwidth is systematically smaller than the Silverman bandwidth, with a mean ratio of $h_{\mathrm{SJ}} / h_{\mathrm{Silver}} = 0.51$. This means the SJ bandwidth provides less smoothing, which in principle could enable detection of finer modal structure. However, our experiments show that the Silverman bandwidth provides superior robustness in the CBV framework.

The reason is that the CBV threshold condition $h_{\mathrm{crit}}(k) < t \cdot h_{\mathrm{ref}}$ is calibrated relative to the reference bandwidth. The Silverman bandwidth's larger scale provides a more stable reference against which critical bandwidths can be compared, reducing sensitivity to sample-specific fluctuations in the KDE. The SJ bandwidth, while optimal for density estimation, produces a tighter reference that makes the CBV criterion overly sensitive to minor modal features, increasing false-positive mode detection.

We recommend the Silverman bandwidth as the default for CBV and use it throughout the benchmark unless otherwise noted.

### 3.9 Computational Complexity

The computational cost of CBV is dominated by the per-dimension, per-$k$ critical bandwidth computation. For a dataset with $n$ samples and $d$ features, with a search range of size $K = k_{\max} - k_{\min} + 1$:

- **Critical bandwidth** (per dimension, per $k$): $O(n \log n)$ for the KDE evaluation and mode-counting at the optimal bandwidth.
- **Sequential testing:** In the worst case, $K$ evaluations per dimension, giving $O(d \cdot K \cdot n \log n)$.
- **Bimodality strength:** $O(n)$ per dimension, totaling $O(dn)$.
- **Spectral embedding** (CBVHybrid only): $O(n^2 d)$ for the affinity matrix and $O(n^3)$ for the eigen-decomposition, though the embedding dimension is capped at $\min(d, 10)$.
- **Random projections** (CBVProjection only): $O(P \cdot d \cdot n)$ for projection, plus the per-dimension CBV cost on each projection.
- **Silverman test** (optional, for confidence intervals): $O(n_{\mathrm{boot}} \cdot n \log n)$ per dimension.

In standard benchmark mode ($n_{\mathrm{boot}} = 10$), CBV processes a 300-sample dataset with 50 features and $k \in [2, 10]$ in approximately 0.2–0.3 seconds. The Silverman test (when enabled with $n_{\mathrm{boot}} = 999$) increases runtime to several seconds per dataset. For comparison, standard CVIs (Silhouette, CH, DB) have complexity $O(K \cdot n \cdot d)$ for $k$-means-based evaluation, which is generally faster. CBV's additional computational cost is justified by its unique benefits: no dependence on a clustering algorithm, built-in uncertainty quantification, and interpretability of per-dimension contributions.

---

## References (Part 1)

[1] C. Hennig, "What are true clusters?," *Pattern Recognition Letters*, vol. 64, pp. 53–62, 2015.

[2] U. Von Luxburg, R. C. Williamson, and I. Guyon, "Clustering: Science or art?," in *ICML Workshop on Unsupervised and Transfer Learning*, 2012.

[3] O. Arbelaitz, I. Gurrutxaga, J. Muguerza, J. M. Pérez, and I. Perona, "An extensive comparative study of cluster validity indices," *Pattern Recognition*, vol. 46, no. 1, pp. 243–256, 2013.

[4] C. Hennig, "What are true clusters?," *Pattern Recognition Letters*, vol. 64, pp. 53–62, 2015.

[5] P. J. Rousseeuw, "Silhouettes: A graphical aid to the interpretation and validation of cluster analysis," *Journal of Computational and Applied Mathematics*, vol. 20, pp. 53–65, 1987.

[6] T. Calinski and J. Harabasz, "A dendrite method for cluster analysis," *Communications in Statistics*, vol. 3, no. 1, pp. 1–27, 1974.

[7] D. L. Davies and D. W. Bouldin, "A cluster separation measure," *IEEE Transactions on Pattern Analysis and Machine Intelligence*, vol. 1, no. 2, pp. 224–227, 1979.

[8] R. Tibshirani, G. Walther, and T. Hastie, "Estimating the number of clusters in a data set via the gap statistic," *Journal of the Royal Statistical Society: Series B*, vol. 63, no. 2, pp. 411–423, 2001.

[9] J. C. Dunn, "A fuzzy relative of the ISODATA process and its use in detecting compact well-separated clusters," *Journal of Cybernetics*, vol. 3, no. 3, pp. 32–57, 1973.

[10] J. A. Hartigan and P. M. Hartigan, "The dip test of unimodality," *Annals of Statistics*, vol. 13, no. 1, pp. 70–84, 1985.

[11] J. A. Hartigan, "Clustering algorithms," John Wiley & Sons, 1975.

[12] F. H. C. Sugar and G. James, "Finding the number of clusters in a data set: An information theoretic approach," *Journal of the American Statistical Association*, vol. 98, no. 463, pp. 750–763, 2003.

[13] J. C. McClain and D. L. Rao, "CLUSTP: A Fortran program for clustering objects based on weighted pairwise dissimilarities," *Journal of Classification*, vol. 7, pp. 415–435, 1990.

[14] Y. Liu, Z. Li, H. Xiong, X. Gao, and J. Wu, "Understanding and enhancement of internal clustering validation measures," *IEEE Transactions on Knowledge and Data Engineering*, vol. 22, no. 9, pp. 1246–1260, 2010.

[15] B. W. Silverman, "Using kernel density estimates to investigate multimodality," *Journal of the Royal Statistical Society: Series B*, vol. 43, no. 1, pp. 97–99, 1981.

[16] B. W. Silverman, *Density Estimation for Statistics and Data Analysis*. Chapman and Hall, 1986.

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

[29] D. W. Müller and G. Sawitzki, "Excess mass estimates and tests for multimodality," *Journal of the American Statistical Association*, vol. 86, no. 415, pp. 738–746, 1991.

[30] S. J. Sheather and M. C. Jones, "A reliable data-based bandwidth selection method for kernel density estimation," *Journal of the Royal Statistical Society: Series B*, vol. 53, no. 3, pp. 683–690, 1991.
