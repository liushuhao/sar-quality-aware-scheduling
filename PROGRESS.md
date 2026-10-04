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

### [13:40] 票 16 三件套完成（commit `7313984`）

**第三件（级联求交器）落地**：`windows.py` 新增 `intersect_intervals`（闭区间并集求交，保留零长度点，空腿返回空而非静默忽略）+ `mask_intervals`（布尔掩码采样成极大run）。**结构上**做到「不复现任一腿的谓词」——每腿由其属主计算，求交器只做交。

**端到端实测**（设计几何，SLS）：入射腿 240 s ∩ 包络腿 101 s ∩ 端查腿 **93.45 s ⇒ 真窗 93.45 s**，窗心驻留 6.4348 s、入射 44.981°，三腿逐级收窄。

**两处实测发现的坑（均由自己的守卫抓住）**：
- `mask_intervals` 的 run 端点会落在掩码边界**外侧**：先测到 SLS 包络外溢 0.04° 触发域守卫 raise；再测到 1 ULP 外溢（`5.000000000000001` 对 `<= 5.0` 掩码）⇒ 端点满足性守卫直接变红。
- ⇒ inset 改为「一步长 + 8 ULP」，并新增 `test_mask_run_endpoints_satisfy_their_own_mask` 钉死该性质。

**测试**：本文件 16 → **18**。

### [13:45] 票 16 真窗族生成器落地（commit `9bc5947`）

**`generate_real_scenario`**：R1C/R2F/R3H/R4H 四族，每任务窗由真实轨道几何经三件套级联生成，**窗宽是物理量**（设计轨道实测 201.06 s）。平台轨道为**必填参数**（`ValueError` 拒绝默认），因本族的要点就是几何是注册输入而非生成器自造。

**实测（seed 100, density 20, demand C）**：抽 20 → 服务 10，`no_window` 剔除 10（真实几何拒收一半，300 s 方框不可能产生这种处置）；窗宽 mean/min/max 全为 201.063262 s；逐任务带 `r0_m=775274.2` / `incidence_deg=44.987` / `vector_squint_min_t_s=7.085`（与 `t_ca_s=0.0` **分列**，实测二者确非同一点）。

**确定性实测**：同 seed 两次生成 **byte-identical**，异 seed 不同；台账守恒 10+10=20。

**变异红证（票面要求 ≥1）第一轮 = 假绿，已修**：回退 evaluator 的逐任务注入后 **22 个 duration 守卫全绿**——因为它们直接测 `duration_scene_s`，不经消费方。⇒ 新增端到端守卫 `test_real_scenario_injection_reaches_the_evaluator`：用真实 manifest 断言 evaluator **自己的** `_dwell` 与库常数 dwell 不同；回退后变红且诊断为两值相同（`1.3027299992939185 != 1.3027299992939185`），恰证「几何停止被读」。还原后 37 passed。

**一处自查修正**：注入在设计轨道附近只差 **0.0097%**（R0 775274 vs 775426），单看数值近乎无差——这正是「字段登记了但没消费」能长期潜伏的原因，故守卫必须比较**两条路径**而非比较差值大小。

### [14:05] 票 16 全套测试确认

本域套件 **`194 passed, 1 skipped, 1 xfailed in 1089.75s`**（票 15 收官时 165 ⇒ **+29**；**零失败**，skip/xfail 与基线同为 1+1 未净增）。冻结六族 196 文件零 diff，`src/sar_sim` 零改动。

### [14:39] 票 16 completed（9/9）+ 票 17 验收项 3 完成

**票 16 收尾三项**（`e9b1e48` `2b0d8f4`）：
- **场景模板预注册** `realwindow_scenario_template.json` 落盘 + **与代码常量绑定的漂移守卫**（7 字段全对，漂移即红）
- **过载比校准环**（验收项 6）：`scripts/calibrate_overload.py`，rc=0。**入射带是真旋钮**（需求档不是——C/H 各档比值完全相同），实测 **0.85 / 0.50 / 0.40 / 0.25 共 4 档 ≥ 注册下限 3**，全部损失来自 `no_window`。只写 `--out`，冻结六族 196 文件零 diff
- **高 cross-track 变异夹具**：R2F 细需求族路由到 SLS/SPT，实测 R0 跨度 **671–1026 km（1.53×）**、最强任务 **+32.30%** 偏离库常数；守卫自检要求跨度 >20% 才接受自己为证人。**回退注入 ⇒ 2 守卫变红**，还原后 19 passed
- **前篇对照注记**落 manifest `scenario.predecessor_comparison`（含 overload ratio 0.5）

**票 17 验收项 3（参数化）**（`2b15b79`）：`MatrixDirs` 把四条路径全部字段化并穿透 `load_progress`/`ensure_manifests`/单元循环；默认值**逐位复现**原行为（冻结可复现），真窗跑**必须**显式传目录。`--generator realwindow` 无 `--platform` 时**拒绝**（轨道是注册输入，驱动无权自造）。

**全套确认**：`198 passed, 1 skipped, 1 xfailed in 1266.12s`（票 15 收官 165 ⇒ **+33**，零失败，skip/xfail 未净增）。冻结六族 196 文件零 diff，`src/sar_sim` 零改动。

### [14:57] 票 17：prereg v2 冻结（第一轮独立审查判 **REJECT** → 修后重冻，commit `65f8ee5`）

**第一轮独立审查（无会话历史 subagent）判 REJECT，六条发现**：
1. 冻结文件在审查期间被改动（当时未跟踪）⇒ 现已提交，字节稳定
2. `known_power` **过时且自相矛盾**：写 n=30/sd 1.05854，而分层规则实际给出 n=20/sd 0.88042
3. 冻结与所消费的票 22 裁决**暗中矛盾**
4. 机检 `verify_ticket22_adjudications.py` 仍按 n=30 校验（它校验的是**票 22 裁决**，不是冻结）
5. 分层规则**欠定**（R 族无「全 STR」对应物；逐 seed 中位数可翻转分层）
6. **最大缺陷：没有任何可证伪预测**——正是预注册要防的失败模式

**六条处置（实测复核）**：
- 分层规则按字面执行：M2WF 中位 distinct-fq **1.5 < 2** ⇒ 结构零层；**主分层 = M2WH + M4WH，n=20，sd=0.88042**（实测 mean 0.81072，单侧 p=2.93e-4）
- `known_power` 重算：n=20 时 MDE(80%) = **0.579×sd = 0.5099**；票 22 的 n=30/1.05854 明标为**已废止注记**
- 新增 `stratum_rule_outcome_on_v1_evidence` 明写「规则优先于票 22 注记」，消除暗中矛盾
- 分层确定性：只在**注册的基准 seed + 基准预算**上评估一次；R 族的「全 STR」子句换成其**可测内容**（每单元 distinct-fq 恒为 1，即 sd 恰为 0 的条件）
- **新增可证伪预测 P1–P4**（各含量、阈值、**明确证伪条件**）：P1 前沿丰富度（**未收敛 = 未检验，不是证伪**；证伪亦**禁**塌缩/相变声明）｜P2 质量余量｜P3 promotion｜P4 容量（**推导未落地前不预测**，拒 retrofit）
- **拒接 A4**：改票 22 机检去迁就冻结等于篡改历史记录；冻结的分层由它自己的校验负责

**一处自查抓到的缺陷**：把 sha256 写进被哈希文件里是自指，永不可能相等 ⇒ 已改为记录**受审内容**的哈希并注明「完整性以 git 为准」，文件已提交故字节不可变。

**两轮 JSON 语法错误均由我自己发现并修**（尾逗号），第一轮的审查者是在文件仍可解析时读的。

**独立审查第二轮已派出**（文件已入 git，审查期间不会再变）。

