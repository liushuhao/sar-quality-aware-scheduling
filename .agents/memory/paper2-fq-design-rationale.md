---
name: paper2-fq-design-rationale
description: paper2 f_Q/时长耦合设计问答沉淀（2026-09-26 用户同意 A 案）——f_Q 调度敏感通道真实含量、T 派生=需求最小时长、g_T×AASR 窗内张力、多星→Ch5 钩子
metadata:
  type: project
---

2026-09-26 D6 裁决问答轮（用户三连问后同意 A 案 ach 口径，ledger #57）。设计澄清五条，写论文/实现时按此口径：

1. **f_Q 调度敏感通道的真实含量**：coarsest-sufficient 映射下 ρ_a,ach ≈ 需求值（差档位余量），req→ach 本质是「档位余量的静态逐任务重加权」；f_Q 里真正调度敏感的模式物理只有两个——g_T(T(t_i)) 通道（SLS 显著）+ AASR(ψ̄(t_i)) 硬约束。论文贡献句「逐模式指标进目标维」按此真实含量写，勿写过头。
2. **T 派生 = 需求最小时长**：决策空间无时长基因，SPT 时长由需求反推/STR 波束通过/SLS 公式算出，无「多驻留换质量」选项——「需求 T_min vs 质量想更长」冲突在现决策空间结构上不存在，只在时长成为决策变量的世界出现（Out of Scope = future work）。
3. **g_T×AASR 窗内张力**（SLS）：g_T 单调随 T（长驻留高分，推向大斜视角/窗边），AASR 硬约束 -13dB 在大斜视角谱折叠高危区对顶（推向窗中）——窗内真实物理张力，是 feature。SPT/STR 沿窗 T 近常数，g_T 平坦。
4. **辐射因子构成**：q_rad = g_T/R³；1/R³ ≡ cos³θ/h³ = Ch3 f3 核原样迁移（条带关切），g_T 驻留增益是聚束/滑聚分化点（票 05 对照 Song 2025 钉形式，验不过退化 1/R³）。ρ_a,ach 与 g_T 同随 T 涨（同旋钮两表现），乘性聚合放大长驻留奖励——物理真实但论文须写明相关性，共线质疑出口 = D7 promotion 升三目标。
5. **多星多目标 → Ch5 钩子，不进本篇**：星间几何差使分配即质量决策，耦合价值放大——但查新按单星口径、Ch5 领地、归因卫生三理由不上本篇；写法 = Limitations/natural extension 一段（同时是 Ch5 设计钩子）。触发改判：正式实验量出单星耦合张力不足（W 档碎片化不显著/基线差距小）→ 多星作为 Ch5 立项论证而非本篇扩容。

**时长两几何通道**：沿轨向斜视角 ψ（tan 差式）+ 横轨向入射角 θ（R∝1/cosθ，L_syn∝R）——耦合比单一斜视角版更丰富，Kim SAT fixture/CN112330091A 启发式均为斜视角通道佐证。

相关：[[paper2-objective-delta-rationale]]、[[project-next-paper-squint-duration]]、[[symbolic-gate-deferred-ch5]]
