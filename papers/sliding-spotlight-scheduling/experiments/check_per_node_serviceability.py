#!/usr/bin/env python3
"""Ticket 52 (G1) -- per-node serviceability checker for the registered dense domain.

Recomputes the paper's per-node serviceability claim from the current artifacts
so it stops depending on the one-time manual verification of eb1b006:

  * C1 definition sentence (paper/main.tex): *every* node in the dense domain
    carries *at least one* in-band transit over the span (printed 25/25).
  * SS5.1 scenario-construction sentence (paper/main.tex): the 25/25 reading is
    a construction-time measurement on the full-span domain; the manifest ledger
    stores aggregate admission counts, not per-node columns.
  * Registered centre-node rate: 2.00 transits/24h
    (experiments/realwindow_scenario_template.json,
    amendment_20261005_ticket25.dense_domain.servability_evidence -- the
    expectation is parsed FROM that registry string, never recomputed back
    from this checker's own output).

WORLD SCOPE: caliber v5 / experiments/v5_results (RUN_LINEAGE node L8).
Constants that are NOT written into the manifests are pinned per world below,
each with its generation-side source, following the per-world pinning idiom of
RUN_LINEAGE.md ("SUPERSEDED" rows): R_KM_PER_DEG_LAT and the longitude scale
formula (sss_core/scenarios.py:114, 530-538), the family/density registry and
the 10-seeds-per-family shape (realwindow_scenario_template.json
amendment_20261005_ticket25.family_registry + seed_rule).

drawn/served semantics (ticket 52, pinned):
  * nodes are reverse-mapped from scenario task lat/lon -- the manifest
    carries no node field;
  * drawn[node] counts drawn-but-removed tasks: the registered assignment rule
    (target i -> node i % 25, row-major) is applied to
    generation_ledger.n_drawn, because removed tasks never reach the tasks
    list (sss_core/scenarios.py:558-560).  Drawn coverage is therefore only a
    LOWER-BOUND proof for served; the checker asserts served <= drawn per node.
  * zero-draw nodes are legal (R1C draws 20 tasks onto 25 nodes) and are
    reported BY NAME, never silently dropped.

Exit code: 0 = green, 1 = red (any failed assertion, missing/drifted input, or
registry parse failure -- printed as FAIL lines, never silent).

Usage (repo root):
    PYTHONPATH=src:papers/sliding-spotlight-scheduling \
      "/d/Program Files/Python/python" \
      papers/sliding-spotlight-scheduling/experiments/check_per_node_serviceability.py
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent          # papers/sliding-spotlight-scheduling
if str(FORK) not in sys.path:
    sys.path.insert(0, str(FORK))

# ── world pinning (caliber v5 / L8) ─────────────────────────────────────────
WORLD = "caliber v5 / experiments/v5_results (RUN_LINEAGE node L8)"
DEFAULT_SCENARIOS_DIR = FORK / "experiments" / "v5_results" / "scenarios"
DEFAULT_PLATFORM = FORK / "experiments" / "v5_results" / "platform.json"
DEFAULT_TEMPLATE = FORK / "experiments" / "realwindow_scenario_template.json"

R_SCHEMA = "scenario-manifest/2.1-realwindow"
# family -> (variant_index, density_n); realwindow_scenario_template.json
# amendment_20261005_ticket25.family_registry (R4H retired by AD-5)
FAMILIES = {"R1C": (1, 20), "R2F": (2, 50), "R3H": (3, 100)}
SEEDS_PER_FAMILY = 10  # seed_rule variant_index*100 + seed_index, seed_index 0..9

# conversion constants NOT in the manifest (sss_core/scenarios.py:114, 530-538)
R_KM_PER_DEG_LAT = 111.32        # [教科书] meridian km per degree
# longitude: deg = km / (R_KM_PER_DEG_LAT * cos(radians(centre_lat)))

ASSIGNMENT_RULE_MARKERS = ("i % 25", "row-major")  # drift tripwire on the rule string

DISCLOSURE = (
    "DISCLOSURE (mirrors paper SS5.1): the manifest generation_ledger stores "
    "aggregate admission counts (n_drawn / n_served / removals), NOT per-node "
    "columns; the per-node drawn/served counts below are reverse-mapped -- "
    "drawn via the registered assignment rule (target i -> node i % 25, "
    "row-major) applied to generation_ledger.n_drawn (so drawn-but-removed "
    "tasks still count as drawn), served via nearest-node reverse map of task "
    "lat/lon (min tie margin reported below)."
)


class CheckerError(RuntimeError):
    """Input/registry level failure -- reported as RED, never silent."""


# ── grid / geometry primitives ───────────────────────────────────────────────

def grid_nodes(centre_lat, centre_lon, grid_n, spacing_km):
    """Node lat/lon BEFORE jitter; mirrors sss_core/scenarios.py:525-538."""
    lon_scale = R_KM_PER_DEG_LAT * math.cos(math.radians(centre_lat))
    nodes = []
    for node in range(grid_n * grid_n):
        gi, gj = divmod(node, grid_n)
        lat = centre_lat + (gi - grid_n // 2) * (spacing_km / R_KM_PER_DEG_LAT)
        lon = centre_lon + (gj - grid_n // 2) * (spacing_km / lon_scale)
        nodes.append((lat, lon))
    return nodes


def _dist_km(lat, lon, node_lat, node_lon, lon_scale):
    """Equirectangular km in the SAME metric the generator scatters in."""
    return math.hypot(
        (lat - node_lat) * R_KM_PER_DEG_LAT, (lon - node_lon) * lon_scale
    )


def nearest_node(lat, lon, nodes, lon_scale):
    """(node_index, tie_margin_km); margin = d(second) - d(nearest)."""
    d1, d2, arg = math.inf, math.inf, -1
    for k, (nlat, nlon) in enumerate(nodes):
        d = _dist_km(lat, lon, nlat, nlon, lon_scale)
        if d < d1:
            d1, d2, arg = d, d1, k
        elif d < d2:
            d2 = d
    return arg, d2 - d1


def centre_node_index(grid_n):
    return (grid_n // 2) * grid_n + grid_n // 2


# ── manifest loading + drawn/served analysis ────────────────────────────────

def _load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_r_manifests(scenarios_dir):
    """All R-family manifests in the directory (schema filter; M-family is
    'scenario-manifest/1.0' and is NOT the dense domain)."""
    scenarios_dir = Path(scenarios_dir)
    if not scenarios_dir.is_dir():
        raise CheckerError(f"scenarios dir missing: {scenarios_dir}")
    out = []
    for path in sorted(scenarios_dir.glob("*.json")):
        doc = _load_json(path)
        if doc.get("schema") == R_SCHEMA:
            out.append((path.name, doc))
    if not out:
        raise CheckerError(
            f"no {R_SCHEMA} manifests in {scenarios_dir} -- silent-empty is "
            "a failure mode, not a pass"
        )
    return out


_GRID_KEYS = (
    "domain_centre_deg", "domain_side_km", "grid_n", "grid_spacing_km",
    "scatter_half_cell_km", "grid_assignment_rule", "span_days",
    "enum_step_s", "gap_merge_s", "incidence_band_deg",
)


def grid_params(manifests, failures):
    """Cross-manifest consistency of the registered grid/enumeration params."""
    ref_name, ref_doc = manifests[0]
    ref = ref_doc["preregistration"]
    for name, doc in manifests[1:]:
        pre = doc["preregistration"]
        for key in _GRID_KEYS:
            if pre.get(key) != ref.get(key):
                failures.append(
                    f"grid param {key!r} drifted: {ref_name}={ref.get(key)!r} "
                    f"vs {name}={pre.get(key)!r}"
                )
    rule = str(ref.get("grid_assignment_rule", ""))
    for marker in ASSIGNMENT_RULE_MARKERS:
        if marker not in rule:
            failures.append(
                f"assignment rule string in {ref_name} lacks {marker!r}: {rule!r}"
            )
    return ref


def generator_drift_failures(ref):
    """Manifest-registered params vs the CURRENT generator constants: if the
    generator moved without a v5 rerun, this checker must go red (route-H
    inferred-vs-explicit drift guard, B leg)."""
    import sss_core.scenarios as S

    pairs = [
        ("grid_n", ref["grid_n"], S.R_GRID_N),
        ("grid_spacing_km", ref["grid_spacing_km"], S.R_GRID_SPACING_KM),
        ("scatter_half_cell_km", ref["scatter_half_cell_km"], S.R_SCATTER_HALF_CELL_KM),
        ("domain_centre_deg", ref["domain_centre_deg"], list(S.R_DOMAIN_CENTRE_DEG)),
        ("domain_side_km", ref["domain_side_km"], S.R_DOMAIN_SIDE_KM),
        ("span_days", ref["span_days"], S.R_SPAN_DAYS),
        ("enum_step_s", ref["enum_step_s"], S.R_ENUM_STEP_S),
        ("gap_merge_s", ref["gap_merge_s"], S.R_GAP_MERGE_S),
        ("incidence_band_deg", ref["incidence_band_deg"], list(S.R_INCIDENCE_BAND_DEG)),
    ]
    return [
        f"generator drift: manifest {key}={man!r} vs sss_core {gen!r}"
        for key, man, gen in pairs if man != gen
    ]


def world_shape_failures(manifests):
    """v5 world pinning: exactly the 3 registered families x 10 seeds with the
    registered densities (template family_registry + seed_rule)."""
    failures = []
    by_family = {}
    for name, doc in manifests:
        m = re.fullmatch(r"(R\d[A-Z])_seed(\d+)", Path(name).stem)
        if not m:
            failures.append(f"unregistered manifest name shape: {name}")
            continue
        fam, seed = m.group(1), int(m.group(2))
        by_family.setdefault(fam, []).append(seed)
        sc = doc["scenario"]
        if sc.get("family_code") != fam:
            failures.append(f"{name}: family_code {sc.get('family_code')!r} != filename")
        if fam in FAMILIES:
            variant, density = FAMILIES[fam]
            if sc.get("density_n_targets") != density:
                failures.append(
                    f"{name}: density {sc.get('density_n_targets')} != registered {density}"
                )
            lo = variant * 100
            if not lo <= seed < lo + SEEDS_PER_FAMILY:
                failures.append(f"{name}: seed {seed} outside [{lo}, {lo + SEEDS_PER_FAMILY})")
    if sorted(by_family) != sorted(FAMILIES):
        failures.append(
            f"families present {sorted(by_family)} != registered {sorted(FAMILIES)}"
        )
    for fam, seeds in by_family.items():
        if len(seeds) != SEEDS_PER_FAMILY or len(set(seeds)) != len(seeds):
            failures.append(
                f"{fam}: {len(seeds)} manifests ({len(set(seeds))} distinct seeds), "
                f"registered {SEEDS_PER_FAMILY} per family"
            )
    return failures


def analyze_manifests(manifests):
    """Per-scenario and aggregate per-node drawn/served + tie-margin audit.

    drawn: registered rule (target i -> node i % 25) applied to n_drawn --
    counts drawn-but-removed tasks (they never reach the tasks list).
    served: nearest-node reverse map of each task's lat/lon.
    """
    ref = manifests[0][1]["preregistration"]
    grid_n = ref["grid_n"]
    n_nodes = grid_n * grid_n
    centre = ref["domain_centre_deg"]
    lon_scale = R_KM_PER_DEG_LAT * math.cos(math.radians(centre[0]))
    nodes = grid_nodes(centre[0], centre[1], grid_n, ref["grid_spacing_km"])

    failures = []
    per_scenario = {}
    agg_drawn = [0] * n_nodes
    agg_served = [0] * n_nodes
    min_margin = (math.inf, None)  # (km, scenario)
    for name, doc in manifests:
        led = doc["generation_ledger"]
        tasks = doc["tasks"]
        n_drawn, n_served = led["n_drawn"], led["n_served"]
        removals = led["removals"]
        if sum(removals.values()) + n_served != n_drawn:
            failures.append(
                f"{name}: ledger rule broken: sum(removals)={sum(removals.values())} "
                f"+ n_served={n_served} != n_drawn={n_drawn}"
            )
        if n_served != len(tasks):
            failures.append(f"{name}: n_served={n_served} != len(tasks)={len(tasks)}")
        drawn = [0] * n_nodes
        for i in range(n_drawn):
            drawn[i % n_nodes] += 1
        served = [0] * n_nodes
        for t in tasks:
            node, margin = nearest_node(t["lat_deg"], t["lon_deg"], nodes, lon_scale)
            if margin < min_margin[0]:
                min_margin = (margin, name)
            if margin <= 0.0:
                failures.append(
                    f"{name}: task at ({t['lat_deg']}, {t['lon_deg']}) has "
                    f"non-positive tie margin {margin:.4f} km -- B-leg reverse "
                    "map is dead, recompute leg must be re-adjudicated"
                )
            served[node] += 1
        for k in range(n_nodes):
            if served[k] > drawn[k]:
                failures.append(
                    f"{name}: node {k} served {served[k]} > drawn {drawn[k]} "
                    "(drawn coverage is the lower-bound proof for served)"
                )
        zero_draw = [k for k in range(n_nodes) if drawn[k] == 0]
        per_scenario[name] = {
            "drawn": drawn, "served": served, "zero_draw": zero_draw,
            "n_drawn": n_drawn, "n_served": n_served,
        }
        for k in range(n_nodes):
            agg_drawn[k] += drawn[k]
            agg_served[k] += served[k]
    return {
        "nodes": nodes, "grid_n": grid_n, "n_nodes": n_nodes,
        "per_scenario": per_scenario,
        "agg_drawn": agg_drawn, "agg_served": agg_served,
        "zero_draw_agg": [k for k in range(n_nodes) if agg_drawn[k] == 0],
        "min_margin_km": min_margin[0], "min_margin_scenario": min_margin[1],
        "failures": failures,
    }


def format_zero_draw_lines(analysis):
    """Zero-draw nodes, BY NAME, per scenario (never silently dropped)."""
    lines = []
    for name in sorted(analysis["per_scenario"]):
        zd = analysis["per_scenario"][name]["zero_draw"]
        if zd:
            lines.append(
                f"ZERO-DRAW {name}: nodes {zd} (drawn=0; legal -- density "
                f"{analysis['per_scenario'][name]['n_drawn']} < "
                f"{analysis['n_nodes']} nodes; still transit-checked below)"
            )
    if not lines:
        lines.append("ZERO-DRAW: none in any scenario")
    zagg = analysis["zero_draw_agg"]
    lines.append(
        "AGGREGATE ZERO-DRAW: " + (f"nodes {zagg}" if zagg else "none")
    )
    return lines


# ── registered expectations (registry face, NOT this checker's output) ──────

def parse_template_expectations(template_path):
    """(nodes_with_transit, total_nodes, centre_rate_per_24h) parsed from the
    registry string (realwindow_scenario_template.json
    amendment_20261005_ticket25.dense_domain.servability_evidence)."""
    try:
        ev = _load_json(template_path)["amendment_20261005_ticket25"]["dense_domain"][
            "servability_evidence"
        ]
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise CheckerError(f"registry template unreadable: {exc}") from exc
    m = re.search(r"(\d+)/(\d+) nodes carry >=1 in-band transit", ev)
    if not m:
        raise CheckerError(
            f"registry servability_evidence no longer carries the 'N/N nodes' "
            f"claim: {ev!r}"
        )
    c = re.search(r"centre node ([0-9]+(?:\.[0-9]+)?) transits/24h", ev)
    if not c:
        raise CheckerError(
            f"registry servability_evidence no longer carries the centre-node "
            f"rate: {ev!r}"
        )
    return int(m.group(1)), int(m.group(2)), float(c.group(1))


# ── geometric transit enumeration (the generation code path, reused verbatim) ─

def compute_node_transit_counts(platform_path, nodes, *, span_days, step_s,
                                gap_merge_s, band_deg):
    """In-band transit count per node over the span, re-enumerated with the
    registered orbit and the generation-side enumeration function
    (sss_core.scenarios._ground_track_passes, AD-2).  Module-level seam so the
    red-proof fixture can simulate an erased node (transit counts are a
    geometric recompute, not an editable stored artifact)."""
    import numpy as np

    import sss_core.scenarios as S
    from sss_core.realwindows import GroundTarget, KeplerianElement

    spec = _load_json(platform_path)
    epoch = datetime.fromisoformat(spec["epoch"])
    elements = KeplerianElement(  # mirror scripts/run_matrix.py:270-283
        semi_major_axis=float(spec["semi_major_axis_m"]),
        eccentricity=float(spec["eccentricity"]),
        inclination=math.radians(float(spec["inclination_deg"])),
        raan=math.radians(float(spec["raan_deg"])),
        arg_perigee=math.radians(float(spec["arg_perigee_deg"])),
        true_anomaly=math.radians(float(spec["true_anomaly_deg"])),
        epoch=epoch,
    )
    span_s = span_days * 86400.0
    # shared coarse track, one _ecef_track pass for ALL nodes (scenarios.py:522)
    times = np.arange(0.0, span_s + 0.5 * step_s, step_s)
    pos, _vel = S._ecef_track(elements, epoch, times)
    counts = {}
    for k, (lat, lon) in enumerate(nodes):
        target = GroundTarget(target_id=f"node{k}", lat=lat, lon=lon)
        passes = S._ground_track_passes(
            elements, epoch, target, times, pos,
            tuple(float(b) for b in band_deg), float(step_s), float(gap_merge_s),
        )
        counts[k] = len(passes)
    return counts


# ── main ─────────────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scenarios-dir", default=str(DEFAULT_SCENARIOS_DIR))
    ap.add_argument("--platform", default=str(DEFAULT_PLATFORM))
    ap.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    args = ap.parse_args(argv)

    print(f"WORLD: {WORLD}")
    print(f"constants pinned per world: R_KM_PER_DEG_LAT={R_KM_PER_DEG_LAT} "
          "(sss_core/scenarios.py:114); lon deg = km / (111.32 * "
          "cos(centre_lat)) (scenarios.py:530-538)")
    try:
        manifests = load_r_manifests(args.scenarios_dir)
        exp_ok, exp_total, exp_centre_rate = parse_template_expectations(args.template)

        failures = world_shape_failures(manifests)
        ref = grid_params(manifests, failures)
        failures += generator_drift_failures(ref)
        analysis = analyze_manifests(manifests)
        failures += analysis["failures"]

        grid_n = analysis["grid_n"]
        n_nodes = analysis["n_nodes"]
        centre_idx = centre_node_index(grid_n)
        span_days = float(ref["span_days"])

        counts = compute_node_transit_counts(
            args.platform, analysis["nodes"],
            span_days=span_days, step_s=float(ref["enum_step_s"]),
            gap_merge_s=float(ref["gap_merge_s"]),
            band_deg=ref["incidence_band_deg"],
        )

        n_ok = sum(1 for k in range(n_nodes) if counts.get(k, 0) >= 1)
        zero_transit = [k for k in range(n_nodes) if counts.get(k, 0) < 1]
        if zero_transit:
            failures.append(
                f"nodes with ZERO in-band transits over the span: {zero_transit}"
            )
        if n_ok != exp_ok or n_nodes != exp_total:
            failures.append(
                f"headline mismatch: recomputed {n_ok}/{n_nodes} vs registered "
                f"{exp_ok}/{exp_total}"
            )
        centre_rate = counts.get(centre_idx, 0) / span_days
        if round(centre_rate, 2) != round(exp_centre_rate, 2):
            failures.append(
                f"centre node {centre_idx} rate {centre_rate:.2f} transits/24h "
                f"!= registered {exp_centre_rate:.2f}"
            )

        # ── report ──
        print(DISCLOSURE)
        print(
            f"grid: centre {tuple(ref['domain_centre_deg'])}, {grid_n}x{grid_n}, "
            f"spacing {ref['grid_spacing_km']} km, jitter half-cell "
            f"{ref['scatter_half_cell_km']} km, span {span_days} d, band "
            f"{tuple(ref['incidence_band_deg'])} deg "
            "(manifest preregistration, all manifests consistent)"
        )
        for line in format_zero_draw_lines(analysis):
            print(line)
        print(
            f"min tie margin: {analysis['min_margin_km']:.2f} km "
            f"({analysis['min_margin_scenario']}) [guard: > 0]"
        )
        print(
            "node  cell    lat_deg   lon_deg  drawn  served  transits  per_24h"
        )
        for k in range(n_nodes):
            gi, gj = divmod(k, grid_n)
            lat, lon = analysis["nodes"][k]
            print(
                f"{k:>4}  ({gi},{gj})  {lat:8.4f}  {lon:8.4f}  "
                f"{analysis['agg_drawn'][k]:>5}  {analysis['agg_served'][k]:>6}  "
                f"{counts.get(k, 0):>8}  {counts.get(k, 0) / span_days:>7.2f}"
            )
        print(
            f"HEADLINE: {n_ok}/{n_nodes} nodes carry >=1 in-band transit over "
            f"{span_days * 24:.0f} h (registered {exp_ok}/{exp_total})"
        )
        print(
            f"CENTRE node {centre_idx}: {counts.get(centre_idx, 0)} transits over "
            f"{span_days} d = {centre_rate:.2f} transits/24h "
            f"(registered {exp_centre_rate:.2f} -- realwindow_scenario_template.json "
            "amendment_20261005_ticket25.dense_domain.servability_evidence)"
        )
    except CheckerError as exc:
        print(f"FAIL: {exc}")
        print("VERDICT: RED")
        return 1
    except Exception as exc:  # never silent
        import traceback

        traceback.print_exc()
        print(f"FAIL: unexpected {type(exc).__name__}: {exc}")
        print("VERDICT: RED")
        return 1

    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        print(f"VERDICT: RED ({len(failures)} failure(s))")
        return 1
    print("VERDICT: GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
