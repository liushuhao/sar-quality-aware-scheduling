# S2 Review Consolidation — 2026-08-10（5 审稿人 full 意见整合 + 对抗验证）

> 5 审稿人（EIC/R1 方法论/R2 领域/R3 跨学科/DA）全部 Major Revision。本表去重整合全部意见，逐条对抗验证（数据/代码），4 档分类，RDR 编号唯一分配。S5 按此逐条修。

## 已对抗验证确认（🔴 CRITICAL / 数据级）

| RDR | 意见 | 来源 | 验证结果 | 处置 |
|---|---|---|---|---|
| rdr-008 | §7.2 L1115-1117 "MOEA-2 8.2% 质量提升 / f1*=0.68 at N=20 / 32% profit loss" 与 Table1(0.87/+4.5%) 矛盾，8.2% 全文无出处 | EIC+R1+DA | **确认**：0.68 = 随机初始化 control 值（hotstart_control S1 random_f1_mean=0.677）；8.2% 无任何当前数据支持 | 机械修：§7.2 用 Table1 当前值重写（f1*=0.87, +4.5% f2），删 0.68/8.2%；连带的 "4-8% resolution improvement" 句重调 |
| rdr-009 | §6.6 σ 扫描 control 用过时数据：同 10 个 S3-A 场景 f3=0.140 vs 主实验 0.436，f2=0.549 vs 0.535；sweep git f1a2dd75(旧代码) vs 主实验 solver 90de261f；"coverage 200/300" 与消融表 S3 n_sel=154.5 矛盾 | R1 CRITICAL + DA | **确认**：sweep_summary + sigma_0.x 全为旧代码 f1a2dd75 产物 | **重跑 σ 扫描（当前代码）进行中**（后台 bdkiv9znq）；重跑后更新 §6.6 或标记无效 |
| rdr-010 | G-BL 非严格覆盖上限：MOEA-3 S1-D_seed08 f1*=1.0625（f1_raw=119>f1_gbl=112，约束可行）、S1-D_seed02 1.0215、MOEA-2 S1-D_seed08 1.0089；论文 "G-BL already maximizes coverage profit" / "G-BL ranks first in coverage" 为事实错误 | DA CRITICAL | **确认**（3 场景 f1*>1.0 全部 constraint_feasible=True） | 改 §6.4/§7.1 framing："G-BL 为近最优覆盖锚点（3/200 场景 MOEA 超基线）"；GA-P-BL "delimiting claims" 论证重述（守卫保证等价，非 G-BL 最优） |
| rdr-011 | found front vs feasible surface：G-SM 解（f1*=0.37,f3=0.70 at S4；0.51,0.644 at S1）在 MOEA-3 前沿外（论文自承认）；"front compression" 与 "coverage pressure removes trading freedom" 是 found front 属性，无法与搜索不完整性分离 | R3 CRITICAL + R2 | **确认**：G-SM 高密度 +32% f3 证明 f3 有优化空间，MOEA 前沿不延伸 G-SM 区 = 搜索限制 vs 物理饱和 | 措辞降级为"found-front compression under G-BL-seeded search" + 明示"不排除搜索不完整，G-SM 区未被 MOEA 探索"；或 G-SM 种子控制实验（可选） |

## MAJOR（代码/方法级，多数已确认或待验证 agent）

