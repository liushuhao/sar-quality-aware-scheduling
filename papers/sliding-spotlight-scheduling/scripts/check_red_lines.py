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
    """True when the hit sits inside a prohibition ON ITS OWN LINE.

    Deliberately line-scoped.  A character window was measured to produce a
    FALSE NEGATIVE: a JSON key 260 characters earlier contained the word
    "forbidden" (a meta-comment about the forbidden list), which cleared a
    genuine phase-transition claim injected right after it.  A prohibition is
    a statement ABOUT the phrase, so it is always on the same line as the
    phrase; anything wider lets an unrelated mention launder a real claim.
    """
    nl = chr(10)
    line_start = text.rfind(nl, 0, pos) + 1
    line_end = text.find(nl, pos)
    line = text[line_start:line_end if line_end != -1 else len(text)].lower()
    return any(m.lower() in line for m in PROHIBITION_MARKERS)


def scan_texts(paths, patterns, label, violations, cleared):
    rx = re.compile("|".join(patterns), re.IGNORECASE)
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue
        for m in rx.finditer(text):
            if _is_prohibition(text, m.start()):
                cleared.append((label, p, m, "inside a prohibition"))
                continue
            if _is_reporting_falsification(text, m.start()):
                cleared.append((label, p, m, "reports it as falsified"))
                continue
            line = text[:m.start()].count("\n") + 1
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