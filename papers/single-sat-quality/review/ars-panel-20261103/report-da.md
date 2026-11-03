# Devil's Advocate Report — paper1

## Canary
1. Read-only: I must not modify, create, or delete any file except my one report file.
2. Every finding quotes the exact manuscript text it criticizes, with section name and approximate tex line number.
3. No fabricated facts: I never assert what a cited reference contains beyond what the manuscript itself claims.
4. Numbers: quoted exactly as printed; no recomputation or correction.
5. No network access.
6. A negative claim carries the same evidence burden as a positive one: I mark as CRITICAL only what the manuscript's own text supports; otherwise MAJOR/MINOR or "observation, not defect".
7. Stdout is at most 5 lines; the report goes to the file.

> Reading note: the `Read` tool was blocked in this session by a failing pre-tool-use hook
> (`context-mode/hooks/pretooluse.mjs`, missing Git Bash). Chunks were read via PowerShell
> `Get-Content` in the prescribed ranges (1-320, 321-640, 641-960, 961-1280, 1281-1588), once each,
> with line numbers preserved. No other deviation from the reading discipline.

---

## Strongest counter-argument

The paper's headline is that embedding SAR physics as separate objectives changes what a scheduler
should choose, and that the effect is real at sparse density, contracts as the squint envelope
narrows, and vanishes at operational density. The last clause is the problem. In the Abstract and
the Conclusion the vanishing is presented as a property of the problem — "coverage pressure removes
the freedom to move acquisitions" — and sold to readers as "a quantitative rule for when
quality-aware SAR scheduling justifies its coverage cost". But the paper's own §7.1 finding (5)
states that "coverage convergence toward the G-BL anchor is conditional on the hot start, not a
structural property", and §6.4 states that the compressed front "characterises the G-BL-seeded front
... not the feasible surface as a whole", because a one-line squint-minimising heuristic reaches
$f_3\approx0.79$ at $N=500$, a region "outside the MOEA-3 surface". So the boundary is an artefact
of initialising the population at the coverage corner, not a boundary of the physics. The paper also
shows a random-initialised run of the same solver reaching higher $f_2$ at sparse density than the
headline front, so even the sparse-regime gains are anchored-front lower bounds. Meanwhile the
ablation reports that removing the incidence-angle component entirely "produces no measurable change
in any reported metric" — meaning the one conflict axis the paper invokes as its non-redundancy
mechanism does not drive selection, while the squint axis that does drive it enters both quality
objectives with the same sign. What survives is a careful measurement of a single aligned lever
(squint) plus a density-dependent price for using it — a genuinely useful result, but narrower than
the title, abstract, and highlights claim.

## Issue list

### DA-01 [CRITICAL] The density boundary is sold as physics but the paper's own text calls it an initialisation artefact (dimension: logic chain, over-generalisation)
- Quote: "It vanishes at operational densities: beyond $N \approx 150$ the found fronts converge to
  the greedy coverage anchor with quality margins below $2\%$, **because coverage pressure removes
  the freedom to move acquisitions** while solver convergence to lower-squint geometry aligns $f_2$
  and $f_3$ through the shared $\cos\psi_{\text{sq}}$ factor." (Conclusion, ~tex 1528-1533;
  Abstract, ~49-51, carries the same claim without the causal clause)
  Against: "coverage convergence toward the G-BL anchor is **conditional on the hot start, not a
  structural property**" (§6.6 Summary of Findings, finding 5, ~1346-1350) and "The compression
  characterises the G-BL-seeded front near the full-coverage working point, **not the feasible
  surface as a whole**" (§6.4, ~1087-1088).
- Why it breaks the argument: the paper gives two incompatible explanations for one phenomenon.
  A reader of the Abstract, the Highlights ("negligible beyond N = 150 targets") and the Conclusion —
  i.e. everything a reviewer or planner actually reads — is told the boundary is operational. The
  Discussion says it is an artefact of where the search starts. The two imply opposite advice: if
  geometric, stop using quality-aware scheduling at scale; if initialisation, run the solver
  differently and the advantage may persist.
- What would settle it: a random-initialised MOEA-3 run at $N=150,200,300,500$ reported on the same
  quality metrics as the hot-started run, with the resulting front merged into the reported one. The
  paper already runs random init for MOEA-2 and for variant D; extending it to MOEA-3 at dense
  density closes the question either way.

### DA-02 [CRITICAL] The Highlights attribute the whole $f_3$ gain to "the third objective" (dimension: logic chain, stakeholder blind spot)
- Quote: "Third objective adds +40\% (NESZ-ordering index) at sparse density, 15\% coverage cost"
  (highlights.tex, line 22)
  Against: "MOEA-3 raises $f_3$ by $+40\%$ ... at a $15\%$ coverage cost ... with a controlled
  $+4.9\%$ third-objective margin under a matched radiometric-aware knee rule" (Abstract, ~44-46)
  and "a controlled margin of $+4.9\%$ ($p = 2.3\times10^{-11}$, 47 of 50)" (§6.4, ~1196-1197).
- Why it breaks the argument: the $+40\%$ is the full three-objective method versus the coverage
  baseline; the third objective's own measured contribution is $+4.9\%$ ($+6.2\%$ under unmatched
  knees). The Highlight overstates the third objective's value by roughly eight-fold, in the one
  document that is read without the body. This is the paper's single most over-claimed sentence.
- What would settle it: rewrite the bullet to the measured attribution (e.g. "Three-objective SAR
  scheduling buys +40% NESZ-index at sparse density; the third objective alone adds +4.9%").

### DA-03 [CRITICAL] The claimed non-redundancy mechanism is contradicted by the paper's own ablation (dimension: logic chain, ignored alternative explanation)
- Quote (the mechanism the paper invokes): "solver convergence to low-squint regimes removes the
  alignment axis and leaves the $\theta_{\text{elev}}$ trade-off, whose exploitation is what
  saturates under coverage pressure at high density" (§3.2, ~475-478).
  Quote (the ablation): "Variant C (no incidence) produces no measurable change in any reported
  metric. This inertness is consistent with the window geometry: the elevation-plane incidence angle
  varies by only a few degrees across a visibility window ... so the $\theta_{\text{elev}}$ factor
  in $f_2$/$f_3$ acts as an approximately common scale within each window; removing it preserves the
  within-window task ordering and hence the selected schedule." (\S\ref{sec:ablation}, ablation file
  lines 128-137)
  And: "The incidence conflict of \S\ref{sec:pareto-coupling} therefore operates through the
  across-window/aggregate geometry rather than through per-window selection." (ablation file ~136-137)
- Why it breaks the argument: if deleting the entire incidence component changes nothing —
  $f_1^*$ $0.845$ vs $0.850$, $f_2$ $0.375$ vs $0.376$, $f_3$ $0.703$ vs $0.698$, $n_\text{sel}$
  $16.0$ vs $15.6$ at S1 — then the $\theta$ trade-off cannot be "what saturates". The only
  component that moves the search is the squint factor, and §3.2 itself says squint "enters both
  objectives with the same sign" and is "an alignment rather than a trade-off axis". The paper's
  non-redundancy argument therefore rests on a *correlation* measured across tasks, not on a
  *decision-level* trade-off: the negative $r$ exists because different tasks sit at different
  incidence angles, while the scheduler can only move squint, where both objectives agree.
- What would settle it: a selection-level test. Show a schedule pair where trading $f_2$ against
  $f_3$ requires different choices (same tasks, same coverage), or drop the claim and state that the
  third objective is a steeper re-weighting of the same squint-alignment lever. Contrast the
  ablation's variant inertness directly with the §6.4 sentence "Configurations that see
  $\psi_{\text{sq}}$ select schedules spanning the $\theta_{\text{elev}}$ trade-off" (~1175-1177) —
  variant C sees $\psi$ and is blind to $\theta$, and yet reproduces A.