### [15:49] 票 17：第二轮独立审查（ACCEPT WITH REQUIRED AMENDMENTS）→ 五条修订 + 红线机检

**第二轮审查**（文件已入 git 故审查期间不再变动）判 ACCEPT WITH REQUIRED AMENDMENTS，其最有价值的三条：
- **本轮实质缺陷**：冻结只登记了 P1–P3（三条皆自票面抬升），而**论文真正的两条新载荷——容量律与交换率——完全没有可证伪预测**（P4 当时登记为 WITHHELD）。⇒ P4 改为**关于闭合度「模式」而非「水平」**的预测并给出证伪条件；**串行界推导与 v1 实测值正式登记**（0.3435 / 0.0372 / 0.0303 / 0.0186 / 0.0142）；交换率按票面定位保持**观察项**（无证伪条件、须标探索性）。
- **退化族子句改用 f_Q 极差**而非 distinct_fq：实测 M1NC/M3NC 极差 **1.110e-16**、非退化族 2.4–3.6；distinct_fq 在 1e-6 处舍入会误判「小但非零」的族。
- **`consumed_gates` 收窄**：票 22 门禁校验的是**历史裁决**，不覆盖本冻结的 n=20 分层——原措辞「every number this freeze quotes」属**过度声明**，已改。
- 审查者另称 `dq_all` 应为 34/49 而非 20/49；**主线程独立复算否定了这一条**（49 可用单元中非零恰为 **20**，sd 0.93996），20/30 是票 22 注记的巧合，未采纳。

**红线五条机检**（`scripts/check_red_lines.py`，rc=0，双向变异验证）：
- **建检查时抓出真实文档缺口**：formula-spec 只就**分辨率**披露过 45° 外推，**驻留闭式**的 45° 段从未披露——而票 15 正是把生产闭式推到 45°。§8.9 第 8 条补记（含 SLS 26.9° 是 `a_res=0` 物理边界而非外推，故以域守卫 fail-loud）
- **两个假阴性被实测抓出并修正**（非调参掩盖）：① 字符窗口过宽 ⇒ 260 字符外一个含 "forbidden" 的 JSON 键**洗白**了真注入的相变声明 ⇒ 改为**逐行**判定（禁令必与被禁词同行）；② 检查器扫到**自身的模式表**。
- 默认域为论文与注册工件，**不含 `.scratch/`**（那里正是讨论禁令的地方，扫它会报出每份「为禁止而引用」的文档）；`--include-scratch` 保留可审计。

**冻结自检门禁** `scripts/verify_prereg_v2.py` **27 checks rc=0**，并经变异反验：掏空分层规则 ⇒ rc=1（首版曾漏检，因它只算结果不读规则）。

### [16:32] 票 17 prereg v2 冻结获**独立审查 ACCEPT**（三轮闭环），两处门禁漏洞已修

第三轮（确认轮）判 **ACCEPT**：冻结可据以点火真窗主实验。裁定要点：
- **`dq_all` 计数争议终局**：审查者第二轮称的 **34/49 有误**——它用 `>0` 无 epsilon 判定，把 **14 个 dq_all ∈ (0, 1e−12] 的浮点残渣**计成了质量增益。第三轮复核**站在我方**：**20/49**，sd 0.93996。
- 我方自测补充了成因：严格 `>0` 得 34、`>1e-9`/`>1e-12` 均得 **20**；那 14 个单元的 dq_all 约 1e-16，即前沿无新 f_Q 值，计入非零率会**虚增非零率却不进均值**。

**审查者在我自己的两个门禁上各找到一处真漏洞，均已修 + 变异反验**：
- `verify_prereg_v2.py`：分层阈值用**子串**匹配 ⇒ `"2" in rule` 对 `"20"` 为真，改阈值的规则仍全绿 ⇒ 改为**解析数值比对**（28 checks），审查者的原样变异 `distinct_fq < 20` ⇒ **rc=1 并指名数值**
- `check_red_lines.py`：禁令标记**同行任意位置**即可洗白声明 ⇒ 改为**位置化 + 子句作用域**；验证三向：诚实禁令 0 违规、审查者的**洗白句**（"forbidden to be called a phase transition; yet the front collapse is real"）**rc=1**、无标记的裸声明 **rc=1**

**一处过期自述已修**：`consumed_gates.scope_caveat` 仍称红线检查「prose-only」——脚本落地后该句变假，已改。

**剩余自陈局限（不掩盖）**：`check_red_lines.py` 校验的是 **45° 包络常量已注册**，不校验披露**文字**正确——后者是文档评审义务，非机检可及。已登记入冻结 `independent_review_3.remaining_caveat`。

### [16:57] 锚几何修复后的全套回归 + **主实验点火**

**全套回归**：本域 `198 passed, 1 skipped, 1 xfailed in 1073.14s`（与修复前同数，skip/xfail 未净增）⇒ 锚改用逐任务几何**未引入任何回归**。冻结 50 anchor 逐位一致（上条已证）。

**主实验点火**（`.scratch/sliding-spotlight-scheduling/v2-run/`，冻结六族零 diff）：
- 预算阶梯按**冻结注册**执行：40/60 → 80/120 → 160/240（**160/240 为上限**，320/480 额度已耗尽，禁消费）
- 家族 R1C/R2F/R3H/R4H × 10 seed × 3 档 = **120 单元**
- 命令形如：
  `PYTHONHASHSEED=0 python -B papers/sliding-spotlight-scheduling/scripts/run_matrix.py --generator realwindow --platform <spec.json> --variants 1,2,3,4 --pop 40 --gen 60 --scenarios-dir .scratch/.../v2-run/scenarios --matrix-dir .scratch/.../v2-run/p40g60`
- 估算求解耗时：40/60 档约 2 min、80/120 约 8 min、160/240 约 30 min（按 v1 实测 2.85 s/单元线性外推）

**点火前状态**：prereg v2 已获三轮独立审查 **ACCEPT**；四门禁 rc=0；冒烟 exit 0 且 cv 精确 0。

### [17:20] 主实验 40/60 档：抓到**第三个**口径分裂（设计问题，非实现 bug）

**跑况**：首跑 exit 0 但 **40 单元中 11 个 exit 1**（driver 按设计只对 exit-10/全失败报警，exit-1 被计入 totals 却未构成失败——**这一条本身是门禁缺口，已登记**）。

**根因链（三层，逐层实测）**：
1. **锚/评估器几何分裂**（已修，`130a9b2`）：锚用库 R0、评估器用逐任务 r0_m ⇒ 10 个锚起点中 8 个落在自己可行集外，CV=0.0646 触发 fail-loud 断言，`run_matrix` 静默零产出守卫 exit 4 拦停。
2. **生成器级联用库 R0**（已修）：包络腿与端查腿用 `squint_at(dt, t_ca, lib.geo)`（无 r0_m）⇒ 发出边沿达 **48.74°** 的窗（超 45° 包络），评估器按逐任务 R0 重推时判 **7 个 SPT 任务不可调度** ⇒ CV=2.0。加 `R_ENVELOPE_GUARD_FRACTION=0.01` 内缩包络后又遇 **45.016° vs 45.0°** 的边界越界（掩码内缩一步长不足以覆盖端查括号）。
3. **C3/C4 归一化参考与被测量不同口径（未解，已派审）**：`T_env_max = 10.5830 s` 是**库几何**下的包络最大驻留；真窗任务逐任务 R0 可高出基线 **+13.5%**（实测 R4H_seed405 任务 141：r0=880245 vs 775426，驻留 **10.8512 s > 10.5830 s**）⇒ C3/C4 归一值 **1.0253 > 1.0** ⇒ `c3_ok`/`c4_ok` 双双 False ⇒ CV=2.0。
   - 已确认**不是** C2（0 违例）、**不是** 冲突（0 违例）、**不是** 不可调度（0 个）。
   - 已确认窗尾垫**无同类问题**：垫是**乘性分数**，对 R0 缩放不变；受影响的只有**加性参考量** `T_env_max`。

