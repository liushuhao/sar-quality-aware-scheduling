#!/usr/bin/env python3
"""Reproduce hot-start vs random-init control for S1 (10 scenarios) and S2 (4 scenarios).

Mirrors s3_s4_control.json structure: for each scenario run MOEA-2 with
  - hot-start (G-BL solution + Gaussian sigma=0.5 noise, 3 seeds)
  - random init (no hot-start, 3 seeds)

Selects A-seed bucket:
  S1: S1-A_seed00.pkl .. S1-A_seed09.pkl  (10 scenarios)
  S2: S2-A_seed00.pkl .. S2-A_seed03.pkl  (4 scenarios)

Output: experiments/results/p1-1_random_init/s1s2_control.json
"""
import pickle, json, sys, time, hashlib, os
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
from sar_sim.solver.types import build_agile_instance, precompute_geometry

SLEW_RATE = 0.0524
SETTLE_TIME = 5.0
HOTSIG = 0.5
N_SEEDS = 3

# which scenarios to run: (scale, start_idx, count)
PLAN = [
    ("S1", 0, 10),
    ("S2", 0, 4),
]


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
    """Run MOEA-2 on a scenario. mode in ('hot', 'random'). Returns dict."""
    t0 = time.time()

    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    windows = data.get("windows", [])
    targets = data.get("targets", [])
    n_targets = data.get("n_targets", len(targets))

    # instance shared by both modes
    instance = build_agile_instance(
        windows, targets,
        max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
    )
    precompute_geometry(instance, step_s=10.0)

    kwargs = {}
    if mode == "hot":
        x0 = make_hotstart(windows, targets, instance)
        kwargs["hotstart_individual"] = x0
        kwargs["hotstart_sigma"] = HOTSIG

    # seed for pymoo RNG
    rng_seed = scenario_seed * 100 + extra_seed

    res = moea_solver(
        windows, targets,
        population_size=100,
        n_generations=200,
        n_obj=2,
        n_ref_dirs=5,
        max_slew_rate=SLEW_RATE,
        settle_time=SETTLE_TIME,
        seed=rng_seed,
        **kwargs,
    )
    rt = time.time() - t0

    meta = res.metadata
    return {
        "mode": mode,
        "seed": scenario_seed,
        "extra_seed": extra_seed,
        "n_targets": n_targets,
        "n_selected": int(meta.get("n_selected", 0)),
        "f1": float(meta.get("f1", 0.0)),
        "f1_raw": float(meta.get("f1_raw", 0.0)),
        "f1_gbl": float(meta.get("f1_gbl", 1.0)),
        "f2": float(meta.get("f2", 0.0)),
        "f3": float(meta.get("f3", 0.0)),
        "runtime_s": round(rt, 3),
    }


def main():
    results = {}
    n = 0
    for scale, start_idx, count in PLAN:
        scale_results = []
        scale_n = 0
        for idx in range(start_idx, start_idx + count):
            pkl = SCENARIOS_DIR / scale / f"{scale}-A_seed{idx:02d}.pkl"
            if not pkl.exists():
                print(f"WARN missing {pkl}", flush=True)
                continue
            seed = idx  # scenario seed for reproducibility
            for extra in range(N_SEEDS):
                hot_res = run_one(pkl, seed, "hot", extra)
                rnd_res = run_one(pkl, seed, "random", extra)
                scale_results.append({
                    "scenario": pkl.name,
                    "seed": seed,
                    "extra_seed": extra,
                    "hot": hot_res,
                    "random": rnd_res,
                })
                scale_n += 1
                n += 1
                marker = " "
                if scale_n % 1 == 0 and (scale_n % 2 == 0 or scale_n == 1):
                    marker = f" [{scale_n}]"
                print(f"[{scale}-{idx:02d}] seed={seed} extra={extra}  hot_f1={hot_res['f1']:.3f}  rnd_f1={rnd_res['f1']:.3f}{marker}", flush=True)
        results[scale] = scale_results

    # summary
    summary = {}
    for scale, rows in results.items():
        hot_f1 = [r["hot"]["f1"] for r in rows]
        rnd_f1 = [r["random"]["f1"] for r in rows]
        diffs = [h - rf for h, rf in zip(hot_f1, rnd_f1)]
        summary[scale] = {
            "n": len(rows),
            "hot_f1_mean": float(np.mean(hot_f1)),
            "hot_f1_std": float(np.std(hot_f1, ddof=1)) if len(hot_f1) > 1 else 0.0,
            "random_f1_mean": float(np.mean(rnd_f1)),
            "random_f1_std": float(np.std(rnd_f1, ddof=1)) if len(rnd_f1) > 1 else 0.0,
            "delta_mean": float(np.mean(diffs)),
            "delta_std": float(np.std(diffs, ddof=1)) if len(diffs) > 1 else 0.0,
        }

    out = {
        "params": {
            "pop": 100, "gen": 200,
            "hotstart_sigma": HOTSIG,
            "n_seeds": N_SEEDS,
            "n_obj": 2, "n_ref_dirs": 5,
            "moea": "MOEA-2",
            "scenario_plan": {
                "S1": "S1-A_seed00..09 (10 scenarios)",
                "S2": "S2-A_seed00..03 (4 scenarios)",
            },
        },
        "summary": summary,
        "results": results,
    }

    out_path = RESULTS_DIR / "s1s2_control.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n=== SUMMARY ===", flush=True)
    for scale, s in summary.items():
        print(f"  {scale}: n={s['n']}, hot={s['hot_f1_mean']:.3f} ({s['hot_f1_std']:.3f}), "
              f"rnd={s['random_f1_mean']:.3f} ({s['random_f1_std']:.3f}), "
              f"delta={s['delta_mean']:.3f} ({s['delta_std']:.3f})", flush=True)
    print(f"Wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
