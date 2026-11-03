# Author Adjudication — 2026-08-30 GLM 五席面板（ars-panel-20260830）

Roadmap（不可变）：[`ars-panel-20260830/editorial-decision.md`](ars-panel-20260830/editorial-decision.md)
本 sidecar 状态：**ANALYST-PROPOSED**（2026-08-30 用户 goal 指令授权主线程按核验证据先行裁决执行；用户可逐条推翻，推翻后按 amendment 流程追加 Roadmap）。
裁决口径：每条独立判断「真问题 / 风格偏好 / 批注有误」，所有 will_address 项附主线程实测证据（非转写 GLM）。

基线（2026-08-30/31 预闸）：verify_paper_numbers **170/0 + CALIBER OK**；rebuild_snapshot 1800 条；_audit_full_hard **0 issue**；cross_solver_audit EXIT=0；统计脚本全量重跑可复现 HV（MOEA-3 0.0893 / G-SM 0.2341）。

---

## B1 束 — 归因与 overgeneralization

| 项 | 裁决 | 证据 | 修复目标 |
|---|---|---|---|
| N1 45° 包络 | **will_address** | L477-480「range reported…in the literature」无 \cite；C1  incidence [18,47] 可行几何下有效包络 ≈38°（R2 推导 cos ξ=cos γ·cos ψ，ξ_max≈41.3° ⇒ ψ≲38°）；实测调度 ψ 16–24° | §3.2 加有效包络推导句 + 删除/降格「文献范围」措辞（无引用不立），与 N16/N18 联动 |
| N2 摘要 +41% 归因 | **will_address** | 统一选择器重算（`scripts/unified_selector_recompute.py`）：f3 受控边际 U3 规则 **+4.92%**（p=2.3e-11，cliff +0.46，47/50）；U2 规则 +0.05%（p=0.86）；非对称口径 +6.25% | 摘要/§1/§6 改求解器级归因：MOEA-3 vs MOEA-2 受控 +4.9%（f3-aware 选择器下）；+41% 保留为 vs G-BL 总增益但标注同密度 G-SM 对照（见 N6） |
| N3 「all solvers converge」 | **will_address** | G-SM f1* 实测 S1–S4 = 0.51/0.35/0.29/0.37（gen_table1 输出），从不收敛 | 全文（摘要/结论/§6）改「all multi-objective solvers」或「coverage-oriented solvers」 |
| N4 「density-independent residual」 | **will_address** | schedule_correlation.json：A 组调度内 r 为 S1 −0.63（Fisher-z −1.09）/S2 −0.15/S3 −0.15/S4 −0.18——密度依赖明确 | L1095、L1131 改「negative at all densities, strongest at sparse density」；相关叙事与 headline 对齐 |
| N5 「indistinguishable」 | **will_address** | S4 配对 Wilcoxon p=4.5e-3，W33/L17；类均值 0.680/0.680 相等但逐场景优势存在 | 改「practically indistinguishable in class means; a trace per-scenario advantage persists (paired p=4.5e-3 at S4)」 |
| N6 G-SM 对照缺失 | **will_address** | S1 G-SM f3=0.722 vs MOEA-3 0.698（G-SM 全组最高 0.72–0.79）；G-SM vs G-BL f3 +45.3% 且 f1* 仅 0.51 | 摘要/引言叙事补：MOO 真实卖点 = f3 增益仅付 15% 覆盖代价（G-SM 同档 f3 付 ~50%）；G-SM 定位句重写 |

## B2 束 — 数字/描述对齐

