---
name: project-ideaspark-audit-20260926
description: 第二篇稿子想法 idea-spark 五跑审查闭环：四维全过（4 条 spec 硬化项 + 3 篇新增近邻 + 可发表性中高）；工件 archive/ideaspark-audit-20260925/
metadata:
  node_type: memory
  type: project
  originSessionId: 443f6e6b-e4a4-403f-bace-1d0cbc6ee736
  modified: 2026-09-25T22:31:13.747Z
---

2026-09-26 第二篇（滑聚/聚束变时长调度）想法经 idea-spark 五跑审查（多 query 复跑律）闭环，接续 [[project-next-paper-squint-duration]] 的 scoop-check。

**判决**：模型正确性/算法有效性/创新性/可发表性四维全过；可发表概率中高（ASR/IJAE 级）。五跑 = q1 direct advance / q2 framing revise→闭合 / q3 mechanism advance / q4 architecture advance（池降级，SS 配额死+arXiv 406 仅 OpenAlex）/ q5 同句对照 advance（池 ⊇ q1，收敛同机制族）。

**Why**: 实验构建前最后闸；结果支持投入实验，但带回写项。

**裁决（2026-09-26 用户确认）**：三项待裁均同意——spec 回写 4 项随架构闸 A 环节并入；+3 近邻与 delta 收窄写论文期执行；可投实验绿灯（下一环节 = A 环节）。

**How to apply**:
- 工件：`archive/ideaspark-audit-20260925/synthesis-report.md`（四维判决+证据链）+ `runs/q1-q5/`（q1 含完整 Phase 4 三语卡片）+ `worklog.md`。
- **spec 回写 4 条**（下次动 spec 时并入）：D2 模式映射方向 = coarsest-sufficient（finest 会使模式熵≡0，q3 执行证据）；§3.1(A) 窗预编译子区间并集从防御细节升硬要求（U 形 squint 非凸可行集，q1 执行证据）；可行性谓词含 e≤w_e（q2 执行证据）；"零违规"声明只相对模型口径（q5）。
- **related work +3 篇**（scoop-check 未覆盖）：W4366808570（2023 线性劣化+PSD 双目标并行机——理论侧最近邻，delta 句加一档收窄）；W7124926031（2026 列生成 multi-AEOS，模式盲，精确法基准引用）；6ea23b35（2026-04 SAR 窗生成物理质量筛查，stripmap 二值阈值——质量侧最近邻）。fe7cb2fa = scoop-check B4 确认同键。
- **投稿前补查族**：radar resource management / DTCTP-crashing / speed-scaling（deteriorating-jobs 已由 q2 整池闭合：裸机标量目标无双目标窗口化）。
- 论文预留：真实/半真实任务臂（五跑共性顾虑=全合成场景）+ 模式外生化正面辩护段（q2 独立生成默认模式当基因=领域直觉默认，审稿人必问）。
- **ZCode 侧讨论沉淀对账（2026-09-26 用户令）**：`.remember/plan-20260925-paper2-design-constraints.md`（ZCode 会话沉淀，定位=参考非硬约束）与本审查五跑独立收敛一致（双目标/模式集/f1=Σp/红线），无冲突。spec 回写清单 4 项→**6 项**：+⑤归一层锚禁令（质量锚禁用"各模式自身最优"否则跨模式差异抹平，ZCode §3.2，命中 q3 dB 裕度坐标）+⑥模式可行性判据=方位向尺寸 vs 波束方位脚印（与时长几何共用，ZCode §5，蓝图未显式写）。用户裁决：6 项均留 A 环节一并处理。§4 指标/排除清单、§5 条带证伪条件 → A 环节素材。「模式选择内生化」措辞按蓝图 §1 外生化口径表述防误读。
- 环境教训：SS 匿名日配额会耗尽（run4 整源 0）；arXiv API 当日 406 拒本机；MDPI 403——本地 `literature/fulltext/` 语料注入 fulltext_cache（source_used=local_corpus_inject）是可靠兜底。
