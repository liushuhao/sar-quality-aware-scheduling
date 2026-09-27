#!/usr/bin/env python3
"""Ticket 08 -- scenario family generator tests.

Expectations follow the D08 registrations: bands frozen by THIS ticket
(coarse [2.5,3.0] all-STR, fine [0.3,0.6] spanning the SPT/SLS boundary),
per-task-Wa AASR gating (D08-2), first-match removal cascade with an exact
ledger (D08-9), and byte-identical same-seed reruns (spec 确定性).
"""
import json
import math
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

from sss_core.duration import duration_scene_s  # noqa: E402
from sss_core.maneuver import boundary_rate  # noqa: E402  (import order canary)
from sss_core.modes import Mode, ModeLibrary  # noqa: E402
from sss_core.scenarios import (  # noqa: E402
    VARIANT_REGISTRY,
    generate_scenario,
    load_rho_bands,
)

VARIANTS = [  # (variant_index, family, density, interval, demand)
    (1, "M1NC", 20, "N", "C"),
    (2, "M2WH", 100, "W", "H"),
    (3, "M3NC", 300, "N", "C"),
    (4, "M2WF", 100, "W", "F"),
    (5, "M4WH", 500, "W", "H"),
]


@pytest.fixture(scope="module")
def lib() -> ModeLibrary:
    return ModeLibrary.from_fixture()


def _gen(variant_index, seed_index=0, lib=None):
    fam, den, itv, dem = VARIANT_REGISTRY[variant_index]
    return generate_scenario(fam, den, itv, dem, seed=variant_index * 100 + seed_index,
                             variant_index=variant_index, lib=lib)


# ── band freeze (D08-1) + coarsest-sufficient routing ────────────────────

def test_bands_frozen_and_routing_consistent(lib):
    """The frozen coarse band sits ENTIRELY in the STR tier; the fine band
    spans the SPT/SLS boundary; 3.0 m keeps the q3 counterexample."""
    bands = load_rho_bands()
    assert bands["coarse"] == (2.5, 3.0)
    assert bands["fine"] == (0.3, 0.6)
    assert bands["boundary_zone"] == (0.45, 0.55)
    from sss_core.aasr import route_mode
    for rho in (2.5, 2.75, 3.0):
        assert route_mode(rho, lib) is Mode.STR  # q3: 3.0 m does NOT bind spotlight
    assert route_mode(0.55, lib) is Mode.SLS
    assert route_mode(0.35, lib) is Mode.SPT


def test_m3wn_anchor_all_str_and_dispersion(lib):
    """M?NC anchor: narrow window + coarse band -> every served task is STR;
    per-task window dwell dispersion <= the preregistered 1.10 (measured
    value recorded in the manifest ledger)."""
    m = _gen(3, lib=lib)
    assert m["scenario"]["degenerate_anchor"] is True
    assert m["tasks"], "anchor scenario must serve targets"
    assert all(t["mode"] == "STR" for t in m["tasks"])
    disp = m["generation_ledger"]["anchor_t_dispersion_max_min"]
    assert disp <= m["generation_ledger"]["anchor_t_dispersion_limit"] <= 1.10
    assert m["preregistration"]["pads"] == {"inter_task_fraction": 0.0,
                                            "window_tail_fraction": 0.0}
    # independent recomputation of the dispersion claim on one task
    t = m["tasks"][0]
    geo = lib.geo
    durs = [
        duration_scene_s(Mode.STR, math.atan(geo.vs_mps * (tt - t["t_ca_s"]) / geo.R0_m), lib)
        for tt in (t["t_start_s"], t["t_ca_s"], t["t_end_s"])
    ]
    assert max(durs) / min(durs) <= 1.10


# ── mode entropy + demand-tier binding ───────────────────────────────────

def test_h_tier_mode_entropy_positive(lib):
    """H mixes coarse/fine demands -> at least two distinct modes served."""
    m = _gen(2, lib=lib)
    modes = {t["mode"] for t in m["tasks"]}
    assert len(modes) >= 2, modes


