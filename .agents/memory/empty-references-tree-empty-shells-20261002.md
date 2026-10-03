---
name: empty-references-tree-empty-shells-20261002
description: 16 个 ppw-* 论文写作技能是 README 二次转写品，80 条 references 引用零可解析，触发即静默失效——已备份删除；含上游 34.5k star 但无人报告失效的调查结论
metadata:
  node_type: memory
  type: project
  originSessionId: db31c19b-4aa5-4c94-8c0b-5c9252951e97
  modified: 2026-10-02T15:49:14.279Z
---

2026-10-02 删掉 16 个从第三方 README 转写的论文写作技能（15 个 `ppw-*` + `paper-polish-workflow` + `get-paper`），备份在 gitignored 的 `.agents/skills-archive/`。

**根因**：它们声明 80 条 `references/` 引用（`expression-patterns`、`anti-ai-patterns`、`journals/`、`skill-conventions.md` 等），**可解析 0 条，断链率 100%**。`.agents/skills/` 下只有 SKILL.md，整棵 references 树从未存在。技能 Step 0「加载 references」第一步就落空 → **静默失效**：会话里技能清单照常列出、description 照常匹配，用户以为有能力，实际触发即断。之所以一直没暴露：从未被触发过。

**上游核查（关键，别再重复查）**：
- 自报来源 `github.com/Leey21/awesome-ai-research-writing`，但该仓全仓**仅 4 个文件**（README.md + images/），**无任何 skill 目录、无 references**，README 里也 0 次提及 `expression-patterns` 等
- 上游 README 的 Skills 总览只有 5 个（`20-ml-paper-writing` / `humanizer` / `docx` / `doc-coauthoring` / `canvas-design`），**没有一个叫 `ppw-*`** ⇒ 本地这批是**二次转写品，非官方发行**
- 34,511 star / 2,478 fork，但**贡献者仅 3 人**（作者本人 43 次提交），30 天 PR = 0，最近提交 2026-08-19
- **20 个 issue 无一条报告技能失效**，全是索要 prompt / 问模板 / 提改进（`#30 缺论文模板` 最接近）⇒ 多数人把它当 prompt 收藏夹，不是当 skills 用

**处置**：删除而非补齐——上游没有可补，且即便补齐也是我伪造的内容，会掩盖「整套references 缺失」这个事实，比现状更坏。同时清掉 `CLAUDE.md` 的 6 处失效技能引用，改为登记移除原因 + 上游链接。

**同类判据（可复用）**：技能/skill 报「引用某 references 文件」时，**先确认那棵树是否存在再谈别的**。这次是先量了「16 技能 / 80 引用 / 0 可解析」，才发现不是单点死链而是全空壳——而 better-harness lint 只报了 1 条（`ppw-update:156`，因它写了绝对路径而其余 14 个写相对路径未被匹配），差 15 倍。见 [[feedback-grep-filename-is-not-reading-content]]（grep 命中≠核对成立，此处同型的另一面：**lint 报一条≠只有一个问题**）。

**未做（留痕）**：`.planning/workflow-memory.json` 里两条 `ppw:*` 记录保留未删——它是历史数据不是损坏资产，且已无读取方（唯一读者是刚删的技能）；其余 memory/plan 文档中的历史提及同样保留。

相关 [[paper2-goal-card-handoff-20261002]] [[feedback-grep-filename-is-not-reading-content]]。