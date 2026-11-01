#!/usr/bin/env python3
"""Guards for the R5/R6 check group.

Two jobs:

1. Pin the local AASR integrator in ``verify_r56_group`` to the registered
   one.  The group needs a scene-extent switch that ``sss_core.aasr`` does
   not have, so it carries a copy; at the base setting the copy must equal
   ``aasr_direct`` exactly, or a re-registration of D06-1/D06-3 would let the
   gate drift from the model it verifies.

2. Pin the group's discrimination.  A presence test over a paragraph's
   number set cannot see a swap, so every mutation class that broke an
   earlier version is a test here: reversed endpoint pairs, exchanged
   mapping values, exchanged mode groups, exchanged labels, an inverted
   direction sentence, a deleted monotonicity claim, and a decoy number
   planted in a cross-reference ("as Section 4.9 sets out").
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))
sys.path.insert(0, str(FORK / "scripts"))

import verify_r56_group as r56  # noqa: E402
from sss_core.aasr import aasr_direct  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402

MAIN = FORK / "paper" / "main.tex"
TEXT = MAIN.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def exp():
    return r56.r56_expectations()


@pytest.mark.parametrize("mode", [Mode.STR, Mode.SLS])
@pytest.mark.parametrize("psi_deg", [0.0, 6.0, 12.0, 18.0, 26.0])
def test_the_copy_matches_the_registered_integral(mode, psi_deg):
    lib = ModeLibrary.from_fixture()
    psi = math.radians(psi_deg)
    reg = aasr_direct(mode, psi, lib.geo.k, r56.PRF_HZ, lib)["aasr_db"]
    copy = r56._aasr(lib, mode, psi)
    assert copy == pytest.approx(reg, abs=1e-9), (
        f"the R5 group's integrator has drifted from sss_core.aasr at "
        f"{mode.name}/{psi_deg} deg: {copy} vs {reg}")


def test_the_unmutated_manuscript_passes(exp):
    fails, _passes, seen = r56.check_r56(TEXT, "main.tex", exp)
    assert fails == []
    assert seen >= r56.R56_MIN_CHECKS


MUTATIONS = {
    "endpoint pair reversed": (
        "$-16.45$ to $-20.22$", "$-20.22$ to $-16.45$"),
    "mapping values exchanged": (
        "$-19.38$ and $-18.87$", "$-18.87$ and $-19.38$"),
    "stripmap mapping values exchanged": (
        "$-5.17$ and $-3.88$", "$-3.88$ and $-5.17$"),
    "mode groups exchanged": (
        "$-16.45$ to $-20.22$, $-19.38$ and $-18.87$~dB for sliding spotlight "
        "and $-2.78$ to $-7.74$, $-5.17$ and $-3.88$~dB for stripmap",
        "$-2.78$ to $-7.74$, $-5.17$ and $-3.88$~dB for sliding spotlight "
        "and $-16.45$ to $-20.22$, $-19.38$ and $-18.87$~dB for stripmap"),
    "level-shift labels exchanged": (
        "by $+4.9$~dB (sliding spotlight) and $+18.6$~dB (stripmap)",
        "by $+18.6$~dB (sliding spotlight) and $+4.9$~dB (stripmap)"),
    "direction sentence inverted": (
        "no mapping of it reverses the direction",
        "every mapping of it reverses the direction"),
    "monotonicity claim deleted": ("monotone at $2^{\\circ}$ steps, ", ""),
    "decoy number in a cross-reference": (
        "by $+4.9$~dB (sliding spotlight)",
        "by $+6.1$~dB (sliding spotlight); as Section 4.9 sets out for the "
        "sliding case"),
    "R6 mode labels exchanged": (
        "$1.045$ (spotlight)", "$1.008$ (spotlight)"),
    "one endpoint falsified": ("$-3.88$~dB", "$-3.98$~dB"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_each_mutation_is_caught(exp, name):
    anchor, replacement = MUTATIONS[name]
    assert anchor in TEXT, f"probe anchor vanished from the manuscript: {name}"
    mutated = TEXT.replace(anchor, replacement, 1)
    assert mutated != TEXT
    fails, _passes, _seen = r56.check_r56(mutated, "main.tex", exp)
    assert fails, f"the gate did not catch the mutation: {name}"


def test_a_missing_anchor_fails_by_default(exp, monkeypatch):
    monkeypatch.delenv("L8_R56_OPTIONAL", raising=False)
    mutated = TEXT.replace("target-side Doppler occupancy", "scene occupancy", 1)
    fails, _p, _s = r56.check_r56(mutated, "main.tex", exp)
    assert any("anchor paragraph" in f for f in fails)


def test_the_optional_flag_silences_a_synthetic_manuscript(exp, monkeypatch):
    monkeypatch.setenv("L8_R56_OPTIONAL", "1")
    fails, _p, seen = r56.check_r56("A synthetic manuscript with no anchors.",
                                    "synthetic", exp)
    assert fails == [] and seen == 0


def test_model_invariants_are_reported_not_counted(exp):
    ok, bad = r56.r5_invariants(exp)
    assert bad == [] and len(ok) == 7
    _f, _p, seen = r56.check_r56(TEXT, "main.tex", exp)
    assert seen == r56.R56_MIN_CHECKS  # the 14 manuscript checks, no more
