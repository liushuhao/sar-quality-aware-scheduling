#!/usr/bin/env python3
"""Ticket 52 -- standing tests for the per-node serviceability checker (G1).

Collected by the domain suite = the standing gate is wired (ticket 52
acceptance item 4: the suite picking this file up IS the registration; the
checker itself lives at experiments/check_per_node_serviceability.py).

Shapes:
  * real v5 world             -> rc 0, HEADLINE 25/25, centre node reproduces
    the registered 2.00 transits/24h, per-node drawn counts match the
    registered assignment rule (i % 25 over n_drawn), zero-draw nodes named.
  * red proof (a): one node's in-band transits erased -> rc 1 AND the node is
    named.  The transit count is a geometric RECOMPUTE, not a stored artifact,
    so "erasing a node's transits" is only expressible at the counter seam:
    the fixture is a full temp-dir COPY of the world inputs (manifests +
    platform + template) with compute_node_transit_counts stubbed to zero
    node 7.  Tilting the orbit or narrowing the band cannot target one node.
  * red proof (b): a fixture with zero-draw nodes (real R1C manifests: N=20
    drawn onto 25 nodes -> nodes 20-24 drawn 0) -> named explicitly, never
    dropped from the 25-node table.

Expectations come from the registry face (realwindow_scenario_template.json)
and the registered assignment rule -- never read back from the checker's own
output (ticket 52 acceptance: no self-referential expectations).

Usage (repo root):
    PYTHONPATH=src:papers/sliding-spotlight-scheduling \
      "/d/Program Files/Python/python" -m pytest \
      papers/sliding-spotlight-scheduling/tests/test_per_node_serviceability.py -v
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def _haversine_km(lat1, lon1, lat2, lon2):
    """Independent metric (NOT the checker's equirectangular one) for the
    tie-margin cross-check."""
    import math

    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))

FORK = Path(__file__).resolve().parent.parent
REPO = FORK.parent.parent
CHECKER = FORK / "experiments" / "check_per_node_serviceability.py"
SCENARIOS = FORK / "experiments" / "v5_results" / "scenarios"
PLATFORM = FORK / "experiments" / "v5_results" / "platform.json"
TEMPLATE = FORK / "experiments" / "realwindow_scenario_template.json"
sys.path.insert(0, str(FORK / "experiments"))

import check_per_node_serviceability as cpns  # noqa: E402

ZERO_DRAW_R1C = [20, 21, 22, 23, 24]  # N=20 onto 25 nodes, rule i % 25
# rule-derived aggregate drawn: nodes 0-19 get 10*1 (R1C) + 10*2 (R2F) +
# 10*4 (R3H) = 70; nodes 20-24 get 0 + 20 + 40 = 60
EXPECTED_AGG_DRAWN = [70] * 20 + [60] * 5


@pytest.fixture(scope="module")
def real_run() -> subprocess.CompletedProcess:
    """One end-to-end subprocess run against the real v5 world, shared."""
    return subprocess.run(
        [sys.executable, "-B", str(CHECKER)],
        capture_output=True, text=True, cwd=str(REPO), timeout=600,
    )


def _copy_world(tmp_path: Path, names=None):
    """Temp-dir fixture copy of the world inputs (v5 originals untouched)."""
    scn = tmp_path / "scenarios"
    scn.mkdir()
    for p in sorted(SCENARIOS.glob("*.json")):
        if names is None or p.name in names:
            shutil.copy2(p, scn / p.name)
    plat = tmp_path / "platform.json"
    tmpl = tmp_path / "template.json"
    shutil.copy2(PLATFORM, plat)
    shutil.copy2(TEMPLATE, tmpl)
    return scn, plat, tmpl


def test_real_world_green_headline_and_counts(real_run):
    out = real_run.stdout
    assert real_run.returncode == 0, out[-2000:]
    assert "HEADLINE: 25/25 nodes carry >=1 in-band transit over 72 h" in out
    assert re.search(
        r"CENTRE node 12: 6 transits over 3\.0 d = 2\.00 transits/24h "
        r"\(registered 2\.00", out
    ), "centre node must reproduce the registered 2.00 transits/24h"
    # per-node rows present for ALL 25 nodes (none dropped), each >=1 transit
    rows = re.findall(r"^\s*(\d+)\s+\(\d,\d\)\s+.*\s(\d+)\s+(\d+)\s+(\d+)\s+([0-9.]+)$",
                      out, re.M)
    assert len(rows) == 25, f"expected 25 per-node rows, got {len(rows)}"
    for row in rows:
        assert int(row[3]) >= 1, f"node {row[0]} carries 0 in-band transits"
    # the real zero-draw trigger path is reported BY NAME for every R1C seed
    assert out.count("ZERO-DRAW R1C_") == 10
    assert f"nodes {ZERO_DRAW_R1C}" in out
    assert "AGGREGATE ZERO-DRAW: none" in out
    assert "VERDICT: GREEN" in out


def test_real_world_drawn_served_structure():
    """drawn/served against the registered rule + registry ledger face (no
    geometry -- the in-process analyze path on the real manifests)."""
    analysis = cpns.analyze_manifests(cpns.load_r_manifests(SCENARIOS))
    assert analysis["failures"] == []
    assert analysis["agg_drawn"] == EXPECTED_AGG_DRAWN
    # served totals must equal the registry ledger face (generation_ledger)
    ledger_served = sum(
        doc["generation_ledger"]["n_served"]
        for _, doc in cpns.load_r_manifests(SCENARIOS)
    )
    assert sum(analysis["agg_served"]) == ledger_served
    for name, sc in analysis["per_scenario"].items():
        for k in range(25):
            assert sc["served"][k] <= sc["drawn"][k], (
                f"{name} node {k}: served above drawn -- drawn coverage is "
                "only a lower-bound proof for served"
            )
        if name.startswith("R1C"):
            assert sc["zero_draw"] == ZERO_DRAW_R1C
        else:
            assert sc["zero_draw"] == []
    assert analysis["min_margin_km"] > 0.0, (
        "B-leg reverse map dies on a non-positive tie margin (route-decision "
        "red line); recompute leg must be re-adjudicated"
    )
    # independent-metric cross-check of the tie-margin guard: haversine over
    # the same tasks, none of the checker's distance code involved
    manifests = cpns.load_r_manifests(SCENARIOS)
    ref = manifests[0][1]["preregistration"]
    centre = ref["domain_centre_deg"]
    nodes = cpns.grid_nodes(centre[0], centre[1], ref["grid_n"],
                            ref["grid_spacing_km"])
    min_hav = min(
        sorted(_haversine_km(t["lat_deg"], t["lon_deg"], nlat, nlon)
               for nlat, nlon in nodes)[1]
        - sorted(_haversine_km(t["lat_deg"], t["lon_deg"], nlat, nlon)
                 for nlat, nlon in nodes)[0]
        for _, doc in manifests for t in doc["tasks"]
    )
    assert min_hav > 0.0, "haversine tie margin non-positive -- metric-independent"


def test_red_erased_node_is_named(tmp_path, monkeypatch, capsys):
    """Red proof (a): erase node 7's in-band transits -> RED, node 7 named."""
    scn, plat, tmpl = _copy_world(tmp_path)
    monkeypatch.setattr(
        cpns, "compute_node_transit_counts",
        lambda *a, **k: {i: (0 if i == 7 else 6) for i in range(25)},
    )
    rc = cpns.main([
        "--scenarios-dir", str(scn), "--platform", str(plat),
        "--template", str(tmpl),
    ])
    out = capsys.readouterr().out
    assert rc == 1
    assert "nodes with ZERO in-band transits over the span: [7]" in out
    assert "HEADLINE: 24/25" in out
    # the erased node surfaces as exactly its two coupled views (node-level
    # + headline-level) and nothing else -- the centre rate stays 2.00-green
    assert "FAIL: headline mismatch: recomputed 24/25 vs registered 25/25" in out
    assert out.count("FAIL:") == 2
    assert "centre node 12 rate" not in out
    assert "VERDICT: RED" in out
    # the drawn/served pipeline really ran on the fixture copy (real data)
    assert "ZERO-DRAW R1C_seed100" in out


def test_zero_draw_nodes_named_and_kept(tmp_path):
    """Red proof (b): zero-draw nodes are named and stay in the node universe."""
    scn, _, _ = _copy_world(tmp_path, names={"R1C_seed100.json", "R1C_seed101.json"})
    analysis = cpns.analyze_manifests(cpns.load_r_manifests(scn))
    assert analysis["failures"] == []
    for name, sc in analysis["per_scenario"].items():
        assert sc["zero_draw"] == ZERO_DRAW_R1C, name
    # nodes 20-24 are present in the maps with drawn == 0 -- not dropped
    assert len(analysis["agg_drawn"]) == 25
    assert [analysis["agg_drawn"][k] for k in ZERO_DRAW_R1C] == [0] * 5
    assert analysis["zero_draw_agg"] == ZERO_DRAW_R1C
    lines = cpns.format_zero_draw_lines(analysis)
    zd = [ln for ln in lines if ln.startswith("ZERO-DRAW R1C_seed100")]
    assert zd and all(str(k) in zd[0] for k in ZERO_DRAW_R1C)
    assert any(
        ln == f"AGGREGATE ZERO-DRAW: nodes {ZERO_DRAW_R1C}" for ln in lines
    )


def test_template_expectations_come_from_registry():
    """Anti-self-reference seam: headline + centre rate are parsed from the
    registered template string, never produced by the checker itself."""
    assert cpns.parse_template_expectations(TEMPLATE) == (25, 25, 2.00)
