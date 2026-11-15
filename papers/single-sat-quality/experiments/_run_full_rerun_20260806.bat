@echo off
REM Full consistency rerun after window fix c91d398 (2026-08-06).
REM Launched via schtasks so the process survives terminal restarts.
cd /d "%~dp0"
echo started %DATE% %TIME% > logs\full_rerun_20260806.master.log
python _full_rerun_20260806.py >> logs\full_rerun_20260806.master.log 2>&1
echo exit=%ERRORLEVEL% %DATE% %TIME% >> logs\full_rerun_20260806.master.log
