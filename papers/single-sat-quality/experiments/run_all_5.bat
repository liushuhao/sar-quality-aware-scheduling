@echo off
REM ============================================================
REM  Master: Re-run all 5 solvers (fresh data, no ablation)
REM  Run from project root (%~dp0..)
REM
REM  Stages:
REM    1. Cleanup old data (backup, not delete)
REM    2. Baselines (G-BL + G-SM) — ~2 min
REM    3. GA-P-BL — ~60-120 min
REM    4. MOEA-2 (2obj) — ~4-8 hr
REM    5. MOEA-3 (3obj) — ~6-10 hr
REM
REM  All output piped to experiments/logs/ with timestamps.
REM  Each stage logs to its own file for progress monitoring.
REM ============================================================
setlocal enabledelayedexpansion

set PROJECT=%~dp0..
set VENV=%PROJECT%\.venv\Scripts\python
set LOGDIR=%PROJECT%\experiments\logs

cd /d %PROJECT%
mkdir %LOGDIR% 2>nul

echo ============================================================
echo  HERMES — Full Solver Re-run (5 solvers)
echo  Start: %DATE% %TIME%
echo ============================================================

REM ── Stage 0: Cleanup ─────────────────────────────────────────
echo.
echo [0/4] Cleaning up old data...
%VENV% experiments/cleanup_old_data.py > %LOGDIR%\cleanup_%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%.log 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   Cleanup FAILED — aborting
    exit /b 1
)
echo   Cleanup OK. Old files backed up.

REM ── Stage 1: Baselines ───────────────────────────────────────
echo.
echo [1/4] Running Baselines (G-BL + G-SM)...
echo  Start: %DATE% %TIME%
%VENV% experiments/run_baselines_v4.py > %LOGDIR%\baselines_%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%.log 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   Baselines FAILED — check log. Continuing anyway...
)
echo   Baselines DONE at %TIME%
type %LOGDIR%\baselines_*.log 2>nul | findstr /C:"complete" /C:"Scenarios"

REM ── Stage 2: GA-P-BL ─────────────────────────────────────────
echo.
echo [2/4] Running GA-P-BL...
echo  Start: %DATE% %TIME%
%VENV% experiments/run_so_f1_bl.py --no-resume > %LOGDIR%\ga_p_bl_%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%.log 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   GA-P-BL FAILED — check log
)
echo   GA-P-BL DONE at %TIME%

REM ── Stage 3: MOEA-2 ──────────────────────────────────────────
echo.
echo [3/4] Running MOEA-2 (2-objective NSGA-III)...
echo  Start: %DATE% %TIME%
%VENV% experiments/run_moea_2obj.py --no-resume > %LOGDIR%\moea_2obj_%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%.log 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   MOEA-2 FAILED — check log
)
echo   MOEA-2 DONE at %TIME%

REM ── Stage 4: MOEA-3 ──────────────────────────────────────────
echo.
echo [4/4] Running MOEA-3 (3-objective NSGA-III)...
echo  Start: %DATE% %TIME%
%VENV% experiments/run_moea_3obj.py --no-resume > %LOGDIR%\moea_3obj_%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%.log 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   MOEA-3 FAILED — check log
)
echo   MOEA-3 DONE at %TIME%

REM ── Done ─────────────────────────────────────────────────────
echo.
echo ============================================================
echo  ALL SOLVERS COMPLETE
echo  End: %DATE% %TIME%
echo  Logs: %LOGDIR%
echo ============================================================

REM Quick summary of output files
echo.
echo Output files:
dir /b experiments\results\baselines_200.json 2>nul && echo   ✓ baselines_200.json
dir /b experiments\results\b2_profit_bl\_progress.json 2>nul && echo   ✓ b2_profit_bl\_progress.json
dir /b experiments\results\moea_2obj\_progress.json 2>nul && echo   ✓ moea_2obj\_progress.json
dir /b experiments\results\moea_3obj\_progress.json 2>nul && echo   ✓ moea_3obj\_progress.json

endlocal
