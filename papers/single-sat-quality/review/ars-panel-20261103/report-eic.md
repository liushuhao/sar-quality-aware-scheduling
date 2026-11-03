# Journal-Fit Review — paper1

Seat: Journal-Fit Reviewer (handling-editor seat), Advances in Space Research.
Manuscript: `papers/single-sat-quality/small-paper-ijae.tex` (1,588 lines) + `sections/_ablation_section.tex` (181 lines) + `highlights.tex` (30 lines).
Date: 2026-11-03.

## Canary
1. Read-only: I must not modify, create, or delete any file except my one report file.
2. Every finding quotes the exact manuscript text it criticizes, with section name and approximate tex line number.
3. No fabricated facts: I never assert what a cited reference contains beyond what the manuscript itself claims; literature gaps are phrased as candidate gaps only.
4. Numbers: I quote them exactly as printed; I never compute, alter, or correct numbers (arithmetic-consistency observations allowed only as "state A appears inconsistent with state B as quoted").
5. No network access; I do not attempt to fetch references.
6. I report genuine strengths and weaknesses; no manufactured findings, no finding quotas, no rubber-stamping.
7. My stdout is at most 5 lines; the report goes to the file.

## Summary judgement
The manuscript fits ASR well: single-agile-satellite mission planning with SAR imaging physics inside the objective space is squarely the journal's territory, and the paper states its delta against named prior work more crisply than most submissions. The body is unusually disciplined about its own limits (an explicit ordering-index defense of the NESZ objective, a deflated transition threshold, a hypervolume result that would flatter a different solver but is demoted anyway), and the Introduction's contribution list matches what the Results and Conclusion actually deliver. The problem is at the front matter: the highlights attribute the headline "+40%" to the third objective when the paper's own controlled figure is +4.9%, the abstract reports the sparse-regime gains without the hot-start anchoring that Sec. 6.6 says they depend on, and nothing in the title, abstract, or highlights tells the reader the evidence is a simulated scenario family.

## Strengths
- **The title names exactly what the paper optimizes.** "Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite: Balancing Profit, NESZ, and Geometric Resolution" (title, ~l.24) corresponds 1:1 to f_1*, f_2, f_3 in Sec. 3.2; the singular "satellite" correctly advertises the single-platform scope.
- **The boundaries are in the abstract, not only in the small print.** "Two measured boundaries delimit that gain." (Abstract, ~l.46) and "it vanishes beyond N ~ 150 ... under greedy hot-start initialization" (~l.49-51).
- **The delta against prior work is named, not gestured at.** "the closest prior work to ours ... but it omits imaging quality dimensions" (~l.228-230) and "This separates the physics from the coarse visibility composite of Kramer2025SARVis and the generic image-quality composite of Wei2025MONP" (~l.160-162).
- **The paper demotes its own strongest-looking result.** "+6.2% under the reported knee rules ... we re-selected both fronts under a matched radiometric-aware rule, which gives a controlled margin of +4.9% ... against +0.05% (p = 0.86) for a radiometric-blind rule" (~l.1189-1202).
- **It reports a control that damages its own headline.** "random initialization attains higher f_2 at sparse density (0.505 vs. 0.395 at S1, +28%)" (~l.1264-1266), and adds: "the sparse-regime margins are anchored-front values" (~l.1269-1271).
- **Limitations reports an unexplained result as unexplained.** "the S1 coverage reversal under variant D (\S\ref{sec:ablation}) currently lacks a mechanistic explanation" (~l.1486-1490).

## Findings

### EIC-01 [MAJOR] Highlights credit the third objective with the whole solver-vs-greedy difference
- Quote: "Third objective adds +40\% (NESZ-ordering index) at sparse density, 15\% coverage cost" (Highlights, bullet 3, highlights.tex ~l.22)
- Problem: +40% is the MOEA-3 versus G-BL difference in f_3 (Table 1: 0.698 vs 0.497), i.e. the effect of the entire multi-objective search relative to a physics-blind greedy baseline. The paper's own measurement of what the *third objective* contributes is "+6.2% under the reported knee rules" and, under a matched selection rule, "+4.9%" (~l.1189-1202). The highlight is therefore an attribution error of roughly an order of magnitude, and it contradicts the abstract, which keeps the two figures apart ("+40\% radiometric-index quality ... with a controlled +4.9\% third-objective margin", ~l.44-46). Editors see highlights before the manuscript does; this one misstates the central controlled result.
- Fix: Rewrite bullet 3 as two claims, e.g. "Physics objectives raise NESZ-ordering quality +40% at 15% coverage cost (sparse)" and "Third objective adds a controlled +4.9% margin beyond a matched two-objective front". Keep the parenthetical "(NESZ-ordering index)".