| RDR | 意见 | 来源 | 验证 | 处置 |
|---|---|---|---|---|
| rdr-012 | GA-P-BL never-worse-than-baseline guard §4.3 未描述（§6.1/§7.1/结论引用"§4.3 guard"但 §4.3 无）；GA-P-BL 200/200 恒等 G-BL，五求解器实为 4 输出，GA 是否真搜索未被检验 | R1+R2+R3+DA | **确认**（so_f1.py L743 有 guard，§4.3 无） | §4.3 补 guard 描述；GA-P-BL 重定位为"G-BL 利润最优性对照"；或补守卫介入前 GA 适应度诊断 |
| rdr-013 | G-BL §4.2 策略描述错：称"预存离轴角(最大仰角=最小入射)"，实现为窗口起始时刻（baseline_b1 在 w.t_start，R2 实测 S1 θ=44.5°/ψ=31.4° 最大入射侧）；与 §6.4 "G-BL 种子插最早可行时刻(更高斜视)" 自相矛盾 | R2 MAJOR | **确认**（读 baseline_b1 代码） | §4.2 重写 G-BL 观测时刻描述 = 窗口起始（最大入射+高斜视），与 §6.4 一致 |
| rdr-014 | 低斜视前提数据不符：论文 "|ψ|<10° 主导调度" + "cosψ 因子贡献 4-5%"，实测 MOEA-3 调度内平均 |ψ|=16-24°（中位 14-25°, p90 33-39°），cosψ 贡献 9-17% | R2 MAJOR | **确认**（重算 ψ：S1 mean 19.4°/S2 23.9°/S3 19.2°/S4 16.0°，median 13.7-25.2°；|ψ|<10° 仅 17-35%；cos³ψ 衰减 8-26%，p90 处 44-53%） | 用实测 ψ/θ 分布重写机制段；重估 cosψ 因子 |
| rdr-015 | 包络相关性 -0.97 采样口径：r_visible_envelope.py 在完整时间跨度（含跨窗口间隙，θ 达 83°）采样，只过滤 |ψ|≤45° 未过滤 C1 入射角；C1 可行窗口采样下约 -0.70~-0.84，接近调度内相关 | R2 MAJOR + DA | **部分确认**：代码确全跨度采样（θ 实测 85.7°）未过滤 C1，"C1-feasible"描述错；但正确过滤（窗口内+θ∈[18,47]）后 r 仍 -0.966，**-0.97 数值稳健**（R2 的 -0.70~-0.84 未复现） | 修正 "C1-feasible" 表述为"|ψ|≤45° 可见性包络"；数值保留 |
| rdr-016 | f3=cos³θ·cos³ψ 平坦地球近似（R≈R_elev/cosψ）：47° 处 R³ 高估约 17%；标准 NESZ 含 sinθ（地面分辨元）因子使 θ 动态范围约加倍；未量化未声明 | R2 MAJOR | **部分确认**：论文用"≈"声明近似但未量化（47° 处 R³ 高估 17.0% 数学正确）、未披露 sinθ 因子 | 量化近似误差 + 声明 NESZ sinθ 约定；或改精确 R(t)³ |
| rdr-017 | HV §5.3 描述 per-solver-pooled 归一化 + 称"未用全求解器池化(单点求解器会压缩范围)"，statistical_analysis.py 实际全局池化；单点求解器各贡献 200 点不压缩 | R1 MAJOR + DA | **确认**（statistical_analysis.py L210-259 全局归一化，statistical_results.json 单一全局区间；hv_by_solver 与论文表逐位一致） | §5.3 对齐实现（改描述为全局归一化）；单点求解器各 200 点修正 |
| rdr-018 | HV 表省略 G-SM（G-SM HV=0.1023 全场最高 > MOEA-3 0.0593）；表 2 排序 MOEA-3>MOEA-2>G-BL 纳入 G-SM 后反转；per-solver-pooled 下跨 solver HV 比较可疑却用于 Wilcoxon δ=-0.58 | DA MAJOR | **确认**（hv_by_solver 数据） | 披露 G-SM HV 或说明省略理由；HV 只作 within-solver 趋势 |
| rdr-019 | 密度类异质未披露：S1-D/S3-D n_orbits=1、S2-E 高纬(±40-70°)、S4-D incidence_max=25°、S4-B 强聚集(n_sel≈36)；"三种分布类型"描述不完整；密度效应与窗口几何混淆 | R1 MAJOR | **确认**（generate_all_scenarios.py：S1-D/S3-D n_orbits=1、S2-E high_lat ±40-70°、S4-D incidence_max=25°、S4-B n_sel=35.6；簇数 2/5/10/20 各异） | §5.1 披露 A-E 全部配置；按子配置分层报告 S4；证明 N 趋势不受 S4-D/B 影响 |
| rdr-020 | f1* 归一化循环性：f1*=f1/f1_G-BL，G-BL 又作热启动种子；"MOEA 覆盖接近 1.0" = "种子+G-BL 归一化指标上接近" | R1 MINOR | 确认（定义） | 显式说明循环性（§6.6 已诚实，补明确表述） |
| rdr-021 | 热启动随机初始化对照样本小（10/4/5/5 场景×3 seeds；D 15+15）且全部求解器被 G-BL 种子注入，存在循环论证风险 | EIC MAJOR | 确认（数据） | 主张降级为"G-BL 种子条件下"（摘要/结论已部分限定，补全）；或扩样本（算力所限可豁免，说明） |
| rdr-022 | MOEA-2(H=13)/MOEA-3(H=91) 参考点不对称，"第三目标 +84%" 可能部分来自参考点密度 | EIC MAJOR | 确认（H 定义） | 显式讨论并列为限制；或等参考点对照 |
| rdr-023 | "Greedy methods approach Pareto-optimal coverage" 无最优性界；L990 承认无精确解；random-search 只证明 random≤greedy | R3 MAJOR | 确认（无 bound） | 降级为"G-BL-seeded 求解器在覆盖上收敛到 G-BL 附近"（empirical）；MILP 小实例 bound 列为 future work |
| rdr-024 | 摘要 "+58% f3 at only 2% coverage cost" 选择性：同场景 MOEA-3 f2 比 G-BL 低 6%（0.540 vs 0.574）；摘要未提几何质量代价 | EIC+R3+R2 | 确认（Table1） | 摘要补 f2 代价句 |
| rdr-025 | 无 wall-clock runtime 数据；运营论文 runtime 决定性 | R3 MAJOR | 确认（论文只写 single CPU core） | 补每求解器×密度均值 runtime（如有数据）或声明不比较 runtime + 拒 wall-clock（见记忆 feedback-wallclock） |
| rdr-026 | used_gbl_fallback 标志未持久化（so_f1.py 内存设置，runner 未落盘）+ GA-P-BL 无 solver seed（不可复现） | DA MAJOR | **确认**（快照无此字段 + run_so_f1_bl 无 seed） | 代码修：runner 落盘 used_gbl_fallback + 固定 seed；重跑 GA-P-BL（如影响数据则更新） |
| rdr-027 | per-task f2-f3 pooled r 混入 schedule 间方差；S3/S4 ~150-200 任务/调度 vs S1 ~18，池化权重随密度剧变；应补 per-schedule 相关分布 | R1 MINOR + DA MAJOR | **确认**（schedule_correlation.json 只 pooled；补算 per-schedule：S1 mean -0.602/median -0.670/range[-0.967,+0.248]/Fisher-z -0.643 vs pooled -0.611，含正 r 调度） | 补 per-schedule 相关（Fisher-z 均值）或降级表述 |

