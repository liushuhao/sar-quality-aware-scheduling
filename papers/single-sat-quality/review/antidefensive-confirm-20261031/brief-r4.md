# 审查任务书 — 反防御性写作修改批确认轮（R4，复测+全量回归）

## Canary（必须遵守）
1. 只读审查：除你的 stdout 外不得修改、创建、删除任何文件。
2. 每条发现必须引用稿件原文（逐字），附节名与 tex 行号。
3. 不编造事实；数字逐字引用稿件。
4. 无网络访问。
5. 有什么报什么；不得制造发现，也不得盖章放水。若一切干净，明说干净。
6. stdout 输出完整审查报告。

## 背景
- 稿件：`papers/single-sat-quality/small-paper-ijae.tex`（单卫星敏捷 SAR 调度论文，已投 ASR）。
- 本批反防御修改共三波：
  - ceaf935：主批 12 处（diff: `review/antidefensive-confirm-20261031/diff-ceaf935.patch`）
  - 16a972b：确认轮修复 1 处（diff: `review/antidefensive-confirm-20261031/diff-16a972b-fix.patch`）
  - 6f2561a：证伪轮修复 1 处（diff: `review/antidefensive-confirm-20261031/diff-r3-fix.patch`）
- 修改后全文 = `papers/single-sat-quality/small-paper-ijae.tex`（约 1710 行）。

## 上一轮概况（供针对性复测）
证伪轮审查认定 Limitations 节 "at a fixed timeliness operating point" 按字面读与 §7.2 求解器行为描述（G-BL earliest-feasible vs G-SM 最小斜视 vs quality-steering 可延迟）存在歧义冲突，已修复为：
"The utility model optimizes quality and quantity without an explicit latency or urgency objective; acquisition timeliness is therefore not evaluated as a separate scheduling dimension and is left to future work."

## 审查任务
### 针对性复测
1. 修复后的 timeliness 句是否与 §7.2、G-SM 描述（§4.3）完全一致无矛盾、无歧义残留？
2. 修复是否引入新问题（衔接、语法、同义反复）？

### 全量回归
A. 12+2 处反防御修改逐处核验（达成目的？引入新问题？**双向风险：删减后是否产生夸大宣称——conditional / approximate / tested-scope 类必要限定是否在某处被删光**？）
B. 扩展扫描：摘要—引言—结论三处一致性 / patch hunks 前后衔接 / 交叉引用承载 / 拼接处重复 / 间接波及面。

## 输出格式
```
## 复测结论

## Part A: 逐处核验表
| # | patch 位置 | 达成目的? | 引入新问题? | 主张诚实性 | 证据(引原文+行号) |

## Part B: 扩展扫描发现
（每条：CRITICAL/MAJOR/MINOR/NOTE + 行号 + 原文引用 + 理由 + 建议）

## Verdict
PASS / PASS-WITH-FINDINGS / FAIL + 一句总判
```

## 效率指引
全文可整读。优先：复测修复处 → A 层双向夸大风险 → B 层一致性。
