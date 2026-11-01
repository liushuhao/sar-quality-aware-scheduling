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
import os
import re
import statistics
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
V5 = FORK / "experiments" / "v5_results"
SWEEP = V5 / "sweep"
AGGREGATE = V5 / "sweep_results.json"
LEDGER = V5 / "reading_ledger_l8.json"
CENSUS = Path(__file__).resolve().parent / "readings_census.json"
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


def _moves_bind(moves_m, mv) -> list:
    """Bind printed per-seed movers to registered ones, one-to-one, by verb.

    The manuscript prints magnitudes; the registered movers are signed
    (positive = the seed lost coverage).  The verb carries the missing sign:
    "loses X" can only be a registered +X, "gains X" only a -X.  Matching
    each printed value against the whole registered set -- the behaviour
    before 2026-11-01 -- let "one loses 1.83 ... one gains 0.42" pass with
    the two numbers exchanged, because the set is unchanged (R104).  Each
    registered value is consumed at most once, so a sentence cannot satisfy
    two clauses from one mover.

    Within one polarity the two lists are sorted and paired in order: for
    one-dimensional tolerance matching that is optimal (an exchange argument
    on any crossing pair), and it is O(n log n) where a permutation search is
    n! -- measured 4.8 s for a ten-clause sentence against the ten-mover row.

    The registered movers carry their seed id (2026-11-01, R105): a sentence
    that claims the SAME seed moves in two dips can only be checked if the
    binding knows which seed each printed magnitude belongs to.  The pairing
    is still by magnitude, so the id rides along as a consequence of the
    correct match, not as an input to it.

    Returns [(match, seed, registered_value)] in sentence order, or [] when
    no assignment exists.
    """
    if len(mv) != len(moves_m):
        return []
    out = []
    for sign in (1.0, -1.0):
        reg = sorted(((seed, q) for seed, q in mv if q * sign > 0),
                     key=lambda t: t[1])
        prt = [(m, float(m.group(1))) for m in moves_m
               if (1.0 if _lose_word(m.group(0)) else -1.0) == sign]
        if len(reg) != len(prt):
            return []
        prt.sort(key=lambda t: t[1])
        for (m, val), (seed, q) in zip(prt, reg):
            if abs(val - abs(q)) > _printed_tol(m.group(1)):
                return []
            out.append((m, seed, q))
    order = {id(m): i for i, m in enumerate(moves_m)}
    return sorted(out, key=lambda t: order[id(t[0])])


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

    # ---- the two local declines and their per-seed movers ------------------
    # A "dip" is the median difference between two adjacent grid points, in
    # percentage points; the "movers" are the per-seed differences behind it
    # (only nonzero movers are registered -- the paper accounts exactly those).
    dips: dict = {}
    moves: dict = {}
    for fam in FAMILIES:
        for a, b in ((0.8, 0.9), (1.3, 1.4)):
            ma, mb = coverage[(fam, a)][0], coverage[(fam, b)][0]
            if ma is not None and mb is not None:
                dips[(fam, a, b)] = (
                    (ma - mb) * 100.0,
                    f"median s={a} minus median s={b}, pp")
            pa = {p.name.rsplit("seed", 1)[1][:-5]:
                  _load(p)["max_f1_star_on_front"] for p in _units(fam, a)}
            pb = {p.name.rsplit("seed", 1)[1][:-5]:
                  _load(p)["max_f1_star_on_front"] for p in _units(fam, b)}
            mv = [(seed, (pa[seed] - pb[seed]) * 100.0)
                  for seed in sorted(set(pa) & set(pb))
                  if abs(pa[seed] - pb[seed]) > 1e-12]
            if mv:
                moves[(fam, a, b)] = (mv,
                                      f"per-seed s={a} minus s={b}, pp, "
                                      "nonzero movers only")
    exp["dip_pp"] = dips
    exp["per_seed_moves"] = moves

    # ---- census numbers the results section states -------------------------
    exp["launched_units"] = (N_SEEDS * len(FAMILIES) * len(S_GRID),
                             "nine grid points x three families x ten seeds")
    exp["treatment_units"] = (sum(len(_units(f, s)) for f in ("R2F", "R3H")
                                  for s in S_GRID),
                              "sweep artifacts of the two treatment families")

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
        exp["mode_floor_m"] = (
            {m.name: float(lib.rho_az(m)) for m in (Mode.STR, Mode.SLS,
                                                    Mode.SPT)},
            "ModeLibrary.from_fixture().rho_az(mode), zero-squint")
        # R50: the per-mode library f_q constants and their magnitude ratios
        # are PRINTED in the quality-model section, so they belong under the
        # number gate -- a fixture change would otherwise fork the printed
        # text from the platform figure silently.
        from sss_core.quality import f_q_per_task
        _fq = {m.name: float(f_q_per_task(m, 0.0, lib.geo.R0_m, lib))
               for m in (Mode.STR, Mode.SLS, Mode.SPT)}
        exp["mode_fq_const"] = (
            _fq, "sss_core.quality.f_q_per_task(mode, psi=0, r=lib.geo.R0_m)")
        exp["mode_fq_ratio"] = (
            {("SLS", "STR"): _fq["SLS"] / _fq["STR"],
             ("SPT", "STR"): _fq["SPT"] / _fq["STR"],
             ("SPT", "SLS"): _fq["SPT"] / _fq["SLS"]},
            "ratio of the recomputed per-mode f_q constants")
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
_S_TAG = re.compile(r"\bs\s*=\s*(\d(?:\.\d)?)\b|订单原要求|as-placed\s+point",
                    re.IGNORECASE)
_S_TAG_ANY = re.compile(r"\bs\s*=\s*\d(?:\.\d)?", re.IGNORECASE)
# Family codes R1C/R2F/R3H and world tags L7/L8/v5 contain digits; a bare
# \d+ would read those as candidate readings and truncate a trailing
# "for R3H" context before the pairing phrase completes (measured: the "3"
# of R3H was scored, and the "8" of L8 failed a synthetic draft).  Digits
# directly preceded by a letter are therefore not candidate numbers, and
# the same truncation happens at the "50" of "50-task family", so any number
# whose tail is digit/dash + "task" is excluded too (the lookahead must span
# digits, or the engine backtracks to "5" and slips past it).
_NUM = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?(?![\d-]*task\b)")
_COST_RE = re.compile(r"\bcost\b[^;]{0,40}?(\d+(?:\.\d+)?)\s*"
                      r"(?:pp|percentage\s+points)", re.IGNORECASE)
_DELIV_TOKEN = re.compile(r"f[_ ]?\{?\\?Q[_, ]?\\?(?:mathrm|text)?\{?deliv"
                          r"\}?\}?", re.IGNORECASE)
_DELIV_NUM = re.compile(r"(\d+(?:\.\d+)?)\s*m\s*\$\^\{?-2\}?\$")
_FUL_FAM = re.compile(r"for\s+(R1C|R2F|R3H)", re.IGNORECASE)
_RET_FAM = re.compile(r"for\s+the\s+(control|50-task|100-task)\s+family",
                      re.IGNORECASE)
_RET_FAM_MAP = {"control": "R1C", "50-task": "R2F", "100-task": "R3H"}
_FAM_DESC = (("R1C", r"control\s+family|single[-\s]orbit"),
             ("R2F", r"50[-\s]task"),
             ("R3H", r"100[-\s]task"))
_RANGE_CTX = re.compile(r"from\s+\$?s\s*=\s*(\d(?:\.\d)?)[^;]*?"
                        r"to\s+\$?s\s*=\s*(\d(?:\.\d)?)", re.IGNORECASE)
# The closing math "$" sits between a grid value and the following "and" in
# the LaTeX faces ("$s=0.8$ and $s=0.9$"), so the between/range patterns eat
# an optional "$" after each number.
_BETWEEN = re.compile(r"between\s+\$?s\s*=\s*(\d(?:\.\d)?)\$?\s+and\s+"
                      r"\$?s\s*=\s*(\d(?:\.\d)?)\$?", re.IGNORECASE)
_MOVE = re.compile(r"\b(?:lose[sd]?|losing|gain[sd]?|gaining)\s+\$?"
                   r"(\d+(?:\.\d+)?)\$?", re.IGNORECASE)


def _lose_word(text: str) -> bool:
    """True for the "lost coverage" polarity of a printed mover clause."""
    return re.match(r"los", text.strip(), re.IGNORECASE) is not None
# R105: a sentence that claims seed IDENTITY across two dips -- "the same seed
# gains 0.42 points as in the first dip, and a different seed loses 1.14".
# The magnitudes and verbs are bound as before; these clauses say which SEED
# each one belongs to, which is checkable once the movers carry their seed ids.
_SAME_SEED = re.compile(r"same\s+seed[^.;]{0,40}?(lose[sd]?|losing|gain[sd]?|"
                        r"gaining)\s+\$?(\d+(?:\.\d+)?)", re.IGNORECASE)
_DIFF_SEED = re.compile(r"(?:a\s+)?(?:different|another)\s+seed[^.;]{0,40}?"
                        r"(lose[sd]?|losing|gain[sd]?|gaining)\s+\$?"
                        r"(\d+(?:\.\d+)?)", re.IGNORECASE)
_PRIOR_DIP = re.compile(r"first\s+(?:dip|decline)|previous\s+(?:dip|decline)|"
                        r"earlier\s+(?:dip|decline)", re.IGNORECASE)
# Any wording that claims seed identity: if a sentence carries one of these but
# neither clause pattern can read it, the claim is unchecked -- that must fail,
# not pass (the escape R104 closed for the magnitudes themselves, 2026-11-01
# review: "another seed" and "the same seed that lost ..." both slipped past).
_IDENT_VOCAB = re.compile(r"\b(?:same|different|another|other)\s+seeds?\b|"
                          r"同一个种子|不同种子", re.IGNORECASE)
