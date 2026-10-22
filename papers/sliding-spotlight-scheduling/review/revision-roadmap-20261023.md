# Revision Roadmap — 2026-10-22 独立外审（五席 + 编辑裁决）

**Source**: `papers/sliding-spotlight-scheduling/review/paper2-independent-review-20261022.md` — 独立外审式五席评审（期刊适配 / 方法论统计 / SAR 领域 / 实践跨学科 / Devil's Advocate + 编辑裁决），判 **Major Revision**。
**Mode**: ARS `academic-paper` revision-coach 路径改编。locator 用 `main.tex:line`；PDF 页码以 `paper/main.pdf`（48 pp.）为准。
**Immutable core**: 36 项可核验发现（R-01 … R-36），按主题分组。**本 Roadmap 的独特点**：每条在落盘前已由主线程**独立复算核验**（非照抄审查结论），核验证据（file:line + 复算命令 + 结果）随条携带。
**Manuscript**: `papers/sliding-spotlight-scheduling/paper/main.tex`（单语，无 ZH 镜像）。
**Author triage**: 单独 `author-adjudication-20261023.md`（DRAFT，待用户逐条裁决）。

## Legend

- **Type**: Major（核心主张/方法/结论或硬错误） | Minor（质量/完整性） | Editorial（措辞/格式）
- **Cost**: sentence | section | restructure | figure | new_data
- **核验裁决**（主线程独立复算后判定）：
  - ✅ **成立** — 审查主张经独立复算确认，且对主张有实质影响
  - 🟡 **半成立** — 事实核心成立，但审查定性过重 / 或论文已部分披露
  - ⓘ **披露已覆盖** — 事实成立但论文已明确披露，仅剩措辞/敏感性缺口
  - ❌ **不成立** — 审查主张经复算被证伪（本批：无）
- **Obligation**: 留空——用户在 sidecar 裁决；不从严重度/核验结论推导。

---

## 核验总览（先于逐条）

| 核验项 | 命令 / 方法 | 结果 |
|---|---|---|
| L8 数字闸 | `python scripts/verify_paper_numbers_l8.py --paper paper/main.tex` | rc=0，**74/74 复现**（与审查一致） |
| 收紧方向代价 | 自 `experiments/v5_results/sweep_results.json` 重算各 family×s 中位数 | R3H 1.0→0.9=**26.01pp**、1.0→0.8=**46.58pp**；R1C 1.0→0.9=**46.02pp**；R2F 1.0→0.8=**0.00pp**（全部逐位命中审查） |
| R3H 机制分解 | 自 30 个 R manifest 重算 STR 优先级份额 / 地板上界 | 非 STR 份额中位 **0.5007**、s=0.9 上界 **0.7484**、R1C s=0.9 上界 **0.5694**（全部命中审查） |
| 477,308 分解 | 自 sweep pilot artifacts 重算 | = 9,430 条 front 记录 Σ n_selected；distinct 任务 **13,845**；比值 **34.5×**（命中） |
| 相关性脆弱性 | 自 sweep_results.json 重算 Pearson | r=0.3286(n=26)→去 R1C s=0.9 = **−0.0699**(n=25)；r=0.2495(n=260)→压 30 场景均值 = **0.0278**（命中） |
| SAT 定义 | 读 `literature/fulltext/kim2021_aerospace_fulltext.txt:233-236` | **「Synthetic Aperture Time (SAT)」**；`saturat` 词根全文 **0 命中**（铁证） |
| 预注册时序 | 读 `experiments/analysis_prereg_v2.json` + `experiments/RUN_LINEAGE.md` | L8 sweep 落地 **2026-10-20**；登记 L8 主结果的 amendment 日期 **2026-10-21**（晚于数据，命中） |

> 核验纪律：全部数字经主线程实跑复核（非信审查自述）；文件路径、行号、复算命令随条可重跑。

---

## Index

### Part A — 阻断级发现（对应审查 B1–B7）

| ID | 位置 | 核验 | Type | Cost | 简述 |
|----|------|------|------|------|------|
| R-01 | 摘要 L29 / 标题 L16 / §6.2 | ✅ | Major | section | 头条 4.15/2.36 是「对饱和点」差（放松方向），标题却称「收紧代价」；真收紧代价 26/46.6/46.0pp 在正文 §6.1 才有 |
| R-02 | §6.2 L279–281 / Table 1 | ✅ | Major | sentence | 「own saturation」= 同曲线九点网格 argmax；R1C 饱和点=订单点代价恒 0（藏住 46.02pp）、R2F 在网格边界 s=2.0 |
| R-03 | §5.1 L228 / §6.2 L283 | ✅ | Major | sentence | R1C s=0.8「10/10 不可行」是 [2.5,3.0]m×0.8<2.4669 的算术必然；带宽正文 0 披露 |
| R-04 | §6.1 L268 / §6.3 L291 | ✅ | Major | restructure | 三族任务数与 STR 占比完全共变；R3H 收紧损失 77–96% 由 STR 地板排除解释，非 dwell/transfer 机制 |
| R-05 | 摘要 L29 / §6.5 L322 / 结论 L385 | ✅ | Major | sentence | C5「无违反」+477,308 是构造性/成员级重复计数（distinct 仅 13,845），且恒等式对 STR 不成立 |
| R-06 | §3.5 L177 / §5.3 L248 | ✅ | Major | sentence | 头条量（own-saturation 代价）随 2026-10-21 amendment 才登记，晚于 2026-10-20 数据——「frozen/registered」措辞不适用 |
| R-07 | Table 1 L287 vs L283 | ✅ | Major | sentence | Table 1 R1C C3「met」自认依赖「infeasible 记作零覆盖」约定，与同页「两者绝不可互换」矛盾（正文自带） |
| R-08 | p.14 L144 / §6.5 L334 / Fig 4 | 🟡 | Major | sentence | f_Q,deliv 式 cos²ψ 与其注册口径自洽（非印错）；真缺陷=「squint-**loss** factor」命名方向反（式使 f_Q 随斜视增大）+「delivered」读数带多余 sec²ψ |
| R-09 | §2.1 L71/L75/L122 | ✅ | Major | sentence | SAT 展开「saturation-avoidance time」错误——Kim 原文 = **synthetic aperture time**，且与本文「saturation arm」语义相撞 |
| R-10 | 摘要 L29 / §5 L236 / §6 L266 | ✅ | Major | sentence | 「single-orbit」事实错误：R1C 跨 70.3–72.0 h（≈3 天/≈45 圈）、145–162 窗、7.3–8.1 窗/任务 |

