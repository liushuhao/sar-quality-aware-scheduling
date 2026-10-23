# Editorial Decision Letter — Full Panel Review, 2026-10-23

**Manuscript**: *Resolution-Driven Dwells in SAR Task Scheduling: Mode Composition Decides What Tighter Requirements Cost* (main.tex, post-t54 state, commit 479eda5)
**Panel**: 5 seats — Journal-Fit (E1–E10), Methodology (M1–M3, m1–m6), Domain/SAR (D1–D3, D4–D9), Perspective/Operations×Theory (P1–P9), Devil's Advocate (DA1–DA13)
**Seat verdicts**: EIC Major Revision (0C/3M/7m) · Methodology Major Revision (0C/3M/6m) · Domain Major Revision (0C/3M/6m) · Perspective Major Revision (0C/4M/5m) · DA 2 CRITICAL / 6 MAJOR / 5 MINOR
**DECISION: MAJOR REVISION** (unanimous across the four reviewing seats; both Devil's-Advocate CRITICAL findings adjudicated **validated** — see §3)

---

## 1. Editor's summary

This panel reviewed the manuscript fresh: every seat read the full paper in an isolated context, blind to the project's prior review batches and to each other's outputs. The manuscript that emerged is one whose *substance* the panel rates unusually high and whose *delivery* still blocks acceptance. Three independent verification streams came back clean: the domain seat reproduced **every physics-layer number it attempted** (full §3.1 constant chain, the complete AASR sequence including the SLS≡STR degeneracy and SPT −7.05 dB, f_dc = 345.7 kHz, oracle deviations +0.419/+2.102/+5.305%); the methodology seat recomputed **every headline statistic** (26.0/46.6/46.0/0.27 pp, 4.15/2.36 pp, 20.01/26.01 and 44.78/46.58 floor accounting, 477,308/13,845, 184/926, 135/458, 18.25/30.44) and found **zero internal inconsistencies beyond the two wording defects below**; and the counterfactual numbers match the artifact ledger exactly. No seat found a defect that invalidates the coverage–demand curves themselves.

What blocks acceptance sits in four clusters: (i) the abstract headlines two numbers whose *decision-relevant meaning* is conditional on choices the abstract does not carry (the repair rule behind 18–30 pp; the confounded family design behind "mode composition decides"); (ii) two self-contradictions inside the paper (§3.1 vs §7.3 on the velocity convention; abstract "within 0.27 points throughout" vs the 0.359-pp dip of §6.4) plus two verbatim duplicated blocks; (iii) a physics layer with two derivation/label defects ((R0/R)³ premise; g_T misnomer) and one unquantified production-vs-exact dwell deviation that feeds the central counterfactual; (iv) a manuscript that is not self-contained for an external reader (private registry pointers, internal governance dialect). All are fixable — most by rewording, the rest by **reanalyses of existing artifacts**; only the optional composition-matched family would need new runs.

## 2. Consensus findings (multi-seat corroboration)

| # | Finding | Seats | Status after main-thread verification |
|---|---------|-------|----------------------------------------|
| C1 | Counterfactual 18–30 pp gap is conditional on a priority-blind drop-the-later-task repair; gap ≈ dropped-task priority mass (184/926→18.25 pp, 135/458→30.44 pp); no re-timing/priority-aware/margin arm; abstract states it unqualified | DA2 (CRITICAL) + M2 + P3-adjacent | **Verified**: arithmetic reproduces; repair rule quoted from §6.6 |
| C2 | Title/abstract causal claim ("Mode Composition Decides") rests on 3 families in which composition is perfectly confounded with task count, window density and tier mix; paper concedes the covariation (§6.1); no crossing cell exists | DA1 (CRITICAL) + P1 | **Verified**: §6.1 sentence quoted verbatim by both seats |
| C3 | §7.3 asserts coverage readings are "invariant to" the scene-velocity convention; §3.1 asserts the opposite ("the coverage readings … carries the convention"); C2 mixes scaled dwells with unscaled 4.07 s maneuver + 2 s settle, so §7.3 is the false side | D1 + DA6 | **Verified**: both sentences read in main.tex (L117 vs L405) |
| C4 | Abstract "within 0.27 points throughout" contradicts the 0.359-pp dip (§6.4) and the 2.63-pp grid range; the Conclusion already carries the correct wording | E1 + DA11 | **Verified** (L29 vs L300/L348; L419 correct) |
| C5 | Two verbatim duplicated blocks: "Across the five constraint families…" (§3.4) and "Across the 30 released R-family manifests…" (§5.1) | E4 + m3 + P5 + DA10 (four seats) | **Verified**: 2 occurrences each (grep count) |
| C6 | Manuscript not self-contained: in-text pointers to formula-spec §8.17-9, AD-3, "L8 (caliber v5)", "exit-11", internal review dates; deposit promised only upon acceptance; governance dialect ("caliber" ×38–45, "registered" ×85 — counts corrected by the 2026-10-24 re-review; seat 1's original 33/~50 understated) | E2 + E3 + DA13 | **Verified** (pointers present; corrected counts re-verified by grep, 2026-10-24) |
| C7 | Preregistration packaging outruns the ledger: main-result-form amendment dated after the sweep (disclosed); refined verdict reading dated after external review (disclosed); C3/C4 "structurally never binding" was engineered 2026-10-20 — same day as the sweep — by redefining the normalization reference after task-law dwells measured 1.2008× false violations (formula-spec §8.17-13, **not disclosed in the paper**) | DA5 + m2 | **§8.17-13 verified in formula-spec.md L594** |
| C8 | Floor-exclusion bound carries 77–96% of the R3H tightening drops, but abstract headlines 26.0/46.6 pp without the floor share | DA4 + corroborated by M3/P1 framing | Verified (Table 2 + §6.1 arithmetic) |

## 3. Devil's Advocate CRITICAL adjudication (Iron Rule #4)

- **DA1 — confounded causal claim: VALIDATED.** The design has no composition-matched cell; the paper's own §6.1 sentence concedes it. The retired R4H was a density arm (N=500), not a composition-matched cell — the deconfounding cell (100 tasks, no-STR mix) does not exist in the design. The title's causal verb is supportable only in the within-family reading. **Blocks silent acceptance.** Revision path: reword title/abstract to the within-family descriptive claim (keeping the abstract's task-level sentence), or add one composition-matched family (100 tasks, no-STR mix — generator-supported).
- **DA2 — repair-rule-manufactured counterfactual gap: VALIDATED.** The gap arithmetic is essentially the dropped-task priority mass, making the 18–30 pp reading a property of the chosen repair rather than a bound on what endogenous dwell buys; the robust, repair-independent quantity is the 20–29% violation rate. **Blocks silent acceptance.** Revision path: add ≥1 alternative repair arm (priority-aware drop and/or bounded left-shift re-timing) as a reanalysis of the registered artifacts; lead with the violation rate; qualify the abstract.

Both CRITICALs are addressed by rewording + artifact reanalysis; neither requires the experimental campaign to be redone. With both validated, Accept finalization is blocked → Major Revision.

## 4. Disagreements and arbitration

1. **Is the title overclaiming?** EIC: "title is accurate … no overclaim found" (presentation-level judgement). DA1/P1: causal claim unsupported by the design (inferential judgement). *Arbitration*: DA1/P1 prevail on the inferential question — the EIC verdict addressed whether the title describes the paper's content, not whether the design isolates the causal factor. Reword or extend; the EIC's presentation-level view stands otherwise.
2. **Is the preregistration narrative credible?** Seat 2: "coherent and, by community standards, unusually honest" (after verifying the amendment ledger). DA5: "a registered-report referee would reject the discipline claim" (packaging vs timeline). *Arbitration*: both stand at different levels. The timeline disclosure is exemplary and stays; the packaging must come down to it — contribution 3 downgraded to what was actually frozen (grid + criteria), the C3/C4 reference redefinition disclosed in the paper, and "frozen in advance" claims carrying their §5.3 pointer at first use.
3. **Severity of the domain majors D2/D3** (single-seat findings): accepted as validated — the seat verified them against the solver fork (duration.py, quality.py) and reproduced the surrounding physics exactly; the main thread independently verified the adjacent registry claim (§8.17-13). No counter-evidence exists in any seat's report.

## 5. Revision Roadmap (immutable core)

### Tier 1 — must address before resubmission

- **T1 (C1/DA2/M2)** Counterfactual: add at least one alternative repair rule (priority-aware drop and/or bounded re-timing) as reanalysis of existing artifacts; report the 20–29% violation rate as the repair-independent headline; state the repair dependence wherever 18–30 pp appears, including the abstract. *(Final-adjudication execution conditions, 2026-10-24: priority-aware drop retains ≈70% of the gap — E[min]/E[p]=3.85/5.5, R3H ≈12.8 pp / R2F ≈21.3 pp, still double-digit; do not describe the gap as repair-manufactured — it is the measured consequence of an infeasible plan under the registered rule; soften "would ship the plan without knowing" to an epistemic statement about the dwell model.)*
- **T2 (C2/DA1/P1)** Title/abstract: either reword to the within-family descriptive claim (e.g., "the stripmap floor, not dwell growth, carries most of the tightening cost; mode mix sets where the cliff sits") with the confound stated at first mention, or add one composition-matched family (100 tasks, no-STR). Author's choice; rewording is sufficient if chosen explicitly.
- **T3 (C3/D1/DA6)** Delete or invert the §7.3 invariance sentence to match §3.1; add the registry's actual justification for the inertial convention (Kim Table-3 reproduction 0.2–0.5% inertial vs 4.7% ECEF-relative); add a one-line sensitivity statement.
- **T4 (C4/E1/DA11/m2/DA7)** Abstract repairs: mirror the Conclusion's "within 0.27 points of its as-placed coverage at every tighter point"; qualify "18–30 points" per T1; attach the §5.3 timeline pointer to "frozen in advance"; report 2.36 and 0.93 pp both, for both families, with the divergence explained (DA7).
- **T5 (C6/E2/E3/DA13)** Self-containedness: strip or translate internal pointers (formula-spec §8.17-9, AD-3, L8, exit-11) into a standard reproducibility statement; de-jargonizing pass ("caliber"/"registered"/"scenario world" → measurement convention / pre-registered / scenario set); deposit the registration chain and ledgers as supplementary material **at submission** (strongly preferred to upon-acceptance for T9's credibility). *(The post-hoc amendment dates are NOT in scope for stripping — protected disclosure, see below and §8 item 3.)*
- **T6 (D2)** Dwell closure: quantify the production symmetric-span construction against the already-implemented exact Eq.(20)–(23) chain over each envelope; reword "tan-exact Kim Eq.(22)/(24) chain" to the symmetric-construction description; state the W_a squint-scaling semantics.
- **T7 (D3)** Quality model: rename g_T (dwell/integration-gain ratio, = 1/A, not antenna gain); re-derive the R³ factor via T ∝ R/ρ_a (cell-growth premise is false in the model's own terms); disclose the deliberate ρ_a² weighting; recast the 24.3×/67.6× magnitudes as index properties.
- **T8 (C7/DA3/DA5)** Contribution packaging: restate contribution 1 as dwell-closure + transfer-chain feasibility (C5 is a raise-guarded identity — the paper says so); disclose the C3/C4 reference redefinition (2026-10-20, after 1.2008× false violations) alongside the existing "structurally never binding" statement; downgrade contribution 3's "frozen before data" to grid+criteria scope.
- **T9 (C8/DA4)** Floor share travels with headline drops: 20.01/26.01 and 44.78/46.58 next to 26.0/46.6 pp in abstract, §6.1 and Conclusion; state that the freeze forbids run-time re-routing that the registered feasibility test would permit at moderate squint.
- **T10 (C5)** Delete the two duplicated blocks (§3.4, §5.1).

### Tier 2 — should address

- **T11 (M1)** Budget-insensitivity: run a scoped budget check (e.g., R2F at the two dip points, 160/240) or soften §6.4's "no budget changes the picture" to the measured statement.
- **T12 (M3+DA-obs)** As-placed costs (4.15/2.36 pp): compute any non-trivial upper bound at s=1.0, or scope to "under the anchor construction"; examine the 6.0-pp residual at s=0.9 (bound 0.748 vs obs 0.688).
- **T13 (P4)** Report served-task fraction beside served-priority fraction at every grid point (artifact reanalysis); state whether uniform weighting is inert by construction.
- **T14 (P3)** Transfer-margin sensitivity replay on the R3H curve (pad 12.5/25%; maneuver 2.409 s median vs 4.07 s bound) — same reanalysis instrument as the counterfactual.
- **T15 (P2)** Rewrite the §4 theory paragraph: start-time-dependent setup (not sequence-dependent); drop the colliding "position-dependent" term; one-line NP-hardness remark (orienteering containment); connect to the already-cited time-dependent-transition AEOS line.
- **T16 (m4/m6)** Counterfactual dispersion (per-seed ranges 12.0–25.6 / 24.5–35.2 pp exist in artifacts); label median-vs-aggregate violation calibers; replace "untouched" with "essentially untouched (median gap 0.0)".
- **T17 (m1/DA9/m5)** "family maximum" → "the unit's best-found coverage" (§1.1, §1.2(3), Conclusion); family labels as intervals per §5.2's own rule.
- **T18 (D4–D9)** Domain minors: registry erratum for the stale "physical sliding domain" phrase (formula-spec §3.1) + cap/boundary-coincidence note; SPT start-domain clip (|ψ|+β/2 ≤ 45°) stated; elevation-plane near-cancellation argument replaces the wrong "could only lower" direction; Song scene-scan-span channel named as candidate reconciliation; Currie & Brown (1992) + Lanari et al. (2001) added to §2.1; 45° Earth-curvature number for T_env,max = 10.5830 s.
- **T19 (seat2-Q4/DA8/P9)** Define the one-priority-unit tolerance and address its proximity to the observed dips; acknowledge per-tier tightening (not uniform scaling) as the operational axis. **Tier-bound sensitivity sweep is mandatory** (DA8's registered minimum — "a tier-bound sensitivity sweep showing the step location moves with the knob"); the mid-band tier arm remains optional. *(Weighting restored 2026-10-24 after re-review flagged the downgrade: DA8 is the one Tier-2 MAJOR without a seat-offered wording exit.)*
- **T20 (N1, re-review 2026-10-24)** Rename the frozen shape criteria C1–C3 → S1–S3 (collision with constraint families C1–C5, §3.4 vs §5.3/§6.3/Table 3); update Table 3 and §6.3 together with T10 in one pass.
- **T21 (N2, re-review 2026-10-24)** "the single-satellite family/control" label (abstract, conclusion) distinguishes nothing in a single-satellite study; fold into E8's family-label fix.
- **T22 (N3, re-review 2026-10-24)** §6.4 "the median falls because the net of those two displacements is negative" — arithmetically loose (a 10-seed median follows order statistics, not a two-seed net sign); delete the net-sign clause; the next sentence already carries the correct mechanism.

### Tier 3 — polish (non-blocking)

Nomenclature list (E5); prune ~270 uncited bib entries (E6); highlights/keywords fixes (E7); one family-label convention (E8); submission-package consistency — stale checklist item on caleiras2026a pages, unused fig3_quality_vs_squint.pdf, cover-letter voice (E9); caption slimming (E10); wall-clock one-liner (P7); onboard/constellation connection from the four uncited autonomy refs (P8); per-seed dispersion in Table 2 (DA12); demote §4 operator detail / add anchor-only reference line (P6); compress §7.2 (EIC); priority-distribution robustness (P4b).

### What the panel explicitly protects (do not "fix" away)

Unanimous: the infeasibility-vs-zero discipline; the floor-exclusion decomposition (Table 2); the frozen-criteria-failures-reported-as-results practice; the 258/260 construction-face attribution with named exceptions; the exact post-hoc-amendment dates; the counterfactual's internal controls (same solver/budget/population). These are the paper's distinguishing virtues — revision must preserve them.

## 6. Panel provenance (typed, per review-panel-provenance/1.0 semantics — builder script unavailable in this skill install, recorded manually)

- **Invocation-context freshness**: all five seats dispatched as fresh subagents (separate contexts, no session history). ✓
- **Peer-output visibility**: none — each seat saw only its own brief; no seat read anything under review/ before writing. ✓
- **Role separation**: prompt-level personas; EIC/methodology/domain/perspective configured per Phase-0 field analysis (aerospace mission planning; OR/metaheuristics+preregistration; spaceborne SAR systems; ground-segment operations × scheduling theory); DA fixed. Role separation is NOT evidence of independent error processes. ✓ disclosed
- **Model family**: single family (session model, GLM-class) across all five seats and the synthesizer → **correlated-error disclosure applies**: cross-seat corroboration (§2) is weak-form agreement, not independent replication. No cross-model seat ran (ARS_CROSS_MODEL not configured; manuscript not sent to any external provider).
- **Provider/accountable human**: local session; no human reviewer; synthesizer = main session that dispatched the seats.
- **Deviation from skill defaults**: sprint-contract two-call (blind/paper-visible) Phase 1 not used — single-call paper-visible seats per this project's established panel practice; sprint checker scripts not shipped in this skill install, hence not run. Acronym check (advisory #849): **did not run** (scripts/ directory absent from this skill copy).
- **Main-thread verification**: duplications (grep = 2/2), abstract 0.27 vs 0.359 dip, §3.1(L117)/§7.3(L405) contradiction, formula-spec §8.17-13 (L594) all re-verified by the synthesizer before this letter.

## 7. Attachment: Acronym Check (advisory, #849)

The acronym check did not run (the skill's `scripts/check_acronyms.py` is not present in this install). No reviewer finding derives from this attachment.

## 8. Re-review integration (2026-10-24, Claude Code cross-tool audit)

A fresh Claude Code session (`rr1-claudecode-rereview.md`, same dir) audited this letter against the five seat reports and the manuscript. Verdict: **synthesis SOUND-WITH-CORRECTIONS** (0 fabrication across T1–T19/C1–C8/§3; all arithmetic reproduced; both CRITICAL adjudications upheld after both-sides argument; Major Revision upheld). Main-thread verification confirmed its three load-bearing claims (dialect counts, C-label collision, L352 clause) before integration. Corrections now applied:

1. **C6 counts corrected** (above): caliber 38 word-boundary / 45 with plural; registered 85. Direction of the original error: understatement.
2. **T19 weighting restored** (above): DA8's minimum remedy (tier-bound sensitivity sweep) is mandatory again.
3. **T5 scope guard**: T5 translates *registry pointers and internal jargon*; the **post-hoc amendment dates are protected disclosure** (see §5 protected list) and must survive T5 — T5 and the protected list coexist under this reading; over-execution that deletes the dates is a defect, not compliance.
4. **Recorded licenses** (no content change): T3's anchor was silently corrected from seat 5's "§6.4" to the actual §7.3 sentence (L405) — correct call, now on record; T2's "generator-supported" mildly strengthens P1's "appears to make this cheap" — treat the hedge as the seat's.
5. **New findings adopted** (panel-wide misses, all MINOR, verified by main thread):
   - **N1 (→ T20, Tier 2)** C-label collision: constraint families C1–C5 (§3.4) vs frozen shape criteria C1–C3 (§5.3/§6.3/Table 3); rename criteria (e.g., S1–S3) and update Table 3 + §6.3 + the letter's own C7 row wording when executing.
   - **N2 (→ T21, Tier 3)** "the single-satellite family/control" (abstract, conclusion) distinguishes nothing in a single-satellite study; fold into E8's family-label fix.
   - **N3 (→ T22, Tier 3)** §6.4 L352 "the median falls because the net of those two displacements is negative" — arithmetically loose (a 10-seed median follows order statistics, not a two-seed net sign); delete the net-sign clause; the following sentence already states the correct mechanism.

Roadmap now T1–T22. The three-layer chain proceeds to final adjudication by a third model family (opencode/deepseek) on this corrected letter + the re-review.

## 9. Final adjudication (2026-10-24, opencode/deepseek-v4.1-flash-free — `adjudication-opencode-20261024.md`, same dir)

**ADJUDICATION: Major Revision | chain SOUND-WITH-CORRECTIONS — confidence: high.** All four chain-joint spot-checks HOLD; both CRITICAL rulings upheld as VALIDATED (DA1 with the task-level/family-level qualification; DA2 with the repricing below); verdict agrees with all three layers. Corrections ordered by the adjudicator and applied to this letter (all verified by the main thread before integration):

1. §5 roadmap now carries T20–T22 as rows (previously declared only in §8).
2. T5's parenthetical no longer lists "internal dates" (collided with the protected-list and §8 guard).
3. R4H attribution corrected (density arm, not deconfounding cell) in §3 DA1.
4. T1 carries the adjudicator's repricing: priority-aware drop retains ≈70% of the gap (E[min]/E[p] = 3.85/5.5; R3H ≈12.8 pp, R2F ≈21.3 pp — verified independently) — the gap survives alternative repair at double-digit magnitude; plus the two execution conditions recorded there.
5. T8 execution note: disclose §8.17-13 with its technical rationale (library-constant reference → task-law dwells measured 1.2008×, theoretical worst 1.274× → per-task envelope maximum), not the date alone.

**Residual risk (adjudicator J4, adopted):** after all qualifications, the surviving positive claim is narrow — a referee who accepts every correction may still judge the residual contribution incremental for an AST-class venue. No roadmap item measures this; it is the one path by which a fully compliant revision still returns rejection.
