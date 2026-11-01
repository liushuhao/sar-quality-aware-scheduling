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

import json
import os
import re
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
    # R104 (2026-11-01): the two values of one sentence exchanged -- the set
    # of printed magnitudes is unchanged, so only a polarity-bound match sees it
    (MAIN, MAIN_TEXT, "one loses 1.83 percentage points and one gains 0.42",
     "one loses 0.42 percentage points and one gains 1.83"),
    (MAIN, MAIN_TEXT, "the same seed gains 0.42 points as in the first dip, "
                      "and a different seed loses 1.14",
     "the same seed gains 1.14 points as in the first dip, "
     "and a different seed loses 0.42"),
    # the mover clauses math-wrapped: before the pattern learned the optional
    # "$", moves_m came back empty and the whole block was skipped silently
    (MAIN, MAIN_TEXT, "one loses 1.83 percentage points",
     "one loses $9.99$ percentage points"),
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
    (MAIN, MAIN_TEXT, "to exceed the library reference by up to $1.2008",
     "to exceed the library reference by up to $9.9999"),
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

    env = dict(os.environ, PYTHONHASHSEED="0", L8_CENSUS_OPTIONAL="1")
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


# ── R105: the cross-dip seed identity claim (2026-11-01) ─────────────────
# The sentence keeps every magnitude and every verb; what changes is WHICH
# seed the text credits.  The registered movers carry their seed ids now, so
# the claim is decidable against the earlier dip instead of passing on the
# magnitudes alone.
IDENT = ("the same seed gains 0.42 points as in the first dip, "
         "and a different seed loses 1.14")


def _fails_of(text):
    fails, _p, _n, _s = v8.check_paper(text, MAIN.name, exp_fixture())
    return fails


_EXP_CACHE = None


def exp_fixture():
    global _EXP_CACHE
    if _EXP_CACHE is None:
        need = bool(v8._DELIV_TOKEN.search(MAIN_TEXT)
                    or re.search(r"squint[-\s]?loss", MAIN_TEXT, re.I))
        _EXP_CACHE = v8.recompute(need_deliv=need)
    return _EXP_CACHE


@pytest.mark.parametrize("mutated", [
    # the two clauses exchange their adjectives: the same magnitudes and verbs,
    # so only a seed-identity check can see it (this was R105's blind spot)
    IDENT.replace("the same seed gains", "a different seed gains").replace(
        "and a different seed loses", "and the same seed loses"),
    # the same-seed clause stops naming the dip it points back to
    IDENT.replace("as in the first dip, ", ""),
], ids=["adjectives-swapped", "prior-dip-dropped"])
def test_r105_identity_mutations_are_caught(mutated):
    assert IDENT in MAIN_TEXT
    text = MAIN_TEXT.replace(IDENT, mutated, 1)
    assert text != MAIN_TEXT
    assert _fails_of(text), f"identity mutation not caught: {mutated!r}"


def test_r105_the_identity_sentence_is_not_a_free_pass():
    """The untouched sentence must score -- an identity claim that the gate
    silently skips is the fail-open shape R104 closed for the magnitudes."""
    assert IDENT in MAIN_TEXT
    assert not _fails_of(MAIN_TEXT)


# ── R106: the reading census (2026-11-01) ────────────────────────────────
CENSUS = FORK / "scripts" / "readings_census.json"


def _registered():
    """The registered value set the CLI folds into the census (exp + T54)."""
    exp = exp_fixture()
    t54 = v8.t54_expectations(
        served_instances=exp["served_task_instances"][0],
        cost_r3h=abs(exp["coverage_cost_pp"]["R3H"][0]),
        cost_r2f=abs(exp["coverage_cost_pp"]["R2F"][0]))
    return v8.registered_values(exp) + v8.registered_values(t54)


def _scored_literals(text):
    v8._CENSUS_COLLECT = []
    try:
        v8.check_paper(text, MAIN.name, exp_fixture())
        return list(v8._CENSUS_COLLECT)
    finally:
        v8._CENSUS_COLLECT = None


def test_r106_untouched_manuscripts_match_their_census():
    reg = json.loads(CENSUS.read_text(encoding="utf-8"))
    for paper, text in ((MAIN, MAIN_TEXT), (FULL, FULL_TEXT)):
        scored = _scored_literals(text)
        assert scored, f"{paper.name}: nothing was scored"
        assert v8.check_census(text, paper.name, scored, reg,
                               paper.suffix.lower() == ".tex",
                               _registered()) == []


@pytest.mark.parametrize("anchor,replacement", [
    # a reprint the sentence-anchored classes never read: the floor is stated
    # seven times in the manuscript and checked once
    ("$2.4669$~m (Section", "$2.4667$~m (Section"),
])
def test_r106_a_reprint_drift_is_caught(anchor, replacement):
    reg = json.loads(CENSUS.read_text(encoding="utf-8"))
    scored = _scored_literals(MAIN_TEXT)
    assert anchor in MAIN_TEXT
    drifted = MAIN_TEXT.replace(anchor, replacement, 1)
    fails = v8.check_census(drifted, MAIN.name, scored, reg, True,
                            _registered())
    assert any("2.4669" in f for f in fails), fails


