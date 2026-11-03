# R1 (Methodology) report — ars-panel-20261030
## Canary
1. Read-only: I must not modify, create, or delete any file except my one report file.
2. Every finding must quote the exact manuscript text it criticizes, with section name and approximate tex line number.
3. No fabricated facts: I never assert what a cited reference contains beyond what the manuscript itself claims; literature gaps are phrased as candidate gaps only.
4. Numbers: I quote them exactly as in the manuscript; I never compute, alter, or correct numbers (arithmetic-consistency observations allowed only as "state A appears inconsistent with state B as quoted").
5. No network access; I do not attempt to fetch references.
6. I report genuine strengths and weaknesses; no manufactured findings, no finding quotas, no rubber-stamping.
7. My stdout is at most 5 lines; the report goes to the file.

## Overall assessment
**Recommendation signal: Major.** The manuscript has a substantial experimental program and unusually candid discussion of hot-start dependence, anchored fronts, HV cardinality, and budget limitations. Nevertheless, several methodological issues affect central comparisons rather than presentation alone. Most importantly, the pooled HV analysis does not explain how two-objective and three-objective fronts are embedded in a common dimensional space, yet their HV values enter direct rankings and a Friedman test. The density design also changes geometry differently across classes, so class-pooled trends do not by themselves isolate target count. The controlled third-objective margin depends on a matched re-selection rule that is not specified sufficiently to reproduce, and the random-init variant-D control does not sustain the stated objective-intrinsic attribution. The remaining findings concern effect-size nomenclature, control isolation, solver-seed disclosure, multiplicity families, and two internal consistency problems. These issues appear addressable through clearer definitions, appropriately scoped claims, and targeted additional analyses; they do not establish that the empirical results are false, but the present evidence chain is not yet adequate for the strength of some conclusions.

## Findings
**R1-01** | Severity: MAJOR | Location: §4.5 Multi-Objective Evolutionary Optimization, tex lines 677–680; §5.3 Evaluation Metrics and Statistical Tests, lines 795–803; Table `tab:hv`, lines 919–921

Quote: "MOEA-2 optimizes two objectives: $f_1^*$ (normalized profit) and $f_2$ (mean geometric quality, Eq.~\ref{eq:f2}). MOEA-3 adds $f_3$ (mean NESZ radiometric quality, Eq.~\ref{eq:f3}) as a third objective." / "Hypervolume is computed with reference point $(0, 0, 0)$ in the min--max-normalized objective space" / "This shared normalization framework makes cross-solver HV values directly comparable as relative rankings" / "MOEA-3  & 0.0893 & 0.1053 \\" / "MOEA-2  & 0.0668 & 0.0642 \\"

Issue: The HV procedure does not state how a two-objective MOEA-2 front is represented in the three-dimensional normalized space implied by the quoted reference point and the six bounds. Shared min/max bounds alone do not define a common-dimensional HV for two-objective and three-objective fronts.

Why it matters: HV is dimensional: a two-dimensional dominated area and a three-dimensional dominated volume are not made commensurable merely by pooling bounds. This uncertainty propagates to the direct MOEA-2/MOEA-3 table comparison and to the pooled-HV Friedman ranking, both of which are used as statistical evidence.

Suggested remedy (non-binding): Explicitly define the common embedding, including whether $f_3$ is recomputed post hoc for every MOEA-2 and baseline point and how missing coordinates are handled. If no common three-dimensional front is constructed, restrict HV inference to configurations with the same objective dimension or replace the pooled comparison with a dimension-appropriate diagnostic.

**R1-02** | Severity: MAJOR | Location: §5.1 Scenario Classes and Experimental Design, tex lines 723–731

Quote: "variants A--C modulate only the target distribution, while variants D and E additionally modulate the observation geometry, with a class-dependent role --- S1-D and S3-D use a single orbital revolution (yielding fewer and narrower windows), S2-E places targets at high latitudes ($\pm 40$--$70^\circ$), and S4-D narrows the incidence ceiling from $47^\circ$ to $25^\circ$. The 50 scenarios per class consist of these 5 variants $\times$ 10 random seeds each; the density trend reported in \S\ref{sec:scale-sensitivity} is robust to these within-class modulations"