### DA-04 [MAJOR] A one-line heuristic beats the proposed method on both quality objectives at the density where the paper's headline lives (dimension: cherry-picking, ignored alternative explanation)
- Quote: G-SM S1: $f_1^* = 0.51$, $f_2 = 0.389$, $f_3 = 0.722$; MOEA-3 S1: $f_1^* = 0.85$,
  $f_2 = 0.376$, $f_3 = 0.698$ (Table~\ref{tab:solver-profiles}, ~904-909). S2: G-SM $f_2=0.357$,
  $f_3=0.735$ vs MOEA-3 $f_2=0.329$, $f_3=0.597$.
- Why it weakens the argument: at $N=20$ and $N=100$ a deterministic greedy rule that only minimises
  squint produces equal-or-better geometry at 2--3× the coverage cost. The paper's Comparisons of
  the form "$+40\%$ versus G-BL" are true but silence this comparator; only one sentence in the
  Introduction (~137-139) acknowledges it, and the Abstract never does. The honest result is about
  the *price* of quality (coverage), not about the quality achieved.
- What would settle it: a coverage-matched comparison — interpolate each method's
  quality-versus-$f_1^*$ curve and report which dominates at $f_1^*=0.85$. The paper has the front
  data to do this and does not.

### DA-05 [MAJOR] Hypervolume is described as cardinality-sensitive and cardinality-insensitive in the same paper — and the demotion is what lets the method avoid losing (dimension: logic chain)
- Quotes: "Hypervolume (HV) is reported as a secondary, **cardinality-sensitive** diagnostic"
  (§5.3, ~782-783); "Because HV rewards **front cardinality as well as front quality**" (§6.1,
  ~966-967); "HV rewards an extreme single point and is **insensitive to cardinality**" (§6.4,
  ~1223). Also "its HV of $0.2341$ exceeds MOEA-3's $0.0893$" (§5.3, ~784-785).
- Why it breaks the argument: HV is the standard MOO indicator, and on it a single greedy point
  beats the 91-point front by 2.6×. The paper's reason for demoting HV ("cardinality") is
  self-contradictory and, in the direction that matters, backwards: cardinality sensitivity would
  favour the 91-point set, not the single point. Discarding the one standard metric that disagrees
  with the conclusion reads as adjudication in the paper's own favour.
- What would settle it: an explicit statement that HV with origin-anchored boxes is dominated by
  extreme points here, plus one cardinality-fair indicator (e.g. unary additive epsilon, R2 with a
  fixed weight set, or best-point-normalised HV) in which all solvers contribute equal weight. Note
  that the pooled normalisation bounds are themselves set by G-SM's extremes (C3-j), so HV is not an
  independent arbiter either — the paper should say that too.

### DA-06 [MAJOR] The variant-correlation numbers cannot be read from the printed definitions (dimension: logic chain)
- Quote: "in the $\psi_{\text{sq}}$-only limit both rise with $\cos\psi_{\text{sq}}$
  ($r_\psi = +0.997$)" (§6.4, ~1129-1132) versus "variant C removes incidence
  ($f_2=\cos\psi_{\text{sq}}$, $f_3=\cos^3\psi_{\text{sq}}$) and the correlation holds at $-0.65$,
  indistinguishable from variant A" (§6.4, ~1172-1173). Same construction for variant B
  ($f_2=\sin\theta_{\text{elev}}$, $f_3=\cos^3\theta_{\text{elev}}$) reported at $-0.23$ against a
  stated $\theta$-only limit of $r_\theta=-0.997$.
- Why it weakens the argument: taken literally, variant C's two objectives are a monotone transform
  of each other and its per-task correlation must be $+1$; the paper says $+0.997$ for that limit
  and $-0.65$ for the variant. Either the correlation is computed on the common *post hoc*
  $f_2,f_3$ (in which case the parenthetical definitions mislead), or the numbers are wrong.
  "Which objective component steers the conflict" — the section that decides whether the physics is
  real — depends on these four numbers.
- What would settle it: state the exact variables and population over which each correlation is
  computed (variant objective values vs common post hoc values; per-task vs per-schedule), and
  reprint the four numbers under one stated convention.

### DA-07 [MAJOR] The operational boundary is partly an artefact of an arbitrary resource constant (dimension: ignored alternative explanation, over-generalisation)
- Quote: "$E_{\max}=10^7$ and $M_{\max}=10^{11}$ (arbitrary units) ... typical per-task consumptions
  are $e_i=5\times10^4$ and $m_i=5\times10^8$. Both caps therefore translate into the same ceiling of
  200 concurrently scheduled tasks." (§3.3, ~559-562). Limitation: "the C3--C4 resource caps equate
  to a 200-task ceiling ... and bind in roughly half of the dense S3--S4 scenarios, so dense-regime
  convergence reflects both temporal (C2) and resource (C3--C4) saturation" (§7.4, ~1490-1494).
- Why it weakens the argument: two hand-set constants are tuned to coincide at exactly 200 tasks;
  at $N=300$ the perturbation control reports "coverage stays flat at 200 of the 300 targets"
  (~1279-1280). The density at which the multi-objective advantage vanishes is therefore partly a
  function of a constant the authors chose. The caveat appears only in Limitations, never in the
  Abstract, Highlights or the "quantitative rule" sentence.
- What would settle it: a sweep of the ceiling (e.g. 100 / 200 / 400 tasks) with $N_{50}$ and the
  f2-gain curve re-estimated, or a demonstration that the temporal constraint (C2) alone binds at
  the same densities.

### DA-08 [MAJOR] The coverage cost is measured against a weak baseline (dimension: ignored alternative explanation, stakeholder blind spot)
- Quote: "Tasks are sorted by earliest start time $t_{\text{start}}$ and greedily inserted into the
  schedule at their earliest feasible time." (§4.2, ~612-613). Also: "G-BL ... makes no use of SAR
  imaging physics when ordering or selecting tasks." (~611)
- Why it weakens the argument: the "profit-only baseline" never consults the priority weight $p_i$
  when *ordering*. A priority-sorted greedy is the obvious stronger coverage anchor and is not among
  the five configurations. Every headline cost ("$14\%$ coverage cost", "$f_1^*=0.51$") is relative
  to this anchor; a weak anchor inflates the apparent cost of quality and, since G-BL also
  under-covers in one scenario by $13.5\%$ (GA-P-BL), "near-optimal coverage anchor" is asserted
  from a small sample.
- What would settle it: add a priority-ordered greedy (same feasibility rules, sort by $p_i$) as a
  sixth comparator; if the MOEA's coverage deficit grows, the value proposition changes.

### DA-09 [MAJOR] Mean-per-task quality can be improved by dropping hard targets, and the paper never measures that (dimension: cherry-picking, ignored alternative explanation)
- Quote: "All quality objectives use the *mean* over scheduled tasks, making them independent of the
  number of scheduled tasks $m = |\mathcal{S}|$ and thereby producing a genuine ``quantity versus
  quality'' Pareto trade-off." (§3.2, ~365-367)
- Why it weakens the argument: mean-per-task quality is invariant to $m$ arithmetically but not to
  *selection*. A solver can raise mean $f_2$/$f_3$ by dropping the targets whose achievable geometry
  is poor — which is a selection effect, not an imaging-quality improvement. The task counts are
  reported ($n_\text{sel}$ in the ablation table, e.g. $15.6$ vs $19.5$ at S1) but nowhere is the
  quality of the *dropped* set reported, so the reader cannot tell which mechanism produced the gain.
- What would settle it: report the achievable-quality distribution of dropped versus retained
  targets, or a coverage-matched comparison restricted to the same selected task set.

### DA-10 [MAJOR] The headline radiometric gain is model-dependent by a factor of 2.4 (dimension: cherry-picking, over-generalisation)
- Quote: "Recomputing the sparse-regime comparison ... with the retained factor enlarges the MOEA-3
  gain over G-BL from $+40\%$ to $+94\%$ ... the proxy reading is conservative" (§3.2, ~433-436).
