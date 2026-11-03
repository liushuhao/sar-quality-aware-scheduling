# Perspective Review — paper1

## Canary
1. Read-only: I must not modify, create, or delete any file except my one report file.
2. Every finding quotes the exact manuscript text it criticizes, with section name and approximate tex line number.
3. No fabricated facts: I never assert what a cited reference contains beyond what the manuscript itself claims.
4. Numbers: quoted exactly as printed; no recomputation or correction.
5. No network access.
6. Genuine strengths and weaknesses; no manufactured findings, no quotas.
7. Stdout is at most 5 lines; the report goes to the file.

## Summary judgement
The paper does the hard part of an applications contribution better than most: it states
its boundaries (squint envelope, density, horizon) and it measures two of them with
controlled sweeps instead of asserting them. The transferability limit, however, is not
the one the paper advertises. What an operator of a different constellation, band or mode
must redo is not "re-run the ablation" but "re-derive the baseline": every headline
percentage is a ratio to an earliest-window greedy that never looks at the priority
weights, so the reported value of quality-aware scheduling is measured against a
benchmark no planning team would field, and the reported "coverage cost" is a weighted
sum whose task-level composition is never shown. Operationally the objectives are
meaningful in kind (resolution, NESZ) but the decision they sit in is thin: a two-orbit
horizon, one observation per target, a 30 s fixed dwell, an invented 200-task resource
ceiling, no latency, no downlink, and a wide-squint platform that the manuscript itself
notes operational systems would yaw-steer away from. The "so what" is real but narrower
than the highlights claim, and it competes with a two-step heuristic (squint-minimised
placement plus greedy backfill) that the paper never tests.

## Strengths
- The boundary work is genuine: "repeating the sparse $N=20$ configurations with the
  window-generation squint cap reduced from $45^\circ$ to $25^\circ$ and $15^\circ$ ...
  shows that the multi-objective edge contracts monotonically with the envelope"
  (§7.2, ~L1398-1405). This is the kind of platform-parameter sensitivity an operations
  reviewer asks for and rarely gets.
- Controls against the obvious confounds are present and adversarial to the authors'
  own thesis: "Random-initialized MOEA-2 loses $0.393 \pm 0.251$, $0.551 \pm 0.060$,
  $0.684 \pm 0.050$, and $0.475 \pm 0.067$ in $f_1^*$ at S1--S4 relative to hot-start
  MOEA-2" (§6.6, ~L1260-1262); that result weakens the headline and is reported anyway.
- The proxy nature of $f_3$ is disclosed with a number, not a hedge: "Recomputing the
  sparse-regime comparison of \S\ref{sec:overall-performance} with the retained factor
  enlarges the MOEA-3 gain over G-BL from $+40\%$ to $+94\%$ ... the proxy reading is
  conservative" (§3.2, ~L433-437).
- The single algorithmic shortcut is conceded rather than buried: "this gain comes from
  the one-line squint-minimization heuristic rather than from multi-objective search"
  (§7.2, ~L1395-1396).
- The data-availability and AI-use statements are complete for an Elsevier submission,
  and the limitations section enumerates caps, dwell time and static targets rather than
  leaving them for the reader to discover (§7.4, ~L1490-1498).

## Findings

### R3-01 [MAJOR] The baseline ignores the objective it is scored on
- Quote: "Tasks are sorted by earliest start time $t_{\text{start}}$ and greedily
  inserted into the schedule at their earliest feasible time." (§4.2, ~L612-613)
- Problem: $f_1$ is a priority-weighted sum (Eq. 1), but G-BL orders tasks by window
  start time and never reads $p_i$. That is not a description of operational practice —
  a planning team sorts by priority, by value-per-opportunity, or by deadline. Every
  headline ratio in the paper ($+33.7\%$ in $f_2$, $+40\%$ in $f_3$, the "$14\%$" and
  "$15\%$" coverage costs, the $N_{50}$ crossing) is a ratio to this baseline, so the
  reported value of quality-aware scheduling is measured against a benchmark that is
  weak in precisely the dimension the paper is about. A priority-first greedy would very
  likely land between G-BL and MOEA on the coverage axis, shrinking the coverage cost
  and, with it, the apparent price of quality.
- Why this is not settled by GA-P-BL: that control "makes GA-P-BL output numerically
  identical to G-BL in 199 of 200 scenarios" (§4.3, ~L658-659). The paper reads this as
  confirming the baseline. It supports two incompatible readings — G-BL is near-optimal
  for $f_1$, or the single-objective GA cannot search this space — and the paper does not
  discriminate them. If the second, the MOEA gains may reflect the diversity pressure of
  extra objectives rather than search power.
