# waveb 确认席报告（两轮修复落地确认 + 全文残渣扫）

- 审查对象：`papers/sliding-spotlight-scheduling/paper/main.tex`（当前 HEAD 工作树，499 行）；镜像 `paper/full.md`、`paper/sections/*.md`
- 复核范围：`eba51b9`（Fig 7 展开）+ `42f4d39`（Wave B+C，34 处修复，摘要 272→250 词）的落地结果
- 立场：**独立确认席**（fresh context），不重做前席论证，只验"改到位没有、改出问题没有"
- 只读声明：未修改仓库任何文件，未编译 LaTeX、未跑测试套件（避免向 `paper/` 写 aux 产物）；唯一写入 = 本报告
- 方法：逐条读对应段落原文（非 diff）；长行用逐行 dump 读全；数字回源到 `experiments/v5_results/`（`reading_ledger_l8.json` 390 条、`counterfactual_fd/counterfactual_summary.json`、`figure_data/fig8_counterfactual.json`、`sweep/sweep_results.json`）；镜像按句子级探针比对
- 严重度：P0 = 事实/数字/自相矛盾；P1 = 口径漂移、误导读法、必须修；P2 = 表述与结构

---

## 一、14 项验收清单：逐条结论

| # | 验收点 | 结论 | 落地证据（引句 / 位置） |
|---|---|---|---|
| 1 | 摘要 ≤250 词 + 六项必备内容 | ✅ ok | 空白切分 244 token（连字符区间拆开计 247），六项齐：失败测量（"a median 27--42\% of pairs (per-seed 17--50\%)"）、修复后代价（"land 7--30 points below"）、内生机理（"the mode parameters follow the required resolution"）、三族九点栅格（"Three scenario families sweep a frozen nine-point requirement grid"）、地板归属（"stripmap floor accounting for 20.0 and 44.8 of those points"）、反向恢复（"Loosening recovers 4.15 and 2.36 points"）。`main.tex:29` |
| 2 | C3 逐任务包络归一 + 10.5830 书库锚 | ✅ ok | "Per-task duty is normalised against the per-task envelope reference --- the largest task-law scene dwell admissible for the task's own order at the measured window's slant range, over the modes that can serve it (library-calibre anchor of this reference: $T_{\mathrm{env,max}}=10.5830$~s at the $45^{\circ}$ edge, attained by SPT ...)"；`13.7579` 全文 0 命中，旧口径只以历史对照形式出现。`main.tex:206` |
| 3 | C5 的 STR 支 `(D/2)/cosψ` + arccos clip + 空集 | ✅ ok | "its delivered resolution is the squint-dependent floor value $(D/2)/\cos\bar\psi$ --- at or finer than the requirement --- so its admissible start domain is clipped to $\lvert\bar\psi\rvert\le\arccos((D/2)/\rho_{\mathrm{req}})$, a band that tightens continuously ... and is empty for any requirement [below the floor]"。与 `sss_core/windows.py:resolution_clip` 一致（ratio>1 → 空集；ψ_max=min(acos(ratio), envelope)）。`main.tex:208` |
| 4 | retention 用 stripmap-clip 定义 + R1C 51.14% | ✅ ok | "On the STR-clip-only convention --- retention is the fraction of the tie-set feasible measure that remains feasible after the stripmap clip (the clip: ... $\lvert\bar\psi\rvert\le\arccos((D/2)/\rho_{\mathrm{req}})$ ...; numerator: ... after the clip, denominator: ... before it), evaluated at the as-placed point ... retention reads 51.14\% for the control family"。`ledger[224]=0.5114`。`main.tex:400` |
| 5 | C5 inventory 句写成"两式"（identity / clip） | ✅ ok | "C5 is a raise-guarded identity for the two task-law modes and a start-domain clip for STR, rather than a scored constraint; the inventory above is the registered model, not a claim that five mechanisms bind."`main.tex:211` |
| 6 | 地板归属 bound-to-bound 25.16/49.93 + 净 20.01/44.78，5.15 有出处 | ✅ ok | "bound-to-bound, the floor effect is 25.16 points to $s=0.9$ and 49.93 to $s=0.8$ (the drop of the floor-exclusion bound from its trivial 1.000 at $s\ge1.0$); net of the as-placed point's own 5.15-point shortfall against that trivial bound (Section~\ref{sec:asplaced}), this reads as 20.01 of the observed 26.01-point drop to $s=0.9$ and 44.78 of the 46.58-point [drop]"。算术自洽：1−0.7484=25.16、1−0.5007=49.93、25.16−5.15=20.01、49.93−5.15=44.78、1−0.9485=5.15；且 `verify_paper_numbers_l8.py` 对 0.748/0.501 有界守卫。`main.tex:307` |
| 7 | 配对落差 25.6/42.1/47.0 + 区间 + 6/10 天花板 | ✅ ok | "these read 25.6 (per-seed 16.1--32.8), 42.1 (26.8--52.9; six of the control's ten seeds already sit at its 1.0 ceiling at the as-placed point, which widens the median-of-medians difference) and 47.0 (38.0--54.1)"。`ledger[155..157]` = 25.5863 / 46.9807 / 42.0696，note 逐条带 per-seed range 与 "6/10 seeds sit at the 1.0 ceiling"。`main.tex:348` |
| 8 | S1/S3 容差归属 + s=0.8 中位数相等 | ✅ ok | "the tolerance of the refined reading belongs to the tight arm (S3) only --- S1 is evaluated on the raw medians as frozen ..."；"the median at $s=0.8$ equals the as-placed median at the displayed precision"；"under the convention-v5 model the same family reads 0.9764 at $s=0.8$, equal to its own as-placed value at the displayed precision --- not below it --- so the tight arm no longer falls at all"。三处（引句、Table 3 `R2F … not met`、lead 句 "Two of the three frozen criteria fail"）互相一致。`main.tex:356,358` |
| 9 | double-digit 分层 | ✅ ok | "the measured consequence ... is at least 7 points under every rule tested on the dense families, and double-digit under every rule on the 100-task family"。与 repair 臂 30.44/30.11/25.33（100-task）对得上。`main.tex:422` |
| 10 | Shi et al. 姓氏修正 | ✅ ok | `refs.bib` `xin2024sar` 作者字段 `{{Shi}, Xin}` → 正文 "Shi et al." 正确（原 `Xin` 为名） |
| 11 | 保守臂 28.3/55.5 + 结论中不并入 7--30 区间 | ⚠️ 数值 ok，精密度有残留（见 P2-1） | 正文 "serves a median 28.3 and 55.5 points less ... (per-seed ranges 15.15--33.46 and 51.98--69.10)"；结论 "the conservative pre-shrunk arm costs 28.3 and 55.5 points"，且与 "land 7--30 points short" 分句并列、未混入该区间。`fig8_counterfactual.json` 收据值 = 28.3 / 55.52（R2F / R3H） |
| 12 | 第六条 scope statement + 无外部基线 | ❌ 内容到位、**计数未更新** | 第六句与 "And no scheduler from the published literature is run on this scenario set: ... the construction and counterfactual arms are its only baselines." 均已落地（`main.tex:447`），但同段首句仍是 "Five scope statements are registered before anything is claimed."，其后枚举 First…**Sixth** → 见 P1-1 |
| 13 | τ 密度方向 / a_res 拆分 / ρ_ach 反演 / SLS 闭式 / fixture 校验 / AASR a_res≡A / survivor set / 0.07% / 1.2008 注记 | ✅ ok | ①τ："a uniform grid on $\tau$ gives each window a share of the samples proportional to its width --- an implicit weighting toward wider windows relative to a per-window-uniform baseline"（方向正确：**偏向更宽窗口**，且显式与 wall-clock uniform 区分）`main.tex:254`；②"$a_{\mathrm{res}}=1-\frac{K_c}{K_a}\equiv A$"、"the $\cos^3$ factors cancel at beam-centre crossing, so the compression factor $a_{\mathrm{res}}\equiv A$ [squint-invariant]"`main.tex:146,148`；③反演："The C5 parameter laws are its inverse: setting $\rho_{a,\mathrm{ach}}=\rho_{\mathrm{req}}$ ... solves to $A_{\mathrm{task}}=2\rho_{\mathrm{req}}\cos\bar\psi/D$"`main.tex:~192`；④SLS 闭式："A planar closed form ... $T_{\mathrm{SLS}}=(R_0\theta_a+W_a)/(A\,v_s)\cdot\sec^2\bar\psi$ ... survives as the test-time oracle"（+0.4185% @12°，+2.1% @cap，+5.3% @45°）；⑤fixture："$\theta_a/A=\lambda/(2\rho_a)$ holds at the library design point ... residual $3.5\times10^{-18}$"`main.tex:170`；⑥AASR/0.07%："the ratio is at most one (to within the 0.07\% squint variation of the spotlight gain)"`main.tex:186`；⑦survivor set = 地板排除界内的逐任务可服子集："every non-stripmap task servable, each stripmap task servable only if its scaled requirement still reaches the $2.4669$~m floor"`main.tex:307`；⑧"measured (dated design record) to exceed the library reference by up to $1.2008\times$ on the 50-task family (theoretical worst $1.274\times$)" —— 注记日期可回源 `formulas/formula-spec.md` §8.17 第 13 条（2026-10-20），非虚注 |
| 14 | retention 的 R2F definitional + ledger 状态句 | ✅ ok | "100.00\% for the 50-task family (definitional: it carries no stripmap task, so the clip is empty)"；"the ledger stores a status entry for it alongside the 0.0 values of the preregistered scoring convention (annotated as such, consumed by no curve), and no average, no smoothing and no line segment passes through it"；`ledger[0]` id=`coverage.status.R1C.s0.8`，note 明写 "NOT a zero-coverage measurement and must not be plotted or quoted as one"。`main.tex:400,352` |

