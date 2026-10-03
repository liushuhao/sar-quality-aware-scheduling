---
name: feedback-no-config-change-during-long-batch
description: 长耗时后台批跑期间禁止改 ~/.claude/settings.json（hook/env），会触发 hermes 热重载/重启带死子进程
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 863a5c09-e7ff-404c-8313-76817689d703
  modified: 2026-08-05T23:12:14.946Z
---

长耗时 detached 批跑（schtasks 起的 python 实验/编译/训练）进行期间，**不要修改 `~/.claude/settings.json`**——尤其 hooks、env、plugin 配置。配置变更会触发 hermes 桌面代理重启（两个 `hermes_cli.main serve` 进程同时重新拉起），把同登录会话里的子进程一起带死，即使是 schtasks 启动的也不例外（默认凭据任务仍在用户登录会话内，非独立 session 0）。

**Why:** 2026-08-06 06:35，MOEA-3+三消融批跑（98/200）期间我修了 settings.json 里 RTK hook 的 rtk 绝对路径，保存后 hermes 在 06:35:06/07 重启，launcher PID 20236 + runner PID 21092 双双死亡，进度停在 06:48 写盘点。schtasks 默认 /RU 当前用户不能隔离会话重启；要真正脱离需 `/RU SYSTEM`（管理员权限）或开机任务。

**How to apply:**
- 启动长批跑**之前**把所有 hook/env/settings 改动做完、验证好；批跑期间只读不写 settings.json、.claude/ 配置、插件开关。
- 若批跑期间必须改配置：先确认能接受子进程被杀，改完立即重启批跑（runner 有增量落盘 + resume，数据不丢但浪费已算时间）。
- 对绝对不能中断的任务（>2h、一次性），用管理员权限 `schtasks /Create /RU SYSTEM` 或独立的 Task Scheduler "不管用户是否登录都运行"任务，跑在 session 0 不受桌面/hermes 重启影响。
- 与 [[feedback-long-task-checkpointing]] 互补：那条解决启动方式（schtasks > Start-Process），这条解决运行期禁动配置。
