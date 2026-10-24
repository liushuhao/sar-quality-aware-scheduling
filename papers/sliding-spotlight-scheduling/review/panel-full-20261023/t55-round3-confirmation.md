# Round-3 CONFIRMATION (Claude Code) — 2026-10-24

Reviewer: fresh subagent, round 3 of the fix-verification loop. Scope: verify ONLY the six items round 2 left open (m6, N1, N2, N3, two bare "L8" node-names, T13 justification clause), plus a fresh-eyes pass over exactly the passages those fixes touched. Materials: `paper/main.tex`, `paper/full.md`, `paper/sections/sec3_problem_formulation.md`, `sec5_experimental_design.md`, `sec6_results.md` (+ `sec2_related_work.md` for a surviving-word check), round-2 report `t55-round2-conformance.md`. Read-only except this file.

**Commit note**: the fixes are committed as `a573e6f` ("paper2 t55 R1/R2 修复轮", 2026-10-24 09:55), which bundles the R1 batch (already verified RESOLVED in round 2 against the then-working-tree) with the R2 fixes under test here; `paper/` worktree is clean at HEAD. The R2 fix portion per the commit message: m6, N1, N2, N3, L8×2, T13 — exactly the six items below.

## Per-item verification

### (1) m6 — em-dash graft "---, so" in the §6.3 withdrawn-penalty sentence: RESOLVED

