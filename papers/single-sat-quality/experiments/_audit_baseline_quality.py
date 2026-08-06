"""Data-quality audit: re-run G-BL (b1) and G-SM (b3) per scenario and
independently verify C1-C4 + out-of-window on the decoded schedule.

Pickle fixtures are this repo's own scenario files (trusted).
"""
import pickle, sys
from pathlib import Path
from collections import defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers/single-sat-quality"
sys.path.insert(0, str(ROOT / "src"))

from sar_sim.solver.baselines import baseline_b1, baseline_b3
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry, compute_full_attitude
from sar_sim.verification.constraints import ConstraintVerifier

SLEW, SETTLE = 0.0524, 5.0


def audit(classes):
    stats = {s: defaultdict(int) for s in ("b1", "b3")}
    worst = {s: 0.0 for s in ("b1", "b3")}
    nsel = {s: [] for s in ("b1", "b3")}
    n = 0
    for cls in classes:
        for pkl in sorted((PAPER / "experiments/scenarios" / cls).glob("*.pkl")):
            data = pickle.load(open(pkl, "rb"))
            inst = build_agile_instance_from_scenario(
                data, max_slew_rate=SLEW, settle_time=SETTLE,
                altitude_m=float(data.get("satellite", {}).get("altitude_km", 693)) * 1000.0)
            precompute_geometry(inst, step_s=10.0)
            t2i = {t.target_id: i for i, t in enumerate(inst.tasks)}
            N = inst.N
            n += 1
            for solver, fn in (("b1", baseline_b1), ("b3", baseline_b3)):
                res = fn(data["windows"], data["targets"],
                         geom_cache=inst.geom_cache, instance=inst)
                phi = np.zeros(N); ta = np.zeros(N); sel = []; oow = 0
                for obs in res.schedule:
                    i = t2i.get(obs.window.target_id)
                    if i is None:
                        continue
                    sel.append(i)
                    t = obs.t_actual_start.timestamp()
                    ta[i] = t
                    roll, _, _ = compute_full_attitude(inst.tasks[i], t, 1.0, inst)
                    phi[i] = roll
                    wt = inst.tasks[i].window_times
                    if wt and not any(ws <= t <= we for ws, we in wt):
                        oow += 1
                rep = ConstraintVerifier(inst).verify_solution(sel, phi, t_actual=ta)
                s = stats[solver]
                s["scen"] += 1
                c2, c1 = rep.results["C2"], rep.results["C1"]
                if not c2.passed:
                    s["c2"] += 1
                    worst[solver] = max(worst[solver],
                                        max((v.magnitude for v in c2.violations), default=0.0))
                if not c1.passed: s["c1"] += 1
                if oow: s["oow"] += 1
                if not rep.results["C3"].passed: s["c3"] += 1
                if not rep.results["C4"].passed: s["c4"] += 1
                nsel[solver].append(len(sel))
    print(f"scenarios audited: {n}")
    for solver in ("b1", "b3"):
        s = stats[solver]
        arr = np.array(nsel[solver])
        print(f"  {solver}: C2fail={s['c2']} C1fail={s['c1']} OOWscen={s['oow']} "
              f"C3fail={s['c3']} C4fail={s['c4']} worstC2={worst[solver]:.4f}s | "
              f"nsel mean={arr.mean():.1f} min={arr.min()} max={arr.max()}")


if __name__ == "__main__":
    classes = sys.argv[1].split(",") if len(sys.argv) > 1 else ["S1", "S2", "S3", "S4"]
    audit(classes)
