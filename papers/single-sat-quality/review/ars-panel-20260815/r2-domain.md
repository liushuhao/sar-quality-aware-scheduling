# Peer Review Report

## Manuscript Information
- **Title**: Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite: Balancing Profit, NESZ, and Geometric Resolution
- **Journal**: Advances in Space Research
- **Review Date**: 2026-08-15
- **Review Round**: Round 1

---

## Reviewer Information

### Reviewer Role
Peer Reviewer 2 (Domain)

### Reviewer Identity
Independent domain reviewer — remote-sensing/SAR task scheduling researcher (agile Earth-observation scheduling, SAR mission performance modelling, multi-objective optimization applied to satellite scheduling).

### Review Focus
(1) Physical fidelity of the NESZ/resolution/squint objective models and of the geometry-to-quality mapping; (2) coverage and correct citation of the agile-EOS scheduling and SAR-scheduling literature; (3) whether the "third objective redundant vs. density-dependent" resolution is convincingly argued; (4) realism of the operating assumptions (Stripmap, single satellite, squint envelope, scenario design); (5) physical soundness of the §6.4 correlation findings and their interpretation.

---

## Overall Assessment

### Recommendation
Major Revision

### Confidence Score
4 — Mostly within my area of expertise (SAR signal/geometry modelling, EOS scheduling, MOEA application); high confidence in the figure/statistics verifications performed against the repository data.

### Summary Assessment
The paper embeds two physics-derived quality objectives (geometric resolution index f2 = sinθelev·cosψ, NESZ radiometric index f3 = cos³ξ) into NSGA-III-based scheduling and reports a density-dependent saturation of the multi-objective advantage (N ≈ 20–100 transition, negligible beyond N ≈ 150–300), conditional on greedy hot-start initialization. As domain reviewer I verified the physical core: the NESZ ∝ R³ scaling, the exact LVLH identity cosξ = cosθelev·cosψ, the f2–f3 null correlation r_null = −0.51 (Monte Carlo re-check: −0.511), and the θ-only/ψ-only limits (±0.997) are all correct, and the §2.2 simplification disclosures (plane-Earth range, suppressed sinθ factor, pattern roll-off) are honest and quantitatively bounded. I also recomputed the headline tables from the repository data and found Table 2, Table 4 (ablation), and most stated percentages consistent. However, the manuscript in its current form misrepresents its own ablation and effect-size evidence: Fig. 6's axes (±4%) cannot contain the −18%/+25% S1 variant-D values reported in Table 4 (verified against the same _progress.json), and §6.2's Cliff's δ = +0.88 for the G-SM f3 effect contradicts §4.3's +1.0 and a direct recomputation (δ = 0.99, 199/200 scenarios). The squint envelope (|ψ| ≤ 45°, scheduled means 16–24°) also sits in tension with the paper's own claim that real platforms slew "only a few degrees," conditioning the operational reading of the headline gains. These are repairable but substantive, hence Major Revision.

---

## Strengths

### S1: Physically sound and honestly calibrated SAR quality models
The objective decomposition is defensible: NESZ ∝ R³ for Stripmap after azimuth compression gain (§2.2), ρ_rg ∝ 1/sinθ and ρ_az ∝ 1/cosψ are standard textbook forms, and the "no double counting" choice f3 = cos³ξ with the exact identity cosξ = cosθelev·cosψ is mathematically consistent (verified in code, `src/sar_sim/metrics/nesz.py`). The two-objective optima genuinely conflict (f2 favours higher incidence, f3 favours the zero-Doppler point), a real and correctly stated physical mechanism. The simplifications are disclosed with magnitude bounds ("overestimates slant range by roughly 5% and R³ by roughly 17%" at the 47° edge) and explicitly demoted to a relative-ordering index.
**Evidence Anchor**: [`equation: Eq. (9) r_null = −0.51 (recomputed −0.5110 by Monte Carlo, N=2×10⁵); §2.2 plane-Earth disclosure`]

