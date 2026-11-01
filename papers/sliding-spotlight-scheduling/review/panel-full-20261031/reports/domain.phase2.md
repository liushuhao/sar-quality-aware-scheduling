contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: warn
trigger: "domain inaccuracies, imprecise if defensible approximations"

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read the manuscript as a specialist in agile-SAR mission planning and checked the physics chain end to end: the antenna-to-resolution identities, the rotation-centre geometry, the dwell closures, the ambiguity formulation, the quality index, and the floor arithmetic that produces the control family's infeasibility. The geometry and arithmetic are internally consistent and I re-derived the load-bearing constants independently (D = lambda/theta_a = 4.9338 m; A D/2 = 0.5000 m; the per-mode index constants 0.8107 / 19.7352 / 54.8322 per square metre and their 24.3x / 67.6x / 2.8x ratios all reproduce from the stated formulas). The stripmap floor step is exact arithmetic, not a search outcome, and the paper demonstrates it with an in-sweep tier-shift whose predicted threshold is confirmed at the observed cell. Prior work is represented with unusual care: the nearest SAR-specific neighbours are named and separated, the literature's task envelope is kept as a separate registered field rather than merged with the design envelope, and the paper explicitly declines to claim absence for the multi-objective quality line.

The substantive domain reservation is the ambiguity module. Section 3.3 integrates azimuth ambiguity over a Doppler occupancy built from the zero-squint azimuth resolution alone, while Section 3.2 builds the dwell from beam sweep plus an explicit scene-length term W_a. The scene sweep therefore enters the imaging-time closure and is excluded from the ambiguity integral, and the beam-limited footprint screen in Section 5.1 reinforces that exclusion. That asymmetry, not merely the modelling choice, is what drives the reported squint direction. Section 7.2 offers the scene-scan-span channel as a candidate reconciliation but does not connect it to the paper's own dwell closure, so the claim of "a difference of mechanism, not merely of sign" is not supported at the level the paper asserts.

The remaining reservations are secondary and largely disclosed by the authors themselves: the delivery identity's status as a definition rather than a physical validation, the approximation status of the dwell closure that feeds the transfer chain, the deliberately double-counted azimuth weight in the quality index, two of five constraint families that cannot bind, and some terminology overlap. None of these touches the coverage-cost result, which survives them.

### S1: Geometry and index arithmetic reproduce independently from the stated formulas

Every load-bearing constant I re-derived matches: the antenna azimuth length from wavelength and beamwidth, the sliding factor from the rotation-centre ratio, the per-mode zero-squint resolutions, the per-mode quality constants, and the stated magnitude ratios. Full-precision residual claims and the fixture identity are consistent with the quoted values.

**Evidence Anchor**: equation: §3.1–§3.3 (D = lambda/theta_a; A = r0/(R0+r0); rho_a per mode; f_q per-mode constants and ratios)

### S2: Approximations and convention choices are labelled with direction and magnitude

The manuscript does not merely list limitations; it gives each one a direction and, where possible, a magnitude, and it keeps conventions that must not be mixed apart. The ambiguity sum excludes the principal image for a stated reason, the sliding-spotlight squint cap is declared a design choice rather than a physical boundary, and the omission of the absolute Doppler centre is quantified against the PRF.

**Evidence Anchor**: text: §2.1 and §3.3 "a registered conservative value, a design choice" and "keeping $m=0$ would place the principal image in its own numerator"

### S3: Prior work is represented faithfully, including the neighbours that would undermine a stronger claim

The related-work section separates the imaging line, the scheduling line and the quality-aware line at a stated seam, names the four closest SAR-specific mission-planning papers, distinguishes the staring/video line where duration is also a planning quantity, and explicitly refuses an absence claim for multi-objective quality work. That is the correct handling of a narrow novelty margin.

**Evidence Anchor**: text: §2.3–§2.4 "nothing here claims its absence" and "the imaging geometry is fixed upstream of the scheduler"

### S4: The stripmap floor step is demonstrated as arithmetic, with a predictive check

The control family's infeasibility at the tightest point is derived from the frozen bandwidth and the frozen grid rather than asserted, and the tier-shift reanalysis predicts the threshold location and finds the observed step exactly there. This is the strongest single piece of physical validation in the results section.

**Evidence Anchor**: text: §6.7 "the predicted all-infeasible threshold moves to $s^{*}=2.4669/(3.0/1.1)=0.905$, and the observed step moves exactly there"

### S5: Retracted readings are disclosed rather than silently carried

The v4 tight-arm penalty is explicitly withdrawn, the retired power analysis is stated as retired and not reproduced, the synthetic-family artifact carries a provenance caveat wherever cited, and the retired ablation is kept out of the counterfactual. For a field with a long history of stale-comparison drift this is a meaningful discipline.

**Evidence Anchor**: text: §6.3, §6.6 and §8 "the tight-arm penalty is withdrawn rather than quietly carried forward" and "is not mixed in"

### W1: The ambiguity module excludes the scene scan span that the dwell closure includes, and that asymmetry drives the reported squint direction

