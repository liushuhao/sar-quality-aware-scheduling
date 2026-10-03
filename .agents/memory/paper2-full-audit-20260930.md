---
name: paper2-full-audit-20260930
description: Paper2 三层全面审查闭环：数据全复现、公式层净、5 处文档级修正已提交、U1-U3 已裁落票、跨模型简报待跑
metadata:
  node_type: memory
  type: project
  originSessionId: eccb7b46-1ff2-4f2d-850b-e5a3d1a30c55
  modified: 2026-09-30T22:35:41.805Z
---

2026-09-30 paper2 交接前三层全面审查（audit-program + 3 路 fresh subagent A/B/C + 主线程机械对账）闭环。

**核心判决**：数据层 100% 复现（阶梯 2→4→17→48、反转 5→43/4→25、115/115 no_promotion、50/50 exit 0、manifest 三重 sha）；公式层内部一致、实现无偏差；全部缺陷为文档级。
**已修**（commit 3f188d3，注释级零行为）：aasr.py D06-3 角引用 12°→~15.1°、滑带 6.64 dB、quality 0.03%、modes §5→§2/§6 引用。spec.md（scratch）：:77 相变措辞改三腿、:3-4 触发链加更正行。
**驳回**：duration.py:73 "0.42/0.44"（两个不同量）；6c Eq12/13 不一致指控（审计员约定混用，两式代数一致）。
**残留最高优先**：formula-spec.md:81 斜视注记方向错（cos 应为 sec，ρ_a∝sec ψ̄）——冻结文件，**票 18 blocking gate 承载，v1.1 必须写 sec**；票 18 checklist 需加 Eq12/13 edge-vs-axis 约定钉死。
**待用户裁决 → 已裁（2026-09-30 用户「按推荐走」）**：U1 predicates 重冻结 → 票 15 验收新增项；U2 票 18 新增 sec 方向 + Eq12/13 约定两项；U3 容量数 owner → 票 17 验收新增项（出工件前禁引具体数）。台账 #72-75 回填。
**工件**：`.scratch/sliding-spotlight-scheduling/audit-20260930/`（A/B/C/D 判决 + E 跨模型简报——用户 GLM-5.3 跑，回传合并）。
**终态（2026-09-30 收工）**：U1-U6 全落（U1-U3 按推荐、U4-U6 经第一性原理反思修订版：min-over-pairs 下界 + 偏离模式观察项 + 双向采信 + D15 一行登记 co-②③/预算有界披露/novelty 锚）；E 简报 in-session 自攻完成（F 文件，同源非异源——真异源可另行跑）；票 18 闭环（gate-review FAIL→修→确认 ALL-CLOSED→acceptance 6P+1 部分→cddcdf9 补齐；commits 1bd49d8+cddcdf9）；台账 #72-77。**【2026-10-01 更新】停审判断已被 audit2 推翻**（换模型后四路 fresh subagent 挖 17 项，行为级仍 0 但前提级 6 条，见 [[paper2-audit2-full-review-20260930]]）⇒ **下步 = 票 15**（物理域 45°，ready-for-agent，T0）。33 commits 未 push（沙箱硬拒，用户终端）。

**Why**: 用户对 paper2 状态不放心，要求理论+代码全面复审；上会话前提洗钱教训后首个系统性前提审计。
**How to apply**: 票 15 开工前对照 formula-spec v1.1 §3.1（式源）+ 票 17 三项 audit 验收；跨模型真异源补跑可另发 E 简报。相关 [[paper2-spec-v05-cycle-20260930]] [[feedback-premise-laundering]]。
