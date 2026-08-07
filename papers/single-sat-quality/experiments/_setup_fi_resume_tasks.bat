@echo off
REM Register + fire the 3 full-interval resume scheduled tasks (schtasks survives hermes restarts).
setlocal
set BATDIR=D:\hermes\my-workspace\projects\planning-paper\papers\single-sat-quality\experiments
schtasks /create /tn planningpaper_fi_gapbl /tr "cmd /c \"\"%BATDIR%\_resume_fi_gapbl.bat\"\"" /sc once /st 23:59 /f
echo gapbl create exit=%ERRORLEVEL%
schtasks /create /tn planningpaper_fi_moea2 /tr "cmd /c \"\"%BATDIR%\_resume_fi_moea2.bat\"\"" /sc once /st 23:59 /f
echo moea2 create exit=%ERRORLEVEL%
schtasks /create /tn planningpaper_fi_moea3 /tr "cmd /c \"\"%BATDIR%\_resume_fi_moea3.bat\"\"" /sc once /st 23:59 /f
echo moea3 create exit=%ERRORLEVEL%

echo. & echo Launching...
schtasks /run /tn planningpaper_fi_gapbl
echo gapbl run exit=%ERRORLEVEL%
schtasks /run /tn planningpaper_fi_moea2
echo moea2 run exit=%ERRORLEVEL%
schtasks /run /tn planningpaper_fi_moea3
echo moea3 run exit=%ERRORLEVEL%