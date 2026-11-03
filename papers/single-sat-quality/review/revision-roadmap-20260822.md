# Revision Roadmap — 2026-08-22 Self-Review (Zotero Annotations)

**Source**: `review/注释 (2026-8-22 17-37-06).md` — author's own Zotero annotations on `small-paper-ijae.pdf` (self-review, not external review, not committee).
**Mode**: ARS `academic-paper` revision-coach, peer-review path. No anchored block manifest; locators use `file:line`.
**Immutable core**: 31 concerns parsed (SR-01 … SR-31), source-ordered. Severity = finding type (Major/Minor/Editorial), NOT obligation. Author triage lives in separate `author-adjudication-20260822.md`.
**Manuscript**: `papers/single-sat-quality/small-paper-ijae.tex` (EN) + `small-paper-ijae-zh.tex` (ZH, must sync).

## Legend

- **Type**: Major (core argument/method/conclusion or hard error) | Minor (quality/completeness) | Editorial (wording/format) | Positive
- **Cost**: sentence | section | restructure | figure | new_data
- **Obligation**: left blank — author confirms in sidecar; not derived from severity.

---

## Index

| ID | Page | Locator | Type | Cost | Short |
|----|------|---------|------|------|-------|
| SR-01 | 1 | abstract L34–63 | Major | restructure | Abstract not standalone; f1/f2/f3/solver jargon + number dump |
| SR-02 | 2 | L73–74 | Minor | sentence | "single-pass" definition opens intro before motivation |
| SR-03 | 2 | L95 | Editorial | sentence | "inherently" overstated |
| SR-04 | 3 | L138 | Minor | sentence | f3 used in intro before formal definition |
| SR-05 | 3 | L138–140 | Minor | sentence | f2 used in intro before formal definition |
| SR-06 | 4 | L150–173 | Minor | restructure | Contribution item 1 is 23 lines, bundles 4 claims |
| SR-07 | 4 | L174–175 vs L96–97 | Minor | sentence | f2 index reads as inconsistent with ρ_rg/ρ_az (actually inverse, not stated) |
| SR-08 | 6 | L253–314 | Major | restructure | §2.2 mixes lit review with own derivation (plane-Earth/5%/17%/ordering defense); f2/f3 defined early |
| SR-09 | 8 | L349 | — | — | Window W_i placement — **not_on_point candidate** (correctly a task attribute; constraint in §3.3) |
| SR-10 | 9 | L378 | Minor | sentence | f2 referenced in §3.1 before Eq f2 at L413 |
| SR-11 | 11 | L468 | — | — | a_i,b_i,d_i "undefined" — **not_on_point candidate** (defined L349–350) |
| SR-12 | 11 | L480–485 | Major | sentence | 45° squint called "capability-superset"; some platforms reach 55° → factually wrong |
| SR-13 | 11 | L482–485 | Major | sentence | "platforms slew only a few degrees" understates agility; delete (same root as SR-12) |
| SR-14 | 12 | L496 | — | — | C2 variables "undefined" — **not_on_point candidate** (∆η L493, ω L352, τ L354) |
| SR-15 | 12 | L511 | — | — | e_i,m_i "undefined" — **not_on_point candidate** (defined L355–356) |
| SR-16 | 15 | L667 | Minor | sentence | "(labeled A–E in the scenario files)" ties prose to repo files |
| SR-17 | 15 | L670–673 | Minor | sentence | Variants A–E under-explained; only D/E described; "why S1-D not S2-D" |
| SR-18 | 16 | L693 | Major | sentence | `scripts/generate_s5_scenarios.py` path in manuscript body |
| SR-19 | 16 | L695 | Minor | sentence | "5° above local horizon" redundant vs incidence [18,47]; remove |
| SR-20 | 16 | L696–697 | Minor | sentence | "~50% left/right" unused in any result; remove |
| SR-21 | 16 | L705 | Minor | sentence | "pymoo 0.6.1.6" version in body; move to reproducibility note |
| SR-22 | 18 | L775 | Editorial | sentence | "S4 alone" → "densest class (S4)" |
| SR-23 | 18 | L778 | Editorial | sentence | Double semicolon around "knee-point value" |
| SR-24 | 18 | L781 | Editorial | sentence | "effects contract" → "gains diminish" |
| SR-25 | 20 | fig1 (gen L447–489) | Major | figure | Fig1 right panel: label/annotation overlap (visual bug) |
| SR-26 | 20 | L854 | Minor | sentence | Fig1 gets one sentence; panel/HV/δ under-explained |
| SR-27 | 21 | L903 | Minor | sentence | Claim "Fig3/Table5 not cited" is false (L903 cites both); but Fig3 f3 panel not discussed in prose |
| SR-28 | 22 | fig3 (gen L600–685) | Minor | figure | Fig3 dense (6 boxplots+logistic); faint per-scenario dots unexplained in caption |
| SR-29 | 23 | Table5 L927–938 | Minor | sentence | Class column "redundant"; S7/S8 order looks arbitrary (actually N-ordered, needs note) |
| SR-30 | 24 | fig4 (gen L333–338) | Major | figure | G-BL yellow square invisible — GA-P-BL green diamond overplots (numerically identical by construction) |
| SR-31 | 26 | L1087–1116 | Minor | restructure | "Envelope versus schedule correlation" paragraph ~30 lines, 5 claims; split |

