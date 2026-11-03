# 第三章论文 v11 全量审查报告

**论文标题**: Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite: Balancing Profit, NESZ, and Geometric Resolution

**审查日期**: 2026-08-02

**审查范围**: 全量更新后的 small-paper-ijae.tex (1209 行) + 辅助文件 + 代码一致性验证

**审查方法**: 三路并行探索 — 论文全文精读、辅助文件逐件分析、代码-论文交叉验证

---

## 1. 审查概述

本次审查对全量更新后的论文进行了端到端复审，涵盖论文内容、辅助文件、代码一致性三个维度。与 v10 审查相比，v10 的 3 项 P1 遗留问题均已修复，但同时发现了 5 项代码-论文参数不一致的新问题，其中 1 项为投稿前必须修复的关键问题。

### 1.1 修复总览

| 维度 | v10 遗留 | 已修复 | 未修复 | 新发现 | 净遗留 |
|------|:---:|:---:|:---:|:---:|:---:|
| v10 P1 级 | 3 | 3 | 0 | — | 0 |
| v10 P2 级 | 4 | 1 | 1 | — | 1 |
| v10 P3 级 | 1 | 0 | 0 | — | 0 |
| **本次新发现** | — | — | — | **12** | **12** |
| **合计** | **8** | **4** | **1** | **12** | **13** |

### 1.2 关键发现

- v10 的 P1 级问题全部修复（HotStart 种子、credit.md Funding Acquisition、cover letter 标题单复数）
- **新发现 1 项 P0 级关键问题**: GA-P-BL 遗传算子参数论文与代码不一致（η_c、p_m 均不匹配）
- 5 项代码-论文描述不一致问题（此前审查未覆盖代码内部参数级一致性）
- 论文内容本身质量高，术语一致性保持良好

---

## 2. v10 遗留问题修复状态

### 2.1 P1 级修复确认（全部已修复 ✅）

| # | v10 问题 | 状态 | 核验详情 |
|---|---------|:---:|----------|
| P1-Remain-1 | HotStart 采样器随机种子不固定 | ✅ 已修复 | `moea.py` L592: `rng = np.random.RandomState(self.seed)`；`so_f1.py` L492: 同样修复。seed 来自 `seed or 1`，确定性可复现 |
| P1-New-1 | credit.md 包含 "Funding Acquisition" | ✅ 已修复 | credit.md 当前 CRediT 角色列表不含 Funding Acquisition，符合论文"无专项资助"声明 |
| P1-New-2 | Cover letter 标题 "Satellites"（复数）| ✅ 已修复 | cover-letter.md L10-11: "an Agile SAR Satellite"（单数），与论文标题一致 |

### 2.2 P2 级修复确认

| # | v10 问题 | 状态 | 核验详情 |
|---|---------|:---:|----------|
| P2-Remain-1 | sar-domain-knowledge.md f2/f3 定义过时 | ❌ 未修复 | L51-55 仍写 f2=NESZ 成像质量、f3=方位分辨率质量，与代码/论文实际定义完全互换 |
| P2-Remain-2 | §7.2 分辨率估算未加注 "ground-range" | ⏳ 待确认 | L1084-1085: "ρ_rg ≈ 5.3 m at θ = 30°"，估算正确但未明确标注为 ground-range |
| P2-New-1 | Highlights 缺少 hot-start 显式限定 | ✅ 已修复 | Highlight 2: "G-BL-seeded NSGA-III..."，Highlight 5: "G-BL-seeded MOEAs..."，均含限定语 |
| P2-New-3 | 参考文献格式不一致 | ⏳ 部分修复 | 6 项中部分已修正，但仍有 3 条条目使用全名而非缩写（见 §4.5） |

### 2.3 P3 级

| # | v10 问题 | 状态 | 核验详情 |
|---|---------|:---:|----------|
| P3-New-1 | 摘要中 SAR 缩写未展开 | ❌ 未修复 | 摘要 L35 首次使用 "SAR" 仍未展开为 "Synthetic Aperture Radar (SAR)" |