**教训（与前两次同型，值得记）**：逐任务几何注入后，**凡以库几何为基准的加性参考量都会与被测量脱钩**。已修两处（锚、生成器级联），第三处（C3/C4 归一化）需政策裁决而非打补丁——已派 1 视角 subagent 审「逐任务参考 / 全包络上界 / 判为真实违约并在生成期剔除」三选项。

### [18:01] 主实验 **40/60 档完成：40/40 单元 exit 0，CV 全部精确 0**

**第五处（最后一处）口径分裂**：`promotion_spread_db`（`nsga2.py:135`）用库 R0 算斜视，且域外样本让 `aasr_direct` **raise** 直接杀死单元。修法两条：① 用 `plan.r0_m`；② promotion 是**未强制**读数（D12-3 语义），域外样本记 **+inf dB**（无限差 AASR）而非崩溃——保持 spread 有意义且单元存活。
**附带**：生成期 AASR 门必须从**点**改为**窗**（最差点在高斜视端，SLS 在窗中点之前就可能出域）；域外样本 ⇒ 记 `aasr` 剔除，**不崩**。

**结果（40/60 档，10 seed × 4 族）**：

| 族 | anchor f1* 中位 | max f1* 中位 | front 中位 | **distinct_fq 中位** | promotion |
|---|---|---|---|---|---|
| R1C | 0.8789 | 1.0000 | 40.0 | **15.0** | no_promotion |
| R2F | 0.4576 | 0.4576 | 7.0 | **7.0** | no_promotion |
| R3H | 0.3108 | 0.3108 | 2.0 | **2.0** | no_promotion |
| R4H | 0.2186 | 0.2186 | 2.0 | **2.0** | no_promotion |

- **CV 全部精确 0**；无 inf promotion；冻结六族 196 文件零 diff；`src/sar_sim` 零改动。
- ⚠️ **R3H/R4H 的 distinct_fq 中位 2.0 < 注册阈值 3**，但**单档不构成任何判决**——P1 只在 **CONVERGED** 阶梯上说话；front 中位 2.0（远小于 pop 40）说明**未饱和**，与 R1C 的 front=40（饱和签名）形态不同，正是收敛标定要区分的两种情形。80/120 与 160/240 两档已在跑。

**门禁缺口（已记，未修）**：`run_matrix` 只对 exit-10 与「零成功」报警，**exit-1 不算失败**——本次三处真 bug 全部表现为 exit-1，首跑 40 单元中 11 个 exit-1 仍返回 exit 0。须在票 17 收尾时补该报警面。

### [19:26] 票 17 收尾项推进（commits `40a1420` `d632a50` `7dd6c7a` `b88b90c`）

**exit-1 报警面（门禁缺口，已修）**：`run_matrix` 原把 exit-1（`run_pilot` 的 setup-error）计入 totals 却不算失败 ⇒ **首跑 40 单元中 11 个 exit-1 仍返回 exit 0**。本次主实验的**五处真缺陷全部**表现为 exit-1，连续四轮「成功」跑其实丢了三分之一工作量。现 exit-1 ⇒ `EXIT_UNIT_SETUP_ERROR=7` 并打印「setup error 是崩溃不是结果」。

**结果表 + per-mode f_Q 分解**（`build_v2_results.py`）：分解需先修一处——前沿记录只有 `{cv,f1_star,f_q,n_selected,starts}`，**无 mode 字段**，直接读会把全部成员归进一个 `?` 桶；改为经 `starts` 的任务下标回查 manifest 模式。修后模式混合与需求档路由吻合：R1C（粗）纯 STR、R2F（细）跨 SLS/SPT/SLS+SPT、混合档三模式齐全。

**去支配解（两版都错，第三版才对）**：
- v1「需**严格**支配」⇒ 冗余 **0/2883**，**漏报**（ULP 重复非严格被支配），掩盖 81% 缺陷；
- v2「任意成员 `>=` 即算」⇒ R1C 非支配 **0**，**错报**（重复成员互相排除，而跨度真实的前沿不可能非支配集为空）；
- **v3 两趟**（先剔严格被支配、再在存活集内按 (f1\*,f_Q) 去重）⇒ R1C 160→**16**（冗余 89.7%）、R2F 57→36、R3H 12→12、R4H 6→5。
⇒ **distinct_f_Q 去支配前后完全不变**（16.5/35.5/12.0/5.0）⇒ 重复成员未携带新质量取值，**P1 判词不受影响**；但**任何引用 front_size 的地方必须用去支配值**（R1C 报 160 而真实 16）。

**caliber 标记**：`experiments/caliber_registry.json` 登记冻结合成族为 **caliber v1**（票 15 换闭式前产出，与 v2 **不可比**，须随数携带）；两族还差**几何口径**（逐任务 R0），故未标数的引用一律视为不可采信。

**收敛报告强制项**：现由 `build_v2_results.py` 与结果表**同批落盘**（缺一不落），逐族写明「UNCONVERGED 族不支持任何物理声明，**含阈值恰好达标的丰富度声明**」，并记「>160/240 额度已耗尽，加预算属新决策」。

**验收项 19（保守 AASR 谓词）裁决**：实测**窗边采样不足**——窗内 11 点最差 −21.346 dB vs 仅窗边 −25.315 dB，**48/48 个任务都漏掉窗内最差点、低估约 4 dB**（票面记的 2.92 dB 是合成族值）。对 −13 dB 门仍有 **8.35 dB 余量**故数据未脏，但门不保守。生成期已按**窗内最坏**判据接线；v1 的「grid cell 上界 + 1 dB 裕度」谓词**本轮显式不接线**（接线会引入域外钳位返回错物理的第二重口径风险，票 15 已清过同类坑）——**记此备查，非遗漏**。

**verify 门禁扩本域套件**：`domain_tests` 步已注册，期望数 pin 为 **实测 `--collect-only` 的 200**（198 passed + 1 skipped + 1 xfailed）——我先写 198 被 collect-only 抓出。⚠️ 本域套件含多次 ±45° 网格构建，约 18 min，该步在本轮实测仍在跑。

### [19:30] promotion 结构维实测：**结论在真几何下翻转**

| 族 | R_fam (dB) | 结构维 | 读数收敛 | **两维判词** |
|---|---|---|---|---|
| R1C | 4.0032 | DEAD | CONVERGED | **DEAD × CONVERGED**（非触发，预算无关） |
| R2F | **6.8213** | **ALIVE** | UNCONVERGED | **ALIVE × UNCONVERGED ⇒ 冻结明文 NO CLAIM** |
| R3H | **6.8216** | **ALIVE** | UNCONVERGED | 同上 |
| R4H | **6.8213** | **ALIVE** | UNCONVERGED | 同上 |

- 对照：票 22 实测九个**合成**族 R 全 < 6.0（最大 P8WH 5.501，距阈 0.499 dB）。**真窗族三个细/混合档族越过阈值**（6.82，余量 0.82 dB）⇒ **合成族的「结构性非触发」不可外推到真窗族**。
- 本轮 promotion **未触发**（三档 max 全 < 6.0：R1C 3.899 / R2F 3.573 / R3H 0.157 / R4H 0.287）；但对三个 ALIVE 族，这**只是本轮预算下的观测**，**不是**「结构性死」的结论——冻结对 ALIVE × UNCONVERGED 的规定是 **NO CLAIM**。

### [19:41] 票 17 剩余四项推进