Issue: The density classes do not differ only in target count: the geometry manipulations associated with a given variant label change by class. Class-pooled means therefore mix density with a class-specific geometry/variant composition, while the quoted robustness statement does not provide a complete variant-stratified density analysis.

Why it matters: Density dependence and saturation are central mechanisms in the results and ablation interpretation. If the class comparison also changes orbital-window availability, latitude, or incidence limits, the pooled trend cannot by itself attribute changes to density. An example that one sparse-regime deficit appears across S1 variants does not establish robustness of the full S1–S4 trend.

Suggested remedy (non-binding): Report the density trend within each invariant variant definition, or analyze a common baseline variant across all densities. Alternatively, use a variant-by-density analysis and narrow class-pooled claims to the explicit mixture of geometry conditions tested.

**R1-03** | Severity: MAJOR | Location: §6.4 Pareto Coupling and Compression, tex lines 1095–1103

Quote: "re-selecting both fronts under a matched radiometric-aware rule gives a controlled third-objective margin of $+4.9\%$ ($p = 2.3\times10^{-11}$, 47 of 50), whereas a radiometric-blind rule gives $+0.05\%$ ($p = 0.86$)"

Issue: The exact matched radiometric-aware and radiometric-blind selectors are not defined. In particular, the manuscript does not give their objective-weighting formulas, whether common normalization bounds are used for both fronts, or how ties are resolved. The default knee rule alone does not specify this additional re-selection analysis.

Why it matters: The controlled margin is a headline result and is used to separate the value of the third objective from the effect of knee selection. That separation depends directly on the selector; without its precise definition, readers cannot reproduce the control or assess whether the two re-selection rules differ only in the intended radiometric awareness.

Suggested remedy (non-binding): Define both selectors mathematically, specify shared normalization and tie handling, and state that all other selection steps are identical. Report the paired per-scenario selections or a reproducible pseudocode rule alongside the margin.

**R1-04** | Severity: MAJOR | Location: §6.6 Robustness and Calibration, tex lines 1346–1357; §6.5 Physical-Objective Ablation, `_ablation_section.tex` lines 18–24

Quote: "A random-init variant-D control (15 S3 and 15 S4 runs, no G-BL hot start) also converges to low squint" / "The lower-squint convergence is therefore objective-intrinsic rather than a hot-start residue" / "[D. No physics] $f_2 = f_3 = 1$ (constant per-task objective; solver receives no geometric information"

Issue: This control removes the G-BL hot start only in variant D, where the physical objectives are constant. Low post hoc squint argues against a hot-start-only explanation under those tested conditions, but the quoted term "objective-intrinsic" is ambiguous and stronger than the control isolates. If it refers to the physical content of $f_2$/$f_3$, the control cannot establish that mechanism because both are constant; if it refers to $f_1^*$ or generic objective structure, the control still does not distinguish that mechanism from decoder behavior, constraint filtering, or schedule-size effects.

Why it matters: The conclusion can be read as attributing low-squint convergence to the physical objectives despite relying on a no-physics control. Even under the broader reading, the positive mechanism remains unidentified; only the narrower rejection of a hot-start-only explanation is supported.

Suggested remedy (non-binding): Run the same random-init control with full-physics variant A and compare geometric outcomes at matched coverage or schedule size. Otherwise, narrow the conclusion to "not solely a G-BL hot-start residue under the tested variant-D conditions" and leave the positive mechanism unresolved.

**R1-05** | Severity: MINOR | Location: §5.3 Evaluation Metrics and Statistical Tests, tex lines 787–794; Fig. 1 caption, line 929

Quote: "the matched-pairs sign statistic $\delta_{\text{pairs}} = (W - L)/n$, which coincides with Cliff's $\delta$ when each scenario is evaluated as a matched pair." / "pairwise effect sizes as the matched-pairs sign statistic $\delta_{\text{pairs}} = (W-L)/n$, which equals Cliff's $\delta$ for the within-scenario pairing; the gray band marks the negligible-effect range ($|\delta|<0.147$ of \citet{Romano2006}; shown for reference, as the conventional unpaired $\delta$ is weaker for the within-pair comparisons"

