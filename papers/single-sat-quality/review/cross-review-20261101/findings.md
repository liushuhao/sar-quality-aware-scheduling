# 异源回扫报告 — paper1 2026-11-01 改稿批次

审查对象（按字节实测，非按任务书推测）：

| 文件 | 字节 | mtime |
|---|---|---|
| `small-paper-ijae.tex` | 98,730 | 2026-11-01 17:38:39 |
| `small-paper-ijae-zh.tex` | 88,969 | 2026-11-01 17:38:48 |
| `small-paper-ijae.pdf` | 979,141 | 2026-11-01 17:38:53 |
| `small-paper-ijae-zh.pdf` | 608,517 | 2026-11-01 17:38:56 |

**版本漂移声明**：我在 17:36 首次读取 `small-paper-ijae.tex` 时该文件为 98,684 字节，图 8(d) 图注当时写作
"...random initialization (mean and SD over 15 runs per class)"，未区分热启动柱的样本口径；17:38 的版本已改为
"under greedy hot-start (class mean over the 50 scenarios) and random initialization (mean and SD over 15 runs per class)"。
本报告全部行号与结论均基于上表 17:38 的字节，不基于 17:36 的旧版。

---

## 红线复述

1. 只读：不得修改、创建、删除仓库中任何文件（唯一例外是你自己的报告 `findings.md`）。
2. 不得发明数字：报告里每个数字必须来自你实际读到的文件内容，或你实际运行的命令输出。
3. 不得把"我检查过了"当证据：每条发现必须给 `file:line` + 引用原文或命令输出。
4. 不确定就写"未验证"，不许猜。
5. 不得建议删除论文中的诚实限定（Limitations 中的适用范围声明），本批任务只是压缩冗余，不是删免责。

---

## 发现

### 任务 A：数字与数据源一致性

| # | 严重度 | 位置 | 问题 | 证据（引用/命令输出） | 建议 |
|---|---|---|---|---|---|
| A-1 | 建议 | `small-paper-ijae.tex:1112-1113`（zh:794） | 零假设散布写作"±0.02"，实测最大半宽仅 0.013 | `null_new_caliber2026.json`：S1 p025/p975 = −0.617/−0.591（半宽 0.013）、S2 −0.624/−0.610（0.007）、S3 −0.620/−0.609（0.006）、S4 −0.613/−0.607（0.003）。原文："95\% spread $\pm 0.02$ across 20 shuffles per class" | 改为 "$\pm 0.01$" |
| A-2 | 建议 | `small-paper-ijae.tex:1112`（zh:794） | "within each density class gives $r_{\text{null}} = -0.60$" 对 S2/S3 不成立 | 同文件逐类 `r_shuffle_null_mean`：S1 −0.602、S2 −0.615、S3 −0.615、S4 −0.609；两位小数下 S2/S3 应为 −0.62 | 改为 "$-0.60$ to $-0.62$" 或直接给四类区间 |
| A-3 | 建议 | `small-paper-ijae.tex:176`（zh:137）；摘要 `:54`（zh:54） | 贡献列表写"dilutes to $-0.2$ to $-0.15$"，与 §6.4 三值不符；摘要写"$-0.15$ at high density"，而最密类 S4 为 −0.23（趋势非单调） | §6.4 `:1135`："$-0.15$, $-0.13$, $-0.23$ at S2--S4"；数据 `schedule_correlation.json` S2 −0.1523 / S3 −0.1262 / S4 −0.2290。−0.13 与 −0.23 均落在 $[-0.2,-0.15]$ 之外 | 贡献列表改 "$-0.13$ to $-0.23$ at S2--S4"；摘要改 "dilutes to $r\approx-0.13$ to $-0.23$ at S2--S4" 或明确"至 S3 最弱、S4 回弹" |
| A-4 | 建议 | `small-paper-ijae.tex:1277-1279`（zh:930-931） | "all 10 sweep scenarios reach the ceiling" 与同句 199.5 自相矛盾 | `sigma_sweep/sweep_summary.json`，moea_3obj / S3 / σ=0.7：`n_selected_mean 199.5`, `n_selected_std 0.7`, `n 10`。10 次均值 199.5 且 SD 0.7 时不可能全为 200 | 改为 "199.5 at $\sigma=0.7$ (9 of 10 at the ceiling)" 或删掉后半句 |
| A-5 | 观察 | `small-paper-ijae.tex:1177-1178`（zh:846） | "pooled within-schedule $f_2$ SD is $0.16$ at S1--S3"，S2 实为 0.1684，两位小数应为 0.17 | `schedule_correlation_ablation.json` A_full_physics `f2_std`：S1 0.16395、S2 0.16841、S3 0.15835、S4 0.13819；`f2_range` 0.6488/0.6533/0.6533/0.6458（"range 0.65 in every class" 成立） | 改 "0.16--0.17" 或逐类给出 |
| A-6 | 观察 | `small-paper-ijae.tex:1302-1303`（zh:949-950） | 热启动 154.5/142.7 与随机初始化 70.3/117.8 的样本口径不同：前者 50 个场景，后者 5 场景×3 种子=15 次 | `moea_3obj_no_physics/_progress.json` `completed` 300 条，S3/S4 各 50 条 → 154.50/142.68；`variant_d_random_init/full.json` `params`：`n_scenarios 5, n_seeds 3`，S3 15 次均值 70.27、S4 117.80 | 数字本身无误；建议在图注或正文注明热启动侧为"全类 50 场景均值"，或改用同一 5 场景子集重算 |
| A-7 | 观察 | `small-paper-ijae.tex:742` 与 `:1135` | 两处都写"变体 A"，数值却不同（−0.80/−0.23/−0.15/−0.31 vs −0.62/−0.15/−0.13/−0.23），易被读成矛盾 | `:741-742`："restricted to variant A ... (pooled per-task $r$: $-0.80$, $-0.23$, $-0.15$, $-0.31$)" 来自 `schedule_correlation_a_only.json`（`n_schedules` 每类 10，S1 `r` −0.7980）；`:1135` 来自全类 50 条排程（`schedule_correlation.json`，S1 −0.6228）。两组数各自正确 | 在 `:741-743` 明写"10 variant-A schedules per class"，避免与 §6.4 的 50 条口径混淆 |