- Grep `---, so` across all of `paper/`: **0 matches** (main.tex, full.md, all sections/*.md).
- main.tex L343 now reads: "…equal to its own as-placed value at the displayed precision --- not below it --- so the tight arm no longer falls at all."
- Mirror layers carry the identical fixed sentence: full.md L396 and sec6_results.md L55, both "--- not below it --- so the tight arm no longer falls at all."
- Fix exactly as round 1 specified (comma dropped, parenthetical intact).

### (2) N1 — mirror drift on "physical sliding domain" / "tan-exact Kim Eq": RESOLVED

- Grep `physical sliding domain` across `paper/`: **0 matches** (was full.md L291 + sec5_experimental_design.md L11).
- Grep `tan-exact Kim` across `paper/`: **0 matches** (was full.md L159 + sec3_problem_formulation.md L27).
- §5.1 mirrors now carry the corrected sentence: full.md L291 and sec5_experimental_design.md L11 both read "…a sample outside the mode envelope contributes an exclusion, so it can never mask an unserviceable window." — matching main.tex L262. (Punctuation differs between layers — main.tex ". A sample" vs mirrors "; a sample" — but round-1/round-2 quotes show this period/semicolon divergence pre-existed the fix; the phrase swap preserved each layer's punctuation. Pre-existing, not introduced.)
- §3.2 mirrors now carry the reworded opening: full.md L159 and sec3_problem_formulation.md L27 both read "The production closures follow the reference geometry's scene-level sweep-span construction, evaluated tan-exactly about the centre squint (the symmetric construction quantified against the exact chain below)…" — matching main.tex L160. The umbrella no longer asserts tan-exactness for all three modes.
- Surviving "tan-exact" word instances (main.tex L99/L160/L176; full.md L93/L159/L177; sec2_related_work.md L17; sec3_problem_formulation.md L27/L39) checked for stale umbrellas: L176/sec3:39 "the spotlight gain is the tan-exact point-dwell ratio" (specific, correct — SPT point dwell IS the tan-difference); L159/sec3:27 "evaluated tan-exactly about the centre squint" and "the kill-test switch from the planar form to the tan-exact chain" (the fixed sentence's own wording + historical reference); L99/sec2:17 "the tan-exact closure chain of Section 3.2" — shorthand consistent with the revised §3.2 framing, pre-existing, not a touched passage, and round-2's full-document read did not flag it. No stale umbrella survives.

### (3) N2 — false-universal clause: RESOLVED

- Grep `wherever the loosening recovery is quoted` across `paper/`: **0 matches** (fix route (a), deletion).
- §6.2 sentence now ends cleanly at the divergence explanation — main.tex L335: "…which reads 3.98 points for the mixed family and 0.93 for the 50-task family; the paired statistic is smaller than the median-of-medians because several seeds already saturate at the loose end. Both as-placed costs are readings under the anchor construction…" No dangling connector, no graft.
- Mirrors identical: full.md L376, sec6_results.md L39.

### (4) N3 — tolerance definition at §5.3 first-use paragraph, named mapping, §6.3 back-reference: RESOLVED (manuscript); one mirror-drift residual filed as N4 below

- §5.3 first-use paragraph (main.tex L278, the "Three criteria, frozen…" paragraph): the first-use sentence still reads "…the tight arm reads pairwise per-seed deltas against a one-priority-unit tolerance…" and the definition immediately follows in the same paragraph: "**The one-priority-unit tolerance is one count of the priority numerator, $1/\sum_i p_i$ of the scenario --- the smallest nonzero priority movement --- which is about 0.86 (R1C), 0.38 (R2F) and 0.19 (R3H) points at the registered task counts.**" Definition at first-use paragraph ✓; family mapping **named** exactly as the fix spec asked (0.86 R1C / 0.38 R2F / 0.19 R3H) ✓. Grep `0\.86 \(R1C\)` confirms presence in all three layers: main.tex L278, full.md L315, sec5_experimental_design.md L27.
- §6.3 main.tex L341 now uses the back-reference: "…against the one-priority-unit tolerance of Section~\ref{sec:hypotheses}." The old inline definition is gone from main.tex §6.3; the `\ref{sec:hypotheses}` target is §5.3 (L274), where the definition now lives — correct reference. No earlier use of the term exists before L278 (grep: main.tex L278 ×2, L335, L341 ×2, L351 — L335's "flat to within one priority unit" postdates the definition in reading order; Table-3 caption L351's bare mention is acceptable with the definition in §5.3).
- Values still consistent with the verdicts round 2 verified: R2F dips 0.268/0.359 < 0.38; R3H plateau movement 0.18 ≤ 0.19.

### (5) Bare "L8" node-names (L270 body + Table-2 caption): RESOLVED

- Grep `L8` across `paper/`: the only hit is `SUBMISSION_CHECKLIST.md` L3 — an internal tracking document where "L8 数字闸" (L8 number-gate) is a legitimate project term, not manuscript text. Manuscript layers (main.tex, full.md, sections/*.md): **0 hits**.
- main.tex L270 body: "The artifacts are the released artifact set of this scenario generation (measurement conventions v5)… The released set re-runs the sweep over the same frozen scenario population --- the task set, the visibility windows and the mode assignment are carried over unchanged, so the demand axis is the only thing that moves --- at a single registered budget of 40/60 population/generations." Mirror: full.md L303, sec5_experimental_design.md L19 (identical).
- Table-2 caption main.tex L296: "…(released artifacts, budget 40/60)." Mirror full.md L352 identical.
- "conventions v5" is not a new bare node-name: it is used consistently across the paper (L286, L343) and defined by context ("measurement conventions v5").

### (6) T13 — omission-justification clause in §6.5: RESOLVED

- main.tex L376 now carries: "**The all-stripmap control is deliberately omitted from this reading: its served fraction equals its priority fraction wherever it is feasible (both saturate together), and its step cell is arithmetic rather than a schedule outcome (Section~\ref{sec:criteria}).**" Explicit "deliberately omitted" + two-part reason + cross-reference to §6.3 (`sec:criteria`, L339 — where the step-cell infeasibility arithmetic is explained; correct target). Grep `deliberately omitted` confirms all three layers: main.tex L376, full.md L423, sec6_results.md L73 (mirror renders the ref as "Section 6.3" — correct).
- The every-grid-point completeness clause itself remains unmet by design (three R3H points + R2F tight-side range only); the justification route round 2 accepted is now explicitly on the record, which was the open residual.

## Fresh-eyes pass over the touched passages

Grammar/numbering sweep of exactly the edited sentences (main.tex L262/L270/L278/L296/L335/L341/L343/L376 + all their mirror counterparts): no new grafts found. Specifically checked: em-dash parenthetical balance in L343 and L278; sentence boundary after the N2 deletion in L335 (clean, no orphaned connector); the L278 definition's relative clause parses ("which is about…" attaches to the $1/\sum_i p_i$ count through the em-dash appositive); cross-reference targets of the two new back-references (`sec:hypotheses` → §5.3 where the definition lives; `sec:criteria` → §6.3 where the step-cell arithmetic lives) — both correct; numbers in touched passages consistent with prior rounds' traces (0.86/0.38/0.19 vs dips 0.268/0.359 and plateau 0.18; 0.9764 vs §6.5's 0.974–0.976 range; 3.98/0.93 paired medians unchanged; 40/60 budget; conventions v5). Protected amendment dates in the touched §5.3 paragraph survive (2026-10-20/21/22/23 all present at L278).

## New defects introduced by these fixes

- **N4 (MINOR) — mirror drift, same class as round-2 N1: the §6.3 back-reference was applied to main.tex only.** full.md L385 and sec6_results.md L45 still carry the pre-fix round-1 text: "…against a tolerance of one priority unit --- one count of the priority numerator, 1/sum_i p_i of the scenario, i.e. the smallest nonzero priority movement, which is about 0.86, 0.38 and 0.19 points for the three families at their registered task counts." — while main.tex L341 now reads "…against the one-priority-unit tolerance of Section~\ref{sec:hypotheses}." So the mirrors (a) duplicate a definition main.tex replaced with a back-reference, and (b) retain the **unnamed** mapping ("for the three families") that N3 ordered named. No verdict changes (the retained text is factually consistent, and round 2 judged the unnamed mapping a clarity nit, not correctness); it is a two-line re-port of main.tex L341 into both mirror layers. Fix: replace the inline definition clause in full.md L385 / sec6_results.md L45 with the back-reference form ("…against the one-priority-unit tolerance of Section 5.3.").

## Verdict line

ROUND3: 0 critical / 0 major / 1 minor | LOOP: CLOSED

Closed basis: all six open items RESOLVED in the manuscript layer (with mirror propagation verified for m6, N1, N2, N3-definition, L8, T13); the single new defect (N4) is a minor mirror-sync re-port, same severity class as round-2 N1, and minors do not block closure under the loop rule. N4 is one edit in two files and can be landed without a further confirmation round; if a round 4 is run anyway, N4 is its only open item.