---

## 3. 论文内容审查

### 3.1 结构完整性 ✅

论文共 1209 行（主文件）+ 170 行（消融节外部引入），结构完整：

| 节号 | 标题 | 行号 |
|---|---|---|
| Abstract | 摘要 | 34–62 |
| Keywords | 关键词 | 63–65 |
| §1 | Introduction | 70–164 |
| §2 | Related Work | 168–284 |
| §3 | Problem Formulation | 288–449 |
| §4 | Methodology | 453–559 |
| §5 | Experimental Setup | 563–662 |
| §6 | Results and Analysis | 666–1021 |
| §7 | Discussion | 1026–1133 |
| §8 | Conclusion | 1137–1164 |
| — | AI Disclosure / Acknowledgments / CRediT / Funding | 1166–1203 |

**图表引用完整性**：
- 5 个图（fig1–fig5）编号连续，无缺漏，PDF/PNG 文件均存在 ✅
- 6 个表（tab:solvers, tab:scenarios, tab:solver-profiles, tab:hv, tab:scale-sensitivity, tab:ablation）均有定义且被引用 ✅
- 无 TODO/FIXME/XXX/HACK/PLACEHOLDER 标记 ✅

### 3.2 摘要 ✅（1 项小问题）

**缩写展开**：
- NSGA-III: "Non-dominated Sorting Genetic Algorithm III" ✅
- MOEA: "multi-objective evolutionary algorithm" ✅
- NESZ: "Noise-Equivalent Sigma Zero" ✅
- G-BL: "greedy baseline" ✅
- SAR: ❌ 首次使用未展开（P3 级）

**术语**：
- "practically indistinguishable" ✅（L57）
- "saturation regime"（L37）与 "saturation boundary"（L60）双用 — 语义有区分，可接受

**数值声明**：+8.2%（S1）、<2%（S4）、0.18–0.46（随机初始化亏损）— 均与正文一致 ✅

### 3.3 引言 ✅

**贡献声明**（L139–164）列 2 项贡献：
1. 表征经验饱和态 + 消融实验验证
2. NESZ 和几何质量分解为目标 + 区别于标量可见性复合指标

**范围限定**：
- "single-pass, single-satellite Stripmap setting" ✅（L141-142）
- "conditional on greedy-baseline (G-BL) hot-start initialization" ✅（L149-151）

**"五个视角"计数**：§6 结果部分（L745）提及 "five perspectives"，实际包含 5 个子节（§6.1–§6.5 + §6.6），计数匹配 ✅

### 3.4 问题建模

**三个目标**（L340–373）：

| 目标 | 公式 | 代码一致性 |
|---|---|---|
| f₁* | (1/f₁^G-BL) Σ pᵢ | ✅ 一致 |
| f₂ | (1/|S|) Σ sinθᵢ · cosψ_sq,ᵢ | ✅ 一致 |
| f₃ | (1/|S|) Σ cos³θᵢ · cos³ψ_sq,ᵢ | ✅ 一致 |

**约束**（L404–449）：
- 论文定义 C1–C4 四个编号约束
- C1 包含入射角范围 + 斜视角限制（两个子约束）
- C2 包含姿态机动 + 非重叠（两个子约束）
- C3–C4 为能量/内存预算（设为非约束）

**⚠️ 问题**: 论文约束编号 C1–C4 与代码 C1–C7 不对应（详见 §5.4）

### 3.5 方法论

**五个求解器**（Table 1, L460–475）：G-BL、G-SM、GA-P-BL、MOEA-2、MOEA-3 ✅

**⚠️ 参数声明问题**：
- 论文 L527–531 声称 GA-P-BL 使用 SBX(p_c=0.9, η_c=20) + PM(p_m=0.1, η_m=20)
- 论文 L538–539 声称 MOEA "与 GA-P-BL 相同的遗传算子"
- 代码实际参数与上述声明不符（详见 §5.1–§5.2）

