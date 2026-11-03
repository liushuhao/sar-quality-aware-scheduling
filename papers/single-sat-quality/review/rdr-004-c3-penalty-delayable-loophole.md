# RDR-004 — 进化族 C3 罚函数"可延迟即豁免"，解码时刻从不执行/修复

**状态**: 代码 fixed（7 处），冒烟通过，全量重跑待执行 → 部分 fixed
**日期**: 2026-08-02
**来源**: RDR-003 核验时顺藤摸瓜；qwen/trae 两份报告均**未触及**（trae §5.5 只提 C1 预过滤 vs 在线罚函数，未审 C3 语义）
**优先级**: 🔴 P0（投稿阻断）
**代码修复**: so_f1.py、moea.py（单星+多星两分支）、solver_factory.py、三个 run_moea_3obj_no_*.py；py_compile 全通过；单测 33 passed（perf/ga_p_perf 的 9 个失败为 S5 数据缺失的预存问题，stash 后复现，与本改无关）

## 缺陷

`B2ProfitProblem._evaluate`（so_f1.py L187-223）、`SARSchedulingProblem._evaluate`（moea.py L234-283）、三个消融 runner（`run_moea_3obj_no_physics.py` L137、`run_moea_3obj_no_incidence.py` L128、`run_moea_3obj_no_squint.py` L187）的 C3（论文 C2，姿态转移）罚函数均为：

```python
earliest_start_b = max(task_b.t_earliest, t_end_a + tau_trans)
if earliest_start_b + task_b.duration <= task_b.t_latest:
    continue                      # ← 只要"B 理论上可延迟"就零罚分
```

罚函数只要求"存在某种延迟使 B 可行"，从不约束**解码出的实际时刻**；解码函数（`_build_schedule_from_b2` / `_build_schedule_from_moea`）原样透传 τ 解码时刻，无修复步骤。报告的 f1/f2/f3 全部按这些未修复时刻计算。

## 实跑核验

**GA-P-BL（存盘解直接审计，experiments/audit_gapbl_saved.py，218 场景全量）**：

| 类 | 场景 | 观测数 | 硬重叠对(t_b<t_a+dur) | C3 违规 | 缺额 p50/max |
|----|----|----|----|----|----|
| 全部 | 218 | 25,425 | **10,784 (42.8%)** | 10,990 (43.6%) | 35.3s / 37.3s |

210/218 场景含大违规；xWin=0（窗口成员罚函数有效），C1paper 仅 37（S1/S2）。即 GA-P-BL 存盘 schedule 近半相邻对时间上不可执行，缺额中位数≈观测时长（近完全重叠）。τ 基因在单目标 GA 中近乎中性漂移 → f2/f3 实为任意时刻的事后值。

**MOEA-3/2（同参数实跑重放，experiments/audit_moea_live.py）**：

| 运行 | 重叠对 | xWin | C3 worst |
|----|----|----|----|
| MOEA-3 S1/S2/S3/S4 A_seed00 | 1/11、5/86、14/187、29/247 | S3: 3 | 32–36s |
| MOEA-2 S3/S4 A_seed00 | 17/187、20/247 | S3: 3 | 34–36s |

MOEA 的 τ 受 f2/f3 目标塑形，重叠率（1–13%）远低于 GA-P-BL，但缺陷同源且确实存在。三个消融 runner grep 确认同一模式 → Table 6 全部变体同受影响。

**G-BL 对照**：构造时真修复（延迟+丢弃），40/40 场景 0 违规。

## 决策

🔴 必须修。改为**直接约束解码时刻**（而非解码后修复）：

```python
gap = t_b - (t_a + task_a.duration)
if gap < tau_trans:
    g += (tau_trans - gap) / max(task_b.duration, 1.0)
```

理由：修复式解码会造成"优化量 ≠ 报告量"（优化器按修复前集合拿分，报告按修复后丢观测算分），统计失真残留。直接罚函数使优化收敛到的就是可执行 schedule，与论文 L495-496 描述的语义（"if no feasible delay exists, the task is dropped" 的可行性定义）一致。窗口成员罚函数（xWin）已有效，保留。

## 修复位点（7 处，同一模式）

1. `src/sar_sim/solver/so_f1.py` L195-223（B2ProfitProblem，单分支）
2. `src/sar_sim/solver/moea.py` L243-262（多星分支，非论文路径但一致修）
3. `src/sar_sim/solver/moea.py` L263-283（单星分支）
4. `src/sar_sim/solver/solver_factory.py` L187-195（被 __init__ 工厂引用；论文 runner 不直接走，但同模式一致修）
5. `experiments/run_moea_3obj_no_physics.py` ~L130-139
6. `experiments/run_moea_3obj_no_incidence.py` ~L120-130
7. `experiments/run_moea_3obj_no_squint.py` ~L180-191

## 重跑清单（算力量大，需 Windows 终端长跑）

- GA-P-BL: `run_so_f1_bl.py`（218 场景）
- MOEA-2/3: `run_moea_2obj.py` / `run_moea_3obj.py`（各 200）
- 消融 A–D: 三个 no_* runner（各 200）
- Table 5 MOEA 行、σ sweep、random-init 对照、N₅₀ logistic、HV、Friedman/δ 全部重算
- 重算后核对全部正文数值（f1\*=1.18、+8.2%、N₅₀≈140、δ 系列、HV 0.173/0.169/0.140）

## 风险

- GA-P-BL f1\* **大概率明显下降**（43% 重叠对 → 优化器须放弃部分密集选择）→ "GA-P-BL 超越贪心锚点"结论可能弱化，结论段限定语需复核；
- MOEA 列小幅移动；饱和态/N₅₀ 为结构性结论，预期稳健但必须重算确认；
- 与 RDR-003 的修复相互独立，可并行，重跑结果合并后再统一改文本。

## 冒烟验证（代码修后）

- GA-P-BL 4 个 S1 场景（seed=0）：重叠对 **0/19**（修前全密度 43%）；
- MOEA-3 S1-A_seed01 重跑：xWin=0、C3big=0、overlap=0/10，f1=0.688/f2=0.599/f3=0.219（修前存盘 f1=0.596，数值变了但可行性恢复）；
- 新罚函数量纲复核：完全重叠缺口≈38s /30s ≈1.26 ×1e5 ≈1.26e5，远超最大 f1≈5000，单对违规即不可行，硬约束语义正确。
- **风险确认**：新罚函数比旧"延迟即豁免"严得多，S3/S4 密集区求解器可能被迫少选任务 → f1* 预期下降，"GA-P-BL 超越贪心锚点"结论力度待全量重跑后复核。S1 冒烟仍 20/20 全选（稀疏区无影响）。

## 验证清单

- [x] 7 处修改 + `python -m py_compile` + 单测 33 passed（perf 失败为预存 S5 数据问题）
- [x] 冒烟：GA-P-BL S1 4 场景重叠→0；MOEA-3 S1 重叠→0
- [ ] 全量重跑：run_so_f1_bl.py（GA-P-BL 218）、run_moea_2obj/3obj（各 200）、三消融（各 200）
- [ ] 全量后 ConstraintVerifier 审计全部存盘解：C3big=0、xWin=0（脚本 audit_gapbl_saved.py + audit_moea_live.py）
- [ ] 重算 S7/S8 baselines（RDR-003 联动）、Table 2/3/5/6、fig、统计
- [ ] 核对正文数值，重点 GA-P-BL f1*=1.18 是否仍成立；中英同步；双版编译
