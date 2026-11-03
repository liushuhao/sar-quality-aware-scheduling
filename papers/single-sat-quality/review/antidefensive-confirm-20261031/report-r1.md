## Part A: 逐处核验表

| # | patch 位置 | 达成目的？ | 引入新问题？ | 主张诚实性 | 证据（引原文＋行号） |
|---|---|---|---|---|---|
| 1 | 摘要尾句；patch 5–12；tex 57–59 | 是。将较弱的 “delimits” 改为更积极的 “maps … most benefits”。 | 未见。 | 未越界。“empirical, conditional” 保留，且前文分别给出稀疏增益与稠密低于 2% 的证据，足以支持密度间比较。 | “These results establish an empirical, conditional saturation regime that maps when physics-aware multi-objective scheduling most benefits single-satellite SAR operations.”（57–59） |
| 2 | 引言求解器概述；patch 16–23；tex 126–133 | 是。删除引言中的重复实现结果。 | 未见；指代和列举完整。 | 未越界。保留的 “never worse” 仍由回退守卫直接保证；199/200 的信息在方法和结果节仍完整存在。 | “that returns the greedy schedule whenever it fails to improve profit, so it is never worse than G-BL”（128–130）；“identical to G-BL in 199 of 200 scenarios”（665–666）。 |
| 3 | 引言贡献 1；patch 26–38；tex 155–165 | 是。将 “tested search” 前移至总限定语，删除句尾重复。 | 未见。 | 未越界。“under the tested search and configuration” 在贡献项开头限定整个机制与高密度结论，作用域没有丢失。 | “single-pass, single-satellite Stripmap setting under the tested search and configuration”（157–159）；“from the two-objective one at high densities”（163–164）。 |
| 4 | HV 计算段；patch 41–48；tex 819–825 | 是。删除已经由前句表达的点数 caveat。 | 未见。 | 未越界。“cardinality caveat” 和对应节引用均保留。 | “subject to the cardinality caveat stated above and detailed in \S~\ref{sec:pareto-coupling}.”（824–825） |
| 5 | HV 表注；patch 52–57；tex 943–945 | 是。压缩表注中的重复解释。 | 未见。 | 未越界。表注仍明确点名 “point-count asymmetry discussion”，并非删除限定后把 HV 当成独立质量判据。 | “single-point solvers G-SM and GA-P-BL are omitted; see the point-count asymmetry discussion in \S~\ref{sec:pareto-coupling}”（945）。 |
| 6 | Pareto 前沿限定；patch 61–70；tex 1302–1303 | 是。将较长的不可最优性自白压缩为直接限定。 | 未见。 | 未越界。必要的 “approximate fronts” 与 “under the tested search budget” 两项限定都保留；没有改称真实或最优 Pareto 集。 | “The Pareto fronts reported here are approximate fronts obtained via NSGA-III under the tested search budget.”（1302–1303） |
| 7 | 热启动控制；patch 74–81；tex 1334–1340 | 是。删除“我们没有构造”的过程性自白，保留结果解释边界。 | 未见；长句衔接成立。 | 未越界。“could extend” 仍表明合并前沿只是可能性，“anchored-front values rather than envelope maxima” 完整保留。 | “so the sparse-regime margins are anchored-front values rather than envelope maxima.”（1339–1340） |
| 8 | 扰动敏感性；patch 84–92；tex 1352–1368 | 是。删除对同一适用范围的重复说明。 | 未见。 | 未越界。“S3 scenarios only” 仍直接限定整个 sweep；新增句只是说明高密度不变性为何在该类上检验，没有把结论扩展到稀疏区。 | “This sweep was run on S3 scenarios only (the dense transition class), the regime in which the invariance claim operates.”（1364–1366） |
| 9 | 随机搜索校准；patch 96–102；tex 1370–1378 | 是。删除本段并未主张的机制归因 caveat。 | 未见。 | 未越界。段落仍只说 “bounds”，且 “unconstrained”“on these scenarios” 两个口径均保留，没有声称识别 MOEA 优势来源。 | “the contrast bounds what unstructured selection achieves on these scenarios.”（1377–1378） |
| 10 | 搜索预算控制；patch 106–113；tex 1403–1417 | 是。删除未报告收敛轨迹的主动递刀句。 | 未见。 | 未越界。十倍场景范围、双倍预算对照和 “conditional on the tested budget” 均保留；没有升格为普遍收敛保证。 | “on the same ten scenarios”（1412–1413）；“the quality claims are understood as conditional on the tested budget.”（1416–1417） |
| 11 | 限制节的时效性句；patch 116–127；tex 1610–1613 | **未完全达成。** 精简了 caveat，但同时改变了事实主体。 | **MAJOR：把仅属于 G-BL 的最早可行时刻放置泛化为所有任务。** | **越界。** 新句与 G-SM 的最小斜视时刻选择及质量导向解可延迟观测的正文描述直接矛盾。 | 新句：“with each task placed at its earliest feasible time”（1611–1612）。反证：“placed at the discretized time step that minimizes squint angle”（633–635）；“quality-steering solutions may delay acquisitions to reach lower-squint geometry”（1549–1551）。 |
| 12 | 结论；patch 131–146；tex 1633–1657 | 是。两处删除均压缩重复 caveat；结论主线更集中。 | 未见。 | 未越界。近似性仍由 “found front”“under the tested search” 承载；覆盖收敛的热启动条件保留。删去的相关系数分类属于证据细分，结论整体仍明确限定为 G-BL-seeded 搜索。 | “compressing the found front”（1645）；“under the tested search”（1648–1649）；“Coverage convergence toward the G-BL reference is conditional on the hot start”（1650–1652）；“in G-BL-seeded MOEA formulations”（1633–1635）。 |