**任务 A 逐行复算 vs 正文值（任务书表格 6 行，全部一致）**

| 正文数值 | 位置 | 数据源复算值 | 判定 |
|---|---|---|---|
| A：−0.62 / −0.15 / −0.13 / −0.23（S1–S4） | en:1135 | −0.62283 / −0.15228 / −0.12615 / −0.22902 | 一致 |
| B/C/D 在 S1：−0.23 / −0.65 / −0.13 | en:1167-1172 | −0.22550 / −0.65446 / −0.13345 | 一致 |
| 包络 −0.36（S1 −0.35，S2–S3 −0.37） | en:1143 | 逐类 −0.355 / −0.371 / −0.370 / −0.360（四类均值 −0.364 → −0.36） | 一致 |
| 置换零假设 −0.60 | en:1112, 1117 | −0.602 / −0.615 / −0.615 / −0.609 | 一致（精度问题见 A-1/A-2） |
| 随机初始化亏损 −0.393/−0.551/−0.684/−0.475，SD 0.251/0.060/0.050/0.067 | en:1258-1259 | `summary`：−0.39256/−0.55103/−0.68361/−0.47535，SD 0.25112/0.05969/0.04994/0.06700 | 一致 |
| 随机搜索 0.527 / 0.930 / 1.000 | en:1287-1288 | 5 场景 `f1_star_mean` 均值 0.526996（跨场景 SD 0.002997）、`p90` 均值 0.929934（SD 0.007484）、`best` 全 1.0 | 一致 |
| 变体 D：随机 70.3/117.8；热启动 154.5/142.7 | en:1302-1303；图 8(d) | 70.267 / 117.800；154.500 / 142.680 | 一致（口径见 A-6） |

### 任务 B：图与图注一致性

| # | 严重度 | 位置 | 问题 | 证据（引用/命令输出） | 建议 |
|---|---|---|---|---|---|
| B-1 | 建议 | 图 7（`figures/fig7_corr_density.png`；图注 `small-paper-ijae.tex:1154-1162`，zh:829-833） | 图里有一条未入图例、图注也未描述的灰色点线（零假设均值），读者无法判读 | `scripts/gen_fig7_fig8.py:94`：`ax.plot(xs, nl_mu, color='0.35', lw=0.8, ls=(0, (1, 1)))`——无 `label=`；同段 `:92` 的 band 有 label。PNG 中该点线位于 r≈−0.60 处 | 图注补一句"点线为零假设均值"，或给该线加图例项 |

其余元素全部吻合，列入"已核未发现"。

### 任务 C：中英镜像

| # | 严重度 | 位置 | 问题 | 证据（引用/命令输出） | 建议 |
|---|---|---|---|---|---|
| C-1 | 建议 | `small-paper-ijae-zh.tex` 正文 32 行、共 41 处 `——` | 破折号清理只落在英文稿：英文正文 `---` = 0，中文仍有 41 处破折号对 | 英文：脚本统计 `---` 于非注释行为 0（唯一残留见 D-2 的 `--`）。中文：`:68, :84, :95, :171, :181, :182, :197, :219, :342, :362, :388, :391, :417, :483, :537, :547, :566, :593, :594, :688, :707, :961, :963, :990, :1009, :1026, :1027, :1030, :1031, :1033, :1047, :1104`，累计 41 | 按英文稿同一标准改写为逗号/括号/分句 |
| C-2 | 建议 | `small-paper-ijae-zh.tex:858` | 重复字：`各求解器的膝点最大化自身的目目标和` | 原文引："由于各求解器的膝点最大化自身的目目标和（\S~\ref{sec:evaluation-metrics}）" | 改"目标和" |
| C-3 | 观察 | `small-paper-ijae-zh.tex:56, 73, 176, 275, 472, 488, 758, 845, 1084` | 中文正文使用 ASCII 直引号 `"..."` 共 10 处 | 例 `:56`：`任务规划者可将这两条边界读作"质量感知 SAR 调度何时值得付出覆盖率代价"的定量判据。` | 统一为中文引号 |
| C-4 | 观察 | `small-paper-ijae-zh.tex:65, 187` vs `small-paper-ijae.tex:68, 188` | 中文稿缺 `\label{sec:introduction}` 与 `\label{sec:moea-description}` | `\label` 计数：en 34、zh 32；差集恰为这两个。但 zh 无对应 `\ref`，两版 PDF 文本 `??` 计数均为 0，无破损引用 | 无害；若后续要复用锚点再补 |
| C-5 | 观察 | `small-paper-ijae-zh.tex:68` vs `small-paper-ijae.tex:72` | 同一句一处用破折号插入语、一处用括号，镜像不一致 | en:72 `Their agility (the ability to slew the antenna beam away from the nadir track)`；zh:68 `其敏捷性——天线波束偏离星下点轨迹的能力——` | 与 C-1 一并统一 |

