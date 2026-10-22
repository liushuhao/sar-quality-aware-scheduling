# Terminal Review — 2026-10-22 独立外审终审（ZCode 席）

**对象**: `paper2-independent-review-20261022.md`（五席外审，Major Revision）+ `revision-roadmap-20261023.md`（36 项核验）+ `author-adjudication-20261023.md`（DRAFT）。
**性质**: 第三席终审。对两席一致条目做承重数字抽验（非全量重跑），对两席分歧 4 处（R-08/R-12/R-19/R-30）逐处下场实证。
**结论先行**: **审查的 Major Revision 裁决成立；36 项 0 项不成立；核验席对审查的 4 处修正全部成立。P0 十条必须全做（Reject 触发条件在案），P1 建议做满。**

## 终审独立实证（本席复算，非转录）

| 项 | 方法 | 结果 |
|---|---|---|
| 收紧方向代价 | 自 sweep_results.json 重算族中位差 | R3H 1.0→0.9 = 26.01pp、1.0→0.8 = 46.58pp；R1C 1.0→0.9 = 46.02pp；R2F 0.27/0.00pp；头条 4.15/2.36 复现（R-01 ✅） |
| 配对 per-seed delta | 10 场景逐对 | R2F 0.935pp（=头条 2.36 的 40%）；R3H 3.978pp、10/10 正（R-18 ✅） |
| Pearson 脆弱性 | 重算 + 去单点 | r=0.3286(n=26) → −0.0699(n=25)（R-12 ✅） |
| 地板排除份额 | 10×R3H + 10×R1C manifest 逐任务 | R3H s=0.8 上界 0.5007、s=0.9 上界 0.7484（口径=非 STR 全可行 + STR 按 0.9ρ≥2.4669）；R1C s=0.9 上界 0.5694；seed300 构成 54 STR+15 SLS+30 SPT（R-04 ✅） |
| 477,308 分解 | 260 单元 front 记录重扫 | Σn_selected = 477,308（9,430 条）；最佳成员 distinct 任务 = 13,845（34.5×）（R-05 ✅） |
| AASR 门槛绑定 | 30 manifest generation_ledger | removals = aasr 0 / footprint 0 / below_finest 0 / no_window 15（R-20 ✅） |
| SAT 定义 | Kim fulltext grep | `saturat` 零命中；§2.3 标题 Synthetic Aperture Time（R-09 ✅） |
| ρ_req 带宽 | scenarios.py 注释 + 正文 grep | 粗档 [2.5,3.0] 冻结（"ENTIRELY inside the STR routing tier"）；正文带宽 0 披露、地板 2.4669 有（R-03 ✅） |
| 种子直传 | run_matrix.py 源码 | `split("_seed")` → `--seed` 直传求解器（R-14 ✅） |
| bib 缺陷 | 计数 | 307/307 双括号、147 journal 残留（R-27/28 ✅） |
| R1C C3「met」 | sweep_results checks | C3=true 直接由 0.0 < 1.0 产生（exit11 记零约定）+ 正文 L287 自认（R-07 ✅） |
| R-08 印式 vs 注册口径 | formula-spec §8.17-10（:588） | 逐字一致——**非印错**；sec²ψ 源于任务级 A_task=2ρ_req·cosψ_sel/D 代入库口径恒等链，内部自洽；真缺陷 =「squint-loss factor」命名方向反 +「delivered」语义混（核验席修正成立） |
| R-19 速度披露 | main.tex L97 | 披露明文在（inertial ≠ beam-footprint ground velocity）；缺口=敏感性（核验席修正成立） |
| R-12 no-pooling 子主张 | main.tex L242 vs L332 | L242 禁的是 R 族 raw f_q（index levels）跨族合并；相关用的是归一化兑现率——审查子主张过重（核验席修正成立） |

## 终审裁决（36 项 → 四档）

### 第一档：必修（P0，审查 Reject 触发条件在案，不做即拒）

