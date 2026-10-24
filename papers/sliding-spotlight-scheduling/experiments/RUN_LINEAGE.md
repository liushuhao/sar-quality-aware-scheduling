# RUN LINEAGE — papers/sliding-spotlight-scheduling/

> 手工维护的**唯一**运行谱系登记处（形态决策：2026-10-02，否决生成器脚本 —— 节点数在 10 量级，
> 生成器属过度工程）。目的：把散落在 commit message、prereg amendment、results 目录里的
> 「假设 → 冻结 → 结果 → 裁决」串成一棵树，直接服务论文的消融表与被否证路线段落。
>
> **维护规则（硬）**：`experiments/results/` 下每新增一个子目录，必须在本表登记一行；
> `experiments/v2_results/` 与 `experiments/v3_results/` 同样必须各有一行（票 30 扩展守卫）；
> 节点路径必须真实存在。由 `tests/test_run_lineage_completeness.py` 守卫，违反即红。

## 一、节点登记

| 节点 | 父节点 | 假设 / 目的（跑之前登记的） | 冻结依据 | 结果目录 | 产物 | 裁决 | 证据 |
|---|---|---|---|---|---|---|---|
| `L0` | —（根） | 驱动链可用性冒烟；M1NC 退化锚点变体 | `analysis_prereg.json` meta 声明：冻结前唯一产物即此文件 | `experiments/results/pilot/` | 1 | 保留 —— anchor baseline，f1\* 归一化的分母 | `analysis_prereg.json` meta.frozen_before_evidence |
| `L1` | `L0` | 五变体（M1NC / M2WH / M3NC / M2WF / M4WH）在主指标（`f1_star_max`、`f_q_front`、HV、晋级率）上可区分 | `analysis_prereg.json` v1.0.0，`frozen_before_evidence`（逐单元 `pilot-result/1.1` + git_head） | `experiments/results/matrix/` | 50 artifacts + `_driver.log` + `_progress.json` | 跑完 50/50 exit 0，产物齐；**晋级判据全变体未达**（6.0 dB 阈值） | `6aa365a`（冻结，先于任何 W/H 全矩阵结果）、`1b67398`（run） |
| `L1a` | `L1` | 场景 manifest 生成物的确定性与 seed 规则 | `scenario_manifest_template.json`（seed_convention D08-9：seed = variant_index·100 + seed_index） | `experiments/results/scenarios/` | 50 | 确定性成立 —— 收敛驱动重生成的 manifest 与冻结矩阵 manifest **byte-identical** | `9ef11bd` |
| `L1b` | `L1` | 独立 verifier 证据报告（非求解器自述） | — | `experiments/results/verify/` | 7 | `report_pilot` + audit20260930 报告 + `a6_adjudication_20260929.md` + `run_verify_20261006.txt` + `report_pilot_20261006.json` + `run_verify_20261006_closeout.txt` + `report_pilot_20261006_closeout.json` | `3f188d3` 起登记；**票 23 后实测回填（2026-10-04）**：12 步门禁（含首次实跑的 `snapshot_rebuild`，对 v2 syn 工件 bit-exact PASS）+ `scatter_precheck` REPORT（A6 注册升级，record 非失败）+ 0 FAIL ⇒ **12 PASS + 1 REPORT + 0 FAIL**；pilot 域=v2-run syn 工件（v1 冻结件对 v2 代码为 front 重构面，等价判据=anchor Δ=0，见 confound_control）；**audit4 re-run (2026-10-06, ticket 29, pin=223): 12 PASS + 1 REPORT + 0 FAIL; full stdout at experiments/results/verify/run_verify_20261006.txt; report JSON at experiments/results/verify/report_pilot_20261006.json**；**closeout re-run（2026-10-06，/goal 终验，pin=228）: 12 PASS + 1 REPORT + 0 FAIL（与上一轮逐 step 比对唯一步差异=域步 passed 223→228）；`run_verify_20261006_closeout.txt` / `report_pilot_20261006_closeout.json` 同目录** |
| `L2` | `L1` | **假设：front 上 distinct f_Q 的塌缩是密度驱动的物理塌缩** | density probe prereg amendment + predicates 扩 P6–P9（`predicates_calibration.json`） | `experiments/results/probe_density/` | 20 artifacts + `manifests/` 25 | **当时读作「否证」——后被 `L3` 重裁**。本层实测：frontier cliff 出现在 N=40→60 之间；晋级在**所有**密度上 dead（max 3.891 dB < 6.0，commit `0231900`）。注意「否证」的当时对象是**密度驱动**这一归因，不是 cliff 现象本身；cliff 的性质由 `L3` 裁决 | `8721f68`（prereg amendment）、`0231900`（results） |
| `L3` | `L2` | **假设：cliff 是物理塌缩，而非搜索预算不足** | `amendment_20260930_matrix_readjudication`（criteria before data；1× / 4× / 16× / 64× 预算阶梯） | `experiments/results/probe_convergence/` | 45 artifacts | **NOT-YET-CONVERGED** —— median distinct-f_Q 随预算 2 → 4 → 17 → 48，无平台期；PHYSICAL 叙述被否证。用户裁决 **path A**：改叙事/重设计实验，停止继续升级算力 | `43911b0`、`9ef11bd`、`338984e`（audit2 redline：无按密度平台期即不得声称 PHYSICAL） |
| `L5` | `L2` | 真窗族 v2 世界（caliber v2）的结果聚合件：R1C/R2F/R3H/R4H 四族在 40/60、80/120、160/240 三档的读数 | `analysis_prereg_v2.json`（2026-10-03 冻结）+ `experiments/promotion_prereg.json` 6.0 dB | `experiments/v2_results/` | 3 aggregate JSON（`results_table.json` / `convergence_report.json` / `confound_control.json`） | **M 族仍有效 / 真窗部分作废** —— `confound_control.json` 全为合成 M 族（票 25 未触及，锚点 Δ 逐位 0）**有效**；`results_table.json` 与 `convergence_report.json` 的 **R 族数字永久禁引**：它们出自 R17 断几何世界（过境由任意相位点而非真实过境枚举而来，t_ca/r0 为任务标量），票 25 实测该规则下 8 个簇 0 个可服务，场景已不存在；且被票 28 的 per-window C3/C4 口径取代（同几何最坏差 36.04%）。三件均已加 `void_realwindow` 标记块（票 30 (f)） | `experiments/v2_results/results_table.json`、`experiments/v2_results/confound_control.json`（真窗禁引标记见各件 `void_realwindow` 块） |
| `L6` | `L5` | **真窗族 v3 世界（caliber v3）**：过境枚举重设计 + per-window t_ca/r0 schema 后，R2F/R3H 的前沿是否仍"塌缩"？promotion 判决是否预算稳健？ | `experiments/realwindow_scenario_template.json` 的 `amendment_20261005_ticket25` + `experiments/v3_results/CALIBRATION_PREREG.md`（判词规则见数前冻结）；`analysis_prereg_v2.json` 的 `amendment_20261005_v3_realwindow` | `experiments/v3_results/` | 90 单元（3 族 × 3 预算 × 10 种子）+ 30 manifests + 标定表 + 机器锚 | **基预算的前沿塌缩判 SEARCH-ARTIFACT、叙事作废**（R3H 基档 6/10 单元前沿退化为单点、中位前沿 1，160/240 档回升至 140、distinct-fq 中位 99）；**R2F/R3H 结构维 ALIVE 可引、读数维 NO CLAIM**（R_fam **8.74/10.91 dB** ≥ 6.0〔(乙) 旋转中心口径，票 40 重算；旧律读数 9.75/11.99 已废——见 `verify_v3_verdicts.py` 的 `[old:]` 注释〕，为模型级结构界，非物理结论）；**R1C 结构维 DEAD**（3.9998 dB，锚点 f1* 逐位 1.0）；**promotion=no_promotion 对 16× 预算稳健**（90/90，最大 spread 3.9722 dB < 6.0）；160/240 仍单调上升未平台 ⇒ 一切前沿丰富度边界主张两向禁。**不追预算是用户 2026-10-05 裁决**，触发=审稿人要求收敛证据 | `experiments/v3_results/MANIFEST.md`、`experiments/v3_results/CALIBRATION_PREREG.md`（逐文件 md5 + 各档 code head `220a796`） |
| `L7` | `L6` | **票 48 新世界（caliber v4：分辨率逐任务硬约束 + 单目标覆盖）**：分辨率从路由键升为硬约束后，「覆盖率 vs 分辨率要求」曲线（扫需求松紧系数 s）的形状与约束的覆盖代价；合成 5 族在新模型下重跑供冻结前沿重钉。**任务总体固定**：sweep 复用 L6 的 30 份真窗 manifest，仅内存缩放 ρ_req（不重生成、不重路由）。⚠ 过渡期披露：本节点落地后、票 50 改写前，run_verify/verify_paper_numbers 等验证链仍钉 L1/L6 旧世界（append-only 修订在票 50）。⚠ **冻结态已兑现：本节点的重算触发点（票 49 验收通过）于 2026-10-20 触发，重算结果 = `L8`；本节点曲线按「票 49 落地前」口径冻结，R2F/R3H 的覆盖代价读数（−1.6/−5.5pp）自 L8 落地起停止引用** | 票 48 第 7 条冻结扫描网格：s ∈ {0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 2.0}（9 点，s=1.0=订单原要求）；基预算 40/60；判据（见数前冻结）=s≤1.5 段覆盖单调、s≥1.5 饱和对照、s<1.0 为不可服务臂；质量兑现率=描述性读数（窗选择口径：实拍窗实拍斜视 f_q ÷ 该任务全部窗零斜视最优，≤1，聚合器 `f_q_fulfillment_ratio_*`；raw f_q 列为绝对量勿作比值引用），promotion 列=vacuous 失效标记（单目标世界无 D12-3 决策）；曲线冻结态=「票 49 落地前」模型口径，重算触发点=票 49 验收通过（其落地改变滑聚/聚束两族约束松紧） | `experiments/v4_results/` | sweep/（9 s × 3 族 × 10 种子 = 270 单元，逐 s 点 `_progress.json`）+ matrix/（合成 5 族 × 10 种子重跑，50/50 exit 0）+ sweep_results.json（聚合 + 三判据机械检查）+ scenarios/（30 R manifest 字节副本自 v3_results/ + 50 M manifest **现头新生成**——见判据列漂移注记）+ platform.json（md5 `f2b6ce087bce85135ab163b98ca52126`，源=`.scratch/.../v2-smoke/platform.json` 与 L6 同源） | **曲线落地（2026-10-19），三判据三族全过**（`build_sweep_results.py` exit 0）：中位覆盖 R1C 0/0.540/1.000（s=0.8/0.9/1.0，s≥1.0 饱和 1.0）；R2F 0.446/0.683/0.960/0.972/0.976（s≥1.2 饱和）；R3H 0.230/0.545/0.927/0.974/0.979/0.982（s≥1.3 饱和）。**订单原要求（s=1.0）的覆盖代价：R2F −1.6pp、R3H −5.5pp、R1C 0**（对各自饱和值）。违例复核：9 s 点全部被服务实例（累计 ~45.4 万）违反 0.00%（无约束基线 53.2%）。s=0.8 紧臂 R1C 全 10 种子 exit 11（需求细于任务**预分配模式档位**地板——R1C 全 STR 地板 2.4669 m、0.8×订单 2.018–2.369 m 判空；模式分配按票 48 冻结，非「平台能力」上限：SPT 地板 0.3 m 存在 6.7× 空间。终审 P0 更正，计覆盖 0）。⚠ manifest 漂移注记：L1 冻结合成 manifest 与现头重生成仅 `generation_ledger.anchor_t_dispersion_max_min` 差 2 ulp（诊断字段，tasks 逐字节同，跨进程稳定）——判为 L1 冻结（2026-09-27）后解释器/libm 一次性位移（Δ=2e-8，诊断字段末两位小数差 2；double 在 1.0 附近 1 ulp≈2.2e-16，「2 ulp」为误标），v4 合成侧改现头新生成并冻结于此 | 代码 head `b25e841`（实现）+ `0c8dab8`（全量运行头，与 b25e841 零代码差量，纯 chore）+ `ea63140`（数据冻结）；判别读数（落码后真实管线）：可行宽度保留率 51.20/84.40/63.70%、裁剪 vs 整窗丢弃可服务 98.00/97.35/94.97 vs 38.00/72.86/51.36%、锚点违反 0/194+0/470+0/913；最小验证 R1C×10×{s=1.0,1.2} 违反 0/15840 |
| `L8` | `L7` | **票 49 新世界（caliber v5：B-full 任务级模式参数律，formula-spec v1.9 §8.17）**：滑聚/聚束参数随订单连续可调且在选中起拍斜视处交付分辨率=订单后，重跑「覆盖率 vs 分辨率要求」曲线；合成 5 族新模型重跑供冻结前沿重钉。**任务总体固定**：sweep 复用 L7 的 80 份 manifest 字节副本（30 R + 50 M，grandfather 模式分配不重切），仅内存缩放 ρ_req。本节点 = L7 冻结态登记的重算触发点（票 49 验收通过）的兑现 | formula-spec **v1.9** §8.17（12+13 项修订登记，gate=闸卷+18/18 探针+双轨对抗审 0 P0，commit `a3a7122`）；扫描网格沿票 48 第 7 条冻结 9 点**不变**；三判据沿 L7 预注册**原样继承**（不作利于数据的改判）；实现代码 head `50795ca`（sweep 腿为发射时工作树内容、自记 head 见读数列）；冻结数据政策显式改判重跑（票面第 9 条：数据级准入/驻留改变，非读数级） | `experiments/v5_results/` | sweep/（9 s × 3 族 × 10 种子 = 270 单元，逐 s 点 `_progress.json`）+ matrix/（合成 5 族 × 10 种子，50/50 exit 0）+ sweep_results.json（聚合 + 三判据机械检查，聚合器增 `--results` 参数默认 v4 不变行为）+ scenarios/（80 件字节副本自 v4_results，实测逐字节一致；platform.json md5 `f2b6ce087bce85135ab163b98ca52126` 命中 L7 登记）+ t49_minunit/（最小单元过程件：R1C×3 种子 + R2F_seed200） | **曲线落地（2026-10-20），继承判据如实上报：R1C/R3H 三判据全过，R2F 两条失败（机制已定谳，不 tune 判据）**。中位覆盖：R1C 0/0.540/1.000→1.0（与 L7 同形，全 STR 族参数无关）；R3H 0.483/0.688/0.949/0.977/0.981/0.988/0.988/0.990/0.990（单调✓饱和✓紧臂✓；**s=1.0 覆盖代价 −4.15pp**，较 L7 −5.5pp 收窄）；**R2F 0.976/0.974/0.976/0.976/0.996/0.996/0.992/0.992/1.0——C3 失败：紧臂 s=0.8 = 0.976 **不再下跌**（L7 紧臂 0.446 → L8 0.976，紧臂惩罚消失；⚠2026-10-20 异源审查更正：对 L8 自身饱和值 s=2.0 的 1.0，订单点代价仍 −2.36pp，原「=饱和值/−1.61pp 代价消失」系误平移 L7 读数）——机制=参数自适应吸收可行性代价（交付由构造成立，收紧订单只付驻留不付服务），正是票 49 论点的直接测量；C1 失败（两处 dip 同源同构：s=0.8→0.9 中位 −0.268pp、s=1.3→1.4 中位 −0.359pp）——以 1.3→1.4 为例：seed206 少服务一任务（task 45，**SLS**，订单 ρ=0.5574 m×s，s=1.3/1.4 为 0.7246/0.7803）f1 1.0→0.988636，seed209 多服务一任务（+0.42pp），中位移动由 206 引起——逐任务约束通道全部随 s 单调放松（SLS/SPT 驻留↓+起拍域↑、AASR ρ-不变恒等式、C3/C4 预算比≈ρ-不变、STR 裁剪域↑；80 manifest 11,885 带订单任务扫描零违例）⇒ 可行集收缩被排除；⚠2026-10-20 异源审查更正归因：R2F+R3H 全部 180 个 sweep 单元 max_f1_star==anchor_f1_star 且 search_only_max_f1_star 恒空（仅 R1C/M1NC 6 松序单元例外）⇒ dip 出在**贪心锚构造**（确定性、可复现），非 pymoo 搜索未命中，与 L3 SEARCH-ARTIFACT 判例不同构；禁作物理单调性主张的结论不变**。违例：9 s 点 tie-set 被服务实例累计 **477,308**（交付等式恒等检查在每次驻留求值 active，violation 即 raise，exit 全 0 除登记项）。紧臂结构保真：仅 s=0.8 R1C 10 种子 exit-11（STR 裁剪语义与 L7 逐字同，{0:20, 11:10} 与 L7 同构）。冻结前沿重钉：`test_verify_gate` 钉 v5 110 单元 + 无约束臂重定义（同驻留口径剥约束——剥 ρ 会连带换驻留，M2WF_seed400 实测反超 3482<3560）+ 保留率重钉 STR-clip-only 口径 **R1C 0.5114 / R2F 1.0 / R3H 0.7100**（L7 的 84.4/63.7% 含 §8.17-12 已废的 SLS/SPT 库口径窄化） | 代码 head：matrix 腿自记 `50795ca`、sweep 腿自记 `a3a7122`+工作树（12:24 发射先于 12:59 提交，树内容即后提交的 `50795ca`；2026-10-20 异源审查原位重跑 s0_8/R2F_seed200 与 s1_4/R2F_seed206，40/40 前端 starts 逐位复现）+ launcher rc=0 elapsed 4470s；判别读数：最小单元 R1C×3 种子 + R2F_seed200 完整求解路径 exit 0 / cv=0 / 0 违反；聚合器 exit 1（R2F 判据失败如实非零退出，非静默）；`test_verify_gate` 25 passed（L8 重钉）；台账 R60/R61 为本世界登记的预存债 |

