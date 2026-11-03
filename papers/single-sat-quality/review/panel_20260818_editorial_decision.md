# Editorial Decision — Pre-Submission ARS Panel (2026-08-18)

**Manuscript:** "Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite: Balancing Profit, NESZ, and Geometric Resolution" (small-paper-ijae.tex, EN)
**Target:** Advances in Space Research (Elsevier)
**Panel:** EIC + R1 (methodology/statistics) + R2 (SAR/domain) + R3 (cross-domain/operations) + Devil's Advocate. Independent, read-only.
**Data pre-gate:** PASSED (verify 165/0, CALIBER OK at 3372e2e; 1800 solutions OOW/C1-C4=0; cross_solver/gapbl/moea_live/window_c1 all 0). No data-integrity findings.
**Prior round:** ARS Accept 2026-08-17 (R1-R18 closed); this is an extra pre-submission pass after CRediT/tolerance commits.

---

## Decision: MINOR REVISION

No CRITICAL findings from any seat; Devil's Advocate explicitly records 0 CRITICAL, so the IRON RULE bar to Accept is not tripped. The five seats converge, however, on a set of framing/specification defects in how the headline claims are stated relative to the (sound) data. All are fixable with prose changes and one optional small control run; no experiment requires rerunning the 1800-solution corpus.

**Score consensus:** rigor 78-80, originality 68, significance 62-65, clarity 82, reproducibility 90, journal fit 78, data soundness 90.

The paper's strongest asset — flagged independently by R3 and the Devil's Advocate — is the envelope-null-schedule decomposition (r_null = -0.51; envelope corr -0.97 vs schedule -0.63 -> -0.15). This anchor-independent geometric result is more defensible than the "saturation boundary" headline and should be promoted to co-headline status.

---

## Required Revisions (consensus MAJOR, >=2 reviewers each except where noted)

### F1. Downgrade "boundary / ceiling" language to qualified regime [EIC, R1-M3, R3-M3/M4, DA-M1]
The phrases "empirical saturation boundary," "coverage ceiling," and "greedy methods attain the tested family's coverage ceiling" overstate what the data support:
- N50 ~ 50 has bootstrap CI [30,62] from six density points, four censored at <=1% (manuscript already discloses this).
- One sparse scenario reaches f1*=1.108 (+10.8% over G-BL), so G-BL is a near-optimal reference, not a strict ceiling.
- True Pareto fronts are unknown (intractable N>=20); fronts are best-known NSGA-III approximations.
- The convergence is conditional on G-BL hot-start (random-init deficits 0.39-0.68).

**Fix:** Replace "boundary" with "transition" / "regime for G-BL-seeded NSGA-III under the tested configuration." Replace "coverage ceiling" with "coverage reference." State the conditioning conjunction (hot-start + best-known fronts + single-pass/single-sat/Stripmap) at every claim site (Abstract, Sec 1 contributions, Sec 7.1, Sec 8), not only in Limitations. Resurface hot-start dependence in the Conclusion, not just the Abstract.

### F2. Correct the 0.3 m resolution number in Sec 7.2 [R3-M1, single-reviewer but concrete numerical error]
Lines 1247-1249: "few-percent resolution improvement (~0.3 m at C-band: rho_rg ~ 5.3 m at theta=30deg)." The 5.3 m baseline is arithmetically correct (c/(2B sin theta) = 3e8/(2*56.5e6*0.5) = 5.31 m). But +34% in f2 maps to roughly a 25% reduction in pixel AREA (since pixel area ~ 1/f2), i.e. ~0.7 m linear, not 0.3 m; and 0.3/5.3 = 5.7% does not match the S1 gain.

**Fix:** Either derive the number correctly from f2 (state the f2-to-meters mapping and the incidence angle assumed) or remove the specific meter figure and keep the qualitative statement. Verify against Table 1 numbers; this is exactly the class of hardcoded-prose number the verify gate does not currently anchor.

### F3. Relabel GA-P-BL as a control, not a fifth solver [EIC, R1, DA-C4; R2 minor]
GA-P-BL output is numerically identical to G-BL by construction (never-worse-than-baseline guard). Calling it one of "five solvers" inflates the comparison set and the Friedman denominator. The manuscript already notes the tie; make it systematic.

**Fix:** In Table 1 caption, Sec 4.1, Sec 5.3, Sec 7.1, and Abstract: describe the comparison as "two greedy heuristics, one single-objective GA control (numerically identical to G-BL), and two NSGA-III variants." Note the Friedman statistic is conservative toward fewer distinct rankings (already stated at line 1220; keep).

### F4. Resolve the H=13 vs H=91 reference-point confound for +7% f3 [R1-M1, DA-C1/M2]
MOEA-3 uses H=91 Das-Dennis reference directions vs MOEA-2 H=13 (p=12). The 7x jump in reference-direction density is entangled with the third objective's marginal value; the S1 "+7% f3" claim (0.699 vs 0.654, p=5.5e-13, delta=0.88) is the ONLY density where f3 differentiates, and it may be partly a search-coverage artifact. The manuscript notes this in Limitations but not at the claim site.

