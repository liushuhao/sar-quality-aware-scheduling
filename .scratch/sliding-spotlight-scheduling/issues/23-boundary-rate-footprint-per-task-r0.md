# Ticket 23: per-task R0 caliber split — full same-root sweep（R14+R15+第八处）

**What to build:** Every quantity benchmarked against library geometry must
decouple cleanly from the measured per-task geometry (ticket 16). Same-root
sweep found the split in THREE production paths, not two: (a) `boundary_rate`
(maneuver.py:95) feeding the C2 pair in evaluator + anchor fits/repair;
(b) `footprint_ok` (windows.py:384) SPT bound in the real-window generator
gate; (c) `aasr_direct` (aasr.py:200) — no r0 parameter, so the SPT aliasing term
k_at0 ∝ wa/r0 and the promotion spread readout (nsga2.py:146) use library R0
while their squint inputs are per-task. (Gate-review Y3 narrowing: SLS/STR
branches are r0-invariant at given psi — K_c/K_a = k/cos²ψ cancels exactly,
b_d has no R0 — so the aasr impact is confined to SPT tasks; R1C's all-STR
R_fam 4.0032 cannot move.) All three functions gain an optional `r0_m`
(None = library calibration caliber, bit-identical for pre-ticket-16
families); production consumers thread `plan.r0_m`. `verify.py` mirrors
thread per-task r0 at FOUR points — promotion_replay (:330 squint_at,
:331-334 aasr_direct, plus adding the try/except ValueError → +inf catch
aligned verbatim with nsga2.py:152-155, whose absence makes the finite-
exclusion branch dead code today) and the scatter/f_q REPORT points (:383,
:415). `aasr.py:312` (`AASRGrid._build_dense`) stays library caliber by
registration: the STR/SLS grid tables are exactly r0-invariant (k_c/k_a
cancel), the SPT table is the registered platform-level 5 km worst edge
(D06-2), and its only consumers are the calibration gate and tests — no
per-task path reads the grid. A static guard test pins the allowlist of
remaining library-R0 reads (by file:function granularity) so the ninth
instance cannot land silently. The real-window ladder is rerun and the
impact is MEASURED per unit against the superseded artifacts (the
"invalidates all 270 units" premise in the ledger was an untested
assumption: the maneuver fallback constant absorbs boundary_rate wherever
it is armed — fallback threshold measured at d_psi < 1.4545°, gate-review
confirmed — so the true requirement drift is bounded by the model-branch
t_rate share ~±0.04 s; the rerun diff settles it empirically).

**Blocked by:** None — can start immediately (user adjudication 2026-10-03:
R14/R15 修 + 根因排查指令；预算拍板维持待办)。

**Status:** ready-for-agent

**Tier:** T1（单点逻辑 + 全链透传 + 守卫测试；非 schema/seam/新建文件；触碰生产
求解与 promotion 判定语义故保 T1 全仪式：TDD 红绿 + 变异红证 + implement 前
1 路定向 gate-review + 核心片 acceptance 核验）

- [ ] `boundary_rate(..., r0_m=None)` / `footprint_ok(..., r0_m=None)` /
      `aasr_direct(..., r0_m=None)`：None → 库 R0（标定/合成口径不变）；既有
      合成测试零改动仍绿。
- [ ] 透传全集：evaluator C2 调用点(:278-279)；anchor fits/repair 六处经
      `boundary_rate_of`（包装本身加形参）；scenarios.py 真窗 AASR 门（窗内
      11 点采样处）与 footprint 门（移入 pass 循环用该 pass `r0_task`）；
      nsga2.py `promotion_spread_db`(:146)；verify.py `promotion_replay`
      (:330 squint + :331-334 aasr + 补 `except ValueError → float("inf")`
      与 nsga2.py:152-155 逐字对齐)。
- [ ] verify.py :383/:415 REPORT 镜像透传 manifest 逐任务 r0_m；
      `aasr_headroom` 标定探针保持库口径不动。
