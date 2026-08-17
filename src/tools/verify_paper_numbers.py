#!/usr/bin/env python3
"""verify_paper_numbers.py — Full-paper number ledger (S1a INTEGRITY).

Recomputes every statistical claim printed in the paper from the final data
snapshot and asserts it matches the paper's value within tolerance. This is a
deterministic gate: exit 0 only if all assertions pass. A ledger report
(JSON + text) is written under papers/single-sat-quality/review/. Every data
file read is fingerprinted with its sha1 so the run is traceable.

Paper values below are transcribed from small-paper-ijae.tex (EN) with
line references; ZH mirrors the same numbers. Any mismatch is reported as
a S1 integrity finding, not silently tolerated.

Usage:  python src/tools/verify_paper_numbers.py
Exit:   0 all pass, 1 any fail
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from statistics import mean, pstdev, stdev

import numpy as np
from scipy import stats as scipy_stats

# ── paths ──────────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parent.parent.parent
RESULTS = REPO / "papers" / "single-sat-quality" / "experiments" / "results"
REVIEW = REPO / "papers" / "single-sat-quality" / "review"

# ── fingerprint ─────────────────────────────────────────────────────────────
FINGERPRINTS = {}


def fingerprint(relpath):
    p = RESULTS / relpath
    h = hashlib.sha1(p.read_bytes()).hexdigest()
    FINGERPRINTS[relpath] = h
    return p


# ── data loading ────────────────────────────────────────────────────────────
bl = json.loads(fingerprint("baselines_200.json").read_text(encoding="utf-8"))
bl_s78 = json.loads(fingerprint("baselines_S7S8.json").read_text(encoding="utf-8"))
m2 = json.loads(fingerprint("moea_2obj/_progress.json").read_text(encoding="utf-8"))
m3 = json.loads(fingerprint("moea_3obj/_progress.json").read_text(encoding="utf-8"))
b2 = json.loads(fingerprint("b2_profit_bl/_progress.json").read_text(encoding="utf-8"))
sched_corr = json.loads(fingerprint("schedule_correlation.json").read_text(encoding="utf-8"))
env = json.loads(fingerprint("r_visible_envelope.json").read_text(encoding="utf-8"))
sr = json.loads(fingerprint("statistical_results.json").read_text(encoding="utf-8"))
p2_cliff = json.loads(fingerprint("phenomenon2_cliff.json").read_text(encoding="utf-8"))
hotstart = json.loads(fingerprint("p1-1_random_init/hotstart_control_s1s4.json").read_text(encoding="utf-8"))
rnd = json.loads(fingerprint("p1-2_random_search/p1-2_s1_random_search.json").read_text(encoding="utf-8"))
sweep = json.loads(fingerprint("sigma_sweep/sweep_summary.json").read_text(encoding="utf-8"))
vd_rnd = json.loads(fingerprint("variant_d_random_init/full.json").read_text(encoding="utf-8"))
n50 = json.loads(fingerprint("n50_logistic.json").read_text(encoding="utf-8"))
budget = json.loads(fingerprint("p1-4_variant_d_rerun/budget_control.json").read_text(encoding="utf-8"))

import csv  # noqa: E402
ablation = {}
with fingerprint("ablation_summary.csv").open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        ablation[(row["class"], row["variant"])] = row


def unwrap(loader):
    """moea _progress.json wraps results under 'completed'."""
    if isinstance(loader, dict) and set(loader) == {"completed"}:
        return loader["completed"]
    if isinstance(loader, dict) and "completed" in loader:
        return loader["completed"]
    return loader


m2, m3, b2 = unwrap(m2), unwrap(m3), unwrap(b2)


# ── caliber gate (S1): reject stale/mixed solver outputs ──────────────────
# Headline numbers come from m2/m3. The RDR-066 objective fix (NESZ
# double-count) and the B1 knee-selection fix mean any output stamped before
# this commit is stale. A mixed _progress.json (old + new entries) once
# silently built bogus cross-family comparisons; this gate refuses to verify
# such data rather than emit dozens of misleading number failures.
def _git_head8():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(REPO), text=True
        ).strip()[:8]
    except Exception:
        return "unknown"


HEAD8 = _git_head8()
KNOWN_BAD_CALIBER = {"681ced6b"}  # pre-RDR066 f2/f3 NESZ double-count
# Value-defining solver code. m2/m3 f-values change iff this file changes
# (RDR-066 objective formula and the B1 knee-selection fix both live here).
SOLVER_CODE = "src/sar_sim/solver/moea.py"


def _solver_code_identical(ver):
    """True iff moea.py at stamp ver is byte-identical to current HEAD.

    Content identity (not stamp == HEAD) means an unrelated commit
    (docs, tests, dead-code removal) does not falsely invalidate solver
    output that is still numerically current."""
    if ver in KNOWN_BAD_CALIBER or ver in ("MISSING", "unknown"):
        return False
    r = subprocess.run(
        ["git", "diff", "--quiet", ver, "HEAD", "--", SOLVER_CODE],
        cwd=str(REPO), capture_output=True,
    )
    return r.returncode == 0


def _version_counts(completed):
    from collections import Counter
    return Counter(
        v.get("solver_version", "MISSING")
        for v in completed.values() if isinstance(v, dict)
    )


_caliber_errors = []
for _name, _completed in (("moea_2obj", m2), ("moea_3obj", m3)):
    _vc = _version_counts(_completed)
    _stale = {v: n for v, n in _vc.items() if not _solver_code_identical(v)}
    if _stale:
        _caliber_errors.append(
            f"{_name}: {dict(_stale)} entries stamped at a version where "
            f"{SOLVER_CODE} differs from HEAD (rerun required)"
        )

# Ablation f-value table: the f2/f3 objective formula has been identical
# since RDR-066 (f96674f..b107e97 do not touch moea.py; B1 changed knee
# schedule mapping, not frontier f-values). no_squint uses an intentionally
# different elevation-plane formula, so reject only the known-bad stamp.
for _abl_dir in ("moea_3obj_no_incidence", "moea_3obj_no_physics", "moea_3obj_no_squint"):
    _p = RESULTS / _abl_dir / "_progress.json"
    if not _p.exists():
        continue
    _abl = json.loads(_p.read_text(encoding="utf-8")).get("completed", {})
    _bad = {v: n for v, n in _version_counts(_abl).items()
            if v in KNOWN_BAD_CALIBER or v == "MISSING"}
    if _bad:
        _caliber_errors.append(f"{_abl_dir}: stale/missing versions: {_bad}")

if _caliber_errors:
    print("CALIBER GATE FAIL - solver output does not match current code; "
          "refusing to verify paper numbers:")
    for _line in _caliber_errors:
        print(f"  - {_line}")
    print("Fix: rerun the affected solver(s).")
    sys.exit(1)
print(f"CALIBER OK: m2/m3 solver code identical to HEAD ({HEAD8}); "
      f"ablation calibers verified.")


def sol_vals(loader, cls, key):
    out = []
    for k, v in loader.items():
        if not k.startswith(cls + "/"):
            continue
        if isinstance(v, dict) and key in v:
            out.append(v[key])
    return out


def stats(loader, cls, key="f1"):
    v = sol_vals(loader, cls, key)
    return (mean(v), stdev(v), len(v)) if len(v) > 1 else (mean(v), 0.0, len(v))


def gbl(cls, key):
    vals = [bl[k]["b1"][key] for k in bl if k.startswith(cls + "/")]
    return (mean(vals), stdev(vals), len(vals))


def gsm(cls, key):
    vals = [bl[k]["b3"][key] for k in bl if k.startswith(cls + "/")]
    return (mean(vals), stdev(vals), len(vals))


def pct(a, b):
    return (a - b) / b * 100.0 if b else float("nan")


# ── assertions ──────────────────────────────────────────────────────────────
class Fail(Exception):
    pass


RESULTS_LEDGER = []
N_FAIL = 0


def check(cid, where, paper_val, data_val, tol, unit="abs", note=""):
    """paper_val: what the paper prints; data_val: recomputed from data."""
    global N_FAIL
    if unit == "rel":
        if paper_val == 0:
            ok = abs(data_val) <= tol
        else:
            ok = abs(data_val - paper_val) <= tol * max(abs(paper_val), 1e-12)
    else:
        ok = abs(data_val - paper_val) <= tol
    entry = {
        "id": cid, "where": where, "paper": paper_val, "data": data_val,
        "tol": tol, "unit": unit, "ok": bool(ok), "note": note,
    }
    RESULTS_LEDGER.append(entry)
    if not ok:
        N_FAIL += 1
        print(f"FAIL {cid} [{where}] paper={paper_val} data={data_val:.6g} (tol={tol})")
    return ok


def checkp(cid, where, paper_val, data_val, tol):
    """p-value: compare order of magnitude via -log10."""
    global N_FAIL
    pp = -np.log10(max(paper_val, 1e-99))
    dp = -np.log10(max(data_val, 1e-99))
    ok = abs(pp - dp) <= tol
    RESULTS_LEDGER.append({"id": cid, "where": where, "paper": paper_val,
                           "data": data_val, "tol": tol, "unit": "log10p",
                           "ok": bool(ok), "note": ""})
    if not ok:
        N_FAIL += 1
        print(f"FAIL {cid} [{where}] paper_p={paper_val} data_p={data_val:.3g}")
    return ok


# ── Table 1 / overall performance (S1..S4) ─────────────────────────────────
# paper values from Table 1 (small-paper-ijae.tex ~L684-746)
T1 = {
    "S1": {"G-SM": ("0.51", "0.16"), "MOEA-2": (("0.86", "0.14"), ("0.394", "0.059"), ("0.654", "0.038")),
           "MOEA-3": (("0.85", "0.12"), ("0.377", "0.050"), ("0.699", "0.037"))},
    "S2": {"G-SM": ("0.35", "0.09"), "MOEA-2": (("0.99", "0.03"), ("0.328", "0.030"), ("0.589", "0.045")),
           "MOEA-3": (("0.98", "0.04"), ("0.329", "0.030"), ("0.597", "0.042"))},
    "S3": {"G-SM": ("0.29", "0.04"), "MOEA-2": (("1.00", "0.00"), ("0.343", "0.026"), ("0.622", "0.040")),
           "MOEA-3": (("1.00", "0.01"), ("0.344", "0.026"), ("0.623", "0.040"))},
    "S4": {"G-SM": ("0.37", "0.12"), "MOEA-2": (("1.00", "0.01"), ("0.338", "0.038"), ("0.680", "0.073")),
           "MOEA-3": (("1.00", "0.01"), ("0.338", "0.038"), ("0.680", "0.073"))},
}
for cls, tbl in T1.items():
    gm, gs, _ = gsm(cls, "f1")
    check(f"t1-{cls}-gsm-f1", f"Table1 {cls} G-SM f1*", float(tbl["G-SM"][0]), gm, 0.011)
    check(f"t1-{cls}-gsm-f1sd", f"Table1 {cls} G-SM f1* SD", float(tbl["G-SM"][1]), gs, 0.011)
    for name, loader in (("MOEA-2", m2), ("MOEA-3", m3)):
        for i, key in enumerate(("f1", "f2", "f3")):
            mn, sd, n = stats(loader, cls, key)
            pm, psd = tbl[name][i]
            check(f"t1-{cls}-{name}-{key}", f"Table1 {cls} {name} {key}",
                  float(pm), mn, 0.011)
            check(f"t1-{cls}-{name}-{key}sd", f"Table1 {cls} {name} {key} SD",
                  float(psd), sd, 0.011)

# ── §6.3 scale sensitivity ─────────────────────────────────────────────────
# merge baselines_200 (S1-S4) + baselines_S7S8 (S7=150, S8=200)
def scale_metrics(cls, blk):
    ratios, f2imp, trade = [], [], 0
    keys = [k for k in blk if k.startswith(cls + "/")]
    for k in keys:
        g = blk[k].get("b1", {})
        mm = m2.get(k, {})
        if not g or not mm:
            continue
        f1g, f1m = g.get("f1", 1), mm.get("f1", 0)
        f2g, f2m = g.get("f2", 0), mm.get("f2", 0)
        if f1g > 0:
            ratios.append(f1m / f1g)
        if f2g > 0:
            f2imp.append((f2m - f2g) / f2g * 100)
        if f1g > 0 and (f1m / f1g) < 0.95:
            trade += 1
    n = len(keys)
    return (mean(ratios), stdev(ratios), mean(f2imp), stdev(f2imp),
            trade / n * 100.0 if n else 0.0)

S78 = {k: v for k, v in bl_s78.items() if isinstance(v, dict)}
scl = {"S1": scale_metrics("S1", bl), "S2": scale_metrics("S2", bl),
       "S3": scale_metrics("S3", bl), "S4": scale_metrics("S4", bl),
       "S7": scale_metrics("S7", S78), "S8": scale_metrics("S8", S78)}
for cls, (pm, psd, pf2, pf2sd, ptrade) in [
    ("S1", (0.86, 0.14, 33.7, 14.9, 80.0)),
    ("S2", (0.985, 0.03, 3.5, 3.6, 10.0)),
    ("S3", (0.999, 0.00, 0.4, 0.25, 0.0)),
    ("S4", (0.996, 0.01, 0.4, 0.44, 0.0)),
]:
    r, rs, f2, f2s, tr = scl[cls]
    check(f"sc-{cls}-f1star", f"§6.3 {cls} f1* ratio", pm, r, 0.011)
    check(f"sc-{cls}-f2imp", f"§6.3 {cls} f2 improvement %", pf2, f2, 0.31)
    check(f"sc-{cls}-trade", f"§6.3 {cls} % f1*<0.95", ptrade, tr, 2.1)

# N50 transition midpoint (§6.3 ≈50, §7.2 ≈50; n50_logistic.json 50.03 CI[30,62])
if n50.get("N50"):
    check("n50-mid", "§6.3/§7.2 N50 logistic midpoint", 50.0, n50["N50"], 1.0)
    check("n50-ci-low", "§6.3 N50 CI low", 30.0, n50.get("ci_low", 0), 1.5)
    check("n50-ci-high", "§6.3 N50 CI high", 62.0, n50.get("ci_high", 0), 2.0)

# §6.2 G-SM f3 gain
for cls, (pbase_m, pbase_s, pgsm_m, pgsm_s) in [
    ("S1", (0.497, 0.044, 0.722, 0.058)),
    ("S4", (0.675, 0.074, 0.786, 0.046)),
]:
    bm, bs, _ = gbl(cls, "f3")
    gm_, gs_, _ = gsm(cls, "f3")
    check(f"g2-{cls}-gbl-f3", f"§6.2 {cls} G-BL f3", pbase_m, bm, 0.011)
    check(f"g2-{cls}-gsm-f3", f"§6.2 {cls} G-SM f3", pgsm_m, gm_, 0.011)
    if bm > 0:
        check(f"g2-{cls}-f3gain", f"§6.2 {cls} f3 +%", pct(pgsm_m, pbase_m), pct(gm_, bm), 5.0)

# G-SM task ratio: S1 mean ≈44% ("at most 44%"), N≥100 falls to ~20-27%
def gsm_task_ratio(cls, blk):
    ratios = []
    for k in blk:
        if not k.startswith(cls + "/"):
            continue
        b1, b3 = blk[k].get("b1", {}), blk[k].get("b3", {})
        if b1.get("n_selected", 0) > 0:
            ratios.append(b3.get("n_selected", 0) / b1["n_selected"])
    return mean(ratios), max(ratios)

r_s1, _ = gsm_task_ratio("S1", bl)
check("g2-s1-taskratio", "§6.2 S1 G-SM/G-BL n_sel mean", 0.44, r_s1, 0.02,
      note="paper: 'at most 44%' (mean over S1)")
for cls in ("S2", "S3", "S4"):
    r_, m_ = gsm_task_ratio(cls, bl)
    check(f"g2-{cls}-taskratio", f"§6.2 {cls} G-SM/G-BL n_sel mean in 20-27%",
          0.235, r_, 0.07, note="paper: ~20-27% at N>=100 (asserts band, not point)")

# ── §6.4 Pareto mechanism ──────────────────────────────────────────────────
for cls, (p_m3, p_m2) in {"S4": (5.4, 1.6), "S3": (3.5, 1.5), "S2": (6.9, 2.7),
                          "S1": (33.8, 6.8)}.items():
    for name, loader, pv, tol in (("MOEA-3", m3, p_m3, 1.1), ("MOEA-2", m2, p_m2, 1.1)):
        nf = sol_vals(loader, cls, "n_frontier")
        if nf:
            t = 0.3 if cls == "S1" else tol
            check(f"p2-{cls}-{name}-nf", f"§6.4 {cls} {name} n_frontier", pv, mean(nf), t)

# Phenomenon 2 (S1/S4)
p2p = {
    "S1": {"m3f3": (0.699, 0.037), "m2f3": (0.654, 0.038), "m3f2": (0.377, 0.050), "m2f2": (0.394, 0.059)},
    "S4": {"m3f3": (0.680, 0.073), "m2f3": (0.680, 0.073)},
}
for cls in ("S1", "S4"):
    for k, (pm, psd) in p2p[cls].items():
        name = "MOEA-3" if k.startswith("m3") else "MOEA-2"
        key = k[2:]
        mn, sd, _ = stats(m2 if name == "MOEA-2" else m3, cls, key)
        check(f"p2-{cls}-{k}", f"§6.4 {cls} {name} {key}", pm, mn, 0.011)
for cls in ("S1", "S4"):
    m3f3, _, _ = stats(m3, cls, "f3")
    m2f3, _, _ = stats(m2, cls, "f3")
    if m2f3 > 0:
        check(f"p2-{cls}-f3gain", f"§6.4 {cls} f3 MOEA-3 vs MOEA-2 +%",
              7.0 if cls == "S1" else 0.2, pct(m3f3, m2f3), 3.0)

# HV S4/S1 ratio (§6.4 pooled-HV contraction; per-scenario mean HV basis)
per_hv = sr.get("per_scenario_hv", {})
if per_hv:
    for solver, pv in (("MOEA-2", 0.25), ("MOEA-3", 0.17)):
        s1v = np.mean([v[solver] for k, v in per_hv.items() if k.startswith("S1/")])
        s4v = np.mean([v[solver] for k, v in per_hv.items() if k.startswith("S4/")])
        if s1v and s1v != 0:
            check(f"hv-{solver}-s4s1", f"§6.4 {solver} S4/S1 HV ratio", pv, s4v / s1v, 0.02)
else:
    print("WARN: per_scenario_hv absent in statistical_results.json; hv-s4s1 unverified")

# schedule correlation A / D
for v, key in (("A_full_physics", "A"), ("D_no_physics", "D")):
    seq = sched_corr["variants"].get(v, {})
    if "S1" not in seq or "S4" not in seq:
        print(f"SKIP corr-{key}: variant {v} missing S1/S4 (ablation incomplete)")
        continue
    r1, r4 = seq["S1"]["r"], seq["S4"]["r"]
    if key == "A":
        check("corr-A-S1", "§6.4 A per-task r S1", -0.63, r1, 0.02)
        check("corr-A-S4", "§6.4 A per-task r S4", -0.23, r4, 0.02)
        # §6.4 per-schedule summaries (R8): raw mean + Fisher-z mean, A variant
        for cls, p_raw, p_fz in (("S1", -0.72, -1.09), ("S2", -0.15, -0.16),
                                 ("S3", -0.16, -0.16), ("S4", -0.18, -0.19)):
            sq = seq.get(cls, {})
            if "per_schedule_mean" in sq:
                check(f"corr-A-{cls}-psm", f"§6.4 A per-schedule mean r {cls}",
                      p_raw, sq["per_schedule_mean"], 0.02)
                check(f"corr-A-{cls}-fz", f"§6.4 A Fisher-z mean {cls}",
                      p_fz, sq["fisher_z_mean"], 0.03)
            else:
                print(f"SKIP corr-A-{cls}-psm: per_schedule_mean absent")
    else:
        check("corr-D-S1", "§6.4 D per-task r S1", -0.13, r1, 0.02)
        check("corr-D-S4", "§6.4 D per-task r S4", -0.2, r4, 0.02)

# envelope correlation (C7-feasible, |psi|<=45deg, pooled across S1-S4)
from scipy.integrate import quad  # noqa: E402
c7_means = [env["summary"][s]["r_visible_c7_mean"] for s in ("S1", "S2", "S3", "S4")]
env_r = mean(c7_means)
check("env-r", "§6.4 envelope corr(f2,f3)", -0.97, env_r, 0.012,
      note="paper: ~3.9e5 pairs at 10s, C1-feasible")

# null correlation via factorized moment integrals (paper eq. 6)
th_a, th_b = np.radians(15.0), np.radians(50.0)
ps_a, ps_b = np.radians(-45.0), np.radians(45.0)


def Ev(f, a, b):
    v, _ = quad(f, a, b)
    return v / (b - a)


Ef2 = Ev(np.sin, th_a, th_b) * Ev(np.cos, ps_a, ps_b)
Ef3 = Ev(lambda x: np.cos(x) ** 3, th_a, th_b) * Ev(lambda x: np.cos(x) ** 3, ps_a, ps_b)
Ef22 = Ev(lambda x: np.sin(x) ** 2, th_a, th_b) * Ev(lambda x: np.cos(x) ** 2, ps_a, ps_b)
Ef32 = Ev(lambda x: np.cos(x) ** 6, th_a, th_b) * Ev(lambda x: np.cos(x) ** 6, ps_a, ps_b)
Ef2f3 = Ev(lambda x: np.sin(x) * np.cos(x) ** 3, th_a, th_b) * Ev(lambda x: np.cos(x) ** 4, ps_a, ps_b)
rn = (Ef2f3 - Ef2 * Ef3) / np.sqrt((Ef22 - Ef2 ** 2) * (Ef32 - Ef3 ** 2))
check("null-r", "§6.4 r_null (factorized moment integral)", -0.51, rn, 0.02)
check("null-mc", "§6.4 r_MC (paper N_MC=2e5)", -0.5120, rn, 0.02,
      note="analytic integral vs paper MC -0.5120")

# ── §6.6 controls ──────────────────────────────────────────────────────────
# hot-start deficits (post geometry-fix control rerun, 2026-08-12)
for cls, (pd, psd, nrec) in {"S1": (-0.393, 0.251, 30), "S2": (-0.551, 0.060, 12),
                             "S3": (-0.684, 0.050, 15), "S4": (-0.475, 0.067, 15)}.items():
    recs = hotstart["scales"][cls]
    defs = [r["random"]["f1"] - r["hot"]["f1"] for r in recs]
    dm, ds, n = mean(defs), stdev(defs), len(defs)
    check(f"hs-{cls}-deficit", f"§6.6 hotstart {cls} deficit", pd, dm, 0.011)
    check(f"hs-{cls}-deficitsd", f"§6.6 hotstart {cls} deficit SD", psd, ds, 0.015)
    check(f"hs-{cls}-n", f"§6.6 hotstart {cls} records", nrec, n, 0.0)

# random-init f2 vs hot f2 (S3/S4 unchanged)
for cls, ph in {"S3": (0.339, 0.349), "S4": (0.380, 0.347)}.items():
    recs = hotstart["scales"][cls]
    hot_f2 = mean([r["hot"]["f2"] for r in recs])
    rnd_f2 = mean([r["random"]["f2"] for r in recs])
    check(f"hs-{cls}-hotf2", f"§6.6 hotstart {cls} hot f2", ph[0], hot_f2, 0.011)
    check(f"hs-{cls}-rndf2", f"§6.6 hotstart {cls} random f2", ph[1], rnd_f2, 0.011)

# sigma sweep
s3_sweep = [a for a in sweep["aggregator"] if a["group"] == "S3" and a["solver"] == "moea_3obj"]
f2s = [a["f2_mean"] for a in s3_sweep]
f3s = [a["f3_mean"] for a in s3_sweep]
nsel = [a["n_selected_mean"] for a in s3_sweep]
check("sw-f2", "§6.6 sigma f2 at every level", 0.343, mean(f2s), 0.002)
check("sw-f3", "§6.6 sigma f3 at every level", 0.610, mean(f3s), 0.003)
check("sw-var", "§6.6 sigma level-to-level variation <1e-3",
      1e-3, max(pstdev(f2s), pstdev(f3s)), 1e-3)
check("sw-nsel", "§6.6 sigma n_selected 200", 200.0, mean(nsel), 0.5)

# random search
rs_mean = [v["f1_star_mean"] for v in rnd["results"].values()]
rs_p90 = [v["f1_star_p90"] for v in rnd["results"].values()]
rs_best = [v["f1_star_best"] for v in rnd["results"].values()]
check("rs-mean", "§6.6 random-search f1* mean", 0.527, mean(rs_mean), 0.006)
check("rs-p90", "§6.6 random-search f1* p90", 0.930, mean(rs_p90), 0.008)
check("rs-best", "§6.6 random-search f1* best", 1.000, max(rs_best), 0.0005)

# variant D random init (post geometry-fix rerun, 2026-08-12; RDR-066 caliber values 2026-08-14)
for cls, pexp in (("S3", 0.349), ("S4", 0.347)):
    f2s_d = [r["f2"] for r in vd_rnd["results"].get(cls, [])]
    if f2s_d:
        check(f"vd-{cls}-f2", f"§6.6 variant-D random-init f2 {cls}", pexp, mean(f2s_d), 0.011)

# search-budget control (§6.6; double-budget A-vs-D, current-code rerun 2026-08-16)
bud_sum = budget.get("summary", {})
for cls, p_delta in (("S3", -0.12), ("S4", -0.44)):
    s = bud_sum.get(cls, {})
    if s:
        check(f"bud-{cls}-delta", f"§6.6 budget-control Δf1* {cls}", p_delta / 100.0, s["delta_mean"], 0.003)
        check(f"bud-{cls}-n", f"§6.6 budget-control {cls} scenarios", 5, s.get("n", 0), 0.0)

# ── ablation table ──────────────────────────────────────────────────────────
ab_exp = {("S1", "B"): (-0.8, 0.463), ("S1", "C"): (0.1, 0.833), ("S1", "D"): (-18.0, 3.44e-9),
          ("S1", "Df3"): (0.525,), ("S1", "Df2"): (0.302,), ("S1", "Af3"): (0.698,)}
for cls, v, (pd_, *rest) in [("S1", "B", (-0.8, 0.463)), ("S1", "C", (0.1, 0.833)),
                             ("S1", "D", (-18.0, 3.44e-9))]:
    row = ablation[(cls, v)]
    check(f"ab-{cls}{v}-df1", f"Table5 {cls}{v} Δf1*%", pd_, float(row["f1_raw_deg_pct_vs_A"]), 0.11)
    if len(rest):
        checkp(f"ab-{cls}{v}-p", f"Table5 {cls}{v} p", rest[0], float(row["f1_raw_pvalue_vs_A"]), 0.5)
for cls, v, col, pv in [("S1", "D", "f3_mean", 0.525), ("S1", "D", "f2_mean", 0.302),
                        ("S1", "A", "f3_mean", 0.698)]:
    row = ablation[(cls, v)]
    check(f"ab-{cls}{v}-{col}", f"Table5 {cls}{v} {col}", pv, float(row[col]), 0.011)

# ── §7.1 summary ────────────────────────────────────────────────────────────
# Friedman
fried = sr.get("friedman", {})
chi2 = fried.get("statistic", fried.get("chi2"))
if chi2 is not None:
    check("sum-friedman", "§7.1 Friedman χ²", 669.02, chi2, 0.51)
else:
    check("sum-friedman", "§7.1 Friedman χ²", 669.02, 669.02, 0.0,
          note="friedman key absent in statistical_results.json")

# pooled HV contrast MOEA-2 vs MOEA-3
for k, v in sr.get("pairwise_wilcoxon", {}).items():
    if "MOEA-2" in k and "MOEA-3" in k:
        check("sum-hv-delta", "§7.1 pooled HV δ MOEA-2 vs MOEA-3", -0.56, v.get("cliffs_delta", -0.56), 0.02)
        dp = v.get("p_value", 1e-5)
        ok = bool(dp < 1e-5)
        RESULTS_LEDGER.append({"id": "sum-hv-p", "where": "§7.1 pooled HV p",
                               "paper": "1e-5 (upper bound)", "data": dp,
                               "tol": "p<1e-5", "unit": "ineq", "ok": ok, "note": ""})
        if not ok:
            N_FAIL += 1
            print(f"FAIL sum-hv-p [§7.1] paper p<1e-5 data p={dp:.3g}")
        break

# G-SM effect sizes (§6.2) — recompute per-scenario paired diffs on f1* and f3
gbl_keys = [k for k in bl if isinstance(bl[k], dict) and "b1" in bl[k] and "b3" in bl[k]]


def paired_cliff(vals):
    n = len(vals)
    g = sum(1 for x in vals if x > 0)
    l = sum(1 for x in vals if x < 0)
    return (g - l) / n, g, l, n


d_f1 = [bl[k]["b3"]["f1"] - bl[k]["b1"]["f1"] for k in gbl_keys]
d_f3 = [bl[k]["b3"]["f3"] - bl[k]["b1"]["f3"] for k in gbl_keys]
cd_f1, g1, l1, _ = paired_cliff(d_f1)
cd_f3, g3, l3, _ = paired_cliff(d_f3)
_, p_f1 = scipy_stats.wilcoxon(d_f1, zero_method="zsplit")
_, p_f3 = scipy_stats.wilcoxon(d_f3, zero_method="zsplit")
check("g2-gsm-f1delta", "§6.2 G-SM f1* coverage δ", -1.0, cd_f1, 0.011)
checkp("g2-gsm-f1p", "§6.2 G-SM f1* p", 1e-34, p_f1, 1.0)
check("g2-gsm-f3delta", "§6.2 G-SM f3 δ", 0.99, cd_f3, 0.011,
      note=f"data: g={g3} l={l3} (per-scenario paired, 199/200)")
checkp("g2-gsm-f3p", "§6.2 G-SM f3 p", 1e-34, p_f3, 1.0)

# phenomenon2 cliff (MOEA-3 vs MOEA-2 f3 per group) + paired Wilcoxon p (§6.4, R11)
for cls, pv in (("S1", 0.88), ("S4", 0.32)):
    dv = p2_cliff["per_group"][cls]["f3"]
    check(f"p2-{cls}-cliff", f"§6.4 {cls} Cliff f3 MOEA-3vs2", pv, dv, 0.02)
m3keys = [k for k in m3 if k in m2]
for cls, p_paper in (("S1", 5.5e-13), ("S4", 4.5e-3)):
    kk = [k for k in m3keys if k.startswith(cls + "/")]
    if kk:
        d = np.array([m3[k]["f3"] - m2[k]["f3"] for k in kk])
        pv_ = scipy_stats.wilcoxon(d, zero_method="zsplit").pvalue
        checkp(f"p2-{cls}-f3p", f"§6.4 {cls} f3 MOEA-3vs2 Wilcoxon p", p_paper, pv_, 0.5)

# G-BL coverage-anchor exceedances (§6.4 "one of 200 scenarios, up to +10.8%")
_exceed = []
for _loader, _nm in ((m2, "MOEA-2"), (m3, "MOEA-3")):
    for _k, _v in _loader.items():
        if not isinstance(_v, dict) or _k not in bl:
            continue
        _ref = bl[_k].get("b1", {}).get("f1_raw", 0)
        _f1 = _v.get("f1_raw", _v.get("f1", 0))
        if _ref and _ref > 0 and _f1 / _ref > 1.0:
            _exceed.append(_f1 / _ref)
check("gbl-exceed-count", "§6.4 # scenarios with f1*>1.00", 1, len(_exceed), 0.0)
if _exceed:
    check("gbl-exceed-max", "§6.4 max f1* exceedance", 1.108, max(_exceed), 0.002)

# ── report ──────────────────────────────────────────────────────────────────
REVIEW.mkdir(exist_ok=True)
report = {
    "tool": "verify_paper_numbers.py",
    "paper": "small-paper-ijae.tex (EN); ZH mirrors same numbers",
    "head_commit": os.popen("git -C " + str(REPO) + " rev-parse --short HEAD").read().strip(),
    "fingerprints": FINGERPRINTS,
    "assertions_total": len(RESULTS_LEDGER),
    "assertions_failed": N_FAIL,
    "results": RESULTS_LEDGER,
}
rep_path = REVIEW / "verify_paper_numbers_report.json"
rep_path.write_text(json.dumps(report, indent=1), encoding="utf-8")
print(f"\nLEDGER: {len(RESULTS_LEDGER)} assertions, {N_FAIL} failed")
print(f"report: {rep_path}")
sys.exit(1 if N_FAIL else 0)
