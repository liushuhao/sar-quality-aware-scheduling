@echo off
cd /d "%~dp0.."
.venv\Scripts\python experiments\run_moea_3obj_no_physics.py --groups S4 >> experiments\results\moea_3obj_no_physics\_run.log 2>&1
