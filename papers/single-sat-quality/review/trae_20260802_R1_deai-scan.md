# ppw:de-ai Phase 1 检测报告

> **目标文件：** `small-paper-ijae.tex` + `sections/_ablation_section.tex`
> **检测范围：** 全文（Abstract → Conclusion + 消融章节）
> **检测维度：** 词汇滥用（Vocabulary Inflation）、句式过度（Sentence Overclaims）、过渡平滑化（Transition Smoothing）
> **运行模式：** Phase 1 Scan only（只检测不改写）
> **检测时间：** 2026-08-02

---

## 概要

Found **15 AI patterns**（**5 High Risk** / **4 Medium Risk** / **6 Optional**）
Skipped domain terms / protected formats: 2 类（见文末附录）

---

## HIGH RISK（高风险，强烈建议改写）

### [#1] [HIGH RISK] Transition Smoothing — "A rather than B" 机械对比过度使用（≥18次）

**Pattern:** 全文反复使用 "rather than" / "not X but Y" / "distinct from" / "without V-ing" / "separates cases where A from cases where B" 框架进行对比，密度远超人类作者（60页短文 ≥18 处）。SKILL.md 核心约束明确标记此结构为 AI 机械化连接的典型特征。

**典型原文举例（按位置）：**
- Abstract (L42–43, L59–61):  
  `…distinct from scalar visibility composites used in prior SAR scheduling.`  
  `…reflecting the geometric coupling of the low-squint regime rather than a mathematical identity between objectives. Rather than identifying a superior solver, our results establish an empirical saturation boundary for physics-aware multi-objective scheduling under the tested…conditions.`
- §6.4 Pareto Compression (L918–928):  
  `The θ-conflict therefore persists inside the schedules rather than being reversed; scheduled observations are not drawn uniformly from the envelope, … select low-squint geometries that suppress the θ-conflict and align f₂ with f₃ … but the residual negative correlation corresponds to the θ-axis conflict space where genuine f₂–f₃ trade-offs remain. The 3-objective redundancy is therefore an empirical convergence effect—not a mathematical identity between f₂ and f₃ but a consequence of solver convergence to low-squint regimes that narrows, without eliminating, the incidence-angle conflict.`
- §6.4 (L942–948):  
  `…move the correlation toward zero—from −0.95 in the visibility envelope to ≈ −0.69 to −0.17 within the full-physics schedules—but do not reverse its sign: the incidence-angle conflict is narrowed by low-squint convergence, not eliminated. This partial attenuation is an active effect of the solvers, not a consequence of geometric envelope constraints…`
- §6.6 Robustness (L989–990, L1005–1006, L1016–1018):  
  `The coverage ceiling is therefore a G-BL initialization effect rather than an artifact of the MOEA framework.`  
  `…the MOEA's gains therefore reflect structured search rather than luck.`  
  `These controls collectively favor the low-squint convergence explanation over hot-start residue, noise-level sensitivity, random chance, or insufficient budget, while not ruling out all algorithm-specific effects.`
- §7.1 Summary (L1028–1038, L1044–1056):  
  `separates cases where multi-objective optimization yields a measurable quality–coverage advantage from cases where it does not.`  
  `…the three-objective formulation is effectively redundant, because per-task f₂–f₃ correlation within schedules stays negative but weakens with density … confirming that low-squint convergence narrows, rather than removes, the incidence-angle conflict; (3)…G-SM occupies a distinct high-radiometric-quality regime at substantial density-dependent coverage cost; (4)…; and (5)…coverage convergence toward the G-BL anchor is conditional on the hot start, not a structural property. The first four reflect geometric properties…(finding (2) being an empirical convergence effect under those properties…); the fifth reflects solver initialization.`
- §7.2 + §7.4 + §8:  
  `delimiting the present claims to the marginal value of adding physical objectives rather than to profit-oriented search alone.`  
  `…not a mathematical identity between f₂ and f₃.`  
  `…rendering the three-objective formulation effectively redundant. Coverage convergence toward the G-BL anchor is conditional on the hot start; the geometric redundancy is the anchor-independent result. GA-P-BL still exceeds the anchor through single-objective temporal search, so this result delimits the benefit of adding physical objectives.`

