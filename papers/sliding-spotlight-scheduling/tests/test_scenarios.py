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


# ── ticket 25: real-window family, ground-track transit enumeration ──────
#
# The pre-ticket-25 world (8 clusters sampled at epoch + {0, 600} s) yielded
# ZERO servable tasks after the ticket-24 incidence fix -- measured, not
# assumed: 600 s is 37.5 deg of true anomaly and is not a ground-track
# crossing (ledger R22).  Ticket 25 re-derives the pass enumeration
# (AD-2), moves the dense region to a single 5x5 domain at 20N/0E (AD-4)
# and re-bases the ladder to 20/50/100 (AD-5).  The four tests that were
# parked on R22_BLOCKED are re-derived here against the new world, plus
# the three mutation red-proofs the ticket registers.

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


def _gen_real(variant_index=1, lib=None):
    """One real-window manifest: R1C (N=20, C) by default."""
    from datetime import datetime

    from sss_core.realwindows import KeplerianElement
    from sss_core.scenarios import generate_real_scenario

    lib = lib or ModeLibrary.from_fixture()
    a = 6_371_000.0 + lib.geo.altitude_m
    epoch = datetime(2026, 1, 1)
    plat = (
        KeplerianElement(
            semi_major_axis=a, eccentricity=0.001,
            inclination=math.radians(45.0), raan=0.0, arg_perigee=0.0,
            true_anomaly=0.0, epoch=epoch,
        ),
        epoch,
    )
    fam, den, tier = {1: ("R1C", 20, "C"), 2: ("R2F", 50, "F"),
                      3: ("R3H", 100, "H")}[variant_index]
    return generate_real_scenario(fam, den, tier, variant_index * 100,
                                  variant_index, lib=lib, platform=plat)


def test_real_scenario_requires_platform_oracle():
    """The orbit is a registered input, not something the generator invents."""
    from sss_core.scenarios import generate_real_scenario

    _, lib = _platform()
    with pytest.raises(ValueError, match="platform orbit"):
        generate_real_scenario("R1C", 20, "C", seed=100, lib=lib)


def test_real_passes_from_ground_track_and_offset_rule_is_red():
    """MUST-2 + the AD-2 red proof (ledger R22's discriminator).

    Green half: under ground-track enumeration the R1C domain serves every
    drawn target through the FULL four-leg cascade (incidence n envelope n
    end-check n AASR) -- a served task is four-leg clean by construction of
    the generator's per-window cascade.

    Red half: reverting the enumeration to the v1 rule (in-band runs within
    +-120 s of epoch + {0, 600} s) yields ZERO passes -- those offsets are
    arbitrary phase points, measured ~6000 s away from the nearest in-band
    transit at this domain.  A revert must empty the scenario, not merely
    shrink it.
    """
    import numpy as np

    from sss_core import scenarios as S

    plat, lib = _platform()
    m = S.generate_real_scenario("R1C", 20, "C", 100, 1, lib=lib, platform=plat)
    led = m["generation_ledger"]
    assert led["n_served"] == 20, led
    assert sum(led["removals"].values()) + led["n_served"] == led["n_drawn"]
    assert led["n_windows_total"] >= 20
    assert led["windows_per_task_max"] >= 2, (
        "fixture lost its multi-transit structure -- the per-window t_ca "
        "schema would be untested on generated data"
    )

    # mutation: the v1 offset rule, expressed through the same enumeration
    # interface (in-band runs near epoch + {0, 600} s only)
    real_passes = S._ground_track_passes

    def offset_rule_passes(elements, epoch, target, track_times, track_ecef,
                           band, step_s, gap_merge_s):
        pos, _ = S._ecef_track(
            elements, epoch,
            np.concatenate([np.arange(-120.0, 120.0 + step_s, step_s)
                            + 0.0, np.arange(480.0, 720.0 + step_s, step_s)]),
        )
        # rebuild in-band runs on the two legacy spans only
        from datetime import timedelta

        from sss_core.realwindows import kepler_to_eci, satellite_to_target_vector

        def inc(t):
            st = kepler_to_eci(elements, epoch + timedelta(seconds=float(t)))
            return satellite_to_target_vector(st, target)[4]

        passes = []
        for base in (0.0, 600.0):
            runs, start = [], None
            for k in range(int(240.0 / step_s) + 1):
                t = base - 120.0 + k * step_s
                ok = band[0] <= inc(t) <= band[1]
                if ok and start is None:
                    start = t
                elif not ok and start is not None:
                    runs.append((start, t - step_s))
                    start = None
            if start is not None:
                runs.append((start, base + 120.0))
            for lo, hi in runs:
                passes.append((lo, hi, [(lo, hi)]))
        return passes

    S._ground_track_passes = offset_rule_passes
    try:
        m_old = S.generate_real_scenario(
            "R1C", 20, "C", 100, 1, lib=lib, platform=plat)
    finally:
        S._ground_track_passes = real_passes
    assert m_old["generation_ledger"]["n_served"] == 0, (
        "the offset-rule mutation still serves targets -- the red proof "
        "lost its discrimination"
    )


