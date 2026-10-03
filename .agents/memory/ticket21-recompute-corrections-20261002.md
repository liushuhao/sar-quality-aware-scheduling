---
name: ticket21-recompute-corrections-20261002
description: paper2 票21 独立复算推翻我两条论证——F1 桥接句不成立（Song 未给 sign(Ka)）与 F5「无等价脚本」误判（守卫是 pytest 不是脚本）；附带 F2 漏改两处源码注释
metadata:
  node_type: memory
  type: project
  originSessionId: db31c19b-4aa5-4c94-8c0b-5c9252951e97
  modified: 2026-10-02T13:49:53.029Z
---

2026-10-02 票 21 提交（`d38a844`）后，fresh subagent 独立复算推翻我两条论证。**判决不变，被推翻的是论证**。两条都已实测复核并改写 `formula-spec.md` §8.8。

**F1 论证错误（判决 p.3 仍成立）**：我曾用「§5 桥接句 `1−K_c/K_a≈A∈(0,1)` 反证 p.5」作第二依据。**不成立** —— Song 全文只在 `:287` 指名 `K_a` 为 "Doppler-modulated frequency"，**从未给出符号**；桥接式对 `sign(K_a)` 不敏感（取 p.5 只需同时假定 `sign(K_a)=sign(K_c)` 即自洽，**sign-neutral**）。我的错误是无据默认 `K_a>0`。**现仅以 Eq.(1) 代数立论**：`A=1−R_0k_θ/v_g`（`:156-159`）+ `A∈(0,1)` + `R_0,v_g>0` ⇒ `0<k_θ<v_g/R₀`，不依赖 `sign(K_a)`。附带好处：Eq.(1) 是精确式（无 ≈），故原先援引 Eq.(5) 的「近似不跨零」caveat 属多余，已删。
**教训**：用源文献里**另一个符号的符号**去论证时，必须先核该符号在源中是否给了符号；「未给符号」≠「符号为正」。

**F5 论证错误（改指而非仅删除）**：我写「全仓 0 命中且**无等价脚本**」——前半对（`numerical_check.py` 确无），后半错。守卫是 **pytest 不是脚本**：`tests/test_duration_models.py::test_identity_theta_a_over_A_equals_lambda_over_2rho`（`assert |θ_a/A − λ/(2ρ)| ≤ 1e-12·λ`，docstring 明写「Formula-spec §6 table 5」），实现 `sss_core/duration.py:63,158`。正确处置是**改指该测试**。我「grep `*.py` 找 theta_a 时命中的是 duration/geometry/modes/windows，没打开 test_duration_models.py 逐个看」——**grep 到文件名不等于读过内容**（同 `feedback-verifier-shares-failure-surface`）。

**F2 漏改**：除 spec 两处 + `platform_kim2021.json` 外，`sss_core/predicates.py:22`（写「three places」）与 `sss_core/duration.py:41`（写「p.7 / p.11」）也各带一个错数。同一注册数字散在**四处**，audit3 只报了其中三处。教训：修「某处计数错」时按**故障模式**全搜（四处都是同一数字的不同副本），不是按已知清单。

**F3 我的处置已正确**：subagent 建议「不要保留空指针、改指另一篇同样无 NESZ 的文献不构成核验」——我的写法正是删除空指针 + 保留 `[自推导待验证]` + 声明无外部源 + 要求 limitation 披露，未换名。已补强证据（`noise figure`/`SNR` 亦 0；`noise` 仅 `:143` SCNR/`:649` 矩阵 N/`:761` TBR/`:962` 参考文献）。

**已验**：四腿 grep 数字与 subagent 完全一致（4 处 25% / nesz=0 / `:287` 无符号）；回归 302 passed / 1 skipped / 1 xfailed。

相关 [[f1-song-sign-adjudication-20261002]] [[paper2-audit3-retarget-20261001]] [[feedback-verifier-shares-failure-surface]] [[paper2-deferred-debts]]。