**Suggested rewrite direction:** 把机械对比拆成独立陈述，或用转折连词（however, though, conversely）自然衔接；把 "not A but B" 改成 "B, not A" 的后置限定或直接陈述。

---

### [#2] [HIGH RISK] Transition Smoothing — 机械分类/章节导航模板（6处）

**Pattern:** 每节开篇直接使用 "我们考察三个研究方向 / 本研究包含三类实验 / 下节从五个视角展开分析" 等明确的目录式导航句，并对每个分支用相同语法结构（§X 动词 A；§Y 动词 B；§Z 动词 C…）排比列出。这是大模型为了"结构清晰"而刻意添加的路标，人类写作通常内隐在段落逻辑中而非显式宣告。

**典型原文：**
- §2 Related Work (L169–171):  
  `We examine three lines of research that our study connects: satellite scheduling (2.1), SAR physical quality modeling (2.2), and multi-objective evolutionary optimization (2.3).`
- §5.4 Experiment Design Overview (L650–662):  
  `This study comprises three classes of experiments. The first is the main experiment, running all five solvers (G-BL, G-SM, GA-P-BL, MOEA-2, MOEA-3) on 50 scenarios per density class (S1–S4), totaling 200 scenarios. Results from the main experiment are presented in §6.1–§6.4 and §6.2. The second is the ablation experiment, which successively removes the squint component (variant B), the incidence-angle component (variant C), and all physical objectives (variant D) from the MOEA-3 framework, running each variant on the same 200 scenarios (§6.5). The third comprises robustness control experiments—hot-start dependence, perturbation-sensitivity sweep, random-search calibration, and search-budget control—which verify that the main and ablation findings are not artifacts of initialization or parameter choices (§6.6).`
- §6 Results 章节导航 (L745–750):  
  `The following sections deepen this overall analysis from five perspectives: §6.2 examines the special trade-off of squint-aware scheduling, §6.3 investigates scale sensitivity (how multi-objective advantage varies with target density), §6.4 reveals the geometric mechanism of Pareto compression, §6.5 verifies the condition dependence of this mechanism through ablation, and §6.6 separates initialization and search-budget confounds through robustness controls.`

**Suggested rewrite direction:** 删除显式分类宣告，直接从每个子节的第一句自然承接上节结论；五重排比的章节导航建议删除，改为图号自然引导。

---

### [#3] [HIGH RISK] Sentence Overclaims — 超长复合句堆叠（8处单句 ≥60词）

**Pattern:** 单句内嵌 ≥3 层从句、括号解释、多重冒号/分号，实际阅读时需要多次停顿断句。典型集中在定量结果解释段（§6.4、_ablation）和方法段（§5.3）。人类作者通常在这些位置拆成 2–3 句，或以从句+独立句的形式展开。

**典型原文：**
- Abstract (L37–43，约 85 词单句):  
  `We characterize an empirical saturation regime for multi-objective SAR quality optimization in single-pass, single-satellite Stripmap operation by integrating two physical quality dimensions, Noise-Equivalent Sigma Zero (NESZ, radiometric) and geometric resolution, as decomposed optimization objectives within a Non-dominated Sorting Genetic Algorithm III (NSGA-III) framework, distinct from scalar visibility composites used in prior SAR scheduling.`
- §6.4 Empirical correlation 段 (L910–928，约 170 词一整段连续复合句):  
  `Pooled across all scheduled tasks from the 200 scenarios, the per-task empirical correlation between f₂ and f₃ within the solver-selected schedules is negative but weaker than the envelope: for the full-physics MOEA-3 (variant A) it ranges from −0.69 (S1) to −0.17 (S4), and for the no-physics variant D from −0.44 (S1) to −0.18 (S4), decreasing in magnitude as scenario density rises (Table VII). The θ-conflict therefore persists inside the schedules rather than being reversed; scheduled observations are not drawn uniformly from the envelope, and all solvers, including the greedy baselines, select low-squint geometries that suppress the θ-conflict and align f₂ with f₃ along the shared cos ψ_sq factor, but the residual negative correlation corresponds to the θ-axis conflict space where genuine f₂–f₃ trade-offs remain. The 3-objective redundancy is therefore an empirical convergence effect—not a mathematical identity between f₂ and f₃ but a consequence of solver convergence to low-squint regimes that narrows, without eliminating, the incidence-angle conflict.`
