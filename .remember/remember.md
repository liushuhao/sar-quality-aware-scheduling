# Handoff

## State
- review2 R1 波（修图）配额中断半程态：任务0九步全过+七图诊断+fig1 修复(`7d67b6f`)+fig3-7 一轮样式(`0247efd`)+main.pdf 重建(`8734200`)已提交；二轮 cmr10 五脚本+图 PDF **在途未提交**（我亲验 stdout vs 基线全等、.err=benign 字体警告）。fig2 BLOCKED 已裁（`r1/adjudication_fig2.md`：坐标 token 豁免 ≤5 上限全量入表，aasr/1.25 语义零容忍）。
- 执行者死于周配额 1310（12:27），重置 2026-10-17 00:57；续跑锚=`r1/PROGRESS.md`（含我 12:5x 主线程注记）。
- 事故已沉淀：宿主内置 analyze_image/Read-PNG 上传 ufileos CDN（违 spec §0.8），稿件裁片外泄不可撤回——台账 R37+项目记忆，R2 起图像判读只走 PIL/本地 CLI。
- 台账 open=4 全带关闭条件：R19（票27/Ch5 触发）、R35（清偿=R2 任务5+6）、R36（本半程态）、R37（CDN 泄面核验）。

## Next
1. 配额重置后续跑 R1：SendMessage `agent_5940f1e9-367a-4e94-bf64-a27f8d2f1a38`（或新执行者读 PROGRESS.md），顺序=复核二轮五脚本→fig2 重建→任务4 视觉验收（red_proof 时序终验）→书验收1-6→我跑暗卷 R1-1..R1-8。
2. R1 过后发射 R2（书 `55c9571a` 未动、spec blob `50be1fa4` 三处同值仍有效）；R2 面板/独立审按 R37 教训禁云图像路径。

## Context
- Agent 派发两层故障都会复发：off-peak-ticket-expired=瞬时重试即过；1310=数日不可恢复，先看配额窗口再排无人值守波。
- 运行纪律不变：勿改 `~/.claude/settings.json`；论文口径禁动（26.9°/真窗 v3/R_fam 8.74/10.91）；`?? .githooks/` 勿碰。
