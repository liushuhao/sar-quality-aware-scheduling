"""Independent constraint verification for agile SAR scheduling.

Checks constraints C1-C5 from the problem formalization, producing
per-constraint PASS/FAIL results.  Completely independent of
SARschedulingProblem._evaluate — reuses only the transition time model
(compute_transition_time) and Earth-curvature conversion (off_nadir_to_incidence)
which are physics functions, not solver logic.

Constraints checked (from problem_formalization.md):
    C1 — Angle Feasibility:  |φ_i| ∈ [φ_min_i, φ_max_i]
    C2 — Resolution:         θ(|φ_i|) ≥ θ_min_res
    C3 — Attitude Transition: τ(φ_a, φ_b) ≤ available_gap
    C4 — Energy Budget:       Σ e_i ≤ E_max
    C5 — Memory Budget:       Σ m_i ≤ M_max
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from sar_sim.solver.types import (
    AgileTask,
    AgileSARInstance,
    compute_los_separation,
    compute_transition_time,
)

# ---------------------------------------------------------------------------
# Report data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ViolationDetail:
    """Structured information about a single constraint violation.

    Attributes:
        constraint: constraint label (C1–C5)
        task_ids: which task(s) are involved
        expected: what the constraint requires
        actual: what the solution provides
        magnitude: how much the constraint is violated (>0)
        description: human-readable explanation
    """
    constraint: str
    task_ids: List[int]
    expected: str
    actual: str
    magnitude: float
    description: str = ""


@dataclass(frozen=True)
class PerConstraintResult:
    """Result of checking a single constraint.

    Attributes:
        constraint: label (C1–C5)
        passed: True if no violations found
        total_checks: number of individual checks performed
        violations: list of violation details (empty if passed)
        worst_violation_magnitude: largest violation magnitude (0 if none)
    """
    constraint: str
    passed: bool
    total_checks: int
    violations: Tuple[ViolationDetail, ...] = ()
    worst_violation_magnitude: float = 0.0

    def __bool__(self) -> bool:
        return self.passed


@dataclass(frozen=True)
class VerificationReport:
    """Complete constraint verification report for one solution.

    Attributes:
        results: per-constraint results (keys: "C1"–"C5")
        overall_pass: True iff all constraints pass
        n_constraints_checked: number of constraints checked (always 5)
        n_passed: how many constraints passed
        n_failed: how many constraints failed
        all_violations: concatenated list of all violations across all constraints
    """
    results: Dict[str, PerConstraintResult]
    overall_pass: bool
    n_constraints_checked: int
    n_passed: int
    n_failed: int
    all_violations: Tuple[ViolationDetail, ...] = ()

    def summary(self) -> str:
        """One-line summary: e.g. 'PASS (5/5)' or 'FAIL (3/5, C3+C4 violated)'."""
        if self.overall_pass:
            return f"PASS ({self.n_passed}/{self.n_constraints_checked})"
        failed = [c for c, r in self.results.items() if not r.passed]
        return f"FAIL ({self.n_passed}/{self.n_constraints_checked}, {'+'.join(failed)} violated)"

    def format_report(self) -> str:
        """Multi-line formatted verification report."""
        lines = ["=" * 60]
        lines.append(f"  CONSTRAINT VERIFICATION — {self.summary()}")
        lines.append("=" * 60)
        for c in ["C1", "C2", "C3", "C4", "C5"]:
            r = self.results[c]
            status = "PASS" if r.passed else "FAIL"
            lines.append(f"  {c} [{status}]  {r.total_checks} checks, "
                         f"worst violation={r.worst_violation_magnitude:.4f}")
            for v in r.violations:
                lines.append(f"    └─ {v.description}")
        lines.append("=" * 60)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Per-constraint verification functions
# ---------------------------------------------------------------------------

def verify_c1_angle_feasibility(
    selected_indices: List[int],
    phi_signed: np.ndarray,
    tasks: List[AgileTask],
) -> PerConstraintResult:
    """C1: Each selected task's |φ_i| must lie in [phi_min_i, phi_max_i].

    The off-nadir angle phi is signed (± for left/right looking), so
    the constraint is checked on the absolute value |φ_i|.

    Args:
        selected_indices: which tasks are selected
        phi_signed: signed off-nadir angles (indexed by task index)
        tasks: all tasks in the instance

    Returns:
        PerConstraintResult with per-task violation details
    """
    violations: List[ViolationDetail] = []
    total_checks = 0

    for i in selected_indices:
        task = tasks[i]
        phi_abs = abs(float(phi_signed[i]))
        total_checks += 1

        # Below minimum
        if phi_abs < task.phi_min:
            mag = task.phi_min - phi_abs
            violations.append(ViolationDetail(
                constraint="C1",
                task_ids=[i],
                expected=f"|φ| >= {task.phi_min:.6f}",
                actual=f"|φ| = {phi_abs:.6f}",
                magnitude=mag,
                description=f"Task {i} ({task.target_id}): |φ|={phi_abs:.4f} "
                            f"below lower bound {task.phi_min:.4f} (Δ={mag:.4f})",
            ))

        # Above maximum
        if phi_abs > task.phi_max:
            mag = phi_abs - task.phi_max
            violations.append(ViolationDetail(
                constraint="C1",
                task_ids=[i],
                expected=f"|φ| <= {task.phi_max:.6f}",
                actual=f"|φ| = {phi_abs:.6f}",
                magnitude=mag,
                description=f"Task {i} ({task.target_id}): |φ|={phi_abs:.4f} "
                            f"above upper bound {task.phi_max:.4f} (Δ={mag:.4f})",
            ))

    worst = max((v.magnitude for v in violations), default=0.0)
    return PerConstraintResult(
        constraint="C1",
        passed=len(violations) == 0,
        total_checks=total_checks,
        violations=tuple(violations),
        worst_violation_magnitude=worst,
    )


def verify_c2_resolution(
    selected_indices: List[int],
    phi_signed: np.ndarray,
    tasks: List[AgileTask],
) -> PerConstraintResult:
    """C2: Each selected task's |φ_i| must satisfy resolution requirement.

    Checks |φ_i| >= phi_min_res for each selected task.  The resolution
    requirement is expressed as the minimum off-nadir angle φ_min_res
    (consistent with how the MOEA encodes this constraint).

    For Earth-curvature-corrected resolution, the incidence angle θ(|φ|)
    should be >= θ_min_res, but phi_min_res is already stored in off-nadir
    space, so the direct comparison is equivalent given the 1.5–5° curvature.

    Args:
        selected_indices: which tasks are selected
        phi_signed: signed off-nadir angles
        tasks: all tasks

    Returns:
        PerConstraintResult
    """
    violations: List[ViolationDetail] = []
    total_checks = 0

    for i in selected_indices:
        task = tasks[i]
        phi_abs = abs(float(phi_signed[i]))
        total_checks += 1

        if task.phi_min_res > 0 and phi_abs < task.phi_min_res:
            mag = task.phi_min_res - phi_abs
            violations.append(ViolationDetail(
                constraint="C2",
                task_ids=[i],
                expected=f"|φ| >= {task.phi_min_res:.6f} (resolution)",
                actual=f"|φ| = {phi_abs:.6f}",
                magnitude=mag,
                description=f"Task {i} ({task.target_id}): |φ|={phi_abs:.4f} "
                            f"below resolution minimum {task.phi_min_res:.4f} "
                            f"(Δ={mag:.4f})",
            ))

    worst = max((v.magnitude for v in violations), default=0.0)
    return PerConstraintResult(
        constraint="C2",
        passed=len(violations) == 0,
        total_checks=total_checks,
        violations=tuple(violations),
        worst_violation_magnitude=worst,
    )


def verify_c3_transition(
    selected_indices: List[int],
    phi_signed: np.ndarray,
    tasks: List[AgileTask],
    max_slew_rate: float,
    settle_time: float,
    instance: Optional["AgileSARInstance"] = None,
    t_actual: Optional[Union[np.ndarray, List[float]]] = None,
) -> PerConstraintResult:
    """C3: All consecutive selected tasks must have feasible transitions.

    For every consecutive pair of selected tasks sorted by t_earliest,
    the attitude transition time τ(φ_a, φ_b) must not exceed the
    available gap between t_end(a) and t_start(b).

    When ``instance`` is provided, uses the full 3-axis attitude model
    (roll, pitch, yaw).  When ``instance`` is None, falls back to the
    legacy off-nadir-only model for backward compatibility.

    When ``t_actual`` is provided (together with ``instance``), uses the
    actual observation times for LOS angular separation (via
    ``compute_los_separation``) and gap computation, matching the MOEA's
    own C3 evaluation.  Without ``t_actual``, falls back to t_earliest
    to preserve backward compatibility.

    Args:
        selected_indices: which tasks are selected
        phi_signed: signed off-nadir angles
        tasks: all tasks
        max_slew_rate: maximum attitude slew rate (rad/s)
        settle_time: post-maneuver settling time (s)
        instance: optional AgileSARInstance for full 3-axis C3 check
        t_actual: optional actual observation times (length N, indexed by
                  task index).  When provided, used for LOS separation
                  and gap calculation.

    Returns:
        PerConstraintResult
    """
    violations: List[ViolationDetail] = []
    total_checks = 0

    if len(selected_indices) < 2:
        return PerConstraintResult(
            constraint="C3",
            passed=True,
            total_checks=0,
        )

    # Sort by earliest start time (same ordering used in MOEA)
    sorted_indices = sorted(selected_indices, key=lambda i: tasks[i].t_earliest)

    # If t_actual is provided, also sort indices by actual time for
    # consistent ordering (mirrors MOEA's sort-by-t_actual approach).
    if t_actual is not None:
        sorted_indices = sorted(
            selected_indices, key=lambda i: float(t_actual[i]),
        )

    for k in range(len(sorted_indices) - 1):
        i_a = sorted_indices[k]
        i_b = sorted_indices[k + 1]
        task_a = tasks[i_a]
        task_b = tasks[i_b]
        total_checks += 1

        if t_actual is not None and instance is not None:
            # Use actual observation times for both LOS separation
            # and gap calculation (matching MOEA._evaluate logic).
            t_a = float(t_actual[i_a])
            t_b = float(t_actual[i_b])
            delta_eta = compute_los_separation(
                task_a, t_a, task_b, t_b, instance,
            )
            tau = delta_eta / max_slew_rate + settle_time
            t_end_a = t_a + task_a.duration
            available_gap = t_b - t_end_a
        else:
            tau = compute_transition_time(
                task_a, float(phi_signed[i_a]),
                task_b, float(phi_signed[i_b]),
                max_slew_rate, settle_time,
                instance=instance,
            )
            t_end_a = task_a.t_earliest + task_a.duration
            available_gap = task_b.t_earliest - t_end_a

        if available_gap < tau:
            mag = tau - available_gap
            violations.append(ViolationDetail(
                constraint="C3",
                task_ids=[i_a, i_b],
                expected=f"available_gap >= {tau:.3f}s",
                actual=f"available_gap = {available_gap:.3f}s",
                magnitude=mag,
                description=f"Transition {task_a.target_id}→{task_b.target_id}: "
                            f"need {tau:.2f}s, have {available_gap:.2f}s "
                            f"(Δ={mag:.2f}s). φ_a={phi_signed[i_a]:.4f}, "
                            f"φ_b={phi_signed[i_b]:.4f}",
            ))

    worst = max((v.magnitude for v in violations), default=0.0)
    return PerConstraintResult(
        constraint="C3",
        passed=len(violations) == 0,
        total_checks=total_checks,
        violations=tuple(violations),
        worst_violation_magnitude=worst,
    )


def verify_c4_energy(
    selected_indices: List[int],
    tasks: List[AgileTask],
    energy_budget: float,
) -> PerConstraintResult:
    """C4: Total energy consumption must not exceed budget.

    Σ x_i · e_i ≤ E_max

    Args:
        selected_indices: which tasks are selected
        tasks: all tasks
        energy_budget: maximum energy budget (E_max)

    Returns:
        PerConstraintResult
    """
    energy_used = sum(tasks[i].energy for i in selected_indices)
    passed = energy_used <= energy_budget
    mag = max(0.0, energy_used - energy_budget)

    violations: Tuple[ViolationDetail, ...] = ()
    if not passed:
        violations = (ViolationDetail(
            constraint="C4",
            task_ids=list(selected_indices),
            expected=f"Σ energy <= {energy_budget:.1f}",
            actual=f"Σ energy = {energy_used:.1f}",
            magnitude=mag,
            description=f"Energy: {energy_used:.1f} > {energy_budget:.1f} "
                        f"(excess={mag:.1f})",
        ),)

    return PerConstraintResult(
        constraint="C4",
        passed=passed,
        total_checks=1,
        violations=violations,
        worst_violation_magnitude=mag,
    )


def verify_c5_memory(
    selected_indices: List[int],
    tasks: List[AgileTask],
    memory_budget: float,
) -> PerConstraintResult:
    """C5: Total memory consumption must not exceed budget.

    Σ x_i · m_i ≤ M_max

    Args:
        selected_indices: which tasks are selected
        tasks: all tasks
        memory_budget: maximum memory budget (M_max)

    Returns:
        PerConstraintResult
    """
    memory_used = sum(tasks[i].memory for i in selected_indices)
    passed = memory_used <= memory_budget
    mag = max(0.0, memory_used - memory_budget)

    violations: Tuple[ViolationDetail, ...] = ()
    if not passed:
        violations = (ViolationDetail(
            constraint="C5",
            task_ids=list(selected_indices),
            expected=f"Σ memory <= {memory_budget:.1f}",
            actual=f"Σ memory = {memory_used:.1f}",
            magnitude=mag,
            description=f"Memory: {memory_used:.1f} > {memory_budget:.1f} "
                        f"(excess={mag:.1f})",
        ),)

    return PerConstraintResult(
        constraint="C5",
        passed=passed,
        total_checks=1,
        violations=violations,
        worst_violation_magnitude=mag,
    )


# ---------------------------------------------------------------------------
# ConstraintVerifier — orchestrator
# ---------------------------------------------------------------------------

class ConstraintVerifier:
    """Independent constraint verifier for agile SAR scheduling solutions.

    Checks all five constraints (C1–C5) for a given solution against
    the problem instance.  Completely independent of MOEA._evaluate.

    Usage::

        verifier = ConstraintVerifier(instance)
        report = verifier.verify_solution(selected_indices, phi_signed)

        if report.overall_pass:
            print("Solution feasible ✓")
        else:
            print(report.format_report())
            # Mark infeasible, skip from Pareto front, etc.
    """

    def __init__(self, instance: AgileSARInstance):
        """Create a verifier for a specific problem instance.

        Args:
            instance: the AgileSARInstance defining task bounds and resources
        """
        self._instance = instance
        self._tasks = instance.tasks
        self._phi_min = instance.phi_min
        self._phi_max = instance.phi_max
        self._max_slew_rate = instance.max_slew_rate
        self._settle_time = instance.settle_time
        self._energy_budget = instance.energy_budget
        self._memory_budget = instance.memory_budget

    @property
    def instance(self) -> AgileSARInstance:
        return self._instance

    def verify_solution(
        self,
        selected_indices: List[int],
        phi_signed: Union[np.ndarray, List[float]],
        t_actual: Optional[Union[np.ndarray, List[float]]] = None,
    ) -> VerificationReport:
        """Verify all constraints for a decoded solution.

        Args:
            selected_indices: list of selected task indices
            phi_signed: signed off-nadir angles, indexed by task index
                        (length N, only entries at selected_indices matter)
            t_actual: optional actual observation times (length N, indexed by
                      task index).  When provided, used for C3 LOS separation
                      and gap calculation (matching MOEA._evaluate).

        Returns:
            VerificationReport with per-constraint PASS/FAIL status
        """
        phi_signed = np.asarray(phi_signed, dtype=float)

        results: Dict[str, PerConstraintResult] = {}

        results["C1"] = verify_c1_angle_feasibility(
            selected_indices, phi_signed, self._tasks)
        results["C2"] = verify_c2_resolution(
            selected_indices, phi_signed, self._tasks)
        results["C3"] = verify_c3_transition(
            selected_indices, phi_signed, self._tasks,
            self._max_slew_rate, self._settle_time,
            instance=self._instance,
            t_actual=t_actual)
        results["C4"] = verify_c4_energy(
            selected_indices, self._tasks, self._energy_budget)
        results["C5"] = verify_c5_memory(
            selected_indices, self._tasks, self._memory_budget)

        all_pass = all(r.passed for r in results.values())
        n_passed = sum(1 for r in results.values() if r.passed)
        n_failed = len(results) - n_passed

        all_violations: List[ViolationDetail] = []
        for r in results.values():
            all_violations.extend(r.violations)

        return VerificationReport(
            results=results,
            overall_pass=all_pass,
            n_constraints_checked=len(results),
            n_passed=n_passed,
            n_failed=n_failed,
            all_violations=tuple(all_violations),
        )

    def verify_from_chromosome(
        self,
        X: np.ndarray,
    ) -> Tuple[VerificationReport, List[int], np.ndarray]:
        """Verify constraints from a raw pymoo chromosome (2N or 3N encoding).

        Supports both encodings:
          2N (new): x[0:N] + tau[N:2N]
          3N (legacy): x[0:N] + d[N:2N] + φ_abs[2N:3N]

        For 2N, phi is derived from geometry at decoded t_actual.
        For 3N, phi is extracted directly from the chromosome.

        Args:
            X: chromosome vector of length 2N or 3N

        Returns:
            (report, selected_indices, phi_signed)
        """
        N = self._instance.N
        if len(X) == 2 * N:
            # ── 2N encoding: x + tau ────────────────────────────
            x_bin = X[:N]
            tau = X[N:2*N]
            from sar_sim.solver.types import compute_full_attitude
            phi_signed = np.zeros(N, dtype=float)
            for i in range(N):
                if x_bin[i] > 0.5:
                    task = self._instance.tasks[i]
                    t_act = task.t_earliest + tau[i] * (
                        task.t_latest - task.duration - task.t_earliest)
                    roll, _, _ = compute_full_attitude(task, t_act, 1.0, self._instance)
                    phi_signed[i] = abs(roll)
            selected_indices = [i for i in range(N) if x_bin[i] > 0.5]
        elif len(X) == 3 * N:
            # ── 3N encoding (legacy Plan A) ─────────────────────
            x_bin = X[:N]
            directions = X[N:2*N]
            phi_abs = X[2*N:3*N]
            phi_signed = np.where(np.asarray(directions) > 0.5,
                                  np.asarray(phi_abs),
                                  -np.asarray(phi_abs))
            selected_indices = [i for i in range(N) if x_bin[i] > 0.5]
        else:
            raise ValueError(
                f"Chromosome length {len(X)} does not match "
                f"2*N = {2*N} or 3*N = {3*N} for instance with N={N}")

        report = self.verify_solution(selected_indices, phi_signed)
        return report, selected_indices, phi_signed

    def verify_frontier(
        self,
        frontier: List[dict],
    ) -> List[Tuple[dict, VerificationReport]]:
        """Verify all solutions in a Pareto frontier.

        Each frontier dict must have keys 'selected' (list of indices)
        and 'phis' (list of signed off-nadir angles).

        The 'phis' list may be either:
        - Full N-length array (indexed by task index), or
        - Per-selected-task array (same length as 'selected', positional
          correspondence).  This method automatically reconstructs the
          full N-length array when needed.

        Args:
            frontier: list of decoded frontier solutions

        Returns:
            list of (solution_dict, VerificationReport) pairs
        """
        results = []
        for sol in frontier:
            selected = sol["selected"]
            phis = sol["phis"]
            # Reconstruct full N-length phi_signed if phis is per-selected
            if len(phis) == len(selected) and len(phis) < self._instance.N:
                phi_full = np.zeros(self._instance.N, dtype=float)
                for idx, task_idx in enumerate(selected):
                    phi_full[task_idx] = phis[idx]
            else:
                phi_full = np.asarray(phis, dtype=float)
            report = self.verify_solution(selected, phi_full)
            results.append((sol, report))
        return results

    def feasible_frontier(
        self,
        frontier: List[dict],
    ) -> List[dict]:
        """Filter frontier to only feasible solutions (all constraints pass).

        Args:
            frontier: list of decoded frontier solutions

        Returns:
            list of feasible solution dicts
        """
        return [sol for sol, report in self.verify_frontier(frontier)
                if report.overall_pass]
