# Paper #10 — Final Results Roadmap

> 方法论审查后待办事项清单（优先级排序）

---

## P0：必须完成（最终结果质量）

### P0-1：添加统计显著性检验
- **问题**：当前仅计算准确率和平均排名，无 Friedman 检验 / Nemenyi 事后检验
- **方案**：在 `benchmark/runner.py` 的 `summarize_results()` 中添加：
  - `scipy.stats.friedmanchisquare()` — 检验各指标间是否有显著差异
  - `scikit-posthocs.posthoc_nemenyi_friedman()` — 若显著则进行事后两两比较
  - 输出 Friedman p 值 + Nemenyi 临界差图数据
- **影响**：为 CBV 排名第 4 位提供统计支持，判断其与 Gap/CH 的差距是否显著
- **依赖**：需要 `scikit-posthocs` 包（`pip install scikit-posthocs`）

### P0-2：DUD Index 问题处理
- **问题**：DUD 始终选择 k=10（搜索范围上限），准确率 0%，因为其得分随 k 单调递增
- **方案**：在论文中说明 DUD Index 是为**固定 k 下的聚类比较**设计的（而非 k 估计），将其从主要排名中剔除，放入附录作为参考
- **任务**：
  - 修改 `run_benchmark.py`：在正式基准中排除 DUD
  - 可选：在附录中单独报告 DUD 的表现
- **影响**：CBV 排名方法从 4/7 → 4/6（去掉 DUD 不会改变其他指标的相对位置）

### P0-3：添加 Seeds 数据集
- **描述**：UCI Seeds 数据集（210×7, k=3），加载器已实现但被排除
- **方案**：在 `benchmark/real_data.py` 中启用 `include_seeds=True` 或修改 `load_all()` 方式
- **影响**：真实数据集从 5 个 → 6 个

### P0-4：Benchmark 重跑
- **描述**：在完成上述三项 P0 后，重新运行完整基准测试
- **方案**：`cd 10-papers/scripts/paper-10 && uv run python run_benchmark.py`
- **预计时间**：~7-8 分钟（436s）

### P0-5：可复现性确认
- **问题**：确认 random_state 是否传导至所有随机组件
- **检查结果**：✅ CBVSpectral 已将 `random_state` 传递给 `SpectralEmbedding`（第 92 行），也传递给 `CBVIndex`（第 78 行）
- **结论**：无需改动

---

## P1：重要优化（论文完整性）

### P1-1：超额质量（Excess Mass）层优化
- **问题**：`use_excess_mass=True` 在 benchmark 中无效（当前设置为 False）
- **发现**：`excess_mass()` 在 `n_boot=0` 时始终返回 `n_modes=1`（点估计无法区分多模态），需要 `n_boot>=50` 才有效，但会引入 ~45000 次额外 bootstrap 调用
- **方案**：
  1. 论文中将 excess mass 标注为"已实现但计算成本高，留作未来优化"
  2. 可选：在附录中展示小规模验证（在 3-5 个数据集上用 n_boot=50 测试高 k 场景的改善效果）
- **影响**：不影响最终 benchmark 结果，仅影响论文叙述

### P1-2：失败模式文档化
- **描述**：6 类失败模式需要系统记录到论文中
- **任务**：
  - 合成数据：按类别分类失败数据集
  - 每类给出 1 个典型案例解释
  - 非凸形状（moons/circles）：CBV → 始终得 k=3，Gap 正确但 Silhouette/CH/DB 也失败
  - 高 k 低估（k≥5）：CBV 在 k=3-4 卡住
  - 记录为论文 §Results / §Discussion 内容
- **文件**：`10-papers/papers/paper-10-cluster-validation.md`

---

## P2：文档与提交

### P2-1：更新 Paper 参考文档
- **内容**：
  - 替换 §Next Steps 为最终状态（所有步骤完成）
  - 添加最终实验结果（accuracy table + ranking + failure analysis）
  - 添加统计检验结果
  - 更新论文贡献声明：CBV 准确率 43.3%，排名 4/6

### P2-2：更新 handover.md
- **内容**：记录本次方法论审查 + 最终结果确认

### P2-3：Git 提交
- **提交内容**：
  - `10-papers-framework.md`
  - `10-papers/` 整个目录（所有代码、结果、文档）
  - 包含准确的提交信息

---

## 执行顺序

```
P0-1 (统计检验) ─┐
P0-2 (DUD处理)   ├→ P0-4 (重跑基准) → P1-2 (失败分析) → P2-1 (论文doc) → P2-2 (handover) → P2-3 (提交)
P0-3 (Seeds)    ┘     │
                      P1-1 (excess mass doc)
```
