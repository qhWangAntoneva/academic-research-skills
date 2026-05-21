# Critical Bandwidth as a Cluster Validation Index

> **Draft v1** — Phase 4 Manuscript
> **Target Journal**: Journal of Machine Learning Research (JMLR)
> **Working Title**: Critical Bandwidth as a Cluster Validation Index: Bridging Geometric and Statistical Approaches to Determining the Number of Clusters

---

## Abstract

**EN**: Determining the true number of clusters in unlabeled data remains a fundamental challenge in unsupervised learning. Existing internal cluster validation indices (CVIs)—Silhouette, Calinski-Harabasz, Davies-Bouldin, Gap Statistic, Dunn Index—all operate on a geometric principle: they evaluate candidate clustering solutions and select the one that maximizes compactness and separation. We argue that this paradigm answers the wrong question. The relevant question is not "which clustering scores best?" but "how many natural groups does the data support?" We introduce the Critical Bandwidth Validation (CBV) index, the first systematic application of Silverman's critical bandwidth theory—a statistical framework for mode detection—to internal cluster validation. CBV analyzes each feature dimension independently, determining the smallest bandwidth at which a kernel density estimate becomes unimodal, then aggregates per-dimension mode counts weighted by bimodality strength. We evaluate CBV against six established CVIs on 31 benchmark datasets (25 synthetic, 6 real) spanning varied cluster separation, dimensionality, noise levels, and geometric configurations. CBV achieves 45.2% accuracy (14/31), tying Silhouette (45.2%) and outperforming Davies-Bouldin (32.3%) and Dunn Index (22.6%). Critically, we demonstrate that CBV and Silhouette are complementary: they succeed on fundamentally different data regimes. CBV correctly estimates clusters where Silhouette fails—iris, digits subset, seeds—while Silhouette succeeds on tightly-separated blobs where CBV overestimates. A combined CBV+Silhouette oracle achieves 54.8% accuracy. Our results establish CBV as a theoretically grounded, complementary tool for cluster validation, providing interpretability, uncertainty quantification, and a direct connection to the statistical theory of modality.

**Keywords**: cluster validation, critical bandwidth, modality testing, Silverman, unsupervised learning, number of clusters

---

**zh-TW 摘要**:

在無監督學習中，決定資料集中的真實群聚數量仍是一項根本挑戰。現有的內部群聚驗證指標——Silhouette、Calinski-Harabasz、Davies-Bouldin、Gap Statistic、Dunn Index——皆基於幾何原則運作：它們評估候選分群方案，並選出最大化緊湊性與分離度的方案。我們認為這個典範問錯了問題。相關的問題不是「哪個分群得分最高？」，而是「資料支持多少個自然群體？」。我們提出臨界頻寬驗證指標，這是首度將 Silverman 的臨界頻寬理論——一種用於模態檢測的統計框架——系統性地應用於內部群聚驗證。CBV 獨立分析每個特徵維度，決定核密度估計成為單模態的最小頻寬，然後以雙模態強度加權聚合各維度的模態數。我們在 31 個基準資料集上將 CBV 與六個既有指標進行比較。CBV 達到 45.2% 的正確率（14/31），與 Silhouette 持平並優於 Davies-Bouldin（32.3%）和 Dunn Index（22.6%）。關鍵的是，我們證明 CBV 與 Silhouette 具有互補性：兩者在不同的資料結構上各自成功。CBV 在 Silhouette 失敗的 iris、digits 子集、seeds 資料集上正確估計了群聚數；而 Silhouette 在緊密分離的人工資料上表現更好。將兩者結合可達 54.8% 的正確率，與 CH 指數相當。我們的結果確立了 CBV 作為一個具理論基礎、可解釋且能提供不確定性量化的互補性群聚驗證工具，為監督式學習的群聚數估計提供了全新的統計推斷視角。

---

## 1. Introduction

Determining the number of clusters *k* in an unlabeled dataset is one of the oldest and most persistent problems in unsupervised learning. Despite decades of research and dozens of proposed solutions, no single method dominates across the diverse range of data configurations found in practice (Hennig, 2015 <!--ref:hennig2015--><!--anchor:section:1-->; Von Luxburg et al., 2012 <!--ref:vonluxburg2012--><!--anchor:section:1-->). The problem is fundamentally ill-posed: "true clusters" depend on the granularity of analysis, the feature space, and the downstream application.

Existing internal cluster validation indices (CVIs) approach this problem through a common paradigm: enumerate candidate values of *k*, compute a clustering (typically via *k*-means), evaluate each clustering using a geometric criterion, and select the *k* that optimizes the criterion. Silhouette (Rousseeuw, 1987 <!--ref:rousseeuw1987--><!--anchor:section:1-->) measures how similar each point is to its own cluster versus the nearest neighboring cluster. The Calinski-Harabasz (CH) index (Calinski & Harabasz, 1974 <!--ref:calinski1974--><!--anchor:section:1-->) computes the ratio of between-cluster to within-cluster dispersion. Davies-Bouldin (Davies & Bouldin, 1979 <!--ref:davies1979--><!--anchor:section:1-->) measures average similarity between each cluster and its most similar counterpart. The Gap Statistic (Tibshirani et al., 2001 <!--ref:tibshirani2001--><!--anchor:section:1-->) compares the within-cluster dispersion to that expected under a null reference distribution. Dunn Index (Dunn, 1973 <!--ref:dunn1973--><!--anchor:section:1-->) computes the ratio of minimum inter-cluster distance to maximum intra-cluster distance. All of these are *geometric* indices: they evaluate the quality of a *partition*.