### Part B — 方法 / 统计发现

| ID | 位置 | 核验 | Type | Cost | 简述 |
|----|------|------|------|------|------|
| R-11 | §3.4 L167 / §7 | ✅ | Major | section | 机动 hybrid 不连续非单调：0.46 s→4.07 s 跳变落在锚点典型跃迁上；fallback 频率与 pad/settle/PRF/AASR 敏感性全缺 |
| R-12 | §6.6 L332 | ✅ | Major | sentence | 两个 Pearson r 均脆弱（单点/聚合即塌）；数字闸无 Pearson 路径不覆盖。「违反自定 no-pooling」子主张 🟡（该条禁 raw f_q 合并，相关用的是归一化兑现率） |
| R-13 | refs.bib / main.tex | ✅ | Minor | section | 最近的 SAR 区域观测 4 篇（liu2025a/shen2024multistrip/xin2024sar/li2026efficient）在 bib 内、引用均 0 |
| R-14 | §5.3 L246 / run_matrix.py:341 | ✅ | Major | new_data | 场景种子=求解器种子（文件名解析直传）；「10 seed」是 10 个不同场景非 10 次求解重复，搜索噪声与场景抽样不可分离 |
| R-15 | §5.2 L236 / Table | ✅ | Minor | sentence | 「46 admitted/99 admitted/342/753 窗」均为单 seed 取值（实测 R2F 46–50、R3H 99–100、窗 337–391/731–779） |
| R-16 | Table 1 / §6.1 L264 | ✅ | Major | sentence | K1–K3 判定无容差：R2F 两次下降 0.268/0.359pp<一个优先级单位(~0.38pp)、8/10 配对 delta 恰 0.0、C3 在 0.9764vs0.9764 精确平局翻转 |
| R-17 | §4 / §6 | ✅ | Minor | section | EA 贡献被自数据否定：anchor 258/260 最优、例外恰 R1C seed100/105(+4.27/+4.63pp)；front_size=pop 233/260；search_only null 260/260 |
| R-18 | §6.1 / §6.2 | ✅ | Major | sentence | 摘要两成本在噪声量级：R2F 2.36pp 配对中位仅 **0.93pp**（40%）、CI 大幅重叠；R3H 4.15pp 方向稳健（配对 3.98pp，10/10 正） |

### Part C — 领域发现

| ID | 位置 | 核验 | Type | Cost | 简述 |
|----|------|------|------|------|------|
| R-19 | §3.1 L97 | 🟡 | Minor | sentence | 7578.05 m/s 是卫星惯性速度（非场景/足迹速度，ECEF 低 ~5–8%）；正文 L97 已明确披露口径，仅剩无敏感性分析 |
| R-20 | §2.1 L73 / §7.2 L355 | ✅ | Major | sentence | AASR 门槛从未绑定（30 manifest removals aasr=0）；方向对比对任何可行性判定无作用，且 §7.2 自认「不构成反驳」 |
| R-21 | §2.1 L73 vs §7.2 L355 | ✅ | Major | sentence | §2.1 称方向对比是「a result of this paper」，§7.2 却称「not a measurement that refutes the anchor」——限定应前置 |
| R-22 | §3.4 L164–173 / 摘要 | ✅ | Minor | sentence | 五约束族真正绑定的只有 C2 与 STR 地板（C1 生成侧、C3/C4「structurally never binding」L173、C5 是 raise 恒等式、AASR 移除 0） |
| R-23 | §7 L351 | ✅ | Editorial | sentence | 「cloud-cover attrition」对 X 波段 SAR 是范畴错误（从光学 EO 模板继承）；应改降雨/电离层/RFI 或删 |
| R-24 | §6.1 L266 | 🟡 | Editorial | sentence | 「no intermediate regime」与同句 R1C s=0.9=0.5398（一个中间覆盖值）字面矛盾；若 regime=连续机制则成立，措辞可更准 |

### Part D — 格式 / 引用 / 排版发现（审查附录 B）

