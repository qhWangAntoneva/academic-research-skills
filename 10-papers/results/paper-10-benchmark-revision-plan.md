# Paper #10 — Benchmark Revision Plan (Addressing Peer Review)

> **Target**: From 31 datasets to ~65+ datasets, 6 to 10+ indices, single to multi-seed protocol
> **Estimated effort**: ~16-20 hours total (spread across ~6 sessions)
> **Prepared**: 2026-05-21

---

## Overview

The peer review identified 12 distinct benchmark concerns. This plan addresses them with concrete, prioritized steps. Each item specifies: what to add, how to add it, which files to modify, time estimate, and risk assessment.

### Current State

| Dimension | Current | Target |
|-----------|:-------:|:------:|
| Datasets | 31 (25 synthetic + 6 real) | ~65 (50 synthetic + 15 real) |
| Indices | 6 (excl. DUD) | 9-10 (incl. CBV) |
| k-range | [2, 10] | [2, min(20, floor(sqrt(n/2)))] |
| Random seeds | 1 (random_state=42) | 5-10 |
| n_init | 3 (indices) vs 10 (CBV) | 10 (all) |
| Metrics | Exact-match accuracy + rank | Exact-match, +/-1, MAE, ARI |
| Real datasets | 6 | 15 |
| Complementarity datasets | 6 (3+3) | ~20+ |

---

## P0 Items (Must Fix for Publishability)

### P0.1 — Expand Synthetic Dataset Suite (31 to ~50)

> **Why**: Domain reviewer explicitly cited Arbelaitz et al. 2013 (720 synthetic + 20 real). Even 50 synthetic + 15 real (65 total) is modest, but it moves from "clearly too small" to "defensible for a methods paper."

#### What to Add (23 new synthetic datasets)

**Category A: Anisotropic / Skewed Clusters (6 datasets)**
Use `make_blobs` with anisotropic cluster covariance (elliptical clusters) to test robustness to non-spherical cluster shapes — a well-known blind spot for mode-based methods.

```
skewed_blobs_k3_cov2:   3 clusters, 2D, one cluster has covariance [[2,0],[0,0.5]]
skewed_blobs_k4_cov2:   4 clusters, 2D, mixed spherical + elliptical
skewed_blobs_k5_cov2:   5 clusters, 2D, all with varying covariances
skewed_blobs_k3_cov4:   3 clusters, 4D (2 informative + 2 noise), mixed covariance
skewed_blobs_k5_cov4:   5 clusters, 4D, mixed covariance
skewed_blobs_k8_cov2:   8 clusters, 2D, random covariance matrices
```

Implementation: Add `make_skewed_blobs()` method to `SyntheticDataGenerator` that accepts a list of covariance matrices or generates them automatically using `np.random.RandomState` with controlled eigenvalues.

**Category B: Variance Heterogeneity (6 datasets)**
Clusters with substantially different variances — one tight cluster, one diffuse cluster. Tests whether CBV's 1D KDE resolves the diffuse cluster's modes.

```
varhet_k3_tight:      k=3, std=[0.3, 2.0, 2.0], samples=[100, 100, 100]
varhet_k3_imbalance:  k=3, std=[0.5, 3.0, 3.0], samples=[200, 50, 50]
varhet_k4_mixed:      k=4, std=[0.3, 0.3, 2.0, 2.0]
varhet_k5_wide:       k=5, std=[0.5, 0.5, 1.5, 2.0, 2.5]
varhet_k3_withnoise:  k=3, as above but with 2 noise dimensions added
varhet_k5_withnoise:  k=5, as above with 3 noise dimensions
```

Implementation: Add `make_variance_heterogeneity()` method. Key challenge: scikit-learn's `make_blobs` accepts a single `cluster_std` or a sequence, so use sequence form.

**Category C: Imbalanced Clusters (6 datasets)**
Cluster sizes vary dramatically (e.g., 80%-10%-10%). This tests one of the Devil's Advocate's specific criticisms and is a known weakness for many CVIs.

