# Peer Review Report

## Manuscript Information
- **Title**: Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite: Balancing Profit, NESZ, and Geometric Resolution
- **Manuscript ID**: N/A (panel review, Advances in Space Research)
- **Review Date**: 2026-08-15
- **Review Round**: Round 1 (fresh review, no prior history)

---

## Reviewer Information

### Reviewer Role
Peer Reviewer 3 (Perspective — cross-disciplinary / practical applicability)

### Reviewer Identity
Operations-research researcher (multi-objective optimization and mission-planning systems) with Earth-observation domain exposure — an "adjacent-field" reviewer rather than a SAR specialist. I evaluate this paper for what other communities (OR scheduling, EO mission operations, satellite systems engineering) would learn from it, whether its operational guidance is implementable, and whether its fundamental modeling assumptions survive cross-disciplinary scrutiny. Where SAR physics conventions are at stake, I flag my outsider status explicitly rather than overrule the field's standards.

### Review Focus
(1) Transfer value of the physics-aware multi-objective framing beyond SAR (optical, hyperspectral, constellations) and honest scoping thereof; (2) computational cost vs. operational planning cycles; (3) robustness of results to scenario/assumption structure; (4) the §6.4 correlation result as a scheduling insight for the broader OR community; (5) whether limitations are honestly bounded.

---

## Overall Assessment

### Recommendation
**Major Revision**

### Confidence Score
**4** — Mostly within my area of expertise (OR, MOO, mission operations); SAR-specific physics conventions are adjacent territory, and I verified runtime claims directly against the companion repository's run data.

### Summary Assessment
The paper formulates agile SAR scheduling with two physically decomposed quality objectives (geometric index $f_2 = \sin\theta\cos\psi$, radiometric index $f_3 = \cos^3\xi$) inside NSGA-III, and reports a scale-dependent saturation: multi-objective quality gains ($+34\%$ $f_2$, $+41\%$ $f_3$ at $N=20$) collapse to $<1\%$ by $N \geq 300$, with the third objective's value density-dependent rather than identically redundant. The claim structure is unusually rigorous for a computational study: the saturation is scoped to single-pass, single-satellite Stripmap, explicitly *not* a "superior solver" claim, and the news that solver-selected schedules actively move the $f_2$–$f_3$ correlation (−0.97 envelope → −0.63 schedule at S1) is a transferable methodological template. The comparisons rest on a strong evidence base (200 scenarios × 5 geometry variants × 10 seeds; 1,200 ablation runs; four robustness controls). However, two issues from my seat impede acceptance: the paper's headline motivation ("time-critical monitoring missions") never becomes an objective or metric — within-window timing is utility-free, which is a consequential modeling choice the paper never acknowledges; and §5.4 promises a search-budget control that §6.6 does not deliver while claiming "not a budget artifact." Both are repairable (framing rewrite; one cheap subset run or an honest re-scope), which is why I stop short of Reject, but the Defects are material enough that re-review is warranted.

---

## Strengths

### S1: Honest, self-bounding limitation practice — rare in computational scheduling papers
**Evidence Anchor**: [`text: §2.2 "It is therefore used here as a relative ordering index across observation geometries, not as an absolute radiometric prediction"; "an empirical convergence effect—not a mathematical identity between f2 and f3" (§6.4)`]
The NESZ model's plane-Earth approximation is quantified (5% range, 17% $R^3$ error at the $47^\circ$ edge), the HV point-count confound is both analytically identified and numerically documented (G-SM's single point, HV 0.2351, would outrank MOEA-3's whole front, 0.0921), and the third-objective redundancy is repeatedly qualified as "empirical convergence … not a mathematical identity." From the OR community's perspective, this is replicable-science behavior worth endorsing as a model.

### S2: The envelope–null–schedule correlation decomposition is a transferable methodological template
**Evidence Anchor**: [`equation: §6.4 r_null = −0.51 (independence null) vs envelope −0.97 vs schedule −0.63 (S1) / −0.15 (S3)`]
Distinguishing the feasible-envelope correlation (−0.97), an independence null (−0.51), and solver-selected schedule correlations (−0.63 → ≈−0.15 with density), and showing the attenuation is "an active effect of the solvers, not a consequence of geometric envelope constraints," is exactly the kind of structure-vs-policy separation any physics-coupled scheduling domain (optical, hyperspectral, radar) should borrow. This is the paper's most exportable contribution.

