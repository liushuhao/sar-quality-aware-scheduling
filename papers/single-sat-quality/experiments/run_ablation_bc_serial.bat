@echo off
REM Run remaining ablation B and C serially, detaching from Hermes.
REM Logs to file. Auto-resume.
cd /d "%~dp0.."

echo === B start: %date% %time% >> experiments\results\moea_3obj_no_squint\_bg.log
.venv\Scripts\python experiments\run_moea_3obj_no_squint.py >> experiments\results\moea_3obj_no_squint\_bg.log 2>&1
echo === B end: %date% %time% >> experiments\results\moea_3obj_no_squint\_bg.log

echo === C start: %date% %time% >> experiments\results\moea_3obj_no_incidence\_bg.log
.venv\Scripts\python experiments\run_moea_3obj_no_incidence.py >> experiments\results\moea_3obj_no_incidence\_bg.log 2>&1
echo === C end: %date% %time% >> experiments\results\moea_3obj_no_incidence\_bg.log

echo === DONE
