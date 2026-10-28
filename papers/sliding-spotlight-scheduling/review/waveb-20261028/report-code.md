# seat=code — Wave B 代码一致性审查报告

审查对象：`papers/sliding-spotlight-scheduling/paper/main.tex`（当前 HEAD 工作树）
对照实现：`papers/sliding-spotlight-scheduling/sss_core/`（duration / modes / geometry / quality / aasr / evaluator / scenarios / predicates / maneuver / anchor / nsga2 / windows）+ `experiments/check_per_node_serviceability.py`
验证方式：只读调用真实库（解释器 `D:\Program Files\Python\python.exe`，Python 3.14.4），探针脚本全部写在仓库外（`C:/Users/33151/AppData/Local/Temp/opencode/`）；除本报告外未写入任何仓库文件。

## 0. 红线复述

1. **只读**：禁改仓库任何文件；唯一可写 = 本报告文件。
2. **可证伪**：每条发现带 file:line（或节/页）+ 原文引句 + 为什么是问题 + 建议修法；无引句的发现作废。
3. **严重度**：P0 = 事实错/数字错/物理错/自相矛盾（必须修）；P1 = 论证缺口/口径漂移/误导读法（应修）；P2 = 表述与结构改进（可选）。
4. **不确定写 QUESTION**，并说明需要什么才能裁定；禁止把口味当缺陷。
5. 审的是当前 HEAD 工作树状态的 `main.tex`（含本轮新增 Fig 2/4/6/7/8）。

## 1. 发现

### P0

#### P0-1（对应第⑤项）C3 的归一化参考写的是库常量，实现用的是逐任务/逐窗口的任务律参考

**位置**：`paper/main.tex:206`（§3.4，C3 条目）↔ `paper/main.tex:211`（同节末段）↔ `sss_core/predicates.py:141-143, 269`；`sss_core/evaluator.py:524-527`

**原文引句**

- C3（main.tex:206）：
  > "Per-task duty is normalised against the mode-library envelope reference $T_{\mathrm{env,max}}=10.5830$~s (the largest feasible scene dwell at the envelope-edge squint, attained by SPT; a planar-closure reading at the $45^{\circ}$ edge, inheriting the Earth-curvature extrapolation of Section~\ref{sec:geometry}) with mode weights STR/SLS/SPT $=1.0/1.15/1.3$; the normalisation denominator is the largest weight times the envelope reference, $1.3\,T_{\mathrm{env,max}}$ (the C4 reference below omits this weight factor)."
- §3.4（main.tex:211）：
  > "the normalisation reference was redefined on 2026-10-20, on the day the sweep ran, from the mode-library constant dwell to the per-task envelope-maximum task-law dwell, after the task-law dwells were measured to exceed the library reference by up to $1.2008\times$ on the 50-task family (theoretical worst $1.274\times$) and had produced false violations"
- 代码（predicates.py:141-143）：
  > `if rho_req_m is None:` / `return max(_scene_durations(lib, r0_m).values())` / `return max(_task_envelope_durations(lib, r0_m, rho_req_m).values())`
- 代码（predicates.py:269）：
  > `ref = max(C3_WEIGHTS.values()) * _t_env_max(lib, r0_m, rho_req_m)`
- 代码（evaluator.py:524-527）：
  > `if not c3_ok(` / `plan.mode, self._dwell(i, starts[i]), self.lib,` / `r0_m=w.r0_m, rho_req_m=plan.rho_req_m,` / `):`

**为什么是问题**

1. **数字不符。** 在 30 个已发布 R 族清单的 9,044 个 (task, window-`r0`) 对上，生产分母 `1.3·T_env,max(r0, ρ)` 的范围是 **2.0865–22.8050 s**（中位 10.1823）：R1C 2.087–3.069（中位 2.348）、R2F 8.501–22.805（中位 12.642）、R3H 2.087–22.438（中位 3.064）。论文写的 1.3×10.5830 = **13.7579 s** 只在 R2F 中段巧合成立；对全条带的 R1C，分母被高估 4.5–6.6×（13.7579/3.069 = 4.48，13.7579/2.087 = 6.59），生产里该族的归一化占空最高 0.769，按论文公式只有 0.172。
2. **自相矛盾（同一小节内）。** 紧接 C3 的末段用过去时登记了 2026-10-20 的改口径（库常量 → 逐任务任务律），C3 条目却仍用现在时把库常量写成"the normalisation denominator"。实现里还有一次更早的改口径（predicates.py:97-114，2026-10-03，r0 逐任务），C3 完全没写，只有 C4 的括注提了 "each measured window's own slant range"。
3. **按论文写的公式，参考自身就超过 1。** 取 `R2F_seed201` 的一个 SPT 任务（ρ = 0.304128537 m，其窗口 r0 = 1,018,690.37 m）：这一 caliber 的包络极大驻留（正是 C3 参考所指向的对象）是 17.5423 s。论文公式给 1.3×17.5423/13.7579 = **1.6576 > 1**，生产给 1.3×17.5423/(1.3×17.5423) = **1.000**。也就是说，论文打印的分母连它自己定义的"最大可行驻留"都归一化不到 1 以内，与同节 "their normalised values cannot exceed 1.0 there" 直接冲突——不是实现放松了约束，而是正文的参考值不是实现用的参考值。
4. **次要：即便作为库常量，"largest feasible scene dwell" 也不严格。** SPT 的起始域由 |ψ_sel|+β/2 ≤ 45° 界定：库 span（2.9603°）时为 43.52°，最细阶数（ρ=0.3 m）时为 42.98°（`duration.spt_start_squint_limit`；论文自己在 main.tex:150 写 "about $43^{\circ}$ at the finest order"）。43.52° 处的库驻留约 10.06 s；10.5830 s 是 45° 处的值——论文同句也承认它是 "a planar-closure reading at the $45^{\circ}$ edge" 外推读数。"feasible" 与 "extrapolated" 不能同时描述同一个数。

