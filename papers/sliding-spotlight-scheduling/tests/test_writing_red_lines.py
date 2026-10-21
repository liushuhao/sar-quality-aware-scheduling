#!/usr/bin/env python3
"""Ticket 37 -- red-line gate: the writing-obligation bans (W1-W13) and the
scan-set gate (--must-include).

Every ban carries THREE fixtures, because a check that only ever sees the
violating text proves nothing:

  * a violating line            -> rc == 1 and the expected label is printed
  * the licensed form of the     -> rc == 0 (the A1 deadlock: the mandatory
    SAME string                     obligations REQUIRE "NOT-PLATEAUED" in the
                                    text, so a keyword ban would be a
                                    permanently red gate)
  * a mutation that reverts the
    classification logic         -> the test goes red (see
                                    ``test_mutation_*``)

The mutations here are real reversions of the guard logic, not deletions of
patterns: dropping the whitelist would make the licensed fixtures fail, and
dropping the ban would make the violating fixtures pass.  Both directions are
covered, which is the property that distinguishes a discriminating check from
a check that fires or a check that never fires.

Usage (repo root):
    PYTHONHASHSEED=0 PYTHONPATH=src \
      "/d/Program Files/Python/python" -m pytest \
      papers/sliding-spotlight-scheduling/tests/test_writing_red_lines.py -v
"""
from __future__ import annotations

import importlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

FORK = Path(__file__).resolve().parent.parent
CHECKER = FORK / "scripts" / "check_red_lines.py"
sys.path.insert(0, str(FORK / "scripts"))

crl = importlib.import_module("check_red_lines")


def run_gate(tmp_path: Path, body: str, suffix: str = ".md",
             *extra: str) -> subprocess.CompletedProcess:
    """Run the gate over ONE manuscript-shaped fixture file."""
    p = tmp_path / ("chapter" + suffix)
    p.write_text(body, encoding="utf-8", newline="")
    env = dict(os.environ, PYTHONHASHSEED="0")
    return subprocess.run(
        [sys.executable, "-B", str(CHECKER), "--path", str(p), *extra],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
    )


def assert_bans(body: str, label: str, suffix: str = ".md") -> None:
    """The violating form must fire THAT label, and only that label."""
    r = run_gate(_TMP, body, suffix)
    assert r.returncode == 1, f"expected rc=1 for {label}, got {r.returncode}"
    assert f"VIOLATION   {label}:" in r.stdout, (
        f"{label} did not fire; stdout was:\n{r.stdout}")


def assert_clears(body: str, suffix: str = ".md") -> None:
    """The licensed form must pass with no violation at all."""
    r = run_gate(_TMP, body, suffix)
    assert r.returncode == 0, (
        f"expected rc=0, got {r.returncode}\n{r.stdout}\n{r.stderr}")


# --------------------------------------------------------------------------
# W1 / A1 + E2 -- the plateau ban, in BOTH directions.
# This is the A1 deadlock.  "NOT-PLATEAUED" is MANDATORY on every
# frontier-richness reading (checklist A1, D-6, figure captions), so a plain
# keyword ban is a permanently red gate.  The licensed form is the verdict
# LABEL in qualifier position; the banned form is a standalone richness
# assertion in either direction.
# --------------------------------------------------------------------------
W1 = "W1 A1 plateau (both directions)"

W1_VIOLATES = [
    ("has plateaued", "The front has plateaued at 160/240, so richness is bounded.\n"),
    ("has NOT plateaued + bound",
     "The front has not plateaued, therefore the upper bound on richness holds.\n"),
    ("has NOT plateaued bare",
     "The front has not plateaued at the top budget.\n"),
    ("is plateaued", "The front is plateaued, so the front is the converged true front.\n"),
    ("zh 未平台", "160/240 档前沿未平台，故丰富度上界成立。\n"),
    ("zh 已平台", "160/240 档前沿已平台，故前沿即收敛真前沿。\n"),
]
W1_CLEARS = [
    # Each fixture MUST contain a token W1 actually matches -- otherwise it
    # proves nothing about the whitelist (the first cut used "carry the
    # NOT-PLATEAUED caveat", which no W1 pattern matches, so the guard was
    # never exercised).
    #
    # The licensed form is the verdict LABEL, not the verdict RESTATED.  A
    # caption obligation asks for the tag "NOT-PLATEAUED", not for the prose
    # "the front has not plateaued" -- and the latter IS the banned assertion
    # in its reverse direction, so a fixture containing both is correctly
    # red.  Two fixtures below (has plateaued / not plateaued) pin that the
    # mixed shape is NOT whitelisted.
    ("EN label as annotation",
     "Front richness by family at 160/240; reported as NOT-PLATEAUED.\n", ".md"),
    ("EN caption tag",
     "Figure 3. Front richness at 160/240 (NOT-PLATEAUED).\n", ".md"),
    ("EN caveat wording",
     "The readings carry the NOT-PLATEAUED caveat.\n", ".md"),
    ("ZH qualifier",
     "丰富度读数取 160/240 档，标注 NOT-PLATEAUED（未平台）。\n", ".md"),
    ("ZH clause",
     "两档间仍单调上升，按 NOT-PLATEAUED 条款处理。\n", ".md"),
    ("prohibiting shape",
     "The front has not plateaued, and neither may it be described as plateaued: "
     "both directions are forbidden.\n", ".md"),
    ("tex math form",
     "\\emph{Front richness at 160/240, tagged NOT-PLATEAUED.}\n", ".tex"),
]


@pytest.mark.parametrize("name,body", W1_VIOLATES, ids=[n for n, _ in W1_VIOLATES])
def test_w1_plateau_ban_fires_in_both_directions(name, body):
    assert_bans(body, W1)


@pytest.mark.parametrize("name,body,sfx", W1_CLEARS, ids=[n for n, _, _ in W1_CLEARS])
def test_w1_licensed_qualifier_form_clears(name, body, sfx):
    """The A1 deadlock resolution: mandating the label must not redden the gate."""
    assert_clears(body, sfx)


