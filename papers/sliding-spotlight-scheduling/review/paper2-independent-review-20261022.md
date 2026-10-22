# Paper2 独立同行评审报告

**稿件**：*Agile Sliding-Spotlight SAR Satellite Scheduling with Per-Task Resolution Requirements: The Cost of Tightening the Order*
**作者**：Liu Shuhao（单作者，哈尔滨工程大学）
**目标期刊**：Aerospace Science and Technology（Elsevier）
**评审日期**：2026-10-22
**评审对象**：`paper/main.tex`、`paper/main.pdf`（48 pp.）、`paper/sections/*.md`

---

## 0. 评审元信息

| 项 | 内容 |
|---|---|
| 评审性质 | 独立外审式评审，只读；未修改稿件任何文件 |
| 评审阵容 | 五席：期刊适配 / 方法论与统计 / SAR 领域 / 实践与跨学科 / Devil's Advocate，另加编辑裁决 |
| 证据基础 | 稿件全文与图；`experiments/v5_results/sweep_results.json`；30 个 scenario manifest；`analysis_prereg_v2.json`；`sss_core/` 关键实现；`refs.bib` |
| 数字复算 | `scripts/verify_paper_numbers_l8.py --paper main.tex`：rc=0，**74/74 复现，0 失配**；另独立复算 27 组 family×s 中位数、per-seed 覆盖、族规模、模式构成、地板阈值 |
| 独立性声明 | 评审结论不引用 `review/`、`archive/` 既有审计作为论据；仅在 §3.4 说明与已闭环内部决议的关系 |
| 局限 | 未重跑实验；SAR 物理链按稿件内部一致性核对（SAT 定义与质量方程已对照 Kim 原文与登记式，其余公式未逐式复算）；页码均指 `main.pdf` 的 PDF 页 |

---

## 1. 裁决与摘要

### 1.1 建议：**Major Revision（大修）**

**不直接接受**，因为标题级主张（"收紧订单的覆盖代价"）在三个独立维度上不成立：

1. **方向**：摘要报告的 4.15 / 2.36 pp 是"没有放松到最松点"的代价，不是"收紧"的代价。同一份数据里，收紧方向的代价是 R3H 26.0 pp（1.0→0.9）与 46.6 pp（1.0→0.8）、R1C 46.0 pp（1.0→0.9）。
2. **基线**："own saturation" 是同一曲线在九点网格上的 argmax。R1C 的饱和点就是订单点，代价因此恒为 0；R2F 的饱和点在网格边界 s=2.0；R3H 的"平台"与 s=1.4 只差 0.0018（一个优先级单位）。
3. **归因**：三族在任务数（20/46–50/99–100）与模式构成（100% STR / 0% STR / 41–54 个 STR）上完全共变，族间形状无法归因于订单轴。R3H 收紧侧损失中，约 96%（1.0→0.8）与 77%（1.0→0.9）可由 STR 地板排除解释，不是稿件声称的 dwell/transfer 机制。

**不直接拒稿**，因为内核是真实且少见的贡献：dwell 由模式与所选起始时刻内生决定，分辨率订单作为逐任务硬约束，物理链闭合可验证，数字台账 74/74 复现。上述三项缺陷主要落在"再分析 + 重写"，不需要推翻实验。另有一类独立的正确性问题（B7：印出的质量方程方向、SAT 展开、几何标签），修法廉价但必须在修回稿中清除。

**Reject 触发条件**：若修回稿只软化措辞（把 "cost" 改叫 "premium"、把 "single-orbit" 改掉），而不做 §4 的 P0-1～P0-4（方向双向报告、披露 ρ 带宽与地板算术、模式分解、三值判定），则应拒稿——因为届时标题、摘要与实验之间的缺口仍然存在。

### 1.2 一句话概括

> 这是一篇工程上扎实、复现性罕见地好的**平台与公式论文**，被包装成了一篇它并没有做的**一般性代价定律论文**；两者之间的差额，正好是七条阻断项。

### 1.3 七条阻断项（详见 §3）

| # | 问题 | 共识度 |
|---|---|---|
| B1 | 标题级度量方向与命名错位 | 4/5 席 + 数据复算 |
| B2 | "own saturation" 基线是曲线自身 argmax，网格依赖 | 4/5 席 |
| B3 | R1C s=0.8 的"10/10 不可行"是 `[2.5,3.0] m` 粗档与 2.4669 m 地板的算术必然，带宽在正文中从未披露 | 1 席 + 代码核对 |
| B4 | 族间混杂；R3H 机制未分解，地板排除占主导 | 4/5 席 + ceiling 复算 |
| B5 | C5 恒等式、"无违反"、477,308 是构造性/成员级重复计数，且对 STR 不成立 | 4/5 席 |
| B6 | 第三贡献"纪律性"不成立：预注册不覆盖标题度量；Table 1 的 R1C "met" 依赖正文明确禁止的零覆盖约定 | 3/5 席 + 预注册文件核对 |
| B7 | 印出的 f_Q,deliv 方程 cos²ψ 方向反了；SAT 展开错误；"single-orbit" 事实错误 | 领域席 + 原文/数据核对 |

B1–B6 是"主张与证据不匹配"，B7 是"印出来的东西本身错了"。两类都必须修，但 B7 的修法最便宜——它是勘误级，不是重构级。

### 1.4 三条主要优点（应在修回稿中保留并前置）

- **S1 物理链闭合且可核**：tan-exact dwell 闭包、θ_a/A = λ/(2ρ_a) 恒等式残差 3.5×10⁻¹⁸、planar-oracle 偏差 +0.4185%/+2.1%/+5.3%（12°/cap/45°），这些是真正的工程贡献。
- **S2 复现性**：74/74 数字复现；27 个中位数独立复算一致；"不可行 ≠ 覆盖为零"的区分贯穿正文、图与台账，且执行得很干净。
- **S3 诚实**：主动披露 anchor 在 258/260 单元最优、C1/C3 失败照报、上一世界的 tight-arm penalty 撤回、g_T 无外部校验、AASR 方向与文献相反。这在投稿中很少见，应保留。

