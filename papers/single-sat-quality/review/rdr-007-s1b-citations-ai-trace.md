# RDR-007 — S1b 引用完整性 + AI 痕迹（rev2 审稿）

**来源**：S1 INTEGRITY S1b（子 agent 引用上下文 B1 + AI 痕迹 7 模式审查，2026-08-10）
**优先级**：P2（机械已修）/ P1（Chang 核实中）
**状态**：混合（见各条）

## 机械类（事实错，已修，双版编译待确认）

| ID | 问题 | 修复 |
|---|---|---|
| C-1 | bib Peng2019Orienteering 标题 "Agile Earth Observation Satellite Scheduling: An Orienteering Problem with Time-Dependent Profits and Resources" —— 实为 "An Orienteering Problem with Time-Dependent Profits and Travel Times"（COR 111:84-98；Crossref 核实，无 AEOS 前缀，无 "Resources"） | 已修 bib title |
| C-2 | bib Wei2025MONP 标题漏 "Problem"（实为 "…Agile Earth Satellite Scheduling Problem Considering Image Quality"，SWEVO 2025） | 已修 bib title |
| C-3 | bib Zhou2025TwoPhase 标题 "…Two-Phase Hybrid Algorithm for Multi-Agile Earth Observation Satellite Scheduling" —— Crossref 正式标题 "Deep Reinforcement Learning-Based Two-Phase Hybrid Optimization for Scheduling Agile Earth Observation Satellites"（Remote Sensing 17(12):1972, DOI 10.3390/rs17121972 已核） | 已修 bib title |

## 高优先核实（待 agent 结果）

| ID | 问题 | 影响 |
|---|---|---|
| C-4 | §2 L209-213 称 Chang2022Gaofen "two adaptive NSGA-II variants" + "bi-objective (profit + energy)… omits imaging quality"。检索证据：ALNS+NSGA-II 与 ALNS+NSGA-III（非两个 NSGA-II 变体）+ Scilit 关键词 "THREE-OBJECTIVE"。若该文实为三目标（含成像质量），"closest prior work omits imaging quality" 论证受影响 | 若确认，改 §2 措辞（§7.1 结论不受影响，例外文献 Wei2025/Kramer2025 仍成立） |

## 裁决类（AI 痕迹，S3 处理，不直接改）

| ID | 问题 | 建议 |
|---|---|---|
| A-1 | "not a mathematical identity between objectives" / "the third objective is therefore density-dependent rather than redundant" 跨摘要/§6.4/§7.4/结论复用 ≥4 次 | RDR-002 科学诚实措辞保留；只在 §6.4 机制段 + §7.4 各留一次，其余改正面陈述（"redundancy is conditional on density"） |
| A-2 | §6.4 机制四段连续以 "not X but Y" 收束（L890/L941/L961/L977）| 改其中 2-3 处收尾为数据总结句 |
| A-3 | §6.6 四 control 段收尾三处同用 "therefore…rather than" 公式 | 至少两段改写收尾 |

## 附加发现（裁决）

| ID | 问题 |
|---|---|
| H-3 | highlights.tex #3 "MOEA-2 and MOEA-3 near-identical: 3-obj redundancy anchor-independent" 与 RDR-002 后正文结论（§6.4/§7.1 "density-dependent rather than redundant"，稀疏区 MOEA-3 显著 +84% f3）**矛盾**。需改 highlights #3（S5 处理） |

## 验证清单

- [ ] bib 3 处修复后编译双版（EN pdflatex / ZH xelatex）确认 bibtex 无 error
- [ ] Chang2022 C-4 agent 结果回来后裁定
- [ ] A-1/A-2/A-3 与 H-3 在 S3 整合 / S5 REVISE 处理
