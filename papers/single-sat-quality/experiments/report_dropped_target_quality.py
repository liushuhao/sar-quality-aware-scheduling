#!/usr/bin/env python3
"""R8 (panel 20261103 R2-02/DA-09): dropped-vs-retained achievable quality.

For every S1-S4 scenario, each target carries an achievable radiometric-quality
upper bound f3_max = cos^3(phi_min) (phi_min = lowest off-nadir reachable
within the task's visibility windows, best-NESZ end). Splitting targets into
retained (in the solver's `selected`) versus dropped gives the two
distributions DA-09 asks for: if dropped targets concentrate at low f3_max,
part of the mean-per-task quality gain is a selection effect, not an
imaging-quality improvement.

Solvers read from the main-run progress files (same result sets as
Table 1); instance build mirrors run_replicate_variance.py::run_one.

Output: experiments/results/dropped_target_quality.json
"""
import json, os, pickle, sys
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJ / "src"))

from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

PROJECT = _PROJ / "papers" / "single-sat-quality"
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results"
OUT_PATH = RESULTS_DIR / "dropped_target_quality.json"

SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
SOLVERS = [("MOEA-3", "moea_3obj/_progress.json"), ("MOEA-2", "moea_2obj/_progress.json")]
GROUPS = ["S1", "S2", "S3", "S4"]


def _atomic_write_json(path: Path, obj) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main():
    out = {"f3_max_definition": "cos^3(min phi over the task's cached window grid)",
           "f2_max_definition": "max over the cached grid of sqrt(max(cos^2 psi - cos^2 phi, 0))",
           "solvers": {}}
    for solver_name, prog_rel in SOLVERS:
        prog_path = RESULTS_DIR / prog_rel
        completed = json.load(open(prog_path))["completed"]
        per_group = {}
        for group in GROUPS:
            ret_all, drop_all = [], []
            ret2_all, drop2_all = [], []
            n_scen = 0
            for key, v in sorted(completed.items()):
                if not key.startswith(group + "/"):
                    continue
                pkl = SCENARIOS_DIR / group / key.split("/")[1]
                if not pkl.exists():
                    continue
                data = pickle.load(open(pkl, "rb"))
                inst = build_agile_instance_from_scenario(
                    data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
                precompute_geometry(inst, step_s=10.0)
                sel = set(v.get("selected", []))
                if not sel:
                    continue
                f3_max, f2_max = [], []
                for i in range(inst.N):
                    rows = inst.geom_cache.cache[i]
                    phi_min = float(rows[:, 1].min())
                    f3_max.append(float(np.cos(phi_min)) ** 3)
                    best2 = 0.0
                    for phi, cps in zip(rows[:, 1], rows[:, 3]):
                        c2 = cps * cps - phi * phi
                        if c2 > best2:
                            best2 = c2
                    f2_max.append(float(np.sqrt(max(best2, 0.0))))
                ret = [f3_max[i] for i in sorted(sel) if i < inst.N]
                drop = [f3_max[i] for i in range(inst.N) if i not in sel]
                ret2 = [f2_max[i] for i in sorted(sel) if i < inst.N]
                drop2 = [f2_max[i] for i in range(inst.N) if i not in sel]
                ret_all.extend(ret)
                drop_all.extend(drop)
                ret2_all.extend(ret2)
                drop2_all.extend(drop2)
                n_scen += 1
            per_group[group] = {
                "n_scenarios": n_scen,
                "n_retained": len(ret_all), "n_dropped": len(drop_all),
                "f3max_retained_mean": float(np.mean(ret_all)) if ret_all else None,
                "f3max_dropped_mean": float(np.mean(drop_all)) if drop_all else None,
                "f3max_retained_std": float(np.std(ret_all, ddof=1)) if len(ret_all) > 1 else None,
                "f3max_dropped_std": float(np.std(drop_all, ddof=1)) if len(drop_all) > 1 else None,
                "f2max_retained_mean": float(np.mean(ret2_all)) if ret2_all else None,
                "f2max_dropped_mean": float(np.mean(drop2_all)) if drop2_all else None,
            }
            print(f"{solver_name} {group}: retained={per_group[group]['n_retained']} "
                  f"f3max={per_group[group]['f3max_retained_mean']:.4f} | "
                  f"dropped={per_group[group]['n_dropped']} "
                  f"f3max={per_group[group]['f3max_dropped_mean']:.4f}", flush=True)
        out["solvers"][solver_name] = per_group
    _atomic_write_json(OUT_PATH, out)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
