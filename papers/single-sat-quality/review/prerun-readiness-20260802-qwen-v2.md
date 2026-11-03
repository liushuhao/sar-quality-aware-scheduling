# 实验开跑前代码就绪审查报告 V2

**审查日期**: 2026-08-02（第二轮，代码更新后复审）
**审查员**: qwen (千问办公)
**前置报告**: `prerun-readiness-20260802-qwen.md`（V1，5 个🔴阻塞）
**审查目的**: 确认 V1 阻塞项修复后代码是否具备全量实验重跑条件
**审查范围**: `src/sar_sim/solver/` 核心代码 + `verification/constraints.py` + 实验脚本
**审查方法**: 主 agent Read/Grep 逐行核验 + 调用链追踪（verify_frontier → verify_solution → verify_c2_transition）

---

## 严重度统计

| 严重度 | V1 | V2 | 变化 |
|--------|-----|-----|------|
| 🔴 阻塞 | 5 | **1** | -4（B3 C2重检 + B4 遗传参数 + B5 MOEA frontier过滤 已修复） |
| ⚠️ 部分修复 | 0 | **2** | B2 decode兜底 + B5 管线接入 部分完成 |
| 🟢 已修复 | 3 | **5** | +2（B3 + B4） |

**总体结论**: ❌ **仍不具备开跑条件**，但差距从 5 个🔴缩小到 1 个❌ + 2 个⚠️。Claude Code 修复了 B3（C2 重检）、B4（遗传参数对齐）、B5 的 MOEA frontier 过滤分支。B1（θ 过滤一行改动）仍未动。B2/B5 的 ConstraintVerifier 接入存在三个缺陷：C2 在 t_earliest 上检查而非 t_actual、GA-P-BL 只标记不过滤、消融 runner 完全未接入。

---

## 修复确认（5 项 ✅）

### ✅ B3 — squint 最小化后 C2 重新检查

**位置**: `src/sar_sim/solver/baselines.py` L678-679
**V1 状态**: ❌ 阻塞
**V2 状态**: ✅ 已修复

新增代码：
```python
# L678-679
# ── Re-check C2 after squint/θ optimization (t_actual may have moved) ──
observations = _enforce_c2_transitions(observations, instance=instance)
```

baseline_b3 (G-SM) 当前执行顺序：

```
L648  _enforce_c2_transitions()           ← C2 姿态转移
L651-657  deduplicate                      ← 去重
L665  _b3_squint_minimize()               ← squint 最小化（改 t_actual）
L679  _enforce_c2_transitions()           ← C2 重检 ✅ NEW
L686  _enforce_c3c4()                     ← C3/C4 能量+存储预算
```

squint 最小化改了 t_actual 后，C2 重新强制姿态转移可行性。C3/C4 预算削减在最后，不依赖 t_actual。顺序正确。

---

### ✅ B4 — 遗传算子参数对齐

**位置**: `src/sar_sim/solver/moea.py` L575-580, `src/sar_sim/solver/so_f1.py` L520-524
**V1 状态**: ❌ 阻塞
**V2 状态**: ✅ 已修复

**moea.py L575-580（NSGA3 构造）**:
```python
algorithm = NSGA3(
    pop_size=population_size,
    ref_dirs=ref_dirs,
    sampling=sampling,
    crossover=SBX(prob=0.9, eta=20),     # ✅ 显式设置（V1: 未设 → pymoo 默认 15）
    mutation=PM(prob=0.1, eta=20),       # ✅ 显式设置（V1: 未设 → pymoo 默认 1/n_var）
) if sampling is not None else NSGA3(
    pop_size=population_size,
    ref_dirs=ref_dirs,
    crossover=SBX(prob=0.9, eta=20),     # ✅ 无 sampling 分支也设置
    mutation=PM(prob=0.1, eta=20),
)
```

**so_f1.py L520-524（GA 构造）**:
```python
algorithm = GA(
    pop_size=population_size,
    sampling=_HotStartSampling(x0, population_size, (seed if seed is not None else 1)),
    crossover=SBX(prob=0.9, eta=20),     # ✅ V1: eta=15
    mutation=PM(prob=0.1, eta=20),       # ✅ V1: prob=1/(2N), V1: eta=20(已对)
    eliminate_duplicates=False,
)
```

