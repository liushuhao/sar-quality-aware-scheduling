# Devil's Advocate report — ars-panel-20261030
## Canary
1. Read-only: I must not modify, create, or delete any file except my one report file.
2. Every finding must quote the exact manuscript text it criticizes, with section name and approximate tex line number.
3. No fabricated facts: I never assert what a cited reference contains beyond what the manuscript itself claims; literature gaps are phrased as candidate gaps only.
4. Numbers: I quote them exactly as in the manuscript; I never compute, alter, or correct numbers (arithmetic-consistency observations allowed only as "state A appears inconsistent with state B as quoted").
5. No network access; I do not attempt to fetch references.
6. I report genuine strengths and weaknesses; no manufactured findings, no finding quotas, no rubber-stamping.
7. My stdout is at most 5 lines; the report goes to the file.

## Strongest counter-argument
The strongest reading of the evidence is not that physics-aware scheduling has been shown to improve SAR operations generally, but that, inside a G-BL-seeded NSGA-III experiment, a decision maker can select schedules with higher values of two surrogate indices by accepting different coverage. The paper itself says the fronts are best-known approximations, not verified Pareto sets, and that random initialization reaches higher $f_2$ at S1–S3 while merged hot/random fronts were not constructed. Dense convergence therefore characterizes the tested search family near its coverage anchor, not a necessary property of the full physical objective space.

The headline effects also depend on how a front is reduced to one schedule. MOEA-2 and MOEA-3 use different normalized-sum knee rules; the controlled $f_3$ advantage is $+4.9\%$, while a radiometric-blind matched rule yields $+0.05\%$ with $p = 0.86$. Adding $f_3$ is thus valuable chiefly when the decision rule already values $f_3$, rather than automatically producing a superior operating point.

Finally, $f_3$ is explicitly a relative ordering index, not an absolute NESZ ranking across widely separated incidence angles, and mean indices can change when the selected task subset changes. Coverage-profit loss does not establish the mission cost of dropping particular tasks, nor does an index gain establish detection, calibrated-image, or latency value. The best-coverage $+12.5\%$ $f_2$ result may be operationally useful, but the broader wording about physical necessity, greedy sufficiency, and transfer to optical scheduling outruns the demonstrated evidence.

## Findings
**DA-01** | Severity: MAJOR | Location: Objective Functions, tex lines 428–436; Abstract, tex line 136

Quote: "rather than an absolute NESZ ranking across widely separated incidence angles."; "radiometric gains (MOEA-3 raises $f_3$ by $+40\%$"

Issue: The headline calls the change a radiometric gain, but the manuscript defines $f_3$ only as a relative ordering index under an approximate model. A schedule-level mean of that index, evaluated over a changing selected-task subset, is not validated here as an absolute or calibrated radiometric-performance measure.

Why it matters: A reader can interpret the headline percentage as a physical improvement in NESZ or image utility, although the demonstrated quantity is a relative change in $f_3$. Subset composition can also contribute to the schedule mean, so the size of the index gain does not by itself establish the operational radiometric benefit.

Suggested remedy (non-binding): Consistently label the result an "$f_3$ ordering-index gain," keep the proxy qualification beside headline and conclusion numbers, and validate schedule-level $f_3$ against absolute radiometric outcomes on fixed task subsets before using stronger operational language.

**DA-02** | Severity: MAJOR | Location: Summary of Findings, tex line 1398; Robustness and Calibration, tex line 1303; Conclusion, tex line 1604

Quote: "the greedy baseline is operationally sufficient."; "We did not construct this merged reference front"; "fronts are best-known NSGA-III approximations rather than verified Pareto sets."

Issue: “Operationally sufficient” is broader than the demonstrated result. The experiments show limited measured benefit in the tested dense configuration, but they do not establish a mission-requirement threshold, exhaust alternative initializations or simple local improvements, or verify the attainable Pareto set.

Why it matters: This wording can turn a conditional algorithmic observation into an operational recommendation. Unknown global optimality does not itself disprove sufficiency, but neither does convergence to G-BL prove that G-BL meets a user's coverage, quality, priority, or timeliness requirements.

Suggested remedy (non-binding): Replace the categorical phrase with “the tested multi-objective variants provide little additional benefit over G-BL in the dense scenarios studied,” and reserve operational sufficiency for an analysis tied to explicit mission requirements.

**DA-03** | Severity: MAJOR | Location: Robustness and Calibration, tex lines 1361–1383; Mechanism of Pareto Compression, tex lines 1119–1121

