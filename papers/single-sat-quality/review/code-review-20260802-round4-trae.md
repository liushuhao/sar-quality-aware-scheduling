# Code Review — 第四轮深挖（消融 vs 基线一致性）

- **作者**: trae
- **日期**: 2026-08-02
- **前序报告**: [code-review-20260802-constraint-refactor-trae.md](code-review-20260802-constraint-refactor-trae.md)（初评+复审）、[code-review-20260802-round3-trae.md](code-review-20260802-round3-trae.md)（第三轮）
- **审查重点**: 消融脚本与基线 solver 的 `_evaluate` 约束一致性、验证器接口匹配、φ↔θ 双函数一致性、post-hoc 过滤正确性

## 本轮发现

### R4-P0 — 消融脚本与基线 solver 的 C1 inline penalty **不一致**（Spec — 高）

#### 问题陈述

主求解器和 solver_factory 已按 paper §3 的约束分层设计（C1 在窗口生成阶段强制，求解 `_evaluate` 中**不再**重复 inline C1 检查），但三个消融脚本（`run_moea_3obj_no_incidence.py`、`run_moea_3obj_no_squint.py`、`run_moea_3obj_no_physics.py`）**仍然保留了四层冗余的 C1 inline penalty**：

| 检查项 | 主 SARSchedulingProblem | solver_factory | 消融 no_incidence | 消融 no_squint | 消融 no_physics |
|---|---|---|---|---|---|
| phi_min / phi_max | ❌ 不检查 | ❌ 不检查 | ✅ `phi_abs_val < task.phi_min` 罚 | ✅ 同左 | ✅ 同左 |
| phi_min_res（已删 resolution）| ❌ 不检查 | ❌ 不检查 | ✅ `phi_abs_val < task.phi_min_res` 罚 | ✅ 同左 | ✅ 同左 |
| squint ≤ 45°（inline）| ❌ 不检查 | ❌ 不检查 | ✅ `squint_dict[i] > MAX_SQUINT_RAD` 罚 | ✅ 同左 | ✅ 同左 |
| window τ 区间 | ✅ 检查 | ✅ 检查 | ✅ 检查 | ✅ 检查 | ✅ 检查 |
| C2 transition RDR-004 | ✅ 检查 | ✅ 检查 | ✅ 检查 | ✅ 检查 | ✅ 检查 |
| C3/C4 energy/memory | ✅ 检查 | ✅ 检查 | ✅ 检查 | ✅ 检查 | ✅ 检查 |
| post-hoc ConstraintVerifier | ✅ 有（moea.py L623-635）| 无（single-obj 不用）| ✅ 有（L205-213）| ✅ 有（L316-323）| ✅ 有（L214-221）|

