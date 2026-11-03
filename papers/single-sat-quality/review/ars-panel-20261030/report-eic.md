# EIC report — ars-panel-20261030
## Canary
1. Read-only: I must not modify, create, or delete any file except my one report file.
2. Every finding must quote the exact manuscript text it criticizes, with section name and approximate tex line number.
3. No fabricated facts: I never assert what a cited reference contains beyond what the manuscript itself claims; literature gaps are phrased as candidate gaps only.
4. Numbers: I quote them exactly as in the manuscript; I never compute, alter, or correct numbers (arithmetic-consistency observations allowed only as "state A appears inconsistent with state B as quoted").
5. No network access; I do not attempt to fetch references.
6. I report genuine strengths and weaknesses; no manufactured findings, no finding quotas, no rubber-stamping.
7. My stdout is at most 5 lines; the report goes to the file.

## Overall assessment
**Recommendation: Major** from the fit-and-framing standpoint. The manuscript is a strong ASR scope fit: it couples agile-satellite mission planning with acquisition-geometry-dependent SAR quality, and its single-satellite, two-orbit boundaries are clear. The experimental narrative is unusually candid about hot-start dependence, approximate Pareto fronts, resource ceilings, and proxy metrics. The main numerical claims in the abstract and highlights have identifiable support in §6–§7, and the advertised formulation and density-dependent analyses are substantively delivered.

Two framing problems prevent a Minor recommendation. First, the title, abstract, highlights, and conclusion present NESZ/radiometric percentage gains without carrying the body's explicit restriction of $f_3$ to a geometry-based relative ordering index; "+40% NESZ" is therefore not an accurate statement of the evidence. Second, the novelty statement in §2.3 is difficult to reconcile with the manuscript's own descriptions of cited MOEA and bi-objective image-quality scheduling work. These issues affect central positioning rather than isolated wording. I also recommend narrowing universal dense-regime wording, qualifying the optical-transfer claim, and making the abstract's density units and specialist terminology accessible to a broad ASR readership.

## Findings

**EIC-01** | Severity: MAJOR | Location: Title, Abstract, §3.2 Objective Functions, Conclusion; tex lines 23, 45, 427–436, 1582–1585; Highlights lines 16 and 22

Quote: "Third objective matters at sparse density: +40\% NESZ over greedy at 15\% coverage cost" (Highlights); by contrast, §3.2 states "a relative ordering index across observation geometries, not as an absolute radiometric prediction" and "a geometry proxy rather than an absolute NESZ ranking across widely separated incidence angles."

Issue: The front matter and conclusion convert an explicitly qualified geometry-based ordering index into unqualified NESZ or radiometric-quality improvement. The title similarly names NESZ without signaling a proxy. The body supports percentage changes in $f_3$, not a demonstrated percentage improvement in absolute NESZ or operational image quality.

Why it matters: This is the paper's most visible value claim and the third objective's principal motivation. An ASR reader can reasonably interpret "+40% NESZ" as a physical radiometric improvement, whereas the manuscript itself disclaims that interpretation. The limitation should travel with the claim, not appear only in the methods section.

Suggested remedy (non-binding): Rename the metric consistently as an NESZ-related geometric/radiometric ordering proxy in the title or abstract, highlights, and conclusion. Report "+40% in $f_3$" rather than "+40% NESZ," with a short proxy qualifier at first use. Retain the body's explanation of the suppressed factor and restricted comparison domain.

**EIC-02** | Severity: MAJOR | Location: §2.1 Related Work and §2.3 Positioning; tex lines 234–249 and 305–307

Quote: "To our knowledge, MOEAs have not been applied to SAR scheduling with physical quality objectives; the closest work uses single-objective optimization with post hoc quality evaluation." Earlier, §2.1 describes cited work that "incorporates a composite image quality score as an optimization objective" and another "bi-objective image-quality-loss/energy model."

Issue: As written, the novelty statement appears inconsistent with the manuscript's own related-work summary. The defensible candidate delta is narrower and is already visible elsewhere in the paper: separate, continuous, physics-derived geometric and radiometric objectives, rather than a scalar visibility/image-quality composite or an attitude-angle proxy. Section 2.3 does not carry that distinction into either its negative claim or its "closest work" claim.