## MINOR（文字/表述，S5 批量）

| RDR | 意见 | 来源 |
|---|---|---|
| rdr-028 | +4.5%(摘要/§6.1) vs +4.7%(§6.3/Table) f2 增益口径不统一 | EIC+R1 |
| rdr-029 | S2 f1* 0.98(Table1) vs 0.985(Table4)；S4 1.00 vs 0.996 四舍五入不一致 | EIC+R1 |
| rdr-030 | N50：§6.3 称"CI 不收敛"但实际 n50_logistic.json/重跑 CI=[30,62] 收敛（1000 bootstrap 全有效）；§7.2 "具体转换估计"过强；**另 gen_all_figures.py:647 bootstrap 用 b>0 过滤正斜率致 n50_samples 空 CI=nan（图无 CI 带，代码 bug）** | R1+DA | **确认**（n50_logistic.json N50=50 CI=[30.2,61.8]） | §6.3 改"有限 CI[30,62] 但仅 2 信息点，弱约束"；修 gen_all_figures.py b>0 bug |
| rdr-031 | highlights #3 "MOEA-2/3 near-identical redundant anchor-independent" 与正文冲突（稀疏 +84%）；"anchor-independent" 与 finding(5) 张力 | EIC+R2+DA |
| rdr-032 | Moreira2025 bib 卷/年不一致（Proc IEEE 卷 114 应为 2026 非 2025） | R2 |
| rdr-033 | "generated under the same Sentinel-1 bilateral configuration"——Sentinel-1 右视 only，bilateral 非 Sentinel-1 配置；S7/S8 平台称谓统一 | EIC+R3 |
| rdr-034 | §6.2 "G-SM schedules at most 44% of tasks" 无表支撑（Table2 只给 f1* 利润比） | EIC |
| rdr-035 | 摘要 230 词超 ASR ~200 词上限；"not identifying a superior solver" 句可精简 | EIC |
| rdr-036 | §6.4 vs §7.1 findings 五点重述冗余 | EIC |
| rdr-037 | C3/C4 非绑定未在 Limitations flag（真实 SAR 能源/下行常为绑定资源） | R3 |
| rdr-038 | fixed dwell 30s 移除决策变量未在 Limitations 声明 | R3 |
| rdr-039 | f2 未加权均值 vs f1 优先权重：高优先目标与低优先同等几何权重 | R3 |
| rdr-040 | f3 flat-Earth 未声明（并入 rdr-016 或单列）；Sentinel-1 类参数下 | R3 |
| rdr-041 | r_null=-0.51 "exact partition" 措辞过度；θ/ψ 独立均匀是任意假设 | R2 |
| rdr-042 | |ψ|≤45° 最大斜视假设未注（真实平台斜视能力远小，若 ψ_max=5° 结论平凡化） | R2 |
| rdr-043 | Friedman 检验指标(HV)未指明；scipy 无并列修正（G-BL=GA-P-BL 大量并列） | R1+R3 |
| rdr-044 | zsplit 将 ~1e-17 浮点噪声当非零 → G-BL vs GA-P-BL 虚假 p=0.084 | R1 |
| rdr-045 | Cliff δ 定义：(gt-lt)/n 并列计 0 非 0.5；阈值标"Vargha-Delaney"实为 Romano 等 | R1 |
| rdr-046 | "population 200 不改变结论"无数据支撑（p1-4_variant_d_rerun 空目录） | R1+DA |
| rdr-047 | variant D 噪声 RandomState() 无种子不可复现 | DA |
| rdr-048 | envelope -0.97 vs 脚本注释 -0.95 数字核对 | DA |
| rdr-049 | 新颖性声明未对照中文 SAR 质量调度文献补查 | R2 |

