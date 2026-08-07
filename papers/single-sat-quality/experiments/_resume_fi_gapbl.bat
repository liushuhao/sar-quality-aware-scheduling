@echo off
REM Resume GA-P-BL full-interval rerun (code f1e55e5) after hermes restart.
REM Launched via schtasks so the process survives hermes restarts.
cd /d D:\hermes\my-workspace\projects\planning-paper\papers\single-sat-quality\experiments
"D:\Program Files\Python\python.exe" run_so_f1_bl.py --resume --groups S1 S2 S3 S4 >> logs\rerun_fi_resume_gapbl.log 2>&1
echo exit=%ERRORLEVEL% %DATE% %TIME% >> logs\rerun_fi_resume_gapbl.log