- Why it weakens the argument: two defensible NESZ expressions produce gains of $+40\%$ and $+94\%$;
  the paper reports the smaller and calls it conservative. That is legitimate, but a headline number
  that doubles under a modelling choice should carry that range where the headline is read. The
  Abstract's "radiometric-index quality" is the only trace of the caveat.
- What would settle it: print the $+40\%$/$+94\%$ bracket wherever the $+40\%$ is quoted, or
  normalise the objective so the gain is invariant to the choice.

### DA-11 [MAJOR] One scenario per class is used to bound solver stochasticity, and every significance test assumes scenarios are replicates (dimension: logic chain)
- Quote: "Each scenario is solved once per stochastic configuration ... so within-instance search
  stochasticity is not replicated" and "five repeats of each NSGA-III solver on one variant-A
  scenario per class reproduce bit-identically at S1 and S4, and where variation appears (S2, S3)
  the within-instance standard deviation (SD) of the knee values stays at or below $0.004$"
  (§5.4, ~849-860).
- Why it weakens the argument: the design openly does not replicate stochasticity; the check that
  supposedly bounds it rests on four scenarios (one per class) under five seeds. Bit-identical
  repeats at two classes and variation at the other two is itself unexplained. All Friedman and
  Wilcoxon tests treat scenario as the unit of replication, so unmeasured solver noise is absorbed
  into the residual and the reported $p$-values are more confident than the design supports.
- What would settle it: a stratified replication (e.g. 5 scenarios per class × 5 seeds) reporting
  within-instance versus between-scenario variance, and a variance-component correction to the
  paired tests.

### DA-12 [MAJOR] The reported Pareto front is dominated by points the authors' own control finds (dimension: over-generalisation, ignored alternative explanation)
- Quote: "random initialization attains higher $f_2$ at sparse density ($0.505$ vs.\ $0.395$ at S1,
  $+28\%$ ...)" (§6.6, ~1264-1266) against "the best-$f_2$ point reaches $f_2 = 0.449$ at
  $f_1^* = 0.58$" (§5.3, ~833-834).
- Why it weakens the argument: a random-init MOEA-2 at $f_1^*\approx0.47$ reaches $f_2=0.505$, above
  the best-$f_2$ point of the headline hot-started front. The "front" is therefore an approximation
  demonstrably inside the reachable set, and the paper's own hedge ("All fronts reported here are
  approximate ... under the tested search budget", ~1185-1186) concedes it. The Abstract presents
  the resulting numbers as measured gains with no tightness qualifier.
- What would settle it: merge the hot-start and random-init fronts per scenario and report the union
  front, or state explicitly that all reported quality values are lower bounds on the achievable
  front and quantify the gap.

### DA-13 [MINOR] Two printed $f_2$ ranges cannot both be right (dimension: internal consistency)
- Quote: "the pooled within-schedule $f_2$ standard deviation is $0.16$--$0.17$ at S1--S3 and
  $0.14$ at S4 for variant A, **with pooled range $0.65$ in every class**" (§6.4, ~1179-1181) versus
  the HV bounds "$f_2$: $0.11$--$0.56$" (§5.3, ~808). A $0.65$ span cannot exist inside a $0.45$
  global span.
- Why: either the two "ranges" are different objects (then one must be renamed) or one number is
  wrong. This matters because the sentence is the rebuttal of the "range-contraction" alternative.

### DA-14 [MINOR] Correlation calibres and their reported ranges do not line up (dimension: internal consistency)
- Quote: Abstract "coverage pressure dilutes that conflict to between $-0.13$ and $-0.23$ at high
  density" (~54-55) versus §5.1 "pooled per-task $r$ ... $-0.80$, $-0.23$, $-0.15$, $-0.31$ from S1
  to S4, the caliber of \S\ref{sec:pareto-coupling}" (~742-744). $-0.31$ at S4 lies outside the
  Abstract's stated high-density band while the text calls it the same calibre.

### DA-15 [MINOR] Dispersion swamps the HV summary (dimension: reporting)
- Quote: "MOEA-3 & 0.0893 & 0.1053" (Table~\ref{tab:hv}, ~944). A mean whose SD is 2.4× its value
  is not a summary; per-class HV or a robust statistic is needed if HV is retained at all.

### DA-16 [MINOR] Multiple-comparison families are defined two ways (dimension: internal consistency)
- Quote: "$\alpha=0.05/12$, the 12 being the three non-physics variants by four density classes
  against A within each reported metric" (§6.6, ~1360-1363) versus the ablation table caption's
  "family comprises the 12 variant-by-class comparisons" and the Fig.~5 caption's "applied within
  each reported metric" (which would make the family 36). One of the three statements is wrong.

## Ignored alternative explanations

1. **A trivial quality-aware heuristic (G-SM) achieves equal-or-better geometry.** Disclosed in one
   sentence, never carried into the Abstract, never given a coverage-matched comparison (DA-04).
2. **Hot-start anchoring.** The paper's own control shows random init buying far more $f_2$ at sparse
   density and reaching regions "outside the MOEA-3 surface" (DA-01, DA-12).
3. **The 200-task resource ceiling.** Two hand-set constants set the density at which coverage
   saturates (DA-07).
4. **Selection effects from mean-per-task metrics.** Dropping poorly-placed targets raises the mean
   without improving imaging (DA-09).
5. **The NESZ proxy definition.** The gain doubles under an alternative, equally defensible factor
   (DA-10).
6. **A weak coverage anchor.** Earliest-start greedy, not priority-ordered greedy (DA-08).
7. **Fixed 30 s dwell.** Removes the strongest real-world radiometric lever; the paper's radiometric
   objective is therefore geometric placement only (disclosed only in Limitations, ~1495-1496).
8. **The baseline's incidental quality rises with density.** G-BL's own $f_3$ climbs from $0.497$ (S1)
   to $0.675$ (S4), so part of the "contracting advantage" is a rising floor rather than a shrinking
   opportunity. The squint-cap analysis explains the analogous ceiling effect explicitly (§7.2,
   ~1409-1411) but the density analysis does not apply the same reasoning.

## Missing stakeholder perspectives

- **Mission planner / operator.** "14% coverage cost" is never translated into targets lost, priority
  mass lost, or revisit latency. The paper admits there is no timeliness objective (§7.4), but the
  operational recommendation is written as if coverage were the only currency.
- **Instrument engineer.** At the scheduled mean squint of $16$--$24^\circ$ the Doppler centroid is
  quoted at $10^2$\,kHz against a PRF of $10^0$--$10^1$\,kHz; the paper invokes yaw steering and
  Doppler-centroid tracking without an ambiguity or SNR budget. An instrument reviewer will ask
  whether the $f_3$ ordering survives real Stripmap processing at those squints.
- **Reviewer of the competing baseline.** G-SM is given one sentence and no front; HV, the metric on
  which it wins, is demoted; the HV normalisation bounds are set by its own extremes. A referee
  sympathetic to simple heuristics will read this as an unfair fight.
- **Downlink / power subsystem.** Energy and memory enter as "arbitrary units" settings tuned to a
  single ceiling, so the dense-regime conclusion does not transfer to a real platform with a real
  duty cycle.

## Observations (non-defects)

- The ordering-preserving argument for the suppressed $\sin\theta$ factor (§3.2, ~429-433) is correct
  as stated and is a good defensive move.
- The matched radiometric-aware knee rule and the $p=4$/$H=15$ reference-direction control (§6.4,
  ~1194-1206) are well designed and close the obvious "unequal search budget" objection for the S1
  margin.
- The squint-cap sweep is correctly explained as a ceiling effect — the baseline's absolute geometry
  improves as options are filtered out (§7.2, ~1409-1411).
- The physical-modelling-scope paragraph (§3.3, ~517-532) and the C1 "experimental setting, not a
  platform claim" disclaimer (~505-507) are unusually explicit and should be kept.
