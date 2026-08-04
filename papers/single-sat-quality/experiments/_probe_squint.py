"""C1 squint: GeomCache linear interp vs precise compute_full_attitude.

Checks the dangerous direction on every selected observation of every saved
solution: cached psi_sq passes (<=45deg) but precise psi_sq fails. Also
measures linear error and what cubic interpolation would give.

Pickle fixtures are this repo's own scenario files (trusted local data).
"""
import json, pickle, sys, bisect
from pathlib import Path
import numpy as np

ROOT = Path(r"D:/hermes/my-workspace/projects/planning paper")
PAPER = ROOT / "papers/single-sat-quality"
sys.path.insert(0, str(ROOT / "src"))
from sar_sim.solver.types import (
    build_agile_instance_from_scenario, precompute_geometry,
    compute_full_attitude,
)
MAX_SQ = np.radians(45.0)

def lin_at(arr_col, t_grid, t):
    if t <= t_grid[0]: return arr_col[0]
    if t >= t_grid[-1]: return arr_col[-1]
    k = bisect.bisect_left(t_grid, t) - 1
    k = max(0, min(k, len(t_grid)-2))
    a = (t-t_grid[k])/(t_grid[k+1]-t_grid[k])
    return (1-a)*arr_col[k]+a*arr_col[k+1]

def cub_at(arr_col, t_grid, t):
    if t <= t_grid[0]: return arr_col[0]
    if t >= t_grid[-1]: return arr_col[-1]
    k = bisect.bisect_left(t_grid, t) - 1
    if k < 1 or k >= len(t_grid)-2:
        a=(t-t_grid[k])/(t_grid[k+1]-t_grid[k]); return (1-a)*arr_col[k]+a*arr_col[k+1]
    ts=t_grid[k-1:k+3]; v=0.0
    for j in range(4):
        w=1.0
        for m in range(4):
            if m!=j: w*=(t-ts[m])/(ts[j]-ts[m])
        v+=w*arr_col[k-1+j]
    return v

prog=json.load(open(PAPER/"experiments/results/_snapshot_audit.json",encoding="utf-8"))["completed"]
lin_err=[]; cub_err=[]; fn_lin=[]; max_sq=0.0
for key,e in prog.items():
    data=pickle.load(open(PAPER/"experiments/scenarios"/key,"rb"))
    alt=float(data["satellite"]["altitude_km"])*1000
    inst=build_agile_instance_from_scenario(data,max_slew_rate=0.0524,settle_time=5.0,altitude_m=alt)
    precompute_geometry(inst,step_s=10.0)
    sel=e["selected"]; ta=e["t_actuals"]
    for i,t in zip(sel,ta):
        t=float(t)
        gc=inst.geom_cache.cache[i]
        tg=gc[:,0]; psi_col=gc[:,2]
        psi_lin=lin_at(psi_col,tg,t)
        psi_cub=cub_at(psi_col,tg,t)
        _,_,psi_pre=compute_full_attitude(inst.tasks[i],t,1.0,inst)
        psi_pre=abs(psi_pre)
        lin_err.append(abs(psi_lin-psi_pre))
        cub_err.append(abs(psi_cub-psi_pre))
        max_sq=max(max_sq,psi_pre)
        if psi_lin<=MAX_SQ and psi_pre>MAX_SQ:
            fn_lin.append((key,i,np.degrees(psi_pre),np.degrees(psi_lin)))

lin_err=np.array(lin_err); cub_err=np.array(cub_err)
print(f"observations: {len(lin_err)}")
print(f"max |psi_sq| over all obs: {np.degrees(max_sq):.3f} deg (limit 45)")
print(f"linear 10s: max err={np.degrees(lin_err.max())*3600:.2f} arcsec  p99={np.degrees(np.percentile(lin_err,99))*3600:.2f} arcsec  mean={np.degrees(lin_err.mean())*3600:.3f} arcsec")
print(f"cubic  10s: max err={np.degrees(cub_err.max())*3600:.4f} arcsec")
print(f"FALSE NEGATIVES (lin pass, precise fail): {len(fn_lin)}")
for x in fn_lin[:20]: print("  ",x)