**小结：14 项中 13 项完全落地；第 12 项内容落地但引出计数错误（P1-1）。两轮修复没有把任何一个既有数字改坏。**

---

## 二、P0（必须修）

**零发现。** 全部带量主张回源通过：

- 反事实：`counterfactual_summary.json` → R2F/R3H `violation_rate_pure_median` 0.4239 / 0.2742（正文 42.4 / 27.4），`violating_pairs_pure_total` 199/458、253/926；`gap_pp_median` drop-later 30.44 / 18.25（区间 24.54–35.18 / 11.99–25.56），priority-aware 30.1136 / 17.0594，retime 7.0825 / 25.3321，conservative 28.3 / 55.52 —— 与图注 `main.tex:418` 的三臂读数、家族顺序标注 `(100-task/50-task family medians)` **完全同序**（18.25=100-task，30.44=50-task），未出现家族错位。
- 扫掠：配对落差三条 ledger 值逐位吻合；dip 两条（158/159）的 per-seed 位移与正文 "1.83/0.42、1.14/0.42" 一致，方向（net negative）与 "median moves" 一致。
- 摘要里 26.0/46.6/20.0/44.8 与 §6.2 的 26.01/46.58/20.01/44.78 只是显示位舍入，非错值。

---

## 三、P1（应修）

