#!/usr/bin/env python3
"""Panel-20260830 N18: squint-envelope sensitivity scenarios.

Generates S1-identical scenarios (same seeds, same targets, same instrument
and orbit) with the agility envelope capped at |psi_sq| <= 15 deg and
<= 25 deg, instead of the default 45 deg. Targets are byte-identical in
expectation (same RNG seeds); only window filtering changes, so comparisons
against the existing S1 group are perfectly paired.

Output dirs: experiments/scenarios/E15, experiments/scenarios/E25
(50 scenarios each: labels E15-A..E15-E x seeds 0..9, mirroring S1-A..S1-E).
"""
import pickle, sys
from pathlib import Path

_PROJ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJ / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate_all_scenarios as gas

PROJECT = Path(__file__).resolve().parents[1]
OUT_ROOT = PROJECT / "experiments" / "scenarios"

CAPS = {"E15": 15.0, "E25": 25.0}
N_TARGETS = 20


def cap_params(dist_idx, seed_idx, seed, cap_deg):
    base = {"n_targets": N_TARGETS, "seed": seed, "sat_params": gas.SENTINEL1,
            "look_direction": "both", "max_squint_deg": cap_deg}
    if dist_idx == 0:
        return {**base, "dist_type": "uniform"}
    elif dist_idx == 1:
        return {**base, "dist_type": "clustered", "n_clusters": 5}
    elif dist_idx == 2:
        return {**base, "dist_type": "mixed", "n_clusters": 2}
    elif dist_idx == 3:
        return {**base, "dist_type": "uniform", "n_orbits": 1}
    else:
        return {**base, "dist_type": "uniform"}


def main():
    for group, cap in CAPS.items():
        out_dir = OUT_ROOT / group
        out_dir.mkdir(parents=True, exist_ok=True)
        labels = [f"{group}-{c}" for c in "ABCDE"]
        total = 0
        for dist_idx, label in enumerate(labels):
            for seed_idx in range(10):
                seed = dist_idx * 100 + seed_idx
                fname = f"{label}_seed{seed_idx:02d}.pkl"
                fpath = out_dir / fname
                if fpath.exists():
                    continue
                scenario = gas.generate_one_scenario(**cap_params(dist_idx, seed_idx, seed, cap))
                with open(fpath, "wb") as f:
                    pickle.dump(scenario, f, protocol=pickle.HIGHEST_PROTOCOL)
                s = scenario["stats"]
                total += 1
                print(f"  [{group}] {fname}: {s['n_with_windows']}/{s['n_targets_total']} "
                      f"visible, {s['total_windows']} windows", flush=True)
        print(f"[{group}] generated {total} new (cap {cap} deg)", flush=True)


if __name__ == "__main__":
    main()
