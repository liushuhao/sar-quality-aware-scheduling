# RDR-065 — S1b 引用完整性 + AI 痕迹（fresh full 重跑，2026-08-12）

**来源**：S1 INTEGRITY S1b（子 agent 引用上下文 + AI 痕迹 7 模式，fresh full 全程审稿）
**优先级**：P1（镜像矛盾）/ P2（事实措辞）
**状态**：部分 fixed（事实类已修；裁决类待 S3/S5）

## 机械/事实类（已修，中英同步 + 双版编译过）

| ID | 问题 | 修复 |
|---|---|---|
| B1 | ZH 摘要 L99-100 称稀疏区 MOO "覆盖率的显著下降，仅选择简单贪心调度器捕获目标的一小部分"，与 EN L126-129 "little coverage cost (MOEA-3 +58% f3 @2%, MOEA-2 +4.5% f2 @13%)" **直接矛盾**，且漏 +58% radiometric | ZH 镜像 EN 数值（2%/13%/+58%/+4.5%） |
| B2 | ZH L487 阈值标 "Vargha--Delaney 约定"，EN L666 为 "Romano, Kromrey, Coraggio, and Skowronek (2006)"（rdr-045 已定 Romano 正确）| ZH 改 \citet{Romano2006}；bib 新增 Romano2006 条目（J. Modern Applied Stat. Methods 5(2):423-437, 2006）+ EN/ZH 补 \citet |
| B3 | EN L218 "Chinese-language and Chinese-affiliated" 错——Wu2019 (Adv. Space Res.) 与 ChangZhou2025 (Ann. Oper. Res.) 均为英文期刊 | 删 "Chinese-language and"；ZH 删 "中文语言及" |
| B4 | EN L95/ZH L79 将 Wei2025MONP 列为 "agile SAR scheduling methods" 例外——bib 标题 "Agile Earth Satellite Scheduling Problem" 无 SAR（tavily 核实 Swarm Evol. Comput. 94:101857 为 EO 非 SAR）| 从 SAR 例外清单移除 Wei2025MONP（EN+ZH），保留 Kramer2025SARVis；L206/117 通用 EO 上下文仍引 Wei |

## 裁决类（S3 对抗验证 / 作者确认）

| ID | 问题 | 建议 |
|---|---|---|
| B5 | EN L197 Wu2026WhaleHighDensity 措辞 "reporting convergence challenges that echo the density-driven constraint tightening"——bib 标题为 "increasing task planning efficiency under high target density"，"convergence challenges" 为解读（Liu Fanming 共同作者，作者可确认）| 作者核原文；若标题更贴合，改 "targeting the efficiency loss at high target density" |
| B6 | bib 头注释 "25 cited entries" 过期（实 27 条）| P3，顺手改 |
| B7 | Jacquet2024GNN booktitle "SPAICE2024 / IWPSS 2025" 混两 venue；Wu2026 "pages 1--11" 卷文章页不全；Moreira2025 key 名 vs year=2026（rdr-032 已修 year，key 名 cosmet）| P3 维护项 |
| B8 | "rather than" 全文 31×（§6.4 内 6×：L888/892/930/936/982/1038）；"X is a property of Y" L887/L1082 重复 | P3，ppw:logic/de-ai 轻改部分；"not a mathematical identity"（RDR-002 诚实表述）明确排除不 flag |
| B9 | "Notably," L929 承 G-SM HV 反转（承重，非 AI 味）| 保留 |

## 验证清单

- [x] EN pdflatex + bibtex ×2 编译过（39 页；bibtex 仅 2 个已知正常 warning：Caleiras/Jacquet workshop 无页）
- [x] ZH xelatex + bibtex ×2 编译过（31 页；仅 SimSun 斜体 font-shape 警告，预存）
- [x] Romano2006 入库被引（EN/ZH），无 undefined citation
- [x] 中英 B1-B4 镜像同步
