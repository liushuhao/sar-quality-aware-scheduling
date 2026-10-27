#!/usr/bin/env python3
"""R96 figure wave: caption numbers must trace to figure-data receipts.

Every numeric token in the five new figure captions of ``paper/main.tex``
must match (at the caption's printed precision) a value in the matching
``experiments/v5_results/figure_data/figN_*.json`` receipt, which the plot
scripts generate from the frozen artifacts.  Tokens that are structural
(budget strings, s-grid values, panel markers, version tags) are
whitelisted per figure; everything else unmatched is a FAIL -- a caption
number with no receipt is exactly the "green but untraceable" figure this
gate exists to prevent.

Matching rules, in order: exact string in any receipt value (covers pair
forms like "199/458" and interval forms like "18.25/30.44", because the
receipts store the per-arm medians and pair totals the captions join);
numeric equality at the caption's decimal count (1.35 matches 1.3481 only
after rounding the receipt to the caption's precision -- so the caption
must print the rounded truth); range endpoints ("a--b" both match some
receipt values); "a of b" (both match); single numbers (match some receipt
value at precision).

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/check_figure_receipts.py

rc: 0 every caption number traces; 1 at least one does not.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
TEX = FORK / "paper" / "main.tex"
FD = FORK / "experiments" / "v5_results" / "figure_data"

# figure label -> (receipt file, caption anchor, structural whitelist)
FIGS = {
    "fig:dwelllaw": ("fig2_dwell_mechanism.json",
                     "The endogenous dwell law: scene dwell",
                     {"5", "12", "0.8", "5×5"} & set()),  # built below
    "fig:scenario": ("fig4_scenario_set.json",
                     "The released scenario set",
                     None),
    "fig:probes": ("fig6_construction_probes.json",
                   "Two construction probes, one ruler",
                   None),
    "fig:dwelldist": ("fig7_dwell_distribution.json",
                      "The endogenous dwell as the schedule consumes it",
                      None),
    "fig:counterfactual": ("fig8_counterfactual.json",
                           "The fixed-dwell counterfactual at the as-placed",
                           None),
}
# structural tokens shared by all captions: budget, s-grid, conventions,
# family names ("50-task family"), version tags
COMMON_OK = {"40/60", "160/240", "1.0", "0.9", "1.4", "2.0", "0.8",
             "5", "25", "v5", "0.00", "1", "12", "2", "3", "50", "100",
             "20", "46"}
FIGS["fig:dwelllaw"] = ("fig2_dwell_mechanism.json",
                        "The endogenous dwell law: scene dwell",
                        {"0.36", "775.4", "0.031", "4.9338"})  # fixture
# constants of section 2.1, registered in the body text and the fixture

NUM_TOKEN = re.compile(r"\d+(?:\.\d+)?")


def caption_text(tex: str, anchor: str) -> str:
    i = tex.find("\\caption{" + anchor)
    if i < 0:
        raise SystemExit(f"ABORT: caption anchor not found: {anchor}")
    depth, j = 1, i + len("\\caption{")
    while depth:
        if tex[j] == "{":
            depth += 1
        elif tex[j] == "}":
            depth -= 1
        j += 1
    return tex[i:j]


def receipt_values(receipt: dict):
    vals = []

    def walk(v):
        if isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
        else:
            vals.append(v)

    walk(receipt)
    return vals


def matches(token: str, vals) -> bool:
    # tolerance = half a unit in the caption's last printed digit (the L8
    # gate's registered policy; round-half can flip either way on .5 rests)
    def close(a: float, b: float) -> bool:
        d = len(token.split(".")[1]) if "." in token else 0
        tol = 0.5 * (10 ** -d) + 1e-12
        return abs(a - b) <= tol

    cands = [token]
    if "--" in token or "/" in token or " of " in token:
        cands += re.split(r"--|/| of ", token)
    for t in cands:
        if not re.fullmatch(r"\d+(\.\d+)?", t or ""):
            continue
        f = float(t)
        for v in vals:
            nums = []
            if isinstance(v, (int, float)):
                nums = [float(v), abs(float(v))]  # "pp below" prints magnitudes
            elif isinstance(v, list):
                nums = [float(x) for x in v if isinstance(x, (int, float))]
                nums += [abs(x) for x in nums]
            elif isinstance(v, str) and t in v:
                return True
            if any(close(f, x) for x in nums):
                return True
    return False


def main() -> int:
    tex = TEX.read_text(encoding="utf-8")
    fails, total = [], 0
    for label, (receipt_file, anchor, extra_ok) in FIGS.items():
        receipt = json.loads((FD / receipt_file).read_text(encoding="utf-8"))
        vals = receipt_values(receipt)
        cap = caption_text(tex, anchor)
        ok = COMMON_OK | (extra_ok or set())
        # tokens inside $...$ math and LaTeX macros: strip commands first
        cap_plain = re.sub(r"\\[a-zA-Z]+", " ", cap)
        for tok in NUM_TOKEN.findall(cap_plain):
            if tok in ok:
                continue
            total += 1
            if not matches(tok, vals):
                fails.append(f"{label}: caption token {tok!r} has no "
                             f"receipt match in {receipt_file}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"=== figure receipts: {total - len(fails)}/{total} caption "
          f"numbers trace to receipts ===")
    if fails:
        print("VERDICT: at least one caption number is untraceable")
        return 1
    print("VERDICT: every caption number traces to a figure receipt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
