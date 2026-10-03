"""Evaluator-side coupled predicates: C2/C3/C4 + schedule conflict (spec D9).

Single-predicate-source layering (spec D9): the PRECOMPILE side owns pure
geometric time-varying predicates (``sss_core.windows``: feasible_at,
window_end_ok, footprint_ok, scan guards); THIS module owns the
cross-task coupled predicates and CONSUMES the window atoms plus the
ticket-03/05/07 physics (durations, margin pads, maneuver closure).  The
scheduler (ticket 10), the greedy anchor (ticket 11) and the verify gate
(ticket 12) must import predicates from here -- duplicated predicate
definitions anywhere in sss_core turn the architecture guard red.

Formula registration (D09-5): the C2 assembly, the C3 weight ladder and
the C4 chain are registered EXCLUSIVELY in
``experiments/predicates_calibration.json`` (frozen by ticket 09); the
frozen formula-spec is deliberately not touched for these implementation
conventions.

Ticket-09 decisions D09-1..7:

* D09-1 C2 transfer requirement
  ``need = (1 + pads.inter_task_fraction) * dur_i + t_maneuver + SETTLE_S``
  -- the 25% pad multiplies the DWELL (Kim's own wording, four places —
  p.7 / p.11 execution-layer definitions plus p.19 parameter and p.25
  results restatement; ticket 21 corrected the earlier "three places" —
  and the frozen formula-spec §4.1 registration: "a margin of 25% is
  considered in addition to the SAT"), NOT the maneuver.  ``pads`` is a
  parameter so the M?NC degenerate anchor pays zero pad through the very
  same code path (its manifest pads field is consumed HERE first).  The
  window-tail pad is deliberately absent from C2 (D4 layering: 25% of the
  dwell ~ 2-10 s already dominates the 1% model error ~ 0.1-0.4 s the
  tail pad covers).  The settle term is fixed (a measured Kim constant,
  never padded).
* D09-2 C4 chain: mem_bytes = PRF * T * N_r * b_q * 2 / 8 with b_q = 3 bit
  per component (I and Q each; TerraSAR-X BAQ 8:3 per-component
  compression, Younis 2006 DLR report TX-SEC-TN-MY-01, web-sourced) and
  N_r = 10,000 range samples per echo (registered design assumption -- no
  per-mode source exists).
* D09-3 C3/C4 budgets are NORMALIZED against the mode-library envelope:
  E_i = w_mode * T_i / (w_max * T_env_max) and
  mem_i = mem_bytes_i / (PRF * T_env_max * N_r * 6 / 8), budget = 1.0 --
  a normalized comparison needs a DEFINED reference, otherwise the
  predicate is degenerate.  T_env_max = the largest feasible scene dwell
  in the library at the envelope-edge squint (computable from the frozen
  fixture, no experimental freedom).
* D09-4 C4 is mode-BLIND under the single production PRF (3630 Hz): its
  discrimination channel is the dwell only.  Stated in the calibration
  JSON; the (mode, T, rho) signature is kept for interface stability.
* D09-7 conflict predicate: imaging intervals [t, t+T] with the BARE T
  (pads are scheduling margin, not physical occupancy) must be pairwise
  disjoint; the maneuver gap between consecutive tasks is C2's business
  -- two layers, zero double counting.
"""
from __future__ import annotations

import math

from .duration import MarginPads
from .maneuver import SETTLE_S
from .modes import Mode, ModeLibrary

__all__ = [
    "c2_transfer_requirement_s",
    "c2_transfer_ok",
    "c3_energy_normalized",
    "c4_memory_bytes",
    "c4_memory_normalized",
    "c3_ok",
    "c4_ok",
    "schedule_conflict",
    "C3_WEIGHTS",
    "C4_BITS_PER_COMPONENT",
    "C4_RANGE_SAMPLES_NR",
]

# C3 weight ladder [design assumption, D09-3]: finer mode -> higher duty /
# data-handling overhead.  Registered in predicates_calibration.json.
C3_WEIGHTS = {Mode.STR: 1.0, Mode.SLS: 1.15, Mode.SPT: 1.3}

# D09-2 registered constants
C4_BITS_PER_COMPONENT = 3
C4_RANGE_SAMPLES_NR = 10_000

# D09-1 internal default: the calibration RMT anchor (Kim scenario 1,
# target 1) used when no explicit maneuver time is injected.  Drift-guarded
# against the fixture (test_fixture_drift_guards).
CALIBRATION_KIM_RMT_S = 1.84


def _t_env_max(lib: ModeLibrary, r0_m: float | None = None) -> float:
    """Envelope reference dwell (D09-3): largest library-mode scene dwell at
    that mode's OWN squint envelope edge.

    Ticket 17 adjudication (2026-10-03, the C3/C4 caliber split).  Per-task
    geometry (ticket 16) moved the MEASURED dwell onto a per-task caliber
    while this REFERENCE stayed library-geometry, and a task with r0 13.5%
    above base produced a dwell of 10.8512 s against a reference of
    10.5830 s -- a normalized 1.0253, i.e. a false constraint violation
    (measured on 25 of 40 real-window scenarios, 38 tasks, worst 1.1721).

    The fix is NOT a per-task reference (that makes C3/C4 a self-comparison
    and destroys the discrimination D09-3 requires) and NOT a loosened
    global constant (that drops the budget's bite).  It is to keep the
    reference a PLATFORM-level upper bound -- "the largest dwell the
    admissible envelope admits" -- evaluated at the geometry of the task
    being measured:

      * ``r0_m is None`` (every pre-ticket-16 family) -> the library constant,
        so the frozen families stay bit-identical;
      * ``r0_m`` given -> the same envelope edge evaluated at THAT task's
        slant range, which is the true bound for that task.

    Budget stays 1.0 in both cases, so exceeding the reference still means
    the dwell leaves the certified envelope.
    """
    return max(_scene_durations(lib, r0_m).values())


