# 公式规格（冻结版）— 滑聚/聚束变时长 SAR 调度：驻留时长 + 逐模式分辨率 + AASR/RASR

- 版本: v1.0（2026-09-27，票 01 SLS/时长公式族 blocking gate 产出）
- 状态: **FROZEN**——后续实现票（映射表、时长模块、AASR 硬约束、质量指标、窗域预编译）以本文件为**唯一公式来源**；修改须经新 blocking gate。
- 上游: `.scratch/sliding-spotlight-scheduling/issues/01-sls-formula-blocking-gate.md`（8 项验收 §9 对照）
- 裁决对象: `archive/next-paper-formalization/blueprint-draft.md` §2.2(c)/附 A/附 B（蓝图是二手源，本规格全部公式从 PDF 原文符号级复原，未照抄蓝图）
- 口径依据: `.scratch/sliding-spotlight-scheduling/spec.md` D4/D6/D7 + Further Notes「SLS 公式族 blocking gate」条

---

## 0. 跨源仲裁规则（规格头，全文唯一登记处）

1. **平台参数一级源 = Kim 2021**（`literature/fulltext/kim2021_aerospace_fulltext.pdf`，Aerospace 8(10):277）。TerraSAR-X（Mittermayer 线）、GF-3（Zhang 2018）、Song 2025 的平台数值**仅作映射参考**，不进 fixture；任何跨源数值冲突**以 Kim 为准登记**，冲突条目写入本规格 §8 冲突报告，不得双源并存进实现。
2. **公式（非平台数值）的取式仲裁**：同一物理量多源给式时，取与 Kim 2021 PDF 符号级复原一致的表述为主式，其余作等价式/校核式登记；Kim 未覆盖的物理量（AASR/RASR/AAP）以 Song 2025 为唯一来源（票 05/06 同）。
3. **符号约定**：本规格滑聚因子主符号取 **A ∈ (0,1)**（GF-3/Song 记号，A=1 退条带、A→0 退聚束）；蓝图/spec 中的 k 一律按 **k ≡ 1−A** 桥接（k=0 条带、k→1 聚束）。禁止两套符号混用进代码。
4. **来源类型标注**：[文献] = 具体文献+编号+PDF 页码；[教科书] = 标准教材式（Cumming & Wong / Curlander & McDonough 系）；[自推导] = 本规格构造，必须附验证证据（无验证证据的自推导不得入本规格）。

## 0.1 全文源清单（本规格全部取式出处）

| 文件（`literature/fulltext/` 相对路径） | 文献 | 用途 | 入库状态 |
|---|---|---|---|
| `kim2021_aerospace_fulltext.pdf`（2,250,797 B）+ `.txt` | Kim, Park, Chang, Lee. *Optimal Attitude Maneuvering Analyses for Imaging at Squint Staring and Sliding Spotlight Modes of SAR Satellite*. Aerospace 2021, 8, 277. doi:10.3390/aerospace8100277 | 时长/几何一级源；Table 2/3 fixture | 原在库 |
| `song2025_sensors_sparse.pdf`（8,882,508 B）+ `song2025_sensors_sparse.txt`（本票生成，逐页文本抽取） | Song, Bi, Cai, Li, Zhang, Hong. *Spaceborne Sparse SAR Imaging Mode Design: From Theory to Implementation*. Sensors 2025, 25, 3888. doi:10.3390/s25133888 | AASR/RASR/AAP 唯一来源；SLS 因子第二源 | **本票下载入库**（MDPI OA，mdpi-res.com，2026-09-27） |
| `gf3_2018_zhang_sliding.pdf`（10,325,517 B）+ `gf3_2018_zhang_sliding.txt`（本票生成） | Zhang, Xiao, Ding, Ke, Zeng. *Sliding Spotlight Mode Imaging with GF-3 Spaceborne SAR Sensor*. Sensors 2018, 18, 43. doi:10.3390/s18010043 | SLS 因子第一源；GF-3 映射参考 | **本票下载入库**（MDPI OA，mdpi-res.com，2026-09-27） |
| （未入库）Mittermayer, Lord, Borner. *Sliding Spotlight SAR Processing for TerraSAR-X Using a New Formulation of the Extended Chirp Scaling Algorithm*. IGARSS 2003, Toulouse, pp.1462-1464 | TerraSAR-X 滑聚线 | 非阻塞：IEEE 付费墙；确切书目经 GF-3 全文参考文献 [17]（`gf3_2018_zhang_sliding.txt` p.12-13）钉死；2 全文独立源门槛已由 GF-3+Song 满足，Mittermayer 降为可选旁证 | 未取（不阻塞） |

---

## 1. 符号表

| 符号 | 含义 | 备注 |
|---|---|---|
| $D$ | 天线方位向长度 | Kim **未公布**，由 $D=\lambda/\theta_a$ 推得（§7 SANITY 层） |
| $\theta_a$ | 方位向波束宽度 | Kim Table 2: 0.36° |
| $\lambda$ | 波长 | Kim Table 2: 0.031 m（9.6 GHz） |
| $R_0$ | 孔径中心斜距 | Kim Eq.(2)-(3) 由 $h$、$\theta_{inc}$ 得（值未公布，§7 SANITY 层） |
| $V_s$ | 卫星相对场景速度（ECEF 系） | Kim §2.3.2 假设三（p.7）；**数值未公布**，§7 SANITY 层 |
| $\psi_s, \psi_e, \bar\psi$ | 成像起始/结束斜视角、孔径中心斜视角 | 沿用蓝图 §1.1 / spec D6 |
| $\beta$ | 合成孔径角需求（SPT 扫描跨度）；SLS 场景级扫角另记 $\Delta\theta$ | Kim Eq.(5)/(8) 记 $\Delta\theta$ |
| $A$ | 滑聚因子（混合度因子） | $A=r_0/(R_0+r_0)=1-R_0k_\theta/v_g=\texttt{1}-$k_桥接，§2 |
| $r_0$ | 旋转中心到场景中心距离 | Kim Nomenclature（值未公布，§7） |
| $k_\theta$ | 方位扫描角速率 | Song Eq.(1)/(5) |
| $v_g$ | 地速 | Song Eq.(1) |
| $W_a$ | 距离向幅宽（=场景地距尺寸，Kim 假设幅宽覆盖场景） | Kim Table 2: 5 km |
| $\rho_a, \rho_{rg}$ | 方位/地距分辨率 | |
| $G(\cdot), G_e, G_T, G_R$ | 方位 AAP 及单元/发/收方向图 | Song Eq.(12)-(15b) |
| $\mathrm{PRF}, B_D, K_a, K_c, t_0, f_{ac}$ | 脉冲重复频率、多普勒带宽、多普勒调制率、多普勒中心变化率、目标零多普勒时刻、多普勒中心频率 | Song Eq.(4)-(10) |

