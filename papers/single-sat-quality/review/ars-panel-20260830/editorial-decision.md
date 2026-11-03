# ARS Panel 2026-08-30 — Editorial Decision(不可变 Revision Roadmap)

> 五席盲审(fresh full review)+ 主线程代码/数据/理论验证。五席互不可见对方报告;主线程持验证闸口结果做仲裁与去重。
> 上轮:ars-panel-20260815(R1–R18,2026-08-18 全闭)。本轮对照标注「新发」/「复发」。

## Panel 构成与来源

| 席 | 推荐 | MAJOR | MINOR | 备注 |
|---|---|---|---|---|
| EIC(期刊契合) | Minor Revision | 3 | 14 | 契合度无保留 |
| R1(方法论) | Major Revision | 7 | 8 | 复算约 40 处数字 |
| R2(SAR 领域) | Major Revision | 3 | 9 | 几何推导逐条验证 |
| R3(跨学科) | Major Revision | 5+1C | 5 | |
| DA(魔鬼代言人) | —(无判决权) | 4 | 5 | 攻击面 D 判「不成立」 |
| 主线程(代码/数据/理论) | — | — | — | 174 测试绿;verify gate 170/0;f2/f3 实现-公式代数等价;红线合规 |

## 编辑判决:**Major Revision**

裁决依据:四席推荐 Major;多处 MAJOR 需要补充计算或数据对齐(非纯措辞);无 DA CRITICAL,但 R3 唯一 CRITICAL(45° squint 包络承重)经 R2 独立几何推导验证成立(见 N1),按 IRON RULE #4 记为 validated,支持 Major 判决。**各席一致认为:实证结论方向不动摇,无 CRITICAL 数据造假/方向性错误;修复集中三条阻塞束 + 一批对齐项,不需要推倒。**

## 共识簇(去重后;括号内为独立发现席)

