---
name: rdr066-caliber-verify-gate-20260813
description: "2026-08-13 新口径下 verify_paper_numbers 从 73→2 fail，抓出 §7.1 统计量漏更新（Friedman χ² 552.91→392.47）；全量同步 Table1/§6.2/§6.3/§6.4/§6.6/§7.1 断言"
metadata:
  node_type: memory
  type: project
  originSessionId: c915ef70-ccfb-4e12-aba6-5dedc4e6c7b3
  modified: 2026-08-13T15:19:24.159Z
---

2026-08-13 会话第二段：新口径下 verify_paper_numbers 断言全量更新（73→2 fail），fig1-4 重生成，phenomenon2_cliff 重算。

**verify 更新**：142 断言，140 通过，2 fail（variant-D 段 + 1 SKIP corr-D 均因消融未完）。T1 全表/§6.3 scale/§6.2 G-SM/§6.4 n_frontier/Phenomenon2/相关/§6.6 hotstart+σ/§7.1 Friedman+HW δ/Cliff δ 全同步到新口径。vd-S3/S4 断言 0.527/0.520 旧→论文该段待消融后改。

**抓出漏网**：b107e97 漏更新 §7.1 Friedman χ²=552.91→392.47、HV δ −0.58→−0.22、p 1e-14→1e-5（EN+ZH 已补）。verify 是防止"主数据重跑后论文段漏同步"的最后防线。

**figures**：fig1-4 重生成（新数据，编译通过），fig5 待消融完。

**phenomenon2_cliff**：compute_phenomenon2_cliff.py 改读新 progress，重算（f3 Cliff S1 0.84/S4 0.2）。

**消融断点**：112/113/115 后台续跑（未杀），预计过夜。2 verify fail 待消融完。

**待消融完**：variant-D 论文段（热启动对照值需消融表）、corr-D 断言、fig5 重生成、verify 全绿、提交。

关联 rdr066-newcaliber-correlation-collapse-20260813 objective-change-requires-downstream-recompute