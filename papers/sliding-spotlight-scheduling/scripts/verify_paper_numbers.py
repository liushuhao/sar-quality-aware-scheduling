#!/usr/bin/env python3
"""Ticket 37 D block -- manuscript number ledger (the paper-2 equivalent of
``src/tools/verify_paper_numbers.py``).

Every number the manuscript prints is recomputed from the frozen artifacts
under ``experiments/`` and compared against what the manuscript says.  The
EXPECTATIONS ARE NOT HARDCODED: each check derives its expected value from
the artifact it verifies, and the registered threshold / caliber / verdict
labels are read out of ``analysis_prereg_v2.json`` and
``caliber_registry.json``.  Hardcoding them would make the tool verify
nothing -- the same defect audit4 B8 found in ``claim_trace.json``, where
every verdict was recomputable but had no drift gate.

This is the difference from ``verify_v3_verdicts.py``, which pins the
REGISTERED verdicts against hardcoded constants on purpose (it is the gate
that catches an artifact drifting from its registration).  Here the
registration IS the source, so a manuscript number is checked against the
artifact that produced it and against the caliber it was produced under.

Paired trap numbers (the ticket names these explicitly):
  * 0.499 dB knife-edge is the SYNTHETIC P8WH family's margin-to-threshold,
    NOT R1C's;
  * 26.9 deg is a conservative UPPER BOUND on the physical sliding-spotlight
    boundary; the exact root arccos(sqrt(k)) is recomputed and must sit below;
  * 14.97 orbits is the two-body SIMULATED repeat period; 14.75 includes J2 and
    describes the physical orbit, not this simulator;
  * the three f_q family ranges are caliber-specific and must not be mixed.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/verify_paper_numbers.py \
        --paper paper/full.md [--paper chapter.md --paper paper.tex]

rc:
  0  every extracted number reproduces from the artifacts
  1  at least one mismatch (the manuscript contradicts an artifact)
  2  extraction found nothing to check / artifacts unusable -- NOT a pass
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
V3 = FORK / "experiments" / "v3_results"
PREREG = FORK / "experiments" / "analysis_prereg_v2.json"
CALIBER = FORK / "experiments" / "caliber_registry.json"
TIERS = ("matrix", "matrix_p80g120", "matrix_p160g240")
BASE, MID, TOP = TIERS
FAMILIES = ("R1C", "R2F", "R3H")
N_SEEDS = 10

# TOLERANCES are registered here as a TABLE, not scattered: a tolerance wider
# than the drift it is meant to catch launders a mismatch into a pass (project
# memory: feedback-gate-tolerance-and-prose-extraction-gap).
TOL = {
    "spread_db": 1e-6,        # exact dB reading; no rounding slack
    "median_count": 0.5,      # a median over 10 integer counts
    "f_q": 5e-2,              # 2-dp rounding of a range endpoint
    "fraction": 5e-2,         # 2-dp rounding of a fraction / percentage
    "orbit_turns": 5e-3,      # 2-dp rounding of an orbit count
    "deg": 5e-4,              # 4-dp rounding of the exact SLS root
}

_EARTH_MU_KM3_S2 = 398600.4418
_EARTH_R_KM = 6371.0
_SIDEREAL_DAY_S = 86164.0905


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def front_of(art: dict) -> list:
    """The richness-filtered front (cv <= 1e-9), the registered caliber."""
    return [r for r in art["front"] if abs(r["cv"]) <= 1e-9]


def distinct_fq(art: dict) -> int:
    return len({round(r["f_q"], 6) for r in front_of(art)})


def dq_all(art: dict):
    """The registered estimand: max f_q on the front minus the anchor's."""
    f1a = art["anchor_f1_star"]
    afq = [r["f_q"] for r in art["front"] if abs(r["f1_star"] - f1a) <= 1e-9]
    if not afq or not art["front"]:
        return None
    return max(r["f_q"] for r in art["front"]) - afq[0]


