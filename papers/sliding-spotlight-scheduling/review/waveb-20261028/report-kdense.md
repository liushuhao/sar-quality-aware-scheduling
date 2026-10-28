# Wave B 审查报告 — seat=kdense（K-Dense 同行评审清单席）

- 日期：2026-10-28
- 审查对象：`papers/sliding-spotlight-scheduling/paper/main.tex`（HEAD 工作树，8 图 3 表）+ `paper/refs.bib`
- 方法（来自 peer-review SKILL.md 六类清单）：claim–evidence / methods / statistics / reproducibility / figure-table / citation
- 方法补充：数字抽核对 `experiments/v5_results/` 工件（mode_decomposition.json、margin_sensitivity.json、tier_shift_phi0_9/1_1.json、figure_data/fig4/6/7/8、reading_ledger_l8.json 局部）；引用集正文↔bib 全量比对（36/36）。

## 红线复述

1. 只读：本案未改仓库任何文件，唯一写盘 = 本报告。
2. 所以下列发现每条带 file:line + 原文引句 + 问题理由 + 建议修法；无引句即作废。
3. 严重度：P0=事实错/数字错/物理错/自相矛盾；P1=论证缺口/口径漂移/误导读法；P2=表述结构改进。
4. 不确定的标 QUESTION，不把口味当缺陷。
5. 审的是当前 HEAD main.tex（含本轮新增 Fig 2/4/6/7/8）。

---

## 发现列表

### P0（必须修）

**P0-1　"Xin et al." 作者姓氏误归——属事实性引用错误（citation 类）**

- 位置：`paper/main.tex:110`；`paper/refs.bib:68-69`
- 引句（main.tex:110）："Xin et al.~\citep{xin2024sar} plan SAR regional observation with weighted multi-objective and genetic-algorithm planners"
- 引句（refs.bib）："author = {SHI Xin and XING Mengdao and ZHANG Jinsong and LIU Huitao and WANG Hongxian}"
- 为什么是问题：已联网核实（遥感学报官网 2024 年第 7 期，DOI 10.11834/jrs.20243258），该文第一作者为**石鑫（Shi Xin）**，期刊作者表述是"姓在前+全大写"体例：石鑫/邢孟道/张金松/刘会涛/王虹现。第一作者姓氏是 **Shi**，"Xin"是名。正文称"Xin et al."、且 BibTeX 会按 `SHI Xin` 把 "SHI" 解析为名、"Xin" 解析为姓（authoryear 输出恰好渲染成 Xin et al.），即论文与原始文献对不上——同行评审里这是可被审稿人挑出的硬伤。
- 建议修法：refs.bib 中将作者改写为花括号保护姓的形式 `{Shi}, Xin and {Xing}, Mengdao and ...`（同理其余四位），并把正文 "Xin et al." 改为 "Shi et al."。

**P0-2　§5.6 同段落自相矛者："double-digit under every rule" vs "cuts the 50-task gap to 7.08"（claim–evidence 类）**

- 位置：`paper/main.tex:422`（§sec:counterfactual）
- 引句一："The span 7--30 points is therefore a property of the repair capability, not a single number, and the two rules bracket it: the measured consequence of flying a plan that is infeasible against the real dwell is **double-digit under every rule tested on the dense families**, and which end of the span a deployment approaches depends on how much re-timing authority its repair has."
- 引句二（同段上方）："and (iii) a bounded re-timing --- ... --- which **cuts the 50-task gap to 7.08** but \emph{raises} the 100-task gap to 25.33"
- 为什么是问题：7.08 pp 是个位数，与"双位数、每条规则都成立"直接矛盾；同句又说区间是 7–30（摘要 main.tex:29 也用 7--30，7 正是这条 50-task re-timing 中位数，图中 receipt `fig8.gap_median_pp.retime.R2F = 7.0825`）。这是论文内部自相矛盾，而且恰好出现在核心反事实主张的限定句上。
- 建议修法：把限定句改为与实际一致的表述，例如 "at least 7 points under every rule on the dense families, and double-digit under every rule on the 100-task family"（修法需与摘要 7–30 措辞协调，见"给其他席的提示"）。

### P1（应修）

**P1-1　覆盖率中位数全程无离散度读数（statistics 类）**

- 位置：`paper/main.tex:307`（§sec:curve，Table~\ref{tab:modes} 及正文九点中位数）；`paper/main.tex:311`（表注）
- 引句："Observed: median served-priority fraction of the best-covered member (released artifacts, budget 40/60)."以及正文"0.4827 at $s=0.8$, 0.6884 at $s=0.9$ ..."（307 行）
- 为什么是问题：所有关键 Δ（26.0 / 46.6 / 0.27 / 4.15 / 2.36 pp）都是"十种子中位数的中位数"之差，正文明言种子同时驱动场景与搜索（291 行自曝该混杂），但通篇未给任何区间读数（IQR/百分位/逐种子差范围）；摘要级主张没有不确定性附注。五席中的 ars-method 若只看方法学章节可能漏掉：唯一有逐种子范围的是反事实段（422 行）与 dip 段（385 行），主干表没有。
- 建议修法：在 Table 2 观测列旁或附注给出各点种子 IQR（或 min–max），至少对 26.0/46.6 两条主 Δ 给出逐种子差值区间；工件里（mode_decomposition/sweep pilot 均含逐种子值）不需要新跑任何实验。

