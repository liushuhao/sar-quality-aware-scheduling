# Paper1 bilingual-mirror red-team — consolidated, 2026-11-01

Two independent reviewers (`p1-final-mirror`, `p1-mirror2`) completed this dimension but were blocked by the harness from writing files ("Subagents should return findings as text, not write report files"); their findings arrived as messages. Every finding below was **re-verified by the main thread against the files** before being recorded — line numbers, quotes and cross-checks are the main thread's own. Nothing in the manuscript was edited.

## Verdict

**FINDINGS — 4 Major + several Minor, all Chinese-side.** The English manuscript's mirror partner is not equivalent: the Chinese version contains three statements the English does not make (one of them refuted by the paper's own Table 6) and one sentence whose meaning is inverted. No finding touches the English PDF.

## Major

### ZM-1 — Ablation scenario count is wrong in ZH §5.1

- EN `small-paper-ijae.tex:870-873`: "the ablation experiment … running each variant on the same **six scenario classes (300 scenarios)**".
- ZH `small-paper-ijae-zh.tex:580-581`: "第二类为消融实验 … 每变体在相同的 **200 个场景**上运行".
- Both ablation sections say 6 classes × 50 seeds = **300 runs** per variant (`sections/_ablation_section.tex:35`, `sections/_ablation_section-zh.tex:30`), and the ZH contribution list (`:113`) also says "每种 300 场景".
- Verdict: ZH contradicts EN, its own contribution list, and its own ablation section. Fix: 200 → 300 in ZH `:581`.

### ZM-2 — ZH gives G-BL a placement rule the paper does not have

- EN `:619-623`: tasks are "greedily inserted into the schedule at their earliest feasible time. This earliest-time placement fixes each task's observation geometry implicitly through the window's incidence–squint profile rather than through any quality criterion."
- ZH `:441`: "每个任务在其可见窗口中预存的**离轴角（产生最大仰角的角——相当于固定天底策略）**处观测."
- Verdict: "fixed-nadir policy at the pre-stored off-nadir angle of maximum elevation" is a different algorithm; it also contradicts the ZH sentence immediately before it (`:440`, earliest-feasible-time insertion) and the one after it (`:444`, "G-BL 仅因可行性而选择观测时间"). Delete the sentence and restore the EN meaning ("最早时刻放置隐含地由窗口的入射–斜视剖面决定几何，而非任何质量标准").

### ZM-3 — ZH finding (4) asserts precision the paper does not have, and Table 6 refutes it

- EN `:1455-1456`: "solver outcomes become invariant to the choice of physical objectives at $N \geq 300$ (ablation study)" — no percentages.
- ZH `:974`: "各变体收敛到基线的 **$1\%$ 以内（$f_1^*$）、$0.5\%$ 以内（$f_2, f_3, n_{\text{sel}}$）**".
- Refuted by the paper's own numbers: the ablation text says within **0.2%** for f1* and within **0.6%** for f2 (`_ablation_section-zh.tex:123-124`), and Table 6 gives S3 f3: B 0.618 vs A 0.623 = **−0.80%**, D 0.616 = **−1.12%**; S4 f2: D 0.336 vs A 0.338 = **−0.59%**. f3 and n_sel are not claimed invariant anywhere else.
- Verdict: the ZH sentence adds three unclaimed quantities and an unsupported 0.5% bound. Fix: replace with the EN sentence (no percentages), or with the ablation section's own 0.2%/0.6% figures scoped to f1* and f2 only.

### ZM-4 — ZH conclusion attaches the coverage cost to the wrong solver

- EN `:1637-1638`: "MOEA-2 raises $f_2$ by $+33.7\%$ … and MOEA-3 raises $f_3$ by $+40\%$ over the greedy anchor **at a 14–15% coverage cost**" — the range covers both solvers.
- ZH `:1058`: "MOEA-2 以 $14$–$15\%$ 的覆盖率代价将 $f_2$ 提升 $+33.7\%$（…），MOEA-3 相对贪心参考将 $f_3$ 提升 $+40\%$" — the cost now belongs to MOEA-2 only, leaving MOEA-3's gain uncosted.
- Body values: MOEA-2's f2 gain is priced at 14% (`f_1* = 0.86`), MOEA-3's f3 gain at 15% (`f_1* = 0.85`). 
- Verdict: meaning changed — the ZH conclusion implies the third objective's gain is free. Fix: "MOEA-2 以 14%、MOEA-3 以 15% 的覆盖率代价分别将 $f_2$ / $f_3$ 提升 …".

## Major-adjacent wording inversion

### ZM-5 — "coverage cost" rendered as "coverage advantage"

