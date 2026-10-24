"""R51 drift guard: SLEW / SETTLE must not silently diverge across the tooling.

Ledger entry **R51** (2026-10-24).  Paper-1 tooling hard-codes the attitude slew
rate and the post-maneuver settle time as *local* constants in dozens of scripts
under ``src/sar_sim`` and ``papers/single-sat-quality``.  Every copy agrees today
(0.0524 rad/s and 5.0 s), but nothing stops one copy from drifting: a single
``SLEW_RATE = 0.06`` edit changes every C2 transition time ``tau`` in that
script, and the script's numbers silently stop being comparable with the rest of
the paper.

Canonical source of truth
-------------------------
``src/sar_sim/solver/baselines.py:133-134`` — the defaults of
``_enforce_c2_transitions(max_slew_rate=0.0524, settle_time=5.0)``, i.e. the
library-side definition that the C2 verifier and the baselines share.  The two
numbers are asserted against that definition in
``test_canonical_source_matches_guard_constants`` below, so the guard cannot
drift away from the library either.

Assignment shapes covered (all shapes that occur in the live tree)
------------------------------------------------------------------
    SLEW_RATE = 0.0524                        # plain assignment
    SLEW, SETTLE = 0.0524, 5.0                # tuple unpacking
    SLEW = 0.0524; SETTLE = 5.0               # two statements on one line
    SLEW, SETTLE, STEP = 0.0524, 5.0, 10.0    # extra names ignored, pair checked
    SETTLE_TIME = 5.0    # trailing comment   # comment stripped
    SLEW, SETTLE = (                          # bracket-continued
        0.0524, 5.0)

Only *literal* values are checked.  References are not definitions and are
deliberately skipped, e.g. ``max_slew_rate=run_d.SLEW_RATE`` or
``kwargs.get("max_slew_rate", SLEW_RATE)``; so are keyword arguments such as
``build_agile_instance(..., max_slew_rate=0.0524)`` (lower-case names are not
``SLEW*``/``SETTLE*`` definitions).

Fail-closed floor
-----------------
``MIN_DEFINITION_POINTS`` guards against the guard itself going hollow: if a
path change or a regex regression stops matching, the test fails on the count
instead of passing with zero definitions found.
"""

import re
from pathlib import Path
from typing import Iterator, List, Tuple

import pytest

# ── Canonical values (ledger R51) ────────────────────────────────────────
CANONICAL_SLEW_RATE = 0.0524   # rad/s, ~3 deg/s
CANONICAL_SETTLE_TIME = 5.0    # s
CANONICAL = {
    "SLEW": CANONICAL_SLEW_RATE,
    "SETTLE": CANONICAL_SETTLE_TIME,
}

# Anti-false-green floor: the live tree defines the pair in ~46 files.
MIN_DEFINITION_POINTS = 25

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = (
    REPO_ROOT / "src" / "sar_sim",
    REPO_ROOT / "papers" / "single-sat-quality",
)
CANONICAL_SOURCE = REPO_ROOT / "src" / "sar_sim" / "solver" / "baselines.py"

# ── Scanner internals ────────────────────────────────────────────────────
_NAME = r"[A-Za-z_]\w*"

# Left-hand side of an assignment: bare names, optionally annotated, comma
# separated.  Anything containing brackets/spaces/keywords (``def f(x``,
# ``build(..., max_slew_rate``) fails to match and is therefore ignored.
_LHS_RE = re.compile(
    r"^(?P<names>"
    rf"{_NAME}(?:\s*:\s*[^,=]+)?"
    rf"(?:\s*,\s*{_NAME}(?:\s*:\s*[^,=]+)?)*"
    r")$"
)
_SLEW_SETTLE_NAME = re.compile(r"^(?:SLEW|SETTLE)[A-Z0-9_]*$")
_NUMBER = re.compile(r"^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$")
# An assignment '=', not ==, !=, <=, >=, :=, +=, ...
_ASSIGN_OP = re.compile(r"(?<![=!<>+\-*/%&|^:])=(?!=)")
_STRING_LITERAL = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'')


