# REVIEW_INDEX — single-sat-quality 小论文审查追踪

状态：pending → fixed → closed-with-evidence ｜ rejected = 裁决为不采纳 ｜ superseded = 被新批次取代（注明取代者）｜ waived = 作者豁免（附理由）｜ deferred = 延期（附 owner+触发）

## 2026-11-03 批次：ARS 五席异源面板（claude -p × 5：EIC/R1/R2/R3/DA）+ 确认轮

明细见 [ars-panel-20261103/](ars-panel-20261103/)（五席报告 + 确认轮 + 编辑部决定）。背景：11-01/11-02 两批改动（镜像 4 处 + 3 条文献、第 6 章补图重排、图 3/4/6 与 N50 修正）后的面板重跑；面板前预闸实跑（数字闸 219 断言 0 失败、快照 1800 条重建、全量硬审计 1800 解 0 问题、四审计套件）。

65 条发现（3 CRITICAL / 29 MAJOR / 33 MINOR），确认轮 50 SUPPORTED + 15 DUPLICATE、0 误引。席位信号：EIC Minor、R1/R2/R3 Major、DA 主张收窄。决定 **Major Revision**，主因三类：① 前沿层（亮点/摘要/结论）与正文自证互相打架（亮点把 +40% 归给第三目标、受控值实为 +4.9%；密度边界在结论说成物理必然、§6.6 认作热启动条件性；前沿层从未说明证据来自仿真场景）；② 承重测量依赖论文自认有条件的设置（200 任务人为上限、热启动、弱基线）；③ 第三目标的价值机制与自身消融不符（入射角通道惰性，价值实由斜视通道承担）。修改路线 8 条见编辑部决定。

**裁决（2026-11-03，受托代填 + 异源审查闭环）**：[author-adjudication-20261103.md](author-adjudication-20261103.md) 已 **CONFIRMED**——R1-R14 全部 will_address；三个口径问题已答：Q1 密度边界=分层口径（质量边际消失归覆盖压力[状态级排除法]、锚收敛归热启动条件性）、Q2 价值主通道=斜视（入射角限 per-window 惰性、跨窗口通道保留）、Q5→R5 走收窄+G-SM 交换率零成本支路（混合基线列二审备选）。回扫三轮（opencode/deepseek-v4.1-flash-free，发现 17→4须修→PASS，报告 `.scratch/adjudication-20261103/report-r1..r3.md`）；R7 执行前置=先做主跑 vs replicate 对账（轮 3 M3 实测两者同实例不一致）。待办：按 [revision-roadmap-20261103.md](revision-roadmap-20261103.md) 执行 R1-R14（R1-R4 纯文字零成本先行）；作者可逐条推翻裁决。

**执行进度（2026-11-04，批 2+3 修订会话）**：R7 前置对账完成并 **M3 勘误**——轮 3「同实例不一致」系误用 8-06/07 RDR-066 旧口径淘汰快照作主跑；现行正文数据链（`moea_2obj|moea_3obj/_progress.json`）与 replicate 同实例 S1/S4 逐位一致、S2/S3 在 1e-3 级 repeat 包络内无系统方向，**无 solver 版本/口径漂移，闸过放行扩容跑批**（证据 [reconciliation-r7-m3-20261104.md](reconciliation-r7-m3-20261104.md)；commit 7142ec7）。跑批扩容（每类 10 场景×5 repeats×2 求解器=400 次）后台执行中（`replicate_variance_20261104`，最小单元逐位复现 10-31 已知值）。文本批全落：批 1=R1-R4（2f241e3，11-03）；批 2=R9（405a65f）/R5（c0bbdd5）/R6（f01c64a）；批 3=R10-R14+R8 丢弃质量+R12 收尾（0697dbf）——DA-13 实算裁决：per-task 分量 pooled range 0.6533（正文 0.65 对）与调度级 HV 界 0.11–0.56 为两层对象，消歧句落 §6.4；R8 新口径（窗内最优 cos³ξ）：dropped 可达上界高于 retained（S1 0.92 vs 0.80）反证 cherry-picking 机制。数字闸 219→245 断言 0 失败；EN 49 页/ZH 39 页 0 错 0 悬空。**剩余**：跑批落地后 R7 可复现口径段+重复运行证据段（措辞依赖批结果）。

**收尾（2026-11-05，R7 落地 → R1-R14 全闭）**：扩容跑批 400/400 完整后重写 §5.4（EN/ZH，4e11ee0）——分层事实：聚合层复制子集类均值移动 ≤0.0041/0.0032（S2-S4）/0.0082（S1 f2/f3）、f1 最差对 0.033，最小相邻类差 0.006 仍超移动一个量级 → 结论不动摇；场景层 91% 包络覆盖、最大偏差集中稀疏类；seed07 跨进程 3 局部解（探针 10 次，`experiments/probe_process_entropy_seed07.py`）+seed08 连内分裂如实披露；进程熵来源诚实声明 not identified。数字闸 rep-* 4 条（小样本期望）替换 rep2-* 34 条（274/0）+fingerprint 改指 20261104 批。异源环两轮核查（deepseek 12 项+mimo 2 项+2 微瑕）全处置（`.scratch/ring-20261104-review/aggregate-r7check.md`）。EN 49/ZH 40 页 0 错 0 悬空。R116（fig2 钉种子）按裁决维持挂账（未触图件脚本）。

**R116 已兑现（2026-11-06，f40ce1f）**：R112 批触 `experiments/gen_all_figures.py`，按移交义务一并 钉种——`:257` 全局 `np.random` 换 `default_rng(20261106)`；同批 R112 删硬编码 GROUP_N 改读 `experiments/results/n50_logistic.json` 的 `group_N` 单源（缺文件/缺键双 SystemExit）。证据：改前连跑 fig2 PNG 哈希漂移、改后三连跑 7/7 PNG 全等、6 个非目标图与改前像素逐字节一致（仅 fig2 按裁决变化）；EN 49/ZH 40 页重编 0 错（ZH 须 xelatex）。



## 2026-10-31 批次：ARS 五席异源面板（claude -p × 5：EIC/R1/R2/R3/DA）+ 修复 + 确认轮

明细见 [ars-panel-20261030/](ars-panel-20261030/)（五席报告 + 确认轮报告）。背景：投稿（2026-09-23）后例行全面检查；前置修复数字闸 caliber 误拦（commit 0f7e6ca，双树等价锚 test_paper1_solver_equivalence_pin + 白名单挂证据）。26 发现全命中引文探针（0 编造），裁决 25 修 + 1 数据验证后强化（R1-02 variant-A-only +37.2/+3.5/+0.4/+0.3% 入 §5.1，verify 闸 189→193 断言）+ 1 挂用户（标题 NESZ 命名，未动）。修复批 commit `3faa8d2`（EN+ZH 双版 19+19 处措辞层，既有数字零改动；闸 193/0 + EN 48p/ZH 38p 双编译 0 undefined + pytest 191 + 旧句双版 grep 0 残留）。收敛簇：f₃ 头部 proxy 口径（EIC-01/DA-01/R2-02）、光学迁移假设化（三席同句）、普适语限定、密集场景操作建议拆分。定向审查两次拦截有价值产出：票 00 草稿 BLOCK（实锤 pymoo 算子熵取种致小预算不可复现→熵 RNG 钉死修法）、票 01 闸块 APPROVE（键结构/过滤/四数字独立复算核验）。

| ID | 问题 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| P1030-A/B/C/D | 四收敛簇 + 19 单点发现（明细见台账 disposition-ledger.md，随 .scratch 归档） | 五席面板 | 6 Major / 14 Minor / 余部分采纳 | **closed-with-evidence**（3faa8d2 + R2-04 终态修正 commit；确认轮 Part A 23 resolved/3 landed-incomplete/0 not-resolved——其中 R1-01/R1-02 为喂料范围伪缺口（闸证据在 patch 外，实跑 193/0），R2-04 真缺口已修并独立复核；Part B 仅 1 MINOR 即 R2-04，已修；无 CRITICAL/MAJOR 回归） |
| P1030-FORM | 公式根基核查（用户令）：F1 重推+F2 文献+主线程数值三方交叉，12 条公式 | 票03 | — | **closed-with-evidence**（e6afada：零根基级公式错误，判定表 review/formula-verification-20261031/cross-verification.md；2 处措辞微修落地；F1-#9 驳回=核查简报符号注解错，教训入记忆） |
| P1030-F3VAL | 根因回查唯一表象级处置（f₃ 跨窗有效性改口未验证）→ 补验证落文 | 票04/用户确认 | — | **closed-with-evidence**（构造性保序=单调性必然；真因子增益 +94.3% vs 代理 +40.4%，代理读数保守；脚本+工件+闸 tnf-* 2 断言，见 cross-verification.md 附记） |
| P1030-TITLE | 标题 "Balancing Profit, NESZ, ..." 的 NESZ 命名是否加 proxy 信号 | EIC-01 | — | **pending-user**（投稿后标题漂移敏感，默认不动） |
| P1030-RES1 | R1-02 残余：耦合趋势 variant-A-only 复核 | 本席台账 | P3 | **closed-with-evidence**（aca37b8：A-only r=−0.80/−0.23/−0.15/−0.31，趋势成立入 §5.1，闸 corr-aonly-* 4 断言） |
| P1030-RES2 | R1-07 残余：重复运行量化 within-instance 方差 | 本席台账 | P3 | **closed-with-evidence**（commit 见 RES1 同日：40/40 单元，S1/S4 逐位全同、S2/S3 SD≤0.004≤类间 7%，§5.4 量化句，闸 rep-* 4 断言） |

> **2026-08-18 终验回填**：2026-08-17 及以前各批次所有 `fixed` 项经终验闭合——verify_paper_numbers 165/0 + CALIBER OK、预闸 M1 全绿（cross_solver_audit 70/0、audit_gapbl_saved/audit_moea_live 0 违规、_audit_window_c1_continuous 76190 窗 0、_audit_full_hard 1800 解 0）、ARS panel 2026-08-15 re-review 推荐 Accept（commits c9f9fa8/947836b/3372e2e）、EN pdflatex 41p / ZH xelatex 33p 双编译。下表旧批次状态列统一由 fixed 转 closed-with-evidence；各项原始修复证据保留在括注中。个别数值项的具体数字后被 08-12 口径修正/全量重跑取代，以当前论文 + verify gate 为准，底层问题均已闭。


## 当前批次：2026-07-31 三家 agent 审计（Qwen r3 / Workbuddy v4 / Trae v4-v6）+ 人工核验

明细见 [rdr-001-threeagent-audit-20260731.md](rdr-001-threeagent-audit-20260731.md)