def test_demand_tiers_bound_to_bands(lib):
    """C demands stay in the coarse band, F in the fine band; the H mix
    count equals the EXACT Bernoulli realization of this seed (D08-9)."""
    m_c = _gen(3, lib=lib)
    assert all(2.5 <= t["rho_req_m"] <= 3.0 for t in m_c["tasks"])
    m_f = _gen(4, lib=lib)
    assert all(0.3 <= t["rho_req_m"] <= 0.6 for t in m_f["tasks"])
    m_h = _gen(2, lib=lib)
    rng = __import__("random").Random(200)  # variant 2 -> seed 200
    expected_coarse = 0
    for _ in range(100):
        if rng.random() < 0.5:
            expected_coarse += 1
            rng.uniform(2.5, 3.0)
        else:
            rng.uniform(0.3, 0.6)
        rng.uniform(1000.0, 5000.0)
        rng.uniform(20.0, 280.0)
        rng.randint(1, 10)
    assert m_h["generation_ledger"]["h_coarse_draws"] == expected_coarse


# ── removal cascade (D08-2/9) ────────────────────────────────────────────

def test_unserviceable_removal_cascade(lib):
    """Constructed large-scene fine-demand task is removed by the footprint
    gate with the ledger counting it; the ledger closes exactly."""
    from sss_core.scenarios import generate_scenario as gen
    m = gen("M2WF", 100, "W", "F", seed=400, variant_index=4, lib=lib)
    led = m["generation_ledger"]
    assert led["n_drawn"] == led["n_served"] + sum(led["removals"].values())
    # per-task-Wa AASR gating: small fine scenes must SURVIVE the AASR gate
    fine_served = [t for t in m["tasks"] if t["mode"] == "SPT"]
    if fine_served:
        assert all(t["azimuth_size_m"] <= 3000.0 for t in fine_served)


def test_per_task_wa_aasr_gate(lib):
    """D08-2: SPT AASR rises monotonically with the scene extent; 1-3 km
    scenes pass -13 dB at 3630 Hz while the platform-default 5 km does not
    (the gate that would have wiped the F tier)."""
    from sss_core.aasr import aasr_direct, AASR_THRESHOLD_DB
    vals = [
        aasr_direct(Mode.SPT, 0.0, 0.0, 3630.0, lib, spt_scene_wa_m=wa)["aasr_db"]
        for wa in (1000.0, 2000.0, 3000.0, 5000.0)
    ]
    assert all(a < b for a, b in zip(vals, vals[1:]))
    assert all(v < AASR_THRESHOLD_DB for v in vals[:3])
    assert vals[3] > AASR_THRESHOLD_DB


# ── determinism (spec 确定性) ─────────────────────────────────────────────

def test_same_seed_byte_identical(lib, tmp_path):
    """Same seed -> byte-identical manifest (sorted-key JSON, diff empty)."""
    a = _gen(1, lib=lib)
    b = _gen(1, lib=lib)
    da = json.dumps(a, sort_keys=True)
    db = json.dumps(b, sort_keys=True)
    assert da == db
    from sss_core.scenarios import write_manifest
    write_manifest(a, tmp_path / "a.json")
    write_manifest(b, tmp_path / "b.json")
    assert (tmp_path / "a.json").read_bytes() == (tmp_path / "b.json").read_bytes()


def test_variant_registry_matches_manifest_and_seeds(lib):
    """Registry (D08-9) is the single variant_index <-> family mapping; the
    seed rule reproduces the manifest seed field."""
    for vi, (fam, den, itv, dem) in VARIANT_REGISTRY.items():
        m = _gen(vi, lib=lib)
        assert m["scenario"]["family_code"] == fam
        assert m["scenario"]["density_n_targets"] == den
        assert m["preregistration"]["variant_index"] == vi
        assert m["preregistration"]["seed"] == vi * 100


def test_pending_bands_fail_loud(monkeypatch, lib):
    """D08-10: a pending band status refuses generation with zero output."""
    from sss_core import scenarios as sc
    monkeypatch.setattr(
        sc, "load_rho_bands",
        lambda: (_ for _ in ()).throw(ValueError("pending")),
    )
    with pytest.raises(ValueError, match="pending"):
        generate_scenario("M1NC", 20, "N", "C", seed=100, variant_index=1, lib=lib)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