### S3: Anti-hype register — conditional operational guidance instead of a universal solver recommendation
**Evidence Anchor**: [`text: Conclusion "Rather than identifying a superior solver, our results establish an empirical saturation boundary for physics-aware multi-objective scheduling"`]
§7.2 gives density-conditional advice (sparse: MOEA-2 for geometry; dense: greedy per priority dimension), and the paper explicitly declines to crown a solver. For a cross-disciplinary audience wary of MOEA-hype, this restraint substantially raises credibility.

### S4: Scale-dependent claims on a genuinely systematic evidence base
**Evidence Anchor**: [`table: Table 2 (S1–S4, 50 scenarios/class) + Table 6 (ablation A–D, 1,200 runs) + Table 5 (scale sensitivity incl. S7/S8 intermediate densities)`]
Four density classes × five geometric variants (clustered/uniform/distribution, single-revolution windows, high latitude, narrowed incidence ceiling) × ten seeds, supplemented by intermediate densities N=150/200 that constrain the transition band, with the N50 confidence interval honestly reported as wide ([30, 62]). This is the design a scale-sensitivity claim requires.

### S5: Reproducibility disclosure
**Evidence Anchor**: [`text: Data Availability "Solver code, scenario generators, fixed seeds and configurations, processed JSON/CSV results, analysis scripts, and figures are available"`]
A public companion repository with fixed seeds and regeneration scripts makes the study independently checkable — increasingly the norm the OR community expects.

---

## Weaknesses

### W1: The time-critical motivation never becomes an objective — within-window observation timing is utility-free
**Problem**: The Introduction motivates the work with "Agile Earth-observation satellites … increasingly central to time-critical monitoring missions, from disaster response to maritime surveillance," yet the formulation (§3.2) contains three objectives — profit, geometric quality, radiometric quality — and no timeliness/latency dimension anywhere. A target imaged at the first vs. last second of its visibility window is valued identically; a target observed immediately vs. one orbit later carries the same utility. For the paper's own headline applications (disaster response; maritime surveillance — where detection-to-response latency is the dominant utility dimension), this decouples the stated purpose from the measured quantities.
**Evidence Anchor**: [`text: §1 "Agile Earth-observation satellites equipped with Synthetic Aperture Radar (SAR) are increasingly central to time-critical monitoring missions, from disaster response to maritime surveillance"; §3.2 "we formulate a three-objective optimization problem that captures the tension between scheduling throughput and SAR-specific imaging quality"`]
**Why it matters**: §7.2 issues conditional guidance to mission planners, but the utility model underneath excludes the dimension those planners most care about in the motivating scenarios. The saturation boundary (N50 ≈ 50) and the "greedy suffices at operational densities" recommendation could look different under a latency-aware utility (e.g., a mission-critical target that must be observed before a deadline has no substitute in the additive profit sum). An interesting side-observation the authors could leverage: G-BL's earliest-feasible-time placement is nearly latency-optimal by construction, which *strengthens* the dense-regime greedy recommendation for time-critical operations — but only if the paper says so.
**Suggestion**: Either decouple the introduction's motivation from the actual objective set, or add an explicit limitation/discussion recognizing that the model optimizes quality and quantity at a fixed timeliness operating point, and that latency/urgency is a distinct objective dimension (deadline-constrained scheduling, time-to-first-observation) left to future work. Most valuable: one paragraph in §7.2 noting when the greedy recommendation is also the latency-minimizing one.
**Severity**: Major
**Confidence**: 4 — adjacent-field expertise: OR for surveillance/maritime operations; mission-utility structuring.

### W2: Runtime is stated qualitatively, never measured — yet §7.2 issues operational guidance
**Problem**: §5.2 states "We do not report wall-clock runtimes: the greedy heuristics complete in milliseconds while the evolutionary solvers take minutes on the densest scenarios." No table, no single-core spec context, no scaling statement, and no discussion of whether "minutes" fits a planning or replanning cycle. A practitioner reading the conditional guidance in §7.2 cannot judge computational feasibility without these numbers. I verified the companion repository's run records: MOEA-2/MOEA-3 median single-core wall-clock is ~20–22 s at S1, ~66–67 s at S2, ~217–220 s at S3, ~262–263 s at S4 (max ~390 s) — i.e., the true runtimes are modest and would *support* the operational reading, but the paper never says so.
**Evidence Anchor**: [`text: §5.2 "We do not report wall-clock runtimes: the greedy heuristics complete in milliseconds while the evolutionary solvers take minutes on the densest scenarios"`]
**Why it matters**: For the OR/mission-ops audience, runtime is a first-class decision variable (replanning cycles, rolling horizons, contingency tasking). Withholding the numbers makes the operational implications section unverifiable, even though the underlying data exist and are cheap to report. It is the difference between "academically meaningful" and "practically usable."
**Suggestion**: Report per-class median (and max) wall-clock for all solvers on a stated single-core CPU, plus one sentence mapping to typical planning cycles (e.g., offline daily planning vs. event-driven replanning), and state the generation budget used (200) so readers can extrapolate. No new experiments needed — the data are already in the repo.
**Severity**: Minor
**Confidence**: 5 — directly measured the repository's `runtime_s` fields.

