# Code Review — Constraint Refactor (C1–C4 Alignment)

- **作者**: trae
- **日期**: 2026-08-02
- **审查范围**: 工作树 vs `HEAD`（`8b2120a`），19 个文件未提交
- **审查方法**: 双轴并行（Standards + Spec），对照 `papers/single-sat-quality/small-paper-ijae.tex` §3.3 Constraints
- **备份位置**: `backup/pre-verify-20260802-151348/`
- **关联 RDR**: [rdr-003-gsm-unconstrained-squint-argmin.md](rdr-003-gsm-unconstrained-squint-argmin.md)、[rdr-004-c3-penalty-delayable-loophole.md](rdr-004-c3-penalty-delayable-loophole.md)

## 改动背景

本轮改动目标是把代码从旧 C1–C7 编号体系对齐到论文 §3 的 C1–C4 新体系，并落地 RDR-004（C2 转移惩罚按解码时间直接计算）。配套还有 Earth-radius 统一、squint 公式一致性、baselines 命名更新。

## Standards 轴

### 硬违规

**无**。文件放置（solver 在 `src/sar_sim/solver/`、测试在 `src/tests/`、消融脚本在 `papers/single-sat-quality/experiments/`）、命名格式（`test_<module>_<scenario>.py`、`run_moea_3obj_*.py`）、red lines（无 roll/yaw 替代 φ/ψ_sq、无 solver 代码落入 `papers/`）均符合 `AGENTS.md`。

### 判断性建议（baseline smells）

#### S1. RDR-004 gap-penalty 重复代码（Duplicated Code / Shotgun Surgery）— 优先

同一段 4 行代码出现在 6 个文件：

```python
gap = t_b - (t_a + task_a.duration)
if gap < tau_trans:
    g += (tau_trans - gap) / max(task_b.duration, 1.0)
```

涉及：`moea.py`（单星 + 多星两条路径）、`so_f1.py`、`solver_factory.py`、`run_moea_3obj_no_incidence.py`、`run_moea_3obj_no_physics.py`、`run_moea_3obj_no_squint.py`。

**建议**: 抽到 `solver/types.py` 中 `compute_los_separation` 旁边的 helper（如 `c2_transition_penalty(t_a, t_b, task_a, task_b, tau_trans)`），6 处统一调用。

#### S2. squint 计算重复（Duplicated Code）— 优先

`generate_all_scenarios.py` 与 `generate_s4_s6.py` 各有一份相同的 4 行 squint 公式：

```python
los_unit = los / distance
track_dir = sat_vel_ecef / np.linalg.norm(sat_vel_ecef)
los_along = np.dot(los_unit, track_dir)
squint = np.degrees(np.arcsin(np.clip(abs(los_along), 0.0, 1.0)))
```

注释自承"必须与 `satellite_to_target_vector()` in visibility.py 一致"——即已知第三份拷贝。

**建议**: 把 `satellite_to_target_vector` 中的 squint 计算抽成独立函数（如 `compute_squint_deg(los, sat_vel_ecef)`），三处统一调用。

#### S3. `test_constraint_c4c5.py` 文件名陈旧（Mysterious Name）— 优先

docstring 已改为 "C3/C4"，但文件名仍是 `test_constraint_c4c5.py`。

**建议**: 重命名为 `test_constraint_c3c4.py`。

#### S4. `test_c6_no_duplication_pass` 死测试（Refused Bequest）

C6 已删除，该测试被改造成"测 C2/C3/C4 是否 manageable"，已无 C6 含义。

**建议**: 删除，或重命名为 `test_multisat_no_duplication_backward_compat` 并改写断言以反映真实测试意图。

#### S5. seed 解析重复（Duplicated Code）

`seed if seed is not None else 1` 在 6+ 处重复（`moea.py`、`so_f1.py` ×3、`solver_factory.py`、3 个消融脚本）。

**建议**: 抽 `_resolve_seed(seed)` helper。

#### S6. 部分重命名未表达意图（Mysterious Name）

