# 6. Results and Analysis

All readings in this section are taken from the highest tier of the promoted artifacts (160/240 population/generations) and carry the NOT-PLATEAUED qualifier where frontier richness is stated; the 40/60 base tier is retained only as an under-converged baseline and is never read as a result.

## 6.1 Primary stratum results

The primary stratum for the quality-headroom test is the R2F+R3H pooled stratum, a registered adjudication adopted before the runs; R1C is demoted to a single-orbit control and is read descriptively only. Two registered facts motivate the demotion: the R1C quality axis operates on a different scale from the pooled families (the per-family domains of Section 5.2 are separated by up to two orders of magnitude), and the power design covers R2F/R3H only;

The asymmetry is reported as registered. At the top budget the R2F power is 0.92 at the registered δ, so R2F may claim the test; the R3H power is 0.29, and R3H's outcome is therefore reported as not reaching significance at $n=10$ --- the honest reading of a design whose seed anchor (R3H would need 54 seeds for 80% power) was registered as a cost anchor, not a plan. What the test does *not* constrain is the structural axis: ALIVE and DEAD verdicts on the model-level bound below are structural statements, and a family can be structurally ALIVE while failing to reject at this $n$.

## 6.2 Promotion, two axes

The promotion verdict is stated on two separated axes, and the separation is the result.

**Structural axis (model-level).** The real-window structural spread $R_{fam}$ --- the model-level AASR range attainable across each family's windows, recomputed under the rotation-centre (ticket-40) caliber --- is 3.9998 dB for R1C and 8.74/10.91 dB for R2F/R3H (Fig. 5a). R1C is therefore STRUCTURAL DEAD: its base-seed reading and its reading at every one of the ten seeds sit at or below 3.9998 dB (the weakest seed reads 3.9968 dB), all under the 6.0 dB threshold, so the verdict does not depend on which seed is read; its greedy anchor saturates the served fraction at 1.0 in every unit, its front is a pure quality trade-off surface, and that is exactly why it serves as the control. R2F and R3H are descriptively ALIVE at the model-level structural bound. Two disclosures attach. First, "ALIVE" is a model-level statement about what the scenario admits; it does not mean promotion fires, does not mean any readout has converged, and licenses no physical claim. Second, the knife-edge margin often quoted near promotion verdicts --- 0.499 dB, i.e. a 5.501 dB reading one half-dB under the line --- belongs to the synthetic P8WH family of the earlier calibration; R1C's own margin is 2.000 dB, and the two numbers are never interchangeable.

**Reading axis.** Over all 90 units (3 families × 3 budget tiers × 10 seeds) the promotion decision is no_promotion everywhere, with a maximum spread of 3.9722 dB against the frozen 6.0 dB threshold (Fig. 5b). The no-promotion verdict is robust across the 16× budget ladder and may be cited as a structural reading with its budget evidence attached. The axes must not be merged: structural ALIVE is not a prediction that promotion triggers, and the 90/90 reading-axis outcome does not contradict the structural verdict.

## 6.3 Convergence verdicts and budget tiers

Convergence was calibrated under a preregistered rule frozen before the two additional budget tiers were run. Both treatment families carry the SEARCH-ARTIFACT verdict, and both disclosures are of falsified readings, not assertions.

For R3H the base-budget picture --- 6 of 10 seeds ending at a single-point front (median 1) --- inverts completely under the ladder. At the 160/240 top budget the R3H median front size is 140, and the median distinct-fq count is 99. The apparent collapse was judged a search artifact by the preregistered rule, and the verdict names the mechanism: running a 40×60 budget against 200 decision variables. Any physical-collapse narrative built on the base budget is withdrawn, in both directions; for R2F the same rule fires more mildly: the ladder takes the median front size from 19.5 to 84.5 and the median distinct-fq count from 14.5 to 64.5 (a 4.4× rise), so the base-budget reading there was likewise an artifact of budget, not a property of the scenario (Fig. 4).

Neither family has satisfied the plateau rule: between the middle and the highest tier the R3H median distinct-fq count still rises from 26 to 99, so both families are reported as still rising monotonically at the top budget (NOT-PLATEAUED). The converged true front remains unknown, and any frontier-richness bound is forbidden in both directions at this budget. The H/W observation item --- whether higher-density fronts widen trivially --- is settled by the same close-out verdicts: whatever widening appears is a property of the search budget, as the ladder demonstrates, not of the scenario density.

