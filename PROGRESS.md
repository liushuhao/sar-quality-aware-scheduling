# PROGRESS — paper2 四票施工（22 → 15 → 16 → 17）

任务书：`.scratch/sliding-spotlight-scheduling/_leader-draft.md`

## 目标
四票做完 → 第二篇小论文（滑聚/聚束变时长 SAR 调度）冻结件可签、实验可点火。

## 顺序
1. 票 22（T1，分析设计前置，零源码）— 主比较检验重裁 + promotion 收敛标定
2. 票 15（T0，45° 物理域）— duration.py 生产闭包切 Kim Eq.22 全式 + ρ_a(mode,ψ̄) + AASR ±45°
3. 票 16（T0，真窗族）— 真几何贯通三件套 + 窗求交三级联 + 过载比校准环
4. 票 17（T1，prereg v2 + 主实验）— `--dirs/--generator` 参数化先行，再 v2 冻结，再真窗矩阵

## 最大风险（三条）
- **票 15 的 ±12° 七处硬编码**：漏一处（尤以 `verify.py:159 grid_halving` 最隐蔽，只覆盖 26.7% 域报假 PASS）⇒ 新网格「已验证」是假的。
- **票 15 变异红证夹具**：必须 ψ̄≥26°/45°，12° 档 1% 容差吞掉平面式 0.44% 偏差 ⇒ 永不红 = 仪式空转。
- **票 17 v2 冻结**：须先派无会话历史 subagent 独立审冻结件（不豁免③）；`hv` 无实现须补或注销；冻结六族禁原地重跑（须显式 `--out` 新目录）。

## 任务 0 复核（2026-10-03 实测）
| 项 | 任务书声称 | 实测 | 判 |
|---|---|---|---|
| HEAD | `68a9a76` | `68a9a76` | ✅ |
| `git status --porcelain` | 净 | count=0 | ✅ |
| `git diff paper2-m1-baseline..HEAD -- src/sar_sim` | 空 | 空 | ✅ |
| 共享库 collect | 145 | 145 | ✅ |
| 本域 collect | 159 | 159 | ✅ |
| 解释器 | 3.14.4 | 3.14.4 | ✅ |
| `"hv"` 有 `.py` 实现 | 无 | grep 零命中 | ✅ |
| 0.8931 pin 行号 | `test_verify_gate.py:137` | `:137`（`:134` 是 docstring） | ✅ |
| `grid_halving` 行号 | `verify.py:159` | `:159` | ✅ |
| `shared_lib_tests` 行号 | `verify.py:135` | `:135` | ✅ |

结论：无误，准动代码。

## 施工日志

### [10:05] 票 22 开工（T1，分析设计前置，零源码改动）

证据面已读清（票面 + `duration.py` / `modes.py` / `geometry.py` / `aasr.py` / `predicates.py` / `quality.py` / `evaluator.py` / `anchor.py` / `nsga2.py` / `scenarios.py` / `verify.py` / `formula-spec.md` §3.1 §4.1 §4.2 §4.3）。

票 15 预勘（写给施工用，非裁决）：
- ±12° 硬编码实测 6 处 `sss_core/*.py`：`aasr.py:111` / `aasr.py:341`（票面说 `:336` `_domain_check` 的 def 行，断言体在 `:341`）/ `duration.py:277` / `predicates.py:98` / `scenarios.py:125` / `verify.py:168`。**票面列 7 处，其中 `aasr.py:247` 实为 `GridAxes` dataclass 字段定义（无字面量），须核**。
- `duration_scene_s` 生产闭包 7 调用点对上：anchor×3（`anchor.py:113,114,222`）/ evaluator×2（`:146,:209`）/ predicates×1（`:99`）/ scenarios×1（`:178`）。`quality.py` 走 `duration_point_s`（1 处，票面未列，物理闭包切换时需一并核）。

### [10:39] 票 22 completed — A3 + A4 双裁决

**已验证据**：
- 本域套件 `157 passed, 1 skipped, 1 xfailed in 307.74s`（= 基线 159 collect，skip/xfail 零净增）
- 共享库 `145 passed in 186.40s`
- `scripts/verify_claim_traces.py` → `RESULT: 11/11 claims provenance-verified / no open defects`，**rc=0**
- A3 对照实验 → **exit 0**，工件 `.scratch/sliding-spotlight-scheduling/ticket22-noseed/noseed_control.json`
- 冻结六族：`git status --porcelain papers/` 空、`git diff --stat -- papers/` 空（**零改动**）
- 零 `sss_core` 源码改动（`git diff --stat` 仅 `.scratch/` 与 `PROGRESS.md`）

**A3 裁决**（两视角 subagent + 主线程实测择优）：估计量从 `max_f1*` 换到 **`dq_all` = 全前沿最高 f_Q − 锚 f_Q**，分层（3 非退化族池化 n=30 主检验，逐族 Holm 次要），零保留不做 zero_method，禁覆盖轴显著性检验。主线程实测四个候选：`dq` 0/49 非零、`dom` 0/49、`mq` 0/49 全部结构性打平；`dq_all` 20/49 非零、sd=0.940。功效：逐族 p=0.0134/0.0015/0.0398 全显著，池化 p=2.4e-05，置换 p<1e-5。
**A3 对照实测**：50 单元 → 29 出前沿 / **21 空前沿**；29 中 **26 低于锚**、中位 −0.1630；`seed_worth` 中位 +0.1527。**已知混杂如实登记**：两臂初始化策略不同（非单变量消融），本地复刻方案被自等价守卫拦停（exit 5，29/50 空前沿）。

**A4 裁决**（两视角 subagent + 主线程实测）：两维判词（结构性 × 预算依赖）四格固定措辞。结构界实测 9 族全 <6.0 dB（M1NC/M3NC 0.037，M2WH 5.379，M2WF 5.464，M4WH 5.499，P6 5.439，P7 5.456，P8 5.501，P9 5.303）；平台维 71.03 dB ⇒ 平台活/族内死。**knife-edge 披露**：P8WH 距阈值仅 0.499 dB，且共用 `aasr_direct` 模型继承 D06-6 局限 ⇒ 标 model-level 禁标 physics-level。**量纲纠错**：票 17 验收项 13 写「f_Q 极差 vs 6.0 dB」是错的（f_Q 是 m⁻²），正解用 AASR dB。
**反验**：A4 阈值 1.0/2.0⇒UNCONVERGED、10.0/20.0⇒CONVERGED（真翻转）；A3 估计量换 `dq` ⇒ sd=0.0 / p=nan 功效塌陷。

**一处实测纠错（已改进票 body）**：先前口算的 M2WH「顶两档 median Δ=0.0078」是错比较基数；按注册顶两档（160/240 vs 320/480）实为 **1.892048 dB** ⇒ 判 UNCONVERGED（与「9 族全 DEAD×UNCONVERGED」一致）。

（每票完成后追加：`[HH:MM] TICKET 票NN → completed (<hash>) — <计数> / exit code`）