---

## Detail

### SR-01 — Abstract not standalone
- **Raw**: "这摘要的写法感觉和我之前看到的不一样...一般会说提出了什么方法，怎么验证，结论是什么...摘要中出现了大量f1\f2\f3的表述，这要求读者先熟悉正文内容才行，读起来不友好。"
- **Paraphrase**: Abstract leads with internal notation and a number dump instead of method→validation→conclusion arc; f1/f2/f3/G-BL/G-SM/MOEA are undefined for standalone readers.
- **Type**: Major | **Cost**: restructure
- **Section**: Abstract (L34–63)
- **Commitment**: restructure — rewrite abstract to prose objective names (coverage profit / geometric quality / NESZ radiometric quality), named solvers by description, headline numbers only (sparse +34% geo / +41% NESZ at 14–15% coverage cost; dense <2%; hot-start conditional; −0.97 envelope attenuated not eliminated), explicit method (NSGA-III + decomposed physics objectives) and conclusion (conditional saturation regime).
- **Bounded consequence**: Standalone readability; database/preview first impression. No data change.
- **Sync**: ZH abstract in `small-paper-ijae-zh.tex`.

### SR-02 — single-pass definition misplaced
- **Raw**: "上来先说这个，而且约束这么窄，不符合行文逻辑"
- **Paraphrase**: Intro opens with a defensive term definition ("single-pass" = two orbits, not one overflight) before motivating the problem.
- **Type**: Minor | **Cost**: sentence
- **Locator**: L73–74
- **Commitment**: restructure — move definition to first substantive use (L137 area or §3.1) and open intro with SAR/agile-scheduling motivation.
- **Note**: term IS needed (disambiguates from single-overflight); only placement wrong.

### SR-03 — "inherently"
- **Raw**: "用词过重，弱化"
- **Paraphrase**: "SAR imaging inherently departs from this assumption" overstates; quality can be treated as fixed.
- **Type**: Editorial | **Cost**: sentence | **Locator**: L95
- **Commitment**: prose_edit — weaken ("fundamentally differs in the timing-selectable setting" or restructure).

### SR-04 / SR-05 — f2/f3 used in intro before definition
- **Raw (f3 p3)**: "没有定义"; (f2 p3): "没有定义"
- **Paraphrase**: Intro L138–140 uses $f_2$/$f_3$ with no "denoted" binding; formal definition is §3.2 (L407–431).
- **Type**: Minor | **Cost**: sentence | **Locator**: L124–127 (prose descriptions) → L138
- **Commitment**: add_clarification — at L124–127 append "(denoted $f_2$ and $f_3$ below)" so first symbol use is bound.
- **Note**: SR-10 is the same pattern in §3.1 (L378 "using it in f2") before Eq f2. Same fix class.