| ID | 位置 | 核验 | Type | Cost | 简述 |
|----|------|------|------|------|------|
| R-25 | main.tex:5,14 | ✅ | Editorial | sentence | `\documentclass[review]{elsarticle}`(默认 numeric) 却配 `\bibliographystyle{elsarticle-harv}`；PDF 实排 `[16]` 数字引用 |
| R-26 | §3.4 L167 | ✅ | Editorial | sentence | `\citealt{kim2021optimal}` 在 numeric 模式打出完整作者串「Kim, Hongrae and Park, Joonil and … 16」（PDF 已确认） |
| R-27 | refs.bib | ✅ | Editorial | sentence | **307/307** author 字段双括号 `{{...}}`，参考文献作者名整串输出 |
| R-28 | refs.bib | ✅ | Editorial | sentence | 275 条 journal 字段中 **147** 条含 Google-Scholar 抓取残留（"… - Springer"/"… - Wiley Online Library"） |
| R-29 | refs.bib | ✅ | Minor | section | **280/307** bib 条目未被引用（27 被引）；与 P1-5 接最近文献合并处理 |
| R-30 | 摘要 | ✅ | Editorial | sentence | 摘要 **305 词**（审查说 284–286，我数 305）> AST 250 上限——超限成立，精确数差异不改结论 |
| R-31 | 图 1 | ⓘ | Editorial | figure | 面板标签用 `\footnotesize`（非审查说的「6 pt」）；偏小但具体点数未独立测准，视觉验收时复核 |
| R-32 | 图 3 L273 | ✅ | Editorial | figure | caption ~200 词；面板 (b) y 轴缩放 `[0.958,1.004]`（已确认）放大 0.3pp 噪声且排除 R3H |
| R-33 | 图 4 | ✅ | Editorial | figure | 三条水平线是构造必然（per-mode 常数按构造与斜视无关），信息量近零 |
| R-34 | §8 L399 | ✅ | Minor | sentence | Data availability「available from the corresponding author」与「可复现」第三贡献不匹配（待 Zenodo DOI，=台账 R42） |
| R-35 | cover_letter.md:38 | ✅ | Editorial | sentence | 单作者却写「All authors approve the submission」 |
| R-36 | 多处 \paragraph | ✅ | Editorial | sentence | run-in heading 双句点（PDF 渲染「retired..」「constant..」「scan..」等 15 处）——源已带句点 + class 自动补点 |

---

## Detail（核验证据随条携带；复算命令均可重跑）

### Part A — 阻断级

#### R-01 — 头条度量方向与标题错位　✅
- **审查主张**(B1)：摘要报告的 4.15/2.36 pp 是「没有放松到最松点」的代价，不是「收紧」的代价。同数据里收紧方向代价是 R3H 26.0/46.6 pp、R1C 46.0 pp。
- **核验**：✅ 成立。自 `sweep_results.json` 重算：R3H 1.0→0.9=26.01pp、1.0→0.8=46.58pp、vs 饱和(1.5)=−4.15pp；R2F 1.0→0.9=0.27pp、1.0→0.8=0.00pp、vs 饱和(2.0)=−2.36pp；R1C 1.0→0.9=46.02pp、vs 饱和=0.00pp。**头条 4.15/2.36 确为「订单点对饱和点」的差（放松方向的回看差）**。
- **对审查的修正（半）**：审查暗示全文方向反。**正文 §6.1(main.tex:262) 明确写了**「Tightening the order from the order point to the tightest point that still has a feasible individual costs about half of the served priority mass; loosening it … buys back under five points」，并点明「the side an operator would actually consider」。故**正文方向正确、摘要只挑了放松方向的小数字**——是**摘要/标题与正文的强调不一致**，非全文方向反。标题「The Coverage Cost of Tightening the Order」+ 摘要仅有的两个代价数字（4.15/2.36）会造成「收紧只花 4.15pp」的误读。
- **Type**: Major | **Cost**: section
- **建议动作**(→审查 P0-1)：摘要/§6.2/结论**双向报告**——明写 1.0→0.9 与 1.0→0.8 代价（R3H 26.0/46.6、R1C 46.0/不可行、R2F 0.27/0.00），4.15/2.36 改称「相对本族网格最大值的差/loosening premium」。
- **边界后果**：标题与摘要和实验对齐；不动数据。

#### R-02 — 「own saturation」基线是曲线自身 argmax　✅
- **审查主张**(B2)：基线是同一曲线在九点网格的 argmax，网格依赖；R1C 饱和点=订单点（代价恒 0）、R2F 在网格边界 s=2.0、R3H 平台与 s=1.4 只差 0.0018（一个优先级单位）。
- **核验**：✅ 成立。R1C 自 s=1.0 起中位全 1.0（饱和点=订单点，代价恒 0，**藏住 46.02pp 收紧代价**）；R2F argmax 在边界 s=2.0=1.0000；R3H 1.5 与 2.0 同 0.9900，与 1.4 的 0.9882 差 0.0018 = 1/Σpriority ≈ **一个优先级单位**（R3H Σpriority≈545）。正文 L279 自定义饱和点=「the first grid point at which its median reaches the family's maximum」——网格 argmax 属实。
- **Type**: Major | **Cost**: sentence（§6.2 措辞 + 饱和点敏感性一行）
- **建议动作**(→P0-1/P0-3)：披露饱和点的网格依赖性（尤其 R2F 在边界、R1C 退化）；或改用与网格无关的饱和定义。
- **边界后果**：基线稳健性透明化；不动数据。

