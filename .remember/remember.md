# Handoff

## State
- **票 41/42 闭环**（2026-10-08，commit `ff444e6` + `4e5ad3f`，树净 HEAD=4e5ad3f）：三层审计 + 文献组织核查发现 A-CROSS (乙) 定案的**登记面传播缺口**——代码主链已切 (乙)，9 处登记/写作文档仍教旧律 (甲)。票 41 全回填（formula-spec §8.16 点名取代 §8.11-1/§8.13-3、spec.md D12 dated 勘误、spec-amendment §8.9、清单 v2 F-13/E-338、prereg 追加块取代 A9/strata R_fam〔9.7524/11.9886→8.7407/10.91〕、RUN_LINEAGE L6/N2、caliber 措辞、三处旧律注释、`verify_paper_numbers.py`+测试改 (乙)）。
- 票 42 文献入库：A-CROSS 一轮 4 篇 + GF-3/Kim/Song + Li 2018 + Li 2025 = 9 篇进 `literature/{raw,fulltext,structured}` + `literature_corpus.csv`（333 行）；Ren 2025 PDF 补取成功；Li 2025 仅 metadata_only（venue 未证）。
- 域套件 374P/1S exit 0、共享库 154P exit 0、五门禁 rc=0。冻结件 `platform_kim2021.json` 字节未动；prereg 冻结前缀字节保真。
- 台账 open=5（R7/R19/R27/R30/R31；R31 部分处置，R30 = recompute_r_fam 旧律锚延后）。
- **残留清理（票 43，2026-10-09，commit f44819f+68a159e）**：`recompute_r_fam.py` 默认改指 v3、复现现行判词（R30 闭）；R27（C 类锚=先修快照，加日期化说明）、R31（Li 2018 全文 + Li 2025 venue 定位 EICARS 2025）、R7（上游 behind=0）全闭。**仅 R19（Ch5 物理违反）维持 gated=票 27**（Ch5 未发表、修复改其结果；**不阻塞票 38**）。台账 open=1（R19）。

## Next
1. **票 38**：workflow v3 落地，吃 (乙)——不插重跑段、取数留 v3。
2. **写作期开工**：`writing-workflow.md` v3 + `writing-checklist-v2-20261006.md`（59 条；F-13/E-338 已按 (乙) 重写，取数用新律 R_fam 8.74/10.91）。

## Context
- 转述口径：a_res 因子恒定 ≠ AASR 读数恒定（仍随 B_D∝cosψ 变 ~2 dB，真实几何效应）。
- 论文禁写：26.9° = 物理边界（实为注册保守值）、「分辨率-幅宽折中」为本文贡献、「驻留×f 因子」（f≡1）。
- 审计教训（票 41 根因）：语义变更除代码外须扫**全登记面**（spec/清单/formula-spec 旧节/prereg 子键/血缘表/所有机器锚）——见记忆 `paper2-semantics-change-propagation-surface`。
- 独立脚本消费面：`recompute_r_fam.py` 旧律锚待重登记（R30）；写作期首次引用 R_fam 数字时触发。
