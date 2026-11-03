# RDR-006 — G-SM f3 效应量 δ 硬编码残留（0.91 → 1.0）

**来源**：S1 INTEGRITY 数字清册（verify_paper_numbers.py，2026-08-10）
**优先级**：P1（机械/事实类，数据回源错误）
**状态**：fixed（待 S7 独立验证后 closed）

## 评论/发现原文

论文 §6.2（EN L767 / ZH L597）与 §4（EN L514）、§7.1（EN L~1083）、ZH L383/L838 共 5 处写：

> "Across all 200 scenarios, this produces a large positive effect on $f_3$ (Cliff's $\delta = +0.91$, $p < 10^{-34}$)"

## 数据回源

对 `baselines_200.json` 全部 200 场景逐场景配对计算 G-SM `f3` vs G-BL `f3` 差分：

```
f3:  G-SM vs G-BL cliff_delta = +1.0000  (greater=200, less=0, n=200)
     Wilcoxon W=0, p = 1.436e-34
```

**200/200 场景 G-SM f3 均高于 G-BL**，Cliff's δ 严格 = +1.0。论文 0.91 无任何代码/数据来源（全仓 grep `0.91` 无 delta 相关命中），系历史硬编码残留（早期数据/口径）。

对照组 f1* 维度：`δ = -1.0000, p=1.436e-34`，论文 §6.2 写 `-1.0`，正确。

## 决策

🔴 必须改 —— 事实错误，数据回源 +1.0，论文 0.91 无支撑。

## 修复

EN + ZH 共 5 处 `$\delta = +0.91$` → `$\delta = +1.0$`（replace_all）。
- EN: L514（方法段）、L767（§6.2 结果）、§7.1 finding(3) 附近
- ZH: L383、L597、L838

## 验证清单

- [x] verify_paper_numbers.py 新增真断言 `g2-gsm-f3delta`（期望 +1.0），144 断言全过 exit 0
- [x] EN pdflatex ×2 编译过（36 页）
- [x] ZH xelatex ×2 编译过（30 页）
- [x] 中英数字一致（replace_all 双向覆盖）

## 备注

旧统计 `statistical_results.json` 的 `G-BL_vs_G-SM`（HV 维度 δ=-0.96）与论文 §6.2 的 f1*/f3 维度效应量**不同度量**，不冲突；论文未使用 HV 维度该值。
