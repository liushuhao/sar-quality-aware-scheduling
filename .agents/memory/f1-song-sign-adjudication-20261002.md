---
name: f1-song-sign-adjudication-20261002
description: paper2 票21 F1 裁决依据——Song 2025 自相矛盾取 p.3（代数自洽 + 规格自身桥接句反证 p.5），含实测行号与最弱环节
metadata:
  node_type: memory
  type: project
  originSessionId: db31c19b-4aa5-4c94-8c0b-5c9252951e97
  modified: 2026-10-02T11:44:14.705Z
---

2026-10-02 票 21 F1（Song 2025 转向角速率符号自相矛盾）裁决依据，**全部本轮实测**（`literature/fulltext/song2025_sensors_sparse.txt`，读法必须 `split('\n')`，该文件含 17 个 form-feed 页分隔符，`str.splitlines()` 会把页 1 之后行号全部移位）。

**两个矛盾句都是真的**（都能 grep 到逐字原文）：
- `:163-164`（p.3）"In TOPS, kθ is negative and A > 1, while in Sliding Spotlight and Mosaic mode, **kθ is positive** and 0 < A < 1"
- `:317-318`（p.5）"TOPS has a **positive** rate. Sliding Spotlight and Mosaic have a **negative** one"

**裁决：取 p.3，p.5 登记为源文献疑似符号笔误。** 两条独立证据：

1. **p.3 自洽**——Song Eq.(1) 就在 `:156-159`（距 p.3 那句 3 行）：`A = 1 − R₀k_θ/v_g`。代数 `0<A<1`（滑聚）⇒ `0 < k_θ < v_g/R₀`；`A>1`（TOPS）⇒ `k_θ<0`。p.3 的两个断言与它自己上一段的方程**逐条对得上**。
2. ~~**本规格 §5 桥接句反证 p.5**~~ —— **该论证已于 2026-10-02 被独立复算推翻并删除**。Song 全文只在 `:287` 指名 `K_a` 为 "Doppler-modulated frequency"，**从未给出其符号**；桥接式 `1−K_c/K_a≈A` 对 `sign(K_a)` 不敏感（取 p.5 只需同时假定 `sign(K_a)=sign(K_c)` 即自洽，**sign-neutral**），我的错误是无据默认 `K_a>0`。**判决（取 p.3）不变，现仅以 Eq.(1) 代数立论**，不依赖 `sign(K_a)`。详见 [[ticket21-recompute-corrections-20261002]]。

**同址附带发现（audit3 未报）**：`formula-spec.md:63` 把 `"$0<A<1$ in Sliding Spotlight"` 放在引号内当 Song 原文，该串全文 0 命中；原文是 `kθ is positive and 0 < A < 1`（不等式有空格、符号归 k_θ）。与 `KIM-eq12-13-bridge` 同类——渲染版被当原文回抄。已注册为 `F1-quote-reconstructed`（commit `41443e8`）。

**最弱环节（自审，rule 16，已更新）**：现论证只用 Eq.(1)（**精确式，无 ≈**）+ `A∈(0,1)` + `R_0,v_g>0`，不依赖任何其他符号的符号，故无近似 caveat。真正的残留不确定是**未能排除 p.5 谈的是另一个量**（而非笔误）——p.5 上下文在讲 AASR 式差异「arise from variations in the AAP」，未明说 rate 就是 k_θ；两段都名为 steering angle rate 故 subagent 判为同量，但「同量」这一步是语义判断而非形式证明。**翻判条件**：若找到同级第三方源明确给出滑聚 k_θ<0，重开 F1。

相关 [[paper2-audit3-retarget-20261001]] [[project-paper2-goal-card-handoff-20261002]]。
