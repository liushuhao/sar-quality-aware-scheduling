@echo off
cd /d "%~dp0.."
.venv\Scripts\python experiments\run_moea_3obj_no_incidence.py --groups S4 >> experiments\results\moea_3obj_no_incidence\_run.log 2>&1