**任务 C 计数核对（两版一致）**

| 计数项 | en | zh |
|---|---|---|
| `\section{` | 8 | 8 |
| `\subsection{` | 24 | 24 |
| `\begin{figure` | 6 | 6 |
| `\begin{table` | 5 | 5 |
| `\includegraphics` | 6 | 6 |
| 含 `fig7_corr_density.pdf` | 是（1 次） | 是（1 次） |
| 含 `fig8_controls.pdf` | 是（1 次） | 是（1 次） |
| `-0.62` 出现次数 | 3（`:53, :175, :1135`） | 3（`:53, :136, :813`） |
| `-0.63` 出现次数 | 0 | 0 |

### 任务 D：残留防御性写作与 AI 味（英文稿）

| # | 严重度 | 位置 | 问题 | 证据（引用/命令输出） | 建议 |
|---|---|---|---|---|---|
| D-1 | 建议 | `small-paper-ijae.tex:139` | 纯修辞性 `rather than`：删掉否定半句语义不变 | 原文："The gain is bounded by two conditions that we measure rather than assume." | 改"The gain is bounded by two conditions that we measure." |
| D-2 | 建议 | `small-paper-ijae.tex:420` | 正文残留一个被空格包围的 `--`（与 `---` 同类的插入破折号），任务书的 `---` 计数为 0 但问题未清干净 | 原文："a relative ordering index across observation geometries, not as an absolute radiometric prediction -- the comparisons in \S\ref{sec:evaluation-metrics} and below depend only on the ordering it induces." | 改为冒号或括号 |
| D-3 | 建议 | `small-paper-ijae.tex:736` | 防御性否定框架 `not an artifact`，紧接的 `:737-742` 已给出正面证据（变体 A 子集 +37.2%/+3.5%/+0.4%/+0.3%） | 原文："The trend is likewise not an artifact of the class-specific geometry variants: restricted to variant A ..." | 直接以正面陈述开头（"The trend survives restriction to variant A ..."） |

**任务 D 逐项计数（非注释行）**

| token | 次数 | 行号 |
|---|---|---|
| `---` | **0** | —（要求达成） |
| `rather than` | **30** | 139, 242, 251, 297, 359, 375, 393, 427, 438, 441, 465, 489, 564, 569, 602, 614, 661, 769(×2), 831, 835, 891, 1328, 1354, 1373, 1393, 1404, 1434, 1445, 1452, 1474 |
| `not an artifact` | **1** | 736 |
| `should be read` | **2** | 426, 1473 |
| `Phenomenon`（大写） | **0** | — |
| `phenomenon`（小写） | **1** | 1027 |

判断：30 处 `rather than` 中 29 处属真实技术对比（含任务书点名的 `:427` "rather than an absolute NESZ ranking"），仅 `:139` 为纯修辞。
`should be read` 两处（`:426` "so $f_3$ should be read as a geometry proxy"、`:1473` "the threshold should be read as ..."）属诚实限定，**按红线 5 不建议删除**，仅记录。

### 任务 E：编译产物

| # | 严重度 | 位置 | 问题 | 证据（引用/命令输出） | 建议 |
|---|---|---|---|---|---|
| E-1 | **须修** | `small-paper-ijae-zh.pdf` | 页数 38，任务书要求 37 | `python -c "import fitz; d=fitz.open('small-paper-ijae-zh.pdf'); print(len(d))"` → `38`；英文侧同命令 → `47`（符合）。zh tex 在 17:38:48 被改动、PDF 17:38:56 重编译，晚于任务书基线 | 二选一：把 zh 压回 37 页，或确认 37 已过期并更新任务书验收值。在此之前该验收项不通过 |

**任务 E 其余输出**

| 检查 | 结果 |
|---|---|
| 英文页数 | 47（要求 47）✓ |
| 中文页数 | 38（要求 37）✗ |
| `^!` 错误行 | en 0 / zh 0 ✓（逐行 `startswith('!')` 统计，非 grep 猜测） |
| `Undefined control sequence` | en 0 / zh 0 |
| `LaTeX Warning: Reference/Citation` | en 0 / zh 0 |
| PDF 文本中 `??` | en 0 / zh 0 |
| Overfull \hbox | en 2（log 行 10--13、58--105）；zh 3（435--446、800--810、47--94） |
| 字体警告 | zh 2 条：`Font shape 'TU/SimSun(0)/m/it' undefined`、`TU/SimSun(0)/b/n undefined` |

---

