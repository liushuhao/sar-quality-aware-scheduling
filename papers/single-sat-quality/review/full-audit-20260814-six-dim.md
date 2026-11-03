# 全面审查报告 — 2026-08-14 六维并行

> 覆盖：理论 / 算法 / 代码 / 数据 / 论文 / 关联贯通（全链）。6 个独立审查 agent 并行，主线程合并去重 + 交叉验证。
> 方法：最新工作流——dev-workflow 环节闸门 + thinking-* 方法论（第一性原理/对抗性审查/科学方法/归零）+ 9 类缺口模式 + 审查 loop。
> 状态标注：**[亲验]** = 主线程独立复算/读码确认；**[×N]** = N 个 agent 独立确认；未标注 = 单 agent 待验。

---

## 执行摘要

**RDR-066 新口径（f2/f3 高程面角）核心物理与代码链正确**——4 处 MOEA-3 runner 公式全部同步，守卫测试锁恒等式（除一个空断言）。**但论文整体有大量旧口径残留未同步**：消融表、tab:hv、variant-D control、S4 n_frontier 文字均为旧数据；加上 1 个统计层 HV 归一化方向 bug 和 1 个未提交的求解器修复。**消融三族重跑完成后，消融表/叙事必须全量重算**。

## 🔴 阻塞项（10 项）

### A. 指标层缺陷（影响全部求解器对比）

**A1. [亲验] HV 归一化 f2/f3 方向翻转** — `experiments/statistical_analysis.py:232-237`
- `norm_f2/norm_f3` 用 `1.0 - (x-min)/(max-min)` 把 f2/f3 当最小化；但论文（tex §2.3 "Higher f2/f3 = better"）与代码（moea.py:91 三者最大化、:295 三者同取负）都是最大化。
- **主线程复算**（200 场景）：翻转版 G-SM 反常最高（0.094，质量最好被翻转惩罚成最差），MOEA-3/G-BL=1.07×；修正版 G-SM 优势 9×（0.247），MOEA-3/G-BL=1.54×。**solver 排序与 HV 比全变。**
- fig1_hypervolume + Friedman/Wilcoxon 全建在此 HV 上。附带：compute_hv 2D 阶梯积分（:198-205）用 f2_cur 非 running-max，对 2D 被支配点欠计。
- 修：`norm_f2/f3` 去 `1.0 -`；阶梯积分改 `max(f2_cur, prev)`；全量重算 statistical_results + fig1 + 论文 HV 相关数字。

**A2. [×2] tab:hv + G-SM HV = pre-b107e97 旧统计结果** — `small-paper-ijae.tex:776-778,947`
- 论文 0.0593/0.0417/0.0186、G-SM 0.1023 精确等于 681ced6（RDR-066 前）旧 statistical_results.json；当前数据重算为 MOEA-3 0.0497/MOEA-2 0.0455/G-BL 0.0376/G-SM 0.0632。S4/S1 HV 比 0.18/0.11 → 实际 0.30/0.26。
- verify 只查 S4/S1 HV 比不查绝对值 → 漏网。**修：A1 修复后重算，更新 tab:hv + 正文 G-SM 0.1023 句。**

### B. 代码层缺陷

**B1. [亲验] frontier 去重后与 x_source 索引错位** — `src/sar_sim/solver/moea.py:464-472 → :630-641`（复制到 3 个消融 runner：no_squint:305、no_incidence:196、no_physics:208）
- `solutions_to_frontier` 按 (f1,f2,f3) 去重后 frontier 与原始种群 x_source 行不再对齐；`feasible_indices` 是去重后下标却直接用于 `x_source[feasible_indices]`。
- 后果：knee 解 `SolverResult.schedule` 拿到错误观测时刻，与 `metadata["t_actuals"]` 静默不一致。NSGA-III 无 eliminate_duplicates，精英重复染色体常见。
- 当前落盘 f1/f2/f3 来自 frontier dict 不受影响；消费 `.schedule` 的下游被污染。
- 修：solutions_to_frontier 返回存活行索引，或 filtering 映射回原始行号。4 处同步修。

