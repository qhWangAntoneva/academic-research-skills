# Handover Document — Paper #10 (CBV)

**Handover date:** 2026-06-21
**From:** Session #15 agent
**To:** Next agent section (Phase F-9: Reviewer Feedback)

---

## Executive Summary

论文 v2 已完成重写（8253 词，TNNLS 格式），三位 TNNLS Reviewer 审核结果为 Major Revision。当前需要根据 7 个 CRITICAL 和 15 个 MAJOR 反馈项修订论文。核心修复：量化互补性、添加聚合理论、修正参考文献、添加实践者指南。

---

## What Was Done in This Section (Sessions #13-#15)

### Phase D — Advanced Features ✅
- P0-6: Correlated-dimension ablation study（CBV 对相关维度脆弱）
- P1-3: Sheather-Jones bandwidth option（Silverman 推荐）
- P1-8: CBVProjection class（随机 2D 投影，多数投票）

### Phase E — Full Benchmark ✅
- 10 indices × 58 datasets × 5 seeds，耗时 ~90min
- CBV: 51.4% ± 0.8%（rank #2，最低方差）
- CBVProjection: 46.6%，CBVHybrid: 51.7%

### Phase F-1 至 F-8 — Manuscript + Reviewer Eval ✅
- 论文 v2 完整重写（TNNLS 格式，8253 词）
- 三位 Reviewer 审核：Major Revision（7 CRITICAL, 15 MAJOR, 13 MINOR）

---

## What Remains for Next Agent (Phase F-9)

### 第一优先级 — CRITICAL 修复

1. **量化互补性** (C1)
   - 实现简单集合并（OR-ensemble），报告准确率
   - 计算 CBV vs 每个几何 CVI 的 Jaccard 系数
   - 生成逐数据集正确/错误矩阵
   - 文件: `analysis/complementarity.py` 已有基础，需扩展

2. **添加聚合理论** (C2)
   - 添加 §3.X 小节，证明 per-dimension 投票聚合的条件
   - 至少对各向同性高斯混合的特殊情况给出定理
   - 分析加权均值舍入偏差
   - 文件: `papers/paper-10-cbv-manuscript-v2.md` §3.5 附近插入

3. **完善 Algorithm 1** (C3)
   - 明确定义无 k 满足条件时的默认行为
   - 添加边界检查：h_crit(k_min) >= t·h_Silver 时的处理
   - 文件: `papers/paper-10-cbv-manuscript-v2.md` §3.2

4. **修正参考文献** (C7)
   - 合并 Part 1 和 Part 2 的参考文献为单一列表
   - 修正 [10]（KL index = Krzanowski & Lai 1988，非 Hartigan）
   - 补全 [23]-[27] 的作者名和期刊名
   - 去重，确保全文引用编号一致

5. **精确限定"首创"** (C6)
   - 将"首个基于临界带宽理论的 CVI"改为"首个使用临界带宽模态测试的 CVI"
   - 影响位置: Abstract, §1.4, §2.3, §7

6. **明确 seed/n_init 协议** (C5)
   - 说明 5 个 seed 控制什么（k-means 初始化）
   - 分别报告 CBV 在各 seed 的准确率（应相同，因为 CBV 是确定性的）
   - 文件: §4.4, §5.3

### 第二优先级 — MAJOR 修复

7. **添加事后成对比较** (M4)
   - Nemenyi test 或 paired Wilcoxon + Holm-Bonferroni
   - 报告哪些配对差异显著
   - 文件: §5.1 之后插入

8. **添加逐数据集结果表** (M6)
   - 补充材料：每个数据集 × 每个指标 × 每个 seed 的 k_hat
   - 文件: 新增 supplementary table

9. **添加实践者指南** (M12)
   - §6 增加"Practical Recommendations"小节
   - 何时用 CBV、何时用 Gap、何时用 ensemble
   - 超参数默认值和敏感性

10. **重构 Abstract** (M10)
    - 问题 → 缺口 → 方法 → 结果 → 影响
    - 方法论在动机之后引入

11. **修正标题** (M9)
    - "Critical Bandwidth Validation: A Statistical Modality Approach to Estimating the Number of Clusters"

12. **证明 τ 参数** (M2)
    - 说明 τ=15 是先验设定还是调参
    - 添加 τ 敏感性分析

13. **核函数敏感性** (M3)
    - 高斯 vs Epanechnikov vs biweight

### 第三优先级 — MINOR 修复

14. 双模态强度数学定义
15. 加权均值舍入策略
16. Dip Test 对比（或解释为什么不适合作为 CVI）
17. 增加 seed 数量到 10+
18. k_max=10 限制讨论
19. §2.1/§2.3 冗余合并

---

## Key Files

