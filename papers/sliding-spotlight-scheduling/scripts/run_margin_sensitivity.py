#!/usr/bin/env python3
"""Panel T14 reanalysis (2026-10-24): transfer-margin sensitivity of the R3H
coverage curve, via anchor replay (construction face) over the frozen
scenario population.

The C2 chain charges (1+pad)*T_dwell + maneuver + 2 s settle with pad=25%
and the 4.07 s fallback maneuver bound in production.  This script re-runs
the greedy anchor (the construction face that carries the coverage response,
258/260 units) on the SAME frozen manifests under four margin policies:

  prod    : pad 25%,   fallback maneuver 4.07 s   (registered; regression arm)
  pad125  : pad 12.5%, fallback maneuver 4.07 s
  man2409 : pad 25%,   median measured maneuver 2.409 s
  both    : pad 12.5% + 2.409 s

No frozen file is modified: the pad override goes through a deep-copied
manifest (greedy_anchor reads pads from the manifest's preregistration
block); the maneuver override patches the sss_core.maneuver module constant
FALLBACK_MANEUVER_S at runtime inside this process only, which flows through
calibrate_against_kim into the C2 assembly.  The prod arm must reproduce the
stored sweep anchor values per unit (regression check).

Usage (repo root):
    PYTHONPATH=src:papers/sliding-spotlight-scheduling python \
        papers/sliding-spotlight-scheduling/scripts/run_margin_sensitivity.py
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))
sys.path.insert(0, str(FORK.parent.parent / "src"))

import sss_core.maneuver as _man  # noqa: E402
from sss_core.anchor import anchor_on_manifest  # noqa: E402
from sss_core.modes import ModeLibrary  # noqa: E402

V5 = FORK / "experiments" / "v5_results"
OUT = V5 / "margin_sensitivity.json"

FAMILY = "R3H"
SEED_BASE = 300
GRID = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 2.0]
FALLBACK_PROD = _man.FALLBACK_MANEUVER_S  # 4.07


def median(xs: list) -> float:
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


def anchor_f1(manifest: dict, s: float, pad: float, maneuver_s: float, lib) -> float:
    m = copy.deepcopy(manifest)
    for t in m["tasks"]:
        t["rho_req_m"] = s * float(t["rho_req_m"])
    m["preregistration"]["pads"]["inter_task_fraction"] = pad
    _man.FALLBACK_MANEUVER_S = maneuver_s
    try:
        res = anchor_on_manifest(m, lib)
        return res.f1_star
    finally:
        _man.FALLBACK_MANEUVER_S = FALLBACK_PROD


def main() -> int:
    lib = ModeLibrary.from_fixture()
    configs = {
        "prod": (0.25, 4.07),
        "pad125": (0.125, 4.07),
        "man2409": (0.25, 2.409),
        "both": (0.125, 2.409),
    }
    rows = []
    for k in range(10):
        seed = SEED_BASE + k
        manifest = json.loads(
            (V5 / "scenarios" / f"{FAMILY}_seed{seed}.json").read_text(encoding="utf-8"))
        for s in GRID:
            sdir = f"s{str(s).replace('.', '_')}"
            sweep = json.loads(
                (V5 / "sweep" / sdir / f"pilot_{FAMILY}_seed{seed}.json").read_text(
                    encoding="utf-8"))
            stored_anchor = sweep["anchor_f1_star"]
            rec = {"seed": seed, "s": s, "stored_anchor": stored_anchor}
            for name, (pad, man) in configs.items():
                rec[name] = anchor_f1(manifest, s, pad, man, lib)
            rec["regression_ok"] = abs(rec["prod"] - stored_anchor) <= 1e-9
            rows.append(rec)
            print(f"# seed{seed} s={s}: prod={rec['prod']:.4f} "
                  f"pad125={rec['pad125']:.4f} man2409={rec['man2409']:.4f} "
                  f"both={rec['both']:.4f} reg_ok={rec['regression_ok']}", flush=True)

    agg = {}
    for s in GRID:
        sub = [r for r in rows if r["s"] == s]
        agg[str(s)] = {
            name: round(median([r[name] for r in sub]), 4) for name in configs
        } | {"stored_anchor_median": round(median([r["stored_anchor"] for r in sub]), 4)}
    payload = {
        "family": FAMILY, "configs": {k: dict(zip(("pad", "maneuver_s"), v))
                                      for k, v in configs.items()},
        "regression_failures": sum(1 for r in rows if not r["regression_ok"]),
        "median_curve": agg,
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print("# median curve:", json.dumps(agg, indent=1))
    print(f"# regression failures: {payload['regression_failures']}")
    return 1 if payload["regression_failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