def test_r106_a_new_reprint_is_caught():
    reg = json.loads(CENSUS.read_text(encoding="utf-8"))
    scored = _scored_literals(MAIN_TEXT)
    doubled = MAIN_TEXT.replace("$2.4669$~m (Section",
                                "$2.4669$~m again and $2.4669$~m (Section", 1)
    fails = v8.check_census(doubled, MAIN.name, scored, reg, True,
                            _registered())
    assert any("2.4669" in f for f in fails), fails


def test_r106_a_file_without_a_census_fails_loud():
    """Silence is the loophole: an unregistered manuscript must not pass the
    census by simply having no entry."""
    reg = json.loads(CENSUS.read_text(encoding="utf-8"))
    scored = _scored_literals(MAIN_TEXT)
    fails = v8.check_census(MAIN_TEXT, "some-other.tex", scored, reg, True,
                            _registered())
    assert any("no reading census registered" in f for f in fails), fails


def test_r106_cli_rc_flips_on_a_reprint_drift(tmp_path):
    """The census must be wired into the exit code, not just available."""
    reg_path = CENSUS
    good_dir = tmp_path / "good"
    bad_dir = tmp_path / "bad"
    good_dir.mkdir()
    bad_dir.mkdir()
    (good_dir / "main.tex").write_text(MAIN_TEXT, encoding="utf-8", newline="")
    (bad_dir / "main.tex").write_text(
        MAIN_TEXT.replace("$2.4669$~m (Section", "$2.4667$~m (Section", 1),
        encoding="utf-8", newline="")
    env = dict(os.environ, PYTHONHASHSEED="0")
    for path, want in ((bad_dir / "main.tex", 1), (good_dir / "main.tex", 0)):
        r = subprocess.run([sys.executable, "-B", str(SCRIPT), "--paper",
                            str(path)], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env,
                           cwd=str(FORK.parent.parent))
        assert r.returncode == want, r.stdout[-2000:]
    assert reg_path.is_file()


# ── follow-ups from the 2026-11-01 independent review ────────────────────
# Each of these passed the first cut of R105/R106 with rc=0; they are the
# fail-open shapes the review measured, kept as probes so they cannot return.

def test_a_period_before_the_identity_clause_cannot_hide_it():
    """Splitting the sentence must fail loud, not drop the movers (the review
    measured seen 73 -> 71 with rc=0)."""
    assert "recurs --- the same seed gains" in MAIN_TEXT
    split = MAIN_TEXT.replace("recurs --- the same seed gains",
                              "recurs. The same seed gains", 1)
    fails = _fails_of(split)
    assert any("no 'between s=A and s=B'" in f for f in fails), fails


def test_a_false_paraphrased_identity_claim_is_caught():
    """"another seed" is a different wording, not a free pass."""
    false_claim = MAIN_TEXT.replace("and a different seed loses 1.14",
                                    "and the same seed loses 1.14", 1)
    fails = _fails_of(false_claim)
    assert any("moved the same way in both dips" in f for f in fails), fails


def test_a_true_paraphrase_is_not_a_false_positive():
    """The claim is still true when reworded; the gate must read it, not
    fail it (reading is what makes the next wording checkable)."""
    assert not _fails_of(MAIN_TEXT.replace("and a different seed loses 1.14",
                                           "and another seed loses 1.14", 1))


def test_every_same_seed_clause_is_checked():
    both_same = MAIN_TEXT.replace("and a different seed loses 1.14",
                                  "and the same seed loses 1.14", 1)
    fails = _fails_of(both_same)
    assert any("moved the same way" in f for f in fails), fails


def test_a_commented_out_reading_changes_its_count():
    """A reading inside a commented-out line is not in the compiled paper."""
    reg = json.loads(CENSUS.read_text(encoding="utf-8"))
    lines = MAIN_TEXT.splitlines()
    target = next(i for i, l in enumerate(lines) if "51.14" in l)
    commented = "\n".join(l if i != target else "% " + l
                          for i, l in enumerate(lines))
    scored = _scored_literals(MAIN_TEXT)
    fails = v8.check_census(commented, MAIN.name, scored, reg, True,
                            _registered())
    assert any("51.14" in f for f in fails), fails


def test_a_reprint_outside_the_scored_classes_is_counted():
    """26.0 is printed twice and scored by no class; the census must still see
    it drift (review finding 3)."""
    reg = json.loads(CENSUS.read_text(encoding="utf-8"))
    scored = _scored_literals(MAIN_TEXT)
    assert any("drops 26.0 percentage points" in l for l in MAIN_TEXT.splitlines())
    drifted = MAIN_TEXT.replace("drops 26.0 percentage points",
                                "drops 26.1 percentage points", 1)
    fails = v8.check_census(drifted, MAIN.name, scored, reg, True,
                            _registered())
    assert any("26.0" in f for f in fails), fails


def test_update_census_refuses_a_same_named_copy(tmp_path):
    """--update-census pointed at a copy must not replace the real registry."""
    before = CENSUS.read_bytes()
    copy = tmp_path / "main.tex"
    copy.write_text(MAIN_TEXT, encoding="utf-8", newline="")
    r = subprocess.run([sys.executable, "-B", str(SCRIPT), "--paper",
                        str(copy), "--update-census"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=dict(os.environ,
                                                  PYTHONHASHSEED="0"),
                       cwd=str(FORK.parent.parent))
    assert r.returncode == 1, r.stdout[-1500:]
    assert "REFUSED" in r.stdout, r.stdout[-1500:]
    assert CENSUS.read_bytes() == before, "the census was overwritten by a copy"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))