## 已核未发现问题

**任务 A（逐行复算，全部通过）**

- 变体 A 排程内相关：数据 −0.62283 / −0.15228 / −0.12615 / −0.22902 vs 正文 −0.62 / −0.15 / −0.13 / −0.23（`en:1135`）——逐位吻合。
- 变体 B/C/D 在 S1：数据 −0.22550 / −0.65446 / −0.13345 vs 正文 −0.23 / −0.65 / −0.13（`en:1167-1172`）——吻合。
- 变体 D 在 S2 −0.07：数据 −0.07439（`en:1172`）——吻合。
- 包络相关：四类 −0.355/−0.371/−0.370/−0.360，均值 −0.364 → 正文 −0.36；S1 −0.35、S2–S3 −0.37（`en:1143`）——吻合。
- 逐排程均值 −0.72 / −0.15 / −0.16 / −0.18：数据 −0.71940 / −0.15175 / −0.15475 / −0.18156（`en:1136`）——吻合。
- Fisher-z 均值 −1.09 / −0.16 / −0.16 / −0.19：数据 −1.09092 / −0.15891 / −0.16033 / −0.18597（`en:1136-1137`）——吻合。
- S1 单排程跨度 [−0.97, −0.03] 且全负：数据 `per_schedule_min` −0.96688、`max` −0.02608，50 条无一为正（`en:1138`）——吻合。
- 随机初始化覆盖亏损四值与四 SD（`en:1258-1259`）——见任务 A 表，逐位吻合；样本量 10/4/5/5×3 = 30/12/15/15 与 `summary.n` 一致，亦与图 8(a) 图注 `n=30,12,15,15` 一致。
- 同段 f2 对比：0.5046 vs 0.3945（+27.9%→"+28%"）、0.4600 vs 0.3196（+43.9%→"+44%"）、0.3492 vs 0.3386（+3.1%→"+3%"）、0.3473 vs 0.3800（−8.6%→"−9%"）（`en:1263-1265`）——四舍五入全部成立。
- 随机搜索：0.527 ± 0.003 / 0.930 ± 0.008 / 1.000（`en:1287-1288`）——复算 0.526996 ± 0.002997 / 0.929934 ± 0.007484 / 1.0，完全吻合（± 号取跨场景 SD）。
- 变体 D 四值 70.3 / 117.8 / 154.5 / 142.7（`en:1302-1303`）——复算 70.267 / 117.800 / 154.500 / 142.680，吻合。
- 同段 f2 四值：随机 0.349±0.016 / 0.347±0.015（数据 0.34917±0.01603、0.34748±0.01470，ddof=1）；热启动 0.342±0.026 / 0.336±0.039（数据 0.3420±0.0262、0.3364±0.0385，ddof=1）——吻合。
- 扰动扫描：f2≈0.343、f3≈0.610（moea_3obj 0.3427–0.3432 / 0.6092–0.6099）、f2≈0.343、f3≈0.609（moea_2obj 0.3427–0.3431 / 0.6086–0.6090）、σ=0.7 时 199.5、档间变化 ≤1.3e−3（"~1e−3"）——全部吻合。

**任务 B（逐元素核对）**

- 图 7 曲线数 = 4（A/B/C/D），与正文"four objective variants"一致；PNG 上四点读数 −0.62/−0.15/−0.13/−0.23（A）、−0.23/−0.09/−0.12/−0.22（B）、−0.65/−0.17/−0.13/−0.23（C）、−0.13/−0.07/−0.11/−0.22（D），与 `schedule_correlation.json` / `schedule_correlation_ablation.json` 对应。
- 图 7 图注四要素均存在：50 场景/类池化（数据 `n_schedules 50`）、黑色虚线包络（脚本 `:95` `color='0.15'` 近黑）、灰色带 95% 区间（`:92` `fill_between(nl_lo, nl_hi)`）、20 次置换/类（`null_new_caliber.py:69` `for _ in range(20)`）。
- 图 8 面板数 = 4（a–d），与图注 a–d 一一对应；PNG 目视确认。
- 图 8(a)：灰色散点 + 均值±SD 误差棒均在；n=30/12/15/15 与数据一致。
- 图 8(b)：无误差棒，与图注"error bars omitted"一致；σ∈{0.1,0.3,0.5,0.7} 四档、每档 10 个 S3 场景（`sweep_summary.json` `n:10`）与图注"ten S3 scenarios per level"一致。
- 图 8(c)：5 个 S1 场景、5,000 次抽样、mean/p90/best 三标记、f1*=1 处虚线参考线，全部存在。
- 图 8(d)：柱高比例与 154.5/70.3（S3）、142.7/117.8（S4）一致；随机柱有 SD 误差棒，热启动柱无误差棒——与 17:38 版图注"hot-start (class mean over the 50 scenarios)"、"random initialization (mean and SD over 15 runs per class)"**一致**（17:36 旧版图注此处不含热启动口径限定，已修复）。
- 两版图注 `fig7`/`fig8` 与图内元素无第二处不符。

**任务 C**

