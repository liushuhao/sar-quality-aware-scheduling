---
name: feedback-bilingual-mirror-existence-check
description: 中英镜像核对须查整句存在性+跨段计数一致，不能只 grep 数字（ZH 曾缺整句 caveat、"15 runs" vs 30 内部矛盾）
metadata:
  node_type: memory
  type: feedback
  originSessionId: b1f85881-0f02-4dad-bb71-c3ac00f29f7e
  modified: 2026-08-12T00:22:13.443Z
---

**规则**：中英双版同步核对时，除比对数值外，必须查整句/整段存在性 + 同一实验的跨段计数一致。

**Why**：2026-08-12 收 §6.6 时连挖两个同族问题——
1. EN §6.6 hot-start 段有 "Two caveats qualify this control" 整段，ZH 该段**整句缺失**（rdr-021 样本量 caveat 修复只进了 EN，ZH 没镜像）。grep 数字查不出——ZH 根本没那个数字。
2. EN caveat 写 "15 runs for the variant-D control"，同一节 random-init 段却写 "15 S3 and 15 S4 runs"（=30）。段落 A 计数与段落 B 自相矛盾，跨段核对才暴露。

**How to apply**：
- 镜像后逐段比对：先确认 ZH 段落结构==EN（同段落数、同句子），再比对数字——顺序反了查不出缺失。
- 同一实验出现在多段时，样本计数（runs/scenarios/seeds）全仓 grep 该数，跨段必须一致。
- 改 EN 一句时问"ZH 有没有这句"；修 RDR 时检查该修复是否两版都落了（rdr-021 教训）。关联 feedback-tracking-status-lag feedback-midrun-stale-summary-file。
