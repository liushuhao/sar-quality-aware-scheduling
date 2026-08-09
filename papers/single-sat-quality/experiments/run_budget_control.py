#!/usr/bin/env python3
"""Search-budget control: full-physics A vs no-physics D at double budget.

Doubling pop/gen (200/400) on five S3 and five S4 scenarios. Replaces
archive/20260712_P1-4_variant_d_rerun.py, which built the G-BL hot-start
without instance constraints (RDR-005: infeasible seeds on dense scenarios)
and recorded no provenance. Uses the corrected pattern from the headline
runners: build instance, precompute geometry, constraint-feasible hot-start,
pass instance to solver, record git_commit + pkl_sha1.

Output:
  experiments/results/p1-4_variant_d_rerun/budget_control.json
"""
import pickle, json, sys, time, hashlib, subprocess
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_PROJ / "src"))
sys.path.insert(0, str(_PROJ / "papers" / "single-sat-quality" / "experiments"))

from sar_sim.solver.moea import moea_solver
from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry
from run_moea_3obj_no_physics import moea_solver_no_physics

PROJECT = _PROJ / "papers" / "single-sat-quality"
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "p1-4_variant_d_rerun"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = RESULTS_DIR / "budget_control.json"

SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
POP, GEN = 200, 400
N_SCENARIOS = 5
GROUPS = ["S3", "S4"]


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(PROJECT), text=True).strip()[:8]
    except Exception:
        return "unknown"


def _pkl_sha1(p: Path) -> str:
    sha = hashlib.sha1()
    with open(p, "rb") as f:
        while c := f.read(8192):
            sha.update(c)
    return sha.hexdigest()


def build_hotstart(windows, targets, instance):
    gbl = baseline_b1(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
                      geom_cache=instance.geom_cache, instance=instance)
    target_to_idx = {t.target_id: i for i, t in enumerate(instance.tasks)}
    x0 = np.zeros(2 * instance.N)
    seen = set()
    for obs in gbl.schedule:
        tid = obs.window.target_id
        if tid in target_to_idx and target_to_idx[tid] not in seen:
            idx = target_to_idx[tid]
            seen.add(idx)
            x0[idx] = 1.0
            span = instance.tasks[idx].time_span
            tau = (obs.t_actual_start.timestamp() - instance.tasks[idx].t_earliest) / span if span > 0 else 0.5
            x0[instance.N + idx] = max(0.0, min(1.0, tau))
    return x0 if seen else None


def run_variant(pkl_path, variant):
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    windows, targets = data.get("windows", []), data.get("targets", [])
    instance = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
    precompute_geometry(instance, step_s=10.0)
    hs = build_hotstart(windows, targets, instance)

    t0 = time.time()
    kw = dict(population_size=POP, n_generations=GEN, n_obj=3, n_ref_dirs=12,
              max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
              hotstart_individual=hs, instance=instance, scenario=data)
    if variant == "A_full_physics":
        result = moea_solver(windows, targets, **kw)
    else:
        # no-physics solver defaults f1_gbl=1.0 (raw profit); pass the G-BL
        # normalization so its f1* is comparable with A ([[feedback-cross-runner-field-semantics]]).
        gbl = baseline_b1(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
                          geom_cache=instance.geom_cache, instance=instance)
        kw["f1_gbl"] = max(float(gbl.f1), 1.0)
        result = moea_solver_no_physics(windows, targets, **kw)
    rt = time.time() - t0
    meta = result.metadata
    return {
        "variant": variant,
        "f1": float(meta.get("f1", 0)),
        "f1_raw": float(meta.get("f1_raw", 0)),
        "f2": float(meta.get("f2", 0)),
        "f3": float(meta.get("f3", 0)),
        "n_selected": int(meta.get("n_selected", 0)),
        "constraint_feasible": bool(meta.get("constraint_feasible", True)),
        "all_infeasible": bool(meta.get("all_infeasible", False)),
        "runtime_s": round(rt, 1),
    }


def main():
    state = {}
    if OUT_PATH.exists():
        try:
            state = json.load(open(OUT_PATH, encoding="utf-8"))
            print(f"Resumed: {sum(len(v) for v in state.get('results', {}).values())} pairs done")
        except Exception:
            pass
    results = state.setdefault("results", {})
    git_commit = _git_commit()

    for group in GROUPS:
        d = SCENARIOS_DIR / group
        pkls = sorted(d.glob("*.pkl"))[:N_SCENARIOS]
        if not pkls:
            continue
        pairs = results.setdefault(group, [])
        done = {r["scenario"] for r in pairs}
        print(f"\nGroup {group}: {len(pkls)} scenarios, pop={POP} gen={GEN}")
        for pkl in pkls:
            if pkl.name in done:
                print(f"  {pkl.name} SKIP (done)")
                continue
            t0 = time.time()
            ra = run_variant(pkl, "A_full_physics")
            rd = run_variant(pkl, "D_no_physics")
            delta = ra["f1"] - rd["f1"]
            pair = {"scenario": pkl.name, "pkl_sha1": _pkl_sha1(pkl), "git_commit": git_commit,
                    "A": ra, "D": rd, "delta_f1": delta}
            pairs.append(pair)
            json.dump(state, open(OUT_PATH, "w", encoding="utf-8"), indent=2)
            print(f"  {pkl.name}: A f1*={ra['f1']:.3f} (f2={ra['f2']:.4f})  D f1*={rd['f1']:.3f} (f2={rd['f2']:.4f})  d={delta:+.3f}  t={time.time()-t0:.0f}s", flush=True)

    summary = {}
    for group, pairs in results.items():
        if not pairs:
            continue
        a_f1 = np.array([r["A"]["f1"] for r in pairs])
        d_f1 = np.array([r["D"]["f1"] for r in pairs])
        a_f2 = np.array([r["A"]["f2"] for r in pairs])
        d_f2 = np.array([r["D"]["f2"] for r in pairs])
        summary[group] = {
            "A_f1_mean": float(a_f1.mean()), "A_f1_std": float(a_f1.std()),
            "D_f1_mean": float(d_f1.mean()), "D_f1_std": float(d_f1.std()),
            "delta_mean": float((a_f1 - d_f1).mean()), "n": len(pairs),
            "A_f2_mean": float(a_f2.mean()), "D_f2_mean": float(d_f2.mean()),
            "f2_pooled_mean": float(np.concatenate([a_f2, d_f2]).mean()),
        }
    state["summary"] = summary
    state["params"] = {"pop": POP, "gen": GEN, "n_scenarios": N_SCENARIOS,
                       "groups": GROUPS, "n_obj": 3, "n_ref_dirs": 12, "git_commit": git_commit}
    json.dump(state, open(OUT_PATH, "w", encoding="utf-8"), indent=2)

    print("\n=== SUMMARY ===")
    for g, s in summary.items():
        print(f"  {g}: A={s['A_f1_mean']:.3f}+/-{s['A_f1_std']:.3f}  D={s['D_f1_mean']:.3f}+/-{s['D_f1_std']:.3f}  d={s['delta_mean']:+.3f}  f2_pooled={s['f2_pooled_mean']:.4f}")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
