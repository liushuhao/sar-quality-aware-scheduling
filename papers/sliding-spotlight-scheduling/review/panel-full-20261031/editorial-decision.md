# Editorial Decision Package

**Panel:** `paper2-panel-full-20261031` (`reviewer_full`, 5 seats)
**Manuscript:** "Resolution-Driven Scheduling of Agile SAR Satellite: From Fixed to Endogenous Imaging Dwells"
**Contract:** `reviewer/reviewer_full/v2` (`contract_sha256: e9712090d2469fea15a37b8e22d4e137afbcb2bf38d5789939c5df56738ef7af`)

## Calibration Resolution

`calibration_status: NOT_CALIBRATED`

No candidate or prose-named criterion profile is upgraded by this package. `PROFILE_MEASURED` is unavailable: no closed profile artifact and replay validator bind the exact target fields to the completed panel's `execution_topology_sha256`.

**Criteria binding:** `criteria_binding_unavailable`. No venue criteria manifest or target-criteria binding was supplied for this run. The EIC card states this explicitly; the other four cards carry no criterion-level venue-alignment claim and do not contain the literal disclosure, so the binding state is recorded as supplied rather than reconstructed. No venue-alignment claim is made anywhere in this package; the D-verdicts below are contract-dimension verdicts only.

**Machine-readable boundary:** the `revision-roadmap/1.0` JSON core requires `block_manifest_sha256`, `base_draft_sha256`, and per-item `proposed_targets` block ids drawn from a bound block manifest. This run supplied no block manifest and no base-draft hash. Fabricating block ids would misstate write scope, so the roadmap below is emitted in the reviewer skill's letter form with typed evidence anchors, cost scopes, and closed consequence codes; it can be transcribed into the JSON core once a block manifest is bound. No author triage, display order, or work order is carried.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript titled "Resolution-Driven Scheduling of Agile SAR Satellite: From Fixed to Endogenous Imaging Dwells." The manuscript was reviewed through five role-separated seats: a Journal-Fit seat, a methodology seat, a domain seat, a cross-disciplinary perspective seat, and a Devil's Advocate. Their execution provenance is reported below as six separate axes and is not reduced to a binary independence claim.

### Decision: Major Revision

### Contract Arithmetic (v3.6.2 Sprint Contract Synthesizer Protocol)

**Step 1 — Role-scoped scoring matrix.** Only assessed scores from seats whose `contract_role` appears in the dimension's `eligible_roles` are counted. Ineligible `not_assessed` values and eligible abstentions are excluded from numerator and denominator.

| Dim | Name | Priority | Eligible seats | Assessed scores | Audit verdict |
|---|---|---|---|---|---|
| D1 | methodology_rigor | mandatory | methodology | R1 = warn | warn |
| D2 | domain_accuracy | mandatory | domain | R2 = warn | warn |
| D3 | argumentative_coherence | mandatory | da, methodology | DA = warn; R1 = warn | warn |
| D4 | cross_disciplinary_relevance | high | perspective | R3 = warn | warn |
| D5 | writing_and_structure | normal | eic | EIC = warn | warn |
| D6 | venue_fit_and_contribution | mandatory | eic | EIC = warn | warn |

No assessed eligible seat declared a block or a fatal block. All six dimensions are assessed; no `[DIMENSION-UNASSESSED]` case arises.

**Step 2 — Failure-condition arithmetic.** Quantifier applied per dimension to that dimension's assessed eligible seats, then the expression's dimension quantifier applied to the per-dimension booleans.

| Condition | Severity | Quantifier | Expression | Evaluation | Fired |
|---|---|---|---|---|---|
| F1 | 95 | any | any mandatory dimension has a fatal block | No seat declared a fatal block; fatal scope is valid only for mandatory dimensions | false |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1, D2, D3, D6 all warn | false |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1 majority warn (1/1); D2 majority warn (1/1); D3 majority warn (2/2); D6 majority warn (1/1) — four mandatory dimensions at warn-or-worse | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 warn, not block | false |
| F5 | 40 | any | any dimension scores 'warn' or worse | All six dimensions warn | **true** |
| F0 | 10 | all | every dimension scores 'pass' | Not every dimension passes | false |

**Step 3 — Precedence.** Highest-severity fired condition wins; ties break by ordinal. F3 (70) outranks F5 (40).

```
dimension_verdicts: [D1=warn, D2=warn, D3=warn, D4=warn, D5=warn, D6=warn]
fired_conditions: [F3, F5]
da_critical_adjudications: []
editorial_decision=major_revision
```

The DA reported zero CRITICAL findings, so no `C1..Cn` IDs exist and no `C{n} rejection rationale` lines are emitted. No CRITICAL was invented to populate the line.

### Consensus Analysis

Positions are assessed over the four non-DA seats (EIC, R1, R2, R3); the DA is tracked separately and never enters the consensus denominator. A `—` is `not-mentioned` — silence, not agreement. Every sub-claim below was decomposed from a weakness a seat actually raised; none was authored here. Severity and confidence are transported from the cards, not re-derived.