**Fix (pick one):**
(a) **Preferred:** a matched-reference-point control on the S1 seeds — rerun MOEA-3 with p~4 (H=15) or MOEA-2 with p~41 (H~861, impractical; prefer MOEA-3 p~4), 50 scenarios, and report whether +7% holds. This is a small, bounded run.
(b) If the control is not run, relabel every "+7% f3" / "third objective contributes" claim as "under the H=91 reference-point configuration" and state explicitly that the third objective's marginal value is not yet disentangled from reference-direction density. The Limitations note must move to the claim site.
The abstract "+41% over G-BL" is unconfounded (it compares MOEA-3 to G-BL, not MOEA-3 to MOEA-2) and may stand.

### F5. Specify the MOEA front-point selector for Table 1 [R1-M2]
Table 1 reports single mean f2/f3 per solver per class, but each MOEA front contains 6.8 +/- 2.1 (MOEA-2, S1) to 33.8 +/- 8.4 (MOEA-3, S1) non-dominated points. It is unspecified which point represents a scenario: knee, best-f1, best-f2, median-front, etc. The means are not reproducible without this.

**Fix:** State the selector (e.g., "knee solution selected by [method]") in Sec 5.3 or 4.4, and add a one-paragraph sensitivity check that Table 1 means are stable to (say) best-f1 vs knee vs median-front (if they are; if not, report the range).

### F6. Condition the dense-regime G-SM recommendation on the squint envelope [R2-M1]
Sec 7.2 recommends G-SM for radiometric priority at N>=300, citing +16% f3 at S4. But G-SM exploits the 45 degree squint envelope, which the manuscript itself states "deliberately exceeds typical operational agility" (real platforms slew a few degrees). The +16% is therefore envelope-headroom, not an operational guarantee.

**Fix:** Add a clause to Sec 7.2 and the Conclusion: the G-SM radiometric advantage is quantified under the 45 degree capability-superset envelope; on operationally realistic low-squint platforms the margin shrinks and should be re-quantified. Do not present G-SM as a drop-in operational recommendation without this.

### F7. Demote HV from "primary indicator" given the G-SM inversion [R1 minor, DA-M3]
Sec 5.3 names HV the primary quality indicator, but the manuscript itself shows G-SM single-point HV=0.2341 would beat MOEA-3 (0.0893) if included, and excludes G-SM from Table 3 for that reason. Using a metric you demonstrate is confounded, as primary, undercuts the statistical narrative.

**Fix:** Name per-objective comparisons + Cliff's delta as primary; HV as a secondary, explicitly-cardinality-confounded diagnostic. Move the G-SM HV number into the main text (it is currently buried at line 963) so the reader sees the inversion before Table 3. Keep the Friedman test but state it is driven by NSGA-III dispersion (already at line 1222).

### F8. Tighten the f3 sin(theta) omission caveat for cross-window selection [R2-M3]
f3 = cos^3 xi omits the sin(theta) ground-area factor in standard NESZ. The "relative ordering index" defense is sound for within-window timing (theta varies ~1.5 deg per the variant-C discussion), but sin(theta) spans 0.31 (18deg) to 0.73 (47deg) across the incidence range, so across-window or across-target ordering could shift. The manuscript discloses the omission but not this cross-window implication.

**Fix:** Add one sentence in Sec 2.2 or 3.2: the ordering-index claim holds within a window; cross-target comparisons that span wide incidence ranges should be read as geometry-proxy rather than absolute NESZ ranking. No rerun required.

---

## Single-Reviewer MAJORs (adjudicated)

- **R2-M2 (G-SM f3=0.722 > MOEA-3 0.699 at S1):** Partially valid. The Abstract already states MOEA-3 "matches G-SM's +45% at S1 while retaining roughly twice the coverage (85% vs 44%)." The claim is the coverage-quality PARETO position, not max f3, and this is stated. **Action:** add one clause making explicit that MOEA-3 does not maximize raw f3 at S1 (G-SM does, at lower coverage), so the "+41% over G-BL" is not a claim of best-in-class f3. MINOR.
- **R3-M2 (timeliness motivation / no timeliness objective):** Valid scoping gap. The disaster/maritime motivation motivates timeliness but timeliness is not an objective. **Action:** either soften the motivation language in Sec 1 or add a one-paragraph diagnostic (e.g., mean time-to-acquire for G-BL vs MOEA) in Sec 6. The manuscript's Limitations already acknowledges this indirectly. MINOR-to-MAJOR; recommend the softening as it is cheaper.
- **R3-M5 (C3/C4 never bind):** Valid. Calling the formulation "four-constraint" when two are deliberately non-binding misleads. **Action:** reclassify C3/C4 as "retained for completeness, inactive under all tested scenarios" in Sec 3.3 and any later claim of a four-constraint model. MINOR.
- **R1-M4 (hot-start sample imbalance 10/4/5/5; S3 peak non-monotone):** Valid. The deficit magnitudes are indicative, not precise bounds; the manuscript already says so (lines 1106-1113). **Action:** add bootstrap CI to the reported deficits, or explicitly state no monotone trend is claimed. MINOR.
- **DA-C5 (best-known fronts vs true Pareto):** Already disclosed at lines 1072-1075 and Limitations. **Action:** cross-reference the caveat at the first "redundant" claim site in Abstract/Conclusion. MINOR.
- **DA-C3 (N50 only two informative points):** Already disclosed; F1 subsumes. No separate action.

