# Verification Review Report — Re-Review (Stage 3')

Manuscript: *Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite* (Advances in Space Research)
Round-1 decision: Major Revision (2026-08-15, 5-seat panel)
Re-review date: 2026-08-17

## Judge Record (#539)

- **Verification judge**: Sonnet 4.6 (1M), dispatching an independent EIC verification agent (71 tool calls; direct tex + current-artifact cross-checks).
- **Round-1 panel provenance**: typed artifact missing (`[PANEL-PROVENANCE-ARTIFACT-MISSING]`); six axes `unknown`; five seats role-separated by construction on one model family.
- **Independent cross-model pass**: not_configured.
- **Prompt/rubric surfaces**: `academic-paper-reviewer/references/re_review_mode_protocol.md` (v1.10.0) — Priority-1 traceability rule + new-issue scan.
- **Evidence seen**: revised EN `small-paper-ijae.tex` + ZH `small-paper-ijae-zh.tex`; Round-1 `editorial-decision.md`; `rdr-067-ars-panel-20260815.md`; `verify_paper_numbers_report.json`; direct recomputation against `moea_{2,3}obj/_progress.json` (solver_version 4cfc42c0), `statistical_results.json`, `schedule_correlation.json`, `p1-4_variant_d_rerun/budget_control.json` (git_commit ce8e37fc), `p1-1_random_init/hotstart_control_s1s4.json`, `variant_d_random_init/full.json`, `n50_logistic.json`, `baselines_200.json`, `phenomenon2_cliff.json`.

> This verification round ran on the same model family that drove the revisions; over-optimization to this judge's latent biases is possible (Ren et al. 2026, arXiv:2607.13104 §8.1.2).

## Decision

**Accept** — after the four minor residuals below were corrected in this session. All three Round-1 blocking bundles (B1 prose inversions, B2 unanchored statistics, B3 presentation gaps) are substantively resolved; no Priority-1 item remains open.

## Priority 1 — Must-Fix Items (R1–R18)

| # | Round-1 issue (compact) | Status | Verified | Notes |
|---|---|---|---|---|
| R1 | §6.6 inverted f2 direction ("higher f2 = worse") | FULLY_ADDRESSED | ✅ | EN+ZH; "actually higher — i.e. better geometric quality"; S1–S3 higher, S4 −9% matches hotstart artifact. |
| R2 | §6.4 "attenuation strongest at sparse" inverted | FULLY_ADDRESSED | ✅ | Weakest at S1 (−0.97→−0.63), stronger at S2–S4; matches schedule_correlation.json. |
| R3 | δ=+0.88 basis undocumented; §4.3 conflict | FULLY_ADDRESSED | ✅ | G-SM/G-BL f3 δ=0.99, 199/200, p=1.46e-34; per-class M3-vs-M2 series 0.88/0.56/0.52/0.32 reproduces exactly from 4cfc42c0. |
| R4 | "78%/6%" vs data 80%/10% | FULLY_ADDRESSED | ✅ | Re-review caught a surviving "78%" in the N50 sentence; corrected to 80% (40/50 verified in `moea_2obj/_progress.json`); Table 5 already 80/10. |
| R5 | N50 ≈50 vs ≈45 fork | FULLY_ADDRESSED | ✅ | Both ≈50, CI [30,62]; n50_logistic.json 50.03 [30.18,61.84]. |
| R6 | +10.8% claimed actually +0.89% | FULLY_ADDRESSED (rejection valid) | ✅ | **Author rejection confirmed.** Current `moea_2obj/_progress.json`: one scenario exceeds 1.00 — S1-D_seed04, f1=1.10811 (+10.81%). Panel's 1.0089/+0.89% was S1-D seed08 from the archived 90de261f `_snapshot_final_moea_2obj.json`. "A few"→"One" correct. |
| R7 | Table 6 HV drift | FULLY_ADDRESSED | ✅ | hv_by_solver reproduces: MOEA-3 0.0893, MOEA-2 0.0668, G-BL 0.0234, G-SM 0.2341. |
| R8 | Fisher-z −1.09 vs raw −0.72 | FULLY_ADDRESSED | ✅ | Basis stated (atanh mean over 50 schedules/class); both values + range [−0.97,−0.03] match schedule_correlation.json. |
| R9 | Pareto-sufficiency criterion vacuous | FULLY_ADDRESSED | ✅ | Conjunctive verdict dropped; f1* saturation by G-BL≡1.00 disclosed; per-objective comparisons reported. |
| R10 | Full §6.2–7.2 audit + gate extension | FULLY_ADDRESSED | ✅ | verify gate 165 assertions, 0 FAIL; re-review found one ungated prose line (R4 "78%") now corrected. |
| R11 | +7% f3 lacks test; H-confound | FULLY_ADDRESSED | ✅ | S1 f3 p=5.45e-13, δ=0.88, 47/50; S4 δ=0.32, 33/17, p=0.0045 — all reproduce. Re-review added the missing ZH Limitations mirror of the reference-direction confound sentence. |
| R12 | 45° envelope "conservative" unqualified | FULLY_ADDRESSED | ✅ | Reframed as "idealized capability-superset"; §7.2 conditioned on squint-agile platform. |
| R13 | Budget control promised, unreported | FULLY_ADDRESSED | ✅ | Fresh double-budget rerun (git_commit ce8e37fc, 5 S3 + 5 S4): Δf1* S3 −0.12%, S4 −0.44%; §6.6 "Search-budget control" EN+ZH; gate bud-* assertions pass. |
| R14 | Time-critical motivation never in model | FULLY_ADDRESSED | ✅ | Limitations paragraph + §7.2 latency sentence, EN+ZH. |
| R15 | Random-init hides f1* collapse + n_sel | FULLY_ADDRESSED | ✅ | S3 f1=0.319±0.044, S4 0.522±0.068; n_selected 70.3/117.8; cardinality caveat. |
| R16 | Abstract +41% omits G-SM +45% | FULLY_ADDRESSED | ✅ | Abstract adds G-SM comparator ("matching G-SM's +45% at S1 while retaining roughly twice the coverage"); verified G-SM f3 +45.3%. |
| R17 | Variant C inertness vs incidence mechanism | FULLY_ADDRESSED | ✅ | Window-geometry reconciliation: θ_elev ~1.5° within-window vs ψ 20–35° sweep; ordering-preservation explanation. |
| R18 | ZH mirror | FULLY_ADDRESSED | ✅ | Re-review caught and fixed two ZH gaps: the §6.4 HV/exceedance/frontier paragraph (G-SM HV 0.2341, +10.8%, frontier counts) and the Limitations reference-direction confound sentence. |

