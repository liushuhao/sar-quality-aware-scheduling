@echo off
REM Batch2: ablation no_incidence, full-interval rerun (code f1e55e5+).
REM Launched via schtasks so the process survives hermes restarts.
cd /d D:\hermes\my-workspace\projects\planning-paper\papers\single-sat-quality\experiments
"D:\Program Files\Python\python.exe" run_moea_3obj_no_incidence.py --resume --groups S1 S2 S3 S4 >> logs\rerun_fi_resume_abn_incidence.log 2>&1
echo exit=%ERRORLEVEL% %DATE% %TIME% >> logs\rerun_fi_resume_abn_incidence.log