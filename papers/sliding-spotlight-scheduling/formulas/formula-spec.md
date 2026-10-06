# 公式规格（冻结版）— 滑聚/聚束变时长 SAR 调度：驻留时长 + 逐模式分辨率 + AASR/RASR

- 版本: v1.3（2026-10-03，票 15 物理层落地：勘误登记 §8.9——驻留生产闭式切 Eq.(22)/(24) 链（§4.2 平面式降为测试 oracle）、逐模式斜视包络落 fixture（STR/SPT ±45° 设计界，SLS ±26.9° 为 $a_{\mathrm{res}}\le0$ 物理边界，非选择）、$T_{\mathrm{env,max}}$ 6.7178→10.5830 s（1.5754×，argmax SLS→SPT）、窗尾垫维持 1.00%（生产残差恒 0，纯保守余量）、$B_D$ 纠正为注册式（原实现的 cos² 口径 45° 处欠保守 29.3%）、$f_Q$ 维持零斜视口径、验收项 13 内部恒等链 $f_Q=(g_T/\rho_a)\cdot(1/\rho_{\mathrm{rg}})$；**公式本体与数值零改动**，仅落地裁决与两条被推翻的执行者初稿记录）；v1.2（2026-10-02，票 21 blocking gate 产出：勘误登记 §8.8——Song 符号源文献矛盾裁定、§2 源 2 引文回抄更正、25% 裕度计数 2→4、g_T 空指针改声明、`numerical_check.py` 死指针（3 处）改指存活 pytest 守卫 + 独立复算撤回一条错误论证（§5 桥接句不成立，Song 未给 $\mathrm{sign}(K_a)$）、撤回一条自查误判；公式本体与数值结论零改动，出处全部登记 `experiments/claim_trace.json` 由 `verify_claim_traces.py` 机检）；v1.1（2026-09-30，票 18 blocking gate 产出：新增 §3.1 逐模式 $\rho_a(m,\bar\psi)$ 封闭式 + dated 取代 §3 斜视注记（方向 cos→sec）+ Eq.(12)/(13) 约定钉死（Kim p.9 原文留痕）+ B_D 第三消费方登记 + §4.2/§4.3 生产层反转标记；勘误登记 §8.7；v1.0.1 = 2026-09-27 票 01 产出 + 两路 fresh 审查勘误轮，登记见 §8.6；v1.0 = 票 01 SLS/时长公式族 blocking gate 产出）
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
| $\psi_{s_0}, \psi_{s_1}$ | Eq.(12)-(13) 转向轴角（成像始/终） | **边缘角 = 轴角 ± θ_a/2 各自偏移；轴跨度 = α−θ_a**（§3.1 钉死，Kim p.9 原文留痕）；$t_0,t_1$ = 波束边缘穿越时刻 |
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
2. [文献] Song 2025, `song2025_sensors_sparse.pdf` **p.3**，Eq.(1)：$A = (R_{rot}-R_0)/R_{rot} = 1-R_0k_\theta/v_g$（$R_{rot}$=平台到旋转中心距离；同页正文紧接 Eq.(1) 原文（逐字）"that SAR is working in Stripmap or Scan mode. In TOPS, kθ is negative and A > 1, while in Sliding Spotlight and Mosaic mode, kθ is positive and 0 < A < 1"，另同页 "When A = 0, it indicates that the platform is working in Spotlight mode. If A = 1, this means that Rrot = ∞"）。注意 $R_{rot}=R_0+r_0$，与 GF-3/Kim 完全同构。**符号依据**：由 Eq.(1) 与 $A\in(0,1)$、$R_0,v_g>0$ 直接解出 $0<k_\theta<v_g/R_0$（滑聚 $k_\theta>0$），TOPS $A>1\Rightarrow k_\theta<0$ —— 见 §8.8 源文献符号勘误登记。
3. [文献·隐含式] Kim 2021，**p.9**，Eq.(15)-(16)：$R_0\alpha=(R_0+r_0)(\psi_{s_0}-\psi_{s_1})$ 与 $r_0=R_0\theta_a/(\alpha-\theta_a)$ 联立 ⇔ $\alpha=\theta_a/A$（$\alpha$=点目标总 SAA）——Kim 虽未定义 A 记号，其几何与上两式严格等价（**代数验证内联**（票 21 修订，原引用脚本已不存在，见 §8.8）：以 `platform_kim2021.json` 全精度值 $\theta_a=0.006283185307$ rad、$A=0.202683397006$、$\lambda=0.031$ m、$\rho_{\mathrm{kim}}=0.5$ m 代 $\theta_a/A=0.031000000000$ 与 $\lambda/(2\rho_{\mathrm{kim}})=0.031000000000$，差 $3.5\times10^{-18}$，恒等式成立。注意：本节早前版本写作 `numerical_check.py`（该脚本已不存在）并给出四舍五入后的 $0.006283/0.202683=0.031000$，该舍入显示值直算差 $8.5\times10^{-7}$（非恒等式破裂，系操作数截断所致），**以全精度值为准**；该恒等式的自动守卫为 `tests/test_duration_models.py::test_identity_theta_a_over_A_equals_lambda_over_2rho`（见 §8.8-5）。

**定量旁证**（非取式，仅证因子链正确）：GF-3 全文 p.8 实测 $\Delta f_{dc}=18{,}000$ Hz 对应方位转角 3.8°，$V_s=7568$ m/s、$\lambda=0.0555$ m（C 频段；GF-3 原文 p.4 误排为 0.555 m——其 $\Delta R_q=0.96$ m 例同样仅在该值下自洽，勘误登记 §8.6）：$(2V_s/\lambda)\sin 3.8°=18{,}073$ Hz（偏差 0.4%）——验证 Song Eq.(4) 多普勒中心-扫描角关系。

---

## 3. 逐模式方位分辨率 $\rho_a$（钉死）

$$\rho_{a,\mathrm{STR}}=\frac{D}{2}\,,\qquad
\rho_{a,\mathrm{SLS}}=A\cdot\frac{D}{2}\ {\buildrel k\ \text{桥接}\over=\ }\ (1-k)\cdot\frac{D}{2}\,,\qquad
\rho_{a,\mathrm{SPT}}=\frac{\lambda}{2\,\beta_{\mathrm{span}}}$$