| ID | 问题 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| A1 | 摘要 statistically→practically indistinguishable | Qwen N1 + WB C01 | P1-Critical | closed-with-evidence（中英；2026-08-18 回填） |
| B1 | "bound" 残留 6+1 处 → saturation/constrain/delimit | Trae 2.1 + Qwen L1 | P1 | closed-with-evidence（中英；L961 为人工核验补漏；2026-08-18 回填） |
| C1 | 零多普勒→低入射角因果链 | Trae 2.2 + Qwen L2 | P1 | closed-with-evidence（中英；2026-08-18 回填） |
| C2 | L216 绝对化声明 + decomposed vs composite | WB C02（人工升级） | P1 | closed-with-evidence（中英；2026-08-18 回填） |
| F1 | tab:hv 零引用 + 碎片句 + "among the three tabulated solvers" | Trae 2.4 + WB C05 + Trae v5 D4 | P1 | closed-with-evidence（中英；2026-08-18 回填） |
| D1 | 消融 B 符号 +9.5% → Δ=−9.5% | Trae 2.5 | P1 | closed-with-evidence（中英；2026-08-18 回填） |
| D3 | 经验 r 池化口径说明 | WB C03 | P1 | closed-with-evidence（中英；2026-08-18 回填） |
| D5 | L855 76±20 → 76±14--20 | Trae D2 | P2 | closed-with-evidence（中英；2026-08-18 回填） |
| N1 | §7.1 "physical limits" → geometric properties（含 (2) 经验效应限定） | Trae v6 N1（升级） | P1 | closed-with-evidence（中英；2026-08-18 回填） |
| N2 | L595 timing 悬空承诺 → uniform computational environment | Trae v6 N2 = 人工 E2 | P2 | closed-with-evidence（中英；2026-08-18 回填） |
| N3 | 变体 D r≈+0.95 数据指针 | Trae v6 N3 (=v4 D3) | P2 | closed-with-evidence（中英；2026-08-18 回填） |
| N5 | L904-907 同义反复合并 | Trae v6 N5 = Qwen T3 | P2 | closed-with-evidence（英；中本无此病；2026-08-18 回填） |
| N6 | 消融节 \paragraph→\subsection（英文） | Trae v6 N6 | P2 | closed-with-evidence（英；中本为 subsection；2026-08-18 回填） |
| B2 | definitional/factorized null 统一（L862 definitional coupling 按 N8 裁决保留） | Qwen N2 + Trae v6 N8 | P2 | closed-with-evidence（中英；2026-08-18 回填） |
| B3 | 消融 "geometric upper bound" → saturation | Qwen N3 | P2 | closed-with-evidence（中英；2026-08-18 回填） |
| B4 | L152 resolution → quality index（L1090 按 N7 裁决保留，与标题一致） | Qwen m1 + Trae 2.19 | P2 | closed-with-evidence（中英；2026-08-18 回填） |
| F3 | Table 6 caption → sec:evaluation-metrics（新加 label） | Trae 2.16 | P2 | closed-with-evidence（中英；2026-08-18 回填） |
| F4 | Pareto-sufficient 贴标应用（δ=+0.55, p<1e-34） | WB C04 | P2 | closed-with-evidence（中英；2026-08-18 回填） |
| E3 | at-least-one 约束非激活说明 | Qwen N7 | P2 | closed-with-evidence（中英；2026-08-18 回填） |
| 2.12 | Das-Dennis M→n_obj | Trae 2.6 | P2 | closed-with-evidence（中英；2026-08-18 回填） |
| 2.13 | [θ,ψ] 加 two-axis 限定 | Trae 2.7 | P2 | closed-with-evidence（中英；2026-08-18 回填） |
| 2.17 | ∼0.3 m 括注推导（ρ_rg≈5.3 m） | Trae 2.11 | P2 | closed-with-evidence（中英；2026-08-18 回填） |
| 2.18 | material → 0.20--0.46 量化 | Trae 2.12 | P2 | closed-with-evidence（中英；2026-08-18 回填） |
| E5 | LVLH 轴 / A--E 标记 / 摘要数值密度 / N50 操作阈值 | Qwen+Trae P3 组 | P3 | closed-with-evidence（中英；2026-08-18 回填） |
| E6 | Table 1 --- → n/a | WB C08 | P3 | closed-with-evidence（中英；2026-08-18 回填） |
| G1 | zh L911 注释 Wiley → Elsevier | 人工补漏 | P2 | closed-with-evidence（2026-08-18 回填） |
| ZH | 中文版滞后同步：图名×5（悬空→编译失败）、t 检验→Wilcoxon、消融表值与显著性、B/C 不对称段、D 反超段、62% 句、断句、首个 MOEA、所有这些工作、HV 排名 MOEA-2 第一事实错误 | 人工核验（前序轮次欠账） | P0 | closed-with-evidence（2026-08-18 回填） |
| N7 | L1090 resolution 改 quality index | Trae v6 N7 | — | **rejected**（与标题/摘要命名一致；改则制造新不一致） |
| N8 | L862 definitional coupling 并入 factorized null | Trae v6 N8 | — | **rejected**（不同概念：现象 vs 度量工具） |
| E4 | bib 4 条缺 volume/pages | Qwen m4 / Trae 6.2 | P2 | **closed-with-evidence**（CrossRef：Moreira 114(2):183-219；Herrmann pages 1-13；Liu 11(1) 在线优先；Yao 54(6):3512-3524；empty-pages 警告仅剩 Caleiras/Jacquet 两条 workshop/preprint 正常项；2026-08-18 回填） |
| E1 | p_i 分布 / d_i 取值 | Qwen N5 | P3 | **closed-with-evidence**（p_i ∈ {5..10} 由 uniform[0.5,1.0]×10 取整；d_i = 30s 固定；补入 §5.1 中英；2026-08-18 回填） |
| 2.23 | 求解时间量级 | Qwen N6 | P3 | **waived by author**（§5.2 已改 "uniform computational environment"，不再承诺 timing；结论链不依赖时间数据；审稿人若问以 future work 回答） |
| G2 | 论文 "≈40,000 pairs" vs JSON ≈394,000 | 人工补漏 | P1 | **closed-with-evidence**（"≈40,000"→"≈$3.9\times 10^5$ ... at 10s resolution"；脚本 STEP_S=10s 全量迭代，无降采样，论文文字过时；2026-08-18 回填） |
| C07 | 变体 D 反超的 post hoc 解释 → Limitations 加替代拥挤度算子 future work | WB C07 | P3 | closed-with-evidence（中英；2026-08-18 回填） |
| D01 | GitHub 仓库公开可访问性 | WB D01 | — | **closed**（2026-08-10 复核：已 schannel 重新推送 `66c192e..ffd8d44`，远程==本地；push 前 filter-repo 剥除 `.scratch/` 内部文档历史 + git rm 9 一次性 launcher；边界复核无 review/literature/reference 泄漏） |
| D02 | arXiv 2601.11967 / 2604.19539 存在性与标题 | WB D02 | — | **closed-with-evidence**：2601.11967 ✓（Caleiras, 标题匹配）；2604.19539 是同一文献但 bib 标题错误（"Hybrid Direct-Relay Downlink Scheduling" 实为另一篇），已按 arXiv 实际标题 "Efficient Generation and Quality Screening of Visible Windows for Regional SAR Reconnaissance" 修正 bib，作者展开为 Li, Linhong / Feng, Qi / Li, Kebo / Liang, Yangang（2026-08-18 回填） |
| N50 | 补中间密度收紧 CI | Trae P3 | P3 | **closed-with-evidence**（S7 N=150 + S8 N=200 各 50 场景 MOEA-2+G-BL/G-SM 跑完；N50 169→140，CI [111,227]→[117,169]，宽度收窄 55%；中英 §6.3/Table/方法段/结论已同步，双版编译通过。顺带纠正预存 deficit% 错误：S2/S3/S4 真值 62/16/24%，非 64/14/20%；χ² 1.00/p=0.32；2026-08-18 回填） |
| G3 | 轨道高度 600 km 与仿真不符（实际 Sentinel-1 693 km） | 人工补漏 | P1 | **closed-with-evidence**（中英方法段+局限段共 4 处 600→693；倾角 97.8°/LTAN 06:00 本就正确；双版编译通过；2026-08-18 回填） |
| G4 | 测绘带半宽 ±2.7°/±300 km 与代码不符且自相矛盾 | 人工补漏 | P1 | **closed-with-evidence**（代码 get_swath_params(693,47) 实算 ±5.46°/±608 km；中英方法段改 ±5.5°/±608 km，措辞改"half-width"避免误读为指向角；双版编译通过；2026-08-18 回填） |

## 2026-08-01 批次：Workbuddy v5（中文）+ Trae v7（英文）

明细见 v5/v7 报告。Workbuddy 报中文 1×P1 + 6×P2 + 2 待确认；Trae 判英文 0 P1。人工对抗核验全部落地。

| ID | 问题 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| W-C01 | HV 归一化口径同句自相矛盾（"每求解器池化" vs 括号"所有求解器池化"） | WB C01 | P1 | **closed-with-evidence**（中文 L484 删除矛盾括号句，对齐英文 per-solver 表述 + 全求解器池化未采用的理由；英文本就正确；2026-08-18 回填） |
| W-C02 | 花体 𝒮 同指平台与选定任务集 | WB C02 | P2 | **closed-with-evidence**（平台改 𝒫，实例元组 (𝒯,𝒫,𝒪)，选定集保留 𝒮；与英文一致；2026-08-18 回填） |
| W-C03 | HV 图成孤儿（中文 fig:fig4 零引用）；核验发现英文版 fig:fig1 同为孤儿（Trae v7 误把 label 行当引用） | WB C03 + 人工核验 | P2 | **closed-with-evidence**（中英图后引导段各补 \ref；2026-08-18 回填） |
| W-C04 | G-SM "58%/190 任务/损失 80/42%" 分母错配（190 实为 A 列 n_sel 非 G-BL 容量，58%×190≠80） | WB C04 | P2 | **closed-with-evidence**（删拼凑话术，对齐英文 7.2 的 f1\* 口径：39% coverage cost, f1\*=0.61 vs 1.00；2026-08-18 回填） |
| W-C05 | 摘要范围限定弱化（丢单过境/条带/G-BL 热启动/NSGA-III） | WB C05 | P2 | **closed-with-evidence**（中文摘要末句补回四项边界，对齐英文 L61；2026-08-18 回填） |
| W-C06 | 摘要凭空加"多目标导航规划通用图像质量指标"无引用 | WB C06 | P2 | **closed-with-evidence**（删该短语，对齐英文保守表述；2026-08-18 回填） |
| W-C07 | 消融表 S3/S4 Δ% 与两位小数显示值表面冲突 | WB C07 | P2 | **closed-with-evidence**（中文表前加注：百分比基于未舍入均值；英文本有 Δ 公式定义；2026-08-18 回填） |
| T-N1v7 | 英文 p_i 措辞混离散集与连续分布 | Trae N1-v7 | P2 | **closed-with-evidence**（见 G5，统一改为与真实数据一致；2026-08-18 回填） |
| T-N2v7 | Herrmann2023 缺 volume | Trae N2-v7 | — | **rejected**（CrossRef 确认 IEEE TAES Early Access，无 volume/issue，仅 pages 1–13；不编造卷号） |
| T-N3v7 | Liu2024TwoStageDRL 缺 pages | Trae N3-v7 | P3 | **closed-with-evidence**（CrossRef：vol 11 issue 1, article 35；bib 补 pages={35}；2026-08-18 回填） |
| D01-COI | 中文致谢缺刘繁明教授为 Wu2026 共同作者的 COI 披露 | WB D01 | — | **closed-with-evidence**（中文致谢补贡献边界句，与英文一致；按 Elsevier 投稿稿处理；2026-08-18 回填） |
| D02-sync | 中英 25 处表述差异（中文增补 vs 英文独有稳健性表述） | WB D02 | — | **noted**（数字/结论一致，图 label 两版各自自洽；本批次已统一数值与口径，逐句风格对齐非必需，留待定稿） |
| G5 | p_i 取值范围论文写 {5..10}，实际 400 个场景 pkl 均为 randint(1,10)；求解器无重映射 | 人工核验（推翻 RDR E1 的"已核实"） | P2 | **closed-with-evidence**（中英改为 {1,…,10} 均匀整数；f1\* 为 G-BL 归一化相对量，下界变化只改变方差不改排序，已报告数值均在真实 1–10 数据上算出，结论不受影响，无需重跑；2026-08-18 回填） |

