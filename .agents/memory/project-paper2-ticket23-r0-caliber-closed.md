---
name: project-paper2-ticket23-r0-caliber-closed
description: paper2 票 23 闭环（2026-10-04）——逐任务 r0_m 口径全链收口（R14+R15+第八处 aasr），真窗阶梯
  120/120 重跑，判词全保持，写作期数字以 v2_results 为准
metadata:
  node_type: memory
  type: project
  originSessionId: sess_f55a85ce-34c8-47b6-ac61-b6b6cefe6984
---

票 23（2026-10-04，用户拍板修 R14/R15+根因排查指令）闭环：

- **改**：`boundary_rate`/`footprint_ok`/`aasr_direct` 加 `r0_m=None`（None=标定/合成口径）；evaluator C2、anchor 六处、nsga2 promotion、scenarios 真窗两门（footprint 移 pass 循环+Y1 归因规则）、verify 四镜像全透传；AST 静态守卫钉白名单。commits `dd3aa92`/`d4921e9`。
- **实测推翻台账假设**：「修=作废 270 单元」假——manifests 40/40 identical、R1C 全 STR 零变化、漂移仅经 C2 model 分支（~1e-3 s/对）+SPT kat0。详见 [[feedback-cost-claims-need-measurement]]。
- **重跑**：真窗阶梯 120/120 exit0（head 统一 d4921e9）；旧件 `v2-run-preT23/`；合成 M1NC 对 syn 基线 0 diff；M 五族 anchor Δ=0。
- **判词全保持**：R1C DEAD×CONVERGED（R_fam 4.0018 base/4.0032 max-over-seeds=票 17 注册值精确复现）；R2F/R3H/R4H ALIVE×UNCONVERGED ⇒ NO CLAIM（6.83-6.91，散文值差 ≤0.09 dB 判据不变）；promotion 全档 <6.0 未触发（R2F 顶档 3.57→5.22 dB）；R1C P1 EVALUABLE（dfq 16.5≥3）。
- **写作期取数**：一律 `experiments/v2_results/`（results_table/convergence_report/confound_control）+ `scripts/recompute_r_fam.py`；禁引 v2-run-preT23。
- **遗留**：R12/R13（测试守卫小票）、R7（技能 diff 人审）、真窗三族加预算出 P1 判决（用户拍板待办）、snapshot_rebuild 对 v1 冻结件结构性 N/A（v2 syn 件为正确域）。