| 参数 | 论文声称 (L529-531) | V1 代码 | V2 代码 | 状态 |
|------|---------------------|---------|---------|------|
| SBX pc | 0.9 | 0.9 | 0.9 | ✅ |
| SBX ηc | 20 | 15 | **20** | ✅ 已对齐 |
| PM pm | 0.1 | 1/(2N) 或 1/n_var | **0.1** | ✅ 已对齐 |
| PM ηm | 20 | 20 | 20 | ✅ |
| Das-Dennis p | 12 | 12 | 12 | ✅ |

---

### ✅ V1-🟢-1 — RDR-004 penalty 层（7/7 处，V1 已确认，V2 维持）

全部 7 处旧 `continue` 豁免模式已改为直接约束解码时刻。全局 grep 确认旧模式零残留。详见 V1 报告。

### ✅ V1-🟢-2 — RNG 播种修复（V1 已确认，V2 维持）

`_HotStartSampling` 和 `_MOEAHotStartSampling` 均新增 `seed` 参数，确定性播种。

---

## 阻塞发现（1 项 ❌ + 2 项 ⚠️）

### ❌ B1 — RDR-003 θ 过滤仍使用错误列（phi 而非 theta）

**位置**: `src/sar_sim/solver/baselines.py` L761-763
**V1 状态**: ❌ 阻塞
**V2 状态**: ❌ 仍未修复（连续两轮未动）

当前代码（V1 与 V2 完全相同）：
```python
# L761-763
phi_min = instance.phi_min              # off-nadir 界限
phi_max = instance.phi_max
mask &= (np.abs(arr[:, 1]) >= phi_min) & (np.abs(arr[:, 1]) <= phi_max)
#                 ^^^^^^^^ 列 1 = phi (off-nadir)，应为 arr[:, 4] = theta (incidence)
```

GeomCache 列定义（`types.py` L480）：`[t, phi, psi_sq, cos_psi, theta, q_nesz]`，列 4 = theta（入射角），已由 `off_nadir_to_incidence(phi, altitude)` 预计算。

RDR-003 要求过滤入射角 θ ∈ [15°, 50°]。当前过滤偏天底角 φ，与入射角非线性映射。`off_nadir_to_incidence` 已在文件顶部 L39 import，修复只需改一行。

**影响**: RDR-003 的 baselines 重跑（`run_baselines_v4.py`，200/200）使用此错误过滤，G-SM 列数据不可信。

**修复**:
```python
# L761-763 改为:
theta_min = off_nadir_to_incidence(instance.phi_min, instance.altitude_m)
theta_max = off_nadir_to_incidence(instance.phi_max, instance.altitude_m)
mask &= (arr[:, 4] >= theta_min) & (arr[:, 4] <= theta_max)
```

---

### ⚠️ B2/B5-A — ConstraintVerifier 接入 MOEA frontier 过滤，但 C2 在 t_earliest 上检查

**位置**: `src/sar_sim/solver/moea.py` L622-633, `src/sar_sim/verification/constraints.py` L571-605, L467-518, L236-305
**V1 状态**: ❌ 阻塞（ConstraintVerifier 未接入实验管线）
**V2 状态**: ⚠️ 部分修复（MOEA frontier 过滤已接入，但 C2 验证有缺陷）

**已接入部分 ✅**:

moea.py L622-633（`moea_solver` 返回前）：
```python
# ── Post-hoc constraint verification: filter infeasible solutions ──
n_infeasible = 0
if frontier:
    verifier = ConstraintVerifier(instance)
    verified = verifier.verify_frontier(frontier)
    feasible = [sol for sol, rpt in verified if rpt.overall_pass]
    n_infeasible = len(frontier) - len(feasible)
    if feasible:
        feasible_indices = [i for i, (_, rpt) in enumerate(verified) if rpt.overall_pass]
        x_source = x_source[feasible_indices] if x_source is not None else None
        frontier = feasible
    # If all infeasible, keep original frontier (will be flagged in meta)
```

不可行解从 Pareto 前沿中过滤，knee 解从可行解子集中选取。这是对 V1 的显著改进。

