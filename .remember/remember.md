# Handoff

## State
- **R2 内容波（review2 第二本）正文已改完**：面板 20 条全裁（`r2/panel/08_author_adjudication.md` CONFIRMED，will 12 / wont 7 / not_on_point 1），其中 **11 条落地为 7 个提交**：`8b7abf0`(R2) `2123ea7`(R3/R6) `6ebe630`(R4) `23b31aa`(S2/S3/S4) `c815daa`(S12/S13) `cb4a9cb`(S7) `e472355`(R5)。每个单元五脚本快闸全绿、census C2/C3 逐位不变。
- **终闸未在改完的树上跑过**（只跑过五脚本 + census）→ 台账 **R41**。首跑（10-15 23:03 发射）被电脑重启杀死于第 6 步，产物全在 `r2/`。
- 台账 open=**3**（R41 终闸未跑 / R42 S10-S11 待 DOI / R43 C1 例外表 6 条超 ≤5 容限）；porcelain 剩 3 项**全部可归属**：`M experiments/results/verify/report_pilot.json` 与 `M paper/main.pdf`（都将在终闸重跑/重编时刷新，届时一并提交；现留作在制）、`?? .githooks/`（并行会话产物，禁碰）。`.remember/` 三件已随 `178b0e1` 提交。

## Next
1. **跑终闸**：`bash .scratch/sliding-spotlight-scheduling/goal-review2/r2/_final_gate.sh`（11 步，含 ~40 min 的 run_verify），全绿后填 `r2/freeze-report.md` §3 与 census 例外表（收 R43）。
2. **S10/S11（R42）**：等用户给 locator（已定 = 沿用已有仓 + Zenodo 冻本论文专属快照给 DOI）后改 `main.tex:355`（Data availability）与 `:195`（§5.1）；bundle 须用冻结态 main.tex 组装。
3. 投稿包：三项人填（推荐/回避审稿人、是否特刊、Data availability locator）属用户。

## Context
- **页数 38 → 39**（本波累计增行 + 4 个引导标题），终闸须定性是增行还是浮图移位；按用户决定用模型读抽样页核版式。
- **禁整仓 push**：仓自 2026-09-27 未推、本地领先 254 提交，push 会连带公开 6 个已跟踪内部件（`.remember/{now,remember,residuals}.md`、`.scratch/.../issues/23-*.md`、`BLOCKED.md`、`PROGRESS.md`）。
- **census 是逐 token / 逐行计数**：复述已有数字照样 delta；C3 按"含该词的行数"，行内插 `\paragraph{}` 不改计数，换行会改。改正文前先想"能否指向而不复述"。
- 面板自身**不是独立误差过程**（五席同模型族同会话，决定书自披露）；主线程已逐条回正文取证，核验记录 `r2/panel_triage.md`。
- `.gates/current-ticket` = `T2 R2-wave` **保留**（波次未验收完）；`.scratch/.../r2/` 下有 `_quickgate.sh <tag>` 可复用快闸。