**建议修法**：把 C3 改成 C4 已经用的写法——分母 = 1.3·`T_env,max(r0, ρ)`，`T_env,max` 在**被测窗口的斜距 r0** 与**任务阶数 ρ** 上取各可用模式包络极大（STR 45°；SLS 26.9° 且 ρ_eff = ρ cos ψ；SPT 的 ψ\*(ρ)），并保留 10.5830 s 只作为"库口径/零阶锚点"的脚注；同时把 2026-10-03（r0）与 2026-10-20（ρ）两次改口径一并登记，或让 C3 直接指向 §3.4 而不复述常数。

### P1

#### P1-1（对应第④项）"raises a visible warning in the implementation" —— 生产路径把这条警告吞掉了

**位置**：`paper/main.tex:205`（§3.4，C2）↔ `sss_core/predicates.py:216-218`；`sss_core/maneuver.py:189-197`；`sss_core/anchor.py:408-417`

**原文引句**

- C2（main.tex:205）：
  > "Production evaluates $t_{\mathrm{man}}$ as a registered hybrid: the analytic model stands alone only where it reaches at least half of the measured calibration anchor ($1.84$~s, Kim scenario~1); below that trigger the per-transition maneuver bound falls back to the worst measured required maneuver time ($4.07$~s, pure maneuver, Kim scenario~2) --- a conservative substitution that raises a visible warning in the implementation."
- code（predicates.py:209-218）：
  > "is computed from the ticket-07 closure (fallback armed, warnings suppressed here -- the calibration warning is emitted at setup)"
  > `with warnings.catch_warnings():` / `warnings.simplefilter("ignore")` / `cal = calibrate_against_kim(lib, d_psi_rad, kim_rmt_s=CALIBRATION_KIM_RMT_S)`
- code（maneuver.py:190-197）：
  > `warnings.warn(` / `f"D5 maneuver model under-predicts Kim RMT "` / ... / `"at the C2 layer) -- not a silent degradation",`

**为什么是问题**：生产 C2 链的两处调用（`evaluator.py:497`、`anchor.py:92`）都走 `c2_transfer_requirement_s`，而它把 `calibrate_against_kim` 包在 `catch_warnings()/simplefilter("ignore")` 里。生产代码里唯一未被抑制的调用点是 `anchor.assert_fallback_active`（anchor.py:408-417），而它只被 `tests/test_anchor.py:249` 调用（grep `assert_fallback_active` 全仓 4 处：定义、测试导入、测试断言、测试清单）。也就是说：跑 sweep 时**没有任何警告浮出**；代码注释里 "emitted at setup" 在 runner 侧没有对应调用。论文把这条警告当作"保守替换可见、非静默降级"的凭据，审稿人若去查代码会落空。机制本身（1.84 / 0.5 / 4.07 / 2.0）与代码完全一致，所以只判 P1 而不是 P0。

**建议修法**：二选一——(a) 在 runner 的 setup 真正调用一次 `assert_fallback_active`（或等价的一次性 `warnings.warn`），让这句话为真；(b) 改写为"fallback 无条件武装；逐对校准警告在 C2 循环内被抑制以避免每次运行 1,577 条噪声，setup 断言记录该欠预测"。

#### P1-2（额外发现）§3.5(iii) "the data follow neither" —— 数据的模式分配恰好就是规则 (i) 在 s=1 上的输出

**位置**：`paper/main.tex:225` ↔ `sss_core/scenarios.py:252, 619`；`sss_core/aasr.py:178-189`

**原文引句**

