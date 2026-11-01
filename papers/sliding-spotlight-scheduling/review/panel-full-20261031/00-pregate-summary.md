# Paper2 pre-review verification — 2026-10-31

Review target: `paper/main.tex` at current HEAD (`2e842c9` manuscript change), with no manuscript edits by this review.

All commands ran from the repository root. Logs are under `gates/`; the clean build is under `build/`.

| Check | Result | Exit | Evidence |
|---|---:|---:|---|
| L8 manuscript numbers, `main.tex` + `full.md` | 299 checked, 0 mismatch | 0 | `gates/l8-combined.log` |
| Frozen red lines and writing bans | 1437 files, 0 violation | 0 | `gates/red-lines.log` |
| Figure-caption receipts | 70/70 numbers traced | 0 | `gates/figure-receipts.log` |
| Preregistered analysis freeze | 28 checks, 0 failure | 0 | `gates/prereg.log` |
| Manuscript mirror probes | 60/60 probe-face checks | 0 | `gates/mirrors.log` |
| Layout integrity | 0 FAIL, 0 WARN, 5 advisory | 0 | `gates/layout.log` |
| Claim-level citation traces | 11/11 verified | 0 | `gates/claim-traces.log` |
| Isolated clean compile | 46 pages; pass 4 has 0 error, 0 undefined reference/citation, 0 rerun warning | 0 | `gates/compile-pass4.log`, `build/main.log` |

## Invocation note

Running the L8 checker on `full.md` alone returned exit 2 despite 139/139 numbers matching: its global `L8_MIN_CHECKED=155` silent-drop guard applies to the whole invocation. The canonical combined run (`main.tex` and `full.md` together) checked 299 numbers and exited 0. The standalone log is retained as `gates/l8-full.log`; it is an invocation-surface guard, not a manuscript-number mismatch.

## Advisory-only items

`check_layout_gotchas.py` prints C5, NP, S1, S2, and S3 as non-whitelisted all-cap tokens. C1--C5 and S1--S3 are defined together in the Nomenclature (`main.tex:53`); NP occurs in the standard term “NP-hardness” (`main.tex:213`). These are advisories for human judgement, not gate failures or reviewer findings.

## Scope not yet covered

These are mechanical checks, not peer review. They do not establish novelty, physical validity, venue fit, figure readability, or the truth of claims outside the registered probes. The ARS panel and independent adversarial review are separate later stages.