# The load-bearing boundary: a licensed LABEL does not whitelist a banned
# RESTATEMENT that happens to share the sentence.  Without these two, a future
# widening of the qualifier whitelist would let "NOT-PLATEAUED, therefore the
# front has not plateaued and richness is bounded" through while every
# licence-only test still passed.
@pytest.mark.parametrize("name,body", [
    ("label then banned claim",
     "Reported as NOT-PLATEAUED; the frontier has not plateaued at this budget.\n"),
    ("caption label then banned claim",
     "Figure 3. Richness at 160/240 (NOT-PLATEAUED; the front has not plateaued).\n"),
    ("caveat then banned claim",
     "The readings carry the NOT-PLATEAUED caveat: the ladder has not plateaued.\n"),
], ids=["label_then_claim", "caption_then_claim", "caveat_then_claim"])
def test_w1_label_does_not_whitelist_a_restated_claim(name, body):
    assert_bans(body, W1)


def _never_match():
    import re as _re
    return _re.compile(r"(?!x)x")


def _scan_one(path: Path) -> "tuple[list, list]":
    """Run the ban scanner over one file, (violations, cleared)."""
    violations, cleared = [], []
    crl.scan_writing_bans([path], violations, cleared)
    return violations, cleared


class _patch_guard:
    """Swap one ban's GUARD inside WRITING_BANS for the duration of a block.

    The table binds each guard function BY VALUE at import
    (``compiled = [..., guard] for ... in WRITING_BANS``), so rebinding the
    module attribute would leave the table holding the original.  The mutation
    therefore has to replace the tuple element -- which is also the more honest
    mutation: it is exactly the edit a future regression would make.
    """

    def __init__(self, label: str, guard):
        self.label, self.guard = label, guard

    def __enter__(self):
        self.saved = crl.WRITING_BANS
        crl.WRITING_BANS = [
            (lbl, pats, self.guard if lbl == self.label else g)
            for lbl, pats, g in self.saved
        ]
        return self

    def __exit__(self, *exc):
        crl.WRITING_BANS = self.saved
        return False


def _no_clear(line: str, _m) -> str:
    """A guard that licenses nothing = the whitelist reverted."""
    return ""


def test_mutation_w1_drop_the_whitelist_makes_the_licensed_fixtures_red(tmp_path):
    """Revert the A1 whitelist => the MANDATORY label strings fire.

    This is the inverse of the deadlock the whitelist exists to prevent: if a
    future edit removes the qualifier clearance, the obligations the checklist
    REQUIRES in the text start failing, and this goes red before the gate does.
    """
    with _patch_guard(W1, _no_clear):
        for name, body, sfx in W1_CLEARS:
            p = tmp_path / ("c" + sfx)
            p.write_text(body, encoding="utf-8", newline="")
            violations, _ = _scan_one(p)
            assert any(v.startswith(W1) for v in violations), (
                f"mutated guard still cleared the licensed fixture: {name}")


def test_mutation_w1_drop_the_ban_makes_the_violating_fixtures_pass(tmp_path):
    """The other direction: removing the PATTERN (not the guard) must make the
    banned assertions stop firing.  Without this, a ban that never fires would
    still satisfy every other test in this file."""
    import re as _re
    saved = crl.WRITING_BANS
    try:
        # a pattern that cannot match anything -- the same shape as deleting
        # the entry, but it keeps the table row so the guard stays reachable
        crl.WRITING_BANS = [(lbl, ([r"(?!x)x"] if lbl == W1 else pats), g)
                            for lbl, pats, g in saved]
        for name, body in W1_VIOLATES:
            p = tmp_path / "c.md"
            p.write_text(body, encoding="utf-8", newline="")
            violations, _ = _scan_one(p)
            assert not any(v.startswith(W1) for v in violations), (
                f"ban still fires with an unmatchable pattern: {name}")
    finally:
        crl.WRITING_BANS = saved


def test_mutation_w11_drop_the_evaluator_qualifier_makes_the_obligation_red(tmp_path):
    """A7's whitelist is the ONLY thing standing between 'zero violations' and
    a violation.  Revert it and the bare form must fire."""
    with _patch_guard(W11, _no_clear):
        for name, body in W11_VIOLATES:
            p = tmp_path / "c.md"
            p.write_text(body, encoding="utf-8", newline="")
            violations, _ = _scan_one(p)
            assert any(v.startswith(W11) for v in violations), name


def test_mutation_w13_drop_the_caliber_tag_makes_the_tagged_reading_red(tmp_path):
    """A4: the caliber tag is the licence.  Remove the tag recogniser and a
    TAGGED reading must fire -- the bare form fires either way, so using it
    here would prove nothing about the tag."""
    saved = crl._CALIBER_TAG_RX
    try:
        crl._CALIBER_TAG_RX = _never_match()
        p = tmp_path / "c.md"
        p.write_text("The median f_q reached 84.5 (v3 real-window caliber, "
                     "non-normalised).\n", encoding="utf-8", newline="")
        violations, _ = _scan_one(p)
        assert any(v.startswith(W13) for v in violations)
    finally:
        crl._CALIBER_TAG_RX = saved


# --------------------------------------------------------------------------
# W2 / E1 -- the no-prior-work ban.  Ticket 50 RETIRED the spec.md:82
# licence: the conjunction it licensed ("coupling loop as a first-class
# constraint AND a per-mode SAR metric as an independent objective,
# simultaneously") is no longer the paper's claim, so the sentence it
# licensed must now FIRE.  The guard licenses only quote-to-forbid and
# explicit-retraction shapes.
# --------------------------------------------------------------------------
W2 = "W2 E1 no-prior-work claim"

