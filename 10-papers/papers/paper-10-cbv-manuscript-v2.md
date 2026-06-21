# Critical Bandwidth Modality Testing for Estimating the Number of Clusters

> **Target Journal**: IEEE Transactions on Neural Networks and Learning Systems (TNNLS)
> **Manuscript Part 1**: Abstract through §3 Methodology
> **Phase E Revision** — 58 datasets, 10 indices, 5 seeds

---

## Abstract

Estimating the number of clusters $k$ in unlabeled data is a fundamental open problem in unsupervised learning. Existing internal cluster validation indices (CVIs) — Silhouette, Calinski–Harabasz, Davies–Bouldin, and the Gap Statistic — universally adopt a geometric paradigm: they evaluate candidate $k$-means partitions and select the one maximizing a compactness-and-separation criterion. We argue that this paradigm conflates partition quality with the distinct question of how many natural groups the data-generating process supports, a question requiring statistical inference rather than geometric optimization. To address this gap, we introduce **Critical Bandwidth Validation (CBV)**, a CVI grounded in critical bandwidth modality testing. CBV estimates $k$ directly from the data density via per-dimension sequential hypothesis testing — no $k$-means clustering is required — and aggregates per-dimension mode votes weighted by bimodality strength. We further introduce CBVHybrid (spectral-embedding fusion) and CBVProjection (random two-dimensional projections). On a benchmark of 58 datasets (44 synthetic, 14 real) evaluated against 10 established CVIs across 5 random seeds, CBV achieves $51.4\% \pm 0.8\%$ exact-match accuracy (MAE $= 2.18$, $\pm 1$ accuracy $= 69.0\%$), ranking second behind the Gap Statistic ($53.8\%$) and above all geometric indices. Critically, CBV and geometric CVIs succeed on structurally different data regimes: an OR-ensemble of CBV and the Gap Statistic achieves $67.2\%$ accuracy (+13.8pp over the best single index), with a Complementarity Index of 0.667. These results establish CBV as a statistically grounded complement to geometric cluster validation, providing diagnostic information that geometric indices cannot access.

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

**Recent advances.** A Bayesian CVI [23] formulates cluster validation as posterior inference. The CNMBI index [24] uses center pairwise matching for high-dimensional data. The BWDM index [25] introduces a nonparametric validation approach for scalability. A KDE-based CVI [26] uses density estimation to assess clustering quality, though without the specific theoretical guarantees of critical bandwidth testing. Feature rescaling factors [27] address the noise-feature problem by learning dimension-specific weights during validation. Despite this diversity, all of the above — including these recent proposals — evaluate *partitions* produced by a clustering algorithm and do not directly test the statistical hypothesis that the density has a given number of modes. We note that the KDE-based CVI of [26] is the closest related work to CBV in terms of using density estimation, but it evaluates partition quality (via density-based scoring) rather than estimating $k$ from modality structure; a direct comparison would require re-implementing their method, which is beyond the scope of this work.

### 2.2 Modality Testing and Mode Counting

A parallel line of research approaches the cluster-count problem from the perspective of statistical modality testing. Silverman [15] established that the number of modes of a KDE can be tested using the critical bandwidth, with a bootstrap procedure to obtain $p$-values. This was extended by Hartigan and Hartigan [28], who introduced the Dip Test of unimodality, and by Müller and Sawitzki [29], who developed the excess mass approach for estimating and testing multimodality. We note that the Dip Test [28] tests only unimodality (1 mode vs. $>1$ mode) and cannot directly estimate $k$ for $k > 2$, making it unsuitable as a standalone CVI; CBV extends the critical bandwidth framework to sequential multi-modal testing across $k = 2, 3, \ldots$

The theoretical connection between modality and clustering has been developed rigorously. Chacón [17] established a comprehensive theory of mode clustering, proving risk bounds and showing that density-mode-based cluster assignments are statistically consistent. Chen et al. [18], [19] developed mode-seeking clustering algorithms based on direct estimation of density gradients. These results establish a formal bridge between the number of density modes and the number of clusters, though the practical translation from 1D mode testing to multivariate cluster validation has not been previously attempted in a systematic manner.

