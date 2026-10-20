# ADR 0001 — SLS 转向语义取旋转中心式（a_res ≡ A），废除 26.7567°「物理边界」

- 状态：**Accepted**（2026-10-08；裁决链 = 票 39 A-CROSS 判决 `a-cross-verdict-20261007.md`，三轨对抗审 0🔴 + 确认轮 CLOSED；用户 2026-10-07 22:08 批准实现（票 40，commit `c57b199`））
- 范围：`papers/sliding-spotlight-scheduling`（SLS 模式的 AASR 谱因子语义；驻留链/包络/冻结数据的处置）
- 关联：`formulas/formula-spec.md` v1.7 §8.14（公式注册）+ §8.15（A0 连续体 / A0b 幅宽禁令 / A3 包络语义）；票 39（spec gate）、票 40（实现）

## 1. 背景

SLS（滑动聚束）模式的天线方位扫描律在文献中有两种表述：

- **(甲) 恒定角速率**：dθ/dt = const。GF-3（Zhang 2018）§2.1 字面表述，且其 Eq.(2) 的转向因子 A=r/(R+r) 本身是旋转中心公式。
- **(乙) 对准固定虚拟旋转中心**：波束视轴恒指地表下固定虚拟点，tanψ(t)=V·t/r_rot ⇒ dθ/dt ∝ cos²ψ。Mittermayer 2003（TerraSAR-X，Eq.(1)/(6)）、Prats 2010（TGRS，"rotation center beyond the swath"；"constant rotation rate" 仅出现在其 TOPS 段）、Kim 2021（本仿真注册平台源，Eq.(15)-(24) tan 差式）、Guo 2011（北航，高斜视滑聚，"always steered about the ideal rotation center"）。

两表述在 ψ=0 处重合；运营滑聚系统的转向角仅度以下量级（TS-X steering range 1.141°，Mittermayer Table I），在该区两者数值差 <0.04% 不可分辨。本仿真的窗口斜视实测最大 26.2510°，处于两表述分岔的外推区。

**代码现状（裁决前）**：`duration.py`（场景腿 Kim Eq.22 tan 差式 + 点腿 sec²ψ̄）隐含 (乙)；`aasr.py` 的 K_c（k_θ = k·V/r₀ 常数）隐含 (甲)——同一模式两种扫描律混用，是确凿内部不一致。

## 2. 决策

1. **SLS 扫描律取 (乙)**。证据：三角核三臂收敛（DLR 精确式 / 北航·空天院高斜视算法文献明确否定线性扫描假设 / GF-3 自述其几何「simplified by linear geometry since the azimuth rotation angle is small enough」即 (甲) 是 (乙) 的小角一阶线性化）；第一性推导（cos³ 同角相消）+ 纯几何仿真双重验证。
2. **AASR 谱因子 a_res ≡ A = 1−k 常数**（K_c/K_a = r_c/r_rot = k，与斜视角无关）。26.7567°「滑聚退化为聚束的物理边界」**不存在**——它是把线性化速率外推出定义域后 a_res = 1−k/cos²ψ 的过零点伪影。a_res>0 守卫降为家族角点 k≥1。
3. **驻留链不改**：T(ψ̄) = T₀·sec²ψ̄ 是 (乙) 的精确式，`duration.py` 自票 15 起即为该形式（Kim Eq.22）。
4. **冻结数据零重跑**（判据 = 任一准入翻转 ⇒ 复活；实测 R 族 3346 窗端点 + M 族解析穷举 + promotion 决策全零翻转；R1C/R2F/R3H + M2WF/M2WH 再生成与冻结件逐字段相同）。
5. **26.9° 斜视包络保留为注册保守值**（值不变）：其原「arccos(√k) 物理边界」依据已废，现依据 = 注册的设计选择 + 冻结数据连续性；`platform_kim2021.json#modes...derivation.SLS` 的推导文字作为历史登记保留、被本 ADR 取代（冻结件不改字节）。原 (26.7567°, 26.9°] 带「duration 放行 / aasr 抛错」的分裂语义不复存在（k<1 无抛错路径）。

## 3. 方案对比

| | (甲) 恒定角速率 | **(乙) 旋转中心式（采纳）** | 混合（裁决前现状） |
|---|---|---|---|
| 语义自洽 | 自洽但分辨率 ρ∝a_res(ψ) 非均匀，违背模式设计目的（全域均匀方位分辨率） | ρ_SLS = A·D_a/2 常数（跨距口径；地面沿航向另含 secψ̄，两律同等）——**与 GF-3 Eq.(2) 分辨率式精确闭合** | 内部矛盾（驻留 (乙) / 谱因子 (甲)） |
| 高斜视行为 | 26.7567° 发散（驻留、a_res 同时），伪边界 | 无奇点；驻留 sec² 温和增长 | 读数在高斜视端虚好 ~5 dB |
| 文献支撑 | 仅小角区线性化表述（GF-3 自述） | 四组独立机构精确式一致 | 无 |
| 代价 | 驻留链重写 + 全族重跑（1.5–2 周） | **aasr.py 两处改 + 锚重登记（已落地 c57b199）** | 维持已知缺陷 |

## 4. 与 Kim 2021 分叉的论文级辩护文本（可直接进论文）

