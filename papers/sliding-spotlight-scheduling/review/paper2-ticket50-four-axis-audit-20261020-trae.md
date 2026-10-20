# paper2 票 50 前四轴对抗性审查报告

**作者**: trae
**日期**: 2026-10-20
**对象**: `papers/sliding-spotlight-scheduling/`（paper2）
**性质**: 只读审查；未改动任何源码、论文、数据、注册文件
**方法**: 代码/公式/正文三方对照 + L8 数据逐位复算 + 第一性原理反事实检验

---

## 0. 结论摘要

**判定：Conditional Go（有条件放行）。**

票 50 的定位重写方向（分辨率硬约束 + 单目标覆盖 + 外生扫描轴）在物理上是**必然的**，不是写作偏好：票 49 的交付律已经使"质量作为独立第二目标"在数学上失去独立方差。但当前项目状态**不稳固**，存在 5 个阻断项。其中 B1 是科学有效性阻断，B2–B5 是一致性/治理阻断。

| 编号 | 阻断项 | 性质 | 责任票 |
|---|---|---|---|
| B1 | 扫描轴只缩放订单、冻结模式，制造了论文自身路由规则禁止的配置；R1C/R3H 紧臂塌陷是构造产物 | 科学有效性 | 票 50 决策 + 票 51 重跑 |
| B2 | `f_q` 仍用库零斜视 ρ_a，与票 49 交付律冲突；模式对比叙事物理失效 | 理论一致性 | 票 50 |
| B3 | 论文正文（双目标）与代码（`n_obj=1`）全面脱节，红闸无对应禁语，实测 0 violation | 治理 | 票 50 |
| B4 | 验证链与 5 张图钉死 v3/L6 旧世界，对 L8 无约束 | 可复现性 | 票 50 |
| B5 | 预注册 v2 的 `dq_all`/P1/P2/P3/promotion 在单目标下无定义或为空，未 amendment | 预注册治理 | 票 50 |

**一句话**：票 50 可以启动，但若不在改写前完成 B1 的决策与 B2 的实现，重写后的论文会在"扫描轴测的是什么""质量读数怎么算""90 单元数字从哪来"三处被审稿人直接击穿。

---

## 1. 审查方法与复算清单

全部为只读操作：

| 项目 | 方法 | 结果 |
|---|---|---|
| 论文-代码一致性 | 逐行对照 `paper/main.tex`、`paper/full.md`、`sss_core/*` | 见 §2.2 |
| L8 曲线 | 解析 `experiments/v5_results/sweep_results.json`，独立复算 9 点 × 3 族 | 与 `RUN_LINEAGE.md` 一致，见 §5.1 |
| 前沿结构 | 遍历 260 个 `pilot_*.json`，统计 front 大小、f1 唯一值数、f_q 离散度 | 见 §3.2 |
| 锚点最优性 | 逐单元比较 `max_f1_star_on_front` 与 `anchor_f1_star` | 258/260 相等 |
| 机制归因 | 用 manifest 的模式构成与 ρ 分布，复算 STR 地板越界份额 | R3H 跌幅与份额定量吻合 |
| 数据谱系 | v4/v5 scenarios 80 个文件 sha256 对比 | 80/80 全同 |
| 红闸 | 运行 `check_red_lines.py` | 0 violation / 1070 files |
| 测试 | `pytest papers/sliding-spotlight-scheduling/tests` | 449 passed, 1 skipped, 1373.54 s |

---

## 2. 理论轴

### 2.1 单轴重定位是物理必然，不是写作选择

`sss_core/quality.py` 的 `f_q_per_task` 仍为

```
f_q = 1/(rho_rg * rho_a(mode)) * g_T * (R0/R)^3
```

其中 `rho_a` 取库零斜视常数（STR 2.4669 / SLS 0.5 / SPT 0.3 m）。但票 49 之后：