**缺陷：C2 验证在 t_earliest 而非 t_actual 上执行 ❌**

调用链追踪：

1. `solutions_to_frontier()`（moea.py L440-466）生成 frontier dict，键为 `selected`、`phis`、`f1`、`f2`、`f3`、`n_tasks`——**不含 `t_actual`**

2. `verify_frontier()`（constraints.py L593-603）对每个解调用 `verify_solution(selected, phi_full)`——**不传 `t_actual`**

3. `verify_solution()`（constraints.py L467-518）签名有 `t_actual: Optional = None`，但 L493-497 传给 `verify_c2_transition` 时 `t_actual=None`

4. `verify_c2_transition()`（constraints.py L253-254）当 `t_actual=None` 时，回退到 `t_earliest` 计算 gap："Without t_actual, falls back to t_earliest to preserve backward compatibility"

**后果**: 一个 t_actual 严重重叠的解（两个观测的实际时刻间隔 < tau_trans）可能通过 C2 检查，因为检查的是 t_earliest（最早可见时刻）间隔，而 t_earliest 的间隔通常比 t_actual 宽松。

RDR-004 penalty 修复（7/7 处）在 `_evaluate` 中惩罚 decoded-time gap，提供搜索压力驱使优化器避开 C2 违规。但 penalty ≠ 硬约束——当解空间紧张时优化器可能接受有 penalty 的解，而 frontier 过滤的 C2 检查（在 t_earliest 上）不会捕获这些违规。

**修复方向**:
- 让 `solutions_to_frontier()` 在 frontier dict 中加 `t_actuals` 键（从 `decode_solution` 已有的 t_actuals 传入）
- 让 `verify_frontier()` 读取 `t_actuals` 并传给 `verify_solution()`
- 或让 `verify_frontier()` 调用 `verify_from_chromosome()`（L520，支持从原始染色体解码并验证，含 t_actual）

---

### ⚠️ B2/B5-B — GA-P-BL 只标记不可行不过滤不修复

**位置**: `src/sar_sim/solver/so_f1.py` L583-594
**V1 状态**: ❌ 阻塞（解码函数无约束兜底）
**V2 状态**: ⚠️ 部分修复（ConstraintVerifier 已接入，但只存 metadata）

so_f1.py L583-594（`ga_hotstart_solver` 返回前）：
```python
# Post-hoc constraint verification
if sel:
    phi_full = np.zeros(instance.N, dtype=float)
    for idx, task_idx in enumerate(sel):
        phi_full[task_idx] = phis[idx] if idx < len(phis) else 0.0
    verifier = ConstraintVerifier(instance)
    report = verifier.verify_solution(sel, phi_full)     # 不传 t_actual
    meta["constraint_feasible"] = report.overall_pass     # 只标记
    meta["n_constraints_failed"] = report.n_failed        # 只计数
else:
    meta["constraint_feasible"] = True
    meta["n_constraints_failed"] = 0
```

**两个问题**:

1. **不传 t_actual**（与 B2/B5-A 同一缺陷）：C2 在 t_earliest 上检查

2. **只标记不过滤不修复**: GA-P-BL 返回单个最优解（非 frontier）。`verify_solution` 只把 `constraint_feasible` 和 `n_constraints_failed` 写入 metadata。如果最优解不可行，schedule 和 f1/f2/f3 仍原样返回。下游实验脚本拿到的是不可行 schedule + 不可行数值。

**与 MOEA 的差异**: MOEA 有 frontier，可以过滤不可行解后从可行子集选 knee。GA-P-BL 只有一个解，没有"过滤"选项——要么用，要么没有。需要的是"修复"（delay-within-window 或 drop）而非"过滤"。

**修复方向**:
- 选项 A: `verify_solution` 报告不可行时，在 schedule 上执行 `_enforce_c2_transitions`（baselines.py 已有的 delay-or-skip 逻辑），重算 f1/f2/f3
- 选项 B: 记录 warning + 返回不可行标记，由下游实验脚本决定是否接受（当前行为，加 warning）
- 选项 C: `verify_solution` 传 t_actual 后，若 C2/C1 不过则尝试在窗口内 delay 修复

---

