# Handoff

## State

- **paper2 写作期前置条件已具备（2026-10-06 写作前全面审计，零 P0）**：主线程实跑
  + 两路独立 fresh 审查（无写作会话史）交叉验证。
  - **域套件 228 passed + 1 skipped exit 0**（31m37s；pin `DOMAIN_N0=228/1/0` 精确吻合）；
  - **五道门禁 rc=0**：红线 0 违规/193 文件、溯源 11/11 claims、v3 判决 33 checks、
    prereg v2 28 checks、票 22 43 checks；
  - **双实现比对 PASS**（`compare_v3_recheck.py`：30/30 工件、9 字段 + 5 run 输入**零差异**、
    全部 exit 0）；数据可取性实测：90 单元（3 族×3 预算×10 seed）全在盘 tracked，
    **max spread 3.9722 dB 逐位复现**、90/90 `no_promotion`；
  - **31 票状态**：01–26 + 28–31 全 `completed`；27 `blocked`（触发 = Ch5 重构）。
- **本轮处置 commit `d28052a`**——三项 P2 登记精度缺口，**纯登记：零公式 / 零代码 /
  零数据 / 零阈值**（3 文件 +61/−2）：
  - **①SLS 26.9° 是保守上界，不是精确物理边界**。精确根 `arccos(√k)=26.7567°`
    （`a_res=1−k/cos²ψ=0`），26.9° 处 `a_res=−0.002533` 已在域外，宽 0.1433°。
    **数据影响实测为零**：v3 全部 **1673 个 SLS 任务窗入射角 ∈[30.032°, 59.967°]**，
    与 band 零交集。⇒ **选登记不修码**（修则须 6h 重跑 90 单元换零收益）；
    修复触发条件已登记（任一场景入射角落入该 band 时改常量为 `arccos(√k)` 并复跑）。
  - **②formula-spec §4.2 的 `T_scene_SLS` 为 stale 侧**（`W_a` 在 sec² 外）；
    代码 oracle `duration.py:201-206` + §8.9-1 的 **+0.4185% @12°** 为正典。
    oracle 仅测试比对件、不进生产 ⇒ 零数据影响。
  - **③RUN_LINEAGE N2 只引 L2 单值 3.891 dB，漏 L3**。逐档重算：
    L1 **1.0137** / L2 **3.8906** / L3 **5.0009 dB** ⇒ 结论 no_promotion **不变**（全 < 6.0）。
  - 另登记两项精度缺口：caliber 门禁**不强制 v3 条目**（删之仍 PASS）、v2 caliber **无 `code_head`**。
  - **改后已验**：五门禁 rc=0 + 守卫子集（fixture 漂移 + 溯源 + 谱系完整性）**30 passed exit 0**。
    本轮零代码改动，故 228P 全量套件无需重跑（本会话早前已实跑）。
- **写作义务清单 43 → 46 项**（`writing-checklist-20261005.md`，gitignored）：
  新增 **F-8**（禁称 26.9° 为精确物理边界）/ **F-9**（禁引 §4.2 场景式字面）/
  **D-6**（引 `v2_results/confound_control.json` 须注「v2 caliber，产出 commit 未登记」）。
- **本会话故障归零**：rtk 管道**可在退出码不变（rc 仍 0）的前提下伪造 stdout 摘要**
  ——`pytest --collect-only -q | tail` 报假「No tests collected」，裸命令实为
  `229 tests collected`，**两路 rc 都是 0**。已沉淀：计数/摘要只信裸命令或落盘文件。
  `symptom-fix-gate` 对 `d28052a` 判 SUSPECT（信号 4）经六闸逐条填写判为**误报**——
  改的是 derivation 措辞串非数值，且删除改动后 26.9° 会再被读成 `a_res=0` 精确根。
- 工作树净（`git status --porcelain` = 0）；台账 **R24 新登记**（本轮 P2，关闭条件=写作期
  消费 F-8/F-9/D-6）。

## Next

1. **paper2 写作期开工**（前置全清，本会话已复验）：写作义务清单 **46 项**
   （A★7 / B15 / C9 / D6 / E9）`.scratch/sliding-spotlight-scheduling/writing-checklist-20261005.md` 随行。
   - 取数红线：真窗走 `experiments/v3_results/`（谱系 L6）；M 族走 `experiments/results/`
     （`v2_results` 仅 `confound_control.json` 本体仍有效，但**产出 commit 未登记**）；
     **v2 真窗数字永久禁引**；**caliber 标签随行**（R 族 f_q 非归一化 31–111，M 族 [0,1]，禁混）；
     前沿/质量读数取 **160/240 档**并带 **NOT-PLATEAUED** 限定语（基档仅作欠收敛基线）。
   - δ=6.0 按 amendment 口径（「数值承继」「标定后注册」），**禁写 pre-registered effect size**。
   - 写完必跑 `python papers/sliding-spotlight-scheduling/scripts/check_red_lines.py`（rc 须 0）。
   - 数字 drift 守卫：改 `v3_results` 后须重跑 `scripts/verify_v3_verdicts.py`。
2. **开票 27 已开**（T1，`issues/27-ch5-rotation-horizon-seed-fixes.md`，Status=blocked）：
   R19 Ch5 两项物理违反 + `t_start` clamp + 种子确定性（触发 = Ch5 实验重构启动）。
3. R7/R16 台账 open 项照旧（工具链对账窗口 / 休眠触发器，2026-10-06 已复探）。

## Context

- **三层审计口径**（本会话确立，可复用）：写作期就绪判定 = ①域套件全量实跑 + ②门禁电池
  全 rc=0 + ③两路独立 fresh 审查（理论公式路 / 数据溯源路）交叉，**主线程逐条复算 agent
  报告的每条发现**（不信自述——本会话三条 P2 全部复算后才落处置）。
- **登记层与数据层分离**：`caliber_registry.json` / `RUN_LINEAGE.md` / `analysis_prereg_v2.json`
  属登记层；「文档说了什么」与「代码算出什么」错位时，改登记不动码可免掉全量重跑——
  前提是**实测证明数据零影响**（本轮=1673/1673 窗外）。
- **前情**（2026-10-05/06 /goal 会话）：Audit4 四票 28–31 闭环（`220a796`/`f546573`+`458e486`/
  `cc5849e`+`f6f229c`/`dc44012`）；票 25 真窗重设计（`0692a44`）；票 26 R20 关闭（`89041d1`）；
  分析层两决策已裁（不追预算 + δ=6.0 注册）。详见项目记忆
  `project-paper2-audit4-remediation-closed-20261006`、`project-paper2-ticket25-v3-matrix-landed`、
  `project-paper2-prewriting-audit-20261006`。
- **生成器设计要点**（写论文/审稿会用）：每趟 t_ca = 段内向量 squint 最小点（可能在带外
  近天底处——那是平面 squint 模型的锚，不是带内点）；一趟的两条带内翼合并为一个 pass；
  AASR 腿逐窗执行（比旧「只测最宽窗」更严）；决策变量 2N，过境选择隐式在 tau 里
  （测度归一化 ⇒ 采样偏向宽窗，已登记）。