### SR-06 — Contribution item 1 too long
- **Raw**: "这一段太长了，精简，或者拆成多个小点"
- **Paraphrase**: First enumerated contribution (L150–173) is 23 lines bundling saturation discovery + ablation + initialization conditioning + correlation decomposition.
- **Type**: Minor | **Cost**: restructure | **Locator**: L150–173
- **Commitment**: restructure — split into (a) empirical saturation regime, (b) ablation & hot-start conditioning, (c) envelope-null-schedule geometric-coupling decomposition.

### SR-07 — f2 index vs ρ_rg/ρ_az apparent inconsistency
- **Raw**: "这句话的表述和前面关于几何分辨率、辐射质量的表述不一致...the ground-range resolution degrades with incidence angle (ρrg ∝ 1/sin θ)..."
- **Paraphrase**: Contribution 2 writes f2 = sinθ cosψ_sq while intro writes ρ_rg ∝ 1/sinθ; reader reads contradiction. They are mathematically consistent (f2 ∝ 1/(ρ_rg·ρ_az), ground-pixel-area inverse) but the inverse relation is not stated at the contribution point.
- **Type**: Minor | **Cost**: sentence | **Locator**: L174–175
- **Commitment**: add_clarification — add "(inverse to ground pixel area; ρ_rg ∝ 1/sinθ, ρ_az ∝ 1/cosψ_sq)" at L175. NOT a formula error.
- **Adjudication note**: comment is a clarity failure, not a factual error.

### SR-08 — §2.2 oversteps into own modeling
- **Raw**: "确认本节内容与下面的问题建模有没有冲突？这部分内容是不是理论推导过多，和下面的问题建模有重复？f2\f3的定义属于算法建模的内容，放在本章用于文献综述，不太合适。"
- **Paraphrase**: §2.2 starts as lit review (L254–266) then becomes the paper's own method derivation (L267–305: plane-Earth range model, 5%/17% error, ordering-index defense, squint 10–25% contribution, f3-as-proxy statement). This duplicates §3.2 and defines f2/f3 in the related-work chapter.
- **Type**: Major | **Cost**: restructure | **Locator**: L253–314
- **Commitment**: restructure — move L267–305 own-derivation content to §3.2 / appendix; keep in §2.2 only: established SAR quality models exist (Curlander/Cumming/Moreira) + scheduling literature treats quality as fixed/coarse proxy (gap statement L306–314). Remove f2/f3 definition from §2.2.
- **Bounded consequence**: chapter-boundary correctness; no data change. De-duplicate §3.2.

### SR-09 — W_i window placement [not_on_point candidate]
- **Raw**: "窗口信息与约束相关，写在这里，对吗？"
- **Paraphrase**: Questions whether visibility window W_i=[a_i,b_i] belongs in Task Set (§3.1) vs Constraints.
- **Locator**: L349 (Task Set) vs L467–470 (C-domain constraint).
- **Fact**: Window IS a task attribute (like priority/duration); the constraint is t_i ∈ [a_i,b_i−d_i]. Standard modeling. Both placements correct and present.
- **Candidate**: `not_on_point` — no change; optionally add a half-sentence cross-reference.

### SR-10 — f2 in §3.1 before Eq f2
- see SR-04/05. **Locator**: L378 ("using it in $f_2$").
- **Commitment**: add_clarification — same define-before-use fix; or reword to avoid the symbol before §3.2.

### SR-11 / SR-14 / SR-15 — variables "undefined" [not_on_point candidates]
- **SR-11 raw**: "变量没有定义和说明" (a_i,b_i−d_i at Eq domain). **Fact**: a_i,b_i L349, d_i L350.
- **SR-14 raw**: "缺少变量定义" (C2 formula). **Fact**: ∆η_k L493, ω_max L352, τ_settle L354, d_{s_k} L350, t_s L384.
- **SR-15 raw**: "缺少ei和mi的变量定义". **Fact**: e_i,m_i L355–356.
- **Candidate**: `not_on_point` (all defined in §3.1). Optional gloss after each formula for cross-page readability.