- SLS 的 `A_task = 2 rho_req cos(psi_sel)/D`，`rho_ach = rho_req`（`duration.py::_check_sls_delivery`，容差 1e-12）；
- SPT 的 `beta_task = lambda/(2 rho_req cos(psi_sel))`，`rho_ach = rho_req`（`_check_spt_delivery`）。

也就是说，**SLS 与 SPT 的交付方位分辨率恒等于订单值**。在 `f_q` 公式中，`rho_a` 这一项对 SLS/SPT 不再随模式区分，三个模式的差异只剩驻留增益 `g_T` 与距离因子 `(R0/R)^3`。

直接后果：

1. 论文 §6.4 的"模式常数 0.8107 / 19.7352 / 54.8322 m^-2，24.3× / 67.6× / 2.8×"叙事（`main.tex:284`、`:289`、`:298`）在交付律下不成立；
2. Fig. 3（f_q vs squint）与 Fig. 6（per-mode decomposition）的解释失效；
3. "quality headroom is a second objective"（`main.tex:52`、`:59`、`:85`、`:89`）不仅是定位过时，而是**目标函数与约束系统互相矛盾**。

这条反而是好消息：票 50 的重定位有硬物理支撑，可以在论文里写成"交付律使质量退化为可计算的读数"，而不是"我们换了个故事"。

### 2.2 论文-代码-公式三方不一致清单

| # | 论文位置 | 现文 | 代码/数据事实 |
|---|---|---|---|
| 1 | `main.tex:29` 摘要 | "carries a per-mode image-quality index as a second objective" | `nsga2.py:SchedulingProblemPymoo` `n_obj=1` |
| 2 | `main.tex:52` 贡献 | "the quality headroom is a second objective" | 同上 |
| 3 | `main.tex:59` gap | "per-mode SAR metric as an independent objective" | 同上 |
| 4 | `main.tex:85` 相关工作 | "entering the optimisation as a second objective" | 同上 |
| 5 | `main.tex:89` gap 收束 | "independent objective dimension simultaneously" | 同上；且该句是 `_NOPRIOR_LEGAL_RX` 唯一合法豁免句 |
| 6 | `main.tex:122` §3.2 | SLS 驻留"evaluated at the SLS design azimuth resolution rather than the requested task resolution (conservative for coarser demands)" | `duration.py::kim_checker_scene_sls(psi, rho_req_m=...)`，票 49 后按订单解析 |
| 7 | `main.tex:150` §3.4 | "the sliding factor k is likewise a system parameter" | `duration.py::task_sls_factor(rho_req, psi_sel, geo)`，逐任务 |
| 8 | `main.tex:162` §3.4 | "The bi-objective problem ... (-f1*, -f_q)" | `nsga2.py` 只最小化 `-f1*` |
| 9 | `main.tex:168` §4.1 | "dual-objective evolutionary search" | 同上 |
| 10 | `main.tex:256` §6 | "no unit promotes（max spread 3.9722 dB）"、"R1C ... its front is a pure quality trade-off surface" | L8 全部 260 单元 `promotion.decision = vacuous_single_objective`；front 是 f1 唯一的 tie set |
| 11 | `main.tex:284/289/298/302` | §6.4 "The second objective is fully explained by the mode library"、per-mode 常数、Fig. 3 图注、per-family decomposition | 见 §2.1 |
| 12 | `main.tex:328/330` | §7 caveats："keeps the second objective comparable across windows"、"the second objective trades that change against the served set" | 同上 |
| 13 | `main.tex:29/256` | 90 units、3 budget tiers、t=24.78、8.74/10.91 dB | L8 为 270 单元（3 族 × 9 s × 10 seeds）；旧数字来自 L6/v3 |

另有一处仍然正确、票 50 可保留：`main.tex:146` "the evaluator performs no AASR recheck of its own"。

### 2.3 B1：扫描轴的反事实语义错误（最重要的理论发现）

