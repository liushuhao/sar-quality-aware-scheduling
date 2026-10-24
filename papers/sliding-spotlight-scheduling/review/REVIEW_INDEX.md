# REVIEW_INDEX — sliding-spotlight-scheduling (paper2) 审查追踪

状态：pending → fixed → closed-with-evidence ｜ rejected = 裁决为不采纳 ｜ superseded = 被新批次取代（注明取代者）｜ waived = 作者豁免（附理由）｜ deferred = 延期（附 owner+触发）

> 本索引指向各活跃审查批次的 Roadmap 与裁决 sidecar。paper2 的审查工作流与 paper1（single-sat-quality）同制（见项目 CLAUDE.md「审查意见追踪」）。

## 当前活跃批次

### 2026-10-23 t54 后全量面板复审（ARS 五席 fresh + 编辑裁决 + 三层链闭合 2026-10-24）→ Major Revision

- **面板产物**: [panel-full-20261023/](panel-full-20261023/) — 五席报告（seat1-eic / seat2-methodology / seat3-domain / seat4-perspective / seat5-devils-advocate）+ [editorial-decision.md](panel-full-20261023/editorial-decision.md)（含 T1–T22 路线图、DA 两条 CRITICAL 裁决、§8 复审整合、§9 终裁整合、六轴 provenance）。审查对象 = t54 八步修订后的 main.tex（commit 479eda5），五席全部 fresh 上下文、互不可见、不读旧批次。
- **三层链（2026-10-24 闭合）**: ② Claude Code 复审（ark 后端，[rr1-claudecode-rereview.md](panel-full-20261023/rr1-claudecode-rereview.md)）= 综合裁决 SOUND-WITH-CORRECTIONS（0 伪造、算术全复现、两 CRITICAL 维持、3 综合小缺陷 + 3 稿件新发现 N1–N3）；③ opencode 终裁（deepseek-v4.1-flash-free，[adjudication-opencode-20261024.md](panel-full-20261023/adjudication-opencode-20261024.md)）= **Major Revision 维持，置信 high，链 SOUND-WITH-CORRECTIONS**；四处修正已并入（T20–T22 入表/T5 日期护栏/R4H 归正/T1 重定价 E[min]/E[p]=0.7）。终裁 J4 残余风险：全部限定后残余贡献可能被判增量性——无路线图项可测，唯一「合规修订仍被拒」路径。
- **裁决**: Major Revision（四席一致 + DA 2 CRITICAL 均判 validated + 复审维持 + 终裁维持）。两条 CRITICAL = 反事实 18–30pp 换修理规则即变（缺口≈被丢任务优先质量，主线程算术核实；优先级感知修理仍保留 ≈70% 缺口）/ 标题因果主张撞家族混杂设计（§6.1 自认共变、无交叉单元）。
- **核验**: 领域席独立重算 §3/§7.2 全部物理常数链逐位复现（含 AASR 序列、SLS≡STR 退化、f_dc=345.7kHz、oracle 偏差）；方法论席复算全部统计量零内部不一致；主线程+复审+终裁三方独立复算地板核算/掉任务质量/速度比 1.0493/垫减半 5.4% 全部命中。
- **与 2026-10-22 批次关系**: 独立新批次，非取代；重叠项=佐证残留未清（如双句点仍在文中）。triage 时应做 T1–T22 × R-01…R-36 交叉映射后并批执行。
- **t55 执行（2026-10-24 闭环）**: T1–T22+Tier-3 全部落地，票 `.scratch/t55-panel-fixes/issues/00-execute-t1-t22.md` completed。再分析六件（修理臂三规则/裕度重放/档位平移两臂/精确链/服务任务数/预算核查 40 单元）全部脚本化入 `experiments/v5_results/` 并入数字闸 T55 组（141 检查 rc=0，11 新变异探针 59P）；三轮独立复审 R1→R2→R3（R3=LOOP CLOSED，产物 `t55-round{1,2,3}-*.md`）；双面回归 src 164P + domain 723P+1S；编译 0 错 58 页。裁决记录：T2 取改措辞路（标题去因果动词）；T5 存储时机维持 upon-acceptance（用户既定拍板）；R3H 预算臂实测s=0.9 残差 4×预算不动。
- **状态**: executed（T1–T22 闭环；待用户过目修订稿与标题新措辞）。

