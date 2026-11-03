# 实验开跑前代码就绪审查报告

**审查日期**: 2026-08-02
**审查员**: qwen (千问办公)
**审查目的**: 确认 RDR-003/RDR-004/🔴-1~6 修复后代码是否具备全量实验重跑条件
**审查范围**: `src/sar_sim/solver/` 核心代码 + 实验脚本 + 约束验证体系
**审查方法**: 4 路并行 Explore subagent（RDR-003 θ 过滤 / 解码函数约束兜底 / G-SM 顺序+遗传参数 / 新增测试与约束验证模块）+ 主 agent Read/Grep 交叉验证关键行

---

## 严重度统计

| 严重度 | 数量 | 说明 |
|--------|------|------|
| 🔴 阻塞 | **5** | 代码缺陷未修复，开跑会产生不可信数据 |
| 🟢 已修复 | **3** | 修复确认到位 |
| ⚪ 已存在但未接入 | **1** | 功能完备但未用于实验管线 |

**总体结论**: ❌ **不具备开跑条件**。上一轮审查发现的四个核心问题，仅 RDR-004 penalty 层（7/7 处）确认修复到位。RDR-003 θ 过滤、解码函数约束兜底、G-SM C2-squint 顺序、遗传算子参数均未修复。

---

## 🔴 阻塞发现（5 项）

### 🔴-1 | RDR-003 θ 过滤仍使用错误列（phi 而非 theta）

**位置**: `src/sar_sim/solver/baselines.py` L758-760
**状态**: 未修复（注释加了 `# RDR-003` 但代码未改）

当前代码：
```python
# L758-760
phi_min = instance.phi_min          # off-nadir 界限
phi_max = instance.phi_max
mask &= (np.abs(arr[:, 1]) >= phi_min) & (np.abs(arr[:, 1]) <= phi_max)
                                     # ^^^^ 列 1 = phi (off-nadir)
```

GeomCache 列定义（`types.py` L480）：
```
# columns: [t, phi, psi_sq, cos_psi, theta, q_nesz]
#                            列 0    1      2       3       4      5
```

RDR-003 要求过滤的是**入射角 θ**（incidence angle），对应列 4。当前代码过滤的是**偏天底角 φ**（off-nadir angle），对应列 1。两者通过 `theta = off_nadir_to_incidence(phi, altitude)` 非线性映射，数值接近但不等价。

**影响**:
- 入射角在 [15°, 50°] 范围内但偏天底角不在的行被错误排除
- 入射角超范围但偏天底角恰好落在 [15°, 50°] 的行被错误保留
- `instance` 无 `phi_min`/`phi_max` 属性时 fallback 为 [0°, 90°]，等于不过滤
- **RDR-003 的 baselines 重跑结果使用了这个错误过滤，数据不可信**

**证据**: `off_nadir_to_incidence` 已在文件顶部 L39 import，GeomCache 构造时已将 theta 预计算到列 4（`types.py` L497）。修复只需将 L760 改为 `arr[:, 4]` 并使用入射角界限。

**审查员注**: 上一轮审查（`full-audit-20260802-qwen.md` 🟡-8）将此定级为次要，RDR-003 升级为 P0 后此修复仍未落地。RDR-003 自己的 baselines 重跑（`run_baselines_v4.py`，200/200）使用的是错误过滤后的 `_b3_squint_minimize`，其输出数据（`baselines_200.json` 的 G-SM 列）仍然不可信。

---

### 🔴-2 | 解码函数无约束兜底，原样透传 τ-decoded 时刻

**位置**: `src/sar_sim/solver/so_f1.py` L226-306, `src/sar_sim/solver/moea.py` L311-370
**状态**: 未修复（代码无任何变化）

四个解码函数的当前行为：

| 函数 | 文件:行号 | C1 θ界 | C2/C3 tau_trans | 窗口约束 | 时间不重叠 | 违反处理 |
|------|-----------|--------|-----------------|----------|------------|----------|
| `_decode_b2_solution` | so_f1.py:226-264 | ❌ | ❌ | ❌ | ❌ | 无 |
| `_build_schedule_from_b2` | so_f1.py:267-306 | ❌ | ❌ | 部分¹ | ❌ | 无（透传） |
| `decode_solution` | moea.py:373-434 | ❌ | ❌ | ❌ | ❌ | 无 |
| `_build_schedule_from_moea` | moea.py:311-370 | ❌ | ❌ | 部分¹ | ❌ | 无（透传） |

