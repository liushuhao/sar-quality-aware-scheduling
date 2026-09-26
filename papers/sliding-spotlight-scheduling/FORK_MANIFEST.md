# FORK MANIFEST — papers/sliding-spotlight-scheduling/

> 冻结文档（ADR GRILL-002「Fork Manifest 与基线协议」节授权，票 02 产出，2026-09-27）。
> 本文件是从共享库 `src/sar_sim/` 复制进分叉包 `sss_core/` 的**唯一合法清单**。
> 状态：**FROZEN**（首次冻结 v1，随票 02 提交生效）。

## 回写条款（write-back clause，MUST）

1. 任何后续票要复制共享库的**任何**文件/函数/常量进 `sss_core/`，**必须先回写本 manifest**（新增 F-NN 条目 + 守卫覆盖映射行），再复制，再补恒等式守卫测试——顺序固定，缺一步即违规。
2. **manifest 外复制视为违规**：守卫测试按本清单反向断言（`test_fork_scope_matches_manifest_f01` 型），fork 包出现清单外的共享库符号即红。
3. 复制以「清单内符号」为准，**整文件顺手复制不合法**——每条 F-NN 必须列明复制了哪些符号、明确排除哪些符号及排除理由（最小复制面，防机会式复制把整仓复制从千刀累积达成，ADR GRILL-002 Alternatives (b)）。
4. 共享库侧后续修订（前篇审稿改动）到达时：先 cherry-pick 到分叉 + 守卫对账，再重置 M1 基线 tag——顺序固定（ADR M1 基线重置协议）。

## 基线登记

| 项 | 值 |
|---|---|
| M1 基线 tag | `paper2-m1-baseline`（annotated） |
| 指向 commit | `60ee1e8655dee96c1fc9aaa00c5d7982a7958069` |
| 共享库测试基线 N₀ | 145（`PYTHONPATH=src python -m pytest src/tests/ --collect-only`，2026-09-27） |
| 零字节断言 | `git diff paper2-m1-baseline..HEAD -- src/sar_sim` 为空 + `git status --porcelain src/sar_sim` 为空 |

## 分叉包命名记录

- **选定：`sss_core`**（sliding-spotlight-scheduling core）。与 `sar_sim` 无任何前缀共享，双 `sys.path` 插入下 import 解析零碰撞。
- **被否：沿用 `sar_sim`**——同进程双根 sys.path 插入下先 import 者胜，同名包使守卫对照「自身 vs 自身」恒绿（假绿），直接违反票 02 红线。
- **被否：`sar_sim_p2` / `sar_sim2`**——可读性差且保留碰撞根名前缀，grep/审阅时易与共享库混淆；无技术收益。

## 复制清单（frozen）

### F-01 — NESZ cos³ξ 辐射度量核

| 字段 | 值 |
|---|---|
| 源文件 | `src/sar_sim/metrics/nesz.py` @ `paper2-m1-baseline`（60ee1e8） |
| 分叉文件 | `papers/sliding-spotlight-scheduling/sss_core/metrics/nesz.py` |
| 复制符号 | 常量 `_K_NESZ_DEFAULT`, `_THETA_REF_DEG`, `_THETA_REF`, `_COS3_THETA_REF`；函数 `nesz_linear`, `nesz_db`, `quality_score` |
| 排除符号及理由 | `elevation_to_off_nadir`, `incidence_to_elevation`, `off_nadir_to_incidence`, `incidence_to_off_nadir`（几何换算器——本篇由自身轨道几何 builder 提供精确几何，spec D4 质量链只消费精确几何）；`quality_score_from_elevation`（换算器包装 API，随几何换算器一并排除——同上）；`aggregate_quality`, `quality_summary`（依赖共享类型 `sar_sim.types.ScheduledObservation`，复制会把共享类型拖过分叉边界）；`EARTH_RADIUS_MEAN_M`, `_DEFAULT_ALTITUDE_M`（几何换算器常量，随换算器一并排除）。**共享库 nesz.py 全部 10 函数 + 6 常量对照：复制 3 函数 + 4 常量，其余 7 函数 + 2 常量全在排除清单**（独立审查 2026-09-27 补齐，守卫 denylist 与本清单同步） |
| 数值一致性要求 | 逐位一致（同一操作序列，同解释器下浮点确定）；守卫用**精确相等**断言 |
| 语义注记 | `quality_score` 仅诊断用；本篇目标 f_Q 为独立逐模式量（spec D6），不得与本核混淆 |

## 守卫覆盖映射表（manifest 项 ↔ 守卫测试）

守卫测试文件：`papers/sliding-spotlight-scheduling/tests/test_fork_identity_nesz.py`

| Manifest 项 | 被守卫符号 | 守卫测试 | 断言形态 |
|---|---|---|---|
| F-01 | `nesz_linear` | `test_fork_nesz_linear_matches_shared` | 固定输入逐位一致（含 grazing → inf 分支 + 非默认 K_NESZ 路径） |
| F-01 | `nesz_db` | `test_fork_nesz_db_matches_shared` | 固定输入逐位一致 |
| F-01 | `quality_score` | `test_fork_quality_score_matches_shared` | 固定输入逐位一致 + q(θ_ref)=1 精确 |
| F-01（包边界） | 模块解析 | `test_guard_anti_alias_modules_distinct` | 两侧 `__file__` 路径不同（反别名，防同名包 import 竞争假绿） |
| F-01（包边界） | 模块注册 | `test_guard_anti_alias_sys_modules_keys_distinct` | `sys.modules` 两个全限定名各自注册且文件不同 |
| 回写条款 2 | 分叉自含性 | `test_fork_self_contained_no_sar_sim_import` | 源码 regex：fork 文件禁 `import sar_sim` |
| 复制清单条款 3 | 最小复制面 | `test_fork_scope_matches_manifest_f01` | fork 恰好定义 F-01 符号集，且不含共享库独有符号 |

覆盖率声明：F-01 全部复制符号均有恒等式守卫 + 包级反别名/自含/范围守卫，manifest 覆盖率 100%。新增 F-NN 时映射表必须同步加行，否则回写不完整。

## 运行方式（repo root）

```
# 守卫测试（新域）
PYTHONPATH=src "/d/Program Files/Python/python" -m pytest papers/sliding-spotlight-scheduling/tests/ -v

# 共享库回归面（N₀ == 145 断言防静默漏收集）
PYTHONPATH=src "/d/Program Files/Python/python" -m pytest src/tests/ -v
```
