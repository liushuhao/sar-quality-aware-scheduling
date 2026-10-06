#!/usr/bin/env python3
"""The five prereg red lines as machine checks (ticket 17).

The freeze registers them in prose; a prose red line is not a check.  This
script makes each one executable against the repository's own text and code,
so a forbidden claim is caught by the gate rather than by a reader.

The five (spec D15 recut, ticket 17):
  R1  per-pass caliber          -- no per-pass caliber leak in registered artifacts
  R2  forbidden sentences       -- no collapse / phase-transition declarations
  R3  45-degree extrapolation   -- readings beyond the platform envelope are labelled
  R4  no phase-transition claim -- the specific forbidden claim, checked separately
  R5  real-window positioning  -- the main experiment names the real-window family

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/check_red_lines.py [--path ...]

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
)


def _is_reporting_falsification(text: str, pos: int) -> bool:
    """True when the line REPORTS the claim as falsified rather than making it.

    A keyword scan cannot distinguish "the front collapsed" from "the
    collapse verdict was judged a search-budget artifact and the narrative
    withdrawn".  Measured, several hits in this repository are the second
    kind.  Those are classified as non-violations and PRINTED, so a reader can
    audit each judgement -- tuning the context window until the list is empty
    is how a red-line check becomes a check that never fires.
    """
    line_start = text.rfind(chr(10), 0, pos) + 1
    line_end = text.find(chr(10), pos)
    line = text[line_start:line_end if line_end != -1 else len(text)]
    return any(m in line for m in FALSIFIED_MARKERS)


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
                f"{label}: {p.relative_to(REPO).as_posix()}:{line} "
                f"-> {m.group(0)!r}"
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
            )

    violations: list[str] = []
    cleared: list[tuple] = []

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

    if cleared:
        print(f"\n=== cleared: {len(cleared)} hit(s) suppressed by "
              "prohibition/falsification context (audit trail) ===")
        for label, p, line, token, reason in cleared:
            print(f"CLEARED    {label}: "
                  f"{p.relative_to(REPO).as_posix()}:{line} "
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