#### Step 1b — Sub-claim inventory

| SC | Sub-claim (parent weakness) | EIC | R1 | R2 | R3 | DA | agree/silent/conflict (4 non-DA) | Severity | Disposition |
|---|---|---|---|---|---|---|---|---|---|
| SC-1 | The floor-dominated share of the headline contains an unbounded comparability-policy component; the abstract attributes it to platform physics (EIC W1 / R3 W2) | raised (Major, 5) | — | — | corroborated (Minor, 4) | M1 corroborated (Major, 5) | 2/2/0 | Major | Corroborated (2/4) |
| SC-2 | No published planner is run, so the central magnitude has no external denominator (EIC W2) | raised (Major, 5) | — | — | — | — | 1/3/0 | Major | Single-seat (1/4) |
| SC-3 | Density and mode composition covary, so the "mode-dependence" construct is not identified (EIC W3 / R1 W1) | raised (Major, 4) | corroborated (Major, 4) | — | — | — | 2/2/0 | Major | Corroborated (2/4) |
| SC-4 | The main result form was registered after the sweep; the contribution surface implies a preregistered headline (EIC W4 / R1 W5) | raised (Minor, 5) | corroborated (Minor, 5) | — | — | — | 2/2/0 | Minor | Corroborated (2/4) |
| SC-5 | The "Solving Approach" framing presents the evolutionary search as the method although the anchor carries the result (EIC W5) | raised (Minor, 4) | — | — | — | — | 1/3/0 | Minor | Single-seat (1/4) |
| SC-6 | Table 1's printed precision cannot reproduce the quoted 46.6-point drop (EIC W6) | raised (Minor, 5) | — | — | — | — | 1/3/0 | Minor | Single-seat (1/4) |
| SC-7 | Internal process metadata ("this revision", dated project entries) appears in the main text (EIC W7) | raised (Minor, 5) | — | — | — | — | 1/3/0 | Minor | Single-seat (1/4) |
| SC-8 | Family identifiers R3H/R1C are used before they are defined (EIC W8) | raised (Minor, 5) | — | — | — | — | 1/3/0 | Minor | Single-seat (1/4) |
| SC-9 | The abstract is overloaded and its opening failure has no explicit subject (EIC W9) | raised (Minor, 5) | — | — | — | — | 1/3/0 | Minor | Single-seat (1/4) |
| SC-10 | The 26.0/46.6-point drops and 4.15/2.36-point premiums are construction-bounded but appear unqualified in the abstract (R1 W2) | — | raised (Major, 4) | — | — | M3 corroborated (Major, 4) | 1/3/0 | Major | Single-seat (1/4), DA corroborated |
| SC-11 | Uncertainty reporting is uneven; the bootstrap's inferential target is unnamed (R1 W3) | — | raised (Minor, 4) | — | — | — | 1/3/0 | Minor | Single-seat (1/4) |
| SC-12 | The C3 duty normalisation reference was redefined on the day the sweep ran, without a sensitivity reading against the prior reference (R1 W4 / R2 W5) | — | raised (Minor, 3) | corroborated (Minor, 4) | — | — | 2/2/0 | Minor | Corroborated (2/4) |
| SC-13 | The ambiguity module excludes the scene sweep that the dwell closure includes, and that asymmetry drives the reported squint direction (R2 W1) | — | — | raised (Major, 4) | — | — | 1/3/0 | Major | Single-seat (1/4) |
| SC-14 | The delivered-resolution identity is definitional, so it validates the implementation path, not the physics (R2 W2) | — | — | raised (Minor, 4) | — | — | 1/3/0 | Minor | Single-seat (1/4) |
| SC-15 | The production dwell's error against truth is unquantified; only the two internal closures are compared (R2 W3) | — | — | raised (Minor, 4) | — | — | 1/3/0 | Minor | Single-seat (1/4) |
| SC-16 | The quality index is resolution-dominated and offers no product-level bridge; the term invites over-reading (R2 W4 / R3 W4) | — | — | raised (Minor, 4) | corroborated (Minor, 4) | — | 2/2/0 | Minor | Corroborated (2/4) |
| SC-17 | The "five constraint families" framing overstates a model with exactly two binding members (R2 W5) | — | — | raised (Minor, 4) | — | — | 1/3/0 | Minor | Single-seat (1/4) |
| SC-18 | Terminology overlap between resolution concepts and between dwell concepts (R2 W6) | — | — | raised (Minor, 3) | — | — | 1/3/0 | Minor | Single-seat (1/4) |
| SC-19 | Resolution equality is pointwise; intra-dwell degradation at the selected starts is never bounded (R3 W1) | — | — | — | raised (Major, 4) | — | 1/3/0 | Major | Single-seat (1/4) |
| SC-20 | The fixed-dwell failure rate is convention-contingent, yet is presented as the robust reading and as practice-level failure (R3 W3) | — | — | — | raised (Major, 4) | M4 corroborated (Major, 4) | 1/3/0 | Major | Single-seat (1/4), DA corroborated |
| SC-21 | The uniform demand scan is not the operational per-tier axis; the curve cannot be mapped to a tasking decision (R3 W5) | — | — | — | raised (Minor, 4) | — | 1/3/0 | Minor | Single-seat (1/4) |
| SC-22 | Load-bearing convention labels and dated registered decisions are not defined inside the manuscript (R3 W6) | — | — | — | raised (Minor, 3) | — | 1/3/0 | Minor | Single-seat (1/4) |