# --------------------------------------------------------------------------
# The recomputed expectations.  Each returns (value, provenance) so the report
# can name where every expected number came from -- a reader must be able to
# re-derive it without reading this script.
# --------------------------------------------------------------------------
def recompute() -> dict:
    exp: dict = {}

    # --- promotion: the 90-unit no_promotion verdict -----------------------
    spreads, decisions, units, threshold = [], set(), 0, None
    for tier in TIERS:
        for p in sorted((V3 / tier).glob("pilot_*.json")):
            a = _load(p)
            spreads.append(a["promotion"]["spread_db"])
            decisions.add(a["promotion"]["decision"])
            threshold = a["promotion"]["threshold_db"]
            units += 1
    exp["promotion_units"] = (units, f"{len(TIERS)} tiers x {N_SEEDS} seeds x 3 families")
    exp["promotion_max_spread_db"] = (max(spreads),
                                     "max over promotion.spread_db of all 90 units")
    exp["promotion_decision"] = (sorted(decisions), "the only decision present")
    exp["promotion_threshold_db"] = (threshold, "promotion.threshold_db in the artifacts")

    # --- R3H base/top richness (the search-artifact signature) -------------
    for tier in (BASE, TOP):
        arts = [_load(p) for p in sorted((V3 / tier).glob("pilot_R3H_seed*.json"))]
        exp[f"R3H_front_median_{tier}"] = (
            statistics.median(len(front_of(a)) for a in arts),
            f"median front size, R3H, {tier}")
        exp[f"R3H_distinct_fq_median_{tier}"] = (
            statistics.median(distinct_fq(a) for a in arts),
            f"median distinct-fq, R3H, {tier}")

    # --- the three f_q family ranges (A4 caliber, do NOT mix) --------------
    for fam in FAMILIES:
        arts = [_load(p) for p in sorted((V3 / TOP).glob(f"pilot_{fam}_seed*.json"))]
        fq = [r["f_q"] for a in arts for r in front_of(a)]
        exp[f"{fam}_f_q_min"] = (min(fq), f"min f_q over the {fam} front, {TOP}")
        exp[f"{fam}_f_q_max"] = (max(fq), f"max f_q over the {fam} front, {TOP}")

    # --- R1C control: the anchor saturates at every budget -----------------
    anchors, units = [], 0
    for tier in TIERS:
        for p in sorted((V3 / tier).glob("pilot_R1C_seed*.json")):
            anchors.append(_load(p)["anchor_f1_star"])
            units += 1
    exp["R1C_anchor_units"] = (units, "R1C units across all tiers")
    exp["R1C_anchor_all_one"] = (all(a == 1.0 for a in anchors),
                                 "anchor_f1_star over every R1C unit")

    prereg = _load(PREREG)
    amend = prereg["amendment_20261005_v3_realwindow"]

    # --- the knife-edge trap (B12) ----------------------------------------
    # 0.499 dB is P8WH's (SYNTHETIC) margin to the threshold.  Recomputed from
    # the registered v1 evidence so a manuscript cannot attach the number to
    # R1C, whose own margin is a different quantity entirely.
    struct = prereg["tests"]["promotion_convergence"]["structural_dimension"]
    knife_rx = re.search(r"P8WH\s+([\d.]+)", struct["v1_evidence"])
    thr = exp["promotion_threshold_db"][0]
    exp["knife_edge_family"] = ("P8WH", "the family named in knife_edge_disclosure")
    if knife_rx:
        exp["P8WH_knife_edge_db"] = (
            round(thr - float(knife_rx.group(1)), 4),
            f"{thr} (threshold) - P8WH reading from v1_evidence")

    # --- the effect size, its power, and the seed anchor (A2) -------------
    eff = amend["r_family_effect_size"]
    delta = eff["value"]
    pd_ = eff["power_design"]
    exp["delta"] = (delta, "amendment.r_family_effect_size.value")
    exp["n_seeds"] = (N_SEEDS, "power_design: n seeds per family")
    exp["alpha"] = (pd_["alpha"], "power_design.alpha")
    exp["power_at_delta"] = {}
    exp["seeds_for_80pct"] = {}
    try:
        from scipy import stats as scipy_stats
    except Exception:                                     # pragma: no cover
        exp["_scipy_missing"] = True
    else:
        t_sum = pd_["t_crit_95_df9"] + pd_["t_crit_80_df9"]
        for code in ("R2F", "R3H"):
            arts = [_load(p)
                    for p in sorted((V3 / TOP).glob(f"pilot_{code}_seed*.json"))]
            dq = [dq_all(a) for a in arts]
            sd = statistics.stdev(dq)
            pw = 1 - scipy_stats.nct.cdf(
                pd_["t_crit_95_df9"], N_SEEDS - 1,
                delta / (sd / math.sqrt(N_SEEDS)))
            exp["power_at_delta"][code] = (round(pw, 2),
                                           f"recomputed from the {code} dq_all sd")
            exp["seeds_for_80pct"][code] = (
                math.ceil((t_sum * sd / delta) ** 2),
                f"ceil(((t_0.95 + t_0.80) * sd / delta)^2), sd = {sd:.2f}")

    # --- scenario ledgers: the drawn / served counts ----------------------
    exp["n_drawn"], exp["n_served"], exp["n_windows"] = {}, {}, {}
    for code in FAMILIES:
        m = _load(sorted((V3 / "scenarios").glob(f"{code}_seed*.json"))[0])
        g = m["generation_ledger"]
        exp["n_drawn"][code] = (g["n_drawn"], "generation_ledger.n_drawn, base seed")
        exp["n_served"][code] = (g["n_served"], "generation_ledger.n_served")
        exp["n_windows"][code] = (g["n_windows_total"],
                                  "generation_ledger.n_windows_total")

    # --- the exact SLS root vs the registered conservative bound (F-8) ----
    plat = _load(FORK / "experiments" / "platform_kim2021.json")
    modes = plat["modes"]            # measured: the ladder lives under `modes`
    k = modes["sliding_factor_k_ladder"]["value"]
    env = modes["mode_squint_envelope_deg"]["value"]
    exp["sliding_factor_k"] = (k, "platform_kim2021.sliding_factor_k_ladder.value")
    exp["SLS_registered_bound_deg"] = (env["SLS"],
                                       "mode_squint_envelope_deg.SLS")
    exp["SLS_exact_root_deg"] = (round(math.degrees(math.acos(math.sqrt(k))), 4),
                                "arccos(sqrt(k)), recomputed from k")
    exp["SLS_str_spt_envelope_deg"] = (env["STR"],
                                       "mode_squint_envelope_deg.STR")

    # --- the two-body ground-track repeat (B6 trap) -----------------------
    # The registered figure "14.97 orbits ~= 23.93 h" is the GROUND-TRACK
    # repeat: the ground track closes after one SIDEREAL day of propagation,
    # not after the scenario span.  Deriving it as span_days / period gives
    # 45 turns and is simply a different quantity -- the first cut of this
    # script made that error and the fixture caught it.
    h_km = plat["platform"]["altitude_km"]["value"]
    a_km = h_km + _EARTH_R_KM
    period_s = 2 * math.pi * math.sqrt(a_km ** 3 / _EARTH_MU_KM3_S2)
    exp["orbit_period_s"] = (round(period_s, 1),
                             "2*pi*sqrt(a^3/mu), a = altitude + R_earth")
    exp["orbit_repeat_turns_simulated"] = (
        round(_SIDEREAL_DAY_S / period_s, 2),
        "sidereal day / two-body period (no J2 nodal drift)")
    exp["orbit_repeat_hours"] = (round(_SIDEREAL_DAY_S / 3600.0, 2),
                                 "sidereal day in hours")

    # --- caliber facts the manuscript must tag with ------------------------
    # Parsed defensively.  Ticket 36 CORRECTED this field: it used to read
    # "roughly 31-111", which was a single unit's span promoted to family level
    # in error; the operative registration is now the three PER-FAMILY pooled
    # ranges.  A parser that hard-required the superseded text would break the
    # moment the registration was corrected, so the per-family form is primary
    # and the old pooled form is only a fallback.
    cal = _load(CALIBER)
    note = cal["calibers"]["v3"]["f_q_unit_note"]
    per_family = {}
    for fam, lo, hi in re.findall(
            r"(R1C|R2F|R3H)\s*\[([\d.]+),\s*([\d.]+)\]", note):
        per_family[fam] = (float(lo), float(hi))
    if per_family:
        exp["caliber_v3_f_q_pooled_by_family"] = (
            per_family, "caliber_registry v3.f_q_unit_note, per-family pooled")
    else:
        rng = re.search(r"roughly\s*(\d+)\s*-\s*(\d+)", note)
        exp["caliber_v3_f_q_pooled_by_family"] = (
            rng.groups() if rng else None,
            "caliber_registry v3.f_q_unit_note (no per-family form found)")
    exp["budget_ladder"] = (list(TIERS), "the three budget tiers on disk")
    return exp


