# Wave B 审查报告 — seat=ars-method

审查对象：`papers/sliding-spotlight-scheduling/paper/main.tex`（当前 HEAD 工作树，含新增 Fig 2/4/6/7/8），目标期刊 Aerospace Science and Technology。
审查身份：应用期刊审稿人 + 方法学席 + Devil's Advocate。
读数基线：`experiments/v5_results/` 下的 `reading_ledger_l8.json`、`figure_data/*.json`、`counterfactual_fd/*`、`mode_decomposition.json`、`margin_sensitivity.json`、`served_fraction.json`、`tier_shift/`、`budget_check/`、`anchor_free/`、`scenarios/*.json`；实现侧 `sss_core/predicates.py`、`sss_core/evaluator.py`。

## 0. 红线复述

1. 只读：未修改仓库任何文件，唯一写入是本报告。
2. 每条发现给出 `file:line` + 原文引句 + 为什么是问题 + 建议修法；无引句的发现作废。
3. 严重度：P0 = 事实错/数字错/物理错/自相矛盾；P1 = 论证缺口/口径漂移/误导读法；P2 = 表述与结构。
4. 不确定处写 QUESTION 并说明裁定所需材料；口味不作缺陷。
5. 审的是当前工作树 `main.tex`（8 图 3 表）。

**总结**：1 个 P0、8 个 P1、5 个 P2。P0 是 §3.4 的 C3 归一化参考写成了一个常数，而同小节后文、实现代码和本文自己的 Fig 7 数据都用逐任务任务律参考——按论文写下的常数，C3 在本文自己的数据上就会违例，"C3 结构上永不绑定"这一断言随之失效。方法学层面最重的一条是地板归因的基准问题（P1-1）：20.01/44.78 这两个进了摘要的数字，是把"地板把上限压低了 25.16/49.93"与"订单点构造缺口 5.15"净额相抵后的结果，而 §6.2 明确说这 5.15 不可归因。

---

## 1. P0

### P0-1 C3 的归一化参考：正文写常数，同小节后文/代码/本文图数据都是逐任务任务律参考

**证据 A（正文定义）** — `main.tex:206`（§3.4 Constraints and objectives，`\label{sec:constraints}`）：

> "Per-task duty is normalised against the mode-library envelope reference $T_{\mathrm{env,max}}=10.5830$~s (the largest feasible scene dwell at the envelope-edge squint, attained by SPT; a planar-closure reading at the $45^{\circ}$ edge, inheriting the Earth-curvature extrapolation of Section~\ref{sec:geometry}) with mode weights STR/SLS/SPT $=1.0/1.15/1.3$; the normalisation denominator is the largest weight times the envelope reference, $1.3\,T_{\mathrm{env,max}}$"

**证据 B（同小节、隔五行的自相矛盾）** — `main.tex:211`：

> "the normalisation reference was redefined on 2026-10-20, on the day the sweep ran, from the mode-library constant dwell to the per-task envelope-maximum task-law dwell, after the task-law dwells were measured to exceed the library reference by up to $1.2008\times$ on the 50-task family (theoretical worst $1.274\times$) and had produced false violations"

同一小节的第 206 行说参考是常数 $10.5830$ s，第 211 行说参考已被改成逐任务任务律驻留。二者不能同时为真。

**证据 C（实现）** — `sss_core/predicates.py:269`：

> `ref = max(C3_WEIGHTS.values()) * _t_env_max(lib, r0_m, rho_req_m)`

`_t_env_max`（`predicates.py:141-143`）在 `rho_req_m is not None` 时走 `max(_task_envelope_durations(lib, r0_m, rho_req_m).values())`，即逐任务任务律包络最大值，不是常数；其 docstring（`predicates.py:119-120`）自己写着：

> "SPT rho=0.300907 at psi_star=42.98 deg: 13.4829 s vs the library 10.5830 s = 1.274x"

**证据 D（生产路径确实传入逐任务订单）** — `sss_core/evaluator.py:524-527`：

> `if not c3_ok(plan.mode, self._dwell(i, starts[i]), self.lib, r0_m=w.r0_m, rho_req_m=plan.rho_req_m):`

所以跑出本文全部数据的那条路径用的是**逐任务任务律参考**，论文 §3.4 第 206 行描述的是一个没有跑过的 C3。

**证据 E（本文自己的图数据在常数口径下就会违例）** — `figure_data/fig7_dwell_distribution.json`：