票 48 的扫描设计是"固定任务总体，仅缩放 `rho_req_m`"。`run_pilot.py:81-88` 与 `run_matrix.py --s-factor` 确实只缩放订单，**不重新路由模式**。而论文 §3.4（`main.tex:150`）明确：模式由"（所需分辨率，场景尺寸）经 coarsest-sufficient 库表"映射得到。

两者冲突。实测：

```
R1C（20 任务，全部 STR，rho 2.522–2.961 m）
  s=0.8 → 20/20 任务 rho=2.018–2.369 < 2.4669（STR 地板）
          但 manifest 中 mode 仍为 STR → resolution_clip 返回空集
          → 10/10 个种子 exit 11（无可服务实例），覆盖 0
  若按论文路由规则重路由：s=0.8 时 20/20 任务应变为 SLS，而非 STR
```

也就是说，**R1C 在 s=0.8 的 0 覆盖不是"分辨率需求收紧导致调度能力下降"，而是一个论文模型不允许存在的配置被强制求解的结果**。

同样的机制在 R3H 上可以定量验证：

| s | 族 | STR 任务越界数 | 越界优先级份额 | 实测覆盖 | 相对 s=1.0 的跌幅 |
|---|---|---|---|---|---|
| 0.8 | R3H | 54/54 | 0.5268 | 0.4827 | 0.4658 |
| 0.9 | R3H | 25/54 | 0.2551 | 0.6884 | 0.2601 |
| 0.8 | R1C | 20/20 | 1.0000 | 0.0000 | 1.0000 |
| 0.9 | R1C | 10/20 | 0.4701 | 0.5398 | 0.4602 |

跌幅与"被强制变为不可服务的 STR 优先级份额"在 0.005–0.02 内吻合（差额来自基线本身未服务部分与锚点重排）。R1C 的 0.9 点尤其干净：纯 STR 族，份额 0.4701 对跌幅 0.4602，误差 1.0pp。这证明紧臂的绝大部分响应是 STR 地板的**阶跃**，不是驻留增长带来的连续权衡。

R2F 则给出反向证据：该族 46 个任务全部是 SLS/SPT（16 + 30），**没有任何 STR 任务**，因此 s=0.8 与 s=1.0 的中位覆盖逐位相同（均为 `0.9764210609534351`，`==` 比较为 True）。这不是"数据异常"，而是"没有 STR 通道"的构造性必然，也直接解释了 C3 判据在 R2F 失败。

**结论**：当前 L8 曲线的紧臂（s<1）测的是"冻结模式下的 STR 可行域阶跃"，不是标题所暗示的"覆盖率 vs 分辨率要求"的一般权衡。二者都可以成立，但必须二选一并写清楚：

- 方案 A（重跑）：每个 s 重新生成 manifest（重新路由模式），注册为新谱系 L9。R1C@0.8 会变成全 SLS，曲线形状可能完全不同。
- 方案 B（重述）：明确声明"模式映射冻结在 s=1.0 的订单上，s 只作为同一订单的分辨率敏感性旋钮"，并把结论限定为"低于 STR 地板时该模式不可服务"，同时说明 SLS/SPT 任务在 s<1 的响应来自驻留增长（R2F 近似平坦即为证据）。

无论选哪个，票 50 的"外生扫描轴"都必须带上这个语义限定，否则审稿人只要问一句"需求变了为什么模式没变"就会击穿。

### 2.4 其他理论风险

- **质量指标不是标定物理量**：`main.tex:136` 已自曝"no calibrated radiometric quantity enters"。票 50 把它降为读数是对的；但"质量兑现率"若仍用 `m^-2` 绝对量，必须保留不可跨族比较的声明。
- **SLS 适用域**：`A_task in (0,1)` 等价于 `rho_req < D/(2 cos psi) = 2.4669/cos psi`。生成期分布（R2F 0.32–0.60，R3H 0.31–2.99）不触发上边界，但票 50 若扩展参数范围需重新检查。
- **AASR 准入仍自洽（已核验，非缺陷）**：`aasr.py` 中 SLS 的 `a_res·B_D = 2 V_s cos psi / D` 与 `rho_zero` 无关；SPT 的 AASR 与 `beta_span` 无关。生成期 11 点准入在票 49 后仍与任务律一致，无需改。
- **STR 地板刀刃**：`resolution_clip` 在 `rho_req == 2.4669` 时 `psi_max = 0`，clip 成零宽区间。生成分布 [2.5,3.0] 不触发；但 s 扫描会经过该值（s=0.9 时区间 [2.25,2.70] 跨越 2.4669），实测未出现恰好相等的任务，属测度零事件。建议在论文中一句话披露"恰等于地板时不可调度"。

