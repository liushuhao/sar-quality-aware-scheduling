# Peer Review Report — Journal-Fit Reviewer (EIC seat)

## Manuscript Information
- **Title**: Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite: Balancing Profit, NESZ, and Geometric Resolution
- **Journal**: Advances in Space Research (ASR)
- **Review Date**: 2026-08-15
- **Review Round**: Round 1 (independent panel seat)

---

## Reviewer Information

### Reviewer Role
Journal-Fit Reviewer (Editor-in-Chief seat)

### Reviewer Identity
Senior editor with editorial oversight scope: journal fit vs ASR readership (space research, Earth observation, operational mission planning), originality, significance, structural coherence, and overall quality. Methodology depth is the seat of Reviewer 1; this card judges whether the paper's delivered content matches its claimed contributions.

### Review Focus
(1) Whether claimed contributions match delivered content and whether headline figures trace to the paper's own tables and data artifacts; (2) fit of a single-satellite SAR scheduling study with a negative-result "saturation" headline for ASR's readership; (3) original and significant or re-packaging of known EAO-scheduling results; (4) overall quality signal: internal consistency of the results narrative (esp. §6.4 correlation narrative, ablation interpretation, §6.6 hot-start control), and reproducibility transparency. All headline numbers were spot-checked against the artifacts in `experiments/results/` (statistical_results.json, schedule_correlation.json, baselines_200.json, phenomenon2_cliff.json, n50_logistic.json, moea_2obj/_progress.json) and the ZH mirror.

---

## Overall Assessment

### Recommendation
- [ ] **Accept** — Can be published directly, only minor formatting changes needed
- [ ] **Minor Revision** — Minor revisions needed, no re-review after revision
- [x] **Major Revision** — Substantial revisions needed, re-review required after revision
- [ ] **Reject** — Not suitable for publication in this journal

### Confidence Score
**4** — Mostly within my area of expertise (satellite mission analysis, EO observation scheduling, multi-objective optimization); SAR radiometric detail is adjacent rather than core. All quantitative claims below were verified by direct computation on the paper's published data artifacts.

### Summary Assessment
The paper integrates NESZ radiometric quality and geometric resolution as decomposed physics-derived objectives into an NSGA-III scheduler for single-pass agile SAR Stripmap operations, evaluates five solvers on 200 scenarios across four density classes, and reports a scale-dependent saturation: at sparse density multi-objective search yields real quality gains (+34% f2, +41% f3 at 14–15% coverage cost at N=20), while at operational densities (N≥300) all solvers converge to the greedy anchor. The study is scientifically honest — an unusual and valuable property: the abstract openly states "Rather than identifying a superior solver" and the discussion converts the negative result into a conditional operational guideline. The contribution-to-delivery match is genuine: the two advertised contributions (empirical saturation characterization with ablation and initialization controls; closed-form decomposed quality objectives distinct from prior composite proxies) are both substantively delivered, and every headline figure I checked traces to the paper's tables and data artifacts. However, my spot-check of the results prose against the paper's own artifacts and its own verification-gate tooling found five mismatches — two of them self-contradictions in the mechanism and robustness sections that carry the paper's central claims (§6.4, §6.6), and three wrong or internally inconsistent reported statistics (§6.2, §6.3, §7.2). None of these invalidates a core conclusion, but their concentration in the two sections that constitute the advertised contribution means the results prose requires a full number-vs-data audit, not one-sentence patches.

---

## Strengths

### S1: Scientific honesty and calibrated claim-making
The paper repeatedly refuses to overclaim: HV's point-count confound is disclosed in the Table 3 caption and §6.4; G-SM's winning HV is reported despite inverting the solver ranking; the N50 bootstrap CI is honestly wide; frontier quality is labeled "best-known approximations"; the third-objective story is explicitly "not a mathematical identity"; and the abstract's closing "Rather than identifying a superior solver, our results establish an empirical saturation boundary" sets the right expectation for the whole paper.
**Evidence Anchor**: text: §Abstract "Rather than identifying a superior solver, our results establish an empirical saturation boundary"

