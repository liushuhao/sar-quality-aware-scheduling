# PROGRESS — paper2 四票施工（22 → 15 → 16 → 17）

任务书：`.scratch/sliding-spotlight-scheduling/_leader-draft.md`

## 目标
四票做完 → 第二篇小论文（滑聚/聚束变时长 SAR 调度）冻结件可签、实验可点火。

## 顺序
1. 票 22（T1，分析设计前置，零源码）— 主比较检验重裁 + promotion 收敛标定
2. 票 15（T0，45° 物理域）— duration.py 生产闭包切 Kim Eq.22 全式 + ρ_a(mode,ψ̄) + AASR ±45°
3. 票 16（T0，真窗族）— 真几何贯通三件套 + 窗求交三级联 + 过载比校准环
4. 票 17（T1，prereg v2 + 主实验）— `--dirs/--generator` 参数化先行，再 v2 冻结，再真窗矩阵

## 最大风险（三条）
- **票 15 的 ±12° 七处硬编码**：漏一处（尤以 `verify.py:159 grid_halving` 最隐蔽，只覆盖 26.7% 域报假 PASS）⇒ 新网格「已验证」是假的。
- **票 15 变异红证夹具**：必须 ψ̄≥26°/45°，12° 档 1% 容差吞掉平面式 0.44% 偏差 ⇒ 永不红 = 仪式空转。
- **票 17 v2 冻结**：须先派无会话历史 subagent 独立审冻结件（不豁免③）；`hv` 无实现须补或注销；冻结六族禁原地重跑（须显式 `--out` 新目录）。

## 任务 0 复核（2026-10-03 实测）
| 项 | 任务书声称 | 实测 | 判 |
|---|---|---|---|
| HEAD | `68a9a76` | `68a9a76` | ✅ |
| `git status --porcelain` | 净 | count=0 | ✅ |
| `git diff paper2-m1-baseline..HEAD -- src/sar_sim` | 空 | 空 | ✅ |
| 共享库 collect | 145 | 145 | ✅ |
| 本域 collect | 159 | 159 | ✅ |
| 解释器 | 3.14.4 | 3.14.4 | ✅ |
| `"hv"` 有 `.py` 实现 | 无 | grep 零命中 | ✅ |
| 0.8931 pin 行号 | `test_verify_gate.py:137` | `:137`（`:134` 是 docstring） | ✅ |
| `grid_halving` 行号 | `verify.py:159` | `:159` | ✅ |
| `shared_lib_tests` 行号 | `verify.py:135` | `:135` | ✅ |

结论：无误，准动代码。

## 施工日志

### [10:05] 票 22 开工（T1，分析设计前置，零源码改动）

证据面已读清（票面 + `duration.py` / `modes.py` / `geometry.py` / `aasr.py` / `predicates.py` / `quality.py` / `evaluator.py` / `anchor.py` / `nsga2.py` / `scenarios.py` / `verify.py` / `formula-spec.md` §3.1 §4.1 §4.2 §4.3）。

票 15 预勘（写给施工用，非裁决）：
- ±12° 硬编码实测 6 处 `sss_core/*.py`：`aasr.py:111` / `aasr.py:341`（票面说 `:336` `_domain_check` 的 def 行，断言体在 `:341`）/ `duration.py:277` / `predicates.py:98` / `scenarios.py:125` / `verify.py:168`。**票面列 7 处，其中 `aasr.py:247` 实为 `GridAxes` dataclass 字段定义（无字面量），须核**。
- `duration_scene_s` 生产闭包 7 调用点对上：anchor×3（`anchor.py:113,114,222`）/ evaluator×2（`:146,:209`）/ predicates×1（`:99`）/ scenarios×1（`:178`）。`quality.py` 走 `duration_point_s`（1 处，票面未列，物理闭包切换时需一并核）。

### [10:39] 票 22 completed — A3 + A4 双裁决

**已验证据**：
- 本域套件 `157 passed, 1 skipped, 1 xfailed in 307.74s`（= 基线 159 collect，skip/xfail 零净增）
- 共享库 `145 passed in 186.40s`
- `scripts/verify_claim_traces.py` → `RESULT: 11/11 claims provenance-verified / no open defects`，**rc=0**
- A3 对照实验 → **exit 0**，工件 `.scratch/sliding-spotlight-scheduling/ticket22-noseed/noseed_control.json`
- 冻结六族：`git status --porcelain papers/` 空、`git diff --stat -- papers/` 空（**零改动**）
- 零 `sss_core` 源码改动（`git diff --stat` 仅 `.scratch/` 与 `PROGRESS.md`）

