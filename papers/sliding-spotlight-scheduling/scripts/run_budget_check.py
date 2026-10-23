#!/usr/bin/env python3
"""Panel T11/T12 budget check (2026-10-24): does anchor = best-found survive 160/240?

T11 (seat-2 M1): R2F at the two dip grid points (s=0.9, s=1.4) at 160/240 --
if the search still never beats the anchor there, the dips are construction,
not budget artifacts.

T12 (seat-2 M3 / DA observation): R3H at s=0.9 (the 6.0-pp residual cell,
bound 0.748 vs obs 0.688) and s=1.0 (the as-placed point) at 160/240 --
measures whether a 4x evaluation budget moves coverage toward the bound
(anchor myopia) or leaves it (C2 physics at registered policy).

Reanalysis-only over the frozen scenario population; no scenario
regeneration, no parameter change.  Baseline comparison reads the L8 sweep
artifacts at the same grid points (budget 40/60).

Usage (repo root):
    PYTHONPATH=src:papers/sliding-spotlight-scheduling python \
        papers/sliding-spotlight-scheduling/scripts/run_budget_check.py
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
OUT = V5 / "budget_check"

# (family, seed_base, [s points]) -- R2F dips + R3H residual/as-placed
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
        "--seed", str(seed), "--pop", "160", "--gen", "240",
        "--s-factor", str(s),
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
        "family": family, "seed": seed, "s": s, "budget": "160/240",
        "anchor_f1_star": hi["anchor_f1_star"],
        "max_f1_star_on_front": hi["max_f1_star_on_front"],
        "search_only_max_f1_star": hi["search_only_max_f1_star"],
        "search_beats_anchor": hi["max_f1_star_on_front"] > hi["anchor_f1_star"] + 1e-12,
        "base4060_anchor": base["anchor_f1_star"],
        "base4060_max_front": base["max_f1_star_on_front"],
        "gain_vs_4060_pp": (hi["max_f1_star_on_front"] - base["max_f1_star_on_front"]) * 100.0,
        "wall_s": wall_s,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    results_path = OUT / "budget_check.json"
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
                    print(f"# {family} seed{seed} s={s}: anchor={r['anchor_f1_star']:.4f} "
                          f"front={r['max_f1_star_on_front']:.4f} "
                          f"search_beats={r['search_beats_anchor']} "
                          f"gain40/60={r['gain_vs_4060_pp']:+.2f}pp wall={r['wall_s']:.0f}s",
                          flush=True)

    ok = [r for r in results if "rc" not in r]
    beats = sum(1 for r in ok if r["search_beats_anchor"])
    print(f"# units ok: {len(ok)}  search-beats-anchor: {beats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
