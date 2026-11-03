# Revision Plan — ARS Panel 2026-08-18 (Minor Revision) — DONE

Decision record of recommended execution path. Full findings: `panel_20260818_editorial_decision.md`.

## Status (all complete)
- [x] **F1** boundary/ceiling → qualified "regime/reference," hot-start+best-known-front conditioning at every claim site (Abstract, §1 contributions, §7, §8); r_null decomposition promoted to co-headline. EN+ZH.
- [x] **F2** §7.2 "0.3 m" numerical error → "+34% f2 ≈ 25% pixel-area reduction (area ∝ 1/f2)." EN+ZH.
- [x] **F3** GA-P-BL relabeled as control (numerically identical to G-BL) throughout; "five solvers" → "five configurations." EN+ZH.
- [x] **F4(a)** matched-reference-point control RUN: MOEA-3 p=4 (H=15) on S1 50 scenarios. f3=0.702±0.041 vs p=12 f3=0.699 (paired p=0.149, indistinguishable). +7% over MOEA-2 survives; not a reference-direction artifact. Written into §6.4 + Limitations. EN+ZH. Artifacts: `experiments/run_moea3_p4_control.py`, `experiments/results/moea_3obj_p4_control.json`.
- [x] **F5** knee selector specified (min-max normalized sum max); selector sensitivity verified from frontier data (N≥100 Δf≤0.005; S1 Δ≈0.04–0.06 intentional). EN+ZH.
- [x] **F6** G-SM dense-regime +16% caveated under 45° envelope (exceeds operational "few degrees"). EN+ZH.
- [x] **F7** HV demoted to secondary/cardinality-sensitive; per-objective + Cliff δ primary; G-SM HV inversion (0.2341 vs 0.0893) surfaced. EN+ZH.
- [x] **F8** f3 sinθ omission: cross-window caveat added (sinθ spans 2.4× across 18°–47°; ordering defense strongest within-window, θ_elev varies ~1.5° — verified empirically). EN+ZH.
- [x] **R3-M5** C3/C4 described as inactive/retained for completeness (already in §3.3; no "four-constraint" overclaim remains).
- [x] minor: pymoo 0.6.1.6 version stated; order-of-magnitude wall-clock (22/66/220/260 s median S1–S4); ZH §5.3 per-solver pooling drift corrected to global normalization (matched code `normalize_objectives`).
- [x] **Compile:** EN pdflatex x2 (42 pp), ZH xelatex x2 (33 pp), 0 undefined refs.
- [x] **verify:** 165 assertions / 0 FAIL / CALIBER OK (3372e2e).

## Deferred (judged unnecessary)
- R3-M2 timeliness softening: Limitations already states timeliness is not an explicit objective and motivation is addressed indirectly via earliest-feasible G-BL. No double-softening needed.
- Bilateral side-flip under C2: the C2 angular-gap formula (arccos of 3D LOS dot product) already penalizes a large opposite-side maneuver; no prose gap.
- p4 numbers added to verify_paper_numbers ledger: numbers trace to JSON and paired p=0.149 confirmed; adding a check is optional hardening, not blocking.
- R2 domain minors (1200 km swath, Sentinel-1 class, Moreira2025 year) not yet actioned — these are R2-only and lower priority; revisit if a second revision round requested.

## Next
Commit (EN/ZH tex+pdf, p4 runner+json, 5 panel reports + editorial decision already on disk). Rebuild snapshot not needed (main data unchanged; p4 is a separate control file). Pre-submission package ready after commit.
