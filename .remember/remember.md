# Handoff

## State
- paper2 写作期**未开**——卡在 A-CROSS 未决（SLS 天线扫描律：恒定角速率 vs 对准旋转中心；决定 (b) 重跑是否幻影修复；代码 duration.py=(乙律)/aasr.py=(甲律) 混用确凿）。
- 本会话已提交：ff2c627/fdb4238/9ed593d（票35/36/37）+ 1da97a0/96af405（台账·handoff）。HEAD=96af405，树净 0。全量测试 369P/0F。
- 票 38 已更新（三条新纪律并入 + Blocked-by 加票39）；R29 关闭（.scratch 维持 ignore，锚点改 blob hash）。台账 open=3（R7/R19/R27，均带触发、不阻塞）。

## Next
1. **票 39 先**（关键路径）：交高端档跑 A-CROSS——票面已备 GF-3/Kim/Prats/Mittermayer 引证 + 两分支 + 硬约束「须三角核、不只信这两篇」。定案前不动代码/不重跑/不开写。
2. **票 38 后**：workflow v3 落地，吃 39 结局（改 aasr→结构不变；改 duration→插「重跑+复审」段+取数 v3→v4）。早做有 ~50% 返工风险，故串行。
3. 写作期开工（待 39+38）：走 `writing-workflow.md` v3。

## Context
- 探针票 34：「28% f>2」是**全窗口径**，有效可行窗子集远小（p50 f≈1.004）——别再用全窗数。
- a_res 仅存在于 aasr.py（已核）；26.7567°=arccos(√k) 是给定 k 的推导值非物理墙。
- 三条新纪律（票 38）：语义集冻结闸 / 前提先于量化 / 多审者冲突强制多源仲裁——治「物理诊断反复翻转」。
- 教训沉淀：feedback-relay-without-verify、feedback-physics-semantics-freeze-gate、变异测试禁 git checkout、subagent 403/429 重派带 model。
- FE 拦 .py 改需建票+Tier+`.gates/current-ticket`；`.scratch` gitignore（规划工件走 blob hash 锚）。
