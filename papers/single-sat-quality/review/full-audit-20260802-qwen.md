# 全量审计报告 — single-sat-quality (ASR 第三章小论文)

**审计日期**: 2026-08-02
**审计员**: qwen (千问办公)
**审计范围**: `small-paper-ijae.tex` (英文主文) + `sections/_ablation_section.tex` (消融章节) + `small-paper-ijae.bib` + `highlights.tex` + 实验数据/代码/管道
**审计方法**: 4 路并行 subagent (数据质量 / 公式与代码 / 文档一致性 / 管道完整性) + 主 agent Grep/Read 交叉验证关键 🔴 发现
**对比基准**: 纯新审，不对照 20260801-qwen-V1 旧报告

---

## 严重度统计

| 严重度 | 数量 | 说明 |
|--------|------|------|
| 🔴 严重 | **6** | 数值错误 / 代码与论文不符 / 管道断链，影响结论或可复现性 |
| 🟡 次要 | **14** | 小数位差异 / 推导缺步 / 排版不一致 / 中间产物，不影响核心结论 |
| 🟢 一致 | **~120** | 数值精确吻合 / 公式正确 / 引用完整 / 链路可追溯 |
| ⚪ 无数据源 | **4** | 辅助性数值未存储在 JSON/CSV 中，无法验证 |

**总体评价**: 论文核心数值（Table 2/3/5/6 全部 60+96 个数值、所有统计检验值、Friedman/Wilcoxon/Cliff's δ、N₅₀ 逻辑回归）**全部与实验数据文件精确一致**；数值计算（cos³(10°)≈0.955、r_null=-0.51、r_θ=-0.997）**全部验证正确**；公式符号一致性良好；bib 引用完整无断链。主要问题集中在 **遗传算子参数代码与论文不符**（2 个 🔴）和 **图表生成脚本与论文引用名称错位**（2 个 🔴），以及编译链和 manifest 元数据问题（2 个 🔴）。

---

## 🔴 严重发现（6 项）

### 🔴-1 | moea.py NSGA3 遗传算子参数与论文声明不符

**位置**: 论文 L529-531 vs `src/sar_sim/solver/moea.py` L599-606
**论文声明**: "simulated binary crossover ($p_c = 0.9$, $\eta_c = 20$) and polynomial mutation ($p_m = 0.1$, $\eta_m = 20$)"
**代码实际**: `NSGA3(pop_size=..., ref_dirs=..., sampling=...)` 未传入 crossover/mutation 参数，使用 pymoo 默认值（SBX eta=15, PM prob≈0.9/prob_var=1/n_var）
**证据**:
```python
# moea.py L599-606
algorithm = NSGA3(
    pop_size=population_size,
    ref_dirs=ref_dirs,
    sampling=sampling,
)  # 无 crossover= / mutation= 参数
```
**影响**: SBX 的 ηc=15 vs 20 影响交叉分布范围（ηc 越大后代越接近父代）；PM 的 prob=0.9 vs 0.1 差异极大——pymoo 默认 prob_var=1/n_var 对 n_var=20~500 给出 0.05~0.002，与论文声称的固定 0.1 差异数倍至两个数量级。这影响搜索行为和收敛特性，可能使 MOEA 结果不可复现。
**建议**: 在 moea.py 中显式传入 `crossover=SBX(prob=0.9, eta=20), mutation=PM(prob=0.1, eta=20)`，或修改论文参数描述以匹配实际代码。**这是可复现性的红线问题——投稿前必须对齐。**

---

### 🔴-2 | so_f1.py GA-P-BL 遗传算子参数与论文声明不符

