# Devil's Advocate Report — Seat 5

## 1. Strongest Counter-Argument

The paper's three headline quantities — the 46.6-point collapse, the 18–30-point counterfactual gap, and the causal title — each trace to an author-chosen knob rather than to a property of the world. The coarse tier [2.5, 3.0] m was placed to straddle the 2.4669 m stripmap floor (the paper's own §5.1), so the floor step is template arithmetic, not a discovered law. The mode assignment was frozen by a comparability policy (formula-spec §8.17-9: re-cutting "would break comparability" with the earlier curve) that forbids exactly the re-routing an operator would perform when a requirement passes the floor — a 2.4 m requirement at moderate squint is physically routable to sliding spotlight under the paper's own registered feasibility test, so the catastrophe is policy, not physics. And the counterfactual's 18–30 points are set by a drop-the-later-task repair that no operational planner would use in preference to re-timing. Strip the three knobs and what remains is: an algebraic identity (delivered = required, by construction), a single-machine schedule with one binding constraint (C2) plus a floor check, on which a greedy single-pass repair is unbeatable in 258 of 260 units, swept once on one synthetic template, one satellite, ten seeds. The paper discloses almost all of this — unusually honestly — which is exactly why the correct target is the residual gap between the back-matter disclosures and the title, abstract, and contribution list. Minus the discipline narrative, the surviving sentence is "requirements finer than the stripmap floor are infeasible, and squint-dependent dwells differ from library dwells" — true, but not a scheduling finding at this venue class.

## 2. Issue List

### CRITICAL

**[DA1] CRITICAL — internal validity / confounded design — §6.1: "The three families covary in mode composition as they do in task count".**
The title asserts "Mode Composition Decides What Tighter Requirements Cost," yet in all three families mode composition is perfectly confounded with task count (20/50/100), window density (145–162/337–391/731–779), and tier mix. R2F's flatness — half of the "three shapes" result — is as attributable to capacity slack at N=50 as to the absence of stripmap; the paper never measures C2 tightness per family per grid point, and the one arm that would have begun to deconfound (larger-N families) was retired at registration (§5.2, R4H). No crossing cell (e.g., a no-STR family at N=100, or an all-STR family at N=50) exists in the design. A causal title claim from n=3 confounded cells is not supportable, and the paper's own sentence quoted above concedes the confound without addressing it. Resolution: run the 2×2 (composition × density) crossing, or retitle/reword to a descriptive claim ("coverage response under three frozen mode mixes").

**[DA2] CRITICAL — counterfactual fairness / construct validity — §6.6: "drops the later task of each violating pair".**
The abstract headlines that fixed-dwell planning "lands 18–30 points below the endogenous dwell." That magnitude is manufactured by the repair rule: dropping the later task of each violating pair destroys, by construction, roughly the priority mass of the violating pairs (184/926 pairs ≈ 18.4 tasks of ~100 → 18.25 points; 135/458 ≈ 13.5 of 46–50 → 30.44 points — the arithmetic is essentially the dropped-task mass), so the number measures the punitiveness of drop-based repair, not the value of endogenous dwell. The standard scheduler response is left-shift re-timing inside the (wide, 731–779-window) feasible intervals, or carrying a dwell margin — neither arm is run; the fixed arm is the crudest possible baseline (zero-squint library dwell, no margin). The paper also claims "a classical fixed-duration scheduler would ship the plan without knowing," misrepresenting operational practice, which routinely plans with margins and replans. Resolution: add left-shift-repair and margin-carrying fixed-dwell arms; report the violation rate (robust) and the repaired gap under each rule separately, and drop the single-number headline if it moves.

### MAJOR

**[DA3] MAJOR — circularity / contribution inflation — §1.2: "the required resolution as a per-task hard constraint".**
For SLS/SPT, C5 is satisfied by deriving mode parameters from the requirement (A_task, β_task), so no search decision can ever violate it; the paper admits this ("a raise-guarded identity rather than a scored constraint", §3.4). The residual independent content of the "platform" leg is: the dwell closures feeding one binding constraint (C2) plus the stripmap floor check. Of the five constraint families, C1 is generation-side, C3/C4 are slack, the AASR gate removed zero tasks (§5.1), and C5 is an identity — yet contribution 1 and the abstract sell "per-task hard constraint" and a five-family constraint apparatus. The platform is a dwell calculator; calling its output constraint a "hard constraint" is rhetorical inflation. Resolution: restate contribution 1 as dwell-closure + transfer-chain feasibility; reserve "hard constraint" for the floor check, the only place requirement genuinely excludes solutions.

