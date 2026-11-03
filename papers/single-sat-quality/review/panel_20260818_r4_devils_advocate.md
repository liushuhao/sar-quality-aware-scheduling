# Devil's Advocate Review — Panel R4 (2026-08-18)

**Paper:** Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite: Balancing Profit, NESZ, and Geometric Resolution
**Target:** Advances in Space Research
**Mode:** full, Devil's Advocate seat
**Data pre-gate:** PASS (165/0, CALIBER OK @ 3372e2e; hard-constraint audits all 0). No data-integrity attacks below — argument only.
**Verdict:** **0 CRITICAL, 6 MAJOR, 5 MINOR.** No CRITICAL found; per IRON RULE the editorial seat is not forced away from Accept, but the MAJORs below materially weaken the headline and require revision before the "saturation boundary" framing is publishable as written.

---

## Strongest Counter-Argument

The paper sells an *empirical saturation boundary for physics-aware multi-objective scheduling* as its headline contribution, but every load-bearing element of that boundary is conditional on a choice the authors themselves made, and each condition is disclosed separately while their **conjunction** is never synthesized for the reader. The dense-regime "redundancy" of the third objective rests simultaneously on (i) G-BL hot-start seeding — without it random-init `f1*` deficits are 0.39–0.68 (lines 1087–1088), so MOEA does **not** converge to the anchor; (ii) best-known NSGA-III fronts whose true Pareto set is explicitly unknown and "intractable for N≥20" (lines 1072–1075); and (iii) a reference-point count that jumps 7× from MOEA-2 (H=13) to MOEA-3 (H=91) (lines 586–589), so the +7% S1 `f3` gain credited to "adding the objective" is entangled with "adding 78 reference directions." No one of these is hidden. But the claim "at operational densities the third objective is redundant" is, in light of their conjunction, more precisely: *under G-BL-seeded NSGA-III with unmatched reference points and an unproven frontier, the solver found no dense-regime differentiation.* That is a much narrower statement than "empirical saturation boundary," and it cannot bear the operational recommendation ("use greedy at N≳300", lines 1262–1264) without externalizing the very caveats that produced it.

Meanwhile the result that **is** anchor-independent — the geometric coupling (r_null=−0.51, per-schedule r=−0.72 at S1, envelope −0.97 vs schedule −0.63) — is the paper's genuine analytical contribution, yet it is buried in §6.4 while the headline rides the conditional empirical result. And the one-line G-SM heuristic (δ=+0.99 on `f3`, HV 0.234 vs MOEA-3's 0.089) captures the radiometric benefit more decisively than the NSGA-III machinery at every density; MOEA-3's only marginal win is retaining ~85% coverage where G-SM retains ~44%, a trade-off point rather than a quality victory. The paper is honest about each of these facts in isolation. The counter-argument is that the abstract and conclusion select the *general* framing ("saturation boundary for physics-aware scheduling") when the *disclosed* evidence supports only a *qualified* framing ("saturation boundary for G-BL-seeded NSGA-III under these experimental conditions").

---

## Issue List

### MAJOR

**M1. Headline generalization drops the hot-start condition that the body proves is necessary.**
- Dimension: argument / claim-to-evidence fit.
- Location: Abstract final sentence (lines 56–58) "our results establish an empirical saturation boundary for physics-aware multi-objective scheduling"; Conclusion lines 1341–1343; contrast with Abstract line 50 and Findings (5) lines 1211–1212.
- The abstract correctly states "This convergence is conditional on G-BL hot-start initialization" (line 50) but the punchline (lines 56–58) and the conclusion's central-finding sentence (1341–1343) drop the qualifier and call it a boundary for the *method class*. The body shows random-init `f1*` deficits of 0.39–0.68 (1087–1088) and states "proximity to G-BL is initialization-dependent" (1094). A boundary that holds only when you seed from the anchor it is measured against is a property of the initialization regime, not of physics-aware scheduling. **Fix:** retitle/requalify every "saturation boundary" occurrence as "for G-BL-seeded NSGA-III," and move the anchor-independent geometric-coupling result to co-headline status.

**M2. The "+7% third-objective value" claim does not control the H=13 vs H=91 reference-point confound.**
- Dimension: methodology / internal validity.
- Location: §4.4 lines 586–589; claim at lines 941–949 and Abstract lines 52–55; caveat buried at Limitations lines 1322–1325.
- Adding `f3` also multiplies reference directions 7× (13→91). The paired Wilcoxon/δ=0.88 shows the *outcomes* differ, but cannot attribute the difference to the objective's physical content rather than to richer search-space coverage. A matched-reference-points control (same H, or MOEA-3 with H=13) is absent. Noting the confound in Limitations does not neutralize it for a claim ("the third objective is density-dependent rather than redundant") that depends causally on the comparison. **Fix:** either run the H-matched control or downgrade "third objective contributes `f3` gain" to "three-objective *configuration* produces `f3` gain," and sharpen the Limitations language from "partly entangled" to an explicit non-attribution.