### S2: The trade-space analysis is physically structured, not statistical folklore
The separation of the *definitional* null correlation (−0.51 under independent θ/ψ) from the *geometric envelope* correlation (−0.97, from real LOS kinematics coupling θ and ψ) from the *solver-selected schedule* correlation (−0.63 to −0.15) is a genuinely informative decomposition, and the θ-only (−0.997) and ψ-only (+0.997) limits are not mathematical identities but physically meaningful regime boundaries (verified by Monte Carlo). The claim that lower-squint convergence attenuates, but does not eliminate, the incidence-angle conflict is faithful to the reported numbers.
**Evidence Anchor**: [`text: §6.4 "all solvers select geometries shifted toward lower squint than the visibility envelope"`]

### S3: Up-to-date and appropriately focused related-work coverage
The related-work section integrates the current agile-EOS line (Ferrari 2025 survey; 2024–2026 DRL, Lagrangian, CP, GNN-MCTS, whale-optimization contributions), the SAR-specific scheduling line (Chang 2022 Gaofen NSGA-II/III with ALNS; Wei 2025 neural-policy; Yao 2024 bilevel; Chang/Zhou 2025 memetic; Kramer & Miller 2024/2025), and the classical foundations (Lemaître 2002, Bianchessi 2007, Curlander 1991, Cumming 2005, Deb 2014). The "quality as fixed attribute vs. quality as continuous function of acquisition time" contrast that frames the research gap is well drawn and, to my knowledge, accurate: no cited prior work treats decomposed, physics-derived quality functions as primary scheduling objectives.
**Evidence Anchor**: [`text: §2.1 "the closest approaches embed aggregated quality proxies rather than separate geometric and radiometric objectives"`]

### S4: Experiment design enables the scale-dependence claim
The four density classes plus two intermediate classes (S7/S8, N = 150/200) dedicated to the transition, the logistic-fit midpoint with honest bootstrap CI ([30,62], explicitly "not a precise threshold"), the scenario variants modulating geometry rather than only distribution (S1-D single revolution, S2-E high latitude, S4-D narrowed incidence ceiling), and the four robustness controls (hot-start dependence, perturbation sweep, random search, random-init variant-D) constitute a careful, falsifiable design.
**Evidence Anchor**: [`table: Table 3 scale-sensitivity — S1 78% to S4 0% of scenarios below f1* = 0.95`]

### S5: No overclaiming
The manuscript repeatedly declines to name a superior solver, frames the results as an "empirical saturation boundary," and conditions coverage convergence on hot-start initialization — including in the abstract and conclusion. This is the correct epistemological posture for a negative/saturation finding of this type.
**Evidence Anchor**: [`text: Abstract "Rather than identifying a superior solver, our results establish an empirical saturation boundary"`]

---

## Weaknesses

### W1: Fig. 6 contradicts Table 4 on the ablation magnitudes — the key ablation figure misrepresents the study's largest effects
**Problem**: The ablation figure (fig5_ablation.pdf, included via `\includegraphics{fig5_ablation.pdf}`, §6.5) has y-axes spanning only ±0.04 (±4%) on all three panels (verified by extracting the PDF's tick labels). Table 4 reports S1 variant D at Δf1* = −18.0% and post-hoc f3 degradation of −24.9% (A 0.698 vs. D 0.525), and S1 variant B at +17.8% f3. I recomputed these values from the actual results (`experiments/results/moea_3obj_no_physics/_progress.json` etc. via `compare_variants()`): S1-D f1 = −18.04%, f2 = +19.84%, f3 = +24.87%; S1-B f3 = +17.84%. The figure therefore cannot depict the table's values: the shipped artifact was generated from different (stale) data or with clipping, and the caption ("Bars show degradation relative to the full-physics baseline A") claims a correspondence to Table 4 that does not hold.
**Evidence Anchor**: [`figure: Fig. 6 all panels — y-axis ±0.04 vs. Table 4 S1-D Δf1* = −18.0% (data: −18.04%)`]
**Why it matters**: The variant-D S1 contrast (coverage +3.9 tasks, radiometric −25%) is the single largest physical-objective effect in the study and the basis of the "physics objectives add value in the sparse regime" conclusion. A reader relying on the figure sees that no ablation effect exceeds ~4% anywhere, which is the opposite of the text's claim, eroding confidence in the entire ablation evidence chain.
**Suggestion**: Regenerate Fig. 6 from the current `_progress.json` snapshots (e.g., `experiments/gen_ablation_figure.py` with auto-scaled or per-panel axes), verify bar values against Table 4 programmatically, and state the data provenance in the caption.
**Severity**: Major
**Confidence**: 5 — direct arithmetic verification against repository data

### W2: Internal contradiction on the G-SM f3 effect size, and the §6.2 value disagrees with the data
**Problem**: §4.3 cites "Cliff's δ = +1.0, §6.2" for squint-minimization's effect on f3, while §6.2 itself reports "Cliff's δ = +0.88, p ≈ 1.5×10−34". Recomputation from `results/baselines_200.json` (per-scenario f3, G-SM vs. G-BL, all 200 scenarios) gives δ = 0.990 (G-SM higher in 199 of 200 scenarios, ties 0) — consistent with +1.0 only under rounding, and inconsistent with 0.88. The same computation for f1* gives δ = −1.000, matching §6.2. These are the same pair of solvers, same scenarios; the two sections cannot both be right, and neither states the value the data support.
**Evidence Anchor**: [`text: §6.2 "large positive effect on f3 (Cliff's δ = +0.88"`]
**Why it matters**: The f3 effect size is finding (3)'s headline statistic and is cross-referenced from §4.3; a self-contradictory, data-mismatched statistic invites doubts about the whole reported statistical layer (and the paper's own "verify" culture elsewhere).
**Suggestion**: Recompute all reported Cliff's δ values from the final snapshots in one place, correct §6.2 (δ ≈ 0.99) and §4.3's pointer, and run a scripted cross-check of every reported statistic (δ, p, means) against the shipped data, as the pre-gate verify scripts already do for other numbers.
**Severity**: Minor
**Confidence**: 5 — direct recomputation from shipped data

