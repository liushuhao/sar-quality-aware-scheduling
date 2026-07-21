"""Tests for ablation_report.py — Markdown/CSV report generation (TDD)."""
import json
import math
import sys
from pathlib import Path

_EXPERIMENTS_DIR = Path(__file__).resolve().parent.parent / "experiments"
if str(_EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_EXPERIMENTS_DIR))

import pytest


# ─── Fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def sample_table():
    """Pre-computed compare_variants output for testing the renderer."""
    return {
        "S1": {
            "A": {
                "f1_raw_mean": 300.0, "f1_raw_std": 50.0,
                "f1_per_task_mean": 30.0, "f1_per_task_std": 5.0,
                "f2_mean": 0.572, "f2_std": 0.05,
                "f3_mean": 0.053, "f3_std": 0.10,
                "n_selected_mean": 10.0, "n_selected_std": 2.0,
                "n_scenarios": 50,
            },
            "B": {
                "f1_raw_mean": 76.6, "f1_raw_std": 30.0,
                "f1_per_task_mean": 5.89, "f1_per_task_std": 2.0,
                "f2_mean": 0.565, "f2_std": 0.05,
                "f3_mean": 0.273, "f3_std": 0.14,
                "n_selected_mean": 13.0, "n_selected_std": 5.0,
                "n_scenarios": 50,
                "f1_raw_degradation_pct": 74.47,
                "f1_raw_pvalue": 1e-30,
                "f2_degradation_pct": 1.22,
                "f2_pvalue": 0.42,
                "f3_degradation_pct": -415.0,  # B is higher → "negative" degradation
                "f3_pvalue": 0.001,
            },
        },
    }


# ─── Tests for format_value() ──────────────────────────────────────────

def test_format_value_for_means():
    """Means should be formatted with 4 decimals by default."""
    from ablation_report import format_value
    assert format_value(0.5720, "f2_mean") == "0.5720"
    assert format_value(300.0, "f1_raw_mean") == "300.0000"


def test_format_value_for_percentages():
    """Degradation percentages should be formatted with 1 decimal + % sign."""
    from ablation_report import format_value
    assert format_value(74.47, "f1_raw_degradation_pct") == "74.5%"
    assert format_value(-20.0, "f2_degradation_pct") == "-20.0%"


def test_format_value_for_pvalues():
    """P-values should use scientific notation."""
    from ablation_report import format_value
    assert format_value(0.0001, "f1_raw_pvalue") == "1.0e-04"
    assert format_value(0.42, "f2_pvalue") == "4.2e-01"


def test_format_value_handles_missing():
    """Missing values should render as em-dash."""
    from ablation_report import format_value
    assert format_value(None, "f1_raw_pvalue") == "—"
    assert format_value(float("nan"), "f1_raw_pvalue") == "—"


# ─── Tests for render_markdown() ───────────────────────────────────────

def test_render_markdown_returns_string(sample_table):
    """render_markdown should return a non-empty string."""
    from ablation_report import render_markdown
    md = render_markdown(sample_table)
    assert isinstance(md, str)
    assert len(md) > 100


def test_render_markdown_contains_baseline_column(sample_table):
    """Markdown table should have a column for variant A (baseline)."""
    from ablation_report import render_markdown
    md = render_markdown(sample_table)
    # Should mention A's value or label
    assert "A" in md or "baseline" in md or "full" in md


def test_render_markdown_contains_degradation(sample_table):
    """Markdown should show degradation percentages for non-A variants."""
    from ablation_report import render_markdown
    md = render_markdown(sample_table)
    # Should show 74.5% (B's f1_raw degradation)
    assert "74.5%" in md


def test_render_markdown_handles_empty_table():
    """Empty input should produce a meaningful message, not crash."""
    from ablation_report import render_markdown
    md = render_markdown({})
    assert isinstance(md, str)
    assert len(md) > 0


def test_render_markdown_includes_header_section(sample_table):
    """Markdown should have a section header."""
    from ablation_report import render_markdown
    md = render_markdown(sample_table)
    # Look for some structural marker
    assert any(marker in md.lower() for marker in ["# ", "##", "ablation", "summary"])


# ─── Tests for save_report() ───────────────────────────────────────────

def test_save_report_writes_file(tmp_path, sample_table):
    """save_report should write markdown to a file."""
    from ablation_report import save_report
    out = tmp_path / "report.md"
    save_report(sample_table, str(out))
    assert out.exists()
    content = out.read_text()
    assert len(content) > 0
    assert "74.5%" in content
