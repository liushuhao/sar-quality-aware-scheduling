# Code Review — 第三轮复审（C1–C4 重构后）

- **作者**: trae
- **日期**: 2026-08-02
- **审查范围**: 工作树 vs `HEAD`（`8b2120a`），20 个文件未提交
- **前序报告**: [code-review-20260802-constraint-refactor-trae.md](code-review-20260802-constraint-refactor-trae.md)（初评 + 复审）
- **测试**: 本轮改动相关 32 passed / 6 failed（pkl 场景文件缺失，环境问题，非回归）

## 本轮新增改动

代码从 2225/2182 行增至 2282/2204 行（+57/+22）。新增动作：

1. **`generate_s4_s6.py:55-60`** 改写 `R_e` 处理：`semi_major_axis` 仍用赤道半径反推 h，但测绘带 `ratio` 改用 `R_mean`。
2. **`constraints.py` 重写 `verify_c1_incidence_squint`**：调用 `off_nadir_to_incidence(phi, altitude)` 真正转 θ 后比较；删除 `phi_min_res` 子检查；docstring 显式声明 resolution 已并入 θ^min。
3. **`moea.py` 新增 post-hoc `ConstraintVerifier` 过滤**：求解后过滤不可行解，`meta["n_infeasible_filtered"]` 记录数量。
4. **`so_f1.py` 新增 post-hoc `ConstraintVerifier`**：`meta["constraint_feasible"]` + `meta["n_constraints_failed"]`。
5. **moea.py / so_f1.py 遗传算子显式化**：`SBX eta 15→20`、`PM prob 1/(2N)→0.1`。

## 逐项复核

### P0（上轮升级）— Earth-radius — **已修复 ✓**

`generate_s4_s6.py:55-60` 现在的写法：

```python
# Reverse-compute altitude from semi_major_axis using the same radius
# as make_orbit (equatorial), then use mean radius for φ↔θ conversion.
h = orbit_elements.semi_major_axis - EARTH_EQUATORIAL_RADIUS
altitude_km = h / 1000.0
R_mean = EARTH_RADIUS_MEAN_M
ratio = R_mean / (R_mean + h)
```

**正确性验证**:

- `make_orbit`: `semi_major_axis = altitude + EARTH_EQUATORIAL_RADIUS`（赤道）
- `generate_s4_s6.py:56`: `h = semi_major_axis - EARTH_EQUATORIAL_RADIUS`（赤道反推，与 make_orbit 自洽）✓
- `generate_s4_s6.py:60`: `ratio = R_mean / (R_mean + h)`（平均半径，与 nesz.py / visibility.py 一致）✓
- `compute_batch_visibility` 中 `h_sat_m = altitude_km * 1000.0`（函数入参，不反推）✓

无 7 km 量级误差，无口径不一致。**P0 闭环。**

**残留语义建议**（低优先）：`make_orbit` 用赤道半径算 `semi_major_axis` 是 KeplerianElement 既有约定，与 φ↔θ 转换用平均半径是不同物理量。建议在 `reference/sar-domain-knowledge.md` 或 ADR 中显式记录此约定，避免下次再混淆。

### P1（旧 P2）— 验证器保留已删除 resolution 约束 — **已修复 ✓**

`verify_c1_incidence_squint` 删除了 `phi_min_res` 子检查。docstring 新增："Note: the resolution sub-constraint has been merged into θ^min per the latest paper revision"。

### P2（旧 P3）— 验证器用 φ 代理 θ — **已修复 ✓**

```python
theta = off_nadir_to_incidence(phi_abs, altitude_m)
theta_min = off_nadir_to_incidence(task.phi_min, altitude_m)
theta_max = off_nadir_to_incidence(task.phi_max, altitude_m)
if theta < theta_min: ...
if theta > theta_max: ...
```

真正在 θ 空间比较，faithfulness 缺口消除。`altitude_m` 从 `instance.altitude_m` 获取，缺 instance 时 fallback 到 600_000.0 m（应改为 raise 或显式标注）。

### P3（旧 P4）— squint 验证条件化 — **未改**