def _strip_comment(line: str) -> str:
    """Drop a trailing ``# ...`` comment, respecting string literals."""
    out: List[str] = []
    quote = None
    i = 0
    while i < len(line):
        ch = line[i]
        if quote is not None:
            out.append(ch)
            if ch == "\\" and i + 1 < len(line):
                out.append(line[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def _bracket_delta(code: str) -> int:
    code = _STRING_LITERAL.sub("", code)
    return sum(code.count(c) for c in "([{") - sum(code.count(c) for c in ")]}")


def _logical_lines(text: str) -> Iterator[str]:
    """Yield statements with comments stripped and bracket continuations joined."""
    buf: List[str] = []
    depth = 0
    for raw in text.splitlines():
        code = _strip_comment(raw)
        if not buf and not code.strip():
            continue
        buf.append(code)
        depth += _bracket_delta(code)
        joined = " ".join(buf)
        if depth > 0 or joined.rstrip().endswith("\\"):
            continue
        yield joined
        buf = []
        depth = 0
    if buf:
        yield " ".join(buf)


def _split_top_level(text: str) -> List[str]:
    """Split on commas that are not inside brackets."""
    parts: List[str] = []
    depth = 0
    cur: List[str] = []
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
            continue
        cur.append(ch)
    parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


def find_slew_settle_definitions(source: str) -> List[Tuple[str, float]]:
    """Extract every literal ``SLEW*`` / ``SETTLE*`` definition in ``source``.

    Returns a list of ``(name, value)`` pairs.  Non-literal right-hand sides and
    names outside the ``SLEW*``/``SETTLE*`` family are ignored.
    """
    found: List[Tuple[str, float]] = []
    for statement in _logical_lines(source):
        for stmt in statement.split(";"):
            ops = list(_ASSIGN_OP.finditer(stmt))
            if not ops:
                continue
            segments = [stmt[: ops[0].start()]] + [
                stmt[ops[i].end(): ops[i + 1].start()]
                for i in range(len(ops) - 1)
            ]
            rhs = stmt[ops[-1].end():].strip()
            names: List[str] = []
            for seg in segments:
                m = _LHS_RE.match(seg.strip())
                if not m:
                    names = []
                    break
                names.extend(
                    part.split(":", 1)[0].strip()
                    for part in m.group("names").split(",")
                )
            if not names:
                continue

            if rhs.startswith("(") and rhs.endswith(")"):
                rhs = rhs[1:-1]
            raw_values = _split_top_level(rhs)
            values: List[float] = []
            for raw in raw_values:
                raw = raw.rstrip("\\").strip()
                if not _NUMBER.match(raw):
                    values = []
                    break
                values.append(float(raw))
            if not values:
                continue
            if len(values) != len(names):
                # Ambiguous name/value split (e.g. ``A, B = f()``): leave it to
                # the code reviewer rather than guessing which number is which.
                continue
            found.extend(
                (name, value)
                for name, value in zip(names, values)
                if _SLEW_SETTLE_NAME.match(name)
            )
    return found


def _scan_file(path: Path) -> List[Tuple[str, float]]:
    return find_slew_settle_definitions(
        path.read_text(encoding="utf-8", errors="replace")
    )


def _iter_scan_files() -> Iterator[Path]:
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            yield path


def collect_definition_points() -> List[Tuple[Path, str, float]]:
    """All ``(path, name, value)`` definition points in the live tree."""
    points: List[Tuple[Path, str, float]] = []
    for path in _iter_scan_files():
        for name, value in _scan_file(path):
            points.append((path, name, value))
    return points


def _canonical_for(name: str) -> float:
    return CANONICAL["SLEW"] if name.startswith("SLEW") else CANONICAL["SETTLE"]


# ── 1. Discriminating power: the scanner must see drift ──────────────────

@pytest.mark.parametrize(
    "source, name, value",
    [
        ("SLEW_RATE = 0.0524", "SLEW_RATE", 0.0524),
        ("SLEW = 0.06", "SLEW", 0.06),
        ("SLEW, SETTLE = 0.0524, 5.0", "SLEW", 0.0524),
        ("SLEW, SETTLE = 0.0524, 4.0", "SETTLE", 4.0),
        ("SLEW = 0.0524; SETTLE = 5.0", "SETTLE", 5.0),
        ("SLEW = 0.0524; SETTLE = 3.0", "SETTLE", 3.0),
        ("SETTLE_TIME = 5.0   # seconds", "SETTLE_TIME", 5.0),
        ("SLEW, SETTLE, STEP = 0.0524, 5.0, 10.0", "SETTLE", 5.0),
        ("SLEW, SETTLE = (\n    0.0524, 5.0\n)", "SETTLE", 5.0),
    ],
)
def test_scanner_reads_all_definition_shapes(source, name, value):
    """Every shape used in the tree is parsed into the right (name, value)."""
    defs = dict(find_slew_settle_definitions(source))
    assert name in defs, f"scanner missed {name} in {source!r}: got {defs}"
    assert defs[name] == pytest.approx(value)


@pytest.mark.parametrize(
    "source",
    [
        "SLEW_RATE = 0.06",
        "SETTLE = 4.0",
        "SLEW, SETTLE = 0.0524, 4.5",
        "SLEW = 0.0524; SETTLE = 2.0",
        "SLEW_RATE = 0.06   # drifted",
    ],
)
def test_scanner_flags_drifted_samples(source):
    """Synthetic bad samples must be detected as drift (guard is not inert)."""
    defs = find_slew_settle_definitions(source)
    assert defs, f"scanner returned nothing for {source!r}"
    bad = [
        (name, value)
        for name, value in defs
        if value != pytest.approx(_canonical_for(name))
    ]
    assert bad, f"drift not detected in {source!r}: got {defs}"


@pytest.mark.parametrize(
    "source",
    [
        "x = 0.0524",
        "max_slew_rate = run_d.SLEW_RATE",
        "max_slew_rate=0.0524, settle_time=5.0",
        "if SLEW_RATE == 0.0524:",
        "SLEW_RATE += 0.01",
        'note = "SLEW_RATE = 0.06"',
        "settle_time = max(settle_time, 5.0)",
    ],
)
def test_scanner_ignores_non_definitions(source):
    """References, kwargs, comparisons and aug-assigns are not definitions."""
    assert find_slew_settle_definitions(source) == []


# ── 2. The live tree ─────────────────────────────────────────────────────

def test_scan_roots_exist():
    missing = [str(p) for p in SCAN_ROOTS if not p.exists()]
    assert not missing, f"scan roots missing (guard would go green silently): {missing}"


def test_no_drifted_definitions_in_live_tree():
    """Every literal SLEW*/SETTLE* definition must equal the canonical pair."""
    drifted = []
    for path, name, value in collect_definition_points():
        canonical = _canonical_for(name)
        if value != canonical:
            try:
                shown = path.relative_to(REPO_ROOT)
            except ValueError:  # scan root outside the repo (ad-hoc runs)
                shown = path
            drifted.append(
                f"{shown}: {name} = {value!r} "
                f"(canonical {canonical!r})"
            )
    assert not drifted, (
        "SLEW/SETTLE drift detected (ledger R51; canonical source is "
        "src/sar_sim/solver/baselines.py:133-134):\n  " + "\n  ".join(drifted)
    )


def test_definition_points_meet_floor():
    """Fail-closed floor: zero/low matches means the scanner went blind.

    Note: ``src/sar_sim`` itself uses ``max_slew_rate=`` / ``settle_time=``
    keywords and instance attributes, not upper-case ``SLEW*``/``SETTLE*``
    constants, so the upper-case definition points all live under
    ``papers/single-sat-quality``.  The scan-root check below therefore counts
    *files scanned*, not per-root hits.
    """
    files = list(_iter_scan_files())
    assert len(files) >= 50, (
        f"only {len(files)} python files scanned — scan roots regressed"
    )
    points = collect_definition_points()
    assert len(points) >= MIN_DEFINITION_POINTS, (
        f"only {len(points)} SLEW/SETTLE definition points found, expected "
        f"at least {MIN_DEFINITION_POINTS} — scanner or scan roots regressed"
    )


def test_canonical_source_matches_guard_constants():
    """Guard constants must match the canonical definition in baselines.py."""
    source = CANONICAL_SOURCE.read_text(encoding="utf-8")
    m = re.search(r"def _enforce_c2_transitions\((.*?)\)\s*->", source, re.S)
    assert m, "canonical definition _enforce_c2_transitions(...) not found"
    params = m.group(1)
    slew = re.search(r"max_slew_rate:\s*float\s*=\s*([0-9.eE+-]+)", params)
    settle = re.search(r"settle_time:\s*float\s*=\s*([0-9.eE+-]+)", params)
    assert slew and settle, f"canonical defaults not parseable: {params!r}"
    assert float(slew.group(1)) == pytest.approx(CANONICAL_SLEW_RATE)
    assert float(settle.group(1)) == pytest.approx(CANONICAL_SETTLE_TIME)