**B2. [亲验] resume 只校验 pkl_sha1 不校验 solver_version** — 6 处同病：run_moea_3obj.py:200 / run_moea_2obj.py:209 / no_squint:538 / no_incidence:355 / no_physics:366 / run_so_f1_bl.py:177
- 跳过条件只锁输入 pkl。代码改动不改 pkl 时 `--resume` 静默保留旧代码产物（RDR-066 S1/S2 事故的直接根因）。
- 修：跳过条件加 `and completed[key].get("solver_version")==GIT_COMMIT`。全 6 处。

**B3. [亲验] no_squint 公式修复未提交 + 守卫测试未提交** — `experiments/run_moea_3obj_no_squint.py`（工作树 +24/-18）+ `experiments/test_f2_f3_identity.py`（??）
- HEAD 版 no_squint 仍是旧公式 `f2+=sin(geom.theta), f3+=cos³(geom.theta)`；工作树改成高程面角 `cos_te=cos(phi)/cos_psi`。当前消融后台跑的就是未提交代码，落盘 solver_version=b107e977 失真 → **checkout HEAD 重跑会得旧公式结果，数据不可复现**。
- **立即提交**（B3 是当前消融数据可复现性的前提）。

### C. 数据/论文层旧口径残留

**C1. [×3] 消融表整表旧口径 + 与 Table1 自相矛盾** — `sections/_ablation_section.tex:52-143` vs `small-paper-ijae.tex:740-741`
- 同一 MOEA-3/S1：主表 f3=0.699、消融表变体 A（自称 identical）f3=0.428、f1*=0.98。数据源 `ablation_summary.csv` mtime 08-09（b107e97 前），b107e97 换主数据后未重生成消融 CSV。
- `verify_paper_numbers.py:59-62` 直接读旧 CSV + :367-385 硬编码旧值 → **用旧数据验论文，永远假绿**。
- 修：消融三族重跑完成后，analyze_ablation 重生成 CSV + 重写消融表/§6.4 引用段 + verify 改读新 CSV。**等消融完。**

**C2. [×2] §6.6 variant-D random-init 旧口径** — `small-paper-ijae.tex:1114-1117`（EN）/ZH:806
- 论文 f2=0.527/0.520 vs 数据 `variant_d_random_init/full.json` 0.349/0.347。**verify 门禁当前 2 FAIL**（vd-S3-f2, vd-S4-f2）。
- 论文"与热启动 D 持平/S4 反超"叙事在新数据下反转（随机 f2 均低于热启动）→ 会推翻"低斜视收敛目标内在、非热启动残留"结论。
- 修：按新数据重算该段 + 重写叙事（S4 方向 0.347<0.379 仍成立但 S3 "matches" 变 +3.5%）。

**C3. [×2] §6.4 S4 n_frontier 文字旧值** — `small-paper-ijae.tex:894`
- 论文 20.5±9.9(M3)/1.8±1.0(M2) vs 数据 5.4±6.2/1.6±0.9；同段 952 行 S1 已更新 34.3/8.4，段内自相矛盾。verify 期望值已改新值 → 对数据 PASS 对论文原文失效。

**C4. [×2] §6.4 其他旧口径文字** — tex:776（HV 表见 A2）、:894（n_frontier 见 C3）、:901/:919/:923（G-SM f3≈0.70 实际 0.786、fig4 文字 f2∈[0.500,0.503] 实际 ~0.34）、:952（"three of 200 up to +6%" 实际 1 场景 +10.8%）。

**C5. [×1] ZH §5.3 HV 归一化与 EN 直接矛盾** — `small-paper-ijae-zh.tex:495-498`
- EN §5.3:678-684 全局池化（=实现）；ZH 每求解器池化且明言"未采用全求解器池化"，还载有 rdr-017 已否定的"单点求解器各仅一个点"声称。**ZH 必须镜像 EN。**

**C6. [×1] N50/CI 旧值** — §6.3 双版：论文 N50≈45/CI[24,96] vs `n50_logistic.json` N50=50.03/CI[30.18,61.84]。verify 不覆盖 N50。

## 🟡 中（20 项）

