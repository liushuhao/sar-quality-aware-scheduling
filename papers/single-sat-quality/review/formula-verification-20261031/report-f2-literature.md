# F2 literature cross-check report — formula-verification-20261031

## Sources used

1. **Radar Tutorial, “Side-Looking Airborne Radar”** — https://www.radartutorial.eu/20.airborne/en/ab06.en.html — ground-range resolution in terms of pulse duration and incidence angle.
2. **Radar Tutorial, “Synthetic Aperture Radar”** — https://www.radartutorial.eu/20.airborne/en/ab07.en.html — conventional zero-squint stripmap azimuth-resolution baseline.
3. **Radar Tutorial, “Doppler- Effect”** — https://www.radartutorial.eu/11.coherent/en/co06.en.html — Doppler frequency in terms of radial velocity and wavelength.
4. **Hamidi, “Entropy-Based Doppler Centroid Estimation and Speckle Noise Reduction for Spaceborne SAR Imaging”** — https://arxiv.org/abs/2008.07457 (equation-bearing HTML: https://ar5iv.labs.arxiv.org/html/2008.07457) — Doppler-centroid/range-rate relation and PRF ambiguity.
5. **Moro et al., “Exploring ISAC Technology for UAV SAR Imaging”** — https://arxiv.org/abs/2401.10606 (equation-bearing HTML: https://ar5iv.labs.arxiv.org/html/2401.10606) — received-power, compression-gain, and NESZ equations; inspected for the claimed range cubic law.
6. **Li, Luo, and Zhu, “Estimation of the Image Interpretability of ZY-3 Sensor Corrected Panchromatic Nadir Data,” *Remote Sensing* 6 (2014), 4409–4429** — https://doi.org/10.3390/rs6054409 — published off-nadir GSD equation and its X/Y ground-sample-distance construction.
7. **Radar Tutorial, “Clutter Doppler Frequency”** — https://www.radartutorial.eu/20.airborne/en/ab10.en.html — azimuth beamwidth and Doppler-bandwidth relation.
8. **Davidson and Cumming, “Signal properties of spaceborne squint-mode SAR,” *IEEE Transactions on Geoscience and Remote Sensing* 35 (1997)** — https://doi.org/10.1109/36.581976 (author copy: http://sar.ece.ubc.ca/papers/Davidson_SignalProp_TGRS97.pdf) — squint-SAR Doppler-centroid, ambiguity, and PRF constraints. Only extracted prose is quoted; its image-based equations were not used as evidence.

## Per-formula verdicts

### 1. `ρ_rg = c / (2B sinθ)`

Source [1]: “The cross-track resolution, R r , is defined as: R r = c 0 · t p” over “2 sin θ”; and “t p is the pulse duration of the transmitter, and θ = incidence angle”.

**Verdict: MATCHES-UNDER-APPROXIMATION.** The source gives `ρ_rg = c t_p/(2 sinθ)`. The manuscript follows after the pulse-compression substitution `t_p = 1/B`; it is not the source's uncompressed-pulse form. This also assumes the usual flat local ground/incidence-angle definition and ideal bandwidth-to-resolution conversion.

### 2. `ρ_az = D / (2 cosψ_sq)` for squinted stripmap

Source [2]: “The achievable azimuth resolution of a SAR is approximately equal to one-half the length of the actual (real) antenna and does not depend on platform altitude (distance).”

**Verdict: NOT FOUND.** The inspected authoritative source establishes only the broadside `D/2` baseline, not the additional `1/cosψ_sq` factor. The Davidson–Cumming paper was inspected, but its equations are images and were not treated as read evidence. No adequate accessible source stating the complete displayed squinted-stripmap form was verified; the 10–20% amplitude-weighting allowance likewise was not independently verified.

### 3. `NESZ ∝ R³` for stripmap after azimuth-compression gain

Source [5], equations (6)–(9): `P_RX = [P_TX G_TX f(θ)/(4πR²)] σ [A_e f(θ)/(4πR²)]`; `SNR_foc = SNR_RC N_τ`; `NESZ = σ_0 / SNR_foc`. Its prose states: “after azimuth compression, we have the final focused image where the SNR is increased once again by the number of processed pulses Nτ”.

**Verdict: NOT FOUND.** These equations give received power proportional to `R^-4` and show the compression gains, but the inspected source does not state the further relation between processed pulse count and range needed to reduce the full expression to `R³`. They therefore do not, by themselves, verify the manuscript's cubic law.

### 4. `R ≈ R_elev / cosψ_sq ⇒ NESZ ∝ 1/(cos³θ_elev · cos³ψ_sq)`

**Verdict: NOT FOUND.** No inspected authoritative source stated this combined plane-Earth/flat-squint decomposition. The second proportionality additionally inherits the unverified `R³` premise in item 3; it cannot be promoted to a standard NESZ law from the sources inspected.

### 5. `cos ξ = cos θ_elev · cos ψ_sq`

**Verdict: NOT FOUND.** No authoritative source stating this spherical identity with the manuscript's angle definitions was located in the inspected material. In particular, no source was verified that defines `ξ`, `θ_elev`, and `ψ_sq` as the sides/angles of the applicable right spherical triangle.

### 6. `f₂ = mean over tasks of sin θ_elev · cos ψ_sq`, claimed proportional to an inverse per-task ground-pixel-area factor

