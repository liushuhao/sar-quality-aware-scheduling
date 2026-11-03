# Peer Review Report

**Paper:** Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite: Balancing Profit, NESZ, and Geometric Resolution (small-paper-ijae.tex)
**Target Journal:** Advances in Space Research (ASR)
**Date:** 2026-08-02

## Scoring Overview

| Dimension | Score (1-10) | Justification |
|-----------|:---:|---------------|
| Novelty | 3 | Core "discovery" is a negative result (saturation + redundancy) that effectively falsifies the paper's own three-objective formulation; no positive methodological or algorithmic novelty beyond composing NSGA-III with existing SAR formulas. |
| Methodology | 2 | Ablation variant D (no physics) outperforms full-physics baseline at S1, exposing NSGA-III crowding as a destructive force; MOEA-3 ≈ MOEA-2 negates the decomposed-quality design; no comparison against Wei 2025 MONP / Kramer 2025 SARVis; no MILP validation on small instances. |
| Writing Quality | 5 | Prose is mechanically correct but structurally defensive: the paper buries its negative findings under verbose geometric-coupling commentary instead of stating upfront that the three-objective formulation provides no empirical benefit. |
| Presentation | 4 | Tables are readable but Table 2 (HV) is published despite author's own warning that per-solver pooling makes cross-solver HV incomparable; Fig. 4 legend hides that G-SM lies outside the MOEA-3 Pareto front—a damning observation that should be highlighted, not buried in a caption clause. |
| Significance | 3 | Operational guidance (N≲100 use MOEA-2, N≳300 use greedy) is weakly grounded: the +8.2% f₂ gain at S1 maps to an unverified pixel-size claim, while greedy "Pareto sufficiency" at N≥300 holds only because MOEAs collapse to greedy coverage under G-BL seeding. |

## Major Concerns

### Major Concern 1: Variant D (No Physics) Outperforms Full-Physics Baseline at S1 — NSGA-III Objective-Space Pathology

**Section:** Physical-Objective Ablation (Section 6.5, Table 3, variant D)

**Problem:** At S1 (N=20), variant D with constant f₂=f₃=1 achieves f₁* = 0.81 vs. baseline A's 0.66 — a 22.1% coverage improvement with post-hoc geometric quality nearly identical (0.565 vs. 0.569, <1% difference). The paper's structural explanation (NSGA-III crowding-distance sorting favors fewer-tasks / higher-per-task-quality solutions in three-objective space) is acknowledged but not remedied or externally verified.

**Why it matters:** This is a fatal result for the paper's framing. If *removing all physical content* produces strictly superior schedules on the paper's own primary metric (f₁*) with zero quality loss in the sparse regime where physical objectives are claimed to matter most, then the NSGA-III three-objective formulation is not merely "redundant" — it is actively harmful. The author's "structural explanation" (crowding distance) is a hypothesis, not a verified mechanism; without cross-validation against alternative diversity operators (e.g., SMS-EMOA hypervolume-based selection, MOEA/D decomposition), the paper has demonstrated only that its specific NSGA-III configuration misuses the additional objectives, not that physics-aware objectives in general have marginal value. This undermines every claim about "saturation" and "Pareto sufficiency" because the baseline solver itself is shown to be broken in the regime where the paper's positive claims reside.

**Suggestion:** Either (a) replicate the full ablation with at least one alternative MOEA paradigm (MOEA/D or SMS-EMOA) to separate algorithm-pathology effects from genuine geometric saturation, or (b) reframe the paper as a negative-result / algorithm-failure study and remove the "operational implications" section entirely, since no operational recommendation can be trusted when the recommended solver is provably outperformed by its own no-physics ablated variant.

> **[Chinese]**
> **问题：** 在 S1（N=20）密度下，令 f₂=f₃=1 的消融变体 D 获得 f₁* = 0.81，而完整物理基线 A 仅为 0.66——覆盖率提升 22.1%，同时事后计算的几何质量几乎无差异（0.565 对 0.569，差距 <1%）。论文给出的结构性解释（NSGA-III 的拥挤距离排序在三目标空间中偏向少任务、高单任务质量的解）仅为假设，未经验证。
>
> **为何重要：** 这是对论文整体框架的致命打击。如果在论文声称物理目标最具价值的稀疏场景下，*完全移除所有物理内容* 反而在论文自身的首要指标（f₁*）上产生严格更优的调度方案且零质量损失，那么 NSGA-III 三目标公式就不仅仅是"冗余"——它是**主动有害**的。作者的"结构性解释"（拥挤距离）只是一个假设而非已验证的机制；若不使用其他多样性维护算子（如 SMS-EMOA 的超体积选择、MOEA/D 的分解策略）进行交叉验证，论文只能证明其特定的 NSGA-III 配置错误利用了额外目标，而无法证明物理感知目标本身具有边际价值。这直接动摇了所有关于"饱和"和"帕累托充分性"的论断——因为当推荐求解器被其自身的无物理变体证伪时，没有任何结论可以被信任。
>
> **建议：** 要么（a）使用至少一种替代 MOEA 范式（MOEA/D 或 SMS-EMOA）重复全部消融实验，以分离算法病理效应与真正的几何饱和效应；要么（b）将论文重新定位为负面结果/算法失效研究，并完全删除"操作启示"章节——因为当被推荐的求解器被证明不如其无物理变体时，任何操作建议都是不可信的。

---

### Major Concern 2: The Three-Objective Formulation Is Falsified by Its Own Data — MOEA-2 ≈ MOEA-3 Across All Densities

**Section:** Mechanism of Pareto Compression (Section 6.4, Phenomenon 2; Table 1 solver profiles)

**Problem:** The paper's headline design—decomposing SAR quality into separate NESZ (f₃) and geometric (f₂) objectives within a three-objective NSGA-III—finds zero empirical support. Pooled across 200 scenarios, Cliff's δ between MOEA-2 and MOEA-3 is negligible for f₂ (+0.132) and small for f₃ (-0.176). Table 1 shows numerical identity at S3/S4: both MOEA-2 and MOEA-3 achieve f₂=0.587–0.589 and f₃=0.169–0.175, matching to the third decimal place. The author attributes this to "geometric coupling" and "low-squint convergence" rather than mathematical identity, but this distinction is operationally meaningless: if no solver or density can elicit a difference between the 2- and 3-objective formulations, then the third objective is not "empirically redundant" — it is a *design error*.