## 裁决类（❌ 批注有误 / 豁免候选，S3 对抗后裁定）

- "删除 GA-P-BL"（R3 建议移除 guard）——**豁免**：GA-P-BL 作为 G-BL 利润最优性对照有保留价值，改为正确 framing（rdr-010/012）
- runtime 数据缺失（R3 MAJOR）——**部分豁免**：不比较 runtime 是本论文设计（记忆 feedback-wallclock 休眠注水），补声明即可
- 无最优性界（R3）——**部分豁免**：降级措辞 + future work，MILP bound 不新做（计算成本）

## 对抗验证结果（agent ab5c01c61f46b9095，7/7 全部验证）

- **5 确认**：rdr-014（ψ 数据 vs 论文断言）、rdr-017（HV 全局归一化）、rdr-019（密度类 A-E 异质）、rdr-030（N50 CI[30,62] 收敛 + gen_all_figures.py b>0 图脚本 bug）、rdr-027（pooled r 只 pooled，per-schedule 有正 r）
- **2 部分确认**：rdr-015（包络采样未过滤 C1，描述错但 -0.97 数值稳）、rdr-016（f3 近似未量化，17% 高估正确）
- 额外代码 bug：gen_all_figures.py:647 bootstrap `b>0` 过滤 → N50 图无 CI 带（并入 rdr-030）

## 待办（S3 收尾）

- [x] 对抗验证（7/7 完成）
- [ ] σ 扫描重跑结果（rdr-009，后台 bdkiv9znq）
- [ ] 统计 pass + ppw:logic
- [ ] REVIEW_INDEX 登记 S2/S3 批次
- [ ] Gate M2 确认

## Gate M2（S2 完成，临时化）

- DA-CRITICAL 2 条（rdr-008 §7.2、rdr-010 G-BL 非上限）：已验证 + 有处置 ✓
- 每条 🔴/🟡 有 code/data 验证处置：本表全列 ✓
- Editorial Decision：**Major Revision** → 全条落实（S5）
