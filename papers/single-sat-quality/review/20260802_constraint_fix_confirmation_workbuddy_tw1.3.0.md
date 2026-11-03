> Reviewed by: workbuddy (论小舟 / thesis-writing-mentor) · thesis-workflow v1.3.0 · 2026-08-02
> Subject: 确认 trae 的约束代码修复是否到位（数据翻车根因）

## 结论
**代码修复本身是正确的**，但**论文主结果（MOEA 前沿）没有用修复后代码重跑**，仍是翻车前的旧数据——这是当前最大的风险点。

## 1. 代码修复：正确 ✓

trae 改动（working tree 未提交，git root `.../planning paper`）：
`src/sar_sim/solver/{moea,so_f1,baselines,solver_factory}.py` + `src/sar_sim/verification/{constraints,__init__}.py` + 测试 + `experiments/results/baselines_200.json`。

- **C2 过渡/非重叠（RDR-004，翻车根因）**：旧逻辑"只要 B 能在自己窗口内往后挪就 `continue` 免罚"→ 优化出的实际排程允许观测重叠，而 f2/f3 几何却按这些非法时刻计算。新逻辑直接对解码时刻施加惩罚：`gap = t_b - (t_a + duration_a)`，若 `gap < tau_trans` 就罚。严格更优，可行解仍可找到。✓
- **C1 入射角 + 斜视角 squint**：旧内联惩罚（MOEA-2/MOEA-3/C7）全删，理由"已在窗口生成阶段落实"。已核实 `visibility._check_geometric_constraints` 检查 `incidence∈[min,max]` 且 `squint≤max_squint_deg`，且 `generate_all_scenarios.py:438` 用真实 instrument（incidence 18–47° / 15–35°，squint 默认 45°）生成窗口 → C1 在窗口阶段真落实。✓
- **C3/C4 能量/内存**：逻辑未变，正确。✓
- 基线过滤器 `_enforce_c2_transitions` 用直接 gap 检查+必要时延迟当前观测，基线本就严格可行（非翻车源）。

## 2. 测试：通过（约束逻辑）
pytest（系统 py3.14，含 numpy/pymoo/pytest）跑 `test_phase8 / test_constraint_c4c5 / test_b3_squint_min / test_spec_v4` → **17 passed / 3 failed**。3 个失败全是 `test_spec_v4` 因本机缺 `experiments/scenarios/*` pkl（数据缺失，非代码回归）。

## 3. 数据审计：基线已重跑，主结果未重跑 ⚠️

- `baselines_200.json`（G-BL=b1 / G-SM=b3）于 8/2 重跑。相对 `._baselines_200_pre_rdr003.json` 快照：b1 `n_selected` 105/200 场景变化（mean +0.92，来自 RNG/种子差异，非回归），f2/f3 微变；b3 `f3` mean −0.12（RDR-003 把 squint 最小化限制在本窗口内，符合预期）。基线无回归。
- **`experiments/results/moea_3obj/` 最新 2026-07-12、`moea_2obj/` 2026-07-31、三个 `moea_3obj_no_*` 变体均 7/12**——全在修复（8/2）之前。
- `analyze_ablation.py` 直接读 `moea_3obj / moea_3obj_no_squint / moea_3obj_no_incidence / moea_3obj_no_physics` 作为消融表 A/B/C/D；论文核心 HV/IGD 表来自 `moea_3obj / moea_2obj`。**这些可能仍是基于翻车前（非法排程）数据。**

## 4. 建议（下一步）
1. 在装有 `experiments/scenarios/*` 的机器上，用修复后代码重跑 `moea_3obj` / `moea_2obj` / 三个 `no_*` 变体。
2. 重跑后重新生成论文表格（`.tex` 不在 trae 改动列表中，表格数字可能仍是旧的）。
3. 补一个真断言 squint 拒绝的单元测试——当前 `test_phase8::test_d_check_geometric_constraints_rejects_squint` 是空 `pass`，实际未覆盖。

## 5. 残差备注
- C1 现完全依赖窗口预过滤 + post-hoc verifier（优化器内无内联惩罚），靠 `ConstraintVerifier` 在 `solver_factory.compare_algorithms` 排除 INFEASIBLE 解兜底。
- 分辨率约束 `phi_min_res` 实验默认 0（未传 `resolution_reqs`）→ 被平台入射角范围覆盖，无回归。
