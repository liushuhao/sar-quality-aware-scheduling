#!/usr/bin/env python3
"""N13 measurement (panel 2026-11-07 R3-03; R153 G-BL arm added 2026-11-09):
mean acquisition delay of the knee-point schedules relative to
earliest-feasible placement.

Post-hoc statistic over saved records -- no new solver runs. For each scenario
the instance is rebuilt with the runner-identical constants, and the delay of
each scheduled observation is t_actual_start - task.t_earliest (epoch
seconds), where t_earliest is the earliest start across ALL of the task's
windows (types.py).

G-BL IS measured (R153): the old claim "delay 0 by construction" was false.
Two mechanisms delay G-BL placements -- (i) the C2 fixed-point loop pushes a
start inside its window when the attitude transition from the previous
observation is infeasible (baselines.py), and (ii) the greedily selected window
need not be the task's earliest window. A 500-scenario probe found 69.5% of
G-BL observations delayed (23388/33661); G-BL is therefore emitted as a regular
arm, and its measured per-class means are the reference the knee schedules
are compared against.

Output: per-density-class mean+/-SD (across scenarios) of the per-scenario
mean delay, for MOEA-2, MOEA-3 knee schedules and G-BL, the MOEA-3-vs-G-BL
knee delta, and arm sizes.
"""
import json, pickle, sys
from pathlib import Path
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from sar_sim.solver.types import build_agile_instance_from_scenario
from sar_sim.solver.baselines import baseline_b1

PROJECT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RES = PROJECT / "experiments" / "results"
SLEW_RATE = 0.0524
SETTLE_TIME = 5.0


def load_completed(results_dir):
    return json.load(open(results_dir / "_progress.json", encoding="utf-8"))["completed"]


def schedule_delay(t_actuals, selected, instance):
    """Per-scenario mean delay under the shared t_earliest convention."""
    delays = [t_actuals[k] - instance.tasks[i].t_earliest
              for k, i in enumerate(selected)]
    if not delays:
        return None
    return float(np.mean(delays))


def gbl_delay(data, instance):
    """Recompute deterministic G-BL and score its delay the same way."""
    result = baseline_b1(data["windows"], data["targets"],
                         max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
                         instance=instance)
    tid2i = {t.target_id: i for i, t in enumerate(instance.tasks)}
    delays = [o.t_actual_start.timestamp()
              - instance.tasks[tid2i[o.window.target_id]].t_earliest
              for o in result.schedule]
    if not delays:
        return None
    return float(np.mean(delays))


def main():
    m3 = load_completed(RES / "moea_3obj")
    m2 = load_completed(RES / "moea_2obj")
    keys = sorted(set(m3.keys()) & set(m2.keys()))
    by_class = {}
    for key in keys:
        cls = key.split("/")[0]
        pkl = SCENARIOS_DIR / key
        if not pkl.is_file():
            continue
        with open(pkl, "rb") as f:
            data = pickle.load(f)
        instance = build_agile_instance_from_scenario(
            data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
        row = by_class.setdefault(
            cls, {"MOEA-3": [], "MOEA-2": [], "G-BL": []})
        d3 = schedule_delay(m3[key]["t_actuals"], m3[key]["selected"], instance)
        d2 = schedule_delay(m2[key]["t_actuals"], m2[key]["selected"], instance)
        dg = gbl_delay(data, instance)
        if d3 is not None:
            row["MOEA-3"].append(d3)
        if d2 is not None:
            row["MOEA-2"].append(d2)
        if dg is not None:
            row["G-BL"].append(dg)

    out = {"reference": ("G-BL measured post-hoc via deterministic baseline_b1 "
                         "recomputation (R153, 2026-11-09): delay 0 is not "
                         "guaranteed -- C2 in-window push and non-earliest "
                         "window selection; G-BL is the measured reference arm"),
           "unit": "s", "n_by_class": {}, "class_mean_delay": {}}
    for cls in sorted(by_class):
        row = by_class[cls]
        out["n_by_class"][cls] = {a: len(v) for a, v in row.items()}
        out["class_mean_delay"][cls] = {
            a: {"mean": float(np.mean(v)), "sd": float(np.std(v, ddof=1))}
            for a, v in row.items()}
        cm = out["class_mean_delay"][cls]
        cm["delta_3_minus_2"] = float(
            np.mean(row["MOEA-3"]) - np.mean(row["MOEA-2"]))
        cm["knee_minus_gbl"] = float(
            np.mean(row["MOEA-3"]) - np.mean(row["G-BL"]))

    for cls in sorted(out["class_mean_delay"]):
        cm = out["class_mean_delay"][cls]
        print("%s n=%s  MOEA-3 %.0f±%.0f s  MOEA-2 %.0f±%.0f s  G-BL %.0f±%.0f s  "
              "knee−G-BL=%.0f s  Δ(3−2)=%.0f s" % (
                  cls, out["n_by_class"][cls]["MOEA-3"],
                  cm["MOEA-3"]["mean"], cm["MOEA-3"]["sd"],
                  cm["MOEA-2"]["mean"], cm["MOEA-2"]["sd"],
                  cm["G-BL"]["mean"], cm["G-BL"]["sd"],
                  cm["knee_minus_gbl"], cm["delta_3_minus_2"]))

    dst = RES / "acquisition_delay_analysis.json"
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("saved: %s" % dst)


if __name__ == "__main__":
    main()
