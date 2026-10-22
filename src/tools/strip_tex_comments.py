"""Strip LaTeX comments from a .tex file and print the result to stdout.

Usage:
    python src/tools/strip_tex_comments.py <input.tex>

Rule implemented
----------------
On each line, the first *unescaped* ``%`` (i.e. one preceded by an even
number of backslashes, including zero) starts a comment that runs to the end
of that line; everything from that ``%`` to the end of the line is removed.
A ``%`` preceded by an odd number of backslashes (``\\%``, ``\\\\\\%``) is a
literal percent sign and is kept.  Lines without a comment are passed
through unchanged.

Formatting guarantees
---------------------
* The input is read as UTF-8 bytes and written to ``sys.stdout.buffer`` as
  UTF-8 bytes, so nothing is re-encoded or mangled (CRLF stays CRLF, and
  Chinese text round-trips).
* Line terminators are never removed: a whole-line comment becomes an empty
  line rather than disappearing, so line numbers in the original file remain
  valid when you look up a LaTeX error.

Known limitation (deliberately out of scope)
--------------------------------------------
This is a line-oriented lexer, not a TeX parser.  It does not know about
verbatim-like environments (``verbatim``, ``verbatim*``, ``lstlisting``,
``minted``, ``comment``), where ``%`` is literal text and must be kept.  Any
``%`` inside those environments will therefore be treated as a comment start
and truncated.  Nor does it handle ``%`` inside ``\\verb|...|``.  Run it on
files that are known to be free of such constructs, or post-check the diff.

Only the Python standard library is used (``argparse``, ``sys``, ``pathlib``).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _split_eol(line: str) -> tuple[str, str]:
    """Split a line into (body, terminator), terminator being "\\r\\n", "\\n",
    "\\r" or "" when the line has no terminator."""
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    if line.endswith("\r"):
        return line[:-1], "\r"
    return line, ""


def _backslash_run(body: str, pos: int) -> int:
    """Number of consecutive backslashes immediately before ``pos``."""
    count = 0
    idx = pos - 1
    while idx >= 0 and body[idx] == "\\":
        count += 1
        idx -= 1
    return count


def _strip_line_body(body: str) -> str:
    """Drop the first unescaped % in ``body`` and everything after it."""
    for pos, char in enumerate(body):
        if char != "%":
            continue
        if _backslash_run(body, pos) % 2 == 0:
            return body[:pos]
        # Escaped percent: literal, keep scanning.
    return body


def strip_comments(text: str) -> str:
    """Return ``text`` with LaTeX comments removed, preserving every newline.

    Newline style is preserved per line (mixed CRLF/LF input stays mixed) and
    the number of lines is unchanged.
    """
    out = []
    # Split on "\n" only: rejoining with "\n" is lossless, and a trailing
    # "\r" (from CRLF) is treated as part of the terminator by _split_eol.
    for raw in text.split("\n"):
        body, eol = _split_eol(raw)
        out.append(_strip_line_body(body) + eol)
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="strip_tex_comments.py",
        description=(
            "Print a .tex file with LaTeX comments (% to end of line) removed. "
            "Literal \\% is kept; CRLF is preserved; UTF-8 is used for both "
            "input and output."
        ),
    )
    parser.add_argument(
        "input",
        help="path to the .tex file to process",
    )
    args = parser.parse_args(argv)

    path = Path(args.input)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        print(f"strip_tex_comments: cannot read {path}: {exc}", file=sys.stderr)
        return 2

    text = raw.decode("utf-8")
    sys.stdout.buffer.write(strip_comments(text).encode("utf-8"))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
