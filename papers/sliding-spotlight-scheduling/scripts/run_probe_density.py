#!/usr/bin/env python3
"""Density probe driver: WH-family sweep below M2WH (prereg amendment
``analysis_prereg.json#amendment_20260930_probe_density``).

Variants 6-9 (P6WH 20 / P7WH 40 / P8WH 60 / P9WH 80), 5 seeds each,
solver config identical to the frozen matrix (pop 40 / gen 60).  Artifacts
land in ``experiments/results/probe_density/`` and are NOT part of the
frozen matrix statistics.

Usage (repo root, real interpreter):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" \
        papers/sliding-spotlight-scheduling/scripts/run_probe_density.py \
        [--variants 6,7,8,9] [--seeds 5]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))

from sss_core.scenarios import (  # noqa: E402
    VARIANT_REGISTRY,
    generate_scenario,
    write_manifest,
)

PROBE_DIR = FORK / "experiments" / "results" / "probe_density"
MANIFEST_DIR = PROBE_DIR / "manifests"
PILOT_SCRIPT = FORK / "scripts" / "run_pilot.py"


def git_head() -> str:
    import shutil
    exe = shutil.which("git")
    out = subprocess.run(
        [exe, "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def run_unit(code: str, seed: int, manifest_path: Path) -> tuple[int, dict | None]:
    env = dict(os.environ, PYTHONHASHSEED="0")
    proc = subprocess.run(
        [sys.executable, str(PILOT_SCRIPT),
         "--manifest", str(manifest_path),
         "--seed", str(seed),
         "--pop", "40", "--gen", "60",
         "--out", str(PROBE_DIR)],
        env=env, capture_output=True, text=True,
    )
    art_path = PROBE_DIR / f"pilot_{code}_seed{seed}.json"
    art = json.loads(art_path.read_text(encoding="utf-8")) if (
        proc.returncode == 0 and art_path.exists()
    ) else None
    return proc.returncode, art


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", default="6,7,8,9")
    ap.add_argument("--seeds", type=int, default=5)
    args = ap.parse_args(argv)

    vmap = {int(t): VARIANT_REGISTRY[int(t)] for t in args.variants.split(",")}
    head = git_head()
    print(f"probe code identity: git HEAD {head}", flush=True)

    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[str, list[dict]] = {}
    exit_counts: dict[int, int] = {}
    for vidx, (code, density, interval, tier) in sorted(vmap.items()):
        for si in range(args.seeds):
            seed = vidx * 100 + si
            manifest = generate_scenario(
                code, density, interval, tier, seed, variant_index=vidx,
            )
            mpath = MANIFEST_DIR / f"{code}_seed{seed}.json"
            write_manifest(manifest, mpath)

            t0 = time.monotonic()
            exit_code, art = run_unit(code, seed, mpath)
            wall = time.monotonic() - t0
            exit_counts[exit_code] = exit_counts.get(exit_code, 0) + 1
            if exit_code == 0:
                rec = {
                    "distinct_fq": len(
                        {round(r["f_q"], 6) for r in art["front"]}
                    ),
                    "front_size": art["front_size"],
                    "n_selected": {r["n_selected"] for r in art["front"]},
                    "spread_db": art["promotion"]["spread_db"],
                    "max_f1_star": art["max_f1_star_on_front"],
                    "anchor_f1_star": art["anchor_f1_star"],
                }
                results.setdefault(code, []).append(rec)
                print(
                    f"[{code}_seed{seed}] exit=0 wall={wall:.1f}s "
                    f"front={rec['front_size']} distinct_fq={rec['distinct_fq']} "
                    f"spread={rec['spread_db']:.3f}dB "
                    f"max_f1*={rec['max_f1_star']:.4f}",
                    flush=True,
                )
            else:
                print(f"[{code}_seed{seed}] exit={exit_code} wall={wall:.1f}s",
                      flush=True)
                if exit_code == 10:
                    print("ABORT: exit-10 zero-served (generation defect)",
                          flush=True)
                    return 10

    print("\n=== probe summary (median over seeds) ===", flush=True)
    for code in sorted(results):
        recs = results[code]
        med = sorted(r["distinct_fq"] for r in recs)
        m = med[len(med) // 2] if len(med) % 2 else (med[len(med) // 2 - 1]
                                                      + med[len(med) // 2]) / 2
        verdict = "NOT-TRIVIALIZED" if m >= 3 else "TRIVIALIZED"
        spread_max = max(r["spread_db"] for r in recs)
        prom = "PROMOTION" if spread_max >= 6.0 else "no_promotion"
        print(f"{code}: median distinct_fq={m} -> {verdict}; "
              f"max spread={spread_max:.3f} dB -> {prom}; "
              f"fronts={[r['front_size'] for r in recs]}", flush=True)
    print(f"exit-code totals: {dict(sorted(exit_counts.items()))}", flush=True)
    if not results:
        print("ALARM: zero probe units succeeded", flush=True)
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