Quote: "a physically forced consequence of coverage pressure"; "convergence is therefore not a budget artifact."; "on five S3 and five S4 scenarios"; "not ruling out all algorithm-specific effects."

Issue: The doubled-budget control is useful evidence, but the causal wording is stronger than that control. One budget increase on the stated scenario subset does not establish physical necessity, relax the fixed resource caps, or eliminate initialization and algorithm-specific explanations.

Why it matters: Dense convergence is a central thesis. Calling it physically forced obscures the remaining distinction among temporal packing, the binding 200-task ceiling, the G-BL coverage anchor, and NSGA-III search behavior. The manuscript's own caution about algorithm-specific effects is more defensible than the categorical claim.

Suggested remedy (non-binding): State that convergence persisted under the tested doubled budget and is consistent with coverage/resource pressure. Avoid “physically forced” and “not a budget artifact” unless resource-cap relaxation and broader search controls support them.

**DA-04** | Severity: MINOR | Location: Transferability Across Remote-Sensing Domains, tex lines 1510–1522

Quote: "the same density-dependent saturation would appear."

Issue: The optical saturation claim is stated prospectively without an optical experiment in this study. The manuscript separately acknowledges that optical radiometry differs, but differing constraints and quality models can also alter the density response itself.

Why it matters: The sentence extends an empirical, configuration-specific result to another sensing domain without evidence that the same scheduling trade-off or saturation mechanism holds there.

Suggested remedy (non-binding): Recast the sentence as a testable hypothesis—for example, that a corresponding coverage-quality trade-off may occur—and leave density-dependent optical saturation for future validation.

## Ignored alternative explanations
- **Task-subset composition:** Mean $f_2$ or $f_3$ can change because a different mixture of tasks is selected, not only because shared tasks receive better geometry. Aggregate coverage profit does not show which task types or priorities are exchanged.
- **Initialization/search basin:** G-BL seeding may shape both the found sparse fronts and dense convergence. Random initialization reaches different high-$f_2$, low-coverage schedules, and the unconstructed merged front leaves the attainable compromise set unresolved.
- **Hard resource ceiling versus temporal saturation:** Where the 200-task ceiling binds, flat coverage can reflect a cardinality cap rather than temporal packing alone. Increasing solver generations does not distinguish those mechanisms.
- **Untested cheap quality-aware comparators:** G-SM changes decisions within an earliest-start greedy structure. Coverage-preserving timing adjustments, local search, or small exact-instance benchmarks could yield part of the reported benefit without full multi-objective NSGA-III; the present controls do not exclude that possibility.
- **Other causes of correlation attenuation:** The range-compression check addresses one statistical explanation, but changing task mixtures, discrete geometry support, and common coverage constraints remain candidate contributors to the density trend.

## Missing stakeholder perspectives
- **Task owners and mission planners:** Heterogeneous priority, urgency, and the consequences of dropping particular requests are not represented by aggregate coverage profit alone.
- **Image analysts and downstream users:** Their requirements concern calibrated NESZ, resolution, detection or classification performance, and usable-image thresholds rather than surrogate-index improvements alone.
- **Operators:** Acquisition latency, downlink, energy, and schedule robustness affect whether a nominally better trade-off is executable and useful; feasibility under caps is not the same as operational value.
- **Platform and mission designers:** The strong sensitivity to squint envelope and fixed dwell makes hardware/processing choices part of the scheduling decision, but those actors' design trade-offs are outside the main evaluation.

## Observations (non-defects)
- The manuscript explicitly distinguishes best-known found fronts from verified Pareto sets and discloses the unconstructed merged hot/random reference front; these are important qualifications, not hidden omissions.
- The matched-knee analysis, radiometric-blind control, and $H=15$ reference-direction control materially strengthen the incremental-$f_3$ analysis. The reference-direction-count concern is therefore not reported as an unresolved defect.
- Hot/random initialization, perturbation, doubled-budget, and agility-envelope controls provide useful robustness evidence despite their limited scope.
- The best-coverage front-point result—$+12.5\%$ in $f_2$ at zero coverage cost—is reported in both the abstract and operational discussion and is a genuinely decision-relevant strength.
- The correlation analysis distinguishes pooled, per-schedule, envelope, null, and ablation views; hypervolume is appropriately demoted because of cardinality and representation asymmetries.
- The limitations disclose the synthetic scenario family, fixed orbit and dwell, resource caps, absent latency objective, hot-start dependence, and lack of learning-based benchmarks. These disclosures narrow fair criticism and improve interpretability.
