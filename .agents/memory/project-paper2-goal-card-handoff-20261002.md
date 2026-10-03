---
name: project-paper2-goal-card-handoff-20261002
description: paper2 goal 卡定稿（7 轮 11 路异源审查 45 处全修）+ 票链现状 21/22→15→16→17 五张未开工；含六族冻结边界与三条假零/破坏性路径清单
metadata:
  node_type: memory
  type: project
  originSessionId: 6eadc7ce-9c13-4ecb-96ec-a0d5e685e2bc
  modified: 2026-10-02T00:10:13.365Z
---

2026-10-02 产出 **`.scratch/sliding-spotlight-scheduling/goal-card.md`**（gitignored）——一段 ~6.8KB 中文交接卡，粘贴即开工上下文。设计取舍：**只装不可从仓库推导的东西**（已定裁决、红线、冻结边界、拍板清单、kill test 指针）；**不装**步骤序列 / 测试计数 / 票 Status（用户明示拒绝 leader 技能的碎拆）。七轮 11 路 fresh subagent（异源模型）审查 45 处发现全修，末轮判 CLEAN + fit to hand。

**票链现状（2026-10-02 更新：票 21 已 completed，余四张全 `ready-for-agent`，实测 `Blocked by`/`Tier`）**：
```
21 (T0, None) ─┐
               ├→ 15 (T0, 需 18 done+21) → 16 (T0) → 17 (T1, 需 16+22)
22 (T1, None) ─────────────────────────→ 17
```
22 独立喂 17 不喂 15；22 后于 17 执行会冻结出不可运行的主检验。

**卡围住的三条真会执行的破坏性路径**（全部实测复现）：
1. `run_matrix.py:154-157` 报错文本主动教「删 `_progress.json` 就行」→ 删后重跑经 `run_pilot.py:107-108` 裸 `write_text` **原地覆盖 51 个 tracked v1 工件**。真覆盖源 = `run_matrix.py:194` 传 `--out MATRIX_DIR`（`run_pilot.py` 自身 `--out` 默认 `None`，裸跑不写盘）
2. `run_probe_density.py` **无 resume 守卫**，默认落 `PROBE_DIR`，裸跑覆盖 20 pilot + 25 manifest
3. 六族冻结工件里的 `results/pilot/pilot_M1NC_seed100.json` = **M1NC 锚 0.8931**，`run_verify.py:28` `--pilot` required 消费——最易被当临时目录误覆盖

**kill test 关键裁决**：预注册是**三分支不是二分**——`unconverged`（实测占绝大多数）动作是「报 NOT-YET-CONVERGED + **不作任何物理声明** + 更高预算 = 新决策须用户拍板」，**不是「报负结果」**。且判据**仅钉给合成族**，真窗族只有继承义务（`convergence_calibration.pre_declared_criteria.inheritance`），阶梯在票 17 v2 冻结时才钉；升级额度**已用尽**（票 20 已跑 320/480）。

**Why:** 第一轮实验已把机器造对（127/134 测试、矩阵 50/50），但数据证伪了自己的 headline（相变悬崖 = 搜索预算伪影）。剩余四票全是方法论层（物理域 45° / 场景层重建 / 预注册重裁），不是收尾。卡的作用是让**无会话历史的 agent** 不重复发现「相变」也不踩上述路径。

**How to apply**: 下次开工先读 goal-card.md 再读 spec；票面 `Blocked by`/`Tier` 字段仍为权威源（卡只点「谁喂谁」）。冻结粒度是**数值字段**，授权写入两条：append-only amendment（`amendment_<date>_<slug>`）或 old-caliber 标记/git tag，**无第三条**。相关 [[paper2-spec-v05-cycle-20260930]] [[paper2-audit3-retarget-20261001]] [[feedback-verifier-shares-failure-surface]]。

**2026-10-02 票 21 完成**（6 commits `23132b5`→`68a9a76`）：冻结公式源升 v1.2（勘误登记 §8.8 六条），F1/F2/F3/F5 + R9 两项全闭，溯源门禁接入 verify 链并已跑通双面回归 302 passed。**下一张可起：票 22（T1，无前置）或票 15（T0，已解锁——其验收项 13 前提因 F3 裁决改变，改内部恒等链复算）**。详见 [[ticket21-recompute-corrections-20261002]] [[f1-song-sign-adjudication-20261002]]。