### W3: Squint-agility envelope vs. platform realism — operational reading outruns the modeled platform
**Problem**: The model admits |ψ_sq| ≤ 45° (C1) and schedules mean |ψ| = 16–24° with 90th percentile 32–39° (§2.2), while §3.3 simultaneously asserts "real agile SAR platforms typically slew only a few degrees." For Stripmap SAR, sustained along-track squints of 30–40° are outside the operational envelope of essentially all current spaceborne systems (Sentinel-1 images at zero Doppler; agile X-band systems are limited in squint agility), and at such squints the simple stripmap resolution/NESZ scalings (ρ_az = D/2cosψ, NESZ ∝ R³) become more approximate (range-walk, Doppler-centroid and PRF constraints are not modeled). The headline sparse-regime gains (MOEA-2 +34% f2, MOEA-3 +41% f3, G-SM +45% f3 at S1) exploit this envelope freedom, and the §7.2 operational recommendation ("G-SM for radiometric priority") presupposes that squinted acquisitions are feasible for the target platform. Calling the 45° envelope "conservative" is only true relative to platform squint capability — relative to achievable scheduling gains it is optimistic, and the paper's own "few degrees" remark concedes as much.
**Evidence Anchor**: [`text: §3.3 C1 "real agile SAR platforms typically slew only a few degrees"`]
**Why it matters**: The sparse-regime magnitudes are the paper's quantitative face to mission planners; if a real platform's squint reach is a few degrees, those gains (and the G-SM regime itself, §6.2) shrink or vanish, while the dense-regime saturation finding is robust either way. The paper should state which platform class the envelope targets and bound the sensitivity.
**Suggestion**: (a) Anchor the envelope to an explicit platform class or defend it as an idealized sensitivity envelope for a generic agile SAR; (b) add a cheap sensitivity experiment — rerun MOEA-2/MOEA-3/G-SM on S1–S2 with ψ_max ∈ {10°, 25°} (the pipeline exists); (c) if the envelope stands, soften "conservative" to "capability-superset" and explicitly condition the operational paragraph on squint agility.
**Severity**: Major
**Confidence**: 4 — strong SAR-systems domain background; exact squint limits of specific commercial platforms are not public

