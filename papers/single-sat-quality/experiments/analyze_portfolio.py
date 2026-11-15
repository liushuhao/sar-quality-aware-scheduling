#!/usr/bin/env python3
"""N2 portfolio control (panel 2026-11-07 DA-01 CRITICAL): the G-BL/G-SM
placement-interpolation envelope vs the MOEA fronts, on the same three
coordinates.

Per scenario (DA-01's design, verbatim):
  - q = 0 is the G-BL schedule itself (earliest-feasible placement).
  - For q in {0.25, 0.5, 0.75, 1.0}: a random q-fraction of the G-BL
    schedule's observations is re-placed by the G-SM squint-minimisation
    rule (_b3_squint_minimize, the same helper G-SM uses), C2 transitions
    are repaired with the same enforcement G-SM applies
    (_enforce_c2_transitions), and feasibility (C1-C4) is checked with the
    independent ConstraintVerifier. K=10 random subsets per q, rng seeded
    per (scenario seed, q, trial) for reproducibility.
  - Feasible mixtures are evaluated on the same three coordinates
    (f1 normalized by the scenario's G-BL anchor, f2/f3 via the solver's
    post-hoc formulas).

Per scenario and per MOEA arm the test asks: among feasible mixture points
whose coverage is at or above the arm's knee coverage, does any point match
or beat the knee's quality? If yes, the two-heuristic portfolio reaches the
knee and the frontier claim needs the measured caveat; if no, the paper has
a measured answer to why a mixture falls short (e.g. slew coupling making
large-q mixtures infeasible).
"""
import copy as _copy
import json, pickle, sys, hashlib
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from sar_sim.solver.baselines import (
    baseline_b1, _b3_squint_minimize, _enforce_c2_transitions,
    _compute_f2_f3_posthoc,
)
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry
from sar_sim.verification.constraints import ConstraintVerifier

PROJECT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RES = PROJECT / "experiments" / "results"
SLEW_RATE = 0.0524
SETTLE_TIME = 5.0
Q_GRID = [0.0, 0.25, 0.5, 0.75, 1.0]
K_TRIALS = 10


def load_completed(results_dir):
    return json.load(open(results_dir / "_progress.json", encoding="utf-8"))["completed"]


def _atomic_write_json(path, obj):
    import os
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def eval_observations(obs_list, instance, geom_cache, f1_gbl):
    """f1/f2/f3 + frontier dict for a hand-built schedule.

    phis/t_actuals are built as FULL N-length task-indexed arrays (matching
    what decode_solution emits): verify_frontier treats a positional list as
    task-indexed whenever its length is not strictly less than N, which bites
    exactly when all N tasks are selected (S1)."""
    tasks = instance.tasks
    N = instance.N
    idx_by_tid = {t.target_id: i for i, t in enumerate(tasks)}
    selected = []
    phi_full = [0.0] * N
    t_full = [0.0] * N
    for o in obs_list:
        i = idx_by_tid.get(o.window.target_id)
        if i is None:
            continue
        g = geom_cache.lookup(i, o.t_actual_start.timestamp())
        selected.append(i)
        phi_full[i] = float(g.phi)
        t_full[i] = float(o.t_actual_start.timestamp())
    f1 = sum(tasks[i].priority for i in selected) / max(f1_gbl, 1.0)
    f2, f3 = _compute_f2_f3_posthoc(obs_list, geom_cache, instance)
    return {
        "row": 0, "selected": selected, "phis": phi_full, "t_actuals": t_full,
        "f1": float(f1), "f2": float(f2), "f3": float(f3), "n_tasks": len(selected),
    }


