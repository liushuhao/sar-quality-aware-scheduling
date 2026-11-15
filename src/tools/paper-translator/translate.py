import json
from pathlib import Path

from segment import segment_tex


def build_translations(segments: list, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = []
    for seg in segments:
        payload.append(
            {
                "id": seg["id"],
                "section": seg["section"],
                "english_raw": seg["raw"],
                "chinese_translation": "",
                "your_annotation": "",
            }
        )
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def main() -> None:
    import sys

    tex_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("papers/single-sat-quality/small-paper-ijae.tex")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("tools/paper-translator/output/translations.json")

    tex = tex_path.read_text(encoding="utf-8")
    segments = segment_tex(tex)
    build_translations(segments, out_path)
    print(f"Wrote {len(segments)} translation entries to {out_path}")


if __name__ == "__main__":
    main()
