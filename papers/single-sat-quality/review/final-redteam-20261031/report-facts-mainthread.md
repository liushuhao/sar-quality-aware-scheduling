# Paper1 factual-consistency pass — main-thread, 2026-11-01

Target: `papers/single-sat-quality/small-paper-ijae.tex` at HEAD `ec6d607`. Read-only; no source file edited.

## Mechanical re-run at HEAD

| Check | Result |
|---|---|
| `python src/tools/verify_paper_numbers.py` (cwd = repo root) | **204 assertions, 0 failed**; `CALIBER OK: m2/m3 solver code identical to HEAD (ec6d6076); ablation calibers verified` |
| `check_refs.py` | rc 0, all `\ref`/`\citep` targets resolve (`refs-check.log`) |
| EN compile (isolated) | 48 pages, 0 error, 0 undefined, 0 rerun after pass 4 |
| ZH compile (isolated) | 37 pages, 0 error, 0 undefined, 0 rerun after pass 4 |

## Count claims inventory (`facts-count-claims.log`, 56 distinct claims)

All internally consistent:

- `200 scenarios` = `50 scenarios per class` × 4 classes (S1–S4), stated identically at `:42`, `:133`, `:706`, `:855`, `:945`.
- `300 scenarios per variant` = six ablation classes × 50 (`:168`, `:873`).
- `five configurations` consistent everywhere (`:126`, `:586`, `:609`, `:777`, `:794`, `:853`, `:885`, `:1628`).
- `199 of 200` (GA-P-BL ≡ G-BL) stated at `:666`, `:796`, `:992` — the third instance is a different claim (f3 improves in 199/200), not a duplicate-count.
- `47 of 50` at `:1125` and `:1132`; `33 of 50` at `:1149` and `:1239` — repeated consistently.
- Robustness samples `10/4/5/5 scenarios per class × 3 seeds` and `30 runs (15 per class)` agree between body and caveat (`:1314`, `:1341`).

## Text-vs-table arithmetic spot check (Table `tab:solver-profiles`)

| Claim in text | Table values | Recompute | Verdict |
|---|---|---|---|
| MOEA-2 `+33.7%` f2 at S1 (per-scenario ratio), `+33%` pooled | 0.393 vs 0.295 | 0.393/0.295 = **+33.2%** | OK — text distinguishes per-scenario (+33.7) from pooled-mean (+33) calibers |
| MOEA-3 `+40%` f3 at S1 | 0.698 vs 0.497 | **+40.4%** | OK |
| `14%` coverage cost at S1 knee | `f_1* = 0.86` vs 1.00 | **14%** | OK |
| `15%` cost for the +40% f3 point | `f_1* = 0.85` | **15%** | OK |
| high-density marginal gains `<2%` | S4 f3 0.680 vs 0.675; f2 0.338 vs 0.336 | **+0.74%**, **+0.60%** | OK |
| `S4 MOEA-3 f2 10th percentile 0.291 vs G-BL mean 0.336` | S4 G-BL f2 = 0.336 | matches table | OK |

## Bibliography (unchanged at HEAD; these are the only confirmed factual defects)

- `small-paper-ijae.bib:56` `Chen2024LearnConstruct` — pages `5991--6002` should be **5949–5963** (Crossref `10.1109/TSMC.2024.3411640`).
- `small-paper-ijae.bib:215` `Chen2019MILPMulti` — pages `419--434` should be **694–707** (Crossref `10.1016/j.ejor.2018.11.058`).
- `small-paper-ijae.bib:319` `Romano2006` — DOI `10.22237/jmasm/1162356600` resolves 404; public records give a meeting paper, not JMASM 5(2) 423–437. The 0.147 Clifford's-delta threshold attribution is widely used and is not itself challenged; the venue and DOI must be corrected.
- `ChangZhou2025Memetic` (`:129`) is **not** an error: Online first 2024, print issue 2025, vol 346(2), pp. 861–893.

All three defects above were still present when re-checked on 2026-11-01.

## New findings from this pass

None **on the English side**. This pass produced no factual defect beyond the three bibliography entries already recorded.

The Chinese side does carry factual contradictions — four Majors (ablation count 200 vs 300; an invented G-BL placement rule; unreferenced "0.5% invariance" figures refuted by Table 6; a coverage cost attached to the wrong solver). Those are recorded in `report-mirror.md`; the count and arithmetic checks in this file were run on the EN manuscript.

## Coverage limits

- Arithmetic spot checks cover the headline contrasts only; `verify_paper_numbers.py` carries the remaining 204 assertions but was not manually re-derived.
- Figure pixels were not inspected; captions were checked only through the numbers they quote.
- The pass did not re-open the physics claims today's ARS panel already argued (they are recorded in the paper1 panel artifact, not here).
