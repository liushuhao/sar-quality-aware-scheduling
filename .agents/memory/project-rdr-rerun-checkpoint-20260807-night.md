---
name: project-rdr-rerun-checkpoint-20260807-night
description: 2026-08-07/08 夜 P1修复后核心三族重跑中（schtasks，S3中段）；批2消融schtasks已预建未发射；休眠注水runtime_s教训；审计/论文同步待做
metadata: 
  node_type: memory
  type: project
  originSessionId: 815305c4-f178-4db2-95f8-ce2675b5cb8f
  modified: 2026-08-09T00:12:21.088Z
---

**2026-08-09 08:00 收工（用户中止；批2 全完成 + ablation 段已填）**：
- **批2 三消融 200×3 全完成 + 审计 0 OOW 0 C1-C4**（exit 0 ×3）+ pkl_sha1 四源一致。
- **ablation 段已填 + 提交**（4dfb968，EN+ZH）：核心密度依赖叙事无翻车；旧 bug 时代幅度修正（D +22%→-2.7%、C +21.6%→+7.5%、B -9.5%→-2.0%）；D"近同质量"改"f3 换覆盖"。
- **s1s2 control 完成 → 停闸**：新 random-init delta 0.269/0.493 vs 旧 0.179/0.419，摘要 `0.18--0.46` 须改（0.27--0.49 或区间化，**用户拍板**）。
- **教训**：跨 runner 字段语义不一致（消融 f1_gbl=1.0 占位）→ feedback-cross-runner-field-semantics。
- **下轮 Next**：摘要 random-init 拍板 → s3s4/variant_d controls → §6.5 同步 → §6.4 相关性重算核验 → 三轮自查（ZH fig label）→ 最终编译 → push 等指令（未推送链 c8d8a01…4dfb968）。

**2026-08-09 00:30 状态（中英同步过半 + 批2 跑中）**：
- **EN 数据重写全完成 + ZH 同步过半**（commits 22778e9/36af17b/0183500，双版编译通过 EN 36pp/ZH 31pp）。ZH 已镜像：摘要/§6.1-6.3/§6.4/§7 摘要+运营/§8；EN 残留 GA-P-BL"最强"声明 + §6.4 S4 投影已修。
- **批2 消融跑中**（no_incidence/no_physics/no_squint ~55/54/57，S2 段）+ s1s2 hotstart control 跑中。
- **下轮 Next**：消融完 → audit + analyze_ablation → ablation 表+正文（EN+ZH）；s1s2 control 完 → 核验 random-init 0.18-0.46；s3s4/variant_d controls → §6.5 同步；三轮自查（含 ZH fig label 乱序）+ 最终编译；push 等用户指令（未推送链 c8d8a01…0183500）。
- intake v2.2 定稿（skill + 13 条预填 + 全局规则 7）。

**2026-08-08 23:35 收工状态（S8 完 + §6.3 落地 + 批2 发射）**：
- **MOEA-2 全 300 完成 + 审计全绿**（S1-S4+S7+S8，0 OOW 0 C1-C4，audit 258s）。至此批1 三族全量完成。
- **§6.3 用新数据重写 + 编译通过**（commit 36af17b）：新六档表 S1 0.87/84% → S2 0.985/6% → S7+ 0%；**N50≈50**（旧 140，弱约束——仅 N=20/100 信息点，bootstrap CI 不收敛，论文诚实标注）；§6.4 尾 HV 比例 0.18/0.11、Discussion N50/±32%/63% 同步。
- **批2 三消融已发射**（schtasks，插电 72%）：no_incidence/no_physics/no_squint 各 S1-S4(200)，PIDs 2152/14440/2300，`--resume --groups S1 S2 S3 S4`。
- **下轮 Next**：批2 消融完 → snapshot+audit → 更新 _ablation_section.tex + §6.4 相关性(-0.69 to -0.17) → §6.5 controls 重跑（hot-start/perturb/random/budget，数据全在 _old_buggy_orbit 旧档）→ 摘要 random-init 声明核验 → 中英同步 + 三轮自查 + 编译 + 推送（未推送链 c8d8a01…36af17b）。
- 遗留：gen_table1 脚注已修(commit aa52543)；GA-P-BL runner 未落 used_gbl_fallback；results/_snapshot_moea2obj.json(300 旧) 待删。
- 跨会话：**intake v2 已定稿**（`~/.claude/skills/intake/` + 全局 CLAUDE.md 规则 7 已加；lsh-wiki/stock-work 二轮回应已并，13 条预填故障模式 + 强制机制分层）。临时档 `_intake-*.md` 讨论后可删。