### EIC-02 [MAJOR] Nothing in the title, abstract or highlights says the evidence is simulated
- Quote: "Across 200 scenarios spanning 20 to 500 targets in a two-orbit horizon, sparse request sets reward re-optimisation: +34\% geometric-index quality at a 14\% coverage cost" (Abstract, ~l.42-45)
- Problem: The scenarios are generated, not flown: "All scenarios share a common satellite platform abstracted as a generic C-band Stripmap SAR with bilateral-looking capability" (Sec. 5.1, ~l.712-714), with energy and memory budgets in "arbitrary units" (~l.559-560). The word "synthetic" appears once, in Limitations ("estimated within this synthetic, static scenario family", ~l.1473-1475). An ASR reader of the abstract alone can reasonably read "+34% at a 14% coverage cost" as an operational or flown result. This is the one place where an editorial reader would feel the framing is not fully candid.
- Fix: Add one clause to the abstract's scenario sentence ("in 200 simulated scenarios") and one to the highlights. No change to the numbers.

### EIC-03 [MAJOR] Abstract qualifies the vanishing boundary with the hot start but not the sparse-regime gains
- Quote: Abstract: "it vanishes beyond N ~ 150, where the multi-objective fronts converge to the greedy coverage anchor with quality margins below 2\% under greedy hot-start initialization" (~l.49-51). Body, Sec. 6.6: "Because the headline experiments hot-start from G-BL, the sparse-regime margins are anchored-front values, and a merged hot-start-plus-random-init front could extend the quality--coverage envelope beyond either run alone." (~l.1269-1272)
- Problem: The condition is attached asymmetrically. The body says the *sparse* margins are anchored-front values too, and the random-initialization control shows a strictly better f_2 at sparse density (0.505 vs 0.395 at S1) at a large coverage cost. The abstract's unqualified "+34%/+40%" therefore claims more than the body does. Limitations narrows the condition further again ("the coverage convergence reported here is conditional on this initialization", ~l.1483-1485), so three places in the manuscript give three scopes for the same dependency.
- Fix: Use one scope everywhere. Recommended: abstract and Conclusion say "sparse-regime margins are front values obtained under G-BL hot-start; the frozen coverage anchor is itself initialization-dependent". Sec. 7.4 should then state the same scope rather than the narrower "coverage convergence" one.

### EIC-04 [MAJOR] The originality delta is argued against prior work but never measured against it
- Quote: "To our knowledge, no existing SAR scheduling method treats continuous, physics-derived quality functions as decomposed optimization objectives in their own right" (Sec. 2.1, ~l.248-252), against a Related Work that names five prior SAR MOEA schedulers (~l.225-244).
- Problem: Every quantitative comparison in the paper is against the authors' own greedy baselines; no cited prior method is reimplemented or compared, and the paper does not say so in a place a referee will look. Sec. 4.1 disclaims only *algorithmic-family* comparisons ("A comparison across algorithmic families ... is left to future work", ~l.605-607) and Limitations disclaims only learning-based schedulers (~l.1508-1512). The result is a gap between how the contribution is positioned (a delta over prior SAR scheduling) and what is evidenced (an internal ablation of objective sets). For an ASR editor this is the most likely source of a referee objection, and it is cheap to defuse.
- Fix: Add one sentence to Related Work and one to Limitations stating that no prior SAR scheduling method is reimplemented, why, and that the quantitative claims are therefore scoped to "what physical objectives buy inside one solver family against greedy baselines". That sentence converts an implicit overclaim into an explicit scope.

