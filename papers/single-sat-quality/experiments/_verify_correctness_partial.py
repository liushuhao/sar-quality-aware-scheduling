"""Read-only correctness spot-check on live-rerun _progress.json (batch in flight).
Checks: audit-field completeness, stored pkl_sha1 vs on-disk pkl sha1 (provenance),
constraint-feasibility counts. Does NOT write live files.
"""
import json, hashlib, sys
from pathlib import Path

RES = Path("D:/hermes/my-workspace/projects/planning-paper/papers/single-sat-quality/experiments/results")
SCEN = Path("D:/hermes/my-workspace/projects/planning-paper/papers/single-sat-quality/experiments/scenarios")
FAMS = {
    "b2_profit_bl": "GA-P-BL",
    "moea_2obj": "MOEA-2",
    "moea_3obj": "MOEA-3",
}
REQ = ["selected", "t_actuals", "phis_off_nadir", "pkl_sha1",
       "constraint_feasible", "n_constraints_failed", "solver_version"]

def sha1_of(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()

tot_fam = tot_entries = tot_sha_ok = tot_sha_missing = tot_feas_true = 0
all_bad = []
for fam, label in FAMS.items():
    d = json.load(open(RES / fam / "_progress.json", encoding="utf-8"))
    c = d.get("completed", {})
    n = len(c)
    print(f"== {label} ({fam}): {n} completed ==")
    miss_fields = 0
    sha_ok = sha_mismatch = sha_none = 0
    feas_true = 0
    for k, v in c.items():
        missing = [f for f in REQ if f not in v or v.get(f) in (None,)]
        if missing:
            miss_fields += 1
            all_bad.append((fam, k, "field_missing", missing))
        if v.get("constraint_feasible") is True:
            feas_true += 1
        stored = v.get("pkl_sha1")
        on = sha1_of(SCEN / k)
        if stored is None:
            sha_none += 1
        elif stored == on:
            sha_ok += 1
        else:
            sha_mismatch += 1
            all_bad.append((fam, k, "sha_mismatch", f"{stored[:8]}!={on[:8]}"))
    tot_entries += n; tot_fam += 1
    print(f"  feas=True:{feas_true}  fields_ok:{n-miss_fields}  sha_ok:{sha_ok}  sha_none:{sha_none}  sha_mismatch:{sha_mismatch}")
    tot_feas_true += feas_true

print(f"\nTOTAL frames checked={tot_fam} entries={tot_entries} feas=True={tot_feas_true}")
if all_bad:
    print(f"\n!! {len(all_bad)} issues:")
    for fam, k, kind, det in all_bad[:20]:
        print(f"   {fam} {k} [{kind}] {det}")
    sys.exit(1)
print("\nOK: all fields present, stored pkl_sha1 matches on-disk pkls, all feasible")