- §5.3 Evaluation Metrics (L628–645，约 150 词一整段):  
  `We use hypervolume (HV) as the primary quality indicator for multi-objective comparison. Statistical significance is assessed via the Friedman test for overall differences across 5 solvers × 200 scenarios, followed by pairwise Wilcoxon signed-rank comparisons with Bonferroni correction (α = 0.05/10 = 0.005). Per-objective and ablation comparisons are reported with raw p-values alongside the Bonferroni threshold. Effect sizes are measured by Cliff's δ, classified by the Vargha–Delaney convention (|δ| < 0.147 negligible, < 0.33 small, < 0.474 medium, ≥ 0.474 large). Hypervolume is computed with reference point (0, 0, 0) in the per-solver-pooled min–max-normalized objective space. Per-solver pooling ensures that each solver's HV reflects its own objective range, but it also means that the normalization basis differs across solvers; cross-solver HV comparisons should therefore be interpreted as relative rankings within a shared normalization framework rather than absolute cardinal differences. All-solver-pooled normalization was not used because the single-objective solvers (G-BL, G-SM, GA-P-BL) produce only one point each, which would collapse the min–max range for their objectives.`
- _ablation 反常结果段 (L130–149，约 180 词):  
  `The counterintuitive result that Variant D (no physics) outperforms baseline A on f₁* by 22.1% at S1 is visible in the task counts: D selects 14.7 tasks versus A's 11.1, yet the post hoc geometric quality of the two schedules is nearly identical (f₂ = 0.565 vs. 0.569, a difference of <1%). This near-identity of geometric quality despite the absence of physical objectives reinforces the geometric-coupling interpretation: the low-squint convergence documented in §6.4 is partly a structural property of dense observation-window geometry, but the per-task correlation analysis shows that physical-objective guidance attenuates the incidence-angle conflict further in the sparse regime (r ≈ −0.69 for A versus −0.44 for D at S1), an effect that vanishes as density increases. The coverage gap between A and D arises from the mechanics of NSGA-III in three-objective space: the Pareto front maintained by A contains solutions with fewer tasks but higher per-task quality, which can dominate solutions with more tasks but lower per-task quality in the crowding-distance sorting used by NSGA-III's environmental selection.`

**Suggested rewrite direction:** 在括号解释或分号处拆分为独立句；把冒号后的长解释改为独立陈述句；长推导（因此…又…还…）拆成 2 句+衔接副词。

---

### [#4] [HIGH RISK] Transition Smoothing — "This X serves as / is / confirms Y" 句首定性判断（≥12次）

**Pattern:** 段首或句首频繁用 "This + 名词 + is/confirms/serves as + 定性判断" 收束上文并引出下文。在全文约 30 个主体段落中出现 ≥12 次，密度明显高于人类写作（人类通常用代词自然承接，或直接进入新话题）。

**典型原文举例：**
- §1 Introduction:  
  `This flexibility, however, transforms scheduling from a simple feasibility check into a combinatorial optimization problem…`  
  `This assumption underpins most existing satellite scheduling work, from mixed-integer programming formulations to deep reinforcement learning approaches.`
- §3.2 Objective Functions:  
  `This creates a genuine trade-off: pursuing the cleanest NESZ (zero-Doppler observation) forces acceptance of stretched ground-range pixels; pursuing optimal ground pixel area requires deviating from the zero-Doppler point and accepting elevated radiometric noise.`
- §4.2 G-SM (L510–512):  
  `This strategy serves as a physics-aware greedy baseline: it answers the question "what quality improvement can a simple squint-minimization heuristic achieve, without any multi-objective search?"`
- §4.1 Solver Overview (L480–483):  
  `This design is intentional: it isolates the effect of adding physical quality objectives, which is the paper's research question.`
- §6.4 (L945–948):  
  `This partial attenuation is an active effect of the solvers, not a consequence of geometric envelope constraints: envelope constraints alone would leave the correlation at −0.95.`
