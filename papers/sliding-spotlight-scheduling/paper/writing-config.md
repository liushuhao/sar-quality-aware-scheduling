# Paper2 写作配置（W0 钉死四值）

> 本文件为 `papers/sliding-spotlight-scheduling/paper/` 写作期配置，四值为定稿口径，改动须用户批准。
> 对应清单 v2 A 段 A1（Configuration Record，ARS IRON rule 1）。

| 配置项 | 值 | grep 锚 |
|---|---|---|
| citation-style | `citation-style=authoryear` （bibliography style = elsarticle-harv） | `grep 'citation-style=authoryear' writing-config.md` |
| output-format | `output-format=markdown` （正文工作稿以 markdown 交付，LaTeX 侧由 main.tex 组装） | `grep 'output-format=markdown' writing-config.md` |
| language | `language=en-only` （英文 only，禁中英混排正文） | `grep 'language=en-only' writing-config.md` |
| citation-placeholder | `citation-placeholder=\cite{key}` （正文引用一律 `\cite{key}` 占位，key 对应 .bib entry） | `grep 'citation-placeholder=\\\\cite{key}' writing-config.md` |

辅助记录（非四值）：
- documentclass：elsarticle（kpsewhich 实证 `C:/Users/33151/AppData/Local/Programs/MiKTeX/tex/latex/elsarticle/elsarticle.cls`，exit=0，2026-10-10）
- 终稿节序：引言先行（已裁，非裁量）；W3 起草章序=v3 钉值「建模公式→…→摘要」（起草序非终稿序）
