"""NSGA-II assembly runner (ticket 10): pymoo NSGA2 over the evaluator.

Determinism convention (D10-8): pymoo==0.6.1.6 pinned, a fixed ``seed``
per run, PYTHONHASHSEED=0 in the process environment, single thread, and
manifest task-list order for every float accumulation.

Exit codes (D11, distinguishing -- never fake success):
  0  front produced (|front| >= 1, all CV == 0)
 10  scenario has zero served tasks (nothing to schedule)
 11  run completed but no feasible individual survived (empty front)
  2  usage / setup error
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import Problem
from pymoo.optimize import minimize
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling

from .aasr import aasr_direct
from .evaluator import SchedulingProblem, decode_tau
from .geometry import squint_at
from .modes import Mode

# D12-3 preregistered promotion threshold; derivation chain registered in
# experiments/promotion_prereg.json (6.0 = 2x the sensitivity half-band of
# the -10/-14 dB alternates = 6x the 1.0 dB cell margin = 5x the margin
# plus the <=0.2 dB halving sub-sample excess; arithmetic corrected from
# the original ">= 6x (1.0 + 0.2)" wording 2026-09-29, ticket 13 --
# 6*1.2 = 7.2 > 6.0 was false as registered; threshold value unchanged)
PROMOTION_SPREAD_DB = 6.0
from .modes import ModeLibrary

PYMOO_PINNED = "0.6.1.6"

# CV dust tolerance (ticket 14, 2026-09-29): BELT ONLY.  The primary fix
# is the C2_TOL_S source floor in evaluator.py (boundary-exact anchor
# starts carry a C2 deficit up to 1e-12 s; the unfloored positive part
# produced CV dust ~1e-14, which pymoo's INTERNAL strict CV==0
# feasibility filter treated as infeasible -- emptying the W/H result
# front -- and which crashed the strict construction assert below).
# Tolerance chain (single registration): evaluator C2_TOL_S 1e-12
# (source floor, mirrored by anchor fits) / encode round-trip 1e-9 /
# these consumer belts 1e-9.  Genuine violations are ~seconds, orders of
# magnitude above the belt (anti-fixture: a seed shifted 1.0 s into a
# C2 conflict stays red).
CV_DUST_TOL = 1e-9


class SchedulingProblemPymoo(Problem):
    """pymoo adapter: 2N decision vector, two minimized objectives
    (-f1*, -f_q: BOTH quality axes are maximized), one aggregated CV from
    the evaluator's violation sum."""

    def __init__(self, problem: SchedulingProblem):
        self.sp = problem
        n = problem.n
        super().__init__(
            n_var=2 * n,
            n_obj=2,
            n_constr=1,
            xl=np.zeros(2 * n),
            xu=np.ones(2 * n),
        )

    def _evaluate(self, X, out, *args, **kwargs):
        f = np.empty((X.shape[0], 2))
        g = np.empty((X.shape[0], 1))
        for p in range(X.shape[0]):
            ev = self.sp.evaluate(X[p])
            f[p, 0] = -ev["f1_star"]  # maximize coverage
            f[p, 1] = -ev["f_q"]  # maximize delivered quality (finer = larger f_q)
            g[p, 0] = ev["cv"]
        out["F"] = f
        out["G"] = g


@dataclass
class PilotResult:
    front: list[dict]
    n_evaluations: int
    seed: int
    all_cv_zero: bool
    anchor_seeded: bool = False
    anchor_f1_star: float | None = None
    search_only_max_f1_star: float | None = None  # D12-2 info field
    promotion_spread_db: float | None = None
    promotion_decision: str | None = None


def encode_seed_individual(sp: SchedulingProblem, starts: dict[int, float]) -> list[float]:
    """Inverse of the piecewise decode for a full schedule (D12-1): tau =
    (cumulated measure before the interval + offset) / total measure.
    Round-trips through decode_tau with a 1e-9 tolerance (fail-loud on the
    cumulative-boundary float edge)."""
    x = [0.0] * (2 * sp.n)
    for i, start in starts.items():
        plan = sp.plans[i]
        x[i] = 1.0
        intervals = list(plan.intervals)
        cum = 0.0
        total = sum(hi - lo for lo, hi in intervals)
        for lo, hi in intervals:
            if lo - 1e-12 <= start <= hi + 1e-12:
                tau = (cum + (start - lo)) / total
                break
            cum += hi - lo
        else:
            raise ValueError(f"anchor start {start} outside task {i} feasible set")
        x[sp.n + i] = min(max(tau, 0.0), 1.0)
        # round-trip guard (D12-1)
        back = decode_tau(x[sp.n + i], plan.intervals)
        assert abs(back - start) <= 1e-9, (i, start, back)
    return x


