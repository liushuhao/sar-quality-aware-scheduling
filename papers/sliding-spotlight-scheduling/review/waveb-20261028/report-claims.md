# Wave B — seat=claims（论点/论据/反防御）审查报告

- 审查对象：`papers/sliding-spotlight-scheduling/paper/main.tex`（当前 HEAD 工作树）
- 依据：`C:/Users/33151/.claude/rules/paper-writing.md` §4（反防御性写作）+ §9（英文文字表层），逐条过叙事层（摘要/引言/结果/讨论/结论）与新增图注（Fig 2/4/6/7/8）
- 日期：2026-10-28

## 红线复述（先复述再产出）

1. 只读：未改仓库任何文件；唯一写入 = 本报告。
2. 每条发现带 file:line + 原文引句 + 问题性 + 建议修法；无引句作废。
3. 严重度：P0=事实错/数字错/物理错/自相矛盾；P1=论证缺口/口径漂移/误导读法；P2=表述与结构改进。
4. 不确定写 QUESTION，不把口味当缺陷。
5. 审的是 HEAD 的 main.tex（含本轮新增 Fig 2/4/6/7/8）。

---

## P0（必须修）

**零发现。** 摘要/结论的全部带量主张与正文、表 1、图注逐一对账一致：
- 27--42\%（正文 `main.tex:422` "median per-seed rates 27.4 and 42.4"）、7--30（"cuts the 50-task gap to 7.08 but raises the 100-task gap to 25.33" → 7.08--30.44）、26.0/46.6/20.0/44.8（`main.tex:307` "the floor accounts for 20.01 of the 26.01 ... for 44.78 of the 46.58-point drop"）、46.0（`main.tex:335` R1C 0.5398 → 46.02pp）、≤0.27（`main.tex:333` 0.9764−0.9737=0.27pp）、4.15/2.36/3.98/0.93（`main.tex:350`）均得回源。
- 未发现自相矛盾句：结论未出现与 §6 内任何裁决相反的表述；infeasible-cell 的双读（frozen met / refined undefined）在 §6.3、表 3、§6.6、摘要处的说法互相一致且都携带口径日期。

## P1（应修）

**P1-1　引言首个模式概念句携载限定不完整，与 §3 声明的三种模式规则口径漂移**
- 引句（`main.tex:61`）："Where a task sits on that continuum ... is fixed by the requested resolution --- the requirement, as this paper calls it from here on --- the scene, and the geometry of the pass, and it determines how long the satellite must dwell on the scene."（原句为 "Which point of that continuum a task receives is not a free stylistic choice --- it is fixed by the requested resolution --- ..."）
- 为什么是问题：§4 正文（`main.tex:225`）明确"the data of this paper follow neither of those at run time: they carry the grandfathered assignment"；§3.5（`main.tex:221`）"the assignment is the one the scenario set was generated with, inherited unchanged"。即数据中"mode 由 requirement 派生"只对**参数**成立，**分配**是冻结继承的。引言此句是全文最高层概念句，未带 "under this study's frozen mode assignment" 类限定，读者由此建立的第一心智模型与 §3 的"三条规则"披露冲突——正是规则 §4 硬边界"主张与证据一致"与论文自身随处执行的限定携载纪律在此句上的漏网。贡献句 1（`main.tex:71`）带了限定，但读者先读到的是此句。
- 建议修法：在 `main.tex:61` 该句或其所在段落尾追加一个子句挂限定，如 "…determines how long the satellite must dwell on the scene (the mode assignment in this paper's data is frozen at generation time and held across the demand scan; Section~\ref{sec:axis})"，或在句内把 "is fixed by" 改为 "is fixed at design time by"。一行即可消除与 §3 的口径漂移。

## P2（可选）