### EIC-05 [MINOR] The title sells NESZ; the body sells an ordering proxy
- Quote: Title "Balancing Profit, NESZ, and Geometric Resolution" (~l.24); body: "f_3 should be read as a geometry proxy rather than an absolute NESZ ranking across widely separated incidence angles" (Sec. 3.2, ~l.425-428).
- Problem: The paper's own modeling note says the objective suppresses a sin(theta) factor that "varies by roughly 2.4x" over the tested incidence range (~l.426-427). A title-level reader will read "NESZ" as a radiometric quantity; the paper sells a monotone index. The honest name for f_3 is a NESZ *ordering* index, which is exactly what the highlights call it ("NESZ-ordering index").
- Fix: Either retitle ("...Balancing Coverage, NESZ-Ordering, and Geometric Resolution") or add the qualifier to the abstract's first mention of NESZ. Cheapest is the abstract qualifier, since the highlights already carry it.

### EIC-06 [MINOR] The abstract's radiometric headline invites a reading the table contradicts
- Quote: "+40\% radiometric-index quality at a 15\% cost" (Abstract, ~l.44-45); Table 1, S1: G-SM f_3 = 0.722 +/- 0.058 versus MOEA-3 0.698 +/- 0.039 (~l.906, ~l.909); S4: G-SM 0.786 versus MOEA-3 0.680 (~l.927, ~l.930).
- Problem: A one-line squint-minimization heuristic beats both NSGA-III variants on radiometric quality at every density the table reports. The Introduction says so explicitly ("The single-point squint-minimized heuristic (G-SM) reaches higher f_3 than MOEA-3 in sparse scenarios but only at roughly half the coverage", ~l.138-139), and Sec. 7.2 is candid. The abstract is not. An editor reading only the abstract would over-value the multi-objective machinery for radiometry.
- Fix: One clause in the abstract: "...at a 15% cost (a one-line squint-minimizing heuristic beats it on NESZ at a larger coverage cost)". Short, and it removes the only abstract claim a referee can falsify from the paper's own table.

### EIC-07 [MINOR] "Single-pass" is redefined to mean a two-orbit campaign
- Quote: "Throughout this paper, ``single-pass'' denotes a single satellite operating over a two-orbit scheduling horizon (~200 min, at most one observation per target), not a single overflight." (Introduction, ~l.81-82)
- Problem: In SAR usage "single pass" means one overflight. Defining it as a ~200-minute, two-orbit, at-most-one-observation-per-target campaign is a private convention, and it recurs in the Discussion and Limitations ("the single-pass, single-satellite Stripmap setting", ~l.1461-1462). Any reader who skips two sentences carries the wrong meaning through Sections 6-7, and a referee may read it as a scope inconsistency. The definition itself shows the term was not necessary: "single satellite over a two-orbit horizon" says it without ambiguity.
- Fix: Replace "single-pass" with "single-satellite, two-orbit horizon" throughout, or move the definition into the abstract's first mention so it cannot be missed.

### EIC-08 [MINOR] Solver acronyms and scenario labels are met before they are defined, and out of order
- Quote: "it is never worse than G-BL" (~l.128); "MOEA-3 raises f_3 by +40\%" (~l.133); "G-SM reaches higher f_3" (~l.138) - all in the Introduction, while the labels are defined only in Sec. 4.1 and Table 1 (~l.576-598). Separately: "two additional intermediate classes (S7 at N = 150 and S8 at N = 200 ...)" (Sec. 5.1, ~l.747-749), while S5 and S6 are introduced only in the ablation input (~l.37-41).
- Problem: The contributions list is the section an editor distributes to referees; it uses five solver labels none of which is expanded there, and it quotes a percentage attributed to an unexpanded label. The scenario labels then appear in the order S1-S4, S7, S8, and only much later S5, S6, with no statement that S5/S6 existed all along - a reader will ask whether two classes were dropped.
- Fix: Add a parenthetical gloss at first use ("MOEA-3, the three-objective NSGA-III variant") or reorder Table 1 into the Introduction; and state the full class roster once in Sec. 5.1 (S1-S8, with S5/S6 = non-density stress classes, S7/S8 = intermediate densities).

### EIC-09 [MINOR] The abstract carries internal jargon that an ASR-wide reader cannot decode
- Quote: "with a controlled +4.9\% third-objective margin under a matched radiometric-aware knee rule" (~l.45-46); "close to the independent-angle null of -0.60" (~l.53); "coverage pressure dilutes that conflict" (~l.54).
- Problem: "Knee rule", "independent-angle null" and "dilutes" are defined only in Secs. 5.3 and 6.4. An abstract that requires three lookups is not readable by the journal's optical/astrodynamics/space-systems readership, which is the audience my seat exists to protect.
- Fix: One plain-language gloss per term, e.g. "under a matched selection rule that does not look at NESZ", "against the correlation two independent angles would produce", "weakens to between -0.13 and -0.23".

