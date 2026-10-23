# Cross-Tool Re-Review (Claude Code) — Audit of panel synthesis, 2026-10-24

## 1. Audit summary

The synthesis is faithful. Every roadmap item T1–T19 traces to the seat finding(s) it names, with matching content; all eight consensus rows C1–C8 trace and their "Verified" annotations hold up under my independent re-checks (duplication counts 2/2, abstract vs §6.4 contradiction, §3.1 L117 vs §7.3 L405 contradiction, formula-spec §8.17-13 at L594 — the last resolves as section 8.17 item 13, a numbered-list entry, which is why a literal "8.17-13" string search fails). No CRITICAL/MAJOR seat finding was dropped silently; all 19 majors and both criticals appear in the roadmap or §3/§4. Arithmetic: the floor accounting, the "77–96%" shares, the abstract-contradiction claim, and the velocity-convention arbitration all reproduce exactly; the "gap ≈ dropped-task mass" claim is a fair characterization (R3H near-exact at 18.49 est. vs 18.25 obs; R2F within ~1–3 pp, gap slightly *exceeding* the naive estimate). Both CRITICAL adjudications (VALIDATED) survive a both-sides argument. Defects found in the synthesis are three MINORs: understated dialect counts in C6, a remedy downgrade of DA8 inside T19, and small label licenses. Manuscript-side, the whole panel missed one real (minor) defect: the C1–C5/C1–C3 label collision. Major Revision stands.

## 2. A1 fabrication check — per-item table

Verdicts: **T** = trace confirmed; **T*** = trace confirmed with a note. All anchors are seat report issue IDs, verified against the seat files and main.tex.

### Roadmap T1–T19

| Item | Claimed trace | Verdict | Note |
|---|---|---|---|
| T1 | C1/DA2/M2 | T | DA2 (seat5 CRITICAL) and M2 (seat2 MAJOR) both demand an alternative repair arm and repair-dependence disclosure; "violation rate as repair-independent headline" traces to DA2's "the violation rate (robust)". |
| T2 | C2/DA1/P1 | T | DA1 (CRITICAL) + P1 (MAJOR) both present; T2's rewording example is P1's suggested wording verbatim; "generator-supported" mildly strengthens P1's "the generator template *appears* to make this cheap" (MINOR license). |
| T3 | C3/D1/DA6 | T* | D1 (MAJOR) matches. DA6's content matches but seat5 anchored it to "§6.4" — the actual sentence is in §7.3 (main.tex L405); the letter silently corrected the anchor. Correct call, worth recording. Kim Table-3 0.2–0.5%/4.7% figures trace to D1's fix text. |
| T4 | C4/E1/DA11/m2/DA7 | T | All four exist with matching content (E1 wording fix; DA11 same; m2 §5.3-pointer-at-first-use; DA7 report-both-statistics). |
| T5 | C6/E2/E3/DA13 | T | E2 (registry pointers), E3 (dialect), DA13 (deposit at submission) all present. |
| T6 | D2 | T | Symmetric-construction rewording and W_a squint-semantics both in D2's fix. |
| T7 | D3 | T | g_T rename, R³ re-derivation via T ∝ R/ρ_a, ρ_a² double-weighting disclosure, 24.3×/67.6× recast — all four in D3. |
| T8 | C7/DA3/DA5 | T | DA3's resolution ("restate contribution 1 as dwell-closure + transfer-chain feasibility") and DA5's (downgrade contribution 3; disclose C3/C4 reference redefinition with 1.2008×) both match. |
| T9 | C8/DA4 | T | DA4's "state the floor-share next to every headline drop number" + freeze-forbids-reroute argument match. |
| T10 | C5 (E4/m3/P5/DA10) | T | Four seats reported the two duplicated blocks; my count: exactly 2 occurrences each in main.tex. |
| T11 | M1 | T | M1 (MAJOR) including the "or soften §6.4" exit — the seat itself offered the wording exit. |
| T12 | M3+DA-obs | T | M3 (MAJOR, as-placed upper bound); the 6.0-pp residual (bound 0.748 vs obs 0.688) is in seat5 §3 "Ignored alternative explanations". |
| T13 | P4 | T | P4's fix includes "state explicitly that weighting is inert by construction". |
| T14 | P3 | T | P3's pad 12.5/25% and 2.409 s median vs 4.07 s bound replay match. |
| T15 | P2 | T | All four P2 elements (start-time-dependent setup; drop "position-dependent"; NP-hardness remark; connect the cited time-dependent-transition line). |
| T16 | m4/m6 | T | m4 (median-vs-aggregate calibers; "untouched"→"essentially untouched (median gap 0.0)"); m6 (per-seed ranges 12.0–25.6 / 24.5–35.2 pp). |
| T17 | m1/DA9/m5 | T | m1 ("the unit's best-found coverage" at §1.1, §1.2(3), Conclusion); DA9 same; m5 family labels as intervals per §5.2. |
| T18 | D4–D9 | T | All six seat3 minors map one-to-one (registry erratum + cap/boundary coincidence; SPT clip \|ψ\|+β/2 ≤ 45°; elevation-plane near-cancellation; Song scene-scan-span channel; Currie & Brown 1992 + Lanari 2001; 45° curvature number for T_env,max = 10.5830 s). |
| T19 | seat2-Q4/DA8/P9 | T* | Traces exist, but DA8 (a MAJOR) registered "at minimum a tier-bound sensitivity sweep" with no wording exit; T19 reduces this to "**ideally** one tier-bound sensitivity point". Remedy downgrade — see §7. |

