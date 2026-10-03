---
name: paper2-cv-dust-seed-assert
description: paper2 预存缺陷（2026-09-29 审计发现，未修）——anchor fits 容差 1e-12 与种子 cv 严格 ==0.0 断言冲突，M2WH/M3NC 种子 cv 尘 ~1e-14 必崩 run_pilot；阻断 W/H 全量矩阵
metadata:
  node_type: memory
  type: project
  originSessionId: 8e4b1146-8eb8-43ab-9cd0-63bf039c5442
  modified: 2026-09-28T22:49:19.912Z
---

paper2 票 13 独立审查（2026-09-29）中修复设计审查员发现的**预存缺陷**（非成员性闸引入，修复前后逐位同）：

`anchor.py fits()` 允许 `gap ≥ need − 1e-12`，而 `nsga2.py:165` 对锚种子个体断言 `ev["cv"] == 0.0`（严格浮点等）。锚 starts 恰落 C2 边界时，`SchedulingProblem.evaluate` 的 `max(0, req−gap)` 产出 cv 尘（实测 M2WH 种子 1.4e-14、M3NC 7.1e-15）→ 断言崩 → `run_pilot` 中止。

**Why:** W/H 全量实验矩阵（5 变体 × 10 seed）跑到 M2WH/M3NC 时必撞（M1NC 不触发——pilot 只跑过 M1NC）。修复需独立裁决：evaluate 侧加 ε 地板（改全局 CV 语义，影响所有候选）vs 种子断言放容差（cv ≤ 1e-9，但真违约种子也可能溜过）——两方案各有回归面，不并入票 13。

**How to apply:** 开实验矩阵**前**必须先修此缺陷（新票，T1）。修复时同步考虑：fits 的 1e-12、encode round-trip 的 1e-9、断言容差三者的一致容差链（单一 ε 登记处）。相关 [[paper2-independent-audit-20260929]]。

**【已修复 2026-09-29，票 14，commit d23026b】**：终设计 = A+B 混合（B-only 被 pymoo 内部严格 CV==0 可行过滤证伪——W/H 前沿会空）：evaluator C2_TOL_S=1e-12 源头地板为主 + nsga2 消费带 1e-9。M2WH 生产 pilot 首跑 exit 0 = 阻断解除。本条保留作故障模式记录，索引行已移出。