**Why it matters:** The paper's first stated contribution (§1, bullet 1) claims "analytical characterization of an empirical saturation regime... that renders the three-objective formulation redundant." This is not a contribution — it is a *self-refutation*. A valid negative-result paper would (i) test whether the redundancy persists across alternative solvers, (ii) characterize the precise boundary conditions under which f₂ and f₃ *do* separate (e.g., what minimum squint distribution or orbital configuration re-opens the trade-off), and (iii) not claim "operational implications" from a formulation that has been shown to be unnecessary. Instead, the paper uses 1,200 words of correlation analysis (r_null, envelope vs. schedule correlations, per-density correlation tables) to dress up a simple finding: "we added an objective and it didn't matter." This is neither sufficient for publication in ASR nor honest about the magnitude of the failure.

**Suggestion:** Either (i) add at least two experimental configurations where f₂ and f₃ *do* diverge (e.g., Spotlight/TOPS mode, wider squint envelope, multi-orbit scheduling) so that the three-objective formulation demonstrates at least one regime of non-redundancy, or (ii) remove MOEA-3 entirely and reposition the paper as a two-objective (coverage vs. composite-quality) study with the redundancy finding relegated to a one-paragraph "preliminary negative result" note rather than the central contribution.

> **[Chinese]**
> **问题：** 论文的核心设计——在三目标 NSGA-III 中将 SAR 质量分解为独立的 NESZ（f₃）和几何质量（f₂）目标——没有获得任何实证支持。在全部 200 个场景的聚合中，MOEA-2 与 MOEA-3 的 Cliff's δ 值：f₂ 为可忽略的 +0.132，f₃ 为小效应的 -0.176。表 1 显示在 S3/S4 密度下两者数值完全等同：MOEA-2 和 MOEA-3 的 f₂ 均为 0.587–0.589，f₃ 均为 0.169–0.175，精确到小数点后三位一致。作者将此归因于"几何耦合"和"低斜视收敛"而非数学等价，但这种区分在操作层面毫无意义：如果没有任何求解器或密度级别能触发 2 目标与 3 目标公式的差异，那么第三个目标就不是"经验上冗余"——它是一个**设计错误**。
>
> **为何重要：** 论文声明的第一项贡献（§1 第 1 条）声称"解析刻画了一种经验饱和域……使得三目标公式冗余"。这不是贡献——这是**自我证伪**。一篇合格的负面结果论文应当：(i) 测试冗余性是否在其他求解器上同样成立；(ii) 精确刻画 f₂ 与 f₃ *确实会分离* 的边界条件（例如，何种最小斜视分布或轨道配置会重新打开权衡空间）；(iii) 不会从一个已被证明不必要的公式中推导出"操作启示"。然而，本论文用 1,200 余词的相关性分析（r_null、包络与调度对比、密度分级相关系数表）来包装一个简单的发现："我们加了一个目标，结果没什么用。"这既达不到 ASR 的发表标准，也没有诚实地反映失效的严重程度。
>
> **建议：** 要么（i）增加至少两种 f₂ 与 f₃ 确实会分化的实验配置（如聚光灯/TOPS 成像模式、更宽的斜视包络、多轨道调度），使得三目标公式至少在一个场景域内展现非冗余性；要么（ii）完全删除 MOEA-3，将论文重新定位为两目标（覆盖率 vs. 合成质量）研究，并将冗余性发现降格为一段"初步负面结果"注释而非核心贡献。

---

### Major Concern 3: Hot-Start Dependence Invalidates Coverage Convergence Claims — MOEAs Cannot Independently Find High-Coverage Solutions

**Section:** Robustness and Calibration (§6.6, Hot-start dependence; Table 1 coverage values)

**Problem:** Random-initialized MOEA-2 yields f₁* deficits of -0.20 (S1), -0.43 (S2), -0.46 (S3), -0.33 (S4) relative to G-BL-seeded MOEA-2. The S3 deficit of -0.46 means that without the greedy anchor, MOEA-2 achieves only ~50% of the seeded coverage — this is not a "calibration detail" but a demonstration that the evolutionary algorithm, on its own, fails catastrophically at the problem's primary objective. Critically, the hot-start sample size is grossly inadequate: "10 S1, 4 S2, 5 S3, 5 S4 scenarios" — 24 scenarios out of 200 (12%) — with no statistical comparison (no p-values, no effect sizes) between random-init and hot-start populations.

**Why it matters:** The paper's Discussion section (§7.1) coins the term "Pareto-sufficient" and concludes that at N≥300, "the greedy baseline is operationally sufficient" because MOEA coverage approaches G-BL. But G-BL "approach" is an artifact of initialization: the MOEA isn't learning coverage, it is being spoon-fed the G-BL solution in its first generation and then barely deviating from it. The correct interpretation of the S3/S4 results is not "greedy is Pareto-sufficient" — it is "NSGA-III with G-BL seeding cannot significantly improve upon the greedy solution within 200 generations because the seeding anchor dominates convergence." This is a fundamentally different claim, and it removes any justification for using NSGA-III at all if the only thing it does is converge back to the greedy baseline it was started from. For ASR readers who actually implement satellite operations, this distinction is the difference between deploying a sophisticated MOEA pipeline and running a 5-millisecond greedy heuristic.

**Suggestion:** Run the full 200-scenario main experiment with random initialization (no G-BL hot-start) for all evolutionary solvers (GA-P-BL, MOEA-2, MOEA-3) and all ablation variants. If the coverage deficit persists at the reported -0.20 to -0.46 scale, rewrite the Discussion to state clearly that (a) all positive MOEA results are initialization-dependent, (b) independent MOEA performance is severely degraded, and (c) the "saturation" and "redundancy" findings apply only to G-BL-initialized NSGA-III, not to multi-objective scheduling as a general paradigm.

