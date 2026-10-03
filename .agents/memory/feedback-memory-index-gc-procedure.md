---
name: feedback-memory-index-gc-procedure
description: 记忆索引季度 GC 的正确机制——文件移 archive/ + 删索引行；归档会造「链接指向已归档」NOTE，故优先归档零入链条目
metadata:
  type: feedback
---

**GC 记忆索引 = 文件移 `memory/archive/` + 删该条 MEMORY.md 行**（不是删文件）。
closeout-sweep 的 `index_consistency` 对 `archive/` 前缀豁免，`dangling_links` 把归档
目标算「合法但降 NOTE」，故归档后不会出 FAIL。

**Why**：2026-10-01 季度 GC。先做客观项（索引↔文件双向：140↔140，零孤儿零缺失，
说明索引本身没坏），再做判断题。候选 = 已闭的历史条目（paper1 修订史/面板记录/RDR 重跑
checkpoint）。**关键约束**：53 个候选里 **40 个有入链**（最多 10 条）——归档它们会制造
40+ 条「链接指向已归档条目」NOTE，与「不想看到 NOTE」直接冲突。故只归档**零入链**者。

**How to apply**：
1. 先跑客观检查（索引指向缺失文件 / 未入索引文件）——有则先修，那是真错。
2. 列候选（已闭/已兑现/状态 stale），**算每个的入链数**。
3. 零入链且确已闭 → 移 `archive/` + 删索引行（零 NOTE 代价）。
4. 有入链的 → **留在索引**（归档的 NOTE 代价大于索引行成本）。
5. 另一类真害是 **stale 指引**（「下次开工票 X」已变、「N 项债」已增、结论已被推翻）——
   就地改写索引行，比归档更有价值。
6. 复核：`closeout-sweep` 须仍 FAIL 0 / NOTE 0，索引行数下降。
7. 只动**本工具侧**索引（每次会话注入的那份）；repo/zcode 镜像的既有条目按「不改对方既有条目」不动。

本次结果：142 → 128 行（归档 12 条零入链 + 就地改 6 条 stale），NOTE 0。

相关 [[feedback-mirror-drift-check-design]]。
