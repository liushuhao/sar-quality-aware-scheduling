#!/usr/bin/env python3
"""verify_claim_traces.py — claim-level provenance gate for formula-spec.md.

Motivation: `check_citation_exists.py` (e5f3fc3) verifies that a bib entry
RESOLVES and that its metadata matches.  That is the wrong altitude for the
defects audit3 found in paper2:

  F1  Song 2025 :163 and :317 state OPPOSITE signs for the steering angle
      rate in sliding spotlight.  Both are real lines in a real paper.
  F2  Kim 2021 states the 25% margin in FOUR places (p.7/p.11/p.19/p.25);
      formula-spec, platform_kim2021.json and two source comments each
      carried a different count (2 / 3 / 3 / "three places").
  F3  formula-spec.md:335 pins g_T's cross-check source to "Song 2025 §2-§3";
      Song's full text has ZERO hits for nesz / noise equivalent.
  F5  formula-spec.md:64 and :218 cite `numerical_check.py`; no such file.

Every one of those passes a DOI/arXiv existence check.  They are claim-level
defects: the source exists, but it does not say what the spec says it says.
This gate checks the claim.

Mechanism: each registered claim carries source file + PDF page + a VERBATIM
quote.  A claim passes only if the quote is found inside that page's line
range of the extracted text.  Page boundaries come from the "N of M" PDF
footer markers, so the locator is independent of the quote's own wording.

Two failure modes are kept distinct on purpose:

  * quote absent  -> the spec attributes a statement the source does not make
                     (F1/F3 class), or the quote was transcribed wrong.
  * source missing -> literature/ is gitignored, so a fresh clone cannot
                     verify anything.  Reported as its own exit code, never as
                     a pass.  A silent skip here would make this gate a no-op
                     that looks green.

Line splitting uses split('\\n'), NOT str.splitlines(): the extracted text
contains 33 form-feed (0x0c) page separators, which splitlines() also breaks
on, shifting every line number after the first page by up to 32.

Exit codes:
  0  all registered claims verified
  1  at least one claim's quote is absent from its cited page
  2  a source file is missing (cannot verify) -- NOT a pass
  3  usage / registry error

Usage:
  python papers/sliding-spotlight-scheduling/scripts/verify_claim_traces.py
  python ... --registry <path.json>
  python ... --list
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REGISTRY = (
    REPO_ROOT
    / "papers/sliding-spotlight-scheduling/experiments/claim_trace.json"
)
LITERATURE = REPO_ROOT / "literature/fulltext"


class SourceMissing(Exception):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise SourceMissing(str(path))
    return path.read_text(encoding="utf-8", errors="replace")


def page_map(text: str, total_pages: int) -> dict[int, int]:
    """Map PDF page number -> 1-indexed line where that page's footer starts."""
    starts: dict[int, int] = {}
    for m in re.finditer(r"(\d+)\s+of\s+%d" % total_pages, text):
        starts.setdefault(int(m.group(1)), text[: m.start()].count("\n") + 1)
    return starts


def page_segment(text: str, starts: dict[int, int], page: int) -> str:
    if page not in starts:
        raise KeyError(page)
    first = starts[page]
    nxt = starts.get(page + 1)
    lines = text.split("\n")
    end = (nxt - 1) if nxt else len(lines)
    return " ".join(ln.strip() for ln in lines[first - 1 : end])


def normalize(s: str) -> str:
    """Collapse whitespace so extraction line-wrapping cannot mask a match."""
    return re.sub(r"\s+", " ", s).strip()


