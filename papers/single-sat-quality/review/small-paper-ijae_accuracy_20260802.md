# Accuracy & Matching Verification Report — Pass 3

**Paper:** small-paper-ijae.tex (EN) + small-paper-ijae-zh.tex (ZH)
**Date:** 2026-08-02
**Method:** all numbers recomputed from committed per-run artifacts
(baselines_200.json, baselines_S7S8.json, {moea_3obj,moea_3obj_no_squint,
moea_3obj_no_incidence,moea_3obj_no_physics,moea_2obj}/_progress.json,
statistical_results.json, effect_sizes.json); citation set diff vs .bib;
abstract/conclusion claims traced to source sections.

## 1. Data verification — GREEN (with one convention issue)

| Claim / table | Source | Result |
|---|---|---|
| Table 3, 20 means (f1*/f2/f3 × 5 solvers × 4 classes) | per-run recompute | **20/20 match** |
| Table 3, 60 SD cells | per-run recompute | 29/60 differ — **all exactly ×sqrt(49/50)**: table is ddof=0; text/HV table/stats JSON are ddof=1 (= NC-1 in logic report) |
| HV table (tab:hv) MOEA-3 0.173±0.045 / MOEA-2 0.169±0.037 / G-BL 0.140±0.017 | per_scenario_hv pooled 200 | **match (ddof=1)** |
| Friedman χ²=506.56, p≈10⁻¹⁰⁸ | statistical_results.json | 506.56, 2.55e-108 ✓ |
| MOEA-2 vs MOEA-3 HV: p=1.4×10⁻⁴, δ=−0.23 | pairwise_wilcoxon | p=1.37e-4, δ=−0.23 ✓ |
| Cliff's δ: MOEA-2 f2 vs G-BL +0.55 (p<10⁻³³); G-SM f3 +0.72 (p=1.7e-34); G-SM f1* −0.25 (p=7.0e-34); M2/M3 f2 +0.132 (p=3.9e-10), f3 −0.176 (p=5.6e-14) | effect_sizes.json | **all match** (0.545→0.55, 1.436e-34→p<10⁻³³) |
| Deficit proportions f1*<0.95: 88/62/16/24% (S1–S4) | per-scenario normalized f1* | **exact match**; χ²(1)=1.00/p=0.32 for 16→24 consistent |
| S7/S8: f1* 0.94±0.06 / 0.96±0.04; f2 gain +0.4% / +0.2%; deficit 42% / 30% | baselines_S7S8 + moea_2obj | **exact match** |
| Ablation Δ%: S1 −9.5/+21.6/−22.1; S2 −0.3/+3.2/−1.2; S3 −0.9/−0.4/−0.2; S4 −0.1/−0.6/−0.2 | per-scenario normalized f1*, group means | **12/12 exact** |
| Ablation means (f1*, f2, f3, f1/n, n_sel) | recompute | match at display precision |
| Ablation SD columns | recompute | n_sel column = ddof0 throughout; f1* SD mixed/last-digit (same hygiene issue as NC-1; no prose quotes these SDs, so no visible contradiction) |
| Envelope r=−0.95, null −0.51, r_MC −0.5120; schedule A −0.69→−0.17, D −0.44→−0.18 | prior-round probe scripts (r_visible_envelope.json, reproduce_A_r.py, reproduce_variant_d_r.py) + v7 central-claim recomputation C-D01…C-D11 | consistent (not recomputed this round; inherited) |
| N50≈140 [117,169]; prior [111,227] | n50_logistic.json (N150/N200 round) | consistent (inherited) |
| Physics spot-checks: ρ_rg(30°)=5.3 m; cos³(10°)=0.955; Das-Dennis H(2,12)=13, H(3,12)=91; GA-P-BL f1* range 1.09–1.28 | closed-form / Table 3 | ✓ |

## 2. Citations — CLEAN

- EN 25 cited keys = ZH 25 cited keys = 25 bib entries. 0 missing, 0 uncited,
  0 version-divergent keys; 40 citation calls each.
- arXiv IDs in bib: 2601.11967 (Caleiras, title verified in D02 round) and
  2604.19539 (QualityScreening, title corrected in D02 round) — both as fixed.
- Claim-citation bindings spot-checked (Peng2019 NP-hard reduction; Deb2014
  NSGA-III; Curlander/Cumming/Moreira SAR physics; Chang2022 closest-prior
  positioning; Wu2026 COI note) — all attached to the correct claims.

## 3. Abstract & Conclusion matching — GREEN

Every quantitative abstract claim traced: +8.2% (S1 f2) ✓; "roughly one third
of f1*" (0.32 deficit) ✓; <2% at N≥300 (1.6/1.5%) ✓; random-init deficits
0.20–0.46 ✓; MOEA-3 ≈ MOEA-2 ✓; ablation "barely changes dense-regime" (≤1%) ✓;
scope qualifiers (single-pass/single-satellite/Stripmap/G-BL-seeded) identical
in abstract, contribution 1, §7.3, conclusion ✓. Conclusion findings ⊆
Discussion findings ⊆ Results ✓.

## 4. NEW factual error — ZH-only zero-Doppler-crossing fraction (UC-1 escalated)

ZH §5.1 (L458–460) claims: "约 50%–60% 的可见窗口包含零多普勒穿越……所有场景
类别中保持在 40% 以上". Measured over **all 200 scenarios / 45,345 windows**
(scripts geometry, 10 s grid, crossing = grid min |ψ_sq| ≤ 0.5°; ≤1° gives the
same fractions):

| Class | Windows | Crossing fraction |
|---|---|---|
| S1 | 9,97 | **15.1%** |
| S2 | 4,454 | **17.2%** |
| S3 | 15,000 | **14.9%** |
| S4 | 24,894 | **14.9%** |

Median per-window minimum |ψ_sq| ≈ 27–30° — most windows never approach zero
squint. The claim is wrong by a factor of ~3–4 and the "≥40% in all classes"
statement is false. Consistent with G-SM achieving only partial squint
reduction on average. **Escalated to must-fix (ZH).** EN has no such claim.
Fix: rewrite ZH to the measured ~15–17% (or delete the quantification); the
"|ψ_sq| ≤ 0.5°" discretization sentence in ZH §4.3 remains correct for the
minority of windows that do cross.

## 5. Known issues carried into the fix batch

From the logic report (small-paper-ijae_logic.md): AC-1 (ρ_rg contradiction),
AC-2/M3 (§6.4 duplicate paragraphs), AC-3 (§7.1 double findings), AC-4
(contribution attribution), NC-1 (ddof convention), M1 (§6.6 italic
takeaways), M2 (ablation "warrants closer examination"); plus UC-1 escalated
above. De-AI optional tier (O1–O5) deferred per author decision.

---

*Pass 3 of the 2026-08-02 re-review (logic → de-AI → accuracy).*