- `_c3_with_theta_opt` → `_c2_with_theta_opt`：只换编号，仍不透明
- `_enforce_c4c5` → `_enforce_c3c4`：同上
- `_c3_transition_los` → `_c2_transition_los`：同上

对比好命名：`verify_c1_angle_feasibility` → `verify_c1_incidence_squint`、`test_c6_no_duplication_penalty` → `test_c6_removed_no_duplication_penalty`——这些表达了意图。

**建议**: 进一步重命名为 `_c2_filter_with_theta_slack`、`_enforce_energy_memory_budgets` 等。

#### S7. `verify_c1_incidence_squint` 隐性契约（Speculative Generality）

`instance`、`t_actual`、`max_squint_deg` 为可选参数，缺前两者时 squint 检查静默跳过。squint 是文档化的 C1 子约束，调用方可能误以为 C1 squint 已验证。

**建议**: 在 `PerConstraintResult` 中加 `skipped_checks` 字段或在 `ViolationDetail` 中标记"未验证子约束"。

#### S8. `moea.py` Divergent Change

同一 diff 内为 5 个不同原因改动（C1–C4 重编号、RDR-004 重写、C6 删除、C7-squint 内联删除、seed=0 修复）。均属"对齐论文 §3"，边界模糊，但文件已承载多轴改动。

**建议**: 拆分 commit，至少把 RDR-004 和重编号分开。

#### S9. C1–C4 重编号本身

必要（对齐论文编号），跨文件 scatter 是编号变更的固有特性，非滥用。

## Spec 轴

### (a) 缺漏 / 部分

#### P1. Earth-radius 统一不完整 — 优先

目标 5 要求 `visibility.py`、`generate_all_scenarios.py`、`generate_s4_s6.py` 三文件统一用平均半径。

实际：高程/入射角几何已切到 `EARTH_RADIUS_MEAN_M`，但**轨道半长轴计算仍用赤道半径**：

- `generate_all_scenarios.py:62` — `semi_major_axis = (altitude_km*1000.0) + EARTH_EQUATORIAL_RADIUS`
- `generate_s4_s6.py:37` — 同上

**Spec 行**: 目标 5（项目上下文）。

**影响**: 轨道半径不一致会引入 ~10 km 量级误差（赤道-平均半径差约 21 km），传播到轨道周期、可见性窗口。

**建议**: 这两行也改为 `EARTH_RADIUS_MEAN_M`，或显式说明为何轨道半径用赤道值（如对齐 KeplerianElement 既有约定）。

#### P2. 验证器保留已删除的 resolution 约束 — 优先

`verify_c1_incidence_squint` 仍检查 `phi_abs < task.phi_min_res` 并标为 C1。

**Spec 行**: 论文 §3.3 C1 定义只有 "θ^min ≤ |θ_i| ≤ θ^max and |ψ_sq,i| ≤ ψ_sq^max"。resolution（旧 C2）已被删除并入 C1 的 θ^min 下界。

**建议**: 删除 `phi_min_res` 子检查，或合并到 `phi_min` 检查中（论文已说 φ_min 即由 resolution 推得）。

#### P3. 验证器用 φ 代理 θ

**Spec 行**: "θ^min ≤ |θ_i| ≤ θ^max"。

实际：`verify_c1_incidence_squint` 检查 `phi_abs`（off-nadir），不是 `theta`（incidence）。docstring 自承是 proxy。

**影响**: 1.5–5° 地球曲率修正未在验证器体现。faithfulness 缺口。

**建议**: 在验证器内调用 `off_nadir_to_incidence(phi, altitude)` 转换后再比较，或显式记录"使用 φ proxy，曲率修正误差 1.5–5°"。

#### P4. squint 验证条件化

`verify_c1_incidence_squint` 仅在 `instance with geom_cache and t_actual` 可用时检查 squint，否则"假设窗口生成已强制"。

**Spec 行**: "C1 ... are enforced during visibility-window generation"。

**判断**: faithful（spec 确实说 C1 在窗口生成时强制），但验证器不再是 C1 squint 的独立完整验证。

**建议**: 在 `VerificationReport` 中显式记录"squint 未独立验证，依赖上游窗口生成"。