#### R-03 — R1C s=0.8「不可行」是算术必然，带宽未披露　✅
- **审查主张**(B3)：R1C s=0.8 的「10/10 不可行」是 [2.5,3.0]m 粗档与 2.4669 m 地板的算术必然；带宽正文从未披露。
- **核验**：✅ 成立。R1C seed100 实测 20/20 STR；ρ_req∈[2.5049, 2.9999] m（粗档 [2.5,3.0]，源 `experiments/platform_kim2021.json` 与 `sss_core/scenarios.py:13`）；s=0.8 需 ρ≥2.4669/0.8=**3.0836**，实测 ρ_max=**2.9999** → **永远不可行**。正文对 `2.5`/`3.0 m` 带宽 **0 命中**（已 grep 全文）。
- **对审查的修正（半）**：正文 L283 已定性给机制（"the order at s=0.8 asks for a resolution finer than the stripmap floor the family is fixed to"）——**机制说明在，带宽数值缺**。审查的「改写为一行解析结论（0.8×3.0<2.4669）」是合理补数。
- **Type**: Major | **Cost**: sentence
- **建议动作**(→P0-2)：§5.1 披露 ρ_req 带宽 [2.5,3.0]m(粗)/[0.3,0.6]m(细) 与 STR 地板 2.4669 m；R1C s=0.8 改写为一行解析结论；该格从 K3 判定标为 undefined。
- **边界后果**：读者不看代码即可复算「为何 10/10 不可行」；不动数据。

#### R-04 — 族间混杂；R3H 机制未分解、地板排除占主导　✅
- **审查主张**(B4)：三族在任务数与模式构成上完全共变；R3H 收紧侧损失中 ~96%(1.0→0.8)/77%(1.0→0.9) 可由 STR 地板排除解释，非 dwell/transfer 机制。
- **核验**：✅ 成立（数字逐位命中）。R1C 20/20 STR、R2F 46–50/0 STR（16 SLS+30 SPT）、R3H 99–100/41–54 STR（seed300=54 STR+15 SLS+30 SPT）。自 30 个 R manifest 重算：R3H 非 STR 优先级份额中位 **0.5007**（s=0.8 上界），观测 0.4827（差 1.8pp）；s=0.9 上界 **0.7484**，观测 0.6884（差 6.0pp）；R1C s=0.9 上界 **0.5694**，观测 0.5398（差 3.0pp）。收紧损失 R3H 1.0→0.8=46.58pp 中地板上界解释 44.78pp=**96%**、1.0→0.9=26.01pp 中解释 20.01pp=**77%**——**地板排除占主导**，与 §6.3「spends dwell … collides with the transfer constraint」方向相反。
- **Type**: Major | **Cost**: restructure（新增模式分解表 + 重写机制段）
- **建议动作**(→P0-3)：加模式分解表（每 s 下 STR/SLS/SPT 的 served/dropped/优先级质量）；据此重写 §6.1/§6.3 机制段；若地板占比 >70%，标题与摘要改为「模式构成决定可行性」。
- **边界后果**：机制归因正确；表可由既有 artifacts 算出，不需新实验。

#### R-05 — C5「无违反」+ 477,308 是构造性/成员级重复计数　✅
- **审查主张**(B5)：C5 恒等式、「无违反」、477,308 是构造性/成员级重复计数（distinct 任务数为其 1/34.5），且对 STR 不成立。
- **核验**：✅ 成立。477,308 = 9,430 条 front 记录 Σ n_selected；distinct 任务（每单元最佳成员）= **13,845**；比值 **34.5×**。恒等式只对 SLS/SPT 检查（`sss_core/duration.py::_check_sls_delivery/_check_spt_delivery`），STR 无任务级参数（`task_rho_ach` 对 STR raise）——「无违反」对 STR 子集是空断言。正文 L322 有「not a distinct task」声明，但**摘要 L29 无**该限定。
- **Type**: Major | **Cost**: sentence
- **建议动作**(→P0-5)：摘要/结论删 C5「无违反」、477,308、R2F retention 100%；C5 改述为 per-mode delivery rule（SLS/SPT 等式；STR ≤ 订单、交付地板）；477,308 只留实现脚注并附 distinct 任务数。
- **边界后果**：交付量陈述与构造性事实分离；不动数据。

#### R-06 — 预注册不覆盖头条量　✅
- **审查主张**(B6a)：预注册不覆盖标题度量；own-saturation 代价随 2026-10-21 amendment 才登记，晚于 2026-10-20 的 L8 sweep。
- **核验**：✅ 成立。`analysis_prereg_v2.json` 原 freeze（git_head 1c598bc）主估计量是 `dq_all`/quality headroom + 预算梯 160/240；`amendment_20261021_ticket50_single_axis`（timestamp **2026-10-21**）才「REGISTERS the L8 main result（coverage–demand curve）」。RUN_LINEAGE 记 L8 曲线落地 **2026-10-20**。**amendment 晚于数据**。
- **对审查的修正（半）**：正文 L177/L248 已披露这是「registered as an amendment」——披露在，但**未披露时序**（amendment 晚于数据）。审查的「frozen/registered 不再修饰头条量」成立。
- **Type**: Major | **Cost**: sentence
- **建议动作**(→P0-6)：§3.5/§5.3/摘要精确化——「grid 与 K1–K3 预先登记；own-saturation 代价为 2026-10-21 amendment 后定义，属 post hoc descriptive」；amendment 时间与内容在正文可见。
- **边界后果**：纪律性主张与登记时序一致；不动数据。

