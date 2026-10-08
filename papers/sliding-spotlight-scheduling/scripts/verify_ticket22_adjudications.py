#!/usr/bin/env python3
"""Ticket 22 machine check -- the A3 primary-comparison and A4 promotion
calibration adjudications, re-derived from the FROZEN artifacts.

Ticket 22 changed no source, so its adjudications would otherwise live only
in prose inside a gitignored scratch file.  This script makes them
executable: every number the ticket claims is recomputed here from
``experiments/results/`` and compared against the claim.  Ticket 17 consumes
the same verdicts when it freezes ``analysis_prereg_v2.json``, so drift
between the adjudication and the artifacts is caught BEFORE the freeze.

READS ONLY: papers/sliding-spotlight-scheduling/experiments/results/**
WRITES:      nothing (stdout report only)

Run with ``python -B`` (or PYTHONDONTWRITEBYTECODE=1) so that importing
``sss_core`` does not drop ``__pycache__/*.pyc`` next to the sources -- the
read-only claim then covers the filesystem, not just the artifacts.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/verify_ticket22_adjudications.py

rc:
  0  every checked number reproduces the ticket's claim
  1  at least one number DRIFTED (ticket 17 freeze blocker)
  2  usage / missing artifacts
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))
sys.path.insert(0, str(FORK.parent.parent / "src"))

from sss_core.aasr import PRF_KEYS_HZ, aasr_direct  # noqa: E402
from sss_core.geometry import squint_at  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402

RESULTS = FORK / "experiments" / "results"
MATRIX = RESULTS / "matrix"
SCENARIOS = RESULTS / "scenarios"
PROBE_MANIFESTS = RESULTS / "probe_density" / "manifests"
CONVERGENCE = RESULTS / "probe_convergence"

EXIT_OK, EXIT_DRIFT, EXIT_USAGE = 0, 1, 2

# ---- the ticket's claims (drift here means the adjudication is stale) -----
TICKET_A3_UNITS = 50
TICKET_A3_EXACT_TIE = 49
TICKET_A3_USABLE = 49          # units whose front still contains the anchor point
TICKET_A3_NONDEGEN = ("M2WF", "M2WH", "M4WH")
TICKET_A3_POOLED_N = 30
TICKET_A3_POOLED_SD = 1.05854
TICKET_A4_THRESHOLD_DB = 6.0
TICKET_A4_PLATEAU_MEDIAN_DB = 1.0
TICKET_A4_PLATEAU_UNIT_DB = 2.0
TICKET_A4_LOOSE_MEDIAN_DB = 10.0
TICKET_A4_LOOSE_UNIT_DB = 20.0
TICKET_A4_PLATFORM_RANGE_DB = 35.84  # re-measured 2026-10-07 ticket-40 (yi)
                                     # AASR semantics (formula-spec v1.7 §8.14);
                                     # old linearised-law value 71.03 was inflated
                                     # by the fake a_res collapse past 26.76 deg
TICKET_A4_M2WH_MEDIAN_DELTA = 1.892048
TICKET_A4_M2WH_UNIT_DELTA = 3.128066
TICKET_A4_FAMILY_R = {
    "M1NC": 0.037, "M2WF": 5.464, "M2WH": 5.379, "M3NC": 0.037, "M4WH": 5.499,
    "P6WH": 5.439, "P7WH": 5.456, "P8WH": 5.501, "P9WH": 5.303,
}
# matrix families are registered at one manifest; the density-probe families
# were drawn over 5 seeds and R_fam is the MAX over them (ticket caliber).
TICKET_A4_SINGLE_MANIFEST = ("M1NC", "M2WF", "M2WH", "M3NC", "M4WH")
TICKET_A4_PROBE_FAMILY = ("P6WH", "P7WH", "P8WH", "P9WH")
TICKET_A3_ANCHOR_LOST_UNIT = "pilot_M1NC_seed105.json"

_fails: list[str] = []
_checks = 0


def check(name: str, got, expect, tol: float = 0.0) -> None:
    global _checks
    _checks += 1
    if isinstance(expect, (int, float)) and not isinstance(expect, bool):
        ok = got is not None and not isinstance(got, bool) and abs(float(got) - float(expect)) <= tol
    else:
        ok = got == expect
    if not ok:
        _fails.append(f"{name}: got {got!r}, ticket claims {expect!r}")
    print(f"{'PASS' if ok else 'FAIL'}   {name:44} got={got!r} want={expect!r}")


def anchor_quality(art: dict) -> float | None:
    """f_q of the front member whose f1* equals the anchor's (None if evicted)."""
    f1a = art["anchor_f1_star"]
    for r in art["front"]:
        if abs(r["f1_star"] - f1a) <= 1e-9:
            return r["f_q"]
    return None


