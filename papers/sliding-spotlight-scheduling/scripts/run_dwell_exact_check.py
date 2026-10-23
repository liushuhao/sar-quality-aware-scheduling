#!/usr/bin/env python3
"""Panel T6 reanalysis (2026-10-24): production SLS dwell vs the exact
Eq.(20)-(23) chain, over the squint envelope.

The production SLS scene dwell is the symmetric-alpha construction
(``kim_checker_scene_sls``: Eq.(18) broadside sweep span placed symmetric
about the centre squint, Eq.(22) first form).  The exact squinted chain
(``kim_eq23_theta_s1``: Eq.(23) quadratic for the end squint, Eq.(22) both
forms) is implemented but used only as an internal identity check.  This
script reports the relative deviation of production from exact over:

  * the squint grid 0..26.9 deg (registered SLS cap), step 0.5 deg
  * rho_req sampled over the fine tier [0.3, 0.6] m (SLS routing range)
  * the library platform fixture (Wa = 5 km scene, R0 = 775.4 km)

Both chains are evaluated at the SAME (psi, rho, geo), so the comparison
isolates the construction difference (symmetric span vs exact end squint).

Usage (repo root):
    PYTHONPATH=src:papers/sliding-spotlight-scheduling python \
        papers/sliding-spotlight-scheduling/scripts/run_dwell_exact_check.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))
sys.path.insert(0, str(FORK.parent.parent / "src"))

from sss_core.duration import kim_checker_scene_sls, kim_eq23_theta_s1  # noqa: E402
from sss_core.modes import ModeLibrary  # noqa: E402

OUT = FORK / "experiments" / "v5_results" / "dwell_exact_check.json"

SLS_CAP_DEG = 26.9
RHOS = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]


def main() -> int:
    lib = ModeLibrary.from_fixture()
    geo = lib.geo
    rows = []
    worst = None
    grid_deg = [i * 0.5 for i in range(int(SLS_CAP_DEG * 2))] + [SLS_CAP_DEG]
    for psi_deg in grid_deg:
        psi = math.radians(psi_deg)
        for rho in RHOS:
            prod = kim_checker_scene_sls(psi, rho, geo)["sat_raw_s"]
            try:
                ex = kim_eq23_theta_s1(psi, rho, geo)
            except ValueError:
                rows.append({"psi_deg": psi_deg, "rho_m": rho,
                             "exact_status": "no_real_root"})
                continue
            exact_sat = ex["L_form2_m"] / geo.vs_mps
            rel = (prod - exact_sat) / exact_sat
            rows.append({"psi_deg": psi_deg, "rho_m": rho,
                         "prod_sat_s": prod, "exact_sat_s": exact_sat,
                         "rel_dev": rel, "identity_rel_gap": ex["identity_rel_gap"]})
            if worst is None or abs(rel) > abs(worst["rel_dev"]):
                worst = rows[-1]
    OUT.write_text(json.dumps({
        "comparison": "kim_checker_scene_sls (production, symmetric span) vs "
                      "kim_eq23_theta_s1 exact chain, matched psi/rho/geo",
        "platform": "library fixture (Wa=5 km, R0=775.4 km)",
        "n_points": len(rows),
        "worst": worst,
        "max_abs_rel_dev": max(abs(r.get("rel_dev", 0.0)) for r in rows),
        "dev_at_12deg": [r for r in rows if r["psi_deg"] == 12.0 and r["rho_m"] == 0.5][0],
        "dev_at_cap": [r for r in rows if r["psi_deg"] == SLS_CAP_DEG and r["rho_m"] == 0.5][0],
    }, indent=1), encoding="utf-8")
    print(f"# points={len(rows)} worst rel dev={worst['rel_dev']:+.4%} "
          f"@ psi={worst['psi_deg']}deg rho={worst['rho_m']}m")
    d12 = [r for r in rows if r["psi_deg"] == 12.0 and r["rho_m"] == 0.5][0]
    print(f"# @12deg rho=0.5: rel dev={d12['rel_dev']:+.4%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
