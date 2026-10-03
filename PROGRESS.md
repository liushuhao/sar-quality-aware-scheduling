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

### [11:23] 票 15 T0 硬闸 gate-review 判 FAIL → 10 条 punch 全处置（推翻我两条原裁决）

**criteria**：correctness/specification/evidence/regression 全 FAIL，safety PASS。

**两条原裁决被推翻（已改）**：
- **`T_env_max` 目标值**：我写的 12.8548 s 是**旧 sec² 式在 45°** 的值，**违反本票自裁的 SLS ≤26.9° 上限**。正确值 **10.5830 s（argmax = SPT@45°），因子 1.5754×**（非 1.91×）。
- **窗尾垫**：我先前推「需 3.50%」是**错的**——生产闭式切换后 = 物理参考，残差**恒 0**；为 oracle 差异抬垫属**禁止的症状加垫**。裁决**保留 1.00%** + 加域作用域守卫。

**垫裁决的承重证据（实测复核）**：SLS 平面 oracle 相对新生产的 gap 在**绑定区 |ψ|∈[11.9°,26.9°] 全为正（min +0.4112%）⇒ 无泄漏**；符号翻转只在 ±2.8° 的内部低谷（非绑定区）。原 docstring 的「保守方向」在绑定区成立，但「全域保守」不成立——docstring 须改写。

**punch 10 方向被实测推翻**：`aasr.py:204` 现算 `Vs·cosψ/ρ_a,ach` 展开即 `Vs·cos²ψ/ρ_a(0)`，**正是 §3.1 禁用式**（45° 处比注册式窄 29.3%）。**须改为**注册式 `Vs·cosψ/ρ_a(m,0)`（SLS@45 = 10716.99 Hz，与 spec sanity 逐位吻合）。

**其余处置**：ψ 轴取 **136 点**（保密度；naive 37 点/90° 会粗 3.75× 并让最后的 `halving_stability` FAIL）｜`_domain_check` 改**模式感知**（STR/SPT 45°、SLS 26.9°）｜**f_Q 保持零斜视常数**（D05-4 时间不变性保留，`rho_a,ach` 只上报不进 f_Q 表达式）｜5 个未列红名单的破测补入（含 `test_aasr_grid.py:124`，推翻本票「aasr 域变更碰不到」的判断）｜M?NC 锚值**记为期望零变化**（实测 STR 切换在 ±3.356° 只动 2.144e-6 s ≪ 1e-3 容差 ⇒ 0.8931 不动；真实证人是直接断言不是锚值）｜项 13 内部恒等链 `f_Q = (g_T/ρ_a²)·1/ρ_rg²`，比值恒 4.9338（容差 3e-4）。

### [13:05] 票 15 completed — commits `20ff465` + `d0d32f2`

**已验证据**：
- 本域套件 `165 passed, 1 skipped, 1 xfailed in 1101.44s`（基线 159 → **+6 新守卫**；skip/xfail **未净增**，仍是那两条 R12/exit-11 标记）
- 共享库 `145 passed in 207.98s`（**零回归**）
- `scripts/verify_claim_traces.py` → `11/11 claims provenance-verified / no open defects`，**rc=0**（formula-spec 升 v1.3 后仍全绿）
- `scripts/verify_ticket22_adjudications.py` → `0 failure(s) over 43 checks`，**rc=0**（物理改动不影响票 22 裁决，因其只读冻结工件）
- 冻结六族：`git diff --stat -- experiments/results/` **空**，196 文件数不变，`src/sar_sim` 零改动

**落地要点**：
- 生产闭式：SLS = Eq.(22) 校核器链（45° 偏 5.30% 是唯一真物理问题）；STR = tan 精确（45° 仅偏 0.0009%，切换为口径统一）；**SPT 不动**（已是 Eq.(10)-(11) 精确式）
- 七处 ±12° 全切换 + **模式感知域守卫**（STR/SPT 45°、SLS 26.9°）+ ψ 轴 **136 点保密度**（naive 37 点会粗 3.75× 并让最后的 `halving_stability` FAIL）
- `T_env_max` 10.5830 s（argmax SPT@45°），`C3/C4` 归一化因子 1.5754×
- `B_D` 纠正为注册式（原实现是 §3.1 明令禁用的 cos² 口径，45° 处欠保守 **29.3%**）
- 垫维持 1.00%，`window_tail_pad_report` 改为**记录** oracle 缺口 + 按模式断言保守方向（SLS 绑定区 min **+0.4112%** 全正；STR 全域为负故**不宣称保守**，只受垫覆盖）
- `scene_minus_point_delta_s` 改为**派生** `T_scene − T_point`（消除该类漂移，而非重 pin 数字）

**变异红证 2 条（红→绿双向贴证）**：A（SLS 回退平面）4 红 / B（STR 回退平面）2 红，含专设高斜视证人 `test_high_squint_production_matches_physical_reference`。

**破测 5 项全处置**（重 pin 禁放宽）：含 `scene_minus_point_component_identity`（改生产函数为派生）、`SLS/STR==1/A`（恒等式归 oracle，生产侧 pin 新比值 4.934967753）、`T_env_max` 探针移至 11.5 s + **pin 10.5830**、`grid_halving` 抽样改模式感知 + **样本数不足即 raise**、`test_grid_out_of_domain_raises`（13° 对 STR 合法、46° 才 raise）。