- paper（main.tex:225）：
  > "(iii) The data of this paper follow neither of those at run time: they carry the grandfathered assignment described above."
- code（scenarios.py:619）：
  > `mode = route_mode(rho_req, lib)`
- code（aasr.py:178-189）：
  > "Coarsest-sufficient routing (coarse -> fine, first tier satisfying rho_ach <= rho_req). Footprint legality is a ticket-08 generation-time concern and intentionally NOT here (single-predicate layering, D9)."

**为什么是问题**：30 个 R 族清单共 1,685 个任务，`mode` 与 `route_mode(rho_req)` **逐一相同，0 处不符**。分配规则就是 (i)（按需求取最粗可用层、无场景尺寸测试），在 as-placed 需求上算一次后冻结。"at run time" 让字面为真，但这一段的存在目的正是"防止三条规则混淆"，现在读者反而无法知道分配由哪条规则产生，"grandfathered" 又暗示了第四种来历；而 §3.5(i) 也因此不是"另一条在用的规则"，而是数据实际用的那条。属口径漂移/误导读法（P1）。

**建议修法**：改为 "(iii) the data carry rule (i) evaluated once at the as-placed requirement and then frozen; neither rule is re-run as $s$ moves."

### P2

#### P2-1（对应第⑥项）"a uniform grid on τ samples wider windows more finely" 方向说反了

**位置**：`paper/main.tex:254` ↔ `sss_core/evaluator.py:123-142`

**原文引句**

- paper（main.tex:254）：
  > "A start fraction $\tau$ indexes position within the \emph{feasible measure} of a task's window union, not within wall-clock time: decoding is the measure projection of Fig.~\ref{fig:loop}. Because the projection is measure-normalised, a uniform grid on $\tau$ samples wider windows more finely --- the parameterisation carries an implicit weighting toward wider windows."
- code（evaluator.py:136-140）：
  > `s = tau * total` / `for j, ((lo, hi), w) in enumerate(zip(intervals, measures)):` / `if s < w or j == last:` / `return lo + min(s, w)`

**为什么是问题**：τ 均匀网格在任务窗口并集上的绝对时间间距是 M/n（M = 并集测度），并集越宽间距越大——即"更粗"而不是"更细"；宽度带来的是该窗口在 τ 轴上分到的**样本份额** ∝ 宽度。而且相对"在可行并集上按时间均匀采样"这一自然基线，测度投影并不产生额外偏置（两者都给 p(t) ∝ 1 over the union），所以 "implicit weighting" 相对什么基线成立没有说明。属表述层，无数值后果，故 P2。

**建议修法**：改为 "assigns a wider union a proportionally larger share of the $\tau$ range (absolute-time spacing $M/n$, i.e.\ coarser in time for wider unions)"；若仍要称 "bias"，需写明基线（QUESTION：这里的偏置是相对"按窗口计数均匀"还是相对"按墙钟时间均匀"？前者成立、后者不成立）。

#### P2-2（对应第⑩项）"manifest task-list order everywhere" 与实现、也与本文自己的图注不符

**位置**：`paper/main.tex:250` ↔ `sss_core/evaluator.py:478`；`paper/main.tex:240`

**原文引句**

- paper（main.tex:250）：
  > "The search runs under a fixed random seed per unit, single-threaded, with manifest task-list order everywhere (no set or dictionary iteration order may influence a run), so every unit is bit-reproducible."
- code（evaluator.py:475-478）：
  > `# C2/conflict chains iterate in START-TIME order (index order is NOT` / `# time order -- the anchor-seed cross-check of ticket 12 exposed this` / `# as spurious violations on time-inverted index pairs)` / `order = sorted(starts, key=lambda i: starts[i])`
- 图 3 注（main.tex:240）：
  > "Evaluation: tasks are sorted by start time (index order is not time order)"

**为什么是问题**：C2 链显式按开始时间重排，不是清单序；"everywhere" 为假，且与同文图注直接冲突。可复现性本身成立（`sorted` 确定、`np.random.default_rng(seed)`、pymoo 0.6.1.6 pin、`minimize(..., seed=seed)`、无无序集合进入浮点路径），所以只是表述过强，判 P2。

**建议修法**："... with manifest task-list order for every construction step and a deterministic start-time sort for the C2 chain ..."。

## 2. 已检查、零发现（逐条明说）