**P4 容量闭合度（真窗族实测）+ 一处自我措辞更正**：
- **更正**：我此前把冻结的「串行界 = 合法**下界**」读成「containment（上界）」。实测确认**下界方向正确**——串行一次排一个，并行可重叠成像区间 ⇒ 并行服务**更多** ⇒ `closure>1` 是**预期**。冻结原文对，我的措辞错。
- 实测 closure 随过载**单调上升** 3.706 → 4.664 → 12.238 → 15.732（**极差 4.25×**）⇒ **P4 主体（非平坦模式）未被证伪**。
- **但 P4 预设机制未观测到**：C2 需求（7.76–13.20 s）**恒远小于**窗宽中位（200–219 s）⇒ 转移约束在任何档都**不绑定**，「C2 开始绑定」的 regime 转变**未发生**。如实记为**部分符合，非完整验证**；实际驱动更可能是密度上升致可行集变窄 + 优先级分布变陡。

**验收项 1 合成族对照（消混杂）— 40/60 档已出**：同族同预算，v1 冻结件 vs v2 代码 ⇒ **anchor f1\* 五族 Δ 精确为 0**，distinct_f_q 仅 ±0.5 ⇒ **真窗族差异归因于几何而非闭式**。80/120 与 160/240 两档在跑。

**verify 门禁补两步**（`v2_artifacts` / `caliber_registry`，均 PASS）：前者要求结果表**与**收敛报告**同时存在且族集合一致**（缺报告 = 不可采信态，非部分成功）；后者要求两个 caliber 齐备且**互相声明不可比**。

**门禁套件实测**：本域 `198 passed, 1 skipped, 1 xfailed`（= 收集 200，与新 pin 一致）；共享库 145 passed。

### [20:50] 票 17 确认轮无阻塞 → **四票全部 completed**

**第四轮独立确认审查**（rule 10 退出标准）：**无阻塞发现**。两条残留已当场修掉（`fcfe0ee`）：

1. **合成族对照的「前提」曾无记录**：anchor Δ=0.0 只证明「重跑复现了冻结锚值」，不证明「重跑的是合成 manifest」。该前提**可从工件验证**（每个 pilot 记录所读 manifest，schema 区分 `1.0` / `2.0-realwindow`，family_code 区分 M/R）⇒ 现**逐工件核对并落盘**，**50/50 全 VERIFIED**（审查者指出的「未记录前提」已变为**已验证前提**）。
2. **promotion 的 `+inf` 会读成「fires」**：域外样本记 +inf ⇒ `spread = inf ≥ 6.0` ⇒ decision 变 `promote`，与意图**相反**（无限差的未强制 AASR 不构成加第三目标维的理由）。现将域外候选**排除出 spread 并计入 decision 串**；`verify.py` 的独立 replay **同镜像**（否则两者会静默分歧）。

**票 17 Status → completed（19/19 验收）**。

**四票终态**：

| 票 | Status | 关键产出 |
|---|---|---|
| 22 | completed 7/7 | A3 主比较重裁 + A4 两维标定 + 对照实验 + 43 checks 机检 |
| 15 | completed 13/13 | Eq.(22) 生产闭式 + ±45° 逐模式域 + 165 passed + 变异红证 2 |
| 16 | completed 9/9 | fork write-back 三件 + 三件套级联 + 真窗族 + 校准环 + 198 passed |
| 17 | completed 19/19 | prereg v2（四轮审查 ACCEPT）+ 主实验 270 单元全 exit 0 + 四工件 + 门禁六步 |

**主实验总账**：真窗 120 单元（4 族 × 10 seed × 3 预算）+ 合成对照 150 单元（5 族 × 10 seed × 3 预算）= **270 单元全部 exit 0、CV 全部精确 0**。

**核心结果（受冻结约束）**：R1C **CONVERGED、P1 成立**（dfq 16.5 ≥ 3）；R2F/R3H/R4H **UNCONVERGED ⇒ P1 NOT-YET-TESTED**（阈值虽达但阶梯仍在涨，冻结禁作物理声明）。promotion 结构维**在真几何下翻转**（R2F/R3H/R4H R_fam 6.82 ≥ 6.0 ⇒ ALIVE × UNCONVERGED ⇒ NO CLAIM）。合成对照证明**闭式变更对锚值零影响**（五族三档 Δ 精确 0.0）⇒ 真窗差异归因几何；且**合成族 dfq 本身也随预算陡增** ⇒ 丰富度增长**主要来自预算而非几何**。

**全程未使用「前沿塌缩」「相变」任何字样**（红线机检 rc=0）。

### [21:11] **收官回归（全绿）**

| 面 | 结果 | rc |
|---|---|---|
| 本域 `papers/sliding-spotlight-scheduling/tests/` | **198 passed, 1 skipped, 1 xfailed**（收集 200） | 0 |
| 共享库 `src/tests/` | **145 passed**（= 基线 N0，零回归） | 0 |
| `verify_prereg_v2.py`（冻结自检 28 checks） | PASS | 0 |
| `check_red_lines.py`（红线五条） | PASS | 0 |
| `verify_ticket22_adjudications.py`（43 checks） | PASS | 0 |
| `verify_claim_traces.py` | 11/11 claims | 0 |

skip/xfailed 仍是基线那两条（1 条件跳过 + 1 xfailed = R12 exit-11 缺陷标记），**未净增、未删除**。

**冻结边界**：`experiments/results/` 六族 **196 文件零 diff**；`git diff paper2-m1-baseline..HEAD -- src/sar_sim` **空**；工作树**净**，本会话 **47 commits**。

## 收工归零复盘（2026-10-03 21:2x）

### 故障模式提炼（tech-zeroing 五条）

**主故障模式（五处同根因，逐处实测定位并修复）**：
**「注入逐任务几何后，凡以库几何为基准的量都会与被测量脱钩」**。五处：
1. `anchor.py` 预编译/放置用库 R0，评估器用逐任务 r0_m ⇒ 8/10 锚起点落在自己可行集外，CV=0.0646 崩单元
2. `scenarios.py` 级联的包络腿与端查腿用库 R0 ⇒ 发出边沿 48.74°（超 45° 包络）的窗
3. `predicates.py` `T_env_max` 是库几何量而驻留是逐任务量 ⇒ 38 任务假违规（最差 1.1721）
4. `nsga2.py` promotion 读数用库 R0 且域外 raise ⇒ 杀死单元
5. `evaluator.py` 五处消费点未透传 `plan.r0_m`

**同族但独立的假阴性/假绿（各有实例，均由自己的守卫抓住）**：
- **子串匹配当数值比对**：`"2" in rule` 对 `"20"` 为真 ⇒ 分层阈值改 20 全绿（审查指出）
- **逐行共现当语境判定**：禁令标记同行即洗白真声明（三轮修：字符窗口 → 同行共现 → 位置化子句作用域）
- **判据方向错**：去支配解「需严格支配」漏报 2883 中的 81%；改成「任意成员 >=」又错报（重复互相排除）
- **点测当窗测**：AASR 门只测窗中点，SLS 在窗端已出域 ⇒ 48/48 任务低估约 4 dB
- **未记录前提当因果归因**：合成族 anchor Δ=0.0 只证「复现」不证「跑的是合成 manifest」⇒ 现逐工件核对（50/50 VERIFIED）

### 举一反三新发现（本轮扫出，**未修，已记账**）

`boundary_rate`（`maneuver.py:95`）在**逐任务路径上**（C2 转移项，`evaluator.py:278-279` 调用）却读**库常数** `lib.geo.R0_m` ⇒ **第六处口径分裂**，杠杆项 `Vs·cosψ/R0` 随逐任务 R0 变动 **±42%**（实测 R0×0.778 → 1.229e-2 vs 基线 9.559e-3；R0×1.719 → 5.561e-3）。
**不修的理由**：修它会使刚完成的 270 单元主实验全部失效，须重跑全阶梯（约 50 min 求解）。**故显式记账为延后债**，下一轮若动 C2 语义必须连带处理。
同类待查（低危，因 STR 立即返回 0、SLS/SPT 才读）：`windows.py:384` `footprint_ok` 的 SPT 足印界读库 R0。

