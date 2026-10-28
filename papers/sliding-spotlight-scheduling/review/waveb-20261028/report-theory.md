# paper2 理论/公式核验报告（§2–§4）

审查席：理论/公式审查（只读）。对象：`papers/sliding-spotlight-scheduling/paper/main.tex`（当前 HEAD 工作树，含本轮新增 Fig 2/4/6/7/8）。
日期：2026-10-28。方法：Read 全文逐段 + 用 `sss_core`（只读导入）独立复算，不照论文转写；每个数字都自己算一遍再比对。

---

## 0. 审查红线（先复述）

1. 只读：未修改仓库任何文件；唯一写入是本报告。
2. 每条发现带 `file:line` + 原文引句 + 为什么是问题 + 建议修法；无引句的发现作废。
3. 严重度：P0=事实错/数字错/物理错/自相矛盾（必须修）；P1=论证缺口/口径漂移/误导读法（应修）；P2=表述与结构（可选）。
4. 不确定处标 QUESTION，不把口味当缺陷。
5. 审的是当前 HEAD 工作树。

---

## 1. 复算基线（下面所有发现都引这一节的自算值）

用论文自己列出的常数（θa=0.36°、λ=0.031 m、h=570 km、η=45°）从零复算：

| 量 | 论文值 | 我算得 | 结论 |
|---|---|---|---|
| D = λ/θa | 4.9338 m | 4.933803235848756 | ✓ |
| R0（η=45° 斜距） | 775.4 km | 775.426138 km | ✓ |
| vs = √(μ/(Re+h)) | 7578.05 m/s | 7578.056966 | ✓ |
| A = r0/(R0+r0) | 0.202683397006 | 0.2026833970057931 | ✓ |
| k = 1−A = R0/(R0+r0) | 0.797317 | 0.797316603 | ✓ |
| r0 | 197 119 m | 197 118.689 m | ✓ |
| r0/R0 | 0.254207 | 0.2542069 | ✓ |
| ρ_STR=D/2 / ρ_SLS=A·D/2 / ρ_SPT=λ/(2β_span), β=2.9603° | 2.4669 / 0.5000 / 0.3000 | 2.4669016 / 0.5000000 / 0.3000000 | ✓ |
| θa/A = λ/(2ρa) 残差 | 3.5e−18 | −3.47e−18 | ✓ |
| arccos(√k)（退役线性化边界） | 26.7567° | 26.75667°（26.9−26.7567=0.1433） | ✓ |
| W_a/vs | 0.6598 s | 0.659800 | ✓ |
| T_STR(0°) / T_SLS(A→1,0°) | 未列 | 1.30273 s（两者相等） | ✓ 见 §5 |
| T_env,max（SPT,45°,库口径） | 10.5830 s | 10.583022 s | ✓ |
| 平面 oracle 偏差 @12° / @26.9° | +0.4185% / +2.1% | +0.41850% / +2.1025% | ✓ |
| 对称构造 vs 精确链 最差 | +1.87%（角点）+0.31%（12°） | +1.8715%（26.9°,ρ=0.3）/ +0.3103%（12°,ρ=0.5）/ **−0.5607%**（26.9°,ρ=0.5） | ✓ 且证实"符号依赖需求" |
| g_T：STR/SLS/SPT | 1 / 1/A / tan-exact | 1.000000 / 4.933803 / 8.224835 | ✓ |
| g_T·ρa | =D/2（STR/SLS） | 2.466902（STR,SLS）/ 2.467451（SPT，+0.022%） | ✓ |
| g_T 随 ψ 漂移 | SPT ≤0.07% | 0.0668% | ✓ |
| f_q 常数 STR/SLS/SPT | 0.8107/19.7352/54.8322 m⁻² | 0.810734/19.735213/54.832234 | ✓ |
| 倍数 24.3/67.6/2.8 | — | 24.34/67.63/2.78 | ✓ |
| AASR STR & SLS：0°/12°/26°/26.9°/45° | −21.35 / — / −23.32 / — / — | −21.35/−21.81/−23.32/−23.43/−25.40 dB；STR 与 SLS **逐位相同** | ✓ |
| AASR SPT 全包络 | −7.05 dB 不变 | −7.05 dB（0…45°恒定） | ✓ |
| tie-set 记录数 / 实例数 / 最优成员任务数 | 9,430 / 477,308 / 13,845 | 9,430 / 477,308 / 13,845（260 个 artifact 单元） | ✓ |