#### Points of agreement

- **No sub-claim reached CONSENSUS-4 or CONSENSUS-3.** The strongest support in this panel is two-seat corroboration. Five sub-claims reach it: SC-1 (EIC + R3), SC-3 (EIC + R1), SC-4 (EIC + R1), SC-12 (R1 + R2), SC-16 (R2 + R3). The DA adds separate corroboration to SC-1 (M1), SC-10 (M3) and SC-20 (M4); the DA is not counted in the four-seat denominator.
- **Seventeen sub-claims are single-seat findings.** They are retained and evaluated against their named criteria and anchored evidence; they do not carry a consensus label and are not treated as weaker for that reason alone.
- **Cross-seat convergence on strengths** (not scored sub-claims, so not labelled consensus): the measured separation of construction face from search face (R1 S1; DA credits it), preregistration with failed criteria retained (R1 S2; DA credits it), the categorical separation of infeasibility from zero coverage (EIC S2; R3 S2), concrete reproducibility affordances (R1 S4; R3 S1), and faithful prior-work positioning (EIC S1; R2 S3). Every seat's card carries substantive praise on the measurement layer; this is the reason the decision is Major Revision rather than Reject.

#### Points of disagreement and unresolved items

- **No SPLIT.** No sub-claim drew a `disputed` position: there is no existence conflict and no incompatible-remedy conflict anywhere in the panel.
- **Severity divergence on SC-1** (EIC and DA Major; R3 Minor). The remedies are compatible in direction — R3's "compute the split or state that it is unavailable and why" is a superset of the EIC's minimum qualifier. **Editor's resolution:** obligation follows the Major transported severity because the abstract's headline sentence is affected; R3's Minor rating is preserved here rather than overwritten.
- **DA M2, M5, M6 received no assessment from the four non-DA seats.** This is silence, not agreement. They are recorded as panel-unresolved single-source findings, not as consensus, and are adjudicated individually below; the author must respond to each.
- **DA M5 premise correction.** In the manuscript, the sixteen-fold budget probe is described over twenty re-run units, while the 40-cell coverage belongs to the anchor-free arm (§5.5). The DA's stated "16-fold probe covering 40 of 260 cells" conflates the two probes. Its substance — that no probe covers the 260-unit grid at the higher budget — is unaffected, and the objection stands on the corrected premise.

### Devil's Advocate Adjudication

The DA's CRITICAL table is empty. The DA states this is by design: no singleton rejection-level defect was found. Six MAJOR findings remain and are adjudicated here. "Valid" means the finding's stated premise holds against the manuscript and no seat contradicts it; it is not a vote.

| DA ID | DA issue | Corroboration among non-DA seats | Adjudication | Required author response |
|---|---|---|---|---|
| M1 | Abstract attributes the headline drop to the stripmap floor while §7.1 concedes part of it is the comparability policy; the policy share is never bounded | EIC W1 (SC-1), R3 W2 (SC-1) | **Valid.** The juxtaposition is in the manuscript: the abstract's "stripmap floor accounting for 20.0 and 44.8 of those points" against §7.1's "part of the floor-dominated cost is the comparability policy, not the platform" | Bound or quantify the policy component, or carry the qualifier into abstract and conclusion |
| M2 | Served priority is the stated objective, but the served set is a near-proportional slice of the task set; the metric measures rather than demonstrates optimisation | None (unexamined by non-DA seats) | **Valid as framed.** The manuscript's own readings show served fractions 0.507/0.714/0.935 against priority fractions 0.483/0.688/0.948 and states the uniform priorities are "close to inert in practice" | Priority-aware selection arm, or explicit acknowledgement that the metric reduces to served-task fraction in this scenario set |
| M3 | The curve is construction-carried but not construction-invariant; only an anchor-free random arm is tested as an alternative construction | R1 W2 (SC-10) | **Valid.** The manuscript states the anchor pass can serve one task more or fewer between neighbouring requirements and that no statement attributes differences to the optimiser; that is a one-heuristic result | At least one second principled construction on the same cells, or scope the claim to this construction |
| M4 | The fixed-dwell violation rate is robust to the repair rule only; the zero-squint and conservative instantiations give 27–42% and zero | R3 W3 (SC-20) | **Valid.** The figure caption records the conservative arm at "no violating pair by construction" (0 of 324 and 0 of 354 pairs) at 28.3 and 55.5 points, so the violation rate is a property of the chosen dwell convention | Mid-squint baseline, or confine the claim to the planned-convention family and align the abstract |
| M5 | "Essentially solved by a single construction pass" is inferred from one failed search and a partial probe; a weak solver is equally consistent | None; R1 S1 credits the two probes | **Valid in part.** Premise corrected as above (20 units at 16×; the 40 cells are the anchor-free arm). The manuscript's own sentence scopes the claim to "where the coverage response comes from", but the quoted phrase states a problem property | Scope the phrase to what the probes establish, or add a stronger search or upper bound |
| M6 | The 50-task family's monotonicity failure is reported both as a result about the scenario set and as anchor granularity carrying no demand-axis statement | None | **Valid in part.** The two statements are about different objects (S1 verdict; §6.5 attribution of local declines), but the manuscript never reconciles them, so the double reading is available to a reader | One sentence reconciling the two statuses, or restrict where "result about this scenario set" is asserted |

