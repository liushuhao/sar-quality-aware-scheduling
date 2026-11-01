## Dimension Scores

contract_role: methodology

### D1: methodology_rigor

score: warn
trigger: "the design is broadly adequate but a supporting claim rests on"

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: warn
trigger: "an inference stated more broadly than the design supports"

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

The study design is unusually explicit for this literature: ten independent scenario draws per family and grid point, paired per-seed deltas alongside median-of-medians readings, the search face separated from the construction face by two independent probes, sensitivity reanalyses of the transfer margin and the tier placement, and a dated preregistration record that keeps frozen criteria on the books after they fail. The reproducibility affordances are strong: deterministic single-threaded runs with a fixed hash seed, frozen manifests, a convention registry, and a named artifact deposit. The methodological risks that remain are external-validity risks rather than execution errors: the three families differ in density and mode composition at the same time, so the cross-family shape story is a co-variation claim dressed in places as an attribution; and the headline coverage losses are the greedy anchor's readings, which the body states and the abstract does not carry. Both are repairable by scoping and by one controlled arm, not by new data analysis. Minor issues concern the uneven uncertainty budget and two dated, disclosed design decisions taken after data were seen.

### S1: The search face and the construction face are measured, not asserted

Two independent probes test whether the coverage response is a solver artefact: an anchor-free random-initialisation arm that never exceeds the anchor on any feasible cell and fails outright on 12 dense-family cells, and a sixteen-fold evaluation budget that leaves every reading unchanged. This is the strongest part of the design: it converts a possible confound into a measured result and pre-empts the obvious search-artefact objection.

**Evidence Anchor**: text: Section 5.5, "the anchor-free arm never crosses the identity line, and the sixteen-fold budget arm coincides with it on every cell"

### S2: Frozen criteria are reported with their failures, not retuned

The shape criteria are registered before the scenario data, the criteria text is not edited after the verdict, and both failures on the 50-task family are reported as results about the scenario set. A dated amendment refines the verdict reading but leaves the frozen verdicts on record. This is exactly the discipline the preregistration claim asserts, and it is observable in the paper rather than promised.

**Evidence Anchor**: text: Section 5.3, "a failed criterion is a result about this scenario set, not a defect in the criterion to be edited away"

### S3: Paired per-seed analysis with dispersion and an interval

The main drops are reported both as median-of-medians and as the median of each seed's own paired drop, with per-seed ranges and, for the principal R3H drop, a seed-level bootstrap interval that excludes zero. The paired form is the right design for this scenario construction because it removes scenario-draw variation from the contrast, and the paper uses it deliberately alongside the unpaired summary.

**Evidence Anchor**: text: Section 6.2, "the median over seeds of each seed's own drop"

### S4: Reproducibility affordances are concrete and sufficient for reconstruction

Runs are bit-reproducible under a fixed seed, single-threaded execution, manifest task-list order and deterministic sorting; the environment record pins interpreter, dependencies and hash seed; artifacts, generator and solver sources, verification and reanalysis scripts, and the preregistration chain are named for deposit. Independent reconstruction of every reported reading is therefore plausible from the stated materials.

**Evidence Anchor**: text: Data availability, "the environment record (interpreter version, pinned dependency set, fixed hash seed, single-threaded execution)"

### S5: The tier-placement knob is turned into an exact in-sweep experiment

Scaling the coarse tier is recognised as arithmetically identical to reading the same frozen manifests at shifted demand factors, which yields a prediction for where the floor step should move and a direct check that it moves there. The transfer-margin reanalyses are anchored by reproducing the stored sweep anchors on all replayed units. These are cheap, high-discrimination checks rather than assertions of robustness.

**Evidence Anchor**: text: Section 6.7, "multiplying the whole coarse tier by $1/\phi$ is arithmetically identical to reading the same frozen manifests at demand factors $s/\phi$"

### W1: Density and mode composition covary, so the cross-family shape attribution is not identified

