# Reviewer 1 — Methodology & Statistics

**Paper:** Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite (ASR submission)
**Lens:** experimental design, statistical validity, reproducibility
**Data pre-gate:** PASSED (not re-audited per directive)

**Recommendation: Minor Revision**
**Rigor score: 78 / 100**

The manuscript is unusually self-critical: it discloses the HV point-count confound, the G-BL-anchor normalization, the GA-P-BL collapse, the small hot-start samples, the wide N₅₀ interval, and the H=13/H=91 reference-point asymmetry. Most findings a referee would raise are already named in the text. The issues below are cases where the disclosure is present but does not propagate into claim language, or where a control is one step short of closing the confound it targets. No critical defects in design or data integrity were found.

---

## CRITICAL
None.

---

## MAJOR

### M1 — Das–Dennis reference-point asymmetry confounds the central "+7% f₃" claim
**Where:** §4.4 (MOEA description, H = 13 vs H = 91), §6.4 Phenomenon 2, abstract ("+7%"), §7.4 Limitations ("partly entangled").

MOEA-2 uses p = 12 → H = C(2+12−1,12) = 13 reference directions; MOEA-3 → H = C(3+12−1,12) = 91, a 7× denser reference grid. Under NSGA-III, a finer reference grid improves coverage of the objective space and can lift the attained f₃ of the selected knee even when the third objective carries no additional physical information. The observed +7% f₃ at S1 (0.699 vs 0.654) is therefore not cleanly attributable to "adding the NESZ objective" — it is partly attributable to "searching with seven times as many reference directions." This is a central claim (abstract, contribution 1, conclusion) and the Limitations sentence ("partly entangled") understates a confound that could absorb a non-trivial fraction of the 7% margin.

**Fix:** add a matched-reference control: rerun MOEA-3 with p chosen to give H ≈ 13 (p = 4 yields H = 15) and/or MOEA-2 with p raised to give H ≈ 91 (p ≈ 41, or use two-layer Das–Dennis), on the same S1 seeds. If the +7% persists under matched H, the claim is closed; if it shrinks, report the matched-grid value and weaken the abstract. At minimum, report H alongside every MOEA-2/MOEA-3 contrast and state the +7% as an upper bound on the third-objective effect.

### M2 — The point selected from each MOEA front for Table 1 / per-objective contrasts is unspecified
**Where:** Table 1 (solver profiles), §6.1, §6.4 Phenomenon 2.

