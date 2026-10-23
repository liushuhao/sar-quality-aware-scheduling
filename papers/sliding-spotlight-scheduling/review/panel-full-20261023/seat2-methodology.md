# Review Report — Seat 2: Methodology Reviewer

## 1. Persona card (first person)

I am a senior researcher in simulation methodology, operations research and metaheuristics, with a replication-science and preregistration background; I have refereed regularly for EJOR- and Automatica-class journals. In this review I assess experimental design, statistical validity, preregistration discipline, counterfactual construction, internal numerical consistency, and reproducibility. I read the full manuscript and, where a claim was traceable, the supporting artifacts (frozen formula registry, preregistration ledger, run-lineage register, L8 reading ledger and counterfactual summary). I did not run any code.

## 2. Manuscript summary (≤150 words)

The manuscript makes the SAR imaging dwell endogenous to agile-satellite scheduling: the required azimuth resolution is a per-task hard constraint whose mode parameters are derived at the selected start, so a tighter requirement buys resolution with dwell time, which feeds the inter-task transfer constraint. On three real-window scenario families (20/50/100 tasks, frozen mode assignments) a nine-point demand grid scales all requirements; coverage (served priority fraction) is read as a median over ten seeds at one search budget (40/60). Three shape criteria, frozen before the data, are reported with failures. A frozen-dwell counterfactual replays classical fixed-duration plans against the true dwell: 20–29% of consecutive pairs violate the transfer constraint, and after a deterministic drop-repair the plans land 18–30 points below the endogenous arm. The anchor attains the best-found coverage in 258/260 units, framing the response as construction-driven.

## 3. Assessment

### Design and statistics

The scan design is coherent: the demand axis is external to the scheduler, the scenario population is not regenerated between grid points, and each point is a median over ten scenario draws with per-seed dots shown (Fig. 3 caption: "per-seed readings as dots"). The same-seed confound — "the same seed driving both the scenario draw and the search" (§5.3) — is acknowledged rather than hidden, and the mitigation is measured, not asserted: because the greedy anchor attains the unit's best-found coverage in 258/260 units, the reading is effectively a deterministic function of the scenario draw alone, so search stochasticity contributes almost nothing to the median. That argument is sound, with one boundary the authors should state: it is measured at 40/60 only (see M1). The absence of significance tests is defensible for a descriptive scan: the paper explicitly disclaims pass/fail verdicts ("Coverage admits no pass/fail verdict here", §5.4), the retired power analysis belonged to a vacated estimand, and the headline effects (18–30 points) dwarf any plausible noise. I would nonetheless like explicit per-seed dispersion for the counterfactual (see m6). A second design consequence the authors themselves demonstrate: with n=10, single-seed displacements move the median (§6.4's dip accounting), so medians near plateaus are fragile — honestly handled, but worth a caveat sentence.

### Criteria and preregistration discipline

The preregistration narrative is coherent and, by community standards, unusually honest: §5.3 states with dates that the grid and the three criteria predate the data, that the amendment registering the coverage–demand curve as the main result form "is dated 2026-10-21, after the sweep ran on 2026-10-20", and that the refined criteria reading was registered 2026-10-23 after a 2026-10-22 external review. I verified this against the project ledger (amendment_20261021_ticket50, amendment_20261023_ticket54 in analysis_prereg_v2.json; the grid and criteria were frozen in the predecessor L7 registration and inherited unchanged). The two post-hoc refinements are legitimate because both weaken rather than strengthen claims: the infeasible-cell-as-undefined convention removes a genuine internal inconsistency (the frozen convention scored the all-infeasible R1C s=0.8 cell as a zero-coverage median, contradicting the paper's own §6.2 discipline that infeasibility is never a coverage), and the verdict it changes (R1C tight arm: "met" to "undefined") is reported under both readings. Two caveats: the criteria were shaped on a predecessor world whose data existed at registration (one world removed — disclosed, but the abstract's "frozen in advance" should carry the §5.3 pointer, m2), and the one-priority-unit tolerance sits uncomfortably close to the observed dips (see Q5).