- **STR** [教科书+Kim]：$D/2$。Kim Eq.(4)-(5)（`kim2021_...pdf` **p.6**）：$\rho_a=V_s/B_d$、$\Delta\theta=\lambda/(2\rho_a)$；条带 $B_d=(2V_s/\lambda)\theta_a$、$\theta_a=\lambda/D$ ⇔ $D/2$。Cumming & Wong 标准式。
- **SLS** [文献，2 全文源钉死]：
  - GF-3 2018 **p.3** 正文（紧随 Eq.(2)）："compared with stripmap working mode, the azimuth resolution of the sliding-spotlight mode is **improved by the factor A** as $\rho_{AZ}=A\cdot D_a/2$，where $D_a$ is the azimuth antenna length"。
  - Song 2025 **p.3**，Eq.(2)：$\rho \approx \dfrac{L_a}{2}(N_B+1)\,A$（$L_a$=天线方位向尺寸，$N_B$=子波位数；单波位 $N_B=0$ 为**解读式使用**——subswath 数取 0 的退化，与该文自身 stripmap 基线 $\rho=L_a/2$ 自洽，并与 GF-3 交叉一致 ⇒ $\rho=L_a A/2$；正文："with the steering angle rate increasing, Sliding Spotlight has the highest resolution … TOPS performing the worst"）。
  - 两源 + Kim 隐含式（§2 条 3）三方一致。
- **SPT** [文献·Kim Eq 反演]：$\rho_a=\lambda/(2\beta_{\mathrm{span}})$，即 Kim Eq.(5)（p.6）$\Delta\theta=\lambda/(2\rho_a)$ 的反演；$\beta_{\mathrm{span}}=\psi_s-\psi_e$ 为聚束扫描跨度（Kim Eq.(8)，**p.6**：$\Delta\theta=\lambda/(2\rho_a)=\theta_{s_0}-\theta_{s_1}$）。**口径精确化（对 spec D6 的修正，见 §8.3）**：$\rho_{a,\mathrm{SPT}}$ 是**模式库设计常数**（由 $\beta_{\mathrm{span}}$ 定），映射表 coarsest-sufficient 保证 $\rho_{a,\mathrm{SPT}}\le\rho_{\mathrm{req}}$；进 $f_Q$ 的是 achieved 值 $\lambda/(2\beta_{\mathrm{span}})$，不是需求常数。
- **斜视角修正口径注记**（~~实现口径声明，无未验成分~~【**已取代 2026-09-30 v1.1 §3.1**：本注记「同乘 cos ψ̄」方向错误（应为 sec ψ̄，斜视变粗），且自标「无未验成分」不成立——原文按 dated 取代纪律保留，勘误 §8.7-1】）：本规格三条主式为孔径角语义（$\lambda/(2\times\text{总视角角})$），斜视角不进 $\rho_a$；spec D6「ρ_a 用孔径中心 $\bar\psi$ 语义」若需 Doppler 语义修正（$B_d\propto\cos\bar\psi$，前篇 $\cos\psi_{sq}$ 因子血统），则三模式**同乘** $\cos\bar\psi$ 因子，档序不变——修正属 D6 实现选项，不改变本节公式与档序。
- **SLS 精于条带的单调性**：$A\in(0,1)\Rightarrow\rho_{a,\mathrm{SLS}}<\rho_{a,\mathrm{STR}}$ 严格成立（GF-3 原文 "improved by the factor A"）。蓝图 §2.2(c) 单调性声明方向正确、公式错误，见 §8.1。

### 3.1 逐模式 $\rho_{a,\mathrm{ach}}(m,\bar\psi)$ 封闭式（v1.1，2026-09-30 票 18 blocking gate 产出；dated 取代上文「斜视角修正口径注记」）

**取代声明**：§3 末原「斜视角修正口径注记」称修正为「三模式**同乘 $\cos\bar\psi$」——**方向错误，本节取代**（原注记自标「无未验成分」不成立，勘误登记 §8.7-1）。正确机理：Doppler 语义 $\rho_a=V_s/B_d$（§3 Kim Eq.(4)-(5) 原文），固定角跨度（$\theta_a$ 与转向跨度以角度计固定）下 $B_d\propto\cos\bar\psi$，故 $\rho_a\propto\sec\bar\psi$（**斜视变粗**）；与 §8.2/§4.2 时长族 $\sec^2\bar\psi$ 同源（带宽随斜视收窄）。双路独立验证：audit-20260930 A 路 85 检查重推导 + 主线程独立推导（$B_d\propto\cos\bar\psi$ 链），另 Kim Eq.(13) 结构自证——分母 $\sin(\bar\psi+\alpha/2)-\sin(\bar\psi-\alpha/2)=2\cos\bar\psi\sin(\alpha/2)\propto\cos\bar\psi$。

**生产式（唯一实现口径）**：

$$\rho_{a,\mathrm{ach}}(m,\bar\psi)=\frac{\rho_a(m,0)}{\cos\bar\psi},\qquad \bar\psi\in[0^\circ,45^\circ]$$

零斜视锚点（§3 三 adjudication 不变）：$\rho_a(\mathrm{STR},0)=D/2=2.4669$ m；$\rho_a(\mathrm{SLS},0)=A\cdot D/2=0.5000$ m；$\rho_a(\mathrm{SPT},0)=$ 模式库设计常数 $0.3000$ m（$=\lambda/(2\beta_{\mathrm{span}})$，$\beta_{\mathrm{span}}=2.9603°$）。零斜视处严格等于现常数（锚点回归零漂移）；各模式定义域另受包络约束（STR/SPT ±45° 设计界、SLS 物理滑动域 ~26°，spec D12③）。

**恒等核验式（Eq.(13) 逐模式实例化，非生产路径）**：$\rho_a=\lambda/(4\sin(\alpha_m/2)\cos\bar\psi)$，$\alpha_m\in\{\theta_a,\ \theta_a/A,\ \beta_{\mathrm{span}}\}$；由恒等式 $\sin(\bar\psi+\alpha/2)-\sin(\bar\psi-\alpha/2)=2\cos\bar\psi\sin(\alpha/2)$ 与生产式代数等价。实测残差（常数推导路径差，非公式差）：STR $4.1\times10^{-6}$ / SLS $2.0\times10^{-5}$ / SPT $3.3\times10^{-5}$，**全域容差 $10^{-3}$**。

**sanity 数值表（本票独立复算，sec 形式）**：

| $\bar\psi$ | STR (m) | SLS (m) | SPT (m) |
|---|---|---|---|
| 0° | 2.46690 | 0.50000 | 0.30000 |
| 12°（Kim 参考几何） | 2.52201 | 0.51117 | 0.30670 |
| 45° | 3.48873 | 0.70711 | 0.42426 |

12° 档为**恒等/单调断言**用途（Kim 未公布斜视 $\rho_a$，无外部文献锚，禁找不存在的文献值）；45° 档供票 15 实现核对。