---

## 2. 滑聚因子族（钉死：3 独立源一致；蓝图式证伪）

**主式（钉死）**：

$$A \;=\; \frac{r_0}{R_0+r_0} \;=\; 1-\frac{R_0\,k_\theta}{v_g}\,,\qquad A\in(0,1)\ \text{（滑聚）}$$

- $A=1$（$r_0\to\infty$ / $k_\theta=0$）⇔ 条带；$A\to 0$（$r_0\to 0$）⇔ 聚束；TOPS $k_\theta<0 \Rightarrow A>1$（本论文模式库不含）。
- 桥接：$k \equiv 1-A$（蓝图 k 记号；$k=0$ 条带、$k\to1$ 聚束）。

**出处（符号级逐条核对 PDF 页图）**：
1. [文献] GF-3 2018, `gf3_2018_zhang_sliding.pdf` **p.3**，Eq.(2)：$A = r/(R+r)$（$r$=旋转中心到场景中心，$R$=飞行路径到场景中心斜距；正文："the steering factor A is defined as [29]"）。
2. [文献] Song 2025, `song2025_sensors_sparse.pdf` **p.3**，Eq.(1)：$A = (R_{rot}-R_0)/R_{rot} = 1-R_0k_\theta/v_g$（$R_{rot}$=平台到旋转中心距离；正文明确 "$0<A<1$ in Sliding Spotlight"，$A=0$ Spotlight、$A=1$ Stripmap/Scan）。注意 $R_{rot}=R_0+r_0$，与 GF-3/Kim 完全同构。
3. [文献·隐含式] Kim 2021，**p.9**，Eq.(15)-(16)：$R_0\alpha=(R_0+r_0)(\psi_{s_0}-\psi_{s_1})$ 与 $r_0=R_0\theta_a/(\alpha-\theta_a)$ 联立 ⇔ $\alpha=\theta_a/A$（$\alpha$=点目标总 SAA）——Kim 虽未定义 A 记号，其几何与上两式严格等价（代数验证：`numerical_check.py` 末节，`theta_a/A = lam/(2ρ)` 恒等式成立）。

**定量旁证**（非取式，仅证因子链正确）：GF-3 全文 p.8 实测 $\Delta f_{dc}=18{,}000$ Hz 对应方位转角 3.8°，$V_s=7568$ m/s、$\lambda=0.555$ m：$(2V_s/\lambda)\sin 3.8°=18{,}073$ Hz（偏差 0.4%）——验证 Song Eq.(4) 多普勒中心-扫描角关系。

---

## 3. 逐模式方位分辨率 $\rho_a$（钉死）

$$\rho_{a,\mathrm{STR}}=\frac{D}{2}\,,\qquad
\rho_{a,\mathrm{SLS}}=A\cdot\frac{D}{2}\ {\buildrel k\ \text{桥接}\over=\ }\ (1-k)\cdot\frac{D}{2}\,,\qquad
\rho_{a,\mathrm{SPT}}=\frac{\lambda}{2\,\beta_{\mathrm{span}}}$$

- **STR** [教科书+Kim]：$D/2$。Kim Eq.(4)-(5)（`kim2021_...pdf` **p.6**）：$\rho_a=V_s/B_d$、$\Delta\theta=\lambda/(2\rho_a)$；条带 $B_d=(2V_s/\lambda)\theta_a$、$\theta_a=\lambda/D$ ⇔ $D/2$。Cumming & Wong 标准式。
- **SLS** [文献，2 全文源钉死]：
  - GF-3 2018 **p.3** 正文（紧随 Eq.(2)）："compared with stripmap working mode, the azimuth resolution of the sliding-spotlight mode is **improved by the factor A** as $\rho_{AZ}=A\cdot D_a/2$，where $D_a$ is the azimuth antenna length"。
  - Song 2025 **p.3**，Eq.(2)：$\rho \approx \dfrac{L_a}{2}(N_B+1)\,A$（$L_a$=天线方位向尺寸，$N_B$=子波位数；单波位模式 $N_B=0$ ⇒ $\rho=L_a A/2$；正文："with the steering angle rate increasing, Sliding Spotlight has the highest resolution … TOPS performing the worst"）。
  - 两源 + Kim 隐含式（§2 条 3）三方一致。
