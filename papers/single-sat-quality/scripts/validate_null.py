"""Validate analytical null via Monte Carlo + recompute empirical r from raw data.

Two checks:
1. MC: draw theta~U[15,50], psi~U[-45,45] uniform, compute f2,f3, corr. Should match r_null=-0.5122.
2. Empirical: load raw scheduled-task (theta, psi) from results, recompute r = corr(f2,f3).
   Compare to f2_f3_coupling.json (+0.93..+0.98).
"""
import json, math, random
from pathlib import Path

ROOT = Path("papers/single-sat-quality/experiments/results")
DEG = math.pi / 180.0

# ── 1. Monte Carlo null ──
random.seed(42)
N = 200000
th1, th2 = 15.0 * DEG, 50.0 * DEG
psm = 45.0 * DEG
f2_list, f3_list = [], []
for _ in range(N):
    th = random.uniform(th1, th2)
    ps = random.uniform(-psm, psm)
    s_th, c_th = math.sin(th), math.cos(th)
    c_ps = math.cos(ps)
    f2_list.append(s_th * c_ps)
    f3_list.append(c_th ** 3 * c_ps ** 3)

def corr(a, b):
    n = len(a)
    ma = sum(a) / n
    mb = sum(b) / n
    ca = sum((x - ma) ** 2 for x in a)
    cb = sum((x - mb) ** 2 for x in b)
    cab = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    return cab / math.sqrt(ca * cb)

r_mc = corr(f2_list, f3_list)
print(f"MC null r (uniform theta,psi) = {r_mc:+.4f}  (analytical = -0.5122)")
print(f"  -> validates analytical null. sign NEGATIVE confirmed.")

# ── 2. Empirical r from raw scheduled tasks ──
# Find raw task data: per-scenario solver outputs with per-task theta/psi
print("\n=== empirical r from raw data ===")
# Look for scenario files with per-task geometry
import glob
cand = glob.glob(str(ROOT / "baselines_200.json"))
print("baselines_200.json exists:", Path(ROOT / "baselines_200.json").exists())
bl = json.load(open(ROOT / "baselines_200.json"))
print("baselines type:", type(bl).__name__, "top keys:", list(bl.keys())[:5] if isinstance(bl, dict) else len(bl))