#### R-07 — Table 1 R1C C3「met」依赖被禁约定　✅
- **审查主张**(B6b)：Table 1 的 R1C C3「met」依赖正文明确禁止的零覆盖约定。
- **核验**：✅ 成立（正文自带矛盾）。L287 明写 R1C tight-arm「met」"is a direct consequence of that convention: under an exclusion convention the tight cell would be undefined and the verdict would carry no value"；同页 L283 却写 infeasible「is not a coverage of zero, and the two must never be interchanged」。**自认依赖 + 自相矛盾**。
- **Type**: Major | **Cost**: sentence
- **建议动作**(→P0-4)：Table 1 改三值判定（met / not met / undefined）；R1C s=0.8 格标 undefined，C3 不再「靠约定成立的 met」。
- **边界后果**：判定与「infeasible≠0」纪律自洽；不动数据。

#### R-08 — f_Q,deliv 式 cos²ψ 方向与「squint-loss」命名　🟡
- **审查主张**(B7a)：p.14 印式 cos²ψ 方向反（应在分子，或按 C5 干脆不出现）；§6.5 把 1.3286>1 称作「squint-loss factor」，等于把 24.7% 损失印成 32.9% 增益；修正后 ≈28.3 而非 37.62。
- **核验**：🟡 半成立。**印式与注册口径自洽，非印错**——`formulas/formula-spec.md` §8.17-10 明确登记 `f_{Q,deliv}=D/(2ρ_req²cos²ψ_sel ρ_rg)`（「零斜视等效交付口径，保持 f_Q∝1/ρ_a² 恒等链形式」），实现 `build_reading_ledger_l8.py:519` 一致，且与正文 f_q 用零斜视分辨率的口径（L134/L138）自洽。审查的「cos²ψ 应在分子」是按 achieved-resolution 口径（与本篇零斜视口径不是一回事）。**但审查抓到真矛盾**：式使 f_Q,deliv 随斜视**增大**（sec²ψ 因子），§6.5 却把中位 sec²ψ=1.3286 称作「squint-**loss** factor」——**命名方向反**（实为 +32.9% 增益）；且「delivered」读数按 C5（交付=订单）本不该带 squint 依赖，多了个 sec²ψ。算数 37.62/1.3286=28.3 对。
- **真缺陷定性**：是**「squint-loss」命名方向反 + 「delivered」读数带多余 sec²ψ + caliber 语义混**，不是「印错公式」。
- **Type**: Major | **Cost**: sentence
- **建议动作**(→P0-8)：按 C5 把「delivered」口径改为 `f_Q,deliv=D/(2ρ_req²ρ_rg)`（交付=订单，无 squint 依赖），该格重算 37.62→≈28.3；1.3286 改称/删除；或保留零斜视等效口径但**改名**并去掉「loss」表述、在正文说清 caliber。
- **边界后果**：caliber 与命名一致；不动实验（delivered 是描述性读数）。

#### R-09 — SAT 展开错误　✅
- **审查主张**(B7b)：SAT 展开「saturation-avoidance time」错误；Kim 原文 = synthetic aperture time；且与本文「saturation arm」语义相撞。
- **核验**：✅ 成立（铁证）。`literature/fulltext/kim2021_aerospace_fulltext.txt:233-236`：「2.3. Synthetic Aperture Time … the synthetic aperture time (SAT) can be calculated …」；`saturat` 词根全文 **0 命中**。main.tex L71/L75/L122 均展开为「saturation-avoidance time (SAT)」。
- **Type**: Major | **Cost**: sentence
- **建议动作**(→P0-7)：SAT 改回「synthetic aperture time」；全文检索 `saturat` 清零；注意与本文「saturation arm（饱和臂）」措辞区分。
- **边界后果**：勘误级；不动数据。

#### R-10 — 「single-orbit」事实错误　✅
- **审查主张**(B7c/A.3-1)：R1C 跨 70.3–72.0 h（3 天）、145–162 窗、7.3–8.1 窗/任务，约 44–45 圈；且与 p.36「serial bound defined per pass, not per orbit」自相矛盾。
- **核验**：✅ 成立。R1C 窗跨度实测 **70.31–71.95 h**（≈3 天；两体周期 ≈23.93h/14.97≈1.6h → ≈45 圈）、窗数 **145–162**、窗/任务 **7.25–8.1**。main.tex 多处（L185/L236/L266/L385）称 R1C「single-orbit control」。
- **Type**: Major | **Cost**: sentence
- **建议动作**(→P0-7)：「single-orbit」→「sparse all-stripmap control」或「single-satellite control」（原意应为单星）。
- **边界后果**：事实标签正确；不动数据。

---

### Part B — 方法 / 统计

#### R-11 — 机动 hybrid 不连续非单调　✅
- **审查主张**(M-a)：hybrid 规则「解析值≥0.5×1.84 s 用解析值，否则退回 4.07 s」；0.50 s 机动计 4.07 s、0.95 s 计 0.95 s；锚点典型跃迁模型值 0.46 s 恰落 fallback 区。
- **核验**：✅ 成立。`sss_core/maneuver.py:79-80` `FALLBACK_MANEUVER_S=4.07`、`FALLBACK_TRIGGER_RATIO=0.5`；`anchor.py:384-385` 模型在典型跃迁(dψ≈6.45 mrad)=0.46 s < 0.5×1.84=0.92 → fallback 4.07 s。正文 L167 已披露 hybrid，但**未报 fallback 触发频率，未做 pad/settle/PRF/AASR 敏感性**。
- **Type**: Major | **Cost**: section
- **建议动作**(→P1-3)：连续化（如 max(analytic, floor) 或单一标定常数），或至少报告 fallback 触发频率 + 对 pad/settle/PRF/AASR 阈值做 one-at-a-time 敏感性。
- **边界后果**：C2（绑定约束）的 4.4× 跳变量化；可能需小量补算。

