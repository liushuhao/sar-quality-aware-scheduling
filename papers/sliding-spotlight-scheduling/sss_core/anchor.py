"""Greedy anchor for f1* normalization (spec D8, ticket 11).

Priority-descending single-pass earliest-feasible insertion over the
precompiled feasible subwindows, with blocker-driven re-timing repair.

D11-1 (gate-review FAIL fix): the ticket's original "removal backtracking"
is UNREACHABLE dead code under priority-descending insertion -- every
blocker of a failing task has strictly higher priority, and only
strictly-lower-priority placed tasks were eligible for removal, so no
removal could ever flip a failure into a success.  The spec-D8 motivation
("repair may not converge when delay increases T") is dissolved
STRUCTURALLY here: the precompiled subwindows turn repair into a bounded
single-step candidate scan (each candidate is C2-checked against its
insertion neighbours before acceptance -- no repair cascade exists).
The ticket's red/green "backtracking" pair is carried verbatim by the
re-timing repair ON/OFF flag.  (Spec-owner note returned with the ticket;
editing spec D8 wording is a user-level change.)

D11-2/3 equivalence/redden pair: freezing T to its zero-squint value (one
wrapper point, D11-8: precompilation + C2 dwell + repair candidates all
consume it) must leave the M1NC anchor's served set and f1* EXACTLY equal
with starts within tolerance (brentq subwindow roots shift by ~ms), while
on the wide mixed scenario the starts must MOVE with real >= frozen
pointwise -- the red half.

D11-5 setup check: the maneuver fallback is armed at the scenario's
maximal pointing change (single-axis model < 0.5 x measured Kim RMT), so
the C2 requirement is candidate-exact; should the fallback ever disarm,
candidates become approximate but the final C2 check stays exact
(feasible, possibly not earliest).

D11-6: C2 checks cover the insertion point's predecessor and successor
only (sorted starts make adjacent-pair satisfaction sufficient for all
pairs -- evaluator D10-6); candidate lists are deduplicated then SORTED
(no set iteration order reaches the float path).  The need assembly goes
EXCLUSIVELY through the ticket-09 predicate (D11-7 -- no local
re-assembly of maneuver+settle).

Audit amendment (ticket 13, 2026-09-29, independent review + directed
fix review): every candidate -- left edges AND repair candidates -- must
lie inside the task's feasible subintervals (membership gate in the
acceptance loop, same 1e-12 tol as the seed encoder).  Without it a
fallback-regime repair candidate (constant need) is accepted OUTSIDE the
window span: repro A(pri10, win[0,40], t_ca=3) + B(pri5, win[0,6],
t_ca=3), pads=0 -> B placed at 7.373 s vs feasible [0, 4.697], f1*
overstated 1.0 vs true 2/3.  Model-regime needs vary with the evaluation
position and rejected such candidates incidentally; the fallback regime
removed that protection.  Blast radius measured by the fix reviewer:
M1NC/M2WF/M2WH anchors bit-identical pre/post; M3NC loses 5 out-of-window
starts (f1* 0.2475 -> 0.2345, the old value was inflated) and the M4WH
anchor previously CRASHED at encode (sec2 singularity on an out-of-set
start) -- both strictly improved, no existing artifact pins either.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .duration import MarginPads, duration_scene_s
from .evaluator import TaskPlan, precompile_tasks
from .geometry import squint_at
from .maneuver import FALLBACK_MANEUVER_S, calibrate_against_kim
from .modes import Mode, ModeLibrary
from .predicates import c2_transfer_requirement_s


@dataclass
class AnchorResult:
    starts: dict[int, float]          # plan_index -> scheduled start
    f1_star: float
    total_priority: float
    served_priority: float
    unserved: list[int]


def _need_between(
    dur_i: float,
    d_psi_rad: float,
    omega_i: float,
    omega_j: float,
    lib: ModeLibrary,
    pads: MarginPads,
) -> float:
    """C2 gap requirement, assembled ONLY through the ticket-09 predicate
    (D11-7)."""
    return c2_transfer_requirement_s(
        dur_i, lib, pads,
        d_psi_rad=d_psi_rad, omega_start=omega_i, omega_end=omega_j,
    )["requirement_s"]


def greedy_anchor(
    manifest: dict,
    lib: ModeLibrary,
    repair: bool = True,
    freeze_durations: bool = False,
) -> AnchorResult:
    """Priority-descending earliest-feasible insertion anchor.

    ``repair=False`` restricts candidates to the subwindow left edges (the
    red variant of the ticket's backtracking pair).  ``freeze_durations``
    replaces the squint-dependent dwell by its zero-squint value at EVERY
    consumption point (D11-8 single wrapper: precompilation, C2 dwell,
    repair candidates).
    """
    pads = MarginPads(
        float(manifest["preregistration"]["pads"]["inter_task_fraction"]),
        float(manifest["preregistration"]["pads"]["window_tail_fraction"]),
    )

    def dwell_at(plan: TaskPlan, t: float) -> float:
        if freeze_durations:
            return duration_scene_s(plan.mode, 0.0, lib)
        return duration_scene_s(plan.mode, squint_at(t, plan.t_ca_s, lib.geo), lib)

    # precompile with the SAME frozen-dwell wrapper (D11-8 scope)
    if freeze_durations:
        plans = _precompile_frozen(manifest, lib, pads)
    else:
        plans = precompile_tasks(manifest, lib)

    order = sorted(
        range(len(plans)),
        key=lambda i: (-plans[i].priority, float(manifest["tasks"][i]["t_start_s"]), i),
    )

    starts: dict[int, float] = {}

    def fits(cand: float, plan: TaskPlan) -> bool:
        if not starts:
            return True
        times = sorted(starts.items(), key=lambda kv: kv[1])
        psi_self = squint_at(cand, plan.t_ca_s, lib.geo)
        dur_self = dwell_at(plan, cand)
        pred = [(j, t) for j, t in times if t <= cand + 1e-12]
        succ = [(j, t) for j, t in times if t > cand + 1e-12]
        if pred:
            j, tj = pred[-1]
            pj = plans[j]
            psi_j = squint_at(tj, pj.t_ca_s, lib.geo)
            need = _need_between(
                dwell_at(pj, tj), abs(psi_self - psi_j),
                boundary_rate_of(pj.mode, psi_j, lib),
                boundary_rate_of(plan.mode, psi_self, lib), lib, pads,
            )
            if cand - tj < need - 1e-12:
                return False
        if succ:
            j, tj = succ[0]
            pj = plans[j]
            psi_j = squint_at(tj, pj.t_ca_s, lib.geo)
            need = _need_between(
                dur_self, abs(psi_j - psi_self),
                boundary_rate_of(plan.mode, psi_self, lib),
                boundary_rate_of(pj.mode, psi_j, lib), lib, pads,
            )
            if tj - cand < need - 1e-12:
                return False
        return True

    for idx in order:
        plan = plans[idx]
        if not plan.schedulable:
            continue
        ws = min(lo for lo, _ in plan.intervals)
        candidates = [lo for lo, _ in plan.intervals]
        if repair:
            for j, tj in sorted(starts.items(), key=lambda kv: kv[1]):
                pj = plans[j]
                psi_j = squint_at(tj, pj.t_ca_s, lib.geo)
                psi_self = squint_at(max(ws, tj), plan.t_ca_s, lib.geo)
                need = _need_between(
                    dwell_at(pj, tj), abs(psi_self - psi_j),
                    boundary_rate_of(pj.mode, psi_j, lib),
                    boundary_rate_of(plan.mode, psi_self, lib), lib, pads,
                )
                candidates.append(tj + need)
            candidates = sorted(set(candidates))
        placed = None
        for cand in candidates:
            if cand < ws - 1e-12:
                continue
            # Window membership (ticket 13 audit fix 2026-09-29): repair
            # candidates tj+need may overshoot the task's feasible span --
            # under the maneuver FALLBACK the need is constant, so the
            # fits() re-check cannot self-protect (generation and
            # acceptance see the same need).  Out-of-span candidates are
            # skipped; the task then stays unserved, the greedy-correct
            # outcome.  Same tol as encode_seed_individual (nsga2).
            if not any(lo - 1e-12 <= cand <= hi + 1e-12
                       for lo, hi in plan.intervals):
                continue
            if fits(cand, plan):
                placed = cand
                break
        if placed is not None:
            starts[idx] = placed

    served_p = sum(plans[i].priority_f for i in starts)
    total_p = sum(p.priority_f for p in plans)
    return AnchorResult(
        starts=starts,
        f1_star=served_p / total_p if total_p else 0.0,
        total_priority=total_p,
        served_priority=served_p,
        unserved=[i for i in range(len(plans)) if i not in starts],
    )


def boundary_rate_of(mode, psi_bar_rad: float, lib: ModeLibrary) -> float:
    """Thin single-source re-export (keeps the maneuver implementation the
    only boundary-rate definition, D09-6)."""
    from .maneuver import boundary_rate as _br

    return _br(mode, psi_bar_rad, lib)


def _precompile_frozen(manifest: dict, lib: ModeLibrary, pads: MarginPads):
    """Precompile with the zero-squint dwell (D11-8 frozen wrapper)."""

    def duration(t, mode: Mode, _tca: float):
        return pad_window_tail_(duration_scene_s(mode, 0.0, lib), pads)

    plans = []
    for i, t in enumerate(manifest["tasks"]):
        mode = Mode[t["mode"]]
        t0, t1 = float(t["t_start_s"]), float(t["t_end_s"])
        try:
            from .windows import feasible_subintervals

            fw = feasible_subintervals(lambda tt, m=mode: duration(tt, m, 0.0), t0, t1)
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
                t_ca_s=float(t["t_ca_s"]),
                azimuth_size_m=float(t["azimuth_size_m"]),
                intervals=intervals,
                priority_f=float(t["priority"]),
            )
        )
    return plans


def pad_window_tail_(duration_s: float, pads: MarginPads) -> float:
    from .duration import pad_window_tail

    return pad_window_tail(duration_s, pads)


def anchor_on_manifest(manifest: dict, lib: ModeLibrary, **kwargs) -> AnchorResult:
    """Public entry: the greedy anchor over a scenario manifest (the
    precompilation happens inside ``greedy_anchor`` with the chosen dwell
    wrapper)."""
    return greedy_anchor(manifest, lib, **kwargs)


def assert_fallback_active(lib: ModeLibrary) -> bool:
    """D11-5 setup check at the CALIBRATION geometry (5 km target spacing
    -> d_psi ~ 6.45 mrad, the anchor's typical transition): the maneuver
    fallback must be armed there (model 0.46 s < 0.5 x 1.84 s), which keeps
    the C2 requirement candidate-exact.  At much larger pointing changes
    the model may stand alone -- candidates then become approximate but the
    final C2 check stays exact (feasible, possibly not earliest)."""
    d_psi = 5000.0 / lib.geo.R0_m
    cal = calibrate_against_kim(lib, d_psi, kim_rmt_s=1.84)
    return cal.fallback_active and cal.fallback_bound_s == FALLBACK_MANEUVER_S