- `fig7.R3H.SPT.T_p95 = 10.5965` s
- `fig7.R2F.SPT.T_p95 = 10.7898` s

两者都大于论文声明的 $T_{\mathrm{env,max}}=10.5830$ s。按第 206 行的口径，SPT 归一化占空 = $1.3\times10.5965/(1.3\times10.5830)=1.0013>1.0$。而 `main.tex:211` 断言：

> "both budgets are \emph{structurally} \emph{never binding} inside the squint envelope (their normalised values cannot exceed 1.0 there, so the binding channels are C2 and interval conflicts)"

即：按论文写下的常数，本文 Fig 7 的 SPT 驻留分布尾部（p95 以上，R3H 约 5% 的驻留）就会触发 C3，与"cannot exceed 1.0"直接冲突。按实际实现的逐任务参考则不冲突——这正说明写进论文的是错的那一版。

**为什么是 P0**：这是"公式/文字声明与实现不符"（任务书 code 席第 ⑤ 项明列为 P0 的情形），同时是同一小节内的自相矛盾，且被本文自己的图数据证伪。审稿人只要把 Fig 7 的 p95 和 §3.4 的常数并排看就能发现。

**建议修法**：把第 206 行改成"参考 = 该订单在包络几何下、可服务该订单的各模式中任务律驻留的最大值，再乘最大模式权重 1.3"；$10.5830$ s 只作为库常数基线出现，并紧跟一句"在 $1.274\times$ 的细订单端该库常数不再是上界，故 2026-10-20 起改用逐任务任务律参考"（即把第 211 行那句话前移到定义处，或在此处前向引用）。同时把第 211 行"theoretical worst $1.274\times$"与"$1.2008\times$ 实测"的对应关系保留在定义点，否则读者无法判断参考到底随什么变。

---

## 2. P1

### P1-1 地板归因 20.01/44.78 用的是"观测订单点"作基准，净掉了 §6.2 自称不可归因的 5.15pp

**证据** — `main.tex:307`：

> "The floor-exclusion upper bound ... already caps the family at 0.748 at $s=0.9$ and 0.501 at $s=0.8$: the floor accounts for 20.01 of the 26.01-point drop to $s=0.9$ and for 44.78 of the 46.58-point drop to $s=0.8$, and the residual gap between the bound and the observed medians (6.0 and 1.8 points) is the schedule falling short of a bound that is itself floor-driven."

**复算**（`mode_decomposition.json`：`R3H.rows["0.9"].upper_bound = 0.7484`、`rows["0.8"].upper_bound = 0.5007`、`rows["1.0"].upper_bound = 1.0`、`rows["1.0"].observed_median = 0.9484791`）：

- 论文的算式是 $\mathrm{obs}(1.0)-\mathrm{bound}(0.9)=0.9484791-0.7484=0.20008\to20.01$，$\mathrm{obs}(1.0)-\mathrm{bound}(0.8)=0.44778\to44.78$。
- 地板**自身**的效果是 $\mathrm{bound}(1.0)-\mathrm{bound}(0.9)=1.0000-0.7484=0.2516\to25.16$，$\mathrm{bound}(1.0)-\mathrm{bound}(0.8)=0.4993\to49.93$。
- 两个数恰好相差 $0.05152\to5.15$，即订单点观测值相对自身上限的缺口（$1.0-0.9484791$）。

而 `main.tex:350` 明确说这 5.15pp 不可归因：

> "no upper bound tighter than the trivial 1.0 is available at $s\ge 1.0$ (the floor-exclusion bound is trivially 1.000 there, Table~\ref{tab:modes}), so they are not attributed between genuine C2/interval infeasibility and construction shortfall"

**为什么是问题**：一处说订单点缺口不可归因，另一处却把这个缺口当作基准的一部分、把"地板压低上限 25.16"报成"地板占 20.01"。摘要（`main.tex:29` "the stripmap floor accounting for 20.0 and 44.8 of those points"）与结论（`main.tex:481` "of which the stripmap floor accounts for 20.0 and 44.8 points"）都带这两个数字，读者会以为地板的贡献是 20.0，而按同一份 artifact 的 bound-to-bound 读法是 25.2（占 26.0 的 96.7%，而不是 76.9%）。这不是算错，是标签与基准不一致，且该不一致对"地板 vs 驻留机制"这条 §6.1 的核心分解有实质影响。