- 8/24/6/5/6 五项计数两版完全相同；`fig7_corr_density.pdf` 与 `fig8_controls.pdf` 两版各 1 次；`-0.62` 两版各 3 次、`-0.63` 两版均 0。
- 中文稿 §6.4 数值逐条镜像英文（`:813` "S1 为 −0.62，S2--S4 分别为 −0.15、−0.13、−0.23"），无遗漏、无旧值。

**任务 E**

- 英文 47 页、两版 `^!` 错误行均为 0、无未定义引用/文献、PDF 文本无 `??`。

---

## 未验证范围

1. **`7.6\times10^4$ geometry samples`**（`en:1142`）——`null_new_caliber.py` 只输出相关系数，不落盘样本计数；不重跑该脚本无法核验。
2. **"all 10 sweep scenarios reach the ceiling" 的逐次数据**——`sweep_summary.json` 只存聚合量（mean/std），无 per-run 记录；A-4 的矛盾是**由聚合量算术推出**，不是逐次读数。
3. **`coverage stays flat at 200 of the 300 targets` 与 `\S\ref{sec:constraints}` 的资源上限定义**——未回查约束章节推导。
4. **任务 A 表以外的正文数字**（+33.7%、+34%、+40%、+4.9%、+28%→+2.3%、各 $p$ 值、Cliff's $\delta$、HV 0.2341、$N_{50}$ 等）——本批未逐条回溯数据源，只核了任务书列出的 6 行及其紧邻段落。
5. **中文稿除任务 A 表所列数值外的其余数字**——只核了镜像存在性与关键数，未逐条复算。
6. **图 8(d) 柱高**——只做比例目视核对（PDF 内 154.5/142.7/70.3/117.8），未做像素级测量。
7. **`references`/`.bib` 一致性与引用完整性**——`grep` 层面 0 未定义引用，但未逐条比对 bib 条目。
8. **回归测试套件**（`src/tests/` 与 `papers/sliding-spotlight-scheduling/tests/`）——本任务为只读文稿审查，未运行任何 pytest。
9. **图 7 中 B/C/D 曲线在 S2 的精确读数**——目视为 −0.09/−0.17/−0.07，未与 JSON 逐位比对（JSON 值 −0.09412 / −0.16993 / −0.07439，四舍五入后与图一致，但图内像素读数误差未量化）。

---

# 【追加 · brief2 回扫（任务 A/B/C）】

> 本节由另一次只读回扫（按 `review/cross-review-20261101/brief2.md` 执行）**追加**在上文报告之后；上文未改动一字。
> 并发提示：写入期间检测到同目录 `opencode2/3/4.log` 多实例同时运行，`findings.md` 曾被整体重写一次（mtime 17:42:10）。本节以追加方式落盘，若上文被后续实例重写，本节可能丢失，请以实际文件为准。

## 红线复述（原文）

1. 只读：只允许写 findings.md。
2. 每个数字必须来自实际读到的文件或命令输出。
3. 每条发现必须带 `file:line` + 引用原文。
4. 不确定写"未验证"。
5. 不评价论文该不该做某项研究，只核对一致性。

## 任务 A — 数字核对（brief2 指定 6 条）

| # | 正文值 | 正文位置 | 复算值（数据文件） | 结论 |
|---|---|---|---|---|
| A1 | −0.62 / −0.15 / −0.13 / −0.23（变体 A，S1–S4） | `small-paper-ijae.tex:1135` | −0.62283 / −0.15228 / −0.12615 / −0.22902（`schedule_correlation.json:6/17/28/39`） | 一致 |
| A2 | −0.23 / −0.65 / −0.13（B/C/D 在 S1） | `:1168-1172` | −0.22550（`schedule_correlation_ablation.json:60`）/ −0.65446（`:114`）/ −0.13345（`schedule_correlation.json:52`） | 一致 |
| A3 | ≈−0.36 包络（S1 −0.35，S2–S3 −0.37）；零假设 −0.60 | `:1143`、`:53` | −0.355 / −0.371 / −0.370 / −0.360（`null_new_caliber2026.json:3/11/19/27`），四类均值 −0.364；S1 null −0.602（`:4`） | 一致 |
| A4 | 0.393±0.251 / 0.551±0.060 / 0.684±0.050 / 0.475±0.067 | `:1258-1259` | −0.3926±0.2511 / −0.5510±0.0597 / −0.6836±0.0499 / −0.4753±0.0670（`p1-1_random_init/hotstart_control_s1s4.json`：`scales.S*` 逐条 `random.f1 − hot.f1`，n=30/12/15/15） | 一致 |
| A5 | 0.527 / 0.930 / 1.000 | `:1287-1288` | 0.5270±0.0034 / 0.9299±0.0084 / 1.000（`p1-2_random_search/p1-2_s1_random_search.json` 5 场景） | 一致 |
| A6 | 70.3 / 117.8（随机）；154.5 / 142.7（热启动） | `:1302-1303` | 70.2667 / 117.80（`variant_d_random_init/full.json` `results.S3/S4[].n_selected`，各 15 条）；154.50 / 142.68（`moea_3obj_no_physics/_progress.json` `completed` 前缀 `S3/`、`S4/` 各 50 条） | 一致 |

附核（同段，非 6 条内）：`small-paper-ijae.tex:1136-1138` 的 per-schedule means 与 Fisher-z 逐项吻合，仅 S3 per-schedule mean 有取整差（见 A1-a）。

