#!/usr/bin/env python3
"""Unified hot-start vs random-init control for MOEA-2, S1-S4.

Replaces the two old, mutually-inconsistent control scripts:
  - run_s1s2_hotstart_control.py (n_ref_dirs=5, no resume)
  - scripts/run_hotstart_control_s3s4.py (pre-RDR-005 unconstrained baseline_b1,
    ddof=0 summary, no delta_std)

This runner uses the same solver configuration as the headline MOEA-2 runs
(run_moea_2obj.py): n_ref_dirs=12, hotstart_sigma default 0.5, pop=100,
gen=200, n_obj=2, and the constraint-feasible G-BL hot-start seed (baseline_b1
with instance constraints). Scenario set matches the paper's robustness
paragraph: 10 S1 (A_seed00-09), 4 S2 (A_seed00-03), 5 S3 (A_seed00-04),
5 S4 (A_seed00-04), 3 seeds each, hot vs random.

Incremental save per run + resume. Output:
  experiments/results/p1-1_random_init/hotstart_control_s1s4.json
"""
import pickle, json, sys, time, hashlib
from pathlib import Path
import numpy as np

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
SRC = PROJECT / "src"
sys.path.insert(0, str(SRC))

SCENARIOS_DIR = PROJECT / "papers/single-sat-quality/experiments/scenarios"
RESULTS_DIR = PROJECT / "papers/single-sat-quality/experiments/results/p1-1_random_init"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

from sar_sim.solver.moea import moea_solver
from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

SLEW_RATE = 0.0524
SETTLE_TIME = 5.0
HOTSIG = 0.5  # moea_solver default
N_SEEDS = 3
N_REF_DIRS = 12  # matches run_moea_2obj.py headline config

# (scale, start_idx, count) — A-seed bucket, same as old controls
PLAN = [
    ("S1", 0, 10),
    ("S2", 0, 4),
    ("S3", 0, 5),
    ("S4", 0, 5),
]
OUT_PATH = RESULTS_DIR / "hotstart_control_s1s4.json"


def make_hotstart(windows, targets, instance):
    """Encode G-BL schedule as a 2N chromosome (selection + timing tau)."""
    gbl = baseline_b1(windows, targets, instance=instance)
    target_to_idx = {t.target_id: i for i, t in enumerate(instance.tasks)}
    N = instance.N
    x0 = np.zeros(2 * N)
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
    return x0


def run_one(pkl_path, scenario_seed, mode, extra_seed):
    t0 = time.time()
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    windows = data.get("windows", [])
    targets = data.get("targets", [])
    n_targets = data.get("n_targets", len(targets))

    instance = build_agile_instance_from_scenario(
        data,
        max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
    )
    precompute_geometry(instance, step_s=10.0)

    kwargs = {}
    if mode == "hot":
        kwargs["hotstart_individual"] = make_hotstart(windows, targets, instance)
        kwargs["hotstart_sigma"] = HOTSIG

    rng_seed = scenario_seed * 100 + extra_seed

    res = moea_solver(
        windows, targets,
        population_size=100,
        n_generations=200,
        n_obj=2,
        n_ref_dirs=N_REF_DIRS,
        max_slew_rate=SLEW_RATE,
        settle_time=SETTLE_TIME,
        seed=rng_seed,
        **kwargs,
    )
    meta = res.metadata
    return {
        "mode": mode,
        "seed": scenario_seed,
        "extra_seed": extra_seed,
        "n_targets": n_targets,
        "n_selected": int(meta.get("n_selected", 0)),
        "f1": float(meta.get("f1", 0.0)),
        "f2": float(meta.get("f2", 0.0)),
        "runtime_s": round(time.time() - t0, 3),
    }


def load_existing():
    if not OUT_PATH.exists():
        return {}, 0
    with open(OUT_PATH, encoding="utf-8") as f:
        d = json.load(f)
    n = sum(len(v) for v in d.get("scales", {}).values())
    return d, n


