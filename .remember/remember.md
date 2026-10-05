# Handoff

## State

- **票 24（T0）已实施并验收**（commits `8f13f89` + `3edcd5e` + `bd1aac9`）：真窗入射角改**目标侧向量夹角**（WGS-84 椭球法线 · acos · [0,180]），旧 asin 正弦定理路径删除；**R21 时区同 commit 修**（naive `.timestamp()` → 显式 UTC）。红测先写后实现，**变异回滚 asin ⇒ 5/5 变红**（判别力已证）。
  - **关键实测**：(45N,0E) 真值全程 [94.7°,168.6°]（永不可见），旧码 **1200/1200** 采样点全报带内假值——这就是 460/460 假阳性机理。
  - **双面回归**：本域 **207 passed / 5 skipped / 1 xfailed, exit 0**（skip 净增恰 +4）；共享库 **145 passed = 基线 N₀**，且 `git diff paper2-m1-baseline..HEAD -- src/sar_sim` 增删行 **0** ⇒ **Paper1 链路完好**。
- **共享库按「只增不改」处理**（用户两次拍板后的终态）：其 `_off_nadir_to_incidence` 是 `(off_nadir, altitude)` **标量签名**，被**三篇论文**的场景生成器调用（`single-sat-quality/experiments/generate_all_scenarios.py:28,344-345`、`single-sat-quality/scripts/generate_s5_scenarios.py:26,146-147`、`constellation-scheduling/experiments/ch4_generate_scenarios.py:49-50,321,430,484,497`），向量夹角定义无法保留该签名。**goal-card「共享库 `src/` 零修改」红线恢复原状、从未真正解除。**
- **fork 身份守卫改双验**：共享库七元组仍逐位一致（证明 Paper1 未动）+ fork 新定义对**独立构造**断言。`FORK_MANIFEST.md` **四处**（`:50`/`:53`/`:61` + `test_fork_identity_nesz.py:163`）同 commit 修订。
- **第二独立缺陷 R22 已确证**：生成器取 `epoch + {0,600}s` 当「两趟过境」，600 s = **37.5°** 真近点角（周期 5755 s），是任意相位点非过境点。**修复后当前采样点下 0/8 簇可服务**（实测四带均 0/20）⇒ 4 条真窗测试标 `R22_BLOCKED` 显式 skip。
- **场景设计已定案**（用户四项拍板 + 三轮 gate-review 纠错）：单域 **20°N/0°**、1000 km 边长 5×5 网格、**日程跨度 3 天**、密度阶梯 **20/50/100**、**每窗口一个 `t_ca`**（`squint_at(t,t_ca)` 假设单次最近接近点在多圈下已不成立）。实测节拍 **2.0 趟/24h**（24h/72h × merge{300s,600s} 四组合全给 2.00）；N=100 需 5 趟、3 天 6 趟、**余量仅 1 趟（薄）**，分支预案：实测趟数 <5 则 N=100 出局退 20/50。
- 工作树净（`git status --porcelain` count=0）。

## Next

1. **开票 25**（T0，Blocked by 24——现已解除）：过境枚举 + 每窗 `t_ca` schema + 密集域 + 密度阶梯 + R18 三腿交集。票面已含四轮 gate-review 的全部修正与实测数字，可直接开工。
2. **票 24 剩余三项**（不阻塞 25，可并行）：台账 R17 回写收尾 / 共享库零字节断言已跑待留档 / Paper1 生成器最小单元实跑新旧对比。
3. **重议"三族加预算"**——已被 P0 降级作废，待真窗数据重做后再议。

## Context

- **红线**：修复后禁引任何 `v2_results` 真窗数字；BLOCKED.md 备注 2「真窗三族禁 alive/dead 声明」在重跑前保持；备注 1 预算耗尽约束因阶梯缩档而不触发。
- **R17 仍 open 的部分**：①共享库 `visibility.py:48` 同型潜伏（按只增不改原则**故意不修**，非遗漏）；②「460 任务仰角等价」判据经实测**证伪无判别力**（elevation 路径未被修复触及），已改口径为「入射角<90° 任务集合非空」，待票 25 后实测。
- **残留台账**：R7/R12/R13/R16/R17/R22/R23 open（均 <7 天，rc=0）。R12→并入票 25；R13→T2 单点可随时插；R23=举一反三新发现的两处**弱**判别力自指（非 R13 的完整算式自指）。
- **本会话教训**：6 次同形态翻车（单位/机理倒推/漏算/近似式当恒等式/二次口径/假缺陷），已双写沉淀 `feedback-compute-before-concluding` + `feedback-equivalence-claim-needs-measurement`（Claude/ZCode 项目记忆 + 两侧 core-memories）。
- 收工六步已走完；now.md 事件流已更新并 8s 复验（8904 bytes 稳定，未被 NDC 截断）。