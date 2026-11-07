# Methodology Review — paper1

Seat: Reviewer 1 (methodology). Expertise: evolutionary multi-objective optimisation, benchmark design, statistical reporting.
Manuscript: `papers/single-sat-quality/small-paper-ijae.tex` + `sections/_ablation_section.tex`; figures regenerated 2026-11-06.
Date: 2026-11-07.

## Canary
1. Read-only: I modify no file except this report.
2. Every finding quotes the exact manuscript text, with section and tex line.
3. No fabricated facts; no claims about cited works beyond what the manuscript states.
4. Numbers quoted as printed; where I recompute, I say so explicitly and show the arithmetic.
5. No network access.
6. Genuine strengths and weaknesses.
7. Stdout at most 5 lines.

## Summary judgement
The design is above the norm for this literature: a controlled objective-function ablation with a true null model, a replicated-run variance study (400 solves), matched selection rules for the third objective, and a hypervolume result demoted against the authors' own interest. Three structural issues remain, and one of them is new to this round. First, the paper's own null model reaches *full coverage* at N=20 (variant D, f1* = 1.002) while the three-objective arm sits at 0.850 — so the coverage cost is not, as framed, a consequence of buying quality; it is at least partly a consequence of selection pressure under three objectives. Second, the density boundary is measured under a resource cap that binds in half the dense scenarios, and under a hot start, simultaneously. Third, several statistics are still displayed at a scale whose thresholds were calibrated for a different statistic.

## Strengths
- **The ablation has a real null model.** Variant D "removes the physical objectives altogether" (ablation l.31-35) and the paper treats its higher coverage as a finding rather than an embarrassment.
- **Replication is done and reported honestly.** "At the class-mean level, the quality metrics (f2, f3) shift by less than 0.01 in every class, and f1* by less than 0.04 in the worst sparse-class pair" (l.903-905), with the residual process noise named as not identified (l.911).
- **The hypervolume caveat is executed, not just stated.** "its ranking inverts if the single-point G-SM is included (its HV of 0.2341 exceeds MOEA-3's 0.0893)" (l.831-833); G-SM is therefore excluded from Table 4.
- **Matched selection rule for the third objective.** "+4.9% (p = 2.3×10^-11, 47 of 50), against +0.05% (p = 0.86) for a radiometric-blind rule" (l.1262-1263) with the Das-Dennis p=4 control (l.1269-1272).

## Findings