### Decision Rationale

The decision is arithmetic first. Each dimension was scored only by its eligible seats, with ineligible values excluded from both numerator and denominator. All six dimensions are assessed at `warn`; no seat declared a block or a fatal block. F3 fires because all four mandatory dimensions sit at warn-or-worse in the majority of their eligible seats, and F5 fires because every dimension is warn-or-worse. F3 outranks F5 (70 > 40), so the mechanical decision is Major Revision; F1, F2, F4 and F0 do not fire.

The substance behind that arithmetic is consistent with it. The measurement layer drew repeated credit across seats: the construction/search separation, preregistration with failed criteria retained, the categorical separation of infeasibility from zero coverage, and the reproducibility affordances. The Major reservations concentrate on the interpretive surface of the headline. The floor share carries an unbounded policy component (SC-1); the drops are the greedy anchor's readings but appear unqualified in the abstract (SC-10); "mode-dependence" names a co-variation because density and mode composition change together (SC-3); the ambiguity module drops a scene-sweep term that the dwell closure keeps (SC-13); the fixed-dwell failure rate is convention-contingent (SC-20); and two operational constructs — the pointwise resolution identity (SC-19) and the served-priority objective (DA M2) — do not yet do the work their names promise. None of these demands new physics. Each demands a bound, an arm, or a scoped claim, which is what Major Revision is for. The panel found no fatal defect; it found a paper whose claims outrun its qualifiers.

### Blocking Issues (0–3, immutable source order)

The 0–3 cap is applied to the must-fix items in immutable source order, not by priority. R4–R9 also carry `must_fix` obligations and appear in the roadmap in the same order.

| Transport ref | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| R1 | The floor-dominated share of the headline contains an unbounded comparability-policy component, while the abstract attributes it to platform physics | EIC, R3, DA (M1) | text: Abstract vs §7.1 — "stripmap floor accounting for 20.0 and 44.8 of those points" / "part of the floor-dominated cost is the comparability policy, not the platform" | R1 |
| R2 | The central magnitude has no externally published planner as a denominator, so its significance cannot be placed against the field | EIC | absence: §2 related work, §5 results, §7.1 sixth scope statement; checked §2.2–2.4, Table 1, Figures 5–8, §5.6, §7.1 | R2 |
| R3 | The "mode-dependence" construct is not identified: density and mode composition covary across all three families | EIC, R1 | text: Fig. 4 caption — "Densities and mode composition covary by design across the three families, so nothing in this figure is a controlled comparison" | R3 |

### Review Panel Provenance (#540/#740)

Rendered from `review-panel-provenance/1.0` artifact `panel-provenance.json` (`panel_id: paper2-panel-full-20261031`; `contract_id: reviewer/reviewer_full/v2`; `schema_version: review-panel-provenance/1.0`; `independence_claim: not_computed_from_personas`). The six axes are reported separately. They are not collapsed into a binary or numeric independence claim.

| Axis | Value | Basis |
|---|---|---|
| `blind_to_peer_outputs` | true | All five seats recorded `peer_outputs_visible: false` |
| `fresh_context` | true | Scope is `within_panel_attempt_only` — a fresh context within this panel attempt only; this does not establish that a retry or later round used a context new to attempt history |
| `human_distinct` | false | All five seats are `actor_type: model` with `human_reviewer_id: null` |
| `model_family_distinct` | false | All five seats recorded `model_family: claude` |
| `provider_distinct` | unknown | `provider: null` on all five seats; no provider identity was recorded |
| `role_separated` | true | Five role ids: eic, methodology, domain, perspective, da |

**Correlated-error disclosure** (`required: true`, `reason: same_model_family`): "All model-executed review seats used one model family; role separation does not remove correlated-error risk."

This panel is therefore **not** described as independent. Role separation is reported as a configuration fact, not as evidence of independent error processes, and the convergent readings above are not independent confirmations.

Recorded digests: `contract_sha256: e9712090d2469fea15a37b8e22d4e137afbcb2bf38d5789939c5df56738ef7af`; `execution_topology_sha256: 54b608f6e8509ce5bf3cf2686469e70fc574c3cf763e5caa40e6cb07b19ac244`; `normalized_manifest_sha256: 8ea0f5a76fc99ee0f481a16bb85983da44586a582977aaf14bde457d7858d599`.