| # | 类别 | 位置 | 问题 |
|---|------|------|------|
| Y1 | 理论-约束 | constraints.py:176-177 | C1 验证器入射界 [16.7°,58.1°] 是论文 [18°,47°] 超集，θ=50° 解能过验证，"0 C1 违规"声明比论文弱 |
| Y2 | 理论-约束 | tex:320 + types.py:58-60 | ρ_i^req 分辨率需求声明即弃用，无约束路径消费 |
| Y3 | 理论-数据 | tex:477-479 vs types.py:139-140 | 论文 e_i~10²-10³ 与代码 5×10⁴ 差 50-500 倍（"非约束"结论成立但数字需更正） |
| Y4 | 理论-中英 | small-paper-ijae-zh.tex:179 | ZH §2.3 丢 θ_elev 澄清+误差带 caveat，读者会误读成 RDR-066 修掉的旧口径双计 |
| Y5 | 理论-测试 | test_f2_f3_identity.py:67 | **[亲验]** test_theta_elev_identity 空断言（左右两边相同），应断言 cos(θ_elev)·cos(ψ)≈cos(ξ) |
| Y6 | 代码-测试 | src/tests/ | **[亲验]** 9/20 收集报错（sys.path 写 src/src）+ 陈旧 import（run_so_f1 改名）+ 实验层 4 失败（paired_ttest→wilcoxon）。守卫测试是唯一可信回归网 |
| Y7 | 代码-死代码 | solver_factory.py:138 | ConstraintFreeSARSchedulingProblem 整段重抄，theta_i 算出未用，旧口径残留标志复制分叉风险 |
| Y8 | 数据-语义 | 三消融 runner f1_gbl=1.0 | 消融 f1=raw count vs 主实验 f1 归一 0-1；analyze_ablation 用 f1_raw 绕开，直接消费 "f1" 的下游会错 |
| Y9 | 数据-戳 | moea_2obj/3obj S1+S2 | **[亲验]** solver_version=681ced6b 过期戳，f2/f3+frontier 数值实为新口径（改写值未更戳）；按版本过滤的自动化会误判。重跑只为洗戳非必要 |
| Y10 | 算法-图码 | gen_all_figures.py:423-429 vs tex:770 | fig1 画全部 5 solver，caption 称 G-SM/GA-P-BL omitted，必错其一 |
| Y11 | 算法-公平性 | run_random_search_control.py + tex:1105 | "never exceed G-BL" 过度断言（随机无约束 C2-C4），应限"无约束上界与本批持平" |
| Y12 | 算法-措辞 | tex:557 vs so_f1.py:469 | 论文"noise to τ_i" vs 代码扰全 2N 染色体（~16% selection bit 翻转） |
| Y13 | 数据-回源 | tex:952 | f1*>1 声明过期（"three of 200, +6%" → 实际 1 条 +10.8%） |
| Y14 | 数据-回源 | b2_profit_bl | solver_version=c92d2ec2 旧戳但 f2/f3 已 recompute_b2_f2f3.py 重算新口径，provenance 误导 |
| Y15 | 数据-异常 | no_incidence/no_physics/b2_profit_bl | runtime_s 各 1 条 >6h（机器休眠注水），消费前剔 >1h 离群 |
| Y16 | 论文-表述 | §6.2 G-SM 任务比 | "44% at S1" 实 45%；"~20-27%" 实 S2=28% |
| Y17 | 论文-结构 | ZH §7.1 | 结构漂移：多 GA-P-BL 限定句 + "综合起来"段 + 收尾与 EN "identical via guard" 语义冲突 |
| Y18 | 论文-中英 | ZH §5.1 | S7/S8 "Sentinel-1 双侧视" vs EN "generic C-band bilateral"，同节又自称"通用"，内部矛盾 |
| Y19 | 关联-provenance | GA-P-BL | "never-worse" 守卫已落盘（so_f1.py:792 used_gbl_fallback）✓；但 provenance 戳旧 |
| Y20 | 关联-数据 | schedule_correlation.json | D S2 n_schedules=23 vs no_physics 50 条（消融中途生成），重跑后再生 |

## 🟢 低（主要项）