- Fix: add a priority-first greedy (sort by $p_i$, or by $p_i$ divided by window slack)
  as a sixth configuration and re-express the sparse-regime table against it. Report the
  GA-P-BL / G-BL coincidence as a search-diagnostic with a stated explanation.

### R3-02 [MAJOR] "Coverage cost" never says which targets are sacrificed
- Quote: "MOEA-3 raises $f_3$ by $+40\%$ ($0.698$ vs.\ $0.497$) at a $15\%$ coverage cost
  ($f_1^* = 0.85$)." (§6.1, ~L885)
- Problem: 15% of a priority-weighted sum can mean dropping the lowest-priority tail of a
  uniform $\{1,\dots,10\}$ draw (a cheap trade) or dropping scarce high-value targets (an
  expensive one). The manuscript never reports the priority composition of the dropped
  set for the main comparison; the only such evidence is the ablation's $f_1/n$ column
  (A $5.99$ vs.\ D $5.65$ at S1, §6.5). An operator reading the abstract cannot price the
  trade, which is the one number they actually need.
- Fix: add mean and distribution of $p_i$ over dropped tasks per solver and class to
  Table 2 (one extra column each), and restate the headline as e.g. "gives up the
  priority-1-3 tail" or "gives up 2 of the 5 top-priority targets". Note also that
  priorities are already heterogeneous at $\{1,\dots,10\}$; what the limitations mean by
  "heterogeneous priorities" (§7.4, ~L1475) is a *skewed* demand profile, and that is the
  sensitivity worth running.

### R3-03 [MAJOR] "Operational densities" is a synthetic ceiling wearing an operational word
- Quote: "It vanishes at operational densities: beyond $N \approx 150$ the found fronts
  converge to the greedy coverage anchor with quality margins below $2\%$." (Conclusion,
  ~L1528-1530)
- Problem: the ceiling is invented — "where $E_{\max}=10^7$ and $M_{\max}=10^{11}$
  (arbitrary units)" (§3.3, ~L559-560), and both caps resolve to 200 tasks, binding in
  20 of 50 G-BL schedules at S3 and 27 of 50 at S4. Above 200 targets no solver can image
  more than the cap, so convergence at $N=300$ and $N=500$ is partly arithmetic. The
  horizon is two orbits (~200 min) with at most one look per target, so $N$ itself is not
  a quantity an operator of a different orbit family can transfer.
- Fix: either show $N_{50}$ under a second resource ceiling (e.g.\ 300 or 500 tasks) and
  a longer horizon to demonstrate the boundary is not an artifact, or relabel it
  "within the tested 200-task, two-orbit envelope" everywhere including the highlights,
  and express density in transferable units (targets per access window, or per hour).