- **SPT** [文献·Kim Eq 反演]：$\rho_a=\lambda/(2\beta_{\mathrm{span}})$，即 Kim Eq.(5)（p.6）$\Delta\theta=\lambda/(2\rho_a)$ 的反演；$\beta_{\mathrm{span}}=\psi_s-\psi_e$ 为聚束扫描跨度（Kim Eq.(8)，**p.6**：$\Delta\theta=\lambda/(2\rho_a)=\theta_{s_0}-\theta_{s_1}$）。**口径精确化（对 spec D6 的修正，见 §8.3）**：$\rho_{a,\mathrm{SPT}}$ 是**模式库设计常数**（由 $\beta_{\mathrm{span}}$ 定），映射表 coarsest-sufficient 保证 $\rho_{a,\mathrm{SPT}}\le\rho_{\mathrm{req}}$；进 $f_Q$ 的是 achieved 值 $\lambda/(2\beta_{\mathrm{span}})$，不是需求常数。
- **斜视角修正口径注记**（实现口径声明，无未验成分）：本规格三条主式为孔径角语义（$\lambda/(2\times\text{总视角角})$），斜视角不进 $\rho_a$；spec D6「ρ_a 用孔径中心 $\bar\psi$ 语义」若需 Doppler 语义修正（$B_d\propto\cos\bar\psi$，前篇 $\cos\psi_{sq}$ 因子血统），则三模式**同乘** $\cos\bar\psi$ 因子，档序不变——修正属 D6 实现选项，不改变本节公式与档序。
- **SLS 精于条带的单调性**：$A\in(0,1)\Rightarrow\rho_{a,\mathrm{SLS}}<\rho_{a,\mathrm{STR}}$ 严格成立（GF-3 原文 "improved by the factor A"）。蓝图 §2.2(c) 单调性声明方向正确、公式错误，见 §8.1。

---

## 4. 驻留时长闭式 $T_i=T(t_i,m_i)$

### 4.1 Kim 2021 SAT 公式族符号级复原（校核层；每式 PDF 页码）

以下从 `kim2021_aerospace_fulltext.pdf` 逐页目视复原（txt 抽取件丢 subscript，仅作行号定位；页码为 PDF 页 "N of 33"）：

| Eq | 页 | 精确形式 |
|---|---|---|
| (2) | p.5 | $\dfrac{R_E}{\sin\theta_{look}}=\dfrac{R_E+H}{\sin(180°-\theta_{inc})}=\dfrac{R_0}{\sin\beta}$ |
| (3) | p.5 | $\theta_{look}=\sin^{-1}\!\Big(\dfrac{R_E}{R_E+H}\sin\theta_{inc}\Big)$，$\beta=\theta_{inc}-\theta_{look}$ |
| (4) | p.6 | $\rho_a=\dfrac{V_s}{B_d}$ |
| (5) | p.6 | $\Delta\theta=\dfrac{\lambda}{2\rho_a}$ |
| (6) | p.6 | $L=R_0\,\Delta\theta$ |
| (7) | p.6 | $\Delta t_{SAT_{broad,staring}}=\dfrac{L}{V_s}=\dfrac{R_0\Delta\theta}{V_s}$ |
| (8) | p.6 | $\Delta\theta=\dfrac{\lambda}{2\rho_a}=\theta_{s_0}-\theta_{s_1}$ |
| (9) | p.7 | $\theta_{s_a}=90°-\cos^{-1}\dfrac{\vec{s}\cdot\vec{v}_{ECEF}}{\|\vec{s}\|\cdot\|\vec{v}_{ECEF}\|}$ |
| (10) | p.7 | $L=R_0(\tan\theta_{s_0}-\tan\theta_{s_1})$ |
| (11) | p.7 | $\Delta t_{SAT_{squint,staring}}=\Delta t=\dfrac{L}{V_s}=\dfrac{R_0(\tan\theta_{s_0}-\tan\theta_{s_1})}{V_s}$ |
| (12) | p.9 | $\rho_a=\dfrac{\lambda}{2V_s}\Big(\dfrac{t-t_0}{\sqrt{R_0^2+V_s^2(t-t_0)^2}}-\dfrac{t-t_1}{\sqrt{R_0^2+V_s^2(t-t_1)^2}}\Big)^{-1}$ |
| (13) | p.9 | $\rho_a=\dfrac{\lambda}{2}\Big(\sin(\psi_{s_0}+\tfrac{\theta_a}{2})-\sin(\psi_{s_1}-\tfrac{\theta_a}{2})\Big)^{-1}$ |
| (14) | p.9 | $\psi_{s_0}-\psi_{s_1}+\theta_a=\dfrac{\lambda}{2\rho_a}=\alpha$（广角端 $\sin$ 不可小角近似的界限由 Eq.(20) 承接） |
| (15) | p.9 | $R_0\,\alpha=(R_0+r_0)(\psi_{s_0}-\psi_{s_1})=(R_0+r_0)(\alpha-\theta_a)$ |
| (16) | p.9 | $r_0=\dfrac{R_0\,\theta_a}{\alpha-\theta_a}$ |
| (17) | p.9 | $L=2(R_0+r_0)\tan\dfrac{\Delta\theta}{2}=2R_0\tan\dfrac{\Delta\theta+\theta_a}{2}+W_a$（场景级 SAL；广角近似 $\tan\frac{\Delta\theta}{2}\cong\frac{\Delta\theta}{2}$） |
| (18) | p.9 | $\Delta\theta=\dfrac{R_0\theta_a+W_a}{r_0}$（场景级波束轴扫角） |
| (19) | p.9 | $\Delta t_{SAT_{broad,sliding}}=\dfrac{L}{V_s}=\dfrac{2(R_0+r_0)\tan\frac{R_0\theta_a+W_a}{2r_0}}{V_s}$ |
| (20) | p.11 | $\psi_{s_1}=\dfrac{\theta_a}{2}+\sin^{-1}\Big(\sin\big(\psi_{s_0}+\tfrac{\theta_a}{2}\big)-\dfrac{\lambda}{2\rho_a}\Big)$ |
| (21) | p.11 | $\alpha=\psi_{s_0}-\psi_{s_1}+\theta_a=\psi_{s_0}+\dfrac{\theta_a}{2}-\sin^{-1}\Big(\sin\big(\psi_{s_0}+\tfrac{\theta_a}{2}\big)-\dfrac{\lambda}{2\rho_a}\Big)$ |
| (22) | p.11 | $L=R_0\tan\big(\theta_{s_0}+\tfrac{\theta_a}{2}\big)-R_0\tan\big(\theta_{s_1}-\tfrac{\theta_a}{2}\big)+W_a=(R_0+r_0)(\tan\theta_{s_0}-\tan\theta_{s_1})$ |
| (23) | p.11 | $A_q\tan^2\theta_{s_1}+B_q\tan\theta_{s_1}+C_q=0$，其中 $A_q=\tan\frac{\theta_a}{2}$；$B_q=\frac{r_0}{R_0+r_0}+\Big[\frac{W_a}{R_0+r_0}+\frac{R_0}{R_0+r_0}\tan\big(\theta_{s_0}+\frac{\theta_a}{2}\big)-\tan\theta_{s_0}\Big]\tan\frac{\theta_a}{2}$；$C_q=\frac{R_0}{R_0+r_0}\tan\frac{\theta_a}{2}-\tan\theta_{s_0}+\frac{W_a}{R_0+r_0}+\frac{R_0}{R_0+r_0}\tan\big(\theta_{s_0}+\frac{\theta_a}{2}\big)$（两根中取落在所需斜视角区间的一个） |
| (24) | p.11 | $\Delta t_{SAT_{squint,sliding}}=\dfrac{L}{V_s}=\dfrac{(R_0+r_0)(\tan\theta_{s_0}-\tan\theta_{s_1})}{V_s}$ |