**建议修法**：二选一并写清基准——(a) 用 bound-to-bound 报"地板自身压低上限 25.16/49.93，观测再在 $s=0.9$ 低于上限 6.0、$s=0.8$ 低于 1.8"；或 (b) 保留 20.01/44.78，但把该术语改名为"上限下降扣除订单点缺口后的净额"，并在同句给出 5.15 的来源。摘要/结论随之改一个数字即可。

### P1-2 头条覆盖率差没有离散度，且同一节内 paired/unpaired 口径漂移

**证据 A（无离散度）** — `main.tex:348`：

> "from the as-placed point to $s=0.9$ the median coverage drops 26.0 percentage points for R3H and 46.0 for R1C, and to the tightest feasible point 46.6 for R3H, while R2F holds within 0.27 points (0.00 at $s=0.8$)."

全文检索 `bootstrap`、`confidence interval`、`95\%` 均无命中；`per-seed range` 只在 `main.tex:422` 出现一次，且那是反事实 gap 的逐 seed 范围，不是覆盖率差。Fig 5 画了 per-seed 点（可视离散），但三个头条差值与 4.15/2.36 都没有任何区间。

**复算**（ledger `coverage.per_seed.*`，配对逐 seed 差 $s{=}1.0$ 减 $s{=}0.9$，20 000 次 bootstrap，seed=0，percentile）：

| 量 | 论文值（median 之差） | 配对 median | 配对 bootstrap 95% CI |
|---|---|---|---|
| R3H $s{=}1.0\to0.9$ | 26.0 | 25.59 | **[18.03, 30.15]** |
| R1C $s{=}1.0\to0.9$ | 46.0 | 42.07 | **[34.55, 50.00]** |
| R3H $s{=}1.0\to0.8$ | 46.6 | 46.98 | **[38.98, 49.59]** |

即 26.0 这个头条的 10-seed 区间宽约 12pp，46.0 宽约 15pp。

**证据 B（口径漂移）** — `main.tex:350` 对"放松方向"的代价明确采用配对口径并解释差异：

> "Both costs also have a paired per-seed form --- the median over seeds of each seed's own saturation-minus-as-placed difference --- which reads 3.98 points for the mixed family and 0.93 for the 50-task family; the paired statistic is smaller than the median-of-medians because several seeds already saturate at the loose end."

但同一节第 348 行的收紧方向差用 median 之差，不配对，也不提配对值（42.07 vs 46.02）。R1C 的 3.95pp 差距有明确机制：`coverage.per_seed.R1C.s1.0 = [0.9145, 1.0, 0.9466, 1.0, 1.0, 0.9444, 1.0, 1.0, 1.0, 0.9483]`，10 个 seed 里 4 个严格小于 1.0，median 被钉在 1.0，median 之差因此系统性放大。论文对"天花板导致 median 之差偏大"的机制在别处已经讲清楚（`main.tex:350` 同句），却没有用在自己最重要的那个数上。

**为什么是问题**：同一个 §6 里两个方向用两套口径，且无一套给区间；n=10 的 median 差被当作点估计写进摘要与结论。这是应用期刊统计读数的标准缺口，也让"46.0"这个数在审稿人复算时对不上（复算得 42.07）。

**建议修法**：在 §6.1 或 §6.2 加一张 3×2 小表（median 之差 / 配对 median / bootstrap 95% CI），正文对收紧与放松统一用配对值并同时给 median 之差；摘要里至少保留一位"median over ten seeds"的限定词。

### P1-3 反事实的两个区间都是"中位数之区间"，且结论的 7–30 把本文自己报的保守臂 55.5 排除在外

**证据 A** — `main.tex:29`（摘要）：

> "violates the transfer constraint in 27--42\% of consecutive pairs on the dense families of this scenario set, and after repair the replayed plans land 7--30 points of served priority below the endogenous-dwell schedule"

**证据 B** — `main.tex:481`（结论）：

> "planned with the library dwell, the dense families violate the transfer constraint in 27--42\% of consecutive pairs and, after repair, land 7--30 points short, the span depending on the repair rule"

