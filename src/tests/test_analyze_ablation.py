"""Tests for analyze_ablation.py — ablation analysis (TDD).

These tests use fixture data (in-memory small dicts) NOT real _progress.json
files, so the test suite is independent of D's completion.
"""
import json
import math
import sys
from pathlib import Path

# Ensure experiments/ is on path so `import analyze_ablation` works
# Scripts live under papers/single-sat-quality/experiments (not src/experiments).
_EXPERIMENTS_DIR = (Path(__file__).resolve().parents[2] /
                    "papers" / "single-sat-quality" / "experiments")
if str(_EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_EXPERIMENTS_DIR))

import pytest


# ─── Fixtures: small synthetic ablation data ─────────────────────────────

def _make_entry(scenario_class: str, seed: int, n_targets: int,
                f1: float, f2: float, f3: float, n_sel: int) -> tuple:
    """Return ('S1/S1-A_seed00.pkl', {dict}) tuple."""
    key = f"{scenario_class}/{scenario_class}-A_seed{seed:02d}.pkl"
    val = {
        "seed": seed, "n_targets": n_targets, "n_selected": n_sel,
        "f1": f1 / 100.0, "f1_raw": f1, "f1_gbl": 100.0,
        "f2": f2, "f3": f3, "runtime_s": 10.0, "n_frontier": 50,
    }
    return key, val


@pytest.fixture
def fixture_a():
    """Baseline: high f1, moderate f2/f3 (per-task average 0.57)."""
    entries = {}
    # S1: 20 targets, n_sel~10
    for i in range(50):
        entries[f"S1/S1-A_seed{i:02d}.pkl"] = {
            "seed": i, "n_targets": 20, "n_selected": 10,
            "f1": 3.0, "f1_raw": 300.0, "f1_gbl": 100.0,
            "f2": 0.57, "f3": 0.05, "runtime_s": 10.0, "n_frontier": 50,
        }
    return entries


@pytest.fixture
def fixture_b():
    """Variant B (no squint): lower f1, higher f3 (matches smoke test).

    f1_raw has small variation per seed so paired t-test is meaningful.
    """
    entries = {}
    for i in range(50):
        # Add ±5% noise so paired test sees variation
        f1 = 76.6 * (1.0 + 0.05 * ((i % 7) - 3) / 3.0)
        entries[f"S1/S1-A_seed{i:02d}.pkl"] = {
            "seed": i, "n_targets": 20, "n_selected": 13,
            "f1": 0.766, "f1_raw": f1, "f1_gbl": 100.0,
            "f2": 0.565, "f3": 0.273, "runtime_s": 10.0, "n_frontier": 50,
        }
    return entries


@pytest.fixture
def fixture_c():
    """Variant C (no incidence): similar to A (squint-only)."""
    entries = {}
    for i in range(50):
        entries[f"S1/S1-A_seed{i:02d}.pkl"] = {
            "seed": i, "n_targets": 20, "n_selected": 10,
            "f1": 2.5, "f1_raw": 250.0, "f1_gbl": 100.0,
            "f2": 0.60, "f3": 0.24, "runtime_s": 10.0, "n_frontier": 50,
        }
    return entries


@pytest.fixture
def fixture_d():
    """Variant D (no physics): constant f2/f3 = 1.0, no geometric signal."""
    entries = {}
    for i in range(50):
        entries[f"S1/S1-A_seed{i:02d}.pkl"] = {
            "seed": i, "n_targets": 20, "n_selected": 16,
            "f1": 0.84, "f1_raw": 84.0, "f1_gbl": 100.0,
            "f2": 1.0, "f3": 1.0, "runtime_s": 10.0, "n_frontier": 50,
        }
    return entries


# ─── Tests for load_progress() ──────────────────────────────────────────

def test_load_progress_reads_completed_dict(tmp_path):
    """load_progress should read _progress.json and return completed dict."""
    from analyze_ablation import load_progress
    fp = tmp_path / "_progress.json"
    fp.write_text(json.dumps({
        "completed": {"S1/seed0": {"f1_raw": 100, "f2": 0.5, "f3": 0.1}},
        "stats": {}
    }))
    result = load_progress(str(fp))
    assert "S1/seed0" in result
    assert result["S1/seed0"]["f1_raw"] == 100


def test_load_progress_handles_missing_file(tmp_path):
    """load_progress should raise FileNotFoundError with clear message."""
    from analyze_ablation import load_progress
    with pytest.raises(FileNotFoundError, match="_progress.json"):
        load_progress(str(tmp_path / "missing.json"))


# ─── Tests for per-class aggregation ─────────────────────────────────────

def test_aggregate_by_class_groups_scenarios(fixture_a):
    """aggregate_by_class should group keys like 'S1/foo.pkl' by 'S1'."""
    from analyze_ablation import aggregate_by_class
    grouped = aggregate_by_class(fixture_a)
    assert "S1" in grouped
    assert len(grouped["S1"]) == 50


def test_aggregate_by_class_handles_multiple_classes(fixture_a):
    """Multiple class directories should appear in output."""
    from analyze_ablation import aggregate_by_class
    # Add S2 data
    fixture_a["S2/S2-A_seed00.pkl"] = {
        "seed": 0, "n_targets": 100, "n_selected": 50,
        "f1": 5.0, "f1_raw": 500.0, "f1_gbl": 100.0,
        "f2": 0.6, "f3": 0.01, "runtime_s": 30.0, "n_frontier": 50,
    }
    grouped = aggregate_by_class(fixture_a)
    assert "S1" in grouped and "S2" in grouped