- Eq.(23) 系数经**独立代数重推逐项验证一致**（由 Eq.(22) 两个等价形式对 $\tan\theta_{s_1}$ 消元；本轮复核曾疑 $C_q$ 末项分母为 $r_0$，经 p.11 高分辨率渲染（4× DPI）确认其为 $R_0$，与重推一致）。
- Eq.(25)-(29)（p.13-14）：姿态四元数/DCM 与**旋转中心 ECEF 位置构造**（Eq.(27) 中点式、Eq.(28) 比例式（$\|\cdot\|=W_a$）、Eq.(29) 直线参数式）——蓝图附 A 引用定位正确；D5（边界角速率）与 C1b（旋转中心几何）引用此处，本票不复原其符号细节（姿态域非本票公式族）。
- **25% 裕度**（p.7 Eq.(11) 后、p.11 Eq.(24) 后两处原文）："a margin of 25% is considered in addition to the SAT obtained from Equations (7) or (11) / (19) or (24)"——裕度加在 SAT 之上，属执行层（spec D4 裕度垫语义一致）。

### 4.2 优化器层平面地闭式（spec D4「优化器内」口径；均 [自推导·文献结构]，验证证据 §6）

统一结构：**驻留 = 视角角跨度 × 几何杠杆 / 速度**，四式共用斜视修正 $\sec^2\bar\psi$（线性化；与 Kim Eq.(22) 全式偏差 0.11% @6°、0.44% @12°，§6 表 4）：

| 模式 | 闭式 | 骨架出处 |
|---|---|---|
| STR | $T_{\mathrm{STR}}=\dfrac{\lambda R}{D\,V_s}\sec^2\bar\psi$ | [教科书] SAT=SAL/V（Kim Eq.(6)-(7) 条带极限 $A=1$） |
| SLS | $T_{\mathrm{SLS}}=\dfrac{\lambda R}{D\,A\,V_s}\sec^2\bar\psi\;=\;\dfrac{T_{\mathrm{STR}}}{A}$ | Kim Eq.(15)-(16) 点目标极限（$\alpha=\theta_a/A$）+ Eq.(24) 结构 |
| SPT | $T_{\mathrm{SPT}}=\dfrac{R\,(\tan\psi_s-\tan\psi_e)}{V_s}$，$\psi_s-\psi_e=\beta_{\mathrm{span}}=\dfrac{\lambda}{2\rho_{a,\mathrm{SPT}}}$ | **Kim Eq.(10)-(11) 逐字**（p.7）；线性化 $= \dfrac{R\beta_{\mathrm{span}}}{V_s}\sec^2\bar\psi$ |
| STR/SLS/SPT 公共注记 | $\bar\psi\to0$ 退化广角式；$|\bar\psi|$ 单调增 ⇒ $T$ 单调增（$\tan$/$\sec^2$ 凸性，蓝图 §2.2(b) 性质保留） | |

- **SLS 时长结构修正（对蓝图 §2.2(c) 的纠正，详见 §8.2）**：$(1-k)$（即 $1/A$）因子在**分母放大时长**、$\rho_{req}$ **不进**时长式——模式库常数 $A$ 唯一决定 SLS 时长档；蓝图式 $T_{\mathrm{SLS}}\approx\frac{\lambda R}{2\rho^{req}V_s(1-k)}\cdot\frac{1}{\cos\bar\psi}$ 的 $\rho^{req}$–$(1-k)$ 耦合代入一致性条件后退化为条带时长（自相矛盾），且 $\cos\bar\psi$ 方向/幂次均错（应为 $\sec^2\bar\psi$）。
- **点目标 vs 场景级口径**：上表为**点目标/场景中心**口径（优化器驻留）；Kim Eq.(17)-(19)/(22)-(24) 为**场景级**口径（波束轴扫过全场景，含 $W_a$ 项）。两口径关系：$T^{\mathrm{scene}}_{\mathrm{SLS}}=T_{\mathrm{SLS}}+W_a/(A V_s)$（广角）；调度任务=场景时（Kim Table 2 的 5×5 km 目标即场景），fixture 用场景级（§6 表 3），优化器用点目标口径并在实现票登记二选一（推荐点目标口径进优化器、场景差 $W_a/(AV_s)$ 并入裕度垫，P1 分层语义）。
- **SPT 场景尺寸包络**（C1b 足印约束的物理来源）：SPT 波束足印方位向长度为 $R\theta_a$ 量级（本参考几何 ≈4.87 km，对 5 km 场景无裕量）；滑聚靠波束滑动「maintaining the same resolution」成像更宽区域（Kim p.7 原文、摘要 overlapping-imaging 语义），场景方位尺寸超足印的任务判不可服务（映射表第三键，spec D2）。