def verify_claim(claim: dict, text_cache: dict) -> tuple[str, str]:
    """Return (status, detail).  status in {PASS, FAIL}.

    Three claim kinds, dispatched on `expect` (default "quote-present"):

      quote-present   the quote must appear on the cited page
      absent-term     the term must NOT appear anywhere in the file.  Used to
                      register a claim whose defect IS the absence (F3: the
                      spec pins g_T to a source that never mentions it).
      file-absent     a cited script must NOT exist.  Registers a dead pointer
                      (F5) as a verified fact rather than leaving it implicit.
    """
    expect = claim.get("expect", "quote-present")

    if expect == "file-absent":
        hits = sorted(p.name for p in REPO_ROOT.rglob(claim["absent_path"]))
        if hits:
            return "FAIL", (
                f"{claim['absent_path']} now exists ({len(hits)} hit(s): "
                f"{', '.join(hits[:3])}); spec pointer is no longer dead"
            )
        return "PASS", f"{claim['absent_path']} absent repo-wide (dead pointer confirmed)"

    src = claim["source_file"]
    if src not in text_cache:
        try:
            text_cache[src] = read_text(LITERATURE / src)
        except SourceMissing as exc:
            raise SourceMissing(f"source file missing: {exc}") from exc
    text = text_cache[src]

    if expect == "absent-term":
        term = claim["absent_term"]
        n = len(re.findall(re.escape(term), text, re.IGNORECASE))
        if n:
            return "FAIL", (
                f"{term!r} now appears {n}x in {src}; the empty-source pin it "
                f"registered no longer holds"
            )
        return "PASS", f"{term!r} absent from all {len(text.split(chr(10)))} lines of {src}"

    starts = page_map(text, claim["source_total_pages"])
    try:
        segment = page_segment(text, starts, claim["source_page"])
    except KeyError:
        return "FAIL", f"page {claim['source_page']} not present in {src}"

    quote = claim["quote"]
    if normalize(quote) in normalize(segment):
        return "PASS", f"{src} p{claim['source_page']} L{starts[claim['source_page']]}"
    return "FAIL", (
        f"quote absent from {src} p{claim['source_page']} "
        f"(L{starts[claim['source_page']]}); searched for: {quote[:60]!r}"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    ap.add_argument("--list", action="store_true", help="list claims, verify nothing")
    ap.add_argument(
        "--only", action="append", default=[], help="verify only these claim ids"
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="exit 4 if any claim is still registered as an open defect "
             "(default: report them, exit 0)",
    )
    args = ap.parse_args(argv)

    if not args.registry.is_file():
        print(f"registry not found: {args.registry}", file=sys.stderr)
        return 3
    reg = json.loads(args.registry.read_text(encoding="utf-8"))
    claims = reg["claims"]

    if args.list:
        for c in claims:
            src = f"{c['source_file']} p{c['source_page']}"
            print(f"{c['id']:<10} {c.get('status', '?'):<22} {src:<45} {c.get('summary', '')}")
        print(f"\n{len(claims)} claims")
        return 0

    selected = [c for c in claims if not args.only or c["id"] in args.only]
    if not selected:
        print(f"no claims matched --only {args.only}", file=sys.stderr)
        return 3
    if not claims:
        # An empty registry would otherwise print "0/0 claims verified" and
        # exit 0 -- a gate that checks nothing looks exactly like a clean run.
        print("registry contains zero claims; refusing to report success", file=sys.stderr)
        return 3

    cache: dict[str, str] = {}
    failures: list[tuple[str, str]] = []
    open_defects: list[tuple[str, str]] = []
    for c in selected:
        try:
            status, detail = verify_claim(c, cache)
        except SourceMissing as exc:
            print(f"ERROR  {c['id']}: {exc}", file=sys.stderr)
            print(
                "\nRESULT: rc=2 (source missing) -- NOT a pass. literature/ is "
                "gitignored; restore it before trusting this gate.",
                file=sys.stderr,
            )
            return 2
        reg_state = c.get("status", "verified")
        # A registered defect that still verifies is a *pass on provenance* and
        # a *fail on the spec*.  Reporting only the first is the false-green
        # this summary exists to prevent.
        marker = "  <-- OPEN DEFECT" if reg_state not in ("verified", "closed") else ""
        print(f"{status:<6} {c['id']:<10} [{reg_state}] {detail}{marker}")
        if status == "FAIL":
            failures.append((c["id"], detail))
        elif reg_state not in ("verified", "closed"):
            open_defects.append((c["id"], reg_state))

    total = len(selected)
    if failures:
        print(f"\nRESULT: {len(failures)}/{total} claims FAILED provenance check")
        for cid, detail in failures:
            print(f"  {cid}: {detail}")
        return 1

    print(f"\nRESULT: {total}/{total} claims provenance-verified")
    if open_defects:
        print(
            f"WARNING: {len(open_defects)}/{total} verified claims are registered "
            f"OPEN DEFECTS in the spec -- provenance confirmed, spec still wrong:"
        )
        for cid, state in open_defects:
            print(f"  {cid} [{state}]")
        if args.strict:
            print("\nRESULT: rc=4 (--strict: open defects remain)")
            return 4
    else:
        print("no open defects registered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
