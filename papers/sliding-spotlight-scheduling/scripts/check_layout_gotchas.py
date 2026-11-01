#!/usr/bin/env python3
"""Layout-integrity gate for the paper2 manuscript (lessons-20261016 wave).

Catches the four classes the 2026-10-16 paper1-lessons retrospective found
slipping past the existing final gate:

  1. Overfull \\hbox above a threshold (a 200.98pt overflow shipped to page
     11 of main.pdf while the gate only counted `^!` errors and pages).
  2. Orphan floats: a \\label{fig:...} / \\label{tab:...} with no matching
     \\ref{...} anywhere (the fq-domains table shipped with zero refs).
  3. Figure citation order: the first \\ref to each figure must appear in
     the same order as the figure environments in the source (Fig.~7 was
     cited before Figs. 4-6).
  4. Advisory: all-caps internal-code-looking tokens (e.g. ``H/W'') that the
     ARS acronym checker does not tokenise.  Advisory only -- human judges.

Exit codes: 0 = no FAIL (advisories allowed); 1 = at least one FAIL; 2 = usage.
Verification discipline: the parser carries a --selftest with the three known
defects above embedded as fixtures; a checker that cannot re-detect them has
no discrimination and must not be trusted (cf. verifier-blindspot lessons).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

OVERFULL_FAIL_PT = 50.0   # 200pt shipped once; anything over 50pt is visible
OVERFULL_WARN_PT = 20.0

# Caps tokens that are legitimate (expanded at first use, or standard names).
CAPS_WHITELIST = {
    "SAR", "PRF", "MDE", "AASR", "SLS", "SPT", "STR", "SAT", "UTC", "CV",
    "DC", "TOPS", "CRediT", "GF", "NSGA", "R1C", "R2F", "R3H", "R4H",
    "P8WH", "ALIVE", "DEAD", "NOT-PLATEAUED", "SEARCH-ARTIFACT", "C1", "C2",
    "C3", "C4", "M1", "M2", "M3", "M4", "AND", "OR", "PDF", "ID", "DOI",
    "NESZ", "NOT", "PLATEAUED", "SEARCH", "ARTIFACT", "STRUCTURAL", "T1",
    "ECEF",
}
CAPS_TOKEN = re.compile(r"\b(?:[A-Z][A-Z0-9]{1,9}|[A-Z]/[A-Z])\b")


def parse_overfull(log_text: str) -> list[tuple[float, str]]:
    """[(points, source_lines)] for every Overfull \\hbox in the log."""
    out = []
    for m in re.finditer(
        r"Overfull \\hbox \(([\d.]+)pt too wide\) in paragraph at lines ([^\n]*)",
        log_text,
    ):
        out.append((float(m.group(1)), m.group(2).strip()))
    return out


def float_labels(tex: str) -> list[tuple[str, str]]:
    """[(kind, label)] for figure/table environments, in source order."""
    out = []
    for m in re.finditer(r"\\begin\{(figure|table)\*?\}.*?\\label\{((?:fig|tab):[^}]+)\}", tex, re.S):
        out.append((m.group(1), m.group(2)))
    return out


def first_refs(tex: str) -> dict[str, int]:
    """label -> position of its first \\ref{...} occurrence."""
    pos = {}
    for m in re.finditer(r"\\ref\{([^}]+)\}", tex):
        pos.setdefault(m.group(1), m.start())
    return pos


def check(tex_path: Path, log_path: Path) -> tuple[list[str], list[str], list[str]]:
    """Return (fails, warns, advisories) -- fails are the gate blockers."""
    fails, warns, advisories = [], [], []
    tex = tex_path.read_text(encoding="utf-8", errors="replace")

    # 1. overfull threshold
    if log_path.is_file():
        for pts, lines in parse_overfull(log_path.read_text(encoding="utf-8", errors="replace")):
            if pts > OVERFULL_FAIL_PT:
                fails.append(f"overfull {pts:.1f}pt > {OVERFULL_FAIL_PT:.0f}pt at lines {lines}")
            elif pts > OVERFULL_WARN_PT:
                warns.append(f"overfull {pts:.1f}pt (>{OVERFULL_WARN_PT:.0f}pt) at lines {lines}")

    # 2. orphan floats
    for kind, label in float_labels(tex):
        if label not in first_refs(tex):
            fails.append(f"orphan {kind}: {label} has no \\ref anywhere")

    # 3. citation order: first-ref position must increase with float order
    labels = [lab for _, lab in float_labels(tex)]
    refs = first_refs(tex)
    prev = -1
    for lab in labels:
        if lab in refs:
            if refs[lab] < prev:
                fails.append(
                    f"citation order: {lab} cited before an earlier float "
                    f"(first refs not monotone in float order)"
                )
            prev = max(prev, refs[lab])

    # 4. advisory caps tokens outside whitelisted/expanded usage
    # An escaped percent (\% , a literal sign in the manuscript) is NOT a
    # comment opener; stripping from it silently swallows the rest of the
    # line and any caps token printed after it (R87, 2026-11-01).
    body = re.sub(r"(?<!\\)%.*", "", tex)
    seen: dict[str, int] = {}
    for m in CAPS_TOKEN.finditer(body):
        tok = m.group(0)
        if tok in CAPS_WHITELIST:
            continue
        seen.setdefault(tok, body.count("\n", 0, m.start()) + 1)
    for tok, line in sorted(seen.items()):
        advisories.append(f"caps token '{tok}' at main.tex:{line} not whitelisted/expanded")

    return fails, warns, advisories


# ── selftest: the three shipped defects must be re-detected ──────────────
SELFTEST_TEX = (
    r"\begin{figure}[t]\label{fig:one}\end{figure}" + "\n"
    r"\begin{figure}[t]\label{fig:two}\end{figure}" + "\n"
    r"see Fig.~\ref{fig:two} then Fig.~\ref{fig:one} and the H/W item" + "\n"
    r"a literal 5\% sign and then the SCENE token" + "\n"
    r"\begin{table}[t]\label{tab:orphan}\end{table}" + "\n"
)
SELFTEST_LOG = (
    "Overfull \\hbox (200.97778pt too wide) in paragraph at lines 124--125\n"
    "Overfull \\hbox (3.5pt too wide) in paragraph at lines 10--11\n"
)


def selftest() -> int:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "m.tex").write_text(SELFTEST_TEX, encoding="utf-8")
        (d / "m.log").write_text(SELFTEST_LOG, encoding="utf-8")
        fails, warns, advisories = check(d / "m.tex", d / "m.log")
    joined = "\n".join(fails + advisories)
    need = ["201.0pt", "orphan table: tab:orphan", "citation order: fig:two",
            "'H/W'", "'SCENE'"]
    missing = [n for n in need if n not in joined]
    if missing:
        print(f"SELFTEST FAIL: did not re-detect {missing}")
        print(joined)
        return 1
    print("SELFTEST PASS: overfull/orphan/order/caps all re-detected")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tex", required=True, help="manuscript .tex")
    ap.add_argument("--log", default=None, help="pdflatex .log of the same run")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    fails, warns, advisories = check(Path(args.tex), Path(args.log or "main.log"))
    for w in warns:
        print(f"WARN  {w}")
    for a in advisories:
        print(f"ADVISE {a}")
    if fails:
        for f in fails:
            print(f"FAIL  {f}")
        print(f"=== RESULT: {len(fails)} layout FAIL(s) ===")
        return 1
    print(f"=== RESULT: 0 layout FAIL(s) ({len(warns)} warn, {len(advisories)} advisory) ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
