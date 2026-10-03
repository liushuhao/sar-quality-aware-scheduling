---
name: paper2-deferred-debts
description: paper2 票 03-12 终审登记的延后债（2026-09-27）——exit 11 测试缺口、AASR 窗内 enforcement、_build_dense 独立复核、变异档落盘、spec D4/D8 勘误、A6 上报待决策
metadata:
  node_type: memory
  type: project
  originSessionId: 8e4b1146-8eb8-43ab-9cd0-63bf039c5442
  modified: 2026-10-02T14:16:51.139Z
---

2026-09-27 票 03-12 终审（acceptance 13/13 + 对抗复审 ACCEPT-with-notes）登记的延后债，全部非阻断：

1. ~~**exit 11（空前沿）无测试覆盖**~~ —— **已于 2026-10-02 票 21 关闭**（commit `bf0dbd0`）。`tests/test_pilot_exit_codes.py` 4 测试：真实构造（全窗口压到 1.2 s，实测 0/20 可调度）+ 双向反夹具（可行 manifest 不得退 11；零服务场景钉 10 与 11 有别）+ 子进程调用使退出码成为可观测契约。**但施工中挖出更深缺陷：该 exit 11 分支在 CLI 上不可达（见 #14）**，故本条的「覆盖」是契约覆盖（xfail），非绿测覆盖。
2. **AASR 网格窗内 enforcement 缺位（预注册设计，非缺陷）**——生成期 AASR 门用窗缘单点直算（D08-2 逐任务 Wa），`AASRGrid.is_feasible` 生产调用方为零（仅测试+verify halving）。运行期不 enforcement 属 promotion_prereg 预注册（headroom 反夹具保护散布域）。关闭条件：若审稿人要求窗内最坏 AASR 判据，扩网格逐任务 Wa 查询。
3. **_build_dense 数值积分无独立重积分复核**——与 aasr_direct 中点采样 structural 一致（同 256 点同规则），残留不确定已登记（D06-8）。关闭条件：审稿人质疑时独立变步长重积分对拍。
4. **变异红证仅票面文字**——M7/M8/M10/M12 等变异的命令与输出记录在票面 markdown，无独立变异档落盘；acceptance 核验员已用实变探针独立补证守卫会红。关闭条件：如有正式 audit 需求再落变异日志。
5. **spec 正文两处勘误——已裁决修正（2026-09-29）**：D4 垫基（「25% 机动裕度」→ 垫基 = 驻留 dur_i，Kim 四处原文挂 SAT，票 09 D09-1）+ D8 回溯（「带回溯修复必须」→ 有界单步重定时，不可达证明 scoped 于 priority 降序插入序，票 11 D11-1）。spec.md :20/:33/:48/:52 四处同根一次清完，dated 【勘误 2026-09-29】marker 内联保留原句。零代码影响；formula-spec :120 自称「与 D4 语义一致」由假变真。
6. **A6 口径重议上报——已裁决关闭（2026-09-29）**：维持预注册口径（重议分支枚举为空：g_T 抵消经代码核实 quality.py:92-134 + evaluator.py:246-251，1e-5 是全公式真实读数；调阈值/改公式均违约）；per-mode f_Q 分解报告**判补并升格为写作期绑定交付物**（f_Q≈1/ρ_a² 模式查表，分解=第二目标全部可解释性载体）+ D05-5 双重加权披露段。工件 `papers/sliding-spotlight-scheduling/experiments/results/verify/a6_adjudication_20260929.md`（含 kill test：SPT 残差>1% 重开；观察项：H/W 前沿平凡化则第二腿叙事重构）。
7. **Mittermayer 2003 付费墙未取**（票 01 遗留，非阻塞）。

**2026-10-01 audit3 新增延后债（architecture/debt，非阻断）：**

8. **fork 守卫作用域只覆盖 nesz.py 单模块**——`test_fork_identity_nesz.py` 的反别名/自含/范围三条守卫只作用于 `sss_core/metrics/nesz.py`，而 `FORK_MANIFEST.md:10/:56` 是包级措辞。当前**无违例**（sss_core 全仓零运行时 sar_sim import）。关闭条件：后续票把共享符号复制进非 nesz 模块、或非 nesz 模块 import sar_sim 时。

9. **`sss_core/metrics/nesz.py` 零生产消费者**——唯一登记 fork 只被守卫测试 import；paper2 实际质量度量在 `quality.py`。风险：读者误以为 paper2 辐射度量继承 paper1 cos³ 核。关闭条件：文档层澄清或注释强化。