¹ "部分"= 若 t_act 不落在任何窗口内，选距离最近的窗口但仍用原 t_act 构造 ScheduledObservation，导致 window 与 t_actual_start 可能不一致。

**核心证据**:

`_decode_b2_solution` (so_f1.py L248-253)：
```python
t_act = task.t_earliest + tau[i] * task.time_span
t_actuals.append(t_act)          # 直接解码，无任何检查
```

`_build_schedule_from_b2` (so_f1.py L283-305) fallback 逻辑：
```python
# 若 t_act 不在任何窗口内 → 选最近窗口，仍用 t_act
best_dist = min(abs(t_act - w_start), abs(t_act - w_end))
if dist < best_dist:
    best_dist = dist
    best_window = w
# ... 然后直接构造 ScheduledObservation(t_actual_start=t_act)
```

**影响**: RDR-004 penalty 修复（7 处）只改变优化器搜索压力，不影响解码输出。若 NSGA-III/GA 返回的最终解 penalty > 0（高维问题中完全可能），违规时刻原样进入 ScheduledObservation → 写入 results JSON → 被论文 Table 引用。

RDR-004 审计数据（`audit_gapbl_saved.py`，218 场景）：GA-P-BL 存盘解 **42.8% 相邻对时间重叠、43.6% C3 违规**。这些不可行数据若不修 decode 层，全量重跑后仍会出现同类问题。

**so_f1.py / moea.py 的实际改动**（非约束相关）:
- `_HotStartSampling.__init__` 新增 `seed: int = 1` 参数 — RNG 播种修复（可复现性改进 ✅）
- `ga_hotstart_solver` 调用改为 `_HotStartSampling(x0, population_size, seed or 1)` — 同上
- `moea_solver` 新增 `hotstart_sigma: float = 0.5` 参数 — sigma 参数化
- `_MOEAHotStartSampling` 新增 `sigma` 和 `seed` 参数 — 同上

以上均为可复现性改进，与硬约束执行无关。

---

### 🔴-3 | G-SM squint 最小化后无 C2 重新检查

**位置**: `src/sar_sim/solver/baselines.py` baseline_b3 L648-686
**状态**: 部分修复（C3/C4 移到 squint 之后 ✅，但 C2 未重检 ❌）

当前 baseline_b3 (G-SM) 执行顺序：

```
L648  _enforce_c2_transitions(observations, instance)    ← C2 姿态转移
L651-657  deduplicate                                      ← 去重
L665  _b3_squint_minimize(observations, geom_cache, ...)  ← squint 最小化（改 t_actual）
L683  _enforce_c3c4(observations, ...)                    ← C3/C4 能量+存储预算
```

**问题**: `_b3_squint_minimize` 在窗口范围内重选 t_actual 以最小化 |ψ_sq|（L767 `argmin(|cand[:, 2]|)`）。这个时间移动可能使两个相邻观测的间隔 < tau_trans，打破 C2 约束。而 C3/C4（L683）只做能量/存储预算削减（按优先级丢弃观测），**不检查姿态转移时间**。

**影响**: G-SM 输出的 schedule 可能包含 C2 违规（相邻观测间隔不足），但 f2/f3 仍按这些违规时刻计算。

**对比**: 上一轮审查时函数名为 `_enforce_c3_transitions`，现已拆分为 `_enforce_c2_transitions`（L115，姿态转移）和 `_enforce_c3c4`（L305，预算削减）。命名更清晰，但 C2 在 squint 之前执行的问题仍在。

**修复方向**: 在 `_b3_squint_minimize` 之后、`_enforce_c3c4` 之前，加一次 `_enforce_c2_transitions` 调用。

---

### 🔴-4 | 遗传算子参数仍与论文不符

**位置**: `src/sar_sim/solver/moea.py` L572-579, `src/sar_sim/solver/so_f1.py` L522-523
**状态**: 未修复

**moea.py L572-579（NSGA3 构造）**:
```python
algorithm = NSGA3(
    pop_size=population_size,
    ref_dirs=ref_dirs,
    sampling=sampling,
) if sampling is not None else NSGA3(
    pop_size=population_size,
    ref_dirs=ref_dirs,
)
# 无 crossover= / mutation= 参数 → 使用 pymoo 默认值
```