#### R-12 — 两个 Pearson 相关无效　✅（子主张 🟡）
- **审查主张**(M-b)：r=0.329(n=26) 去 R1C s=0.9 → −0.070；r=0.249(n=260) 压 30 场景均值 → 0.028；两者跨族合并违反自定口径；数字闸不覆盖。
- **核验**：✅ 脆弱性成立（逐位命中）。自 sweep_results.json 重算：r=0.3286(n=26)→去 R1C s=0.9 = **−0.0699**(n=25)；r=0.2495(n=260)→压 30 场景均值 = **0.0278**。`verify_paper_numbers_l8.py` 无 Pearson 路径（确认），闸不覆盖这两数。
- **对审查的修正（🟡）**：「直接违反 p.26『index levels are incomparable across families and are never pooled』」** overstated**——L242 禁的是 **raw f_q** 跨族合并，而相关用的是**归一化兑现率**（per-task ≤1，跨族可比）。**真问题是相关性脆弱（单点/聚合即塌）+ 闸不覆盖**，不是「违反自定口径」。
- **Type**: Major | **Cost**: sentence
- **建议动作**(→P1-4)：删 r=0.329/0.249，或改族内/场景级(n=10)并给 CI，并明确「不可与零区分」；把这两数补进数字闸或删。
- **边界后果**：撤掉不稳健的相关主张；不动数据。

#### R-13 — 最近 SAR 区域观测文献未引用　✅
- **核验**：✅ 成立。`liu2025a/shen2024multistrip/xin2024sar/li2026efficient`（另 liu2017an/wang2020robust）在 refs.bib 内、main.tex 引用均 **0**。
- **Type**: Minor | **Cost**: section（§2 接入 + 三列对比表）
- **建议动作**(→P1-5)：接入这 4 篇最近的 SAR 区域观测工作；加「duration 内生/外生、quality 定位、mode 固定/决策」三列表；软化「near-universal」(L79)。
- **边界后果**：接上最近先行工作。

#### R-14 — 场景种子=求解器种子，「10 seed=10 场景」　✅
- **核验**：✅ 成立。`run_matrix.py:341` 从 manifest 文件名解析 `seed_s` 直传 `run_pilot.py --seed`，`run_pilot.py:116` 进求解器。R2F 实收 46/48/49/50（10 个不同场景，非 10 次求解重复）。「场景抽样噪声」与「搜索随机性」设计上不可分离（每场景只跑一次求解）。
- **Type**: Major | **Cost**: new_data（子样本跑 3 个 solver seed）
- **建议动作**(→P1-1)：说明「seed=独立场景抽样」；至少在子样本上跑 3 个 solver seed 分离搜索噪声；正文「nine views of one world」限定到单 seed 内。
- **边界后果**：噪声来源可归因；需小量补算。

#### R-15 — 族规模常数是单 seed 取值　✅
- **核验**：✅ 成立。「46 admitted/99 admitted/342/753 窗」均为 seed 100/200/300 单次值；实测 R2F 46–50、R3H 99–100、窗 R1C 145–162 / R2F 337–391 / R3H 731–779。
- **Type**: Minor | **Cost**: sentence
- **建议动作**(→P1-2)：族规模改区间（R2F 46–50、R3H 99–100、R1C 145–162 窗等）；「2×99」改「2×N, N=99–100」。
- **边界后果**：单 seed 常数不再作族常量。

#### R-16 — K1–K3 判定无容差　✅
- **核验**：✅ 成立。R2F 两次「下降」0.268/0.359pp < 一个优先级单位（~0.38pp，实测 Σpriority 256–266 → 1 单位≈0.376–0.391pp）；8/10 配对 delta 恰 0.0，配对中位 0.0；C3 在 0.9764 vs 0.9764 **精确平局**翻转（中位不严格 < 即失败）。
- **Type**: Major | **Cost**: sentence
- **建议动作**(→P0-4)：用配对 per-seed delta 替代边际中位数；预定义容差（1 个优先级单位或配对 CI 排除 0）；Table 1 无「靠约定成立的 met」。
- **边界后果**：判定不随平局/亚单位噪声翻转。

#### R-17 — EA 贡献被自数据否定　✅
- **核验**：✅ 成立。anchor 258/260 最优；例外恰 R1C s=1.0 seed100(+4.27pp)/seed105(+4.63pp)——anchor 失手处，说明 anchor 是「best found」非「optimal」。front_size=pop(40) 在 **233/260**；`search_only_max_f1_star` 全 **260/260 为 null**（非测得空集）。
- **Type**: Minor | **Cost**: section
- **建议动作**(→P1-7)：EA 二选一——作方法贡献则补 R 族预算梯；作测量工具则压到 1–2 页并删 SBX/多项式变异细节。
- **边界后果**：不既称方法贡献又称其 258/260 不起作用。

