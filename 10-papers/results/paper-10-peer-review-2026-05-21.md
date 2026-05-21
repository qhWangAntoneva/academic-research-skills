# Paper #10 — Peer Review Results

> **Date**: 2026-05-21
> **Reviewer Panel**: 5 reviewers (EIC + Methodology + Domain + Perspective + Devil's Advocate)
> **Overall Decision**: Major Revision

---

## Editorial Decision Letter

**Journal:** Journal of Machine Learning Research (JMLR)
**Decision:** Major Revision

The reviews were unanimous in recognizing the originality of the core idea — the systematic application of Silverman's critical bandwidth to cluster number estimation — and the honest treatment of failure modes was noted as a strength. However, three themes collectively preclude publication in the current form:

1. **Methodological grounding of the fast-mode procedure** — n_boot=0 is explicitly *not* Silverman's test, providing no p-value or Type I error control.
2. **Headline accuracy figure** — 45.2% on 31 datasets is not a compelling headline; value proposition must shift to diagnostic/interpretability value.
3. **Scope of benchmarking** — 31 datasets (6 real) falls short of field standards; missing critical dataset categories and multiple random seeds.

---

## Cross-Reviewer Consensus: Top Issues

| # | Issue | Count | Severity |
|---|-------|:-----:|:--------:|
| 1 | n_boot=0 is not Silverman's test | 2/5 | CRITICAL |
| 2 | 45.2% accuracy not compelling | 3/5 | CRITICAL |
| 3 | Small/unrepresentative benchmark | 3/5 | MAJOR |
| 4 | Per-dimension independence problematic | 3/5 | MAJOR |
| 5 | Failure modes are fundamental limits | 3/5 | MAJOR |
| 6 | Silverman's test only valid for k=1 vs k=2 | 2/5 | MAJOR |
| 7 | Overclaimed novelty | 2/5 | MAJOR |
| 8 | Complementarity analysis too thin | 2/5 | MAJOR |
| 9 | Single random seed | 2/5 | MAJOR |
| 10 | Oracle narrative logically circular | 1/5 | CRITICAL |

---

## P0 Revision Roadmap (Must-Fix)

| # | Item | Source Reviewers |
|---|------|------------------|
| 1 | Distinguish fast-mode heuristic from Silverman's statistical test | Chacón, Hennig |
| 2 | Reframe contribution away from accuracy superiority | von Luxburg, DA, Hennig |
| 3 | Address per-dimension voting independence assumption | von Luxburg, Chacón, Hennig |
| 4 | Expand benchmark (add dataset categories, more real data) | von Luxburg, Arbelaitz, DA |
| 5 | Classify failures as fundamental limits vs addressable bugs | von Luxburg, Hennig, DA |

## P1 Important

| # | Item |
|---|------|
| 1 | Run with 5+ random seeds |
| 2 | Normalize n_init across all methods |
| 3 | Correct overclaimed novelty |
| 4 | Expand complementarity analysis |
| 5 | Justify adaptive tolerance formula |
| 6 | Add rank-based evaluation metrics |
| 7 | Add more competing indices |

---

## Individual Reviewer Scores

| Reviewer | Score | Decision |
|----------|:-----:|:--------:|
| EIC (von Luxburg) | — | Major Revision |
| Methodology (Chacón) | **5/10** | Major Revisions |
| Domain (Arbelaitz) | **6/10** | Major Revisions |
| Perspective (Hennig) | **7/10** | — |
| Devil's Advocate | — | Adversarial (2 CRITICAL) |