**复算**（`counterfactual_fd/counterfactual_summary.json`）：`R2F.violation_rate_pure_median = 0.4239`（min 0.383, max 0.500）、`R3H.violation_rate_pure_median = 0.2742`（min 0.1739, max 0.3441）。所以 27–42% 是**两个族中位数构成的区间**，单个 seed 的读数是 17.4–50.0%；修复后（非 pure）`R2F 0.289`（0.25–0.3478）、`R3H 0.2022`（0.1304–0.2473）。

**证据 C**（7–30 的边界）— `main.tex:418`（Fig 8 图注，本文自己报的）：

> "the conservative pre-shrunk fixed dwell: no violating pair by construction (0 of 324 and 0 of 354 pairs) at the price of 28.3 and 55.52~pp (50-task and 100-task families respectively)"

`counterfactual_summary.json` 的 `conservative.R3H.gap_pp_median = 55.52`（min 51.98, max 69.1）、`conservative.R2F.gap_pp_median = 28.3`。结论说反事实"quantifies what the endogenous dwell buys ... land 7--30 points short"，而同一反事实的保守臂中位数是 28.3 与 55.5，最大到 69.1——远超 30。读者从摘要/结论会取 30 为上限。

**为什么是问题**：(a) 27–42% 不带 "median" 且不带 per-seed 跨度，读起来像该现象本身的区间，实际 10 个 seed 里有一个是 50.0%；(b) 7–30 是三条修复规则的中位数区间，但本文还报了一条不在其中的臂，且该臂的短差更大。摘要/结论的范围与其所引章节的范围不一致，属于"限定未一致携带"。

**建议修法**：摘要改"median 27–42%（per-seed 17–50%）"；结论补一句"保守预缩臂 28.3/55.5pp（无违例对）"，或把 7–30 明确写成"三条修复规则的中位数区间，不含保守臂"。

### P1-4 S1 与 S3 用两套容差：S1 判"not met"所依据的位移，比 S3 明确宣布为可忽略的容差还小

**证据 A** — `main.tex:293`（§5.3，容差定义）：

> "The one-priority-unit tolerance is one count of the priority numerator, $1/\sum_i p_i$ of the scenario --- the smallest nonzero priority movement --- which, at the median scenario of each family, is 0.89 (R1C), 0.38 (R2F) and 0.19 (R3H) points at the registered task counts"

**证据 B** — `main.tex:356`（§6.3）：

> "The 50-task family fails S1 under both; its tight arm does not fall under either reading (the two dips of Section~\ref{sec:dip} sit below the one-priority-unit tolerance), and both failures are reported as results about this scenario set."

**证据 C** — `main.tex:387`（§6.4）：

> "nothing physical follows from either decline: two opposite single-seed displacements are not a monotonicity claim in either direction, and no statement about the demand axis is made from a movement in the third decimal place."

**复算**：R2F 的两个下陷是 0.268pp（0.8→0.9）与 0.359pp（1.3→1.4），均小于 R2F 的 0.38pp 容差；Table 3（`main.tex:373`）却据它们把 S1 判为 "not met"。同时 S3 的比较是 $s{=}0.8$ 与 $s{=}1.0$（0.9764 vs 0.9764，差 0.00），两个下陷与 S3 无关——第 356 行括号里"两个下陷低于容差"作为"S3 不成立"的理由是答非所问（non sequitur）。

**为什么是问题**：同一测量尺度上，0.268/0.359pp 对 S3 是"低于容差、不构成信号"，对 S1 却是"判失败"的依据；论文还在 §6.4 亲口说第三位小数的移动不构成任何关于需求轴的断言。三个判定（Table 3 的 S1、S3，正文的两处解释）无法同时成立。这是审稿人最容易抓的"criteria 被选择性应用"。

**建议修法**：二选一——(a) 在 §5.3 注册"容差只适用于 S3，S1 按原始 median 判"并明说 S1 的失败由亚容差位移决定（诚实但难看）；或 (b) 对 S1 也用同一容差，则 R2F 的 S1 变为 "met (within tolerance)"，Table 3 相应改值并在正文说明这是 post hoc 精化。无论选哪条，删掉第 356 行括号里那个与 S3 无关的理由。

### P1-5 摘要的因果句（"哪个模式决定代价形状"）在三族混杂设计里没有被识别

**证据 A** — `main.tex:29`（摘要）：

> "Which mode a task receives decides what shape the cost of a requirement change takes; across the three families, density and mode composition covary by design."

**证据 B** — `main.tex:337`：

> "level differences across families are jointly driven by density and mode composition, which covary by design in this scenario set."