G-BL, G-SM, and GA-P-BL produce one schedule → one (f₁*, f₂, f₃) tuple. MOEA-2/MOEA-3 produce a Pareto front of 6.8–33.8 points (§6.4), yet Table 1 reports single mean ± SD f₂, f₃ values for them. The selection rule (knee by minimum Manhattan distance? best f₁*? centroid? the hot-start seed?) is not stated. This matters because:
- The +34% f₂ / +41% f₃ / +7% MOEA-3-vs-MOEA-2 contrasts all depend on which front point is compared;
- Different selectors can flip the sign of the f₂ contrast at S1 (MOEA-3 front contains both higher- and lower-f₂ points than MOEA-2's knee).

**Fix:** state the selector explicitly in §5.3 (e.g., "for each scenario we report the knee solution identified by …"), and report sensitivity to at least one alternative selector (best-f₁* point, or hypervolume-contributing point with maximum f₃). If the qualitative ranking is selector-invariant, say so; if not, qualify the abstract numbers.

### M3 — "Coverage ceiling" language is inconsistent with the manuscript's own counterexample
**Where:** abstract ("coverage anchor"), §6.1 ("tested family's coverage ceiling"), §7.2 ("coverage ceiling", "attain the tested family's coverage ceiling"), §6.4 ("G-BL is a near-optimal rather than a strict coverage anchor"), §7.1.

G-BL is a deterministic earliest-start greedy on an NP-hard problem (Orienteering reduction, §1). One of 200 scenarios yields a MOEA solution at f₁* = 1.108 (§6.4), proving G-BL is not a ceiling. The manuscript correctly says "near-optimal rather than a strict coverage anchor" in §6.4, but §6.1, §7.2, and the abstract repeatedly call G-BL the "coverage ceiling" that greedy methods "attain." This is a framing inconsistency a reviewer will catch.

**Fix:** replace "coverage ceiling" with "coverage reference" or "greedy coverage baseline" throughout, and note in one sentence that G-BL is a strong but non-optimal baseline (the 1/200 overshoot already demonstrates this). The operational recommendation in §7.2 survives this wording change.

### M4 — Hot-start control sample sizes are small, uneven, and the non-monotone S3 peak is not tested
**Where:** §6.6 Hot-start dependence.

Deficits are reported for 10 / 4 / 5 / 5 scenarios per class (×3 seeds). The headline qualitative claim — "deficit peaks at dense S3 (−0.68) … high density does not by itself make random initialization sufficient" — rests on comparing S3 (−0.684 ± 0.050) to S4 (−0.475 ± 0.067). With n = 5 scenarios and within-seed pairing, the S3-vs-S4 gap (~0.21) is large relative to the SEs (~0.02–0.03), but no bootstrap CI or pairwise test is reported, and the uneven cell counts (10 at S1 vs 4 at S2) are unexplained. The manuscript applies the right caveats ("indicative … not precise bounds") but then uses the non-monotonicity to make a mechanistic claim about density.

**Fix:**
1. Explain the 10/4/5/5 allocation (compute budget? scenario availability?) or balance it.
2. Report bootstrap 95% CIs on each deficit and on the S3−S4 contrast.
3. If the S3 > S4 ordering is not robust under bootstrap, replace "peaks at S3" with "is large (≈ 0.4–0.7) at every tested density, with no monotone density trend."

---

## MINOR

### m1 — Variant-C inertness rests on an unsourced quantitative claim
**Where:** ablation section, §"At S1", explanation that θ_elev varies by only "mean ~1.5° in the S1 scenarios" while squint sweeps 20–35°.

The mechanism (θ_elev near-constant within a window → C preserves A's per-window ranking → same selection) is coherent, but the 1.5° figure is not tied to a script, table, or figure. Either cite the computation (script name + summary statistic over the 50 S1 windows) or soften to "varies by only a few degrees across each window, far less than the squint sweep."

### m2 — "Five solvers" overstates a 4 + 1-control comparison
**Where:** §4.1, Table tab:solvers, §1 contributions.

GA-P-BL is numerically identical to G-BL in aggregate (within 0.001) and the manuscript explicitly calls it a control. Describing the study as "five solvers spanning the methodological spectrum" (§1) implies five distinct methods. Reframe as "four distinct solvers plus a single-objective GA control (GA-P-BL), which collapses to the greedy anchor under its never-worse guard." The Friedman test is conservative toward fewer distinct rankings (already noted), so no statistical change is needed.

### m3 — "Random-search calibration" overlabeled for n = 5
**Where:** §6.6 Random-search calibration.

Five S1 scenarios × 5,000 unconstrained samples is a sanity check, not a calibration. Rename to "random-search sanity check" and keep the existing "empirical bound on the tested batch" caveat. The unconstrained sampler (no C2–C4) already prevents this from being a competitive baseline.

### m4 — NSGA-III implementation not identified
**Where:** §4.4.

State whether NSGA-III is pymoo, DEAP, jMetal, or in-house, with version. Required for reproducibility alongside the public-repo statement.

### m5 — HV labeled "primary quality indicator" despite being treated as diagnostic
**Where:** §5.3 ("primary quality indicator"), §6.4 ("should not be interpreted as a standalone quality judgment").

After the excellent point-count discussion, HV functions as a diagnostic, not a primary endpoint. Reorder §5.3: present per-objective paired comparisons (Table 1, Cliff δ) as primary, HV as a secondary front-spread diagnostic. This removes the apparent contradiction between §5.3 and §6.4.

### m6 — Densest-scenario wall-clock omitted
**Where:** §5.2.

The no-wall-clock justification ("claims concern solution quality rather than computational efficiency") is fair, but report the MOEA runtime on one S4 scenario (seconds/minutes) so readers can judge the cost of the "use MOEA-2 at sparse density" operational recommendation. One number suffices.

### m7 — Friedman with three single-point contributors
**Where:** §7.1.

Already acknowledged ("driven largely by within-scenario HV dispersion"). Tighten to one explicit sentence: three of five solvers contribute one HV point per scenario (G-BL ≡ GA-P-BL by construction, G-SM as an extreme single point), so the χ² tests NSGA-III front dispersion more than between-solver ranking; per-objective Wilcoxon/Cliff comparisons carry the inferential weight.

---

## Strengths

- Pre-gate data lock (165 assertions, 1800-solution constraint audit, cross-solver and live-rerun audits) is exemplary; no data-integrity concerns.
- The envelope–null–schedule correlation decomposition (r = −0.97 envelope, −0.51 factorized null, −0.63 to −0.15 schedules) is a genuine analytical contribution and is reported with appropriate Fisher-z transformation and caveats on pooled vs per-schedule correlation.
- Controls are targeted rather than decorative: double-budget, σ-sweep, random-init variant-D, and random-search each close a specific alternative explanation.
- The negative-result framing ("empirical saturation boundary, not a superior solver") is scientifically honest and the abstract does not overclaim.
- Effect sizes (Cliff δ with Romano thresholds) are reported alongside p-values, and the large-N deflation of p is handled correctly.

## Overall

The methodology is sound and the manuscript's self-critique culture is above the ASR median. The four major items are closure gaps on claims the manuscript already half-acknowledges — matched-reference NSGA-III runs, an explicit front-point selector, consistent "reference" not "ceiling" framing, and slightly stronger inference on the small hot-start sample — not redesigns. Minor revision.
