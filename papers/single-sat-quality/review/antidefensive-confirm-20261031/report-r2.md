## 复测结论

1. **事实错误已修复。** 当前 Limitations 句为：“The utility model also optimizes quality and quantity at a fixed timeliness operating point; explicit latency and urgency objectives are left to future work.”（§7.4，tex 1610–1612）。它已删除“所有任务均在最早可行时刻放置”的全称断言，不再与 G-BL、G-SM 的不同放置行为冲突：
   - G-BL：“greedily inserted into the schedule at their earliest feasible time”（§4.2，tex 619–620）。
   - G-SM：“placed at the discretized time step that minimizes squint angle”（§4.3，tex 633–635）。

2. **范围披露保留，且与 Discussion 一致。** “explicit latency and urgency objectives are left to future work”（tex 1611–1612）仍明确披露未优化显式时效目标。Discussion 同样区分：“G-BL places each task at its earliest feasible time within the visibility window, whereas quality-steering solutions may delay acquisitions to reach lower-squint geometry”（§7.2，tex 1548–1551）。两处不再矛盾。

3. **未引入衔接、语法或重复问题。** 分号连接两个完整独立分句；后句 “The reference-point counts of MOEA-2 and MOEA-3 differ by construction”（tex 1612–1613）顺利转入下一项限制，无残缺指代或拼接重复。

## Part A: 逐处核验表

| # | patch 位置 | 达成目的? | 引入新问题? | 主张诚实性 | 证据(引原文+行号) |
|---|---|---|---|---|---|
| 1 | 摘要尾句，tex 57–59 | 是，以 “maps … most benefits” 强化价值表达。 | 未见。 | 未越界；“empirical, conditional” 保留，稀疏增益与稠密低增益均在前文给出。 | “These results establish an empirical, conditional saturation regime that maps when physics-aware multi-objective scheduling most benefits single-satellite SAR operations.”（57–59） |
| 2 | 引言求解器概述，tex 126–133 | 是，删除重复实现结果。 | 未见，列举和括号完整。 | 未越界；“never worse” 仍由回退守卫保证，199/200 在方法节保留。 | “that returns the greedy schedule whenever it fails to improve profit, so it is never worse than G-BL”（128–130）；“identical to G-BL in 199 of 200 scenarios”（665–666）。 |
| 3 | 引言贡献 1，tex 155–165 | 是，合并重复的搜索预算限定。 | 未见。 | 未越界；总限定语仍覆盖整个贡献项，高密度逐场景残余优势也保留。 | “under the tested search and configuration”（158–159）；“a trace per-scenario radiometric advantage persists even at the densest class”（165）。 |
| 4 | HV 计算段，tex 819–825 | 是，删除重复的点数解释。 | 未见。 | 未越界；cardinality caveat 和详解引用均保留。 | “subject to the cardinality caveat stated above and detailed in \S~\ref{sec:pareto-coupling}.”（824–825） |
| 5 | HV 表注，tex 943–945 | 是，压缩表注。 | 未见。 | 未越界；仍明确提示 point-count asymmetry，未把 HV 升格为独立质量判据。 | “see the point-count asymmetry discussion in \S~\ref{sec:pareto-coupling}”（945）。 |
| 6 | Pareto 前沿限定，tex 1302–1303 | 是，以直接限定替代较长自白。 | 未见。 | 未越界；“approximate fronts” 和 “tested search budget” 两项关键限定均保留。 | “The Pareto fronts reported here are approximate fronts obtained via NSGA-III under the tested search budget.”（1302–1303） |
| 7 | 热启动控制，tex 1334–1340 | 是，删除“未构造合并前沿”的过程性表述。 | 未见；“so” 的因果衔接成立。 | 未越界；合并前沿仍只是 “could extend”，并保留 anchored-front 而非 envelope-maximum 的边界。 | “could extend the quality--coverage envelope beyond either run alone”（1336–1337）；“the sparse-regime margins are anchored-front values rather than envelope maxima”（1339–1340）。 |
| 8 | 扰动敏感性，tex 1352–1368 | 是，删除重复适用范围说明。 | 未见。 | 未越界；“S3 scenarios only” 仍限定实验范围，没有扩展为稀疏区结论。 | “This sweep was run on S3 scenarios only (the dense transition class), the regime in which the invariance claim operates.”（1364–1366） |
| 9 | 随机搜索校准，tex 1370–1378 | 是，删除本段未主张的机制归因 caveat。 | 未见。 | 未越界；“unconstrained”“on these scenarios” 和 “bounds” 均保留，没有声称识别 MOEA 优势来源。 | “Because the random sampler is unconstrained and does not enforce C2--C4”（1374–1375）；“the contrast bounds what unstructured selection achieves on these scenarios”（1377–1378）。 |
| 10 | 搜索预算控制，tex 1403–1417 | 是，删除未报告收敛轨迹的主动递刀句。 | 未见。 | 未越界；十场景、双倍预算及 tested-budget 条件均保留，未形成普遍收敛保证。 | “on the same ten scenarios”（1412–1413）；“the quality claims are understood as conditional on the tested budget”（1416–1417）。 |
| 11 | Limitations 时效性句，tex 1610–1612 | **是，第二波修复后达成。** | R1 的全称放置错误已消除，未见新问题。 | 诚实；不再把 G-BL 的放置规则泛化到 G-SM 或质量导向解，时效目标缺口仍明确披露。 | “The utility model also optimizes quality and quantity at a fixed timeliness operating point; explicit latency and urgency objectives are left to future work.”（1610–1612） |
| 12 | 结论，tex 1632–1656 | 是，压缩重复 caveat 和证据细分。 | 未见。 | 未越界；“found front”“tested search”“conditional on the hot start” 及 G-BL-seeded 范围均保留。 | “compressing the found front”（1644）；“under the tested search”（1647–1648）；“Coverage convergence toward the G-BL reference is conditional on the hot start”（1649–1651）。 |

## Part B: 扩展扫描发现

**未发现新增 CRITICAL、MAJOR 或 MINOR 问题。**

- **摘要—引言—结论一致：** 三处均保留热启动条件。摘要为 “conditional on greedy hot-start initialization”（50–52），引言为 “This convergence is conditional on the G-BL hot start”（150–151），结论为 “conditional on the hot start”（1649–1651）。摘要与引言对受控 \(+4.9\%\) 边际也均明确附带 radiometric-aware knee-rule 条件（47–48、139–143）。
- **修改区域衔接：** 12 个 hunk 前后未见句法残缺、悬空指代、别扭重复或段落逻辑断裂；第 11 处修复后的前后句衔接正常。
- **交叉引用：** 本批涉及的 `sec:pareto-coupling` 和 `sec:robustness-calibration` 均有有效标签及多处回引。`sec:introduction` 现仅剩标签（69），属于未使用标签而非悬空引用，不影响内容或编译，无需处理。
- **间接波及面：** 删除的近似前沿、搜索预算、热启动和点数限制均仍能在相应正文或结论中回收；未见本批删减造成必要限定丢失或宣称扩大。

## Verdict

**PASS** — R1 的 timeliness 事实矛盾已关闭；12 处修改均达成精简目的并保留必要限定，复测与全量回归未发现新增须修问题。