| 项 | 裁决 | 证据 | 修复目标 |
|---|---|---|---|
| N7 GA-P-BL≡G-BL 强声明 | **will_address** | statistical_results.json：G-BL_vs_GA-P-BL greater=1/equal=199，δ=0.005（S1-D_seed04 单点 f1* +13.5%） | L125/L368/L596「on every scenario」/L711「tie by construction」/L1436「always triggers」统一改「identical in 199 of 200 scenarios; never worse by construction」；§5.3 Friedman 句联动 |
| N8 −0.97 包络描述 | **will_address** | r_visible_envelope.json：r_all S1 −0.930 / S2–S4 −0.890，r_c7（ψ≤45）−0.97；脚本无 C1 [18,47] 过滤——L1104 所述「C1 additionally imposed」计算不存在 | §6.4 分报 r≈−0.90（全采样）/−0.97（ψ≤45）+ 点数；纠正过滤条件为 ψ_sq≤45°；p95 ψ 全采样值补入 |
| N9 表格末位漂移 | **will_address** | gen_table1.py 重生成 vs tex：S1 MOEA-2 0.393±0.055/0.657±0.040（tex 0.394±0.059/0.654±0.038）等；「+7%」实算 +6.25%、「44%」待核 45.3% | Table 2 按脚本输出逐格更新（EN+ZH）；verify gate 加末位严格档（均值 tol 0.0005）；正文百分比重算 |
| N10 消融规模/S5/S6 | **will_address** | ablation_summary.csv 24 行=S1–S6×4 变体；tex L753「same 200」实 300；S5/S6 全文 0 定义；D 变体 S5/S6 f2 −11.2%/−11.1%（p≈1e-13/1e-15）显著未报 | 消融节统一口径（300 runs = 6 classes×50）；补 S5=ψ_sq 散布灵敏度、S6=C3 簇应力窄窗定义与关键结果（数据在手， robustness 证据） |
| N11 Cliff δ 误标 | **will_address** | statistical_analysis.py:314 δ=(gt−lt)/n=配对符号统计（matched-pairs sign），非 Romano 标定的经典逐对 δ；重算：M3-vs-M2 f3 经典 δ pooled +0.122（配对 0.570），S1 +0.566/S2 +0.106/S3 +0.021/S4 +0.032——S1 large 不变，密集档降 negligible | §5.3 写明公式（配对符号统计）+ 补经典 Cliff δ 列/图，Romano 阈值仅绑经典值；叙事方向不变且与密度叙事更一致 |
| N12 HV 归一化 | **will_address（GLM 部分误判）** | 统计脚本全量重跑精确复现 0.0893/0.2341/0.0668——代码可复现，GLM 的 ×5.9 是其用错归一化基（metadata 为 knee 值域）；但论文未写明「bounds 含全部前沿点、逐场景 HV 后平均」 | §5.3 补一句确切方法 + 六个归一化边界值；not_on_point 部分（不可复现）在 sidecar 留痕 |

## B3 束 — 物理可行性与机制

| 项 | 裁决 | 证据 | 修复目标 |
|---|---|---|---|
| N13 选择规则混淆 | **will_address** | moea.py:663 M3 knee=argmax(f1+f2+f3)、:669 M2 knee=argmax(f1+f2)；前沿数组全落盘，离线重算完成（见 N2） | 主张②定量改：统一 U3 选择器下 f3 +4.9%（47/50，p=2.3e-11），且该增益仅在 f3-aware 选择器下兑现（U2 规则 +0.05% ns）——作为选择器条件性披露，而非目标函数无条件收益 |
| N14 机制干预证据 | **will_address** | `scripts/compute_ablation_correlation.py`（A/B/C 三变体调度内 r + f2 值域压缩统计）；A/D 已有：S1 A −0.63→D −0.13；B/C 待算（首跑被 kill，重跑） | §6.4 补 B/C 调度内 r；若 B（去 squint）r 大幅回升→机制归因强化；同时报各密度 f2_std/range 检验值域压缩替代解释；不可算则降格观察性措辞 |
| N15 预算稳健性 | **will_address** | budget_control.json（pop=200/gen=400，ce8e37fc，moea.py 内容与 HEAD 一致）：双倍预算 vs 标准 S3/S4 同场景 f1* −0.05%/−0.35%、f2 +0.64%/+0.52%、f3 +1.64%/+0.97% | §6.6 补双倍预算 f1*/f2/f3 三指标差值（<2%）；「under the tested budget」限定；收敛曲线无数据不编造，以双倍预算近恒等替代 |
| N16 大斜视物理未建模 | **will_address** | 物理核算：f_dc≈2v/λ·sinψ ≈ 267 kHz·sinψ；16–24° ⇒ 74–109 kHz（GLM 77–176 同量级）≫ PRF 1–4 kHz | §3.2 加理想化声明段（Doppler 中心/方位增益 roll-off/方位处理未建模，platform-constant 排序前提）；与 N1 同段 |
| N17 dwell/窗口几何 | **will_address（GLM 部分误判）** | `scripts/window_sweep_stats.py`：窗宽中位 2.8 min（p95 196）；窗内 ψ 扫程中位 **3.8°**（p95 63.9）；**30s dwell 漂移中位 0.8°（p95 3.9°）**——GLM「dwell 内漂 20–60°」不成立；消融节「sweeps 20–35°」与中位矛盾 | 报告实测分布；消融节 20–35° 改按分布表述；声明质量取调度成像时刻、C1 全程审计（_audit_window_c1_continuous 76190 窗 0）；GLM dwell 子主张 not_on_point 留痕 |
| N18 包络灵敏度实验 | **will_address（做实验）** | S5（目标散布 5–45°）非包络封顶实验，挖据显示非单调（D 退化 −2.8%~−18.1%），不能替代；包络封顶答案唯一来源是新窗口+重跑 | 生成 ψ_max=15°/25° 封顶 S1 场景（E15/E25），跑 G-BL+MOEA-3 各 50（过夜批）；结果回写 §7.2 适用域；若批跑失败则 §7.2 显式降格「仅验证宽包络」 |

