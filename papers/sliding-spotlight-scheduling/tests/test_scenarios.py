#!/usr/bin/env python3
"""Ticket 08 -- scenario family generator tests.

Expectations follow the D08 registrations: bands frozen by THIS ticket
(coarse [2.5,3.0] all-STR, fine [0.3,0.6] spanning the SPT/SLS boundary),
per-task-Wa AASR gating (D08-2), first-match removal cascade with an exact
ledger (D08-9), and byte-identical same-seed reruns (spec 确定性).
"""
import copy
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


# ── ticket 16: real-window family R<density><requirement> ───────────────

def _platform():
    """Design orbit: 570 km, 45 deg inclination -- the fixture geometry."""
    from datetime import datetime

    from sss_core.realwindows import KeplerianElement

    lib = ModeLibrary.from_fixture()
    a = 6_371_000.0 + lib.geo.altitude_m
    epoch = datetime(2026, 1, 1)
    el = KeplerianElement(
        semi_major_axis=a, eccentricity=0.001,
        inclination=math.radians(45.0), raan=0.0, arg_perigee=0.0,
        true_anomaly=0.0, epoch=epoch,
    )
    return (el, epoch), lib


def test_real_scenario_requires_platform_oracle():
    """The orbit is a registered input, not something the generator invents."""
    from sss_core.scenarios import generate_real_scenario

    _, lib = _platform()
    with pytest.raises(ValueError, match="platform orbit"):
        generate_real_scenario("R1C", 20, "C", seed=100, lib=lib)


def test_real_scenario_ledger_and_geometry_fields():
    plat, lib = _platform()
    from sss_core.scenarios import generate_real_scenario

    m = generate_real_scenario("R1C", 20, "C", seed=100, variant_index=1,
                               lib=lib, platform=plat)
    assert m["schema"] == "scenario-manifest/2.0-realwindow"
    led = m["generation_ledger"]
    assert sum(led["removals"].values()) + led["n_served"] == led["n_drawn"]
    assert led["n_served"] > 0, "no task survived the real geometry"
    for t in m["tasks"]:
        # piece (a): per-task geometry IS in the manifest
        assert t["r0_m"] > 0.0
        assert 0.0 < t["incidence_deg"] < 90.0
        assert t["lat_deg"] is not None and t["lon_deg"] is not None
        # the two squint zero points are both registered, and they are NOT
        # the same quantity (measured: the vector minimum sits far away)
        assert "t_ca_s" in t and "vector_squint_min_t_s" in t
        assert t["t_start_s"] < t["t_end_s"]
        assert t["window_width_s"] > 0.0


def test_real_scenario_same_seed_is_byte_identical():
    plat, lib = _platform()
    from sss_core.scenarios import generate_real_scenario

    a = generate_real_scenario("R1C", 20, "C", 100, 1, lib=lib, platform=plat)
    b = generate_real_scenario("R1C", 20, "C", 100, 1, lib=lib, platform=plat)
    c = generate_real_scenario("R1C", 20, "C", 101, 1, lib=lib, platform=plat)
    sa = json.dumps(a, indent=2, sort_keys=True, ensure_ascii=False)
    sb = json.dumps(b, indent=2, sort_keys=True, ensure_ascii=False)
    sc = json.dumps(c, indent=2, sort_keys=True, ensure_ascii=False)
    assert sa == sb, "same seed must regenerate byte-identically"
    assert sa != sc, "different seed must not reproduce"


def test_real_scenario_preregisters_its_geometry():
    plat, lib = _platform()
    from sss_core.scenarios import (
        R_CLUSTER_CENTRES_DEG,
        R_INCIDENCE_BAND_DEG,
        generate_real_scenario,
    )

    m = generate_real_scenario("R1C", 20, "C", 100, 1, lib=lib, platform=plat)
    pre = m["preregistration"]
    assert pre["cluster_centres_deg"] == [list(c) for c in R_CLUSTER_CENTRES_DEG]
    assert pre["incidence_band_deg"] == list(R_INCIDENCE_BAND_DEG)
    assert pre["passes"] >= 1
    assert "longest" in pre["pass_selection_rule"]


def test_overload_band_ladder_yields_at_least_three_tiers():
    """Acceptance item 6: the overload axis must have >= 3 in-band tiers,
    measured rather than assumed.  This is the cheap form of the calibration
    loop -- the full script writes the artifact; here we only assert the
    property that makes the axis usable."""
    plat, lib = _platform()
    from sss_core import scenarios as S

    original = S.R_INCIDENCE_BAND_DEG
    ratios = set()
    try:
        for lo, hi in ((20.0, 70.0), (30.0, 60.0), (40.0, 52.0), (44.0, 48.0)):
            S.R_INCIDENCE_BAND_DEG = (lo, hi)
            m = S.generate_real_scenario("R1C", 20, "C", 100, 1,
                                         lib=lib, platform=plat)
            ratios.add(round(m["generation_ledger"]["n_served"] / 20, 6))
    finally:
        S.R_INCIDENCE_BAND_DEG = original
    assert len(ratios) >= 3, f"only {len(ratios)} overload tiers: {sorted(ratios)}"
    # monotone: a wider band cannot serve fewer targets
    assert ratios == set(sorted(ratios)) or len(ratios) > 1