![fig-4 Budget-ladder convergence](figures/fig4_budget_ladder.pdf){#fig:4}

**Caption (fig-4).** Median front size (left) and median distinct-fq count (right) across the three registered budget tiers, real-window v3 caliber, CV-filtered fronts, 10 seeds per point. Solid: R2F; dashed: R3H. Both families are still rising at the highest tier (NOT-PLATEAUED): no frontier-richness bound is implied in either direction, and the lowest-tier readings are under-converged baselines only.

## 6.4 Per-mode quality decomposition

The second objective is fully explained by the mode library. At the zero-squint library caliber the per-mode f_q constants are 0.8107 (STR), 19.7352 (SLS), and 54.8322 (SPT) $m^{-2}$: magnitude ratios of 24.3× (STR:SLS), 67.6× (STR:SPT), and 2.8× (SLS:SPT). Because the squint factor cancels inside the gain term (exactly for STR/SLS, to within 0.07% for SPT across the full envelope; Fig. 3), these constants --- not squint-dependent readings --- are what the second objective trades against, and the per-mode decomposition is its whole explainability carrier (Fig. 6).

![fig-3 Per-mode f_q versus squint](figures/fig3_quality_vs_squint.pdf){#fig:3}

**Caption (fig-3).** Per-task f_q versus beam-centre squint for the three library modes, evaluated through the frozen platform fixture at the zero-squint library caliber (non-normalised, $m^{-2}$). The levels are flat by design (D05-4): solid STR 0.8107, dashed SLS 19.7352, dash-dot SPT 54.8322 $m^{-2}$; the SPT drift across the full envelope is +0.067%. The separation of the levels, not their slopes, is what the second objective responds to.

Mode composition differs sharply by family: every R1C task routes to STR (20/20), R2F splits 16 SLS / 30 SPT (no STR), and R3H mixes all three (54 STR / 15 SLS / 30 SPT). The decomposition --- mode share × mode constant --- is drawn in Fig. 6.

![fig-6 Per-mode f_Q decomposition](figures/fig6_per_mode_decomposition.pdf){#fig:6}

**Caption (fig-6).** Per-family decomposition of the second objective into mode contributions (share of tasks routed to each mode, from the promoted scenario manifests, × the zero-squint library constant; real-window v3 caliber, non-normalised $m^{-2}$). R1C is single-mode (STR) by construction of the control; R2F and R3H mix modes with different weights. The decomposition is a model-level explanatory vehicle (D05-4/D05-8), not a per-solution statistic.

A required disclosure on double weighting (D05-5). The quality aggregate is weighted twice by construction, and both weightings must be stated together. First, the mode mapping embeds an implicit priority weighting of the requirement: finer requirements route to finer modes, which pay longer dwells, so the $f_1$--$f_Q$ trade-off is real rather than an artifact of the quality formula. Second, the antenna gain term adds an effective $\rho_a^2$ azimuth weighting on top of that. Stating only the first is the documented failure mode; the two together are what the second objective responds to.

## 6.5 Coverage parity

The coverage axis is a constructive parity outcome, not a hypothesis test. The dense-domain construction guarantees the per-node serviceability criterion by design (Section 5.1), and the registered construction lands 49/50 of the served-fraction comparisons on the same side, so a significance test on coverage has no power by construction. We therefore report coverage as what it is --- a construction product inherited by every run --- and make no claim of the form that coverage passed or failed in any branch.

![fig-5 Promotion two-axis verdict](figures/fig5_promotion_two_axis.pdf){#fig:5}

**Caption (fig-5).** The promotion verdict on its two separated axes. (a) Structural axis, model-level only: recomputed $R_{fam}$ per family under the registered rotation-centre caliber from the promoted scenario manifests (3.9998 / 8.74 / 10.91 dB, base seeds; live recomputation reproduces the registration bit-for-bit), against the frozen 6.0 dB threshold. R1C is STRUCTURAL DEAD; R2F/R3H are descriptively ALIVE at the model-level bound. (b) Reading axis: raw per-unit promotion outcomes for all 90 units (3 families × 3 tiers × 10 seeds, real-window v3 caliber); every unit is no_promotion; the largest reads 3.9722 dB. The axes are not merged: (a) never predicts (b).