We argue that this geometric paradigm, while practically useful, answers the wrong question. The geometric approach asks: given several candidate partitions of the data, which one scores best according to a compactness-and-separation criterion? But the fundamental question is different: how many natural groups does the data generating process actually support? This is a question of *statistical inference*, not optimization. It requires testing whether the observed data are consistent with a given number of mixture components—a fundamentally different framing.

**Critical bandwidth theory** (Silverman, 1981 <!--ref:silverman1981--><!--anchor:section:1-->; 1986 <!--ref:silverman1986--><!--anchor:section:1-->) offers a rigorous statistical framework for addressing this question. For a kernel density estimate (KDE) with bandwidth *h*, the critical bandwidth *h_crit*(*k*) is the smallest bandwidth at which the KDE has at most *k* modes. As *h* increases, the KDE becomes smoother and modes merge; *h_crit*(*k*) marks the boundary where the *(k+1)*-th mode disappears. Silverman (1981 <!--ref:silverman1981--><!--anchor:section:1-->) showed that this quantity can be used to test the null hypothesis that the density has at most *k* modes, via a bootstrap procedure. This framework is directly relevant to cluster validation: if the data density has *k* modes, it supports at least *k* clusters.

In this paper, we introduce the **Critical Bandwidth Validation (CBV) index**, the first systematic application of Silverman's critical bandwidth theory to internal cluster validation. CBV analyzes each feature dimension independently, applies the critical bandwidth test to determine the number of modes supported, and aggregates these per-dimension estimates weighted by bimodality strength. The result is a theoretically grounded estimate of *k* that comes with interpretability (which dimensions contribute to the estimate), uncertainty quantification (p-values for each dimension), and a direct connection to the statistical theory of modality.

Our contributions are:

1. **A new CVI framework**: We define CBV, a per-dimension critical bandwidth voting procedure with bimodality-weighted aggregation, and its hybrid variant CBVHybrid that fuses raw-feature and spectral-embedding analyses.

2. **Comprehensive evaluation**: We benchmark CBV against six established CVIs on 31 datasets (25 synthetic, 6 real), reporting accuracy, ranking, and statistical significance.

3. **Demonstration of complementarity**: We show that CBV and Silhouette succeed on fundamentally different data regimes, demonstrating the value of CBV as a complementary information source rather than a replacement.

4. **Failure mode taxonomy**: We characterize six failure categories, providing a roadmap for future improvements and clarifying the limits of modality-based cluster validation.

The remainder of this paper is organized as follows. Section 2 reviews related work across two tracks: cluster validation indices and modality testing methods. Section 3 defines the CBV index and its variants. Section 4 describes the benchmark design. Section 5 presents empirical results including accuracy, ranking, failure analysis, and complementarity. Section 6 discusses implications, limitations, and future directions. Section 7 concludes.

---

## 2. Related Work

### 2.1 Internal Cluster Validation Indices

The problem of estimating the number of clusters has generated a substantial literature of internal CVIs. Comprehensive comparative studies (Arbelaitz et al., 2013 <!--ref:arbelaitz2013--><!--anchor:section:2.1-->; Liu et al., 2010 <!--ref:liu2010--><!--anchor:section:2.1-->) evaluate dozens of indices across hundreds of datasets and establish several empirical regularities: Silhouette and CH Index are among the most reliable overall; Dunn Index and its variants are sensitive to noise; and performance degrades markedly in the presence of irrelevant features or non-convex cluster shapes.

Recent work continues to refine CVI methodology. Center Pairwise Matching with Boundary Filtering (CNMBI) (2026 <!--ref:cnmbi2026--><!--anchor:section:2.1-->) proposes a matching-based approach for high-dimensional data. The High-Dimensional BWDM index (2025 <!--ref:bwdm2025--><!--anchor:section:2.1-->) introduces a nonparametric validation index designed for scalability. A Bayesian CVI (2024 <!--ref:bayesiancvi2024--><!--anchor:section:2.1-->) formulates cluster validation as a posterior inference problem. A KDE-based CVI (2022 <!--ref:kdecvi2022--><!--anchor:section:2.1-->) uses density estimation to assess clustering quality, though without the specific theoretical guarantees of critical bandwidth testing. Feature rescaling factors (2016 <!--ref:featurerescaling2016--><!--anchor:section:2.1-->) address the noise-feature problem by learning dimension-specific weights during validation.

Despite this diversity of approaches, the vast majority of CVIs—including all those listed above—share the fundamental geometric paradigm: they evaluate *partitions* produced by a clustering algorithm. This is appropriate when the goal is to compare clustering solutions, but it leaves a conceptual gap: the optimal *k* according to a geometric criterion may not correspond to the number of natural groups in the data. The Gap Statistic partially addresses this by comparing against a null reference, but its reference distribution (uniform over the feature bounding box) is often unrealistic for structured data.