**so_f1.py L519-525（GA 构造）**:
```python
algorithm = GA(
    pop_size=population_size,
    sampling=_HotStartSampling(x0, population_size, (seed if seed is not None else 1)),
    crossover=SBX(prob=0.9, eta=15),              # ≠ 论文 ηc=20
    mutation=PM(prob=1.0 / (2 * instance.N), eta=20),  # ≠ 论文 pm=0.1
    eliminate_duplicates=False,
)
```

| 参数 | 论文声称 (L529-531) | moea.py 实际 | so_f1.py 实际 | pymoo NSGA3 默认 |
|------|---------------------|-------------|--------------|------------------|
| SBX pc | 0.9 | (未设) → 0.9 | 0.9 | 0.9 |
| SBX ηc | **20** | (未设) → **15** | **15** | 15 |
| PM pm | **0.1** | (未设) → **1/n_var** | **1/(2N)** | 1/n_var |
| PM ηm | **20** | (未设) → 20 | 20 | 20 |
| Das-Dennis p | 12 | 12 ✅ | — | — |

**影响**: 可复现性红线。任何按论文参数复现的尝试会得到不同结果。SBX ηc=15 vs 20 影响交叉分布范围；PM prob=1/(2N)（N=20 时 0.025，N=500 时 0.001）vs 论文 0.1 差异达 4~100 倍。

**修复位置**:
- `moea.py` L572-579: 显式添加 `crossover=SBX(prob=0.9, eta=20), mutation=PM(prob=0.1, eta=20)`
- `so_f1.py` L522: `eta=15` → `eta=20`
- `so_f1.py` L523: `prob=1.0 / (2 * instance.N)` → `prob=0.1`

**附注**: `so_f1.py` L360-361 的 `b2_profit_solver`（非论文实验管道入口）参数也不一致（SBX eta=15, PM prob=0.2, eta=10），但该函数不在论文实验管道中，可单独处理。

---

### 🔴-5 | ConstraintVerifier 未接入实验管线

**位置**: `src/sar_sim/verification/constraints.py`（627 行，C1-C4 全约束验证器）vs 实验脚本
**状态**: 功能完备但未使用

项目已有成熟的约束验证体系：

| 组件 | 位置 | 功能 |
|------|------|------|
| `ConstraintVerifier` | `verification/constraints.py` L436 | 编排器，支持 `verify_solution()` / `verify_from_chromosome()` / `verify_frontier()` / `feasible_frontier()` |
| `verify_c1_incidence_squint()` | L125 | C1: 入射角 + squint 角 |
| `verify_c2_transition()` | L236 | C2: 姿态机动时间 + 非重叠 |
| `verify_c3_energy()` | L348 | C3: 能量预算 |
| `verify_c4_memory()` | L390 | C4: 存储预算 |
| `ViolationDetail` / `PerConstraintResult` / `VerificationReport` | L38-105 | 结构化违规报告 |

`solver_factory.py` 的 `multi_moea_solver`（L622-739）正确集成了 ConstraintVerifier：
```python
# L630
verifier = ConstraintVerifier(instance)
# L659
vr = verifier.verify_frontier(frontier)
# L667-676
for sol, report in vr:
    if report.overall_pass:
        feasible.append(sol)      # 只保留可行解
    else:
        infeasible_count += 1     # 统计不可行解
# L680
reference_frontier = build_reference_frontier(feasible_frontiers)  # 只用可行解
```

**但实验脚本不走 `multi_moea_solver`**。Grep 确认所有实验 runner 直接调用 `moea_solver()`（moea.py）和 `b2_profit_solver_bl_seeded()`（so_f1.py），这两个函数**不调用 ConstraintVerifier**：

| 实验脚本 | 调用函数 | ConstraintVerifier? |
|----------|----------|---------------------|
| `run_moea_3obj.py` | `moea_solver()` | ❌ |
| `run_moea_2obj.py` | `moea_solver()` | ❌ |
| `run_moea_3obj_no_physics.py` | `moea_solver_no_physics()` | ❌ |
| `run_moea_3obj_no_incidence.py` | `moea_solver_no_incidence()` | ❌ |
| `run_moea_3obj_no_squint.py` | `moea_solver_no_squint()` | ❌ |
| `run_so_f1_bl.py` | `b2_profit_solver_bl_seeded()` | ❌ |
| `run_baselines_v4.py` | `baseline_b1` / `baseline_b3` | ❌ |
| `run_baselines_S7S8.py` | `baseline_b1` / `baseline_b3` | ❌ |
| `run_s1s2_hotstart_control.py` | `moea_solver()` | ❌ |
| `run_sigma_sweep.py` | `moea_solver()` | ❌ |