### 3.6 实验设置 ✅

- 200 场景（4 类 × 50 种子），N=20–500 ✅
- 统计检验框架完整：Friedman + Wilcoxon + Cliff's δ + Logistic 回归 ✅
- 求解器配置明确，热启动 std=0.5 与代码一致 ✅
- 平台参数（693 km 圆轨道、C 波段 Stripmap）合理 ✅

### 3.7 结果与分析 ✅

**数值声明验证**（抽样核验）：

| 声明 | 位置 | 验证 |
|---|---|---|
| f₂ 改善 S1: +8.2% | L791 | ✅ 与 Table 5 一致 |
| G-SM f₃ 改善 S1: +34% (0.32→0.44) | L763-764 | ✅ 计算正确 |
| 消融 S1 变体 C: +21.6% | 消融文件 L107 | ✅ 与 Table 6 一致 |
| 随机初始化亏损: 0.18–0.46 | L982-983 | ✅ |
| N₅₀ ≈ 140, CI[117,169] | L1000 | ✅ |
| Friedman χ²=506.56 | L1063 | ✅ |
| 包络相关 r=−0.95 | L935 | ✅ |

**无截断/碎片化句子** ✅
**小数位在各表格内部一致** ✅

### 3.8 讨论

**§7.1 术语**：
- "geometric properties" ✅（L1057，无 "physical limits"）
- "empirical convergence effect" ✅（L1054）

**⚠️ L1017 术语精度问题**：
- 行 1017 使用 "indistinguishable"（无限定词），但论文明确指出 MOEA-2 和 MOEA-3 统计上有差异（p=1.4×10⁻⁴）
- 应改为 "practically indistinguishable" 以与摘要 L57 保持一致

### 3.9 结论 ✅

- 范围限定清晰：N=20–500、单星单过境 Stripmap ✅
- 热启动条件性明确声明 ✅
- GA-P-BL 仍超越锚点的限定语到位 ✅
- 局限性列表完整（6 项）✅
- 未重复大量数值数据 ✅

---

## 4. 辅助文件审查

### 4.1 Cover Letter ✅

- 标题单复数已修正 ✅
- 同刊相关稿件披露完整 ✅
- "empirical saturation regime" 术语与论文一致 ✅
- "conditional on G-BL-seeded NSGA-III convergence" 限定语到位 ✅

**小建议**: L42 "All authors have approved the submission" 对单一作者稿件略显冗余，可改为 "I have approved the submission"。

### 4.2 Highlights ✅

5 条亮点均在 85 字符限内 ✅

| # | 内容 | 字符数 | 限定语 |
|---|---|---|---|
| 1 | SAR imaging quality (NESZ, resolution) integrated as MOO objectives | 74 | — |
| 2 | G-BL-seeded NSGA-III reveals an empirical saturation boundary | 77 | ✅ "G-BL-seeded" |
| 3 | MOEA-2 and MOEA-3 near-identical: 3-obj redundancy anchor-independent | 70 | ✅ "anchor-independent" |
| 4 | Multi-objective advantage concentrates in sparse regimes (N≤100) | 63 | ✅ |
| 5 | G-BL-seeded MOEAs converge to a common coverage ceiling at high density | 70 | ✅ "G-BL-seeded" |

### 4.3 CRediT ✅

- Funding Acquisition 未列入 ✅（符合论文"无专项资助"声明）
- 12 项 CRediT 角色完整
- Note 说明导师角色但非共同作者

**小建议**: 作者承担 Supervision 角色与 Note 中导师提供 supervision 存在轻微矛盾。建议在 Note 中更清晰说明博士监督框架下导师角色不构成共同作者资格的理由。

### 4.4 Declaration ✅

标准利益冲突声明，无问题。

### 4.5 Bibliography ⚠️