### Required Author Response

A point-by-point response is required for every roadmap item below, including the DA-only items. For each item the response must state whether the item is addressed in full, partially, or declined, and give the reason. A declined item remains visible and unresolved; it is not forbidden.

---

## Part 2: Revision Roadmap

Transport refs `R{n}` follow immutable source order (seat order EIC, R1, R2, R3, DA; then finding ordinal) filtered to `must_fix`; `S{n}` and `C{n}` follow the same order within their obligation classes. The numbering is a transport reference, not a rank, and the array order is not a work order.

### Required Revisions (Must Fix)

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Obligation class | Cost scope | Bounded consequence |
|---|---|---|---|---|---|---|---|---|---|
| R1 | [Abstract; §1.2; §7.1; §8] Carry the comparability-policy qualifier wherever the floor share is headlined, and either bound the policy-priced component with a rescue-permitted floor-exclusion arm on the same manifests or state that the split is unavailable and why | SC-1 (EIC W1; R3 W2; DA M1) | major | text: Abstract vs §7.1 — "stripmap floor accounting for 20.0 and 44.8 of those points" / "part of the floor-dominated cost is the comparability policy, not the platform" | 5 — direct juxtaposition of two passages | EIC; corroborated R3 (minor, 4), DA (major, 5) | must_fix | section + re_analysis: Abstract, §1.2, §7.1, §8; floor-exclusion bound under rescue | claim_scope_unsupported → claim: headline floor attribution |
| R2 | [Abstract; §1.2; §2.4; §7.1] Give the served-priority magnitude an external denominator — at least one published mission-planning or SAR scheduler run on the released scenario set — or rescope the significance claim so it does not rest on an unanchored magnitude | SC-2 (EIC W2) | major | absence: §2 related work, §5 results, §7.1 sixth scope statement; checked §2.2–2.4, Table 1, Figures 5–8, §5.6, §7.1 | 5 — absence verified across results and discussion | EIC | must_fix | re_analysis: one published planner on released scenarios; alternative section: significance claims | evidence_gap_remains → claim: significance |
| R3 | [Abstract; §1.2 contribution 2; §5.1; §6] Restate the second contribution as a family-shape contrast under covarying density and composition, or add a density-matched arm (all-stripmap or no-stripmap at N=100, or a stripmap-bearing family at N=50) | SC-3 (EIC W3; R1 W1) | major | text: Fig. 4 caption — "Densities and mode composition covary by design across the three families, so nothing in this figure is a controlled comparison" | 4 — the manuscript states the confound | EIC, R1 | must_fix | section + re_analysis: contribution/abstract; one density-matched arm | claim_scope_unsupported → claim: "mode-dependence" |
| R4 | [Abstract; §1.2; §5.5; §7.1] Carry the anchor-construction qualifier (258/260 best-found; no non-trivial upper bound at the as-placed point) into the abstract and contribution where the 26.0/46.6-point drops and 4.15/2.36-point premiums are quoted, or phrase them as what this construction paid | SC-10 (R1 W2; DA M3) | major | text: Abstract — "the dense family drops 26.0 percentage points to the next point and 46.6 to the tightest one" | 4 — inference-to-design matching | R1; corroborated DA (major, 4) | must_fix | section: Abstract, §1.2, §7.1 | claim_scope_unsupported → claim: coverage drops |
| R5 | [§3.3; §7.2] Re-evaluate the azimuth-ambiguity integral with a scene-sweep occupancy term consistent with the §3.2 $W_a$ dwell closure and re-read the squint-direction contrast, or withdraw the claim of "a difference of mechanism, not merely of sign" | SC-13 (R2 W1) | major | text: §3.3–§7.2 — "the compression factor $a_{\mathrm{res}}\equiv A$ is squint-invariant" / "the registered scene term $W_a$ enters unscaled" | 4 — derived from the manuscript's formulas, cross-checked against the standard treatment | R2 | must_fix | re_analysis: §3.3 ambiguity integral, §7.2 contrast | claim_scope_unsupported → claim: squint-direction mechanism |
| R6 | [§3.4 C5 statement; §5 dwell distribution] Report the cosine-ratio degradation at the selected starts as a per-mode worst case from the dwell-distribution data already computed, or add a one-line bound to the constraint statement | SC-19 (R3 W1) | major | text: §3.4 — "this paper does not claim a constant delivered resolution across a whole imaging pass" | 4 — operations read of a resolution specification | R3 | must_fix | sentence + section: §3.4, one table or line from existing data | interpretive_ambiguity_remains → claim: resolution specification |
| R7 | [Abstract; §6.6] Separate the 27–42% violation rate from the zero-squint convention that generates it: add a realistic mid-squint baseline or confine the claim to the planned-convention family, and align the abstract's "it fails measurably" with that scope | SC-20 (R3 W3; DA M4) | major | text: §6.6 — "the dwell held at its zero-squint library value at every consumption point"; conservative arm "no violating pair by construction" | 4 — two arms with opposite violation outcomes | R3; corroborated DA (major, 4) | must_fix | section: Abstract, §6.6; optional re_analysis: mid-squint arm | claim_scope_unsupported → claim: fixed-dwell failure |
| R8 | [§4 objectives; §6 served-priority reading] Add a priority-aware selection arm, or state explicitly that in this scenario set the served-priority metric reduces to the served-task fraction because uniform priorities are near inert | — (DA M2) | major | text: §6.2 — "the uniform random priorities are close to inert in practice ... a proportional slice of the task set rather than a priority-selected one" | 4 — the manuscript's own served-versus-priority fractions | DA | must_fix | re_analysis: priority-aware arm; alternative section: objective statement | claim_scope_unsupported → claim: served-priority objective |
| R9 | [§5.5] Scope "essentially solved by a single construction pass" to what the probes establish, including probe coverage, or add a stronger search or an upper bound | — (DA M5) | major | text: §5.5 — "the selection problem is, in this scenario set, essentially solved by a single construction pass" | 3 — budget and probe coverage stated by the paper | DA | must_fix | sentence: §5.5 | claim_scope_unsupported → claim: solver statement |