## 二、并行节点（非 results 产物）

| 节点 | 目的 | 冻结依据 | 裁决 | 证据 |
|---|---|---|---|---|
| `L4` | 公式注册：`rho_a(mode, psi)` per-mode 闭式、B_D 第三方消费口径 | `formulas/formula-spec.md` v1.1（ticket 18，阻塞门） | 生产式 `rho_a(m,psi) = rho_a(m,0)/cos(psi)`，域 [0,45]°；B_D 第三方消费修正（原 `Vs·cos/rho_ach` 重复计入 cos，@45° 带宽错 29%） | `1bd49d8`、`cddcdf9` |

## 三、被否证 / 已停止的路线（negative results）

> 这三条是论文 Limitations 与 ablation 讨论的直接素材。审稿人问「为什么不继续」时，答案在这里。

| # | 路线 | 状态 | 否决证据 |
|---|---|---|---|
| N1 | trivialization（front 上 f_Q 塌缩）作为**物理**现象 | **否证** | `L3`：N=40/60/80/100 全部在预算下复活；无平台期。`6355d50` 早先已判 cliff 是 SEARCH ARTIFACT, not physics |
| N2 | 晋级判据（AASR spread ≥ 6.0 dB） | **终局口径已裁：no_promotion，终局读数** | ⚠️ **2026-10-06 写作前审计修正本行引数**（原写「`L1`/`L2`：全密度、全预算下 max 3.891 dB」——实测 **L3 未被引用**）：逐档重算最大 spread = `L1` `results/matrix` **1.0137 dB**、`L2` `results/probe_density` **3.8906 dB**、**`L3` `results/probe_convergence` 5.0009 dB**（`pilot_P7WH_seed701_p160_g240.json`）；「全预算」是 L3 的轴（1×/4×/16×/64× 阶梯），原引的 3.891 只是 L2 单值。**结论不变**：5.0009 < 6.0 仍成立、no_promotion 终局口径不动（登记见 `formula-spec.md` §8.12-1）。**票 22（A4）收敛标定 + 票 25 标定表两处均已落定**：① 读数维 —— 真窗 90/90 单元 spread ≤ 3.9722 dB < 6.0 dB，**对 16× 预算稳健**（三档 40/60→160/240），no_promotion 即终局；② 结构维 —— 按族分述，`R1C` R_fam 3.9998 dB **DEAD**（结构性不可触发），`R2F` **8.7407** / `R3H` **10.91** dB **ALIVE**（(乙) 旋转中心口径，票 40 重算；旧律读数 9.7524/11.9886 已废——见 `verify_v3_verdicts.py` `[old:]` 注释；模型级结构界，即场景允许该量级的 spread；**不是** promotion 会触发，也不是物理结论）。结构维 ALIVE 与读数维 NO CLAIM 分轴陈述，不得合并为一句。**本行不得被读作「已判该判据须重设计」** |
| N3 | `g_T` 单加权 amendment（audit2 期间草拟） | **撤回** | gate-review 实测：仅 `g_T` ON 时 `f_Q` 呈 `1/rho_a^2` 标度 → `g_T` 是平方反比律的载体，D05-5 双加权披露成立。`338984e` |
| N4 | PHYSICAL-vs-SEARCH-ARTIFACT 机器可读判据骨架 | **被 tickets 19/20 否证，已 append 绑定修正** | `338984e`：原判据在**每个**密度上都被推翻，但只活在 spec 散文中，机器可读 artifact 仍带一个已被否证的判据 → append `amendment_20260930_audit2_r1_redline`，绑定「无按密度平台期即不得声称 PHYSICAL collapse」 |

