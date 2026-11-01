# Paper2 main-thread verification — 2026-10-31

## Review target and integrity

- Repository HEAD: `ec6d6076af65f13d0b075dc0c7106074a187ea05`
- `paper/main.tex` SHA-256: `ad0487f52c5811608ca4fa8a0fbbe796a46f512a74027577ce1273c75821da22`
- Working tree before review: clean. No manuscript or source file was edited by this review.
- Isolated clean build: 46 pages, pass 4 has 0 errors, 0 undefined references/citations, 0 rerun warning.
- All five reviewer cards passed ARS phase-conformance; the complete five-seat panel passed the layer-1 checker; the synthesizer passed `check_panel_synthesis.py` (exit 0).

## What the major findings actually establish

| Roadmap | Main-thread verdict | Direct evidence |
|---|---|---|
| R1 floor share carries an unbounded policy component | **CONFIRMED as a claim-scope problem**, not a numeric error. The abstract attaches “20.0 and 44.8 of those points” to the stripmap floor; §7.1 alone adds that “part of the floor-dominated cost is the comparability policy, not the platform.” No number bounds that policy share. | `main.tex:29` vs `main.tex:427` |
| R2 no published planner supplies an external denominator | **CONFIRMED omission, already disclosed.** The paper explicitly says no scheduler from the literature is run; the issue is whether the significance claim can stand without one, not whether the omission is hidden. | `main.tex:429` |
| R3 “mode-dependence” is not identified against density | **CONFIRMED.** The figure caption itself says density and mode composition covary and “nothing in this figure is a controlled comparison.” The contribution label is therefore broader than the identification design. | `main.tex:255`; contribution at `main.tex:72` |
| R4 abstract lacks the construction-bounded qualifier | **CONFIRMED as wording scope.** The abstract reports 26.0/46.6-point drops without saying they are the greedy construction’s readings; the body later states the anchor carries 258/260 units and that no statement attributes the response to the optimiser. | `main.tex:29`; `main.tex:240`; `main.tex:319` |
| R5 ambiguity module omits the scene-sweep occupancy kept in the dwell closure | **PLAUSIBLE, premise partly confirmed, causal claim not independently verified.** The asymmetry is visible: the dwell closure carries `W_a`, while the AASR integral is azimuth-frequency only. The stronger claim that this asymmetry *drives* the reported squint-direction result requires an author derivation or a targeted run; the reviewer did not demonstrate it. Keep the item as a required response, not a confirmed wrong result. | `main.tex:143` (dwell includes `W_a`); `main.tex:176` (AASR integration convention); `main.tex:433` (paper discloses the unmodelled scan-span channel) |
| R6 intra-dwell resolution degradation is unbounded | **CONFIRMED missing magnitude.** The paper explicitly limits the identity to the selected start and gives the cosine-ratio form, but reports no worst-case degradation over the dwell. No contradiction; an operations-facing claim lacks its translation number. | `main.tex:190` |
| R7 fixed-dwell violation rate is convention-contingent | **CONFIRMED.** The zero-squint arm gives 27–42% violations; the conservative pre-shrunk arm gives zero by construction at 28.3/55.5-point cost. “Robust, repair-independent” is true only relative to the repair rule. | `main.tex:400`; `main.tex:404` |
| R8 served-priority objective is nearly inert under uniform priorities | **CONFIRMED as a reporting/objective-semantics issue.** The paper states served fractions track priority fractions to within about two points and that priorities are “close to inert in practice.” This is disclosed, but the stated objective then does not select much. | `main.tex:380` |
| R9 “essentially solved by a single construction pass” | **CONFIRMED over-strong inference.** The evidence is 258/260 anchor domination plus limited probes; no upper bound or stronger search establishes a problem property. | `main.tex:240`; probes at `main.tex:369` |
| S13 R2F S1 verdict vs anchor-granularity disclaimer | **CONFIRMED internal tension in labelling.** The same 0.268/0.359-point movements are called a result about the scenario set and also said to support no demand-axis statement. | `main.tex:338` vs `main.tex:369` |
| EIC W6 table precision | **CONFIRMED minor arithmetic/display mismatch.** Exact values give 46.58 pp (46.6); printed three-decimal values give 46.5 pp. | `gates/eic-w6-rounding.log` |
| Citation metadata | **TWO CORRECTIONS CONFIRMED; three missing marks disproved.** Peng 2019 pages should be 84–98, not 193–205. Shen 2024's current Crossref record is 2025, vol. 63, pp. 1–13. Mittermayer 2003, Cumming & Wong 2005 and Currie & Brown 1992 exist and are checker false negatives. | `01-citation-precheck.md` |

## Overall verification judgement

The panel's **Major Revision** outcome is supported, but the reason is narrower than “the results are wrong.” The registered numbers reproduce, the build is clean, and no reviewer found a fatal computational defect. The Major issues are concentrated in **claim scope and construct naming**: the paper's headline is a construction-bounded, frozen-routing sensitivity reading, while parts of the abstract and contribution surface invite a physical/platform-cost reading; the “mode-dependence” construct is not identified against density; and several operational labels (served priority, fixed-dwell failure, resolution equality) promise more than the measurements deliver.

Three must-fix items are direct numerical/reporting fixes or reframing: R1, R3/R4, and R7/R8. R5 is the one physics item that needs a substantive author analysis; it should not be presented to the user as a proven equation error. R2's external baseline is a design cost the author must either pay or explicitly fold into the significance claim.

## Heterogeneous review status

The free-model attempts were blocked by daily usage limits. The fallback alternate-backend `claude -p` review completed and is recorded in `independent-hetero-review.md`; its one confirmed Major finding was independently recomputed by the main thread in `03-hetero-findings-verification.md`: the printed SLS closure at `main.tex:143` double-counts `W_a` and overstates the executable dwell by 10.3% at the reference point. Reported results are unaffected because the code is the source of all numbers, but the method text is not reproducible as written. This is a correlated-model-family miss: the five-seat panel did not find it, and the panel must not be described as independent.

## Mechanical checks

See `00-pregate-summary.md` and `01-citation-precheck.md`. The L8 checker's standalone `full.md` invocation exits 2 because of its own `L8_MIN_CHECKED=155` floor; the canonical combined `main.tex + full.md` invocation checks 299 numbers and exits 0.