---

## 2. 五席评审

### 2.1 期刊适配席（Journal-Fit）

**结论：marginal fit；Major Revision。**

- **范围在**：星上任务规划与 SAR 模式运用属于 AST 领域，AST 也已发表 SAR 任务调度（稿件 ref. [11]）。"客户的分辨率订单值多少服务优先级"是合法的系统/运用问题。
- **贡献类型不在**：AST 研究论文通常给出有增益的方法，或可推广的设计/分析结论。本文两者都主动放弃——明确声明不作复杂度主张、搜索只是"测量仪器"、模式分配冻结、模式-时间联合分配留待未来。剩下的是一维敏感性扫描。
- **文体不在**：稿件按项目审计组织（preregistration / caliber registry / L8 world / formula-spec §8.17-9 / amendment / withdrawn）。对 AST 而言，这是把过程置于工程结论之上。
- **换刊不是解法**：SAR/遥感刊更差——没有真实数据、没有成像处理、没有标定辐射，AASR 方向与文献相反且无判别实验。AST 或 Acta Astronautica / Advances in Space Research 是合适去处，但必须改写成调度/系统贡献。
- **可转移的洞见被埋没**：真正对 AST 读者有用的是"收紧订单是付出覆盖、还是摧毁可行性，由模式构成决定，而不是由优化器决定"。稿件的 R1C 断崖（1.0→0.5398）、R2F 平台（0.9764→0.9764）、R3H 中间态（0.9485→0.4827）已经把这件事说清楚了。§6.1 p.29 那句"tightening ... costs about half of the served priority mass; loosening ... buys back under five points"才是应该进摘要的句子。
- **最接近的 SAR 区域观测调度文献未引用**：`refs.bib` 中已有 `liu2025a`（SAR regional observation, Aerospace Systems 2025）、`shen2024multistrip`（IEEE TGRS 2024, multistrip stitching）、`xin2024sar`（SAR 多星协同区域观测）、`li2026efficient`（regional SAR reconnaissance windows），`main.tex` 对四者引用次数均为 **0**。这不是"文献少"的问题，而是"最近的先行工作在手边却没接上"。

### 2.2 方法论与统计席（Methodology）

**结论：Major Revision。**

方法论席做了大量独立复算，以下为其通过复核的核心项：

- **"十个 seed"是十个不同场景，不是十次求解重复**。R2F 逐 seed 接纳数为 46/50/49/50/49/49/50/49/50/48；R3H 为 99/99/100/100/100/99/100/100/99/99；R3H 的 STR 数在 41–54 之间变动。稿件写的"46 admitted""99 admitted""342/753 windows"分别只是 seed 200/300 的单次取值（我复算：R1C 145–162 窗、R2F 337–391 窗、R3H 731–779 窗）。
- **求解器种子与场景种子同源**。`run_matrix.py:341-357` 从 manifest 文件名解析 `seed_s` 并原样传给 `run_pilot.py --seed`，而 `run_pilot.py:116` 把它交给求解器。于是"场景抽样噪声"与"搜索随机性"在设计上不可分离；§5.3 的"nine views of one world"（p.27）只在单个 seed 内为真，作为族级描述是错的。
- **摘要的两个成本都在噪声量级附近**。对 10 个场景做 20,000 次 bootstrap：R2F s=1.0 中位数 0.9764，95% CI [0.9689, 0.9958]；s=2.0 为 1.0000 [0.9886, 1.0000]；两段区间大幅重叠。R3H s=1.0 CI [0.9308, 0.9562]，s=1.5 CI [0.9680, 0.9963]。配对后 R3H 的 4.15 pp 方向稳健（10/10 场景为正，符号检验 p≈0.001，配对中位数 3.97–3.98 pp），但 R2F 的 2.36 pp 配对中位数只有 0.93–0.94 pp，约为头条值的 40%。
- **两个 Pearson 相关系数都不成立**。r=0.329（n=26）去掉 R1C s=0.9 单点后变为 **−0.070**（n=25），Fisher 95% CI [−0.067, 0.635]，双侧 p≈0.10；r=0.249（n=260）把九档压成 30 个场景均值后为 **0.028**（n=30）。且两者都跨族合并，直接违反稿件 p.26 "index levels are incomparable across families and are never pooled" 的自定口径。数字门禁也不覆盖这两个数（脚本中无 Pearson 路径）。
- **机动时间模型不连续且非单调**。p.17 的 hybrid 规则是"解析值 ≥ 0.5×1.84 s 时用解析值，否则退回 4.07 s"。于是 0.50 s 的机动被计为 4.07 s，而 0.95 s 的机动被计为 0.95 s。`anchor.py:384-385` 自己写明锚点典型跃迁 dψ≈6.45 mrad 的模型值为 **0.46 s**，恰好落在 fallback 区。C2 是本文的绑定约束（p.18），所以这个 4.4 倍跳变直接进入所有覆盖读数。稿件既未报告 fallback 触发频率，也未做 pad/settle/PRF/AASR 敏感性。
- **EA 的贡献由作者自己的数字否定**：258/260 单元 anchor 即最优；两个例外是 R1C s=1.0 的 seed 100/105（+4.27/+4.63 pp），恰是 anchor 失手处，说明 anchor 不是"optimal"而是 "best found"。另外 front size 在 233/260 单元等于种群规模 40，"tie-set" 实际是保留种群；f_q 的"全体成员均值"因此依赖种群规模；`search_only_max_f1_star` 在所有 artifact 中为 `null`，不是测得的空集。
- **K1–K3（稿件称 C1–C3）判定无容差**：R2F 的两次"下降"为 0.268/0.359 pp，小于一个优先级单位（0.38 pp）；配对后 8/10 场景差值为 0.0000，配对中位数 0.0000。R2F 的 C3 "失败"是一次精确平局（0.9764 vs 0.9764）。判定在平局上翻转，不是检验。
- **477,308 是成员级重复计数**：等于 9,430 条 front 记录的 `n_selected` 之和；每单元最佳方案的 distinct 任务数合计 13,845，前者是后者的 **34.5 倍**。稿件定义没错（p.34 明确"not a distinct task"），但把它放进摘要与结论就变成了交付量陈述。

