@echo off
REM Run GA-P-BL solver (single-objective GA with G-BL hot-start)
REM Output: experiments/results/b2_profit_bl/_progress.json
cd /d "%~dp0.."
echo [GA-P-BL] Start: %DATE% %TIME%
.venv\Scripts\python experiments/run_so_f1_bl.py --no-resume
echo [GA-P-BL] Done: %DATE% %TIME%