**P2-1　摘要内嵌防御性括注 + 无量化比较级形容词**
- 引句（`main.tex:29`）："the zero-squint value, the most fragile fixed-dwell convention" 及 "the span depending on the repair rule (its lower end from a rule added after the sweep)"。
- 为什么是问题：两个括注都是"回答没人问的问题"（§4）——"fragile" 的比较与"下端出自补扫规则"的时序披露属结果/讨论层内容；且 "most fragile" 无文内比较测量支撑（正文 `main.tex:422` 显示确实最优评：预收窄 fixed-dwell 基线可消除违例，零斜视最不利，但摘要级未给出该比较）。披露本体按 §2/§3 须保留，不得删除。摘要句均超长（最长一句 ~80 词），三角文风（§9 最重要的信息最先）被三层括注拖慢。
- 建议修法：摘要里把 repair-rule 时序改为短限定 "(rule-dependent)"，细节留给 §6.7；"the most fragile fixed-dwell convention" 换为量化表述如 "the least conservative fixed-dwell convention (the zero-squint value)"。

**P2-2　元话语（meta-discourse）句：论文谈论文而非谈内容**
- 引句：`main.tex:65` "...are registered as not used, and the paper says so where it matters."；`main.tex:78` "The claim is scoped to the literature surveyed below: the survey rests on the project's curated literature pool --- a converted and catalogued bibliography of the field plus an incremental paper-search sweep over the months preceding writing..."。
- 为什么是问题：§9 三角文风——应写"发现了什么"，不写"论文在何处说了什么"；文献检索方法学自述对期刊读者未问且可移至 Data availability/附录。
- 建议修法：前者删尾句，改为直接列出被弃构型（句子已具备）；后者压缩为一句或移至 §7.6 / Data availability。

**P2-3　预答式"加重强调"回答没人提出的主张**
- 引句 1（`main.tex:138`）："We stress the symbol discipline that the two distances are dimensionally identical but semantically distinct ... and the two are never interchangeable (Fig.~\ref{fig:modes})."
- 引句 2（`main.tex:104`）："that line of work exists, it is not the line this paper takes, and nothing here claims its absence."
- 为什么是问题：§4 交稿前自查——无人主张"r0/R0 可互换"或"本文否认多目标线存在"；自我澄清式强化是在给审稿人搭虚拟稻草人，占篇幅且削弱主线。
- 建议修法：引句 1 保留在 Fig.~\ref{fig:modes} 图注（已有同义披露 `main.tex:155`），正文一句即可；引句 2 收为 "that line of work takes a different placement of quality"，删除辩解尾句。

**P2-4　同一披露句全文重复 3--5 处（防御反射的横向扩散）**
- 引句：完整同句 "the evaluator performs no AASR recheck of its own" 出现于 `main.tex:196,235,277` 及 Fig.~\ref{fig:loop} 图注（`main.tex:240`）；"an infeasibility record, not a coverage of zero / never interchanged" 家族句出现于 `main.tex:223,352,Table~\ref{tab:modes} caption (311),356,481`。
- 为什么是问题：§4/§9——披露一处携边界足矣；同句逐字重复不是文采是无阅读效率损耗，也让 ~64 页 review 版的叙事密度进一步下降。
- 建议修法：保留一处完整句 + 一处图注，其余处缩为 "(Section~\ref{sec:quality})"/"(Section~\ref{sec:floor})" 交叉引用。

**P2-5　同一统计量两种精密度并存（正文 vs 图 8 图注）**
- 引句：`main.tex:422`（正文）"serves a median 28 and 56 points less" vs Fig.~\ref{fig:counterfactual} 图注（`main.tex:418`）"at the price of 28.3 and 55.52~pp"。
- 为什么是问题：不是数字错（28←28.3、56←55.52 舍入一致），但同一读数一粗一精并存触发"正文与图哪个是台账"的查证动作；正文其余读数均给 2--4 位精密度（18.25/30.44/17.06/30.11），唯此处粗化。
- 建议修法：正文改为 "serves a median 28.3 and 55.5 points less"。

