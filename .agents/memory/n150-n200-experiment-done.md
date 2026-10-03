# N150/N200 中间密度实验（2026-07-31 完成）

## 结果（已落地论文，中英双版编译通过）
- 跑了 S7（N=150）+ S8（N=200）各 50 场景的 MOEA-2obj（约 75min，49s/场景，hot-start NSGA-III pop100/gen200）
- **N50: 169 → 140；95% CI [111,227] → [117,169]，宽度收窄 55%**（n50_logistic.py，300 场景，1000 bootstrap seed42）
- 各密度 deficit% 序列：S1 88 / S2 62 / S7 42 / S8 30 / S3 16 / S4 24
- f1*(MOEA-2)：S7 0.94±0.06、S8 0.96±0.04；f2 improvement：S7 +0.4%、S8 +0.2%（中间密度 f2 增益触底近零，S3/S4 小幅回升至 1.6/1.5%，U 形非单调——正文已如实写）
- χ² S3→S4 真值 1.00/p=0.32（非旧论文 0.64/0.42）

## 顺带挖出的预存错误（论文-数据不符，与本次补实验无关，但一并纠正）
- Table scale-sensitivity 的 S2/S3/S4 deficit% 写 64/14/20，数据真值是 62/16/24（S1 88% 恰好对）
- S1 f2 improvement 写 +8.0%，真值 +8.2%
- 讨论/结论多处 "88% to 20%"、中文 "14%/20% 的 S3/S4" 均同步为真值
- 根因：数据自初始化提交 6533c1f 起逐字节未变（git show 验证，200 共同 key 0 值变化），论文数字从一开始就对不上。Trae 等审计只盯逻辑矛盾，从未核过 deficit 计数

## 2026-08-01 追加：平台参数两处预存错误（用户要求按代码改，已 fixed）
- **G3 轨道高度**：论文写 600 km，代码 SENTINEL1 altitude_km=693（中英方法段+局限段共 4 处 600→693）。倾角 97.8°/LTAN 06:00 本就对。
- **G4 测绘带半宽**：论文写 ±2.7°/±300 km，代码 get_swath_params(693,47) 实算 ±5.46°/±608 km。原值还自相矛盾（2.7°@693km 只对应 ~33 km 非 300 km）。中英改 ±5.5°/±608 km，去"angular"改"half-width"——5.46° 是地面角（608/111.32），卫星指向角边缘实为 ~41°，避免误读。
- 台账 G3/G4 已登记，双版编译通过（pdflatex 35 页 / xelatex 30 页，0 error）。教训延续：审计只查逻辑矛盾不查数值出处，平台参数硬数字必须拿代码重算。
- **下次开工第一件事**：旧投稿包 ASR-submission-package.zip（07-22）已陈旧 5+ 轮修订（N50 + deficit 真值 + 高度 + 测绘带），必须重打包。

## 设计决策（重要）
- **S7/S8 只进尺度敏感性分析（Table/N50/文字），不进 5-solver 池化统计**：S7/S8 只跑了 MOEA-2 + G-BL/G-SM，无 MOEA-3/GA-P-BL。statistical_analysis.py 和 gen_all_figures.py 的 common_keys 要求全 5 solver，天然排除它们——头条 δ=+0.72/HV/Wilcoxon 不受中密度过加权污染。方法段已透明说明
- **主设计措辞"200 scenarios / four density classes"保留**：指 S1-S4 完整 5-solver 主库；S7/S8 是补充的 100 个。场景表 tab:scenarios 不加 S7/S8（否则与 solver-profiles 表"all classes"声称冲突）
- **fig5（含 logistic N50 面板）是孤儿图，正文从不引用**（正文 fig1-4）。N50 纯靠文字+Table，故不用重绘 fig5、不用改 gen_all_figures.py
- runner run_moea_2obj.py 的 GROUPS 已加 S7/S8（保留，不还原——实验已成正式数据）

## 教训
1. resume 模式只追加新 key、不重算旧的——加 S7/S8 跑绝对安全，旧 S1-S4 的 200 个值零变化（用 git show HEAD 对比验证过）
2. Python 重定向后台跑时 stdout 全缓冲，log 文件空是假象；真信号是每场景落盘的 _progress.json。用它做进度监控而非 tail log
3. Bash 分类器后端故障（"temporarily unavailable"）会间歇性阻塞所有非只读命令；只读工具不受影响。等它恢复即可，不要反复空转
4. 论文里的数字不能信审计结论"已验证"，要自己用底层 JSON 重算——本轮发现的 64/14/20 假值逃过了 6 轮 agent 审查

## 文件改动
- experiments/results/moea_2obj/_progress.json（+100 S7/S8 场景，现 300）
- experiments/results/n50_logistic.json（新拟合值）
- experiments/run_moea_2obj.py（GROUPS +S7/S8）
- scripts/n50_logistic.py（GROUP_N +S7/S8，docstring 更新）
- small-paper-ijae.tex + small-paper-ijae-zh.tex（§6.3 正文/表/N50段、方法段、结论、摘要 8.0→8.2）
- review/REVIEW_INDEX.md（N50 项 waived→fixed）
- 未做（可选）：MOEA-3obj/GA-P-BL on S7/S8（给完整 6 密度 solver-profiles 表，需 4-8h，非核心）；baselines_S7S8.json 合并进 baselines_200.json（仅当要重绘孤儿 fig5 才需要）
