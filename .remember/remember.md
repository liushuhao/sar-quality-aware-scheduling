# Handoff

## State
- paper2 写作期**未开**——卡在 A-CROSS 未决（SLS 天线扫描律：恒定角速率 vs 对准旋转中心；决定 (b) 重跑是否幻影修复；代码 duration.py=(乙律)/aasr.py=(甲律) 混用确凿）。
- 本会话已提交（repo）：ff2c627/fdb4238/9ed593d（票35/36/37）+ 1da97a0/96af405/7b64a98/13112fb（台账·handoff）。HEAD=13112fb，树净 0。全量测试 369P/0F。
- 规则层（全局，非本仓）：新建 `~/.claude/rules/paper-writing.md`（三条纪律）；`research-ideation.md` 拆分 27→24 行。票 38 已含三条纪律引用；R29 关闭（.scratch 维持 ignore，锚点走 blob hash）。台账 open=3（R7/R19/R27）。

## Next
1. **票 39 先**（关键路径）：交高端档跑 A-CROSS——票面已备 GF-3/Kim/Prats/Mittermayer 引证 + 两分支 + 硬约束「须三角核、不只信这两篇」。定案前不动代码/不重跑/不开写。
2. **票 38 后**：workflow v3 落地，吃 39 结局（改 aasr→结构不变；改 duration→插「重跑+复审」段+取数 v3→v4）。
3. 写作期开工（待 39+38）：走 `writing-workflow.md` v3；模型/数据层纪律见 `~/.claude/rules/paper-writing.md`。

## Context
- 探针票 34：「28% f>2」是**全窗口径**，有效可行窗子集远小（p50 f≈1.004）——别再用全窗数。
- a_res 仅存在于 aasr.py（已核）；26.7567°=arccos(√k) 是给定 k 的推导值非物理墙。
- 三条新纪律已升全局规则 `~/.claude/rules/paper-writing.md`（2026-10-07，两轮独立审零 🔴）。
- rules/*.md **每会话全量注入**（非「按引用读」）⇒ 加规则=加基线；改 rules 须同步 `~/.zcode/AGENTS.md`（字节级闸）。
- 教训沉淀：feedback-relay-without-verify、feedback-physics-semantics-freeze-gate、feedback-rules-autoload-and-tier-choice、变异测试禁 git checkout、subagent 403/429 重派带 model。
- FE 拦 .py 改需建票+Tier+`.gates/current-ticket`；`.scratch` gitignore。