### Consensus table C1–C8

| Row | Claimed seats | Verdict | Note |
|---|---|---|---|
| C1 | DA2 + M2 + P3-adjacent | T | DA2/M2 confirmed; "P3-adjacent" is honestly labeled (P3 is margin sensitivity, not repair). Arithmetic claim independently reproduced (§3 below). |
| C2 | DA1 + P1 | T | Both quote §6.1's covariation sentence; verified verbatim at main.tex L274 ("The three families covary in mode composition as they do in task count"). |
| C3 | D1 + DA6 | T | Both sentences verified: L117 ("every reading that mixes dwells with velocity-independent constants (the coverage readings) … carries the convention") vs L405 ("the coverage readings compare schedules inside one convention, so they are invariant to it"). |
| C4 | E1 + DA11 | T | Abstract L29 "within 0.27 points throughout" vs §6.4 L348 (0.359-pp dip); Conclusion L419 carries the correct wording. |
| C5 | E4 + m3 + P5 + DA10 | T | My python count: "Across the five constraint families" ×2 (both in L185), "Across the 30 released R-family manifests" ×2 (both in L244). |
| C6 | E2 + E3 + DA13 | T* | Pointers verified present (formula-spec §8.17-9 at L195, AD-3 at L228, L8/caliber v5 at L252, exit-11 at L232, internal dates at L260). **But the quoted counts understate**: "caliber" is 38 word-boundary / 45 with plural (not ×33); "registered" is 85–89 (not ~50). Direction is conservative; still a numeric inaccuracy in quoted evidence. |
| C7 | DA5 + m2 | T | formula-spec.md L594 = §8.17 item 13: dated 2026-10-20, records R2F measured 1.2008× (theoretical worst 1.274×) false violations and the reference redefinition. Registry header L3 confirms v1.9 dated 2026-10-20. "Not disclosed in the paper" — confirmed: no occurrence of "1.2008" in main.tex. |
| C8 | DA4 + M3/P1 framing | T | DA4 confirmed; M3 does carry the 20.01/26.01 and 44.78/46.58 accounting; shares recompute to 76.9%/96.1% — "77–96%" correct. |

### §3 CRITICAL adjudications

| Item | Verdict | Note |
|---|---|---|
| DA1 → VALIDATED | T | §6.1 concession verified (L274); R4H retirement verified (L248: "retired at registration because the single-transit STR pass-count scaling exceeds the registered span at N ≥ 150"). |
| DA2 → VALIDATED | T | Repair rule quoted from §6.6 L366 ("a deterministic time-order repair that drops the later task of each violating pair"); abstract L29 states 18–30 pp with no repair qualifier. |

**Dropped-finding sweep:** all seat CRITICALs (DA1–2) and all 19 MAJORs (E1–E3, M1–M3, D1–D3, P1–P4, DA3–DA8) appear in the roadmap or §3/§4. All minors map to T-items or the Tier-3 list (E5–E10, m1–m6, D4–D9, P5–P9, DA9–DA13 all accounted). Seat2's Q5/Q6 (budget justification; bit-reproducibility scope) are questions, not findings; their omission from the roadmap is defensible. No severity misrepresentation found beyond the T19/DA8 remedy downgrade.

