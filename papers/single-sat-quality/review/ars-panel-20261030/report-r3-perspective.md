# R3 (Perspective) report — ars-panel-20261030

## Canary

1. Read-only: I must not modify, create, or delete any file except my one report file.
2. Every finding must quote the exact manuscript text it criticizes, with section name and approximate tex line number.
3. No fabricated facts: I never assert what a cited reference contains beyond what the manuscript itself claims; literature gaps are phrased as candidate gaps only.
4. Numbers: I quote them exactly as in the manuscript; I never compute, alter, or correct numbers (arithmetic-consistency observations allowed only as "state A appears inconsistent with state B as quoted").
5. No network access; I do not attempt to fetch references.
6. I report genuine strengths and weaknesses; no manufactured findings, no finding quotas, no rubber-stamping.
7. My stdout is at most 5 lines; the report goes to the file.

## Overall assessment

**Recommendation signal: Minor (perspective standpoint).**

The paper is unusually candid about its experimental assumptions: the fixed dwell, experimental squint envelope, static targets, single-satellite/single-pass scope, shared resource ceiling, fixed orbit and mode, and hot-start dependence are disclosed rather than hidden. Its main practical contribution is also genuine: the density-regime comparison and the decomposition of geometric coupling, null schedules, and schedule structure give a mission planner a reasoned basis for deciding when additional quality objectives are worth their coverage cost. The manuscript generally distinguishes conditional saturation from mathematical redundancy and treats its fronts as best-known approximations.

Three localized discussion statements nevertheless exceed or blur that otherwise careful framing. The operational guideline combines an unrestricted platform claim with wording that can credit both greedy methods with attaining the coverage reference; the optical-transfer paragraph predicts an untested empirical outcome; and one Pareto-front summary drops the found-front and working-point qualifiers. These issues affect operational interpretation and generalization, not the reported experiments, and appear correctable without new runs.

## Findings

**R3-01** | Severity: MINOR | Location: §7.2 (Operational guidelines), tex lines 1494–1498

Quote: "for dense monitoring campaigns ($N \gtrsim 300$) on any platform, greedy methods (G-SM for radiometric priority, G-BL for coverage priority) attain the tested family's coverage reference and may be preferable."

Issue: "on any platform" extends the recommendation beyond the tested platform and configuration. In addition, the plural subject makes the sentence say that both listed greedy methods attain the coverage reference, whereas the results characterize G-SM's radiometric-priority choice as carrying a coverage cost.

Why it matters: This is the paper's most directly actionable advice. A planner could read it as guaranteeing reference coverage from G-SM, or as establishing dense-regime guidance for untested platforms, neither of which follows from the presented evidence.

Suggested remedy (non-binding): Scope the dense-regime advice to the tested configuration. Separate the two recommendations explicitly: G-BL when attaining the coverage reference is the priority, and G-SM when radiometric quality is prioritized and its coverage cost is acceptable.

**R3-02** | Severity: MINOR | Location: §7.3 (Transferability), tex lines 1515–1521

Quote: "The geometric-resolution objective ($f_2$) carries directly to optical systems, where ground sample distance grows with off-nadir angle (the optical pixel footprint scales as $1/\cos^2\eta$), and the same density-dependent saturation would appear; the radiometric objective ($f_3$, NESZ) does not, because optical radiometry depends on illumination and cloud cover rather than on observation geometry alone."

Issue: The geometric analogy supports considering a corresponding optical objective, but "the same density-dependent saturation would appear" states an empirical cross-sensor outcome that the SAR-only experiments do not test.

Why it matters: Saturation depends on the feasible scheduling landscape and constraints, not solely on the presence of a geometric quality measure. Stating the prediction as a consequence makes the transfer claim stronger than the evidence and could encourage unwarranted reuse of the density thresholds or solver guidance.

Suggested remedy (non-binding): Retain the geometric mapping, but label repetition of density-dependent saturation as a hypothesis for optical scheduling studies. Avoid implying that the tested SAR density regimes or thresholds transfer directly.

**R3-03** | Severity: MINOR | Location: §7.1 (Principal findings), tex lines 1409–1412

Quote: "Taken together, these results establish that the Pareto front, while offering multiple quality-coverage configurations, is compressed by the geometric coupling above: the narrow $f_2$ range limits practical differentiation among front points."

Issue: The unqualified phrase "the Pareto front" reads as a property of the true feasible front and of the front as a whole. Elsewhere, the manuscript more precisely limits this conclusion to the found G-BL-seeded front near the full-coverage working point.

Why it matters: The distinction is central to the paper's cross-disciplinary use of Pareto saturation. Without the qualifiers, an algorithm- and regime-specific observation can be mistaken for global objective redundancy or a general property of the scheduling problem.

Suggested remedy (non-binding): Name the found G-BL-seeded front and the near-full-coverage working point in this summary sentence, preserving the density and initialization qualifications used elsewhere.

## Non-defect observations

- The fixed 30 s dwell is explicitly disclosed, including its removal of dwell–radiometric trade-offs; the conclusions therefore do not silently assume variable-dwell freedom.
- The 45° squint limit is identified as an experimental envelope rather than a universal platform capability, and narrower-envelope sensitivity runs provide a relevant robustness check.
- Energy and memory are modeled as aggregate budgets, while their shared ceiling is acknowledged as a contributor to dense-regime behavior. Static priorities, static known targets, and the absence of an explicit urgency objective are also visible scope choices.
- The limitations section covers the major scope dependencies suggested by the results: single-pass and single-satellite scheduling, Stripmap and fixed-orbit restrictions, scenario-family-specific thresholds, hot-start dependence, and uncertainty for multi-pass or multi-satellite transfer.
- The paper generally uses the coverage–profit framing responsibly by reporting quality gains together with coverage costs and by recognizing that per-task means can conceal coverage collapse. Its distinction between best-known fronts and the unknown true Pareto set is also sound outside R3-03.