1. **①§3.2 闭式 ↔ `duration_scene_s`**：STR = `_tan_diff_s(ψ, θ_a, r0, vs) + W_a/vs`（duration.py:340-343）；SLS = `kim_checker_scene_sls`，任务律传 `ρ_eff = ρ cos ψ`（duration.py:349-360），`A_task` 经 `(R0+r0)=R0/(1−A)` 进分母；SPT = `_tan_diff_s(ψ, β_task)`（duration.py:361-367）。三处与正文描述一致。§3.2 的近似偏差数字也可复现：`experiments/v5_results/dwell_exact_check.json` 的 worst = +1.8715%（26.9°，ρ=0.3 m）、12°/ρ=0.5 m = +0.3103%，对应正文 "+1.87% / +0.31%"。
2. **②交付恒等式 raise 守卫**：`_check_sls_delivery` / `_check_spt_delivery` 默认 `tol=1e-12`（duration.py:229, 263），违反即 `ValueError`；`_dwell` 每次 `duration_scene_s(..., rho_req_m=...)` 都会跑（evaluator.py:462-469）；STR 收到非 None 的 ρ 直接 raise（"STR has no task-level mode parameter"）。与 C5 的 "10^-12 tolerance ... raises instead of being scored" 一致。
3. **③11 点 AASR 准入**：`for j in range(11): tt = lo + (hi-lo)*j/10`（scenarios.py:700-701），越域样本记 `+inf`（720），`max(aasr_vals) > AASR_THRESHOLD_DB` 即拒（721，阈值 −13.0 dB，aasr.py:104）；evaluator 无复检。§5.1 的台账句（main.tex:277）逐字对上：30 个 R 清单合计 `removals = {aasr: 0, footprint: 0, below_finest: 0, no_window: 15}`。
4. **④C2 混合机制**（除 P1-1 的警告句）：`CALIBRATION_KIM_RMT_S=1.84`、`FALLBACK_TRIGGER_RATIO=0.5`、`FALLBACK_MANEUVER_S=4.07`、`SETTLE_S=2.0`（predicates.py:86、maneuver.py:79-81）；pad 只乘 dwell（`padded_dwell = (1+0.25) * dur_i`，predicates.py:222）；`schedule_conflict` 用裸 dwell（predicates.py:343-347）。
5. **⑤代码侧自洽**：`_t_env_max` 对无 ρ/无 r0 的旧族 bit-identical，对有 ρ 的走 task-law，且有 ticket-17/49 的改口径记录；问题在论文陈述（P0-1），不在实现。
6. **⑥解码实现**：`decode_tau` 是并集测度游走，τ=1 落在最后一个 `hi`（`min(s, w)` + last clamp）；`decode_starts` 只用预编译的 `plan.intervals`。与正文 "union of feasible window intervals" 一致（除 P2-1 的密度句）。
7. **⑦25/25 逐节点服务性**：`experiments/check_per_node_serviceability.py` 用注册轨道重算，实跑 `VERDICT: GREEN`：`HEADLINE: 25/25 nodes carry >=1 in-band transit over 72 h`，`CENTRE node 12: 6 transits over 3.0 d = 2.00 transits/24h`（注册值 2.00），min tie margin 0.05 km。与 C1 及 §5.1 的构造时测量声明一致。
8. **⑧模式包络**：`SQUINT_ENVELOPE_DEG=45.0`、`SLS_MAX_SQUINT_DEG=26.9`（duration.py:82, 90）；`env_guard = env_rad * (1.0 - 0.01)`（scenarios.py:631）；`R_PASS_SPAN_S=120.0`（scenarios.py:120）；`mask_intervals` 两端各内缩一个网格步长（`inset = step`，windows.py:367；240 s / 240 = 1.0 s）。与 ±45°/±26.9°/1% 内缩/±120 s/≈1 s 全部一致。
9. **⑨PRF / N_r / b_q**：`PRF_PRODUCTION_HZ=3630.0`（scenarios.py:74）、`C4_RANGE_SAMPLES_NR=10_000`、`C4_BITS_PER_COMPONENT=3`（predicates.py:80-81），`c4_memory_bytes = prf*dur*Nr*3*2/8`（predicates.py:285）；C4 参考不含权重（predicates.py:307-310），与 "the C4 reference below omits this weight factor" 一致。
10. **⑩确定性机制**：manifest seed → `np.random.default_rng(seed)` 填初始种群、`minimize(..., seed=seed)`（nsga2.py:263-287）、pymoo 0.6.1.6 pin；无无序集合进入浮点路径（`sorted(set(...))` 只用于候选去重）；C2 按开始时间排序（确定性）。逐单元位级可复现成立（除 P2-2 的措辞）。

## 3. 对其他席盲区的一句提示

C3 这类"正文公式被同一节的披露段悄悄取消"的错误，单读 C3 条目（理论席会照它复算）或单读披露段（claims 席会当作已登记）都不暴露，只有把 §3.4 两段 + `predicates.py` 对齐才成立；反过来，§4.4 的"采样密度"直觉与 §4.3 的"清单序"措辞，code 席能测出方向，但改成什么口径需要 method/claims 席拍板。

VERDICT: 1/2/2