### W4: Text/table inconsistencies in the scale-sensitivity reporting
**Problem**: §6.3 states the deficit proportion (f1* < 0.95) "collapses from 78% (S1) to 6% (S2)"; Table 3 reports 10% for S2, and recomputation from `moea_2obj/_progress.json` gives 80% (S1) and 10% (S2) — the text's 78%/6% matches neither the table nor the data. Separately, the logistic transition midpoint is reported as N50 ≈ 50 with CI [30, 62] in §6.3 but as "logistic midpoint N50 ≈ 45" in §7.2.
**Evidence Anchor**: [`text: §6.3 "collapses from 78% (S1) to 6% (S2) and to 0%"`]
**Why it matters**: The reader cannot reconcile the prose, the table, and the data; both numbers (6% vs. 10%; 50 vs. 45) appear in claims the paper itself flags as load-bearing ("transition confined to N ∈ [20, 100]").
**Suggestion**: Align §6.3 prose with Table 3 (10%) and the data-derived 80%/10%, and use a single N50 value (or state explicitly in §7.2 that 45 is the re-fit value with the same CI).
**Severity**: Minor
**Confidence**: 5 — direct recomputation

### W5: The third-objective marginal value (+7% f3 at S1) is asserted without a reported test, and is entangled with a disclosed design confound
**Problem**: The "density-dependent, not redundant" resolution rests on MOEA-3 vs. MOEA-2 f3 separation at S1 (0.699 vs. 0.654, +7%). No paired test or effect size for this specific contrast is reported (the pooled-HV Wilcoxon δ = −0.55 is explicitly point-count-confounded), and the Limitations concede the H = 91 vs. H = 13 reference-point asymmetry "partly entangles" the sparse-regime third-objective advantage. Meanwhile variant C (incidence removed) is numerically inert at every density, and variant B's effect is f3-only at S1 — so the "value of the third objective" reduces to the squint channel at one density class.
**Evidence Anchor**: [`text: §6.4 "at S1 the physics-aware solver attains f3 = 0.699±0.037 versus 0.654±0.038 for MOEA-2 (+7%)"`]
**Why it matters**: The abstract's headline framing ("MOEA-3 lifts radiometric quality by +41%") is easily read as the marginal value of adding f3; the actual marginal value is +7% at S1 only, unsupported by a direct test as it stands. The retention-vs-redundancy debate (panel focus) is resolved *directionally* but not *quantitatively*.
**Suggestion**: Report a paired Wilcoxon + Cliff's δ on f3 (and f2) at S1 specifically for MOEA-3 vs. MOEA-2; if significant, restate the claim with the effect size; optionally add a control matching reference-direction counts (e.g., H = 91 for MOEA-2 with a two-objective Das–Dennis grid or run MOEA-2 with H = 91 divisions on the f1–f2 plane) to de-confound reference density.
**Severity**: Major
**Confidence**: 4 — statistical practice within expertise; H-confound assessment from the manuscript's own disclosure

### W6: f2's incidence term uses the satellite-centered cross-track-plane angle, conflated with the target-incidence θ of the canonical resolution formula
**Problem**: §2.2 defines ρ_rg = c/(2B sinθ) with θ the target-centered, Earth-curvature-corrected incidence angle, and §3.2's f2 = Σ sinθelev·cosψ is justified as the inverse of ground pixel area. But θelev, defined via cosθelev = cosξ/cosψ, is the cross-track-plane projection of the LOS measured at the satellite (an angle between ξ and the curvature-corrected θ), not the target incidence: for the tested geometries the two differ by ≈3–4° (e.g., ξ = 30° → θ ≈ 33.6°). Since sinθ and sinθelev are strictly monotone in each other over the tested band, ordering is preserved and the index is defensible — but the "ground pixel area" reading of f2 in §3.2 is not literally the canonical pixel area.
**Evidence Anchor**: [`equation: Eq. (5) f2 = Σ sinθelev,i·cosψsq,i — θelev satellite-centered vs. §2.2 ρ_rg = c/(2B sinθ) target incidence`]
**Why it matters**: Minor for the results (ordering-preserving index), but the paper presents the two angles under one symbol family and claims exact pixel-area semantics; a careful reader (or a SAR engineer) will flag the convention mixing in revision.
**Suggestion**: State explicitly that θelev is the satellite-centered elevation-plane angle, note the ≈3–4° offset from the target-incidence θ of ρ_rg over the tested band, and either compute f2's incidence term with the curvature-corrected θ or justify the satellite-centered form as the ordering-consistent choice (one sentence in §3.2 suffices).
**Severity**: Minor
**Confidence**: 5 — direct spherical-geometry calculation