W2_VIOLATES = [
    ("zh 无人做", "斜视角-时长耦合无人做，本文提出该框架。\n"),
    ("zh 尚无人", "质量感知卫星调度尚无人研究。\n"),
    ("zh 首次提出", "本文首次提出该耦合框架。\n"),
    ("EN no prior work", "No prior work has addressed the squint-duration coupling.\n"),
    # The clause-final form the manuscript actually uses (main.tex:59).  The
    # registered patterns above require a following on/for/has/does/study, so
    # without the extension this shape was invisible to W2 -- which is why
    # retiring the licence alone left the sentence green.
    ("EN clause-final no prior work",
     "Treating the steering-coupling loop as a first-class constraint and "
     "carrying a per-mode SAR metric as an independent objective has no "
     "prior work.\n"),
    ("EN first to", "We are the first to study the coupled metric.\n"),
    ("EN has never been", "The squint-duration coupling has never been studied.\n"),
    # The RETIRED licence, verbatim from spec.md:82.  It must be red now.
    ("retired spec82 conjunction",
     "正确表述 = 耦合闭环一等约束 + 逐模式 SAR 指标进 MOEA 独立目标维，二者同时做无人做。\n"),
]
W2_CLEARS = [
    ("plain related-work phrasing",
     "Prior work treats squint and dwell as independent design variables.\n"),
    ("prohibiting shape",
     "禁「无人做」类声明；先例必须逐条列文献。\n"),
    ("explicitly retired claim",
     "We no longer claim that no prior work couples the loop and the metric.\n"),
]


@pytest.mark.parametrize("name,body", W2_VIOLATES, ids=[n for n, _ in W2_VIOLATES])
def test_w2_no_prior_work_ban_fires(name, body):
    assert_bans(body, W2)


@pytest.mark.parametrize("name,body", W2_CLEARS, ids=[n for n, _ in W2_CLEARS])
def test_w2_licensed_shapes_clear(name, body):
    assert_clears(body)


def test_w2_ban_is_not_a_general_exemption():
    """The retired whitelist licensed exactly one sentence.  With it gone,
    '无人做' must be caught wherever it appears, with no licensed conjunction."""
    r = run_gate(_TMP, "The squint-duration coupling 无人做.\n")
    assert r.returncode == 1


def test_mutation_w2_without_the_clause_final_pattern_the_new_claim_passes(
        tmp_path):
    """The clause-final extension is what catches the manuscript's own novelty
    sentence.  Remove that one pattern and the sentence must pass -- proving
    the ban is driven by the extension, not by luck."""
    saved = crl.WRITING_BANS
    try:
        crl.WRITING_BANS = [
            (lbl, tuple(p for p in pats if p != r"\bno\s+prior\s+work\b")
             if lbl == W2 else pats, g)
            for lbl, pats, g in saved]
        p = tmp_path / "c.md"
        p.write_text("Treating the loop as a constraint and the metric as an "
                     "objective has no prior work.\n",
                     encoding="utf-8", newline="")
        violations, _ = _scan_one(p)
        assert not any(v.startswith(W2) for v in violations), violations
    finally:
        crl.WRITING_BANS = saved


# --------------------------------------------------------------------------
# W3a / W3b -- capacity caliber (spec D15 red line 1) and the not-recomputed
# rule (B15).  Split into two bans because the per-orbit framing and the
# bare capacity NUMBER are different obligations with different exemptions.
# --------------------------------------------------------------------------
W3A = "W3a E3 per-orbit capacity caliber"
W3B = "W3b E3 capacity number (not recomputed)"

W3_VIOLATES = [
    (W3A, "per-orbit capacity", "Each orbit carries at most 24 tasks: the per-orbit capacity is 24.\n"),
    (W3A, "zh per-orbit", "每轨容量为 24 个任务。\n"),
    (W3B, "per-pass capacity NUMBER", "The per-pass capacity of the constellation is 12 tasks.\n"),
    (W3B, "capacity is N", "The capacity is 24 targets per pass.\n"),
    (W3B, "zh 容量 数字", "该容量为 24 个目标。\n"),
]
W3_CLEARS = [
    ("not-recomputed clause",
     "No capacity number may appear until the v3 recomputation lands.\n"),
    ("prohibiting shape",
     "容量口径为禁写：v3 未重算容量，论文禁出现任何 capacity 数字。\n"),
]


@pytest.mark.parametrize("label,name,body", W3_VIOLATES, ids=[n for _, n, _ in W3_VIOLATES])
def test_w3_capacity_bans_fire(label, name, body):
    assert_bans(body, label)


@pytest.mark.parametrize("name,body", W3_CLEARS, ids=[n for n, _ in W3_CLEARS])
def test_w3_not_recomputed_clause_clears(name, body):
    assert_clears(body)


# --------------------------------------------------------------------------
# W4 / E4 -- the universal "a single satellite can only fit N" claim.
# --------------------------------------------------------------------------
W4 = "W4 E4 single-satellite only-N"

W4_VIOLATES = [
    ("zh", "单星一次只能安排 24 个任务。\n"),
    ("zh alt", "一颗星单次至多 12 个目标。\n"),
    ("EN", "A single satellite can only accommodate 24 targets per pass.\n"),
    ("EN may at most", "One satellite may accommodate at most 12 targets.\n"),
]
W4_CLEARS = [
    ("prohibiting shape", "禁写「单星一次只能 N 个」的普适句。\n"),
    ("counter-example framing",
     "The per-pass figure is 24, but the multi-orbit result is a counter-example to any universal N.\n"),
]


@pytest.mark.parametrize("name,body", W4_VIOLATES, ids=[n for n, _ in W4_VIOLATES])
def test_w4_single_satellite_only_n_fires(name, body):
    assert_bans(body, W4)


@pytest.mark.parametrize("name,body", W4_CLEARS, ids=[n for n, _ in W4_CLEARS])
def test_w4_licensed_shapes_clear(name, body):
    assert_clears(body)


# --------------------------------------------------------------------------
# W5 / E5 -- a 45-deg READING must carry the extrapolation label.  Narrowed
# on purpose: the platform inclination IS legitimately 45 deg.
# --------------------------------------------------------------------------
W5 = "W5 E5 45-deg extrapolation label"

W5_VIOLATES = [
    ("dwell at 45", "At 45 deg the dwell time reaches 12.207 s for SLS.\n"),
    ("reading then 45", "The dwell reaches 12.207 s at 45 deg.\n"),
    ("zh", "45° 处驻留时间达 12.207 s。\n"),
]
W5_CLEARS = [
    ("labelled extrapolated", "At 45 deg the dwell time reaches 12.207 s (extrapolated reading).\n"),
    ("labelled zh", "45° 处驻留时间达 12.207 s（按外推披露）。\n"),
    ("prohibiting shape", "禁写 45° 段读数不带外推标注。\n"),
    # the platform inclination is NOT a reading and must not trip the ban
    ("inclination is not a reading", "The satellite orbits at an inclination of 45 degrees.\n"),
]


