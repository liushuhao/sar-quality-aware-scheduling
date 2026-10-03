# 2026-07-31 三家审计全清单修复（Qwen r3 / Workbuddy v4 / Trae v4-v6）

## 状态
- 英文版 small-paper-ijae.tex：P1×7 + P2×16 + P3 组全改，共 ~35 处 Edit
- 中文版：除镜像外还清了前序欠账（图名×5 悬空→编译级故障、t 检验→Wilcoxon、消融表值/显著性、B/C 不对称段与 D 反超段补译、62% 句、跨节断句、"首个 MOEA"、"所有这些工作"、HV 排名 MOEA-2 第一的事实错误、Wiley 注释）
- 台账：review/REVIEW_INDEX.md + 本批次状态表（RDR 机制回归）
- **未完成（分类器后端故障阻塞）**：编译 ×2×2、bib CrossRef 查询、G2 脚本定谳（40k vs 394k pairs）、p_i/d_i/timing 挖掘、arXiv 存在性验证、ppw 技能链正式跑（de-ai/logic 已人工等效执行）

## 非显而易见教训
1. **Trae 机械术语扫描产出假阳性**：v6 N7（L1090 "geometric resolution" 改 quality index）会与标题/摘要命名制造新不一致；N8（"definitional coupling" 并入 "factorized null"）混淆两个不同概念（现象 vs 度量工具）。术语统一类建议必须先过概念审查再应用。
2. **Trae 数值验证的引用纪律缺陷**：v4/v5 把 statistical_results.json per_group 的 4 位值标成出自 solver_summary.csv（后者只有 2 位）。数值真、出处假。用它"全部通过"结论可以，引 its 出处标注要自查。v6 改用 2 位值变相修复。
3. **三家共同盲区**：双语检查（zh L911 Wiley 注释连漏四轮）、样本量计数（论文 "≈40,000 pairs" vs JSON ≈394,000，无人核过）、审计饱和（v5→v6 论文零变化下再审，净新发现仅 2 条且开始产出假阳性——审计回路边际转负信号）。
4. **中文版是旧快照雷区**：zh 文件头部标着对应英文版的 revision 日期，同步前先 diff 头部日期；本次发现 zh 落后 3 轮修订（07-24 vs 07-31），欠账比本轮修复量还大。
5. **N1（physical limits 归类）是真问题但非逻辑矛盾**：经验效应可由物理几何导致，两陈述攻击不同命题；修法按"归类过强"处理（→ geometric properties + (2) 经验效应限定），不按"自相矛盾"。
6. F4 Pareto-sufficient 贴标数据依据：effect_sizes.json MOEA-2_f2_vs_GBL_f2 δ=0.545 (p=1.4e-34)——池化值，贴标时用 "sparse-to-moderate" 限定而非 per-scale 断言。
