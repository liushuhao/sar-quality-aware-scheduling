# 确认轮 — 核对上一轮发现的修复是否落地

只读。逐条核对下列修复是否真的落在文件里、且没有把句子改坏。每条给 `file:line` + 引用修复后的原文。

工作目录：`papers/single-sat-quality`

## 应有改动（英文 `small-paper-ijae.tex`）

1. 正文不再有被空格包围的 ` -- `（D-2）。
2. 句子不再出现 "that we measure rather than assume"（D-1）。
3. 不再出现 "not an artifact of the class-specific geometry variants"，改为正面陈述（D-3）。
4. 变体 A 子集相关系数前应写明 "10 variant-A schedules per class"（A-7）。
5. 置换零假设句应写成 "-0.60$ to $-0.62$ across classes" 且 95% 区间表述为 "within $\pm 0.02$"（A-1/A-2）。
6. 贡献列表与摘要中的相关性下限区间应为 "$-0.13$ to $-0.23$"，不得再出现 "$-0.2$ to $-0.15$"（A-3）。
7. within-schedule f2 标准差句应为 "$0.16$--$0.17$ at S1--S3"（A-5）。
8. 扰动扫描覆盖率句不得再写 "all 10 sweep scenarios reach the ceiling"，应改为 σ ≤ 0.5 全触顶、σ=0.7 均值 199.5（A-4）。
9. 热启动任务数 154.5/142.7 后应注明 "50 scenarios per class"（A-6）。
10. 图 7 中不得再有未入图例的灰色点线；`scripts/gen_fig7_fig8.py` 中不应再有 `nl_mu` 的 `ax.plot` 调用（B-1）。

## 应有改动（中文 `small-paper-ijae-zh.tex`）

11. 上一轮 5/6/7/8/9 五项在中文稿同样落地。
12. 中文稿 `目目标和` 已改为 `目标和`（C-2）。
13. 中文稿正文的 ASCII 直引号 `"` 已改为全角引号（C-3）。
14. 中文稿正文（非注释、非 CRediT 行）的 `——` 应只剩 0 处；只剩两处：文件头注释行与 CRediT 行（C-1）。

## 不要做

- 不要再提新建议，只核对上面 14 条是否成立。
- 不要改任何文件，包括不要写 findings。

## 回传

直接在你的最终消息里给一张表：`序号 | 成立/不成立 | file:line | 引用原文`。
最后一行写：`确认轮：N/14 成立`。