### SR-12 / SR-13 — 45° squint envelope overclaim
- **SR-12 raw**: "设定45度约束不合理，有的能机动到55度，因此在建模阶段，不应指定45度的角度限制。"
- **SR-13 raw**: "这样说不合适，对于某些卫星来讲，机动到这角度没有问题。此句话可删去"
- **Paraphrase**: (1) Calling 45° a "capability-superset envelope" is false if platforms reach 55°. (2) "Real agile SAR platforms typically slew only a few degrees" understates agility and should be deleted.
- **Type**: Major | **Cost**: sentence | **Locator**: L480–485; repeats L1038 (null envelope), L1314–1316 (§7.3 operational implications).
- **Commitment**: prose_edit — delete "capability-superset" claim and the "few degrees" sentence at all three sites; reframe 45° as "a controlled experimental agility envelope spanning the literature-reported range, not a claim about any specific platform". Do NOT rerun — 45° results remain valid; only the claim about platform capability changes.
- **Bounded consequence**: factual accuracy of platform-capability claim; operational-relevance tone.
- **Adjudication note**: user is SAR domain expert; 55° platform fact taken as given.

### SR-16 — "(labeled A–E in the scenario files)"
- **Raw**: "与github上的项目数据绑定，是不是不太合适？"
- **Paraphrase**: Prose references repo file labels.
- **Type**: Minor | **Cost**: sentence | **Locator**: L667
- **Commitment**: prose_edit — drop "(labeled A–E in the scenario files)"; define A–E in prose/table (see SR-17).

### SR-17 — variants D/E described, A/B/C not
- **Raw**: "重点聚集了D和E，那其他的选项没有说。另外为什么选持S1-D而不是S2-D？"
- **Paraphrase**: Five variants A–E; only S1-D/S3-D (single orbit), S2-E (high lat), S4-D (incidence 25°) described. A/B/C said to be "uniform/clustered/mixed" with no table; D's role differs by class (geometry vs single-orbit), confusing.
- **Type**: Minor | **Cost**: section | **Locator**: L667–673
- **Commitment**: add_clarification — small variant-definition table or sentence (A/B/C = distribution variants; D/E = geometry modulation, role class-dependent); state S7/S8 naming note (see SR-29).

### SR-18 — script path in body
- **Raw**: "论文正文里不要出现脚本"
- **Paraphrase**: `scripts/generate_s5_scenarios.py` in manuscript body.
- **Type**: Major | **Cost**: sentence | **Locator**: L693
- **Commitment**: prose_edit — delete path; keep anti-dredging claim "all reported numbers correspond to a fixed scenario manifest (no manifest revision postdates the results)". Repo path already in Data Availability (L1461).

### SR-19 — 5° minimum elevation
- **Raw**: "这个表述与入射角、斜视角约束不匹配，入射角的约束应该更强，这个表述也可以不出现论文正文中。"
- **Paraphrase**: 5° elevation filter is dominated by incidence [18°,47°]; mentioning it adds nothing.
- **Type**: Minor | **Cost**: sentence | **Locator**: L695
- **Commitment**: prose_edit — remove parenthetical or note it is subsumed by incidence filter.

### SR-20 — ~50% left/right split
- **Raw**: "这句话想说明什么意思？如没有用，可以不写。"
- **Paraphrase**: Left/right ~50/50 fact feeds no result.
- **Type**: Minor | **Cost**: sentence | **Locator**: L696–697
- **Commitment**: prose_edit — delete.

### SR-21 — pymoo version in body
- **Raw**: "论文正文应删除对代码或脚本的引用"
- **Paraphrase**: "NSGA-III selection operator is implemented via pymoo 0.6.1.6" is implementation detail.
- **Type**: Minor | **Cost**: sentence | **Locator**: L705
- **Commitment**: prose_edit — rephrase to "NSGA-III follows the reference-point selection of Deb et al. (2014)"; move version to Data Availability/reproducibility note if kept.

### SR-22 / SR-23 / SR-24 — wording
- SR-22 "S4 alone" L775 → Editorial → "the densest class (S4)".
- SR-23 double semicolon L778 (`f1*=0.86; knee-point value; the best-coverage...`) → Editorial → em-dash/parentheses.
- SR-24 "At S2 the effects contract" L781 → Editorial → "performance gains diminish".
- **Commitment**: prose_edit each.

