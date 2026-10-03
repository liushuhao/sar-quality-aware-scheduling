---
name: paper2-independent-audit-20260929
description: paper2 票 01-12 四路独立审查闭环（2026-09-29）——理论/公式全量重推 7/8 硬数逐位复现；抓 anchor 越窗真缺陷（票 13 已修）+ 4 处登记勘误；M3NC/M4WH 锚值变化；spec D5/D8 措辞包待用户
metadata:
  node_type: memory
  type: project
  originSessionId: 8e4b1146-8eb8-43ab-9cd0-63bf039c5442
  modified: 2026-09-28T22:49:31.269Z
---

2026-09-29 用户令独立审查票 01-12（重点理论/公式），四路 fresh subagent（A 时长机动公式重推 / B 质量AASR / C 谓词锚门禁 / D acceptance 兑现）+ 主线程逐条亲手复核。结论与处置：

**通过面**：A 角 8 项中 7 项硬数逐位复现（50,696 m / 8.3622 s / 0.4185% / 系数 32 / 27.4° 支配边界 / RMT 算术）；B 角 9 项硬数全复现（f_Q 锚 / RASR 探针 / K_a cos³ 精确 / B_D cos¹ 推导 / PRF 反相关 / SPT@3044 零点）；C 角 D11-1 不可达证明、D10-6 相邻对充分性（20 万随机 0 违例）、C2/C4 装配、窗域数学全过；D 角 12/12 兑现。

**修复（票 13，commits 9be621a + 8903618 + 5f804d7）**：① anchor 重定时候选越窗（回退态 need 常量，我手复现 B 置 7.373∉[0,4.697]，f1* 虚高 1.0）——成员性闸 + 回归测试；**M3NC 锚 f1* 0.2475→0.2345（旧值虚高）、M4WH 原在 encode 崩，均严格改善**，M1NC/M2WF/M2WH 逐位不变；② promotion 推导链「≥6×(1.0+0.2)」算术假（实 5×1.2 / 6×1.0），三处同步；③ maneuver cos¹「解析导数」撤回（真值 cos²，保守 +2.2%@12°，回退态零生产影响）；④ aasr 恒等式注释（真恒等式 = SLS(k_lib,0)≡STR，band folding 0.000 dB 实测）+ 1.0 dB 裕度依据 stale 重登记（k 轴 901×3 单调递减）+ 24x37x28→24x37x55；⑤ RASR 4 键复核闭合（−42.3..−24.5 dB，诊断位裁决不变）。确认轮 125+1 绿 + verify 8 PASS+1 REPORT+0 FAIL exit 0。

**Why:** 跨会话需知：(1) M3NC/M4WH 锚旧值作废（0.2475/崩），引用须用修复后值（0.2345/0.1199）；(2) **W/H 矩阵开跑前还有一道阻断：[[paper2-cv-dust-seed-assert]]**（种子 cv 尘撞严格断言）；(3) spec D5「解析导数」措辞 + D8 候选集成员性子句 = 用户属主级勘误包，待拍板；(4) 审查法教训：agent 反例首轮复现失败（模型态自保护）——反例必须构造到回退态才触发；subagent 发现必须主线程亲手复核后才修（本轮 4 项全经手验）。

**How to apply:** 实验矩阵开跑前置检查单 = ① 修 cv-dust 票 ② spec 措辞包拍板（不阻塞实验）③ 矩阵脚本消费锚时用新值。相关 [[paper2-implementation-batch-closed]]、[[paper2-deferred-debts]]。

**追加（2026-09-29 晚）：** ①spec D5/D8 措辞包已落（用户 goal 批准，同 D4/D8 dated marker 先例）；②cv-dust 已修——票 14（d23026b）：B-only 被 pymoo 内部严格 CV==0 可行过滤证伪（W/H 前沿空），终设计 A+B 混合（evaluator C2_TOL_S=1e-12 源头地板 + nsga2 带 1e-9）；M2WH 生产 pilot 首跑 exit 0（front 2、max f1*=0.3479=锚、search-only 0.3378、no_promotion）——**实验矩阵全部前置障碍清零**；127 passed + 1 skipped、verify 8PASS+1REPORT+0FAIL。