# Handoff

## State
- **票 23 completed（2026-10-04）**：逐任务 r0_m 口径收口（R14+R15+第八处 aasr_direct）。两 commit：`dd3aa92`（三函数签名+全链透传+8 测试+变异红证 6/6+AST 守卫）→ `d4921e9`（scenarios 真窗两门+verify 四镜像+DOMAIN_N0 208+recompute_r_fam.py）。真窗阶梯重跑 **120/120 exit0**（head 统一 d4921e9），旧件存档 `v2-run-preT23/`。判词全保持：R1C DEAD×CONVERGED（P1 EVALUABLE）；R2F/R3H/R4H ALIVE×UNCONVERGED ⇒ **NO CLAIM**；promotion 全档 <6.0（R2F 顶档 3.57→5.22 dB，仍未触发）。细节见 PROGRESS.md「票 23」节。
- **根因排查产出的关键事实**：台账 R14/R15 之外漏记的第八处= `aasr_direct`（库 R0 进 SPT kat0 与 promotion spread）；「修=作废 270 单元」是未实测假设——实测 R1C 全 STR 零变化、manifests 40/40 byte-identical、变化仅经 C2 model 分支（~1e-3 s/对）与 SPT kat0；R1C 注册值 4.0032 在新口径 max-over-seeds 下精确复现。
- **上游升级（用户拍板「修」）已闭环**：ARS 插件 3.22.2→3.23.0（**重启生效**）+ marketplace current + vendors ff（ARS/caveman）；`upstream-status.py` behind=0。残留：C:\Users\33151 项目路径 local-scope 旧版（ARS 3.22.2/caveman 3.0.0）与用户级混版，建议 update 或移除（subagent 审查建议，低危）。
- 台账 open=4：**R7**（12 技能名候选逐 diff 人审，整块时间）、**R12**（exit-11 CLI 不可达）、**R13**（SAT_MARGIN_KIM 测试自指）、**R16**（红线分类器逗号/转折洗白句，语料零命中）。
- 用户拍板待办：真窗三族 R2F/R3H/R4H **加预算出 P1 判决与否**（维持 NOT-YET-TESTED/NO CLAIM，不加预算即按现判词进写作）。

## Next
1. **写作期启动**（四票+票 23 全闭环，数字全部逐任务口径）：主结果表/消融/limitation 取数走 `experiments/v2_results/` + `recompute_r_fam.py`，禁引 v2-run-preT23 旧数。
2. R12+R13 同批修（独立小票，修法在 `test_pilot_exit_codes.py` docstring / 补 `SAT_MARGIN_KIM==1.25` 断言；R12 修时连带 #15 零长窗 ZeroDivisionError 守卫）。
3. R7 技能上游逐个核 diff → `skill-sync.sh apply`（禁盲自动）。

## Context
- **票 23 方法论沉淀（3 条记忆已写）**：①校准口径分裂的根因模式=「库几何基准量 vs 逐任务被测量」，静态 AST 守卫+白名单是第九处防线；②「修=X 作废」类成本声明必须实测（R14 的 ±42% 是杠杆比值非输出漂移，需求漂移被 fallback 常数与 dwell 主导项吸收）；③判别器设计：行为隔离不可能时（dwell 与 r0 共变）用 AST 结构断言补，变异红证按「整语义单元」退（半变异不红=假绿）。
- **kill test 三分支不变**：`unconverged` ⇒ 报 NOT-YET-CONVERGED + 不作物理声明 + 加预算=新决策须拍板。
- **本机陷阱（沿用）**：`run_matrix` 的 progress 守卫回退读 `_progress.json.bak`——重置时两个都要删；裸 `python` 假零绿 ⇒ 一律 `"/d/Program Files/Python/python"`；长批中途禁改 `~/.claude` 配置（hermes 热重载）；后台任务 exit code 取 raw（管道后 `$?` 拿 tail 的）。
- **冻结粒度**：`experiments/results/` 六族 196 文件零 diff 是底线；授权写入仅 append-only amendment / caliber 标记 / git tag。R_fam 口径变动走 `recompute_r_fam.py` 脚本头登记。
- **写交接件的判据**：凡写「某文件里有某内容」必须本轮打开 grep 到那一行。
