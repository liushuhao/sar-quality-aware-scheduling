# 作者裁决 sidecar — 2026-11-03 面板（CONFIRMED）

规则：每条恰一个选择 —— `will_address`（含精确目标）/ `wont_address`（带理由）/ `not_on_point`（带理由）。
本版裁决由作者委托的审查会话（2026-11-03）代填：每条附证据行号，作者可逐条推翻。
状态流转：DRAFT → AUDITED-DRAFT r2/r3 → **CONFIRMED**（2026-11-03 异源确认轮 3 VERDICT: PASS——轮 2 的 N1-N11 全部 resolved、零须修级新发现；轮 3 exploratory M1-M7 已吸收，见文末台账）。

对应路线：`revision-roadmap-20261103.md`（R1-R14 + 不纳入清单）。
回扫记录：`.scratch/adjudication-20261103/`（任务书 ×2 + report-r1/r2 + 处置台账见文末）。

## 亮点层统一预算（R1/R3/R14 共同约束，先于各条裁决）

`highlights.tex` 头部硬约束：3-5 bullet points、每条 ≤85 字符（含空格）；现 4 条（4→5 合法，真约束是**每条字符数**）。三条路线的亮点层改动合并设计：
- R1：重写第 3 条为单条两句（贪心对照 +40% 与受控 +4.9% 并列），不拆成两条；按 85 字符预算实打实删词（须牺牲部分限定语如 NESZ-ordering index / sparse density 的完整表述，保留数字与基线指向）。**逐条余量实测（2026-11-03）**：四条现长 78/75/84/82 字符，余量 7/10/1/3——R1 的第三个数字（+6.2% 膝规则口径）在 85 字符内放不下则**只进正文不进亮点**；R3 的限定语（≈25-30 字符）四条余量均不容，须与 R1 同句压缩或换更短表述（"in simulation"）。
- R3：仿真场景限定语（"in simulated request sets"类）并入既有条目句内，同样受字符预算约束（见上条余量实测）。
- R14：贡献 #4 **只进摘要不进亮点**——主因：按作者口径保留 4 条（不扩到 5 条）；次因：若扩第 5 条，其表述可压到 ≤85 字符（如「Controlled ablation tests each physics term; coverage edge needs G-BL hot start」=79 字符），故真约束是条目数决策而非字符不可行。roadmap R14 写「摘要与亮点」，此处为范围收窄，特此标注，作者可改判扩第 5 条。

## 裁决表

