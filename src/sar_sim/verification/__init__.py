"""Constraint verification module for agile SAR scheduling.

Provides an independent ConstraintVerifier that checks C1-C4 constraints
(paper §3) per-solution and produces PASS/FAIL verification reports.
Completely independent of MOEA._evaluate — can be used with any solver's
output.

Typical usage in experiment pipeline::

    from sar_sim.verification import ConstraintVerifier, VerificationReport

    verifier = ConstraintVerifier(instance)
    report = verifier.verify_solution(selected_indices, phi_signed)
    if not report.overall_pass:
        solution_marked_infeasible(...)
"""

from sar_sim.verification.constraints import (
    ConstraintVerifier,
    VerificationReport,
    PerConstraintResult,
    ViolationDetail,
    verify_c1_incidence_squint,
    verify_c2_transition,
    verify_c3_energy,
    verify_c4_memory,
)

__all__ = [
    "ConstraintVerifier",
    "VerificationReport",
    "PerConstraintResult",
    "ViolationDetail",
    "verify_c1_incidence_squint",
    "verify_c2_transition",
    "verify_c3_energy",
    "verify_c4_memory",
]
