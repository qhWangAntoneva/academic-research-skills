# Paper #10 — Revision Roadmap (Phase A-F)

> **Status**: Phase A+B+C complete (Benchmark Expansion)
> **Next**: Phase D (Advanced Features)

---

## ✅ 已完成

| Phase | Key Result | Status |
|:-----:|------------|:------:|
| 0-5 | Full pipeline: research → architecture → benchmark (~45%) → manuscript → citation check → abstracts | Done |
| 6 | Peer review: EIC Major Revision, Chacón 5/10, Arbelaitz 6/10, Hennig 7/10, DA 2 CRITICAL | Done |
| **A** | Quick credibility: `mode` rename, `n_init=10`, multi-seed (5), MAE/±1/ARI metrics | **Done** |
| **B** | Methodology hardening: tolerance calibration (tol=1.30), multimodal weighting (excess_mass) | **Done** |

### Multi-Seed Benchmark (Post-Phase B)
- 5 seeds [42, 73, 123, 256, 999], mean ± std across all metrics
- **CBV: 60.6% ± 1.4% accuracy** (tied #1 with Gap), **MAE=0.65** (best), ±1 Acc=83.9% (best), ARI=0.583
- Phase A→B improvement: **accuracy +16.7pp**, MAE −18%, std reduced 50%
- CBV goes from 3rd/6 → Tied-1st/6 in exact-match accuracy

---

## Revision Plan (from Peer Review Results)

### Phase A: Quick Credibility Wins ✅

| # | Item | Status | Files Touched |
|---|------|:------:|:-------------:|
| P0-5 | `n_init=3` → `n_init=10` | ✅ Done | `comparison/indices.py` |
| P0-1 | `fast` → `mode` (threshold/bootstrap) | ✅ Done | `cbv/index.py`, `spectral.py`, `hybrid.py` |
| P0-3 | Add MAE, ±1 Acc, ARI | ✅ Done | `run_benchmark.py` |
| P0-2 | Multi-seed [42,73,123,256,999] | ✅ Done | `run_benchmark.py` |

### Phase B: Methodology Hardening ✅

| # | Item | Effort | Priority | Depends On |
|---|------|:------:|:--------:|:----------:|
| P1-1 | Adaptive tolerance empirical calibration | 7h | High | — |
| P1-2 | Bimodality weighting → multimodal weight | 5h | High | — |
| P1-10 | Weighting scheme sensitivity analysis | 1h | Medium | P1-2 |

**Result**: tolerance=1.30 (from 1.1), weight_method='excess_mass'. CBV accuracy 43.9%→60.6%.

**Inputs needed**: `cbv/index.py`, `cbv/hybrid.py`, `run_benchmark.py`

### Phase C: Benchmark Expansion ✅

| # | Item | Effort | Priority | Status |
|---|------|:------:|:--------:|:------:|
| P1-4 | New competing indices (Hartigan, KL, Jump, McClain-Rao) | 5h | High | ✅ Done |
| P1-5 | Expand synthetic benchmark (+19 datasets) | 3h | Medium | ✅ Done |
| P1-6 | Expand real benchmark (+8 OpenML datasets) | 3h | Medium | ✅ Done |
| P1-7 | Complementarity analysis (agreement, disagreement, failure) | 3h | Medium | ✅ Done |

### Phase D: Advanced Features

| # | Item | Effort | Priority | Depends On |
|---|------|:------:|:--------:|:----------:|
| P0-6 | Correlated-dimension ablation study | 2h | **P0** | — |
| P1-3 | Sheather-Jones bandwidth option | 3h | High | Phase B |
| P1-8 | CBV with random 2D projections | 5h | Medium | Phase B |
| P1-9 | CBVHybrid spectral component spec | 0.5h | Low | Phase B |

### Phase E: Full Benchmark + Analysis

| # | Item | Effort | Priority |
|---|------|:------:|:--------:|
| — | Full multi-seed benchmark run | ~90min | — |
| P2-4 | k-range expansion analysis | 1h | Low |
| — | Final accuracy tables, complementarity figures | — | — |

### Phase F: Manuscript Revision

| # | Section | Effort | Priority |
|---|---------|:------:|:--------:|
| — | Abstract rewrite | 2h | **P0** |
| — | §1 Introduction reframe | 4h | **P0** |
| — | §2 Related Work corrections | 4h | **P0** |
| — | §3 Methodology restructure (9-subsection) | 8h | **P0** |
| — | §5 Results restructure (disagreement headline) | 8h | **P0** |
| — | §6 Discussion revision (failure classification) | 6h | **P0** |
| — | §7 Conclusion rewrite | 2h | **P0** |
| — | Re-review cycle (max 2 rounds) | 6h | **P0** |

---

## Execution Order

```
Phase A (Quick Wins)    ← DONE
     ↓
Phase B (Methodology)   ← DONE
     ↓
Phase C (Benchmark)     ← DONE
Phase D (Advanced Feat.) ← NEXT (parallel with C)
     ↓
Phase E (Full Run)      ← after C+D
     ↓
Phase F (Manuscript)    ← final, uses all outputs
```

## Key Results to Carry Forward

**Core narrative**: CBV is now tied for #1 in exact-match accuracy (60.6%) while maintaining the **lowest MAE (0.65)** and **highest ±1 accuracy (83.9%)** — no longer just "complementary," CBV matches the best geometry-based CVIs while providing unique diagnostic value.

**Failure modes** (target for Phase C/D fixes):
- Non-convex shapes: 6 failures (spectral fusion helps but not fully)
- High-k underestimation (k≥5): 5 failures (excess_mass layer, target)
- Tight-blob overestimation: 2 failures (tolerance calibration P1-1 fixed partially)
- Noise dimension overwhelm: 2 failures (dim pre-filtering exists but may need tuning)
- Real dataset signal loss: 2 failures (addressed by Phase C expansion)
