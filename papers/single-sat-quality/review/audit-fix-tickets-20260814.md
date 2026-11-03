# 全面审查修复清单 — 2026-08-14

> 源：`full-audit-20260814-six-dim.md`（六维审查，10🔴+20🟡）。逐项修复+验证，T0/T1 用 TDD 红绿 + 守卫测试。
> 状态：pending / in_progress / fixed（代码改完） / verified（测试/重跑通过） / closed（提交+回归过）。

## P0 — 立即（不依赖消融重跑）

| # | 票 | 问题 | 改动 | 分层 | 状态 |
|---|----|------|------|------|------|
| P0-1 | B3 | no_squint 公式修复未提交 + 守卫测试未提交 | 验证工作树改动正确，提交 | T1 | closed (a811b70) |
| P0-2 | A1 | HV 归一化 f2/f3 方向翻转 + compute_hv 阶梯积分 | statistical_analysis.py 去 `1.0-`、阶梯积分 max；重算 statistical_results + fig1 | T1 | closed (81b97f3) |
| P0-3 | B1 | frontier 去重后 x_source 索引错位（4 处） | solutions_to_frontier 返回存活行索引；4 runner 同步 | T0 | closed (a2703f1) |
| P0-4 | B2 | resume 只验 pkl_sha1 不验 solver_version（6 处） | 跳过条件加 version 比对 | T1 | closed (3760c94) |

## P1 — 等消融重跑完成后

| # | 票 | 问题 | 改动 | 依赖 | 状态 |
|---|----|------|------|------|------|
| P1-1 | C1 | 消融表整表旧口径 + 与 Table1 矛盾 + verify 读旧 CSV | analyze_ablation 重生成 CSV + 重写消融表/§6.4 + verify 改读新 CSV | 三消融全完 | closed (58f07cc/05f9371/9a3966d) |
| P1-2 | C2 | variant-D random-init 旧口径（verify 2 FAIL） | 按新数据重算该段叙事 | 已有数据 | closed (3a2f8f0) |
| P1-3 | C3/C4 | tab:hv/G-SM HV/S4 n_frontier/f1*>1/fig4 文字已更新；剩余 G-SM δ p 值、§6.2 任务比 | tex 更新 | 部分等消融 | 部分 (43a9f39) |
| P1-4 | C6 | N50/CI 旧值 | tex §6.3 更新 | 无 | closed (1719e91) |
| P1-5 | Y4/Y17/Y18 | 中英镜像（ZH §2.3/§7.1/§5.1） | ZH tex 同步 | 无 | closed (e420a82) |

## P2 — 工程卫生

| # | 票 | 问题 | 改动 | 状态 |
|---|----|------|------|------|
| P2-1 | Y5 | 守卫测试空断言 test_theta_elev_identity | 断言 cos(θ_elev)·cos(ψ)≈cos(ξ) | closed (a811b70) |
| P2-2 | Y6 | 测试套件损坏（9/20 收集错 + 陈旧 import） | 修 sys.path + import 改名 | closed (1a13cd8, 128 passed) |
| P2-3 | Y7 | solver_factory ConstraintFree 死代码 | 清理 | closed (6ce6bde) |
| P2-4 | Y9 | S1/S2 版本戳失真 | 补注或洗戳 | closed (ee152bf, 内容身份判据替代 stamp==HEAD) |
| P2-5 | Y10-Y13 | fig1 图码/caption、随机搜索措辞、τ noise 措辞、f1*>1 声明 | tex 措辞 | closed (fig1 caption 已通用；Y13 旧值已更；Y11/Y12 本次修) |
| P2-6 | Y2/Y3 | ρ_i^req 声明即弃用、资源量级数字 | 删声明或说明 | closed (Y2 删 ρ_i^req；Y3 e_i/m_i 改 5×10⁴/5×10⁸) |

## 每票验收（通用）

- 代码改完 → 跑对应守卫/测试红→绿
- 数据重算 → verify_paper_numbers 断言过
- 论文改完 → 双版编译（EN pdflatex / ZH xelatex）两遍
- 提交 → git status + diff 核对，commit 信息写 why
