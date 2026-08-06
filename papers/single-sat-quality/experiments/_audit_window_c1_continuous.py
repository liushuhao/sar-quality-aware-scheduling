"""Audit ALL visibility windows in ALL scenarios for continuous-C1 violations.

For each window, scan at 0.5s with continuous geometry (compute_full_attitude,
NOT geom_cache) and find segments where theta < theta_min (the global incidence
lower bound). Reports:
  - how many windows have ANY violating segment
  - violating-segment length distribution
  - whether the violating segment is at window tail / head / interior
  - whether, after removing the violating tail, the remaining window can still
    host a 30s observation (duration_min)

This establishes the true scope of the window-generation C1 prefilter defect
and the cost of the fix (regenerate scenarios + full rerun)."""
import pickle, sys, glob, os
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry, compute_full_attitude
from sar_sim.metrics.nesz import off_nadir_to_incidence

PAPER = REPO / "papers/single-sat-quality"
SCEN = PAPER / "experiments/scenarios"
DURATION = 30.0
SCAN_STEP = 0.5
SLEW, SETTLE = 0.0524, 5.0

groups = ["S1", "S2", "S3", "S4"]
stats = defaultdict(lambda: {
    "n_windows": 0, "n_viol_windows": 0,
    "viol_lens": [], "viol_pos": Counter(),
    "n_unhostable_after_tail_trim": 0,
    "trimmed_lens": [],
})

for g in groups:
    files = sorted(SCEN.glob(f"{g}/*.pkl"))
    for fp in files:
        data = pickle.load(open(fp, "rb"))
        alt = float(data.get("satellite", {}).get("altitude_km", 693.0)) * 1000.0
        inst = build_agile_instance_from_scenario(data, max_slew_rate=SLEW, settle_time=SETTLE, altitude_m=alt)
        precompute_geometry(inst, step_s=10.0)
        theta_min = off_nadir_to_incidence(inst.phi_min, inst.altitude_m)
        s = stats[g]
        # map target_id -> task_idx
        tid2idx = {t.target_id: i for i, t in enumerate(inst.tasks)}
        for w in data.get("windows", []):
            s["n_windows"] += 1
            ti = tid2idx.get(w.target_id)
            if ti is None: continue
            task = inst.tasks[ti]
            w_start = w.t_start.timestamp() if hasattr(w.t_start, "timestamp") else w.t_start
            w_end = w.t_end.timestamp() if hasattr(w.t_end, "timestamp") else w.t_end
            ts = np.arange(w_start, w_end, SCAN_STEP)
            if len(ts) < 2: continue
            thetas = []
            for tt in ts:
                roll, _, _ = compute_full_attitude(task, float(tt), 1.0, inst)
                thetas.append(off_nadir_to_incidence(abs(roll), inst.altitude_m))
            thetas = np.array(thetas)
            viol = thetas < theta_min
            if not viol.any():
                continue
            s["n_viol_windows"] += 1
            # find contiguous violating runs
            idx = np.where(viol)[0]
            runs = []
            start = idx[0]; prev = idx[0]
            for k in idx[1:]:
                if k == prev + 1: prev = k
                else: runs.append((start, prev)); start = k; prev = k
            runs.append((start, prev))
            for (a, b) in runs:
                run_len = (b - a) * SCAN_STEP + SCAN_STEP
                s["viol_lens"].append(run_len)
                # position: head if a near 0, tail if b near end, else interior
                if a <= 2: s["viol_pos"]["head"] += 1
                elif b >= len(ts) - 3: s["viol_pos"]["tail"] += 1
                else: s["viol_pos"]["interior"] += 1
            # tail-trim scenario: if violation is at tail, trim window end back to
            # last non-violating point; check if remaining can host 30s obs
            if runs and runs[-1][1] >= len(ts) - 3:
                last_good = runs[-1][0] - 1 if runs[-1][0] > 0 else 0
                # find the latest non-violating index before the tail run
                nonviol = np.where(~viol)[0]
                if len(nonviol):
                    last_good = nonviol[nonviol < runs[-1][0]].max() if (nonviol < runs[-1][0]).any() else nonviol[0]
                    trimmed_end = ts[last_good]
                    remaining = trimmed_end - w_start
                    s["trimmed_lens"].append(w_end - trimmed_end)
                    if remaining < DURATION:
                        s["n_unhostable_after_tail_trim"] += 1

print("="*78)
print(f"{'grp':<4}{'wins':>6}{'viol':>6}{'%':>6}  {'viol_len[min/med/max]':<26}  pos{head/tail/int}")
for g in groups:
    s = stats[g]
    vl = s["viol_lens"]
    vls = f"{min(vl):.1f}/{np.median(vl):.1f}/{max(vl):.1f}" if vl else "-"
    pct = 100*s["n_viol_windows"]/s["n_windows"] if s["n_windows"] else 0
    pos = s["viol_pos"]
    print(f"{g:<4}{s['n_windows']:>6}{s['n_viol_windows']:>6}{pct:>5.1f}%  {vls:<26}  H={pos['head']} T={pos['tail']} I={pos['interior']}")
print()
tot_w = sum(stats[g]["n_windows"] for g in groups)
tot_v = sum(stats[g]["n_viol_windows"] for g in groups)
print(f"TOTAL windows: {tot_w}, with C1-violating segment: {tot_v} ({100*tot_v/tot_w:.1f}%)")
tot_unhost = sum(stats[g]["n_unhostable_after_tail_trim"] for g in groups)
alltrim = sum((stats[g]["trimmed_lens"]) for g in groups)
print(f"Windows that become <30s (unhostable) after tail-trim: {tot_unhost}")
if alltrim:
    import numpy as _np
    print(f"tail-trim amounts (s): min={min(alltrim):.1f} med={_np.median(alltrim):.1f} max={max(alltrim):.1f}")
