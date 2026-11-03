# 异源回扫（精简版）— paper1 2026-11-01

只做三件事。每完成一件，**立刻把该节写入** `review/cross-review-20261101/findings.md`（用追加方式），
不要等全部做完再写。

开工前先把下面五条红线原文复述进 findings.md 开头：
1. 只读：只允许写 findings.md。
2. 每个数字必须来自实际读到的文件或命令输出。
3. 每条发现必须带 `file:line` + 引用原文。
4. 不确定写"未验证"。
5. 不评价论文该不该做某项研究，只核对一致性。

## 任务 A — 数字核对（只核这 6 条）

逐条到数据文件算，写出"复算值 vs 正文值"：

| 正文值 | 正文位置 | 数据文件与字段 |
|---|---|---|
| 变体 A 相关 S1=−0.62, S2=−0.15, S3=−0.13, S4=−0.23 | `small-paper-ijae.tex` 搜 `-0.62` | `experiments/results/schedule_correlation.json` → `variants.A_full_physics.S1.r`（同 S2/S3/S4） |
| 变体 B/C/D 在 S1 = −0.23 / −0.65 / −0.13 | 同上附近 | `experiments/results/schedule_correlation_ablation.json` → `variants.B_no_squint.S1.r` 等 |
| 包络 −0.36（S1 −0.35，S2–S3 −0.37）；零假设 −0.60 | 搜 `-0.36` | `experiments/results/null_new_caliber2026.json` → `S*.r_envelope`、`S*.r_shuffle_null_mean` |
| 覆盖亏损 −0.393 / −0.551 / −0.684 / −0.475 | 搜 `0.684` | `experiments/results/p1-1_random_init/hotstart_control_s1s4.json`：对每类算 mean(random.f1 − hot.f1) |
| 随机搜索 0.527 / 0.930 / 1.000 | 搜 `0.527` | `experiments/results/p1-2_random_search/p1-2_s1_random_search.json` → `results.*.f1_star_mean / f1_star_p90 / f1_star_best` 的均值/最大值 |
| 任务数 70.3 / 117.8（随机初始化）与 154.5 / 142.7（热启动） | 搜 `154.5` | 随机：`experiments/results/variant_d_random_init/full.json` → `results.S3[].n_selected` 均值；热启动：`experiments/results/moea_3obj_no_physics/_progress.json` → `completed` 里键以 `S3/` 开头的记录的 `n_selected` 均值（S4 同法） |

## 任务 B — 中英镜像（只核这 4 项）

```
cd papers/single-sat-quality
grep -c '\\section{' small-paper-ijae.tex small-paper-ijae-zh.tex
grep -c '\\begin{figure' small-paper-ijae.tex small-paper-ijae-zh.tex
grep -c 'fig7_corr_density.pdf' small-paper-ijae.tex small-paper-ijae-zh.tex
grep -c -- '-0.63' small-paper-ijae.tex small-paper-ijae-zh.tex
```
预期：section 数与 figure 数两版相同；两版各含 1 个 fig7 引用；两版 `-0.63` 均为 0。

## 任务 C — 正文残留（只核这 3 个计数）

```
cd papers/single-sat-quality
grep -c -- '---' small-paper-ijae.tex        # 预期 0（注释行不计）
grep -c 'Phenomenon' small-paper-ijae.tex    # 预期 0
grep -n 'rather than' small-paper-ijae.tex | wc -l   # 报总数即可
```

## 回传

- findings.md 结尾给：`发现总数 / 须修数 / 结论（通过|不通过）`。
- 最终消息只用三行：A 是否一致、B 是否一致、C 计数。

严重度只用：须修 / 建议 / 观察。
