# FORK MANIFEST — papers/sliding-spotlight-scheduling/

> 冻结文档（ADR GRILL-002「Fork Manifest 与基线协议」节授权，票 02 产出，2026-09-27）。
> 本文件是从共享库 `src/sar_sim/` 复制进分叉包 `sss_core/` 的**唯一合法清单**。
> 状态：**FROZEN**（首次冻结 v1，随票 02 提交生效）。

## 回写条款（write-back clause，MUST）

1. 任何后续票要复制共享库的**任何**文件/函数/常量进 `sss_core/`，**必须先回写本 manifest**（新增 F-NN 条目 + 守卫覆盖映射行），再复制，再补恒等式守卫测试——顺序固定，缺一步即违规。
2. **manifest 外复制视为违规**：守卫测试按本清单反向断言（`test_fork_scope_matches_manifest_f01` 型），fork 包出现清单外的共享库符号即红。
3. 复制以「清单内符号」为准，**整文件顺手复制不合法**——每条 F-NN 必须列明复制了哪些符号、明确排除哪些符号及排除理由（最小复制面，防机会式复制把整仓复制从千刀累积达成，ADR GRILL-002 Alternatives (b)）。
4. 共享库侧后续修订（前篇审稿改动）到达时：先 cherry-pick 到分叉 + 守卫对账，再重置 M1 基线 tag——顺序固定（ADR M1 基线重置协议）。

## 基线登记

| 项 | 值 |
|---|---|
| M1 基线 tag | `paper2-m1-baseline`（annotated） |
| 指向 commit | `60ee1e8655dee96c1fc9aaa00c5d7982a7958069` |
| 共享库测试基线 N₀ | 145（`PYTHONPATH=src python -m pytest src/tests/ --collect-only`，2026-09-27） |
| 零字节断言 | `git diff paper2-m1-baseline..HEAD -- src/sar_sim` 为空 + `git status --porcelain src/sar_sim` 为空 |

## 分叉包命名记录

- **选定：`sss_core`**（sliding-spotlight-scheduling core）。与 `sar_sim` 无任何前缀共享，双 `sys.path` 插入下 import 解析零碰撞。
- **被否：沿用 `sar_sim`**——同进程双根 sys.path 插入下先 import 者胜，同名包使守卫对照「自身 vs 自身」恒绿（假绿），直接违反票 02 红线。
- **被否：`sar_sim_p2` / `sar_sim2`**——可读性差且保留碰撞根名前缀，grep/审阅时易与共享库混淆；无技术收益。

## 复制清单（frozen）

### F-01 — NESZ cos³ξ 辐射度量核

| 字段 | 值 |
|---|---|
| 源文件 | `src/sar_sim/metrics/nesz.py` @ `paper2-m1-baseline`（60ee1e8） |
| 分叉文件 | `papers/sliding-spotlight-scheduling/sss_core/metrics/nesz.py` |
| 复制符号 | 常量 `_K_NESZ_DEFAULT`, `_THETA_REF_DEG`, `_THETA_REF`, `_COS3_THETA_REF`；函数 `nesz_linear`, `nesz_db`, `quality_score` |
| 排除符号及理由 | `elevation_to_off_nadir`, `incidence_to_elevation`, `off_nadir_to_incidence`, `incidence_to_off_nadir`（几何换算器——本篇由自身轨道几何 builder 提供精确几何，spec D4 质量链只消费精确几何）；`quality_score_from_elevation`（换算器包装 API，随几何换算器一并排除——同上）；`aggregate_quality`, `quality_summary`（依赖共享类型 `sar_sim.types.ScheduledObservation`，复制会把共享类型拖过分叉边界）；`EARTH_RADIUS_MEAN_M`, `_DEFAULT_ALTITUDE_M`（几何换算器常量，随换算器一并排除）。**共享库 nesz.py 全部 10 函数 + 6 常量对照：复制 3 函数 + 4 常量，其余 7 函数 + 2 常量全在排除清单**（独立审查 2026-09-27 补齐，守卫 denylist 与本清单同步） |
| 数值一致性要求 | 逐位一致（同一操作序列，同解释器下浮点确定）；守卫用**精确相等**断言 |
| 语义注记 | `quality_score` 仅诊断用；本篇目标 f_Q 为独立逐模式量（spec D6），不得与本核混淆 |

### F-02 — 真轨道窗几何核（票 16，2026-10-03 登记）

**登记时点**：本条目在**复制之前**登记（回写条款 1 的固定顺序：登记 → 复制 → 补守卫）。裁剪面由 2 视角独立 subagent 审查后择优（票 body「开工前设计裁决」节留痕）。