The three families differ simultaneously in task count (20/50/100), window counts (145--162/337--391/731--779) and mode mix (all stripmap / no stripmap / mixed). The paper acknowledges this in the figure caption and in the results prose, yet elsewhere states that the three curves show what the mode assignment decides about shape. The floor-exclusion bound isolates the stripmap-floor component on the tight side, but the residual shape contrast between the flat 50-task family and the collapsing 100-task family cannot be assigned to mode composition rather than to density and C2 tightness with the present design. Improvement: add at least one density-matched arm (for example an all-stripmap or all-spotlight family at N=100, or an STR-bearing family at N=50), or state the cross-family contrast uniformly as co-variation and withdraw the attributional sentence.

**Severity**: Major
**Evidence Anchor**: text: Caption of Fig. 4, "Densities and mode composition covary by design across the three families, so nothing in this figure is a controlled comparison"
**Confidence**: 4 — simulation-optimisation experiment design and factorial confounding

### W2: The abstract states construction-bounded losses as requirement costs

The body establishes that the anchor attains the best-found coverage in 258 of 260 units, that no upper bound tighter than the trivial one is available at the as-placed point, and that the as-placed premiums are readings under the anchor construction rather than attributed infeasibility. The abstract nonetheless reports the 26.0 and 46.6-point drops, and the 4.15 and 2.36-point premiums, without that qualifier. A stronger construction could move these numbers, so the most-read surface overstates their portability. Improvement: carry the construction qualifier into the abstract, or phrase the quantities as what this construction paid rather than what the requirement costs.

**Severity**: Major
**Evidence Anchor**: text: Abstract, "the dense family drops 26.0 percentage points to the next point and 46.6 to the tightest one"
**Confidence**: 4 — inference-to-design matching in simulation studies

### W3: Uncertainty reporting is uneven across the headline quantities

One headline contrast receives a bootstrap interval, while the 46.6-point drop, the 46.0-point control drop, both as-placed premiums and the 7--30-point counterfactual span carry per-seed ranges only. The bootstrap also treats the ten scenario draws as a sample from a superpopulation without naming that inferential target, while the rest of the paper is explicitly descriptive about this fixed scenario set. Improvement: report the same interval form for every headline contrast, or state once that all inference is descriptive over the ten registered draws and let the single interval be read the same way.

**Severity**: Minor
**Evidence Anchor**: text: Section 6.2, "A seed-level bootstrap of those ten paired R3H drops"
**Confidence**: 4 — nonparametric interval construction and resampling design

### W4: The C3/C4 normalisation was redefined after violations were observed

Both duty and memory budgets are structurally non-binding inside the envelope, and the paper records that the normalisation reference was changed on the day the sweep ran after the earlier reference produced false violations. The redefinition is dated and disclosed, and the natural per-task envelope reference is defensible, but a constraint calibration changed after seeing data is precisely the kind of decision that needs an independent justification or a sensitivity reading against the prior reference. Improvement: report the coverage curve under the prior normalisation for at least the grid points where violations appeared, or justify the per-task envelope reference analytically and show that the choice cannot mask a binding channel.

**Severity**: Minor
**Evidence Anchor**: text: Section 3.4, "the normalisation reference was redefined on 2026-10-20, on the day the sweep ran"
**Confidence**: 3 — constraint modelling and data-dependent calibration

### W5: The main result form was registered after the sweep, and the abstract's preregistration phrasing does not say so

The grid and the three shape criteria predate this scenario set's data, but the amendment that made the coverage--demand curve the main result form is dated the day after the sweep, and the refined verdict reading is later still. The paper states both dates explicitly in the body; the contributions and abstract present the preregistration as covering the criteria and the grid without repeating that the headline estimand is post hoc. Improvement: repeat the two-date boundary once on the contribution surface, or relabel the curve as a descriptive reading whose criteria were preregistered rather than as a preregistered result.

**Severity**: Minor
**Evidence Anchor**: text: Section 5.3, "the amendment that registered the coverage--demand curve as the main result form is dated 2026-10-21, after the sweep ran on 2026-10-20"
**Confidence**: 5 — preregistration timing and HARKing boundaries

## Arithmetic Receipts

no_recomputable_statistics: checked the manuscript for t/F/z/chi-square statistics with df, reported p-values, discrete-scale means or SDs at stated N, and any other input the four bounded procedures cover; it reports served-priority fractions, medians, percentage-point differences, per-seed ranges and one bootstrap interval, none of which is covered, so no receipt is emitted rather than an improvised calculation