## 票 23：逐任务 r0_m 口径收口（2026-10-03/04，用户拍板：修 R14/R15 + 根因排查指令）

### 根因排查（「修根不修面」指令的直接产物）

同根因模式「凡以库几何为基准的量在逐任务路径上脱钩」全仓 AST/grep sweep，命中**三处**生产路径（台账只记了两处）：
1. `boundary_rate`（maneuver.py:95）——R14，C2 杠杆项 ±42%
2. `footprint_ok`（windows.py:384）——R15，SPT 足印界
3. **`aasr_direct`（aasr.py:200）——第八处，台账漏记**：无 r0 形参，K_a/K_c/k_at0 全库 R0，直连真窗 AASR 门与 promotion spread（R_fam 判词来源）

分类排除（合法库口径，守卫白名单钉死）：duration 点目标口径（g_T 比值内 R0 相消）、planar oracle、kim_eq23 内部恒等、anchor fallback-setup 标定检查、quality.q_rad (R_ref/R)³ 参考归一化、AASRGrid._build_dense（k_c/k_a 精确相消+平台级注册口径）。gate-review 一轮 FAIL→修（B1：verify.py promotion_replay 漏镜像+finite 排除分支死代码；B2：:312 错分类+白名单缺项）→确认解除。

### 实施（两 commit）

- `dd3aa92`：三函数 `r0_m=None`（None=标定/合成口径）+ evaluator C2 对 / anchor fits+repair 六处（经 boundary_rate_of）/ nsga2 promotion 透传；8 新测试；变异红证 **6/6**（M2 判别器=end-to-end evaluate() + 二分 straddle——omega 单项 delta ~1e-3 s，STR 两口径全零故测试任务用 SLS）；静态守卫测试（AST 白名单外 `geo.R0_m` 直读即红）。
- `d4921e9`：scenarios.py 真窗 footprint 门移 pass 循环（该 pass r0_task 判定；归因规则注册：footprint 移除 ⟺ 全部可评估 pass 失败，不可评估不计）+ 真窗 AASR 门透传；verify.py 四镜像点（promotion_replay 补 `ValueError→inf` catch 对齐 nsga2；scatter/_per_mode_means 透传 manifest r0）；DOMAIN_N0 200→208；`recompute_r_fam.py` 落成已提交脚本（Y5）。

### 重跑与实测（「修=作废 270 单元」假设被证伪）

- 双面回归：本域 **206 passed + 1 skipped + 1 xfailed**（收集 208，skip/xf 净增 0）+ 共享库 **145 passed**，均 rc=0。
- 最小单元（rule 11）：R1C 负控 10/10 **数值零变化**（全 STR 两口径 omega 全零+AASR r0 不变式）；R2F 正控真变化（f1 0.327→0.367 等）；manifests **40/40 byte-identical**（RNG 序未动，footprint 门结构性 no-op——Y2 预测命中：R 族 r0_task∈[817,1024] km 全高于库 768 km）。
- 合成不变式：M1NC 单元对 v2-run syn 基线 **0 diff**；M 五族 anchor Δ=0.0（confound control 再生成）。
- 全真窗阶梯：**120/120 exit 0**（p40g60 补跑对齐 HEAD d4921e9；三档 head 统一）；逐单元 diff 分类与预登记预期逐项吻合——变化集中在 R2F/R3H/R4H 的 front/promotion（footprint 类=0，非空即 bug 的断言未触发）。
- **R_fam 复算（已提交脚本口径）**：R1C **DEAD**（base 4.0018 / max-over-seeds **4.0032=票 17 注册值精确复现**）；R2F/R3H/R4H **ALIVE**（6.8296/6.9109/6.9104，票 17 散文值差 ≤0.09 dB，判据 6.0 不变）。两维判词不变：R1C DEAD×CONVERGED；三细/混族 ALIVE×UNCONVERGED ⇒ **NO CLAIM**。
- **promotion 读数**：全档 <6.0 未触发；R2F 顶档 max 3.573→**5.224 dB**（距阈 0.78 dB，仍 ALIVE×UNCONVERGED ⇒ NO CLAIM）。dfq 随预算陡增保持（R2F 10.5→26→37）。
- 门禁：verify_prereg_v2 28 checks / verify_ticket22 43 checks / claim_traces 11/11 --strict / red_lines 62 files rc=0 / run_verify（见下）；`experiments/results/` 六族冻结件零 diff。
- 旧阶梯存档 `v2-run-preT23/`；R_fam 复算件 `v2-run/r_fam_recompute_t23.json`。

## 2026-10-04 P0（审查发现，未修复）：真窗四族全量目标物理不可见

**发现路径**：用户审查 geo-map.html（本会话生成的目标分布×星下点轨迹图）发现簇压轨迹（SAR 不能看星下点）→ 量簇-轨迹距离 2722~11977 km 与"全任务入射角带内"矛盾 → 解剖 R1C task0：星下点距目标 10,499 km 而内核报入射角 45.0° → 全量仰角实测。

**根因**：`sss_core/realwindows.py:_compute_off_nadir_angle` 天底角在地平线外**折返**（可见极限 65.4°，背面目标折回 16-40°）；`_off_nadir_to_incidence` 正弦定理换算 + `asin` 只回 [0°,90°] 支——背面目标真入射角（ψ+η，实测例 134.7°）被静默折成 45° 假带内值；`scenarios.py:394 incidence_ok` 无地平线守卫。**共享库 `src/sar_sim/generator/visibility.py:48` 同型同源**（Paper 1 合成窗未触发）。

**实测**：真窗四族全部 460 个"幸存"任务在服务窗内 5 点采样仰角全 <0（0 可见）；"50% 幸存率"= 8 簇中 4 簇落在折返假入射角环带的整数巧合。全链（manifest→三腿窗→求解→v2_results→收敛判决→票 23 复算）内部自洽但物理语义为零；合成族 M 不受影响。

**修复方向（用户已提，未实施）**：入射换算改向量夹角定义（acos(目标天顶单位矢·目标→卫星单位矢)，返回 [0,180] 无分支丢失；可见性 ⟺ 入射角 <90°）+ 变异红证 + 460 任务仰角等价检查。**连带**：共享库 visibility.py 同步裁决、票 16/23 重开、真窗场景重设计（修复后两圈 ±120s 弧下可能 0 簇可见，需重议圈数/历元/簇心摆位）。台账 **R17**。
- **二次排查精化（同日）**：守卫正典位置 = 共享库 `_check_geometric_constraints`（elevation<min_elevation→False，visibility.py:183）。P1（手写几何但逐时刻过检查，min_elevation=5.0 注册）、Ch4（向量化 `elevs>=min_elev(5.0)`）均干净；唯一绕过者 = paper2 fork（刻意不带 find_visibility_windows 时把仰角腿一起丢）。裸函数 `_off_nadir_to_incidence` 结构上无法自带守卫（折返角与近侧角在 (off_nadir,h) 上不可区分），守卫必须在调用点；结构性修法 = `satellite_to_target_vector` 改向量夹角返回真入射角 [0,180]。其余 asin/acos 位点（geometry.py:45 / duration.py:301 / quality.py:282）逐一排除。
- **物理核对分级（用户已批，R17 开票验收范围）**：T1 真窗几何链全换算（定义域+越界行为+第三方交叉验证，绑修复票）；T2 自推导无外部锚量补域声明+物理对照；T3 有文献锚族抽查。T1/T2 派 fresh subagent 核对。


## 2026-10-04 同类物理违反全仓审计（故障模式分类学 × 三路 fresh subagent × 主线程复核）

