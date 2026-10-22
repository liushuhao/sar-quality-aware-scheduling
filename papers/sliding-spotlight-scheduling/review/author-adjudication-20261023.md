# Author Adjudication — 2026-10-22 独立外审

**Binds**: `revision-roadmap-20261023.md`（immutable core，36 项发现 R-01…R-36，含主线程独立复算核验证据）。
**Rule**: 每条恰一个选择。`will_address` = 修 + 精确目标；`wont_address` = 理由、不动工；`not_on_point` = 理由、不动工。**禁默认值、禁从严重度/核验结论推导裁决。**

## Status: **ADJUDICATED — 2026-10-23 按终审报告 + 用户六项拍板固化**

> 裁决来源：`terminal-review-20261023.md`（ZCode 第三席终审，36 项 0 项不成立，四档裁决）+ 用户 2026-10-23 逐项拍板六项（标题 K″/R-08 选 C/Pearson 删/数据公开 upon acceptance/P1-8 接入/正文 order→requirement 全文替换）。36 项全部 `will_address`，无 wont / not_on_point。

## 裁决表

| ID | 核验 | 简述 | Choice | Reason / Targets |
|----|------|------|--------|------------------|
| R-01 | ✅ | 头条 4.15/2.36 是放松方向差，标题称收紧代价（正文 §6.1 方向正确） | will_address | 终审必修档：摘要/§6.2/结论双向报告（收紧 26.0/46.6/46.0pp 进摘要）；随 R-30 摘要重写一并做 |
| R-02 | ✅ | 「own saturation」= 网格 argmax；R1C 饱和=订单点代价恒 0 | will_address | 必修档：随 R-01 披露饱和点网格依赖与 premium 性质 |
| R-03 | ✅ | R1C s=0.8 不可行是 [2.5,3.0]×0.8<2.4669 算术必然；带宽正文 0 披露 | will_address | 必修档：§5.1 披露带宽+地板；s=0.8 改一行解析结论；该格判定改 undefined |
| R-04 | ✅ | 三族混杂；R3H 收紧损失 77–96% 由 STR 地板排除解释 | will_address | 必修档（工作量最大）：模式分解表（数字进数字闸）+ §6.1/§6.3 机制段重写；>70% 条款随标题改判 K″ 兑现 |
| R-05 | ✅ | C5 无违反 + 477,308 是构造性/成员级计数（distinct 13,845），对 STR 不成立 | will_address | 必修档：摘要/结论删「477,308+无违反」；正文加 distinct 对照；C5 改 per-mode delivery rule |
| R-06 | ✅ | 头条量随 2026-10-21 amendment 登记，晚于 2026-10-20 数据 | will_address | 必修档：§3.5 补时序一句（headline 属 post hoc descriptive） |
| R-07 | ✅ | Table 1 R1C C3「met」自认依赖「infeasible 记作零覆盖」约定 | will_address | 必修档：Table 1 三值化（met/not met/undefined）；判读精化走第二次 amendment，与 R-16 联动 |
| R-08 | 🟡 | f_Q,deliv 式与注册口径自洽（非印错）；真缺陷=「squint-loss」命名方向反 | will_address | **用户拍板 C**：删 delivered 读数段 + Fig 4；数字闸退役对应检查项；formula-spec 不动 |
| R-09 | ✅ | SAT 展开错误（Kim = synthetic aperture time） | will_address | 必修档（勘误级）：全文改 synthetic aperture time；`saturat` grep 清零；勿伤 saturation arm |
| R-10 | ✅ | 「single-orbit」事实错误（R1C 跨 3 天/≈45 圈） | will_address | 必修档（勘误级）：5 处改 single-satellite |
| R-11 | ✅ | 机动 hybrid 不连续（0.46 s→4.07 s 跳变）；无 fallback 频率/敏感性 | will_address | 应改档（披露型）：报 fallback 频率 + pad/settle 一行敏感性；PRF/AASR 列 limitation；不改生产实现 |
| R-12 | ✅ | 两 Pearson r 脆弱（单点/聚合即塌）；闸不覆盖 | will_address | **用户拍板删**：整段「Its relation to coverage」删除；闸本不覆盖，无退役项 |
| R-13 | ✅ | 最近 4 篇 SAR 区域观测在 bib 内、引用 0 | will_address | 应改档：§2 接入四篇 + 三列对比表；软化 near-universal |
| R-14 | ✅ | 场景种子=求解器种子；「10 seed=10 场景非 10 次重复」 | will_address | 应改档（正文层）：明示 seed=场景抽样 + one-world 限定单 seed；3 solver-seed 补算缓（anchor 258/260 已压搜索噪声） |
| R-15 | ✅ | 「46/99/342/753」是单 seed 取值 | will_address | 应改档：族规模改区间（46–50/99–100/窗 145–162 等） |
| R-16 | ✅ | K1–K3 无容差；R2F 两次下降<一个优先级单位 | will_address | 必修档：配对 per-seed delta + 容差（1 优先级单位）；与 R-07 同一 amendment |
| R-17 | ✅ | EA 贡献被自数据否定（anchor 258/260） | will_address | 应改档（一词）：L54 coverage-optimal → attains the best-found coverage；§4 结构不动 |
| R-18 | ✅ | R2F 2.36pp 配对中位仅 0.93pp、CI 重叠；R3H 4.15pp 稳健 | will_address | 应改档：摘要 pp 数带配对统计量；R2F 并报 pairwise 0.93 |
| R-19 | 🟡 | 7578.05 是惯性速度（已披露）；真缺口=无敏感性 | will_address | 应改档：一行敏感性（与 R-11 合并做） |
| R-20 | ✅ | AASR 门槛从未绑定（30 manifest removals aasr=0） | will_address | 必修档：§2.1/§5 披露移除 0 |
| R-21 | ✅ | §2.1「a result of this paper」vs §7.2 自认不构成反驳 | will_address | 必修档：§2.1 限定语降格 + §7.2 限定前置 |
| R-22 | ✅ | 五约束族真正绑定的只有 C2 与 STR 地板 | will_address | 应改档：一句披露绑定状态 |
| R-23 | ✅ | 「cloud-cover attrition」对 X 波段 SAR 是范畴错误 | will_address | 措辞批：删/改 SAR 相关环境项 |
| R-24 | 🟡 | 「no intermediate regime」与同句 0.5398 字面矛盾 | will_address | 措辞批：改「无连续中间机制」义 |
| R-25 | ✅ | class(numeric) 与 elsarticle-harv 冲突 | will_address | 格式批：class 加 authoryear；重编译复检全文引用 |
| R-26 | ✅ | `\citealt` 打出完整作者串 | will_address | 格式批：随 R-25 转 harv 后复检 |
| R-27 | ✅ | 307/307 author 字段双括号 | will_address | 格式批：脚本清洗，先备份、被引 27 条逐条人核 |
| R-28 | ✅ | 147/275 journal 字段含 Scholar 残留 | will_address | 格式批：与 R-27 同一脚本批 |
| R-29 | ✅ | 280/307 bib 条目未被引用 | will_address | 与 R-13 合并：保留将引条目，清洗覆盖将引集 |
| R-30 | ✅ | 摘要 305 词 > 250 上限 | will_address | 必修档：随 R-01 重写 ≤250 词（新术语 requirement 已入） |
| R-31 | ⓘ | 图 1 标签用 `\footnotesize`（非「6 pt」） | will_address | 视觉验收时判读实际渲染尺寸，必要时 ≥8pt |
| R-32 | ✅ | 图 3 caption ~200 词；y 轴缩放放大噪声且排除 R3H | will_address | 应改档：caption 砍半 + 图注带 46.6pp；(b) 保留（dip 归因需要） |
| R-33 | ✅ | 图 4 三条平线是构造必然 | will_address | **随 R-08 删除**（用户拍板 C 吸收） |
| R-34 | ✅ | Data availability「from the corresponding author」 | will_address | **用户拍板 upon acceptance**：改「接收后 Zenodo 公开（含 DOI）+ 审稿期可索取」；真 DOI 接收后与代码公开一并做（老债 R42 后置） |
| R-35 | ✅ | cover letter「All authors approve」（单作者） | will_address | 格式批：改单数 |
| R-36 | ✅ | run-in heading 双句点（15 处） | will_address | 格式批：去 `\paragraph` 尾句点 |

**追加拍板项（用户 2026-10-23）**：正文全文术语替换 order → requirement（the order point → the as-placed point；ordered → required；product-order → product-requirement；保留 in order to / order of magnitude / demand-* 词族）；数字闸锚句同步更新；替换独立成批先行。

## 汇总（裁决后填）

- will_address: 36 项
- wont_address: 0 项
- not_on_point: 0 项

## 执行记录（修复后填）

- 修复 commits：
- 编译验证（pdflatex ×2，0 error / 0 undefined）：
- 数字闸 `verify_paper_numbers_l8.py --paper main.tex`：
- 受影响数字是否需重跑实验（本批预期：全部为再分析+重写，除 R-11/R-14 可能需小量补算、R-18 为统计口径改法）：