def promotion_spread_db(sp: SchedulingProblem, front_records: list[dict]) -> dict:
    """Unenforced AASR spread over the front candidates (D12-3): per
    candidate, the max direct AASR over its selected tasks (per-task scene
    extent for SPT, D08-2); spread = max - min across candidates.
    Threshold and derivation chain live in experiments/promotion_prereg.json.

    Ticket 17: two defects, both measured.  The squint here was computed with
    the LIBRARY R0 (fifth instance of the caliber split), and an SLS task
    whose per-task geometry places the start outside the sliding domain made
    ``aasr_direct`` RAISE -- killing the unit mid-solve rather than yielding a
    reading.  A promotion readout is by definition an UNENFORCED measurement
    (D12-3), so an out-of-domain sample is recorded as +inf dB (infinitely bad
    AASR), which keeps the spread meaningful and the unit alive.
    """
    vals = []
    for rec in front_records:
        cand_max = None
        for i_str, start in rec["starts"].items():
            plan = sp.plans[int(i_str)]
            psi = squint_at(start, plan.t_ca_s, sp.lib.geo, r0_m=plan.r0_m)
            try:
                db = aasr_direct(
                    plan.mode, psi, sp.lib.geo.k, plan.prf_hz, sp.lib,
                    spt_scene_wa_m=(
                        plan.azimuth_size_m if plan.mode is Mode.SPT else None
                    ),
                    r0_m=plan.r0_m,
                )["aasr_db"]
            except ValueError:
                # unenforced readout outside the physical sliding domain:
                # infinitely bad AASR, not a crash (D12-3 semantics)
                db = float("inf")
            cand_max = db if cand_max is None else max(cand_max, db)
        if cand_max is not None:
            vals.append(cand_max)
    # A candidate whose AASR left the physical sliding domain is +inf (see
    # above).  Letting that flow into the spread would make inf >= 6.0 read as
    # "promote" -- the OPPOSITE of the intent, since an infinitely bad
    # unenforced AASR is not a reason to add a third objective.  Those
    # candidates are excluded from the spread and reported separately, so the
    # decision stays a statement about finite, comparable readings.
    finite = [v for v in vals if math.isfinite(v)]
    n_infinite = len(vals) - len(finite)
    spread = (max(finite) - min(finite)) if len(finite) >= 2 else 0.0
    from sss_core.aasr import AASR_THRESHOLD_DB
    decision = "promote" if spread >= PROMOTION_SPREAD_DB else "no_promotion"
    if n_infinite:
        decision = f"{decision} (excluded {n_infinite} out-of-domain candidate(s))"
    return {
        "per_candidate_max_db": vals,
        "spread_db": spread,
        "decision": decision,
        "threshold_db": PROMOTION_SPREAD_DB,
        "note": f"threshold -13 dB context; spread vs preregistered {PROMOTION_SPREAD_DB} dB",
        "_threshold_ref": AASR_THRESHOLD_DB,
    }


def run_nsga2(
    manifest: dict,
    lib: ModeLibrary,
    seed: int,
    pop_size: int = 40,
    generations: int = 60,
    seed_individual: list[float] | None = None,
    anchor_f1_star: float | None = None,
) -> PilotResult:
    """One deterministic NSGA-II run over a scenario manifest.

    ``seed_individual`` (D12-1/2): an anchor-encoded vector placed as row 0
    of the initial population (pymoo accepts an array sampling); its CV==0
    and f1* >= anchor are ASSERTED at construction (fail-loud dual check).
    """
    sp = SchedulingProblem(manifest, lib)
    sampling = FloatRandomSampling()
    if seed_individual is not None:
        rng = np.random.default_rng(seed)
        X = rng.random((pop_size, 2 * sp.n))
        X[0] = np.array(seed_individual)
        # dual check (D12-1): the seed must be feasible and cover the anchor
        ev = sp.evaluate(X[0])
        assert ev["cv"] <= CV_DUST_TOL, f"seed individual CV={ev['cv']}"
        if anchor_f1_star is not None:
            assert ev["f1_star"] >= anchor_f1_star - 1e-9, (
                ev["f1_star"], anchor_f1_star
            )
        sampling = X
    algorithm = NSGA2(
        pop_size=pop_size,
        sampling=sampling,
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(eta=20),
        eliminate_duplicates=True,
    )
    res = minimize(
        SchedulingProblemPymoo(sp),
        algorithm,
        ("n_gen", generations),
        seed=seed,
        verbose=False,
    )
    front = []
    if res.F is not None:
        for k in range(len(res.F)):
            x = res.X[k]
            rec = decode_solution(sp, x)
            front.append(
                {
                    "f1_star": float(-res.F[k, 0]),
                    "f_q": float(-res.F[k, 1]),
                    "cv": float(res.CV[k, 0]) if res.CV is not None else rec["cv"],
                    "n_selected": rec["n_selected"],
                    "starts": {str(i): float(s) for i, s in rec["starts"].items()},
                }
            )
    all_zero = all(r["cv"] <= CV_DUST_TOL for r in front) if front else False
    promo = promotion_spread_db(sp, front)
    anchor_f1 = anchor_f1_star
    search_only = None
    if anchor_f1 is not None and front:
        others = [r["f1_star"] for r in front if r["f1_star"] < anchor_f1 - 1e-9]
        search_only = max(others) if others else None
    return PilotResult(
        front=front,
        n_evaluations=pop_size * generations,
        seed=seed,
        all_cv_zero=all_zero,
        anchor_seeded=seed_individual is not None,
        anchor_f1_star=anchor_f1,
        search_only_max_f1_star=search_only,
        promotion_spread_db=promo["spread_db"],
        promotion_decision=promo["decision"],
    )


def load_manifest(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def decode_solution(sp: SchedulingProblem, x):  # re-export shim (site 2)
    from .evaluator import decode_solution as _ds

    return _ds(sp, x)
