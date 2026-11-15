#!/usr/bin/env python3
"""Smoke rerun before the full consistency rerun (window fix c91d398).

Every solver family x {S1-A_seed00 (sparse), S3-A_seed00 (dense)} on the
REGENERATED 2026-08-06 scenario pkls. Dense tier is where constraints bind
(hot-start lesson), sparse tier is the regression control.

Reuses each runner's own run_one / run_scenario — the exact production
construction path, no parallel "correct version" (verify/run divergence is
the failure mode this avoids).

Output: results/_smoke_rerun_20260806/<family>.json  {scenario_key: record}
"""
import importlib
import json
import sys
import time
from pathlib import Path

EXP = Path(__file__).resolve().parent
sys.path.insert(0, str(EXP))
sys.path.insert(0, str(EXP.parents[1] / "src"))

FAMILIES = {
    "moea_2obj": "run_moea_2obj",
    "moea_3obj": "run_moea_3obj",
    "no_incidence": "run_moea_3obj_no_incidence",
    "no_physics": "run_moea_3obj_no_physics",
    "no_squint": "run_moea_3obj_no_squint",
    "ga_p_bl": "run_so_f1_bl",
    "baselines": "run_baselines_v4",
}
SCEN_KEYS = ["S1/S1-A_seed00.pkl", "S3/S3-A_seed00.pkl"]
OUT_DIR = EXP / "results" / "_smoke_rerun_20260806"


def work(task):
    fam, key = task
    t0 = time.time()
    try:
        mod = importlib.import_module(FAMILIES[fam])
        pkl = EXP / "scenarios" / key
        if fam == "baselines":
            rec = mod.run_scenario(pkl)
        else:
            rec = mod.run_one(pkl)
    except Exception as e:
        import traceback
        return fam, key, {"error": str(e), "tb": traceback.format_exc()[-800:]}, time.time() - t0
    return fam, key, rec, time.time() - t0


def save(fam, key, rec):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / f"{fam}.json"
    d = {}
    if p.exists():
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
    d[key] = rec
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1, default=str)


def main():
    import multiprocessing as mp
    tasks = [(f, k) for f in FAMILIES for k in SCEN_KEYS]
    ctx = mp.get_context("spawn")
    t_start = time.time()
    done = 0
    with ctx.Pool(min(7, len(tasks))) as pool:
        for fam, key, rec, dt in pool.imap_unordered(work, tasks):
            done += 1
            save(fam, key, rec)
            flag = ""
            if isinstance(rec, dict):
                if rec.get("error"):
                    flag = "  ERROR=" + str(rec["error"])[:80]
                elif "constraint_feasible" in rec and not rec["constraint_feasible"]:
                    flag = "  <<< INFEASIBLE"
            print(f"[{done:2d}/{len(tasks)}] {fam:14s} {key}  {dt:6.1f}s{flag}", flush=True)
    print(f"\nsmoke done in {time.time() - t_start:.0f}s -> {OUT_DIR}")


if __name__ == "__main__":
    main()