### 本节发现

| # | 严重度 | 位置 | 问题 | 证据 | 建议 |
|---|---|---|---|---|---|
| A1-a | 观察 | `small-paper-ijae.tex:1136` | S3 per-schedule mean 写 −0.16，数据为 −0.1547（应为 −0.15） | 原文 "per-schedule means of $-0.72$ and $-0.15$/$-0.16$/$-0.18$"；`schedule_correlation.json:33` `"per_schedule_mean": -0.15474855189048908` | 改 −0.15，或说明取整口径 |
| A2-a | 观察 | brief2 表格第 2 行 | brief2 把变体 D 也指向 `schedule_correlation_ablation.json`，该文件不含 D | `schedule_correlation_ablation.json:169-171` 的 `sources` 仅 `A_full_physics`/`B_no_squint`/`C_no_incidence`；D 实取 `schedule_correlation.json:52` | 数字无误；修正任务书的数据源指认 |
| A3-a | 观察 | `small-paper-ijae.tex:1143` | S1 包络 −0.355 写作 −0.35（截断），而同句 "≈−0.36" 是四类均值 −0.364，两个不同量共用同一三位数字面 | `null_new_caliber2026.json:3` `"r_envelope": -0.355`；四类均值 −0.364 | 可接受；若要消歧，S1 写 −0.36 并注明均值口径 |
| A6-a | 观察 | `small-paper-ijae.tex:742` vs `:1135` | 两处"变体 A"数值不同（−0.80/−0.23/−0.15/−0.31 vs −0.62/−0.15/−0.13/−0.23） | `:742` 限定为 geometry variant A、每类 10 条排程，数值吻合 `schedule_correlation_a_only.json:6/13/20/27`（−0.7980/−0.2269/−0.1483/−0.3120）；`:1135` 为每类 50 条 | 非矛盾；建议明写"10 schedules per class" |

**任务 A 判定：6/6 一致，0 须修。**

## 任务 B — 中英镜像（brief2 指定 4 项）

| # | 项目 | en | zh | 预期 | 结论 |
|---|---|---|---|---|---|
| B1 | `\section{` | 8 | 8 | 相同 | 一致 |
| B1' | `\section*{`（附） | 6 | 6 | — | 一致 |
| B2 | `\begin{figure` | 6 | 6 | 相同 | 一致 |
| B3 | `fig7_corr_density.pdf` | 1 | 1 | 各 1 | 一致 |
| B4 | `-0.63` | 0 | 0 | 各 0 | 一致 |

证据：两版 8 个 `\section` + 25 个 `\subsection` + 6 个 `\section*`（`\subsubsection` 0）逐条同序同数，仅语言不同——en `small-paper-ijae.tex:68` `\section{Introduction}` ↔ zh `small-paper-ijae-zh.tex:65` `\section{引言}`；en 末条 `:1576` `\section*{Funding}` ↔ zh `:1116` `\section*{资助声明}`。图：两版各 6 个 `\begin{figure}[H]`（en `:951/1007/1032/1093/1152/1239`）与 6 个 `\includegraphics`，无 `figure*`、无 `subfigure`。fig7 引用 en `:1153` 与 zh 各 1 处。

| # | 严重度 | 位置 | 问题 | 证据 | 建议 |
|---|---|---|---|---|---|
| B0-a | 观察 | 本机执行环境 | brief2 给的 `grep -c` 命令在本机 PowerShell 下会静默给出错误计数，不可作为证据 | `grep -n 'begin{figure' small-paper-ijae.tex` 返回的全是 `\begin{document}`/`\begin{table}` 等行（实际按 `begin{` 匹配，27 行）；`grep -c '\\section{'` 返回 0，而精确计数为 8 | 后续任务书改用精确计数通道；本节计数由 Python `str.count(chr(92)+...)` 与 PowerShell `Select-String -SimpleMatch -Pattern ([string][char]92+'section{')` 两路互验，结果一致（16 / 12 合计，分文件 8 / 6） |

**任务 B 判定：4/4 一致，0 须修。**

## 任务 C — 正文残留（brief2 指定 3 个计数）

| # | 计数项 | 实测 | 预期 | 结论 |
|---|---|---|---|---|
| C1 | `---`（非注释行） | 0 | 0 | 一致 |
| C1' | `---`（原始全文件） | 1，唯一一处为注释行 `small-paper-ijae.tex:2` `%  Small Paper --- ASR (Advances in Space Research)` | — | 注释不计，符合预期 |
| C2 | `Phenomenon` | 0 | 0 | 一致 |
| C3 | `rather than` | 30 行 / 31 次（含 `:769` 一行两次） | 报总数 | 已报 |

C3 行号：139, 242, 251, 297, 359, 375, 393, 427, 438, 441, 465, 489, 564, 569, 602, 614, 661, 769(×2), 831, 835, 891, 1328, 1354, 1373, 1393, 1404, 1434, 1445, 1452, 1474。

