# Handoff

## State
- **投稿前端已定稿并提交（2026-10-12）**：标题定 A = `Agile Sliding-Spotlight SAR Satellite Scheduling with Mode-Determined Dwell Duration and an Image-Quality Objective`（用户逐个裁决；两路 fresh 审一致否掉 `Endogenous Dwell`——书目零命中、搭配实测 0 次、对 AA 读者吞主张），同步 6 处零残留。作者块 affiliation+email 逐字照搬 Paper1（`small-paper-ijae.tex:26-31`）。`refs.bib` mittermayer 页码提成 `pages` 字段（值原本就在 booktitle 内，零编造），bibtex 警告 3→2。
- W7 终闸机械套件因改动**全量重跑**并全绿：红线 md+tex rc=0 ×2、59 项台账（37落段/10扫描/12禁语）、数字 full.md 40 + main.tex 39 零 mismatch、pdflatex×3+bibtex rc=0、38 页、7 图全加载。留档 `goal-w2w7/gates/w7_final_regate_after_title_affiliation.txt`。commits：`40bee0e`（六件定稿）、`68caa4a`（SUBMISSION_CHECKLIST.md + main.pdf）。HEAD=68caa4a，工作树净（余 `?? .githooks/`）。
- 台账 open=2：R19（Ch5 重构未启动，自 10-04 零 commit、票 27 blocked，维持）、R35（本会话新立=W7 独立审层 FREEZE 未重跑；判断=不必因本轮零触正文数字，close when=用户令补跑或下轮触正文）。

## Next
1. **投稿=用户本人在 Editorial Manager 操作**（清单 `papers/sliding-spotlight-scheduling/paper/SUBMISSION_CHECKLIST.md`）。三项只能人填：推荐/回避审稿人、是否投特刊、Data availability 措辞。传源文件须含 `figures/` 两个 `.tex`（`\input` 引入，缺了编辑部编译不过）。另 2 条 bib 缺页码（caleiras2026a/wang2024research）本地无来源，拒编，留编辑部补。
2. **review2 两本 goal 书待发射**（已过 4 轮审书闸，判「可发射」）。现算哈希（2026-10-12 收工亲测，活件 vs 归档件 `cmp`=0）r1=`287aa046…` / r2=`55c9571a…`；书内 spec blob 钉值 `50be1fa4…` 与盘上 spec 一致——执行者任务 0 自检链完好。用户倾向先审后投：GLM 5.3 满血会话粘 R1（`.remember/tmp/goal_book_review2_r1.md`）→ 跑完明卷+暗卷验收 → R2 → 投稿包重冻结 → 再投。

## Context
- **哈希勘误勘误（2026-10-12 收工对账）**：并行收尾会话（29c91fa）曾把两书哈希记为 `ec885c15/77bac3be` 并判 `287aa046…/55c9571a…` 是「重写前旧值」——该判定不成立：其现算时点落在审书闸 Round3/4 重写窗口内，且 `ec885c15/77bac3be` 在本书全部历史态中不存在；本轮收工再亲测活件=归档件（cmp 逐位 0）、书内 spec blob `50be1fa4…` 与盘上 spec 一致，**`287aa046…/55c9571a…` 为终态**。读到哈希对锚句先现算（此规保留）。
- rtk 一天咬三次均给「可信但错」结论：`grep -h 多文件` 吐 usage、`grep -c` 假 0（换行所致）、`git check-ignore -v` 输出被吃。**否定性结论（零命中/不在/未跟踪）必须双法复核**，单文件名给 bash grep 或 python 读文件才可靠。
- 运行期纪律不变：勿改 `~/.claude/settings.json`（hermes 热重载带死子进程前科）；勿并行会话写 `paper/**` 或 remember.md。
- 论文口径禁动：26.9°=注册保守值非物理边界、真窗只取 v3_results、R_fam 8.74/10.91、负 promotion 结果如实上报（90 单元无一提升，spread 3.9722 vs 冻结 6.0）。
