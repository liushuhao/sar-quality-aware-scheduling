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
# Synthetic control: the SAME families re-run under the v2 closure.  It
# separates "the Eq.(22) switch" from "the real-orbit geometry" -- ticket 17's
# confound-removal item.  Prefixed syn_ so it can never be mistaken for a
# frozen family artifact.
SYNTHETIC_BUDGETS = [("syn_p40g60", (40, 60)), ("syn_p80g120", (80, 120)),
                     ("syn_p160g240", (160, 240))]
FROZEN_V1_MATRIX = FORK.parents[1] / "papers" / "sliding-spotlight-scheduling"     / "experiments" / "results" / "matrix"

PLATEAU_MEDIAN_DB = 1.0
PLATEAU_UNIT_DB = 2.0
P1_THRESHOLD = 3
PROMOTION_DB = 6.0

# ---- void_realwindow markers (ticket 30 (f), registered by hand 2026-10-06) --
#
# This generator rewrites all three v2_results files wholesale, so a marker
# that lives only in the files on disk is erased by the next run.  The marker
# dicts are therefore pinned here, verbatim, and merged in before each
# json.dumps.  ``scope_in_this_file`` is the only per-file field; the other
# eight are identical across the three and live in _VOID_COMMON.
_VOID_COMMON = {
    "status": "VOID FOR CITATION -- the real-window numbers in this file are "
              "permanently unciteable",
    "reason": "Ledger R17 / ticket 25: these real-window numbers were produced "
              "under the broken-geometry scenario world -- windows came from an "
              "arbitrary phase point rather than from enumerating real transits, "
              "and t_ca/r0 were task scalars rather than per-window quantities. "
              "Ticket 25 measured 0 of 8 clusters servable under that rule, so "
              "the scenario these numbers describe no longer exists. They are "
              "also superseded by the ticket-28 per-window C3/C4 reference "
              "caliber, whose worst-case difference on the same geometry is "
              "36.04%.",
    "superseded_by": "papers/sliding-spotlight-scheduling/experiments/v3_results",
    "caliber_of_replacement": "v3",
    "registered_by": "ticket 30 (f), 2026-10-06 -- audit4 B6",
    "reading_rule": "the numbers in this file are RETAINED as the historical "
                    "record and stay machine-readable, exactly like the "
                    "superseded criteria in analysis_prereg_v2.json. What is "
                    "forbidden is citing the real-window numbers, not their "
                    "existence. Do not read a retained number as a current one.",
    "m_family_status": "STILL VALID",
    "note": "machine anchor for the replacement readings: "
            "scripts/verify_v3_verdicts.py (rc=0)",
}

VOID_RESULTS_TABLE = {
    **_VOID_COMMON,
    "scope_in_this_file":
        "The R-family rows (R1C/R2F/R3H/R4H) are void. They are superseded by "
        "the v3 artifacts and their verdicts (R1C structural DEAD; R2F/R3H descriptive ALIVE; "
        "the base-budget front collapse judged SEARCH-ARTIFACT and its narrative withdrawn as a falsified "
        "artifact) are registered in analysis_prereg_v2.json "
        "amendment_20261005_v3_realwindow. This file also carries no M-family "
        "rows.",
}

VOID_CONVERGENCE_REPORT = {
    **_VOID_COMMON,
    "scope_in_this_file":
        "The R-family verdicts are void: the UNCONVERGED / CONVERGED readings "
        "and the P1 statements attached to them describe the superseded world. "
        "The v3 convergence judgement is the preregistered SEARCH-ARTIFACT / "
        "PHYSICAL / NOT-PLATEAUED rule in "
        "experiments/v3_results/CALIBRATION_PREREG.md, and it returned "
        "SEARCH-ARTIFACT for both R2F and R3H with NOT-PLATEAUED at the top "
        "budget.",
}