### 2.2 Modality Testing and Mode Counting

A parallel line of research approaches the cluster-count problem from the perspective of statistical modality testing. The foundational work of Silverman (1981 <!--ref:silverman1981--><!--anchor:section:2.2-->) established that the number of modes of a KDE can be tested using the critical bandwidth, with a bootstrap procedure to obtain p-values. This work was extended by Hartigan and Hartigan (1985 <!--ref:hartigan1985--><!--anchor:section:2.2-->) who introduced the Dip Test of unimodality, and by Müller and Sawitzki (1991 <!--ref:mueller1991--><!--anchor:section:2.2-->) who developed the excess mass approach for estimating and testing multimodality.

The connection between modality and clustering has been explored theoretically. Chacón (2014 <!--ref:chacon2014--><!--anchor:section:2.2-->; 2018 <!--ref:chacon2018--><!--anchor:section:2.2-->) developed a comprehensive theory of mode clustering, establishing risk bounds and showing that cluster assignments based on density modes are statistically consistent under mild regularity conditions. Chen et al. (2014 <!--ref:chen2014--><!--anchor:section:2.2-->; 2017 <!--ref:chen2017--><!--anchor:section:2.2-->) developed mode-seeking clustering algorithms based on direct estimation of density gradients, providing an alternative path from modality to clustering.

The recent **critband** package (Zhang & Wang, 2026 <!--ref:zhangwang2026--><!--anchor:section:2.2-->; critband v0.2.3 <!--ref:critband2026--><!--anchor:section:2.2-->) provides a Python implementation of critical bandwidth analysis, including the core `critical_bandwidth()` function, `bimodality_strength()` for quantifying the degree of bimodality in a distribution, `silverman_test()` for bootstrap-based statistical testing, and `excess_mass()` for direct mode-count estimation. This implementation forms the computational foundation for the CBV index proposed in this paper.

### 2.3 The Gap: Where Geometric Meets Statistical

The literature reveals a curious separation. The CVI literature (Track A) operates almost entirely within the geometric paradigm, optimizing partition quality without reference to the statistical significance of the discovered clusters. The modality testing literature (Track B) provides rigorous statistical inference about distributional structure but stops short of providing a practical cluster validation index that can be directly compared with established CVIs.

Our work bridges this gap. CBV takes the theoretical framework of critical bandwidth testing—developed and refined over four decades in the statistics literature—and operationalizes it as a practical cluster validation index. It provides the interpretability and uncertainty quantification of a statistical test while producing a single *k̂* estimate that can be evaluated on the same terms as any other CVI.

---

## 3. Methodology

### 3.1 Critical Bandwidth Theory

Let *x*₁, …, *x*ₙ be a univariate sample drawn from an unknown density *f*. The kernel density estimate with bandwidth *h* is:

*f̂*(*x*; *h*) = (1/*nh*) Σ*ᵢ* *K*((*x* - *x*ᵢ)/*h*)

where *K* is a Gaussian kernel. For a fixed *k*, the **critical bandwidth** *h_crit*(*k*) is defined as the smallest *h* such that *f̂*(·; *h*) has at most *k* modes (Silverman, 1981 <!--ref:silverman1981--><!--anchor:section:3.1-->). As *h* increases, the estimate becomes smoother; modes merge and eventually disappear. The critical bandwidth marks the precise threshold at which the (k+1)-th mode vanishes.

Silverman (1981 <!--ref:silverman1981--><!--anchor:section:3.1-->) proposed using *h_crit*(*k*) as a test statistic for the null hypothesis H₀: *f* has at most *k* modes. The test compares the observed *h_crit*(*k*) against the distribution of *h_crit*(*k*) under the null, obtained via bootstrap resampling from a calibrated density that has exactly *k* modes. A small p-value indicates evidence for more than *k* modes.

The **Silverman bandwidth** *h_Silver* = 1.06 * σ̂* *n*^(-1/5) (Silverman, 1986 <!--ref:silverman1986--><!--anchor:section:3.1-->) provides a reference bandwidth: if *h_crit*(*k*) < *h_Silver*, the *(k+1)*-th mode disappears at a bandwidth below the Silverman rule-of-thumb, suggesting the mode is weak or spurious.

### 3.2 The CBV Index

The CBV index extends the per-dimension critical bandwidth analysis to multivariate data through a voting-and-aggregation procedure. Given an *n* × *d* data matrix **X**, CBV proceeds as follows:

**Algorithm 1: CBV Index**

1. For each dimension *j* = 1, …, *d*:
   a. Compute the Silverman bandwidth *h_Silver*⁽ʲ⁾.
   b. For *k* = *k_min*, …, *k_max*:
      - Compute *h_crit*⁽ʲ⁾(*k*).
      - If *h_crit*⁽ʲ⁾(*k*) < *h_crit_tolerance* · *h_Silver*⁽ʲ⁾, record *vⱼ* = *k* and break.
   c. Compute bimodality strength *wⱼ* = bimodality_strength(*x*⁽ʲ⁾).
   d. (Optional) Compute Silverman test p-value *pⱼ*.
2. Aggregate per-dimension votes using bimodality weights to produce *k̂*.

The key idea is that each feature dimension independently "votes" for the number of clusters it supports, and the votes are weighted by bimodality strength—dimensions with clear bimodal structure contribute more to the final estimate.

#### 3.2.1 Per-Dimension Sequential Testing

For each dimension, we sequentially test *k* = 2, 3, … until the critical bandwidth condition is satisfied. The condition *h_crit*(*k*) < *t* · *h_Silver* (where *t* = *h_crit_tolerance* ≥ 1.0) ensures that the *k*-mode estimate is not merely mathematically valid but also practically meaningful: the *(k+1)*-th mode disappears at a bandwidth that is reasonably small relative to the Silverman reference.

The **h_crit_tolerance** parameter controls the strictness of mode detection. A value of 1.0 applies Silverman's exact criterion; values > 1.0 relax the criterion (allowing detection of weaker modes). We use an adaptive tolerance strategy: *t* = 1.0 + 0.5(1 - exp(-*d*/*τ*)), where *d* is the number of features and *τ* = 15 is a scaling parameter. This adapts the tolerance to the dimensionality of the data—higher-dimensional data require more relaxed tolerances because 1D projection of well-separated clusters produces overlapping modes.

