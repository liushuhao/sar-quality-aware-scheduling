---
name: paper2-matrix-run-20260930
description: paper2 全量矩阵 50/50 绿 + 独立核验判「物理稀缺」成立（C2 传递成本×300s 地平线）；两预注册观察项全触发；改写裁决（方案A+低密度探针）与第三篇立项待用户
metadata:
  node_type: memory
  type: project
  originSessionId: dfc0ab69-dc81-433b-af55-4af450f9ac74
  modified: 2026-09-30T01:48:17.458Z
---

2026-09-30 全量实验矩阵（5 变体 × 10 seed）跑完：50/50 exit 0，driver = `run_matrix.py`（含 Windows git 路径 / seed 解析 / 工件键名三次修复），工件 `experiments/results/matrix/`，commit 1b67398。锚登记三变体逐位复现（M1NC 0.8931 / M3NC 0.2345 / M4WH 0.1199 == 票 13/14 值）。

**两预注册观察项全部触发**（analysis_prereg.json 冻结在跑数之前，commit 6aa365a）：

1. **H/W 前沿平凡化**：per-variant median distinct f_q levels 全部 < 3（a6 附录 B 判据）。
2. **promotion 全矩阵不触发**：max spread 1.01 dB < 6.0，no_promotion 50/50 → 三目标档死码。

**独立核验判决（2026-09-30，fresh subagent 六路 + 主线程抽查采信）**：「实现过紧」被推翻——平凡化 = **C2 传递成本（maneuver 4.07 s + settle 2.0 s + 1.25×dwell，5-13 s/次）× 300 s 地平线**的联合稀缺。AASR 剔除 0 任务、窗域 200k 点零漏根、C3/C4 松弛。修正算术：dwell 仅 1.3-6.7 s，串行上限 ~32-40，M4WH served 34 = 上限 85%。锚新读数：M1NC seed105 search 超锚 → 锚=归一下限；W/H 无一超越 → 锚≈注册模型实际上限。残留：greedy vs 上限 ~15% gap（不改机制）。探针 `.scratch/matrix-verify-probes/`。

**密度诊断（关键语境）**：全部目标挤同一 300 s 过境是 paper2 登记设计（scenarios.py:141，D08-7）；**第一篇是 2 圈星下点轨迹真实可见窗，目标不挤**（generate_all_scenarios.py:83,89）——同 N=500 单位时间密度差两个数量级。平凡化随密度出现：M1NC（20/圈）前沿 40 点正常，500/圈塌缩。**论文禁写「单星一次只能 30 个」当普适结论——第一篇自己的多圈结果就是反例，会被审稿人（同一作者）打脸。**

**【推翻 2026-09-30 晚，票 19 收敛标定】**上段相变结论作废：预注册搜索预算标定（amendment_20260930_convergence_calibration，commit 6355d50）实测 P8WH 塌缩在 4×/16× 预算下反转（median distinct_fq 5→31→43 @N=60；4→6→25 @N=80）——**40→60 悬崖 = 搜索伪影非物理**；所有变体 160/240 仍爬升无平台；矩阵平凡化（同预算 40/60 同读数）解释连带未裁决。存活：promotion 全密度死（对预算稳健，160/240 max 5.0<6.0）、容量算术、富侧存在。再裁决须新 amendment（矩阵变体高预算重测 + 平台判据）。原探针数据（40/60 预算）保留为预算敏感度证据。

**密度探针已跑（2026-09-30 晚，commit 8721f68 基建 + 0231900 工件，prereg amendment_20260930_probe_density 数据前冻结判据）**：WH 族扫描 20/40/60/80 × 5 seed 全 exit 0。@pop40/gen60 读数：median distinct f_q = 23(20) / 23(40) / 5(60) / 4(80)，**但该悬崖已被票 19 判为搜索伪影（见上）**。promotion 全密度死（N=20 处 max 3.89 dB < 6，对预算稳健）。

**待用户拍板（探针后）**：① 方案 A 拍板（数据已就绪，可进分析+写作期）；② 第三篇立项（全球分散/多星/多圈——真窗+预算绑定约束，见 [[concept-orbit-vs-pass-horizon]]）。

**How to apply:** 用户拍板后：探针走 spec D10 amendment + analysis_prereg amendment；分析层统计按 prereg 出；写作期两绑定交付物不变（per-mode 分解 + D05-5 双重披露）。相关 [[paper2-independent-audit-20260929]]、[[paper2-deferred-debts]]、[[paper2-objective-delta-rationale]]。