def test_pass_enumeration_gap_merge_is_a_robust_band_parameter():
    """Registered robustness: the pass count must be invariant across
    {150, 300, 600, 1200} s -- the threshold is a band parameter, NOT a
    physical bound (AD-2), and the invariant is guard-tested."""
    import numpy as np

    from sss_core import scenarios as S
    from sss_core.realwindows import GroundTarget

    plat, lib = _platform()
    elements, epoch = plat
    step = S.R_ENUM_STEP_S
    times = np.arange(0.0, S.R_SPAN_S + 0.5 * step, step)
    pos, _ = S._ecef_track(elements, epoch, times)
    # a jittered target shape: node 12 (domain centre) with a fixed offset
    target = GroundTarget(target_id="G", lat=20.3, lon=0.4)
    counts = {
        g: len(S._ground_track_passes(
            elements, epoch, target, times, pos,
            S.R_INCIDENCE_BAND_DEG, step, g))
        for g in (150.0, 300.0, 600.0, 1200.0)
    }
    assert len(set(counts.values())) == 1, counts
    assert counts[300.0] >= 3, counts  # measured 6 at the centre node


def test_t_ca_at_returns_per_window_zero():
    """AD-3 red-proof carrier: with multiple windows the squint zero is
    PER WINDOW; a mutation returning a single scalar t_ca would make the
    two reads equal (zero discrimination)."""
    from sss_core.evaluator import precompile_tasks
    from sss_core.modes import ModeLibrary

    lib = ModeLibrary.from_fixture()
    manifest = {
        "preregistration": {"pads": {"inter_task_fraction": 0.0,
                                     "window_tail_fraction": 0.0}},
        "tasks": [
            {
                "t_start_s": 0.0, "t_end_s": 130.0,
                "azimuth_size_m": 2000.0, "priority": 5, "rho_req_m": 3.0,
                "mode": "STR", "prf_hz": 3630.0,
                "windows": [
                    {"lo_s": 0.0, "hi_s": 20.0, "t_ca_s": 10.0,
                     "r0_m": None, "incidence_deg": 45.0},
                    {"lo_s": 90.0, "hi_s": 110.0, "t_ca_s": 100.0,
                     "r0_m": None, "incidence_deg": 45.0},
                ],
            },
        ],
    }
    plan = precompile_tasks(manifest, lib)[0]
    assert plan.t_ca_at(0.0) == 10.0
    assert plan.t_ca_at(20.0) == 10.0   # closed interval at the window edge
    assert plan.t_ca_at(90.0) == 100.0
    assert plan.t_ca_at(110.0) == 100.0
    assert plan.t_ca_at(95.0) != plan.t_ca_at(15.0), (
        "per-window zeros collapsed -- a scalar t_ca mutation would pass"
    )
    with pytest.raises(ValueError, match="outside every window"):
        plan.window_at(50.0)