## Priority 2 — Should-Fix (S1–S7)

| # | Issue | Status | Notes |
|---|---|---|---|
| S1 | Manifest sync (10-s step, incidence [18°,47°]) | ADDRESSED | §5.1 EN+ZH. |
| S2 | Hot-start per-class Wilcoxon/CI; seed sharing | PARTIALLY_ADDRESSED | Seed-sharing caveat added; no per-class Wilcoxon — acceptable for should-fix given strengthened small-sample caveat. |
| S3 | Friedman G-SM single-point note | ADDRESSED | §7.1 EN+ZH. |
| S4 | θ_elev definition/offset | ADDRESSED | §3.1 EN+ZH. |
| S5 | ψ_max envelope experiment new runs | SKIPPED | Author-explained (new long runs); no adverse finding. |
| S6 | Per-class wall-clock | WAIVED | Prior precedent; §5.2 qualitative runtime retained. |
| S7 | Transferability paragraph | ADDRESSED | New §7.3 EN+ZH. |

Six of seven adopted with content; S5 skipped, S6 waived — above the ≥80% threshold.

## Residuals Found and Corrected This Session

The EIC verification pass returned a provisional **Minor Revision** with four items. All four were corrected before this decision:

1. **EN §6.3** N50 sentence said "($78\%$ and $10\%$)" — current data is 80% (40/50). → 80%.
2. **EN+ZH §6.4** frontier counts "34.3 ± 8.4 / 6.7 ± 2.0" were stale — `_progress.json` gives 33.76±8.44 / 6.78±2.07. → 33.8±8.4 / 6.8±2.1. Gate expected values corrected and S1 tolerance tightened 1.1→0.3 so a 0.5 rounding drift now fails.
3. **§7.1** pooled HV δ printed −0.55 vs `statistical_results.json` pairwise_wilcoxon −0.56. → −0.56 (EN+ZH; gate expected value corrected).
4. **ZH §6.4 / Limitations** two content gaps vs EN (HV/exceedance paragraph; R11 reference-direction confound) — mirrored.

## New Issues Introduced by Revision

None remaining. The four items above were the only defects found in the added/changed passages; no prose-vs-data reversals, no LaTeX errors (EN pdflatex 41p, ZH xelatex 33p, both exit 0), no internal contradictions.

## Evidence Gate (re-run this session)

- `verify_paper_numbers.py`: **165 assertions, 0 FAIL**, CALIBER OK (m2/m3 solver code identical to HEAD 86e71db).
- `pytest` (src/tests + experiments guards): **174 passed**.
- EN pdflatex ×2: exit 0, 41 pages. ZH xelatex ×2: exit 0, 33 pages.
- Solver code unchanged this session (tex + verify-constant edits only); per the rev3 SLIM shortcut, the CODE/DATA audit suite is not re-run (caliber IDENTICAL, verify green, no solver change).

## Decision Rationale

Every Priority-1 item traces to a verified change in the revised manuscript, with headline numbers independently reproduced from current-calibre artifacts (solver_version 4cfc42c0 / git_commit ce8e37fc). The most consequential Round-1 finding (R6, "+0.89% not +10.8%") is itself shown to be a false positive caused by the panel reading an archived stale snapshot (90de261f); the current data supports +10.81%, and the author's rejection is independently confirmed. The four residuals caught at re-review were single-pass editorial corrections (one stale proportion, two rounding/frontier-count values, two ZH mirror gaps), now fixed and re-gated. No core conclusion was invalidated at either round.

**Recommendation: Accept.** Closure is a human editorial decision (M4) — see RDR-067.