### 2.3 SAR 领域席（Domain）

**结论：物理层可用，解释层不可用；Major Revision。**

**经核可用的物理层**（这一层比同类投稿更扎实）：

- 平台常数自洽：D = λ/θ_a = 4.9338 m、R₀ = 775.4 km、r₀ = 197.119 km、A = 0.20268、k = 0.79732；r₀ 与 R₀ 的区分正确且全文一致——这是很多 SAR 调度论文会弄错的地方。
- tan-exact Kim 闭包优于 planar oracle；oracle 偏差 +0.4185%（12°）与 +2.1%（SLS cap）符号与量级正确；θ_a/A = λ/(2ρ_a) 恒等式残差 3.5×10⁻¹⁸。
- 模糊积分排除 m=0 是正确约定（含入会使 AASR ≥ 1 恒成立）；STR 与 SLS 经谱压缩后严格相同（领域席逐点复现），SPT 的斜视不变性是结构性的，不是拟合。
- 台账纪律（预注册网格、caliber 标签、每点十 seed、不可行与零分离、raise-not-score）是少见的好实践。

**解释层问题**：

- **F1 方向**（同 B1）。
- **F2 机制句与场景构成矛盾**（同 B4）。领域席给出 C5-only 上界：s=0.8 为 0.5007、s=0.9 为 0.7484、s=1.0 为 1.0000；据此，地板通道在 s=0.8 "过度解释"了整个 46.6 pp 断崖，而 C2/anchor 残差在收紧时反而**改善** 3.35 pp。这与 §6.3 "spends dwell ... until it collides with the transfer constraint" 的方向相反。
- **F3（新，阻断）方程方向错**：p.14 印出 f_Q,deliv = D / (2 ρ_req² cos²ψ_sel ρ_rg)。但 §3.3 已登记 ρ_a,ach = ρ_a(0)/cosψ——斜视使 ρ_a 变大、质量变小，cos²ψ 应在**分子**，或按 C5（交付 = 订单）干脆不出现。按现式，cos²ψ<1 反而把 f_Q 放大，而 §6.5 又把 1.3286>1 称作 "squint-loss factor"：等于把 24.7% 的损失印成 32.9% 的增益。修正后同一格约为 28.3 m⁻²，而非 37.62。
- **F4 质量指标是分辨率的代数重写**：由 g_T(m)ρ_a(m) = D/2 得 f_q ≡ D/(2ρ_a²ρ_rg)（R=R₀），三个常数 0.8107/19.7352/54.8322 由此精确复现；24.3× 与 67.6× 就是 (2.4669/0.5)² 与 (2.4669/0.3)²。于是"模式间差数量级"只是"模式分辨率不同"，Fig. 4 的三条平线是构造必然，不是发现。
- **F5 速度约定名不副实**：7578.05 m/s 是**卫星惯性速度**，不是"场景速度"——场景不会以 7.58 km/s 运动。领域席按 ECEF 足迹速度复算为 7220–7229 m/s（低 4.8–5.0%）。这使 W_a/v_s 与 SLS/SPT 的 dwell 分母偏短 4.8–5%，逐任务占用率变化 1.5–3.5%（与 4.15/2.36 pp 同量级）；AASR 在 0° 由 −21.35 变为 −23.50 dB，0°→26° 的对比由 1.97 dB 减半为 1.07 dB。稿件披露了"覆盖读数继承该约定"（p.8），但全文无敏感性。
- **F6 方向对比不可比、且对结果无后果**：Song et al. 的平台在阵列（稀疏 vs 均匀）、PRF（1150/2300 vs 3630 Hz）、幅宽（45/90 km vs 5 km）、扫描角（±3.5° vs 26.9°）上同时不同；§2.1 称其为 "a result of this paper"，§7.2 自己却写 "not a measurement that refutes the anchor"。更关键的是：**30 个场景 manifest 的 removals 合计为 aasr=0、footprint=0、below_finest=0、no_window=15**——AASR 门槛在全部已发布场景中未移除任何任务，因此这个方向对比对任何可行性判定都没有作用。
- **F7 SAT 展开错误**：稿件把 SAT 展开为 "saturation-avoidance time"；Kim et al. 2021 原文（项目内 `literature/fulltext/kim2021_aerospace_fulltext.txt` 第 236 行）定义为 **synthetic aperture time (SAT)**，全文无 "saturat" 词根。且该展开与本文自己的 "saturation arm" 语义相撞。
- **F8 "single-orbit" 错误**（同附录 A.3-1）：R1C 跨 70.3–72.0 h（3 天）、145–162 窗、7.3–8.1 窗/任务，约 44–45 圈；且与 p.36 "the registered serial bound is defined per pass, not per orbit" 自相矛盾。原意应为 single-**satellite**。
- **F9 无同实例的固定 dwell 对照**（→ P1-8）。
- **F10 五个约束族只有一个真正绑定**：C1 是生成侧窗口过滤；C3/C4 自认 "structurally never binding"；C5 是 raise 型恒等式；AASR 在已发布数据中移除 0；真正绑定的只有 C2 与 STR 地板。摘要与 §3.4 应说明这是**单约束排程序**，而不是"五约束调度器"。

领域席另列 MINOR：f_ac 省略的论证是 non sequitur（DC 相对变量替换只在完整混叠和上精确，而实现截断于 N_ALIASES；345.7 kHz = 95.2×PRF 不能同时作为"可省略"的理由）；SLS 的 26.9° cap 与 a_res=1−k/cos²ψ 的零点 26.7567° 只差 0.1433°，来源未说明；"no external literature source carries the NESZ equation set" 不实（Curlander & McDonough 1991；Cumming & Wong 2005 已在其文献表中）。

**缺失文献（每条对应一个具体主张，不是凑引用）**：

