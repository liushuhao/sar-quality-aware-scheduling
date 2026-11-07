# Journal-Fit Review — paper1

Seat: Journal-Fit Reviewer (handling-editor seat), Advances in Space Research.
Manuscript: `papers/single-sat-quality/small-paper-ijae.tex` (1,671 lines) + `sections/_ablation_section.tex` (1,468 words) + ZH twin `small-paper-ijae-zh.tex`.
Date: 2026-11-07.

## Canary
1. Read-only: I modify no file except this report.
2. Every finding quotes the manuscript text it criticizes, with section and tex line.
3. No fabricated facts about cited works; literature gaps are phrased as candidate gaps.
4. Numbers quoted as printed; no recomputation.
5. No network access.
6. Genuine strengths and weaknesses; no quotas.
7. Stdout at most 5 lines.

## Summary judgement
Scope fit with ASR is strong and the manuscript is materially better than the 2026-11-03 round: the density boundary now carries its hot-start condition in the abstract ("under greedy hot-start initialization", l.52-53), the simulation provenance is stated ("Across 200 simulated scenarios", l.42), and the third-objective section reports both the favourable and the null selection rule (+4.9% and +0.05%, l.1262-1263). What has not changed is the front-matter attribution. The abstract and highlights still lead with "+40% radiometric / +33.7% geometric over the greedy baseline", while §7.2 of the same manuscript writes that the one-line squint heuristic "matches or exceeds MOEA-3's radiometric quality at every density" and costs 49-71% of coverage (l.1471-1479). A reader who stops at the abstract attributes to multi-objective optimisation a gain that a two-line heuristic already captures. That is the residual front-matter problem, and it is the one an ASR editor would raise first.

## Strengths
- **The claim set has been disciplined since the last round.** The abstract now states two measured boundaries rather than one unqualified gain, and the conditional clause is attached where it belongs ("where the multi-objective fronts converge to the greedy coverage anchor with quality margins below 2% under greedy hot-start initialization", l.50-53).
- **Provenance is stated in the front matter.** "Across 200 simulated scenarios spanning 20 to 500 targets in a two-orbit horizon" (l.42) removes the earlier ambiguity about whether the evidence is empirical.
- **The paper reports the result that damages its own headline.** "G-SM matches or exceeds MOEA-3's radiometric quality at every density ($f_3$ higher by +3.4%, +23.1%, +21.3%, +15.6% at S1-S4)" (l.1471-1474). Very few submissions print the number that undercuts their own method.
- **The decomposition is presented as the transferable artefact, not the ranking.** "The decomposition, rather than any single solver ranking, is the transferable contribution" (l.1537-1538) — a correct and unusually modest framing.
- **Negative results are not buried.** Contribution (iv) states that "solver outcomes become invariant to the choice of physical objectives at high target density (where the objective is retained for quality-assessment completeness rather than incremental gain)" (l.188-193).

## Findings

### EIC-01 [MAJOR] The abstract still attributes a one-line heuristic's gain to multi-objective search
- Quote: "sparse request sets reward re-optimisation over the greedy coverage baseline: +34% geometric-index quality at a 14% coverage cost and +40% radiometric-index quality at a 15% cost" (l.44-47). Against: "G-SM matches or exceeds MOEA-3's radiometric quality at every density" (l.1471-1472) and "this gain comes from the one-line squint-minimization heuristic rather than from multi-objective search" (l.1468-1469).
- Problem: "re-optimisation" is doing ambiguous work. Sparse-regime gains are real, but they are reachable by minimising squint inside each window; the marginal value of the MOEA is the *frontier*, not the endpoint. The abstract reports the endpoint.
- Fix: add one clause to the abstract naming the heuristic comparison, e.g. "a one-line squint-minimising heuristic reaches comparable radiometric quality at lower coverage; the multi-objective value added is the coverage-stratified frontier itself". Then the abstract matches §7.2.

### EIC-02 [MAJOR] The title still advertises NESZ as an optimised radiometric quantity
- Quote: title "Balancing Profit, NESZ, and Geometric Resolution" (l.24); against "It is therefore used here as a relative ordering index across observation geometries, not as an absolute radiometric prediction" (l.437-439) and "the suppressed sinθ factor varies by roughly 2.4×, so f3 should be read as a geometry proxy rather than an absolute NESZ ranking across widely separated incidence angles" (l.443-446).
- Problem: the body is scrupulous; the title and keywords are not. A SAR referee reads "NESZ" as an absolute dB quantity and will check the model against that expectation. This item was carried from the 2026-11-03 panel as pending-user and remains open.
- Fix: either retitle around "radiometric ordering" / "noise-equivalent ordering index", or add a title-level qualifier. Keywords (l.67) should carry the same qualifier.

### EIC-03 [MINOR] Abstract length and density
- Quote: l.35-65 is a single ~250-word paragraph carrying six quantified claims, two boundaries, one correlation value and an ablation count.
- Fix: split into two paragraphs (what was done / where it pays and where it does not). No content change.

### EIC-04 [MINOR] Figure 1 leads the statistical evidence with the diagnostic the paper demotes
- Quote: "Hypervolume (HV) is reported as a secondary diagnostic only" (l.826-828) and "its ranking inverts if the single-point G-SM is included (its HV of 0.2341 exceeds MOEA-3's 0.0893)" (l.831-833).
- Problem: the first figure a reader meets is the HV distribution, i.e. the metric the paper says cannot be interpreted standalone.
- Fix: swap panel order so the effect-size panel leads, or retitle the figure to say which panel is the diagnostic.

### EIC-05 [MINOR] Contribution bullet (iii) is unreadable without the Results
- Quote: l.179-184 packs four correlation values, two null references and a dilution range into one bullet.
- Fix: split into the definitional decomposition (one sentence) and the measured values (one sentence pointing to §6.4).

## Questions to authors
1. If the abstract were rewritten to attribute the sparse-regime gain to squint minimisation and the coverage-stratified frontier to the MOEA, would any claim in the paper become false? If not, why is the current attribution retained?
2. What would the title lose if NESZ were replaced by the ordering-index phrasing the body already uses?