_MOVE_VERB = re.compile(r"\b(?:lose[sd]?|losing|gain[sd]?|gaining)\b", re.IGNORECASE)
_DIP = re.compile(r"(\d+(?:\.\d+)?)\s+(?:pp|percentage\s+points)\s+between\s+"
                  r"\$?s\s*=\s*(\d(?:\.\d)?)\$?\s+and\s+\$?s\s*=\s*"
                  r"(\d(?:\.\d)?)\$?", re.IGNORECASE)
_MODE_FLOOR = re.compile(r"rho_\{a,\\mathrm\{(STR|SLS|SPT)\}\}[^;]{0,60}?"
                         r"(\d+(?:\.\d+)?)\s*\$?\s*~?m", re.IGNORECASE)

# R50: the printed per-mode f_q constants ("$0.8107$ (STR)") and their
# magnitude ratios ("$24.3\times$ (SLS over STR)").  The ratio form carries
# a LaTeX macro (and its closing "$") between the number and the
# parenthesis, so both are part of the pattern.
_MODE_FQ_CONST_RX = re.compile(
    r"\$?(\d+(?:\.\d+)?)\$?\s*\((STR|SLS|SPT)\)")
_MODE_FQ_RATIO_RX = re.compile(
    r"(\d+(?:\.\d+)?)\s*\\times\$?\s*"
    r"\((STR|SLS|SPT)\s+over\s+(STR|SLS|SPT)\)")


def _family_in(sent: str):
    for fam in FAMILIES:
        if fam in sent:
            return fam
    return None


def _fam_in_text(sent: str):
    """Family code, or the family a descriptive phrase names."""
    fam = _family_in(sent)
    if fam:
        return fam
    for code, rx in _FAM_DESC:
        if re.search(rx, sent, re.I):
            return code
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
    return 1.0                      # "订单原要求" / "as-placed point" == s=1.0


def _s_in_ctx(ctx: str):
    """s value from a context string (the first tag it contains)."""
    m = _S_TAG.search(ctx)
    if not m:
        return None
    if m.group(1):
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return 1.0


def _s_tags(sent: str) -> "list[tuple[int, float]]":
    """(position, s value) for every s-tag in the sentence, in order."""
    out = []
    for m in _S_TAG.finditer(sent):
        if m.group(1):
            try:
                out.append((m.start(), float(m.group(1))))
            except ValueError:
                continue
        else:
            out.append((m.start(), 1.0))
    return out


def _blank_s_tag(sent: str) -> str:
    """Drop the s-tag number so it cannot be scored as the reading itself.

    Length-preserving: every tag match becomes same-length spaces, so number
    positions in the blanked text equal the original positions and the
    cost-match exclusion can use spans from either view.
    """
    return _S_TAG_ANY.sub(lambda m: " " * len(m.group(0)), sent)


def _seed_identity(sent: str, label: str, fam: str, lo: float, hi: float,
                   bound: list, moves_reg: dict) -> list:
    """Check "the same seed ... as in the first dip" against the seed ids.

    Until 2026-11-01 the gate bound printed magnitudes to registered ones by
    verb and value only, so the sentence's identity claim -- that the seed
    which gains in the second dip is the seed that gained in the first -- was
    outside the check (R105): exchanging WHICH seed the text credits left
    every magnitude in place.  The movers now carry their seed id, so the
    claim is decidable:

    * every identity clause must be readable; an identity word the patterns
      cannot parse is a fail, not a silent pass (the escape R104 closed for
      the magnitudes themselves);
    * "the same seed ... as in the first dip" requires that seed to be a
      mover of the referenced earlier dip, with that same magnitude;
    * "a different seed" requires a seed different from the one the sentence
      just named.

    The earlier dip is resolved from the registered data (the nearest dip of
    the same family that ends before this one starts), not from a hard-coded
    key, so a re-registered grid cannot leave the check pointing at a stale
    pair.
    """
    same = list(_SAME_SEED.finditer(sent))
    diff = list(_DIFF_SEED.finditer(sent))
    if not same and not diff:
        return []
    out: list = []

    def sign_of(m) -> float:
        return 1.0 if _lose_word(m.group(1)) else -1.0

    def seeds_of(clause):
        verb, val = sign_of(clause), float(clause.group(2))
        return [s for m, s, _q in bound
                if (1.0 if _lose_word(m.group(0)) else -1.0) == verb
                and abs(float(m.group(1)) - val) <= _printed_tol(clause.group(2))]

    priors = [(key[2], key) for key in moves_reg
              if key[0] == fam and key[2] <= lo + 1e-9]
    prior = max(priors)[1] if priors else None
    if same and prior is None:
        out.append(f"{label}: 'same seed' claim at s={lo}->{hi} for {fam} has "
                   f"no earlier registered dip to compare against  "
                   f"[{sent[:90]!r}]")
        return out
    prior_moves = dict((s, q) for s, q in moves_reg[prior][0]) if prior else {}

    ref_seed = None
    if same and not _PRIOR_DIP.search(sent):
        out.append(f"{label}: 'same seed' clause does not name the dip it "
                   f"points back to (first/previous/earlier)  "
                   f"[{sent[:90]!r}]")
    # EVERY same-seed clause is verified, not just the first (2026-11-01
    # review: "… as in the first dip, and the same seed loses 1.14" passed
    # because only same[0] was looked at).
    for clause in same:
        hits = seeds_of(clause)
        if len(hits) != 1:
            out.append(f"{label}: 'same seed' clause gains/loses "
                       f"{clause.group(2)} but that magnitude binds to "
                       f"{len(hits)} mover(s)  [{sent[:90]!r}]")
            continue
        if ref_seed is None:
            ref_seed = hits[0]
        if hits[0] not in prior_moves:
            out.append(f"{label}: text says seed {hits[0]} moved the same "
                       f"way in both dips, but at s={prior[1]}->{prior[2]} "
                       f"the movers are seeds "
                       f"{sorted(prior_moves)}  [{sent[:90]!r}]")
        elif abs(abs(prior_moves[hits[0]]) - float(clause.group(2))) > \
                _printed_tol(clause.group(2)):
            out.append(f"{label}: seed {hits[0]} moves "
                       f"{abs(prior_moves[hits[0]]):.4f} pp at "
                       f"s={prior[1]}->{prior[2]} but the sentence prints "
                       f"{clause.group(2)} 'as in the first dip'  "
                       f"[{sent[:90]!r}]")

    for clause in diff:
        hits = seeds_of(clause)
        if len(hits) != 1:
            out.append(f"{label}: 'different seed' clause gains/loses "
                       f"{clause.group(2)} but that magnitude binds to "
                       f"{len(hits)} mover(s)  [{sent[:90]!r}]")
            continue
        if ref_seed is None:
            out.append(f"{label}: 'different seed' clause has no seed to be "
                       f"different FROM -- the sentence never names the "
                       f"first one  [{sent[:90]!r}]")
        elif hits[0] == ref_seed:
            out.append(f"{label}: the clause is introduced as a DIFFERENT "
                       f"seed, but it binds to seed {hits[0]} -- the same one "
                       f"the previous clause credits  [{sent[:90]!r}]")
    return out


