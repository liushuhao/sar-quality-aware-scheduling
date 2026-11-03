# R3 Review — Cross-Disciplinary / OR & Mission-Operations
# Panel 2 (post F1-F8 revisions), 2026-08-20

**Reviewer:** Cross-disciplinary / operations-research & mission-operations perspective
**Manuscript:** `small-paper-ijae.tex` (EN, 42 pp, HEAD 125e132)
**Target:** Advances in Space Research
**Pre-gate:** verify 167/0, full_hard 1800/0, cross_solver PASS, gapbl 0, moea_live 0, window_c1 76190/0 — accepted as clean.

## Verdict: ACCEPT WITH MINOR REVISIONS
0 CRITICAL, 0 MAJOR, 8 MINOR. Impact score: **72/100** (up from 62 in panel 1). The F1-F8 revisions materially improved operational honesty: the 45° envelope caveat (§7.2:1311-1314), knee selector spec (§5.3:733-745), wall-clock (§5.2:698), central-angle correction (§5.1:663-665), and p4 control (§6.4:996-1001) all land. The qualified-regime framing is now defensible. Remaining issues are residual wording and two small operational gaps.

---

## MINOR findings

### M1. Residual "coverage ceiling" in §6.6 (F1 not fully propagated)
Lines 1150 and 1160 still use the old term:
- L1150: "This constrains the **coverage-ceiling claim**: proximity to G-BL is initialization-dependent."
- L1160: "The **coverage ceiling** is thus a G-BL initialization effect rather than an artifact of the MOEA framework."

Everywhere else F1 changed "ceiling" → "reference" (abstract L57, intro L140, §7.2 L1322, conclusion L1408/1428). These two in the hot-start paragraph are inconsistent. Change to "coverage-reference claim" / "coverage convergence" so the reader doesn't see a surviving absolute claim.

### M2. Residual "redundancy" without qualifier in §6.4 and Limitations
F1 changed conclusion/abstract to "indistinguishable from the two-objective formulation under the tested search," but several body sites still say "redundant/redundancy" bare:
- L627 (§4.4 research question): "geometric coupling renders the third objective **redundant**" — acceptable, this is the hypothesis.
- L965 (§6.4 Phenomenon 1): "the dense-regime **redundancy** is established near the full-coverage working point" — should be "indistinguishability" or "convergence."
- L1080 (§6.4 mechanism): "third-objective **redundancy** is therefore an empirical convergence effect" — partially qualified ("empirical convergence effect, not mathematical identity") but the noun still overstates.
- L1347 (Limitations opening): "The 3-objective **redundancy** reported above is specific to..." — should match conclusion wording.

Not a scientific defect; a consistency cleanup so the qualified framing holds throughout.

### M3. "Five solvers" residual in §7.1 (F3 not fully propagated)
- L1275: "Friedman test on pooled HV confirms overall differences among the **five solvers**" → "five configurations" (F3 changed §5.3 L714 but missed this §7.1 sentence).
- L1245: "all solvers converge to the G-BL anchor and the greedy baseline is **operationally sufficient**" — this sentence in §7.1 summary states operational sufficiency without the hot-start condition, even though finding (5) at L1267 immediately below says "conditional on the hot start." Add "under the G-BL-seeded configuration" at L1245 or cross-reference finding (5).

### M4. Timeliness motivation still unqualified in §1
Limitations L1375-1380 explicitly states timeliness is not an objective and the disaster/maritime motivation is "addressed only indirectly." But §1 L73-75 still leads with "time-critical monitoring missions, from disaster response to maritime surveillance" with no forward pointer. A reader reaches Limitations 60 pages later. Add a clause at L75 or L107 ("the present model optimizes quality/quantity at a fixed timeliness operating point; see §7.4") so the motivation isn't oversold. This is the same gap panel 1's R3-M2 raised; the Limitations acknowledgment exists but the motivation still promises more than the model delivers.

### M5. Operational guideline skips N=100–300 transition band
§7.2 L1316-1322 gives "N≲100 → MOEA-2" and "N≳300 → greedy," but the 100–300 band — where the paper's own data show f1* deficit collapsing from 10% (S2) to 0% (S3) and f2 gain from +3.5% to +0.4% — is unaddressed. S7 (N=150, +1.3%) and S8 (N=200, +0.8%) were run precisely to locate this transition (§5.1 L680-684) but the operational guideline doesn't use them. One sentence: "In the transition band N∈[100,300], MOEA-2 offers <1.5% f2 gain with occasional small coverage deficits; greedy is recommended unless the marginal quality is mission-critical." This would make the guideline actionable across the full tested range.

