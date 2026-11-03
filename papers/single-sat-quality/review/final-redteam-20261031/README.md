# Paper1 final targeted re-review — 2026-10-31 / completed 2026-11-01

## Scope

This is not a repeat of today's full ARS panel. It is a fresh targeted red-team of the final manuscript: internal factual consistency, citation-claim alignment, EN/ZH mirror integrity, and final PDF/submission surface. Read-only: no `.tex`, `.bib`, PDF, or data file was modified.

## Mechanical prechecks

| Check | Result | Evidence |
|---|---|---|
| `verify_paper_numbers.py` (re-run 2026-11-01) | 204 assertions, 0 failed; CALIBER OK; HEAD `ec6d607` | `papers/single-sat-quality/review/verify_paper_numbers_report.json` |
| Isolated EN compile | 48 pages; 0 error, 0 undefined, 0 rerun warning | `build-en/` + `build-en-pass4.log` |
| Isolated ZH compile | 37 pages (pre-fix state; 38 after the fixes below); 0 error, 0 undefined, 0 rerun warning | `build-zh/` + `build-zh-pass4.log` |
| Delivered PDF vs isolated build | EN text SHA equal, ZH text SHA equal, same page counts | terminal check in session |
| Internal refs | `check_refs.py` rc 0, all references resolve | `refs-check.log` |
| Bibliography existence | 28 found, 3 real metadata defects, 1 false-negative book allowlisted | `citation-exists.log`, `citation-metadata-verification.md` |

## Bibliography corrections — found at review time, fixed in commit `d6ab424`

- `Chen2024LearnConstruct` (`small-paper-ijae.bib:56`): pages should be **5949–5963**, not 5991–6002 (Crossref DOI `10.1109/TSMC.2024.3411640`).
- `Chen2019MILPMulti` (`small-paper-ijae.bib:215`): pages should be **694–707**, not 419–434 (Crossref DOI `10.1016/j.ejor.2018.11.058`).
- `Romano2006` (`small-paper-ijae.bib:319`): DOI `10.22237/jmasm/1162356600` returns 404; public records identify it as a meeting paper, not the journal venue printed in the bib. The 0.147 threshold attribution is widely used, but venue/DOI must be corrected.
- `ChangZhou2025Memetic` is not an error: Crossref gives online 2024 / print issue 2025, volume 346(2), pp. 861–893.

## Findings this pass added

| ID | Severity | Finding |
|---|---|---|
| ZM-1 | **major** | ZH `:581` says each ablation variant ran on **200** scenarios; EN, the ZH contribution list and both ablation sections say **300** (6 classes × 50). Internal contradiction in the Chinese version. |
| ZM-2 | **major** | ZH `:441` gives G-BL a "fixed-nadir at the pre-stored off-nadir angle of maximum elevation" placement rule that EN does not have, and that contradicts the ZH sentences immediately before and after it. |
| ZM-3 | **major** | ZH `:974` states variants converge "within 1% (f1*) / 0.5% (f2, f3, n_sel)"; EN states no percentages, the ablation text says 0.2% / 0.6%, and Table 6 shows f3 deviations of −0.80% and −1.12%. |
| ZM-4 | **major** | ZH conclusion `:1058` attaches the 14–15% coverage cost to MOEA-2's f2 gain only, leaving MOEA-3's +40% f3 gain uncosted; EN applies the range to both. |
| ZM-5 | major-adjacent | EN "coverage **cost** … is a sparse-density phenomenon" rendered as ZH "覆盖**优势**" (advantage). |
| Zm-1…14 | minor | Wrong cross-ref for the +0.99 effect; omitted GA-P-BL guard paragraph (13.5% absent from ZH); "always triggers" mistranslation; knee paragraph in a different section; two dropped scope/limitation sentences; caption qualifiers dropped; asymmetric additions on both sides. Full table in `report-mirror.md`. |
| MM-1/MM-2 | minor | Superseded by Zm-2/Zm-4 above and recorded inside `report-mirror.md`. |

The English manuscript itself has no new content defect; its mirror does.

## Reports

- `report-mirror.md` — consolidated EN/ZH mirror report: 4 Major + 5 minor + 14 minor, every item re-verified by the main thread against the files.
- `report-facts-mainthread.md` — factual consistency, count claims, table arithmetic, bibliography status (EN side).
- Supporting scripts and logs: `mirror_numeric_check`, `mirror_multiset_check`, `mirror_section_check`, `mirror_locate_check`, `facts_count_claims` + matching `*.log`.

## Fixes applied (2026-11-01)

All four Major items, the wording inversion, and eleven of the minor items were fixed in the Chinese manuscript; three bibliography entries were corrected in the shared `.bib`; one English sentence was deleted at the author's request (it read as defensive and duplicated the conditional statement immediately before it).

| Item | Change |
|---|---|
| ZM-1 | ZH `:581` ablation count 200 → "六个场景类别（共 300 个场景）" |
| ZM-2 | ZH `:441` invented fixed-nadir sentence → the EN meaning ("earliest-time placement fixes geometry implicitly through the incidence–squint profile") |
| ZM-3 | ZH `:974` invented "1% / 0.5% (f2, f3, n_sel)" → the EN claim with no percentages |
| ZM-4 | ZH conclusion: the 14–15% cost now applies to both solvers ("两者的代价为 14–15% 的覆盖率") |
| ZM-5 | ZH "覆盖优势" → "覆盖代价" |
| Zm-1…Zm-14 | wrong `+0.99` cross-ref → §6.2; GA-P-BL guard paragraph added to ZH §4.4 (bringing `13.5%` into the ZH text); "总是触发" → "仅作用于单一利润目标"; knee-selector paragraph moved from ZH §4 to §5.2; scope limit and ZH-only normative recommendation aligned to EN; normalization rationale added; `ξ` / `sinθ_elev` naming mirrored; two ablation caption qualifiers restored; header sync date updated |
| Bib | `Chen2024LearnConstruct` pages → 5949–5963; `Chen2019MILPMulti` pages → 694–707; `Romano2006` → conference form, unverifiable journal/volume/pages/DOI removed; header entry count 25 → 31 |
| EN | defensive "whether the MOEA can independently discover high-coverage solutions … remains an open question" deleted from §7 |

Verification after the fixes: EN 48 pages, ZH 38 pages, both 0 error / 0 undefined reference / 0 rerun; `verify_paper_numbers.py` 204 assertions, 0 failed; `check_refs.py` all references resolve; 19/19 targeted fix assertions pass (`verify-fixes.log`).

## Reviewer provenance note

Two mirror reviewers ran this dimension and were blocked by the harness from writing report files ("Subagents should return findings as text, not write report files"); their findings arrived as messages and were re-verified here before being recorded. The reviewers' original line references matched the files in every case checked.

## Tooling note worth keeping

The first mirror script (`mirror_numeric_check`) stripped comments with `re.sub(r"%.*$", ...)`, which also deletes everything after every `\%`. Its "first divergence" line (`+34` absent from ZH) was that bug, not a real omission. Numeric mirror checks must strip only unescaped `%` (`(?<!\\)%.*$`).

## Status

Closed, and the fixes are committed. Findings raised: **4 Major + 1 major-adjacent + ~19 minor, all on the Chinese side**, plus **3 bibliography metadata errors**. All of them were fixed in `d6ab424` (see "Fixes applied" above); what remains open is only the asymmetry noted there (Chinese-only explanatory additions that were not carried back into the English version). Nothing here re-opened the physics or the results.