### SR-25 — Fig1 right-panel overlap
- **Raw**: "右图文字重叠在了一起？"
- **Paraphrase**: Visual bug in Fig1 right panel (pairwise Cliff's δ forest plot) — ytick labels and/or MOEA-2-vs-MOEA-3 annotation overlap.
- **Type**: Major | **Cost**: figure | **Locator**: `experiments/gen_all_figures.py` L447–489; output `figures/fig1_hypervolume.pdf`
- **Commitment**: other (figure regen) — increase right margin / reduce font / raise fig height / wrap annotation; rerun `gen_all_figures.py`, visual self-check (scipilot-figure-skill), recompile.
- **Bounded consequence**: figure legibility; no data change.

### SR-26 — Fig1 under-explained in body
- **Raw**: "图1想表达什么含义？解释的过少，占了很大篇幅，但没有展开说明"
- **Paraphrase**: L854 one sentence for a full-width figure; HV distribution reading, δ direction, gray band, key pairwise comparisons not explained.
- **Type**: Minor | **Cost**: sentence | **Locator**: L854
- **Commitment**: add_clarification — expand to 2–3 sentences (what HV boxes show; δ sign/gray band; which pairs negligible vs meaningful; forward-ref cardinality confound to §6.4).

### SR-27 — Fig3/Table5 "not cited" + f3 panel undiscussed
- **Raw**: "正文里没有看到对Fig3和Table5的说明与引用...其他章节是不是也有类似问题？"
- **Paraphrase**: (a) "Not cited" is factually wrong — L903 cites both. (b) Fig3 has an f3 panel that §6.3 prose never discusses.
- **Type**: Minor | **Cost**: sentence | **Locator**: L903 (cite exists); f3 panel gen L566–598.
- **Commitment**: add_clarification — add 1–2 sentences on the f3 panel (MOEA-3 sparse separation / dense convergence, consistent with Table 1). Sweep all 5 figures for body-explanation gaps (Fig1=thin SR-26, Fig2=OK, Fig3 f3=gap, Fig4=OK §6.4, Fig5=OK ablation).
- **Candidate on "not cited"**: `not_on_point` (citation exists).

### SR-28 — Fig3 dense + faint dots unexplained
- **Raw**: "即有蜡烛图，又有曲线图，内容太多了...靠近0的位置，有一些淡黑色的点，图例显示为per-scenario dificit，这条曲线有什么意义？"
- **Paraphrase**: 7-panel figure dense; bottom logistic panel's jittered per-scenario deficit dots not explained in caption.
- **Type**: Minor | **Cost**: figure | **Locator**: caption L920; gen L658–685
- **Commitment**: add_clarification — caption add "Bottom: jittered per-scenario deficit indicators (f1*<0.95) with logistic fit". Keep 7 panels (single scale-sensitivity theme); revisit split if caption fix insufficient.

### SR-29 — Table5 class column / order
- **Raw**: "第一列是不是可以不要，S1~S8的顺序有乱...通过第2列N可以看到目标数的变化，这样就够了吧？"
- **Paraphrase**: Class column seems redundant; row order S1,S2,S7,S8,S3,S4 looks arbitrary but is N-ordered (20,100,150,200,300,500); S7/S8 unexplained.
- **Type**: Minor | **Cost**: sentence | **Locator**: Table5 L927–938
- **Commitment**: add_clarification — KEEP Class column (used throughout paper for cross-ref); add table note "S7/S8 are intermediate scale points (50 scenarios each, MOEA-2 + G-BL/G-SM only; see §5.1)". Order is correct by N.

### SR-30 — Fig4 G-BL marker invisible
- **Raw**: "图例中的黄色方框代表G-BL，但从图中根本看不到这个黄色方框，可能和绿色菱形重叠在了一起"
- **Paraphrase**: G-BL orange square is overplotted by GA-P-BL green diamond because the two are numerically identical by the never-worse-than-baseline guard (L597–603, Table 1 rows equal).
- **Type**: Major | **Cost**: figure | **Locator**: gen L333–338 (panel a), L389–394 (panel b); §4.3 L597–603
- **Commitment**: other (figure regen) — plot GA-P-BL as hollow/edge-only marker so G-BL shows through, OR merge into one marker labeled "G-BL = GA-P-BL" (honest: GA-P-BL is a control, not independent solver). Update legend + caption. Rerun + visual check.
- **Bounded consequence**: figure honesty/legibility; reflects a documented numerical identity, not a data error.

### SR-31 — "Envelope versus schedule correlation" paragraph
- **Raw**: "这段话为什么这么长？"
- **Paraphrase**: L1087–1116 ~30 lines packs 5 claims (envelope −0.97; differs from null −0.51; schedules shift toward zero; active solver effect not envelope constraint; variant-D ablation support).
- **Type**: Minor | **Cost**: restructure | **Locator**: L1087–1116
- **Commitment**: restructure — split at logical boundaries into 2–3 paragraphs.

---

## Cross-cutting sweeps (举一反三)

1. **Symbol define-before-use** (SR-04/05/10): grep first use of f1/f2/f3/G-BL/G-SM/MOEA in abstract + intro + §3.1; bind or reword. ZH sync.
2. **Code/script/package in prose** (SR-16/18/21): grep `\texttt{` in body; move paths/versions to Data Availability (L1457–1463).
3. **Platform-capability overclaim** (SR-12/13): grep "inherently" (L95), "capability-superset" (L481), "few degrees" (L482, L1315); reframe all as controlled experimental bound.
4. **Figure body-explanation gap** (SR-26/27): audit Fig1–Fig5 — each panel/caption explained in prose; Fig1 thin, Fig3 f3 panel missing.
5. **Long paragraphs** (SR-06/31): split >15-line paragraphs in contributions + §6.4.
6. **Scenario-generation cruft** (SR-19/20): remove 5° elevation + 50% L/R sentences that feed no result.

## Out of scope (do not change without separate approval)

- No solver reruns (SR-12/13 reframing does not invalidate 45° results).
- No new experiments/figures beyond fixing Fig1 (SR-25) and Fig4 (SR-30) rendering.
- No claim-strength moves beyond the registered prose edits above.
- ZH mirror must follow EN adjudication one-to-one.

---

# Amendments (2026-08-22 post-re-review, second pass)

Re-reviewed all 31 concerns with fresh eyes before execution. Core entries above unchanged; corrections recorded here.

## SR-01 rationale correction (scope reduced)
Original detail overstated symbol opacity: the abstract DOES bind symbols at first use ("geometric quality $f_2$ L41", "NESZ objective $f_3$ L43", "greedy baseline (G-BL) L44", "squint-minimizing greedy heuristic G-SM L45"). Remaining defect: number density (10+ figures) and buried method sentence. **Reduced commitment**: number diet (keep 4-5 headline numbers: sparse +34% geo / +41% NESZ at 14-15% coverage cost; dense <2%; hot-start deficit range; -0.97 attenuated-not-eliminated) + surface the method sentence. Not a total rewrite.

## SR-17 commitment refinement (sentence before table)
Prefer one defining sentence (A/B/C = target-distribution variants uniform/clustered/mixed; D/E = geometry modulation whose role is class-dependent) over a new table. Table only if sentence proves insufficient. Reason: bilingual layout sync cost.

## NEW ENTRY SR-32 — Fig3 caption does not match figure content
- **Discovered**: post-re-review verification of SR-28.
- **Raw evidence**: caption L920 reads "Geometric quality ($f_2$) by scenario group and solver", but `figures/fig3_scale_sensitivity.pdf` contains 7 panels: boxplots of f1*/f2/f3 x (S1-S2, S3-S4) plus a bottom logistic-transition panel with per-scenario deficit dots. Stale caption from an earlier single-panel version.
- **Type**: Major | **Cost**: sentence | **Locator**: L920 (EN), ZH mirror caption
- **Commitment**: rewrite caption to describe all panels (three objective rows, two density bands, logistic transition with jittered per-scenario deficit indicators and N50 CI); absorb SR-28's dot explanation. Regenerate nothing - caption-only fix.
- **Adjudication**: pending user confirmation (expected will_address).

## Verdicts after re-review
- 29 maintained as-is; SR-01 scope reduced; SR-17 refined; SR-32 added.