| 路线项 | 席位 | 裁决 | 目标 / 理由 |
|---|---|---|---|
| R1 亮点归因 +40%→受控 +4.9% | EIC-01, R1-12, R3-12, DA-02 | will_address | highlights.tex 第 3 条单条内拆两句（字符预算见统一预算节）：(i) 相对贪心 G-BL 的质量增益 +40%（附 15% 覆盖代价）；(ii) 第三目标受控增量 +4.9%（matched radiometric-aware rule），膝规则口径 +6.2% 注明规则差异。数字与正文 tex 1189-1202 一致；基线限定语（"relative to greedy"）随 R5 在摘要/结论/亮点同步补入——结论 1522-1525 现有 +40% 句未点名 G-BL，补限定后才算同口径。 |
| R2 密度边界口径统一 | EIC-03, R1-11, DA-01 | will_address | 改写 tex 1530-1533 的 because 从句（**保留** 1528-1530 前半主张句）：拆成两句——质量边际消失归覆盖压力、锚收敛归热启动条件性；从句第二机制「solver convergence to lower-squint geometry aligns f2 and f3 through the shared cosψ_sq factor」（tex 1531-1533）**保留**，归入前半句（覆盖压力侧）的机制描述——它是 §6.4 压缩论证与 1533-1535「not a redundancy between objectives」的支撑，不得删除。摘要 tex 49-51 同口径。与 §7.1 Summary of Findings (5)（tex 1346-1348）统一。§7.4 Limitations（tex 1481-1486）已是条件口径，作统一参照不改。 |
| R3 前沿层补仿真口径 | EIC-02, R2-09, R3-04 | will_address | 摘要 tex 42-45 补「in simulated request-set scenarios」限定；亮点按统一预算节并入既有条目；Limitations tex 1474-1477 已有「synthetic, static scenario family … family-specific」口径，对齐即可。 |
| R4 第三目标价值机制（斜视通道） | R2-01, R3-07, DA-03 | will_address | 改消融节（`sections/_ablation_section.tex`，\input 于 tex 1231）119-141 邻域与贡献列表（tex 179-184，贡献 #4）：价值主通道=斜视（变体 B 去 squint → f3 −18%）；入射角因子窗口内近似公共尺度（~1.5° vs 斜视 20–35°），其冲突经跨窗口聚合几何起作用（保留 135-137 既有措辞，不写成全局无用）。保留三目标的理由限定写：f3 的 NESZ 排序本身含 θ_elev 因子（质量评估完整性）；S4 侧只写「per-scenario 方向一致（33/50，sign +0.32）但分布效应可忽略（Cliff's δ=+0.03）且边际有界（tex 1207-1212）」——**不**用 +0.32 单独当保留论据。收回任何暗示入射角冲突承重的措辞。 |
| R5 便宜物理对照 或 收窄声明 | R1-06, R2-03, R3-01, R3-08, DA-04, DA-08 | will_address（收窄+交换率支路） | 零成本支路：§7.2 加一段 G-SM 交换率正面讨论——Table 1（tex 904-930）已有全四密度数据：G-SM f3 高于 MOEA-3（由印刷均值复算 +3.4%/+23.1%/+21.3%/+15.6%）但 f1* 仅 0.51/0.35/0.29/0.37，覆盖代价 49%/65%/71%/63%（S1 至 S4）——交换率句与 §7.2 既有「+16% f3 at S4 at a 63% coverage cost」（tex ~1393-1396）口径一致；摘要/结论声明限定为「relative to the greedy coverage baseline」。混合基线（斜视最小化+优先级回填）记二审备选不预先承诺：求解器算子级随机未钉死（§5.4 tex 849-851 口径：场景种子钉实例生成、NSGA-III 采样种子固定、算子级随机不钉），新基线数字须同实例多 repeat 报极差（replicate_variance_20261031 实测：同实例 f1 极差 ≤1.0%、f3 ≤1.36%）——成本中高且结果双向风险。 |
| R6 资源上限敏感性 | R1-04, R2-09, R3-03, DA-07 | will_address（reporting 支路） | 按 C3/C4 是否绑定拆分报告稠密类结果 + 明说预算对照欠功效（tex 557-562、1279-1300 邻域）；E_max/M_max 两档扫描记备选。 |
| R7 可复现口径 + 扩大重复运行子集 | R1-02, R3-11, DA-11, EIC-12 | will_address | **执行前置（回扫轮 3 实测发现）**：replicate 跑批与主跑快照在同一实例上不一致（S1-A_seed00 f1 主跑 0.7396/1.0 vs replicate 均值 0.6458/0.8333，f3 全密度系统性偏低；候选成因=solver 版本/口径漂移，快照 solver_version=04ce55c4）——写「哪些结果可复现」口径段**之前**必须先做一次主跑 vs replicate 对账，否则口径段措辞无据。口径段本身零成本：§5.4（tex 849-858）与 Data Availability（tex 1566）统一，一段话写死。扩容为**中等成本跑批**：`run_replicate_variance.py` 已有但 SCENARIOS 现硬编码每类 1 场景、REPEATS=5（实测脚本 35/37 行），扩到每类 ≥10 场景 ≈ 40 场景 × 5 repeats × 2 求解器 ≈ 400 次求解（现量约 10 倍）；另注意快照内 seed00-09 是**场景实例**种子（每 seed 一个不同实例），不是同实例重复求解——replicate 扩容须用同实例多 repeat 口径。 |
| R8 质量指标丢弃目标构成 | R2-02, DA-09 | will_address（reporting 支路，范围按数据面限定） | 数据面（2026-11-03 两次实测）：**含 `selected` 字段的快照**——MOEA-2（`_snapshot_moea2obj_full300.json`，S1-S4+S7/S8）、MOEA-3（`_snapshot_moea3.json`）、GA-P-BL（`_snapshot_gapbl.json`——**文件名不指 G-BL**，其 `solver` 字段全为 `b2_profit_bl_seeded` 即 GA-P-BL，含 `selected`）、消融变体（`_snapshot_abn_*.json`）；各快照均含 `n_targets/n_selected/selected/t_actuals`（差异仅在前沿字段）。**G-BL 与 G-SM 无 `selected`**：`baselines_200.json` 的 b1/b3 只有 `n_targets/n_selected/f1/f2/f3` 计数——如需这两家的丢弃构成，须从对应 runner 补跑落盘。报告范围按可得数据限定（MOEA-2/MOEA-3/GA-P-BL），统计后在 §3.2/Table 1 邻域报告；不改聚合定义。 |
| R9 变体 C 相关系数指标对 | R1-03, DA-06 | will_address | 固定全物理对（f2–f3）写清被相关指标；改三处锚：正文 tex 1129-1130（ψ-only 极限 r=+0.997）、正文 tex 1171-1173（variant C）、**Fig.7 caption tex 1155-1164**。 |
| R10 PRF / 偏航补偿物理自洽 | R2-04, R3-04 | will_address | 正确锚点：yaw steering/Doppler centroid/PRF 句在 **tex 521-527**（§3.3 Physical modeling scope：10² kHz Doppler vs 10⁰–10¹ kHz PRF），带宽 56.5 MHz 在 **tex 717**（§5.1 场景设计）——roadmap 所记 ~425-430 是 NESZ/sinθ 段，非本项内容。改写使三要素自洽；同时并入 R2-12 的 SAR 运行约束（回波窗/占空比/模糊）讨论句——确认轮 grep：ZH 版四词零命中，EN 版 `downlink` 仅一处且为 Limitations 泛提（tex 1494「other energy or downlink budgets」），非运行约束讨论，属缺失非冲突。 |
| R11 术语与可读性 | EIC-07, EIC-08, R2-06 | will_address | single-pass 改名沿「single-satellite, two-orbit horizon」方向（tex 81-82 定义句本就否定 single overflight，**禁用 flyby/overflight 词**）；求解器/场景标签首现处全称（tex 128-139 邻域）；密度类命名与排序说明（tex 747-749：类序列跳过 S5/S6 直至 S7/S8——**全稿无 S5/S6 标签**，roadmap 所写「S5/S6 类目」系旧称，实指 S7/S8 中间类的命名与排序未解释）。 |
| R12 内部一致性打包 | R2-05(残余), DA-05, DA-13, R1-10, DA-16 | will_address | R2-05 残余按确认轮口径拆开处理：(i) 「sinθ 方向两处相反」属 R2-05 主体论证，确认轮已判 UNSUPPORTED（同一逆 NESZ 指数的两侧描述）——两处锚为 tex 426-427（「suppressed sinθ factor varies by roughly 2.4×」）与 tex 432-433（「dividing by sinθ reweights but cannot reorder」），执行时先回这两处核对，确认属同一操作则**不改**并记录；(ii) 真正的保留项补进本条：+40%→+94%（正文 tex 433-437 邻域）补印刷代数步骤或删强端、补一句模糊受限 NESZ 讨论。其余照旧：超体积敏感性两处相反（DA-05）、两条 f₂ 区间不能同真（DA-13）、多重比较族定义两处（R1-10/DA-16）。 |
| R13 统计报告细项 | R1-07, R1-08, R1-09, DA-15 | will_address | 效应量尺度命名统一（R1-07 命名部分）；20 次置换补 95% 区间或改报法（R1-08）；冗余检验撤出被否指标（R1-09）；DA-15 离散度句按 1.18 倍口径改（非 2.4）。 |
| R14 摘要/讨论可读性与精度 | EIC-09, EIC-10, EIC-11 | will_address | 行话替换（EIC-09）；贡献 #4 补进摘要（EIC-10；亮点层因字符预算不进，见统一预算节）；两条讨论句语法（EIC-11）。 |

