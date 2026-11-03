# RDR-003 — G-SM squint argmin 无窗口/无 θ 约束，产生不可行观测

**状态**: 代码 fixed，baselines 重跑完成（200/200），论文文本/表格待重算 → 部分 fixed
**日期**: 2026-08-02
**来源**: 两份 20260802 审查报告（qwen full-audit / trae v11）对抗性验证时人工实跑发现；qwen 🟡-8 指到机制但定级过低，trae §5.6 只提结构不一致
**优先级**: 🔴 P0（投稿阻断）
**代码修复**: `src/sar_sim/solver/baselines.py::_b3_squint_minimize`（commit 待提交）；单测 `src/tests/test_b3_squint_min.py` 4 passed（含新增跨窗口回归）

## 发现原文（qwen 🟡-8，已升级）

> `_b3_squint_minimize` 搜索 `geom_cache.cache[task_idx]` 跨所有窗口的时间网格，而非仅限当前调度的窗口。若任务有多个窗口，可能从另一个窗口选择时间。论文 L503-505 说 "within each visibility window"。

## 实跑核验（experiments/verify_gsm_c3_v2.py，40 场景，G-BL 对照）

`geom_cache` 覆盖整个过境、不过滤窗口与 θ。argmin|ψ_sq| 的数学极值在星下点穿越处：

- 观测被移到 **θ=0.2°–2.0°、不属于任何可见窗口**的时刻（实测 `t_in_some_window=False`）——卫星看不见目标时"安排"了观测；
- cache 自带 θ/ψ 列与独立 `compute_full_attitude` 计算逐条吻合（排除测量假象）；
- G-BL 对照 40/40 场景 xWin=0、C1paper=0、C3big=0。

| 类 | G-SM C3 大违规(>5s) | 受影响场景 | C1 θ∉[15°,50°] | t 落出本窗口 |
|----|----|----|----|----|
| S1 | 2 | 2/10 | 22 | 27 |
| S2 | 59 | 10/10 | 87 | 129 |
| S3 | 143 | 10/10 | 149 | 265 |
| S4 | 199 | 10/10 | 167 | 349 |

S2-A_seed00 重跑 f1=373.00 / f2=0.5276 / f3=0.3211 / nsel=59，与 `baselines_200.json` **逐位吻合** → 论文数据同源。

## 决策

🔴 必须修。代码修（论文 L502-505 描述 = 意图实现；不可行观测无法用"改论文"洗白）。

## 修复方案

`src/sar_sim/solver/baselines.py::_b3_squint_minimize`：
1. argmin 限定在 `obs.window` 自身 [t_start, t_end] 范围内的缓存行；
2. 掩蔽 θ∉[θ_min, θ_max]（instance 级 15°–50°）的行；
3. 窗口内无合格行 → 该观测保持原时刻（pass-through，不跨窗口）。

重跑：`run_baselines_v4.py`（S1–S4, 200）+ `run_baselines_S7S8.py`（Table 5 中间密度）。

## 受污染的论文产物（重算清单）

- Table 2 G-SM 列（f1\*=0.61±0.09, f2=0.506±0.035, f3=0.356±0.075）；
- Table 5 G-SM 行（含 S7/S8）；
- fig2（squint effect 三面板）；
- §6.2 / §6.6 squint 专项：G-SM f3 +34%(S1)/+70%(S4)、Cliff's δ=+0.72（L507-509 直接引用）；
- 统计：Friedman/Wilcoxon 涉及 G-SM 的配对、effect_sizes.json。

**不受影响**：G-BL 列、GA-P-BL、MOEA-2/3（另见 RDR-004）、N₅₀、饱和态主结论。

## 风险

f3 虚高条目（θ→0 处 cos³θ→1）移除后，G-SM vs G-BL 的 f3 差距与 δ=+0.72 **大概率缩水**；squint 专项段文本可能要重写。重跑后才能定量。

## 重跑结果（experiments/results/baselines_200.json，2026-08-02 修后全量）

旧数据备份于 `experiments/results/_backup_pre_rdr003_004_20260802/`。

| 类 | n | n_sel（旧/新） | G-SM f3 旧 | G-SM f3 新 | G-BL f3 新 | G-SM f1* 旧→新 |
|----|----|----|----|----|----|----|
| S1 | 50 | 14.5/14.5 | 0.435 | **0.331** | 0.325 | 0.849→0.848 |
| S2 | 50 | 34.0/34.0 | 0.456 | **0.323** | 0.305 | 0.740→0.733 |
| S3 | 50 | 71.4/71.4 | 0.361 | **0.237** | 0.216 | 0.637→0.633 |
| S4 | 50 | 80.3/80.3 | 0.356 | **0.236** | 0.210 | 0.613→0.607 |

**解读**：n_sel 完全不变（任务集合一样，纯时刻修正），f1* 几乎不变。G-SM vs G-BL f3 改善从旧值 +34%/+50%/+67%/+70% 崩塌为 +2%/+6%/+10%/+12%。即论文的 +34%(S1)/+70%(S4) 和 Cliff's δ=+0.72 **几乎全部是不可见星下点时刻伪造的 cos³θ→1 虚高**，不是 squint minimization 的真实效果。squint 专项段（§6.2/§6.6）+ fig2 + effect_sizes 必重写/重算。

## 验证清单

- [x] 修后 40 场景样本审计：xWin=0、C1paper=0、C3big=0（G-SM）— verify_gsm_c3_v2.py
- [x] 全量重跑 baselines_200.json（200/200），G-SM f3 全 4 类显著回落（见上）
- [ ] 重跑 run_baselines_S7S8.py（Table 5 中间密度 G-SM 行）
- [ ] 重算 Table 2 G-SM 列、fig2、G-SM vs G-BL Cliff's δ
- [ ] 重写 §6.2/§6.6 squint 段文本（+34%/+70%/δ=+0.72 作废，改用新数值）
- [ ] 中英双语同步
- [ ] 双版编译通过
