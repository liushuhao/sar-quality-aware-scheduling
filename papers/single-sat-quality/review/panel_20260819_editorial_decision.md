# Editorial Decision — Second Pre-Submission ARS Panel (2026-08-19/20)

**Manuscript:** small-paper-ijae.tex (EN, 42 pp, HEAD 125e132) + ZH mirror
**Panel:** EIC + R1 method + R2 SAR/domain + R3 cross-domain + Devil's Advocate, independent fork agents
**Pre-gate:** PASSED 2026-08-19/20 — verify 167/0 CALIBER OK; full_hard 1800 sol OOW/C1-C4=0 (2205s); cross_solver PASS; gapbl 0; moea_live 0; window_c1 76190 windows 0 violations.
**Prior round:** 2026-08-18 Minor Revision F1-F8, all closed (commits 04ad144/ab2fad9/125e132); re-review 2026-08-18 Accept.

---

## Decision: MINOR REVISION

**0 CRITICAL across all five seats** — DA reports 0 CRITICAL, so the IRON RULE bar to Accept is not tripped. Two MAJOR findings (consensus R1+DA) are selector-disclosure and terminology propagation; both are ~30-min prose fixes, no data work. The paper is substantively sound and publishable after a final wording pass.

**Scores:** EIC Accept; R1 rigor 84/100; R2 domain 80/100; R3 impact 72/100 (up from 62); DA 0 CRITICAL.

The F1-F8 revisions materially improved the paper (R3 impact +10 points). The matched-p control (F4) is singled out by EIC and R2 as decisive. The one genuinely new substantive issue this round is **G1**: the headline +34% f2 gain is a knee-point value; the best-f1 point yields only +12.5%. This is not an error — the paper's thesis is a quality/coverage trade-off, so the knee (balanced) point is the right one to report — but the selector dependence must be disclosed at the claim sites, not only in §5.3.

---

## Required (consensus MAJOR)

### G1. Disclose knee-point dependence of the +34% f2 headline [R1-M2, DA-M1] — MOST IMPORTANT
At S1, MOEA-2 f2 = 0.394 at the knee (+34% vs G-BL 0.295, at 14% coverage cost), but the best-f1 front point gives f2 = 0.332 (+12.5%). The +34% therefore depends on choosing the balancing knee, which is currently specified only in §5.3.
**Fix:** At each +34% claim site (Abstract ~line 41; §1 contribution ~line 132; §6.1 ~line 724; §6.3 Table 4 caption; Conclusion ~line 1374), add "(knee-point value; the best-coverage front point gives ~12-13%)" or equivalent one clause. Keep +34% as the reported value (it is the legitimate trade-off point), but disclose the range. Do NOT change Table 1 (it correctly reports the knee). ZH mirror.
Verified from data: knee f2=0.393, best-f1 f2=0.332, G-BL 0.295 → +33.6% vs +12.5%.

### G2. Terminology propagation: residual "ceiling"/"redundancy" [EIC-M1, R3-M1/M2, DA-M2]
F1 changed "boundary/ceiling" to "regime/reference" but three critique sentences still say "coverage-ceiling claim/result" (§6.6 lines ~1150, 1160; Limitations ~1364) and three bare "redundancy/redundant" survive (§6.4 ~965, 1080; Limitations ~1347) where the qualified "indistinguishable under tested search" was intended.
**Fix:** "coverage-ceiling claim/result" → "coverage-convergence claim/result" / "coverage-reference claim"; bare "redundancy" at results sites → "indistinguishability under the tested search" (the Abstract's "density-dependent rather than redundant" is fine — that is the thesis claim, keep). ZH mirror. Pure find-replace, ~10 min.

---

## Should-fix (MAJOR-adjacent, single-seat but cheap and correct)

### G3. F4 matched-p wording: "matched" overstates [R1-M1]
p=4 collapses MOEA-3 reference directions from H=91 to H=15 (magnitude comparable to MOEA-2's H=13), but it is a 3-objective run vs MOEA-2's 2 objectives — not a strict two-way match. The paper currently says "matched to MOEA-2's H=13."
**Fix:** "matched to" → "comparable in magnitude to" (H=15 vs H=13). Conclusion unchanged (paired p=0.149). ZH.

### G4. Abstract silent on the 45° squint envelope [R2-M1, DA-minor]
The body now caveats that sparse gains and G-SM's +16% are quantified under a 45° envelope exceeding operational agility, but the Abstract leads with +34%/+41% without a qualifier.
**Fix:** Add one short clause in the Abstract near the sparse-gain sentence, e.g. "under a deliberately generous 45° squint envelope." One line. ZH.

### G5. "single-pass" needs defining [R2-M2]
The paper propagates over two orbital periods (~200 min, 1-2 windows/target); "single-pass" reads as one overflight in SAR convention.
**Fix:** One defining sentence in §3.1 or §5.1: "single-pass" here denotes a single satellite over a two-orbit scheduling horizon with at most one observation per target, not a single overflight. ZH.

---

## Minor cleanup (R3 8-item pass; fold into one edit)

- **R3-M3:** residual "five solvers" in §7.1 → "five configurations"; add hot-start cross-ref to the operational-sufficiency sentence.
- **R3-M4 (G4-adjacent):** §1 time-critical motivation needs a forward pointer to the timeliness Limitation.
- **R3-M5:** §7.2 guideline jumps from N≲100 to N≳300; add one sentence on the N=100-300 transition band (S7/S8 data: deficit 0% by N=150).
- **R3-M6:** move the 45° envelope caveat adjacent to (within 1-2 lines of) the G-SM dense recommendation, not 6 lines away.
- **R3-M7:** §3.3 note C3/C4 inactive more precisely (caps non-binding under all tested scenarios).
- **R3-M8:** §3.2/§3.3 one sentence confirming the C2 3-D angular-gap formula covers left↔right side-flip maneuvers.
- **R1-M3..M7 / R2-5minors / DA-5minors:** mostly subsumed by G1-G5; the only standalone worth doing is DA's note that variant-C inertness implies f2 acts approximately as a squint metric within-window (already explained in ablation text; optional one-clause strengthening).

---

## What this panel did NOT find

- No data-integrity, reproducibility, or constraint defects (pre-gate clean).
- No challenge to F4 matched-p control logic beyond the G3 wording nit; +7% f3 survives.
- No new CRITICAL from DA; the ten attack angles largely failed against the revised text (pixel-area ∝1/f2 verified to within a constant ~11% θ_elev/θ offset that cancels in ratios; r_null=-0.51 is an analytic integral but the envelope-vs-schedule empirical progression is the actual result; hot-start conditioning is now disclosed everywhere).
- No demand for new experiments, new baselines, or corpus reruns.
- EIC explicitly states a third full panel would have diminishing returns.

---

## Revision Roadmap

1. **G1** (knee disclosure): 5 claim sites in EN + ZH, ~20 min. Most important.
2. **G2** (terminology): 6 find-replace sites EN+ZH, ~10 min.
3. **G3-G5**: 3 one-clause edits EN+ZH, ~15 min.
4. **R3 minor pass**: 8 items, ~30 min.
5. Recompile EN pdflatex×2 + ZH xelatex×2; run verify (G1 adds no new ledged number, but confirm 167/0); rebuild submission zip.
6. Commit; submit.

**Estimated effort:** ~1.5 hours prose, no data runs. After this, stop reviewing and submit.

## Reports on disk
- review/panel_20260819_eic.md
- review/panel_20260819_r1_methodology.md
- review/panel_20260819_r2_domain.md
- review/panel_20260819_r3_perspective.md
- review/panel_20260819_r4_devils_advocate.md