| ID | 裁决 | 改法（终审版） |
|---|---|---|
| R-01 | 必修 | 摘要+§6.2+结论**双向报告**：收紧方向数字（R3H 26.0/46.6、R1C 46.0/不可行、R2F 0.27/0.00）进摘要或 §6.2 汇总句；4.15/2.36 标明「相对本族饱和点（放松端）」。标题可保留（正文 §6.1 方向正确且收紧端是主损失，双向报告后标题成立）。 |
| R-02 | 必修（随 R-01） | §6.2 补饱和点网格依赖披露一句（R1C 饱和=订单点、R2F 在网格边界 2.0——正文 L281 已有雏形，补「premium」性质定性）。 |
| R-03 | 必修 | §5.1 加一句带宽（粗 [2.5,3.0]m / 细 [0.3,0.6]m / 地板 2.4669m）；R1C s=0.8 改一行解析结论（0.8×3.0 = 2.4 < 2.4669）；该格判定改 undefined。 |
| R-04 | 必修（工作量最大） | 新增模式分解表（每 s 下 STR/SLS/SPT served/dropped/priority，数据全部可自 manifest+pilot artifacts 复算，本席已验上界数）；据此重写 §6.1/§6.3 机制段为「地板排除主导」。**表数字须进数字闸**，防重蹈 R-12「闸外数」。 |
| R-05 | 必修 | 摘要/结论删「477,308 + no violation」句；正文 L322 保留并加 distinct 13,845 对照；C5 改述为 per-mode delivery rule（STR 无恒等式）。 |
| R-06 | 必修（一句话） | §3.5/L177 补 amendment 时序（2026-10-21 登记晚于 2026-10-20 数据；headline 属 post hoc descriptive；K1–K3 与 grid 本身为预先登记——保留）。 |
| R-07 + R-16 | 必修（联动） | Table 1 三值化（met / not met / undefined），R1C s=0.8 格 undefined；C3 判定改配对 per-seed delta + 容差（建议 1 个优先级单位）。**注意自洽**：criteria 本体冻结不动，判读精化走 append-only amendment（第二次），正文双行呈现「原冻结判定 + refined reading」，与 R-06 时序披露一致。 |
| R-08 | 必修 | **已拍板修法 C（用户 2026-10-23）**：delivered 读数段连同 Fig 4 整体删除（R-33 一并解决）；formula-spec 冻结件不动；数字闸退役对应检查项。终审原推 A（改名保留）作废——发布会原则裁定该读数为不强化主线、已产出过一次被抓缺陷的负资产。 | |
| R-09 | 必修（勘误级） | 全文 saturation-avoidance time → synthetic aperture time（3 处）；`saturat` 残留 grep 清零；勿误伤 saturation arm（饱和臂）。 |
| R-10 | 必修（勘误级） | single-orbit → single-satellite（5 处）。 |
| R-20 + R-21 | 必修 | §2.1 L73「a result of this paper」降格为「a property of the registered model…」；§7.2 限定前置；§2.1 或 §5 披露 AASR 门槛在已发布 30 场景移除 0。 |
| R-30 | 必修（随 R-01 重写） | 摘要重写 ≤250 词（现 284–305），双向报告+scope 各留一句。 |

### 第二档：应改（P1，决定 AST 主刊上限）

| ID | 裁决 | 改法（终审版） |
|---|---|---|
| R-11 | 应改（披露型） | 报告 fallback 触发频率（可自既有 evaluator 重放统计，不需重跑求解）+ pad/settle 一行敏感性；PRF/AASR 阈值敏感性列 limitation（重生成成本高，不做的代价=标题可保持）。**连续化 hybrid 实现不做**（改生产路径=全量重跑）。 |
| R-12 | 应改 | **推荐删除**两个 Pearson r（无方向性声明、单点即塌、闸不覆盖三重理由）；若保留须族内+CI+「不可与零区分」明示。 |
| R-13 + R-29 | 应改 | 接入 liu2025a/shen2024multistrip/xin2024sar/li2026efficient + 三列对比表（duration 内生/外生、quality 定位、mode 固定/决策）；软化 near-universal（L79）。 |
| R-14 | 应改（正文层） | 正文明示「ten seeds = ten independent scenario draws, each solved once」；「nine views of one world」限定单 seed。3 solver-seed 子样本补算可缓——anchor 258/260 已把搜索噪声压到构造面之下，加一句论证即可。 |
| R-15 | 应改（5 分钟） | L236/L197 族规模改区间（46–50 / 99–100 / 窗 145–162/337–391/731–779）。 |
| R-17 | 应改（一词） | L54「coverage-optimal」→「attains the best-found coverage」；§4 已自称测量工具，无需压缩。 |
| R-18 | 应改 | 摘要每个 pp 数带配对统计量或区间；R2F 头条以配对中位 0.93pp 并报、或改报「2.36 against grid maximum; pairwise 0.93」。 |
| R-19 | 应改（一行） | v_s 取足迹速度时 dwell/覆盖偏移量级一行敏感性（与 R-11 敏感性合并做）。 |
| R-22 | 应改（一句） | §3.4 或摘要说明五约束族中真正绑定的只有 C2 与 STR 地板。 |
| R-32 | 应改 | Fig 3 caption 砍半；图注带收紧方向数字（46.6pp）；(b) 面板保留（dip 归因需要），不强制断轴。 |
| R-33 | 应改 | **推荐删 Fig 4**（三条平线零信息，与 R-08 修法 A 联动后平台能力句引正文常数即可）；省一页版面。 |

### 第三档：措辞与格式（随手清）

R-23（cloud-cover 删/改降雨电离层）、R-24（no intermediate regime 措辞）、R-25/26（class 加 authoryear 选项统一 harv，注意全文引用重排后复检）、R-27/28（bib 批量清洗：脚本先备份、被引 27 条逐条人核）、R-31（图 1 标签视觉验收时判）、R-34（Zenodo DOI，=台账 R42 待用户）、R-35（cover letter 单数）、R-36（\paragraph 尾句点批量去，PDF 15 处）。