**Eq.(12)/(13) edge-vs-axis 约定钉死（Kim p.9 原文级留痕）**：PDF p.9（"9 of 33"）原文桥接句逐字——"Since $V_s(t-t_0)/\sqrt{R_0^2+V_s^2(t-t_0)^2}=\sin(\psi_{s_0}+\frac{\theta_a}{2})$ and $V_s(t-t_1)/\sqrt{R_0^2+V_s^2(t-t_1)^2}=\sin(\psi_{s_1}-\frac{\theta_a}{2})$, Equation (12) can be expressed simply as Equation (13)."——即 $t_0,t_1$ = 波束**边缘**穿越时刻，$\psi_{s_0},\psi_{s_1}$ = **转向轴**角；**边缘角 = 轴角 ± θ_a/2（各自偏移）**，轴跨度 $\psi_{s_0}-\psi_{s_1}=\alpha-\theta_a$（与同页 Eq.(14) $\psi_{s_0}-\psi_{s_1}+\theta_a=\alpha$ 一致）。pymupdf 逐字抽取，留痕即本节引文。

**B_D 第三消费方登记（AASR 侧，spec D12②）**：

$$B_D(m,\bar\psi)=\frac{V_s}{\rho_{a,\mathrm{ach}}(m,\bar\psi)}\equiv\frac{V_s\cos\bar\psi}{\rho_a(m,0)}$$

（SANITY：SLS @45° = 7578.057×cos45°/0.5 = 10717.0 Hz。）**禁用** $V_s\cos\bar\psi/\rho_{a,\mathrm{ach}}(m,\bar\psi)$ 字面式——sec 口径下展开为 $V_s\cos^2\bar\psi/\rho_a(m,0)$，差一个 cos 因子（@45° 宽带窄 29%，反保守；spec D12② 原式已废，勘误登记 §8.7-2）。D06-8 AASR 数值期望随票 15 网格重生成时消费本式。**残差登记（票 18 验收 5 补齐）**：本闭式与 $K_a\cdot T_{\mathrm{point}}$（Eq.22 全式驻留链，D06-1 原推导）的等价残差 = $\rho_a(m,0)$ 常数链小角近似（$\sin(\alpha/2)\approx\alpha/2$ 类）+ Eq.22 tan 链 vs 闭式驻留差，合并量级 $O(\alpha^2\tan^2\bar\psi)$；上界：$\alpha_{\max}=\theta_a/A\approx1.78°\Rightarrow\alpha^2\approx9.6\times10^{-4}$，$\bar\psi=45°$ 端相对残差 $\lesssim10^{-3}$（与 §3.1 恒等容差同量级）；票 15 D06-8 期望重生成时以实测差值复核该上界。

**语义边界**：本节 sec 因子为**沿轨方位口径**（azimuth-along-track）；45° 端分辨率椭圆旋转引入的地面投影修正不在本式范围，实现与论文按外推/简化披露（spec D12④ limitation）。

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
- **25% 裕度**（Kim 2021 全文共 **4 处**，票 21 修订——原记「两处」漏 p.19/p.25；逐处原文，p.7/p.11 为执行层定义，p.19/p.25 为参数复述与结果段回述）：
  - **p.7**（Eq.(11) 后，staring spotlight）："a margin of 25% is considered in addition to the staring spotlight mode SAT obtained from Equations (7) or (11)"
  - **p.11**（Eq.(24) 后，sliding spotlight）："a margin of 25% is considered in addition to SAT at the sliding spotlight mode obtained from Equations (19) or (24)"
  - **p.19**：原文（截断排版）"The margin of SAR SAT is considered as 25%. The constant values ... of the objective function to be minimized in Equa-"
  - **p.25**（结果段回述）："the SAT in Phase 1 took about 8.08~8.38 s for all four targets (25% margin was considered)"
  
  裕度加在 SAT 之上，属执行层（spec D4 裕度垫语义一致）；四处分述 staring/sliding/参数/结果，**模式无关性证据**取 p.7 与 p.11 双例（两种模式同用同一条 25% 规则）。抽取件行号：`kim2021_aerospace_fulltext.txt:334/:512/:923/:1196`。

### 4.2 优化器层平面地闭式（spec D4「优化器内」口径；均 [自推导·文献结构]，验证证据 §6）

> 【勘误标记 v1.1 2026-09-30，spec D4 修订对齐】spec D4 已反转（2026-09-30）：驻留**生产路径 = Kim Eq.(22) 全式**（票 15 切换），本节平面闭式**降级为测试 oracle**；本节公式与 §6 验证值不动（oracle 语义下继续有效）。

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

> 【勘误标记 v1.1 2026-09-30，spec D4 修订对齐】本节「校核器」随 D4 反转**升为生产层**（票 15）；下列误差界条目语义转为 oracle-vs-全式偏差登记。

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
（**式 (10) 的 $(1-K_c/K_a)$ 即滑聚因子谱域形态**：$1-K_c/K_a\approx A$ 为**近似桥接**（$K_a$ 式用 $v_s$、$A$ 式用 $v_g$，平地 $K_a$），桥接 §2——滑聚的 (1−k) 因子在谱域的正确落位是**频率轴重缩放**，不是"回波多普勒调率×(1−k)"（蓝图附 A 第 8 行的挂靠方式证伪，见 §8.4）。三式相同、差异在扫描率符号：**TOPS 负、滑聚/Mosaic 正**（票 21 修订——原文作「TOPS 正、滑聚/Mosaic 负」，系采信 Song p.5 一句而与其 Eq.(1) 矛盾，见 §8.8）。）

**方位 AAP**（p.7-8，Eq.(12)-(15b)，票 06 积分被积函数）：$G(\theta,t)=G_e(\theta)\cdot G_T(\theta,t)\cdot G_R(\theta,t)$，$G_e(\theta)=\mathrm{sinc}^2\big(\frac{L_e}{\lambda}\sin\theta\big)$，$G_{T/R}$ 为单元激励加权和（式 (14a)/(14b)/(15a)/(15b)，$M$=收发模块数，$L_e=L_a/M$，$C_{T/R}$=激励系数）。

