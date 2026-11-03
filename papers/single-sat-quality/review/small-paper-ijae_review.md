# Peer Review Report

**Paper:** small-paper-ijae.tex — Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite
**Target Journal:** Advances in Space Research (ASR)
**Date:** 2026-08-20

## Scoring Overview

| Dimension | Score (1-10) | Justification |
|-----------|:---:|---------------|
| Novelty | 7 | Genuine gap: SAR scheduling with decomposed physics objectives. Limited by single-satellite/single-pass scope, but the saturation-regime finding is non-obvious and well-supported. |
| Methodology | 8 | Rigorous 200-scenario design across 4 density classes; 5 configurations correctly isolate the physical-objective effect; 4 ablation variants with controlled design; 4 robustness controls. Statistical framework appropriate. |
| Writing Quality | 7 | Generally clear and precise. One grammatical defect from recent edit (§7.2 broken sentence). Terminology drift in Limitations (redundancy vs. indistinguishability). Otherwise well-structured prose. |
| Presentation | 7 | Tables well-organized; figures appropriately selected. The 5-figure layout is standard for ASR. Ablation table is dense but readable. |
| Significance | 7 | Operational guideline (N<100 MOEA useful, N>300 greedy sufficient) is directly actionable for mission planners. Limited by the 45° squint envelope exceeding operational reality. |

**Overall: 7.2/10 — solid work, publishable after minor prose fixes.**

## Major Concerns

### Major Concern 1: Grammatical defect in §7.2 (Operational Implications)

**Section:** §7.2, lines ~1301-1308

**Problem:** The recent knee-point disclosure edit (commit 9f20ac6) left a broken sentence: "for maritime surveillance tasks where the The knee-point +34% f2 gain..." The dependent clause opener "where the" is orphaned, and the sentence that originally completed this thought was replaced mid-clause. The result is grammatically malformed.

**Why this matters:** Any reviewer or copy-editor will immediately flag this. It signals hasty post-review patching and undermines the polish of an otherwise well-edited manuscript.

**Suggestion:** Remove "where the" and restructure: "...depends on the application: for maritime surveillance, the knee-point +34% f2 gain at S1 corresponds to roughly a 25% reduction in ground pixel area..." This repairs the grammar while preserving the knee-point disclosure.

> **[Chinese]** 问题：§7.2 的膝点披露编辑（9f20ac6）在"for maritime surveillance tasks where the"后直接接入新句"The knee-point..."，导致"where the"成为悬空从句，语法断裂。为什么重要：审稿人或编辑会立即发现此语法错误，给人匆忙修改的印象。建议：删除"where the"，重构为"...depends on the application: for maritime surveillance, the knee-point +34%..."

---

### Major Concern 2: Terminology regression in Limitations (§7.4)

**Section:** §7.4, line 1349

**Problem:** The Limitations section states "The 3-objective redundancy reported above is specific to the single-pass, single-satellite Stripmap setting." However, §6.4 carefully established that the observed effect is "indistinguishability under tested search" — an empirical convergence phenomenon — not inherent redundancy. §7.1 correctly uses "density-dependent rather than redundant." The Limitations section regresses to the imprecise term, contradicting the paper's own careful framing.

**Why this matters:** A reviewer reading §7.4 in isolation would conclude the paper claims the third objective is fundamentally redundant. This contradicts the paper's thesis (that the effect is conditional on density/initialization) and could prompt a "Major Revision" recommendation from a careful reviewer.

**Suggestion:** Replace "3-objective redundancy" with "density-dependent third-objective indistinguishability" or "the convergence-driven indistinguishability of the three-objective formulation at operational density."

> **[Chinese]** 问题：§7.4 使用"3-objective redundancy"，但§6.4 建立的术语是"indistinguishability under tested search"（经验收敛效应，非固有冗余）。§7.1 正确使用"density-dependent rather than redundant"，§7.4 回退到不精确表述。为什么重要：审稿人若单独阅读§7.4 会误认为论文主张第三目标固有冗余，与论文核心论点矛盾。建议：改为"density-dependent third-objective indistinguishability"。

---

## Minor Concerns

### Minor Concern 1: Single-pass definition not integrated into §3.1

**Section:** §1 (line 73-74), §3.1