```
imbal_k3_mild:     k=3, sizes [150, 100, 50], std=1.0
imbal_k3_severe:   k=3, sizes [250, 25, 25], std=1.0
imbal_k3_extreme:  k=3, sizes [280, 10, 10], std=1.0
imbal_k4_mixed:    k=4, sizes [150, 80, 40, 30]
imbal_k5_severe:   k=5, sizes [200, 30, 25, 25, 20]
imbal_k3_noise:    k=3, imbalanced + 3 noise dimensions
```

Implementation: Add `make_imbalanced_blobs()` method. Use `weights` parameter of `make_blobs` or manual stratified sampling.

**Category D: Near-Empty Clusters (4 datasets)**
Clusters with very few points (e.g., 5-10) among larger clusters. Tests if CBV (or any CVI) can detect tiny clusters.

```
near_empty_k3_5sample:   k=3, sizes [200, 95, 5], std=0.8
near_empty_k4_10sample:  k=4, sizes [200, 100, 50, 10]
near_empty_k3_3sample:   k=3, sizes [250, 47, 3] — edge case
near_empty_k5_mixed:     k=5, sizes [200, 80, 12, 5, 3] — severe edge
```

Implementation: Add `make_near_empty_blobs()` method. Smallest cluster sizes push toward CBV's limits.

**Category E: Additional Non-Convex Shapes (4 datasets)**
Add Swiss Roll (2D manifold extraction) and S-Curve (captures nested structure).

```
swiss_roll_2d:    Swiss roll, extract 2D embedding, k=3
swiss_roll_4d:    Swiss roll, 4D with 2 noise dims added
s_curve_2d:       S-curve, 2D, k=2 (captures two curved manifolds)
s_curve_4d:       S-curve, 4D with 2 noise dims
```

Implementation: Use `sklearn.datasets.make_swiss_roll` and `make_s_curve`, then apply `train_test_split`-like sampling to create cluster structure. Or use spectral embedding to extract 2D manifolds.

Actually, Swiss Roll and S-Curve don't have natural cluster labels. A better approach:

```
dense_vs_sparse_blobs:  2 clusters at very different densities
rings_3_concentric:     k=3, three concentric rings (via make_circles variant)
rings_4_concentric:     k=4, four concentric rings
aniso_circles:          k=2, circles with anisotropic noise
```

Hmm, let me simplify. For non-convex, the existing 6 (moons + circles) are already sufficient. Instead, let me add:

- 3 anisotropic (Category A instead of 6, trim to 3)
- 4 variance heterogeneity (trim to 4)
- 4 imbalanced (trim to 4)
- 2 near-empty (trim to 2)
- 2 more non-convex variants (anisotropic circles, rings)
- 2 "noise dimension explosion": high noise dimensions with few informative

That gives 3+4+4+2+2+2 = 17 new synthetic datasets. 25 existing + 17 = 42 synthetic.

**Category F: High-Noise Dimensions (2 datasets)**

```
classif_k2_info2_noise20:  k=2, 2 informative, 20 noise (up from max 10)
classif_k3_info3_noise15:  k=3, 3 informative, 15 noise
```

Implementation: Simple extension of existing `make_classification` calls.

**Category G: More Diverse k Values (2 datasets)**

```
blobs_k4_d2_std1.0:   k=4, tests gap between popular k=3 and k=5
blobs_k6_d2_std1.0:   k=6, tests boundary of CBV's high-k limit
```

Final new synthetic count: 3 + 4 + 4 + 2 + 2 + 2 + 2 = **19 new synthetic datasets**.
Existing: 25. **Total synthetic: 44**.

**Files to modify:**
- `benchmark/synthetic.py` — add 7 new generator methods + update `generate_benchmark_suite()`

**Time estimate:** ~3 hours (writing generators + validation on 3 samples each)

**Risk:** LOW. Pure data generation, no algorithmic changes.

---

### P0.2 — Expand Real Dataset Suite (6 to 15)

> **Why**: EIC von Luxburg explicitly called out "only 6 real datasets is thin for JMLR." Real datasets provide domain credibility and test generalization beyond synthetic patterns.

#### Datasets to Add (9 new, total 15)

All chosen for: (a) easy UCI/scikit-learn access, (b) diverse k values, (c) diverse sample/feature sizes, (d) different difficulty profiles.