def mixture_points(data, seed):
    """All portfolio points for one scenario."""
    windows, targets = data.get("windows", []), data.get("targets", [])
    instance = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
    precompute_geometry(instance, step_s=10.0)
    geom_cache = instance.geom_cache
    gbl = baseline_b1(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
                      geom_cache=geom_cache, instance=instance)
    obs0 = list(gbl.schedule)
    f1_gbl = sum(instance.tasks[{t.target_id: i for i, t in enumerate(instance.tasks)}[o.window.target_id]].priority
                 for o in obs0)
    verifier = ConstraintVerifier(instance)
    points = []

    for q_idx, q in enumerate(Q_GRID):
        for trial in range(K_TRIALS):
            rng = np.random.default_rng([seed, q_idx, trial])
            n = len(obs0)
            k = int(round(q * n))
            subset = set(rng.choice(n, size=k, replace=False).tolist()) if k else set()
            new_obs = []
            for j, o in enumerate(obs0):
                if j in subset:
                    new_obs.append(_b3_squint_minimize([o], geom_cache, instance)[0])
                else:
                    new_obs.append(_copy.copy(o))
            new_obs = _enforce_c2_transitions(new_obs, instance=instance)
            fd = eval_observations(new_obs, instance, geom_cache, f1_gbl)
            rpt = verifier.verify_frontier([fd])[0][1]
            points.append({"q": q, "trial": trial, "feasible": bool(rpt.overall_pass),
                           "f1": fd["f1"], "f2": fd["f2"], "f3": fd["f3"],
                           "n_tasks": fd["n_tasks"]})
    return points


def main():
    m3 = load_completed(RES / "moea_3obj")
    m2 = load_completed(RES / "moea_2obj")
    baselines = json.load(open(RES / "baselines_200.json", encoding="utf-8"))
    keys = sorted(set(m3.keys()) & set(baselines.keys()))
    print("N2 portfolio control: %d scenarios" % len(keys))

    out = {"q_grid": Q_GRID, "k_trials": K_TRIALS, "scenarios": {}}
    progress_path = RES / "portfolio_analysis.json"
    done = {}
    if progress_path.exists():
        done = json.load(open(progress_path, encoding="utf-8")).get("scenarios", {})
        print("resuming: %d done" % len(done))

    for n, key in enumerate(keys):
        if key in done:
            continue
        with open(SCENARIOS_DIR / key, "rb") as f:
            data = pickle.load(f)
        seed = data.get("seed", 0)
        pts = mixture_points(data, seed)
        feas = [p for p in pts if p["feasible"]]
        rec = {"points": pts}
        for arm, prog in (("MOEA-3", m3), ("MOEA-2", m2)):
            e = prog[key]
            kf1, kf2, kf3 = e["f1"], e["f2"], e["f3"]
            dom = [p for p in feas if p["f1"] >= kf1 - 1e-9]
            rec[arm] = {
                "knee_f1": kf1, "knee_f2": kf2, "knee_f3": kf3,
                "n_feasible": len(feas),
                "max_f2_at_cov": max((p["f2"] for p in dom), default=None),
                "max_f3_at_cov": max((p["f3"] for p in dom), default=None),
                "reaches_knee_f2": bool(any(p["f2"] >= kf2 - 1e-9 for p in dom)),
                "reaches_knee_f3": bool(any(p["f3"] >= kf3 - 1e-9 for p in dom)),
            }
        out["scenarios"][key] = rec
        done[key] = rec
        out["scenarios"] = done
        if (n + 1) <= 2 or (n + 1) % 10 == 0:
            r3 = rec["MOEA-3"]
            print("  [%d/%d] %s feasible=%d/%d reach_f2=%s reach_f3=%s" % (
                n + 1, len(keys), key, r3["n_feasible"], len(pts),
                r3["reaches_knee_f2"], r3["reaches_knee_f3"]))
        _atomic_write_json(progress_path, out)

    # Aggregate per class
    agg = {}
    for key, rec in done.items():
        cls = key.split("/")[0]
        a = agg.setdefault(cls, {"n": 0, "feas_total": 0, "feas_pts": 0,
                                 "reach_f2": 0, "reach_f3": 0})
        a["n"] += 1
        for arm in ("MOEA-3",):
            a["feas_pts"] += rec[arm]["n_feasible"]
            a["reach_f2"] += int(rec[arm]["reaches_knee_f2"])
            a["reach_f3"] += int(rec[arm]["reaches_knee_f3"])
    out["aggregate_MOEA-3"] = agg
    print("Aggregate (vs MOEA-3 knee):")
    for cls in sorted(agg):
        a = agg[cls]
        print("  %s n=%d reach_f2=%d(%.0f%%) reach_f3=%d(%.0f%%)" % (
            cls, a["n"], a["reach_f2"], 100.0 * a["reach_f2"] / max(a["n"], 1),
            a["reach_f3"], 100.0 * a["reach_f3"] / max(a["n"], 1)))
    _atomic_write_json(progress_path, out)
    print("saved: %s" % progress_path)


if __name__ == "__main__":
    main()
