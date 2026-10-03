---
name: feedback-stale-snapshot-audit
description: 审稿/审计重算必须验证数据源版本（git_commit/caliber）——过期快照 _snapshot_final_*.json 制造假发现（R6 +0.89% 误报、δ=1.00 误报）
metadata: 
  node_type: memory
  type: feedback
  modified: 2026-08-16T15:54:30.345Z
  originSessionId: 80437aad-3378-4341-9ad9-02af7b57b953
---

外部审稿人/审计工具报告的数据差异，先验证它用的是哪个数据源、是否当前口径，再决定改不改。过期快照会制造假发现。

**Why**: 2026-08-15 ARS panel 数据侧发现大量基于 `_snapshot_final_moea_2obj.json`（ver=90de261f，RDR-066 前旧口径）重算：
- R6 声称 +10.8% 应改 +0.89%（读快照 seed08=1.0089）；当前权威 `_progress.json`（4cfc42c0）seed04=1.1081（+10.81%），**tex 原值正确**，差点改错。
- 声称 MOEA-3vs2 f3 δ=1.00（50/50 全正）；当前数据 δ=S1 0.88（47/50）/S4 0.32。§6.4 "coincide at S4"（均值 0.680 双方）实际成立。
- 教训：`_snapshot_final_*.json` 是中间/历史产物（P1-1 重跑后未重建），论文数字从 `_progress.json`（4cfc42c0）出。panel 重算路径与论文回源路径不一致 → 假发现。

**How to apply**:
- 任何跨 commit 的数据比较/审计/审稿重算：先看数据文件的 `solver_version`/`git_commit`/`pkl_sha1`，与当前 `_progress.json` 交叉核验。面板/审计声称的"数字对不上"先验它的数据源版本，不盲从也不盲改。
- 论文数字的权威源 = runner 的 `_progress.json`（带 caliber 指纹）+ verify gate 回源，不是 `_snapshot_*`（除非 rebuild_snapshot.py 重建过 gate 快照）。
- 同族：feedback-version-identity-content-not-head feedback-audit-tooling-staleness feedback-verify-catches-post-rerun-sync-gaps [[feedback-verify-hardcoded-numbers]]