## 四、写作映射

> **真窗族的一切取数只走 `L6`（`experiments/v3_results/`）；`L5` 的 R 族数字永久禁引。**

| 论文位置 | 取用节点 |
|---|---|
| 主结果表（5 变体 × 10 seed，caliber v1 合成族） | `L1` + `L1b`（独立 verifier 报告） |
| **真窗族主结果（R1C/R2F/R3H × 3 预算 × 10 种子，caliber v3）** | **`L6`**（+ `experiments/v3_results/MANIFEST.md` 逐文件 md5 与 code head；机器锚 `scripts/verify_v3_verdicts.py`） |
| 消融 / 敏感性 | `L1a`（确定性）、`L2`（密度扫描） |
| 合成族对照（confound control，锚点 Δ 逐位 0） | `L5` 的 `confound_control.json`（**仅此一件有效**，R 族两件禁引） |
| Limitations / 被否证路线 | N1、N2、N4；真窗族的 SEARCH-ARTIFACT 判词见 `L6`（基预算前沿塌缩叙事作废，不得复活） |
| 方法约束口径 | `L4`（`rho_a` 闭式、B_D 第三消费方） |

## 五、未登记项（故意留白）

- `experiments/results/probe_density/manifests/` —— 是 `L2` 的子目录，不单独成节点。
- `experiments/v3_results/` 下的 `scenarios/`、`matrix/`、`matrix_p80g120/`、`matrix_p160g240/`
  —— 是 `L6` 的子目录，与 `experiments/results/` 下的子目录不同级，不单独成节点（票 30 守卫
  只要求这两个 results 目录**各有一行登记**，不要求其下每个子目录单独登记）。
