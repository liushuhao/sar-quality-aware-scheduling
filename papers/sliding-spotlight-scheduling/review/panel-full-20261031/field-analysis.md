# Field Analysis Report

## Paper Basic Information
- **Title**: Resolution-Driven Scheduling of Agile SAR Satellite: From Fixed to Endogenous Imaging Dwells
- **Abstract length**: Approximately 256 words
- **Full text length**: Approximately 20,600 words (source-derived approximation from the Introduction through the end matter, including tables, captions, and mathematical tokens)
- **Number of references**: 36 entries in `refs.bib`

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| Primary Discipline | Agile Earth-observation satellite mission planning and scheduling, with a core contribution in physics-constrained synthetic aperture radar (SAR) satellite scheduling |
| Secondary Disciplines | SAR imaging physics and signal-quality modeling; operations research, single-machine scheduling, and evolutionary optimization; simulation-based experimental design and sensitivity analysis |
| Research Paradigm | Quantitative Research — a formal physics-to-scheduling model evaluated through computational experiments, counterfactual comparisons, and sensitivity analyses |
| Methodology Type | Experimental (in-silico simulation) and Comparative Study — three scenario families, a nine-point demand scan, fixed-dwell and initialization counterfactuals, budget probes, and policy-knob reanalyses |
| Target Journal Tier | **criteria_binding_unavailable** — no author-confirmed #683 Review Target Context or criteria manifest was supplied. No venue, quartile, or journal-specific fit is asserted. Field-general observation: this is a technically dense, specialised aerospace/operations-research manuscript whose maturity and significance should be assessed without invented venue criteria. |
| Paper Maturity | **Pre-submission** — the manuscript has a complete research-paper structure, a substantial related-work positioning, formal constraints and equations, eight figures, two tables, detailed results and limitations, and formatted declarations. Its prose is polished but exceptionally dense, so final review should test claim hierarchy and accessibility as well as technical correctness. |

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC  
**Display role**: Journal-Fit Reviewer  
**Identity Description**: Internal field-general editor experienced in triaging interdisciplinary aerospace-systems, remote-sensing, and operations-research manuscripts, with particular expertise in judging when a physics-to-planning integration constitutes a transferable research contribution rather than a platform-specific engineering demonstration. With no confirmed target venue, this reviewer evaluates editorial significance and likely reader interest without applying or inventing journal-specific criteria.

**Review Focus**:
  1. Assess whether making imaging dwell endogenous to per-task resolution requirements is a substantive scheduling contribution beyond combining established SAR equations with an evolutionary scheduler.
  2. Test whether the title, abstract, contribution claims, and conclusion accurately reflect the actual evidence: requirement sensitivity under a frozen mode assignment, synthetic scenarios, one reference platform, and results carried predominantly by a greedy construction.
  3. Judge the coherence and accessibility of the paper for readers spanning mission planning and SAR engineering, including whether methodological caveats and historical amendments obscure rather than clarify the central contribution.

**Will particularly care about**: Whether the paper offers a general problem formulation and a convincing scientific insight that remain valuable after its scenario-specific and policy-specific floor effects are discounted. The reviewer will also ask whether the work's significance is clear without relying on a named venue's preferences.

**Possible blind spots**: May not independently re-derive the SAR closures or audit the seed-level experimental evidence, and may over-weight breadth, narrative economy, or perceived readership appeal relative to technical validity.

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1  
**Display role**: Peer Reviewer 1  
**Identity Description**: Researcher in simulation-based optimization and computational experimental design for time-dependent single-machine and satellite scheduling, specializing in paired-seed comparisons, counterfactual ablation, search-versus-construction attribution, and uncertainty analysis for heuristic schedulers.

**Review Focus**:
  1. Evaluate the internal validity of the nine-point demand scan: paired use of scenario populations, ten-seed median and bootstrap summaries, the shared scenario/search seed confound, treatment of infeasible cells, and the distinction between preregistered criteria and post hoc main-result or verdict refinements.
  2. Assess whether the anchor-dominance, anchor-free, sixteen-fold-budget, fixed-dwell, repair-rule, margin, and tier-shift probes actually support the attribution of observed effects to construction and constraint physics rather than to search behavior.
  3. Examine the inferential scope of family comparisons and sensitivity claims, especially density/mode-composition confounding, saturation-defined costs, structurally slack C3/C4 constraints, uniform demand scaling, and the absence of published-scheduler baselines.

**Will particularly care about**: Whether each numerical statement has a design capable of supporting it, and whether descriptive, causal, and optimizer-related claims are kept distinct. The reviewer will scrutinize whether infeasibility, zero coverage, construction shortfall, and physical unavailability are analyzed as different events.

