---
name: paper2-audit3-retarget-20261001
description: paper2 audit3 换靶轮（求解器/fork/公式溯源/红队）——挖出前两轮漏的方法论层缺陷：注册统计检验零功效、promotion 无收敛标定、门禁不含本域套件、测试自指
metadata:
  node_type: memory
  type: project
  originSessionId: d0f5ed3f-b55c-4299-bd18-892a682b9298
  modified: 2026-10-01T00:32:37.343Z
---

2026-10-01 用户换模型后要求再跑一轮。**关键决策：换靶而非重复**——前两轮审的是
「实现 vs 登记自一致性」，换靶后审此前从未覆盖的四层。工件
`.scratch/sliding-spotlight-scheduling/audit3-20261001/`（4 份 verdict + DISPOSITION.md）。

**为什么前两轮 6 路零发现**（红队结构性答案）：审查对象几乎全是「代码 ↔ 冻结工件的
自一致性」。实锤问题全在代码**之外**的层——统计检验设计、预算混淆、谓词接线、
测试可证伪性。**结论：换靶比换模型更值钱。**

**实测确认的高优先发现**（主线程逐位复算，非转述）：
- **注册 primary_comparison 零功效**：锚播种进种群（nsga2.py:173，50/50
  `anchor_seeded=True`）⇒ `front_max ≥ anchor` 由构造保证；实测 **49/50 恰好相等**
  （第 50 个 +0.1）⇒ 全零差被 `zero_method='wilcox'` 丢弃 ⇒ **5/5 变体有效对 < 5，
  全部报 insufficient**。
- **promotion 无收敛标定**：散布随预算增长（M2WH 中位 0→0.025→1.917，5 seed 中 3 跳升；
  P7WH max 5.001 dB = 阈值 6.0 的 83%），而 prereg 原文写「dead-at-all-budgets ...
  established and expected to hold」。**与票 19/20 已定性的「前沿塌缩」同型失效**——
  前沿做了收敛标定，promotion 没做。不对称即缺陷。
- **门禁 PASS ≠ 本域测试绿**：`verify.py` 步骤 `shared_lib_tests` 跑共享库
  `src/tests`（145），**无步骤跑本域 `tests/`（127）**；矩阵 50 + 探针 45 从未过门禁。
- **测试自指不可证伪**：`test_aasr_grid.py:152` 把被测常量 `AASR_CELL_MARGIN_DB`
  写进自己上界 ⇒ 改常量两侧同变永绿。
- **NC 前沿含被支配解**（P0 定义符合/影响零）：全 STR ⇒ f_q 恒定 ⇒ 目标空间退化 1 维，
  pymoo `only_non_dominated_front` 下 ULP 级差异互不支配 ⇒ `M1NC_seed100` 40 条 = 2 点，
  37 条被支配。对注册指标零影响（max_f1* 不变 / HV 无实现）。
- **hv 指标注册但全仓无生产者**（主线程补）。
- **公式溯源 P0=0**：30 处文献标注全可解析，Kim Eq.2-29 逐符号复原零错位，幻觉引用 0。
  但 g_T 核对源是**空指针**（Song 全文 NESZ 命中 0）、`numerical_check.py` 被引用两处不存在。
- **fork 完整**：F-01 核真、未登记 fork 0（五路扫描）、D1 零修改、命名空间遮蔽 0。

**正面证据不变**：877 条解从 `starts` 独立重算 `max|Δ|=0.0`（f1*/f_Q/cv）。

**处置（用户 2026-10-01 拍板）**：
- **新建票 21**（formula-spec 勘误 blocking gate，T0，依票 18 先例）：F1 Song TOPS 符号自相矛盾 /
  F2 25% 裕度计数 4-vs-2/3 / F3 g_T 核对源空指针 / F5 `numerical_check.py` 死指针。
- **新建票 22**（分析设计前置，T1）：primary_comparison 重裁 + promotion 收敛标定。
- **票 15 `Blocked by: 18, 21`**（验收项 13 的 f_Q 独立复算依赖 F3 的真实锚）。
- **票 17 `Blocked by: 16, 22`**（v2 冻结直接消费票 22 裁决；顺序颠倒会冻结出不可运行的主检验）。
- 票 17 另加 5 项验收（hv 生产者或注销 / 门禁纳入本域套件 / NC 工件去支配解 /
  饱和≠收敛判据 / 保守谓词接线）。台账 #86-94。

**执行链更新**：`21 → 15 → 16 → 22 → 17`（21 与 22 可并行开工；15 等 21，17 等 16+22）。

基线 338984e，本域套件 127 passed / 1 skipped。

**Why**: 用户对状态不放心，换模型后要求再审；换靶策略证明「审未审过的面」有正期望值，
「重审已审过的面」是零。

**How to apply**: 执行链 = **21 → 15 → 16 → 22 → 17**（21 与 22 可并行起手；票 15 等 21，
票 17 等 16+22）。开工票 15 前先确认票 21 的 F3 已闭合（f_Q 复算需真实锚）。相关
[[paper2-audit2-full-review-20260930]] [[paper2-deferred-debts]] [[feedback-premise-laundering]]。
