@echo off
REM Run MOEA-2 solver (2-objective NSGA-III: f1+f2)
REM Output: experiments/results/moea_2obj/_progress.json
cd /d "%~dp0.."
echo [MOEA-2] Start: %DATE% %TIME%
.venv\Scripts\python experiments/run_moea_2obj.py --no-resume
echo [MOEA-2] Done: %DATE% %TIME%
