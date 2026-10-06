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

# The one licensed sentence shape for the no-prior-work ban, quoted from
# spec.md:82.  Both halves in one clause, no comma splitting them: the claim
# is about the CONJUNCTION being undone, not about either half alone.
_NOPRIOR_LEGAL_RX = re.compile(
    r"二者同时做无人做"
    r"|(?:coupling\s+loop\s+as\s+a\s+first-?class\s+constraint[^.]{0,120}and[^.]{0,120}"
    r"per-?mode\s+SAR\s+metric[^.]{0,120}(?:simultaneously|together|both)"
    r"[^.]{0,60}(?:has\s+never|remains\s+undone|no\s+prior\s+work))",
    re.IGNORECASE,
)

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
    if rel.as_posix().startswith(".scratch/"):
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

    Three traps, all measured on fixtures rather than assumed:

    * A code fence is not prose -- see ``_drop_fences``, which handles the
      payload, not just the delimiter.
    * ``$f_Q$`` and ``\\rho_{a,\\mathrm{ach}}`` put the SYMBOL inside the math
      delimiters and braces, so deleting math bodies silently disarmed every
      ban in a .tex manuscript (the ticket's W5.5 step runs this gate against
      the elsarticle port).  A command name is therefore kept as a bare word
      (``\\emph{X}`` -> ``emph X``, ``\\rho`` -> ``rho``) and the grouping
      characters are deleted, so ``\\rho_{a,\\mathrm{ach}}`` collapses to
      ``rhoa,ach`` -- one token a regex can match, instead of a symbol that
      vanishes and disarms W7.
    * ``\\label{}`` / ``\\ref{}`` must not manufacture prose.  They leave
      ``label``/``ref`` plus the key text, neither of which is a banned token.
    """
    line = line.strip()
    if line.startswith(("```", "~~~")):
        return ""
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


def _clear_noprior(line: str, m) -> str:
    """The ONE licensed no-prior sentence (spec.md:82)."""
    return ("the single licensed conjunction claim (spec.md:82)"
            if _NOPRIOR_LEGAL_RX.search(line) else "")


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
    tail = line[m.end(): m.end() + 60]
    xref = _XREF_RX.search(tail)
    if xref:
        tail = tail[:xref.start()]
    lead = line[max(0, m.start() - 60): m.start()]
    lead = lead[:_XREF_RX.search(lead).start()] if _XREF_RX.search(lead) else lead
    reads = bool(re.search(r"[-+]?\d+(?:\.\d+)?", tail)) or bool(
        re.search(r"(?:of|=|＝|为|达|reaches?|is)\s*$", lead.rstrip())
        and re.search(r"[-+]?\d+(?:\.\d+)?\s*$", lead))
    if not reads:
        return "no f_q reading on the line"
    if _CALIBER_TAG_RX.search(line):
        return "caliber tag present"
    if _line_has_bound_marker(line):
        return "prohibition / falsification context"
    return ""


# A caliber marker that satisfies A4.  Deliberately broad on the tag NAMES and
# narrow on the requirement: the tag may be written many ways, but SOME
# qualifier must be present on the line that states the number.
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
        r"no\s+prior\s+work\s+(?:on|for|has|does|study)",
        r"\bno\s+one\s+has\s+(?:yet\s+)?(?:studied|proposed|addressed)\b",
        # "the coupling HAS NEVER BEEN STUDIED" -- the passive is the form a
        # related-work sentence actually uses; the active-only first cut let
        # the single most likely English phrasing through.
        r"\b(?:has|have|had)\s+never\s+been\s+"
        r"(?:studied|addressed|explored|considered|investigated|modelled|modeled)\b",
        r"\bfirst\s+to\s+(?:study|propose|introduce|establish|show)\b",
        r"首次(?:提出|研究|报道|将)",
    ], _clear_noprior),

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

    # W9 / E9 + A6: coverage is degenerate BY CONSTRUCTION, so "coverage
    # passed / did not pass" is not a test result in either direction.
    ("W9 E9 coverage pass/fail", [
        r"coverage[^.\n]{0,30}\b(?:passed|failed|did\s+not\s+pass|passes|fails)\b",
        r"覆盖(?:轴)?[^。.\n]{0,12}(?:通过|未通过|不通过)",
    ], _clear_by_regex(r"degenerate\s+by\s+construction|构造性打平|构造产物|"
                       r"禁|不得|forbidden|no\s+power|无功效|not\s+a\s+test")),

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
]


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
        for label, rx, guard in compiled:
            for m in rx.finditer(stripped):
                line_no = _line_index(stripped, m.start())
                line = stripped.splitlines()[line_no - 1]
                reason = guard(line, m)
                if reason:
                    cleared.append((label, p, line_no, m.group(0), reason))
                else:
                    violations.append(
                        f"{label}: {_rel(p)}:{line_no} -> {m.group(0)!r}"
                    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", action="append", default=None,
                    help="extra roots to scan")
    ap.add_argument("--include-scratch", action="store_true",
                    help="also scan the planning scratch directory; OFF by "
                         "default because the red lines govern the PAPER and "
                         "the REGISTERED ARTIFACTS, while the scratch is where "
                         "the bans themselves are discussed -- scanning it "
                         "yields a hit on every document that quotes the "
                         "forbidden phrase in order to forbid it")
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
        default_roots.append(REPO / ".scratch" / "sliding-spotlight-scheduling")
    roots = [Path(a) for a in args.path] if args.path else default_roots
    files: list[Path] = []
    for root in roots:
        root = Path(root).resolve()
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            files.extend(
                p for p in root.rglob("*")
                if p.is_file()
                and p.suffix in (".py", ".md", ".json", ".tex")
                and "results" not in p.parts
                and p.resolve() != Path(__file__).resolve()  # the checker
                # necessarily contains the forbidden patterns themselves
                and p.name not in _SELF_SCAN_EXEMPT
            )

    violations: list[str] = []
    cleared: list[tuple] = []

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

    print("=== W1-W13: writing-obligation bans (manuscript-shaped files) ===")
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