### W3: §5.4 promises a search-budget control that §6.6 does not deliver
**Problem**: The Experiment Design Overview lists four robustness controls — "hot-start dependence, perturbation-sensitivity sweep, random-search calibration, and search-budget control—which verify that the main and ablation findings are not artifacts of initialization or parameter choices." §6.6 then reports exactly three paragraphs (hot-start, perturbation, random-search) plus a random-init variant-D control — no generation-budget (e.g., 100/400 generations) experiment appears anywhere in the manuscript. Instead, §6.6 argues the A–D invariance "already holds at standard budget … the convergence is therefore not a budget artifact" — an assertion, not the promised experiment.
**Evidence Anchor**: [`absence: §6.6 Robustness and Calibration — expected a search-budget (generation-count) control experiment; checked §5.4, §6.6, §7, Conclusion`]
**Why it matters**: The saturation claim's robustness pillar is explicitly promised at four and delivered at three. The sentence "the convergence is therefore not a budget artifact" exceeds the evidence. Since the dense-regime result holds even for a random sampler (the random-search control reaches 0.93 of G-BL profit at the 90th percentile), a budget control would very likely confirm the claim — which makes running it (e.g., 400 generations on a subset of scenarios) cheap and worthwhile. At minimum, the claim must be re-scoped or the §5.4 list corrected.
**Suggestion**: Run MOEA-2/MOEA-3 with 100 and 400 generations on a scenario subset (S1, S3, 10 seeds each) and add the result as a short paragraph, or delete "search-budget control" from §5.4 and reword the "not a budget artifact" sentence.
**Severity**: Major
**Confidence**: 5 — direct manuscript comparison of §5.4 and §6.6.

### W4: The same logistic midpoint is reported as N50 ≈ 50 and N50 ≈ 45
**Problem**: §6.3 reports the transition midpoint as "N50 ≈ 50 targets" with CI [30, 62], and §7.2 cites the same §6.3 result as "The logistic midpoint N50 ≈ 45."
**Evidence Anchor**: [`text: §6.3 "yields a transition midpoint N50 ≈ 50" ; §7.2 "The logistic midpoint N50 ≈ 45 (§6.3)"`]
**Why it matters**: Two numbers for one published statistic undermines the paper's own trustworthiness on the headline scale-dependence quantity; readers fitting the logistic themselves will not know which value is authoritative.
**Suggestion**: Report one value (with CI) in both places, and state the fitting procedure identically.
**Severity**: Minor
**Confidence**: 5 — direct reading of both passages.

### W5: Transferability to non-SAR EO scheduling is never discussed — a missed community audience
**Problem**: The Discussion and Limitations bound the result across SAR modes (ScanSAR/Spotlight/TOPS) and multi-satellite settings, but never address what the physics-aware MOEA framing means for optical, hyperspectral, or constellation scheduling — the paper's likely transfer audience. The mapping is genuinely partial and interesting: the geometric-quality index ($\sin\theta$-type GSD dependence) transfers directly to optical systems; the radiometric objective does not (optical radiometry is dominated by solar elevation/cloud cover, not slant range); and cloud masking would inject the stochasticity this deterministic model lacks. The paper's own contribution 2 claims a formulation "distinct from … the scalar visibility composite," which invites exactly this comparison.
**Evidence Anchor**: [`absence: Discussion §7 / Conclusion — expected explicit transferability statement to optical/hyperspectral/constellation scheduling with partial-mapping discussion; checked §6–§8, Abstract, §2`]
**Why it matters**: The abstract claims an "empirical saturation boundary" — for the single-satellite SAR case. A short transfer-mapping paragraph (what geometry physics carries over, what does not, and why) would convert the paper from a SAR-domain result into a baseline for any EO agile-scheduling formulation, matching how the paper itself frames the multi-satellite extension. Without it, adjacent communities must re-derive the scope themselves.
**Suggestion**: Add a "transferability" paragraph in Discussion: (i) geometric-resolution objectives carry to optical (GSD ∝ 1/sinθ); (ii) radiometric/atmospheric objectives do not (illumination, clouds); (iii) the envelope-vs-schedule correlation decomposition (S2) is the transferable analytic device. Optionally connect to the objective-reduction literature (see Reading Recommendations).
**Severity**: Minor
**Confidence**: 4 — adjacent-field: EO mission systems; cloud/illumination modeling beyond my direct expertise.

