# Methodology Review — paper1

## Canary
1. Read-only: I must not modify, create, or delete any file except my one report file.
2. Every finding quotes the exact manuscript text it criticizes, with section name and approximate tex line number.
3. No fabricated facts: I never assert what a cited reference contains beyond what the manuscript itself claims.
4. Numbers: I quote them exactly as printed; I never recompute or correct them (arithmetic-consistency observations allowed only as "state A appears inconsistent with state B as quoted").
5. No network access.
6. Genuine strengths and weaknesses; no manufactured findings, no quotas, no rubber-stamping.
7. Stdout is at most 5 lines; the report goes to the file.

## Summary judgement
The research design is considerably better than the norm for this literature: a controlled objective-function ablation with a genuine null model, budget-matched evolutionary arms, a paired statistical pipeline (Friedman + Wilcoxon with a stated Bonferroni family, Cliff's-style effect sizes), a bootstrap interval on the logistic midpoint, and an unusually complete limitations section. Statistical reporting is mostly correct and complete at the claim level — p-values, effect sizes, dispersion and sample sizes are all present — though several statistics are quoted at a scale whose thresholds were calibrated for a different statistic. The three places that would draw a demanding referee's fire are structural rather than arithmetic: the single-objective GA arm is degenerate (identical to the greedy baseline in 199 of 200 scenarios) so it cannot serve as a search control; the reproducibility model contradicts itself (fixed seeds announced in Data Availability versus "operator-level random draws are not pinned" in the design section); and the two headline boundaries are both measured from G-BL-seeded fronts under an artificial 200-task resource ceiling that binds exactly in the dense regime where the second boundary is claimed. The mechanistic decomposition (§6.4 envelope–null–schedule) is the paper's best contribution and is well defended; the operational reading built on top of it is where the inference outruns the evidence.

## Strengths

- **Envelope–null–schedule decomposition.** "A permutation null that shuffles the visibility-window-grid $\theta_{\text{elev}}$ and $\psi_{\text{sq}}$ marginals within each density class gives $r_{\text{null}} = -0.60$ to $-0.62$" (§6.4, ~line 1111-1113), used to separate definitional coupling from scheduler-induced correlation. This is the right way to attack "are these two objectives redundant?", and few scheduling papers attempt it.
- **Killing the obvious alternative explanation.** "the pooled within-schedule $f_2$ standard deviation is $0.16$--$0.17$ at S1--S3 and $0.14$ at S4 for variant A, with pooled range $0.65$ in every class" (§6.4, ~line 1179-1181) — the authors pre-empt the range-restriction account rather than leaving it to the referee.
- **Matched-rule control for the third objective.** "+4.9% ($p = 2.3\times10^{-11}$, 47 of 50), against $+0.05\%$ ($p = 0.86$) for a radiometric-blind rule" (§6.4, ~line 1196-1197), backed by a reference-direction-density control ($p=4$: $0.702\pm0.041$ vs $0.698$). This is exemplary: it isolates the objective's own contribution from the knee-selection convention.
- **Candid modelling caveats with sign and magnitude.** "it underestimates slant range by roughly $4\%$ and $R^3$ by roughly $13\%$... It is therefore used here as a relative ordering index across observation geometries, not as an absolute radiometric prediction" (§3.2, ~line 416-421), plus the direction-of-bias check that retaining the $\sin\theta$ factor enlarges the gain from $+40\%$ to $+94\%$ (conservative proxy).
- **Dispersion and uncertainty reported where it costs the authors.** Table 1 gives mean ± SD per class; $N_{50}$ carries a bootstrap interval and the caveat "weakly constrained... only the two sparse densities... carry informative deficit proportions ($80\%$ and $10\%$)"; the S4 third-objective edge is reported as "negligible in distribution" ($\delta=+0.03$) even though it is statistically signed.
- **Control experiments that go beyond the minimum.** Hot-start, perturbation ($\sigma$ sweep), random-selection ("5,000 random task selections per scenario"), and doubled-budget controls, each with its own sample size stated.
- **Reproducibility artefacts named.** "NSGA-III via \texttt{pymoo} 0.6.1.6", scenario generators, processed JSON/CSV, repository URL, and an explicit note that binary scenario files and pickles are regenerable (§ Data Availability, ~line 1566-1571).

## Findings

### R1-01 [MAJOR] The "single-objective GA control" is degenerate, so the paper's marginal-value claim has no search control
- Quote: "In practice this guard makes GA-P-BL output numerically identical to G-BL in 199 of 200 scenarios (the single exception improves profit by $13.5\%$; mean $f_1^*$ differs by less than $0.001$)... GA-P-BL therefore acts as a control that confirms the greedy profit baseline rather than as an independent solver." (§4.4 GA-P-BL, ~tex line 658-662)
- Problem: an arm that returns the greedy schedule in 199/200 cases and is floored at "never worse than G-BL" by construction cannot control for the effect of *searching*. The paper's conclusion sentence — "the present claims therefore concern the marginal value of adding physical objectives rather than profit-oriented search alone" (§7.1, ~line 1375-1376) — is precisely the claim this arm fails to test, because there is no matched-budget arm that searches without physics and is allowed to be worse. The two 100×200 evolutionary arms both hot-start from G-BL and only the MOEAs are permitted to trade coverage away. The Introduction's framing ("a single-objective genetic algorithm with greedy hot-start (GA-P-BL, a control...)") reads as a control; §5 neuters it.
- Fix (cheapest first): (i) report how many of the 200 runs the guard actually fired on, and how many runs the unguarded GA scheduled differently; (ii) add one plain random-initialised single-objective GA at matched budget (no floor, no hot start). Either one turns the control into evidence; otherwise the Intro/Conclusion wording must be narrowed to "the marginal value of adding physical objectives *given a greedy-anchored search*".

### R1-02 [MAJOR] Two incompatible reproducibility models, and a 4-point basis for the "stochasticity is negligible" claim
- Quote: "Each scenario is solved once per stochastic configuration (the scenario seed governs instance generation; the NSGA-III sampling seed is fixed at the library default while operator-level random draws are not pinned), so within-instance search stochasticity is not replicated; the released processed results pin the exact front realizations analyzed." (§5.4, ~tex line 849-853)
- Quote: "scenario generators, fixed seeds and configurations, processed JSON/CSV results, analysis scripts, and figures are available" (§ Data Availability, ~tex line 1566-1567)
- Problem: the design section says reruns are *not* pinned and that the archived artefacts are the record; the Data Availability statement promises "fixed seeds" that would let others rerun. A referee reading both will ask which it is, and the answer determines whether the paper is reproducible at all for the MOEA results. Compounding this: the claim that within-instance stochasticity is negligible rests on "five repeats of each NSGA-III solver on one variant-A scenario per class reproduce bit-identically at S1 and S4, and where variation appears (S2, S3) the within-instance standard deviation (SD) of the knee values stays at or below $0.004$" (~line 854-858) — four scenarios in total, from which a blanket statement is made about all 200. "Bit-identically" with unpinned operator draws is also unexplained (it implies effective determinism, e.g. a fixed global RNG seeded from the scenario).
- Fix: one paragraph stating exactly what is seeded (scenario seed, pymoo seed, global numpy seed or none), what is guaranteed to reproduce, and what is not; and report the replicated-run check on a larger, named subset (e.g. ≥10 scenarios per class) with per-class within- vs between-scenario SD ratios rather than a single maximum.

### R1-03 [MAJOR] The variant-C correlation contradicts the paper's own $\psi$-only limit
- Quote: "in the $\psi_{\text{sq}}$-only limit both rise with $\cos\psi_{\text{sq}}$ ($r_\psi = +0.997$)" (§6.4, ~tex line 1129-1130)
- Quote: "variant C removes incidence ($f_2=\cos\psi_{\text{sq}}$, $f_3=\cos^3\psi_{\text{sq}}$) and the correlation holds at $-0.65$, indistinguishable from variant A" (§6.4, ~tex line 1171-1173; variant definition in §6.5, `_ablation_section.tex` lines 16-17)
- Problem: as quoted, the two states are inconsistent. Under variant C's own definitions both metrics are monotone increasing functions of one variable, so their within-schedule Pearson correlation cannot be negative, let alone $-0.65$. The only coherent reading — the Fig. 7 correlations are always computed on the full-physics metrics, evaluated on each variant's produced schedules — is stated nowhere, and Fig. 7's caption ("Correlation between the geometric ($f_2$) and radiometric ($f_3$) objectives... for the four objective variants") does not disambiguate. Since this sentence carries the mechanistic conclusion ("Configurations that see $\psi_{\text{sq}}$ select schedules spanning the $\theta_{\text{elev}}$ trade-off, whereas configurations blind to squint leave the within-schedule geometry at envelope statistics"), an ambiguous metric definition sits under a load-bearing inference.
- Fix: state in §6.4 and in the Fig. 7 caption which pair of metrics is correlated (recommend: the fixed full-physics pair, applied to every variant's schedules), and rewrite the variant-C sentence accordingly; if instead the variant's own definitions are used, explain the sign.

### R1-04 [MAJOR] The dense-regime boundary is confounded with an artificial resource ceiling, and the control that defends it has the same size as the effect
- Quote: "$\sum_{i \in \mathcal{S}} e_i \leq E_{\max}$ and $\sum_{i \in \mathcal{S}} m_i \leq M_{\max}$, where $E_{\max}=10^7$ and $M_{\max}=10^{11}$ (arbitrary units) and typical per-task consumptions are $e_i = 5\times10^4$ and $m_i = 5\times10^8$. Both caps therefore translate into the same ceiling of 200 concurrently scheduled tasks." (§3.3, ~tex line 557-562)
- Quote: "coverage stays flat at 200 of the 300 targets (all ten scenarios at the ceiling for $\sigma \le 0.5$" (§6.6 Perturbation, ~tex line 1279-1280)
- Quote: "shifts quality by at most $+1.64\%$ relative to the standard budget, so the sub-$2\%$ dense-regime margins reflect coverage pressure and not premature convergence" (§6.6, ~tex line 1297-1300)
- Problem: three things stack. (a) Two nominally independent resources are calibrated in arbitrary units to an identical ceiling, so only one constraint is in fact exercised; no sweep of $E_{\max}$/$M_{\max}$ is reported. (b) At S3 ($N=300$) the solver can never exceed 200 tasks, and the paper's own perturbation control shows all ten tested runs pinned at 200 — so "convergence to the greedy coverage anchor" at S3 is partly "everyone hits the same wall", a fact that a referee will locate immediately given Table 1's $f_1^*\to1.00$. (c) The budget-doubling control that is used to rule out premature convergence perturbs quality by "at most $+1.64\%$" on $n=10$ scenarios, while the margin being defended is "<2%" — the control's sensitivity is the same order as the effect, so it licenses neither conclusion.
- Fix: report the dense-class results separately for scenarios where C3–C4 binds and where it does not (the paper already has the counts: "20 of 50 G-BL schedules at S3 and 27 of 50 at S4"); add an $E_{\max}$/$M_{\max}$ sweep at two or three ceilings; and either enlarge the budget control or state that it is underpowered to discriminate the two explanations.

### R1-05 [MAJOR] "Re-optimising observation times" is not separated from re-selecting targets
- Quote: "In sparse request sets, re-optimising observation times buys large quality gains at a stated coverage price: $+40\%$ in radiometric quality at a $15\%$ coverage cost" (§8 Conclusion, ~tex line 1522-1523)
- Quote: "the elevation-plane incidence angle varies by only a few degrees across a visibility window (mean $\sim 1.5^\circ$ in the S1 scenarios), whereas the squint angle sweeps $\sim 20$--$35^\circ$" (§6.5, `_ablation_section.tex` lines 130-132)
- Problem: the ablation's own mechanism result means that within a window the two quality objectives move *together* (both rise with $\cos\psi_{\text{sq}}$); the only genuine conflict is across targets. So the observed quality change is a mixture of "which targets are acquired" and "when in the window each is acquired", and no arm in the paper isolates the two. G-SM is timing-only with greedy selection and is the strongest quality performer in the paper; D is selection-without-quality; the MOEAs are both. The paper never presents this as the 2×2 it nearly is, and the headline sentence attributes the whole effect to timing.
- Fix: add the missing cell (quality-aware selection with earliest-time placement), or at minimum state explicitly that G-SM bounds the timing-only effect and the MOEA arm bounds timing+selection, and reword the Conclusion sentence to match.

### R1-06 [MAJOR] No exchange-rate / matched-coverage comparison, which is what the operational recommendation actually needs
- Quote: "the knee point trades $14\%$ coverage for $+33\%$ $f_2$, while the best-coverage front point still gives $+12.5\%$ $f_2$ at zero coverage cost, a configuration preferable when coverage cannot be sacrificed" (§7.2, ~tex line 1423-1425)
- Problem: the operational guideline is an exchange rate, but the paper never reports or compares one. Using the paper's own Table 1 numbers at S1: G-SM reaches $f_3=0.722$ at $f_1^*=0.51$; MOEA-3 reaches $0.698$ at $f_1^*=0.85$. At S2–S4 G-SM matches or beats MOEA-3 on $f_3$ at roughly a third of the coverage. A referee will therefore ask why a one-line heuristic is not the recommended operating point in the quality-priority regime — the paper answers this only qualitatively ("G-SM occupies a different operating regime", ~line 892) and by noting its HV is highest.
- Fix: report Δquality per unit Δcoverage for each solver at each class (or a coverage-stratified quality table interpolating the MOEA front), and let the recommendation follow from that table rather than from the knee convention.

### R1-07 [MINOR] Effect-size statistic and its thresholds are on different scales
- Quote: "we report the matched-pairs sign statistic $\delta_{\text{pairs}} = (W - L)/n$... the conventional unpaired form gives smaller magnitudes for the same comparisons (e.g. $+0.57$ versus $+0.88$...), and Romano's thresholds are applied to that conventional form wherever both are quoted." (§5.3, ~tex line 798-805)
- Problem: $\delta_{\text{pairs}}=(W-L)/n$ is a signed dominance proportion, not Cliff's $\delta$; it is called "Cliff's $\delta$" at the point of use ("Cliff's $\delta = +0.99$", §6.2, ~line 984; "Cliff's $\delta = -1.0$", ~line 986). Where only the paired form is quoted — which is most headline contrasts — the threshold mapping is undefined, and the same numeric threshold is being applied to a statistic with roughly twice the scale.
- Fix: either always print both forms side by side, or rename the paired quantity and give it its own calibration.

### R1-08 [MINOR] A "95% shuffle interval" estimated from 20 shuffles
- Quote: "A permutation null that shuffles the visibility-window-grid $\theta_{\text{elev}}$ and $\psi_{\text{sq}}$ marginals within each density class gives $r_{\text{null}} = -0.60$ to $-0.62$ across classes (95\% shuffle interval within $\pm 0.02$, 20 shuffles per class)" (§6.4, ~tex line 1111-1114)
- Problem: with 20 shuffles the 2.5th and 97.5th percentiles are effectively single observations; the quoted interval width is not an estimate of a 95% interval. Also, two different nulls are computed ($-0.60$ permutation, $-0.28$ Monte Carlo) with no stated criterion for adopting the permutation value ("We adopt the empirical-marginal permutation value as the factorized null", ~line 1117) — the choice materially moves the reference against which $-0.62$ is judged "null strength".
- Fix: ≥1,000 permutations, or report the observed shuffle range rather than a nominal 95% interval; and add one sentence justifying the null choice (the permutation preserves the empirical marginals, hence is the correct null for "same marginals, no LOS coupling").

### R1-09 [MINOR] The omnibus test is run on the metric the paper disqualifies
- Quote: "The Friedman test on pooled HV confirms overall differences among the five solvers across all 200 scenarios ($\chi^2=669.02$, $p<10^{-140}$...)" (§7.1, ~tex line 1353-1354)
- Problem: §5.3 states that HV's ranking inverts when a single-point solver is included and that "HV is not interpreted as a standalone quality judgment". The omnibus hypothesis test is nonetheless run on HV, and the paper concedes it is "driven largely by the within-scenario HV dispersion of the two multi-point NSGA-III solvers". A test whose null is largely about front cardinality cannot support "overall differences among the five solvers" as a quality statement.
- Fix: run the omnibus per objective (or on the $\delta_{\text{pairs}}$ matrix), or explicitly label the HV omnibus descriptive.

### R1-10 [MINOR] The multiple-comparison family changes between sections and excludes the stress classes
- Quote: "the four-variant ablation of \S\ref{sec:ablation} applies $\alpha=0.05/12$, the 12 being the three non-physics variants by four density classes against A within each reported metric" (§7.1, ~tex line 1360-1363); Table 4 caption repeats "the family comprises the 12 variant-by-class comparisons".
- Problem: the ablation actually runs six classes; the S5/S6 comparisons are reported with $p$-values ($1.6\times10^{-13}$, $1.8\times10^{-15}$, $1.2\times10^{-5}$) but sit outside the declared family, as do the $f_2$/$f_3$ comparisons if the family is per-metric × 4 classes × 3 variants (12) rather than per-metric × 6 classes (18). The family definition should also account for the main table's $\alpha=0.05/10$.
- Fix: enumerate all families in one place, or mark S5/S6 as exploratory.

### R1-11 [MINOR] The abstract's closing sentence generalises a G-BL-seeded MOEA-2 boundary to "quality-aware SAR scheduling"
- Quote: "Mission planners can read the two boundaries as a quantitative rule for when quality-aware SAR scheduling justifies its coverage cost." (Abstract, ~tex line 57-59)
- Problem: the density boundary is estimated from MOEA-2 alone, on G-BL-seeded fronts, under the 200-task ceiling; the abstract's own qualifier ("under greedy hot-start initialization") covers the hot start but not the solver restriction. The paper's own G-SM results show a quality-aware method whose advantage does *not* vanish at density ($f_3=0.756$ vs $0.616$ at S3, $0.786$ vs $0.675$ at S4) — it just costs coverage. So "quality-aware scheduling" as a category is not bounded by this rule; "quality-aware *NSGA-III with a greedy hot start*" is.
- Fix: name the solver class in that sentence, and state the exchange-rate caveat in the same breath.

### R1-12 [MINOR] Highlights misattribute the $+40\%$ to the third objective
- Quote: "Third objective adds +40\% (NESZ-ordering index) at sparse density, 15\% coverage cost" (`highlights.tex` line 22)
- Problem: the controlled marginal value of the third objective is $+4.9\%$ under the matched rule ($+6.2\%$ under the solvers' own knee rules); the $+40\%$ is the whole physics-aware MOEA-3 formulation against G-BL. As printed, the highlight assigns the larger number to the smaller effect — and highlights are what a reader who never opens §6.4 will remember.
- Fix: "Physics-aware objectives add +40% NESZ-index quality at sparse density for a 15% coverage cost; the third objective's own margin is +4.9%".

### R1-13 [MINOR] Unverifiable/unexplained statements that a referee can key on
- Quote: "reproduce bit-identically at S1 and S4" (§5.4, ~line 856) — with operator draws unpinned, "bit-identical" needs one sentence of explanation, otherwise it reads as an unchecked assertion.
- Quote: "the S1 coverage reversal under variant D... currently lacks a mechanistic explanation" (§7.4, ~line 1486-1488) — the paper is honest, but the sentence sits next to the ablation's core claim; consider stating what experiment would settle it, and whether the claim "solver outcomes become invariant to the choice of physical objectives at high density" is robust to that explanation.
- Fix: both are one-paragraph edits.

## Recommendation signal

**Major Revision.**

The methodological core (null decomposition, matched-rule third-objective control, budget-matched arms, honest limitations) is publishable and in places better than the field norm. What blocks acceptance is that three load-bearing claims rest on evidence the paper does not quite supply: the search-control arm is degenerate (R1-01), the reproducibility contract is self-contradictory (R1-02), and both operational boundaries are measured under an artificial ceiling and a greedy anchor whose removal changes the picture (R1-04, R1-06, R1-11).

Three conditions that would move my verdict to Accept:
1. **Resolve the definitional contradictions**: R1-03 (which metric pair Fig. 7 correlates — one caption line plus one rewritten sentence) and R1-02 (one paragraph stating exactly what is and is not seeded; larger replication subset).
2. **Report the decision-relevant comparison**: quality-per-coverage (matched-coverage) for every solver including G-SM at every density class, and re-scope the abstract's "quantitative rule" sentence to the solver class actually measured (R1-06, R1-11).
3. **Give the physics-objective claim a search control**: either an unguarded / random-initialised single-objective GA at matched budget, or an explicit narrowing of the "marginal value of adding physical objectives" claim plus the guard's firing count (R1-01) — together with a dense-class split on where the 200-task ceiling binds (R1-04).

Items R1-05, R1-07–R1-10, R1-12, R1-13 are textual/analysis revisions; they do not by themselves block, but R1-05 changes what the paper's headline sentence is allowed to say.

---

## Appendix — reading log (raw observations, in reading order; the basis for the findings above)

### Chunk 1 (tex 1–320: frontmatter, abstract, Introduction, Related Work)
- Abstract (line 42) "Across 200 scenarios spanning 20 to 500 targets"; Intro line 131-132 "200 systematically varied scenarios across four density classes ($N=20$ to $N=500$)". Consistent.
- Two experimental campaigns coexist without their relationship being stated in the Introduction: 200 scenarios (contribution 1, line 164-165) and "four objective-function variants over six scenario classes, 300 scenarios per variant" (contribution 4, line 179-180).
- Effect sizes quoted without dispersion or tests in the abstract and Introduction: +34%/+14% (43-44), +40%/+15% (44-45), +4.9% (45), +33.7%/+14% (134), +12.5% (135), +28%→+2.3% (47-48).
- GA-P-BL described as "a control that returns the greedy schedule whenever it fails to improve profit, so it is never worse than G-BL" (127-129) — asymmetric by construction, flagged for the budget-fairness dimension.
- Two different quantities date the same boundary: "$N_{50}\approx51$" (171) and "vanishes beyond $N\approx150$" (49).
- Correlation claims (52-55, 173-178) carry no $n$, CI or null-construction detail in the abstract/Intro.
- Line 265: amplitude weighting dropped as platform-constant — stated, legitimate.

### Chunk 2 (tex 321–640: formulation, constraints, solver overview)
- Eq. (f1) line 371: all coverage is relative to the G-BL run on the same scenario; baseline is 1.00 by construction.
- Line 376-381: "GA-P-BL output is identical to G-BL in all but one of the 200 scenarios" — the single most consequential design fact for the comparison.
- f3 caveat, lines 408-448: plane-Earth $R$ underestimates $R^3$ by ~13% at 47°; suppressed $\sin\theta$; "relative ordering index... not an absolute radiometric prediction". Then "Recomputing... enlarges the MOEA-3 gain over G-BL from $+40\%$ to $+94\%$" (433-437) — one alternative metric, no interval.
- Internal tension in the same subsection: mean $|\psi_{\text{sq}}|$ = 16–24° with 90th percentile 32–39° (439-441) versus "solver convergence to low-squint regimes removes the alignment axis" (472-476).
- C1: $|\psi_{\text{sq}}|\le45^\circ$ declared a controlled experimental envelope (502-507) — properly scoped.
- C3–C4: both caps calibrated to the same 200-task ceiling in arbitrary units (557-562); binding counts disclosed (563-570).
- "C2 is the dominant active constraint in most dense-regime scenarios" (550-555) qualified four lines later by C3–C4 binding in 20/50 and 27/50.
- First named effect size: "Cliff's $\delta=+0.99$" (632).

### Chunk 3 (tex 641–960: solver details, setup, metrics, Tables 1–2)
- Budgets: all evolutionary arms 100×200 with the same operators (649-653, 668-669). Greedy arms have no search.
- GA-P-BL guard restated with the 199/200 consequence (655-662); firing count not given.
- Scenario design 4×5×10 = 200 (696-732); variant-A-only replication reported and does reproduce saturation (737-744); S7/S8 used only in the scale analysis and only for MOEA-2 + greedy arms (747-752).
- Replication design and the 4-point replicated-run check (845-860).
- Statistical pipeline: Friedman + Wilcoxon with Bonferroni 0.005, Cliff's δ with Romano thresholds, $\delta_{pairs}$ (779-805). HV demoted to secondary because its ranking inverts with a single-point solver included (782-785); Fig. 1's headline panel is nevertheless the HV distribution (954).
- Selector sensitivity checked at the knee (826-835).
- Table 1: dispersion present; several dense-class contrasts smaller than the SDs (S2 $f_2$ 0.317±0.026 vs 0.329±0.030; S3 0.342±0.026 vs 0.343±0.026; S4 $f_3$ 0.675±0.074 vs 0.680±0.073).
- Table 1 counter-evidence to a headline sentence: G-SM $f_3=0.756$ (S3) and $0.786$ (S4) versus G-BL 0.616 and 0.675.
- Line 764-767: 0.5 s C1 scan over 76,190 windows, zero violations; median within-window 30 s squint change 11°.

### Chunk 4 (tex 961–1280: squint regime, scale sensitivity, mechanism, HV)
- §6.2: $+0.99$ paired (199/200), $-1.0$ on raw $f_1$ with the normalization degeneracy explicitly handled (986).
- §6.3 / Table 3: threshold operationalised as $P(f_1^*<0.95)$, MOEA-2 only; $N_{50}\approx51$, bootstrap $[37,64]$, caveat stated (1055-1062).
- §6.4 nulls: permutation $-0.60$ to $-0.62$ from 20 shuffles/class; Monte Carlo $-0.28$; permutation adopted without a stated criterion (1111-1117).
- §6.4 inconsistency: $\psi$-only limit $r_\psi=+0.997$ (1129-1130) versus variant C $-0.65$ (1171-1173).
- §6.4 range-restriction control (1178-1181) and third-objective matched-rule comparison (1188-1215).
- §6.6 initialization control: random init reaches $f_2=0.505$ vs 0.395 at S1 while losing $0.393$ of $f_1^*$; the anchoring admission follows (1259-1272).
- §6.6 perturbation: all ten S3 runs at the 200 ceiling (1279-1280).

### Chunk 5 (tex 1281–1588: controls, Discussion, Limitations, Conclusion, back matter)
- Chance control: 5,000 random selections on five S1 scenarios (1287-1293).
- Budget control: $+1.64\%$ on $n=10$ used to defend a $<2\%$ margin (1295-1299).
- Random-init variant D: $f_2=0.349\pm0.016$ at S3 at a coverage cost (1300-1309).
- §7.1 finding (2) sentence lacks a main verb (1337-1341); omnibus test is on HV (1353-1354).
- §7.2 agility sweep 45°/25°/15° with 50 paired scenarios per cap (1398-1417); operational guideline as an exchange rate (1419-1431).
- §7.4 limitations: family-specific $N_{50}$, hot-start conditionality, resource ceiling, fixed dwell, small control samples, missing learning-based benchmark (1459-1512).
- § Data Availability: pymoo 0.6.1.6, "fixed seeds and configurations", repository URL (1566-1571) — in tension with §5.4.

### `sections/_ablation_section.tex`
- Four variants A–D with D as a genuine null model; "six scenario classes × 50 seeds = 300 runs (total: 1,200 runs across A--D)" (lines 5-36).
- Variant A reproduces Table 1's MOEA-3 row exactly at S1–S4 — internally coherent.
- Family of 12 (3 variants × 4 classes) declared; S5/S6 reported outside it (Table 4 caption; lines 159-171).
- Variant C defined as $f_2=\cos\psi$, $f_3=\cos^3\psi$ (lines 16-17) — the basis for R1-03.
- Mechanism: within-window $\theta$ varies ~1.5°, $\psi$ sweeps 20–35°; incidence conflict "operates through the across-window/aggregate geometry rather than through per-window selection" (lines 128-137).
- S5/S6: D worse on $f_2$ by ~11%, C indistinguishable, B marginally better on $f_2$ (lines 159-171); D gains 17%/8% raw profit over A.

### `highlights.tex`
- Four bullets; bullet 3 (line 22) attributes $+40\%$ to "Third objective" — the controlled margin is $+4.9\%$.

### Checks performed
- Grep for "matched coverage|equal coverage|same coverage|coverage-matched|exchange rate|per unit coverage" over the main tex and the ablation section: **zero hits** — confirming R1-06 (no exchange-rate comparison anywhere).
