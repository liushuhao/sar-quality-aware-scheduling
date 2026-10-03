---
name: research-agent-tools-deferred
description: agent 辅助工具延后引入清单——OpenResearch/hyperresearch/writing-dna-skill 均不装（2026-09-19 定论），各含唯一触发条件
metadata:
  type: project
---

2026-09-19 评估并经用户拍板：两个热门 research-agent 项目**当前都不引入**（不装）。

**结论分层**：
- **hyperresearch**（jordan-gibbs，Python，16 步综述管线 + OpenAlex/Crossref 期刊检索 + cite-check 闸 + markdown vault）——条件触发才装。**触发条件唯一**：Ch1 绪论综述（1.3.1-1.3.3）实际开写、且现管线（ppw:literature / get-paper / agent-reach）人工核验发现明显漏检期刊文献时，再装再试点。届时硬约束：① vault 必须放 `literature/` 下（红线：禁建顶层 `research/` 目录）；② 管线成稿文字不入论文正文（只用文献池/综合笔记/矛盾图，AI 文风 + 盲审风险）；③ dissertation 档 token 成本要有预算上限。
- **OpenResearch**（alphaXiv，Rust，实验基础设施）——观察名单。改判条件两条同时满足：Windows 出正式版（现为 beta）+ Ch5 regime sweep 实验矩阵确需 run lineage 管理。不作论文研究内容（盲审"物理载体"锚点，防跑题）。
- **Ch5 滚动 scoop 监控**：用现管线月级复跑 scoop-check，不靠新工具。
- **writing-dna-skill**（larashero3-dotcom 写作蒸馏器，2026-09-19 评估）——不引入。理由：目标体裁是媒体写作（公众号/图文），六层 DNA 中 L3 选题/L6 视觉对 LaTeX 投稿无用；学术文风由体裁决定非个人声音；语料门槛 ≥20 篇凑不满；写作痛点（逻辑/术语/AI 痕迹）已由 ppw 管线覆盖。**触发条件唯一**：Ch5 写作期章间文风漂移严重、或 ppw ASR journal 模板（`references/journals/asr.md`）手工建卡住时，用它蒸馏 literature/ 里 ASR 语料半自动建模板。

**Why**：Ch1 回填在 Ch5 定稿后（数月后），现在装 = vault 空转 + 提前烧 token，零收益；现管线已覆盖检索/查新/provenance 全部真实需求，hyperresearch 只是"净增量待证伪"的优化项。pip install 一条命令，two-way door，不装不损失未来选项。

**How to apply**：会话中再遇"要不要装/试用 OpenResearch / hyperresearch / writing-dna-skill / 类似 research 或写作辅助 agent 工具"提案，先查本条——默认不装，触发条件命中才升级讨论。试点产出核验沿用"断言未报告前多词形+语义核验"教训（见 ZCode 侧记忆 review-claims-need-semantic-search）。