## 2026-08-01 批次 v6：Workbuddy 全量深化审查（重点：把前序 "fixed" 拉回数据/工程层复验）

明细见 [archive/20260801_review_report_v6_workbuddy_tw1.3.0.md](archive/20260801_review_report_v6_workbuddy_tw1.3.0.md)。0 P0 / 1 P1 / 4 P2；就绪度 needs_author_input。

| ID | 问题 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| V6-D01 | 变体 D r≈+0.95 无可复现产物：`moea_3obj_no_physics/` 仅 `_progress.json`(_run.log)，只存调度级均值 f2/f3+frontier 均值，无 per-task 几何、无 schedule；per-task 相关无法从已提交数据重算。前序 N3/N3v7 的 "fixed" 只落在括注措辞层 | WB v6（对抗性复验 N3） | P1 | **closed**（2026-08-09 复核：被下方 P0-1/2/3/4 批取代——r 全负、+0.95 为 A/MOEA-3 相关、§6.4 机制段已改写"冲突减弱而非反转"） |
| V6-T01 | S4 MOEA-3 前沿点数 SD 报 ±14，实测 `n_frontier` 为 76.36±17.07（MOEA-2 77.50±20.26，±20✓）。前序 D5 "fixed" 仍与数据不符 | WB v6（对抗性复验 D5） | P2 | **closed**（2026-08-09 复核：被下方 H5 取代——中英 4 处已改 76±17/MOEA-2 78±20/HV 句 76–78 点 SD17–20） |
| V6-F01 | 英文消融图 `fig:fig5`(fig5_ablation.pdf) 成孤儿：英文主稿/消融节均无 \ref；中文对应 `fig:fig6` 已引用（中 L846）→ 中英不对称。W-C03 只修了 HV 图未覆盖消融图 | WB v6 | P2 | **closed-with-evidence**（= H6：消融讨论段补 Fig.~\ref，中英对称；2026-08-18 回填） |
| V6-F02 | `fig4_solver_profiles.pdf` 文件名与内容/图注不符（图注为 Pareto front，内容一致，仅命名误导） | WB v6 | P2 | **closed-with-evidence**（2026-08-10：资产改名 `fig4_pareto_front.{pdf,png,grayscale}`，EN/ZH includegraphics + gen_all_figures.py L408 同步，双版编译通过；2026-08-18 回填） |
| V6-F03 | 中文版图 \label 键名与文件名/英文版错位（hypervolume→fig:fig4 等）；渲染正确、无重复 label、无断链，纯维护隐患 | WB v6 | P2/P3 | **closed-with-evidence**（2026-08-10：ZH 5 个 label + 对应 ref 全部对齐 EN 键 fig1-5，无重复无断链，双版编译通过；2026-08-18 回填） |

本轮正向确认（对抗核验后无问题）：① 两版 \ref 全解析、无断链无重复 label；② bib 25 条全部被引，中英引用键集完全相同，0 缺失 0 未用；③ 5 个图 PDF 全在，两版消融均收录 fig5_ablation.pdf；④ v5 中文修复 W-C01/W-C02/W-C03 均已落地；⑤ 中英摘要关键数值同步；⑥ 包络对数 3.9e5@10s、r_null=−0.51/r_MC=−0.5120、消融表变体 D 均值 f2/f3 均可复现。
carry-over（2026-08-01 时点）：~~D01 需作者重新推送~~ → 已于 2026-08-10 推送 ffd8d44；本机无 pymoo/sar_sim 限制已由重跑完成解除。

## 2026-08-01 批次 v8：Trae v8 + Qwen V1 + 人工核验（中英同步，双版编译通过）

明细见 [archive/comprehensive-review-20260801-v8-traework.md](archive/comprehensive-review-20260801-v8-traework.md) / [archive/full-audit-20260801-qwen-V1.md](archive/full-audit-20260801-qwen-V1.md)。已全部中英同步，pdflatex/xelatex 各 0 error/undefined。

| ID | 问题 | 来源 | 状态 |
|---|---|---|---|
| H1 | cos³(10°)≈0.977 错（实算 0.955）；2–3% level 实为 4–5% | Qwen F1 | **closed-with-evidence**（英；中文无此句；2026-08-18 回填） |
| H2 | L1015 p<10⁻³⁴ 方向错（实 p=1.436e-34 > 1e-34）→ p<10⁻³³ | Qwen L1 | **closed-with-evidence**（中英；2026-08-18 回填） |
| H3 | L604 句首残缺 "a priority weight..." → 补 "Each task is assigned" | Trae P1-1 | **closed-with-evidence**（英；中文本完整；2026-08-18 回填） |
| H4 | L503 δ=+0.72 交叉引用错指 §7.1(sec:summary，无数值) → §6.2(sec:squint-special) | Trae P2-1 | **closed-with-evidence**（英；2026-08-18 回填） |
| H5 | S4 前沿点数 76±14 与 n_frontier 不符（实 MOEA-3 76.36±17.07；MOEA-2 77.50±20.26）；中英 4 处 | WB V6-T01 | **closed-with-evidence**（76±17；MOEA-2 78±20；HV 句改 76–78 点/SD17–20；2026-08-18 回填） |
| H6 | 英文 fig:fig5 消融图孤儿（中文已引用） | Trae/Qwen/WB | **closed-with-evidence**（消融讨论段补 Fig.~\ref；2026-08-18 回填） |
| H7 | 消融节裸 ψ_i → ψ_sq,i（中英各 4 处节内不一致） | Qwen M1 | **closed-with-evidence**（2026-08-18 回填） |
| H8 | 消融节 Das-Dennis n=12 → p=12（对齐主文） | Trae P2-2 | **closed-with-evidence**（中英；2026-08-18 回填） |
| H9 | highlights #2 "upper bound" → "saturation boundary" | Trae/Qwen | **closed-with-evidence**（2026-08-18 回填） |
| H10 | highlights #5 无条件化 "Profit-oriented solvers converge..." → "G-BL-seeded MOEAs converge..."（加 hot-start 限定） | Qwen M5 | **closed-with-evidence**（2026-08-18 回填） |
| H11 | φ 符号过载（L298 纬度 φ_i vs L313 off-nadir φ）→ off-nadir 改 ξ（η 已被 Δη/η_c 占用） | Qwen M2 | **closed-with-evidence**（中英；2026-08-18 回填） |
| H12 | 消融 +32.4% 用舍入值算（未舍入 14.74/11.06=33.3%）→ "about one-third more tasks" | Qwen L5 | **closed-with-evidence**（中英；2026-08-18 回填） |
| H13 | KramerMiller2024 bib 缺 pages（Crossref 62:1–14） | Trae P3-1 | **closed-with-evidence**（补 pages={1--14}；2026-08-18 回填） |
| H14 | 零多普勒因果链补物理括注（closest approach→min slant range→近似 min θ） | Qwen L6 | **closed-with-evidence**（中英；2026-08-18 回填） |
| — | V6-F01 英文消融图孤儿 | WB v6 | = H6 fixed |

裁决不改：
- Qwen L3（Δf1*% 口径）：CSV 的 -23.48% 是 f1_raw 列（表头即 f1_raw_deg_pct），论文 -22.1% 是归一化 f1*，列名已区分，非错误，不加脚注。
- Qwen L4（Table 1 f1/f1*）：表格准确反映各求解器实际优化目标（贪心优化原始 f1，MOEA 优化归一化 f1*），L470 已说明，统一反失真。
- Qwen L8（4 unused label）、Trae P3-2（Δ 符号）、WB V6-F03（中文 label 键错位）：纯偏好/零读者收益且有改动风险，不动。
- WB V6-F02（fig4 文件名 cosmetic）：低优先，定稿再说。
- Qwen L7（manifest.json 过时）：无程序化引用（仅 null_dist_r.py 注释提及其角度范围），不重写以免编造，待作者重建场景时同步。

| V6-D01 | 变体 D "r≈+0.95" 无可复现产物；人工重跑 S1 得 **r=−0.44**（per-task pooled），场景级 −0.92，+0.95 实为物理求解器 A/MOEA-3 的相关。原"结构属性非物理引导"结论方向存疑 | WB v6 + 人工重跑 | **closed/superseded**（旧行；被上方 line 78 及 P0-1 批取代——r 全负、§6.4 机制段已改写、Variant D 重定位为消融对照） |

## 2026-08-01 批次 P0：f2–f3 耦合 "+0.93~0.98" 不可复现（V6-D01 升级）

明细见 [archive/rdr-002-coupling-plus098-unreproducible.md](archive/rdr-002-coupling-plus098-unreproducible.md)。+0.93~0.98 生成脚本在 git 两仓库/backup/旧仓库/全部 .py/全部审查报告中不存在，`r_visible_envelope.py` L107 中为硬编码常量；穷尽所有口径（knee per-task、跨前沿解、跨求解器池化、符号翻转）全部为负。**决定：+0.93~0.98 作废，§6.4/§7.1 finding(2) 机制段改"冲突减弱而非反转"，D 重定位为无引导回到包络水平的消融对照。** 状态 closed（下方 P0-1~P0-4 全 fixed；A S2–S4 数据已补齐、作者确认，D01 闭环见 2026-08-01 v10 + 2026-08-09 §6.4 机制重写）。

| ID | 问题 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| P0-1 | 变体 D "调度内 per-task r≈+0.95" 为假：四类全负（−0.44/−0.59/−0.21/−0.18），原 +0.95 实为 A/MOEA-3 的相关 | 人工重跑（reproduce_variant_d_r.py） | P0 | **closed-with-evidence**（中英改写 + 编译通过；2026-08-18 回填） |
| P0-2 | 论文 §6.4 "调度 +0.93~0.98 正相关 / reversal / active selection" 无任何可复现口径支撑；跨解/跨求解器/符号翻转全部为负 | 人工穷尽 | P0 | **closed-with-evidence**（删 reversal/+0.98/Fisher-z，改"冲突减弱"叙事；2026-08-18 回填） |
| P0-3 | f2_f3_coupling.json n 内部不自洽（S3=69,405 vs S4=4,906），生成脚本丢失 | 人工排查 | P0 | **closed-with-evidence**（加 _deprecated 标注；2026-08-18 回填） |
| P0-4 | 可复现替代叙事：A 调度内 −0.60~−0.69（削弱非反转）、D 跨解 −0.94~−0.98（≈包络）、D 随密度趋零（饱和） | 人工 | P0 | **closed-with-evidence**（A 全密度梯度完成：S1 −0.69/S2 −0.54/S3 −0.20/S4 −0.17；D：−0.44/−0.59/−0.21/−0.18；2026-08-18 回填） |



