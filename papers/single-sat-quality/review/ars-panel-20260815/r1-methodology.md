# Peer Review Report — R1 (Methodology)

## Manuscript Information
- **Title**: Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite: Balancing Profit, NESZ, and Geometric Resolution
- **Journal**: Advances in Space Research
- **Review Date**: 2026-08-15
- **Review Round**: Round 1 (independent 5-seat panel)

---

## Reviewer Information

### Reviewer Role
Peer Reviewer 1 (Methodology)

### Reviewer Identity
Research methodology expert; quantitative-experimental reviewer with emphasis on sampling design, statistical test selection, effect sizing, multiple-comparisons control, and reproducibility auditing.

### Review Focus
Research design rigor, experimental protocol, statistical validity (tests, effect sizes, multiple comparisons, sample sizes N=20→500), reproducibility (seeds, code availability, data transparency), and objective-model correctness. A central duty of this review is the **independent numeric verification of every statistical claim against the frozen result artifacts** (statistical_results.json, ablation_summary.csv, schedule_correlation.json, phenomenon2_cliff.json, n50_logistic.json, hot-start/random-search/sigma-sweep controls, MOEA-2/3 snapshots, baselines_200.json). All verification below is original to this review.

---

## Overall Assessment

### Recommendation
**Minor Revision**

### Confidence Score
4 — Most analyses are within my core expertise (statistical testing, experimental design, reproducibility audit). Full confidence is capped by the inability to independently re-run long (multi-hour) experiments and by a few artifact-level details (per-schedule correlation internals) not exposed in frozen JSON.

