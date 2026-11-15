from pathlib import Path

from translate import build_translations


def _write_segments(tmp_path: Path, segments) -> Path:
    p = tmp_path / "segments.json"
    import json

    p.write_text(json.dumps(segments, ensure_ascii=False), encoding="utf-8")
    return p


def test_build_translations_writes_expected_fields(tmp_path):
    segs = [
        {"id": 1, "section": "Intro", "raw": "Hello."},
        {"id": 2, "section": "Method", "raw": "World."},
    ]
    seg_path = _write_segments(tmp_path, segs)
    out_path = tmp_path / "translations.json"

    result = build_translations(
        __import__("json").loads(seg_path.read_text(encoding="utf-8")), out_path
    )

    assert result == out_path
    data = __import__("json").loads(out_path.read_text(encoding="utf-8"))
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[0]["section"] == "Intro"
    assert data[0]["english_raw"] == "Hello."
    assert data[0]["chinese_translation"] == ""
    assert data[0]["your_annotation"] == ""


def test_build_translations_creates_parent_dirs(tmp_path):
    segs = [{"id": 1, "section": "X", "raw": "T"}]
    seg_path = _write_segments(tmp_path, segs)
    out_path = tmp_path / "nested" / "out" / "translations.json"

    build_translations(
        __import__("json").loads(seg_path.read_text(encoding="utf-8")), out_path
    )
    assert out_path.exists()
