> Reviewed by: workbuddy (论小舟 / thesis-writing-mentor) · thesis-workflow v1.3.0 · 2026-08-01

# 单星 SAR 质量感知调度小论文 — 全面审查报告（v7 / Workbuddy）

## 0. 范围与方法

- **对象**：用户对"第三章"（即 `small-paper-ijae-zh.tex` 中文版 / 全文）的改稿后的**中英双版全文** + `experiments/results/` 下数据 + 历史审查状态。
- **技能路由**：`thesis-workflow` v1.3.0（已按 entry_rule 加载）；读取 `always_load`：`foundation-and-state.md`、`academic-integrity-and-source-policy.md`、`quality-checklist.md`。
- **方法**：(1) 通读英文全文（1204 行）与中文全文关键段；(2) 对 `experiments/results/` 下 JSON/CSV 做对抗性复算（HV、Friedman、N50、包络相关、效应量、S4/S1 比）；(3) 对齐 `REVIEW_INDEX.md` 与 trae v9 综合报告，区分"本轮新发现"与"历史 carry-over"。
- **目标期刊**：Elsevier *Advances in Space Research*（ASR），已按 ASR/elsarticle 模板排版。

---

## 1. 结论先行（最重要风险）

1. **核心论文正文（英文投稿版）无 P0、无 P1。** RDR-002（f2–f3 "+0.93~+0.98 反转"不可复现）已闭环；所有核心数值主张经独立复算与数据一致。
2. **用户本轮"第三章"改稿已修复此前中文版专属缺陷**：符号冲突（𝒮 同指平台/选定集）、HV 归一化自相矛盾、HV 图孤儿引用、p_i 取值范围、离轴角 φ→ξ——均已落实（见 §2）。
3. **本轮新发现（均为 P2）**：中文版 L744 的「S4/S1 超体积比 <1」论断在英文版缺失（中英漂移）；`sec:hv-divergence` 标签仅中文版存在；`r_visible_envelope.json` 仍残留已作废的 `r_solver_empirical=[0.93,0.98]` 且 note 逻辑自相矛盾（与 trae v9 的 P2-Repro-1/2 互相印证）。
4. **整体就绪度：`needs_author_input`**（非 blocked、非 ready_to_submit）。阻塞项为 carry-over，不在论文正文：GitHub 需重新推送（D01）、trae v9 的两个代码 P0、数据卫生清理（V7-N3）。

---

## 2. 用户改稿落地核验（此前中文版缺陷 → 本轮已解决）

| 历史 ID | 问题 | 本轮核验证据 | 状态 |
|---|---|---|---|
| W-C02 | 花体 𝒮 同指"卫星平台"与"选定任务集" | zh L212–213：`𝒫` 指平台、`(𝒯,𝒫,𝒪)`；L243/248/258/270 `𝒮` 指选定集。与英文一致 | **VERIFIED_DONE** |
| W-C01 | HV 归一化同句自相矛盾（"每求解器池化" vs "所有求解器池化"） | zh L484–486：仅"每求解器池化"，无"所有求解器池化"残留；与英文 per-solver 口径一致 | **VERIFIED_DONE** |
| W-C03 | HV 图成孤儿（中文 fig:fig4 零引用） | zh L575：`如图~\ref{fig:fig4} 所示`（标签 L572）。引用存在，非孤儿 | **VERIFIED_DONE** |
| G5 | p_i 取值范围论文写 {5..10}，实为 {1..10} | zh L605：`p_i` drawn uniformly from the integer set `{1,2,…,10}` | **VERIFIED_DONE** |
| H11 | 离轴角 φ 符号过载（φ_i 纬度 vs φ 离轴） | zh L227：`ξ = arctan2(√(l_x²+l_y²), l_z)`，off-nadir 已改 ξ | **VERIFIED_DONE** |

> 说明：上述 5 项均为前序批次（v5/v8）标记为 fixed 的中文版问题；本轮独立读文件确认已真正落地，非仅停留在批注层。

---

## 3. 中央主张对抗性复算（全部一致，evidence-backed）

