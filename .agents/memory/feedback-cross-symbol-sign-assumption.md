---
name: cross-symbol-sign-assumption-needs-source-check
description: 用源文献里另一个符号的符号去论证前，必须核该符号在源中是否给了符号——「未给符号」≠「符号为正」，票21 F1 桥接句论证因此被推翻
metadata:
  node_type: memory
  type: feedback
  originSessionId: db31c19b-4aa5-4c94-8c0b-5c9252951e97
  modified: 2026-10-02T14:18:39.854Z
---

2026-10-02 票 21 F1（Song 2025 转向角速率符号自相矛盾），我裁「取 p.3」时给了两条依据。第二条是：「§5 桥接句 `1−K_c/K_a ≈ A∈(0,1)` 要求 `K_c/K_a>0`，若取 p.5（速率负）则 `1−K_c/K_a = 1+|K_c|/K_a > 1`，任何量级下都不能逼近 A<1」——**这条论证不成立**。独立复算查明：Song 全文只在 `:287` 指名 `K_a` 为 "Doppler-modulated frequency"，**从未给出它的符号**；桥接式对 `sign(K_a)` 不敏感（取 p.5 只需同时假定 `sign(K_a)=sign(K_c)` 即自洽，**sign-neutral**）。我的错误是**无据默认 `K_a>0`**。

**Why:** 这类错误极隐蔽——论证本身自洽、符号演算干净、结论正确，只有前提是无据的。而且它**不会让结论错**，只让论证经不起复算/审稿；票 18 的 gate-review 那一轮若抓到，整条 errata 的可信度都要打折。判决（取 p.3）由第一条依据（Eq.(1) 代数）独立支撑，桥接句纯属多余论证——**多余论证出错比没有论证更糟**。

**How to apply:**
- 论证里出现「因为 X 是正的/负的」时，X 必须是**本篇直接给出的量**；若 X 来自另一符号、另一篇、或「物理上显然」，先去 grep 源里 X 的定义句，确认它**显式给了符号**。未给 = 未知，不能当正。
- 判「某矛盾分支不成立」时，优先找**只用该分支自身涉及的量**的论证（如 Eq.(1) 直接解出 k_θ 符号）；跨符号论证可作旁证，但必须标「依赖未证前提」。
- 顺带收获：撤回该论证后，Eq.(1) 是**精确式**（无 ≈），所以原先附的「近似不跨零」caveat 也成了多余——**一条错论证会连带长出多余的防御**，删掉它要连带复查。

相关 [[f1-song-sign-adjudication-20261002]] [[ticket21-recompute-corrections-20261002]] [[feedback-premise-laundering]] [[feedback-instrument-measurement-traps]]。