**P2-6　相关工作敏捷调度段为注释书目式罗列，未逐项给缺口**
- 引句（`main.tex:98`）："hybrid genetic and simulated-annealing planners for moving-target observation \citep{qin2024multisatellite}, deep reinforcement-learning planners ... \citep{long2024deep,chen2024learning,zhang2025deep}, adaptive large-neighborhood search ... \citep{du2025satellite,he2018a}, ..."
- 为什么是问题：§9 "文献讨论是带 however 的故事，不是注释书目——每篇 = 做了什么 + 剩什么缺口"；此段 10+ 引用仅按方法学聚类，缺口只在全段统一末句给出。定位段（§2.4 Positioning）完成了这个任务，但 §2.2 自身仍停留书评式罗列。
- 建议修法：将 §2.2 的罗列压缩至 5--8 篇代表性工作，每项配半句缺口，或直接声明该段由聚类陈述 + 指向 §2.4。

---

## 已检查、零发现的方面（明说）

1. **novel/robust 封顶（§9）**：`novel` 全文 0 次；`robust` 全文 1 次（`main.tex:422`，且用作"repair-independent"的具体陈述修饰，合规）。
2. **模糊归因（§9）**：无 "研究表明 / It is well established / 学界认为" 式无主语归因；所有文献性均点名（Currie & Brown、Kim、Song、Zhang et al. 等具名格式贯穿 §2）。
3. **推销式结论（§9）**：结论无 "打开新大门/影响深远/奠定基础" 类句；后续方向具体（onboard replanning、constellation-level tier management，`main.tex:483`）。
4. **贡献句挂便宜测量（§4/§5）**：三条贡献句均可在正文回源到带数测量；无"承诺测量未落地"的贡献句。
5. **限定携载一致性**：headline 限定 "under this study's / the frozen mode assignment" 在摘要、贡献 1/2、§6.2、§7.1、结论均有携带（除 P1-1 一处外）；"single budget 40/60"、"single-pass operational scope"、"postal-negative claims" 均一致。
6. **自强弱语句扫描（§4）**：无 "遗憾的是/unfortunately/仅-margin/仍明显落后" 式自我削弱句；`grep signal` 中 "merely" 两处（`main.tex:285,451`）均为对比构造（"rather than merely"）而非自我弱化用法。
7. **新增图注断言与正文一致性**：Fig.2（floor 算术、0.8×[2.5,3.0]、W_a/v_s=0.6598=5000/7578.05 ✓）、Fig.4（145–162/337–391/731–779 窗口数与 §3.2 一致 ✓、"covary by design" 与正文一致 ✓）、Fig.5（46.6pp、cross 标注与 §6.2 一致 ✓）、Fig.6（12/40、28 cells、16× 预算读数与 §6.4 一致 ✓）、Fig.7（dwell 中位数/比率/|ψ̄| 读数为图承载的新量，正文 `main.tex:404` 显式让位给图，无冲突）、Fig.8（199/458、253/926、各修复臂数与 §6.7 一致 ✓，家族顺序在图注内逐处显式标名）。
8. **术语全文一致（§9）**：requirement/demand 二词职责按 §3.5 定义执行；coverage=served priority fraction 别名定义后一致使用；tie-set/infeasible-cell/as-placed point 术语无漂移。
9. **未量化披露（§3 披露即量债）**："the true off-vertical attitude excursion is understated by an unquantified amount"（`main.tex:174,457`）、elevation-plane omission "Its magnitude is not quantified here"（`main.tex:455`）均显式标注为未量化观察，合规。

## 对其他席可能盲区的一句提示

theory/ars 席通常按式与按实验设计审查、容易整段跳过 §6.7 首句与 §7.5 尾句这两处**纯叙事承载全文主结论措辞**的位置——本席对账过；code 席如核到 §6.7 谓 "pre-shrunk" 基线，注意正文与图注精密度差（P2-5）很可能源于 figure_data 收据 vs 舍入管线两端各自定型，建议 code 席回源 `figure_data` 收据本身而非仅正文本台。

VERDICT: 0/1/6
