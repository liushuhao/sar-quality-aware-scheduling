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
            mv = sorted((pa[seed] - pb[seed]) * 100.0
                        for seed in sorted(set(pa) & set(pb))
                        if abs(pa[seed] - pb[seed]) > 1e-12)
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
_MOVE = re.compile(r"\b(?:loses?|gains?)\s+(\d+(?:\.\d+)?)", re.IGNORECASE)
_DIP = re.compile(r"(\d+(?:\.\d+)?)\s+(?:pp|percentage\s+points)\s+between\s+"
                  r"\$?s\s*=\s*(\d(?:\.\d)?)\$?\s+and\s+\$?s\s*=\s*"
                  r"(\d(?:\.\d)?)\$?", re.IGNORECASE)
_MODE_FLOOR = re.compile(r"rho_\{a,\\mathrm\{(STR|SLS|SPT)\}\}[^;]{0,60}?"
                         r"(\d+(?:\.\d+)?)\s*\$?\s*~?m", re.IGNORECASE)


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
    return 1.0                      # "订单原要求" / "order point" == s=1.0


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
            if fam and re.search(r"coverage|覆盖", sent, re.I):
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
                        ("library caliber", r"library[-\s]?caliber|库口径"),
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
            if bet and moves_m:
                lo, hi = float(bet.group(1)), float(bet.group(2))
                printed_moves = [float(m.group(1)) for m in moves_m]
                cands = []
                for (f, a, b), (mv, _prov) in exp["per_seed_moves"].items():
                    if (abs(a - lo) > 1e-9 or abs(b - hi) > 1e-9
                            or len(mv) != len(printed_moves)):
                        continue
                    # the paper prints magnitudes; the registered moves are
                    # signed (positive = the seed lost coverage)
                    if all(any(abs(p - abs(q)) <= _printed_tol(m.group(1))
                               for q in mv)
                           for p, m in zip(printed_moves, moves_m)):
                        cands.append((f, mv))
                if len(cands) == 1:
                    fam_m, mv = cands[0]
                    for p, m in zip(printed_moves, moves_m):
                        near = min(mv, key=lambda q: abs(p - abs(q)))
                        seen += 1
                        _score(label, fails, passes, p, abs(near),
                               _printed_tol(m.group(1)),
                               f"{fam_m} per-seed move (pp) s={lo}->{hi}",
                               "per-seed s=a minus s=b, pp", m.group(0))
                else:
                    fails.append(f"{label}: per-seed move statement s={lo}->"
                                 f"{hi} matches {len(cands)} registered mover "
                                 f"set(s) -- unverifiable or ambiguous  "
                                 f"[{sent[:90]!r}]")

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