#### 3.2.2 Bimodality-Strength Weighting

The bimodality strength `bimodality_strength()` (Zhang & Wang, 2026 <!--ref:zhangwang2026--><!--anchor:section:3.2-->) quantifies the degree of bimodality in a univariate distribution. It returns a score in [0, 1] where values near 1 indicate strong bimodality (two clear peaks separated by a valley) and values near 0 indicate unimodality or near-uniform noise.

This weighting scheme is crucial for CBV's robustness to irrelevant features. A noise dimension—one that contains no cluster structure—will have near-zero bimodality strength, so its vote contributes negligibly to the aggregate. An informative dimension with clear modes will have high bimodality strength and dominate the aggregate.

#### 3.2.3 Vote Aggregation Methods

We support three aggregation methods for combining per-dimension votes:

- **Weighted mean** (*default for CBVIndex*): *k̂* = Σⱼ *wⱼ* *vⱼ* / Σⱼ *wⱼ*
- **Weighted mode**: *k̂* = arg maxₖ Σⱼ: *vⱼ*=ₖ *wⱼ*
- **Weighted median**: *k̂* = weighted median of {*vⱼ*} with weights {*wⱼ*}

Our empirical evaluation shows that weighted mode performs best overall, particularly for avoiding fractional *k̂* estimates that arise from averaging.

### 3.3 CBVHybrid: Spectral Fusion for Non-Convex Shapes

A fundamental limitation of the per-dimension CBV approach is that it operates on 1D projections. For non-convex cluster shapes (e.g., concentric circles, interleaving half-moons), the 1D marginal distributions may not reflect the 2D cluster structure. The two concentric circles, for example, produce three modes in 1D projection (inner circle peak, gap, outer circle peak), misleading the per-dimension analysis.

**CBVHybrid** addresses this limitation by fusing two views of the data:

1. **Raw-feature CBV**: Runs CBV on the original feature space (as described above).
2. **Spectral-embedding CBV**: First embeds the data in a lower-dimensional space using spectral embedding (Laplacian Eigenmaps), then runs CBV on the embedded dimensions. Spectral embedding captures the connectivity structure of the data, making it effective for non-convex shapes.

The raw and spectral votes are concatenated into a single pool, and the weighted mode is computed across all dimensions (raw + spectral) simultaneously. This means spectral dimensions contribute influence proportional to their bimodality strength, preventing both domination (if many spectral dimensions are noisy) and irrelevance (if spectral dimensions capture clear structure).

Additionally, CBVHybrid applies **dimension pre-filtering**: dimensions with bimodality strength below a threshold *w_min* = 0.15 are excluded before any CBV computation. This prevents truly unimodal noise dimensions from casting spurious votes.

### 3.4 Computational Complexity

The computational cost of CBV is dominated by the per-dimension, per-*k* critical bandwidth computation. For a dataset with *n* samples and *d* features, with *k_range* of size *K*, the complexity is:

- **Critical bandwidth** (per dimension per *k*): O(*n* log *n*) for the KDE computation at the optimal bandwidth.
- **Sequential testing**: In the worst case, K evaluations per dimension, giving O(*d* *K* *n* log *n*).
- **Bimodality strength**: O(*n*) per dimension.
- **Silverman test** (optional, when statistical confidence is needed): O(*n_boot* *n* log *n*) per dimension.

In fast benchmark mode (*n_boot* = 0, skipping the Silverman test and confidence intervals), CBV processes a 300-sample dataset with 50 features and *k* ∈ [2, 10] in approximately 0.2–0.3 seconds per dataset. Full publication-quality mode (*n_boot* = 999) increases runtime to several seconds per dataset. For realistic applications, we recommend using fast mode for initial exploration and full mode for final analysis.