## 3. A2 arithmetic — five recomputations

**1. Counterfactual gap ≈ dropped-task priority mass (DA2/C1).** Assumptions: priorities i.i.d. randint(1,10) (stated §3.4/§5.1), so the mean cancels in mass ratios; one distinct dropped task per violating pair (each task is the "later" of at most one consecutive pair); counts 184/926 and 135/458 are 10-seed aggregates.
- R3H: 18.4 dropped tasks/seed over 99–100 admitted → naive estimate **18.49 pp** vs observed **18.25 pp**. Solving gap = E − F + D with E = 0.9485 gives the fixed arm's pre-repair selection F ≈ 0.9509 ≈ E — selection masses nearly identical, so the gap *is* the dropped mass to within 0.24 pp.
- R2F: 13.5 dropped/seed over 46–50 admitted → naive estimate **27.0–29.3 pp** vs observed **30.44 pp**; the observed gap slightly *exceeds* the naive estimate (dropped tasks carried above-mean priority, or F slightly below E, or median-vs-aggregate effects; m4/T16 already flags the caliber issue).
- **Ruling: fair characterization, not an overstatement** — the gap is accounted by the dropped-task mass to within ~0.2 pp (R3H) and ~1–3 pp (R2F, in the direction of the gap being larger). This supports the letter's/DA2's core point: the number measures the repair's punitiveness, not a bound on what endogenous dwell buys.

**2. Floor-exclusion accounting.** From §6.1/Table 2 values: drop to s=0.9 = 0.9485 − 0.6884 = **26.01** ✓; floor part 0.9485 − 0.7484 = **20.01** ✓ (bound 0.7484 rounds to Table 2's 0.748); residual 0.7484 − 0.6884 = **6.00** ✓ ("6.0 … points"). Drop to s=0.8 = 0.9485 − 0.4827 = **46.58** ✓; floor part 0.9485 − 0.5007 = **44.78** ✓ (bound 0.5007 rounds to 0.501); residual **1.80** ✓. Shares 76.9% / 96.1% — the letter's "77–96%" is correct. Fully consistent.

**3. Abstract contradiction (C4).** R2F grid medians (§6.1, L300): min 0.9737, max 1.0000 → full-grid range **2.63 pp**; the s=1.3→1.4 dip is **0.36 pp** > 0.27. The conclusion's wording ("within 0.27 points of its as-placed coverage at every tighter point", L419) is the correct claim (0.9764 − 0.9737 = 0.27 at s=0.9; 0.00 at s=0.8). **Confirmed: the abstract sentence is false under its natural reading** ("throughout" + no reference point), and false under the stricter adjacent-point reading too.

**4. Velocity-convention arbitration (C3).** C2 charges (1+0.25)·T_dwell + 4.07 s + 2.0 s. Dwells scale with the velocity convention (inertial 7578.05 → ECEF-relative 7221.69 m/s = factor 1.0493, +4.9%); the maneuver bound and settle constants do not. Hence C2 feasibility at the margin, and therefore coverage readings, move with the convention; only dwell *ratios* are invariant (which is what §3.1 actually claims). The window lengths are themselves velocity-dependent, which strengthens the same direction. **The letter's arbitration — §7.3 (L405) is the false side — is physically correct.** (Seat5 DA6's "~8–12%" magnitude guess is loose vs the 4.9% figure; direction right; the letter did not inherit the wrong magnitude.)

**5. Duplicate blocks (C5).** Python occurrence counts on main.tex: "Across the five constraint families" = **2** (both within L185); "Across the 30 released R-family manifests" = **2** (both within L244). Letter's "2 occurrences each" confirmed.

## 4. A3 CRITICAL adjudications — both sides, then ruling

### DA1 (confounded causal title) → VALIDATED: upheld

*For the paper:* the mechanism evidence is within-family and real — Table 2 attributes 77–96% of R3H's tightening drop to the stripmap floor; R2F (no STR) is flat; R1C (all STR) steps at exactly the floor arithmetic (§6.3's 0.8×[2.5,3.0] ⊂ finer-than-2.4669 argument). The abstract's sentence "Which mode a task receives decides what a requirement change costs" is task-level and arguably supported within-family. The confound is conceded in the paper itself (§6.1), not hidden.