### S2: Headline quantitative claims trace to the data
Every headline number I verified against the artifacts is correct: +34% f2 (pooled-mean ratio, 0.394/0.295, with disclosure that the per-scenario-ratio mean is +33.7%), +41% f3 (0.699/0.497), +7% MOEA-3-vs-MOEA-2 f3 at S1 (0.699/0.654), sub-2% gains at S3/S4, hot-start f1* deficits 0.39/0.55/0.68/0.48, G-SM f1* Cliff δ = −1.0 with p ≈ 1.4×10⁻³⁴, and the §6.4 pooled correlations (S1 r = −0.623, S2 −0.152, S3 −0.126, S4 −0.229). The abstract and conclusion are consistent with the body on all claims I could check.
**Evidence Anchor**: dataset: schedule_correlation.json — A_full_physics S1 r=−0.623/Table 1 S1 rows

### S3: A genuinely useful negative result for the ASR operations readership
The core finding — physics-aware MOEA quality gains vanish at operational densities and greedy methods suffice — is the kind of calibration result space-ops planners can use directly, and the conditional guidance in §7.2 (MOEA-2 for sparse geometric-priority requests, G-SM for radiometric priority, G-BL for dense coverage) is concrete and actionable.
**Evidence Anchor**: text: §7.2 "for dense monitoring campaigns ($N \gtrsim 300$), greedy methods ... attain the tested family's coverage ceiling and may be preferable"

### S4: Strong control architecture around the central inference
The "saturation is real, not a search artifact" inference is defended by four independent probe families: the ablation (A–D, 1200 runs), the perturbation sweep, the random-search calibration, and the random-init control — all pointing the same direction, with the A–D invariance at S3/S4 (Δf1* ≤ 0.2%) cross-checked by the H-reference-count asymmetry disclosed in Limitations.
**Evidence Anchor**: table: tab:ablation — S3/S4 rows Δf1* ≤ 0.2% across B/C/D

### S5: Reproducibility posture
Public companion repository, fixed seeds, per-scenario artifacts carrying version hashes, effect sizes with Bonferroni thresholds, and a verification gate over the paper's numbers. This is well above the typical ASR submission standard.
**Evidence Anchor**: text: §Data Availability "The companion repository is publicly available at https://github.com/liushuhao/sar-quality-aware-scheduling"

---

## Weaknesses

### W1: Hot-start control reports the geometric-quality direction backwards — internal contradiction in §6.6
**Problem**: §6.6 states "random-init f2 is higher --- i.e. worse geometric quality --- at sparse density (0.505 vs. 0.395 at S1, 0.460 vs. 0.320 at S2)". Under the paper's own definition (§3.2: "Higher f2 indicates smaller ground pixel area (better geometric resolution)"), 0.505 > 0.395 means the random-init schedules achieve *better* per-task geometric quality, not worse. The same paragraph then asserts "the anchor materially improves both coverage and geometry in the sparse regimes", disagrees with the numbers printed three lines above it, and the closing inference "random initialization reaches comparable or better geometric quality once coverage saturates" is also only partially supported (S4: 0.347 vs 0.380). The ZH mirror reproduces the same contradiction. A reader cannot extract the control's message without recomputing the comparison.
**Evidence Anchor**: text: §6.6 "random-init f2 is higher — i.e. worse geometric quality — at sparse density (0.505 vs. 0.395 at S1)"
**Why it matters**: This control bounds the paper's headline claim ("coverage convergence is conditional on the hot start"); as printed it asserts the opposite of what the control's own data show, garbling the robustness argument that the Introduction's contribution (1) depends on.
**Suggestion**: Rewrite the paragraph's direction gloss: random-init achieves *higher mean geometric quality* at sparse density (at a large coverage cost), is comparable at S3, and is ~9% lower at S4; then restate the paragraph's conclusion consistently with these directions. Sync the ZH mirror.
**Severity**: Major
**Confidence**: 5 — verified against §3.2 definition, §6.6 numbers, and Table 1 (hot-start MOEA-2 S1 f2 = 0.394)

