# paper2 票 50 前 TRAE 四轴审查报告 — ZCode 对账核验

**作者**: zcode（GLM，经 ZCode 主线程）
**日期**: 2026-10-20
**对象**: [`paper2-ticket50-four-axis-audit-20261020-trae.md`](paper2-ticket50-four-axis-audit-20261020-trae.md)（TRAE 异源审查报告，判定 Conditional Go，列阻断项 B1–B5 + 高优先项 N1–N8）
**性质**: 只读对账；未改动任何源码、论文、数据、注册文件
**方法**: TRAE 报告全部承重断言逐条对照仓内实况独立复算——代码读源、数据重算、正文逐行比对、公式源注册条款对读。

---

## 0. 结论摘要

TRAE 报告**事实层全部属实**：约 20 项承重断言复算无一证伪（§1）。「Conditional Go」方向正确。但 5 个阻断项中 2 项（B1/B2）**不是未决事项**——票 49 blocking gate（formula-spec v1.9 §8.17，2026-10-20 同日落盘）已对其做出注册裁决（§2）；其余 3 项（B3/B4/B5）与 N1–N8 均为票 50 自身的验收内容。因此：

- **票 50 之前不存在需要单独闭环的前置工作**；
- 真正待用户拍板的只有一项：**是否开 L9 重跑票**（TRAE 方案 A）。ZCode 推荐不开（§3）；
- 证伪条件：导师/审稿人要求「覆盖率 vs 分辨率需求」为不限定冻结映射的一般权衡命题，则开 L9。

## 1. 核验覆盖与结果总表

### 1.1 代码轴（全部证实）

| TRAE 断言 | 复算 | 证据 |
|---|---|---|
| `f_q` 用库零斜视常数，未接交付分辨率 | ✓ | `sss_core/quality.py:140` `rho_a = lib.rho_az(mode)` |
| 求解器 `n_obj=1`、`f_q` 仅描述性读数不进选择压力 | ✓ | `sss_core/nsga2.py:72-90`（docstring 自述「degenerates to an elitist GA」） |
| `search_only` 只收集严格低于锚点的成员 → 恒 None，「搜索赢/平」不可区分 | ✓ | `sss_core/nsga2.py:315-317` |
| 扫描只缩放 `rho_req_m`、不重路由模式 | ✓ | `scripts/run_pilot.py:76-89`（注释原文「scale the ORDER, never the population」） |
| 交付恒等式容差 1e-12（SLS/SPT） | ✓ | `sss_core/duration.py:222-274` |
| `verify_paper_numbers.py` 钉死 v3_results | ✓ | `scripts/verify_paper_numbers.py:52` |
| `build_sweep_results.py` 硬编码 V4/scenarios | ✓ | `scripts/build_sweep_results.py:62-64` |
| 红闸无双目标禁语（0 violation 下 11 处旧叙事全放行） | ✓ | `scripts/check_red_lines.py` 全文 grep「second objective/bi-objective/dual-objective/two objectives/independent objective」零命中 |
| `_NOPRIOR_LEGAL_RX` 唯一英文豁免句式 = main.tex:89 句 | ✓ | `scripts/check_red_lines.py:284-290` |
| W9 豁免词 `degenerate by construction`（单目标下语义反转） | ✓ | `scripts/check_red_lines.py:768-775` |
| `EMPTY_SELECTION_FQ_PLACEHOLDER = 1.0` | ✓ | `sss_core/evaluator.py:80,446` |
| 验证链/图 3–7 钉旧世界 | ✓ | `plot_fig3_quality_vs_squint / fig4_budget_ladder / fig5_promotion_two_axis / fig6_per_mode_decomposition / fig7_power_curve`、`verify_v3_verdicts.py`、`verify_prereg_v2.py`、`check_coverage_parity.py`、`run_verify.py` 均在且指向 v3 系 |

### 1.2 数据轴（逐位复现）