**位置**: 论文 L529-531 vs `src/sar_sim/solver/so_f1.py` L542-544
**论文声明**: SBX pc=0.9, ηc=20; PM pm=0.1, ηm=20
**代码实际**: SBX(prob=0.9, eta=**15**), PM(prob=**1.0/(2*instance.N)**, eta=20)
**证据**:
```python
# so_f1.py L541-544
algorithm = GA(
    pop_size=population_size,
    sampling=_HotStartSampling(x0, population_size, seed or 1),
    crossover=SBX(prob=0.9, eta=15),              # ≠ 论文 ηc=20
    mutation=PM(prob=1.0 / (2 * instance.N), eta=20),  # ≠ 论文 pm=0.1
    eliminate_duplicates=False,
)
```
**影响**: 对 N=20, PM prob=1/(2×20)=0.025；对 N=500, PM prob=0.001。论文声称固定 pm=0.1。SBX eta=15≠20。与 🔴-1 同属遗传算子参数不一致，影响可复现性。
**建议**: 将代码改为 `SBX(prob=0.9, eta=20), PM(prob=0.1, eta=20)` 以匹配论文，或在论文中如实注明实际参数（含 N 依赖的 PM prob）。**注意**: `b2_profit_solver()`（非 seeded 版本，L379-384）参数也不匹配（SBX eta=15, PM prob=0.2, eta=10），但该函数不在论文实验管道中，可单独处理。

---

### 🔴-3 | gen_all_figures.py 输出文件名与论文引用全部错位

**位置**: `experiments/gen_all_figures.py` L278, L408, L499, L685 vs 论文 L738, L776, L806, L857
**论文引用的 5 个 figure 文件名**:
- `fig1_hypervolume.pdf` (L738)
- `fig2_squint_effect.pdf` (L776)
- `fig3_scale_sensitivity.pdf` (L806)
- `fig4_solver_profiles.pdf` (L857)
- `fig5_ablation.pdf` (ablation L95)

**脚本实际生成的文件名**:
- `fig1_squint_effect` (L278) → 错位
- `fig2_solver_profiles` (L408) → 错位
- Fig 3 被 REMOVED（L281 注释），不生成 → 缺失
- `fig4_hypervolume` (L499) → 错位
- `fig5_scale_sensitivity` (L685) → 错位

**现状**: `figures/` 目录下存在正确命名的 5 个 PDF（fig1_hypervolume.pdf 等），说明它们要么被手动重命名，要么由某个已不存在的脚本版本生成。**当前 gen_all_figures.py 无法直接重新生成论文所需的图。**
**影响**: 图表生成链路断裂——若需重新生成图表（如审稿要求修改），将无法通过当前脚本完成。
**建议**: 重写 gen_all_figures.py 中的 `save_figure()` 调用名称使其与论文引用一致，或创建显式的 rename 映射文档。

---

### 🔴-4 | gen_fig6_ablation.py 输出 fig6_ablation.pdf 而非论文引用的 fig5_ablation.pdf

**位置**: `experiments/gen_fig6_ablation.py` L205, `experiments/gen_ablation_figure.py` L151 vs ablation section L95
**论文引用**: `\includegraphics[width=\textwidth]{fig5_ablation.pdf}`
**代码实际**: 两个脚本均输出 `fig6_ablation.pdf`
**证据**: gen_fig6_ablation.py L205 `out = FIG_DIR / "fig6_ablation.pdf"`；gen_ablation_figure.py L151 `default=str(PROJECT / "figures" / "fig6_ablation.pdf")`
**现状**: `figures/fig5_ablation.pdf` 存在（手动重命名），但脚本生成的是 fig6。
**建议**: 将两个脚本的默认输出路径改为 `fig5_ablation.pdf`；删除或归档 gen_ablation_figure.py（功能被 gen_fig6_ablation.py 覆盖）。

---

### 🔴-5 | compile.bat 缺少 bibtex 编译步骤

