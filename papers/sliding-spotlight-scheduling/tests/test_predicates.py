#!/usr/bin/env python3
"""Ticket 09 -- coupled predicates + calibration + single-source guard.

The C2 pad object is the DWELL (D09-1, three-source ruling); the C4 chain
carries N_r and I/Q (D09-2); C3/C4 budgets normalize against the frozen
library envelope (D09-3).  The architecture guard derives the scanned
predicate list from ``predicates.__all__`` (D09-6) and asserts the live
consumer (scenario generator) resolves its window atoms to sss_core.
"""
import inspect
import math
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

import sss_core.predicates as pred  # noqa: E402
from sss_core.duration import MarginPads  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402
from sss_core.predicates import (  # noqa: E402
    c2_transfer_ok,
    c2_transfer_requirement_s,
    c3_energy_normalized,
    c3_ok,
    c4_memory_bytes,
    c4_memory_normalized,
    c4_ok,
    schedule_conflict,
)


@pytest.fixture(scope="module")
def lib() -> ModeLibrary:
    return ModeLibrary.from_fixture()


# ── C2 (D09-1) ────────────────────────────────────────────────────────────

def test_c2_pad_object_is_dwell(lib):
    """The 25% pad multiplies the dwell; settle is a fixed term; the
    maneuver enters unpadded."""
    req = c2_transfer_requirement_s(10.0, lib, MarginPads.standard(), maneuver_s=4.07)
    assert req["padded_dwell_s"] == pytest.approx(12.5)
    assert req["requirement_s"] == pytest.approx(12.5 + 4.07 + 2.0)
    assert req["maneuver_s"] == 4.07 and req["settle_s"] == 2.0


def test_c2_pads_parameterized_anchor_zero(lib):
    """M?NC zero-pad flows through the SAME code path (D09-1): the anchor
    pays padded dwell == bare dwell; a hardcoded 0.25 would break this."""
    std = c2_transfer_requirement_s(10.0, lib, MarginPads.standard(), maneuver_s=4.0)
    anchor = c2_transfer_requirement_s(10.0, lib, MarginPads.degenerate_anchor(), maneuver_s=4.0)
    assert anchor["padded_dwell_s"] == 10.0
    assert anchor["requirement_s"] == pytest.approx(16.0)
    assert std["requirement_s"] - anchor["requirement_s"] == pytest.approx(2.5)


def test_c2_predicate_boundary(lib):
    """Boundary: exact requirement is feasible (tolerance), below is not."""
    req = c2_transfer_requirement_s(10.0, lib, MarginPads.degenerate_anchor(), maneuver_s=4.0)
    need = req["requirement_s"]
    assert c2_transfer_ok(0.0, need, 10.0, lib, MarginPads.degenerate_anchor(), maneuver_s=4.0)
    assert not c2_transfer_ok(0.0, need - 0.5, 10.0, lib, MarginPads.degenerate_anchor(), maneuver_s=4.0)


# ── C3/C4 (D09-2/3/4) ────────────────────────────────────────────────────

def test_c3_weights_ordering_and_normalization(lib):
    """Finer mode weighs more; at the envelope reference the finest mode
    saturates to exactly 1.0 (normalization is non-degenerate)."""
    t_env = None
    from sss_core.predicates import _t_env_max

    t_env = _t_env_max(lib)
    e_spt = c3_energy_normalized(Mode.SPT, t_env, lib)
    assert e_spt == pytest.approx(1.0)  # envelope reference saturates
    assert c3_energy_normalized(Mode.STR, t_env, lib) < 1.0
    assert c3_ok(Mode.STR, t_env, lib)
    assert c3_ok(Mode.SPT, t_env * 0.999, lib)  # just inside the envelope
    assert not c3_ok(Mode.SPT, t_env * 1.01, lib)  # beyond it -> violation


