# RDR-005 — G-BL C2 可行性缺陷：观测结束时间误用窗口跨度 + 延迟时刻 LOS 不重算

- 日期：2026-08-02
- 来源：Trae 反馈"G-BL 在少量大场景 S3 有 0.2–0.7s C2 缺口"→ 对抗性全量审计
- 严重级：P0（求解器可行性 + f1* 归一化基线错误）
- 状态：fixed（代码），待全量重跑确认数值
- 文件：`src/sar_sim/solver/baselines.py`

## 评论原文 / 现象

Trae 报告 G-BL 基线在少量 S3 大场景有 0.2–0.7s 的 C2（姿态机动+不重叠）缺口，
定性为"基线 bug，GA-P-BL 通过 fallback 保证不差于 G-BL"。

## 对抗性验证（推翻"少量、微小"判断）

全量 400 场景独立审计（`experiments/_audit_gbl_c2.py`）：

- **369/400 场景 C2 不通过**，不是"少量 S3"。
- 违反量级分两类：
  1. **硬重叠 ~20s**：S3 等场景存在 `duration_min=30s` 但可见窗口跨度仅 10s
     的边界瞬态窗口（全库 113,349 窗口中 9,696 个 span < duration）。
  2. **0.05–0.65s 缺口**：S3 单场景 137 对违反。
- 按类分布（违反对数）：S4=7181, S3=5023, S8=2686, S7=1856, S2=930,
  S5=264, S6=170, S1=83。

## 根因（两个独立缺陷）

### 根因 A：观测结束时间被设成窗口结束而非"开始+持续时间"

`baseline_b1` 非延迟（gap 充足）与首观测路径写：
```python
ScheduledObservation(window=w, t_actual_start=w.t_start, t_actual_end=w.t_end)
```
观测实际只持续 `duration_min`（30s），但代码把结束时间拉到可见窗口末尾
（窗口跨度 span 从 10s 到 180s 不等）。

后果：
- span < duration 的窗口（10s 窗口/30s 观测）→ 假装观测只占 10s，
  与下一观测硬重叠约 20s。
- span > duration 的正常窗口（70–180s）→ 把观测错误地延伸到窗口末，
  过度保守，少排后续任务。G-BL 覆盖率被系统性低估。

`_enforce_c2_transitions`（G-PROFIT/G-SM 的 C2 后处理）同病：
不规整观测结束时间，且对 span < duration 的窗口不跳过。

### 根因 B：延迟决策时用错误时刻的 LOS 算 tau

两个函数在 gap 不足时把观测延迟到 `earliest_feasible = prev_end + tau`，
但 tau 是用延迟**前**的候选时刻（`w.t_start` / `curr.t_actual_start`）
的 LOS 间隔算的。卫星在延迟的几秒内已移动，延迟时刻的真实 tau 更大
（LOS 间隔随时间增大），于是解码 schedule 在独立验证下仍有
0.05–0.65s 缺口。

此外 `_c2_transition_los` 直接调 `_satellite_body_frame` 传播卫星位置，
而独立 verifier 走 `compute_los_separation` 的 10s 网格插值缓存，两者
在边界有 <0.001 rad ≈ <0.02s 的数值分歧。

## 修复

1. 所有观测结束时间统一为 `t_actual_start + duration_min`，绝不用 `w.t_end`。
2. span < duration 的窗口直接判为无法容纳观测、跳过（基线选择路径 +
   `_enforce_c2_transitions` 首观测规整路径）。
3. 延迟改用定点迭代：在候选延迟时刻重算 LOS tau，最多 8 轮直到 gap 真正
   覆盖 tau；窗口内放不下则拒绝。
4. `_c2_transition_los` 委托给 `compute_los_separation`（与 MOEA 评估器、
   独立 verifier 同一缓存函数），缓存缺失时回退直接传播。三处 tau 现在
   逐位一致。
5. 加 `_C2_GATE_EPS = 0.01s` 调度侧保护带，吸收 datetime/timestamp
   微秒级舍入，使每个被接受的 schedule 干净通过验证；不写入报告的 tau。
6. 顺带修 Trae 引入的 naive/aware datetime 不一致：`_b3_squint_minimize`、
   MOEA/GA-P 的 `_build_schedule_*` 按源窗口 tz 还原（pkl naive，测试夹具
   aware），消除 Windows 上 naive 1970 datetime `.timestamp()` 的 OSError。
7. `so_f1.ga_hotstart_solver` 修复后重验证使用修复 schedule 自身的
   t_actual/phi，而非复用修复前数组。

## 追加发现（首轮重跑后数据质量审计掘出，2026-08-02 晚）

独立审计（`_audit_baseline_quality.py`，对 400 场景重建 schedule 跑
ConstraintVerifier）在首轮基线重跑后又掘出两个真实缺陷：

### 根因 C：epoch↔datetime 时区往返 bug（污染 G-SM 的 f2/f3）

