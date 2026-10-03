---
name: project-next-paper-squint-duration
description: 下一篇小论文立项：滑聚/聚束变时长调度，scoop-check 9 步 Level 3 可投入；最近邻 5 篇（含五院总体部 CN112330091A）；含表述红线（禁说"斜视角-时长耦合无人做"）
metadata:
  node_type: memory
  type: project
  originSessionId: 4dfc6beb-03be-462e-b7d4-5951b6f61bd8
  modified: 2026-09-26T16:10:54.346Z
---

2026-09-25 下一篇小论文启动：滑聚(sliding spotlight)/聚束(spotlight)模式时长随斜视角变化的一等约束建模 + 任务收益与逐模式成像质量双目标（含条带→滑聚/聚束质量指标迁移）。前一篇（条带模式 quality-aware scheduling, ASR 投稿）已闭环。

> **本条目已于 2026-09-25 更新至 step9 收尾态**（原 07:25 版为 step1-8 记，已 superseded）。工件：`archive/scoop-check-20260925/step9-tail-closure.md`。

## 查新结论（scoop-check 9 步全跑，Level 3 — Medium Overlap）

可投入实验。**最近邻 5 篇各 2 轴**：
1. OSWVID（Chang/Zhou/Xing 组 AnnOR 2024，arXiv:2207.01250 全文核实——时长=优先级分配资源、质量=俯仰/横滚角代理、**全文零 SAR 物理词**）
2. multi-strip（NCA 2023，arXiv:2207.01257 全文核实，同组前驱）
3. **CN112330091A/B（北京空间飞行器总体设计部=五院总体部，2020 申 / 2023-09-08 授权，"星载 SAR 成像自主任务规划方法"）—— 同域 + 同单位**
4. Zhou ICSPCC 2025 机载 SAR（斜视角-时长耦合最近邻但机载波束级）
5. Kim & Chang 2020 AST（spotlight 星座调度，时长疑逐目标固定；三角定位关闭）

## ⚠️ 表述红线（写论文前必读，踩了会被审稿人打）

**禁止**再说「斜视角-时长耦合无人做」。CN112330091A 的规划准则 (b) 明写 *"正侧视时 SAR 卫星聚束模式成像合成孔径时间短，单次成像时间少可使得总成像时间尽可能的短"*，排序准则 (d) 明写 *"保证成像时前/后斜视角较小，使得成像时间尽可能的短"*——**中文域已把该耦合用作排序启发式**。期刊侧西电（系统工程与电子技术 2018, 40(7):1472-1477）已算 SSM 成像时长↔大斜视角。

**可辩护表述**（收窄后）：耦合闭环（调度选时刻→时刻定斜视角→斜视角定时长→**时长反哺可行性**）作为一等约束 + 逐模式 SAR 指标（分辨率重定义、AASR 因方位谱折叠升一级指标、RASR/NESZ）进 MOEA **独立目标维** —— 二者同时做，无人做。

**Delta 一句话**：Unlike OSWVID（分配式时长+角度代理质量），本工作时长=f(斜视角,模式) 物理内生、决策耦合闭环一等约束、逐模式 SAR 指标进 MOEA 目标。

**Why:** 耦合闭环无人建模；滑聚逐模式质量公式在成像文献已现成（Song 2025 Sensors 逐模式 AASR/RASR），"选哪套+怎么进目标"本身就是贡献点。

## How to apply

**工件**：`archive/3w-scan-20260925/report.md`（3W 扫描）+ `archive/scoop-check-20260925/step1-9.md`（step1-7 主链 / step8 风险关闭 / **step9 收尾 + 附录 A 目标函数追查 + 附录 B 中文新增**）+ 全文 PDF `literature/fulltext/`（OSWVID、multi-strip、Kim 2021、Zheng 2023 Sensors）。

**全部尾巴已关**（step9）：
- **A4** Springer Aerospace Systems 2025 = **虚警**：其摘要无 "variable image duration"，该字样来自其**参考文献列表**引用 B4 → 降 1 轴
- **B4** 书目更正为 *Appl. Soft Comput.* **vol 169**, art. 112575, **2025-01**（非 170 卷）；机构**湘潭大学**；摘要已获（IDRL-MQ/MD 决定起止时刻+时长，质量=observation quality 同 B1 谱系）→ 1-2 轴
- **B10** DOI 更正 `10.3873/j.issn.1000-1328.2017.06.005`（原记录脱漏连字符）；摘要已获（DDE-VNS；质量=f(观测时刻)，光学谱系）→ 1 轴
- **Kim 2020 AST**：开放渠道穷尽后三角定位关闭（摘要三源+同组孪生全文+施引扫描+域逻辑 → 时长=逐目标固定，LOW）
- **中文线**：free-web 面穷尽

**CN112330091A 目标函数是否含 SAR 质量项 → 不升级（step9 附录 A）**：升 3 轴需「含 SAR 物理质量指标式」**且**「时长为决策变量」，后者已被该专利步骤三/四 verbatim 文本证伪（时长/斜视角由波位设计与合成孔径时间**算出**；决策变量=排序顺序 + 成像区域集合 N；模式固定聚束无选择；质量仅作步骤六删减判据；目标为加权标量 w1+…+w4=1）。**唯一残余动作**：内部渠道调该专利说明书 PDF 核「含质量指标式」一项（本单位自有专利，分钟级，不影响 verdict）。