def test_c4_chain_bytes_and_mode_blind(lib):
    """D09-2: bytes = PRF*T*N_r*3*2/8; mode-blind under one PRF (D09-4)."""
    b = c4_memory_bytes(Mode.STR, 5.0, 0.5, 3630.0, lib)
    assert b == pytest.approx(3630.0 * 5.0 * 10000 * 3 * 2 / 8)
    assert c4_memory_bytes(Mode.SLS, 5.0, 0.5, 3630.0, lib) == b
    n = c4_memory_normalized(Mode.STR, 5.0, 0.5, 3630.0, lib)
    # Ticket 15: the envelope reference moved from the 12 deg platform edge
    # (6.7178 s, argmax SLS) to the per-mode envelope (10.5830 s, argmax SPT
    # at 45 deg) -- a 1.5754x rescale.  Both ends of this test are re-pinned
    # to that reference, not loosened: 5 s still sits inside it, and the
    # "beyond" probe has to move past 10.583 s.
    assert 0.0 < n < 1.0  # 5 s sits inside the 10.58 s envelope reference
    assert c4_ok(Mode.STR, 5.0, 0.5, 3630.0, lib)
    assert not c4_ok(Mode.STR, 11.5, 0.5, 3630.0, lib)  # beyond the envelope
    # the reference itself is pinned, so a future silent move turns red
    from sss_core.predicates import _t_env_max as _env_ref
    assert _env_ref(lib) == pytest.approx(10.5830, rel=1e-4)


# ── conflict predicate (D09-7) ───────────────────────────────────────────

def test_schedule_conflict_bare_intervals():
    """Back-to-back is NOT a conflict (strict inequalities); the maneuver
    gap belongs to C2 (two layers, no double counting)."""
    assert not schedule_conflict(0.0, 5.0, 5.0, 5.0)
    assert schedule_conflict(0.0, 5.0, 4.9, 5.0)
    assert schedule_conflict(1.0, 5.0, 0.0, 2.0)


# ── calibration JSON frozen (D09-5) ──────────────────────────────────────

def test_calibration_json_frozen_records():
    import json

    path = FORK_DOMAIN / "experiments" / "predicates_calibration.json"
    cal = json.loads(path.read_text(encoding="utf-8"))
    assert cal["meta"]["frozen_by"].startswith("ticket 09")
    assert "pad_object" in cal["c2_transfer"]
    assert cal["c3_energy"]["weights"]["SPT"] == 1.3
    assert cal["c4_memory"]["bits_per_component"] == 3
    assert cal["c4_memory"]["range_samples_nr"] == 10000
    assert "mode_blind_statement" in cal["c4_memory"]


# ── architecture guard: single predicate source (D09-6) ──────────────────

def test_single_predicate_source_no_duplicate_definitions():
    """Every predicate in predicates.__all__ (plus the window atoms) must be
    defined exactly once across sss_core -- the precompile atoms live in
    windows.py, the coupled predicates in predicates.py, nowhere else."""
    names = sorted(set(pred.__all__) | {"feasible_at", "window_end_ok", "footprint_ok",
                                        "scan_span_reachable", "scan_rate_ok"})
    root = FORK_DOMAIN / "sss_core"
    offenders = []
    for py in root.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        src = py.read_text(encoding="utf-8")
        for name in names:
            for line in src.splitlines():
                s = line.strip()
                if s.startswith(f"def {name}(") and py.name != _owner_file(name):
                    offenders.append(f"{py.name}: {s}")
    assert not offenders, offenders


def _owner_file(name: str) -> str:
    return "predicates.py" if name in pred.__all__ else "windows.py"


def test_window_atoms_resolve_to_fork_modules():
    """The live consumer (scenario generator) must import its window atoms
    from sss_core.windows -- not a copied local definition (D09-6)."""
    import sss_core.scenarios as sc
    import sss_core.windows as win

    assert sc.footprint_ok is win.footprint_ok
    assert inspect.getsourcefile(sc.footprint_ok) == inspect.getsourcefile(win.footprint_ok)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