`_b3_squint_minimize` / moea / so_f1 三处把 epoch 还原 datetime 时，
naive 分支用了 `datetime.utcfromtimestamp(t)`。但前向 `naive.timestamp()`
在 UTC+8 机器上把 naive datetime 当**本地**时间，得到的 epoch 比真实 UTC
少 8 小时；`utcfromtimestamp` 把它当**真实 UTC** 反解 → 往返偏移 −8h，
把观测推到窗口前一天，落出可见窗口（OOW）并触发 C1（roll>50°）。审计首轮
结果：b3 C1fail=198/200、OOW=200/200。GeomCache 对越界时刻 clamp 到首行，
故 f2/f3 用了错误几何（非崩溃但是错值）。

修：naive 分支改用 `datetime.fromtimestamp(t)`（本地，与 naive `.timestamp()`
精确互逆），aware 分支保持 `fromtimestamp(t, timezone.utc)`。三文件同步。
修后 b3 C1/OOW 全 0。

### 根因 D：基线不强制执行 scenario 的 C3/C4 预算

`baseline_b1`/`b2`/`b3` 默认 `energy_budget=inf`/`memory_budget=inf`，
忽略 instance 携带的有限预算（1e7 能量 / 1e11 存储，每观测 5e4/5e8
→ 上限 200 观测）。MOEA 有罚函数遵守，基线却不遵守 → S3 20 场景、S4 27
场景 G-BL 排到 224–234 观测，超预算 12–17%，f1_gbl 虚高。

修：新增 `_resolve_budgets(instance, kwargs)`，传 instance 时用其预算和
每任务成本，显式 kwargs 可覆盖；三处 `_enforce_c3c4` 调用点统一改用。
修后 b1 nsel 在 S1–S4 正确封顶 200（max 234→200），C3/C4 违反 47→0。

## 最终验证（两次重跑后）

- `baselines_200.json`（S1–S4 各 50）+ `baselines_S7S8.json`（S7/S8 各 50）
  全量重跑完成，旧值备份在 `results/_backup_pre_rdr005_20260802/` 和
  `_backup_pre_rdr005b_tzbudget_20260802/`。
- 独立审计 400 场景（含 S5/S6 pkl）：**b1 与 b3 全部 C1=C2=C3=C4=0、
  OOW=0、worst C2=0.0000s**。
- b1 nsel：S1 19.6、S2 65.4、S3 161.5（封顶 200）、S4 159.7、S7 107、S8 131。
- 25 相关测试通过。

## 验证

- S3-A_seed00（最重场景）：C2 违反 137 对 → 0；G-BL schedule size 224 → 264。
- S1/S2/S5/S7 抽验：C2=0，worst=0。
- 相关测试：`test_b3_squint_min`、`test_spec_v4`、`test_baselines_posthoc`
  （含 MOEA/baseline tau 逐位一致测试）、`test_so_f1` 全通过（25 passed, 2 skipped）。
- 全量 400 场景审计在修后跑过一次，后台任务被中止前未取到最终汇总
  （逐场景 precompute_geometry 较慢）；S3 单场景 + 四类抽验已覆盖最重负载。

## 对论文 / 数据的影响（重要）

这是 RDR-003/004 之外的**第三个**求解器正确性缺陷：

- G-BL 是论文 f1* 的归一化分母（`f1* = f1_raw / f1_gbl`）。修复后 S3 的
  G-BL 选中数 224 → 264（+18%），f1_gbl 系统性上升。
- 已重跑的 `baselines_200.json` / `baselines_S7S8.json` 用的是**旧的、
  结束时间错误的** G-BL，f1_gbl 偏低 → 所有 f1* 数值偏高，GA-P-BL 的
  f1*=1.18 等结论需在基线重跑后重新核算。
- "GA-P-BL never worse than G-BL" 的 fallback 比较现在用的是正确的 G-BL，
  但基线本身变了，该保证的数值含义也变。

## 待办

1. **必须再次全量重跑基线**（baselines_200 + baselines_S7S8），再跑
   GA-P-BL / MOEA-2 / MOEA-3 / 三消融——顺序同 RDR-004。
2. 重算 Table 2/3/5/6 中所有 f1* 及 GA-P-BL 相对 G-BL 的增益结论。
3. G-SM（baseline_b3）也走 `_enforce_c2_transitions`，其 f2/f3/n_sel
   同样受结束时间规整影响，需重跑。
4. 审计脚本 `_audit_gbl_c2.py`、`_diag_gbl_s3.py` 保留为回归证据。

## 与外部报告的关系

qwen/trae 两版外部审查均未报此缺陷；Trae 仅观察到"0.2–0.7s 微缺口"表象，
未识别 20s 硬重叠和覆盖率低估这两个更严重后果。再次说明外部审查的可行性
覆盖不足，需自有独立审计兜底。