@pytest.mark.parametrize("name,body", W5_VIOLATES, ids=[n for n, _ in W5_VIOLATES])
def test_w5_unlabelled_45deg_reading_fires(name, body):
    assert_bans(body, W5)


@pytest.mark.parametrize("name,body", W5_CLEARS, ids=[n for n, _ in W5_CLEARS])
def test_w5_labelled_and_non_reading_forms_clear(name, body):
    assert_clears(body)


# --------------------------------------------------------------------------
# W6 / E6 -- the density axis belongs to the thesis.
# --------------------------------------------------------------------------
W6 = "W6 E6 density axis ownership"

W6_VIOLATES = [
    ("zh this paper", "本文的核心贡献是密度轴与调度的耦合分析。\n"),
    ("zh trailing", "密度轴是本篇的主要贡献之一。\n"),
    ("EN", "The density axis is the core contribution of this paper.\n"),
]
W6_CLEARS = [
    ("scoped out", "The density axis belongs to the thesis chapter and is out of scope here.\n"),
    ("prohibiting shape", "禁把密度轴叙事归入本篇。\n"),
]


@pytest.mark.parametrize("name,body", W6_VIOLATES, ids=[n for n, _ in W6_VIOLATES])
def test_w6_density_axis_ownership_fires(name, body):
    assert_bans(body, W6)


@pytest.mark.parametrize("name,body", W6_CLEARS, ids=[n for n, _ in W6_CLEARS])
def test_w6_scoped_forms_clear(name, body):
    assert_clears(body)


# --------------------------------------------------------------------------
# W7 / E7 -- rho_a,ach routing, scan-span/rate "in the loop", and the
# shrinking-feasible-set claim.  All three have zero production consumers.
# --------------------------------------------------------------------------
W7 = "W7 E7 routing / scan-constraint claims"

W7_VIOLATES = [
    ("md rho routing", "rho_a,ach is used for routing the mode selection.\n", ".md"),
    ("zh rho routing", "rho_a,ach 用于路由模式选择。\n", ".md"),
    # the .tex form matters: the elsarticle port is what W5.5 gates, and the
    # first cut of the rho pattern silently missed every one of these
    ("tex rho routing", r"$\rho_{a,\mathrm{ach}}$ is used for routing the mode." + "\n", ".tex"),
    ("scan span in the loop", "The scan span constraint is in the loop for every candidate.\n", ".md"),
    ("scan rate in the loop", "The scan rate limit is enforced during scheduling.\n", ".md"),
    ("zh scan in the loop", "扫描跨度约束在环参与评估。\n", ".md"),
    ("feasible set shrinks", "The feasible set for high-demand tasks shrinks with squint angle.\n", ".md"),
]
W7_CLEARS = [
    ("B_D is the real consumer", "rho_a,ach is consumed only by B_D.\n", ".md"),
    ("prohibiting shape", "禁称扫描率/扫描跨度约束在环。\n", ".md"),
]


@pytest.mark.parametrize("name,body,sfx", W7_VIOLATES, ids=[n for n, _, _ in W7_VIOLATES])
def test_w7_routing_and_scan_bans_fire(name, body, sfx):
    assert_bans(body, W7, sfx)


@pytest.mark.parametrize("name,body,sfx", W7_CLEARS, ids=[n for n, _, _ in W7_CLEARS])
def test_w7_licensed_shapes_clear(name, body, sfx):
    assert_clears(body, sfx)


# --------------------------------------------------------------------------
# W8 / E8 -- delta was registered AFTER calibration.
# --------------------------------------------------------------------------
W8 = "W8 E8 pre-registered effect size"

W8_VIOLATES = [
    ("EN", "The pre-registered effect size delta = 6.0 yields 92% power.\n"),
    ("EN hyphenless", "The preregistered effect size was fixed before the run.\n"),
    ("zh", "δ 为预注册效应量。\n"),
]
W8_CLEARS = [
    ("honest wording", "The effect size was registered after calibration, value inherited from the frozen threshold.\n"),
    ("prohibiting shape", "禁写 pre-registered effect size（δ 标定后注册）。\n"),
    # ALIVE/DEAD are structural verdicts and are NOT bound by delta
    ("ALIVE is not bound by delta", "R2F is descriptively ALIVE; delta does not constrain that verdict.\n"),
]


@pytest.mark.parametrize("name,body", W8_VIOLATES, ids=[n for n, _ in W8_VIOLATES])
def test_w8_pre_registered_effect_size_fires(name, body):
    assert_bans(body, W8)


@pytest.mark.parametrize("name,body", W8_CLEARS, ids=[n for n, _ in W8_CLEARS])
def test_w8_licensed_shapes_clear(name, body):
    assert_clears(body)


# --------------------------------------------------------------------------
# W9 / E9 -- coverage pass/fail.  Ticket 50 rewrote the LICENCE, not the ban:
# coverage is the only axis now, so "degenerate by construction" is
# semantically reversed and clears nothing.  What clears is the paired
# no-judgement predicate (reported as a reading / not a test / has no power),
# with a contrast between predicate and hit blocking the clearance.
# --------------------------------------------------------------------------
W9 = "W9 E9 coverage pass/fail"