**P1-2　"bit-reproducible" 强主张缺环境披露（reproducibility 类）**

- 位置：`paper/main.tex:250`
- 引句："The search runs under a fixed random seed per unit, single-threaded, with manifest task-list order everywhere ..., so every unit is bit-reproducible."
- 为什么是问题：位级复现的承诺依赖解释器与库版本（收据里 `produced_by` 均带固定 Python 路径/PYTHONHASHSEED=0），但正文与 Data availability（495 行）都未声明 Python/依赖版本或环境清单；审稿人按 reproducibility 清单第一条就会问"以何种环境复现"。
- 建议修法：在 Data availability 或实验设计节补一句环境描述（Python 版本、依赖锁定文件、PYTHONHASHSEED=0、单线程），或将环境清单列入将存 Zenodo 的工件清单。

### P2（可选）

**P2-1　贡献 2 的"0.27-point plateau"限定不足，易被读作全程平坦（claim–evidence 类）**

- 位置：`paper/main.tex:72`
- 引句："tightening costs of 26.0--46.6 percentage points on the dense family against a 0.27-point plateau on the 50-task family"
- 为什么是问题：R2F 实际有两个局部下降 0.268 与 0.359 pp（333、385 行），S1 在该族"not met"（Table 3、356 行）；0.27 只对"更紧一侧"成立（摘要 29 行有 "at every tighter point" 限定），贡献句删掉了这个限定。属易误导读法，非数字错。
- 建议修法：补回限定，如 "a 0.27-point tight-side plateau (two sub-0.4-point local declines elsewhere)" 或直接复用摘要的 "at every tighter point"。

**P2-2　Fig 5 无 figure_data 收据；panel (b) 的"context"裁切未声明（figure-table 类）**

- 位置：`paper/main.tex:342`（fig5 caption）；`experiments/v5_results/figure_data/`（仅 fig2/4/6/7/8 有 JSON，fig5 缺）
- 引句："(b)~Upper-band zoom, $y\in[0.958,1.004]$, showing the 50-task family's two local declines ... with the control family drawn for context"
- 为什么是问题：对照 R1C medians（0.5398 at 0.9），说"control family drawn for context"而 y 窗下缘 0.958 —— control 的 s=0.9 点落在窗外，是否裁切/只画 s≥1.0 段无收据可核；fig5-a 的中位数虽可经 mode_decomposition.json 间接追溯，但缩放窗与空心标记位对无工件。非必然错，spectre 清单记为未覆盖项。
- 建议修法：补 fig5 收据 JSON（如其余五图），或在图注注明 control 只以可行点入绘/裁切说明。

**P2-3　refs.bib 两处格式隐患（citation 类）**

- 位置：`paper/refs.bib:54-59`（liu2025a）、`refs.bib:142-149`（li2026efficient）
- 引句：liu2025a "author = {W Liu and D Zhang and Y Tian and X Shao}"；li2026efficient "@misc{li2026efficient, ... journal = {arXiv} ... note = {arXiv preprint}}"
- 为什么是问题：liu2025a 作者只有缩写（疑从题录截断，authoryear 期刊审稿常要求全名）；li2026efficient 用 @misc 却带 `journal` 字段，elsarticle-harv/natbib 下渲染不可靠（应改 @article + journal={arXiv preprint arXiv:2604.19539} 或 @misc+eprint 约定，与库内其它 arXiv 条目风格统一）。
- 建议修法：补全作者姓名；统一 arXiv 条目的 bib 类型与字段。

**P2-4　\label{sec:floor} 置于小节中段，交叉引用读起来像"节"而非"段"（结构）**

- 位置：`paper/main.tex:352`；多处 "Section~\ref{sec:floor}"（如 223、311、335 行）
- 引句："\label{sec:floor}The control family's tightest grid point is a different kind of fact..."
- 为什么是问题：该 label 无 \subsection 层级，\ref 解析为所在小节号（5.2），读者按"Section 5.2"翻回去找到的是整个 as-placed 小节而非专讲不可行点的其中一段，指称失准。
- 建议修法：给该段一个 \paragraph{R1C at $s=0.8$ is an infeasibility record ...}\label{sec:floor} 结构，或在正文里改用 "the infeasibility record of Section 5.2 (below)" 的文字指称。

### QUESTION（未裁定，不占 P 计数）

- 无（本轮六类清单内未形成需要外部材料才能裁决的项；若需要可补充：`liu2025a` 全名需查 Springer 原文；`caleiras2026a` 的 DOI 前缀 10.5220/00144070... 与 ICORES 2026 收录一致性建议在终校时对一次官网页）。

