---
name: grep-filename-is-not-reading-content
description: 修「某能力不存在」前，grep 到文件名不等于读过内容——票21 F5 我据此误报「无等价脚本」，实为守卫是 pytest 不是脚本
metadata:
  node_type: memory
  type: feedback
  originSessionId: db31c19b-4aa5-4c94-8c0b-5c9252951e97
  modified: 2026-10-02T14:18:12.267Z
---

2026-10-02 票 21 修 F5（`numerical_check.py` 死指针）时，我 grep `theta_a` 拿到一串 .py 文件名（duration/geometry/modes/windows），**没有逐个打开**，就写下「全仓 0 命中且**无等价脚本**」。独立复算推翻后半句：等价物存在，只是形态不同 —— 守卫是 **pytest 测试** `tests/test_duration_models.py::test_identity_theta_a_over_A_equals_lambda_over_2rho`（docstring 明写「Formula-spec §6 table 5」），不是脚本。

**Why:** 「不存在」是**强否定断言**，误报代价不对称 —— 误报「无等价物」会把「改指到存活守卫」降格成「删除指针」，**让一条活的回归守卫变成死条文**。而且 grep 的输出单位（文件名）与要回答的问题单位（能力）不同；文件名匹配 ≠ 语义覆盖。同 [[feedback-verifier-shares-failure-surface]]、[[feedback-negative-existence-claims]]，但那条讲的是对话问答须先 grep，这一条讲的是**grep 之后还要读**。

**How to apply:**
- 凡要写「无等价物 / 不存在 / 从未」，grep 出候选后**逐个打开读关键段落**（函数名 + docstring），再落笔。命中文件名只是候选，不是证据。
- 检索时**按形态穷举**，别只搜同类形态：找「验证某恒等式的代码」不能只搜 `*.py` 里的脚本，要一并搜 `test_*`、pytest fixture、注册表 JSON、CI 配置。守卫常住在测试里而非工具里。
- 强否定断言的门槛应高于肯定断言：肯定错了是漏报，否定错了是**破坏性结论**。

相关 [[ticket21-recompute-corrections-20261002]] [[feedback-negative-existence-claims]] [[feedback-verifier-shares-failure-surface]] [[feedback-premise-laundering]]。