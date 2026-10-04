# Handoff

## State
- **P0（2026-10-04，用户审图发现）：真窗四族 460/460 目标物理不可见**——`realwindows.py` 天底角地平线外折返 + `_off_nadir_to_incidence` asin 丢钝角支 + 无地平线守卫，背面目标折返出假带内入射角；共享库 `src/sar_sim/generator/visibility.py:48` 同型潜伏（Paper1 未触发）。全链（manifest→三腿窗→求解→v2_results→收敛判决→票 23）物理语义为零；合成族 M 不受影响。证据链/修复方向全录：项目记忆 `paper2-p0-realwindow-horizon-fold.md` + 台账 **R17** + PROGRESS.md「2026-10-04 P0」节（commit `df15c96`）。
- 修复方向已与用户对齐（**未实施**）：入射换算改向量夹角定义（acos 目标天顶·目标→卫星，WGS-84 椭球法线，返回 [0,180]；可见 ⟺ <90°）+ 变异红证 + 460 任务仰角等价检查。实测修复后两圈 ±120s 弧下可能 **0 簇可见** ⇒ 真窗场景设计（圈数/历元/簇心摆位）需随 spec 修正案重议。
- **同类物理违反全仓审计已完成（2026-10-04，用户令）**：故障模式分类学 F1-F7 × 三路 fresh subagent × 主线程复核。新确认 3 项（fork 三腿级联缺入射交集 R18；Ch5 缺地球自转 + 同型折返潜伏 R19）+ 共享库潜伏群（nesz.py:109 折返、**C1 窗间隙假 PASS 活边**、so_f1 回退 +10.9%；Paper1 已投数值安全 R20）+ 时区机器依赖（R21，可复现性类）。Ch5 gen 仰角守卫声明复核成立。全录 PROGRESS.md「同类物理违反全仓审计」节 + 记忆 `same-class-physics-violations-sweep-20261004.md`。

## Next
1. **用户拍板 P0 处置**：实施向量夹角修复（票 16/23 重开）+ 共享库 visibility.py 是否同步修 + 真窗场景重设计方向。修复前**禁引任何 v2_results 真窗数字**。**新增**：R18（三腿缺交）+R21（时区）建议并入 R17 修复票同批改；R19（Ch5）/R20（共享库 C1 活边优先）各自开票。
2. 重议"三族加预算"拍板项——已被 P0 降级作废（数据物理无效），收敛三层报告分析（两层报告/D+B/加预算）待真窗数据重做后再议。
3. 写作期素材已备：`.scratch/.../limitations-material.md`（L1 逐模式产品目录+撤回跨模式经济比较）、`pipeline-audit.html`（人话审查版）、`geo-map.html`（注意：图上轨迹已修复为内核 timestamp 约定，任务窗口=圈本地时间约定见图注）。

## Context
- "50% 幸存率"= 8 簇中 4 簇落在折返假入射角环带的整数巧合；档位数粒度诊断已查（`_fq_noise_probe.py`：≥3 门槛对粒度稳健）；两套诊断脚本在 `.scratch/sliding-spotlight-scheduling/_geo*.py`、`_fq_noise_probe.py` 可复跑。
- 收尾已过 closeout-sweep（FAIL 0/NOTE 15=既有基线）；工作树净（.scratch/.agents/.remember 均 gitignore）；P0 已双写沉淀（Claude/ZCode 项目记忆+索引、两侧 core-memories、R17 台账）。