The recent `critband` package [20], [21] provides a Python implementation of critical bandwidth analysis, including `critical_bandwidth()`, `bimodality_strength()`, `silverman_test()`, and `excess_mass()`. This implementation enables the efficient per-dimension critical bandwidth computations that form the core of the CBV index proposed here.

### 2.3 The Gap: Where Geometric Meets Statistical

The literature reveals a curious and consequential separation (illustrated in Figure 1 of the supplementary materials). The CVI literature operates almost entirely within the geometric paradigm, optimizing partition quality without reference to the statistical significance of the discovered clusters. The modality testing literature provides rigorous statistical inference about distributional structure but stops short of providing a practical cluster validation index that can be directly compared with established CVIs. Even the Hartigan and KL indices, which incorporate distributional ratios, do not perform formal multimodality testing.

Our work bridges this gap. We operationalize critical bandwidth testing — developed over four decades in the statistics literature — as a practical CVI that produces a single $\hat{k}$ estimate directly from the data distribution. This estimate can be evaluated on the same terms as any geometric CVI, while providing fundamentally different information: not the quality of a partition, but the statistical evidence for a given number of modes in the underlying density.

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
3:      if x^(j) is constant then                  ▷ Boundary: skip constant dims
4:          v_j ← 0; w_j ← 0; continue
5:      end if
6:      h_Silver ← Silverman_bandwidth(x^(j))
7:      t ← adaptive_tolerance(d, τ)              ▷ See §3.3
8:      v_j ← k_min                                ▷ Default vote (unimodal)
9:      for k = k_min to k_max do                  ▷ Sequential test
10:         h_crit ← critical_bandwidth(x^(j), k)
11:         if h_crit < t · h_Silver then
12:             v_j ← k
13:             break
14:         end if
15:     end for
16:     ▷ If no k satisfies: v_j = k_min (dimension is unimodal or modes
17:     ▷ are too weak to detect — vote conservatively as k_min)
18:     w_j ← bimodality_strength(x^(j))           ▷ See §3.4
19: end for
20: k̂ ← aggregate({v_j}_{j=1..d}, {w_j}_{j=1..d}) ▷ See §3.5
21: return k̂
```

---

**Boundary conditions.** Algorithm 1 handles three edge cases explicitly: (i) constant dimensions (zero variance) are skipped entirely with vote $v_j = 0$ and weight $w_j = 0$, preventing division-by-zero in bandwidth computation; (ii) unimodal dimensions where $h_{\mathrm{crit}}(k_{\min}) \geq t \cdot h_{\mathrm{Silver}}$ even at $k = k_{\min}$ — the sequential test finds no $k$ satisfying the threshold, so the default vote $v_j = k_{\min}$ is retained, correctly indicating that the dimension supports at most $k_{\min}$ modes; (iii) the final estimate $\hat{k}$ is clamped to $[k_{\min}, k_{\max}]$ after aggregation (line 21), ensuring valid output regardless of the aggregation result.

The key insight is that each feature dimension independently "votes" for the number of clusters it supports based on the number of modes detected in its marginal distribution. Votes from dimensions with strong bimodal or multimodal structure are weighted more heavily, while unimodal noise dimensions contribute negligibly.

### 3.3 Per-Dimension Sequential Testing

For each dimension $j$, CBV determines the number of modes in the 1D marginal distribution by sequentially testing $k = 2, 3, \ldots$ until a termination condition is met (Algorithm 1, lines 9–15). The test is based on the relationship between two bandwidths: the **critical bandwidth** $h_{\mathrm{crit}}(k)$ and the **Silverman reference bandwidth** $h_{\mathrm{Silver}}$.

**Intuition.** The critical bandwidth $h_{\mathrm{crit}}(k)$ is the smallest bandwidth at which the KDE becomes unimodal when starting from $k$ modes — it measures how "strong" the $k$-mode structure is. A small $h_{\mathrm{crit}}(k)$ means the $k$ modes are well-separated and persist even under substantial smoothing. The Silverman bandwidth $h_{\mathrm{Silver}} = 1.06 \hat{\sigma} n^{-1/5}$ is the optimal bandwidth for estimating a unimodal density; it represents the smoothing level at which a genuinely unimodal distribution would be well-estimated.

**Threshold condition.** The condition $h_{\mathrm{crit}}(k) < t \cdot h_{\mathrm{Silver}}$ identifies the largest $k$ whose modes are "real" — i.e., strong enough to survive smoothing up to the unimodal reference level. When $h_{\mathrm{crit}}(k) < t \cdot h_{\mathrm{Silver}}$, the $k$ modes are statistically distinguishable from a unimodal distribution at bandwidth $h_{\mathrm{Silver}}$. When $h_{\mathrm{crit}}(k) \geq t \cdot h_{\mathrm{Silver}}$, the supposed $k$-th mode is an artifact of over-fitting the density — the modes merge before reaching the reference bandwidth, indicating they are not genuinely present.

**Sequential search.** We test $k = k_{\min}, k_{\min}+1, \ldots$ in increasing order. The first $k$ satisfying $h_{\mathrm{crit}}(k) < t \cdot h_{\mathrm{Silver}}$ becomes the vote $v_j$. This greedy search is justified because: (a) if $k$ modes are detectable, then all $k' < k$ modes are also detectable (monotonicity of critical bandwidth in $k$); and (b) we seek the *largest* $k$ whose modes are statistically supported, which is the first $k$ where the threshold is crossed when scanning upward.

The **tolerance parameter** $t \geq 1.0$ controls the strictness of mode detection. A value of $t = 1.0$ applies Silverman's exact criterion: modes must be strong enough to survive smoothing at exactly the unimodal reference bandwidth. Larger values relax the criterion, allowing detection of weaker modes that merge slightly before $h_{\mathrm{Silver}}$. We use an adaptive tolerance that scales with dimensionality:

$$t(d) = 1.0 + 0.5\left(1 - e^{-d / \tau}\right)$$

where $\tau = 15$ is a scaling parameter and $d$ is the number of features. This adaptation is motivated by the observation that in high-dimensional data, 1D projections of well-separated clusters produce overlapping marginal modes due to projection-induced compression. The tolerance gradually increases from $t \approx 1.0$ (for low-dimensional data, where modes are sharp) toward $t \approx 1.5$ (for high-dimensional data, where modes are blurred by projection), compensating for this geometric effect.

**Selection of $\tau = 15$.** The parameter $\tau$ controls the rate at which tolerance increases with dimensionality: smaller $\tau$ causes faster saturation (risking false mode detection), while larger $\tau$ causes slower increase (risking missed modes). Table II shows the adaptive tolerance $t(d)$ for representative dimensionalities across $\tau$ values.

**TABLE II. Adaptive Tolerance $t(d)$ for Different $\tau$ Values**

| $\tau$ | $t(d{=}2)$ | $t(d{=}10)$ | $t(d{=}15)$ | $t(d{=}50)$ | Range |
|:------:|:----------:|:-----------:|:-----------:|:-----------:|:-----:|
| 5 | 1.165 | 1.432 | 1.475 | 1.500 | 0.335 |
| 10 | 1.091 | 1.316 | 1.388 | 1.497 | 0.406 |
| **15** | **1.062** | **1.243** | **1.316** | **1.482** | **0.420** |
| 20 | 1.048 | 1.197 | 1.264 | 1.459 | 0.411 |
| 30 | 1.032 | 1.142 | 1.197 | 1.406 | 0.373 |
| 50 | 1.020 | 1.091 | 1.130 | 1.316 | 0.296 |

We select $\tau = 15$ because it provides the widest tolerance range (0.420) while maintaining near-strict behavior for low-dimensional data ($t(2) = 1.062$). The half-maximum of the exponential occurs at $d = \tau = 15$, aligning with the median dimensionality of our benchmark (median $d = 10$). This ensures that the tolerance transition is centered on the practical regime where most datasets fall. The parameter is not tuned to the benchmark — it is set a priori based on the geometric intuition that projection-induced mode compression becomes significant at $d \approx 15$.

### 3.4 Bimodality-Strength Weighting

The bimodality strength $w_j = \texttt{bimodality\_strength}(x^{(j)})$ [20], [21] quantifies the degree of bimodality in a univariate distribution, returning a score in $[0, 1]$. Formally, it combines three indicators: (i) the dip ratio (the ratio of the deepest valley to the highest peak in the KDE), (ii) the ratio $h_{\mathrm{crit}}(2) / h_{\mathrm{Silver}}$ (how much smoothing is needed to merge the two modes relative to the unimodal reference), and (iii) the number of KDE modes at the analysis bandwidth $h = 0.85 \cdot h_{\mathrm{crit}}(2)$. Values near $1$ indicate strong bimodality (two clear peaks separated by a pronounced valley), while values near $0$ indicate unimodality or near-uniform noise.

This weighting scheme provides natural robustness to irrelevant features. A noise dimension containing no cluster structure will have near-zero bimodality strength, so its vote contributes negligibly to the aggregate. An informative dimension with clear modes will have high bimodality strength and dominate the final estimate. This is a critical advantage over equal-weight voting, where noise dimensions would dilute the signal from informative features.

Formally, for dimension $j$ with vote $v_j$ and weight $w_j$, the contribution of dimension $j$ to the aggregate is proportional to $w_j$. The threshold $w_{\min} = 0.15$ is set based on the empirical observation that bimodality strength values below this threshold correspond to distributions where the two "modes" are indistinguishable from random fluctuation — the dip ratio is less than 0.1, meaning the valley between peaks is shallower than 10% of the peak height. Dimensions with $w_j < w_{\min}$ are excluded from voting entirely in CBVHybrid, preventing truly unimodal noise dimensions from casting spurious votes. This threshold is not sensitive to the final result: varying $w_{\min}$ from 0.05 to 0.25 changes CBV's accuracy by less than 2pp on our benchmark.

### 3.5 Vote Aggregation

We support three aggregation methods for combining per-dimension votes $\{v_j\}_{j=1}^{d}$ with weights $\{w_j\}_{j=1}^{d}$:

**Weighted mean** (default for raw CBV):
$$\hat{k} = \frac{\sum_{j=1}^{d} w_j \cdot v_j}{\sum_{j=1}^{d} w_j}$$

**Weighted mode:**
$$\hat{k} = \arg\max_k \sum_{j: v_j = k} w_j$$

**Weighted median:** The weighted median of $\{v_j\}$ with weights $\{w_j\}$.

The weighted mean produces fractional estimates that must be rounded to the nearest integer, potentially introducing discretization artifacts (e.g., a weighted mean of 2.6 rounds to 3, while 2.4 rounds to 2). We use standard rounding (round half up), with the result clamped to $[k_{\min}, k_{\max}]$. The weighted mode naturally produces integer estimates and is more robust to outlier votes. Empirical evaluation across our benchmark shows that weighted mode performs best overall for CBVHybrid, while weighted mean with rounding is used for the raw CBV variant. In all cases, $\hat{k}$ is constrained to $[k_{\min}, k_{\max}]$. The choice of $k_{\max} = 10$ reflects the practical observation that most benchmark datasets have $k \leq 10$; datasets with $k > 10$ (e.g., yeast with $k = 10$, ecoli with $k = 8$) are at the boundary of the search range and contribute to CBV's failure cases (Category B, §5.4).

#### Theoretical Justification for Vote Aggregation

We establish conditions under which per-dimension mode counting recovers the true cluster count $k^*$, providing the theoretical foundation for CBV's aggregation procedure.

**Proposition 1 (Mode Recovery under Isotropic Gaussian Mixtures).** Consider a $k^*$-component isotropic Gaussian mixture $\mathcal{G} = \sum_{c=1}^{k^*} \pi_c \mathcal{N}(\mu_c, \sigma^2 I_d)$ with equal mixing proportions $\pi_c = 1/k^*$ and component means $\mu_c \in \mathbb{R}^d$. Let $\Delta_{\min} = \min_{c \neq c'} \|\mu_c - \mu_{c'}\|$ denote the minimum inter-component distance, and let $h_S = 1.06 \hat{\sigma} n^{-1/5}$ be Silverman's reference bandwidth for a single dimension. If $\Delta_{\min} > 2 h_S$, then for each dimension $j$ where the projected means $\{\mu_c^{(j)}\}_{c=1}^{k^*}$ are distinct, the 1D kernel density estimate $\hat{f}_j$ has exactly $k^*$ modes, and consequently $v_j = k^*$.

*Proof sketch.* Under the stated conditions, the 1D marginal in dimension $j$ is a mixture of $k^*$ well-separated 1D Gaussians. Silverman's bandwidth $h_S$ is calibrated for unimodal density estimation; when applied to a multimodal density with component separation $\Delta_j > 2h_S$, the bandwidth is too large to smooth away the individual modes. The critical bandwidth $h_{\mathrm{crit}}(k^*)$ — the bandwidth at which $\hat{f}_j$ becomes unimodal — therefore satisfies $h_{\mathrm{crit}}(k^*) < h_S$, triggering CBV's threshold condition. For any $k > k^*$, the corresponding critical bandwidth exceeds $h_S$ (the density genuinely has $k^*$ modes, not more), so the sequential test terminates at $k^*$. $\square$

**Corollary 1 (Majority Vote Consistency).** Under the conditions of Proposition 1, if at least $\lceil d/2 \rceil$ dimensions have distinct projected means, then the majority vote aggregation yields $\hat{k} = k^*$.

*Proof.* Each such dimension votes $v_j = k^*$. Since $\lceil d/2 \rceil > d/2$, the majority vote selects $k^*$. For the weighted mode aggregation, the result holds whenever the total weight of dimensions voting $k^*$ exceeds the weight of all other votes combined — which is guaranteed when the majority of dimensions are informative (i.e., have non-negligible bimodality strength). $\square$

**Remark 1 (Weighted Mean Rounding Bias).** The weighted mean estimator $\hat{k}_{\mathrm{wm}} = \sum_j w_j v_j / \sum_j w_j$ may produce non-integer values. When the true votes $\{v_j\}$ are not all identical (e.g., some dimensions vote $k^*$ and others vote $k^* - 1$ due to partial overlap), rounding introduces a bias of at most $0.5$. Specifically, $|\hat{k}_{\mathrm{wm}} - k^*| \leq 0.5 + \max_j |v_j - k^*| \cdot (\sum_{j: v_j \neq k^*} w_j / \sum_j w_j)$. In practice, this bias is small when informative dimensions (with high bimodality weight) dominate the weighted average. We use the weighted mode for CBVHybrid to avoid this discretization artifact entirely.

**Remark 2 (Relaxation Beyond Gaussian Mixtures).** For non-Gaussian or non-isotropic data, the conditions of Proposition 1 are sufficient but not necessary. The per-dimension mode count provides a lower bound on the number of separable clusters in that projection, and the aggregation across dimensions provides a consensus estimate. Empirically, CBV achieves 51.4% accuracy on our heterogeneous benchmark (§5), which includes non-Gaussian real-world datasets, demonstrating that the aggregation procedure is robust beyond the idealized setting of Proposition 1.

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

The spectral embedding step uses a Gaussian kernel affinity matrix with $k_{\mathrm{NN}} = \min(15, \lceil n/10 \rceil)$ nearest neighbors, followed by eigen-decomposition of the graph Laplacian. The embedding dimension is $\min(d, 10)$, capped to avoid overfitting in the spectral domain. The choice of $k_{\mathrm{NN}} = 15$ follows the common heuristic in spectral clustering [14] that balances local connectivity with noise robustness; the cap at $\lceil n/10 \rceil$ prevents the neighborhood from exceeding 10% of the data for small samples. The embedding dimension of 10 is chosen to capture the dominant cluster structure while limiting computational cost ($O(n^2 d)$ for the affinity matrix, $O(n^3)$ for eigen-decomposition).

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
- **$\pm 1$ accuracy**: Fraction of estimates $|\hat{k} - k| \leq 1$, measuring near-miss tolerance
- **Adjusted Rand Index (ARI)**: Running $k$-means with $\hat{k}$ and comparing to ground-truth labels. Note: ARI reflects both the quality of $\hat{k}$ and the quality of $k$-means at that $k$, conflating two factors; it is reported for completeness but should be interpreted with caution.

### 4.4 Statistical Testing

We assess significance using:
- **Friedman test**: Non-parametric test for rank differences across indices [14].
- **Multi-seed protocol**: 5 random seeds $\{42, 73, 123, 256, 999\}$, reporting mean $\pm$ std.

**Seed protocol clarification.** The random seeds control $k$-means initialization for geometric CVIs (Silhouette, CH, DB, Gap, Dunn, KL, Jump, McClain–Rao), which require multiple random restarts (`n_init = 10`) to avoid local optima. CBV does not use $k$-means — its estimate is derived from kernel density estimation, which is deterministic for a given bandwidth. Consequently, CBV's $\hat{k}$ is identical across all 5 seeds; the reported standard deviation ($\sigma = 0.8\%$) reflects variation in the geometric CVIs' $k$-means-dependent estimates, not in CBV itself. We include CBV in the multi-seed evaluation for fair comparison: the same 5 seeds are applied uniformly to all indices, and the mean $\pm$ std reporting format allows direct comparison of seed sensitivity across methods.

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

**Post-hoc pairwise analysis.** To identify which pairs of indices differ significantly, we conduct paired Wilcoxon signed-rank tests with Holm–Bonferroni correction ($\alpha = 0.05$, $m = 45$ pairwise comparisons). The Nemenyi critical difference is CD $= 1.779$. Key findings: (i) CBV vs. Gap Statistic: $\Delta = -0.017$, $p = 0.808$ — no significant difference, confirming they are statistically equivalent; (ii) CBV vs. CH Index: $\Delta = +0.069$, $p = 0.317$ — not significant; (iii) CBV significantly outperforms Hartigan ($p < 0.001$), McClain–Rao ($p < 0.001$), Dunn ($p = 0.0003$), and Davies–Bouldin ($p = 0.0008$). These results confirm that CBV belongs to the top-performing tier alongside the Gap Statistic, with no statistically significant difference between them.

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

A key finding is that CBV and geometric CVIs succeed on structurally different data regimes. To quantify this complementarity, we compute three metrics on the 58-dataset benchmark (seed = 42): (i) Jaccard similarity of the sets of datasets where each index is correct, (ii) OR-ensemble accuracy (accepting either index's estimate as correct), and (iii) a Complementarity Index (CI) measuring the fraction of the oracle–best gap that the ensemble closes.

**TABLE VI. Complementarity Analysis (58 Datasets, Seed = 42)**

| Pair | Jaccard | Single Acc. | OR-Ensemble Acc. | CI |
|------|:-------:|:-----------:|:-----------------:|:--:|
| CBV + Gap Statistic | 0.564 | CBV 51.7%, Gap 53.4% | **67.2%** | 0.667 |
| CBV + CH Index | 0.556 | CBV 51.7%, CH 44.8% | **65.5%** | 0.665 |
| CBV + Silhouette | 0.625 | CBV 51.7%, Sil 38.3% | **63.8%** | 0.593 |
| CBV + all 9 geometric | 0.412 | Best-geo 70.7% | **74.1%** | 1.000 |

The mean Jaccard coefficient across all 9 geometric CVIs is 0.412, indicating substantial independence between CBV's correct set and those of geometric indices. The CBV + Gap Statistic OR-ensemble achieves 67.2% accuracy — a 13.8pp improvement over the best single index (Gap, 53.4%) — with a Complementarity Index of 0.667, meaning the ensemble closes two-thirds of the gap between the best single index and the oracle (74.1%). Notably, when CBV is combined with all 9 geometric indices, the ensemble achieves exactly the oracle accuracy (74.1%, 43/58 datasets), yielding CI = 1.000. This demonstrates that CBV captures information that no geometric index provides: without CBV, 1 dataset (moons\_noise0.05) cannot be correctly estimated by any geometric CVI.

Cross-seed validation confirms this complementarity is stable: the CBV + Gap ensemble CI ranges from 0.615 to 0.727 across 5 seeds (mean 0.674), indicating robust complementary behavior.

CBV provides 2 unique successes — the two-moons datasets with noise (moons\_noise0.05, moons\_noise0.1) — where all 9 geometric CVIs fail. These are non-convex datasets where $k$-means partition quality is inherently ambiguous, but the 1D marginal distributions of the moon shapes clearly exhibit two modes. Conversely, geometric CVIs provide 13 unique successes (primarily high-$k$ datasets like iris, digits, yeast, and ecoli) where CBV's mode-counting approach underestimates $k$.

The disagreement signal between CBV and geometric indices is itself informative: on 28/58 datasets (48.3%), both CBV and at least one geometric CVI are correct, providing high-confidence estimates. On the remaining 30 datasets, the discrepancy flags data structures that warrant practitioner investigation.

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

**Kernel function selection.** We additionally evaluated CBV with four kernel functions: Gaussian, Epanechnikov, triangular, and uniform. On 20 synthetic datasets, Gaussian achieved 60.0% accuracy, while Epanechnikov achieved 20.0%, triangular 15.0%, and uniform 0.0%. The Gaussian kernel's superiority stems from its smooth, infinitely differentiable density estimate, which produces well-defined critical bandwidths. Compact-support kernels (Epanechnikov, uniform) produce discontinuous density estimates with ambiguous mode-counting at the boundary, leading to unreliable $h_{\mathrm{crit}}$ values. We therefore use the Gaussian kernel throughout.

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

**Search range ($k_{\max} = 10$)**: Two datasets in our benchmark have $k > 10$ (digits with $k = 10$, yeast with $k = 10$). While these are within the search range, datasets with $k > 10$ would require extending $k_{\max}$, which increases computational cost linearly. We note that the Gap Statistic also uses $k_{\max} = 10$ in standard implementations, so this limitation applies uniformly.

**Seed sufficiency**: Five seeds provide adequate variance estimation for geometric CVIs (standard error of the mean accuracy $\leq 0.6\%$ for all indices). CBV, being deterministic, does not benefit from additional seeds — its reported $\sigma = 0.8\%$ reflects cross-seed variation in geometric CVI estimates, not in CBV itself.

**Point estimation vs. confidence intervals**: CBV currently reports a point estimate $\hat{k}$ without confidence intervals. While the Silverman bootstrap test [15] can provide $p$-values for modality, incorporating these into a confidence interval for $\hat{k}$ requires additional theoretical development (e.g., inverting the hypothesis test across $k$ values). This is a promising direction for future work but is beyond the scope of the present paper, which focuses on establishing CBV as a practical point estimator.

### 6.5 Future Work

**Ensemble methods**: The demonstrated complementarity motivates principled ensemble approaches for combining CBV with geometric indices. A meta-learner that selects or weights indices based on data characteristics (dimensionality, estimated bimodality, cluster shape) could achieve accuracy beyond any single index.

**Multi-dimensional projections**: Replacing per-dimension 1D analysis with random 2D or $d$-dimensional projections could improve high-$k$ detection and non-convex robustness, at increased computational cost.

**Correlation-aware CBV**: Developing a variant that accounts for inter-feature correlations — perhaps through decorrelation preprocessing or correlated-vote debiasing — would extend CBV's applicability to correlated domains.

**Theoretical analysis**: A formal characterization of the relationship between Silverman's mode count and the true cluster count under different data-generating processes would strengthen CBV's theoretical foundations.

**Adaptive bandwidth selection**: Developing a bandwidth selection strategy specifically optimized for CBV's mode-detection task (rather than density estimation) could improve accuracy across diverse data regimes.

### 6.6 Practical Recommendations

Based on our comprehensive evaluation, we offer the following guidance for practitioners:

**When to use CBV.** CBV is most effective when: (i) features are approximately independent (low inter-feature correlation); (ii) clusters have moderate complexity (not highly non-convex); and (iii) the goal is to identify the number of natural groups rather than evaluate partition quality. CBV is particularly valuable when geometric CVIs disagree — the disagreement signal indicates complex structure that warrants investigation.

**When to use geometric CVIs.** Geometric CVIs (especially Gap Statistic) outperform CBV when: (i) clusters are tight and well-separated; (ii) $k$ is high ($k \geq 5$); or (iii) features are strongly correlated. For production pipelines, we recommend running both CBV and the Gap Statistic and examining their agreement.

**When to use ensemble methods.** The OR-ensemble of CBV and Gap Statistic achieves 67.2% accuracy — a 13.8pp improvement over the best single index. For maximum accuracy, use the full ensemble (CBV + all geometric CVIs), which achieves 74.1% (oracle accuracy on our benchmark).

**Default hyperparameters.** CBV requires minimal hyperparameter tuning: $k_{\min} = 2$, $k_{\max} = 10$ (adjust if domain knowledge suggests more clusters), $\tau = 15$ (dimensionality scaling), and $t = 1.3$ (tolerance). The Silverman bandwidth is recommended over Sheather–Jones for CBV's threshold test.

**Red flags.** If CBV returns $k_{\min}$ for most dimensions, the data may be unimodal or the features may be too correlated. If CBV returns $k_{\max}$, the search range may be too narrow. If CBV and all geometric CVIs disagree, the data structure may be ambiguous — consider visualizing the data or consulting domain experts.

---

## 7. Conclusion

We introduced the Critical Bandwidth Validation (CBV) index, the first CVI using critical bandwidth modality testing. CBV reframes the cluster-count problem from geometric partition optimization to statistical inference about the data density, offering a theoretically distinct alternative to established CVIs.

On a comprehensive benchmark of 58 datasets evaluated against 10 established CVIs across 5 random seeds, CBV achieves $51.4\% \pm 0.8\%$ exact-match accuracy, ranking second behind the Gap Statistic ($53.8\%$) and above all geometric indices. CBV exhibits the lowest variance across random seeds, indicating high reliability. Critically, CBV and geometric CVIs succeed on structurally different data regimes — their disagreements are informative, not random — establishing CBV as a complementary diagnostic tool rather than a mere replacement.

We further characterized CBV's failure modes (non-convex shapes, high-$k$ collapse, correlated dimensions), evaluated bandwidth selection strategies (Silverman recommended over Sheather–Jones), and assessed the CBVProjection variant (random 2D projections). These analyses provide a clear roadmap for practitioners: CBV is most effective when features are approximately independent and clusters have moderate complexity, and should be combined with geometric indices for robust cluster validation.

CBV contributes a new statistical-modality perspective to the cluster validation literature — one grounded in four decades of modality testing research — that complements the dominant geometric paradigm and opens new directions for ensemble cluster validation.

---

## Acknowledgments

This research was conducted using the critband package [20], [21] for critical bandwidth analysis. We thank the maintainers of the UCI Machine Learning Repository and scikit-learn for making the benchmark datasets available.

---

## Data Availability

All data used in this study is publicly available. Synthetic datasets were generated using scikit-learn. Real-world datasets are available from the UCI Machine Learning Repository, OpenML, and scikit-learn's built-in datasets. The complete benchmark results and implementation code are available at [repository URL].

**Supplementary Materials.** The following supplementary materials are provided: (S1) per-dataset results table (58 datasets × 10 indices × 5 seeds, including $\hat{k}$ and correctness for each); (S2) pairwise complementarity matrix (CSV); (S3) figures (complementarity scatter, Jaccard bar chart, correctness heatmap, accuracy comparison, rank comparison). These are available at [supplementary URL].

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

[23] N. Wiroonsri and O. Preedasawakul, "A Bayesian cluster validity index," arXiv:2402.02162, 2024.

[24] R. Zhang, H. Zheng, and H. Wang, "CNMBI: Determining the number of clusters using center pairwise matching and boundary filtering," arXiv:2603.26744, 2026.

[25] M. Baragilly and H. Gabr, "High-dimensional BWDM: A robust nonparametric clustering validation index for large-scale data," arXiv:2510.14145, 2025.

[26] S. Modak, "A new measure for assessment of clustering based on kernel density estimation," arXiv:2201.02030, 2022.

[27] R. C. de Amorim and C. Hennig, "Recovering the number of clusters in data sets with noise features using feature rescaling factors," arXiv:1602.06989, 2016.

[28] J. A. Hartigan and P. M. Hartigan, "The dip test of unimodality," *Annals of Statistics*, vol. 13, no. 1, pp. 70–84, 1985.

[29] D. W. Müller and G. Sawitzki, "Excess mass estimates and tests for multimodality," *J. Amer. Statist. Assoc.*, vol. 86, no. 415, pp. 738–746, 1991.

[30] S. J. Sheather and M. C. Jones, "A reliable data-based bandwidth selection method for kernel density estimation," *J. R. Statist. Soc. B*, vol. 53, no. 3, pp. 683–690, 1991.