**RASR**（p.6，Eq.(11)——**票 05 RASR 动态范围判定主式**；模式间成因相同、逐式同型）：
$$\mathrm{RASR}=\frac{\sum_{m\neq0}\dfrac{G_r^2\big(\theta_r(r+m\cdot c/\mathrm{PRF}/2),\eta\big)\cos\big[\theta_i(r+m\cdot c/\mathrm{PRF}/2)\big]}{(r+m\cdot c/\mathrm{PRF}/2)^3\sin\big[\theta_i(r+m\cdot c/\mathrm{PRF}/2)\big]}}{\dfrac{G_r^2(\theta_r,\eta)\cos[\theta_i(r)]}{r^3\sin[\theta_i(r)]}}$$
（$\theta_i(r)$=入射角，$G_r$=距离向 AAP；模糊区 $r_m=r+m\,c/(2\,\mathrm{PRF})$。多子波位模式各子波位 PRF/入射角不同 ⇒ 逐子波位 RASR。）**评估区约定**（蓝图 4.1(5) 待定项的钉死）：单波位模式下对任务场景**近/远距离边缘各评一次、取最差**（$r$ 取场景近/远缘斜距）——Song 式为逐 $r$ 函数、无场景平均语义，取最差边缘与 D7 硬约束保守方向一致。[文献结构+实现约定]

**Song 定量锚**（票 06/05 的文献数值窗；p.8-9）：AASR 与 PRF 反相关、随扫描角增大恶化；传统滑聚扫描角 >1° 时 AASR 恶化约 **8.6 dB**（p.8）；稀疏滑聚 AASR 增约 **15.2 dB**（p.8）；稀疏模式 RASR 较传统降约 **10.7 dB**（p.8）。Song Table 1（p.7，滑聚模式参数，映射参考）：PRF 1150/2300 Hz、方位分辨率 0.5 m、方位波束宽 0.22°、平台速度 7600 m/s、最大扫描角 ±3.5°、方位幅宽 45 km、距离幅宽 90.16/45.03 km、中视角 35.24°/38.41°。
**模式参数表**：Song Table 1 按仲裁规则 §0.1 仅作映射参考，平台数值不进 fixture。

---

## 6. 档序断言数值用例表（票 03 落地为测试；手工+文献双算）

核算方式（票 21 修订，原引用脚本 `numerical_check.py` 经实测全仓 0 命中、且标注「temp 归档」已不可解析；**该恒等式的存活守卫是 pytest 而非脚本**：`tests/test_duration_models.py::test_identity_theta_a_over_A_equals_lambda_over_2rho`（`assert |θ_a/A − λ/(2ρ)| ≤ 1e-12·λ`，配方内自洽恒等），实现见 `sss_core/duration.py:63,158`。见 §8.8）：核心数字已誊入本规格 §6 表与 §7 fixture 表，读者可依表中全精度操作数复算（例：§2 源 3 的 $\theta_a/A=\lambda/(2\rho)$ 恒等式，全精度差 $3.5\times10^{-18}$）。平台参数全部取 Kim Table 2（PDF p.19-20），几何按 Kim Eq.(2)-(3)。**可机检**：全部引文出处登记于 `experiments/claim_trace.json`，由 `scripts/verify_claim_traces.py` 逐条核验（页码 + 逐字引文）。

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
| SAT 裕度 | 25% | Kim 全文 4 处（p.7 / p.11 执行层定义 + p.19 参数 + p.25 结果回述；票 21 修订，原记「p.7 / p.11 两处」） |
| 稳定时间 | 2 s（×3 = 6 s；4 目标 3 间隔，Table 3 计 (2/2/2)） | Table 2 + Table 3 |
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

$\beta_{req}=\lambda/2\rho_a$（Kim Eq.(5)）、SAT=SAL/V 框架、SPT 斜视 $\tan$ 式（Kim Eq.(10)-(11) 逐字）、STR 物理口径（P9 定案）、NESZ $\propto R^3$、RASR 教科书式、旋转中心几何（Kim Eq.(27)-(29)）——均与本规格复原一致。NESZ $g_T(T_i,m_i)$ 维持**[自推导待验证]**（本规格唯一保留的待核标记；核验归票 05；降级预案 = spec D6 独立退出通道）。**外部对照源声明（票 21 修订）**：早前版本把核对源钉为「Song 2025 §2-§3 + Cumming & Wong」，实测该钉**两腿皆空**——Song 全文 `nesz` / `noise equivalent` / `noise figure` / `SNR` 命中均为 **0**（`song2025_sensors_sparse.txt` 全部 1007 行；「noise」仅见于 `:143` SCNR、`:649` 下采样矩阵 $N$、`:761` TBR、`:962` 参考文献，无一处噪声系数方程；该文为稀疏成像模式设计，不含辐射度量方程）；Cumming & Wong 系教科书，`literature/fulltext/` 未入库（`literature/raw/` 仅有无关的 Davidson_Cumming_1997），无任何可解析页码。故本规格 g_T **无外部文献源，纯自推导**，核验方式改为**内部恒等核验**（与 §3.1 的 $\rho_a$ 恒等式、§4.3 校核层同型），并在 limitation 披露「g_T 未获外部文献交叉验证」。**不作「换一个空指针」的处置**——改指另一篇同样无 NESZ 方程的文献不构成核验。见 §8.8。

### 8.6 勘误登记（v1.0.1，2026-09-27 两路 fresh 独立审查后）

独立审查（formula 取式路 + fork 边界路，均 0 critical）发现并已修，全部不触公式本体与数值结论（审查复算：§6 全表命中、三 PDF 取式零错误、Kim Eq.(23) 系数独立重推吻合）：

1. **§2 定量旁证 λ 值**：原照抄 GF-3 原文 p.4 的 0.555 m 排版错误——18,073 Hz 仅在 C 频段 0.0555 m 下成立（按 0.555 复算只得 1,807 Hz）。已改 0.0555 m 并注记原文错误；旁证结论（0.4% 偏差验证 Song Eq.(4)）不受影响。
2. **§7 稳定时间**：「×4 = 6 s」算术错，实为 2 s × 3 间隔 = 6 s（Table 3 计 (2/2/2)）。
3. **§3/§5 标注补强**：Song Eq.(2) 单波位 $N_B=0$ 补「解读式使用」标注；$1-K_c/K_a\approx A$ 补「近似桥接」（$v_s$ vs $v_g$）标注。
4. **§0.1 GF-3 PDF 登记路径**：登记名与盘上文件名不一致（sensors vs zhang），以盘上文件改名落实，路径现已可解析（10,325,517 B 核对一致）。

残留已知项（接受不修）：§6 表 2 SPT@12° ECEF 格 5.802 与独立复算 5.798–5.800 差 ≤0.05%（舍入级；票 03 以本表为期望值带实现）。

### 8.7 勘误登记（v1.1，2026-09-30 票 18 blocking gate；gate-review 确认轮 ALL-CLOSED）

