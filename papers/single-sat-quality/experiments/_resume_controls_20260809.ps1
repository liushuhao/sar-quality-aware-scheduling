$Exp = 'D:\hermes\my-workspace\projects\planning-paper\papers\single-sat-quality\experiments'
$Logs = "$Exp\logs"
# resume hotstart control (S4 6->15; S1/S2/S3 complete)
Start-Process -FilePath python -ArgumentList 'run_hotstart_control_s1s4.py' -WorkingDirectory $Exp -RedirectStandardOutput "$Logs\hotstart_control_resume.log" -RedirectStandardError "$Logs\hotstart_control_resume_err.log" -WindowStyle Hidden
# resume sigma sweep (sigma0.3 7/10 + sigma0.5 + sigma0.7)
Start-Process -FilePath python -ArgumentList 'run_sigma_sweep.py --groups S3 --sigmas 0.1 0.3 0.5 0.7 --solvers moea_3obj --max-scenarios 10' -WorkingDirectory $Exp -RedirectStandardOutput "$Logs\sigma_sweep_resume.log" -RedirectStandardError "$Logs\sigma_sweep_resume_err.log" -WindowStyle Hidden
# resume random-init D (S4 14/15, 1 run left)
Start-Process -FilePath python -ArgumentList '..\scripts\run_variant_d_random_init.py' -WorkingDirectory $Exp -RedirectStandardOutput "$Logs\random_init_d_resume.log" -RedirectStandardError "$Logs\random_init_d_resume_err.log" -WindowStyle Hidden
Start-Sleep -Seconds 5
Write-Host "launched 3 control resumes"