- **L1 敏捷 EOS 调度基础**（对应 §2.2 "duration 是调度前属性"的断言，现仅 2 条支撑）：Lemaître et al. 2002（AST 6(5):367–381，就在本刊）、Bensana et al. 1999、Vasquez & Hao 2001。
- **L2 可控加工时间调度**（对应本文的核心结构迁移）：Shabtay & Steiner 2007、Alidaee & Womer 1999。引这条线会把"新问题类"准确降格为"领域实例化"，反而更稳。
- **L3 SAR 模式/模糊/辐射标准**：De Zan & Guarnieri 2006（TOPS）、Moreira et al. 2013（tutorial）、Curlander & McDonough 1991。
- **L4 `refs.bib` 中已有但未引的 SAR 调度工作**：`shen2024multistrip`、`xin2024sar`、`liu2025a`、`li2026efficient`、`liu2017an`、`wang2020robust` 等。

### 2.4 实践与跨学科席（Perspective）

**结论：Major Revision。**

- **对调度值班员：不可用**。没有运行时间、没有下行/地面站、没有动态到达、没有重规划、单星、合成需求模板、均匀随机优先级（p.24 自认"not a measured campaign profile""no physical provenance"）。即使完美求解也不是可飞行的计划。
- **对任务设计者：只有一句定性结论可用**——收紧陡、放松平，且不对称；这正是 p.29 的那句话。但头条 4.15/2.36 是"从松端回看"的差，且稿件自己说各族"comparable to nothing but itself"（p.31），摘要却把三个数并列。
- **对研究者：有用**。负结果（anchor 在 258/260 单元即最优）与"构造 vs 搜索"的分离告诉社区：难点在接纳与 dwell 闭包，不在元启发式搜索。
- **"平台"名不副实**：C3/C4 "structurally never binding"（p.18），功率/热/存储是装饰；SAR 真正绑定的资源是数据量与下行。按稿件自己的 C4 常数，1 s dwell ≈ 27 MB，4 s 示例 ≈ 108 MB/任务，99 任务 ≈ 10.8 GB（未压缩），这个数字全文没有出现。速度约定（p.8 用惯性速度作地速）会系统性偏移绝对 dwell 数个百分点，稿件披露但未量化。
- **"cloud-cover attrition" 对 X 波段 SAR 是范畴错误**（p.37），暴露了从光学 EO 模板继承的 scope 清单；应改为降雨/电离层/RFI 或删除。
- **跨学科机会**：雷达资源管理（dwell 调度、QoS 接纳）、时间依赖调度理论（已引 Gawiejnowicz 却未用其理论）、带 sequence-dependent setup 的加权区间选择/RCPSP、容差-成本工程（"order 是容差、dwell 是工时、coverage 是良率"——这是最贴切的重构）、观测-下行联合调度、商业 SAR 任务书。均可在 Related Work 中用一段接上。

### 2.5 Devil's Advocate

**结论：Major Revision；若三项核心分析不做，则 Reject。**

其最强反驳可归纳为一句：**头条量不是"收紧订单的代价"，而是"没有放松订单的代价"**。据此给出四条 CRITICAL：

1. **方向反了**（同 B1）。
2. **"own saturation" 不是物理饱和**，是同一曲线在任意九点网格上的最大值；网格截到 1.5，R2F 的"代价"就变成 1.96 pp；网格延到 3.0，R3H 可能变化。R1C 的 0.00 是构造性的。
3. **设计与模式构成混杂**：三族在任务数与 STR 占比上完全共变，曲线形状的顺序恰好是 STR 占比的顺序。STR 在 R3H 中占优先级 41.4–61.0%（median 50.1%），s=0.8 的观测值 0.4827 与这个天花板几乎相等——收紧侧"塌陷"主要是"约一半任务在地板处变成不可接纳"，不是 dwell 冲突。
4. **C5 是参数化，不是约束**：违反即抛异常，完成运行不可能有违反；"max cv = 0.0"是验收测试的定义，不是观测。且恒等式对 STR 不成立（STR 交付 2.4669 m 地板、无任务级参数），R1C 20/20、R3H 54/99 都是 STR。

其 MAJOR 另补充：单侧度量（收益侧未测）、"single-orbit" 事实错误、十 seed 是十场景且无区间、EA 仅 2/260、"预注册不覆盖头条量"、C1/C2/C3 命名冲突、27 篇文献支撑"near-universal"过强、摘要/篇幅/术语、从三族过度概括。

其"非缺陷观察"与我的判断一致，应保留：坦率披露、不可行/零的区分、形状准则失败照报、两次局部下降的逐 seed 归因、dwell 闭包、符号纪律（r₀ vs R₀）、不夸称算法复杂度。

---

## 3. 编辑裁决

### 3.1 共识表与独立核验

