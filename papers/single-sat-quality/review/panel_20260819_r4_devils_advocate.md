# Devil's Advocate Review — Second Full Panel (2026-08-19)

**Manuscript:** "Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite" (42 pp, EN)
**Revision state:** commits 04ad144, ab2fad9, 125e132 applied; pre-gate PASSED (167/0, 1800 sol 0 constraints, 76190 windows 0 C1 violation).
**Prior DA review (2026-08-18):** 0 CRITICAL, 6 MAJOR — all addressed by F1-F8 revisions.

---

## Strongest Counter-Argument (200-300 words)

The revisions successfully reframed the headline from an unconditional "boundary" to a qualified regime, ran a genuine matched-reference-point control, and fixed the 0.3 m error. But the paper's most visible number — the abstract's "+34% geometric quality gain" — is selector-dependent in a way the abstract does not disclose. The +34% (0.394 vs 0.295) is the **knee point** of the MOEA-2 front. The same front's best-coverage point achieves only f2=0.332, a +12.5% gain over G-BL. The paper transparently documents this in §5.3 ("at sparse S1 the knee and best-f1 means differ by about 0.04–0.06... expected and intentional"), but the abstract, §1, §6.1, and conclusion all report +34% without noting that it characterizes the balancing knee, not the coverage-maximizing operating point. A mission planner who reads the abstract and expects +34% quality at 14% coverage loss gets the knee; a coverage-priority operator gets only +12.5%. This is not a data error — the knee is a legitimate trade-off point — but it is a reporting gap between the headline claim and the selector specification buried two sections later.

Second, the F1 terminology revision is incomplete: "redundancy" and "coverage ceiling" survive in at least six locations (lines 965, 1080, 1150, 1160, 1347, 1364) despite the abstract and contributions now insisting on "indistinguishable under tested search" and "coverage reference." This creates internal contradiction — a reader encountering line 1080 ("third-objective redundancy") after reading line 157 ("indistinguishable from the two-objective") sees two different claims.

Neither issue is fatal. The science is sound, the controls are genuine, and the data is clean. But both should be fixed before submission.

---

## Issue List

### CRITICAL: 0

No CRITICAL findings. The data integrity is verified (pre-gate), the matched-p control is a real experiment (not a relabel), and the core geometric-coupling mechanism is empirically supported.

### MAJOR

**M1 — Headline +34% is knee-selector-specific; not disclosed at claim sites.**
- **Dimension:** Reporting / internal consistency
- **Location:** Abstract line 41 ("MOEA-2 extracts a +34% gain"); §1 line 138; §6.1 line 774; Conclusion line 1405. Selector specified only at §5.3 lines 733-745.
- **Evidence:** §5.3 reports S1 knee vs best-f1 differ by 0.04-0.06 in f2. From the frontier data, MOEA-2 S1 knee f2=0.394 (+34% vs G-BL 0.295); best-f1 f2=0.332 (+12.5%). The +34% is the balancing knee, not a universal MOEA-2 property. The paper says this is "intentional" but the claim sites don't qualify the number.
- **Why it matters:** The abstract's +34% is the paper's most-cited number. A reader cannot tell from the abstract that this requires accepting the knee (14% coverage loss AND the quality-coverage balance point). The best-coverage MOEA-2 point delivers only +12.5% f2.
- **Fix:** Add "at the knee (trade-off) point" or equivalent at every +34% claim site (abstract, §1, §6.1, conclusion), or report both knee and best-f1 f2 in the abstract.

**M2 — F1 terminology revision incomplete: "redundancy" and "coverage ceiling" survive.**
- **Dimension:** Internal consistency
- **Locations:**
  - Line 965: "the dense-regime redundancy is established near the full-coverage working point"
  - Line 1080: "The third-objective redundancy is therefore an empirical convergence effect"
  - Line 1150: "This constrains the coverage-ceiling claim"
  - Line 1160: "The coverage ceiling is thus a G-BL initialization effect"
  - Line 1347 (Limitations): "The 3-objective redundancy reported above"
  - Line 1364: "the coverage-ceiling result reflects the combination"
- **Evidence:** F1 replaced "boundary" with "regime," "ceiling" with "reference," and "redundant at operational densities" with "indistinguishable under the tested search" in the abstract, contributions, §7.2, and conclusion. But the six sites above retain the old language, contradicting the qualified wording.
- **Fix:** Replace "redundancy" → "indistinguishability under the tested search" (or "convergence") at lines 965, 1080, 1347; replace "coverage ceiling" → "coverage reference" or "coverage convergence" at lines 1150, 1160, 1364.

### MINOR

