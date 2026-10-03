---
name: feedback-verify-hardcoded-numbers
description: 论文/分析中的具体数值必须能回源到生成脚本或原始数据，硬编码数字是事故温床
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d89f53e7-4152-4a37-accc-25193061d82b
  modified: 2026-08-10T05:17:49.595Z
---

审查论文/分析时，任何具体数值（相关、p 值、百分比、系数）都要能**回源**到：① 生成它的脚本；② 原始数据文件；③ 至少一个可独立复算的口径。三者皆无 → 该数字视为不可复现，优先标废弃而非保留。

2026-08-01 事故：论文 §6.4 的 "+0.93~0.98 调度正相关" 是 headline 机制主张的支柱，但生成脚本在 git 两仓库/backup/旧仓库/全部 .py 都不存在，且在 `r_visible_envelope.py` L107 中是**硬编码常量**（`"r_solver_empirical": [0.93, 0.98]`）。穷尽所有口径（knee per-task、跨前沿解、跨求解器池化、符号翻转）全部为负——真实值是 −0.17~−0.69。变体 D 的 r≈+0.95 同理是假的。最终整段机制叙事重写，4 个 commit 善后。

2026-08-09 事故：摘要 `random-init f1* deficit 0.18--0.46` + 正文 §6.6 `-0.18/-0.42/-0.46/-0.33` 回源到 **buggy-orbit 时代旧 control 文件**（`_old_buggy_orbit_20260802/`，值 0.179/0.419/0.461/0.328 全对上）。RDR-005 轨道修复 + P1 窗口修复后 MOEA-2 结果已变，control 数据没重跑，正文沿用旧值；且旧 s3_s4_control.json **无 delta_std 字段**，正文 S3/S4 的 `±0.04` 完全无源。当前代码新 control 给出 S1=0.269/S2=0.493（n_ref_dirs=12 对齐主线）。修复：统一 runner `run_hotstart_control_s1s4.py` 重跑 S1-S4。
**副教训（FM-3 对照组配置分叉）**：旧两个 control 脚本各演进，`run_s1s2_hotstart_control.py` 用 n_ref_dirs=5、`run_hotstart_control_s3s4.py` 用无约束 baseline_b1（RDR-005 前），都与主线 n_ref_dirs=12 分叉 → 数字不可比。对照组必须复用主线 runner 的参数常量。

2026-08-10 事故（M-F1，S1 integrity 清册抓到）：论文 §6.2/§4/§7.1 共 5 处（中英）G-SM f3 效应量写 "Cliff's δ = +0.91"，重算 200 场景配对 = **+1.0000**（g=200/l=0, W=0, p=1.44e-34）。0.91 全仓 grep 无任何代码/数据来源——§6.2 重写时旧统计残留未随最终数据更新。**防复发已落闸**：新建 `src/tools/verify_paper_numbers.py`（S1a 数字清册），144 断言把论文每个统计 claim ↔ 最终数据快照重算 ↔ 容差，数据文件 sha1 指纹 + 报告归档 `review/verify_paper_numbers_report.json`，exit 0/非0，作为投稿 gate 确定性脚本套之一。

**Why**：审稿人复现是投稿的必答题；数字来源断了，整段论证一起垮。且"写死在某脚本里的常量"极具迷惑性——看起来有出处，实际是复读不可验证的值。
**How to apply**：
1. 论文定稿前逐数字 grep 来源：每个 r/p/百分比 必须能 trace 到生成脚本或原始数据
2. 数字若来自"早前某次分析"而脚本已丢 → 当场重算或用可复现口径替代，不许保留
3. 审查报告说"该数有数据支撑"时，自己重算一遍（WB v6 报 V6-D01 不可复现正是这轮唯一的真警报）
4. 硬编码常量的引用点（如脚本 out 字典）是排查重点——它可能只是搬运历史值
5. 关联 [[revision-20260801-v8-d01-reversal]]（完整数据+记录）[[feedback-long-task-checkpointing]]
