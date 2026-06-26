# Re-Review Report — CBV Manuscript (Round 2)

**Decision: Major Revision** | **Score: 5.5/10** (↑ from 4.5/10)

---

## Reviewer Recommendations

| Reviewer | Score | Recommendation | Gate |
|----------|:-----:|----------------|:----:|
| EIC (von Luxburg) | 7/10 | Minor Revision | ✅ Pass |
| Methodology | 5/10 | Major Revision | ⚠️ Hold |
| Domain | 6/10 | Major Revision | ⚠️ Hold |
| Perspective | 7/10 | Minor Revision | ✅ Pass |
| DA (Hennig) | 4/10 | Major Revision | 🔴 Block |

---

## What Was Fixed (Acknowledged)

| Issue | Status | EIC | Meth | Domain | Persp | DA |
|-------|:------:|:---:|:----:|:------:|:-----:|:--:|
| "Second place" → "statistically competitive" | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Proposition 1 weakened | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Variance misinterpretation fixed | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Mode-cluster qualification (§6.4) | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Relevance to Learning Systems | ✅ | ✅ | — | — | ✅ | — |
| References updated | ✅ | ✅ | — | ⚠️ | — | — |

---

## Remaining DA CRITICAL Issues

1. **Foundational contradiction (§1 + §4 methodology).** Paper cites Hennig (2015) that cluster count is not well-defined, then evaluates against ground-truth labels as if deterministically correct. Never reconciles.

2. **Mode-cluster gap not operationalized.** §6.4 acknowledges the gap but abstract, title, and Results all treat mode count as cluster count. Must either reframe CBV as "mode count estimator" or add mode-cluster divergence quantification.

---

## Other Key Remaining Issues

### Methodology (HIGH)
- CBV threshold is a heuristic, not a proper hypothesis test (no bootstrap p-value, no Type I error calibration)
- τ=15, w_min=0.15 calibrated on test data without hold-out validation
- Missing model-based clustering (GMM-BIC/ICL) as benchmark competitor

### Domain (HIGH)
- Ensemble clustering literature uncited (Strehl & Ghosh 2003, Fred & Jain 2005)
- Hall & York (2001) and Cheng & Hall (1998) added but decorative (never discussed)
- HDBSCAN absent as density-based competitor paradigm

### EIC (Minor)
- OR-ensemble reported from single seed only
- Kernel sensitivity only on 20 datasets
- High-k collapse breakdown by k value

### DA
- CI=1.000 statistically expected under independence (29% chance), not evidence of structural complementarity
- No confidence intervals on CBV point estimates
- Entirely dependent on critband package with no standalone reproducibility
- Proposition 1 proves nothing about realistic conditions

---

## Trajectory

First round 4.5 → Second round 5.5 (+1.0). EIC recommends Minor Revision at 7/10 — a strong signal that the core narrative restructure is correct. Remaining problems are:
- **Tier 1 (DA CRITICAL):** Resolve foundational contradiction + operationalize mode-cluster gap. These are reframing tasks, not new experiments.
- **Tier 2 (Method/Domain HIGH):** Add GMM-BIC/ICL baseline, ensemble literature, threshold calibration caveat.
- **Tier 3 (EIC minor):** Multi-seed OR-ensemble, kernel ablation scope note.

With one more focused revision, the paper should reach acceptance level.
