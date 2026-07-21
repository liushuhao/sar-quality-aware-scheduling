@echo off
REM Run Baselines (G-BL + G-SM) — fast, ~2 min
REM Output: experiments/results/baselines_200.json
cd /d "%~dp0.."
echo [Baselines] Start: %DATE% %TIME%
.venv\Scripts\python experiments/run_baselines_v4.py
echo [Baselines] Done: %DATE% %TIME%