### R3-04 [MAJOR] The enabling platform is hypothetical, and the paper's own Doppler numbers say operational systems remove the mechanism
- Quote: "the Doppler centroid $f_{\text{dc}} \approx (2v/\lambda)\sin\psi_{\text{sq}}$
  (of order $10^2$\,kHz at the scheduled $16$--$24^\circ$ squints, versus a PRF of order
  $10^0$--$10^1$\,kHz, large enough that operational Stripmap systems employ yaw
  steering, with Doppler-centroid tracking handling the residual" (§3.3, ~L521-525)
- Problem: the entire value proposition rides on the squint axis — the ablation shows the
  incidence component is inert (R3-07) — and yaw steering is precisely the mechanism that
  nulls squint in the antenna frame. The paper acknowledges this in a parenthetical and
  then states "absolute performance claims for platforms without Doppler compensation at
  large squint are out of scope", followed later by the conditional "on platforms with
  $|\psi_{\text{sq}}| \lesssim 25^\circ$ agility, or without Doppler-centroid compensation
  for large squints ... the greedy baseline attains comparable quality at full coverage"
  (§7.2, ~L1414-1416). That is a large concession buried in §7. For an applications
  journal, the first question a reader asks is whether their spacecraft has a $45^\circ$
  squint envelope; the manuscript answers "This bound is an experimental setting, not a
  claim about any specific platform's demonstrated operating mode" (§3.3, ~L505-507).
- Fix: put the operational prerequisite in the abstract and highlights ("wide-squint,
  Doppler-compensated platform"), and add one paragraph placing the tested envelope
  against published SAR system parameters so a reader can locate their own platform.

### R3-05 [MAJOR] Quality is scored at an instant; the image integrates over a dwell in which geometry moves as much as between candidates
- Quote: "a 0.5\,s-resolution scan of all 76{,}190 windows across the four density
  classes reports zero violations; the median change of squint over any 30\,s
  within-window sub-interval is $11^\circ$, 95th percentile $15^\circ$" (§5.1, ~L764-767)
- Problem: $f_2$ and $f_3$ are evaluated at one acquisition time, but a 30 s Stripmap
  aperture integrates over an $\sim 11^\circ$ squint excursion — while the solver's
  decision grid is 10 s and the ablation reports within-window squint sweeps of
  $\sim 20$--$35^\circ$. A decision margin of a few degrees of squint is therefore being
  optimised inside a band of variation of the same order. This does not invalidate the
  ranking, but it sets its resolution, and the paper reports the number without drawing
  the consequence.
- Fix: state the error explicitly — e.g. score each candidate at mid-dwell and over the
  dwell endpoints, and report how many schedule-level rankings change. At minimum, say in
  §3.2 that the objective is a mid-dwell point estimate inside a $\pm 5$--$7^\circ$ band.

### R3-06 [MINOR] Mean-versus-priority decoupling is a modelling choice with an operational cost
- Quote: "The quality indices are unweighted means over the scheduled set, orthogonal to
  the priority weights used in $f_1$: they reflect the average imaging geometry of the
  selected tasks rather than biasing quality toward high-priority targets." (§3.2, ~L392-394)
- Problem: the choice is defended as a design feature and it does buy a clean
  quantity-versus-quality frontier, but it means a non-dominated schedule can improve the
  reported quality by degrading the images of the top-priority targets. A mission
  commander's preference runs the other way.
- Fix: report one priority-weighted quality column as a sensitivity check; if the
  frontier ordering is unchanged, one sentence closes the objection.

### R3-07 [MINOR] The incidence objective carries no solver behaviour; the three-objective framing overstates the active dimensionality
- Quote: "Variant C (no incidence) produces no measurable change in any reported metric."
  (§6.5, ablation ~L128-129)
- Problem: with $\theta_{\text{elev}}$ varying "by only a few degrees across a visibility
  window (mean $\sim 1.5^\circ$)", the only axis the scheduler can steer on is squint.
  The paper explains this correctly (the incidence effect is compositional, across
  windows) but the contribution statement and abstract still present a three-dimensional
  objective space in which the third physical dimension does work. For a reader deciding
  whether to adopt the formulation, the honest summary is "two quality metrics, one of
  which drives timing decisions".
- Fix: say this in the contribution list and the abstract: squint is the operative axis,
  incidence is a schedule-composition weighting. It costs nothing and buys credibility
  with anyone who would otherwise try to reproduce a $\theta$-driven gain and fail.

### R3-08 [MINOR] The cheapest competitor to NSGA-III is never tested
- Quote: "this gain comes from the one-line squint-minimization heuristic rather than
  from multi-objective search" (§7.2, ~L1395-1396)
- Problem: G-SM alone loses too much coverage ($f_1^*=0.51$ at S1), and MOEA-3 keeps it
  ($0.85$). The practitioner's obvious middle path — squint-minimised placement for the
  tasks you keep, then greedy priority backfill of the remaining capacity — is not among
  the five configurations, and it plausibly lands close to MOEA-3 on both axes. Given the
  measured run time of "$22$\,s (S1), $66$\,s (S2), $220$\,s (S3), and $260$\,s (S4)"
  (§5.2, ~L770), the operational argument for NSGA-III has to be quality, not speed.
- Fix: add the two-step hybrid as a sixth configuration; if it reaches, say, two-thirds of
  the MOEA quality gain at full coverage, that is itself a useful, publishable finding.

### R3-09 [MINOR] Two contradictory statements about hypervolume
- Quote A: "Because HV rewards front cardinality as well as front quality, these rankings
  are interpreted only as secondary diagnostics" (§6.1, ~L966-967).
  Quote B: "HV rewards an extreme single point and is insensitive to cardinality: every
  single-objective solver contributes one point per scenario" (§6.4, ~L1222-1224).
- Problem: the two sentences say opposite things about cardinality. Both are defensible
  in different senses (HV is monotone under set inclusion, and also dominated by a
  single extreme point), but as written an MOO reader will take them as an inconsistency,
  and the paper's whole defensive posture on HV (G-SM 0.2341 above MOEA-3 0.0893) depends
  on which statement is true.
- Fix: one sentence defining the sense in which each holds, stated once and referenced.

### R3-10 [MINOR] The null model spans a factor of two, and the interpretation is anchored on one end
- Quote: "A permutation null that shuffles the visibility-window-grid
  $\theta_{\text{elev}}$ and $\psi_{\text{sq}}$ marginals within each density class gives
  $r_{\text{null}} = -0.60$ to $-0.62$ across classes ... and Monte Carlo sampling over
  the uniform box gives $r_{\text{MC}} = -0.28$" (§6.4, ~L1111-1116)
- Problem: three defensible nulls give $-0.28$, $-0.36$ (envelope) and $-0.60$. The
  interpretive sentence "Sparse schedules therefore recover the independent-angle conflict"
  is true only against the $-0.60$ null; against the envelope value the $-0.62$ is
  stronger than the null, which would make sparse schedules an over-conflict regime. The
  authors choose the empirical-marginal permutation null for stated reasons, and that is
  legitimate, but the reader cannot see how much of the story depends on the choice.
- Fix: give the conclusion under all three nulls in one sentence and say which parts
  survive.

### R3-11 [MINOR] Reproducibility: an unresolved tension and two availability channels
- Quote: "the NSGA-III sampling seed is fixed at the library default while operator-level
  random draws are not pinned, so within-instance search stochasticity is not replicated"
  (§5.1, ~L850-853), against "five repeats of each NSGA-III solver on one variant-A
  scenario per class reproduce bit-identically at S1 and S4" (~L854-856).
- Problem: "not pinned" and "bit-identically" are only compatible if the library default
  determines every draw, which the text does not state; and the claim covers one scenario
  per class. An engineering team adopting the method needs a stated tolerance, not a
  binary. The Data Availability statement compounds this: "available from the corresponding
  author. The companion repository is publicly available at [URL]" — two channels, and
  "Generated binary scenario files and per-run pickle objects are not tracked".
- Fix: state one reproduction target — command, scenario id, expected output, tolerance —
  and pick one availability channel.

### R3-12 [MINOR] Highlights overstate the third objective's measured contribution
- Quote: "Third objective adds +40\% (NESZ-ordering index) at sparse density, 15\%
  coverage cost" (highlights.tex, bullet 3)
- Problem: $+40\%$ is MOEA-3 versus G-BL overall (§6.1, ~L885), not what adding the third
  objective buys. The controlled third-objective margin is $+4.9\%$ under the matched
  radiometric-aware rule (§6.4, ~L1196-1197), with $+0.05\%$ under a radiometric-blind
  rule. As written, the highlight is a stronger claim than the body supports, and it is
  the sentence most readers will retain.
- Fix: "+4.9\% controlled margin from the third objective" or attribute the 40% to
  three-objective scheduling versus greedy.

## Suggested references (candidate gaps only)
- Operational SAR mission-planning practice and ground-segment tasking (how real
  planning teams order requests): needed to justify or replace the earliest-window greedy
  as the conventional baseline (R3-01).
- Priority/value models and timeliness in Earth-observation tasking (value of information,
  deadline and urgency weighting): would let the paper price the coverage loss rather than
  expressing it as a weighted-sum percentage (R3-02).
- Preference articulation and knee-point selection in many-objective optimisation: the
  equal-weight normalised-sum knee is one of several defensible rules; citing the
  alternatives would strengthen §5.3 (R3-09).
- Squint and Doppler-centroid compensation in operational SAR (yaw steering, Doppler
  tracking): needed to place the $45^\circ$ envelope in a real platform family (R3-04).
- Multi-pass and constellation scheduling with quality objectives: the paper's own
  transferability claim would be better grounded with the closest prior work in that
  regime (R3-03, §7.4).

## Recommendation signal
**Major Revision.** Three conditions would move my verdict to Minor:
1. Add a priority-first greedy baseline and re-express the sparse-regime headline gains
   against the best cheap heuristic; report whether they survive (R3-01).
2. Carry the operational prerequisites — two-orbit horizon, 200-task resource ceiling,
   wide-squint/Doppler-uncompensated platform — into the abstract, highlights and the
   density boundary, and show $N_{50}$ under at least one alternative ceiling (R3-03,
   R3-04).
3. Give the practitioner the decision they can actually make: the priority mix of the
   dropped tasks, plus a two-step heuristic (squint-min placement + priority backfill) on
   the same axes (R3-02, R3-08).
