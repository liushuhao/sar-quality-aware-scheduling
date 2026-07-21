from pathlib import Path

from merge import apply_revisions


def test_merge_applies_annotation(tmp_path):
    orig = r"\section{Intro}\nOriginal text.\n\section{Method}\nMethod text."
    comparison = """# Paper Review Comparison
| id | section | english_raw | chinese_translation | your_annotation |
|-----|---------|-------------|---------------------|-----------------|
| 1 | Intro | Original text. | 原始文本。 | replace: Original text. -> Revised text. |
| 2 | Method | Method text. | 方法文本。 |  |
"""
    out = tmp_path / "paper.revised.tex"
    apply_revisions(orig, comparison, out)
    content = out.read_text(encoding='utf-8')
    assert "Revised text." in content
    assert "Original text." not in content
    assert r"\section{Method}" in content