*For VALIDATED:* the title's subject is "Mode Composition" — a family-level property — and the only family-level contrast in the design is perfectly confounded (composition × task count 20/50/100 × window density 145–162/337–391/731–779 × tier mix); no crossing cell exists, and the one arm that would have begun deconfounding (R4H) was retired for capacity reasons (L248). The within-family evidence shows the *floor mechanism* decides costs; it does not show that *composition* (vs density) decides the family shapes — R2F's flatness is as consistent with 50-task capacity slack as with no-STR composition, and no C2-tightness-per-point measurement separates them. A causal verb in the title from n=3 confounded cells is exactly what a methods referee rejects.

*Ruling:* VALIDATED is the right call, and the revision path is proportionate (reword to the within-family claim, or one composition-matched family). Note the abstract's task-level sentence is more defensible than the title; T2's rewrite option should keep the task-level reading and drop the family-level one.

### DA2 (repair-rule-manufactured gap) → VALIDATED: upheld

*For the paper:* (i) the 20–29% violation rate is measured pre-repair and is repair-independent — a robust headline already in the abstract; (ii) §6.6 discloses the repair rule in the same sentence as the gap ("after a deterministic time-order repair that drops the later task of each violating pair", L366); (iii) the counterfactual is a registered, internally controlled reanalysis (same solver/budget/population), not a straw arm; (iv) my A2.1 recomputation shows the gap equals the dropped mass — i.e., the number is *accountable*, not arbitrary.

*For VALIDATED:* the abstract states "lands 18–30 points below the endogenous dwell" (L29) with no repair qualifier, and the conclusion repeats it without one (L419). Because the gap ≈ dropped-task mass (A2.1), its magnitude is set by the choice of repair: a priority-aware drop loses less mass per pair (priorities are position-independent, so dropping the cheap task of each violating pair roughly halves the expected mass loss at the same pair count); a bounded re-timing arm has wide windows to absorb into (731–779 windows over 99–100 tasks on R3H). The paper's own claim that "a classical fixed-duration scheduler would ship the plan without knowing" (L366) compounds it — operational practice plans with margins, as DA2 notes. So the decision-relevant form of the number ("what does ignoring dwell physics cost?") is currently an upper-ish estimate presented as a point estimate in the two most-read locations of the paper.

*Ruling:* VALIDATED is the right call. The repair-independent 20–29% violation rate survives as the robust headline; the gap must carry its repair qualifier wherever stated. The letter's adjudication and revision path (T1) are sound. Neither CRITICAL invalidates the coverage–demand curves; both are framing/conditioning defects — correctly filed as blocking silent acceptance, not as fatal.

## 5. A4 new findings (manuscript-side, panel-wide misses)

1. **NEW-1 (MINOR, presentation) — C-label collision between constraint families and shape criteria.** §3.4 defines constraint families C1–C5 (L178–182); §5.3/§6.3/Table 3 reuse C1/C2/C3 for the frozen shape criteria (L260, L323, L339–341). A reader meeting "C1: not met" in Table 3 after §3.4's "C1 filters at generation time" must disambiguate by context alone. The collision propagated into the synthesis itself: the letter's consensus row "C7" discusses constraint "C3/C4" inside a table whose rows are labeled C1–C8. No seat flagged it. Fix: rename the criteria (e.g., S1–S3 or K1–K3).
2. **NEW-2 (MINOR, presentation) — "the single-satellite family" distinguishes nothing.** Abstract L29 and Conclusion L419 label R1C "the single-satellite family/control", but the entire study is single-satellite (§1.1 L44); §6.1 L302 introduces it as a name ("The control family is the single-satellite one"), so it is a label, not a contradiction — but it reads as if R2F/R3H were multi-satellite. E8 caught the other family-label inconsistencies and missed this instance; its fix should be extended.
3. **NEW-3 (MINOR, borderline) — §6.4's median-mechanism shorthand is arithmetically loose.** L352: "the median falls because the net of those two displacements is negative." A 10-seed median does not follow the sign of a two-seed net displacement; it follows the ranks of the central order statistics. The next sentence ("the median of ten readings following two of its members") states the correct mechanism, so the fix is deleting the net-sign clause. Safe to drop if space is tight.