## 未执行项说明
- ppw 技能链：polish/logic/de-ai 已人工等效执行，三轮自查（R/M/D 归属 / 缩写首现 / 减法）已完成。
- Trae v6 的 2.8（physical limits 术语洁癖）、2.9（句子位置）、2.15（同）等纯偏好项：2.15 已随 N1 合并处理；2.8 按 N1 裁决执行。
- 编译验证（中英双版本 bibtex+2×pdflatex/xelatex）：英文 35 页 0 undefined；中文 30 页 0 undefined。

## 2026-08-01 批次 v7：Workbuddy 全面审查（用户"第三章"改稿后，中英双版 + 数据对抗复算）

明细见 [20260801_review_report_v7_workbuddy_tw1.3.0.md](20260801_review_report_v7_workbuddy_tw1.3.0.md)。0 P0（论文正文）/ 0 P1（论文正文）/ 4 P2；就绪度 needs_author_input。

| ID | 问题 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| 改稿核验 | W-C02 𝒮符号 / W-C01 HV归一化 / W-C03 HV图引用 / G5 p_i范围 / H11 φ→ξ 五项前序中文缺陷 | WB v7 独立读文件核验 | — | **VERIFIED_DONE**（均落地） |
| V7-N1 | 中英漂移：S4/S1 超体积比 <1 论断仅中文 L744 有，英文缺失；且无文中表/图支撑 | WB v7（solver_summary.csv 复算 0.724/0.675<1，论断为真） | P2 | **closed-with-evidence**（v9-closure 已 fixed：英文补镜像句 0.72/0.67；2026-08-18 回填） |
| V7-N2 | 中英漂移：sec:hv-divergence 标签/引用仅中文版存在 | WB v7 | P2 | **P2（可选对齐）** |
| V7-N3 | 数据卫生：r_visible_envelope.json 残留 r_solver_empirical=[0.93,0.98] 且 note 逻辑自相矛盾（r_visible_c7=-0.95 vs "≈0.93"）；f2_f3_coupling.json 仍留 results/ | WB v7（与 trae v9 P2-Repro-1/2 互相印证） | P2 | **closed-with-evidence**（v9-closure 已 fixed：JSON 删脏字段 + 脚本去硬编码；2026-08-18 回填） |
| V7-N4 | 中文版图标签键名错位（HV=fig:fig4 等），编译通过、无断链 | WB v7（=V6-F03/Qwen L8 已裁决不改） | P2/P3 | **superseded**（2026-08-12 S0 对账：=V6-F03 同一缺陷，2026-08-10 ZH 5 个 label 对齐 EN fig1-5 已 fixed） |

carry-over（非本轮新发现）：D01 GitHub 需重推（pushed_at=2026-07-22 早于改稿）；trae v9 代码 P0-Code-1/2（check_numerical.py / check_refs.py 路径构造 bug）；v9 P1-Code-1/2/3、P1-Data-1。
中央主张复算（C-D01~C-D11）全部与 experiments/results 数据一致：HV 池化、Friedman 506.56/2.55e-108、N50 139.62/[117.4,168.5]、包络 r_c7 −0.95x、r_null −0.51/r_MC −0.5120、A/D 调度内 r −0.69→−0.17/−0.44→−0.18、效应量（MOEA-2 vs G-BL f2 δ=0.545/p=1.44e-34 等）、S4/S1 HV 比 0.724/0.675、变体 D Δ=−22.1%、热启动缺口 0.20–0.46。RDR-002 P0 已闭环。

## 2026-08-01 批次 v9-closure：WB v7 + Trae v9 修复落地（含人工对抗核验新发现）

逐条核验后修复，中英同步，双版编译通过（英 36 页 0 undefined / 中 30 页）。代码改动 py_compile + 既有测试 + 定向 smoke 验证。

| ID | 问题 | 来源 | 状态 |
|---|---|---|---|
| V9-P0-1 | `src/tools/check_numerical.py` L6 raw-string 路径 bug，脚本不可跑 | Trae v9 P0-Code-1 | **closed-with-evidence**（PROJECT 指 repo root，路径改 `papers/single-sat-quality/experiments/results`；跑通，输出与论文一致；2026-08-18 回填） |
| V9-P0-2 | `src/tools/check_refs.py` L4 同样 raw-string + 过时 `docs/` 前缀 | Trae v9 P0-Code-2 | **closed-with-evidence**（指 `papers/single-sat-quality/small-paper-ijae.tex`；跑通，MISSING 为不跟踪 \input 的脚本假阳性，PDF 0 undefined 证实；2026-08-18 回填） |
| V9-P1-cover | cover-letter.md 仍写 "empirical upper bound"/"solver convergence"，未与正文 saturation boundary 同步 | Trae v9 P1-CoverLetter-1 | **closed-with-evidence**（改 "empirical saturation regime" + G-BL-seeded NSGA-III 限定 + single-pass Stripmap 范围；2026-08-18 回填） |
| V7-N3 | `r_visible_envelope.json` 残留 `r_solver_empirical=[0.93,0.98]` + note 符号矛盾；生成脚本 L107 硬编码会重写回脏值 | WB v7 + Trae v9 P2-Repro-1 | **closed-with-evidence**（JSON 删字段 + 修 note；脚本 docstring/out/print 同步去硬编码；JSON 合法）。`f2_f3_coupling.json` 已有 `_deprecated` 字段，`cross_solver_audit.py` 仍加载且无活跃调用者，保留原位不移动（2026-08-18 回填） |
| V9-P1-f1gbl | `moea_solver()` 在 pop f1_gbl 前就 `**kwargs` 透传给不接受它的 `build_agile_instance`，传 f1_gbl= 时 TypeError（latent：主实验不传，run_variant_d 调的是 no_physics 变体） | Trae v9 P1-Code-1 | **closed-with-evidence**（pop 提前到 build 调用前；test_moea_c1_f3 4 passed；定向验证旧码必崩、新码顺序正确；2026-08-18 回填） |
| V9-P1-D-narr | §6.4 变体 D 段写 D "weaker attenuation" 且物理目标 "amplified" 低斜视收敛，与论文自身定义（向零移动=attenuation）及实测 r（A=−0.69 移 0.26，D=−0.44 移 0.51）**方向矛盾**——Trae v9/WB v7 均漏报，补 Trae 引导句会盖住矛盾 | 人工对抗核验 | **closed-with-evidence**（中英改写为诚实解读：稀疏区物理目标迫使求解器遍历 f2–f3 权衡故 A 保留更强负相关 −0.69；无物理 D 仅冲利润、时间紧凑性偶然低斜视故残差相关更弱 −0.44；高密度结构紧凑性主导二者趋同 −0.18，消融对比在权衡活跃的 S1 最大；2026-08-18 回填） |
| V7-N1 | S4/S1 HV 比 <1 论断仅中文有，英文缺失 | WB v7 | **closed-with-evidence**（英文补镜像句，给数值 0.72/0.67 + Δf1*≈0.3；中文同步补 0.72/0.67 数值；solver_summary.csv 复算 0.724/0.675 为真；2026-08-18 回填） |

裁决不改（对抗性否决或降档）：
- Trae v9 P1-Intro-1（贡献声明再加范围限定）：摘要末句/highlights/§7.3 已四重限定，再加冗余，**不改**。
- Trae v9 P1-Code-2（地球半径 6378137 vs 6371000）：真实但 nesz.py:69 已注释说明，入射角差 <0.05°，对结论无影响，**降 P3/可选**，本轮不动。
- Trae v9 P1-Code-3（HotStart 未固定种子）：README 已声明 not bit-reproducible，**wontfix**。
- Trae v9 P1-Code-5/C7 验证器、P2 代码重构/重复、P3 项：投稿后技术债，本轮不动。
- V7-N2（sec:hv-divergence 标签仅中文）、V7-N4（中文图 label 键错位）：编译自洽、零读者收益、有断链风险，**deferred**。

carry-over（需作者动作）：**D01 GitHub 重新推送最终代码**（pushed_at=2026-07-22 早于本轮 + RDR-002 修复；Data Availability 指向该仓库）——push 涉意外发，由作者执行。

## 2026-08-02 批次：ppw-logic + ppw-de-ai + 数据/引用准确率复核

三家 pass：① ppw-logic 全稿逻辑验证；② ppw-de-ai AI 味扫描；③ 数据/引用/摘要准确率核对（重算每单元格 + 全部 25 条 bib 交叉核对）。报告：`small-paper-ijae_logic.md`、`small-paper-ijae_accuracy_20260802.md`。

| ID | 问题 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| AC-1 | §2.2 "Both degrade as observation departs from zero-Doppler" — ρ_rg 说反了（零多普勒处 ρ_rg 最差而非最好），与 §3.2 内部矛盾 | ppw-logic | P1 | **closed-with-evidence**（中英；EN L237 / ZH L172 拆开讲 ρ_az vs ρ_rg 方向，指出即 §3.2 θ 轴权衡起源；2026-08-18 回填） |
| AC-2+M3 | §6.4 Phenomenon 1 两段重复（压缩主张 + 0.06 vs 0.10 数字各说一遍；"The important result is therefore not X, but Y" 戏剧性转折） | ppw-logic + ppw-de-ai | P2 | **closed-with-evidence**（中英；合并为一段 + 图后一段，删除重复与修辞转折；2026-08-18 回填） |
| AC-3 | §7.1 五项发现列表前已声明 "four findings reflect …" 而列表后又重复 "The first four reflect …"；列表后又整段散文体重述全部五项 | ppw-logic | P2 | **closed-with-evidence**（EN；删列表前重复导语，列表后砍散文重述段落，补一句 GA-P-BL 单目标增益 delimitation。ZH §7.1 结构不同，未重；2026-08-18 回填） |
| AC-4 | Intro 贡献 1 把热启动条件性归给消融研究，实际由 §6.6 对照确立 | ppw-logic | P2 | **closed-with-evidence**（中英；拆分归属：消融→high density 不变性；初始化对照→热启动条件性；2026-08-18 回填） |
| NC-1 | Table 3 20 均值全部正确；60 个 SD 格中 29 个 = ddof=0（总体标准差）而非论文其余处用的 ddof=1；唯一可见表-文矛盾：G-SM S4 f3 0.074 vs 0.075。消融表 n_sel SD 与 f1* SD（D S1 0.33 vs 0.34）也是 ddof=0 | 数据重算 | P2 | **closed-with-evidence**（中英；Table 3 与消融表 SD 列全改为 ddof=1；gen_table1.py 补 `from pathlib import Path` 修导入；2026-08-18 回填） |
| M1 | §6.6 四个对照实验末尾都用 "\textit{This control isolates X, not Y}" 同结构斜体收尾 | ppw-de-ai | P2 | **closed-with-evidence**（中英；去斜体，句式变化；2026-08-18 回填） |
| M2 | 消融节 "warrants closer examination" | ppw-de-ai | P2 | **closed-with-evidence**（中英；改为直接陈述 "its mechanism is visible in the task counts"；2026-08-18 回填） |
| UC-1（升级为 P0） | 中文版 L463–465 称"约 50%–60% 的可见窗口包含零多普勒穿越……所有类别中 ≥40%"——实测 200 场景 / 45,345 窗口统计为 **15.1%/17.2%/14.9%/14.9%**（中位数 min |ψ| 27°–30°），差 3–4 倍 | Pass 3 数据复核 + sar_sim 几何实测 | P0 | **closed-with-evidence**（ZH 改为 15%–17% 实测值；EN 本无此主张，无需改；2026-08-18 回填） |

