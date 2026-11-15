"""Caliber equivalence pin (paper1): HEAD solver tree vs 2026-08-14 stamped tree.

Why this exists: verify_paper_numbers.py whitelists result stamps ``4cfc42c0``
and ``720e63c8`` as REVIEWED_EQUIVALENT. The commits after the stamp --
R51 dead-kwarg removal (moea.py / types.py), ticket-26 fail-loud fallback
(so_f1.py, never-executed path), C1 window-containment add (verification /
constraints.py; the verifier runs inside moea_solver's frontier filter, but
the new window check cannot fire on decoded solutions since tau is clipped
to [0, 1]) -- are all off the stored-data generation path, so the stored
m2/m3 results remain numerically current at HEAD. The stamp pair itself
differs only in __init__.py / solver_factory.py removal, not in any
value-chain file, so one pin covers both stamps.

This test is the enforcement behind that whitelist: it materializes the
stamped tree via ``git archive``, runs the same scenario through both trees,
and requires identical value fields. A future behavior-changing edit that
shows up on the sampled surface (sparse S1 + one more density group, both
objective counts, single-sat) fails here, and the whitelist in
verify_paper_numbers.py must then be re-adjudicated (rerun or re-pin);
edits visible only on unsampled branches are caught by the FULL run and the
regression suite, not by this pin alone.

Determinism: ``seed=None`` falls back to 1, but pymoo 0.6.x operators do not
consume the algorithm RNG -- they draw from ``np.random.default_rng(None)``
(system entropy) via ``default_random_state``, so identical code is NOT
bit-reproducible across processes at small budgets. The fixture runner
therefore pins the entropy draws to a fixed seed before importing pymoo;
with the pin, identical code produces identical output at any budget.

Set ``P1_PIN_FULL=1`` for the full-budget evidence run (pop=100, gen=200,
matching the stored MOEA_PARAMS, plus a dense S4 scenario; writes
papers/single-sat-quality/review/pin-equivalence-evidence-20261031.json and
reports -- without asserting -- how close the rerun lands on the stored
entries, which also exposes environment/library drift). Default is a tiny
budget so the suite stays fast.
"""
import io
import json
import os
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PAPER = REPO / "papers" / "single-sat-quality"
STAMP = "720e63c8"
BAD_STAMP = "681ced6b"
VALUE_FIELDS = ("f1", "f1_raw", "f1_gbl", "f2", "f3", "n_selected", "n_frontier")
LIST_FIELDS = ("frontier_f1", "frontier_f2", "frontier_f3",
               "selected", "t_actuals", "phis_off_nadir")
AUDIT_FIELDS = ("constraint_feasible", "n_constraints_failed")