---

## MINOR findings (deduplicated across seats)

1. Variant-C "theta_elev varies ~1.5 degrees within window" (ablation line 118) is asserted, not measured — cite the computed value or a script. [R1]
2. Random-search n=5 is a sanity check, not a "calibration" — relabel in Sec 6.6. [R1]
3. NSGA-III implementation/library and version not named — add to Sec 5.2 or reproducibility statement. [R1, R2]
4. No wall-clock reported; operators care about latency. One sentence with order-of-magnitude per density is enough (claim is quality not efficiency, so not a full benchmark). [R1, R3]
5. Transferability paragraph (Sec 7.3) is thin for a cross-domain claim — either expand to 2-3 sentences with the optical/IR mapping or trim the claim. [R3]
6. Bilateral left->right side flip under C2 transition time not explicitly checked (a large angular maneuver may be physically required between consecutive opposite-side observations). One sentence confirming C2 covers this, or a note. [R3]
7. R2 domain notes: 1200 km swath width is wide for Stripmap (verify against instrument params); fixed 30 s dwell implies ~225 km along-track at 693 km — state whether intentional; D=12.3 m/B=56.5 MHz is Sentinel-1-class but Sentinel-1 is non-agile — clarify the "generic C-band" abstraction; check Moreira2025 bibliographic year. [R2]
8. Unweighted mean f2/f3 vs priority-weighted quality: state explicitly that quality is per-task-averaged and not weighted by p_i (already in Sec 3.2, but make it salient in Sec 5.3). [R3]
9. "Five solvers" / "superior solver" phrasing throughout — harmonize with F3. [all]
10. S7/S8 used only for scale-sensitivity, not pooled five-solver comparisons — make this exclusion more prominent at first mention (currently Sec 5.1). [R3]
11. Hot-start perturbation sigma=0.5 applied to a [0,1] chromosome can push values outside range; clarify clipping/bound handling in Sec 4.3-4.4. [R1 implicit]
12. CRediT already lists Visualization (commit 3372e2e); AI disclosure is 5 lines and within policy. No action. [EIC]

---

## What this panel did NOT find

- No data-integrity, constraint-violation, or reproducibility defects (pre-gate PASSED; data audits all zero).
- No challenge to the core geometric-coupling mechanism (r_null decomposition, envelope vs schedule correlation progression -0.97 -> -0.63 -> -0.15). Every seat treated this as the paper's durable contribution.
- No challenge to the SAR first-principles formulas themselves; the approximation caveats are disclosed. The R2 concerns are about the SCOPE of the ordering-index defense, not its correctness.
- No demand for new baselines (MOEA/D, SMS-EMOA, learning-based) beyond what Limitations already scopes out.
- No challenge to the statistical test choices (Friedman + Wilcoxon + Bonferroni + Cliff delta); the concerns are about WHAT is fed to them (single-point vs multi-point HV; reference-point asymmetry).

---

## Revision Roadmap (recommended order)

1. **F1 + F3 + F7** (framing pass, one edit session): replace boundary/ceiling, relabel GA-P-BL control, demote HV. Touches Abstract, Sec 1 contributions, Sec 5.3, Sec 7.1-7.2, Sec 8. EN + ZH mirror.
2. **F2** (0.3 m number): derive or remove; hard-numeric prose error. Verify with a script and consider adding it to the verify_paper_numbers ledger.
3. **F4** (reference-point confound): decide (a) matched-p control run on S1 or (b) relabel. Option (a) is a bounded ~50-scenario MOEA-3 run at p=4; recommended because it converts a flagged limitation into a result. If run, results feed Sec 6.4 and Abstract.
4. **F5** (selector spec): inspect runner code, state selector, add sensitivity sentence.
5. **F6 + F8** (envelope conditioning + sin theta caveat): prose, Sec 2.2/3.2/7.2.
6. **R3-M2/M5 + minors**: one cleanup pass.
7. Recompile EN (pdflatex x2) + ZH (xelatex x2), rerun verify_paper_numbers (F2 may change a ledged number; F4 option (a) will change several), rebuild snapshot + audits if any data changed, then submission.

**Estimated effort:** 1-2 days prose-only without F4(a); 2-3 days with the matched-p control. No corpus-scale rerun.

---

## Reviewer reports (on disk)

- `review/panel_20260818_eic.md` — EIC
- `review/panel_20260818_r1_methodology.md` — methodology/statistics
- `review/panel_20260818_r2_domain.md` — SAR/domain
- `review/panel_20260818_r3_perspective.md` — cross-domain/operations
- `review/panel_20260818_r4_devils_advocate.md` — Devil's Advocate
