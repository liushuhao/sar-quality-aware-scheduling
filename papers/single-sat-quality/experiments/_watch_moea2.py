#!/usr/bin/env python3
"""Poll MOEA-2 progress every N seconds; print a line when the count changes."""
import json, time, sys, os
from pathlib import Path

PROG = Path("experiments/results/moea_2obj/_progress.json")
interval = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0

last = -1
while True:
    try:
        d = json.load(open(PROG))
        c = d.get("completed", {})
        n = len(c)
        if n != last:
            from collections import Counter
            g = dict(Counter(k.split("/")[0] for k in c))
            print(f"[{time.strftime('%H:%M:%S')}] {n}/300 {g}", flush=True)
            last = n
        if n >= 300:
            print("MOEA-2 COMPLETE", flush=True)
            break
    except Exception as e:
        print(f"[watch] err {e}", flush=True)
    time.sleep(interval)