### W2: §6.4 mechanism claim "attenuates most strongly at sparse density" contradicts the section's own numbers
**Problem**: §6.4 states the lower-squint convergence "attenuates the envelope correlation most strongly at sparse density (−0.97 → −0.63 at S1)". The envelope correlation is computed once, pooled across classes (−0.97), so attenuation per class is: S1 0.34, S2 0.82, S3 0.84, S4 0.74 — the *smallest* attenuation is at S1, and it is ~2.5× larger at S2/S3. The claim as written inverts the paper's own reported density dependence.
**Evidence Anchor**: text: §6.4 "attenuates the envelope correlation most strongly at sparse density (−0.97 → −0.63 at S1)"
**Why it matters**: §6.4 is the paper's mechanism section — the analytical heart of contribution (1). A wrong statement about where the attenuation is strongest misleads on exactly the density-dependence the new-objective analysis is meant to establish (the residual negative correlation is in fact roughly density-flat).
**Suggestion**: Restate using the reported values: attenuation from the −0.97 envelope is smallest at S1 (residual −0.63, the strongest remaining conflict) and largest at S2/S3 (residual −0.15/−0.13), i.e., the conflict persists most at sparse density and the residual is density-independent — which is what the following sentence already argues. Text-only correction; no re-analysis needed.
**Severity**: Major
**Confidence**: 5 — arithmetic on values printed in the same subsection and on schedule_correlation.json (S1 −0.623, S2 −0.152, S3 −0.126, S4 −0.229)