| # | Dataset | Samples | Features | k | File Loader | Challenge |
|---|---------|:-------:|:--------:|:-:|-------------|-----------|
| 1 | **Glass** | 214 | 9 | 6 | UCI URL | Imbalanced, small clusters |
| 2 | **Ecoli** | 336 | 7 | 8 | UCI URL | Many small clusters |
| 3 | **Yeast** | 1,484 | 8 | 10 | UCI URL | High-k real data, imbalanced |
| 4 | **Ionosphere** | 351 | 34 | 2 | UCI URL | High-dim, noisy |
| 5 | **Vehicle** | 846 | 18 | 4 | OpenML via sklearn | Moderate dim, 4-way |
| 6 | **Vowel** | 990 | 10 | 11 | UCI URL | High-k real (11) |
| 7 | **Pima Diabetes** | 768 | 8 | 2 | UCI URL | Imbalanced classes |
| 8 | **Haberman** | 306 | 3 | 2 | UCI URL | Very imbalanced, overlaps |
| 9 | **Wine Quality Red** | 1,599 | 11 | 6 | UCI URL | Ordinal target, large n |

**Implementation plan for each:**
- Glass: `pd.read_csv(UCI_URL, header=None, names=[...])`, label in last column (Type)
- Ecoli: Similar, last column is localization site
- Yeast: Similar, last column is class
- Ionosphere: UCI URL, binary classification, 34 features (some redundant)
- Vehicle: OpenML ID 54, or use UCI source
- Vowel: UCI URL, 11-class vowel recognition
- Pima: UCI URL, 768 x 8, binary diabetes outcome
- Haberman: UCI URL, 306 x 3, binary survival
- Wine Quality Red: UCI URL, 1,599 x 11, 6-class quality

**Files to modify:**
- `benchmark/real_data.py` — add `load_glass()`, `load_ecoli()`, `load_yeast()`, `load_ionosphere()`, `load_vehicle()`, `load_vowel()`, `load_pima()`, `load_haberman()`, `load_wine_quality()` + update `load_all()`
- `benchmark/real_data.py` — add `get_metadata()` expansion

**Time estimate:** ~3 hours (downloading, parsing, integration testing)

**Risk:** LOW-MEDIUM. Some UCI URLs may be stale; have fallback to local files. Need to handle tab/space-separated files, missing headers.

---

### P0.3 — Normalize n_init Across All Indices (10 for all)

> **Why**: Reviewers flagged n_init=3 for comparison indices vs. n_init=10 for CBV as an asymmetry favoring CBV. Fix: normalize all to n_init=10.

**Current:** All non-CBV indices instantiate `KMeans(n_init=3, random_state=...)` inside their per-k loops.
**Fix:** Change to `KMeans(n_init=10, random_state=...)`.

**Files to modify:**
- `comparison/indices.py` — find/replace `n_init=3` --> `n_init=10` in `silhouette_cvi`, `ch_cvi`, `db_cvi`, `gap_cvi`, `dunn_cvi`, `dud_cvi` (6 occurrences)

**Time estimate:** ~5 minutes (find-and-replace)

**Risk:** NEGLIGIBLE. Runtime will increase (~3x), but it's a one-word change. Expected accuracy impact: small but potentially meaningful for indices sensitive to k-means initialization (Dunn, DUD especially).

---

### P0.4 — Multi-Seed Evaluation Protocol (5-10 seeds)

> **Why**: Single seed (random_state=42) is statistically indefensible. Need 5-10 seeds reporting mean +/- std or majority-vote accuracy.

**Design Decision: Majority-Vote Protocol**

Two viable approaches:
- **Option A (simple, preferred)**: Run each CVI on each dataset with 5 different seeds. For each CVI-dataset pair, take the **majority k_hat** across seeds. Report final accuracy as (majority correct)/total. This preserves the binary correct/wrong framework.
- **Option B (informative)**: Report mean +/- std of accuracy across 5 seeds for each CVI. This provides uncertainty bounds but complicates the narrative.

**Recommendation: Option A** (majority vote) for main results, with per-seed variability reported in an appendix.

**Seeds:** [42, 123, 456, 789, 101112] (for 5-seed protocol). Expand to 10 if runtime permits.