**缺陷类**（P0 抽象）：F1 逆三角丢支 / F2 非单调折返 / F3 静默 clip 吞不可行值 / F4 缺物理守卫 / F5 错根·象限 / F6 域外静默 / F7 物理不变量破坏。扫描面 = 共享库 src/sar_sim + fork sss_core 全文件 + Ch5 实验层；三路 subagent 独立审，主线程对全部新确认项做代码读数+数值探针复核。

**新确认违反 3**（台账 R18/R19）：
1. **fork `scenarios.py:469` 三腿级联缺入射交集**——`window = intersect(env_iv, end_iv)`，`inc_iv`(:403) 只用于选锚点 tca；发射窗不受 30–60° 入射带约束，windows.py:256 注册的三腿级联（incidence ∩ envelope ∩ end-check）与实现不符。机制级确认；冻结产物全伪影下真 pass 量级不可测，修 P0 后转正。
2. **Ch5 `ch4_run_pilot.py:192` compute_sat_position 缺 −ω_e·t 地球自转项**——:299 注释写出正确公式但代码未实现，半轨星下点漂移 ~11.9°@500km；pilot 全部窗口几何在"非自转地球"帧内自洽（可实现的另一个宇宙，非本地球）。
3. **Ch5 `ch4_run_pilot.py:244` 正弦定理+asin 折返（P0 同型）**——当前场景参数端到端 0 触发（72 窗全合法、最低真仰角 +43°），但 containment 是涌现性质而非设计守卫：γ=90°（垂直经线目标）折叠 θ=47.95° vs INC_MAX=47 裕度仅 0.95°；对抗扫描（lat≤60° 全经度）8610 个背面带内样本；单/双平面 config、INC_MAX≥48、目标盒贴近相邻平面中点任一即击穿。

**共享库潜伏群**（台账 R20；**Paper1 已投数值在折叠轴上安全**——主链被 visibility.py:183 仰角守卫先行保护，探针三 instrument 预设全拒背面目标）：`nesz.py:109` 折返+clip 静默吞 η>64.4°→90°；**活边 = `verification/constraints.py:182` C1 对窗间隙时刻假 PASS**（解码时刻 t∈[t_earliest,t_latest] 含间隙、C1 无窗口包含检查：elev=−40° 目标真入射 130.0° 折成 49.98° 判 PASS；Paper1 最终解窗口包含故已投结果不受影响，so_f1.py:598 GA-P 事后校验路径为残留风险）；so_f1.py:420/568 无 cache 回退路径 f2 均匀 +10.9%（标准 runner 全部先 precompute_geometry，不触发）；nesz.py:47 elevation_to_off_nadir 域混用（真入射存进 phi_min/max，偏 9.42°，零活消费者）。

**可复现性类（非物理，台账 R21）**：fork realwindows.py:294 + 共享库 visibility.py:124 用 naive datetime 的 `.timestamp()` 喂 ECEF 旋转 → 按机器本地时区解释 → 地球相位 120.33°（UTC+8）机器依赖；"byte-identical from seed" 仅同时区机器成立。

**复核为真 / 判良性**：① Ch5 gen:434 `elevs >= min_elev(5.0)` 守卫先行声明独立复核**成立**（106 窗×3 时刻真实轨道重算：min elev 28.1°、θ∈[18.31,46.62] 全带内、0 折叠受害）；② fork 侧 windows 不变量（对抗构造全过）、机动闭合解（d_omega 负不可达、接缝欠预测封顶 4.8ms）、duration 根选择（顺序依赖但当前域恒选中物理根）、椭球/球混用（入射 +0.161°/仰角 −0.585°，亚度量级）、geometry.py:64 atan≡atan2（r0>0 恒成立）均良性；③ **P0 更强证据**：冻结轨道+epoch 全圈 5s 步扫描——8 簇在两个生成盒内真可见且带内样本数 = 0（5/8 簇整圈不可见），R-family served 任务 100% 折叠伪影，比 R17 的"460/460 仰角<0"更进一步。

**待用户裁决**：R18/R19/R20/R21 修复排期与 R17 合并方式（推荐 R18+R21 并入 R17 修复票同批改，R19/R20 各自开票——Ch5 未投稿可慢修但 C1 假 PASS 活边优先）。


**复核轮（同日，用户令"再确认"+“核对论文一是否受影响”）**：
- **三项新违反全部确认，零修正**：R18 代码读数复验（inc_iv 仅 :410-412 选锚点；窗口交集 :469 只含 env∩end）；R19a 代码读数复验（compute_sat_position 旋转矩阵无 ω_e 项、:299 注释含正确公式）+ 主线程封数探针（缺自转 11.86°/半轨@500km）；R19b 同型确认；R20 C1 假 PASS 升级为**主线程直调真实 verify_c1 复现**（折返 φ=40° → 0 违规 PASS；换算 45.46° 带内 vs 真值 134.54° 远带外）；R21 封数（naive−UTC = −28800s → 相移 239.67°）。三路报告交叉一致性无矛盾；死 API 声明复核成立（incidence_in_band/closest_approach_states/iter_states 零生产调用者）。
- **Paper1（single-sat-quality，已投稿）报告数字不受影响**，证据链六条：①数据生成侧可见窗由共享库生成，仰角守卫（visibility.py:183 elevation≥min_elev 先行于入射带）挡住一切背面输入（探针：三 instrument 预设全拒）；②质量评分链 θ=90°−elev 无反三角、窗内 [0°,90°] 精确域；③全部 driver 先 precompute_geometry（scripts/ grep 实证）→ so_f1 无 cache 回退（f2 +10.9%）不触发；④报告 frontier 构成 = pymoo res.X（仅 G≤0 可行解）且 G=0 ⟺ 严格窗内（窗成员 gap 罚进 G，penalty 1e5）→ 报告成员全部窗内，窗内 geom_cache 换算精确（可见域误差 ≤2.3e-13°）→ f2/f3 无折返污染；⑤论文正文 :495 明示「C1 enforced during visibility-window generation」——事后验证器的假 PASS 路径不背书任何论文数字；⑥GeomCache 折返污染诊断列（θ/q）Paper1 零消费。**残留**：res.X is None（最终种群零可行）全种群回退路径与 GA-P best 事后校验（so_f1.py:598）理论上可让越窗成员带折返增益混入，但需罚项压制失效的病态运行；原始逐解 pkl 本地已清，无法事后逐解复核——如审稿人质疑可重跑复验（风险方向=高估 f2/f3，利我方向，须诚实披露）。

## 2026-10-04 晚 真窗场景重设计（用户提问触发的实测 + spec 修正案 v0.6）

**触发**：用户拍板启动 P0 修复，并问「目标如何分布比较好」——密集域 ≥1000 km、单圈为主、多圈择优保通用性。本节记录实测证据与据此定案的设计；**结论改写了上一节的归因**。

**探针**（`.scratch/sliding-spotlight-scheduling/_probe_*.py`，7 个，全部按修复后向量夹角定义自建几何，不读 asin 折返世界的任何值）。过程中三个探针 bug 自查修正：`V_SAT` 单位（m/s 当 km/s 用）、pass 分箱（按中点桶聚类 → 改为按窗口时间 gap 聚类）、以及**扫描窗口只覆盖一个轨道周期**（95.9 min）而非完整地轨周期——最后一个曾导致 6/8 簇被误判不可达，修正后为 6/8 可达。

**发现 A — 纬上限 45°，两簇恒死**：i=45° ⇒ 目标纬度上限 45°。(56,22) elev_max 18.09°/inc_min 71.91°、(62,−70) elev_max 7.43°/inc_min 82.57°，全地轨周期 0 带内窗口。其余 6 簇 3–6 趟/周期。⇒ 密集域集中是**物理必需**非设计偏好。