### ⚠️ B2/B5-C — 三个消融 runner 完全未接入 ConstraintVerifier

**位置**: `papers/single-sat-quality/experiments/run_moea_3obj_no_*.py`
**V1 状态**: ❌ 阻塞
**V2 状态**: ⚠️ 未接入

Grep `ConstraintVerifier|verify_solution|verify_frontier|feasible_frontier` 在三个消融 runner 中零匹配：

| 文件 | 自定义 Problem 类 | ConstraintVerifier? |
|------|-------------------|---------------------|
| `run_moea_3obj_no_physics.py` | `NoPhysicsProblem` | ❌ |
| `run_moea_3obj_no_incidence.py` | `NoIncidenceProblem` | ❌ |
| `run_moea_3obj_no_squint.py` | `NoSquintProblem` | ❌ |

这三个 runner 自定义了独立的 `moea_solver_no_*` 函数和 Problem 类，不走 `moea.py` 的 `moea_solver()`，因此不经过 L622-633 的 frontier 过滤。Table 6 消融实验全部 4 个变体（A/B/C/D）不受约束验证保护。

RDR-004 penalty 修复（7/7 处）覆盖了这三个 runner（L136-139/L127-130/L186-189），所以优化器内部的 C3 penalty 已修复。但没有 post-hoc 验证层兜底。

**修复方向**: 在三个 runner 的 `moea_solver_no_*` 返回前加 ConstraintVerifier 过滤（复用 moea.py L622-633 的模式），或让它们调用 `moea_solver()` 并传入自定义 Problem 类。

---

## 解码函数状态（V1 → V2 无变化）

四个解码函数本身**仍未加约束兜底**，但 MOEA 路径通过 frontier 过滤间接弥补，GA-P-BL 路径通过 metadata 标记部分弥补。

| 函数 | 文件:行号 | 函数内约束检查 | 外部验证 |
|------|-----------|----------------|----------|
| `_decode_b2_solution` | so_f1.py L227-265 | ❌ 无 | ga_hotstart_solver 的 verify_solution（不传 t_actual） |
| `_build_schedule_from_b2` | so_f1.py L268-307 | ❌ 无 | 同上 |
| `decode_solution` | moea.py L376-434 | ❌ 无 | moea_solver 的 verify_frontier（不传 t_actual） |
| `_build_schedule_from_moea` | moea.py L314-373 | ❌ 无 | 同上 |

解码函数行为与 V1 完全一致：τ 直接解码为 t_actual，无窗口/C1/C2/重叠检查，fallback 选最近窗口。

---

## 阻塞清单（V2）

| # | 修复项 | 文件:行号 | 改动量 | V1 状态 | V2 状态 |
|---|--------|-----------|--------|----------|----------|
| B1 | θ过滤改用 arr[:,4] + 入射角界限 | baselines.py L761-763 | 3 行 | ❌ | ❌ |
| B2a | verify_frontier 传 t_actual | constraints.py L593-603 + moea.py L440-466 | ~10 行 | ❌ | ⚠️ 新缺陷 |
| B2b | GA-P-BL 不可行解修复/过滤 | so_f1.py L583-594 | ~15 行 | ❌ | ⚠️ 只标记 |
| B2c | 消融 runner 接入 ConstraintVerifier | 3 × run_moea_3obj_no_*.py | ~15 行 × 3 | ❌ | ⚠️ 未接入 |
| B3 | squint 后 C2 重检 | baselines.py L678-679 | — | ❌ | ✅ |
| B4 | 遗传算子参数对齐 | moea.py L579-580 + so_f1.py L523-524 | — | ❌ | ✅ |
| B5 | ConstraintVerifier 接入管线 | moea.py L622-633 | — | ❌ | ⚠️ 部分 |

**最小开跑前置条件**（按优先级）:

1. **B1（3 行）**: baselines.py L761-763 改 arr 索引和界限。**连续两轮未修，最易遗漏。**
2. **B2a（~10 行）**: `solutions_to_frontier` 加 `t_actuals` 键 或 `verify_frontier` 改调 `verify_from_chromosome`。否则 MOEA frontier 过滤的 C2 检查无效。
3. **B2b（~15 行）**: so_f1.py 不可行时执行 `_enforce_c2_transitions` 修复 + 重算 f1/f2/f3，或至少 log warning。
4. **B2c（~15 行 × 3）**: 三个消融 runner 加 ConstraintVerifier 过滤。

