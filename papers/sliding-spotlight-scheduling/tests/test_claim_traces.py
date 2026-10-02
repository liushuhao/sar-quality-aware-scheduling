#!/usr/bin/env python3
"""Test wrapper for the claim-provenance gate.

The gate itself is a standalone script (scripts/verify_claim_traces.py) with
its own exit codes, because it is meant to run in CI and in run_verify.py as a
process, not as an import.  This wrapper puts it in the domain regression suite
so a claim that silently rots turns the test run red.

Two things are asserted here, and the distinction matters:

  * every registered claim's quote is still findable in its cited source
    (provenance intact), AND
  * the verifier reports its open defects rather than reporting a clean 10/10
    (no false green).

Deliberately NOT asserted: that the spec is correct.  Nine of the ten claims
are registered defects awaiting ticket 21; failing this suite on them would
mean the gate is working and the ticket is late, so those are surfaced through
the caller's rc and the printed WARNING instead.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
SCRIPT = FORK_DOMAIN / "scripts" / "verify_claim_traces.py"
REGISTRY = FORK_DOMAIN / "experiments" / "claim_trace.json"
# tests/ -> sliding-spotlight-scheduling/ -> papers/ -> <repo root>
LITERATURE = FORK_DOMAIN.parents[1] / "literature" / "fulltext"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


@pytest.fixture(scope="module")
def registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_script_and_registry_exist():
    assert SCRIPT.is_file(), f"missing verifier: {SCRIPT}"
    assert REGISTRY.is_file(), f"missing claim registry: {REGISTRY}"


def test_registry_is_not_empty(registry):
    """An empty registry would make the whole suite vacuously green."""
    assert registry["claims"], "claim registry has zero claims"


def test_every_claim_has_required_fields(registry):
    """A claim missing page/quote/total_pages silently degrades to a no-op."""
    required = {"id", "source_file", "quote", "source_page", "source_total_pages"}
    bad = [
        c.get("id", "<no id>")
        for c in registry["claims"]
        if not required.issubset(c)
    ]
    assert not bad, f"claim(s) missing required fields: {bad}"


def test_claim_ids_unique(registry):
    ids = [c["id"] for c in registry["claims"]]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    assert not dupes, f"duplicate claim id(s): {dupes}"


def test_page_within_source_bounds(registry):
    """A page number past the PDF's last page makes page_segment raise KeyError
    at verify time; catch it at registry-edit time instead."""
    bad = [
        c["id"]
        for c in registry["claims"]
        if not 1 <= c["source_page"] <= c["source_total_pages"]
    ]
    assert not bad, f"claim(s) with out-of-range source_page: {bad}"


def test_provenance_gate_passes():
    """Every registered quote must still be findable in its cited source.

    Skipped, not failed, when literature/ is absent: it is gitignored, and a
    fresh clone legitimately cannot verify.  The gate script returns rc=2 there
    rather than pretending to pass.
    """
    if not LITERATURE.is_dir():
        pytest.skip(f"literature/ absent ({LITERATURE}); provenance unverifiable")
    r = run()
    assert r.returncode == 0, (
        f"claim provenance gate failed (rc={r.returncode}):\n{r.stdout}\n{r.stderr}"
    )


def test_gate_reports_open_defects():
    """The false-green guard: ticket-21 defects are registered, so the gate must
    name them.  If someone marks them all 'verified' without fixing the spec,
    this goes red.

    Fails only if the registry claims zero open defects while audit3's F1/F2/
    F3/F5 are still unfixed in formula-spec.md.
    """
    if not LITERATURE.is_dir():
        pytest.skip("literature/ absent; open-defect state unverifiable")
    r = run()
    open_states = {"open", "known-wrong", "known-broken", "provenance-label-wrong"}
    registered = [
        c["id"]
        for c in json.loads(REGISTRY.read_text(encoding="utf-8"))["claims"]
        if c.get("status") in open_states
    ]
    if not registered:
        pytest.fail(
            "no open defects registered, but audit3 F1/F2/F3/F5 remain "
            "unfixed in formula-spec.md — do not mark claims closed until "
            "ticket 21 actually lands"
        )
    for cid in registered:
        assert cid in r.stdout, (
            f"claim {cid} is registered as an open defect but the gate output "
            f"does not mention it — false green:\n{r.stdout}"
        )


def test_empty_registry_is_rejected(tmp_path, registry):
    """A gate that checks nothing must not exit 0."""
    empty = dict(registry)
    empty["claims"] = []
    p = tmp_path / "empty.json"
    p.write_text(json.dumps(empty, ensure_ascii=False), encoding="utf-8")
    r = run("--registry", str(p))
    assert r.returncode == 3, f"empty registry returned rc={r.returncode}, expected 3"


def test_tampered_quote_is_rejected(tmp_path, registry):
    """Mutation: corrupt one quote, the gate must go red.

    Without this the suite would only ever see the happy path, and a verifier
    that always returns PASS would look identical to a working one.
    """
    if not LITERATURE.is_dir():
        pytest.skip("literature/ absent")
    bad = json.loads(json.dumps(registry))
    target = next(c for c in bad["claims"] if c.get("expect", "quote-present") == "quote-present")
    target["quote"] = "THIS SENTENCE IS NOT IN ANY OF THE SOURCES"
    p = tmp_path / "tampered.json"
    p.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
    r = run("--registry", str(p), "--only", target["id"])
    assert r.returncode == 1, (
        f"tampered quote not caught (rc={r.returncode}):\n{r.stdout}"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
