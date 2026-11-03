# R1 Methodology/Statistics Review — Panel 2 (2026-08-19)

**Reviewer:** Methodology & statistics
**Manuscript:** small-paper-ijae.tex (42 pp, post F1-F8 revisions, HEAD 125e132)
**Recommendation:** MINOR REVISION (rigor 84/100, up from 78)

## Summary

The F1-F8 revisions materially strengthen the statistical presentation. The matched-reference-point control (F4), knee-selector specification (F5), HV demotion (F7), and pixel-area derivation (F2) are all sound and correctly reported. No CRITICAL issues. Two residual MAJOR points concern the F4 control design logic and the sparse-regime knee sensitivity; the rest are MINOR.

---

## Findings

### M1. F4 matched-p control controls direction count, not reference-point count — logic slightly mis-stated (MAJOR)

§6.4 (lines 996-1001) and Limitations (lines 1381-1383) describe the p=4 rerun as "matched to MOEA-2's H=13." The numbers are H(2,12)=13 (MOEA-2) vs H(3,4)=15 (MOEA-3 p=4), which are close but not equal, and the two configurations differ in objective count (2 vs 3), not just reference-point density. The control actually tests *"does collapsing the 3-objective reference set from 91 to 15 directions change f3?"* — and it does not (0.702 vs 0.699, p=0.149). That is a valid and useful result: it shows f3 is not an artifact of the 7x reference-direction inflation. But it is **not** a matched comparison to MOEA-2: a genuinely matched design would compare MOEA-3-p4 to MOEA-2 with an equal-or-greater H (e.g. MOEA-2 at p≈39, H=40) holding pop/gen fixed, to show the +7% gap survives when MOEA-2 is given comparable reference density. The current control is one-directional (it only rules out "MOEA-3 f3 is high because H=91"), which is the more important confound but should be labeled honestly.

**Fix:** Reword "matched to MOEA-2's H=13" to "collapsing MOEA-3's reference set to H=15, comparable in magnitude to MOEA-2's H=13." The substantive claim survives; the overclaim of a two-sided match does not. Optionally note the symmetric control (MOEA-2 at matched H) as future work.

### M2. Sparse S1 knee sensitivity of 0.04-0.06 is ~1 SD — the +34% claim is selector-dependent (MAJOR)

§5.3 (lines 739-745) reports knee-vs-best-f1 class-mean differences of "about 0.04-0.06 in f2 and f3" at S1, described as "expected and intentional." But Table 1 reports MOEA-2 S1 f2 = 0.394±0.059; a 0.04-0.06 swing is 0.7-1.0 within-scenario SD. The +34% headline (0.394 vs 0.295) uses the knee. If the reported point were best-f1, the S1 f2 mean drops to ~0.332 (from the selector analysis), giving +12.5% over G-BL instead of +34%. The selector choice therefore changes the headline sparse-regime gain by a factor of ~2.7. The dense-regime claims are robust (Δ≤0.005), but the abstract's "+34% geometric quality" is not selector-invariant.

This is not a fatal flaw — the knee is a defensible, pre-specified representative point — but the manuscript should (a) state that the +34% is the knee value, and (b) give the best-f1-anchored sparse gain (or the range) so a reader can see the selector sensitivity at the claim site, not only in §5.3. Currently §6.1 (line 774) reports +34% without the qualifier.

**Fix:** Add "(at the knee point; best-f1 gives +12-13%)" or a footnote at the first +34% in §6.1/Abstract, or report the knee/best-f1 range. The dense numbers need no change.

### M3. Friedman still pools 3 single-point solvers — acceptable now but one sentence is off (MINOR)

§5.3 (lines 713-718) now correctly notes G-BL/GA-P-BL tie and that the statistic is "driven largely by within-scenario dispersion of the two multi-point NSGA-III solvers." But it still says the test is "across the five configurations × 200 scenarios" for overall differences; with two of five configs identical by construction and a third (G-SM) a single point, the Friedman null (all configs equal per scenario) is essentially a test of MOEA-2 vs MOEA-3 vs G-SM, not a 5-way test. The current caveat is adequate; just drop "five configurations" in favor of "the non-identical configurations" for precision. No reanalysis needed.

### M4. Wall-clock reports median but no IQR (MINOR)

Line 698 gives medians 22/66/220/260 s. The runtime distribution is right-skewed (NSGA-III on hard instances); a median without spread is acceptable for an order-of-magnitude note, and the text explicitly says "order-of-magnitude indications rather than a benchmark." No change required, but IQR or max would cost one line.

### M5. Pixel-area 25% derivation is correct but implicit (MINOR, verified)

Verified: ρ_rg = c/(2B sinθ), ρ_az = D/(2 cosψ_sq), so pixel area ∝ 1/(sinθ·cosψ) = 1/f2, and 1 − 0.295/0.394 = 25.1% ✓. §7.2 (the maritime sentence) states "pixel area scales as 1/f2" which is correct, but the derivation is not shown — a reader must trust it. One inline equation (area = ρ_rg ρ_az ∝ 1/f2) would make it self-contained. The f2 index uses θ_elev while ρ_rg uses target-side θ, but both orderings agree per §3.2, so the area proportionality holds to the ordering accuracy already disclosed. Not blocking.

### M6. N50 caution is now adequate (no action)

§6.3 CI [30,62] with "coarse indicator... not a precise threshold" language is appropriately hedged. Good.

### M7. Hot-start control sample still 10/4/5/5 (no action needed)

Unchanged from panel 1, already disclosed with the within-seed caveat (line 1164). The prose no longer overclaims monotonicity. Fine.

---

## What improved

- HV demotion to secondary with the G-SM 0.2341 inversion surfaced in §5.3 is the right call; the per-objective + Cliff δ primary framing is statistically coherent.
- Knee selector is now specified (min-max normalized sum argmax) and sensitivity is measured from frontier data rather than asserted.
- Matched-p result f3=0.702 (p4) vs 0.699 (p12), paired p=0.149 is correctly reported as "statistically indistinguishable" and the Limitations entanglement note is converted to a positive result.
- pymoo 0.6.1.6 stated.
- The 167-assertion verify gate (incl. the new p4 and pixel-area checks) is good reproducibility hygiene.

## Verdict

MINOR REVISION. M1 (reword the match claim) and M2 (qualify +34% with selector sensitivity at the claim site) are the only items requiring prose changes; both are localized. Rigor 84/100.
