"""Coverage-parity recompute gate (constraint-audit A2-G2, 2026-10-16).

Paper claim (main.tex, coverage parity paragraph): over all 90 promoted
pilot artifacts (3 budget tiers x 3 families x 10 seeds) the
coverage-maximal front member ties the anchor served fraction exactly
(90/90), and R1C saturates f1*=1.0 in 30/30.  This gate recomputes both
counts from the artifacts so the sentence cannot silently drift.

Exit 0 iff units==90, ties==90, R1C saturation==30.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "experiments" / "v3_results"
TIERS = ["matrix", "matrix_p80g120", "matrix_p160g240"]


def main() -> int:
    ties = satur = total = 0
    bad: list[str] = []
    for tier in TIERS:
        d = BASE / tier
        if not d.is_dir():
            print(f"missing tier dir: {d}")
            return 1
        for p in sorted(d.glob("pilot_*.json")):
            rec = json.loads(p.read_text(encoding="utf-8"))
            a = rec.get("anchor_f1_star")
            m = rec.get("max_f1_star_on_front")
            if a is None or m is None:
                bad.append(f"{tier}/{p.name}: missing fields")
                continue
            total += 1
            if m == a:
                ties += 1
            else:
                bad.append(f"{tier}/{p.name}: anchor={a!r} max_front={m!r}")
            if p.name.startswith("pilot_R1C"):
                if m == 1.0:
                    satur += 1
                else:
                    bad.append(f"{tier}/{p.name}: R1C f1*={m!r} != 1.0")
    print(f"units={total} ties={ties} R1C_saturated={satur}")
    if bad:
        print("FAILURES:")
        for b in bad:
            print(" ", b)
        return 1
    if (total, ties, satur) != (90, 90, 30):
        print("COUNT MISMATCH: expected units=90 ties=90 R1C=30")
        return 1
    print("coverage parity 90/90 exact ties; R1C 30/30 f1*=1.0 -- PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
