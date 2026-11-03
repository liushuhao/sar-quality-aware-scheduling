# 异源回扫任务书 — paper1 2026-11-01 改稿批次

## 你的身份与红线（先复述再开工）

你是只读审查席，模型家族与施工席不同。开工前，把下面五条红线**原文复述**到报告开头，缺任一条视为未通过验收：

1. 只读：不得修改、创建、删除仓库中任何文件（唯一例外是你自己的报告 `findings.md`）。
2. 不得发明数字：报告里每个数字必须来自你实际读到的文件内容，或你实际运行的命令输出。
3. 不得把"我检查过了"当证据：每条发现必须给 `file:line` + 引用原文或命令输出。
4. 不确定就写"未验证"，不许猜。
5. 不得建议删除论文中的诚实限定（Limitations 中的适用范围声明），本批任务只是压缩冗余，不是删免责。

## 背景（自包含，不需要会话历史）

论文：`papers/single-sat-quality/small-paper-ijae.tex`（英文）与 `small-paper-ijae-zh.tex`（中文），
单星敏捷 SAR 卫星三目标调度。本次改稿做了四件事：

1. 第 6.4 节（帕累托压缩机制）与 6.6 节（鲁棒性与校准）大幅压缩文字，改为引用两张新图；
2. 新增图 `figures/fig7_corr_density.pdf` 与 `figures/fig8_controls.pdf`
   （生成脚本 `scripts/gen_fig7_fig8.py`）；
3. 摘要、引言结果段、贡献列表、结论重排叙事：把"多目标在高密度饱和失效"从主贡献降为适用边界，
   头条改为"稀疏区可量化的质量收益 + 适用包络"；
4. 中英双语同步，删掉 41 处破折号连接与 19 处 "rather than" 句式。

## 你的任务（逐条执行，逐条回证据）

### 任务 A：数字与数据源一致性（最重要）

下列数值出现在正文，请到数据文件核对。允许两位小数误差只在明确舍入时成立。

| 正文数值 | 位置 | 数据源 |
|---|---|---|
| 变体 A 在 S1 的排程内相关 −0.62；S2 −0.15；S3 −0.13；S4 −0.23 | §6.4 | `experiments/results/schedule_correlation.json` → `variants.A_full_physics.<class>.r` |
| 变体 B/C/D 在 S1 为 −0.23 / −0.65 / −0.13 | §6.4 | `experiments/results/schedule_correlation_ablation.json` → `variants.<name>.S1.r` |
| 包络相关 −0.36（S1 −0.35，S2–S3 −0.37）；置换零假设 −0.60 | §6.4 | `experiments/results/null_new_caliber2026.json` → `r_envelope` / `r_shuffle_null_mean` |
| 随机初始化覆盖亏损 S1–S4 = −0.393/−0.551/−0.684/−0.475，SD 0.251/0.060/0.050/0.067 | §6.6 | `experiments/results/p1-1_random_init/hotstart_control_s1s4.json`（random.f1 − hot.f1 的均值/SD） |
| 随机搜索平均 0.527、90 分位 0.930、最优 1.000 | §6.6 | `experiments/results/p1-2_random_search/p1-2_s1_random_search.json` → `results.*.f1_star_mean / f1_star_p90 / f1_star_best` |
| 随机初始化变体 D：S3 调度 70.3 个、S4 117.8 个；热启动 154.5 / 142.7 | §6.6 与图 8(d) | `experiments/results/variant_d_random_init/full.json` → `results.S3/S4[].n_selected`；`experiments/results/moea_3obj_no_physics/_progress.json` → `completed` 里 S3/S4 的 `n_selected` 均值 |

要求：逐行给出 你的复算值 vs 正文值。任何不一致按"须修"报出。

### 任务 B：图与图注一致性

- 打开 `figures/fig7_corr_density.png` 与 `figures/fig8_controls.png`（可读图）。
- 核对：图注描述的每个元素（面板数量、误差棒含义、样本量 n、参考线）在图里是否确实存在；
  图上曲线数与正文所讲变体数是否一致。
- 核对图 8(d) 的柱高是否与任务 A 里 70.3 / 117.8 / 154.5 / 142.7 吻合（柱形按比例即可，不需精确）。

### 任务 C：中英镜像

- `small-paper-ijae.tex` 与 `small-paper-ijae-zh.tex`：
  统计 `\section{`、`\subsection{`、`\begin{figure`、`\begin{table` 数量是否相同；
  两版是否都含 `fig7_corr_density.pdf` 与 `fig8_controls.pdf`；
  两版是否都含字符串 `-0.62`（若一版还在用 `-0.63` 即不改，按须修报出）。

### 任务 D：残留的防御性写作与 AI 味

在英文稿里逐项计数并给行号：
`---`（正文中的破折号，不含注释行）、`rather than`、`not an artifact`、
`should be read`、`Phenomenon`。
判断标准：正文里的破折号（`---`）应为 0；`rather than` 若属真实技术对比（例如
"rather than an absolute NESZ ranking"）不算问题，只报纯粹修辞性的（把否定半句删掉意思不变的）。

### 任务 E：编译产物

运行（只读命令，允许）：

```
cd papers/single-sat-quality
python -c "import fitz; d=fitz.open('small-paper-ijae.pdf'); print(len(d))"
python -c "import fitz; d=fitz.open('small-paper-ijae-zh.pdf'); print(len(d))"
grep -c "^!" small-paper-ijae.log small-paper-ijae-zh.log
```

英文应为 47 页、中文 37 页、错误行为 0。不符合按须修报出。

## 回传格式

报告写到 `papers/single-sat-quality/review/cross-review-20261101/findings.md`，结构：

```
## 红线复述
（五条，原文）

## 发现
| # | 严重度 | 位置 | 问题 | 证据（引用/命令输出） | 建议 |
（严重度只用三档：须修 / 建议 / 观察）

## 已核未发现问题
（任务 A–E 中检查通过的部分，各一行，附复算值）

## 未验证范围
（明确列出你没能力或没时间验证的部分）
```

最终消息里给：发现总数、须修数、以及一句结论（通过 / 不通过）。