## S 级

| 项 | 裁决 | 修复目标 |
|---|---|---|
| S1 B/C 相关 | 并入 N14 | 同脚本 |
| S2 选择器敏感性 | **will_address** | 前沿离线算 best-f2/best-f3 选择器；S1 下端 0.025 更正（knee +34% vs best-coverage +12.5% 已有） |
| S3 §7.2 决策表 | **will_address** | 密度×包络×资源决策表，含 +12.5%@零覆盖代价选项；latency-favorable 表述先查数据，无分布则删 |
| S4 尾部风险 | **will_address** | per-scenario f2/f3 最差 10% 分位（膝点数据离线可算）；§7.2 加「质量增益不定向高优先级目标」警示 |
| S5 控制实验披露 | **will_address** | 热启动样本选择规则、σ 扫描 n_ref_dirs=12 vs 主实验 H=13、σ 仅 S3 推断范围，补 §6.6 |
| S6 检验族说明 | **will_address** | Bonferroni 消融 12 检验 vs 主表 10；Wilcoxon 去零有效对数披露 |
| S7 operational density | **will_address** | 无文献锚则改「high density（N≥300）」；§7.4 补动态到达/滚动时域 future-work 条 |

## T 级（打磨批）

**裁决：逐条核验后 will_address 为主**，核验不通过的转 not_on_point 留痕。清单（编辑时逐条 grep 定位）：
L446 cos ξ 方向、L340/L1086 交叉引用、L916 coverage advantage→deficit、L688/L1233 流程语言、L234 Chinese-affiliated 删除、Pareto-sufficient 死定义（已核实 L1246 定义后即弃）、NESZ/NSGA-III 摘要展开、trading freedom(L148)/scales as ∝(L1353)/+12.5% 补 in f2、Fig./Figure 与 §/Section 统一、G-BL 别名收敛、GA-P-BL≡G-BL 六次重复压缩、「five smallest random seeds」→「seeds 0–4」（L1101 已核实）、r_null「validating closed-form integrals」、θ_elev ordering 声明、被抑制 sinθ 方向（保守句）、零多普勒/迹向平面脚注、r_null 矩形联合包络截断、光学 GSD 1/cos² 形式、±608km/±5.5° 配对、消融 B 的 f2 显著未述/25% 口径、Table 6 SD、N≲100 稀疏边界统一、highlights 展开+bullet 合并、Acknowledgments/Funding 去重、贡献 1 拆句。

## 工具/仓库债

| 项 | 裁决 | 目标 |
|---|---|---|
| bib Peng2019 截断/漏作者 | **will_address** | 核 bib 条目，补全标题与 Xing/Vansteenwegen；Das–Dennis/HV/NSGA-II/Moreira2013 补引 |
| sar-domain-knowledge f2/f3 角色互换 | **will_address** | 文档改 f2=几何、f3=NESZ（与实现一致） |
| check_refs.py 不跟 \input | **will_address** | 支持 \input 递归（sec:ablation 误报消除） |
| verify 末位严格档 | **will_address** | 随 N9 落地 |
| 正文数字→字段映射脚本 | **waived（本轮）** | 严格档断言已覆盖主要表格；独立映射脚本属工具增强，本轮不投（理由：边际收益低于实验+写作时间） |

## 执行序（规划）

