# R2 (Domain/SAR) report — ars-panel-20261030

## Canary

1. Read-only: I must not modify, create, or delete any file except my one report file.
2. Every finding must quote the exact manuscript text it criticizes, with section name and approximate tex line number.
3. No fabricated facts: I never assert what a cited reference contains beyond what the manuscript itself claims; literature gaps are phrased as candidate gaps only.
4. Numbers: I quote them exactly as in the manuscript; I never compute, alter, or correct numbers (arithmetic-consistency observations allowed only as "state A appears inconsistent with state B as quoted").
5. No network access; I do not attempt to fetch references.
6. I report genuine strengths and weaknesses; no manufactured findings, no finding quotas, no rubber-stamping.
7. My stdout is at most 5 lines; the report goes to the file.

## Overall assessment

**Recommendation signal: Major** from the domain standpoint.

The manuscript presents a generally coherent Stripmap geometry model, gives explicit directions of improvement for both quality indices, and is commendably clear that its radiometric objective is a proxy rather than an absolute NESZ prediction. The Earth-curvature-corrected incidence relation, the separation of cross-track and squint effects, and the distinction between found-front compression and the full feasible trade-off surface are useful strengths. The fixed orbit, two-orbit horizon, and visibility-window construction are also adequately scoped as simulation assumptions rather than claims about a specific operational mission.

Two issues nevertheless affect the physical interpretation of the main objectives. First, the geometric index mixes an ordering-consistent elevation-plane angle with a target-side ground-pixel-area formula, and its schedule-level mean is later converted directly into a quantitative pixel-area reduction. Second, the within-window justification for the NESZ proxy does not establish the cross-window radiometric ordering on which scheduling and aggregate comparisons rely. These points require clarification or additional validation before the quality improvements can carry their stated SAR-operational meaning. The remaining findings concern narrower consistency and terminology issues.

## Findings

**R2-01** | Severity: MAJOR | Location: §3.2, Objective 2 (tex lines 390–402), and §7.2, Operational Implications (tex lines 1451–1459)

Quote: "The ground pixel area of a SAR image is the product of ground-range resolution $\rho_{\text{rg}} = c / (2B \sin\theta)$ and azimuth resolution $\rho_{\text{az}} = D / (2 \cos\psi_{\text{sq}})$."

Quote: "$f_2 = \frac{1}{|\mathcal{S}|} \sum_{i \in \mathcal{S}} \sin\theta_{\text{elev},i} \cdot \cos\psi_{\text{sq},i}$"

Quote: "knee-point $+33.7\%$ $f_2$ gain at S1 corresponds to roughly a $25\%$ reduction in ground pixel area (pixel area scales as $1/f_2$ for the geometric index of Eq.~\ref{eq:f2})"

Issue: The pixel-area expression uses the target-side incidence angle $\theta$, whereas $f_2$ substitutes the satellite-centered elevation-plane angle $\theta_{\text{elev}}$. The manuscript defends the latter as ordering-consistent, not as quantitatively identical to $\theta$. In addition, $f_2$ is an unweighted mean of per-task inverse-area factors; the reciprocal of that mean is not generally the mean ground pixel area of the scheduled tasks. Thus the stated schedule-level conversion from a change in mean $f_2$ to a ground-pixel-area reduction requires assumptions that are not supplied.

Why it matters: This conversion gives the geometric objective a quantitative operational interpretation and informs the mission-specific recommendation. An ordering proxy can support relative selection without supporting a physical area-reduction claim.

Suggested remedy (non-binding): Either define the geometric objective from the same physically consistent per-task area expression used in its interpretation, or retain $f_2$ explicitly as an ordering index and remove the direct area conversion. If area reduction is operationally important, report an explicitly defined aggregate of the actual per-task ground pixel areas separately.

**R2-02** | Severity: MAJOR | Location: §3.2, Objective 3 (tex lines 428–436), and §3.3, Physical Scope (tex lines 525–529)

Quote: "This ordering defense is strongest for within-window timing selection, where incidence varies by only a few degrees"

Quote: "across targets or windows that span the full $18^\circ$--$47^\circ$ incidence range, the suppressed $\sin\theta$ factor varies by roughly $2.4\times$, so $f_3$ should be read as a geometry proxy rather than an absolute NESZ ranking across widely separated incidence angles."

Quote: "This idealization preserves the relative ordering of acquisition geometries \emph{within} the simulated platform family, which is what the solver comparisons act on"

