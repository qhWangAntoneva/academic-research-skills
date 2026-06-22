# Handover Document — Paper #10 (CBV) TNNLS Submission

**Handover date:** 2026-06-22
**From:** Session #16 agent (Stages 1-4 polishing)
**To:** Next agent section (LaTeX Conversion + Submission)

---

## Executive Summary

论文 v2 已完成 4 轮打磨（Stage 1-4），从 8253 词扩展到 10853 词。所有 reviewer CRITICAL/MAJOR/MINOR 修复项已完成（除 LaTeX 格式转换）。当前状态：Markdown 格式，内容完整，语言质量达标。下一步是 LaTeX 转换 + TNNLS 格式适配 + 最终提交。

---

## What Was Done in This Section (Sessions #16, Stages 1-4)

### Stage 1 — Reviewer CRITICAL+MAJOR+MINOR Fixes (7 CRITICAL + 12 MAJOR + 9 MINOR)
- **C1**: 量化互补性 — OR-ensemble 67.2%, Jaccard 0.412, 逐数据集矩阵, 3张图
- **C2**: 聚合理论 — Proposition 1 + Corollary 1 + Remarks
- **C3**: Algorithm 1 边界情况 — 常量维度跳过 + 默认行为 + clamp
- **C4**: h_crit 阈值逻辑重写 — Intuition/Threshold/Sequential 三段式
- **C5**: seed/n_init 协议 — CBV 确定性说明
- **C6**: "首创"限定 — 改为 "using critical bandwidth modality testing"
- **C7**: 参考文献合并 — 删除 Part1, [10]=Krzanowski, [23]-[27]补全作者
- **M2**: τ=15 证明 + 容差曲线表 (Table I)
- **M3**: 核函数敏感性 — Gaussian 60% >> Epanechnikov 20% >> Triangular 15% >> Uniform 0%
- **M4**: Wilcoxon+Holm-Bonferroni — CBV≈Gap (p=0.808)
- **M6**: 逐数据集结果表 (补充材料)
- **M9**: 标题 → "Critical Bandwidth Modality Testing for Estimating the Number of Clusters"
- **M10**: Abstract 重构 (Problem→Gap→Method→Results→Impact)
- **M12**: §6.6 实践者指南

### Stage 2 — Structural + Content Fixes
- §1.3/§2.3 冗余合并 (§2.3 现在讲 "目标 disconnect" 新内容)
- §2.1 补充稳定性方法 (Ben-Hur, Tibshirani) + 深度学习方法 (DEC, VaDE)
- Proposition 1 条件修复 (Δ_min→Δ_j per-dimension)
- Appendix A 完整证明
- moons 矛盾解决 (CBV 成功, circles 失败)
- Table I-VII 顺序编号
- 预处理细节 (z-score), Gap 数字说明

### Stage 3 — Consistency Fixes
- §1.3/§2.3 残余冗余彻底解决
- §2.1 $k$ 渲染 bug 修复
- Proposition 1 主文与 Appendix 一致 (Δ_j)
- Table 引用编号修正

### Stage 4 — Language Quality
- "fundamentally" 6→3, "notably" 3→0
- 大小写统一 (Hartigan Statistic, Jump Statistic)
- 孤立 DUD 引用清理
- 结论 "Critically" → "Importantly" 避免重复

---

## What Remains for Next Agent (LaTeX Conversion + Submission)

### 第一优先级 — LaTeX 转换
1. **Markdown → LaTeX 转换** — 使用 IEEEtran 模板
2. **章节编号** — decimal (1, 1.1) → Roman (I, I-A)
3. **公式编号** — 添加 \begin{equation} + \label
4. **表格** — Markdown → LaTeX tabular 环境
5. **算法** — 伪代码 → algorithm/algorithmic 环境
6. **交叉引用** — §2.3 → \ref{sec:gap}

### 第二优先级 — 内容适配
7. **作者/机构信息** — 需用户提供
8. **Abstract 截断** — ~250词 → ≤200词
9. **图表嵌入正文** — 当前仅在补充材料, 需嵌入 5-8 张图
10. **Word count 检查** — 确保 ≤12000 词 (含参考文献)

### 第三优先级 — 提交准备
11. **补充材料打包** — S1(逐数据集表), S2(互补性矩阵), S3(图表)
12. **Cover letter 起草**
13. **建议审稿人列表**

---

## Key Files

