contract_role: perspective

## Dimension Scores

### D1: methodology_rigor

score: not_assessed

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: not_assessed

### D4: cross_disciplinary_relevance

score: warn
trigger: "the operational reading of the counterfactual, the product meaning of the reported quality index, or the reproducibility and mission-use path left implicit or asserted without concrete affordances"

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

I read this as an Earth-observation mission-operations and SAR data-product outsider: not asking whether the optimisation is sound, but whether the objects the paper builds — a resolution equality held at a selected start, a frozen mode assignment, a reported quality index, a fixed-dwell counterfactual — mean something a customer, a product engineer or a planner could act on. The manuscript is unusually disciplined about disclosure, and several of the conventional failure modes of this genre are pre-empted; what remains is mostly translation, not error.

### S1: Reproducibility affordances are concrete rather than aspirational

Deterministic ordering, fixed seeds, single-threaded execution, an environment record, artifact lineage with parent generation and frozen code state, and a manuscript-number checker that recomputes every reported reading before the results section is read. For an outside reader this is the difference between a claim and a re-runnable measurement, and it is rare at this level of detail.

**Evidence Anchor**: text: §4.3 Search operators and selection, "every unit is bit-reproducible"

### S2: Constructs are guarded against the misreadings an operations reader would make

The paper repeatedly separates categories that this genre usually blurs: infeasibility from zero coverage, capability from result, search face from construction face, policy-specific cost from platform physics. These are exactly the distinctions a mission-operations reader needs to avoid importing a number into a decision it cannot support.

**Evidence Anchor**: text: §3.5 The demand-tightening axis, "an infeasible grid point is not a point on the curve"

### S3: The counterfactual is reported as a bracket rather than a headline number

Three repair rules plus a conservative pre-shrunk arm, all replayed on the same stored plans, with the between-family ordering flipping across arms. Reporting the span as a property of repair capability gives a reader something to reason with, rather than a single cost figure that would not survive contact with a real ground segment.

**Evidence Anchor**: text: §6.6 The fixed-dwell counterfactual, "a property of the repair capability, not a single number"

### W1: Resolution equality is pointwise at the selected start and the intra-dwell degradation is never quantified

The identity the paper builds — delivered resolution equals the requirement — holds at the start instant; inside the imaging interval the delivered resolution follows the ratio of cosines, and the manuscript states it does not claim a constant resolution across the pass. That is honest, but it leaves the outside reader unable to answer the product question: if the requirement is 0.5 m, what is the worst delivered resolution over the served scene at the starts this schedule actually selects (median start squints of 20–38 degrees)? Without a bound or a table of the degradation over the observed start distribution, the headline identity reads as a bookkeeping fact about an instant, not as a product specification. Remedy: report the cosine ratio at the selected starts — the same quantity the dwell distribution figure already computes — as a per-mode worst case, or add a one-line bound to the constraint statement.

**Severity**: Major
**Evidence Anchor**: text: §3.4 Constraints and objectives, "this paper does not claim a constant delivered resolution across a whole imaging pass"
**Confidence**: 4 — reading the paper as an EO SAR product and mission-operations consumer of resolution specifications.

### W2: The policy-specific share of the floor cost is admitted but never split

The tight-side collapse is decomposed and the dominant component is the stripmap floor; the scope discussion concedes that under the registered selection policy a coarse order slipping below the floor remains routable to sliding spotlight, and that the frozen assignment forbids exactly that rescue. So the floor figure the abstract quotes contains an unquantified policy component. An operations reader will take 20.0 and 44.8 points as what the antenna costs them, when part of it is what the paper's comparability choice costs. Remedy: compute the same floor-exclusion bound with the rescue permitted — the bound is arithmetic on the same manifests — and report the platform-priced and comparability-priced parts separately, or state explicitly that the split is not available and why.

**Severity**: Minor
**Evidence Anchor**: text: §7.1 Scope and negative claims, "part of the floor-dominated cost is the comparability policy, not the platform"
**Confidence**: 4 — practical reading of which costs a mission planner can attribute to hardware.