**证据 C** — `main.tex:273`（Fig 4 图注）：

> "Densities and mode composition covary by design across the three families, so nothing in this figure is a controlled comparison."

**为什么是问题**：摘要用 "decides"（识别性动词），而本文三处自认密度与模式构成共变、无对照比较。论文对**水平**的模式依赖有真实的族内证据（Table 2 的地板排除分解在 R3H 内部完成），但对**形状**（step / plateau / collapse）的断言只来自三族之间的一次比较，密度、任务数、窗口数同时变化（145–162 / 337–391 / 731–779 窗口）。三族不是三个模式水平，而是三个混杂对象。这是全篇主张链第③环的唯一识别缺口，且它被写进了摘要的最后一句。

**建议修法**：摘要改为"在本场景集里，三族的代价形状与其模式构成和密度一致，但二者共变，故这一差别不被识别到模式本身"；或补一个族内对照（同一 R3H 清单上把 STR 任务重路由为 SLS，正是 §7.1 第 445 行提到的 registered selection policy 已经允许的救援），把形状差异从族间搬到族内。后者成本高但能救回这条主张。

### P1-6 定位表把本文的模式列写成"由需求决定"，与 §3.5(iii) 的"祖父式赋值"直接冲突

**证据 A** — `main.tex:125`（Table 1 末行）：

> "This paper & endogenous per task and start & reported reading, never optimised & frozen per task by its requirement"

**证据 B** — `main.tex:225`（§3.5）：

> "(iii) the data of this paper follow neither of those at run time: they carry the grandfathered assignment described above. Where this paper says that the mode follows the requirement, it means that the parameters of the \emph{assigned} mode follow the requirement, not that the assignment itself changes."

**为什么是问题**：Table 1 是审稿人判断"本文与最近邻的差别"的唯一一页。Mode 列写 "frozen per task by its requirement"，读起来是"每个任务的模式由它的需求决定"——这正是 §3.5(iii) 否认的事。本文数据的模式是生成时祖父继承的，不随 $s$ 重算（`main.tex:221`）。表格单元格与正文的差别不是措辞，是主张。

**建议修法**：该格改 "grandfathered per task (assignment frozen; parameters follow the requirement)"，并在表注加一句"本文数据不重路由模式"。

### P1-7 局限清单漏掉场景维度代表性，且全文没有外部已发表调度器的对照

**证据** — `main.tex:443-447`（§7.1 五条 scope 声明）分别覆盖：容量律口径、模式赋值冻结、单预算、分辨率–驻留权衡与传感器层、运行层。**没有**一条覆盖场景集的维度边界。场景参数见 `main.tex:136` 与 `main.tex:268`：

> "altitude $h=570$~km, inclination $45^{\circ}$, wavelength $\lambda=0.031$~m, azimuth beam width $\theta_a=0.36^{\circ}$, and a square scene of 5~km side length"

> "The dense domain is a 1000~km square centred at 20°N/0°E, a $5\times 5$ node grid at 250~km spacing with per-cell target jitter, a 3-day span in coordinated universal time (UTC)."

**为什么是问题**：(a) 全部结论来自一个平台（Kim X 波段）、一个倾角（45°）、一个地理域（20°N/0°E、1000 km）、一个 3 天跨度、一个场景模板；驻留闭式、可见窗数、C2 机动链全部随这些维度变，而 §7 的五条 scope 声明一条也没提，读者会以为局限清单是完整的。这是 AST 审稿人必问的"representativeness"。(b) 全文的比较对象只有自己的构造/反事实臂（anchor、anchor-free、16× budget、fixed-dwell replay），没有任何一个已发表调度器在同一清单上的结果；对应用期刊，这不是硬性要求，但当主张是"endogenous dwell 改变了调度结果"时，缺少一个外部基线会让"我们的求解器/构造是否只是弱基线"无法排除。注意 §7.4（`main.tex:473`）已经承认搜索只贡献 2/260 单元，这使外部基线问题更尖锐而非更轻。

**建议修法**：§7.1 加第六条"scenario-set representativeness"，一句话列明单平台/单倾角/单域/单跨度，并说明哪些结论对该维度不敏感（比值型结论）哪些敏感（绝对覆盖率）；外部基线可写进 future work，但要写明"本场景集未与已发表调度器对照，因此本文不主张求解质量优于文献方法"——这句话现在没有。

