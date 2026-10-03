---
name: paper2-audit2-full-review-20260930
description: paper2 换模型后全量再审（audit2）：四路 fresh subagent 挖 17 项、行为级 0；主线程 g_T 理论误判被 gate-review 实测推翻；R1 amendment 已提交 338984e
metadata:
  node_type: memory
  type: project
  originSessionId: d0f5ed3f-b55c-4299-bd18-892a682b9298
  modified: 2026-09-30T22:34:58.406Z
---

2026-09-30 晚用户换后台模型后要求「从想法到当前全部再审」。四路 fresh subagent
（前提/代码/数据/跨层）+ 主线程理论层 + 1 路 gate-review。工件
`.scratch/sliding-spotlight-scheduling/audit2-20260930/`（4 份 verdict + DISPOSITION.md）。

**核心判决：行为级缺陷 0，数据判决全部逐位复现**（50/50 manifest sha、115 记账、
distinct-fq 阶梯 2→4→17→48、promotion 全死 max 5.0009 dB、锚 0.8931297709923665）。
上轮「四路零发现 = 停审」判断**推翻 = 同源饱和假象**，新模型挖出 17 项。

**【教训：主线程理论审查也会错，且错在方向相反处】** 我判定「g_T 代数冗余 ⇒ D05-5
『BOTH』双重加权声明不成立」，写进 DISPOSITION 并准备改 prereg。gate-review 实测推翻：
`f_Q(SLS)/f_Q(SPT)` 在 `g_T OFF` 时 = 0.6 = ρ_SPT/ρ_SLS（**一次方**）、`g_T ON` 时 = 0.3599
（**二次方**）⇒ 1/ρ_a² 律**由 g_T 提供**，D05-5 声明正确，amendment 撤销。
错因：把 OFF 路径幂次当 ON 路径。**D05-3 恒等式 `g_T(m)=ρ_a,STR/ρ_a(m)` 是正确链**
（不是「1/A 是 1/ρ_SLS 的倒数」——那等式不成立，实测 4.9338 vs 2.0）。

**票 15 开工前已处置（DISPOSITION §2）**：
- D-1 红名单归因错误：剔 `test_quality_fq.py:112`（Kim 0.5m 文献窗）；
  **`:78` 恢复**——SPT 是唯一经 `duration_point_s(SPT)`→`duration_scene_s(SPT)`
  委派的路径（duration.py:104-105），只动 SPT scene 分支 ⇒ 实测 exit 1 红。
- D-2 ±12° 硬编码**7 处非 3 处**；漏 `verify.py:118 grid_halving` 采样域 ⇒ 网格扩
  ±45° 后「减半稳定性 ≤0.5%」实为 **24°/90°=26.7% 域验证报假 PASS**（唯一有时限后果项）。
- D-3 R1 红线机器可读侧：`analysis_prereg.json` 携带 `physics_collapse_verdict`
  「COLLAPSE IS PHYSICAL」骨架（真名：probe_density + convergence_calibration 各一处），
  与票 19/20 判决矛盾 = 前提洗钱。已 append-only amendment（commit 338984e）。
- F3/F4：票 18/19 checkbox 回写（7/7 + 5/5）；票 15「四消费方」实为 5 处（漏
  `scenarios.py:178`，在 `if anchor:` 分支内仅锚族触达）。

**append-only 字节级做法（两次失败后定案）**：`json.dumps` 重写会把 Prettier 风格
单行对象展开成多行（29 insertions/3 deletions = 破坏字节一致性）。正解 = **文本插入**
在末个 `}` 前拼 amendment + 断言冻结前缀**字节**不变。最终 10 insertions/0 deletions，
9 个既有键字节不变、CRLF 保持。脚本 `experiments/_amend_audit2.py`。

**台账 #78-85 回填**（disposition-ledger.md）。**测试 127 passed / 1 skipped / exit 0**。

**Why**: 换模型是审查信号源更新的正当理由（同源饱和下多轮 = 边际收益衰减）；本次
证明同源四路零发现会给出假阴性，且**主线程的理论判断同样需要独立二审**。

**How to apply**: 下次开工**票 15**（45° 物理域，T0）；开工前置 = 判 Tier + 门禁标记 +
1 路定向 gate-review（DISPOSITION 三处已改完）。32+1 commits 待 push（沙箱策略级硬拒，
用户终端跑）。相关 [[paper2-full-audit-20260930]] [[paper2-spec-v05-cycle-20260930]]
[[feedback-premise-laundering]]。
