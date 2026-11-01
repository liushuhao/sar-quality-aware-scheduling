# Paper2 revision log — edits applied to the manuscript, 2026-11-01

Scope: the confirmed defect from `03-hetero-findings-verification.md` plus the text-side resolutions of the panel's must-fix items. Every edit is listed with its carrier; "not done" items say why.

## 1. SLS dwell closure (H1, confirmed defect)

| Carrier | Change |
|---|---|
| `paper/main.tex:143` | Printed hybrid `(R_0+r_0)(\tanθ_s0 − \tanθ_s1)+W_a` replaced by the executable form `R_0[tan(θ_s0+θ_a/2) − tan(θ_s1−θ_a/2)] + W_a`, with `α = θ_a + (R_0θ_a+W_a)/r_0` and `r_0 = R_0θ_a/(λ/(2ρ_req) − θ_a)` stated inline |
| `paper/sections/sec3_problem_formulation.md:27` | same replacement |
| `paper/full.md:147` | same replacement |
| `sss_core/duration.py:297-300` | docstring now describes the executable form |
| `formulas/formula-spec.md` (after Eq.(24) row) | new note: the two Eq.(22) forms must not be mixed; 12°/0.5 m values 50,695.671 m (code) / 50,919.920 m (right-hand form alone) / 55,919.920 m (the hybrid that was printed) |

## 2. Panel must-fix items — text-side resolutions

| Item | Applied | Where |
|---|---|---|
| R1 floor share qualified | ✅ | Abstract: "at most 20.0 and 44.8 … part of that share is the comparability policy of a frozen mode assignment rather than the antenna floor"; §7.1 same qualifier |
| R2 no external denominator | ✅ rescoped | Abstract: "Every magnitude above is internal to this scenario set: no scheduler from the published literature is run on it, so none of these numbers is a cross-scheduler comparison." |
| R3 mode-dependence confound | ✅ restated | Contributions lead + item 2: "family-shape contrast … density and mode composition covary by design … contrasts across family shapes rather than density-controlled effects" |
| R4 anchor qualifier at the headline numbers | ✅ | Abstract after the 4.15/2.36 sentence: "what the anchor construction paid, not a measured gap to an optimum; no non-trivial upper bound … 258 of the 260 units" |
| R5 azimuth-ambiguity asymmetry | ⚠️ claim withdrawn, not re-derived | "a difference of mechanism, not merely of sign" → "a bandwidth-side reading consistent with the registered model rather than a demonstrated difference of mechanism" (§3.3/§7.2 paragraph). The re-derivation with a scene-occupancy term is **not done**. |
| R6 intra-dwell resolution degradation | ❌ not done | Needs the cosine-ratio statistic computed from the dwell-distribution data; no number was invented. |
| R7 violation rate vs zero-squint convention | ✅ | Abstract: "it fails measurably **under the least conservative dwell convention** … a statement about that convention, not about an operator's own dwell planning" |
| R8 served-priority near-inert | ✅ stated | §4 objective statement: "the metric is close to inert … $f_1$ behaves as the served-task fraction" |
| R9 "essentially solved by a single construction pass" | ✅ scoped | §5.5: "within the tested search family and the probe coverage recorded here, a single construction pass reaches the best coverage found in this scenario set" |

## 3. Should-fix items touched

- S3 (table precision): `tab:modes` caption now states that medians are rounded to three decimals and that the text's percentage-point drops come from the unrounded medians.
- S4 ("this revision" deixis): two occurrences replaced with ordinary tense — "(10,000 resamples, computed in this study)"; "rules (ii) and (iii) were added in the reanalysis of 2026-10-24 and are not preregistered arms".
- S9 (closure error unquantified at first mention): already stated in §3.2 ("not separately quantified here"); no change needed.

Remaining S1, S2, S5–S8, S10–S13 were not edited: they are framing/precision suggestions whose resolution needs author decisions (e.g. S2's method framing, S13's reconciliation of two stated positions) rather than a verified defect fix.

## 4. Markdown mirror

`paper/full.md` was synced with every manuscript prose edit above. The `paper/sections/*.md` drafts are stale relative to `main.tex` *before* this revision (different abstract wording, abbreviated refs) and were only updated where the text matched exactly; they are not the manuscript of record.

## 5. Verification after the revision

| Gate | Result |
|---|---|
| Isolated compile (`build-20261101/`) | 46 pages, 0 error, 0 undefined, 0 rerun after pass 4 |
| L8 number ledger (`main.tex` + `full.md`) | 299 checked, 0 mismatch, exit 0 |
| Red lines and writing bans | 1487 files, 0 violation, exit 0 |
| Figure-caption receipts | 70/70, exit 0 |
| Preregistered analysis freeze | 28 checks, 0 failure, exit 0 |
| Manuscript mirror probes | 60/60, exit 0 |
| Layout integrity | 0 FAIL, 5 advisory (unchanged) |
| Claim-level citation traces | 11/11, exit 0 |

`paper/main.pdf` was regenerated from this build. `refs.bib:3` provenance count updated to the actual 36 entries.