### Suggested Revisions (Should Fix)

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Obligation class | Cost scope | Bounded consequence |
|---|---|---|---|---|---|---|---|---|---|
| S1 | [Abstract; §1.2; §5.3] Repeat the two-date boundary once on the contribution surface: grid and criteria preregistered; coverage–demand curve designation post hoc | SC-4 (EIC W4; R1 W5) | minor | text: §5.3 — "is dated 2026-10-21, after the sweep ran on 2026-10-20" | 5 — dates stated explicitly | EIC, R1 | should_fix | sentence + section: Abstract, §1.2 | reporting_requirement_unmet → claim: preregistration |
| S2 | [§4.5] Present the deterministic construction as the method and the evolutionary search as a check on it | SC-5 (EIC W5) | minor | text: §4.5 — "the greedy anchor already attains the best coverage found for the unit in this study in 258 of the 260 units" | 4 — section role versus measured contribution | EIC | should_fix | section: §4.5 framing | interpretive_ambiguity_remains → section: §4 |
| S3 | [Table 1; §6.2] Print Table 1 at the precision the text quotes, or quote the drop to the table's precision (0.948, 0.483 → 46.5, not 46.6) | SC-6 (EIC W6) | minor | table: Table 1, R3H observed column, rows $s=1.0$ and $s=0.8$ (0.948 and 0.483) | 5 — arithmetic from printed values | EIC | should_fix | sentence + table: Table 1 | reporting_requirement_unmet → table: Table 1 |
| S4 | [§5.6; §6.6; Appendix] Move the dated registration chain to an appendix and replace the "this revision" deixis with ordinary tense | SC-7 (EIC W7) | minor | text: §5.6 — "reanalysis additions of this revision" | 5 — verbatim in the manuscript | EIC | should_fix | section: §5.6, §6.6, appendix | editorial_conformance_unmet → manuscript |
| S5 | [Abstract] Add one sentence naming the contribution before the numbers, and an explicit subject for "it fails measurably" | SC-9 (EIC W9) | minor | text: Abstract — "For a sliding-spotlight platform it fails measurably" | 5 — reading of the abstract as printed | EIC | should_fix | sentence: Abstract | reader_traceability_reduced → claim: abstract |
| S6 | [§6.2 and every headline contrast] Report the same interval form for every headline contrast, or state once that all inference is descriptive over the ten registered draws | SC-11 (R1 W3) | minor | text: §6.2 — "A seed-level bootstrap of those ten paired R3H drops" | 4 — resampling design | R1 | should_fix | section: §6.2 and affected results | reporting_requirement_unmet → manuscript |
| S7 | [§3.4; §6] Report the coverage curve under the prior normalisation at the grid points where violations appeared, or justify analytically that the per-task envelope reference cannot mask a binding channel | SC-12 (R1 W4; R2 W5) | minor | text: §3.4 — "the normalisation reference was redefined on 2026-10-20, on the day the sweep ran" | 3 (R1) / 4 (R2) — data-dependent calibration | R1, R2 | should_fix | re_analysis or section: §3.4, §6 | evidence_gap_remains → claim: constraint calibration |
| S8 | [§1.2] State in the contribution sentence that C5 is a consistency architecture rather than a validated physical model | SC-14 (R2 W2) | minor | text: §1.2 — "an identity the search cannot violate rather than a constraint it could" | 4 — C5 construction and verification visible in §3.4 | R2 | should_fix | sentence: §1.2 | interpretive_ambiguity_remains → claim: platform contribution |
| S9 | [§3.2] State at the closure's introduction that the production closure's error against truth is unquantified, not only that the two internal closures differ by at most 1.9% | SC-15 (R2 W3) | minor | text: §3.2 — "the symmetric construction deviates from the exact chain by at most $1.9\%$" | 4 — both closures and their comparison in one paragraph | R2 | should_fix | sentence: §3.2 | interpretive_ambiguity_remains → claim: dwell closure |
| S10 | [§3.3; Abstract] Pair the reported quality reading with a resolution-dominated label at first use and state what it licenses and what it does not; optionally carry one calibrated side descriptor | SC-16 (R2 W4; R3 W4) | minor | text: §3.3 — "the index deliberately weights azimuth resolution twice" | 4 — construction and disclosure explicit | R2, R3 | should_fix | sentence + section: §3.3, Abstract | interpretive_ambiguity_remains → claim: quality index |
| S11 | [§6.7; Abstract framing] Run the per-tier variant on the mixed family, or state at the abstract-level framing that the uniform scan is a controlled analogue, not an operational forecast | SC-21 (R3 W5) | minor | text: §6.7 — "the axis an operator would actually use" | 4 — requirements-management reading | R3 | should_fix | section or re_analysis: §6.7, Abstract | interpretive_ambiguity_remains → claim: operational reading |
| S12 | [Appendix] One compact appendix table mapping each convention label and dated registered decision to its content and its effect on the reported readings | SC-22 (R3 W6) | minor | absence: model, experimental-design, and results sections; checked nomenclature, model, design, results, discussion | 3 — outsider reconstruction from the manuscript alone | R3 | should_fix | section: appendix | reader_traceability_reduced → manuscript |
| S13 | [§5.3; §6.5] Reconcile in one sentence the R2F S1 verdict ("a result about this scenario set") with the anchor-granularity attribution of the same movements | — (DA M6) | major | text: §5.3 vs §6.5 — "both failures are reported as results about this scenario set" / "no statement about the demand axis is made from a movement in the third decimal place" | 4 — two stated positions on one pair of numbers | DA | should_fix | sentence: §5.3, §6.5 | interpretive_ambiguity_remains → claim: R2F monotonicity |

