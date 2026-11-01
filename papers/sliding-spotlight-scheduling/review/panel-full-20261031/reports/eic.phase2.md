contract_role: eic

## Dimension Scores

### D1: methodology_rigor

score: not_assessed

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: not_assessed

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: warn
trigger: "recurring convention slips short of unevaluable"

### D6: venue_fit_and_contribution

score: warn
trigger: "framed somewhat beyond the evidence the manuscript is set up to deliver"

## Review Body

No venue criteria manifest or target-criteria binding was supplied for this run, so this card makes no criterion-level venue-alignment claim. The judgements below are made from the configured readership position only: an interdisciplinary aerospace, remote-sensing and operations-research audience, for whom the questions are whether the physics-to-planning integration is a substantive contribution, whether the headline claims are sized to the evidence, and whether such a reader can follow the result.

The manuscript is an unusually disciplined piece of technical reporting. Its structural choices are the conventional ones for the field and are executed carefully, and its candour about its own limits is far above the norm. The weaknesses I record are not about competence; they are about what a reader is invited to conclude from the headline numbers, and about a layer of internal project bookkeeping that has leaked into the published surface of the paper.

### S1: The gap is located precisely and against the right neighbours

The related-work section does not gesture at a gap; it names the four nearest SAR-planning papers and states what each one carries and what each one does not, and the positioning paragraph identifies the imaging-versus-scheduling seam rather than a vacuum. That is the kind of positioning an editorial reader can test.

**Evidence Anchor**: text: §2.4 Positioning — "none carries a per-task dwell that responds to a per-task resolution requirement inside the scheduling loop"

### S2: Infeasibility is kept categorically distinct from zero coverage

The paper insists, in the results, the criteria table and the conclusion, that a cell with no admissible individual is not a coverage of zero, and it carries that distinction into the figure and the ledger. This is a discipline most papers in this area do not maintain, and it changes what the negative result means.

**Evidence Anchor**: text: §5.2 The as-placed point and the floor step — "That is not a coverage of zero, and the two must never be interchanged."

### S3: The formulation is a recognisable new object for an operations-research reader

The scheduling problem is stated in the vocabulary of its own literature — start-time-dependent setup and processing times — and the manuscript states explicitly why the existing structural results for monotone time-dependent processing times do not transfer. That is a substantive interdisciplinary contribution rather than an application wrapper.

**Evidence Anchor**: text: §4 Solving Approach — "a task's processing time is a non-monotone function of where it is started within its window"

### S4: The fixed-dwell counterfactual yields a practitioner-relevant failure mode

Quantifying how often a plan built on library dwell breaks when replayed against the real dwell gives a mission-planning reader something actionable, and the result is measured before any repair rule is applied, so it does not depend on the repair policy chosen.

**Evidence Anchor**: text: §5.7 The fixed-dwell counterfactual — "the dense families' schedules do not survive the replay"

### W1: The floor share of the headline is a frozen-assignment artifact, but it is reported beside platform physics

The paper attributes 20.0 of the 26.0-point drop and 44.8 of the 46.6-point drop to the stripmap antenna floor, and the abstract, the first contribution and the conclusion all present that floor as the one place where the requirement excludes solutions outright. The scope section then states that under the registered selection policy those same coarse-tier orders remain routable to sliding spotlight at moderate squint, and that the frozen assignment forbids exactly that rescue. So the majority of the headline effect is a property of the comparability freeze, not of the platform. The manuscript discloses this, but the disclosure sits in the limitations and never travels with the number. An editorial reader who takes the abstract at face value will over-attribute the cost to the physics. The minimum remedy is to carry the policy qualifier into the abstract and the conclusion where the floor share is quoted, and to say plainly that the floor-dominated share would largely vanish under a free router.

**Severity**: Major
**Evidence Anchor**: text: §7.1 Scope and negative claims — "part of the floor-dominated cost is the comparability policy, not the platform"
**Confidence**: 5 — judgement rests on a direct comparison of two passages in the same manuscript.

### W2: No published planner is run, so the magnitude of the central reading has no external reference

Every baseline in the paper is built by its own authors: the greedy anchor, the repair arms and the pre-shrunk fixed-dwell arm. The scope section states this openly as a sixth scope limit. The consequence is that a mission-planning reader cannot place the served-priority levels anywhere: whether 0.948 at the as-placed point is strong, ordinary or weak against the state of the art is unanswerable from this manuscript, and the paper's own significance claim rests on that number. Adding even one literature planner on the released scenario set would convert a within-study sensitivity reading into a result with a denominator the field shares.

**Severity**: Major
**Evidence Anchor**: absence: §2 Related Work, §5 Results and §7.1 scope statements — expected a run of a published mission-planning or SAR scheduler on the released scenario set; checked §2.2–2.4 related-work survey, Table 1 and Figures 5–8 result readings, §5.6 counterfactual arms, §7.1 sixth scope statement
**Confidence**: 5 — absence verified across the whole results and discussion surface of the manuscript.

### W3: The central construct is named "mode-dependence" although the design cannot separate mode from density

