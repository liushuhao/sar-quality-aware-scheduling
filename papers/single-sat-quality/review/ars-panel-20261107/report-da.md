# Devil's Advocate Report — paper1

Seat: Devil's Advocate (fixed fifth seat).
Manuscript: `papers/single-sat-quality/small-paper-ijae.tex` + `sections/_ablation_section.tex`.
Date: 2026-11-07.

## Canary
1. Read-only: I modify no file except this report.
2. Every finding quotes the exact manuscript text, with section and tex line.
3. No fabricated facts; a negative claim carries the same evidence burden as a positive one.
4. Numbers quoted as printed.
5. No network access.
6. Genuine strengths and weaknesses.
7. Stdout at most 5 lines.

## Strongest counter-argument

The paper asks the reader to accept that a three-objective physics-aware search adds value in sparse regimes. Its own table places the value outside the MOEA arm: at S1 the one-line squint-minimising heuristic G-SM reaches f2 = 0.389 and f3 = 0.722, both *above* MOEA-3's 0.376 and 0.698, at f1* = 0.51; G-BL reaches f1* = 1.00 at f2 = 0.295, f3 = 0.497. So two greedy rules — one that maximises coverage, one that minimises squint — bracket the MOEA-3 knee on both axes. At S4 the paper itself concedes that G-SM "reaches f3 ≈ 0.79 at f1* ≈ 0.37 ... a region outside the MOEA-3 surface". The paper's residual defence is that MOEA-3 supplies "the coverage-stratified frontier itself, which the one-line heuristic cannot enumerate" (l.1477-1479), but no experiment tests whether a mixture of the two greedy schedules — a random portfolio, or a per-scenario choice of which greedy rule to run — reproduces that frontier. If it does, the multi-objective apparatus is bookkeeping: the planner can obtain the same exchange rate by running two trivial heuristics and picking a point. The paper's decisive claim would then reduce to the measurement, not the method — which would still be worth publishing, but not under this title.

## Issue list

### DA-01 [CRITICAL] The frontier defence is untested against a two-heuristic portfolio (dimension: alternative explanation)
- Quote: "MOEA-3's remaining value is the coverage-stratified frontier itself, which the one-line heuristic cannot enumerate" (l.1477-1479).
- Evidence, stated both ways:
  - Against the MOEA: Table 3 S1 — G-SM f1* = 0.51±0.16, f2 = 0.389±0.086, f3 = 0.722±0.058; MOEA-3 f1* = 0.85±0.12, f2 = 0.376±0.050, f3 = 0.698±0.039. S2 — G-SM f2 = 0.357, f3 = 0.735 against MOEA-3's 0.329 and 0.597. So at two of four densities the greedy heuristic is at or above the MOEA on both quality axes, at lower coverage. §6.4 also states "G-SM reaches f3 ≈ 0.79 at f1* ≈ 0.37 at S4, a region outside the MOEA-3 surface" (l.1141-1143).
  - For the MOEA: at S1, MOEA-2's f2 (0.393±0.055) is marginally above G-SM's (0.389±0.086), and at S3/S4 the MOEA arms sit 0.001-0.002 above G-BL in f2. So the MOEA does not lose everywhere on f2; the margin over the greedy endpoints is ≤1% of the index in the best case.
- Problem: the frontier claim is the last standing argument for the method, and it is asserted rather than measured. What is missing is the comparison that decides it — a schedule family interpolating between G-BL and G-SM (e.g. apply squint-minimisation to a random fraction q ∈ {0, 0.25, 0.5, 0.75, 1} of selected tasks), evaluated on the same three coordinates. On the f3–coverage plane the MOEA knee lies inside the range the two greedy rules already span; on f2 the MOEA-2 knee is at most ~1% above both endpoints, within one standard deviation. If the interpolated family reaches the knee, the multi-objective apparatus is bookkeeping; if it falls short, the paper finally has a measured answer to the question every referee will ask.
- What would settle it: that envelope, reported on the same three coordinates as Fig. 4 and Table 3. No such test exists anywhere in the manuscript or in `experiments/`.

