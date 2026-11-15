$Exp = 'D:\hermes\my-workspace\projects\planning-paper\papers\single-sat-quality\experiments'
$Logs = "$Exp\logs"
# 1. MOEA-2 main rerun (resume 176/400)
Start-Process -FilePath python -ArgumentList 'run_moea_2obj.py' -WorkingDirectory $Exp -RedirectStandardOutput "$Logs\moea2obj_rdr066_20260813.log" -RedirectStandardError "$Logs\moea2obj_rdr066_20260813_err.log" -WindowStyle Hidden
# 2. MOEA-3 main rerun (resume 176/300)
Start-Process -FilePath python -ArgumentList 'run_moea_3obj.py' -WorkingDirectory $Exp -RedirectStandardOutput "$Logs\moea3obj_rdr066_20260813.log" -RedirectStandardError "$Logs\moea3obj_rdr066_20260813_err.log" -WindowStyle Hidden
# 3. sigma sweep (old 90f7202c invalidated -> fresh, S3 x 10, both solvers)
Start-Process -FilePath python -ArgumentList 'run_sigma_sweep.py','--groups','S3','--sigmas','0.1','0.3','0.5','0.7','--solvers','moea_2obj','moea_3obj','--max-scenarios','10' -WorkingDirectory $Exp -RedirectStandardOutput "$Logs\sigma_rdr066_20260813.log" -RedirectStandardError "$Logs\sigma_rdr066_20260813_err.log" -WindowStyle Hidden
# 4. variant-D random-init control (old 08-11 invalidated -> fresh)
Start-Process -FilePath python -ArgumentList 'run_variant_d_random_init.py' -WorkingDirectory $Exp -RedirectStandardOutput "$Logs\variantd_rdr066_20260813.log" -RedirectStandardError "$Logs\variantd_rdr066_20260813_err.log" -WindowStyle Hidden
# 5. budget control (resume: S3-A done, continue S3-B..S4-E)
Start-Process -FilePath python -ArgumentList 'run_budget_control.py' -WorkingDirectory $Exp -RedirectStandardOutput "$Logs\budget_rdr066_20260813.log" -RedirectStandardError "$Logs\budget_rdr066_20260813_err.log" -WindowStyle Hidden
Start-Sleep -Seconds 5
Write-Host "launched 5 reruns"