**新增 6 个守卫**：`test_oracle_gap_is_discriminating_at_high_squint`（含 **12° 陷阱反向断言**）、`test_high_squint_production_matches_physical_reference`、`test_squint_envelope_guards_fail_loud`、`test_mode_squint_envelope_matches_fixture`、`test_seven_psi_sites_all_track_the_mode_envelope`（行为绑定替代源码 grep）、`test_t_env_max_tracks_the_per_mode_envelope` + `test_fQ_inverse_rho_a_squared_identity`（验收项 13 内部恒等链，隐含量 `1/ρ_rg = 2.0`）。

**一处自查纠错**：验收项 13 我先写成 `f_Q = (g_T/ρ_a²)·1/ρ_rg²`、隐含量 4.9338（实为 `1/A`），实测正解是 `f_Q = (g_T/ρ_a)·(1/ρ_rg)`、隐含量 **2.0**，已改。

### [13:25] 票 16 开工：fork write-back 三步完成（commit `92dfc35` + `d676cce`）

**守卫缺口修复（复制前的前置，两视角共同指出）**：
- `test_fork_self_contained_no_sar_sim_import` 原只查 `metrics/nesz.py` 单文件 ⇒ 新 fork 文件写 `import sar_sim` 无人拦截
- `test_fork_scope_matches_manifest_f01` 用 `hasattr` 绑在单模块对象 ⇒ 符号复制进新文件不可见，**manifest 条款 2 只是文本承诺**
- 两者均扩为全 `sss_core` 树扫描。**反验**：注入探针文件（`from sar_sim.types import ...` + 重定义被排除的 `aggregate_quality`）⇒ 2 守卫变红，含旧守卫看不见的新文件符号；移除后全绿

**F-02 fork 落地**（回写条款固定顺序：登记 → 复制 → 守卫）：
- 裁剪面：`orbit.py` 全量 + `visibility.py` **几何子集** + `target.py` 两 helper + WGS-84 常量链；**排除** `find_visibility_windows`/`visibility_matrix`（返回共享 `ObservationWindow` 且携带第二套窗口语义，违票面「禁私有重实现」）
- `KeplerianElement`/`ECIState` **本地独立定义**（纯 frozen dataclass）——F-01 的排除先例针对带行为的方法型类型，纯数据类不适用
- 守卫 `test_fork_identity_realwindows.py` **14 passed**（与 F-01 合计 22）。**反验**：地球自转角速率扰动 1e−11 ⇒ 2 守卫变红

**两个 squint 是不同物理量（实测坐实，两视角的共同担忧被改写为「缺两个原子」）**：
- 共享向量 squint = 目标处**全沿轨偏航角**（600 s 内 6.542°–19.843°，窗内几乎不动）
- 分叉 `squint_at` = **窗内相对 t_ca 的偏移**（±12° 摆动）
- **零点也不重合**：向量最小点在 dt=−600 s，`squint_at` 零点在 dt=0
⇒ manifest 须登记**两个零点**字段；包络腿只消费 `squint_at`，向量 squint 仅诊断上报

**逐任务几何注入的物理必要性（实测）**：`R0` 随入射角在 20–70° 带内变动 **−22.20% ~ +71.94%** ⇒ piece-b 不是装饰性的。裁决走**最小改动面**：`TaskPlan` 扩展逐任务几何 + `duration_scene_s`/`squint_at` 接受可选 R0 覆盖（None ⇒ `lib.geo`），使旧 M/P 族**逐位不变**（冻结六族零 diff）。

**入射窗实测**：设计几何下 300 s 过境入射角 45.007°→47.393° 平滑变化，20–70° 掩码全程 in_band ⇒ 入射腿可用。

**未验项（明确标记，未当作完成）**：`duration.py:141,145-149,166,168` 的 `geo.R0_m` 直接引用尚未覆盖注入。

（每票完成后追加：`[HH:MM] TICKET 票NN → completed (<hash>) — <计数> / exit code`）
### [13:33] 票 16 中途：逐任务几何注入落地（commit `fd5232e`）

**实现**：`duration_scene_s(..., r0_m=None)` / `squint_at(..., r0_m=None)` / `kim_checker_scene_sls(..., r0_m=None)` + `TaskPlan` 扩展三字段（`r0_m` / `incidence_deg` / `vector_squint_min_t_s`）；`evaluator` 五处消费点全部接通（precompile / `_dwell` / C2 对斜视 / f_Q 的 `r_m`）。

**非侵入性证明（硬证据）**：重算全部 **50 个冻结 matrix 工件的 greedy anchor f1\*，与记录值逐位比对，零 mismatch** ⇒ 旧族走 `None` 分支结果完全不变，`experiments/results/` 零 diff。

**3 个新守卫**：`None` 携带库常数时必须逐位 no-op｜携带真值时**必须**移动驻留（防 stub 通过 None-only 检查，实测跨度 >40%）｜`squint_at` 关系是 `atan(x/r)`，角度比**接近但严格小于** R0 比（实测 1.686 vs 1.7，我第一版断言写成精确相等已被自己的测试抓住）。

**一处自查纠错**：初版守卫断言 `a/b == 1.7` 精确，实测 1.686 ⇒ `atan` 非线性，比值本就不等于自变量比；已改为 `1.0 < a/b < 1.7 且 |a/b−1.7| < 0.05` 的正确关系。

**剩余未做**（票 16 尚有 6 项）：三级联求交器 / 真窗族生成器（`R<密度><需求>`）/ 过载比校准环 / 单过境选择规则 / 同 seed byte-compare / 变异红证。