**M3. HV is called the "primary quality indicator" while being shown to be misleading and excluding the metric's winner.**
- Dimension: methodology / reporting.
- Location: "primary quality indicator" line 681; G-SM HV=0.2341 > MOEA-3 0.0893 disclosed at lines 961–965 but omitted from Table 3 (lines 780–793); χ²=669 reported at line 1219.
- The paper demonstrates that HV rewards frontier cardinality over front quality (lines 966–968), excludes the single-point solvers from the HV table on that exact basis, yet still uses HV as the primary indicator and headline Friedman statistic. A metric you have shown is confounded should be a supporting metric, not the primary one, and the omnibus χ² — which the authors concede is "driven largely by within-scenario HV dispersion" (1222–1223) — should not anchor the statistical-validity claim. **Fix:** reposition HV as secondary; make the per-objective paired comparisons primary; report Friedman on a cardinality-controlled indicator or explicitly mark χ² as descriptive.

**M4. "Redundant at operational densities" overreaches given unknown true Pareto fronts.**
- Dimension: epistemic scope.
- Location: line 147 "renders the three-objective formulation redundant at operational densities"; §6.4 lines 1072–1075; Ablation lines 135–144.
- The authors state the fronts are "best-known approximations" and the true Pareto set is unknown/intractable. From "our seeded NSGA-III found <0.2% differentiation at N≥300" one can conclude "this solver configuration did not differentiate," not "the objective is redundant." The ablation's A–D invariance (Table 5) shows invariance of *this search*, not of the feasible surface — and G-SM reaching `f3≈0.79` outside the MOEA-3 surface (lines 913–915) is direct evidence that feasible high-`f3` dense-regime points exist that the MOEA front did not reach. **Fix:** replace "redundant" with "empirically indistinguishable under the tested search configuration" wherever the dense-regime claim appears, and cite G-SM's off-surface point as the counterexample that forbids the stronger word.

**M5. G-BL is called a "coverage ceiling" while being beaten on profit in one scenario.**
- Dimension: internal consistency.
- Location: "tested family's coverage ceiling" lines 134 and 1264; "near-optimal rather than strict coverage anchor" line 968 (+10.8% on one of 200).
- A ceiling cannot be exceeded. The single +10.8% case is rare but it falsifies "ceiling" literally; the correct word ("near-optimal anchor") already appears one paragraph later. **Fix:** use "near-optimal coverage anchor" consistently; reserve "ceiling" for the resource-bound sense only.

**M6. Generalization universe is narrow relative to the "boundary" claim, and disclosed only in Limitations.**
- Dimension: external validity.
- Location: Abstract/Conclusion "boundary" language vs §5.1 (single 693 km sun-sync orbit, one C-band instrument, p_i uniform 1–10, fixed 30 s dwell, C3/C4 non-binding lines 486–488, no timeliness objective lines 1317–1321).
- The saturation boundary is asserted over an effectively one-point instrument/orbit design with non-binding resource budgets and no latency objective despite time-critical monitoring being the stated motivation (lines 70–71, 1319–1321). Whether `N50≈50` or the dense-regime invariance survives ScanSAR/Spotlight, varied altitude, binding downlink/energy, or urgency-weighted profit is untested. **Fix:** add a single sentence to Abstract/Conclusion bounding the boundary to "single-pass, single-satellite Stripmap under non-binding resource budgets" (the Limitations content exists; it needs to travel upward to the claim sites), and soften "boundary" to "observed transition under the tested configuration."

### MINOR

**m1. Abstract mixes profit-ratio and task-count-ratio in one coverage comparison.**
- Lines 46–47: "retaining roughly twice the coverage (85% vs. 44% of G-BL tasks)." The 85% is MOEA-3's `f1*` (profit); the 44% is G-SM's scheduled-task-count ratio (line 836). They are numerically close because p_i is uniform, but the parenthetic labels both as task ratios. **Fix:** state both on the same metric (prefer task-count ratio for both) or label explicitly.

**m2. The "Pareto-sufficient" definition in §7.1 is admitted non-discriminating, then not used.**
- Lines 1175–1183: the conjunctive rule "cannot bind" and "labels all solvers trivially Pareto-sufficient," then per-objective comparisons are reported instead. This is dead exposition that advertises a criterion the authors immediately abandon. **Fix:** cut the definition or fold its intent into one sentence.