| # | 严重度 | 位置 | 问题 | 证据 | 建议 |
|---|---|---|---|---|---|
| C0-a | 观察 | `small-paper-ijae.tex:2` | 未注释的 `---` 为 0，但 grep 原始计数为 1，直接跑命令会与"预期 0"打架 | 原文 `%  Small Paper --- ASR (Advances in Space Research)` | 任务书注明"排除 `%` 开头行"，或直接给出非注释计数口径 |

**任务 C 判定：3/3 符合预期（C1 需按"注释行不计"口径读）。**

## 本节结论

发现总数 6（A1-a、A2-a、A3-a、A6-a、B0-a、C0-a），**须修 0**，6 条全部为"观察"级。结论：**通过**。brief2 任务 A/B/C 全部通过：A 6/6 一致、B 4/4 一致、C 3 项计数符合预期。
（与上文 report 的对应：本节的 A1-a 未被上文覆盖；A2-a/C0-a 为任务书口径问题，非论文问题；A6-a 与上文 A-7 同源；B0-a 为工具问题。）


# 【追加 · brief2 回扫（任务 A/B/C）· 第二实例】

> 本节由按 `review/cross-review-20261101/brief2.md` 执行的回扫**追加**在上文之后；上文未改动一字。
> 并发处理记录：本实例开工时2026年11月1日 17:42（多个 `opencode` 实例并发）曾检测到该文件被另一实例整体重写并已含一份 `brief2` 节，故本节以"追加"方式落盘，不做覆盖。
> 审查对象字节实测（`os.stat`，本节全部行号与结论基于此版本）：`small-paper-ijae.tex` 98,783 B / `mtime` 2026-11-01 17:45:53；`small-paper-ijae-zh.tex` 89,505 B / 17:46:29。精确计数用 Python `str.count`（`ed`/`PowerShell grep` 通道已由上文上一节证明不可靠，不复用）。

## 红线复述（原文）

1. 只读：只允许写 "findings.md"。
2. 每个数字必须来自实际读到的文件或命令输出。
3. 每条发现必须带 `file:line` + 引用原文。
4. 不确定写"未验证"。
5. 不评价论文该不该做某项研究，只核对一致性。

## 任务 A — 数字核对（6/6 一致，独立复算）

| # | 正文值（正文位置） | 复算值（实际读数） | 结论 |
|---|---|---|---|
| A1 | 变体 A：S1=−0.62，S2=−0.15，S3=−0.13，S4=−0.23（`small-paper-ijae.tex:1135`"variant A it is $-0.62$ at S1 and $-0.15$, $-0.13$, $-0.23$ at S2--S4"） | `schedule_correlation.json→variants.A_full_physics`：r = −0.62283 / −0.15228 / −0.12615 / −0.22902 | 一致 |
| A2 | B/C/D 在 S1 = −0.23 / −0.65 / −0.13；D 另在 S2=−0.07（`:1168-1172`"collapses to $-0.23$"、"holds at $-0.65$"、"falls to $-0.13$ at S1 and $-0.07$ at S2"） | `schedule_correlation_ablation.json→variants`：B_no_squint S1 r=−0.22550→−0.23 ✓；C_no_incidence S1 r=−0.65446→−0.65 ✓。D 不在 ABLATION 文件中，其值在 `schedule_correlation.json→variants.D_no_physics`：S1 r=−0.13345→−0.13 ✓、S2 r=−0.07439→−0.07 ✓；未采信文件值，另按官方 `caliber`（`scripts/compute_schedule_correlation.py:73-94`，源 `moea_3obj_no_physics/_progress.json`）在内存独立复算得 S1 −0.1334（976 任务/50 排程）、S2 −0.0744，与文件一致 | 一致（D 的数据源见 F-1） |
| A3 | 包络 −0.36（S1 −0.35，S2–S3 −0.37）；零假设 −0.60（`:1143-1144`"$\mathrm{corr}(f_2,f_3) \approx -0.36$ ($-0.35$ at S1, $-0.37$ at S2--S3)"；`:1113`、`:1117`"$r_{\text{null}}=-0.60$"） | `null_new_caliber2026.json`：`r_envelope` S1 −0.355 / S2 −0.371 / S3 −0.370 / S4 −0.360（四位均值 −0.364 → −0.36，亦等于 S4 的 −0.36）；`r_shuffle_null_mean` S1 −0.602 / S2 −0.615 / S3 −0.615 / S4 −0.609（S1 → −0.60 精确吻合；其余在原文自述 ±0.02 类间散布内） | 一致（−0.35 为 −0.355 截断，见 F-2） |
| A4 | 覆盖亏损 −0.393 / −0.551 / −0.684 / −0.475（`en:1266-1267`"Random-initialized MOEA-2 loses $0.393\pm0.251$, $0.551\pm0.060$, $0.684\pm0.050$, and $0.475\pm0.067$ in $f_1^*$ at S1--S4"） | `p1-1_random_init/hotstart_control_s1s4.json`：`summary.deficit_mean` = −0.39256 / −0.55103 / −0.68361 / −0.47535（SD 0.25112 / 0.05969 / 0.04994 / 0.06700），n=30/12/15/15；按任务书口径用 `scales.S*[]` 逐条重算 `mean(random.f1 − hot.f1)` 得 −0.39256 / −0.55103 / −0.68361 / −0.47535，两条通道相同 | 一致 |
| A5 | 随机搜索 0.527 ± 0.003 / 0.930 ± 0.008 / 1.000（`en:1287-1288`"$f_1^*=0.527 \pm 0.003$, a 90th percentile of $0.930 \pm 0.008$, and a best sample of $1.000$"） | `p1-2_random_search/p1-2_s1_random_search.json`：5 场景（S1-A_seed00..04）`f1_star_mean` 均值 0.526996（跨场景 SD 0.003351→±0.003）、`f1_star_p90` 均值 0.929934（SD 0.008368→±0.008）、`f1_star_best` 5 场景全 1.0（均值 1.0/最大 1.0） | 一致 |
| A6 | 任务数 70.3 / 117.8（随机初始化）、154.5 / 142.7（热启动）（`en:1302-1303`"it schedules $70.3$ and $117.8$ tasks at S3 and S4, against $154.5$ and $142.7$ for the hot-started variant"） | 随机：`variant_d_random_init/full.json→results`（params：n_scenarios 5、n_seeds 3 → 各组 15 条）S3 `n_selected` 均值 70.2667→70.3 ✓、S4 117.800 ✓；热启动：`moea_3obj_no_physics/_progress.json→completed`（键前缀 `S3/`/`S4/`）各 50 条，S3 均值 154.500 ✓、S4 142.680→142.7 ✓（口径差异见 F-3） | 一致 |