---

## 3. 算法轴

### 3.1 单目标 NSGA-II 已退化为精英 GA

`nsga2.py:66-74` 的 docstring 已如实写明：`n_obj=1` 时 NSGA-II 的非支配排序退化为按单目标排序。这不是隐藏缺陷，但票 50 不能再把它写成"多目标进化搜索"。

### 3.2 前沿是 f1 唯一的 tie set（260/260）

遍历 260 个 pilot artifact：

- **unique f1 数 = 1 的单元：260/260**。单元内所有前沿成员覆盖率完全相同；
- front 大小分布：40（233 个）、2（11）、1（9）、5（2）、26/4/12/17/10（各 1）；
- 237/260 个单元的前沿含 ≥2 个不同 `f_q`。

也就是说，所谓"前沿"是"达到同一最大覆盖率的若干等价排程"，`f_q` 在其上自由浮动，但**从未受到选择压力**（`nsga2.py:92` 只把 `-f1*` 写入 F）。因此：

- 任何"前沿平均 f_q"都是 tie-break 噪声，不是优化结果；
- `main.tex:256` 的"R1C front is a pure quality trade-off surface"在 L8 中为假；
- 票 50 若报告"质量兑现率"，必须锚定**单一确定性方案**（锚点）或注册显式 tie-break，不能对 tie set 取均值。

**连带推翻旧主结果**：`main.tex:248` 的核心统计量 `dq_all` 定义为"同一前沿上 max f_q 减锚点 f_q"，报告 mean 66.872、`t=24.78`。在 L8 中前沿是覆盖相同的 tie set，`f_q` 从未进入目标函数，因此该差值只是 tie set 内 `f_q` 的任意极差；其非负性与大 t 值都是"max-minus-first"构造的产物，不是搜索带来的质量增益。`main.tex:306` 自己也承认"coverage-maximal front member ties the anchor's served fraction exactly in 90/90 units"——覆盖维度早已打平，旧世界的可解释性完全依赖"质量是第二目标"这一前提。**该统计量不能迁移到单目标世界，也不能仅作为"旧世界数字"保留在新论文中。**


### 3.3 锚点在处理族 180/180 已最优

| 族 | 单元数 | 搜索严格改进锚点的单元 | 最大改进 |
|---|---|---|---|
| R1C | 80（s=0.8 无 artifact） | 2 | +0.0463（s=1.0，seed 100/105） |
| R2F | 90 | 0 | 0 |
| R3H | 90 | 0 | 0 |

即：治疗族（R2F/R3H）的 180 个单元里，进化搜索**一次都没有超过贪心锚点**。260 个单元 × 2400 次评估 ≈ 62.4 万次评估，治疗族增益为 0。

这不是"实验失败"，而是一个可发表的证伪结果：在"分辨率硬约束 + 单目标覆盖"的世界里，贪心锚点已逼近该编码下的最优，搜索只提供局部最优性证据。票 50 的贡献叙事必须据此重写（见 §3.5），否则"收敛验证"会被审稿人视为把无增益包装成贡献。

### 3.4 `search_only_max_f1_star` 字段语义缺陷

`nsga2.py:315-317`：

```
others = [r["f1_star"] for r in front if r["f1_star"] < anchor_f1 - 1e-9]
search_only = max(others) if others else None
```