> Obligation is an editorial gate, not a copy of severity. S13 carries a transported Major severity but a one-sentence resolution of a labelling tension, so it is gated at `should_fix` rather than `must_fix`.

### Optional Polish (Consider)

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Obligation class | Cost scope | Bounded consequence |
|---|---|---|---|---|---|---|---|---|---|
| C1 | [§4.1] Define the family identifiers R3H and R1C on first use, or defer the identifiers to the results | SC-8 (EIC W8) | minor | text: §4.1 — "the densest real-window family (R3H" | 5 — direct reading order | EIC | consider | sentence: §4.1 | reader_traceability_reduced → section: §4.1 |
| C2 | [§3.4; Abstract] Present C1–C5 as a model whose binding set has two members, rather than as five interacting constraint families | SC-17 (R2 W5) | minor | text: §3.4 — "has exactly two members" | 4 — both statements in one paragraph | R2 | consider | sentence: §3.4, Abstract | interpretive_ambiguity_remains → claim: platform model |
| C3 | [§3.3–§3.5] State the resolution-pair and dwell-pair distinctions at first use of each pair | SC-18 (R2 W6) | minor | text: §3.3 — "denotes spatial-resolution quality under a gain-shaped multiplier" | 3 — judged from the manuscript's usage pattern | R2 | consider | sentence: §3.3–§3.5 | reader_traceability_reduced → manuscript |

### Source-Traceability Checklist

- [ ] R1 — obligation `must_fix`: qualify or bound the comparability-policy share of the floor cost
- [ ] R2 — obligation `must_fix`: external denominator for the served-priority magnitude, or a rescoped significance claim
- [ ] R3 — obligation `must_fix`: identify or withdraw the "mode-dependence" construct
- [ ] R4 — obligation `must_fix`: carry the anchor-construction qualifier to the abstract and contribution
- [ ] R5 — obligation `must_fix`: resolve the ambiguity-module scene-sweep asymmetry
- [ ] R6 — obligation `must_fix`: bound the intra-dwell resolution degradation at the selected starts
- [ ] R7 — obligation `must_fix`: scope the fixed-dwell failure to its convention, or add a mid-squint baseline
- [ ] R8 — obligation `must_fix`: test or acknowledge the served-priority objective's inert weighting
- [ ] R9 — obligation `must_fix`: scope the "essentially solved" inference
- [ ] S1 — obligation `should_fix`: state the two-date preregistration boundary on the contribution surface
- [ ] S2 — obligation `should_fix`: reframe §4.5 around the construction, with the search as a check
- [ ] S3 — obligation `should_fix`: align Table 1 precision with the quoted drop
- [ ] S4 — obligation `should_fix`: move process metadata to an appendix and remove "this revision"
- [ ] S5 — obligation `should_fix`: name the contribution and the failing subject in the abstract
- [ ] S6 — obligation `should_fix`: harmonise uncertainty reporting across headline contrasts
- [ ] S7 — obligation `should_fix`: justify or sensitivity-check the C3 normalisation redefinition
- [ ] S8 — obligation `should_fix`: label C5 as a consistency architecture in the contribution sentence
- [ ] S9 — obligation `should_fix`: state that the production dwell's error against truth is unquantified
- [ ] S10 — obligation `should_fix`: label and bound the quality index's product meaning
- [ ] S11 — obligation `should_fix`: state that the uniform scan is a controlled analogue
- [ ] S12 — obligation `should_fix`: add the convention/provenance appendix table
- [ ] S13 — obligation `should_fix`: reconcile the R2F S1 verdict with the anchor-granularity attribution
- [ ] C1 — obligation `consider`: define family identifiers on first use
- [ ] C2 — obligation `consider`: describe the constraint inventory by its binding set
- [ ] C3 — obligation `consider`: disambiguate resolution and dwell terminology at first use