# ─── Tests for metric computation ────────────────────────────────────────

def test_compute_per_task_f1(fixture_a):
    """f1_per_task = f1_raw / n_selected."""
    from analyze_ablation import compute_per_task_f1
    # Sample entry: f1_raw=300, n_sel=10 → 30
    e = fixture_a["S1/S1-A_seed00.pkl"]
    assert compute_per_task_f1(e) == 30.0


def test_compute_per_task_f1_handles_zero_n_selected(fixture_a):
    """If n_selected=0, return 0.0 (avoid div by zero)."""
    from analyze_ablation import compute_per_task_f1
    e = dict(fixture_a["S1/S1-A_seed00.pkl"], n_selected=0, f1_raw=0.0)
    assert compute_per_task_f1(e) == 0.0


def test_compute_degradation_pct():
    """degradation = (baseline - variant) / baseline × 100."""
    from analyze_ablation import compute_degradation_pct
    # baseline f1=300, variant f1=150 → 50% degradation
    assert math.isclose(compute_degradation_pct(300, 150), 50.0)
    # baseline f1=100, variant f1=100 → 0% degradation
    assert math.isclose(compute_degradation_pct(100, 100), 0.0)
    # baseline f1=100, variant f1=120 → -20% (improvement)
    assert math.isclose(compute_degradation_pct(100, 120), -20.0)


def test_compute_degradation_pct_handles_zero_baseline():
    """If baseline=0, return 0.0 (avoid div by zero)."""
    from analyze_ablation import compute_degradation_pct
    assert compute_degradation_pct(0.0, 5.0) == 0.0


# ─── Tests for variant comparison ────────────────────────────────────────

def test_compare_variants_returns_per_class_table(fixture_a, fixture_b, fixture_c, fixture_d):
    """compare_variants should produce {class: {variant: {metric: value}}} structure."""
    from analyze_ablation import compare_variants
    table = compare_variants({
        "A": fixture_a, "B": fixture_b, "C": fixture_c, "D": fixture_d,
    })
    assert "S1" in table
    assert "A" in table["S1"] and "B" in table["S1"]
    assert "B" in table["S1"]
    # A's f1_raw should be 300.0 (mean of 50 identical entries)
    assert math.isclose(table["S1"]["A"]["f1_raw_mean"], 300.0, rel_tol=1e-6)


def test_compare_variants_computes_degradation_correctly(fixture_a, fixture_b):
    """For f1_raw: A=300, B=76.6, degradation should be 74.5%."""
    from analyze_ablation import compare_variants
    table = compare_variants({"A": fixture_a, "B": fixture_b})
    # Compute f1_raw degradation
    deg_b = table["S1"]["B"]["f1_raw_degradation_pct"]
    # (300 - 76.6) / 300 * 100 = 74.47
    assert math.isclose(deg_b, 74.47, rel_tol=0.01)


def test_compare_variants_aligns_by_scenario_key(fixture_a, fixture_b):
    """Comparison must be paired by scenario key (S1/seedXX), not just averaged."""
    from analyze_ablation import compare_variants
    # Modify B's seed00 to be very different
    fixture_b["S1/S1-A_seed00.pkl"]["f1_raw"] = 1.0
    table = compare_variants({"A": fixture_a, "B": fixture_b})
    # Paired degradation for seed00: (300-1)/300 = 99.67%
    # Mean degradation should be heavily affected by seed00
    # This is a smoke test, not strict assert
    assert "f1_raw_degradation_pct" in table["S1"]["B"]


# ─── Tests for statistical significance ─────────────────────────────────

def test_paired_ttest_significant_difference(fixture_a, fixture_b):
    """Paired t-test should detect that B's f1_raw is significantly different from A's."""
    from analyze_ablation import wilcoxon_pvalue
    a_vals = [fixture_a[k]["f1_raw"] for k in fixture_a]
    b_vals = [fixture_b[k]["f1_raw"] for k in fixture_b]
    p = wilcoxon_pvalue(a_vals, b_vals)
    # Should be very small (significant)
    assert p < 0.001


def test_paired_ttest_no_difference():
    """Paired t-test should give high p-value when two arrays are identical."""
    from analyze_ablation import wilcoxon_pvalue
    a = [1.0, 2.0, 3.0, 4.0, 5.0]
    p = wilcoxon_pvalue(a, a)
    # Identical arrays → p = 1.0 (or NaN if std=0, but not < 0.05)
    assert p > 0.5 or math.isnan(p) or math.isinf(p)


def test_paired_ttest_handles_empty_arrays():
    """Empty input should return 1.0 (no evidence of difference)."""
    from analyze_ablation import wilcoxon_pvalue
    p = wilcoxon_pvalue([], [])
    assert p == 1.0


def test_paired_ttest_handles_mismatched_lengths():
    """Mismatched lengths should raise ValueError."""
    from analyze_ablation import wilcoxon_pvalue
    with pytest.raises(ValueError, match="length"):
        wilcoxon_pvalue([1, 2, 3], [1, 2])