### P1-1　`42f4d39` 新增第六条 scope statement，但段首计数句仍是 "Five"

- 引句（`main.tex:443`）："**Five** scope statements are registered before anything is claimed. First, ..." → 同段（`main.tex:443/445/447`）实际枚举 **First / Second / Third / Fourth / Fifth / Sixth**，第六句为 `447` 行末 "Sixth, the scenario set itself: every reading comes from one platform ... And no scheduler from the published literature is run on this scenario set ..."
- 为什么是问题：这是段首句对段内结构的**自我计数**，读者数到第六句即证伪；审稿人最容易抓的一类缺陷（"the paper cannot count its own claims"），且它出现在 §7.1 限制章的开篇位置，正好削弱"自我设限纪律"的论证力度。
- 引入者：`42f4d39`（加第六句未同步首句）。镜像 `full.md:493` 同错。
- 修法：`main.tex:443` + `full.md:493` 的 "Five" → "Six"（一处词，零风险）。
- 附带（并入 P2-5）：`paper/sections/sec7_discussion.md:5,9` 仍是**五条**版本（缺整个 Sixth 句与"无外部基线"子句），需重生成。

### P1-2　"delivered resolution equals the requirement" 的无限定版本在引言与结论残留，与 §2.4/摘要已修正的口径冲突

