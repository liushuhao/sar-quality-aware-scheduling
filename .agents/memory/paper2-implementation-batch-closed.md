---
name: paper2-implementation-batch-closed
description: paper2 票 03-12 全部闭环（2026-09-27，commits 6cad746..8471f65）——求解器装配全链 124+1 绿；票 12 双链对账实抓票 10 C2 时序缺陷；fixture 漂移守卫补齐
metadata:
  node_type: memory
  type: project
  originSessionId: 8e4b1146-8eb8-43ab-9cd0-63bf039c5442
  modified: 2026-09-28T15:58:31.823Z
---

2026-09-27 第二篇论文（滑聚/聚束变时长调度）实现票 03-12 单会话全部闭环。commits：03=6cad746、04=b7c9cfe、05=f49d732、06=e881a77、07=ad48c30、08=fd8eed7、09=7ea9580、10=57a307e、11=6531e01、12=15f8b67、终审修复=8471f65。分叉包 `papers/sliding-spotlight-scheduling/sss_core/` 全链：成像模型→窗域预编译→质量族→AASR 网格→机动闭式→场景族→谓词→pymoo NSGA-II 装配→贪婪锚→verify 门禁。最终计数：分叉 124 passed + 1 skipped exit 0；共享库 145 == N₀ exit 0；M1 双查双零；verify 全门禁 8 PASS + 1 REPORT（A6 结构性上报）exit 0。两路 fresh 终审：acceptance 13/13 ACCEPT + 对抗复审 ACCEPT-with-notes（0 critical），确认轮 CONFIRM OK。2026-09-28 会话复跑分叉测试 124+1 exit 0 复核一致。

**Why:** 跨会话需知：(1) 全部 12 票闭环，无遗留用户裁决点；下一步 = 全量实验矩阵（5 变体×10 seed）+ 论文写作（均未开工）。(2) pilot 基线数字：M1NC seed100 锚种子后前沿 max f1* = 0.8931（= 锚 17/20），search-only 0.6641，f_q 恒 0.8107（全 STR），promotion=no_promotion（spread < 6 dB，机制验证）。(3) 关键预注册已冻结：ρ_req 档带粗 [2.5,3.0]/细 [0.3,0.6]/边界 [0.45,0.55]、k_ladder=0.797317、PRF 四键 {1150,2300,3044,3630}、promotion spread ≥ 6.0 dB、AASR 阈值 −13 dB（Villano 2016）。(4) 每票 implement 前定向 gate-review 共抓出 6 次 FAIL/PASS-with-notes 级预设计错误（垫对象三源裁定、移除回溯不可达证明、粗档带漏 SLS、SPT 全局 Wa 反保守等），全部修于动工前。

**How to apply:** 环境：python=`"/d/Program Files/Python/python"`、git=`/mingw64/bin/git`（裸命令被 rtk shim 污染）；pilot/verify 命令见 scripts/ docstring（PYTHONHASHSEED=0 强制）。闸门 hook 纪律：票目录任何更新都会使 .gates/current-ticket 过期，写源码前重写标记。相关工作 [[paper2-deferred-debts]]、[[paper2-ticket12-double-chain-catch]]、[[paper2-architecture-gate-closed]]。