**Possible blind spots**: May treat the SAR physical model as an exogenous input and under-examine whether equation or geometry errors invalidate the scheduling experiment; may also emphasize internal validity at the expense of literature novelty and operational relevance.

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2  
**Display role**: Peer Reviewer 2  
**Identity Description**: Senior researcher in agile SAR satellite mission planning and sliding-spotlight/spotlight imaging, specializing in rotation-centre geometry, synthetic-aperture-time and dwell closures, attitude-maneuver modeling, azimuth ambiguity, and quality-aware observation scheduling.

**Review Focus**:
  1. Check the physical correctness and provenance of the rotation-centre formulation, mode resolutions, task-level C5 parameter laws, scene-level dwell closures, squint dependence, velocity convention, and start-domain clipping, including the registered broadside-derived and high-squint approximations.
  2. Evaluate whether the AASR admission model, uncalibrated quality index, range-resolution anchor, and C2 maneuver/transfer approximation support the paper's feasibility and image-quality statements, and whether their disclosed omissions threaten the central coverage results.
  3. Assess the accuracy and completeness of the literature positioning, particularly the claimed contrast with fixed-duration agile scheduling, the nearest SAR-specific planning work, and the distinction between requirement-driven parameter adaptation and requirement-driven mode routing.

**Will particularly care about**: Whether the endogenous dwell is physically faithful enough to justify the reported scheduling consequences, and whether the claimed research seam remains genuine after the closest imaging and mission-planning literature is interpreted correctly.

**Possible blind spots**: May concentrate on equation fidelity and literature genealogy while giving less attention to statistical design, search diagnostics, presentation accessibility, or whether the proposed model is useful to mission operators.

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3  
**Display role**: Peer Reviewer 3  
**Identity Description**: Earth-observation mission-operations and SAR data-product researcher specializing in translating customer resolution orders into acquisition plans, ground/onboard replanning interfaces, and product-level verification. This paper is highly cross-disciplinary; the disciplinary coverage strategy is for Reviewer 2 to cover core SAR physics and agile-scheduling scholarship, while this reviewer examines the distinct operational and data-product realization perspective.

**Review Focus**:
  1. Test whether resolution equality at the selected start, a grandfathered mode assignment, and a reported rather than optimized quality index are meaningful models of an actual customer product and delivered full-scene acquisition.
  2. Assess the operational interpretation of the fixed-dwell counterfactual and repair rules, including how two-body orbit propagation, lower-bound maneuver pricing, slack energy/memory budgets, and omitted downlink, dynamic-arrival, and replanning processes limit deployment conclusions.
  3. Evaluate reproducibility and pathways to practical use: whether the synthetic demand template, released-artifact promises, scenario assumptions, and proposed onboard/constellation continuations provide a credible basis for independent replication and eventual mission validation.

**Will particularly care about**: Whether the scheduling output corresponds to a product an operator could actually promise and verify, and whether the counterfactual yields actionable guidance for acquisition planning rather than only an internally consistent simulation result.

**Possible blind spots**: May penalize the paper for omitted operational systems that lie outside its declared single-pass scope, request deployment evidence disproportionate to a model study, or under-assess formal scheduling novelty and statistical rigor.

## Review Strategy Recommendations

- Keep the panel venue-neutral. The Journal-Fit/internal EIC seat should evaluate originality, significance, and reader interest at the field level only; no quartile, named-journal standard, or substitute target should enter the review.
- Separate three evidence layers explicitly: mathematical/model identities, simulation-derived empirical readings, and operational interpretation. A valid construction identity does not by itself validate the physical approximation, and a large simulated sensitivity does not by itself establish mission-level impact.
- Make the frozen mode assignment a central cross-seat question. The methodology reviewer should test its experimental-comparability rationale, the domain reviewer its physical and literature meaning, the practical reviewer its product-policy realism, and the EIC whether the resulting scope still supports the headline contribution.
- Preserve the manuscript's distinction between construction and search. Reviewers should not convert the 258/260 anchor result into either an optimizer-superiority claim or an automatic dismissal; they should ask whether the greedy construction and counterfactual probes are adequate instruments for the paper's actual estimands.
- Enforce disciplined interpretation of the scenario matrix: density and mode composition covary across families, so cross-family level rankings need special scrutiny; infeasible cells are not zero-coverage observations; preregistered grid/criteria and later descriptive or refined readings should not be collapsed into one evidentiary status.
- Expect productive tension between seats. The domain reviewer may regard physical approximations as decisive where the methodology reviewer sees an internally valid model-based experiment; the practical reviewer may request routing or replanning beyond the declared scope. The synthesizer should distinguish threats to current claims from valuable future extensions rather than averaging these positions.
- The fixed Devil's Advocate remains the fifth execution seat and receives no dynamic configuration card; its most useful target is the strongest version of the novelty and evidence claims, not a repeat of any single specialist checklist.