def test_taskplan_windows_must_not_overlap():
    """AD-3 invariant, asserted not assumed: window interiors never overlap
    (touching endpoints are allowed and resolved by first match)."""
    from sss_core.evaluator import TaskPlan, TaskWindow
    from sss_core.modes import Mode, ModeLibrary

    lib = ModeLibrary.from_fixture()
    base = dict(index=0, priority=1, rho_req_m=3.0, mode=Mode.STR,
                prf_hz=3630.0, azimuth_size_m=2000.0, intervals=(),
                priority_f=1.0)
    TaskPlan(**base, windows=(
        TaskWindow(lo=0.0, hi=10.0, t_ca_s=5.0),
        TaskWindow(lo=10.0, hi=20.0, t_ca_s=15.0),  # touching: allowed
    ))
    with pytest.raises(ValueError, match="overlap"):
        TaskPlan(**base, windows=(
            TaskWindow(lo=0.0, hi=11.0, t_ca_s=5.0),
            TaskWindow(lo=10.0, hi=20.0, t_ca_s=15.0),
        ))


def test_window_subset_of_incidence_interval():
    """AD-6 (ledger R18): the emitted windows are inside the 30-60 deg
    incidence band because the incidence leg JOINS the cascade
    intersection.  Red proof: dropping the incidence leg from the
    intersection must emit at least one window whose edge leaves the band
    (the envelope leg alone spans +-120 s around t_ca, wider than the
    in-band runs)."""
    from sss_core import scenarios as S
    from sss_core.realwindows import kepler_to_eci, satellite_to_target_vector
    from sss_core import windows as W
    from datetime import timedelta

    plat, lib = _platform()
    elements, epoch = plat
    m = _gen_real(lib=lib)

    def endpoint_incidences(manifest):
        from sss_core.realwindows import GroundTarget

        vals = []
        for t in manifest["tasks"]:
            target = GroundTarget(target_id="X", lat=t["lat_deg"],
                                  lon=t["lon_deg"])
            for w in t["windows"]:
                for tt in (w["lo_s"], w["hi_s"]):
                    st = kepler_to_eci(elements, epoch + timedelta(seconds=tt))
                    vals.append(satellite_to_target_vector(st, target)[4])
        return vals

    real = endpoint_incidences(m)
    assert real, "no windows generated"
    lo_b, hi_b = S.R_INCIDENCE_BAND_DEG
    assert all(lo_b - 1e-6 <= v <= hi_b + 1e-6 for v in real), (
        "a window edge left the incidence band with the AD-6 leg in place"
    )

    # mutation: intersect WITHOUT the incidence leg (3-set calls drop set 0)
    real_intersect = W.intersect_intervals

    def drop_incidence(*sets):
        return real_intersect(*sets[1:]) if len(sets) >= 3 else real_intersect(*sets)

    W.intersect_intervals = drop_incidence
    try:
        m_mut = _gen_real(lib=lib)
    finally:
        W.intersect_intervals = real_intersect
    mutated = endpoint_incidences(m_mut)
    assert any(not (lo_b - 1e-6 <= v <= hi_b + 1e-6) for v in mutated), (
        "dropping the incidence leg did NOT move any window edge out of "
        "band -- the AD-6 red proof lost its discrimination"
    )


def test_real_scenario_ledger_and_window_fields():
    """Schema 2.1: per-window geometry blocks, span scalars, ledger close."""
    m = _gen_real()
    assert m["schema"] == "scenario-manifest/2.1-realwindow"
    led = m["generation_ledger"]
    assert sum(led["removals"].values()) + led["n_served"] == led["n_drawn"]
    assert led["n_served"] > 0
    for t in m["tasks"]:
        assert t["windows"], "served task without windows"
        los = [w["lo_s"] for w in t["windows"]]
        assert los == sorted(los), "windows must be sorted by lo_s"
        assert t["t_start_s"] == los[0]
        assert t["t_end_s"] == max(w["hi_s"] for w in t["windows"])
        for a, b in zip(t["windows"], t["windows"][1:]):
            assert a["hi_s"] <= b["lo_s"], "window interiors overlap"
        for w in t["windows"]:
            assert w["r0_m"] > 0.0
            assert 30.0 <= w["incidence_deg"] <= 60.0
            assert w["t_ca_s"] is not None
            assert w["width_s"] > 0.0