## 口径问题（题面 + 代填答案，附证据，作者可推翻）

### Q1 密度边界的成因认定（题面：三选一）

题面（转录自旧版 sidecar——主线程会话内留档，盘上无独立题面文件可核）：「密度边界的成因，作者认定是哪一个？(a) 覆盖压力是物理机制，热启动只是搜索路径；(b) 边界是热启动工件，随机初始化下优势可能延续；(c) 两者的叠加，需要一次随机初始化对照来分离。论文现在三处各说一套（结论 1528-1533 / §6.6 1346-1348 / §6.4 1087-1089）。」

**答案：分层口径——(a) 与 (b) 各对一半，作用于两个不同子现象；分离证据已在论文内，无需新对照即可改口径（接近 (c) 但不需补实验）。**

论文内实为两个子现象、两个机制，证据均已印在正文：

- **α 质量边际消失（dense-regime quality margin < 2%，如 S3 f3 +1.1%、S4 +0.7% vs G-BL，Table 1）→ 覆盖压力**。证据为**排除法双证据**，并诚实注明其强度边界：① 预算翻倍对照（tex 1296-1300）——budget 加倍 quality 至多 +1.64%、f1* 差 <0.5%，原文结论句「the sub-2% dense-regime margins reflect coverage pressure and not premature convergence」（「margins below 2%」在本文四处同形固定指质量边际：tex 51/143/1530/1299）。**强度边界**：位移上限 +1.64% 与边际本身（0.7–1.1%）同量级，严格读下预算解释未被完全封死——此处的排除是「加倍预算未使 sub-2% 状态改变」的状态级判断，非量级级证明，改写时不宜升格为「已证明物理成因」；② variant-D 随机初始化（tex 1300-1309）——不带 G-BL 播种仍复现同等低斜视收敛（S3 0.349 vs 0.342；S4 0.347 vs 0.336），排除「热启动残留」解释。两个竞争解释被（状态级）排除后归因覆盖压力（1530-1531 的「coverage pressure removes the freedom to move acquisitions」是机制假说本身，由上述排除支撑）。
- **β 前沿收敛到贪心锚（覆盖侧收敛）→ 热启动条件性**。证据：随机初始化 MOEA-2 相对热启动丢覆盖 0.39–0.68 f1*（tex 1260-1263）「G-BL seeding therefore drives the coverage convergence」；§7.1 Summary of Findings (5)（tex 1346-1348）与 §7.4 Limitations（tex 1481-1486）同口径，且 1485-1486 明说 unconditional 行为需 full-scale random-init 实验才能确立。

