---
name: revision-20260801-v8-d01-reversal
description: "2026-08-01 三家审计 + 变体 D r≈+0.95 复现失败 → 升级为 §6.4 \"+0.93~0.98\" 全口径不可复现，机制段须重写"
metadata: 
  node_type: memory
  type: project
  originSessionId: d89f53e7-4152-4a37-accc-25193061d82b
---

2026-08-01 三家 agent 全量审计。14 项编辑性修复已中英同步、双版编译 0 error（cos³(10°) 0.977→0.955、p<10⁻³⁴ 方向错、L604 句首、L503 引用、前沿点 SD 76±17、fig:fig5 孤儿、ψ_sq 符号、Das-Dennis p、highlights upper bound + hot-start 限定、off-nadir φ→ξ 解符号过载、32.4%→one-third、KramerMiller pages、零多普勒括注）。

**P0 发现（closed 2026-08-01）**：论文 §6.4 的 "+0.93~0.98 调度正相关 / reversal / active selection" 机制主张不可复现。
- 变体 D 声称 r≈+0.95 → 全量重跑四类全负（−0.44/−0.59/−0.21/−0.18，随密度趋零）
- 物理求解器 A 同口径也全负（S1 −0.69/S2 −0.54/S3 −0.20/S4 −0.17）；跨前沿解（A −0.84~−0.98、D −0.94~−0.98）、跨求解器池化（−0.89）、符号翻转（部分不符）——**无任何口径给出正值**
- +0.93~0.98 生成脚本在 git 两仓库/backup/旧仓库/全部 .py/全部审查报告中不存在；`scripts/r_visible_envelope.py` L107 中为硬编码常量
- f2_f3_coupling.json n 内部不自洽（S3=69,405 vs S4=4,906）

**可复现替代叙事（已写入论文）**：物理目标把包络负相关"削弱"（−0.95→−0.69 稀疏）而非"反转"；D（无物理）稀疏时衰减更弱（−0.44）、密集时与 A 重合（≈−0.18）；密度升高冲突进一步减弱（尺度饱和）。核心三论点（尺度依赖饱和、三目标冗余、热启动条件性）不受影响。

**Why**：headline 机制主张无数据支撑，审稿人复现会翻车；必须重写而非润色。
**How to apply**：已改英 §6.4（经验相关段 + 包络对比段）、§7.1 finding(2)、中 L718-740/L827-834、消融节（英 L136/中 L120 旧叙事残骸"结构属性而非物理引导"已修）；删 reversal/+0.98/Fisher-z 措辞，用可复现对照；f2_f3_coupling.json 加 _deprecated 标注；probe 脚本入库（reproduce_variant_d_r.py、reproduce_A_r.py、probe_cross_solver_pool.py、probe_coupling_caliber.py）；中英双版编译通过。

**Git 状态（2026-08-01 提交完毕，4 commits）**：
- f76e52e P0 机制重写（10 文件，883+/132-）
- 084c1d7 三家审计编辑修复 H1-H14 + 报告归档
- 5c4ec77 清理 review/ 根目录旧报告
- 9d9e0d7 消融节旧叙事残骸修复（自查发现，提交前必须再扫一轮消融节）

**遗留**：① GitHub 仓库暂缓推送（作者决定，pushed_at 仍 2026-07-22）；② 下一步请其他 agent（academic-paper-reviewer / ppw-logic / ppw-de-ai）审查 P0 重写，传 RDR-002 路径 + 改动范围。完整记录见 review/rdr-002-coupling-plus098-unreproducible.md（closed）。注意：求解器 seed=None 有少量随机差异但负号稳健；sar_sim 在 `planning paper/src`，脚本 sys.path 指向缺失目录需 PYTHONPATH。[[revision-20260801-wbv5-traev7]] [[feedback-long-task-checkpointing]]