### W6: The squint-agility envelope (45°) is far beyond real platforms, and no envelope-sensitivity is tested
**Problem**: C1 assumes "ψ_sq^max … (assumed ≤ 45°; real agile SAR platforms typically slew only a few degrees …)" — as the authors note, real platforms have far less squint agility than the tested envelope, and the realized schedules use mean |ψ| of 16–24°. The quantitative gains (esp. the $f_3$ results, which depend on $\cos^3\psi$) are therefore envelope-dependent, but the only perturbation tested (σ sweep) varies initialization noise, not the physical agility envelope.
**Evidence Anchor**: [`text: §3.3 C1 "real agile SAR platforms typically slew only a few degrees, so this is a conservative envelope for the tested agility"`]
**Why it matters**: An operator of an actual platform (few degrees of squint) cannot port the sparse-regime gain magnitudes directly; the paper's own disclosure shows the envelope is generous relative to practice. The qualitative conclusion (density-driven saturation) plausibly survives a realistic envelope — the θ-conflict would dominate even more — but that is an inference, not a result.
**Suggestion**: Either add a remark that the conservative envelope bounds the tested agility family and that reduced squint agility only strengthens θ-dominance (one tightly argued paragraph), or run a 5–10° envelope variant on S1 to quantify the sparse-regime gain under realistic agility. Also worth answering in the reply letter.
**Severity**: Minor
**Confidence**: 4 — satellite-platform agility figures vary by platform; envelope mathematics checked against the paper's own equations.

---

## Detailed Comments

### Title & Abstract
The abstract overdelivers on clarity and honesty: key numbers (+34%/+41%, 14–15% coverage cost, 0.39–0.68 random-init deficits) are concrete, and the "rather than a mathematical identity" hedge is a model of calibration. One cross-disciplinary note: the abstract's "operational densities" ($N \geq 300$) framing presumes the reader knows what operational single-pass densities are — for non-SAR readers, one clause anchoring $N$ to "targets per pass/orbit" would help.

### Introduction
The motivation ("time-critical monitoring missions, from disaster response to maritime surveillance," §1) and the objective set diverge — see W1. Otherwise the problem statement (quality as a continuous function of timing) is compelling, crisply distinguishes the paper from fixed-quality scheduling, and the NP-hardness framing via Orienteering-with-time-dependent-profits correctly signals the OR ancestry. The five-solver span (greedy → single-objective GA → NSGA-III) is a sensible methodological ladder.

