# Handoff

## State
- **票 44/45/46 三张全 completed**：`b6d677f`（退化窗口域在入口被拒，不再从数值内核抛 ZeroDivisionError）/ `71d6819`（域套件计数判据由精确钉改下界 + 判据抽成可单测纯函数）/ `d8d3120`（三入口四处密度参数 `n_scan`/`n_step` 校验）。
- 终态全量：**`PASS=12 REPORT=1 FAIL=0` / `EXIT=0`**；`domain_tests` `expected_n0=376`（下界）对 `passed=385` —— 加 9 个测试**未要求重钉**；`shared_lib_tests` 154/154（有意保留的精确面）。
- 台账 **open=1**：只剩 **R37**（图像 CDN 外泄面），待 R2 波清偿。wontfix=5 / closed=34，`list` rc=0 无 stale。`.gates/current-ticket` 已清空。
- porcelain：仓库仅 `?? .githooks/`（并行会话，勿碰）。

## Next
1. **发射 R2 波（内容波）**：书 `goal-review2/archived/goal_book_review2_r2.md`（sha256 `55c9571a…`）、spec `goal-review2/review2-spec.md`（sha256 `50be1fa4…`）——现算一致。执行档目录 `r2/` 待建。面板/独立审按 R37 禁云图像路径。
2. **firecrawl 认证**：待用户在**应用内 `/mcp` 菜单**连账号（`! claude mcp login …` 走不通，`!` 无 TTY）。
3. R2 完成后终闸；投稿动作与清单三项人填（推荐/回避审稿人、是否特刊、Data availability）属用户。

## Context
- **改源码前先落门禁标记**：`mkdir -p .gates && printf '<TIER> <票号>\n' > .gates/current-ticket`。**改了票面文件会让标记过期**（hook 报"票目录有更新"），须重写标记再继续改源码（`.md` 不受限）。
- **域套件计数已与旧文档不一致**：`verify.py` 现为下界 376（不是精确钉），实测 385；`review2-spec.md` 里 `154+374` 那句是描述性括注且**该文件是 sha 钉死件不可改**——判据本身（`rc=0`、`PASS=12 REPORT=1 FAIL=0`）不受影响，执行 R2 时别把计数不符当环境漂移。
- **firecrawl 是用户级持久配置**：`~/.claude.json` 顶层 `mcpServers.firecrawl`，url=`https://mcp.firecrawl.dev/v2/mcp`（**不是**插件的 `/v2/mcp-search`，那个只收 OAuth token，key 打必 401）+ `Bearer` 头；插件缓存里的 `.mcp.json` 已回滚为 stock，**无补丁可丢**。该连接 28 个工具，故 2.0.0 净能力损失为零。已知噪声：插件那条 stock 长显 `! Needs authentication`、贡献 0 工具（消它要改 `~/.claude/settings.json`，本仓禁改）。
- 运行纪律：勿改 `~/.claude/settings.json`；论文口径禁动（26.9°/真窗 v3/R_fam 8.74/10.91）；`?? .githooks/` 勿碰。
- **断言判别力**（本会话多踩，已入记忆）：`==` 两侧出现同一函数名（尤其一侧显式传默认值）＝自比恒真；期望值须取自被测之外，并**当场做判别力实测**（漂一点被测，断言必须红）。含反引号/`$` 的长文本走 `python - <<'PY'` 引号定界 heredoc，写完回读校验。
- 书的钉值是 **sha256**，`git hash-object` 给的是 sha1 blob——对不上属正常，别当漂移证据。
