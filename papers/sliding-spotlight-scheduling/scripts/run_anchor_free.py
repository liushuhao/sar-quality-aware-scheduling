#!/usr/bin/env python3
"""Ignition arm R87-04 (ticket 62): anchor-free control at the registered budget.

Runs the same pilot cells as run_budget_check.py but WITHOUT the greedy anchor
seed (--no-anchor-seed), to test whether the dips / the as-placed residual
depend on the anchor construction (ticket 12 D12-1/2 seeding).

Reanalysis-only over the frozen scenario population; baseline comparison reads
the L8 sweep artifacts at the same grid points (budget 40/60, anchor seeded) --
the anchor arm's anchor_f1_star is the reference ceiling.

Usage (repo root):
    PYTHONPATH=src:papers/sliding-spotlight-scheduling python \
        papers/sliding-spotlight-scheduling/scripts/run_anchor_free.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))
sys.path.insert(0, str(FORK.parent.parent / "src"))

V5 = FORK / "experiments" / "v5_results"
OUT = V5 / "anchor_free"

# (family, seed_base, [s points]) -- same cells as run_budget_check.py
UNITS = [
    ("R2F", 200, [0.9, 1.4]),
    ("R3H", 300, [0.9, 1.0]),
]


def sdir(s: float) -> str:
    return f"s{str(s).replace('.', '_')}"


def run_unit(family: str, seed: int, s: float) -> dict:
    manifest = V5 / "scenarios" / f"{family}_seed{seed}.json"
    unit_dir = OUT / sdir(s)
    unit_dir.mkdir(parents=True, exist_ok=True)
    out_json = unit_dir / f"pilot_{family}_seed{seed}.json"
    t0 = time.time()
    cmd = [
        sys.executable, str(FORK / "scripts" / "run_pilot.py"),
        "--manifest", str(manifest),
        "--seed", str(seed), "--pop", "40", "--gen", "60",
        "--s-factor", str(s),
        "--no-anchor-seed",
        "--out", str(unit_dir),
    ]
    import os
    env = {**os.environ, "PYTHONHASHSEED": "0"}
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    wall_s = time.time() - t0
    if proc.returncode != 0:
        return {"family": family, "seed": seed, "s": s, "rc": proc.returncode,
                "stderr_tail": proc.stderr[-300:], "wall_s": wall_s}

    hi = json.loads(out_json.read_text(encoding="utf-8"))
    base_path = V5 / "sweep" / sdir(s) / f"pilot_{family}_seed{seed}.json"
    base = json.loads(base_path.read_text(encoding="utf-8"))
    return {
        "family": family, "seed": seed, "s": s, "budget": "40/60",
        "anchor_free_max_f1_star": hi["max_f1_star_on_front"],
        "anchor_arm_f1_star": base["anchor_f1_star"],
        "anchor_arm_max_front": base["max_f1_star_on_front"],
        "anchor_arm_source": str(base_path.relative_to(V5.parent.parent)),
        "free_beats_anchor_arm": hi["max_f1_star_on_front"] > base["anchor_f1_star"] + 1e-12,
        "free_vs_anchor_arm_pp": (hi["max_f1_star_on_front"] - base["anchor_f1_star"]) * 100.0,
        "free_vs_front_pp": (hi["max_f1_star_on_front"] - base["max_f1_star_on_front"]) * 100.0,
        "wall_s": wall_s,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    results_path = OUT / "anchor_free.json"
    results = []
    if results_path.exists():
        results = json.loads(results_path.read_text(encoding="utf-8"))
    done = {(r["family"], r["seed"], r["s"]) for r in results if "rc" not in r}

    for family, seed_base, s_points in UNITS:
        for seed in range(seed_base, seed_base + 10):
            for s in s_points:
                if (family, seed, s) in done:
                    continue
                r = run_unit(family, seed, s)
                results.append(r)
                results_path.write_text(json.dumps(results, indent=1), encoding="utf-8")
                if "rc" in r:
                    print(f"# ERROR {family} seed{seed} s={s}: rc={r['rc']}", flush=True)
                else:
                    print(f"# {family} seed{seed} s={s}: free={r['anchor_free_max_f1_star']:.4f} "
                          f"anchor_arm={r['anchor_arm_f1_star']:.4f} "
                          f"beats={r['free_beats_anchor_arm']} "
                          f"delta={r['free_vs_anchor_arm_pp']:+.2f}pp wall={r['wall_s']:.0f}s",
                          flush=True)

    ok = [r for r in results if "rc" not in r]
    beats = sum(1 for r in ok if r["free_beats_anchor_arm"])
    print(f"# units ok: {len(ok)}  free-beats-anchor-arm: {beats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
