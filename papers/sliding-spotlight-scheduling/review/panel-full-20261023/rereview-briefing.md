# Re-Review Briefing — Adversarial verification of a five-seat panel synthesis (2026-10-24)

You are an INDEPENDENT cross-tool re-reviewer. A five-seat simulated review panel reviewed the manuscript below; a synthesizer (editorial seat) then merged the five reports into an Editorial Decision Letter with a revision roadmap. Your job is NOT to re-run the panel. Your job is to adversarially audit the SYNTHESIS: fabrication, arithmetic, adjudication quality, roadmap traceability, and missed load-bearing findings. You have no prior session context; everything you need is in the files listed below. You are the second layer of a three-layer chain: panel+synthesis (done) → your re-review (this) → a final adjudication by a third model family (after you).

## Materials (read-only)

- Manuscript: `D:/hermes/my-workspace/projects/planning-paper/papers/sliding-spotlight-scheduling/paper/main.tex` (Elsevier elsarticle, ~48 pp; read in FULL)
- Seat reports (all five, in `D:/hermes/my-workspace/projects/planning-paper/papers/sliding-spotlight-scheduling/review/panel-full-20261023/`):
  - `seat1-eic.md` (journal fit; issues E1–E10)
  - `seat2-methodology.md` (M1–M3, m1–m6)
  - `seat3-domain.md` (D1–D3, D4–D9)
  - `seat4-perspective.md` (P1–P9)
  - `seat5-devils-advocate.md` (DA1–DA13)
- Editorial Decision Letter (the object under audit): `editorial-decision.md` (same dir)
- Frozen formula registry (for tracing registry claims): `D:/hermes/my-workspace/projects/planning-paper/papers/sliding-spotlight-scheduling/formulas/formula-spec.md`

## HARD CONSTRAINTS

- READ-ONLY on the manuscript and all project files. Your ONLY permitted write is your one output report (path below). No LaTeX builds. No test suites. No network. No reads of anything else under `review/` outside `panel-full-20261023/`.
- You MAY run small read-only computations (python one-liners, grep) to recompute arithmetic. Do not write any file other than your report.
- Every verdict you issue must carry an evidence anchor (file + location + short quote or recomputed number). If you cannot verify a claim, say UNVERIFIED — never guess.
- Do not manufacture findings. A clean audit result is a legitimate result.

## Audit tasks (do all six; report per task)

**A1 — Fabrication check (Iron Rule: every synthesis point must trace to a seat report).**
For EACH roadmap item T1–T19 in editorial-decision.md §5: name which seat finding(s) it claims to trace to, and verify the trace actually exists in that seat's report with matching content (not just similar keywords). Also check §2 (consensus table C1–C8) and §3 (CRITICAL adjudications). Flag any synthesis point that no seat report supports, any seat finding materially misrepresented in strength/severity, and any seat finding of CRITICAL/MAJOR severity that the letter drops without mention.

**A2 — Arithmetic recomputation.** Recompute independently:
1. The counterfactual gap ≈ dropped-task priority mass claim (DA2/C1): from the manuscript's §6.6 numbers (184/926 pairs, 135/458 pairs; families ~99–100 and 46–50 tasks with stated coverage medians), is the claim "the 18.25/30.44 pp gaps are essentially the dropped tasks' priority mass" a fair characterization, an overstatement, or an error? State your own estimate and its assumptions.
2. The floor-exclusion accounting: Table 2 vs §6.1 "20.01 of the 26.01-point drop" and "44.78 of the 46.58-point drop".
3. The abstract contradiction (C4): "within 0.27 points throughout" (abstract) vs the 0.359 pp dip (§6.4) vs the conclusion's wording (L419 region). Confirm or refute that the abstract sentence is false under its natural reading.
4. The §3.1 vs §7.3 velocity-convention contradiction (C3): both sentences are quoted in the letter; read them in main.tex (§3.1 scene-velocity paragraph; §7.3 "The scene-velocity convention ... so they are invariant to it"). Is the letter's arbitration (§7.3 is the false side) physically correct given C2 charges (1+0.25)·T_dwell + 4.07 s + 2.0 s?
5. Duplicate blocks C5: count occurrences in main.tex of "Across the five constraint families" and "Across the 30 released R-family manifests".

**A3 — CRITICAL adjudication quality (the letter's two validated CRITICALs).**
- DA1 (confounded causal title): is VALIDATED the right call given the manuscript's own §6.1 sentence and the absence of composition-matched cells? Or is the within-family evidence (floor decomposition on R3H; R2F flatness; R1C step) strong enough that the title's causal reading survives? Argue both sides, then rule.
- DA2 (repair-rule-manufactured gap): same — steel-man the paper's defense (the 20–29% violation rate is repair-independent; the gap is disclosed as coming after "a deterministic time-order repair"; is abstract disclosure adequate?), then rule.

**A4 — Missed findings sweep.** Read the manuscript for load-bearing defects the panel and letter may ALL have missed (the panel was same-model-family; correlated errors are plausible). Focus areas: abstract/conclusion consistency beyond C4; Table 1–3 internal consistency; §3.5's three-mode-rules paragraph vs §5.2's grandfathered composition; the criteria timeline (§5.3 vs §6.3); anything in the counterfactual design beyond the repair rule. Report at most your top 3 as NEW findings with severity, or state none found.

**A5 — Verdict soundness.** The letter's final decision is Major Revision (four seats unanimous + 2 validated CRITICALs). Given your audit results: is Major Revision the right verdict, or should it be Minor (if you find the fixes are mostly editorial) / Reject (if you find a defect that invalidates the curves)? Rule with rationale.

**A6 — Roadmap completeness/ordering.** Are Tier 1/2/3 assignments correctly weighted? Any must-fix misfiled as should-fix or vice versa? Any T-item that conflicts with another T-item or with the "explicitly protects" list?

## Output

Write your report to:
`D:/hermes/my-workspace/projects/planning-paper/papers/sliding-spotlight-scheduling/review/panel-full-20261023/rr1-claudecode-rereview.md`

Structure:
```
# Cross-Tool Re-Review (Claude Code) — Audit of panel synthesis, 2026-10-24
## 1. Audit summary (≤200 words)
## 2. A1 fabrication check — per-item table (T1–T19, C1–C8, §3 adjudications): trace confirmed / misrepresented / unsupported
## 3. A2 arithmetic — five recomputations with your numbers
## 4. A3 CRITICAL adjudications — both-sides argument + ruling each
## 5. A4 new findings (≤3, or "none")
## 6. A5 verdict ruling + rationale
## 7. A6 roadmap weighting notes
## 8. Provenance: tool, model if known, fresh context, read-only scope, computations run
```
Final line: `REREVIEW-VERDICT: synthesis SOUND | SOUND-WITH-CORRECTIONS | UNSOUND — CRITICAL: n | MAJOR: n | MINOR: n` (n = defects you found IN THE SYNTHESIS, not in the manuscript).

Write nothing else. Do not modify the manuscript or any seat report.