### 第四档：用户拍板结果（2026-10-23 逐项确认完毕）

1. **标题**：✅ 已拍板 **K″**：*Resolution-Driven Dwells in SAR Task Scheduling: Mode Composition Decides What Tighter Requirements Cost*。标题弃用 order（消「阶次/顺序」歧义）；**扩展拍板：正文全文 order → requirement**（the order point → the as-placed point、ordered → required、product-order → product-requirement；保留 in order to / order of magnitude / demand-* 词族）；关键词第 5 项同步；正文首次出现处 order 与 requirement 挂钩。
2. **R-08 修法**：✅ 已拍板 **C**——delivered 读数段连同 Fig 4 整体删除（R-33 一并解决），formula-spec 冻结件不动，数字闸退役对应检查项。
3. **Fig 4 删否**：✅ 被第 2 项吸收（删）。
4. **Pearson（R-12）**：✅ 已拍板 **删**——整段「Its relation to coverage」删除。
5. **Zenodo DOI（R-34）**：✅ 已拍板 **upon acceptance**——§8 改「接收后 Zenodo 公开（含 DOI）+ 审稿期可向通讯作者索取」；真 DOI 与代码公开留到接收后（老债 R42 后置）。
6. **P1-8 固定 dwell 反事实**：✅ 已拍板 **接入**——L8 口径现算 3 族×10 seed=30 单元（重放式：dwell 冻结库值排班，按真实时长查 C2 违反率与覆盖差）；产出进摘要第一段支撑「fails in a quantifiable way」；10-17 的 v4 消融数据不混用。

## 执行顺序（建议 9 步，含拍板后更新）

1. 机械批：标题换 K″、SAT/single-orbit/\paragraph 句点/cover letter/bib 清洗/引用风格统一（一次 commit）。
2. **术语批（独立）**：正文全文 order → requirement（映射见表上方追加拍板项）；数字闸锚句同步更新；换词后先跑全绿基线。
3. 摘要+结论重写（双向报告、≤250 词、删 477,308、新术语）。
4. 带宽披露 + 判定三值化 + amendment（R-03/06/07/16）。
5. 模式分解表（脚本自 manifest+pilot artifacts 出数）+ §6.1/§6.3 机制段重写（R-04，最大头）。
6. §2.1 限定 + AASR 披露 + 约束绑定句（R-20/21/22）。
7. 反事实小节（P1-8，30 单元重放）+ 图（Fig 3 caption、Fig 4/delivered 段删除）+ 文献接入与对比表（R-13）。
8. 数字闸联动更新（退役 delivered/Pearson 旧锚、纳入新表/区间/反事实数字）+ pdflatex ×2 编译 0 error + 域套件双面回归（`PYTHONPATH=src python -m pytest src/tests/` + paper2 域套件，独占跑）。
9. 全文一致性 grep（`saturat`、`single-orbit`、`squint-loss`、裸 order 术语残留、双句点）+ verify_paper_numbers_l8 rc=0。

**执行票必带的补充裁决与禁令（2026-10-23 收工复盘补）**：
- **P1-7 贡献声明三选二显式裁决**：保留平台腿与纪律性贡献，主结果贡献降格为「模式依赖的订单敏感性」叙事（由 R-01 双向报告 + R-06 时序披露 + R-04 机制段重写组合兑现）；EA 选「测量工具」侧（§4 现状即此，仅 L54 一词改），不补预算梯。贡献列表 §1.2 重写时按此对齐。
- **审查报告附录 C 六条「不建议做」禁令**（roadmap 搬运时整节丢失，此处补回）：①不要重调 K1–K3 救 R2F；②不要删 R1C 不可行结果（改叙述为解析推论）；③路由实验不做前标题必须带固定模式分配限定语义（K″ 已含 mode composition 主张——修回信需说明「decides」为现象层概括、观察合法，分解表与三族共变为证）；④不要为保 EA 方法叙事而保留 SBX 细节叙事（按测量工具定位）；⑤不要把 registered/caliber 全局换同义词当修完 R-06（须时间线+pre-specified vs post hoc 清单）；⑥不要新增跨族 pooled 统计（R-12 删除后不回填）。

## 残余风险（终审自审）

- Table 1 判读精化与「criteria 不再编辑」自我纪律的表面冲突——已用第二次 amendment + 双行呈现化解，但正文行文必须把「判定未动、判读精化」写死，否则给审稿人留新靶。
- R-04 新表数字若不进数字闸，就是下一轮「闸外数」事故的种子。
- bib 批量清洗触碰 307 条——先备份 + 被引条目逐条人核，防 Scholar 残留清进正文引用。
- 引用风格切 authoryear 后全文引用重排，须重编译复检（\citealt 在 harv 下正常）。

*终审未修改稿件任何文件；本报告所有复算命令与中间量可重跑。*