结论段（tex 1528-1533）的错误不在强度而在**捆绑**：because 从句把 α 的覆盖压力成因安在整个「fronts converge … with quality margins below 2%」上，而该句主语混合了 β。修法（并入 R2）：拆句分层，两子现象各归各的成因（cosψ_sq 对齐机制块保留，见 R2），与 §7.1 (5) 统一。可选补强（不阻塞 R2）：MOEA-3 侧随机初始化对照（现仅有 MOEA-2 与 variant-D）。

### Q2 第三目标的价值来源

题面（转录自旧版 sidecar，同 Q1 来源说明）：「第三目标的价值来源：作者是否同意『价值由斜视通道承担、入射角轴在本场景族惰性』？若同意，R4 按此改写；若不同意，需要给出入射角轴在何处起作用的证据。」

**答案：同意主通道=斜视；「惰性」仅限 per-window 选择层面——入射角按「窗口内近似公共尺度、跨窗口聚合通道保留」写，不写成全局惰性。**

- 消融自有数据：变体 B（去斜视）f3 −18%（_ablation_section.tex 123-127）；变体 C（去入射角）per-window 选择层面无变化（128-135）。→ 价值主通道=斜视，成立。
- 但消融节自己写明（135-137）「The incidence conflict … operates through the across-window/aggregate geometry rather than through per-window selection」——入射角冲突经跨窗口聚合几何起作用，非全局无用。面板「入射角轴惰性」判词仅在选择层面成立。
- 保留三目标的理由（按 R4 限定口径）：f3 的 NESZ 排序含 θ_elev 因子（质量评估完整性）；S4 侧只到「方向一致但分布效应可忽略（δ=+0.03）、边际有界（tex 1207-1212）」，第三目标的价值集中在稀疏区，稠密区保留它是质量口径完整性而非增量主张。