| ID | 主张 | 论文位置 | 数据来源（证据指针） | 结论 |
|---|---|---|---|---|
| C-D01 | HV 池化 MOEA-3 0.173/0.045；MOEA-2 0.169/0.037；G-BL 0.140/0.017 | tab:hv (L724–726 / zh 表) | solver_summary.csv 池化≈0.1728/0.1686/0.1401 | ✓ 一致 |
| C-D02 | Friedman χ²=506.56, p≈10⁻¹⁰⁸ | L1047–1048 | statistical_results.json：506.56 / 2.55e-108 | ✓ 一致 |
| C-D03 | N50≈140, CI [117,169] | L824–828 | n50_logistic.json：139.62 / [117.4,168.5] | ✓ 一致 |
| C-D04 | 包络相关 ≈−0.95；窗口对 ≈3.9×10⁵ | L936–938 | r_visible_envelope.json：r_c7 S1−S4 = −0.9622/−0.9549/−0.9524/−0.9517；c7 总对=393,974 | ✓ 一致 |
| C-D05 | r_null=−0.51；r_MC=−0.5120 | L895–899 | r_visible_envelope.json + 蒙特卡洛 | ✓ 一致 |
| C-D06 | A 调度内 r：−0.69→−0.17；D：−0.44→−0.18 | L916–919 / zh L720–721 | RDR-002 人工重跑（variant_d_per_task_r.json） | ✓ 一致（冲突减弱非反转） |
| C-D07 | MOEA-2 vs G-BL f2 δ=+0.55, p<10⁻³³ | L1019 | effect_sizes.json：MOEA-2_f2_vs_GBL_f2 = 0.545 / 1.44e-34 | ✓ 一致 |
| C-D08 | G-SM f3 δ=+0.72；MOEA2 vs MOEA3 δ=+0.132/−0.176 | L754 / L876–877 | effect_sizes.json（GSM_f3 0.72；MOEA2_f2 0.132；MOEA2_f3 −0.176） | ✓ 一致 |
| C-D09 | S4/S1 HV 比 <1 | zh L744（英文无，见 V7-N1） | solver_summary.csv：MOEA-2 0.146539/0.202343=**0.724**；MOEA-3 0.146798/0.217549=**0.675** | ✓ 论断为真 |
| C-D10 | 变体 D S1 反超 Δ=−22.1%, p=3.3e-7 | L107–108 / tab:ablation | ablation_summary.csv + tab:ablation | ✓ 一致 |
| C-D11 | 随机热启动 f1* 缺口 0.20–0.46 | L53 / L973–974 | robustness 节（10 S1/4 S2/5 S3/5 S4 实测） | ✓ 一致 |

---

## 4. 本轮新发现（P2）

### V7-N1 · 中英漂移：S4/S1 超体积比论断仅中文版存在
- **位置**：zh L744「在 S4（N=500），帕累托前沿的超体积比（S4/S1）小于 1」；英文版 grep `S4/S1`/`HV ratio`/`hypervolume ratio` **无任何匹配**。
- **证据**：solver_summary.csv 复算 S4/S1 = 0.724（MOEA-2）、0.675（MOEA-3），均 <1 → **论断本身为真**。
- **风险**：(a) 中英双版不同步；(b) 该论断在论文内**无对应表格/图支撑**——正文 tab:hv 为 200 场景池化 HV，未给逐密度 HV；读者无法从文中直接核到 S4/S1 比。
- **严重度**：P2（双语同步 + 报告完整性）。
- **解决条件**：二选一——英文版补等效论述（镜像中文），或中文版删除以对齐英文；若保留，建议在尺度敏感性节补一个逐密度 HV 小表或脚注给出证据指针。
- **状态**：TODO_AUTHOR_CONFIRM。

### V7-N2 · 中英漂移：`sec:hv-divergence` 标签/引用仅中文版存在
- **位置**：zh L694 `\label{sec:hv-divergence}`（L625 引用）；英文版无此标签/引用（统一用 `sec:pareto-coupling`）。
- **证据**：两版均编译通过（标签自洽、无断链），属小节锚点命名差异。
- **严重度**：P2（极低读者风险，仅维护/交叉引用一致性）。
- **解决条件**：定稿时统一锚点命名；当前不阻断。
- **状态**：P2（可选对齐）。

### V7-N3 · 数据卫生：`r_visible_envelope.json` 残留已作废常量且 note 逻辑自相矛盾
- **位置**：`experiments/results/r_visible_envelope.json` L3–6 `r_solver_empirical=[0.93,0.98]`；L239 note「r_visible_c7 ~= r_solver (0.93)」。
- **证据**：读文件确认。`r_visible_c7 = −0.95`（负），而 `r_solver_empirical=[0.93,0.98]`（正）——note 的"≈"逻辑在 RDR-002 作废 "+0.93" 框架后已成**符号错误残留**。`f2_f3_coupling.json` 虽标 `_deprecated` 仍在 results/（trae v9 P2-Repro-2 同判）。
- **风险**：论文正文已不使用该值（改用 r_null=−0.51 / r_c7≈−0.95），故**不影响读者可见结论**；但若审稿人/复算者检查原始数据，矛盾 note 可能引发疑问。
- **严重度**：P2（数据卫生，非论文正文错误）。
- **解决条件**：在 JSON 中标注 `# DEPRECATED: see RDR-002` 或直接删除 `r_solver_empirical` 并修正 L239 note；`f2_f3_coupling.json` 移至 archive/ 或加 README 说明。
- **状态**：TODO_AUTHOR_CONFIRM（修改数据文件需作者授权；我可在你确认后直接编辑）。

