# Code Review — 第五轮深挖（post-hoc repair 不对称 + 命名陈旧 + docstring 残留）

- **作者**: trae
- **日期**: 2026-08-02
- **前序报告**: [round1](code-review-20260802-constraint-refactor-trae.md)、[round3](code-review-20260802-round3-trae.md)、[round4](code-review-20260802-round4-trae.md)
- **审查重点**: so_f1.py post-hoc repair 逻辑、baselines.py `_enforce_c2_transitions` 与 RDR-004 一致性、测试命名陈旧、constraints.py docstring 残留

## 本轮发现

### R5-P0 — so_f1.py post-hoc repair 与 moea.py post-hoc filter 策略不对称（Spec — 中）

#### 问题陈述

两个 solver 在 post-hoc ConstraintVerifier 发现 infeasible 解时采用**不同策略**：

| Solver | post-hoc 策略 | 代码位置 |
|---|---|---|
| moea.py | **filter out**：丢弃整个 infeasible 解，frontier 缩小 | [moea.py:L623-L635](file:///d:/hermes/my-workspace/projects/planning%20paper/src/sar_sim/solver/moea.py#L623-L635) |
| so_f1.py | **repair via delay**：调用 `_enforce_c2_transitions` 尝试 delay 修复，重算 f1/f2/f3 | [so_f1.py:L595-L636](file:///d:/hermes/my-workspace/projects/planning%20paper/src/sar_sim/solver/so_f1.py#L595-L636) |

#### 评估

**不是 bug**。两种策略对不同 solver 类型是合理的：
- MOEA 是多目标优化，frontier 有多个解，丢弃 infeasible 解后仍有足够样本。
- GA-P 是单目标优化，只有一个最优解，丢弃等于无解；repair（delay + 重算）是唯一合理选择。

**但是**，这种不对称是**隐式设计**，没有在代码注释或论文中说明。审稿人若对比 moea.py 和 so_f1.py 的 post-hoc 逻辑，会困惑为什么策略不同。

**建议**：在 [so_f1.py:L583](file:///d:/hermes/my-workspace/projects/planning%20paper/src/sar_sim/solver/so_f1.py#L583) 的 `# Post-hoc constraint verification (with t_actual for C2)` 注释后加一行：
```python
# Post-hoc constraint verification (with t_actual for C2).
# Unlike MOEA (which filters out infeasible frontier solutions), GA-P is
# single-objective with one best solution — we repair via delay-repair
# (_enforce_c2_transitions) and recompute f1/f2/f3, rather than discard.
```

### R5-P1 — so_f1.py repair 后 `sel`/`phis`/`t_acts` 局部变量未更新（Standards — 低，当前无 bug）

#### 问题陈述

[so_f1.py:L595-L636](file:///d:/hermes/my-workspace/projects/planning%20paper/src/sar_sim/solver/so_f1.py#L595-L636) 的 repair 块更新了 `schedule`、`f1`、`f2_posthoc`、`f3_posthoc`、`meta`，但**未更新**局部变量 `sel`、`phis`、`t_acts`。

#### 评估

**当前无 bug**：return 语句 [L640-L644](file:///d:/hermes/my-workspace/projects/planning%20paper/src/sar_sim/solver/so_f1.py#L640-L644) 只用 `schedule`、`f1`、`meta`，不用 `sel`/`phis`/`t_acts`。

**风险**：若未来有人在 return 前加代码使用 `sel` 或 `phis`（比如 logging 或 debug），会用到 repair 前的旧值。

**建议**（低优先）：在 repair 块末尾加：
```python
# Note: sel/phis/t_acts are NOT updated after repair; downstream must
# use schedule + meta, not these locals.
```

### R5-P2 — 测试文件名/函数名仍含旧约束编号（Standards — 低）

前轮 S3 只记录了 `test_constraint_c4c5.py` 文件名。本轮 grep 发现**四处**陈旧命名：

| 文件 | 行 | 陈旧标识 | 应改为 |
|---|---|---|---|
| `test_constraint_c4c5.py` | 文件名 | `c4c5` | `test_constraint_c3c4.py` |
| `test_moea_multisat.py` | [L506](file:///d:/hermes/my-workspace/projects/planning%20paper/src/tests/test_moea_multisat.py#L506) | `def test_per_sat_c4c5_budget()` | `test_per_sat_c3c4_budget()` |
| `test_moea_perf.py` | [L66](file:///d:/hermes/my-workspace/projects/planning%20paper/src/tests/test_moea_perf.py#L66) | `def test_o3_c4c5_vectorized_unchanged()` | `test_o3_c3c4_vectorized_unchanged()` |
| `test_moea_multisat.py` | [L276](file:///d:/hermes/my-workspace/projects/planning%20paper/src/tests/test_moea_multisat.py#L276) | `def test_c6_no_duplication_pass()` | 前轮 S4 已记（死测试），应删除或重命名 |

**修复**：重命名文件 + 函数名（grep 全局替换引用）。约 10 行改动。

### R5-P3 — constraints.py docstring 仍写 "C3 check"（Standards — 低）

[constraints.py:L253](file:///d:/hermes/my-workspace/projects/planning%20paper/src/sar_sim/verification/constraints.py#L253) 和 [L262](file:///d:/hermes/my-workspace/projects/planning%20paper/src/sar_sim/verification/constraints.py#L262) 的 `verify_c2_transition` docstring 仍写：

- L253: `own C3 evaluation. Without t_actual, falls back to t_earliest`
- L262: `instance: optional AgileSARInstance for full 3-axis C3 check`

应改为 `C2 evaluation` 和 `C2 check`。2 行改动。

### R5-P4 — `_b3_squint_minimize` mask 用 phi 空间而非 incidence 空间（Spec — 低，数学等价）

#### 问题陈述

[baselines.py:L750-L760](file:///d:/hermes/my-workspace/projects/planning%20paper/src/sar_sim/solver/baselines.py#L750-L760) 的 `_b3_squint_minimize` 中，RDR-003 修复的 mask 用 `instance.phi_min`/`phi_max`（off-nadir 空间）：

```python
phi_min = instance.phi_min
phi_max = instance.phi_max
mask &= (np.abs(arr[:, 1]) >= phi_min) & (np.abs(arr[:, 1]) <= phi_max)
```

但 paper §3 C1 是 **incidence 空间**（θ^min ≤ |θ_i| ≤ θ^max）。

#### 评估

**数学等价**：phi 和 incidence 单调相关（`sin(θ) = (R_e+h)/R_e · sin(φ)`），所以 phi 空间的 mask 等价于 incidence 空间的 mask。无当前 bug。

**faithfulness 缺口**：paper §3 说 C1 是 incidence 空间，代码在 phi 空间做 mask。若审稿人逐行对比，会注意到这个口径差异。

**建议**（低优先）：在 [baselines.py:L755](file:///d:/hermes/my-workspace/projects/planning%20paper/src/sar_sim/solver/baselines.py#L755) 加注释：
```python
# C1 is formally on incidence θ (paper §3), but φ↔θ is monotonic, so
# masking in φ-space is equivalent. Using φ here avoids an extra
# off_nadir_to_incidence() call per sample point.
```

### R5-P5（已验证正确）— `_enforce_c2_transitions` 的 delay-repair 逻辑与 RDR-004 不冲突

#### 验证

`_enforce_c2_transitions`（[baselines.py:L150-L203](file:///d:/hermes/my-workspace/projects/planning%20paper/src/sar_sim/solver/baselines.py#L150-L203)）的行为：
1. 检查 decoded-time gap（L178-L180）
2. 如果 gap 够，保留
3. 如果 gap 不够，**尝试 delay curr**（L184-L200）
4. delay 后可行 → 保留 delayed 版本；不可行 → 丢弃

**与 RDR-004 不冲突**：
- RDR-004 是关于 MOEA `_evaluate` 中的 **penalty 计算**（不再 waive）。
- `_enforce_c2_transitions` 是 baseline 的 **greedy filter + delay-repair**，不是 penalty。
- delay-repair 后的 observation 确实是 C2-feasible 的（gap 够了），报告的 metric 是 feasible timing。
- 这与 RDR-004 修复前的"waive"不同——waive 是不罚但保留 infeasible timing；delay-repair 是改 timing 使其 feasible。

**结论**：`_enforce_c2_transitions` 不需要改成 RDR-004 风格。它已经是正确的 filter + repair 逻辑。✓

### R5-P6（已验证正确）— so_f1.py repair 后 f2/f3 重算与主 moea.py 公式一致

[so_f1.py:L617-L618](file:///d:/hermes/my-workspace/projects/planning%20paper/src/sar_sim/solver/so_f1.py#L617-L618)：
```python
f2_num += math.sin(geom.theta) * geom.cos_psi
f3_num += (math.cos(geom.theta) ** 3) * (geom.cos_psi ** 3)
```

对比 [moea.py:L181-L182](file:///d:/hermes/my-workspace/projects/planning%20paper/src/sar_sim/solver/moea.py#L181-L182)：
```python
f2_num += math.sin(theta_i) * cos_psi_i
f3_num += (math.cos(theta_i) ** 3) * (cos_psi_i ** 3)
```

公式一致。`geom.cos_psi` 等价于 `math.cos(geom.psi_sq)`。✓

## 本轮总体结论

### 已验证正确（2 项）
R5-P5（`_enforce_c2_transitions` delay-repair 与 RDR-004 不冲突）、R5-P6（so_f1 repair 后 f2/f3 公式一致）。

### 新问题（4 项，全部低-中优先）

| # | 级别 | 影响范围 | 修复量 |
|---|---|---|---|
| R5-P0 | 中（Spec 注释） | post-hoc 策略不对称未说明 | 3 行注释 |
| R5-P1 | 低（fragile） | sel/phis/t_acts 未更新 | 2 行注释 |
| R5-P2 | 低（命名） | 4 处陈旧命名 | ~10 行重命名 |
| R5-P3 | 低（docstring） | 2 处 "C3" 应为 "C2" | 2 行 |
| R5-P4 | 低（注释） | phi vs incidence 口径 | 3 行注释 |

### 与前序报告对比

- **R4-P0**（消融 C1 inline 不一致）仍是当前**最高优先**未修问题。
- **N3**（post-hoc `n_frontier_points` 口径）仍是高风险。
- 本轮新发现全部是**低-中优先**的注释/命名/docstring 问题，无新的功能 bug。

### 下一步优先级（累计）

1. **R4-P0**（高）— 消融脚本删 ~27 行 inline C1 检查
2. **N3**（高）— post-hoc `n_frontier_points` 字段重命名 + 数据口径决策
3. **R5-P0**（中）— so_f1.py post-hoc repair 策略说明注释
4. **R5-P2**（低）— 测试文件名/函数名重命名
5. **R5-P3**（低）— constraints.py docstring 修 "C3"→"C2"
6. **R5-P1/R5-P4**（低）— 注释加固
7. S1-S7、N1、N5（低优先，长期挂起）

## 第五轮总结

本轮深挖了 so_f1.py 的 post-hoc repair 逻辑（前轮只看了 moea.py 的 filter 逻辑），发现 moea（filter）和 so_f1（repair via delay）的策略不对称是合理设计但未注释。`_enforce_c2_transitions` 的 delay-repair 与 RDR-004 不冲突（RDR-004 是 penalty 计算，不是 filter/repair）。测试命名有 4 处陈旧。constraints.py docstring 有 2 处 "C3" 残留。`_b3_squint_minimize` 的 phi-space mask 数学等价但注释可加固。

**本轮无新的功能 bug**。所有发现都是注释/命名/docstring 层面的改进。代码功能正确性在第四轮已验证的核心点上保持。