def _scene_durations(lib: ModeLibrary, r0_m: float | None = None) -> dict:
    from .duration import duration_scene_s, mode_squint_envelope_rad

    return {
        m: duration_scene_s(m, mode_squint_envelope_rad(m), lib, r0_m=r0_m)
        for m in Mode
    }


def c2_transfer_requirement_s(
    dur_i: float,
    lib: ModeLibrary,
    pads: MarginPads,
    maneuver_s: float | None = None,
    d_psi_rad: float = 0.0,
    omega_start: float = 0.0,
    omega_end: float = 0.0,
) -> dict:
    """Required gap between the START of task i and the start of the next
    task (D09-1): padded dwell + maneuver + settle.  ``maneuver_s`` lets
    the caller inject a precomputed production maneuver time; otherwise it
    is computed from the ticket-07 closure (fallback armed, warnings
    suppressed here -- the calibration warning is emitted at setup)."""
    import warnings

    if maneuver_s is None:
        from .maneuver import calibrate_against_kim, maneuver_time_production

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cal = calibrate_against_kim(lib, d_psi_rad, kim_rmt_s=CALIBRATION_KIM_RMT_S)
        maneuver_s = maneuver_time_production(
            d_psi_rad, omega_start, omega_end, lib, cal
        )["t_maneuver_s"]
    padded_dwell = (1.0 + pads.inter_task_fraction) * dur_i  # D09-1
    return {
        "requirement_s": padded_dwell + maneuver_s + SETTLE_S,
        "padded_dwell_s": padded_dwell,
        "maneuver_s": maneuver_s,
        "settle_s": SETTLE_S,
        "pad_fraction": pads.inter_task_fraction,
    }


def c2_transfer_ok(
    t_i: float,
    t_j: float,
    dur_i: float,
    lib: ModeLibrary,
    pads: MarginPads,
    maneuver_s: float | None = None,
    d_psi_rad: float = 0.0,
    omega_start: float = 0.0,
    omega_end: float = 0.0,
) -> bool:
    """C2: task j may start only after i's padded dwell + maneuver + settle."""
    req = c2_transfer_requirement_s(
        dur_i, lib, pads, maneuver_s, d_psi_rad, omega_start, omega_end
    )
    return (t_j - t_i) >= req["requirement_s"] - 1e-12


def c3_energy_normalized(
    mode: Mode, dur_s: float, lib: ModeLibrary, r0_m: float | None = None
) -> float:
    """Normalized weighted dwell in [0, ~1] against the envelope reference
    (D09-3); budget = 1.0.

    ``r0_m`` (ticket 17 adjudication): the per-task slant range the measured
    dwell was computed with.  Passing it evaluates the reference on the SAME
    caliber; omitting it uses the library constant, which is what every
    pre-ticket-16 family does.
    """
    ref = max(C3_WEIGHTS.values()) * _t_env_max(lib, r0_m)
    return C3_WEIGHTS[mode] * dur_s / ref


def c4_memory_bytes(
    mode: Mode,
    dur_s: float,
    rho_req_m: float,
    prf_hz: float,
    lib: ModeLibrary,
) -> float:
    """Raw-data volume of one imaging task in bytes (D09-2).  ``mode`` and
    ``rho_req_m`` are interface-stability parameters: under the single
    production PRF the chain is mode-blind (D09-4) and rho enters only via
    the dwell."""
    del mode, rho_req_m, lib
    return prf_hz * dur_s * C4_RANGE_SAMPLES_NR * C4_BITS_PER_COMPONENT * 2 / 8.0


def c4_memory_normalized(
    mode: Mode,
    dur_s: float,
    rho_req_m: float,
    prf_hz: float,
    lib: ModeLibrary,
    r0_m: float | None = None,
) -> float:
    """Memory against the envelope reference (D09-3); budget = 1.0.

    ``r0_m``: see ``c3_energy_normalized`` -- same-caliber reference.
    """
    ref = (
        prf_hz * _t_env_max(lib, r0_m) * C4_RANGE_SAMPLES_NR
        * C4_BITS_PER_COMPONENT * 2 / 8.0
    )
    return c4_memory_bytes(mode, dur_s, rho_req_m, prf_hz, lib) / ref


def c3_ok(
    mode: Mode, dur_s: float, lib: ModeLibrary,
    budget: float = 1.0, r0_m: float | None = None,
) -> bool:
    return c3_energy_normalized(mode, dur_s, lib, r0_m) <= budget + 1e-12


def c4_ok(
    mode: Mode,
    dur_s: float,
    rho_req_m: float,
    prf_hz: float,
    lib: ModeLibrary,
    budget: float = 1.0,
    r0_m: float | None = None,
) -> bool:
    return (
        c4_memory_normalized(mode, dur_s, rho_req_m, prf_hz, lib, r0_m)
        <= budget + 1e-12
    )


def schedule_conflict(t_i: float, dur_i: float, t_j: float, dur_j: float) -> bool:
    """True iff the two BARE imaging intervals overlap (D09-7): strict
    inequalities keep back-to-back schedules conflict-free; the maneuver
    gap between consecutive tasks is enforced by C2, not here."""
    return (t_i < t_j + dur_j) and (t_j < t_i + dur_i)
