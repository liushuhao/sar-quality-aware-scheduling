# 异源回扫任务书 — paper1 2026-11-02 修复批次

## 红线（先复述再干活）

1. 只读：不得修改、创建、删除仓库内任何文件；唯一允许写的是你自己报告里的文字。
2. 不得发明数字：每个数字必须来自你实际读到的文件内容或命令输出。
3. 不得把"我检查过了"当证据：每条发现给 `file:line` + 引用原文或命令输出。
4. 不确定写"未验证"，不许猜。
5. 只审本次改动，不提与本批无关的重构建议。

## 审查对象（工作目录：仓库根 `D:\hermes\my-workspace\projects\planning-paper`）

- 文本 diff：`papers/single-sat-quality/review/audit-20261102/review-diff.patch`（452 行，含 tex / py / md / json）
- 变更清单：`papers/single-sat-quality/review/audit-20261102/review-diffstat.txt`
- 处置台账：`papers/single-sat-quality/review/audit-20261102/fix-plan.md`
- 二进制改动（PDF/PNG）不在 diff 内，只需核对文件存在性与引用关系。

## 本批改了什么（供定位，不当作结论）

1. N50 数值：中英各 4 处 `N_{50}\approx 50`→`51`，CI `[30,62]`→`[37,64]`；
   `experiments/results/n50_logistic.json` 重跑（50.77 / [37.0, 64.2]）。
2. 摘要密度阈值：`N \geq 300` → `N \gtrsim 150`（中英摘要各一处）。
3. 图脚本：图 3 底部拟合改用六类 300 场景并读 JSON；图 4 图例重新定位；
   消融图 y 标签缩短、阈值 0.005→0.05/12、输出改名 fig5_ablation。
4. 删除：4 个 `*_grayscale.png`、`fig6_ablation.{pdf,png}`（后者未跟踪）。
5. 数字闸 `src/tools/verify_paper_numbers.py`：N50 检查改为解析两版 tex 再与 JSON 比对。
6. 中文补 3 条引用、2 个 label；IQR/SD 补全称。

## 要你核的问题（逐条回答）

A. 数值一致性
   A1. 两版 tex 里所有 `N_{50}` 印刷值和 CI 是否已全部改成 51 / [37,64]？有无漏改？
   A2. `n50_logistic.json` 的 N50、ci_low、ci_high 与 tex 印刷值四舍五入后是否一致？
   A3. 图 3 生成脚本现在是否真的用六类（S1,S2,S7,S8,S3,S4）场景、读同一 JSON？
       还是仍会与正文分叉？给出代码行号。

B. 阈值措辞
   B1. 摘要是否已无 `N \geq 300`？结论/贡献列表/高亮/投稿信仍是 150 吗？
   B2. 改写后的摘要句子是否语法通顺、`\gtrsim` 用法正确？

C. 图脚本正确性
   C1. 图 4 图例的新锚点是否会再次压住 x 轴标题？依据是什么（坐标/边距）。
   C2. 消融图标签改短后是否丢失必要信息？图注是否覆盖？
   C3. 生成脚本输出改名后，仓库里还有哪里引用 `fig6_ablation`？会不会有脚本仍写旧名？

D. 删除面
   D1. 被删的 grayscale / fig6 文件是否还有任何 tex/py/md 引用？
   D2. 删除是否影响 `pytest` 或 provenance 检查？

E. 闸门有效性
   E1. 新 N50 检查是否真的读 tex（而不是自比自）？给出代码行号。
   E2. 有没有"正则匹配不到 → 静默通过"的路径？例如某版 tex 里一处都匹配不到时会发生什么？

## 回传格式

先复述 5 条红线。然后一张表：

`编号 | 严重度(须修/建议/未发现问题) | file:line | 问题 | 证据（引用原文或命令输出） | 建议`

最后一行写：`发现数：N（须修 X / 建议 Y）`。没有发现也要写"N=0"。