### 4.3 校核层与误差界（spec D4「Kim 全式为实现层校核器」的落位）

- 校核器 = §4.1 Eq.(2)-(3)（$R_0$ 全曲率）+ Eq.(20)-(23)（斜视 SLS 精确解，二次方程取根规则：两解取落在 $[\theta_{s_1}^{min},\theta_{s_1}^{max}]$ 内者）+ Eq.(22)/(24)。
- 优化器闭式误差源与当前实测界：$\sec^2$ 线性化 ≤0.44%（@12°，随 $\bar\psi$ 增大）；平面地 $R_0$ 近似 ~4% $R$ 量级（蓝图 §2.3 简化声明，同前篇 $f_3$ 先例）；$|\bar\psi|\gtrsim45°$（W 档边缘）线性化失效，校核器误差超裕度垫（初值 5%）即报警升级（spec D4 语义）。

---

## 5. 逐模式 AASR / RASR（Song 2025 唯一来源；票 06 AASR、票 05 RASR 判定据此取式）

以下全部 [文献] Song 2025，符号级复原自 `song2025_sensors_sparse.pdf` p.5（Eq.(5)-(10)）与 p.6（Eq.(11)）：

**多普勒中心及其变化率**（p.4-5）：
$$f_{ac}(t)=\frac{2v_r}{\lambda}\sin\big(\theta_{ac}(t)\big)\quad(4)\qquad
K_c=\frac{df_{ac}(t)}{dt}\approx\frac{2v_s}{\lambda}k_\theta\quad(5)$$
（$\theta_{ac}$=目标方向与天线电轴的有效斜视角；条带/Scan 的 $\theta_{ac}$ 固定，聚束/滑聚/TOPS 随扫描时变。）

**条带 AASR**（p.5，Eq.(6)）：
$$\mathrm{AASR}_{St}=\frac{\sum_{m=-\infty}^{+\infty}\int_{-B_D/2}^{B_D/2}G(f_a+m\cdot\mathrm{PRF})^2\,df_a}{\int_{-B_D/2}^{B_D/2}G(f_a)^2\,df_a}$$
（与方位位置无关；$G$=方位 AAP，$B_D$=多普勒带宽。）

**聚束 AASR**（p.5，Eq.(7)，随目标方位位置 $t_0$ 变）：
$$\mathrm{AASR}_{Sp}=\frac{\sum_{m=-\infty}^{+\infty}\int_{-B_D/2-K_at_0}^{B_D/2-K_at_0}G\big(m\cdot\mathrm{PRF}-K_at_0\big)^2\,df_a}{\int_{-B_D/2-K_at_0}^{B_D/2-K_at_0}G\big(-K_at_0\big)^2\,df_a}$$

**Scan AASR**（p.5，Eq.(8)）：
$$\mathrm{AASR}_{Sc}=\frac{\sum_{m}\int_{-B_D/2-K_at_0}^{B_D/2-K_at_0}G(f_a+m\cdot\mathrm{PRF})^2\,df_a}{\int_{-B_D/2-K_at_0}^{B_D/2-K_at_0}G(f_a)^2\,df_a}$$

**TOPS / 滑聚 / Mosaic AASR**（p.5，Eq.(9)-(10)——**票 06 主式**）：
$$\mathrm{AASR}_{T,S,M}=\frac{\sum_{m=-\infty}^{+\infty}\int_{-B_D/2+f_{ac}}^{B_D/2+f_{ac}}G\big(f_a'+m\cdot\mathrm{PRF}\big)^2\,df_a}{\int_{-B_D/2+f_{ac}}^{B_D/2+f_{ac}}G\big(f_a'\big)^2\,df_a}\,,\qquad
f_a'=\Big(1-\frac{K_c}{K_a}\Big)(f_a-f_{ac})$$
（**式 (10) 的 $(1-K_c/K_a)$ 即滑聚因子谱域形态**：$1-K_c/K_a=A$ 桥接 §2——滑聚的 (1−k) 因子在谱域的正确落位是**频率轴重缩放**，不是"回波多普勒调率×(1−k)"（蓝图附 A 第 8 行的挂靠方式证伪，见 §8.4）。三式相同、差异在扫描率符号：TOPS 正、滑聚/Mosaic 负。）

**方位 AAP**（p.7-8，Eq.(12)-(15b)，票 06 积分被积函数）：$G(\theta,t)=G_e(\theta)\cdot G_T(\theta,t)\cdot G_R(\theta,t)$，$G_e(\theta)=\mathrm{sinc}^2\big(\frac{L_e}{\lambda}\sin\theta\big)$，$G_{T/R}$ 为单元激励加权和（式 (14a)/(14b)/(15a)/(15b)，$M$=收发模块数，$L_e=L_a/M$，$C_{T/R}$=激励系数）。

