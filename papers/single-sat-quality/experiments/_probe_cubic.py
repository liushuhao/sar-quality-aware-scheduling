"""Full sweep: 10s grid linear vs cubic interp vs precise, all 102 solutions.

Pickle fixtures are this repo's own scenario files (trusted local data).
"""
import pickle, sys, json
from pathlib import Path
import numpy as np

ROOT = Path(r"D:/hermes/my-workspace/projects/planning paper")
PAPER = ROOT / "papers/single-sat-quality"
sys.path.insert(0, str(ROOT / "src"))
from sar_sim.solver.types import (
    build_agile_instance_from_scenario, precompute_geometry,
    _lat_lon_to_ecef, _satellite_body_frame,
)
SLEW = 0.0524

def los_sep(ta, tb, sa, sb, tmap, tida, tidb):
    pa=_lat_lon_to_ecef(tmap[tida].lat,tmap[tida].lon); pb=_lat_lon_to_ecef(tmap[tidb].lat,tmap[tidb].lon)
    la=pa-sa; lb=pb-sb
    d=float(np.dot(la,lb))/(float(np.linalg.norm(la))*float(np.linalg.norm(lb)))
    return float(np.arccos(np.clip(d,-1,1)))

def lin(gt,gp,t):
    step=gt[1]-gt[0]; k=max(0,min(int((t-gt[0])/step),len(gt)-2))
    a=(t-gt[k])/(gt[k+1]-gt[k]); return (1-a)*gp[k]+a*gp[k+1]

def cub(gt,gp,t):
    step=gt[1]-gt[0]; k=max(1,min(int((t-gt[0])/step),len(gp)-3))
    ts=gt[k-1:k+3]; p=np.zeros(3)
    for j in range(4):
        w=1.0
        for m in range(4):
            if m!=j: w*=(t-ts[m])/(ts[j]-ts[m])
        p+=w*gp[k-1+j]
    return p

prog=json.load(open(PAPER/"experiments/results/_snapshot_audit.json",encoding="utf-8"))["completed"]
lin_all=[]; cub_all=[]; fn_lin=0; fn_cub=0
for key,e in prog.items():
    data=pickle.load(open(PAPER/"experiments/scenarios"/key,"rb"))
    alt=float(data["satellite"]["altitude_km"])*1000
    inst=build_agile_instance_from_scenario(data,max_slew_rate=SLEW,settle_time=5.0,altitude_m=alt)
    precompute_geometry(inst,step_s=10.0)
    gt=inst.sat_position_cache.times; gp=inst.sat_position_cache.positions; tmap=inst.target_map
    sel=e["selected"]; ta=e["t_actuals"]; phis=e["phis_off_nadir"]
    order=sorted(sel,key=lambda i:float(ta[sel.index(i)]))
    for k in range(len(order)-1):
        a,b=order[k],order[k+1]
        ta_=float(ta[sel.index(a)]); tb_=float(ta[sel.index(b)])
        spa=_satellite_body_frame(ta_,inst)[3]; spb=_satellite_body_frame(tb_,inst)[3]
        tida=inst.tasks[a].target_id; tidb=inst.tasks[b].target_id
        ep=los_sep(ta_,tb_,spa,spb,tmap,tida,tidb)
        el=abs(los_sep(ta_,tb_,lin(gt,gp,ta_),lin(gt,gp,tb_),tmap,tida,tidb)-ep)/SLEW
        ec=abs(los_sep(ta_,tb_,cub(gt,gp,ta_),cub(gt,gp,tb_),tmap,tida,tidb)-ep)/SLEW
        lin_all.append(el); cub_all.append(ec)
lin_all=np.array(lin_all); cub_all=np.array(cub_all)
print(f"transitions: {len(lin_all)}")
print(f"linear 10s: max={lin_all.max()*1000:.3f}ms p99={np.percentile(lin_all,99)*1000:.3f}ms mean={lin_all.mean()*1000:.4f}ms")
print(f"cubic  10s: max={cub_all.max()*1000:.4f}ms p99={np.percentile(cub_all,99)*1000:.4f}ms mean={cub_all.mean()*1000:.5f}ms")