Why it matters: Positioning against the cited literature is central to editorial originality assessment. An apparent internal contradiction invites the reading that prior multi-objective quality-aware scheduling is being understated, even though contribution 4 offers a more precise and plausible distinction.

Suggested remedy (non-binding): Replace the broad absence claim with the specific formulation delta and identify which cited work is closest under that definition. Explicitly distinguish physical objective decomposition from composite quality scores, post hoc evaluation, and operational objectives; avoid implying that all cited quality-aware approaches are single-objective.

**EIC-03** | Severity: MINOR | Location: §6.4 Mechanism of Pareto Compression; tex lines 1058–1066

Quote: "In dense regimes, solver convergence to lower-squint geometries combined with schedule saturation limits quality differentiation regardless of solver strategy."

Issue: "Regardless of solver strategy" is broader than the evidence and sits uneasily with the same paragraph's correct restriction to "the found front under G-BL-seeded search" and the full-coverage working point. The study compares configurations within one algorithmic family plus greedy controls; it does not establish a solver-independent limit over the feasible surface.

Why it matters: A universal mechanism statement can outlive the surrounding caveats when quoted or paraphrased, turning a conditional empirical result into a general claim about scheduling algorithms.

Suggested remedy (non-binding): Replace the universal phrase with the tested scope, for example differentiation among the tested G-BL-seeded NSGA-III configurations near the full-coverage operating point. Preserve the existing statement that the full feasible trade-off surface is not established.

**EIC-04** | Severity: MINOR | Location: §7.3 Transferability Across Remote-Sensing Domains; tex lines 1510–1522

Quote: "the same density-dependent saturation would appear"

Issue: The manuscript predicts with certainty that the empirical saturation phenomenon transfers to optical systems, but the presented experiments concern single-satellite Stripmap SAR. The envelope–null–schedule decomposition may be transferable; the occurrence of the same saturation phenomenon is not demonstrated here.

Why it matters: This shifts a useful analytical hypothesis into an unsupported cross-domain finding and unnecessarily broadens the paper's claims beyond its evidence.

Suggested remedy (non-binding): Recast this as a testable possibility ("could" or "would be expected under analogous coverage-pressure conditions") and distinguish transfer of the analytical device from transfer of the empirical result.

**EIC-05** | Severity: MINOR | Location: Abstract; tex lines 40–50

Quote: "Across 200 scenarios spanning densities 20--500" and "matched radiometric-aware knee rule"

Issue: The abstract does not explain that density is target count per common two-orbit scenario, and it introduces several specialist constructs—knee rule, greedy coverage anchor, hot start, and multiple correlation values—before their operational meaning is available. The numbers are supported, but the entry point is dense for an ASR-wide reader without SAR-scheduling background.

Why it matters: The abstract is the primary accessibility point for the journal's broad readership. "Densities 20--500" can be misread as a spatial density with omitted units, while the selector terminology obscures the otherwise useful conditional third-objective result.

Suggested remedy (non-binding): State "20--500 targets per two-orbit scenario" and simplify or briefly contextualize the knee-rule statement. Prioritize the operational finding—when the extra objective changes the selected schedule—over algorithm-internal terminology in the abstract.

## Non-defect observations
- Scope fit is strong: scheduling acquisition times explicitly changes observation geometry, making the quality-aware mission-planning problem appropriate for an ASR audience.
- Apart from the NESZ/proxy wording, the checked headline numbers have body anchors: the sparse geometric and radiometric-index gains and coverage costs appear in §6.1, the controlled $+4.9\%$ margin in §6.4, and the G-SM trade-off in §6.2.
- The introduction's principal contributions are delivered: the formulation is specified, density-dependent saturation is measured, the third-objective and coupling mechanisms receive ablations and controls, and operational guidance is qualified by an agility-envelope sensitivity analysis.
- The paper is commendably explicit about hot-start dependence, anchored rather than globally maximal sparse fronts, best-known rather than verified Pareto sets, class-mean versus per-scenario behavior, resource-cap effects, fixed dwell, and the absence of learning-based benchmarks.
- The distinction between coverage convergence and per-task quality is maintained particularly well, as is the distinction between mathematical redundancy and empirical convergence under coverage pressure.