- The chance control (5,000 random selections, ~1287-1293) is a genuinely informative null.
- The paper states plainly that the compressed front is a G-BL-seeded phenomenon "not the feasible
  surface as a whole" (§6.4, ~1087-1088) — the honesty is there; the problem is that the Abstract
  and Conclusion do not carry it.
- The Limitations section is candid to the point of self-harm (unexplained S1 variant-D coverage
  reversal; small control samples; fixed dwell; no learning baseline). Keep it.
- The variant-A-only replication in §5.1 (~737-743) is a sound control for the geometry confound
  inside S4.

## "So what?" verdict

What survives the attack is narrower than the title but real. On one platform, one orbit, one mode,
and one fixed dwell, embedding SAR geometry into a many-objective scheduler produces a modest,
density-dependent gain in mean ground-pixel-area index and in a NESZ-ordering proxy; the gain is
purchasable, is bounded by the squint envelope, and is largely reproduced by a one-line
squint-minimising greedy at a higher coverage price. The paper's real contributions are the
measurable *price* of quality (the coverage-for-quality trade-off curve), the observation that
widening the squint envelope is what creates the opportunity, and a transferable
envelope–null–schedule decomposition for separating geometric coupling from solver-induced
correlation. The claim that the third objective is "not redundant" is not established: the paper's
own ablation shows the incidence axis it invokes is inert for selection, and the objectives share
the one axis that does move the search. The claim that the advantage "vanishes at operational
densities" is a statement about a hot-started search, not about the problem, and the paper says so
itself — twice — while the Abstract, Highlights and Conclusion say the opposite. If the framing were
brought down to the level of the Discussion, the paper would be a solid, slightly negative, useful
result. As written, the summary layers promise a method-level conclusion the evidence does not
carry.

---

## Reading log

### Chunk 1 (tex lines 1-320: preamble, abstract, Introduction, Related Work, start of Problem Formulation)

Raw observations, to be consolidated below:

- **C1-a (abstract, ~43-45).** "+34% geometric-index quality at a 14% coverage cost and +40%
  radiometric-index quality at a 15% cost" — the introduction prints "+33.7%" (~134). Rounding is
  consistent, but the abstract's "+34%" and "+40%" are the only numbers most readers see; both are
  *relative* changes with no baseline scale given (relative to what value? per cent of what?). The
  abstract never states what the coverage cost means operationally (targets dropped).
- **C1-b (abstract, ~50-51).** "it vanishes beyond $N \approx 150$, where the multi-objective fronts
  converge to the greedy coverage anchor with quality margins below $2\%$ under greedy hot-start
  initialization." The conditional "under greedy hot-start initialization" is appended after the
  claim, not before it. Whether the convergence is a property of the density or of the initialisation
  is exactly the alternative explanation a referee will raise; the abstract's word order pre-empts
  the stronger reading.
- **C1-c (abstract, ~56-57).** "which locates the loss of value in the schedule geometry and not in a
  redundancy between objectives." This is the paper's causal verdict stated in the abstract, before
  the reader can see that the evidence is a correlation coefficient compared against a null
  (~53-54). "not in a redundancy" is a negative claim; the abstract supplies no measurement inline.
- **C1-d (abstract, ~46-47 and ~140-144).** "Two measured boundaries delimit that gain." Both
  boundaries are adversities (gain contracts; gain vanishes). The abstract does not state in the same
  breath how large the surviving operating region is — a reader remembers "two boundaries" more than
  "boundary 1 starts at 45° and boundary 2 at N≈150".
- **C1-e (Introduction, ~127-130).** "a single-objective genetic algorithm with greedy hot-start
  (GA-P-BL, a control that returns the greedy schedule whenever it fails to improve profit, so it is
  never worse than G-BL)". A control that is by construction never worse than the baseline is a weak
  comparator; it cannot fail. What it is *for* is unclear until the ablation. Flag for later.
- **C1-f (Introduction, ~137-139).** "The single-point squint-minimized heuristic (G-SM) reaches
  higher $f_3$ than MOEA-3 in sparse scenarios but only at roughly half the coverage of G-BL
  ($f_1^* \approx 0.51$)." A one-line heuristic beats the flagship three-objective method on one of
  the two quality objectives. The paper discloses it, which is to its credit, but the sentence does
  not say what MOEA-3 buys over G-SM — i.e. whether the MOEA is needed at all for the physics terms.
- **C1-g (Introduction, ~138-139 vs abstract ~43-45).** Coverage cost is quantified for MOEA-2/3
  (+14%/+15%) but G-SM's coverage is given as "$f_1^* \approx 0.51$", a different unit (normalised
  coverage, not a per-cent cost). The reader cannot put G-SM's trade-off on the same axis as the
  MOEAs' without going into the results.
- **C1-h (Introduction, ~151-185, contributions).** Contribution 1 claims a three-objective
  formulation plus "a systematic quality–coverage comparison across two greedy heuristics, a
  single-objective GA control, and two NSGA-III variants on 200 scenarios in four scale classes";
  contribution 4 claims "A controlled ablation (four objective-function variants over six scenario
  classes, 300 scenarios per variant)". Two different scenario universes (200 scenarios / four
  classes vs 300 scenarios per variant / six classes) are advertised back to back with no sentence
  tying them together. Which one is the evidence base for the headline claim is ambiguous at the
  introduction.
- **C1-i (Introduction, ~173-178).** "An anchor-independent decomposition of the $f_2$–$f_3$ coupling:
  the trade-off is mild over raw visibility geometry ($r \approx -0.36$ against an independent-angle
  null of $r \approx -0.60$), is restored to null strength inside sparse schedules ($-0.62$) by
  squint-aware steering, and dilutes to $-0.13$ to $-0.23$ under coverage pressure at high density."
  Note the logical shape: raw geometry $r=-0.36$ (weaker than null), schedules $-0.62$ (at null),
  high density $-0.13$ to $-0.23$ (much weaker than null). Three different regimes, all read as
  "coupling". "Restored ... by squint-aware steering" asserts a cause from a correlation.
- **C1-j (Related Work, ~248-252).** "To our knowledge, no existing SAR scheduling method treats
  continuous, physics-derived quality functions as decomposed optimization objectives in their own
  right: the closest approaches embed aggregated quality proxies rather than separate geometric and
  radiometric objectives." Repeated near-verbatim at ~296-299. A "to our knowledge" hedge covers the
  search, not the scope of the twin claim ("decomposed", "continuous", "physics-derived",
  "in their own right"). Each qualifier narrows the claim; the paper should name which single
  qualifier does the work.
- **C1-k (Problem Formulation, ~312-315).** "operating in Stripmap mode, which provides the widest
  continuous swath with uniform quality and analytically tractable NESZ and resolution expressions".
  Mode restriction is explicit and justified on tractability. Legitimate scoping; note that the
  quality mechanisms are mode-dependent (spotlight dwell), so the conclusion is Stripmap-scoped.
  Observation, not defect.

### Chunk 2 (tex lines 321-640: Problem Formulation 3.1-3.3, start of Methodology)

- **C2-a (structure of the objective pair, ~388 and ~403).**
  $f_2 = \frac{1}{|\mathcal S|}\sum \sin\theta_{\text{elev}}\cos\psi_{\text{sq}}$ and
  $f_3 = \frac{1}{|\mathcal S|}\sum \cos^3\xi$ with $\cos\xi=\cos\theta_{\text{elev}}\cos\psi_{\text{sq}}$.
  Both are separable products over the **same two angles**, and the manuscript says so itself
  (~461-471): squint "enters both objectives with the same sign" and is "an alignment rather than a
  trade-off axis", leaving "the residual two-axis structure ... $[\theta_{\text{elev}},\psi_{\text{sq}}]$"
  with a single genuine conflict axis. Consequence for the headline: adding $f_3$ to $f_2$ adds a
  second, differently-shaped view of the *same* $\theta_{\text{elev}}$ choice, plus a squint factor
  already present in $f_2$. This is the strongest structural ground for the "redundancy" attack, and
  it comes from the paper's own algebra, not from outside.
