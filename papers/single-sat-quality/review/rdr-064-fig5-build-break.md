# RDR-064 — fig5_ablation.pdf 被误删，HEAD 编译断

**来源**：S1 编译门（2026-08-12 全程审稿重跑，EN pdflatex fatal）
**优先级**：P0（build-breaking 回归）
**状态**：fixed（文件恢复；gen_all_figures 图清单待 S4 审计补齐）

## 评论/发现原文

```
! Package pdftex.def Error: File `fig5_ablation.pdf' not found: using draft setting.
l.95 ...phics[width=\textwidth]{fig5_ablation.pdf}
!  ==> Fatal error occurred, no output PDF file produced!
```

## 根因

commit `040a9e3`（"remove orphan figure assets"）删除 `figures/fig5_ablation.pdf`，判定依据是
`gen_all_figures.py` 只输出 fig1-4。但 `sections/_ablation_section.tex` L95 与
`_ablation_section-zh.tex` L91 **仍引用**该图（\includegraphics + \label{fig:fig5} + 文本
Fig.~\ref{fig:fig5}），RDR H6/V6-F01 明确补过该引用——图非孤儿，属误删。

## 决策

🔴 必须改 —— 编译断，且消融图是论文 Fig.5 必备。

## 修复

从 git `6c4e98d` 恢复 `figures/fig5_ablation.pdf`（38.1K）。

## 验证清单

- [x] fig5_ablation.pdf 恢复
- [x] EN pdflatex ×2 编译过（39 页）
- [x] ZH xelatex ×2 编译过（31 页）

## 备注

- `gen_all_figures.py` 无 fig5/ablation 输出——消融图生成脚本不在仓内，复现性缺口，
  列入 S4 图审计（F-NNN）处理：fig5 数据须回源当前 ablation_summary.csv + 生成脚本入仓。