# --------------------------------------------------------------------------
# Extraction: find the numbers the manuscript states and compare them.
# --------------------------------------------------------------------------
_TIER_TAG_RX = re.compile(
    r"40\s*/\s*60|160\s*/\s*240|80\s*/\s*120|base\s+budget|top\s+budget|"
    r"base\s+tier|top\s+tier", re.IGNORECASE)


def _nearest_tier_tag(window: str) -> str:
    """Which budget tier a number belongs to, by the closest tag before it."""
    hits = list(_TIER_TAG_RX.finditer(window))
    if not hits:
        return BASE
    tag = hits[-1].group(0)
    if re.search(r"160|top", tag, re.I):
        return TOP
    return BASE


def _round_tol(found: str) -> float:
    """Tolerance implied by the manuscript's OWN rounding of the number.

    A manuscript states "3.9722 dB" for a recomputed 3.972248...; demanding
    bit-equality would red every correctly-rounded draft.  The tolerance is
    derived from the digits actually printed, so a manuscript that quotes more
    precision is held to more precision -- and a manuscript that prints a
    wrong number still fails, because the error is orders of magnitude larger
    than the last printed digit.
    """
    frac = found.split(".")[1] if "." in found else ""
    if not frac:
        return 0.5
    return 0.5 * 10 ** (-len(frac))


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s)


