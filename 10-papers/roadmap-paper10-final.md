# Paper #10 — Revision Roadmap (Phase A-F)

> **Status**: Phase A complete (Quick Credibility Wins)
> **Next**: Phase B (Methodology Hardening) — P1-1 tolerance calibration, P1-2 multimodal weight

---

## ✅ 已完成 (Preliminary Pipeline)

| Phase | Key Result | Status |
|:-----:|------------|:------:|
| 0-5 | Full pipeline: research → architecture → benchmark (~45%) → manuscript → citation check → abstracts | Done |
| 6 | Peer review: EIC Major Revision, Chacón 5/10, Arbelaitz 6/10, Hennig 7/10, DA 2 CRITICAL | Done |
| A | Quick credibility: `mode` rename, `n_init=10`, multi-seed (5), MAE/±1/ARI metrics | **Done** |

### Final Pre-Revision Benchmark (Single Seed)
- 31 datasets (25 synthetic + 6 real), 7 CV indices, k=(2,10), threshold mode
- CBV: 45.2% (14/31), tied 3rd/6 with Silhouette
- Friedman chi²=106.66, p<0.0001; CBV vs Silhouette Nemenyi p=0.0116*

### Multi-Seed Benchmark (Post-Phase A)
- 5 seeds [42, 73, 123, 256, 999], mean ± std across all metrics
- CBV: 43.9% ± 2.9% accuracy, **MAE=0.79** (best), **±1 Acc=87.1%** (best), ARI=0.593

---

## Revision Plan (from Peer Review Results)

### Phase A: Quick Credibility Wins ✅

| # | Item | Status | Files Touched |
|---|------|:------:|:-------------:|
| P0-5 | `n_init=3` → `n_init=10` | ✅ Done | `comparison/indices.py` |
| P0-1 | `fast` → `mode` (threshold/bootstrap) | ✅ Done | `cbv/index.py`, `spectral.py`, `hybrid.py` |
| P0-3 | Add MAE, ±1 Acc, ARI | ✅ Done | `run_benchmark.py` |
| P0-2 | Multi-seed [42,73,123,256,999] | ✅ Done | `run_benchmark.py` |

### Phase B: Methodology Hardening ← NEXT

| # | Item | Effort | Priority | Depends On |
|---|------|:------:|:--------:|:----------:|
| P1-1 | Adaptive tolerance empirical calibration | 7h | High | — |
| P1-2 | Bimodality weighting → multimodal weight | 5h | High | — |
| P1-10 | Weighting scheme sensitivity analysis | 1h | Medium | P1-2 |

**Inputs needed**: `cbv/index.py`, `cbv/hybrid.py`, `run_benchmark.py`

### Phase C: Benchmark Expansion

| # | Item | Effort | Priority | Depends On |
|---|------|:------:|:--------:|:----------:|
| P1-4 | New competing indices (Hartigan, KL, etc.) | 5h | High | — |
| P1-5 | Expand synthetic benchmark (+19 datasets) | 3h | Medium | — |
| P1-6 | Expand real benchmark (+9 datasets) | 3h | Medium | — |
| P1-7 | Expand complementarity analysis | 3h | Medium | Phase B |

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
Phase B (Methodology)   ← NEXT
     ↓
Phase C (Benchmark)     ← parallel with D
Phase D (Advanced Feat.) ← parallel with C
     ↓
Phase E (Full Run)      ← after C+D
     ↓
Phase F (Manuscript)    ← final, uses all outputs
```

## Key Results to Carry Forward

**Core narrative**: CBV is not the best at exact match (43.9%), but has the **lowest MAE (0.79)** and **highest ±1 accuracy (87.1%)** — supporting "diagnostic complementarity" thesis.

**Failure modes** (target for Phase B/C fixes):
- Non-convex shapes: 6 failures (spectral fusion helps but not fully)
- High-k underestimation (k≥5): 5 failures (excess_mass layer, target)
- Tight-blob overestimation: 2 failures (tolerance calibration, P1-1)
- Noise dimension overwhlem: 2 failures (dim pre-filtering exists but may need tuning)
- Real dataset signal loss: 2 failures (addressed by Phase C expansion)
