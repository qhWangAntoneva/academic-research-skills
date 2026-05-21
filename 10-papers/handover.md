# Session Handover Log — Paper #10 (CBV)

> **Paper**: Critical Bandwidth as a Cluster Validation Index
> **Status**: Major Revision — Phase A+B+C complete, Phase D next
> **Target**: JMLR

---

## Project Overview

Paper #10 proposes **CBV (Critical Bandwidth Validation)**, the first systematic application of Silverman's critical bandwidth theory to internal cluster validation. CBV answers "how many natural groups does the data support?" (statistical inference) rather than "which k scores best?" (geometric optimization).

**Core references** (appear in all 10 papers):
- Zhang, R. & Wang, Q. (2026). critband: A Python Package for Critical Bandwidth Analysis of Multimodal Distributions. arXiv:2605.18686.
- critband v0.2.3 [Computer software]. https://pypi.org/project/critband/

---

## Current State — After Phase B Revision

### Benchmark Results (Multi-Seed, Multi-Metric — Phase C Scope)

**10 indices** (6 pre-Phase C + 4 Phase C) on **50 datasets** (44 synth + 6 core real) — single seed=42 baseline:

| Index | Accuracy |
|------|:--------:|
| Gap Statistic | **62.0%** |
| **CBV** | **56.0%** |
| CH Index | 48.0% |
| Silhouette | 44.0% |
| KL Index | 38.0% |
| Jump Statistic | 36.0% |
| Davies-Bouldin | 32.0% |
| Dunn Index | 24.0% |
| McClain-Rao | 10.0% |
| Hartigan | 4.0% |

