# Re-Review Verification — ARS Panel 2026-08-18 (F1-F8 closure)

**Mode:** academic-paper-reviewer re-review (verification). Reviewer: EIC + editorial synthesizer.
**Manuscripts:** small-paper-ijae.tex (EN, 42 pp) + small-paper-ijae-zh.tex (ZH, 33 pp). Both compile.
**Revisions verified:** 04ad144 (F1-F8) + ab2fad9 (R2 minors + verify hardening + attachment sync).
**Data pre-gate:** verify 167/0 CALIBER OK at ab2fad9 (not re-audited per directive).

## R&R Traceability Matrix

| Item | Verdict | Evidence (current text) |
|------|---------|------------------------|
| **F1** boundary/ceiling → qualified regime | CLOSED | EN L57 "empirical, **conditional** saturation regime for **G-BL-seeded**...under the tested single-pass, single-satellite Stripmap configuration"; L142-143 "convergence is conditional on G-BL hot start...fronts are **best-known** NSGA-III"; contribution L150-158 "under the tested configuration...**indistinguishable from the two-objective one**...under the tested search"; conclusion L1400-1403, L1411. ZH L50, L101, L955, L959 mirror. "coverage reference" replaces "ceiling" (EN L140, L913; ZH L101, L913). No unconditional "boundary/ceiling" survives (grep clean). |
| **F2** §7.2 "0.3 m" numerical error | CLOSED | EN L1303-1305 "+34% f2 gain...roughly a **25% reduction in ground pixel area** (pixel area scales as 1/f2)"; ZH L900 mirrors. Math verified: 1-0.295/0.394 = 0.251 = 25.1%. No "0.3 m"/"5.3 m" residue (grep clean). verify ledger anchors the 25% (op-s1-area-pct) and 0.702. |
| **F3** GA-P-BL relabeled control | CLOSED | EN L128-130 "(GA-P-BL, **a control** that returns the greedy schedule whenever it fails to improve profit, and is therefore numerically identical to G-BL)"; L600 "acts as a control"; "five **configurations**" throughout (L519,542,698,714,751,771,1396); ZH L95, L381, L535, L948 mirror. No "five solvers" as independent-solver claim. |
| **F4** H=13 vs H=91 reference-point confound | CLOSED (control RUN) | EN L997-1000 "Das-Dennis **p=4 (H=15)**...yields f3=**0.702±0.041** (50 scenarios)...statistically indistinguishable from p=12 0.699"; ZH L701. Limitation EN L1381-1383 + ZH L938 updated from "partly entangled" to "matched control confirms...not driven by reference-direction density." Data trace: experiments/results/moea_3obj_p4_control.json = 0.7023±0.0413, exact match; paired p=0.149. +7% survives (MOEA-2 0.654 vs p4 0.702 = +7.3%). |
| **F5** front-point selector specified | CLOSED | EN L733-745 specifies knee = argmax(min-max normalized sum): f1+f2 for MOEA-2, f1+f2+f3 for MOEA-3; sensitivity verified "N≥100 Δ≤0.005; S1 Δ≈0.04-0.06 intentional." ZH L430 mirrors. Matches code src/sar_sim/solver/moea.py L650-670 (verified: knee_idx = argmax(f1_norm+f2_norm[+f3_norm])). |
| **F6** G-SM dense +16% envelope caveat | CLOSED | EN L1312-1314 "under the 45° squint envelope...deliberately exceeds typical operational agility of a few degrees, so the margin...should be re-quantified"; ZH L906 mirrors. |
| **F7** HV demoted to secondary | CLOSED | EN L706-712 "**per-objective comparisons paired with Cliff's δ as the primary**...HV **secondary, cardinality-sensitive**...ranking **inverts** if G-SM included (0.2341 vs 0.0893)"; G-SM HV 0.2341 surfaced at L1019 (main text). ZH L500, L711 mirror. Friedman conservative/NSGA-III-dispersion caveat EN L716-718. |
| **F8** f3 sinθ cross-window caveat | CLOSED | EN L285-291 "ordering defense strongest for **within-window** timing (incidence varies ~1.5°); across targets spanning 18°-47°, suppressed sinθ varies ~2.4×, so f3 read as geometry proxy"; ZH L188 mirrors. Within-window 1.5° independently verified from data (θ_elev range mean 1.48° over 662 S1 windows). |
| **R2-M1** cross-track geometry (5.5°/608 km) | CLOSED | EN L663-665 "cross-track half-width roughly ±608 km, a **ground central angle** of about ±5.5° (NOT off-nadir), corresponding to 47° incidence"; ZH L462. Verified: η_max=41.27°, 693·tan(41.27°)=608 km; 608/111.32=5.46° central angle. Original "±5.5° from nadir" was an off-nadir mislabel. |
| **R2** Moreira2025→2026 citekey | CLOSED | bib year=2026; citekey renamed in EN (2), ZH (2), bib (1). Compiles with bibtex, 0 undefined citations. |
| **minor** pymoo version | CLOSED | EN L703, ZH L496: "pymoo 0.6.1.6"; installed version confirmed 0.6.1.6. |
| **minor** wall-clock order-of-magnitude | CLOSED | EN L698, ZH L488: median 22/66/220/260 s S1-S4. Traced to runner runtime_s: MOEA-2 22/66/220/262, MOEA-3 21/67/217/263 (sleep-inflated >1h filtered). Exact match. |
| **minor** ZH §5.3 per-solver pooling drift | CLOSED | ZH L500-512 now states global single-normalization basis + cardinality caveat, matching code normalize_objectives (global min/max) and EN. The old incorrect "per-solver pooling" text removed. |