### P1-8 摘要 272 词，超过已裁决的 ≤250 上限（R-30 未闭合）

**证据** — `main.tex:29` 摘要实测 272 词（`\cite`/数学清理后按空白切分）。`review/author-adjudication-20261023.md` R-30 记录：

> "摘要 305 词 > 250 上限 | will_address | 必修档：随 R-01 重写 ≤250 词"

**为什么是问题**：这不是口味，是目标期刊的形式要求 + 一条已裁决为"必修"的项仍未闭合。投稿系统与编辑部会按字数截断或退改。同时 P1-3、P1-5 的修法都需要往摘要里加限定词，字数只会更紧。

**建议修法**：删掉摘要里可移到正文的两处（"its lower end from a rule added after the sweep" 这一括号可移到 §6.6；"Served priority is the only objective; image quality is reported, never optimised." 可压成半句），并借 P1-3/P1-5 的改写一次性收到 250 以内。

---

## 3. P2

### P2-1 Fig 4 收据把 `drawn` 写成 46–50，论文的 50 drawn / 46–50 admitted 是对的

`figure_data/fig4_scenario_set.json` 的 `fig4.composition_interval.R2F` 为 `{"drawn": "46-50", "admitted": "46-50", ...}`，而 `scenarios/R2F_seed*.json` 的 `generation_ledger.n_drawn` 在 10 个 seed 上全部等于 50，`n_served` 为 46–50（removals 全为 `no_window`，0–4 个）。所以论文 `main.tex:281` 的 "R2F (50 drawn, 46--50 admitted, 337--391 windows)" 与 `main.tex:373` 的 "R2F (50 / 46--50)" 是**正确**的，错的是图注收据字段名/值。影响：任何以收据为 ground truth 的读者或后续门禁会把 drawn 读成 46–50，进而以为 admission 没有剔除。修法：收据侧把该字段改为 `drawn: "50-50"`、`admitted: "46-50"`（本席只读，不代改）。

### P2-2 R2F 的 retention 100.00% 是定义性的，不是测量

`main.tex:400`：

> "retention reads 51.14\% for the control family, 100.00\% for the 50-task family and 71.00\% for the 100-task family"

R2F 的模式构成是 `STR: 0-0`（`fig4_scenario_set.json`、`mode_decomposition.json` 均同），而 retention 的定义是"STR clip 之后仍可行的 tie-set 测度占比"；没有 STR 任务时分子分母恒等，100.00% 是恒等式而非读数。正文没有点明。修法：加"（R2F 无 STR 任务，该值按构造为 1）"。

### P2-3 "the ledger stores it as a status rather than as a value" 只对了一半

`main.tex:352`：

> "the ledger stores it as a status rather than as a value"

`reading_ledger_l8.json` 里确实有 `coverage.status.R1C.s0.8 = "no_feasible_individual"`（unit `status`），但同时还有 `coverage.curve_entry.R1C.s0.8 = 0.0`（note："the value the preregistered C-checks consume"）、`coverage.min/max = 0.0`、`coverage.per_seed = [0.0×10]`（note："exit-11 seeds enter as 0.0 in this array"）。即台账**也**存了 0.0 作为值，而且正是预注册判据消费的那个值。台账的 note 已自解释，所以误导风险有限，但句子本身不准确。修法：改"台账另存一条 status 记录，数值字段按评分约定填 0.0 并附注，不参与曲线"。

### P2-4 25/25 服务性在发布工件里不可复核（论文已披露）

`main.tex:204` 断言 "$25/25$ nodes over 72~h"，`main.tex:268` 说明 "The manifest ledger stores aggregate admission counts, not per-node columns"。披露是诚实的，但一个可复核性主张在发布包里没有对应表。修法：把逐节点 in-band transit 表加进 Zenodo 包（一行 25 个节点即可），或把该句降为构造性断言。

### P2-5 QUESTION：Table 1 第一行把三篇工作压成一格，"exogenous constant" 对 chen2024learning 是否公允无法从本仓库裁定

`main.tex:120`：

> "Agile EO scheduling \citep{long2024deep,qin2024multisatellite,chen2024learning} & exogenous constant & outside the planner & fixed by design"