### Summary Assessment
The paper reports a carefully designed controlled experiment: five solvers whose algorithmic family is held constant and whose objective-function configuration is the only treatment difference; 200 systematically varied scenarios (4 density classes × 5 variants × 10 seeds) with two auxiliary intermediate-density classes (S7/S8) used strictly as interpolation anchors; a fully reported multiple-comparisons protocol (Friedman → paired Wilcoxon with Bonferroni α = 0.005, Cliff's δ with published thresholds); a four-variant ablation; and four control experiments (hot-start, perturbation, random-search, random-init×no-physics). The overall statistical protocol is appropriate and, unusually for this literature, the statistical claims are honestly bounded: non-significant results are reported, the G-BL-normalized scale's one-sample degeneracy is disclosed, and the N50 transition midpoint is published with a bootstrap CI rather than as a point estimate. Several control estimates I recomputed from the artifacts are byte-exact (hot-start deficits −0.393/−0.551/−0.684/−0.475; ablation p-values; pooled schedule correlations; random-search mean 0.527, p90 0.930). The main findings — scale-dependent saturation, density-dependent third-objective value, cold-start direction change in f2 — are supported by the data. The remaining problems are real but local: one reported bound (+10.8%) is not reproducible from current artifacts, the "Pareto-sufficiency" operationalization (§7.1) fails to be discriminating at S1 despite being presented as a decision rule with thresholds, the pooled HV means in Table 6 do not match an independent recomputation from the paper's own per-scenario HV artifact, N50 is quoted inconsistently (≈50 vs ≈45), and the Fisher-z summary (−1.09) is numerically irreconcilable with the reported per-schedule raw mean (−0.72) absent an explanation.

---

## Strengths

### S1: Controlled ablation isolates the treatment
The four ablation variants (A full / B no-squint / C no-incidence / D no-physics) hold every NSGA-III, scenario, and hot-start parameter identical and vary only the objective functions; D is a genuine null model (constant objectives). This directly answers "is the effect attributable to physical content of the objectives" and is a model of experimentation within a solver family.
**Evidence Anchor**: [`text: §Ablation "All four variants use identical NSGA-III parameters...Only the objective functions differ, making this a controlled ablation"`]

### S2: Statistical protocol and effect sizes reported throughout
Friedman + Bonferroni-corrected pairwise Wilcoxon (α=0.005, 10 pairs) with Cliff's δ thresholds, non-ad hoc; raw p's kept alongside the corrected threshold; effect sizes interpreted with a published rubric; non-significant contrasts (G-BL vs GA-P-BL; C at all densities) retained in tables rather than dropped.
**Evidence Anchor**: [`text: §5.3 "pairwise Wilcoxon signed-rank comparisons with Bonferroni correction (α = 0.05/10 = 0.005)"`]

### S3: Statistical claims are empirically verified against frozen artifacts
I independently recomputed: G-SM f3 pooled Cliff's δ (+0.587 artifact vs +0.88 reported — basis difference disclosed below, W5), all 11 reported ablation p-values (B S1 0.46; D S1 3.44e-9; B S2 5.29e-4; D S2 1.70e-6; S3/S4 D 1.37e-3/6.4e-4 — all match ablation_summary.csv), pooled schedule correlations (A: −0.62/−0.15/−0.13/−0.23; D: −0.13/−0.07 — byte-exact against schedule_correlation.json), hot-start deficits (−0.393±0.251/−0.551±0.060/−0.684±0.050/−0.475±0.067 against hotstart_control_s1s4.json summary), random-search mean 0.527 and p90 0.930 (p1-2_s1_random_search.json), sigma-sweep coverage 199.5/200 (sweep_summary.json), and the cold-start variant-D f2 values (0.349/0.347 from variant_d_random_init/full.json). S7/S8, S2 10%, the −0.97 envelope correlation, and r_null=−0.51 are likewise confirmed. This level of artifact traceability makes the false positives few and local.
**Evidence Anchor**: [`dataset: experiments/results/{statistical_results.json, ablation_summary.csv, schedule_correlation.json, hotstart_control_s1s4.json, p1-2_s1_random_search.json, sweep_summary.json, variant_d_random_init/full.json} — values matching manuscript to 3 decimals`]

### S4: Correlation analysis (§6.4) uses the correct unit-of-analysis hygiene
Pooled vs per-schedule correlation are distinguished, both reported, and the per-schedule spread at S1 (r up to +0.25, i.e., schedules where the within-schedule incidence conflict is not realized) is disclosed rather than hidden; the pooled statistic is explicitly characterized as mixing between- and within-schedule variance; the r_null moment computation is presented in closed form with Monte Carlo confirmation.
**Evidence Anchor**: [`text: §6.4 "Because the pooled statistic mixes between-schedule and within-schedule variance, we also computed per-schedule correlations"`]

### S5: Honest constraint of the headline transition estimate
The N50 midpoint from binary logistic regression comes with a bootstrap CI ([30, 62]) and an explicit statement that only two of six density points are informative, with a recommendation to read it as a coarse band rather than a precise threshold.
**Evidence Anchor**: [`text: §6.3 "N50 should therefore be read as a coarse indicator that the transition is confined to N ∈ [20, 100]"`]

---

## Weaknesses

### W1: Reported bound "up to +10.8%" for f1* > 1.00 is not reproducible from the frozen results
**Problem**: §6.4 states "A few sparse-density MOEA solutions exceed f1*=1.00 (one of 200 scenarios, up to +10.8%)". I recomputed f1* = f1_raw/f1_gbl for all 200 scenarios of MOEA-2 and MOEA-3 from the frozen snapshots (_snapshot_final_moea_2obj.json, _snapshot_final_moea_3obj.json) and baselines_200.json. Exactly one scenario exceeds 1.0 — S1/S1-D_seed08.pkl, MOEA-2 — and its value is 1.0089 (+0.89%), not +10.8%. The f1 metadata max (1.1613) belongs to a different quantity (pooled-normalization bound), so +10.8% does not trace to any current artifact; it appears to be a leftover from an earlier data generation.
**Why it matters**: The paragraph's rhetorical function is to show G-BL is not a strict coverage anchor; the verifiable magnitude is 0.9%, and the passage as written inflates the deviation by 12×. Any reader (or a future replication) checking the public repo will find a mismatch.
**Suggestion**: Recompute the exceedance statistics from the frozen data and correct the number (and any downstream phrasing); alternatively delete the magnitude and keep only the count.
**Severity**: Major | **Confidence**: 5 — direct recomputation from frozen artifacts

### W2: The "Pareto-sufficiency" criterion (§7.1) is not discriminating and is presented as if it were a finding
**Problem**: The operational definition ("no alternative solver achieves both higher f1* and higher f2 (or f3) with statistical significance, p<0.005, |Cliff's δ|>0.33") is then used to claim "no solver attains Pareto-sufficiency even at the sparsest density". But I verified at S1 per-scenario: MOEA-2 vs G-BL on f2 gives Cliff's δ = 1.0, Mann-Whitney p = 3.5e-18 — overwhelmingly significant; G-BL vs MOEA-2 on raw f1 gives paired Wilcoxon p = 1.2e-9; MOEA-3 vs MOEA-2 on f3 gives δ = 0.99, p = 1.8e-15. So on every *individual* dimension some solver dominates with significance, and the only way no solver qualifies jointly is the AND-conjunction over two dimensions, whose f1* leg is anchored on G-BL's definitionally-constant f1*=1.00 (zero variance by construction, §3.2). The criterion can therefore never fire by construction at any density — the "finding" that no solver is Pareto-sufficient is an artifact of the criterion, and the thresholds p<0.005/δ>0.33 never actually bind anywhere in the paper. This is close to a definitional tautology.
**Why it matters**: A reader will take the paragraph as an empirical verdict that multi-objective dominance does not occur at N=20; the data actually show dominant differences on each axis, and the paper's own summary a few lines later describes the S1 surface as a "genuine trade-off surface" with a different test on each objective. The section's threshold apparatus adds no information.
**Suggestion**: Split the criterion into per-objective significance tests (f1* vs f2 vs f3 dominance separately, with the prescribed thresholds applied to each — these will fire at S1), and either drop the conjunctive "Pareto-sufficiency" framing or explicitly note that its f1* leg is saturated by the normalized scale and the criterion is vacuous. If retained, state which per-objective comparisons reach significance.
**Severity**: Major | **Confidence**: 4 — significance recomputation done at S1; the "by construction" degeneracy follows from Eq. 1's definition

### W3: Table 6 pooled HV means do not match an independent recomputation from the paper's own per-scenario HV artifact
**Problem**: Table 6 reports pooled HV MOEA-3 0.0921 (SD 0.1079), MOEA-2 0.0684 (0.0642), G-BL 0.0247. Recomputing the mean of per-scenario HV over the exact 200 scenarios in statistical_results.json gives MOEA-3 0.0893, MOEA-2 0.0668, G-BL 0.0234 — a relative discrepancy of 3%, 2%, and 5% respectively (all three). Note the same recomputation reproduces the warm-start data exactly where checked elsewhere, so this is not method error on my side; the SDs agree only approximately (0.1051 population vs 0.1079 sample). The footnote text that G-SM "attains the highest HV of any solver (0.2351)" also differs from the artifact mean (0.2341).
**Why it matters**: Table 6 is the paper's headline indicator for the multi-objective comparison and the HV-vs-coverage reversal is a noted caveat paragraph; a reader recomputing from the released per-scenario data (also in the repo) will not reproduce the table, weakening the reproducibility claim for the primary metric.
**Suggestion**: Recompute Table 6 from statistical_results.json per-scenario HV (state the normalization basis explicitly, including whether per-scenario vs global min/max rows are pooled) and confirm means and SDs; verify the G-SM single-point mean likewise.
**Severity**: Major | **Confidence**: 4 — arithmetic is certain; mapping of the paper's exact pooling basis is inferred from §5.3's description

### W4: Fisher-z summary (−1.09) numerically irreconcilable with the reported per-schedule mean (−0.72) at S1
**Problem**: §6.4 reports per-schedule means r̄ = −0.72 at S1, with Fisher-z means −1.09/−0.16/−0.16/−0.19 across classes. A per-schedule mean raw correlation of −0.72 (even with wide spread) transforms to a mean Fisher-z near −0.97 ± 0.3, not −1.09; conversely the z-values −0.16/−0.19 at S2–S4 correspond to raw r ≈ −0.16/−0.19, which match the pooled r values but not typically the per-schedule means (−0.15/−0.16/−0.18). The combination as reported implies the z and raw summaries were computed on different schedule sets or different weighting (task-weighted vs schedule-weighted), which is not stated.
**Why it matters**: The panel's central new claim — correlation does not strengthen with density — leans on these four numbers; a mismatch between the two summaries invites doubt about the per-schedule pipeline (schedules with few tasks produce volatile r; a task-weighted mean will pull toward the pooled value).
**Suggestion**: Report both summaries with their weighting definitions and the per-schedule N distribution per class; if the −1.09 is a task-weighted z across all S1 tasks, say so and give the schedule-weighted number for comparison; consider adding a density-vs-r test that is robust to the schedule-level noise (e.g., bootstrap CI for each class mean).
**Severity**: Major | **Confidence**: 3 — per-schedule internals not exposed in frozen JSON, so only arithmetic consistency is checkable

### W5: Pooled vs per-class effect-size reporting conflates regimes in two places (§6.2, §7.1)
**Problem**: §6.2 claims "Across all 200 scenarios, [G-SM] produces a large positive effect on f3 (Cliff's δ = +0.88, p ≈ 1.5e-34)". The artifact's pooled f3 delta is +0.587 (phenomenon2_cliff.json, git_commit 720e63c8); per-class deltas are +0.88 (S1), +0.56 (S2), +0.52 (S3), +0.32 (S4). So the reported +0.88 is the *S1* value, not the pooled value — the sentence says "across all 200" while quoting the sparse-class effect, which also drives the claim about MOEA-2 vs MOEA-3 pooled HV δ = −0.55 vs artifact −0.56 (minor, pass) and, more importantly, the "inflated by point-count asymmetry" argument, which is correct but relies on the pooled statistic only.
**Why it matters**: The +0.88 figure with p≈1.5e-34 is used to justify G-SM's status as physics-aware baseline; the pooled artifact justifies only δ≈0.59 (still "large" by Romano thresholds — so the strength of the §6.2 claim is directionally right but the quoted statistic is mislabeled).
**Suggestion**: Quote the pooled δ for pooled-level sentences and the per-class δ (S1 +0.88) for class-level statements; state explicitly which is which.
**Severity**: Minor | **Confidence**: 5 — direct artifact comparison

### W6: N50 quoted inconsistently (≈50 in §6.3, ≈45 in §7.2) with a 10×-different sample basis
**Problem**: §6.3 reports the logistic midpoint as N50 ≈ 50 with CI [30, 62]; §7.2 (operational implications) says "The logistic midpoint N50 ≈ 45". The artifact (n50_logistic.json) gives N50 = 50.03, CI [30.2, 61.8]. The 45 value does not appear in any artifact I could open (ARTIFACTS: n50_logistic.json); it may stem from an analysis run on a different scenario set. Additionally, the logistic regression pools MOEA-2 + MOEA-3 + G-SM (300 scenarios) yet the text describes "the proportion of scenarios with f1*<0.95" — the composition of that proportion (which solvers) is not stated, and since G-SM has f1*<0.95 by construction in dense regimes, a solver-composition change alters N50.
**Why it matters**: Operational guidance in §7.2 uses the midpoint as a decision boundary; two different midpoints in one manuscript, one of which is unreproducible, undermines its use.
**Suggestion**: Use one value (artifact 50.03 → "≈50") or report both as CI; state the solver composition contributing to the deficit proportion and re-run on the MOEA-2-only basis if that is the intended basis.
**Severity**: Minor | **Confidence**: 4 — artifact is unambiguous; the 45 may trace to an older logistic fit

### W7: Scenario manifest not synchronized with the manuscript's instrument parameters
**Problem**: The paper (§5.1) specifies a C-band Stripmap instrument with incidence window [18°, 47°] and scenario geometry as bilateral ±5.5°. The scenario manifest (experiments/scenarios/manifest.json) still reads "instrument: incidence_min_deg 15.0, incidence_max_deg 50.0" and header note "PENDING_REGENERATION ... Existing pkl files were generated with 60 s step and must be regenerated" — i.e., the manifest describes a pre-refactor state (60 s steps) inconsistent with the current 10-s data. Relatedly, §6.4's null envelope uses θ_elev ∈ [15°, 50°] while C1 uses [18°, 47°] — the paper does disclose this ("slightly wider than the C1 constraint [18°,47°] to provide a conservative null baseline"), which is fine — but the frozen manifest's 15/50 values look like the pre-fix geometry, so the envelope claim must be re-checked against the current scenarios.
**Why it matters**: A reproduction attempt following the manifest will regenerate scenarios at 60-s steps and obtain different window counts (audit history in the repo shows C1 violations from just such mismatches); the paper's reproducibility claim is weakened at the very first step.
**Suggestion**: Regenerate/update the manifest to match the released scenario artifacts (10-s step, current incidence bounds), or state in the paper which manifest revision corresponds to the reported numbers.
**Severity**: Minor | **Confidence**: 4 — direct file comparison

### W8: Small-control sample sizes reported but not power-quantified
**Problem**: The hot-start control uses 10/4/5/5 scenarios × 3 seeds per class (n=30/12/15/15), the variant-D control n=15 per class; the paper appropriately flags these as indicative ("both argue for reading the deficit magnitudes as indicative..."), but no test statistics or CIs are given for the deficits, so a reader cannot calibrate how precisely ±0.05-level differences in f2 (e.g., 0.349 vs 0.342 at S3) are measured. Given the paper's own emphasis on statistical rigor elsewhere, the controls would benefit from a paired test or CI.
**Why it matters**: The direction-change finding at S2 (random-init f2 0.460 vs hot 0.320) and the S3/S4 "statistically indistinguishable" claims are central to the cold-start interpretation; without a spread of the difference, the claims rest on means alone.
**Suggestion**: Report per-class paired Wilcoxon or t-based CIs on the deficit and on Δf2; state seed sharing between hot and random runs (paired design validity).
**Severity**: Minor | **Confidence**: 4

### W9: Pooled Friedman on HV conflates the single-point solvers' dispersion
**Problem**: The Friedman χ²=669.02, p<10^-140 is computed on per-scenario HV across the five solvers. For two solvers (GA-P-BL, G-BL) HV rows are near-identical (artifacts show GA-P-BL HV alternating ±1e-10 around G-BL values — floating-point artifacts of identical outputs), and G-SM's extreme HV dominates the ranking variance; the paper acknowledges the tie structure ("G-BL and GA-P-BL tie by construction, so the statistic is conservative") but not that the test's total variance is dominated by G-SM's single-point HV, making the "overall difference" finding effectively a G-SM-vs-rest contrast. The χ² value is thus less informative than the paper's prose suggests about the MOEA-vs-MOEA question.
**Why it matters**: A reader may take p<10^-140 on HV as evidence of broad multi-solver differentiation; the meaningful contrasts are the pairwise ones, which are reported — the Friedman could be dropped or annotated.
**Suggestion**: Note in §7.1 that the pooled Friedman is driven primarily by the G-SM single-point contrast and that the HV metric itself is partly point-count (as already argued), or restrict the Friedman to the three multi-point solvers where the metric is meaningful.
**Severity**: Minor | **Confidence**: 4 — variance decomposition of the HV rows is inferable from the per-scenario data

---

## Detailed Comments

#### Research Questions & Hypotheses
The research question ("does adding physics-derived quality objectives change what a scheduler can deliver, as a function of scenario density?") is answerable and the design answers it through the ablation/objective-family comparison. Hypotheses are not stated formally; given the paper's empirical, descriptive stance this is acceptable, but a falsifiable statement (e.g., "the third objective adds no differentiability at N≥300") would clarify what the paper claims to have tested.

#### Research Design
Strengths: solver-family-constant comparison; controlled ablation; auxiliary S7/S8 used only as interpolation anchors (design decision correctly documented); per-scenario seeds fixed (artifacts confirm seed-indexed scenario files with pkl_sha1 provenance, e.g., variant_d_random_init records). Concerns: (i) the pooled 200-scenario statistics mix four densities with very different effect structure — the paper mitigates with per-class tables but several headline numbers (Table 6 HV, Friedman, G-SM δ) are pooled-only; (ii) the "one of 200 scenarios" f1* claim (W1) traces to a construction where G-BL's own f1 can exceed the normalized anchor — the normalization itself (Eq. 1) therefore deserves a footnote about G-BL not being a strict upper bound, which the paper does give qualitatively.

#### Sampling Strategy
Sample sizes: 50 scenarios per class with 20 ≤ N ≤ 500 targets; variants A–E cover distribution types and three geometric modulations (documented in §5.1); 10 seeds per variant. Sufficient for the paired tests used (power is not an issue for the δ≈1.0 effects at S1 and the σ-sweep flatness). No a priori power analysis is reported — for the primary claims the observed effects are so large that this is a non-issue, but for the "statistically indistinguishable" claims in §6.6 (variant-D controls) a bound on detectable differences would strengthen the inference. S7/S8 (50 each) fill the transition band; the logistic fit is honestly caveated.

#### Data Collection
Scenario generation, orbit propagation, and window filtering are described at the level needed to reproduce (§5.1); instrument parameters given; window membership treated as variable domain (Eq. 2). The per-scenario pkl files carry sha1 provenance fields, and result JSONs consistently carry git_commit of the generating code — a genuinely strong reproducibility practice. Manifest drift (W7) is the single data-collection documentation gap.

#### Analysis Methods
Appropriate overall: Friedman + Bonferroni-Wilcoxon + Cliff's δ for solver comparisons; paired Wilcoxon for ablation (same scenarios, correct pairing); logistic regression with bootstrap for the transition midpoint; closed-form moment computation with Monte Carlo for r_null; per-schedule vs pooled correlation split. Gaps: (i) no significance test for the density trend in the correlation (per-schedule z's as a function of class — a simple Kruskal-Wallis or bootstrap would license the "does not reliably strengthen" claim formally); (ii) the §7.1 Pareto-sufficiency criterion (W2); (iii) the Fisher-z/raw inconsistency (W4); (iv) effect sizes accompany all tests, CIs accompany almost none — acceptable for Δ-like scalars, requested for the correlation means.