## Part B: 扩展扫描发现

### MAJOR-1 — 限制节引入内部事实矛盾

- **位置**：§7.4 Limitations，tex 1610–1613。
- **原文**：“The utility model also optimizes quality and quantity at a fixed timeliness operating point, with each task placed at its earliest feasible time; explicit latency and urgency objectives are left to future work.”
- **理由**：patch 原句将最早可行放置明确归于 “the greedy baseline”；修改后该限定消失，变成所有任务均如此。正文明确说明 G-SM 选择最小斜视时刻（632–645），质量导向解也可能延迟观测（1547–1552）。这不是单纯措辞弱化，而是本批新引入的事实错误。
- **建议**：改为：  
  “The utility model also optimizes quality and quantity without explicit latency or urgency objectives, which are left to future work; G-BL places tasks at their earliest feasible times, whereas quality-steering solvers may delay acquisitions.”

### NOTE-1 — 引言标签不再被回引，但无内容或编译问题

- **位置**：`sec:introduction` 标签在 tex 69。
- **事实**：patch 删除了限制节中的 `\S~\ref{sec:introduction}`；修改后全文仅剩 `\label{sec:introduction}`，没有其他 `\ref{sec:introduction}`。
- **判读**：这是一个未使用标签，不是悬空引用，不会造成 LaTeX 引用错误，也不影响论证。无需为了保留回引而恢复被删句。

其余扩展扫描未见问题：

- 摘要（51–52）、引言（150–151）、结论（1650–1652）均保留热启动条件；摘要和引言对受控 \(+4.9\%\) 边际及 knee-rule 条件的表述也一致。
- 本批涉及的 `sec:pareto-coupling`、`sec:robustness-calibration` 引用仍有其他承载，未出现引用目标丢失。
- 除第 11 处外，未见删句造成的句法残缺、指代悬空、段落断裂或别扭重复。
- 未见保留数值被改写；近似前沿、热启动作用域等必要限定仍可由修改后全文回收。

## Verdict

**FAIL** — 其余 11 处均达成反防御精简目的且未削弱必要限定，但第 11 处把贪婪基线的观测时刻规则错误泛化到全部任务，修正前不应通过确认轮。