`verify_c1_incidence_squint` 仍仅在 `instance.geom_cache + t_actual` 可用时检查 squint。建议在 `VerificationReport` 中显式记录 squint 未独立验证。

### S1 — RDR-004 gap-penalty 重复 — **未改**

6 处 4 行重复代码仍在（moea.py ×2、so_f1.py、solver_factory.py、3 个消融脚本）。未抽 helper。

### S2 — squint 计算重复 — **未改**

3 处 4 行重复（generate_all_scenarios.py、generate_s4_s6.py、visibility.py）。

### S3 — `test_constraint_c4c5.py` 文件名 — **未改**

### S4 — `test_c6_no_duplication_pass` 死测试 — **未改**

### S5 — seed 解析重复 — **未改**

### S6 — 部分重命名不透明 — **未改**

### S7 — 验证器隐性契约 — **未改**

### P5 — RDR-003 越界 — **未改**（仍混在本轮 diff 中）

### P6 — seed=0 防御 — **未改**（已扩散到 generate_all_scenarios.py:472）

## 本轮新发现问题

### N1. post-hoc ConstraintVerifier 引入循环依赖风险（Standards）— 中

`so_f1.py:41` 新增 `from sar_sim.verification.constraints import ConstraintVerifier`。

`verification/constraints.py` 已 import `solver.types`。若 `solver.types` 反过来 import `solver.something` 再 import `so_f1`，会形成循环。

实际检查：`verification/constraints.py` 只 import `solver.types`，不 import `solver.so_f1` 或 `solver.moea`，所以当前无循环。但这是脆弱依赖，建议在 `verification/__init__.py` 或 `constraints.py` 顶部加 `# noqa: avoid circular import — solver modules import this for post-hoc verification` 注释，或在架构文档中说明。

### N2. 遗传算子参数变更涉及 OP-1（Spec）— **已闭环 ✓（误判更正）**

moea.py 新增显式 `SBX(prob=0.9, eta=20)` + `PM(prob=0.1, eta=20)`；so_f1.py `ga_hotstart_solver` 把 `SBX eta 15→20`、`PM prob 1/(2N)→0.1`。