### Counterfactual validity

The freeze-dwell arm is a registered reanalysis with tight internal control (same solver, budget, scenario population). The mechanism is real: planning at the zero-squint library dwell systematically underestimates the squint-dependent dwell, and the C2 pad does not absorb it (20–29% of pairs violate on the dense families). The 18–30-point gap, however, is a property of the full pipeline including the repair rule — "a deterministic time-order repair that drops the later task of each violating pair" (§6.6) — which is priority-blind and does no re-timing or replanning. The magnitude is consistent with the violation counts (dropping ~18% of selected tasks on R3H, ~29% on R2F yields roughly the observed priority loss), but a priority-aware or re-timing repair would land lower. As registered and disclosed the number is correct; as a headline ("lands 18–30 points below") it invites over-generalization to "classical schedulers lose 18–30 points", which the repair-rule dependence does not support (M2).

### Reproducibility

Strong on artifacts: a reading ledger stores each reading with unit, caliber and source path; a manuscript-number checker recomputes Section 6 from the artifacts; seeds are pinned per unit, runs are single-threaded with manifest task-list order. I cross-checked the counterfactual summary in the artifacts: gap medians 18.25/30.44 pp and pair counts 184/926, 135/458, 9/10 zero-violation seeds for R1C all match the text. Weaker on manuscript-level statements: the "bit-reproducible" claim is unqualified by platform or verified scope; the software stack (the pinned pymoo version lives in the prereg file, not the paper) is absent; deposition is Zenodo-upon-acceptance with on-request availability during review — acceptable, though I encourage earlier deposition of at least the ledger and checker. The duplicated sentences (m3) suggest the manuscript has not fully benefited from the project's own verification tooling at the prose level.

## 4. Issues

### CRITICAL

None. Every headline number I could recompute is internally consistent (see §5), and the design's limitations are disclosed rather than concealed.

### MAJOR

**[M1] §6.4/sec:dip — "no budget changes the picture, because the effect sits in the construction" — the budget-insensitivity claim is deductive, not measured in this world.**
Problem: the reported reading is the best-covered member of the tie-set, i.e. max(anchor, search). The anchor component is budget-independent, but the nil search component was measured only at 40/60 in the L8 world; the budget-ladder pilots cited in the data availability statement ("per-unit pilot records across the three budget tiers") belong to earlier model calibers, and the run-lineage register confirms the L8 sweep axis has a single budget. A larger budget could in principle lift the search above the anchor at the dip points and erase them — exactly the mechanism by which an earlier reading was retired ("a larger search budget removed it", §6.4). Why it matters: the construction-face separation is load-bearing for the paper's central interpretive claim (coverage response = construction, not search), and §7.4 prices out the budget extension "by policy" ("raising it was judged to buy a different search") — a judgement, not evidence. Suggested fix: run a small, scoped budget check on the current model (e.g., R2F at 160/240 over the ten seeds at the two dip grid points) and report whether anchor = best-found still holds; if not run, soften §6.4 to "the anchor component of the reading is budget-independent; the search component was nil at the registered budget".

**[M2] §6.6/sec:counterfactual — "a deterministic time-order repair that drops the later task of each violating pair" — the 18–30pp gap is repair-rule-specific, with no sensitivity analysis.**
Problem: the drop rule is priority-blind and performs no re-timing or replanning; any classical deployment would repair with at least priority awareness (drop cheaper tasks) or re-time starts within windows. The gap therefore reads as an upper-ish estimate of the cost of planning with a wrong dwell model, but the abstract states "lands 18–30 points below the endogenous dwell" without the repair qualifier. Why it matters: this is one of the two numbers in the abstract; its decision-relevant form ("what does ignoring the dwell physics cost?") depends on the assumed repair capability. Suggested fix: add one alternative repair (priority-aware drop, or bounded re-timing) even on a single family, and report both gaps; or add an explicit sentence in §6.6 and the abstract that the figure is conditional on the registered repair rule.

