#!/usr/bin/env python3
"""Fork identity guard for the NESZ cos^3 kernel (ADR GRILL-002 MUST M2, ticket 02).

Locks the first forked formula copy (FORK_MANIFEST.md item F-01,
sss_core/metrics/nesz.py <- src/sar_sim/metrics/nesz.py):

  * anti-alias: the fork module and the shared module must resolve to two
    DIFFERENT files (guards against a same-name package winning the import
    race under dual sys.path insertion, which would make every identity
    check below compare the module against itself -- always green);
  * identity: fork implementation == shared implementation on fixed fixture
    inputs (exact float equality; both bodies perform the identical op
    sequence, so any drift -- even one ULP -- fails the guard);
  * self-containment: the fork file must not import from `sar_sim`
    (runtime dependency on the shared lib is forbidden by the fork design);
  * scope: the fork file defines exactly the manifest-listed symbols and
    none of the shared-only ones (minimal copy surface, manifest-bound).

Run (repo root):
    PYTHONPATH=src "/d/Program Files/Python/python" -m pytest \
        papers/sliding-spotlight-scheduling/tests/test_fork_identity_nesz.py -v
"""
import re
import sys
from pathlib import Path

import numpy as np
import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent   # papers/sliding-spotlight-scheduling
REPO = FORK_DOMAIN.parent.parent                       # repo root

sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(FORK_DOMAIN))

import sar_sim.metrics.nesz as shared_nesz  # noqa: E402
import sss_core.metrics.nesz as fork_nesz   # noqa: E402

# Fixed fixture inputs: incidence angles 0..85 deg plus the two branch
# edges of the cos^3 kernel (grazing limit where cos(theta) <= 1e-15).
THETAS = np.concatenate([
    np.linspace(0.0, np.radians(85.0), 171),
    np.array([np.radians(89.9999999), np.pi / 2]),
])

# Manifest F-01 scope (must stay in sync with FORK_MANIFEST.md).
FORK_SYMBOLS = {"nesz_linear", "nesz_db", "quality_score"}
SHARED_ONLY_SYMBOLS = {
    "elevation_to_off_nadir",
    "incidence_to_elevation",
    "off_nadir_to_incidence",
    "incidence_to_off_nadir",
    "aggregate_quality",
    "quality_summary",
}


# ── anti-alias guard ─────────────────────────────────────────────────────

def test_guard_anti_alias_modules_distinct():
    """Fork and shared modules must be two different files on disk."""
    fork_file = Path(fork_nesz.__file__).resolve()
    shared_file = Path(shared_nesz.__file__).resolve()
    assert fork_file != shared_file, (
        "anti-alias violation: fork and shared NESZ resolve to the same file "
        f"({fork_file}) -- import race / name collision, identity checks below "
        "would compare the module against itself"
    )
    # Fork copy lives inside the paper domain; shared copy under src/sar_sim.
    assert "sliding-spotlight-scheduling" in fork_file.parts
    assert fork_file.name == "nesz.py"
    shared_parts = shared_file.parts
    assert "src" in shared_parts and "sar_sim" in shared_parts, (
        f"shared NESZ no longer resolves under src/sar_sim: {shared_file}"
    )


def test_guard_anti_alias_sys_modules_keys_distinct():
    """Both fully-qualified names registered in sys.modules, distinct files."""
    assert "sar_sim.metrics.nesz" in sys.modules
    assert "sss_core.metrics.nesz" in sys.modules
    f_shared = Path(sys.modules["sar_sim.metrics.nesz"].__file__).resolve()
    f_fork = Path(sys.modules["sss_core.metrics.nesz"].__file__).resolve()
    assert f_shared != f_fork


# ── numeric identity guards (fixed inputs, exact equality) ───────────────

def test_fork_nesz_linear_matches_shared():
    """nesz_linear: fork == shared bit-for-bit on the fixed fixture grid."""
    for theta in THETAS:
        assert fork_nesz.nesz_linear(float(theta)) == shared_nesz.nesz_linear(float(theta))
    # Non-default K_NESZ path.
    assert fork_nesz.nesz_linear(0.4, K_NESZ=2.5e-3) == shared_nesz.nesz_linear(0.4, K_NESZ=2.5e-3)
    # Grazing branch: both must be +inf.
    assert fork_nesz.nesz_linear(np.pi / 2) == float("inf")
    assert shared_nesz.nesz_linear(np.pi / 2) == float("inf")


def test_fork_nesz_db_matches_shared():
    """nesz_db: fork == shared bit-for-bit on the fixed fixture grid."""
    for theta in THETAS:
        assert fork_nesz.nesz_db(float(theta)) == shared_nesz.nesz_db(float(theta))


def test_fork_quality_score_matches_shared():
    """quality_score: fork == shared bit-for-bit on the fixed fixture grid."""
    for theta in THETAS:
        assert fork_nesz.quality_score(float(theta)) == shared_nesz.quality_score(float(theta))
    # Sanity of the cos^3 normalization itself: q(theta_ref) == 1 exactly.
    assert fork_nesz.quality_score(fork_nesz._THETA_REF) == 1.0


# ── self-containment and manifest scope guards ───────────────────────────

def test_fork_self_contained_no_sar_sim_import():
    """Fork source must not import the shared library (fork isolation)."""
    src = (FORK_DOMAIN / "sss_core" / "metrics" / "nesz.py").read_text(encoding="utf-8")
    assert not re.search(r"^\s*(from|import)\s+sar_sim\b", src, re.MULTILINE), (
        "fork file imports from sar_sim -- runtime dependency on the shared "
        "library breaks fork isolation (ADR GRILL-002)"
    )


def test_fork_scope_matches_manifest_f01():
    """Fork defines exactly the manifest F-01 symbols, none of the shared-only ones."""
    for name in FORK_SYMBOLS:
        assert hasattr(fork_nesz, name), f"manifest F-01 symbol missing in fork: {name}"
    for name in SHARED_ONLY_SYMBOLS:
        assert not hasattr(fork_nesz, name), (
            f"shared-only symbol {name} appeared in fork -- outside manifest "
            "F-01 copy scope; write it back to FORK_MANIFEST.md first"
        )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