260 个 sweep 单元里 **每一个** front 的 f1_star 都只有单一取值（max−min=0），front_size ∈ {1,2,4,5,26,40}，pop=40——"tie-set"在事实层面成立。11 点采样（`lo+(hi−lo)j/10, j=0..10`）、−13 dB 阈值、10⁻¹² 交付守卫均在实现中逐字对上。

---

## 2. 发现 — P0

### P0-1 交付恒等式的 STR 分支方向写反（"at or coarser"）

**位置**：`main.tex:398`
**原文**："The delivery identity that constraint C5 enforces is a per-mode rule: for sliding spotlight and spotlight the delivered resolution equals the requirement at the selected start by construction, and **for stripmap the library floor is delivered at or coarser than the requirement**."

**为什么是问题**：可服务的 STR 任务是 ρ_req ≥ 2.4669 m 的那批（C5 自己在 `main.tex:208` 说 "a requirement finer than the floor has no admissible mode for that task"）。交付值 = (D/2)/cosψ_sel ∈ [2.4669, ρ_req]（机制见 P0-2），所以交付值 **≤ ρ_req，即 at or FINER than the requirement**，永不可能"coarser"。这句话把整个 floor 论证赖以成立的单侧不等式反向了：按字面读，STR 任务会系统性地 **达不到** 订单分辨率，而 C5 的正文明明说 finer-than-floor 根本无可行模式。两句直接冲突，且这是"identity"陈述的第三条腿，读者据此复核 Table 3 的 floor 排除界必然对不上。

**建议修法**：改为 "for stripmap the library floor is delivered at or finer than the requirement — equivalently, the requirement is at or coarser than the 2.4669 m floor"，或直接改成 "the delivered value is clipped to be at least as fine as the order"。

---

### P0-2 C5 的 STR 分支不是"交付常数"，而是一条依赖斜视的可行域裁剪；论文把它写成"无任务级参数 + 交付 floor + raise-guard"

**位置**：`main.tex:208`（C5）、`main.tex:211`（约束清单）、`main.tex:400`（retention 定义）
**原文 208**："The stripmap mode (STR) delivers the library floor of 2.4669 m: it has **no task-level parameter**, so a requirement finer than the floor has no admissible mode for that task, and a tighter requirement there is a step at the floor rather than a continuous degradation."
**原文 211**："C1 filters at generation time, C3/C4 are structurally slack inside the envelope, and **C5 is a raise-guarded identity rather than a scored constraint**."
**原文 400**："retention is the fraction of the tie-set feasible measure that remains feasible after **the stripmap clip** (numerator: the tie-set measure still feasible after the clip, denominator: the tie-set measure before it), evaluated at the as-placed point."

**为什么是问题**（三层，层层可证）：