| TRAE 断言 | 复算 | 方法 |
|---|---|---|
| 260 工件 + 10 exit 11（R1C s=0.8 十种子） | ✓ | glob 遍历 + `sweep_results.json` exit_codes |
| 决策全部 `vacuous_single_objective` | ✓ | 同上，260/260 |
| 全部 260 前沿 unique f1 = 1（tie set，f_q 无选择压力） | ✓ | 同上 |
| 前沿大小分布 40×233、2×11、1×9、5×2、26/4/12/17/10 各 1 | ✓ | 同上 |
| L8 覆盖率中位 27 值全表 | ✓ | `experiments/v5_results/sweep_results.json` |
| R2F s=0.8 与 s=1.0 中位逐位相同（0.9764210609534351） | ✓ | 同上 |
| 族模式构成：R1C 20 STR（ρ 2.522–2.961 m）；R2F 46 = 16 SLS + 30 SPT 无 STR；R3H 99 = 54 STR + 15 SLS + 30 SPT | ✓ | `experiments/v5_results/scenarios/*.json` |
| STR 地板 2.4669 m | ✓ | `ModeLibrary.from_fixture().rho_az(STR)` = 2.466901617924378 |
| 紧臂机制表（越界份额 vs 覆盖跌幅） | ✓ | 独立复算：R1C s=0.8 份额 1.0000/跌幅 1.0000；R1C s=0.9 0.4701/0.4602；R3H s=0.8 0.5268/0.4658；R3H s=0.9 0.2551/0.2601——与 TRAE 表逐位一致 |
| 锚点最优性 258/260；搜索仅 2 单元胜出、最大增益 +0.0463 | ✓ | 遍历 260 工件 front_max vs anchor_f1_star |
| 质量兑现率中位表 | ✓ | `sweep_results.json` f_q_fulfillment_ratio_median |

### 1.3 正文轴

17 处 `paper/main.tex` 引用：14 处逐字命中所引行号；3 处为 LaTeX 标记差异（`$k$` 数学定界符、`\emph{calibrated}`、`3.9722` 行号漂移 ±2），实质内容全部属实。含旧世界主结果 `dq_all` mean 66.872、t=24.78（L248）、摘要内 90 单元/3 预算档叙事（L29）。

## 2. 两处对账更正（TRAE 报告相对仓内真实状态的滞后）

### 更正 1：B1 非未决决策 —— formula-spec v1.9 §8.17-9 已裁决

TRAE 要求「票 50 第一件事由用户拍板 A/B（A=重跑重路由并注册 L9；B=冻结映射语义重述）」。实际：票 49 blocking gate 已注册（`formulas/formula-spec.md` §8.17-9）：

> 既有族（含票 49 re-run）**沿用场景冻结的模式分配**（grandfather——重切混合比会破坏与票 48 曲线的可比性，如需重切须另票另跑）；注册的**选择政策**供论文叙事与未来族生成 = 可行集判据 + 场景尺寸二键 + 粗端唯 STR。

即 **TRAE 的方案 B 已是注册裁决**；方案 A（重跑 = L9）是公式源显式留给另票的可选项。B1 剩余有效部分 = 票 50 写作义务：把冻结映射语义、STR 地板阶跃性质、机制分解写进方法与图注——本就属票 50 正文改写范围。

（附注：TRAE 反事实细节「s=0.8 时 R1C 20/20 应重路由为 SLS」在 §8.17-9 二键政策下足印内任务应选 SPT——方向正确（非 STR），细节不精确，不影响结论。）

### 更正 2：B2 非未决冲突 —— §8.17-10 已裁决

§8.17-10 原文：

> **f_Q 口径**：优化器与聚合**保持库口径**（§8.9-6 不变，既有族逐位）。新增**描述性变体**（只读数、不进目标、**实现归票 50 取数面**）：$f_{Q,\text{deliv}}=D/(2\rho_{req}^2\cos^2\psi_{\text{sel}}\,\rho_{rg})$……引用须带口径标签，两口径不可混比。

TRAE 建议 2（实现 `f_Q_deliv` 并量化两口径差）正是该已注册义务的执行；§6.4 模式常数叙事（0.8107/19.7352/54.8322）删除是票 50 改写本身。故 B2 降格为票 50 取数面义务，非票前阻断。

## 3. 修正后的票前图景与施工顺序

- **B1/B2**：已有公式源裁决锚，无需再决策。
- **B3**（红闸补双目标禁语 + 退役 `_NOPRIOR_LEGAL_RX` 英文豁免 + 重写 W9 豁免 + 扩展 W13 口径标签）、**B4**（验证链与图 3–7 重指 L8 或显式退役并登记）、**B5**（预注册 append-only amendment：显式 vacate `dq_all`/P1/P2/P3/promotion，注册 L8 主结果与兑现率定义）、**N1–N8**：全部并入票 50 验收。
- 施工顺序建议（修正 TRAE §7）：**票 50 第一施工步 = 红闸禁语补丁**（先立禁语再改正文，防改写期旧叙事回流；本项目 2026-10-11 有 writing-bans 门禁盲区先例）→ 正文改写（含 R2F 证伪如实报告 + 锚点已最优/搜索无覆盖增益的叙事重写）→ 取数面 `f_Q_deliv` 与兑现率口径标注 → 验证链重指/退役与预注册 amendment 随改写收口。