**2026-08-08 20:17 收工状态（批1 中止，250/300）**：
- **批1 三族 S1-S4 全完成 + 审计全绿**（GA-P-BL/MOEA-2/MOEA-3 各 200，0 OOW 0 C1-C4）。statistical_analysis + gen_table1 已完成 → 最终 Table 1 → docs/table1-solver-matrix.md。G-BL vs GA-P-BL p=0.084 ns；MOEA-2 vs MOEA-3 p<0.001（f3 非冗余）。见 project-paper-data-check-20260808。
- **MOEA-2 S7 完成、S8 未跑**：19:53:22 进程被外部终止（exit=1，无 traceback 无 WER，同秒 VBScriptDeprecationAlert 系统维护，非代码缺陷），S7 49/50 定格；`schtasks //run` + `--resume` 重发，pkl_sha1 跳过 249，补算 S7-E 尾场景 → **250/300（S7 50/50 全完成）**。用户指令中止，S8（50 场景 ≈1.7h）未跑。
- **下轮 Next**：若需 300 场景完整声明 → `schtasks //run //tn planningpaper_fi_moea2`（--resume，只算 S8 50）→ 补 audit → `recompute_scale_sensitivity.py` + `gen_all_figures.py` → 批2 消融发射+审计（schtasks 已预建 `planningpaper_fi_abn_*`）→ 论文重写（Table 1 已备好数值，§6.1/6.2/摘要 f3 冗余段、GA-P-BL 段、MOEA-2 deficit 段）→ 编译推送。
- 教训：进程崩溃无 traceback 无 WER = 外部终止（睡眠/维护），判死前查系统维护事件；log 尾滞后 ≠ 死，判活用 progress json + 进程。详见 feedback-external-process-kill-resume。
- 遗留：gen_table1.py 脚注 "f2/f3 lower is better" 须改 higher-better；GA-P-BL runner 未落 used_gbl_fallback。

**2026-08-08 17:59 收工状态（第三日续跑）**：
- **GA-P-BL 200/200 完成 + 审计全绿**（_snapshot_gapbl.json，0 OOW 0 C1-C4，246s/6 worker）。**GA-P-BL = G-BL 逐位相同坐实**（全 200 含 S4，df2/df3=0；so_f1.py:743 "never worse than G-BL" 回退全触发）。
- **MOEA-3 199/200**（S4 剩 1，17:58 mtime 新鲜）、**MOEA-2 199/300**（S4 剩 1，S7/S8 未跑）。S4-E 尾段单场景 5-15min 属正常（N=500 紧 incidence），**mtime 停滞 9-16min ≠ 挂死**，判活须 进程+WorkingSet+log 尾 三要素。
- 会话内数据核对结论见 project-paper-data-check-20260808：GA-P-BL=G-BL、论文 Table 全旧数据无法复现、f3 冗余声明稀疏场景被证伪、S4 反转（MOEA f2 +5% 但 f3 −12%，f3 密集段冗余）、S3/S4 前沿近点压缩。
- 批2 消融 schtasks 未发射（等批1 审计全过）。
- **下轮 Next**：MOEA-3/MOEA-2 S4 完 → snapshot+audit → statistical_analysis + gen_table1（重算）+ scale_sensitivity + figures → 批2 消融发射+审计 → 论文重写（Table/§6.1/6.2/摘要 f3 冗余段、GA-P-BL 段）→ 编译推送。
- 教训：GA-P-BL runner 未落盘 `used_gbl_fallback`，数据无法区分 fallback/真收敛；下轮若重跑 GA-P-BL 补字段。