> **[Chinese]**
> **问题：** 随机初始化的 MOEA-2 相对于 G-BL 热启动的 MOEA-2，在 f₁* 上的缺口分别为：S1 为 -0.20、S2 为 -0.43、S3 为 -0.46、S4 为 -0.33。S3 的 -0.46 缺口意味着，若没有贪婪锚点，MOEA-2 仅能达到热启动覆盖率的约 50%——这不是"校准细节"，而是证明进化算法本身在首要目标上**完全失效**。更严重的是，热启动对照的样本量严重不足：仅使用了"10 个 S1、4 个 S2、5 个 S3、5 个 S4 场景"——200 个场景中的 24 个（占 12%），且随机初始化与热启动种群之间未提供任何统计比较（无 p 值、无效应量）。
>
> **为何重要：** 论文讨论章（§7.1）提出了"帕累托充分性"的概念，并得出结论：在 N≥300 时，"贪婪基线在操作上已充分"，因为 MOEA 的覆盖率趋近 G-BL。但这种"趋近 G-BL"纯粹是初始化的人为现象：MOEA 并没有"学会"如何实现高覆盖率——它是在第一代就被喂食了 G-BL 解，然后几乎不敢偏离它。S3/S4 结果的正确解读，不是"贪婪方法具有帕累托充分性"——而是"带有 G-BL 种子的 NSGA-III 在 200 代内无法显著超越贪婪解，因为种子锚点主导了收敛"。这是一个性质完全不同的论断，它彻底移除了使用 NSGA-III 的一切合理性：如果它做的唯一事情就是收敛回它被给定的贪婪起点，那为什么不直接运行贪婪启发式呢？对于 ASR 中真正从事卫星操作工程的读者来说，这一区别意味着是部署一套复杂的 MOEA 流水线还是运行一个 5 毫秒的贪婪启发式——天壤之别。
>
> **建议：** 对所有进化求解器（GA-P-BL、MOEA-2、MOEA-3）及全部消融变体，使用随机初始化（无 G-BL 热启动）完整运行 200 个场景的主实验。如果覆盖率缺口仍维持在报告的 -0.20 至 -0.46 量级，请重写讨论章，明确声明：(a) 所有正面的 MOEA 结果均依赖于初始化；(b) MOEA 的独立表现严重退化；(c) "饱和"与"冗余"发现仅适用于 G-BL 初始化的 NSGA-III，不适用于多目标调度作为一般范式。

---

### Major Concern 4: Missing Baseline Comparisons Against Directly Cited Competitors (Wei 2025 MONP, Kramer 2025 SARVis) and Exact MILP Solvers

**Section:** Solver Overview (§4.1); Experimental Setup (§5)

**Problem:** The paper positions itself against two very close prior works: Wei et al. 2025 ("MONP: neural-policy-guided MOEA with composite image quality") and Kramer et al. 2025 ("SAR constellation scheduling with weighted visibility-performance composite embedding a SAR-quality proxy"). The author explicitly distinguishes the present formulation from both in the introduction's contribution bullet 2, claiming decomposition superiority over these scalar composites. Yet neither Wei 2025 nor Kramer 2025 are implemented or empirically compared even on a single scenario. There is also no small-instance MILP validation (the author notes in §3 that the problem is NP-hard via Orienteering reduction but never checks whether Gurobi/CPLEX can solve instances with N=20 or N=50 to optimality as an upper bound).

**Why it matters:** For ASR readers, the question is not "is NSGA-III better than a greedy heuristic I can write in an afternoon" — it is "should I use this method instead of the 2025 methods I read about in last month's issue?" By deliberately avoiding comparison to the only two SAR-scheduling papers that also use physical quality objectives, the paper has no external validity. The internal five-way comparison (G-BL, G-SM, GA-P-BL, MOEA-2, MOEA-3) is a comparison against homemade baselines, all produced by the same author with the same codebase. There is no way to know whether Wei's MONP or Kramer's composite would dominate all five solvers in the comparison set or whether they would exhibit the same "saturation" behavior — meaning the paper's entire saturation thesis is bounded to a single solver family written by one person. The missing MILP upper bound is equally damaging: without knowing what optimal f₁* is at S1, we cannot evaluate whether the greedy baseline is "good" (say 95% of optimal) or "mediocre" (60% of optimal); the entire NSGA-III vs. greedy framing could be an argument among suboptimal solvers.

**Suggestion:** (1) Replicate at least the core experiment (S1-S4, 50 scenarios each) against a re-implementation or author-shared version of Wei 2025 MONP; if code is unavailable, implement a reasonable facsimile of the Kramer 2025 weighted visibility--quality composite as a competing scheduler. (2) Run a commercial MILP solver (Gurobi or CPLEX) on the N=20 and N=100 scenario classes with a time limit of 30 minutes per instance to provide provable optimality gaps for at least the sparse-regime baselines. Add a column "MILP gap" to Table 1 for S1 and S2.

> **[Chinese]**
> **问题：** 论文将自己与两篇最相近的前期工作直接对立：Wei 等人 2025（"MONP：带合成图像质量的神经策略引导 MOEA"）和 Kramer 等人 2025（"带加权可见性-性能合成指标并嵌入 SAR 质量代理的 SAR 星座调度"）。作者在引言贡献第 2 条中明确将本论文的公式与上述两者区分，声称分解式方法优于它们的标量合成形式。然而，Wei 2025 和 Kramer 2025 均未被实现，甚至未在一个场景上进行经验对比。同时，论文也没有提供小实例 MILP 验证——作者在 §3 中指出该问题可通过定向问题归约证明为 NP 难，但从未验证 Gurobi/CPLEX 能否在 N=20 或 N=50 的实例上求到最优解作为上界参照。
>
> **为何重要：** 对于 ASR 读者而言，真正的问题不是"NSGA-III 是否比我一个下午就能写出来的贪婪启发式更好"——而是"我是否应该用这个方法，替代我上个月刚读到的 2025 年方法？"论文刻意回避了与仅有的两篇同样使用物理质量目标的 SAR 调度论文的对比，因此不具备任何外部有效性。论文内部的五维对比（G-BL、G-SM、GA-P-BL、MOEA-2、MOEA-3）本质上是与自制基线的比较，全部由同一作者在同一代码库中实现。我们无法知道 Wei 的 MONP 或 Kramer 的合成指标是否会全面碾压这五个求解器，也无法知道它们是否会展现相同的"饱和"行为——这意味着论文的整个饱和命题，仅限于由一个人编写的单一求解器家族。缺失 MILP 上界同样致命：若不知道 S1 下最优 f₁* 是多少，我们就无法判断贪婪基线是"优秀"（例如达到最优的 95%）还是"平庸"（仅 60%）；整个 NSGA-III 与贪婪的比较，可能只是一群次优求解器之间的内讧。
>
> **建议：** (1) 至少在核心实验（S1-S4，每类 50 场景）上对比 Wei 2025 MONP 的复现版或作者共享版本；若代码不可获取，请实现 Kramer 2025 加权可见性-质量合成指标的合理近似作为竞争调度器。(2) 在 N=20 和 N=100 场景集上使用商业 MILP 求解器（Gurobi 或 CPLEX），单实例时限 30 分钟，至少在稀疏域为基线提供可证明的最优性差距。在表 1 中为 S1 和 S2 增加"MILP 差距"列。

