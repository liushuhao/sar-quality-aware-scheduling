#!/usr/bin/env python3
"""fig-2 (R96 figure wave): the endogenous dwell law -- T against rho_req.

The mechanism figure behind the title claim, placed in the dwell section:
the task-law dwell of the production chain (formula-spec v1.9 section 4.1,
Kim Eq.(22)/(24) tan-exact via ``sss_core.duration.duration_scene_s``) as a
function of the required azimuth resolution, per mode, at zero squint with a
thin ribbon to the 12 deg reference squint.

Library scene caliber (W_a = 5 km reference scene, library R0): this figure
states the platform law, not the evaluator's per-task dwell -- the empirical
counterpart (per-task scene size, per-window slant range, selected starts)
is the dwell-distribution figure, and the two captions say so.

STR has no task-level parameter, so its dwell is flat in rho_req -- the
graphical definition of the exogenous constant this paper retires.  The
sliding branch exists only inside its task-law domain (rho_req cos(psi) <
D/2) and degenerates onto the stripmap transit at the domain edge; the
spotlight branch lies one scene-sweep term W_a/v_s below it there.

Zero experiments: every value is a deterministic function of the frozen
platform fixture and the frozen production closures.  The script also
writes a figure-data receipt (ledger-entry format) covering every number
the caption quotes, under ``experiments/v5_results/figure_data/``.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/plot_fig2_dwell_mechanism.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))

OUT = FORK / "paper" / "figures" / "fig2_dwell_mechanism.pdf"
RECEIPT = FORK / "experiments" / "v5_results" / "figure_data" / "fig2_dwell_mechanism.json"

X_MIN, X_MAX = 0.25, 3.15
RHO_GRID = [X_MIN + i * (X_MAX - X_MIN) / 460.0 for i in range(461)]
PSI_RIBBON_DEG = 12.0
TIER_FINE = (0.3, 0.6)
TIER_COARSE = (2.5, 3.0)
S08_COARSE_RECT = (0.8 * TIER_COARSE[0], 0.8 * TIER_COARSE[1])  # (2.0, 2.4)
PRODUCER = ("PYTHONHASHSEED=0 \"/d/Program Files/Python/python\" -B "
            "papers/sliding-spotlight-scheduling/scripts/plot_fig2_dwell_mechanism.py")
CAL_TAG = "figure receipt / library scene caliber / frozen fixture + production closures"


def _entry(eid, value, unit, source_file, source_path, note=None):
    e = {"id": eid, "value": value, "unit": unit, "caliber_tag": CAL_TAG,
         "produced_by": PRODUCER,
         "source": {"file": source_file, "path": source_path}}
    if note:
        e["note"] = note
    return e


def main() -> int:
    from sss_core.duration import duration_scene_s
    from sss_core.modes import Mode, ModeLibrary

    lib = ModeLibrary.from_fixture()
    geo = lib.geo
    floor = geo.D_m / 2.0

    def dwell(mode, psi_deg, rho):
        return duration_scene_s(mode, math.radians(psi_deg), lib,
                                rho_req_m=None if mode is Mode.STR else rho)

    print(f"# fixture: D={geo.D_m:.4f} m  floor=D/2={floor:.4f} m  "
          f"R0={geo.R0_m/1e3:.1f} km  vs={geo.vs_mps:.2f} m/s  "
          f"theta_a={math.degrees(geo.theta_a_rad):.2f} deg  "
          f"lambda={geo.wavelength_m} m  Wa={geo.scene_wa_m/1e3:.0f} km  "
          f"registered r0={geo.r0_m:.0f} m")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["cmr10"],
        "mathtext.fontset": "cm", "axes.unicode_minus": False,
        "font.size": 9.5, "axes.labelsize": 9.5, "axes.titlesize": 9.5,
        "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "legend.fontsize": 7.6,
        "axes.linewidth": 0.8, "lines.linewidth": 1.3,
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "axes.formatter.use_mathtext": True,
        "figure.constrained_layout.use": True,
    })

    fig, ax = plt.subplots(figsize=(3.85, 2.55))

    receipts = []
    # --- demand-tier bands and the arithmetic of the infeasible cell -------
    for (lo, hi) in (TIER_FINE, TIER_COARSE):
        ax.axvspan(lo, hi, color="0.5", alpha=0.12, lw=0, zorder=1)
    ax.axvspan(*S08_COARSE_RECT, color="0.2", alpha=0.05, lw=0, zorder=1)
    ax.text(0.5 * (S08_COARSE_RECT[0] + S08_COARSE_RECT[1]), 13.15,
            "$0.8\\times$coarse\n$=[2.0,2.4]$", ha="center", va="top",
            fontsize=6.2, color="0.30")

    # --- the three mode branches -------------------------------------------
    curves = {}
    edge = floor / math.cos(0.0)  # SLS domain edge at psi = 0
    for mode, style, lw in ((Mode.STR, "-", 1.6), (Mode.SLS, (0, (5, 1.6)), 1.3),
                            (Mode.SPT, (0, (1, 1.2)), 1.3)):
        xs, ys = [], []
        for rho in RHO_GRID:
            if mode is not Mode.SLS or rho < edge:
                xs.append(rho)
                ys.append(dwell(mode, 0.0, rho))
        # ribbon to the 12 deg reference squint: the law barely moves
        xr, yr = [], []
        for rho in xs:
            try:
                yr.append(dwell(mode, PSI_RIBBON_DEG, rho))
                xr.append(rho)
            except ValueError:
                break  # 12 deg domain edge reached; ribbon stops there
        if xr:
            ax.fill_between(xr, ys[:len(yr)], yr, color="black", alpha=0.10,
                            lw=0, zorder=2)
        name = mode.name
        curves[name] = (xs, ys)
        ax.plot(xs, ys, color="black", linestyle=style, lw=lw, zorder=3)

    # direct endpoint labels (no legend box: mode colours do not exist here)
    ax.text(X_MAX - 0.03, dwell(Mode.STR, 0.0, 0) + 0.28, "STR",
            ha="right", fontsize=8.5)
    ax.text(0.305, curves["SLS"][1][0] - 1.15, "SLS", ha="left", fontsize=8.5)
    ax.text(0.305, curves["SPT"][1][0] + 0.45, "SPT", ha="left", fontsize=8.5)
    ax.text(0.315, 2.35, "fine tier", rotation=90, fontsize=6.2, color="0.35",
            ha="left", va="bottom")
    ax.text(3.13, 2.35, "coarse tier", rotation=90, fontsize=6.2, color="0.35",
            ha="right", va="bottom")

    # stripmap floor = the SLS domain edge at zero squint
    ax.axvline(floor, color="0.35", lw=0.7, ls=":", zorder=2)
    ax.text(floor - 0.04, 11.3, "STR floor $D/2=2.4669$ m\n= SLS domain edge",
            ha="right", va="top", fontsize=6.4, color="0.30")

    # registered operating point on the sliding branch
    t_sls_05 = dwell(Mode.SLS, 0.0, 0.5)
    ax.plot([0.5], [t_sls_05], marker="o", markersize=3.6, color="black",
            zorder=4)
    ax.annotate("registered operating point\n$\\rho_{\\mathrm{req}}=0.5$ m "
                "($r_0=197\\,119$ m)", xy=(0.5, t_sls_05),
                xytext=(0.62, 8.6), fontsize=6.4,
                arrowprops=dict(arrowstyle="-", lw=0.6, color="0.35"))

    ax.set_xlim(X_MIN, X_MAX)
    ax.set_ylim(0.0, 13.5)
    ax.set_xticks([0.3, 0.5, 1.0, 2.0, floor, 3.0])
    ax.set_xticklabels(["0.3", "0.5", "1", "2", "2.4669", "3"])
    ax.set_yticks([0, 2, 4, 6, 8, 10, 12])
    ax.set_xlabel(r"required azimuth resolution $\rho_{\mathrm{req}}$ (m)")
    ax.set_ylabel(r"scene dwell $T$ (s), $\bar\psi=0^{\circ}$")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight")
    print(f"# written {OUT}")

    # --- receipt: every caption number, ledger-entry format -----------------
    wa_vs = geo.scene_wa_m / geo.vs_mps
    vals = {
        "floor_m": floor,
        "str_dwell_s_psi0": dwell(Mode.STR, 0.0, 0),
        "str_dwell_s_psi12": dwell(Mode.STR, PSI_RIBBON_DEG, 0),
        "sls_dwell_s_rho0.3": dwell(Mode.SLS, 0.0, 0.3),
        "sls_dwell_s_edge": curves["SLS"][1][-1],
        "sls_dwell_s_rho0.5_regpoint": t_sls_05,
        "spt_dwell_s_rho0.3": dwell(Mode.SPT, 0.0, 0.3),
        "spt_dwell_s_floor": dwell(Mode.SPT, 0.0, floor),
        "scene_sweep_s": wa_vs,
        "sls_domain_edge_m": edge,
        "r0_registered_m": geo.r0_m,
        "ribbon_squint_deg": PSI_RIBBON_DEG,
        "tier_fine": list(TIER_FINE),
        "tier_coarse": list(TIER_COARSE),
        "s08_coarse_rect": list(S08_COARSE_RECT),
        "D_m": geo.D_m,
        "R0_km": geo.R0_m / 1e3,
        "theta_a_deg": math.degrees(geo.theta_a_rad),
        "lambda_m": geo.wavelength_m,
        "Wa_km": geo.scene_wa_m / 1e3,
    }
    notes = {
        "floor_m": "D/2 with D=lambda/theta_a; also the SLS task-law domain edge at zero squint",
        "scene_sweep_s": "W_a/v_s: the constant gap between the STR and SPT branches at the floor",
        "sls_domain_edge_m": "rho_req cos(psi) < D/2; the SLS branch is truncated here, not extrapolated",
        "s08_coarse_rect": "0.8 x [2.5,3.0] m: the coarse tier under the s=0.8 tightening lies wholly fine-side of the floor",
    }
    for k, v in vals.items():
        print(f"# receipt {k} = {v if isinstance(v, list) else round(v, 6)}")
        receipts.append(_entry(f"fig2.{k}", v,
                               "m" if k in ("floor_m", "sls_domain_edge_m",
                                           "r0_registered_m") else
                               ("deg" if k == "ribbon_squint_deg" else
                                ("m-band" if isinstance(v, list) else "s")),
                               "scripts/plot_fig2_dwell_mechanism.py",
                               f"vals.{k}", notes.get(k)))
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps({"figure": "fig2_dwell_mechanism",
                                   "entries": receipts}, indent=1),
                       encoding="utf-8")
    print(f"# written {RECEIPT}")

    # silent-zero guard: all three branches must have drawn
    n_pts = {k: len(v[0]) for k, v in curves.items()}
    print(f"# plotted {n_pts}")
    if min(n_pts.values()) < 100:
        print("ABORT: a mode branch rendered (near-)empty", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