25 条引用条目，类型分布合理（@article=20, @inproceedings=2, @book=2, @misc=1）。

**问题 A — 作者姓名全名/缩写混用**（3 条）：

| 条目键 | 当前格式 | 应改为 |
|--------|---------|--------|
| `QualityScreening2026` | Li, Linhong and Feng, Qi and Li, Kebo and Liang, Yangang | Li, L. and Feng, Q. and Li, K. and Liang, Y. |
| `Caleiras2026SuperAgile` | Caleiras, Margarida and Moniz, Samuel and Nascimento, Paulo Jorge | Caleiras, M. and Moniz, S. and Nascimento, P. J. |
| `Wu2026WhaleHighDensity` | Wu, Wei and Wu, Xiande and Liu, Fanming and Zhu, Jiaxing | Wu, W. and Wu, X. and Liu, F. and Zhu, J. |

**问题 B — 其他格式细节**：
- 多字母缩写格式不统一（`E.L.` vs `E. L.` vs `J.-F.`）
- 尾逗号不一致（部分条目末字段后有逗号，部分无）
- 文件名 `small-paper-ijae.bib` 与投稿期刊 ASR 不符（不影响功能）

---

## 5. 代码-论文一致性审查

### 5.1 🔴 P0: GA-P-BL 遗传算子参数不一致

**严重程度**: P0（投稿前必须修复）

**论文声明**（L527–531）：
- SBX: p_c=0.9, η_c=20
- PM: p_m=0.1, η_m=20

**代码实际**（`so_f1.py` L543–544，`ga_hotstart_solver()`）：
- SBX: prob=0.9, **eta=15**（η_c 不匹配）
- PM: **prob=1.0/(2*instance.N)**, eta=20（p_m 严重不匹配）

**影响**: p_m=0.1（固定）vs p_m=1/(2N)（N=20时=0.025, N=500时=0.001）——变异概率相差 4–100 倍，直接影响搜索行为和收敛速度。审稿人要求复现时将得到不同结果。

**建议**: 统一论文与代码。若代码为实际运行版本，应更新论文参数；若论文参数为设计意图，应更新代码并重新运行实验。

### 5.2 🟠 P1: MOEA 遗传算子未显式配置

**论文声明**（L538–539）：MOEA 使用"与 GA-P-BL 相同的遗传算子"

**代码实际**（`moea.py` L599–606）：NSGA3 创建时未显式指定 SBX/PM 算子，使用 pymoo 默认值。

**影响**: pymoo 默认算子参数与论文声称的 SBX(p_c=0.9, η_c=20) + PM(p_m=0.1, η_m=20) 不符。虽然 pymoo NSGA-III 默认使用 SBX+PM，但默认参数不同。

**建议**: 在 `moea.py` 中显式配置与论文一致的 SBX/PM 参数，或在论文中说明使用 pymoo 默认值。

### 5.3 🟠 P1: GA-P-BL 染色体编码描述不符

**论文声明**（L521–525）：每个染色体仅编码 τ ∈ [0,1]^N，任务选择向量 x 从约束求解中产生。

**代码实际**（`so_f1.py` L69）：使用 2N 编码（x[0:N] + τ[N:2N]），x 是显式决策变量（阈值 0.5 二值化）。

**影响**: 论文描述与实际实现不符。虽然概念上 x 由 τ 决定（x = τ > 0.5），但代码将两者都作为决策变量。审稿人可能质疑方法论描述的准确性。

**建议**: 更新论文描述以反映实际 2N 编码，或在代码中改为仅编码 τ。

### 5.4 🟠 P1: 约束编号体系冲突

| 约束内容 | 论文编号 | 代码编号 | 一致性 |
|---------|---------|---------|--------|
| 角度可行性 | C1（部分） | C1 | ⚠️ |
| 分辨率 | — | C2 | ❌ |
| 姿态转换 | C2 | C3 | ❌ |
| 能量 | C3 | C4 | ❌ |
| 存储 | C4 | C5 | ❌ |
| 无目标重复 | — | C6 | ❌ |
| 斜视角 | C1（部分） | C7 | ❌ |