**m3. GA-P-BL as one of "five solvers" is a control, not a solver.**
- Lines 122–125, Table 1, Friedman at line 1219. GA-P-BL is numerically G-BL by construction (lines 571–577). The paper says this plainly, but the "five solvers spanning the methodological spectrum" framing (line 122) oversells a 3-effective-solver comparison plus two controls. **Fix:** describe as "three solvers and two controls."

**m4. "Physics-aware" vs. the admitted plane-Earth proxy.**
- `f3=cos³ξ` under a model that overestimates R³ by ~17% at 47° and omits the sinθ ground-area factor (lines 260–267). The authors correctly call it an "ordering index, not absolute prediction," but the running term "physics-aware" is stronger than "geometry-proxy ordering." **Fix:** one-line qualifier on first use of "physics-aware" in Abstract/Intro.

**m5. N₅₀ precision language.**
- Lines 890–895: the bootstrap CI [30,62] is wide and four of six points are censored ≤1%. The authors do call it "coarse," but the operational guideline (line 1256) cites N₅₀ without the CI. **Fix:** carry the CI into §7.2 when N₅₀ is invoked.

---

## Ignored Alternative Explanations

1. **Search-budget interaction with objective count.** The double-budget control (lines 1156–1164) tests A vs D at 200/400 on 5 S3 + 5 S4 scenarios. It does not test MOEA-2 vs MOEA-3 at matched budget/reference points, which is the exact comparison behind the "third objective adds value" claim. The invariance of A–D at double budget does not certify the A(3-obj) vs MOEA-2(2-obj) contrast.
2. **Crowding/selection as the sparse-regime mechanism, not the physics.** Variant D schedules 3.9 *more* tasks at S1 (19.5 vs 15.6, line 109) and reaches `f1*=1.002`. The paper attributes this to removal of physical objectives, but an equally live explanation is that the extra objectives change NSGA-III's crowding/niching and therefore selection pressure on `f1` independent of geometric content. The Limitations note about alternative crowding operators (lines 1309–1312) acknowledges this for variant D but the same mechanism is not considered for the A-vs-MOEA-2 third-objective claim.
3. **Window geometry, not objective count, may drive S1 gains.** At S1, windows are fewer/narrower and per-window θ varies only ~1.5° while squint sweeps 20–35° (lines 117–119); the +34% `f2` gain may be largely a squint-selection effect available to any solver that varies start times, which G-SM demonstrates. The MOEA's marginal contribution over G-SM is coverage retention, not geometric discovery.
4. **The −0.63 S1 schedule correlation could reflect task *selection*, not time *placement*.** Pooled per-task correlation mixes which tasks are selected with when they are observed. The per-schedule statistic (r=−0.72) partially addresses this but does not decompose selection vs placement.

## Missing Stakeholder Perspectives

- **Mission operators.** The operational recommendation (greedy at dense N) is made without a latency/timeliness objective, yet the motivation is time-critical monitoring. An operator would ask whether greedy earliest-placement (which is latency-favorable) actually wins on the unmodeled timeliness axis — the paper asserts this (lines 1268–1271) without measuring it.
- **SAR system engineers.** f3 is an ordering proxy; a SAR engineer would want NESZ in dB and ground-resolution in meters for at least one worked example, not only dimensionless indices. §7.2 gestures at one (~0.3 m at C-band, line 1247) but the f3 gains are never translated to radiometric units, so "is +41% f3 operationally meaningful?" is unanswered.
- **Metaheuristic methodologists.** The comparison is NSGA-III-only. The authors defer NSGA-III vs MOEA/D vs SMS-EMOA to future work (lines 521–523), but the "saturation" claim is partly a property of reference-point niching; a methodologist would expect at least one non-NSGA-III multiobjective solver before generalizing about "multi-objective scheduling."

## Observations (Non-Defects)

- The geometric coupling analysis (r_null factorization, envelope −0.97 vs schedule −0.63, Monte Carlo validation N=2×10⁵, lines 977–1049) is rigorous, original, and the anchor-independent core of the paper. It deserves headline prominence over the conditional empirical saturation.
- The four-control robustness block (§6.6) is unusually thorough for an ASR methods paper and pre-empts most cheap critiques.
- The ablation's within-solver design (identical NSGA-III params, same G-BL seed, lines 27–34) is correctly reasoned for paired Wilcoxon.
- The explicit statement that GA-P-BL's guard returns G-BL (lines 571–577) and that G-BL is only near-optimal (line 968) is good scientific hygiene.
- Data layer is audited clean (pre-gate passed); none of the above concerns data integrity.

---

*End of Devil's Advocate report. 0 CRITICAL → editorial seat not blocked from Accept; 6 MAJOR require revision to the claim-to-evidence framing, HV methodology, and reference-point attribution before the "saturation boundary" headline is defensible.*