# Mirrors run_one() in experiments/run_moea_3obj.py exactly (scenario load,
# instance build, G-BL hot-start encode, solver call, value extraction) minus
# the progress-file machinery. Budget comes from argv so one script serves
# both the tiny suite run and the full evidence run.
#
# The np.random.default_rng pin must sit before the sar_sim imports: pymoo
# operators request entropy-seeded generators (default_random_state), and
# without the pin identical code drifts run-to-run (verified empirically:
# same tree, two runs, different f1). With the pin, tree equality is
# bit-exact while the known-bad negative control still fires.
FIXTURE_RUNNER = r"""
import json, pickle, sys
sys.path.insert(0, sys.argv[1])
import numpy as np
_orig_rng = np.random.default_rng
np.random.default_rng = lambda seed=None: _orig_rng(20260814 if seed is None else seed)
from sar_sim.solver.moea import moea_solver
from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

pkl_path, out_path = sys.argv[2], sys.argv[3]
pop, gen, n_obj = int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])

with open(pkl_path, "rb") as f:
    data = pickle.load(f)
windows, targets = data["windows"], data["targets"]
SLEW_RATE, SETTLE_TIME = 0.0524, 5.0

instance = build_agile_instance_from_scenario(
    data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
precompute_geometry(instance, step_s=10.0)
gbl = baseline_b1(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
                  geom_cache=instance.geom_cache, instance=instance)
target_to_idx = {t.target_id: i for i, t in enumerate(instance.tasks)}
x0 = np.zeros(2 * instance.N)
seen = set()
for obs in gbl.schedule:
    tid = obs.window.target_id
    if tid in target_to_idx:
        idx = target_to_idx[tid]
        if idx not in seen:
            seen.add(idx)
            x0[idx] = 1.0
            span = instance.tasks[idx].time_span
            tau = (obs.t_actual_start.timestamp() - instance.tasks[idx].t_earliest) / span if span > 0 else 0.5
            x0[instance.N + idx] = max(0.0, min(1.0, tau))
hotstart = x0 if seen else None

result = moea_solver(
    windows, targets,
    population_size=pop, n_generations=gen, n_obj=n_obj,
    n_ref_dirs=12, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
    hotstart_individual=hotstart, instance=instance,
)
meta = result.metadata
frontier = meta.get("frontier", [])
out = {
    "f1": float(meta.get("f1", 0.0)),
    "f1_raw": float(meta.get("f1_raw", 0.0)),
    "f1_gbl": float(meta.get("f1_gbl", 1.0)),
    "f2": float(meta.get("f2", 0.0)),
    "f3": float(meta.get("f3", 0.0)),
    "n_selected": int(meta.get("n_selected", 0)),
    "n_frontier": len(frontier),
    "frontier_f1": [float(s.get("f1", 0)) for s in frontier],
    "frontier_f2": [float(s.get("f2", 0)) for s in frontier],
    "frontier_f3": [float(s.get("f3", 0)) for s in frontier],
    "selected": meta.get("selected", []),
    "t_actuals": meta.get("t_actuals", []),
    "phis_off_nadir": meta.get("phis_off_nadir", []),
    "constraint_feasible": bool(meta.get("constraint_feasible", True)),
    "n_constraints_failed": int(meta.get("n_constraints_failed", 0)),
}
with open(out_path, "w") as f:
    json.dump(out, f, default=str)
"""


def _materialize_tree(tmp_path_factory, stamp):
    d = tmp_path_factory.mktemp(f"p1_pin_tree_{stamp}")
    r = subprocess.run(
        ["git", "archive", "--format=tar", stamp, "src/sar_sim"],
        cwd=str(REPO), check=True, capture_output=True,
    )
    with tarfile.open(fileobj=io.BytesIO(r.stdout)) as tf:
        try:
            tf.extractall(str(d), filter="data")
        except TypeError:  # python < 3.12: no filter kwarg
            tf.extractall(str(d))
    return d / "src"


def _run_tree(tree_src, pkl, pop, gen, n_obj, out_path, script_path):
    r = subprocess.run(
        [sys.executable, str(script_path), str(tree_src), str(pkl),
         str(out_path), str(pop), str(gen), str(n_obj)],
        capture_output=True, text=True, timeout=3600,
    )
    assert r.returncode == 0, (
        f"fixture runner failed (tree={tree_src}):\n{r.stderr[-2000:]}"
    )


def _first_pkl(group):
    pkls = sorted((PAPER / "experiments" / "scenarios" / group).glob("*.pkl"))
    assert pkls, (
        f"no scenarios under experiments/scenarios/{group}: this pin, like "
        "verify_paper_numbers.py, needs the local scenario data"
    )
    return pkls[0]


def _default_scenario():
    """S1 always; plus one more density group so the pin is not a single-
    scenario sampler (review finding F2). S5 preferred, falls back in order."""
    for group in ("S5", "S4", "S3", "S2"):
        d = PAPER / "experiments" / "scenarios" / group
        if d.is_dir() and any(d.glob("*.pkl")):
            return [_first_pkl("S1"), _first_pkl(group)]
    return [_first_pkl("S1")]


@pytest.fixture(scope="session")
def stamp_tree(tmp_path_factory):
    return _materialize_tree(tmp_path_factory, STAMP)


@pytest.fixture(scope="session")
def fixture_script(tmp_path_factory):
    p = tmp_path_factory.mktemp("p1_pin_scripts") / "fixture_runner.py"
    p.write_text(FIXTURE_RUNNER, encoding="utf-8")
    return p


