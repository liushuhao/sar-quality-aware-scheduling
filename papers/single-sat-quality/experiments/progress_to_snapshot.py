#!/usr/bin/env python3
"""Convert a solver _progress.json into the snapshot format the hard-audit
script (_audit_full_hard.py) consumes.

MOEA runners persist entries keyed by "S1/S1-A_seed00.pkl" with fields
selected / t_actuals / phis_off_nadir — the same schema the audit needs.
The only transformation is emitting {"completed": {...}} (or passing the
raw dict through when already shaped that way).

Usage: python progress_to_snapshot.py <progress.json> <out.json>
"""
import json, sys
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    data = json.load(open(src, encoding="utf-8"))
    completed = data["completed"] if "completed" in data else data
    # Audit needs key -> {selected, t_actuals, phis_off_nadir, ...}
    missing = [k for k, v in completed.items()
               if not all(f in v for f in ("selected", "t_actuals", "phis_off_nadir"))]
    if missing:
        print(f"WARNING: {len(missing)} entries missing audit fields "
              f"(e.g. {missing[0]}) — audit will skip them silently?")
    dst.write_text(json.dumps({"completed": completed}, indent=2), encoding="utf-8")
    print(f"wrote {dst} ({len(completed)} entries)")


if __name__ == "__main__":
    main()
