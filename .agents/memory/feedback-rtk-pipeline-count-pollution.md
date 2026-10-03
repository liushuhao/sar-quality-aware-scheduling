---
name: feedback-rtk-pipeline-count-pollution
description: rtk wrapper 噪声行污染管道 wc 计数——判数必须用裸命令
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4dfc6beb-03be-462e-b7d4-5951b6f61bd8
  modified: 2026-09-25T05:55:55.746Z
---

rtk hook 会向 stdout 注入 `[rtk] /!\ ...` 状态行。任何 `命令 | wc -l` 会把噪声行计入，产生假计数（实例：`git log origin/main..HEAD | wc -l` 报 1，裸命令实为 0 推净）。本会话咬两次。

**Why:** 假计数直接造成状态误判（已推净被报未推净）；rtk 行只在部分命令出现，间歇性更隐蔽。

**How to apply:** 凡「判数/判空」目的：① 用裸命令肉眼看输出（`git status --porcelain`、`git log A..B --oneline`）；② 必须管道时先 `grep -v rtk` 再数；③ `rev-parse A B` 比对 SHA 是免管道的铁证手段。适用所有 Git Bash 会话（rtk 为用户级配置）。
