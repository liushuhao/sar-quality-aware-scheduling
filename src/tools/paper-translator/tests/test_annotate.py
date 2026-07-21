from pathlib import Path

from annotate import build_comparison


def test_annotate_builds_comparison(tmp_path):
    segs = [
        {"id": 1, "section": "Abstract", "raw": "Hello world.", "text_for_translation": "Hello world ."}
    ]
    trans = [
        {"id": 1, "section": "Abstract", "translation": "你好世界。"}
    ]
    out = tmp_path / "comparison.md"
    build_comparison(segs, trans, out)
    content = out.read_text(encoding='utf-8')
    assert "Hello world." in content
    assert "你好世界。" in content
    assert "your_annotation" in content