**Problem:** The "single-pass" definition (two-orbit horizon, ~200 min) is placed as a floating note at the top of §1 before the Introduction body. It is not referenced in §3.1 where the system model is formally specified, nor in §5.1 where the scheduling horizon is described.

**Why this matters:** Minor structural weakness. Readers may encounter the term in §3.1 or §5.1 without recalling the §1 clarification.

**Suggestion:** Add a brief parenthetical in §5.1 or §3.1 linking back to the §1 definition, or relocate the definition to §3.1 where it formally belongs.

> **[Chinese]** 问题："single-pass"操作定义放在§1开头（L73-74），但§3.1 系统模型和§5.1 实验设置中均未回引。为什么重要：读者可能在§3.1或§5.1首次遇到此术语时遗忘§1的定义。建议：在§3.1或§5.1加一句回引，或将定义移至§3.1。

---

### Minor Concern 2: f2 improvement reporting — pooled means vs. per-scenario ratios

**Section:** Abstract (line 41), §6.3 Table 6 caption

**Problem:** The Abstract reports "+34% in f2 at N=20" as the ratio of pooled class means (MOEA-2 pooled mean / G-BL pooled mean - 1). Table 6 reports "+33.7%" as the mean of per-scenario ratios. These are slightly different quantities due to Jensen's inequality. The Table 6 caption acknowledges this ("the abstract reports the ratio of pooled means"), but the Abstract does not note the methodological difference.

**Why this matters:** Very minor. A methodologically astute reviewer might note the inconsistency. The 0.3 percentage-point difference is negligible in practice.

**Suggestion:** No change required. The current approach (reporting the more intuitive pooled-ratio in the Abstract, noting the per-scenario alternative in Table 6) is standard practice and acceptable.

> **[Chinese]** 问题：Abstract报告"+34%"为汇总均值之比，Table 6报告"+33.7%"为逐场景比值的均值，两者因Jensen不等式略有差异。Table 6脚注已注明，但Abstract未说明。为什么重要：极轻微。方法论敏感的审稿人可能注意此差异，实际影响可忽略。建议：无需修改，当前处理方式符合学术惯例。

---

## Questions for Authors

1. The 45° squint envelope is noted as exceeding operational agility. Has the authors' group or any cited platform demonstrated >10° squint capability, or is the 45° bound purely a theoretical ceiling? If the former, a citation would strengthen the operational relevance; if the latter, the operational guideline should explicitly note this caveat at the claim sites.

   > **[Chinese]** 45° squint包络被标注为超出实际敏捷性。作者团队或任何已引用平台是否展示过>10° squint能力，还是45°纯为理论上限？若有实际先例，引用可增强操作相关性；若为理论值，操作指南应在声明处明确注明此限定。

2. The hot-start dependence (§6.6) means the dense-regime convergence is conditional. Are the authors planning unconditional random-init experiments at full scale (200 scenarios × 4 classes), or is the current partial experiment (10/4/5/5 scenarios × 3 seeds) considered sufficient evidence for the conditional claim as stated?

   > **[Chinese]** 热启动依赖性（§6.6）意味着密集区域收敛是有条件的。作者是否计划全规模无条件随机初始化实验（200场景×4类），还是认为当前部分实验（10/4/5/5场景×3种子）对条件性结论已足够？

---

## Verdict

**Recommendation:** Minor Revision

The paper presents a rigorous, well-designed study with a genuinely novel contribution (physics-aware SAR scheduling with scale-dependent saturation analysis). The methodology is sound, the statistical framework appropriate, and the operational implications are clearly stated. Two prose defects from recent editing — a grammatical break in §7.2 and a terminology regression in §7.4 — require immediate repair before submission. Both are ~15-minute fixes with no data implications. After these repairs, the paper is ready for submission to ASR.

> **[Chinese]** 建议：小修后接收。论文呈现了严谨、设计良好的研究，具有真正新颖的贡献（物理感知SAR调度及尺度依赖饱和分析）。方法论合理，统计框架恰当，操作含义表述清晰。两处近期编辑造成的语言缺陷——§7.2 语法断裂和§7.4 术语回退——需在投稿前立即修复。均为~15分钟的纯文字修复，无数据影响。修复后论文可投ASR。

---

*Found 2 major concerns, 2 minor concerns, 2 questions for authors.*