def check_paper(text: str, label: str, exp: dict) -> "tuple[list, list, list, int]":
    """Score EVERY reading in each sentence, not just the first.

    Ticket-50 phase-5 correction: the results section packs several readings
    into one sentence (one sentence carries all nine curve medians), and the
    earlier ``re.search`` asserted only the first number per sentence -- a
    mutation test showed 8 of 14 probed manuscript numbers could be changed
    with the gate still green.  Each class below now walks all candidate
    numbers and pairs each one with its own (family, s) context.
    """
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

        # ---- delivered caliber (descriptive variant): line-level -----------
        # The token and the number can sit in different sentences of the same
        # line (the label sentence and the reading sentence), so this class
        # runs on the line rather than the sentence.
        if "deliv" in exp and _DELIV_TOKEN.search(line):
            fam_l, s_l = _family_in(line), _s_in(line)
            if fam_l and s_l is not None:
                for m in _DELIV_NUM.finditer(line):
                    want = exp["deliv"][(fam_l, s_l)]["median"]
                    seen += 1
                    if want is None:
                        fails.append(f"{label}: {fam_l} f_Q_deliv @ s={s_l} "
                                     "has no defined domain")
                    else:
                        _score(label, fails, passes, float(m.group(1)), want,
                               _printed_tol(m.group(1)),
                               f"{fam_l} f_Q_deliv @ s={s_l}",
                               "recomputed from the stored starts", m.group(0))

        for sent in _SENT_SPLIT.split(line):
            fam, s = _family_in(sent), _s_in(sent)
            blank = _blank_s_tag(sent)

            # ---- coverage reading ------------------------------------------
            # A coverage-COST sentence also contains the word "coverage" and a
            # number, so the number the cost states must not be scored against
            # the curve: it is a difference in percentage points, not a level.
            is_cost = bool(
                _COST_RE.search(blank)
                and re.search(r"saturat|饱和", sent, re.I))
            is_drop_form = bool(re.search(
                r"drops?\s+\d|within\s+[\d.]+\s+points",
                sent, re.I))
            if (fam and re.search(r"coverage|覆盖", sent, re.I)
                    and not is_drop_form):
                idx = sent.lower().find("coverage")
                if idx == -1:
                    idx = sent.find("覆盖")
                cost_span = None
                if is_cost:
                    cm = _COST_RE.search(blank)
                    if cm:
                        cost_span = (cm.start(1), cm.end(1))
                tail = blank[idx:]
                tags = _s_tags(sent)
                for m in _NUM.finditer(tail):
                    a, b = idx + m.start(), idx + m.end()
                    if cost_span and a >= cost_span[0] and b <= cost_span[1]:
                        continue
                    nxt = _NUM.search(tail, m.end())
                    end_ctx = idx + nxt.start() if nxt else len(sent)
                    ctx = sent[b:end_ctx]
                    pct = re.match(r"\s*\\?%", ctx)
                    printed = float(m.group(0))
                    if pct:
                        printed /= 100.0
                    tok_tol = m.group(0) + ("%" if pct else "")
                    # a "from s=A ... to s=B" span: every grid point in the
                    # range must equal the printed value
                    rg = _RANGE_CTX.search(ctx)
                    if rg:
                        lo, hi = float(rg.group(1)), float(rg.group(2))
                        for g in S_GRID:
                            if lo - 1e-9 <= g <= hi + 1e-9:
                                want, prov = exp["coverage_median"][(fam, g)]
                                seen += 1
                                _score(label, fails, passes, printed, want,
                                       _printed_tol(tok_tol),
                                       f"{fam} coverage @ s={g} (range)",
                                       prov, m.group(0))
                        continue
                    sval = _s_in_ctx(ctx)
                    if sval is None:
                        prev = [t for t in tags if t[0] < a]
                        if prev:
                            sval = prev[-1][1]
                    if sval is None:
                        continue
                    want, prov = exp["coverage_median"][(fam, sval)]
                    seen += 1
                    _score(label, fails, passes, printed, want,
                           _printed_tol(tok_tol), f"{fam} coverage @ s={sval}",
                           prov, m.group(0))

            # ---- coverage cost against the family's own saturation ---------
            cm = _COST_RE.search(blank)
            if cm and fam and re.search(r"saturat|饱和", sent, re.I) and (
                    s == 1.0 or re.search(r"as-placed\s+point|订单", sent, re.I)):
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

            # ---- retention (per-number family pairing, LaTeX \%) -----------
            rm_tok = re.search(r"retention", sent, re.I)
            if rm_tok:
                retain = exp["retention_pct"][0]
                for m in _NUM.finditer(blank, rm_tok.end()):
                    nxt = _NUM.search(blank, m.end())
                    ctx = sent[m.end():nxt.start() if nxt else len(sent)]
                    if not re.match(r"\s*\\?%", ctx):
                        continue
                    fam_r = _RET_FAM.search(ctx)
                    fam_i = (_RET_FAM_MAP[fam_r.group(1)] if fam_r else fam)
                    if fam_i is None or fam_i not in retain:
                        continue
                    want, prov = retain[fam_i]
                    seen += 1
                    _score(label, fails, passes, float(m.group(0)), want,
                           _printed_tol(m.group(0)), f"{fam_i} retention (%)",
                           prov, m.group(0))

            # ---- squint-loss factor (delivered caliber) --------------------
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

            # ---- fulfillment reading (three-part tag obligatory) -----------
            ful = re.search(r"fulfillment[-\s]?ratio|兑现率", sent, re.I)
            if ful and fam and s is not None:
                scored_any = False
                for m in _NUM.finditer(blank, ful.end()):
                    nxt = _NUM.search(blank, m.end())
                    ctx = sent[m.end():nxt.start() if nxt else len(sent)]
                    fm2 = _FUL_FAM.search(ctx)
                    fam_i = fm2.group(1).upper() if fm2 else fam
                    want, prov = exp["fulfillment_median"][(fam_i, s)]
                    seen += 1
                    if want is not None:
                        scored_any = True
                        _score(label, fails, passes, float(m.group(0)), want,
                               _printed_tol(m.group(0)),
                               f"{fam_i} fulfillment ratio @ s={s}",
                               prov, m.group(0))
                if scored_any:
                    missing = [n for n, rx in (
                        ("library convention", r"library[-\s]?(?:convention|caliber)|库口径"),
                        ("tie-set mean", r"tie[-\s]?set|全体成员"),
                        ("reading, not a target",
                         r"not\s+an?\s+(?:optimization|optimisation)\s+target|"
                         r"报告读数|非优化目标|不进目标"),
                    ) if not re.search(rx, line, re.I)]
                    if missing:
                        fails.append(f"{label}: fulfillment-ratio reading lacks "
                                     f"caliber element(s) {missing}  "
                                     f"[{line[:90]!r}]")

            # ---- tie-set records -------------------------------------------
            tm = re.search(r"(\d[\d,]*)\s+tie[-\s]?set\s+records", sent, re.I)
            if tm:
                printed = float(tm.group(1).replace(",", ""))
                want, prov = exp["tie_set_records"]
                seen += 1
                _score(label, fails, passes, printed, float(want),
                       _printed_tol(tm.group(1)), "tie-set records", prov,
                       tm.group(0))

            # ---- anchor-optimal units (X of [the] Y [sweep] units) ---------
            am = re.search(r"(\d+)\s+of\s+(?:the\s+)?(\d+)\s+(?:sweep\s+)?units",
                           sent, re.I)
            if am:
                want_a, prov_a = exp["anchor_optimal_units"]
                want_s, prov_s = exp["sweep_units"]
                seen += 1
                _score(label, fails, passes, float(am.group(1)), float(want_a),
                       _printed_tol(am.group(1)), "anchor-optimal units",
                       prov_a, am.group(0))
                seen += 1
                _score(label, fails, passes, float(am.group(2)), float(want_s),
                       _printed_tol(am.group(2)),
                       "sweep units (artifact census)", prov_s, am.group(0))
            for m in re.finditer(r"(\d+)\s+sweep\s+units", sent, re.I):
                if am and am.start() <= m.start() < am.end():
                    continue
                want, prov = exp["treatment_units"]
                seen += 1
                _score(label, fails, passes, float(m.group(1)), float(want),
                       _printed_tol(m.group(1)), "treatment sweep units",
                       prov, m.group(0))

            # ---- launched units --------------------------------------------
            lm = re.search(r"(\d+)\s+launched\s+units", sent, re.I)
            if lm:
                want, prov = exp["launched_units"]
                seen += 1
                _score(label, fails, passes, float(lm.group(1)), float(want),
                       _printed_tol(lm.group(1)), "launched units", prov,
                       lm.group(0))

            # ---- delivery-identity violation ceiling -----------------------
            vm = re.search(r"maximum[^;]{0,40}?over every record is\s+"
                           r"(\d+(?:\.\d+)?)", sent, re.I)
            if vm:
                want, prov = exp["delivery_cv_max"]
                seen += 1
                _score(label, fails, passes, float(vm.group(1)), float(want),
                       _printed_tol(vm.group(1)),
                       "delivery-identity violation ceiling", prov, vm.group(0))

            # ---- the two local declines (pp between two grid points) -------
            # Fail-loud: a dip sentence whose (family, s, s) key has no
            # registered reading must not be silently skipped -- that is
            # exactly the silent-green the phase-5 fix removes.
            fam_d = _fam_in_text(sent)
            for m in _DIP.finditer(sent):
                if fam_d is None:
                    continue
                key = (fam_d, float(m.group(2)), float(m.group(3)))
                if key not in exp["dip_pp"]:
                    fails.append(f"{label}: dip statement s={m.group(2)}->"
                                 f"{m.group(3)} for {fam_d} has no registered "
                                 f"reading  [{sent[:90]!r}]")
                    continue
                want, prov = exp["dip_pp"][key]
                seen += 1
                _score(label, fails, passes, float(m.group(1)), want,
                       _printed_tol(m.group(1)),
                       f"{fam_d} dip (pp) s={m.group(2)}->{m.group(3)}",
                       prov, m.group(0))

            # ---- per-seed movers (loses/gains between two grid points) -----
            bet = _BETWEEN.search(sent)
            moves_m = list(_MOVE.finditer(sent))
            # An identity claim the clause patterns cannot read is a fail, not
            # a pass: "and another seed loses 1.14" and "the same seed that
            # lost 1.83 ... gains 0.42" both used to slip through untouched
            # (2026-11-01 review; same escape shape R104 closed).
            _ident = _IDENT_VOCAB.search(sent)
            if (_ident and _MOVE_VERB.search(sent)
                    and not (_SAME_SEED.search(sent) or _DIFF_SEED.search(sent))):
                fails.append(f"{label}: seed-identity wording "
                             f"{_ident.group(0)!r} carrying a mover clause that "
                             f"neither identity pattern can read -- the claim "
                             f"would go unchecked  [{sent[:90]!r}]")
            if bet and moves_m:
                lo, hi = float(bet.group(1)), float(bet.group(2))
                cands = []
                for (f, a, b), (mv, _prov) in exp["per_seed_moves"].items():
                    if abs(a - lo) > 1e-9 or abs(b - hi) > 1e-9:
                        continue
                    bound = _moves_bind(moves_m, mv)
                    if bound:
                        cands.append((f, bound))
                if len(cands) == 1:
                    fam_m, bound = cands[0]
                    for m, seed, q in bound:
                        seen += 1
                        _score(label, fails, passes, float(m.group(1)), abs(q),
                               _printed_tol(m.group(1)),
                               f"{fam_m} per-seed move (pp) s={lo}->{hi} "
                               f"[seed {seed}]",
                               "per-seed s=a minus s=b, pp", m.group(0))
                    fails.extend(_seed_identity(sent, label, fam_m, lo, hi,
                                                bound, exp["per_seed_moves"]))
                else:
                    fails.append(f"{label}: per-seed move statement s={lo}->"
                                 f"{hi} matches {len(cands)} registered mover "
                                 f"set(s) -- unverifiable or ambiguous  "
                                 f"[{sent[:90]!r}]")
            elif bet and _MOVE_VERB.search(sent):
                # a between-grid sentence that DOES talk about a seed moving,
                # but whose clause the mover pattern could not read (measured
                # escape: the numbers wrapped in $...$ left moves_m empty and
                # the whole block was skipped -- no check, no fail)
                fails.append(f"{label}: 'between s={bet.group(1)} and s="
                             f"{bet.group(2)}' carries a loses/gains clause the "
                             f"mover pattern cannot read  [{sent[:90]!r}]")
            elif moves_m and re.search(r"\bseeds?\b|种子", sent, re.I):
                # a per-seed mover clause with no grid pair in the SAME
                # sentence: a period inserted before it splits the sentence and
                # the whole block silently vanished (2026-11-01 review measured
                # seen drop 73 -> 71 with rc=0).  The clause is unverifiable
                # here, so it must be loud.
                fails.append(f"{label}: per-seed mover clause with no "
                             f"'between s=A and s=B' in the same sentence -- "
                             f"the grid pair (and the seed registry it selects) "
                             f"cannot be resolved  [{sent[:90]!r}]")

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

            # ---- per-mode zero-squint resolutions (library constants) ------
            if "mode_floor_m" in exp:
                for mm in _MODE_FLOOR.finditer(sent):
                    mode, printed = mm.group(1), float(mm.group(2))
                    want = exp["mode_floor_m"][0][mode]
                    seen += 1
                    _score(label, fails, passes, printed, want,
                           _printed_tol(mm.group(2)),
                           f"{mode} zero-squint azimuth resolution (m)",
                           exp["mode_floor_m"][1], mm.group(0))

            # ---- per-mode library f_q constants + magnitude ratios (R50) --
            # Only the sentence that states the constants is checked, so the
            # "N (MODE)" shape elsewhere in the manuscript is not mistaken
            # for a capability reading.
            if "mode_fq_const" in exp and re.search(
                    r"per-?mode\s+constants?", sent, re.I):
                for mm in _MODE_FQ_CONST_RX.finditer(sent):
                    printed, mode = float(mm.group(1)), mm.group(2)
                    want = exp["mode_fq_const"][0][mode]
                    seen += 1
                    _score(label, fails, passes, printed, want,
                           max(_printed_tol(mm.group(1)), 1e-3),
                           f"{mode} zero-squint f_q constant (m^-2)",
                           exp["mode_fq_const"][1], mm.group(0))
                for mm in _MODE_FQ_RATIO_RX.finditer(sent):
                    printed = float(mm.group(1))
                    num, den = mm.group(2), mm.group(3)
                    want = exp["mode_fq_ratio"][0].get((num, den))
                    if want is None:
                        continue
                    seen += 1
                    _score(label, fails, passes, printed, want,
                           _printed_tol(mm.group(1)),
                           f"f_q magnitude ratio {num} over {den}",
                           exp["mode_fq_ratio"][1], mm.group(0))
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


