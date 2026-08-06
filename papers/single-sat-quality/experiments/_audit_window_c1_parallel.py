"""Parallel continuous-C1 window audit. Samples 10 scenarios per group first
to get a quick scope estimate; if violation rate is meaningful, run full."""
import pickle, sys, glob, os
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
import multiprocessing as mp

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry, compute_full_attitude
from sar_sim.metrics.nesz import off_nadir_to_incidence

PAPER = REPO / "papers/single-sat-quality"
SCEN = PAPER / "experiments/scenarios"
DURATION = 30.0
SCAN_STEP = 0.5
SLEW, SETTLE = 0.0524, 5.0

def audit_scen(pkl_path):
    data = pickle.load(open(pkl_path, "rb"))
    alt = float(data.get("satellite", {}).get("altitude_km", 693.0)) * 1000.0
    inst = build_agile_instance_from_scenario(data, max_slew_rate=SLEW, settle_time=SETTLE, altitude_m=alt)
    precompute_geometry(inst, step_s=10.0)
    theta_min = off_nadir_to_incidence(inst.phi_min, inst.altitude_m)
    tid2idx = {t.target_id: i for i, t in enumerate(inst.tasks)}
    out = {"n_windows": 0, "n_viol": 0, "viol_lens": [], "pos": Counter(),
           "unhostable": 0, "trim_lens": []}
    for w in data.get("windows", []):
        out["n_windows"] += 1
        ti = tid2idx.get(w.target_id)
        if ti is None: continue
        task = inst.tasks[ti]
        w_start = w.t_start.timestamp() if hasattr(w.t_start, "timestamp") else w.t_start
        w_end = w.t_end.timestamp() if hasattr(w.t_end, "timestamp") else w.t_end
        ts = np.arange(w_start, w_end, SCAN_STEP)
        if len(ts) < 2: continue
        thetas = np.empty(len(ts))
        for k, tt in enumerate(ts):
            roll, _, _ = compute_full_attitude(task, float(tt), 1.0, inst)
            thetas[k] = off_nadir_to_incidence(abs(roll), inst.altitude_m)
        viol = thetas < theta_min
        if not viol.any(): continue
        out["n_viol"] += 1
        idx = np.where(viol)[0]
        runs = []; start = idx[0]; prev = idx[0]
        for k in idx[1:]:
            if k == prev+1: prev = k
            else: runs.append((start,prev)); start=k; prev=k
        runs.append((start,prev))
        for (a,b) in runs:
            out["viol_lens"].append((b-a)*SCAN_STEP+SCAN_STEP)
            if a <= 2: out["pos"]["head"] += 1
            elif b >= len(ts)-3: out["pos"]["tail"] += 1
            else: out["pos"]["interior"] += 1
        if runs and runs[-1][1] >= len(ts)-3:
            nonviol = np.where(~viol)[0]
            pre = nonviol[nonviol < runs[-1][0]]
            if len(pre):
                last_good = pre.max()
                trimmed_end = ts[last_good]
                out["trim_lens"].append(w_end - trimmed_end)
                if trimmed_end - w_start < DURATION:
                    out["unhostable"] += 1
    return out

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=0, help="0=all, else N per group")
    ap.add_argument("--jobs", type=int, default=mp.cpu_count())
    a = ap.parse_args()
    groups = ["S1","S2","S3","S4"]
    files = []
    for g in groups:
        fs = sorted(SCEN.glob(f"{g}/*.pkl"))
        if a.sample > 0:
            fs = fs[:a.sample] if len(fs) > a.sample else fs
        files.extend(fs)
    print(f"auditing {len(files)} scenarios with {a.jobs} workers...", flush=True)
    with mp.Pool(a.jobs) as pool:
        results = pool.map(audit_scen, files)
    agg = defaultdict(lambda: {"n_windows":0,"n_viol":0,"viol_lens":[],"pos":Counter(),"unhostable":0,"trim_lens":[]})
    for fp, r in zip(files, results):
        g = fp.stem.split("_")[0] if "_" in fp.stem else fp.parent.name
        g = fp.parent.name
        s = agg[g]
        s["n_windows"] += r["n_windows"]; s["n_viol"] += r["n_viol"]
        s["viol_lens"].extend(r["viol_lens"]); s["pos"].update(r["pos"])
        s["unhostable"] += r["unhostable"]; s["trim_lens"].extend(r["trim_lens"])
    print("="*80)
    print(f"{'grp':<5}{'wins':>7}{'viol':>6}{'%':>6}  {'len[min/med/max]':<20}  H/T/I      unhost")
    totw=totv=0; totunhost=0; alltrim=[]
    for g in groups:
        s=agg[g]; vl=s["viol_lens"]
        vls=f"{min(vl):.1f}/{np.median(vl):.1f}/{max(vl):.1f}" if vl else "-"
        pct=100*s["n_viol"]/s["n_windows"] if s["n_windows"] else 0
        p=s["pos"]
        print(f"{g:<5}{s['n_windows']:>7}{s['n_viol']:>6}{pct:>5.1f}%  {vls:<20}  {p['head']}/{p['tail']}/{p['interior']:<7} {s['unhostable']:>5}")
        totw+=s["n_windows"]; totv+=s["n_viol"]; totunhost+=s["unhostable"]; alltrim+=s["trim_lens"]
    print(f"\nTOTAL windows={totw} viol={totv} ({100*totv/totw:.1f}%)  unhostable-after-trim={totunhost}")
    if alltrim:
        print(f"trim (s): min={min(alltrim):.1f} med={np.median(alltrim):.1f} max={max(alltrim):.1f}")