**RASR**（p.6，Eq.(11)——**票 05 RASR 动态范围判定主式**；模式间成因相同、逐式同型）：
$$\mathrm{RASR}=\frac{\sum_{m\neq0}\dfrac{G_r^2\big(\theta_r(r+m\cdot c/\mathrm{PRF}/2),\eta\big)\cos\big[\theta_i(r+m\cdot c/\mathrm{PRF}/2)\big]}{(r+m\cdot c/\mathrm{PRF}/2)^3\sin\big[\theta_i(r+m\cdot c/\mathrm{PRF}/2)\big]}}{\dfrac{G_r^2(\theta_r,\eta)\cos[\theta_i(r)]}{r^3\sin[\theta_i(r)]}}$$
（$\theta_i(r)$=入射角，$G_r$=距离向 AAP；模糊区 $r_m=r+m\,c/(2\,\mathrm{PRF})$。多子波位模式各子波位 PRF/入射角不同 ⇒ 逐子波位 RASR。）**评估区约定**（蓝图 4.1(5) 待定项的钉死）：单波位模式下对任务场景**近/远距离边缘各评一次、取最差**（$r$ 取场景近/远缘斜距）——Song 式为逐 $r$ 函数、无场景平均语义，取最差边缘与 D7 硬约束保守方向一致。[文献结构+实现约定]

**Song 定量锚**（票 06/05 的文献数值窗；p.8-9）：AASR 与 PRF 反相关、随扫描角增大恶化；传统滑聚扫描角 >1° 时 AASR 恶化约 **8.6 dB**（p.8）；稀疏滑聚 AASR 增约 **15.2 dB**（p.8）；稀疏模式 RASR 较传统降约 **10.7 dB**（p.8）。Song Table 1（p.7，滑聚模式参数，映射参考）：PRF 1150/2300 Hz、方位分辨率 0.5 m、方位波束宽 0.22°、平台速度 7600 m/s、最大扫描角 ±3.5°、方位幅宽 45 km、距离幅宽 90.16/45.03 km、中视角 35.24°/38.41°。
**模式参数表**：Song Table 1 按仲裁规则 §0.1 仅作映射参考，平台数值不进 fixture。

---

## 6. 档序断言数值用例表（票 03 落地为测试；手工+文献双算）

核算脚本：本票验证脚本 `numerical_check.py`（temp 归档，核心数字誊录入表；实跑输出见票回传）。平台参数全部取 Kim Table 2（PDF p.19-20），几何按 Kim Eq.(2)-(3)。

**参考几何**：$h=570$ km、$i=45°$、$\lambda=0.031$ m、$\theta_a=0.36°$、$\theta_{inc}=45°$、场景 5×5 km、$\bar\psi\in\{0°,12°\}$ ⇒ $\theta_{look}=40.4692°$、$R_0=775.43$ km [Kim 式推得，SANITY 层]；$V_s\in\{7578.05$（惯性）$,\ 7221.69$（ECEF@40°N 升段）$\}$ m/s [Kim 未公布，双口径登记，SANITY 层]；$D=\lambda/\theta_a=4.9338$ m、$A=2\rho_{\mathrm{kim}}/D=0.202683$（即 $k=0.797317$）、$r_0=197.12$ km [SANITY 层]。

**表 1：三模式 $\rho_a$ 档序（票 03 硬断言：STR > SLS > SPT 严格）**

| 模式 | 公式（§3） | 期望值 |
|---|---|---|
| STR | $D/2$ | **2.4669 m** |
| SLS | $A\cdot D/2$ | **0.5000 m** |
| SPT | $\lambda/(2\beta_{\mathrm{span}})$，$\beta_{\mathrm{span}}=2.9603°$（库设计点 $\rho=0.3$ m） | **0.3000 m** |

严格有序 ✓。**设计约束登记**：Kim 单一设计点 $\rho=0.5$ m 同时落到 SLS（$A\cdot D/2$）与 SPT（$\beta_{\mathrm{span}}=1.7762°$）⇒ 相等、不严格——模式库必须使 SPT 设计点**严格细于** SLS 档（约束传映射表票；测试用上表库点，禁用 Kim 单点凑断言）。

**表 2：优化器层驻留期望值（§4.2 闭式；s 单位，左列 $V_s$=惯性/右列 ECEF）**

| 模式 | $T(\bar\psi=0°)$ | $T(\bar\psi=12°)$ |
|---|---|---|
| STR | 0.643 / 0.675 | 0.672 / 0.705 |
| SLS（点目标口径） | 3.172 / 3.329 | 3.315 / 3.479 |
| SPT（$\rho=0.3$ m） | 5.288 / 5.549 | 5.527 / 5.802 |

（方向注记：驻留与 $\rho_a$ 反序——SPT 最细故驻留最长，即 $f_1$–$f_Q$ 张力的物理来源。）

**表 3：Kim Table 3 回验（场景级 SLS SAT × 1.25 裕度；文献双算锚）**

| 量 | 本规格公式推算 | Kim Table 3（p.29） | 偏差 |
|---|---|---|---|
| $\Delta\theta$ 场景扫角（Eq.(18)） | 2.8695° | （未公布） | — |
| $L$ 广角（Eq.(17)） | 48,717 m | （未公布） | — |
| $L$ 斜视 12°（Eq.(22)） | 50,696 m | （未公布） | — |
| SAT@12° ×1.25（$V_s$=惯性） | **8.362 s** | 目标 1 = **8.38 s** | **0.2%** |
| SAT@0° ×1.25（$V_s$=惯性） | **8.036 s** | 目标 3 = **8.08 s**（最低档） | **0.5%** |
| SAT@12° ×1.25（$V_s$=ECEF） | 8.775 s | 8.38 s | 4.7% |
| Kim 隐含 $V_s$ 窗口 | [7537, 7562] m/s | — | 介于 ECEF/惯性之间，近惯性 |

