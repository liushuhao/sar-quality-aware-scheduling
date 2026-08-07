#!/usr/bin/env python3
"""Guard tests for the cross-family provenance invariant (fault mode 2b).

Covers:
  * _provenance.check_pkl_sha1_consistency — mismatch hard-fails, all-missing
    warns-but-passes, all-agree passes.
  * runner resume-by-pkl_sha1 — a stale entry (old sha) is recomputed, not
    skipped; a matching entry is skipped.

Run: python -m pytest test_provenance_guard.py -v
"""
import os
import sys
import types
from pathlib import Path

import pytest

EXP = Path(__file__).resolve().parent
sys.path.insert(0, str(EXP))

from _provenance import check_pkl_sha1_consistency  # noqa: E402


# ── check_pkl_sha1_consistency ──────────────────────────────────────────

def test_check_all_agree(capsys):
    """Same sha across two sources → no error, no unverifiable."""
    n_mis, n_unv = check_pkl_sha1_consistency({
        "A": {"S1/x.pkl": "abc123", "S1/y.pkl": "def456"},
        "B": {"S1/x.pkl": "abc123", "S1/y.pkl": "def456"},
    }, label="unit")
    assert n_mis == 0
    assert n_unv == 0


def test_check_mismatch_exits(capsys):
    """Different sha for the same key across sources → sys.exit(1)."""
    with pytest.raises(SystemExit) as ei:
        check_pkl_sha1_consistency({
            "A": {"S1/x.pkl": "abc123"},
            "B": {"S1/x.pkl": "ffffff"},
        }, label="unit")
    assert ei.value.code == 1
    err = capsys.readouterr().err
    assert "MISMATCH" in err and "S1/x.pkl" in err


def test_check_all_missing_passes(capsys):
    """No source has sha (legacy data) → warn, but do not fail."""
    n_mis, n_unv = check_pkl_sha1_consistency({
        "A": {"S1/x.pkl": None},
        "B": {"S1/x.pkl": None},
    }, label="unit")
    assert n_mis == 0
    assert n_unv == 1
    assert "warn" in capsys.readouterr().out.lower()


def test_check_partial_missing_is_unverifiable(capsys):
    """One source has sha, another doesn't for same key → unverifiable."""
    n_mis, n_unv = check_pkl_sha1_consistency({
        "A": {"S1/x.pkl": "abc123"},
        "B": {"S1/x.pkl": None},
    }, label="unit")
    assert n_mis == 0
    assert n_unv == 1  # can't prove mismatch, can't prove equality


# ── runner resume-by-sha1 ───────────────────────────────────────────────

def _make_runner_module(name, *, entry_template):
    """Build a minimal in-memory module mimicking a runner's main resume loop.

    The real runners share this exact resume pattern:
        if key in completed and completed[key].get("pkl_sha1") == _pkl_sha1(fpath):
            continue
    We replicate it here to lock the invariant without running the (expensive)
    solvers, and assert the production files still contain that guard line.
    """
    mod = types.ModuleType(name)

    def _pkl_sha1(fpath):
        # fpath is a string whose "bytes" we treat as its sha
        return f"sha-of-{fpath}"

    def run_loop(completed, fpaths):
        recomputed = []
        for fpath in fpaths:
            key = f"S1/{fpath}.pkl"
            if key in completed and completed[key].get("pkl_sha1") == _pkl_sha1(fpath):
                continue  # cached, same pkl
            # would call run_one here
            completed[key] = {**entry_template, "pkl_sha1": _pkl_sha1(fpath)}
            recomputed.append(key)
        return completed, recomputed

    mod._pkl_sha1 = _pkl_sha1
    mod.run_loop = run_loop
    return mod


def test_resume_skips_matching_sha():
    mod = _make_runner_module("fake_runner_match", entry_template={"f1": 1.0})
    completed = {"S1/a.pkl": {"f1": 1.0, "pkl_sha1": "sha-of-a"}}
    completed, recomputed = mod.run_loop(completed, ["a", "b"])
    assert "S1/a.pkl" not in recomputed          # skipped (sha matches)
    assert "S1/b.pkl" in recomputed              # new scenario computed
    assert completed["S1/a.pkl"]["pkl_sha1"] == "sha-of-a"


def test_resume_recomputes_stale_sha():
    """A cached entry whose pkl changed must be recomputed, not silently kept."""
    mod = _make_runner_module("fake_runner_stale", entry_template={"f1": 1.0})
    completed = {"S1/a.pkl": {"f1": 0.5, "pkl_sha1": "OLD-STALE-SHA"}}
    completed, recomputed = mod.run_loop(completed, ["a"])
    assert "S1/a.pkl" in recomputed             # stale → recomputed
    assert completed["S1/a.pkl"]["pkl_sha1"] == "sha-of-a"
    assert completed["S1/a.pkl"]["f1"] == 1.0   # fresh value overwrites stale


def test_resume_legacy_entry_without_sha_recomputed():
    """A cached entry with no pkl_sha1 field (old data) must be recomputed."""
    mod = _make_runner_module("fake_runner_legacy", entry_template={"f1": 1.0})
    completed = {"S1/a.pkl": {"f1": 0.5}}  # legacy: no pkl_sha1 key
    completed, recomputed = mod.run_loop(completed, ["a"])
    assert "S1/a.pkl" in recomputed
    assert "pkl_sha1" in completed["S1/a.pkl"]


# ── production-file guard: the resume line must exist in every runner ────

RUNNER_FILES = [
    "run_so_f1_bl.py",
    "run_moea_2obj.py",
    "run_moea_3obj.py",
    "run_moea_3obj_no_incidence.py",
    "run_moea_3obj_no_physics.py",
    "run_moea_3obj_no_squint.py",
    "run_baselines_v4.py",
    "run_baselines_S7S8.py",
    "run_sigma_sweep.py",
]


@pytest.mark.parametrize("fname", RUNNER_FILES)
def test_runner_has_pkl_sha1_resume_guard(fname):
    """Every runner's resume loop must gate on pkl_sha1, not key presence alone."""
    src = (EXP / fname).read_text(encoding="utf-8")
    assert "pkl_sha1" in src, f"{fname} does not reference pkl_sha1"
    # The resume guard must compare the stored sha against the current pkl.
    # Right-hand side may be _pkl_sha1(fpath) or a precomputed cur_sha var.
    assert '.get("pkl_sha1") ==' in src, \
        f"{fname} missing the pkl_sha1 resume guard comparison"


def test_downstream_consumers_call_provenance_guard():
    """Merge scripts must invoke the cross-family provenance check."""
    for fname in ["statistical_analysis.py", "recompute_scale_sensitivity.py",
                  "analyze_ablation.py", "gen_fig6_ablation.py"]:
        src = (EXP / fname).read_text(encoding="utf-8")
        assert "check_pkl_sha1_consistency" in src, \
            f"{fname} does not call check_pkl_sha1_consistency"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