**影响**: 论文使用 C1–C4（4 个编号约束），代码使用 C1–C7（最多 7 个）。编号完全不对应，审稿人对照代码时将产生困惑。

**建议**: 统一约束编号体系。建议在论文中明确约束与代码的对应关系，或统一编号。

### 5.5 🟠 P1: C1 执行位置描述不符

**论文声明**（L413）：入射角和斜视角约束（C1）在可见窗口生成阶段强制。

**代码实际**（`moea.py` L218–220）：斜视角约束作为罚函数在 `_evaluate()` 中在线检查，而非在窗口生成阶段预过滤。

**影响**: 论文声称预过滤但代码实际为在线罚函数，两种方法对搜索空间的影响不同。

**建议**: 更新论文描述以反映实际实现（在线罚函数），或在代码中实现窗口生成阶段的预过滤。

### 5.6 🟡 P2: G-SM 实现结构不一致

**论文声明**（L502）："G-SM 共享 G-BL 的贪婪结构（按最早开始时间排序）"

**代码实际**（`baselines.py` L627）：G-SM (baseline_b3) 委托给完全不同的 `greedy_solver` 模块，而非复用 G-BL (baseline_b1) 的排序逻辑。

**影响**: 两个基线求解器的贪婪逻辑不同，与论文"共享结构"的声明矛盾。

**建议**: 更新论文描述，或统一 G-SM 实现以复用 G-BL 的排序逻辑。

### 5.7 🟡 P2: constraints.py 缺失 C7 验证

**问题**: `moea.py` 和 `so_f1.py` 均实现了 C7（|ψ_sq| ≤ 45°）作为罚函数，但 `constraints.py` 的独立验证器 `ConstraintVerifier.verify_solution()` 仅检查 C1–C5，不检查 C7。

**影响**: 验证报告不完整，无法独立确认求解器输出的解满足斜视角约束。

**建议**: 在 `ConstraintVerifier` 中添加 C7 检查。

### 5.8 🟡 P2: sar-domain-knowledge.md f2/f3 定义过时

**问题**: 领域知识文档 L51-55 仍记载旧定义：
- f2 = NESZ 成像质量（cos³θ / cos³θ_ref）
- f3 = 方位分辨率质量（cos ψ_sq）

实际代码和论文定义：
- f2 = 几何分辨率（sinθ · cosψ_sq）
- f3 = NESZ 辐射质量（cos³θ · cos³ψ_sq）

**f2 和 f3 的定义在文档中完全互换。**

**建议**: 更新 sar-domain-knowledge.md 以匹配当前代码和论文。

### 5.9 🟢 P3: nesz_linear() 缺失 cos³ψ_sq

**问题**: `nesz.py` L124-139 的 `nesz_linear()` 函数仅计算 `K_NESZ / cos³θ`，不含 cos³ψ_sq 因子。但模块文档（L6-7）记载 `NESZ(θ, ψ_sq) = K_NESZ / (cos³θ · cos³ψ_sq)`。

**影响**: 该函数标注为 "DIAGNOSTIC ONLY"，不影响优化目标计算（f3 在 moea.py 中内联计算，公式正确）。但诊断函数与文档公式不一致可能引起混淆。

---

## 6. 术语一致性

### 6.1 已修复并保持的术语 ✅

| 术语 | 状态 | 核验 |
|------|:---:|------|
| "saturation regime" | ✅ | 摘要 L37, Intro L141 |
| "saturation boundary" | ✅ | 摘要 L60, Conclusion L1156/1161 |
| "practically indistinguishable" | ✅ | 摘要 L57 |
| "geometric properties" | ✅ | §7.1 L1057（无 "physical limits"） |
| "empirical convergence effect" | ✅ | §6.4 L927, §7.1 L1054 |
| 消融 Δ 符号 | ✅ | 消融节一致使用 |
| "hot-start" 条件性 | ✅ | 贡献声明 L149-151 |