### W3: The counterfactual establishes the failure of a modelling convention, not of observed operational practice

The fixed-dwell arm freezes the dwell at its zero-squint library value. The paper itself calls that the least conservative convention and adds a conservative arm, which is good practice; but nothing in the manuscript establishes whether working planners — as distinct from the scheduling literature's structural assumption — in fact use zero-squint dwell, a margin-padded dwell, or a conservative endpoint dwell. As written, the abstract's "it fails measurably" reads as a statement about practice, while the evidence supports a statement about a convention. Remedy: anchor the baseline to operational practice with a citation or an explicit scope sentence confining the claim to the planned-convention family, and note that the conservative arm is the closer analogue of a prudent ground segment.

**Severity**: Major
**Evidence Anchor**: text: §6.6 The fixed-dwell counterfactual, "the dwell held at its zero-squint library value at every consumption point"
**Confidence**: 4 — mission-planning practice reading of what a fixed-dwell planner would plausibly consume.

### W4: The reported quality reading cannot answer a product-quality question

The index is a resolution-shaped capability statement with no calibrated radiometric content, and the fulfillment ratio is a within-task ratio against the task's own zero-squint optimum. Both are labelled honestly and repeatedly. The residual gap from a data-product perspective is that no bridge is offered to any standard product-quality descriptor, so a customer cannot tell what 0.658 or 0.7447 means for the delivered image in the terms a product specification would use. Remedy: state in one sentence what the reading does license (relative window/start choice within a task) and what it explicitly does not, and, if cheap, carry one calibrated descriptor — a noise-equivalent figure or a product-level ambiguity budget — as a reported side reading rather than as part of the index.

**Severity**: Minor
**Evidence Anchor**: text: §3.3 Image quality model, "it states a platform capability, and it supplies the numerator of a reported reading"
**Confidence**: 4 — SAR product-specification reading of resolution and radiometric descriptors.

### W5: The experimental axis is not the operational one, by the authors' own statement

Uniform scaling of the whole demand book is a controlled version of the question the paper wants to answer, and the manuscript says directly that per-tier tightening is the axis an operator would use and is future work. The consequence for an outside reader is that the curve cannot be mapped onto a procurement or tasking decision, where requirements move one product tier at a time. The tier-placement experiment in the sensitivity subsection partially answers this for the all-stripmap control; extending that arithmetic to the mixed family would make the operational reading available at low cost. Remedy: either run the per-tier variant on the mixed family or move a sentence into the abstract-level framing that the scan is a controlled analogue, not an operational forecast.

**Severity**: Minor
**Evidence Anchor**: text: §6.7 Policy-knob sensitivities, "the axis an operator would actually use"
**Confidence**: 4 — requirements-management reading of how product tiers actually move.

### W6: Load-bearing definitions live outside the manuscript

The paper's own convention vocabulary — measurement-convention version labels, registered decisions with dates, the preregistration amendment chain, the design record — is cited as authority throughout, but the manuscript contains no consolidated table defining those labels or reproducing the registered decisions it relies on. Adjacent-field readers can follow the physics and the results, but not the provenance grammar, and the repeated deferral to external records weakens the self-containedness that a journal reader and a reproducibility check both expect. Remedy: one compact appendix table mapping each convention label and dated decision to its content and its effect on the reported readings.

**Severity**: Minor
**Evidence Anchor**: absence: the manuscript's model, experimental-design, and results sections — expected a consolidated in-manuscript definition of the convention labels and dated registered decisions cited as authority; checked the nomenclature, the model section, the experimental-design section, the results section, and the discussion against the labels used in the text
**Confidence**: 3 — outsider's reconstruction attempt of the provenance grammar from the manuscript alone.

Taken together, the perspective reading is that the paper is operationally legible where it is most careful and under-translated where its headline constructs cross into product and mission language. The score is warn rather than block because every construct remains reconstructable, but the resolution identity, the fixed-dwell baseline and the floor decomposition each need one more translation step before an operations reader can use them.