- ticket 19/20 的原始否决记录、audit2 的 scratch 层裁决 —— 按仓库策略 `.scratch` 已 gitignore，
  正文只保留 `338984e` 的 append 结果，不在此重复。

## 六、票 50 阶段一：验证链与图的逐件处置（2026-10-21，B4/B3）

> **世界切换**：写作取数自本日起以 **`L8`（`experiments/v5_results/`，caliber v5）** 为准。
> 第四节「写作映射」的 `L6` 行保留为**冻结历史**（L6 的 verdict 仍可引，但其 promotion / R_fam /
> dq_all 读数已被票 50 amendment vacate，见 `analysis_prereg_v2.json#amendment_20261021_ticket50_single_axis`）。
> 本节逐件登记旧世界的验证链与图：**要么重指 L8，要么显式退役**，不留"旧世界仍绿"的沉默面。

| 项 | 现指向 | 处置 | 留痕 |
|---|---|---|---|
| `scripts/verify_paper_numbers_l8.py` | **新建**，读 `experiments/v5_results/` | **ACTIVE —— 论文数字闸（L8）**：覆盖率–需求曲线、兑现率三要素标签、tie-set 事实（260/260 unique f1 = 1）、anchor-optimal 258/260、STR 库地板 2.4669 m；raw 单元与 `sweep_results.json` 交叉核对，不一致即 FAIL | 本行 + 预注册 amendment `machine_anchor` + `tests/test_verify_paper_numbers_l8.py` |
| `scripts/verify_paper_numbers.py` | 钉 `experiments/v3_results/`，仅 `--paper` | **SUPERSEDED 作为论文数字闸**；保留为 v3/L6 世界验证器。每次运行打印 `WORLD: caliber v3 / node L6 -- SUPERSEDED…` 横幅，使其不能再被误当作现行闸（原"对 L8 恒绿"的失败模式） | 本行 + 脚本 docstring 的 WORLD SCOPE 段 |
| `scripts/verify_v3_verdicts.py` | v3 verdicts（R_fam/ALIVE/DEAD/no_promotion） | **保留为 L6 机器锚**；不再作论文读数闸（promotion / R_fam 读数已 vacate） | 本行 + amendment |
| `scripts/verify_prereg_v2.py` | v1 冻结件（`experiments/results/`） | **保留**：验证的是冻结前缀，amendment 为 append-only、前缀字节未动 | 本行 + amendment `_doc` |
| `scripts/check_coverage_parity.py` | v3 90/90 覆盖parity | **退役（论文用途）**：v3 世界的 90 单元 parity 不再是主结果；L8 对应读法（anchor coverage-optimal 258/260）已并入 `verify_paper_numbers_l8.py` | 本行 |
| `scripts/run_verify.py` | 显式传 `--pilot/--manifest` | **不变**：世界无关的通用 CLI，不钉任何 results 目录 | 本行 |
| `scripts/plot_fig3_quality_vs_squint.py` | 平台冻结 fixture（无 results 依赖） | **保留（阶段二已执行降级）**：平台模型图——逐模式 f_q 的量级与斜视不敏感性，是"质量模型存在"的平台证据；图内注记与 docstring 已去掉目标语义，PDF 已按新注记重绘；不读任何 results 目录，故不会随重跑过期 | 本行 + `paper/figures/fig3_quality_vs_squint.pdf`（已重绘） |
| `scripts/plot_fig3_coverage_vs_requirement.py` | `experiments/v5_results/sweep_results.json` | **新建 = 新主图**：覆盖率–需求曲线（9 点、三族、种子散布）；不可行点画成"无可行解"而非 0 覆盖；两处 dip 原样画出不平滑；输出 `paper/figures/fig3_coverage_vs_requirement.pdf` | 本行 + 该 PDF + `reading_ledger_l8.json` |
| `scripts/plot_fig4_budget_ladder.py` | v3 三档预算阶梯 | **退役（阶段二已执行：脚本与 PDF 一并删除）**：L8 扫需求轴只有单一预算 40/60；"搜索相对锚点的增益分布"不作为替代件——258/260 单元锚点已最优，增益分布近乎全零，画出来会被读成前沿丰富度读数（同样已 vacate），而该事实以标量在台账 `demand.anchor_optimal_units` 报出 | 本行 + 删除记录 |
| `scripts/plot_fig5_promotion_two_axis.py` | v3 promotion / R_fam | **退役（阶段二已执行：脚本与 PDF 一并删除）**：单目标世界 promotion 为 vacuous 标记；需求满足面证据（477,308 服务实例 / cv 恒 0 / 不可行语义分列）是计数不是图，落 `reading_ledger_l8.json` 的 `demand.*` 条目，不另造图 | 本行 + 删除记录 |
| `scripts/plot_fig6_per_mode_decomposition.py` | v3 manifests + 库常数 | **退役（阶段二已执行：脚本与 PDF 一并删除）**：该图是双目标叙事的解释器，且数据源是 v3 世界与库常数；兑现率读数的解释已由台账的分族读数与口径标签承担，按 L8 重做属新的注册读数（本阶段未奉命） | 本行 + 删除记录 |
| `scripts/plot_fig7_power_curve.py` | v3 `dq_all` power | **退役（阶段二已执行：脚本与 PDF 一并删除）**：`dq_all` 已 vacate，power 曲线无功效对象；本阶段未获新的已注册功效问题，故不重指 | 本行 + 删除记录 |

