from pathlib import Path

from segment import segment_tex


def _parse_annotations(comparison_md: str) -> dict:
    lines = comparison_md.strip().splitlines()
    header = None
    idx_col = None
    ann_col = None
    rev: dict[int, dict] = {}

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells:
            continue
        if header is None:
            header = [c.lower() for c in cells]
            for i, h in enumerate(header):
                if h == "id":
                    idx_col = i
                elif "annotation" in h:
                    ann_col = i
            continue
        try:
            seg_id = int(cells[idx_col])
        except (TypeError, ValueError, IndexError):
            continue
        ann = (cells[ann_col] if ann_col < len(cells) else "").strip()
        rev[seg_id] = {"raw_annotation": ann}

    return rev


def apply_revisions(orig_tex: str, comparison_md: str, out_path: Path):
    seg_map = {s["id"]: s for s in segment_tex(orig_tex)}
    ann = _parse_annotations(comparison_md)
    out = []
    warnings = []

    for seg in seg_map.values():
        seg_id = seg["id"]
        entry = ann.get(seg_id, {})
        text = entry.get("raw_annotation", "").strip()

        if text.startswith("replace:"):
            mapping = text[len("replace:"):].strip()
            if "->" in mapping:
                old, new = mapping.split("->", 1)
                old = old.strip()
                new = new.strip()
                if old and old in seg["raw"]:
                    out.append(seg["raw"].replace(old, new, 1))
                    continue
                warnings.append(f"seg {seg_id}: `old` not found")
        elif text == "delete":
            continue
        elif text.startswith("insert:"):
            inserted = text[len("insert:"):].strip()
            out.append(inserted + "\n" + seg["raw"])
            continue

        out.append(seg["raw"])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(out), encoding="utf-8")
    if warnings:
        warn_path = out_path.with_suffix(".revised.warnings.txt")
        warn_path.write_text("\n".join(warnings), encoding="utf-8")
    return warnings


def main():
    import sys
    orig_path = Path(sys.argv[1])
    comp_path = Path(sys.argv[2])
    out_path = Path(sys.argv[3]) if len(sys.argv) > 3 else orig_path.with_suffix(".revised.tex")
    orig = orig_path.read_text(encoding='utf-8')
    comp = comp_path.read_text(encoding='utf-8')
    apply_revisions(orig, comp, out_path)
    print(f"Wrote revised paper to {out_path}")


if __name__ == '__main__':
    main()
