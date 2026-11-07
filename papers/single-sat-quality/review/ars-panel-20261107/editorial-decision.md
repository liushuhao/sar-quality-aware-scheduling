# Editorial Decision — paper1

Journal: Advances in Space Research (simulated).
Manuscript: "Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite: Balancing Profit, NESZ, and Geometric Resolution".
Panel: Journal-Fit (EIC), Methodology (R1), Domain/SAR (R2), Perspective (R3), Devil's Advocate (DA). Five role-separated seats, single execution process — role separation is **not** an independent-error-process claim.
Date: 2026-11-07.

## Pre-review data lock (run before the panel)
| Gate | Result |
|---|---|
| `python src/tools/verify_paper_numbers.py` (repo root) | 272 assertions, **0 failed**; CALIBER OK; census 138 literals watched per language |
| `python experiments/rebuild_snapshot.py` (paper dir) | snapshot rebuilt, **1,800 entries** |
| `python experiments/_audit_full_hard.py --snapshot …` | **1,800 solutions, 0 issues** (1,780 s) |
| `experiments/cross_solver_audit.py` | **ALL CHECKS PASS**, 0 orphan |
| `src/tools/check_refs.py` | all references resolve |
| EN/ZH structural parity | 8 sections / 24 subsections / 6 figures / 5 tables / 6 equations / 94 citations, identical in both |
| `_audit_gapbl_saved` / `audit_moea_live` / `_audit_window_c1_continuous` | running at decision time (see §Open items) |

No data-integrity finding. Every issue below is a framing, reporting, or figure-layer item.

## Decision
**Major Revision.**

Thirty findings from five seats (1 CRITICAL, 10 MAJOR, 18 MINOR, 1 observation; 23 clusters after de-duplication). The evidence base is sound and the manuscript is materially improved since the 2026-11-03 round. The revision is required for three reasons:

1. **A validated DA-CRITICAL blocks acceptance.** The paper's last standing argument for the method over a one-line heuristic — the coverage-stratified frontier — is asserted, not measured (DA-01). The evidence is genuinely two-sided: at S1 and S2 the squint-minimising heuristic is at or above MOEA-3 on both quality axes at lower coverage, while at S1 MOEA-2's f2 (0.393) sits ~1% above G-SM's (0.389), inside one standard deviation. That two-sidedness is the point: the margin the method has over greedy heuristics is small enough that its residual value has to be demonstrated, and the demonstration (a G-BL/G-SM interpolation envelope against the fronts) is missing.
2. **A second new structural finding.** The no-physics null reaches full coverage at S1 (f1* = 1.002 vs 0.850), so the "quantity versus quality trade-off" is at least partly a three-objective selection-pressure artefact (R1-01 / DA-03). The paper admits the anomaly but does not resolve it.
3. **Front matter remains ahead of the body.** The abstract reports the +40%/+34% gains against the coverage-only baseline without the heuristic comparison that §7.2 prints, and reports the +4.9% margin without the +0.05% null (EIC-01, DA-02, DA-05).

Figure defects (Fig. 1 axis mislabel, Fig. 5 legend, Fig. 6 asterisk caption, Fig. 6 sign convention) are individually minor but are all cases where the text was corrected in the previous round and the figure was not — they should be closed in one pass.

## Consensus and disagreement
- **Consensus (all five seats):** the sparse-regime gain is real; the dense-regime vanishing is conditional; the paper's honesty about its own proxy and its own damaging control is a strength.
- **Disagreement:** R2 reads the squint envelope as merely needing a realizability caveat; R3 reads it as narrowing the contribution to a platform class that may not exist; DA reads it as making the headline comparative claim unchanged-but-misattributed. The editorial position is R2's: the caveat is sufficient for the physics, but the front matter must carry it.
- **DA-CRITICAL adjudication:** DA-01 is validated (the manuscript contains no portfolio test and no argument why a mixture would fail) and is therefore not rejected; it blocks Accept and becomes roadmap item N2.