- §6.5 Ablation (_ablation L126–128, L134–138, L147–149, L161–170):  
  `This asymmetry confirms that the coverage–quality trade-off is driven primarily by the θ axis, consistent with the dominance of incidence-angle conflict in the envelope correlation (r ≈ −0.95, §6.4).`  
  `This near-identity of geometric quality despite the absence of physical objectives reinforces the geometric-coupling interpretation: …`  
  `This structural explanation is consistent with the search-budget control (§6.6), where doubling population and generations does not separate A from D.`  
  `This numerical invariance is the direct signature of the scale-dependent saturation discussed in §6.3: once the density of candidate observation windows saturates the schedule (N exceeds the maximum selectable targets under the attitude maneuver and squint constraints), the objective function only penalizes infeasible solutions rather than differentiating among feasible ones.`
- §6.6 Robustness (L1016–1018):  
  `These controls collectively favor the low-squint convergence explanation over hot-start residue, noise-level sensitivity, random chance, or insufficient budget, while not ruling out all algorithm-specific effects.`
- §7.1 Summary (L1028–1031):  
  `This operational criterion separates cases where multi-objective optimization yields a measurable quality–coverage advantage from cases where it does not.`
- §8 Conclusion (L1137–1139):  
  `The central finding is a scale-dependent empirical saturation of the marginal benefit of physical objectives in G-BL-seeded MOEA formulations for single-pass, single-satellite Stripmap SAR operations.`

**Suggested rewrite direction:** 一半改写为直接进入新事实陈述（删除 This X is）；另一半改为更自然的衔接（"Consistent with…", "The observation that…", "Taken together,…"）。

---

### [#5] [HIGH RISK] Sentence Overclaims — 冒号 + 长解释/列表过度堆叠（≥25处）

**Pattern:** SKILL.md 核心约束 2&3：移除机械连接、减少插入符号。全文几乎每节都有 "X: [50+词解释]" 或 "X: A, B, and C" 的冒号堆叠结构，把本该由独立句或从句承载的内容全部压缩进冒号后，形成"一口气解释到底"的AI风格。

**典型原文（抽样，≥25处仅展示代表）：**
- §2.2 SAR Physical Quality Modeling (L238–243):  
  `The two resolution components respond oppositely to departure from the zero-Doppler geometry (ψ_sq = 0, θ minimal): ρ_az worsens as |ψ_sq| grows, whereas ρ_rg is coarsest at the minimal incidence of closest approach and improves as θ rises away from it—the origin of the θ-axis trade-off formalized in §3.2.`
- §6.4 Envelope vs schedule (L934–948):  
  `Across C1-feasible visibility samples (|ψ_sq| ≤ 45°, computed across all visibility windows from 20 representative scenarios, approximately 3.9 × 10⁵ window–time-step pairs at 10 s resolution), corr(f₂, f₃) = −0.95, a strong negative correlation dominated by the incidence-angle conflict. This envelope correlation of −0.95 differs from the factorized null r_null = −0.51 (§6.4) because the latter assumes independent θ and ψ_sq, whereas real visibility geometry couples the two angles through the LOS vector, making the θ-conflict dominate. The solver-selected schedules thus move the correlation toward zero—from −0.95 in the visibility envelope to ≈ −0.69 to −0.17 within the full-physics schedules—but do not reverse its sign: the incidence-angle conflict is narrowed by low-squint convergence, not eliminated.`
- §7.2 Operational Implications (L1091–1096):  
  `Our results suggest a conditional operational guideline: for sparse observation requests (N ≲ 100), MOEA-2 may provide geometric quality gains that outweigh the coverage penalty in specific contexts; for dense monitoring campaigns (N ≳ 300), greedy methods (G-SM for radiometric priority, G-BL for coverage priority) approach Pareto-optimal coverage and may be preferable.`
- §7.4 Limitations (L1099–1125，整段大量冒号):  
  `Our study is bounded by scope decisions that define directions for future work. The 3-objective redundancy reported above is specific to the single-pass, single-satellite Stripmap setting: it reflects solver convergence to low-squint regimes that suppress the θ-axis conflict (§6.4, Eq. (14)), not a mathematical identity between f₂ and f₃.`

**Suggested rewrite direction:** 把冒号后长解释独立成句，用 "Specifically, / For example, / To see this," 等软连接；把多个括号内定量说明移到表格或补充材料注释。

---

