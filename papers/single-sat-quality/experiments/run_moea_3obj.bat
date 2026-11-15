@echo off
REM Run MOEA-3 solver (3-objective NSGA-III: f1+f2+f3)
REM Output: experiments/results/moea_3obj/_progress.json
cd /d "%~dp0.."
echo [MOEA-3] Start: %DATE% %TIME%
.venv\Scripts\python experiments/run_moea_3obj.py --no-resume
echo [MOEA-3] Done: %DATE% %TIME%