而 `main.tex:61` 单点引用 chen2024learning 支撑"the observation duration is a task attribute fixed in advance"。若 chen2024learning 的模型含任何形式的可变驻留（哪怕是 learning-based 的时长预测），这一格就把最近邻的差别说小了。裁定所需：chen2024learning 的方法节原文。若确实固定，建议在该行加一句"三篇均为固定时长"，以免读者以为其中某篇不是。

---

## 4. Devil's Advocate：四条核心主张的最强反驳与预答评估

**DA-1「交付恒等式是同义反复，五个约束族里只有 STR 地板真的绑定，约束集是装饰」**
最强形式：C5 由构造满足（$A_{\rm task}$、$\beta_{\rm task}$ 从 $\rho_{\rm req}$ 反解），C3/C4 结构松弛，C1 在生成侧过滤，于是"把需求放进约束集"这件事没有任何约束力，唯一有物理后果的是天线地板。
预答评估：**已预答，且答得干净**。`main.tex:208` 明说恒等式在每次驻留评估处按 $10^{-12}$ 复验、"a violation raises instead of being scored"，并限定为"pointwise at that start"；`main.tex:211` 明说"the set that actually binds in this scenario set is exactly two: the C2 transfer chain and the stripmap floor ... the inventory above is the registered model, not a claim that five mechanisms bind"；`main.tex:196` 明说 AASR 准入"binds on no task"。这不是被动招供，而是主动把约束集的作用重新定义为"把需求送进驻留、再由 C2 定价"。唯一可再加强的：摘要"an identity the solver cannot violate"一句读者可能误读为贡献，可加"（恒等式是需求进入驻留的通道，不是本文的算法贡献）"。

**DA-2「固定驻留基线取的是最脆弱的约定；换成保守基线就零违例，27–42% 是稻草人」**
最强形式：摘要自称用了 "the most fragile fixed-dwell convention"；保守预缩臂 0/324、0/354 违例对，说明"固定驻留不可行"这个说法只在最激进的口径下成立。
预答评估：**正文已预答，摘要/结论未携带**。Fig 8b（`main.tex:418`）与 `main.tex:422` 尾部把保守臂连同 28.3/55.52pp 一并报出，且 `main.tex:418` 明说"the family ordering flips between arms ... neither panel supports a between-family ranking"。这在方法学上是加分项：两臂互为正反面（脆弱臂证明不可行，保守臂证明即使可行也更差）。问题只在摘要/结论的范围界定（见 P1-3）：结论的 7–30 把 28.3/55.5 挡在外面。修好 P1-3，这条反驳即完全关闭。

**DA-3「三族模式依赖没有被识别」**
最强形式：三族同时在密度（20/50/100）、窗口数（145–162/337–391/731–779）、模式构成上变化，形状差异（step/plateau/collapse）无法归给模式；摘要却写 "decides"。
预答评估：**未预答——只做了让步，没有作答**。`main.tex:337`、`main.tex:273` 两处主动声明共变、"nothing in this figure is a controlled comparison"，这是诚实，但不是识别。这是本文唯一一处"承认混杂之后仍然保留了因果动词"的地方，因此是本席认定的最弱环节（见 P1-5）。可救的路径只有两条：改摘要措辞，或在 R3H 族内做一次模式重路由对照。

**DA-4「258/260 说明搜索是惰性的；$s\ge1.0$ 无上界，所以 4.15pp 不可归因，'代价'没有机制」**
最强形式：搜索在 260 个单元里只有 2 个超过锚；订单点及以上地板排除上界恒为 1.0，因此 4.15pp 既不是 C2/区间不可行、也不是搜索不足，而是一个没有解释的残差。
预答评估：**已预答，且是全文最坦率的一段**。`main.tex:350` 明说 "they are not attributed between genuine C2/interval infeasibility and construction shortfall"；`main.tex:473` 明说 "a mode gene would add decision variables to a search whose measured contribution is two units out of 260"；`main.tex:387` 用 anchor-free（12/40 无可行个体、12.9–54.9pp 低于锚）与 16× budget（增益 0.00）两条探针把"惰性"重新定义为"构造承载响应"。唯一残留：论文没说清**需要什么**才能把 4.15pp 归因（例如一个含 C2/区间不可行的上界），建议在 §6.2 末加一句 future work，把这个残差变成可检验的悬置项而不是终点。

---

## 5. 已检查、零发现的方面（明说）

