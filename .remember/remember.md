# Handoff

## State
- **review2 R1 波（修图）已完成并收口**：`f5ce52e`（fig2 重建）+ `2ecc2ef`（行距/残重叠）+ `e4b2f88`（fig3-7 rcParams 定稿）。验收全绿（七图 0 文字重叠、五脚本 stdout 零漂移、编译 38 页）。
- 本轮「清残留」会话已收口：W6 复选框补记证据（`goal-w2w7/PROGRESS.md`）、`r1/fig_predicates.md` 与 `r1/BLOCKED.md` 的 fig2 stale 表述更正、R19 台账关闭转票 27、R38 前提复测推翻并重挂条件、`residual-ledger.py move --why` 静默丢字段缺陷修复（`~/.agents` 27691f3，含 selftest 回归）、**run_verify 全量已跑通**（PASS=12 REPORT=1 FAIL=0 / EXIT=0，528 测试 0 失败）。
- 台账 open 仅 R37（R2 波清偿）、R38（11 项 plugin refresh），均带条件、未 stale。
- porcelain：`M .remember/now.md`、`M .remember/residuals.md`、`M papers/sliding-spotlight-scheduling/experiments/results/verify/report_pilot.json`（脚本输出契约）+ `?? .githooks/`（并行会话，勿碰）。

## Next
1. **发射 R2 波（内容波）**：书 `goal-review2/archived/goal_book_review2_r2.md`（sha256 `55c9571a…`）、spec `goal-review2/review2-spec.md`（sha256 `50be1fa4…`）——本轮现算均一致。执行档目录 `r2/` 尚未创建。面板/独立审按 R37 禁云图像路径。
2. 探针残留已按用户点头处置：删 `_crop_probe` 4.7M + `.scratch/_tmp_img` 257K；**`_audit_me` 377K 保留**——删前扫描发现 `r1/vision/ac_fig4.txt:31` 引其为 fig4 判词溯源件，且 3 个脚本读 main.pdf 仍可复跑，待单独裁。同类散件（`.scratch/` 顶层 14 个 `_*.png`/`_measure.py` 约 1.2M）未动。**`.scratch` 里 v2-run / v2-run-preT23 / v3-run / v3-run-recheck 是 verify 门禁的消费输入，勿删。**
3. R2 完成后终闸；投稿动作与清单三项人填（推荐/回避审稿人、是否特刊、Data availability）属用户。

## Context
- 运行纪律不变：勿改 `~/.claude/settings.json`；论文口径禁动（26.9°/真窗 v3/R_fam 8.74/10.91）；`?? .githooks/` 勿碰。
- **改任何源码后缀文件前先落门禁标记**（项目 pre-tool hook 实测会拦）：`mkdir -p .gates && printf '<TIER> <票号>\n' > .gates/current-ticket`；`.md` 不受限。
- 书的钉值是 **sha256**，`git hash-object` 给的是 sha1 blob——两者对不上属正常，别当漂移证据（2026-10-12 曾因此误判一次）。
- 图 文件→PDF 页映射：figN 文件名=outline 编号 ≠ PDF Figure 编号。真映射：fig1→p10/F1、fig2→p16/F2、fig7→p21/F3、fig4→p25/F4、fig3→p26/F5、fig6→p27/F6、fig5→p28/F7。
- 关键教训：PyMuPDF 重叠机验阈过严（1.2mm）会漏真重叠，0.8mm 才抓出 fig2 的 1.4mm 压字；TikZ 节点继承 ~15pt 行距致盒过高，`\baselineskip=3.4mm` 是排版可控关键。
