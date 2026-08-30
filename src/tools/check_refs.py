import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent  # repository root
PAPER = PROJECT / "papers" / "single-sat-quality"
main = PAPER / "small-paper-ijae.tex"

def read_with_inputs(tex_path: Path) -> str:
    """Read tex, expanding \\input{...} (relative to the file's directory)."""
    text = tex_path.read_text(encoding="utf-8")
    out = []
    for line in text.splitlines(keepends=True):
        m = re.search(r"\\input\{([^}]+)\}", line)
        if m:
            inc = m.group(1)
            inc_path = (tex_path.parent / inc)
            if not inc_path.suffix:
                inc_path = inc_path.with_suffix(".tex")
            if inc_path.exists():
                out.append(read_with_inputs(inc_path))
                continue
        out.append(line)
    return "".join(out)

text = read_with_inputs(main)
labels = re.findall(r"\\label\{([^}]+)\}", text)
refs = re.findall(r"\\ref\{([^}]+)\}", text)
print(f"scanned {main.name} + \\input files")
print("MISSING:")
missing = [x for x in refs if x not in labels]
for x in sorted(set(missing)):
    print(" ", x, f"({missing.count(x)}x)")
if not missing:
    print("  none — all references resolve")
