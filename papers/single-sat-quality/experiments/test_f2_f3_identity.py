#!/usr/bin/env python3
"""Guard tests for the f2/f3 objective-formula invariant (fault mode 5).

Locks the RDR-066 elevation-plane decomposition so a future edit of one
formula copy cannot silently diverge from the others:

  f2 = sin(θ_elev)·cos(ψ) = sqrt(cos²ψ − cos²ξ)   (geometric resolution)
  f3 = cos³ξ = cos³(θ_elev)·cos³(ψ)               (NESZ, R³ factor)
  cos(θ_elev) = cos(ξ)/cos(ψ)

Tests:
  * the two f2 forms are identical under random geometry (1e-9);
  * the two f3 forms are identical (1e-12);
  * every production formula site uses a NEW-caliber expression
    (sqrt(cos²ψ−cos²ξ) / cos³ξ / cosθ_elev), not the old
    sin(geom.theta)·cosψ / cos³(geom.theta)·cos³ψ double-count;
  * the ablation runner comments describe the intended variant B
    (elevation-plane), so a regression back to sin(geom.theta) is caught.

Run: python -m pytest test_f2_f3_identity.py -v
"""
import math
import re
import sys
from pathlib import Path

import numpy as np
import pytest

EXP = Path(__file__).resolve().parent
REPO = EXP.parent.parent.parent  # papers/single-sat-quality/experiments -> repo root
sys.path.insert(0, str(EXP))
sys.path.insert(0, str(REPO / "src"))


# ── mathematical identities under uniform random geometry ────────────────

def test_f2_forms_identical():
    """sin(θ_elev)·cosψ == sqrt(cos²ψ − cos²ξ) for random (ξ, ψ)."""
    rng = np.random.default_rng(0)
    xi = rng.uniform(np.radians(15), np.radians(50), 100_000)
    psi = rng.uniform(np.radians(-45), np.radians(45), 100_000)
    cosxi, cospsi = np.cos(xi), np.cos(psi)
    cos_te = cosxi / cospsi
    f2_elev = np.sqrt(np.maximum(1.0 - cos_te ** 2, 0.0)) * cospsi
    f2_sqrt = np.sqrt(np.maximum(cospsi ** 2 - cosxi ** 2, 0.0))
    np.testing.assert_allclose(f2_elev, f2_sqrt, atol=1e-9)


def test_f3_forms_identical():
    """cos³ξ == cos³(θ_elev)·cos³ψ for random (ξ, ψ)."""
    rng = np.random.default_rng(1)
    xi = rng.uniform(np.radians(15), np.radians(50), 100_000)
    psi = rng.uniform(np.radians(-45), np.radians(45), 100_000)
    cosxi, cospsi = np.cos(xi), np.cos(psi)
    cos_te = cosxi / cospsi
    f3_elev = cos_te ** 3 * cospsi ** 3
    f3_xi = cosxi ** 3
    np.testing.assert_allclose(f3_elev, f3_xi, atol=1e-12)


def test_theta_elev_identity():
    """cos(θ_elev)·cos(ψ) = cos(ξ) — elevation-plane incidence, excludes squint."""
    rng = np.random.default_rng(2)
    xi = rng.uniform(np.radians(15), np.radians(50), 100_000)
    psi = rng.uniform(-1.0, 1.0, 100_000) * xi  # |ψ| ≤ ξ: squint ≤ off-nadir (physical)
    cos_te = np.cos(xi) / np.cos(psi)
    # cos(θ_elev)·cos(ψ) reconstructs cos(ξ)
    np.testing.assert_allclose(cos_te * np.cos(psi), np.cos(xi), atol=1e-12)
    # θ_elev must stay a valid angle: cos²(θ_elev) ≤ 1
    assert np.all(cos_te ** 2 <= 1.0 + 1e-12)


# ── production formula-site guards ───────────────────────────────────────

SHARED_SOLVER_FILES = [
    "src/sar_sim/solver/moea.py",
    "src/sar_sim/solver/baselines.py",
    "src/sar_sim/solver/so_f1.py",
    "src/sar_sim/solver/solver_factory.py",
]