### 2026-10-22 独立外审（五席 + 编辑裁决）→ Major Revision

- **审查报告**: [paper2-independent-review-20261022.md](paper2-independent-review-20261022.md)
- **Roadmap（含主线程独立复算核验证据）**: [revision-roadmap-20261023.md](revision-roadmap-20261023.md) — 36 项发现 R-01…R-36；**每条均经独立复算核验**（✅成立 / 🟡半成立 / ⓘ披露已覆盖），核验命令与结果随条携带。
- **作者裁决 sidecar**: [author-adjudication-20261023.md](author-adjudication-20261023.md) — **Status: DRAFT，待用户逐条裁决**（will_address / wont_address / not_on_point）。
- **终审（ZCode 席，2026-10-23）**: [terminal-review-20261023.md](terminal-review-20261023.md) — 第三席终审：15 项承重数字独立抽验全部命中、4 处两席分歧逐处实证（核验席修正全成立）；**Major Revision 成立、36 项 0 项不成立、P0 必修**；含逐条终审裁决（四档）与 8 步执行顺序；待用户拍板 6 项（标题/R-08 修法/Fig 4/Pearson/DOI/P1-8）。

| 主题 | 条目 | 核验分布 | 状态 |
|------|------|----------|------|
| Part A 阻断级（B1–B7 方向/基线/带宽/混杂/计数/预注册/印出错误） | R-01…R-10 | ✅ 8 / 🟡 2 | pending（待裁决） |
| Part B 方法/统计（机动/相关/文献/种子/容差/EA/CI） | R-11…R-18 | ✅ 8 | pending（待裁决） |
| Part C 领域（速度/AASR/方向对比/约束绑定/cloud-cover/措辞） | R-19…R-24 | ✅ 4 / 🟡 2 | pending（待裁决） |
| Part D 格式/引用/排版（class/引用/bib/摘要/图/双句点） | R-25…R-36 | ✅ 11 / ⓘ 1 | pending（待裁决） |

**核验结论**：36 项中 **0 项经复算被判不成立**；审查的承重数字（26.01/46.58/46.02pp、0.5007/0.7484/0.5694、477,308→13,845、r 0.3286→−0.0699、SAT=synthetic aperture time、预注册时序 2026-10-20 sweep vs 2026-10-21 amendment）全部逐位复现。审查的 Major Revision 裁决有充分证据支撑。数字闸基线：`verify_paper_numbers_l8.py --paper main.tex` rc=0、74/74。

**注意事项（裁决时参考）**：
- R-08（f_Q,deliv cos²ψ）：审查定性「印错公式」过重——印式与 formula-spec §8.17-10 注册口径逐字一致；真缺陷是「squint-loss」命名方向反 + 「delivered」读数带多余 sec²ψ。
- R-12（两相关）：审查「违反自定 no-pooling 口径」子主张不准确——该口径禁 raw f_q 合并，相关用的是归一化兑现率；真问题是相关性脆弱 + 闸不覆盖。
- R-19（速度）：正文 L97 已明确披露惯性速度口径；真缺口是无敏感性分析。
- R-34（Data availability）：与台账 R42（Zenodo DOI）同源，待用户 DOI 串。

## 历史批次

- 2026-10-20 票50前置四轴审查（TRAE）→ 对账确认 B1/B2 已三重注册裁决，非开放项；见 [paper2-ticket50-four-axis-audit-20261020-trae.md](paper2-ticket50-four-axis-audit-20261020-trae.md) + [paper2-ticket50-trae-audit-reconciliation-20261020-zcode.md](paper2-ticket50-trae-audit-reconciliation-20261020-zcode.md)。
- 2026-10-20 项目级复盘 → [retro-project-20261020.md](retro-project-20261020.md)（五类元模式 + 结构性教训「写作期在裁决未定前铺开」）。