**验证**：EN pdflatex 3 遍 0 undefined（35 p），ZH xelatex 2 遍 0 undefined（30 p），bibtex 0 errors。引用 25/25/25 完美对合；Friedman 506.56、效应量 δ 全部、deficit 比例、S7/S8、12 个消融 Δ% 全部重算核对一致。

## 2026-08-02 批次 v8：Workbuddy 全面审查（用户未提交改稿，v8/v9/ppw 修复中英落地 + 数据复算）

明细见 [20260802_review_report_v8_workbuddy_tw1.3.0.md](20260802_review_report_v8_workbuddy_tw1.3.0.md)。0 P0（正文）/ 0 P1（正文）/ 1 P2；就绪度 needs_author_input。

| ID | 问题 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| 改稿核验 | 本轮未提交 diff：贡献归属拆分(AC-4)、§2.2 ρ方向(AC-1)、Table3/消融表 SD ddof=1(NC-1)、§6.4合并(AC-2+M3)、§6.6去斜体(M1)、§7.1 EN重组(AC-3)、消融 D 改写(M2)、ZH §5.2 零多普勒比例(UC-1) — 全部中英落地 | WB v8 独立读 diff | — | **VERIFIED_DONE** |
| 复算-Table3 | f2/f3 全 20 格均值±ddof=1 SD 从原始 _progress.json 复算，逐格吻合 tex | WB v8 | — | **VERIFIED_DONE** |
| 复算-消融SD | ablation_summary.csv std(ddof=0)×√(50/49)→ddof=1，吻合 tex | WB v8 | — | **VERIFIED_DONE** |
| 复算-交叉引用 | 新加 sec:objective-functions / sec:robustness-calibration 两 ref 均有 label，无断链 | WB v8 | — | **VERIFIED_DONE** |
| V8-N1 | 中英 §7.1 结构漂移：EN 改 5 项列表+GA-P-BL delimitation，ZH 未同步（仍留导语+”首先，求解器调查显示了一个清晰的排序”散文段，且 4 段枚举对不上 EN 5 项） | WB v8 | P2 | **closed-with-evidence**（2026-08-09 复核：ZH §7.1 现为五段枚举 \textbf{(1)}--(5) + GA-P-BL 限定句，散文段已删，与 EN 结构一致；2026-08-18 回填） |
| UC-1-溯源 | 45,345 窗 / 15.1/17.2/14.9/14.9% / 27–30° 在仓内无生成脚本（应出自 sar_sim，经 Data Availability 指 GitHub） | WB v8 | P2 | **fixed**（2026-08-05 重算：实际 76,190 窗、min|ψ| 中位 7–9°、穿越率 0%；45,345/15.1%/27–30° 系人工核验算错，无任何版本来源；中文 §5.2 改可复现口径，脚本 zero_doppler_stats.py） |

裁决不改：RDR-002 闭环、V7-N1/V7-N3 已在 v9-closure fixed 无回归；V7-N2/V7-N4 仍 deferred（编译自洽、零读者收益）。
carry-over：D01 GitHub 需重推（pushed_at=2026-07-22 早于全部修复）。

## 2026-08-02 批次：两份审查报告（qwen full-audit / trae v11）对抗性验证 → 自掘出求解器可行性缺陷簇

对 `full-audit-20260802-qwen.md` 与 `comprehensive-review-20260802-v11-trae.md` 逐条回源验证。两报告收敛项（遗传算子参数、2N 编码描述、图脚本命名）为真；qwen 4/6 个 🔴 夸大（manifest 死文件、compile.bat 有缓存 .bbl）、trae T-1（L1017 indistinguishable）为假阳性（误读句子主语，实指消融 A–D 预算对照）。验证过程中实跑 ConstraintVerifier 掘出两份报告均漏的 P0 缺陷簇：

明细见 [rdr-003-gsm-unconstrained-squint-argmin.md](rdr-003-gsm-unconstrained-squint-argmin.md) / [rdr-004-c3-penalty-delayable-loophole.md](rdr-004-c3-penalty-delayable-loophole.md)。验证脚本：`experiments/verify_gsm_c3_v2.py`、`experiments/audit_gapbl_saved.py`、`experiments/audit_moea_live.py`。

| ID | 问题 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| G-SM-1 | G-SM squint argmin 跨全过境无过滤 → 21–35% 观测落在不可见时刻（θ→0.2°、不属于任何窗口）+ C1 θ<15° + C3 缺额 17–53s；S2 起 30/30 场景受影响；重跑与 baselines_200.json 逐位吻合（论文数据同源） | 人工实跑（升级 qwen 🟡-8） | P0 | **closed**（2026-08-10 复核：全量重跑 + squint 段/fig2/δ 重写完成——§6.2 Squint-Aware Special Regime 现数据 G-SM f3 +2%/+12%；S7/S8 完成、Table1/§6.3/§6.6/摘要回源通过，提交闸门 08-09 全绿） |
| C3-1 | 进化族 C3 罚函数"B 可延迟即豁免"，解码时刻从不执行 → GA-P-BL 存盘解 42.8% 相邻对硬重叠（218 场景全量）、MOEA-2/3 实跑 1–13% 重叠、三消融 runner 同模式 | 人工实跑（两报告均漏） | P0 | **closed**（2026-08-10 复核：进化族全量重跑完成；GA-P-BL f1*=1.18 待复核 → 被 GP-1 取代——GA-P-BL=G-BL 逐位相同为设计行为（不劣于基线守卫恒触发），已文档化披露，非 f1*=1.18；全部表图用窗口修复后数据重算，回源通过） |
| OP-1 | 遗传算子论文-代码不符（ηc 20 vs 15；pm 0.1 vs 1/(2N)；MOEA 走 pymoo 默认） | qwen 🔴-1/2 + trae §5.1/5.2 收敛，已验证 | P1 | **closed-with-evidence**（2026-08-04 复核：so_f1.py:541 GA-P-BL 与 moea.py:595-601 均实为 SBX(0.9,20)+PM(0.1,20)，与论文 L529-531 一致；round-3 "代码向论文对齐" 成立，论文无需改，closed；2026-08-18 回填） |
| ENC-1 | 论文称染色体仅编码 τ、x "emerges from constraint resolution"；代码 2N 编码 x+τ 均为决策变量（trae 独有发现，qwen 漏，已验证） | trae §5.3 | P1 | **closed-with-evidence**（中英 §4.3 改 2N 编码描述，"emerges from constraint resolution" 删，编译通过；2026-08-18 回填） |
| FIG-1 | gen_all_figures.py 输出名与论文 \includegraphics 全错位 + fig3 不生成（已验证；figures/ 为手动重命名产物） | qwen 🔴-3/4（降 🟡→公开仓库卫生 P2） | P2 | **closed**（2026-08-09 复核：fig1-5 全在且命名匹配论文引用；gen_all_figures.py 已输出 `fig{i}_*.pdf`；submission-gate 重生成 fig3 字节级未变、fig2 仅 12B，生成链路可用） |
| 驳回 | trae T-1 L1017（上下文为 A–D 预算对照非 MOEA-2/3）；qwen 🟡-1（s3_s4_control.json 无 delta_std 字段，证据源不存在）；qwen 🔴-6 manifest（零引用死文件）；qwen 🔴-5 compile.bat（.bbl 缓存存在，编译正常）；trae §5.4 约束编号（代码注释内部约定）；trae P3-1 摘要 SAR 展开（ASR 领域惯例无需） | 人工对抗验证 | — | **rejected** |
| GP-1 | GA-P-BL 输出与 G-BL 逐位相同——"不劣于基线"守卫在单利润目标恒触发（非退化，设计行为） | 2026-08-08 数据核对 | P2 | **closed**（2026-08-09 复核：论文已文档化 EN §6.1 L682/§7.1 L1105/§7.3 L1137/§8 L1192、ZH §7.1 L825；claim 限定为"添加物理目标的边际价值"，结论不受影响） |

## 2026-08-02 批次：代码双轴审查（C1–C4 重构后，作者 trae）

明细见 [code-review-20260802-constraint-refactor-trae.md](code-review-20260802-constraint-refactor-trae.md)。Standards 0 硬违规 + 9 判断性建议；Spec 4 缺漏 + 2 越界 + 1 误导注释；RDR-004 公式方向与跨文件一致性确认正确。最严重两项：Earth-radius 统一不完整（轨道半长轴仍用赤道半径）、验证器保留论文已删除的 resolution 子检查。修复优先级表见报告末尾。

复审（trae，同日）：代码更新后 P1 升级为 P0——`make_orbit` 的 `semi_major_axis` 仍用赤道半径，下游 `R_e` 已切平均半径，导致 h 多算 7 km。其他优先项（P2/S1/S2）未落地。本轮改动相关 31 测试通过。

第三轮复审（trae，2026-08-02）：见 [code-review-20260802-round3-trae.md](code-review-20260802-round3-trae.md)。P0/P1/P2 已闭环（Earth-radius 自洽、resolution 子检查删除、φ→θ 真转换）；N4 已验证无问题。新增高风险两项：（1）N2 误判更正后关闭（代码向论文 20/0.1 对齐，OP-1 代码侧闭环）；（2）N3 — post-hoc ConstraintVerifier 过滤改变 `n_frontier_points` 口径，重跑数据与已提交 baselines_200.json 等不可混合。S1/S2/S3-S7/P3 未改。本轮改动相关 32 测试通过（6 failed 为 pkl 缺失）。

第四轮深挖（trae，2026-08-02）：见 [code-review-20260802-round4-trae.md](code-review-20260802-round4-trae.md)。**新 P0 发现**：R4-P0 消融脚本（no_incidence/no_squint/no_physics）仍保留四层 C1 inline penalty（phi_min/max、phi_min_res、squint），但主 SARSchedulingProblem / solver_factory 已按 §3 分层设计移除 inline C1。消融与基线 penalty 结构不一致，导致消融 delta 归因不可信。三脚本各删 ~9 行即闭环。其余已验证 6 项（frontier 对齐、无循环导入、φ↔θ 数学等价、RDR-004 7 处一致、no_physics count-only 与注释一致、C1 窗口 squint 检查正确）。N3、S1-S7、N1、N5 仍挂起。

第五轮深挖（trae，2026-08-02）：见 [code-review-20260802-round5-trae.md](code-review-20260802-round5-trae.md)。**无新功能 bug**。新发现 5 项全部低-中优先：R5-P0 so_f1.py post-hoc repair（delay-repair）与 moea.py post-hoc filter 策略不对称（合理设计但未注释）；R5-P1 repair 后 sel/phis/t_acts 局部变量未更新（当前无 bug，fragile）；R5-P2 测试命名 4 处陈旧（test_constraint_c4c5.py 文件名 + test_per_sat_c4c5_budget + test_o3_c4c5_vectorized_unchanged + test_c6_no_duplication_pass）；R5-P3 constraints.py docstring 2 处 "C3" 应为 "C2"；R5-P4 `_b3_squint_minimize` phi-space mask 数学等价但注释可加固。已验证 2 项：`_enforce_c2_transitions` delay-repair 与 RDR-004 不冲突、so_f1 repair 后 f2/f3 公式与 moea 一致。

