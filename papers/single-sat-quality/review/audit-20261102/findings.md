# paper1 检查报告 — 2026-11-02（文字与图片专项）

审查对象：`papers/single-sat-quality/` 当前 HEAD（9a3514b）+ 工作树。
方式：既有闸实跑 + 逐图判读 + 正文/数据/脚本三方对账。本报告只读审查阶段的产出。

## 一、既有闸实跑结果

| 检查 | 命令 | 结果 |
|---|---|---|
| 数字闸 | `python src/tools/verify_paper_numbers.py`（cwd=仓库根） | 204 断言 / 0 失败，CALIBER OK |
| 英文编译 | `small-paper-ijae.log` | 0 错误 / 0 未定义引用 / 0 缺字；overfull 2；47 页 |
| 中文编译 | `small-paper-ijae-zh.log` | 0 错误 / 0 未定义引用 / 0 缺字；overfull 3；字体警告 2；38 页 |
| 结构镜像 | 计数对比 | 章节 8/8、小节 25/25、图 7/7、表 6/6 |
| 图号 | PDF 全文扫描 | 印刷图 1–7 连续，无悬空引用（fig7→图 6、fig8→图 7） |
| 高亮 | 字符计数 | 78/75/84/82，上限 85 |
| 后置件 | 人工比对 | AI 声明、CRediT、资助、declaration 与正文一致 |

## 二、必改（F 系列）

### F1 图 3 底部拟合的样本集与正文不符，且 N50/CI 三处不一致

- 正文（`small-paper-ijae.tex:1056-1061`，`small-paper-ijae-zh.tex:756-758`）声明：拟合用六个密度点
  （N=20,100,150,200,300,500）、300 个场景，得 N50≈50、CI [30,62]。
- 图 3 的实际拟合只用 200 个"五求解器齐全"的场景（N=20/100/300/500）；
  代码：`experiments/gen_all_figures.py:139-150` 的 `common_keys` 要求 5 个求解器齐备，
  S7/S8 无 GA-P-BL / MOEA-3，被排除；`experiments/gen_all_figures.py:614-678` 直接对这批点拟合并自举。
  图内标注：N50≈51、95% CI [38,62]。
- 数据文件 `experiments/results/n50_logistic.json` 生成于 2026-08-10；其输入
  `moea_2obj/_progress.json` 已在 2026-08-15（commit 58f07cc）重生成。当前数据重算：
  **N50=50.8、CI [37,64]**（`python scripts/n50_logistic.py` 实跑输出）。
- 数字闸 `src/tools/verify_paper_numbers.py:317-321` 把硬编码常数（50.0 / 30.0 / 62.0）与 JSON 比对，
  **从不读正文**——正文写 80 也照样过。属"审计工具自比自"盲区。

处置：单一真源 = `scripts/n50_logistic.py` 的六类拟合；图 3 改为读该 JSON 并画六类散点；
正文（中英）数值更新；闸改为解析正文数值再与 JSON 比对。

### F2 图 4 图例压住两个面板的 x 轴标题

- `experiments/gen_all_figures.py:377-378`：`fig.legend(..., loc='lower center', bbox_to_anchor=(0.5,-0.02))`。
- `save_publication_figure` 用 `bbox_inches='tight'`（`:30`），画布由设计 4.28 in 扩到 4.81 in；
  插入为 `0.75\textwidth`=4.05 in 后再缩 16%，图例文字实际 5.5 pt。
- 视觉证据：`.remember/tmp/fig4_bottom_zoom.png`（图例横穿 "f1* (Norm. Profit)"）。

处置：图例移入画布内（轴上方或面板内），或为图例预留底部边距后按 4.05 in 出图；重出后复测字号。

### F3 消融图（`fig5_ablation.pdf`，印刷为图 6）第二面板 y 轴标题与第一面板标题相撞

- `experiments/gen_fig6_ablation.py`（实际产出图）三行面板共享左缘；第二行 y 标签 "f2 degradation (%)"
  的 "f2" 压到第一行标签 "%" 上。
- 视觉证据：`.remember/tmp/fig5_left_zoom.png`。

处置：改用 `fig.supylabel` 或在 `subplots_adjust(left=…)` 加宽左缘；重出后复测。

### F4 消融图内注与图注的显著性阈值不一致

- 图内文字："* paired Wilcoxon vs A, p < 0.005 (Bonferroni threshold)"
- 图注（EN `sections/_ablation_section.tex:110` / ZH `:99`）：`p<0.05/12`（=0.00417）。

处置：图内改为 `p < 0.05/12`，与图注同一表达式。

### F5 摘要与结论的密度阈值互相矛盾

- 摘要（`small-paper-ijae.tex:49`，`small-paper-ijae-zh.tex:50`）："vanishes at operational densities (N ≥ 300)"。
- 结论（`small-paper-ijae.tex:1529`，`small-paper-ijae-zh.tex:1083`）："vanishes … beyond N ≈ 150"。
- 贡献列表（`:171`）、高亮、cover letter 均写 150。

处置：待用户裁决（见 fix-plan Q1）。

## 三、建议（S 系列）

| 编号 | 问题 | 证据 |
|---|---|---|
| S1 | 中文稿缺 3 条英文稿有的一级引用：`Deb2002NSGA2`（zh:213）、`Zitzler1999HV`（zh:218）、`DasDennis1998`（zh:497） | 引用键差集 |
| S2 | 中文稿缺 `\label{sec:introduction}`、`\label{sec:moea-description}`（台账 R111） | label 计数 37 vs 35 |
| S3 | 论文用 `fig5_ablation.pdf`，生成脚本只写 `fig6_ablation.*`，靠人工复制同步 | `gen_fig6_ablation.py:221` |
| S4 | `fig6_ablation.{pdf,png}` 是 fig5 的同字节副本，且未被 git 跟踪、无任何 tex 引用 | md5 相同 |
| S5 | `fig1–4` 的 grayscale PNG 停留 2026-07-24，图已在 11-01 重画 | 文件时间戳 |
| S6 | `IQR` 全文无全称；`SD` 在 `:857` 先用、`:898` 才给 "standard deviation" | 全文检索 |
| S7 | 投稿包 `ASR-submission-20260923-r2.zip` 早于 11-01 改稿 | zip 内文件时间 |
| S8 | 图按 5.7 in 设计，实际 `\textwidth` = 5.40 in（整体缩 5%）；基础字号仍 ≥6.16 pt | PyMuPDF 量测 |

## 四、未跑过的检查（建议补）

1. 11-01 大改后未跑 ARS 五席模拟审稿（上次面板 10-31，早于改稿）。
2. 项目 CLAUDE.md 的三轮自查（归属 / 新人 / 减法）在新叙事后未重跑。
3. 文献元数据复核上次为 08-18。
4. 图注逐元素回源只做了目视，未程序化。
5. 若目标刊要求灰度或 300 dpi TIFF，需重出图件。