**A3 裁决**（两视角 subagent + 主线程实测择优）：估计量从 `max_f1*` 换到 **`dq_all` = 全前沿最高 f_Q − 锚 f_Q**，分层（3 非退化族池化 n=30 主检验，逐族 Holm 次要），零保留不做 zero_method，禁覆盖轴显著性检验。主线程实测四个候选：`dq` 0/49 非零、`dom` 0/49、`mq` 0/49 全部结构性打平；`dq_all` 20/49 非零、sd=0.940。功效：逐族 p=0.0134/0.0015/0.0398 全显著，池化 p=2.4e-05，置换 p<1e-5。
**A3 对照实测**：50 单元 → 29 出前沿 / **21 空前沿**；29 中 **26 低于锚**、中位 −0.1630；`seed_worth` 中位 +0.1527。**已知混杂如实登记**：两臂初始化策略不同（非单变量消融），本地复刻方案被自等价守卫拦停（exit 5，29/50 空前沿）。

**A4 裁决**（两视角 subagent + 主线程实测）：两维判词（结构性 × 预算依赖）四格固定措辞。结构界实测 9 族全 <6.0 dB（M1NC/M3NC 0.037，M2WH 5.379，M2WF 5.464，M4WH 5.499，P6 5.439，P7 5.456，P8 5.501，P9 5.303）；平台维 71.03 dB ⇒ 平台活/族内死。**knife-edge 披露**：P8WH 距阈值仅 0.499 dB，且共用 `aasr_direct` 模型继承 D06-6 局限 ⇒ 标 model-level 禁标 physics-level。**量纲纠错**：票 17 验收项 13 写「f_Q 极差 vs 6.0 dB」是错的（f_Q 是 m⁻²），正解用 AASR dB。
**反验**：A4 阈值 1.0/2.0⇒UNCONVERGED、10.0/20.0⇒CONVERGED（真翻转）；A3 估计量换 `dq` ⇒ sd=0.0 / p=nan 功效塌陷。

**一处实测纠错（已改进票 body）**：先前口算的 M2WH「顶两档 median Δ=0.0078」是错比较基数；按注册顶两档（160/240 vs 320/480）实为 **1.892048 dB** ⇒ 判 UNCONVERGED（与「9 族全 DEAD×UNCONVERGED」一致）。

### [10:55] 票 22 completed — commit `b08526e`

补充单元 22b：`scripts/verify_ticket22_adjudications.py`（300 行）把 A3+A4 裁决变成可复跑门禁——**42 checks / 0 failure / rc=0**。票 17 冻结 v2 前直接消费。
- **只读证明**：跑前跑后 `experiments/results` 196 文件不变、抽查工件 md5 `6efbf819…` 不变、`git status --porcelain papers/` 仅新增脚本本身
- **反验两向**：claim 值改 `1.892048`→错值 `0.0078` ⇒ `FAIL a4_m2wh_median_delta` / **rc=1** / `VERDICT: adjudication has DRIFTED`；还原 ⇒ rc=0
- **采样稳健性**：新增 `a4_R_*_sampling_stable` 4 项（P族 5 点 vs 21 点扫描一致）——knife-edge 判决（P8WH 5.5012 dB）非采样假象
- **容差稳健性**：tie count 49 在 tol 1e-15…1e-6 全域稳定，唯一非零差是那个 +0.1
- **一处诚实修正**：收紧 plateau 阈值时判决不变（M2WH 已超阈 ⇒ 收紧 no-op），脚本**不声称双向翻转**，改为打印三档对照并注明「loosening is the live edge」

### [11:05] 票 22b gate-review 修复轮 — commit `b2a636c`

