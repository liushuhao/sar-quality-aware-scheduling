---
name: figure-tooling-setup
description: scipilot-figure-skill installed; scientific-agent-skills figure assets removed
metadata: 
  node_type: memory
  type: project
  originSessionId: 6090f757-ae6b-4618-ad54-db920f1c2326
---

**2026-07-22**: 画图工具链已迁移至 scipilot-figure-skill。

### 全局安装
- **scipilot-figure-skill v2.1.0** — `~/.claude/skills/scipilot-figure-skill/`
  - 可视化顾问：数据剖析 → 按论证目标推荐图型 → 主动拦截 18 条画图禁忌
  - 视觉自检闭环：渲染 PNG → 程序自检缺字/裁切/重叠 → AI 读图复核 → 回改
  - 多期刊规范：Nature/Science/IEEE/Elsevier/PNAS/CJK
  - 技术栈：matplotlib + seaborn + SciencePlots（静态）+ plotly（交互）

### 已清理的本地资产
- 从 `scientific-agent-skills-main/scientific-visualization` 复制的文件已全部删除：
  - `scripts/`: style_presets.py, figure_export.py, color_palettes.py
  - `styles/`: nature.mplstyle, publication.mplstyle, presentation.mplstyle
  - `references/`: journal_requirements.md, color_palettes.md, matplotlib_examples.md, publication_guidelines.md
- 原因：scipilot-figure-skill 完全覆盖且超越（setup_style.py → style_presets；export_figure.py → figure_export；7 份参考文档覆盖 4 份）

### 保留的生成图
- `figures/` 下 fig1-fig6 的 PDF/PNG 仍是论文用图，不受影响
- SciencePlots 仍在（scipilot 依赖它作为样式引擎）

### 其他技能
- **Superpowers** — 已卸载（与 mattpocock-skills 重叠，无可替代价值）
- **mattpocock-skills** — 已安装（22 skills，覆盖 engineering 全流程）
- **nature-skill** — 仍不推荐安装（结论不变）
- **Paper-Polish-Workflow-skill** — 2026-07-22 安装（16 ppw skills：polish/de-ai/logic/abstract/caption/reviewer-simulation/team 等，见 AGENTS.md 速查表）
  - 安装位置: `.agents/skills/ppw-*`（项目本地）
  - 用途: 论文润色全流程，可作为 ARS 管线的"后写作"补充
  - 限制: 需要 `references/journals/[journal].md` 模板才能指定期刊，ASR 模板未创建

**Why**: scipilot-figure-skill 的"顾问+自检"模式填补了之前只有"样式预设+导出"的缺口，且 CJK 支持对中文论文有实际价值。

**How to apply**: 需要画图时调用 `/scipilot-figure-skill`，它会先做数据剖析再推荐图型，最后走自检闭环。旧版 `gen_all_figures.py` 等脚本仍可运行，但新图建议走 scipilot 流程。