---

### Major Concern 5: The +8.2% f₂ Gain Operational Claim Is Unverified — No Pixel-Size or Task-Utility Mapping

**Section:** Operational Implications (§7.2); Scale Sensitivity (§6.3, Table 2)

**Problem:** The operational implications section makes a concrete domain claim: an 8.2% f₂ improvement at S1 "can distinguish small vessel classes that fall within the same pixel at baseline resolution (~0.3 m at C-band)." This is a critical bridging claim between abstract quality-index optimization and real ASR-domain relevance — yet it is supported by zero evidence. f₂ is defined as sinθ·cosψ_sq (Eq. 2); there is no mapping from Δf₂ = +0.044 (0.585 vs. 0.541) to actual ground-range and azimuth pixel dimensions in meters. The 0.3 m figure is fabricated out of whole cloth: with the paper's stated parameters (C-band bandwidth B=56.5 MHz, antenna D=12.3 m), ground-range resolution at θ=30° is ρ_rg ≈ c/(2B·sinθ) ≈ 2.998e8/(2·56.5e6·0.5) ≈ 5.3 m, not sub-meter. Even an 8.2% improvement yields only ~4.9 m — two orders of magnitude off the "small vessel class distinction" claim.

**Why it matters:** This is not a harmless exaggeration — it is the only sentence in the entire paper that connects the abstract f₂ index to ASR's readership of remote-sensing scientists and mission planners. If the pixel-size arithmetic is wrong, then the paper's single link to domain relevance collapses. Worse, the claim misrepresents what f₂ actually measures: f₂ is a dimensionless product of trigonometric terms that is proportional to (1 / (ρ_rg · ρ_az)), but absolute pixel area also depends on platform constants (B, D) that cancel out in the normalized index. Two schedules with identical f₂ can have wildly different absolute pixel areas if they use different incidence angles (because sinθ appears in both numerator and denominator when back-calculating). By skipping the conversion and pulling a 0.3 m number out of the air, the author has effectively fabricated the one domain-relevant result that the ASR reviewer is actually looking for.

**Suggestion:** Delete the fabricated 0.3 m claim. Compute actual per-schedule ground-range and azimuth pixel dimensions in meters using the paper's stated platform parameters (B=56.5 MHz, D=12.3 m) for G-BL, MOEA-2, and MOEA-3 at each density level. Report mean and standard deviation of ρ_rg and ρ_az alongside f₂, and state the actual absolute pixel-area improvement in percent and m². If the improvement is indeed only ~0.4 m (5.3 m → 4.9 m), then describe the operational implication honestly: "for a 5 m class vessel, this reduces the pixel fraction occupied by the target by roughly 8%, marginally improving detection confidence in single-look imagery but not crossing any classification threshold."

> **[Chinese]**
> **问题：** 操作启示章节提出了一个具体的领域声明：S1 密度下 f₂ +8.2% 的改善"可以在基线分辨率下区分落入同一像素的小型船只类别（C 波段下约 0.3 米）"。这是连接抽象质量指标优化与 ASR 领域实际价值的关键性桥接断言——但没有任何证据支撑。f₂ 被定义为 sinθ·cosψ_sq（式 2）；论文从未提供从 Δf₂ = +0.044（0.585 对比 0.541）到实际米级地面距离分辨率和方位向像素尺寸的映射。0.3 米这个数字纯属虚构：根据论文给出的参数（C 波段带宽 B=56.5 MHz，天线长度 D=12.3 m），θ=30° 时地面距离分辨率为 ρ_rg ≈ c/(2B·sinθ) ≈ 2.998e8/(2·56.5e6·0.5) ≈ 5.3 米，而非亚米级。即使改善 8.2%，也仅约 4.9 米——与"小型船只类别区分"的断言相差两个数量级。
>
> **为何重要：** 这不是无害的夸张——这是整篇论文中唯一将抽象 f₂ 指标与 ASR 目标读者群体（遥感科学家和任务规划人员）实际关切联系起来的句子。如果像素尺寸算术错误，那么论文唯一与领域相关性的桥梁就崩塌了。更严重的是，该断言歪曲了 f₂ 的实际含义：f₂ 是一个与 1/(ρ_rg·ρ_az) 成正比的无量纲三角函数乘积，但绝对像素面积还取决于平台常数（B、D），这些常数在归一化指标中被约去了。具有相同 f₂ 的两个调度方案，如果使用不同的入射角，可能具有差异极大的绝对像素面积（因为 sinθ 在反推计算中同时出现在分子和分母）。作者跳过了换算，凭空编造了一个 0.3 米的数字，这实质上伪造了 ASR 审稿人真正关注的唯一领域相关结果。
>
> **建议：** 删除编造的 0.3 米断言。使用论文声明的平台参数（B=56.5 MHz，D=12.3 m），按密度级别为 G-BL、MOEA-2、MOEA-3 计算每个调度方案的实际米级地面距离分辨率和方位向像素尺寸。在 f₂ 之外同时报告 ρ_rg 和 ρ_az 的均值和标准差，并给出实际绝对像素面积的百分比改善量及 m² 绝对值。如果改善确实仅约 0.4 米（5.3 m → 4.9 m），请诚实描述操作含义："对于 5 米级船只，这将使目标在像素中所占比例减少约 8%，在单视成像中略微提升检测置信度，但不足以跨越任何细分类别阈值。"

## Minor Concerns

### Minor Concern 1: Hypervolume Table (Table 2) Is Published Despite Self-Acknowledged Incomparability

**Section:** Overall Solver Performance (§6.1, Table 2)