**发现 B — 第二独立缺陷（台账 R22）**：生成器取 `epoch + {0,600}·pass_i` 当「两趟过境」，600 s = 375.3° 真近点角（周期 5755 s）= 任意相位点非过境点。实测当前 offset 可服务簇 **0/8**，真实过境枚举 **6/8**。⇒ **R17 单独修完真窗族仍归零**。

**发现 C — 推翻 R17 既有预判**：R17 台账原记「修复后指标单调不升（纯假阳性删除、零假阴性）」——被 B 推翻。实际是**先归零、过境修好后按新缺陷回升**。R17 已标 REPLACED 指向 R22。

**发现 D — 单趟容量硬上限**：槽位 = dwell + C2（inc45°）STR 8.70 s / SLS 20.35 s / SPT 17.75 s；v_sat 7.578 km/s；窗宽实测 80–240 s。单趟容量：STR 9/13/24（80/120/210 s），SLS·SPT 3-4/5-6/10-11。密度阶梯 ⇒ R1C N=20 需 174 s（**站边界**）、R2F 需 4.1 趟、R3H 需 12.4 趟、R4H 需 20.7 趟。

**发现 E — 区域尺度**：20°N/0° 域心最稳（4 趟/周期、窗宽 200–220 s；30°N 波动 0–190 s）。1000 km 边长 5×5 网格 25/25 可服务、入射角离散 28.7°；300 km 仅 9.1° 异质性不足；2000 km = 264 s 沿迹时间 > 最长窗 210 s，单趟装不下。

**用户拍板（四项）**：① 密度阶梯缩到 20/50/100/200（落在 1/3/5/9 趟（=ceil(N/24)；gate-review 复算纠正，首版 1/3/7/14 算术不可能），矩阵规模约原 40%，**不需追加预算**——BLOCKED.md 备注 1 预算耗尽约束保持）；② R17 + 过境枚举**同批修**（分开则中间态必然归零、易被误读为修复失败）；③ 多圈支持改 `TaskPlan` 为**每窗口一个 t_ca**（T0 schema 收口；`squint_at(t,t_ca)` 假设单次最近接近点在多圈下已不成立）；④ 共享库 `visibility.py` 本轮**不动**，R20 C1 活边另开票。

**落盘**：`spec-amendment-v06.md`（AD-1..AD-8 架构决策、可逆性矩阵、MUST/WANT、钢人代炼含翻转条件、10 类缺口、票映射）。R18（三腿缺交）+ R21（时区）并入同批。票映射：24 = 几何+时区（T0）、25 = 过境+schema+场景（T0）、26 = R20 活边（T1）、27 = R19 Ch5（T1）。**修正案 DRAFT，待两路 fresh subagent 独立审查**（物理第一性原理 / 实现可行性，已派出）。工作树净（`.scratch` 全 gitignore）。

**未动的既有约束**：BLOCKED.md 备注 2「真窗三族禁 alive/dead 声明」在重跑前保持；备注 1 预算耗尽约束因缩档而不触发；冻结六族零 diff 仍是 MUST-3 硬门。

### gate-review（票 24/25 implement 前定向二审）：四维全 FAIL → 已修票

派 fresh subagent 独立审 24/25 两张 T0 票（criteria: correctness/specification/evidence/regression/safety），**四维全 FAIL**。主线程逐条复算关键项后确认成立并修票：

- **CRITICAL ×3（safety + regression）**：改共享库的 `_off_nadir_to_incidence` 会打断**三篇论文的场景生成器**——`single-sat-quality/experiments/generate_all_scenarios.py:28,344-345`、`single-sat-quality/scripts/generate_s5_scenarios.py:26,146-147`、`constellation-scheduling/experiments/ch4_generate_scenarios.py:49-50,321,430,484,497`，均按 `(off_nadir, altitude)` **标量签名**调用，而向量夹角定义无法保留该签名（折返角与近侧角在 `(η,h)` 上不可区分）。**上一轮「共享库同步修」的拍板被此推翻** ⇒ 用户二次拍板**共享库只增不改**，**goal-card「共享库 `src/` 零修改」红线恢复原状（未解除）**。CRITICAL 未消解而是被承接：改 fork 身份守卫为双验（共享库七元组仍逐位一致 + fork 新定义走自建物理基准），FORK_MANIFEST.md:61 登记同步修订、与守卫同 commit。
- **MAJOR：密度阶梯算术错误（主线程自查复算确认）**——`20/50/100/200 → 1/3/7/14 趟` 在单趟容量 24 下**不可能**：N=100→7 需 cap∈(14.29,16.67]、N=200→14 需 cap∈(14.29,15.38]、N=20→1 需 cap≥20，交集为空；且与自述「N=500 需 20.7 趟」自相矛盾。正确值 **ceil(N/24) = 1/3/5/9**。spec + 票 25 + 台账 R22 + 本节四处已同步。
- **MAJOR：`TaskPlan.t_ca_s` 读者漏列**——首版只列四处 verify 镜像，漏 `anchor.py`（6 处 :121,142,149,160,179,180 + 构造 :262）与 `nsga2.py:144`；这两处若沿用标量将**静默用错零点**（比崩溃更坏）。另 `verify_ticket22_adjudications.py` 的 `t_ca_s` 实为 **:139**（票面误引 :133）。
- **MAJOR：MUST-1「仰角 > 0」无判别力**——elevation 代码路径未被 AD-1 触及，改前改后都过。替换为「**入射角 < 90° 的任务集合非空**」（直测新定义语义）+ 新增「锐角支与旧 asin 路径差异 < 1e-9°」的正面等价断言。
- **MAJOR：MUST-7 预闸四步无效**——`rebuild_snapshot.py:20-33` 只读缓存 `_progress.json` + `.tex`，**不重新生成场景**，无法见证共享库回归。改为 Paper1 生成器**实跑一个最小单元**新旧对比，预闸降为额外证据并注明覆盖范围。
- **MAJOR：合成族 no-op 判据空洞**——逐点钉死四条：① `evaluator.py:158` 的 `t0,t1` 必须直取 manifest 值禁反算；② `evaluator.py:138-139` 单窗空列表必须落 `None` 不得翻成可调度；③ `t_ca_at` 在单窗上返回存储原值不重算；④ `decode_tau` 展平并集按原序重建。并新增守卫钉死 evaluator 输出对六族冻结件。
- **MINOR**：`visibility.py` 的 `.timestamp()` 实为 `:124-125`。

**票面形态变更**：票 24 从「共享库同步修」改为「fork 内新路径 + 共享库只增不改 + fork 身份守卫修订」，红线解除留痕已改写为「未解除」。

### gate-review 确认轮（票 24/25）：5 CLOSED / 1 PARTIALLY + 5 新 MAJOR → 已修票