## RESIDUAL finding (caught by this re-review)

**RESIDUAL MAJOR (pre-existence, now fixed locally but NOT yet committed): two TAB control-character corruptions in ZH introduced by the revision's heredoc edits.**

- ZH L496: `\texttt{pymoo}` had become `<TAB>exttt{pymoo}` (literal 0x09), rendering as a tab + "exttt" in the compiled PDF.
- ZH L701: `$7\times$` had become `$7<TAB>imes$`, rendering as "7" + tab + "imes" instead of "7×" in the p4 control sentence.

Root cause: Python heredoc string literals interpreted `\t` as a tab (same class as the `\ref`→CR corruption noted in feedback memory). ZH compiled with exit 0 (undefined control sequences swallowed by nonstopmode), so the PDF silently mis-rendered. Both fixed in the working tree (verified `$7\times$` and `\texttt{pymoo}` now present; grep -P "\t" = 0). **These two fixes must be committed before submission; the committed ab2fad9 ZH PDF still contains the corrupt rendering.**

EN is clean (0 TAB chars). No other control-char corruption found.

## New issues introduced by edits
- None beyond the two ZH TAB corruptions above. No broken refs (0 undefined on both), no duplicated sentences, no EN/ZH numeric divergence on the F1-F8 anchors (16-anchor parity check: p4 0.702, 25%, 608 km, 5.5°, 22/66/220/260, 0.2341, pymoo 0.6.1.6, -0.97, etc. all present in both).
- EN L627 "renders the third objective redundant" survives but is a research-question hypothesis ("tests whether..."), not a conclusion claim — acceptable.
- ZH L928 "三目标冗余" is scoped "限于单次过境、单星条带设置" and immediately qualified as empirical not identity — consistent with F1, acceptable.

## Decision

**ACCEPT, conditional on committing the two ZH TAB fixes.** 8/8 F-items verified closed with traceable evidence; R2 minors closed; no CRITICAL, no new MAJOR beyond the two rendering corruptions (which are fixed in the working tree). After committing the ZH fix, the manuscript is ready for submission. No further review round needed.