| File | Location | Status |
|------|----------|--------|
| HANDOVER.md | `10-papers/HANDOVER.md` | This file |
| handover.md | `10-papers/handover.md` | Session log (sessions #1-#15) |
| roadmap-paper10-final.md | `10-papers/roadmap-paper10-final.md` | Phase roadmap |
| manuscript v2 | `10-papers/papers/paper-10-cbv-manuscript-v2.md` | 完整手稿 v2 (8253 词) |
| manuscript v1 | `10-papers/papers/paper-10-cbv-manuscript.md` | 旧版手稿 (参考用) |
| reviewer feedback | `10-papers/papers/reviewer-feedback-summary.md` | 3-Reviewers 汇总 |
| CBV core | `10-papers/scripts/paper-10/cbv/index.py` | CBVIndex + sheather_jones_bandwidth |
| CBVHybrid | `10-papers/scripts/paper-10/cbv/hybrid.py` | CBVHybrid |
| CBVProjection | `10-papers/scripts/paper-10/cbv/projection.py` | CBVProjection (Phase D) |
| Benchmark runner | `10-papers/scripts/paper-10/run_benchmark.py` | 全量基准脚本 |
| Multi-seed results | `10-papers/scripts/paper-10/results/metrics_multi_seed.csv` | 5-seed 聚合指标 |
| Per-seed accuracy | `10-papers/scripts/paper-10/results/accuracy_per_seed.csv` | 逐 seed 准确率 |
| Ablation results | `10-papers/scripts/paper-10/results/ablation_correlated_dims.csv` | Phase D 消融 |
| Projection results | `10-papers/scripts/paper-10/results/benchmark_projection_results.csv` | CBVProjection 基准 |
| Figures | `10-papers/scripts/paper-10/figures/` | figure1-4 (.py + .png) |

---

## Commands for Next Agent

```bash
# 运行全量基准（如需重新生成）
cd 10-papers/scripts/paper-10
python run_benchmark.py

# 运行投影基准
python run_benchmark_projection.py

# 运行消融实验
python analysis/ablation_correlated_dims.py

# 查看当前结果
cat results/metrics_multi_seed.csv
cat results/accuracy_per_seed.csv
```

---

## Important Notes

1. **目标期刊已改为 TNNLS**（非 JMLR）。TNNLS 要求 IEEE 格式、编号章节、正式学术英语。
2. **Phase E 数据是最终数据**。论文中所有数字必须使用 58 数据集 × 5 seeds 的结果，不要使用旧的 31 数据集结果。
3. **CBV 核心结果**: 51.4% ± 0.8% accuracy (rank #2)，Gap Statistic 53.8% ± 1.4%。
4. **互补性是论文最强的概念贡献**，但需要定量支撑（C1 修复）。
5. **聚合理论是最关键的理论缺口**（C2 修复），TNNLS Reviewer 1 标记为 CRITICAL。
6. **不要修改 cbv/ 目录下的代码**，除非 reviewer 要求新的实验。
7. **参考文献有两个列表需要合并**（Part 1 references + Part 2 references），这是必须修复的编辑问题。

---

## Contact Points

- **项目根目录**: `C:\Users\lenovos\academic-research-skills`
- **论文目录**: `10-papers/`
- **代码目录**: `10-papers/scripts/paper-10/`
- **结果目录**: `10-papers/scripts/paper-10/results/`

---

## Session #16 — Stage 1-4 Reviewer Fixes + Polishing (2026-06-22)

### What Was Done
- **Stage 1**: All 7 CRITICAL + 12 MAJOR + 9 MINOR reviewer fixes completed
  - C1: Quantified complementarity (OR-ensemble 67.2%, Jaccard 0.412)
  - C2: Aggregation theory (Proposition 1 + Corollary 1)
  - C3-C7: Algorithm boundary conditions, h_crit logic, seed protocol, "first" claims, references merged
  - M2-M12: τ justification, kernel sensitivity, pairwise tests, title, abstract, practitioner guide
- **Stage 2**: Structural fixes (§1.3/§2.3 merge, literature gaps, Proposition 1 condition, moons contradiction, table numbering)
- **Stage 3**: Consistency fixes (Proposition 1 Δ_j, table references, $k$ rendering bug)
- **Stage 4**: Language quality (fundamentally 6→3, notably 3→0, capitalization, DUD cleanup)

### Key Decisions
- Proposition 1 uses per-dimension Δ_j (not global Δ_min) — matches proof
- CBV is deterministic; 5 seeds control k-means for geometric CVIs only
- Gaussian kernel strongly preferred (60% vs 20% Epanechnikov)
- CBV≈Gap Statistic: p=0.808, statistically indistinguishable

### What Remains
- LaTeX conversion (Markdown → IEEEtran)
- Section numbering (decimal → Roman)
- Equation numbering
- Author/affiliation info
- Abstract trim to ≤200 words
- Figure embedding in manuscript body
- Cover letter + suggested reviewers

### Files Created/Modified
- `10-papers/papers/paper-10-cbv-manuscript-v2.md` — main manuscript (10853 words)
- `10-papers/papers/appendix-content.md` — appendix source
- `10-papers/HANDOVER_F9.md` — handover document
- `10-papers/scripts/paper-10/analysis/complementarity_enhanced.py`
- `10-papers/scripts/paper-10/analysis/tau_sensitivity.py`
- `10-papers/scripts/paper-10/analysis/posthoc_pairwise.py`
- `10-papers/scripts/paper-10/analysis/kernel_sensitivity.py`
- `10-papers/scripts/paper-10/figures/cbv_vs_gap_scatter.png`
- `10-papers/scripts/paper-10/figures/jaccard_complementarity.png`
- `10-papers/scripts/paper-10/figures/complementarity_heatmap.png`
- `10-papers/scripts/paper-10/results/complementarity_matrix.csv`
- `10-papers/scripts/paper-10/results/posthoc_pairwise.csv`
