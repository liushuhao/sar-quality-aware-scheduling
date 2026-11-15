import pickle, sys, json
sys.path.insert(0, 'src')
from sar_sim.solver.moea import moea_solver
from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry
import numpy as np

data = pickle.load(open('papers/single-sat-quality/experiments/scenarios/S1/S1-A_seed07.pkl', 'rb'))
windows, targets = data["windows"], data["targets"]
instance = build_agile_instance_from_scenario(data, max_slew_rate=0.0524, settle_time=5.0)
precompute_geometry(instance, step_s=10.0)
gbl = baseline_b1(windows, targets, max_slew_rate=0.0524, settle_time=5.0,
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
result = moea_solver(windows, targets, population_size=100, n_generations=200, n_obj=2,
                     n_ref_dirs=12, max_slew_rate=0.0524, settle_time=5.0,
                     hotstart_individual=hotstart, instance=instance)
m = result.metadata
print('f1=%.6f n_sel=%d n_frontier=%d' % (m.get('f1', 0), m.get('n_selected', 0), m.get('n_frontier', 0)))