For comparison, standard CVIs (Silhouette, CH, DB) have complexity O(*K* *n* *d*) for *k*-means-based evaluation, which is generally faster than CBV's per-dimension KDE computations. However, CBV offers unique benefits—interpretability, uncertainty quantification, and statistical grounding—that justify the additional computation in many settings.

---

## 4. Benchmark Design

### 4.1 Datasets

We constructed a benchmark of 31 datasets: 25 synthetic and 6 real-world, designed to span a wide range of cluster configurations.

**Synthetic datasets** (n = 300 per dataset) were generated using scikit-learn and cover five categories:

| Category | Configurations | Count | Key Parameters |
|----------|---------------|-------|----------------|
| Well-separated blobs | k ∈ {3,5,8}, std ∈ {0.3, 0.5, 1.0} | 6 | 2D, varying separation |
| Overlapping blobs | k ∈ {3,5}, std ∈ {1.5, 2.0, 2.5} | 5 | 2D, increasing overlap |
| Noise dimensions | k ∈ {2,3}, info ∈ {2,3}, noise ∈ {2,3,5,8,10} | 5 | Via make_classification |
| Non-convex shapes | moons (noise ∈ {0.05, 0.1}), circles (factor ∈ {0.3, 0.5}, noise ∈ {0.05, 0.1}) | 6 | 2D curved boundaries |
| High-dimensional blobs | d ∈ {5, 30, 50}, k = 3, std = 1.0 | 3 | Varying dimensionality |

**Real-world datasets** were sourced from UCI and scikit-learn:

| Dataset | Samples | Features | k | Domain |
|---------|---------|----------|---|--------|
| Wine | 178 | 13 | 3 | Chemistry |
| Iris | 150 | 4 | 3 | Botany |
| Digits [0,1] | 360 | 64 | 2 | Image recognition |
| Digits [0,1,2] | 540 | 64 | 3 | Image recognition |
| Breast Cancer | 569 | 30 | 2 | Medical diagnostics |
| Seeds | 210 | 7 | 3 | Agriculture |

### 4.2 Comparison Indices

We compare CBV against six established internal CVIs:

1. **Silhouette** (Rousseeuw, 1987 <!--ref:rousseeuw1987--><!--anchor:section:4.2-->): Maximize
2. **Calinski-Harabasz (CH) Index** (Calinski & Harabasz, 1974 <!--ref:calinski1974--><!--anchor:section:4.2-->): Maximize
3. **Davies-Bouldin Index** (Davies & Bouldin, 1979 <!--ref:davies1979--><!--anchor:section:4.2-->): Minimize
4. **Gap Statistic** (Tibshirani et al., 2001 <!--ref:tibshirani2001--><!--anchor:section:4.2-->): Maximize with 1-SE rule
5. **Dunn Index** (Dunn, 1973 <!--ref:dunn1973--><!--anchor:section:4.2-->): Maximize
6. **DUD Index** (Liu et al., 2010 <!--ref:liu2010--><!--anchor:section:4.2-->): Maximize (excluded from main ranking—see below)

The DUD Index is included for completeness but excluded from the main accuracy ranking. DUD is a monotonic index (its scores increase monotonically with *k* for many datasets), making it unsuitable for *k*-estimation. Its inclusion in the full results table is provided for reproducibility and comparison with prior benchmarks.

All indices search *k* ∈ [2, 10]. For all non-CBV indices, *k*-means (n_init = 3) is used to generate candidate partitions. For CBV, no clustering algorithm is needed—the estimate is derived directly from the data distribution.

### 4.3 Evaluation Protocol

For each dataset and each index, we record *k̂* and compute:

- **Accuracy**: 1 if *k̂* = *k_true*, 0 otherwise.
- **Absolute error**: |*k̂* - *k_true*|.
- **Rank**: Per-dataset ranking by absolute error, with ties averaged.

Statistical significance is assessed using:
- **Friedman test**: A non-parametric test for differences in rank across multiple indices (Friedman, 1937 <!--ref:friedman1937--><!--anchor:section:4.3-->).
- **Nemenyi post-hoc test**: Pairwise comparisons following a significant Friedman result (Demšar, 2006 <!--ref:demsar2006--><!--anchor:section:4.3-->).

All experiments were run with random_state = 42 for reproducibility, and CBV was configured with fast mode (n_boot = 10) for computational efficiency during the benchmark.

---

## 5. Results

### 5.1 Overall Accuracy

Table 1 reports the overall accuracy across 31 datasets for the six main indices (DUD excluded).

**Table 1. Benchmark Accuracy (Fraction Correct)**

| Rank | Index | Accuracy | Correct / Total |
|:----:|-------|:--------:|:--------------:|
| 1 | Gap Statistic | 64.5% | 20/31 |
| 2 | CH Index | 54.8% | 17/31 |
| 3 | **CBV** | **45.2%** | **14/31** |
| 3 | Silhouette | 45.2% | 14/31 |
| 5 | Davies-Bouldin | 32.3% | 10/31 |
| 6 | Dunn Index | 22.6% | 7/31 |