**[M3] §6.2/sec:asplaced — "R3H pays a coverage cost of 4.15 percentage points at the as-placed point" — the as-placed costs have no non-trivial optimality certificate.**
Problem: at s≥1.0 the floor-exclusion bound of Table 2 is trivially 1.000, so the 4.15pp (R3H) and 2.36pp (R2F) as-placed costs cannot be attributed between genuine C2/interval infeasibility and greedy-anchor shortfall; no upper bound tighter than 1.0 is computed, and the search never tests the anchor there. The 26.0/46.6pp tightening costs do not have this problem (the floor bound accounts for 20.01/26.01 and 44.78/46.58), which makes the asymmetry visible. Why it matters: the as-placed cost is the operationally most quoted number ("what does the requirement as placed cost?"), and its slack is unquantified. Suggested fix: compute even a crude upper bound at s=1.0 (e.g., a C2/interval-conflict relaxation, or an exhaustive check on the control family) and report the slack; alternatively scope the sentence to "under the anchor construction at the registered budget".

### MINOR

**[m1] §1.1/sec:faces — "attains the family maximum in 258 of the 260 sweep units" — "maximum" overstates and "family" is the wrong noun.**
The quantity is the best coverage found by this study's search in that unit at 40/60 (correctly hedged in §4.5 as "the best coverage found for the unit in this study"); no optimality certificate exists, and the intro's "family maximum" additionally suggests a maximum over the family. Fix: use "the unit's best-found coverage" in §1.1, §1.2(3) and the conclusion.

**[m2] Abstract — "three shape criteria are frozen in advance and reported with their failures" — the frozen claim should carry the §5.3 timeline pointer at first use.**
Contribution 3 likewise asserts "frozen before this scenario world's data were read" without noting that the main-result form and the reading protocol were registered post hoc (disclosed in §5.3/§6.3). One cross-referencing clause at each first claim keeps the preregistration narrative from reading stronger than its ledger.

**[m3] §3.4 and §5.1 — duplicated sentences (copy-editing artifacts).**
"The set that actually binds ... is exactly two" passage appears twice verbatim in §3.4, and the "aasr 0, footprint 0, below-finest 0" ledger sentence appears twice verbatim in §5.1. Delete the duplicates.

**[m4] §6.6 — "violated in 20–29% of consecutive pairs (median over seeds; 184 of 926 pairs ...)" — two different statistics juxtaposed; and "untouched" overstates the control family.**
The median per-seed rates (20.2%, 28.9% per the artifacts) differ slightly from the aggregate fractions (184/926 = 19.9%, 135/458 = 29.5%); label the counts as totals explicitly. The ledger records for R1C one violating pair in one seed with a 6.31pp gap; the text's "untouched" is contradicted by its own "nine of ten seeds" qualifier — replace with "essentially untouched (median gap 0.0)".

**[m5] Table 3/tab:criteria labels vs §5.2 — "R2F (50 / 46)" pins a single-seed admitted count.**
§5.2 states admitted counts as intervals (46–50; 99–100) and explicitly warns "a single-seed value is not a family constant", yet Table 3 and §6.1/§7 fix labels at 46 and 99. Use drawn counts plus intervals, or "(min–max admitted)".

**[m6] §6.6 — "18.25 and 30.44 percentage points (family medians)" — no dispersion for the counterfactual.**
The artifacts contain per-seed ranges (R3H 12.0–25.6pp; R2F 24.5–35.2pp) that the paper omits, while the main curve gets per-seed dots in Fig. 3. One clause with min–max (and for the violation rates) would let readers judge stability; the ranges are wide enough to matter for the 18–30pp abstract phrasing.

## 5. Strengths (evidence-based)

