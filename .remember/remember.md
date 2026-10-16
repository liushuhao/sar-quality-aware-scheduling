# Handoff

## State
- **paper2「paper1→paper2 举一反三」波收口 2026-10-16**：用户切强模型授权「处理全部问题」。
  复盘报告+执行全程 `.scratch/sliding-spotlight-scheduling/paper2-vs-paper1-lessons-20261016.md`。
  **9 提交**（`3278ed1..7d4d393`）：正文清内部工件码(pytest 全路径/ticket-40/D05-x)→消 200pt 溢出；
  define-before-use(H/W/C2/R3H/ALIVE-DEAD)+f_Q→f_q 统一+去重+摘要预注册限定；fig:promotion
  浮块移位(首引序 1→7 单调)；em-dash 101→80；表 caption 根因修复(原表从无 \caption)+P8WH/P2 清除；
  refs.bib 17 条双源核验修正(he2018a 假标题/zhang2025deep 错作者)/新增 `scripts/check_layout_gotchas.py` 门禁。
- **终闸 12 步在最终树(`0529f7d`)绿，`FINAL_GATE_EXIT=0`**：红线0 / 数字回源39-0 / prereg28 / v3-33 /
  claim 11/11 / run_verify PASS=12 REPORT=1 FAIL=0 / 编译×2 零error **40页** / census C1 DIFF(6条工件码删除)·
  C2 键本体不变(35 hits)·C3 只增(48→50,13→14) / 渲染40页 / 新步12 layout 0 FAIL。
- **对抗审(fresh 子 agent)verdict SHIP**（零 blocker/零回归）；**视觉读图 4 页全过**（p11 溢出消除/Table1/Fig.4/p40）。
- 工作树净（仅 `?? .githooks/` 并行会话，禁碰）。台账新 **R46**（deposit zip 过期）/ **R47**（figN↔Figure 号错位 wontfix）。

## Next
1. **R42（S10/S11）**：用户给 locator（已定 = 仓 `sar-quality-aware-scheduling` + Zenodo 冻本论文快照给 DOI）后，
   改 `main.tex:355`（Data availability）与 `§5.1`；bundle 用冻结态 main.tex 组装。**本波唯一未完正文动作。**
2. **R46**：投稿前用最新 main.tex+refs.bib 重组 deposit zip（现包是 lessons 波前树）。
3. 投稿包三项人填（推荐/回避审稿人、是否特刊、Data availability locator）属用户。

## Context
- **页数 39→40 = 文献表尾溢出 2 条**（表 caption + bib 补卷期页）：非浮图移位、非空页，review 模式接受留档。
- **禁整仓 push**：仓自 2026-09-27 未推、本地大幅领先，push 会连带公开 6 个已跟踪内部件
  (`.remember/{now,remember,residuals}.md`、`.scratch/.../issues/23-*.md`、`BLOCKED.md`、`PROGRESS.md`)。
- **模型记忆**：`.claude/.../memory/project-paper2-lessons-wave-20261016.md`——含 STR≡SLS AASR 恒等、
  +5.3%@45° 外推域口径、bib 核验须对出版社 byline 复核（子 agent 曾编 8 人名单）等非显而易见事实。
- `review2-spec.md §0.10` 的 refs.bib 冻结已被本波经用户明示授权覆盖（可 `git revert cc307cd`）。
- `.gates/current-ticket` = `T2 R42-pending`。