### W3: §6.2 effect size "Cliff's δ = +0.88 across all 200 scenarios" does not match the data
**Problem**: §6.2 reports G-SM vs G-BL on f3 "across all 200 scenarios" as δ = +0.88. Direct paired computation on the paper's baselines_200.json (b3 − b1 per scenario, same formula the paper's own verify gate uses) gives δ = 0.99 (199/200 scenarios with higher f3; Wilcoxon p = 1.46×10⁻³⁴, matching the quoted p ≈ 1.5×10⁻³⁴). The value 0.88 instead matches the *S1-group* MOEA-3-vs-MOEA-2 f3 δ in phenomenon2_cliff.json — a different comparison. The paper's verification tool itself notes the printed value is hardcoded with no source.
**Evidence Anchor**: text: §6.2 "Across all 200 scenarios, this produces a large positive effect on f3 (Cliff's δ = +0.88, p ≈ 1.5×10⁻³⁴)"
**Why it matters**: An effect size published in the results section must be reproducible from the released data; the printed value is not, and its provenance is ambiguous (it coincides with a different comparison's value). The error is direction-safe (true δ is larger), but unanchored statistics in the results prose undermine the paper's otherwise strong verification posture.
**Suggestion**: Recompute and print δ = +0.99 (or the computation basis actually used), with the p-value; add δ to the verify gate's asserted set.
**Severity**: Minor
**Confidence**: 4 — direct computation on published artifact; residual uncertainty on the authors' intended aggregation basis

### W4: §6.3 text "6% (S2)" contradicts Table 5 ("10%") and the data (10.0%)
**Problem**: §6.3: "the proportion ... collapses from 78% (S1) to 6% (S2) and to 0% at N ≥ 150". Table tab:scale-sensitivity reports S2 = 10%, and my direct computation on moea_2obj/_progress.json with baselines_200.json normalization gives exactly 10.0% (5/50 scenarios with f1* < 0.95). The text's 6% is stale.
**Evidence Anchor**: text: §6.3 "collapses from 78% (S1) to 6% (S2) and to 0% at N ≥ 150"
**Why it matters**: Text–table–data three-way mismatch in the core scale-sensitivity result; the transition narrative itself is unaffected (both values support the same trend), but the mismatch recurs in the paper's flagship table.
**Suggestion**: Print 10% in §6.3 to match Table 5 and the data; also confirm the tabulated 78% vs my recomputation of 80% for S1 (basis: which scenario set/threshold normalization produced 78%).
**Severity**: Minor
**Confidence**: 5 — direct computation on the paper's progress and baseline artifacts

### W5: N50 quoted as ≈45 (§7.2) and ≈50 (§6.3) — two values for one statistic
**Problem**: §6.3 reports the logistic transition midpoint as "N50 ≈ 50 targets", while §7.2 cites the same statistic as "The logistic midpoint N50 ≈ 45"; the artifact n50_logistic.json gives N50 = 50.03 (CI 30.2–61.8). Both prose values cannot be right.
**Evidence Anchor**: text: §7.2 "The logistic midpoint $N_{50} \approx 45$ (§6.3) provides a coarse indicator estimate"
**Why it matters**: A self-contradicting statistic quoted twice — exactly the class of unanchored number the paper's own discipline (verify gate) exists to catch.
**Suggestion**: Unify on 50 (matching §6.3 and the artifact), or state the computation basis for 45 if a different data subset was used.
**Severity**: Minor
**Confidence**: 5 — two prose locations + the published artifact disagree

### W6: Fig. 5 cannot display the only significant ablation effect
**Problem**: As rendered, fig5_ablation.pdf y-axes span approximately ±0.04 (%), yet Table ablation reports variant D at S1 with Δf1* = −18.0% and Δf3 = −25% — the single significant ablation contrast (p = 3.4×10⁻⁹), and the figure's only dramatic bar. A ±0.04 axis cannot contain a −18 bar, so the figure either clips it or was generated from a different scale than the table; either way the figure hides the paper's most important ablation result. Additionally, fig5 exists only as PDF while figs 1–4 ship PNG/camera twins, breaking submission consistency.
**Evidence Anchor**: figure: Fig. 5 — y-range vs Table ablation D-S1 Δf1* = −18.0%
**Why it matters**: The ablation's key message is "physics matters at sparse density through radiometric quality with a coverage cost" — the figure is the only visual of exactly that contrast.
**Suggestion**: Regenerate fig5 from the same data as Table ablation (e.g., broken y-axis or per-variant panel), verify by eye that the D-S1 bar renders, and add the twin formats.
**Severity**: Minor
**Confidence**: 4 — PDF text extraction of tick labels; cannot fully exclude a scale factor I could not parse

---

## Detailed Comments

### Journal Fit
Fit is strong. ASR's scope covers space mission operations, Earth observation system analysis, and radar remote sensing; agile SAR scheduling with physics-derived imaging-quality objectives sits precisely at that intersection, and the operational guidance (§7.2) speaks directly to space-ops practitioners. The tone, structure (elsarticle), length, and declarative statements are appropriate. A single-author experimental study of this type is within ASR norms. One scope note for the authors: the paper is framed as a calibration of *physics-aware multi-objective scheduling*; because the headline result is negative at operational densities, the paper's value for ASR readers depends on the reliability of the reported statistics — which is precisely where the W1–W5 cluster of unanchored numbers sits. Fixing that cluster is a fit-critical repair, not cosmetics.

### Originality
The decomposition of SAR quality into separate closed-form NESZ and geometric-quality objectives inside a MOEA scheduler is a modest but real departure from the cited prior art (composite quality proxies in Kramer2025SARVis and Wei2025MONP; operational-metric objectives in Chang2022Gaofen; attitude-angle proxies in ChangZhou2025Memetic), and the paper positions itself explicitly against all of them. The saturation-boundary characterization is the more distinctive contribution: an empirical, density-dependent boundary on where physics-aware multi-objective search pays off, with a causal mechanism (lower-squint convergence attenuating the θ-conflict envelope) that is analyzable in closed form. Neither is algorithmically novel — the authors do not claim it to be. Originality is adequate for ASR; it would be stronger with an independent novelty check against the learning-based scheduling frontier (currently only a limitations mention).

### Significance
Local-to-moderate, honestly bounded. The direct operational value (when to use which solver class, at which densities) is real and immediately usable; the scientific value is the density-dependence of objective usefulness in the single-pass single-satellite Stripmap setting, with the multi-pass/multi-satellite generalization explicitly deferred. The N50 ≈ 50 midpoint with CI [30, 62] — backed by only two informative density points — is weak quantification but is transparently flagged as such, which is the right call. The paper will likely be well cited within the EAO scheduling sub-community; broader interest is limited by scope, which the paper states.

### Structural Coherence
Title → abstract → introduction contributions → results → conclusion are aligned; the singular "an Agile SAR Satellite" in the title correctly matches the single-satellite, single-pass scope that the redundancy claim is explicitly confined to. The results section is organized as a coherent argument (overview → squint regime → scale sensitivity → mechanism → ablation → controls). The coherence failures are the internal contradictions documented in W1/W2/W5 — all located in the two sections that carry the advertised contributions. There is no over-promising/under-delivering: every claimed contribution is delivered, and the abstract's numbers all reproduce from the tables.

### Title & Abstract
Title is accurate and informative; the singular-satellite scope is correct. Abstract is well structured (≈200 words), states the setup, the sparse-density gains, the dense-density saturation, the hot-start conditionality, the third-objective nuance, and the boundary-setting disclaimer. One inaccuracy at the level of precision: "peaking at intermediate densities" for the random-init deficit conflicts with §6.6's own "the dense S3 class" (N=300 is Table 4's "transition region"); harmless but should be unified (this is part of the W1-adjacent label drift).

### Introduction
Motivation is persuasive (quality varies with acquisition time; prior work treats quality as fixed attribute or proxy), the research gap argument is explicit, and the two contributions are precisely worded and delivered. The novelty claim "no existing SAR scheduling method treats continuous, physics-derived quality functions as decomposed optimization objectives" is narrow and defensible given the cited set.