- 已修正的版本（正确口径）：
  - 摘要 `main.tex:29`："for **the two task-law modes** the delivered resolution equals it at the selected start by construction ... **the stripmap branch delivers at or finer than the order via a start-domain clip**"
  - C5 `main.tex:208`："The stripmap mode (STR) has no task-level parameter: its delivered resolution is the squint-dependent floor value $(D/2)/\cos\bar\psi$ --- **at or finer than the requirement**"
  - §6.8 `main.tex:398`："**a per-mode rule**: for sliding spotlight and spotlight ... equals the requirement ... and for stripmap ... at or finer"
- 仍为无限定"相等"的三处：
  1. `main.tex:71`（贡献 1）："... the mode parameters follow the requirement where the mode has them --- **so that the delivered resolution equals the requirement at the selected start by construction**, an identity the search cannot violate rather than a constraint it could ---"
  2. `main.tex:108`（§1.4）："the mode parameters follow the requirement where the mode has them, **the resolution delivered at the selected start equals the requirement**, and the coverage cost ..."
  3. `main.tex:479`（结论首段）："... its parameters follow the requirement per task, **so the delivered resolution equals the requirement at the selected start by construction**; the dwell is then an endogenous consequence ..."
  4. （弱化变体，同源）`main.tex:360`（§6.2 机理句）："The mechanism is the parameter adaptation of constraint C5: the mode parameters are derived from the requirement at the selected start, **so the delivered resolution equals the requirement by construction**, and a tighter requirement therefore spends dwell rather than serviceability."
- 为什么是问题：STR 没有任务级参数，交付是 `(D/2)/cosψ̄` **at or finer**（且只在 clip 边界取等号）。三处无限定句让读者（尤其只读引言贡献句与结论的人）建立"三模式皆恒等"的心智模型，随后在 §2.4 读到"STR 无参数、交付 at or finer"即构成**论文自述冲突**——正是 C5 修正要消除的那类漂移。`42f4d39` 只把摘要与 §2.4/§6.8 改到位，结论 `479` 未被改动（属**修正暴露出的残余**，非新引入的错值）。
- 修法（每处半句，不增行）：
  - `71`：`...so that, for the two modes that carry task-level parameters, the delivered resolution equals the requirement at the selected start by construction (the stripmap branch delivers at or finer through its start-domain clip) ---`
  - `108`：`...the resolution delivered at the selected start equals the requirement for the two task-law modes and is at or finer than it for stripmap, and ...`
  - `479`：`...its parameters follow the requirement per task, so for the two task-law modes the delivered resolution equals the requirement at the selected start by construction (stripmap delivers at or finer through the start-domain clip); ...`
  - `360`：`...so for the two task-law modes the delivered resolution equals the requirement by construction, ...`

---

## 四、P2（可选）

### P2-1　同一读数两种精密度并存：图注 55.52 vs 正文/结论 55.5；结论还缺家族归属

- 引句：
  - 图注 `main.tex:418`："at the price of 28.3 and **55.52**~pp (50-task and 100-task families respectively)"
  - 正文 `main.tex:422`："serves a median 28.3 and **55.5** points less ... (family medians; per-seed ranges 15.15--33.46 and 51.98--69.10)"
  - 结论 `main.tex:481`："the conservative pre-shrunk arm costs **28.3 and 55.5 points** (Section~\ref{sec:counterfactual})"
- 为什么是问题：`figure_data/fig8_counterfactual.json` 收据侧是 55.52，正文侧四舍五入到 55.5 —— 两处都对，但**同一读数一粗一精并存**触发"哪个是台账"的查证动作（claims 席上一轮已报过此条，`42f4d39` 只改了正文，图注侧未同步，故仍残留）。结论句另有**独立**问题：其前一句刚按 "100-task ... 50-task" 顺序提过两族，而 "28.3 and 55.5" 是 50/100 顺序，句中未标族名，读者可错配。
- 修法：图注 `418` 的 `55.52` → `55.5`（或以 `55.52` 统一正文/结论）；结论 `481` 改为 "costs 28.3 points on the 50-task and 55.5 on the 100-task family"。