Source [1] supplies only the range-side incidence factor through “2 sin θ” in its resolution denominator.

**Verdict: NOT FOUND.** The inspected sources do not state this task-averaged objective or establish that the full product `sinθ_elev cosψ_sq` is an inverse per-task ground-pixel-area factor. The aggregate index appears manuscript-specific; sourcing one trigonometric component is not verification of the claimed standard formula.

### 7. `f₃ = mean over tasks of cos³ ξ`, claimed as a NESZ-ordering index under item 4's decomposition

Source [5] defines NESZ as “the equivalent normalized radar cross section ( σ 0 ) that yields a unitary Signal-to-Noise Ratio (SNR) of the resulting image”, but does not state this task-averaged index.

**Verdict: NOT FOUND.** No inspected source states `mean(cos³ξ)` as a NESZ-ordering index. It depends on the unverified geometry and range scaling in items 3–5 and should not be represented as a literature-standard objective.

### 8. `f_dc ≈ (2v/λ) sinψ_sq`

Source [3]: “f D = 2·v · cos α” over “λ”; “α = angle between the direction of the transmitted/reflected signal and the direction of flight of the target”; and “Only the radial speed is then also measured.” Source [4], equation (7): `f_dc = 2/λ · dR(η)/dη |_(η=ηc) = 2/λ · v²ηc/R(ηc)`.

**Verdict: MATCHES-UNDER-APPROXIMATION.** With the angle complement `α = 90° − ψ_sq`, the general radial-velocity Doppler expression gives the manuscript's magnitude. Approximations/scope: monostatic two-way propagation, constant platform speed over the relevant measurement, squint measured from broadside in the velocity/line-of-sight plane, beam-center evaluation, and magnitude-only/sign-free use as the manuscript explicitly states.

### 9. `ψ_sq = arcsin(|l_x| / R)`

**Verdict: NOT FOUND.** No inspected authoritative source stated this inverse-sine construction with the manuscript's `l_x` definition. Sources [3] and [4] support the Doppler/range-rate physics, not this particular vector-geometry identity; that missing geometry cannot be inferred from item 8 alone.

### 10. Off-nadir optical pixel footprint `∝ 1/cos²η`

Source [6], equation (2): `GSD = (PP/FL) × (SL / cos(LA))`. It defines the variables as follows: “PP is the pixel pitch, FL is the focal length, SL is the slant range and LA is the look angle”. It also states: “The GSD was computed in inches in both the X and Y dimensions (the along-scan and cross-scan directions, respectively), and we calculated their geometric mean.”

**Verdict: MATCHES-UNDER-APPROXIMATION.** The published source gives a one-dimensional `sec(LA)` projection. Applying that same projection to both X and Y ground-sample distances and multiplying them gives area proportional to `sec²(LA)`; that area-product step is a derivation, not a verbatim footprint equation in the source. It requires fixed slant range, pixel pitch, and focal length, locally flat terrain, a small-pixel/pinhole approximation, and neglect of Earth curvature and terrain relief.

## Disclosure completeness

The disclosed list is incomplete. Additional first-order effects found in standard treatments are:

1. **Azimuth antenna beamwidth/pattern and Doppler bandwidth.** Source [7]: “The Doppler bandwidth consists of the frequencies produced, as a result of scatterers falling in the beamwidth of the radar, as the platform moves past the targets.” It gives the narrow-beam relation `f_D1 − f_D2 = 2v·φ_a/λ` and defines `φ_a` as “the −3dB beamwidth”. Thus an azimuth antenna/pattern-dependent Doppler bandwidth enters the imaging model independently of the disclosed elevation-pattern roll-off.
2. **Processed azimuth bandwidth and aperture/window choice.** The same source [7] ties Doppler bandwidth to beamwidth, while source [8] states: “Finally, the behavior of azimuth bandwidth is important in terms of maintaining a PRF that satisfies the SAR constraint of fitting a received echo between transmitted pulses.” A fixed geometric resolution formula therefore omits the usable/processed bandwidth, aperture length, and weighting/window assumptions that determine realized resolution and ambiguities. The disclosed 10–20% amplitude-weighting constant does not disclose these broader processing choices.
3. **PRF/azimuth-ambiguity coupling.** Source [4]: “Since the sampling rate in the azimuth direction is equal to the PRF, therefore, if the Doppler centroid frequency exceeds the PRF, there will be ambiguity in its estimated value.” It also gives `f_dc = M × PRF + f'_dc, M ∈ ℤ` with `−PRF/2 ≤ f'_dc ≤ PRF/2`. Source [8] independently warns: “Doppler centroid variation with terrain height can lead to undersampling and azimuth ambiguities.” PRF selection, centroid wrapping, terrain-dependent centroid variation, and azimuth ambiguities therefore merit explicit disclosure rather than only a magnitude-only Doppler caveat.

## Summary

- **DIFFERS:** none.
- **NOT FOUND:** #2 (complete squinted-stripmap resolution and weighting allowance), #3 (`NESZ ∝ R³`), #4 (combined range/NESZ decomposition), #5 (spherical identity with the manuscript's definitions), #6 (task-mean inverse-ground-pixel-area index), #7 (task-mean NESZ-ordering index), and #9 (`arcsin(|l_x|/R)` geometry).
- Items #1, #8, and #10 match only under the approximations and derivation steps named above.