### 6.2 新发现术语问题

| # | 问题 | 位置 | 严重程度 |
|---|------|------|---------|
| T-1 | "indistinguishable" 无限定词 | L1017 | P2 — 应改为 "practically indistinguishable" |
| T-2 | NESZ 大小写不一致 | L39,94,244 vs L64,217 | P3 — "Noise-Equivalent Sigma Zero" vs "noise-equivalent sigma zero" |
| T-3 | G-BL 连字符不一致 | 摘要 L49 "greedy baseline" vs L152 "greedy-baseline" | P3 |
| T-4 | AEOS 未展开 | L199-200 | P2 — 应为 "Agile Earth-Observation Satellite" |
| T-5 | MOEA/D 未展开 | L483 | P3 |
| T-6 | SMS-EMOA 未展开 | L483 | P3 |

### 6.3 排版一致性

| # | 问题 | 位置 | 严重程度 |
|---|------|------|---------|
| F-1 | `\citep` 前空格不一致 | 6 处用 `~`，5 处用普通空格 | P3 |
| F-2 | `\S\ref` vs `\S~\ref` 不一致 | L622, L623, L654 缺少 `~` | P3 |

---

## 7. 新发现问题优先级清单

### P0 级（投稿前必须修复）

| # | 问题 | 文件 | 预计修复时间 |
|---|------|------|:---:|
| P0-1 | GA-P-BL 遗传算子参数不一致（η_c=20 vs 15, p_m=0.1 vs 1/(2N)） | 论文 L527-531 或 so_f1.py L543-544 | 10 min* |

*P0-1 修复时间取决于选择更新论文还是代码。若更新代码需重跑实验，则时间大幅增加。若更新论文参数以匹配代码，则约 10 min。

### P1 级（投稿前应修复）

| # | 问题 | 文件 | 预计修复时间 |
|---|------|------|:---:|
| P1-1 | MOEA 遗传算子未显式配置 | moea.py L599-606 或论文 L538-539 | 5 min |
| P1-2 | GA-P-BL 染色体编码描述不符 | 论文 L521-525 | 5 min |
| P1-3 | 约束编号体系冲突（论文 C1-C4 vs 代码 C1-C7） | 论文 §3.3 或代码 | 15 min |
| P1-4 | C1 执行位置描述不符（论文称预过滤 vs 代码在线罚函数） | 论文 L413 | 3 min |
| P1-5 | L1017 "indistinguishable" → "practically indistinguishable" | 论文 L1017 | 1 min |
| P1-6 | AEOS 未展开 | 论文 L199 | 1 min |

### P2 级（建议修复）

| # | 问题 | 文件 | 预计修复时间 |
|---|------|------|:---:|
| P2-1 | G-SM 实现结构与论文描述不符 | baselines.py L627 或论文 L502 | 10 min |
| P2-2 | constraints.py 缺失 C7 验证 | constraints.py | 10 min |
| P2-3 | sar-domain-knowledge.md f2/f3 定义过时 | reference/sar-domain-knowledge.md | 5 min |
| P2-4 | 参考文献作者姓名全名/缩写混用（3 条） | small-paper-ijae.bib | 5 min |
| P2-5 | §7.2 分辨率估算未标注 "ground-range" | 论文 L1084-1085 | 2 min |

### P3 级（可选改进）