## 2026-08-02 批次：G-BL 可行性独立审计（人工，第三求解器缺陷）

明细见 [rdr-005-gbl-endtime-c2.md](rdr-005-gbl-endtime-c2.md)。

| ID | 问题 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| RDR-005 | G-BL 观测结束时间误设为窗口末（`t_actual_end=w.t_end`）而非 `start+duration_min`：span<duration 窗口致 ~20s 硬重叠（9,696/113,349 窗口），span>duration 窗口过度保守少排任务；叠加延迟时刻不重算 LOS，369/400 场景 C2 违反。首轮重跑审计又掘出：(C) epoch↔datetime 时区往返致 G-SM 观测被推 −8h 出窗口、f2/f3 用 clamp 错几何（b3 C1/OOW 198/200）；(D) 基线默认 budget=inf 不遵守 scenario 200 观测上限（S3/S4 47 场景超预算 f1_gbl 虚高） | trae "G-BL C2 微缺口"反馈 → 人工全量审计推翻 | P0 | **closed**（2026-08-10 复核：全 6 族用新基线/窗口修复数据重跑完成，f1* 分母已按新 G-BL 基线；Table1/§6.3/§6.6/摘要回源通过，提交闸门 08-09 全绿） |

## 2026-08-10 批次：S1 INTEGRITY（rev2 全论文数字清册 verify_paper_numbers.py）

明细见 [rdr-006-gsm-f3-delta.md](rdr-006-gsm-f3-delta.md)。工具 `src/tools/verify_paper_numbers.py`：144 断言（Table1/§6.2/§6.3/§6.4/§6.6/§7.1/消融表），数据文件 sha1 指纹，报告 `review/verify_paper_numbers_report.json`，exit 0。

| ID | 问题 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| M-F1 | G-SM f3 效应量 Cliff's δ 论文 0.91，最终数据回源 +1.0000（200/200 场景 G-SM f3 > G-BL，W=0 p=1.44e-34）；0.91 全仓无代码/数据来源，硬编码残留；中英 5 处 | verify_paper_numbers.py（S1 机械类） | P1 | **closed-with-evidence**（中英 5 处 0.91→1.0；新增 g2-gsm-f3delta 断言期望 +1.0 全绿；双版编译过；2026-08-18 回填） |

Gate M1（S1 完成）：机械/事实类 0 未决 ✓（M-F1 已修）；裁决类登记：0 条（本轮清册全部为机械类数据回源断言）。

## 2026-08-10 批次：S1b 引用完整性 + AI 痕迹（子 agent integrity 审查）

明细见 [rdr-007-s1b-citations-ai-trace.md](rdr-007-s1b-citations-ai-trace.md)。引用上下文 B1（25 bib 核对，WebSearch/Crossref/Scilit 证据）+ AI 痕迹 7 模式（无空洞强调/hedge 滥用，整体诚实限定型写作）。

| ID | 问题 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| C-1 | bib Peng2019Orienteering 标题错（"…Profits and Resources" + 多余 AEOS 前缀）→ 实为 "An Orienteering Problem with Time-Dependent Profits and Travel Times" | S1b B1（Crossref 核实） | P2 | **closed-with-evidence**（bib title 已改；双版编译待确认；2026-08-18 回填） |
| C-2 | bib Wei2025MONP 标题漏 "Problem" | S1b B1 | P2 | **closed-with-evidence**（bib title 已改；2026-08-18 回填） |
| C-3 | bib Zhou2025TwoPhase 标题与 Crossref 正式标题不符（"…Hybrid Algorithm for Multi-Agile…"→"…Hybrid Optimization for Scheduling Agile…"） | S1b B1（Crossref DOI 10.3390/rs17121972 核实） | P2 | **closed-with-evidence**（bib title 已改；2026-08-18 回填） |
| C-4 | §2 Chang2022Gaofen "two adaptive NSGA-II variants" + "bi-objective (profit+energy)" vs 检索证据 ALNS+NSGA-II/III + Scilit "THREE-OBJECTIVE" | S1b B1 高优先核实 | P1 | **closed-with-evidence**（2026-08-11 复核：§2 已于 commit 673a4e1 改正确——ALNS+NSGA-II/III + three-objective；tavily 取到 ScienceDirect 摘要逐字确认：three-objective model = loss rate of ground targets + invalid observation + times of opening sensor，two algorithms = ALNS+NSGA-II, ALNS+NSGA-III，与 §2 现文本一致，无需再改；2026-08-18 回填） |
| A-1 | "not a mathematical identity / density-dependent rather than redundant" 跨摘要/§6.4/§7.4/结论复用 ≥4 次 | S1b AI 痕迹模式 3/5 | P3 | **adjudicated-keep**（2026-08-11：每短语实为 2 次——摘要+正文各一，属正常复述；"not a mathematical identity" 是 RDR-002 有意诚实表述，CLAUDE.md 明确保留；不改） |
| A-2 | §6.4 机制四段连续 "not X but Y" 收束 | S1b AI 痕迹模式 5 | P3 | **adjudicated-keep**（2026-08-11：§6.4 三处 "not X but Y" 各为必要科学对比——定义性耦合 L940、经验收敛效应 L992、因果区分 L1030；非 AI 填充；不改） |
| A-3 | §6.6 四 control 段收尾同构 | S1b AI 痕迹模式 1/5 | P3 | **closed-with-evidence**（2026-08-11：random-search 尾句 "rather than luck" 删除（EN+ZH），打破四 control 段同构；其余三段 "rather than X" 为诚实限定保留；2026-08-18 回填） |
| H-3 | highlights.tex #3 "MOEA-2/3 near-identical redundant" 与 RDR-002 后结论矛盾（稀疏 +84% f3） | 人工扫 highlights | P2 | **closed-with-evidence**（2026-08-11：highlights #3 "redundant at operational densities"→"saturating at high density"，94→81 字符，避免与"密度依赖而非冗余"结论矛盾；2026-08-18 回填） |

A3 幽灵引用：25/25 bib 全被引，0 孤儿 0 悬空（复核通过）。

## 2026-08-10 批次：S2 5 审稿人 full + S3 意见整合/对抗验证

明细见 [s2-review-consolidated-20260810.md](s2-review-consolidated-20260810.md)。5 审稿人（EIC/R1 方法论/R2 领域/R3 跨学科/DA）全 **Major Revision**，41 条意见去重整合为 rdr-008~049。对抗验证 7/7（agent）：5 确认（低斜视 ψ、HV 归一化、密度类异质、N50 CI、pooled r）+ 2 部分确认（包络采样描述、f3 近似）。Gate M2 临时化确认中（σ 重跑完成定）。

**状态回填（2026-08-11）**：S5 批 1-7 已提交 commits `03f7a40`/`20541df`/`b6b270f`/`c92d2ec`，下方对应 rdr-008~061 行多数已 fixed；下表状态列逐行更新中，未回填的行以 commit 为准。当前未决：rdr-009/053（σ 重跑，2026-08-11 重启中）、rdr-026（代码已修，GA-P-BL 重跑验证待做）、rdr-035/036/047/048/049/054/055/056（MINOR）、rdr-062（已 fixed）。

**状态回填（2026-08-12）**：σ/hotstart/variantD 三 control 几何修正重跑全完成（σ 80 runs / hotstart 144 / variantD 30，git 90f7202）——rdr-009/026/047/053/054/055 全部 closed（见下），§6.6 EN+ZH 数字已更新（扰动 f3 0.1401→0.435、variantD S3 持平/S4 更高 0.520 vs 0.490）。rdr-056（§6.4 池化对象）同日 closed——回源 MOEA-3 快照改精确数值 + 非单调措辞。S5 批次 P0/P1/P2 全部清零。

