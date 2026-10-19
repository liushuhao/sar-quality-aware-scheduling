"""Scheduler assembly: single-objective NSGA-II over a scenario manifest
(ticket 48: coverage f1* is the one objective; f_Q survives only as a
descriptive reading -- see nsga2.PROMOTION_VOID_SINGLE_OBJECTIVE).

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

Objective (pymoo minimizes): (-f1*) -- f1* = selected priority sum
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
from .windows import feasible_subintervals, resolution_clip

EMPTY_SELECTION_FQ_PLACEHOLDER = 1.0  # worst normalized-quality stand-in

# C2 gap tolerance (ticket 14, 2026-09-29): the greedy anchor's fits()
# admits gap >= need - C2_TOL_S, so boundary-exact anchor starts can carry
# a C2 deficit of up to 1e-12 s.  Without the floor below the positive
# part turns that into CV dust (~1e-14 after float round-trips), which
# pymoo's INTERNAL feasibility filter treats as infeasible (strict CV==0
# on the optimal-set extraction) -- emptying the result front on W/H
# bands.  The floor zeroes sub-picosecond deficits (physically
# meaningless; genuine violations are ~seconds), making boundary-exact
# seeds cv EXACTLY 0.0.  Tolerance chain (single registration): anchor
# fits 1e-12 (this constant) / encode round-trip 1e-9 / nsga2 consumer
# belt CV_DUST_TOL 1e-9.
C2_TOL_S = 1e-12


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


@dataclass(frozen=True)
class TaskWindow:
    """One transit window of a task (ticket 25, AD-3).

    ``lo``/``hi`` are the window bounds in manifest time; ``t_ca_s`` is THIS
    window's ``squint_at`` zero -- each enumerated transit has its own zero,
    and reusing one zero across passes mis-derives dwell / envelope / AASR
    (the defect AD-3 closes).  ``r0_m`` / ``incidence_deg`` are this pass's
    geometry.  ``intervals`` holds the end-check-feasible subintervals
    within ``[lo, hi]``, filled at precompile (never re-derived elsewhere).
    """

    lo: float
    hi: float
    t_ca_s: float
    r0_m: float | None = None
    incidence_deg: float | None = None
    intervals: tuple[tuple[float, float], ...] = ()


@dataclass
class TaskPlan:
    """Per-task precompilation consumed by evaluation (fixed at setup).

    Ticket 16 adds the per-task geometry block: ``r0_m`` / ``incidence_deg``
    are None for every pre-ticket-16 family (their manifests carry no
    geometry), which is what keeps the frozen result families bit-identical.

    Ticket 25 (AD-3): the window structure is a LIST of :class:`TaskWindow`
    (one per enumerated transit).  ``t_ca_at(t)`` returns the zero of the
    window CONTAINING t -- closed-interval convention (``lo <= t <= hi``):
    ``decode_tau`` at tau=1 lands exactly on ``hi`` (D04-1 closed feasibility),
    so a half-open match would pick the wrong window at the boundary.
    A manifest without a ``windows`` field is the synthetic single-window
    family: one TaskWindow spans ``[t_start_s, t_end_s]`` and every lookup
    returns the stored scalar, keeping those manifests byte-identical.
    """

    index: int
    priority: int
    rho_req_m: float | None  # None = manifest carries no order (pre-ticket-25)
    mode: Mode
    prf_hz: float
    azimuth_size_m: float
    intervals: tuple | None  # None = unschedulable (empty feasible set)
    priority_f: float
    windows: tuple[TaskWindow, ...] = ()
    r0_m: float | None = None
    incidence_deg: float | None = None
    vector_squint_min_t_s: float | None = None

    def __post_init__(self):
        # AD-3 invariant, asserted not assumed: window INTERIORS never
        # overlap (pass spacing is hours; a single pass window is minutes).
        # Touching endpoints are allowed (two in-band flanks of one pass can
        # meet at the band edge -- a zero-measure boundary); ``window_at``
        # resolves that case deterministically by first match.
        ordered = sorted(self.windows, key=lambda w: w.lo)
        for a, b in zip(ordered, ordered[1:]):
            if a.hi > b.lo:
                raise ValueError(
                    f"task {self.index}: windows overlap "
                    f"([{a.lo}, {a.hi}] vs [{b.lo}, {b.hi}])"
                )

    @property
    def schedulable(self) -> bool:
        return self.intervals is not None

    def window_at(self, t: float) -> TaskWindow:
        """The window containing t (closed interval, first match)."""
        for w in self.windows:
            if w.lo <= t <= w.hi:
                return w
        raise ValueError(
            f"t={t} outside every window of task {self.index} "
            f"({[w.lo for w in self.windows]}..{[w.hi for w in self.windows]})"
        )

    def window_nearest(self, t: float) -> TaskWindow:
        """Nearest window by distance (0 if inside).  ONLY for heuristic
        estimates at times that are not yet committed to a window -- the
        anchor's repair-candidate generator.  Every committed evaluation
        path must use ``window_at`` (fail-loud), never this."""
        return min(
            self.windows,
            key=lambda w: max(w.lo - t, t - w.hi, 0.0),
        )

    def t_ca_at(self, t: float) -> float:
        """The squint zero of the window containing t (stored value,
        never recomputed)."""
        return self.window_at(t).t_ca_s


def precompile_tasks(
    manifest: dict, lib: ModeLibrary, freeze_durations: bool = False
) -> list[TaskPlan]:
    """Precompile per-task feasible subintervals with the manifest's OWN
    window-tail pad (D04-2/D10-8 single source: manifest pads).

    Ticket 16: a task may carry its own geometry block (``r0_m`` /
    ``incidence_deg`` / ``vector_squint_min_t_s``).  Absent block -> the
    library constants, which is every pre-ticket-16 manifest, so those stay
    bit-identical.

    Ticket 25 (AD-3): a task may carry a ``windows`` list (one entry per
    enumerated transit: ``lo_s``/``hi_s``/``t_ca_s``/``r0_m``/
    ``incidence_deg``).  Each window gets its OWN duration closure (its own
    squint zero and its own slant range) and its own end-check; the flattened
    feasible union is rebuilt in the manifest's window order (``decode_tau``
    measure-walk unchanged).  A task without ``windows`` is the synthetic
    single-window family: one TaskWindow spans ``[t_start_s, t_end_s]`` taken
    DIRECTLY from the manifest (never re-derived from ``t_ca`` + half-width),
    and the single-window semantics (empty feasible set -> ``intervals=None``,
    i.e. unschedulable) are preserved bit-for-bit.
    """
    pads = MarginPads(
        float(manifest["preregistration"]["pads"]["inter_task_fraction"]),
        float(manifest["preregistration"]["pads"]["window_tail_fraction"]),
    )
    plans = []
    for i, t in enumerate(manifest["tasks"]):
        mode = Mode[t["mode"]]  # manifests store the enum NAME (STR/SLS/SPT)
        # per-task geometry (ticket 16); absent on every pre-ticket-16 manifest
        r0_t = float(t["r0_m"]) if t.get("r0_m") is not None else None
        inc_t = (
            float(t["incidence_deg"])
            if t.get("incidence_deg") is not None else None
        )
        vsq_t = (
            float(t["vector_squint_min_t_s"])
            if t.get("vector_squint_min_t_s") is not None else None
        )

        if "windows" in t:
            specs = [
                (
                    float(w["lo_s"]),
                    float(w["hi_s"]),
                    float(w["t_ca_s"]),
                    float(w["r0_m"]) if w.get("r0_m") is not None else None,
                    (
                        float(w["incidence_deg"])
                        if w.get("incidence_deg") is not None else None
                    ),
                )
                for w in t["windows"]
            ]
        else:
            # synthetic / pre-ticket-25 single window: fields straight from
            # the manifest, so the frozen families see identical floats
            specs = [(
                float(t["t_start_s"]), float(t["t_end_s"]),
                float(t["t_ca_s"]), r0_t, inc_t,
            )]

        windows: list[TaskWindow] = []
        any_feasible = False
        for lo, hi, t_ca, w_r0, w_inc in specs:

            def duration(t, _mode=mode, _tca=t_ca, _r0=w_r0):
                _squint = (
                    0.0 if freeze_durations
                    else squint_at(t, _tca, lib.geo, r0_m=_r0)
                )
                return pad_window_tail(
                    duration_scene_s(_mode, _squint, lib, r0_m=_r0),
                    pads,
                )

            try:
                fw = feasible_subintervals(duration, lo, hi)
                ivs = tuple(fw.intervals) if fw else ()
            except ValueError:
                ivs = ()
            # ticket 48: the ordered resolution must hold where the task is
            # actually shot, not only at zero squint.  Manifests without
            # rho_req_m (pre-ticket families) skip the clip bit-for-bit.
            if ivs and t.get("rho_req_m") is not None:
                ivs = resolution_clip(
                    ivs, mode, float(t["rho_req_m"]), t_ca, w_r0, lib
                )
            # truthiness matches FeasibleWindows.__bool__ exactly: an
            # all-degenerate feasible set is NOT schedulable (decode_tau
            # cannot walk a zero-measure union) -- this is what keeps a
            # single-window manifest's None-vs-() semantics unchanged
            any_feasible = any_feasible or any(hi_iv > lo_iv for lo_iv, hi_iv in ivs)
            windows.append(
                TaskWindow(
                    lo=lo, hi=hi, t_ca_s=t_ca, r0_m=w_r0, incidence_deg=w_inc,
                    intervals=ivs,
                )
            )
        intervals = (
            tuple(iv for w in windows for iv in w.intervals)
            if any_feasible else None
        )
        plans.append(
            TaskPlan(
                index=i,
                priority=int(t["priority"]),
                # ticket 48 fix: the clip guard above keys on .get(), but this
                # constructor read the key unconditionally -- a pre-ticket-25
                # manifest would have KeyError'd HERE, after the clip skip, so
                # the commit-message promise ("no-field manifests skip
                # bit-for-bit") was false end-to-end.  None flows through; the
                # C4 consumer's rho parameter is a registered interface-stability
                # slot (D09-4, deleted inside the predicate), so None is inert.
                rho_req_m=(
                    float(t["rho_req_m"])
                    if t.get("rho_req_m") is not None else None
                ),
                mode=mode,
                prf_hz=float(t["prf_hz"]),
                azimuth_size_m=float(t["azimuth_size_m"]),
                intervals=intervals,
                priority_f=float(t["priority"]),
                windows=tuple(windows),
                r0_m=r0_t,
                incidence_deg=inc_t,
                vector_squint_min_t_s=vsq_t,
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

    def __init__(
        self, manifest: dict, lib: ModeLibrary, freeze_durations: bool = False
    ):
        self.manifest = manifest
        self.lib = lib
        self.freeze_durations = freeze_durations
        self.plans = precompile_tasks(manifest, lib, freeze_durations)
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
        w = plan.window_at(start)
        squint = (
            0.0 if self.freeze_durations
            else squint_at(start, w.t_ca_s, self.lib.geo, r0_m=w.r0_m)
        )
        return duration_scene_s(
            plan.mode,
            squint,
            self.lib,
            r0_m=w.r0_m,
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
            w_a = pa.window_at(starts[a])
            w_b = pb.window_at(starts[b])
            psi_a = squint_at(starts[a], w_a.t_ca_s, self.lib.geo, r0_m=w_a.r0_m)
            psi_b = squint_at(starts[b], w_b.t_ca_s, self.lib.geo, r0_m=w_b.r0_m)
            req = c2_transfer_requirement_s(
                self._dwell(a, starts[a]),
                self.lib,
                self.pads,
                d_psi_rad=abs(psi_b - psi_a),
                omega_start=boundary_rate(pa.mode, psi_a, self.lib, r0_m=w_a.r0_m),
                omega_end=boundary_rate(pb.mode, psi_b, self.lib, r0_m=w_b.r0_m),
            )
            gap = starts[b] - starts[a]
            violations += max(0.0, req["requirement_s"] - gap - C2_TOL_S)
            if schedule_conflict(starts[a], self._dwell(a, starts[a]), starts[b], self._dwell(b, starts[b])):
                violations += 1.0
        for i in order:
            plan = self.plans[i]
            # ticket 28: same caliber as the dwell (per-window r0) -- the dwell
            # is measured at the geometry of the window the start falls in
            # (``_dwell`` -> ``w.r0_m``), so the C3/C4 reference must be
            # evaluated there too (predicates._t_env_max, ticket 17).  On the
            # schema-2.1 real-window family the task-level block is absent, so
            # quoting ``plan.r0_m`` silently fell back to the library constant.
            w = plan.window_at(starts[i])
            if not c3_ok(
                plan.mode, self._dwell(i, starts[i]), self.lib,
                r0_m=w.r0_m,
            ):
                violations += 1.0
            if not c4_ok(
                plan.mode, self._dwell(i, starts[i]), plan.rho_req_m,
                plan.prf_hz, self.lib, r0_m=w.r0_m,
            ):
                violations += 1.0

        f1 = sum(self.plans[i].priority_f for i in order) / max(self.total_priority, 1e-12)
        f_q_terms = []
        for i in order:
            w_i = self.plans[i].window_at(starts[i])
            f_q_terms.append(
                f_q_per_task(
                    self.plans[i].mode,
                    squint_at(starts[i], w_i.t_ca_s, self.lib.geo, r0_m=w_i.r0_m),
                    # per-window slant range (ticket 25); None -> library constant
                    self.lib.geo.R0_m if w_i.r0_m is None else w_i.r0_m,
                    self.lib,
                )
            )
        f_q = f_q_aggregate(f_q_terms)
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
