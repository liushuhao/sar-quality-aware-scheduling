# Handoff

## State
- **A-CROSS 已定案并落地**：SLS 扫描律 = (乙) 旋转中心（tanψ=Vt/r_rot）；(甲) 恒速率 = 其小角线性化。a_res≡A 常数、26.7567° 边界废除、驻留 sec²ψ̄ 本就正确、**零重跑**（R 族 3346 端点 + M 族解析穷举 + promotion 全零翻转；R1C/R2F/R3H/M2WF/M2WH 再生成与冻结件逐字段相同）。判决 `.scratch/sliding-spotlight-scheduling/a-cross-verdict-20261007.md`（三轨对抗审 0🔴 + 确认轮 CLOSED）；ADR `papers/sliding-spotlight-scheduling/docs/adr/0001-sls-rotation-center-semantics.md`。
- 已提交：c57b199（票 40 实现：aasr.py 双路径切 (乙)+守卫降 k≥1+formula-spec v1.7 §8.14+两台审计锚重登记，判词全存活 R1C DEAD/R2F 8.74 ALIVE/R3H 10.91 ALIVE）+ 3115f59（票 39 收尾：ADR 0001 + §8.15 + 清单 F-8/B4 改写 F-14 新增）。票 39/40 均 completed。HEAD=3115f59，树净 0，全量 374P/0F/1S，verify gate PASS=12/FAIL=0。
- 台账 open=5（R7/R19/R27 维持 + 新 R30 recompute_r_fam 旧律锚、R31 两处二手引证全文）；now.md 事件流已更新。
- **票 41/42 已闭环**（2026-10-08，commit `ff444e6`）：全面三层审计 + 文献组织核查发现 (乙) 定案的**登记面传播缺口**——代码主链已切 (乙)，但 9 处登记/写作文档仍教 (甲)。票 41 全回填（formula-spec §8.16 点名取代 §8.11-1/§8.13-3、spec.md D12 dated 勘误、spec-amendment §8.9、清单 v2 F-13/E-338 改写、prereg 追加块取代 A9/strata R_fam〔9.7524/11.9886→8.7407/10.91〕、RUN_LINEAGE L6/N2 R_fam、caliber 措辞、三处旧律注释、`verify_paper_numbers.py`+测试改 (乙)+变异红证）。票 42 文献入库：A-CROSS 一轮 4 篇 + GF-3/Kim/Song + Li 2018 + Li 2025 = 9 篇并入 `literature/{raw,fulltext,structured}` + `literature_corpus.csv`（333 行）；Ren 2025 PDF 补取成功；Li 2025 仅 metadata_only（venue 未证）。冻结件 `platform_kim2021.json` 字节未动；prereg 冻结前缀字节保真。

## Next
1. **票 38**：workflow v3 落地，吃 (乙) 结局——**不插重跑段、取数留 v3 不升 v4**；把 A-CROSS/ADR 0001/零重跑判据写进流程。
2. **写作期开工**：`writing-workflow.md` v3 + `writing-checklist-v2-20261006.md`（59 条；**F-13/E-338 已于票 41 按 (乙) 重写**，取数用 RUN_LINEAGE L6/N2 的新律 R_fam 8.74/10.91，非旧 9.75/11.99）；模型/数据层纪律 `~/.claude/rules/paper-writing.md`。

## Context
- 转述口径：a_res（因子）恒定 ≠ AASR 读数恒定——读数仍随 B_D∝cosψ 变 ~2 dB（真实几何效应）；高斜视端旧码虚好 ~5 dB 已消除。用户对此质疑过一次，已实测校准。
- 论文禁写：26.9°=物理边界（是注册保守值）、「分辨率-幅宽折中」为本文贡献（A0b，清单 F-14）、「驻留×f 因子」（f≡1）。
- 独立审计脚本消费面：verify_v3_verdicts/verify_ticket22 锚已重登记（新律值带溯源注释）；recompute_r_fam.py 等 v3 重算链留待下次审计会话（R30）。
- 双轨审余项：异源 CLI 对抗审已跑过（STANDS WITH CORRECTIONS 0🔴）；后续 T0 决策照旧双轨。
- **审计教训（票 41 根因）**：A-CROSS (乙) 定案只回填了实现者手上的文件（aasr.py/ADR/§8.14-15/两台锚/prereg A3+A6/清单 F-8+B4），**spec.md、清单 F-13/E-338、formula-spec §8.11-1/§8.13-3、prereg A9、RUN_LINEAGE、verify_paper_numbers** 全漏——登记面传播缺口。改语义后除代码外须扫全登记面（spec/清单/公式规格旧节/所有机器锚/血缘表）。