**Problem:** Table 2 reports HV values for MOEA-3 (0.173), MOEA-2 (0.169), and G-BL (0.140) as if they were comparable. Yet §5.3 explicitly states: "per-solver-pooled min–max normalization... means that the normalization basis differs across solvers; cross-solver HV comparisons should therefore be interpreted as relative rankings within a shared normalization framework rather than absolute cardinal differences." This wording is mealymouthed — the HV values are not "relative rankings"; they are computed in *different normalized spaces* and are therefore mathematically incomparable. Publishing a ranked table while warning the reader not to compare it is contradictory and creates a high risk that readers will cite the MOEA-3 > MOEA-2 > G-BL HV order as a genuine finding.

**Why it matters:** Misleading or contradictory data presentation is a persistent issue in applied MOEA papers, and ASR reviewers are right to police it. Table 2 invites readers to draw a false conclusion, and the caveat in §5.3 is insufficient to correct the damage.

**Suggestion:** Either remove Table 2 entirely and replace it with a statement that "HV is not comparable across solvers due to differing normalization bases, and is therefore reported only in the online supplement for individual within-solver diagnostic use," or recompute HV with a single, all-solver-pooled normalization reference set — and if this collapses single-solver HV values to degenerate numbers, explain why and keep the table with a clear explanation rather than a deceptive ranking.

> **[Chinese]**
> **问题：** 表 2 报告了 MOEA-3（0.173）、MOEA-2（0.169）和 G-BL（0.140）的 HV 值，仿佛它们具有可比性。然而 §5.3 明确写道："各求解器独立池化的最小-最大归一化……意味着各求解器的归一化基不同；因此跨求解器 HV 比较应被解释为共享归一化框架内的相对排序，而非绝对基数差异。"这段措辞过于含糊——HV 值不是"相对排序"；它们在**完全不同的归一化空间**中计算，因此在数学上**不可比较**。发布一个带有排序暗示的表格，同时警告读者不要进行比较，这是自相矛盾的，极易导致读者将 MOEA-3 > MOEA-2 > G-BL 的 HV 排名当作真实发现加以引用。
>
> **为何重要：** 误导性或自相矛盾的数据呈现是 MOEA 应用论文中的痼疾，ASR 审稿人有责任予以制止。表 2 引诱读者得出错误结论，而 §5.3 中的免责声明不足以抵消其危害。
>
> **建议：** 要么完全删除表 2，替换为如下声明："由于各求解器的归一化基准不同，HV 不可跨求解器比较，因此仅在在线补充材料中报告，用于求解器内部的诊断参考"；要么使用**所有求解器统一池化**的单一归一化参考集重新计算 HV——如果这样做导致单求解器 HV 值退化为无意义数值，请保留表格并明确解释原因，而不是给出具有欺骗性的排名。

---

### Minor Concern 2: GA-P-BL's Dominance on Coverage Is Underanalyzed — It Should Be the Reference Solver, Not G-BL

**Section:** Solver Profiles (Table 1, all density classes); Overall Performance (§6.1)

**Problem:** GA-P-BL achieves the highest f₁* at every density level: 1.09 (S1), 1.28 (S2), 1.15 (S3), 1.17 (S4) — consistently outperforming both G-BL (1.00 by definition) and the MOEA variants (0.66–0.98). Yet the entire paper normalizes f₁* against G-BL, not against the best-performing single-objective solver. The author's justification in §3.2 ("Normalization by G-BL rather than GA-P-BL is conservative for the MOEA coverage deficit") is the wrong framing: if the question is "what does adding physical quality objectives cost in coverage terms?" then the correct denominator is the best available coverage-only solver, not the simplest. Using G-BL systematically understates the MOEA coverage penalty by 9–28 percentage points.

**Why it matters:** The scale-sensitivity midpoint N₅₀ ≈ 140 was computed by logistic regression against G-BL-normalized f₁* deficits. If GA-P-BL were used instead, the "deficit" at every density would grow substantially, shifting N₅₀ dramatically. The entire operational guideline ("N≲100 use MOEA-2, N≳300 use greedy") is indexed to an artificially weak reference point.

**Suggestion:** Add a supplementary normalization of f₁* against GA-P-BL in all tables and figures (add f₁** = f₁ / f₁^GA-P-BL as a sixth column to Table 1). Recompute the N₅₀ logistic regression using this GA-P-BL-normalized deficit. Report both numbers, and justify the choice of reference solver in operational terms — for a mission planner comparing candidate schedulers, the true opportunity cost is vs. the best available coverage solver, not vs. a greedy baseline.

> **[Chinese]**
> **问题：** GA-P-BL 在所有密度级别上均获得最高的 f₁* 值：S1 为 1.09、S2 为 1.28、S3 为 1.15、S4 为 1.17——始终优于 G-BL（定义为 1.00）和所有 MOEA 变体（0.66–0.98）。然而整篇论文均以 G-BL 而非表现最佳的单目标求解器作为 f₁* 的归一化基准。作者在 §3.2 中的辩解（"使用 G-BL 而非 GA-P-BL 归一化，对 MOEA 的覆盖率缺口来说是保守的"）采用了错误的框架：如果问题是"增加物理质量目标在覆盖率方面的代价是什么"，那么正确的分母应当是可用的最优纯覆盖率求解器，而非最简单的那个。使用 G-BL 系统性地将 MOEA 的覆盖率惩罚低估了 9–28 个百分点。
>
> **为何重要：** 尺度敏感性转折点 N₅₀ ≈ 140 是通过对 G-BL 归一化的 f₁* 缺口做逻辑回归得到的。如果改用 GA-P-BL，每个密度级的"缺口"都会显著扩大，N₅₀ 也会大幅偏移。整个操作指引（"N≲100 使用 MOEA-2，N≳300 使用贪婪法"）都是建立在一个人为弱化的参考点之上的。
>
> **建议：** 在所有表格和图中增加一组以 GA-P-BL 为基准的 f₁* 补充归一化结果（在表 1 中增加第 6 列 f₁** = f₁ / f₁^GA-P-BL）。使用 GA-P-BL 归一化的缺口重新计算 N₅₀ 逻辑回归。同时报告两组数字，并从操作角度论证参考求解器的选择——对于在候选调度器之间进行权衡的任务规划人员而言，真正的机会成本是相对于最好的覆盖率求解器，而非相对于一个简单的贪婪基线。