1. **§3 斜视角修正口径注记方向错误**：原注记（现 :81 附近）称修正为「三模式同乘 $\cos\bar\psi$」且自标「无未验成分」——两处均不成立。Doppler 语义 $\rho_a=V_s/B_d$、固定角跨度 $B_d\propto\cos\bar\psi$ ⇒ $\rho_a\propto\sec\bar\psi$（斜视**变粗**非变细）。audit-20260930 双路独立推导 + Kim Eq.(13) 结构三方一致。已由 §3.1 dated 取代（原注记保留原文 + 取代标记，非删除）。
2. **B_D 公式 cos 因子重复计入（spec D12② 侧错误，本文件登记正式式）**：spec D12② 原登记 $B_D=V_s\cos\psi/\rho_{a,\mathrm{ach}}(\psi)$ 在 sec 口径下字面展开 $=V_s\cos^2\bar\psi/\rho_a(m,0)$，差一个 cos 因子（@45° SLS 宽带 10717 vs 7578 Hz，窄 29% 反保守）。正式式见 §3.1：$B_D=V_s/\rho_{a,\mathrm{ach}}(m,\bar\psi)\equiv V_s\cos\bar\psi/\rho_a(m,0)$。spec D12② 已同步勘误（2026-09-30 gate-review P0-1）。
3. **§4.2/§4.3 分层标签过时**：spec D4 2026-09-30 反转（生产 = Kim 全式、平面式降 oracle）后，两节标题沿用旧「优化器层/校核层」称谓——已加 dated 勘误标记，正文公式与 §6 验证值不动。

### 8.8 勘误登记（v1.2，2026-10-02 票 21 blocking gate；溯源门禁机检）

本轮修订全部属**来源指向与计数一致性**，**未改动任何公式本体或数值结论**（audit3 已确认公式层 P0=0、幻觉引用 0）。逐条出处已登记入 `experiments/claim_trace.json`，由 `scripts/verify_claim_traces.py` 逐条机检（页码 + 逐字引文，定位与引文相互独立）。

1. **Song 2025 转向角速率符号源文献自相矛盾 — 裁定取 p.3，p.5 判为源文献笔误**：Song 全文两处给出相反符号——
   - p.3（`song2025_sensors_sparse.txt:163-164`，紧接 Eq.(1)）："In TOPS, kθ is negative and A > 1, while in Sliding Spotlight and Mosaic mode, **kθ is positive** and 0 < A < 1"
   - p.5（`:317-318`）："TOPS has a **positive** rate. Sliding Spotlight and Mosaic have a **negative** one"
   
   裁定取 p.3，**决定性依据 = 该文 Eq.(1) 自身的代数**：`A=1-R_0k_\theta/v_g`（`:156-159`）配 $A\in(0,1)$ 与 $R_0,v_g>0$，直接解出 $0<k_\theta<v_g/R_0$（滑聚 $k_\theta>0$）；TOPS $A>1\Rightarrow k_\theta<0$。p.3 与该方程逐条自洽，p.5 与之矛盾而 p.5 自身无方程支撑 —— 故 p.5 判为源文献笔误。旁证：GF-3（$A=r/(R+r)$、$\omega_r=\theta/T>0$）与 Kim（$r_0>0$ 几何）均与 p.3 同向，无源支持 p.5；本规格 §2（`:58`，TOPS $k_\theta<0$）本已采 p.3，改后与 §5 一致，同时消除规格内部矛盾。已改 §5 符号标签为「TOPS 负、滑聚/Mosaic 正」（**原句保留在本条登记内，非静默改**）。**⚠️ 撤回一条错误论证（票 21 独立复算发现）**：本条初版曾以「§5 桥接句 $1-K_c/K_a\approx A\in(0,1)$ 反证 p.5」为第二依据 —— **该论证不成立**：Song 全文仅在 `:287` 指名 $K_a$ 为「Doppler-modulated frequency」，**从未给出其符号**，桥接式对 $\mathrm{sign}(K_a)$ 不敏感（取 p.5 只须同时假定 $\mathrm{sign}(K_a)=\mathrm{sign}(K_c)$ 即可自洽，sign-neutral）。该错误源于默认 $K_a>0$ 而源中无据。**现仅以 Eq.(1) 代数立论，不依赖 $\mathrm{sign}(K_a)$**。**残留不确定**：Eq.(1) 为精确式（无 ≈），故符号结论无近似 caveat（初版援引 Eq.(5) 的 ≈ 号作 caveat 属多余）；仍不能排除 p.5 另指他量，故以本条显式登记而非默认采纳。**翻判条件**：出现同级第三方源明确给出滑聚 $k_\theta<0$。
2. **§2 源 2 引文系回抄渲染版（非原文）**：原记正文明确 "$0<A<1$ in Sliding Spotlight" 并置于引号内，实测该串在 Song 全文 **0 命中**；原文为 `kθ is positive and 0 < A < 1`（不等式有空格、符号归 $k_\theta$）。已替换为两段逐字原文（`A=0`/`A=1` 释义句一并补全）。数学结论未变。
3. **「25% 裕度」计数 2→4**：Kim 全文实为 **4 处**（p.7 / p.11 执行层定义、p.19 参数、p.25 结果回述；抽取件 `:334/:512/:923/:1196`），原记「p.7 / p.11 两处」漏 p.19/p.25。`experiments/platform_kim2021.json` 记 3 处漏 p.19，且其自身 `:159`（已引 p.25）与 `:180`（仅列 p.7/p.11/p.25）**互相矛盾**。§4.1 与 §7 表格两处同步改；模式无关性双例证据保留 p.7/p.11。
4. **g_T 核对源空指针 → 显式声明无外部文献源**：原钉「Song 2025 §2-§3 + Cumming & Wong」，实测 Song 全文 `nesz`/`noise equivalent` **命中 0**（该文为稀疏成像模式设计，不含辐射度量方程）；Cumming & Wong 未入库、无可解析页码。改为显式登记「**无外部文献源，纯自推导 + 内部恒等核验**」，核验方式与 §3.1/§4.3 同型，并要求在 limitation 披露「g_T 未获外部文献交叉验证」。**影响**：票 15 验收项 13 的 f_Q 独立复算不再依赖外部锚，改依内部恒等链。
5. **`numerical_check.py` 死指针（3 处）**：`:64`、`:224` 引用该脚本（`:224` 自标「temp 归档」），实测**全仓 0 命中**（`src/tools/check_numerical.py` 属 Ch3 无关工具）。**⚠️ 本条初版误称「无等价脚本」——独立复算纠正**：该恒等式的存活守卫是 **pytest 而非脚本**——`tests/test_duration_models.py::test_identity_theta_a_over_A_equals_lambda_over_2rho`（`assert |θ_a/A − λ/(2ρ)| ≤ 1e-12·λ`，docstring 明写「Formula-spec §6 table 5」），实现见 `sss_core/duration.py:63,158`。故正确处置是**改指该测试**而非仅删除指针；现已改指，并把全精度操作数与实测残差（$\theta_a/A$ 与 $\lambda/(2\rho)$ 差 $3.5\times10^{-18}$）就地写进正文，使读者无须跑测试亦可复算。⚠️ 附带更正：早前 §6 表列 $0.006283/0.202683=0.031000$ 并注 `equal: True`，但按该**四舍五入显示值**直算差 $8.5\times10^{-7}$（恒等式本身成立，系操作数截断造成的显示误导）——已注明以全精度值为准。
6. **🟢 撤回一条自查发现（Kim p.9 桥接句标签，原判有误）**：本轮初查曾据 `.txt` 抽取件（`Since  ( ) = sin  + and`，符号被丢）判定 §3.1「pymupdf 逐字抽取」标签失实。**经 pymupdf（fitz 1.27.2.3）直抽 PDF p.9 复核：该句结构完整、字形呈 mojibake**（`ටోඬమା౞మ(௧ି௧బ)మ= sin ቀ𝜓௦బ+ … ఏౌశቁ and … = sin ቀ𝜓௦భ− ఏౌశቁ, Equation (12) can be expressed simply as Equation (13).`），与规格渲染式同构 ⇒ **规格标签正确，不改**。教训：`.txt` 抽取件不能裁决一条声明来自**另一种抽取器**的引文。