W9_VIOLATES = [
    ("EN passed", "The coverage axis passed at the base budget.\n"),
    ("EN did not pass", "The coverage test did not pass at the base budget.\n"),
    ("EN failed", "Coverage failed, so the parity hypothesis is rejected.\n"),
    ("zh 通过", "覆盖轴检验通过。\n"),
    ("zh 未通过", "覆盖轴检验未通过。\n"),
    # The RETIRED premise must no longer licence a pass/fail sentence: under
    # the single-axis positioning coverage is not a degenerate second axis.
    ("retired degenerate-by-construction premise",
     "Coverage parity is degenerate by construction, so the coverage test passed.\n"),
    # Laundering: a no-judgement predicate in an EARLIER clause does not clear
    # an assertion after a contrast.
    ("predicate then contrastive assertion",
     "Coverage is reported as a reading; yet coverage passed at the base budget.\n"),
    # A sentence terminator separates claims on the same line.
    ("predicate then new sentence",
     "Coverage has no power as a test. Coverage passed at the base budget.\n"),
]
W9_CLEARS = [
    # Each fixture MUST contain a hit W9 actually matches, or it proves nothing
    # about the licence (the first cut's prose did not, so the guard was never
    # exercised).
    ("reported as a reading, not a test",
     "Coverage is reported as a reading, not a test: coverage passed is not a "
     "claim this paper makes.\n"),
    ("no power as a test",
     "Coverage has no power as a test, so a coverage axis failed reading is "
     "not a result.\n"),
    ("single-objective tie-set reading",
     "All 260 units carry a single-objective tie-set (unique f1 = 1), and there "
     "is no pass/fail: coverage passed is not a statement.\n"),
    ("prohibiting shape", "禁「coverage 通过」类判词；覆盖只报读数。\n"),
]


@pytest.mark.parametrize("name,body", W9_VIOLATES, ids=[n for n, _ in W9_VIOLATES])
def test_w9_coverage_pass_fail_fires(name, body):
    assert_bans(body, W9)


@pytest.mark.parametrize("name,body", W9_CLEARS, ids=[n for n, _ in W9_CLEARS])
def test_w9_licensed_shapes_clear(name, body):
    assert_clears(body)


def test_mutation_w9_reverting_to_the_retired_premise_reds_the_reading_fixtures(
        tmp_path):
    """Put the retired 'degenerate by construction' licence back and the NEW
    licensed fixtures must stop clearing -- proving the exemption is carried by
    the new anchor, not by the old premise."""
    old = crl._clear_by_regex(r"degenerate\s+by\s+construction|构造性打平|构造产物")
    with _patch_guard(W9, old):
        # The prohibiting fixture is deliberately excluded: its clearance is
        # the prohibition marker, not the retired premise, so it stays clear
        # under the old guard too.
        for name, body in W9_CLEARS[:3]:
            p = tmp_path / "c.md"
            p.write_text(body, encoding="utf-8", newline="")
            violations, _ = _scan_one(p)
            assert any(v.startswith(W9) for v in violations), (
                f"the retired licence still clears the new fixture: {name}")


# --------------------------------------------------------------------------
# W10 / E10 + B9 -- the optimizer consumes duration_scene_s, so the
# point-target-caliber sentence is stale (formula-spec 8.13-1).
# --------------------------------------------------------------------------
W10 = "W10 E10 point-target caliber"

W10_VIOLATES = [
    ("zh", "优化器驻留采用点目标口径。\n"),
    ("EN", "The optimizer consumes the point-target caliber for dwell.\n"),
]
W10_CLEARS = [
    ("names the real caliber", "The optimizer consumes the scene-level duration_scene_s.\n"),
    ("prohibiting shape", "禁写「优化器驻留用点目标口径」（实况 = 场景级）。\n"),
    ("contrastive table caption", "点目标 vs 场景级口径：优化器消费场景级。\n"),
]


@pytest.mark.parametrize("name,body", W10_VIOLATES, ids=[n for n, _ in W10_VIOLATES])
def test_w10_point_target_caliber_fires(name, body):
    assert_bans(body, W10)


@pytest.mark.parametrize("name,body", W10_CLEARS, ids=[n for n, _ in W10_CLEARS])
def test_w10_licensed_shapes_clear(name, body):
    assert_clears(body)


# --------------------------------------------------------------------------
# W11 / A7 -- a zero-violation statement is relative to the evaluator.
# --------------------------------------------------------------------------
W11 = "W11 A7 zero-violation caliber"

W11_VIOLATES = [
    ("EN zero", "Across all 90 units there were zero violations.\n"),
    ("EN 0", "Across all 90 units there were 0 violations.\n"),
    ("zh", "90 个单元零违规。\n"),
    ("zh 无违规", "全部单元无违规。\n"),
]
W11_CLEARS = [
    ("EN relative to evaluator",
     "Across all 90 units there were zero violations relative to the evaluator.\n"),
    ("zh relative to evaluator", "90 个单元零违规（相对于评估器）。\n"),
    ("EN evaluation model",
     "Zero violations were observed with respect to the evaluation model.\n"),
]


@pytest.mark.parametrize("name,body", W11_VIOLATES, ids=[n for n, _ in W11_VIOLATES])
def test_w11_zero_violation_without_caliber_fires(name, body):
    assert_bans(body, W11)


@pytest.mark.parametrize("name,body", W11_CLEARS, ids=[n for n, _ in W11_CLEARS])
def test_w11_relative_to_evaluator_clears(name, body):
    assert_clears(body)


# --------------------------------------------------------------------------
# W12 / A3 -- the v2 real-window artifacts are permanently uncitable, with
# the ONE registered exception (confound_control.json).
# --------------------------------------------------------------------------
W12 = "W12 A3 v2 real-window citation"

W12_VIOLATES = [
    ("bare path", "The base-budget front size was 19.5 in experiments/v2_results/results_table.json.\n"),
    ("spaces", "See v2 results for the convergence report.\n"),
    ("tex", "The R2F reading is taken from v2\\_results.\n"),
]
W12_CLEARS = [
    ("registered exception",
     "The M-family anchor delta comes from v2_results/confound_control.json.\n"),
    ("v3 is the live source", "All real-window readings come from v3_results.\n"),
]


@pytest.mark.parametrize("name,body", W12_VIOLATES, ids=[n for n, _ in W12_VIOLATES])
def test_w12_v2_real_window_citation_fires(name, body):
    assert_bans(body, W12)


@pytest.mark.parametrize("name,body", W12_CLEARS, ids=[n for n, _ in W12_CLEARS])
def test_w12_exception_and_v3_cite_clear(name, body):
    assert_clears(body)


# --------------------------------------------------------------------------
# W13 / A4 -- an f_q READING must carry its caliber tag.  The tag travels on
# the LINE that states the number, not somewhere else in the document.
# --------------------------------------------------------------------------
W13 = "W13 A4 f_q caliber tag"