# A number together with the text that introduces it.  Sentences are split on
# SENTENCE terminators only -- the first cut used ``[^.\n]`` as the window,
# which cannot cross a decimal point, so "R1C min f_q 1.49" and every other
# decimal-bearing sentence produced ZERO extractions and the tool reported a
# green run over 7 numbers it had not actually checked.
_SENT_SPLIT_RX = re.compile(r"(?<=[.;。；])\s+")
_NUM_RX = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w])")


def _sentences(body: str) -> list:
    return [s for s in _SENT_SPLIT_RX.split(body) if s.strip()]


def _numbers_in(sentence: str) -> "list[tuple[int, str]]":
    return [(m.start(), m.group(1)) for m in _NUM_RX.finditer(sentence)]


def _judge_context(body: str, label: str, exp: dict, fails: list, passes: list,
                   seen: "list[int]", anchor_rx, expect, tol_key, what: str,
                   window: int = 200) -> None:
    """Match every number in a sentence that ``anchor_rx`` recognises.

    ``expect`` maps a (tier, code) key to (value, provenance).  The number is
    matched against the entry whose anchor word appears closest before it, so
    "R2F power is 0.92 ... the R3H power is 0.29" routes each to its own family
    without the family name having to be adjacent to the digit.
    """
    for m in anchor_rx.finditer(body):
        if expect is None:
            continue
        # the sentence containing the anchor
        lo = max((body.rfind(c, 0, m.start()) for c in ".;。；"), default=-1)
        hi_cuts = [body.find(c, m.start()) for c in ".;。；"]
        hi_cuts = [h for h in hi_cuts if h != -1]
        hi = min(hi_cuts) if hi_cuts else len(body)
        sent = body[lo + 1: hi]
        nums = _numbers_in(sent)
        if not nums:
            continue
        # nearest anchor word before each number decides the key
        anchors = [(a.start(), a.group(0)) for a in anchor_rx.finditer(sent)]
        for pos, num in nums:
            key = None
            for astart, atext in anchors:
                if astart <= pos:
                    key = atext
            if key is None:
                continue
            entry = expect.get(key)
            if entry is None:
                continue
            want, prov = entry
            _record(label, fails, passes, seen, float(num), _TOL[tol_key],
                    f"{what} [{key}]", prov, num)


def _record(label, fails, passes, seen, delta, tol, what, prov, printed,
            want=None) -> None:
    """Score one printed number.  ``delta`` = printed - recomputed.

    The failure line prints the RECOMPUTED value, not the delta.  The first
    version formatted the delta into the message, so a mismatch read
    "manuscript 4.5000 vs max promotion spread=0.5277" -- a number that is
    neither the manuscript's nor the artifact's, and that a reader cannot act
    on.
    """
    seen[0] += 1
    if abs(delta) <= tol:
        passes.append(f"{label}: {printed} == {what}  [{prov}]")
    else:
        expect = f"={want}" if want is not None else ""
        fails.append(f"{label}: manuscript {printed} vs recomputed {what}"
                     f"{expect} (off by {delta:+.4g}, tol {tol})  [{prov}]")