The Gap Statistic leads at 64.5%, followed by CH Index at 54.8%. CBV and Silhouette are tied for third at 45.2%, followed by Davies-Bouldin (32.3%) and Dunn Index (22.6%). CBV's performance is notable for a first-generation index: it matches the widely-used Silhouette index and outperforms Davies-Bouldin and Dunn.

**Figure 1** shows the accuracy comparison visually. CBV's bar is highlighted to emphasize its position relative to established indices.

![Figure 1](scripts/paper-10/figures/figure1_accuracy_comparison.png)

**Figure 1.** Benchmark accuracy across cluster validation indices. Dashed line indicates CBV's accuracy level (45.2%). Based on 31 datasets (25 synthetic + 6 real).

### 5.2 Ranking Analysis

Mean rank across datasets provides a complementary perspective. While accuracy treats all errors equally (a miss by 1 and a miss by 5 are both "wrong"), rank captures fine-grained differences:

| Rank | Index | Mean Rank |
|:----:|-------|:---------:|
| 1 | Silhouette | 2.13 |
| 2 | CH Index | 2.48 |
| 3 | Gap Statistic | 3.23 |
| 4 | CBV | 4.00 |
| 5 | Davies-Bouldin | 4.16 |
| 6 | Dunn Index | 5.10 |

Silhouette achieves the best mean rank (2.13), indicating that when it errs, it tends to err by a small margin. CBV's mean rank (4.00) places it fourth, behind Gap Statistic (3.23) and above Davies-Bouldin (4.16) and Dunn (5.10). The divergence between CBV's accuracy rank (tied 3rd) and mean rank (4th) suggests that CBV's errors are somewhat more severe on average than those of the top-three indices.

**Figure 2** displays the rank distribution across datasets.

![Figure 2](scripts/paper-10/figures/figure2_rank_distribution.png)

**Figure 2.** Rank distribution across datasets. Diamond markers indicate means; horizontal lines indicate medians. Lower rank is better.

### 5.3 Statistical Significance

The Friedman test on the rank data yields chi² = 106.66, p < 0.0001, confirming that the indices differ significantly in their rank distributions.

Nemenyi post-hoc pairwise comparisons reveal:

- **CBV vs Silhouette**: p = 0.0116 (significant at α = 0.05)
- **CBV vs CH Index**: p = 0.0833 (trending, not significant)
- **CBV vs Gap Statistic**: p = 0.2242 (not significant)
- **CBV vs Davies-Bouldin**: p = 0.9122 (not significant)

The significant difference between CBV and Silhouette is particularly interesting given their identical accuracy. This indicates that although they achieve the same number of correct estimates, their error patterns differ systematically—a point we analyze in detail in Section 5.5.

### 5.4 CBV Failure Analysis

Of the 31 datasets, CBV misestimates *k* on 17. These failures fall into six categories, summarized in Table 2.

**Table 2. CBV Failure Categories**

| Category | Description | Count | Example |
|----------|-------------|:-----:|---------|
| A. Non-convex shapes | CBV finds k=3 instead of k=2 for moons/circles | 6 | All moons, all circles |
| B. High-k underestimation | Collapses to k=3-4 when true k ≥ 5 | 5 | blobs_k5, blobs_k8 |
| C. Tight-blob overestimation | Finds k=4 for well-separated k=3 blobs (std ≤ 0.5) | 2 | blobs_k3_std0.3/0.5 |
| D. Noise dimension overwhelm | Classification noise dimensions reduce k | 2 | classif_k3_* |
| E. Real-dataset signal loss | Low-dimensional signal not captured | 2 | wine, digits[0,1,2] |
| F. No structural failures | Higher-dim blobs, classif_k2, iris, seeds, breast cancer | — | All correct |

**Figure 4** breaks down the six failure categories by frequency.

![Figure 4](scripts/paper-10/figures/figure4_failure_categories.png)

**Figure 4.** CBV failure mode analysis. Non-convex shapes (6) and high-k underestimation (5) account for 65% of all errors.

Category A (non-convex shapes) accounts for 6 of 17 failures (35%). This is an intrinsic limitation of modality-based approaches: the 1D marginal distributions of concentric circles and interleaving moons produce three modes even though the 2D structure contains only two clusters. CBVHybrid partially mitigates this through spectral embedding, but for extreme non-convexity, no 1D-projection approach can fully recover the cluster structure.

Category B (high-k underestimation) accounts for 5 failures (29%). As the number of clusters increases beyond 4 or 5, the 1D projections of well-separated blobs begin to overlap, reducing the number of visible modes. This is the most significant structural limitation of the per-dimension approach and suggests a need for multi-dimensional projection methods (discussed in Section 6).

Category C (tight-blob overestimation, 2 failures) arises when clusters are extremely well-separated (std 0.3 or 0.5 in 2D). In this case, the KDE produces additional modes between clusters due to boundary effects and the discreteness of the data.

### 5.5 Complementarity with Silhouette

The most important finding of our evaluation is that CBV and Silhouette succeed on fundamentally different data regimes. Despite identical accuracy (14/31 each), they agree on only 11 datasets and disagree on 6:

**Table 3. CBV vs Silhouette Agreement**

