# Handoff

## State

- **分析层两决策已裁（2026-10-05，用户终拍，逐项呈问）**：①**不加预算**（>160/240 不追；
  promotion 判决预算稳健，追预算只买前沿丰富度；前沿类主张按 NOT-PLATEAUED 带限定语写，
  触发=审稿人要求收敛证据）；②**R 族效应量注册 δ=6.0**（promotion 阈值同源；R2F 层 92%
  功效可声称，R3H 层 29% 如实披露、报「未达显著」；ALIVE 判词照常描述性引用）。
  登记在票 22「追加裁决」节 + 功效曲线 `_power_curve_rq_effect_size.py`（MDE 复算对上）。
  **分析层无未决决策，写作期可开工**。
- **票 25（T0）已实施并验收（2026-10-05，commit `0692a44`）**：真窗场景全面重设计——
  过境按地轨枚举（AD-2）、`TaskWindow` 每窗口一个 t_ca 的 schema（AD-3）、密集域
  20°N/0° 5×5 网格 250 km 间距（AD-4）、阶梯重定 20/50/100 + `span_days=3`（AD-5/9）、
  入射腿进级联交集（AD-6/R18）、删三个死 API、run_pilot exit-11 可达（R12）。
  - **关键实测**：R1C 新域 **20/20 全链四腿 served**（158 窗、逐任务 3-12 窗、
    域心 2.00 趟/24h 复现预注册值）；gap-merge {150,300,600,1200}s 趟数不变（守卫测试钉死）。
  - **MUST-3 守卫**：50 冻结 pilot 前沿 f1/f_q 全部 ≤1e-9 复现（M 族单窗路径字节不变）；
    共享库 145 passed（= 基线 N₀）；`git diff paper2-m1-baseline..HEAD -- src/sar_sim` 零 diff。
  - **双面回归**：共享库 145P exit 0；paper2 域 **219P + 1S exit 0**（4 条 R22_BLOCKED
    测试复活转绿，xfail 退役，净增 7 测试）。四门禁 rc=0（red_lines / claim_traces /
    prereg_v2 28 checks / ticket22 43 checks）。
  - **gate-review acceptance**：fresh subagent 独立核验 **PASS（5/5 criteria）**，
    自跑抽验红证与 MUST-3 守卫；唯一部分兑现项（台账翻行）已随后关闭。
  - **三条变异红证判别力实测确认**：offset 规则 0 served / 删入射腿出带外窗 /
    标量 t_ca 零判别暴露。
- **票 24 收尾三项完成（commit `03bdad5`）**：R17 台账回写核对、共享库零字节断言
  实跑留档（写入 FORK_MANIFEST 基线表）、Paper1 生成器最小单元新旧对比一致
  （S1-A_seed00 归一化哈希 `d40ff961b01e2bbf`）。
- **R13/R23 关闭（commit `e1a9826`）**：SAT_MARGIN_KIM==1.25、尾隙 0.01、PRF 四值
  三处独立取值锚补齐（T2 插入，37 tests passed）。
- **台账收口**：R12/R13/R17/R17b/R18/R21/R22/R23 关闭带证据；**open=4**
  （R7 工具链 / R16 休眠触发器 / R19 Ch5 / R20 共享库），全部带关闭条件且 <2 天，
  `residual-ledger.py list` rc=0。
- **两处偏差已登记进模板 amendment（`amendment_20261005_ticket25`）**：
  ①票面「扫描跨度 14.75 圈」含 J2 节点漂移，仿真传播器为二体（无 J2）⇒ 在仿真中
  地轨重复 = 14.97 圈 ≈ 23.93 h；扫描跨度 3 天 > 任一周期，结论不受影响。
  ②MUST-5 登记为可证伪口径「每节点 ≥1 带内过境」（25/25 实测）——字面「最好入射
  ∈[30,60]」在域心因近天底过境不成立（21.7°），近天底过境只是不产生带内窗，无害。
- 工作树净（票 23/24/25 状态行与台账簿记提交后）。

## Next

1. **paper2 写作期开工**（分析层无未决决策；取数：真窗走 v3-run code head ≥`036e297`，
   M 族走 v2_results；R 族效应量 δ=6.0 按票 22 追加裁决口径引用）。
2. **开票 27**（T1）：R19 Ch5 两项物理违反 + t_start clamp + 种子确定性（Ch5 重构时，
   无急迫性）。