1. **Disclosure discipline that exceeds field practice.** The registration timeline is stated with dates and unfavorable implications ("the headline curve is a post hoc descriptive reading", §5.3); the verdict-changing criterion refinement is reported beside the frozen verdict ("the only cell where the two readings differ", §6.3); the withdrawn predecessor-world reading is labelled as withdrawn ("that penalty is withdrawn", §6.3).
2. **The seed confound is defused by measurement, not rhetoric.** The 258/260 anchor-domination fact plus the two named exception units (+0.0427/+0.0463, §4.5) is exactly the right evidence structure for the "construction face" argument.
3. **The floor-exclusion bound (Table 2) is a genuine analytical decomposition.** Attributing 20.01 of 26.01 and 44.78 of 46.58 points of the tightening drop to the stripmap floor, with a stated residual semantics, is checkable — I recomputed all four subtractions and they hold to rounding against the table and the §6.1 medians.
4. **Internal numerical consistency is excellent.** Across abstract, §6, Table 2, Table 3 and the conclusion I recomputed: 26.0/46.6/46.0/0.27pp tightening costs; 4.15/2.36pp as-placed costs; 477,308 instances / 9,430 records / 13,845 distinct tasks / 34.5× ratio; 184/926 and 135/458 pairs; 18.25/30.44pp gaps; the 20.01/44.78 accounting; and the C1/C2/C3 verdicts against the §6.1 medians — all consistent, and the counterfactual numbers match the artifact ledger exactly.
5. **The infeasibility/zero distinction is enforced everywhere it could leak** (cross marker in Fig. 3, "kept off the curve", "it is never plotted, averaged, or quoted", §6.2) — a distinction most papers in this area blur.
6. **A counterfactual that is registered and internally controlled** (same solver, budget and scenario population; "the same solver, the same budget", §6.6) rather than an after-the-fact straw arm.

## 6. Questions to authors

1. Do any budget-tier runs exist on the current (caliber v5) model, and does anchor = best-found still hold at 160/240, at least on R2F at the two dip points? If yes, please report; if no, please soften §6.4 (M1).
2. How sensitive is the 18–30pp counterfactual gap to the repair rule — priority-aware dropping, bounded re-timing, or a single replan with true dwells? Even a lower bound ("any repair must drop at least k tasks") would contextualize the number (M2).
3. Is any upper bound tighter than 1.0 available at s=1.0 for R3H/R2F (C2 or interval-conflict relaxation, exhaustive check on small instances), to separate anchor greediness from genuine infeasibility in the 4.15/2.36pp as-placed costs (M3)?
4. How exactly is a "priority unit" defined for the one-priority-unit tolerance registered on 2026-10-23 (presumably 1/Σp per scenario, hence seed-dependent)? The R2F dips (0.268/0.359pp) sit near the plausible unit size (~0.36pp for 50 tasks) — was the tolerance chosen with knowledge of the dip magnitudes?
5. What justifies 40/60 as the registered budget on the current model specifically — were the "pre-scan convergence-calibration pilots" (data availability) run on caliber v5 or on a predecessor?
6. The "bit-reproducible" claim (§4.3): on which platforms and how many units has it been verified, and will the deposited artifacts include the reproduction script and its expected outputs?

## 7. Recommendation

**Major Revision** — confidence: high (4/5).

Rationale: the core descriptive findings are internally consistent, honestly scoped, and supported by an unusually disciplined artifact and registration chain; nothing invalidates the headline curves. But three methodological gaps each touch a load-bearing number or claim: the budget-insensitivity argument is deductive where one small measured check (or softened wording) is needed (M1); the abstract-level 18–30pp counterfactual figure is conditional on an arbitrary, priority-blind repair rule with no sensitivity analysis (M2); and the as-placed costs carry unquantified optimality slack with no certificate (M3). All are addressable with small, scoped analyses and wording changes rather than a new experimental campaign, which is why this is a major revision rather than a rejection.

## 8. Provenance

This review was produced by a fresh subagent with no prior session context and no visibility into other reviewers' outputs or any material under the project's review/ directory other than this report's own output path. The reviewer model belongs to the same model family as the other panel seats; no human reviewer participated. All evidence anchors derive from the manuscript file, the frozen formula registry, and read-only inspection of the experiment-layer ledgers and artifacts; no code, tests, or builds were executed.

VERDICT: Major Revision | CRITICAL: 0 | MAJOR: 3 | MINOR: 6
