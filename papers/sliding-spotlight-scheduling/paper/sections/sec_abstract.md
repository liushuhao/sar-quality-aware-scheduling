# Abstract

Agile Earth-observation satellites that steer a single antenna across stripmap, sliding-spotlight, and spotlight modes are usually scheduled under an exogenous, fixed imaging duration. For a sliding-spotlight platform that assumption fails measurably: planning with the fixed library dwell violates the transfer constraint in 20--29% of consecutive pairs on the dense families, and after repair the replayed plans land 7--30 points of served priority below the endogenous-dwell schedule, the span depending on the repair rule. This paper makes the dwell endogenous: the mode parameters follow the required resolution, the delivered resolution equals it at the selected start by construction --- an identity the solver cannot violate --- and the stripmap antenna floor is the one place a finer requirement genuinely excludes solutions. Served priority is the only objective; image quality is reported, never optimised. Three scenario families sweep a frozen nine-point requirement grid under a frozen mode assignment: the dense family drops 26.0 percentage points to the next tighter point and 46.6 to the tightest feasible one (the stripmap floor accounting for 20.0 and 44.8 of those points), the all-stripmap control becomes infeasible at the tightest point, and the family without stripmap stays within 0.27 points of its as-placed coverage at every tighter point. Loosening recovers 4.15 and 2.36 points (0.93 paired per seed). Which mode a task receives decides what a requirement change costs; the families differ in task count and mode mix together, so the cross-family contrast is an observation, not an attribution.

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