> **阶段二已执行**（2026-10-21）：fig4/5/6/7 的绘图脚本与 PDF **一并删除**（不是只标记退役）；fig3 平台图已按新语义重绘；新主图已落地。
> `verify_paper_numbers_l8.py` 当前对正文的实跑结果：**rc=2（NO L8 NUMBERS WERE EXTRACTED）**——正文仍是 v3 世界数字，
> 这是"未就绪"的显式报告，不是 pass（readings-only 模式 rc=0）。
>
> ⚠ **构建中断（阶段二→阶段三之间的已知态）**：正文 `paper/main.tex` 仍 `\includegraphics` 四件已删 PDF
> （`main.tex:235` fig7、`:262` fig5、`:277` fig4、`:297` fig6；`paper/full.md` 对应位置同），
> 故此区间内 `pdflatex` 会 fatal。这是"图件真退役"与"本阶段禁改正文"两条约束的直接后果，不是遗漏：
> 阶段三改写这些图槽时一并移除引用。恢复单件用 `git checkout -- <path>`（四件均为 git 跟踪文件）。
>
> **状态取代说明（阶段五追加，2026-10-21）**：上方三行（rc=2 与构建中断）是**阶段二当刻**的记录。阶段三改写后正文已含 L8 数字，`verify_paper_numbers_l8.py --paper main.tex --paper full.md` 转绿；阶段五（票 50 终审处置）把该闸覆盖面从每稿面 18 项扩到 **68 项**（逐句全数断言 + 新增 dip/逐种子位移/交付口径/模式地板/普查计数类）。旧行号（`main.tex:235/:262/:277/:297`）为阶段二行号。详见 `.scratch/sliding-spotlight-scheduling/t50/phase5-receipt.md`。