ConstraintVerifier 仅出现在三个审计脚本中：

| 审计脚本 | 用途 |
|----------|------|
| `audit_gapbl_saved.py` | GA-P-BL 存盘解审计（RDR-004 核验） |
| `audit_moea_live.py` | MOEA 实时审计 |
| `verify_gsm_c3_v2.py` | G-SM C3 验证（RDR-003 核验） |

**影响**: 优化器输出的解即使有约束违规，也不会被过滤或修复，直接进入 results JSON → 论文 Table。ConstraintVerifier 的可行解过滤逻辑（已在 `multi_moea_solver` 中验证可行）未惠及实际实验管线。

**修复方向**: 在 `moea_solver()` 返回前调用 `ConstraintVerifier.verify_solution()` 或 `feasible_frontier()` 做可行解过滤；或在各实验 runner 的结果收集阶段加 post-hoc 验证步骤。

---

## 🟢 已修复确认（3 项）

### 🟢-1 | RDR-004 C3 罚函数 penalty 层（7/7 处）

全部 7 处已从旧 `continue` 豁免模式改为直接约束解码时刻：

```python
# 统一新模式（7 处一致）
gap = t_b - (t_a + task_a.duration)
if gap < tau_trans:
    g += (tau_trans - gap) / max(task_b.duration, 1.0)
```

| # | 文件 | 行号 | 状态 |
|---|------|------|------|
| 1 | `so_f1.py` | L210-219 | ✅ 已修，带 `# RDR-004` 注释 |
| 2 | `moea.py` | L256-261 | ✅ 已修（多星分支） |
| 3 | `moea.py` | L276-280 | ✅ 已修（单星分支） |
| 4 | `solver_factory.py` | L190-193 | ✅ 已修 |
| 5 | `run_moea_3obj_no_physics.py` | L136-139 | ✅ 已修 |
| 6 | `run_moea_3obj_no_incidence.py` | L127-130 | ✅ 已修 |
| 7 | `run_moea_3obj_no_squint.py` | L186-189 | ✅ 已修 |

全局 grep 确认旧模式 `earliest_start_b = max(task_b.t_earliest, t_end_a + tau_trans)` 零残留。

**审查员注**: penalty 层修复到位，但如 🔴-2 所述，decode 层未修，优化器输出的最终解仍可能携带未修复的违规时刻。

### 🟢-2 | RNG 播种修复

`so_f1.py` 和 `moea.py` 的 HotStartSampling 类均新增 `seed` 参数，将 `np.random.RandomState()` 改为确定性播种 `np.random.RandomState(self.seed)`。可复现性改进。

### 🟢-3 | RDR-003 窗口过滤和 pass-through

`_b3_squint_minimize` 的窗口范围过滤（L755-757）和无合格行 pass-through（L761-765）均正确实现。squint 最小化不再跨窗口选择时间。（但 θ 过滤仍错误，见 🔴-1。）

---

## ⚪ 已存在但未接入（1 项）

### ⚪-1 | 完整约束验证体系（verification 子包）

`src/sar_sim/verification/constraints.py`（627 行）提供 C1-C4 全约束验证，支持 per-solution 和 per-frontier 验证，输出结构化违规报告（`ViolationDetail` / `PerConstraintResult` / `VerificationReport`）。已在 `multi_moea_solver` 中正确集成。但实验管线不调用 `multi_moea_solver`，见 🔴-5。

**相关测试**:
- `src/tests/test_b3_squint_min.py` — G-SM squint 最小化单测（4 tests: `test_b3_selects_min_squint`, `test_b3_does_not_jump_windows`, `test_b3_window_boundary`, `test_b3_no_geom_cache_fallback`）
- `src/tests/test_constraint_c4c5.py` — C3/C4 预算约束测试（3 tests）
- `src/tests/test_moea_c1_f3.py` — MOEA C1/f3 测试

**未找到** `test_decode_feasibility.py` 或类似解码可行性测试——解码函数无约束兜底的 gap 在测试层面也同样存在。

---

## 阻塞清单（开跑前必须全部完成）