### P2-2　"S1 ... moved by exactly the sub-tolerance displacements" 读作"位移量恰好等于 X"

- 引句（`main.tex:356`）："... S1 is evaluated on the raw medians as frozen, so **its verdict is moved by exactly the sub-tolerance displacements** recorded in Section~\ref{sec:dip}, and that is the failure being reported."
- 为什么是问题：句意想说"裁决由低于容差的位移决定"，但 "moved by exactly X" 在英文里默认读作"位移量恰好是 X"；加上 `exactly` 是对幅度的强断言（实际位移是 −0.2683/−0.3590 pp 这类具体值，且 S1 判据是"任一 tighter 点低于 as-placed"而非幅度阈值），读者会去追问"exactly 到几位"。
- 修法：`so its verdict is decided by the sub-tolerance displacements recorded in Section~\ref{sec:dip}`（删 `exactly`，`moved by` → `decided by`）。

### P2-3　"Every cost in this subsection is measured against the family's own saturation point" 与紧邻上一段的 as-placed 锚点不符

- 引句（`main.tex:350` 段首）："**Every cost in this subsection** is measured against the family's own saturation point --- the first grid point at which its median reaches the family's maximum --- and never against another family or another generation. Every cost is a within-family quantity."
- 为什么是问题：紧邻其上的 `main.tex:348` 给的是 "from the as-placed point to $s=0.9$ the median coverage drops 26.0 percentage points"，锚点是 **as-placed**（R3H 0.9485），不是饱和点（0.9900）；若按饱和点算应是 30.2。该段随后只论证 as-placed premium（4.15/2.36），所以"Every cost"这一全称量化是过宽的，读者可能据首句去反算 L348 的 26.0/46.0/46.6 而得出"对不上"。属**既有**表述（非本轮引入）。
- 修法：`Every **as-placed** cost in this subsection is measured against the family's own saturation point`（一词），或把首句移到 4.15/2.36 之前。

### P2-4　"(dated design record)" 括注切开 "measured ... to exceed" 的动宾

- 引句（`main.tex:211`）："... after the task-law dwells **were measured (dated design record) to exceed** the library reference by up to $1.2008\times$ on the 50-task family (theoretical worst $1.274\times$) and had produced false violations"
- 为什么是问题：语法成立但读起来卡（括注落在 `measured` 与 `to exceed` 之间），且同一句已有两个括号（`(theoretical worst 1.274×)`），三括号连排在英文科技写作里属可优化项。注记本体必须保留（披露即量债）。
- 修法：`after the task-law dwells were measured --- a dated design record --- to exceed the library reference ...`，或后置 `(measured under the dated design record of 2026-10-20)`。

### P2-5　book-layer 镜像两处漂移（`sections/*.md`）

- 事实：`main.tex` 为准，`full.md` 必同步，`paper/sections/*.md` 为书层镜像。本轮检查：
  - `paper/sections/sec7_discussion.md:5,9`：仍是 "Five scope statements" 且**整段缺 Sixth 句**（P1-1 的同一处，镜像侧更旧一层）。
  - `paper/sections/sec6_results.md:95`：fig-8 段仍是**压缩前**版本 —— 多出 lead 句 "The fixed-dwell plan does not survive the replay on the dense families. The transfer constraint is violated in 27--42\% of consecutive pairs (median per-seed rates 27.4 and 42.4; ...)"，而 `main.tex:422` / `full.md:461` 已改为以 "The violation rate --- median per-seed rates 27.4 and 42.4; ..." 起句（数字一致，仅结构与起句不同）。
- 为什么是问题：数字无误，但书层若被 `\include` 或导出使用，会出现"同一节两个起句"；且 Sixth 句在书层缺失会让 scope 章少一条限制（少披露比多披露风险高）。
- 修法：由 `main.tex` 重生成 `sec7_discussion.md`、`sec6_results.md`（或在生成脚本里补一次全量重跑）。

