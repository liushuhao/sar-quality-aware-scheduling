import json
from pathlib import Path


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def build_comparison(segments: list, translations: list, out_path: Path):
    trans_map = {t["id"]: t.get("translation", "") for t in translations}
    lines = [
        "# Paper Review Comparison",
        "",
        "| id | section | english_raw | chinese_translation | your_annotation |",
        "|-----|---------|-------------|---------------------|-----------------|",
    ]
    for seg in segments:
        tid = seg["id"]
        zh = trans_map.get(tid, "")
        lines.append(
            f"| {tid} | {_md_cell(seg['section'])} | {_md_cell(seg['raw'])} | {_md_cell(zh)} |  |"
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding='utf-8')


def main():
    import sys
    seg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tools/paper-translator/output/segments.json")
    trans_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("tools/paper-translator/output/translations.json")
    out_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("tools/paper-translator/output/comparison.md")
    segs = json.loads(seg_path.read_text(encoding='utf-8'))
    trans = json.loads(trans_path.read_text(encoding='utf-8'))
    build_comparison(segs, trans, out_path)
    print(f"Wrote comparison to {out_path}")


if __name__ == '__main__':
    main()