---

### Minor Concern 3: Scenario Distribution Analysis Is Missing — 3 Distribution Types Aggregated Without Differentiation

**Section:** Scenario Design (§5.1)

**Problem:** §5.1 states that each scenario class uses three distribution types (uniform random, 5-cluster clustered, half-uniform/half-clustered mixed) with 5 distribution-seed combinations × 10 random seeds = 50 scenarios per class. Yet no results are ever disaggregated by distribution type. The scale-sensitivity, ablation, and Pareto-compression analyses all pool the 50 scenarios in each class without reporting whether uniform vs. clustered scenarios exhibit different saturation behavior, different N₅₀ midpoints, or different MOEA-2 vs. MOEA-3 separations.

**Why it matters:** Target clustering is arguably the most operationally relevant scenario parameter — real mission planning rarely encounters uniform random targets; it encounters clusters (disaster response, concentrated maritime traffic, military formations). If the 5-cluster scenarios drive all of the reported 8.2% S1 f₂ gain while uniform scenarios show 0% gain, then the operational implication changes entirely. The author has the disaggregated data and simply chose not to report it.

**Suggestion:** Add a supplementary breakdown table or paneled figure showing, per density class, the key metrics (f₁* MOEA-2 deficit vs. G-BL, f₂ gain, ablation variant D vs. baseline A) separated by distribution type: uniform, clustered, mixed. If clustering does not materially change any finding, say so explicitly and report the Cliff's δ between distribution types. If it does, the operational implications section must be rewritten to condition guidance on target clustering as well as target density.

> **[Chinese]**
> **问题：** §5.1 说明每个场景类别使用三种目标分布类型（均匀随机、5 聚类、半均匀半聚类混合），共 5 种分布-种子组合 × 10 个随机种子 = 每类 50 个场景。然而论文从未按分布类型拆分结果。尺度敏感性、消融实验、帕累托压缩分析，全部将每类 50 个场景池化，未报告均匀分布与聚类分布的场景是否展现不同的饱和行为、不同的 N₅₀ 转折点，或不同的 MOEA-2 与 MOEA-3 分离度。
>
> **为何重要：** 目标聚类可以说是操作层面最具相关性的场景参数——真实任务规划中很少遇到均匀随机目标；实际遇到的都是成簇目标（灾害响应、集中海上交通、军事编队）。如果 5 聚类场景贡献了报告中全部的 8.2% S1 f₂ 增益，而均匀场景的增益为 0%，则操作启示将完全改变。作者手中握有拆分后的数据，只是选择不报告。
>
> **建议：** 增加一个补充拆分表格或分图，按密度类别对关键指标（MOEA-2 相对 G-BL 的 f₁* 缺口、f₂ 增益、消融变体 D 相对基线 A 的表现）按分布类型拆分：均匀、聚类、混合。如果聚类不实质改变任何结论，请明确说明并报告分布类型间的 Cliff's δ。如果确实有差异，操作启示章节必须被重写，使操作建议同时取决于目标聚类程度和目标密度。

---

### Minor Concern 4: Inadequate Statistical Reporting for Key Hot-Start and Perturbation-Sensitivity Controls

**Section:** Robustness and Calibration (§6.6)

**Problem:** All four robustness controls use ad-hoc, underpowered sample sizes with no inferential statistics. Hot-start dependence: 24 scenarios out of 200 (12%), no p-values, no effect sizes — just mean deficit numbers. Perturbation sensitivity: 10 S3 scenarios × 3 seeds per σ value = 30 runs per σ, pooled into a single statement that f₂ changes by <0.002, with no statistical test of whether the σ=0.1 and σ=0.7 distributions differ. Random-search calibration: 5 S1 scenarios × 5,000 random draws — fine for coverage, but the author uses this to claim "MOEA's gains reflect structured search rather than luck" without comparing the *f₂* distribution of random search to MOEA-2's f₂ distribution, which is the dimension where structured quality search should be detectable. Search-budget control: 5 S3 + 5 S4 scenarios, 10 total, with Δf₁* = -0.005 at S3 and +0.002 at S4 reported without standard errors or confidence intervals.

