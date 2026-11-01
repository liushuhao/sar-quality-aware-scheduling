# R5 / R6 闭环：方位模糊的场景跨度通道重估 + 驻留内分辨率退化界

**日期**: 2026-11-01（第二轮）
**来源**: [editorial-decision.md](editorial-decision.md) must-fix 义务 R5、R6（2026-10-31 投稿前五席面板）
**上位执行记录**: [04-revision-applied.md](04-revision-applied.md)（第一轮：R1–R4/R7–R9 已落地，R5 只撤回主张、R6 未做）

本文件是这两条义务的收尾工件：重估了什么、数字从哪来、写进正文哪句、由哪个门禁兜住，以及一轮独立复审推翻掉的初稿说法（见 §复审与更正）。

---

## R5 —— 把场景跨度通道放回模糊积分

**面板要求**（原文）: *Re-evaluate the azimuth-ambiguity integral with a scene-sweep occupancy term consistent with the §3.2 $W_a$ dwell closure and re-read the squint-direction contrast, or withdraw the claim of "a difference of mechanism, not merely of sign"*。

第一轮走「撤回」分支；本轮走「重算」分支。

### 起点：这个模型里场景跨度到底在哪几条腿上

| 位置 | 场景跨度怎么进 | 代码 |
|---|---|---|
| §3.2 驻留闭式 | 扫掠角 `α = θ_a + (R0θ_a + W_a)/r0`，`W_a` 以**旋转中心距离 r0≈197 km** 为杠杆 | `sss_core/duration.py:481-482` |
| 条带/滑聚 AASR 积分带 | **不进**：`B_D = Vs·cosψ/ρ_a`（时长链、库口径） | `aasr.py:258` → `modes.py:bandwidth_d_hz` |
| 聚束 AASR 分支 | **进**，且**不含 ψ**：`kat0 = (2Vs/λ)(W_a/2)/R0`，按最坏边缘计 | `aasr.py:247-252` |

两条腿的杠杆不同（`r0≈197 km` vs `R0≈775 km`，差 **3.94×**），幂次也不同（闭式无 ψ，聚束分支 ψ⁰）。所以「把闭式里那一项搬进积分」不是一次单位换算——这是初稿的错误说法，见 §复审与更正。

### 三条候选映射（都实测，不挑好看的）

目标斜视随沿轨偏移 x 的变化：`f(x) = (2Vs/λ)·sin(atan(tanψ + x/R0))`，故场景两端频差（ψ=0/12/26° 三处与 `(2Vs/λ)cos³ψ·W_a/R0` 相对误差 <0.01%）：

| 映射 | 加进积分带的量 | 依据 |
|---|---|---|
| 几何（cos³） | `(2Vs/λ)·cos³ψ·W_a/R0` | 目标斜视随沿轨位置的真实几何 |
| 登记带约定（cos¹） | `(2Vs/λ)·cosψ·W_a/R0` | 与 `B_D = Vs·cosψ/ρ_a` 自身用的 cos 幂一致 |
| 聚束腿（ψ⁰） | `(2Vs/λ)·W_a/R0` | 模型自己登记的换算（`aasr.py:248`，无 ψ） |

三条在 ψ=0 处同值（3152.5 Hz），分歧只在高斜视端。

### 结果（生产 PRF 3630 Hz，库口径 k=0.797317）

| 读数 | ψ=0° | ψ=26° | 方向 |
|---|---|---|---|
| 登记带（正文原读数，复现） | −21.35 dB | −23.32 dB | 随斜视改善 |
| SLS + cos³ / cos¹ / cos⁰ | −16.45 | −20.22 / −19.38 / −18.87 | 全部单调改善 |
| STR + cos³ / cos¹ / cos⁰ | −2.78 | −7.74 / −5.17 / −3.88 | 全部单调改善 |

零斜视电平位移（三条相同）：SLS **+4.9 dB**、STR **+18.6 dB**。

模型自带的场景跨度通道（聚束分支）：点目标 **−28.28 dB** vs 5 km 场景 **−7.05 dB**，即 **21.2 dB**——这是本模型里场景跨度影响最大的一处。

稳健性：0–26° 按 2° 步长逐点算，六种（模式×映射）全部单调改善；双程方向图也按 cosψ 缩放的自洽探针同号；积分点数 256→4096、混叠阶数 6→20 变化 <0.005 dB。

### 结论

**方向不由场景跨度决定**：三条映射要么让积分带随斜视收窄（角度按 cos²，多普勒按 cos³），要么保持不变（ψ⁰），没有一条会随斜视加宽——而带不加宽就不可能加宽混叠折入。所以面板提的「scene-ensemble scan span grows the Doppler occupancy with scan angle」这条候选和解，在本模型的平地球几何下不成立。