## MEDIUM RISK（中风险，建议改写）

### [#6] [MEDIUM RISK] Transition Smoothing — 提醒式过渡 "Note that / We caution that / should be interpreted as"（4处）

**Pattern:** 显式添加"注意/我们提醒/应解读为"等元叙述提醒读者如何解读结果，属于AI为了"周到"而插入的引导句，人类作者通常把提醒隐含在语境中或通过限定词（coarse, approximate, relative）自然表达。

**典型原文：**
- §6.3 Scale Sensitivity (L832–835):  
  `Note that the deficit proportion is non-monotonic at the high-density end (S3: 16% → S4: 24%, χ²(1) = 1.00, p = 0.32); N₅₀ should therefore be read as a coarse transition indicator rather than a precise threshold.`
- §6.4 (L968–971):  
  `We caution that the Pareto fronts reported here are best-known approximations obtained via NSGA-III; whether they represent the true Pareto-optimal set is unknown without exact methods, which remain intractable for N ≥ 20 in this problem class.`
- §5.3 Metrics (L637–643):  
  `Per-solver pooling ensures that each solver's HV reflects its own objective range, but it also means that the normalization basis differs across solvers; cross-solver HV comparisons should therefore be interpreted as relative rankings within a shared normalization framework rather than absolute cardinal differences.`
- _ablation (L30–33):  
  `Within-solver ablation with identical NSGA-III parameters and the same G-BL seed injection controls confounding factors sufficiently that the Wilcoxon signed-rank test is appropriate for paired comparison of objective-function variants.`

**Suggested rewrite direction:** 删除 "Note that / We caution that"，直接陈述事实 + 自然限定（如把 "should be read as a coarse indicator" 嵌入主句末尾，或在指标名前加 approximate/relative）。

---

### [#7] [MEDIUM RISK] Sentence Overclaims — "The asymmetry / contrast / counterintuitive result X is Y" 机械定性开头（4处）

**Pattern:** 段首用 "The [抽象名词] between A and B is [定性形容词]." 的模板化方式引入机制分析，AI痕迹清晰。

**典型原文：**
- _ablation L114–115:  
  `The asymmetry between variants B and C at S1 is informative.`
- _ablation L130–133:  
  `The counterintuitive result that Variant D (no physics) outperforms baseline A on f₁* by 22.1% at S1 is visible in the task counts: D selects 14.7 tasks versus A's 11.1, yet the post hoc geometric quality of the two schedules is nearly identical (f₂ = 0.565 vs. 0.569, a difference of <1%).`
- _ablation L134–135:  
  `This near-identity of geometric quality despite the absence of physical objectives reinforces the geometric-coupling interpretation:`
- §6.4 L930–931:  
  `The contrast between envelope correlation and schedule correlation is stark.`

**Suggested rewrite direction:** 直接给出定量结果开头（如 "At S1, removing the incidence component [C] changes f₁* by +21.6% while removing squint [B] changes by −9.5%…"），删除 "is informative / is stark / reinforces the interpretation" 的定性帽子。

---

### [#8] [MEDIUM RISK] Transition Smoothing — 模板化未来工作 "remains an open question / is left to future work / awaits verification"（4处）

**Pattern:** 高频重复出现未来工作模板，尤其在 §4.1、§7.4 集中出现。人类论文的 future work 通常 1–2 句或并入 Limitations 结尾。

**典型原文：**
- §4.1 Solver Overview (L482–484):  
  `A comparison across algorithmic families (e.g., NSGA-III vs. MOEA/D (decomposition-based) vs. SMS-EMOA (hypervolume-based)) is left to future work (§7.4).`
- §7.4 Limitations (L1116–1125):  
  `whether the MOEA can independently discover high-coverage solutions without greedy seeding remains an open question.`  
  `Similarly, the NSGA-III crowding-distance explanation for the S1 variant-D reversal (§6.5) awaits verification with alternative crowding operators.`  
  `Finally, we do not benchmark against learning-based schedulers (e.g., Chen 2025), which represent an alternative methodological family; a systematic comparison of physics-aware heuristic methods against data-driven approaches is left to future work.`

**Suggested rewrite direction:** 合并为 1 个 future work 段，用自然句式串联；移除 "awaits verification" 等被动模板。