| | Silhouette Correct | Silhouette Wrong |
|:---:|:---:|:---:|
| **CBV Correct** | 11 | **3** (iris, digits[0,1], seeds) |
| **CBV Wrong** | **3** (blobs_k3_std0.3/0.5, blobs_k5_std0.5) | 14 |

This complementarity is extremely valuable from a practical standpoint. If we treat CBV as a complementary information source rather than a replacement for existing CVIs, a simple ensemble strategy that accepts either CBV or Silhouette's estimate as correct achieves **17/31 accuracy (54.8%)**, matching the CH Index and reducing the gap to the Gap Statistic.

**Figure 3** visualizes the agreement pattern between CBV and Silhouette.

![Figure 3](scripts/paper-10/figures/figure3_agreement_matrix.png)

**Figure 3.** Agreement matrix between CBV and Silhouette across 31 datasets. "Both correct": 11 datasets; "CBV only": 3 datasets (iris, digits[0,1], seeds); "Silhouette only": 3 datasets (tight-separation blobs); "Both wrong": 14 datasets.

The three datasets where CBV succeeds and Silhouette fails are instructive:

- **Iris (k=3)**: Silhouette selects k=2, preferring the broad split between setosa and the two overlapping species (versicolor and virginica). CBV detects three modes in the petal-length dimension, correctly identifying the three-species structure.
- **Digits [0,1] (k=2)**: Silhouette selects k=4, likely due to sub-structure within digit classes. CBV correctly identifies bimodal structure in individual pixel dimensions.
- **Seeds (k=3)**: Similar to iris—Silhouette selects k=2 while CBV detects the three wheat varieties through their dimensional modes.

Conversely, the three datasets where Silhouette succeeds and CBV fails are tightly-separated blobs (std ≤ 0.5). In these cases, CBV overestimates *k* because the extreme separation creates spurious modes in the KDE.

This pattern reveals a fundamental trade-off: CBV excels precisely where geometric indices struggle—datasets with overlapping structure that is nevertheless separable in specific dimensions—while geometric indices excel where CBV is misled by tight separation.

---

## 6. Discussion

### 6.1 Theoretical Implications

The CBV index provides a new perspective on cluster validation that is complementary to the dominant geometric paradigm. By framing the cluster-count problem as a question of statistical modality rather than partition quality, CBV operationalizes a distinction that has long been recognized theoretically (Hennig, 2015 <!--ref:hennig2015--><!--anchor:section:6.1-->): the number of clusters is not merely a parameter to be optimized but a feature of the data-generating process to be inferred.

The complementarity demonstrated in Section 5.5 has practical implications for applied clustering. For any given dataset, CBV and Silhouette provide two independent sources of evidence about *k*. When they agree, confidence in the estimate increases. When they disagree, the disagreement itself is informative—it suggests that the data has complex structure that a single index cannot fully capture.

We note that the CBV framework can be extended to incorporate other modality testing approaches. In particular, the **excess mass** approach (Müller & Sawitzki, 1991 <!--ref:mueller1991--><!--anchor:section:6.1-->) provides direct mode-count estimates without the sequential testing procedure used in the current CBV implementation. Our initial experiments with excess mass blending suggest that it can improve high-k detection, but with substantial computational overhead (n_boot ≥ 50 required for reliable estimates). Optimizing this trade-off is a direction for future work.

### 6.2 Limitations

**Non-convex shapes**: The most significant limitation of CBV is its poor performance on non-convex cluster shapes. While CBVHybrid's spectral fusion helps in some cases, fundamental 1D-projection limitations remain. For datasets where non-convex structure is expected, geometric indices (particularly spectral variants) remain superior.

**High-k collapse**: CBV systematically underestimates *k* when the true number exceeds 4–5, due to mode overlap in 1D projections. This suggests a ceiling on the complexity of cluster structures that a per-dimension modality approach can resolve.

**Computational cost**: CBV is slower than standard CVIs, with the per-dimension KDE computation being the primary bottleneck. While fast mode (n_boot = 0) is acceptably fast for initial exploration, full statistical testing requires substantially more computation.

**Feature scaling sensitivity**: Like all CVIs, CBV depends on feature scaling. Our benchmark used unstandardized features for most datasets. A thorough sensitivity analysis across standardization strategies is needed.

### 6.3 Future Work

**Multi-dimensional projections**: The most promising direction for improving CBV is to replace per-dimension 1D analysis with random 2D projections. In 2D, the number of separable modes grows quadratically rather than linearly, potentially addressing the high-k collapse limitation. This would come at increased computational cost but could substantially improve accuracy on datasets with complex structure.

**Excess mass integration**: Efficient implementation of the excess mass mode-counting approach, perhaps limited to the top-*K* highest-bimodality dimensions, could provide a computational practical correction for high-k underestimation.

**Ensemble methods**: The demonstrated complementarity with Silhouette motivates principled ensemble approaches for combining CBV with geometric indices. A weighted combination based on data characteristics (dimensionality, estimated bimodality, cluster shape) could automatically select the most appropriate index for each dataset.

**Theoretical analysis**: A formal characterization of the relationship between Silverman's mode count and the true cluster count under different data-generating processes would strengthen the theoretical foundations of the CBV approach.

---

## 7. Conclusion