def a3_estimands() -> tuple[dict, list[str]]:
    out = {"dq_all": {}, "dq": {}, "dom": {}, "mq": {}}
    lost: list[str] = []
    for p in sorted(MATRIX.glob("pilot_*.json")):
        art = json.loads(p.read_text(encoding="utf-8"))
        code = p.name[len("pilot_"):].rsplit("_seed", 1)[0]
        f1a = art["anchor_f1_star"]
        afq = anchor_quality(art)
        if afq is None:
            lost.append(p.name)
            continue
        front = art["front"]
        out["dq_all"].setdefault(code, []).append(
            max(r["f_q"] for r in front) - afq)
        elig = [r for r in front if r["f1_star"] >= f1a - 1e-6]
        out["dq"].setdefault(code, []).append(
            (max(r["f_q"] for r in elig) - afq) if elig else 0.0)
        out["dom"].setdefault(code, []).append(
            float(sum(1 for r in front
                      if r["f1_star"] > f1a + 1e-9 and r["f_q"] > afq + 1e-9)))
        elig2 = [r for r in front if r["f_q"] >= afq - 1e-9]
        out["mq"].setdefault(code, []).append(
            (max((r["f1_star"] for r in elig2), default=f1a) - f1a))
    return out, lost


def reachable_range_db(manifest: dict, lib: ModeLibrary, n_pts: int = 21) -> float:
    """Unenforced AASR range [dB] over task x start x routed mode x registered PRF.

    Ticket 25: sampling is PER WINDOW -- the old whole-span scan against one
    scalar t_ca loses its semantics once a task carries multiple transits
    (each with its own zero).  Legacy manifests (scalar triad) are the
    single-window special case and reproduce the original sequence."""
    vals = []
    for t in manifest["tasks"]:
        mode = Mode[t["mode"]]
        wa = float(t["azimuth_size_m"])
        if "windows" in t:
            win_specs = [
                (float(w["lo_s"]), float(w["hi_s"]), float(w["t_ca_s"]))
                for w in t["windows"]
            ]
        else:
            win_specs = [
                (float(t["t_start_s"]), float(t["t_end_s"]), float(t["t_ca_s"]))
            ]
        for t0, t1, t_ca in win_specs:
            for i in range(n_pts):
                tt = t0 + (t1 - t0) * i / (n_pts - 1)
                try:
                    vals.append(aasr_direct(
                        mode, squint_at(tt, t_ca, lib.geo),
                        lib.geo.k, float(t["prf_hz"]), lib,
                        spt_scene_wa_m=(wa if mode is Mode.SPT else None),
                    )["aasr_db"])
                except ValueError:
                    pass  # SLS sample outside the domain (defensive; unreachable for k<1 under A-CROSS (yi))
    if not vals:
        raise ValueError("no AASR sample reachable")
    return max(vals) - min(vals)


