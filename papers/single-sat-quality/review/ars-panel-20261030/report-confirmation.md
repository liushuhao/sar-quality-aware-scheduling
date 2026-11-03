# Confirmation round — ars-panel-20261030 fix batch

## Canary
1. Read-only: I must not modify, create, or delete any file except my one report file.
2. Every finding must quote the exact manuscript text it criticizes, with section name and approximate tex line number.
3. No fabricated facts; numbers quoted exactly as in the manuscript.
4. No network access.
5. I report what I find; no manufactured findings, no rubber-stamping. If everything is correctly landed and clean, I say so.
6. My stdout is at most 5 lines; the report goes to the file.

## Part A: fix-landing verdict table

| ID | Verdict | Evidence |
|---|---|---|
| EIC-01 | resolved | Highlights #3 now says "Third objective adds +40\% (NESZ-ordering index) at sparse density, 15\% coverage cost"; the abstract says "+40\% radiometric-index quality" and the Chinese counterpart says "辐射排序指标增益", carrying the ordering-index caliber; the title was intentionally left unchanged. |
| EIC-02 | resolved | §2.3 now states: "These trade-offs have not been made explicit in prior SAR scheduling: the closest approaches embed aggregated quality proxies or composite quality scores within the optimization loop, rather than separate, continuous, physics-derived geometric and radiometric objectives." |
| EIC-03 | resolved | The dense-regime sentence is limited to "differentiation among the tested G-BL-seeded NSGA-III configurations near the full-coverage working point." |
| EIC-04 | resolved | The optical-transfer claim is now explicitly hypothetical: "an analogous density-dependent saturation is a testable expectation for such settings". |
| EIC-05 | resolved | The abstract now supplies the scenario unit — "Across 200 scenarios spanning 20--500 targets per two-orbit scenario" — and the intentionally retained knee-rule wording remains unchanged. |
| R1-01 | landed-incomplete | The patch supplies the intended manuscript clarification: "every solver's persisted frontier points---including the two-objective MOEA-2 fronts and the single-point greedy solutions---carry all three coordinates ($f_3$ is evaluated post hoc for solvers that do not optimize it), so each HV is computed in the same normalized three-objective space"; the wording-only patch contains no verification-gate assertion, so that non-manuscript landing is not evidenced here. |
| R1-02 | landed-incomplete | The requested robustness sentence is present: "restricted to variant A (distribution-only modulation, identical geometry definition across classes), the MOEA-2 $f_2$ gain over G-BL is $+37.2\%$ (S1), $+3.5\%$ (S2), $+0.4\%$ (S3), and $+0.3\%$ (S4), reproducing the saturation on the pure density axis." The associated verify-gate four-assertion landing is outside the supplied patch; the separate coupling-trend residual was not rechecked. |
| R1-03 | resolved | The matched knee-rule definition now specifies "objectives min--max normalized within the front, then the point maximizing the normalized sum ($f_1+f_2+f_3$ for the aware rule, $f_1+f_2$ for the blind rule; $f_3$ is evaluated post hoc on every point of both fronts)---so they differ only in the radiometric term". |
| R1-04 | resolved | The causal claim is narrowed to "is therefore not a hot-start residue", with the residual mechanism explicitly unresolved: "which structural component drives the residual convergence is not resolved by this control." |
| R1-05 | resolved | The statistic is named "the matched-pairs restriction of Cliff's $\delta$ (counting only within-scenario pairs)"; the Chinese figure caption likewise says "Cliff's $\delta$ 的匹配对限制形式", without replacing conventional Cliff's-delta usage elsewhere. |
| R1-06 | resolved | The random-search conclusion now says "the contrast bounds what unstructured selection achieves on these scenarios and does not isolate the source of the MOEA's advantage." |
| R1-07 | resolved | The stochasticity limitation is disclosed: "Each scenario is solved once per stochastic configuration (the scenario seed governs instance generation; the NSGA-III sampling seed is fixed at the library default while operator-level random draws are not pinned), so within-instance search stochasticity is not replicated; the released processed results pin the exact front realizations analyzed." No repeated-run experiment was claimed. |
| R1-08 | resolved | The ablation family is made explicit in the table caption as "the family comprises the 12 variant-by-class comparisons", in the figure caption as "applied within each reported metric", and in the summary as "the 12 being the three non-physics variants by four density classes against A within each reported metric". |
| R1-09 | resolved | The single-solution coverage exceedance is decoupled from the HV mechanism by "The HV comparison of this solution also illustrates the point-count asymmetry"; the numerical result itself is unchanged. |
| R1-10 | resolved | The highest-radiometric claim is now qualified "for the highest $f_3$ among the NSGA-III configurations". |
| R2-01 | resolved | The operational interpretation now says "roughly a $25\%$ smaller per-task geometric area factor" and adds that "the exact schedule-level area change additionally depends on the selected task mix". |
| R2-02 | resolved | Within cluster A, only the result-layer wording was changed: "+34\% geometric-index quality" and "+40\% radiometric-index quality"; the already-qualified §3.2 discussion and the title remain unchanged as adjudicated. |
| R2-03 | resolved | The conclusion restores both qualifications: "The saturation arises under coverage pressure at high density" and "while the within-schedule trade-off persists (negative at every density, \S\ref{sec:pareto-coupling})". |
| R2-04 | landed-incomplete | The requested magnitude label was added — "the Doppler-centroid magnitude $f_{\text{dc}} \approx (2v/\lambda)\sin\psi_{\text{sq}}$" — but the immediately following "(its sign follows the look direction and is outside the model scope)" leaves the signed expression and unsigned magnitude terminology inconsistent. |
| R3-01 | resolved | The recommendation is platform-bounded and splits the two greedy roles: "on the tested platform family, G-BL attains the coverage reference---with the multi-objective variants adding little over it---while G-SM attains the highest radiometric quality at a substantial coverage cost, so the greedy choice follows the mission's priority." |
| R3-02 | resolved | Cluster B is implemented by the revised conditional wording "an analogous density-dependent saturation is a testable expectation for such settings". |
| R3-03 | resolved | The discussion now refers specifically to "the found G-BL-seeded front near the full-coverage working point". |
| DA-01 | resolved | Cluster A is implemented in the highlights and abstract with the index caliber, including "+40\% radiometric-index quality", while the title remains unchanged by design. |
| DA-02 | resolved | The operational statement is restricted to "the tested multi-objective variants provide little additional benefit over the greedy baseline." |
| DA-03 | resolved | "physically forced" was softened to "consistent with coverage pressure locking the selection at high density", while the supported sentence "the search-budget control below confirms that the convergence is not a budget artifact." was retained as required. |
| DA-04 | resolved | The three-seat cluster-B concern is addressed by "an analogous density-dependent saturation is a testable expectation for such settings". |