B1 和 B2a 是硬阻塞——不修则数据不可信。B2b 和 B2c 是软阻塞——不修则 GA-P-BL 和消融数据可能含不可行解，但 penalty 修复已降低违规概率。

---

## 约束执行层级全景（V2）

```
                     MOEA 路径                          GA-P-BL 路径
                     ─────────                          ───────────
优化器内部:
  _evaluate()        penalty (RDR-004 7/7 ✅)           penalty (RDR-004 ✅)
                     + 遗传参数对齐 (B4 ✅)              + 遗传参数对齐 (B4 ✅)

解码层:
  decode/build       ❌ 无约束检查                       ❌ 无约束检查
                     (原样透传 τ-decoded t_actual)       (原样透传 τ-decoded t_actual)

Post-hoc 验证层:
  frontier 过滤       ⚠️ verify_frontier ✅              ⚠️ verify_solution (metadata only)
                     但 C2 在 t_earliest ❌              C2 在 t_earliest ❌
                     不可行解被过滤 ✅                   不可行解只标记不过滤 ❌

实验管线接入:
  moea_solver()       ✅ frontier 过滤已接入              N/A (由 ga_hotstart_solver)
  ga_hotstart_solver  N/A                                ⚠️ metadata 已接入
  消融 runner (×3)    ❌ 未接入                           N/A

Baselines 路径:
  baseline_b1 (G-BL)  C2 内联 delay-or-skip ✅           C1 不检查 ❌
  baseline_b3 (G-SM)  C2 → squint → C2重检(B3✅) → C3/C4  C1 θ过滤错误(B1❌)
```

---

## 修复后重跑计划（V1 计划维持不变）

```
Phase 1: 合并所有代码修复
  B1 (baselines.py θ 过滤)      ──┐
  B2a (verify_frontier 传 t_actual) ─┤── 同时修
  B2b (GA-P-BL 不可行修复)       ──┤
  B2c (消融 runner 接入验证)      ──┘

Phase 2: 并行重跑（B3/B4 已修复，RDR-004 penalty 已修复）
  路线 A: run_baselines_v4.py (200) + run_baselines_S7S8.py (100)
  路线 B: run_so_f1_bl.py (200)
  路线 C: run_moea_3obj.py (200) + run_moea_2obj.py (200)
          + run_moea_3obj_no_*.py (3 × 200)

Phase 3: 统计重算 (statistical_analysis.py)

Phase 4: 论文数值更新 + 核心结论验证
```

**预估时间**: Phase 2 三路并行 ~6h。Phase 3 ~30min。Phase 4 视数据变化而定。

---

## 与 V1 的差异总结

| 维度 | V1 (5 个🔴) | V2 (1❌ + 2⚠️) | 改进 |
|------|-------------|----------------|------|
| B1 θ过滤 | ❌ 未修 | ❌ 未修 | 无变化 |
| B2 decode 兜底 | ❌ 无任何兜底 | ⚠️ MOEA frontier 过滤已接入（但 C2 弱检）；GA-P-BL 只标记 | 显著改进 |
| B3 C2 重检 | ❌ 无 | ✅ 已加 | 修复 |
| B4 遗传参数 | ❌ eta=15/prob≠0.1 | ✅ eta=20/prob=0.1 | 修复 |
| B5 管线接入 | ❌ 未接入 | ⚠️ MOEA 已接入（有缺陷）；GA-P-BL metadata；消融未接入 | 部分修复 |

Claude Code 在本轮修复了 B3（1 行）、B4（3 行）、B5-MOEA 分支（~15 行 frontier 过滤），共约 19 行实质改动。未修复的 B1 也是约 3 行改动。B2 的三个子缺陷各需 10-15 行。

---

*报告生成于 2026-08-02 by qwen (千问办公)，第二轮复审。遵循项目约定: 🔴/🟡/🟢/⚠️ 分级，报告放 papers/<theme>/review/，文件名加 `-qwen` 后缀。*
