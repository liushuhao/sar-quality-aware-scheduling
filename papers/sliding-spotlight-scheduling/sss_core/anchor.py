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
from .evaluator import (
    C2_TOL_S,
    TaskPlan,
    TaskWindow,
    conservative_freeze_squint,
    precompile_tasks,
)
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
    freeze_durations: bool | str = False,
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
        # ticket 16: the anchor must precompile and place against the SAME
        # per-task geometry the evaluator scores with.  Using the library R0
        # here made 8 of 10 anchor starts fall outside their own precompiled
        # feasible set on the real-window family (measured CV 0.0646), because
        # the evaluator re-precompiles with r0_m and the two disagreed.
        # ticket 25: per-WINDOW geometry -- t falls in one transit window,
        # and that window's own zero and slant range drive the dwell.
        # ticket 49 (§8.17-4/8): the task's order and scene size drive the
        # mode parameters and the scene term, exactly as in the evaluator.
        w = plan.window_at(t)
        rho = plan.rho_req_m if plan.mode is not Mode.STR else None
        if freeze_durations is True:
            return duration_scene_s(
                plan.mode, 0.0, lib, r0_m=w.r0_m,
                rho_req_m=rho, l_az_m=plan.azimuth_size_m,
            )
        if freeze_durations == "conservative":
            return duration_scene_s(
                plan.mode,
                conservative_freeze_squint(
                    plan.mode, w.lo, w.hi, w.t_ca_s, w.r0_m, rho, lib),
                lib, r0_m=w.r0_m,
                rho_req_m=rho, l_az_m=plan.azimuth_size_m,
            )
        return duration_scene_s(
            plan.mode,
            squint_at(t, w.t_ca_s, lib.geo, r0_m=w.r0_m),
            lib, r0_m=w.r0_m,
            rho_req_m=rho, l_az_m=plan.azimuth_size_m,
        )

    # precompile with the SAME frozen-dwell wrapper (D11-8 scope)
    if freeze_durations:
        plans = _precompile_frozen(
            manifest, lib, pads, freeze_durations=freeze_durations)
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
        w_self = plan.window_at(cand)
        psi_self = squint_at(cand, w_self.t_ca_s, lib.geo, r0_m=w_self.r0_m)
        dur_self = dwell_at(plan, cand)
        pred = [(j, t) for j, t in times if t <= cand + 1e-12]
        succ = [(j, t) for j, t in times if t > cand + 1e-12]
        if pred:
            j, tj = pred[-1]
            pj = plans[j]
            w_j = pj.window_at(tj)
            psi_j = squint_at(tj, w_j.t_ca_s, lib.geo, r0_m=w_j.r0_m)
            need = _need_between(
                dwell_at(pj, tj), abs(psi_self - psi_j),
                boundary_rate_of(pj.mode, psi_j, lib, r0_m=w_j.r0_m),
                boundary_rate_of(plan.mode, psi_self, lib, r0_m=w_self.r0_m), lib, pads,
            )
            if cand - tj < need - C2_TOL_S:
                return False
        if succ:
            j, tj = succ[0]
            pj = plans[j]
            w_j = pj.window_at(tj)
            psi_j = squint_at(tj, w_j.t_ca_s, lib.geo, r0_m=w_j.r0_m)
            need = _need_between(
                dur_self, abs(psi_j - psi_self),
                boundary_rate_of(plan.mode, psi_self, lib, r0_m=w_self.r0_m),
                boundary_rate_of(pj.mode, psi_j, lib, r0_m=w_j.r0_m), lib, pads,
            )
            if tj - cand < need - C2_TOL_S:
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
                w_j = pj.window_at(tj)
                psi_j = squint_at(tj, w_j.t_ca_s, lib.geo, r0_m=w_j.r0_m)
                c_ref = max(ws, tj)
                # heuristic estimate site: c_ref need not lie in a window of
                # THIS task (tj is another task's start), so use the nearest
                # window -- the candidate itself is membership-gated and then
                # re-checked by fits() against its true window
                w_self = plan.window_nearest(c_ref)
                psi_self = squint_at(c_ref, w_self.t_ca_s, lib.geo, r0_m=w_self.r0_m)
                need = _need_between(
                    dwell_at(pj, tj), abs(psi_self - psi_j),
                    boundary_rate_of(pj.mode, psi_j, lib, r0_m=w_j.r0_m),
                    boundary_rate_of(plan.mode, psi_self, lib, r0_m=w_self.r0_m), lib, pads,
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


def boundary_rate_of(
    mode,
    psi_bar_rad: float,
    lib: ModeLibrary,
    r0_m: float | None = None,
) -> float:
    """Thin single-source re-export (keeps the maneuver implementation the
    only boundary-rate definition, D09-6)."""
    from .maneuver import boundary_rate as _br

    return _br(mode, psi_bar_rad, lib, r0_m=r0_m)


def _precompile_frozen(
    manifest: dict, lib: ModeLibrary, pads: MarginPads, freeze_durations=True
):
    """Precompile with the zero-squint dwell (D11-8 frozen wrapper).

    Ticket 25: dual-schema like ``precompile_tasks`` -- a ``windows`` list
    gives per-window [lo, hi] domains (constant dwell per window's own r0);
    a task without ``windows`` is the single-window synthetic family, whose
    fields are read straight from the manifest.
    """

    def duration(t, mode: Mode, _tca: float, r0=None, rho=None, laz=None,
                 _lo=None, _hi=None):
        if freeze_durations == "conservative":
            _squint = (
                conservative_freeze_squint(mode, _lo, _hi, _tca, r0, rho, lib)
                if (_lo is not None and _hi is not None) else 0.0
            )
        else:
            _squint = 0.0
        return pad_window_tail_(
            duration_scene_s(
                mode, _squint, lib, r0_m=r0, rho_req_m=rho, l_az_m=laz
            ),
            pads,
        )

    plans = []
    for i, t in enumerate(manifest["tasks"]):
        mode = Mode[t["mode"]]
        # ticket 16: the frozen-dwell variant must use the SAME per-task R0 as
        # the production precompile, or its intervals describe a different
        # feasible set than the one it is compared against
        r0_t = float(t["r0_m"]) if t.get("r0_m") is not None else None
        # ticket 49: the frozen arm carries the same task parameters and the
        # same SPT start-domain clamp as production -- otherwise its feasible
        # set describes a different mode.
        rho_t = (
            float(t["rho_req_m"]) if t.get("rho_req_m") is not None else None
        )
        az_t = (
            float(t["azimuth_size_m"])
            if t.get("azimuth_size_m") is not None else None
        )
        task_rho = rho_t if mode is not Mode.STR else None
        if "windows" in t:
            specs = [
                (
                    float(w["lo_s"]), float(w["hi_s"]), float(w["t_ca_s"]),
                    float(w["r0_m"]) if w.get("r0_m") is not None else r0_t,
                )
                for w in t["windows"]
            ]
        else:
            specs = [(
                float(t["t_start_s"]), float(t["t_end_s"]),
                float(t["t_ca_s"]), r0_t,
            )]
        windows = []
        any_feasible = False
        for lo, hi, w_tca, w_r0 in specs:
            # ticket 49 (§8.17-11): the same SPT start-domain clamp as the
            # production precompile (mode applicability is not an ablation
            # arm -- the frozen arm holds the DWELL, not the domain).
            domains = ((lo, hi),)
            if mode is Mode.SPT and task_rho is not None:
                from .windows import spt_task_start_domain

                domains = spt_task_start_domain(
                    ((lo, hi),), task_rho, w_tca, w_r0, lib
                )
            ivs: tuple = ()
            for d_lo, d_hi in domains:
                from .windows import feasible_subintervals

                try:
                    fw = feasible_subintervals(
                        lambda tt, m=mode, _r0=w_r0, _rho=task_rho,
                        _laz=az_t: duration(tt, m, 0.0, _r0, _rho, _laz,
                                            _lo=lo, _hi=hi),
                        d_lo, d_hi,
                    )
                    ivs += tuple(fw.intervals) if fw else ()
                except ValueError:
                    continue
            # ticket 48: the SAME resolution hard constraint as the production
            # precompile -- otherwise the frozen arm describes a different
            # feasible set than the one it is compared against.
            if ivs and t.get("rho_req_m") is not None:
                from .windows import resolution_clip

                ivs = resolution_clip(
                    ivs, mode, float(t["rho_req_m"]), w_tca, w_r0, lib
                )
            any_feasible = any_feasible or any(h > l for l, h in ivs)
            # the freeze applies to the DWELL only (D11-8 scope): the
            # window's squint zero stays the manifest's real t_ca, exactly
            # like the pre-ticket-25 frozen precompile
            windows.append(
                TaskWindow(lo=lo, hi=hi, t_ca_s=w_tca, r0_m=w_r0, intervals=ivs)
            )
        intervals = (
            tuple(iv for w in windows for iv in w.intervals)
            if any_feasible else None
        )
        plans.append(
            TaskPlan(
                index=i,
                priority=int(t["priority"]),
                # ticket 48: same None tolerance as the evaluator constructor
                # -- the clip guard skips above, the field read must not
                # KeyError behind it (pre-ticket-25 manifests).
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
