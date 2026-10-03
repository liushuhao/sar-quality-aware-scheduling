---
name: paper2-sls-formula-pinned
description: paper2 SLS 公式族 2026-09-27 票 01 钉死——ρ_a,SLS=(1−k)·D/2 三源一致，蓝图 D/(2(1−k)) 因子挂反已证伪；formula-spec v1.0 为唯一公式来源
metadata:
  type: project
---

2026-09-27 票 01（SLS 公式族 blocking gate）闭环：三独立全文源（GF-3 2018 Eq.(2)+正文 "improved by the factor A"、Song 2025 Sensors 25(13):3888 Eq.(1)-(2)、Kim 2021 Aerospace 8(10):277 Eq.(15)-(16) 隐含式）一致钉死 **ρ_a,SLS = (1−k)·D/2 = A·D/2**（A=滑聚混合度因子，k≡1−A 桥接；A∈(0,1) 滑聚严格细于条带）。蓝图 §2.2(c) 的 D/(2(1−k)) 系因子挂反，已证伪；蓝图「滑聚细于条带」单调性叙事方向正确，无需重写、未升级用户裁决。

**Why:** 跨会话任何公式引用必须走 `papers/sliding-spotlight-scheduling/formulas/formula-spec.md` v1.0.1（FROZEN；同日两路 fresh 独立审查 0 critical——三 PDF 取式零错误、数值全复算命中——勘误轮修 GF-3 旁证 λ 照抄原文排版错等 3 major+4 minor，登记 §8.6），禁回蓝图取式——蓝图是已被证伪的二手源（同时证伪的还有：蓝图 SLS 时长式的 ρ_req–(1−k) 耦合结构、cosψ̄ 修正项方向/幂次（应为 sec²ψ̄）、附 A 的 k_a=(1−k) 挂靠（正确落位 = Song Eq.(10) 谱域频率轴重缩放 1−K_c/K_a））。

**How to apply:** ① SLS 时长 T_SLS=T_STR/(1−k) 配 sec²ψ̄ 斜视修正，Kim Table 3 回验偏差 0.2–0.5%（V_s≈惯性口径）；② spec v0.4 D4/D6 已同步；③ Kim 未公布 PRF/k 档/α_max/j_max/粗档带——fixture 全 null+fail-loud，票 06（AASR 需 PRF）须另 sourcing 并 manifest 回写，粗档带归 D2 映射票冻结；④ Mittermayer 2003 付费墙未取（GF-3+Song 双源已满足门槛）。相关工作 [[project-next-paper-squint-duration]]、[[paper2-fq-design-rationale]]。
