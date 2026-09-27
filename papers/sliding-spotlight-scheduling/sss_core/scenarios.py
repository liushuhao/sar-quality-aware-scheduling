"""Scenario family generator ``M<d><i><r>`` (spec D2/D10, ticket 08).

Family code ``M<density 1-4><interval N|W><demand C|F|H>``; densities
20/100/300/500 inherit the Paper-1 gradient.  Preregistration lives in
``experiments/scenario_manifest_template.json`` (seed convention
``variant_index*100 + seed_index``; rho_req tiers bind BY REFERENCE to
``experiments/platform_kim2021.json#resolution.rho_req_bands`` -- values
are never copied here).

Ticket-08 decisions D08-1..10 (post gate-review; the review FAILED the
original design and forced two real fixes):

* D08-1 bands frozen by THIS ticket: coarse [2.5, 3.0] m (ENTIRELY inside
  the STR routing tier -- the original [1.0, 3.0] proposal leaked
  [1.0, 2.4669) into SLS and broke the M?NC all-STR anchor; reviewer
  recomputed on the frozen router), fine [0.3, 0.6] m (spans the SPT/SLS
  routing boundary so the F tier mixes modes on its own), boundary zone
  [0.45, 0.55] m (cheap-ablation prereg).  The 0.6 m upper edge is a
  registered design convention (no Kim source), like the SPT 0.3 library
  point.
* D08-2 per-task AASR gate: the SPT worst-edge evaluation uses the TASK's
  own azimuth extent (aasr_direct(spt_scene_wa_m=...)), not the platform
  5 km default -- a 1-3 km fine-demand scene is AASR-feasible while the
  5 km default is not; the platform default stays over-conservative for
  smaller scenes, never the reverse.
* D08-5 squint convention: with the frozen inertial Vs the squint rate is
  Vs/R0 = 0.56 deg/s, so the N window spans +-3.36 deg and the W window
  +-11.20 deg (both inside the +-12 deg envelope, asserted at generation).
* D08-6 priority = randint(1, 10), the exact Paper-1 convention
  (generate_all_scenarios.py:133), keeping the f1 axis same-source.
* D08-9 removals are FIRST-MATCH cascaded (below_finest -> footprint ->
  aasr) and the manifest must satisfy sum(buckets) + served == drawn.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from .aasr import AASR_THRESHOLD_DB, aasr_direct, route_mode
from .duration import MarginPads, duration_scene_s
from .fixture import fixture_value, load_platform_fixture
from .modes import Mode, ModeLibrary
from .windows import footprint_ok

FORK_DOMAIN = Path(__file__).resolve().parent.parent
RESULTS_DIR = FORK_DOMAIN / "experiments" / "results" / "scenarios"

# D08-9: variant registry (seed = variant_index * 100 + seed_index);
# the five ticket variants span the density gradient and all three demand
# tiers (M4WH: the original M4WW slip used an invalid demand letter 'W' --
# legal demand letters are C/F/H only)
VARIANT_REGISTRY = {
    1: ("M1NC", 20, "N", "C"),   # degenerate anchor (narrow + coarse -> all STR)
    2: ("M2WH", 100, "W", "H"),
    3: ("M3NC", 300, "N", "C"),
    4: ("M2WF", 100, "W", "F"),
    5: ("M4WH", 500, "W", "H"),
}

DENSITY_BY_INDEX = {1: 20, 2: 100, 3: 300, 4: 500}
INTERVAL_HALF_WIDTH_S = {"N": 6.0, "W": 20.0}  # D08-5: +-3.36 / +-11.20 deg
PASS_HORIZON_S = 300.0
PRF_PRODUCTION_HZ = 3630.0  # platform operating point (design convention)

ANCHOR_T_DISPERSION_LIMIT = 1.10  # spec D10 / Testing Decisions (preregistered)
H_MIX_DOCUMENTED_RANGE = (0.35, 0.65)  # documentation value; the test asserts
# the EXACT Bernoulli realization count for the seed (D08-9)


def load_rho_bands() -> dict:
    """Bind the frozen bands BY REFERENCE; fail loud if still pending
    (D08-10, manifest-template completeness rule)."""
    fx = load_platform_fixture()
    bands = fx["resolution"]["rho_req_bands"]
    if str(bands.get("status", "")).startswith("pending"):
        raise ValueError(
            "rho_req bands are still pending_D2_mapping_ticket: scenario "
            "generation must refuse to run (manifest-template completeness "
            "rule, D08-10)"
        )
    return {
        "coarse": tuple(float(v) for v in bands["coarse_band_m"]["value"]),
        "fine": tuple(float(v) for v in bands["fine_band_m"]["value"]),
        "boundary_zone": tuple(float(v) for v in bands["boundary_zone_m"]["value"]),
    }


def generate_scenario(
    family_code: str,
    density_n: int,
    interval: str,
    demand_tier: str,
    seed: int,
    variant_index: int | None = None,
    lib: ModeLibrary | None = None,
) -> dict:
    """Generate one scenario instance and return its manifest (dict).

    Determinism: the ONLY stochastic source is ``random.Random(seed)``,
    consumed in a fixed per-target order (demand -> size -> t_ca ->
    priority; the H Bernoulli draw precedes the demand draw), so the same
    seed reproduces the manifest byte-identically (spec 确定性).
    """
    if demand_tier not in ("C", "F", "H"):
        raise ValueError(f"invalid demand tier {demand_tier!r}")
    if interval not in INTERVAL_HALF_WIDTH_S:
        raise ValueError(f"invalid interval {interval!r}")
    if density_n not in DENSITY_BY_INDEX.values():
        raise ValueError(f"invalid density {density_n}")
    lib = lib or ModeLibrary.from_fixture()
    bands = load_rho_bands()  # D08-10 fail loud
    half_w = INTERVAL_HALF_WIDTH_S[interval]
    psi_max_window = math.atan(lib.geo.vs_mps * half_w / lib.geo.R0_m)
    if abs(psi_max_window) > math.radians(12.0):
        raise ValueError("window exceeds the +-12 deg squint envelope (D08-5 guard)")

    rng = random.Random(seed)
    tasks = []
    removals = {"below_finest": 0, "footprint": 0, "aasr": 0}
    h_draws = 0  # exact Bernoulli realization count (D08-9)
    dispersion = 1.0
    anchor = family_code.endswith("NC")

    for _ in range(density_n):
        # H: per-target Bernoulli(p=0.5) BEFORE the demand draw (fixed order)
        if demand_tier == "H":
            use_coarse = rng.random() < 0.5
            h_draws += int(use_coarse)
            band = bands["coarse"] if use_coarse else bands["fine"]
        else:
            band = bands["coarse"] if demand_tier == "C" else bands["fine"]
        rho_req = rng.uniform(*band)
        # size convention (D08-2 rationale): fine-resolution targets are
        # physically smaller scenes; the AASR/footprint gates remove the rest
        if band == bands["coarse"]:
            l_az_m = rng.uniform(2000.0, 5000.0)
        else:
            l_az_m = rng.uniform(1000.0, 3000.0)
        t_ca = rng.uniform(half_w, PASS_HORIZON_S - half_w)  # D08-7
        priority = rng.randint(1, 10)  # D08-6, Paper-1 convention

        # first-match removal cascade (D08-9)
        if rho_req < lib.rho_az(Mode.SPT) - 1e-12:
            removals["below_finest"] += 1
            continue
        mode = route_mode(rho_req, lib)
        if not footprint_ok(mode, l_az_m, lib):
            removals["footprint"] += 1
            continue
        psi_edge = math.atan(lib.geo.vs_mps * half_w / lib.geo.R0_m)
        aasr = aasr_direct(
            mode,
            psi_edge,
            lib.geo.k,
            PRF_PRODUCTION_HZ,
            lib,
            spt_scene_wa_m=(l_az_m if mode is Mode.SPT else None),
        )["aasr_db"]
        if not (aasr <= AASR_THRESHOLD_DB):
            removals["aasr"] += 1
            continue

        t0, t1 = t_ca - half_w, t_ca + half_w
        # window dwell dispersion (anchor property; sampled edges+centre)
        if anchor:
            ts = [t0, t_ca, t1]
            durs = [duration_scene_s(mode, _squint_at(t, t_ca, lib), lib) for t in ts]
            dispersion = max(dispersion, max(durs) / min(durs))
        tasks.append(
            {
                "t_start_s": round(t0, 9),
                "t_end_s": round(t1, 9),
                "t_ca_s": round(t_ca, 9),
                "azimuth_size_m": round(l_az_m, 6),
                "priority": priority,
                "rho_req_m": round(rho_req, 9),
                "mode": mode.name,
                "prf_hz": PRF_PRODUCTION_HZ,
            }
        )

    assert sum(removals.values()) + len(tasks) == density_n  # D08-9 ledger
    pads = MarginPads.degenerate_anchor() if anchor else MarginPads.standard()
    manifest = {
        "schema": "scenario-manifest/1.0",
        "scenario": {
            "family_code": family_code,
            "density_n_targets": density_n,
            "interval_width": interval,
            "demand_tier": demand_tier,
            "platform_fixture": "experiments/platform_kim2021.json",
            "degenerate_anchor": anchor,
        },
        "preregistration": {
            "seed": seed,
            "variant_index": variant_index,
            "seed_rule": "variant_index*100 + seed_index (ticket-02 template)",
            "rho_req_bands_source": (
                "experiments/platform_kim2021.json#resolution.rho_req_bands "
                "(bound by reference, frozen by ticket 08)"
            ),
            "pads": {
                "inter_task_fraction": pads.inter_task_fraction,
                "window_tail_fraction": pads.window_tail_fraction,
            },
            "prf_production_hz": PRF_PRODUCTION_HZ,
            "priority_convention": "randint(1,10) (Paper-1 generate_all_scenarios.py:133)",
        },
        "generation_ledger": {
            "n_drawn": density_n,
            "removals": removals,
            "n_served": len(tasks),
            "h_coarse_draws": h_draws,
            "anchor_t_dispersion_max_min": round(dispersion, 9),
            "anchor_t_dispersion_limit": ANCHOR_T_DISPERSION_LIMIT,
        },
        "tasks": tasks,
    }
    if anchor:
        assert dispersion <= ANCHOR_T_DISPERSION_LIMIT, dispersion
    return manifest


def _squint_at(t: float, t_ca: float, lib: ModeLibrary) -> float:
    """Planar squint at time t for a target with closest approach t_ca."""
    return math.atan(lib.geo.vs_mps * (t - t_ca) / lib.geo.R0_m)


def write_manifest(manifest: dict, path: Path) -> None:
    """Byte-stable manifest write (sorted keys; the same-seed rerun must
    produce an identical file, spec 确定性)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    import json

    path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