| 编号 | 问题 | 提出席 | 我的独立核验 | 判定 |
|---|---|---|---|---|
| B1 | 头条度量方向与标题相反 | DA, Persp, JF, Meth | 由 `sweep_results.json` 直接复算：R3H 1.0→0.9 = 26.01 pp，1.0→0.8 = 46.58 pp；R1C 1.0→0.9 = 46.02 pp；R2F 1.0→0.8 = 0.00 pp | **成立（阻断）** |
| B2 | "own saturation" 是网格 argmax | DA, Meth, JF, Persp | R2F 饱和点在网格边界 2.0；R3H 0.9900 与 1.4 的 0.9882 差 0.0018 = 一个优先级单位；R1C 订单点即饱和点 | **成立（阻断）** |
| B3 | R1C s=0.8 不可行是算术必然，带宽未披露 | Meth（+ 我的代码核对） | `sss_core/scenarios.py:13` 冻结粗档 `[2.5,3.0] m`，注释明言"ENTIRELY inside the STR routing tier"；0.8×3.0 = 2.40 < 2.4669；正文全文检索不到 `2.5`/`3.0 m` 带宽 | **成立（阻断）** |
| B4 | 族间混杂 + R3H 机制未分解 | DA, Persp, Meth, JF | 三族 N 与 STR 数完全共变（20/20STR、46–50/0STR、99–100/41–54STR）；我复算非 STR 优先级份额中位数 0.5007，s=0.8 观测 0.4827（差值 1.8 pp）；s=0.9 天花板中位数 0.7484，观测 0.6884（差值 6.0 pp） | **成立（阻断）** |
| B5 | C5/无违反/477,308 是构造性陈述 | DA, Persp, Meth, JF | `verify_paper_numbers_l8.py:244` 显示 477,308 = Σ front[*].n_selected；distinct 任务数为其 1/34.5；STR 无任务级参数 | **成立（阻断）** |
| B6a | 预注册不覆盖头条量 | DA（+ 我核对 `analysis_prereg_v2.json`） | 原 freeze 2026-10-03 的主估计量是 `dq_all`/quality headroom，预算梯 160/240；2026-10-21 修正案才 "REGISTERS the L8 main result"（coverage–demand curve），晚于 2026-10-20 的 L8 sweep | **成立（阻断）** |
| B6b | Table 1 的 R1C C3 "met" 依赖被禁止的约定 | JF, Meth, Persp | p.31 明写"That is not a coverage of zero, and the two must never be interchanged"，同一页又说该单元"enters the criteria as the zero-coverage outcome"；p.31 自认"under an exclusion convention ... the verdict would carry no value" | **成立（阻断）** |
| B7a | 印出的 f_Q,deliv 方程 cos²ψ 方向反 | Domain | p.14 印式 `f_Q,deliv = D/(2 ρ_req² cos²ψ_sel ρ_rg)` 与 §3.3 登记的 `ρ_a,ach = ρ_a0/cosψ` 方向相反：cos²ψ<1 反使质量**变大**；§6.5 又称 1.3286>1 为 "squint-loss factor"，把 24.7% 的损失印成 32.9% 的增益；修正后该格 ≈28.3 m⁻²，非 37.62 | **成立（阻断）** |
| B7b | SAT 展开错误 | Domain | `literature/fulltext/kim2021_aerospace_fulltext.txt:236` 明确 SAT = **synthetic aperture time**，全文无 "saturat" 词根；稿件展开为 "saturation-avoidance time"，且与本文自己的 "saturation arm" 语义相撞 | **成立（阻断）** |

**判定说明**：B3 只有一席提出，但它是本次评审中证据最硬的一条——带宽是代码里冻结的常量，正文却把它省略，导致一个"经验发现"实际上是生成器的算术推论。这比任何统计争议都更直接地影响标题主张。B7 同样只有一席提出，但性质不同：它不是解释问题，而是**印在纸上的式子与文字是错的**，可由原文与内部一致性直接判定，无需重跑。

### 3.2 采纳（单席提出但成立）

- **M-a 机动模型不连续**（Methodology 席）：我已核对 `maneuver.py:79,178-189` 与 `anchor.py:384-385`。0.46 s → 4.07 s 的跳变落在锚点典型跃迁上。列为 P1-3，必须在修回稿中至少报告 fallback 频率与 pad 敏感性。
- **M-b 两个相关系数无效**（Methodology 席）：数值可复算，且违反稿件自定的跨族不可比口径。P1-4。
- **M-c 最接近的 SAR 区域观测文献未引用**（Journal-Fit 席）：四个 key 在 `refs.bib` 中存在、在 `main.tex` 中引用数为 0。P1-5。
- **M-d 格式与引用缺陷**（本报告独立发现）：见附录 B。P0-9。
- **D-a 印出的质量方程方向反**（Domain F3）：p.14 印式与 §3.3 登记式互斥，且 §6.5 把损失称作 factor。这是**已印出的错误**，不是措辞问题；修法廉价（改 cos²ψ 位置并重算该格，或按 C5 删去该项），但不能以"实现口径已登记"带过。P0-8。
- **D-b SAT 展开错误**（Domain F7）：原文可查，属勘误级。P0-7。
- **D-c 速度约定名不副实**（Domain F5）：7578.05 m/s 是卫星惯性速度而非场景速度，ECEF 足迹速度低 4.8–5.0%，逐任务占用率偏移 1.5–3.5%，与头条数同量级。稿件已披露但未量化，要求改称并补一行敏感性。P1-3。
- **D-d AASR 门槛从未绑定**（Domain F6/F10）：30 个 manifest 的 removals 合计 `aasr=0, footprint=0, below_finest=0, no_window=15`。因此 §2.1 的方向对比对任何可行性判定都没有作用，§7.2 的自我否认实际上是对的——应把这句话前置到 §2.1，而不是留到最后。P0-7。

### 3.3 不采纳或降级

- **"立即拒稿"**（DA 的条件式结论；Meth 亦称"Reject defensible"）：不作为当前裁决。理由：内核贡献可保留，且七条阻断项中 B1/B2/B5/B6 可由再分析与重写解决，B3/B4 可由既有 artifact 的模式分解解决（不需新实验，除可选的路由曲线），B7 是勘误级。保留为 Reject 触发条件。
- **"缺运行时间 / 下行 / 动态到达"**（Persp F5）：**降级为 scope**，不作为阻断。理由：稿件在 p.37 已明确列出这些不做；AST 可以接受一个明确限定的一次性规划模型。但两处必须改：(i) "cloud-cover attrition" 删除或改成 SAR 相关环境；(ii) 若保留 "platform" 一词，至少给出每任务/每族数据量的一行估算。
- **"27 篇文献太薄，应做系统综述"**：部分采纳。不要求系统综述，但要求 (i) 接入 `refs.bib` 中四篇最近的 SAR 区域观测工作；(ii) 把 "near-universal" 软化为 "common in the surveyed subset"；(iii) 加一张结构化对比表（duration 内生/外生、quality 目标/约束、mode 固定/决策）。
- **"把 §4 砍成一段"**（DA M8）：部分采纳（→ P1-7）。若作者选择保留 EA 作为贡献，则必须补 R 族的预算梯；若选择承认 EA 只是测量工具，则可压缩到 1–2 页并删去 SBX/多项式变异的细节。二者择一，不能既称方法贡献又称其在 258/260 单元不起作用。

### 3.4 与既有内部审计的关系

本报告不重开已闭环的内部决议：