### Literature Review / Theoretical Framework
Coverage of the scheduling, SAR-quality, and MOEA literatures is appropriate (primarily Reviewer 2's seat). Two perspective notes: (i) the related work correctly identifies Chang2022Gaofen as closest prior work, but the distinction drawn (decomposed physical quality vs. operational-quality proxies) would be sharper if the paper engaged the EMO literature on *redundant objectives / objective reduction*, which formalizes exactly the "third objective becomes redundant" question (see Reading Recommendations); (ii) the claimed novelty — "no existing SAR scheduling method treats continuous, physics-derived quality functions as decomposed optimization objectives" — is strong and verifiable within the cited set, but a single sentence mapping how Kramer2025SARVis's "weighted visibility–performance composite" differs from §3.2's decomposition (mean per-task physical indices vs. weighted composite) would preempt the obvious related-work objection.

### Methodology / Research Design
The formulation is clean and the decomposition into incidence (θ) vs. squint (ψ) mechanisms is well built (§3.2–3.3). From an OR standpoint, three observations: (i) normalizing coverage by the G-BL outcome embeds a specific solver's performance into the objective ($f_1^*$), which makes the MOEA-vs-baseline comparison partially circular — the paper discloses this caveat for the random-init deficits, but a cross-disciplinary reader would like one sentence on why absolute profit or an upper-bound normalization was not used; (ii) C3–C4 at $10^7$/$10^{11}$ with non-binding intent is a reasonable completeness choice, but the downstream claim that saturation "may not transfer when energy or downlink capacity is the binding constraint" (§7.4) deserves one forward reference to existing energy-aware scheduling work — the infrastructure already exists and would strengthen the limitation; (iii) the runtime non-reporting (W2) is the largest methodology gap from the practitioner side.

### Results / Findings
The results section is strong and unusually self-critical (HV confounds quantified; per-schedule correlation spread $r \in [-0.97, +0.25]$ at S1 honestly reported; negative results reported as such). The §6.4 correlation analysis is the paper's most novel element (S2) — the envelope/null/schedule three-way contrast is precisely what makes the "scheduling-insight vs. geometry-necessity" reading defensible. On the panel's specific question of whether the correlation finding is overgeneralized: it is not — it is scoped to the tested orbit/geometry, and the "not reliably density-strengthening" observation (pooled −0.63 at S1 vs. −0.23 at S4) is stated rather than smoothed over. One implicit assumption worth surfacing: the correlation is computed over solver-selected *schedules* — i.e., it is a property of the feasible-set geometry seen through the lens of these particular solvers and this orbit (dawn–dusk SSO); for other orbits/LTANs the envelope geometry and hence the correlation could change, a sensitivity the paper does not claim but a reader might assume.

### Discussion
The Pareto-sufficiency operationalization (§7.1) is a good, transferable construct (statistical dominance criterion for solver sufficiency), and the five findings are well synthesized. The conditional operational guidance (§7.2) is the right register, but it sits on the timeliness-free utility model (W1) and unreported runtime (W2), which limits its usability. One further cross-disciplinary point: §7.2's 0.3 m C-band resolution example is the only place where index-space $f_2$ is translated into physical terms (meters); a small mapping table (index → GSD/NESZ in engineering units) would dramatically raise the paper's utility to operators.

### Conclusion
Appropriately scoped and honest; "these findings establish an empirical saturation boundary … and provide a baseline against which multi-satellite, multi-pass, and multi-mode extensions can be measured" is exactly the right closing register.

### References
Citation quality is handled primarily by Reviewer 2. From the perspective seat: the Ferrari2025 survey (cited in §2.1) is an appropriate anchor for future dynamic/rolling-horizon work; the absence of the objective-reduction literature (see S2/W5 context) is the notable gap from a cross-disciplinary standpoint.

---

## Questions for Authors

1. **Squint-agility realism (W6)**: Your envelope allows |ψ| ≤ 45° while real stripmap platforms slew only a few degrees. How do the sparse-regime gains (+34% f2, +41% f3 at N=20) change under a realistic envelope (e.g., 5°)? Does the "third-objective value at sparse density" conclusion survive — or does the θ-conflict dominate even more strongly, which would strengthen your mechanism story?

2. **Timeliness (W1)**: If a latency dimension were added (e.g., priority-weighted time-to-first-observation, or deadline-constrained tasking), would the saturation boundary N50 ∈ [30, 62] move? Is G-BL's earliest-feasible-time placement near-latency-optimal, and if so, does that make the dense-regime greedy recommendation *stronger* for the time-critical missions named in your Introduction?

3. **Priority-structure robustness**: With uniform priorities {1..10}, dropping low-weight targets to buy quality is cheap — the 14–15% coverage costs at S1 are partly a consequence of this distribution. How do the Table 3 trade-offs change under a bimodal structure (a few urgent targets + many routine)? This directly affects the practical reading of the coverage-quality trade-off.

4. **Runtime and budget (W2, W3)**: Will you report per-class single-core wall-clock (already recorded in your runner outputs), and run the promised search-budget control (e.g., 100 vs. 400 generations on a subset) so the "not a budget artifact" claim rests on data?

---

## Minor Issues

- §7.1: the phrase "Under the window-corrected data" is unexplained jargon — a fresh reader cannot tell what window correction is being referenced; define or drop it.
- §6.4: the representative-S4 front is said to span "about 0.08 in f1*" (Phenomenon 1) but "S4 fronts span only Δf1* ≈ 0.06" later in the same section — reconcile to one value.
- Contribution 1 (Introduction): "200 scenarios per variant" for the ablation, vs. §6.5's "six scenario classes × 50 seeds = 300 runs per variant"; the manuscript presents S1–S4 (200 scenarios) in Table 5 but runs 6 classes — state both numbers consistently.
- §7.2: only one physical-unit translation is given (0.3 m at C-band); a compact index→GSD/NESZ mapping table would serve operators.

---

## Criterion-Bound Judgements

Calibration status: `NOT_CALIBRATED`

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | peer-review rubric (quality_rubrics.md) | MEETS | text: §2.3 "no existing SAR scheduling method treats continuous, physics-derived quality functions as decomposed optimization objectives" (per §2.3 claim) | Decomposed physical quality objectives in agile SAR scheduling + a negative result (saturation) rather than a solver claim; the correlation-in-schedules analysis is novel | Novelty of the saturation *explanation* (lower-squint convergence) rests on single-orbit evidence | Yes |
| Methodological Rigor | quality_rubrics.md | PARTLY_MEETS | absence: §6.6 — expected search-budget control; checked §5.4, §6.6, §7 | Strong overall design (200 scenarios, ablation, robustness suite); undermined by a promised-and-missing control (W3) and unquantified runtime (W2) | Runtime, priority structure, and squint-envelope sensitivity untested | Yes |
| Evidence Sufficiency | quality_rubrics.md | MEETS | table: Table 2 + Table 5 + Table 6 | Scale-dependent claim supported across 4 (+2 intermediate) densities, 5 geometric variants, 10 seeds; per-schedule correlation spread honestly reported | S1 correlation based on pooled/per-schedule stats over 50 scenarios — adequate for the claim made | Yes |
| Argument Coherence | quality_rubrics.md | PARTLY_MEETS | text: §6.3 "N50 ≈ 50" vs §7.2 "N50 ≈ 45" | Overall narrative coherent; N50 inconsistency (W4) and motivation–model gap (W1) break the frame at two exposed points | — | Yes |
| Writing Quality | quality_rubrics.md | MEETS | text: Abstract (verbatim hedges) | Clear, dense, unusually honest hedging; "window-corrected data" (§7.1) and a few unexplained terms are editorial | — | No |
| Literature Integration | quality_rubrics.md | MEETS | text: §2 lines 200–230 (Chang2022Gaofen, Wei2025MONP, Kramer2025SARVis) | Positioned against closest prior work; objective-reduction (EMO) strand missing would strengthen transferability (W5) | Missing strand is a strengthening opportunity, not a coverage defect | No |
| Significance & Impact | quality_rubrics.md | PARTLY_MEETS | text: §7.2 conditional guidance; Conclusion saturation-boundary claim | Saturation boundary + analytic template are genuinely useful to EO scheduling and OR communities; impact limited by missing transfer discussion (W5), timeliness gap (W1), runtime data (W2) | Practical impact judged from OR/mission-ops standpoint | Yes |

Decision-bearing criteria are Originality, Methodological Rigor, Evidence Sufficiency, Argument Coherence, and Significance & Impact. The combined picture is a strong original contribution whose rigor and impact claims carry repairable gaps (W1–W5): none invalidates the core saturation finding, all can be addressed without new core re-analysis (one subset experiment, framing/limitation rewrites, consistency fixes). Recommendation stands at Major Revision primarily for the W3 evidence-claim gap and W1 motivation-model mismatch, with re-review after revision.

---

## Cross-Disciplinary Reading Recommendations

- **Objective reduction in evolutionary multi-objective optimization** — the EMO literature on "redundant objectives" (Brockhoff & Zitzler, *Are All Objectives Necessary? On Dimensionality Reduction in Evolutionary Multiobjective Optimization*, IEEE TEC) formalizes exactly the "third objective becomes redundant" question posed in §6.4–§7.1. Connecting the empirical density-dependent redundancy to this framework would give the paper's core concept established theoretical vocabulary. `[UNVERIFIED — search lead; verify exact year/volume before citing]`
- **Repeat-pass geometric consistency for monitoring/InSAR** — the time-series SAR community's requirement of *consistent* acquisition geometry across revisits (e.g., Ferretti, Prati & Rocca, PSInSAR methodology, IEEE TGRS) is the strongest cross-disciplinary caveat to the per-image optimal-quality objective: for change-detection and interferometric monitoring (compatible with the paper's maritime/monitoring motivation), consistency, not per-image optimality, is often the quality criterion. Worth one sentence in Limitations/future directions. `[UNVERIFIED — search lead; verify metadata]`
- **Cloud/illumination-aware optical scheduling** — for the W5 transfer discussion: search leads on stochastic optical scheduling accounting for cloud cover and solar elevation, and the Ferrari-2025 survey family your paper already cites (in-paper, verified) for the dynamic/rolling-horizon branch.