W13_VIOLATES = [
    ("md reading after", "The median f_q reached 84.5 at the top budget.\n", ".md"),
    ("md reading equals", "The median f_q = 84.5 at the top budget.\n", ".md"),
    ("zh reading", "f_q 中位数为 84.5（160/240 档）。\n", ".md"),
    ("tex reading", "The median $f_Q$ reached 84.5 at the top budget.\n", ".tex"),
]
W13_CLEARS = [
    ("tagged EN", "The median f_q reached 84.5 (v3 real-window caliber, non-normalised).\n", ".md"),
    ("tagged zh", "f_q 中位数为 84.5（v3 真窗口径，非归一化）。\n", ".md"),
    ("tagged tex", "The median $f_Q$ reached 84.5 (caliber v3).\n", ".tex"),
    # a formula mention is not a reading -- a digit elsewhere on the line
    # (an equation number, a table number) must not trip the obligation
    ("formula mention", "We define f_q in Eq.(9).\n", ".md"),
    ("tex formula mention", "We denote the delivered quality by $f_Q$ and define it in Eq.~(9).\n", ".tex"),
]


@pytest.mark.parametrize("name,body,sfx", W13_VIOLATES, ids=[n for n, _, _ in W13_VIOLATES])
def test_w13_untagged_fq_reading_fires(name, body, sfx):
    assert_bans(body, W13, sfx)


@pytest.mark.parametrize("name,body,sfx", W13_CLEARS, ids=[n for n, _, _ in W13_CLEARS])
def test_w13_tagged_or_non_reading_lines_clear(name, body, sfx):
    assert_clears(body, sfx)


def test_guard_offsets_are_line_local_not_document_offsets(tmp_path):
    """Positional guards must judge the LINE they are handed.

    The match object came from the whole document, so before the rebase a hit
    on line 2+ saw ``line[:m.start()]`` == the whole line and an empty tail:
    the same sentence cleared on line 1 and fired on line 2 (phase-1 review
    finding, CRITICAL).  This pins the rebase via W13's reading detector, the
    guard that was demonstrably wrong.
    """
    body = ("A clean opening line.\n"
            "The median f_q reached 84.5 at the top budget.\n")
    p = tmp_path / "c.md"
    p.write_text(body, encoding="utf-8", newline="")
    violations, _ = _scan_one(p)
    assert any(v.startswith(W13) and ":2 " in v for v in violations), violations


# --------------------------------------------------------------------------
# W14 (ticket 50 A1) -- the single-axis positioning.
# The paper no longer carries "a per-mode SAR metric as an independent
# objective dimension".  Asserting the old framing is banned; a retrospective
# or negated mention is licensed (the manuscript must be able to say what it
# no longer does).
# --------------------------------------------------------------------------
W14 = "W14 single-axis positioning"

W14_VIOLATES = [
    ("EN second objective",
     "The quality headroom is a second objective rather than a post-hoc check.\n"),
    ("EN hyphen", "We solve a second-objective formulation.\n"),
    ("EN bi-objective",
     "The bi-objective problem maximises served priority and quality.\n"),
    ("EN dual-objective",
     "The solver is a dual-objective evolutionary search.\n"),
    ("EN two objectives", "The search optimises two objectives at once.\n"),
    ("EN independent objective dimension",
     "Carrying a per-mode SAR metric as an independent objective dimension is new.\n"),
    ("EN title", "Scheduling with Mode-Determined Dwell and an Image-Quality "
                 "Objective\n"),
    ("EN plural", "The solver optimises second objectives at once.\n"),
    ("EN ordinal", "The 2nd objective is the quality index.\n"),
    ("EN quality-is-an-objective",
     "We treat image quality as an objective in the loop.\n"),
    ("zh 第二目标", "本文将图像质量作为第二目标。\n"),
    ("zh 第二个目标", "把图像质量作为第二个目标参与优化。\n"),
    ("zh 双目标", "双目标优化问题在覆盖与质量之间权衡。\n"),
    ("zh 独立目标维", "把逐模式 SAR 指标作为独立目标维。\n"),
    # The prohibition sits in a LATER comma-clause and must not clear.
    ("prohibition in a later clause",
     "The second objective is retained, and calling the schedule a physical "
     "limit is forbidden.\n"),
    # A retirement word in an earlier clause does not clear an assertion after
    # a contrast.
    ("laundering after contrast",
     "The former framing is retired; yet quality is a second objective.\n"),
    # Negating the retraction asserts the framing.
    ("negated retraction",
     "The second objective is not withdrawn from the formulation.\n"),
]
W14_CLEARS = [
    ("no longer treat", "We no longer treat image quality as a second objective.\n"),
    ("former formulation",
     "The former two-objective formulation is replaced by a per-task hard "
     "constraint.\n"),
    ("not a second objective",
     "Image quality is not a second objective in this paper.\n"),
    ("not an objective dimension",
     "The metric is not an objective dimension in this paper.\n"),
    ("withdrawn framing",
     "The second objective was withdrawn from the formulation.\n"),
    ("zh 不再", "本文不再把图像质量作为第二目标。\n"),
    ("zh 旧双目标作废",
     "旧的双目标形式已作废，改为单目标加逐任务硬约束。\n"),
    ("no longer an objective",
     "We no longer treat quality as an objective in the loop.\n"),
    ("prohibiting shape", "禁「第二目标」类表述。\n"),
]


@pytest.mark.parametrize("name,body", W14_VIOLATES, ids=[n for n, _ in W14_VIOLATES])
def test_w14_second_objective_framing_fires(name, body):
    assert_bans(body, W14)


@pytest.mark.parametrize("name,body", W14_CLEARS, ids=[n for n, _ in W14_CLEARS])
def test_w14_retrospective_mentions_clear(name, body):
    assert_clears(body)


def test_mutation_w14_drop_the_guard_reds_the_retrospective_fixtures(tmp_path):
    """Remove the clearance and the licensed retrospective forms must fire --
    proving the guard, not the pattern, separates the two shapes."""
    with _patch_guard(W14, _no_clear):
        for name, body in W14_CLEARS:
            p = tmp_path / "c.md"
            p.write_text(body, encoding="utf-8", newline="")
            violations, _ = _scan_one(p)
            assert any(v.startswith(W14) for v in violations), name