单目标下 rank-0 成员的 f1 全相同，故该列表恒空、字段恒 None。更严重的是：在两个搜索**确实赢过锚点**的单元（R1C s=1.0 seed 100/105）中，因为它只收集"严格低于锚点"的成员，同样返回 None。也就是说，该字段在"搜索赢"和"搜索平"两种情况下都无法区分，**不能作为"搜索无增益"的证据**。

正确做法：记录 `front_max_f1_star`、`anchor_on_front`（布尔）、`gain_over_anchor = front_max - anchor`。本报告的 258/260 结论即用该口径独立复算。

### 3.5 贡献重写建议

按现有证据，三条贡献应改为：

1. **物理到调度器的闭合链**：逐任务模式参数律（SLS 的 `A_task`、SPT 的 `beta_task`）与交付恒等式（往返 ≤1e-12），使"订单分辨率"直接决定驻留与可行域。
2. **分辨率作为预编译硬约束**：`resolution_clip` 在窗枚举阶段收缩可行域，覆盖率代价可逐族量化；并披露 STR 地板的阶跃性质。
3. **需求敏感性实验的机制分解**：覆盖率随订单收紧的响应由"STR 可行域阶跃"与"SLS/SPT 驻留增长"两部分构成；报告 R2F 的 C1/C3 证伪，并给出优先级份额预测与实测跌幅的定量吻合。

同时明确写入：**锚点已最优、搜索无覆盖增益**；NSGA-II 仅作为局部最优性检查，不作为贡献。

---

## 4. 代码轴

### 4.1 静默失效面

| # | 位置 | 问题 | 当前影响 |
|---|---|---|---|
| 1 | `run_pilot.py:81-88` / `run_matrix.py --s-factor` | 只缩放 `rho_req_m`，不按新的（分辨率，场景）重路由模式 | B1：扫描轴与路由规则冲突 |
| 2 | `scripts/build_sweep_results.py:62-64` | 聚合 v5 时仍从 `V4/scenarios` 读 manifest | 本次核对 v4/v5 的 80 个 scenario sha256 全同，数字未受影响；但路径硬编码，v5 若改场景即静默用错 |
| 3 | `sss_core/quality.py` | `rho_a` 用库常数，未接交付分辨率 | B2，直接影响论文读数 |
| 4 | `sss_core/nsga2.py:315` | `search_only` 语义倒置/空转 | 见 §3.4 |
| 5 | `sss_core/nsga2.py:312` | 每单元仍计算并写入 `promotion_spread_db`，但 decision 恒 void | 旧图/旧文可能误引 spread（3.9722 dB 即来自旧世界） |
| 6 | `sss_core/evaluator.py:80,446` | `EMPTY_SELECTION_FQ_PLACEHOLDER = 1.0` | 空选择在 `n_obj=1` 下进不了 rank-0，低风险；但 1.0 对 STR 并非"最差"（0.81 < 1.0），注释与语义不符 |
| 7 | `sss_core/windows.py::resolution_clip` | `rho_req == 2.4669` 时零宽 | 测度零，需披露 |
| 8 | `sss_core/aasr.py::AASRGrid` | 已降级 verify-only，无生产消费者 | 死代码，票 50 可退役或保留为校验 |
| 9 | `scripts/build_sweep_results.py` | R2F 判据失败 → exit 1 | 如实非零；但流水线若忽略 rc 会把红判成绿，需在票 50 明确"红即结果" |

### 4.2 红闸覆盖缺口（实测）

`check_red_lines.py` 运行结果：**0 violation / 1070 files**。但 `WRITING_BANS`（`check_red_lines.py:636-803`）中没有任何一条覆盖：

- "second objective" / "second-class objective" / "bi-objective" / "dual-objective" / "two objectives" / "independent objective"；
- 因此 `main.tex` 与 `full.md` 中 11 处双目标表述全部放行。

这意味着**票 50 改写完成后，闸也无法防止双目标叙事回流**。必须补禁语，且要处理三个连带点：

