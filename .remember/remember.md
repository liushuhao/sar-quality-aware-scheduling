# Handoff

## State
- 投稿前端已定稿提交（40bee0e/68caa4a）：标题定稿（两路 fresh 审否掉 Endogenous Dwell）、affiliation+email 照搬 Paper1、W7 机械套件重跑全绿（`goal-w2w7/gates/w7_final_regate_after_title_affiliation.txt`）；投稿动作=用户本人在 EM（清单 `paper/SUBMISSION_CHECKLIST.md`，三项须人填）。
- review2 两本 goal 书已过 4 轮独立审书闸（终判「可发射」零 FAIL，回执 `goal-review2/review-verdict-round1.md` 202 行）并交付用户；审前修掉 W6 预存 cover_letter 守门红灯（writing bans 只在 pytest 守门测试、W5 后无人跑过；纯换行修正，115/115 绿，随 40bee0e 入库；教训=`project-paper2-writingbans-gate-gap` 记忆）。
- 我对账推翻并行收尾会话的哈希勘误（29c91fa 记 ec885c15/77bac3be——该现算落在审书闸 Round3/4 重写窗口内、两值在书史不存在）：终态 r1=`287aa046…`/r2=`55c9571a…`（活件=归档件 cmp=0）、书内 spec blob=`50be1fa4…` 与盘一致（4d14b17）。
- 台账 open=2：R19（票 27 blocked，Ch5 重构触发）、R35（W7 FREEZE 未重跑，close when=用户令补跑或下轮触正文）。

## Next
1. 用户在 GLM 5.3 满血会话粘书 R1（`.remember/tmp/goal_book_review2_r1.md`）发射 → 主线程明卷+暗卷验收（探针=`.remember/tmp/goal_dark_slots_review2.md`）→ 粘 R2 → 验收 → 投稿包重冻结。
2. 用户 EM 投稿（用户倾向先审后投；若决定直接投则两书作废，零沉没）。

## Context
- 读哈希对锚句先现算——并行写手多，本仓已发生两次哈希勘误反转。
- 运行纪律不变：勿改 `~/.claude/settings.json`（hermes 热重载前科）；论文口径禁动（26.9°=注册保守值、真窗只取 v3_results、R_fam 8.74/10.91）。