**位置**: `compile.bat` L3-4
**问题**: 仅运行两次 `pdflatex -interaction=nonstopmode -halt-on-error`，缺少 `bibtex small-paper-ijae` 步骤
**影响**: 论文使用 `\bibliography{small-paper-ijae}` + `\bibliographystyle{elsarticle-harv}`，含 25 个 \cite/\citet 引用。缺少 bibtex 会导致所有引用显示为 `[?]`，参考文献列表为空。**若用户使用外部 IDE（如 TeXstudio/VS Code）编译则不受影响**，但 compile.bat 本身不完整。
**附加问题**: L2 硬编码绝对路径 `cd /d "D:\hermes\..."`，违反 AGENTS.md "路径硬代码" 红线。
**建议**: 改为标准序列 `pdflatex → bibtex → pdflatex → pdflatex`，路径用 `%~dp0` 替代硬编码。

---

### 🔴-6 | manifest.json 陈旧，与论文 Table 1 严重不一致

**位置**: `experiments/scenarios/manifest.json` vs 论文 L567-581 (Table 1)
**论文声明**: S1(N=20), S2(N=100), S3(N=300), S4(N=500)，每类 50 scenarios，轨道高度 693 km
**manifest.json 实际**:
```json
"scales": {"small": 20, "medium": 100, "large": 500},  // 缺少 S3(N=300)
"n_seeds": 30,                                          // ≠ 论文 10 seeds × 5 types = 50
"total_scenarios": 90,                                   // ≠ 论文 200
"orbit": {"altitude_km": 600.0}                          // ≠ 论文 693 km
```
**影响**: manifest.json 是早期 S5/S6 实验的遗留（generate_s5_scenarios.py 用 600 km），不反映当前 4 类 × 50 = 200 scenario 配置。任何依赖 manifest.json 的自动化流程会误用元数据。
**证据**: `experiments/generate_all_scenarios.py` L38 SENTINEL1 dict 使用 `altitude_km: 693.0`，与 manifest 不符。
**建议**: 重新生成 manifest.json 以反映实际 4 类 × 50 scenario 配置，或将其拆分为每类独立 manifest。

---

## 🟡 次要发现（14 项）

### 数据质量路（3 项）

**🟡-1** | 论文 L983 | S4 hot-start deficit SD: 论文 0.04 vs 数据 0.046（应四舍五入为 0.05）| `p1-1_random_init/s3_s4_control.json` delta_std=0.046
**🟡-2** | 论文 L1006 | random search f1* SD: 论文 0.01 vs 数据 0.015（应四舍五入为 0.02）| `p1-2_s1_random_search.json` SD=0.015
**🟡-3** | 论文 L989 | random/hot f2 区间: 论文 [0.605,0.624]/[0.594,0.603] vs 数据 [0.601,0.611]/[0.591,0.598]（S3+S4）| 数据范围比论文所述更窄，可能包含 S1/S2 数据

### 公式与代码路（5 项）

**🟡-4** | 论文 L245-251 | NESZ ∝ 1/(cos³θ·cos³ψ_sq) 推导中 cos³θ 项来源未显式说明。推导链: NESZ∝R³ → R≈R_elev/cos(ψ_sq) → 缺步 → 1/(cos³θ·cos³ψ_sq)。需补充 R_elev ∝ 1/cosθ 的说明。
**🟡-5** | 论文 L827-830 | N₅₀≈140 依赖 logistic-in-N 模型形式；若用标准 logit+log(N) 则 N₅₀≈119。论文未指定模型形式。建议注明 "logistic-in-N: p=1/(1+exp(k(N-N₅₀)))"。
**🟡-6** | `baselines.py` L633 vs 论文 L502 | G-SM (baseline_b3) 调用 `greedy_solver()` 按优先权降序排序，而论文声明 "shares G-BL's greedy structure (sort by earliest start time)"。G-BL (baseline_b1) L397 确实按 t_start 排序。排序策略不一致，但 G-SM 的核心 squint-minimization 特征已正确实现。
**🟡-7** | `types.py` L80, `nesz.py` L76 | 代码默认高度 600 km ≠ 论文 693 km。`build_agile_instance` 的 `altitude_m` 参数可被覆盖，若实验脚本传入 693 km 则无影响。建议确认实验脚本传参。
**🟡-8** | `baselines.py` L714-765 | `_b3_squint_minimize` 搜索 `geom_cache.cache[task_idx]` 跨所有窗口的时间网格，而非仅限当前调度的窗口。若任务有多个窗口，可能从另一个窗口选择时间。论文 L503-505 说 "within each visibility window"。