### R1-01 [MAJOR] The coverage cost of the multi-objective arm is not established as a trade-off: the no-physics null reaches full coverage
- Quote (ablation Table 6, S1): variant A `f1* = 0.850±0.123`, `n_sel = 15.6±2.6`; variant D `f1* = 1.002±0.011`, `n_sel = 19.5±0.7`, `Δf1*% = −18.0%` (p=3.4×10^-9). Against the framing "thereby producing a genuine 'quantity versus quality' Pareto trade-off" (l.374-376) and "at S1 MOEA-2 improves f2 by +33.7% ... while accepting a 14% coverage reduction" (l.932-935).
- Problem: variant D optimises essentially one objective (two constants plus profit) and reaches *above* the greedy anchor at S1, while the three-objective arm loses 15% coverage. So the coverage deficit is not the unavoidable price of the quality axis: a search that carries no quality objectives recovers the coverage. Two readings follow, and the paper does not separate them: (i) quality costs coverage (the paper's reading), or (ii) three-objective selection pressure costs coverage irrespective of what the third objective is (a solver artefact). The paper itself concedes "the S1 coverage reversal under variant D ... currently lacks a mechanistic explanation" (l.1568-1571).
- Fix: run one diagnostic arm — MOEA-3 with f3 replaced by a *third copy of f1* (or a constant), i.e. three objectives with no quality content. If coverage still sits near 0.85, the deficit is selection pressure, not quality; if it recovers to ~1.00, the trade-off reading survives. This is one experiment on 50 S1 scenarios (~22 s each per l.815).

### R1-02 [MAJOR] Two conditioning factors load one headline boundary: 200-task resource cap and G-BL hot start
- Quote: "Both caps therefore translate into the same ceiling of 200 concurrently scheduled tasks ... 20 of 50 G-BL schedules at S3 and 27 of 50 at S4 select exactly 200 tasks" (l.597-601); and "coverage convergence toward the G-BL anchor is conditional on the hot start" (l.1415-1416).
- Problem: the density boundary ("beyond N ≈ 150 ... quality margins below 2%") is measured on a population that is (a) seeded at the coverage corner and (b) capped at 200 tasks in roughly half of S3/S4. §3.3 splits the bound/unbound subpopulations by quality profile but the logistic midpoint N50 (l.1107-1114) is fit to the pooled mix. Two separate mechanisms are being reported as one boundary.
- Fix: refit N50 on C2-limited scenarios only (the unbound subset), and report the bound subset separately; one sentence in §6.3 and one in §7.4. The data already exist.

### R1-03 [MAJOR] Figure 1 displays δ_pairs as "Cliff's δ" and draws the Romano negligible band on it
- Evidence: Fig. 1 right-panel axis reads "Cliff's δ (effect size)" (`figures/fig1_hypervolume.pdf`); the caption (l.1005) correctly says "the matched-pairs sign statistic δ_pairs = (W−L)/n ... the gray band marks the negligible-effect range (|δ|<0.147 of Romano2006; shown for reference, as the conventional unpaired δ is weaker ...)". §5.3 states the two forms differ in magnitude "(e.g. +0.57 versus +0.88 for the sparse MOEA-3/MOEA-2 f3 comparison)" (l.849-851).
- Problem: the text was corrected in the 2026-11-03 round (R13 naming item), the figure was not. A reader of the figure applies Romano's thresholds to a statistic on roughly half the scale, which is exactly the error §5.3 warns about.
- Fix: relabel the axis "δ_pairs (matched-pairs sign statistic)" and drop or restyle the shaded band as "for reference only".

### R1-04 [MINOR] Figure 5 legend claims a 95% interval that the text says is not one
- Evidence: `figures/fig7_corr_density.pdf` legend reads "independent-angle null (shuffle 95%)"; the caption (l.1225-1227) says "the shaded band is the observed shuffle range of the independent-angle shuffle null (20 shuffles per class)", and the body says "a nominal 95% interval would require an order of magnitude more draws" (l.1166-1168).
- Fix: relabel the legend "observed shuffle range (20 shuffles/class)".

### R1-05 [MINOR] Figure 6's caption promises significance marks it does not draw
- Evidence: caption (ablation l.110) — "Asterisks mark paired Wilcoxon comparisons against A significant at the Bonferroni threshold (p<0.05/12, applied within each reported metric)"; source `experiments/gen_fig6_ablation.py:187` marks asterisks only `if metric == "f1"` (comment: "Statistical claim in the paper concerns normalized profit f1*").
- Problem: caption and code disagree. The text reports significant f2 (variant B, p=1.1×10^-5) and large f3 differences, so a reader expects marks there.
- Fix: amend the caption to "asterisks mark the f1* comparisons" — that is what the code does and what the pre-specified claim is.

### R1-06 [MINOR] Sign convention flips between Figure 6 / Table 6 and §6.5 prose
- Evidence: `gen_fig6_ablation.py:135` computes `deg = (mean(A) − mean(V)) / mean(A)`, so a positive bar means the variant is worse; the figure footnote says "negative = variant outperforms A". §6.5 states the opposite convention for quality: "Percentages quoted for the quality metrics f2 and f3 in the text follow the direct relative-change convention (V−A)/A (negative values indicate degradation)" (ablation l.44-47).
- Problem: the same quantity appears as +25 in the figure and −25% in the text. Both are defined, but a reader checking one against the other will conclude an error.
- Fix: use one sign convention in figure and text; if the current one is kept, repeat the convention line in the f2/f3 panel labels.

### R1-07 [MINOR] The search-budget control cannot defend the claims it is cited for
- Quote: "shifts quality by at most +1.64% relative to the standard budget. That shift is the same order as the sub-2% margins it is meant to defend, so the control alone cannot separate premature convergence from all runs reaching the same coverage wall" (l.1364-1368).
- Assessment: the sentence is honest, and the bound/unbound split is offered as the substitute. But the budget control uses 5+5 scenarios, and the only place a budget effect could still matter is S1 where margins are large — where it was not run.
- Fix: run the doubled-budget control on 5 S1 scenarios (cheapest place for the effect to show) or delete the control from the robustness section and cite the bound/unbound split alone.

### R1-08 [MINOR] Reproducibility statement contradicts the design section
- Quote: Data Availability — "Solver code (NSGA-III via pymoo 0.6.1.6), scenario generators, fixed seeds and configurations ... are available" (l.1649-1651); §5.4 — "the NSGA-III sampling seed is fixed at the library default while operator-level random draws are not pinned" (l.897-899).
- Problem: "fixed seeds" will be read as full determinism. The paper's own replicated-run section says otherwise.
- Fix: rewrite the Data Availability clause to "fixed scenario seeds and solver configuration; process-level random draws are not pinned, see §5.4".

## Questions to authors
1. For variant D at S1 (f1* = 1.002, n_sel = 19.5 vs A's 15.6), what stops the three-objective arm from reaching the same coverage? If the answer is "reference-direction selection pressure", the phrase "quantity versus quality Pareto trade-off" needs qualification.
2. Is the N50 logistic fit computed on all scenarios or only C2-limited ones? If all, please refit on the unbound subset.

## Arithmetic checked (recomputed, stated as such)
- Variant B at S1: f3 0.574 vs A 0.698 → (0.574−0.698)/0.698 = −17.8% (text says −18%) ✓. f2 0.353 vs 0.376 → −6.1% (text says −6.2%) ✓.
- Variant D at S1: f3 0.525 vs 0.698 → −24.8% (text says −25%) ✓.
- Abstract +40%: 0.698/0.497 = 1.404 → +40.4% ✓. +33.7% per-scenario ratio vs +33% pooled: 0.393/0.295 = 1.332 ✓ consistent with the stated dual reporting.