1. **模型事实**：`sss_core/windows.py:548-554` 对 STR 做的正是 `ratio = rho_az(STR)/rho_req`；`ratio>1 → 返回空集`；否则 `psi_max = min(acos(ratio), 45°)` 并用 `clip_to_squint_span` 把该任务的可行起点区间裁到 |ψ| ≤ ψ_max。即 STR 的交付值是 **(D/2)/cosψ**，不是 D/2；它在每个起点上都随斜视变大，并且这条裁剪对 STR 是**可打分的域约束**，不是 raise-guard（raise-guard 只在 SLS/SPT 上，`sss_core/duration.py:201-277`，STR 传 `rho_req=None` 直接跳过：`evaluator.py:446`）。
2. **可观察量反证"交付 floor"**：R1C 在 as-placed 点（s=1.0）的订单是粗层 [2.5,3.0] m，**全部高于** 2.4669 m 的 floor，因此若 STR 真按 floor 常数交付，retention 必须是 100%。实测 `main.tex:400` 报的是 **51.14%**。这个数就是被 STR 裁剪掉的那部分：ψ_max = arccos(2.4669/ρ_req) ∈ [9.33°(ρ=2.5), 34.72°(ρ=3.0)]，R1C 的可行起点测度里有 48.86% 落在 9.33° 以外。该 retention 的**唯一**来源在测试里被钉死：`tests/test_verify_gate.py:226` 把 `resolution_clip` 换成恒等映射后算 raw measure，`test_verify_gate.py:284` 钉 `{"R1C": 0.5114, "R2F": 1.0, "R3H": 0.7100}`，注释明写 "the pin now measures the STR resolution clip ONLY"。也就是说：论文里唯一出现"the stripmap clip"的地方（§4.5）从未定义它，而它的定义恰好推翻了 §2.4 对 STR 的三句描述。
3. **推论影响两处主张**：(a) "a tighter requirement there is a step at the floor rather than a continuous degradation"——floor 之上还有一条**连续**通道（ψ_max 随 ρ_req→floor⁺ 连续收缩到 0），as-placed 点就已经生效（s=1.0 无任何收紧，仍丢 49% 起点测度）；(b) Table 3 的 floor-exclusion bound 只做零斜视 floor 测试、不含此裁剪，所以 bound 与观测之间 6.0/1.8 点的残差里，除"schedule falling short"之外还可能有**整任务被裁剪掉**的成分（若某任务全部已准入区间都落在 ψ_max 之外），论文目前只归因于后者。

**建议修法**（三句话即可闭合，不改数）：① C5 的 STR 分支显式写成 `ρ_del = (D/2)/cosψ_sel`，可行起点满足 `|ψ_sel| ≤ arccos((D/2)/ρ_req)`，`ρ_req < D/2` 时集空；② §4.5 把"the stripmap clip"定义出来（逐任务可行起点 union 裁到上述斜视带，测度按所有已选任务、所有窗口求和后取比值），并点明 as-placed 点 R1C 已损失 48.9%；③ `main.tex:211` 的 "C5 is a raise-guarded identity rather than a scored constraint" 改成 "C5 is a raise-guarded identity for the two task-law modes and a start-domain clip for STR"。

---

## 3. 发现 — P1

### P1-1 "a_res does not degrade with squint" 会被读成"分辨率不随斜视退化"，与 C5/STR 裁剪/§4.2 的 B_D 机制相反

**位置**：`main.tex:148`
**原文**："the $\cos^3$ factors cancel at beam-centre crossing, so $a_{\mathrm{res}}$ **does not degrade with squint**; the sliding-spotlight **design** azimuth resolution is the constant $A\,D_a/2$."

**为什么是问题**：这句话本身对**压缩因子**成立（我复算 a_res ≡ A，代码同：`aasr.py:268-270`），但紧随其后的名词短语会被读成分辨率不变。而模型里交付分辨率明确随 secψ 退化：C5 的 `A_task=2ρcosψ/D`（`main.tex:208`）正是 `ρ_ach=A·D/(2cosψ)` 的逆（`duration.py:122-142, 201-219`）；STR 的裁剪同样用 `ρ_a(STR)/cosψ`（`windows.py:552`）；§4.2 又用 "B_D = v_s cos ψ/ρ_a(m,0), which squint narrows" 解释 AASR 方向（`main.tex:451`）。26.9° 处 secψ=1.122、45° 处 1.414——这不是小项。同一段文字里"因子不退化"与"分辨率按 secψ 退化"两种读法并存，是理论节的核心歧义。

**建议修法**：拆成两句——"the compression factor is squint-invariant (a_res≡A); the **achieved** resolution still carries the 1/cosψ projection registered in §2.3, which is what C5's parameter laws compensate"，并把 "design azimuth resolution" 改成 "zero-squint design caliber"。