- 半径惯例分裂：nesz.py 用 6371 km vs types.py 6378 km，入射角差 ~0.1°（theory）
- f3 平面地球 R³ 误差带符号依赖约定（EN 47° 假设平面 vs 代码实际 ξ≈41.3°）
- no_incidence 隐藏双目标（f3=f2³ 恒等），值得论文注明
- solver_factory multi_moea_solver/compare_algorithms 死代码，3 处隐患（不 precompute/不传 f1_gbl/强制 pop）
- moea.py:498 docstring 术语漂移（θ vs θ_elev）
- run_so_f1_bl.py:90-97 f1_gbl 重复计算
- ZH 孤儿 \label{sec:hv-divergence}、ZH 消融表缺 +33.7% 注释、ZH §6.4 缺 G-SM 0.1023 句（旧值，实为幸免）

## 已确认良好（防复发到位）

- **f2/f3 新口径 4 处 runner 全部同步**（moea/so_f1/baselines/solver_factory + 3 消融），恒等式被守卫锁住（除 Y5 空断言）
- solver/verifier 双路径一致：C2 均走 compute_los_separation，C1 squint 上限同 45°，incidence 判定不产生假失败
- 几何 instance：主实验/消融/基线 runner 均 build_agile_instance_from_scenario（正确）
- penalty 死参数已修（moea.py:286），三消融副本同步
- 约束链 PASS：ConstraintVerifier C1-C4 与审计脚本键一致，无键错位
- 场景参数 PASS：n_targets S1=20/S2=100/S3=300/S4=500，S4-D 紧 incidence [18,25] 与论文一致
- Table1 全 20 格、摘要 +34%/+41%/+7%、§6.6 hot-start deficit −0.393..−0.684、σ 0.343/0.610、random-search 0.527/0.930/1.000、包络 −0.97、r_null −0.51、Friedman 392.47 均正确

## 贯通状态（linkage 6 主线）

| 主线 | 状态 | 说明 |
|------|------|------|
| 1. f2/f3 公式 | 部分 | 代码链全新口径，但 no_squint 未提交（B3）+ 论文消融表数字旧（C1） |
| 2. f1 语义 | PASS | f1_raw 全链优先，占位未污染 |
| 3. 约束 | PASS | verifier/audit/论文键一致 |
| 4. 口径版本 | FAIL | S1/S2 戳失真（Y9）+ 消融表旧（C1）+ 消费端无版本过滤（B2） |
| 5. 消融隔离 | 部分 | 公式隔离正确，但论文表/叙事旧口径且重跑进行中 |
| 6. 场景参数 | PASS | 密度/紧 incidence 与论文一致 |

## 修复优先级建议

**P0（立即，不依赖消融）**
1. B3 提交 no_squint 公式 + 守卫测试（消融数据可复现性前提，工作树已改）
2. A1 修 HV 归一化 + 阶梯积分，重算 statistical_results + fig1
3. B1 frontier 索引错位（4 处）+ 守卫
4. B2 resume 加 solver_version 校验（6 处）

**P1（等消融完重跑后）**
5. C1 重生成消融表/叙事 + verify 改读新 CSV
6. C2 variant-D random-init 重算叙事
7. C3/C4/C6 论文旧数字文字更新
8. Y4/Y17/Y18 中英镜像同步

**P2（工程卫生）**
9. Y5 守卫空断言修复；Y6 测试套件修复；Y7 死代码清理
10. Y9 S1/S2 戳补注或洗戳；Y10-Y13 论文措辞

## 覆盖面与局限

- 6 agent 读了：src/sar_sim 全部 28 模块、实验 runner 15+、测试 20+、results/ 全族 JSON、论文 EN+ZH 全 8 章+消融节、REVIEW_INDEX 全表
- 主线程亲验：HV 翻转（复算 200 场景）、no_squint 未提交（git diff+HEAD）、S1/S2 值新口径（bak 对比+frontier 数组）、S2 n_sel=子类差异、守卫空断言、测试套件收集失败
- 局限：消融三族后台运行中（数据快照）；部分论文数字（§6.4 per-schedule 相关等）无落盘数据文件；理论 agent 未深读 ga/greedy/so_f1/ilp
- **修复后必须重跑 verify_paper_numbers + 双版编译 + gen_all_figures 全量回归**
