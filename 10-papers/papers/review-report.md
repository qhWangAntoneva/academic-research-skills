# 5-Reviewer Panel Report — CBV Manuscript

**Decision: Major Revision** | **Score: 4.5/10**

---

## Reviewer Configuration

| Role | Reviewer | Affiliation | Expertise |
|------|----------|-------------|-----------|
| EIC | Prof. Ulrike von Luxburg | University of Tübingen | Clustering theory, unsupervised learning |
| Methodology | Prof. Olatz Arbelaitz | University of the Basque Country | CVI benchmarking (Arbelaitz 2013) |
| Domain | Prof. Jose E. Chacón | Universidad de Extremadura | Mode clustering, KDE theory |
| Perspective | Prof. Sandrine Dudoit | UC Berkeley | Multiple hypothesis testing, FDR |
| Devil's Advocate | Dr. Christian Hennig | University of Bologna | Cluster analysis foundations |

---

## Score Breakdown

| Dimension | Score | Key Limitation |
|-----------|:-----:|----------------|
| Novelty | 7/10 | Bridge between modality testing and CVI is genuinely novel |
| Soundness | 3/10 | Proposition 1 too narrow; no Type I error control; asymmetric comparison |
| Clarity | 5/10 | "Second place" narrative contradicts own statistical tests |
| Transparency | 7/10 | Failure taxonomy is commendable; oracle bound not clearly labeled |
| Empirical Contribution | 5/10 | Complementarity is valuable; 51.4% is wrong on nearly half of curated data |
| Reproducibility | 3/10 | Code "upon acceptance"; no bootstrap CIs; bimodality formula unspec'd |

---

## CRITICAL Issues (Must Fix)

1. **No multiplicity correction** (R4-CRITICAL). Sequential testing across d dimensions and K values of k creates up to 36,864 implicit tests. No Type I error control, no FDR correction.

2. **Mode-cluster equivalence asserted, not proven** (R5-CRITICAL). The paper equates "number of density modes" with "number of clusters" without defending this. Chacón (2015) proves consistency of mode-based assignments, not that modes = clusters. Hennig (2015), which the paper cites, exposes this as a category error.

3. **51.4% accuracy framing is misleading** (R5-CRITICAL). CBV is wrong on 48.6% of datasets. The Gap at 53.8% is not statistically distinguishable. "Second place" is a misleading narrative.

---

## 4-of-5 Consensus Issues

| # | Issue | R1 | R2 | R3 | R5 | Count | Fix |
|---|-------|:--:|:--:|:--:|:--:|:----:|-----|
| 4 | Proposition 1 too narrow | ✓ | ✓ | ✓ | ✓ | 4 | Weaken claim, add limitations paragraph |
| 5 | Complementarity needs stronger stats | ✓ | ✓ | ✓ | ✓ | 4 | Bootstrap CI; all-seeds reporting |
| 6 | "Second place" vs own tests | ✓ | ✓ | ✓ | ✓ | 4 | Reframe around complementarity, not ranking |
| 7 | Variance misinterpretation | ✓ | ✓ | ✓ | ✓ | 4 | Bootstrap stability analysis |

---

## Priority Revision Roadmap

### Phase 0: Pre-revision
- Release code and results at submission
- Add "Relevance to Learning Systems" section for TNNLS scope

### Phase 1: CRITICAL
1. Multiplicity correction (simulation-based Type I error; FDR across dimensions)
2. Rewrite all mode-cluster equivalence claims with careful qualifications
3. Reframe empirical narrative from "second place" to complementarity thesis

### Phase 2: Consensus (4/5)
4. Proposition 1 → illustrative special case
5. Bootstrap CIs for Complementarity Index
6. Replace "ranking" with "statistically indistinguishable"
7. Bootstrap stability over data resamples

### Phase 3: Important (3/5)
8. τ=15: derive or cross-validate; add sensitivity analysis
9. Sequential Dip-test baseline
10. Scalability across dataset regimes
11. Correlated-dimension ablation expansion

### Phase 4-5: Completeness
- Standard reference datasets (Arbelaitz 2013 subsets)
- Bimodality strength exact formula
- Practical recommendations with concrete decision rules
- Confidence interval demo for 3-5 datasets
- Key missing references (Hall & York 2001, Charrad 2014, etc.)