1. `_NOPRIOR_LEGAL_RX`（`check_red_lines.py:284-290`）唯一的英文合法句就是 `main.tex:89` 的"independent objective dimension"句。票 50 删除该句后，这条豁免正则应同步退役，否则未来草稿可以复用该句式通过闸。
2. W9 的放行词 `degenerate by construction`（`:770`）在单目标下语义反转：覆盖率不再是"构造性打平"，而是唯一目标。该豁免必须重写，否则既放行错误表述，又禁止正确表述。
3. W13 只要求 `f_q` 带 caliber 标签（`:800-802`），没有要求新主结果带"窗选择口径/兑现率定义"。票 50 应扩展为：质量读数必须标注"库零斜视口径"或"交付口径"，以及"锚点方案"或"tie-set 均值"。

此外，`analysis_prereg_v2.json` 的 R5 只锚定 v2 主实验族，对 L7/L8 sweep 零约束；票 50 的新主结果目前没有对应的预注册条款。

### 4.3 测试状态与元问题

- paper2 域套件：**449 passed, 1 skipped**（exit 0，1373.54 s）。票 49 新增测试后仍全绿。
- 元问题：套件包含 `test_writing_red_lines.py`、`test_claim_traces.py`、`test_verify_gate.py`，但**全部通过**的情况下，论文仍整体停留在双目标世界。这说明现有闸校准的是"旧世界内部自洽"，而不是"论文与当前代码/数据同世界"。票 50 需要一个跨层断言：正文引用的数据谱系标签（L6/L8）必须与生成该数字的 artifact 目录一致。

---

## 5. 数据轴

### 5.1 L8 曲线逐位复算

`experiments/v5_results/sweep_results.json`，中位覆盖率：

| s | R1C | R2F | R3H |
|---|---|---|---|
| 0.8 | 0.0000（10/10 exit 11） | 0.9764 | 0.4827 |
| 0.9 | 0.5398 | 0.9737 | 0.6884 |
| 1.0 | 1.0000 | 0.9764 | 0.9485 |
| 1.1 | 1.0000 | 0.9764 | 0.9766 |
| 1.2 | 1.0000 | 0.9960 | 0.9812 |
| 1.3 | 1.0000 | 0.9960 | 0.9882 |
| 1.4 | 1.0000 | 0.9924 | 0.9882 |
| 1.5 | 1.0000 | 0.9924 | 0.9900 |
| 2.0 | 1.0000 | 1.0000 | 0.9900 |

判据（票 48 预注册）：

| 族 | C1 单调 | C2 饱和 | C3 紧臂下跌 |
|---|---|---|---|
| R1C | 通过 | 通过 | 通过 |
| R2F | **失败**（0.8→0.9 −0.27pp；1.3→1.4 −0.36pp） | 通过 | **失败**（0.8 与 1.0 逐位相同） |
| R3H | 通过 | 通过 | 通过 |

质量兑现率中位数（`f_q_fulfillment_ratio_median`）：

| s | R1C | R2F | R3H |
|---|---|---|---|
| 0.8 | —（无 artifact） | 0.7852 | 0.7921 |
| 0.9 | 0.6172 | 0.7791 | 0.7276 |
| 1.0 | 0.6580 | 0.7764 | 0.7447 |
| 1.2 | 0.7273 | 0.7855 | 0.7875 |
| 1.5 | 0.7511 | 0.7720 | 0.7888 |
| 2.0 | 0.7511 | 0.7951 | 0.7954 |

读数整体在 0.62–0.80，非单调。它不是"搜索找到的质量"，而是**锚点选窗相对最优可达窗的损失**（分母为每任务全窗零斜视最大值）。票 50 必须把它定义为"锚点方案的窗选择兑现率"，不能写成"优化后的质量达成"。

### 5.2 L7 → L8 的差异

