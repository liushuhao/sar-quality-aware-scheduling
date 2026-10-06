# Handoff

## State
- paper2 写作期**未开**——卡在 A-CROSS 未决（SLS 天线扫描律：恒定角速率 vs 对准旋转中心，决定 (b) 重跑是否为幻影修复；代码 duration.py=(乙律)/aasr.py=(甲律) 混用确凿）。
- 本会话已提交：ff2c627 票35 死分支双修 / fdb4238 票36 登记更正(族级 f_q 范围+stratum) / 9ed593d 票37 红线全量覆盖+数字回源工具 / 1da97a0 台账。HEAD=1da97a0，树净 0。全量测试 369P/0F。
- (b) 重跑决策**挂起**：原据「驻留∝1/a_res」+「28%」两处未验证转述，已被换模审者推翻（a_res 是 AASR 谱因子）。

## Next
1. **A-CROSS**：票 39（`.scratch/sliding-spotlight-scheduling/issues/39-*`）交高端档跑——票面已备 GF-3/Kim/Prats/Mittermayer 原文引证 + 两分支 + 硬约束「不只信这两篇、须三角核」。定案前不动代码/不重跑/不开写。
2. **.scratch 被 gitignore**（台账 R29）：票 34-39/判词文件未跟踪，票 38「钉 hash」落不了地。用户裁决 ①改 .gitignore 放行 或 ②接受无版本历史。
3. 写作期开工（待 A-CROSS）：走 `.scratch/.../writing-workflow.md` v2 + 票 38 落地后的 v3。

## Context
- 探针票 34 已跑：322 SLS 任务，「28% f>2」是**全窗口径**，有效可行窗子集远小（p50 f≈1.004）——别再用全窗数。
- 换模多路审结论：a_res 仅存在于 aasr.py（已核）；26.7567°=arccos(√k) 是给定 k 的推导值非物理墙。
- 台账 open=4（R7 技能半/R19 Ch5票27/R27 锚点漂移/R29 .scratch）；FE 拦 .py 改需建票+Tier+`.gates/current-ticket`。
- 教训已沉淀：transposed findings 前先验前提（feedback-relay-without-verify）、变异测试禁 git checkout、subagent 403/429 重派带 model。
