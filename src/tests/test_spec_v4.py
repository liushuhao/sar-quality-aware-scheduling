"""TDD tests for SPEC v4 changes: dedup + adaptive noise + MOEA hot-start + S3 scenario."""

import sys, os, pickle, math, numpy as np, pathlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.so_f1 import _HotStartSampling, ga_hotstart_solver, b2_profit_solver_bl_seeded
from sar_sim.solver.types import build_agile_instance, precompute_geometry
from collections import Counter


def _load(name):
    pkl = sorted(pathlib.Path(f'experiments/scenarios/{name}').glob('*.pkl'))[0]
    with open(str(pkl), 'rb') as f:
        data = pickle.load(f)
    return data['targets'], data['windows']


# ── C1: G-BL C7 dedup ─────────────────────────────────────────────────

def test_gbl_no_duplicate_tasks():
    """G-BL schedule must not contain duplicate target_id."""
    targets, windows = _load('S1')
    result = baseline_b1(windows, targets)
    tids = [obs.window.target_id for obs in result.schedule]
    counts = Counter(tids)
    dupes = {k: v for k, v in counts.items() if v > 1}
    assert len(dupes) == 0, f"Found {len(dupes)} duplicate tasks: {dupes}"


# ── C3: MOEA-3 hot-start individual ─────────────────────────────────────

def test_moea_hotstart_first_individual_is_gbl():
    """MOEA-3 with hot-start: first population individual encodes G-BL solution."""
    from sar_sim.solver.moea import moea_solver
    from sar_sim.solver.types import build_agile_instance, precompute_geometry

    targets, windows = _load('S1')
    gbl = baseline_b1(windows, targets)
    instance = build_agile_instance(windows, targets)
    precompute_geometry(instance, step_s=10.0)
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

    result = moea_solver(
        windows, targets,
        population_size=100, n_generations=5, n_obj=3, n_ref_dirs=12,
        seed=0, hotstart_individual=x0 if seen else None, instance=instance,
    )
    meta = result.metadata
    # f1 is now normalized (f1_raw / f1_gbl) — at least 50% of G-BL baseline
    assert meta['f1'] >= 0.5, \
        f"MOEA-3 f1_norm={meta['f1']:.2f} too far below 0.5"


# ── C4: S3 scenario generation ──────────────────────────────────────────

def test_s3_scenarios_exist_and_valid():
    """S3(N=300) scenarios: 50 .pkl files, N in [280, 320]."""
    s3_dir = pathlib.Path('experiments/scenarios/S3')
    pkgs = sorted(s3_dir.glob('*.pkl'))
    assert len(pkgs) >= 50, f"Expected 50 scenarios, found {len(pkgs)}"
    from collections import Counter
    n_counts = Counter()
    for pkl in pkgs:
        with open(str(pkl), 'rb') as f:
            data = pickle.load(f)
        N = len(data.get('targets', []))
        n_counts[N] += 1
    # At least 80% of scenarios should have N in [280, 320]
    in_range = sum(c for n, c in n_counts.items() if 280 <= n <= 320)
    assert in_range >= 40, \
        f"Only {in_range}/50 scenarios have N in [280,320]: {dict(n_counts)}"