**但电平会被改到不能忽视**：三条映射都把 INT 放在 0° 处抬到 −2.78 dB，高于 −13 dB 准入线——即「带里带场景跨度」这一读法下条带模式一个都进不来。登记带因此是一个**处理口径**（逐目标/分块处理），不是保守余量。正文把这句写进去了。

正文落点：`main.tex` §7.2 对比段 + §3.3 积分带约定句。

**未越界的边界**：这是同一方位向方向图、同一登记几何下的模型内重算，不构成对 Song 平台读数的反驳。

**为什么不进 formula-spec**：spec §5 登记的 AASR 积分带就是 `±B_D/2`（本重算不改这个带），三条场景跨度式是**讨论层对照量**、无生产消费方；spec 头部规定改动须经 blocking gate。`sss_core/aasr.py` 零改动。

---

## R6 —— 驻留内分辨率退化界

**面板要求**（原文）: *Report the cosine-ratio degradation at the selected starts as a per-mode worst case from the dwell-distribution data already computed, or add a one-line bound to the constraint statement*。

**数据**：与 fig-7 同源同路径（`experiments/v5_results/sweep/s1_0/pilot_*.json` + `scenarios/*.json`，s=1.0，每族十种子，best-covered member，30 单元 / **1607** 个被服务任务）。驻留用生产闭式在选中起点重算，`ψ(t)` 用冻结窗口几何的 `squint_at`。

**统计量**：C5 正文承诺的 `ρ_req·cosψ_sel/cosψ(t)` 在驻留区间内的最坏值（`atan` 单调，最坏必在端点）。

| 模式 | 中位 | 最坏 | 退化超 10% |
|---|---|---|---|
| STR | 1.000 | 1.008 | 0 |
| SLS | 1.000 | 1.020 | 0 |
| SPT | 1.000 | 1.045 | 0 |

中位恒为 1.000：多数选中起点落在窗口的斜视递减侧。

正文落点：`main.tex` §3.4 约束 C5（面板给的第二选项「one-line bound to the constraint statement」）。

---

## 门禁

`scripts/verify_r56_group.py`（14 项检查/篇 + 7 条模型不变量），由 `scripts/verify_paper_numbers_l8.py` 接线：

- **有序归属匹配**：每个数字按「紧挨它自己的标签之前那串数」读取——`for sliding spotlight` 前四位、`(stripmap)` 前一位——所以换组、换标签、端点对调都会红。单纯「段落里有这个数」的检查已被证明无判别力（模式对调后 19/19 全绿）。
- **交叉引用数剔除**：`Section 3.3` / `Eq. 7` 这类同形数先剔除，防止拿章节号顶替读数。
- **模型不变量单列**：六条单调性 + 一条方向图自洽只报告、不计入「已验稿件数」，并另加两条正文断言（方向句必须存在且未被反转、`monotone at` 必须存在）。
- **两层地板**：`R56_MIN_CHECKS=14`/篇（整组掉线——锚点被改写、模块没 import——直接 ABORT），加上原来的全局地板 `155×篇数`（单篇跑法与双篇跑法都合法）。全局地板单独看抓不住「整组消失」：去掉 R56 组后单篇仍有 160 ≥ 155、照样放行，所以每篇的组地板是必需的。
- **可选开关**：`L8_R56_OPTIONAL=1` 给合成小稿直通（与既有 `L8_B16X_OPTIONAL` 同制）。
- **单测**：`tests/test_verify_r56_group.py`（24 条）钉住①本地积分器与 `sss_core.aasr.aasr_direct` 在 STR/SLS × 0–26° 逐点相等，②九类变异必须被抓。

> **2026-11-01 增补（commit `6faf243`，清残留 R102/R104）**：本组由 14 项扩到 **17 项/篇**，新增 §7.2 范围脚注里的 SPT 库边 AASR 与 SLS/SPT 零斜视处理带宽（按句中真正印出的模式标签绑定数值，且标签与 kHz 之间须恰好两个数），并额外闸住同一常数在该段内的第二处印刷；`R56_MIN_CHECKS` 同步 14→17，单测 24→31 条。跨句的种子身份断言（「the same seed ... as in the first dip」）仍不在本组覆盖内，挂残留 R105。原 14 项行为未变。

## 验证（本轮实跑，cwd = `papers/sliding-spotlight-scheduling`）