- **B1（冻结模式分配）** 已在 ticket 48/50 记录为设计选择。本报告接受它是**合法的 scope 选择**，问题不在"冻结"，而在标题/摘要没有把这个条件放进第一句。
- **B2（f_Q_deliv 实现口径）** 已按 §8.17-10 处置，本报告不复议。
- **L9（路由自由度）** 不作为修回条件，列为 P2 可选项。要求的是**披露**，不是补实验。

换言之：内部审计判定"这些是已裁决的设计决定"，本报告同意；但**读者只看到最终稿**，最终稿必须自己承担这些决定的表述后果。

---

## 4. 修订路线图

### P0 — 阻断项（修回前必须完成）

| # | 位置 | 动作 | 验收判据 |
|---|---|---|---|
| P0-1 | 标题、摘要 p.1–2、§6.2 p.31、结论 p.43 | 双向报告：明写 1.0→0.9 与 1.0→0.8 的代价（R3H 26.0/46.6 pp；R1C 46.0/不可行；R2F 0.27/0.00 pp），并把 4.15/2.36 改称 "loosening premium" 或"相对本族网格最大值的差" | 摘要中每个成本数字都带方向与两端 s 值；不再出现无方向的 "pays a coverage cost" |
| P0-2 | §5.1 p.24、§5.2 p.26、§6.2 p.31 | 披露 ρ_req 带宽 `[2.5,3.0] m`（粗）/`[0.3,0.6] m`（细）与 STR 地板 2.4669 m；把 R1C s=0.8 改写为一行解析结论（0.8×3.0 < 2.4669），并把该格从 K3 判定中标为 undefined | 读者不看代码即可复算"为何 10/10 不可行"；该格不再计为 0 覆盖 |
| P0-3 | §6.1 p.29、§6.3 p.32、Table 1 p.33 | 增加模式分解表：每个 s 下 STR / SLS / SPT 的 served 数、dropped 数、优先级质量；据此重写机制段 | 表中能直接读出"R3H 收紧侧损失中地板排除占多少"；若 >70%，标题与摘要必须改为"模式构成决定可行性" |
| P0-4 | Table 1 p.33、§5.3 p.27 | 三值判定（met / not met / undefined）；用配对 per-seed delta 替代边际中位数；预定义容差（建议 1 个优先级单位或配对 CI 排除 0） | Table 1 无"靠约定成立的 met"；R2F 的两次 0.3 pp 下降不再触发失败，或明确说明为何仍触发 |
| P0-5 | 摘要 p.2、§1.2 p.4、§6.5 p.34、结论 p.43 | 删除 C5 "no violation"、477,308、R2F retention 100%；C5 改述为 per-mode delivery rule（SLS/SPT 等式；STR ≤ 订单、交付地板）；报告等式实际被检查的记录比例 | 摘要不再出现"无违反"类陈述；477,308 只出现在实现脚注，且附 distinct 任务数 |
| P0-6 | 摘要 p.1、§3.5 p.19–20、§5.3 p.28 | 精确化预注册表述："grid 与 K1–K3 形状检查预先登记；own-saturation 代价为 2026-10-21 修正案后定义，属 post hoc descriptive" | "frozen/registered" 不再修饰头条量；修正案的时间与内容在正文可见 |
| P0-7 | 全文（摘要 p.2、§2.1 p.8–9、§5.3 p.27、§6.2 p.29、§7.2 p.39、p.43） | 术语与事实标签：形状准则改名 K1–K3，与约束 C1–C5 分离；SAT 改回 "synthetic aperture time"；"single-orbit" → "sparse all-stripmap control"；删 "no intermediate regime"；"true orbit geometry" → "propagated two-body geometry"；速度常数改称 "satellite inertial speed"；把 §7.2 的"该对比不构成反驳"前置到 §2.1 | 全文检索 `C3` 不再同时指能量与 tight arm；无 "saturat" 展开；无 "single-orbit"；§2.1 自带对该对比的限定 |
| P0-8 | §3.3 p.15、§6.5 p.34、Fig. 4 p.33 | 修 p.14 印式：cos²ψ 归位（或按 C5 删去该项）；重算并统一 37.62 → ≈28.3 m⁻²；1.3286 改称 "squint quality penalty" 或按其真实方向描述；确认 f_q 与 (ρ_req/ρ_a)² 的等价关系在正文可见 | 任取一格手算可复现；无"损失被称为增益"的表述；Fig. 4 不再是三条构造性平线 |
| P0-9 | 摘要 p.1–2、`refs.bib`、全文排版 | 摘要压到 ≤250 词（现 284–286）；清理 307 条双括号作者、147 条 scholar 残留；修 `\citealt` 打印串（p.17）；`elsarticle-harv` 与 numeric 二选一；修 overfull hbox 与双句点 | 摘要词数达标；参考文献作者/期刊字段干净；编译 0 error、无 >10 pt overfull、无 "Kim, Hongrae and ... 16" 类串 |

### P1 — 应做项（决定修回稿能否达到 AST 主刊水准）

