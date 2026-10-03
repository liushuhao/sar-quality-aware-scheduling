---
name: revision-20260801-wbv5-traev7
description: 2026-08-01 Workbuddy v5(中)+Trae v7(英)审查修复，含两个非显而易见发现
metadata: 
  node_type: memory
  type: project
  originSessionId: 6c8ab907-f390-482c-8be3-3541b40142da
---

2026-08-01 批次：Workbuddy 审中文版（1×P1 + 6×P2 + 2 待确认）、Trae 审英文版（判 0 P1）。全部修复，中英双编译通过（0 undefined）。REVIEW_INDEX 已落档 W-C01~C07 / T-N1~N3 / D01 / G5。

**两个非显而易见发现（对抗核验时挖出，审查报告本身没报或报错）：**

1. **HV 图在两个版本都是孤儿**——Trae v7 声称英文版 fig:fig1 在 L733 被引用，实际那是 `\label` 定义行，grep 把定义误算成引用。中文版改 label 后也丢了引用。两版图后引导段都补了 `\ref`。教训：查"是否被引用"必须 grep `\ref{`，不能 grep label 名字。

2. **p_i 范围论文写 {5..10}，实际数据是 {1..10}（G5）**——400 个实验场景 pkl 全部 `random.randint(1,10)`，求解器直接用、无重映射。前序 RDR E1 自称已核实 {5..10}，但没真加载 pkl。f1\* 是 G-BL 归一化比值（尺度不变），下界变化只改方差不改排序，所有已报告数值都在真实 1–10 数据上算出，结论不受影响，故改论文如实报告 {1..10} 而非重跑。
   - **复用技巧**：pkl 引用的 `sar_sim` 模块已从 repo 重构消失，普通 pickle.load 报 ModuleNotFoundError。用自定义 `pickle.Unpickler.find_class` 返回空 Stub 类即可绕过、直接读 `target.priority` 等字段（见会话脚本）。

3. **Trae N2-v7（Herrmann2023 缺 volume）是误报**——CrossRef 确认 IEEE TAES Early Access 无 volume/issue，只有 pages 1–13，不能编卷号。Liu2024 是 article-number 35（非传统页码），已补 pages={35}。

**Why:** 审查报告是输入信号不是结论，逐条回源文件/数据核验才发现报告自身错误。
**How to apply:** 以后任何"已核实数值范围"类声明，优先直接加载真实 pkl/csv 验证；审稿工具的 grep 类结论要复查它是不是把 label/定义行当引用。关联 [[n150-n200-experiment-done]] [[revision-20260731-fullfix]]。