**误判更正（2026-08-02）**：初稿 N2 称"论文 §5.1 仍是 ηc=15 / pm=1(2N)，偏差扩大"。经直接 grep [small-paper-ijae.tex:L529-L531](file:///d:/hermes/my-workspace/projects/planning%20paper/papers/single-sat-quality/small-paper-ijae.tex#L529-L531)，论文原文：

> The GA runs for 200 generations with simulated binary crossover ($p_c = 0.9$, $\eta_c = 20$) and polynomial mutation ($p_m = 0.1$, $\eta_m = 20$).

论文**一直写的是** ηc=20 / pm=0.1。本轮代码改动是**代码向论文对齐**（so_f1 旧代码 ηc=15 / pm=1(2N) → 论文值；moea 从 pymoo 默认隐式值 → 论文显式值）。**偏差消除了，不是扩大。OP-1 项代码侧已闭环。**

**残留**：REVIEW_INDEX.md 的 OP-1 描述仍写"路径 A：改论文描述匹配代码"——这是基于旧假设。应更新为"代码已匹配论文，OP-1 关闭"或类似。

### N3. post-hoc 过滤可能改变已报告数据（Spec）— 高

moea.py 在求解后用 `ConstraintVerifier` 过滤不可行解，并把过滤后的 frontier 用于后续 knee 选择和 meta；so_f1.py 把 `constraint_feasible` 写入 meta。

影响：

- 之前 `n_frontier_points` 是原始前沿点数；现在 `frontier` 已过滤，`n_frontier_points` 是过滤后点数，`n_infeasible_filtered` 单独记录被过滤数。
- 所有依赖 `n_frontier_points` 的下游分析（box plot、SD、统计检验）的口径都变了。
- 之前 baselines_200.json、消融结果等已提交数据是**未过滤**口径；本轮重跑会是**过滤后**口径。两批数据不可直接混合。

**建议**: 在重跑前明确：（a）所有报告表格统一用过滤后口径；（b）`n_frontier_points` 字段重命名为 `n_frontier_feasible`，或在 meta 中同时保留 `n_frontier_raw` 和 `n_frontier_feasible`。当前 meta 只有 `n_frontier_points` + `n_infeasible_filtered`，可推算 raw 但字段名误导。

### N4. `compute_batch_visibility` 中 `h_sat_m` 来源（Spec）— **已验证 ✓**

经 grep 确认：`h_sat_m = altitude_km * 1000.0`，是函数入参传入的标称高度，**不**从 `orbit.semi_major_axis` 反推。与 `make_orbit` 自洽，无 7 km 误差。本项闭环。

### N5. so_f1.py post-hoc 检查只验证单解，不验证 frontier（Spec）— 中

moea.py 过滤整个 frontier；so_f1.py 只检查 knee 单解。对单目标 GA 这足够（只有一个最优解），但若 `ga_hotstart_solver` 后续扩展为返回 Pareto frontier，逻辑会漏检。当前设计合理，但应在 `so_f1.py` 注释中说明"single-objective, only knee verified"。

## 修复进度总览

| # | 类别 | 状态 |
|---|------|------|
| P0（Earth-radius） | Spec | **已修复 ✓**（generate_s4_s6 自洽，compute_batch_visibility 无误差） |
| P1（resolution 子检查） | Spec | **已修复 ✓** |
| P2（φ→θ 转换） | Spec | **已修复 ✓** |
| P3（squint 验证条件化） | Spec | 未改 |
| S1（RDR-004 helper） | Standards | 未改 |
| S2（squint helper） | Standards | 未改 |
| S3-S7 | Standards | 未改 |
| N1（循环依赖风险） | Standards | 新增，低优先（加注释即可） |
| N2（OP-1 算子参数） | Spec | **已闭环 ✓**（误判更正：代码向论文 20/0.1 对齐，偏差消除） |
| N3（post-hoc 过滤口径） | Spec | 新增，高（重跑数据不可混合） |
| N4（h_sat_m 来源） | Spec | **已验证 ✓**（h_sat_m = altitude_km × 1000，无误差） |
| N5（so_f1 单解验证） | Spec | 新增，低优先 |

## 复审结论

**已修复/已闭环**（5 项）：
- P0 — Earth-radius：四口径一致，无 7 km 误差
- P1 — 验证器删除已废弃 resolution 子检查
- P2 — 验证器真正在 θ 空间比较（φ→θ 转换）
- N2 — 遗传算子参数（误判更正）：代码向论文 20/0.1 对齐，OP-1 代码侧闭环
- N4 — `h_sat_m` 来源已验证（函数入参，无反推误差）

**仍未改**：S1/S2（helper 抽取）、S3-S7（命名/死测试等）、P3（squint 验证条件化）、N1（循环依赖注释）、N5（so_f1 单解验证注释）— 均低优先。

**当前唯一高风险**：
- **N3** — post-hoc ConstraintVerifier 过滤改变 `n_frontier_points` 口径。已提交的 `baselines_200.json`、消融结果等是**未过滤**口径；本轮重跑会是**过滤后**口径。两批数据不可直接混合。建议：（a）字段重命名为 `n_frontier_feasible`，或（b）meta 同时保留 `n_frontier_raw` 和 `n_frontier_feasible`。

**测试**：本轮改动相关 32 passed；6 failed 全是场景 pkl 缺失（环境问题），非回归。

**下一步优先级**：
1. 决策 N3 的 post-hoc 过滤字段命名 + 数据口径策略
2. （可选）抽 S1 / S2 helper，消除 6+ 处重复
3. （可选）修 S3-S7、P3、N1、N5（低优先，命名/注释）

## 更正声明（N2）

第三轮初稿的 N2 判断（"遗传算子参数变更让 OP-1 偏差更严重"）为**误判**。论文 [small-paper-ijae.tex:L529-L531](file:///d:/hermes/my-workspace/projects/planning%20paper/papers/single-sat-quality/small-paper-ijae.tex#L529-L531) 一直写的是 ηc=20 / pm=0.1，本轮代码改动是代码向论文对齐。根本原因：基于 REVIEW_INDEX.md OP-1 的旧描述反向推断，未直接验证论文原文。
