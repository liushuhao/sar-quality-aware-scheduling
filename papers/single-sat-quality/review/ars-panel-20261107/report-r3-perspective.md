# Perspective Review — paper1

Seat: Reviewer 3 (perspective). Expertise: Earth-observation mission operations, learning-based and exact scheduling methods, cross-domain transfer.
Manuscript: `papers/single-sat-quality/small-paper-ijae.tex` + `sections/_ablation_section.tex`.
Date: 2026-11-07.

## Canary
1. Read-only: I modify no file except this report.
2. Every finding quotes the exact manuscript text, with section and tex line.
3. No fabricated facts about cited works; alternative methods are named only as candidate comparators.
4. Numbers quoted as printed.
5. No network access.
6. Genuine strengths and weaknesses.
7. Stdout at most 5 lines.

## Summary judgement
The paper's real product is a measurement, not a method: where the quality–coverage exchange rate is worth paying, and where it is not. That is publishable in ASR. The gap between that product and the paper's framing is the practical one — the manuscript never tells a planner what a "+33.7% geometric quality" schedule looks like in metres, never tests whether a trivially available method (an exact solver at small N, or a portfolio of the two greedy heuristics) reproduces the result, and makes one operational recommendation (prefer coverage when timeliness matters) that no measurement in the paper supports.

## Strengths
- **The paper converts a method paper into a decision boundary.** "Mission planners can read the two boundaries as a quantitative rule for when quality-aware SAR scheduling justifies its coverage cost" (l.62-64) — this is the right ambition for ASR.
- **The exchange-rate framing is honest and useful.** "Read as an exchange rate, this favors the quality-first heuristic when coverage can be spent ... The operational choice is therefore application-side — coverage budget versus achievable quality — rather than solver-side" (l.1471-1479).
- **The envelope sweep answers the question a planner actually asks.** "MOEA-3's f2 advantage shrinks from +28% at the 45° cap to +9% at 25° and +2.3% at 15° ... absolute geometry improves for every solver under the tighter cap (G-BL f2 rises from 0.295 to 0.405 to 0.448)" (l.1485-1493). This is the paper's most decision-relevant paragraph and it sits too late.
- **The transferability claim is correctly scoped.** "the radiometric objective (f3, NESZ) does not [transfer], because optical radiometry depends on illumination and cloud cover rather than on observation geometry alone" (l.1535-1537).

## Findings

### R3-01 [MAJOR] No comparator from outside the authors' own solver family
- Quote: "A comparison across algorithmic families (e.g. NSGA-III vs. MOEA/D vs. SMS-EMOA) is left to future work" (l.650-651); "we do not benchmark against learning-based schedulers (e.g. Chen2025NeuralPriority), which represent an alternative methodological family" (l.1590-1594).
- Problem: the baselines are two greedy heuristics and a GA that the paper itself establishes is "numerically identical to G-BL in all but one scenario" (l.939-942). So four of five configurations reduce to two behaviours. The paper's claim "quality-aware multi-objective scheduling pays" is therefore measured against a coverage-only greedy rule, not against any published SAR scheduler or any exact method. The 2026-11-03 panel raised this and the resolution taken was to narrow the statement (roadmap R5 alternative branch); the narrowing appears in the text but the abstract still reads as a general result.
- Fix (cheapest first): (a) an exact MILP/branch-and-bound optimum on a handful of N=20 scenarios to anchor how far G-BL is from optimal coverage — this answers "is the greedy anchor even good?"; (b) one published heuristic from the scheduling literature adapted to the same instance format. (a) is a day of work and removes the most likely referee objection.

### R3-02 [MINOR] The quality indices are never translated into physical units
- Quote: "the knee-point +33.7% f2 gain at S1 corresponds to roughly a 25% smaller per-task geometric area factor ... the exact schedule-level area change additionally depends on the selected task mix" (l.1459-1463).
- Problem: a mission planner does not schedule in units of a dimensionless index. With the stated platform (D = 12.3 m, B = 56.5 MHz) the knee-point geometry corresponds to roughly 5.3 × 6.5 m at 30° incidence / 20° squint; a +33.7% index gain is about 25% less pixel area, i.e. from ~34 m² to ~26 m². One worked example converts the whole results section into operational language.
- Fix: one sentence in §7.2 with the metres, flagged as an order-of-magnitude example at representative geometry.

### R3-03 [MINOR] The timeliness recommendation is not backed by any measurement
- Quote: "the coverage-priority choice is the natural default when acquisition timeliness matters" (l.1518-1523), and the acknowledgement "The utility model optimizes quality and quantity without an explicit latency or urgency objective; acquisition timeliness is therefore not evaluated as a separate scheduling dimension" (l.1578-1580).
- Problem: the recommendation is plausible but unmeasured; §7.4 already says latency is out of scope. Making the recommendation while declaring the dimension unmeasured is the one place where the operational section overreaches.
- Fix: either measure the mean acquisition delay of the knee-point schedules (it is already in the schedules — a post-hoc statistic, no new runs) or soften the sentence to "would need to be evaluated".

### R3-04 [MINOR] Priority weights are uniform on 1–10; no sensitivity to skew
- Quote: "Each task is assigned a priority weight p_i drawn uniformly from the integer set {1,2,…,10}" (l.799).
- Problem: operational request streams are heavy-tailed (a few high-value targets). Under skew, coverage profit and mean quality decouple further, and the sparse-regime exchange rate could move materially. No sensitivity arm exists.
- Fix: one sentence in §7.4 naming the skew assumption explicitly as a scope limit, or a small sensitivity run at S1.

### R3-05 [MINOR] Transferability claim lacks a citation
- Quote: "the cross-track optical ground sample distance scales as 1/cos²η; the pixel area additionally takes a 1/cos η along-track factor" (l.1531-1535).
- Fix: cite a standard optical geometry reference, or mark it as a standard result.

### R3-06 [MINOR] The horizon length is fixed and its effect is never discussed
- Quote: "a single-satellite, two-orbit-horizon problem: one satellite plans observations over a two-orbit scheduling horizon (~200 min)" (l.86-88).
- Problem: the density boundary is plausibly a horizon-length artefact as much as a density effect (longer horizons give more scheduling freedom per target). The scenario library already contains one-revolution variants (S1-D, S3-D) but they are used only for robustness, not for the boundary.
- Fix: one sentence in §7.4 or a two-point comparison using the existing single-revolution variants.

## Questions to authors
1. How far is G-BL's coverage from the exact optimum at N=20? Without that number, "the greedy anchor" is a reference without a quality scale.
2. Would the sparse-regime exchange rate survive a priority distribution skewed toward 1–2 high-value targets?
3. What is the mean acquisition delay of the knee-point schedules relative to G-BL's earliest-feasible placement? The schedules already contain it.