def test_high_cross_track_fixture_rejects_a_reverted_injection():
    """Ticket 16 mutation item, re-based on the dense domain (ticket 25):
    the fixture must witness a per-window-r0 revert.  Incidences span the
    30-60 band, so the per-pass slant range spreads far off the library
    constant; the evaluator's own dwell for a geometry-bearing task must
    differ from the library-constant dwell by > 5%.
    """
    from sss_core.duration import duration_scene_s
    from sss_core.evaluator import SchedulingProblem
    from sss_core.geometry import squint_at

    lib = ModeLibrary.from_fixture()
    m = _gen_real(variant_index=2, lib=lib)  # R2F: fine demand -> SLS/SPT mix
    sp = SchedulingProblem(m, lib)
    bearing = [p for p in sp.plans if any(w.r0_m is not None for w in p.windows)]
    assert bearing, "no task carries per-window geometry"
    base = lib.geo.R0_m
    spread = max(
        abs(w.r0_m - base) / base
        for p in bearing for w in p.windows if w.r0_m is not None
    )
    assert spread > 0.20, (
        f"fixture lost its cross-track spread ({spread:.4f}); a revert would "
        "be invisible again"
    )
    plan = max(
        bearing,
        key=lambda p: max(abs(w.r0_m - base) for w in p.windows
                          if w.r0_m is not None),
    )
    w = max(plan.windows, key=lambda w: abs(w.r0_m - base))
    start = 0.5 * (w.lo + w.hi)  # inside the window, in window_at's domain
    with_injection = sp._dwell(plan.index, start)
    without = duration_scene_s(
        plan.mode, squint_at(start, w.t_ca_s, lib.geo), lib
    )
    assert with_injection != without
    assert abs(with_injection - without) / without > 0.05, (
        "high cross-track fixture still too weak to witness a revert"
    )


def test_overload_band_ladder_yields_at_least_three_tiers():
    """Acceptance item 6 (re-based): the overload axis must have >= 3
    in-band tiers, measured rather than assumed."""
    from sss_core import scenarios as S

    plat, lib = _platform()
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


def test_ecef_track_array_matches_scalar_geometry():
    """The vectorized incidence readout is pinned to the frozen scalar
    definition (realwindows.satellite_to_target_vector) at <= 1e-9 deg."""
    import numpy as np

    from sss_core import scenarios as S
    from sss_core.realwindows import (
        GroundTarget,
        kepler_to_eci,
        satellite_to_target_vector,
    )
    from datetime import timedelta

    plat, lib = _platform()
    elements, epoch = plat
    target = GroundTarget(target_id="G", lat=20.3, lon=0.4)
    times = np.arange(0.0, 6000.0, 250.0)
    pos, _ = S._ecef_track(elements, epoch, times)
    arr = S._incidence_deg_array(pos, target)
    for t, a in zip(times, arr):
        st = kepler_to_eci(elements, epoch + timedelta(seconds=float(t)))
        scalar = satellite_to_target_vector(st, target)[4]
        assert abs(float(a) - scalar) <= 1e-9, (t, float(a), scalar)


def test_real_scenario_preregisters_its_geometry():
    """The manifest's preregistration block carries the enumeration design
    (AD-2/AD-4/AD-5/AD-9) as registered values, not prose."""
    from sss_core import scenarios as S

    m = _gen_real()
    pre = m["preregistration"]
    assert pre["domain_centre_deg"] == list(S.R_DOMAIN_CENTRE_DEG)
    assert pre["grid_n"] == S.R_GRID_N
    assert pre["grid_spacing_km"] == S.R_GRID_SPACING_KM
    assert pre["span_days"] == S.R_SPAN_DAYS
    assert pre["enum_step_s"] == S.R_ENUM_STEP_S
    assert pre["gap_merge_s"] == S.R_GAP_MERGE_S
    assert pre["incidence_band_deg"] == list(S.R_INCIDENCE_BAND_DEG)
    assert "vector-squint minimum" in pre["pass_enumeration_rule"]
    assert "gap_merge_s" in pre["pass_enumeration_rule"]


