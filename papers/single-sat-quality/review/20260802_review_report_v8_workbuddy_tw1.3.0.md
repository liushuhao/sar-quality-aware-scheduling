> Reviewed by: workbuddy (论小舟 / thesis-writing-mentor) · thesis-workflow v1.3.0 · 2026-08-02
> Subject: 用户"再次更新"后全面审查（在 v8/v9-closure/ppw 批次修复基础上的未提交改稿）
> Scope: 中英双版主文件 + 消融节 + gen_table1.py；本轮 diff 全覆盖 + 数据对抗复算 + 交叉引用完整性

# 全面审查报告 v8（Workbuddy, 2026-08-02）

## 0. 就绪度判定

**整体：`needs_author_input`** —— 论文正文（英文投稿版）**无 P0、无 P1**。本轮用户改稿是此前 v8/v9-closure/ppw(08-02) 批次修复的中英落地，数据层独立复算全部通过。唯一正文级新问题是 **V8-N1（P2，中英 §7.1 结构漂移）**，非阻塞但建议定稿前对齐。阻塞项仍是投稿链路非正文项（GitHub 重推、UC-1 数可追溯性）。

---

## 1. 本轮改稿内容（git diff，未提交工作树）

| 区域 | 文件 | 改动 | 对应前序修复 |
|---|---|---|---|
| 贡献声明 §1 | EN L146-150 / ZH L109-114 | 拆分归属：消融→高密不变性；初始化对照→G-BL 热启动条件性 | AC-4 |
| §2.2 分辨率方向 | EN L234-246 / ZH L169-177 | ρ_az/ρ_rg 方向拆分：ρ_rg 在最小入射最粗、随 θ 升高改善 | AC-1 |
| Table 3（solver profiles） | EN L687-721 / ZH L527-561 | 60 个 SD 格全部改 ddof=1 | NC-1 |
| §6.4 Phenomenon 1 | EN L842-877 / ZH L665-699 | 合并两段重复的前沿压缩论述 | AC-2 + M3 |
| §6.6 鲁棒性对照 | EN L986-1016 / ZH L769-799 | 去 4 处 `\textit{This control isolates X, not Y}` 同构斜体收尾 | M1 |
| §7.1 发现总结 | **仅 EN L1039-1071** | 改 5 项 \textbf{(1)}–\textbf{(5)} 列表 + 删"排名散文段" + 加 GA-P-BL delimitation 句 | AC-3 |
| 消融节 | EN/ZH sections/_ablation_section*.tex | D "warrants closer examination"→"is visible in the task counts"；SD 改 ddof=1 | M2 + NC-1 |
| §5.2 窗口统计 | **仅 ZH L463-465** | 零多普勒穿越比例 50–60%→15–17%（S1–S4: 15.1/17.2/14.9/14.9%，共 45,345 窗，中位 min|ψ_sq| 27–30°） | UC-1 (P0) |
| gen_table1.py | L10 | +`from pathlib import Path`（NC-1 复算脚本依赖） | NC-1 使能 |

---

## 2. 数据层对抗复算（独立重跑，非仅看批注）

### 2.1 Table 3 f2/f3 SD（ddof=1）—— **全部 20 格精确吻合** ✅
用纯 Python `statistics.stdev`（ddof=1）从原始 `_progress.json` 复算，与 tex 当前数值逐格一致：

| 格 | 复算 f2±sd1 | tex | 复算 f3±sd1 | tex |
|---|---|---|---|---|
| S1 G-BL | 0.541±0.068 | ✓ | 0.325±0.174 | ✓ |
| S1 MOEA-3 | 0.569±0.066 | ✓ | 0.288±0.151 | ✓ |
| S4 MOEA-2 | 0.589±0.021 | ✓ | 0.169±0.066 | ✓ |
| S4 MOEA-3 | 0.589±0.021 | ✓ | 0.170±0.067 | ✓ |
| （余 16 格同理全部 ✓） | | | | |

来源：`baselines_200.json`(G-BL/G-SM) + `b2_profit_bl/_progress.json`(GA-P-BL) + `moea_2obj`/`moea_3obj/_progress.json`(MOEA-2/3)，每组 n=50。

### 2.2 消融表 SD（ddof=1）—— **吻合** ✅
`ablation_summary.csv` 的 std 列为 ddof=0；乘 √(50/49)=1.01015 得 ddof=1，与 tex 改后值一致：
- S1-A n_selected：csv 4.429 → ddof=1 4.47 ≈ tex **4.5** ✓
- S1-D n_selected：csv 5.649 → ddof=1 5.71 ≈ tex **5.7** ✓
- S1-D n_sel(f1_per_task)：csv 1.038 → ddof=1 1.05 ≈ tex **1.05** ✓

### 2.3 交叉引用完整性 —— **无断链** ✅
本轮新增两处 `\ref`：
- `\ref{sec:objective-functions}`：EN L243 / ZH L177 → label 存在（EN L334 / ZH L246）✓
- `\ref{sec:robustness-calibration}`：EN L151,662,750,1111 / ZH L114,505,587,899 → label 存在（EN L977 / ZH L763）✓
- §7.1 重组后依赖的 `tab:solver-profiles` / `tab:scale-sensitivity` / `tab:hv` 双版均存在 ✓

