# Paper2 re-review package — 2026-10-31

- Target: `paper/main.tex`, repository HEAD `ec6d607`, source SHA-256 `ad0487f52c5811608ca4fa8a0fbbe796a46f512a74027577ce1273c75821da22`.
- Review mode: one fresh five-seat ARS panel, paper-blind precommitment followed by independent cards, plus one heterogeneous independent review.
- Outcome: **Major Revision** in the simulated panel; 0 Critical, 9 must-fix Major roadmap items, 0 DA Critical. The heterogeneous reviewer found one additional confirmed Major defect in the printed SLS dwell closure that the panel missed. Do not treat the five-seat panel as an independent error process: all five panel seats recorded the same model family.
- No manuscript, source, data, or existing review file was edited.
- **Applied afterwards (2026-11-01, commits `8597573` paper2 / `d6ab424` paper1):** the SLS closure defect and the text-side panel items were fixed and verified — see `04-revision-applied.md` for the change list and the post-fix gate results.

## Read in this order

1. `00-pregate-summary.md` — mechanical gates: 299 numbers, red lines, figure receipts, prereg, mirrors, layout, claims, isolated build.
2. `editorial-decision.md` — formal five-seat decision letter, arithmetic audit, consensus inventory, 9 must-fix + 13 should-fix + 3 optional items. Advisory attachments are appended.
3. `independent-hetero-review.md` — independent alternate-backend report (0 Critical, 1 Major confirmed, 1 Minor).
4. `03-hetero-findings-verification.md` — main-thread reproduction of the hetero Major: printed SLS formula overstates code by **10.3%** at 12°; causal evidence that all results remain code-generated and valid, but the method text is not reproducible as printed.
5. `02-main-verification.md` — main-thread verification of the panel's high-severity claims; distinguishes confirmed claim-scope problems from one PLAUSIBLE physics challenge.
6. `01-citation-precheck.md` — two real bibliography corrections (Peng pages, Shen year) and three false-negative existence checks.

## Supporting artifacts

- `contract.json`, `metadata.json`, `panel-provenance.json`
- `reports/*.phase1.md` and `reports/*.phase2.md`
- `gates/` — all command logs
- `build/` — isolated clean LaTeX build (46 pages)
- `brief-independent-hetero.md` — self-contained red-team brief

## Non-blocking tool notes

- ARS's provenance builder pins the contract by LF-normalized bytes; the installed Windows checkout is CRLF. It was run against a byte-identical LF copy (`full-lf.json`) after a direct raw-byte check. This is a portability defect in the checker, not a manuscript issue.
- `verify_paper_numbers_l8.py` enforces `L8_MIN_CHECKED=155` per invocation; checking `full.md` alone returns exit 2 even with 139/139 matches. The canonical combined `main.tex + full.md` run checks 299 and exits 0.
- The ARS reviewer-claim advisory check was not run because it needs a tool-less judge subagent; this is explicit in the decision letter's advisory attachment.