def test_realwindow_template_amendment_matches_code_constants():
    """AD-9 guard: the amendment's registered ladder is pinned to
    ``R_DENSITY_BY_INDEX`` (verify_prereg_v2 greps neither file, so THIS
    test is the drift guard), and the v1 frozen fields survive unrewritten
    (append-only discipline)."""
    import json as _json

    from sss_core import scenarios as S

    tpath = FORK_DOMAIN / "experiments" / "realwindow_scenario_template.json"
    t = _json.loads(tpath.read_text(encoding="utf-8"))
    # append-only: the frozen v1 fields are still verbatim
    assert t["scenario"]["density_n_targets"] == "<20 | 100 | 300 | 500>"
    assert t["preregistration"]["passes"] == 2
    am = t["amendment_20261005_ticket25"]
    ladder = [int(x) for x in
              am["density_n_targets"].strip("<>").split("|")]
    assert ladder == sorted(S.R_DENSITY_BY_INDEX.values()), (
        "template amendment ladder drifted from R_DENSITY_BY_INDEX"
    )
    dd = am["dense_domain"]
    assert dd["centre_deg"] == list(S.R_DOMAIN_CENTRE_DEG)
    assert dd["grid_spacing_km"] == S.R_GRID_SPACING_KM
    assert am["span_days"] == S.R_SPAN_DAYS
    assert am["enumeration"]["scan_step_s"] == S.R_ENUM_STEP_S
    assert am["enumeration"]["gap_merge_s"] == S.R_GAP_MERGE_S
    assert "R4H" in am["family_registry"]["retired"]


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


def test_real_scenario_injection_absent_leaves_precompile_untouched():
    """And the mirror image: windows WITHOUT the geometry block must
    precompile against the library constants, which is what keeps
    synthetic-style consumption safe."""
    from sss_core.evaluator import SchedulingProblem

    lib = ModeLibrary.from_fixture()
    m = _gen_real()
    stripped = copy.deepcopy(m)
    for t in stripped["tasks"]:
        for w in t["windows"]:
            w.pop("r0_m", None)
            w.pop("incidence_deg", None)
    sp = SchedulingProblem(stripped, lib)
    assert all(
        w.r0_m is None and w.incidence_deg is None
        for p in sp.plans for w in p.windows
    )


def test_real_scenario_injection_reaches_the_evaluator():
    """Piece (b) must be CONSUMED, not merely present: the evaluator's own
    dwell for a per-window-geometry start differs from the library-R0
    dwell.  Reverting the injection turns it red."""
    from sss_core.duration import duration_scene_s
    from sss_core.evaluator import SchedulingProblem
    from sss_core.geometry import squint_at

    lib = ModeLibrary.from_fixture()
    m = _gen_real()
    sp = SchedulingProblem(m, lib)
    bearing = [j for j, p in enumerate(sp.plans) if any(w.r0_m is not None for w in p.windows)]
    assert bearing, "no task carries the geometry block -- the manifest is a fiction"
    i = bearing[0]
    plan = sp.plans[i]
    w = next(w for w in plan.windows if w.r0_m is not None)
    assert w.r0_m != lib.geo.R0_m, "fixture picked a task at the design R0"
    start = 0.5 * (w.lo + w.hi)
    with_injection = sp._dwell(i, start)
    without = duration_scene_s(
        plan.mode, squint_at(start, w.t_ca_s, lib.geo), lib
    )
    assert with_injection != without, (
        "evaluator ignored the per-window geometry -- reverting the "
        "injection would be invisible"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