| # | 位置 | 动作 | 验收判据 |
|---|---|---|---|
| P1-1 | §5.3 p.27、§6.1–6.4 pp.28–33、Fig. 3 | 每点报 median [95% bootstrap CI]；主分析改为配对 per-seed delta（十场景配对，s 轴九点）；说明"seed = 独立场景抽样"，并至少在子样本上跑 3 个 solver seed 以分离搜索噪声 | 摘要的每个 pp 数都带区间或配对统计量；"one world" 表述消失 |
| P1-2 | §5.2 p.26、Table 1 | 族规模改为区间：R2F 46–50 admitted、R3H 99–100、R1C 145–162 窗、R2F 337–391 窗、R3H 731–779 窗；"2×99" 改为"2×N, N=99–100" | 单 seed 常数不再作为族常量出现 |
| P1-3 | §3.4 p.17、§7 p.39 | 机动 hybrid 连续化（如 `max(analytic, floor)` 或单一标定常数），或至少报告 fallback 触发频率，并对 pad ∈ {15,20,25,30,35}%、settle ∈ {1,2,4} s、PRF ∈ {2300,3044,3630} Hz、AASR 阈值 ±1 dB 做 one-at-a-time 敏感性 | 机动时间对 dψ 单调；正文给出"结论对这些常数不敏感"或给出敏感度数字 |
| P1-4 | §6.6 p.35 | 删除 r=0.329/0.249，或改为族内、场景级（n=10）并给 CI；不得跨族合并 caliber | 全文无跨族 pooled 相关；若保留则明确"不可与零区分" |
| P1-5 | §2 pp.5–8 | 接入 `liu2025a`、`shen2024multistrip`、`xin2024sar`、`li2026efficient`；加一张三列表（duration 内生/外生、quality 定位、mode 固定/决策）；软化 "near-universal" | 最近先行工作被讨论而非仅列入 bib；"near-universal" 有界定 |
| P1-6 | Fig. 3 p.30、Fig. 4 p.33 | Fig. 3(b) 纳入 R3H 收紧侧（可用断轴），或至少在图注写出 46.6 pp；Fig. 4 三条水平线删除，换成 delivered-resolution 或 data-volume 的可用读数 | 主图能看出头条数与收紧侧断崖；无"平线图" |
| P1-7 | §1 pp.3–4、§4 pp.19–23、结论 p.43 | 贡献声明三选二：保留"物理闭合的调度实例"与"可复现 artifact"，删去"一般性代价定律"框架；第三贡献"纪律性"或者用时间线表兑现（见 P0-6），或者删除。EA 二者择一：作为方法贡献则补 R 族预算梯；作为测量工具则压到 1–2 页并删 SBX/多项式变异细节 | 摘要的三条贡献都能在正文找到对应证据；不再同时称 EA 是方法贡献又称其在 258/260 单元不起作用 |
| P1-8 | 新增小节（可选但建议） | 加固定 dwell 反事实：把 dwell 冻结在 s=1.0 库值求解，再用真实 C2/C5 重放，报告违反率与覆盖差；或删去 "fails in a quantifiable way" 的强主张 | 若保留"可量化地错误"，必须给出量化 |

### P2 — 可选增强（不影响本次裁决）

- 路由开启曲线（coarse-sufficiency 规则）：量化"模式自由度"的价值，直接回应 B3/B4 的 operational 版本。
- 每任务/每族数据量与下行容量检查；wall-clock 运行时。
- 网格扩展（到 3.0/4.0）与独立饱和定义（解析上界或物理最粗订单）。
- 代码、prereg、artifact 的 DOI 存档（Zenodo/figshare 或同侪仓库），以兑现第三贡献；现为 "available from the corresponding author"。
- 篇幅：48 页压到 ~30 页；把 provenance 段落移入 supplement。

---

## 5. 复审判定标准

**Accept（或 Minor Revision）当且仅当**：

1. P0-1～P0-9 全部落实，且摘要中不再出现与实验方向不一致的成本陈述；
2. 模式分解表已给出，且机制段与分解结果一致（无论地板占主导与否）；
3. Table 1 无"靠约定成立的 met"，K1–K3 有容差与配对统计；
4. p.14 印式与 §3.3 登记式一致、该格读数已重算；全文无 "single-orbit"/"saturation-avoidance time" 类错误标签；摘要 ≤250 词，引用格式统一，编译干净。

**Reject 当**：

- 作者只做措辞软化（改称 premium、改掉 single-orbit），但拒绝披露 ρ 带宽、拒绝模式分解、拒绝对头条量做双向报告；或
- 修回稿仍以"frozen/registered"修饰 2026-10-21 之后定义的 own-saturation 代价。

**留在 Major Revision 的情形**：P0 完成但 P1-1/P1-3 未做——此时论文可作为一篇诚实的单世界敏感性研究发表，但需把标题缩到 "order sensitivity under a frozen mode assignment"。

---

## 附录 A：独立复算表

### A.1 复现性

| 检查 | 结果 |
|---|---|
| `verify_paper_numbers_l8.py --paper main.tex` | rc=0，**74/74**，0 retired-world token |
| 27 组 family×s 中位数 | 与 `sweep_results.json` 全部一致 |
| per-seed 覆盖（270 单元） | 与 manifest/artifact 一致 |

### A.2 我另行复算的量

| 量 | 复算值 | 稿件值 | 备注 |
|---|---|---|---|
| R3H C(0.8), C(0.9), C(1.0), C(1.5) | 0.4827 / 0.6884 / 0.9485 / 0.9900 | 同 | 一致 |
| R3H 1.0→0.9 | **26.01 pp** | 未报告为"cost" | 稿件只说"about half" |
| R3H 1.0→0.8 | **46.58 pp** | 未报告为"cost" | |
| R3H vs s=1.5 | 4.15 pp | 4.15 pp | 方向为"放松收益" |
| R1C 1.0→0.9 | **46.02 pp** | 未报告为"cost" | |
| R2F 1.0→0.8 | **0.00 pp** | 未报告 | "tightening is free" |
| R2F vs s=2.0 | 2.36 pp | 2.36 pp | 饱和点在网格边界 |
| R3H 非 STR 优先级份额（10 场景） | median **0.5007**（0.3895–0.5865） | 未报告 | s=0.8 观测 0.4827，差 1.8 pp |
| R3H s=0.9 地板天花板 | median **0.7484**（0.6667–0.8140） | 未报告 | 观测 0.6884，差 6.0 pp |
| R1C s=0.9 地板天花板 | median **0.5694**（0.4706–0.7568） | 未报告 | 观测 0.5398，差 3.0 pp |
| R1C 任务/窗/ρ | 20 / 145–162 / 2.5049–2.9999 m | "20, 158" | 单 seed 值 |
| R2F 任务/窗/ρ | 46–50 / 337–391 / 0.3011–0.5999 m | "46, 342" | 单 seed 值 |
| R3H 任务/窗/STR | 99–100 / 731–779 / 41–54 | "99, 753" | 单 seed 值 |
| R3H 模式构成（seed 300） | 54 STR + 15 SLS + 30 SPT | 未报告 | 仅有"mixes all three modes" |
| p.14 质量方程的读数（修正 cos²ψ 后） | ≈**28.3 m⁻²** | 37.62 | 差 24.7%，方向与"损失"相反 |
| 1.3286 的真实作用 | cos⁻²ψ（>1，抬高 f_Q） | 称 "squint-loss factor" | 量纲/方向描述错 |
| 24.3× / 67.6× 的来源 | (2.4669/0.5)² / (2.4669/0.3)² | 称"模式间差数量级" | 纯由分辨率决定 |
| 30 场景 AASR 移除数 | **0**（aasr=0, footprint=0, below_finest=0, no_window=15） | §2.1 用其做方向对比 | 门槛从未绑定 |
| 场景速度（ECEF 足迹） | 7220–7229 m/s | 7578.05 m/s（惯性） | 低 4.8–5.0% |
| 477,308 的来源 | Σ front 记录 `n_selected`（9,430 条） | 477,308 | 成员级计数 |
| distinct 任务数（每单元最佳） | **13,845** | 未报告 | 477,308 的 1/34.5 |
| 摘要词数 | **284–286** | — | AST 上限 250 |
| PDF 页数 | **48** | 48 | `main.log` 一致 |
| overfull hbox | 18.05 / 11.14 / 9.33 / 7.63 pt | 未处理 | main.tex L79–80, L132–133, L168–169 |