### DA-02 [MAJOR] The headline numbers are attributed to multi-objective optimisation although a greedy rule produces them (dimension: over-generalisation)
- Quote: abstract "sparse request sets reward re-optimisation over the greedy coverage baseline: +34% geometric-index quality at a 14% coverage cost and +40% radiometric-index quality at a 15% cost" (l.44-47); §6.2 "G-SM ... improving f3 from 0.497±0.044 to 0.722±0.058 (+45%)" (l.1040-1042).
- Problem: the +45% that a one-line heuristic achieves exceeds the +40% the abstract attributes to re-optimisation, at a larger coverage cost. The comparison is technically valid (it is stated against G-BL), but the reader's natural inference — that multi-objective search is what buys the quality — is not what the data show.
- Fix: name both comparators in the abstract, or make the headline a range: "+40% radiometric at 15% coverage cost (a squint-minimising heuristic reaches +45% at 49% cost)".

### DA-03 [MAJOR] The "quantity versus quality trade-off" framing is undercut by the no-physics null, which achieves full coverage (dimension: logic chain)
- Quote: "All quality objectives use the mean over scheduled tasks, making them independent of the number of scheduled tasks m = |S| and thereby producing a genuine 'quantity versus quality' Pareto trade-off" (l.374-376). Against ablation Table 6 S1: variant D (no physics) `f1* = 1.002±0.011`, `n_sel = 19.5±0.7` versus variant A `f1* = 0.850±0.123`, `n_sel = 15.6±2.6`.
- Problem: if removing all physical objectives returns coverage *above* the greedy anchor, then the 15% coverage loss of the full-physics arm is not the price of quality — it is at least partly the price of optimising three objectives. The paper's own limitation admits "the S1 coverage reversal under variant D ... currently lacks a mechanistic explanation" (l.1568-1571). Until that is explained, "genuine trade-off" is an interpretation, not a measurement.
- Fix: one diagnostic arm (three objectives, no quality content) as described in R1-01, or rephrase the trade-off claim as conditional on the objective set.

### DA-04 [MAJOR] The density boundary is quoted with more precision than the estimate supports
- Quote: abstract "it vanishes beyond N ≈ 150, where the multi-objective fronts converge to the greedy coverage anchor with quality margins below 2%" (l.51-53); §6.3 "only the two sparse densities carry informative deficit proportions (80% and 10%), while the four denser points are all at most 1%, so the bootstrap confidence interval is wide (N50 ∈ [37, 64])" (l.1110-1114); §7.4 "the threshold should be read as family-specific rather than platform-independent" (l.1555-1559).
- Problem: the boundary rests on two informative density points, is fitted through four points pinned at zero, and its own CI spans 37–64 — yet the abstract states "vanishes beyond N ≈ 150" as if it were a measured threshold. The paper says all of this in the body; the front matter does not.
- Fix: carry the CI into the abstract ("an effective boundary near N ≈ 50, CI [37, 64]; no scenario beyond N = 150 shows a coverage deficit above 5%").

### DA-05 [MINOR] The abstract reports the favourable selection rule only
- Quote: "+4.9% third-objective margin under a matched selection rule that also accounts for radiometric quality" (l.47-48); §6.4: "+4.9% ... against +0.05% (p = 0.86) for a radiometric-blind rule" (l.1262-1263).
- Problem: the paper is transparent in the body — two rules, one favourable, one null — but the abstract cites only the favourable one, which reads as selecting the statistic that supports the claim.
- Fix: one clause naming the null result, or drop the number from the abstract and keep it in §6.4.

## Ignored alternative explanations
1. **Portfolio / mixture** (DA-01) — the obvious cheap competitor to a Pareto front, never tested.
2. **Selection-pressure artefact** (DA-03) — three objectives vs one may cost coverage independent of objective content.
3. **Window-edge baseline artefact** — G-BL places tasks at earliest feasible time, which sits near the squint cap; the measured quality gain may be a property of that placement rule rather than of quality awareness (R2-03 in the previous round; not resolved by narrowing the claim alone).

## Missing stakeholder perspectives
- **Mission planner with a pass-planning tool**: would the frontier be usable, or is the two-boundary rule the only actionable output?
- **Payload/PRF engineer**: the schedules require a timing design the paper excludes; no seat in the review panel can validate whether such a platform exists.

## Observations (non-defects)
- The paper prints the result that damages its own headline (G-SM exceeding MOEA-3 in f3 at every density). That is a mark of good faith, and it is why the remaining issue is framing rather than concealment.
- The hypervolume demotion and the G-SM exclusion from Table 4 are correct calls, made against the authors' own interest.
