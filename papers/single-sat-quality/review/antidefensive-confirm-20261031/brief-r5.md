# 审查任务书 — 反防御性写作修改批独立复审（红队视角）

## Canary（必须遵守）
1. 只读审查：除你的 stdout 外不得修改、创建、删除任何文件。
2. 每条发现必须引用稿件原文（逐字），附节名与 tex 行号。
3. 不编造事实；数字逐字引用稿件。
4. 无网络访问。
5. 有什么报什么；不得制造发现，也不得盖章放水。若一切干净，明说干净。
6. stdout 输出完整审查报告。

## 背景
- 稿件：`papers/single-sat-quality/small-paper-ijae.tex`（单卫星敏捷 SAR 调度论文，已投 ASR）。
- 最近三波 commit 对稿件做了一批「反防御性写作」措辞层修改（原则：论文是学术发布会，不是自我审查报告——删除作者主动递给审稿人的自白句、合并重复限定语、精简重复 caveat）：
  - ceaf935：主批（diff: `papers/single-sat-quality/review/antidefensive-confirm-20261031/diff-ceaf935.patch`）
  - 16a972b：确认轮修复（diff: `papers/single-sat-quality/review/antidefensive-confirm-20261031/diff-16a972b-fix.patch`）
  - 6f2561a：证伪轮修复（diff: `papers/single-sat-quality/review/antidefensive-confirm-20261031/diff-r3-fix.patch`）
- 修改后全文 = `papers/single-sat-quality/small-paper-ijae.tex`（约 1710 行）。
- 声称：零数字改动、纯措辞层、不损失必要限定。

## 你的任务：以红队立场攻击这批修改
先完整读两个 diff，再对照修改后全文。你的职责是**证伪**「这批修改干净且无副作用」——主动找：
1. **事实失真**：改写/删句后，句子是否陈述了与正文其他部分矛盾的内容（求解器行为、实验范围、数字归属）？
2. **夸大漂移**：删除限定语后，摘要/引言/结论的主张是否比证据更宽（conditional / approximate / tested-scope 类必要限定是否在某处被删光）？
3. **结构残伤**：删句拼接处的语法残缺、指代悬空、逻辑断裂、别扭重复；交叉引用是否失去承载。
4. **一致性破坏**：摘要—引言—结论三处对同一事实的表述是否仍然互相一致；修改是否造成正文前后矛盾。
5. 任何其他你独立发现的问题（不限于此清单）。

## 输出格式
```
## 发现列表
（每条：CRITICAL/MAJOR/MINOR/NOTE + 行号 + 原文引用 + 理由 + 建议；无发现则写「零发现」）

## Verdict
PASS / PASS-WITH-FINDINGS / FAIL + 一句总判
```

## 效率指引
全文可整读。diff 先读，hunk 前后各 ~15 行上下文必查。宁缺毋滥：每条发现必须能被原文逐字支撑。