#### R-18 — 摘要两成本在噪声量级　✅
- **核验**：✅ 成立。R2F 配对 per-seed delta(s2.0−s1.0) 中位 **0.93pp**（=头条 2.36 的 40%）；bootstrap：R2F s=1.0 95% CI [0.970,0.9958]、s=2.0 [0.9886,1.0] 大幅重叠。R3H 4.15pp 方向稳健（配对中位 3.98pp，10/10 场景为正）。
- **Type**: Major | **Cost**: sentence
- **建议动作**(→P1-1)：每点报 median [95% bootstrap CI]；主分析改配对 per-seed delta；摘要每个 pp 数带区间或配对统计量。
- **边界后果**：R2F 头条量级下修/带区间；R3H 保留。

---

### Part C — 领域

#### R-19 — 速度约定（惯性速度 vs 场景/足迹速度）　🟡
- **审查主张**(D-c/F5)：7578.05 m/s 是卫星惯性速度非场景速度，ECEF 足迹速度低 4.8–5.0%，逐任务占用率偏移 1.5–3.5%（与头条同量级）；披露了但无敏感性。
- **核验**：🟡 半成立。**正文 L97 已明确披露**：「inertial scene velocity v_s=7578.05 m/s. This is the platform inertial velocity, registered as the scene-traversal velocity … rather than the beam-footprint ground velocity」，并说明覆盖读数继承该约定。我粗算：纯曲率地面速度 ≈6956 m/s（−8.2%），含自转约 −5%（审查的 7220–7229 量级可信但模型相关）。**真缺口=无敏感性分析**；「名不副实」略苛（正文命名其实清楚）。
- **Type**: Minor | **Cost**: sentence
- **建议动作**(→P1-3)：补一行敏感性（v_s 取足迹速度时覆盖/驻留偏移量级）；称谓与口径保持一致。
- **边界后果**：绝对驻留数的系统偏移被量化。

#### R-20 — AASR 门槛从未绑定　✅
- **核验**：✅ 成立。30 个 R manifest 的 generation_ledger removals 合计 `aasr=0, footprint=0, below_finest=0, no_window=15`（R1C 0 + R2F 10 + R3H 5）——**AASR 门槛在全部已发布场景中未移除任何任务**。§7.2 L355 自认方向对比「establishes a difference of registered model behavior, not a measurement that refutes the anchor」。
- **Type**: Major | **Cost**: sentence
- **建议动作**(→P0-7)：§2.1/摘要说明 AASR 门槛在已发布场景中未绑定（removals aasr=0）；把 §7.2 的「该对比不构成反驳」前置到 §2.1。
- **边界后果**：方向对比的解释力被正确界定。

#### R-21 — §2.1「a result of this paper」与 §7.2 自否认张力　✅
- **核验**：✅ 成立。§2.1 L73 称方向对比「is a result of this paper rather than a contradiction to be smoothed over」；§7.2 L355 却称「not a measurement that refutes the anchor」且「no experiment in this paper discriminates the two steering semantics」。
- **Type**: Major | **Cost**: sentence
- **建议动作**(→P0-7)：把 §7.2 的限定（不构成反驳、无判别实验）前置到 §2.1，使 §2.1 自带对该对比的限定。
- **边界后果**：前后表述一致，不 overstated。

#### R-22 — 五约束族真正绑定的只有 C2 与 STR 地板　✅
- **核验**：✅ 成立。C1 生成侧窗口过滤；C3/C4「structurally never binding」（L173 自认）；C5 是 raise 恒等式；AASR 移除 0（R-20）。真正绑定的只有 C2 与 STR 地板。
- **Type**: Minor | **Cost**: sentence
- **建议动作**：摘要/§3.4 说明这是**单约束排程序**（C2 + STR 地板），而非「五约束调度器」；或至少在 §3.4 明确各约束的绑定状态。
- **边界后果**：约束复杂度表述诚实。

#### R-23 — 「cloud-cover attrition」对 X 波段 SAR 是范畴错误　✅
- **核验**：✅ 成立。§7 L351「no cloud-cover attrition」——SAR 穿透云层，云非 SAR 质量因子（光学 EO 模板继承）。
- **Type**: Editorial | **Cost**: sentence
- **建议动作**(→审查 §3.3)：删或改降雨/电离层/RFI 等 SAR 相关环境。
- **边界后果**：scope 清单领域正确。

#### R-24 — 「no intermediate regime」字面矛盾　🟡
- **核验**：🟡 半成立。§6.1 L266 同句先给 R1C s=0.9=0.5398（一个中间覆盖值），再说「there is no intermediate regime for it to occupy」。字面矛盾；若「regime」=连续中间机制（R1C 是阶跃非连续）则成立。
- **Type**: Editorial | **Cost**: sentence
- **建议动作**：改「无连续中间机制」或「无中间取值区间」，避免字面矛盾。
- **边界后果**：措辞精确。

---

### Part D — 格式 / 引用 / 排版

#### R-25 — class 与 bibliographystyle 冲突　✅
- **核验**：✅ 成立。`\documentclass[review]{elsarticle}`（默认 numeric）+ `\bibliographystyle{elsarticle-harv}`；PDF 实排 `[16]` 数字引用（已用 PyMuPDF 确认 `[16]` 存在）。
- **Type**: Editorial | **Cost**: sentence
- **建议动作**(→P0-9)：统一为 harv（`\documentclass[authoryear,review]{elsarticle}`）或明确 numeric，并同步 writing-config。

#### R-26 — `\citealt` 打印完整作者串　✅
- **核验**：✅ 成立。L167 `\citealt{kim2021optimal}` 在 numeric 模式 + 双括号作者字段下打出「Kim, Hongrae and Park, Joonil and Chang, Young-Keun and … 16」（PDF 已确认）。
- **Type**: Editorial | **Cost**: sentence
- **建议动作**：改 `\citep`/`\citet` 或移除 alt 类命令（与 R-25/R-27 联动）。