**机检口径**：本轮 11 条 claim 中，销账 5 条（§8.8-1~5 覆盖 F1×3 / F2×4 / F3 / F5 的重复归并），`claim_trace.json` 对应 `status` 转 `verified`/`closed` 后 `verify_claim_traces.py --strict` 应 rc=0。**回归面**：两个互不相交测试面（`src/tests/` 共享库 145 + 本域 `papers/sliding-spotlight-scheduling/tests/`），计数以 `--co` 实测为准，勿写死。

### 8.9 勘误登记（v1.3，2026-10-03 票 15；物理层落地 append-only）

本轮**未改动任何公式本体**——§3.1 的 $\rho_{a,\mathrm{ach}}$ 式、§4.1 的 Eq.(20)-(24) 链、§5 的 AASR 族全部原样；本节登记的是**落地裁决**与其**被推翻的候选**。

1. **驻留生产闭式 = Eq.(22)/(24) 链（spec D4 反转的落地，票 15）**。§4.2 的平面 $\sec^2$ 闭式**降级为测试 oracle**（实现为 `duration_scene_planar_oracle`），不再进生产路径。落地口径：
   - **SLS**：生产 = `kim_checker_scene_sls` 的 `sat_raw_s`，即 §4.1 Eq.(22)/(24) 的对称 α 构造。平面式在 $\bar\psi=12°$ 偏 **+0.4185%**、在 SLS 物理边界 $26.9°$ 偏 **+2.1025%**、在 $45°$ 偏 **+5.3048%**——后者超 1% 冻结垫 5.3 倍，故必须切。
   - **STR**：生产 = tan 精确场景渡越 `_tan_diff_s(ψ,θ_a,R_0,V_s) + W_a/V_s`。实测平面式在 $45°$ 仅偏 **−0.0009%**（$\theta_a=0.36°$ 极窄 ⇒ $\sec^2$ 线性化几乎无损），**切换不动物理**，理由是口径统一与消除「STR 也在 45° 失效」的误读。
   - **SPT**：**不动**。`_tan_diff_s` 本就是 §4.1 Eq.(10)-(11) 的精确式，$45°$ 处与平面线性式仅差 **−0.0890%**。
2. **逐模式斜视包络（§3.1 域的具体化）**：STR/SPT **±45°**（spec D12-3 设计界，**无文献源**，注册的设计选择）；SLS **±26.9°**，该值**不是选择**而是 $a_{\mathrm{res}}=1-K_c/K_a\le 0$ 在库 $k=0.797317$ 处的物理滑聚边界（D06-3 守卫）。登记于 `experiments/platform_kim2021.json#modes.mode_squint_envelope_deg`，**与 Kim Table 2 的 ±12° 任务包络分列两个字段**（前者物理域、后者文献任务域，合并即洗白来源）。
3. **$T_{\mathrm{env,max}}$ 迁移（本轮推翻执行者初稿）**：C3/C4 归一化参考从「单一 12° 平台边」改为「逐模式包络边」，实测 **6.7178 s → 10.5830 s（1.5754×）**，argmax **SLS → SPT**。⚠️ 执行者初稿取 **12.8548 s / 1.91×**，那是**旧平面式在 45° 的值**，**违反本规格自设的 SLS ≤26.9° 包络**，已作废。
4. **窗尾垫维持 1.00%（本轮推翻执行者初稿）**：切换后生产闭式**即**物理参考，生产残差**恒 0**，1.00% 退化为纯保守余量（`e ≤ w_e` 的余量只缩可行集、不漏解）。⚠️ 执行者初稿据「SLS 平面 oracle 在包络边偏 2.1025%」推出「垫须升至 3.50%」，**该推理作废**：抬垫守的是一条**生产路径永不计算**的残差，属对已退役 oracle 的症状加垫。`WINDOW_TAIL_PAD_FROZEN` 冻结值不变，`window_tail_pad_report()` 改为**记录** oracle 缺口并按模式断言保守方向（SLS 绑定区 $\ge 11.9°$ 全为正，min **+0.4112%**；STR 全域为负但量级 $10^{-5}$，故**不宣称保守**，只受垫覆盖）。
5. **$B_D$ 口径纠正（执行者与独立审查双方各错一半，实测定案）**：注册式为 $B_D=V_s\cos\bar\psi/\rho_a(m,0)$。⚠️ 实现原写 `Vs*cos(psi)/rho_az_ach`，在 §3.1 的 sec 形式下展开即 $V_s\cos^2\bar\psi/\rho_a(m,0)$，**正是 §3.1 明令禁用的 cos² 口径**——$45°$ 处比注册式窄 **29.3%**，**欠保守**。独立审查误判为「代码已等于注册式、无需改动」，实测推翻：**须改**。现实现为 `ModeLibrary.bandwidth_d_hz`（注册式），SLS@45° = **10716.99 Hz**，与 §3.1 SANITY 登记值 **10717.0 Hz** 逐位吻合。
6. **$f_Q$ 维持零斜视口径（执行范围裁决）**：§3.1 的 $\rho_{a,\mathrm{ach}}(m,\bar\psi)$ 已函数化并供 $B_D$ 与上报使用，但 **$f_Q$ 表达式仍取零斜视常数 $\rho_a(m,0)$**。理由：D05-4 时间不变性与 `verify.py::scatter_precheck` 的「结构散布 ~2e-4、已知结果」两条注册断言都建立在常口径上；令 $f_Q$ 随 $\bar\psi$ 变会同时失效二者，且超出本票授权。
7. **验收项 13 的内部恒等链**（承接 §8.8-4 的「g_T 无外部文献源」裁决）：$f_{Q,i}=(\rho_{\mathrm{rg}}\rho_a)^{-1}g_T(R_0/R)^3$，在 $R=R_0$ 下化为 $f_Q=(g_T/\rho_a)\cdot(1/\rho_{\mathrm{rg}})$，隐含量 $1/\rho_{\mathrm{rg}}=2.0$ 为**模式无关常数**（$\rho_{\mathrm{rg}}=0.5$ m 设计锚，D05-1）⇒ 这就是「$f_Q\propto 1/\rho_a$」的精确陈述。守卫 `tests/test_quality_fq.py::test_fQ_inverse_rho_a_squared_identity`，容差 3e-4（容 SPT 的 D05-3 残差 0.022%）。

