---
name: feedback-remember-ndc-race-truncates-now
description: remember 0.33.0 的 NDC 压缩与追加竞态会把 now.md 写成只剩几字节；收工后必须验 now.md 可解码，今日内容在 today-*.md 核
metadata:
  node_type: memory
  type: feedback
  originSessionId: 73a7ff6b-571d-4056-818e-932e947d01ff
---

remember 插件 0.33.0 的 NDC（now.md → today-`<day>`.md 压缩）与"压缩期间有人追加"竞态时，
会把 `now.md` 写成只剩被保留的那几字节——**文件被毁，但当天内容在 `today-<day>.md` 里完好**。

**Why：** 2026-10-01 19:50:37 实测：项目店 `.remember/now.md` 从 7,888 字节变成 **11 字节**（UTF-8 不可解码，
内容是"…跑完。"的字节尾巴，还切在一个多字节字符中间）。插件自己的日志给出全过程：
`19:49:35 [write] appended ## 19:49 | main` → `19:49:37 [ndc] now.md -> today-2026-10-01.md` →
`19:50:38 [ndc] kept 11b appended during compression` / `7888->6180b (-21%)`——即压缩窗口里检测到追加，
保留逻辑按**字节偏移**切尾，最终提交只剩这 11 字节。当天内容未丢：`today-2026-10-01.md`（19,837 B、
08:25→19:49 共 16 节）完好，其中还有对本次会话后段的压缩摘要。同刻无我方进程写入该文件（我的追加脚本
在写之前就抛了 TypeError）。

**How to apply：**
- 收工写完 now.md 后**立刻验证**：文件可 UTF-8 解码且字节数与预期同量级（`python -c "open(p,'rb').read().decode('utf-8')"`）；
  很小或解码失败 = 中招。
- 中了不要慌：先看 `today-<day>.md` 是否含被毁区间（通常含），再按插件缓冲语义把 now.md 恢复成
  **边界之后的内容**（别把整天内容重新灌回 now.md，下一轮 NDC 会把它们二次压进 today 造成重复）。
- 报 store 状态时别只报 `now.md`——它是缓冲，真值是 `today-*.md` + `core-memories.md`。
- 这是第三方插件缺陷（0.33.0，NDC 提交路径）；本地可做的只有"写完即验 + 可恢复"，别改插件的 cache 逻辑
  （插件更新会覆盖）。

见 [[feedback-live-file-write-guards]]（活文件读改写的并发守卫）、[[remember-store-layout-and-core-gc-20261001]]（store 布局与 GC）。

**第二次实证（2026-10-01 22:28，同一会话内两犯）**：收工写 now.md 后，落在插件 NDC 压缩窗口内的追加再次被
「保留」成**唯一内容**——`[write] appended: ## 22:26 | main` → `[ndc] now.md -> today-*.md` → 收工条落在窗口内 →
`[ndc] kept 1275b appended during compression` / `11101->9413b (-15%)` → **now.md 只剩这 1275B**（头部还切在多字节字符中间）。
内容未丢：压缩后的历史进了 `today-2026-10-01.md`（34.7KB），条目本身留在 now.md。**上游 latest（0.33.0）仍带此 bug**，
无版本可升（按「一律 latest」政策已验）。加强措施 = **写完立刻验 + 隔 5-10 秒复验**（插件的提交发生在我们的写之后），
发现被截断即按缓冲语义重写；已写进 `~/.claude/commands/shutdown.md` 与 ZCode 侧副本。
