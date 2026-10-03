# Accept 后仍要独立审：friendly review 漏过的三防线

两轮内部审（07-12/07-13 都 Accept）的 Ch3 小论文，2026-07-19 独立审查（4 并行 subagent：领域文献/代码数据/图表LaTeX/Devil's Advocate）仍发现 6 CRITICAL + 12 MAJOR。friendly review 系统性漏过三类：

1. **数据可追溯性**：论文数字与 results/ JSON 不一致（HV 漂移 +0.01）、关键实验脚本有 bug（Variant D 实际跑 Variant A）、prose-only 数字无脚本支撑（N50 logistic 回归）。friendly review 读论文不读代码/数据。
2. **最新文献**：前置威胁论文未引（Kramer 2025）。friendly review 不独立 web 核实文献存在性/作者/DOI，且 subagent 会基于用户给的前提跑（循环论证风险，推 Acta Astro 时踩过）。
3. **Devil's Advocate**：random-search 击败 MOEA-2、Δr 类别错误（相关系数不可线性做差）、feasibility-manifold 替代解释未处理。friendly review 不做对抗性论证。

**Why:** 2026-07-19 Ch3 审查。内部审基于"论文叙事自洽"判 Accept，但叙事自洽 ≠ 数据可追溯/文献完整/论证无漏洞。三防线是 friendly review 的结构性盲区。

**How to apply:** 论文投稿前，除常规内部审外，必跑三防线独立审查：(1) 逐数字 grep 到 results/ JSON 或脚本；(2) 关键前置文献独立 web 核实（作者/DOI/年份），不轻信 subagent 基于前提的结论；(3) Devil's Advocate subagent 做"最强反驳"测试。高危区：prose-only 数字（无脚本生成的统计量）、"first to"类 novelty 声明、Δr/相关系数差这类统计量运算。