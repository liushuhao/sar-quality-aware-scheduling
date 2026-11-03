# Postscript 2026-10-31 — 反防御性写作批次对确认轮记录的影响

Commit ceaf935（反防御性写作审查 12 处落地）与本面板确认记录的两处交互：

1. **R1-06 引用句失配**：confirmation 表 Part A 中 R1-06 的 resolved 证据引用了正文句
   "...and does not isolate the source of the MOEA's advantage"。该半句是修复实现时
   把 remedy 措辞（"without isolating the source of the gain"）搬入正文的冗余自白，
   本次按反防御审查删除。R1-06 的实质要求（撤除 "the MOEA's gains reflect structured
   search" 归因主张、收窄到观察对比）在删除后仍然满足——归因句不在正文，主张仍为
   "bounds what unstructured selection achieves on these scenarios"。

2. **convergence-trace 披露句删除**：R1 报告 Non-defect observations 曾正面提到
   search-budget control 披露 "the absence of a convergence trace"。该句无对应
   finding 义务（不属任何 remedy），本次删除；"small scenario scope" 披露与
   "conditional on the tested budget" 条件声明均保留。

其余 10 处改动不触及本面板任何 finding 的修复面（26 条逐条对撞，无回归）。