### 文档一致性路（3 项）

**🟡-9** | 论文 L409 (eq:observation-domain), L432 (eq:c2) | 两个方程有 `\label` 但全文无任何 `\ref`/`\eqref` 引用。正文以 "C2" 文字提及该约束（L413, L414, L424, L437, L515），但从不通过 `\eqref{eq:c2}` 定位。建议在首次提 "C2" 时改用 `\eqref{eq:c2}`。
**🟡-10** | 论文 L64, L217 vs L39, L94, L244, L364 | NESZ 大小写不一致：正式定义用 Title Case "Noise-Equivalent Sigma Zero"，keyword 和 running text 用 lowercase "noise-equivalent sigma zero"。建议统一。
**🟡-11** | highlights.tex H3 | "3-obj redundancy anchor-independent" 措辞精度问题。论文 body (L925) 称 redundancy 是 "empirical convergence effect"，conclusion (L1152) 说 "geometric redundancy is the anchor-independent result"——论文区分了现象与机制。highlight 将二者合并，建议改为 "3-obj redundancy persists without hot-start" 或 "geometric redundancy anchor-independent"。
**附加排版**: 约 20 处 `\S\ref`（无 `~`）vs 25 处 `\S~\ref`（有 `~`）混用；`fig1` caption 用 "left/right" 而 `fig2/fig4` 用 "(a)/(b)/(c)"；`Herrmann2023` 缺 volume/number。

### 管道完整性路（3 项）

**🟡-12** | `experiments/statistical_analysis.py` L3 | docstring 声明 "300 scenarios" 但论文用 200。可能是早期 S1-S6 设计残留。
**🟡-13** | `experiments/statistical_analysis.py` L292 | Cliff's δ 有两套实现：嵌入的简化版 `(greater-less)/n`（用于日志打印）和 `gen_all_figures.py` L169-176 的标准版（遍历所有交叉对）。effect_sizes.json 使用标准版，不影响输出，但代码冗余易混淆。
**🟡-14** | `scripts/run_full_experiment.py` L15-16 | 语法错误 `Path(r"PROJECT / "experiments\scenarios"")`（raw string 内嵌引号）。该脚本是 Phase 4.2 早期遗留，处理 "S1-S6 共 300 scenarios"，已无法执行。建议归档或删除。同类: `scripts/generate_s5_scenarios.py` L17 同样语法错误，S5/S6 不在论文中。

**其他管道观察**: S7/S8 .pkl 文件缺失（results JSON 存在，可复现）；figures/experiments/ 含大量中间产物（pareto_fronts_S*.pdf, hv_boxplot_S*.pdf, figure_1/2/3.pdf 等）未被论文引用；experiments/README.md 仅列 4 个 runner 脚本，遗漏 20+ 个实际脚本；baseline_b2 在 run_full_experiment.py 中被调用但 AGENTS.md 未登记。

---

## ⚪ 无数据源验证（4 项）

| 位置 | 声明值 | 说明 |
|------|--------|------|
| L893 | r_MC=-0.5120 | Monte Carlo 验证值未存储在 JSON/CSV，仅有 `scripts/validate_null.py` 可重新计算 |
| L832 | 四点 CI [111, 227] | 四点(S1-S4)逻辑回归 CI 未存储（n50_logistic.json 存的是六点 CI） |
| L914 | A 变体经验相关 -0.69~-0.17 | `f2_f3_coupling.json` 已标记 DEPRECATED（正值，不可复现），A 变体需运行 reproduce_A_r.py |
| L915 | D 变体 S1 相关 -0.44 | `variant_d_per_task_r.json` 仅含 S2-S4，S1 数据缺失 |

---

## 🟢 一致性确认（核心发现）

### 数据精确吻合

