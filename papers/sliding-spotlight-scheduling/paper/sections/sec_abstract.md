# Abstract

Agile Earth-observation satellites that steer a single antenna across stripmap, sliding-spotlight, and spotlight modes are usually scheduled under an exogenous, fixed imaging duration. For a sliding-spotlight platform that assumption fails measurably: planning with the fixed library dwell violates the transfer constraint in 20--29% of consecutive pairs on the dense families, and after repair the replayed plans land 7--30 points below the endogenous dwell, the span depending on the repair rule. This paper makes the dwell endogenous and derives the mode parameters from the required resolution: for sliding spotlight and spotlight the delivered resolution equals the requirement at the selected start by construction --- an identity the solver cannot violate --- while the stripmap tier stays at its antenna floor, the one place a requirement genuinely excludes solutions. Served priority is the only objective; image-quality readings are reported, not optimised. A frozen nine-point demand grid scales every requirement from 0.8 to 2.0; three shape criteria registered before this scenario set's data were read (the main-result form itself was registered afterwards) are reported with their failures. Tightening is where coverage moves: the dense 100-task family drops 26.0 percentage points from the as-placed requirement to the next point down and 46.6 points to the tightest feasible point, with the stripmap floor accounting for 20.0 and 44.8 of those points; the all-stripmap control drops 46.0 points at $s=0.9$ and becomes infeasible at $s=0.8$; the 50-task family stays within 0.27 points of its as-placed coverage at every tighter point. Loosening from the as-placed point recovers 4.15 percentage points for the 100-task family against its own saturation and 2.36 points for the 50-task family (0.93 points as the paired per-seed median; the statistics diverge because several seeds saturate at the loose end). Which mode a task receives decides what a requirement change costs; because the three families differ in task count and mode mix together, the cross-family contrast is reported as an observation rather than an attribution, and all conclusions are scoped to requirement sensitivity under this fixed mode assignment.

# Nomenclature

| Symbol | Meaning | Symbol | Meaning |
|---|---|---|---|
| $A$ | sliding factor ($=r_0/(R_0+r_0)=1-k$) | $A_{\mathrm{task}}$ | task-level sliding factor |
| $D$ | antenna azimuth length | $k$ | rotation-centre parameter |
| $R_0$ | aperture-centre slant range | $r_0$ | rotation-centre-to-scene-centre distance |
| $v_s$ | inertial scene velocity | $T$ | dwell duration (SAT) |
| $\rho_a$ | azimuth resolution | $\rho_{\mathrm{rg}}$ | ground-range resolution |
| $\rho_{\mathrm{req}}$ | required azimuth resolution | $\rho_{a,\mathrm{ach}}$ | squint-achieved azimuth resolution |
| $g_T$ | dwell-gain ratio | $f_q$ | quality index |
| $f_1$ | served priority fraction | $s$ | demand-tightening factor |
| $\tau$ | start-time fraction gene | $t_{\mathrm{man}}$ | maneuver time |
| $d_\psi$ | inter-task squint difference | AASR | azimuth ambiguity-to-signal ratio |
| PRF | pulse repetition frequency | NESZ | noise-equivalent sigma zero |
| STR/SLS/SPT | stripmap / sliding spotlight / spotlight | SAT | synthetic-aperture time |
| C1--C5 | constraint families (Section 3.4) | S1--S3 | frozen shape criteria (Section 5.3) |