---

## Coverage Receipt
Not required — both Strengths and Weaknesses are populated.

---

## Detailed Comments

### Literature Review
- **Coverage**: Strong on the 2020–2026 literature (survey, DRL, CP, hybrid, SAR-specific MOEAs). Gaps: (a) the foundational SPOT5 single-satellite daily-scheduling line (Bensana/Lemaître/Verfaillie 1999; Vasquez & Hao 2001 tabu search) — the paper's §2.1 opens with Lemaître 2002 as the "earliest formal treatment," which is true only for *agile* satellites, and the contrast with the classical fixed-attribute model would be sharpened by citing the SPOT5 roots; (b) the formal objective-reduction / redundancy literature in many-objective optimization (Brockhoff & Zitzler 2009; Saxena, Deb et al. 2013), which is directly relevant to the "redundant vs. density-dependent" question and to the HV/correlation discussion — at present, redundancy is treated purely empirically; (c) bi-objective agile-EOS scheduling by Tangpattanakul–Jozefowiez–Lopez (~2015), an intermediate link between single-objective classical scheduling and the NSGA-based multi-objective work the paper sits in; (d) a Sentinel-1 capability/system-level reference (e.g., Geudtner et al., IGARSS 2014) would ground the "generic C-band platform" and the NESZ-decibel discussion.
- **Integration quality**: Good — §2.1 is a critical synthesis organized by the quality-modeling thesis (fixed attribute vs. continuous function) rather than an enumeration; the three-stream structure (scheduling / SAR physics / MOEA) supports the research gap directly.
- **Research gap argument**: Convincing and appropriately hedged ("to our knowledge"); the closest-work contrast (Chang 2022 operational metrics; Kramer & Miller visibility-performance composite; Wei 2025 composite score) is fairly drawn.

### Theoretical Framework
- **Appropriateness**: NSGA-III with Das–Dennis reference points is an appropriate framework for 2–3 objective problems; the mean-over-scheduled-tasks normalization that decouples quality from coverage is a thoughtful design choice that makes the quality–coverage Pareto trade-off genuine rather than an artifact of selection count.
- **Application depth**: The framework is applied deeply, not cosmetically — the objective space is derived from LOS kinematics, the correlation analysis separates definitional vs. scheduler-induced coupling, and the ablation variants (B/C/D) are designed to isolate components. The physical inside of the objectives is the paper's genuine framework contribution.
- **Alternative frameworks**: The paper could be pushed to cite and use objective-correlation/reduction diagnostics (Brockhoff–Zitzler; Saxena) to formalize "redundancy" beyond an empirical ±0.2–0.7 correlation narrative, and MOEA/D or SMS-EMOA comparisons are correctly deferred to future work (§4.1).

### Academic Argument Quality
- **Factual accuracy**: Spot-checked headliners: Table 2 S1 (G-BL f2 = 0.295, f3 = 0.497; MOEA-2 f1* = 0.86, +33.3% f2; MOEA-3 f1* = 0.85, +40.4% f3) matches the data; the ρ_rg ≈ 5.3 m example at θ = 30° is correct (c/2B sin30° with B = 56.5 MHz). Verified anchors that are correct: r_null = −0.51 (MC −0.5110), θ-only −0.997, ψ-only +0.997, the ±608 km / ±5.5° swath consistency, G-SM f1* δ = −1.000. Verified anchors that are wrong or stale: §6.2 δ = +0.88 (data: 0.99), §6.3 "6%"/"78%" (data: 10%/80%), N50 50 vs. 45, Fig. 6 ±4% vs. Table 4 −18%/+25%.
- **Argument logic**: The causal chain observed → lower-squint convergence → envelope correlation attenuated (−0.97 → −0.63) → margin collapse at high density is coherent and well-defended by the D-variant control (r ≈ −0.13 at S1 without physics). One place to tighten: the "no-physics solver's packing incidentally favors lower-squint windows" explanation for D's weak correlation is asserted without direct evidence on the time/geometry distributions D actually selects — a two-sentence diagnostic (mean |ψ| and θ distribution of D's S1 schedules) would close the loop.
- **Terminology precision**: The θ/θelev/ξ convention family (§3.1–3.2) is explicitly defined and internally consistent, except the pixel-area reading noted in W6. "Conservative envelope" (W3) is the one genuinely misleading label.

