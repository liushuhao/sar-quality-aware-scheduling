"""Guard tests for runner resume/caliber hardening (2026-08-14).

Locks the two fault modes behind the mixed-caliber rerun:
  * _solver_code_identical must accept a stamp whose moea.py matches HEAD
    and reject a stamp where the value-defining solver code changed. Using
    stamp == HEAD would wrongly invalidate current results after an unrelated
    commit (docs/tests/dead-code); using content identity avoids that.
  * _atomic_write_json must round-trip, leave no .tmp, and overwrite safely
    so a hard power-off mid-write cannot truncate resume state.

The runners are imported from their file paths (not via package import) so
loading them does not invoke main(); both guard their solve loop behind
``if __name__ == "__main__"``.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
EXP = REPO / "papers" / "single-sat-quality" / "experiments"
SRC = REPO / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _load_runner(filename: str):
    path = EXP / filename
    spec = importlib.util.spec_from_file_location(filename.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def r3():
    return _load_runner(Path("run_moea_3obj.py"))


@pytest.fixture(scope="module")
def r2():
    return _load_runner(Path("run_moea_2obj.py"))


def _head_short() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=str(REPO), text=True
    ).strip()[:8]


# A commit that changed src/sar_sim/solver/moea.py (B1 knee fix). Its
# solver code differs from HEAD, so a result stamped at it must be treated
# as stale (moea.py at f96674f != moea.py at HEAD).
STALE_BECAUSE_MOEA_CHANGED = "f96674f"
# Pre-RDR066 NESZ double-count, explicitly bad.
KNOWN_BAD = "681ced6"


@pytest.mark.parametrize("runner_name", ["r2", "r3"])
def test_solver_code_identical_to_head(request, runner_name):
    runner = request.getfixturevalue(runner_name)
    assert runner._solver_code_identical(_head_short()) is True


@pytest.mark.parametrize("runner_name", ["r2", "r3"])
@pytest.mark.parametrize("stamp", [STALE_BECAUSE_MOEA_CHANGED, KNOWN_BAD])
def test_stale_stamp_rejected(request, runner_name, stamp):
    runner = request.getfixturevalue(runner_name)
    assert runner._solver_code_identical(stamp) is False


@pytest.mark.parametrize("runner_name", ["r2", "r3"])
@pytest.mark.parametrize("stamp", ["", "unknown", "MISSING"])
def test_malformed_stamp_rejected(request, runner_name, stamp):
    runner = request.getfixturevalue(runner_name)
    assert runner._solver_code_identical(stamp) is False


@pytest.mark.parametrize("runner_name", ["r2", "r3"])
def test_atomic_write_roundtrip(request, runner_name, tmp_path):
    runner = request.getfixturevalue(runner_name)
    p = tmp_path / "progress.json"
    payload = {"completed": {"S1/x.pkl": {"f1": 1.0}}, "n": 3}
    runner._atomic_write_json(p, payload)
    assert json.loads(p.read_text(encoding="utf-8")) == payload
    assert not (tmp_path / "progress.json.tmp").exists()


@pytest.mark.parametrize("runner_name", ["r2", "r3"])
def test_atomic_write_overwrite(request, runner_name, tmp_path):
    runner = request.getfixturevalue(runner_name)
    p = tmp_path / "progress.json"
    runner._atomic_write_json(p, {"v": 1})
    runner._atomic_write_json(p, {"v": 2})
    assert json.loads(p.read_text(encoding="utf-8")) == {"v": 2}
    assert not (tmp_path / "progress.json.tmp").exists()