| 字段 | 值 |
|---|---|
| 源文件 | `src/sar_sim/generator/orbit.py`、`src/sar_sim/generator/visibility.py`（几何子集）、`src/sar_sim/generator/target.py`（两个几何 helper）@ `paper2-m1-baseline`（60ee1e8） |
| 分叉文件 | `sss_core/realwindows.py`（单模块，避免碎片化） |
| 复制符号 | **orbit**：`solve_kepler`, `_rgf`, `_rgi`, `_rgu`, `kepler_to_eci`, `propagate_orbit`, 常量 `MU_EARTH`；**visibility 几何子集**：`_compute_off_nadir_angle`, `_determine_look_direction`（**票 24 起**），`satellite_to_target_vector`（**票 24 起不再是逐字复制**——入射角改目标侧向量夹角，见下方语义注记）；**target**：`lat_lon_to_ecef`, `compute_earth_rotation_angle`, `eci_to_ecef_rotation`, 常量 `EARTH_EQUATORIAL_RADIUS`, `EARTH_FLATTENING`, `EARTH_POLAR_RADIUS`, `EARTH_E2`（后四者是 `lat_lon_to_ecef` 的**必需** WGS-84 依赖链：`EARTH_E2` 由 `EARTH_POLAR_RADIUS`/`EARTH_EQUATORIAL_RADIUS` 派生，后者再由 `EARTH_FLATTENING` 派生——AST 实测确认函数体直接引用，排除即断链） |
| 分叉内独立定义（**非复制**） | `KeplerianElement`、`ECIState` —— 纯 `@dataclass(frozen=True)` 数据类，无方法体依赖（仅 `__post_init__` 校验），本地定义是**切断**共享类型边界而非跨越。**F-01 的排除先例在此不适用**：F-01 排除 `aggregate_quality` 是因其类型 `ScheduledObservation` 携带行为与调度器所有权纠缠，纯数据类不同 |
| 排除符号及理由 | `find_visibility_windows`, `visibility_matrix`（**票 16 裁剪的核心**）：二者返回 `ObservationWindow` 共享类型，且窗口**语义**（掩码判定、处置计数、簇生成）必须由本篇 `sss_core.predicates` 独占——票面明令「禁生成器私有重实现」，复制过来即制造第二套窗口语义；`make_targets`（目标工厂，票 16 自带地理簇生成器）；`EARTH_RADIUS_MEAN_M`（**F-01 已排除**，重复复制即制造第二源；F-02 引用分叉自身 `sss_core.geometry.R_EARTH_M`，值同为 6371000.0，由常量双源守卫钉死）。**WGS-84 四常量已在复制面内**（初稿曾误列排除，AST 实测 `lat_lon_to_ecef` 函数体直接引用 `EARTH_EQUATORIAL_RADIUS` 与 `EARTH_E2`，排除即 NameError） |
| 数值一致性要求 | 逐位一致；守卫用**精确相等**断言。**票 24 分域**：轨道传播链（`propagate_orbit`/`solve_kepler`/旋转 helper）**仍逐位一致**；`satellite_to_target_vector` 的 incidence 与 elevation **不再逐位比对**（定义已分叉），其余元组亦因 R21 时区修复而发散 ⇒ 改由 `geodetic_normal` + 独立构造对照 |
| 语义注记（**关键**） | 共享库的 `squint_deg`（`visibility.py:154-159`，`arcsin(\|los·track\|/\|los\|)`）与本篇 `sss_core.geometry.squint_at`（`atan(Vs·(t−t_ca)/R0)`）**不是同一个物理量**：前者是目标处的**全沿轨偏航角**（实测 600 s 内 6.542°–19.843°，跨度 13.3°，几乎不随窗内时间变化），后者是**窗内相对最近点的偏移**（以 `t_ca` 为零点，±12° 摆动）。实测同目标同几何下 `dt=0` 时二者为 12.749° vs 0.000°，**无法通过标定互相换算**。⇒ 三级联：**入射掩码腿**消费向量 incidence，**模式包络腿必须消费 `squint_at(t)`**（它才是驱动 `duration_scene_s` 与 AASR `b_d` 的那个斜视），向量 squint **不得**代入包络判定 |

**F-02 守卫**（`tests/test_fork_identity_realwindows.py`，票 16 产出）：