### M6. G-SM dense-regime recommendation separated from its envelope caveat
§7.2 L1308-1314 states G-SM's +16% f3 at S4 and then the 45° envelope caveat. But the actual recommendation at L1320-1321 ("G-SM for radiometric priority") is 6 lines later and does not repeat the caveat. An operational reader skimming the guideline sees "G-SM for radiometric priority" without "only under high-squint envelope; re-quantify for typical few-degree platforms." Move or repeat the caveat at L1320 so the recommendation and its boundary condition are adjacent.

### M7. C3/C4 still framed as "four constraints" despite being non-binding
L469: "The remaining **four constraints** couple task selection..." L508-512 explicitly states C3/C4 are "non-binding under all tested scenarios... retained for completeness." If E_max=10^7 and M_max=10^11 are set above every feasible schedule by construction (typical per-task e=5×10^4, so even 500 tasks use 2.5×10^7 ≪ 10^7... wait: 500×5×10^4 = 2.5×10^7 > 10^7). Let me check: L512 says "typical per-task e_i=5×10^4"; S4 selects ~142 tasks (Table ablation L84: n_sel=142.3), so energy used ≈ 7.1×10^6 < 10^7, non-binding. But if all 500 tasks were selected it would be 2.5×10^7 > cap — the cap binds only at full selection, which never happens. The paper should state this more precisely: C3/C4 are "inactive in the tested scenarios because observed task counts (≤~200 at S3, ≤~142 at S4) stay well below the caps" rather than "sufficiently high." Minor honesty/ precision point. Also L469 "four constraints" should acknowledge C3/C4 are inactive (e.g., "two active constraints (C1–C2) plus two inactive resource caps (C3–C4) retained for completeness").

### M8. Bilateral side-flip under C2 not explicitly addressed
C2 (L486-496) uses arccos of the 3D LOS dot product, which automatically penalizes a left-to-right side flip (large angular gap → large Δη → infeasible if time gap insufficient). This is correct. But there is no sentence confirming it. A reader may wonder whether bilateral-looking schedules require an additional side-switch constraint. One sentence: "The 3D angular-gap formulation in C2 automatically penalizes cross-side maneuvers; no separate side-flip constraint is needed." This is a clarity MINOR, not a defect.

---

## What the revisions got right (no action)

- **Pixel-area 25% mapping** (L1303-1304): verified. f2 0.295→0.394, area ratio 0.295/0.394=0.749, reduction 25.1%. Correct and replaces the stale 0.3 m cleanly.
- **p4 matched-reference control** (L996-1001): f3=0.702±0.041 vs p=12 0.699, paired p=0.149 — this is the right evidence and closes panel 1's F4 cleanly. Five sentences in the mechanism section is appropriate; not operational overhead.
- **Wall-clock** (L698): 22/66/220/260 s median matches runner data (22/67/220/262). The latency gap (ms vs minutes) directly supports the dense-regime greedy recommendation rather than undermining it.
- **Central angle** (L663-665): ±608 km = ±5.5° ground central angle at 47° incidence, not off-nadir. Geometrically correct (eta=41.3° off-nadir, 5.7° central angle).
- **Knee selector** (L733-745): spec is now precise (min-max normalized sum), and the sensitivity verification (N≥100 Δ≤0.005; S1 Δ0.04–0.06 intentional) is honestly reported.
- **f3 cross-window caveat** (L285-291): sinθ spans 2.4× across 18–47°; ordering defense strongest within-window (θ_elev ~1.5°). Well-stated.
- **pymoo version** (L703): 0.6.1.6 stated.
- **Unweighted mean** (L415-417): choice stated and defended.
- **Anchor-independent geometric coupling** (r_null=-0.51, envelope -0.97, schedule -0.63→-0.15): this is the paper's durable result and survives every caveat. Promoted to co-headline in abstract/conclusion.

---

## New issues introduced by revisions
None of substance. The residual wording in M1-M3 is the only category — F1/F3 were applied at claim sites (abstract, conclusion, §7.2) but not fully propagated to body paragraphs (§6.4, §6.6, §7.1). This is a consistency pass, not a scientific problem.

The qualified-regime framing does not overwhelm the result: the abstract leads with conditional language (L57-59) but immediately follows with the anchor-independent coupling result (L60-62), giving the reader something unconditional to take away. Good balance.

---

## Recommendation
**Accept with minor revisions.** All 8 MINOR items are wording/consistency fixes or one-sentence additions; no new experiments, no re-analysis, no data changes. The paper is substantively ready. The operational message is now credible: sparse N<100 → MOEA-2 for geometric quality or MOEA-3 for radiometric (under high-squint envelope); dense N≥300 → G-BL (coverage) or G-SM (radiometric, envelope-dependent); transition band 100–300 needs one sentence. The anchor-independent envelope-null-schedule decomposition is the transferable contribution and is properly positioned.

Estimated revision effort: <1 hour prose.