No panel-missed defect found that touches a load-bearing number. Spot checks beyond the seats' recomputations: 477,308/13,845 = 34.48 ≈ 34.5 ✓; 345.7 kHz = 95.2×3630 Hz and 300.6×1150 Hz ✓; sweep rates 0.4233/0.6686 °/s × 4 s = 1.69/2.67° ≈ 1.7–2.7° ✓; pad-halving sensitivity: median transfer 5.643+2.784+2.0 = 10.427 s, halving the 1.129 s pad component moves it 5.4% ≈ "roughly 5%" ✓; R3H plateau from s=1.4 spans 0.18 pp ≈ one priority unit (1/(99×5.5) ≈ 0.18%) ✓; Table 2 observed columns match the §6.1 medians at rounding ✓; Table 3 verdicts are internally consistent with the §6.3 text once the criterion direction is honored (R2F C3 "not met" = the tight arm *fails to fall*, matching "its tight arm does not fall under either reading"). §3.5's three-mode-rules paragraph and §5.2's grandfathered composition are consistent. §5.3 vs §6.3 timelines agree (refined reading registered 2026-10-23 in both).

## 6. A5 verdict ruling

**Major Revision — upheld.** The defects that block acceptance are real and correctly identified (one abstract falsehood, one intra-paper self-contradiction, two validated CRITICAL framing defects, non-self-containedness), and none of them invalidates the coverage–demand curves: three independent verification streams reproduced the numbers, and my own recomputations of the load-bearing arithmetic (floor accounting, dropped-mass accounting, dip vs abstract) all confirm the manuscript's internal consistency. Minor Revision is not sufficient — two CRITICALs plus an abstract-level factual error exceed "minor" by any editorial standard. Reject is not warranted — every fix is rewording or reanalysis of existing artifacts; no seat and no finding here requires new experiments (only T2's *optional* composition-matched family would). The letter's verdict is the correct one.

## 7. A6 roadmap weighting notes

- **T19/DA8 remedy downgrade (the one real weighting defect).** DA8 is a MAJOR whose registered minimum remedy is "a tier-bound sensitivity sweep showing the step location moves with the knob"; T19 files it under Tier 2 with "ideally one tier-bound sensitivity point" — a must became an option. Every other Tier-2 MAJOR (M1, M3, P3, P4) has a wording exit that the *seat itself* offered; DA8 has none. Recommend: either restore DA8's sweep as mandatory within T19, or record an explicit editorial override with rationale.
- Tier 1 composition is otherwise correct: both CRITICALs, all abstract/self-containedness items, and the physics-layer corrections (T6/T7) are must-fix; T10 (minor-severity duplicates) is trivially cheap and highly visible, so Tier 1 is right.
- Tier 2/3 assignments otherwise defensible; DA12 (per-seed dispersion in Table 2) in Tier 3 while m6/m4 (counterfactual dispersion) sit in T16/Tier 2 is a mild asymmetry — same class of fix, different tiers — but the counterfactual numbers are the more decision-relevant, so the split is acceptable.
- **Watch item, not a conflict:** T5 (strip internal pointers/dates) vs the protected list ("the exact post-hoc-amendment dates"). These coexist if T5 translates *registry pointers* while keeping the *dates*; the letter should say so explicitly to prevent an over-execution of T5 that deletes the protected disclosure.
- No T-item contradicts another T-item; the "explicitly protects" list is consistent with all 19 items.

## 8. Provenance

Tool: Claude Code (CLI session), harness-reported model string `ccs-claude-huoshan--ark-code-latest` (routing identity per local configuration; reported as-is per the "panel identity ≠ actual tier" rule). Fresh context: this session began with only the briefing file; no prior session history, no reads of anything under `review/` outside `panel-full-20261023/`. Read-only throughout; the only write is this report. Materials read in full: briefing, editorial-decision.md, seat1–seat5 reports, main.tex (all 438 lines); formula-spec.md read in targeted part (header L3; §8.17 items 9 and 13 at L586/L594). Computations run (all read-only python one-liners): occurrence counts for the two duplicated blocks, "caliber"/"registered" counts, and the arithmetic in §3 (dropped-mass estimates, floor accounting, R2F grid range, velocity ratio 1.0493, and the §5 spot checks). No LaTeX builds, no test suites, no network.

REREVIEW-VERDICT: synthesis SOUND-WITH-CORRECTIONS — CRITICAL: 0 | MAJOR: 0 | MINOR: 3