_CENSUS_COLLECT: "list | None" = None
# scored readings whose printed token carries no decimal point (counts, integer
# percentages): they stay outside the census, and the run says how many.
_CENSUS_MISSES = 0


def strip_tex_comments(text: str) -> str:
    """Drop LaTeX comments: an escaped ``\\%`` is a sign, a bare ``%`` a comment.

    The census counts what the compiled paper prints.  Without this, commenting
    a sentence out left every literal count unchanged and the deletion
    invisible (2026-11-01 review; the R87 layout script had the same hole).
    """
    out = []
    for line in text.splitlines():
        cut, i = len(line), 0
        while True:
            j = line.find("%", i)
            if j < 0:
                break
            run, k = 0, j - 1
            while k >= 0 and line[k] == "\\":
                run, k = run + 1, k - 1
            if run % 2 == 0:      # even backslashes: a bare % starts a comment
                cut = j
                break
            i = j + 1
        out.append(line[:cut])
    return "\n".join(out)


def _census_literal(printed_raw: str, printed: float) -> "str | None":
    """The printed literal that carries the scored value, or None.

    Counting literals is only meaningful for READINGS: an integer in the match
    ("no feasible 2 of 10 units") is a count, not a reading, and census-counting
    a bare "2" would fire on every prose edit that reorders a list.  A
    percentage token scores as its fraction, so the /100 form is matched too.
    """
    toks = re.findall(r"\d+(?:\.\d+)?", printed_raw or "")
    for t in toks:
        if "." not in t:
            continue
        try:
            v = float(t)
        except ValueError:
            continue
        if abs(v - printed) <= 1e-9 or abs(v / 100.0 - printed) <= 1e-9:
            return t
    return None


def _score(label, fails, passes, printed, want, tol, what, prov, printed_raw):
    global _CENSUS_MISSES
    if _CENSUS_COLLECT is not None:
        lit = _census_literal(printed_raw, printed)
        if lit:
            _CENSUS_COLLECT.append(lit)
        elif "." in (printed_raw or ""):
            _CENSUS_MISSES += 1
    if want is None:
        fails.append(f"{label}: {what} has no registered L8 reading  [{prov}]")
        return
    delta = printed - float(want)
    if abs(delta) <= tol:
        passes.append(f"{label}: {what} = {printed}  [{prov}]")
    else:
        fails.append(f"{label}: manuscript {printed} vs recomputed {what}="
                     f"{want} (off by {delta:+.4g}, tol {tol})  [{prov}]")


def registered_values(exp: dict) -> "list[float]":
    """Every number the artifacts produce, minus the grid tags themselves.

    The grid values (0.8 … 2.0) are axis labels, not readings: counting their
    literals would make every ``s=0.8`` tag a census entry and fire on any
    grid edit.
    """
    vals: list = []

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, (list, tuple, set)):
            for v in o:
                walk(v)
        elif isinstance(o, (int, float)) and not isinstance(o, bool):
            vals.append(float(o))

    walk(exp)
    return [v for v in vals
            if not any(abs(v - g) <= 1e-12 for g in S_GRID)]


def census_literals(text: str, scored: "list[str]", registered: "list[float]",
                    strip_comments: bool = True) -> "list[str]":
    """Literals the census counts: what the gate scored, plus every printed
    number that is a correct rounding of a registered reading.

    The second half is what makes a reprint visible even when no anchored class
    reads it (2026-11-01 review: "26.0 percentage points" is printed twice and
    scored nowhere, so a scored-only census could not see it drift).
    """
    body = strip_tex_comments(text) if strip_comments else text
    lits = set(scored)
    for m in re.finditer(r"\d+\.\d+", body):
        tok = m.group(0)
        v = float(tok)
        if any(abs(v - g) <= 1e-12 for g in S_GRID):
            continue          # an s-axis tag, not a reading
        tol = _printed_tol(tok)
        if any(abs(v - r) <= tol for r in registered):
            lits.add(tok)
    return sorted(lits)


def census_counts(text: str, literals: "list[str]",
                  strip_comments: bool = True) -> dict:
    """literal -> how many times the COMPILED manuscript prints it.

    LaTeX comments are dropped first: a reading inside a commented-out
    sentence is not in the paper, so commenting one out must change its count.
    Only for .tex -- in the markdown face a bare "%" is a percent sign, and
    stripping there would cut every percentage reading off its line.
    """
    body = strip_tex_comments(text) if strip_comments else text
    out = {}
    for lit in sorted(set(literals)):
        rx = r"(?<![\d.])" + re.escape(lit) + r"(?![\d])"
        out[lit] = len(re.findall(rx, body))
    return out


def check_census(text: str, label: str, scored: "list[str]",
                 registry: dict, strip_comments: bool = True,
                 registered: "list[float] | None" = None) -> list:
    """Every scored reading literal must be printed the registered times.

    The sentence-anchored classes above score the occurrence they can see: a
    reading printed seven times (2.4669) was checked once, and an edit to any
    of the other six left the gate green (R106).  Matching each anchored
    class to every reprint is not available -- the reprints sit in sentences
    that carry no reading context -- but their COUNT is: a drifted, deleted
    or duplicated occurrence changes how many times the literal appears.  The
    census is frozen here on purpose, so the change lands in review as a diff
    rather than as a silent edit.

    A file with no census entry is a fail, not a skip: silence is exactly the
    loophole.  Synthetic fixtures opt out explicitly with L8_CENSUS_OPTIONAL=1.
    """
    fails: list = []
    name = Path(label).name
    known = registry.get("files", {}).get(name)
    cur = census_counts(text, census_literals(text, scored, registered or [],
                                               strip_comments),
                        strip_comments)
    if known is None:
        fails.append(f"{label}: no reading census registered for {name} -- the "
                     f"gate cannot tell whether a reading printed once is "
                     f"printed correctly elsewhere (review the text, then "
                     f"regenerate with --update-census)")
        return fails
    for lit, n in sorted(cur.items()):
        if lit not in known:
            fails.append(f"{label}: reading {lit} is printed but has no census "
                         f"entry ({CENSUS.name}) -- a new reading occurrence "
                         f"needs review, then --update-census")
        elif known[lit] != n:
            fails.append(f"{label}: reading {lit} is printed {n} time(s), the "
                         f"census registers {known[lit]} -- one occurrence was "
                         f"edited, added or removed (--update-census if that "
                         f"was intended)")
    for lit in sorted(set(known) - set(cur)):
        fails.append(f"{label}: the census registers {lit} ({known[lit]} "
                     f"occurrence(s)) but nothing prints it any more")
    return fails