**2026-08-08 12:15 第三次续跑（开机恢复）**：
- 8:05 关机定格 134/131/130 未变。12:15 `schtasks /run` 三任务全发射成功，3 python 活（PIDs 16420/11396/13832，run_so_f1_bl/run_moea_2obj/run_moea_3obj，`--resume --groups`，HEAD dd77836 含 P1 修复）。
- 剩余：gapbl S3(16)+S4(50)=66、moea2 S3(19)+S4(50)+S7(50)+S8(50)=169、moea3 S3(20)+S4(50)=70。活跃估算 gapbl/moea3 ~5h、moea2 ~12-16h。
- 判活：`wmic process where "name='python.exe'" get ProcessId,CommandLine`（注意引号逃逸）+ progress mtime。

**状态 2026-08-07 22:33（P1 修复后重跑夜班，第二次续跑）**：

接续 feedback-window-full-interval-p1-20260807。P1 修复（commit `f1e55e5`）后进化族全量重跑。

**⚠️ 第一次批跑被 hermes 重启杀掉（20:21 Start-Process 启动 → 21:13 死）**：
- 证物：progress mtime 停在 21:13，python 进程消失；hermes.exe update 22:16 重启，本会话 22:19 新开。
- **教训（升级）**：`Start-Process` 和 bash `&` 都**不抗 hermes 重启**（内存按 session 清理子进程树）。唯一可靠 = **schtasks 计划任务**（`_run_full_rerun_20260806.bat` 注释早有此义）。已获用户批准使用。

**⚠️ 2026-08-08 06:50 纠正误诊（重要）**：
- 曾疑 S3 场景运行时 ~100x 回归（22176s vs 旧 156s）→ **误诊**。机理：批跑夜间机器休眠，`runtime_s` 是墙钟差，休眠期间照样涨（b2 S3-A_seed09=369min、moea3 S3-A_seed08=308min 等 4 个离群全是休眠）。活跃真实成本 **2-12 min/场景**（前台 200 代实测 440s，n_sel=200 与批跑一致）。
- 对比铁证：全部 S3 条目除 4 个休眠离群外均 139-748s；三个族各 1-2 个离群，与休眠事件吻合。
- **结论：无回归、数据有效、不用修求解器**。旧 156s vs 新 ~400s 的 2-4x 是 n=200→300 正常超线性缩放。
- **遗留数据质量项**：`runtime_s` 被 statistical_analysis.py 带进结果 dict 但**不进任何报告表格**（论文只报 f1/f2/f3/HV）——低影响；但任何未来消费 runtime_s 的步骤须先剔除 >1h 离群（休眠注水）。
- 教训：夜间长跑墙钟 runtime_s 不可信，判性能回归必须用前台实测或活跃时间，不能拿跨休眠的墙钟比历史。

**第二次续跑（22:28 schtasks 启动，--resume，跳过已完成）**：
- 任务：`planningpaper_fi_gapbl` / `planningpaper_fi_moea2` / `planningpaper_fi_moea3`，各跑 bat `experiments/_resume_fi_{gapbl,moea2,moea3}.bat`（`--resume --groups S1 S2 S3 S4`；moea2 加 `S7 S8`），log `logs/rerun_fi_resume_*.log`。
- 22:33 验证：3 python 进程活（run_so_f1_bl/run_moea_2obj/run_moea_3obj，git_commit 486b60a7），进度 69/68/67（gapbl 67→69 等），mtime 新鲜，0 infeasible 0 errors。
- 判活（**别看 log，block-buffered**）：`schtasks /query /tn planningpaper_fi_* /v /fo LIST`（Last Run Result=0）+ progress mtime；或 `_check_alive.ps1`（logs/，无 filter 版本看全部 python）。

