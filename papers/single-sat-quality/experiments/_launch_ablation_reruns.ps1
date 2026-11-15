$Exp = 'D:\hermes\my-workspace\projects\planning-paper\papers\single-sat-quality\experiments'
$Logs = "$Exp\logs"
Start-Process -FilePath python -ArgumentList 'run_moea_3obj_no_incidence.py' -WorkingDirectory $Exp -RedirectStandardOutput "$Logs\noinc_rdr066_20260813.log" -RedirectStandardError "$Logs\noinc_rdr066_20260813_err.log" -WindowStyle Hidden
Start-Process -FilePath python -ArgumentList 'run_moea_3obj_no_physics.py' -WorkingDirectory $Exp -RedirectStandardOutput "$Logs\nophys_rdr066_20260813.log" -RedirectStandardError "$Logs\nophys_rdr066_20260813_err.log" -WindowStyle Hidden
Start-Process -FilePath python -ArgumentList 'run_moea_3obj_no_squint.py' -WorkingDirectory $Exp -RedirectStandardOutput "$Logs\nosq_rdr066_20260813.log" -RedirectStandardError "$Logs\nosq_rdr066_20260813_err.log" -WindowStyle Hidden
Start-Sleep -Seconds 5
Write-Host "launched 3 ablation reruns"
