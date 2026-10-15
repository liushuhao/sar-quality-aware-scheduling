# Handoff

## State
- **R1 修图波已完成**（`f5ce52e`/`2ecc2ef`/`e4b2f88`，七图 0 重叠、编译 38 页）。
- 本会话三件事全收口：**清残留**（`.scratch/` 全域裁决，删 7.8M 零引用产物、有引用者逐条留证保留；W6 证据回填；`r1/fig_predicates.md`/`BLOCKED.md` stale 更正；R19 关闭转票 27；R38 关闭）；**`run_verify` 全量跑通**（PASS=12 REPORT=1 FAIL=0 / EXIT=0，528 测试 0 失败）；**firecrawl 升 2.0.0 并接通**（API key + `/v2/mcp`，`claude mcp list` ✔ Connected，真调用冒烟过）。
- 台账 **open=2**：**R37**（图像 CDN 外泄面，待 R2 波清偿）+ **R40**（新，见下）。wontfix=5 / closed=33，`list` rc=0 无 stale。
- porcelain：仓库仅 `?? .githooks/`（并行会话，勿碰）；`~/.agents` 干净。

## Next
1. **发射 R2 波（内容波）**：书 `goal-review2/archived/goal_book_review2_r2.md`（sha256 `55c9571a…`）、spec `goal-review2/review2-spec.md`（sha256 `50be1fa4…`）——现算一致。执行档目录 `r2/` 待建。面板/独立审按 R37 禁云图像路径。
2. **R40 是否立票待你裁**：`sss_core/windows.py:109` 守卫只挡负长、零长 `t_start == window_end` 未挡 → `ZeroDivisionError`，而 `evaluator.py:283` 只 `except ValueError`。已实测复现；**当前不可达**（80 manifest / 11885 任务窗口，零长或负长 = 0，最短 0.25 s）。改 `sss_core/` 属 spec 只读面，动手须先立票。
3. R2 完成后终闸；投稿动作与清单三项人填（推荐/回避审稿人、是否特刊、Data availability）属用户。

## Context
- **firecrawl 的 `.mcp.json` 在插件缓存内**（`.claude/plugins/cache/firecrawl/firecrawl/2.0.0/.mcp.json`），**插件一更新就被覆盖，需重打补丁**：url = `https://mcp.firecrawl.dev/v2/mcp`（**不是**插件默认的 `/v2/mcp-search`——那个只收 OAuth token，key 打必 401）+ `headers.Authorization: "Bearer fc-…"`。该连接暴露 28 个工具（含 crawl/map/monitor/interact/parse/agent），故 2.0.0 净能力损失为零；旧 1.1.0 缓存目录保留可回滚。
- 运行纪律：勿改 `~/.claude/settings.json`；论文口径禁动（26.9°/真窗 v3/R_fam 8.74/10.91）；`?? .githooks/` 勿碰。**改任何源码后缀文件前先落门禁标记**：`mkdir -p .gates && printf '<TIER> <票号>\n' > .gates/current-ticket`（`.md` 不受限）。
- **含密文件/含反引号长文本的 shell 处理**（本会话踩过两次，已入 core-memories）：读含密文件先 `json.load` 取字段再选择性打印，**禁整段读进来正则脱敏**（掩码前提与被掩内容的病同源会失效）；含反引号或 `$` 的长文走 `python - <<'PY'` 引号定界 heredoc 或 Write 工具，写完回读校验。
- 书的钉值是 **sha256**，`git hash-object` 给的是 sha1 blob——对不上属正常，别当漂移证据。
- 图 文件→PDF 页映射：figN 文件名=outline 编号 ≠ PDF Figure 编号。真映射：fig1→p10/F1、fig2→p16/F2、fig7→p21/F3、fig4→p25/F4、fig3→p26/F5、fig6→p27/F6、fig5→p28/F7。