**Protocol:**
1. For each random_state in seed_list:
   a. Generate synthetic datasets with that seed
   b. Run all indices with that seed (CBV also gets that seed)
2. For each CVI-dataset pair, collect the k_hat array across seeds
3. Compute majority k_hat (mode of k_hat values)
4. Compute accuracy from majority k_hat vs k_true
5. Report per-seed accuracy range as supplementary material

**Critical note for synthetic data generation:**
Currently, `SyntheticDataGenerator(random_state=42)` is fixed. For multi-seed protocol, each seed must generate its OWN set of synthetic datasets (not just different algorithm seeds on the same data). This is because k-means initialization and dataset generation are both controlled by random_state.

For real datasets, the data is fixed; only k-means initialization changes across seeds.

**Files to modify:**
- `run_benchmark.py` — wrap execution in loop over seeds, add majority-vote aggregation
- `benchmark/runner.py` — add `run_all_multiseed()` method
- Or better: create new utility `run_multiseed_benchmark(kwargs)` in a new script

**Time estimate:** ~2 hours (implementation + verification on 5 seeds)

**Risk:** LOW. The main risk is that some seeds produce degenerate synthetic datasets (too overlapping, etc.). Mitigation: fix the synthetic data generation seeds to produce stable, known-good configurations, while only varying the k-means initialization seed.

Wait — actually, the standard practice in the field (Arbelaitz, Milligan) is to:
- **Fix** the dataset generation seed (so all indices see the same data)
- **Vary** the algorithm random_state (k-means initialization)

This is the correct approach. The reviewer's concern is about initialization dependency, not data sampling dependency.

---

### P0.5 — Add Metric Diversity

> **Why**: Exact-match accuracy is too harsh and masks fine-grained performance differences, as noted by Chacon.

**Metrics to add:**

1. **Exact-match accuracy** (keep existing): 1 if k_hat == k_true
2. **+/-1 accuracy**: 1 if abs(k_hat - k_true) <= 1. Gives credit for "close" estimates.
3. **Mean Absolute Error (MAE)**: mean(|k_hat - k_true|) across datasets.
4. **Average Rank**: per-dataset ranking by absolute error (already implemented).
5. **Adjusted Rand Index (ARI)**: For each index, re-run k-means with the estimated k, compare resulting labels against ground truth using ARI. This is the most informative metric because it captures whether the "wrong" k still produces reasonable clusters.
   - Caveat: For k=2 datasets, 5-means vs 2-means comparison is gated by the true number of clusters. ARI is computed between k-means(k_hat) labels and ground truth.
   - Implementation: for each CVI-dataset, run KMeans(n_clusters=k_hat, n_init=10), compute `adjusted_rand_score(y_true, kmeans_labels)`.
   - For CBV and DUD (non-k-means-based), this is especially interesting — does CBV's k_hat produce meaningful clusters even when wrong?

**Files to modify:**
- `benchmark/runner.py` — add `compute_additional_metrics(results_df, datasets)` method
- `comparison/report.py` — add ARI computation, +/-1 accuracy, MAE
- `run_benchmark.py` — integrate additional metrics into CSV output

**Time estimate:** ~2 hours (ARI computation requires re-running k-means for each estimate, which is O(n_datasets * n_indices) additional KMeans fits)

**Risk:** LOW-MEDIUM. ARI computation for large datasets (n=1500+) plus all k-values could be computationally heavy. Mitigation: only compute ARI for estimated k (not all k candidates).

---

### P0.6 — Expand Complementarity Analysis

> **Why**: Current complementarity analysis is based on only 3+3=6 datasets where CBV and Silhouette disagree. With ~65 datasets, the disagreement set will grow to ~15-20 datasets.

**Current state:** CBV correct 14, Silhouette correct 14, both correct 11, CBV-only 3, Silhouette-only 3, both wrong 14.

**Plan:**
1. With 65+ datasets, the disagreement set will likely grow to ~15-20 datasets, providing a much more robust basis for complementarity claims.
2. Expand complementarity from CBV-vs-Silhouette only to:
   - CBV vs Silhouette
   - CBV vs CH Index  
   - CBV vs Gap Statistic (the top-3 non-CBV indices)