22b 首版被独立 gate-review 判 **FAIL**（correctness/specification/evidence）。8 条 punch list 全处理，实测证据：
- **防空绿普查**：断言 4 个目录的确切单元数（`all([])`/`median([])` 在空目录上静默通过）。**它当场抓出我自己的一个错**：convergence 是 45 单元（M2WH 5×3 + P7/P8/P9WH 各 5×2），我原写 15。普查扰动反验 ⇒ rc=2 拦停。
- **口径显式化**：per-family 扫描口径（矩阵族取 base seed、探针族取 5 seed 最大——无统一规则能复现 9 个值）、平台极差口径（k 固定在 `lib.geo.k`；自由扫 k 得 78.47 dB 是**另一个问题**不是本问题的修正）、median-delta 口径（差中位数 1.892 vs 逐 seed delta 中位数 0.037，差 ~50×）
- **构造性零标注**：`dq`/`dom`/`mq` 是构造性为零，断言它们为 0 不证明数据性质——已注明只有 `dq_all>0` 是判别性检查
- **`-B` 运行**：`__pycache__` 也纳入只读声明
- **最终 43 checks / 0 failure / rc=0**

### [11:05] 票 15 开工前勘察 + 设计裁决（票面 +90 行，零源码改动）

派 2 视角 fresh subagent + 主线程实测，裁三个设计缺口：
- **GAP1**：STR 换 tan 精确式（45° 仅偏 0.0009%，为口径一致）；**SLS 生产切 Eq.(22) 校核器**（45° 偏 **5.30%**，本票唯一真物理问题）；**SPT 不动**（已是 Eq.(10)-(11) 精确式，45° 仅偏 0.089%）
- **GAP2 kill test（关键实测）**：扫 11700 个冻结任务 ⇒ **372 个（3.2%）路由档在自身边沿 ψ 处不达标**（例：M2WF `rho_req=0.5029` 路由到 SLS 0.5 m，11.06° 处实际 0.5095 m）。⇒ 欠服务是**现存事实**不是未来风险；但最大边沿 ψ 仅 11.059°，扩域会按 secψ 放大 ⇒ 裁决「保持零斜视路由 + 上报达成分辨率 + limitation 披露」，斜视感知路由另开票
- **GAP3**：`T_env_max` 12°→45° 会使归一化因子变 **1.91×**（6.7178→12.8548 s），必须移；垫不缩小（只缩可行集不漏解），新增可重算断言

**预期红名单重裁（实测证伪 3/5 条）**：
- `test_windows_precompile.py:191` 只断言窗口**形状**不比较数值，最大 ψ=11.06° 非高斜视 ⇒ ❌
- `test_aasr_grid.py` 可行集 pin 在 **ψ=0** ⇒ ❌
- `test_quality_fq.py:70` 循环**只到 ±12°**（违反本票自己的 ≥26° 规矩）+ 票面引 `duration.py:104-105` 实为 SLS 分支（SPT 在 `:106-107`）⇒ ❌
- `test_anchor.py:207`/`test_verify_gate.py:137` 是重算式但 M1NC 是 ±3.36° 窄窗，偏差可能落在 `abs=1e-3` 内 ⇒ ⚠️ 须实测

**变异夹具的硬约束（新发现）**：STR/SPT 全域偏差 <0.1%，**回退平面式不会红** ⇒ 变异夹具**必须用 SLS + ≥26°**（45° 偏 5.30% ≫ 1% 垫）。票面原定「驻留回退平面式版必红」若只用 STR/SPT 夹具将恒假绿。
**变异红证 B（ρ_a 回退常数版）目前不可证伪**——`rho_a,ach(mode,ψ)` 函数尚不存在，须随本票落地。

**七处 ±12° 假 PASS 排序（实测）**：① `verify.py:168` `grid_halving` 只采 26.7% 新域 ⇒ 确认静默假 PASS ② `duration.py:277` 垫按 12° 标定而真实 45° 误差 5.30% ⇒ 欠覆盖 5 倍 ③ `aasr.py:111`+`:247` 若只放宽守卫不扩轴，`_locate` 把 45° **静默钳到 12° 单元**（实测返回 `i_psi=35`）④ `predicates.py:98` 保守但错 ⑤⑥ raise 响亮 ⑦ 受③约束。

**失败顺序**：序 1–3（纯数学 + ρ_a + 垫/T_env_max，约 10 s）已能抓全部物理问题；网格工作（~28 s + `grid_halving` 3–10 min）放最后。

（每票完成后追加：`[HH:MM] TICKET 票NN → completed (<hash>) — <计数> / exit code`）