### P1-2 `ρ_a,ach` 被定性为"只用于报告、路由无消费者"，但 C5 的两条任务律恰是它的逆；恒等式全文只有断言没有推导

**位置**：`main.tex:188`
**原文**："the squint-dependent achieved resolution $\rho_{a,\mathrm{ach}}(m,\bar\psi)=\rho_a(m,0)/\cos\bar\psi$ is registered for reporting; the router consumes the zero-squint constant, and **the only bandwidth consumer of $\rho_{a,\mathrm{ach}}$ is the Doppler bandwidth** … **there is no consumer of the achieved resolution in mode routing**."

**为什么是问题**：字面限定在 "mode routing" 上不算错，但这段的功能是给 ρ_ach 定性，读者带走的结论是"secψ 只是报告口径"。事实是：`A_task D/(2cosψ_sel) = ρ_req` 与 `λ/(2β_task cosψ_sel) = ρ_req` 两条恒等式正是由 ρ_ach 的逆给出的（`duration.py:126-128, 201-219`），STR 裁剪也消费它（P0-2）。而 §2 全文没有一处把这条推导写出来——C5 只重复"so the delivered resolution equals the requirement by construction"。于是论文最强的那句（"an identity the solver cannot violate"）在公式层是断言的。

**建议修法**：在 §2.2 或 C5 补两行：`ρ_ach(m,ψ) = A·D/(2cosψ) = λ/(2β cosψ)`，令 `ρ_ach=ρ_req` 解出 `A_task`、`β_task`；然后明确"secψ 对 C5 的两条律与 STR 裁剪是承重的，只对 f_q 读数是报告口径"。

### P1-3 摘要把交付恒等式不加限定地升格到全模式（去重提示：claims 席可能同报，若去重以 claims 席为准）

**位置**：`main.tex:29`
**原文**："the mode parameters follow the required resolution, **the delivered resolution equals it at the selected start by construction — an identity the solver cannot violate** — and the stripmap antenna floor is the one place a finer requirement excludes solutions outright"

**为什么是问题**：正文对这条恒等式有两处限定：C5 只说 SLS/SPT 是恒等式，STR 是一句"delivers the library floor"（按 P0-1/P0-2 应读作"至多与订单一样粗"的裁剪）；§4.5 又加了 per-mode 的回退。摘要把三模式的差异压成一句无条件的"cannot violate"，而"排除"只留给 floor。按 P0-2 的机制，STR 分支既不是恒等、也不是纯粹排除，而是连续裁剪。

**建议修法**：摘要改 "for the two task-law modes the delivered resolution equals the requirement at the selected start by construction — an identity the solver cannot violate — while the stripmap branch delivers at or finer than the order by clipping its start domain"。

---

## 4. 发现 — P2

**P2-1** `main.tex:148` "$A\,D_a/2$"：`D_a` 全文只此一处（其余处用 `D`，Nomenclature 也只定义 `D`）。统一为 `D`。

**P2-2** `main.tex:161` "for SLS it is the symmetric construction of Eq.~(22)/(24) with the task-level sliding factor $A_{\mathrm{task}}=…$ **in the denominator**"：这是**平面 oracle** 的形态（同段后文自己给出 `T_SLS=(R0θa+W_a)/(A v_s)·sec²ψ` 并称其为 oracle）；生产闭式是 `(R0+r0)(tanθs0−tanθs1)+W_a` 除以 `v_s`（我复算：ψ=0 时 6.428930 s，A→1 时与 STR 逐位相等）。论文没有写出生产闭式，导致 Fig 2 caption 的 "one scene-sweep term below"（我复算 1.30273−0.64293=0.65980 ✓）与 floor 退化只能靠实现复核。建议把生产式写一行，并把"in the denominator"限定到 oracle。

**P2-3** `main.tex:170` "The zero-squint anchors close an identity: $\theta_a/A=\lambda/(2\rho_a)$ … residual $3.5\times10^{-18}$"：这是 `ρ_a=A D/2` 与 `D=λ/θa` 的代数重排（我复算残差 −3.47e−18 ✓），除 fixture 漂移外不可能失败。称"identity"易被读成物理校验。建议改称 "a fixture self-consistency check"。