3. R7/R16 台账 open 项照旧（工具链对账窗口 / 休眠触发器）。

## Context

- **红线**：`v2_results` 真窗数字继续禁引（旧世界伪影；v2 M 族合成数字仍有效）。
  BLOCKED.md 备注 2「真窗三族禁 alive/dead 声明」保持到 v3 数据落地。**后续全部工作已落地（/goal 2026-10-05 晚）**：
  ①收敛标定 60/60 exit 0（两档 80/120+160/240，claude 执行/ZCode 判读）——R2F/R3H
  基预算塌缩均为 SEARCH-ARTIFACT（R3H ×99 反转）但未平台；promotion 预算稳健
  （90/90 ≤3.97dB）；功效 MDE80=4.87/13.87（R 族 f_q 值域 31–111 非归一化，跨族禁混）。
  判定表+功效回填 CALIBRATION_PREREG.md。
  ②票 26 落地（89041d1+6a16866）：C1 窗包含守卫 + so_f1 fail-loud + 9 红证测试 +
  N₀ 145→154 三处联动 + m1_double_check 收窄（reviewer 补刀，worker 漏项）。
  台账 R20 关闭（open=3）。Paper1 189/189 + S1-A 哈希同留档。
**真窗矩阵 v3 已落地（2026-10-05 晚，两次发射）**：首射 18/30 exit-1 暴露
  encode_seed_individual 多窗测度缝（anchor 起点恰在区间左缘，tau*total 丢 1 ulp 后
  游走翻入前一过境），修于 `036e297`（nextafter 跨缝 + 实崩案例红绿测试 + 全量
  220P+1S 回归）；二射 **30/30 exit 0**（5.5 min；claude CLI 执行+看护、ZCode
  诊断/修复/审查，分工按用户指令）。**v3 判决**：R1C 全 10 种子 anchor f1*=1.0、
  front 28-40（轻载域）；R2F/R3H anchor 0.938-0.9925；R_fam：R2F **9.75-12.13 ALIVE**
  / R3H **11.99 ALIVE** / R1C 4.00 DEAD（= WANT-1 单圈对照成立）；R3H 7/10 前沿塌缩
  ⇒ promotion 判决仍 NOT-YET-TESTED；30/30 no_promotion 禁读作结构死（欠收敛读数）。
  产物 `.scratch/.../v3-run/`（scenarios 30 + matrix 31 + progress + 简报）。
  BLOCKED.md 备注 2 已解除 v2 隔离（commit `1d4f637`）。
- **生成器设计要点**（写论文/审稿会用）：每趟 t_ca = 段内向量 squint 最小点（可能
  在带外近天底处——那是平面 squint 模型的锚，不是带内点）；一趟的两条带内翼合并为
  一个 pass（sub-band 中段 ≪ gap-merge 阈值）；AASR 腿逐窗执行（每窗独立过四腿，
  比旧"只测最宽窗"更严）；决策变量仍 2N，过境选择隐式在 tau 里（测度归一化 ⇒
  采样偏向宽窗，已登记）。
- **本会话教训**：stash 二分定位到 `_precompile_frozen` 把 t_ca 错冻成 0（D11-8 冻结
  的是 dwell 不是 psi 几何）——"冻结"语义要逐字段问；向量化共享轨道（kepler 循环
  一次/场景）把 R1C 从分钟级压到 2 s，是「冻结路径复用 + 几何向量化」的干净分层。
- **跨工具审补充（17:55，commit `b76be2d`）**：用户点名的 Claude Code CLI 对抗审
  判 FAIL 并抓出同模型 fresh 验收全漏的 3 缺陷（fp_fail 未初始化 / 三处注册文本写
  bisection 而实现为 33 点网格 / probe2+3 未迁 per-window），已全部补救并过确认轮
  （test_scenarios 25/25、probe2/3 exit 0、四门禁 rc=0）。票 25 验收终态 = 双轨通过。
  教训已双写 core-memories；**规则化建议待你批准**：rule 10/16 补一行「T0/one-way
  验收加异源模型对抗审（自包含简报 + claude -p 只读工具面）」。
- **收工六步**：归零复盘（本页 State/Next/Context + now.md 事件流）、记忆沉淀
  （无新增跨项目教训；票 25 偏差已进 amendment）、neat-freak 待跑 closeout-sweep。