#### R-27 — 307/307 author 字段双括号　✅
- **核验**：✅ 成立。refs.bib **307/307** 条 `author = {{...}}`，导致作者名以整串（Firstname Lastname and …）输出，natbib 无法解析 first/last。
- **Type**: Editorial | **Cost**: sentence（批量去双括号 + 拆 `and`）
- **建议动作**：去双括号、逐条拆分 `and`（与 R-26 联动）。

#### R-28 — 147/275 journal 字段含 Scholar 残留　✅
- **核验**：✅ 成立。275 条 journal 字段中 **147** 条含「 - Springer」「 - Wiley Online Library」「 - mdpi.com」等抓取残留（如 liu2025a、xin2024sar）。
- **Type**: Editorial | **Cost**: sentence（批量清洗）
- **建议动作**：逐条清洗 journal 字段（修回扩充文献时会带入）。

#### R-29 — 280/307 bib 条目未被引用　✅
- **核验**：✅ 成立。总 307 条、被引 **27**、未引 **280**。
- **Type**: Minor | **Cost**: section
- **建议动作**：与 R-13（接最近文献）合并——保留将引的，清减纯凑数条目。

#### R-30 — 摘要 305 词 > AST 250 上限　✅
- **核验**：✅ 超限成立。我数 **305**（p1 240 + p2 65；审查说 284–286，计数法差异，均 >250）。
- **Type**: Editorial | **Cost**: sentence
- **建议动作**(→P0-9)：压到 ≤250 词，保留 1 个头条数 + 1 句 scope（与 R-01 双向报告联动）。

#### R-31 — 图 1 面板标签字号　ⓘ
- **核验**：ⓘ 部分。图 1 TikZ 源用 `\footnotesize`（非审查说的「6 pt」）；elsarticle[review] 下 footnotesize ≈10pt 量级。**「6 pt」具体值未独立测准**；偏小问题可在视觉验收复核。
- **Type**: Editorial | **Cost**: figure
- **建议动作**：视觉验收时判读实际渲染尺寸，必要时提到 ≥8pt（采模型读图，按 2026-10-15 裁决）。

#### R-32 — 图 3 caption 冗长 + y 轴缩放放大噪声　✅
- **核验**：✅ 成立。`plot_fig3_coverage_vs_requirement.py:141` `axz.set_ylim(0.958, 1.004)`；caption（L273）~200 词；面板 (b) 截断至 [0.958,1.004] 放大 0.3pp 噪声且不含 R3H。
- **Type**: Editorial | **Cost**: figure
- **建议动作**(→P1-6)：缩 caption；面板 (b) 纳入 R3H 收紧侧（断轴）或图注写出 46.6pp。

#### R-33 — 图 4 三条平线是构造必然　✅
- **核验**：✅ 成立。per-mode 常数按构造与斜视无关（squint 因子在 g_T 内相消，L138），三条平线是构造必然非发现。
- **Type**: Editorial | **Cost**: figure
- **建议动作**(→P1-6)：删平线图，换 delivered-resolution 或 data-volume 的可用读数。

#### R-34 — Data availability「from the corresponding author」　✅
- **核验**：✅ 成立。L399「available from the corresponding author」，与「可复现」第三贡献不匹配。
- **Type**: Minor | **Cost**: sentence
- **建议动作**：Zenodo/figshare DOI + hash（=台账 R42，待用户 DOI 串，见 handoff）。

#### R-35 — cover letter「All authors approve」（单作者）　✅
- **核验**：✅ 成立。`cover_letter.md:38`「All authors approve the submission」。
- **Type**: Editorial | **Cost**: sentence
- **建议动作**：改单数（"The author approves …"）。

#### R-36 — run-in heading 双句点　✅
- **核验**：✅ 成立。`\paragraph{... .}` 源已带句点，elsarticle class 自动再补点 → PDF 渲染「retired..」「constant..」「scan..」等 **15 处**。
- **Type**: Editorial | **Cost**: sentence（批量去 \paragraph 尾句点）
- **建议动作**：去 `\paragraph` 标题尾句点，统一为单句点。

---

## 审查中被我判为 overstated / 有误导的子主张（不单独列项，随条标注）

1. **B1「全文方向反」**——正文 §6.1 已正确给收紧方向（"costs about half"），问题只在摘要/标题强调（见 R-01）。
2. **B7a「印在纸上的式子错了」**——印式与其注册口径逐字一致（见 R-08）；真缺陷是命名方向反 + caliber 语义混。
3. **M-b「违反自定 no-pooling 口径」**——该口径禁 raw f_q 合并，相关用的是归一化兑现率（见 R-12）；真问题是相关性脆弱。
4. **D-c「速度名不副实」**——正文 L97 命名与披露其实清楚（见 R-19）；真缺口是无敏感性。
5. **B-6 摘要词数**——审查 284–286 vs 我数 305；**均 >250，超限结论不变**（见 R-30）。

## 未发现审查「不成立」项

本批 36 项中，**0 项经复算被判 ❌ 不成立**。审查的承重数字（26.01/46.58/46.02pp、0.5007/0.7484/0.5694、477,308→13,845、r 0.3286→−0.0699、SAT 定义、预注册时序）全部逐位复现。其「Major Revision」裁决有充分证据支撑。