### A.3 与稿件不一致的事实陈述（4 处）

1. **"single-orbit"**（p.1, p.19, p.26, p.29, p.43）：场景跨 3 天、R1C 每任务 3–12 个可见窗、首末窗中心跨约 2.6 天，属多圈多 pass。
2. **族规模常数**（p.26）："46 admitted / 99 admitted / 158 / 342 / 753 windows" 均为 seed 100/200/300 的单次值。
3. **"no intermediate regime"**（p.29）：同页给出 R1C s=0.9 = 0.5398，正是一个中间覆盖值；应为"无连续中间机制"，而非"无中间取值"。
4. **SAT 的展开**（§2.1）：引用的 Kim et al. 2021 原文定义为 synthetic aperture time；稿件展开为 "saturation-avoidance time"，该词在其文献表中无来源。

---

## 附录 B：格式、引用与排版缺陷清单

| # | 位置 | 缺陷 | 修法 |
|---|---|---|---|
| B-1 | `main.tex:5,8,14` | `\documentclass[review]{elsarticle}` 默认 numeric，却设 `\bibliographystyle{elsarticle-harv}`；正文实际排成 `[16]` 数字引用 | 统一为 harv（`\documentclass[authoryear,review]{elsarticle}`）或明确改投 numeric 口径，并同步 `writing-config.md` |
| B-2 | p.17 | `\citealt{kim2021optimal}` 在 numeric 模式下打印出完整作者串 "Kim, Hongrae and Park, Joonil and Chang, Young-Keun and Lee, Soo-Ho 16" | 改为 `\citep`/`\citet` 或移除 alt 类命令 |
| B-3 | `refs.bib` | **307/307** 条 author 字段为双括号 `{{...}}`，导致参考文献表作者名以 "Firstname Lastname and ..." 形式整串输出 | 去除双括号，逐条拆分 `and` |
| B-4 | `refs.bib` | 275 条 journal 字段中 **147** 条含 Google-Scholar 抓取残留（"… - Springer"/"… - Wiley Online Library"），如 `liu2025a`、`xin2024sar`（后者 DOI 还带尾部 `@`，作者名有乱码） | 逐条清洗；被引 27 条中虽无此残留，但修回扩充文献时会带入 |
| B-5 | 全文 | 280/307 条 bib 条目未被引用；27 条被引文献支撑三大主题 | 与 P1-5 合并处理 |
| B-6 | p.1–2 | 摘要 284–286 词 > AST 250 词上限 | 压缩，保留 1 个头条数 + 1 句 scope |
| B-7 | 图 1 | 面板标签约 6 pt，印刷不可读 | 提高到 ≥8 pt |
| B-8 | Fig. 3 p.30 | caption 约 200 词；面板 (b) y 轴截断至 [0.958,1.004] 放大 0.3 pp 噪声，且排除 R3H | 缩短 caption；重画（见 P1-6） |
| B-9 | Fig. 4 p.33 | 三条水平线（quality index vs squint），信息量近零 | 删除或替换 |
| B-10 | p.44 | 数据可用性为 "available from the corresponding author"，与"可复现"第三贡献不匹配 | Zenodo/figshare DOI + hash |
| B-11 | cover letter | 单作者却写 "All authors approve the submission" | 改单数 |
| B-12 | p.29, p.32, p.39, p.40 | 多处 run-in heading 双句点（"What the amendment retired.."、"The range-resolution anchor is a design constant.."） | 统一为单句点 |

---

## 附录 C：不建议做的修改

1. **不要重调 K1–K3 去"救"R2F**。稿件现在的处理（失败照报、不 retune）是正确的，也是少数真正加分的"纪律"证据；问题只在判定无容差与 R1C 的零覆盖约定，不在失败本身。
2. **不要删掉 R1C 的不可行结果**。它是本文最干净的物理结论之一；要改的是它的**叙述方式**（从"经验发现"改为"带宽与地板的解析推论"）。
3. **不要用一次路由开启实验去主张一般性**。路由曲线是 P2 加分项；在没有它之前，标题必须限定 "under a frozen mode assignment"。
4. **不要为了"看起来像方法论文"而保留 EA 的方法叙事**。258/260 的负结果比一个装饰性的 GA 更有价值；把 EA 降为验证工具、把 anchor + 物理闭包升为方法，反而更符合 AST 的口味。
5. **不要把"registered/caliber"全局替换成同义词**就当作修完 B6。问题不是词，而是**哪些量在何时被登记**；必须给出时间线与"pre-specified vs post hoc"的清单。
6. **不要新增跨族 pooled 统计**来"增强说服力"。稿件自定的 caliber 不可比规则是对的；跨族比较只能以"形状/机制"表述，不能以"数值大小"表述。

---

*报告完。评审未修改稿件任何文件；所有复算脚本与中间量可在评审者工作目录复现。*
