# Handover Document — Paper #10 (CBV) TNNLS Submission

**Handover date:** 2026-06-26
**From:** Session #18 agent (Swarm Revision + 2-Round Review)
**To:** Next agent section (DA CRITICAL Resolution + Final Polish)

---

## Executive Summary

论文已完成 2 轮 7 智能体审稿（评分从 4.5→5.5/10）。EIC 给出 Minor Revision（7/10）建议，但 Devil's Advocate 仍有 2 个 CRITICAL 问题待解决。修改方向从"排名第二"转为"统计等位 + 互补性"，已添加模态-聚类差距章节和 Relevance to Learning Systems 章节。编译干净，11 页，933KB PDF。

---

## What Was Done in This Section (Session #18)

### Phase 1 — First 7-Agent Review Panel
- Full 5-reviewer panel with field-analyst-configured expert identities
- EIC: Prof. Ulrike von Luxburg (Tübingen), Methodology: Prof. Olatz Arbelaitz (Basque), Domain: Prof. Jose E. Chacón (Extremadura), Perspective: Prof. Sandrine Dudoit (UC Berkeley), DA: Dr. Christian Hennig (Bologna)
- **Decision: Major Revision | Score: 4.5/10**
- 3 CRITICAL + 4 consensus (4/5) + 4 majority (3/5) issues documented
- Cross-reviewer issue matrix (25 issues) + 6-phase Revision Roadmap produced

### Phase 2 — Parallel Sonnet Subagent Revisions
- **6 subagents** ran concurrently, each handling a specific review dimension:
  1. Narrative reframe (10 edits: abstract, §1.4, §5.1, conclusion)
  2. Mode-cluster qualification (4 structural insertions: after Corollary 1, new §6.4, §1.2, §2.2)
  3. Variance correction (3 edits: §5.2, §4.4, §5.3)
  4. Bibliography update (1 fix + 5 additions: Sugar & James 2003, Hall & York 2001, Charrad 2014, Cheng & Hall 1998, Fisher & Marron 2001, Ben-Hur 2002)
  5. Practical recommendations + Relevance to Learning Systems rewrite
  6. Statistical enhancements (critical difference diagram, τ=15 heuristic acknowledgment)
- **Compiled**: 915 lines, 11 pages, 933 KB, zero LaTeX errors/warnings

### Phase 3 — Second 7-Agent Re-Review
- Same 5 reviewers re-evaluated the revised manuscript
- **Score: 5.5/10 (+1.0 improvement)**
- EIC: **Minor Revision (7/10)** — "all critical issues and all consensus issues satisfactorily resolved"
- Perspective: **Minor Revision (7/10)** — cross-disciplinary concerns addressed
- DA: **Major Revision (4/10)** — 2 CRITICAL issues remain
- Methodology: **Major Revision (5/10)** — threshold heuristic, hyperparameter calibration
- Domain: **Major Revision (6/10)** — missing ensemble literature, GMM-BIC baseline

---

## What Remains for Next Agent

### Tier 1 — DA CRITICAL (Must Fix, Blocks Acceptance)

1. **Resolve foundational contradiction.** Paper opens citing Hennig (2015) that "true cluster count is not well-defined" (§1), then evaluates against ground-truth labels as deterministically correct (§4-5). Never reconciles these two positions. **Fix options:** (a) reframe CBV as mode-count estimator with dedicated mode-count benchmark; or (b) add explicit reconciliation paragraph stating ground-truth k is a convenient proxy, report accuracy against both labels AND consensus-derived best k.

2. **Operationalize mode-cluster gap into evaluation.** §6.4 acknowledges modes≠clusters but abstract, title, and Results treat them as equivalent. **Fix:** Either reframe title/abstract to "mode counting" scope, or add quantified mode-cluster divergence analysis showing what fraction of errors are attributable to this gap.

### Tier 2 — Methodology + Domain HIGH (Should Fix)

3. **Heuristic threshold, not hypothesis test.** The CBV threshold is described as "statistically distinguishable" but uses no bootstrap p-value, no Type I error calibration. Need either (a) implement Silverman bootstrap, or (b) consistently label as heuristic with calibration statement.

4. **Hyperparameter calibration.** τ=15 and w_min=0.15 were set on evaluation data without hold-out. Add accuracy across τ ∈ {5,10,15,20,30} to show headline result is not driven by tuning.

5. **Missing benchmark competitor.** Add GMM-BIC and GMM-ICL as baselines.

6. **Ensemble literature.** Cite Strehl & Ghosh (2003), Fred & Jain (2005) in §5.5. Report best non-CBV pairwise OR-ensemble.

7. **CI=1.000 null model.** Show expected CI under independence at observed marginal accuracy rates.

### Tier 3 — EIC/Perspective Minor (Recommended)

