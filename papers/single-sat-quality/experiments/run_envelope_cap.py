#!/usr/bin/env python3
"""Panel-20260830 N18: run G-BL + MOEA-3 on squint-cap scenarios (E15/E25).

Scenarios are S1-identical (same seeds/targets) with |psi_sq| capped at 15 /
25 deg at window generation. Existing S1 runs are the 45-deg baseline.
Output: experiments/results/envelope_cap/_progress.json
  {"completed": {"E15/E15-A_seed00.pkl": {"moea3": {...}, "gbl": {...}}}}
Atomic write + resume; MOEA settings identical to headline runner
(pop=100, gen=200, n_ref_dirs=12, G-BL hot-start).
"""
import pickle, json, sys, time, hashlib, subprocess, os, tempfile
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJ / "src"))

from sar_sim.solver.moea import moea_solver
from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

PROJECT = Path(__file__).resolve().parents[1]
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
OUT_DIR = PROJECT / "experiments" / "results" / "envelope_cap"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = OUT_DIR / "_progress.json"

SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
POP, GEN, N_REF = 100, 200, 12
GROUPS = ["E15", "E25"]


def _git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(PROJECT), text=True).strip()[:8]
    except Exception:
        return "unknown"


def _pkl_sha1(p):
    sha = hashlib.sha1()
    with open(p, "rb") as f:
        while c := f.read(8192):
            sha.update(c)
    return sha.hexdigest()


def atomic_write(state):
    fd, tmp = tempfile.mkstemp(dir=str(OUT_DIR), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, OUT_PATH)


def load_state():
    if OUT_PATH.exists():
        try:
            return json.load(open(OUT_PATH, encoding="utf-8"))
        except json.JSONDecodeError:
            for bak in sorted(OUT_DIR.glob("_progress.backup_*.json"), reverse=True):
                try:
                    return json.load(open(bak, encoding="utf-8"))
                except Exception:
                    continue
    return {"completed": {}, "stats": {}}


def run_one(pkl_path):
    data = pickle.load(open(pkl_path, "rb"))
    windows, targets = data.get("windows", []), data.get("targets", [])
    instance = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
    precompute_geometry(instance, step_s=10.0)

    gbl = baseline_b1(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
                      geom_cache=instance.geom_cache, instance=instance)

    target_to_idx = {t.target_id: i for i, t in enumerate(instance.tasks)}
    x0 = np.zeros(2 * instance.N)
    seen = set()
    for obs in gbl.schedule:
        tid = obs.window.target_id
        if tid in target_to_idx:
            idx = target_to_idx[tid]
            if idx not in seen:
                seen.add(idx)
                x0[idx] = 1.0
                span = instance.tasks[idx].time_span
                tau = (obs.t_actual_start.timestamp() - instance.tasks[idx].t_earliest) / span if span > 0 else 0.5
                x0[instance.N + idx] = max(0.0, min(1.0, tau))
    hotstart = x0 if seen else None

    t0 = time.time()
    result = moea_solver(
        windows, targets,
        population_size=POP, n_generations=GEN, n_obj=3, n_ref_dirs=N_REF,
        max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
        hotstart_individual=hotstart, instance=instance,
    )
    rt = time.time() - t0
    meta = result.metadata

    frontier = [{"f1": float(s.get("f1", 0)), "f2": float(s.get("f2", 0)), "f3": float(s.get("f3", 0))}
                for s in meta.get("frontier", [])]
    moea3 = {
        "n_targets": data.get("n_targets", len(targets)),
        "n_selected": int(meta.get("n_selected", 0)),
        "f1": float(meta.get("f1", 0.0)),
        "f1_raw": float(meta.get("f1_raw", 0.0)),
        "f1_gbl": float(meta.get("f1_gbl", 1.0)),
        "f2": float(meta.get("f2", 0.0)),
        "f3": float(meta.get("f3", 0.0)),
        "runtime_s": round(rt, 3),
        "n_frontier": len(frontier),
        "frontier_f1": [s["f1"] for s in frontier],
        "frontier_f2": [s["f2"] for s in frontier],
        "frontier_f3": [s["f3"] for s in frontier],
        "n_obj": 3,
        "selected": meta.get("selected", []),
        "t_actuals": meta.get("t_actuals", []),
        "constraint_feasible": bool(meta.get("constraint_feasible", True)),
        "n_constraints_failed": int(meta.get("n_constraints_failed", 0)),
        "all_infeasible": bool(meta.get("all_infeasible", False)),
    }
    gbl_meta = getattr(gbl, "metadata", {}) or {}
    gbl_e = {
        "f1": 1.0,
        "f1_raw": float(gbl_meta.get("f1_raw", gbl.f1)),
        "f2": float(gbl.f2),
        "f3": float(gbl_meta.get("f3", 0.0)),
        "n_selected": len(gbl.schedule),
    }
    return {"moea3": moea3, "gbl": gbl_e}


def main():
    state = load_state()
    completed = state["completed"]
    git_commit = _git_commit()
    for group in GROUPS:
        d = SCENARIOS_DIR / group
        pkls = sorted(d.glob("*.pkl"))
        if not pkls:
            print(f"Group {group}: no scenarios in {d}")
            continue
        for pkl in pkls:
            key = f"{group}/{pkl.name}"
            if key in completed and "moea3" in completed[key]:
                continue
            try:
                out = run_one(pkl)
            except Exception as e:
                print(f"  {key} ERROR {type(e).__name__}: {e}", flush=True)
                continue
            out["pkl_sha1"] = _pkl_sha1(pkl)
            out["git_commit"] = git_commit
            out["cap_deg"] = 15.0 if group == "E15" else 25.0
            completed[key] = out
            atomic_write(state)
            m = out["moea3"]
            print(f"  {key}: f1*={m['f1']:.3f} f2={m['f2']:.3f} f3={m['f3']:.3f} "
                  f"feas={m['constraint_feasible']} t={m['runtime_s']:.0f}s", flush=True)
        n = sum(1 for k in completed if k.startswith(group + "/"))
        print(f"Group {group}: {n} done", flush=True)


if __name__ == "__main__":
    main()