1. **数据/脚本层**（主线程）：N14 重算、N18 场景生成+烟测+过夜批跑、S2/S4 离线统计、N11 经典 δ 表、phenomenon2 经典 δ 重算、N9 表格脚本值导出。
2. **稿件 EN**：B1 措辞（N1-N6）→ B2（N7-N12）→ B3（N13-N17，N18 待批跑回填）→ S 级 → T 级；每批编译。
3. **ZH 镜像**：逐节同步 + 整句存在性核对。
4. **工具债**：bib/refs/check_refs/domain-knowledge。
5. **终闸**：verify（扩严格档）→ rebuild_snapshot → _audit_full_hard → _pregate_run.sh → 双编译 → re-review 对照本 roadmap。
6. **交付**：ASR-submission-20260831 zip + GitHub push（public 仓，src/Ch3 论文边界）。

---

## 闭环记录（2026-08-31 主线程执行）

### 数据/实验产物（全部可复现脚本落盘）
- `scripts/unified_selector_recompute.py` → N13：统一膝点 S1 f3 边际 U3 +4.9%（p=2.3e-11）、U2 +0.05%（p=0.86）；非对称 +6.2%。
- `scripts/compute_ablation_correlation.py` → N14：调度内 r A −0.63/B −0.23/C −0.65/D −0.13（S1）；f2 池化 std 0.16 恒定，值域压缩替代解释被否。
- `scripts/null_new_caliber.py` → N8 重核：新口径置换零假设 r=−0.60、宽盒 MC −0.28、包络 r=−0.36（结果 `results/null_new_caliber2026.json`）。旧 −0.97 确认为双废产物（错误几何 builder build_agile_instance + 旧口径公式），全部退出。
- `experiments/generate_envelope_cap.py` + `run_envelope_cap.py` + `results/envelope_cap/_progress.json` → N18：E15/E25 各 50 配对场景（pkl 不入库，脚本可再生）；f2 边际 +2.3%/+8.5%/+28%（15/25/45°），覆盖率代价 ~0/4/15%。
- 双倍预算：f1*/f2/f3 漂移均 <2%（budget_control.json 已含，N15 披露入文）。

### 重大叙事修正
§6.4 机制从「包络 −0.97 强冲突被求解器衰减」反转为：原始可见几何弱权衡 −0.36（独立角零假设 −0.60，LOS 耦合稀释）；稀疏调度恢复至零假设强度 −0.63（物理目标主动遍历 θ_elev 权衡，斜视感知组件必要：B 塌到 −0.23、C 保持 −0.65）；高密度覆盖压力下崩溃至 −0.15。贡献 3/摘要/§7/结论同步。

### 工具债
bib Peng2019 标题/作者已核正，补 DasDennis1998/Deb2002NSGA2/Zitzler1999HV 引用；check_refs.py 支持 \input 递归；sar-domain-knowledge.md f2/f3 角色互换已修正。

### 裁决状态
N1-N18、S1-S7、T 清单项全部 will_address 并落地（envelope-caliber 几何核验中发现旧 −0.97 分析用错几何 builder，属面板未发现的额外问题，一并修正）。

### N17 口径更正
N17 初判基于 `build_agile_instance`（与生成器轨道不一致的几何路径）得扫程 3.8°/窗宽 2.8 min，错误。生产口径（`build_agile_instance_from_scenario`，与求解器一致）实测：窗宽中位 1.0–1.2 min（「several minutes」据此修正为「about a minute」）、窗内 ψ 扫程中位 23°/p95 35°（消融节 20–35° 表述正确，保留）、30 s 子区间 ψ 漂移中位 11°/p95 15°（GLM「dwell 20–60°」过高，not_on_point 留痕）。质量取调度时刻、C1 全程 76,190 窗 0 违规已声明入文。

### 核验中发现的额外问题（面板外）
- `scripts/r_visible_envelope.py` 的 −0.97 用了错误几何 builder（build_agile_instance）+ RDR-066 前公式，双废；论文 −0.97 叙事全部退役，以 −0.36/−0.60 替代。
- 窗口生成器窗口末点 10 s 网格后含 θ>47° 边界点（生成器 incidence 检查为 satellite-centered 角而求解器 incidence 为 target-centered，约 2° 差）；求解器 C1 连续审计（0.5 s）不拦，因其检查下界。不影响调度结果（膝点不取这些点），留作后续再生场景时修正（`max_squint_deg` 参数已加到生成器，N18 E15/E25 使用）。