- **C2-b (~415-437, NESZ proxy).** The manuscript discloses that the plane-Earth proxy
  "underestimates slant range by roughly 4% and $R^3$ by roughly 13%" and suppresses $\sin\theta$,
  then reports that using the retained factor "enlarges the MOEA-3 gain over G-BL from $+40\%$ to
  $+94\%$". The headline $+40\%$ is thus one of two numbers differing by a factor $>2$, both computed
  by the authors, and the smaller one is chosen as the reported result. The paper's justification
  ("the proxy reading is conservative") is legitimate, but the magnitude instability of the headline
  under a modeling choice is disclosed only in the body, never in the abstract or contributions.
- **C2-c (~429-433).** "In fact the suppression is ordering-preserving by construction: the ground
  incidence is a monotone function of the same off-nadir angle ... so dividing by $\sin\theta$
  reweights but cannot reorder acquisition geometries." Checked against the stated forms: ordering
  in $f_3$ is ordering in $\xi$; the omitted factor is a monotone function of the same $\xi$, so the
  argument holds. **Observation, not defect** — and a genuinely good defensive argument.
- **C2-d (~426-428).** Immediately after that argument the paper says "$f_3$ should be read as a
  geometry proxy rather than an absolute NESZ ranking across widely separated incidence angles." The
  paper is honest, but the abstract then reports "$+40\%$ radiometric-index quality", and the phrase
  "radiometric-index" is the only carry-over of this caveat. A reader who stops at the abstract
  believes a radiometric quantity was optimised.