VOID_CONFOUND_CONTROL = {
    **_VOID_COMMON,
    "scope_in_this_file":
        "SCOPE INVERTED relative to its siblings: this file contains ONLY "
        "synthetic M-family measurements (M1NC/M2WF/M2WH/M3NC/M4WH), which are "
        "unaffected by ticket 25 and were re-measured post-fix at bit-exact "
        "anchor_delta 0. The file therefore stays VALID. It carries the void "
        "only as an inherited note: the real-window comparison it was built to "
        "attribute is superseded, so any argument that CONSUMES this control to "
        "qualify a real-window number inherits the void, while the control's "
        "own numbers do not.",
}


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


def nondominated_front(front: list[dict]) -> list[dict]:
    """The genuine Pareto set: strictly-dominated members AND exact duplicates
    removed.

    Ticket 17 acceptance item 16.  pymoo's ``only_non_dominated_front`` keeps
    ULP-level duplicates, so a family whose f_q barely varies ends up with
    dozens of copies of one point -- a "front" that is one point repeated.

    Two passes, because a single pairwise test is wrong in both directions:

      * a pairwise "someone is >= me" test makes DUPLICATES exclude each
        other, so a front of pure duplicates yields ZERO survivors (measured:
        R1C reported 0 non-dominated, which is impossible for a front that
        spans a real f1 range);
      * requiring a STRICT improvement misses the duplicates entirely
        (measured: that version reported 0 redundancies across 2883
        members, hiding an 81% defect).

    So: pass 1 drops members with a strictly better member; pass 2 keeps one
    representative per distinct (f1_star, f_q) pair among the survivors.
    """
    strict_survivors = []
    for i, x in enumerate(front):
        beaten = any(
            (y["f1_star"] > x["f1_star"] or y["f_q"] > x["f_q"])
            and y["f1_star"] >= x["f1_star"]
            and y["f_q"] >= x["f_q"]
            for j, y in enumerate(front)
            if j != i
        )
        if not beaten:
            strict_survivors.append(x)
    seen: set[tuple[float, float]] = set()
    unique = []
    for x in strict_survivors:
        key = (x["f1_star"], x["f_q"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(x)
    return unique


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

        nd_front = [nondominated_front(a["front"])
                    for a in levels[BUDGETS[-1][0]][fam]]
        nd_counts = [len(x) for x in nd_front]
        report["families"][fam] = {
            "front_size_median_by_budget": [statistics.median(x) for x in fs],
            "nondominated_front_median_at_top": statistics.median(nd_counts),
            "redundant_member_fraction_at_top": round(
                1.0 - statistics.median(nd_counts) / statistics.median(fs[-1]), 4
            ) if statistics.median(fs[-1]) else 0.0,
            "distinct_fq_of_nondominated_median": statistics.median(
                [len({round(r["f_q"], 6) for r in x}) for x in nd_front]
            ),
            "distinct_fq_median_by_budget": med,
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

    # MANDATORY companion: the convergence report is what makes any richness
    # statement admissible.  Ticket 17's red line says a richness claim without
    # ladder evidence is not a claim -- so the two artifacts are written
    # together or the results are not written at all.
    conv = {
        "schema": "v2-convergence-report/1.0",
        "note": "regenerated by build_v2_results.py; kept as a separate file "
                "because it is the admissibility record for any P1 statement",
        "plateau_rule": report["freeze"]["plateau_rule"],
        "verdicts": {
            fam: {
                "convergence": v["convergence_verdict"],
                "top_pair_median_delta": v["top_pair_median_delta"],
                "top_pair_max_unit_delta": v["top_pair_max_unit_delta"],
                "P1_status": v["P1"]["status"],
                "P1_statement": v["P1"]["statement"],
                "promotion_fires_anywhere": v["P3_promotion"]["fires_anywhere"],
            }
            for fam, v in report["families"].items()
        },
        "rule": "an UNCONVERGED family supports no physical claim whatsoever, "
                "including a richness claim whose threshold happens to be met",
        "escalation": "the budget allowance above 160/240 is spent (ticket 20 "
                      "ran 320/480); raising it for a verdict is a new decision, "
                      "not a default",
    }
    # ---- confound control: synthetic families, v2 closure vs frozen v1 ----
    control = {"schema": "v2-confound-control/1.0",
               "why": "the real-window results differ from the frozen ones in "
                      "TWO ways -- the Eq.(22) closure and the real-orbit "
                      "geometry. Re-running the SYNTHETIC families under the "
                      "v2 closure at the same budget ladder attributes the "
                      "difference to geometry.",
               "note": "the v1 column is the FROZEN artifact (read-only); the "
                       "v2 column is a fresh run in .scratch, never in place",
               "premise_check": "the v2 column is only a synthetic control if it "
                                "actually consumed the SYNTHETIC manifests. That "
                                "is verified per artifact below by reading each "
                                "pilot's own manifest back and checking its "
                                "schema and family code, so the attribution is "
                                "not resting on an unrecorded premise.",
               "families": {}}
    syn_levels = {}
    for name, _ in SYNTHETIC_BUDGETS:
        d = RUN / name
        if d.is_dir():
            syn_levels[name] = load_level(name)
    if syn_levels:
        frozen = {}
        for p in sorted(FROZEN_V1_MATRIX.glob("pilot_*.json")):
            art = json.loads(p.read_text(encoding="utf-8"))
            fam = Path(art["manifest"]).name.rsplit("_seed", 1)[0]
            frozen.setdefault(fam, []).append(art)
        for fam, arts_v1 in sorted(frozen.items()):
            a1 = statistics.median(x["anchor_f1_star"] for x in arts_v1)
            d1 = statistics.median(distinct_fq(x) for x in arts_v1)
            # premise check: prove the v2 column ran the SYNTHETIC manifests
            premise = {"checked_artifacts": 0, "schema_ok": 0, "family_ok": 0}
            if name in syn_levels and fam in syn_levels[name]:
                for art in syn_levels[name][fam]:
                    mp = Path(art["manifest"])
                    if not mp.is_absolute():
                        mp = FORK.parents[1] / mp
                    premise["checked_artifacts"] += 1
                    try:
                        mm = json.loads(mp.read_text(encoding="utf-8"))
                    except (OSError, ValueError):
                        continue
                    if mm.get("schema") == "scenario-manifest/1.0":
                        premise["schema_ok"] += 1
                    if mm.get("scenario", {}).get("family_code") == fam:
                        premise["family_ok"] += 1
            row = {"v1_frozen": {"anchor_f1_star": round(a1, 6),
                                 "distinct_fq_median": d1},
                   "premise_check": premise}
            for name, _ in SYNTHETIC_BUDGETS:
                if name not in syn_levels or fam not in syn_levels[name]:
                    continue
                arts = syn_levels[name][fam]
                row[name] = {
                    "anchor_f1_star": round(
                        statistics.median(x["anchor_f1_star"] for x in arts), 6),
                    "distinct_fq_median": statistics.median(
                        distinct_fq(x) for x in arts),
                }
            if SYNTHETIC_BUDGETS[0][0] in row:
                row["anchor_delta_at_40g60"] = round(
                    row[SYNTHETIC_BUDGETS[0][0]]["anchor_f1_star"] - a1, 6)
            control["families"][fam] = row

    OUT.mkdir(parents=True, exist_ok=True)
    control["void_realwindow"] = VOID_CONFOUND_CONTROL
    conv["void_realwindow"] = VOID_CONVERGENCE_REPORT
    report["void_realwindow"] = VOID_RESULTS_TABLE
    (OUT / "confound_control.json").write_text(
        json.dumps(control, indent=2, sort_keys=True, ensure_ascii=False) + chr(10),
        encoding="utf-8",
    )
    (OUT / "convergence_report.json").write_text(
        json.dumps(conv, indent=2, sort_keys=True, ensure_ascii=False) + chr(10),
        encoding="utf-8",
    )
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
    if control["families"]:
        print("confound control (anchor delta at 40/60, v2 vs frozen v1):")
        for fam, row in control["families"].items():
            print(f"  {fam:7} d(anchor)={row.get('anchor_delta_at_40g60')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())