## 4. 与 TRAE 的推荐分歧：L9 重跑（方案 A）

- **TRAE**（§7-1）：建议 A（重跑）若时间允许。
- **ZCode 推荐**：不开 L9，按 §8.17-9 冻结口径撰写票 50。理由：① 冻结口径命题自洽且机制分解已定量验证（份额-跌幅 0.5–2pp 吻合），是可发表的完整命题，只需如实限定为「固定模式分配下的订单敏感性」；② 项目复盘最大结构教训「写作期在裁决未定前铺开」（`review/retro-project-20261020.md`），重跑将再拖一轮定位改写；③ 公式源明确「另票另跑」，后补路径畅通；④ 成对设计下 L9 与 L8 之差恰为重排收益，后补不损失科学价值。
- **证伪条件**：导师/审稿人明确要求一般权衡命题（非冻结映射敏感性）→ 开 L9。

## 5. 待用户拍板

1. L9 重跑票开不开（ZCode 推荐：不开）。
2. 本对账文件与 TRAE 报告的入库处置（review/ 现行追踪位；当前两者均未提交）。

## 6. 附：核验命令（可复跑）

```bash
cd papers/sliding-spotlight-scheduling
python -c "import json;d=json.load(open('experiments/v5_results/sweep_results.json'));print({f:{s:v['coverage_median'] for s,v in d['families'][f].items()} for f in d['families']})"
python -c "import json,glob,collections;a=[json.load(open(f)) for f in glob.glob('experiments/v5_results/sweep/s*/pilot_*.json')];print(len(a),collections.Counter(x['promotion']['decision'] for x in a),sum(1 for x in a if len({r['f1_star'] for r in x['front']})==1))"
python -c "import json,collections;m=json.load(open('experiments/v5_results/scenarios/R3H_seed300.json'));print(collections.Counter(t['mode'] for t in m['tasks']))"
grep -c "second objective\|bi-objective\|dual-objective" scripts/check_red_lines.py  # 期望 0
```

## 7. 异源终裁合并（2026-10-20 同日增补）

终裁人：claude code CLI（异源，cc-switch 路由 deepseek-v4.1-flash，只读工具面，后台任务 exec_260fa993，exit 0）。简报与裁决全文：`.scratch/sliding-spotlight-scheduling/t50/adjudication-brief-20261020.md`、`adjudication-verdict-20261020-claude.md`。裁决按惯例经本线程对抗核验后并入。

### 7.1 终裁结论（四点全决）

1. **争议 1（B1）：ZCode 胜**——B1 已由 §8.17-9 + 票 48 第 7 条 P0 更正 + t48 终审记录三重注册为「冻结模式分配臂」措辞义务，剩余为写作义务而非待拍板决策。
2. **争议 2（B2）：ZCode 胜**——§8.17-10 已注册「库口径保留 + `f_Q_deliv` 实现归票 50 取数面」；TRAE 定为改写前闸门属状态误判。
3. **争议 3（L9）：有条件方案**——默认不开（ZCode 立场采纳），命中触发条件才开（标题/摘要无法回避冻结映射限定、导师/审稿人要求一般权衡命题、平台级结论须进正文）；开则按配对实验登记 L9−L8 = 重路由收益。**此为终裁给用户的触发规则，待用户追认。**
4. **争议 4（票前前置）：无需单独闭环，全部并入票 50**——但「并入」须先补票面（见 7.3）。

### 7.2 终裁承重断言的核验记录（本线程复算）