3. Characterize the "success region" of each CVI. For each pair, identify the data characteristics that predict which index will succeed:
   - Dimensionality (low vs high)
   - Cluster separation (well-separated vs overlapping)
   - Cluster count (low k ≤4 vs high k ≥5)
   - Shape (convex vs non-convex)
   - Balance (balanced vs imbalanced)
4. Use this characterization to justify ensemble recommendations.

**Implementation:**
- Compute per-dataset metadata features (n_samples, n_features, k_true, cluster_separation, shape_type, balance_ratio)
- Create a "success region" classifier (decision tree or simple thresholds)
- Visualize with a 2D scatter plot colored by which index succeeds

**Files to modify:**
- `figures/figure3_agreement_matrix.py` — update for more indices and more datasets
- New `figures/figure5_success_regions.py` — characterize success regions
- `comparison/report.py` — add complementarity analysis methods

**Time estimate:** ~3 hours (data analysis + visualization)

**Risk:** LOW. The success-region analysis may find limited structure; simply documenting "CBV succeeds when Silhouette fails on {dataset list}" is still valuable.

---

## P1 Items (Important for Field Standards)

### P1.1 — Add 3-4 More Competing Indices

> **Why**: Chacon noted only 6 competing indices vs 40+ in the literature. Adding 3-4 more covers the most historically important omissions.

**Indices to add (in order of priority):**

1. **Hartigan Index (1975)**: `Hartigan = (W_k / W_{k+1} - 1) * (n - k - 1)`. Simple ratio-based criterion. Add to indices.py as `hartigan_cvi()`.
   - Implementation: ~15 lines. Runs k-means for consecutive k values, computes W_k ratio.

2. **KL Index (Krzanowski & Lai 1988)**: `KL(k) = |DIFF_k - DIFF_{k+1}| / DIFF_k` where `DIFF_k = (k-1)^{2/d} * W_{k-1} - k^{2/d} * W_k`. Well-established in the benchmark literature.
   - Implementation: ~20 lines.

3. **CCC (Cubic Clustering Criterion, Sarle 1983)**: Compares R² of clustering against expected R² under uniform null. More sophisticated than simple ratio indices.
   - Implementation: ~30 lines. Requires computing expected R² from uniform distribution simulation.

4. **COP Index (Gurrutxaga et al. 2010)**: `COP = (1/n) * sum(within_cluster_dispersion / between_cluster_separation)`. Recent, from Arbelaitz's group.
   - Implementation: ~20 lines.

**Files to modify:**
- `comparison/indices.py` — add 4 new CVI functions
- `comparison/indices.py` — update `get_all_indices()` factory to include new indices
- `run_benchmark.py` — update index list

**Time estimate:** ~2 hours (implementation + verification on 3 test datasets)

**Risk:** LOW. All are standard, well-documented indices with simple formulas.

---

### P1.2 — k-Range Expansion with Justification

> **Why**: k-range [2,10] is narrow and possibly favors CBV (which struggles at high k). Need principled upper bound.

**Current:** Fixed k_range=(2, 10) for all datasets. 
**Fix:** Use dataset-dependent upper bound: `k_max = min(20, int(floor(sqrt(n/2))))`. This follows Milligan & Cooper (1985)'s recommendation of `/n` as an upper bound heuristic.

For n=300 samples: sqrt(150) ~ 12, so k_max = 12.
For n=150 (Iris): sqrt(75) ~ 8, so k_max = 8.
For n=1500 (Yeast): sqrt(750) ~ 27, capped at 20.

This means:
- Most synthetic datasets (n=300): k_max=12 (up from 10)
- Iris (n=150): k_max=8 (down from 10)
- Wine (n=178): k_max=10 (same)
- Breast Cancer (n=569): k_max=16
- Larger real datasets: k_max up to 20

**Consequence:** Some indices that prefer high k (DUD, Davies-Bouldin) will have wider range, potentially reducing their accuracy. CBV may also change with wider range.

**Files to modify:**
- `benchmark/runner.py` — accept per-dataset k_range
- `comparison/indices.py` — the `CVIWrapper` already accepts per-instance k_range
- `run_benchmark.py` — compute k_max per dataset
- `cbv/core.py` or `cbv/index.py` — ensure CBV accepts per-dataset k_range