8. **⚠️ 45° 段读数的外推标注（票 17 红线 R3 的落点，2026-10-03 补记）**：本规格 §3.1:115 已就**分辨率**的 45° 端披露过外推（椭圆旋转的地面投影修正不在式内），但**驻留闭式**的 45° 段此前**无对应标注**——而票 15 正是把生产闭式推到 45°。现补记：
   - **STR/SPT 的 45° 段**：`_tan_diff_s` 在 $ar\psi=45°$ 处为**平面精确式**（flat-earth tan 差），但该式**未含地球曲率**；库内 R0 取自全曲率 Eq.(2)-(3)，两者在 45° 端**不自洽**（平面 tan 以 R0 为半径，与球面弦距在高角处发散）。⇒ 45° 段驻留读数按**外推**披露。
   - **SLS 的 26.9° 段**：该处为 `a_res = 1-K_c/K_a = 0` 的**物理边界**，非外推；边界外（26.9°–45°）Eq.(22) 闭式**仍可求值**（45° 处 12.207 s）但**无任何已注册约束能认证该域**，故实现以域守卫 fail-loud 拒绝，而非返回未认证的读数。
   - **落点**：`sss_core/duration.py` 的 `SQUINT_ENVELOPE_DEG` / `SLS_MAX_SQUINT_DEG` 与 `mode_squint_envelope_rad` 为唯一注册处；论文 limitation 须承接本条。

**冻结声明**：本节为 append-only 勘误，§1–§7 的公式本体与数值**零改动**；本轮改动全部落在实现层与 fixture 的包络登记字段。

### 8.10 勘误登记（v1.4，2026-10-06 票 31；写作前文档卫生）

本节**零公式改动**——登记的是写作期必须知道的**释义漂移 / 死指针 / 悬空待核标记**三处。
§1–§7 的公式本体与全部数值一字未动；§8.1–§8.9 的正文亦未改写。

1. **§1 符号表 $W_a$ 的方向性释义与其在 Eq.(17)/(22) 中的沿轨用途相反（audit4 C4）**。
   §1 现记「$W_a$ = 距离向幅宽（=场景地距尺寸，Kim 假设幅宽覆盖场景）」。但 Eq.(17)
   与 Eq.(22) 中 $W_a$ 是**加在波束轴扫掠项之后的场景沿轨（across-track / 场景方位向）
   场景长度项**——Kim 的 $L$ 是场景级覆盖长度，其中 $2R_0\tan(\cdots)$ 扫过的是方位角张开的
   距离向跨度，$W_a$ 补的正是**沿轨方向**的场景尺寸。两句话在 5 km **方形**场景下数值无差
   （Kim Table 2：5 km × 5 km），故本规格历次复算从未暴露该冲突。
   ⇒ **论文符号表的处置**：写「**场景（方形）尺寸**」或直接**不给方向性释义**；
   **禁**写「距离向幅宽」这一方向性说法。§1 原文按 append-only 保留不改。
   **本规格内部另有独立旁证**：§4.2 的「点目标 vs 场景级口径」段记
   $T^{\mathrm{scene}}_{\mathrm{SLS}}=T_{\mathrm{SLS}}+W_a/(AV_s)$，该 $W_a$ 项即场景级覆盖
   所需的渡越时间——与 Eq.(17)/(22) 中 $W_a$ 的角色一致，与「距离向」的方向性说法不一致。

2. **§6 表 5 的死指针清理注记（audit4 C6）**。§6 表 5 首行仍留「（脚本输出 `equal: True`）」，
   而 §8.8-5 已判定该脚本 `numerical_check.py` **全仓 0 命中**（`:64` / `:224` 两处引用皆死），
   并已改指存活守卫 `tests/test_duration_models.py::test_identity_theta_a_over_A_equals_lambda_over_2rho`。
   ⇒ §6 表 5 的 `equal: True` 字样是**同一死指针的残留**，其所指脚本不存在。
   正确读法：**以全精度操作数复算**（实测 $\theta_a/A$ 与 $\lambda/(2\rho)$ 差 $3.5\times10^{-18}$），
   或跑上述 pytest。§6 表 5 原文按 append-only 保留；**判定依据以本条为准**。
   （配套提醒见 §8.8-5 末句：表中 $0.006283/0.202683=0.031000$ 系四舍五入显示值，
   按显示值直算差 $8.5\times10^{-7}$，**恒等式本身成立**，勿据显示值判红。）

3. **§8.5 末条 g_T「[自推导待验证]」挂指针 → §8.8-4 终裁（audit4 C6）**。§8.5 末尾保留
   「NESZ $g_T(T_i,m_i)$ 维持**[自推导待验证]**」，并注明「核验归票 05」。**该指向已被终裁取代**：
   §8.8-4 已裁定 g_T **无任何外部文献源**（Song 全文噪声方程命中 0；Cumming & Wong 未入库），
   核验方式改为**内部恒等核验**（与 §3.1 的 $\rho_a$ 恒等式、§4.3 校核层同型），
   并要求 limitation 披露「g_T 未获外部文献交叉验证」。
   ⇒ 本规格**唯一保留的「待核」标记的终态是「无外部文献源 + 内部恒等核验 + 论文 limitation 披露」**，
   不是「等待外部文献验证」。§9 验收项 3 所称「全文唯一待核标记 = §8.5 末条 g_T」按本条读。
   「核验归票 05」的指向作废（票 05 已闭）；g_T 的口径**未被本节改动**。

**冻结声明**：本节同为 append-only 勘误，§1–§7 公式本体与数值**零改动**。
三项均为**写作期义务**（见 `.scratch/sliding-spotlight-scheduling/writing-checklist-20261005.md`
公式写作指引 F-1/F-2/F-3），无一项要求回改实现。