| # | 问题 | 文件 | 预计修复时间 |
|---|------|------|:---:|
| P3-1 | 摘要中 SAR 缩写未展开 | 论文 L35 | 1 min |
| P3-2 | NESZ 大小写不一致 | 论文多处 | 3 min |
| P3-3 | G-BL 连字符不一致 | 论文 L49 vs L152 | 1 min |
| P3-4 | MOEA/D 和 SMS-EMOA 未展开 | 论文 L483 | 1 min |
| P3-5 | `\citep` 前空格不一致 | 论文多处 | 5 min |
| P3-6 | `\S~\ref` 不一致 | 论文 L622, L623, L654 | 2 min |
| P3-7 | nesz_linear() 缺失 cos³ψ_sq | nesz.py L124-139 | 5 min |
| P3-8 | Cover letter "All authors" 单一作者冗余 | cover-letter.md L42 | 1 min |

---

## 8. 投稿就绪度评估

### 8.1 维度评分

| 维度 | v10 评分 | v11 评分 | 变化 | 阻塞项 |
|------|:---:|:---:|:---:|--------|
| 论文内容 | 97% | 96% | ↓1% | L1017 术语、编码描述、约束编号 |
| 数据完整性 | 98% | 98% | — | — |
| 代码正确性 | 95% | 85% | ↓10% | P0 参数不一致、MOEA 算子未配置 |
| 可复现性 | 90% | 80% | ↓10% | P0 参数不一致直接影响复现 |
| 术语一致性 | 98% | 95% | ↓3% | L1017、AEOS、NESZ 大小写 |
| 辅助文件 | 90% | 92% | ↑2% | bib 作者姓名（3 条） |

### 8.2 评分变化说明

代码正确性和可复现性评分下降的原因是：本次审查首次深入代码参数级一致性检查，发现了 v10 未覆盖的算子参数不匹配问题。这些问题并非本次更新引入的新缺陷，而是此前审查未触及的深层一致性问题。

### 8.3 总体就绪度: ~88%（v10: ~93%）

就绪度下降反映的是审查深度的提升，而非论文质量退步。论文内容本身质量保持高水平。

---

## 9. 审查结论

### 9.1 论文整体评价

论文科学质量高，实验设计严谨，统计分析规范，术语一致性总体良好。核心贡献（经验饱和态的发现与表征、物理目标分解为多目标）具有实质学术价值。消融实验和初始化控制实验的设计体现了良好的实验方法论。

### 9.2 关键阻塞项

**投稿前必须解决的唯一 P0 问题**是 GA-P-BL 遗传算子参数不一致。这有两种修复路径：

**路径 A（更新论文以匹配代码）**：
- 将论文 L527-531 的参数改为 SBX(η_c=15)、PM(p_m=1/(2N))
- 同时说明 MOEA 使用 pymoo 默认算子
- 优点：无需重跑实验
- 风险：p_m=1/(2N) 的变异策略需在方法论中解释合理性

**路径 B（更新代码以匹配论文并重跑）**：
- 修改 so_f1.py 和 moea.py 的算子参数为 η_c=20, p_m=0.1
- 重跑全部 200 场景 × 5 求解器
- 优点：论文参数描述保持不变
- 风险：重跑结果可能改变，需重新验证所有数值声明

**推荐路径 A**，因为 1/(2N) 是合理的变异概率策略（与问题规模成反比），只需在论文中如实描述。

### 9.3 修复时间估算

| 优先级 | 项数 | 预计总时间 |
|--------|:---:|:---:|
| P0 | 1 | 10 min（路径 A）|
| P1 | 6 | 30 min |
| P2 | 5 | 32 min |
| P3 | 8 | 19 min |
| **合计** | **20** | **约 91 min** |

### 9.4 推荐意见

**推荐**: 修复 P0 级参数不一致问题后即可投稿。P1 级问题建议在投稿前一并处理（约 30 min），P2–P3 级可在审稿返回后修订阶段处理。

---

*审查报告生成时间: 2026-08-02*
*审查工具: Trae AI Agent (三路并行探索)*
*论文版本: small-paper-ijae.tex (1209 行, 全量更新后)*
*代码版本: src/sar_sim/ (moea.py, so_f1.py, baselines.py, nesz.py, types.py, constraints.py)*