### Q3 R5 走哪条

题面（转录自旧版 sidecar，同 Q1 来源说明）：「R5 走哪条：补实验（成本高）还是收窄声明（零成本，但摘要与结论的定位要同步降低）？」

**答案：收窄声明 + 已有 G-SM 交换率正面讨论（零成本支路）；补实验列二审备选。**

- 关键事实（面板簇 C 未采）：**G-SM 已在 Table 1 全四密度实测**（tex 904-930）——f3 全面高于 MOEA-3（印刷均值复算 +3.4%/+23.1%/+21.3%/+15.6%），代价 f1* 0.51/0.35/0.29/0.37（覆盖代价 49–71%，S1 至 S4）。「便宜启发式未被测试」部分失实；真缺口=§7.2 未把这条交换率讲透 + 声明未限定。
- 补「保覆盖混合基线」需新实现+新跑：算子级随机未钉死（§5.4 tex 849-851），新基线数字须同实例多 repeat 报极差（replicate_variance_20261031 实测，均值口径：同实例 f1 极差 ≤1.0%、f3 ≤1.36%），成本中高；且结果双向风险（混合基线若追平 MOEA-3，主张进一步削弱）。
- 执行：§7.2 交换率段（已有数据）+ 声明限定「relative to the greedy coverage baseline」（摘要/结论/亮点同步）；若二审仍要求物理基线，再走混合基线（roadmap 支路保留）。

## 证据核查记录（2026-11-03 主线程实测，三轮）

- Table 1 G-SM/MOEA-3 四密度数字：tex 904-930 逐行读；增幅由印刷均值复算（0.722/0.698=+3.4%、0.735/0.597=+23.1%、0.756/0.623=+21.3%、0.786/0.680=+15.6%）。
- 稳健性对照：tex 1259-1309 整段读（初始化/预算+随机初始化）；1260-1263、1296-1300、1300-1309 引文逐字核对。
- 消融变体 B/C：_ablation_section.tex 119-146 整段读；消融节以 `\input` 于 tex 1231 引入。
- 章节结构实测（grep \section/\subsection）：1075 Mechanism of Pareto Compression、1234 Robustness and Calibration、1314 Discussion、1315 Summary of Findings、1459 Limitations——故 1346-1348 属 §7.1（非面板所称 §6.6），消融节不称 §6.4。
- R7 成本实测：`run_replicate_variance.py` L35 SCENARIOS=4（每类 1 场景）硬编码、L37 REPEATS=5；快照 seed00-09 为场景实例种子（同标签 n_targets 同、pkl_sha1 各异）。
- R8 数据面实测（两轮）：`_snapshot_moea2obj_full300.json` 条目含 `n_targets/n_selected/selected/t_actuals`（solver=c1_moea_2obj_f1_f2）；**`_snapshot_gapbl.json` 实开 solver 字段全为 `b2_profit_bl_seeded`（=GA-P-BL，含 selected，S1-A_seed00 f1=1.0）——文件名不指 G-BL**；`baselines_200.json` 按场景键含 b1/b3（G-BL/G-SM）仅计数无 selected；`_snapshot_moea3/_snapshot_abn_*` 在盘。
- R10 锚实测：yaw/Doppler/PRF 句在 tex 521-527，56.5 MHz 在 tex 717；tex 425-431 为 NESZ 代理/sinθ 段；R12 sinθ 两处锚 tex 426-427、432-433。
- R9 锚实测：Fig.7 caption 在 tex 1155-1164。
- R4 反限定实测：tex 1207-1212 同句含 Cliff's δ=+0.03 negligible 与「marginal value … is bounded」。
- highlights.tex 头部约束实测：「3-5 bullet points, each ≤85 characters」，现 4 条。
- 复现口径实测：§5.4 tex 849-861（三种子分工 + bit-identical at S1/S4 + SD≤0.004）；`replicate_variance_20261031/_progress.json` 40 条在盘（4 场景×2 求解器×5 repeat）。

