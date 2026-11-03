# RDR-066 — f2/f3 目标模型修正：NESZ 斜视双计（高程面角统一）

**来源**：S2 审稿 R2-MAJOR-1 + S3 对抗验证（2026-08-12）
**优先级**：P0（模型级错误 → 全 f2/f3 数字 + 全求解器重跑）
**状态**：代码已修 + 全量重跑中；数据/论文待重跑完成后更新

## 发现

论文 §3.1 定义 off-nadir 角 ξ = atan2(sqrt(l_x²+l_y²), l_z)（**含沿轨/斜视分量**），
又用 NESZ ∝ R³ ∝ 1/(cos³θ·cos³ψ)——内部不自洽。R² 分解 R ≈ R_elev/cosψ 仅在
θ 为**高程面角**时成立。

代码双路径（geom cache + live）都用 θ = off_nadir_to_incidence(全 ξ) 再乘 cos³ψ：
- `moea.py:179` theta_i = off_nadir_to_incidence(phi_dict[i])，phi_dict[i]=全 roll
- `moea.py:182` f3_num += cos³θ·cos³ψ —— **斜视双计**

恒等式：cos³θ_elev·cos³ψ ≡ cos³ξ（卫星侧角，验证 maxdiff 5.6e-16）。

## 决策（作者定 Option 2）

**f2/f3 全用高程面角**：
- f2 = sinξ_elev·cosψ = |los_y| = sqrt(cos²ψ − cos²ξ)（地面距投影用高程面入射）
- f3 = cos³ξ（R³ 因子；= cos³ξ_elev·cos³ψ 恒等）

f2 因 θ 从全入射改高程面 → 各 solver f2 值降 ~20-35%（S1 样本 0.61→0.47）。

## 修复（代码，已提交 待 commit）

- `moea.py` 4 处：f2 → sqrt(max(cos²ψ−cos²ξ,0))，f3 → cos³(φ)
- `baselines.py` posthoc：同上
- `so_f1.py` 4 处：同上
- `solver_factory.py`：同上
- `nesz.py`/`moea.py`/`baselines.py` docstring 同步

## 影响

- **r_null = −0.51 不变**（Option 2 保留原函数形式 cos³θ·cos³ψ，θ,ψ 独立均匀）
- 经验 per-task 相关（§6.4 −0.61..−0.78）随新 f3 重推
- 探针（3 场景）：S1 MOEA-3 vs G-BL f3 增益 code +111% → 正确口径 ~+52%；S4 饱和不变
- **全量重跑**（f2/f3 是优化目标）：MOEA-2（400）、MOEA-3（300）、消融 B/C/D、σ sweep、
  variant D、hotstart、budget control
- **事后重算**（便宜）：G-BL、G-SM、GA-P-BL 的 f2/f3
- 论文：Table1-3、figures、§6.2 G-SM δ、§6.4 相关、§6.6 全数字、摘要 +58%/+84%、
  highlights、ZH 镜像全随新数据更新；§3.1 Eq.2 + §3.2 目标公式重写（θ_elev 定义）

## 验证清单

- [x] 恒等式实测 maxdiff 5.6e-16
- [x] f2 公式 sqrt(cos²ψ−cos²ξ) = |los_y| maxdiff 3.9e-16
- [x] 烟测：S1-A_seed00 MOEA-3 新代码 f1=0.667 f2=0.4545 f3=0.6842 feasible
- [x] 重跑确认从 S1 全量（MOEA-2 400 / MOEA-3 300）
- [ ] 重跑完成后：Table/figure/§6.x/摘要/highlights/ZH 全数更新 + verify_paper_numbers 断言更新
- [ ] 双版编译
