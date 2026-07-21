"""Tests for gen_ablation_figure.py (TDD) — ablation chart generation."""
import sys
from pathlib import Path
_EXP = Path(__file__).resolve().parent.parent / "experiments"
sys.path.insert(0, str(_EXP))

import pytest
import numpy as np


# Fixture: small variant data mimicking ablation_summary structure
@pytest.fixture
def variant_data():
    """Simulated per-class, per-variant means for testing the plotter."""
    classes = ["S1", "S2", "S3", "S4"]
    variants = ["A", "B", "C", "D"]
    metric_labels = ["f1_degradation_pct", "f2_degradation_pct",
                     "f3_degradation_pct"]
    data = {}
    for cls in classes:
        data[cls] = {}
        for v in variants:
            if v == "A":
                data[cls][v] = {m: 0.0 for m in metric_labels}
            else:
                data[cls][v] = {m: np.random.uniform(-5, 5) for m in metric_labels}
    return data, classes, variants, metric_labels


def test_prepare_bar_data_returns_correct_structure(variant_data):
    """bar_data should have variants as keys and metric arrays."""
    from gen_ablation_figure import prepare_bar_data
    data, classes, variants, metric_labels = variant_data
    bar_data = prepare_bar_data(data, classes, variants, metric_labels)
    assert "B" in bar_data
    assert len(bar_data["B"]["f1_degradation_pct"]) == len(classes)


def test_prepare_bar_data_skips_baseline(variant_data):
    """prepare_bar_data should only include the variants it receives."""
    from gen_ablation_figure import prepare_bar_data
    data, classes, _, _ = variant_data
    # Pass only non-baseline variants
    bar_data = prepare_bar_data(data, classes, ["B", "C", "D"],
                                ["f1_degradation_pct"])
    assert "A" not in bar_data
    assert "B" in bar_data


def test_bar_colors_cover_all_variants(variant_data):
    """Color map should have entries for each non-baseline variant."""
    from gen_ablation_figure import get_bar_colors
    colors = get_bar_colors(["B", "C", "D"])
    assert "B" in colors and "C" in colors and "D" in colors


def test_figure_saved_to_file(tmp_path, variant_data):
    """gen_figure should write a PDF file without error."""
    from gen_ablation_figure import gen_ablation_figure
    data, classes, _, metric_labels = variant_data
    # Pass only non-baseline variants
    out = tmp_path / "test_ablation.pdf"
    gen_ablation_figure(data, classes, ["B", "C", "D"], metric_labels, str(out))
    assert out.exists()
    assert out.stat().st_size > 1000  # at least 1KB
