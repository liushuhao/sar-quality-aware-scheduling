## 发现列表

**MAJOR — §7.4 Limitations，`small-paper-ijae.tex:1610–1612`**

原文：

> “The utility model also optimizes quality and quantity at a fixed timeliness operating point; explicit latency and urgency objectives are left to future work.”

**理由：**“fixed timeliness operating point”与正文所述求解器行为不符。§7.2 Operational Implications 明确写道（`small-paper-ijae.tex:1547–1551`）：

> “G-BL places each task at its earliest feasible time within the visibility window, whereas quality-steering solutions may delay acquisitions to reach lower-squint geometry”

G-SM 同样会在窗口内选择最小斜视时刻，而非固定在统一时刻（`small-paper-ijae.tex:632–645`）。因此，不同求解器及候选解的观测时机会变化；没有被优化的是 **timeliness 目标**，不是存在一个固定的 timeliness 操作点。本批修改删除了“最早可行时刻仅属于 greedy baseline”的解释，却保留了这个过宽表述，导致限制节与 §7.2 直接矛盾，也掩盖了“时效性随解变化但未作为指标评估”的真实边界。

**建议：**改为：

> “The utility model optimizes quality and quantity without an explicit latency or urgency objective; acquisition timing varies across solvers, but timeliness is not evaluated as a separate scheduling dimension and is left to future work.”

## Verdict

**FAIL** — 限制节仍将可变的观测时刻称为固定的 timeliness operating point，与 §7.2 的求解器行为描述直接矛盾；其余修改块未见须修级问题。