def main():
    state, done_n = load_existing()
    scales = state.setdefault("scales", {})
    results = []  # flat list of {scale, scenario, seed, extra_seed, hot, random}

    for scale, start_idx, count in PLAN:
        for idx in range(start_idx, start_idx + count):
            pkl = SCENARIOS_DIR / scale / f"{scale}-A_seed{idx:02d}.pkl"
            if not pkl.exists():
                print(f"WARN missing {pkl}", flush=True)
                continue
            for extra in range(N_SEEDS):
                key = f"{scale}/{scale}-A_seed{idx:02d}.pkl#{extra}"
                if key in state.get("done", {}):
                    continue
                hot_res = run_one(pkl, idx, "hot", extra)
                rnd_res = run_one(pkl, idx, "random", extra)
                results.append({
                    "scale": scale,
                    "scenario": pkl.name,
                    "seed": idx,
                    "extra_seed": extra,
                    "hot": hot_res,
                    "random": rnd_res,
                })
                state.setdefault("done", {})[key] = True
                # Replace (not append): a pre-existing record with the same key from an
                # earlier runner version must be overwritten, else resume doubles counts.
                scales.setdefault(scale, [])
                scales[scale] = [r for r in scales[scale]
                                 if not (r["scenario"] == pkl.name
                                         and r["seed"] == idx and r["extra_seed"] == extra)]
                scales[scale].append(results[-1])
                json.dump(state, open(OUT_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
                print(f"[{scale}-{idx:02d}] x{extra} hot={hot_res['f1']:.3f} rnd={rnd_res['f1']:.3f} d={hot_res['f1']-rnd_res['f1']:+.3f}", flush=True)

    # summary with ddof=1
    summary = {}
    for scale, rows in scales.items():
        hot_f1 = np.array([r["hot"]["f1"] for r in rows])
        rnd_f1 = np.array([r["random"]["f1"] for r in rows])
        diffs = hot_f1 - rnd_f1
        hot_f2 = np.array([r["hot"]["f2"] for r in rows])
        rnd_f2 = np.array([r["random"]["f2"] for r in rows])
        def dd1(a):
            return float(np.std(a, ddof=1)) if len(a) > 1 else 0.0
        summary[scale] = {
            "n": len(rows),
            "hot_f1_mean": float(np.mean(hot_f1)),
            "hot_f1_std": dd1(hot_f1),
            "random_f1_mean": float(np.mean(rnd_f1)),
            "random_f1_std": dd1(rnd_f1),
            "deficit_mean": float(np.mean(rnd_f1 - hot_f1)),  # random deficit vs hot (negative = hot better)
            "deficit_std": dd1(diffs),
            "hot_f2_mean": float(np.mean(hot_f2)),
            "random_f2_mean": float(np.mean(rnd_f2)),
        }

    state["params"] = {
        "pop": 100, "gen": 200, "hotstart_sigma": HOTSIG,
        "n_seeds": N_SEEDS, "n_obj": 2, "n_ref_dirs": N_REF_DIRS,
        "moea": "MOEA-2",
        "scenario_plan": {s: f"{s}-A_seed{start:02d}..{start+count-1:02d} ({count} scenarios)" for s, start, count in PLAN},
    }
    state["summary"] = summary
    json.dump(state, open(OUT_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("\n=== SUMMARY ===", flush=True)
    for scale, s in summary.items():
        print(f"  {scale}: n={s['n']} hot={s['hot_f1_mean']:.3f}±{s['hot_f1_std']:.3f} "
              f"rnd={s['random_f1_mean']:.3f}±{s['random_f1_std']:.3f} "
              f"deficit={s['deficit_mean']:.3f}±{s['deficit_std']:.3f} "
              f"f2: hot={s['hot_f2_mean']:.3f} rnd={s['random_f2_mean']:.3f}", flush=True)
    print(f"Wrote {OUT_PATH}", flush=True)


if __name__ == "__main__":
    main()
