---
name: feedback-negative-existence-claims
description: "负存在断言（\"论文/代码没有 X\"）禁凭模型先验答——5 秒 grep 能证伪的不许裸说；对话式问答是 rule 13 真空档"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1179617b-2be9-4e1c-934c-2cc5db239b2e
  modified: 2026-09-30T00:42:43.849Z
---

**规则**：用户问「论文/代码考虑了 X 吗」，答「没有/未建模」前必须 grep 实证。模型先验（「这类论文通常不建模」）不是证据。

**Why**：2026-09-30 断言「两篇论文都没建模能源/固存」，用户质询后实测 C1-C4 全在（types.py:112-138），当场收回。CLAUDE.md rule 13 无读不立只覆盖 spec/票/plan 工件写作，对话问答是真空档——负存在断言错答直接误导研究方向决策。

**How to apply**：「X 存在吗」类问题 → grep 关键符号/字段再答；找不到 → 说「grep 关键词 A/B/C 零命中」而非「没有」；不确定检索词覆盖面 → 明示检索面让用户补关键词。同根教训：转写原文（Edit old_string、引用 spec/记忆）必先回读，凭记忆转写必失真（本会话 F2/F3 两实例）。