8. **OR-ensemble across all 5 seeds.** Report mean ± std, not just seed 42.
9. **Hall & York integration.** Discuss in §3.3 whether calibration corrections affect CBV threshold.
10. **HDBSCAN in related work.** Add as density-based competitor paradigm.
11. **Reproducibility statement.** Show CBV implementable with scipy/numpy alone, or provide standalone supp material.
12. **Critical difference diagram** (implement as actual figure or explicit table of average ranks + CD interval).

---

## Key Files

| File | Location | Status |
|------|----------|--------|
| **Manuscript (LaTeX)** | `10-papers/papers/paper-10-cbv-ieee.tex` | 915 lines, revised 2x, compiles clean |
| **Manuscript (PDF)** | `10-papers/papers/paper-10-cbv-ieee.pdf` | 11 pages, 933 KB |
| **Handover** | `10-papers/handover.md` | Sessions #1-#18 log |
| **Round 1 review report** | `10-papers/papers/review-report.md` | 5-reviewer, 4.5/10 |
| **Round 2 re-review report** | `10-papers/papers/re-review-report.md` | 5-reviewer, 5.5/10 |
| **Reviewer feedback (original)** | `10-papers/papers/reviewer-feedback-summary.md` | Original 3 TNNLS reviewers |
| **README** | `10-papers/papers/README.md` | Paper introduction in Chinese |
| **Cover letter** | `10-papers/papers/cover-letter.md` | TNNLS submission cover |
| **Suggested reviewers** | `10-papers/papers/suggested-reviewers.md` | 6 experts |
| **Supplementary materials** | `10-papers/papers/supplementary-materials.md` | S1-S5 index |
| **Supplementary S1** | `10-papers/papers/supplementary_table_s1.csv` | 58×10×5 per-dataset results |
| **Supplementary S2** | `10-papers/papers/supplementary_fig2.csv` | Complementarity matrix |
| **Supplementary S4** | `10-papers/papers/supplementary_posthoc.csv` | Post-hoc pairwise tests |
| **Figures** | `10-papers/papers/figures/*.png` | 7 figures (accuracy, rank, Jaccard, heatmap, scatter) |
| **Manuscript v2 (Markdown)** | `10-papers/papers/paper-10-cbv-manuscript-v2.md` | Source (10,853 words) |
| **Appendix** | `10-papers/papers/appendix-content.md` | Proposition 1 proof + kernel table |
| **CBV core** | `10-papers/scripts/paper-10/cbv/index.py` | CBVIndex |
| **CBVHybrid** | `10-papers/scripts/paper-10/cbv/hybrid.py` | CBVHybrid |
| **Benchmark runner** | `10-papers/scripts/paper-10/run_benchmark.py` | Full benchmark |
| **Analysis scripts** | `10-papers/scripts/paper-10/analysis/*.py` | 4 analysis scripts |
| **Results** | `10-papers/scripts/paper-10/results/*.csv` | Multi-seed metrics, per-dataset, complementarity, post-hoc |

---

## Commands for Next Agent

```bash
# Compile manuscript
cd /c/Users/lenovos/academic-research-skills/10-papers/papers
pdflatex paper-10-cbv-ieee.tex
pdflatex paper-10-cbv-ieee.tex  # Rerun for cross-refs

# Run full benchmark (if needed)
cd /c/Users/lenovos/academic-research-skills/10-papers/scripts/paper-10
uv run python run_benchmark.py

# Run complementarity analysis
cd /c/Users/lenovos/academic-research-skills/10-papers/scripts/paper-10
uv run python analysis/complementarity_enhanced.py

# Check current results
cat results/metrics_multi_seed.csv
cat results/accuracy_per_seed.csv

# Run 7-agent review workflow
cd /c/Users/lenovos/academic-research-skills
# Invoke: Skill("academic-paper-reviewer", "full") then pass paper path
```

---

## Important Notes

1. **Do NOT modify `cbv/` directory code** unless reviewer requests new experiments.
2. **All numbers must use 58-dataset × 5-seed results.** Do not revert to older 31-dataset results.
3. **CBV core result**: 51.4% ± 0.8% accuracy, statistically competitive with Gap (53.8%, p=0.808).
4. **Profile trajectory**: Round 1: 4.5 → Round 2: 5.5. EIC recommends Minor Revision at 7/10. One more focused revision may reach acceptance.
5. **DA CRITICAL issues are structural/reframing**, not experimental. They require narrative reorganization, not new code.
6. **Do NOT change Proposition 1 or Corollary 1** — these were already weakened per reviewer feedback. Instead, the framing around them needs adjustment.
7. **The paper needs author biography photo or `IEEEbiographynophoto`** — currently using nophoto placeholder.

---

## Contact Points

- **Project root**: `C:\Users\lenovos\academic-research-skills`
- **Paper directory**: `C:\Users\lenovos\academic-research-skills\10-papers\papers`
- **Code directory**: `C:\Users\lenovos\academic-research-skills\10-papers\scripts\paper-10`
- **Author**: Qi-Hao Wang, Xidian University, qhwang@xidian.edu.cn
- **Target journal**: IEEE TNNLS
- **Code repo**: https://github.com/cbv-benchmark (private, to be made public upon acceptance)