主 moea.py 的设计理由写在注释里（[moea.py:L187-L191](file:///d:/hermes/my-workspace/projects/planning%20paper/src/sar_sim/solver/moea.py#L187-L191)）：
> C1 (incidence + squint) is already enforced at window-generation time, so no inline geometry check is needed here.

消融脚本的 `_evaluate` **既**在 inline 罚了三层 C1（phi 范围、phi_min_res、squint），**又**在 post-hoc 用 ConstraintVerifier 验证 C1。双重惩罚。

#### 具体定位

- [run_moea_3obj_no_incidence.py:L103-L119](file:///d:/hermes/my-workspace/projects/planning%20paper/papers/single-sat-quality/experiments/run_moea_3obj_no_incidence.py#L103-L119) — phi_min/max、phi_min_res、squint 三层检查
- [run_moea_3obj_no_squint.py:L143-L173](file:///d:/hermes/my-workspace/projects/planning%20paper/papers/single-sat-quality/experiments/run_moea_3obj_no_squint.py#L143-L173) — 同上，注释仍是 "C3: transition feasibility"（旧编号）
- [run_moea_3obj_no_physics.py:L111-L128](file:///d:/hermes/my-workspace/projects/planning%20paper/papers/single-sat-quality/experiments/run_moea_3obj_no_physics.py#L111-L128) — 同上

#### 后果

1. **消融 delta 归因不可信**：消融 → 基线的 f2/f3 下降可能部分来自消融脚本过约束导致解集更小，不全是 objective function 中 incidence/squint/physics 项缺失导致。审稿人若复现实验（用主 solver 中相同 C1 分层设计做消融），会得到不一致的 delta。
2. **双重惩罚**：inline G 加上 post-hoc 过滤，可行解的搜索空间被过度压缩。如果某消融报告的 `n_infeasible_filtered` 远小于基线，可能是 inline 约束把大部分解限制为可行，而不是算法本身的效果。
3. **phi_min_res 已是废约束**：paper §3 合并 resolution 到 θ^min，在窗口生成的 incidence_min 中体现。消融脚本还在 `_evaluate` 中用 phi 空间检查 `phi_abs_val < phi_min_res`——这是**双重且错误口径**的检查（应该是 incidence 空间检查，不是 phi 空间；且应该在 window-stage，不是 evaluate-stage）。

#### 修复

三个消融脚本的 `_evaluate` 应与主 moea.py SARSchedulingProblem._evaluate **完全对齐**：

删除以下 inline 检查块（三脚本各约 9 行）：
```python
# 删：phi_min / phi_max（C1 冗余）
if phi_abs_val < task.phi_min: g += task.phi_min - phi_abs_val
if phi_abs_val > task.phi_max: g += phi_abs_val - task.phi_max
# 删：phi_min_res（已合并入 θ^min）
if phi_abs_val < task.phi_min_res: g += task.phi_min_res - phi_abs_val
# 删：squint ≤ 45°（C1 冗余）
if squint_dict[i] > MAX_SQUINT_RAD: g += squint_dict[i] - MAX_SQUINT_RAD
```

保留：window τ 区间检查 + C2 RDR-004 + C3/C4。

删除后，消融/基线的 G penalty 结构完全一致，只有 f2/f3 的计算不同——这才是消融设计的本意。

**额外建议**：三个消融脚本的 no_physics/no_incidence/no_squint 命名含义是"修改目标函数中的物理项"，不是"修改约束集"。若约束集不同，消融脚本的 docstring 应明确写"同时移除 C1 inline 检查，与主 solver 一致"——否则 reviewers 会怀疑设计是否有意为之。

### R4-P1 — 消融脚本 `_evaluate` 仍引用旧约束编号（Standards — 低）

- [run_moea_3obj_no_squint.py:L175](file:///d:/hermes/my-workspace/projects/planning%20paper/papers/single-sat-quality/experiments/run_moea_3obj_no_squint.py#L175) 注释写 `# C3: transition feasibility`——应为 `# C2`。
- [run_moea_3obj_no_incidence.py:L122](file:///d:/hermes/my-workspace/projects/planning%20paper/papers/single-sat-quality/experiments/run_moea_3obj_no_incidence.py#L122) 和 [no_physics.py:L131](file:///d:/hermes/my-workspace/projects/planning%20paper/papers/single-sat-quality/experiments/run_moea_3obj_no_physics.py#L131) 未写注释但位置与 moea.py 对齐，正确。不影响运行。

### R4-P2 — no_squint 消融脚本的 C1 squint inline 检查名不副实（Spec — 低，依赖 P0 修复）

`no_squint.py` 标题："Variant B: NO SQUINT (squint component removed from f2/f3)."

正确做法：f2/f3 中不乘 cos(ψ_sq)（已实现），但 **constraint 层 squint 仍应在窗口阶段强制（已做），`_evaluate` 中**不再**额外 squint 罚**（若 R4-P0 修复则自动一致）。

当前 no_squint 额外罚了 squint。虽然这和"消融 objective 中的 squint 项"不矛盾，但与主 solver 设计不一致——如果 R4-P0 修复，这个点就自动关闭。

### R4-P3（低优先）— 两个 φ↔θ 转换函数只有一个下划线差异，极易混淆（Standards）

| 函数 | 签名 | 输入单位 | 输出单位 | 所在模块 | 可见性 |
|---|---|---|---|---|---|
| `_off_nadir_to_incidence(off_nadir_deg, sat_altitude_m)` | degrees → degrees | degrees | degrees | [visibility.py:L48-L75](file:///d:/hermes/my-workspace/projects/planning%20paper/src/sar_sim/generator/visibility.py#L48-L75) | private（_前缀） |
| `off_nadir_to_incidence(phi_rad, altitude_m)` | radians → radians | radians | radians | [nesz.py:L77-L102](file:///d:/hermes/my-workspace/projects/planning%20paper/src/sar_sim/metrics/nesz.py#L77-L102) | public |

两个函数**数学完全等价**（`sin(θ) = (R_e+h)/R_e · sin(φ)`），没有当前 bug。但：
- 命名差一个 `_`，参数名、顺序、单位完全不同，未来很容易被误用（比如把 visibility.py 调用换成 nesz.py 版本但忘记单位转换，反之亦然）。
- 两个函数分别存在 visibility.py（窗口生成阶段，degrees 世界）和 nesz.py（metric 阶段，radians 世界），分工合理但缺乏注释说明。

**建议**（低优先）：
- 在 `visibility.py` 的 `_off_nadir_to_incidence` docstring 中加一条："This is the degrees-world twin of sar_sim.metrics.nesz.off_nadir_to_incidence; the two are mathematically identical but operate in different angular-unit regimes."
- 或者让 visibility.py 的 private 版本直接调用 nesz.py 的 public 版本 + deg/rad 转换，消除数学重复。当前不算 bug，可放低优先。

### R4-P4（已验证正确）— post-hoc ConstraintVerifier frontier 过滤与 x_source 对齐

**结论：正确。**

- moea.py L458: `decode_solution` 返回 per-selected `phis`（长度 = len(selected)）。
- moea.py L459-L462: `solutions_to_frontier` 把 per-selected phis 和 t_acts 放进 dict。
- constraints.py L598: `verify_frontier` 检测到 `len(phis) == len(selected) < N`，自动重建 full-N phi_full（unselected 填 0，不影响因为只迭代 selected_indices）。✓
- moea.py L627-633: `feasible_indices = [i for i, (_, rpt) in enumerate(verified) if rpt.overall_pass]`，顺序与 frontier 和 `x_source` 完全一一对应（frontier 来自 X_pop 行顺序，verified 是 frontier 的顺序映射）。✓

没有错位。

### R4-P5（已验证正确）— 导入链无循环依赖

`moea.py` 和 `so_f1.py` 直接 import `sar_sim.verification.constraints.ConstraintVerifier`，不经过 `__init__.py`。实测 `python -c "from sar_sim.solver.moea import moea_solver; from sar_sim.solver.so_f1 import b2_profit_solver_bl_seeded"` 通过，无循环。

### R4-P6（已验证正确）— 两 φ↔θ 函数数学等价性

- visibility.py: `sin_incidence = (R_e+h)/R_e · sin(radians(off_nadir_deg)); return degrees(arcsin(sin_incidence))`
- nesz.py: `factor = (R_e+h)/R_e; return arcsin(factor · sin(phi_rad))`

完全等价。没有 C1 过滤偏差。

### R4-P7（已验证正确）— RDR-004 在 7 处一致

- moea.py: 单星 + 多星分支（×2）
- so_f1.py: B2ProfitProblem（×1）
- solver_factory.py: ConstraintFreeSARSchedulingProblem（×1）
- 三个消融脚本各 1 处（×3）

全部使用：`gap = t_b - (t_a + task_a.duration); if gap < tau_trans: g += (tau_trans - gap) / max(task_b.duration, 1.0)`，方向正确，符号一致，分母一致。✓

### R4-P8（已验证正确）— no_physics 消融的 f2/f3 count-only 与注释一致

no_physics.py L79-80: `f2_num = zeros(n_pop)  # VARIANT: count only`；L98-99: `f2_num[p] += 1.0; f3_num[p] += 1.0`。除以 n_sel 后，f2 = f3 = n_selected / n_selected = 1（总是 1）。正确，不需要 incidence/theta/phi 数据，所以 no_physics 不记录几何也合理——但为了约束检查仍存 phi_dict/squint_dict（L101-109 注释已说明），这是合理设计。✓

## 本轮总体结论

### 已验证正确（6 项）
R4-P4（frontier/x_source 对齐）、R4-P5（无循环导入）、R4-P6（φ↔θ 数学等价）、R4-P7（RDR-004 一致性）、R4-P8（no_physics count-only）+ 之前已验证的 C1 incidence/squint 窗口检查（L164-193 `_check_geometric_constraints` 接受 squint 参数）。

### 新问题（4 项）

| # | 级别 | 影响范围 | 修复量 |
|---|---|---|---|
| R4-P0 | 高（Spec） | 消融实验 delta 归因不可信 | 三脚本各删 9 行 ≈ 27 行 |
| R4-P1 | 低（注释） | 无功能影响 | 1 行注释 |
| R4-P2 | 低（依赖 P0） | no_squint 命名与实现轻微脱节 | 随 P0 自动关闭 |
| R4-P3 | 低（可维护性） | 无当前 bug，未来风险 | 2 行 docstring 或 1 行 wrapper |

### 必须立即修
**R4-P0**。这是本轮最重要发现：三个消融脚本的 G penalty 结构与基线 solver 不一致，导致消融结果的 baseline vs. 消融 delta 不能干净归因于 objective function 中 incidence/squint/physics 项的变化。如果不修复，当前已跑的消融实验结果（`baselines_200.json` 已重跑，但消融结果可能是旧的？或者还没跑？需要确认消融实验数据是否还没重新生成）——若还没重跑，先修代码再跑；若已重跑用的是不一致脚本，结果要么重跑要么在 RDR 中记录"消融脚本使用了更严格的 inline C1 约束"。

## 与前序报告对比

- P0（Earth-radius）、P1（resolution）、P2（φ→θ 转换）、N2（OP-1/误判更正）、N4（h_sat_m）已在第三轮闭环。
- N3（post-hoc 口径问题）仍是高风险，本报告不变。
- 新增 R4-P0（消融 C1 不一致）是本轮唯一新的 P0 级问题。
- N1（循环依赖注释）、N5（so_f1 单解验证）、S1-S7 等低优先问题本轮未进展，仍挂起。

**下一步优先级**：
1. 修 R4-P0（三脚本删 ~27 行 inline C1 检查）
2. 决策 N3（post-hoc `n_frontier_points` 重命名）
3. （可选）修 R4-P1/P2/P3、N1/N5 + S1-S7（低优先，30min 内可做完）
