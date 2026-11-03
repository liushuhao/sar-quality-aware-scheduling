## 复测结论

修复后的 timeliness 句与 §7.2、§4.2 和 §4.3 一致，原有歧义已关闭：

- §7.4 仅陈述“没有显式延迟或紧急度目标，未把时效性作为独立调度维度评价”（tex 1610–1612），不再声称所有任务均采用最早可行时刻，也不再假设存在固定的 timeliness 操作点。
- §7.2 将最早可行放置明确限定于 G-BL，并说明 quality-steering 可能延迟观测（tex 1547–1552）。
- §4.2 描述 G-BL 的最早可行插入及必要延迟（tex 619–626）；§4.3 描述 G-SM 选择最小斜视时刻（tex 631–645）。三者不再相互冲突。
- 新句语法完整，与前后 limitations 衔接自然，无同义反复或新增夸大宣称。

## Part A: 逐处核验表

| # | patch 位置 | 达成目的? | 引入新问题? | 主张诚实性 | 证据(引原文+行号) |
|---|---|---|---|---|---|
| 1 | 摘要，`delimits`→`maps ... most benefits` | 是，贡献表达更直接 | 无 | 保留经验性与条件性，没有扩大为普适优势 | “an empirical, conditional saturation regime that maps when ... most benefits”（57–59）；稀疏与高密度收益已在42–57限定 |
| 2 | 引言 GA-P-BL，删重复199/200细节 | 是，减少实现流水细节 | 无 | 保留保护机制的准确含义；具体计数仍在方法节 | “returns the greedy schedule whenever it fails to improve profit, so it is never worse than G-BL”（128–130）；“identical to G-BL in 199 of 200 scenarios”（665–667） |
| 3 | 贡献1，上移 tested-search 限定 | 是，限定覆盖整项贡献，避免重复 | 无 | 仍明确限定搜索、配置及 class means，并保留高密度逐场景残余优势 | “under the tested search and configuration”（158–159）；“indistinguishable in class means”（163–165） |
| 4 | §5.3 HV 段，删重复基数说明 | 是 | 无 | cardinality caveat 未删除 | “subject to the cardinality caveat stated above and detailed in \S~\ref{sec:pareto-coupling}”（823–825） |
| 5 | HV 表注压缩 | 是，表注更简洁 | 无 | 仍明确单点/多点不对称及讨论位置 | “see the point-count asymmetry discussion in \S~\ref{sec:pareto-coupling}”（945） |
| 6 | §6.4 Pareto front 限定压缩 | 是，删除额外不可解性展开 | 无 | approximate 与 tested-budget 两个关键限定均保留，未暗示已验证最优 | “approximate fronts obtained via NSGA-III under the tested search budget”（1302–1303） |
| 7 | Hot-start control，删 merged-front 过程句 | 是 | 无 | 仍承认合并前沿可能扩展，并将结果限定为 anchored-front values | “could extend the quality--coverage envelope beyond either run alone”（1335–1338）；“anchored-front values rather than envelope maxima”（1339–1340） |
| 8 | Perturbation sensitivity，压缩适用范围 | 是 | 无 | S3-only 的测试范围仍明示，未向稀疏 regime 外推 | “This sweep was run on S3 scenarios only ... the regime in which the invariance claim operates”（1364–1366） |
| 9 | Random-search calibration，删额外自否定 | 是 | 无 | 仍明确是 tested batch 的经验界限而非构造保证 | “an empirical bound on the tested batch rather than a construction guarantee”（1374–1376）；“bounds what unstructured selection achieves”（1377–1378） |
| 10 | Search-budget control，删 convergence-trace 附注 | 是 | 无 | 同样本范围及预算条件保留，未宣称完整收敛证明 | “on the same ten scenarios”（1412–1413）；“conditional on the tested budget”（1415–1417） |
| 11 | ceaf935 Limitations timeliness 初改 | 终态达成；初改的误泛化已由#13/#14纠正 | 终态无 | 终态只声明实际优化目标与评价范围 | “without an explicit latency or urgency objective”（1610–1612） |
| 12 | 结论压缩 approximate-front 与相关性附注 | 是 | 无 | 结论仍保留 tested configuration、tested search、hot-start 和适用密度范围；近似前沿限定仍在§6.4 | “under the tested configuration”（1632–1635）；“under the tested search”（1646–1648）；“conditional on the hot start”（1649–1651）；“N=20--500”（1655–1656） |
| 13 | 16a972b，删除“每个任务均最早可行放置” | 部分达成：关闭了错误泛化；`fixed timeliness operating point` 的残留歧义由#14关闭 | 终态无 | 被删除的全求解器放置断言没有恢复 | 当前句仅保留“without an explicit latency or urgency objective”（1610–1612） |
| 14 | 6f2561a，重写 timeliness 句 | 是，彻底移除固定操作点假设 | 无衔接、语法或重复问题 | 与求解器实际行为一致，也没有把定性讨论冒充延迟测量 | “acquisition timeliness is therefore not evaluated as a separate scheduling dimension and is left to future work”（1611–1612）；§7.2“by construction rather than by a measured latency figure”（1547–1549） |

## Part B: 扩展扫描发现

未发现 CRITICAL、MAJOR 或 MINOR 问题。

- **摘要—引言—结论一致**：三者均将核心结论限定为经验性的密度相关饱和；摘要保留“empirical, conditional”（57–59），引言保留“conditional on the G-BL hot start”（147–151），结论保留 tested search、hot-start 和密度范围（1632–1656）。
- **双向限定检查通过**：approximate-front（1302–1303）、S3-only（1364–1366）、tested-batch empirical bound（1374–1378）、tested-budget（1415–1417）、hot-start conditional（1649–1651）均未被删光。
- **交叉引用承载正常**：HV 两处说明均指向既有的 `sec:pareto-coupling`（824–825、945；标签位于1082）；结论 hot-start 限定指向既有的 `sec:robustness-calibration`（1649–1651；标签位于1308–1309）。
- **拼接与间接波及面正常**：各 hunk 前后未见断句、重复限定或语义跳变；G-BL 的最早可行放置仍只归属于 G-BL，未波及 G-SM 或 MOEA 描述。

## Verdict

PASS — timeliness 歧义已完全关闭，三波修改的终态未引入新问题，必要的条件性、近似性与测试范围限定均得到保留。