The second contribution is titled "the mode-dependence of what a requirement costs", and the abstract attributes the family shapes to mode composition. Yet the three families differ in density and mode composition simultaneously, and the manuscript itself says the scenario figure carries no controlled comparison. What the data identify is a joint density-and-mode response, not a mode effect: no arm holds density fixed while varying mode. This matters because "mode-dependence" is the paper's headline construct and the one a reader would carry away. Either retitle the result as what it is — a family-shape contrast under covarying density and composition — or add the arm that separates them.

**Severity**: Major
**Evidence Anchor**: text: Figure 4 caption — "Densities and mode composition covary by design across the three families, so nothing in this figure is a controlled comparison"
**Confidence**: 4 — the confound is stated by the manuscript; the inference is editorial about how the contribution is named.

### W4: The headline is a post hoc main-result designation

The registration timeline is stated with unusual honesty: the grid and the three criteria precede the data, while the registration of the coverage–demand curve as the main result form is dated one day after the sweep ran. The numbers themselves are unaffected, and because the grid and criteria are frozen the forking-paths risk on this specific quantity is limited. But it means the headline cannot be read as confirmatory, and the manuscript should not allow the phrase "main result" to imply otherwise. A single sentence in the introduction marking the curve as a descriptive reading whose designation followed the data would settle it.

**Severity**: Minor
**Evidence Anchor**: text: §4.3 The demand scan — "the headline curve is a post hoc descriptive reading"
**Confidence**: 5 — the manuscript states the date ordering explicitly.

### W5: The "Solving Approach" section carries an optimisation component the results render inert

A full section is given to a single-objective evolutionary search under a fixed 40/60 budget, while the measured marginal contribution of the search is two units out of 260, and the anchor attains the best-found coverage everywhere else. The paper analyses this well and does not claim solver credit, but the section's framing — its title, its budget justification, its operators — still reads as though the search were the method. For a scheduling readership, the section would be stronger if it presented the deterministic construction as the method and the evolutionary search as a check on it. This is a framing mismatch, not a method defect.

**Severity**: Minor
**Evidence Anchor**: text: §4.5 The search face and the construction face — "the greedy anchor already attains the best coverage found for the unit in this study in 258 of the 260 units"
**Confidence**: 4 — based on the section's stated role versus the measured contribution it reports.

### W6: The printed table cannot reproduce the quoted drop

The text quotes a 46.6-point drop from the as-placed point to the tightest feasible point of the dense family, derived from 0.9485 and 0.4827. Table 1 prints the same cells at three decimals, 0.948 and 0.483, from which the drop is 46.5 points. The discrepancy is a rounding artifact and materially harmless, but the manuscript states that every reading is recomputed by an automated number checker from the artifacts, and a reader performing the same recomputation from the printed table arrives at a different last digit. Print the table to the precision at which the text quotes it, or quote the drop to the precision the table supports.

**Severity**: Minor
**Evidence Anchor**: table: Table 1 — R3H observed column, rows s=1.0 and s=0.8 (0.948 and 0.483)
**Confidence**: 5 — arithmetic from values printed in the manuscript.

### W7: Internal process metadata appears in the main text

The manuscript refers twice to "this revision", a referent that has no meaning for a journal reader, and carries ten dated project entries with specific days in 2026 in the running text. Some of this is evidential for the third contribution, which is precisely about registration discipline. But the dates are development history, and "this revision" refers to an internal review round the reader never sees. Moving the dated registration chain into an appendix, and replacing the revision deixis with an ordinary tense, would keep the evidence and remove the residue.

**Severity**: Minor
**Evidence Anchor**: text: §5.6 The fixed-dwell counterfactual — "reanalysis additions of this revision"
**Confidence**: 5 — the phrase and the dated entries are verbatim in the manuscript.

### W8: Two family labels are used before they are defined

The solver section quotes the dense and control families by their identifiers, with their task counts, one section before the experimental design section defines them. Inline pointers mitigate this, but a reader meeting "R3H" and "R1C" for the first time in the method section must hold two undefined labels until the next section. Either define the families on first use or defer the identifiers to the results.

**Severity**: Minor
**Evidence Anchor**: text: §4.1 Encoding and evaluation — "the densest real-window family (R3H" and "R1C, 20 drawn and 20 admitted"
**Confidence**: 5 — direct reading order of the manuscript.

### W9: The abstract is loaded to the limit and its opening referent is unclear

At 249 words in a single paragraph the abstract carries nine numeric readings, three caveats and two parenthetical conventions. Its second sentence, "For a sliding-spotlight platform it fails measurably", leaves the subject of the failure implicit between the satellites and the assumption. The result is an abstract a specialist can decode and a neighbouring-field reader cannot. One short sentence naming the contribution before the numbers begin, and an explicit subject for the failure, would cost nothing and buy the interdisciplinary readership the paper is aiming at.

**Severity**: Minor
**Evidence Anchor**: text: Abstract — "For a sliding-spotlight platform it fails measurably"
**Confidence**: 5 — reading of the abstract as printed.