### EIC-10 [MINOR] Contribution #4 (the ablation, a quarter of the compute) is missing from the abstract and the highlights
- Quote: "A controlled ablation (four objective-function variants over six scenario classes, 300 scenarios per variant)" (Introduction, contribution list, ~l.179-184); "Each variant completes six scenario classes x 50 seeds = 300 runs (total: 1,200 runs across A-D)" (ablation section, ~l.35-36).
- Problem: The front matter describes a two-experiment paper's first experiment only. The negative-result control (variant D, "no physics") is arguably the paper's most quotable finding for an ASR reader deciding whether to read on.
- Fix: Add one highlights bullet, e.g. "Physics objectives change outcomes only in sparse, wide-envelope regimes (ablation, 1,200 runs)" - within the 85-character limit.

### EIC-11 [MINOR] Two sentences in the Discussion read as garbled
- Quote: "Taken together, these results establish that the found G-BL-seeded front near the full-coverage working point, while offering multiple quality-coverage configurations, is compressed by the geometric coupling above" (Sec. 7.1, ~l.1337-1341); "beyond N ~ 150 the found fronts converge to the greedy coverage anchor" (Conclusion, ~l.1528-1530).
- Problem: "the found G-BL-seeded front" has a displaced participle; the reader has to reparse to see that "is compressed" is the main verb. It recurs in the Conclusion, so it reads as a drafting habit rather than a slip.
- Fix: "the front we obtain near the full-coverage working point ... is compressed by ..." in both places.

### EIC-12 [MINOR] Availability and AI declarations need one pass of accuracy checking before submission
- Quote: "The companion repository is publicly available at \url{https://github.com/liushuhao/sar-quality-aware-scheduling}." (~l.1568-1569); "During the preparation of this work the author used AI-assisted tools (Claude, Codex) for manuscript preparation and revision assistance only." (~l.1547-1551)
- Problem: (a) The availability sentence is in the present tense and asserts public access; I cannot verify it offline, and if the repository is private at submission it is a false statement in a policy-checked section. (b) The AI declaration limits use to "manuscript preparation and revision assistance", while the paper reports a large computational study; the declaration should be checked against actual practice so it does not understate use in code generation or analysis.
- Fix: Confirm the repository resolves anonymously on submission day (or soften to "will be released upon acceptance"); re-read the AI declaration against what AI actually did and widen the wording if needed.

## Recommendation signal
**Minor Revision.**

Reasons:
1. Scope and audience fit are strong: single-satellite agile SAR scheduling with imaging physics in the objective space is core ASR territory, and the paper is written for mission planners, not only for SAR specialists.
2. The originality delta is stated crisply and honestly in prose, but it is never evidenced against a prior method; that is a scope statement the authors can add in one paragraph rather than an experiment they must run.
3. The body's claim discipline is above the journal's average - the NESZ ordering defense, the deflated N50, the demoted hypervolume, and the against-interest initialization control are all things referees usually have to demand.
4. The front matter does not yet match that discipline: a highlights misattribution (EIC-01), an asymmetry in how the hot-start condition is applied (EIC-03), and an undisclosed simulation basis (EIC-02) are exactly the three things an ASR editor reads first.
5. Accessibility is adequate for the journal's breadth but carries avoidable load: a private definition of "single-pass", five unexpanded solver labels in the contributions list, and out-of-order scenario classes.

Conditions I would require for an Accept verdict:
1. Highlights and abstract rewritten so that the +40% is attributed to the physics-aware solver versus the greedy baseline, the controlled third-objective margin is reported as +4.9% (or +6.2% with its rule named), and the abstract states that the scenarios are simulated. (EIC-01, EIC-02, EIC-03)
2. One explicit scope sentence in Related Work (repeated in Limitations) stating that no prior SAR scheduling method is reimplemented and that the quantitative claims are therefore confined to "what physical objectives buy inside one solver family against greedy baselines"; plus the accessibility fixes in EIC-07 and EIC-08, which cost a few lines each. (EIC-04, EIC-07, EIC-08)