Issue: The physical justification is strongest for within-window timing selection, but the scheduler also optimizes and compares $f_3$ across tasks, windows, and aggregate schedules spanning much wider geometry differences. The later broad statement about preserved ordering does not distinguish ordering of the geometric proxy from radiometric ordering under the suppressed factors. Consequently, the scope in which higher $f_3$ should be interpreted as better NESZ-related quality remains ambiguous precisely over the decision space used by the optimizer.

Why it matters: Sparse-regime gains attributed to radiometric quality depend on cross-window selection, not only on choosing a time within one window. If cross-window NESZ ordering is not established, those gains are securely interpretable as changes in a geometric surrogate, but not necessarily as equivalent radiometric improvements.

Suggested remedy (non-binding): Separate the two claims explicitly: exact ordering of the defined geometric surrogate versus approximate ordering of physical NESZ. Either validate the latter over the feasible cross-window incidence/squint domain with the retained physical factors, or consistently describe cross-window and aggregate results as surrogate-geometry improvements and avoid quantitative radiometric interpretations there.

**R2-03** | Severity: MINOR | Location: §6.4, Pareto-Front Coupling (tex lines 1058–1066 and 1119–1122), and §8, Conclusion (tex lines 1599–1601)

Quote: "This compression is a property of the found front under G-BL-seeded search rather than of the full feasible trade-off surface: the squint-minimizing heuristic G-SM reaches feasible high-$f_3$ operating points"

Quote: "differentiation regardless of solver strategy."

Quote: "selection, not because the underlying $f_2$--$f_3$ trade-off vanishes. The within-schedule correlation remains negative at every density."

Quote: "The saturation arises from solver convergence to lower-squint regimes under which the geometric coupling aligns $f_2$ and $f_3$ along the shared $\cos\psi_{\text{sq}}$ factor"

Issue: "Regardless of solver strategy" is broader than the manuscript's own G-SM counterexample at S4, and the conclusion presents lower-squint geometric alignment as the cause of saturation without retaining the results section's emphasis on coverage pressure and the persistence of the underlying trade-off. The abbreviated conclusion can therefore read as a stronger and different mechanism from the one established in §6.4.

Why it matters: The distinction determines whether dense-regime indistinguishability is a limitation of particular seeded searches near high coverage, a consequence of schedule saturation, or a disappearance of the physical objective conflict. These have different implications for solver design and for transfer to other operating regimes.

Suggested remedy (non-binding): Qualify the universality statement to the tested G-BL-seeded NSGA-III configurations and high-coverage operating region. In the conclusion, retain coverage pressure as the saturation mechanism and describe low-squint coupling as the geometric contribution to front compression, while explicitly noting that the feasible trade-off and negative within-schedule correlation persist.

**R2-04** | Severity: MINOR | Location: §2.2, Observation Geometry (tex lines 344–348), and §3.3, Physical Scope (tex lines 519–522)

Quote: "squint angle $\psi_{\text{sq}} = \arcsin(|l_x| / R)$"

Quote: "not modeled: the Doppler centroid $f_{\text{dc}} \approx (2v/\lambda)\sin\psi_{\text{sq}}$"

Issue: The defined squint angle is nonnegative because it uses $|l_x|$, whereas the displayed Doppler-centroid expression has the form of a signed quantity. As written, the two definitions do not express opposite Doppler signs for fore- and aft-looking views with the same unsigned squint magnitude.

Why it matters: This does not affect the objective values, which depend on squint magnitude, but it weakens terminology and sign discipline in the paragraph defining the unmodeled radar effects.

Suggested remedy (non-binding): Define a signed along-track angle for the Doppler expression, or label the expression explicitly as a Doppler-centroid magnitude and state that its sign is outside the model scope.

## Non-defect observations

- The manuscript explicitly distinguishes the target-side incidence angle from the satellite-centered elevation-plane angle and discloses their Earth-curvature-related difference; the concern in R2-01 is the later quantitative interpretation, not concealment of that distinction.
- The NESZ discussion discloses omitted Earth-curvature, antenna-pattern, and reference-area effects rather than presenting the proxy as an absolute radiometric model.
- The direction of improvement is clear for both quality objectives, and the discussion correctly distinguishes shared-squint coupling from mathematical redundancy of the objectives.
- The explicit definition of "single-pass" as one satellite over the stated two-orbit scheduling horizon avoids leaving that potentially ambiguous term implicit.
- The generic orbital platform, restricted incidence range, fixed observation duration, and short scheduling horizon are presented as simulation assumptions; no domain-critical orbit-realism defect was identified under those stated assumptions.
