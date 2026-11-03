# Paper1 citation-metadata verification — 2026-10-31

## Raw checker result

`python src/tools/check_citation_exists.py --bib papers/single-sat-quality/small-paper-ijae.bib` returned exit 1: 31 entries, 28 found, 1 missing, 2 allowlisted, 3 metadata warnings, 0 lookup errors. The checker's output is `citation-exists.log` in this directory.

## Confirmed metadata corrections

1. **`Chen2024LearnConstruct` page range is wrong.**
   - Bib: pages 5991--6002.
   - Crossref for DOI `10.1109/TSMC.2024.3411640`: volume 54, issue 10, **pages 5949--5963**, published October 2024.
   - Status: CONFIRMED, Minor (bibliographic correctness; no claim change).

2. **`Chen2019MILPMulti` page range is wrong.**
   - Bib: pages 419--434.
   - Crossref for DOI `10.1016/j.ejor.2018.11.058`: volume 275, issue 2, **pages 694--707**, published June 2019.
   - Status: CONFIRMED, Minor.

3. **`Romano2006` is recorded with a journal and DOI that do not resolve.**
   - Bib: *Journal of Modern Applied Statistical Methods* 5(2), pages 423--437, DOI `10.22237/jmasm/1162356600`.
   - DOI resolution: HTTP 404 from `https://doi.org/10.22237/jmasm/1162356600` (`romano-doi.log`).
   - Public records for this title identify the authors and year, but index it as a conference/meeting paper (e.g. the annual meeting of the Florida Association for Institutional Research, 2006); no journal record was found for this title.
   - The 0.147 negative-effect threshold is widely attributed to this work, so the citation's scientific use may be correct; the **bibliographic venue/DOI is not**.
   - Status: CONFIRMED as a bibliography defect, Minor. Recommended action: verify the exact conference/working-paper record or replace it with a source that carries the Cliff's-delta thresholds explicitly. Do not retain the unresolved DOI.

## Checked and not an error

- **`ChangZhou2025Memetic`** — Crossref reports online publication 6 August 2024 and print issue March 2025, volume 346(2), pages 861--893. The bib's `year=2025` is the issue year; not a defect.
- **`Curlander1991`, `Cumming2005`** — already allowlisted as book/legacy references.
- **3 warnings versus 1 missing** — the checker's three metadata warnings are the two page ranges above plus the ChangZhou year; the missing entry is Romano. The three are distinct records, not duplicate reports.

## Minor note

The checker also reports that the bib's own header says “25 cited entries” while the file currently has 31 entries. This is a provenance comment inside the `.bib`, not a manuscript claim; update it for hygiene if the file is distributed.

## Scope

This verification establishes bibliographic metadata only. It does not re-audit the claims supported by these works; the independent and targeted review reports cover claim alignment.