- **旧发现**：6 项中 5 项 CLOSED（共享库零字节、死 API 归属已补、t_ca 读者补全、MUST-1 判别力、MUST-7 预闸、no-op 四点）；1 项 PARTIALLY（密度阶梯算术已对，但**与日程跨度硬矛盾**）。
- **MAJOR-1（最重，主线程复算确认）**：**(20,0) 只有 1.0 趟/24h**——我 spec 与票里写的「4 趟/日程」是把 **48 h 窗口数字当成 24 h**。按容量 24（窗宽 210 s）算，N=200 需 9 趟 ⇒ 跨度 4.5 天。进一步实测发现**窗宽与趟数反相关、无单一最优**：`(20,0)` 1.0 趟/24h / 窗宽 210 s / 容量 24；`(30,100)` 2.0 趟/24h / 窗宽 80–140 s / 容量 9–16；`(30,0)`/`(34,−118)` 1.5 趟/24h。⇒ **用户拍板「缩短跨度 + 降阶梯」**：阶梯 `20/50/100`、**日程跨度 3 天**（新 AD-9，跨度作为预注册量；N=100 需 5 趟，实测趟间隔 510 min ≈ 8.5 h ⇒ 3 天约 8–9 趟，余量须实测不得凭线性外推）。N=150/200 出局。
- **MAJOR-2**：FORK_MANIFEST 修订范围欠估——删 fork 两个 helper 会同时失效 `:50`（复制符号列）、`:53`（逐位一致要求）、`:61`（守卫表行）与 `tests/test_fork_identity_nesz.py:163`（许可符号集），**四处须同 commit**。
- **MAJOR-3**：守卫①不可实施（首版写「共享库对三个生成器逐位一致」——共享库对共享库恒真，零判别力；真保证是 `FORK_MANIFEST.md:21` 已有的 `src/sar_sim` 零 diff 断言，**复用并实跑留档**即可）。
- **MAJOR-4**：偏离面比首版写的更广——**R21 改 fork 的 ECEF 旋转会使 `s[0]`/`s[2]`/`s[3]`/`s[6]` 全部发散**，不只是 incidence/elevation。现存 `test_fork_identity_realwindows.py:145-152` 对 `s[0]` 断言 `array_equal`、对 `s[3]/s[6]` 断言 `==` ⇒ **R21 落地后必然红**，故 R21 与 AD-1 必须同 commit，守卫须逐项声明可比/不可比。
- **MAJOR-5**：锐角等价断言「与旧 asin 路径逐位同值」不可证伪（旧路径同票删除后无参照源）⇒ 判据写实为「与**共享库保留的** `_off_nadir_to_incidence(off_nadir,h)` 之差 < 1e-9°」（共享库那版本票不删，可 import 作参照）。
- **MAJOR-6**：冻结 prereg 模板 `realwindow_scenario_template.json:13` 登记 `"<20|100|300|500>"` 须按 append-only 加 `amendment_<date>_<slug>` 字段（禁原地改）；且 **`verify_prereg_v2.py` 对模板与阶梯零 grep 命中** ⇒ 该漂移当前无人看守，须补守卫。
- **既存 bug（非本轮引入，确认轮发现）**：`sss_core/scenarios.py:110` 的 `R4H=500` 与 `scripts/recompute_r_fam.py:49` 的 `R4H=400` **已经分叉**；R4H 出局后两处都删并留痕（`verify_prereg_v2` 不查此表，故此前未被发现）。
- **MINOR**：`t_ca_at` 须用**闭区间** `lo<=t<=hi`（`windows.py:90` 闭区间约定 + `decode_tau` 在 τ→1 返回 `hi`），写成半开区间会在 τ=1 取错窗；跨窗重叠实测不发生（趟间隔 8.5 h ≫ 单趟 210 s）但须作断言钉死。

**主线程自查补漏**：票 24 改写时丢了三个死 API 的删除（`incidence_in_band`/`closest_approach_states`/`iter_states`，`realwindows.py:323/341/362`，grep 复验零调用者），已补进票 25 并确认 `__all__` 同步；同时核实 fork 范围守卫 `test_fork_exposes_exactly_the_registered_f02_symbols` 是**单向断言**（只查登记符号存在），故删 fork 内部两个 helper 不会让它红——方案自洽。

### gate-review 第三轮：verdict BLOCKED（3 项阻塞）→ 已修 → 第四轮放行确认

三项阻塞，主线程逐条独立复算后**全部成立**（含我自己一轮二次错误）：

- **BLOCK-1 趟数标签自相矛盾**：主线程二次错误。原始「4 趟/48h」实为「2 趟/24h」；
  我中间误标「1.0 趟/24h」（把 2 次/48h 当成每天 1 次）。**第三轮裁定 2.0 为正确值**，
  主线程独立复算确证：24h 与 72h 两种跨度 × merge 阈值 {300s,600s} 四种组合
  **全部给出 2.00 趟/24h**。⇒ 3 天 = 6 趟、N=100 需 5 趟、**余量 1 趟，设计成立**。
  票 25 与 spec 六处「1.0」标签已改；AD-4 正文残留的「4 趟/日程」一并修。
  **纠错留痕保留在案**（三轮各自错在哪），不删。
- **BLOCK-2 锐角等价断言不可实施 + 容差自相矛盾**：首版参照源写
  `fork._compute_off_nadir_angle`，而该函数被本票 :37 删除 ⇒ 断言无法构造；
  且容差 `< 1e-9°` 与同句自述的「球面 vs WGS-84 法线差 ~0.6°」矛盾 ⇒ **正确实现也会红**。
  改为：参照源用**共享库** `_compute_off_nadir_angle`（`visibility.py:27`）+
  `_off_nadir_to_incidence`（`:48`）（本票保留不动，可 import）；
  容差改**双判据**——① 球面对球面 `< 1e-9°`（隔离法线差异，证公式等价）
  ② 实际 WGS-84 口径 `< 1.0°`（容许 0.6° 模型差）。
- **BLOCK-3 R4H「族表分叉」是我的误读，非 bug**：`scripts/recompute_r_fam.py:49` 的
  `FAMILIES = {..., "R4H": 400}` 其值是 **`base_seed`**（`:98` 以 `for code, base_seed`
  解包后拼 `seed{base_seed}`），**不是** `sss_core/scenarios.py:110` 的 `n_targets`（R4H=500）。
  两者是**不同量** ⇒ 无分叉。票面该条已撤回，只保留「R4H 出局时两处条目一并删除」。

另确认 4 项 CLOSED（FORK_MANIFEST 四处联动、零字节守卫复用、R21 四元组发散同 commit、
prereg 模板 append-only + 守卫补漏），行号抽查 20+ 处仅 3 处 MINOR（已在票面就地修正）。

**升级闸（rule 10）**：同一审者累计 3 轮未清零 → 按规则连同证据呈用户拍板。
用户 2026-10-05 令「继续」⇒ 进第四轮（放行前最后一轮），若仍有阻塞项则不再自审迭代。

### 第四轮等待期间主线程自查：又证伪一条验收判据（本轮第三次同类错误）

派第四轮 gate-review 的同时，我实测了票 24 的**锐角支等价判据**，**实测证伪它自己**：
在真实轨道（i=45°, e=0.001, h=570 km）上取**同一卫星状态**同时算两式，锐角支（新定义 incidence<90°）的差：

| 站点 | 旧正弦换算 vs 新矢量夹角 最大差（锐角支） |
|---|---|
| lat20/lon0 | **2.36°** |
| lat0/lon0 | **3.59°** |
| lat45/lon10 | **0.43°** |

差值随接近角单调增大、**不是常数**。⇒ **「两式公式等价、差 < 1e-9°」前提被证伪**：
`sin θ_i = (R+h)/R · sin η` 是**几何近似**（假设连线与球面几何相交于一点），
矢量夹角是精确式，**近似式 ≠ 恒等式**。
**若不实测，该判据会让正确实现也判红**——即验收标准本身是错的，比没判据更坏。

**处置**：票 24 该判据改**单向**——只验新定义自身（① 背面 >90° ② 正上方 ≈0，误差<0.01°
③ 轨道周期连续，相邻 1s 跳变<0.1° 排除折返）；旧路径对照仅作留档（记三点实测差），
**不得宣称等价**。spec MUST-1 同步改写（原「仰角>0」经第三轮判定无判别力，一直未同步，一并修）。
新增 MUST-1b 明文登记该证伪，防后续冷读再把「等价」当判据。

**本轮同类错误第三次**（前两次：48h 窗口的「2 次」当「每天 1 次」、
`recompute_r_fam.py` 的 `base_seed` 读成 `n_targets` 误报既存 bug）——
共同形态：**没算就下结论**。已沉淀为记忆 `feedback-equivalence-claim-needs-measurement`
（等价/逐位/恒等类判据必先实测；近似式与精确式不可互称等价；报既存 bug 前先确认同名是否同量）。