### (b) 越界（Scope Creep）

#### P5. RDR-003 改动未在本轮目标内

`_b3_squint_minimize` 加了窗口约束 + φ-envelope mask（RDR-003），并新增 `test_b3_does_not_jump_windows`。

**Spec 行**: 本轮目标是 RDR-004，论文 §3.3 不涉及此项。

**判断**: 改动本身合理（修复真实 bug），但应单独 commit 并标注 RDR-003。

#### P6. seed=0 防御性处理

`seed or 1` → `seed if seed is not None else 1` 跨 6+ 文件，防 seed=0。

**Spec 行**: 未要求。

**判断**: 防御性合理（seed=0 是合法种子），但属隐性 bugfix，应在 commit message 中单独说明。

### (c) 实现已正确

#### ✓ RDR-004 gap-penalty 公式

`gap = t_b - (t_a + task_a.duration); if gap < tau_trans: g += (tau_trans - gap)/max(task_b.duration, 1.0)`

忠实实现 `t_{s_{k+1}} ≥ t_{s_k} + d_{s_k} + Δη_k/ω_max + τ_settle`，方向正确，跨 6 文件一致。

#### ✓ so_f1.py 和 baselines.py 仍 inline 检查 C2

so_f1.py 用 penalty 形式；baselines.py 用 `_enforce_c2_transitions` filter 形式——机制不同但都 inline 强制。

#### ✓ `_check_geometric_constraints` 接受 squint 参数

`visibility.py:169,191` 已使用 squint；两路径公式等价。

#### ✓ `test_c6_removed_no_duplication_penalty` 断言正确

`G[0,0] == 0` 对（spec 无 anti-duplication 约束；多星 C2 是 per-satellite）。但注释陈述过头（见 P7）。

### (d) 误导注释

#### P7. `test_c6_removed_no_duplication_penalty` 注释

注释称"单星 C2 隐含 unique assignment"。

**实际**: C2 只防时间重叠，不防同一目标被连续观测两次。

**建议**: 改为"C2 防止时间重叠；target 重复观测不被 spec 禁止，因此不惩罚"。

## 修复优先级

| # | 项目 | 类别 | 优先级 | 改动量 |
|---|------|------|--------|--------|
| P1 | Earth-radius 统一（轨道半长轴） | Spec 缺漏 | 高 | 2 行 |
| P2 | 删除验证器中 resolution 子检查 | Spec 缺漏 | 高 | ~10 行 |
| S1 | 抽 RDR-004 gap-penalty helper | Standards | 高 | ~30 行 |
| S2 | 抽 squint 计算 helper | Standards | 高 | ~20 行 |
| S3 | 重命名 `test_constraint_c4c5.py` | Standards | 中 | 文件名 |
| P7 | 修 `test_c6_removed` 注释 | Spec 误导 | 中 | 2 行 |
| S4 | 删除/重写 `test_c6_no_duplication_pass` | Standards | 中 | ~30 行 |
| P3 | 验证器用 θ 而非 φ | Spec 缺漏 | 中 | ~5 行 |
| P4 | 验证器标记 squint 未验证 | Spec 缺漏 | 低 | ~10 行 |
| S5 | 抽 `_resolve_seed()` | Standards | 低 | ~15 行 |
| S6 | 进一步重命名 | Standards | 低 | 可选 |
| P5/P6 | RDR-003 / seed=0 单独 commit | Spec 越界 | 低 | commit 拆分 |

## 总结

- **Standards 轴**: 0 硬违规，9 判断性建议；最严重为 RDR-004 gap-penalty 跨 6 处重复（应抽 helper）。
- **Spec 轴**: 4 缺漏 + 2 越界 + 1 误导注释；最严重为 Earth-radius 统一不完整（轨道半长轴仍用赤道半径）和验证器保留已删除的 resolution 约束。
- **已正确**: RDR-004 公式方向与一致性、C2 inline 检查、squint 公式等价性、文件放置与命名规范。

建议先修 P1、P2（2 行 + 10 行，立即闭环 spec 缺漏），再处理 S1、S2（消除重复）。

---

