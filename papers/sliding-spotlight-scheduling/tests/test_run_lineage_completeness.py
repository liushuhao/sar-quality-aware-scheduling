#!/usr/bin/env python3
"""Completeness guard for experiments/RUN_LINEAGE.md.

The lineage table is HAND-MAINTAINED (decision 2026-10-02: a generator script
for ~10 nodes is over-engineering).  Hand-maintained registries rot silently,
so this guard fails when:

  1. a directory appears under experiments/results/ that is not registered;
  2. RUN_LINEAGE.md names a results path that does not exist (phantom node);
  3. a node id is registered twice.

It deliberately does NOT assert artifact counts — those legitimately change
while a run is in flight, and a count guard would fire on healthy work.
"""
import re
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
RESULTS = FORK_DOMAIN / "experiments" / "results"
LINEAGE = FORK_DOMAIN / "experiments" / "RUN_LINEAGE.md"

PATH_TOKEN = re.compile(r"experiments/results/([A-Za-z0-9_][A-Za-z0-9_\-]*)")
NODE_ROW = re.compile(r"^\|\s*`(L\d+[a-z]?)`\s*\|", re.M)


@pytest.fixture(scope="module")
def doc() -> str:
    return LINEAGE.read_text(encoding="utf-8")


def registered_nodes(doc: str) -> set[str]:
    return set(PATH_TOKEN.findall(doc))


def test_lineage_file_exists():
    assert LINEAGE.is_file(), f"missing lineage registry: {LINEAGE}"


def test_results_root_exists():
    assert RESULTS.is_dir(), f"missing results root: {RESULTS}"


def test_every_results_dir_is_registered(doc):
    """Any new top-level node must be added to the table in the same commit."""
    on_disk = {p.name for p in RESULTS.iterdir() if p.is_dir()}
    missing = sorted(on_disk - registered_nodes(doc))
    assert not missing, (
        "unregistered run node(s) under experiments/results/: "
        f"{missing} — add a row to RUN_LINEAGE.md (section 一) "
        "and link the results path"
    )


def test_no_phantom_results_paths(doc):
    """Every path the registry names must actually exist on disk."""
    on_disk = {p.name for p in RESULTS.iterdir() if p.is_dir()}
    phantom = sorted(registered_nodes(doc) - on_disk)
    assert not phantom, (
        f"RUN_LINEAGE.md references results path(s) that do not exist: {phantom}"
    )


def test_node_ids_unique(doc):
    """A duplicated L-id means two rows silently claim the same lineage slot."""
    ids = NODE_ROW.findall(doc)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    assert ids, "no node rows parsed — table format changed?"
    assert not dupes, f"duplicate node id(s) in RUN_LINEAGE.md: {dupes}"


def test_every_node_row_carries_an_evidence_commits(doc):
    """Anti-rot: a lineage row with no evidence commit is an unsourced claim.

    Accepts a backticked short sha (7+ hex) or an explicit artefact reference
    (backticked .json / .md path) — the two forms actually used in the table.
    """
    bad = []
    for line in doc.splitlines():
        if not NODE_ROW.match(line):
            continue
        node = NODE_ROW.match(line).group(1)
        if not re.search(r"`[0-9a-f]{7,}`|`[^`]+\.(json|md)`", line):
            bad.append(node)
    assert not bad, (
        f"lineage row(s) with no evidence commit/artefact pointer: {bad}"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
