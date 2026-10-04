---
name: feedback-discriminator-and-gate-pin-design
description: 判别器设计三课——行为隔离不可能时用 AST 结构断言补；变异红证按整语义单元退（半变异假绿）；门禁计数 pin 语义必须匹配实现
metadata:
  node_type: memory
  type: feedback
  originSessionId: sess_f55a85ce-34c8-47b6-ac61-b6b6cefe6984
---

票 23 变异红证与门禁复跑抓出的三个设计陷阱：

1. **半变异假绿**：M2 变异只退 evaluator 两条 omega 调用之一 → 测试仍绿（另一半仍透传）。变异必须退**整语义单元**（同一消耗点的全部行）。
2. **行为判别器上限**：anchor 路径 dwell 与 r0 共变（同一 plan），omega 单项无法行为隔离——换 AST 结构断言（所有 `boundary_rate_of` 调用必须带 `r0_m=` kwarg）+ wrapper 透传单测；evaluator 路径可隔离（dwell 固定），用二分 straddle 端到端判别（omega delta ~1e-3 s，gap 网格扫描会相位错过——二分变号点+微移避开 delta≈0 点）。
3. **门禁 pin 语义漂移**：verify.py `domain_tests` 用 `collected = passed + failed` 当收集数——pytest -q tail 无 collected 数字，skip/xfail 被排除 ⇒ N0=收集数时条件**永不可满足**（票 17 时代 N0=200 vs passed 198 该步从未真绿过，18min 套件掩盖了它）。修法：pin passed 数 + 显式 pin 基线 skip/xfail 对（净增 0 纪律进门禁）。

**Why:** 判别力缺口在「测试绿」表面下不可见，只有变异红证/首次 pin 变更才暴露；STR 的 boundary_rate 恒 0 使 STR 任务对 omega 口径天然免疫（判别器必须选 SLS/SPT 任务）。

**How to apply:** 写变异红证时先列「该语义单元的全部代码行」，变异一次退光；门禁 pin 改动时对照实现语义（passed vs collected vs selected）；涉及恒零/恒真分支（STR/SLS r0 不变式）的判别器必须避开。相关 [[feedback-cost-claims-need-measurement]] [[feedback-assert-silent-skip]]
