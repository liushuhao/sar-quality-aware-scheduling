---
name: review-20260922-resource-cap-facts
description: 20260922 审稿修复 commit c0787cf——C3/C4 资源上限=200 任务天花板且半数密集场景绑定（推翻正文 non-binding 论断）；verify 闸锚表格不锚定性声明、ZH 表格无闸两大盲区
metadata: 
  node_type: memory
  type: project
  originSessionId: 20685b8a-ee6d-4e7b-81ca-ed2a150b96cc
  modified: 2026-09-22T15:05:44.782Z
---

2026-09-22 全文审稿修复（commit `c0787cf`，verify 189/0，双 PDF 编译过）。

**已坐实并改正的事实（勿回退）**：
- C3/C4 两资源上限换算恰好都是 200 任务（10⁷/5×10⁴；10¹¹/5×10⁸）。G-BL 顶格场景：S3 20/50、S4 27/50；消融 A S3 15/50；σ-sweep 10 个 S3 场景 n_selected=200.0/std=0（=S3-A seeds 00-09 子集，与消融 50 场景 154.2±39.9 不矛盾）。正文 "non-binding under all tested scenarios" 已改为如实描述；密集收敛 = C2 时间饱和 ∪ C3/C4 资源饱和。
- ZH 尺度表曾整表落后一个数据版本（±0.14、0.985/+3.5%、S4 +0.4%），结论 +41% vs EN +40%，已同步。

**Why**：verify_paper_numbers 189 断言全部锚表格数字，"资源充足/不绑定"类定性句无断言覆盖，机器闸全绿仍放过算术矛盾（caps÷单任务消耗 vs 数据 n_sel 分布三条链独立坐实）；ZH 镜像表完全在 verify 门外，漂移到下次人工对账才可见。

**How to apply**：
1. 审稿/预闸时对一切定性设计声明（non-binding / far below / sufficiently high）做上限算术：cap ÷ per-unit 消耗 vs 实测计数分布，三链取證（baseline progress JSON + 消融 + sweep）。
2. 双语对账必须表级核对（逐行数值），不能只对 prose；ZH 表不在任何闸内。
3. 若未来改 E_max/M_max/e_i/m_i 或重跑 S3/S4，联动重查 §3.3、§7.4 两段定性表述与 200 任务天花板数值。

关联 stale-snapshot-audit [[feedback-bilingual-mirror-existence-check]]。
