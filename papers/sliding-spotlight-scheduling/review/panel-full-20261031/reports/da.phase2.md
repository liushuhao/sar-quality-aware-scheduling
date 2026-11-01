contract_role: da

## Dimension Scores

### D1: methodology_rigor

score: not_assessed

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: warn
trigger: "the stated scope of a claim exceeds what the evidence licenses"

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

The manuscript does several things that adversarial reviewers rarely get to credit. It separates the construction face from the search face and measures rather than asserts that separation; it reports failed pre-registered criteria instead of re-tuning them; it labels the caliber of each reading and keeps the fixed-dwell counterfactual's repair rules apart because their span is rule-dependent; and it refuses to plot an infeasible cell as zero coverage. Those are the marks of an argument built to survive contact with a hostile reader, and they are why this review lands no singleton rejection-level defect: the CRITICAL table is empty by design, not by default.

The strongest counter-argument is that the headline measures a bookkeeping decision rather than a physical cost. Reduce the model to what actually moves. The mode assignment is frozen, the resolution identity for sliding spotlight and spotlight cannot fail, so the only exclusion the requirement can exert is the stripmap antenna floor; and the paper's own decomposition assigns 20.0 of the 26.0-point drop and 44.8 of the 46.6-point drop to that floor. The body then concedes that part of that floor-dominated cost is the comparability policy, because the registered selection policy would re-route such an order to sliding spotlight at moderate squint and the freeze forbids exactly that rescue. So the quantity the abstract presents as what tightening costs is, by an unstated fraction, the price of a controlled-experiment convention. What survives as a genuine dwell-mechanism reading is the no-stripmap family, whose response the paper itself reports as flat within 0.27 points with an as-placed cost of 2.36 points. A skeptical reader can restate the whole result more parsimoniously: under a frozen routing and one greedy construction, coverage is nearly insensitive to the requirement except where the antenna floor makes service arithmetically impossible. That alternative fits every reported number, needs no claim about endogenous dwell trade-offs, and is the same "arithmetic, not search" reading the authors themselves give the control family.

The coherence weakness is therefore not that the chain is broken but that its load-bearing links are qualified far from where the claims are made, and that two attributions rest on alternative explanations the paper does not exclude. The abstract carries the scope of the freeze in one clause and then attributes the drop to a physical floor; the served-priority objective is described as the only objective while the paper's own served and priority fractions show a construction that keeps a proportional, not a priority-selected, slice of the task set; the curve is established as construction-carried but not as construction-invariant; the fixed-dwell failure rate is robust to repair but maximally sensitive to the baseline convention that defines it; and the inference from a search that never beats its own seed to the claim that the problem is "essentially solved by a single construction pass" is equally consistent with a solver too weak to contribute. None of these invalidates the reported measurements. Each materially weakens the interpretation built on them, and each is repairable by an arm, a bound, or a rewriting of the claim rather than by new physics.

#### CRITICAL

| # | Issue | Evidence Anchor | Confidence |
|---|---|---|---|

#### MAJOR

| # | Issue | Evidence Anchor | Confidence |
|---|---|---|---|
| M1 | The abstract attributes the headline drop to the stripmap floor, while the scope section concedes that part of the floor-dominated cost is the comparability policy; the policy share is never bounded, so the headline's physical interpretation is not established as stated. Remedy: quantify or bound the policy component with a routing-free arm, or carry the qualifier into the abstract and conclusion. | text: §abstract vs. §sec:scope "stripmap floor accounting for 20.0 and 44.8 of those points" against "part of the floor-dominated cost is the comparability policy, not the platform" | 5 — direct juxtaposition of abstract and scope text within the same manuscript |
| M2 | The stated objective is served priority, but the paper's own reading shows the served set is a near-proportional slice of the task set, so the priority weighting carries almost no selection pressure; a priority-blind construction produces exactly this pattern. The objective is therefore measured, not demonstrated to be optimized. Remedy: a priority-aware selection arm, or explicit acknowledgement that the metric reduces to served-task fraction in this scenario set. | text: §sec:demand "the uniform random priorities are close to inert in practice" with "a proportional slice of the task set rather than a priority-selected one" | 4 — the paper's own served-versus-priority fractions at s=0.8/0.9/1.0 |
| M3 | The curve is shown to be construction-carried but not construction-invariant: the anchor's deterministic pass can gain or lose a task between neighbouring requirements, and the only alternative construction tested is anchor-free random initialization. A different selection rule could produce a different shape, so "what tightening costs" is established for one heuristic, not for the problem. Remedy: at least one second principled construction (priority-aware greedy) on the same cells. | text: §sec:dip "at a given requirement that pass can serve one task fewer or one task more than at the neighbouring requirement" and §sec:faces "a construction property rather than a search artifact" | 4 — the paper's own attribution and its stated probe design |
| M4 | The fixed-dwell violation rate is described as the robust reading, but its robustness is to the repair rule only: the same fixed-dwell assumption yields 27-42 percent under the zero-squint instantiation and zero under the conservative pre-shrunk instantiation. No realistic mid-squint baseline is run, so the failure of the fixed-dwell assumption is a property of the chosen dwell convention, not of the assumption as a class. | text: §sec:counterfactual "it is the robust, repair-independent reading of the counterfactual" against the conservative arm's "no violating pair by construction" | 4 — two arms of the same counterfactual with opposite violation outcomes |
| M5 | "Essentially solved by a single construction pass" is inferred from one evolutionary search failing to beat its own seed at the registered budget and on a 16-fold probe covering 40 of 260 cells; the paper's own anchor-free arm, which returns no feasible individual on 12 of 40 cells, is equally consistent with an underpowered solver. The inference needs either a stronger search or an upper bound before it can be stated as a problem property. | text: §sec:faces "essentially solved by a single construction pass" | 3 — the budget and probe coverage are stated by the paper itself, so the bound on the inference is visible |
| M6 | The 50-task family's monotonicity failure is simultaneously reported as a result about the scenario set and disclaimed as carrying no statement about the demand axis; the same 0.268 and 0.359 percentage-point movements cannot support both readings. If they are anchor granularity, S1's failure is a property of the construction and should be labelled as such wherever it is counted as a result. | text: §sec:dip "no statement about the demand axis is made from a movement in the third decimal place" against §sec:criteria "both failures are reported as results about this scenario set" | 4 — two stated positions about the same pair of numbers |