| File | Location | Status |
|------|----------|--------|
| HANDOVER.md | `10-papers/handover.md` | Session log (sessions #1-#15) |
| **Manuscript v2** | `10-papers/papers/paper-10-cbv-manuscript-v2.md` | **主文件, 10853词, 完整** |
| Appendix content | `10-papers/papers/appendix-content.md` | 附录源文件 |
| Reviewer feedback | `10-papers/papers/reviewer-feedback-summary.md` | 3-Reviewers 汇总 |
| CBV core | `10-papers/scripts/paper-10/cbv/index.py` | CBVIndex + sheather_jones_bandwidth |
| CBVHybrid | `10-papers/scripts/paper-10/cbv/hybrid.py` | CBVHybrid |
| CBVProjection | `10-papers/scripts/paper-10/cbv/projection.py` | CBVProjection |
| Benchmark runner | `10-papers/scripts/paper-10/run_benchmark.py` | 全量基准脚本 |
| **分析脚本** | | |
| 互补性分析 | `10-papers/scripts/paper-10/analysis/complementarity_enhanced.py` | C1 分析 |
| τ 敏感性 | `10-papers/scripts/paper-10/analysis/tau_sensitivity.py` | M2 分析 |
| 事后成对比较 | `10-papers/scripts/paper-10/analysis/posthoc_pairwise.py` | M4 分析 |
| 核函数敏感性 | `10-papers/scripts/paper-10/analysis/kernel_sensitivity.py` | M3 分析 |
| **结果文件** | | |
| 多seed指标 | `10-papers/scripts/paper-10/results/metrics_multi_seed.csv` | 10指标×58数据集 |
| 逐数据集结果 | `10-papers/scripts/paper-10/results/per_dataset_results.csv` | 58×10 矩阵 |
| 逐seed准确率 | `10-papers/scripts/paper-10/results/accuracy_per_seed.csv` | 5 seed |
| 互补性矩阵 | `10-papers/scripts/paper-10/results/complementarity_matrix.csv` | C1 输出 |
| 事后比较 | `10-papers/scripts/paper-10/results/posthoc_pairwise.csv` | M4 输出 |
| **图表** | | |
| CBV vs Gap 散点 | `10-papers/scripts/paper-10/figures/cbv_vs_gap_scatter.png` | C1 图 |
| Jaccard 柱状图 | `10-papers/scripts/paper-10/figures/jaccard_complementarity.png` | C1 图 |
| 正确性热图 | `10-papers/scripts/paper-10/figures/complementarity_heatmap.png` | C1 图 |
| 准确率对比 | `10-papers/scripts/paper-10/figures/figure1_accuracy_comparison.png` | 原有图 |
| 排名分布 | `10-papers/scripts/paper-10/figures/figure2_rank_distribution.png` | 原有图 |
| 一致性矩阵 | `10-papers/scripts/paper-10/figures/figure3_agreement_matrix.png` | 原有图 |
| 失败分类 | `10-papers/scripts/paper-10/figures/figure4_failure_categories.png` | 原有图 |

---

## Commands for Next Agent

```bash
# 查看当前论文状态
wc -w 10-papers/papers/paper-10-cbv-manuscript-v2.md
git log --oneline -5

# 运行全量基准（如需重新生成）
cd 10-papers/scripts/paper-10
python run_benchmark.py

# 运行互补性分析
python analysis/complementarity_enhanced.py

# 运行事后成对比较
python analysis/posthoc_pairwise.py

# 查看当前结果
cat results/metrics_multi_seed.csv
cat results/accuracy_per_seed.csv

# 生成图表
cd figures
python figure1_accuracy_comparison.py
python figure2_rank_distribution.py
```

---

## Important Notes

1. **目标期刊 TNNLS** — IEEE 格式, Roman 章节编号, 编号公式
2. **论文 10853 词** — 接近 TNNLS 12000 词上限, LaTeX 转换后需检查
3. **所有数字基于 58 数据集 × 5 seeds** — 不要使用旧的 31 数据集结果
4. **CBV 核心结果**: 51.4% ± 0.8% accuracy (rank #2), Gap 53.8% ± 1.4%
5. **CBV≈Gap 统计等价**: p=0.808, 无显著差异
6. **互补性是主要贡献**: OR-ensemble 67.2%, CI=0.667
7. **不要修改 cbv/ 目录下的代码** — 除非 reviewer 要求新实验
8. **Git: 领先 origin/main 15 commits** — LaTeX 转换后需 push

---

## Session History (from handover.md)

| Session | Phase | Key Result |
|---------|-------|------------|
| #1-#5 | Research + Architecture | CBV concept, critband package |
| #6 | Peer Review | EIC Major Revision |
| #7-#9 | Phase A-C | Mode rename, tolerance calibration, benchmark expansion |
| #10-#12 | Phase D-E | SJ bandwidth, CBVProjection, full 58-dataset benchmark |
| #13-#15 | Phase F-1~F-8 | Manuscript v2 (8253词), TNNLS review |
| #16 | Stage 1-4 | Reviewer fixes + polishing (10853词) |

---

## Contact Points

- **项目根目录**: `C:\Users\lenovos\academic-research-skills`
- **论文目录**: `10-papers/`
- **代码目录**: `10-papers/scripts/paper-10/`
- **结果目录**: `10-papers/scripts/paper-10/results/`
