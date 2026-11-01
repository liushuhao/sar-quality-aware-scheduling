#!/usr/bin/env python3
"""R5/R6 check group (2026-11-01 submission panel, obligations R5 and R6)
for ``verify_paper_numbers_l8.py``.

Standalone module so the main gate only needs a three-line wiring (same
pattern as ``verify_t55_group``).  Opt out with ``L8_R56_OPTIONAL=1`` when
the manuscript under test is a synthetic fixture that legitimately carries
neither anchor paragraph -- the same escape hatch ``L8_B16X_OPTIONAL`` uses.

What it gates
-------------
R5 -- the azimuth-ambiguity direction contrast of Section 7.2.  The panel
demanded either a re-evaluation of the integral carrying a scene-sweep
occupancy term consistent with the Section 3.2 W_a dwell closure, or the
withdrawal of the "difference of mechanism" claim.  Both were done; the
manuscript now prints the re-evaluation, and this module recomputes it:

  * the registered calibration sequence the paragraph quotes,
  * the scene-extent channel under the model's three mappings
    (geometric cos^3, registered cos^1, psi-free), at both endpoints,
  * the level shifts the three share at zero squint,
  * the spotlight branch's own scene-extent effect (the model already
    carries the scene extent there, as a worst-edge offset).

R6 -- the intra-dwell delivered-resolution bound added to constraint C5:
per-mode worst ``cos(psi_sel)/cos(psi(t))`` over the selected starts, from
the SAME frozen v5 sweep artifacts and the same loading path as fig-7.

Matching discipline (the point of the checks)
---------------------------------------------
A presence test over a paragraph's number set is not a check: every value
lives in one paragraph, so swapping two groups, or swapping a sentence's
endpoints, leaves the set unchanged (measured: a mode-swapped paragraph
passed 19/19).  Every number below is therefore read **in order, from the
words that immediately precede its own label** -- the four values that end
the clause before "for sliding spotlight", the value just before
"(stripmap)" -- so a swap, a relabelling or a reversed pair fails.

The integrator is a LOCAL COPY of ``sss_core.aasr``'s band integral, kept
because the registered one has no scene-extent switch; ``tests/
test_verify_r56_group.py`` pins the copy to ``aasr_direct`` at the base
setting, so a re-registration of D06-1/D06-3 breaks that test rather than
silently diverging.  Pattern, alias count and integration points are
imported, not copied.

rc of the host gate is unchanged: a printed number that no longer
reproduces from the artifacts is a FAIL, and a missing anchor paragraph is
a FAIL too (a vanished check surface must not read as a pass) unless the
optional flag is set.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path

import numpy as np

FORK = Path(__file__).resolve().parent.parent
V5 = FORK / "experiments" / "v5_results"
if str(FORK) not in sys.path:
    sys.path.insert(0, str(FORK))

from sss_core.aasr import (  # noqa: E402
    N_ALIASES, N_INTEGRATION_POINTS, _pattern, aasr_direct)
from sss_core.modes import Mode, ModeLibrary  # noqa: E402

PRF_HZ = 3630.0                     # registered production PRF (D06-4)
FAM_SEEDS = {"R1C": range(100, 110), "R2F": range(200, 210),
             "R3H": range(300, 310)}
R5_PSI_DEG = tuple(range(0, 27, 2))  # 0..26 in 2 deg steps (SLS registered cap)
R6_SERVED_TASKS = 1607              # recomputed below; an exact pin, not a floor
R56_MIN_CHECKS = 17                 # per-manuscript floor (whole-group loss guard)


def _aasr(lib: ModeLibrary, mode: Mode, psi_rad: float, extra_hz: float = 0.0,
          pattern_cos: bool = False, k: float | None = None) -> float:
    """AASR in dB with an optional scene-extent occupancy added to the band.

    Same integration as ``sss_core.aasr.aasr_direct`` (same midpoint rule,
    same alias truncation, same excluded m = 0) plus two modelling switches
    the R5 re-evaluation needs:

    ``extra_hz``     added to the processed band (the scene-extent span),
    ``pattern_cos``  squint-scales the two-way pattern width (a probe of the
                     model's own convention, not a registered reading).

    ``test_verify_r56_group.test_the_copy_matches_the_registered_integral``
    keeps this a faithful copy at ``extra_hz = 0``.
    """
    geo = lib.geo
    vs = geo.vs_mps
    cos_psi = math.cos(psi_rad)
    k_lib = 1.0 - geo.A
    kk = k_lib if k is None else k
    if mode is Mode.SPT:
        raise ValueError("R5 group integrates STR/SLS only (SPT collapses)")
    a_res = 1.0 - kk if mode is Mode.SLS else 1.0
    band = lib.bandwidth_d_hz(mode, psi_rad) + extra_hz
    f = -band / 2.0 + (np.arange(N_INTEGRATION_POINTS) + 0.5) * (band / N_INTEGRATION_POINTS)
    ar = a_res * f
    cw = cos_psi if pattern_cos else 1.0
    den = float(np.sum(_pattern(ar, vs, geo.D_m / cw) ** 2)) * (band / N_INTEGRATION_POINTS)
    num = 0.0
    for m in range(-N_ALIASES, N_ALIASES + 1):
        if m == 0:
            continue
        num += float(np.sum(_pattern(ar + m * PRF_HZ, vs, geo.D_m / cw) ** 2)) * (
            band / N_INTEGRATION_POINTS)
    return 10.0 * math.log10(num / den)


def _r5(lib: ModeLibrary) -> dict:
    geo = lib.geo
    vs, lam = geo.vs_mps, geo.wavelength_m
    wa, r0_slant = geo.scene_wa_m, geo.R0_m

    def ex_geom(psi):   # target squint moves as cos^2 in along-track offset
        return (2.0 * vs / lam) * math.cos(psi) ** 3 * wa / r0_slant

    def ex_reg(psi):    # the cos^1 convention the registered band itself uses
        return (2.0 * vs / lam) * math.cos(psi) * wa / r0_slant

    def ex_flat(psi):   # the psi-free mapping the spotlight branch registers
        return (2.0 * vs / lam) * wa / r0_slant

    out = {"v0": {d: _aasr(lib, Mode.SLS, math.radians(d)) for d in (0, 6, 12, 18, 26)}}
    for tag, ex in (("geom", ex_geom), ("reg", ex_reg), ("flat", ex_flat)):
        out[("sls", tag)] = {d: _aasr(lib, Mode.SLS, math.radians(d), ex(math.radians(d)))
                             for d in R5_PSI_DEG}
        out[("str", tag)] = {d: _aasr(lib, Mode.STR, math.radians(d), ex(math.radians(d)))
                             for d in R5_PSI_DEG}
    out["sls_level_shift"] = out[("sls", "geom")][0] - out["v0"][0]
    out["str_level_shift"] = out[("str", "geom")][0] - out["v0"][0]
    out["sls_patcos"] = _aasr(lib, Mode.SLS, math.radians(26), ex_geom(math.radians(26)),
                              pattern_cos=True)
    out["sls_patcos_0"] = _aasr(lib, Mode.SLS, 0.0, ex_geom(0.0), pattern_cos=True)
    # the registered spotlight branch ALREADY carries the scene extent, as a
    # worst-edge frequency offset; the paragraph quotes the effect size
    spt_scene = aasr_direct(Mode.SPT, 0.0, 0.0, PRF_HZ, lib)["aasr_db"]
    spt_point = aasr_direct(Mode.SPT, 0.0, 0.0, PRF_HZ, lib,
                            spt_scene_wa_m=1e-9)["aasr_db"]
    out["spt_scene_effect_db"] = spt_scene - spt_point
    # the same paragraph's scope note prints two more constants, both a pure
    # function of the registered library: the zero-squint processing bands of
    # the two task-law modes, and the spotlight library-edge AASR at the
    # platform-level scene extent (the default spt_scene_wa_m, i.e. 5 km).
    out["band_khz"] = {"SLS": lib.bandwidth_d_hz(Mode.SLS, 0.0) / 1e3,
                       "SPT": lib.bandwidth_d_hz(Mode.SPT, 0.0) / 1e3}
    out["spt_library_edge_db"] = spt_scene
    # model invariants (reported separately from the manuscript checks)
    for key in (("sls", "geom"), ("str", "geom"), ("sls", "reg"), ("str", "reg"),
                ("sls", "flat"), ("str", "flat")):
        vals = [out[key][d] for d in R5_PSI_DEG]
        out[("mono",) + key] = all(vals[i + 1] <= vals[i] + 1e-9 for i in range(len(vals) - 1))
    out["patcos_mono"] = out["sls_patcos"] <= out["sls_patcos_0"] + 1e-9
    return out


def _r6(lib: ModeLibrary) -> dict:
    from sss_core.duration import duration_scene_s
    from sss_core.geometry import squint_at

    worst, n = {}, 0
    for fam, seeds in FAM_SEEDS.items():
        for seed in seeds:
            pilot = json.loads((V5 / "sweep" / "s1_0" / f"pilot_{fam}_seed{seed}.json")
                               .read_text(encoding="utf-8"))
            sc = json.loads((V5 / "scenarios" / f"{fam}_seed{seed}.json")
                            .read_text(encoding="utf-8"))
            tasks = sc["tasks"]
            best = max(pilot["front"], key=lambda m: (m["f1_star"], -m["cv"]))
            for idx, t in best["starts"].items():
                task = tasks[int(idx)]
                win = next((w for w in task["windows"] if w["lo_s"] <= t <= w["hi_s"]), None)
                if win is None:
                    continue
                n += 1
                mode = Mode[task["mode"]]
                rho = None if mode is Mode.STR else task["rho_req_m"]
                psi0 = squint_at(t, win["t_ca_s"], lib.geo, r0_m=win["r0_m"])
                dwell = duration_scene_s(mode, psi0, lib, r0_m=win["r0_m"],
                                         rho_req_m=rho,
                                         l_az_m=task["azimuth_size_m"])
                psi_end = squint_at(t + dwell, win["t_ca_s"], lib.geo, r0_m=win["r0_m"])
                worst_psi = psi_end if abs(psi_end) > abs(psi0) else psi0
                ratio = math.cos(psi0) / math.cos(worst_psi)
                worst[mode.name] = max(worst.get(mode.name, 0.0), ratio)
    return {"served": n, "worst": worst}


def r56_expectations() -> dict:
    lib = ModeLibrary.from_fixture()
    r5, r6 = _r5(lib), _r6(lib)
    if r6["served"] != R6_SERVED_TASKS:
        raise RuntimeError(
            f"R6 recomputation sees {r6['served']} served tasks, not the "
            f"registered {R6_SERVED_TASKS} -- the frozen artifacts changed; "
            "re-derive the printed bound and update this pin together with it")
    return {"r5": r5, "r6": r6}


# ── manuscript reading ───────────────────────────────────────────────────
#
# Numbers are read from the words that PRECEDE their own label, in order, so
# a swap of two groups, a relabelling, or a reversed endpoint pair fails.
# Cross-reference numbers ("Section 3.3", "Eq. 7", "Fig. 2") are stripped
# before extraction: they share the shape of the readings and would otherwise
# serve as decoys for a corrupted value.

_MINUS = str.maketrans({"−": "-", "–": "-"})
# mode labels as they appear in the parenthetical attributions; a qualifier
# appended to the label must not turn a correct attribution into a false red
_LABEL_STR = re.compile(r"\(stripmap[^)]{0,12}\)")
_LABEL_SLS = re.compile(r"\(sliding spotlight[^)]{0,12}\)")
_LABEL_SPT = re.compile(r"\(spotlight[^)]{0,12}\)")
# the scope note's band attribution, read for its MODE ORDER so the printed
# pair is bound to the labels the sentence actually names
_BAND_ATTR = re.compile(
    r"the\s+(SLS|SPT)\s+and\s+(SLS|SPT)\s+processing bandwidths")
_REF = re.compile(r"\b(?:Section|Sections|Sec\.|Eq\.|Eqs\.|Fig\.|Figure|Figs\.|"
                  r"Table|Tables|Ref\.|Refs\.)\s*~?\$?\d+(?:\.\d+)?")
_NUM = re.compile(r"[-−]?\d+\.\d+")


def _paragraph(text: str, anchor: str) -> str | None:
    for para in text.split("\n\n"):
        if anchor in para:
            return para
    return None


def _clean(seg: str) -> str:
    return _REF.sub(" ", seg.translate(_MINUS))


def _printed_tol(val: float) -> float:
    """Half a unit in the last printed digit, read off the value itself."""
    txt = f"{val}"
    dec = len(txt.split(".")[1]) if "." in txt else 0
    return 0.5 * 10.0 ** (-dec) if dec else 0.5


def _nums_ending_before(para: str, phrase, window: int = 170) -> list:
    """The numbers in the ``window`` chars just before each ``phrase`` hit.

    NOT a contiguous run: every decimal in the window is returned, so the
    callers take a suffix of it (``_last_before`` the last one,
    ``_tail_matches`` the last ``n``).  Contiguity is deliberately not
    enforced -- a window that reaches back past a sentence boundary and picks
    up an earlier reading is handled by the caller's anchor choice, not here.

    ``phrase`` may be a compiled pattern, so a label that legitimately grows
    a qualifier ("(stripmap mode)") does not read as a false red.
    """
    pat = phrase if hasattr(phrase, "finditer") else re.compile(re.escape(phrase))
    out = []
    for m in pat.finditer(para):
        seg = _clean(para[max(0, m.start() - window):m.start()]).rstrip()
        nums = [float(x) for x in _NUM.findall(seg)]
        if nums:
            out.append(nums)
    return out


def _last_before(para: str, phrase, window: int = 120):
    hits = _nums_ending_before(para, phrase, window)
    return hits[0][-1] if hits else None


def _tail_matches(para: str, phrase, wants, window: int = 170) -> bool:
    for nums in _nums_ending_before(para, phrase, window):
        if len(nums) < len(wants):
            continue
        if all(abs(a - b) <= _printed_tol(b)
               for a, b in zip(nums[len(nums) - len(wants):], wants)):
            return True
    return False


def check_r56(text: str, label: str, exp: dict) -> "tuple[list, list, int]":
    fails: list = []
    passes: list = []
    seen = 0
    r5, r6 = exp["r5"], exp["r6"]
    optional = os.environ.get("L8_R56_OPTIONAL") == "1"

    def term(name, want, got, note=""):
        nonlocal seen
        seen += 1
        if got is not None and abs(got - want) <= _printed_tol(want):
            passes.append(f"{label}: {name} {want}{note}")
        else:
            fails.append(f"{label}: {name} {want}{note} -- manuscript prints "
                         f"{got}; recomputed {want}")

    para = _paragraph(text, "target-side Doppler occupancy")
    if para is None:
        if not optional:
            fails.append(f"{label}: R5 anchor paragraph (the scene-extent "
                         "contrast) is missing -- the check surface vanished")
    else:
        term("R5 registered AASR at 0 deg", round(r5["v0"][0], 2),
             _last_before(para, "at zero squint"), " dB")
        term("R5 registered AASR at 26 deg", round(r5["v0"][26], 2),
             _last_before(para, "calibration-grid edge"), " dB")
        term("R5 spotlight scene-extent effect", round(r5["spt_scene_effect_db"], 1),
             _last_before(para, "between a point target"), " dB")
        sls_want = [round(r5[("sls", t)][0], 2) for t in ("geom",)] + [
            round(r5[("sls", t)][26], 2) for t in ("geom", "reg", "flat")]
        str_want = [round(r5[("str", t)][0], 2) for t in ("geom",)] + [
            round(r5[("str", t)][26], 2) for t in ("geom", "reg", "flat")]
        for name, phrase, wants in (
            ("R5 sliding-spotlight endpoints (cos3 -> cos1 -> psi-free)",
             "for sliding spotlight", sls_want),
            ("R5 stripmap endpoints (cos3 -> cos1 -> psi-free)",
             "for stripmap", str_want),
        ):
            seen += 1
            if _tail_matches(para, phrase, wants):
                passes.append(f"{label}: {name} {wants}")
            else:
                fails.append(f"{label}: {name} {wants} -- the ordered run before "
                             f"'{phrase}' does not reproduce (swapped, relabelled "
                             "or wrong)")
        term("R5 sliding-spotlight level shift", round(r5["sls_level_shift"], 1),
             _last_before(para, _LABEL_SLS), " dB")
        term("R5 stripmap level shift", round(r5["str_level_shift"], 1),
             _last_before(para, _LABEL_STR), " dB")
        # the scope note's two library constants (R102, 2026-11-01).  The
        # bands are bound to the LABELS the sentence prints ("the X and Y
        # processing bandwidths ... A and B kHz"), not to a fixed order, and
        # the clause between the labels and the unit must carry exactly two
        # numbers.  A first version read only the ordered pair and let three
        # escapes through (measured, all three): the two labels exchanged, the
        # attribution dropped entirely, and a fabricated third band prepended.
        seen += 1
        mlab = _BAND_ATTR.search(para)
        kz = para.find("kHz", mlab.end()) if mlab else -1
        got = ([float(x) for x in _NUM.findall(_clean(para[mlab.end():kz]))]
               if kz > 0 else [])
        if mlab is None or kz < 0:
            fails.append(f"{label}: R5 the 'the X and Y processing bandwidths' "
                         "attribution is missing -- the band check has no surface")
        elif len(got) != 2:
            fails.append(f"{label}: R5 the kHz clause carries {len(got)} band(s) "
                         f"{got}, not the two the attribution names")
        else:
            bands = [round(r5["band_khz"][mlab.group(1)], 1),
                     round(r5["band_khz"][mlab.group(2)], 1)]
            if all(abs(a - b) <= _printed_tol(b) for a, b in zip(got, bands)):
                passes.append(f"{label}: R5 zero-squint processing bands "
                              f"({mlab.group(1)}, {mlab.group(2)}) {bands} kHz")
            else:
                fails.append(f"{label}: R5 zero-squint processing bands "
                             f"({mlab.group(1)}, {mlab.group(2)}) {bands} kHz -- "
                             f"the sentence prints {got}")
        term("R5 spotlight library-edge AASR", round(r5["spt_library_edge_db"], 2),
             _last_before(para, "is the library-edge constant"), " dB")
        # the same constant is printed a second time in the same paragraph
        # ("the spotlight ratio is squint-invariant at -7.05 dB"); a gate on
        # one printing leaves the other free to drift (measured 2026-11-01)
        term("R5 spotlight squint-invariance level (first printing)",
             round(r5["spt_library_edge_db"], 2),
             _last_before(para, "exactly as the degenerate-integral"), " dB")
        seen += 1
        if "no mapping of it reverses the direction" in para:
            passes.append(f"{label}: R5 direction claim present and unpolarised")
        else:
            fails.append(f"{label}: R5 the 'no mapping ... reverses the direction' "
                         "sentence is missing or reversed")
        seen += 1
        if "monotone at" in para:
            passes.append(f"{label}: R5 monotonicity claim present")
        else:
            fails.append(f"{label}: R5 the 'monotone at ... steps' claim is missing")

    para6 = _paragraph(text, "intra-dwell ratio")
    # R6's pinned constants are checked against the recomputation whether or
    # not the manuscript paragraph is found: a drifted artifact must not be
    # reported as "anchor missing".
    for mode, pin in (("STR", 1.008), ("SLS", 1.020), ("SPT", 1.045)):
        got = round(r6["worst"][mode], 3)
        if abs(got - pin) > 0.0005:
            seen += 1
            fails.append(f"{label}: R6 {mode} worst intra-dwell ratio recomputes to "
                         f"{got}, but the check pins {pin} -- re-derive the printed "
                         "bound and update the pin together")
        elif para6 is not None:
            seen += 1
            printed = _last_before(para6, {
                "STR": _LABEL_STR, "SLS": _LABEL_SLS, "SPT": _LABEL_SPT}[mode])
            if printed is not None and abs(printed - got) <= 0.0005:
                passes.append(f"{label}: R6 {mode} worst intra-dwell ratio {got}")
            else:
                fails.append(f"{label}: R6 {mode} worst intra-dwell ratio {got} -- "
                             f"the statement prints {printed}")
        elif not optional:
            seen += 1
            fails.append(f"{label}: R6 anchor paragraph (the C5 bound) is missing")

    if para6 is not None:
        seen += 1
        med = _last_before(para6, "in every mode")
        if med is not None and abs(med - 1.0) <= 0.0005:
            passes.append(f"{label}: R6 median intra-dwell ratio 1.000")
        else:
            fails.append(f"{label}: R6 median ratio reads {med}, expected 1.000")
        seen += 1
        # read the count back out of the recomputation, so a drifted pin can
        # never be "verified" against a hardcoded literal
        served = r6["served"]
        printed_rx = (r"(?<![\d.])" + f"{served:,}".replace(",", r"(?:\{,\}|,)")
                      + r"(?![\d.])")
        if re.search(printed_rx, para6.translate(_MINUS)):
            passes.append(f"{label}: R6 served-task count {served}")
        else:
            fails.append(f"{label}: R6 served-task count {served} not printed")
    return fails, passes, seen


def r5_invariants(exp: dict) -> "tuple[list, list]":
    """Model invariants, reported apart from the manuscript checks.

    They say something about the physics, not about the manuscript, so they
    must not be counted as manuscript checks (a green count that never read
    the text is the failure mode this split exists to prevent).
    """
    r5 = exp["r5"]
    ok, bad = [], []
    for key in (("mono", "sls", "geom"), ("mono", "str", "geom"),
                ("mono", "sls", "reg"), ("mono", "str", "reg"),
                ("mono", "sls", "flat"), ("mono", "str", "flat")):
        (ok if r5[key] else bad).append(f"R5 invariant: monotone improvement {key[1:]}")
    (ok if r5["patcos_mono"] else bad).append(
        "R5 invariant: squint-scaled-pattern variant keeps the sign")
    return ok, bad
