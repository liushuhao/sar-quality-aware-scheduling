# R3 — Cross-Disciplinary / Operations Perspective

**Paper:** Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite (ASR submission)
**Lens:** OR / mission-operations / practical impact / fundamental assumptions
**Data integrity:** pre-gate passed, not re-audited.

---

## Recommendation: **MINOR REVISION**

The core empirical finding (density-dependent saturation of physical objectives under G-BL-seeded NSGA-III) is internally honest and adequately caveated in §7.4. The cross-disciplinary problems are about **operational linkage and claim breadth**, not scientific validity. None block publication, but the ~0.3 m operational number is under-justified and the "saturation boundary" is framed more broadly than the single-configuration experiment supports.

**Impact score: 62 / 100** — rigorous niche contribution; operational value is asserted more than demonstrated.

---

## CRITICAL

None.

---

## MAJOR

### M1. Operational resolution number not tied to measured gain (§7.2, ~line 1247)
> "...a few-percent resolution improvement ($\sim$0.3 m at C-band: $\rho_{\text{rg}} \approx 5.3$ m at $\theta=30^\circ$) may affect whether adjacent targets within the same pixel are resolved..."

The arithmetic for the baseline is correct: $c/(2B)=3\!\times\!10^8/(2\!\times\!56.5\!\times\!10^6)=2.66$ m slant-range; $\sin30^\circ=0.5$ gives 5.3 m ground-range. But the **0.3 m improvement is not derived**. At S1, $f_2$ rises from 0.295 to 0.394 (+34%). Since ground pixel area $\propto 1/f_2 = 1/(\sin\theta_{\text{elev}}\cos\psi_{\text{sq}})$, a +34% index corresponds to ~25% smaller pixel area and ~13% smaller linear dimension — on a 5.3 m ground-range that is ~0.7 m, not 0.3 m, before accounting for the azimuth component and the fact that actual S1 geometry is not $\theta=30^\circ,\psi=0$.

The sentence reads two ways, both problematic:
1. If 0.3 m is the *measured* S1 gain, it is inconsistent with +34% $f_2$.
2. If it is an *illustrative* "few percent matters" number at a reference geometry, it is unconnected to the reported MOEA gain and misleads the reader into thinking the sparse-regime benefit is only ~5%.

**Fix:** Either (a) compute the actual ground-range/azimuth resolution improvement at S1 from the solver-produced $\theta,\psi$ distributions and quote that, or (b) rewrite as an explicitly illustrative statement decoupled from the +34% result: e.g., "at $\theta=30^\circ$, a 5% change in ground-range resolution is ~0.27 m, which can be decisive for sub-pixel target separation; the MOEA-2 gain reported above is substantially larger in the $f_2$ index but maps nonlinearly to metric resolution." Do not leave 0.3 m orphaned.

### M2. Timeliness motivates the paper but is not an objective or a result
Introduction (line 70) opens on "time-critical monitoring missions, from disaster response to maritime surveillance." §7.4 concedes "time-critical monitoring motivation ... is addressed only indirectly, through earliest-feasible placement." No latency, revisit, or deadline-miss result is reported anywhere.

For an operations-focused ASR readership this is a real "so what?" gap. G-BL's earliest-feasible placement is *plausibly* timely but never quantified (mean acquisition time relative to window open? deadline satisfaction? time-to-last-task?). The operational recommendation ("dense $N\geq300$: use G-BL") rests on coverage + quality, with latency asserted by mechanism rather than measured.

**Fix:** Add one paragraph in §7.2 reporting a simple timeliness diagnostic for G-BL vs MOEA variants — e.g., mean/90th-percentile offset of $t_{s_k}$ from $a_{s_k}$ or fraction of tasks acquired in the first half of their window — even if only on a subset. If that is infeasible pre-submission, soften the Introduction's disaster/maritime framing to "agile Earth observation" and state explicitly that latency is out of scope.

### M3. "Empirical saturation boundary" is broader than the evidence
The term appears in abstract (line 57), contribution 1 (line 139), and conclusion (line 1362). The experiment holds fixed: single satellite, single pass, Stripmap, 693 km orbit, 30 s dwell, $45^\circ$ squint envelope, C-band, G-BL seed, one algorithm family. §7.4 lists all of these as limitations, but the boundary language in the abstract/conclusion does not carry a scoping qualifier. A "boundary" suggests portability; what is shown is a saturation *observation under one configuration*.

**Fix:** Add a scoping qualifier at first and last use: "an empirical saturation boundary **for the single-pass, single-satellite Stripmap configuration tested**" (abstract), and mirror in conclusion. Keep §7.4 as-is.

### M4. G-BL anchor is not a coverage optimum, yet dense-regime sufficiency is judged against it
§6.4 notes one sparse scenario where a MOEA solution reaches $f_1^*=1.108$ (+10.8% above G-BL), proving G-BL is not a strict coverage anchor. At dense N, all MOEAs converge to $f_1^*\approx1.00$, which the paper reads as "greedy is sufficient." But normalization against a non-optimum cannot establish sufficiency — only that the tested MOEA family does not beat *this* greedy. The "tested family's coverage ceiling" phrasing (line 134, 1264) hedges correctly in places; other places (abstract line 48, §7.2) drop the hedge.