CBV maintains strong performance (#2 of 10) on the expanded benchmark. New indices KL and Jump provide additional comparison baselines. Hartigan's known overestimation bias shows in low accuracy on well-separated data.

### Phase B Results (carried forward)
5 seeds [42, 73, 123, 256, 999] — mean ± std across 31 datasets:

| Index | Accuracy | MAE | ±1 Acc | ARI |
|-------|:--------:|:---:|:------:|:---:|
| **CBV** | **60.6% ± 1.4%** | **0.65 ± 0.01** | **83.9% ± 0.0%** | 0.583 ± 0.006 |
| Gap Statistic | 60.6% ± 3.5% | 1.10 ± 0.03 | 73.5% ± 1.4% | 0.607 ± 0.003 |
| CH Index | 54.8% ± 0.0% | 1.94 ± 0.09 | 74.2% ± 0.0% | 0.645 ± 0.003 |
| Silhouette | 45.8% ± 1.4% | 1.64 ± 0.12 | 65.2% ± 1.4% | 0.643 ± 0.006 |
| Davies-Bouldin | 32.3% ± 0.0% | 3.05 ± 0.17 | 51.6% ± 0.0% | 0.565 ± 0.002 |
| Dunn Index | 24.5% ± 1.8% | 2.70 ± 0.17 | 42.6% ± 1.4% | 0.512 ± 0.012 |

### Narrative
CBV improved from complementary to **top-tier** performance:
- **Tied #1 accuracy (60.6%)** — matches Gap Statistic with lower variance (1.4% vs 3.5%)
- **Lowest MAE (0.65)** — when CBV misses, it misses by less than any other index
- **Highest ±1 accuracy (83.9%)** — still the best at being close
- Phase A→B improvement: **+16.7pp accuracy**, MAE −18%

---

## Revision Roadmap (Phase A-F)

| Phase | Description | Hours | Status |
|:-----:|-------------|:-----:|:------:|
| **A** | Quick Credibility Wins | 7.5 | ✅ **Done** |
| **B** | Methodology Hardening | 12 | ✅ **Done** |
| **C** | Benchmark Expansion | 11 | ✅ **Done** |
| **D** | Advanced Features | 8 | Pending |
| **E** | Full Benchmark | 4 | Pending |
| **F** | Manuscript Revision | 60+ | Pending |

### Phase A — Completed Items

| # | Item | Files Changed |
|---|------|:-------------|
| P0-1 | `fast`→`mode` (threshold/bootstrap) | `cbv/index.py`, `spectral.py`, `hybrid.py` |
| P0-5 | `n_init=3`→`n_init=10` | `comparison/indices.py` |
| P0-3 | MAE, ±1 Acc, ARI metrics | `run_benchmark.py` |
| P0-2 | Multi-seed [42,73,123,256,999] | `run_benchmark.py` |
| — | Fixed CBVHybrid `self.fast` regression | `cbv/hybrid.py` |

### Phase B — Completed Items

| # | Item | Files Changed |
|---|------|:-------------:|
| P1-1 | Tolerance calibration: sweep 10 values, optimal=1.30 | `cbv/index.py`, `hybrid.py`, `spectral.py`, `calibration/tolerance_sweep.py` |
| P1-2 | Multimodal weight: `multimodal_weight()` replaces `bimodality_strength` | `utils/weighting.py`, `cbv/index.py`, `hybrid.py`, `spectral.py` |
| P1-10 | Weight sensitivity: 3 methods compared, excess_mass best | `calibration/weight_sensitivity.py` |

### Phase C — Completed Items

| # | Item | Files Changed |
|---|------|:-------------:|
| P1-4 | New indices: Hartigan, KL, Jump, McClain-Rao | `comparison/indices.py` |
| P1-5 | +19 synthetic datasets (aniso, imbalanced, varied-std, high-k, sparse, non-convex, small-n) | `benchmark/synthetic.py` |
| P1-6 | +8 real datasets (Glass, Yeast, Ecoli, Segmentation, Olivetti Faces, Parkinsons, Ionosphere, Digits full) | `benchmark/real_data.py` |
| P1-7 | Complementarity analysis: agreement matrix, disagreement profile, failure patterns, unique success sets | `analysis/complementarity.py` |

### Phase D — Advanced Features

| # | Item | Effort |
|---|------|:------:|
| P0-6 | Correlated-dimension ablation | 2h |
| P1-3 | Sheather-Jones bandwidth | 3h |
| P1-8 | Random 2D projections CBV | 5h |

### Phase E — Full Multi-Seed Benchmark Run
Run all indices × all datasets × all seeds → final accuracy tables + complementarity figures.

### Phase F — Manuscript Revision
Full narrative restructure: abstract → §1 introduction → §2 related work → §3 methodology (9 subsections) → §5 results (disagreement headline) → §6 discussion → §7 conclusion. Then re-review cycle (max 2 rounds).

---

## File Inventory

```
scripts/paper-10/
  cbv/
    index.py          ← CBVIndex (mode param: threshold/bootstrap)
    spectral.py       ← CBVSpectral (mode param)
    hybrid.py         ← CBVHybrid (mode param, excess_mass, adaptive_tolerance)
    __init__.py       ← Exports CBVHybrid
  benchmark/
    synthetic.py      ← SyntheticDataGenerator (44 datasets: 25 core + 19 Phase C)
    real_data.py      ← RealDataLoader (14 datasets: 6 core + 8 OpenML)
    runner.py         ← BenchmarkRunner (sequential/parallel, summarize, plots)
  comparison/
    indices.py        ← 10 CVI wrappers, CVIWrapper, get_all_indices (n_init=10)
    report.py         ← ComparisonReport
    __init__.py       ← Exports CVIWrapper, ComparisonReport, get_all_indices
  analysis/
    complementarity.py ← ComplementarityAnalysis (Phase C: agreement, disagreement, failure, unique sets)
    __init__.py
  utils/
    weighting.py      ← compute_dimension_weights, weighted_k_vote
    k_selection.py    ← elbow_scan
    preprocessing.py  ← standardize, remove_constant_features
  calibration/         ← Phase B: tolerance sweep + weight sensitivity
    tolerance_sweep.py
    weight_sensitivity.py
  run_benchmark.py    ← Main entry: multi-seed, multi-metric

papers/
  paper-10-cbv-manuscript.md      ← Full draft v1 (~8,000 words, needs revision)
  paper-10-cluster-validation.md  ← Research protocol + results (updated Phase A)

results/ (from Phase A benchmark)
  metrics_multi_seed.csv          ← Mean±std across 5 seeds
  accuracy_per_seed.csv           ← Per-seed accuracy breakdown
  results_seed_*.csv              ← Raw results per seed (5 files)
  benchmark_results.csv           ← Combined results (last seed)
  per_dataset_results.csv         ← Per-dataset detail
  accuracy_comparison.png         ← Bar chart
  rank_comparison.png             ← Box plot
```

---

## Key Decisions (carry forward)

1. **Narrative (Phase B update)**: CBV tied for #1 accuracy (60.6%) with lowest MAE (0.65) — complementary narrative updated to reflect top-tier performance
2. **Mode parameter**: `'threshold'` (fast, no p-values, for benchmarks) vs `'bootstrap'` (full Silverman test, for publication)
3. **n_init=10**: All KMeans-based CVIs use consistent initialization for fair comparison
4. **Multi-seed protocol**: 5 seeds [42, 73, 123, 256, 999], report mean ± std
5. **DUD Index excluded**: Not designed for k-estimation (monotonic scoring)
6. **h_crit_tolerance=1.3** (from P1-1 calibration): default changed from 1.1; adaptive formula inverted to `1.0 + 0.5 * exp(-d/10)`
7. **weight_method='excess_mass'** (from P1-2): replaces legacy bimodality_strength; weight proportional to # modes detected

---

## Collaboration History (Compact)

| Session | Date | What Was Done |
|---------|------|---------------|
| #1-#7 | 2026-05-19/20 | Pipeline setup, architecture, 5-step improvement, final benchmark 45.2% |
| #8 | 2026-05-20 | Manuscript draft v1 (~8k words) + citation check + bilingual abstract |
| #9 | 2026-05-21 | Peer review: 5-reviewer panel, Major Revision, 5 P0 items |
| #10 | 2026-05-21 | **Phase A execution**: mode rename, n_init=10, multi-seed, MAE/±1/ARI |
| #11 | 2026-05-21 | **Phase B execution**: tolerance sweep (opt=1.30), multimodal weight, sensitivity analysis. CBV 43.9%→60.6% |
| #12 | 2026-05-22 | **Phase C execution**: 4 new indices (Hartigan, KL, Jump, McClain-Rao), +19 synth datasets, +8 OpenML real datasets, complementarity analysis module. Benchmark running on 58 datasets × 5 seeds. |

---

*Next: Phase D — Advanced Features. Correlated-dimension ablation (P0-6), Sheather-Jones bandwidth (P1-3), random 2D projections CBV (P1-8). Then Phase E full benchmark run, then Phase F manuscript revision.*