## Part A summary
resolved 23 / landed-incomplete 3 / not-resolved 0

## Part B: regression findings

**MINOR | §3.3 “Physical modeling scope” / “物理建模范围”, EN approximately lines 522–523 and ZH approximately lines 364–365**

- **Quote (EN):** "the Doppler-centroid magnitude $f_{\text{dc}} \approx (2v/\lambda)\sin\psi_{\text{sq}}$ (its sign follows the look direction and is outside the model scope)"
- **Quote (ZH):** "多普勒质心幅值 $f_{\text{dc}} \approx (2v/\lambda)\sin\psi_{\text{sq}}$（其符号取决于观测方向，不在模型范围内；"
- **Issue:** The edit labels the expression a magnitude but retains a signed sine and immediately discusses its sign. A magnitude should be nonnegative, whereas the displayed expression and the following clause describe a signed Doppler centroid. The same wording appears in both manuscripts, so this is a shared technical-language inconsistency rather than an EN/ZH mirror divergence.
- **Suggested remedy:** Either denote the magnitude with an absolute value, or call the quantity the signed Doppler centroid and reserve “magnitude” for its absolute value; apply the same terminology in both versions.

No other edit-introduced contradiction, grammar/LaTeX defect, changed-point mirror mismatch, or new over-/under-claim was confirmed in the revised regions.

## Verdict
PASS-WITH-FINDINGS
