# paper2 投稿操作清单 — Acta Astronautica

**状态**：包已冻结，W7 终闸机械部分全绿（留档 `goal-w2w7/gates/w7_final_regate_after_title_affiliation.txt`）。
选题 A 定稿 + 作者块补齐已完成。**投稿动作由你本人在 Editorial Manager 完成。**

## 一、投稿文件（全部在 `papers/sliding-spotlight-scheduling/paper/`）

| EM 表单要求的件 | 本仓文件 | 备注 |
|---|---|---|
| Manuscript（主稿） | `main.pdf`（38 页）或 `main.tex` + `refs.bib` + `figures/` | AST 通常要 pdf 供审、源文件录用后收。建议两者都备 |
| Cover Letter | `cover_letter.md` | 已含定稿标题；需转 pdf 或纯文本粘贴 |
| Highlights | `highlights.md`（5 条，均 ≤83 字符） | EM 表单逐条填入 |
| Declaration of Competing Interest | `declaration.md` | 已含 "no specific grant" Funding 段 |
| CRediT authorship | `credit.md` | 单作者全角色 |
| Suggested reviewers | **需你填** | 见下方第三节 |

`figures/` 需随源文件一并上传：`fig3/4/5/6/7_*.pdf`（5 张数据图）+ `fig1_modes_geometry.tex` + `fig2_scheduling_loop.tex`（2 张 TikZ，靠 `\input` 引入，缺了编译不过）。

## 二、EM 表单元数据（照抄即可）

- **Title**：`Agile Sliding-Spotlight SAR Satellite Scheduling with Mode-Determined Dwell Duration and an Image-Quality Objective`
- **Authors**：`Liu Shuhao`
- **Corresponding email**：`liushuhao@hrbeu.edu.cn`
- **Affiliation**：`College of Intelligent Systems Science and Engineering, Harbin Engineering University`
- **Address**：`145 Nantong Street, Nangang District, Harbin 150001, China`
- **Article type**：Research Paper / Full Length Article（AST 的 VSI 常规栏目）
- **Keywords**：直接从 `main.tex` 的 `\begin{keyword}` 块取（5 项，勿改——它们是 W6 钉值）

## 三、需要你决定、我无法代填的

1. **推荐审稿人 3-6 名 + 回避名单**。这是 AST 的常规要求，属编辑裁量。建议只推荐真正读过本文核心文献（Song 2025 的 AASR、Kim 2021 的滑动聚束几何）方向的人。
2. **是否投 VSI（特刊）**。普通栏目即可；若你已知某个对口的特刊可选。
3. **Data availability 声明**。独立审层的 MINOR-4 曾建议在 W6 承载一条 90/90 指针，当时裁决为「此处不承载」。投稿表单会问，你需要决定写什么（现在稿内无独立 Data Availability 段落）。

## 四、投稿前最后三项自检（你点上传前做）

1. **pdf 页数与图表**：38 页、7 图全部在位（已验）
2. **标题五处一致**：`main.tex` / `highlights.md` / `cover_letter.md` / `credit.md` / `declaration.md`（已验，零残留旧标题）
3. **refs.bib 三条缺页码**：`mittermayer2003sliding`、`caleiras2026a`、`wang2024research` 无 page 字段，bibtex 报 3 个 `empty pages` warning。不影响审稿，但编辑部排版时会来找你补。建议投稿前顺手补上。

## 五、已知的、已裁决不动的（勿在投稿前临时改）

- 论文如实报告**负结果**：90 个单元无一 promotion（max spread 3.9722 dB vs 冻结 6.0 dB 阈值），front-collapse 读数已作为搜索伪影撤回。这是预注册纪律的一部分，不是缺陷。
- 主检验报**双 p**（t=24.78，单侧 p≈3e-16，置换 p=1e-5），prereg 要求。
- 容量法则**只有 per-pass 口径、无数字**——B15/E3 注册义务使然，不是遗漏。
- 运行层**无实测数据**（R3 席曾判 CRITICAL，裁决为 wont_address：promoted 工件无计时字段，新跑违反取数纪律），已用 §7.1 scope 句对冲。
