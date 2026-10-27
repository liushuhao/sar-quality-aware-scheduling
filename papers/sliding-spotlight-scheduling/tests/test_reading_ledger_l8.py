#!/usr/bin/env python3
"""Ticket 50 phase 2 -- the L8 reading ledger is GENERATED and traceable.

What these tests defend:
  * every entry carries id / caliber tag / value / source / producer, so a
    number cannot be quoted without its provenance;
  * the cheap half of the ledger reproduces exactly from the artifacts
    (``build(fast=True)``), so a hand-edit or a stale file is caught without
    paying for the five-minute delivered-caliber pass;
  * an infeasible grid point is a STATUS, not a zero -- the distinction the
    figure and the manuscript both depend on;
  * the demand total is a served-instance count, and it is recomputed rather
    than trusted;
  * the retired-world ban list exists in one place, with both halves;
  * the new figure is really on disk and really non-empty (a silent zero-render
    is the failure this pins).

Usage: PYTHONHASHSEED=0 python -B -m pytest \
    papers/sliding-spotlight-scheduling/tests/test_reading_ledger_l8.py -q
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK / "scripts"))

import build_reading_ledger_l8 as lb  # noqa: E402

LEDGER = FORK / "experiments" / "v5_results" / "reading_ledger_l8.json"
FIGURE = FORK / "paper" / "figures" / "fig5_coverage_vs_requirement.pdf"


@pytest.fixture(scope="module")
def doc() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def fast() -> dict:
    return lb.build(fast=True)


def by_id(entries):
    return {e["id"]: e for e in entries}


def test_ledger_exists_and_declares_its_world(doc):
    assert doc["schema"] == "reading-ledger-l8/1.0"
    assert doc["world"] == "L8"
    assert doc["caliber"] == "v5"
    assert doc["n_entries"] == len(doc["entries"])


def test_every_entry_carries_its_provenance(doc):
    for e in doc["entries"]:
        for key in ("id", "value", "unit", "caliber_tag", "source",
                    "produced_by"):
            assert key in e, (e.get("id"), key)
        assert e["source"]["file"], e["id"]
        assert e["source"]["path"], e["id"]


def test_the_two_global_caliber_tags_are_registered_verbatim(doc):
    tags = doc["caliber_tags"]
    assert tags["CAL_TAG_FULFIL"] == lb.CAL_TAG_FULFIL
    assert tags["CAL_TAG_DELIV"] == lb.CAL_TAG_DELIV
    # the obligations that must travel with the readings
    assert "库口径 f_q" in tags["CAL_TAG_FULFIL"]
    assert "tie-set 全体成员均值" in tags["CAL_TAG_FULFIL"]
    assert "非优化目标" in tags["CAL_TAG_FULFIL"]
    assert "描述性变体" in tags["CAL_TAG_DELIV"]
    assert "不可混比" in tags["CAL_TAG_DELIV"]
    assert "STR 无定义域" in tags["CAL_TAG_DELIV"]


def test_fulfillment_entries_carry_the_fulfillment_tag(doc):
    ents = [e for e in doc["entries"] if e["id"].startswith("fulfillment.")]
    assert ents
    for e in ents:
        assert e["caliber_tag"] == lb.CAL_TAG_FULFIL, e["id"]


def test_delivered_caliber_entries_carry_the_delivered_tag(doc):
    ents = [e for e in doc["entries"] if e["id"].startswith("deliv.")]
    assert ents, "the delivered-caliber section did not run"
    for e in ents:
        assert e["caliber_tag"] == lb.CAL_TAG_DELIV, e["id"]


def test_the_cheap_half_of_the_ledger_reproduces(fast, doc):
    """A hand-edit or a stale file is caught without the 5-minute pass."""
    want = {k: v for k, v in by_id(doc["entries"]).items()
            if not k.startswith("deliv.")}
    got = by_id(fast["entries"])
    assert set(got) == set(want), (sorted(set(got) ^ set(want))[:6])
    for k in got:
        assert got[k] == want[k], k


def test_an_infeasible_point_is_a_status_not_a_zero(doc):
    """R1C at s=0.8 must not be quotable as a zero-coverage reading."""
    ents = by_id(doc["entries"])
    status = ents["coverage.status.R1C.s0.8"]["value"]
    assert status == "no_feasible_individual"
    assert ents["coverage.median.R1C.s0.8"]["value"] is None
    assert ents["infeasible.units.R1C.s0.8"]["value"] == 10
    # the value the inherited C-checks consume is kept, but named as such
    assert ents["coverage.curve_entry.R1C.s0.8"]["value"] == 0.0


def test_no_other_point_is_marked_infeasible(doc):
    bad = [e["id"] for e in doc["entries"]
           if e["id"].startswith("infeasible.units.") and e["value"]]
    assert bad == ["infeasible.units.R1C.s0.8"], bad


def test_coverage_cost_is_measured_against_the_familys_own_saturation(doc):
    ents = by_id(doc["entries"])
    # -4.15 pp for R3H and -2.36 pp for R2F are the registered readings
    assert ents["coverage_cost_pp.R3H"]["value"] == pytest.approx(-4.15, abs=0.005)
    assert ents["coverage_cost_pp.R2F"]["value"] == pytest.approx(-2.36, abs=0.005)
    assert "saturation" in ents["coverage_cost.R3H"]["note"]
    for fam in ("R1C", "R2F", "R3H"):
        assert ents[f"coverage_saturation.{fam}"]["value"] is not None


def test_demand_total_is_a_served_instance_count_and_is_recomputed(doc):
    ents = by_id(doc["entries"])
    assert ents["demand.served_task_instances"]["value"] == 477308
    assert "INSTANCE" in ents["demand.served_task_instances"]["note"]
    # recompute independently of the ledger
    total = 0
    for fam in lb.FAMILIES:
        for s in lb.S_GRID:
            for p in sorted((lb.SWEEP / lb.s_name(s)).glob(
                    f"pilot_{fam}_seed*.json")):
                art = json.loads(p.read_text(encoding="utf-8"))
                total += sum(r["n_selected"] for r in art["front"])
    assert total == ents["demand.served_task_instances"]["value"]


def test_the_zero_violation_reading_is_not_written_as_a_count_of_violations(doc):
    e = by_id(doc["entries"])["demand.delivery_identity_cv_max"]
    assert e["value"] == 0.0
    assert "raise" in e["note"]
    assert "Do not quote" in e["note"]


def test_retention_is_mirrored_from_the_gate_test_that_owns_it(doc):
    ents = by_id(doc["entries"])
    assert ents["retention.R1C"]["value"] == 0.5114
    assert ents["retention.R2F"]["value"] == 1.0
    assert ents["retention.R3H"]["value"] == 0.7100
    src = FORK / "tests" / "test_verify_gate.py"
    assert src.is_file()
    assert "retention_expect" in src.read_text(encoding="utf-8")
    for fam in ("R1C", "R2F", "R3H"):
        assert "test_verify_gate" in ents[f"retention.{fam}"]["source"]["file"]


def test_delivered_caliber_reports_its_exclusions(doc):
    total = by_id(doc["entries"])["deliv.domain_totals"]["value"]
    served = by_id(doc["entries"])["demand.served_task_instances"]["value"]
    assert total["defined"] + total["excluded_str"] + total["no_order"] == served
    assert total["excluded_str"] > 0, "STR exclusion must be visible, not zero"
    # R1C is entirely stripmap: the delivered caliber has no domain there
    for s in lb.S_GRID[1:]:
        assert by_id(doc["entries"])[f"deliv.domain.defined.R1C.s{s}"]["value"] == 0
        assert by_id(doc["entries"])[f"deliv.median.R1C.s{s}"]["value"] is None


def test_no_direction_claim_is_registered(doc):
    notes = doc["notes"]
    assert "direction" in notes["falsified_direction_claim"]
    rel = by_id(doc["entries"])["relation.coverage_vs_fulfillment.units"]
    assert rel["value"] > 0, "the measured pooled coefficient is positive"
    assert "no direction claim" in rel["note"]


def test_the_ban_list_has_both_halves(doc):
    bans = doc["manuscript_ban_list"]
    hard = {b["id"] for b in bans["hard_banned"]}
    soft = {b["id"] for b in bans["allowed_with_label"]}
    assert hard == {"old_world_90_units", "pooled_quality_position_3_9722",
                    "pooled_quality_t_24_78", "dq_all_66_872",
                    "promotion_two_axis",
                    "fallback_every_transition_carries",
                    "fallback_bound_as_measurement",
                    "floor_inside_coarse_tier", "dip_different_seeds",
                    "fig3b_two_families_at_issue",
                    "abstract_self_limiting_close", "solver_not_contribution"}
    assert soft == {"l7_tight_arm_0_446", "l7_coverage_cost_5_5pp",
                    "l7_cost_misattributed_1_61pp", "old_retention_84_4",
                    "old_retention_63_7"}
    for b in bans["hard_banned"] + bans["allowed_with_label"]:
        assert b["why"], b["id"]
    assert bans["required_label_regex"]


def test_the_main_figure_is_on_disk_and_not_empty():
    assert FIGURE.is_file(), f"missing figure {FIGURE}"
    blob = FIGURE.read_bytes()
    assert blob[:4] == b"%PDF", "not a PDF"
    assert len(blob) > 10_000, f"suspiciously small figure ({len(blob)} bytes)"