**P2-4** `main.tex:250` "the **survivor set** of a unit is a tie-set on coverage rather than a trade-off front"：单目标非支配集（rank 1）确实是 tie-set（260/260 单元实测 f1 单值 ✓），但标准 NSGA-II 的 survivor set 在 rank 1 未填满种群时还含被支配个体（实测 front_size ∈{1,2,4,5,26,40} vs pop=40）。建议写"the returned front (the population's non-dominated set)"，与 §2.5 "a unit's front is a tie-set carrying one coverage value" 对齐。

**P2-5** `main.tex:186` "so the ratio is at most one"：对 STR/SLS 严格成立（g_T 与 ψ 无关，实测 spread 0.0%），但对 SPT 有 0.0668% 的 gain 漂移，实测比值上界是 1.00067 而非 1。建议写 "at most one to within the 0.07% SPT gain variation"。

**P2-6** `main.tex:194` "The frequency-axis rescaling by $(1-K_c/K_a)\approx(1-k_\theta R_0/v_g)$"：实现里该因子就是 `a_res = 1−k = A`（`aasr.py:270`）；`kθ` 全文没有数值定义，且 §2.1（`:140`）已承认 `A=1−R0kθ/vg` "is a restatement … not an independent literature identity"（取 `kθ=vg/(R0+r0)` 才成立，取几何上自然的 `vg/r0` 会给 A=−2.93）。建议 AASR 段直接写 `a_res=A`，把 kθ 形态留在 §2.1 的语义注里。

---

## 5. 已检查、零发现的方面（明说）

以下都逐式复算过，结论：**未发现问题**。