10. **AASR 保守谓词零接线**——注册的 grid-cell 上界 + 1 dB 裕度谓词生产路径零消费者；生成门用 `aasr_direct` 且**只在窗边采样**（SLS 窗内最差点在 t_ca，比窗边坏 2.92 dB）；生成期剔除在 10200 任务上剔除 0 个。数据未脏（窗内 11 点采样最差 −21.3 dB，余量 8 dB）。关闭条件：审稿人要求窗内最坏 AASR 判据时扩逐任务 Wa 查询（与已登记的 #2 AASR 窗内 enforcement 债同源）。

11. ~~**测试自指不可证伪**~~ —— **已于 2026-10-02 票 21 关闭**（commit `bf0dbd0`）。实测比原记录更严重：该断言**根本不可能失败**——`aasr.py:370` 算 `bound=block.max()+MARGIN`，断言 `bound−direct ≤ 3.0+MARGIN`，同一常量在两边，**margin 从 0 到 10 dB 全部通过**（实测）。修法：字面量 `4.0 dB`（实测最大 gap 2.0754 + 1.0 margin 上取整）+ 常量值独立钉 + 「offset 在所有 cell 均匀」结构检查 + margin 变异测试。变异红证：回退旧自指写法**仍绿**（证明其无判别力）；改 `aasr.py:133` 为 5.0 → 2 条红。

12. **C3/C4 结构上永不 binding**——归一化参考取库包络最大驻留（`evaluator.py:43-49` 自认）⇒ 大论文 Ch5 核心命题「绑定约束翻转 C2 vs C3/C4」在现工件内**不可呈现**。f1 优先级 `randint(1,10)` 无物理来源。关闭条件：大论文 Ch5 动工前须先裁决该命题的可呈现性。

13. **promotion 与 primary_comparison 的预算敏感（已升为票 17 阻塞项）**——D-A3/D-A4 本身进票 17 验收，此处仅记：任何「X 全预算死/稳健」类注册声明，必须先过收敛标定（与前沿同等待遇）。

**2026-10-02 票 21 施工新增（R9 两项关闭时挖出）：**

14. **exit 11 在 CLI 路径上不可达（新 P1，票 21 R9#1 施工时发现）**——`run_pilot.py` 先算 greedy anchor 再判空前沿，全部任务不可调度时 anchor 的 cv=1.0，触发 `nsga2.py:178` 的 `assert ev["cv"] <= CV_DUST_TOL`，进程 exit 1 + traceback，**到不了** `run_pilot.py:77-78` 的 EXIT_EMPTY_FRONT。即 D11 四退出码里专门为「场景物理不可调度」写的那支，CLI 永远返回不了。修法位置已写进 `tests/test_pilot_exit_codes.py` 的 docstring（在 `anchor_on_manifest` 前判 `any(p.schedulable ...)`）。**关闭条件**：修完把该测试的 strict xfail 去掉（已验证：打上修复补丁后 xfail 变 XPASS，strict 下会强制要求删标记）。⚠️ 未修时不得写成 `assert rc == 1`——那会把缺陷钉成期望行为。**台账 R12**。
15. **`precompile_tasks` 对零长窗口抛未捕获 ZeroDivisionError**（新 P2，同轮发现）——`windows.py:84` 的有限差分在 `h=0` 时除零；`evaluator.py:150` 只 `except ValueError`，接不住。触发条件：任务窗口 `[t_start_s, t_end_s]` 长度为 0。关闭条件：`feasible_subintervals` 入口加零长守卫或改捕获 `ZeroDivisionError`。**与 #14 同源**（都是「构造不可行场景」的路径没做边界防护），修 #14 时应一并扫。

**2026-10-02 票 21 已关闭项（补记，防重复发现）：**

16. ~~**F1/F2/F3/F5 四项式源缺陷**~~ —— **已 closed**（`d38a844` + 复算纠错 `68a9a76`），式源升 **v1.2**，勘误登记 §8.8 六条。机检：`verify_claim_traces.py --strict` rc=0。**副作用**：F3 裁决为「g_T 无外部文献源」，故本单**不再**有任何 g_T 外部锚；票 15 验收项 13 的 f_Q 复算已改走内部恒等链。

**Why:** 跨会话防重复发现与漏办：以上各项均已核为非阻断，但都有自己的关闭条件；新会话接手实验期或审稿响应时应先查此单。

**How to apply:** 实验期开跑前先处理 6（A6 上报决策）；审稿响应期按意见查 2/3/7；写测试补齐时查 4；spec 下轮修订时一并做 5。**#1 与 #11 已于票 21 closed**（#1 exit-11 构造测试在 `tests/test_pilot_exit_codes.py`，但它顺带挖出 #14 的真缺陷；#11 已修并变异红证）。**#14/#15 未修**，修 #14 时一并扫 #15。相关 [[paper2-implementation-batch-closed]] [[ticket21-recompute-corrections-20261002]]。