def main(argv=None) -> int:
    global _CENSUS_COLLECT, _CENSUS_MISSES
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", action="append", default=None,
                    help="manuscript file(s) to check; omit for readings only")
    ap.add_argument("--update-census", action="store_true",
                    help="rewrite readings_census.json from the current "
                         "manuscript (review the text first: the census is "
                         "what makes a reprint invisible no more)")
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
    need_deliv = any(_DELIV_TOKEN.search(t) or re.search(r"squint[-\s]?loss", t,
                                                         re.I)
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
    census_reg = _load(CENSUS) if CENSUS.is_file() else {"files": {}}
    census_skipped: list = []
    registered_vals = registered_values(exp)
    census_new: dict = {"note": "Every literal the L8 core classes and T54 "
                                "score, and how many times the COMPILED "
                                "manuscript prints it (R106). An occurrence "
                                "that drifts, disappears or is duplicated "
                                "changes the count; regenerate with "
                                "--update-census after reviewing the text. "
                                "T55 / R56 / 16x / ignition readings are "
                                "outside this census (residual R110).",
                        "files": {}, "paths": {}}
    print("\n=== manuscript L8 numbers vs artifacts ===")
    from verify_r56_group import (R56_MIN_CHECKS, check_r56,
                                  r5_invariants, r56_expectations as _r56_exp)
    try:
        r56 = _r56_exp()  # R5 ambiguity re-evaluation + R6 intra-dwell bound
    except Exception as exc:  # artifacts moved under the registered readings
        print(f"ABORT: could not recompute the R5/R6 readings: {exc}", file=sys.stderr)
        return 2
    seen56_total = 0
    for p, text in texts.items():
        _CENSUS_COLLECT = []
        _CENSUS_MISSES = 0
        fails, passes, _notes, seen = check_paper(text, p.name, exp)
        t54 = t54_expectations(
            served_instances=exp["served_task_instances"][0],
            cost_r3h=abs(exp["coverage_cost_pp"]["R3H"][0]),
            cost_r2f=abs(exp["coverage_cost_pp"]["R2F"][0]))
        f54, p54, seen54 = check_t54(text, p.name, t54)
        # the census covers the core classes AND T54 (both score through this
        # module's funnels); T55 / R56 / 16x / ignition live in other modules
        # and are outside it -- stated in the census note, tracked as R110
        scored = list(_CENSUS_COLLECT)
        _CENSUS_COLLECT = None
        # T54 readings come from a separate expectation dict, so they must be
        # folded in here or their reprints stay outside the census
        reg_vals = registered_vals + registered_values(t54)
        fails += f54
        passes += p54
        seen += seen54
        from verify_t55_group import check_t55, t55_expectations as _t55_exp
        t55 = _t55_exp()
        f55, p55, seen55 = check_t55(text, p.name, t55)
        fails += f55
        passes += p55
        seen += seen55
        fb, pb, seenb = check_budget16x(
            text, p.name, V5 / "budget_check" / "budget_check.json")
        fails += fb
        passes += pb
        seen += seenb
        fi, pi, seeni = check_ignition_sentences(
            text, p.name,
            _load(V5 / "counterfactual_fd" / "counterfactual_summary.json"
                  )["conservative"],
            V5 / "anchor_free" / "anchor_free.json",
            _load(V5 / "anchor_free" / "probe16x" / "pilot_R3H_seed302.json"),
            _load(V5 / "budget_check" / "budget_check.json"))
        fails += fi
        passes += pi
        seen += seeni
        f56, p56, seen56 = check_r56(text, p.name, r56)
        fails += f56
        passes += p56
        seen += seen56
        seen56_total += seen56
        rev, _ = reverse_check(text, p.name)
        # --update-census wins over the fixture opt-out: an update run must
        # never be downgraded into a silent no-op that then wipes the file.
        if args.update_census:
            census_new["files"][p.name] = census_counts(
                text, census_literals(text, scored, reg_vals,
                                      p.suffix.lower() == ".tex"),
                p.suffix.lower() == ".tex")
            census_new.setdefault("paths", {})[p.name] = str(p.resolve())
            census_note = (f"census rewritten "
                           f"({len(census_new['files'][p.name])} literal(s))")
        elif os.environ.get("L8_CENSUS_OPTIONAL") == "1":
            census_note = "CENSUS SKIPPED (L8_CENSUS_OPTIONAL=1)"
            census_skipped.append(p.name)
        else:
            fc = check_census(text, p.name, scored, census_reg,
                               p.suffix.lower() == ".tex", reg_vals)
            fails += fc
            census_note = (f"{len(fc)} census mismatch(es)" if fc
                           else "census matches")
        if _CENSUS_MISSES:
            census_note += f"; {_CENSUS_MISSES} scored number(s) outside the " \
                           f"census (no decimal point)"
        all_fail += fails
        all_pass += passes
        reverse += rev
        total += seen
        print(f"  {p.name}: {seen} L8 number(s) checked ({seen54} T54, {seen55} T55, "
              f"{seen56} R56), "
              f"{len(fails)} mismatch(es), {len(rev)} retired-world token(s); "
              f"{census_note}")

    # Per-GROUP floor: the R5/R6 group is a late extension, and a whole-group
    # loss (its anchor reworded away, its module not imported) leaves the
    # manuscript total far above any global floor.  Guard it on its own.
    if (os.environ.get("L8_R56_OPTIONAL") != "1"
            and seen56_total < R56_MIN_CHECKS * len(texts)):
        print(f"ABORT: the R5/R6 group contributed {seen56_total} checks < "
              f"{R56_MIN_CHECKS * len(texts)} ({R56_MIN_CHECKS}/manuscript) -- "
              "the group stopped reading the manuscript")
        return 2
    # Model invariants ride along as FAILs (they are what makes the printed
    # direction claim true); they are not counted as manuscript checks.
    _inv_ok, inv_bad = r5_invariants(r56)
    all_fail += inv_bad

    _skip = (f"  [CENSUS SKIPPED: {', '.join(census_skipped)}]"
             if census_skipped else "")
    print(f"\n=== RESULT: {len(all_fail)} mismatch(es) over {total} checked ==="
          f"{_skip}")
    for f in all_fail:
        print(f"FAIL   {f}")

    # A regex that no longer matches silently drops its checks (seen never
    # increments), so a manuscript regression could turn the gate green by
    # shrinking the check surface.  Floor the check count at the last
    # registered level PER MANUSCRIPT (R83: 145, ignition sentences
    # 2026-10-25: 155) -- scaled by how many were passed, because the harness
    # and the mutation tests legitimately run one at a time.  The R5/R6 group
    # carries its own per-group floor above, which is what a global count
    # cannot see.  The unit tests override this via L8_MIN_CHECKED=0.
    MIN_CHECKED = int(os.environ.get("L8_MIN_CHECKED", "155")) * max(len(texts), 1)
    if total < MIN_CHECKED:
        print(f"ABORT: check surface shrank to {total} < {MIN_CHECKED} -- "
              "a gate regex stopped matching the manuscript (silent-drop "
              "guard, fullreview 2026-10-24)")
        return 2

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
    if args.update_census:
        if all_fail:
            print("REFUSED: the census is not rewritten while the gate has "
                  "mismatches -- fix the manuscript first")
            return 1
        merged = dict(census_reg.get("files", {}))
        merged_paths = dict(census_reg.get("paths", {}))
        blocked = [(name, merged_paths[name], path)
                   for name, path in census_new.get("paths", {}).items()
                   if merged_paths.get(name) and merged_paths[name] != path
                   and Path(merged_paths[name]).exists()]
        if blocked:
            print("REFUSED: these entries belong to a different file with the "
                  "same name -- updating from a copy would silently replace "
                  "the real registry")
            for name, old, new in blocked:
                print(f"  {name}: registered={old}  this run={new}")
            return 1
        if not census_new["files"]:
            print("REFUSED: this run scored no reading literal -- nothing to "
                  "write (a census of {} would erase the registry)")
            return 1
        merged.update(census_new["files"])
        merged_paths.update(census_new.get("paths", {}))
        out = {"note": census_new["note"], "files": merged,
               "paths": merged_paths}
        CENSUS.write_text(json.dumps(out, ensure_ascii=False, indent=1,
                                     sort_keys=True) + "\n", encoding="utf-8")
        print(f"census rewritten -> {CENSUS} "
              f"({sum(len(v) for v in merged.values())} literal(s) over "
              f"{len(merged)} file(s); {len(merged) - len(census_new['files'])} "
              f"entry(ies) kept from the previous run)")
    if all_fail:
        print("VERDICT: the manuscript contradicts the L8 artifacts")
        return 1
    print(f"VERDICT: every checked L8 number reproduces ({len(all_pass)} "
          "verified)")
    return 0




# --------------------------------------------------------------------------
# T54 registered readings (ticket 54, 2026-10-23): the external-review
# remediation added new registered numbers to the manuscript -- tightening
# drops, the fixed-dwell counterfactual, the maneuver-fallback replay, the
# mode-decomposition table (tab:modes), the family-size intervals and the
# distinct-task count.  Every expectation is RECOMPUTED from the artifacts;
# nothing below is a hardcoded truth value.
# --------------------------------------------------------------------------

def _t54_drop_pp(sweep: dict, fam: str, s_target: float) -> float:
    a = sweep["families"][fam]["1.0"]["coverage_median"]
    b = sweep["families"][fam][str(s_target)]["coverage_median"]
    return (a - b) * 100.0


def t54_expectations(served_instances: int | None = None,
                     cost_r3h: float | None = None,
                     cost_r2f: float | None = None) -> dict:
    """Recompute every T54 expectation from the artifacts."""
    exp: dict = {}
    sweep = _load(AGGREGATE)
    for fam in FAMILIES:
        for s_t in (0.8, 0.9):
            exp[("drop", fam, s_t)] = _t54_drop_pp(sweep, fam, s_t)
    # mode-decomposition table (bound) + observed medians, rounded as printed
    mode = _load(V5 / "mode_decomposition.json")
    for fam in FAMILIES:
        for s in S_GRID:
            row = mode["families"][fam]["rows"][str(s)]
            exp[("tab_bound", fam, s)] = round(row["upper_bound"], 3)
            exp[("tab_obs", fam, s)] = round(row["observed_median"], 3)
    # counterfactual (2026-10-25 user ruling: switched to the pure-plan
    # caliber -- before any repair; the old fields were the repair-traversal
    # caliber and under-read, since dropped tasks mask violating pairs)
    cf = _load(V5 / "counterfactual_fd" / "counterfactual_summary.json")
    for fam in FAMILIES:
        exp[("cf_gap", fam)] = cf[fam]["gap_pp_median"]
        exp[("cf_vp", fam)] = cf[fam]["violating_pairs_pure_total"]
        exp[("cf_ap", fam)] = cf[fam]["adjacent_pairs_pure_total"]
        exp[("cf_rate", fam)] = cf[fam]["violation_rate_pure_median"]
    repagg = _load(V5 / "counterfactual_fd" / "counterfactual_repairs_agg.json")
    _meds = [repagg[f]["median_gap_pp"][r] for f in ("R2F", "R3H")
             for r in ("drop_later", "priority_aware", "retime")]
    exp["cf_gap_span_lo"] = round(min(_meds))
    exp["cf_gap_span_hi"] = round(max(_meds))
    # fallback replay
    fb = _load(V5 / "maneuver_fallback_stats.json")
    exp["fb_pairs"] = fb["n_pairs"]
    exp["fb_pct"] = round(fb["model_below_bound_frac"] * 100)
    exp["fb_median"] = fb["model_median_s"]
    exp["fb_min"] = fb["model_min_s"]
    exp["fb_max"] = fb["model_max_s"]
    exp["fb_padded"] = fb["req_padded_dwell_s_median"]
    exp["fb_maneuver"] = fb["req_maneuver_s_median"]
    exp["fb_settle"] = fb["req_settle_s_median"]
    # family-size intervals over the ten seeds (R-15)
    import collections
    comp: dict = collections.defaultdict(lambda: collections.defaultdict(list))
    for fam, base in (("R1C", 100), ("R2F", 200), ("R3H", 300)):
        for seed in range(base, base + 10):
            man = _load(V5 / "scenarios" / f"{fam}_seed{seed}.json")
            tasks = man["tasks"]
            comp[fam]["drawn"].append(len(tasks))
            comp[fam]["admitted"].append(sum(1 for x in tasks if x.get("windows")))
            comp[fam]["windows"].append(sum(len(x["windows"]) for x in tasks))
    for fam in FAMILIES:
        for k in ("drawn", "admitted", "windows"):
            exp[("ival", fam, k)] = (min(comp[fam][k]), max(comp[fam][k]))
    # distinct served tasks over the best-covered members
    best_sel = 0
    for fam in FAMILIES:
        for s in S_GRID:
            d = V5 / "sweep" / ("s" + str(s).replace(".", "_"))
            for pilot_path in sorted(d.glob(f"pilot_{fam}_seed*.json")):
                pilot = _load(pilot_path)
                front = [m for m in pilot["front"] if m["cv"] <= 0.0] or pilot["front"]
                best = max(front, key=lambda m: m["f1_star"])
                best_sel += best["n_selected"]
    exp["distinct"] = best_sel
    exp["served_instances"] = served_instances
    exp["_cost_r3h"] = cost_r3h
    exp["_cost_r2f"] = cost_r2f
    mode_d = _load(V5 / "mode_decomposition.json")
    for s_t in (0.8, 0.9):
        ub = mode_d["families"]["R3H"]["rows"][str(s_t)]["upper_bound"]
        obs = mode_d["families"]["R3H"]["rows"][str(s_t)]["observed_median"]
        drp = _t54_drop_pp(_load(AGGREGATE), "R3H", s_t)
        exp[("_ub", s_t)] = ub
        exp[("_drop", s_t)] = drp
        exp[("_gaprem", s_t)] = (ub - obs) * 100.0
        exp[("_explained", s_t)] = drp - (ub - obs) * 100.0
    # R2F paired per-seed median between s=1.0 and its own saturation (s=2.0)
    pa, pb = [], []
    for seed in range(200, 210):
        a = _load(V5 / "sweep" / "s1_0" / f"pilot_R2F_seed{seed}.json")
        b = _load(V5 / "sweep" / "s2_0" / f"pilot_R2F_seed{seed}.json")
        fa = [m for m in a["front"] if m["cv"] <= 0.0] or a["front"]
        fb2 = [m for m in b["front"] if m["cv"] <= 0.0] or b["front"]
        pa.append(max(fa, key=lambda m: m["f1_star"])["f1_star"])
        pb.append(max(fb2, key=lambda m: m["f1_star"])["f1_star"])
    exp["pair_r2f_sat_pp"] = statistics.median(
        [b_ - a_ for a_, b_ in zip(pa, pb)]) * 100.0
    # R3H paired per-seed drop s=1.0 -> s=0.9 plus a seed-level bootstrap CI
    # for the median (post-hoc, added in the 2026-10-28 revision wave); RNG
    # seeded so gate recomputation is exact; B=10000 must match the prose
    import random as _random
    r3a, r3b = [], []
    for seed in range(300, 310):
        a = _load(V5 / "sweep" / "s1_0" / f"pilot_R3H_seed{seed}.json")
        b = _load(V5 / "sweep" / "s0_9" / f"pilot_R3H_seed{seed}.json")
        fa = [m for m in a["front"] if m["cv"] <= 0.0] or a["front"]
        fb3 = [m for m in b["front"] if m["cv"] <= 0.0] or b["front"]
        r3a.append(max(fa, key=lambda m: m["f1_star"])["f1_star"])
        r3b.append(max(fb3, key=lambda m: m["f1_star"])["f1_star"])
    r3_drops = [a_ - b_ for a_, b_ in zip(r3a, r3b)]
    exp["pair_r3h_drop_pp"] = statistics.median(r3_drops) * 100.0
    rng = _random.Random(20261028)
    boots = sorted(statistics.median(rng.choices(r3_drops, k=len(r3_drops)))
                   for _ in range(10000))
    exp["pair_r3h_ci"] = (boots[round(0.025 * 9999)] * 100.0,
                          boots[round(0.975 * 9999)] * 100.0)
    return exp


_T54_CHECKS = [
    # (pattern with CAPTURE groups, handler(m, t54) -> [(printed, want, tol, desc)])
    (re.compile(r"drops\s+(\d+(?:\.\d+)?)\s+percentage\s+points\s+for\s+R3H\s+and\s+(\d+(?:\.\d+)?)\s+for\s+R1C"),
     lambda m, e: [(float(m.group(1)), e[("drop", "R3H", 0.9)], 0.055, "R3H drop to s=0.9"),
                   (float(m.group(2)), e[("drop", "R1C", 0.9)], 0.055, "R1C drop to s=0.9")]),
    (re.compile(r"drops\s+(\d+(?:\.\d+)?)\s+percentage\s+points\s+from\s+the\s+as-placed"),
     lambda m, e: [(float(m.group(1)), e[("drop", "R3H", 0.9)], 0.055, "R3H drop to s=0.9")]),
    (re.compile(r"(\d+(?:\.\d+)?)\s+points\s+to\s+the\s+tightest\s+feasible\s+point"),
     lambda m, e: [(float(m.group(1)), e[("drop", "R3H", 0.8)], 0.055, "R3H drop to s=0.8")]),
    (re.compile(r"to\s+the\s+tightest\s+feasible\s+point\s+(\d+(?:\.\d+)?)\s+for\s+R3H"),
     lambda m, e: [(float(m.group(1)), e[("drop", "R3H", 0.8)], 0.055, "R3H drop to s=0.8")]),
    (re.compile(r"drops\s+(\d+(?:\.\d+)?)\s+points\s+at\s+\$s=0\.9\$"),
     lambda m, e: [(float(m.group(1)), e[("drop", "R1C", 0.9)], 0.055, "R1C drop to s=0.9")]),
    (re.compile(r"within\s+(\d+(?:\.\d+)?)\s+points"),
     lambda m, e: [(float(m.group(1)), e[("drop", "R2F", 0.9)], 0.011, "R2F tighter-side drop")]),
    (re.compile(r"(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)\s+percentage\s+points\s+\(family medians[^)]*\)"),
     lambda m, e: [(float(m.group(1)), e[("cf_gap", "R3H")], 0.011, "cf gap R3H median"),
                   (float(m.group(2)), e[("cf_gap", "R2F")], 0.011, "cf gap R2F median")]),
    (re.compile(r"(\d+)\s+of\s+(\d+)\s+pairs\s+for\s+the\s+100-task\s+family"),
     lambda m, e: [(int(m.group(1)), e[("cf_vp", "R3H")], 0, "cf violating pairs R3H"),
                   (int(m.group(2)), e[("cf_ap", "R3H")], 0, "cf adjacent pairs R3H")]),
    (re.compile(r"(\d+)\s+of\s+(\d+)\s+for\s+the\s+50-task\s+family"),
     lambda m, e: [(int(m.group(1)), e[("cf_vp", "R2F")], 0, "cf violating pairs R2F"),
                   (int(m.group(2)), e[("cf_ap", "R2F")], 0, "cf adjacent pairs R2F")]),
    (re.compile(r"violated in\s+(\d+)--(\d+)\\%\s+of\s+consecutive\s+pairs"),
     lambda m, e: [(int(m.group(1)), round(min(e[("cf_rate", f)] * 100 for f in ("R3H", "R2F"))), 0.5, "cf rate band lo"),
                   (int(m.group(2)), round(max(e[("cf_rate", f)] * 100 for f in ("R3H", "R2F"))), 0.5, "cf rate band hi")]),
    (re.compile(r"no violating pair in nine of ten seeds and a\s+(\d+(?:\.\d+)?)-point\s+median\s+gap"),
     lambda m, e: [(float(m.group(1)), e[("cf_gap", "R1C")], 1e-9, "cf gap R1C median")]),
    (re.compile(r"over the\s+(\d[\d,]*)\s+consecutive\s+pairs"),
     lambda m, e: [(int(m.group(1).replace(",", "")), e["fb_pairs"], 0, "fallback replay pairs")]),
    (re.compile(r"sits below the bound in\s+(\d+)\\%"),
     lambda m, e: [(int(m.group(1)), e["fb_pct"], 0, "fallback below-bound share")]),
    (re.compile(r"median\s+(\d+(?:\.\d+)?)~s,\s+range"),
     lambda m, e: [(float(m.group(1)), e["fb_median"], 0.0006, "fallback model median")]),
    (re.compile(r"range\s+(\d+(?:\.\d+)?)--(\d+(?:\.\d+)?)~s"),
     lambda m, e: [(float(m.group(1)), e["fb_min"], 0.0006, "fallback model min"),
                   (float(m.group(2)), e["fb_max"], 0.005, "fallback model max")]),
    (re.compile(r"(\d+(?:\.\d+)?)~s\s+of\s+pad-carrying\s+dwell,\s+(\d+(?:\.\d+)?)~s\s+of\s+charged\s+maneuver\s+time"),
     lambda m, e: [(float(m.group(1)), e["fb_padded"], 0.0006, "median padded dwell"),
                   (float(m.group(2)), e["fb_maneuver"], 0.0006, "median charged maneuver")]),
    (re.compile(r"against a \$([0-9.]+)\$~s measurement"),
     lambda m, e: [(float(m.group(1)), 1.84, 0, "fallback calibration anchor (sec7)")]),
    (re.compile(r"calibration anchor \(\$([0-9.]+)\$~s, Kim scenario~1\)"),
     lambda m, e: [(float(m.group(1)), 1.84, 0, "fallback calibration anchor (C2)")]),
    (re.compile(r"is charged the measured ([0-9.]+)~s fallback bound"),
     lambda m, e: [(float(m.group(1)), 4.07, 0, "fallback bound charge")]),
    (re.compile(r"serves\s+(\d[\d,]*)\s+distinct\s+tasks"),
     lambda m, e: [(int(m.group(1).replace(",", "")), e["distinct"], 0, "distinct served tasks")]),
    (re.compile(r"a\s+factor\s+of\s+(\d+(?:\.\d+)?)\s+below\s+the\s+instance\s+count"),
     lambda m, e: [(float(m.group(1)), round(477308.0 / e["distinct"], 1), 0.05, "distinct ratio")]),
    (re.compile(r"violates?\s+the\s+transfer\s+constraint\s+in\s+(\d+)--(\d+)\\%"),
     lambda m, e: [(int(m.group(1)), round(min(e[("cf_rate", f)] * 100 for f in ("R3H", "R2F"))), 0.5, "cf rate band lo"),
                   (int(m.group(2)), round(max(e[("cf_rate", f)] * 100 for f in ("R3H", "R2F"))), 0.5, "cf rate band hi")]),
    (re.compile(r"median\s+per-seed\s+rates\s+(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)"),
     lambda m, e: [(float(m.group(1)), round(min(e[("cf_rate", f)] * 100 for f in ("R3H", "R2F")), 1), 0.05, "cf per-seed median R3H-side"),
                   (float(m.group(2)), round(max(e[("cf_rate", f)] * 100 for f in ("R3H", "R2F")), 1), 0.05, "cf per-seed median R2F-side")]),
    (re.compile(r"lands?\s+(\d+)--(\d+)\s+points\s+below"),
     lambda m, e: [(int(m.group(1)), e["cf_gap_span_lo"], 0.5, "cf gap band lo"),
                   (int(m.group(2)), e["cf_gap_span_hi"], 0.5, "cf gap band hi")]),
    (re.compile(r"land\s+(\d+)--(\d+)\s+percentage\s+points\s+short"),
     lambda m, e: [(int(m.group(1)), e["cf_gap_span_lo"], 0.5, "cf gap band lo"),
                   (int(m.group(2)), e["cf_gap_span_hi"], 0.5, "cf gap band hi")]),
    (re.compile(r"recovers?\s+(\d+(?:\.\d+)?)\s+percentage\s+points\s+for\s+the\s+100-task\s+family"),
     lambda m, e: [(float(m.group(1)), abs(e["_cost_r3h"]), 0.055, "R3H as-placed cost (abstract/conclusion)")]),
    (re.compile(r"(\d+(?:\.\d+)?)\s+points\s+for\s+the\s+50-task\s+family"),
     lambda m, e: [(float(m.group(1)), abs(e["_cost_r2f"]), 0.055, "R2F as-placed cost (abstract/conclusion)")]),
    (re.compile(r"(\d+(?:\.\d+)?)\s+points\s+paired\s+per\s+seed"),
     lambda m, e: [(float(m.group(1)), round(e["pair_r2f_sat_pp"], 2), 0.005, "R2F paired per-seed median")]),
    (re.compile(r"caps\s+the\s+family\s+at\s+(\d+(?:\.\d+)?)\s+at\s+\$s=0\.9\$\s+and\s+(\d+(?:\.\d+)?)\s+at\s+\$s=0\.8\$"),
     lambda m, e: [(float(m.group(1)), round(e["_ub", 0.9], 3), 0.0006, "floor bound s=0.9"),
                   (float(m.group(2)), round(e["_ub", 0.8], 3), 0.0006, "floor bound s=0.8")]),
    (re.compile(r"accounts\s+for\s+(\d+(?:\.\d+)?)\s+of\s+the\s+(\d+(?:\.\d+)?)-point\s+drop\s+to\s+\$s=0\.9\$"),
     lambda m, e: [(float(m.group(1)), round(e["_explained", 0.9], 2), 0.006, "floor-explained s=0.9"),
                   (float(m.group(2)), round(e["_drop", 0.9], 2), 0.006, "observed drop s=0.9")]),
    (re.compile(r"(\d+(?:\.\d+)?)\s+of\s+the\s+(\d+(?:\.\d+)?)-point\s+drop\s+to\s+\$s=0\.8\$"),
     lambda m, e: [(float(m.group(1)), round(e["_explained", 0.8], 2), 0.006, "floor-explained s=0.8"),
                   (float(m.group(2)), round(e["_drop", 0.8], 2), 0.006, "observed drop s=0.8")]),
    (re.compile(r"residual\s+gap[^;]*?\((\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)\s+points\)"),
     lambda m, e: [(float(m.group(1)), round(e["_gaprem", 0.9], 1), 0.051, "residual gap s=0.9"),
                   (float(m.group(2)), round(e["_gaprem", 0.8], 1), 0.051, "residual gap s=0.8")]),
    (re.compile(r"drop\s+to\s+\$s=0\.8\$\s+is\s+(\d+(?:\.\d+)?)\s+percentage\s+points"),
     lambda m, e: [(float(m.group(1)), e[("drop", "R3H", 0.8)], 0.055, "fig caption drop")]),
    (re.compile(r"the\s+(\d+(?:\.\d+)?)~s\s+settle"),
     lambda m, e: [(float(m.group(1)), e["fb_settle"], 0.005, "settle term")]),
    (re.compile(r"bootstrap of those ten paired R3H drops \(10,000 resamples, "
                r"computed for this revision\) puts a 95\\?% confidence "
                r"interval for the median at (\d+(?:\.\d+)?)--(\d+(?:\.\d+)?)"),
     lambda m, e: [(float(m.group(1)), round(e["pair_r3h_ci"][0], 1), 0.051,
                    "R3H paired bootstrap CI lo"),
                   (float(m.group(2)), round(e["pair_r3h_ci"][1], 1), 0.051,
                    "R3H paired bootstrap CI hi")]),
    (re.compile(r"Attribution of the (\d+(?:\.\d+)?)-point as-placed residual "
                r"is left as future work"),
     lambda m, e: [(float(m.group(1)), round(abs(e["_cost_r3h"]), 2), 0.055,
                    "R3H as-placed residual (future-work sentence)")]),
]

_TAB_ROW = re.compile(
    r"^(" + "|".join(str(s).replace(".", "\.") for s in S_GRID) + r")\s*&"
    r"\s*([\d.]+)\s*&\s*([\d.]+|---)\s*&\s*([\d.]+)\s*&\s*([\d.]+)"
    r"\s*&\s*([\d.]+)\s*&\s*([\d.]+)\s*\\\\$")

_IVAL_ANCHORS = []  # (superseded: capture-based interval check below)


def check_t54(text: str, label: str, t54: dict) -> "tuple[list, list, int]":
    fails: list = []
    passes: list = []
    seen = 0

    def score(ok: bool, printed: str, want: str, desc: str) -> None:
        nonlocal seen
        seen += 1
        if _CENSUS_COLLECT is not None:
            cm = re.match(r"\d+(?:\.\d+)?", printed or "")
            if cm and "." in cm.group(0):
                _CENSUS_COLLECT.append(cm.group(0))
        if ok:
            passes.append(f"{label}: {desc}")
        else:
            fails.append(f"{label}: T54 {desc} -- printed {printed} vs recomputed {want}")

    for line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", line)
        if not line.strip():
            continue
        for rx, handler in _T54_CHECKS:
            m = rx.search(line)
            if not m:
                continue
            for printed, want, tol, desc in handler(m, t54):
                seen += 1
                ok = abs(printed - want) <= tol
                if ok:
                    passes.append(f"{label}: T54 {desc}")
                else:
                    fails.append(f"{label}: T54 {desc} -- printed {printed} "
                                 f"vs recomputed {want}")

        tm = _TAB_ROW.match(line.strip())
        if tm:
            s_val = float(tm.group(1))
            vals = [tm.group(n) for n in (2, 3, 4, 5, 6, 7)]

            def _obs(fam, sv, printed):
                return "---" if printed == "---" else t54[("tab_obs", fam, sv)]

            expect = [t54[("tab_bound", "R1C", s_val)], _obs("R1C", s_val, vals[1]),
                      t54[("tab_bound", "R2F", s_val)], _obs("R2F", s_val, vals[3]),
                      t54[("tab_bound", "R3H", s_val)], _obs("R3H", s_val, vals[5])]
            got = [v if v == "---" else float(v) for v in vals]
            seen += 1
            ok = all((gv == "---" and ev == "---")
                     or (gv != "---" and ev != "---" and abs(gv - ev) <= 5e-4)
                     for gv, ev in zip(got, expect))
            if ok:
                passes.append(f"{label}: T54 tab:modes row s={s_val}")
            else:
                fails.append(f"{label}: T54 tab:modes row s={s_val} -- "
                             f"printed {got} vs recomputed {expect}")
        for fam in FAMILIES:
            for k in ("admitted", "windows"):
                m2 = re.search(
                    fam + r"[^;]*?(\d+)--(\d+)\s+" + k, line)
                if not m2:
                    continue
                lo, hi = t54[("ival", fam, k)]
                got = (int(m2.group(1)), int(m2.group(2)))
                seen += 1
                if got == (lo, hi):
                    passes.append(f"{label}: T54 {fam} {k} interval")
                else:
                    fails.append(f"{label}: T54 {fam} {k} interval -- printed "
                                 f"{got} vs recomputed {(lo, hi)}")
    return fails, passes, seen


# --- ticket 62 ignition arm 3.2 (R87-04): the 16x budget-check sentences ----
# The s=0.9 sentence predates this check and its 0.6884 was NOT covered by
# any gate surface (mutation 0.6884->0.6885 stayed green, 2026-10-25); the
# as-placed sentence is new in the same wave.  Both medians are recomputed
# from experiments/v5_results/budget_check/budget_check.json -- a MISSING
# sentence is a FAIL (the reading is registered, it may not silently
# disappear), and a beats-anchor artifact invalidates both sentences.
def check_budget16x(text: str, label: str, budget_path: Path):
    fails: list = []
    passes: list = []
    seen = 0
    rows = json.loads(budget_path.read_text(encoding="utf-8"))
    ok = [r for r in rows if "rc" not in r]
    for s, rx, desc in (
        (0.9, re.compile(r"at \$s=0\.9\$ the mixed family's ten re-run units "
                         r"keep the median exactly at ([0-9.]+)"),
         "16x median s=0.9 (R3H)"),
        (1.0, re.compile(r"ten re-run units at \$s=1\.0\$ hold the median at "
                         r"exactly ([0-9.]+)"),
         "16x median s=1.0 (R3H, as-placed)"),
    ):
        units = [r for r in ok if r["family"] == "R3H" and r["s"] == s]
        want = statistics.median(r["max_f1_star_on_front"] for r in units)
        beats = [r for r in units if r.get("search_beats_anchor")]
        if beats:
            fails.append(f"{label}: B16X artifact invalid for s={s} -- "
                         f"{len(beats)}/{len(units)} units beat the anchor; "
                         "both manuscript sentences are falsified")
            continue
        m = rx.search(text)
        # synthetic unit-test manuscripts legitimately carry no 16x sentence;
        # they opt out via L8_B16X_OPTIONAL=1 (same pattern as L8_MIN_CHECKED)
        # -- absent then skips the check entirely (no seen, no pass) so the
        # zero-extraction exit-2 contract of those fixtures is untouched.
        # The real manuscript never sets it, so a dropped sentence stays a FAIL.
        if not m and os.environ.get("L8_B16X_OPTIONAL") == "1":
            continue
        seen += 1
        if not m:
            fails.append(f"{label}: B16X {desc} -- sentence MISSING from "
                         "manuscript (registered reading, silent drop)")
        elif m.group(1) != f"{want:.4f}":
            # string equality on the 4-decimal print: a 5e-4 numeric
            # tolerance swallowed the last-digit mutation probe (2026-10-25)
            fails.append(f"{label}: B16X {desc} -- printed {m.group(1)} "
                         f"vs recomputed {want:.4f}")
        else:
            passes.append(f"{label}: B16X {desc}")
    return fails, passes, seen


# --- ticket 62 ignition sentences (user-approved 2026-10-25): the
# conservative fixed-dwell sentence (sec:counterfactual) and the anchor-free
# sentence (sec:dip).  Every number is recomputed from the artifacts; a
# missing sentence is a FAIL, same silent-drop semantics as B16X.
def check_ignition_sentences(text: str, label: str, cons_summary: dict,
                             anchor_free_path: Path, probe_pilot: dict,
                             budget_rows: list):
    fails: list = []
    passes: list = []
    seen = 0

    def need(m, desc, ok, printed, want):
        nonlocal seen
        # Synthetic unit-test fixtures carry no ignition sentences; they opt
        # out via L8_B16X_OPTIONAL=1 exactly like B16X (absent then skips the
        # check entirely -- no seen, no pass).  The real manuscript never sets
        # it, so a dropped sentence stays a FAIL.
        if not m and os.environ.get("L8_B16X_OPTIONAL") == "1":
            return
        seen += 1
        if not m:
            fails.append(f"{label}: IGN {desc} -- sentence fragment MISSING")
        elif not ok:
            fails.append(f"{label}: IGN {desc} -- printed {printed} "
                         f"vs recomputed {want}")
        else:
            passes.append(f"{label}: IGN {desc}")

    # conservative sentence: medians, pairs, per-seed ranges
    r2f, r3h = cons_summary["R2F"], cons_summary["R3H"]
    m = re.search(r"serves\s+a\s+median\s+(\d+(?:\.\d+)?)\s+and\s+"
                  r"(\d+(?:\.\d+)?)\s+points\s+less", text)
    want_lo = round(r2f["gap_pp_median"], 1)
    want_hi = round(r3h["gap_pp_median"], 1)
    need(m, "conservative gap medians", bool(m) and
         (round(float(m.group(1)), 1), round(float(m.group(2)), 1))
         == (want_lo, want_hi),
         (m.group(1), m.group(2)) if m else None, (want_lo, want_hi))
    m = re.search(r"among\s+the\s+(\d+)\s+and\s+(\d+)\s+consecutive\s+pairs",
                  text)
    want_pairs = (r2f["adjacent_pairs_pure_total"],
                  r3h["adjacent_pairs_pure_total"])
    pure_zero = (r2f["violating_pairs_pure_total"] == 0
                 and r3h["violating_pairs_pure_total"] == 0)
    need(m, "conservative pair counts (zero-violation precondition)",
         bool(m) and pure_zero
         and (int(m.group(1)), int(m.group(2))) == want_pairs,
         (m.group(1), m.group(2)) if m else None, want_pairs)

    # anchor-free sentence: rc cells, feasible cells, 16x probe gap
    af = json.loads(anchor_free_path.read_text(encoding="utf-8"))
    rc_cells = [r for r in af if "rc" in r]
    ok_cells = [r for r in af if "rc" not in r]
    m = re.search(r"no\s+feasible\s+individual\s+on\s+(\d+)\s+of\s+the\s+(\d+)\s+re-run\s+cells",
                  text)
    need(m, "anchor-free rc-cell count", bool(m)
         and int(m.group(1)) == len(rc_cells)
         and int(m.group(2)) == len(rc_cells) + len(ok_cells)
         and all(r["family"] == "R3H" for r in rc_cells),
         (m.group(1), m.group(2)) if m else None,
         (len(rc_cells), len(rc_cells) + len(ok_cells)))
    m = re.search(r"any\s+of\s+the\s+(\d+)\s+feasible\s+cells", text)
    need(m, "anchor-free feasible-cell count", bool(m)
         and int(m.group(1)) == len(ok_cells),
         m.group(1) if m else None, len(ok_cells))
    m = re.search(r"recovers\s+a\s+front\s+still\s+(\d+(?:\.\d+)?)\s+points\s+below\s+the\s+anchor",
                  text)
    anchor_arm = [r for r in budget_rows
                  if r["family"] == "R3H" and r["seed"] == 302
                  and r["s"] == 0.9][0]
    # like-for-like: the probe runs at s=0.9, so the comparison anchor is the
    # anchor arm's s=0.9 seed-302 construction (0.5936), NOT the s=1.0 one
    want_gap = round((anchor_arm["anchor_f1_star"]
                      - probe_pilot["max_f1_star_on_front"]) * 100, 1)
    need(m, "anchor-free 16x probe gap", bool(m)
         and float(m.group(1)) == want_gap,
         m.group(1) if m else None, want_gap)
    return fails, passes, seen


if __name__ == "__main__":
    sys.exit(main())
