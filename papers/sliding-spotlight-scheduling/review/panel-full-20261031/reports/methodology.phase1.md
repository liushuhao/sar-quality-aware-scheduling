## Contract Paraphrase

D1: From a methodology-rigor standpoint, D1 asks whether the experimental apparatus and the reporting built around it can bear the weight a methodological referee would place on them for simulation-based optimization of time-dependent satellite scheduling: whether comparisons are constructed as paired or otherwise controlled contrasts sharing random seeds, whether replication and dispersion are reported at the granularity the claims require, whether a counterfactual or ablation arm genuinely isolates the effect it is credited with, whether search behaviour is separated from construction behaviour wherever the argument depends on that separation, whether uncertainty accompanies the headline quantities, and whether the reproducibility affordances (seeds, solver settings, data, pipeline) would let an independent researcher arrive at the same numbers. The judgement is about the design-to-inference chain behind each reported number, not about presentation polish.

D2: D2 asks whether the manuscript's domain-specific claims and its representation of prior work are correct — the standard under which concrete factual or terminological assertions about SAR mission planning are checked against current domain evidence, and under which a misrepresentation of earlier work would matter. This is the remit of the domain seat; I read the dimension only to understand what my own methodology judgement does not cover.

D3: D3 asks whether the central thesis holds together: whether the question posed at the outset, the design used, the results reported, and the conclusions drawn are mutually consistent, whether each piece of evidence actually supports the claim it is attached to, and whether an inferential leap or fallacy would undermine the core argument even where the individual analyses are executed correctly. It is the chain-from-premise-to-conclusion seat, audited separately from the correctness of any single computation.

D4: D4 asks whether the framing, definitions and implications are legible to readers from adjacent fields and whether interdisciplinary claims are substantiated rather than asserted. It belongs to the perspective seat; I read it only to keep my own methodological judgement from overlapping that remit.

D5: D5 asks about manuscript organisation, expository clarity, figure and table quality, and adherence to venue conventions. It belongs to the editor seat and is not part of my scoring remit.

D6: D6 asks whether the manuscript fits the configured venue and offers an original, significant contribution for its readership. No venue criteria manifest was supplied for this run, so I make no venue-alignment claim and defer this dimension to the editor seat.

## Scoring Plan

### D1: methodology_rigor

dimension_id: D1
what_to_look_for: whether each reported number is produced by a design that can support its inferential scope — paired or otherwise controlled seed-level comparisons, replication counts and dispersion, ablation or counterfactual arms that isolate the attributed effect, separation of search effects from construction effects where the argument needs it, uncertainty attached to headline quantities, and reproducibility affordances sufficient for independent reconstruction.
what_triggers_block: a core claim depends on a comparison structure that cannot distinguish the compared conditions, or on an ablation or counterfactual arm whose design leaves the credited effect confounded with another change, or on numbers whose replication base is not stated, so the supporting analysis cannot be reconstructed from the paper.
what_triggers_warn: the design is broadly adequate but a supporting claim rests on a single unreplicated run, an unpaired contrast where a paired design was available, an unstated seed or solver configuration, or missing dispersion or uncertainty for a quantity that carries argumentative weight.
what_triggers_fatal: the reported evidence is internally impossible under any plausible execution of the stated design, or the paper's own reproducibility apparatus contradicts the numbers it reports, such that no correction short of new experiments could restore the core claim.

### D3: argumentative_coherence

dimension_id: D3
what_to_look_for: whether the question, design, results and conclusions form one chain — whether every numerical statement is given the scope its design earns, whether contrasts and causal-sounding attributions are licensed by the comparisons actually run, whether caveats stated in one place are contradicted elsewhere, and whether the central thesis survives its own reported evidence.
what_triggers_block: the central thesis is contradicted by the paper's own reported results, or a load-bearing conclusion is drawn from evidence that cannot support it under any reading of the described design, so the argument does not close.
what_triggers_warn: a local overreach — an inference stated more broadly than the design supports, a caveat contradicted in a later section, or a comparative claim whose comparator is not the one actually run — while the central thesis still survives.
what_triggers_fatal: the core claim is self-contradictory or unfalsifiable as stated, with evidence and conclusion mutually exclusive under every reading of the paper, so no revision short of withdrawing the thesis could resolve it.

criteria_binding_unavailable

[CONTRACT-ACKNOWLEDGED]