- EN `:1035`: "The coverage **cost** of multi-objective optimization is therefore a sparse-density phenomenon".
- ZH `:708`: "因此多目标覆盖**优势**是稀疏密度现象".
- The surrounding sentences make the intended meaning recoverable, so this is a summary-line inversion rather than a data error, but the direction word is wrong. Fix: 优势 → 代价.

## Minor

| ID | Location | Issue (verified) |
|---|---|---|
| Zm-1 | ZH `:450` vs EN `:639` | The $+0.99$ G-SM effect is pointed at §7.1 (`sec:summary`) in ZH but at §6.2 (`sec:squint-special`) in EN; the derivation lives in §6.2. |
| Zm-2 | ZH `:462-471` vs EN `:662-669` | ZH §4.4 omits the GA-P-BL never-worse-than-baseline guard paragraph (199/200, +13.5%, mean $f_1^*$ within 0.001, control role). `13.5` appears nowhere in the ZH file. |
| Zm-3 | ZH `:1065` vs EN `:1653` | "the guard acts on the single profit objective" mistranslated as "总是触发" (always triggers) — trigger frequency vs scope of the guard. |
| Zm-4 | ZH §5.2 vs EN §5.2 | The knee-selector / selector-sensitivity paragraph is in EN §5.2 Evaluation Metrics (`:827-847`) but in ZH §4 MOEA subsection (`:482`); ZH §5.2 does not carry it. |
| Zm-5 | ZH `:746-754` vs EN `:1090-1095` | ZH drops the scope limit that the compression is "a property of the found front … rather than of the full feasible trade-off surface", including the G-SM counter-evidence ($f_3 \approx 0.79$ at S4 outside the MOEA-3 surface). |
| Zm-6 | ZH §7 limitations vs EN `:1597-1600` | ZH drops the open question "whether the MOEA can independently discover high-coverage solutions without greedy seeding". |
| Zm-7 | ZH `:264-271` vs EN `:385-390` | ZH Objective 1 omits the EN normalisation rationale (G-BL vs GA-P-BL conservative, 199/200 identical, mean $f_1^* = 1.00$). |
| Zm-8 | ZH `:326-327` vs EN `:462-464` | Variable naming drift: EN "$\xi$ minimal" / "$\sin\theta_{\text{elev}}$"; ZH "θ 最小" / "$\sin\theta$". |
| Zm-9 | EN `:262-311` vs ZH `:180-205` | ZH-only related-work content (Taylor/Hamming weighting, Moreira survey sentence, NSGA-III crowding-distance and application list). Additive on the ZH side; harmless but asymmetric. |
| Zm-10 | ZH `:552-553`, `:569-571` | ZH-only calibration paragraphs (niche pressure with 91 directions and a pop=200 check; operational anchors for $\lvert\delta\rvert$). |
| Zm-11 | ZH `:101-102` vs EN `:138-143` | ZH intro adds "零覆盖代价" and the $+0.05\%$ radiometric-blind figure; EN carries both in the body but not the intro. |
| Zm-12 | ZH `:998-1002` vs EN `:1503-1507` | ZH adds a normative recommendation for G-SM usage and an $f_1^*$ gap phrase that EN does not contain. |
| Zm-13 | ablation captions ZH `43/97` vs EN `54/108` | Caption qualifiers dropped in ZH: "Δf1*% column", "12 variant-by-class comparisons", "applied within each reported metric". |
| Zm-14 | ZH `:4` | Header claims a stale sync date ("revision 2026-07-31，已同步") given the divergences above. |

## Checked and clean

Abstract (all magnitudes and qualifiers), all 8 section and 22 subsection headings, all 5 figure and 6 table captions apart from Zm-13, the solver-profile / HV / scale-sensitivity / ablation table values themselves, §6.1–6.3 and 6.5–6.6, §7.1 and §7.3, AI disclosure, CRediT, data availability, competing interests and funding. All cross-references resolve except Zm-1. Highlights and cover letter agree with the manuscript's numbers (checked separately).

## Why this pass disagrees with the earlier main-thread note

The first main-thread mirror pass compared numbers and section structure only; it caught Zm-2 and Zm-4 and missed ZM-1, ZM-2, ZM-3, ZM-5 because those are semantic or added-precision defects that a numeric multiset cannot see. The reviewer passes caught them; the table above records the main thread's re-verification, not the reviewers' claims.

## Coverage limits

Not inspected: `.bib` (covered separately in `report-facts-mainthread.md`), rendered figure pixels, source-data recomputation. Translation style, sentence order and typography were deliberately excluded.