---

## 检查过且零发现的方面（明确列出）

1. **citation（悬挂/未消费）**：正文引用键 36 个 ↔ bib 条目 36 条，逐一比对 1:1，无悬挂引用、无未消费条目；\citealt 用法正确（main.tex:205）。
2. **figure-table（引用完整性）**：8 张图每张都被正文引用（fig1→L138、fig2→L161、fig3→L235/254、fig4→L268、fig5→L307、fig6→L387、fig7→L404、fig8→L413）；3 张表均有正文引用（tab:related→L111、tab:modes→L307/L350/L481、tab:criteria→L355/356）。
3. **figure-table（收据比对）**：fig4 收据（组成区间 20/20、46–50、99–100；窗数 145–162/337–391/731–779）↔图注逐项一致；fig6 收据（12/40 不可行、12.89–54.90 pp、检索增益 0、160/240 预算）↔图注一致；fig7 收据（44 项：T 中位 1.2114/1.1932→"约 1.2 s"；SLS 5.10；SPT 3.74–10.79；比值 1.08–1.11/1.35/1.82–2.03/最大 2.65；squint 20.07–23.57/25.73/34.95–37.77）↔图注逐项一致；fig8 收据（42.39/27.42%；199/458、253/926；四个臂中位 30.445/18.247、30.114/17.059、7.083/25.332；conservative 0/324、0/354 对价 28.3/55.52；R1C 1/186、逐种子 6.31）↔图注与正文逐项一致（含 422 行逐种子区间 11.99–25.56、24.54–35.18）。Fig1/Fig3 为 TikZ 矢量图，文件存在，编译闸 0 错。
4. **表 2 自洽（tab:modes）**：九点×三族×(bound, obs) 与 `mode_decomposition.json` 全量一致（0.501/0.748、0.483/0.688/0.948/0.977/0.981/0.988/0.988/0.990/0.990、0.569/0.540、R1C 0.8 行 bound 0.000/obs "—"）；正文派生 Δ（20.01/26.01、44.78/46.58、残差 6.0/1.8）由收据复算成立。
5. **§knobs 数值**：margin_sensitivity.json（最大移动 0.9766→0.9833=0.67pp ≤"at most 0.7"；floor 双点在 pad/mane­ver-only 下不动、联合法移动 ±0.18pp；prod 列与 stored_anchor_median 全 9 点重合）与 tier_shift 收据（φ=1.1：s=0.8 与 0.9 均 10/10 无可行、s=1.0 中位 0.5675→"0.568"；φ=0.9：全格无不可行、s=0.8 中位 0.4688→"0.469"）均与正文一致；s*=0.905 算式复算成立（2.4669/(3.0/1.1)=0.9047）。
6. **主张链自洽性抽查**：477,308 实例/9,430 记录/13,845 任务/34.5 倍（398 行）内部自洽；270=260+10 单位口径（258 行、398 行）一致；27–42% ↔ 27.42/42.39 一致；7–30 ↔ 7.08–30.44 一致（除 P0-2 的限定句）；纹理数值如 345.7 kHz=95.2×3630=300.6×1150、ECEF 换算 +4.9%（7578.05/7221.69=1.0493）、§2.1 常数链（θa/A=λ/(2ρ_a)=0.031、A=0.202683→k=0.797317→r0/R0=A/(1−A)=0.254207）均复算通过。
7. **Data availability ↔ 工件**：声明列出的工件类型在 `experiments/v5_results/` 中都能对上（scenarios/、sweep/ 逐单元 pilot 记录、预算层 pilot、tier_shift/、budget_check/、counterfactual_fd/、anchor_free/、matrix/），"acceptance 后 Zenodo、评审期 on request" 与仓库现状不冲突（引用条目是否真上传不在本席可证范围，见下）。
8. **术语一致性重点抽查**：requirement/demand、coverage= f₁、tie-set、as-placed、"infeasibility record ≠ zero coverage"、"dense family/s 与 50-task family" 的使用在除 P0-2 之外的抽样点上口径一致（含 ledger 禁语清单的敏感句型——正文未见硬违语）。
9. **伦理/诚信格式面**：CRediT、竞利声明、资助单一作者声明齐备；参考文献池标注了来源与转换说明（refs.bib 头注），无版本遗留杂项。

## 对其他席可能盲区的一句提示

给 bundle owner：修 P0-2 的"double-digit"措辞时，其余五席尤其 claims 席的检查基线（摘要"7–30"、"27–42%"）与 code 席的 counterfactual 口径都不受影响，但若有人顺手把 "dense families" 统一改为单数指 R3H，会与摘要的复数用法冲突——等待下一轮统一术语时一并处理；另外 seat=code 不审 refs.bib 与引用（P0-1 只有本席与 ars-method 可能覆盖），请勿在采纳本席结论前先改作者名而不同步改正文称谓。

VERDICT: 2/2/4