**2026-08-08 07:00 批1 进度**：S3 中段（gapbl 17/50、moea2 15/50、moea3 14/50），全绿 0 infeasible/0 errors。活跃 ~2-12 min/场景。剩余活跃估算：gapbl/moea3 ~8h、moea2 ~16h（S3 尾+S4+S7+S8），墙钟随睡眠拉长。

**⚠️ 2026-08-08 08:05 用户关机，批跑主动停止（断点）**：
- 三个批1 任务已 `/end` + taskkill（PID 11860/18224/1172 全死，schtasks /end 只标记任务不杀进程，须 taskkill //PID //F //T）。
- 定格进度：GA-P-BL 134/200（S3=34）、MOEA-2 131/300（S3=31）、MOEA-3 130/200（S3=30），全绿 0 infeasible。
- **下次开机恢复**：三个任务仍注册着（/sc once 已跑过一次，直接 `schtasks /run /tn planningpaper_fi_{gapbl,moea2,moea3}` 会重跑整组，靠 `--resume` + pkl_sha1 守卫跳过 130+ 已完成，只算剩余）。log 追加 `rerun_fi_resume_*.log`。
- 08:00 已重新验证：392 场景三层全绿（字段/pkl_sha1/可行性 + 硬约束 C1-C4/OOW 全窗，S3 新增全过）。

**批2 消融已预建（commit dd77836，2026-08-08 07:00，未发射）**：
- 3 个 schtasks 已注册：`planningpaper_fi_abn_{incidence,physics,squint}`，各跑 `experiments/_resume_abn_{incidence,physics,squint}.bat`（`--resume --groups S1 S2 S3 S4`，200/族），log `logs/rerun_fi_resume_abn_*.log`。
- 发射条件：**批1 全量审计通过后**。命令：`schtasks /run /tn planningpaper_fi_abn_incidence`（physics/squint 同理）。
- 已验证：三个消融 runner（run_moea_3obj_no_{incidence,physics,squint}.py）都落 `pkl_sha1`（resume 守卫 355 行类）+ 审计字段（selected/t_actuals/phis_off_nadir/constraint_feasible）。
- 注册脚本：`experiments/_setup_abn_tasks.bat`（只 create 不 run）。

**完成后流程（Next 顺序）**：
1. 逐族 `progress_to_snapshot.py results/<fam>/_progress.json _snapshot_<fam>.json` + `_audit_full_hard.py --snapshot ... --jobs 6`（新整段判据 + 非零退出码，任一非 0 即停）。
2. `statistical_analysis.py`（provenance 守卫校验跨族 sha）→ `gen_table1.py`/`recompute_scale_sensitivity.py`/`gen_all_figures.py`。
3. 批1 审计通过后发射批2 消融（schtasks 已预建，勿再 Start-Process）：`schtasks /run /tn planningpaper_fi_abn_{incidence,physics,squint}` → 完成后审计。
4. 比对 Table 1/§6.3（N50≈60 是窗口修复前+P1 旧数据，须重算），中英同步，pdflatex 英/xelatex 中各两遍 + 三轮自查。
5. 提交推送（FastGitHub `http.schannelCheckRevoke=false`）。未推送链：c8d8a01…f1e55e5（filter-repo 后首推核对 public 边界）。
6. 可选：新代码重跑基线补 pkl_sha1 字段（~9min 确定性），消除 provenance 守卫 legacy warn——非阻塞。

**基线不用重跑**（solver 有整段检查 baselines.py:194,237）。作废数据已移 `*.bak_pre_fullinterval_20260807`。

相关：feedback-window-full-interval-p1-20260807、feedback-diagnostic-replay-must-use-exact-params、project-rdr-rerun-checkpoint-20260807-batch1、[[feedback-long-task-checkpointing]]、[[feedback-no-config-change-during-long-batch]]。