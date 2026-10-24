#!/usr/bin/env python3
"""Ticket 50 phase 5 (final-review R1) -- mutation tests for the L8 gate.

The 2026-10-21 independent final review mutated 14 manuscript numbers and 8
slipped through with the gate still rc=0: the checker asserted only the FIRST
number of each sentence, while the results section packs several readings
into one sentence.  These tests inject one wrong value at a time into the
real manuscript text and require the gate to fail, then re-check the
untouched text and require it to pass.  The 8 values the review missed are
all in the list; no tolerance was relaxed to make them pass.

The expectations are recomputed once per module from the raw sweep units
(including the expensive delivered-caliber path), so every probe runs against
the same in-memory gate the CLI uses.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

FORK = Path(__file__).resolve().parent.parent
SCRIPT = FORK / "scripts" / "verify_paper_numbers_l8.py"
MAIN = FORK / "paper" / "main.tex"
FULL = FORK / "paper" / "full.md"
sys.path.insert(0, str(FORK / "scripts"))

import verify_paper_numbers_l8 as v8  # noqa: E402
from verify_t55_group import (  # noqa: E402
    check_t55 as _check_t55,
    t55_expectations as _t55_exp,
)

_T55_CACHE = None


def t55():
    global _T55_CACHE
    if _T55_CACHE is None:
        _T55_CACHE = _t55_exp()
    return _T55_CACHE

MAIN_TEXT = MAIN.read_text(encoding="utf-8")
FULL_TEXT = FULL.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def exp():
    return v8.recompute(need_deliv=True)


_T54_CACHE = None


def t54():
    global _T54_CACHE
    if _T54_CACHE is None:
        e = v8.recompute(need_deliv=True)
        _T54_CACHE = v8.t54_expectations(
            served_instances=e["served_task_instances"][0],
            cost_r3h=abs(e["coverage_cost_pp"]["R3H"][0]),
            cost_r2f=abs(e["coverage_cost_pp"]["R2F"][0]))
    return _T54_CACHE


# (paper_path, text, anchor, wrong_value) -- the anchor is the exact string
# in the file whose first occurrence is mutated (replace with count=1).
PROBES = [
    # --- the 8 values the final review mutated and the old gate missed -----
    (MAIN, MAIN_TEXT, "0.6884 at $s=0.9$", "0.1111 at $s=0.9$"),
    (MAIN, MAIN_TEXT, "0.9766 at $s=1.1$", "0.1111 at $s=1.1$"),
    (MAIN, MAIN_TEXT, "0.9812 at $s=1.2$", "0.1111 at $s=1.2$"),
    (MAIN, MAIN_TEXT, "0.9924 at $s=1.4$", "0.1111 at $s=1.4$"),
    (MAIN, MAIN_TEXT, "0.7764 for R2F", "0.1111 for R2F"),
    (MAIN, MAIN_TEXT, "0.7447 for R3H", "0.1111 for R3H"),
    (MAIN, MAIN_TEXT, r"51.14\% for the control family",
     r"22.22\% for the control family"),
    # --- further probes: every reading class must be mutation-sensitive ----
    (MAIN, MAIN_TEXT, "0.9764 at $s=1.0$", "0.1111 at $s=1.0$"),
    (MAIN, MAIN_TEXT, "0.5398 at $s=0.9$", "0.1111 at $s=0.9$"),
    (MAIN, MAIN_TEXT, "cost of 4.15 percentage points",
     "cost of 9.99 percentage points"),
    (MAIN, MAIN_TEXT, "cost of 2.36 percentage points",
     "cost of 9.99 percentage points"),
    (MAIN, MAIN_TEXT, "477,308 task instances", "1,111 task instances"),
    (MAIN, MAIN_TEXT, "0.268 percentage points between",
     "0.777 percentage points between"),
    (MAIN, MAIN_TEXT, "0.359 percentage points between",
     "0.777 percentage points between"),
    (MAIN, MAIN_TEXT, "one loses 1.83 percentage points",
     "one loses 9.99 percentage points"),
    (MAIN, MAIN_TEXT, "a different seed loses 1.14",
     "a different seed loses 9.99"),
    (MAIN, MAIN_TEXT, "9,430 tie-set records", "9,999 tie-set records"),
    (MAIN, MAIN_TEXT, "in 258 of 260 units", "in 111 of 260 units"),
    (MAIN, MAIN_TEXT, "2.4669$~m", "9.9999$~m"),
    (MAIN, MAIN_TEXT, "0.5000$~m", "9.9999$~m"),
    (MAIN, MAIN_TEXT, "0.3000$~m", "9.9999$~m"),
    (MAIN, MAIN_TEXT, "180 sweep units", "181 sweep units"),
    (MAIN, MAIN_TEXT, "270 launched units", "271 launched units"),
    (MAIN, MAIN_TEXT, "over every record is 0.0", "over every record is 5.5"),
    (MAIN, MAIN_TEXT, "0.9485 at the as-placed point", "0.1111 at the as-placed point"),
    (MAIN, MAIN_TEXT, "0.4827 at $s=0.8$", "0.1111 at $s=0.8$"),
    (MAIN, MAIN_TEXT, "0.9900 at $s=1.5$", "0.1111 at $s=1.5$"),
    (MAIN, MAIN_TEXT, "0.9882 at $s=1.3$", "0.1111 at $s=1.3$"),
    (MAIN, MAIN_TEXT, "1.0000 at $s=2.0$", "0.5555 at $s=2.0$"),
    (MAIN, MAIN_TEXT, "1.0000 from $s=1.0$", "0.5555 from $s=1.0$"),
    (MAIN, MAIN_TEXT, "0.6580 for R1C", "0.1111 for R1C"),
    (MAIN, MAIN_TEXT, r"100.00\% for the 50-task family",
     r"22.22\% for the 50-task family"),
    (MAIN, MAIN_TEXT, r"71.00\% for the 100-task family",
     r"22.22\% for the 100-task family"),
    (MAIN, MAIN_TEXT, "drops 26.0 percentage points from the as-placed",
     "drops 9.99 percentage points from the as-placed"),
    (MAIN, MAIN_TEXT, "0.501 & 0.483", "0.999 & 0.483"),
    (MAIN, MAIN_TEXT, "18.25 and 30.44 percentage points",
     "9.99 and 30.44 percentage points"),
    (MAIN, MAIN_TEXT, "median 2.409~s, range", "median 9.99~s, range"),
    # --- the markdown face (plain %, same classes) -------------------------
    (FULL, FULL_TEXT, "0.7764 for R2F", "0.1111 for R2F"),
    (FULL, FULL_TEXT, "51.14% for the control family",
     "22.22% for the control family"),
    (FULL, FULL_TEXT, "0.9924 at $s=1.4$", "0.1111 at $s=1.4$"),
    # --- R50: the printed per-mode f_q constants and their ratios ---------
    (MAIN, MAIN_TEXT, "$0.8107$ (STR)", "$0.1111$ (STR)"),
    (MAIN, MAIN_TEXT, "$19.7352$ (SLS)", "$11.1111$ (SLS)"),
    (MAIN, MAIN_TEXT, "$54.8322$ (SPT)", "$44.4444$ (SPT)"),
    (MAIN, MAIN_TEXT, "$24.3\\times$ (SLS over STR)",
     "$99.9\\times$ (SLS over STR)"),
    (MAIN, MAIN_TEXT, "$67.6\\times$ (SPT over STR)",
     "$99.9\\times$ (SPT over STR)"),
    (MAIN, MAIN_TEXT, "$2.8\\times$ (SPT over SLS)",
     "$99.9\\times$ (SPT over SLS)"),
    # --- T55 reanalysis numbers (2026-10-24 panel fixes) -----------------
    (MAIN, MAIN_TEXT, "only to 17.06 and 30.11", "only to 9.99 and 30.11"),
    (MAIN, MAIN_TEXT, "50-task gap to 7.08", "50-task gap to 9.99"),
    (MAIN, MAIN_TEXT, "100-task gap to 25.33", "100-task gap to 9.99"),
    (MAIN, MAIN_TEXT, "0.9766 to 0.9833 at $s=1.1$",
     "0.9766 to 0.9999 at $s=1.1$"),
    (MAIN, MAIN_TEXT, "reads a median of 0.568", "reads a median of 0.999"),
    (MAIN, MAIN_TEXT, "reads a partial 0.469", "reads a partial 0.999"),
    (MAIN, MAIN_TEXT, "measured to exceed the library reference by up to $1.2008",
     "measured to exceed the library reference by up to $9.9999"),
    (MAIN, MAIN_TEXT, "s^{*}=2.4669/(3.0/1.1)=0.905",
     "s^{*}=2.4669/(3.0/1.1)=0.999"),
    (FULL, FULL_TEXT, "only to 17.06 and 30.11", "only to 9.99 and 30.11"),
    (FULL, FULL_TEXT, "0.9766 to 0.9833 at $s=1.1$",
     "0.9766 to 0.9999 at $s=1.1$"),
    (FULL, FULL_TEXT, "0.8107$ (STR)", "0.1111$ (STR)"),
]


@pytest.mark.parametrize(
    "paper,text,anchor,wrong",
    [pytest.param(p, t, a, w, id=f"{p.name}:{a[:28]}") for p, t, a, w in PROBES],
)
def test_each_probe_mutation_is_caught_and_restore_is_clean(exp, paper, text,
                                                            anchor, wrong):
    assert anchor in text, f"probe anchor missing from {paper.name}: {anchor}"
    mutated = text.replace(anchor, wrong, 1)
    assert mutated != text, "mutation did not change the text"

    fails, _passes, _notes, _seen = v8.check_paper(mutated, paper.name, exp)
    f54, _p54, _s54 = v8.check_t54(mutated, paper.name, t54())
    f55, _p55, _s55 = _check_t55(mutated, paper.name, t55())
    fails = list(fails) + list(f54) + list(f55)
    assert fails, f"mutating {anchor!r} was NOT caught"

    fails0, passes0, _notes0, seen0 = v8.check_paper(text, paper.name, exp)
    assert not fails0, fails0
    assert seen0 > 0
    assert passes0, "restored text scored nothing -- extraction is dead"


def test_the_original_manuscripts_pass_unchanged(exp):
    for paper, text in ((MAIN, MAIN_TEXT), (FULL, FULL_TEXT)):
        fails, _passes, _notes, seen = v8.check_paper(text, paper.name, exp)
        assert not fails, fails
        assert seen >= 60, f"{paper.name}: expected the expanded coverage"


def test_cli_rc_is_one_for_a_wrong_value_and_zero_restored(tmp_path):
    """The CLI's exit code, not just check_paper's fail list."""
    bad = tmp_path / "bad.tex"
    good = tmp_path / "good.tex"
    bad.write_text(MAIN_TEXT.replace("0.6884 at $s=0.9$",
                                     "0.1111 at $s=0.9$", 1),
                   encoding="utf-8", newline="")
    good.write_text(MAIN_TEXT, encoding="utf-8", newline="")

    env = dict(os.environ, PYTHONHASHSEED="0")
    argv = [sys.executable, "-B", str(SCRIPT), "--paper", str(bad)]
    r = subprocess.run(argv, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env,
                       cwd=str(FORK.parent.parent))
    assert r.returncode == 1, r.stdout[-2000:]
    assert "0.6884" in r.stdout or "0.1111" in r.stdout

    argv = [sys.executable, "-B", str(SCRIPT), "--paper", str(good)]
    r = subprocess.run(argv, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env,
                       cwd=str(FORK.parent.parent))
    assert r.returncode == 0, r.stdout[-2000:]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