## 七、票 50 阶段二：数据面与图面（2026-10-21）

| 项 | 处置 | 留痕 |
|---|---|---|
| `experiments/v5_results/reading_ledger_l8.json` | **新建 = L8 读数台账**（生成物，禁止手改）：27 个族-s 点的中位/最小/最大/逐种子、exit-11 状态、相对各自饱和值的覆盖代价、两处 dip 的逐种子位移、服务实例总数、三判据、兑现率、覆盖-兑现相关系数、保留率镜像、交付口径变体 | `scripts/build_reading_ledger_l8.py`（`--check` 重算比对，漂移即 rc=1）+ `tests/test_reading_ledger_l8.py` |
| `scripts/verify_fq_deliv_minunit.py` | **新建 = 交付口径最小单元独立核对**：从原始 manifest 自带窗口查询与斜视算术重算，与实现路径要求 1e-12 一致（实测逐位相等）；并验 STR 任务级请求必 raise、`sec^2 12° = 1.0452` 与 `rho_req=D/2` 闭式两个注册锚 | 本行 + 阶段二回执 |
| `paper/figures/fig3_coverage_vs_requirement.pdf` | **新建 = 新主图**（替换退役的 fig3 槽位；文件名写死，阶段三按此引用） | `scripts/plot_fig3_coverage_vs_requirement.py` + 本表首行 |
| 台账的退役世界禁项清单 | **全局唯一定义**落在台账 `manuscript_ban_list`（真禁项 5 条 / 允许但须同标签注 5 条 + 标注正则）；`verify_paper_numbers_l8.py` 与阶段三都读这一份 | 台账 `manuscript_ban_list` + 回执 |


