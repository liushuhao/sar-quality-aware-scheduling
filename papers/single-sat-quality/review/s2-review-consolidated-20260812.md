# S2 5 审稿人 full 综合（fresh full 全程审稿，2026-08-12）

## 面板

| 审稿人 | 裁决 | 分数 | 发现 |
|---|---|---|---|
| EIC | Minor Revision | 贡献 72 / 适配 78 | 5 MINOR |
| R1 方法论 | — | rigor 73 | 1 MAJOR + 9 MINOR |
| R2 领域 | — | 领域贡献 54 | 3 MAJOR + 5 MINOR |
| R3 跨学科 | — | 实用 55 | 5 MAJOR + 2 MINOR |
| DA | 2 CRITICAL | — | 2 CRITICAL + 5 MAJOR + 2 MINOR |

**综合裁决：MAJOR REVISION**（DA 2 CRITICAL 阻挡 Accept）。

## 三 P0（已对抗验证 + 修复中，见 rdr-066）

- C1 budget_control.json 缺失（§6.6 "not a budget artifact" 无支撑）→ 重跑中
- C2 hotstart 漏传 instance → 默认轨道，f2 基址错 3.8× → runner 修 + 重跑中
- C3 f3 NESZ 斜视双计 → Option 2 全高程面角（f2=sinξ_elev·cosψ, f3=cos³ξ）→ 代码修 f96674f + MOEA-2/3 重跑中

## 其余发现（~28 条，转 rdr-067+）

### 一致性 / 编辑类（数据独立，可先修）
| 来源 | 发现 |
|---|---|
| EIC-i + R1-MAJOR | f2 增益基数不一：摘要 +4.5% vs §6.3/§7.1/结论 +4.7%（pooled-ratio vs mean-of-ratios）；摘要 "~6%" vs §6.4 "~10%"（vs G-BL vs vs MOEA-2）——正文需解释基数 |
| EIC-ii + R1 + DA | GA-P-BL "五求解器" 过度声明 + never-worse guard 未披露 unguarded 结果（S1-D_seed04 +13.5%）；GA-P-BL 输出恒等 G-BL 未诊断 |
| EIC-iii + DA | NESZ 17% R³ 误差 → 排序稳健性未论证（现被 RDR-066 模型修正吸收，重跑后补误差带） |
| EIC-iv + R1 | 主实验种子策略/重复数未在正文声明（仅 control 有 seed） |
| EIC-v | §6.6 "dense S3" vs 摘要 "intermediate densities" 术语冲突 |
| R1-MINOR | NSGA-III 实现/版本未声明；消融 Δ% 从舍入表值不可复现；Pareto-sufficiency 阈值后验/武断；hotstart SD 有效 n = 场景数 |
| R2-MINOR | novelty 措辞 vs Wei2025 需软化（分解 vs 复合代理）；摘要过度泛化（饱和限于单平台/单 pass/固定轨道） |
| R3-MINOR | NP-hardness "intractable N≥20" 与所引 MILP 小实例工作矛盾 |
| DA-MINOR | N50 CI [30,62] 未入摘要；Table1 GA-P-BL S1 "1.00±0.00" vs 数据 1.003±0.019 |

### 方法类（需验证 / 部分数据）
| 来源 | 发现 |
|---|---|
| R1 | HV pooled 基含 G-SM（设 f3 max ~0.70）却从 Table 排除 G-SM；reference (0,0,0) = anti-ideal；Friedman χ² 含 GA-P-BL 重复组 → 4 distinct solvers per class；嵌套设计当独立；f2 头部缺 paired effect size；hotstart/random-search 小样本有效 n |
| R3 | slew 保真（单轴 ω_max 除全 3D LOS 角，无 ω_max/τ_settle 敏感性）；decoder 偏置（全进化求解器共享最早插入解码 → front compression 可能是 decoder 族属性）；无 runtime 不可操作；C3/C4 非绑定（5-7 阶富余）真实 SAR 能源/下行受限；f1* 归一化锚循环 |
| R2 | sinθ 地面面积因子 §3.2 重丢；30s dwell 移除主导辐射杠杆（已披露）；\|ψ\|≤45° 包络超真实平台 1 数量级 |
| DA | 饱和边界过度声明（G-SM f3=0.70 在 MOEA-3 前沿外，50/50 场景）；+58% 是 ordering-only 索引的量级声明（17% R³ 误差）；"~0.3 m" 对 +4.5% f2 过度（线性 ≈2.2% ≈0.12 m）；分解价值（S1 D 在 f1*/f2 胜过 A）；cherry-picking by variant（S1 f3 增益 +16.6%..+95.6%） |

## Gate M2（临时化）
S3 对抗验证：3 P0 全确认 → M2 视为 confirm-with-major（DA-CRITICAL 已验证，fix 路径明确 = 重跑）。修订完成 + re-review 后正式 close。

## 验证队列（R1/DA 要求数据文件）
- [ ] budget_control.json（重跑产出）
- [ ] hotstart 重跑后 f2 基址 vs Table2 一致
- [ ] G-SM 前沿外（DA "50/50 S4"）重跑后复核
- [ ] 消融 Δ% 从原始均值复现
- [ ] N50 CI、Friedman、pooled HV 复算
