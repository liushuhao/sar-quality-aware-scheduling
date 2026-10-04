---
name: same-class-physics-violations-sweep-20261004
description: 2026-10-04 同类物理违反全仓审计（P0 故障模式分类学 F1-F7 × 三路 subagent × 主线程复核）——新确认 3 项 + 共享库潜伏群 + 时区依赖；Paper1 已投数值安全；Ch5 gen 守卫复核成立
metadata:
  type: project
---

2026-10-04 用户令"分析故障模式，全仓扫同类物理违反"。以 R17 P0 为原型抽象缺陷分类学：**F1 逆三角丢支 / F2 非单调折返 / F3 静默 clip 吞不可行值 / F4 缺物理守卫 / F5 错根·象限 / F6 域外静默 / F7 物理不变量破坏**。三路 fresh subagent（共享库 / fork / Ch5）+ 主线程代码读数与数值探针复核全部新确认项。

**新确认违反（台账 R18/R19）**：
1. fork `scenarios.py:469` 三腿级联缺入射交集——window=intersect(env_iv,end_iv)，inc_iv 只选锚点；发射窗不受 30–60° 入射带约束，windows.py 注册设计与实现不符（R18，修 P0 后转正）。
2. Ch5 `ch4_run_pilot.py:192` compute_sat_position 缺 −ω_e·t（:299 注释有公式未实现），半轨漂移 ~11.9°@500km，pilot 全部窗口在非自转帧内自洽（R19）。
3. Ch5 `ch4_run_pilot.py:244` 正弦定理+asin 折返（P0 同型）——当前参数 0 触发但 containment 涌现非设计：γ=90° 裕度仅 0.95°，对抗扫描 8610 背面带内样本（R19）。

**共享库潜伏群（R20，Paper1 已投数值安全——visibility.py:183 仰角守卫先行保护主链）**：`nesz.py:109` 折返+clip 吞 η>64.4°→90°；**活边 = `verification/constraints.py:182` C1 对窗间隙时刻假 PASS**（elev=−40° 折 49.98° 判过；Paper1 最终解窗口包含故不受影响；so_f1.py:598 事后校验残留风险）；so_f1.py:420/568 无 cache 回退 f2 +10.9%（标准 runner 不触发）；nesz.py:47 phi_min/max 域混用偏 9.42°（零活消费者）。

**可复现性类（R21，非物理）**：fork realwindows.py:294 + 共享库 visibility.py:124 naive datetime `.timestamp()` → 机器本地时区 → 地球相位 120.33°（UTC+8）机器依赖；跨时区机器 byte-identical 失效。

**复核成立/良性**：Ch5 gen:434 `elevs>=min_elev(5.0)` 先行守卫独立复核为真（106 窗 min elev 28.1° 全带内）；fork windows 不变量/机动闭合解（接缝欠预测封顶 4.8ms）/duration 根顺序依赖（当前域恒物理根）/椭球混用（亚度级）良性；**P0 更强证据**：冻结 epoch 全圈扫描 8 簇生成盒内真带内可见样本=0，served 任务 100% 折叠伪影。

**Why:** P0 不是孤立 bug 而是缺陷类实例；同型几何代码在仓内三处拷贝（fork/共享库/Ch5 实验），逐处守卫可达性各异——"函数会折"不等于"链路会错"，裁决必须追到守卫的数值上界。

**How to apply:** 修复排期推荐：R18+R21 并入 R17 修复票同批（fork 同文件/同 write-back 面）；R19 Ch5 开票慢修（未投稿）；R20 优先修 C1 假 PASS（verify 前置窗口包含检查），其余随 R17 共享库裁决。修复前禁引 v2_results 真窗数字不变。

相关：[[paper2-p0-realwindow-horizon-fold]]

**二次复核轮（同日，零修正）+ Paper1 影响核对收口**：三项新违反全部确认——R18/R19 代码读数复验+封数探针（缺自转 11.86°/半轨@500km）；C1 假 PASS 升级为主线程直调真实 verify_c1 复现（折返 φ=40°→0 违规，真值 134.5° 远带外）。**Paper1 报告数字不受影响**，六条证据链：①生成链仰角守卫先行（visibility.py:183）②质量链 θ=90°−elev 无反三角 ③全部 driver 先 precompute_geometry ④报告 frontier=pymoo res.X（G≤0）且 G=0⟺严格窗内→窗内换算精确 ≤2.3e-13° ⑤正文 small-paper-ijae.tex:495 明示 C1 属窗生成侧执行 ⑥GeomCache 污染列零消费。残留=res.X is None 零可行回退+GA-P best 事后校验（罚项压制下病态运行才触发；原始逐解 pkl 已清不可事后复核，审稿人质疑则重跑复验——风险方向=高估 f2/f3 利我方向，须诚实披露）。commit b537da1。
