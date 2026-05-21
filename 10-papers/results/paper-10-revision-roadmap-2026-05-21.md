# Paper #10 — Unified Revision Roadmap

> **Based on**: Peer Review (5 reviewers) + Expert Team Analysis (Methodology, Benchmark, Narrative, Implementation)
> **Total estimated effort**: ~55 hours (P0: ~35h, P1: ~15h, P2: ~5h)
> **Status**: Pending execution

---

## Executive Summary

The peer review returned **Major Revision** with 5 P0 must-fix items. Four expert agents analyzed the requirements independently. This document synthesizes their plans into a single, prioritized, executable roadmap.

### Strategic Reframing

The paper's core problem is **narrative**, not methodology. The current framing ("CBV achieves 45.2% accuracy") is a losing battle. The revision must shift to:

> **"CBV is the first CVI grounded in statistical modality testing. Its primary value is not accuracy superiority but diagnostic complementarity — CBV and geometry-based CVIs measure different aspects of cluster structure, and their disagreements are informative."**

---

## P0: Must-Fix Before Re-Submission (~35 hours)

| # | Item | Hours | Type | Expert Source |
|---|------|:-----:|:----:|:-------------:|
| 1 | Distinguish n_boot=0 heuristic from Silverman's test | 3 | Code + MS | Methodology, Implementation |
| 2 | Multi-seed benchmark (5 seeds) | 2 | Code | All 4 experts |
| 3 | Add evaluation metrics (MAE, ±1, ARI) | 2 | Code | Methodology, Implementation |
| 4 | Restructure paper narrative (abstract, intro, results, discussion) | 35h* | MS | Narrative |
| 5 | Fix n_init asymmetry (n_init=10 for all) | 0.5 | Code | Benchmark, Implementation |
| 6 | Add correlated-dimension ablation study | 2 | New script | Methodology, Implementation |

*\*Narrative restructure runs in parallel with code work showing as total hours, not sequential.*

### P0-1: n_boot=0 Heuristic vs. Silverman's Test (3h)
**Files**: `cbv/index.py`, `run_benchmark.py`
**Approach**: Rename `fast` parameter to `mode` with explicit `"threshold"` vs `"bootstrap"` options. Add logging disclaimers.

### P0-2: Multi-Seed Protocol (2h)
**Files**: `run_benchmark.py`, `benchmark/runner.py`
**Approach**: Loop over seeds [42, 73, 123, 256, 999], report mean ± std.

### P0-3: Evaluation Metrics (2h)
**Files**: `benchmark/runner.py`, `run_benchmark.py`
**Approach**: Add MAE, ±1 accuracy, ARI alongside exact-match accuracy.

### P0-4: Narrative Restructure
**Sections affected**: Abstract, §1 Introduction, §2 Related Work, §5 Results, §6 Discussion, §7 Conclusion
See Narrative Expert's full section-by-section plan (separate document).

### P0-5: n_init Normalization (0.5h)
**Files**: `comparison/indices.py`
**Approach**: Replace all `n_init=3` with `n_init=10`.

### P0-6: Correlated Dimension Ablation (2h)
**Files**: New `benchmark/correlated_synthetic.py`
**Approach**: Generate data where cluster structure exists only in feature correlations (unimodal marginals).

---

## P1: Important (~15 hours)

| # | Item | Hours | Expert Source |
|---|------|:-----:|:-------------:|
| 1 | Adaptive tolerance empirical calibration | 7 | Methodology |
| 2 | Bimodality weighting → multimodal weight | 5 | Methodology |
| 3 | Add Sheather-Jones bandwidth option | 3 | Methodology |
| 4 | Add new competing indices (Hartigan, KL, etc.) | 5 | Benchmark, Implementation |
| 5 | Expand synthetic benchmark (+19 datasets) | 3 | Benchmark |
| 6 | Expand real benchmark (+9 datasets) | 3 | Benchmark |
| 7 | Expand complementarity analysis | 3 | Benchmark |
| 8 | Add CBV with random 2D projections | 5 | Methodology |
| 9 | CBVHybrid spectral component specification | 0.5 | Implementation |
| 10 | Weighting scheme sensitivity analysis | 1 | Implementation |

---