def main() -> int:
    for d in (MATRIX, SCENARIOS, PROBE_MANIFESTS, CONVERGENCE):
        if not d.is_dir():
            print(f"ABORT: missing artifacts directory {d}", file=sys.stderr)
            return EXIT_USAGE
    lib = ModeLibrary.from_fixture()

    # Anti-false-green census: every glob below is vacuously satisfiable when its
    # directory is empty (all([]) / median([]) pass silently).  Pin the exact
    # expected counts BEFORE any check runs, so an incomplete artifact tree is a
    # hard usage error rather than a green run over nothing.
    census = {
        "matrix_units": len(list(MATRIX.glob("pilot_*.json"))),
        "scenario_manifests": len(list(SCENARIOS.glob("*.json"))),
        "probe_manifests": len(list(PROBE_MANIFESTS.glob("*.json"))),
        "convergence_units": len(list(CONVERGENCE.glob("pilot_*.json"))),
    }
    bad = [f"{k}={v} != {n}" for k, v, n in (
        ("matrix_units", census["matrix_units"], 50),
        ("scenario_manifests", census["scenario_manifests"], 50),
        ("probe_manifests", census["probe_manifests"], 25),
        ("convergence_units", census["convergence_units"], 45),
    ) if v != n]
    for code in TICKET_A4_SINGLE_MANIFEST:
        n = len(list(SCENARIOS.glob(f"{code}_seed*.json")))
        if n != 10:
            bad.append(f"{code}_manifests={n} != 10")
    for code in TICKET_A4_PROBE_FAMILY:
        n = len(list(PROBE_MANIFESTS.glob(f"{code}_seed*.json")))
        if n != 5:
            bad.append(f"{code}_manifests={n} != 5")
    print("=== artifact census (anti-false-green) ===")
    print(f"       {census}")
    if bad:
        for b in bad:
            print(f"FAIL   census: {b}", file=sys.stderr)
        print("ABORT: artifact tree incomplete -- a check over missing inputs "
              "would pass vacuously", file=sys.stderr)
        return EXIT_USAGE

    print("\n=== A3 / root cause: the coverage comparison is guaranteed ===")
    units = exact = 0
    for p in MATRIX.glob("pilot_*.json"):
        art = json.loads(p.read_text(encoding="utf-8"))
        units += 1
        exact += abs(art["max_f1_star_on_front"] - art["anchor_f1_star"]) <= 1e-12
    check("a3_units", units, TICKET_A3_UNITS)
    check("a3_exact_ties", exact, TICKET_A3_EXACT_TIE)

    print("\n=== A3 / estimands: three rejected are tied, one carries spread ===")
    # NOTE on discriminating power: `dq`, `dom` and `mq` are zero BY CONSTRUCTION
    # (the anchor is the coverage-maximal point, so anything conditioned on
    # f1 >= anchor_f1 admits only the anchor itself).  Asserting they are zero
    # confirms the construction, not a data property -- only `dq_all > 0` is the
    # discriminating check, and the zero checks guard against a future change
    # that would quietly make them non-zero.
    est, lost = a3_estimands()
    usable = sum(len(v) for v in est["dq_all"].values())
    check("a3_usable_units", usable, TICKET_A3_USABLE)
    check("a3_anchor_evicted_units", lost, [TICKET_A3_ANCHOR_LOST_UNIT])
    nz = {
        "dq": sum(1 for vs in est["dq"].values() for x in vs if abs(x) > 1e-12),
        "dom": sum(1 for vs in est["dom"].values() for x in vs if x > 0),
        "mq": sum(1 for vs in est["mq"].values() for x in vs if abs(x) > 1e-12),
    }
    check("a3_rejected_dq_nonzero", nz["dq"], 0)
    check("a3_rejected_dom_nonzero", nz["dom"], 0)
    check("a3_rejected_mq_nonzero", nz["mq"], 0)
    nz_all = sum(1 for vs in est["dq_all"].values() for x in vs if x > 1e-12)
    check("a3_dq_all_nonzero_is_positive", 1 if nz_all > 0 else 0, 1)
    print(f"       (dq_all nonzero units = {nz_all}; the ticket reports 20 at ticket time)")

    print("\n=== A3 / power on the accepted estimand ===")
    pooled = [v for c in TICKET_A3_NONDEGEN for v in est["dq_all"][c]]
    check("a3_pooled_n", len(pooled), TICKET_A3_POOLED_N)
    check("a3_pooled_sd", round(statistics.stdev(pooled), 5), TICKET_A3_POOLED_SD,
          tol=1e-4)
    rejected = [v for c in TICKET_A3_NONDEGEN for v in est["dq"][c]]
    check("a3_rejected_pooled_sd_is_zero",
          1 if statistics.stdev(rejected) == 0.0 else 0, 1)
    if statistics.stdev(pooled) > 0:
        from scipy import stats as _st
        p = _st.ttest_1samp(pooled, 0.0, alternative="greater").pvalue
        check("a3_pooled_one_sided_p_below_alpha", 1 if p < 0.05 else 0, 1)
        print(f"       (one-sided pooled p = {p:.3e})")

    print("\n=== A4 / structural dimension: reachable AASR range per family ===")
    # CALIBER (ticket line "R 的口径"), stated here so the anchors are not
    # unfalsifiable constants: the matrix families are scanned at their BASE
    # seed manifest only (M1NC_100 / M2WF_400 / M2WH_200 / M3NC_300 /
    # M4WH_500); the density-probe families were drawn over 5 seeds and their
    # R_fam is the MAX over those 5 manifests.  A uniform rule does not
    # reproduce all nine values (scanning every matrix seed gives M2WF 5.498 /
    # M2WH 5.487 / M4WH 5.505; taking the first probe seed gives P6WH 5.320).
    for code in TICKET_A4_SINGLE_MANIFEST:
        found = sorted(SCENARIOS.glob(f"{code}_seed*.json"))
        if not found:
            _fails.append(f"a4_{code}: no manifest under results/scenarios")
            print(f"FAIL   a4_R_{code:44} manifest missing")
            continue
        r = reachable_range_db(json.loads(found[0].read_text(encoding="utf-8")), lib)
        check(f"a4_R_{code}", round(r, 3), TICKET_A4_FAMILY_R[code], tol=0.002)
        check(f"a4_{code}_below_threshold",
              1 if r < TICKET_A4_THRESHOLD_DB else 0, 1)
    for code in TICKET_A4_PROBE_FAMILY:
        found = sorted(PROBE_MANIFESTS.glob(f"{code}_seed*.json"))
        if not found:
            _fails.append(f"a4_{code}: no manifest under probe_density/manifests")
            print(f"FAIL   a4_R_{code:44} manifest missing")
            continue
        if len(found) < 2:
            _fails.append(f"a4_{code}: expected a multi-seed probe family, got 1")
        r = max(reachable_range_db(json.loads(p.read_text(encoding="utf-8")), lib)
                for p in found)
        check(f"a4_R_{code}_max_over_seeds", round(r, 3),
              TICKET_A4_FAMILY_R[code], tol=0.002)
        check(f"a4_{code}_below_threshold",
              1 if r < TICKET_A4_THRESHOLD_DB else 0, 1)
        # Sampling robustness: R is an extremum over each task's window, so it
        # is attained at an endpoint.  Measured stable from 5 to 161 points per
        # task -- a coarser scan is not a hidden source of drift.
        r_coarse = max(reachable_range_db(
            json.loads(p.read_text(encoding="utf-8")), lib, n_pts=5)
            for p in found)
        check(f"a4_R_{code}_sampling_stable",
              1 if abs(r_coarse - r) <= 1e-3 else 0, 1)

    print("\n=== A4 / platform dimension: the platform CAN express >= 6 dB ===")
    # CALIBER: k is held at the library design point lib.geo.k (= 1 - A), which is
    # what every registered scenario family uses.  Scanning k freely over
    # [0, 0.9] instead yields 78.47 dB -- a DIFFERENT question (the grid's full
    # k extent), not a correction of this one.  Both are printed so the caliber
    # is visible rather than implied.
    vals = []
    for prf in PRF_KEYS_HZ:
        for mode in Mode:
            for d in range(-45, 46):
                try:
                    vals.append(aasr_direct(
                        mode, math.radians(d), lib.geo.k, prf, lib)["aasr_db"])
                except ValueError:
                    pass
    if not vals:
        print("ABORT: no platform AASR sample reachable", file=sys.stderr)
        return EXIT_USAGE
    prange = max(vals) - min(vals)
    check("a4_platform_range_db", round(prange, 2), TICKET_A4_PLATFORM_RANGE_DB,
          tol=0.02)
    check("a4_platform_alive",
          1 if prange >= TICKET_A4_THRESHOLD_DB else 0, 1)
    # the single-PRF worst slice the ticket quotes (SLS @ 3044 Hz)
    sls3044 = []
    for d in range(-45, 46):
        try:
            sls3044.append(aasr_direct(
                Mode.SLS, math.radians(d), lib.geo.k, 3044.0, lib)["aasr_db"])
        except ValueError:
            pass
    if sls3044:
        # re-registered 2026-10-07 ticket 40: spread 6.99 dB under the (yi)
        # rotation-centre semantics (old 48.20 was the linearised-law artefact
        # of a_res collapsing through zero at 26.76 deg); the ticket's
        # substantive A4 claim (platform can express >= 6 dB) still PASSES
        check("a4_platform_worst_slice_sls_3044",
              round(max(sls3044) - min(sls3044), 2), 6.99, tol=0.02)

    print("\n=== A4 / budget dependence: the plateau criterion is live ===")
    ladder: dict[int, dict] = {}
    for p in sorted(CONVERGENCE.glob("pilot_*.json")):
        a = json.loads(p.read_text(encoding="utf-8"))
        ladder.setdefault(a["seed"], {})[(a["pop_size"], a["generations"])] = \
            a["promotion"]["spread_db"]
    b0, b1 = (160, 240), (320, 480)
    seeds = [s for s in sorted(ladder) if b0 in ladder[s] and b1 in ladder[s]]
    check("a4_ladder_seeds_with_top_pair", len(seeds), 5)
    if not seeds:
        print("ABORT: no convergence seed carries the registered top budget pair",
              file=sys.stderr)
        return EXIT_USAGE
    med_delta = abs(statistics.median([ladder[s][b1] for s in seeds])
                    - statistics.median([ladder[s][b0] for s in seeds]))
    unit_delta = max(abs(ladder[s][b1] - ladder[s][b0]) for s in seeds)
    # CALIBER: med_delta is the DIFFERENCE OF MEDIANS across the top budget pair
    # (= 1.917193 - 0.025145 = 1.892048).  The median of per-seed deltas is a
    # different and much smaller quantity (0.036611); conflating them would
    # understate the drift by ~50x, so the definition is pinned here.
    check("a4_m2wh_median_delta", round(med_delta, 6),
          TICKET_A4_M2WH_MEDIAN_DELTA, tol=1e-5)
    check("a4_m2wh_unit_delta", round(unit_delta, 6),
          TICKET_A4_M2WH_UNIT_DELTA, tol=1e-5)
    at_registered = (med_delta <= TICKET_A4_PLATEAU_MEDIAN_DB
                     and unit_delta <= TICKET_A4_PLATEAU_UNIT_DB)
    check("a4_m2wh_unconverged_at_registered_threshold",
          0 if at_registered else 1, 1)
    # Liveness must be shown in the direction that can actually flip for THIS
    # family.  M2WH already sits above the registered median threshold, so
    # tightening it is a no-op; the informative direction is loosening, which
    # turns UNCONVERGED into CONVERGED.  Asserting a two-way flip here would
    # be tautological for this family.
    at_loose = (med_delta <= TICKET_A4_LOOSE_MEDIAN_DB
                and unit_delta <= TICKET_A4_LOOSE_UNIT_DB)
    check("a4_loosened_verdict_is_converged", 1 if at_loose else 0, 1)
    check("a4_criterion_is_live_flips_when_loosened",
          1 if at_loose != at_registered else 0, 1)
    at_tight = (med_delta <= 0.001 and unit_delta <= 0.002)
    print(f"       (registered {TICKET_A4_PLATEAU_MEDIAN_DB}/{TICKET_A4_PLATEAU_UNIT_DB} dB -> "
          f"{'CONVERGED' if at_registered else 'UNCONVERGED'}; "
          f"loosened {TICKET_A4_LOOSE_MEDIAN_DB}/{TICKET_A4_LOOSE_UNIT_DB} -> "
          f"{'CONVERGED' if at_loose else 'UNCONVERGED'}; "
          f"tightened 0.001/0.002 -> {'CONVERGED' if at_tight else 'UNCONVERGED'} "
          f"-- tightening is a no-op for this family, loosening is the live edge)")

    print(f"\n=== RESULT: {len(_fails)} failure(s) over {_checks} checks ===")
    for f in _fails:
        print(f"FAIL   {f}")
    if _fails:
        print("VERDICT: adjudication has DRIFTED from the artifacts -- ticket 17 "
              "must not freeze v2 against these numbers")
        return EXIT_DRIFT
    print("VERDICT: ticket 22 adjudications reproduce from the frozen artifacts")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())