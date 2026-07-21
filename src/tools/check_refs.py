import re
from pathlib import Path
PROJECT = Path(__file__).resolve().parent.parent
p = Path(r'PROJECT / "docs\small-paper-ijae.tex"')
text = p.read_text(encoding='utf-8')
labels = re.findall(r'\\label\{([^}]+)\}', text)
refs = re.findall(r'\\ref\{([^}]+)\}', text)
print('LABELS:')
for x in labels: print(' ', x)
print('REFS:')
for x in refs: print(' ', x)
print('MISSING:')
for x in refs:
    if x not in labels:
        print(' ', x)