Issue: A within-pair sign proportion and conventional unpaired Cliff's delta are different estimands: the latter uses cross-observation pairwise comparisons, whereas the former uses only matched pairs. They do not become generally equivalent merely because the data are paired. The figure appropriately notes that the conventional value differs, but the equality claim and shared visual threshold remain misleading.

Why it matters: Effect-size direction, magnitude, and the negligible-effect interpretation can change with the estimand. Clear nomenclature is especially important here because both forms are reported elsewhere in the manuscript.

Suggested remedy (non-binding): Name $(W-L)/n$ only as a paired sign-dominance statistic, define tie handling explicitly, and keep conventional Cliff's delta separate. Use Romano's thresholds only for the estimator for which they are intended, or label the paired-statistic band strictly as an uncalibrated visual reference.

**R1-06** | Severity: MINOR | Location: §6.6 Robustness and Calibration, tex lines 1336–1344

Quote: "On five S1 scenarios, 5,000 random task selections per scenario produce mean $f_1^*=0.527\pm0.003$ and a 90th percentile of $0.930\pm0.008$" / "Because the random sampler is unconstrained and does not enforce C2--C4, this is an empirical bound on the tested batch rather than a construction guarantee. High coverage under random sampling therefore occurs only by chance; the MOEA's gains reflect structured search."

Issue: The random comparator does not enforce the same feasibility constraints and is not described as matching the MOEA's decoder, evaluation budget, or selection procedure. It consequently mixes differences in structured evolutionary search with differences in feasibility handling and sampling mechanics.

Why it matters: The quoted conclusion attributes the MOEA advantage specifically to structured search, but this control can support only a contrast with this unconstrained sampler on the tested scenarios. The manuscript's own caveat about an empirical bound does not resolve that attribution gap.

Suggested remedy (non-binding): Add a constraint-enforcing random decoder with an explicitly matched evaluation budget, or narrow the claim to the observed superiority over the stated unconstrained random-selection baseline without isolating the source of the gain.

**R1-07** | Severity: MINOR | Location: §5.1 Scenario Classes and Experimental Design, tex lines 728–730; §5.4 Experimental Protocol, lines 833–835

Quote: "The 50 scenarios per class consist of these 5 variants $\times$ 10 random seeds each" / "The first is the main experiment, running all five configurations (G-BL, G-SM, the GA-P-BL control, MOEA-2, MOEA-3) on 50 scenarios per density class (S1--S4), totaling 200 scenarios."

Issue: The quoted seed count describes scenario generation, but the main protocol does not state the solver-seed mapping or whether stochastic solvers receive repeated independent runs per scenario. It is therefore unclear how search stochasticity is separated from instance variability in the main experiment.

Why it matters: A scenario seed does not necessarily determine an optimizer's random stream. One stochastic run per instance can be a valid design, but its uncertainty interpretation differs from replicated within-instance runs, and exact solver seeds are needed to reproduce the paired Wilcoxon inputs and front realizations.

Suggested remedy (non-binding): State the solver-seed rule and the number of independent optimizer runs per scenario. If each scenario is run once, justify that design and consider replicated runs on a representative subset to quantify within-instance search variability.

**R1-08** | Severity: MINOR | Location: §7 Discussion, statistical-testing clarification, tex lines 1429–1432; §6.5 Physical-Objective Ablation, `_ablation_section.tex` lines 54 and 108

Quote: "Pairwise Wilcoxon signed-rank tests use the Bonferroni threshold $\alpha=0.005$ ($\alpha=0.05/10$; the four-variant ablation of \S~\ref{sec:ablation} applies $\alpha=0.05/12$ across the 12 variant-by-class" / "Asterisks mark paired Wilcoxon comparisons against A significant at the Bonferroni threshold ($p<0.05/12$)."

Issue: The main ten-pair family is clear, but the ablation family is not fully delimited. The same threshold is invoked while the ablation reports multiple outcome metrics and additional S5/S6 comparisons; the text does not state whether correction is per metric, per class group, or across all reported ablation tests, nor which analyses are confirmatory versus exploratory.