**竞争谱系**：湘潭大学 Chang Zhongxiang / Zhou Zhongbao 组（B1-B4 论文 + CN120180917A 专利，同源已由 B4 机构确认）= 最直接竞争者；五院总体部 = 同域同单位矩阵（CN112330091A/B + CN111007506A/B + CN106226768A）。

**时长模型的中文物理引用源**：CN111007506A/B（五院总体部，滑聚时长=滑动因子 + 波束地面移动速度）；西电（系统工程与电子技术 2018, 40(7):1472-1477，多普勒中心距离空变量最小约束算 SSM 成像时长，处理大斜视角）。

**下一步** = 实验构建（复用本仓 src/ 求解器 infra，变时长=窗口模型改造，matt 工作流 TDD 从第一票上）。

**投稿前 final check**（唯一未跑项）：知网/万方专业检索式——主题 = 滑聚*调度*成像质量 / 滑聚*任务规划*时长 / 斜视角*成像时长*(任务规划+卫星)。本查新无订阅，仅 free-web 可达。

**环境注意**：`paper-search` 专家技能（search.sh / paper.sh）**硬依赖 `jq`**。本机原缺 → 已 `winget install jqlang.jq`（装到 `C:/Users/33151/AppData/Local/Microsoft/WinGet/Packages/jqlang.jq_Microsoft.Winget.Source_8wekyb3d8bbwe/jq.exe`）。GitHub release 直连被网络策略阻断（curl exit 35），不要试图从 release 下载。

**注意**：`literature/` 命中 `.gitignore:13` → 上述全文 PDF **不入版本控制，仅本地存在**（换机/清理即丢）。

> **2026-09-26 增量**：idea-spark 五跑审查闭环（四维全过，见 [[project-ideaspark-audit-20260926]] / `.agents/memory` 同名）；用户裁决可投实验。~~下一步 = 架构闸 A 环节~~ → **A 环节已闭环（见文末增量）**。

> **2026-09-26 A 环节闭环增量**：seams 四层确认（用户拍板）→ spec v0.2（回写 6 项 + steel-man 硬化）→ ADR GRILL-002 落盘（`reference/adr/`，AGENTS.md 红线行 + Placement 表两处例外注）→ steel-man A1-A17 全落修（2🔴：A1 f_Q 改逐模式 achieved ρ_a·g_T 辐射因子——偏离 P3 拍板字面式，**用户 2026-09-26 已同意**（设计澄清见 paper2-fq-design-rationale）；A2 蓝图 SLS 公式方向矛盾升 blocking gate）→ gate-review 四路 14 处修复 + 确认轮 13/13 闭合 → **to-tickets 12 票落本地 `.scratch/sliding-spotlight-scheduling/issues/01-12`**。下一步 = 工作前沿：票 01（SLS/公式钉死）+ 票 02（骨架/fork manifest/Kim fixture）无前置可并行。工件：spec.md + disposition-ledger.md（56 项零空白）+ architecture-gate.md（审查轮次全录）。全部本地留存（reference/、AGENTS.md、.scratch/ 均 gitignore，无可提交项）。

> **2026-09-26 step10 残余闭合**：三族（RRM/DTCTP-crashing/speed-scaling）+ 知网检索式 free-web 等价跑完，**Level 3 维持无升轴**。工件 `archive/scoop-check-20260925/step10-residual-families.md`。要点：①新增次近邻 5 条——CN115545410A/B（**上海卫星工程研究所**，方位敏捷多目标，时长由波位参数算出、零质量零模式选择）+ 宇航学报 47(7):1889 2026（同所+哈工大，光学推扫，像移速度质量+优先级，时长固有）+ Yao RS 16(9):1496 2024（ISAR 时长变量，脉冲级）+ JORMS 2024 时变收益（光学）+ Q-RAM/DTCTP-C/近似计算 mandatory-optional 三条引用素材；②**竞争矩阵新增：上海卫星工程研究所**（SAR 方位敏捷专利 + 光学质量规划论文双线活跃）；③**表述红线追加：禁说「质量感知卫星调度无人做」**（光学域已活跃），可辩护表述仍限「耦合闭环一等约束 + 逐模式 SAR 物理指标独立目标维 + 模式选择三者同时」；④sciengine 多星协同论文明写「未考虑卫星斜视」= 间隙正面确认；⑤订阅版知网专业检索仍留投稿前用户侧（free-web 已扫）。

> **2026-09-27 强模型升级重审闭环**：用户换 GLM-5.3 全量后对 A 环节产物复审（5 路并行 fresh subagent，升级重审模式不喂旧发现清单）——flash 轮 13/13 全 PASS 被推翻：**5 维各有 FAIL，25 项发现全落修**（ledger #58）。硬项：M1 验证区间欠约束（tag 区间双查）、fork 包名 sar_sim 致守卫自比自假绿、票 07/08 缺 Blocked by 01、票 01 无 AASR 取式致票 06 悬空边、τ 解码四位点（moea.py:128/:410/:679+so_f1.py:82）、票 09 死验收。确认轮 23/23 PASS 闭合，spec v0.3。教训：**flash 审查链多轮全绿 ≠ 无缺口，档位升级后升级重审值得**；阈值类预注册值（0.5%/1.10/≥20）为复审轮新定，实验前用户可否决。
