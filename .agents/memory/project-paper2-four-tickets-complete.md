---
name: project-paper2-four-tickets-complete
description: paper2 四票（22/15/16/17）2026-10-03 全部 completed——真窗族主实验 270 单元跑完，冻结件已签，剩余须拍板项
metadata:
  node_type: memory
  type: project
  originSessionId: dc1d746b-99cc-4dfa-b677-5ab3c5d336f1
  modified: 2026-10-03T13:28:06.422Z
---

paper2（滑聚/聚束变时长 SAR 调度）四张票 **2026-10-03 全部 completed**，本会话 50 commits，冻结六族 196 文件零 diff，`src/sar_sim` 自 M1 零修改，两面回归全绿（本域 198+1skip+1xfail / 共享库 145）。

**主实验总账**：真窗 120 单元（R1C/R2F/R3H/R4H × 10 seed × 3 预算）+ 合成对照 150 单元（M1NC/M2WF/M2WH/M3NC/M4WH 同阶梯）= **270 单元全部 exit 0、CV 全部精确 0**。

**核心结论（受冻结约束，不得越读）**：
- **P1 前沿丰富度**：R1C **CONVERGED、成立**（顶档 distinct_f_q 16.5 ≥ 3）；R2F/R3H/R4H **UNCONVERGED ⇒ NOT-YET-TESTED**（阈值虽达但阶梯仍在涨：35.5/12.0/5.0，Δ 11.0/6.0/2.0）——冻结明文此时禁作任何物理声明。
- **P3 promotion 结构维在真几何下翻转**：真窗三族 R_fam **6.82 ≥ 6.0（ALIVE）**，而九个合成族全 <6.0（最大 5.501）⇒ **合成族的「结构性非触发」不可外推**；三族按 ALIVE × UNCONVERGED ⇒ **NO CLAIM**。
- **P4 容量闭合度**：模式非平坦（closure 随过载单调升 3.706→15.732，4.25×）⇒ 主体成立；但**预设机制未观测到**（C2 需求 7.76–13.20 s 恒 < 窗宽 200–219 s，转移约束从不绑定）⇒ 部分符合，非完整验证。
- **消混杂**：合成族 anchor Δ 精确 0.0 ⇒ 闭式变更对锚零影响，真窗差异归因几何；**且合成族 dfq 本身也随预算陡增** ⇒ 丰富度增长**主要来自预算而非几何**。

**须随结果带走的约束**（详见 `BLOCKED.md`）：
1. **>160/240 的预算额度已耗尽**（合成族 320/480 票 20 已跑，`43911b0`）⇒ 要给真窗三族出判决须**用户拍板**加预算，且合成族先例显示可能买不到判决；
2. 真窗三族禁 alive/dead 声明；
3. 「前沿塌缩」「相变」全禁（红线机检 rc=0）。

**已知延后债**：`boundary_rate`（`maneuver.py:95`）在 C2 路径上仍读库 R0（**第六处口径分裂**，杠杆偏 ±42%）——修它会使 270 单元全部失效，须连带重跑全阶梯；`snapshot_rebuild` 门禁步未跑；v1「grid cell 上界 + 1 dB 裕度」保守谓词**显式不接线**（已改窗内最坏判据，实测窗边采样低估约 4 dB、48/48 任务）。

相关：[[paper2-spec-v05-cycle-20260930]]、[[feedback-caliber-split-on-geometry-injection]]、[[feedback-gate-laundering-and-tau-green]]、[[paper2-spec-v05-cycle-20260930]]