**[DA4] MAJOR — designed artifact / floor arithmetic — §6.1: "for 44.78 of the 46.58-point drop".**
The paper's own Table 2 shows the floor-exclusion bound accounts for 96% of the R3H collapse at s=0.8 and 77% at s=0.9 — i.e., the mixed family's headline fall is the stripmap floor reproducing R1C's arithmetic, a direct consequence of placing the coarse tier to straddle 2.4669 m ("sits inside the coarse tier", §5.1) and of the frozen assignment. Under the paper's own registered feasibility test (A_task ∈ (0,1) ⟺ ρ_req·cosψ_sel < 2.4669), a material fraction of the "dead" coarse-tier tasks at s=0.8–0.9 are physically routable to SLS at low-to-moderate squint; the freeze forbids the rescue, and formula-spec §8.17-9 records the freeze's motive as curve comparability, not physics. The abstract still headlines 46.6 points unqualified. Resolution: state the floor-share next to every headline drop number (not only in §6.1), and quantify how much of the drop a registered-policy re-router would recover.

**[DA5] MAJOR — preregistration narrative — §5.3: "the headline curve is a post hoc descriptive reading".**
The amendment registering the coverage–demand curve as the main result form is dated 2026-10-21, after the 2026-10-20 sweep; the "refined reading" of criteria verdicts is dated 2026-10-23, after the 2026-10-22 external review; formula-spec v1.9 (which introduced the task-level parameter law C5 depends on, and §8.17-13's redefinition of the C3/C4 reference after false violations were measured — R2F 1.2008×) is also dated 2026-10-20, the same day the sweep ran. What was genuinely pre-registered for this world is the grid and three shape criteria; the estimand, the model's final constraint semantics, and the verdict-reading conventions all post-date contact with the data or review. The paper states the dates exactly — commendably — but contribution 3 ("a discipline that keeps the result falsifiable") and the abstract's "frozen in advance" sell more than the timeline supports; a registered-report referee would reject the discipline claim. Separately, §3.4 calls C3/C4 "structurally never binding ... their normalised values cannot exceed 1.0" as design semantics, when formula-spec §8.17-13 shows that property was engineered on 2026-10-20 by redefining the reference to the envelope maximum after the old reference produced violations. Resolution: downgrade contribution 3 to what it is (frozen grid and criteria, honest post-hoc disclosure); disclose the C3/C4 reference redefinition explicitly.

**[DA6] MAJOR — internal inconsistency / unquantified sensitivity — §6.4: "so they are invariant to it".**
§3.1 states that coverage readings "carry the [velocity] convention" because they mix dwells with velocity-independent constants; §6.4 states the opposite — that coverage readings are "invariant to it." Both cannot hold: if all dwells scale by α while the maneuver bound (4.07 s), settle (2 s), and window lengths do not, C2 feasibility at the margin changes, hence coverage changes. The paper itself quantifies an exactly analogous effect ("halving the pad moves the median requirement by roughly 5%"); an inertial-vs-ground velocity convention plausibly shifts dwells by ~8–12%, which is material for a mechanism the paper says lives at the C2 margin (20–29% of pairs sit close enough to violate under a dwell perturbation). Resolution: correct §6.4, and run the sweep once under an alternative velocity convention as a sensitivity check.

**[DA7] MAJOR — selective reporting — Abstract: "(0.93 points paired per seed)".**
The loosening recovery for R2F is headlined as 2.36 points (median-of-medians vs. the s=2.0 grid boundary) while the paired per-seed median, 0.93 points — 2.5× smaller and arguably the right estimand given the paper's own per-seed pairing logic elsewhere — sits in parentheses, unexplained; R3H's 4.15-point headline gets no paired counterpart at all. The two statistics diverge because the s=2.0 median saturates at 1.0000 while several seeds already sit there; which number is "the" number changes whether loosening "recovers" anything operationally meaningful. Resolution: report both statistics for both families, state why they diverge, and pick one as primary before the abstract.

**[DA8] MAJOR — external validity / missing sensitivity — §5.1: "a registered synthetic template parameter, not a measured campaign profile".**
The template is bimodal ([2.5,3.0] ∪ [0.3,0.6] m) with no demand between 0.6 and 2.5 m — exactly the mid-band where real product requests (1–3 m class) concentrate and where mode routing is genuinely contested. No sensitivity to tier bounds, tier mix ratio, or priority distribution (uniform randint, disclosed as bookkeeping) is run, yet the location and size of the headline floor step are direct functions of the tier-bound placement. The paper never claims real-demand validity, but its title-level claim is stated unconditionally. Resolution: at minimum a tier-bound sensitivity sweep showing the step location moves with the knob; ideally one mid-band tier.

### MINOR

**[DA9] MINOR — overstatement — §1.1: "the greedy anchor already attains the family maximum in 258".** §4.5 correctly says "attains the best coverage found for the unit in this study" — best-found under one weak search (40/60 budget, 200-dim problems), not a maximum. The intro's stronger wording is unsupported. Resolution: align intro with §4.5.

**[DA10] MINOR — editing — §3.4 and §5.1: duplicated sentences.** "Across the five constraint families, the set that actually binds ... five mechanisms bind" appears twice in one paragraph (§3.4); "Across the 30 released R-family manifests ... ever binding in this scenario world" likewise (§5.1). Resolution: delete duplicates.

**[DA11] MINOR — abstract precision — Abstract: "within 0.27 points throughout".** The conclusion's correct phrasing is "at every tighter point"; R2F gains 2.36 points toward s=2.0, so "throughout" overstates flatness. Resolution: mirror the conclusion's wording.

**[DA12] MINOR — uncertainty quantification.** Ten seeds, scenario and search noise confounded by design (disclosed), medians without dispersion or intervals; third-decimal-point claims (0.9764 vs 0.9764) rest on this base. Resolution: per-seed intervals in Table 2.

**[DA13] MINOR — verifiability — Data availability.** Preregistration chain and artifacts deposited "upon acceptance," available on request meanwhile; the timeline underpinning contribution 3 is currently self-attested. Resolution: deposit the preregistration file and L8 artifacts before or at submission.

## 3. Ignored Alternative Explanations / Paths

- **R2F flatness = capacity slack, not mode composition.** No STR family at N=50, no non-STR family at N=100, and no C2-tightness measurement per grid point; the flat curve is equally consistent with "50 tasks leave re-timing headroom."
- **20–29% violation rate = absence of margin in the baseline.** A fixed-dwell forecast with an industry-style margin (the paper's own 25% pad semantics) would shrink the violation count; the zero-margin library arm maximizes it.
- **258/260 anchor optimality = weak search.** 2,400 evaluations on 198–200-dimensional chromosomes is a small budget; anchor-equals-best-found is also what premature convergence around an injected elite looks like. The two R1C exceptions show the search can improve, so the 258 figure bounds the search, not the anchor.
- **The 6.0-point residual at s=0.9 (bound 0.748 vs obs 0.688)** — the only part of R3H's drop not explained by the floor — is unexamined; it could be anchor myopia (single bounded pass) rather than physics.
- **The "0.93 vs 2.36" divergence** (DA7) is a distributional artifact the paper does not explain.

## 4. Missing Stakeholder Perspectives

- **Operational AEOS planners:** portrayed via the "would ship the plan without knowing" caricature; real systems plan with margins and repair by re-timing, and are the very population the counterfactual claims to judge.
- **SAR payload/system designers:** with NESZ uncalibrated and the resolution-vs-swath trade out of scope, the headline claim is unusable for the design decisions it most resembles.
- **Mid-band product customers (0.6–2.5 m):** entirely unrepresented by the bimodal template, though they are the class most affected by mode-routing policy in practice.
- **Constellation operators:** single satellite, no downlink, no dynamic arrival — conclusions silent for the multi-satellite setting where most tightening decisions are made.
- **Registered-report referees / replicators:** asked to accept a self-hosted, post-hoc-amended registration chain on request-based access (DA5, DA13).

## 5. Observations (Non-Defects)

Challenges the paper already adequately answers; recorded so the panel does not re-litigate them:

- **C5 circularity as such:** the paper labels it "a raise-guarded identity rather than a scored constraint" and enumerates the binding set (C2 + floor) explicitly; only the contribution-1 rhetoric (DA3) remains attackable.
- **Floor dominance:** Table 2 and the 44.78/46.58 sentence state it plainly; the defect is placement (abstract), not concealment (DA4).
- **Infeasible-cell handling:** "an infeasibility record, not a coverage of zero" — kept off the curve, never averaged, cross-drawn in the figure; exemplary.
- **Search-vs-construction separation:** measured (258/260), stated in the intro, and used consistently to block optimizer attributions; the two exception units are recorded with their gains.
- **Preregistration dates:** stated exactly, including the post-hoc status of the headline form — the honesty is real; the issue is only the contribution-3 packaging (DA5).
- **R2F dips:** per-seed accounting shows two opposite single-seed displacements, and no monotonicity claim is drawn from third-decimal moves.
- **AASR direction contrast:** flagged as a difference of registered model semantics, not a refutation of Song et al.; the squint-invariant SPT degeneracy is derived structurally.
- **Scope discipline:** five registered scope statements, the frozen-assignment qualifier in the abstract's last sentence, caliber labels traveling with the fulfillment ratio, and no cross-family quality comparison.

## 6. Provenance

Fresh subagent context; manuscript `main.tex` and supporting `refs.bib` / `formulas/formula-spec.md` read in full or in targeted part; no visibility into other seats' outputs or anything under `review/` prior to writing this report; same model family as other seats; no human reviewer in the loop; no builds, test runs, or network access performed.

VERDICT: DA panel contribution | CRITICAL: 2 | MAJOR: 6 | MINOR: 5