### 8.11 勘误登记（v1.5，2026-10-06 写作前全面审计；零公式/零代码改动）

本节**零公式改动、零代码改动**——登记写作前全面审计（主线程实跑五道门禁 + 域套件 228P/1S exit 0
+ 两路独立 fresh 审查）挖出的**两处登记精度缺口**。被指正处原文按 append-only 保留，判定以本条为准。

1. **SLS 斜视包络 26.9° 是物理边界的保守上界，精确根为 26.7567°（独立审查 P2）**。
   §8.9-2（`:385`）称 SLS ±26.9° 「不是选择而是 $a_{\mathrm{res}}=1-K_c/K_a\le0$ 在库 $k=0.797317$
   处的物理滑聚边界」，§8.9-8（`:394`）称该处「$a_{\mathrm{res}}=0$ 的物理边界，非外推」。
   **实测**：$a_{\mathrm{res}}=1-k/\cos^2\bar\psi$ 的根精确为 $\bar\psi=\arccos\sqrt{k}=$
   **26.7567°**；在登记值 26.9° 处 $\cos^2\bar\psi=0.795303$、$a_{\mathrm{res}}=-0.002533$（已在域外）。
   ⇒ 26.9° **不是**边界本身，而是**比精确根宽 0.1433° 的保守上界**。
   - **代码不动**：硬编码 `sss_core/duration.py:88`（`SLS_MAX_SQUINT_DEG=26.9`）与
     `sss_core/aasr.py:368`（网格域检查）同取宽值 ⇒ band $(26.7567°,\,26.9°]$ 内
     **驻留闭式与网格域检查放行，而 `aasr_direct` 抛 `a_res <= 0`**（D06-3 守卫）。
     band 内读数属**未认证外推**，非错误值；且该 band 宽 0.14°，无任何真实几何落入。
   - **数据影响实测为零**：v3 真窗族**全部 1673 个 SLS 任务窗入射角 ∈ [30.032°, 59.967°]**
     （`experiments/v3_results/scenarios/*.json` 逐窗扫描），与 band **零交集**。
   - **⇒ 写作处置**：论文**禁**称 26.9° 为「$a_{\mathrm{res}}=0$ 的精确物理边界」；
     应写「物理滑聚边界 $\arccos\sqrt{k}=26.76°$，实现取 **26.9° 保守上界**」。
     §8.9-8 首段的 45° 段外推标注**不变**。
   - **修复触发条件**：任一场景入射角落入 $(26.7567°,\,26.9°]$（当前 1673/1673 窗外）时，
     须把常量改为 $\arccos\sqrt{k}$ 或显式登记为近似，并复跑受影响真窗单元。
   - **配套登记**：`experiments/platform_kim2021.json#modes.mode_squint_envelope_deg.derivation.SLS`
     同一措辞（「the physical sliding-spotlight boundary, not a choice」）同受本条纠正；
     该字段**值不改**（26.9 仍是被代码消费的注册上界）。

2. **§4.2「点目标 vs 场景级口径」的 $T^{\mathrm{scene}}_{\mathrm{SLS}}$ 式为 stale 侧（独立审查 P2）**。
   §4.2（`:175`）记 $T^{\mathrm{scene}}_{\mathrm{SLS}}=T_{\mathrm{SLS}}+W_a/(AV_s)$（广角），
   即 $W_a$ 项在 $\sec^2$ **之外**；实现 `sss_core/duration.py:201-206`
   `duration_scene_planar_oracle` 的 SLS 支为 $(R_0\theta_a+W_a)/(AV_s)\cdot\sec^2\psi$
   ——**$W_a$ 在 $\sec^2$ 之内**。实测 $12°$ 处代码式与生产 Eq.(22) 值差 **+0.4185%**，
   §4.2 记法差 **−1.74%**；§8.9-1 已登记 **+0.4185% @12°** 为实测正典
   ⇒ **§4.2 是 stale 侧**。
   ⇒ 引用场景级 $T^{\mathrm{scene}}$ 时**以代码 oracle 形式（$W_a$ 在 $\sec^2$ 内）+ §8.9-1 的
   +0.4185% 为准**，**禁引 §4.2 字面式**。该 oracle 已由 §8.9-1 降级为**测试比对件**、不进生产
   路径 ⇒ **零数据影响**。§4.2 原文 append-only 保留。

### 8.12 登记包精度缺口（2026-10-06 写作前审计数据层；登记层，非数据层）

1. **`RUN_LINEAGE.md` N2 行的「全密度、全预算下 max 3.891 dB」只引了 L2 单值**。
   主线程逐档重算三档最大 spread：`L1` `results/matrix` = **1.0137 dB**、
   `L2` `results/probe_density` = **3.8906 dB**、
   **`L3` `results/probe_convergence` = 5.0009 dB**（`pilot_P7WH_seed701_p160_g240.json`）。
   ⇒ 「3.891」是 L2 单值，**L3 未被引用**；而「全预算」是 L3 的轴（1×/4×/16×/64× 阶梯）。
   **结论不变**：$5.0009 < 6.0$ 仍成立、no_promotion 终局口径**不动**。属精度非阈值错误。
2. **caliber 门禁未强制 v3 条目**（`sss_core/verify.py:336` `caliber_registry_present()`）：
   只断言 `{"v1","v2"} ⊆ set(calibers)` + 互不可比，**不含 v3** ⇒ 删掉 v3 条目该门禁仍 PASS。
   v3 条目**当前在盘且正确**，不构成数据风险；风险在写作义务 A4「caliber 标签随行」的
   **机器强制缺位**（registry 自身 `#rule` 是约定式声明，弱于其检查）。
3. **v2 caliber 条目无 `code_head`**：`caliber_registry.json` v2 条目只记 `produced_after`
   （ticket 16/17），无 `code_head`（对照 v1 有 `20ff465/d0d32f2`、v3 有 `220a796`）；
   `RUN_LINEAGE.md` L5 行证据列只列工件路径、无产出 commit。
   ⇒ 唯一仍有效的 v2 件（`v2_results/confound_control.json`，M 族）**无产出 commit 记录**。
   **不改数据的修法**：引用该件时注明「v2 caliber，产出 commit 未登记（M 族受控参照）」。

**冻结声明**：本节**零公式、零代码、零数据、零阈值改动**，全部为登记精度与写作措辞义务。
前三项均为**写作期义务**（增补进 `writing-checklist-20261005.md` 的 F-8/F-9 与 D-6），
无一项要求回改实现或重跑矩阵。

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
