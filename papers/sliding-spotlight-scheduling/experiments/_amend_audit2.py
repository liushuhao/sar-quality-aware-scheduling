"""Append the audit2 R1-redline amendment to analysis_prereg.json by TEXT insertion.

Run from papers/sliding-spotlight-scheduling/:
    "/d/Program Files/Python/python" experiments/_amend_audit2.py

Why text insertion rather than a json.dumps round-trip: the frozen file uses
hand-tuned single-line array objects (Prettier style) that a re-serialiser expands
into multiple lines. Semantic equality would hold, but the append-only discipline
requires the frozen prefix to stay BYTE-identical, and this repo has a
`byte-compare refuses resume` rule (spec D13 clause 3). Two earlier attempts with
json.dumps produced a 29-insert / 3-delete diff; this version inserts before the final
closing brace and asserts the frozen prefix bytes are untouched.

Scope: ONE amendment only. The g_T single-weight amendment drafted during audit2 was
WITHDRAWN -- gate-review measured that f_Q scales as 1/rho_a^2 only while g_T is ON
(g_T OFF gives 1/rho_a^1), so g_T is the carrier of the inverse-square law, D05-5's
dual-weighting disclosure is correct, and no correction is owed to the preregistration.
"""
import json
from collections import OrderedDict
from pathlib import Path

PREREG = Path(__file__).resolve().parent / "analysis_prereg.json"
AMENDMENT_NAME = "amendment_20260930_audit2_r1_redline"

R1_REDLINE = OrderedDict(
    [
        (
            "rationale",
            "Audit2 (2026-09-30: four fresh-subagent lanes -- premise / code / data / cross-layer -- "
            "plus a main-thread theory pass, run after a backend model change) found that the "
            "machine-readable verdict skeleton still encodes the PHYSICAL-vs-SEARCH-ARTIFACT binary "
            "that tickets 19/20 adjudicated as SEARCH-ARTIFACT at every density. The refutation lived "
            "only in the spec prose (D14 / D15), so the primary machine-readable artifact retained a "
            "refuted criterion. Append-only per amendment_discipline: nothing already present is "
            "mutated; this records the adjudication and forbids the refuted branch.",
        ),
        (
            "verdict",
            "Frontier collapse at any density in the synthetic family is a SEARCH ARTIFACT. The "
            "PHYSICAL branch is REFUTED: amendment_20260930_convergence_calibration shows the front "
            "keeps growing with budget at N=40/60/80/100, and the N=100 ladder 2->4->17->48 "
            "(distinct-fq at budget 60/120/160/240/320/480) exhibits NO plateau, so the reading is "
            "NOT-YET-CONVERGED rather than collapsed.",
        ),
        (
            "applies_to",
            [
                "amendment_20260930_probe_density.physics_collapse_verdict (wording 'COLLAPSE IS PHYSICAL' -- branch now dead)",
                "amendment_20260930_convergence_calibration.physics_collapse_verdict (same skeleton, same status)",
                "amendment_20260930_convergence_calibration.search_artifact_verdict (this amendment is consistent with it and supersedes the earlier conditional reading)",
            ],
        ),
        (
            "binding_rule",
            "No PHYSICAL-collapse claim may be made from any density readout, at any budget, without a "
            "per-density convergence ladder exhibiting a plateau (distinct-fq flat across a further "
            "budget doubling) under a pre-registered plateau threshold. Absence of a plateau is "
            "NOT-YET-CONVERGED, never 'collapsed'. This restates spec D15 red line 1 in machine-readable "
            "form so the preregistration no longer carries a refuted criterion.",
        ),
    ]
)


def main() -> None:
    raw_bytes = PREREG.read_bytes()
    raw = raw_bytes.decode("utf-8")
    crlf = "\r\n" in raw
    nl = "\r\n" if crlf else "\n"

    before_bytes = raw_bytes
    before = json.loads(raw, object_pairs_hook=OrderedDict)
    if AMENDMENT_NAME in before:
        raise SystemExit(f"{AMENDMENT_NAME} already present -- refusing to duplicate")

    lines = raw.split(nl)
    while lines and lines[-1] == "":
        lines.pop()
    if lines[-1] != "}":
        raise SystemExit(f"unexpected file tail: {lines[-1]!r}")
    if lines[-2] != "  }":
        raise SystemExit(f"unexpected last key close: {lines[-2]!r}")

    body = json.dumps(R1_REDLINE, ensure_ascii=False, indent=2)
    rendered = "\r\n".join(("  " + ln if ln else ln) for ln in body.split("\n"))
    new_lines = lines[:-2] + ["  },", f'  "{AMENDMENT_NAME}": {rendered}', "}", ""]
    PREREG.write_bytes(nl.join(new_lines).encode("utf-8"))

    after_bytes = PREREG.read_bytes()
    after = json.loads(after_bytes.decode("utf-8"), object_pairs_hook=OrderedDict)

    # frozen prefix must survive byte-identically, not merely semantically
    frozen_keys = [k for k in before if not k.startswith("amendment_")]
    prefix_len = len(nl.join(lines[:-2]).encode("utf-8"))
    prefix_after = after_bytes[:prefix_len]
    if prefix_after != before_bytes[:prefix_len]:
        raise SystemExit("frozen prefix bytes drifted -- aborting")

    for k in before:
        if json.dumps(after[k], ensure_ascii=False) != json.dumps(before[k], ensure_ascii=False):
            raise SystemExit(f"frozen field mutated: {k}")
    added = [k for k in after if k not in before]
    if added != [AMENDMENT_NAME]:
        raise SystemExit(f"unexpected key delta: {added}")
    if len(frozen_keys) == 0:
        raise SystemExit("no frozen keys -- refusing to treat the file as append-only")

    print(
        f"OK append-only: {len(before)} pre-existing keys byte-identical "
        f"(newline={'CRLF' if crlf else 'LF'}), added {added}"
    )


if __name__ == "__main__":
    main()