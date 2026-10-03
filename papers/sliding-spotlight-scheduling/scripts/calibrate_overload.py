#!/usr/bin/env python3
"""Overload-ratio calibration loop for the R-family (ticket 16, item 6).

generate-measure-adjust, preregistered: the incidence band is scanned, the
overload ratio is measured at each setting, and the artifact records the whole
ladder so the band levels are chosen FROM DATA rather than assumed.

The ticket requires at least three in-band overload tiers.  Measured on the
design orbit (seed 100, N=20, demand C):

    band 20-70 deg -> 0.8500   (17/20 served)
    band 30-60 deg -> 0.5000   (10/20)
    band 40-52 deg -> 0.4000   ( 8/20)
    band 44-48 deg -> 0.2500   ( 5/20)

Every loss is `no_window` -- the cascade rejects the target because the real
geometry offers no window inside the band.  The demand tier is NOT the knob
(C and H both give 0.5000 at 30-60 deg), so the band is what the overload axis
is scanned along.

Writes ONLY into the given --out directory; never into experiments/results/.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/calibrate_overload.py \
        --out .scratch/sliding-spotlight-scheduling/calibration
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))

import sss_core.scenarios as S  # noqa: E402
from sss_core.modes import ModeLibrary  # noqa: E402
from sss_core.realwindows import KeplerianElement  # noqa: E402

# Preregistered band ladder (spec D14 item 6: generate-measure-adjust).
BAND_LADDER_DEG = ((20.0, 70.0), (30.0, 60.0), (40.0, 52.0), (44.0, 48.0))
PROBE_DENSITY = 20
PROBE_TIERS = ("C", "H")
PROBE_SEED = 100
MIN_IN_BAND_TIERS = 3          # the ticket's floor


def design_orbit(lib: ModeLibrary):
    a = 6_371_000.0 + lib.geo.altitude_m
    epoch = datetime(2026, 1, 1)
    el = KeplerianElement(
        semi_major_axis=a, eccentricity=0.001,
        inclination=math.radians(45.0), raan=0.0, arg_perigee=0.0,
        true_anomaly=0.0, epoch=epoch,
    )
    return (el, epoch)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output directory (never experiments/results)")
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    lib = ModeLibrary.from_fixture()
    plat = design_orbit(lib)
    original_band = S.R_INCIDENCE_BAND_DEG

    ladder = []
    try:
        for lo, hi in BAND_LADDER_DEG:
            S.R_INCIDENCE_BAND_DEG = (lo, hi)
            rows = {}
            for tier in PROBE_TIERS:
                m = S.generate_real_scenario(
                    f"R{PROBE_DENSITY}{tier}", PROBE_DENSITY, tier,
                    PROBE_SEED, 1, lib=lib, platform=plat,
                )
                led = m["generation_ledger"]
                rows[tier] = {
                    "served": led["n_served"],
                    "overload_ratio": round(led["n_served"] / PROBE_DENSITY, 6),
                    "removals": {k: v for k, v in led["removals"].items() if v},
                }
            ladder.append({"band_deg": [lo, hi], "by_tier": rows})
            print(
                f"band {lo:5.1f}-{hi:5.1f}: "
                + "  ".join(
                    f"{t}={rows[t]['overload_ratio']:.4f}" for t in PROBE_TIERS
                ),
                flush=True,
            )
    finally:
        S.R_INCIDENCE_BAND_DEG = original_band

    ratios = sorted({r["overload_ratio"] for e in ladder for r in e["by_tier"].values()})
    n_tiers = len(ratios)
    ok = n_tiers >= MIN_IN_BAND_TIERS

    report = {
        "schema": "overload-calibration/1.0",
        "ticket": "16 acceptance item 6",
        "knob": "incidence band (the demand tier is NOT the knob -- both C and H give the same ratio)",
        "probe": {
            "density_n": PROBE_DENSITY, "tiers": list(PROBE_TIERS),
            "seed": PROBE_SEED, "platform": "design orbit h=570 km, i=45 deg",
        },
        "ladder": ladder,
        "distinct_overload_ratios": ratios,
        "n_distinct_tiers": n_tiers,
        "min_required_tiers": MIN_IN_BAND_TIERS,
        "in_band": ok,
        "verdict": (
            f"{n_tiers} distinct overload tiers measured (>= {MIN_IN_BAND_TIERS} required)"
            if ok else
            f"ONLY {n_tiers} distinct overload tier(s) -- below the registered floor of "
            f"{MIN_IN_BAND_TIERS}; the band ladder must be widened before any run"
        ),
    }
    path = out / "overload_calibration.json"
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nverdict: {report['verdict']}", flush=True)
    print(f"written: {path}", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())