### Response Letter Template

Use the reviewer skill's `templates/revision_response_template.md` format and respond to every item above, including the DA-only items R8, R9, and S13. Each response should state the item, the action taken with its section reference, and the verification performed; a declined item should state the reason and remain visible.

---

## Part 3: Reviewer Report Summary (Appendix)

The five cards are sprint-contract dimension cards. They carry dimension scores and per-finding confidence, not a report-level recommendation or report-level confidence; no recommendation is inferred here.

### Journal-Fit Review Report Summary

- Dimension scores: D5 = warn; D6 = warn; D1–D4 not assessed (ineligible).
- Per-finding confidence: 4–5.
- Key point: positioning, disclosure, and the infeasibility/zero distinction are strong; the headline invites over-attribution of the floor cost, and the mode-dependence construct is not identified.

### Reviewer 1 (Methodology) Summary

- Dimension scores: D1 = warn; D3 = warn; D2, D4–D6 not assessed (ineligible).
- Per-finding confidence: 3–4.
- Key point: the design and reproducibility reporting are unusually strong; the cross-family attribution and the abstract's construction-bounded losses exceed what the design supports, both repairable by scoping or one controlled arm.

### Reviewer 2 (Domain) Summary

- Dimension score: D2 = warn; D1, D3–D6 not assessed (ineligible).
- Per-finding confidence: 3–4.
- Key point: the physics chain and load-bearing constants reproduce independently; the substantive reservation is the ambiguity module's scene-sweep asymmetry, which leaves the squint-direction mechanism claim unsupported.

### Reviewer 3 (Perspective) Summary

- Dimension score: D4 = warn; D1–D3, D5–D6 not assessed (ineligible).
- Per-finding confidence: 3–4.
- Key point: reproducibility and construct guarding are excellent; the resolution identity, the fixed-dwell baseline, and the floor decomposition each need one more translation step before an operations reader can act on them.

### Devil's Advocate Summary

- Recommendation: not stated — findings only.
- Findings: 0 CRITICAL, 6 MAJOR, 0 MINOR.
- Key challenge: the headline may measure a bookkeeping convention more than a physical cost — under a frozen routing and one greedy construction, coverage is nearly insensitive to the requirement except where the antenna floor makes service arithmetically impossible. The DA records that this alternative fits every reported number, and states the CRITICAL table is empty by design rather than default.

## Attachment: Suggested-Reference Check (advisory, #1001)

```text
Suggested-reference check (script output, not a reviewer finding; #1001)
Seats read: R2, R3 (partial).
Not read:
- R2: the report has no suggested-references block.
- R3: the report has no suggested-references block.
No suggested reference could be read.
```

## Attachment: Reviewer Claim Check (advisory, #1002)

The reviewer claim check did not run: it requires a tool-less judge subagent, and this Windows inline-panel orchestration did not invoke one. This omission is advisory only; it changes no finding, score, roadmap item, or decision.

## Attachment: Acronym Check (advisory, #849)

```text
### Acronym check (advisory; no reply needed)
Coverage: body, English abstract (partial)
Not in this input: Chinese abstract.
Not checked:
- Body, line 122: SLS (the initials before its parentheses do not spell it)
- Body, line 122: SPT (the initials before its parentheses do not spell it)
- Body, line 122: STR (the initials before its parentheses do not spell it)
- Body, line 147: SAT (the initials before its parentheses do not spell it)
- Body, line 179: AASR (the initials before its parentheses do not spell it)
- Body, line 278: UTC (the initials before its parentheses do not spell it)
- Body, line 309: R1C (the initials before its parentheses do not spell it)
- Body, line 309: R2F (the initials before its parentheses do not spell it)
- Body, line 309: R3H (the initials before its parentheses do not spell it)
- Body, line 490: DC (the initials before its parentheses do not spell it)

| Scope | Line | Rule | Acronym | Uses |
|---|---|---|---|---|
| Body | 78 | Not defined | GF | 1 |
| Body | 228 | Not defined | NP | 1 |
| Body | 291 | Not defined | R4H | 1 |
| Body | 508 | Not defined | ECEF | 2 |
```
