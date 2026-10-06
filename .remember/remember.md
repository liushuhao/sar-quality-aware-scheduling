# Handoff

## State

- **paper2 写作前二轮（换模升级）重审 + 收尾补修全部闭环**。写作期前置条件具备，工作树净。
- 两轮处置共 **7 commits**：`2f9d73f` formula-spec §8.13（v1.6）+ 6 处原地更正；`bfb5863` 票 32 六处代码侧；`7961126`+`8b393a5`+`ff591a4` 台账；`f050fa1` BLOCKED；`9f42532` handoff；`e228dfb`+`416c582` 票 33（R16 洗白句边界 + R27 4 锚）。票 32/33 确认轮均 PASS。
- **全绿**：五门禁 rc=0（0/193 + 14 CLEARED、11/11、33、28、43）；全量 run_verify **12P+1R+0F**；靶向 pytest 36 passed。写作义务清单 **46→51 项**。

## Next

1. **paper2 写作期开工**（前置全清）。取数：真窗走 `experiments/v3_results/`（L6）、M 族走 `experiments/results/`；v2 真窗数字永久禁引；写完必跑 `scripts/check_red_lines.py`（rc 须 0）。清单 `.scratch/sliding-spotlight-scheduling/writing-checklist-20261005.md`。
2. **台账 open=4**：R7 技能半 / R19 Ch5（票 27 blocked）/ R26 红线覆盖 1-of-9（待 .tex 落盘后补）/ R27 剩 17 处 C 类锚点漂移。
3. 无阻塞。

## Context

- **full run_verify 用 canonical pilot** `.scratch/.../v2-run/syn_p40g60/pilot_M1NC_seed100.json`；tracked `experiments/results/pilot/` 票 12 件在 HEAD 不可复现（`snapshot_rebuild` 必红 rc=20），已写进 `run_verify.py` docstring 警示。
- **门禁 hook 生效**：改 .py 源码前须建票 + 写 `**Tier:**` + `.gates/current-ticket` 标记（票目录一更新标记即判过期，须重写）。
- Windows 路径坑：`check_red_lines.py` 的 `--path` 已 resolve（曾因 `relative_to(REPO)` 大小写归一化抛 ValueError 而 rc=1 假绿）。MEMORY.md 已 GC 35275→16760B。