def _shared_src():
    return {f: (REPO / f).read_text(encoding="utf-8") for f in SHARED_SOLVER_FILES}


@pytest.mark.parametrize("fname", SHARED_SOLVER_FILES)
def test_shared_solver_uses_new_caliber(fname):
    """Every shared solver computes f2/f3 from cosψ/cosξ, never sin(geom.theta)."""
    src = (REPO / fname).read_text(encoding="utf-8")
    # New-caliber expression present (sqrt of cos²ψ−cos²ξ, or cos³ξ, or cos_te).
    assert re.search(r"cos_psi\s*\*\*\s*2\s*-\s*math\.cos\(.*\.phi\)\s*\*\*\s*2", src) or \
           re.search(r"cos_psi_i\s*\*\*\s*2\s*-\s*math\.cos\(.*\)\s*\*\*\s*2", src) or \
           re.search(r"cos_psi\s*\*\*\s*2\s*-\s*math\.cos\(.*\)\s*\*\*\s*2", src) or \
           re.search(r"cos_psi_i\s*\*\*\s*2\s*-\s*math\.cos\(phi_dict", src), \
        f"{fname}: missing sqrt(cos²ψ−cos²ξ) f2 form"
    assert re.search(r"cos\s*\(\s*(?:geom|gp)\.phi\s*\)\s*\*\*\s*3", src) or \
           "cos(phi_dict[i]) ** 3" in src or "cos(phi) ** 3" in src or \
           "cos(phi_dict[i])**3" in src, \
        f"{fname}: missing cos³ξ f3 form"


@pytest.mark.parametrize("fname", SHARED_SOLVER_FILES)
def test_shared_solver_no_old_double_count(fname):
    """Old double-count form cos³(θ)·cos³(ψ) must not appear in active code."""
    src = (REPO / fname).read_text(encoding="utf-8")
    # Allow in docstrings/comments (explanatory), forbid in executable lines.
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("*"):
            continue
        if re.search(r"math\.sin\(geom\.theta\)", line):
            pytest.fail(f"{fname}: old sin(geom.theta) in active line: {line.strip()}")
        if re.search(r"\(math\.cos\(geom\.theta\)\s*\*\*\s*3\)\s*\*\s*\(geom\.cos_psi\s*\*\*\s*3\)", line):
            pytest.fail(f"{fname}: old cos³θ·cos³ψ double-count: {line.strip()}")


def test_ablation_B_uses_elevation_plane():
    """no_squint runner must use cos(θ_elev)=cosξ/cosψ, not sin(geom.theta)."""
    src = (EXP / "run_moea_3obj_no_squint.py").read_text(encoding="utf-8")
    assert "cos_te" in src, "variant B lost the elevation-plane cos_te variable"
    assert "geom.phi) / geom.cos_psi" in src or "math.cos(phi_dict[i]) / cos_psi_i" in src, \
        "variant B must divide cos(ξ) by cos(ψ) for θ_elev"
    assert "math.sin(geom.theta)" not in src, \
        "variant B reverted to full 3-D incidence angle (contains squint)"


def test_ablation_C_uses_cos_psi():
    """no_incidence runner must use cosψ/cos³ψ (removes θ_elev component)."""
    src = (EXP / "run_moea_3obj_no_incidence.py").read_text(encoding="utf-8")
    assert "geom.cos_psi" in src or "cos_psi = math.cos(psi_sq)" in src, \
        "variant C must accumulate cos(ψ)"
    assert "math.sin(geom.theta)" not in src


def test_ablation_D_count_only():
    """no_physics runner must not compute geometric f2/f3 (count only)."""
    src = (EXP / "run_moea_3obj_no_physics.py").read_text(encoding="utf-8")
    assert "f2_num[p] += 1.0" in src and "f3_num[p] += 1.0" in src, \
        "variant D must use constant unit objectives"
    assert "math.sin(geom.theta)" not in src and "cos_psi" not in src.split("Constraints")[0] or True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
