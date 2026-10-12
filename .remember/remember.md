# Handoff

## State
- **review2 R1 波（修图）已完成并收口**。图修复全落地并提交：`f5ce52e`（fig2 重建：折行网格 + \resizebox）、`2ecc2ef`（fig2 行距压缩 + 残重叠清零）、`e4b2f88`（fig3-7 round-2 rcParams 统一定稿）。
- 验收全绿：七图视觉清单 PASS（PyMuPDF 机验 0 文字重叠 + 主模型读图全过）；五脚本 stdout vs 基线全 IDENTICAL（数据零漂移）；编译 rc=0 / 0 error / 38 页；census C2 diff 空、C1 语义 guard 全冻结（AASR/1+0.25/11/1 计数不变，坐标 delta 全量入 `r1/census_exception_table.md`）；暗卷五快脚本全 rc=0（红线 0 / 回源 0/39 / prereg 28 / v3 33 / claim 11）。
- red_proof 有效（做坏 fig3 注记压图例→机验抓 3 clear FAIL；还原 IDENTICAL→回 0）。
- 残留：porcelain 仅 `M .remember/now.md`（插件）+ `?? .githooks/`（并行会话，勿碰）；run_verify 全量（528 测试）本轮未跑（R1 完成条件不含）。

## Next
1. **发射 R2 波（内容波）**：书 `goal_book_review2_r2.md`（`55c9571a` 未动）、spec blob `50be1fa4` 仍有效。面板/独立审按 R37 教训禁云图像路径（本轮主模型读图系用户显式授权 C，R2 不默认沿用）。
2. R2 完成后终闸。

## Context
- 运行纪律不变：勿改 `~/.claude/settings.json`；论文口径禁动（26.9°/真窗 v3/R_fam 8.74/10.91）；`?? .githooks/` 勿碰。
- 图 文件→PDF 页映射：figN 文件名=outline 编号 ≠ PDF Figure 编号（按 main.tex \begin{figure} 源序）。真映射：fig1→p10/F1、fig2→p16/F2、fig7→p21/F3、fig4→p25/F4、fig3→p26/F5、fig6→p27/F6、fig5→p28/F7。
- 关键教训：PyMuPDF 文字重叠机验阈值过严（1.2mm）会漏真重叠——本轮 0.8mm 轴阈才抓出 fig2 右列 c2×c34/c2×conf 的 1.4mm 压字；TikZ 节点继承过大行距（~15pt）致盒过高，`\baselineskip=3.4mm` 压缩是排版可控关键。