| Manifest 项 | 被守卫符号 | 断言形态 |
|---|---|---|
| F-02 | `propagate_orbit`, `solve_kepler` | ≥3 组固定 `KeplerianElement` 夹具逐位一致；**禁只给 raan=0/arg_perigee=0 的圆轨道**（会掩盖旋转矩阵错误，本仓历史事故模式）；含 `e≥0.05` 使 Newton 迭代 >1 步 |
| F-02 | 共享库 `satellite_to_target_vector` | **票 24 起守卫共享库本身**：七元组逐位一致，证明它未被改动（三篇论文的场景生成器依赖其标量签名，故本票不改它） |
| F-02 | fork `satellite_to_target_vector` | **票 24 起**：入射角对 `geodetic_normal` + 独立 ECEF 构造断言（差 < 1e-6），并断言背面目标不报带内值；**不与共享库比对**（旧正弦定理是几何近似，与精确向量夹角在锐角支差 0.4–3.6°，实测） |
| F-02（常量双源） | `R_EARTH_M` / `MU_EARTH_M3_S2` | 分叉 `geometry.py` 常量 == 共享 `nesz.EARTH_RADIUS_MEAN_M` / `orbit.MU_EARTH` |
| F-02（范围） | 全 fork 符号集 | 恰好 F-01+F-02 登记符号；`find_visibility_windows`/`visibility_matrix` **必须缺席**（最锋利的一条） |
| 回写条款 2 | 全树自含 | 复用 `test_fork_identity_nesz.py` 的两个全树守卫（票 16 已扩面） |

## 守卫覆盖映射表（manifest 项 ↔ 守卫测试）

守卫测试文件：`papers/sliding-spotlight-scheduling/tests/test_fork_identity_nesz.py`

| Manifest 项 | 被守卫符号 | 守卫测试 | 断言形态 |
|---|---|---|---|
| F-01 | `nesz_linear` | `test_fork_nesz_linear_matches_shared` | 固定输入逐位一致（含 grazing → inf 分支 + 非默认 K_NESZ 路径） |
| F-01 | `nesz_db` | `test_fork_nesz_db_matches_shared` | 固定输入逐位一致 |
| F-01 | `quality_score` | `test_fork_quality_score_matches_shared` | 固定输入逐位一致 + q(θ_ref)=1 精确 |
| F-01（包边界） | 模块解析 | `test_guard_anti_alias_modules_distinct` | 两侧 `__file__` 路径不同（反别名，防同名包 import 竞争假绿） |
| F-01（包边界） | 模块注册 | `test_guard_anti_alias_sys_modules_keys_distinct` | `sys.modules` 两个全限定名各自注册且文件不同 |
| 回写条款 2 | 分叉自含性 | `test_fork_self_contained_no_sar_sim_import` | **全树** `rglob("sss_core/**/*.py")` 源码 regex：禁 `import sar_sim`（票 16 扩面：原实现只查 `metrics/nesz.py` 单文件，新 fork 文件不受约束） |
| 回写条款 2 | 分叉自含性（全树符号） | `test_no_shared_only_symbol_defined_anywhere_in_the_fork` | **全树** AST 扫描：任一 fork 文件顶层定义的共享库专有符号即红（票 16 扩面：原 `test_fork_scope_matches_manifest_f01` 用 `hasattr` 绑在单模块对象上，符号复制进新文件不可见） |
| 复制清单条款 3 | 最小复制面 | `test_fork_scope_matches_manifest_f01` | fork 恰好定义 F-01 符号集，且不含共享库独有符号 |

覆盖率声明：F-01 全部复制符号均有恒等式守卫 + 包级反别名/自含/范围守卫，manifest 覆盖率 100%。新增 F-NN 时映射表必须同步加行，否则回写不完整。

## 运行方式（repo root）

```
# 守卫测试（新域）
PYTHONPATH=src "/d/Program Files/Python/python" -m pytest papers/sliding-spotlight-scheduling/tests/ -v

# 共享库回归面（N₀ == 145 断言防静默漏收集）
PYTHONPATH=src "/d/Program Files/Python/python" -m pytest src/tests/ -v
```

## 票 10 零复制声明（2026-09-27，非 F-NN 文档节）

票 10 调度器装配**未复制任何共享库符号**：pymoo 0.6.1.6（外部依赖，不触回写条款）提供 NSGA2 算法档（D8 授权实现票按 pymoo 支持定）；前篇 `solver/moea.py` 为 NSGA-III 三目标 + 固定时长物理，无符号可复用。2N 编码结构同构（moea.py:107-116 设计参照）但解码语义异构（分段投影 vs 线性映射）；分叉域内全部 τ 解码位点收口 `sss_core/evaluator.py::decode_tau`（位点清单见该模块 docstring），并有源扫描守卫禁止域内出现前篇线性解码模式。前篇四点位（moea.py:128/:412/:679 + so_f1.py:84/:243）仅为设计参照，非守卫对象。