### Contribution to the Field
- **Incremental contribution**: Genuine and specific: (i) a decomposed, closed-form, ordering-consistent NESZ + geometric-resolution objective pair embedded in NSGA-III scheduling (the first to my knowledge with this decomposition); (ii) an empirically characterized density-dependent saturation regime with a physical mechanism (lower-squint convergence + envelope correlation attenuation) rather than a mere empirical "it doesn't work"; (iii) a rigorous conditional result (hot-start dependence) that future work can build on. The contribution advanced is "understanding when and why physics-aware multi-objective scheduling stops paying" — a legitimate and useful negative-space result for the community.
- **Positioning**: Clearly positioned against Chang 2022 / Kramer & Miller / Wei 2025 with explicit differentiation (decomposed vs. composite proxies). The claim "no existing method uses continuous physics-derived quality as decomposed objectives" survives scrutiny of the cited set.
- **Overclaiming risk**: Low — the abstract, §7.1, and Conclusion all hedge appropriately ("operationally sufficient," "conditional on the hot start," "empirical saturation boundary"). The main overreach risk is the operational-implications paragraph (§7.2) and the abstract's +41% framing (see W3 and W5); the "third objective is density-dependent rather than redundant" phrase is stronger than the evidence (a +7% at one density class with an admitted confound) and would be more accurate as "its marginal value is confined to sparse densities and carried by the squint channel."

### Missing Key References
All items below are recommendations for the authors to locate and verify; none were found in session materials, so each is tagged `[UNVERIFIED]` per the no-invention rule, with my attestation confidence stated:
1. `[UNVERIFIED]` Bensana, Lemaître, Verfaillie (1999), *Constraints* — daily photograph scheduling of an Earth-observation satellite (SPOT5 benchmark). Foundational single-satellite scheduling formulation; high confidence of existence; the §2.1 opening should cite it alongside Lemaître 2002.
2. `[UNVERIFIED]` Vasquez & Hao (2001), *Computational Optimization and Applications* — logic-constrained knapsack + tabu for the SPOT5 daily problem. Canonical metaheuristic result for the same benchmark; high confidence of existence.
3. `[UNVERIFIED]` Brockhoff & Zitzler (2009), *IEEE Transactions on Evolutionary Computation* — "Objective Reduction in Evolutionary Multiobjective Optimization: Theory and Applications" (also the PPSN 2006 precursor). High confidence of existence; directly grounds the third-objective redundancy question.
4. `[UNVERIFIED]` Saxena, Deb, Duro (2013), *IEEE Transactions on Evolutionary Computation* — nonlinear/linear objective reduction in many-objective optimization. High confidence of existence; complements #3 for the mixed linear/curvilinear case.
5. `[UNVERIFIED]` Tangpattanakul, Jozefowiez, Lopez (c. 2015, *Engineering Optimization* / related venues) — bi-objective (NSGA-II, coverage vs. minimization) scheduling of agile satellites. Medium-high confidence of existence; intermediate link in the MOEA-EOS line.
6. `[UNVERIFIED]` Geudtner, Torres, Snoeij, Davidson, Rommen (IGARSS 2014) — "Sentinel-1 system capabilities" (exact title/venue to verify). Medium confidence; would ground the generic C-band platform and NESZ conventions in an operational example.

---

