# Panel 2026-08-18 — Reviewer 2 (SAR Physics + Agile EO Scheduling Domain)

**Paper:** Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite (ASR target)
**Lens:** SAR imaging-physics correctness, scheduling-literature placement, domain contribution, reference completeness
**Data layer:** pre-gate passed; not re-audited.

## Recommendation: **Minor Revision**
Domain contribution is real and the physics is largely correct with appropriate caveats. Main substantive concerns: (i) the 45° squint envelope undermines the operational recommendation more than the text concedes, (ii) the θ_elev vs target-side θ gap is understated at the incidence edge, (iii) one reference-omission issue and a handful of missing canonical citations. Score: **78/100**.

---

## CRITICAL
None. No factual physics errors that invalidate the results; all approximations are disclosed.

## MAJOR

**M1. 45° squint envelope vs operational recommendation — domain-relevance gap.**
§3.3 C1 (line 454) adopts |ψ_sq| ≤ 45° as an "idealized capability-superset envelope" while conceding "real agile SAR platforms typically slew only a few degrees." This is acceptable as a stress test, but the operational guideline in §7.2 (lines 1259–1264) recommends G-SM for "radiometric priority" at dense N without re-stating that its +16% f3 at S4 (Table 1) was measured under the same 45° envelope. At realistic ±2–5° squint, both the MOEA-3 +41% sparse gain and G-SM's +16% dense gain shrink substantially because cos³ψ_sq is nearly flat for |ψ_sq|<5°. The paper must explicitly bound the operational claim: the dense-regime G-SM recommendation is envelope-dependent.
*Fix:* In §7.2 add a one-sentence caveat that the G-SM/MOEA-3 f3 gains scale with achievable squint and should be re-quantified for a specific platform's agility envelope; the qualitative "greedy suffices at N≥300" conclusion is robust because coverage convergence is C2-driven, but the f3 magnitudes are not.