## 回扫处置台账

### 轮 1（17 发现）

| F# | 严重度 | 前提核验 | 处置 |
|---|---|---|---|
| F1 | 高 | **部分成立**——证据②（variant-D=热启动否定对照非覆盖压力正面测量）成立已采纳；证据①的指称解读不成立（确认轮 3.1 独立裁决撤销：「margins below 2%」四处同形固定指质量边际 tex 51/143/1530/1299；A–D f1* 差 0.12-0.44% 与 so 句逻辑不合；直接先行是 quality shift ≤+1.64%） | Q1 α 证据链改写为排除法结构并注明量级性排除 |
| F2 | 高 | 成立（roadmap R12 行与不纳入节自相矛盾，r1 稿原样继承） | R12 拆开：sinθ 项按 UNSUPPORTED 主判先核后定（r3 补两处锚）；+94% 代数与模糊 NESZ 两保留项补进清单 |
| F3 | 中 | 成立（§7.2 自己印 63% at S4） | 「近半」改四档 49/65/71/63（r3 修类标签 S1-S4） |
| F4 | 中 | 成立（because 从句 1530-1533，原范围会吞主张留半句） | R2 目标改「改写 1530-1533 because 从句，保留 1528-1530 主张」 |
| F5 | 中 | 成立（脚本 L35/L37 实测；seed=场景实例种子） | R7 成本改「中等成本跑批≈400 次求解」+ 实例种子/重复求解口径提醒 |
| F6 | 中 | 成立（521-527/717 实测；425-431 为 NESZ 段） | R10 锚改 521-527+717；R2-12 运行约束并入 R10 清单 |
| F7 | 中 | 成立（聚合结论；R1 计数细节自纠——单条两句不新增条目） | 新增「亮点层统一预算」节（r3 改按字符预算建模，N4/N7） |
| F8 | 中 | 成立（1207-1212 同句 δ=+0.03 negligible、bounded 实测） | R4/Q2 保留理由改限定口径，+0.32 不单独当论据 |
| F9 | 低 | 成立（章节头 grep 实测） | 消融节定位改文件名+\input 行 1231，不写节号 |
| F10 | 低 | 成立（1346-1348 在 §7.1，1315 起实测） | R2/Q1 标签改「§7.1 Summary of Findings (5)」 |
| F11 | 低 | 成立（caption 1155-1164 实测） | R9 三锚补 caption 行号 |
| F12 | 中 | 成立（81-82「not a single overflight」与 single-flyby 相反） | R11 候选改「single-satellite, two-orbit horizon」方向，禁 flyby/overflight 词 |
| F13 | 低 | 成立（结论 1522-1525 未点名 G-BL） | R1 目标注明基线限定随 R5 同步，不预支「已同口径」 |
| F14 | 低 | 成立（§7.4 1481-1486 已条件口径；because 句在 §8） | R2 的 §7.4 改为「统一参照不改」 |
| F15 | 低 | 部分成立（MOEA-2 快照确不覆盖五求解器；gapbl/moea3/abn_* 在盘） | r2 范围限定已做，r3 修数据面归属（见 N1） |
| F16 | 低 | 成立（题面文件缺失，答案无法回题面核验） | Q1/Q2/Q3 题面原文全部回填本文档（源自旧版 sidecar，主线程会话内留档）；r2 台账「r1 覆盖时误删」措辞有误——实为主线程重写裁决书时未保留题面，r1 是只读轮不可能覆盖 |
| F17 | 低 | 成立（复算 +23.1/+21.3） | 数字修正并注明由印刷均值复算 |

### 轮 2（4 须修 + 7 exploratory）

