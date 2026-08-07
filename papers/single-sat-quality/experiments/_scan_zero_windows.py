#!/usr/bin/env python3
"""Quantify zero-window grid-resolution artifacts across all 400 scenarios.

For every target whose pkl windows are ALL zero-duration (caused by a single
10s-grid sample passing in a short pass), rescan that target at 5s and 1s
with the SAME instrument params the pkl was generated with, and count how
many recover a non-zero window long enough for a 30s observation.

Does not modify any pkl. Read-only diagnostic.
"""
import pickle, sys, time, glob, os
from datetime import timedelta
from collections import defaultdict
from pathlib import Path
import multiprocessing as mp

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_all_scenarios import make_orbit, compute_batch_visibility, SENTINEL1
from sar_sim.types import SARInstrument

EXP = Path(__file__).resolve().parent
SCEN = EXP / "scenarios"
OBS_DURATION_S = 30.0  # a window is "usable" only if >= this

def instrument_for(scen_path: Path):
    """Reconstruct instrument from scenario naming. Only S4-D uses tight [18,25];
    everything else is standard SENTINEL1 [18,47]. Verified: current code
    reproduces pkl windows bit-for-bit with these params."""
    name = scen_path.parent.name + "/" + scen_path.name
    inc_max = 25.0 if name.startswith("S4/S4-D") else SENTINEL1["incidence_max"]
    return SARInstrument(
        incidence_min=SENTINEL1["incidence_min"], incidence_max=inc_max,
        look_direction="both", antenna_type="reflector", min_elevation=5.0)

def scan_one(pkl_path):
    d = pickle.load(open(pkl_path, "rb"))
    cfg = d["config"]; alt = float(d["satellite"]["altitude_km"])
    orbit = make_orbit(alt, ltan=6.0, epoch=cfg["t_start"])
    instr = instrument_for(Path(pkl_path))
    by_t = defaultdict(list)
    for w in d["windows"]:
        by_t[w.target_id].append(w)
    only_zero = [t for t, ws in by_t.items()
                 if all((x.t_end - x.t_start).total_seconds() == 0 for x in ws)]
    if not only_zero:
        cls = os.path.basename(os.path.dirname(pkl_path))
        return cls, 0, 0, 0, 0, 0, 0.0
    targets_by_id = {t.target_id: t for t in d["targets"]}
    sel = [targets_by_id[t] for t in only_zero if t in targets_by_id]
    out = {"pkl_zero": len(only_zero)}
    for step_s in (10, 5, 1):
        wd = compute_batch_visibility(
            orbit, "SAT-01", sel, instr, cfg["t_start"], cfg["t_end"],
            timedelta(seconds=step_s), alt, max_window_width_s=None)
        n_recovered = 0; usable_dur = 0.0; max_dur = 0.0
        for tid in only_zero:
            wins = wd.get(tid, [])
            durs = [(w.t_end - w.t_start).total_seconds() for w in wins]
            if any(x > 0.5 for x in durs):
                n_recovered += 1
            best = max(durs) if durs else 0.0
            if best >= OBS_DURATION_S:
                usable_dur += 1
            max_dur = max(max_dur, best)
        out[step_s] = (n_recovered, usable_dur, max_dur)
    cls = os.path.basename(os.path.dirname(pkl_path))
    return (cls, len(only_zero),
            out[5][0], out[5][1], out[1][0], out[1][1],
            out[1][2])

def main():
    pkls = sorted(glob.glob(str(SCEN / "S*" / "*.pkl")))
    print(f"scanning {len(pkls)} scenarios (only-zero targets at 5s/1s)...", flush=True)
    t0 = time.time()
    agg = defaultdict(lambda: {"scen": 0, "oz": 0,
                               "rec5": 0, "use5": 0,
                               "rec1": 0, "use1": 0, "max1": 0.0})
    with mp.Pool(6) as pool:
        for i, row in enumerate(pool.imap_unordered(scan_one, pkls), 1):
            cls, oz, r5, u5, r1, u1, m1 = row
            a = agg[cls]; a["scen"] += 1; a["oz"] += oz
            a["rec5"] += r5; a["use5"] += u5; a["rec1"] += r1; a["use1"] += u1
            a["max1"] = max(a["max1"], m1)
            if i % 40 == 0:
                print(f"  {i}/{len(pkls)} ({time.time()-t0:.0f}s)", flush=True)
    print(f"\n{'class':<6}{'scen':>5}{'only-zero':>10}{'rec@5s':>9}{'usable@5s':>11}"
          f"{'rec@1s':>9}{'usable@1s':>11}{'max1s':>8}")
    tot = defaultdict(int); tot["max1"] = 0.0
    for cls in sorted(agg):
        a = agg[cls]
        print(f"{cls:<6}{a['scen']:>5}{a['oz']:>10}{a['rec5']:>9}{a['use5']:>11}"
              f"{a['rec1']:>9}{a['use1']:>11}{a['max1']:>8.0f}")
        for k in ("scen", "oz", "rec5", "use5", "rec1", "use1"):
            tot[k] += a[k]
        tot["max1"] = max(tot["max1"], a["max1"])
    print(f"{'TOT':<6}{tot['scen']:>5}{tot['oz']:>10}{tot['rec5']:>9}{tot['use5']:>11}"
          f"{tot['rec1']:>9}{tot['use1']:>11}{tot['max1']:>8.0f}")
    print(f"\n'rec' = targets regaining a >0.5s window at finer grid")
    print(f"'usable' = of those, max window >= {OBS_DURATION_S:.0f}s (fits one observation)")
    print(f"elapsed {time.time()-t0:.0f}s")

if __name__ == "__main__":
    main()
