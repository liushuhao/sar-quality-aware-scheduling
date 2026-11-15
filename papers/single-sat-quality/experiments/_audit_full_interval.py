#!/usr/bin/env python3
"""Quantify start-OOW vs full-interval-OOW across completed families.

Start-OOW = t_actual not in any window (current audit check).
Full-OOW  = [t_actual, t_actual+duration] not fully inside any window.
The physical requirement is full-OOW=0; start check misses observations that
begin in a short window but extend past its end.
"""
import pickle, json, sys, os, time
from pathlib import Path
from collections import Counter
import multiprocessing as mp
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

EXP = Path(__file__).resolve().parent
DUR = 30.0

def _audit_one(args):
    key, e = args
    scen = EXP / "scenarios" / key
    if not scen.exists():
        return None
    d = pickle.load(open(scen, "rb"))
    inst = build_agile_instance_from_scenario(d, max_slew_rate=0.0524, settle_time=5.0)
    precompute_geometry(inst, step_s=10.0)
    sb = fb = 0
    for idx, tt in zip(e["selected"], e["t_actuals"]):
        w = inst.tasks[idx].window_times
        if not any(ws <= tt <= we for ws, we in w):
            sb += 1
        if not any(ws <= tt and tt + DUR <= we for ws, we in w):
            fb += 1
    return key, sb, fb, len(e["selected"])

def audit_progress(path, label):
    p = json.load(open(path, encoding="utf-8"))
    completed = p.get("completed", p)
    items = list(completed.items())
    with mp.Pool(6) as pool:
        results = [r for r in pool.imap_unordered(_audit_one, items) if r]
    start_bad = sum(r[1] for r in results)
    full_bad = sum(r[2] for r in results)
    nsel = sum(r[3] for r in results)
    bad_scen = [(r[0], r[1], r[2]) for r in results if r[2]]
    by_cls = Counter(k.split("/")[0] for k, *_ in bad_scen)
    print(f"\n=== {label}: {len(results)} scenarios, {nsel} observations ===")
    print(f"  start-OOW (current audit): {start_bad}")
    print(f"  full-interval-OOW (physical): {full_bad}")
    print(f"  scenarios with full-OOW: {len(bad_scen)}  by class: {dict(sorted(by_cls.items()))}")
    for k, sb, fb in bad_scen[:20]:
        print(f"    {k}: start={sb} full={fb}")

audit_progress(EXP / "results/b2_profit_bl/_progress.json", "GA-P-BL")
audit_progress(EXP / "results/moea_3obj/_progress.json", "MOEA-3")