Section 3.3 builds Doppler occupancy from the zero-squint azimuth resolution only, so the only squint-dependent channel is a narrowing bandwidth, which mechanically makes the ambiguity ratio improve with squint and produces the reported monotone improvement from -21.35 dB to -23.32 dB against a literature anchor that degrades with scan angle. Section 3.2, by contrast, builds the dwell from beam-edge sweep plus an explicit scene-length term, and Section 5.1 screens the along-track footprint at the beam-limited bound; both treat the azimuth extent as beam footprint plus scene sweep. The competing literature mechanism that Section 7.2 names as the reconciliation candidate, a scene-ensemble scan span that grows Doppler occupancy with scan angle, is therefore not simply unmodelled: it is modelled in one closure and dropped in the other. As a result the paper cannot support its claim that the contrast is "a difference of mechanism, not merely of sign" — the sign may be an artifact of the occupancy construction. Repairing this requires re-evaluating the ambiguity integral with a scene-sweep occupancy term and re-reading the direction contrast, which is substantial re-analysis but leaves the coverage results untouched, since the ambiguity gate never binds in this scenario set.

**Severity**: Major
**Evidence Anchor**: text: §3.2–§7.2 "the compression factor $a_{\mathrm{res}}\equiv A$ is squint-invariant" and "the registered scene term $W_a$ enters unscaled" and "the scene-scan-span channel is the candidate reconciliation a targeted experiment would test first"
**Confidence**: 4 — derived from the manuscript's own formulas and cross-checked against the standard azimuth-ambiguity and sliding-spotlight literature treatment.

### W2: The delivered-resolution identity is definitional, so it cannot serve as evidence of physical correctness

Constraint C5 sets the task-level sliding factor and spotlight sweep span from the requirement at the selected start and then verifies that the delivered resolution equals the requirement. That identity holds for any model, right or wrong, because the parameter was solved from it; it validates the implementation path, not the physics that produced the dwell. The paper is transparent that the search "cannot violate" it, but the contributions section presents it as the enabling platform leg, and the only independent physical check offered is the internal comparison of the symmetric construction against the exact rotating-centre chain. A domain reader should read the platform contribution as a consistency architecture rather than as a validated physical model, and the manuscript would be stronger saying so in the contribution sentence itself.

**Severity**: Minor
**Evidence Anchor**: text: §1.2 "an identity the search cannot violate rather than a constraint it could"
**Confidence**: 4 — consistency between C5's construction and its verification is visible directly in §3.4.

### W3: The dwell that prices the transfer chain is the approximate closure, and its true error is unquantified

The production dwell uses the symmetric beam-edge construction; the exact rotating-centre quadratic enters only as an internal identity check, and the two are reported to differ by at most 1.9 percent at the envelope corner. The window-tail pad, however, is explicitly not claimed to bound the production closure's squint error, which is stated as not separately quantified. Because the dwell enters the inter-task constraint through a 25 percent pad the practical consequence is almost certainly small, but the paper's central mechanism is exactly this dwell, so the gap between "the two internal closures differ by 1.9 percent" and "the production closure's error against truth is unknown" should be stated where the closure is introduced rather than only in the caveat section.

**Severity**: Minor
**Evidence Anchor**: text: §3.2 "the symmetric construction deviates from the exact chain by at most $1.9\%$" and "it is not claimed to bound the production closure's own squint error"
**Confidence**: 4 — the closures and their stated comparison are given in one paragraph.

### W4: The quality index is deliberately non-radiometric, and the term "image quality" travels further than the index supports

The index weights azimuth resolution twice by construction, the gain term has no external cross-validation, and no calibrated radiometric quantity enters it. The manuscript discloses all three. The residual concern is lexical rather than numerical: the abstract states that "image quality is reported, never optimised", and the reported reading travels per family, while the index itself is a resolution-dominated quantity with a relative range factor. A reader who takes the fulfillment ratios as a quality measure comparable across families would be over-reading, and although the paper forbids that comparison, the term itself invites it. Renaming the quantity at first use, or pairing it with the resolution-dominated label every time it appears, would close the gap.

**Severity**: Minor
**Evidence Anchor**: text: §3.3 "the index deliberately weights azimuth resolution twice"
**Confidence**: 4 — the construction and its disclosure are explicit in the same paragraph.

### W5: Two of five constraint families cannot bind, and one was made non-binding by a same-day redefinition

The energy/duty and memory families are structurally slack inside the squint envelope, and the duty normalisation reference was redefined on the day the sweep ran, from the library-constant dwell to a per-task envelope maximum that exceeds the earlier reference by up to 1.2008x, removing false violations by construction. The paper states plainly that the binding set has exactly two members and that the inventory is a model, not a claim that five mechanisms bind. The domain consequence is that the platform model's power and storage budgets are effectively unconstrained in this scenario set, so the "five constraint families" framing overstates the richness of the physical model relative to the two families that actually price a schedule. This is a labelling issue rather than an error, but it matters when a reader assesses whether the scheduler is being asked to solve a realistic mission-planning problem.

**Severity**: Minor
**Evidence Anchor**: text: §3.4 "the normalisation reference was redefined on 2026-10-20, on the day the sweep ran" and "has exactly two members"
**Confidence**: 4 — both statements are in the same constraint-inventory paragraph.

### W6: Terminology overlap between resolution concepts and between dwell concepts

The manuscript uses "resolution" for the per-task azimuth requirement in the constraint set but for a two-axis quantity in the quality index, and it uses dwell, synthetic-aperture time and imaging time at points where the referent differs (scene-level sweep versus point-target integration). Demand and requirement are declared to be one object in Section 3.5, which helps, but the declaration is local. A short statement at first use of each pair, rather than a reminder in one subsection, would remove the ambiguity without changing any claim.

**Severity**: Minor
**Evidence Anchor**: text: §3.3 "denotes spatial-resolution quality under a gain-shaped multiplier"
**Confidence**: 3 — judged from the manuscript's own usage pattern across sections, not from an external terminology standard.