---

### [#9] [MEDIUM RISK] Sentence Overclaims — 破折号（—）过度使用补充解释（≥15处）

**Pattern:** SKILL.md 约束 3 明确："尽量减少破折号（—）的使用，建议使用逗号、括号或从句结构替代。" 本文在长推导段（尤其 §6.4、_ablation、§7.4）中反复使用双破折号插入解释，密度很高。

**典型原文抽样：**
- §6.4 L925–928:  
  `The 3-objective redundancy is therefore an empirical convergence effect—not a mathematical identity between f₂ and f₃ but a consequence of solver convergence to low-squint regimes that narrows, without eliminating, the incidence-angle conflict.`
- §6.4 L942–945:  
  `The solver-selected schedules thus move the correlation toward zero—from −0.95 in the visibility envelope to ≈ −0.69 to −0.17 within the full-physics schedules—but do not reverse its sign: the incidence-angle conflict is narrowed by low-squint convergence, not eliminated.`
- _ablation L122–125:  
  `Variant B (no squint), by contrast, retains incidence-angle variation and achieves the opposite trade-off—improved coverage (Δf₁* = −9.5%, i.e., 9.5% above baseline A) at negligible quality cost.`
- §8 Conclusion L1152–1156:  
  `These findings establish an empirical saturation boundary for what physics-aware multi-objective scheduling can contribute to single-satellite SAR operations, and provide a baseline against which multi-satellite, multi-pass, and multi-mode extensions can be measured.`

**Suggested rewrite direction:** 把破折号插入内容改为括号注释、独立定语从句或同位语。

---

## OPTIONAL（可选/低风险，≥3 次才触发，按需改写）

### [#10] [OPTIONAL] Transition Smoothing — 显式 enumerate/description 列表环境使用（3处）

**Pattern:** SKILL.md 约束 2 "严禁使用列表格式：必须将所有的 item 内容转化为逻辑连贯的普通段落。" 但学术论文中贡献点、实验变体列表是惯例。触发但等级低，保留可选。

**典型原文：**
- §1 Contributions (L138–164): `\begin{enumerate}[nosep]` 2 条贡献
- §5.4 Experiment classes (L650–662): `The first is…The second is…The third comprises…`
- _ablation variants (L9–24): `\begin{description}` 4 条变体 A/B/C/D

**Suggested rewrite direction:** 贡献点列表建议保留（领域惯例）；变体描述可合并为段落；三类实验的显式宣告建议删除。

---

### [#11] [OPTIONAL] Sentence Overclaims — 正文中 `\textbf{}` 粗体强调结构小标题（3处）

**Pattern:** SKILL.md 约束 3 "禁用强调格式：严禁在正文中使用加粗或斜体进行强调。学术写作应通过句式结构来体现重点。" 本文 §6.4 把结构小标题用 `\textbf{}` 加粗嵌入正文段落，未使用 `\subsubsection*`。

**典型原文（§6.4 内嵌入段落中）：**
- L843: `\textbf{Phenomenon 1: Front compression.}`
- L872: `\textbf{Phenomenon 2: Three-objective redundancy.}`
- L879: `\textbf{Mechanism: geometric coupling and low-squint convergence.}`

**Suggested rewrite direction:** 改为 `\subsubsection*{Phenomenon 1}` 或直接以主题句开头，删除 `\textbf{}` 强调。

---

### [#12] [OPTIONAL] Transition Smoothing — "systematically" 副词过度修饰（8次）

**Pattern:** 作为大模型表达"严格/科学实验"的口头禅，反复附加在实验/场景前面。人类作者通常只在方法部分说明 1 次设计为 systemically varied，后续直接引用。

**典型原文：**
- "200 systematically varied scenarios"（≥5 次，跨 §1、§5、§7、§8）
- "systematic comparison"（2 次，§2、§7.4）
- "systematic characterization"（1 次，§1 贡献点 2）

**Suggested rewrite direction:** 保留在 §5 Experimental Setup 首次说明，后续全部删除副词，直接说 "200 scenarios"。

---

### [#13] [OPTIONAL] Transition Smoothing — 转折词 In contrast / Conversely / By contrast 密集使用（5处）

