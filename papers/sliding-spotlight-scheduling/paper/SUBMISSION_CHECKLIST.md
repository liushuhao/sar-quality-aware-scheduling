# paper2 投稿操作清单 — Aerospace Science and Technology (AST)

**状态**：票 50 全链完成（阶段三·A/B 改写 + 阶段四终检 + 阶段五终审处置），2026-10-21 全量门禁绿（红闸 0/1076、L8 数字闸 136 项 0 mismatch【两稿面各 68，阶段五扩至逐句全数】、预注册闸 28 项 0 失败、版式闸 0 FAIL、编译两遍 48 页 0 error 0 未定义引用、域套件 papers + src rc=0）；本文件随稿同步（旧定位条目已清）。
**投稿动作由你本人在 Editorial Manager 完成。**

## 一、投稿文件（全部在 `papers/sliding-spotlight-scheduling/paper/`）

| EM 表单要求的件 | 本仓文件 | 备注 |
|---|---|---|
| Manuscript（主稿） | `main.pdf`（46 页，elsarticle `preprint` 单倍行距，2026-10-29 压缩波批0/批1 后编译物）+ `main.tex` + `refs.bib` + `figures/` | 现行 AST 指南要求**可编辑源文件**（"A PDF is not an acceptable source file"）——EM 传 LaTeX 源码组，由 EM 自建审稿 PDF；另需每位作者 100 词内简介 + 证件照（随图上传） |
| Cover Letter | `cover_letter.md` | 已含定稿标题；需转 pdf 或纯文本粘贴 |
| Highlights | `highlights.md`（5 条，最长 83 字符） | EM 表单逐条填入 |
| Declaration of Competing Interest | `declaration.md` | 已含 "no specific grant" Funding 段 |
| CRediT authorship | `credit.md` | 单作者全角色 |
| Suggested reviewers | **需你填** | 见下方第三节 |

`figures/` 需随源文件一并上传（2026-10-28 R96 图面扩展波更新）：六张数据图 PDF `fig2_dwell_mechanism.pdf`、`fig4_scenario_set.pdf`、`fig5_coverage_vs_requirement.pdf`（原 fig3_ 改名）、`fig6_construction_probes.pdf`、`fig7_dwell_distribution.pdf`、`fig8_counterfactual.pdf` + 两张 TikZ `fig1_modes_geometry.tex`、`fig3_scheduling_loop.tex`（原 fig2_ 改名；靠 `\input` 引入，缺了编译不过）；`fig3_quality_vs_squint.pdf` 不被正文引用，不需上传。

## 二、EM 表单元数据（照抄即可）

- **Title**：`Resolution-Driven Scheduling of Agile SAR Satellite: From Fixed to Endogenous Imaging Dwells`
- **Authors**：`Liu Shuhao`
- **Corresponding email**：`liushuhao@hrbeu.edu.cn`
- **Affiliation**：`College of Intelligent Systems Science and Engineering, Harbin Engineering University`
- **Address**：`145 Nantong Street, Nangang District, Harbin 150001, China`
- **Article type**：Research Paper / Full Length Article（AST 的 VSI 常规栏目）
- **Keywords**：直接从 `main.tex` 的 `\begin{keyword}` 块取（6 项，勿改——它们是 W6 钉值）

## 三、需要你决定、我无法代填的

1. **推荐审稿人 3-6 名 + 回避名单**。这是 AST 的常规要求，属编辑裁量。建议只推荐真正读过本文核心文献（Song 2025 的 AASR、Kim 2021 的滑动聚束几何）方向的人。
2. **是否投 VSI（特刊）**。普通栏目即可；若你已知某个对口的特刊可选。
3. **Data availability 声明**。主稿末尾已有 Data availability 段（指向 promoted artifacts、预注册文件、口径登记与验证脚本）；投稿表单若另问，照该段口径填。

## 四、投稿前最后三项自检（你点上传前做）

1. **pdf 页数与图表**：46 页（preprint 单倍行距；2026-10-29 压缩波：批0 排版切换 + fig2/fig8 图面修复 + 批1 纯压缩 ≈-1 页，Table 1 已删——其内容由 §2.4 散文完全承载）、8 图（Fig1/Fig3 TikZ + Fig2/4/5/6/7/8 数据图）全部在位；编译零 error、零未定义引用；视觉验收 2026-10-29 三轮闭环 8/8 PASS（fig2 地板标注冲突、fig8(b) 图例/基线标注/(a)标签三处修复后复判过）。**关于 AST 指南「<35 页」**：劝导性条款、无强制后果；本稿单倍行距 46 页（约 22,000 词）——进一步压缩受 L8 数字闸静默丢失守卫与 T55/IGN 片段钉限制（§6.7/§3.2/§6.5/§7.1 的读数句为历轮波次刻意钉入的检查面），投稿前不再压缩。
2. **标题五处一致**：`main.tex` / `highlights.md` / `cover_letter.md` / `credit.md` / `declaration.md`。
3. **[2026-10-24 已失效]** `caleiras2026a` 现有 `pages = {110--121}`，此条不再适用，bibtex 报 1 个 `empty pages` warning（阶段五实测：`mittermayer2003sliding` 有 `pages = {1462-1464}`、`wang2024research` 有 `pages = {328--332}`）。不影响审稿，但编辑部排版时会来找你补。建议投稿前顺手补上。

## 五、本版已裁决、勿在投稿前临时改

- 主结果是**覆盖率–需求曲线**（三族 × 九点需求网格）：R3H 订单点代价 4.15 个百分点、R2F 2.36 个百分点，均对各自饱和值；R1C 最紧点十种子全部 exit-11 = **无可行解**，不是「覆盖 0」（图与文分开画、分开写）。
- 三条形状判据**如实在报**：R1C/R3H 全过，R2F 两条不过（单调、紧臂），判据不因数据改判。
- 质量索引降为**平台能力 + 报告读数**（兑现率，带三part 口径标签），不进目标函数；覆盖是唯一目标。
- 容量法则**只有 per-pass 口径、无数字**——注册义务使然，不是遗漏。
- 运行层**无实测计时数据**，已用 §7.1 的范围句对冲。