@pytest.mark.parametrize("n_obj", [2, 3])
def test_solver_tree_equivalence(stamp_tree, fixture_script, tmp_path, n_obj):
    full = os.environ.get("P1_PIN_FULL") == "1"
    pop, gen = (100, 200) if full else (24, 5)
    scenarios = _default_scenario() + ([_first_pkl("S4")] if full else [])
    # dedupe while keeping order (S4 may already be the fallback second group)
    seen = set()
    scenarios = [p for p in scenarios if not (p in seen or seen.add(p))]

    evidence = []
    for pkl in scenarios:
        out_old, out_new = tmp_path / "old.json", tmp_path / "new.json"
        _run_tree(stamp_tree, pkl, pop, gen, n_obj, out_old, fixture_script)
        _run_tree(REPO / "src", pkl, pop, gen, n_obj, out_new, fixture_script)
        with open(out_old, encoding="utf-8") as f:
            a = json.load(f)
        with open(out_new, encoding="utf-8") as f:
            b = json.load(f)

        drift = [k for k in VALUE_FIELDS if a[k] != b[k]]
        drift += [k for k in LIST_FIELDS if a[k] != b[k]]
        drift += [k for k in AUDIT_FIELDS if a[k] != b[k]]
        detail = {k: (a[k], b[k]) for k in drift}
        assert not drift, (
            f"value drift {pkl.name} n_obj={n_obj} stamp={STAMP} vs HEAD: {detail}"
        )

        entry = {"scenario": pkl.name, "n_obj": n_obj, "identical": True}

        # FULL mode: compare against the stored stamped entries too
        # (report-only: library-version drift may show as float dust here,
        #  which is environment, not code, and must not fail the pin).
        if full:
            result_dir = "moea_3obj" if n_obj == 3 else "moea_2obj"
            prog = json.loads(
                (PAPER / "experiments" / "results" / result_dir
                 / "_progress.json").read_text(encoding="utf-8"))
            stored = prog["completed"].get(f"{pkl.parent.name}/{pkl.name}")
            if stored is None:
                entry["stored_comparison"] = "no stored entry"
            else:
                deltas = {}
                for k in ("f1", "f1_raw", "f1_gbl", "f2", "f3"):
                    sv, nv = float(stored[k]), b[k]
                    deltas[k] = {"stored": sv, "rerun": nv,
                                 "rel": abs(nv - sv) / max(abs(sv), 1e-12)}
                entry["stored_comparison"] = deltas
        evidence.append(entry)

    if full:
        out = {
            "what": "paper1 solver caliber equivalence evidence",
            "stamp": STAMP,
            "head": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=str(REPO), text=True).strip()[:8],
            "budget": {"population_size": pop, "n_generations": gen},
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tree_vs_tree": "bit-identical on all value/list/audit fields",
            "results": evidence,
        }
        dest = PAPER / "review" / f"pin-equivalence-evidence-20261031-obj{n_obj}.json"
        dest.write_text(json.dumps(out, indent=2), encoding="utf-8")


def test_pin_discriminates_known_bad(tmp_path_factory, fixture_script, tmp_path):
    bad_tree = _materialize_tree(tmp_path_factory, BAD_STAMP)
    pkl = _first_pkl("S1")
    out_bad, out_new = tmp_path / "bad.json", tmp_path / "new.json"
    _run_tree(bad_tree, pkl, 24, 5, 3, out_bad, fixture_script)
    _run_tree(REPO / "src", pkl, 24, 5, 3, out_new, fixture_script)
    with open(out_bad, encoding="utf-8") as f:
        a = json.load(f)
    with open(out_new, encoding="utf-8") as f:
        b = json.load(f)
    drift = [k for k in VALUE_FIELDS if a[k] != b[k]]
    drift += [k for k in LIST_FIELDS if a[k] != b[k]]
    assert drift, (
        "negative control failed: known-bad stamp 681ced6b (pre-RDR066 "
        "f2/f3 double-count) produced no drift vs HEAD -- the pin is blind"
    )