- **C2-e (~559-570, resource caps).** "$E_{\max}=10^7$ and $M_{\max}=10^{11}$ (arbitrary units) ...
  typical per-task consumptions are $e_i=5\times10^4$ and $m_i=5\times10^8$. Both caps therefore
  translate into the same ceiling of 200 concurrently scheduled tasks." Two *arbitrary* constants are
  tuned to produce exactly the same ceiling of 200 tasks. Then: "20 of 50 G-BL schedules at S3 and 27
  of 50 at S4 select exactly 200 tasks, so the binding constraint there is C3--C4 rather than C2".
  **The dense-regime saturation — presented as an operational density boundary — is driven by a
  chosen constant.** The paper concedes it in one clause ("should be read as convergence to the
  feasible task count under both constraint families"), but I have not yet seen any sensitivity test
  that moves the 200-task ceiling. If none exists, the "vanishes beyond $N\approx150$" boundary is a
  statement about this constant.
- **C2-f (~369-381, $f_1$ normalisation).** $f_1^*$ is normalised by the G-BL profit. At high density
  with a binding cap, G-BL is itself constrained to 200 tasks, so $f_1^*$ measured against it can
  never exceed 1 and the "coverage cost" is always relative to a capped baseline. Also note $f_2,f_3$
  are *not* normalised by any baseline, while $f_1^*$ is — three objectives on different footings in
  the same Pareto front (see C2-h).
- **C2-g (~608-623, G-BL definition).** "Tasks are sorted by earliest start time $t_{\text{start}}$
  and greedily inserted into the schedule at their earliest feasible time." A *profit-only* baseline
  that never consults the priority weight $p_i$ when ordering is a weak definition of "profit-only":
  a priority-sorted greedy is the obvious stronger comparator, and it is not among the five
  configurations. Since all coverage-rate numbers ("$14\%$ coverage cost", "$f_1^*\approx0.51$") are
  measured against this anchor, a weak anchor inflates the apparent cost of quality.
- **C2-h (~365-367 and ~391-394).** "All quality objectives use the *mean* over scheduled tasks,
  making them independent of the number of scheduled tasks ... and thereby producing a genuine
  'quantity versus quality' Pareto trade-off." Mean-per-task quality is independent of $m$
  arithmetically, but not of *which* tasks are selected. The metric can be raised by dropping targets
  whose achievable geometry is poor. That is a legitimate design choice if the coverage cost is
  reported alongside (it is), but the phrase "genuine trade-off" asserts that the gain is a real
  quality improvement rather than a selection effect. No measurement of *which* targets are dropped,
  or of the quality distribution over dropped targets, appears anywhere I have read so far.
- **C2-i (~517-532, physical scope).** Doppler centroid "of order $10^2$\,kHz at the scheduled
  $16$--$24^\circ$ squints, versus a PRF of order $10^0$--$10^1$\,kHz". This states that the
  scheduled squints are far outside unambiguous Stripmap operation without yaw steering; the paper
  declares the idealisation and bounds it ("absolute performance claims for platforms without Doppler
  compensation at large squint are out of scope"). **Observation** — the disclosure is explicit. But
  it means the ~16--24° mean squint at which the alignment argument is made is itself a modelling
  artefact of a platform the paper explicitly declines to claim exists.
- **C2-j (~599-607).** "The five configurations differ primarily in objective-function configuration
  rather than algorithmic paradigm. This design is intentional: it isolates the effect of adding
  physical quality objectives". Good design for the stated question, and it also *limits* what the
  paper may claim: nothing here supports "physics-aware objectives change what a **scheduler** should
  choose" as an algorithmic claim, only as an objective-set claim on one solver family.
- **C2-k (~630-632).** G-SM "minimizes squint angle as a computationally cheap proxy for maximizing
  $f_3$ ... the correlation between squint minimization and $f_3$ improvement is confirmed by the
  large effect size (Cliff's $\delta = +0.99$)". An effect size of a between-group comparison is not
  a correlation, and "confirmed by the large effect size" is a weaker statement than it sounds given
  that $f_3$ is by construction monotone decreasing in $|\psi_{\text{sq}}|$. Minor wording.

### Chunk 3 (tex lines 641-960: Methodology 4.4, Experimental Setup, Results 6.1)

- **C3-a (Table~\ref{tab:solver-profiles}, ~904-930).** The single most damaging table entry for
  the paper's framing: at S1, **G-SM attains $f_2=0.389$ and $f_3=0.722$ while MOEA-3 attains
  $f_2=0.376$ and $f_3=0.698$.** A one-line squint-minimising greedy beats the flagship
  three-objective method on *both* quality objectives at the density where the paper's headline
  lives. At S2 the same: G-SM $f_2=0.357$, $f_3=0.735$ vs MOEA-3 $f_2=0.329$, $f_3=0.597$. So the
  paper's stated metric ($+40\%$ $f_3$ relative to G-BL) is $-3.3\%$ relative to G-SM at S1 and
  $-19\%$ at S2. The defence is that G-SM costs much more coverage ($f_1^*=0.51$ vs $0.85$), which
  is true — but the paper never frames the result that way in abstract or contributions.
- **C3-b (~783-786).** "its ranking inverts if the single-point G-SM is included (its HV of $0.2341$
  exceeds MOEA-3's $0.0893$), so HV is not interpreted as a standalone quality judgment." The
  reason given is "cardinality-sensitive", but cardinality sensitivity biases HV *toward* sets with
  many points, and G-SM is a **single point**. A single point beating a 13- or 91-point set by 2.6×
  is not a cardinality artefact; it is the standard MOO indicator saying the greedy point is in a
  better region. The manuscript demotes the one standard metric on which its method loses to a
  one-line heuristic. This is the clearest instance of the paper adjudicating in its own favour on
  a metric choice, and the stated justification does not support the move.
- **C3-c (~926-930 vs ~675).** S4: G-SM reaches $f_3=0.786$ at $f_1^*=0.37$, while G-BL is
  $0.675$ and MOEA-3 is $0.680$. A schedule with $f_3$ 16% above the greedy anchor therefore
  *exists* at $N=500$. The paper reports the dense-regime fronts as "compressed" and the gain as
  vanishing. Both cannot be true descriptions of the same reachable set. Either the MOEA never
  reaches a region that a greedy heuristic finds trivially, or the front does contain it and the
  knee/profiles hide it. **This is the strongest single piece of internal evidence that "the gain
  vanishes at high density" is a statement about the MOEA's search, not about the physics.**
- **C3-d (~827-830).** "the dense-regime fronts are compressed (S4 spans only about $0.014$ in
  $f_2$)". Compressed *fronts* from a 100-individual, 200-generation NSGA-III on a $2N=1000$-dimensional
  chromosome, hot-started at the coverage corner, are exactly what a search failure looks like.
  The manuscript uses the compressed front as evidence about the problem; C3-c shows the same
  manuscript has a schedule 16% better in $f_3$ sitting in its own results table.
- **C3-e (~663-689, MOEA specification).** MOEA-2 uses $H=13$ reference directions, MOEA-3 uses
  $H=91$, with the **same** population 100 / generations 200. The two- and three-objective runs
  therefore have very different budget per reference direction. The headline third-objective margin
  ($+4.9\%$) is measured under an allocation that is generous to MOEA-2 and thin for MOEA-3, so the
  margin is at best a lower bound and at worst an artefact of unequal search coverage. A
  budget-equalisation control is needed before the number can be read as "what the third objective
  is worth".
- **C3-f (~849-860, replication).** "Each scenario is solved once per stochastic configuration ...
  so within-instance search stochasticity is not replicated"; the check is "five repeats of each
  NSGA-III solver on one variant-A scenario per class". One scenario per class cannot bound
  stochasticity across the suite; and "reproduce bit-identically at S1 and S4" while varying at
  S2/S3 is itself unexplained (a deterministic-hash-like behaviour in two classes and not in two
  others). All significance tests below treat scenarios as the replicate, so solver noise is
  folded into the residual and the tests are more confident than the design supports.
- **C3-g (~743-744 vs abstract ~53-55).** Variant-A pooled per-task $f_2$–$f_3$ correlations are
  given as "$-0.80$, $-0.23$, $-0.15$, $-0.31$ from S1 to S4", described as "the caliber of
  \S\ref{sec:pareto-coupling}". The abstract states "coverage pressure dilutes that conflict to
  between $-0.13$ and $-0.23$ at high density". $-0.31$ at S4 sits outside that stated range.
  Either the calibers differ (in which case the parenthetical's "the caliber of" is wrong) or the
  abstract's range is wrong. One of the two must be fixed.
- **C3-h (~425-426 vs ~766-767).** "incidence varies by only a few degrees (about $1.5^\circ$ mean
  within-window range in the S1 scenarios)" coexists with "the median change of squint over any
  30\,s within-window sub-interval is $11^\circ$". Within a window, the control lever is almost
  entirely squint, and squint moves $f_2$ and $f_3$ in the *same* direction (§3.2 says so). So
  within-window time selection is an alignment problem with no trade-off. The genuine
  $\theta_{\text{elev}}$ conflict can only act through *which* target/window is selected. The paper
  never states where the trade-off is actually exercised; this matters because it determines
  whether three-objective machinery is needed at all or whether per-task squint minimisation plus
  selection suffices (which is G-SM).
- **C3-i (~700-711, scenario classes).** S4 is defined as $N=500$ but one of its five variants
  ("S4-D narrows the incidence ceiling from $47^\circ$ to $25^\circ$") changes the *geometry*, not
  just density. The density trend and a geometry change are therefore entangled inside the S4 class
  mean. The variant-A replication (~737-743) is a genuine and good control for this, and it
  reproduces saturation — credit where due; but the main table's S4 mean still mixes the two.
- **C3-j (~808-818, HV normalisation).** HV uses reference point $(0,0,0)$ in
  min–max-normalised space with bounds pooled across all solvers and scenarios ($f_1$: $0.06$–$1.16$;
  $f_2$: $0.11$–$0.56$; $f_3$: $0.45$–$0.87$). The bounds are set by the extreme points, which are
  produced by G-SM, so G-SM's advantage is partly baked into the scale. This cuts *against* my
  C3-b reading and should be stated: HV here is not an independent arbiter either. The honest
  position is that neither HV nor $\delta$ settles MOEA vs G-SM, and the paper needs a direct
  coverage-matched comparison (quality at matched $f_1^*$), which it does not present.
- **C3-k (Table~\ref{tab:hv}, ~944-946).** MOEA-3 HV $0.0893 \pm 0.1053$: the standard deviation
  exceeds the mean by 2.4×. A mean with that dispersion is not a summary of anything. If HV is
  retained as a diagnostic it should be reported per class or with a robust statistic.
- **C3-l (~881-886).** Two gain estimators coexist in one sentence: "improves $f_2$ by $+33.7\%$
  ... on the per-scenario-ratio basis (the pooled-mean ratio gives $+33\%$ ...)". The abstract
  prints $+34\%$, the contributions $+33.7\%$. Consistent within rounding, but the paper should say
  once which estimator is the reported one, because the two differ systematically (ratio of means ≠
  mean of ratios).
- **C3-m (~520-524 again, and ~715-721).** The platform is "a generic C-band Stripmap SAR" with
  $D=12.3$\,m and $B=56.5$\,MHz over $18^\circ$–$47^\circ$ bilateral incidence. Stated as generic.
  Observation: a 12.3 m antenna at C-band is a large, high-resolution instrument; the physics
  conclusions are conditioned on this specific parameter set, which the paper does not sweep.

### Chunk 4 (tex lines 961-1280: Results 6.2 squint regime, 6.3 scale sensitivity, 6.4 Pareto compression, start of 6.6 robustness)

- **C4-a (the two explanations for dense convergence, ~1077-1091 vs ~1087-1091).** §6.3 opens "The
  dense-regime convergence of \S\ref{sec:scale-sensitivity} has a geometric cause: the two physical
  objectives conflict most strongly when the scheduler can move acquisitions, and coverage pressure
  takes that freedom away." Twelve lines later: "The compression characterises the G-BL-seeded front
  near the full-coverage working point, **not the feasible surface as a whole**: the
  squint-minimizing heuristic G-SM reaches $f_3 \approx 0.79$ at $f_1^* \approx 0.37$ at S4, a region
  outside the MOEA-3 surface." The section first attributes the convergence to geometry and then
  shows it is a property of one seeded search. The two explanations predict different remedies
  (nothing to do vs. search harder); the paper keeps both and the abstract reproduces the stronger
  one ("the multi-objective fronts converge to the greedy coverage anchor", "it vanishes beyond
  $N\approx150$").
- **C4-b (~1090-1091, and §6.2 ~991-994).** The paper states outright that G-SM reaches
  $f_3\approx0.79$ at $N=500$, i.e. **+16% radiometric quality above the greedy anchor at the
  densest class**, at a 63% coverage cost. The abstract's operational rule ("when quality-aware SAR
  scheduling justifies its coverage cost") therefore cannot be read as "physics-aware scheduling
  stops paying at high density" — only as "the *coverage-preserving* MOEA gain stops paying". That
  distinction is never drawn in the abstract or in the contributions, and it is the difference
  between a boundary of the method and a boundary of the physics.
- **C4-c (hard sign contradiction, ~1129-1132 vs ~1172-1173).** In the null construction: "in the
  $\psi_{\text{sq}}$-only limit both rise with $\cos\psi_{\text{sq}}$ ($r_\psi = +0.997$)." In the
  variant analysis: "variant C removes incidence ($f_2=\cos\psi_{\text{sq}}$,
  $f_3=\cos^3\psi_{\text{sq}}$) and the correlation holds at $-0.65$, indistinguishable from
  variant A". Variant C **is** the $\psi$-only limit. The manuscript asserts $+0.997$ for that limit
  and $-0.65$ for the variant that realises it. Both cannot be true. (Same shape for variant B:
  "$f_2=\sin\theta_{\text{elev}}$, $f_3=\cos^3\theta_{\text{elev}}$" is the $\theta$-only limit the
  manuscript assigns $r_\theta=-0.997$, yet variant B is reported at $-0.23$.) Whatever the
  resolution (mis-printed formulae, or correlations computed on a different object than stated), the
  argument in "Which objective component steers the conflict" rests on these two numbers.
- **C4-d (HV cardinality: self-contradiction, ~782-783 vs ~966-967 vs ~1223).** §5.3: "Hypervolume
  (HV) is reported as a secondary, **cardinality-sensitive** diagnostic". §6.1: "Because HV rewards
  front cardinality as well as front quality". §6.4: "HV rewards an extreme single point and is
  **insensitive to cardinality**". Three statements, one contradiction, and it is the stated reason
  for demoting HV. If HV is cardinality-insensitive, the G-SM result in C3-b is not dismissible.
- **C4-e (~1223-1226).** "HV rewards an extreme single point and is insensitive to cardinality:
  every single-objective solver contributes one point per scenario, while MOEA-3 contributes
  $33.8 \pm 8.4$ non-dominated points at S1". These two clauses do not cohere: if HV were
  insensitive to cardinality, the point count would not matter, and there would be no reason to
  mention $33.8$ points as a caveat.
- **C4-f (~1259-1272, random initialisation).** "random initialization attains higher $f_2$ at
  sparse density ($0.505$ vs.\ $0.395$ at S1, $+28\%$; $0.460$ vs.\ $0.320$ at S2, $+44\%$)" — and
  loses $0.393$ in $f_1^*$ at S1. So at $f_1^*\approx0.47$, a random-init MOEA-2 reaches
  $f_2=0.505$, which is **above the best-$f_2$ point the paper reports for its own hot-started front
  at S1** ("the best-$f_2$ point reaches $f_2 = 0.449$ at $f_1^* = 0.58$", ~833-834). The reported
  front is thus dominated by a point the authors' own control finds. The paper calls all fronts
  "approximate ... under the tested search budget" (~1185-1186), which is honest, but the headline
  numbers are then lower bounds of unknown tightness, and the abstract presents them as measured
  gains without that qualifier.
- **C4-g (~1194-1206, matched knee rule).** This is the best-designed control in the paper and it
  is reported properly: both fronts re-selected under "the identical procedure ... differ only in
  the radiometric term", giving $+4.9\%$ against $+0.05\%$ for the blind rule, plus a
  reference-direction count control ($p=4$, $H=15$) that reproduces $f_3=0.702$ vs $0.698$.
  **Observation, not defect — credit.** It closes the "budget inequality" objection from C3-e for
  the S1 margin.
- **C4-h (~1180-1181 vs ~808-809).** "the pooled within-schedule $f_2$ standard deviation is
  $0.16$--$0.17$ at S1--S3 and $0.14$ at S4 for variant A, with pooled range $0.65$ in every class."
  But the HV normalisation bounds state "$f_2$: $0.11$--$0.56$" over all solvers, scenarios and
  frontier points — a total range of $0.45$. A pooled range of $0.65$ for $f_2$ cannot coexist with
  a global $f_2$ span of $0.45$. One of the two printed numbers is wrong or the two "ranges" are
  different objects.
- **C4-i (~1055-1067, $N_{50}$).** The logistic midpoint $N_{50}\approx51$ has a bootstrap CI of
  $[37,64]$ and the paper correctly says it "should therefore be read as a coarse indicator ... not
  as a precise threshold". The abstract and contribution 2 then print "$N_{50} \approx 51$" without
  the interval, alongside "negligible advantage beyond $N=150$". Two numbers measuring two different
  things (coverage-deficit midpoint vs. f2-gain floor) are presented as one envelope.
- **C4-j (~1226-1228).** "In one of the 200 scenarios a sparse-density MOEA solution exceeds
  $f_1^*=1.00$ ($+10.8\%$ above G-BL), so the greedy schedule is a near-optimal coverage anchor."
  One scenario out of 200 is thin support for "near-optimal coverage anchor"; and GA-P-BL's single
  improving scenario was $+13.5\%$ (§4.4). Both are smaller than the pooled $f_1$ bound of $1.16$
  used for HV normalisation — the source of the $1.16$ extreme is never identified.
- **C4-k (~1135-1145, calibration of the "coupling" metric).** Four different correlation objects
  now coexist: $r_{\text{null}}=-0.60$ to $-0.62$ (permutation), $r_{\text{MC}}=-0.28$ (uniform box),
  envelope $-0.36$, in-schedule $-0.62$ (S1) / $-0.15$/$-0.13$/$-0.23$ (S2--S4), per-schedule Fisher-z
  means $-1.09$/$-0.16$/$-0.16$/$-0.19$, and variant-A pooled values $-0.80$/$-0.23$/$-0.15$/$-0.31$
  (§5.1). The paper is careful about naming each, but the headline sentence in the abstract picks one
  of the six and calls it "the" conflict. A referee cannot reproduce which quantity the abstract
  number is.
- **C4-l (~1274-1280).** Perturbation control: "coverage stays flat at 200 of the 300 targets (all
  ten scenarios at the ceiling for $\sigma\le0.5$...)". At S3 every tested scenario sits at the
  200-task resource ceiling. This is the clearest confirmation of C2-e that the dense-regime
  behaviour is governed by the chosen cap, and the perturbation sweep cannot see it because the
  ceiling is saturated at every perturbation level.

### Chunk 5 (tex lines 1281-1588: end of robustness, Discussion, Conclusion, back matter)

- **C5-a (central contradiction: conclusion vs.\ own finding 5, ~1528-1536 vs ~1346-1351 and
  ~1087-1091).** The Conclusion states: "It vanishes at operational densities: beyond
  $N \approx 150$ the found fronts converge to the greedy coverage anchor ... **because coverage
  pressure removes the freedom to move acquisitions** while solver convergence to lower-squint
  geometry aligns $f_2$ and $f_3$ through the shared $\cos\psi_{\text{sq}}$ factor." Nine hundred
  lines earlier, finding (5) of the paper's own summary states: "coverage convergence toward the
  G-BL anchor is **conditional on the hot start, not a structural property**", and §6.4 states the
  compression "characterises the G-BL-seeded front ... **not the feasible surface as a whole**".
  The Conclusion converts a solver-initialisation artefact into a physical cause, and the Abstract
  inherits it ("it vanishes beyond $N\approx150$"). This is the paper's central logical defect: the
  same phenomenon is described as (a) a geometric necessity in the abstract/conclusion and (b) an
  initialisation artefact in the discussion.
- **C5-b (~1522-1524, conclusion opening).** "In sparse request sets, **re-optimising observation
  times** buys large quality gains at a stated coverage price: $+40\%$ in radiometric quality at a
  $15\%$ coverage cost..." Re-optimising observation times is exactly what G-SM does too, and G-SM
  buys $+45\%$ $f_3$ at a $49\%$ cost. The sentence attributes to the general mechanism
  ("re-optimising observation times") a number that belongs to one particular solver at one
  particular knee. The attribution is the alternative explanation the paper must separate, and the
  Conclusion conflates it.
- **C5-c (~1344-1351, finding 4 vs.\ the title).** Finding (4): "solver outcomes become invariant to
  the choice of physical objectives at $N \geq 300$ (ablation study)". Combined with finding (2)'s
  "the advantage shrinking to $\lesssim 0.2\%$ at $N \geq 300$", the paper's own summary says the
  physics objectives do not change the outcome at operational densities. The title advertises a
  method that "balances profit, NESZ, and geometric resolution"; the evidence supports a
  characterisation of *when* that balance matters, not a method that improves operations. The
  manuscript's own framing ("we measure where the formulation pays off") is the honest version and
  is better than the title.
- **C5-d (~1461-1472, limitation scope).** The limitation states the third-objective
  indistinguishability is "specific to the single-pass, single-satellite Stripmap setting" and "not
  a mathematical identity between $f_2$ and $f_3$". Good. But the abstract carries none of this
  scope; it says the boundaries are "a quantitative rule for when quality-aware SAR scheduling
  justifies its coverage cost", which is a platform-level recommendation drawn from one orbit, one
  mode, one altitude, one antenna.
- **C5-e (~1490-1494, resource caps).** Limitation: "the C3--C4 resource caps equate to a 200-task
  ceiling ... and bind in roughly half of the dense S3--S4 scenarios, so dense-regime convergence
  reflects both temporal (C2) and resource (C3--C4) saturation, and results may differ under other
  energy or downlink budgets". **This is the admission that the operational boundary depends on a
  chosen constant, and it is stated only in Limitations — never in the abstract, contributions or
  conclusion.** No sensitivity sweep over the cap is reported anywhere.
- **C5-f (~1495-1498, dwell).** "the dwell time is fixed at 30\,s, removing the dwell-versus-SNR
  trade-off that an agile scheduler could otherwise exploit." Honest and important: in real SAR
  design, dwell is the strongest radiometric lever. Fixing it means the paper's radiometric
  objective can only be improved through geometry. The abstract's "radiometric quality" gain is
  therefore a geometric-placement gain only. Disclosed in Limitations only.
- **C5-g (~1398-1417, squint-cap sweep).** "MOEA-3's $f_2$ advantage shrinks from $+28\%$ at the
  $45^\circ$ cap to $+9\%$ at $25^\circ$ and $+2.3\%$ at $15^\circ$ ... absolute geometry improves for
  every solver under the tighter cap (G-BL $f_2$ rises from $0.295$ to $0.405$ to $0.448$), because
  window filtering removes the low-quality high-squint options." Correctly explained as a ceiling
  effect — the baseline improves, so the *relative* advantage shrinks. **Observation, not defect**;
  this is one of the paper's better-reasoned results, and the mechanism is stated.
- **C5-h (~1419-1441, operational guideline).** This paragraph is materially more cautious than the
  abstract: it conditions on $N\lesssim100$, on squint-agile platforms, and on the $45^\circ$
  experimental envelope, and it says G-SM "attains the highest radiometric quality at a substantial
  coverage cost, so the greedy choice follows the mission's priority". **Observation — the
  discussion is honest. The mismatch is between the discussion and the abstract/conclusion.**
- **C5-i (~1287-1293, chance control).** "5,000 random task selections per scenario produce mean
  $f_1^*=0.527 \pm 0.003$, a 90th percentile of $0.930 \pm 0.008$, and a best sample of $1.000$ ...
  Unconstrained random selection never exceeded the greedy baseline". This is a good control — and
  it also shows that coverage is a weak discriminator (random selection reaches 93% of the greedy
  profit at the 90th percentile). If coverage is nearly free, the "14% coverage cost" that anchors
  the whole value argument is a modest price. The paper does not use the control this way.
- **C5-j (~1295-1309, search-budget control).** "Doubling the budget ... shifts quality by at most
  $+1.64\%$ ... so the sub-$2\%$ dense-regime margins reflect coverage pressure and not premature
  convergence." Tested on ten scenarios (5 S3 + 5 S4). The control bounds the *within-basin* search
  improvement; it cannot bound the 16% $f_3$ gap to G-SM's region (C4-b), because that region lies
  outside the hot-started basin. The inference from "+1.64%" to "not premature convergence" is
  broader than the test.
- **C5-k (~1330-1337, finding 1 and 2 wording).** Finding (1) "the quality advantage of
  multi-objective optimization saturates with target density ($+33.7\%$ in $f_2$ at $N=20$ falling to
  $+0.3\%$ at $N=500$)" and finding (2) "the third objective is density-dependent rather than
  redundant". Both described as "geometric properties" in the sentence that follows. But finding (5)
  says the coverage convergence is initialisation-dependent, and §6.4 says the compression is of the
  seeded front. The five findings are internally inconsistent about which are geometry and which are
  solver.
- **C5-l (~1533-1535, conclusion).** "The within-schedule trade-off persists at every density
  (negative correlation ...), so the dense-regime convergence is an empirical effect of the schedule
  geometry, not a redundancy between objectives." The inference from "correlation stays negative"
  to "not redundant" is the paper's key non-redundancy argument. A negative correlation establishes
  conflict; it does not establish that the objective set is non-redundant (see C2-a: the two
  objectives are both monotone products of the same two angles). The paper never performs the
  decisive test of objective redundancy — an objective-reduction study showing that removing $f_3$
  changes the selected schedules — beyond the $+4.9\%$ knee margin at S1.
- **C5-m (~1373-1376).** "the present claims therefore concern the marginal value of adding physical
  objectives rather than profit-oriented search alone." Good scoping sentence. It should also appear
  in the Abstract.

### Chunk 6 (`sections/_ablation_section.tex`, all 181 lines)

- **C6-a (~128-137).** "Variant C (no incidence) produces no measurable change in any reported
  metric." Table values confirm: S1 A vs C is $f_1^*$ $0.850$/$0.845$, $f_2$ $0.376$/$0.375$, $f_3$
  $0.698$/$0.703$, $f_1/n$ $5.99$/$5.86$, $n_\text{sel}$ $15.6$/$16.0$. Everything within noise.
  The stated reason is that incidence "acts as an approximately common scale within each window".
  **This is the ablation's most consequential result and it is treated as a supporting detail.**
- **C6-b (~15 and ~133-137).** Note the internal tension: variant C is *defined* as removing
  $\theta_{\text{elev}}$ from both objectives, and the prose then says "The incidence conflict of
  \S\ref{sec:pareto-coupling} therefore operates through the across-window/aggregate geometry rather
  than through per-window selection." That is an assertion about where the conflict operates, not a
  measurement. Nothing in the paper measures an across-window θ decision.
- **C6-c (~35-42).** S5 (along-track spread) and S6 (narrow-window clusters) are genuine stress
  classes beyond the density axis. Credit.
- **C6-d (~163-167).** "B shows a small $f_2$ difference that is significant at S6 ($+4.6\%$,
  $p = 1.2\times10^{-5}$) but not at the corrected threshold at S5 ($+3.2\%$, $p = 0.046$)". Removing
  the squint component makes post hoc $f_2$ *better* at S6. Directionally opposite to S1 (where B is
  $-6.2\%$ on $f_2$). Unexplained; a reader cannot tell whether this is a real geometry effect or
  crowding noise.
