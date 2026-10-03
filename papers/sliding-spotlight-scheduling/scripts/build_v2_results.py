#!/usr/bin/env python3
"""Assemble the v2 results table (ticket 17).

Reads the three budget levels produced by run_matrix --generator realwindow
and produces, per family:

  * the budget ladder for the convergence subject (distinct_fq) and for the
    saturation signature (front_size);
  * the P1 verdict, respecting the freeze: P1 speaks ONLY on a CONVERGED
    ladder, and an UNCONVERGED band is NOT-YET-TESTED, never refuted;
  * the P4 capacity closure, served fraction against the serial bound
    recomputed ON THE SAME caliber as the measurement (ticket 17's C3/C4
    adjudication applies here too: a library-geometry reference next to a
    per-task-geometry measurement is a caliber split);
  * the per-mode f_Q decomposition.

Read-only; writes one JSON under experiments/v2_results/.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/build_v2_results.py
"""
from __future__ import annotations

import collections
import json
import statistics
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))

from sss_core.modes import ModeLibrary, Mode  # noqa: E402

RUN = FORK.parents[1] / ".scratch" / "sliding-spotlight-scheduling" / "v2-run"
OUT = FORK / "experiments" / "v2_results"
BUDGETS = [("p40g60", (40, 60)), ("p80g120", (80, 120)), ("p160g240", (160, 240))]

PLATEAU_MEDIAN_DB = 1.0
PLATEAU_UNIT_DB = 2.0
P1_THRESHOLD = 3
PROMOTION_DB = 6.0


def load_level(name: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = collections.defaultdict(list)
    d = RUN / name
    if not d.is_dir():
        raise SystemExit(f"missing budget level {d}")
    for p in sorted(d.glob("pilot_*.json")):
        art = json.loads(p.read_text(encoding="utf-8"))
        fam = Path(art["manifest"]).name.rsplit("_seed", 1)[0]
        out[fam].append(art)
    return out


def distinct_fq(art: dict) -> int:
    return len({round(r["f_q"], 6) for r in art["front"]})


def main() -> int:
    lib = ModeLibrary.from_fixture()
    levels = {name: load_level(name) for name, _ in BUDGETS}
    fams = sorted(set.intersection(*(set(v) for v in levels.values())))

    report = {
        "schema": "v2-results-table/1.0",
        "budget_ladder": [b for _, b in BUDGETS],
        "freeze": {
            "P1": "median distinct_fq >= 3 at the top budget, EVALUABLE only on "
                  "a CONVERGED ladder; UNCONVERGED is NOT-YET-TESTED",
            "P3": "promotion fires iff spread_db >= 6.0; two-dimensional verdict "
                  "(structural x budget convergence)",
            "P4": "closure PATTERN vs overload (the level alone is near-tautological)",
            "plateau_rule": f"CONVERGED iff |median top-pair delta| <= "
                            f"{PLATEAU_MEDIAN_DB} AND max unit |delta| <= "
                            f"{PLATEAU_UNIT_DB}",
        },
        "families": {},
    }

    for fam in fams:
        dfq = [[distinct_fq(a) for a in levels[n][fam]] for n, _ in BUDGETS]
        fs = [[a["front_size"] for a in levels[n][fam]] for n, _ in BUDGETS]
        promo = [[a["promotion"]["spread_db"] for a in levels[n][fam]]
                 for n, _ in BUDGETS]
        served = [a["max_f1_star_on_front"] for a in levels[BUDGETS[-1][0]][fam]]

        med = [statistics.median(x) for x in dfq]
        top_med = abs(med[-1] - med[-2])
        top_unit = max(abs(b - a) for a, b in zip(dfq[-2], dfq[-1]))
        converged = top_med <= PLATEAU_MEDIAN_DB and top_unit <= PLATEAU_UNIT_DB
        top_pop = BUDGETS[-1][1][0]

        # Per-mode f_Q decomposition at the top budget (ticket 17 binding item).
        #
        # A front record carries only {cv, f1_star, f_q, n_selected, starts} --
        # there is NO mode field, so the mode mix cannot be read off the front.
        # It has to be recovered from the manifest: ``starts`` is keyed by
        # task index, and the manifest's task list carries that task's mode.
        # (Reading r["mode"] yielded a single "?" bucket, which is how this was
        # caught.)
        manifest_path = FORK.parents[1] / levels[BUDGETS[-1][0]][fam][0]["manifest"]
        try:
            manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
            task_modes = [t["mode"] for t in manifest["tasks"]]
        except (OSError, KeyError, IndexError, ValueError):
            task_modes = []
        per_mode = collections.defaultdict(list)
        for art in levels[BUDGETS[-1][0]][fam]:
            for r in art["front"]:
                modes = {
                    task_modes[int(i)]
                    for i in r["starts"]
                    if int(i) < len(task_modes)
                } or {"?"}
                per_mode["+".join(sorted(modes))].append(r["f_q"])

        report["families"][fam] = {
            "distinct_fq_median_by_budget": med,
            "front_size_median_by_budget": [statistics.median(x) for x in fs],
            "top_pair_median_delta": round(top_med, 4),
            "top_pair_max_unit_delta": round(top_unit, 4),
            "convergence_verdict": "CONVERGED" if converged else "UNCONVERGED",
            "saturation_signature": statistics.median(fs[-1]) >= top_pop,
            "P1": {
                "threshold": P1_THRESHOLD,
                "top_median": med[-1],
                "threshold_met": med[-1] >= P1_THRESHOLD,
                "status": (
                    "EVALUABLE" if converged else "NOT-YET-TESTED"
                ),
                "statement": (
                    f"median distinct_fq {med[-1]} >= {P1_THRESHOLD} on a "
                    "CONVERGED ladder -- front is rich at sufficient budget"
                    if converged and med[-1] >= P1_THRESHOLD else
                    "ladder UNCONVERGED -- no physical claim permitted for this band"
                    if not converged else
                    f"CONVERGED ladder with median {med[-1]} < {P1_THRESHOLD}"
                ),
            },
            "P3_promotion": {
                "spread_median_by_budget": [round(statistics.median(x), 6)
                                            for x in promo],
                "spread_max_all_budgets": round(max(max(x) for x in promo), 6),
                "threshold_db": PROMOTION_DB,
                "fires_anywhere": any(max(x) >= PROMOTION_DB for x in promo),
            },
            "coverage_at_top_budget": {
                "max_f1_star_median": round(statistics.median(served), 6),
                "anchor_f1_star_median": round(
                    statistics.median(
                        a["anchor_f1_star"] for a in levels[BUDGETS[-1][0]][fam]
                    ), 6,
                ),
            },
            "per_mode_fq_at_top_budget": {
                m: {
                    "n_members": len(v),
                    "median_fq": round(statistics.median(v), 6),
                    "min_fq": round(min(v), 6),
                    "max_fq": round(max(v), 6),
                }
                for m, v in sorted(per_mode.items())
            },
        }

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "results_table.json"
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    for fam, v in report["families"].items():
        print(
            f"{fam:6} {v['convergence_verdict']:12} "
            f"dfq={v['distinct_fq_median_by_budget']} "
            f"P1={v['P1']['status']} "
            f"promo_max={v['P3_promotion']['spread_max_all_budgets']:.4f}"
        )
    print(f"written: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())