## 复审（2026-08-02，代码更新后）

代码再次更新（diff stat 从 2213/2170 行变 2225/2182 行，+12 行）。逐项复核如下。

### 已修复

**无**。上轮报告的全部优先项（P1、P2、S1、S2）均未落地。

### P1 升级（更严重）— P0 级

上轮 P1 是"轨道半长轴仍用赤道半径"。本轮在 `generate_s4_s6.py:55` 把 `R_e` 改成 `EARTH_RADIUS_MEAN_M`，但 `make_orbit` 中 `semi_major_axis = altitude + EARTH_EQUATORIAL_RADIUS` **未同步修改**（两文件均未改）。

后果：

```python
# generate_s4_s6.py
R_e = EARTH_RADIUS_MEAN_M              # 6,371,000 m
h = (orbit_elements.semi_major_axis - R_e)
# orbit_elements.semi_major_axis = altitude + EARTH_EQUATORIAL_RADIUS
#                                  = altitude + 6,378,137
# → h = altitude + 6,378,137 - 6,371,000 = altitude + 7,137
# 即 h 比真实 altitude 多算 7,137 m（约 7 km）
```

**之前是"统一用赤道半径"（自洽但与目标 5 不符），现在是"轨道用赤道、反推 h 用平均"（不自洽，引入 7 km 误差）**。这比上轮报告的 ~21 km 量级估算更精确——实际误差是赤道-平均半径差 7,137 m。

传播影响：`ratio = R_e / (R_e + h)` → 测绘带半宽计算；`altitude_km = h / 1000.0` → 下游所有高度相关计算。

**修复**: `generate_all_scenarios.py:62` 和 `generate_s4_s6.py:37` 的 `make_orbit` 中 `semi_major_axis = altitude + EARTH_EQUATORIAL_RADIUS` 改为 `EARTH_RADIUS_MEAN_M`。

### 未修复（与上轮相同）

| # | 状态 | 备注 |
|---|------|------|
| P2 | 未改 | `verify_c1_incidence_squint` 仍检查 `phi_min_res` 并标 C1 |
| P3 | 未改 | 验证器仍用 φ 代理 θ |
| P4 | 未改 | squint 验证仍条件化 |
| S1 | 未改 | RDR-004 gap-penalty 仍 6 处重复 |
| S2 | 未改 | squint 计算仍 3 处重复 |
| S3 | 未改 | `test_constraint_c4c5.py` 文件名未改 |
| S4 | 未改 | `test_c6_no_duplication_pass` 仍存在 |
| S5 | 未改 | seed 解析仍重复 |
| S6 | 未改 | 部分重命名仍不透明 |
| S7 | 未改 | 验证器隐性契约仍在 |

### 新增问题

#### P6-ext. seed=0 防御扩散

`generate_all_scenarios.py:472` 新增 `s5_base_seed or seed` → `s5_base_seed if s5_base_seed is not None else seed`。

这是 P6（seed=0 防御）从 solver 层扩散到 scenario 生成层。改动本身合理，但 P6 的越界范围扩大。

### 已正确（与上轮一致）

- RDR-004 公式方向与跨文件一致性 ✓
- C2 inline 检查 ✓
- squint 公式等价性 ✓
- 文件放置与命名规范 ✓

### 测试验证

本轮改动直接相关的测试全部通过：

```
src/tests/test_constraint_c4c5.py
src/tests/test_moea_multisat.py
src/tests/test_b3_squint_min.py
src/tests/test_baselines_posthoc.py
src/tests/test_phase8.py
→ 31 passed
```

其他测试失败（44 项）均为场景 pkl 文件缺失（`experiments/scenarios/S1` 等目录为空），与本轮代码改动无关，属测试环境问题。

### 复审结论

**P1 升级为 P0**：Earth-radius 不一致现在导致 7 km 量级误差（赤道-平均半径差），传播到测绘带、高度、轨道周期。必须立即修复 `make_orbit` 中 `semi_major_axis` 计算。

其他优先项（P2、S1、S2）未落地，建议按上轮修复优先级表执行。测试通过率对本轮改动相关项 100%，无回归。