| 闸 | 命令 | 结果 |
|---|---|---|
| 数字闸 L8 | `python scripts/verify_paper_numbers_l8.py --paper paper/main.tex --paper paper/full.md` | rc=0，`0 mismatch over 327 checked`（R56 14+14；基线 299） |
| L8 单测 | `pytest tests/test_verify_paper_numbers_l8.py` | `21 passed` |
| R56 单测 | `pytest tests/test_verify_r56_group.py` | `24 passed` |
| 变异夹具 | `pytest tests/test_verify_l8_mutation.py tests/test_verify_gate.py` | 见下 |
| 红线/写作禁则 | `python scripts/check_red_lines.py` | rc=0 |
| 图注收据 | `python scripts/check_figure_receipts.py` | rc=0，`70/70` |
| 预注册冻结 | `python scripts/verify_prereg_v2.py` | rc=0，`28 checks` |
| 镜像探针 | `python scripts/sync_mirrors_check.py` | rc=0，`60/60` |
| 主张引用链 | `python scripts/verify_claim_traces.py` | rc=0，`11/11` |
| 版式 | `python scripts/check_layout_gotchas.py ...` | rc=0，`0 FAIL` |
| 编译 | `pdflatex` ×2 | rc=0，**47 页**，0 error，0 undefined |

## 反向验证（逆反断言，全部实跑）

| 变异 | 结果 |
|---|---|
| 端点对调（`−16.45 to −20.22` → `−20.22 to −16.45`） | ✅ 抓 |
| 同组两映射值对调（`−19.38` ↔ `−18.87`；`−5.17` ↔ `−3.88`） | ✅ 抓 |
| SLS / STR 整组对调 | ✅ 抓（2 条） |
| 两个电平位移的归属对调 | ✅ 抓（2 条） |
| 方向句反转（`no mapping ... reverses` → `every mapping ... reverses`） | ✅ 抓 |
| 删掉 `monotone at ... steps` | ✅ 抓 |
| 诱饵数（`+4.9`→`+6.1` 再补 `as Section 4.9 sets out`） | ✅ 抓 |
| R6 模式标签对调 | ✅ 抓（2 条） |
| 单值改错（`−3.88`→`−3.98`） | ✅ 抓 |
| 删锚短语 | ✅ 抓（且检查面 14→5，低于地板） |
| 标签加限定词（`(stripmap)`→`(stripmap mode)`） | ✅ 不误报 |

## 复审与更正（2026-11-01，两轮 fresh 独立审）

**第二轮（门禁审）** 推翻的：

1. **新组把仓内既有单测打红 7 条**（`tests/test_verify_paper_numbers_l8.py`，合成小稿不带锚点却预期 rc=0）。根因=只跑了稿件闸、没跑仓内 pytest；修法=`L8_R56_OPTIONAL` 直通开关 + 该文件的 env 补一行，现 21 passed。
2. **「段落里有这个数」检查无判别力**（模式标签/端点任意互换全绿）。改为有序归属匹配，见上表。
3. **7/14 条曾经的检查从不读正文**（六条单调性 + 方向图自洽）却计入「已验」——已移出计数、改报告为模型不变量，另补两条正文断言。
4. **整组掉线仍绿**（全局地板 155 对 327 无约束力）——加每篇 14 条地板，全局地板改为按篇数缩放（155×篇数，双篇=310）。
5. 本地积分器与 `aasr_direct` 是副本关系却写成「不可能漂移」——已改写 docstring 并用单测逐点钉住。

**第一轮（物理审）** 推翻的：

一审推翻的两条初稿说法，均已改正：

1. **「闭式丢掉的那一项重新进入为 `(2Vs/λ)cos³ψ·W_a/R0`」——不成立**：闭式那一项是 `W_a/r0`（旋转中心杠杆），与 `W_a/R0`（斜距处目标侧张角）差 3.94×，且不是多普勒占据量。初稿把两个量当成同一个。改法：正文不再说「dropped term re-enters」，而是分别列出闭式的场景项与积分能承载的目标侧占据量，并把模型自带的 ψ⁰ 换算单列。
2. **「场景跨度不在登记积分里」——对聚束分支为假**：`aasr.py:247-252` 明明带着 `kat0=(2Vs/λ)(W_a/2)/R0`（价值 21.2 dB）。§3.3 该句已改为只说条带/滑聚不带、聚束分支带。
3. 另修正措辞：`target-level` → `library-caliber`（生产走库口径，`rho_zero_task_m` 无生产调用方）；「积分没有斜视相关压缩因子这一项」→「`a_res` 进积分但按斜视无关推导」。

**保留的意见（不改）**：正文「the $26^{\circ}$ calibration-grid edge」是既有文字；26° 确是网格点（0.6667° 步长第 39 点），但不是轴端（轴到 ±45°），「edge」指校准读数序列的端点。不影响读数。

## 未覆盖 / 残留

- 未登记第四种读法：把闭式的旋转中心杠杆 `W_a/r0` 当多普勒跨度（0° 处 SLS −5.21 dB / STR +5.37 dB，全族不可行）。它不是多普勒占据量（多普勒只由目标斜视决定），故不作为映射候选；正文写明登记带是处理口径。
- 斜视相关压缩因子、随扫描角变化的天线单元方向图：模型无此项。
- 26° 端之外的 45° 设计域未重算（正文读数只到 26°）。