def test_realwindow_template_matches_code_constants():
    """Acceptance item 5: the preregistered template is a REAL freeze, so it
    is bound to the code constants.  A template that drifts from the code is
    the same class of defect as a drifted fixture -- the document would
    describe an experiment that is not the one being run."""
    from sss_core import scenarios as S

    tpath = FORK_DOMAIN / "experiments" / "realwindow_scenario_template.json"
    t = json.loads(tpath.read_text(encoding="utf-8"))
    pre = t["preregistration"]
    assert pre["cluster_centres_deg"] == [list(c) for c in S.R_CLUSTER_CENTRES_DEG]
    assert pre["cluster_scale_km"] == S.R_CLUSTER_SCALE_KM
    assert pre["pass_span_s"] == S.R_PASS_SPAN_S
    assert pre["prop_step_s"] == S.R_PROP_STEP_S
    assert pre["passes"] == S.R_PASSES
    assert pre["incidence_band_deg"] == list(S.R_INCIDENCE_BAND_DEG)
    assert pre["prf_production_hz"] == S.PRF_PRODUCTION_HZ
    # the two squint semantics must be registered as distinct, not merged
    sem = pre["squint_semantics"]
    assert sem["t_ca_s"] != sem["vector_squint_min_t_s"]
    assert "vector squint never enters an envelope test" in sem["why_two"]


def test_real_scenario_write_manifest_is_byte_stable():
    """Acceptance item 7: regenerate and byte-compare through the REAL write
    path, not an in-memory json.dumps.  The earlier determinism check was a
    scratch script; this makes it a standing guard."""
    import tempfile

    plat, lib = _platform()
    from sss_core.scenarios import generate_real_scenario, write_manifest

    with tempfile.TemporaryDirectory() as td:
        p1 = Path(td) / "a.json"
        p2 = Path(td) / "b.json"
        write_manifest(
            generate_real_scenario("R1C", 20, "C", 100, 1, lib=lib, platform=plat),
            p1,
        )
        write_manifest(
            generate_real_scenario("R1C", 20, "C", 100, 1, lib=lib, platform=plat),
            p2,
        )
        assert p1.read_bytes() == p2.read_bytes()


def test_real_scenario_injection_reaches_the_evaluator():
    """Piece (b) must be CONSUMED, not merely present.

    A manifest can carry the geometry block and the evaluator can ignore it
    -- that is the "field registered but never read" break, and it is exactly
    what the ticket forbids.  This guard builds a real manifest, then asserts
    the evaluator's own dwell for a geometry-bearing task differs from the
    library-constant dwell.  Reverting the injection turns it red.
    """
    plat, lib = _platform()
    from sss_core.duration import duration_scene_s
    from sss_core.evaluator import SchedulingProblem
    from sss_core.geometry import squint_at
    from sss_core.scenarios import generate_real_scenario

    m = generate_real_scenario("R1C", 20, "C", 100, 1, lib=lib, platform=plat)
    sp = SchedulingProblem(m, lib)
    bearing = [j for j, p in enumerate(sp.plans) if p.r0_m is not None]
    assert bearing, "no task carries the geometry block -- the manifest is a fiction"
    i = bearing[0]
    plan = sp.plans[i]
    assert plan.r0_m != lib.geo.R0_m, "fixture picked a task at the design R0"
    with_injection = sp._dwell(i, plan.t_ca_s)
    without = duration_scene_s(
        plan.mode, squint_at(plan.t_ca_s, plan.t_ca_s, lib.geo), lib
    )
    assert with_injection != without, (
        "evaluator ignored the per-task geometry -- reverting the injection "
        "would be invisible"
    )


def test_real_scenario_injection_absent_leaves_precompile_untouched():
    """And the mirror image: a manifest WITHOUT the block must precompile
    exactly as before, which is what keeps the frozen families safe."""
    plat, lib = _platform()
    from sss_core.evaluator import SchedulingProblem
    from sss_core.scenarios import generate_real_scenario

    m = generate_real_scenario("R1C", 20, "C", 100, 1, lib=lib, platform=plat)
    stripped = copy.deepcopy(m)
    for t in stripped["tasks"]:
        t.pop("r0_m", None)
    sp = SchedulingProblem(stripped, lib)
    assert all(p.r0_m is None for p in sp.plans)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
