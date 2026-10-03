---
name: remember-store-layout-and-core-gc-20261001
description: 注入源=<project_dir>/.remember/core-memories.md（非 ~/.remember/claude-code/）；2026-10-01 两处 core-memories 季度 GC 完成（项目店 26→8 节、跨项目店 90→70 节）
metadata:
  node_type: memory
  type: project
  originSessionId: 73a7ff6b-571d-4056-818e-932e947d01ff
  modified: 2026-10-01T03:01:53.393Z
---

**事实（2026-10-01 实测）**：SessionStart 注入的 `core-memories.md` 是 **`<project_dir>/.remember/core-memories.md`**
（remember 插件按 project_dir 定位 store；planning-paper 的注入源即仓库内 `.remember/`），**不是**
`~/.remember/claude-code/core-memories.md`（旧布局，本仓会话不注入它）。判据：把 harness 落盘的 SessionStart hook
输出（`~/.claude/projects/D--hermes-my-workspace-projects-planning-paper/<sid>/tool-results/hook-*-stdout.txt`
的 `--- core-memories.md ---` 段）与本仓 store 文件逐行 diff，**只差末尾一个空行**（33870 vs 33869 字节）。

**Why：** 曾用 `~/.remember/claude-code/core-memories.md`（那里确实有 124KB 的**另一个**同名文件）去比对注入块，
得出"注入不含最新条目、最近的教训没进上下文"的错误结论。比较"注入 vs 磁盘"前必须先确认注入源，
同名文件不等于同一文件。

**How to apply：** 报记忆状态、量注入成本、做记忆 GC 前，先确认 store 路径（`<project_dir>/.remember/`），
再动手；不要按 `~/.remember/` 下的目录名猜。

**本次动作（2026-10-01 季度 GC，rule 15 记忆同法，归档不删）**
- 项目店 `D:\hermes\...\planning-paper\.remember\`：`core-memories.md` 33,869 → 10,000 字节（26 → 8 节），
  18 节原文照录移入同目录 `core-memories-archive-20261001.md`（23,182 字节），保 `.bak-20261001`。
- 跨项目店 `~/.remember/claude-code\`：`core-memories.md` 127,003 → 94,209 字节（90 → 70 节），
  20 节移入同名 archive（33,209 字节），保 `.bak-20261001`。判据 = 该节自带 `auto memory:` 镜像声明且抽查命中
  （抽 10 个名字全部存在）+ 会话规则遵守复盘类（产出已在规则层）。判据不单点：镜像声明之外，还要求该节是已闭弧。
- 归档件不被注入：插件只注入六个固定文件名（identity / core-memories / today-<date> / now / recent / archive），
  rotated 列表只 glob `archive-*.md` / `recent-*.md`，本文件名不匹配。
- 两个 store 均被 `.gitignore`（内容 `*`）排除：**归档件与 `.bak` 是唯一副本，禁当垃圾清**。
- 未动：`~/.remember/hermes/`（9KB、末条 08-09、内容为各项目已闭弧，消费路径未知）；
  `~/.remember/zcode/`（另一工具 store，只修本会话追加段的换行，不改其既有条目）。

**EOL 教训（本次踩到）**：claude-code / zcode 店是 CRLF，而 bash `printf '%s\n' >> file` 追加会造**混合换行**
（claude-code 实测 879 CRLF + 49 裸 LF）。追加 store 记忆用 Write 工具或显式 `\r\n`；GC 工具已加
"混合换行即中止，统一后保持文件原约定"。

**Why：** 项目店每会话注入，26 节里多数是已闭环的项目事件；durable 教训已落在 auto-memory（feedback-* / project-*）
或全局规则里——只留 8 节 = 每会话省约 23KB（首轮误判 2 个无镜像条目，独立复核后回填）。
rule 15 对记忆的规定是"移出、归档不删"，不是删除。

**工具**：`~/.agents/scripts/gc-core-memories.py`（`--file/--prefix-file/--tag/--mode lock-write|atomic-replace/--dry-run`）。
默认 **lock-write**：本机探针实测——持任何句柄都让 `os.replace` 报 WinError 5；锁在 EOF **之内**挡不住追加；
锁在 EOF **之外**只挡旧 EOF 之后那一段，**原地改写一 truncate 就失效**（复核实证：锁只覆盖旧 EOF 之后 = 从没挡住过任何追加）。
正解 = 锁 **[0, size+4096)**（整个文件 + 下一次追加的落点），锁下 `ftruncate`+分段写；解锁用**同一区间**。
实测：truncate 前/后/写到一半的追加**全部 Permission denied**，解锁后追加正常；61MB 竞态两模式全绿，复核方 13 时点 + 3 窄窗 + TOCTOU 写方 + 抢锁写方，**0 丢失/0 静默丢**。
**恢复标记** `.gc-incomplete`（截断前写、read-back 后删）内记 `tag/src/bak/archive/prefixes/decisions`——
下次跑见标记即 rc 11，按标记里的**那次 run 的**路径打印恢复步骤（含要删的侧件，防 rc 6 死锁）；dry-run 遇标记只告警。
代价：放弃 replace 原子性（半途死 = 半写文件，靠 `.bak` + 标记恢复）；被挡的写方**报错而非静默丢**（刻意）。
边界：改写若**变大超过 size+4096**，超出部分无锁保护——本工具只做收缩，属余量而非常态。
`atomic-replace` 保留 stage+stat 守卫+replace（原子，但 stat→replace 微秒窗仍在，且只有无人并发写时可用）。
**决策 journal**（复核方要求）：每次跑出 `core-memories-gc-<tag>.decisions.txt`——逐节 `ARCHIVE | 标题 | 命中前缀 + 该节自带 auto memory 镜像名`
或 `KEEP | 标题 | not selected`，加源 sha256/mode/计数；两次已完成的 GC 已**回填**。另有前缀清单 `<tag>.prefixes.txt`。
测试：`gc-core-memories.selftest.py`（10 例）+ `gc-core-memories.racetest.py`（61MB 竞态、两模式各 5 时点）。

**How to apply：** 下季度照此形状走：`--dry-run` 先看名单 → 逐条核镜像（名字要真存在）→ 独立 subagent 复核
（逐节 verbatim + 逐节找镜像证据 + 查误归档）→ 跑 closeout-sweep 核基线。
