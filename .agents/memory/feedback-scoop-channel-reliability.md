---
name: feedback-scoop-channel-reliability
description: 查新抓取通道可靠性清单（2026-09-26 实测）——tavily/exa 活、stepfun 无订阅死、webReader 对编码URL/直链PDF 挂、Google Patents 只能 tavily 抓、curl -o 前先 mkdir
metadata:
  node_type: memory
  type: feedback
  originSessionId: e3fae2af-fadc-43a2-b6a1-7e3b5553f547
  modified: 2026-09-26T09:39:44.077Z
---

2026-09-26 step10 三族+中文查新实测通道状态：

- **活**：exa MCP（中英检索均可，中文期刊官网内容可直击）、tavily MCP（含 include_domains 域限定；**Google Patents 全文抓取唯一成功通道**——curl 与 WebFetch 均被拒/域校验失败）
- **死**：stepfun MCP（"no active step plan subscription"，无订阅）；webReader MCP（对含 %20 的检索 URL 报 -400 格式错、对直链 PDF 报 500）；WebFetch（patents.google.com 域校验失败）；curl 直连 Google Patents（两次拒）
- **万方/知网专业检索**（`*` 算子）无登录态不可达，等价做法 = 全域中文检索 + 期刊官网直击（宇航学报/电子与信息学报/系统仿真学报 PDF/HTML 可直达）
- **环境**：conda 不在 Git Bash PATH，agent-reach 直接可用；agent-reach check-update 网络失败（同 GitHub release 直连被阻策略）

**Why:** 一次查新连踩 5 个通道故障，逐个试错浪费轮次；教训 = 调研类任务先按此清单选通道，失败即弃不重试（重试无效例：curl 换 UA 仍拒）。

**How to apply:** 查新/抓取任务开工按「tavily 主 + exa 备 + 期刊官网直击」配通道；专利全文走 tavily；`curl -o` 深路径前先 `mkdir -p`（本次踩：目录不存在 exit 1）；会话产物直接写正式位置（`literature/fulltext/`），TEMP 只作中转即刻迁移（本次用户问出「是否落盘」才发现 TEMP 残留）。