1. **§2.1 平台常数链**：D、R0（45° 斜距独立用椭球几何算出 775.426 km）、vs（用 μ/(Re+h) 独立算出 7578.057）、A、k、r0、r0/R0、三模式零斜视分辨率、`D/2` 全部逐值复现；`k = R0/(R0+r0)` 与 `A = r0/(R0+r0)` 的互逆关系正确（不是把 k 误当 A）；±26.9° 帽与 arccos(√k)=26.7567° 的 0.14° 间距 ✓；SPT 起点上限 "about 43°"（复算 42.98°）✓；ECEF 7500/7222 的 4.9% 标定方向 ✓。
2. **§2.1 动力学链**：K_a、K_c 的量纲（s⁻²）与 `a_res=1−K_c/K_a≡A` 的代数正确（K_c/K_a=R0/(R0+r0)=k），cos³ 在波束中心互消的表述与实现一致。
3. **§2.2 驻留闭式的量纲与边界**：`(R0θa+W_a)/(A v_s)·sec²ψ`、`R0(tan−tan)/v_s`、`2R tan(β/2)/v_s` 量纲均为秒；ψ=0 处 SLS 分支 `A→1` 极限与 STR **逐位相等**（1.30273 s），且在 12°/26.9° 处 A→1 极限仍与 STR 逐位相等（1.33178 / 1.46821 s）——"degenerates onto the stripmap transit" 在三处都是精确的；SPT 在 floor 处比 SLS 低 **恰好一个 W_a/v_s=0.65980 s** ✓；A→0（spotlight 端）与 ψ→包络端的行为单调、无奇点。
4. **任务律与域界**：`A_task=2ρcosψ/D`（无量纲）与 `β_task=λsecψ/(2ρ)`（rad）均量纲正确；域界 `ρ_req cosψ < D/2` 与 `A_task∈(0,1)` 严格等价；`β` 的成形点夹逼 `|ψ|+β/2≤45°` 与 42.98° 一致；SPT 最细可服务订单 λ/π≈9.9 mm ≪ 细层 0.24 m，因此"stripmap floor 是唯一 fine-side 排除"这一抽象级主张在本网格内成立（未被 SPT 端破坏）。
5. **恒等式**：`g_T·ρ_a=D/2` 对 STR/SLS 精确（2.466902），SPT 高 0.022%（"a fraction of a percent above" ✓）；`g_T(SLS)=1/A` 精确（4.933803）；`f_q=(g_T/ρ_a)/ρ_rg` 在 R=R0 处塌缩正确；`D/ρ_a²` 形式与三个常数逐位一致（54.82 vs 54.8322）。
6. **质量模型的 (R0/R)³ 链**：`T∝R/ρ_a` 在固定分辨率下成立、`1/R⁴ × R = R⁻³` 与 NESZ∝R³ 的教科书结果同向，量纲与"relative normalisation, no calibration"的定性自洽；f_q 的两个消费角色（能力陈述 + fulfillment 分子）与 §4.7 的标签逐字一致。
7. **AASR 定义与 m≠0 排除**：排除 m=0 的理由正确（含 m=0 时分子即分母，比值 ≥1 恒成立）；积分限 `±B_D/2+f_ac`、DC 相对坐标下 f_ac 消失的说明与实现（`aasr.py:281-293`）一致；"SPT 退化积分与 f_a 无关"正确（`aasr.py:245-253` 的比值确实与 f_a 无关）；数值 −21.35/−23.32/−7.05 dB 与 STR≡SLS 的"精确相同"逐位复现。
8. **C1–C5 自洽性**：C2 的 `(1+0.25)T_dwell + t_man + t_settle`、pad 只乘 dwell、冲突谓词用裸 T、1.84/4.07 s 混合触发与实现逐项一致；C4 的 `PRF·T·N_r·b_q·2/8` 量纲（bit）与 3630/10000/3 常数一致；C3/C4 "结构上永不 binding" 有代数支撑（C3 ≤ w_max/1.3 = 0.77 < 1；C4 = T/T_env ≤ 1，等式只在包络端，而 1% 内缩守卫把端点排除）；T_env,max=10.5830 s 与"最大权重 × 参考"的措辞、代码 `predicates.py:269` 一致（我一开始怀疑 10.5830 是 1.3× 后的值，复算后确认它就是库口径 T_env,max，误判撤回）。
9. **§3 测度投影与 tie-set**：`τ` 在可行 union 上按测度均匀 ⇒ 墙钟密度均匀、单窗份额 ∝ 窗宽、"相对墙钟无偏/相对逐窗均匀有偏"的三句都正确；"nonlinear by construction" ✓；tie-set 的三个计数（9,430 / 477,308 / 13,845）我按 260 个 artifact 独立重算，全部逐位命中；front 全单元单值 ✓。
10. **§2 的其余定量陈述**：0.4233–0.6686 °/s ↔ 1.7–2.7°@4 s ✓；对称构造 vs 精确链 +1.87%/+0.31%/符号随需求翻转（复算 −0.5607% @ρ=0.5/26.9°）✓；oracle 偏差 0.4185%/2.1%/5.3% ✓；T_STR 1.2 s 量级、SPT 3.6–10.8 s 与闭式量级相符。

**QUESTION（1 条，需要回执才能裁定，不计入发现）**：`main.tex:211` 的 "the task-law dwells were measured to exceed the library reference by up to **1.2008×**"——1.274× 这个理论上界我在 `predicates.py:120` 的注释里找到并复算吻合（13.4829/10.5830=1.2742），但 1.2008× 的实测值没有对应收据文件；如能给出该测量的 artifact 路径即可关闭，否则建议标注为 design-record 内部记录。

---

## 6. 对其他席的一句提示

code 席请注意：论文/代码里"constraint violation 最大值为 0.0"这个可观察量对 STR 是**恒为零**的——STR 的交付约束在 precompile 阶段就被 `resolution_clip` 折进可行域（越界起点根本没进入测量，`evaluator.py:356`），所以它不能当作"交付恒等式在 STR 上成立"的证据（见 P0-2）；claims 席若保留摘要的 "an identity the solver cannot violate"，需与 P0-1/P1-3 的 STR 分支口径一起改，否则摘要与 §4.5 会互指。

VERDICT: 2/3/6
