# Author Adjudication — 2026-08-22 Self-Review

**Binds**: `revision-roadmap-20260822.md` (immutable core, 31 concerns + amendment SR-32).
**Rule**: one explicit choice per item. `will_address` = fix + exact targets; `wont_address` = reason, no work; `not_on_point` = reason, no work. No default.

## Status: CONFIRMED — 2026-08-22 user approved (SR-12/13 no-rerun approach + execution order P0 first)

## Execution result (2026-08-22, same session)
All will_address items DONE in both EN and ZH:
- P0: SR-01 abstract rewritten (number diet + arc); SR-12/13 45° reframed at 3 sites each language; SR-18 script path deleted (SR-19/20 same-sentence deletions included); SR-32 Fig3 caption rewritten; SR-25 Fig1 overlap fixed (figsize 9.5x5.5, δ>0 note below axis, negligible label beside band — visually verified); SR-30 Fig4 G-BL visible via hollow GA-P-BL diamond, legend "G-BL (= GA-P-BL)" — visually verified.
- P1: SR-02 single-pass def moved after motivation; SR-04/05/10 symbol bindings added; SR-06 contributions split to 4 items; SR-07 inverse-pixel-area clarifier; SR-08 §2.2 derivation moved to §3.2 new paragraph "Modeling choices behind Eq f3" (EN+ZH), §2.2 keeps lit review + pointer; SR-17 variant sentence; SR-26 Fig1 body expanded; SR-27 f3-panel prose added in §6.3.
- P2: SR-03/21/22/23/24/29/31 done.
- Verification: EN pdflatex x2 = 43pp 0 errors; ZH xelatex x2 = 35pp 0 errors; 0 undefined refs; verify_paper_numbers 170 assertions 0 FAIL + CALIBER OK.
- not_on_point items (SR-09/11/14/15/27-part): no changes made, per adjudication.
- Pending: pregate steps 2-4 (rebuild_snapshot + hard audit) running in background at time of writing.

## Post-re-review adjustments (second pass, before execution)
- SR-01: scope reduced (number diet + arc, not total rewrite) — abstract already binds symbols at first use
- SR-17: sentence-first, table only if insufficient
- SR-32 (new): will_address — Fig3 caption stale, rewrite to cover 7 panels

---

| ID | Choice | Reason / Targets |
|----|--------|------------------|
| SR-01 | **will_address** | Rewrite EN+ZH abstracts: prose objective names, method→validation→conclusion arc, headline numbers only |
| SR-02 | will_address | Move single-pass definition to L137 area / §3.1; open intro with motivation |
| SR-03 | will_address | Weaken "inherently" L95 |
| SR-04/05 | will_address | Add "(denoted f2/f3 below)" binding at L124–127 |
| SR-06 | will_address | Split contribution 1 into 3 items |
| SR-07 | will_address | Add inverse-pixel-area clarifier at L175 |
| SR-08 | will_address | Move §2.2 own-derivation (L267–305) into §3.2; keep lit review + gap only |
| SR-09 | not_on_point | Window is a task attribute; constraint correctly in §3.3 Eq domain. No change |
| SR-10 | will_address | Same define-before-use fix at L378 |
| SR-11/14/15 | not_on_point | All variables defined in §3.1 (L349–356, L493). Optional glosses skipped — cross-page forgetting is reader-side, formulas standard |
| SR-12/13 | will_address | Delete "capability-superset" + "few degrees" claims at L480–485, L1038 context, L1314–1316; reframe as controlled experimental envelope. No rerun |
| SR-16 | will_address | Drop "(labeled A–E in the scenario files)" L667 |
| SR-17 | will_address | Add variant-definition sentence/table (A/B/C distribution; D/E geometry modulation) |
| SR-18 | will_address | Delete script path L693; keep manifest-freshness claim |
| SR-19 | will_address | Remove 5° elevation parenthetical L695 |
| SR-20 | will_address | Delete ~50% L/R sentence L696–697 |
| SR-21 | will_address | Rephrase pymoo line L705; version → Data Availability if retained |
| SR-22 | will_address | Wording swap L775 |
| SR-23 | will_address | Fix double semicolon L778 |
| SR-24 | will_address | "effects contract" → "gains diminish" L781 |
| SR-25 | will_address | Fix Fig1 right-panel overlap: regen with layout fix + visual self-check |
| SR-26 | will_address | Expand Fig1 body text L854 to 2–3 sentences |
| SR-27 | not_on_point (part) | "Not cited" claim false — L903 cites both. But will_address the real gap: add f3-panel prose in §6.3 |
| SR-28 | will_address | Caption note for per-scenario deficit dots; keep panels |
| SR-29 | will_address (partial) | KEEP Class column (reject deletion); add S7/S8 table note |
| SR-30 | will_address | Fix Fig4 G-BL overplotting: hollow GA-P-BL marker or merged "G-BL = GA-P-BL" label; regen + visual check |
| SR-31 | will_address | Split envelope-vs-schedule paragraph into 2–3 paragraphs |

## Summary
- will_address: 25 concerns (some grouped)
- not_on_point: 5 (SR-09, SR-11, SR-14, SR-15, SR-27-part)

## Execution order (work order, author-approved)
1. P0 hard fixes: SR-01 abstract, SR-12/13 squint claims, SR-18 script path, SR-25 Fig1, SR-30 Fig4
2. P1 structure: SR-08 §2.2 move, SR-06 split, SR-02, SR-04/05/07/10 bindings, SR-17 variants, SR-26/27 figure prose
3. P2 wording: SR-03/16/19/20/21/22/23/24/29/31
4. ZH mirror sync throughout; dual compile after each batch