---

## 五、已检查、零发现的方面（明说查过）

1. **四级数值一致（摘要–正文–结论–图注）**：27–42%（摘要）/27.4+42.4（正文、图注）、7–30（摘要、正文、结论）、26.0/46.6/20.0/44.8（摘要、§6.2、结论）、4.15/2.36/3.98/0.93（摘要、§6.2、结论）、retention 51.14/100.00/71.00（仅 §6.8 出现，无第二处）、保守臂 28.3/55.5（正文、结论）与 28.3/55.52（图注，见 P2-1）。**除 P2-1 外无第二处不一致。**
2. **家族顺序**：图注 `(100-task/50-task)` 与正文 "18.25 and 30.44 ... (11.99--25.56 and 24.54--35.18)" 同序；保守臂图注 `(50-task and 100-task)` 与正文 "28.3 and 55.5 ... (15.15--33.46 and 51.98--69.10)" 同序。两组顺序不同但**各自标注明确**，不构成错位（结论侧见 P2-1）。
3. **语法/表层残留扫描**（全文）：重复词 0；句中双空格 0；标点前空格 0；`TODO/XXX/FIXME/TBD` 0；逐行括号配平（无一行净差 ≠0）；`$` 配对正常；无未定义 `\ref`；无重复 `\label`。**残留只在上面 5 条里。**
4. **`full.md` 五处指定镜像点**：摘要（"for the two task-law modes ... at or finer than the requirement"）、§2.4 C5（"at or finer than the requirement"）、retention（"retention reads 51.14% for the control family" + "definitional: it carries no stripmap task"）、§6.2 地板（"20.01 of the observed 26.01-point drop" / "44.78 of the 46.58-point" / "25.16 points to" / "49.93 to"）、结论（"the delivered resolution equals the requirement at the selected start by construction" —— 即 P1-2 的镜像同错）**全部在位**，无一句丢失。
5. **S1/S3 表面矛盾判定为不存在**：S3 是"预测下探"型判据（median at $s=0.8$ below the as-placed），"紧臂不再下探"即 S3 未达；Lead 句、Table 3 的 `R2F … not met`、正文三处互证。**不作缺陷报。**
6. **摘要词数**：空白切分 244（区间拆分 247），在 250 上限内；不是"必须恰好 250"，**不作缺陷报。**
7. **只读纪律**：未编译、未跑套件；`paper/` 下无新增文件（aux/log 均未生成）。

---

## 六、给修复席的最小补丁清单（按行号，共 9 处 + 2 个镜像重生成）

| # | 位置 | 改法 | 严重度 |
|---|---|---|---|
| 1 | `main.tex:443` | "Five" → "Six" | P1-1 |
| 2 | `full.md:493` | "Five" → "Six" | P1-1 |
| 3 | `main.tex:71` | 贡献 1 补"两模式 + STR clip"半句 | P1-2 |
| 4 | `main.tex:108` | §1.4 补分模式半句 | P1-2 |
| 5 | `main.tex:360` | "for the two task-law modes" 限定 | P1-2 |
| 6 | `main.tex:479` | 结论补"两模式 + STR clip"半句（与摘要 `29` 同措辞） | P1-2 |
| 7 | `main.tex:418` | `55.52` → `55.5` | P2-1 |
| 8 | `main.tex:481` | "costs 28.3 points on the 50-task and 55.5 on the 100-task family" | P2-1 |
| 9 | `main.tex:356` | "moved by exactly the sub-tolerance displacements" → "decided by the sub-tolerance displacements" | P2-2 |
| 10 | `main.tex:350` | "Every cost" → "Every as-placed cost" | P2-3 |
| 11 | `main.tex:211` | "(dated design record)" 改为破折号插入或后置 | P2-4 |
| 12 | `sections/sec7_discussion.md`、`sections/sec6_results.md` | 由 `main.tex` 重生成 | P2-5 |

改动量：`main.tex` 6 个词 + 4 个半句；`full.md` 1 个词；镜像 2 个文件重生成。**不动任何数字的数值、不动表格、不动图注里的测量口径。**

VERDICT: 0/2/5