Table 2 (solver-profiles) 全部 60 个数值（5 solvers × 4 classes × 3 metrics × {mean,SD}）与 `baselines_200.json` + 各 `_progress.json` 精确一致。

Table 3 (hv) 3 个 HV 值与 `statistical_results.json` 的 `hv_by_solver` 精确一致（MOEA-3: 0.173±0.045, MOEA-2: 0.169±0.037, G-BL: 0.140±0.017）。

Table 5 (scale-sensitivity) 全部 6 行 × 4 列与 `moea_2obj/_progress.json` + `baselines_200.json` + `baselines_S7S8.json` 精确一致，包括 S7/S8 中间密度点。

Table 6 (ablation) 全部 96 个数值（4 variants × 4 classes × 6 columns）与各消融变体 `_progress.json` 精确一致。

所有统计检验值（Friedman χ²=506.56/p≈10⁻¹⁰⁸, Wilcoxon p 值, Cliff's δ 配对值）与 `statistical_results.json` / `effect_sizes.json` 精确一致。

N₅₀=139.6≈140, CI[117.368, 168.509]≈[117,169] 与 `n50_logistic.json` 精确一致。

G-SM f3 改善 +34%(S1)/+70%(S4)、GA-P-BL f1*=1.09-1.28、HV S4/S1 ratio 0.72/0.67 等正文数值全部验证正确。

### 数值计算正确

cos³(10°)=0.9551≈0.955 ✓；"4-5%水平"=1-0.955=4.5% ✓；r_θ=-0.997（sinθ vs cos³θ 在 θ∈[15°,50°] 均匀分布）✓；r_ψ=+0.997（cosψ vs cos³ψ 在 |ψ|≤45°）✓；r_null=-0.51（解析积分=-0.5122, MC=-0.5106）✓；Das-Dennis H=13(2-obj)/91(3-obj) ✓。

### 公式符号一致

φ_i 表示纬度（L303），ξ 表示 off-nadir（L318），全文未见 φ 混用作 off-nadir ✓。消融节所有 ψ_{sq} 正确写作 `\psi_{\text{sq},i}`，无遗漏下标 ✓。f1/f2/f3 公式与 moea.py/baselines.py/so_f1.py 代码实现一致 ✓。θ=arcsin((R_e+H)/R_e·sinξ) 球面几何正确 ✓。

### 文档完整

\label/\ref 配对无断链（所有引用有定义）✓。bib 25 条目与 25 引用 key 完全对应，无断链无多余 ✓。图表编号连续（fig1-5, tab 1-6）✓。数字跨章节一致（8.2%, N₅₀≈140, 200 scenarios, δ=+0.72 等）✓。章节交叉引用内容匹配 ✓。

### 核心管道可追溯

5 个核心结果文件（solver_summary.csv, statistical_results.json, effect_sizes.json, ablation_summary.csv, baselines_200.json）与论文 Table 一一对应 ✓。统计方法（Friedman+Wilcoxon+Bonferroni+Cliff's δ）在 statistical_analysis.py 中正确实现 ✓。核心 solver 入口（moea_solver, b2_profit_solver_bl_seeded, baseline_b1/b3, quality_score）与 AGENTS.md 登记一致 ✓。控制实验脚本（run_hotstart_control, run_variant_d_random_init, validate_null, run_sigma_sweep）与论文 §6.6 各控制实验对应 ✓。

---

## 修订建议清单（按优先级）

### P0 — 投稿前必须修复（可复现性红线）

1. **🔴-1/🔴-2**: 对齐遗传算子参数。选择一: 代码改 `SBX(prob=0.9, eta=20), PM(prob=0.1, eta=20)`；选择二: 论文改述实际参数。**建议选择一**（改代码），因为 ηc=20 和固定 pm=0.1 是更标准的 NSGA-III 配置。
2. **🔴-3/🔴-4**: 修复图表生成脚本输出名，使其与论文 `\includegraphics` 引用一致。重写 gen_all_figures.py 的 `save_figure()` 调用；gen_fig6_ablation.py 输出改 `fig5_ablation.pdf`。
3. **🔴-5**: compile.bat 加入 `bibtex small-paper-ijae` 步骤（若已有外部编译流程可降级为 🟡，但仍建议修复）。

