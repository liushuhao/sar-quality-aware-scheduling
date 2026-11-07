#!/usr/bin/env python3
"""N13 measurement (panel 2026-11-07 R3-03): mean acquisition delay of the
knee-point schedules relative to earliest-feasible placement.

Post-hoc statistic over saved records -- no new solver runs. For each scenario
the instance is rebuilt with the runner-identical constants, and the delay of
each scheduled observation is t_actual_start - task.t_earliest (epoch
seconds). G-BL is not measured: it places every task at its earliest feasible
time by construction (delay 0 is its definition, the reference itself).

Output: per-density-class mean+/-SD (across scenarios) of the per-scenario
mean delay, for MOEA-2 and MOEA-3 knee schedules, plus the arm-pair delta.
"""
import json, pickle, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from sar_sim.solver.types import build_agile_instance_from_scenario

PROJECT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RES = PROJECT / "experiments" / "results"
SLEW_RATE = 0.0524
SETTLE_TIME = 5.0


def load_completed(results_dir):
    return json.load(open(results_dir / "_progress.json", encoding="utf-8"))["completed"]


def scenario_delay(record, pkl_path):
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    instance = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
    delays = [record["t_actuals"][k] - instance.tasks[i].t_earliest
              for k, i in enumerate(record["selected"])]
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
        row = by_class.setdefault(cls, {"MOEA-3": [], "MOEA-2": []})
        for arm, prog in (("MOEA-3", m3), ("MOEA-2", m2)):
            d = scenario_delay(prog[key], pkl)
            if d is not None:
                row[arm].append(d)

    out = {"reference": "G-BL places earliest-feasible by construction (delay 0 = the reference)",
           "unit": "s", "n_by_class": {}, "class_mean_delay": {}}
    for cls in sorted(by_class):
        row = by_class[cls]
        out["n_by_class"][cls] = {a: len(v) for a, v in row.items()}
        out["class_mean_delay"][cls] = {
            a: {"mean": float(np.mean(v)), "sd": float(np.std(v, ddof=1))} for a, v in row.items()
        }
        out["class_mean_delay"][cls]["delta_3_minus_2"] = float(
            np.mean(row["MOEA-3"]) - np.mean(row["MOEA-2"]))

    for cls in sorted(out["class_mean_delay"]):
        cm = out["class_mean_delay"][cls]
        print("%s n=%s  MOEA-3 %.0f±%.0f s  MOEA-2 %.0f±%.0f s  Δ(3−2)=%.0f s" % (
            cls, out["n_by_class"][cls]["MOEA-3"],
            cm["MOEA-3"]["mean"], cm["MOEA-3"]["sd"],
            cm["MOEA-2"]["mean"], cm["MOEA-2"]["sd"], cm["delta_3_minus_2"]))

    dst = RES / "acquisition_delay_analysis.json"
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("saved: %s" % dst)


if __name__ == "__main__":
    main()