- **C6-e (~43-50).** The degradation convention is stated carefully (raw-profit means for
  $\Delta f_1^*\%$, direct relative change for $f_2$/$f_3$, opposite signs). Good practice — but it
  means the table mixes two sign conventions across columns, which is a reader hazard.
- **C6-f (~173-181).** "the physical quality objectives add value mainly in the sparse regime, and
  primarily through radiometric quality ... by $N \geq 300$ the choice of physical objectives is
  numerically irrelevant to outcomes." This is the paper's own best summary of its ablation, and it
  is a *negative* result about the third objective at operational density. It is not in the
  Abstract.

### Chunk 7 (`highlights.tex`, 30 lines)

- **C7-a (line 22).** "Third objective adds +40\% (NESZ-ordering index) at sparse density, 15\%
  coverage cost" — the $+40\%$ is MOEA-3 versus G-BL (the whole three-objective method), not the
  third objective, whose measured contribution is $+4.9\%$ ($+6.2\%$ unmatched). This is the
  clearest factual misattribution in the submission package.
- **C7-b (line 19).** "Quality gain shrinks with target density; negligible beyond N = 150 targets"
  — carries none of the hot-start conditionality that the Discussion says is essential (finding 5).
- **C7-c (line 16).** "Imaging quality (NESZ, resolution) added as multi-objective scheduling
  targets" — accurate as a novelty statement relative to the cited prior work, and appropriately
  modest (it claims formulation, not superiority).
- **C7-d (line 25).** "Quality edge contracts with agility: greedy suffices under narrow squint
  envelopes" — matches §7.2. Fine.

---