def test_mutation_w14_drop_the_ban_makes_the_old_framing_pass(tmp_path):
    """Remove the pattern and the banned assertions must stop firing."""
    saved = crl.WRITING_BANS
    try:
        crl.WRITING_BANS = [(lbl, ([r"(?!x)x"] if lbl == W14 else pats), g)
                            for lbl, pats, g in saved]
        for name, body in W14_VIOLATES:
            p = tmp_path / "c.md"
            p.write_text(body, encoding="utf-8", newline="")
            violations, _ = _scan_one(p)
            assert not any(v.startswith(W14) for v in violations), name
    finally:
        crl.WRITING_BANS = saved


# --------------------------------------------------------------------------
# W15a (ticket 50 A4) -- the fulfillment-ratio reading carries a three-part
# caliber tag: library f_q + tie-set member mean + reported reading, not a
# target.  The producer is scripts/build_sweep_results.py:75-88.
# --------------------------------------------------------------------------
W15A = "W15a A4 fulfillment-ratio caliber"

W15A_VIOLATES = [
    ("bare ratio", "The fulfillment ratio reaches 0.62 at the order point.\n"),
    ("two of the three tags",
     "The median fulfillment ratio is 0.62 (library caliber f_q, mean over the "
     "tie-set members).\n"),
    ("zh bare", "兑现率中位数为 0.62。\n"),
    ("partially tagged zh", "兑现率中位数为 0.62（库口径 f_q）。\n"),
]
W15A_CLEARS = [
    ("three-part tag",
     "The median fulfillment ratio is 0.62 (library caliber f_q, mean over the "
     "tie-set members; reported reading, not an optimization target).\n"),
    ("zh three-part tag",
     "兑现率中位数为 0.62（库口径 f_q、tie-set 全体成员均值、报告读数非优化目标）。\n"),
    ("mention without a number",
     "We define the fulfillment ratio in Section 5.\n"),
    ("prohibiting shape", "禁「兑现率 = 0.62」不带三要素口径标签。\n"),
]


@pytest.mark.parametrize("name,body", W15A_VIOLATES, ids=[n for n, _ in W15A_VIOLATES])
def test_w15a_untagged_fulfillment_reading_fires(name, body):
    assert_bans(body, W15A)


@pytest.mark.parametrize("name,body", W15A_CLEARS, ids=[n for n, _ in W15A_CLEARS])
def test_w15a_three_part_tag_clears(name, body):
    assert_clears(body)


def test_mutation_w15a_drop_the_tie_set_tag_makes_the_tagged_reading_red(
        tmp_path):
    """The tie-set element is load-bearing: remove its recogniser and the fully
    tagged fixture must fire (the ratio would otherwise be read as the anchor
    solution's reading, which is the error the tag exists to prevent)."""
    saved = crl._FULFILLMENT_TIESET_RX
    try:
        crl._FULFILLMENT_TIESET_RX = _never_match()
        p = tmp_path / "c.md"
        p.write_text(W15A_CLEARS[0][1], encoding="utf-8", newline="")
        violations, _ = _scan_one(p)
        assert any(v.startswith(W15A) for v in violations), violations
    finally:
        crl._FULFILLMENT_TIESET_RX = saved


# --------------------------------------------------------------------------
# W15b (ticket 50 A4) -- the descriptive f_Q_deliv variant must be labelled
# and declared incomparable with the library caliber (formula-spec 8.17-10).
# --------------------------------------------------------------------------
W15B = "W15b A4 f_Q_deliv descriptive tag"

W15B_VIOLATES = [
    ("bare variant",
     "The variant f_Q_deliv reaches 0.71 in the same units.\n", ".md"),
    ("labelled but no non-comparability",
     "The descriptive variant f_Q_deliv reaches 0.71.\n", ".md"),
]
W15B_CLEARS = [
    ("labelled and incomparable",
     "The descriptive variant f_Q_deliv reaches 0.71 (not comparable with the "
     "library-caliber f_q).\n", ".md"),
    ("mention without a number",
     "We define f_Q_deliv in Eq.(12).\n", ".md"),
    ("tex labelled and incomparable",
     "The descriptive variant $f_{Q,\\text{deliv}}$ reaches 0.71 and is not "
     "comparable with the library caliber.\n", ".tex"),
]


@pytest.mark.parametrize("name,body,sfx", W15B_VIOLATES,
                         ids=[n for n, _, _ in W15B_VIOLATES])
def test_w15b_untagged_fq_deliv_reading_fires(name, body, sfx):
    assert_bans(body, W15B, sfx)


@pytest.mark.parametrize("name,body,sfx", W15B_CLEARS,
                         ids=[n for n, _, _ in W15B_CLEARS])
def test_w15b_labelled_incomparable_reading_clears(name, body, sfx):
    assert_clears(body, sfx)


# --------------------------------------------------------------------------
# English falsified markers (ticket 37, review-fable D block).
# Without them the COLLAPSE pattern fires on the sentence that WITHDRAWS the
# collapse -- the ordinary way to report the registered SEARCH-ARTIFACT
# verdict in English.
# --------------------------------------------------------------------------
def test_english_search_artifact_disclosure_does_not_fire_r2():
    body = ("Results. The apparent front collapse at the base budget was a "
            "search artifact: raising the budget to 160/240 restored the "
            "front. The collapse narrative is withdrawn.\n")
    r = run_gate(_TMP, body)
    assert r.returncode == 0, r.stdout
    assert "cleared" in r.stdout.lower()


def test_english_budget_artifact_disclosure_does_not_fire_r2():
    body = ("The apparent collapse was a budget artifact, so the narrative is "
            "withdrawn.\n")
    assert run_gate(_TMP, body).returncode == 0


def test_english_collapse_assertion_still_fires():
    """The marker addition must not disarm the ban it was added to protect."""
    r = run_gate(_TMP, "The front collapse is a property of the scenario.\n")
    assert r.returncode == 1


def test_prohibition_laundering_still_catches_the_verdict_shape():
    """Round-4 review shape: a boundary between marker and claim must still
    be caught.  The added falsified markers must not launder across it."""
    body = ("Calling the front a search artifact is forbidden; yet the front "
            "collapse is real.\n")
    r = run_gate(_TMP, body)
    assert r.returncode == 1, r.stdout


