"""Launch GA-P-BL, MOEA-2, MOEA-3 as detached background processes.

Each solver runs independently, writing to its own _progress.json.
This script exits immediately after spawning; the solvers continue.
"""
import subprocess, sys, os
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
VENV_PYTHON = PROJECT / ".venv" / "Scripts" / "python.exe"
EXPERIMENTS = PROJECT / "experiments"

SOLVERS = [
    ("GA-P-BL", "run_so_f1_bl.py", ["--no-resume"]),
    ("MOEA-2",  "run_moea_2obj.py",  ["--no-resume"]),
    ("MOEA-3",  "run_moea_3obj.py",  ["--no-resume"]),
]

CREATE_NEW_CONSOLE = 0x00000010  # new console window (mutually exclusive with DETACHED)

procs = []
for name, script, args in SOLVERS:
    cmd = [str(VENV_PYTHON), str(EXPERIMENTS / script)] + args
    print(f"[{name}] Launching: {' '.join(cmd)}")
    p = subprocess.Popen(
        cmd,
        cwd=str(PROJECT),
        creationflags=CREATE_NEW_CONSOLE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )
    procs.append((name, p))
    print(f"  PID: {p.pid}")

print(f"\nAll {len(procs)} solvers launched. This script exiting — solvers continue in background.")
print("Monitor:")
print(f"  GA-P-BL: {PROJECT / 'experiments' / 'results' / 'b2_profit_bl' / '_progress.json'}")
print(f"  MOEA-2:  {PROJECT / 'experiments' / 'results' / 'moea_2obj' / '_progress.json'}")
print(f"  MOEA-3:  {PROJECT / 'experiments' / 'results' / 'moea_3obj' / '_progress.json'}")
