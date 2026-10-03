---
name: paper2-spec-v05-cycle-20260930
description: paper2 spec v0.5 定稿过闸（方案A+45°物理+真窗族+密度轴闭环）；票 18→15→16→17 链 ready；四路 gate FAIL 13 项全修+确认轮 PASS；下次开工票 18
metadata:
  node_type: memory
  type: project
  originSessionId: 1179617b-2be9-4e1c-934c-2cc5db239b2e
  modified: 2026-09-30T22:35:18.890Z
---

2026-09-30 用户拍板三合一：方案 A（相变叙事）+ 物理域 45° 适配 + 真轨道窗 + 大论文密度轴闭环（前篇稀疏端/本篇密集端同一定律两端）。落 spec v0.5（D12 物理域/D13 真窗族/D14 prereg v2/D15 红线，`.scratch/sliding-spotlight-scheduling/spec.md`——**gitignore 不进库，本记忆+now.md 是唯一跨会话指针**）。

**Gate-review 四路**：13 发现（D14 v1带/v2物理混杂、AASR B_D 第三消费方、真几何三件套、formula-spec 冻结源缺口、must-red 名单、变异夹具档位、old-caliber、过境选择、校准环、驱动参数化、127 计数漂移）全落修，确认轮 13/13 PASS。台账 #63-69。

**【重裁 2026-09-30 晚，票 19/20】**：D14/D15 悬崖前提作废（收敛标定证伪，见 [[paper2-matrix-run-20260930]]）；headline 改三腿 = 平台物理 / 容量定律 / **收敛检验方法学**（预注册标定抓住 budget artifact）；交换率降可选；新增第五红线「禁相变塌缩类声明」；票 17 重写（收敛标定 = v2 强制项）；票 19/20 闭合。台账 #70-71。执行链不变：18→15→16→17。

**执行链（全 ready-for-agent）**：票 18（formula-spec v1.1 blocking gate：逐模式 ρ_a(mode,ψ̄) 封闭式钉死，式源 formula-spec.md:104 Eq.12/13 实例化 + B_D 重推导）→ 15（45° 物理域：驻留换 Eq.22 全式、三消费点、SLS 26° 物理滑动域=平台属性）→ 16（真窗族：fork propagate_orbit+visibility、真几何三件套、单过境规则、过载比校准环）→ 17（v2 带重标定前置 + prereg v2 + 矩阵 + 相变对照 + 红线机器检查）。

**Why**: 合成族证据链（矩阵 50/50 + 探针相变悬崖 40→60）已冻结为 v1 口径受控参照；用户要 operational 真窗 + 45° 敏捷星域。

**How to apply**: 下次会话直接开工**票 15**（票 18 已闭环 1bd49d8+cddcdf9；读 `.scratch/sliding-spotlight-scheduling/issues/15-physics-domain-45deg.md`，其三处验收项已由 audit2 修正——±12° 硬编码 7 处含 verify.py:118 采样域、红名单行级重列、五消费方）；实现期每票走 Tier 前置门禁（15/16 T0、17 T1）；探针/矩阵 v1 工件 old-caliber 标记在票 15。相关 [[paper2-matrix-run-20260930]]、[[paper2-audit2-full-review-20260930]]、[[concept-orbit-vs-pass-horizon]]。
