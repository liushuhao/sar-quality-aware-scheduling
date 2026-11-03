# Pre-gate 提炼项 — 2026-08-15（首跑粗糙版）

> 预闸跑出来的工具/流程痛点，用于跑完迭代后提炼 skill。提交：2c9f909。

1. **audit 脚本 namespace 漂移**：cross_solver_audit 引用已删除的 effect_sizes.json / f2_f3_coupling.json（stats 重构后没人同步），直接崩溃。→ skill 的预闸清单必须含"audit 与数据 namespace 同步检查"（启动时先 py_compile + 冒烟跑 fixture）。
2. **audit 硬编码期望值 = drift 类**：Table2/Table5 的 paper= 期望写死在脚本里，数据重跑后 19 条 false FAIL（tex 其实已同步新数据）。→ 修法：audit 期望值从 tex 表逐 cell 解析，不硬编码（消灭整类 rot）。
3. **Table2 只查 S4**：S1-S3 行无守卫（历史上静默陈旧的风险区）。已扩到全 4 类。
4. **verify_paper_numbers 不覆盖 Table2/Table5**：144 断言只管摘要/§6.x/统计量。表级数字唯一守卫是 cross_solver_audit。→ 表值回源覆盖需显式分配（或 parse-tex 后自然覆盖）。
5. **审计成本**：audit_moea_live 96s/场景全量 ≈ 数小时。→ R&R 分支 SLIM 跳过有依据；pre-sub 首次 FULL 可接受，重跑判定用 caliber。
6. **audit 默认输入孤儿化（3rd rot，已修 c15a2e0 待核）**：_audit_full_hard 默认 `_snapshot_audit.json` producer 死在重构里，磁盘上留 08-04 旧 GA-P-BL → 2645 假 OOW（166/200 场景）。→ 预闸脚本必须"启动时重建输入，不信任磁盘文件"，`rebuild_snapshot.py` 已成 canonical builder（6 族拼 flat，composite key `<fam>|<scenario>` 防 2obj/3obj 场景键碰撞）。版本混合正常：720e63c8≡4cfc42c0 内容同一、消融 b107e97/f96674f 已裁决等价。
7. **G-BL/G-SM 无落盘明细**：baselines_200 b1/b3 只存指标不存 selected/t_actuals，_audit_full_hard 查不了这两族；可行性靠构造期审计（audit_gapbl 系）。→ 提炼时考虑补持久化或明示覆盖边界。
8. **同模式延修实例**：`_audit_cache_vs_precise.py:29` SNAP 同样指向死文件 `_snapshot_audit.json`（非 gate 脚本，诊断用途）——下次统一 sweep 时改指 `_snapshot_gate.json` 并适配 composite key。另 _audit_window_c1_parallel/_audit_baseline_quality/_audit_gbl_c2 未跑，纳入 gate 全量前先 smoke。
9. **_audit_full_hard 默认值已删（e142fc8）**：强制 `--snapshot`，防止未来 naive 运行再踩死文件。历史跟踪的 `_snapshot_*` 兄弟文件（10 个）保留不动作——取消跟踪是独立决定，待用户拍板。
10. **窗口审计覆盖边界**：_audit_window_c1_continuous 只扫 S1-S4（76190 窗，历史同数）；S5-S8 窗口未被连续 C1 覆盖（full_hard 已验其 saved 解 0 违规，但窗口本体未扫）→ 提炼时扩 groups 或明示边界。

## 流程观察

- 预闸 value 证实：2 个 rot 实例 30 分钟内被确定性脚本抓到（非文本审稿人可见）。
- 人机节点生效：预闸是纯机械（AI 干活），分诊/接受是人的动作。