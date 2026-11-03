# R2 — SAR Physics & Domain Review (Panel 2026-08-19, after F1-F8)

**Reviewer:** SAR remote-sensing physics + agile EO scheduling domain
**Manuscript:** small-paper-ijae.tex (42 pp), sections/_ablation_section.tex, small-paper-ijae.bib
**Target:** Advances in Space Research
**Data pre-gate:** PASSED (167/0, 1800 sol OOW/C1-C4=0, 76190 windows clean). No data-integrity findings.

## Verdict: MINOR REVISION (domain score 80/100, up from 78)

No CRITICAL. The F6/F8 caveats and cross-track correction are substantive improvements; NESZ approximation, G-SM proxy, and scope are now adequately disclosed. Two framing/terminology issues remain that an ASR domain reader will notice.

---

## Resolved by F1-F8 (verified)

- **F6 45° envelope caveat:** now present in both C1 (lines 479-483) and §7.2 (lines 1311-1314). Adequate.
- **F8 f3 cross-window caveat:** lines 285-291 correctly state within-window θ_elev varies ~1.5° while sinθ spans 2.4× across 18-47°, and label f3 a geometry proxy. Adequate.
- **Cross-track geometry (lines 662-665):** "ground central angle of about ±5.5°, corresponding to the 47° incidence limit." Verified against code (generate_s5_scenarios.py:83-84: η_max=41.27°, swath_half=h·tanη=608 km, swath_half_deg=608/111.32=5.46°). Internally consistent. The true spherical central angle is γ=θ−η=5.72°; "about ±5.5°" covers the 0.26° gap. OK.
- **Moreira2026:** citekey and bib year now agree (bib year=2026, Proc. IEEE 114(2):183-219, DOI 10.1109/jproc.2025.3621586). Correct — that DOI/volume corresponds to a 2026 issue.
- **f3 double-counting check:** cos³ξ = cos³θ_elev·cos³ψ_sq is the correct decomposition of full off-nadir (cosξ=cosθ_elev·cosψ_sq), not double-counting. The shared cosψ_sq in f2/f3 is the geometric coupling the paper analyzes. No defect.

---

## MAJOR

### M1. Abstract reports sparse-regime gains without the 45°-envelope caveat

The abstract (lines 41-46) leads with "+34% f2 at 14% coverage cost" and "+41% f3 at 15% cost" and "matching G-SM's +45%," but says nothing about the 45° squint envelope that the body (lines 479-483, 1311-1314) states "deliberately exceeds typical operational agility" of "a few degrees." A reader of the abstract alone would take these gains as operationally available. The body is now well-caveated; the abstract is not.

**Fix (one sentence, abstract):** after "under a generous agility assumption" or qualify "under the tested 45° squint envelope." E.g. append to line 46: "(these sparse-regime gains are quantified under a 45° squint envelope that exceeds typical operational agility; §3.3)." This is the same envelope qualification already in the body.

### M2. "Single-pass" terminology collides with SAR convention

Title, abstract, and scope repeatedly say "single-pass ... Stripmap" (lines 38, 150, 1289, 1402, etc.). In SAR, "single-pass" conventionally means one satellite overflight (one imaging pass). But here visibility windows propagate over **two orbital periods (~200 min)** (line 687), and targets are distributed ±608 km cross-track — far wider than any C-band Stripmap imaging swath (~40-80 km). The schedule therefore spans multiple overflights; "single-pass" means one observation per target (as opposed to multi-pass stacking/InSAR), not one overflight.

An ASR SAR reader will initially read "single-pass Stripmap" as "one overflight, Stripmap swath," which contradicts the 1216 km accessible band and 200-min window. The ambiguity matters because the operational recommendation and "single-pass, single-satellite" scope restriction (lines 1347-1353) hinge on it.

**Fix:** define "single-pass" at first use in §1 or §3.3: e.g. "single-pass (one observation per target, over a two-orbit scheduling horizon; not a single satellite overflight)." Alternatively use "single-observation" throughout and reserve "pass" for an overflight. At minimum one clarifying sentence.

---

## MINOR

### m1. Residual "coverage ceiling" wording
Three uses survive in the hot-start control and Limitations (lines 1150 "coverage-ceiling claim," 1160 "coverage ceiling is thus a G-BL initialization effect," 1364 "coverage-ceiling result"). F1 replaced "ceiling" with "reference" at claim sites; these residual uses are acceptable because they *critique* the claim rather than assert it, but for full consistency either quote-mark them ("'coverage ceiling' claim") or switch to "coverage-reference claim." One-line sweep.

### m2. f3 cross-window caveat could state the optimization implication
Lines 285-291 say f3 is a "geometry proxy ... across widely separated incidence angles." But the MOEA *selects across windows/targets* spanning the full 18-47° range in sparse regimes. Add one clause: because f3 rewards low incidence (cos³ξ) without the sinθ ground-area factor, cross-window f3-driven selection favors low-incidence views more than an absolute NESZ metric would; results are interpreted as relative geometry, consistent with the G-SM squint-proxy agreement (δ=+0.99). This heads off the "is the MOEA chasing a mis-ordered signal" question.

### m3. Platform abstraction vs Sentinel-1 class (carried from prior round)
D=12.3 m, B=56.5 MHz C-band (lines 655-656) is Sentinel-1-class, but Sentinel-1 is non-agile and its Stripmap mode is deprecated. The paper calls this a "generic C-band Stripmap SAR with bilateral-looking capability" (line 652), which is an abstraction, not a real platform. That's defensible for a scheduling study, but one sentence noting the instrument parameters are a composite abstraction (not a specific flown agile SAR) would preempt a domain reviewer's "no such platform" objection.

### m4. ±608 km "observation band" vs imaging swath
Line 663 "accessible observation band" is a good replacement for "swath," but a reader may still infer the radar images 1216 km cross-track. Consider "target-distribution band" or "accessibility band over the scheduling horizon" to make clear this is where candidate targets are placed (over two orbits), not the instantaneous Stripmap swath. (Tied to M2.)

### m5. G-SM δ=+0.99 is near-mechanical
Line 572/868: Cliff δ=+0.99 between G-SM squint minimization and f3 is expected because f3 ≈ cos³ξ and squint minimization directly drives cosψ_sq; under the 45° envelope this is a near-ceiling correlation. The paper reports it as a finding; one clause noting it is a structural proxy correlation (not independent validation) would be precise. Not blocking.

---

## What is sound (do not change)

- NESZ ∝ R³ and cos³ξ relative-index framing with explicit 17%/5% error and sinθ omission disclosed.
- r_null/envelope/schedule decomposition (-0.51/-0.97/-0.63) — the paper's durable contribution, domain-correct.
- Matched-reference-point control (p=4/H=15, f3=0.702 vs p=12 0.699) — cleanly disentangles H=91 artifact.
- Knee selector specification and verified sensitivity.
- C3/C4 correctly flagged non-binding; C2 as dominant dense-regime constraint is physically right.
- Ablation variant-C inertness (θ_elev ~1.5° within-window) consistent with geometry.

## Recommendation

Minor Revision. M1 (abstract envelope qualifier) and M2 (define "single-pass") are the only must-fixes; m1-m5 are wording tightenings. No new experiments, no domain defect in the physics or data.
