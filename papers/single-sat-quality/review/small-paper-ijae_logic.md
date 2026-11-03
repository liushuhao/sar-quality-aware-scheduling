# Logic Verification Report

**Paper:** small-paper-ijae.tex (EN, HEAD 9f20ac6)
**Date:** 2026-08-20

## Part 1 — Argument Chain View

| Section | Primary Claim | Connects To | Status |
|---------|--------------|-------------|--------|
| Introduction | SAR quality varies with observation timing; no existing method treats physics-derived quality as decomposed MOO objectives; saturation regime exists | Methods | Connected |
| Related Work | Prior scheduling works omit or approximate SAR physical quality dimensions | Methods (gap confirmed by formulation) | Connected |
| Problem Formulation | Three-objective formulation (f1 coverage, f2 geometric, f3 NESZ) with C1-C4 constraints | Methods (solver designs implement this) | Connected |
| Methodology | Five configurations isolate the effect of adding physical quality objectives | Results (experiments run exactly these) | Connected |
| Results | Scale-dependent saturation: +34% f2 at S1, <1% at S4; mechanism = geometric coupling + lower-squint convergence | Discussion | Connected |
| Discussion | Saturation regime is conditional on initialization and search; operational guidelines follow from density threshold | Conclusion | Connected |
| Conclusion | Physics-aware MOO provides benefit only at sparse density under tested conditions | — | Terminal |

## Part 2 — Categorized Issue List

### Argument Chain Gaps

No argument chain breaks found. The Introduction promise (five configurations, scale-dependent saturation) is fulfilled in Results and synthesized in Discussion. The mechanism section (§6.4) bridges Results to Discussion convincingly.

---

### Unsupported Claims

No unsupported claims found. All quantitative claims trace to Table 4, Table 5, or ablation results. Statistical assertions cite p-values and Cliff's δ.

---

### Terminology Inconsistencies

**Issue TI-1: "redundancy" vs. "indistinguishability under tested search" — Terminology Drift in §7.4**
**Section:** [§6.4, §7.1, §7.4 (Limitations)]
**Problem:** §6.4 carefully establishes the term "third-objective indistinguishability" — the empirical convergence effect where MOEA-3 and MOEA-2 produce equivalent outcomes at operational density, explicitly distinguishing this from mathematical redundancy. §7.1 uses "density-dependent rather than redundant" correctly. However, §7.4 (Limitations, line 1349) reverts to "The 3-objective redundancy reported above," dropping the careful qualification. This re-introduces the exact imprecise framing that §6.4 spent significant text ruling out.
**Why this matters:** A reviewer reading §7.4 in isolation would conclude the paper claims the third objective is inherently redundant — contradicting the paper's own thesis that the effect is conditional on density and convergence. This weakens the Limitations section's credibility.
**Suggestion:** Replace "3-objective redundancy" in §7.4 with "density-dependent third-objective indistinguishability" or "the convergence-driven indistinguishability of the three-objective formulation at operational density" to match §6.4/§7.1 terminology.
> **[Chinese]** 问题：§6.4 建立了"indistinguishability under tested search"术语，§7.1 正确使用"density-dependent rather than redundant"，但 §7.4（Limitations）回退到"The 3-objective redundancy"，丢失了限定条件。为什么重要：审稿人若只读 §7.4 会误以为论文主张第三目标固有冗余，与论文自身"条件性收敛效应"的论点矛盾。建议：§7.4 中"3-objective redundancy"改为"density-dependent indistinguishability"或等价限定表述。

---

**Issue TI-2: "single-pass" definition placement — §1 vs. §3.1**
**Section:** [§1 line 73-74, §3.1]
**Problem:** The operational definition of "single-pass" (two-orbit scheduling horizon, ~200 min) is placed as a floating clarification at the very start of §1 (lines 73-74), before the Introduction body begins. It is not repeated or cross-referenced in §3.1 (System Model), where the two-orbit horizon and task-set design are formally specified. This placement is unusual — readers encountering it at the top of §1 may not retain the definition through Related Work and Problem Formulation before encountering it again in §5.1.
**Why this matters:** Minor structural issue. The definition is present and accurate, but its separation from the formal system model in §3.1 weakens its integration into the paper's technical spine.
**Suggestion:** Low priority. Consider adding a brief forward reference in §3.1 ("as defined in §1, the scheduling horizon spans two orbital periods") or moving the definition to §3.1 where the system model is formally introduced. Alternatively, the current placement is defensible if the author judges the §1 positioning serves as a necessary readerOrientation note before the Introduction body.
> **[Chinese]** 问题："single-pass"操作定义（两个轨道周期、~200分钟）放在§1开头（L73-74），但§3.1系统模型中未回引或重复。为什么重要：定义与形式化模型分离，读者在Related Work和问题建模之间可能遗忘此定义。建议：低优先级——可在§3.1加一句回引，或维持现状（§1位置作为reader Orientation可接受）。