### V7-N4 · 中文版图标签键名与文件名/英文版错位（历史 deferred 确认仍存）
- **位置**：zh 标签 HV=fig:fig4、squint=fig:fig1、scale=fig:fig5、Pareto=fig:fig2、ablation=fig:fig6（英文为 fig:fig1–fig:fig5 顺序）。
- **证据**：zh 主文件 4 个 `\label{fig:}` + 消融输入 `\label{fig:fig6}`；全部 `\ref` 解析一致、无重复 label、无断链（编译通过）。
- **严重度**：P2/P3（纯维护隐患）。
- **说明**：此为 V6-F03 / Qwen L8 已**裁决不改**项（改动有断链风险、零读者收益）。本轮确认仍处该状态，**不重复建议修改**。
- **状态**：deferred（定稿清理时再对齐，当前无需动作）。

---

## 5. 历史 carry-over（非本轮新发现，仍开放）

| ID | 问题 | 严重度 | 状态 | 来源 |
|---|---|---|---|---|
| D01 | GitHub 仓库需重新推送：pushed_at=2026-07-22 早于本轮改稿；Data Availability Statement 指向该仓库 | P1（投稿就绪） | needs_author_input | REVIEW_INDEX / WB D01 |
| v9-P0-Code-1 | `src/tools/check_numerical.py` L6 路径构造用原始字符串而非 Path 运算，脚本无法运行 | P0（代码/验证工具） | pending-author | trae v9 §4.2 |
| v9-P0-Code-2 | `src/tools/check_refs.py` L4 同上，且 `docs/` 前缀过时 | P0（代码/验证工具） | pending-author | trae v9 §4.2 |
| v9-P1-Code-1/2/3 | moea.py f1_gbl 传参 BUG；地球半径常量不一致（6,378,137 vs 6,371,000）；HotStart 随机种子未固定 | P1（代码） | pending-author | trae v9 §4.3 |
| v9-P1-Data-1 | 消融变体 D 的 f1_raw 绝对值建议在表/正文显式给出 | P1（报告完整性） | pending-author | trae v9 §3.4 |
| v9-P2-Repro-1/2 | 同 V7-N3（已归并） | P2 | pending-author | trae v9 §3.6 |

> 注：v9 的两个**代码 P0** 不触及论文正文科学结论，但影响复算/验证工具可用性；投稿前建议修复。论文正文本身不因代码脚本缺陷而失效。

---

## 6. 质量门禁（thesis-workflow quality-checklist 终检）

- [x] 目标/类型/章节/语言/规范明确（ASR 英文投稿版 + 中文同步版）
- [x] 用户材料、期刊要求、已核验来源、模型建议、待核验项已区分
- [x] 一句话主论点、论证地图、章节契约一致（经验饱和区：稀疏多目标有增益、密集三目标冗余、热启动条件性）
- [x] 术语/符号/分析单位前后一致（𝒫/𝒮 已统一；θ/ψ_sq 耦合叙事闭环 RDR-002）
- [x] 文献身份/DOI 未猜测；M1/M2/F 分层；25 条 bib 全部被引（历史批次已核验）
- [x] 主张—证据—位置可追溯（§3 核验清单）
- [x] 未编造样本量/p 值/实验参数
- [x] 图表含编号/标题/单位/来源/统计说明（5 图 + tab:hv/tab:ablation/tab:scale-sensitivity 等）
- [x] 原始数据→处理数据→正文主张可追溯（§3 复算通过）
- [x] 改写未新增事实/数据/来源
- [x] 正文引文与参考文献双向对应
- [x] 无 P0（论文正文）、无诚信/伦理/合规失效项
- [~] 投稿材料就绪度：GitHub 重推（D01）+ 代码 P0（v9）待作者处理

---

## 7. 整体就绪度判定

**`needs_author_input`**

- 论文正文（英文投稿版）：✅ 无 P0/P1；所有核心数值经独立复算与数据一致；RDR-002 已闭环。
- 阻塞项均在正文之外，需作者动作：
  1. **D01** GitHub 重新推送（保证 Data Availability Statement 准确）；
  2. **V7-N1 / V7-N2** 中英漂移，作者决定对齐方向；
  3. **V7-N3** 数据文件卫生清理（我可授权后直接改）；
  4. **v9 代码 P0/P1** 投稿前修复复算工具。

---

## 8. 低负担下一步

**建议作者先处理 D01（GitHub 重推）+ V7-N3（JSON 卫生）**——两者都不需要重写论文，却是投稿/复算链路上的"脏数据"风险点；中英漂移 V7-N1/N2 可在定稿一轮统一。

如需，我可在你确认后：
- 直接编辑 `r_visible_envelope.json`（删 `r_solver_empirical` + 修正 note）与归档 `f2_f3_coupling.json`；
- 在英文版补 S4/S1 HV 比论述或在中文版删除，使双版一致。

---

> 本审查不替代导师、领域方法专家或期刊编辑判断；不承诺录用、查重结果或答辩结果。所有"fixed/VERIFIED_DONE"均基于本轮可读产物与可定位数据，未做本地重放（本机无 pymoo/sar_sim）。
