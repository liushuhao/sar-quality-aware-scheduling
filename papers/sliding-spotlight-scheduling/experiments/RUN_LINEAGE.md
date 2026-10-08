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