已证实：票 50 票面存在（`.scratch/.../issues/50-paper-positioning-single-axis.md`，Status: ready-for-agent，Tier T0）且验收清单确无 B1/B2/B4 条目、`Blocked by: 48` 确漏 49；票 48:17 P0「冻结模式分配臂」措辞义务原文属实；`review2/t48-claude-track2-full.md:19`「重路由臂」原文属实；`RUN_LINEAGE.md` L7/L8 行引文属实（含 launcher rc=0 elapsed 4470s）；`retro-project-20261020.md:96/:101` 引文属实；`aasr.py:178-189` `route_mode` 确为最粗充分路由（ρ=2.0 → SLS），与 §8.17-9 二键政策、L8 实际 grandfather 构成**三条不同规则**；`build_sweep_results.py:75-88` 兑现率确为**库口径 f_q、对 tie-set 全体成员取均值**（非锚点方案读数）；`verify_paper_numbers.py` 确只有 `--paper` 参数（对 L8 恒绿而非 FAIL）；R1C 十种子 ρ 范围 2.5049–2.9999 属实（0.8×max=2.3999 < 2.4669，结论保持）；`duration.py:216-219` 对 STR 传任务级参数直接 raise 属实（f_Q_deliv 对 STR 无定义的代码根据）。

两处计数/引用出入（不影响结论）：① `_NOPRIOR` 许可句式按「coupling loop as a first-class constraint」短语计为 4 文件 **6 处**（终裁记 5 处）；② 终裁证伪条件中「现有 23/23 负相关」**未被复现**（见 7.4）。

### 7.3 终裁对双方的错误清单——ZCode 方接受项

终裁列 ZCode 六条，全部接受：①「约 20 项复算无一证伪」措辞过强（正文引文 3 处标记差异 + TRAE 反事实细节 SLS→SPT 更正均属被修正是实）；② B1 证据链不全——除 §8.17-9 外，直接依据是票 48:17 与 t48 终审记录（§2 更正 1 应引三重来源）；③ 「全部并入票 50 验收」在票面无落点，可执行性缺口（终裁已把「补票面 4 条」列为开工第一步，见 7.5）；④ 「份额-跌幅 0.5–2pp 吻合」丢了基线未服务修正——R3H s=0.8 原始差 6.1pp，扣基线未服务 5.15pp 后约 1pp（TRAE 原文同病）；⑤ `f_Q_deliv` 公式对 STR 无定义域未披露（STR 交付=库地板 2.4669 m，非 ρ_req；任务级参数对 STR 直接 raise）；⑥ 以复盘教训支撑不开 L9 强度夸大——该教训对象是「主结果形态未定」，单轴形态已定案，L9 争的是适用范围（方向不变、强度修正）。

### 7.4 ZCode 在终裁之外的新发现（三级复算，超出 TRAE 与终裁）

**票 50 票面「覆盖越高、兑现越低」方向断言在 L8 数据不可复现**（票面 What-to-build 句；终裁证伪条件中「23/23 负相关」同源、同被证伪）。实测：26 个族-s 点合并 Pearson r = **+0.33**；260 个单元合并 r = **+0.25**（R1C +0.49 / R2F +0.01 / R3H +0.15，全为非负）；组内 10 种子 20 组 = 13 负 7 正混合。「负相关」印象唯一来源是跨族比较——而 R 族 f_q 未归一化、跨族禁混是项目注册口径。**处置建议**：票面该括注删除或改「与覆盖的关系读数待测」（票面验收项已有中性表述「同时给出它与覆盖的关系读数」，删括注即可，零成本）。

### 7.5 修正后的票 50 开工序列（终裁版，取代 §3 顺序建议）

1. **补票面**（动正文前）：验收清单补 4 条——B1 冻结臂语义 + STR 地板阶跃披露 + §3.4 路由句与数据来源一致性（三规则分叉必须写明）；B2 `f_Q_deliv` 实现或全量库口径标签 + tie-set 均值声明 + STR 定义域披露；B4 L8 验证器（参数化或新建）+ Fig 3–7 逐件处置；B5 amendment 含「注册 L8 主结果与兑现率定义」而非仅 vacate。`Blocked by` 补 49。删除「覆盖越高、兑现越低」括注（7.4）。
2. **第一施工步 = 红闸禁语补丁**：双目标禁语、`_NOPRIOR_LEGAL_RX` 4 文件 6 处同步退役/替换、W9 豁免重写、W13 扩展口径标签；先立禁语再改正文。
3. 正文改写（含 R2F 证伪如实报告、锚点已最优/搜索无覆盖增益叙事）。
4. 取数面 `f_Q_deliv` 与兑现率重算/标注；验证链重指与预注册 amendment 随改写收口。

### 7.6 待用户拍板（更新）

1. L9 触发规则追认（7.1 第 3 条；ZCode 与终裁一致推荐默认不开）。
2. 本文件、TRAE 报告、终裁记录（.scratch 不入 git）的入库处置。