# --------------------------------------------------------------------------
# C block -- --must-include.  A gate that prints "0 violations over 194
# files" while the draft sits in an unscanned directory is a false green.
# --------------------------------------------------------------------------
def test_must_include_missing_file_fails(tmp_path):
    r = run_gate(tmp_path, "A clean sentence.\n", ".md",
                 "--must-include", str(tmp_path / "nowhere" / "full.md"))
    assert r.returncode == 1
    assert "SCAN SET" in r.stdout


def test_must_include_scanned_file_passes(tmp_path):
    p = tmp_path / "chapter.md"
    p.write_text("A clean sentence.\n", encoding="utf-8", newline="")
    env = dict(os.environ, PYTHONHASHSEED="0")
    r = subprocess.run(
        [sys.executable, "-B", str(CHECKER), "--path", str(tmp_path),
         "--must-include", str(p)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    assert r.returncode == 0, r.stdout


def test_must_include_existing_but_unscanned_file_fails(tmp_path):
    """The exact false green this closes: the file EXISTS and is a valid
    manuscript, but the scan set never covered it."""
    scanned = tmp_path / "scanned"
    scanned.mkdir()
    (scanned / "chapter.md").write_text("A clean sentence.\n",
                                         encoding="utf-8", newline="")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    draft = elsewhere / "full.md"
    draft.write_text("A clean sentence.\n", encoding="utf-8", newline="")
    env = dict(os.environ, PYTHONHASHSEED="0")
    r = subprocess.run(
        [sys.executable, "-B", str(CHECKER), "--path", str(scanned),
         "--must-include", str(draft)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    assert r.returncode == 1
    assert "was NOT scanned" in r.stdout


def test_scan_set_lists_filenames_not_only_a_count(tmp_path):
    """W4 of the workflow: the RESULT line must name the manuscript."""
    p = tmp_path / "chapter.md"
    p.write_text("A clean sentence.\n", encoding="utf-8", newline="")
    env = dict(os.environ, PYTHONHASHSEED="0")
    r = subprocess.run(
        [sys.executable, "-B", str(CHECKER), "--path", str(p)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    assert r.returncode == 0
    assert "chapter.md" in r.stdout, "the scan set was not printed by name"


def test_out_of_repo_path_is_reported_not_crashed(tmp_path):
    """--path outside the repo used to abort with a ValueError traceback from
    relative_to(REPO), so no violation could be reported at all."""
    p = tmp_path / "chapter.md"
    p.write_text("The front collapse is real.\n", encoding="utf-8", newline="")
    r = run_gate(tmp_path, p.read_text(encoding="utf-8"))
    assert r.returncode == 1
    assert "Traceback" not in r.stderr


# --------------------------------------------------------------------------
# Scoping: the writing bans must NOT run on the registration layer, which is
# REQUIRED to quote what it forbids, nor on .py code.
# --------------------------------------------------------------------------
def test_registration_files_are_exempt_from_the_writing_bans():
    for p in (FORK / "experiments" / "analysis_prereg_v2.json",
              FORK / "formulas" / "formula-spec.md"):
        assert not crl._is_manuscript_shaped(p), (
            f"{p} is registration, not manuscript -- the bans must skip it")


# The ticket-50 phase-1 ledger: the EXPECTED red state of the manuscript after
# the W14/W2/W9 patch and BEFORE the phase-2 rewrite.  It is a machine-checked
# artifact so the rewrite list cannot drift from the gate.
LEDGER = Path(__file__).resolve().parent / "data" / "t50_phase1_expected_bans.json"
_VIOLATION_RX = re.compile(
    r"^VIOLATION\s+(?P<label>.+?): (?P<file>[^:]+):(?P<line>\d+) -> ")


def _repo_violations() -> "tuple[int, set]":
    env = dict(os.environ, PYTHONHASHSEED="0")
    r = subprocess.run(
        [sys.executable, "-B", str(CHECKER)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, cwd=FORK.parent.parent)
    got = set()
    for ln in r.stdout.splitlines():
        m = _VIOLATION_RX.match(ln.strip())
        if m:
            got.add((m.group("file"), int(m.group("line")), m.group("label")))
    return r.returncode, got


def test_repo_violation_set_equals_the_registered_phase1_ledger():
    """Ticket 50 phase 1: the manuscript is EXPECTED red until phase 2.

    Equality against a machine-readable ledger, not "no violations": a ban
    whose whitelist is too narrow reddens lines nobody is rewriting (the
    failure this test used to guard), while a ban that never fires silently
    passes.  Pinning the exact expected-red set gives phase 2 its checklist and
    forces an explicit update whenever that list moves; phase 2 shrinks it to
    an empty list and re-runs the gate green.
    """
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    want = {(v["file"], int(v["line"]), v["label"]) for v in ledger["violations"]}
    assert want, "the phase-1 ledger is empty -- the new bans are not firing"
    registered = {lbl for lbl, _pats, _g in crl.WRITING_BANS}
    assert set(ledger["labels"]) <= registered, "ledger names an unregistered ban"
    rc, got = _repo_violations()
    assert rc == 1 and got, "the manuscript must be red until phase 2 rewrites it"
    assert got == want, (
        "expected-red set drifted from the ledger\n"
        f"  new: {sorted(got - want)}\n  gone: {sorted(want - got)}")


def test_violations_outside_the_manuscript_tree_are_empty():
    """The writing bans govern the manuscript.  Audit records under review/ are
    registered out of scope (a reconciliation report MUST quote the retired
    framing in order to audit it); anything else here is a scope leak."""
    _rc, got = _repo_violations()
    stray = {(f, l, lab) for f, l, lab in got if "/paper/" not in f}
    assert stray == set(), f"violations outside paper/: {sorted(stray)}"


def test_review_records_are_not_manuscript_shaped():
    p = FORK / "review" / "retro-project-20261020.md"
    assert p.exists()
    assert not crl._is_manuscript_shaped(p)


# A module-level tmp dir so the helper signatures stay readable.  pytest's
# tmp_path is per-test; the ban table tests share one fixture FILE path.
_TMP = Path(__import__("tempfile").mkdtemp(prefix="t37-"))