- **数字复现**：摘要/结论/三张表/八张图注中的每一个数都与 `reading_ledger_l8.json`、`figure_data/*.json`、`counterfactual_fd/*`、`mode_decomposition.json`、`margin_sensitivity.json`、`served_fraction.json`、`tier_shift/`、`budget_check/`、`anchor_free/`、`scenarios/*.json` 逐位对上：26.0/46.6/46.0/0.27/0.00、4.15/2.36/3.98/0.93、20.01/44.78（算术可复现，问题只在基准标签，见 P1-1）、27.4/42.4、253/926 与 199/458、18.25/30.44/17.06/30.11/25.33/7.08、28.3/55.52、258/260、477,308/9,430/13,845/34.5×、12/40 与 12.9–54.9pp、15.5pp、0.5114/1.0/0.7100、0.6580/0.7764/0.7447、0.507/0.714/0.935 对 0.483/0.688/0.948、145–162/337–391/731–779、0.905/0.740/0.568/0.540/0.469、≤0.67pp（0.9833−0.9766）。**没有发现第二个数字错。**
- **C4 公式与实现一致**：`main.tex:207` 的 $\mathrm{PRF}\cdot T\cdot N_r\cdot b_q\cdot 2/8$ 与 `predicates.py:285` 的 `prf_hz * dur_s * C4_RANGE_SAMPLES_NR * C4_BITS_PER_COMPONENT * 2 / 8.0` 逐项一致，且 C4 参考确实不带模式权重（`predicates.py:307-310`），与正文"the C4 reference below omits this weight factor"相符。
- **tier-shift 算术**：$s^*=2.4669/(3.0/1.1)=0.9045\to0.905$、$2.4669/(3.0/0.9)=0.7401\to0.740$；移位后 0.568 与原族 0.540 的"同形"判断可接受；$\phi=0.9$ 下 0.469 与"最紧格部分带"一致。**零发现**。
- **图/表引用完整性**：8 张图（Fig 1–8）与 3 张表（Table 1–3）均在正文被显式引用，无悬挂图、无悬挂表。
- **不可行 vs 零覆盖的纪律**：Fig 5 图注、Table 2 的 "---"、Table 3 的 "undefined"、§6.2 的 `\label{sec:floor}` 段四处口径一致，全文未出现把该格当 0 的表述（唯一瑕疵是 P2-3 的台账措辞）。
- **单预算/单种子耦合披露**：`main.tex:291` 主动写明 "the same seed driving both the scenario draw and the search, so scenario-sampling noise and search noise are not separated by the design"，并用 258/260 与 16× 探针界定其影响范围；`main.tex:475` 另有一条单预算声明。**披露充分**（离散度不足是 P1-2，不是披露不足）。
- **预注册时序**：`main.tex:293` 明确区分"网格与三判据先于数据"与"头条曲线为 post hoc descriptive（amendment 2026-10-21 晚于 2026-10-20 sweep）"，并说明 2026-10-23 的精化是第二次 post hoc。诚实且可核。
- **数据可得性**：`main.tex:495` 列出的工件（清单、三档 pilot 记录、预注册与 amendment 链、约定注册表、求解器与生成器源码、复核脚本）与我实际读到的目录一致，无虚指。
- **期刊契合度**：SAR 系统 + 调度/优化双属性落在 AST 范围内；不需要改投建议。唯一需注意的是本文的方法贡献是"锚构造 + 测量"，而非新的元启发式，审稿人可能读成 case study——§4.5（`sec:faces`）已把这一点前置，风险可控。

---

## 6. 对其他席的一句话提示

**theory 席**：§3.4 的 C3 是"正文常数 vs 实现逐任务参考"的错配，纯推导核验会顺利通过（公式本身没错），只有把 `predicates.py:269` 或 Fig 7 的 p95 与 `main.tex:206` 并排才看得见——别只验公式，验"论文写的那版公式是不是跑的那版"。
**code 席**：除任务书第 ⑤ 项外，请顺手核 `_t_env_max` 里"可服务该订单的模式集合"（SLS 的 $A_{\rm task}\in(0,1)$、SPT 无可行起点则跳过）是否与论文"attained by SPT"的表述一致——按任务律参考，最大值未必落在 SPT。
**kdense 席**：`fig4_scenario_set.json` 的 `drawn` 字段语义是错的（P2-1），而图注↔收据 68/68 门禁只比对数值存在与否、不比字段语义，这条不会被门禁抓到。

VERDICT: 1/8/5
