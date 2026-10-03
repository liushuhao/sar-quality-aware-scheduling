---
name: ch3-paper-accept-ready
description: Ch3 ASR 论文 2026-08-31 起 Accept-ready 可投;review/ 目录 gitignore
  仅本地留存;verify gate 缺 tail p10 断言(延后债)
metadata:
  node_type: memory
  type: project
  originSessionId: sess_a77252e3-b484-4191-9b08-7a5e47acb074
---

papers/single-sat-quality(ASR 投稿)2026-08-30 五席盲审判 Major Revision(review/ars-panel-20260830/editorial-decision.md,N1–N18+S/T 清单),经 commit b94adf2 + 95ea214 修复,2026-08-31 re-review 残留清零,状态 **Accept-ready,可投**(闸口 185/0 + 174 测试 + refs 全绿)。全文包络叙事已换新:包络 r≈−0.36 / 独立角 null −0.60 / 稀疏调度 −0.63(旧 −0.97 为默认轨道构建+旧口径 artifact,已撤回)。

**Why:** 跨会话需要知道投稿状态与两个非显而易见的坑:(1) `papers/single-sat-quality/review/` 整目录被 .gitignore L85 忽略——审查报告(REVIEW_INDEX、editorial-decision、re-review)仅本地留存,尝试 commit 会失败,属项目既有安排;(2) 存在一条延后债。

**How to apply:** 下次动 `src/tools/verify_paper_numbers.py` 时补一条 tail-risk 断言:正文 §5.3 "S4 MOEA-3 f2 10th percentile 0.291" 回源 `experiments/results/panel20260830_extra.json` → tail_risk.S4.MOEA-3_f2.p10=0.2913(G-BL_f2.mean=0.3364),已人工核验但无机械闸口防漂移。审查方法论教训见 review-claims-need-semantic-search。

**投稿状态更新(2026-09-25):** cover-letter 日期已刷新为 20260923 并重打投稿包(git log c90d169 "paper: refresh cover letter date for 20260923 submission package"),Ch3 已于 2026-09-23 前后实际投出,待办①②视为已办。

**投稿前待办(2026-08-31 确认,已闭合):** ① cover-letter.md/.pdf 日期刷新(已办,20260923);② `ASR-submission-20260818.zip` 投稿包过时(不含 0830 panel 修订与 0831 残留清理),须按当前 HEAD 重打(EN 主稿 + 已重编 highlights/cover-letter PDF + 图源;ZH 版不投)。ASR 投稿门户是 Editorial Manager 站点 **AISR**(https://www.editorialmanager.com/aisr/,站点代码不是 asr,易混);订阅路线(subscription)发表免费、约 12 个月后自动开放,gold OA 约 $3,500——无强制 OA 要求则走订阅路线。已有材料齐备:highlights 4 bullets 合规(3–5 条 ×≤85 字符)、AI/CRediT/利益冲突/数据可用性声明均在 tex 内。