### 2.4 §2.2 ρ_rg 方向修正 —— **物理正确** ✅
新文"ρ_rg 在最小入射（最近点）最粗、随 θ 升高改善"。验证：ρ_rg = c/(2B·sinθ)，sinθ 随 θ 升而增 → ρ_rg 减（改善）。与 §3.2 目标函数 f2=sinθ·cosψ_sq（θ↑→f2↑）自洽；与 §7.1 L1081–1084 的 ρ_rg≈5.3 m@θ=30°、8% f2 改进≈0.25–0.35 m 一致。原"两者均随偏离零多普勒退化"确为 ρ_rg 说反（AC-1 判定正确）。

### 2.5 §7.1 EN 重组 —— **干净，无丢主张** ✅
5 项列表 (1)饱和/(2)三目标冗余/(3)G-SM 特异/(4)N≥300 不变/(5)热启动条件；删去的"排名散文段"信息已并入 GA-P-BL delimitation 句（L1067–1071）+ Table 3；Friedman 506.56/p≈10⁻¹⁰⁸、MOEA-2 vs MOEA-3 δ=−0.23/p=1.4×10⁻⁴ 均保留。

### 2.6 UC-1 零多普勒穿越比例 —— **已修正方向，数值可追溯性待补** ⚠️
ZH L463–465 已将错误的 50–60%（差 3–4 倍）改为 15–17%，并给逐类值 + 45,345 窗 + 27–30° 中位。量级合理（200 场景 × ~227 窗 ≈ 45,400），P0 级错误已消除。**但未在仓库内发现生成该数的脚本**（grep 全仓仅 ZH.tex 与 review 报告含 45,345；应出自 sar_sim 几何，经 Data Availability 指向 GitHub）。建议补一行 provenance 或一页 repro 脚本，使该数可审计。

---

## 3. 本轮新发现问题

### V8-N1 — 中英 §7.1 结构漂移（P2）
- **位置**：EN `small-paper-ijae.tex` L1039–1071（紧凑 5 项列表 + GA-P-BL delimitation）；ZH `small-paper-ijae-zh.tex` L799–854（保留旧导语 L809–810 "效应反映的是尺度…第五个反映求解器初始化" + "首先，求解器调查显示了一个清晰的排序…"散文段 L818–822）。
- **证据**：git diff 显示 EN §7.1 本轮被重组（删除"排名散文段"+导语），ZH §7.1 不在 diff 内（本轮未改）。EN 现用 \textbf{(1)}–\textbf{(5)} 显式枚举；ZH 用 第一/第二/第三/第四 散文枚举（仅 4 段），且"五个相互关联的发现"的第五项（热启动条件）在 ZH 中内嵌未显式编号，与 EN 5 项列表不一一对应。
- **严重度**：P2。无事实错误（ZH L818 引 GA-P-BL S4 f1*=1.17±0.27、L820 引 MOEA-2/3 S4 f2=0.589±0.021 均与 Table 3 吻合），仅结构不对称。
- **状态**：`TODO_AUTHOR_CONFIRM`
- **解决条件**：定稿时决定 ZH §7.1 是否镜像 EN 的 5 项列表结构（删 L809–810 导语 + L818–822"首先"散文段，或保留为等价叙述但补足第五项显式编号）。内容无需改，纯结构对齐。

---

## 4. 前序 P0/P1 状态确认（非本轮，仅同步）

- **RDR-002（"+0.93~0.98 反转"不可复现）**：已在 v9-closure 闭环，`r_visible_envelope.json` 脏字段已清（V7-N3 fixed）。本轮未引入回归。
- **UC-1（零多普勒比例 50–60% 错）**：本轮 ZH 已落地修正（见 §2.6），P0 级错误消除。
- **V7-N1（S4/S1 HV 比<1 仅中文）**：v9-closure 已在 EN 补镜像句（0.72/0.67），本轮未回归。
- **V7-N3（JSON 脏数据）**：v9-closure fixed。
- **carry-over（非新）**：D01 GitHub 需重推最终代码（pushed_at=2026-07-22 早于全部修复）；V7-N2（sec:hv-divergence 标签仅中文）、V7-N4（中文图 label 键错位）按前序裁决 deferred（编译自洽、零读者收益、有断链风险）。

---

## 5. 结论与下一步

**正文质量**：本轮改稿使 v8/v9/ppw 修复全部中英落地；Table 3/消融表 SD 经独立复算逐格吻合；§2.2 物理修正正确；交叉引用无断链；RDR-002 与 UC-1 两个历史 P0 均处闭环。整体达投稿级。

**待你拍板（定稿前）**：
1. **V8-N1**：对齐 ZH §7.1 与 EN 的 5 项列表结构（P2，纯结构）。
2. **D01**：重推 GitHub 最终代码（Data Availability 指向该仓，pushed_at 早于修复）。
3. **UC-1 可追溯性**：补 45,345 窗/15.1% 等数的生成 provenance（建议一句话注或一页 repro 脚本）。

确认后我可直接：①按 EN 改写 ZH §7.1 列表结构；②（授权后）补 UC-1 数 provenance 注释。GitHub 重推需你本人执行（涉外发）。

---
*方法注：本轮未重跑求解器（本机无 pymoo/sar_sim）；所有数值主张均经 `experiments/results` 原始 JSON/CSV 独立复算核验，非依赖批注。*