> **红闸扫描域变更（主线程裁定，2026-10-21，票 50 阶段一遗留项）**：`check_red_lines.py` 的 `_is_manuscript_shaped` 把 `review/` 目录**移出**写作禁语扫描面。
> 理由：`review/` 是审计与对账记录（provenance），按既有设计同 `experiments/`、`formulas/`、`scripts/`、`sss_core/`、`tests/` 一样属于"必须引用被禁措辞才能审计它"的登记面；不排除则正文改写完成后闸将永久为红（没人看的闸）。
> 边界与守卫：①正文树 `paper/` 仍在扫描面内（阶段一实测 54 条 violation 未清零 ⇒ 闸未绿，不存在"为绿而扩面"）；②不变量测试 `test_violations_outside_the_manuscript_tree_are_empty` 钉住"paper/ 之外零违规"；③若日后要让审查记录也受禁语约束，须另建"审计引用豁免"机制，不得简单恢复扫描（会造死锁）。
> 关联：`.scratch/sliding-spotlight-scheduling/t50/phase1-receipt.md` §3 末与 §9 暗卷自查 #1。



## 八、票 50 收口（阶段三·B + 阶段四合并波，2026-10-21）

| 项 | 处置 | 留痕 |
|---|---|---|
| 正文三面（main.tex / full.md / sections/*.md）+ 投稿包 | 定位改写完成（阶段三·A/B）+ 阶段四波一致性修复（sec1-3 自 full.md 机械再生、main.tex 富披露吸收进 full.md 17 处、ARS 审稿 4 修 + 三轮自查 1 修）；门禁全绿：红闸 0/1076、L8 数字闸 36 项 0 mismatch、预注册闸 28 项 0 失败、版式闸 0 FAIL（3 advisory 基线既有）、旧 v3 闸报 SUPERSEDED 横幅（预期）；编译两遍 45 页 0 error 0 未定义引用；域套件 papers 664 passed/1 skipped + src 154 passed（rc 均 0） | .scratch/sliding-spotlight-scheduling/t50/phase3-parity.md + phase3-parity-machine.json + phase3-receipt.md + phase4-ars-review.md + phase4-three-round-check.md + phase4-receipt.md |

## 九、票 61：生成端驻留口径参数化（2026-10-24，R61 债兑付）

> **重生成前置登记（append-only）**：`sss_core/scenarios.py` 的 `generate_scenario` / `generate_real_scenario` 自票 61 起带 `duration_caliber` 参数——默认 `"library"` 与改动前**位级一致**（冻结 v3/v5 世界的字节再生保证不变，票 35 dead-branch 守卫钉住）；`"task-law"` 使两处驻留点位（anchor 窗驻留分散度 + 真窗族发射 end-check）按评估端约定消费任务自身订单（`round(rho_req,9)`/`round(l_az_m,6)` 与 manifest 落盘值一致；STR 不传 rho 由票 48 clip 承载；SPT 先经 `spt_task_start_domain` 钳位镜像 evaluator.py:310-314）。
> **任何新世界 manifest 重生成必须显式 `duration_caliber="task-law"` 并在本文件登记**——防「发射窗集与任务律可行集口径分裂」（R61 原风险）的机制是显式登记的选择，不是静默默认。
> 判别测试：`tests/test_generator_task_law_caliber.py`（同订单生成端==evaluator `_dwell` 位精确 + library 对比例 + 双点位生成级红证）。定向审查：`.scratch/sliding-spotlight-scheduling/t61-exec/review.md`。