### 🔴 阻塞束 B1 — 摘要/正文归因与 overgeneralization(措辞级,但摘要独立传播)
- **N1(复发深化,R3 CRITICAL + R2 M1)** 45° squint 包络:①「文献报告范围」无引用,据 R2,现役 Stripmap 偏航导引压 Doppler 中心,45° 斜视非已演示运行模式;②R2 几何推导:C1 上限下有效包络仅 ~38°(cos ξ = cos θ_elev·cos ψ_sq ⇒ ξ ≥ ψ_sq;θ≤47° ⇒ ξ≤41.3°;联合 θ≥18° 得 |ψ_sq|≲38°),45° 声明装饰性。上轮 R12 加了 capability-superset 限定语,本轮两席认定不足。**修复**:声明有效包络(一句推导)+ 引用或删除「文献范围」;见 B3 敏感性实验决策点。
- **N2(新发;EIC M2 + DA #1)** 摘要 +41% 归因句:"adding the radiometric objective lifts…" 把 MOEA-2 搭车效应(+32%)记功于 f3 目标(受控边际 +7%)。改求解器级措辞(MOEA-3 raises…)或并列 +7%。
- **N3(新发;R1 M7)** 摘要/结论 "all solvers converge to the greedy coverage anchor" 与 G-SM 数据(f1*=0.29/0.37)矛盾 → "all **multi-objective** solvers"。
- **N4(新发;EIC M3)** §6.4 两处 "density-independent residual correlation"(L1092–1095, L1130–1132)与核心卖点 "density-dependent" 直接矛盾 → 改 "negative at all densities, strongest at sparse density"。
- **N5(新发;DA #5)** "indistinguishable" 与自家 S4 配对检验(p=4.5e-3 过阈)相抵 → "practically indistinguishable in class means (a trace per-scenario advantage persists)"。
- **N6(新发;DA 替代解释 1)** 摘要 +41% 叙事不提 G-SM 同密度 +45%(f3 全四档压 MOEA-3)——多目标真实卖点是「15% 而非 49% 覆盖代价取得 f3 增益」,摘要未讲。与 N2 一并改写。

### 🔴 阻塞束 B2 — 数字/描述与数据对齐(根因:表格非脚本化,上轮 R7 同类复发)
- **N7(新发;R1 M2 + EIC M1 + 主线程,三重独立互证)** GA-P-BL「逐场景与 G-BL 数值相同」被自家数据否定:statistical_results.json greater=1/equal=199;S1-D_seed04 GA f1*=1.1351(+13.5%);Table 2 S1 自身 ±0.02。五处强声明(L125, L368, L596 "on every scenario", L711 "tie by construction", L1436 "always triggers")→ 统一 "identical in 199 of 200, never worse by construction"。连带核查 §5.3 Friedman「tie」论证与 N5 相关句。
- **N8(新发;R1 M4)** 包络 −0.97 描述错位:−0.97 是 C1 过滤后值(c7=397,423 点);未过滤实为 −0.89~−0.93,"essentially unchanged" 不成立;未过滤样本 |ψ_sq| p95≈63° 与 45° 包络表述矛盾。该数进摘要/贡献3/结论。**数值本身有支撑**,改描述:分报 all/c7 两值与点数,说明窗口生成过滤关系。
- **N9(复发同类,上轮 R7;R1 M5 + 主线程 gate 仲裁)** Table 2/5 成组末位漂移:S1 MOEA-2 f2 ±0.059(数据 0.055)、f1* ±0.14(0.135)、S2 f1* 论文内三值 0.99/0.985/数据 0.981、Table 5 S7/S8 行错位嫌疑、"+7%"(现 +6.2%)、44%(45.3%)。verify gate 容差 0.006 吸收漂移(gate 工作正常,但按容差放行)。**修复**:表格脚本化重生成 + 论文内表间一致性;gate 增加「末位一致」严格档断言(容差 0.0005)。
- **N10(新发;EIC minor1 + R1 M6)** 消融规模自相矛盾:主文 "200 scenarios per variant"(L152–153, L752–754)vs 消融节 "six classes × 50 = 300 runs";ablation_summary.csv 实有 S1–S6,S5/S6 全文未定义且其 D 变体显著(−16.9%/−8.4%)未报告未解释。统一口径 + 定义 S5/S6 或说明省略理由。
- **N11(新发;R1 M1)** 「Cliff's δ」实为配对符号统计 (W−L)/n,非经典逐对 δ;Romano 阈值为后者标定。HV 对比两算法差 7 倍(−0.56 vs 0.08,分类翻转)。多数 "large" 判定同档,结论方向不变。**修复**:§5.3 写明所用公式,或改经典 δ 重算并核对分类。
- **N12(新发;R1 M3)** HV 归一化描述不可复现:按所述全局基复算 = 观测值 ×5.9(稳定因子 0.17),疑似逐场景池化。给出确切代码/bounds,或改描述并讨论影响。

### 🔴 阻塞束 B3 — 物理可行性与机制证据(含作者决策点)
- **N13(新发;DA #2,最重新发现)** +7% 边际(核心主张②唯一定量证据)存在**选择规则混淆**:MOEA-2 knee 最大化 f1+f2(对 f3 盲),MOEA-3 knee 最大化 f1+f2+f3(照顾 f3)。**修复(必须)**:统一选择规则重算 S1 MOEA-2 vs MOEA-3 差距;此题不修主张②定量链悬空。数据在手,计算成本低。
- **N14(新发;DA #4)** 机制归因(低 squint 收敛→衰减)缺最决定性干预证据:消融 B/C 的调度内 f2–f3 相关未报告;且存在未排除替代解释——密集档 f2 值域压缩(0.014)机械衰减相关。**修复**:用现成 no_squint/no_incidence 快照算 B/C 调度内相关;若不可算则降格措辞为观察性推断 + 明确列该替代解释。
- **N15(新发;DA #3)** 预算对照只验 f1*,未验「质量增益 <2%」的预算稳健性;无收敛曲线佐证 200 代收敛。**修复(二选一)**:双倍预算补报 A/D 的 f2/f3(若快照含);或摘要级主张加 "under the tested budget" 并在 §6.6 说明。
- **N16(新发;R2 M2)** 大斜视成像可行性未建模:Doppler 中心 f_dc≈280kHz·sinψ(调度结果 16–24° ⇒ 77–176kHz,vs PRF 1–4kHz 量级)、方位增益 roll-off、大斜视方位处理——均随 squint 变化,破坏「platform-constant」排序辩护。**修复**:§3.2 加理想化声明段;与 N1 联动。
- **N17(新发;R2 M3)** 30s dwell 与单时刻质量缺口:dwell 内 squint 漂移可达 20–60°(与调度所用范围同量级);质量取值时刻(start/mid/mean)未声明;C1 是否全程 [t, t+30s] 成立未说明;**内部矛盾**:「窗口 spanning several minutes」(L685–686)vs「窗内 squint 扫 20–35°」(ablation L118–120)几何上不能同时成立(报告实际分布,统一两处)。
- **N18(作者决策点;R3 2.1 + R2 M1)** 窄 squint 包络敏感性实验(S1 × {15°,25°},三配置,约 300 runs):做 → 应用结论获得真实平台适用域;不做 → §7.2 sparse 推荐显式降格「仅适用宽 squint 包络」+ 增益随包络单调收缩的机理论证。**必须二选一。**

### 🟡 S 级(强烈建议,低成本)
- **S1** 消融 B/C 调度内相关(N14 的具体化,若快照可算则一石二鸟)
- **S2** §5.3 knee 选择器敏感性补 best-f2/best-f3 选择器 + S1 下端 0.025 更正(R1 minor2)
- **S3** §7.2 重写为可执行决策表(密度 × 包络 × 资源 → 配置 + 选择点 + 回退),补 +12.5%@零覆盖代价选项(R3 2.5);时效性:补 acquisition-latency 分布或删 latency-favorable 表述(R3 2.2)
- **S4** 均值目标尾部风险:报 per-schedule 最差 10% f2/f3;§7.2 加「质量增益不定向于高优先级目标」警示(R3 2.4 + DA 利益相关者 1)
- **S5** 控制实验披露补全:热启动样本选择规则、σ 扫描 n_ref_dirs=12 vs 主实验 H=13、σ 扫描仅 S3 的推断范围限定(R1 minor3)
- **S6** Bonferroni 检验族说明(消融 12 检验 vs 10);Wilcoxon 去零有效对数(R1 minor1/4)
- **S7** 「operational density」命名:给文献锚或改 "high density";§7.4 补动态到达/滚动时域条目(R3 2.3)

### 🟢 T 级(打磨,一次性清单)
主文:L446–447 cos ξ 方向写反(R2)⬥ L340/L1086 交叉引用错(EIC)⬥ L916–917 "coverage advantage"→deficit(EIC)⬥ L688/L1233 流程语言泄漏(EIC)⬥ L233–236 "Chinese-affiliated" 国籍分类删除(EIC)⬥ Pareto-sufficient 死定义删除或脚注(EIC/DA)⬥ NESZ/NSGA-III 摘要内展开(EIC)⬥ "trading freedom"(L148)、"scales as ∝"(L1352)、+12.5% 首现补 "in f2"(EIC)⬥ Fig./Figure 与 §/Section 统一(EIC)⬥ G-BL 别名收敛至 1–2 种(EIC)⬥ GA-P-BL≡G-BL 六次重复压缩(EIC)⬥ 「five smallest random seeds」→"seeds 0–4"(DA)⬥ r_null 措辞 "validating the closed-form integrals"(DA #7)⬥ θ_elev 命名/ordering 声明收窄 "fixed-squint cross-track ordering"(R2)⬥ 被抑制 sinθ 因子方向补一句(保守方向)(R2)⬥ 零多普勒平面 vs 迹向平面脚注(R2)⬥ r_null 矩形按联合包络截断(R2)⬥ 光学迁移 GSD 形式修正(1/cos² 非 1/sinθ)(R2/R3)⬥ ±608km/±5.5° 几何配对统一(R2)⬥ 消融 B 的 f2 −6.2% 显著未述、25% higher 口径统一(R1)⬥ Table 6 补 SD 或注省略(R1)⬥ 稀疏边界口径统一 N≲100(cover letter/highlights/正文)(EIC)⬥ highlights MOO/G-BL-seeded 展开 + bullet2/5 合并(EIC)⬥ Acknowledgments/Funding 资助重复删一(EIC)⬥ 贡献1 拆句(EIC)

### 🔧 工具/仓库债(非稿件)
- `small-paper-ijae.bib` Peng2019Orienteering 标题截断 + 漏 Xing/Vansteenwegen 两作者(主线程经 ScienceDirect/SMU InK 实锤;实际标题 "Agile earth observation satellite scheduling: An orienteering problem with time-dependent profits and travel times")
- Das–Dennis/HV/NSGA-II 原始文献补引;§2.2 补 Moreira et al. 2013(R2)
- `reference/sar-domain-knowledge.md` f2/f3 角色与论文/实现互换(文档滞后:f2=NESZ→应为几何;f3=方位→应为 NESZ);红线引用的几何约定部分不受影响
- `src/tools/check_refs.py` 不跟进 `\input`(sec:ablation/tab:ablation 误报)
- verify gate 增「末位一致」严格档(N9);发布正文数字→数据字段映射脚本(R1 minor8)

## 与上轮(0815 panel R1–R18)对照
- **复发同类**:N9(数字漂移,R7 同根——修了 HV 表,Table 2/5 未脚本化)、N1(R12 深化——限定语被证明不足)
- **上轮修复经验证有效**:δ=+0.99 数字本身、80%/10%、N50=50、HV 表值、+7% 的统计量披露(R11)、−0.63/−0.72 basis(R8)
- **本轮全部为新一轮独立发现**:B1/B2/B3 各束在上轮清单中无对应项(除上述两复发)

## 判决执行说明
- 上轮投稿包(20260818 zip)对应稿件与本轮清单不兼容:B1–B3 清零前不投。
- 修复后按项目流程走 re-review(对照本 roadmap 逐项验证),verify gate 同步扩展后全绿 + 双编译过为闭合标准。