**Fix:** (a) Consistently say "the tested family's coverage ceiling" not "the coverage ceiling." (b) Add an external reference for the dense-regime coverage level — a LP relaxation of the profit-maximization ignoring C2 attitude coupling, or a time-budget upper bound $\sum_i p_i \mathbf{1}[\text{window exists}]$ — so "G-BL ≈ 1.00" is compared to an absolute ceiling, not to itself. Even a loose upper bound would let the reader judge whether 1.00 is near-optimal or merely the best-of-tested.

### M5. C3 (energy) and C4 (memory) never bind
§3.3 (line 486): $E_{\max}=10^7$, $M_{\max}=10^{11}$, "set sufficiently high to be non-binding under all tested scenarios." A four-constraint formulation in which two constraints are mathematically inactive is, for an operations audience, decorative — real SAR scheduling is frequently downlink- or energy-bound. Including them without a binding scenario risks a reviewer reading the model as more operationally complete than it is, and inflates the "C1–C4 all zero" audit into a stronger statement than it is (zero violations of an infinite cap is trivial).

**Fix:** Either (a) move C3–C4 to a "modeled but inactive" footnote / appendix and state the resource-unconstrained regime explicitly up front (§7.4 already says this — move it forward), or (b) add one resource-tightened condition showing where saturation behavior changes (acknowledged as future work if infeasible). Option (a) is sufficient and honest.

---

## MINOR

### m1. $f_2$/$f_3$ unweighted means ignore priority
$f_1$ uses priority weights $p_i$; $f_2,f_3$ are unweighted means (line 391). For operational use, mission planners care whether *high-priority* targets get good geometry, not whether the average geometry is good. A schedule could improve mean $f_2$ by shifting good geometry onto low-priority tasks. Add a one-sentence limitation, or a priority-weighted sensitivity in §6.6.

### m2. No wall-clock despite ops recommendation
§5.2 says runtimes are not reported. The dense-regime recommendation ("use G-BL") is partly a latency argument (line 1268: "latency-favorable") but no runtime is given. Even per-scenario medians (greedy ms vs MOEA minutes, already stated qualitatively) would substantiate the claim. One line of numbers.

### m3. Transferability section is one paragraph (§7.3)
The cross-domain claim ("$f_2$ transfers to optical, $f_3$ does not; the envelope–null–schedule decomposition transfers") is plausible but unsupported — no optical geometry cited, no reference to optical GSD scheduling literature. For a paper that lists cross-disciplinary perspective as a contribution axis, one paragraph is thin. Either shorten the claim to "we expect the decomposition to transfer" or add 2–3 sentences with one optical-scheduling citation.

### m4. Bilateral side-flip feasibility under C2
Scenarios are 50/50 left/right windows (line 669). C2 enforces angular separation between consecutive LOS vectors, but a left→right flip is a large slew ($2\theta$ ~ 36–94°) that may not be physically achievable within the inter-observation gap even if $\omega_{\max}$ is a single-axis bound. The paper does not report whether selected schedules actually mix sides or cluster on one side, nor whether the "conservative" $\omega_{\max}$ is realistic for cross-axis maneuvers. If schedules cluster single-side, the bilateral configuration contributes less diversity than claimed; if they flip, the maneuver model deserves validation. Report per-schedule fraction of side switches and confirm $\omega_{\max}$ covers cross-nadir slews.

### m5. N=20 operational relevance
The headline +34%/+41% gains are at $N=20$, which is sparse even for reconnaissance (1–2 windows/target, 15.6/20 selected). The 14–15% coverage cost at N=20 is a meaningful loss. Frame the sparse regime as "low-demand scheduling" rather than implying general sparse relevance; the S2 ($N=100$) numbers (+3.5% $f_2$, +1% coverage cost) are the more operationally interesting transition point.

### m6. Comparison-set caveat
No MOEA/D, SMS-EMOA, or learning-based baseline. This is acceptable given the negative-result framing and explicit future-work statement (line 522, 1325), but the abstract's "rather than identifying a superior solver" should read "rather than identifying a superior solver **within the tested NSGA-III/greedy family**." One clause.

### m7. S7/S8 scope asymmetry
S7 ($N=150$) and S8 ($N=200$) were run only for MOEA-2 and the two greedy baselines, not MOEA-3 or GA-P-BL (line 657). The logistic $N_{50}\approx50$ fit uses six points, four of which are at zero deficit. The asymmetry is disclosed but the scale-sensitivity figure/table should visually mark that S7/S8 are partial-family points, so a reader does not assume the full five-solver comparison at those densities.

---

## Observations (non-defects)

- The honesty about G-BL-seeded dependence (§6.6), HV point-count confounding (§6.4), plane-Earth approximation error (§2.2), and "not a mathematical identity" is a genuine strength and should not be cut under de-AI pressure.
- The envelope–null–schedule $r=-0.97 \to -0.63 \to -0.15$ progression is the most transferable idea in the paper; it deserves more prominence in the abstract relative to the solver comparison.
- The "Pareto-sufficient" definition in §7.1 that trivially labels every solver sufficient is correctly discarded; the paper is better for acknowledging it rather than hiding it.

---

## Top fixes for the editor

1. Derive or decouple the 0.3 m number (M1).
2. Add one timeliness diagnostic or soften the disaster/maritime motivation (M2).
3. Scope "saturation boundary" to the tested configuration (M3).
4. Add an external coverage reference for the dense regime (M4).
5. Reclassify C3/C4 as inactive rather than as constraints (M5).
