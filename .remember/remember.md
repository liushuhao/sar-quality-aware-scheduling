# Handoff

## State
- paper2 写作期**未开**——卡在 A-CROSS 未决（SLS 天线扫描律：恒定角速率 vs 对准旋转中心；决定 (b) 重跑是否幻影修复；代码 duration.py=(乙律)/aasr.py=(甲律) 混用确凿）。
- 本会话完成：票 34/35/36/37 回写 completed（验收勾选，36 ⑨⑩ 延后并入票39）；`.gates/current-ticket` 清空；「票 Status 回写」升通用规（dev-workflow「票生命周期纪律」+ shutdown step5③「票账对齐」）；§4 改三段链镜像 claude→agents→zcode + 清 closeout-sweep.py 旧名引用。
- HEAD=7b64a98，repo 树净 0；sweep FAIL 0/NOTE 0。治理件改动备份 `~/.claude/backups/rules-extend-20261007-074926/`。

## Next
1. **票 39 先**（关键路径，唯一高端档票）：交高端档跑 A-CROSS——票面已备 GF-3/Kim/Prats/Mittermayer 引证 + 两分支 + 硬约束「须三角核、不只信这两篇」。定案前不动代码/不重跑/不开写。
2. **票 38 后**：workflow v3 吃 39 结局（改 aasr→结构不变；改 duration→插「重跑+复审」段+取数 v3→v4）。
3. 写作期开工（待 39+38）：走 `writing-workflow.md` v3。

## Context
- A-CROSS 两分支：判同步律→改 aasr 的 K_c、a_res≡A、无边界、无需重跑；判恒定律→改 duration、26.7567° 边界真实、需重跑全矩阵。
- 三条新纪律已升全局规则 `~/.claude/rules/paper-writing.md`（语义集冻结/口径随数字携带/前提先于量化，2026-10-07）；票 38 引用之。
- 台账 open=3（R7/R19/R27，均带触发、不阻塞）。探针票34：「28% f>2」是全窗口径，有效子集 p50 f≈1.004——别再用全窗数。
- now.md 有并行写入者（07:55 `paper-writing.md` 条目非本会话）——收尾勿碰非本会话产物。
- FE 拦 .py 改需建票+Tier+`.gates/current-ticket`；`.scratch` gitignore（规划工件走 blob hash 锚）。