**Why it matters:** §5.3 sets up a rigorous statistical framework (Friedman test, Wilcoxon signed-rank with Bonferroni α=0.005, Cliff's δ effect sizes) and applies it diligently to the 200-scenario main experiment. The robustness controls then abandon this framework entirely. A skeptical reader cannot distinguish "the effect is genuinely zero" from "the sample size is too small to detect it." Given that these controls are the only defense against the severe confounds identified in Major Concerns 1 and 3, their statistical weakness materially undermines the paper's central claims.

**Suggestion:** Either (a) expand all four robustness controls to match the main experiment's statistical framework: run perturbation sensitivity on all 200 scenarios, expand search-budget control to 50 per class, expand random-init hot-start to all 200 scenarios, and report full Wilcoxon + Cliff's δ tables for every comparison; or (b) reduce the §5.3 statistical framework to match what is actually done consistently, and explicitly label the robustness controls as "pilot diagnostics with small samples" rather than rigorous validations.

> **[Chinese]**
> **问题：** 四个鲁棒性对照实验均使用临时的、统计功效不足的样本量，且未提供推断统计。热启动依赖性：200 场景中仅 24 个（12%），无 p 值、无效应量——仅报告均值缺口数字。扰动敏感性：10 个 S3 场景 × 每 σ 3 个种子 = 每 σ 30 次运行，仅汇总为 f₂ 变化 <0.002 的一句话，未对 σ=0.1 和 σ=0.7 的分布是否差异做任何统计检验。随机搜索校准：5 个 S1 场景 × 5,000 次随机采样——对覆盖率而言尚可，但作者据此声称"MOEA 的增益反映结构化搜索而非运气"，却未比较随机搜索的 f₂ 分布与 MOEA-2 的 f₂ 分布——这恰恰是应能检测到结构化质量搜索的维度。搜索预算对照：5 个 S3 + 5 个 S4 场景，共 10 个，报告 S3 的 Δf₁* = -0.005 和 S4 的 +0.002，未附带标准误或置信区间。
>
> **为何重要：** §5.3 建立了严格的统计框架（Friedman 检验、Bonferroni α=0.005 的 Wilcoxon 符号秩检验、Cliff's δ 效应量），并在 200 场景主实验中勤勉应用。然而鲁棒性对照实验完全抛弃了这一框架。持怀疑态度的读者无法区分"效应值确实为零"与"样本量太小检测不到"。鉴于这些对照实验是针对主要问题 1 和 3 中所指出的严重混淆因素的唯一辩护，其统计薄弱性实质上削弱了论文的核心主张。
>
> **建议：** 要么（a）扩大全部四个鲁棒性对照实验，使其与主实验的统计框架保持一致：在全部 200 场景上运行扰动敏感性分析，将搜索预算对照扩展至每类 50 场景，将随机初始化热启动测试扩展至全部 200 场景，并对每一组对比报告完整的 Wilcoxon 检验和 Cliff's δ 表；要么（b）降低 §5.3 的统计框架，使其与实际一致执行的水平相符，并将鲁棒性对照明确标记为"小样本预研诊断"，而非严格的验证结论。

## Questions for Authors

1. **Q1.** At S1, variant D (no physics) outperforms baseline A on f₁* by 22.1% with <1% post-hoc f₂ loss. You attribute this to NSGA-III crowding-distance pathology. Have you tested whether a different diversity operator (e.g., ε-dominance, SMS-EMOA hypervolume indicator selection, or simply removing crowding distance in favor of random tie-breaking) eliminates the D-vs-A reversal? If not, what evidence supports that this is a crowding-distance artifact rather than a general property that all MOEAs will perform worse when given the decomposed physical objectives?
   > **[Chinese]** **Q1.** 在 S1 密度下，无物理变体 D 在 f₁* 上超越完整物理基线 A 达 22.1%，而事后 f₂ 损失 <1%。您将此归因于 NSGA-III 的拥挤距离机制缺陷。请问您是否测试过其他多样性维护算子（如 ε-占优、SMS-EMOA 的超体积指标选择，或直接用随机平局打破替代拥挤距离）可以消除 D 与 A 的反转？如果没有，请问有何证据表明这只是拥挤距离的人为副作用，而非所有 MOEA 在使用分解式物理目标时都会表现更差的普遍属性？

2. **Q2.** You assert (§7.1) that "solver outcomes become invariant to the choice of physical objectives at N ≥ 300" based on ablation. But this invariance holds only when all four ablation variants are G-BL hot-started. If you remove the hot-start (run all variants A–D with random initialization) at N=300, does the invariance persist? Specifically, does variant D (no physics) with random init still converge to the same f₁* and f₂ as variant A, or does the physical content begin to matter when the solver cannot rely on a greedy anchor?
   > **[Chinese]** **Q2.** 您在 §7.1 中基于消融实验断言"在 N≥300 时，求解器结果对物理目标的选择具有不变性"。但该不变性仅在全部四个消融变体均使用 G-BL 热启动时成立。如果在 N=300 时移除热启动（让变体 A–D 全部随机初始化），该不变性是否仍然成立？具体而言，无物理变体 D 在随机初始化下是否仍能收敛到与变体 A 相同的 f₁* 和 f₂？或者，当求解器无法依赖贪婪锚点时，物理内容是否开始发挥作用？

3. **Q3.** Table 1 shows G-SM occupies a region "outside the MOEA-3 Pareto surface" (§6.4 caption to Fig. 4). Why doesn't your NSGA-III population — which is seeded with G-BL and then evolved for 200 generations with crossover and mutation — ever discover the G-SM operating point? Is this a consequence of: (a) the G-BL seeding anchoring the population in a different basin, (b) the genetic operators being unable to mutate from G-BL-like schedules to G-SM-like schedules in 200 generations, or (c) the G-SM point being locally suboptimal with respect to small perturbations and therefore never retained by the environmental-selection operator? Which explanation do you favor, and what experiment would distinguish them?
   > **[Chinese]** **Q3.** 表 1 和图 4 说明 G-SM 位于"MOEA-3 帕累托面之外"（§6.4 图 4 说明）。请问为什么您的 NSGA-III 种群——虽然以 G-BL 为种子，但经过 200 代的交叉与变异——从未发现 G-SM 的工作点？这是因为：(a) G-BL 种子将种群锚定在了另一个盆地；(b) 遗传算子在 200 代内无法从类 G-BL 调度变异到类 G-SM 调度；还是 (c) G-SM 点相对于微小扰动是局部次优的，因而从未被环境选择算子保留？您倾向于哪一种解释，何种实验可以区分这三种假说？

4. **Q4.** You derive the null correlation r_null = -0.51 (Eq. 4) under the assumption that θ and ψ_sq are independent and uniform. But the real envelope correlation across visibility windows is -0.95 (§6.4, "Envelope versus schedule correlation"). You note the difference arises because real visibility geometry couples θ and ψ_sq through the LOS vector. Given that the real envelope is dominated by r ≈ -0.95 rather than r_null = -0.51, why do you spend more than two paragraphs analyzing the factorized null distribution when its magnitude bears no relation to the actual geometric coupling your solvers encounter? What operational insight does the r_null = -0.51 number provide that the empirically measured envelope correlation of -0.95 does not?
   > **[Chinese]** **Q4.** 您在 θ 和 ψ_sq 独立均匀的假设下推导出零相关系数 r_null = -0.51（式 4）。但实际可见性窗口上的真实包络相关系数为 -0.95（§6.4 "包络与调度相关系数"）。您指出差异源于真实可见性几何通过视线向量耦合了 θ 与 ψ_sq。鉴于真实包络的相关系数由 r ≈ -0.95 主导而非 r_null = -0.51，请问您为何用两个以上段落分析因子化的零分布，而其幅度与求解器实际遇到的几何耦合毫无关系？r_null = -0.51 这一数字提供了何种操作洞见，是经验测量得到的 -0.95 包络相关系数所不能提供的？

5. **Q5.** The Discussion (§7.2, "Operational Implications") recommends: for N ≲ 100 use MOEA-2 for geometric quality gains; for N ≳ 300 use greedy methods (G-SM or G-BL depending on priority). But GA-P-BL achieves the highest coverage at every density (f₁* = 1.09–1.28) while maintaining G-BL-equivalent f₂ quality. Why is GA-P-BL not mentioned anywhere in the operational guidance, and why should a mission planner deploy *any* MOEA variant (MOEA-2 or MOEA-3) when GA-P-BL strictly dominates them on coverage and matches or exceeds them on quality at every density level?
   > **[Chinese]** **Q5.** 讨论章 §7.2（操作启示）建议：N ≲ 100 时使用 MOEA-2 以获取几何质量增益；N ≳ 300 时使用贪婪方法（根据优先级选择 G-SM 或 G-BL）。但 GA-P-BL 在所有密度级别上均取得最高覆盖率（f₁* = 1.09–1.28），同时保持与 G-BL 相当的 f₂ 质量。请问为什么 GA-P-BL 在操作指南中完全未被提及？当 GA-P-BL 在覆盖率上严格主导所有 MOEA 变体，且在每个密度级别上的质量与它们相当或更优时，任务规划人员有何理由部署任何 MOEA 变体（MOEA-2 或 MOEA-3）？

6. **Q6.** You use a fixed C-band platform abstraction with D=12.3 m, B=56.5 MHz, incidence range [18°, 47°], and maximum squint 45°. These parameters (especially the wide incidence range combined with a Stripmap-only restriction) determine the geometric-coupling strength. If you shrink the incidence envelope to [25°, 35°] (narrow-swath high-precision Stripmap) or widen the maximum squint to 60° (super-agile platform), does the MOEA-2 vs. MOEA-3 redundancy break down? Have you done any sensitivity analysis on platform parameters, and if so, what minimum envelope width reintroduces measurable f₂–f₃ divergence?
   > **[Chinese]** **Q6.** 您使用了固定的 C 波段平台抽象：D=12.3 m、B=56.5 MHz、入射角范围 [18°, 47°]、最大斜视 45°。这些参数（尤其是宽入射角范围结合仅 Stripmap 模式的限制）直接决定了几何耦合强度。如果将入射角包络缩小至 [25°, 35°]（窄幅高精度 Stripmap），或把最大斜视扩大至 60°（超敏捷平台），MOEA-2 与 MOEA-3 的冗余性是否会被打破？您是否对平台参数做过敏感性分析？若有，请问多大的包络宽度阈值会重新引入可测量的 f₂–f₃ 分化？

## Verdict

**Recommendation:** Reject

This paper contains an internally consistent negative result — that under G-BL-seeded NSGA-III with a single-satellite single-pass Stripmap C-band configuration, the decomposed three-objective formulation collapses to the two-objective one and the marginal value of physical quality objectives saturates beyond N ≈ 300 targets — but several severe flaws prevent it from being publishable in ASR in its current form. The most damaging are: (1) ablation variant D (no physics) strictly outperforms the full-physics baseline in the sparse regime where physical objectives are claimed to matter, exposing the NSGA-III formulation as actively counterproductive; (2) all MOEA coverage convergence results are conditional on an insufficiently-validated G-BL hot-start, with random-init deficits ranging from -0.20 to -0.46; (3) the paper fails to compare against its two closest directly-cited competitors (Wei 2025 MONP, Kramer 2025 SARVis); (4) the sole domain-relevant operational claim (8.2% gain enabling sub-meter vessel discrimination) is quantitatively incorrect with a fabricated pixel-size figure. None of these issues can be resolved with minor revisions; Major Concerns 1, 2, 3, and 4 each require substantial new experimental campaigns (alternative MOEA paradigms, 200-scenario random-init runs, competitor re-implementations, MILP upper bounds) that are beyond the scope of a revision cycle. The core framing (framing a self-falsified three-objective design as a "saturation regime contribution") is also rhetorically problematic for ASR's mission-oriented readership. I recommend rejection, with encouragement to resubmit after: (a) resolving the NSGA-III crowding pathology with at least one competing MOEA, (b) running the full experimental matrix without hot-start initialization, (c) adding comparison to Wei 2025 and/or Kramer 2025, and (d) either demonstrating at least one configuration where the three-objective formulation has genuine non-redundant value, or restructuring the paper as a focused negative-result study on MOEA initialization-pathology and density-driven convergence collapse.

> **[Chinese]**
> **推荐结论：拒稿**
>
> 本论文包含一个内部自洽的负面结果——在单星单轨道 Stripmap C 波段配置下，使用带有 G-BL 热启动的 NSGA-III 时，分解式三目标公式坍缩为两目标公式，且物理质量目标的边际价值在 N ≈ 300 个目标以上趋于饱和——但多个严重缺陷导致其当前形式无法在 ASR 上发表。其中最具破坏性的是：(1) 在声称物理目标最具价值的稀疏场景下，无物理消融变体 D 严格优于完整物理基线，暴露了 NSGA-III 公式实际上是起反作用的；(2) 所有 MOEA 覆盖率收敛结果均依赖于未经充分验证的 G-BL 热启动，随机初始化的缺口高达 -0.20 至 -0.46；(3) 论文未与其最接近且被直接引用的两篇竞争工作（Wei 2025 MONP、Kramer 2025 SARVis）进行对比；(4) 唯一与领域相关的操作声明（8.2% 增益支持亚米级船只识别）在定量上是错误的，像素尺寸数字系凭空编造。这些问题无一能通过小幅修改解决；主要问题 1、2、3、4 各自都需要大量的新增实验工作（替代 MOEA 范式、200 场景随机初始化运行、竞争工作复现、MILP 上界），已超出一轮修订的合理范畴。核心叙事框架——将一个被自我证伪的三目标设计包装为"饱和域贡献"——对于 ASR 以任务为导向的读者群体而言，在修辞上也存在严重问题。我建议拒稿，并鼓励作者在以下工作完成后重新投稿：(a) 使用至少一种竞争 MOEA 算法解决 NSGA-III 的拥挤距离病理；(b) 在不使用热启动初始化的情况下运行完整实验矩阵；(c) 增加与 Wei 2025 和/或 Kramer 2025 的对比；(d) 要么证明至少存在一种配置使得三目标公式具有真正的非冗余价值，要么将论文重构为聚焦于 MOEA 初始化病理和密度驱动收敛坍缩的负面结果专题研究。

---

*Report summary: 5 major concerns, 4 minor concerns, 6 questions for authors, verdict: Reject.*