## Questions for Authors
1. Which real platform class does the ψ_sq ≤ 45° / θ ∈ [18°, 47°] envelope represent, and how would the headline sparse-regime gains (MOEA-2 +34% f2, MOEA-3 +41% f3, G-SM +45% f3 at S1) change under a reduced envelope (e.g., ψ_max = 10°)? A sensitivity run on S1–S2 would answer this without a full recompute.
2. Does including the disclosed-but-omitted sinθ ground-reference-area factor (and/or the antenna elevation-pattern roll-off) in the f3 model change any reported ordering or the correlation values (§6.4)? The ordering argument in §2.2 is plausible; a one-line numerical check (cos³ξ vs. cos³ξ·sinθ over [18°, 47°]) would settle it.
3. What are the paired Wilcoxon p and Cliff's δ for MOEA-3 vs. MOEA-2 on f3 and on f2 at S1? The +7% marginal-value claim currently has no reported test, and it is the load-bearing statistic for "density-dependent rather than redundant."
4. Can the authors reconcile the reported G-SM f3 effect sizes (§4.3: +1.0; §6.2: +0.88) with the shipped data (recomputed 0.990, 199/200 scenarios)? Which statistic chain (and which snapshot) produced the 0.88, and does any other reported statistic come from that same stale snapshot?
5. For variant D at S1, what are the mean |ψ_sq| and θ distributions of the selected times? The claim that "temporal packing incidentally favors lower-squint windows" (explaining D's r ≈ −0.13) would be directly supported by these diagnostics.

---

## Minor Issues

### Language / Grammar
- None of consequence.

### Citation Format
- §2.1's "earliest formal treatments" attribution should cite Bensana 1999/Vasquez–Hao 2001 (SPOT5) or qualify "of agile satellites" (§2.1, paragraph 2).
- The Yao 2024 and Wu 2019 (also ASR) references are correctly cited; check the Wei 2025 MOEA "composite image quality score" description against the source ("image quality" = which metric?).

### Figures and Tables
- Fig. 6 (see W1) must be regenerated with axes that represent Table 4 (or the table's values corrected to the figure's — not acceptable as-is).
- Fig. 1's panel (a) annotation "G-SM better: N/200" is only visible at print size if the figure is rendered ≥ half-width; consider stating both δ and the 199/200 count in a caption.
- Table 3 row S2 (10%) and §6.3 prose (6%) must be reconciled (W4 appears text-side); the S1 cell (78%) differs from data (80%) by one scenario — re-verify the reported value.
- The N50 value appears twice (≈50, ≈45); use one authoritative number with its CI in both places.

### Layout
- §6.4 is long (≈80 lines with three italic sub-blocks); consider promoting the "Mechanism" derivation (envelope vs. null vs. schedule correlation) to a compact appendix-style block or a dedicated table of the four correlation values (null −0.51, envelope −0.97, schedule −0.63/−0.15/−0.13/−0.23, D-control −0.13), which would materially aid readability.

---

## Criterion-Bound Judgements

Calibration status: `NOT_CALIBRATED`

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | ARS quality rubric | MEETS | [`equation: Eq. (5),(9) decomposition + null analysis`] | First decomposed physics-quality objectives in SAR scheduling; empirical saturation regime as a contribution | Literature beyond cited set not exhaustible | yes — central |
| Methodological Rigor | ARS quality rubric | MEETS | [`table: Table 4 ablation; §5.3 metrics`] | Controlled ablation, four robustness controls, honest CIs | Fig. 6 / δ = 0.88 staleness reduce confidence (repairable) | yes — revised figure/statistics needed |
| Evidence Sufficiency | ARS quality rubric | PARTLY_MEETS | [`absence: §6.4 — expected direct test of MOEA-3 vs. MOEA-2 f3 at S1; checked §6.1–§6.4, §7.1`] | Headline tables verified against data; sparse-regime third-objective claim lacks a direct test and is confounded (H asymmetry) | Envelope-sensitivity experiments not run | yes |
| Argument Coherence | ARS quality rubric | MEETS | [`text: §6.4 mechanism + §9.1 Limitations`] | Mechanism story is internally consistent and limitation-aware | Two statistic contradictions (δ, %, N50) must be fixed | yes — minor |
| Writing Quality | ARS quality rubric | MEETS | [`text: §2.2 disclosure paragraph`] | Precise, honest, well-structured prose | §6.4 density could be improved (see Minor Issues) | no |
| Literature Integration | ARS quality rubric | MEETS | [`text: §2.1 gap argument`] | Current and synthesized; gap claim survives scrutiny | Foundational SPOT5 + objective-reduction refs missing | no |
| Significance & Impact | ARS quality rubric | PARTLY_MEETS | [`text: §7.2 operational implications`] | Useful negative result + conditional guidance; operational transfer depends on squint-envelope realism | Real-platform squint limits not public; gains conditioned on idealized envelope | yes |

---

RECOMMENDATION: Major Revision