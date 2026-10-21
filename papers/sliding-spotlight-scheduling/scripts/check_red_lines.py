#!/usr/bin/env python3
"""The five prereg red lines as machine checks (ticket 17), plus the
writing-obligation bans of the writing checklist (ticket 37).

The freeze registers them in prose; a prose red line is not a check.  This
script makes each one executable against the repository's own text and code,
so a forbidden claim is caught by the gate rather than by a reader.

The five (spec D15 recut, ticket 17):
  R1  per-pass caliber          -- no per-pass caliber leak in registered artifacts
  R2  forbidden sentences       -- no collapse / phase-transition declarations
  R3  45-degree extrapolation   -- readings beyond the platform envelope are labelled
  R4  no phase-transition claim -- the specific forbidden claim, checked separately
  R5  real-window positioning  -- the main experiment names the real-window family

The writing bans (ticket 37, checklist E section + A1/A3/A4/A7).  These
govern the MANUSCRIPT, not the registration layer, so they are scoped to
manuscript-shaped files (see ``_is_manuscript_shaped``) -- the registration
files legitimately quote every forbidden phrase in order to forbid it:
  W1  A1 plateau, BOTH directions  W2  A1/E1 no-prior-work  W3  E3 capacity
  W4  E4 single-satellite "only N"  W5  E5 45-deg extrapolation label
  W6  E6 density axis               W7  E7 scan/routing bans
  W8  E8 pre-registered effect size  W9  E9 coverage pass/fail
  W10 E10 point-target caliber      W11 A7 zero-violation caliber
  W12 A3 v2 real-window citation   W13 A4 f_q caliber tag
  W14 single-axis positioning (no second / independent objective framing)
  W15a A4 fulfillment-ratio caliber  W15b A4 f_Q_deliv descriptive tag

Scan surface (what this gate does and does NOT read):
  * Default root ``papers/sliding-spotlight-scheduling``; file suffixes
    ``.py/.md/.json/.tex``; ``results/`` and this checker are skipped, as are
    the build caches ``.pytest_cache/`` and ``__pycache__/`` (a cache README
    is not manuscript prose).
  * The W-family bans run ONLY on manuscript-shaped files --
    ``_is_manuscript_shaped``: ``.md``/``.tex``, not under a registration
    directory (experiments / formulas / scripts / sss_core / tests), not
    under ``review/`` (an audit record must quote what it audits), and not
    under ``.scratch/`` unless ``--include-scratch`` is given.
  * ``paper/main.pdf`` (the submission artifact) is NOT scanned.  A PDF is a
    compilation product, not a source of truth: scanning it would let a stale
    build pass while the ``.tex`` is already rewritten, or fail while the
    ``.tex`` is clean.  The manuscript of record this gate polices is
    ``paper/main.tex``; keep the PDF in sync by rebuilding it (a separate
    obligation, see SUBMISSION_CHECKLIST.md).
  * ``paper/refs.bib`` and ``paper/main.bbl`` are NOT scanned: ``.bib`` is a
    citation database and ``.bbl`` is generated from it, and both legitimately
    carry banned tokens inside TITLES OF CITED WORKS (``bi-objective`` in
    zehetner2017sampling / chang2021integrated).  Banning a cited title would
    be banning the literature, not the manuscript's own claim.
  * ``--path`` must exist: a nonexistent path used to yield an empty scan set
    and a clean rc=0, i.e. a green gate over nothing.  It is a usage error
    (rc=2) now.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/check_red_lines.py [--path ...]
        [--must-include <manuscript> ...]

rc:
  0  no red line violated
  1  at least one violated (each reported with file:line)
  2  usage error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent

# Files that legitimately CONTAIN the forbidden phrases because their job is to
# test for them.  The checker excludes itself for this reason; ticket 37's
# fixture file has the same property -- every ban needs a violating sample, and
# writing those samples makes the file a hit on the ban it is testing.  Scoped
# to exact file NAMES, so a new manuscript in tests/ is still scanned.
_SELF_SCAN_EXEMPT = frozenset({"test_writing_red_lines.py"})

# Claims that are falsified and must never appear as ASSERTIONS.  They may
# appear inside a prohibition list (that is where they are supposed to live),
# so every hit is classified by context rather than merely counted.
COLLAPSE_PATTERNS = [
    r"front\s+collapse", r"collapse[sd]?\s+(?:of\s+the\s+)?(?:pareto\s+)?front",
    r"前沿塌缩", r"塌缩前沿",
]
PHASE_PATTERNS = [
    r"phase\s+transition", r"critical\s+exponent", r"percolation",
    r"相变", r"临界指数", r"渗流",
]

# Clause boundaries that separate a prohibition marker from a forbidden
# phrase, turning co-occurrence into laundering (round-4 / R16 review):
# sentence terminators, a spaced dash, and contrastive conjunctions.  A bare
# "and" is NOT a boundary -- "'X' and 'Y' are forbidden" governs both phrases.
CLAUSE_END = (";", "；", ".", "。")
DASH_MARKERS = (" -- ", " – ", " — ", "—")
CONTRAST_RX = re.compile(
    r"(?<![-\w])(?:yet|but|however|although|though|whereas|nevertheless|"
    r"nonetheless)(?![\w-])|然而|不过|但是|却|(?<!不)但",
    re.IGNORECASE,
)


def _has_clause_boundary(segment: str) -> bool:
    """True when a boundary separates a marker from the hit it would shield."""
    return (
        any(t in segment for t in CLAUSE_END)
        or any(d in segment for d in DASH_MARKERS)
        or CONTRAST_RX.search(segment) is not None
    )

# A hit only counts as a violation when it is NOT inside a prohibition.
PROHIBITION_MARKERS = (
    "forbidden", "must never", "never be stated", "not licensed",
    "is forbidden", "禁止", "禁声明", "no statement of", "forbids any",
    # Chinese prohibition markers -- the bare character 禁 over-matches
    # (it appears in ordinary prose), so only the phrase forms count
    "禁再宣称", "禁声明", "禁「", "禁“", "不可宣称", "不得作任何物理声明",
    "禁止",
)


FALSIFIED_MARKERS = (
    "伪影", "已证伪", "作废", "叙事作废", "falsified", "refuted",
    "not licensed", "已被推翻", "撤回",
    # English verdict disclosure (ticket 37).  The registered verdict label
    # for the base-budget collapse is SEARCH-ARTIFACT, so the ordinary way to
    # report it -- "the apparent front collapse was a search artifact" -- is a
    # disclosure of a falsified reading, not an assertion of one.  Without
    # these the COLLAPSE pattern fires on the sentence that withdraws it.
    # Residual risk accepted and documented: a line that both launders and
    # names the verdict is suppressed.  The laundering shape that motivated
    # round-4 review carries a CLAUSE BOUNDARY, and this classifier is
    # line-scoped -- see the W1/W2 checks, which are boundary-aware, for the
    # high-value bans.  Bare "search budget" is NOT a marker (it describes
    # raising the budget, not a verdict); only the artifact-tagged forms are.
    "search artifact", "search-artifact", "budget artifact",
    "budget-artifact", "search-budget artifact", "search budget artifact",
    "已作废", "叙事已作废",
)


def _rel(p: Path) -> str:
    """Repo-relative when possible, absolute otherwise.

    ``Path.relative_to(REPO)`` raises for a path outside the repository, so
    printing a finding for a file passed via ``--path`` from elsewhere (a
    manuscript draft in a scratch dir, a test fixture in tmp) used to abort
    the gate with a traceback instead of reporting the finding.  Reported
    residual: a stack traceback IS a non-zero exit, so the gate could not
    silently pass -- but it could not print the violation either.
    """
    try:
        return p.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return p.as_posix()


def _is_reporting_falsification(text: str, pos: int) -> bool:
    """True when the line REPORTS the claim as falsified rather than making it.

    A keyword scan cannot distinguish "the front collapsed" from "the
    collapse verdict was judged a search-budget artifact and the narrative
    withdrawn".  Measured, several hits in this repository are the second
    kind.  Those are classified as non-violations and PRINTED, so a reader can
    audit each judgement -- tuning the context window until the list is empty
    is how a red-line check becomes a check that never fires.

    Ticket 37 tightened this, because adding the English SEARCH-ARTIFACT
    markers widened what the marker shields and re-opened the round-4
    laundering hole: "Calling the front a search artifact is forbidden; yet
    the front collapse is real" was cleared by the very marker meant to
    describe a falsified reading.  So a marker now shields a hit only when no
    CONTRASTIVE element separates them -- a contrastive conjunction or a
    spaced dash means the sentence asserts the claim *in opposition to* the
    marker, which is laundering.

    Only the contrast test, not the full ``_has_clause_boundary``: the honest
    reporting shape spans sentences inside one line ("... a falsified reading.
    At the base budget the apparent front collapse does not survive the budget
    ladder: ... the reading was a search artifact"), and demanding a
    same-clause marker would red the gate on the repository's own verdict
    records.
    """
    line_start = text.rfind(chr(10), 0, pos) + 1
    line_end = text.find(chr(10), pos)
    line = text[line_start:line_end if line_end != -1 else len(text)]
    before = line[:pos - line_start].lower()
    after = line[pos - line_start:].lower()

    def _nearest(hay: str) -> int:
        best = -1
        for m in FALSIFIED_MARKERS:
            i = hay.rfind(m.lower())
            if i > best:
                best = i
        return best

    pre = _nearest(before)
    if pre != -1 and not _has_contrast(before[pre:]):
        return True
    post = _nearest(after)
    if post != -1 and not _has_contrast(after[:post]):
        return True
    return False


def _has_contrast(segment: str) -> bool:
    """True when a contrastive conjunction / spaced dash splits a segment."""
    return (CONTRAST_RX.search(segment) is not None
            or any(d in segment for d in DASH_MARKERS))


def _is_prohibition(text: str, pos: int) -> bool:
    """True when the hit is inside a prohibition that GOVERNS it.

    Two shapes count, both measured in this repository:

      BEFORE  "禁「前沿塌缩」类声明"        -- marker precedes the phrase
      AFTER   "'X' and 'Y' are forbidden"   -- marker follows and governs
                                             the quoted phrases on the line

    Round-3 review finding: mere co-occurrence is NOT enough.  The
    demonstrated false negative was one sentence carrying a marker that
    belonged to its first clause and laundered a claim in its second:

        "The regime is forbidden to be called a phase transition; yet the
         front collapse is real."

    So a marker shields a hit only when no clause boundary separates them: a
    sentence terminator, a spaced dash, or a contrastive conjunction.  A bare
    "and" does NOT separate -- the prohibition routinely reads "'X' and 'Y'
    are forbidden declarations in every branch" with both phrases governed by
    one trailing marker, and that must still clear.
    """
    nl = chr(10)
    line_start = text.rfind(nl, 0, pos) + 1
    line_end = text.find(nl, pos)
    line = text[line_start:line_end if line_end != -1 else len(text)]
    before = line[:pos - line_start].lower()
    after = line[pos - line_start:].lower()

    def _nearest(hay: str) -> int:
        best = -1
        for m in PROHIBITION_MARKERS:
            i = hay.rfind(m.lower())
            if i > best:
                best = i
        return best

    # A clause boundary also separates: the demonstrated laundering is
    # "forbidden to be called a phase transition; yet the front collapse is
    # real" -- a semicolon (or ", yet", or " -- ") ends the governed clause.
    # The legitimate AFTER shape ("'X' and 'Y' are forbidden declarations") is
    # a single clause with no internal boundary, so a clause-level test keeps
    # it while catching the laundering.
    pre = _nearest(before)
    if pre != -1 and not _has_clause_boundary(before[pre:]):
        return True
    post = _nearest(after)
    if post != -1 and not _has_clause_boundary(after[:post]):
        return True
    return False


def scan_texts(paths, patterns, label, violations, cleared):
    rx = re.compile("|".join(patterns), re.IGNORECASE)
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue
        for m in rx.finditer(text):
            line = text[:m.start()].count("\n") + 1
            if _is_prohibition(text, m.start()):
                cleared.append((label, p, line, m.group(0),
                                "inside a prohibition"))
                continue
            if _is_reporting_falsification(text, m.start()):
                cleared.append((label, p, line, m.group(0),
                                "reports it as falsified"))
                continue
            violations.append(
                f"{label}: {_rel(p)}:{line} -> {m.group(0)!r}"
            )


# ---------------------------------------------------------------------------
# Writing-obligation bans (ticket 37)
# ---------------------------------------------------------------------------
# The five R-lines above police the registration layer, and that layer MUST
# quote every forbidden phrase in order to forbid it.  The bans below police
# the MANUSCRIPT instead: a draft that says "the front has plateaued" is
# wrong even though analysis_prereg_v2.json says the same words inside a
# prohibition.  So they run on manuscript-shaped files only -- see
# ``_is_manuscript_shaped``.
#
# Every ban reuses the two context classifiers above rather than a bare count:
# the mandatory obligations D-6 / figure-caption REQUIRE the very strings some
# of these patterns match, so a keyword scan alone would make the gate
# permanently red (ticket A-block deadlock).

# (dir, file) components that are registration / provenance, not manuscript.
_REGISTRATION_DIRS = ("experiments", "formulas", "scripts", "sss_core", "tests")

# Build caches that must never enter the scan set.
_SKIP_DIR_NAMES = frozenset({".pytest_cache", "__pycache__", ".mypy_cache",
                             ".git", ".ruff_cache"})

# ---------------------------------------------------------------------------
# Contexts that license a RETROSPECTIVE mention (ticket 50, W14 / W15).
# ---------------------------------------------------------------------------
# The single-axis positioning retires the dual-objective framing, so the
# manuscript must stay free to say what it NO LONGER does: "we no longer treat
# image quality as a second objective", "the former two-objective formulation".
# Three shapes license a hit, each a REUSE of an existing classifier rather
# than a third notion of context:
#   * prohibition   -- PROHIBITION_MARKERS, CLAUSE-scoped (_clause_marker);
#   * withdrawal    -- the FALSIFIED_MARKERS vocabulary, CLAUSE-scoped;
#   * retrospective -- the regex below, BOUND to the banned phrase.
#
# A bare retro participle is not enough.  The phase-1 gate pass demonstrated
# that a free-floating "replaced" clears "replacing the fixed dwell makes
# quality a second objective", which ASSERTS the framing; so each alternative
# below ties the retro word to the banned construction itself.
_RETROSPECTIVE_RX = re.compile(
    r"\bno\s+longer\s+(?:an?\s+)?(?:second|secondary|independent|dual|two)\b"
    r"|\bno\s+longer\s+(?:treat|treats|carry|carries|use|uses|model|models|"
    r"regard|regards|formulate|formulates|claim|claims)\w*\b"
    r"|\b(?:former|formerly|retired|superseded|replaced|withdrawn)\s+"
    r"(?:\w+\s+){0,4}(?:two|dual|bi)[-\s]?objective\b"
    r"|\b(?:was|is|has\s+been)\s+withdrawn\b"
    r"|\b(?:two|dual|bi)[-\s]?objective\s+(?:formulation|framing|problem)\b"
    r"[^.\n]{0,40}\b(?:retired|superseded|withdrawn|replaced)\b"
    r"|不再[^。\n]{0,12}(?:第二目标|双目标|独立目标)"
    r"|(?:原|旧)(?:先|来|有)?的?(?:双目标|两目标|第二目标)[^。\n]{0,12}"
    r"(?:作废|退役|取消|不再)"
    r"|(?:双目标|第二目标)[^。\n]{0,12}(?:作废|退役|取消)",
    re.IGNORECASE,
)

# "not a second objective" is only a RETIREMENT when it negates OUR framing.
# The same words appear in the banned gap sentence -- "the quality-aware line
# supplies requirement-level mode selection but not a second objective" -- which
# ASSERTS that the paper carries one (phase-1 review finding: a free-floating
# negation cleared the assertion).  So the negation must sit next to a
# first-person / this-paper subject.
#
# ``[-\s]+`` rather than ``\s+``: the hyphenated compound ("not a
# second-objective study") is the same claim and was firing as a false positive
# (F1 in the discrimination probe).
_NEGATED_IN_PAPER_RX = re.compile(
    r"\b(?:we|our|this\s+(?:paper|work|study))\b[^.\n]{0,80}"
    r"\bnot\s+(?:an?|the)\s+(?:second|secondary|independent)[-\s]+"
    r"(?:objective|target)\b"
    r"|\bnot\s+(?:an?|the)\s+(?:second|secondary|independent)[-\s]+"
    r"(?:objective|target)\b[^.\n]{0,40}"
    r"\b(?:in|for)\s+this\s+(?:paper|work|study)\b"
    r"|\b(?:we|our|this\s+(?:paper|work|study))\b[^.\n]{0,80}"
    r"\bnot\s+(?:an?|the)\s+objective\s+dimension\b"
    r"|\bnot\s+(?:an?|the)\s+objective\s+dimension\b[^.\n]{0,40}"
    r"\b(?:in|for)\s+this\s+(?:paper|work|study)\b"
    # "This paper does NOT CARRY an image-quality objective as an independent
    # objective dimension" -- the negated VERB form of the same retirement.
    # Round-2 self-attack finding: the noun-phrase alternatives above cover
    # "is not a second objective", not "does not carry ... as an objective".
    #
    # The bridge between the verb and "objective" is tempered against a bare
    # "and": "We do not model quality post hoc AND the quality index is a
    # second objective" is an assertion, and the untempered window licensed it
    # (round-2 audit finding).
    r"|\b(?:we|our|this\s+(?:paper|work|study))\b[^.\n]{0,80}"
    r"\b(?:do|does|did|will|would)?\s*not\s+"
    r"(?:carry|treat|use|model|formulate|regard|optimise|optimize|include)\b"
    r"(?:(?!\band\b)[^.\n]){0,60}\bobjectives?\b",
    re.IGNORECASE,
)


def _clause_marker(line: str, pos: int, markers) -> str:
    """The first marker sitting in the hit's OWN clause, or ''.

    Clause scope is the fix the phase-1 review asked for.  ``_is_prohibition``
    deliberately does not treat a comma as a boundary (one prohibition can
    govern "'X' and 'Y' are forbidden"), so on a long line a prohibition in a
    LATER comma-clause cleared an assertion in an earlier one:

        "The second objective is retained, and calling the schedule a physical
         limit is forbidden."          <- cleared under line scope, must fire

    Restricting the marker to ``_clause_around`` closes that shape without
    narrowing the legitimate one-clause prohibition.
    """
    clause, _start = _clause_around(line, pos)
    if clause is None:
        return ""
    low = clause.lower()
    for mk in markers:
        i = low.find(mk.lower())
        if i != -1 and not _has_contrast(low[i:]):
            return mk
    # A colon-introduced prohibition list ("Forbidden: X, Y", "禁：X") puts the
    # marker in the PREVIOUS clause, because _LABEL_CLAUSE_CUTS contains ':'.
    # Without this branch the listed phrases fired on the marker that forbids
    # them (false positive F3 in the discrimination probe).
    if _start is not None and _COLON_PROHIBITION_RX.search(line[: _start]):
        return "colon-introduced prohibition"
    return ""


def _marker_gap(line: str, pos: int, marker: str, hit_end: int = None) -> str:
    """Text between the hit and the nearest occurrence of ``marker``.

    Used for the laundering vetoes: a marker only governs a hit it is adjacent
    to.  When an independent clause sits in between, the marker belongs to that
    clause and must not license this hit.

    ``hit_end`` extends the BEFORE-marker gap to the end of the matched phrase.
    Without it a pattern that spans its own copula ("quality IS a second
    objective") hid the copula from the check, and "… is forbidden and image
    quality is a second objective" cleared (round-2 audit finding).
    """
    clause, start = _clause_around(line, pos)
    if clause is None:
        return ""
    low = clause.lower()
    mk = marker.lower()
    before = low.rfind(mk, 0, max(0, pos - start))
    if before != -1:
        end = hit_end if hit_end is not None else pos
        return line[start + before + len(mk): end]
    after = low.find(mk, max(0, pos - start))
    if after != -1:
        begin = hit_end if hit_end is not None else pos
        return line[begin: start + after]
    return ""


# Ticket-50 discrimination probe, defect H4: "Image quality is a second
# objective and any statement to the contrary is forbidden."  The trailing
# "and" does not end the clause (a deliberate design choice -- "'X' and 'Y' are
# forbidden" governs both phrases), so the prohibition marker at the end of the
# sentence shielded an assertion in its middle.  A marker whose object is
# ANOTHER proposition ("any statement to the contrary", "otherwise", "any
# claim") is not a licence for this one.
_PROHIBITION_LAUNDER_RX = re.compile(
    r"to\s+the\s+contrary|otherwise|\bcontrary\s+to\b|any\s+statement|"
    r"no\s+statement|any\s+claim|den(?:y|ies|ied)|counts?\s+as|"
    r"\b(?:say|state|claim|write)s?\s+otherwise\b|\bit\s+(?:is|was)\b",
    re.IGNORECASE)

# A copula inside the gap that is NOT the marker's own auxiliary means the
# marker has a different subject: "… is forbidden and image quality IS a second
# objective" (the round-2 cross-line case).  In the legitimate AFTER shape
# ("'X' and 'Y' ARE forbidden") the copula sits immediately before the marker,
# so it does not count.
_COPULA_NOT_GOVERNING_RX = re.compile(
    r"\b(?:is|are|was|were|be|been|has|have|had)\b(?!\s*$)", re.IGNORECASE)

# Ticket-50 discrimination probe, defect H5: a retrospective shell that KEEPS
# the framing.  "The former two-objective formulation is retained as the core
# framing of this paper" reports the old framing as former while asserting it
# is the paper's framing; the retro word must not license a retention verb in
# the same clause.
#
# The vocabulary is deliberately tied to a FRAMING object where the verb is
# generic.  Round 2 showed both failure directions: a bare `\bstill\b` /
# `\bremains?\b` vetoed the legitimate "… is retired and coverage still governs
# the schedule" (phase 2 will write exactly that), while a narrow list let
# "survives as the organising principle" / "is what this paper builds on" /
# "is adopted throughout this paper" through.  So: retain/keep are retained as
# bare markers (they have no other object in this manuscript), and the rest
# need a framing complement.
_RETENTION_RX = re.compile(
    r"\bretain(?:s|ed|ing)?\b|\bwe\s+keep\b|\bkeeps?\b|\bkept\b"
    r"|\bis\s+still\b|\bwas\s+still\b"
    r"|\bstays?\s+(?:central|the\s+(?:core|framing|principle)|what)\b"
    r"|\bremains?\s+(?:the\s+)?(?:core|central|framing|first-class|what|our|"
    r"organis\w*|organiz\w*)"
    r"|\bremains?\s+(?:an?\s+)?(?:second|independent|primary)?\s*objectives?\b"
    r"|\bstill\s+(?:defines?|central|the\s+(?:framing|core|organis\w*|"
    r"organiz\w*|principle)|what\s+(?:this\s+)?paper)\b"
    r"|\bsurviv(?:es|ed)\s+(?:as|the)\b|\bbuilds?\s+on\b"
    r"|\badopt(?:s|ed)?\s+throughout\b"
    r"|\bcore\s+framing\b|\bas\s+the\s+contribution\b|\bis\s+the\s+contribution\b"
    r"|\borganis(?:es|ing)\s+principle|\borganiz(?:es|ing)\s+principle"
    r"|保留|仍是|仍为|仍旧|核心框架|组织原则",
    re.IGNORECASE)

# A falsified-verdict marker ("search artifact") licenses a hit only when it is
# adjacent to it.  "The search artifact reading is retired and image quality is
# a second objective" puts an independent subject+predicate between the marker
# and the claim, so the marker describes a different clause (defect K1).
_INDEPENDENT_PREDICATE_RX = re.compile(
    r"\b(?:is|are|was|were|remains?|becomes?|has|have|had)\b", re.IGNORECASE)

# "neither axis is an objective", "the axes are not objectives" -- the retired
# framing NEGATED in the hit's own clause.
_NEGATED_OBJECTIVE_IN_CLAUSE_RX = re.compile(
    r"\b(?:not|neither|nor|never|no)\b[^.\n]{0,40}\bobjectiv", re.IGNORECASE)


def _clear_dual_objective(line: str, m) -> str:
    """W14: asserting the retired framing is banned; a retrospective or
    negated mention of it is licensed."""
    token = (m.group(0) or "").lower()
    clause, _start = _clause_around(line, m.start())
    # The promotion verdict's axes are not objectives, and the manuscript is
    # allowed to SAY so: "stated on two separated axes and neither axis is an
    # objective" is the retired framing being negated, not asserted (round-2
    # false positive).  Restricted to axis hits so it cannot launder a
    # "second objective" claim that merely shares a clause with a negation.
    if "ax" in token and clause and _NEGATED_OBJECTIVE_IN_CLAUSE_RX.search(clause):
        return "the axes are negated as objectives in this sentence"
    mk = _clause_marker(line, m.start(), PROHIBITION_MARKERS)
    if mk:
        # The marker must govern THIS hit: a prohibition whose object is some
        # other proposition ("any statement to the contrary is forbidden") does
        # not license the assertion it trails (H4).  A copula in the gap that
        # is not the marker's own auxiliary means the marker has another
        # subject (round-2 cross-line case).
        gap = _marker_gap(line, m.start(), mk, hit_end=m.end())
        if not (_PROHIBITION_LAUNDER_RX.search(gap)
                or _COPULA_NOT_GOVERNING_RX.search(gap)):
            return f"inside a prohibition ({mk!r})"
    mk = _clause_marker(line, m.start(), FALSIFIED_MARKERS)
    if mk:
        # "is NOT withdrawn" negates the retraction and therefore ASSERTS the
        # framing; the falsified vocabulary must not become a licence for it.
        clause, _start = _clause_around(line, m.start())
        if re.search(r"\bnot\s+(?:\w+\s+){0,2}(?:withdrawn|retired|superseded|"
                     r"replaced|falsified|refuted)\b|未(?:作废|退役|取消|撤回)",
                     clause or "", re.IGNORECASE):
            return ""
        # An independent predicate between marker and claim means the marker
        # attaches to another clause (K1).
        gap = _marker_gap(line, m.start(), mk)
        if _INDEPENDENT_PREDICATE_RX.search(gap) or _RETENTION_RX.search(gap):
            return ""
        return f"reports the framing as withdrawn ({mk!r})"
    clause, _start = _clause_around(line, m.start())
    if clause and (_RETROSPECTIVE_RX.search(clause)
                   or _NEGATED_IN_PAPER_RX.search(clause)):
        # The retro shell must not carry a retention claim in the same clause:
        # "the former two-objective formulation is retained as the core framing"
        # reports a withdrawal it does not make (H5).
        if _RETENTION_RX.search(clause):
            return ""
        return "retrospective mention in the hit's own clause"
    return ""


def _clear_no_prior_work(line: str, m) -> str:
    """W2 after ticket 50 retired the spec.md:82 conjunction licence.

    The retired licence was a WHITELIST for the dual-objective conjunction.
    With the second objective gone, that conjunction is no longer the paper's
    claim, so W2 takes the sentence over.  The guard therefore licenses only
    the quote-to-forbid and explicit-retraction shapes -- deliberately NOT
    ``_is_reporting_falsification``: its "search artifact" / "budget artifact"
    markers share long manuscript lines with the no-prior-work sentence
    (main.tex:59, full.md:40), which laundered exactly the claim this ban must
    catch (phase-1 review finding).
    """
    mk = _clause_marker(line, m.start(), PROHIBITION_MARKERS)
    if mk:
        return f"inside a prohibition ({mk!r})"
    clause, _start = _clause_around(line, m.start())
    if clause and re.search(
            r"\bno\s+longer\s+(?:claim|claims|make|makes)\b|\bnot\s+claimed\b"
            r"|\bwithdrawn\b|不再声称|不作宣称", clause, re.IGNORECASE):
        return "explicitly retired claim"
    return ""

# A frontier-richness VERDICT label used as a qualifier/annotation is licensed:
# "carrying the NOT-PLATEAUED caveat", "NOT-PLATEAUED at 160/240".  The same
# word as an INDEPENDENT assertion about the front is banned in BOTH
# directions (checklist A1 / E2): neither "the front has plateaued" nor "the
# front has not plateaued, therefore richness is bounded".
_VERDICT_LABEL_RX = re.compile(
    r"(?:NOT[\s\-_]*PLATEAUED|SEARCH[\s\-_]*ARTIFACT|"
    r"PLATEAUED|平台期|未平台|已平台|搜索伪影|塌缩叙事已作废)",
    re.IGNORECASE,
)

# A hyphenated verdict LABEL standing on its own -- the shape the figure-caption
# obligation and checklist D-6 actually produce ("richness at 160/240
# (NOT-PLATEAUED; ...)", "Reported as NOT-PLATEAUED; ...").  It is a separate
# test from _QUALIFIER_RX because it must NOT fire inside the banned assertion
# "the front has not plateaued": there the same characters follow a copula and
# are part of a claim, not a label.  Regex alternatives could not express the
# difference (an unguarded ``NOT[\s-]*PLATEAUED`` matched inside "has NOT
# plateaued" and whitelisted a banned sentence), so the check is positional.
_VERDICT_LABEL_TOKEN_RX = re.compile(r"NOT[\s\-_]*PLATEAUED", re.IGNORECASE)
_COPULA_BEFORE_LABEL_RX = re.compile(
    r"\b(?:has|have|had|is|are|was|were|does|do|did)\s+$", re.IGNORECASE)
# Boundaries of the clause a label modifies.
_LABEL_CLAUSE_CUTS = (";", "；", ":", "：", ",", "，", "(", ")", "[", "]",
                      "。", ".", "—", "–")

# A prohibition that INTRODUCES a list with a colon ("Forbidden: ...", "禁：...")
# sits in the previous clause by construction, because the clause cut includes
# ':' / '：'.  The listed phrases are exactly what it forbids, so the marker
# must govern them (false-positive F3 in the ticket-50 discrimination probe).
#
# The colon form is NARROW: the marker must open the line (list style) or be
# predicated of a meta-noun ("the phrase/label/term ... is forbidden:").
# Otherwise "…is forbidden: <a full assertion>" became a free licence for
# whatever followed the colon (round-2 audit finding).
_COLON_PROHIBITION_RX = re.compile(
    r"^\s*(?:[-*+]\s*)?(?:forbidden|prohibited|banned|禁[止用]?|不得)\s*[:：]"
    r"|\b(?:phrases?|phrasings?|labels?|terms?|wordings?|statements?|claims?|"
    r"words?|表述|措辞|声明|说法|措辞)\b[^.\n:：]{0,40}"
    r"(?:forbidden|prohibited|banned|禁止|禁|不得)\s*[:：]",
    re.IGNORECASE)


def _clause_around(line: str, pos: int) -> tuple:
    """The clause containing ``pos`` as (text, start_index), or (None, None).

    Clause-scoped context is what stops a qualifier from licensing a claim it
    does not modify.  Returns None when the hit opens its clause, i.e. there is
    no enclosing clause to test.
    """
    lo = max((line.rfind(c, 0, pos) for c in _LABEL_CLAUSE_CUTS), default=-1)
    hi_cuts = [line.find(c, pos) for c in _LABEL_CLAUSE_CUTS]
    hi_cuts = [h for h in hi_cuts if h != -1]
    hi = min(hi_cuts) if hi_cuts else len(line)
    return line[lo + 1: hi], lo + 1


def _standalone_label_is_qualifier(line: str, pos: int) -> bool:
    """True when the label nearest ``pos`` is a LABEL, not a claim.

    Scoped to the label's own CLAUSE, not the whole line.  A line can carry
    both a licensed label and a banned assertion -- "(NOT-PLATEAUED; the front
    has not plateaued)" is the exact shape the earlier line-level version got
    wrong in both directions: it cleared the whole line because a label
    appeared somewhere, and it failed the licensed caption because a banned
    phrase followed.  Cutting at the nearest clause boundary (semicolon, comma,
    colon, bracket, sentence terminator) means each label is judged against
    the words that actually modify it, so "reported as NOT-PLATEAUED" clears
    while "the front HAS NOT plateaued" does not -- in the same sentence.
    """
    best = None
    for m in _VERDICT_LABEL_TOKEN_RX.finditer(line):
        if best is None or abs(m.start() - pos) < abs(best - pos):
            best = m.start()
    if best is None:
        return False
    lo = max((line.rfind(c, 0, best) for c in _LABEL_CLAUSE_CUTS), default=-1)
    pre = line[lo + 1: best]
    return not _COPULA_BEFORE_LABEL_RX.search(pre)


# Qualifier / annotation context: the label is attached to a caveat, a figure
# caption tag, a verdict token, or a "both directions" prohibition.
_QUALIFIER_RX = re.compile(
    r"caveat|qualifier|qualif(?:y|ied)|tag(?:ged)?\b|label(?:led)?\b|"
    r"as\s+an?\s+(?:annotation|qualifier|caveat|label)|"
    # The verdict label ITSELF in qualifier position: "Reported as
    # NOT-PLATEAUED; ...", "richness at 160/240 (NOT-PLATEAUED; ...)".
    # Without this the two shapes the figure-caption obligation and D-6
    # actually produce -- a bare label, no "caveat" word -- were violations,
    # i.e. the whitelist missed precisely the strings it exists to license.
    #
    # The hyphenated label is REQUIRED here.  An unhyphenated alternative let
    # ``h[as not plateaued]`` match inside the ordinary banned phrase "the front
    # has not plateaued" -- a false negative created by the fix for a false
    # positive.  The parenthesised / delimited forms must also close, so a
    # banned clause cannot hide behind an opening bracket.
    r"NOT[\s\-_]*PLATEAUED[\s\-_]*caveat|"
    r"(?:reported|labelled|labeled|tagged|carrying|carries|carry)\s+"
    r"(?:the\s+)?NOT[\s\-_]*PLATEAUED\b|"
    r"(?:is|are|be|been)\s+(?:carried|attached|stated|required|mandated|"
    r"disclosed|reported|marked|flagged)|"
    r"must\s+(?:carry|state|be)|"
    r"under\s+the\s+NOT|per\s+the\s+NOT|per\s+the\s+NOT[\s\-_]*PLATEAUED|"
    r"(?:in|both|either)\s+directions?|two[\s\-_]way|"
    r"forbidden\s+in\s+both|"
    r"(?:仍|仍\s*未|依|按|受|接受)\s*(?:NOT|未)?[\s\-_]*(?:PLATEAUED|平台)|"
    r"标注|限定语|判词|条款|须带|必带|必标|需带|双(?:向|向都)",
    re.IGNORECASE,
)

# Prohibition / falsification context, re-used for the verdict checks so a
# checklist sentence that quotes the ban stays clean.
_REPORTING_RX = re.compile(
    r"|".join(
        [
            r"forbidden", r"must\s+never", r"never\s+be\s+stated", r"禁",
            r"禁\s*禁", r"不得", r"不可宣称", r"已证伪", r"作废",
            r"falsified", r"refuted", r"withdrawn", r"void",
            r"pseudo\s*[- ]?proof",
        ]
    ),
    re.IGNORECASE,
)


# Set by ``--include-scratch``.  The flag used to add the scratch directory to
# the FILE set while ``_is_manuscript_shaped`` kept filtering every W-family
# hit out of it, so the flag was a no-op for the writing bans (probe defect
# M8).  The module-level switch makes the flag mean what its help says.
_INCLUDE_SCRATCH = False


def _is_manuscript_shaped(p: Path) -> bool:
    """True when a file can hold manuscript prose rather than registration.

    The writing bans would fire on every file that registers a ban -- the
    registry is REQUIRED to quote what it forbids -- so they are scoped to
    text the author writes.  A manuscript is .md/.tex, is not under a
    registration directory, and is not the checker itself.
    """
    if p.suffix not in (".md", ".tex"):
        return False
    try:
        rel = p.resolve().relative_to(REPO)
    except ValueError:
        rel = p                      # out-of-repo -- treat as manuscript
    if any(part in _REGISTRATION_DIRS for part in rel.parts):
        return False
    if rel.as_posix().startswith(".scratch/") and not _INCLUDE_SCRATCH:
        return False
    # Review records (review/) are audit artifacts, not manuscript prose: a
    # reconciliation report MUST quote the retired framing in order to audit
    # it, exactly like the registration layer it audits.  Scoping them out is
    # not a weakening -- the manuscript stays in scope -- it prevents a
    # permanently red gate after the manuscript is rewritten, which is the
    # "nobody reads it" failure mode (ticket-50 phase-1 decision; the receipt
    # records the measured before/after counts).
    if any(part == "review" for part in rel.parts):
        return False
    return p.resolve() != Path(__file__).resolve()


def _drop_fences(text: str) -> str:
    """Remove fenced blocks whole, keeping the line count intact.

    A ban quoted inside a code fence is not a claim, but a per-line filter
    only sees the fence DELIMITER lines -- the payload between them was still
    scanned and fired.  Blanking the payload keeps every reported line number
    pointing at the original file.
    """
    out, in_fence = [], False
    for ln in text.splitlines():
        if ln.strip().startswith(("```", "~~~")):
            in_fence = not in_fence
            out.append("")
        else:
            out.append("" if in_fence else ln)
    return "\n".join(out)


def _strip_markup(line: str) -> str:
    """Drop TeX commands and code fences, but KEEP what they wrap.

    Four traps, all measured on fixtures rather than assumed:

    * A code fence is not prose -- see ``_drop_fences``, which handles the
      payload, not just the delimiter.
    * ``$f_Q$`` and ``\\rho_{a,\\mathrm{ach}}`` put the SYMBOL inside the math
      delimiters and braces, so deleting math bodies silently disarmed every
      ban in a .tex manuscript (the ticket's W5.5 step runs this gate against
      the elsarticle port).  A command name is therefore kept as a bare word
      (``\\rho`` -> ``rho``) and the grouping characters are deleted, so
      ``\\rho_{a,\\mathrm{ach}}`` collapses to ``rho a, ach`` -- one token a
      regex can match, instead of a symbol that vanishes and disarms W7.
    * ``\\label{}`` / ``\\ref{}`` must not manufacture prose.  They leave
      ``label``/``ref`` plus the key text, neither of which is a banned token.
    * SPACING is spacing.  LaTeX has a dozen ways to write a word gap
      (``~``, ``\\,``, ``\\;``, ``\\:``, ``\\ ``, ``\\thinspace``,
      ``\\\\``, ``\\text{ }``) and a dozen formatting wrappers (``\\emph{X}``,
      ``\\textbf{X}``, ``\\text{X}``).  Left unnormalised, each one splits a
      banned phrase into tokens no pattern matches: ``second~objective``,
      ``second\\emph{objective}`` (which became ``second emph objective``) and
      ``second\\\\objective`` (where the bare-command rule ate ``\\\\objective``
      whole) were all invisible (defect H8 in the discrimination probe).  They
      are normalised to a single space, or to their content, BEFORE the command
      rules run.
    """
    line = line.strip()
    if line.startswith(("```", "~~~")):
        return ""
    # -- spacing, before any command rule can treat it as a command ----------
    line = line.replace("\\\\", " ")                     # TeX line break
    line = re.sub(r"\\[,;:!/ ]", " ", line)              # \, \; \: \! \/ "\ "
    line = line.replace("\\-", "-")                      # discretionary hyphen
    line = line.replace("~", " ")                        # non-breaking space
    line = re.sub(r"\\(?:thinspace|enspace|quad|qquad|hfill|hspace\*?"
                  r"\{[^{}]*\})", " ", line)
    # -- formatting wrappers keep their CONTENT and drop their name ----------
    # The wrapper list is a whitelist and will always be missing one; the ones
    # here are the forms a LaTeX draft actually uses to break a phrase
    # (round-2 self-attack: \mbox{ }, \textup{ }, \mathit{objective},
    # \operatorname{deliv} all survived the first cut).
    for _ in range(2):
        line = re.sub(r"\\(?:emph|textbf|textit|textrm|textup|textsl|textmd|"
                      r"textnormal|textsc|textsuperscript|textsubscript|text|"
                      r"mathrm|mathit|mathbf|mathsf|mathtt|operatorname|mbox|"
                      r"hbox|fbox)\s*\{([^{}]*)\}", r" \1 ", line)
    # \command[opt]_{arg} -> "command arg"  (name kept, argument kept).  The
    # subscript/superscript group is where the math symbols live: without it
    # ``\rho_{a,\mathrm{ach}}`` lost "rho" to the bare-command rule below and
    # W7 could never match a .tex draft.  The argument pattern admits ONE
    # nested level and the substitution runs to a fixpoint, because the real
    # notation nests (``\mathrm{ach}`` inside ``_{...}``) and a single pass
    # leaves the inner command unexpanded -- which is exactly the shape that
    # produced the silent false negative on the .tex fixture.
    _arg = r"((?:[^{}]|\{[^{}]*\})*)"
    for _ in range(4):
        before = line
        line = re.sub(r"\\([a-zA-Z]+)\*?(?:\[[^\]]*\])?[_\^]?\{" + _arg + r"\}",
                      r" \1 \2 ", line)
        line = re.sub(r"\\([a-zA-Z]+)\*?(?:\[[^\]]*\])?\{" + _arg + r"\}",
                      r" \1 \2 ", line)
        if line == before:
            break
    # A bare \command (spacing macros, \rho with no group)
    line = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", " ", line)
    # TeX's escaped literal ``\_`` is an UNDERSCORE, not a subscript command.
    # Deleting the backslash turned ``v2\_results`` into ``v2results``.  The
    # underscore itself is KEPT: it is part of the tokens the bans match
    # (``v2_results``, ``f_q``), and blanking it merged ``v2`` with ``results``
    # and let the W12 ban through.
    line = line.replace("\\_", "_")
    for ch in ("$", "{", "}"):
        line = line.replace(ch, " ")
    return re.sub(r"[ \t]{2,}", " ", line)


# A numeral that belongs to a cross-reference is not a reading of the symbol
# before it ("f_Q is defined in Eq.(9)").  Truncate the look-ahead here.
_XREF_RX = re.compile(
    r"\b(?:Eq|Eqn|Equation|Fig|Figure|Table|Tab|Sec|Section|Ref|Appendix|"
    r"Alg|Algorithm|Lst|Lemma|Thm|Prop|Cor)\b\.?|§", re.IGNORECASE)


def _line_has_bound_marker(line: str) -> bool:
    """True when the line is listing / prohibiting, not asserting."""
    return bool(_REPORTING_RX.search(line))


def _line_index(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _line_start(text: str, pos: int) -> int:
    """Offset of the first character of the line containing ``pos``."""
    return text.rfind("\n", 0, pos) + 1


class _RelMatch:
    """A match proxy whose offsets are relative to the LINE a guard receives.

    ``guard(line, m)`` is documented as operating on ONE line, but the match
    object came from the WHOLE document: for any hit below line 1,
    ``m.start()`` exceeded the line length, so ``line[:m.start()]`` was the
    whole line and ``line[m.start():]`` was empty.  Every positional guard
    (W1's qualifier, W13's reading detector, the W14/W15 additions) silently
    judged the wrong text -- the phase-1 review demonstrated the same sentence
    clearing on line 1 and firing on line 2.  Offsets are rebased here, once,
    instead of patching each guard.
    """

    __slots__ = ("_m", "_off")

    def __init__(self, m, off: int):
        self._m, self._off = m, off

    def start(self) -> int:
        return self._m.start() - self._off

    def end(self) -> int:
        return self._m.end() - self._off

    def group(self, *args):
        return self._m.group(*args)



def _guard(clear_if):
    """Adapt a clearance predicate into the guard signature."""
    def _guard(line: str, m) -> "str | None":
        return clear_if(line, m) or None
    return _guard


def _clear_by_regex(*rxs):
    """Clearance from context regexes, mirroring ``_is_prohibition``'s shape."""
    c = [re.compile(r, re.IGNORECASE) for r in rxs]
    def _f(line: str, _m) -> str:
        for rx in c:
            if rx.search(line):
                return f"licensed context: {rx.pattern[:40]!r}"
        return ""
    return _f


# A caliber obligation applies to a READING, and a reading is a number BOUND to
# the symbol -- "f_q reached 84.5", "f_q = 84.5", "f_q ranges 1.35", "f_q
# 中位数为 84.5".  A digit that merely follows within a window is not one, and
# the phase-1 review (with the offset rebased) showed why the window test is
# too loose: "f_q domains over all 90 promotion units", an image link
# "![fig-3 Per-mode f_q versus squint](figures/fig3_...)" and the definition
# "f_{q,i}=\frac{1}{...}" all carry a digit without stating a reading.
_READING_BINDING = (
    r"(?:=|＝|≈|:|：|of|is|are|was|were|reached|reaches|reads?|reading|"
    r"ranges?|values?|equals?|median|中位数\s*为|中位数|为|达|是|约|范围)"
)
# A binding word may be followed by a copula before the number: "the value IS
# 71.3", "the ratio, computed on the library f_q, WAS 0.62".  The first cut
# required the number to sit immediately after the binding token, so
# "the f_Q_deliv value is 71.3" was read as "no reading on the line" and the
# caliber obligation never started (defect M3 in the discrimination probe).
_READING_AFTER_RX = re.compile(
    r"\s*" + _READING_BINDING + r"\s*(?:of\s*)?"
    r"(?:(?:is|are|was|were|equals?|reaches?|reads?|of)\s*)?"
    r"[-+]?\d+(?:\.\d+)?",
    re.IGNORECASE,
)
# The same, when a parenthetical / participial bridge separates the token from
# its binding ("the fulfillment ratio, computed on the library f_q, reached
# 0.62").  Anchored at the token and bounded at 40 characters with no sentence
# terminator, so a digit belonging to a LATER sentence cannot bind here.
_READING_BRIDGED_RX = re.compile(
    r"[^.\n]{0,40}?" + _READING_BINDING + r"\s*(?:of\s*)?"
    r"(?:(?:is|are|was|were|equals?|reaches?|reads?)\s*)?"
    r"[-+]?\d+(?:\.\d+)?",
    re.IGNORECASE,
)


def _states_a_reading(line: str, m) -> bool:
    """True when the hit's token is actually BOUND to a number on this line.

    Shared by W13 (f_q) and W15 (fulfillment ratio / f_Q_deliv): a formula
    mention is not a reading, so a digit that belongs to a cross-reference
    ("f_q is defined in Eq.(9)", "see Table 4") must not trip the obligation.
    """
    tail = line[m.end(): m.end() + 60]
    xref = _XREF_RX.search(tail)
    if xref:
        tail = tail[:xref.start()]
    if _READING_AFTER_RX.match(tail):
        return True
    return bool(_READING_BRIDGED_RX.match(tail))


def _clear_plateau_qualifier(line: str, m) -> str:
    """A1 deadlock resolution: verdict LABEL vs richness ASSERTION.

    Legal  = the verdict label used as a qualifier/annotation ("carries the
             NOT-PLATEAUED caveat", "NOT-PLATEAUED at 160/240"), or a line
             that is prohibiting / reporting the falsified reading.
    Illegal= a standalone claim that the front HAS plateaued, or that it HAS
             NOT plateaued and therefore carries a richness bound.

    Every context test here is CLAUSE-SCOPED, and that is the whole design.
    The first version asked "does this LINE contain a qualifier word?" and
    therefore whitelisted "the readings carry the NOT-PLATEAUED caveat: the
    ladder HAS NOT PLATEAUED" -- the caveat licensed a banned claim two clauses
    later.  A label licenses the words it modifies and nothing else, so the
    qualifier must appear in the hit's own clause.
    """
    if _is_prohibition(line, m.start()):
        return "inside a prohibition"
    if _is_reporting_falsification(line, m.start()):
        return "reports it as falsified"
    clause, _start = _clause_around(line, m.start())
    if _QUALIFIER_RX.search(clause):
        return "verdict label in qualifier position"
    if _standalone_label_is_qualifier(line, m.start()):
        return "verdict label in its own clause (caption / obligation form)"
    if _line_has_bound_marker(clause):
        return "prohibition / falsification context"
    return ""


def _clear_fq_caliber(line: str, m) -> str:
    """A4: a line stating an f_q NUMBER must carry its caliber tag.

    The number has to be the f_q token's OWN reading -- after it ("f_q reached
    84.5") or bound to it before it ("f_q = 84.5", "f_q of 99").  A digit
    elsewhere on the line ("f_q is defined in Eq.(9)", "see Table 4") is not
    a reading, so a bare has-digit test both cleared nothing and fired on
    every formula mention.
    """
    if not _states_a_reading(line, m):
        return "no f_q reading on the line"
    if _CALIBER_TAG_RX.search(line):
        return "caliber tag present"
    if _line_has_bound_marker(line):
        return "prohibition / falsification context"
    return ""


# W9 (ticket 50): the no-judgement predicate that replaced the retired
# "degenerate by construction" premise.  Coverage is the ONLY axis now, so the
# clearance has to come from what the reading IS -- a reported reading on the
# demand curve -- not from a claim that the axis degenerates.  Bare topic words
# ("single-objective", "tie-set", "reading") are deliberately NOT clearances:
# the new text uses them everywhere, so they would saturate the whitelist
# (phase-1 review finding).  Registration anchors:
#   * analysis_prereg_v2.json tests.coverage_parity_as_result -- "Reported as a
#     construction and a count, in the results, as a result";
#   * the ticket-50 amendment (coverage-demand curve = the main result);
#   * L8 data -- every sweep unit carries a single-objective tie-set
#     (unique f1 on the front = 1), so no pass/fail verdict exists to report.
_W9_NO_JUDGEMENT_RX = re.compile(
    r"reported?\s+as\s+(?:a\s+)?(?:result|reading|count)"
    r"|not\s+(?:a|an|the)\s+(?:test|verdict|judgement|judgment|"
    r"hypothesis\s+test|pass[/\s-]?fail\s+test)"
    r"|no\s+pass[/\s-]?fail|neither\s+passed\s+nor\s+failed"
    r"|no\s+claim\s+of\s+the\s+form|make\s+no\s+claim"
    r"|no\s+power|无功效|不作检验|非检验|非判词|无判词|不计通过|非通过",
    re.IGNORECASE,
)
# W9's own boundary set (defect H6).  Deliberately NOT applied to the other
# bans: there, a bare "and" coordinates two phrases under one trailing marker
# ("'X' and 'Y' are forbidden"); here the predicate is a full declarative, so a
# conjunction means a second clause.
#
# An ANAPHORIC subject is the same signal: ", so IT IS not a test" / "because
# IT IS not a test" restate the hit, while the licensed "…, so a coverage axis
# failed reading is not a result" predicates a different noun phrase.  Keying
# on the pronoun keeps that licensed sentence (which the phase-1 suite already
# carries) while closing the round-2 bypasses.
_W9_CONJUNCTION_RX = re.compile(
    r"\b(?:and|or|which)\b|"
    r"\b(?:it|this|that|these|those|they)\s+(?:is|are|was|were|has|have)\b",
    re.IGNORECASE)


def _clear_coverage_reading(line: str, m) -> str:
    """W9: only a no-judgement PREDICATE clears a pass/fail-shaped sentence.

    The predicate is line-scoped, but a contrast or a spaced dash between it
    and the hit blocks the clearance -- otherwise "coverage is reported as a
    reading; yet coverage passed at the base budget" would launder the claim
    the ban exists to catch.

    W9 also uses a WIDER boundary set than the other bans
    (``_W9_CONJUNCTION_RX``).  Its predicate is an independent declarative, so
    there is no "'X' and 'Y' are forbidden" governing relation to protect: a
    bare "and", a bare "or" or a relative "which" between predicate and hit
    means the predicate describes something else.  Without it, "Coverage passed
    at the base budget, which is not a test" and "Coverage has no power as a
    test and coverage passed at the base budget" both cleared (defect H6).  A
    comma ALONE is not a boundary -- "Coverage has no power as a test, so a
    coverage axis failed reading is not a result" is a licensed sentence and
    must stay clear.
    """
    mk = _clause_marker(line, m.start(), PROHIBITION_MARKERS)
    if mk:
        return f"inside a prohibition ({mk!r})"
    for pm in _W9_NO_JUDGEMENT_RX.finditer(line):
        seg = (line[pm.end():m.start()] if pm.start() < m.start()
               else line[m.start():pm.start()])
        # A sentence terminator blocks as well as a contrast: "Coverage has no
        # power as a test. Coverage passed at the base budget." is two claims
        # on one line, and the first must not licence the second.
        if not (_has_clause_boundary(seg)
                or _W9_CONJUNCTION_RX.search(seg)):
            return "no-judgement predicate governs the hit"
    return ""


# W15a (ticket 50 A4): a FULFILLMENT-RATIO reading carries a three-part tag.
_FULFILLMENT_LIB_RX = re.compile(
    r"library[-\s]?caliber|库口径|zero[-\s]?squint\s+library|library\s+f_?q|"
    r"f_?q[^.\n]{0,25}library", re.IGNORECASE)
_FULFILLMENT_TIESET_RX = re.compile(
    r"tie[-\s]?set|tie\s+set|全体成员|all\s+(?:front|tie)|mean\s+over|"
    r"averaged\s+over\s+(?:the\s+)?(?:tie|front|members)", re.IGNORECASE)
# The third element is ONE obligation -- "a reported reading, not an
# optimization target" -- so it is TWO recognisers, both required.  A single OR
# let "(library caliber, tie-set mean, reported reading)" pass with the
# not-a-target half missing (defect M2 in the discrimination probe).
_FULFILLMENT_READING_RX = re.compile(
    r"reported?\s+reading|reporting\s+reading|reading,?\s+not|"
    r"reported?\s+only|报告读数|只读数|仅作读数", re.IGNORECASE)
_FULFILLMENT_NONTARGET_RX = re.compile(
    r"not\s+an?\s+(?:optimization|optimisation)\s+target|not\s+an?\s+objective|"
    r"非优化目标|不进目标|非目标", re.IGNORECASE)


def _clear_fulfillment_caliber(line: str, m) -> str:
    """A fulfillment-ratio number must carry all three caliber elements.

    Registration (ticket-50 amendment, formulas/formula-spec.md 8.17-10):
    the ratio is (i) computed on the LIBRARY f_q, (ii) averaged over ALL
    tie-set members -- not the anchor solution's reading, whose producer is
    scripts/build_sweep_results.py:75-88 -- and (iii) a REPORTED READING, not
    an optimization target.  A line that states a number and misses any one of
    the three is a violation; a mention with no number is not a reading.
    """
    if not _states_a_reading(line, m):
        return "no fulfillment reading on the line"
    mk = _clause_marker(line, m.start(), PROHIBITION_MARKERS)
    if mk:
        return f"inside a prohibition ({mk!r})"
    missing = [name for name, rx in (
        ("library caliber", _FULFILLMENT_LIB_RX),
        ("tie-set mean", _FULFILLMENT_TIESET_RX),
        ("reported reading", _FULFILLMENT_READING_RX),
        ("not an optimization target", _FULFILLMENT_NONTARGET_RX))
        if not rx.search(line)]
    if missing:
        return ""
    return "three-part caliber tag present"


def _clear_fq_deliv(line: str, m) -> str:
    """W15b: the descriptive f_Q_deliv variant must carry its label and the
    non-comparability clause (formula-spec 8.17-10: the two calibers must not
    be mixed)."""
    if not _states_a_reading(line, m):
        return "no f_Q_deliv reading on the line"
    mk = _clause_marker(line, m.start(), PROHIBITION_MARKERS)
    if mk:
        return f"inside a prohibition ({mk!r})"
    if (re.search(r"descriptive|描述性", line, re.IGNORECASE)
            and re.search(r"not\s+comparab|incomparab|不可混比|不得混比|"
                          r"不与[^.\n]{0,10}混比", line, re.IGNORECASE)):
        return "descriptive-variant label + non-comparability present"
    return ""


# A caliber marker that satisfies A4.
_CALIBER_TAG_RX = re.compile(
    r"caliber|口径|v1\b|v2\b|v3\b|M\s*族|R\s*族|真实窗|真窗|合成族|"
    r"real-?window|synthetic|normalis?z|归一化?|非归一化?|不可比|incomparable|"
    r"f_?q\s*(?:值域|范围|range)|not\s+normalised|not\s+normalized",
    re.IGNORECASE,
)

# A7: a zero-violation statement is licensed only when it says relative to the
# evaluator.  The obligation is one clause, so the clearance is checked on the
# line rather than by a separate prohibition classifier.
_A7_CALIBER_RX = re.compile(
    # A7's obligation names the EVALUATOR as the referent.  Both phrasings
    # count: "relative to the evaluator" and "with respect to the evaluation
    # model" are the same obligation said two ways, and the second one was
    # missing from the first cut.
    r"relative\s+to\s+(?:the\s+)?(?:evaluator|evaluation\s+model|evaluation|"
    r"model|evaluator\s+model|constraint\s+set|feasibility\s+judgement|"
    r"feasibility\s+judgment)\b|"
    r"with\s+respect\s+to\s+(?:the\s+)?(?:evaluator|evaluation\s+model|"
    r"evaluation|model)\b|"
    r"relative\s+to\s+the\s+evaluator\b|"
    r"相对(?:于)?\s*(?:评估器|评价器|评估模型|评估口径|模型|约束集)|"
    r"评估器(?:口径|给出|判定)|相对于评估器",
    re.IGNORECASE,
)


def _clear_a7(line: str, _m) -> str:
    if _A7_CALIBER_RX.search(line):
        return "relative-to-evaluator qualifier present"
    return ""


# A3: the v2 real-window artifacts are permanently uncitable, with ONE
# registered exception (confound_control.json, still valid, M family).  The
# ban is on CITING the R-family v2 numbers, so it fires on a v2_results
# reference that is not the confound_control exception.
def _clear_a3_v2(line: str, _m) -> str:
    if "confound_control" in line:
        return "the registered v2 exception (M family, still valid)"
    return ""


# The writing bans.  ``(label, patterns, guard)`` -- see scan_writing_bans.
WRITING_BANS = [
    # W1 / A1 + E2: plateau claims in BOTH directions.
    #
    # The verdict LABEL is itself a pattern, not just a whitelist token.  With
    # the label outside the pattern set, a caption containing ONLY the tag
    # ("richness at 160/240 (NOT-PLATEAUED)") produced no hit at all, so the
    # qualifier whitelist was never exercised on the exact shape the caption
    # obligation requires -- the deadlock this check exists to prevent, hidden
    # behind a check that appeared to pass.  Matching the label and then
    # clearing it on context is what makes the two sides testable against each
    # other.
    ("W1 A1 plateau (both directions)", [
        r"\b(?:has|have|had)\s+not\s+plateaued\b",
        r"\b(?:has|have|had)\s+plateaued\b",
        r"\bis\s+not\s+plateaued\b",
        r"\bis\s+plateaued\b",
        r"\bthe\s+front\s+(?:has|have|had)\s+(?:not\s+)?plateaued\b",
        r"NOT[\s\-_]*PLATEAUED",
        r"未平台", r"已平台", r"平台期",
        r"(?:仍|仍然)?单调上升(?:且)?未?平台",
    ], _clear_plateau_qualifier),

    # W2 / E1: the no-prior-work ban, both halves plus the English shapes.
    ("W2 E1 no-prior-work claim", [
        r"无人做", r"尚无人做", r"尚无人(?:研究|提出|报道)",
        # Ticket-50 discrimination probe, defect M5: the ordinary paraphrases.
        # "无人研究过" / "前人未研究过" are the same claim as "无人做"; the verb
        # list was the hole, not the concept.
        r"无人(?:研究|提出|报道|考察|建模|触及)过?",
        r"前人(?:未|没有|未曾?)(?:研究|提出|报道|涉及|考察)",
        r"no\s+prior\s+work\s+(?:on|for|has|does|study)",
        # Ticket 50: the clause-final form.  "…has no prior work;" ends the
        # clause, so the registered pattern above (which requires a following
        # on/for/has/does/study) never matched the manuscript's own novelty
        # sentence.  That is why retiring the spec.md:82 licence alone left
        # the sentence green: W2 was not looking at it.
        #
        # "No previous work / no prior study / no previous research" are the
        # same noun phrase (round-2 self-attack finding A19), so the family is
        # matched as a set; the bare "no prior work" literal is subsumed.
        r"\bno\s+(?:previous|prior)\s+(?:work|study|studies|research|effort)\b",
        r"\bno\s+one\s+has\s+(?:yet\s+)?(?:studied|proposed|addressed)\b",
        r"\bnobody\s+(?:has|had|have)\s+(?:yet\s+)?"
        r"(?:studied|proposed|addressed|considered|investigated|modelled|"
        r"modeled|explored)\b",
        # "the coupling HAS NEVER BEEN STUDIED" -- the passive is the form a
        # related-work sentence actually uses; the active-only first cut let
        # the single most likely English phrasing through.
        r"\b(?:has|have|had)\s+never\s+been\s+"
        r"(?:studied|addressed|explored|considered|investigated|modelled|modeled)\b",
        # The verb list, not the concept, was the hole: "the first to PLACE the
        # loop inside the scheduler" is the same claim as "the first to study".
        r"\bfirst\s+to\s+(?:study|propose|introduce|establish|show|place|put|"
        r"formulate|model|treat|combine|join|consider|explore|address|"
        r"quantify|characterise|characterize)\b",
        r"首次(?:提出|研究|报道|将)",
    ], _clear_no_prior_work),

    # W3a / E3 + spec D15 red line 1: the per-orbit capacity caliber.  The
    # registered caliber is per-PASS; naming a per-orbit capacity is the
    # banned framing regardless of any number on the line.
    ("W3a E3 per-orbit capacity caliber", [
        r"per[-\s]?orbit\s+(?:capacity|throughput|limit|upper\s+bound)",
        r"每轨[^。\n]{0,8}(?:容量|吞吐|上限|可容)",
        r"\bclosure\b[^.\n]{0,30}\bas\s+(?:a\s+)?validation\s+score\b",
    ], _clear_by_regex(r"禁|不得|forbidden|must\s+not|per[-\s]?pass",
                       r"no\s+universal|counter-?example")),

    # W3b / B15: until the v3 serial bound is recomputed, NO capacity NUMBER
    # may appear in the paper.  Deliberately broad on the word 'capacity' and
    # permissive about where the number sits relative to it -- the earlier
    # adjacent-only form let "per-pass capacity is 12" through, which is
    # still a capacity number under the not-recomputed rule.
    ("W3b E3 capacity number (not recomputed)", [
        r"\bcapacity\b[^.\n]{0,30}?\d|\bcapaci(?:ty|ties)\b\s*(?:=|:|of|is|was|＝)",
        r"容量[^。\n]{0,12}?\d",
    ], _clear_by_regex(r"v3\s+(?:未|not)\s+(?:re)?computed",
                       r"NOT\s+RECOMPUTED", r"not\s+recomputed",
                       r"禁|不得|forbidden|must\s+not|no\s+capacity\s+number")),

    # W4 / E4: the universal "a single satellite can only fit N" claim.
    ("W4 E4 single-satellite only-N", [
        r"单星[^。\n]{0,15}(?:一次|单次)[^。\n]{0,15}(?:只能|至多|最多|不超过)\s*\d+",
        # the same claim with a verb between the count and the modal
        # ("单星一次只能安排 24 个"): the first cut's window had no room for
        # the verb, which is how the sentence is normally written.
        r"单星[^。\n]{0,15}(?:一次|单次)[^。\n]{0,20}"
        r"(?:只能|至多|最多|不超过)[^。\n]{0,10}\d+",
        r"一颗星[^。\n]{0,15}(?:一次|单次)[^。\n]{0,15}(?:只能|至多|最多)\s*\d+",
        # both English orders: "a single satellite CAN ONLY accommodate 24"
        # and "one satellite MAY accommodate AT MOST 12" (subject before the
        # modal, and the modal after the verb).
        r"\b(?:a\s+)?single\s+satellite\b[^.\n]{0,60}"
        r"(?:can|may|could|will)\s+(?:only\s+|just\s+|merely\s+)?"
        r"(?:accommodate|schedule|serve|fit|handle)\s+(?:at\s+most\s+|only\s+)?\d+",
        r"\b(?:one|a)\s+satellite\b[^.\n]{0,40}"
        r"(?:accommodate|schedule|serve|fit|handle)\w*\s+"
        r"(?:at\s+most\s+|only\s+|no\s+more\s+than\s+)?\d+",
    ], _clear_by_regex(r"禁|不得|forbidden|must\s+not|no\s+universal",
                       r"反例|counter-?example", r"multi-?orbit|多圈")),

    # W5 / E5 + B4: a 45-deg READING must carry the extrapolation label.
    # Narrowed deliberately: the ban is on an unlabelled 45-deg dwell or
    # bandwidth NUMBER, not on the number 45 (the platform inclination is
    # legitimately 45 deg and appears in the fixture).
    ("W5 E5 45-deg extrapolation label", [
        r"(?:45\s*(?:°|deg|度))\s*(?:时|处|下|\band\b)?[^。.\n]{0,30}?"
        r"[-+]?\d+(?:\.\d+)?\s*(?:s\b|秒|ms\b|Hz|kHz|MHz|dB)",
        r"[-+]?\d+(?:\.\d+)?\s*(?:s\b|秒|ms\b|Hz|kHz|MHz|dB)[^。.\n]{0,30}?"
        r"(?:at\s+)?45\s*(?:°|deg|度)",
    ], _clear_by_regex(r"extrapolat|外推", r"禁|不得|forbidden",
                       r"physical\s+bound|物理边界")),

    # W6 / E6: the density axis belongs to the thesis, not this paper.
    ("W6 E6 density axis ownership", [
        # The subject-then-owner order ("the density axis is the core
        # contribution of this paper") puts more than 25 characters between
        # the axis and the ownership phrase; the first cut's 25-char window
        # missed it. 60 chars covers a full clause without crossing sentences.
        r"(?:本篇|本文|这项|本研究|this\s+(?:paper|work|study|article))"
        r"[^。.\n]{0,60}(?:密度轴|density\s+axis)",
        r"(?:密度轴|density\s+axis)[^。.\n]{0,60}"
        r"(?:本篇|本文|这项|本研究|this\s+(?:paper|work|study|article))",
        # ownership verbs: "this paper studies the density axis"
        r"(?:本篇|本文|this\s+(?:paper|work|study))\s+"
        r"(?:研究|study|studies|examines|addresses|covers)[^。.\n]{0,25}"
        r"(?:密度轴|density\s+axis)",
    ], _clear_by_regex(r"禁|不得|归(?:属)?(?:大论文|thesis)|belongs?\s+to|"
                       r"out\s+of\s+scope|future\s+work|not\s+this\s+paper")),

    # W7 / E7 + F-5: rho_a,ach routing, scan-span/rate "in the loop", and the
    # shrinking-feasible-set claim.  All three have zero production consumers.
    ("W7 E7 routing / scan-constraint claims", [
        r"(?:scan[_\s-]?span|scan[_\s-]?rate|扫描跨度|扫描率)[^。.\n]{0,25}"
        r"(?:in\s+the\s+loop|enforced|active|在环|参与评估|生效)",
        # \s* between the parts: _strip_markup expands \rho_{a,\mathrm{ach}}
        # to "rho a, ach", so a pattern written as the plain text form
        # ``rho_a,ach`` matches markdown and silently misses every .tex draft.
        r"(?:rout(?:e|ed|ing)|路由)[^。.\n]{0,25}"
        r"\brho\s*[_{]?\s*a[^。.\n]{0,12}ach",
        r"\brho\s*[_{]?\s*a[^。.\n]{0,12}ach[^。.\n]{0,25}"
        r"(?:rout(?:e|ed|ing)|路由)",
        r"(?:细需求|high-?demand)[^。.\n]{0,20}(?:可行域|可行集)[^。.\n]{0,20}"
        r"(?:斜视|squint)[^。.\n]{0,10}收缩",
        r"(?:feasible\s+(?:set|region|domain))[^.\n]{0,45}squint",
    ], _clear_by_regex(r"禁|不得|forbidden|must\s+not|zero\s+production|"
                       r"no\s+consumer|not\s+used|is\s+commented", r"B_D")),

    # W8 / E8: delta was registered AFTER calibration, so "pre-registered
    # effect size" is false whatever the surrounding sentence says.
    ("W8 E8 pre-registered effect size", [
        r"pre-?registered\s+effect\s+size", r"预注册效应量", r"预注册效果量",
    ], _clear_by_regex(r"禁|不得|must\s+not|not\s+pre-?registered|"
                       r"registered\s+after\s+calibration|"
                       r"标定后注册|作废|forbidden", r"ALIVE|DEAD|structur")),

    # W9 / E9 + A6.  Ticket 50 rewrote the LICENSE, not the ban: coverage is
    # the single axis now, so "degenerate by construction" is semantically
    # reversed and no longer clears anything.  What clears is the paired
    # no-judgement predicate (reported as a reading / not a test) -- see
    # _clear_coverage_reading.
    ("W9 E9 coverage pass/fail", [
        r"coverage[^.\n]{0,30}\b(?:passed|failed|did\s+not\s+pass|passes|fails)\b",
        r"覆盖(?:轴)?[^。.\n]{0,12}(?:通过|未通过|不通过)",
    ], _clear_coverage_reading),

    # W10 / E10 + B9: the optimizer consumes duration_scene_s, so the
    # point-target-caliber sentence is stale (formula-spec 8.13-1).
    ("W10 E10 point-target caliber", [
        r"优化器[^。\n]{0,15}点目标",
        r"(?:optimizer|optimiser)[^.\n]{0,45}point[-\s]?target",
    ], _clear_by_regex(r"禁|不得|作废|forbidden|superseded|stale|"
                       r"duration_scene_s|场景级", r"点目标\s*vs|vs\.?|对照")),

    # W11 / A7: a zero-violation statement is relative to the evaluator.
    ("W11 A7 zero-violation caliber", [
        r"(?:zero|0)\s+violations?\b", r"零违规", r"无违规",
    ], _clear_a7),

    # W12 / A3: the v2 real-window artifacts are permanently uncitable.
    ("W12 A3 v2 real-window citation", [
        # ``v2\_results``: the .tex port escapes the underscore, so a pattern
        # that does not tolerate a backslash silently skips every LaTeX
        # manuscript -- the same class of false negative as the rho symbol.
        r"v2\s*[\\]?_\s*results", r"v2\s+results", r"v2结果",
    ], _clear_a3_v2),

    # W13 / A4: an f_q number must carry its caliber tag.
    ("W13 A4 f_q caliber tag", [
        r"\bf_?[qQ]\b", r"\bf\s*[_\\{]?\s*[qQ]\b",
    ], _clear_fq_caliber),

    # W14 (ticket 50 A1): the single-axis positioning.  The paper's
    # contribution is no longer "a per-mode SAR metric as an independent
    # objective dimension"; the only objective is coverage and the order
    # resolution is a per-task hard constraint.  Every shape below has to go
    # red in the CURRENT text, which is the expected phase-1 state; the
    # rewrite list is .scratch/sliding-spotlight-scheduling/t50/
    # ban-ledger-phase1.md.
    #
    # The title / keyword line is included on purpose: "…and an Image-Quality
    # Objective" is the same retired framing in the place a reader sees first
    # (phase-1 review finding).  "two-objective" is the singular form the old
    # licence text used; "biobjective"/"bi objective" are the spellings the
    # bibliography-style prose produces.
    ("W14 single-axis positioning", [
        r"\bsecond[-\s]?objectives?\b",
        r"\bsecond,\s+(?:independent\s+)?objectives?\b",
        r"\b2nd[-\s]?objective\b",
        r"\bsecondary\s+objectives?\b",
        r"\bbi[-\s]?objectives?\b",
        r"\bdual[-\s]?objectives?\b",
        r"\btwo[-\s]?objectives?\b",
        r"\b(?:independent\s+)?objective\s+dimensions?\b",
        r"\bimage[-\s]?quality\s+objectives?\b",
        # the same claim without the word "second": "quality is an objective".
        # The copula is a SET, not just "is": "Quality remains an objective of
        # the schedule, though not the second" asserted the framing while
        # slipping past the "is"-only pattern (defect H3).
        r"\bquality\s+(?:is|are|was|were|remains?|stays?|becomes?|counts?\s+as|"
        r"continues?\s+to\s+be)\s+(?:still\s+)?(?:an?|the|one\s+of\s+the)\s+"
        r"(?:independent\s+|second\s+|primary\s+|key\s+)?objectives?\b",
        r"\bquality\b[^.\n]{0,20}\bas\s+an?\s+(?:independent\s+)?objective\b",
        # Ticket-50 discrimination probe, defect H1: the retired framing said
        # without the word "objective".  Every pattern below was verified to
        # MISS in the current manuscript, and the ones that must keep missing
        # are the promotion verdict's "two separated axes" (structural /
        # reading) and the R1C "quality axis" (a scale, not an objective) --
        # both stay clear because the pattern demands an objective-family word
        # in the same clause.
        #
        # Round-2 audit widened three of them: the singular "two-axis"
        # formulation, the hyphenated "objective-vector", and a coordination
        # verb ("optimi[sz]") after the axes, which is how the paper's own
        # sentence is written.  A bare "criteri" after the axes was REMOVED: it
        # is promotion prose ("two separated axes … separate criteria").
        r"\b(?:two|both)[-\s]+(?:\w+[-\s]+){0,2}ax(?:is|es)\b[^.\n:]{0,40}?"
        r"(?:objectiv|maximi[sz]|minimi[sz]|optimi[sz]|trade[-\s]?off)",
        r"(?:optimi[sz]|maximi[sz]|minimi[sz])\w*[^.\n:]{0,40}?"
        r"\b(?:two|both)[-\s]+(?:\w+[-\s]+){0,2}ax(?:is|es)\b",
        r"\bobjective[-\s]+(?:vector|space)\b",
        r"\b(?:both|the\s+two)\s+objectives?\b",
        r"\b(?:secondary|second)\s+criteri(?:on|a)\b",
        r"\b(?:two|bi)[-\s]?criteri(?:on|a)\b",
        r"\bsecond\s+(?:\w+\s+){0,2}?axis\b",
        # Defect H2 -- the CURRENT manuscript's own leak: the conclusion asserts
        # "the quality index of the served set is a first-class objective" and
        # "the task priorities that drive the first objective", neither of which
        # any pattern above matched, so sec8_conclusion.md was entirely absent
        # from the expected-red ledger.  "first-class constraint" (a legitimate
        # phrase used four times) is not matched: the noun must be "objective".
        r"\bfirst[-\s]class\s+objectives?\b",
        r"\bfirst\s+objective\b",
        r"\bquality\s+index\b[^.\n]{0,40}\bis\s+an?\s+[^.\n]{0,18}objective\b",
        r"第二目标", r"第\s*[二2]\s*个?\s*目标", r"双目标",
        r"两(?:个|项|条)?目标", r"质量(?:作为|当作|视作)(?:一[个条])?目标",
        r"独立目标维", r"第二优化目标", r"次要目标",
    ], _clear_dual_objective),

    # W15a (ticket 50 A4): a fulfillment-ratio number must carry its
    # three-part caliber tag -- library f_q, tie-set mean, reported reading
    # (not an optimization target).  Kept as its own label rather than folded
    # into W13 because W13 is anchored on the f_q TOKEN: one merged guard would
    # have to dispatch on the matched text, and the ledger's per-line label
    # would stop naming which obligation failed.
    ("W15a A4 fulfillment-ratio caliber", [
        # ``fulfillment\_ratio`` in .tex keeps its underscore through
        # _strip_markup, so the character class has to admit "_" (defect H8).
        r"fulfill?ment[_\- \t]?ratio", r"兑现率", r"\bf_q_fulfillment\b",
    ], _clear_fulfillment_caliber),

    # W15b (ticket 50 A4): the descriptive variant f_Q_deliv, once implemented
    # (formula-spec 8.17-10), must be labelled descriptive and declared
    # incomparable with the library caliber.  Two patterns because _strip_markup
    # turns the .tex form into "f_ Q, deliv" (the subscript underscore survives
    # and \text / \mathrm leave their CONTENT behind).  The first cut required
    # ``f Q, text deliv`` -- a string _strip_markup never produces -- so W15b
    # never fired on a .tex manuscript at all (defect H7).
    ("W15b A4 f_Q_deliv descriptive tag", [
        r"f[_ ]?q[_ ]?deliv\b",
        r"\bf[_ ]*q\s*,\s*(?:(?:text|mathrm|mathit|textrm)\s+)?deliv\b",
    ], _clear_fq_deliv),
]


# The bans whose phrases are multi-word and can therefore be split by a hard
# line wrap.  See the wrap-junction pass in scan_writing_bans.
_WRAP_SCAN_LABELS = frozenset({
    "W14 single-axis positioning",
    "W15a A4 fulfillment-ratio caliber",
    "W15b A4 f_Q_deliv descriptive tag",
})

# Guards that need the SURROUNDING lines to classify the hit.
#   * A retrospective marker ("We no longer treat image quality as a") sits on
#     the line above the banned phrase it governs, and a withdrawal verb ("was"
#     / "withdrawn.") on the line below it: a line-scoped guard saw only half
#     the sentence and fired on a licensed mention (defect M1 / false positive
#     F2).  The guard's own clause cut is what keeps this honest -- a marker in
#     the NEXT sentence is outside the hit's clause and still does not clear.
#   * The caliber obligations (W15) start when EITHER the label or its number
#     appears, so a label on line 1 and the number on line 2 ("The fulfillment
#     ratio" / "is 0.62") must still be judged (defect M4).
# Scoped to these labels on purpose: W13's caliber tag is per-line by design,
# and widening its window would let a tag on one line license a number on the
# next.
_CONTEXT_LABELS = frozenset({
    "W14 single-axis positioning",
    "W15a A4 fulfillment-ratio caliber",
    "W15b A4 f_Q_deliv descriptive tag",
})


def scan_writing_bans(paths, violations, cleared):
    """Run the checklist E-section / A1-A7 bans over manuscript-shaped files.

    Each entry is ``(label, patterns, guard)``.  ``guard`` is a callable
    ``(line, match) -> str | None``: it returns a clearance reason for a
    licensed shape, or None to let the hit stand as a violation.  Keeping the
    whitelist beside the pattern is what makes the A1 deadlock fixable -- the
    licensed qualifier form and the banned standalone assertion are the SAME
    STRING, so no amount of pattern narrowing separates them; only context
    does.  The guards reuse the existing prohibition / falsification
    classifiers rather than adding a third notion of context.
    """
    compiled = [(lbl, re.compile("|".join(pats), re.IGNORECASE), guard)
                for lbl, pats, guard in WRITING_BANS]
    for p in paths:
        if not _is_manuscript_shaped(p):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue
        stripped = "\n".join(
            _strip_markup(ln) for ln in _drop_fences(text).splitlines())
        lines = stripped.splitlines()
        fired: set[tuple[str, int]] = set()
        for label, rx, guard in compiled:
            for m in rx.finditer(stripped):
                line_no = _line_index(stripped, m.start())
                line = lines[line_no - 1]
                abs_start = _line_start(stripped, m.start())
                context, offset = line, abs_start
                if label in _CONTEXT_LABELS:
                    lead = lines[line_no - 2] if line_no >= 2 else ""
                    tail = lines[line_no] if line_no < len(lines) else ""
                    if lead.strip():
                        context = lead + " " + context
                        offset -= len(lead) + 1
                    if tail.strip():
                        context = context + " " + tail
                rel = _RelMatch(m, offset)
                reason = guard(context, rel)
                if reason:
                    cleared.append((label, p, line_no, m.group(0), reason))
                else:
                    violations.append(
                        f"{label}: {_rel(p)}:{line_no} -> {m.group(0)!r}"
                    )
                    fired.add((label, line_no))
        # Hard-wrapped prose: a banned phrase split across a newline
        # ("second\nobjective" in cover_letter.md:15) is invisible to a
        # per-line scan.  Joining each adjacent pair restores it; only matches
        # that CROSS the junction are reported, so nothing is double-counted.
        # Scoped to the ban labels whose phrases are multi-word.
        #
        # The pairs are taken over NON-BLANK lines: a blank line is a paragraph
        # break a hostile draft can hide a split behind ("second" / blank /
        # "objective"), and the earlier version skipped those pairs outright
        # (defect H8 / case F4).
        live = [i for i, ln in enumerate(lines) if ln.strip()]
        for a, b in zip(live, live[1:]):
            left, right = lines[a], lines[b]
            joined = left + " " + right
            for label, rx, guard in compiled:
                if label not in _WRAP_SCAN_LABELS:
                    continue
                for m in rx.finditer(joined):
                    if m.end() <= len(left) or m.start() >= len(left):
                        continue          # does not cross the junction
                    line_no = a + 1
                    if (label, line_no) in fired:
                        continue
                    reason = guard(joined, m)
                    if reason:
                        cleared.append((label, p, line_no, m.group(0), reason))
                    else:
                        violations.append(
                            f"{label}: {_rel(p)}:{line_no} -> {m.group(0)!r}")
                        fired.add((label, line_no))


def main(argv=None) -> int:
    global _INCLUDE_SCRATCH
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", action="append", default=None,
                    help="extra roots to scan")
    ap.add_argument("--include-scratch", action="store_true",
                    help="also scan the planning scratch directory; OFF by "
                         "default because the red lines govern the PAPER and "
                         "the REGISTERED ARTIFACTS, while the scratch is where "
                         "the bans themselves are discussed -- scanning it "
                         "yields a hit on every document that quotes the "
                         "forbidden phrase in order to forbid it.  It now also "
                         "extends the W-family (writing-ban) scope, which it "
                         "did not before: see _INCLUDE_SCRATCH")
    ap.add_argument("--must-include", action="append", default=None,
                    metavar="PATH",
                    help="fail unless PATH is in the scanned set (repeatable). "
                         "The gate used to print only a file COUNT, so a "
                         "manuscript left in the wrong directory produced "
                         "'0 violations over 194 files' -- a clean pass over "
                         "the registration layer with the draft never read. "
                         "A named manuscript that was not scanned is a "
                         "failure, not a pass (ticket 37 block C).")
    args = ap.parse_args(argv)

    default_roots = [REPO / "papers" / "sliding-spotlight-scheduling"]
    if args.include_scratch:
        _INCLUDE_SCRATCH = True
        default_roots.append(REPO / ".scratch" / "sliding-spotlight-scheduling")
    roots = [Path(a) for a in args.path] if args.path else default_roots
    files: list[Path] = []
    for root in roots:
        root = Path(root).resolve()
        # A path that does not exist scanned ZERO files and printed a clean
        # rc=0: a green gate over nothing (probe defect M6).  It is a usage
        # error, like a mis-typed --must-include.
        if not root.exists():
            print(f"SCAN SET: --path {str(root)!r} does not exist", file=sys.stderr)
            return 2
        if root.is_file():
            # A .txt/extensionless draft scanned ZERO writing-ban hits (the W
            # family only reads .md/.tex), so a mis-suffixed manuscript would
            # pass silently.  Naming one explicitly is a usage error.
            if root.suffix not in (".py", ".md", ".json", ".tex"):
                print(f"SCAN SET: --path {str(root)!r} has an unsupported "
                      f"suffix {root.suffix!r}", file=sys.stderr)
                return 2
            files.append(root)
        elif root.is_dir():
            files.extend(
                p for p in root.rglob("*")
                if p.is_file()
                and p.suffix in (".py", ".md", ".json", ".tex")
                and "results" not in p.parts
                # Build caches are not manuscript prose; .pytest_cache/README.md
                # was in the 1075-file scan set (probe defect L4).
                and not any(part in _SKIP_DIR_NAMES for part in p.parts)
                and p.resolve() != Path(__file__).resolve()  # the checker
                # necessarily contains the forbidden patterns themselves
                and p.name not in _SELF_SCAN_EXEMPT
            )

    violations: list[str] = []
    cleared: list[tuple] = []

    # An EMPTY scan set is the same false green as a nonexistent path: the gate
    # would print "0 violations over 0 files" and exit clean (round-2 audit).
    if not files:
        print("SCAN SET: nothing to scan -- the path(s) yielded no file", file=sys.stderr)
        return 2

    # Block C: name the files, not just their number, and refuse to pass when
    # a manuscript the caller named was not actually scanned.
    scanned_keys = {p.resolve() for p in files}
    for want in (args.must_include or []):
        wp = Path(want).resolve()
        if not wp.is_file():
            violations.append(
                f"SCAN SET: --must-include {want!r} does not exist")
        elif wp not in scanned_keys:
            violations.append(
                f"SCAN SET: --must-include {want!r} was NOT scanned "
                f"(the gate would have passed without reading it)")

    print(f"=== scan set: {len(files)} file(s) ===")
    for p in files:
        print(f"SCAN     {_rel(p)}")

    print("=== R4: phase-transition / percolation claims ===")
    scan_texts(files, PHASE_PATTERNS, "R4 phase-transition", violations, cleared)

    print("=== R2: front-collapse claims ===")
    scan_texts(files, COLLAPSE_PATTERNS, "R2 front-collapse", violations, cleared)

    print("=== R1: per-pass caliber ===")
    # A registered artifact must carry its caliber; the v1 families predate
    # the Eq.(22) switch and are caliber v1 by construction.
    reg = REPO / "papers" / "sliding-spotlight-scheduling" / "experiments"
    prereg_v2 = reg / "analysis_prereg_v2.json"
    if prereg_v2.is_file():
        blob = prereg_v2.read_text(encoding="utf-8")
        if "caliber" not in blob:
            violations.append(
                "R1: analysis_prereg_v2.json does not register a caliber tag"
            )
    else:
        violations.append("R1: analysis_prereg_v2.json missing")

    print("=== R3: 45-degree extrapolation labelling ===")
    # read the registered envelope from source rather than importing it: the
    # module uses relative imports and cannot be loaded standalone
    dur_src = (REPO / "papers" / "sliding-spotlight-scheduling" / "sss_core"
               / "duration.py")
    try:
        text = dur_src.read_text(encoding="utf-8")
        if "SQUINT_ENVELOPE_DEG" not in text:
            violations.append(
                "R3: sss_core/duration.py no longer registers the 45-degree "
                "envelope"
            )
        # the formula spec must disclose the extrapolation scope
        fs = (REPO / "papers" / "sliding-spotlight-scheduling" / "formulas"
              / "formula-spec.md")
        fs_text = fs.read_text(encoding="utf-8", errors="ignore").lower()
        # the disclosure may be in either language; the spec is bilingual
        disclosed = "extrapolat" in fs_text or "外推" in fs_text
        if not fs.is_file() or not disclosed:
            violations.append(
                "R3: formula-spec.md does not disclose the 45-deg extrapolation"
            )
    except (OSError, UnicodeDecodeError) as exc:
        violations.append(f"R3: could not read the envelope registration ({exc})")

    print("=== R5: real-window positioning ===")
    if prereg_v2.is_file():
        freeze = json.loads(prereg_v2.read_text(encoding="utf-8"))
        fam = freeze["matrix_scope"]["family"]
        if "R<density>" not in fam and "real-window" not in fam.lower():
            violations.append(
                "R5: the freeze does not position the main experiment on the "
                "real-window family"
            )
    else:
        violations.append("R5: analysis_prereg_v2.json missing")

    print("=== W1-W15: writing-obligation bans (manuscript-shaped files) ===")
    scan_writing_bans(files, violations, cleared)

    if cleared:
        print(f"\n=== cleared: {len(cleared)} hit(s) suppressed by "
              "prohibition/falsification context (audit trail) ===")
        for label, p, line, token, reason in cleared:
            print(f"CLEARED    {label}: {_rel(p)}:{line} "
                  f"-> {token!r} ({reason})")
    print(f"\n=== RESULT: {len(violations)} violation(s) over "
          f"{len(files)} file(s) scanned ===")
    for v in violations:
        print(f"VIOLATION   {v}")
    if violations:
        print("VERDICT: a prereg red line is violated")
        return 1
    print("VERDICT: no prereg red line violated")
    return 0


if __name__ == "__main__":
    sys.exit(main())