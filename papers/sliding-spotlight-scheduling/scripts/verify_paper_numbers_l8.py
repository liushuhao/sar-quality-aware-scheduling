#!/usr/bin/env python3
"""Ticket 50 -- L8 / caliber v5 manuscript-number ledger.

Why this file exists
--------------------
``verify_paper_numbers.py`` pins ``experiments/v3_results`` and takes no result
root, so after the paper moved to the L8 world (caliber v5, ticket 49) it kept
returning rc=0 without ever opening an L8 artifact.  "Green but irrelevant" is
worse than a failure because nothing reports it.  This ledger is the L8
counterpart: every number it checks is recomputed from ``experiments/v5_results``
and cross-checked against the per-unit pilots, and it refuses to pass when it
extracts nothing.

What it registers (ticket-50 amendment, analysis_prereg_v2.json)
---------------------------------------------------------------
  * MAIN RESULT FORM: the coverage-demand curve -- per family, the median
    served fraction over the frozen s grid {0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4,
    1.5, 2.0}, one value per s point, at the base budget 40/60.
  * FULFILLMENT RATIO: (i) library f_q, (ii) mean over ALL tie-set members
    (scripts/build_sweep_results.py:75-88), (iii) a REPORTED READING, not an
    optimization target.  A line stating the ratio must carry all three tags.
  * TIE-SET FACTS: every sweep unit is single-objective (n_obj=1), so a front's
    unique f1 count is 1 and "coverage passed/failed" has no meaning; the
    greedy anchor is coverage-optimal in 258 of 260 units.
  * INFEASIBLE POINTS: an all-exit-11 grid point is a structural fact, taken
    from the driver ledger -- never inferred from a missing artifact, which is
    how a crashed unit would be laundered as "no feasible individual".
  * RETIRED-WORLD TOKENS: the ban list is read from
    ``experiments/v5_results/reading_ledger_l8.json`` (single global
    definition; phase 3 uses the same file).

Tolerance policy: the tolerance is half a unit in the LAST PRINTED DIGIT, not
a fixed fraction.  A fixed 0.5 pp tolerance is wider than the whole spread the
R2F curve reports (adjacent medians differ by under 0.3 pp), so it would let a
draft swap two grid points and still pass.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/verify_paper_numbers_l8.py \
        [--paper paper/main.tex ...]

    Without --paper the tool prints the recomputed readings and exits 0
    (explicit readings-only mode: a banner names the mode, so an empty run can
    never look like a manuscript check).

rc:
  0  readings printed, or every extracted number reproduces
  1  at least one mismatch (the manuscript contradicts the L8 artifacts)
  2  extraction found nothing / the artifacts are unusable -- NOT a pass
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
V5 = FORK / "experiments" / "v5_results"
SWEEP = V5 / "sweep"
AGGREGATE = V5 / "sweep_results.json"
LEDGER = V5 / "reading_ledger_l8.json"
FAMILIES = ("R1C", "R2F", "R3H")
S_GRID = (0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 2.0)
N_SEEDS = 10


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def s_name(s: float) -> str:
    return f"s{str(s).replace('.', '_')}"


def _units(fam: str, s: float) -> "list[Path]":
    return sorted((SWEEP / s_name(s)).glob(f"pilot_{fam}_seed*.json"))


def _printed_tol(token: str) -> float:
    """Half a unit in the last printed digit (== a correct rounding).

    A percentage token is converted with it: "97.4%" is 0.974 to +/-0.0005, not
    +/-0.05, and getting that wrong hands the check a 5-point tolerance.
    """
    is_percent = token.strip().endswith("%")
    m = re.search(r"(\d+)(?:\.(\d+))?", token.replace(",", ""))
    dec = len(m.group(2) or "") if m else 0
    tol = 0.5 * 10 ** (-dec)
    return tol / 100.0 if is_percent else tol


def _exit_census(fam: str, s: float) -> "tuple[int, set, set]":
    """(n_exit11, exit11 keys, artifact seeds) from the DRIVER LEDGER.

    Exit-11 means "no feasible individual survived"; a unit that died any other
    way is a crash and must be reported as one, not folded into the structural
    fact.  An exit-11 unit must also own no artifact (a stale one would be
    double-counted as zero AND read as data).
    """
    sdir = SWEEP / s_name(s)
    progress = _load(sdir / "_progress.json")
    exits = {k: v["exit"] for k, v in progress["units"].items()
             if k.split("_")[0] == fam}
    bad = {k: e for k, e in exits.items() if e not in (0, 11)}
    if bad:
        raise RuntimeError(f"{fam} s={s}: unexpected exit codes {bad} -- a "
                           "crash, not a recorded outcome")
    e11 = {k for k, e in exits.items() if e == 11}
    seeds = {p.name.rsplit("seed", 1)[1][:-5] for p in _units(fam, s)}
    orphans = {k.rsplit("_", 1)[1] for k in e11} & seeds
    if orphans:
        raise RuntimeError(f"{fam} s={s}: exit-11 unit(s) {sorted(orphans)} own "
                           "an artifact")
    if len(seeds) + len(e11) != N_SEEDS:
        raise RuntimeError(f"{fam} s={s}: census break {len(seeds)}+"
                           f"{len(e11)} != {N_SEEDS}")
    return len(e11), e11, seeds


def recompute(need_deliv: bool = False) -> dict:
    """Recompute the L8 readings from the RAW units, then cross-check the
    aggregate.  Returns {key: (value, provenance)}.

    The cross-check matters: if ``sweep_results.json`` and the pilots disagree,
    every manuscript number derived from either is in doubt, and the tool must
    say so rather than pick one silently.
    """
    exp: dict = {}
    agg = _load(AGGREGATE)
    problems: list = []

    coverage: dict = {}
    fulfill: dict = {}
    exit11: dict = {}
    per_seed: dict = {}
    for fam in FAMILIES:
        for s in S_GRID:
            files = _units(fam, s)
            n_e11, _e11, _seeds = _exit_census(fam, s)
            if len(files) + n_e11 != N_SEEDS:
                problems.append(f"{fam} s={s}: {len(files)} artifacts + "
                                f"{n_e11} exit-11 != {N_SEEDS}")
            raw = [_load(p)["max_f1_star_on_front"] for p in files]
            covs = [0.0] * n_e11 + raw
            med = statistics.median(covs) if covs else None
            rec = agg["families"][fam][str(s)]
            # the FULL sorted array, not just the median: a tampered per-seed
            # value would otherwise pass a scalar comparison
            if sorted(covs) != sorted(rec["coverage_per_seed"]):
                problems.append(f"{fam} s={s}: per-seed array differs between "
                                "the raw units and the aggregate")
            if med is None or abs(med - rec["coverage_median"]) > 1e-12:
                problems.append(
                    f"{fam} s={s}: raw-unit median {med} != aggregate "
                    f"{rec['coverage_median']}")
            coverage[(fam, s)] = (med, f"median of {len(covs)} raw-unit "
                                       f"max_f1_star_on_front, exit-11 = 0")
            per_seed[(fam, s)] = (covs, "raw-unit coverage_per_seed")
            fulfill[(fam, s)] = (
                rec.get("f_q_fulfillment_ratio_median"),
                "sweep_results.f_q_fulfillment_ratio_median (library f_q, "
                "mean over the tie-set, build_sweep_results.py:75-88)")
            exit11[(fam, s)] = (n_e11,
                               "ledger exit-11 count (no artifact by design)")
    exp["coverage_median"] = coverage
    exp["coverage_per_seed"] = per_seed
    exp["fulfillment_median"] = fulfill
    exp["exit11"] = exit11

    # ---- criteria, recomputed from the medians -----------------------------
    checks = {}
    for fam in FAMILIES:
        m = [coverage[(fam, s)][0] for s in S_GRID]
        if any(v is None for v in m):
            raise RuntimeError(f"{fam}: a grid point has no median")
        c1 = all(a <= b + 1e-12 for a, b in zip(m[:-1], m[1:]))
        c2 = m[-1] >= m[-2] - 1e-12
        c3 = m[0] < m[3]
        got = agg["checks"][fam]
        if (c1, c2, c3) != (got["C1_monotone_s<=2.0"],
                            got["C2_saturation_2.0>=1.5"],
                            got["C3_tight_arm_drops(0.8<1.0)"]):
            problems.append(f"{fam}: criteria recomputed from medians differ "
                            "from the aggregate")
        checks[fam] = {"C1": c1, "C2": c2, "C3": c3}
    exp["criteria"] = (checks, "recomputed from the medians")

    # ---- coverage cost against each family's own saturation value ----------
    cost = {}
    for fam in FAMILIES:
        sat_s = max(S_GRID, key=lambda s: (coverage[(fam, s)][0], -s))
        cost[fam] = ((coverage[(fam, 1.0)][0] - coverage[(fam, sat_s)][0]) * 100.0,
                     f"order-point median minus the family's own saturation "
                     f"at s={sat_s}")
    exp["coverage_cost_pp"] = cost

    # ---- demand satisfaction -------------------------------------------------
    served = records = 0
    cv_max = 0.0
    anchor_opt = 0
    for fam in FAMILIES:
        for s in S_GRID:
            for p in _units(fam, s):
                art = _load(p)
                records += len(art["front"])
                served += sum(r["n_selected"] for r in art["front"])
                for r in art["front"]:
                    cv_max = max(cv_max, float(r.get("cv", 0.0)))
                if abs(art["max_f1_star_on_front"]
                       - art["anchor_f1_star"]) <= 1e-12:
                    anchor_opt += 1
    exp["served_task_instances"] = (served, "sum of front[*].n_selected")
    exp["tie_set_records"] = (records, "number of tie-set records")
    exp["delivery_cv_max"] = (cv_max, "max front[*].cv (0 = no violation)")
    exp["anchor_optimal_units"] = (anchor_opt,
                                   "max_f1_star_on_front == anchor_f1_star")

    # ---- tie-set facts (W9's anchor and the anchor-optimality reading) ------
    tie_units = vacuous = 0
    search_wins: list = []
    for fam in FAMILIES:
        for s in S_GRID:
            for p in _units(fam, s):
                art = _load(p)
                if art["promotion"]["decision"] == "vacuous_single_objective":
                    vacuous += 1
                if len({round(r["f1_star"], 12) for r in art["front"]}) == 1:
                    tie_units += 1
                if (art["max_f1_star_on_front"]
                        > art["anchor_f1_star"] + 1e-12):
                    search_wins.append(f"{p.name}@{s}")
    exp["sweep_units"] = (sum(len(_units(f, s)) for f in FAMILIES for s in S_GRID),
                          "pilot artifacts under sweep/s*/")
    exp["matrix_units"] = (len(list((V5 / "matrix").glob("pilot_*.json"))),
                           "pilot artifacts under matrix/")
    exp["vacuous_units"] = (vacuous, "promotion.decision == vacuous_single_objective")
    exp["tie_set_units"] = (tie_units, "fronts whose unique f1 count is 1")
    exp["search_win_units"] = (sorted(search_wins),
                               "max_f1_star_on_front > anchor_f1_star")

    # ---- the STR library floor (B1's step disclaimer) ----------------------
    sys.path.insert(0, str(FORK))
    sys.path.insert(0, str(FORK.parents[1] / "src"))
    try:
        from sss_core.modes import Mode, ModeLibrary
        lib = ModeLibrary.from_fixture()
        exp["str_floor_m"] = (float(lib.rho_az(Mode.STR)),
                              "ModeLibrary.from_fixture().rho_az(Mode.STR)")
    except Exception as exc:                      # pragma: no cover
        exp["str_floor_m_abort"] = (str(exc), "sss_core import failed")

    # ---- retention: mirrored, not recomputed here --------------------------
    retention = {}
    if LEDGER.is_file():
        for e in _load(LEDGER).get("entries", []):
            if e["id"].startswith("retention."):
                retention[e["id"].split(".", 1)[1]] = (
                    e["value"] * 100.0,
                    "mirrored from tests/test_verify_gate.py::retention_expect "
                    "(the gate test owns the 110-unit differential arm)")
    exp["retention_pct"] = (retention, "percent, STR-clip-only caliber")

    # ---- delivered caliber (only when the manuscript mentions it) ----------
    if need_deliv:
        exp["deliv"] = _deliv_stats()

    exp["_aggregate_problems"] = (problems,
                                  "raw-unit vs sweep_results.json cross-check")
    return exp


def _deliv_stats() -> dict:
    """Per-(family, s) medians of the descriptive delivered caliber.

    Expensive (it re-precompiles each unit), so it runs only when the
    manuscript actually states one of these readings.  The per-instance value
    comes from the ledger generator's ``deliv_value`` so the checker and the
    ledger cannot disagree; the independent re-derivation of that function is
    ``scripts/verify_fq_deliv_minunit.py``.
    """
    sys.path.insert(0, str(FORK))
    sys.path.insert(0, str(FORK.parents[1] / "src"))
    sys.path.insert(0, str(FORK / "scripts"))
    import build_reading_ledger_l8 as lb

    from sss_core.evaluator import SchedulingProblem
    from sss_core.modes import Mode, ModeLibrary
    from sss_core.nsga2 import load_manifest
    from sss_core.quality import ground_range_resolution_m

    lib = ModeLibrary.from_fixture()
    rho_rg = ground_range_resolution_m(lib)
    d_m = lib.geo.D_m
    out = {}
    for fam in FAMILIES:
        for s in S_GRID:
            vals, sec2 = [], []
            for p in _units(fam, s):
                art = _load(p)
                manifest = load_manifest(
                    V5 / "scenarios" / Path(art["manifest"]).name)
                if s != 1.0:
                    for t in manifest["tasks"]:
                        if t.get("rho_req_m") is not None:
                            t["rho_req_m"] = s * float(t["rho_req_m"])
                sp = SchedulingProblem(manifest, lib)
                for rec in art["front"]:
                    for k, start in rec["starts"].items():
                        plan = sp.plans[int(k)]
                        if plan.mode is Mode.STR or plan.rho_req_m is None:
                            continue
                        val, psi = lb.deliv_value(plan, start, lib, rho_rg, d_m)
                        vals.append(val)
                        sec2.append(1.0 / math.cos(psi) ** 2)
            out[(fam, s)] = {
                "median": statistics.median(vals) if vals else None,
                "sec2_median": statistics.median(sec2) if sec2 else None,
            }
    return out


# --------------------------------------------------------------------------
# Extraction from the manuscript
# --------------------------------------------------------------------------
_SENT_SPLIT = re.compile(r"(?<=[.;。；])\s+")
_S_TAG = re.compile(r"\bs\s*=\s*(\d(?:\.\d)?)\b|订单原要求|order\s+point",
                    re.IGNORECASE)
_S_TAG_ANY = re.compile(r"\bs\s*=\s*\d(?:\.\d)?", re.IGNORECASE)


def _family_in(sent: str):
    for fam in FAMILIES:
        if fam in sent:
            return fam
    return None


def _s_in(sent: str):
    m = _S_TAG.search(sent)
    if not m:
        return None
    if m.group(1):
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return 1.0                      # "订单原要求" / "order point" == s=1.0


def _blank_s_tag(sent: str) -> str:
    """Drop the s-tag number so it cannot be scored as the reading itself."""
    return _S_TAG_ANY.sub(" ", sent)


def check_paper(text: str, label: str, exp: dict) -> "tuple[list, list, list, int]":
    fails: list = []
    passes: list = []
    seen = 0
    # Line scope is kept: the caliber tag must travel on the LINE that states
    # the number (W13/W15a's obligation), and collapsing newlines would let a
    # tag on a later line license the reading.
    for line in text.replace("\\_", "_").splitlines():
        line = re.sub(r"[ \t]+", " ", line)
        if not line.strip():
            continue
        for sent in _SENT_SPLIT.split(line):
            fam, s = _family_in(sent), _s_in(sent)
            blank = _blank_s_tag(sent)

            # ---- coverage reading ------------------------------------------
            # A coverage-COST sentence also contains the word "coverage" and a
            # number, so it must not be scored against the curve: the number it
            # carries is a difference in percentage points, not a level.
            is_cost = bool(
                re.search(r"\bcost\b[^;]{0,40}?\d+(?:\.\d+)?\s*"
                          r"(?:pp|percentage\s+points)", blank, re.I)
                and re.search(r"saturat|饱和", sent, re.I))
            if (fam and s is not None and not is_cost
                    and re.search(r"coverage|覆盖", sent, re.I)):
                idx = sent.lower().find("coverage")
                if idx == -1:
                    idx = sent.find("覆盖")
                tail = _blank_s_tag(sent[idx:])
                m = re.search(r"(\d+(?:\.\d+)?)\s*(%?)", tail)
                if m:
                    printed = float(m.group(1))
                    if m.group(2):
                        printed /= 100.0
                    want, prov = exp["coverage_median"][(fam, s)]
                    seen += 1
                    _score(label, fails, passes, printed, want,
                           _printed_tol(m.group(0)), f"{fam} coverage @ s={s}",
                           prov, m.group(0))

            # ---- coverage cost against the family's own saturation ---------
            cm = re.search(r"\bcost\b[^;]{0,40}?(\d+(?:\.\d+)?)\s*"
                           r"(?:pp|percentage\s+points)", blank, re.I)
            if cm and fam and re.search(r"saturat|饱和", sent, re.I) and (
                    s == 1.0 or re.search(r"order\s+point|订单", sent, re.I)):
                printed = abs(float(cm.group(1)))
                want, prov = exp["coverage_cost_pp"][fam]
                seen += 1
                _score(label, fails, passes, printed, abs(want),
                       _printed_tol(cm.group(1)), f"{fam} coverage cost (pp)",
                       prov, cm.group(0))

            # ---- infeasible grid point -------------------------------------
            im = re.search(r"\b(?:no\s+feasible|infeasible)\b[^;]{0,60}?"
                           r"(\d+)\s+of\s+10\b", blank, re.I)
            if im and fam and s is not None:
                want, prov = exp["exit11"][(fam, s)]
                seen += 1
                _score(label, fails, passes, float(im.group(1)), float(want),
                       _printed_tol(im.group(1)),
                       f"{fam} infeasible units @ s={s}", prov, im.group(0))

            # ---- demand satisfaction ---------------------------------------
            dm = re.search(r"(\d[\d,]*)\s+task[\s-]*instances", sent, re.I)
            if dm:
                printed = float(dm.group(1).replace(",", ""))
                want, prov = exp["served_task_instances"]
                seen += 1
                _score(label, fails, passes, printed, float(want),
                       _printed_tol(dm.group(1)), "served task instances",
                       prov, dm.group(0))

            # ---- retention --------------------------------------------------
            rm = re.search(r"retention[^;]{0,40}?(\d+(?:\.\d+)?)\s*%", blank,
                           re.I)
            if rm and fam:
                retain = exp["retention_pct"][0]
                if fam in retain:
                    want, prov = retain[fam]
                    seen += 1
                    _score(label, fails, passes, float(rm.group(1)), want,
                           _printed_tol(rm.group(1)), f"{fam} retention (%)",
                           prov, rm.group(0))

            # ---- delivered caliber (descriptive variant) --------------------
            dq = re.search(r"f[_ ]?q[_ ]?deliv[^;]{0,50}?(\d+(?:\.\d+)?)",
                           blank, re.I)
            if dq and fam and s is not None and "deliv" in exp:
                want = exp["deliv"][(fam, s)]["median"]
                seen += 1
                if want is None:
                    fails.append(f"{label}: {fam} f_Q_deliv @ s={s} has no "
                                 "defined domain")
                else:
                    _score(label, fails, passes, float(dq.group(1)), want,
                           _printed_tol(dq.group(1)),
                           f"{fam} f_Q_deliv @ s={s}",
                           "recomputed from the stored starts", dq.group(0))
            sl = re.search(r"squint[-\s]?loss[^;]{0,50}?(\d+(?:\.\d+)?)", blank,
                           re.I)
            if sl and fam and s is not None and "deliv" in exp:
                want = exp["deliv"][(fam, s)]["sec2_median"]
                seen += 1
                if want is None:
                    fails.append(f"{label}: {fam} squint-loss @ s={s} has no "
                                 "defined domain")
                else:
                    _score(label, fails, passes, float(sl.group(1)), want,
                           _printed_tol(sl.group(1)),
                           f"{fam} squint-loss factor @ s={s}",
                           "median of 1/cos^2(psi_sel)", sl.group(0))

            # ---- fulfillment reading (three-part tag obligatory) ------------
            fm = re.search(r"(?:fulfillment[-\s]?ratio|兑现率)[^;]{0,40}?"
                           r"(\d+(?:\.\d+)?)", blank, re.I)
            if fm and fam and s is not None:
                printed = float(fm.group(1))
                want, prov = exp["fulfillment_median"][(fam, s)]
                seen += 1
                if want is not None:
                    _score(label, fails, passes, printed, want,
                           _printed_tol(fm.group(1)),
                           f"{fam} fulfillment ratio @ s={s}", prov, fm.group(0))
            if fm:
                missing = [n for n, rx in (
                    ("library caliber", r"library[-\s]?caliber|库口径"),
                    ("tie-set mean", r"tie[-\s]?set|全体成员"),
                    ("reading, not a target",
                     r"not\s+an?\s+(?:optimization|optimisation)\s+target|"
                     r"报告读数|非优化目标|不进目标"),
                ) if not re.search(rx, line, re.I)]
                if missing:
                    fails.append(f"{label}: fulfillment-ratio reading lacks "
                                 f"caliber element(s) {missing}  [{line[:90]!r}]")

            # ---- the STR floor (a step, not a continuous degradation) ------
            sm = re.search(r"STR[^;]{0,60}?(?:floor|地板)[^;]{0,20}?"
                           r"(\d+(?:\.\d+)?)\s*m", sent, re.I)
            if sm and "str_floor_m" in exp:
                printed = float(sm.group(1))
                want, prov = exp["str_floor_m"]
                seen += 1
                _score(label, fails, passes, printed, want,
                       _printed_tol(sm.group(1)), "STR library floor", prov,
                       sm.group(0))
    return fails, passes, [], seen


def reverse_check(text: str, label: str) -> "tuple[list, list]":
    """Retired-world tokens in the manuscript.

    Both lists come from the ledger's ``manuscript_ban_list`` -- one global
    definition, so phase 3 and this checker cannot drift apart.
    """
    if not LEDGER.is_file():
        return [], ["note: no reading ledger -- retired-world token check "
                    "skipped"]
    bans = _load(LEDGER).get("manuscript_ban_list", {})
    hard = [(b["id"], re.compile(b["regex"], re.I)) for b in bans.get(
        "hard_banned", [])]
    soft = [(b["id"], re.compile(b["regex"], re.I)) for b in bans.get(
        "allowed_with_label", [])]
    label_rx = re.compile(bans.get("required_label_regex", r"(?!)"), re.I)
    fails: list = []
    for no, line in enumerate(text.replace("\\_", "_").splitlines(), 1):
        flat = re.sub(r"[ \t]+", " ", line)
        for bid, rx in hard:
            m = rx.search(flat)
            if m:
                fails.append(f"{label}:{no}: retired-world token {bid!r} "
                             f"({m.group(0)!r}) -- it belongs to a superseded "
                             "world and must not appear")
        for bid, rx in soft:
            m = rx.search(flat)
            if m and not label_rx.search(flat):
                fails.append(f"{label}:{no}: {bid!r} ({m.group(0)!r}) appears "
                             "without an explicit retracted/superseded label "
                             "on the same line")
    return fails, []


def _score(label, fails, passes, printed, want, tol, what, prov, printed_raw):
    if want is None:
        fails.append(f"{label}: {what} has no registered L8 reading  [{prov}]")
        return
    delta = printed - float(want)
    if abs(delta) <= tol:
        passes.append(f"{label}: {what} = {printed}  [{prov}]")
    else:
        fails.append(f"{label}: manuscript {printed} vs recomputed {what}="
                     f"{want} (off by {delta:+.4g}, tol {tol})  [{prov}]")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", action="append", default=None,
                    help="manuscript file(s) to check; omit for readings only")
    args = ap.parse_args(argv)

    if not AGGREGATE.is_file():
        print(f"ABORT: missing L8 aggregate {AGGREGATE}", file=sys.stderr)
        return 2

    texts = {}
    if args.paper:
        for a in args.paper:
            p = Path(a)
            if not p.is_file():
                print(f"ABORT: manuscript {a} does not exist", file=sys.stderr)
                return 2
            texts[p] = p.read_text(encoding="utf-8", errors="ignore")
    need_deliv = any(re.search(r"f[_ ]?q[_ ]?deliv|squint[-\s]?loss", t, re.I)
                     for t in texts.values())

    try:
        exp = recompute(need_deliv=need_deliv)
    except Exception as exc:
        print(f"ABORT: could not recompute the L8 expectations: {exc}",
              file=sys.stderr)
        return 2

    problems, _ = exp["_aggregate_problems"]
    if problems:
        print("=== raw units and sweep_results.json DISAGREE ===")
        for p in problems:
            print(f"MISMATCH   {p}")
        print("VERDICT: the L8 artifact and its aggregate disagree -- no number "
              "derived from either can be trusted")
        return 1

    print("=== L8 / caliber v5 recomputed from experiments/v5_results ===")
    print(f"  sweep units      = {exp['sweep_units'][0]}")
    print(f"  matrix units     = {exp['matrix_units'][0]}")
    print(f"  vacuous units    = {exp['vacuous_units'][0]}")
    print(f"  tie-set units    = {exp['tie_set_units'][0]}")
    print(f"  anchor-optimal   = {exp['anchor_optimal_units'][0]}")
    print(f"  search-win units = {exp['search_win_units'][0]}")
    print(f"  served instances = {exp['served_task_instances'][0]} "
          f"over {exp['tie_set_records'][0]} records "
          f"(cv max {exp['delivery_cv_max'][0]})")
    if "str_floor_m" in exp:
        print(f"  STR library floor= {exp['str_floor_m'][0]:.4f} m")
    for fam in FAMILIES:
        vals = ", ".join(
            f"s={s}: cov {exp['coverage_median'][(fam, s)][0]:.4f}"
            + (f" / ful {exp['fulfillment_median'][(fam, s)][0]:.4f}"
               if exp["fulfillment_median"][(fam, s)][0] is not None else "")
            for s in S_GRID)
        print(f"  {fam}: {vals}")
        print(f"    cost vs own saturation: "
              f"{exp['coverage_cost_pp'][fam][0]:+.2f} pp; criteria "
              f"{exp['criteria'][0][fam]}")

    if not args.paper:
        print("\nMODE: readings only (no --paper supplied) -- this is NOT a "
              "manuscript check")
        return 0

    all_fail: list = []
    all_pass: list = []
    reverse: list = []
    total = 0
    print("\n=== manuscript L8 numbers vs artifacts ===")
    for p, text in texts.items():
        fails, passes, _notes, seen = check_paper(text, p.name, exp)
        rev, _ = reverse_check(text, p.name)
        all_fail += fails
        all_pass += passes
        reverse += rev
        total += seen
        print(f"  {p.name}: {seen} L8 number(s) checked, {len(fails)} "
              f"mismatch(es), {len(rev)} retired-world token(s)")

    print(f"\n=== RESULT: {len(all_fail)} mismatch(es) over {total} checked ===")
    for f in all_fail:
        print(f"FAIL   {f}")

    if total == 0:
        print("\n=== retired-world tokens (expected until the phase-3 rewrite) ===")
        for r in reverse:
            print(f"PENDING   {r}")
        print("VERDICT: NO L8 NUMBERS WERE EXTRACTED -- an extraction failure, "
              "not a pass (the manuscript is still on the v3 world)")
        return 2

    if reverse:
        print(f"\n=== retired-world tokens: {len(reverse)} ===")
        for r in reverse:
            print(f"FAIL   {r}")
        all_fail += reverse
    if all_fail:
        print("VERDICT: the manuscript contradicts the L8 artifacts")
        return 1
    print(f"VERDICT: every checked L8 number reproduces ({len(all_pass)} "
          "verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