> Our sliding-spotlight model follows the rotation-centre formulation of the sliding family [Mittermayer2003, Prats2010, Kim2021]: the antenna boresight is kept pointed at a fixed virtual rotation centre below the surface, so the steering angle obeys tan ψ(t) = V_rel·t / r_rot. Some operational descriptions state the steering as a constant angular rate [Zhang2018]; this is the first-order (small-angle) linearisation of the same geometry, and the two coincide to within 1 − cos²ψ (<0.1%) in the ≈1° steering ranges of deployed systems. Our scheduling windows reach |ψ| = 26.25°, outside that regime, where only the exact geometry is valid: the spectral compression factor equals the design constant a_res = 1 − k = A (k = the registered sliding factor) at every squint (the cos³ factors of the Doppler-centroid and target chirp rates cancel at beam-centre crossing), the dwell follows sec²ψ̄ exactly, and no degeneracy boundary exists. The constant-rate reading would instead drive a_res → 0 at ψ = arccos√k = 26.76°—an artefact of extrapolating the linearised rate, which we therefore do not use.

（措辞按 anti-defensive-writing 纪律复核：只立己方语义与适用域，不攻击 Zhang2018。）

## 5. 不利后果

- 高斜视端 AASR 读数上移最多 ~4.91 dB（26° 端 −28.23→−23.32 dB，票 40 落地实测对；判决文档 §8 的 −28.26/−23.35 为判前估算对，以实测为准；保守余量收窄但仍 >10 dB）；R_fam 结构维读数下移 ~1 dB（判词全存活：R1C DEAD 不动、R2F 8.74 / R3H 10.91 ≥ 6.0 ALIVE）。
- 三处 `except ValueError → +inf` 哨兵对 k<1 成为不可达防御分支（方向由源码钉测试锁定）。
- 独立审计脚本的旧律锚需按新口径重登记（票 40 已处置 `verify_v3_verdicts.py` 与 `verify_ticket22_adjudications.py` 两台；`recompute_r_fam.py` 等其余 v3 重算链消费点留待下次审计会话核）。

## 6. 反转路径（证伪锚）

出现任一证据则重开：① 在轨指令表证据（TerraSAR-X/GF-3 运行文档公开多度量级斜视下指令角仍线性于时间且为设计选择）；② Kim 2021 平台源被证给出恒速率式且与其 Eq.(15)-(24) 冲突；③ §2.2 推导链（cos³ 同角相消/相对角速率）被驳。反转时：**整 commit `c57b199` 原子 revert**（该 commit 混装代码+测试+锚+注册，只回滚 aasr.py 会令新测试红、两台 verify 锚 FAIL、§8.14 与代码漂移）；部分回滚须同步回移 `verify_v3_verdicts.py`/`verify_ticket22_adjudications.py` 锚与 §8.14 注册。冻结数据在两语义下任务集合相同（已证），反转后仍无需重跑。

## 7. A0 模式族连续体框架（用户 2026-10-06 22:54 框架的注册版）

三模式 = 虚拟旋转点位置的单参数连续体：k=1−A，k→0（旋转点无穷远）= 条带；0<k<1（旋转点在场景以远、地表之下）= 滑聚；k→1（旋转点在目标处）= 聚束。本仿真注册工作点 k=0.7973（旋转点在场景中心以远 r₀=197 km）。**「滑聚在 arccos(√k) 退化为聚束」的表述作废**——(乙) 下 a_res≡A 对一切 ψ 成立，模式间过渡由 k 单调参数化，无退化角。k 调小 ⇒ 旋转点更远 ⇒ 分辨率增益下降、幅宽约束放松——该权衡是**传感器设计层**性质，本仿真 W_a 为规划输入，**论文不得声称「分辨率-幅宽折中」由本文仿真体现或为本文贡献**（登记为 limitation + future work，见 checklist F-9）。

## 8. 验证记录

判决文档 §9（三轨对抗审：物理重推/文献逐字/异源 CLI，0🔴 + 确认轮 CLOSED）；票 40 收口记录（全量 374P/0F/1S exit 0、verify gate PASS=12/REPORT=1/FAIL=0、变异红证、R/M 再生成字节同一）。

## 9. B-full 参数化消费（2026-10-20，票 49 blocking gate）

A0 的 $k$ 连续体允许工作点取任意 $k\in(0,1)$；票 49 把它从注册工作点 $k=0.7973$ 推广为逐任务取值 $k_{\text{task}}=1-A_{\text{task}}$，$A_{\text{task}}=2\rho_{req}\cos\psi_{\text{sel}}/D$（$\psi_{\text{sel}}$ = 评估基准时刻斜视，唯一源 `squint_at`；交付律 $\rho_{a,\mathrm{ach}}(\psi_{\text{sel}})=\rho_{req}$ 点态精确）。旋转中心几何、扫描律 $\tan\psi=Vt/r_{\text{rot}}$、$a_{\mathrm{res}}\equiv A$ 三条注册结论原样成立，只是 $r_{\text{rot}}$ 取任务值。故 B-full 不新增几何、不新增模式，是对 A0 的参数化消费；冻结工作点是其特例 $\rho_{req}=0.5\sec\psi_{\text{sel}}$（三点实测 ulp=0）。SLS AASR 在一致换算（$k$ 与 $B_D$ 同源随任务）下精确只依赖 $(\psi,\mathrm{PRF})$（$a_{\mathrm{res}}B_D=2V_s\cos\psi/D$ 与 $\rho$ 无关）。公式注册见 formula-spec v1.9 §8.17；证伪条件与读数影响面同节。