⇒ 公式族在 **$V_s\approx$ 惯性口径下 0.2–0.5% 复现 Kim 全部四值带 [8.08, 8.38] s**（目标 2/4 的 8.18/8.13 落在中间斜视角插值带上，方向一致）。Kim 的 "relative velocity" 口径无法从原文判定（未公布 $V_s$ 数值与逐目标斜视角），故 fixture 断言取**双口径覆盖带 [8.0, 8.9] s**（SANITY 层，见 §7 降级声明），**禁**按单一口径做紧等值断言。

**表 4：$\sec^2\bar\psi$ 斜视修正 vs Kim Eq.(22) 全式（自推导验证证据）**

| $\bar\psi$ | Eq.(22) 全式 $L$ | 线性化 $L_{broad}\sec^2\bar\psi$ | 偏差 |
|---|---|---|---|
| 6° | 49,202 m | 49,256 m | 0.11% |
| 12° | 50,696 m | 50,919 m | 0.44% |

**表 5：公式内部恒等式（可做精确断言，非文献拟合）**

| 恒等式 | 验证 |
|---|---|
| $\theta_a/A \overset{?}{=} \lambda/(2\rho_{\mathrm{kim}})$（§2 源 3 代数） | $0.006283/0.202683 = 0.031000$ rad ≡ $\lambda/(2\cdot0.5)$ ✓（脚本输出 `equal: True`） |
| SPT 跨度可达性 | $\beta_{\mathrm{span}}(0.3\,\mathrm{m})=2.9603° \le 2\times12°$ 包络 ✓ |

---

## 7. Kim fixture 输入向量逐分量出处登记（防凑参落窗）

**已公布分量（published；可直接进 fixture 硬断言）**：

| 分量 | 值 | 出处 |
|---|---|---|
| 轨道高度 $h$ | 570 km | Kim Table 2, PDF p.19 |
| 轨道倾角 $i$ | 45° | Kim Table 2, PDF p.19 |
| 波长 $\lambda$（9.6 GHz） | 0.031 m | Kim Table 2 + p.19 正文 |
| 波束宽 $\theta_a$ | 0.36° | Kim Table 2 续表, PDF p.20 |
| 分辨率（设计） | 0.5 m × 0.5 m | Kim Table 2, PDF p.19 |
| 场景/幅宽 | 5 km × 5 km | Kim Table 2 + §2.3.2 假设一（p.7） |
| 斜视角包络 | ±12° | Kim Table 2 + p.20 正文 |
| 成像入射角 | 45° | p.20 正文（"at an angle of incidence of 45°"） |
| 模式 | 滑聚（Table 3 SAT 所对应） | p.20 正文（"images are taken in sliding spotlight mode"） |
| 逐目标 SAT（场景 1） | 8.38 / 8.18 / 8.08 / 8.13 s；Phase-1 合计 32.77 s | Table 3, PDF p.29 |
| 场景 2 | SAT 合计 32.81 s（8.38/8.15/8.08/8.20）；Phase-2 RMT 11.06 s（3.62/3.37/4.07）；总 49.87 s | Table 3, PDF p.29 |
| Phase-2 RMT（场景 1） | 5.60 s（1.84/1.91/1.85）；总 44.37 s | Table 3, PDF p.29 |
| SAT 裕度 | 25% | p.7 / p.11 正文两处 |
| 稳定时间 | 2 s（×4 = 6 s） | Table 2 + Table 3 |
| MOI / CMG 扭矩 / 角动量 | [1000,700,500] kg·m² / 60 Nm / 40 Nms | Table 2, PDF p.19（D5 校准辅助） |
| jerk 目标权重 $k_2$ | 100 rad²/sec⁵（$k_1$=1 s） | p.19 正文（D5 校准辅助） |

**未公布分量（NOT published by Kim）——显式降级为 SANITY 层断言**：

| 分量 | 本规格推得值 | 推得途径 |
|---|---|---|
| 场景相对速度 $V_s$ | 7578.05 m/s（惯性）/ 7221.69 m/s（ECEF@40°N） | 轨道力学（$h,i$ + 地球常数）；Kim 口径不可判定（§6 表 3 隐含窗 [7537,7562]） |
| 斜距 $R_0$ | 775.43 km | Kim Eq.(2)-(3) + $h,\theta_{inc}$ |
| 天线方位长 $D$ | 4.9338 m | $\lambda/\theta_a$ |
| 滑聚因子 $A$（=$1-k$） | 0.202683（$k=0.797317$） | $2\rho_{\mathrm{kim}}/D$（GF-3/Song 关系反解） |
| 旋转中心距 $r_0$ | 197.12 km | $AR_0/(1-A)$ |
| 逐目标斜视角 | 未公布（包络 ±12° 内按序列递减） | 假设：目标 1≈12°、目标 3≈0° 仅用于回验归因 |
| $\alpha_{\max}/j_{\max}$ 包络 | 未以包络形式公布 | D5 校准用 RMT 实测值 + CMG/MOI 换代界（SANITY 层） |

**降级声明（票验收项 8 的落实）**：上表 SANITY 层分量**只允许**承担：(a) 量级/方向/带宽检查（例：§6 表 3 的 SAT 覆盖带断言 $[\text{8.0, 8.9}]$ s）；(b) 公式内部恒等式精确断言（§6 表 5——恒等式是公式一致性，不是文献值拟合）。**禁止**：(c) 对 Kim 报告值做紧等值/窄容差断言（当前任何 <5% 容差都隐含 $V_s$ 口径偷换）；(d) 实现期回调/微调 SANITY 层输入参数使输出落入文献窗（凑参落窗）——SANITY 层输入一经实现票冻结即不可调，调即新 blocking gate。前篇教训（几何/参数错则全批作废）见全局规则 11 与 spec Testing Decisions。

---

## 8. 冲突报告 + 修订建议（票验收项 5；不自行改三模式叙事）

### 8.1 🔴 蓝图 §2.2(c) $\rho_{a,\mathrm{SLS}}=D/(2(1-k))$ —— **证伪（常数挂反）**

