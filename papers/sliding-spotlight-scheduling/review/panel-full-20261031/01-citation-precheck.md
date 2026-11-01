# Paper2 citation-existence precheck — 2026-10-31

Command: `python -B src/tools/check_citation_exists.py --bib papers/sliding-spotlight-scheduling/paper/refs.bib`

Raw result: exit 1; 36 entries, 33 found, 3 marked MISSING, 5 metadata warnings, 0 lookup errors (`gates/citation-exists.log`). Each item below was checked against public publisher or DOI metadata before being classified.

## The three MISSING marks are not fabricated-reference findings

| Citation | Verification | Adjudication |
|---|---|---|
| `mittermayer2003sliding` | IEEE Xplore document 1294144 confirms the exact title, authors, IGARSS 2003 conference, and DOI `10.1109/IGARSS.2003.1294144`: https://ieeexplore.ieee.org/document/1294144 | Real reference; checker false negative. Adding the DOI would improve traceability. |
| `cumming2005digital` | Artech House lists the book by Ian G. Cumming and Frank H. Wong, ISBN `9781580530583`: https://us.artechhouse.com/Digital-Processing-of-Synthetic-Aperture-Radar-Data-P1549.aspx . MathWorks also lists Artech House, 2005, ISBN `1-58053-058-3`. | Real book; checker false negative. The publisher page says “Copyright: 2004” while other catalogues use 2005; this is not enough evidence to call the manuscript's 2005 publication year wrong. |
| `currie1992wideswath` | IET record gives “Wide-swath SAR”, A. Currie and M. A. Brown, DOI `10.1049/ip-f-2.1992.0016`; search records also confirm volume 139(2), 122–135, 1992: https://digital-library.theiet.org/doi/10.1049/ip-f-2.1992.0016 | Real reference; checker false negative. Adding the DOI would improve traceability. |

## Metadata warnings: two confirmed corrections, three non-errors

### Confirmed

1. **`peng2019agile` — page range is wrong.** The bib prints `193--205`, but Elsevier's publisher page for DOI `10.1016/j.cor.2019.05.030` gives *Computers & Operations Research*, volume 111, November 2019, **pages 84–98**. Source: https://www.sciencedirect.com/science/article/abs/pii/S0305054819301510 . This is a real bibliography correction, not a criticism of the cited claim.
2. **`shen2024multistrip` — current publication metadata needs review.** Crossref for DOI `10.1109/TGRS.2024.3513483` currently reports publication year **2025**, volume **63**, pages **1–13**, whereas the bib has only `year={2024}`. The DOI's 2024 component is not proof of the citation year. This likely reflects early-access versus issue metadata; the current publisher/Crossref record supports updating the bibliography rather than treating the reference as nonexistent.

### Not confirmed as errors

- **`habet2010bounding`:** Springer explicitly gives online publication 15 November 2008 and issue date October 2010, volume 47, pages 307–333. The manuscript's issue-year citation `2010` is correct. Source: https://link.springer.com/article/10.1007/s10589-008-9220-7 .
- **`zhang2018sliding`:** MDPI's publisher record gives *Sensors* 2018, 18(1), article 43, DOI `10.3390/s18010043`. The manuscript's `2018` is correct.
- **`caleiras2026a`:** SciTePress confirms ICORES 2026, pages 110–121, DOI `10.5220/0014407000004055`. The warning is only a short-versus-full proceedings-title difference. Source: https://www.scitepress.org/Link.aspx?doi=10.5220/0014407000004055 .

## Scope

This check establishes reference existence and selected metadata only. It does not prove that every manuscript claim is supported by the cited source; the separate claim-trace gate verified its 11 registered claims, and the fresh panel may assess broader claim–citation alignment.
