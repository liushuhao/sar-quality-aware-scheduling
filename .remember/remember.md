# Handoff

## State

- **paper2 写作前二轮（换模升级）重审闭环**：4 路 fresh 无锚定审查 + 主线程逐条复算，16 项确认发现全处置。三条「照抄即写错」直接错误已封（geodetic_normal 0.0° 假陈述 / §4.2 优化器点目标口径与实现相反 / quality docstring 零斜视符号错写）。
- **3 commits**：`2f9d73f` formula-spec §8.13（v1.6）+ 6 处原地更正；`bfb5863` 票 32 六处代码侧（2 门禁判别力修复）；`8b393a5` 台账。票 32 确认轮 11/11 PASS。
- **全绿**：五门禁 rc=0（0/193 + 14 CLEARED 首次可审计、11/11、33、28、43）；全量 run_verify **12P+1R+0F**；双实现 90 单元零差异；靶向 pytest 36 passed。工作树净。
- 写作义务清单 **46→51 项**（新增 F-10~F-13 + E 段禁语行），随行 `.scratch/sliding-spotlight-scheduling/writing-checklist-20261005.md`。

## Next

1. **paper2 写作期开工**（前置全清）：取数真窗走 `experiments/v3_results/`（L6）、M 族走 `experiments/results/`；v2 真窗数字永久禁引；写完必跑 `scripts/check_red_lines.py`（rc 须 0）。
2. **R27（新）**：`spec-amendment-v06.md` 源码锚点 21/52 漂移（清单 `.scratch/rewcheck-20261006/anchor_audit_findings.md`），A/B 两类 4 处最廉价可先修。
3. 台账 open=5（R7 技能半 / R16 / R19 Ch5 票 27 blocked / R26 / R27），各带关闭条件。

## Context

- **full run_verify 用 canonical pilot**：`.scratch/.../v2-run/syn_p40g60/pilot_M1NC_seed100.json`；tracked `experiments/results/pilot/` 票 12 件在 HEAD 不可复现（`snapshot_rebuild` 必红 rc=20），已写进 `run_verify.py` docstring 警示。
- **Windows 路径坑**：`check_red_lines.py --path` 传仓内相对路径会因 `relative_to(REPO)` 大小写归一化抛 ValueError（rc 仍是 1 = 假绿形态），已修（roots 先 resolve）。
- MEMORY.md 已 GC：35275→16760B，13 主题文件入 `memory/archive/`。