**Time estimate:** ~1 hour

**Risk:** MEDIUM. Changing k-range changes the competitive landscape. Some indices will change their estimates in non-trivial ways. Need to verify that the wider range doesn't break any index (e.g., gap_cvi with B=50 reference datasets becomes slower for k_max=20).

---

### P1.3 — Document Dataset Selection Criteria

> **Why**: Devil's Advocate noted "no dataset selection criteria documented." This is a methodological transparency issue.

**What to add to the manuscript (Section 4.1):**

A clear bullet list of inclusion criteria, e.g.:
1. **k range**: All datasets have known ground-truth k in [2, 11] (covers low to moderate cluster counts).
2. **Dimensionality**: 2 to 64 features (low to moderate dimensionality, where per-dimension voting is tractable).
3. **Sample size**: 150 to 1,600 samples (moderate, avoiding small-sample KDE instability).
4. **Cluster geometry**: Convex blobs, non-convex moons/circles, and real-world mixtures are all included.
5. **Noise**: At least 5 datasets include explicit noise dimensions to test robustness.
6. **Cluster balance**: Balanced, moderately imbalanced, and severely imbalanced cluster sizes are all represented (NEW, with P0.1 additions).
7. **Source**: All datasets are publicly available and widely used in the CVI literature.

**Files to modify:**
- `papers/paper-10-cbv-manuscript.md` — update Section 4.1

**Time estimate:** ~30 minutes

**Risk:** NEGLIGIBLE.

---

### P1.4 — Add Foundational Missing References

> **Why**: Domain reviewer noted missing foundational refs: Milligan & Cooper 1985, Kaufman & Rousseeuw 1990, Vinh et al. 2010.

**References to add:**

1. **Milligan, G. W. & Cooper, M. C. (1985).** An examination of procedures for determining the number of clusters in a data set. *Psychometrika*, 50(2), 159-179. — The seminal benchmark in cluster validation. Cite in 2.1 and 4.1 (to frame benchmark design).
2. **Kaufman, L. & Rousseeuw, P. J. (1990).** *Finding Groups in Data: An Introduction to Cluster Analysis*. Wiley. — Standard reference for PAM and silhouette concepts beyond the original 1987 paper. Cite in 2.1.
3. **Vinh, N. X., Epps, J., & Bailey, J. (2010).** Information theoretic measures for clusterings comparison: Variants, properties, normalization and correction for chance. *JMLR*, 11, 2837-2854. — Standard reference for ARI variants and cluster comparison metrics. Cite in 4.3 (evaluation protocol).

**Files to modify:**
- `papers/paper-10-cbv-manuscript.md` — add citations in appropriate sections + add to References

**Time estimate:** ~15 minutes

**Risk:** NEGLIGIBLE.

---

## P2 Items (Nice to Have; Defer if Time-Constrained)

### P2.1 — Dataset Selection Visualizations

Create a figure showing the distribution of benchmark datasets across key dimensions (k_true vs n_features, colored by shape type). This addresses the transparency concern and provides a quick visual reference for dataset coverage.

**Files to modify:**
- New `figures/figureS1_dataset_coverage.py`

**Time estimate:** ~1 hour

---

### P2.2 — Computational Cost Comparison Table

Expand the existing computational complexity analysis into a table with actual wall times for all indices, showing the trade-off between CBV's higher computation and its unique benefits.

**Time estimate:** ~1 hour

---

## Execution Order and Dependencies