**Pattern:** 虽属标准学术转折，但在 60 页短文中以几乎相同的句首位置连续出现 ≥5 次，可视为轻度平滑化特征。

**典型原文：**
- §2.1 L203: `In contrast, SAR imaging quality varies continuously with acquisition geometry and is directly optimizable within the scheduling window.`
- _ablation L107–108: `Conversely, Variant D (no physics) improves apparent f₁* by −22.1% (p = 3.3 × 10⁻⁷) by selecting about one-third more tasks (14.7 vs. 11.1), while Variant B (no squint) yields a −9.5% change (p = 1.2 × 10⁻³).`
- _ablation L122: `Variant B (no squint), by contrast, retains incidence-angle variation and achieves the opposite trade-off—improved coverage (Δf₁* = −9.5%, i.e., 9.5% above baseline A) at negligible quality cost.`
- §7.2 中类似对比句

**Suggested rewrite direction:** 保留 1–2 处关键对比，其余用 however / though 嵌入从句或直接并列陈述。

---

### [#14] [OPTIONAL] Vocabulary Inflation — "reveal" 作为发现动词使用（3次，达到阈值）

**Pattern:** SKILL.md 高频词表同族词（unveil / delineate / reveal 是 AI 常用"揭示/揭露"大词）。虽然 reveal 不在 exact 词表内，但结合同族 AI 特征，3 次触发阈值。

**典型原文：**
- §6 导航 L748: `§6.4 reveals the geometric mechanism of Pareto compression`
- _ablation L100–103: `The ablation results (Table VII, Fig. 5) reveal that the influence of physical objective modeling is concentrated in sparse scenarios and vanishes as scenario density increases — a pattern consistent with our scale-sensitivity analysis (§6.3).`
- 另 1 处（§1/Limitations）：`reveal` 的同义变体

**Suggested rewrite direction:** 改为中性动词 show / indicate / find，或在章节导航处删除该动词直接列事实。

---

### [#15] [OPTIONAL] Vocabulary Inflation — "characterize / characterization" 作为总括动词使用（≥5次，接近阈值但语境合理）

**Pattern:** AI 论文常在摘要、贡献点反复使用 "We characterize X regime / provide a characterization of Y" 作为"我们做了系统研究"的占位表达。本文中虽使用较克制，但仍达到可选项级别。

**典型原文：**
- Abstract L37: `We characterize an empirical saturation regime for multi-objective SAR quality optimization…`
- §1 L140–141: `The discovery and analytical characterization of an empirical saturation regime…`
- 其他分散处

**Suggested rewrite direction:** 摘要处可保留（摘要需要一个总括动词），贡献点处改为 analysis 或直接改为发现陈述。

---

## 附录：Skipped Items（领域术语保护 / 格式保护）

| # | 候选模式 | 判定 | 理由 |
|---|---|---|---|
| S1 | "Integrate"（Abstract + Conclusion 各 1 次，见 AI 高频词表 Integrate） | **SKIPPED** | 在 SAR/工程领域 integrate = "整合/集成"是常规术语，并非为了形式上的高级感而堆砌 |
| S2 | 定量指标报告（p值、Cliff's δ、效应量、Friedman/Wilcoxon 检验说明在正文中直接列出） | **SKIPPED** | 这是定量研究论文核心结果呈现的标准格式，不属于 AI 过渡平滑 |
| S3 | 数学公式、符号定义、`\ref` 交叉引用、`tabular/booktabs` 表格环境 | **SKIPPED** | LaTeX 学术论文标准结构，非语言类 AI 模式 |
| S4 | "empirical"（全文 ≈20 次） | **SKIPPED** | 领域核心术语（empirical study / regime / saturation / correlation），非 AI 滥用词汇 |

---

## 建议的 Phase 2 改写组合（给用户选择参考）

根据本报告的高/中风险集中度，建议 Phase 2 选择：
- **Fix all High Risk**（#1–#5，共 5 项）→ 去掉最显著的 AI 机械结构，预计降低检测分数 60–70%
- **Fix High + Medium**（#1–#9，共 9 项）→ 覆盖主要 AI 痕迹，适合直接投稿场景
- **Fix all**（#1–#15，共 15 项）→ 含可选项精细润色，适合顶刊要求严苛的语言审校
