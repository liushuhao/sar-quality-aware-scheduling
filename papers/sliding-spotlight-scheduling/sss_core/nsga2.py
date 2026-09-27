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
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import Problem
from pymoo.optimize import minimize
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling

from .evaluator import SchedulingProblem
from .modes import ModeLibrary

PYMOO_PINNED = "0.6.1.6"


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


def run_nsga2(
    manifest: dict,
    lib: ModeLibrary,
    seed: int,
    pop_size: int = 40,
    generations: int = 60,
) -> PilotResult:
    """One deterministic NSGA-II run over a scenario manifest."""
    sp = SchedulingProblem(manifest, lib)
    algorithm = NSGA2(
        pop_size=pop_size,
        sampling=FloatRandomSampling(),
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
            rec = sp.decode_solution(x) if hasattr(sp, "decode_solution") else decode_solution(sp, x)
            front.append(
                {
                    "f1_star": float(-res.F[k, 0]),
                    "f_q": float(-res.F[k, 1]),
                    "cv": float(res.CV[k, 0]) if res.CV is not None else rec["cv"],
                    "n_selected": rec["n_selected"],
                    "starts": {str(i): float(s) for i, s in rec["starts"].items()},
                }
            )
    all_zero = all(r["cv"] == 0.0 for r in front) if front else False
    return PilotResult(front=front, n_evaluations=pop_size * generations, seed=seed,
                       all_cv_zero=all_zero)


def load_manifest(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def decode_solution(sp: SchedulingProblem, x):  # re-export shim (site 2)
    from .evaluator import decode_solution as _ds

    return _ds(sp, x)