**m1 — "pixel area scales as 1/f2" is approximate, not exact.**
- Location: §7.2 line 1303-1304.
- f2 = sin(θ_elev)cos(ψ_sq); actual pixel area ∝ 1/(sin θ_target cos ψ_sq). θ_elev differs from target-side θ by "a few degrees" (line 374). At θ≈30° this is a ~3-5% discrepancy. "Roughly a 25% reduction" already hedges with "roughly," but "scales as" implies exact proportionality.
- Fix: "pixel area scales approximately as 1/f2" or note θ_elev ≈ θ.

**m2 — Matched-p control is valid but could be stronger.**
- Location: §6.4 lines 996-1001.
- p=4 gives H=15 for 3-objective MOEA-3; MOEA-2 p=12 gives H=13. The comparison (MOEA-3 p=4 vs p=12) shows f3 is invariant to reference-direction density, which is the right test. A purist would also run MOEA-2 at matched H, but the current control adequately addresses the confound. No action required; note for completeness.

**m3 — r_null=-0.51 labeled "anchor-independent result" but is analytic algebra.**
- Location: Abstract line 60 ("anchor-independent geometric-coupling result"); Contribution 1 line 166-171.
- r_null=-0.51 is a closed-form moment integral (line 1042-1047). The genuinely empirical anchor-independent result is the attenuation from envelope -0.97 to schedule -0.63/-0.15. r_null is an analytic baseline, not a finding. Consider "anchor-independent geometric-coupling baseline" or distinguish the analytic null from the empirical progression.

**m4 — Line 965 "dense-regime redundancy" directly contradicts line 157 "indistinguishable."**
- (Subsumed by M2 but flagging the most visible contradiction.)

**m5 — Sparse MOEA gains rely on 45° envelope; abstract silent.**
- The abstract reports +34%/+41% without the §3.1 caveat that 45° "deliberately exceeds typical operational agility." §7.2 now caveats G-SM but the MOEA sparse gains exploit the same envelope. One clause in the abstract ("under the tested 45° squint envelope") would close the gap.

---

## Ignored Alternative Explanations

1. **The knee selector is a value judgment, not a neutral default.** Maximizing normalized sum implicitly weights all three objectives equally. An operator who weights coverage 3× quality would select a different front point with different f2/f3 gains. The paper does not justify equal weighting. (Related to M1.)

2. **The r_null=-0.51 analytic null assumes uniform θ_elev ∈ [15°,50°] and ψ_sq ∈ [-45°,45°], but real visibility windows do not sample these uniformly** — they are concentrated by orbital mechanics. The paper acknowledges the envelope correlation (-0.97) uses real geometry, but the null's uniform assumption may overstate the "structural conflict." The Monte Carlo validation (r_MC=-0.5120) confirms the integral, not the realism of the prior.

3. **Variant C inertness (θ_elev varies ~1.5° within window) explains why removing θ has no effect, but this also means f2 is almost entirely a squint metric within a window** — the "geometric resolution" objective is effectively a squint objective for per-window selection. The cross-window θ variation (which f2 doesn't capture because θ_elev is near-constant within a window) is the only place the incidence component operates.

---

## Missing Stakeholder Perspectives

- **Mission operator selecting a front point:** The paper gives a knee point but no guidance on how to select alternative points for different coverage/quality weights. The operational guideline says "MOEA-2 may provide gains" without saying which front point to use.
- **SAR systems engineer:** The plane-Earth approximation's 17% R³ error at 47° is disclosed, but its impact on the f3 ranking across the 18°-47° range is not quantified. If the approximation biases high-incidence schedules, the G-SM high-f3 result could partly be artifact.
- **Reproducibility auditor:** The knee selector code (moea.py) is in the repo, but the paper doesn't cite the file/function. A one-line pointer would help.

---

## Observations (non-defects)

- The matched-p control (f3=0.702 at p=4 vs 0.699 at p=12, paired p=0.149) is a genuine experiment that converts a limitation into evidence. Well done.
- The envelope-null-schedule decomposition (-0.97 → -0.63 → -0.15) is the paper's strongest empirical contribution and survives all qualifications.
- The hot-start conditioning is now stated at every claim site; the random-init deficits (0.39-0.68) honestly bound the coverage convergence.
- Pre-gate data integrity is verified; no constraint violations across 1800 solutions or 76190 windows.
- GA-P-BL relabeled as control is correct and improves clarity.
- pymoo version, wall-clock, and central-angle fix are appropriate additions.

---

## Verdict

**CRITICAL: 0. MAJOR: 2 (M1 selector qualification, M2 terminology residue). MINOR: 5.**

No CRITICAL — the IRON RULE does not block Accept. The two MAJORs are prose/reporting fixes (no new experiments needed): qualify +34% as knee-specific at claim sites, and complete the F1 terminology replacement in six residual locations. Both are ~30 minutes of editing. The manuscript is scientifically sound and publication-ready after these fixes.
