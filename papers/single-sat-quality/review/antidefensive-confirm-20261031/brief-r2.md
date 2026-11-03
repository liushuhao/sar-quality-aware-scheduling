# 审查任务书 — 反防御性写作修改批确认轮（R2，复测+全量回归）

## Canary（必须遵守）
1. 只读审查：除你的 stdout 外不得修改、创建、删除任何文件。
2. 每条发现必须引用稿件原文（逐字），附节名与 tex 行号。
3. 不编造事实；数字逐字引用稿件。
4. 无网络访问。
5. 有什么报什么；不得制造发现，也不得盖章放水。若一切干净，明说干净。
6. stdout 输出完整审查报告。

## 背景
- 稿件：`papers/single-sat-quality/small-paper-ijae.tex`（单卫星敏捷 SAR 调度论文，已投 ASR）。
- 本批反防御修改共两波：
  - 第一波 ceaf935：12 处措辞层修改（diff: `review/antidefensive-confirm-20261031/diff-ceaf935.patch`）
  - 第二波 16a972b：确认轮修复 1 处（diff: `review/antidefensive-confirm-20261031/diff-16a972b-fix.patch`）
- 修改后全文 = `papers/single-sat-quality/small-paper-ijae.tex`（约 1710 行）。

## 上一轮审查概况（供针对性复测）
R1 审查 12 处，11 处干净；1 处 MAJOR（Limitations 节 timeliness 句把 G-BL 的 earliest-feasible 放置误泛化为所有任务）已修复：删去失锚从句，现句为 "The utility model also optimizes quality and quantity at a fixed timeliness operating point; explicit latency and urgency objectives are left to future work."

## 审查任务
### 针对性复测
1. 修复后的 timeliness 句是否事实正确（对照正文 G-BL/G-SM 的实际放置行为）？是否仍保留 scope 披露（无显式 latency/urgency 目标）？是否与 Discussion 中 G-BL vs quality-steering 的描述一致不矛盾？
2. 修复是否引入新问题（衔接、语法、重复）？

### 全量回归（两层，同 R1 标准）
A. 12 处反防御修改逐处核验（达成目的？引入新问题？**双向风险：删减后是否产生夸大宣称——必要限定 conditional/approximate/tested-scope 类是否被删光**？）
B. 扩展扫描：摘要—引言—结论三处一致性 / patch hunks 前后 ~15 行衔接 / 交叉引用承载 / 拼接处重复词 / 修改间接波及面。

## 输出格式
```
## 复测结论
（针对修复处的 1-3 判定）

## Part A: 逐处核验表
| # | patch 位置 | 达成目的? | 引入新问题? | 主张诚实性 | 证据(引原文+行号) |

## Part B: 扩展扫描发现
（每条：CRITICAL/MAJOR/MINOR/NOTE + 行号 + 原文引用 + 理由 + 建议）

## Verdict
PASS / PASS-WITH-FINDINGS / FAIL + 一句总判
```

## 效率指引
全文可整读。优先：复测修复处 → A 层双向夸大风险 → B 层一致性。
