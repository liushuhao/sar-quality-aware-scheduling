"""Unified-selector recomputation for panel-20260830 N13.

Confound: paper's +7% f3 margin compares MOEA-3 knee (selector maximizes
f1+f2+f3) against MOEA-2 knee (selector maximizes f1+f2, blind to f3).
Part of the gap is selector gaming, not search value of the third objective.

This script re-selects from the persisted frontiers under BOTH unified rules:
  U3: knee = argmax(f1n+f2n+f3n) on each solver's own frontier
  U2: knee = argmax(f1n+f2n) on each solver's own frontier
then compares MOEA-3 vs MOEA-2 per scenario (paired, S1 sparse class).

Reads results/moea_{2,3}obj/_progress.json (frontier_f1/f2/f3 arrays).
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

EXP = Path(__file__).resolve().parents[1] / "experiments"


def load(group_prefix):
    out = {}
    for nobj, name in [(2, "moea_2obj"), (3, "moea_3obj")]:
        p = EXP / "results" / name / "_progress.json"
        d = json.load(open(p))["completed"]
        for key, e in d.items():
            if not key.startswith(group_prefix):
                continue
            f1 = np.array(e["frontier_f1"], dtype=float)
            f2 = np.array(e["frontier_f2"], dtype=float)
            f3 = np.array(e["frontier_f3"], dtype=float)
            if len(f1) == 0:
                continue
            out.setdefault(key, {})[nobj] = (f1, f2, f3)
    return out


def knee(f1, f2, f3, rule):
    def norm(v):
        r = v.max() - v.min()
        return (v - v.min()) / r if r else np.zeros_like(v)
    s = norm(f1) + norm(f2)
    if rule == "U3":
        s = s + norm(f3)
    i = int(np.argmax(s))
    return f1[i], f2[i], f3[i]


def cliffs_delta(a, b):
    a, b = np.asarray(a), np.asarray(b)
    gt = sum((x > b).sum() for x in a)
    lt = sum((x < b).sum() for x in a)
    return (gt - lt) / (len(a) * len(b))


def main():
    group = sys.argv[1] if len(sys.argv) > 1 else "S1"
    data = load(group + "/")
    rows = []
    for key, solv in sorted(data.items()):
        if 2 not in solv or 3 not in solv:
            continue
        f1_2, f2_2, f3_2 = solv[2]
        f1_3, f2_3, f3_3 = solv[3]
        r = {"key": key}
        for rule in ("U3", "U2"):
            r[f"m2_{rule}"] = knee(f1_2, f2_2, f3_2, rule)
            r[f"m3_{rule}"] = knee(f1_3, f2_3, f3_3, rule)
        rows.append(r)

    print(f"{group}: n={len(rows)} paired scenarios\n")
    for rule in ("U3", "U2"):
        m2f3 = np.array([r[f"m2_{rule}"][2] for r in rows])
        m3f3 = np.array([r[f"m3_{rule}"][2] for r in rows])
        m2f2 = np.array([r[f"m2_{rule}"][1] for r in rows])
        m3f2 = np.array([r[f"m3_{rule}"][1] for r in rows])
        m2f1 = np.array([r[f"m2_{rule}"][0] for r in rows])
        m3f1 = np.array([r[f"m3_{rule}"][0] for r in rows])
        w = stats.wilcoxon(m3f3, m2f3)
        d = cliffs_delta(m3f3, m2f3)
        print(f"=== Rule {rule} (knee=argmax {'f1+f2+f3' if rule=='U3' else 'f1+f2'}) ===")
        print(f"  f3: MOEA-2 {m2f3.mean():.4f}  MOEA-3 {m3f3.mean():.4f}  "
              f"margin {(m3f3.mean()/m2f3.mean()-1)*100:+.2f}%  "
              f"paired p={w.pvalue:.2e}  cliff={d:+.3f}")
        print(f"  f2: MOEA-2 {m2f2.mean():.4f}  MOEA-3 {m3f2.mean():.4f}  "
              f"margin {(m3f2.mean()/m2f2.mean()-1)*100:+.2f}%")
        print(f"  f1*: MOEA-2 {m2f1.mean():.4f}  MOEA-3 {m3f1.mean():.4f}  "
              f"coverage cost {(m3f1.mean()/m2f1.mean()-1)*100:+.2f}%")
        win = int((m3f3 > m2f3).sum())
        print(f"  per-scenario f3: MOEA-3 wins {win}/{len(rows)}\n")

    # paper's current asymmetric comparison for reference
    m2_asym = np.array([knee(*solv[2], "U2")[2] for solv in
                        (data[k] for k in sorted(data)) if 2 in solv and 3 in solv])
    m3_asym = np.array([knee(*solv[3], "U3")[2] for solv in
                        (data[k] for k in sorted(data)) if 2 in solv and 3 in solv])
    print(f"=== Paper's asymmetric comparison (m2 U2 knee vs m3 U3 knee) ===")
    print(f"  f3 margin: {(m3_asym.mean()/m2_asym.mean()-1)*100:+.2f}% "
          f"({m3_asym.mean():.4f} vs {m2_asym.mean():.4f})")


if __name__ == "__main__":
    main()