## Carry-over from the 2026-11-03 round (verification, not re-litigation)
| Prior item | Landed? | Evidence |
|---|---|---|
| R1 (highlights: split physical gain vs third-objective margin) | partial (text) | `highlights.tex` bullet 3 now separates the two numbers ("Re-optimisation gains +40% radiometric over greedy (15% cost); third objective +4.9%") but still omits the +0.05% null and the heuristic comparison |
| R2 (density boundary conditional on hot start) | yes | abstract l.50-53, §7.1 finding (5) |
| R3 (simulation provenance in front matter) | yes | abstract l.42 |
| R4 (third objective's value flows through squint) | yes | ablation l.128-137, contribution (iv) |
| R5 (cheap physics control **or** narrowed statement) | narrowed statement only | §7.2 l.1471-1479; no retiming control exists in the manuscript or in `experiments/` |
| R6 (resource-cap reporting) | partial | bound/unbound split in §3.3; N50 still fit on the pooled mix (N5 below) |
| R7 (reproducibility wording) | partial | §5.4 explicit; Data Availability still says "fixed seeds" (N6) |
| R8 (dropped-target composition) | yes | §3.2 l.377-385 ("0.92 dropped vs 0.80 retained") |
| R9 (correlation pair fixed to full physics) | yes | Fig. 5 caption l.1216-1227 |
| R10 (PRF / yaw-steering physics) | yes | §3.3 l.540-568 |
| R11–R14 (terms, consistency, stats, abstract) | partial | text fixed; **figures not** — Fig. 1 axis (N7), Fig. 5 legend (N8) |

## Roadmap (cost-ordered; N-items are this round's)
| # | Item | Severity | Cost | Anchor |
|---|---|---|---|---|
| N1 | Abstract + highlights: name the squint-minimising heuristic beside the +40%/+34%; add the +0.05% null beside +4.9% | CRITICAL (framing) | sentence ×3 | l.44-48; `highlights.tex` bullets 2-3 |
| N2 | Portfolio control: G-BL/G-SM mixture envelope vs the MOEA fronts on the same three coordinates | CRITICAL | experiment (no new solver) | Table 3, Fig. 4 |
| N3 | Diagnostic arm: three objectives with no quality content (f3 replaced by a copy of f1) to separate trade-off from selection pressure | MAJOR | experiment (~50 S1 runs) | ablation Table 6 |
| N4 | Realizability caveat appended to the §7.2 operational guideline | MAJOR | sentence | l.1501-1505 |
| N5 | Refit N50 on C2-limited scenarios only; carry the CI into the abstract | MAJOR | analysis + sentence | l.1107-1114 |
| N6 | Data Availability wording: fixed scenario seeds vs unpinned process draws | MAJOR | sentence | l.1649-1651 |
| N7 | Fig. 1 axis label: "Cliff's δ" is δ_pairs; restyle the Romano band as reference-only | MAJOR | figure regeneration | `experiments/gen_all_figures.py:502`; fig1_hypervolume.pdf |
| N8 | Fig. 5 legend: labels a 20-draw percentile band "shuffle 95%", which §6.4 itself says is not a nominal 95% interval | MINOR | figure regeneration | `scripts/gen_fig7_fig8.py:93` |
| N9 | Fig. 6 caption: asterisks mark f1* only (matches `gen_fig6_ablation.py:187`) | MINOR | caption | ablation l.110 |
| N10 | One sign convention across Fig. 6, Table 6 and §6.5 prose | MINOR | caption + sentence | ablation l.44-47 |
| N11 | External anchor: exact optimum coverage at N=20 (or one published heuristic) | MAJOR | experiment | §4.1, §7.4 |
| N12 | Translate f2/f3 into metres in §7.2 | MINOR | sentence | l.1459-1463 |
| N13 | Timeliness: measure knee-point acquisition delay, or soften the recommendation | MINOR | analysis/sentence | l.1518-1523 |
| N14 | Title/keyword NESZ qualifier (still pending-user from 2026-11-03) | MAJOR | title + keywords | l.24, l.67 |
| N15 | Abstract split; Fig. 1 panel order; contribution bullet (iii) split | MINOR | sentences | l.35-65, l.179-184 |
| N16 | θ_elev vs target-side incidence: quote the degrees | MINOR | sentence | l.356-361 |
| N17 | Priority-skew and horizon-length scope notes | MINOR | sentences | l.799, l.86-88 |
| N18 | Budget control: run at S1 or drop it | MINOR | experiment/sentence | l.1361-1368 |
| N19 | Transferability: cite the optical 1/cos²η relation | MINOR | sentence | l.1531-1535 |

Execution notes:
- N1, N4, N6, N9, N10, N12, N13, N16, N17, N19 are text-only and bilingual (EN + ZH).
- N7, N8, N9 require figure regeneration; the regeneration already exists and is reproducible (`gen_fig6_ablation.py`, `gen_all_figures.py`), so this is a label change plus a rerun, not a new analysis.
- N2, N3, N11 add analysis on existing scenario data where possible; N3 needs new solver runs.
- Any change to a printed number triggers `verify_paper_numbers.py --update-census` plus census-diff review, per the project's symptom-fix gate.

## Pre-review data lock — completed
All seven gates finished green after this decision was drafted:
- `audit_gapbl_saved` → 0 issues (S1-S4, 0.0 worst deviation)
- `audit_moea_live` → EXIT=0 (live re-run matches the saved record: e.g. S4-A_seed00 rerun f1=1.0000 f2=0.3873 f3=0.6563 vs saved 0.38703/0.65536, 0 constraint violations)
- `_audit_window_c1_continuous` → 76,190 windows, 0 C1-violating segments, 0 unhostable after tail-trim

## Open items at decision time
- Data Availability URL (l.1652, `https://github.com/liushuhao/sar-quality-aware-scheduling`) could not be checked from this environment (network blocked). The author should confirm it resolves publicly before resubmission; an unresolvable URL is a factual defect, not a style one.