**M2. Third objective underperforms the squint-only heuristic at S1 — under-discussed.**
At S1 (Table 1): G-SM f3 = 0.722 ± 0.058, MOEA-3 f3 = 0.699 ± 0.037, MOEA-2 f3 = 0.654 ± 0.038. A one-line greedy heuristic that minimizes squint per window reaches *higher* f3 than the three-objective NSGA-III at the sparse regime where f3 is claimed to matter most. The paper reports MOEA-3's +41% over G-BL but does not note that G-SM attains +45% with 51% coverage vs MOEA-3's 85%. The MOEA value is the Pareto trade-off (coverage for f3), not raw f3 maximization — this is implicit but never stated. The abstract's "+41% at 15% coverage cost" could mislead a domain reader into thinking MOEA-3 finds the best f3.
*Fix:* Add one sentence in §6.1 and §6.4 noting G-SM achieves higher absolute f3 than MOEA-3 at S1; the MOEA-3 contribution is retaining 85% coverage (vs G-SM's 44%) while purchasing most of the f3 gain. This strengthens rather than weakens the paper — it clarifies the decomposition.

**M3. f3's omission of the sinθ ground-area factor — caveat present but magnitude understated.**
§2.2 (lines 260–267) acknowledges f3 = cos³ξ suppresses the sinθ factor that standard NESZ-referenced-to-ground-area includes, and says comparisons "depend only on the ordering it induces." Within a single window θ_elev varies ~1.5° (ablation §C, line 118), so within-window ordering is preserved. But across windows/tasks in the same schedule, sinθ spans sin18°=0.31 to sin47°=0.73 — a factor 2.4, larger than the cos³ξ range across the same interval. The "ordering index" defense holds for *which time within a window* but is weaker for *which tasks are selected* across windows. The paper's f2 already captures sinθ, so the trade-off structure is partly preserved, but a domain reader will flag this.
*Fix:* State explicitly that f3 is an ordering index within the scheduling choice (time within window + task selection jointly), not an absolute NESZ prediction; the 17% R³ error at 47° is a separate concern from the sinθ omission. Optionally report a sensitivity check using cos³ξ·sinθ_elev for one density class to confirm ordering invariance.

## MINOR

**m1. θ_elev vs target-side θ difference understated.**
§3.1 (lines 348–352): "differs from the target-side incidence angle of §3.1 by a few degrees due to Earth curvature." At H=693 km and θ=47°, the spherical-Earth mapping gives ξ≈41.3° (sin ξ = (Re/(Re+H))sinθ = 0.659), i.e. ~5.7° at the edge — more than "a few." f2 monotonicity in θ_elev still holds, so the ordering claim is defensible, but the numerical gap should be stated accurately (up to ~6° at the 47° edge).
*Fix:* "differs by up to ~6° at the 47° incidence edge."

**m2. Plane-Earth R³ error: 5%/17% is roughly right but state basis.**
At ξ≈41°, plane R≈1016 km vs spherical R≈949 km → ~7% overestimate in R, ~22% in R³. Paper states 5%/17%. These are rough and within the right order; cite the geometry used (H/cosξ at the edge) rather than leaving the number unsupported.

**m3. f2 formula uses θ_elev but ρ_rg canonically uses target-side θ.**
Eq. 4 (line 387): f2 = sinθ_elev·cosψ_sq. The ground-range resolution ρ_rg = c/(2B sinθ) (Eq. 3, line 240) uses θ, not θ_elev. Since f2 is explicitly an "index" and monotonic, this is acceptable, but state that f2 uses θ_elev as an ordering-consistent proxy for sinθ (consistent with §3.1's θ_elev discussion).

**m4. Antenna D=12.3 m / B=56.5 MHz is Sentinel-1-like — the "generic" framing is slightly misleading.**
§5.1 (lines 630–632): 693 km SSO, D=12.3 m, B=56.5 MHz, C-band is essentially Sentinel-1's Stripmap/EW geometry. Sentinel-1 is not squint-agile (azimuth electronic steering ~±0.5° in TOPS, no large mechanical squint). The paper says "generic C-band Stripmap" — fine — but a domain reviewer will note the platform abstraction conflates a non-agile antenna with an idealized 45° squint envelope.
*Fix:* One sentence noting the antenna parameters are Sentinel-1-class while the 45° squint envelope is an idealized agility superset not representative of any specific C-band mission.

**m5. Missing canonical references.**
- NESZ/system-level: Oliver & Quegan (1998), *Understanding Synthetic Aperture Radar Images*, Artech House — standard reference for NESZ and image-quality decomposition.
- Agile SAR scheduling prior art the bibliography may have missed: Du et al. (2022–2024) have several agile-SAR scheduling papers; the paper cites many Chinese-group works (Chang, Wei, Yao, Wu) but no Du. If none exists on decomposed quality objectives, state the search basis.
- Squint SAR geometry: no meta-hyperbolic-range or squint-mode reference (e.g., Wong & Cumming 1999 on Doppler centroid); not strictly required since Curlander/Cumming suffice, but the ψ_sq treatment would benefit from one.
- Moreira2025 is bib-dated 2026 (Proc. IEEE 114(2)): confirm volume/year; if advanced-access 2025, cite as 2025/2026 consistently.

**m6. G-SM Cliff δ=+0.99 is a near-ceiling, not a discovery.**
§6.2 (line 818): δ=+0.99 with 199/200 scenarios improving. Given f3 is dominated by cos³ψ_sq and G-SM directly minimizes ψ_sq per window, this is mechanically expected. Report it as a sanity check ("confirms squint is the dominant within-window f3 lever") rather than as evidence of a large G-SM effect.

**m7. "Bilateral-looking ±5.5° cross-track = ±608 km" swath is extremely wide.**
Line 639: ±5.5° from nadir at 693 km gives ~608 km ground cross-track per side — a 1200 km total swath, far wider than any C-band Stripmap mission (Sentinel-1 SM ~80 km, Cosmo-Skymed ~40–200 km depending mode). This is consistent with the incidence [18°,47°] range but is not a Stripmap-realistic illumination geometry (it implies ScanSAR-like or multiple sub-swaths to cover). Since the paper abstracts the instrument, acceptable, but note the swath is an idealized access envelope, not a single-Stripmap swath.

**m8. Priority weights p_i ∈ {1..10} uniform.**
Line 661: uniform integer priority is a standard simulation assumption but not domain-realistic (operational priorities are skewed, often 80/20). Doesn't affect the physics claims but limits operational generalization; one sentence in §5.1 acknowledging this is enough.

**m9. Fixed 30 s dwell.**
Line 662 and §7.4: Stripmap dwell is typically determined by azimuth antenna length and PRF, not a fixed 30 s (30 s at 7.5 km/s = 225 km along-track, far longer than a single Stripmap take for most missions). The paper treats it as fixed observation duration d_i. This is a scheduling abstraction, not a SAR-accurate dwell. Note in §7.4 or §5.1.

## Physics correctness — verified

- NESZ ∝ R³ after azimuth compression gain: correct (Curlander ch. 5).
- cos³ξ decomposition cos³ξ = cos³θ_elev·cos³ψ_sq: algebraically correct under the plane geometry; used consistently.
- ρ_rg = c/(2B sinθ), ρ_az = D/(2 cosψ_sq): standard unweighted forms correct.
- r_θ = −0.997 (θ-only), r_ψ = +0.997 (ψ-only), r_null = −0.51: moment factorizations correct given independent uniform θ_elev and ψ_sq.
- Envelope r = −0.97 vs null −0.51: the stronger envelope anti-correlation due to geometric LOS coupling is plausible and well-explained.
- Spherical-Earth incidence mapping θ = arcsin((Re+H)/Re · sinξ) (line 338): formula correct (direction — note this maps off-nadir ξ to target-side θ; the paper states the inverse at line 338, verify direction in code but the *form* is standard).
- Ablation C inertness (θ_elev varies ~1.5° within window vs ψ_sq 20–35°): physically sound.

## Literature placement — assessed

The "no existing SAR scheduling method treats continuous, physics-derived quality functions as decomposed objectives" claim (lines 228–232) is **supported** by the cited prior art: Chang2022 (operational metrics), Wei2025 (composite score), Kramer2025 (visibility-performance composite), ChangZhou2025 (attitude-angle proxy), Wu2019 (coverage/timeliness). The decomposition into separate f2 (geometric) and f3 (radiometric) objectives with closed-form physics is genuinely novel within SAR scheduling. The claim would be stronger with an explicit statement of search methodology (years, databases, keywords) in §2 or a footnote.

## Transferability (§7.3) — sound

f2 → optical GSD (∝ 1/sinθ) transfer is correct. f3 not transferring to optical (illumination/cloud) is correct. The envelope-null-schedule decomposition is the most transferable device and is appropriately highlighted.

## Summary

Physics is correct within disclosed approximations. The main revisions are framing: the 45° squint envelope's effect on operational recommendations (M1), the fact that G-SM beats MOEA-3 on raw f3 at S1 (M2), and an honest accounting of the sinθ omission and θ_elev gap (M3, m1). Add Oliver & Quegan and verify Du-line prior art. Domain contribution: **clear, if narrow** — a negative/empirical-saturation result for decomposed physics objectives in single-pass Stripmap scheduling. Publishable after minor revision.