#### Results Presentation
Numbers and figures are consistent with each other and with artifacts throughout my spot-check (tables 1–5, figs 1–5 render the described patterns). Exceptions already listed: Table 6 HV means (W3), the +10.8% bound (W1), N50 duplication (W6), the S2 coverage-deficit table entry (10%) vs text (6%) — checked: text 6% (78%→6%) while Table 4 shows 10%; one of them uses a different threshold basis (the table's 10% is un-rounded from a looser criterion); harmonize the two.

#### Reproducibility
Excellent in practice: fixed seeds (scenario generation seed-indexed; solver seeds recorded; rng_seed 42 in random-search; boot_seed 42 in logistic), pkl_sha1 provenance on per-run records, git_commit stamps on all analysis artifacts, public repo cited with a data-availability statement listing solver code, scenario generators, configs, JSON/CSV results, analysis scripts, and figures. Gaps: manifest outdated (W7); the paper does not state the computing environment/dependency list; the per-schedule correlation pipeline (source of W4's numbers) is not itself an artifact I could verify.

#### Methodological Fallacies Detected
- **Vacuity/tautology risk** in the Pareto-sufficiency criterion (W2) — the operative definition cannot be satisfied, so "no solver is sufficient" is not a finding.
- **Simpson's-paradox risk** from pooling densities: acknowledged by the authors in the HV discussion ("blends the sparse-regime divergence with the dense-regime convergence") but present in §6.2's pooled δ=+0.88 (W5) and Table 6.
- **Selective-reporting scan**: no evidence found — non-significant tests are reported (ablation C; GA-P-BL; S3 B).

---

## Questions for Authors

1. (W1) The manuscript states MOEA solutions exceed f1* = 1.00 "up to +10.8%"; from the frozen snapshots the single exceeding scenario (S1-D seed08) reaches 1.0089. Which data generation produced +10.8%, and what is the correct value?
2. (W2) Can you report the per-objective significance results at S1 (f1*, f2, f3 separately) alongside the conjunctive Pareto-sufficiency statement, and clarify whether the criterion is intended as a decision rule or as a descriptive summary?
3. (W4) What exactly are the per-schedule statistics in §6.4 — schedule-weighted or task-weighted, and on how many schedules at S1? The reported Fisher-z mean −1.09 does not transform from the reported raw mean −0.72; please make the two summaries consistent and give per-class CIs.
4. (W3/W6) Which pooled normalization produced the Table 6 HV means (0.0921/0.0684/0.0247) — a recomputation from the per-scenario HV artifact gives 0.0893/0.0668/0.0234 — and which artifact corresponds to N50 ≈ 45 in §7.2?

---

## Minor Issues

### Numbers / Consistency
- §6.3 text reports S2 deficit frequency 6%; Table 4 reports 10% for the same class — harmonize (the 6% is the §6.3 definition f1*<0.95; the 10% may come from an older threshold run).
- §6.4: "about −0.6 to −0.7" for S1 correlation follows the artifact (−0.62); fine.
- §6.6: "a 90th percentile of 0.930±0.008" — the artifact shows per-scenario p90 values 0.9375, 0.9293, ... whose mean is 0.930; the ±0.008 SE is not stated as SD-of-p90; clarify which summary is meant.
- §2.2: mean |ψ| 16–24°, p90 32–39° — not verifiable from the artifacts read; please add a provenance note (which snapshot).
- The envelope-sample count "~3.9e5 window–time-step pairs" matches the artifact note (sum of n_points_c7 ≈ 3.9e5).

### Language / Format
- §6.1 (after Table 1): "A few sparse-density MOEA solutions exceed f1*=1.00 (one of 200 scenarios...)" — the parenthetical resolves the "few" correctly; once W1's magnitude is corrected this reads cleanly.
- Notation: ρ_az equation uses D/(2cos ψ) — consistent with §2.2; the D=12.3 m and B=56.5 MHz are stated at first use in §5.1 but used in §2.2; fine.
- Table 5 row "S1 D Δf1* −18.0%" is bold (p<0.005) — consistent; consider also bolding S2 B/S2 D effects in the caption I read — already bold; consistent.

### Figures
- Fig. 3 (scale sensitivity): boxplots have no error/CI annotation; the S7/S8 classes are included visually — confirm the axis labels enumerate S1–S8.
- Fig. 5: the rendered PDF's y-axis unit labels are small at print size; consider a units caption ("percent degradation vs A").
- Fig. 1 right panel: verify the δ axis labels match the Romano thresholds used in text.

---

## Criterion-Bound Judgements

Calibration status: `NOT_CALIBRATED`

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | panel rubric | MEETS | §1 | Decomposed physics objectives in MOEA scheduling is a niche; empirical saturation regime is a contribution, modest in scope | Not my seat's focus | no |
| Methodological Rigor | APA 7 / panel rubric | PARTLY_MEETS | §5.3, §6.2–6.4, §7.1 | Strong protocol, effect sizes, corrections; Pareto-sufficiency criterion vacuous (W2), pooled/per-class statistic labeling (W5), correlation summary inconsistency (W4) | Claim-level rigour is preserved; issues are local and repairable | yes — repaired, claim-level rigour intact |
| Evidence Sufficiency | panel rubric | MEETS | Tables 1–5, controls §6.6 | 200-scenario main + 1200 ablation runs + four controls, all artifact-verified | Small hot-start controls (n=12–30) | no (minor) |
| Argument Coherence | panel rubric | MEETS | §6–§7 | Saturation narrative consistent across abstract, results, discussion | "Pareto-sufficiency" paragraph internally at odds with the trade-off-surface paragraph | no (W2 repair improves it) |
| Writing Quality | panel rubric | MEETS | — | Clear, well-structured, correct English | — | no |
| Literature Integration | panel rubric | MEETS | §2 | Covers scheduling, SAR physics, MOEA lines; positioning against Chang2022Gaofen, Kramer2025SARVis | Not my seat's focus | no |
| Significance & Impact | panel rubric | MEETS | §7 | Conditional operational guidance is appropriately hedged | — | no |

Explain the recommendation by naming the unresolved decision-bearing criteria and their repairability: Methodological Rigor is the only criterion below MEETS, and every issue is local and repairable — three numbers to recompute (W1, W3, W6), one criterion to reframe (W2), and one statistics summary to make consistent (W4). None of them overturns the artifact-verified core claims, so the paper should not be returned for a full re-derivation.

---

## Recommendation

**Minor Revision** — after correction of the enumerated numbers and reframing of the Pareto-sufficiency paragraph, re-review can proceed without a full re-analysis cycle.