---
name: feedback-long-task-checkpointing
description: 长耗时脚本必须增量落盘 + 不用 tail 管道，否则看不到进度且中途崩全丢
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d89f53e7-4152-4a37-accc-25193061d82b
  modified: 2026-08-07T12:27:53.480Z
---

长任务（>30min、多阶段）的脚本设计与运行方式：

1. **增量落盘**：每个阶段/类别跑完就 append/写一次结果文件，不要全跑完才 dump。否则中途崩全丢，且外部无法读中间进度。
2. **不要用 `| tail` 跑后台长任务**：tail 是块缓冲，日志文件长时间 0 字节，看不见任何进度。直接重定向到文件（`> log 2>&1`）让 Python 的 flush/print 直写，或脚本内 `flush=True`。
3. 启动前加 `flush=True` / 每 N 条打印进度，这样外部 `cat` 日志能看到活。
4. **Claude Code 后台任务（run_in_background）不可靠**：2026-08-05 两次后台启动 MOEA-2 均 exit 127（shell 环境 PATH 差异）+ 一次随 hermes 服务重启被杀。**`Start-Process -WindowStyle Hidden` 也不可靠**：2026-08-05 21:14 用它 detached 起 MOEA-2，21:19 hermes 服务自重启（5 进程同时拉起、WinDivert 驱动重装、SCM 7045），该 detached 子进程仍被带死。**改用 Windows 计划任务（schtasks）**，进程脱离 hermes 进程树，hermes 重启杀不到；2026-08-05 21:20 起的 MOEA-2 用此法全程未断，300/300 干净跑完：
   ```bash
   # 1) 写 .bat（cd /d 工作目录 + 重定向日志），然后：
   powershell -Command "schtasks /Create /TN '<name>' /TR 'cmd.exe /c <abs>.bat' /SC ONCE /ST 23:59 /F"
   powershell -Command "schtasks /Run /TN '<name>'"
   ```
   查活：`Get-CimInstance Win32_Process -Filter "Name='python.exe'" | ? CommandLine -match '<script>'`。**注意**：/RU SYSTEM 需管理员权限会被拒；默认当前用户即可。不要用 `/ST 00:00`（报"早于当前时间无效"）。
5. **批量写盘模式**：runner 每 N 条才写一次 `_progress.json` → 进度"看似停滞"（连续两次相同）实际 CPU 满负荷。判断停滞先查 CPU，别急着杀进程。
6. **schtasks 跑 .bat 手关黑窗口 = CTRL_C_EVENT**：直接 `cmd /c run.bat` 弹窗时用户手关窗口，Python 收到 0xC000013A 退出（看似正常退出码）。.bat 里用 `< NUL` 重定向 stdin 只防 stdin 关闭，防不住手关窗口；真要不弹框被误关，用 `Start-Process -WindowStyle Hidden`（但仍受 hermes 重启带死，见 [[feedback-no-config-change-during-long-batch]]）或 schtasks（脱离进程树）。
7. **Claude Code 后台任务（run_in_background / bash `&`）会清理子进程树**（2026-08-07 实测）：`bash launcher.sh &` 里 `wait` 的子 runner，等 master log 一写 "all finished"（实际是被杀）就全死，progress 停在 20-28 条，无 "complete" 收尾行。**在 Claude Code 里要脱离启动长任务，用 PowerShell `Start-Process -WindowStyle Hidden` 且命令直接返回**（不套 bash `&`、不用 run_in_background 包一层）。2026-08-07 三族各 20s/场景，Start-Process 脱离后 4+ 分钟仍存活、progress 持续落盘。**在 hermes 环境才需要 schtasks**（记忆第 4 条）；Claude Code 环境 schtasks 反而复杂。判活/杀进程：`Get-CimInstance Win32_Process -Filter "Name='python.exe'" | ? CommandLine -match '<script>'`。
8. **诊断/审计脚本别用 run_in_background 叠加 bash `&`**：2026-08-07 审计脚本两次空跑（cwd 漂移、进程秒退无报错），Windows `mp.Pool` 在模块顶层还缺 `if __name__=='__main__'` 守卫会 spawn 递归崩。诊断脚本用前台单进程跑，或 Start-Process 脱离 + 显式重定向。

**Why**：2026-08-01 跑变体 D S2-S4 重算（~2.7h），脚本三类别全跑完才写 JSON，又用 `| tail` 启动，导致近 1 小时里既看不到进程输出、文件也停在 S1，只能干等无法判断是否卡住。与 [[bash-classifier-backend-gotcha]] 和全局 CLAUDE.md 里 2026-07-26 下载复盘同源——后台/长任务的可见性与落盘必须设计进去，不能事后赌。

**How to apply**：写任何多阶段长脚本时，阶段循环末尾 `json.dump(partial)` 落盘；Bash 后台跑用 `> file 2>&1` 而非 `| tail`；进度打印 `flush=True`。