| 族 | s=0.8 | s=0.9 | s=1.0 | s=2.0 |
|---|---|---|---|---|
| R1C L7/L8 | 0 / 0 | 0.5398 / 0.5398 | 1 / 1 | 1 / 1 |
| R2F L7/L8 | 0.4455 / 0.9764 | 0.6830 / 0.9737 | 0.9603 / 0.9764 | 0.9764 / 1.0000 |
| R3H L7/L8 | 0.2297 / 0.4827 | 0.5448 / 0.6884 | 0.9266 / 0.9485 | 0.9819 / 0.9900 |

R1C 完全不变（全 STR，与票 49 无关）；R2F/R3H 全点抬升，符合票 49 "SLS/SPT 按订单交付、不再被库分辨率窄化"的预期。**L8 取代 L7 是成立的**，旧 L7 数字不得再引用。

### 5.3 exit 11 与普查

- 270 个单元 = 260 artifacts + 10 个 exit 11（R1C s=0.8，10 个种子全部无可服务实例）；
- 聚合器 census 守卫要求 `artifacts + exit11 == 10`，实测全部满足；无孤儿 artifact；
- 所有 artifact 的 `s_factor` 与目录一致；`provenance` 检查有效。

### 5.4 旧世界验证链清单（票 50 必须重指或退役）

| 脚本/图 | 钉住的世界 | 后果 |
|---|---|---|
| `verify_paper_numbers.py` | `v3_results` + 3 个 budget tier；期望 `decisions == {no_promotion}` | L8 的 decision 恒为 `vacuous_single_objective`，脚本对 L8 必 FAIL；它验证的是旧论文 |
| `verify_v3_verdicts.py` | `v3_results` | 同上 |
| `verify_prereg_v2.py` | `experiments/results/matrix`（v1/v2） | 与 L8 无交集 |
| `recompute_r_fam.py` | `v3_results/scenarios` | 同上 |
| `check_coverage_parity.py` | `v3_results` | 同上 |
| `plot_fig5/6/7` | `v3_results` | 图 5/6/7 直接编码双目标世界 |
| `plot_fig3` | v3 口径（v2 显式排除） | f_q 常数叙事 |
| `run_verify.py` snapshot | 旧 pilot | 对 L8 必 FAIL |

结论：7 张图中 Fig. 1/2（几何、调度回路）可保留，**Fig. 3–7 必须重绘或退役**；否则论文会出现"新数字 + 旧图"的混合世界。

---

## 6. 风险登记表

### 阻断（票 50 改写前必须闭环）

| ID | 风险 | 触发条件 | 验收判据 |
|---|---|---|---|
| B1 | 扫描轴冻结模式，紧臂是构造产物 | 论文声称"coverage vs resolution requirement" | 明确选择 A（重跑、新谱系）或 B（重述为冻结模式敏感性），并在方法与图注中写明 |
| B2 | f_q 与交付律冲突 | 论文任何 f_q 数字或模式对比 | `f_Q_deliv` 实现并量化差异，或全文改标"库零斜视口径"且删除模式对比 |
| B3 | 正文双目标 vs 代码单目标 | 红闸 0 violation | 新增双目标禁语 + 改写正文 + 双稿源同步 |
| B4 | 验证链/图钉旧世界 | `verify_paper_numbers.py` 对 L8 必 FAIL | 全部重指 L8 或显式退役，并在报告中列出 |
| B5 | 预注册 v2 失效 | 论文仍以 v2 为设计依据 | append-only amendment，逐项处置 `dq_all`/P1/P2/P3/promotion；其中 `dq_all` 不是"待重算"，而是结构性无效（见 §3.2） |

### 非阻断但高优先

| ID | 风险 | 建议 |
|---|---|---|
| N1 | R2F C1/C3 失败 | 作为证伪结果如实报告，附优先级份额预测表（§2.3） |
| N2 | `search_only` 字段空转 | 改为 `gain_over_anchor` + `anchor_on_front`，或删除 |
| N3 | `fulfillment_ratio` 硬编码 V4 | 改为使用聚合目录参数；当前数字因 80/80 sha256 相同而有效 |
| N4 | tie-set 读数 | 质量读数锚定锚点方案，或注册 tie-break |
| N5 | 双稿源 | `main.tex` 与 `full.md`/`sections` 同步改写，闸需 `--must-include` 两份 |
| N6 | Fig. 3–7 | 退役或重绘；新增"覆盖率 vs s + 机制分解"图 |
| N7 | promotion spread 仍写入 artifact | 标记为 void 描述列，禁止引用 |
| N8 | `EMPTY_SELECTION_FQ_PLACEHOLDER=1.0` 注释与语义不符 | 改为 `None`/`NaN` 或修正注释 |