| # | 严重度 | 前提核验 | 处置 |
|---|---|---|---|
| N1 | 中 | **核心成立**（`_snapshot_gapbl` solver 全 `b2_profit_bl_seeded`=GA-P-BL、含 selected，实测复核；baselines_200 仅 b1/b3 计数）——但审者「S1-A_seed00 f1=0.6458」细节不成立：实测该条 f1=1.0，0.6458 是 replicate 文件 MOEA-2 rep00 的值 | R8 数据面归属反向修正：GA-P-BL 有 selected（gapbl 快照）、G-BL/G-SM 无（仅计数），范围=MOEA-2/MOEA-3/GA-P-BL |
| N2 | 中 | 成立（§5.4 tex 849-861 实读 + replicate_variance_20261031/_progress.json 在盘实测；「8%」无出处弃用） | R5/Q3 成本论据改 §5.4 三种子分工口径 + replicate 实测极差 ≤1.0%/1.36% |
| N3 | 低 | 成立（四值对应 S1-S4） | 括注改「S1 至 S4」 |
| N4 | 低 | 成立（4→5 合法，真约束 85 字符） | 统一预算节改按字符预算建模，R14 理由改字符预算并标注对 roadmap 的范围收窄 |
| N5 | exploratory | 成立（r1 只读不可能覆盖；重写者=主线程） | 台账 F16 行措辞修正（本表上方） |
| N6 | exploratory | 成立（串在 1474-1477） | R3 锚改 1474-1477 |
| N7 | exploratory | 成立（字符预算未建模） | 统一预算节 + R1 目标补字符预算口径（须删词、牺牲部分限定语） |
| N8 | exploratory | 成立（cosψ_sq 对齐块去向未交代） | R2 补「第二机制保留、归前半句机制描述、不得删除」 |
| N9 | exploratory | 成立（EN tex 1494 有一处 downlink 泛提） | R10 措辞改「ZH 四词零命中；EN downlink 一处为 Limitations 泛提」 |
| N10 | exploratory | 成立（贡献 #4 在 179-184） | R4 锚改 tex 179-184 |
| N11 | exploratory | 成立（两处均在 425-437 内） | R12(i) 补两处锚 tex 426-427、432-433 |

### 轮 3（PASS，7 exploratory 全部吸收）

| # | 内容 | 处置 |
|---|---|---|
| M1 | S5/S6 全稿零命中，747-749 实讲 S7/S8 | R11 改「S7/S8 中间类命名与排序说明（roadmap 旧称 S5/S6）」 |
| M2 | 极差分母口径未声明（max vs 均值） | R5/Q3 补「均值口径」标注 |
| M3 | replicate 与主跑快照同实例不一致（f1 0.7396/1.0 vs 0.6458/0.8333；f3 系统性偏低；候选成因=solver 版本/口径漂移） | **R7 增执行前置**：写可复现口径段前先做主跑 vs replicate 对账。**2026-11-04 对账完成，前置解除**：原「不一致」系误用 8-06/08-07 RDR-066 旧口径淘汰件（`_snapshot_*.json`）作主跑；现行正文数据源（`moea_2obj\|moea_3obj/_progress.json`，8-14 新口径重跑）与 replicate 同实例对比 = S1/S4 逐位一致、S2/S3 在 1e-3 级 repeat 波动包络内、无系统方向，无 solver 版本/口径漂移，闸过。证据链与复核命令 → `reconciliation-r7-m3-20261104.md` |
| M4 | Q1 α 括注量纲张力（位移上限 +1.64% > 边际 0.7-1.1%，严格读预算解释未封死） | Q1 α 补「强度边界」段：排除是状态级判断非量级级证明，改写不升格 |
| M5 | 「题面原文」身份盘上不可核 | 三处题面标注改「转录自旧版 sidecar（会话内留档）」 |
| M6 | 预算节未给逐条字数；R1 第三个数字无落点 | 统一预算节补四条余量实测（78/75/84/82）+ +6.2% 落点规则 |
| M7 | R14 主次因未分（条目数决策 vs 字符预算） | R14 改主因=条目数口径、次因=同条字符，附 79 字符候选证伪「字符不可行」 |