```
Phase 0: Setup
  P0.3 (n_init fix) — 5 min — no dependencies
  P1.4 (refs) — 15 min — no dependencies
  │
  ▼
Phase 1: Data Expansion
  P0.1 (synthetic datasets) — 3h — depends on: nothing
  P0.2 (real datasets) — 3h — depends on: nothing
  │  Can run P0.1 and P0.2 in parallel
  │
  ▼
Phase 2: Index Expansion
  P1.1 (new indices) — 2h — depends on: nothing
  P1.2 (k-range) — 1h — depends on: nothing
  │  Can run P1.1 and P1.2 in parallel with Phase 1
  │
  ▼
Phase 3: Protocol Changes
  P0.4 (multi-seed) — 2h — depends on: P0.3 (n_init standardized)
   │
   ▼
Phase 4: Full Benchmark Run
  Integration + execution — 4-6h — depends on: P0.1, P0.2, P0.3, P0.4, P1.1, P1.2
  │  This is the heavy lift: 65+ datasets × 10 indices × 5 seeds
  │  Estimated runtime: ~45-90 minutes for the full grid
  │
  ▼
Phase 5: Analysis
  P0.5 (metric diversity) — 2h — depends on: Phase 4 results
  P0.6 (complementarity) — 3h — depends on: Phase 4 results
  P1.3 (selection criteria) — 30 min — can be written in parallel
  │
  ▼
Phase 6: Manuscript Update
  Update Section 4 (Benchmark Design) — 1h
  Update Section 5 (Results) — 2h
  Update Section 6 (Discussion) — 1h
  Update all figures — 2h
  └── Total: ~6h for manuscript revisions

Grand total: ~26-30 hours (optimistic) to ~35-40 hours (realistic)
```

---

## Specific Code Changes Summary

### New Files to Create

| File | Purpose | Est. Lines |
|------|---------|:----------:|
| `benchmark/controlled_experiments.py` | Variance heterogeneity, near-empty, imbalanced generators | ~100 |
| `results/benchmark_multiseed.py` | Multi-seed aggregation script | ~80 |
| N/A (new Fig 5) | `figures/figure5_success_regions.py` | ~80 |

### Files to Modify

| File | Changes | Est. Impact |
|------|---------|:-----------:|
| `benchmark/synthetic.py` | Add 7 new generator methods + update `generate_benchmark_suite()` | +180 lines |
| `benchmark/real_data.py` | Add 9 new loaders + update `load_all()` | +200 lines |
| `comparison/indices.py` | Add 4 new indices + update factory | +100 lines |
| `comparison/indices.py` | Find/replace `n_init=3` → `n_init=10` | +0 lines (6 edits) |
| `benchmark/runner.py` | Add multi-seed, ARI, +/-1 metrics | +80 lines |
| `run_benchmark.py` | K_max per dataset, multi-seed loop, new indices | +50 lines |
| `papers/paper-10-cbv-manuscript.md` | Update §§4-6, add 3 refs, update figures | Extensive |
| 4 existing figure scripts | Update data sources for 65+ datasets | +20 each |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| UCI URLs stale/unavailable | LOW | MEDIUM | Fallback to OpenML or cached local copies |
| Multi-seed runtime blowup (65 datasets x 10 indices x 5 seeds) | HIGH | MEDIUM | Run in background; use joblib; set 90-min timeout |
| New indices have different k-preferences (e.g., Hartigan prefers lower k) | MEDIUM | LOW | This is expected — the whole point is comparison |
| Wider k-range changes competitive landscape dramatically | LOW | HIGH | Pre-run sensitivity analysis on 10 datasets first |
| ARI computation is slow for large datasets with high k_hat | MEDIUM | LOW | Sample points if n > 2000; cap k at 20 |
| Some synthetic configs produce degenerate clusters (all points merge into 1) | LOW | LOW | Pre-validate each configuration on 3 seeds before full run |

---

## Verification Protocol

After each phase, run validation checks:

**Phase 1 (Data expansion):**
```
python -c "
from benchmark.synthetic import SyntheticDataGenerator
g = SyntheticDataGenerator(42)
suite = g.generate_benchmark_suite()
print(f'Total synthetic: {len(suite)}')
for ds in suite[:3]: print(f'  {ds[\"name\"]}: {ds[\"X\"].shape}, k={ds[\"k_true\"]}')
"
```

**Phase 2 (Index expansion):**
```
python -c "
from comparison.indices import get_all_indices
indices = get_all_indices(k_range=(2, 10))
print(f'Total indices: {len(indices)}')
print([i.name for i in indices])
"
```

**Phase 3 (Full benchmark):**
Run `run_benchmark.py` on a 10-dataset subset first, verify all 10 indices produce valid k_hat values.

---