### 本节新增发现（均不含上文已记事项）

| # | 严重度 | 位置 | 问题 | 证据 | 建议 |
|---|---|---|---|---|---|
| F-1 | 观察 | `brief2.md` 表格 A2 行 / 版本漂移 | 任务书把变体 D 指向 `schedule_correlation_ablation.json`，该文件只含 A/B/C（`variants`：`A_full_physics`、`B_no_squint`、`C_no_incidence`）；D 实际在 `schedule_correlation.json`（且该文件同时含 A 与 D 两键） | `schedule_correlation_ablation.json` `variants`/`sources` list；`schedule_correlation.json` `variants` list | 修正任务书 A2 行的数据源指认；正文数字本身无误 |
| F-2 | 观察 | `small-paper-ijae.tex:1144` | "−0.35 at S1" 为 S1 包络 −0.355 的截断（两位四舍五入应得 −0.36）；同句统计值 −0.36 是四类均值（−0.364）或 S4 值（−0.360），S1 的 −0.35 与统计值 −0.36 属两个不同口径共用近似数字 | `null_new_caliber2026.json` `r_envelope` S1 −0.355、S4 −0.360；四类均值 −0.364 | 可接受；如需消歧可写 "−0.36（四类均值；S1 −0.355）" |
| F-3 | 观察 | `small-paper-ijae.tex:1302-1303`（图 8d） | 热启动 154.5/142.7 来自 50 场景全类均值（`_progress.json` 各 50 条），随机初始化 70.3/117.8 来自 5 场景 × 3 种子 = 15 次均值（`variant_d_random_init/full.json` params），两侧样本口径不同（数字本身无误） | `os.stat`/JSON 内 `params` 字段实读 | 非数字错误；如图注需注明热启动侧"50 场景均值"更稳妥 |

## 任务 B — 中英镜像（4/4 一致）

| # | 项目 | en | zh | 预期 | 结论 |
|---|---|---|---|---|---|
| B1 | `\section{` | 8 | 8 | 相同 | 一致 |
| B2 | `\begin{figure` | 6 | 6 | 相同 | 一致 |
| B3 | `fig7_corr_density.pdf` | 各 1 次（en 出现 1 行 1 次、zh 同；`/includegraphics` 各 6） | 1 | 1 | 一致 |
| B4 | `-0.63` | 0 | 0 | 各 0 | 一致 |

证据：Python `count` 直测 en/zh 两文件（字节见本节开头）；`-0.62` 附测 en 4 次 / zh 3 次（非本任务要求项，仅记录）。

## 任务 C — 正文残留（3/3 符合预期）

| # | 计数项 | 实测（本节字节版 17:45:53） | 预期 | 结论 |
|---|---|---|---|---|
| C1 | `---`（非注释行） | **0**（原始全文件 1 次，唯一在 `small-paper-ijae.tex:2` 注释行 "%  Small Paper --- ASR (Advances in Space Research)"） | 0（注释行不计） | 一致 |
| C2 | `Phenomenon` | **0** 行 0 次 | 0 | 一致 |
| C3 | `rather than` | **30 次 / 29 行**（`:770` 一行 2 次）行号：243, 252, 298, 360, 376, 394, 428, 439, 442, 466, 490, 565, 570, 603, 615, 662, 770(×2), 832, 836, 892, 1331, 1357, 1376, 1396, 1407, 1437, 1448, 1455, 1477 | 报总数即可 | 已报 |

注：本行号基于 17:45:53 版本，与上文报告 17:38:39 版本整体偏移 +1 行（上文记 139, 242, …；本节 243, 252, …），系版本推进所致，两类结论一致。

## 本节结论

发现总数 3（F-1、F-2、F-3），**须修 0**，3 条均为"观察"级。brief2 汇总：任务 A 6/6 一致、任务 B 4/4 一致、任务 C 3/3 符合预期。结论：**通过**。
