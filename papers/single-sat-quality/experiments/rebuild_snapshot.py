"""Rebuild the full hard-constraint audit snapshot from live solver progress files.

_audit_full_hard.py's default snapshot (results/_snapshot_audit.json) is an
orphan: its producer died in the 08-06 window-fix refactor and the file on disk
dates from 08-04 (pre-window-fix GA-P-BL, version ac7e0aef), which makes the
audit report thousands of false out-of-window violations against current
scenario windows. This script is the canonical snapshot builder for the audit
gate: it reassembles the flat {scenario_key: entry} snapshot from the current
progress JSONs of every solver family that persists selected/t_actuals/phis.

Baselines (G-BL/G-SM, baselines_200.json b1/b3) do not persist per-task
selected/t_actuals, so they are excluded here; their feasibility is covered by
the construction-time audits (audit_gapbl-style reruns).
"""
import json
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "results"

FAMILIES = [
    "moea_2obj",
    "moea_3obj",
    "b2_profit_bl",
    "moea_3obj_no_incidence",
    "moea_3obj_no_physics",
    "moea_3obj_no_squint",
]

OUT = RESULTS / "_snapshot_gate.json"


def main():
    out = {}
    versions = {}
    for fam in FAMILIES:
        prog = json.load(open(RESULTS / fam / "_progress.json", encoding="utf-8"))
        comp = prog["completed"]
        for key, entry in comp.items():
            if not all(f in entry for f in ("selected", "t_actuals", "phis_off_nadir")):
                raise SystemExit(f"{fam}: entry {key} lacks selected/t_actuals/phis_off_nadir")
            # Composite key: scenario keys collide across families (both moea_2obj
            # and moea_3obj use "S1/..."), so the flat dict is keyed by
            # "<fam>|<scenario>"; _audit_full_hard resolves the pkl path and the
            # density class from the "scenario" field.
            out[f"{fam}|{key}"] = {"scenario": key, "entry": entry}
            versions[f"{fam}|{key}"] = entry.get("solver_version", "?")
    json.dump({"completed": out}, open(OUT, "w", encoding="utf-8"))
    print(f"snapshot written: {OUT} ({len(out)} entries)")
    from collections import Counter
    print("versions:", dict(Counter(versions.values())))


if __name__ == "__main__":
    main()