## P2: Improvements (~5 hours)

| # | Item | Hours |
|---|------|:-----:|
| 1 | Add missing foundational refs (Milligan & Cooper 1985, etc.) | 0.5 |
| 2 | Add computational cost analysis | 1 |
| 3 | Dataset selection criteria documentation | 0.5 |
| 4 | Add k-range expansion analysis | 1 |
| 5 | Software version + hardware specs appendix | 0.5 |
| 6 | Apply peer review revision to manuscript | 1.5 |

---

## Execution Order

### Phase A: Quick Credibility Wins (~7.5h)
```
Day 1: P0-5 (n_init fix, 0.5h) → P0-1 (mode rename, 3h) → P0-3 (metrics, 2h) → P0-2 (seeds, 2h)
→ Validate: run benchmark, check no regression
```
**Deliverable**: Updated benchmark results with proper naming, multi-seed, multi-metric tables.

### Phase B: Methodology Hardening (~12h)
```
Day 2: P1-1 (tolerance calibration, 7h) → P1-2 (multimodal weight, 5h)
→ Validate: sweep results table, weight comparison figure
```
**Deliverable**: Calibration experiment results, weight method comparison.

### Phase C: Benchmark Expansion (~11h)
```
Day 3: P1-4 (new indices, 5h) → P1-5 + P1-6 (synth + real data, 6h)
→ Validate: complete benchmark run (~60min)
```
**Deliverable**: Expanded benchmark (31 → ~65 datasets, 6 → 10 indices).

### Phase D: Advanced Features (~8h)
```
Day 4: P0-6 (correlated data, 2h) → P1-3 (SJ bandwidth, 3h) → P1-8 (2D projections, 5h)
→ Validate: unit tests, compare accuracy vs baseline
```
**Deliverable**: CBVProjected, SJ bandwidth results.

### Phase E: Full Benchmark + Analysis (~4h)
```
Day 5: P1-7 (complementarity expansion, 3h) → P2-4 (k-range expansion, 1h) 
→ Full benchmark run (~90min)
→ Analyze: accuracy tables, complementarity figures, failure analysis update
```
**Deliverable**: Final benchmark results with all improvements.

### Phase F: Manuscript Revision (~40h writing across all authors)
```
Week 2-3:
- Abstract rewrite
- §1 Introduction reframe
- §2 Related Work corrections + CVI pluralism addition
- §3 Methodology restructure (following proposed 9-subsection structure)
- §5 Results restructure (disagreement analysis as headline)
- §6 Discussion revision (failure classification, use case)
- §7 Conclusion rewrite
```
**Deliverable**: Complete revised manuscript v2.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| P1-1 calibration gives different tolerance → accuracy shift | High | Medium | Re-run benchmark; document both formulas |
| P1-2 multimodal weight changes CBV accuracy | Medium | Medium | Report both weight methods; show robustness |
| P1-8 (2D projections) computationally expensive | High | Medium | Limit to n_projections=20; use fast mode |
| Full benchmark runtime with 65×10×5 = 3250 evaluations | High | Medium | Use joblib, early stopping on failed configs |
| Narrative restructure uncovers additional issues | Medium | Medium | Iterative: draft → review → revise |
| Code changes introduce regression on previously correct cases | Low | High | Regression test suite (currently correct 14 datasets) |

---

## Recommended Decision

**For a time-constrained revision (target: 2 weeks):**

| Phase | Hours | Priority |
|-------|:-----:|:--------:|
| A (quick credibility) | 7.5 | **P0 — Do first** |
| B (methodology hardening) | 12 | **P0 — Do second** |
| F (manuscript revision) | 40 | **P0 — In parallel with B** |
| C (benchmark expansion) | 11 | **P1 — If time permits** |
| D (advanced features) | 8 | **P2 — Deferrable** |
| E (full benchmark) | 4 | **P1 — After C** |

**Minimum viable revision** (addresses all CRITICAL + MAJOR reviewer concerns):
- Phase A: 7.5h ✅ Addresses Chacón 5/10 credibility issues
- Phase B: 12h ✅ Addresses methodology concerns
- Phase F: 40h ✅ Addresses all narrative concerns
- **Total: ~60h** = 1.5 weeks full-time
