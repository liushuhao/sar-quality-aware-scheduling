# RDR-063 — hotstart control 数据新旧混入，§6.6 deficit 混算

**来源**：S1 INTEGRITY 数字清册（verify_paper_numbers.py，2026-08-12 全程审稿重跑）
**优先级**：P0（数据污染 → 论文数值错）
**状态**：fixed（数据清理 + 论文更新 + 断言更新；待 S7 独立验证后 closed）

## 评论/发现原文

verify_paper_numbers.py 12 断言失败，含 `hs-S1..S4-n`（paper=30/12/15/15 data=60/24/30/30）、
`hs-S3/S4-deficit/sd`、`sw-f2/f3`、`vd-S3/S4-f2`。

## 根因

`experiments/results/p1-1_random_init/hotstart_control_s1s4.json` 在 2026-08-12 几何修复重跑
（commit `acb64df`）时 **append 而非替换**：旧 72 记录（pre-geomfix，commit `0036c2e`）+ 新 72 记录
（post-geomfix）= 144。`run_hotstart_control_s1s4.py` 的 resume 只查 `done` dict（`pkl#extra` 格式），
旧记录无匹配 done key → 全量重跑后 `scales[scale].append(...)`，未先去重。

逐位核对 git `0036c2e`：文件前半（first_half）与旧版本 deficit 序列完全一致 → 前半=旧、后半=新。
论文 §6.6 deficit（EN L1055/ZH L771）现值 = 144 混算：
- 旧（pre-geomfix，错）：S1 −0.245 / S2 −0.486 / S3 −0.678 / S4 −0.540
- 混算 144（论文现印）：−0.237 / −0.480 / −0.622 / −0.461
- **新（post-geomfix，正确）**：S1 −0.229±0.121 / S2 −0.475±0.056 / S3 −0.565±0.026 / S4 −0.382±0.046

## 决策

🔴 必须改 —— 论文 deficit 数值来自污染样本（几何修复前后混合），真值应为 post-geomfix 72 记录。

## 修复

1. **数据清理**：`hotstart_control_s1s4.json` 按 (scenario, seed, extra_seed) 保留最后出现（=新），
   n=30/12/15/15=72，done dict 重建 72 key，summary 用 ddof=1 重算。
2. **runner 根因**：`run_hotstart_control_s1s4.py` append 前按 (scenario, seed, extra_seed)
   去重替换（resume 幂等），防复发。
3. **论文更新**（deficit 全 6 处）：
   - EN：L49 摘要 `0.24--0.62`→`0.23--0.57`；L1055 四值→`−0.229±0.121 / −0.475±0.056 / −0.565±0.026 / −0.382±0.046`；L1058-60 `−0.62→−0.57 / −0.24→−0.23 / −0.46→−0.38`
   - ZH：L46 摘要同改；L771 四值同改；L773-74 同改
   - f2 行（L1063-64 "0.551 vs 0.550"）无需改——post-geomfix 仍成立
4. **断言更新**：`verify_paper_numbers.py` hs-* deficit/sd→post-geomfix 值、sw-f2/f3→0.535/0.435、
   vd-f2→0.527/0.520。

## 验证清单

- [x] 数据清理后 n=72，done 72 key，deficit = post-geomfix 精确值
- [x] 论文 EN+ZH 6 处改完，双版编译过（EN 39 页 / ZH 31 页 0 error）
- [x] verify_paper_numbers.py 144 断言 0 failed（12→0）
- [x] f2 行数值 post-geomfix 复算仍吻合（S3 0.551 vs 0.550 / S4 0.551 vs 0.551）

## 备注

- 数据文件 git 追踪（0036c2e 72 → acb64df 144 → 本轮 72 post-geomfix），历史可追溯。
- 摘要 "0.23--0.57" 范围 = |min|=0.229(S1) 至 |max|=0.565(S3)。
- 举一反三：variant_d_random_init/full.json（30）、sigma_sweep/sweep_summary.json（8 row）、
  random_search 均验 0 重复——污染仅 hotstart 一处。
