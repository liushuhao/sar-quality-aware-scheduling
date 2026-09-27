"""Scheduler assembly: dual-objective NSGA-II over a scenario manifest.

Ticket 10 (T0 seam).  Algorithm decision D10-1: pymoo NSGA2 (0.6.1.6,
pinned) with a self-contained 2N Problem -- ZERO shared-library copies
(the Paper-1 ``moea.py`` is a three-objective NSGA-III with fixed-duration
physics; no symbol is reusable, and pymoo is an external dependency that
does not touch the FORK_MANIFEST copy clauses -- see its ticket-10
zero-copy record).  Encoding: x in [0,1]^(2N), x[:N] selection genes
(> 0.5 selects), x[N:2N] tau genes -- SAME structure as Paper 1
(``moea.py:107-116``), DIFFERENT decode semantics (piecewise projection
below, not the linear ``t_earliest + tau*time_span``).

DECODE-SITE INVENTORY (D10-4; the fork-domain registry that replaces the
Paper-1 four-site list -- moea.py:128/:412/:679 and so_f1.py:84/:243 are
design references only, never copied):
  1. ``SchedulingProblem.evaluate``             (in-evaluation decode)
  2. ``decode_solution``                        (post-hoc schedule decode)
  3. ``decode_tau``                             (the single primitive 1 & 2 call)
A source-scan guard (tests) bans any OTHER linear-tau decode pattern in
sss_core; adding a fourth site without routing it through ``decode_tau``
is the exact silent-drift failure mode Paper 1 suffered.

D10-2 non-convex sampling: decode-time projection -- tau genes range over
[0,1] freely and are projected onto the precompiled feasible union by
measure-preserving walk; geometric window feasibility therefore holds BY
CONSTRUCTION and the violation vector collects ONLY the coupled
predicates (C2 transfer, C3, C4, schedule conflict) plus unschedulable
selections and empty selections.  Rejected alternatives: repair operators
(extra randomness breaks determinism) and f1 penalties (duplicate CV).

D10-3 contracts: ``decode_tau`` RAISES on an empty/zero-measure interval
set (callers convert that to a per-task CV violation); the runner
distinguishes exit codes per D11 -- 0 success, 10 zero-served scenario,
11 empty front, 2 usage.

Objectives (pymoo minimizes): (-f1*, -f_q) -- f1* = selected priority sum
over all served priorities; f_Q = the ticket-05 MEAN aggregate over the
selected set (time-invariant per D05-4, so it depends only on the
selected subset; |front| >= 1 is the promised assertion, no more).  An
empty selection is a CV violation with placeholder objectives (never
NaN -- the D05-8 raise is intercepted here first).

C2 conservatism note (D10-6): the per-pair maneuver uses the fallback
envelope 4.07 s; consecutive-pair enforcement is SUFFICIENT for pairwise
non-overlap because sorting by start makes requirement_i >= dur_i, so
satisfying every adjacent gap keeps all pairs gap-safe.  C3/C4 are
evaluated but slack by construction inside the squint envelope (their
normalized values cannot exceed 1.0 there) -- the binding violation
channels are C2, conflicts and empty/unschedulable selections.

Run convention (D10-8): pymoo==0.6.1.6, PYTHONHASHSEED=0, single thread,
manifest task-list order everywhere (no set/dict iteration order may
reach a float sum).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .duration import MarginPads, duration_scene_s, pad_window_tail
from .geometry import squint_at
from .maneuver import boundary_rate
from .modes import Mode, ModeLibrary
from .predicates import (
    c2_transfer_ok,
    c2_transfer_requirement_s,
    c3_ok,
    c4_ok,
    schedule_conflict,
)
from .quality import f_q_aggregate, f_q_per_task
from .windows import feasible_subintervals

EMPTY_SELECTION_FQ_PLACEHOLDER = 1.0  # worst normalized-quality stand-in


def decode_tau(tau: float, intervals) -> float:
    """Project tau in [0,1] onto the feasible union by measure walk (D10-2).

    Half-open stepping with a last-interval clamp: tau = 1.0 lands exactly
    on the final hi (no epsilon flake at the boundary).  Raises on an
    empty/zero-measure set -- the caller converts that to a CV violation
    (per task) or a D11 exit (per scenario); silence is forbidden.
    """
    intervals = list(intervals)
    measures = [hi - lo for lo, hi in intervals]
    total = sum(measures)
    if total <= 0.0:
        raise ValueError("decode_tau on an empty/zero-measure feasible set")
    s = tau * total
    last = len(intervals) - 1
    for j, ((lo, hi), w) in enumerate(zip(intervals, measures)):
        if s < w or j == last:
            return lo + min(s, w)
        s -= w
    raise AssertionError("unreachable")  # pragma: no cover


@dataclass
class TaskPlan:
    """Per-task precompilation consumed by evaluation (fixed at setup)."""

    index: int
    priority: int
    rho_req_m: float
    mode: Mode
    prf_hz: float
    t_ca_s: float
    azimuth_size_m: float
    intervals: tuple | None  # None = unschedulable (empty feasible set)
    priority_f: float

    @property
    def schedulable(self) -> bool:
        return self.intervals is not None


def precompile_tasks(manifest: dict, lib: ModeLibrary) -> list[TaskPlan]:
    """Precompile per-task feasible subintervals with the manifest's OWN
    window-tail pad (D04-2/D10-8 single source: manifest pads)."""
    pads = MarginPads(
        float(manifest["preregistration"]["pads"]["inter_task_fraction"]),
        float(manifest["preregistration"]["pads"]["window_tail_fraction"]),
    )
    plans = []
    for i, t in enumerate(manifest["tasks"]):
        mode = Mode[t["mode"]]  # manifests store the enum NAME (STR/SLS/SPT)
        t0, t1 = float(t["t_start_s"]), float(t["t_end_s"])
        t_ca = float(t["t_ca_s"])

        def duration(t, _mode=mode, _tca=t_ca):
            return pad_window_tail(
                duration_scene_s(_mode, squint_at(t, _tca, lib.geo), lib), pads
            )

        try:
            fw = feasible_subintervals(duration, t0, t1)
            intervals = tuple(fw.intervals) if fw else None
        except ValueError:
            intervals = None
        plans.append(
            TaskPlan(
                index=i,
                priority=int(t["priority"]),
                rho_req_m=float(t["rho_req_m"]),
                mode=mode,
                prf_hz=float(t["prf_hz"]),
                t_ca_s=t_ca,
                azimuth_size_m=float(t["azimuth_size_m"]),
                intervals=intervals,
                priority_f=float(t["priority"]),
            )
        )
    return plans



class SchedulingProblem:
    """2N Problem evaluation (selection + tau) against the predicates.

    Violation vector (all >= 0, summed into the pymoo CV):
      * selected an unschedulable task (+1 each)
      * empty selection (+1, placeholder objectives)
      * C2 transfer gaps between consecutive selected tasks (positive part)
      * schedule conflicts between any selected consecutive pair (safety net)
      * C3/C4 evaluated per selected task (slack by construction, D10-6)
    """

    def __init__(self, manifest: dict, lib: ModeLibrary):
        self.manifest = manifest
        self.lib = lib
        self.plans = precompile_tasks(manifest, lib)
        self.n = len(self.plans)
        self.pads = MarginPads(
            float(manifest["preregistration"]["pads"]["inter_task_fraction"]),
            float(manifest["preregistration"]["pads"]["window_tail_fraction"]),
        )
        self.total_priority = sum(p.priority_f for p in self.plans)

    # ── decode (site 1) ──────────────────────────────────────────────
    def decode_starts(self, x) -> dict[int, float]:
        """tau -> start time for SELECTED schedulable tasks:
        {plan_index: start}.  Selection of an unschedulable task is not a
        decode error -- it is counted as a violation in ``evaluate``."""
        starts: dict[int, float] = {}
        for i, plan in enumerate(self.plans):
            if x[i] <= 0.5:
                continue
            if not plan.schedulable:
                continue
            starts[i] = decode_tau(x[self.n + i], plan.intervals)
        return starts

    def _dwell(self, i: int, start: float) -> float:
        plan = self.plans[i]
        return duration_scene_s(
            plan.mode, squint_at(start, plan.t_ca_s, self.lib.geo), self.lib
        )

    # ── evaluate ─────────────────────────────────────────────────────
    def evaluate(self, x) -> dict:
        violations = 0.0
        starts = self.decode_starts(x)
        # C2/conflict chains iterate in START-TIME order (index order is NOT
        # time order -- the anchor-seed cross-check of ticket 12 exposed this
        # as spurious violations on time-inverted index pairs)
        order = sorted(starts, key=lambda i: starts[i])
        for i, plan in enumerate(self.plans):
            if x[i] > 0.5 and not plan.schedulable:
                violations += 1.0
        if not order:
            return {
                "f1_star": 0.0,
                "f_q": EMPTY_SELECTION_FQ_PLACEHOLDER,
                "cv": violations + 1.0,
                "starts": {},
                "n_selected": 0,
            }

        for a, b in zip(order, order[1:]):
            pa, pb = self.plans[a], self.plans[b]
            psi_a = squint_at(starts[a], pa.t_ca_s, self.lib.geo)
            psi_b = squint_at(starts[b], pb.t_ca_s, self.lib.geo)
            req = c2_transfer_requirement_s(
                self._dwell(a, starts[a]),
                self.lib,
                self.pads,
                d_psi_rad=abs(psi_b - psi_a),
                omega_start=boundary_rate(pa.mode, psi_a, self.lib),
                omega_end=boundary_rate(pb.mode, psi_b, self.lib),
            )
            gap = starts[b] - starts[a]
            violations += max(0.0, req["requirement_s"] - gap)
            if schedule_conflict(starts[a], self._dwell(a, starts[a]), starts[b], self._dwell(b, starts[b])):
                violations += 1.0
        for i in order:
            plan = self.plans[i]
            if not c3_ok(plan.mode, self._dwell(i, starts[i]), self.lib):
                violations += 1.0
            if not c4_ok(plan.mode, self._dwell(i, starts[i]), plan.rho_req_m, plan.prf_hz, self.lib):
                violations += 1.0

        f1 = sum(self.plans[i].priority_f for i in order) / max(self.total_priority, 1e-12)
        f_q = f_q_aggregate(
            [
                f_q_per_task(
                    self.plans[i].mode,
                    squint_at(starts[i], self.plans[i].t_ca_s, self.lib.geo),
                    self.lib.geo.R0_m,
                    self.lib,
                )
                for i in order
            ]
        )
        return {
            "f1_star": f1,
            "f_q": f_q,
            "cv": violations,
            "starts": starts,
            "n_selected": len(order),
        }

    def c2_uses_predicate_source(self) -> bool:
        """Identity guard hook (D09-6/D10-8): the C2 requirement comes from
        the ticket-09 predicate module, never a local copy."""
        return c2_transfer_ok.__module__ == "sss_core.predicates"


def decode_solution(problem: SchedulingProblem, x) -> dict:
    """Post-hoc decode (site 2): full schedule record for one decision
    vector -- MUST agree with evaluate's site-1 decode (guard-tested)."""
    ev = problem.evaluate(x)
    return {
        "f1_star": ev["f1_star"],
        "f_q": ev["f_q"],
        "cv": ev["cv"],
        "n_selected": ev["n_selected"],
        "starts": {i: s for i, s in sorted(ev["starts"].items())},
    }
