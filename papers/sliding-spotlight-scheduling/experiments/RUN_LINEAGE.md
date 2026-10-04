# RUN LINEAGE — papers/sliding-spotlight-scheduling/

> 手工维护的**唯一**运行谱系登记处（形态决策：2026-10-02，否决生成器脚本 —— 节点数在 10 量级，
> 生成器属过度工程）。目的：把散落在 commit message、prereg amendment、results 目录里的
> 「假设 → 冻结 → 结果 → 裁决」串成一棵树，直接服务论文的消融表与被否证路线段落。
>
> **维护规则（硬）**：`experiments/results/` 下每新增一个子目录，必须在本表登记一行；
> 节点路径必须真实存在。由 `tests/test_run_lineage_completeness.py` 守卫，违反即红。

## 一、节点登记

| 节点 | 父节点 | 假设 / 目的（跑之前登记的） | 冻结依据 | 结果目录 | 产物 | 裁决 | 证据 |
|---|---|---|---|---|---|---|---|
| `L0` | —（根） | 驱动链可用性冒烟；M1NC 退化锚点变体 | `analysis_prereg.json` meta 声明：冻结前唯一产物即此文件 | `experiments/results/pilot/` | 1 | 保留 —— anchor baseline，f1\* 归一化的分母 | `analysis_prereg.json` meta.frozen_before_evidence |
| `L1` | `L0` | 五变体（M1NC / M2WH / M3NC / M2WF / M4WH）在主指标（`f1_star_max`、`f_q_front`、HV、晋级率）上可区分 | `analysis_prereg.json` v1.0.0，`frozen_before_evidence`（逐单元 `pilot-result/1.1` + git_head） | `experiments/results/matrix/` | 50 artifacts + `_driver.log` + `_progress.json` | 跑完 50/50 exit 0，产物齐；**晋级判据全变体未达**（6.0 dB 阈值） | `6aa365a`（冻结，先于任何 W/H 全矩阵结果）、`1b67398`（run） |
| `L1a` | `L1` | 场景 manifest 生成物的确定性与 seed 规则 | `scenario_manifest_template.json`（seed_convention D08-9：seed = variant_index·100 + seed_index） | `experiments/results/scenarios/` | 50 | 确定性成立 —— 收敛驱动重生成的 manifest 与冻结矩阵 manifest **byte-identical** | `9ef11bd` |
| `L1b` | `L1` | 独立 verifier 证据报告（非求解器自述） | — | `experiments/results/verify/` | 3 | `report_pilot` + audit20260930 报告 + `a6_adjudication_20260929.md` | `3f188d3` 起登记；**票 23 后实测回填（2026-10-04）**：12 步门禁（含首次实跑的 `snapshot_rebuild`，对 v2 syn 工件 bit-exact PASS）+ `scatter_precheck` REPORT（A6 注册升级，record 非失败）+ 0 FAIL ⇒ **12 PASS + 1 REPORT + 0 FAIL**；pilot 域=v2-run syn 工件（v1 冻结件对 v2 代码为 front 重构面，等价判据=anchor Δ=0，见 confound_control） |
| `L2` | `L1` | **假设：front 上 distinct f_Q 的塌缩是密度驱动的物理塌缩** | density probe prereg amendment + predicates 扩 P6–P9（`predicates_calibration.json`） | `experiments/results/probe_density/` | 20 artifacts + `manifests/` 25 | **当时读作「否证」——后被 `L3` 重裁**。本层实测：frontier cliff 出现在 N=40→60 之间；晋级在**所有**密度上 dead（max 3.891 dB < 6.0，commit `0231900`）。注意「否证」的当时对象是**密度驱动**这一归因，不是 cliff 现象本身；cliff 的性质由 `L3` 裁决 | `8721f68`（prereg amendment）、`0231900`（results） |
| `L3` | `L2` | **假设：cliff 是物理塌缩，而非搜索预算不足** | `amendment_20260930_matrix_readjudication`（criteria before data；1× / 4× / 16× / 64× 预算阶梯） | `experiments/results/probe_convergence/` | 45 artifacts | **NOT-YET-CONVERGED** —— median distinct-f_Q 随预算 2 → 4 → 17 → 48，无平台期；PHYSICAL 叙述被否证。用户裁决 **path A**：改叙事/重设计实验，停止继续升级算力 | `43911b0`、`9ef11bd`、`338984e`（audit2 redline：无按密度平台期即不得声称 PHYSICAL） |

## 二、并行节点（非 results 产物）

| 节点 | 目的 | 冻结依据 | 裁决 | 证据 |
|---|---|---|---|---|
| `L4` | 公式注册：`rho_a(mode, psi)` per-mode 闭式、B_D 第三方消费口径 | `formulas/formula-spec.md` v1.1（ticket 18，阻塞门） | 生产式 `rho_a(m,psi) = rho_a(m,0)/cos(psi)`，域 [0,45]°；B_D 第三方消费修正（原 `Vs·cos/rho_ach` 重复计入 cos，@45° 带宽错 29%） | `1bd49d8`、`cddcdf9` |

## 三、被否证 / 已停止的路线（negative results）

> 这三条是论文 Limitations 与 ablation 讨论的直接素材。审稿人问「为什么不继续」时，答案在这里。

| # | 路线 | 状态 | 否决证据 |
|---|---|---|---|
| N1 | trivialization（front 上 f_Q 塌缩）作为**物理**现象 | **否证** | `L3`：N=40/60/80/100 全部在预算下复活；无平台期。`6355d50` 早先已判 cliff 是 SEARCH ARTIFACT, not physics |
| N2 | 晋级判据（AASR spread ≥ 6.0 dB） | **在已测范围不可达；终局口径待裁** | `L1`/`L2`：全密度、全预算下 max 3.891 dB < 6.0 dB。**但「不可达」是否等于「结构性死」尚未裁决**——票 22（A4）正在做收敛标定 + 结构性死双维判词，票 17 消费其结论。**本行不得被读作「已判该判据须重设计」** |
| N3 | `g_T` 单加权 amendment（audit2 期间草拟） | **撤回** | gate-review 实测：仅 `g_T` ON 时 `f_Q` 呈 `1/rho_a^2` 标度 → `g_T` 是平方反比律的载体，D05-5 双加权披露成立。`338984e` |
| N4 | PHYSICAL-vs-SEARCH-ARTIFACT 机器可读判据骨架 | **被 tickets 19/20 否证，已 append 绑定修正** | `338984e`：原判据在**每个**密度上都被推翻，但只活在 spec 散文中，机器可读 artifact 仍带一个已被否证的判据 → append `amendment_20260930_audit2_r1_redline`，绑定「无按密度平台期即不得声称 PHYSICAL collapse」 |

## 四、写作映射

| 论文位置 | 取用节点 |
|---|---|
| 主结果表（5 变体 × 10 seed） | `L1` + `L1b`（独立 verifier 报告） |
| 消融 / 敏感性 | `L1a`（确定性）、`L2`（密度扫描） |
| Limitations / 被否证路线 | N1、N2、N4 |
| 方法约束口径 | `L4`（`rho_a` 闭式、B_D 第三消费方） |

## 五、未登记项（故意留白）

- `experiments/results/probe_density/manifests/` —— 是 `L2` 的子目录，不单独成节点。
- ticket 19/20 的原始否决记录、audit2 的 scratch 层裁决 —— 按仓库策略 `.scratch` 已 gitignore，
  正文只保留 `338984e` 的 append 结果，不在此重复。