### Literature Review / Theoretical Framework
Three structured lines (scheduling / SAR quality modeling / MOEA theory) with up-to-date citations (several 2025–2026), and explicit differentiation from the closest works. Reviewer 2's seat owns depth; my seat notes the review is functional for the paper's purpose without being exhaustive.

### Methodology / Research Design
The five-solver design (differences in objective configuration, not algorithmic paradigm) is a clean isolation of the paper's question; the common G-BL hot-start with a never-worse-than-baseline guard for GA-P-BL, the dashed disclosure that GA-P-BL ≡ G-BL, the mean-based quality objectives decoupled from task count, and the energy/memory budgets set deliberately non-binding (with the limitation disclosed) are all sound. Runtime not reported — acceptable given the claims are about solution quality (stated). C1-only window filtering with C2 checked inline by each solver is clearly described. Reviewer 1 owns the depth here.

### Results / Findings
The results are complete, well-figured (figs 1–4), and statistically framed (Friedman + Bonferroni Wilcoxon + Cliff's δ with disclosed thresholds). The HV confound discussion is exemplary. The findings as *data* are consistent with the artifacts; the findings as *prose* carry the W1–W5 cluster. The correlation narrative (§6.4) correctly reflects the new-caliber data (S1 pooled r = −0.62, per-schedule −0.72, density-flat residual ≈ −0.15…−0.23, D-variant S1 r ≈ −0.13) — the narrative is supported once W2's misphrasing is corrected.

### Discussion
§7.1's synthesis correctly downgrades the findings (no solver Pareto-sufficient even at sparse density); §7.2's conditional guidance is concrete; Limitations is unusually thorough and honest (scope confinement, H-count entanglement, dwell-time fixedness, no learning-based benchmark, random-init extent). The N50 45-vs-50 fork (W5) needs unification; the §7.1 statement "at sparse density (about −0.63 pooled, −0.72 per-schedule)" matches §6.4 and the data.

### Conclusion
Directly addresses the research question, restates the conditional finding, and correctly attributes what is anchor-dependent (coverage convergence) vs anchor-independent (geometric coupling). No over-inference. The boundary statement "$N=20$–$500$" appropriately scopes the claim.

### References
Formatting appears consistent (elsarticle-harv); recency is good; several 2026-dated items will need verification that they are published (not preprint) — Reviewer 2/3 seats own this; flagging as housekeeping.

---

## Questions for Authors

1. **§6.2 f3 effect size**: My per-scenario paired computation on baselines_200.json gives Cliff's δ = 0.99 (199/200, p = 1.46×10⁻³⁴) for G-SM vs G-BL on f3, while the text prints +0.88 — which coincidentally equals the S1-group MOEA-3-vs-MOEA-2 f3 δ in your own artifact phenomenon2_cliff.json. What computation produced 0.88, and which value does the paper intend to print?
2. **§6.6 hot-start geometry**: Under your own definition (higher f2 = better geometric resolution), the random-init schedules at S1/S2 have *better* mean geometric quality (0.505 vs 0.395), yet §6.6 glosses this as "worse" and concludes the anchor "materially improves both coverage and geometry in the sparse regimes". Which reading is intended, and does it survive the S4 data point (random 0.347 vs hot-start 0.380) for the claim "comparable or better ... once coverage saturates"?
3. **§6.4 attenuation claim**: With the envelope correlation fixed at −0.97 across classes, the attenuation you report is smallest at S1 (0.34) and largest at S2/S3 (0.82–0.84). Please restate "attenuates the envelope correlation most strongly at sparse density" in a way that is consistent with these numbers, or correct the intended claim.
4. **Fig. 5**: The rendered y-axes span ≈ ±0.04%, which cannot contain the −18% and −25% D-variant S1 bars reported in Table ablation. Was the figure generated from a different data subset than the table? Please regenerate so the ablation's only significant contrast is visible.

---

## Minor Issues

- **Label unification**: "dense S3 class" (§6.6) vs "peaking at intermediate densities" (abstract) vs "Medium-large, transition region" (Table 4) — pick one consistent stage label for N=300.
- **ZH mirror**: The W1 (and related) errors are mirrored in small-paper-ijae-zh.tex; the bilingual pair must be corrected together.
- **C-variant p-value**: §6.4/ablation says variant C "produces no measurable change" without reporting p; add p ≈ 0.83 (per the Wilcoxon basis used for B) for symmetry.
- **Rounding**: §6.4 variant-D S2 correlation "−0.06" vs artifact value −0.074 (rounds to −0.07); S4 pooled "≈ −0.2 to −0.15" sits slightly outside the −0.229 value — quote the exact values.
- **S1 proportion basis**: text/Table 5 print 78% for S1 f1* < 0.95 while my recomputation on the progress data gives 80%; state the scenario-set and normalization basis for the tabulated 78%.
- **Figure twins**: fig5_ablation exists only as PDF while figs 1–4 ship PNG and grayscale versions.
- **Stale header comment**: the .tex source header still carries the plural "Agile SAR Satellites" title line while \title is singular (harmless but confusing in the repository).

### Language / Grammar
No language-blocking issues; the prose is clear and disciplined throughout.

---

## Criterion-Bound Judgements

Calibration status: `NOT_CALIBRATED`

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | ASR originality bar | PARTLY_MEETS | text: §1 contribution (2) "distinct from the scalar visibility composite of Kramer2025SARVis" | Decomposed physics objectives are a genuine but incremental departure from cited composites/proxies; saturation boundary is a novel empirical characterization, not a new algorithm | Independent prior-art sweep not performed by this seat | yes — contributes to acceptance decision |
| Methodological Rigor | ASR empirical standard | PARTLY_MEETS | text: §5.3 "Friedman test ... Bonferroni correction" | Design, controls, and statistics framework are strong; reported-statistic provenance has verified drifts (W3, W4, W5); depth owned by Reviewer 1 | Methodology detail delegated to Reviewer 1 | yes |
| Evidence Sufficiency | ASR evidence bar | MEETS | dataset: schedule_correlation.json; table: tab:ablation | 200 scenarios × 5 solvers + 1200 ablation runs + 4 control families; headline numbers reproduce; prose drift does not invalidate any core claim | Residual concern bundled in W-cluster | yes |
| Argument Coherence | ASR coherence bar | PARTLY_MEETS | text: §6.6 "i.e. worse geometric quality"; text: §6.4 "attenuates the envelope correlation most strongly at sparse density" | Title→abstract→conclusion arc is aligned; results prose contains two self-contradictions (W1, W2) and a forked statistic (W5) in the two contribution-carrying sections | — | yes — mandatory to fix before acceptance |
| Writing Quality | ASR style | MEETS | text: §Conclusion | Clear, precise, appropriately hedged; minor label drift only | — | no |
| Literature Integration | ASR relevance | MEETS | text: §2.1 "The common limitation of this prior work is that SAR physical quality metrics ... are either absent or approximated by coarse proxies" | Three structured lines, recency 2025–2026, explicit differentiation from closest works | Citation verification owned by Reviewers 2/3 | no |
| Significance & Impact | ASR contribution bar | PARTLY_MEETS | text: §7.2 conditional operational guideline | Genuinely useful calibration result for ops planning; scope honestly bounded to single-satellite/single-pass; local-to-moderate impact | Impact projection inherently uncertain | yes |

Unresolved decision-bearing criteria at this seat: **Argument Coherence** (two verified self-contradictions in mechanism/robustness sections — repairable with text corrections and a full results-vs-data audit, no new experiments) and the **reported-statistics provenance** cluster (W3–W5). Neither is fatal to the science; both are repairable in one focused revision round. The gap between the paper's excellent verification infrastructure and the drift in its prose suggests the latest data-caliber changes (§6.4 correlation narrative, §6.6 controls) were not fully propagated into the results text before submission.

---

## Verdict

**RECOMMENDATION: Major Revision**

Rationale: The manuscript is a well-designed, honestly calibrated, fit-appropriate study whose central findings I independently confirmed against its own artifacts — but the results prose fails to be a faithful mirror of those artifacts in five verified spots, two of which (W1 §6.6 hot-start direction, W2 §6.4 attenuation claim) invert or garble statements in the exact sections that carry contribution (1), and the ablation figure (W6) hides the ablation's only significant effect. The corrections are all within reach (no new experiments; correct values are computable from the paper's own released data), which is why this is Major Revision rather than Reject. The revision should include a full number-vs-artifact audit of §§6.2–7.2 (the verify-gate assert set should be extended to cover the δ, N50, deficit-percentage, and correlation-gloss statements that today slip through), together with the W1/W2 narrative corrections in both language versions.