- [ ] 真窗 footprint 跨 pass 归因规则（票内注册，模板冻结不可编辑）：
      footprint 移除 ⟺ 所有可评估（incidence 非空）pass 上 `footprint_ok`
      全失败；不可评估 pass 既不算通过也不算失败；按模板 first-match 顺序
      取第一个「全 pass 失败」的门。
- [ ] 预登记 diff 预期（gate-review Y2/Y3 实测）：footprint 移除类**必须为
      空**（R 族 r0_task∈[817,1024] km 全高于库 768 km，fine SPT l_az≤3 km
      低于物理最小足印界）；aasr 变化仅限 SPT 任务（kat0∝wa/r0，SLS/STR 在
      给定 psi 下 r0 严格不变）；R1C R_fam=4.0032 不动；非空/越类 = 实现
      bug 非「新物理」。
- [ ] 静态守卫测试：sss_core 生产模块禁新增 `geo.R0_m` 直读，允许清单按
      文件:函数 粒度显式钉死：duration.duration_scene_s 与
      kim_checker_scene_sls 的 None 回退、duration.duration_point_s（点目标
      口径，g_T 比值内 R0 相消）、duration.duration_scene_planar_oracle
      （test oracle）、duration.duration_spt_exact_s（标定别名）、
      duration.kim_eq23_theta_s1（D03-1 内部恒等检查）、anchor.
      assert_fallback_active（标定几何）、quality.q_rad（D05-6 参考归一化
      (R_ref/R)³）、evaluator SchedulingProblem.evaluate f_q None 回退、
      aasr.aasr_direct 与 windows.footprint_ok 与 maneuver.boundary_rate 的
      None 回退点、aasr.AASRGrid._build_dense（STR/SLS 表 k_c/k_a 精确相消
      + SPT 平台级注册口径，无逐任务消费者）、verify.scatter_precheck 与
      verify._per_mode_means（REPORT 镜像的合成族 None 回退口径，同
      evaluator f_q 回退注册理由）、geometry 字段定义；守卫对
      白名单外新增读数即红。
- [ ] 变异红证：回滚任一透传点（或让三个函数忽略 r0_m）新测试须红；逐测试
      名记证。
- [ ] 双面回归绿：本域 + 共享库 rc=0，skip/xfailed 净增 0。
- [ ] 冻结边界：`experiments/results/` 六族冻结件零 diff。
- [ ] 最小单元（rule 11）：R1C seed100 manifest 重生成 + 单元重跑，与被取代
      工件逐项 delta 归因（AASR 门值 / footprint 移除 / C2 需求）。
- [ ] 全真窗阶梯重跑：4 族 × 10 seed × 3 预算全 exit 0；逐单元 diff 旧工件，
      变化单元归类（aasr 门 / footprint / C2 model 分支），零变化单元给计数。
- [ ] 合成对照零漂移：抽 1 合成单元重跑，数值字段与现工件全等。
- [ ] promotion 判定复算：R_fam 结构维与 spread 用新读数重算，ALIVE/DEAD/
      NO CLAIM 判词逐族复裁决；复算口径先落成**已提交脚本**
      （`scripts/recompute_r_fam.py`，扫描口径 = 任务 × 窗内 11 起点 × 路由
      模式 × 4 注册 PRF，逐项登记），翻转则 BLOCKED.md 约束同步改写。
- [ ] verify.py `DOMAIN_N0` 收集数 pin 随新增测试同步上调（含注释推导式）。
- [ ] 门禁复跑全 PASS：verify_prereg_v2 / verify_ticket22_adjudications(43) /
      verify_claim_traces(11) / check_red_lines(rc=0) / run_verify。
- [ ] 台账 R14/R15 关闭（带证据，含「±42%→需求漂移」实测换算）；PROGRESS.md
      新节；BLOCKED.md 约束随新数字更新；v2_results 表再生成。
