# paper2 投稿操作清单 — Aerospace Science and Technology (AST)

**状态**：票 50 全链完成（阶段三·A/B 改写 + 阶段四终检 + 阶段五终审处置），2026-10-21 全量门禁绿（红闸 0/1076、L8 数字闸 136 项 0 mismatch【两稿面各 68，阶段五扩至逐句全数】、预注册闸 28 项 0 失败、版式闸 0 FAIL、编译两遍 48 页 0 error 0 未定义引用、域套件 papers + src rc=0）；本文件随稿同步（旧定位条目已清）。
**投稿动作由你本人在 Editorial Manager 完成。**

## 一、投稿文件（全部在 `papers/sliding-spotlight-scheduling/paper/`）

| EM 表单要求的件 | 本仓文件 | 备注 |
|---|---|---|
| Manuscript（主稿） | `main.pdf`（48 页）或 `main.tex` + `refs.bib` + `figures/` | AST 通常要 pdf 供审、源文件录用后收。建议两者都备 |
| Cover Letter | `cover_letter.md` | 已含定稿标题；需转 pdf 或纯文本粘贴 |
| Highlights | `highlights.md`（5 条，最长 82 字符） | EM 表单逐条填入 |
| Declaration of Competing Interest | `declaration.md` | 已含 "no specific grant" Funding 段 |
| CRediT authorship | `credit.md` | 单作者全角色 |
| Suggested reviewers | **需你填** | 见下方第三节 |

`figures/` 需随源文件一并上传：`fig3_coverage_vs_requirement.pdf`、`fig3_quality_vs_squint.pdf`（2 张数据图）+ `fig1_modes_geometry.tex`、`fig2_scheduling_loop.tex`（2 张 TikZ，靠 `\input` 引入，缺了编译不过）。

## 二、EM 表单元数据（照抄即可）

- **Title**：`Agile Sliding-Spotlight SAR Satellite Scheduling with Per-Task Resolution Requirements: The Coverage Cost of Tightening the Order`
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

1. **pdf 页数与图表**：48 页、4 图全部在位；编译零 error、零未定义引用（本次重编译实测）。
2. **标题五处一致**：`main.tex` / `highlights.md` / `cover_letter.md` / `credit.md` / `declaration.md`。
3. **refs.bib 一条缺页码**：`caleiras2026a` 无 page 字段，bibtex 报 1 个 `empty pages` warning（阶段五实测：`mittermayer2003sliding` 有 `pages = {1462-1464}`、`wang2024research` 有 `pages = {328--332}`）。不影响审稿，但编辑部排版时会来找你补。建议投稿前顺手补上。

## 五、本版已裁决、勿在投稿前临时改

- 主结果是**覆盖率–需求曲线**（三族 × 九点需求网格）：R3H 订单点代价 4.15 个百分点、R2F 2.36 个百分点，均对各自饱和值；R1C 最紧点十种子全部 exit-11 = **无可行解**，不是「覆盖 0」（图与文分开画、分开写）。
- 三条形状判据**如实在报**：R1C/R3H 全过，R2F 两条不过（单调、紧臂），判据不因数据改判。
- 质量索引降为**平台能力 + 报告读数**（兑现率，带三part 口径标签），不进目标函数；覆盖是唯一目标。
- 容量法则**只有 per-pass 口径、无数字**——注册义务使然，不是遗漏。
- 运行层**无实测计时数据**，已用 §7.1 的范围句对冲。
