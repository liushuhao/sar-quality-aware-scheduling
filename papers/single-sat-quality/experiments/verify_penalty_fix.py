#!/usr/bin/env python3
"""Verify C2 penalty fix on dense S2 scenario (was C2-violating pre-fix)."""
import sys, pickle, time
from pathlib import Path
import numpy as np
sys.path.insert(0, 'D:/hermes/my-workspace/projects/planning-paper/src')
from sar_sim.solver.moea import moea_solver
from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry
from sar_sim.verification.constraints import ConstraintVerifier

with open('experiments/scenarios/S2/S2-C_seed02.pkl', 'rb') as f:
    data = pickle.load(f)
inst = build_agile_instance_from_scenario(data, max_slew_rate=0.0524, settle_time=5.0)
precompute_geometry(inst, step_s=10.0)

gbl = baseline_b1(data['windows'], data['targets'], max_slew_rate=0.0524, settle_time=5.0,
                  geom_cache=inst.geom_cache, instance=inst)
t2i = {t.target_id: i for i, t in enumerate(inst.tasks)}
x0 = np.zeros(2 * inst.N); seen = set()
for obs in gbl.schedule:
    idx = t2i.get(obs.window.target_id)
    if idx is not None and idx not in seen:
        seen.add(idx); x0[idx] = 1.0
        span = inst.tasks[idx].time_span
        tau = (obs.t_actual_start.timestamp() - inst.tasks[idx].t_earliest) / span if span > 0 else 0.5
        x0[inst.N + idx] = max(0.0, min(1.0, tau))
hotstart = x0 if seen else None

t0 = time.time()
result = moea_solver(data['windows'], data['targets'], population_size=100, n_generations=200, n_obj=2,
                     max_slew_rate=0.0524, settle_time=5.0, hotstart_individual=hotstart, instance=inst)
meta = result.metadata
print(f'S2-C_seed02 (fixed): f1={meta["f1"]:.3f} nsel={meta["n_selected"]} '
      f'inf_filt={meta["n_infeasible_filtered"]} ({time.time()-t0:.0f}s)')

N = inst.N; phi = np.zeros(N); t = np.zeros(N)
for i, tt, p in zip(meta['selected'], meta['t_actuals'], meta['phis_off_nadir']):
    phi[i] = p; t[i] = tt
rep = ConstraintVerifier(inst).verify_solution(meta['selected'], phi, t_actual=t)
fails = [c for c in ['C1', 'C2', 'C3', 'C4'] if not rep.results[c].passed]
print('audit:', 'CLEAN' if not fails else f'FAIL {fails}')
