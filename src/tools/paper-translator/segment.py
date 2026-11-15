import json
from pathlib import Path

SECTION_TYPES = ('\section', '\subsection', '\subsubsection', '\paragraph')


def _is_section_line(line: str) -> bool:
    s = line.strip()
    return any(s.startswith(cmd) for cmd in SECTION_TYPES)


def _extract_section_name(line: str) -> str:
    s = line.strip()
    for cmd in SECTION_TYPES:
        if s.startswith(cmd):
            after = s[len(cmd):]
            if after.startswith('*'):
                after = after[1:]
            if after.startswith('{'):
                end = after.find('}')
                if end != -1:
                    return after[1:end]
    return 'Preamble'


def segment_tex(tex: str) -> list:
    lines = tex.splitlines()
    segments = []
    current_section = 'Preamble'
    buf = []
    env_depth = 0

    def flush():
        nonlocal buf
        if not buf:
            return
        raw = "\n".join(buf).strip()
        if not raw:
            buf = []
            return
        segments.append({
            "id": len(segments) + 1,
            "section": current_section,
            "type": "block",
            "raw": raw,
        })
        buf = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('\begin{'):
            buf.append(line)
            env_depth += stripped.count('\begin{') - stripped.count('\end{')
            continue
        if env_depth > 0:
            buf.append(line)
            env_depth += stripped.count('\begin{') - stripped.count('\end{')
            continue
        if _is_section_line(line):
            flush()
            current_section = _extract_section_name(line)
            buf.append(line)
            continue
        buf.append(line)
    flush()
    return segments


def main():
    import sys
    path = sys.argv[1]
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("tools/paper-translator/output/segments.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tex = Path(path).read_text(encoding='utf-8')
    segs = segment_tex(tex)
    out_path.write_text(json.dumps(segs, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote {len(segs)} segments to {out_path}")


if __name__ == '__main__':
    main()
