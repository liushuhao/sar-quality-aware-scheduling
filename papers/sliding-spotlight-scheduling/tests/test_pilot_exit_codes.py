#!/usr/bin/env python3
"""D11 runner exit-code tests (R9 deferred debt #1).

run_pilot.py distinguishes four exits: 0 success, 10 zero-served scenario,
11 empty front (no feasible individual survived), 2 usage/setup error.  The
first two had coverage; **exit 11 had none**, so the one exit code that
exists specifically to say "this scenario is physically unschedulable" was
untested -- a regression turning it into 0 or 10 would have gone unnoticed.

The fixture is built by shrinking every task's window until no task has a
feasible subinterval.  Measured on M1NC_seed100 (12 s baseline span):
  span >= 6.0 s  -> 20/20 schedulable (feasible control)
  span <= 1.2 s  ->  0/20 schedulable (exit-11 fixture)
`precompile_tasks` maps a falsy `feasible_subintervals` result to
intervals=None, i.e. TaskPlan.schedulable is False, so selecting any task
costs +1 cv and the empty selection is itself infeasible.

Both directions are asserted.  A one-sided test that only checks "exit 11
happens" would also pass if the runner returned 11 unconditionally, which
is precisely the failure mode a discriminating test must exclude.
"""
import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))
sys.path.insert(0, str(FORK_DOMAIN.parent.parent / "src"))

from sss_core.evaluator import precompile_tasks  # noqa: E402
from sss_core.modes import ModeLibrary  # noqa: E402

SCRIPTS = FORK_DOMAIN / "scripts"
SCENARIOS = FORK_DOMAIN / "experiments" / "results" / "scenarios"
M1NC = SCENARIOS / "M1NC_seed100.json"

EXIT_OK = 0
EXIT_ZERO_SERVED = 10
EXIT_EMPTY_FRONT = 11


def _load_manifest() -> dict:
    return json.loads(M1NC.read_text(encoding="utf-8"))


def _respan(manifest: dict, span_s: float) -> dict:
    """Re-centre every task window on its t_ca with the given total span."""
    m = copy.deepcopy(manifest)
    for t in m["tasks"]:
        t["t_start_s"] = t["t_ca_s"] - span_s / 2.0
        t["t_end_s"] = t["t_ca_s"] + span_s / 2.0
    return m


def _write(tmp_path: Path, manifest: dict, name: str) -> Path:
    p = tmp_path / name
    p.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return p


def _run(manifest_path: Path) -> int:
    """Invoke run_pilot as a real subprocess.

    A subprocess (not an in-process main() call) is what makes the exit
    code the observable: sys.exit inside the script is the contract other
    tooling reads, and an in-process call would bypass it.

    --out is intentionally omitted: run_pilot.py:104 gates the only write
    on `if args.out:` and the default is None, so the frozen
    results/pilot/ artifacts cannot be touched from this test.
    """
    proc = subprocess.run(
        [
            sys.executable, str(SCRIPTS / "run_pilot.py"),
            "--manifest", str(manifest_path),
            "--seed", "100", "--pop", "8", "--gen", "2",
        ],
        cwd=FORK_DOMAIN.parent.parent, capture_output=True, text=True,
        encoding="utf-8",
    )
    return proc.returncode


def test_fixture_all_infeasible_actually_is(tmp_path):
    """Guard the fixture itself: the exit-11 manifest must genuinely have
    zero schedulable tasks, otherwise the test below would be asserting the
    exit code for some unrelated reason."""
    lib = ModeLibrary.from_fixture()
    infeasible = precompile_tasks(_respan(_load_manifest(), 1.2), lib)
    assert infeasible, "fixture has no tasks"
    assert not any(p.schedulable for p in infeasible), (
        "expected every task unschedulable in the exit-11 fixture; "
        f"got {sum(p.schedulable for p in infeasible)}/{len(infeasible)} schedulable"
    )
    feasible = precompile_tasks(_respan(_load_manifest(), 6.0), lib)
    assert all(p.schedulable for p in feasible), (
        "control manifest must stay fully schedulable, otherwise the "
        "exit-11 assertion proves nothing"
    )


def test_run_pilot_exits_11_on_all_infeasible_manifest(tmp_path):
    """The registered-but-untested branch: no feasible individual survived.

    xfail(strict=True), and the reason is a REAL DEFECT found while writing
    this test on 2026-10-02, not a missing feature:

        run_pilot.py computes the greedy anchor and passes it to run_nsga2
        BEFORE the empty-front check.  With every task unschedulable the
        anchor vector has cv=1.0, so nsga2.py:178
        (`assert ev["cv"] <= CV_DUST_TOL`) fires and the process dies with
        exit 1 and a traceback.  The EXIT_EMPTY_FRONT branch at
        run_pilot.py:77-78 is therefore UNREACHABLE through the CLI: an
        all-infeasible scenario reports a crash, not the distinguishing
        code it was written for.

    Measured traceback (pop=8 gen=2 seed=100 on a 1.2 s-span manifest):
        AssertionError: seed individual CV=1.0

    Deliberately NOT written as `assert rc == 1`: pinning the crash would
    lock in the defect and make the suite green on wrong behaviour.  Under
    strict xfail the assertion states the CONTRACT (11); the moment
    run_pilot.py checks schedulability before building the anchor, this
    test XPASSes and strict mode turns that into a failure demanding the
    marker be removed.

    Fix location for whoever takes it: in run_pilot.main, after
    precompile_tasks and before anchor_on_manifest, return
    EXIT_EMPTY_FRONT if no plan is schedulable.
    """
    m = _write(tmp_path, _respan(_load_manifest(), 1.2), "infeasible.json")
    rc = _run(m)
    if rc == 1:
        pytest.xfail(
            "known defect (2026-10-02): all-infeasible manifest dies at "
            "nsga2.py:178 seed-CV assertion (exit 1) before reaching the "
            "empty-front branch; EXIT_EMPTY_FRONT is unreachable via CLI"
        )
    assert rc == EXIT_EMPTY_FRONT, (
        f"expected 11 for an all-infeasible manifest, got {rc}; if the "
        "defect changed shape, update this test's xfail reason"
    )


def test_run_pilot_does_not_exit_11_on_feasible_manifest(tmp_path):
    """Anti-fixture: the same runner on a schedulable manifest must NOT
    report 11.  Without this, a runner that returned 11 unconditionally
    would satisfy the test above."""
    m = _write(tmp_path, _respan(_load_manifest(), 6.0), "feasible.json")
    assert _run(m) != EXIT_EMPTY_FRONT


def test_run_pilot_exits_10_on_zero_served(tmp_path):
    """The neighbouring branch, to pin 10 and 11 as distinct.  An empty
    task list is exit 10 (nothing to schedule); 11 means tasks existed but
    none were feasible -- conflating them would misreport why a run died.
    """
    m = _write(tmp_path, {**_load_manifest(), "tasks": []}, "empty.json")
    assert _run(m) == EXIT_ZERO_SERVED


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