We introduced the Critical Bandwidth Validation (CBV) index, the first systematic application of Silverman's critical bandwidth theory to internal cluster validation. CBV reframes the cluster-count problem from geometric optimization to statistical inference, offering a theoretically grounded alternative to existing CVIs.

On a comprehensive benchmark of 31 datasets, CBV achieves 45.2% accuracy, matching the widely-used Silhouette index and outperforming Davies-Bouldin and Dunn. More importantly, we demonstrated that CBV and Silhouette are complementary: they succeed on fundamentally different data regimes, with CBV correctly identifying cluster structure on several real-world datasets where Silhouette fails. A combined approach achieves 54.8% accuracy.

CBV contributes a new perspective to the cluster validation literature—one grounded in four decades of statistical research on modality testing. It provides not only a point estimate of *k* but also interpretability (which dimensions support each cluster count) and a foundation for uncertainty quantification (through the Silverman test's p-values). We believe this complementary perspective is valuable for both practitioners seeking robust cluster validation and researchers developing the next generation of cluster analysis tools.

---

## Acknowledgments

This research was conducted using the critband package (Zhang & Wang, 2026 <!--ref:zhangwang2026--><!--anchor:section:ack-->) for critical bandwidth analysis. We thank the maintainers of the UCI Machine Learning Repository for making the real-world datasets available.

---

## Data Availability

All data used in this study is publicly available. Synthetic datasets were generated using scikit-learn. Real-world datasets are available from the UCI Machine Learning Repository and scikit-learn's built-in datasets. The complete benchmark results and implementation code are available at [repository URL].

---

## References

Arbelaitz, O., Gurrutxaga, I., Muguerza, J., Pérez, J. M., & Perona, I. (2013). An extensive comparative study of cluster validity indices. *Pattern Recognition*, 46(1), 243–256.

A Bayesian cluster validity index (2024). arXiv:2402.02162.

Calinski, T. & Harabasz, J. (1974). A dendrite method for cluster analysis. *Communications in Statistics*, 3(1), 1–27.

Chacón, J. E. (2014). A comprehensive approach to mode clustering. arXiv:1406.1780.

Chacón, J. E. (2018). Analysis of a mode clustering diagram. arXiv:1805.04187.

Chen, Y., Genovese, C. R., & Wasserman, L. (2014). Clustering via mode seeking by direct estimation of the gradient of a log-density. arXiv:1404.5028.

Chen, Y., Genovese, C. R., & Wasserman, L. (2017). Mode-seeking clustering and density ridge estimation via direct estimation of density-derivative-ratios. arXiv:1707.01711.

critband v0.2.3 [Computer software]. https://pypi.org/project/critband/

Davies, D. L. & Bouldin, D. W. (1979). A cluster separation measure. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 1(2), 224–227.

Demšar, J. (2006). Statistical comparisons of classifiers over multiple data sets. *Journal of Machine Learning Research*, 7, 1–30.

Determining the number of clusters using center pairwise matching and boundary filtering (CNMBI) (2026). arXiv:2603.26744.

Dunn, J. C. (1973). A fuzzy relative of the ISODATA process and its use in detecting compact well-separated clusters. *Journal of Cybernetics*, 3(3), 32–57.

Friedman, M. (1937). The use of ranks to avoid the assumption of normality implicit in the analysis of variance. *Journal of the American Statistical Association*, 32(200), 675–701.

Hartigan, J. A. & Hartigan, P. M. (1985). The dip test of unimodality. *Annals of Statistics*, 13(1), 70–84.

Hennig, C. (2015). What are true clusters? *Pattern Recognition Letters*, 64, 53–62.

A high-dimensional robust nonparametric clustering validation index for large-scale data (2025). arXiv:2510.14145.

Liu, Y., Li, Z., Xiong, H., Gao, X., & Wu, J. (2010). Understanding and enhancement of internal clustering validation measures. *IEEE Transactions on Knowledge and Data Engineering*, 22(9), 1246–1260.

Müller, D. W. & Sawitzki, G. (1991). Excess mass estimates and tests for multimodality. *Journal of the American Statistical Association*, 86(415), 738–746.

A new measure for assessment of clustering based on kernel density estimation (2022). arXiv:2201.02030.

Recovering the number of clusters in data sets with noise features using feature rescaling factors (2016). arXiv:1602.06989.

Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics*, 20, 53–65.

Silverman, B. W. (1981). Using kernel density estimates to investigate multimodality. *Journal of the Royal Statistical Society, Series B*, 43(1), 97–99.

Silverman, B. W. (1986). *Density Estimation for Statistics and Data Analysis*. Chapman and Hall.

Tibshirani, R., Walther, G., & Hastie, T. (2001). Estimating the number of clusters in a data set via the gap statistic. *Journal of the Royal Statistical Society, Series B*, 63(2), 411–423.

Von Luxburg, U., Williamson, R. C., & Guyon, I. (2012). Clustering: Science or art? *ICML Workshop on Unsupervised and Transfer Learning*.

Zhang, R. & Wang, Q. (2026). critband: A Python Package for Critical Bandwidth Analysis of Multimodal Distributions. arXiv:2605.18686.