def check_paper(text: str, label: str, exp: dict) -> "tuple[list, list, int]":
    """Return (failures, passes, n_numbers_checked) for one manuscript."""
    fails: list = []
    passes: list = []
    seen = [0]
    body = _norm(text)

    def near(want, tol, what, prov, printed) -> None:
        """Compare a printed number against the recomputed ``want``.

        The delta is what the tolerance applies to -- passing the raw value
        made a NEGATIVE difference (manuscript minus recomputed) compare as a
        large magnitude, so every correct base-tier number was reported as
        "median = -139.0" against 140.
        """
        try:
            got = float(printed)
        except (TypeError, ValueError):
            return
        _record(label, fails, passes, seen, got - float(want), tol, what,
                prov, printed, want=want)

    # ---- R3H base/top medians --------------------------------------------
    # Both tiers are stated in the same sentence ("at 40/60 the median front
    # is 1 ... at 160/240 it rises to 140"), so a number is matched against the
    # tier tag NEAREST to it -- judged per (tier tag, anchor word) PAIR rather
    # than per sentence.  Scoring a whole sentence against one tier (the first
    # cut) reported the base reading 1 against the top median 140.
    for prefix, short, anchor in (
            ("front", "front-size median", r"front"),
            ("distinct_fq", "distinct-fq median",
             r"distinct[-\s_]?f[\s_-]?q")):
        table = {}
        for tier in (BASE, TOP):
            k = f"R3H_{prefix}_median_{tier}"
            if k in exp:
                table[tier] = exp[k]
        if len(table) != 2:
            continue
        for m in re.finditer(
                rf"(?P<tag>{_TIER_TAG_RX.pattern})"
                rf"[^;]{{0,90}}?{anchor}[^;]{{0,40}}?"
                rf"(?P<val>\d+(?:\.\d+)?)", body, re.IGNORECASE):
            tier = TOP if re.search(r"160|top", m.group("tag"), re.I) else BASE
            want, prov = table[tier]
            near(want, TOL["median_count"],
                 f"{short} @ {'top 160/240' if tier == TOP else 'base 40/60'}",
                 prov, m.group("val"))

    # ---- promotion ---------------------------------------------------------
    if "promotion_max_spread_db" in exp:
        want, prov = exp["promotion_max_spread_db"]
        for sent in _sentences(body):
            m = re.search(r"spread[^;]{0,40}?(\d+(?:\.\d+)?)", sent, re.I)
            if m:
                near(want, _round_tol(m.group(1)), "max promotion spread",
                     prov, m.group(1))
    if "promotion_threshold_db" in exp:
        want, prov = exp["promotion_threshold_db"]
        for sent in _sentences(body):
            m = re.search(r"threshold[^;]{0,40}?(\d+(?:\.\d+)?)\s*dB",
                          sent, re.I)
            if m:
                near(want, TOL["spread_db"], "promotion threshold", prov,
                     m.group(1))
    if "promotion_units" in exp:
        want, prov = exp["promotion_units"]
        for sent in _sentences(body):
            m = re.search(r"(\d+)\s*(?:units?|cells?|runs?)", sent, re.I)
            if m:
                near(want, 0.0, "promotion unit count", prov, m.group(1))

    # ---- per-family f_q ranges (A4: never mix calibers) -------------------
    for fam in FAMILIES:
        for key, which in ((f"{fam}_f_q_min", "min"),
                           (f"{fam}_f_q_max", "max")):
            if key not in exp:
                continue
            want, prov = exp[key]
            for sent in _sentences(body):
                if fam not in sent:
                    continue
                m = re.search(rf"{which}\D{{0,14}}?(\d+(?:\.\d+)?)", sent,
                              re.I)
                if m:
                    near(want, TOL["f_q"], f"{fam} f_q {which} @{TOP}", prov,
                         m.group(1))

    # ---- the SLS angle boundary (F-8 trap) --------------------------------
    if "SLS_exact_root_deg" in exp:
        root, prov = exp["SLS_exact_root_deg"]
        bound = exp["SLS_registered_bound_deg"][0]
        for sent in _sentences(body):
            m = re.search(r"(?:arccos|exact\s+root|精确根)"
                          r"[^;]{0,40}?(\d+(?:\.\d+)?)", sent, re.I)
            if m:
                near(root, TOL["deg"], "exact SLS root arccos(sqrt(k))", prov,
                     m.group(1))
        # The bound-vs-root ordering is an INTERNAL consistency check on the
        # registration, not a manuscript number: it is deliberately NOT counted
        # toward ``seen``.  Counting it made a manuscript with no checkable
        # numbers at all report "1 number checked, 0 mismatches" and exit 0 --
        # exactly the silent-zero green the ticket forbids
        # (feedback-figure-silent-zero).
        if not (root < bound):
            fails.append(f"{label}: the registered bound {bound} deg is not above "
                         f"the recomputed exact root {root} deg -- F-8 inverted")
        else:
            passes.append(f"{label}: registered bound {bound} deg > recomputed "
                          f"exact root {root} deg  [platform_kim2021]")

    # ---- the two-body ground-track repeat (B6 trap) -----------------------
    if "orbit_repeat_turns_simulated" in exp:
        want, prov = exp["orbit_repeat_turns_simulated"]
        for sent in _sentences(body):
            m = re.search(r"(\d+(?:\.\d+)?)\s*(?:orbits?|turns?|圈)",
                          sent, re.I)
            if m:
                near(want, TOL["orbit_turns"],
                     "simulated ground-track repeat period", prov, m.group(1))

    # ---- the power / effect-size pair (A2) --------------------------------
    # Anchored on the POWER word, not the family name: the family name appears
    # in a different clause from the percentage ("R2F power is 0.92 (7 seeds
    # for 80% power)"), so anchoring on the family picked up the 80 from the
    # seed clause and compared it against 0.92.
    for code in ("R2F", "R3H"):
        if code not in exp.get("power_at_delta", {}):
            continue
        want, prov = exp["power_at_delta"][code]
        for m in re.finditer(
                rf"{code}[^;]{{0,90}}?power[^;]{{0,20}}?is[^;]{{0,12}}?"
                rf"(\d+(?:\.\d+)?)\s*%?", body, re.IGNORECASE):
            near(want, TOL["fraction"], f"{code} power at delta", prov,
                 m.group(1))
        want, prov = exp["seeds_for_80pct"][code]
        for m in re.finditer(
                rf"{code}[^;]{{0,120}}?(\d+)\s*seeds?[^;]{{0,40}}?80", body,
                re.IGNORECASE):
            near(want, 0.0, f"{code} seeds for 80% power", prov, m.group(1))

    # ---- scenario drawn / served ------------------------------------------
    for code in FAMILIES:
        for key, what in (("n_drawn", "tasks drawn"),
                          ("n_served", "tasks served"),
                          ("n_windows", "windows enumerated")):
            if code not in exp.get(key, {}):
                continue
            want, prov = exp[key][code]
            for sent in _sentences(body):
                if code not in sent:
                    continue
                for _pos, num in _numbers_in(sent):
                    if float(num) == float(want):
                        seen[0] += 1
                        passes.append(f"{label}: {code} {what} = {want}  [{prov}]")
    return fails, passes, seen[0]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", action="append", required=True,
                    help="manuscript file (.md chapter / full.md / .tex); "
                         "repeatable")
    args = ap.parse_args(argv)

    for p in (PREREG, CALIBER):
        if not p.is_file():
            print(f"ABORT: missing registration artifact {p}", file=sys.stderr)
            return 2
    if not V3.is_dir():
        print(f"ABORT: missing artifact directory {V3}", file=sys.stderr)
        return 2

    papers = []
    for a in args.paper:
        p = Path(a)
        if not p.is_file():
            print(f"ABORT: manuscript {a} does not exist", file=sys.stderr)
            return 2
        papers.append(p)

    try:
        exp = recompute()
    except Exception as exc:                              # pragma: no cover
        print(f"ABORT: could not recompute the expectations: {exc}",
              file=sys.stderr)
        return 2

    print("=== recomputed from experiments/v3_results + the freeze ===")
    for k in sorted(exp):
        v = exp[k]
        if isinstance(v, dict):
            inner = {kk: vv[0] for kk, vv in v.items()}
            print(f"  {k} = {inner}")
        else:
            print(f"  {k} = {v[0]!r}   [{v[1]}]")

    all_fail: list = []
    all_pass: list = []
    total = 0
    print("\n=== manuscript numbers vs artifacts ===")
    for p in papers:
        text = p.read_text(encoding="utf-8", errors="ignore")
        fails, passes, seen = check_paper(text, p.name, exp)
        all_fail += fails
        all_pass += passes
        total += seen
        print(f"  {p.name}: {seen} number(s) checked, "
              f"{len(fails)} mismatch(es)")

    print(f"\n=== RESULT: {len(all_fail)} mismatch(es) over "
          f"{total} checked number(s) ===")
    for f in all_fail:
        print(f"FAIL   {f}")
    if total == 0:
        print("VERDICT: NO NUMBERS WERE EXTRACTED -- an extraction failure, "
              "not a pass (feedback-figure-silent-zero)")
        return 2
    if all_fail:
        print("VERDICT: the manuscript contradicts the frozen artifacts")
        return 1
    print(f"VERDICT: every checked number reproduces from the artifacts "
          f"({len(all_pass)} verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