### P1 — 审稿前应修复

4. **🔴-6**: 重新生成 manifest.json 以反映 4 类 × 50 scenario + 693 km 配置。
5. **🟡-4**: NESZ 推导补充 cos³θ 来源说明（一句: "where R_elev ∝ 1/cosθ from the elevation-plane viewing geometry"）。
6. **🟡-6/🟡-8**: G-SM 排序策略和 squint 搜索范围与论文描述对齐。选择一: 代码改用 t_start 排序 + 限当前窗口搜索；选择二: 论文改述实际策略。
7. **🟡-9**: 在正文首次提 "C2" 处改用 `\eqref{eq:c2}`，消除零引用 label。

### P2 — 清理项（不影响投稿）

8. **🟡-5**: N₅₀ logistic 模型形式注明。
9. **🟡-10/🟡-11**: NESZ 大小写统一；highlight H3 措辞精化。
10. **🟡-12/🟡-13/🟡-14**: 统计脚本 docstring 修正；Cliff's δ 实现统一；废弃脚本归档。
11. 排版统一: `\S~\ref`、fig1 面板标注风格、Herrmann2023 bib 补全。
12. 清理 figures/experiments/ 中间产物；扩展 experiments/README.md。

---

## 冻结门控 Checklist

投稿前必须全部通过:

- [ ] **G1**: moea.py NSGA3 显式传入 SBX(eta=20) + PM(prob=0.1)（或论文改述）
- [ ] **G2**: so_f1.py ga_hotstart_solver 显式传入 SBX(eta=20) + PM(prob=0.1)（或论文改述）
- [ ] **G3**: gen_all_figures.py 输出名与论文 5 个 `\includegraphics` 引用一致
- [ ] **G4**: gen_fig6_ablation.py 输出名改为 fig5_ablation.pdf
- [ ] **G5**: compile.bat 含 bibtex 步骤（或有文档化的外部编译流程）
- [ ] **G6**: manifest.json 反映 4 类 × 50 scenario + 693 km 配置
- [ ] **G7**: 重新运行 moea/so_f1/baselines 确认参数修改后结果一致性（若改了代码参数，需重跑实验验证数值不变或更新 Table）
- [ ] **G8**: NESZ 推导补充 cos³θ 来源说明
- [ ] **G9**: eq:observation-domain / eq:c2 零引用消除

**注意**: G7 是关键——若修改遗传算子参数（G1/G2），实验结果可能变化，需重跑 200+800 runs 验证 Table 2/3/5/6 数值是否仍一致。若结果变化，需更新论文数值。这是参数对齐的最大成本。

---

## 审计方法说明

本审计采用 4 路并行 Explore subagent + 主 agent 交叉验证:

| 路线 | 职责 | 核对项数 |
|------|------|---------|
| 数据质量路 | Table 2/3/5/6 + 正文统计值 vs results/*.json/csv | ~120 |
| 公式与代码路 | 数值计算 + 符号一致性 + solver 代码 vs 论文方法声明 | ~25 |
| 文档一致性路 | \label/\ref 配对 + bib + 术语 + 数字跨章节一致 | ~40 |
| 管道完整性路 | scenario manifest + 图表生成链路 + 脚本入口 + 编译链 | ~30 |

主 agent 对 6 个 🔴 发现全部用 Grep/Read 直接读取代码/文件行进行交叉验证，确认无误报。4 项 ⚪ 无数据源的数值为辅助性声明（MC 验证、四点 CI、经验相关），不影响论文核心论证。

---

*报告生成于 2026-08-02 by qwen (千问办公)。遵循项目约定: 论文级审计用 🔴/🟡/🟢 分级，报告放 papers/<theme>/review/。*