Why it matters: Multiplicity control depends on family membership, not only on the divisor shown. Without that definition, readers cannot determine which reported significance labels share a controlled error rate.

Suggested remedy (non-binding): Enumerate each hypothesis family and its members, including outcomes and robustness classes, and label analyses outside a corrected family as exploratory with raw $p$-values.

**R1-09** | Severity: MINOR | Location: §6.4 Pareto Coupling and Compression, tex lines 1130–1132

Quote: "This $f_1^*$ exceedance is driven by point-count asymmetry"

Issue: The quoted explanation attaches a front-cardinality mechanism to an $f_1^*$ exceedance. Under the manuscript's definitions, $f_1^*$ is the normalized profit of a schedule, whereas point-count asymmetry is an HV/front-comparison property. The stated causal link therefore does not follow as written.

Why it matters: This conflates a solution-level coverage result with a set-level diversity/cardinality diagnostic and can misdirect the interpretation of the exceptional scenario.

Suggested remedy (non-binding): Clarify whether the intended quantity was HV rather than $f_1^*$, or provide a solution-level mechanism for the profit exceedance independently of front cardinality.

**R1-10** | Severity: MINOR | Location: §7.1 Mechanistic Interpretation, tex lines 1393–1396; Table `tab:solver-profiles`, lines 879–884

Quote: "MOEA-3 trades $f_2$ ($-4\%$ vs.\ MOEA-2) for the highest $f_3$ ($0.698$, $+6.2\%$ vs.\ MOEA-2 under the reported knee rules)" / " & G-SM    & $0.51 \pm 0.16$ & $0.389 \pm 0.086$ & $0.722 \pm 0.058$ \\"

Issue: State A appears inconsistent with state B as quoted: the discussion calls MOEA-3's S1 $f_3$ value the highest, while the S1 table row reports a higher quoted $f_3$ value for G-SM. No recomputation is needed to identify the wording conflict.

Why it matters: The sentence obscures the distinction between the best radiometric quality among the MOEA configurations and the best across all listed solvers, weakening an otherwise useful no-domination discussion.

Suggested remedy (non-binding): Qualify the superlative as applying only to MOEA-2/MOEA-3, or revise the sentence to acknowledge G-SM's quoted table value.

## Non-defect observations
- The manuscript repeatedly discloses G-BL normalization and hot-start dependence, including the anchored-front caveat and the need for full-scale random-init experiments; this is materially better than treating the MOEA fronts as unconditional optima.
- GA-P-BL's near-degeneracy with G-BL is reported openly, and the guard's construction is used to explain the Friedman test's limited discrimination rather than hidden.
- The unmatched and matched knee comparisons are explicitly distinguished, and the conventional unpaired Cliff's delta is reported alongside the paired sign statistic in the headline third-objective comparison.
- Per-scenario-ratio and pooled-mean calibers are distinguished, and found fronts are described as best-known approximations rather than verified Pareto-optimal sets.
- The search-budget control explicitly discloses its small scenario scope and the absence of a convergence trace, and it conditions the quality claims on the tested budget.
- MOEA-2 and MOEA-3 use the same stated population, generation budget, and genetic operators; a separate reference-direction-count control addresses an important alternative explanation for the third-objective result.
- Final-chunk statistical clarification: the discussion identifies pooled HV as the Friedman response, states the ten-pair and ablation correction thresholds, and specifies that zero within-pair differences are dropped and reported separately (tex lines 1424–1436). It also appropriately cautions that the omnibus HV result is driven largely by NSGA-III front dispersion.
- Final-chunk reproducibility disclosure: the manuscript names `pymoo` 0.6.1.6, gives a public repository, and states that fixed seeds/configurations, processed results, analysis scripts, and regeneration scripts are available (tex lines 1645–1651).
- Final-chunk numerical consistency: except for R1-10, the discussion/conclusion retain the previously read S1 quoted states—MOEA-2 `$f_1^*=0.86$`, `$+33.7\%$` `$f_2$`, MOEA-3 `$+40\%$` `$f_3$`, and a `14`–`15\%` coverage cost (tex lines 1451–1454 and 1594–1598). No values were recomputed.