---

### Number Contradictions

No number contradictions found. Key cross-references verified:

| Claim site | Value | Table/Data source | Consistent? |
|---|---|---|---|
| Abstract: "+34% f2 at N=20" | 0.394 vs 0.295 | Table 4 S1 MOEA-2 vs G-BL | ✓ |
| Abstract: "+41% f3 at N=20" | 0.699 vs 0.497 | Table 4 S1 MOEA-3 vs G-BL | ✓ |
| Abstract: "14% coverage cost" | f1*=0.86 | Table 4 S1 MOEA-2 | ✓ |
| Abstract: "15% coverage cost" | f1*=0.85 | Table 4 S1 MOEA-3 | ✓ |
| §6.1: "+34% f2" | Same as above | Table 4 | ✓ |
| §6.1: knee-point disclosed | "+12.5% best-coverage front" | Added in 9f20ac6 | ✓ |
| §6.3 Table 6: "+33.7% at S1" | Per-scenario mean ratio | Footnote in caption: "abstract reports ratio of pooled means" | ✓ (methodological difference acknowledged) |
| §7.1: "+33.7% at N=20 falling to +0.4% at N=500" | Matches Table 6 | Table 6 S1 and S4 | ✓ |
| §7.2: "+25% pixel area reduction from +34% f2" | 1/f2 scaling: (0.394-0.295)/0.394 ≈ 25.1% | Eq.2 relationship | ✓ |

---

### Structural Issues (supplementary)

**Issue S-1: Broken sentence in §7.2 (Operational Implications)**
**Section:** [§7.2, lines ~1301-1308]
**Problem:** The sentence beginning "For maritime surveillance tasks where the" (original text) was interrupted by the G1 knee-point disclosure edit (commit 9f20ac6), which prepended "The knee-point +34% f2 gain at S1 corresponds to roughly a 25% reduction in ground pixel area..." The resulting paragraph reads:

> "...depends on the application: for maritime surveillance tasks where the The knee-point +34% f2 gain at S1 corresponds to roughly a 25% reduction in ground pixel area..., the coverage cost may be justified; for area-monitoring missions, the greedy baseline remains preferable."

The phrase "for maritime surveillance tasks where the" is now an orphaned clause — the original sentence that completed this thought was removed during the G1 edit, but the dependent clause opener was left behind. Additionally, the new sentence starting "The knee-point..." should begin with "For" to connect grammatically to the preceding colon.

**Why this matters:** This is a grammatically broken sentence that will be immediately caught by any reviewer or copy-editor. It signals hasty post-review editing.

**Suggestion:** Repair to one of:
- Option A: Remove "where the" and start the new sentence with "For": "...depends on the application: for maritime surveillance, the knee-point +34% f2 gain..."
- Option B: Complete the original maritime surveillance sentence and start a new sentence after the semicolon: "...depends on the application. For maritime surveillance, the knee-point +34% f2 gain at S1 corresponds to roughly a 25% reduction in ground pixel area..., and the coverage cost may be justified; for area-monitoring missions, the greedy baseline remains preferable."
> **[Chinese]** 问题：§7.2（L1301-1308）存在断裂句。G1膝点披露编辑（9f20ac6）在"for maritime surveillance tasks where the"后插入新句"The knee-point +34%..."，导致"where the"成为悬空从句。为什么重要：语法错误明显，任何审稿人或编辑会立即发现。建议：删除"where the"，或将整句重构为完整句。

---

**Issue S-2: §7.4 uses "redundancy" where §6.4 established "indistinguishability"**
*(Same as TI-1, listed here for visibility as it also has a structural dimension)*

---

Found 3 issues: 0 AC-, 0 UC-, 2 TI-, 0 NC- (plus 1 structural S-1).