| ID | 问题 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| rdr-008 | §7.2 "MOEA-2 8.2%/f1*=0.68/32% loss" 与 Table1(0.87/+4.5%) 矛盾；0.68=随机初始化 control 值，8.2% 无源 | EIC+R1+DA | P0 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-009 | §6.6 σ 扫描 control 用旧代码 f1a2dd75（同场景 f3=0.14 vs 主实验 0.44，f2/n_sel 也不一致），无法验证当前 σ 稳健性 | R1+DA | P0 | **closed**（2026-08-12：σ 重跑完成——80 runs（4σ × 2 solvers × 10 S3），sweep_summary.json git 90f7202c；修正几何后 MOEA-3 f2≈0.535/f3≈0.435（旧 0.5492/0.1401），水平间变化 ≤2×10⁻³，coverage 恒 200/300；§6.6 扰动段 EN+ZH 已更新数字） |
| rdr-010 | G-BL 非严格覆盖上限：MOEA-3 S1-D f1*=1.0625/1.0215、MOEA-2 1.0089（3 场景约束可行）；"G-BL maximizes coverage profit/ranks first" 过强 | DA | P0 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-011 | found front vs feasible：G-SM 高 f3 解在 MOEA-3 前沿外，"front compression/coverage pressure" 是 found front 属性，无法分离搜索不完整性 | R3+R2 | P0 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-012 | GA-P-BL never-worse guard §4.3 未描述（§6.1/§7.1 引用"§4.3"但无）；GA-P-BL 200/200 恒等 G-BL 未诊断 | R1+R2+R3+DA | P1 | **closed-with-evidence**（S5 批6；2026-08-18 回填） |
| rdr-013 | G-BL §4.2 描述"最小入射/最大仰角"vs 实现窗口起始（最大入射）；与 §6.4 自相矛盾 | R2 | P1 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-014 | "低斜视\|ψ\|<10° 主导 + cosψ 4-5%"与实测矛盾（mean 16-24°/median 14-25°/p90 32-39°，cos³ψ 衰减 8-26%） | R2 | P1 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-015 | 包络 -0.97 采样未过滤 C1 入射角，"C1-feasible"描述错（数值 -0.97 稳，正确过滤 -0.966） | R2+DA | P1 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-016 | f3 平坦地球近似未量化（47° 处 R³ 高估 17%）+ 未披露 NESZ sinθ 因子 | R2 | P1 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-017 | HV §5.3 描述 per-solver-pooled vs 实现全局归一化；"单点求解器各一个点"错（各 200 点） | R1+DA | P1 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-018 | HV 表省略 G-SM（G-SM HV=0.1023 全场最高）；纳入后排序反转；pooled HV 跨 solver 比较可疑 | DA | P1 | **closed-with-evidence**（S5 批5；2026-08-18 回填） |
| rdr-019 | 密度类 A-E 非均匀（S1-D/S3-D n_orbits=1、S2-E 高纬、S4-D 紧入射 25°、S4-B n_sel=35.6）；§5.1 只披露"三种分布类型" | R1 | P1 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-020 | f1* 归一化循环性（f1* 基准=G-BL，G-BL 又作热启动种子） | R1 | P2 | **closed-with-evidence**（S5 批5；2026-08-18 回填） |
| rdr-021 | 热启动随机初始化对照样本小（10/4/5/5×3）+ 全求解器 G-BL 种子注入，循环论证风险 | EIC | P1 | **closed-with-evidence**（S5 批5；2026-08-18 回填） |
| rdr-022 | MOEA-2(H=13)/MOEA-3(H=91) 参考点不对称，"第三目标 +84%" 混淆因素 | EIC | P1 | **closed-with-evidence**（S5 批6；2026-08-18 回填） |
| rdr-023 | "greedy approach Pareto-optimal coverage" 无最优性界 | R3 | P1 | **closed-with-evidence**（S5 批6；2026-08-18 回填） |
| rdr-024 | 摘要 "+58% f3 at 2% cost" 选择性：隐藏 MOEA-3 f2 比 G-BL 低 6% | EIC+R3+R2 | P1 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-025 | 无 wall-clock runtime 数据 | R3 | P2 | **closed-with-evidence**（S5 批6；2026-08-18 回填） |
| rdr-026 | used_gbl_fallback 未持久化 + GA-P-BL 无 seed（不可复现） | DA | P1 | **closed**（2026-08-12：代码修（落盘标志+固定 seed）+ GA-P-BL 全量重跑 200/200 完成（git c92d2ec，log _gapbl_rerun_rdr026_20260811.log）；b2_profit_bl/_progress.json used_gbl_fallback 全 False 落盘；f1 除 S1 单场景 1.135 外全 1.0（=G-BL，塌缩为设计行为，见 GP-1）） |
| rdr-027 | per-task pooled r 忽略 schedule 间方差（per-schedule S1 有正 r） | R1+DA | P2 | **closed-with-evidence**（S5 批5；2026-08-18 回填） |
| rdr-028 | +4.5%(摘要/§6.1) vs +4.7%(§6.3/Table) f2 口径不统一 | EIC+R1 | P2 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-029 | S2 f1* 0.98 vs 0.985；S4 1.00 vs 0.996 四舍五入 | EIC+R1 | P2 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-030 | N50 "CI 不收敛"错（n50_logistic CI=[30,62] 收敛）；§7.2"具体估计"过强；gen_all_figures.py b>0 图脚本 bug（N50 图无 CI） | R1+DA | P1 | **closed-with-evidence**（EN §6.3 措辞批1-4 + ZH §6.3 CI [30,62] 2026-08-11 镜像；gen_all_figures.py bootstrap 过滤 03f7a40 从 b>0 改 abs(b)>1e-6 恢复 CI，2026-08-11 再收紧为 b<-1e-6（拒绝 b>0 错向拟合，实测 CI [24,66]→[31,67]）；fig3 重生成待 GA-P-BL 完成（脚本读 b2_profit_bl）；2026-08-18 回填） |
| rdr-031 | highlights #3 "near-identical redundant" 与正文冲突 | EIC+R2+DA | P2 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-032 | Moreira2025 bib 卷/年（Proc IEEE 卷 114=2026 非 2025） | R2 | P2 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-033 | "Sentinel-1 bilateral" 术语错（Sentinel-1 右视 only） | EIC+R3 | P3 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-034 | "G-SM at most 44% of tasks" 无表支撑 | EIC | P3 | **closed-with-evidence**（S5 批5；2026-08-18 回填） |
| rdr-035 | 摘要 ~230 词超限 | EIC | P3 | **closed-with-evidence**（2026-08-11：EN 摘要 265→200 词，全数字保留，删"not only feasibility"/"scalar composites"定位/结尾条件列表，G-BL 首现补全称，MOEA-3 归属保留；ZH 摘要同步删定位句+结尾条件、补 ~6% 几何代价披露；双版编译 0 undefined；2026-08-18 回填） |
| rdr-036 | §6.4 vs §7.1 findings 重述冗余 | EIC | P3 | **closed-with-evidence**（2026-08-11：§7.1 finding (2) 尾句机制重述——近逐字重复 §6.4 "coverage pressure... conflict persists"——改为指向 \S\ref{sec:pareto-coupling}；中英同步，双版编译 0 undef；2026-08-18 回填） |
| rdr-037 | C3/C4 非绑定未 flag（真实 SAR 能源/下行常绑定） | R3 | P3 | **closed-with-evidence**（S5 批6；2026-08-18 回填） |
| rdr-038 | fixed dwell 30s 未声明 | R3 | P3 | **closed-with-evidence**（S5 批6；2026-08-18 回填） |
| rdr-039 | f2 未加权均值 vs f1 优先权重 | R3 | P3 | **closed-with-evidence**（S5 批7；2026-08-18 回填） |
| rdr-041 | r_null "exact partition" 措辞过度（θ/ψ 独立均匀任意假设） | R2 | P3 | **closed-with-evidence**（S5 批7；2026-08-18 回填） |
| rdr-042 | \|ψ\|≤45° 最大斜视假设未注（真实平台斜视能力小） | R2 | P3 | **closed-with-evidence**（S5 批7；2026-08-18 回填） |
| rdr-043 | Friedman 指标(HV)未指明 + 无并列修正 | R1+R3 | P2 | **closed-with-evidence**（S5 批5；2026-08-18 回填） |
| rdr-044 | zsplit 浮点噪声当非零 → 虚假 p=0.084 | R1 | P2 | **closed-with-evidence**（S5 批5；2026-08-18 回填） |
| rdr-045 | Cliff δ 定义并列计 0 非 0.5；阈值标"Vargha-Delaney"实为 Romano | R1 | P2 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-046 | "population 200 不改变结论"无数据支撑（p1-4 空目录） | R1+DA | P2 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-047 | variant D 噪声 RandomState() 无种子 | DA | P2 | **closed**（2026-08-11 代码修：三消融 runner hot-start 采样 `RandomState(seed)`，py_compile+import+确定性测试过；2026-08-12 数据：variant D random-init 重跑 30/30 完成，full.json git 90f7202，S3 f2=0.5274±0.013/S4 0.5205±0.009，与热启动 D 对照入 §6.6） |
| rdr-048 | envelope -0.97 vs 脚本 -0.95 数字核对 | DA | P3 | **closed-with-evidence**（2026-08-11：脚本重跑确认 S1 r_c7 均值 -0.9786、池化 -0.9714 → 论文 -0.97 正确（池化取整）；脚本 docstring/note 的陈旧 "-0.95" 已改为 ~-0.97，json 重新生成，exit 0；2026-08-18 回填） |
| rdr-049 | 新颖性未对照中文 SAR 质量调度文献 | R2 | P3 | **closed-with-evidence**（2026-08-11：后台调研确认无直接重叠（CNKI 付费墙覆盖部分，暂定）；§2.1 补中文文献对照段——Chang \& Zhou (Annals OR 346:861-893, 2025) 姿态角质量代理 + Wu et al. (ASR 63:2551-2565, 2019) 覆盖/时效 NSGA-III，两篇 Crossref 验证；差异化定位"分解物理目标 + 密度依赖权衡"；中英同步，双版编译 0 warning；2026-08-18 回填） |

裁决类（S3 裁定）：GA-P-BL 移除 guard = 豁免（保留作对照，改 framing rdr-010/012）；runtime 数据 = 部分豁免（声明不比较）；无最优性界 = 部分豁免（降级 + future work）。

## 2026-08-10 批次：S3 ppw:logic 跨节一致性（子 agent 独立发现）

| ID | 问题 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| rdr-050 | Intro C1 "solver convergence to low-squint that **suppress the θ-axis conflict**" vs §6.4/§7.1 自己"相关 persists/strengthens、饱和由 coverage pressure not conflict disappearance"——Intro 与机理段矛盾 | ppw:logic | P1 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-051 | §6.3 L843-844 "Beyond N≈150 no scenario shows deficit >5% (0%)" vs L806-807 "0% at N≥150 (2% at S4 single)" + Table S4=2%——"no scenario/0%"为假 | ppw:logic | P2 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-052 | §6.3 同节 transition "confined to N∈[20,100]" vs 末句 "N=100-300 therefore captures" 矛盾 | ppw:logic | P2 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-053 | §6.6 Perturbation "mean f3=0.1401" vs Table2/6 S3 f3=0.453（差 3 倍）——σ 扫描旧数据（=rdr-009 同源） | ppw:logic | P0 | **closed**（2026-08-12：并入 rdr-009——σ 重跑完成，f3 0.1401→0.435，与主实验 S3 f3≈0.44 一致；§6.6 扰动段已更新） |
| rdr-054 | §6.6 "hot-started D f2≈0.515-0.535" 不覆盖 Table6 热启动 D S4 f2=0.490；"slightly higher" 对 12% 差距过轻 | ppw:logic | P2 | **closed**（2026-08-12：variant D 重跑后改写——随机初始化 D S3 f2=0.527（与热启动 D 0.527 持平）、S4 f2=0.520（>热启动 D 0.490，低斜视），"S3 持平/S4 更高"叙事取代"略高"，12% 差距显式呈现；EN+ZH 同步） |
| rdr-055 | §6.6 "random-init f2 0.549 vs hot 0.551"（hot f2=0.551）vs Table2 热启动 MOEA-2 S3 f2=0.530/S4 0.493 | ppw:logic | P2 | **closed**（2026-08-12：控制子集（10/4/5/5 场景）内 hot-vs-random 对照更新为 S3 0.551 vs 0.550、S4 0.551 vs 0.551；绝对值差异源于控制用 5 场景子集、Table2 用全场景，对照在子集内自洽） |
| rdr-056 | §6.4 "mean f2 0.54→0.51, f3 0.43→0.52" 池化对象不明（MOEA-3?）+ f3 非单调（S2 降至 0.375）被掩盖 | ppw:logic | P2 | **closed**（2026-08-12：回源 _snapshot_final_moea_3obj.json——MOEA-3 调度内均值 S1→S4 f2 0.5396→0.4902、f3 0.4283→0.5354（S2 0.3749 回落）；§6.4 括号句改"MOEA-3 变体 A，调度内平均 f2 大致 0.54→0.49，f3 大致 0.43→0.54（S2 回落 0.37）"，EN+ZH 同步，双版编译 0 undef） |
| rdr-057 | §6.3 "0.998-0.999 at N≥150 (S7-S3)" 不含 S8=0.997 | ppw:logic | P3 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-058 | §7.1 "MOEA-3 f3 advantage ≈+1.5% at N≥300" 实际 S3 +2.03%（0.453 vs 0.444） | ppw:logic | P3 | **closed-with-evidence**（S5 批1-4：EN §7.1 改 "≈+1.5--2%"；ZH §7.1 2026-08-11 镜像同步；2026-08-18 回填） |
| rdr-059 | §6.4 三处 \ref{sec:pareto-coupling} 自引用（该节自身） | ppw:logic | P3 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-060 | §6.5 "selected-task counts identical to two decimal places" 过强（S3 C 154.4 vs 154.5, S4 C 142.5 vs 142.7） | ppw:logic | P3 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-061 | §7.1 "G-BL mid-range f3 (0.271)" 实为 S1 五值中倒数第二 | ppw:logic | P3 | **closed-with-evidence**（S5 批1-4；2026-08-18 回填） |
| rdr-062 | ZH §7.2 N50≈140 vs EN §6.3/§7.2 N50≈50（中英漂移 P0）；ZH §6.1 G-SM 覆盖率表述与 EN 出入 | ppw:logic | P0 | **closed-with-evidence**（2026-08-11 镜像：ZH §7.2 N50≈140→≈50、f1\*=0.68/32%→0.87/13%、8.2%/4.4%/88%/62%→+4.5%/+1.4%/84%/6%、S3 0.98/1.6%/16%/24% 删除并补"至多 2% + GA-P-BL 无单独差距"收束、G-SM +34%/67%/0.33→+32%/63%/0.37、4-8%→百分之几；ZH §6.3 0.998→0.997、CI"不收敛"→[30,62]、0%→至多一场景；ZH §7.1 +1.5%→+1.5--2%；ZH §6.1 补 GA-P-BL 对照句；xelatex 2 遍 0 undefined；2026-08-18 回填） |