---

## 7. 改进建议（按执行顺序）

1. **先做 B1 决策（票 50 第一件事）**：在票 50 正文改写前，由用户拍板 A/B。建议 A（重跑）若时间允许：它是唯一能让"覆盖率 vs 分辨率要求"成为真命题的路径；若选 B，则论文标题、摘要、图注都必须限定为"固定模式映射下的订单敏感性"。
2. **实现 `f_Q_deliv`（B2）**：`quality.py` 增加交付口径（`rho_ach = rho_req` for SLS/SPT，`rho_req` 不适用于 STR），保留库口径作为对照列；在 L8 artifact 上重算兑现率并记录两者差值。
3. **补红闸禁语（B3）**：在 `WRITING_BANS` 增加双目标词组；退役 `_NOPRIOR_LEGAL_RX`；重写 W9 豁免；扩展 W13 口径标签。
4. **重指验证链（B4）**：`verify_paper_numbers.py` 改为按谱系参数化（`--results v5_results`），或新建 L8 专用验证器；旧脚本标记 `LEGACY/L6` 并禁止在论文中引用其输出。
5. **预注册 amendment（B5）**：append-only 增加 L8 块，注册新主结果（覆盖率 vs s、C1/C2/C3 的实际结果含 R2F 失败、兑现率定义），并显式 vacate `dq_all`/P1/P2/P3/promotion。
6. **报告 R2F 证伪（N1）**：正文用一段 + 一张表写清"跌幅 ≈ STR 优先级份额"，把 C1/C3 失败转化为机制证据。
7. **统一读数口径（N2/N4/N7）**：锚点方案为唯一报告对象；tie set 只用于说明"覆盖最优解不唯一"。
8. **图件重制（N6）**：Fig. 3–7 退役；新图建议为三族覆盖率 vs s，叠加"STR 越界份额"虚线作为机制对照。

---

## 8. 附：关键复算命令

```powershell
# L8 曲线与判据
python -c "import json;d=json.load(open(r'papers/sliding-spotlight-scheduling/experiments/v5_results/sweep_results.json'));print(d['checks'])"

# 前沿结构 / 锚点最优性 / promotion 状态
python -c "import json,glob;print([(a['front_size'],len({r['f1_star'] for r in a['front']}),a['promotion']['decision']) for f in glob.glob(r'papers/sliding-spotlight-scheduling/experiments/v5_results/sweep/s*/pilot_*.json')[:5] for a in [json.load(open(f))]])"

# 模式构成与 STR 地板越界份额
python -c "import json,collections;m=json.load(open(r'papers/sliding-spotlight-scheduling/experiments/v5_results/scenarios/R3H_seed300.json'));print(collections.Counter(t['mode'] for t in m['tasks']))"

# 红闸
python papers/sliding-spotlight-scheduling/scripts/check_red_lines.py

# 双面回归
python -m pytest papers/sliding-spotlight-scheduling/tests -q
```

---

## 9. 审查边界

- 未运行完整 L8 重跑；所有读数来自已落盘 artifact，未验证 launcher 的端到端可重复性（仅核对了 `_progress.json` 与谱系记录）。
- 未逐条重算 `verify_paper_numbers.py` 的 100+ 检查；结论基于其数据源常量（`V3`、`TIERS`）与 L8 的 decision 字段。
- 未评估论文的文献覆盖与 novelty 表述；票 50 的引用复核需另行执行。
- 未修改任何文件；本报告为唯一新增产物。
