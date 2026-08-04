"""Generate one test scenario for verification."""
import sys, pickle
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from generate_all_scenarios import generate_one_scenario, SENTINEL1, OUTPUT_ROOT

scenario = generate_one_scenario(
    n_targets=20, seed=0, sat_params=SENTINEL1,
    look_direction="both", dist_type="uniform",
)
out = OUTPUT_ROOT / "S1" / "S1-A_seed00.pkl"
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "wb") as f:
    pickle.dump(scenario, f, protocol=pickle.HIGHEST_PROTOCOL)

stats = scenario["stats"]
print(f"Generated {out.name}: "
      f"{stats['n_with_windows']}/{stats['n_targets_total']} visible, "
      f"{stats['total_windows']} windows, "
      f"{stats['compute_time_s']:.1f}s")
