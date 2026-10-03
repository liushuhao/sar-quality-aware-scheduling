---
name: symbolic-gate-deferred-ch5
description: SymPy 符号门延后至 Ch5 开工——双实现一致性/cosθcosψ=cosξ identity/公式↔实现三检查;提前触发=审稿人质疑公式实现
metadata:
  type: project
---

2026-09-25 审查外部调研报告（符号推导工具调研，LLM 提议 + CAS 判定路线）后的延后决定。

**问题（三项无覆盖）**：
1. `src/sar_sim/generator/visibility.py:48` `_off_nadir_to_incidence` 与 `src/sar_sim/metrics/nesz.py:86` 同一球面公式双实现（度/弧度各一份），一致性仅靠 `visibility.py:137` 注释声明，无强制
2. `cosθ_elev·cosψ = cosξ` 恒等式（f3 公式根基，RDR-066）无测试覆盖
3. 论文 f2/f3 公式 ↔ 代码实现一致性无检查

**方案（Ch5 开工时执行，约半天）**：装 K-Dense `scientific-agent-skills` 的 sympy skill（注意：仓已由 `claude-scientific-skills` 改名，gh 重定向证实）+ 写 `src/tools/check_symbolic.py` 只验上述三项。报告其余建议不做：梯度检查（求解器全零阶，无梯度路径，仅 `types.py:77` 注释提及 penalty gradient）、旋转正交性（初等旋转 by construction）、单调性（arcsin(c·sinφ) 一眼真，一次性证明非门）。

**为何延后**：Ch3 已投（2026-09-25 EM 上传闭环），现在建无消费者；Ch5 复用 sar_sim 代码（Ch3 约束 × N + 星间无重复，任务级仍 f1/squint），届时新代码进入即被检查。推迟零成本，现在做若 Ch5 改公式/几何需返工。

**触发提前**：审稿人质疑公式实现正确性 → 立即做第 3 项。

相关：[[ch3-paper-accept-ready]]
