@echo off
REM Register batch2 ablation schtasks (create only, do NOT run).
REM Fire manually after batch1 audit passes: schtasks /run /tn planningpaper_fi_abn_<name>
setlocal
set BATDIR=D:\hermes\my-workspace\projects\planning-paper\papers\single-sat-quality\experiments
schtasks /create /tn planningpaper_fi_abn_incidence /tr "cmd /c \"\"%BATDIR%\_resume_abn_incidence.bat\"\"" /sc once /st 23:59 /f
schtasks /create /tn planningpaper_fi_abn_physics /tr "cmd /c \"\"%BATDIR%\_resume_abn_physics.bat\"\"" /sc once /st 23:59 /f
schtasks /create /tn planningpaper_fi_abn_squint /tr "cmd /c \"\"%BATDIR%\_resume_abn_squint.bat\"\"" /sc once /st 23:59 /f
echo. & echo Registered 3 ablation tasks (not run). Fire with:
echo   schtasks /run /tn planningpaper_fi_abn_incidence
echo   schtasks /run /tn planningpaper_fi_abn_physics
echo   schtasks /run /tn planningpaper_fi_abn_squint