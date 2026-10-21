#!/usr/bin/env python3
"""Minimum-unit check for the delivered-caliber variant (ticket 50 phase 2).

Why a SECOND script: comparing an implementation against itself proves
nothing. This script re-derives ``f_Q_deliv`` for one family x one seed x one
demand point straight from the stored artifact and the raw manifest -- its own
window lookup, its own squint arithmetic, its own ground-range resolution --
and requires agreement with the implementation path to 1e-12. It also pins the
two anchors the formula spec owns, and exercises the branch that must FAIL:
STR has no task-level mode parameter, so a task-level request there raises.

Registered formula (formula-spec v1.9 section 8.17-10):

    f_Q,deliv = D / (2 * rho_req^2 * cos^2(psi_sel) * rho_rg)

Post-processing only: no solver run, no artifact write.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/verify_fq_deliv_minunit.py \
        [--family R3H] [--s 1.0] [--seed 300]

rc: 0 agreement within tolerance; 1 disagreement or a missing branch;
    2 the chosen unit has no instance in one of the required buckets.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))
sys.path.insert(0, str(FORK.parents[1] / "src"))
sys.path.insert(0, str(FORK / "scripts"))

from sss_core.duration import task_rho_ach            # noqa: E402
from sss_core.evaluator import SchedulingProblem      # noqa: E402
from sss_core.modes import Mode, ModeLibrary          # noqa: E402
from sss_core.nsga2 import load_manifest              # noqa: E402
from sss_core.quality import ground_range_resolution_m  # noqa: E402

V5 = FORK / "experiments" / "v5_results"
TOL = 1e-12


def s_name(s: float) -> str:
    return f"s{str(s).replace('.', '_')}"


def window_at_raw(task: dict, t: float) -> dict:
    """The stored window containing ``t`` -- read from the JSON, not TaskPlan."""
    if "windows" in task:
        for w in task["windows"]:
            if float(w["lo_s"]) <= t <= float(w["hi_s"]):
                return w
        raise SystemExit(f"t={t} outside every stored window")
    # synthetic single-window manifest: the fields sit on the task itself
    return {"lo_s": task["t_start_s"], "hi_s": task["t_end_s"],
            "t_ca_s": task["t_ca_s"], "r0_m": task.get("r0_m")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", default="R3H")
    ap.add_argument("--s", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=300)
    args = ap.parse_args(argv)

    art_path = (V5 / "sweep" / s_name(args.s)
                / f"pilot_{args.family}_seed{args.seed}.json")
    if not art_path.is_file():
        print(f"ABORT: no artifact {art_path}", file=sys.stderr)
        return 2
    art = json.loads(art_path.read_text(encoding="utf-8"))
    manifest = load_manifest(V5 / "scenarios" / Path(art["manifest"]).name)
    for t in manifest["tasks"]:
        if t.get("rho_req_m") is not None:
            t["rho_req_m"] = args.s * float(t["rho_req_m"])

    lib = ModeLibrary.from_fixture()
    geo = lib.geo
    d_m = geo.D_m
    rho_rg_impl = ground_range_resolution_m(lib)
    # independent derivation: B_rg = c/(2*rho_design*sin(theta_i)) substituted
    # into rho_rg = c/(2*B_rg*sin(theta_i)) leaves rho_design identically
    rho_rg_indep = geo.rho_design_m
    print(f"# rho_rg: implementation {rho_rg_impl!r}  independent "
          f"{rho_rg_indep!r}  (identity: both reduce to rho_design)")

    sp = SchedulingProblem(manifest, lib)
    rec = art["front"][0]

    import build_reading_ledger_l8 as impl   # implementation side of the compare

    picks: dict = {}
    counts = {"STR": 0, "SLS": 0, "SPT": 0}
    for k, start in rec["starts"].items():
        idx = int(k)
        plan = sp.plans[idx]
        counts[plan.mode.name] += 1
        if plan.mode is Mode.STR or plan.rho_req_m is None:
            continue
        picks.setdefault(plan.mode.name, (idx, float(start)))
    print(f"# served instances by mode (record 0): {counts}")

    failures = []

    # ---- the two defined buckets -------------------------------------------
    for mode_name in ("SLS", "SPT"):
        if mode_name not in picks:
            print(f"ABORT: no served {mode_name} instance in this unit",
                  file=sys.stderr)
            return 2
        idx, start = picks[mode_name]
        plan = sp.plans[idx]

        # implementation path
        got_impl, psi_impl = impl.deliv_value(plan, start, lib, rho_rg_impl, d_m)

        # independent path: raw window -> inline squint -> formula
        task_raw = manifest["tasks"][idx]
        w = window_at_raw(task_raw, start)
        r0 = geo.R0_m if w.get("r0_m") is None else float(w["r0_m"])
        psi_indep = math.atan(geo.vs_mps * (start - float(w["t_ca_s"])) / r0)
        c = math.cos(psi_indep)
        f_indep = d_m / (2.0 * float(task_raw["rho_req_m"]) ** 2 * c * c
                         * rho_rg_indep)

        diff = abs(got_impl - f_indep)
        rel = diff / abs(f_indep)
        print(f"# {mode_name} task {idx}: f_Q_deliv impl {got_impl!r}  "
              f"independent {f_indep!r}  |diff| {diff:.3e}  rel {rel:.3e}")
        print(f"#   psi_sel impl {math.degrees(psi_impl):.9f} deg  "
              f"independent {math.degrees(psi_indep):.9f} deg")
        if diff > TOL:
            failures.append(f"{mode_name} task {idx}: |diff| {diff:.3e} > {TOL}")

    # ---- the branch that must raise ----------------------------------------
    if not counts["STR"]:
        print("ABORT: no served STR instance to exercise the no-domain branch",
              file=sys.stderr)
        return 2
    try:
        task_rho_ach(Mode.STR, 0.5, 0.0, lib)
    except ValueError as exc:
        print(f"# STR task-level request raises as registered: {exc}")
    else:
        failures.append("task_rho_ach(STR) returned a value instead of raising")
        print("# STR task-level request DID NOT raise")

    # ---- anchors owned by the formula spec ---------------------------------
    rho_req, psi = 0.42, math.radians(12.0)
    c = math.cos(psi)
    f12 = d_m / (2.0 * rho_req ** 2 * c * c * rho_rg_indep)
    f0 = d_m / (2.0 * rho_req ** 2 * rho_rg_indep)
    ratio = f12 / f0
    print(f"# anchor sec^2(12 deg): ratio {ratio!r} vs registered 1.0452")
    if abs(ratio - 1.0452) > 5e-5:
        failures.append(f"sec^2(12 deg) ratio {ratio!r} != 1.0452")
    # rho_req = D/2 at zero squint reduces to 2/(rho_rg*D) exactly
    f_eq = d_m / (2.0 * (d_m / 2.0) ** 2 * rho_rg_indep)
    closed = 2.0 / (rho_rg_indep * d_m)
    print(f"# anchor rho_req=D/2, psi=0: {f_eq!r} vs 2/(rho_rg*D) {closed!r} "
          f"|diff| {abs(f_eq - closed):.3e}")
    if abs(f_eq - closed) > TOL:
        failures.append("the rho_req=D/2 closed form does not reproduce")

    if failures:
        print("VERDICT: FAIL")
        for f in failures:
            print(f"FAIL   {f}")
        return 1
    print(f"VERDICT: the two paths agree within {TOL} on every checked branch")
    return 0


if __name__ == "__main__":
    sys.exit(main())
