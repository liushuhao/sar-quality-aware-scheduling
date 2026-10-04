---
name: feedback-cost-claims-need-measurement
description: 「修=X 作废/成本 Y」类声明必须实测——R14 的 ±42% 是杠杆比值非输出漂移，「修=作废 270 单元」被重跑证伪
metadata:
  node_type: memory
  type: feedback
  originSessionId: sess_f55a85ce-34c8-47b6-ac61-b6b6cefe6984
---

票 23（2026-10-04）实测：台账 R14 记「修 boundary_rate 会使已完成的 270 单元全部失效，须重跑全阶梯（~50 min）」——重跑后证明该前提**未实测且错误**：±42% 是杠杆项比值（Vs·cosψ/R0），不是输出漂移；真窗阶梯 manifests 40/40 byte-identical、R1C 全 STR 零数值变化、变化仅经 C2 model 分支（omega 贡献 ~1e-3 s/对，被 fallback 常数与 dwell 主导项吸收）与 SPT kat0。

**Why:** 成本声明被写进台账关闭条件时没有测量支撑；fallback 常数（4.07 s 恒武装段）与 dwell ∝ r0 主导项把 omega 误差吸收到远低于判别阈——「通路存在」≠「读数受影响」。

**How to apply:** 凡写「修 X 会使 Y 作废/需重跑 Z」进台账或 BLOCKED：先跑一个最小判别（改一行→重跑一个单元→diff），或引用 fallback/主导项分析给出上界；写不出的，关闭条件标「成本未实测，动手前先测」。同理适用于「审稿人翻车点」类风险声明。相关 [[feedback-measure-both-switch-paths]] [[feedback-instrument-measurement-traps]]
