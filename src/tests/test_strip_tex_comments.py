"""Tests for strip_tex_comments.py — LaTeX comment stripping.

Style follows the other files in src/tests/: a module docstring stating what
is locked, ``Path(__file__).resolve()`` based repo paths, and pytest cases
that build their own fixtures in ``tmp_path`` (no fixture data files added).

The cases lock the behaviours the CLI promises:
  * a file without comments is returned byte-for-byte unchanged;
  * the first unescaped ``%`` starts a comment, and the rest of that line goes;
  * a whole-line comment leaves an *empty* line (line count is preserved);
  * ``\\%`` is a literal percent and survives;
  * a leading ``%%`` is one comment, not two;
  * CRLF input stays CRLF on stdout;
  * UTF-8 Chinese text round-trips;
  * an even backslash run (``\\\\%``) still opens a comment.
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "src" / "tools"
SCRIPT = TOOLS / "strip_tex_comments.py"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from strip_tex_comments import strip_comments  # noqa: E402


# ---------------------------------------------------------------------------
# Pure-function tests
# ---------------------------------------------------------------------------

def test_no_comments_file_is_unchanged():
    """A file with no % at all must come out identical."""
    text = "\\documentclass{article}\n\\begin{document}\nHello.\n\\end{document}\n"
    assert strip_comments(text) == text


def test_trailing_comment_is_removed():
    """Text before an unescaped % is kept, the comment is dropped."""
    assert strip_comments("x = 1 % explain the 1\n") == "x = 1 \n"


def test_whole_line_comment_leaves_empty_line():
    """A comment-only line becomes an empty line, so line numbers stay valid."""
    text = "% a banner comment\nreal content\n"
    assert strip_comments(text) == "\nreal content\n"
    # Same number of lines: 3 pieces when split on "\n".
    assert len(strip_comments(text).split("\n")) == len(text.split("\n"))


def test_literal_percent_backslash_is_kept():
    """\\% is a literal percent sign and must survive."""
    text = "profit = 5\\% of budget\n"
    assert strip_comments(text) == text


def test_double_percent_at_line_start_is_one_comment():
    """%% is a single comment mark, so the whole line goes."""
    text = "%% Section note\nbody\n"
    assert strip_comments(text) == "\nbody\n"


def test_crlf_line_endings_are_preserved():
    """CRLF input keeps CRLF on every line, commented or not."""
    text = "kept % gone\r\nclean line\r\n"
    assert strip_comments(text) == "kept \r\nclean line\r\n"


def test_utf8_chinese_line_round_trips():
    """A Chinese line without comments is untouched; with one, only the tail goes."""
    assert strip_comments("中文无注释\n") == "中文无注释\n"
    assert strip_comments("中文行 % 中文注释\n") == "中文行 \n"


def test_even_backslash_run_opens_comment():
    """\\\\% is an escaped backslash followed by an unescaped %, so it comments out."""
    text = "path C:\\\\% trailing\n"
    assert strip_comments(text) == "path C:\\\\\n"


# ---------------------------------------------------------------------------
# CLI tests (real subprocess, byte-level stdout comparison)
# ---------------------------------------------------------------------------

@pytest.fixture
def tex_file(tmp_path):
    """Write a CRLF + Chinese + comment fixture file and return its path."""
    path = tmp_path / "sample.tex"
    path.write_bytes(
        "% 抬头注释\r\n"
        "费率 5\\% 保留\r\n"
        "中文正文 % 去掉这段\r\n"
        "无注释行\r\n".encode("utf-8")
    )
    return path


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
    )


def test_cli_strips_and_preserves_utf8_crlf(tex_file):
    """stdout is exact UTF-8 bytes with CRLF kept; exit code is 0."""
    proc = _run_cli(str(tex_file))
    assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")
    expected = (
        "\r\n"
        "费率 5\\% 保留\r\n"
        "中文正文 \r\n"
        "无注释行\r\n"
    ).encode("utf-8")
    assert proc.stdout == expected
    assert b"\r\n" in proc.stdout


def test_cli_help_exits_zero():
    """--help must work (argparse) and exit 0."""
    proc = _run_cli("--help")
    assert proc.returncode == 0
    out = proc.stdout.decode("utf-8", "replace")
    assert "input" in out
    assert "%" in out