| # | 修复项 | 文件:行号 | 改动量 | 影响 |
|---|--------|-----------|--------|------|
| B1 | θ 过滤改用 `arr[:, 4]` + 入射角界限 | baselines.py L758-760 | 1 行 | G-SM 数据 |
| B2 | 解码函数加 validate_and_repair 兜底 | so_f1.py L264/L306, moea.py L370/L434 | ~30 行新增 | 全部 Table 数值 |
| B3 | squint 后加 C2 重新检查 | baselines.py L665 之后 | 1 行调用 | G-SM 数据 |
| B4 | 遗传算子参数对齐 | moea.py L572-579, so_f1.py L522-523 | 3 行 | 全部 Table 数值 |
| B5 | ConstraintVerifier 接入实验管线 | moea.py 返回前 或 各 runner | ~10 行 | 可行解过滤 |

**级联关系**: B1+B2+B3 必须合并修复后一次重跑 baselines；B2+B4+B5 必须合并修复后一次重跑 MOEA + GA-P-BL。两组可并行（baselines 独立于 MOEA/GA-P-BL），但 B2 是共享依赖（同时影响 baselines 和 MOEA/GA-P-BL 的 decode 逻辑——实际上 baselines 走自己的 decode 路径，MOEA/GA-P-BL 走 `_build_schedule_from_*`，所以 B2 只影响 MOEA/GA-P-BL）。

**修正**: B1+B3 只影响 G-SM（baselines），B2+B4+B5 只影响 GA-P-BL + MOEA。两组独立，可并行修复和重跑。但 RDR-004 penalty 修复（已完成）同时影响两组，所以两组都需要在 penalty 修复的基础上重跑。

---

## 修复后的重跑计划

```
Phase 1: 合并所有代码修复
  B1 (baselines.py θ 过滤)  ─┐
  B3 (baselines.py C2 重检) ─┤── 同时修
  B2 (decode 兜底)           ─┤
  B4 (遗传算子参数)          ─┤
  B5 (ConstraintVerifier 接入)─┘

Phase 2: 并行重跑
  路线 A: run_baselines_v4.py (200) + run_baselines_S7S8.py (100)
          → baselines_200.json, baselines_S7S8.json
          → Table 2 G-BL/G-SM 列, Table 5 G-BL/G-SM 行

  路线 B: run_so_f1_bl.py (200)
          → GA-P-BL 存盘解 + progress.json
          → Table 2 GA-P-BL 列, Table 5 GA-P-BL 行

  路线 C: run_moea_3obj.py (200) + run_moea_2obj.py (200)
          + run_moea_3obj_no_*.py (3 × 200)
          → MOEA-2/MOEA-3 progress.json + 消融 progress.json
          → Table 2 MOEA 列, Table 3 HV, Table 5 MOEA 行, Table 6 消融

Phase 3: 统计重算
  statistical_analysis.py → statistical_results.json + effect_sizes.json
  → Friedman/Wilcoxon/Cliff's δ 全量重算

Phase 4: 论文数值更新
  Table 2/3/5/6 + 正文统计值 + §6.2/§6.6 G-SM 文本 + §6.5 消融文本
  → 核心结论是否成立？变体 D 是否仍击穿完整物理基线？
```

**预估时间**: Phase 2 路线 A ~1h, 路线 B ~2h, 路线 C ~4-6h（200+800 runs，3-obj MOEA 最慢）。三路并行 ~6h。Phase 3 ~30min。Phase 4 视数据变化幅度而定。

---

## 方法论说明

本审查采用 4 路并行 Explore subagent：

| 路线 | 职责 | 核查项数 |
|------|------|---------|
| RDR-003 θ 过滤 | baselines.py `_b3_squint_minimize` 逐行审查 | 3 项（窗口/角度/pass-through） |
| 解码函数约束兜底 | so_f1.py + moea.py 4 个解码函数 | 4 约束 × 4 函数 = 16 项 |
| G-SM 顺序 + 遗传参数 | baseline_b3 调用链 + NSGA3/GA 构造参数 | 2 项 |
| 新增测试与约束验证模块 | src/sar_sim/ 全目录搜索 + tests/ | ~20 关键词 |

主 agent 对 5 个 🔴 发现全部用 Read 直接读取代码行交叉验证。ConstraintVerifier 接入情况通过 Grep 实验脚本 import 行确认。

---

*报告生成于 2026-08-02 by qwen (千问办公)。遵循项目约定: 论文级审计用 🔴/🟡/🟢 分级，报告放 papers/<theme>/review/，文件名加 `-qwen` 后缀。*