- **文献判决**：3 独立源一致给出 $\rho_{a,\mathrm{SLS}}=A\cdot D/2=(1-k)\cdot D/2$——$(1-k)$ 在**分子**（§3）。蓝图式把 $(1-k)$ 放分母，$k\in(0,1)$ 时恒**粗**于条带 $D/2$，与蓝图自身及 GF-3 原文（"improved by the factor A"）、Song 原文（"Sliding Spotlight has the highest resolution … TOPS performing the worst"）的「滑聚细于条带」单调性矛盾——矛盾根因 = 蓝图抄式时把因子挂反。
- **方向结论（回传一句话的展开）**：文献方向 = 滑聚**细**于条带（蓝图叙事方向正确、公式错误）；修正后 $\rho_{a,\mathrm{SLS}}=(1-k)D/2$ 严格细于 $D/2$，**三模式叙事（STR 最粗、SPT 最细）无需重写，不升级用户裁决**。spec D6 的占位「SLS=D/(2(1−k)) [常数待 SLS blocking gate 钉死]」按既定 gate 流程由本规格覆盖，建议主线程在 spec 下轮修订时把该占位改为「SLS=(1−k)D/2，见 formula-spec §3」（一行改动，非叙事变更）。
- **证伪条件登记（可证伪性）**：若后续出现 ≥1 个可查全文的同级源明确给出 $\rho_a=D/(2(1-k))$ 且其 $k$ 定义与本规格 $k\equiv1-A$ 同向，则本节翻案、重开 gate。

### 8.2 🟡 蓝图 §2.2(c) SLS 时长式 $T_{\mathrm{SLS}}\approx\frac{\lambda R_i}{2\rho^{req}_i V_s(1-k)}\cdot\frac{1}{\cos\bar\psi_i}$ —— **证伪（结构耦合错误 + 修正项错误）**

- $\rho^{req}$ 与 $(1-k)$ 不能独立出现在时长式：SLS 模式 achieved 分辨率 $\rho_{a,\mathrm{SLS}}=(1-k)D/2$ 把二者锁死，代入即得 $\lambda R/(DV_s)$ = 条带时长，结构自相矛盾。正确结构：时长由**模式常数** $A$ 定（§4.2），$\rho_{req}$ 只进映射表选档（D2 语义）。
- 斜视修正：$\cos\bar\psi$（粗化方向）错；Kim Eq.(22) 全式数值验证支持 $\sec^2\bar\psi$（细化方向的反义——时长**拉长**，表 4，0.44% @12°）。
- 附 A「SLS Doppler rate $(1-k)$ 因子」条：见 §8.4。

### 8.3 🟡 spec D6「SPT=ρ_req」口径 —— **精确化（非证伪）**

$\rho_{a,\mathrm{SPT}}$ 是模式库设计常数 $\lambda/(2\beta_{\mathrm{span}})$，achieved ≤ required；进 $f_Q$ 的是 achieved（D6 主旨不变，语义从「需求常数」收紧为「库常数 ≤ 需求」）。蓝图 §4.1(2)「STR/SLS 的 ρ_a 是结果、SPT 的是要求」的结构性差异表述**保留**，但 SPT 的 achieved 同样是库常数，不随任务变。

### 8.4 🟡 蓝图附 A「SLS Doppler rate $k_a=\frac{2v^2}{\lambda R}(1-k)$（滑聚标准关系）」—— **挂靠位置错误**

文献支持的正确落位（本规格 §5）：(1−k)（=$1-K_c/K_a$，Song Eq.(10)）出现在**谱域频率轴重缩放**与**分辨率/驻留**上；回波多普勒调率由几何（$K_a$）决定，扫描改变的是多普勒**中心**变化率 $K_c$（Song Eq.(5)）。票 05/06 实现禁止引用蓝图 $k_a(1-k)$ 形式。

### 8.5 🟢 其余蓝图公式族复核结果（无冲突，按蓝图原样进实现）

$\beta_{req}=\lambda/2\rho_a$（Kim Eq.(5)）、SAT=SAL/V 框架、SPT 斜视 $\tan$ 式（Kim Eq.(10)-(11) 逐字）、STR 物理口径（P9 定案）、NESZ $\propto R^3$、RASR 教科书式、旋转中心几何（Kim Eq.(27)-(29)）——均与本规格复原一致。NESZ $g_T(T_i,m_i)$ 维持**[自推导待验证]**（本规格唯一保留的待核标记；核验归票 05，对照源 = Song 2025 §2-§3 + Cumming & Wong；降级预案 = spec D6 独立退出通道）。

---

## 9. 票 01 验收 8 项对照

| # | 验收项 | 落点 |
|---|---|---|
| 1 | Kim Eq.(17)-(24) 符号级复原 + 页码；fixture 输入向量随登记 | §4.1（含 (2)-(16) 全族）；§7 |
| 2 | SLS ρ_a 常数与 (1−k) ≥2 独立全文源钉死；全文落盘并登记路径 | §2/§3（GF-3+Song+Kim 隐含式）；§0.1 路径与字节数 |
| 3 | 零「待核」残留（NESZ g_T 除外） | 全文唯一待核标记 = §8.5 末条 g_T |
| 4 | 档序断言数值用例表（手工/文献双算） | §6 表 1-5 |
| 5 | 冲突报告 + 修订建议单列 | §8（不自行改叙事；升级判定见 §8.1） |
| 6 | 逐模式 AASR/RASR 进规格带出处（票 05/06 唯一来源） | §5 |
| 7 | 跨源仲裁规则随规格头登记 | §0 |
| 8 | Kim fixture 逐分量出处 + 未公布分量降级声明 | §7（两张表 + 降级声明四条） |
