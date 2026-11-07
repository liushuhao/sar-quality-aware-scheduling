# Domain Review — paper1

Seat: Reviewer 2 (SAR systems / radar imaging physics).
Manuscript: `papers/single-sat-quality/small-paper-ijae.tex` + `sections/_ablation_section.tex`.
Date: 2026-11-07.

## Canary
1. Read-only: I modify no file except this report.
2. Every finding quotes the exact manuscript text, with section and tex line.
3. No fabricated facts about cited works.
4. Numbers quoted as printed; arithmetic I perform is labelled as mine.
5. No network access.
6. Genuine strengths and weaknesses.
7. Stdout at most 5 lines.

## Summary judgement
The SAR side of the paper is unusually careful for a scheduling manuscript: the platform is internally consistent, the NESZ proxy is defended with its own error budget, and the Doppler/PRF passage added since the last round is technically correct. The remaining domain concerns are about what the model *implies for a real platform*, not about arithmetic: the schedules live at 16–24° mean squint, which requires a PRF and receive-window design that standard Stripmap does not have, and the energy/memory budget that sets the dense-regime ceiling is expressed in arbitrary units with no relation to a real duty cycle. Both are disclosed; neither yet reaches the operational recommendation.

## Strengths
- **The platform parameters cohere.** 693 km sun-synchronous at ~97.8°, D = 12.3 m, B = 56.5 MHz, bilateral 18–47° incidence (l.756-765). With ρ_rg = c/(2B sinθ) these give 3.6 m at 47°, 5.3 m at 30°, 8.6 m at 18°; ρ_az = D/(2cosψ) gives 6.15 m at zero squint and 6.5 m at 20°. The quoted objective values are therefore engineering-consistent, not arbitrary scores.
- **The NESZ proxy is defended with its own error budget.** "at the 47° edge ... it underestimates slant range by roughly 4% and R³ by roughly 13%" (l.433-435) and the alternative computation "+40% to +94%" (l.452-456). This is the right way to handle a proxy.
- **The ordering argument is stronger than the paper claims.** The omitted terms — the ground-reference sinθ factor, the two-way azimuth antenna gain roll-off with squint, and the azimuth processing loss — are all monotone in the same controlling variable (|ψ_sq| rising worsens them). The paper argues the sinθ case explicitly; the antenna-gain case is at least as clean and would strengthen the defence.
- **The Doppler/PRF paragraph is correct.** "the geometric Doppler centroid f_dc ≈ (2v/λ) sin ψ_sq reaches 10² kHz at the scheduled 16–24° squints, one to two orders of magnitude above typical Stripmap PRFs (10⁰–10¹ kHz)" (l.546-549). Checked: C-band λ = 0.0555 m, v ≈ 7.06 km/s, 2v/λ ≈ 2.55×10⁵ Hz, so 20° squint gives ≈ 87 kHz. The statement holds. The yaw-steering claim also holds — yaw steering compensates Earth rotation, not geometric squint.
- **The elevation-plane incidence angle is correctly separated from target-side incidence.** "θ_elev ... differs from the target-side incidence angle defined above by a few degrees due to Earth curvature at these orbital altitudes, but it preserves the cross-track ordering" (l.356-361).

## Findings

### R2-01 [MAJOR] The operational recommendation does not carry the realizability caveat that §3.3 establishes
- Quote: §3.3 — "A squinted acquisition therefore requires a dedicated receive-window and PRF timing design, which is outside the model ... absolute performance claims for platforms without a dedicated large-squint timing/processing chain are out of scope" (l.554-567). Against §7.2 — "Our results suggest a conditional operational guideline: for sparse observation requests (N ≲ 100) on squint-agile platforms (the 45° experimental envelope of §3.2), MOEA-2 may provide geometric quality gains that outweigh the coverage penalty" (l.1501-1505).
- Problem: the recommendation names "squint-agile platforms" as though such platforms schedule Stripmap at 16–24° mean squint routinely. They do not: that geometry needs PRF in the tens-to-hundreds of kHz and a receive-window design outside conventional Stripmap, which the paper itself says is out of scope. The caveat exists two sections earlier and is absent from the sentence a mission planner will quote.
- Fix: append the caveat to the recommendation, e.g. "on platforms with a dedicated large-squint timing/processing chain (§3.3)". One clause, no new claim.

### R2-02 [MINOR] "NESZ" in title and keywords versus "ordering index" in §3.2
- Quote: keywords "noise-equivalent sigma-zero (NESZ)" (l.67) and title (l.24) versus "used here as a relative ordering index ... not as an absolute radiometric prediction" (l.437-439).
- Fix: qualify the keyword and title (see EIC-02), or add "(ordering index)" in the keyword list.

### R2-03 [MINOR] The θ_elev / target-side incidence difference is asserted but not quantified
- Quote: "differs ... by a few degrees due to Earth curvature at these orbital altitudes" (l.357-359).
- Problem: "a few degrees" is load-bearing for an ordering claim across targets at different latitudes. A referee will want the number at 18° and 47°.
- Fix: quote the two differences (one short parenthetical), or state the maximum over the tested envelope.

### R2-04 [MINOR] The dense-regime ceiling is an arbitrary-unit resource cap
- Quote: "Emax = 10^7 and Mmax = 10^11 (arbitrary units) and typical per-task consumptions are e_i = 5×10^4 and m_i = 5×10^8. Both caps therefore translate into the same ceiling of 200 concurrently scheduled tasks" (l.595-599).
- Problem: two independent budgets are calibrated to coincide on one integer, which makes the ceiling a design choice rather than a physical constraint. It binds in 20/50 S3 and 27/50 S4 scenarios — i.e. it shapes the very regime where the paper's second boundary lives. For SAR, the binding currency is duty cycle and downlink, not an abstract counter.
- Fix: either tie the cap to a stated platform number (e.g. duty cycle × horizon, or downlink bandwidth × contact time) or state explicitly that the dense boundary is conditional on this cap and report the C2-limited subset boundary (see R1-02).

### R2-05 [MINOR] Mean squint of 16–24° with a 90th percentile of 32–39° needs a platform justification
- Quote: "the mean |ψ_sq| across the four density classes is 16–24°, with a 90th percentile of 32–39°" (l.461-464).
- Problem: for an "agile SAR" the agility is usually demonstrated at Spotlight squints; here it is being used in Stripmap. A reader will ask whether a platform exists that does Stripmap at 30° squint. The paper's answer is "the 45° cap is an experimental setting, not a claim about any specific platform" (l.527-530) — correct, but the results are then further from a real system than the title implies.
- Fix: one sentence in §5.1 anchoring the envelope to a platform class (e.g. large-squint experimental SARs / dedicated squinted-Stripmap designs), or a note that a 25° cap is the realistic upper end and that §7.2's envelope sweep already covers the consequence.

### R2-06 [OBSERVATION, not a defect] The azimuth antenna gain roll-off strengthens rather than weakens the ordering argument
- The paper excludes "the azimuth antenna gain roll-off with squint" (l.560-561) from the model. Because antenna gain falls monotonically with |ψ_sq| while f2 and f3 already reward low squint, the omission can only make the reported quality advantage conservative in direction. The paper does not say this and could.

## Questions to authors
1. At 25° squint, what PRF and duty cycle would the described platform need, and does any cited platform achieve it in Stripmap? If the answer is "no platform, experimental envelope only", does the §7.2 recommendation still read as written?
2. Are Emax and Mmax calibrated against any documented platform energy or downlink budget, or are they chosen to produce a 200-task ceiling? If the latter, the dense-regime boundary should be labelled as conditional on that choice.