## 2026-08-12 批次：S2 5 审稿人 full + S3 对抗验证（fresh full 全程审稿）

明细见 [s2-review-consolidated-20260812.md](s2-review-consolidated-20260812.md)（待写）+ [rdr-066-f3-nesz-model-fix.md](rdr-066-f3-nesz-model-fix.md)。S2 5 审稿人（EIC 72/78、R1 73、R2 54、R3 55、DA）→ **MAJOR REVISION**，2 CRITICAL + 8 MAJOR + 12 MINOR 批。

S3 对抗验证三 P0 全确认：
| ID | 问题 | 验证 | 状态 |
|---|---|---|---|
| C1 | budget_control.json 缺失，§6.6 "not a budget artifact" 无控制支撑 | ✅ 文件不存在，run_budget_control.py 功能完好但 08-09 被外部杀无输出 | **closed-with-evidence**（budget control 2026-08-16 当前代码重跑 10 scenarios 完成；§6.6 budget 段 EN+ZH 落地，见 R13/86e71db；2026-08-18 回填） |
| C2 | hotstart control 漏传 instance → 默认轨道（raan=0），f2 基址不符（S1-A_seed00 control 0.159 vs main 0.610） | ✅ 同 scenario 重算：主几何 0.6099 vs 默认 0.1098 纯几何差 | **closed-with-evidence**（hotstart control 几何 bug 已修 + σ/hotstart/variantD 三 control 2026-08-12 全量重跑完成，§6.6 EN+ZH 同步；2026-08-18 回填） |
| C3 | f3 NESZ 斜视双计（θ 从全 ξ + 乘 cos³ψ）；作者定 Option 2：f2/f3 全用高程面角 | ✅ 恒等式 cos³θ_elev·cos³ψ=cos³ξ 实测 5.6e-16；探针：S1 增益 +111%→+52%，S4 饱和不变 | **closed-with-evidence**（f3 NESZ 双计已修(f96674f)，MOEA-2/3 全量重跑完成(4cfc42c0)，Table/figures/§6.x/摘要/highlights/ZH 全数更新；2026-08-18 回填） |

连带：Option 2 改 f2 → 全部优化 f2 的求解器重跑（MOEA-2/3、消融、σ、variantD、hotstart、budget）。重跑完成后 Table/figures/§6.x/摘要/highlights/ZH 全数更新。S3 其余 ~28 条意见（GA-P-BL 披露、HV 方法、base 一致、decoder/slew 保真、novelty 措辞等）待重跑后逐条对抗验证 + 修订。

S2 批次 RDR 编号：C1/C2/C3 = rdr-066；意见级 rdr-067+ 待整合。

## 2026-08-12 批次：S1 INTEGRITY 全程审稿重跑（fresh full，verify_paper_numbers.py 12 失败全修）

明细见 [rdr-063-hotstart-control-contamination.md](rdr-063-hotstart-control-contamination.md) / [rdr-064-fig5-build-break.md](rdr-064-fig5-build-break.md)。数据文件 `p1-1_random_init/hotstart_control_s1s4.json` git 追踪。

| ID | 问题 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| RDR-063 | hotstart control 新旧混入（144=旧72 pre-geomfix+新72 post-geomfix），§6.6 deficit 混算 −0.237/−0.480/−0.622/−0.461；真值 −0.229/−0.475/−0.565/−0.382 | verify_paper_numbers.py（12 断言失败） | P0 | **closed-with-evidence**（数据清理 72 记录 + runner append 去重根因 + 论文 EN/ZH 6 处 + 断言更新；双版编译过，144 断言 0 failed；2026-08-18 回填） |
| RDR-064 | 040a9e3 误删 fig5_ablation.pdf（判孤儿依据 gen_all_figures 只出 4 图），ablation 节仍引用 → HEAD 编译 fatal | EN pdflatex 编译门 | P0 | **closed-with-evidence**（git 6c4e98d 恢复；双版编译过 EN 39 页/ZH 31 页；fig5 生成脚本入仓待 S4；2026-08-18 回填） |

S1 其余：引用完整性 + AI 痕迹（S1b）本批已跑——[rdr-065-s1b-citations-ai-trace.md](rdr-065-s1b-citations-ai-trace.md)。结构 PASS（27 bib 全被引，EN/ZH 键集一致）；4 条事实类已修（ZH 摘要覆盖率矛盾 P1、Romano 阈值 bib 缺失 + ZH Vargha-Delaney 错标、Chinese-language、Wei2025MONP SAR 误置例外）；5 条裁决类（Wu2026 措辞、bib P3 维护、rather than 重复）待 S3。Gate M1 机械/事实类已清。

## 2026-08-16 批次：ARS panel 2026-08-15（五席 Major Revision）修订批

明细见 [rdr-067-ars-panel-20260815.md](rdr-067-ars-panel-20260815.md) + [ars-panel-20260815/editorial-decision.md](ars-panel-20260815/editorial-decision.md)（不可变 roadmap）。判决 **Major Revision**，3 阻塞束 B1（§6.6/§6.4 两处倒读数据）/B2（统计回源不上）/B3（fig5 零柱、budget control 未交付、Pareto 判据空洞、G-SM 比较框架缺失）。分诊（2026-08-16 用户裁决）：R1-R18 全修、S 项只做 S1-S4/S6/S7（S5 信封实验跳过）、R13 先验证盘上数据。

| Ref | 问题 | 决策 | 状态 |
|---|---|---|---|
| R1 | §6.6 hot-start 几何方向倒读（f2 高=好） | 🔴 改写 gloss+结论+摘要 deflection | **closed-with-evidence**（EN+ZH；2026-08-18 回填） |
| R2 | §6.4 衰减"稀疏最强"倒读（实 S1 最弱 −0.63） | 🔴 按残差改写 | **closed-with-evidence**（EN+ZH；2026-08-18 回填） |
| R3 | δ=+0.88 不可复现（per-scenario f3 δ=1.00）；§4.3 "+1.0" 冲突 | 🔴 全 δ 重算+标 basis | **closed-with-evidence**（δ=+0.99 199/200，gate 断言；2026-08-18 回填） |
| R4 | §6.3 "78%/6%" vs 数据 80%/10% | 🔴 文本对齐 | **closed-with-evidence**（EN+ZH+Table5+gate；2026-08-18 回填） |
| R5 | N50 §6.3=50 vs §7.2=45（artifact 50.03 CI[30.2,61.8]） | 🔴 统一 ≈50 | **closed-with-evidence**（§7.2 45→50；gate 断言；2026-08-18 回填） |
| R6 | +10.8% 实为 +0.89%（1.0089 单场景） | 🔴 改数字+重写 hedge | **rejected**（panel 读 90de261f 过期快照；当前 4cfc42c0 seed04=+10.81% 与 tex 一致；仅修 "A few"→"One" + gate 断言） |
| R7 | Table6 HV 漂移 2-5%（0.2351 vs 0.2341） | 🔴 重算表+标 basis | **closed-with-evidence**（0.0893/0.0668/0.0234；prose 0.2341；2026-08-18 回填） |
| R8 | Fisher-z −1.09 vs raw −0.72 无 basis | 🟡 标 weighting/补 CI | **closed-with-evidence**（basis+50 sched/class；range +0.25→−0.03；per_schedule 入 artifact+gate；2026-08-18 回填） |
| R9 | Pareto-sufficiency 判据空洞（AND+f1* 饱和永不 bind） | 🔴 reframe descriptive | **closed-with-evidence**（conjunctive 弃用+per-objective 报告，EN+ZH；2026-08-18 回填） |
| R10 | 全量 §6.2-7.2 vs artifact 审计未做 | 🔴 审计+gate 断言扩展 | **closed-with-evidence**（gate 144→161；数字全回源；2026-08-18 回填） |
| R11 | +7% f3 无检验统计量 | 🔴 补 Wilcoxon+δ+effect size | **closed-with-evidence**（S1 p=5.5e-13 δ=0.88 47/50；S4 δ=0.32；gate 断言；2026-08-18 回填） |
| R12 | squint 45° vs 真实"几度"；"conservative" 无限定 | 🟡 platform 锚定/限定语 | **closed-with-evidence**（capability-superset + §7.2 条件化，EN+ZH；2026-08-18 回填） |
| R13 | budget control 承诺未交付（盘上 budget_control.json） | 🔴 先验 provenance | **closed-with-evidence**（盘上数据 stale；当前代码 400-gen 重跑 10 scenarios：S3 −0.12%/S4 −0.44% Δf1*；§6.6 加 budget 段 EN+ZH；gate +4 断言；86e71db；2026-08-18 回填） |
| R14 | time-critical 动机从未进模型 | 🟡 limitation 段 | **closed-with-evidence**（limitation+§7.2 latency，EN+ZH；2026-08-18 回填） |
| R15 | random-init control 藏 f1* 崩塌（0.319/0.522；n_sel 70.3） | 🔴 补数+cardinality caveat | **closed-with-evidence**（EN+ZH；2026-08-18 回填） |
| R16 | 摘要 +41% 不报 G-SM 同基线 +45.3% | 🔴 框架重平衡 | **closed-with-evidence**（摘要加 G-SM 比较器，EN+ZH；2026-08-18 回填） |
| R17 | 消融 C 惰性（p=0.83）vs §6.4 机制不自洽 | 🔴 显式调和 | **closed-with-evidence**（窗口几何实证：θ_elev 1.5° vs ψ 24°，EN+ZH；2026-08-18 回填） |
| R18 | 中英漂移 | 🔴 全量镜像+gate 同步 | **closed-with-evidence**（ZH 全镜像+双编译；2026-08-18 回填） |

**2026-08-17 re-review**：EIC 独立核验 R1-R18，判 Minor Revision，4 残余当轮已修（EN §6.3 78%→80%；EN+ZH §6.4 frontier 34.3/6.7→33.8/6.8 + gate S1 容差收紧；§7.1 HV δ −0.55→−0.56；ZH 补 §6.4 HV/exceedance 段 + Limitations confound 句）。verify 165/0 + CALIBER OK、pytest 174、双编译过（41p/33p）。报告 [verification-review.md](ars-panel-20260815/verification-review.md)。

**2026-08-18 closure（M4）**：用户授权按 Accept 推荐提交。CRediT 补 Visualization 角色（EN+ZH，commit 3372e2e），cover-letter 日期更新，双版重编（EN 41p/ZH 33p），verify 165/0 + CALIBER OK。预闸 M1 全绿（cross_solver 70/0、gapbl/moea_live 0 违规、window 76190 窗 0、full_hard 1800 解 0）。投稿包 `ASR-submission-20260818.zip`（主稿 PDF + LaTeX source/figures + highlights/cover/credit/declaration）已生成，source 在临时目录独立编译验证 41p 0 undefined。**R1-R18 全闭，论文投递就绪（待用户 Editorial Manager 上传）。**

