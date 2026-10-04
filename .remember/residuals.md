# Residual ledger

Open items that survived a session. A row leaves this table only by being closed (evidence) or declared wontfix (reason) — never by being copied forward untouched.

```ledger
| id | item | status | first_seen | last_moved | close_condition |
|---|---|---|---|---|---|
| R1 | 跨项目 store GC：~/.remember/hermes/ (9KB) 与 ~/.remember/zcode/ (18KB) | wontfix | 2026-10-01 | 2026-10-01 | 下季度 GC 或用户点名 |
| R2 | 事故证据件 ~/.claude/tmp/now.md.corrupt-1950 (11B) | closed | 2026-10-01 | 2026-10-01 | NDC 竞态已沉淀，确认无后续用途即删 |
| R3 | GC 工具两条已知边界（改写变大超 size+4096 无锁保护；守卫只 stat） | wontfix | 2026-10-01 | 2026-10-01 | 需要零窗口时上文件锁 |
| R4 | GC 工具未归档判定 journal | closed | 2026-10-01 | 2026-10-01 | 已实现 |
| R5 | 两工具共享插件的版本差异：caveman 2.4.0 (vendors) vs 3.0.0 (plugins/cache)；better-harness 0.6.5 vs 0.5.0 | closed | 2026-10-01 | 2026-10-01 | 决定升级哪一侧或接受差异（caveman 2.4.0 的 VALID_MODES 与 3.0.0 一致，规则措辞两侧均成立） |
| R6 | better-harness 现为 0.7.0-alpha2（上游 latest）—— alpha 是否接受，或退回 0.6.5 | wontfix | 2026-10-01 | 2026-10-01 | 用户裁决；影响 Claude 侧 better-harness 插件的 review-trigger 行为 |
| R7 | 技能上游映射：9 pinned + 12 名字候选（10 个本地已改需逐个核 diff）—— 核完才能对齐升级 | open | 2026-10-01 | 2026-10-03 | 逐 skill diff 人审后按 skill-sync apply；禁盲自动 |
| R8 | 重复副本裁决：ARS 技能（academic-paper/-reviewer/-pipeline/deep-research）插件已托管，~/.agents/skills 散副本是否退役；vendors 与 marketplaces 是否单源 | closed | 2026-10-01 | 2026-10-01 | 单源决策（用户的「双份共享物只有单源或机械核对」原则） |
| R9 | paper2 延后债里「可执行有验收」的两项：#1 exit-11 空前沿构造测试、#11 test_aasr_grid.py:152 测试自指（补不变量断言+变异红证） | closed | 2026-10-01 | 2026-10-02 | **2026-10-02 重挂具体化**：并入票 21（其验收预期零代码改动，与 exit-11 构造测试相容）或票 17 门禁扩展；自指项须补不变量断言 + 变异红证。新关闭条件 = 票 21 或 17 开工时同批落地，或用户判 wontfix |
| R10 | paper2 延后债外部触发型 7 项（#2 AASR 窗内 enforcement / #3 _build_dense 重积分 / #4 变异日志 / #7 Mittermayer 付费墙 / #8 fork 守卫作用域 / #9 nesz.py 零消费者 / #10 AASR 谓词零接线） | wontfix | 2026-10-01 | 2026-10-01 | 已判 wontfix：触发条件（审稿人质疑 / 后续票改共享符号）写在 paper2-deferred-debts.md，触发前无动作 |
| R11 | 上轮 handoff Next 未动的两项：paper2 票 21/22 未开工；下季度记忆 GC | closed | 2026-10-01 | 2026-10-02 | 票 21/22 开工（无前置）；记忆 GC 到下季度或用户点名 |
| R12 | paper2 exit-11 CLI 不可达（票21 R9#1 施工挖出）：run_pilot 先算 anchor 触发 nsga2.py:178 seed-cv 断言 exit 1，到不了空前沿分支 | open | 2026-10-02 | 2026-10-03 | 修 run_pilot 在 anchor 前判 any(p.schedulable) 后，删 test_pilot_exit_codes 的 strict xfail 标记 |
| R13 | 第二处测试自指（票21 收工举一反三扫出，与 R9#11 同根）：test_duration_models.py:309 断言 sat_margined_s == sat_raw_s * SAT_MARGIN_KIM，而 duration.py:175 正是这么算的 ⇒ 改常量两侧同变，实测 margin 0.5~99 断言全真，零判别力 | open | 2026-10-02 | 2026-10-03 | 补 SAT_MARGIN_KIM==1.25 的独立取值断言（1.25 来自 Kim p.7/p.11 的 25% 裕度，已在票21 F2 核过四处原文）；或把断言改成对 1.25 字面量。连带扫其余 assert 引用本模块常量的测试 |
| R14 | 第六处口径分裂：`boundary_rate` 读库 R0（C2 杠杆项 ±42%）| closed | 2026-10-03 | 2026-10-04 | **票 23 关闭（dd3aa92/d4921e9）**：r0_m 全链透传 + 变异红证 6/6 + 守卫测试。影响实测（非假设）：manifests 40/40 byte-identical；R1C 全 STR 零数值变化；R2F/R3H/R4H 23-30/40 单元经 C2 model 分支+SPT kat0 变化；需求漂移 ~1e-3 s/对（bisect 判别器实测）；「修=作废 270 单元」前提被证伪。真窗阶梯 120/120 exit0 重跑；R_fam 判词不变；promotion 未触发不变 |
| R15 | `footprint_ok` SPT 足印界读库 R0（同 R14 根因）| closed | 2026-10-03 | 2026-10-04 | **票 23 关闭**：门移入 pass 循环按该 pass r0_task 判定，级联归因保模板序。实测：R 族零任务受影响（足印 diff 类为空、manifests byte-identical）——r0_task∈[817,1024] km 全高于库 768 km 且 fine SPT l_az≤3 km 低于物理最小界，结构性 no-op（gate-review Y2 预测命中） |
| R16 | `check_red_lines.py` 禁令分类器对**逗号/破折号/转折词连接**的洗白句仍放行（第四轮独立审查指出）：`"Denying a phase transition is forbidden, yet our front collapse is real."` 判 0 违规。当前语料零命中（rc=0）故为已知边界非活漏洞 | open | 2026-10-03 | 2026-10-03 | 未来语料出现该句式前修分类器；修法是把 `CLAUSE_END` 从句/分句扩展到逗号与转折词，或改为要求标记与被禁词在同一子句内 |
```
