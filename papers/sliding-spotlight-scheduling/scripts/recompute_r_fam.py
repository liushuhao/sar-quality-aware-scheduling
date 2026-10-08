#!/usr/bin/env python3
"""Ticket 23: recompute the real-window family structural dimension (R_fam)
under the per-task-r0 caliber, as a committed reproducible script (gate-review
Y5).  Ticket 41 / A-CROSS (yi) re-registration: the default scenarios dir is
now the PROMOTED v3 real-window family (``experiments/v3_results/scenarios``)
and the operative reproduction targets are the ticket-40 (yi) values
**R1C 3.9998 / R2F 8.7407 / R3H 10.91 dB** (base seed), matching
``scripts/verify_v3_verdicts.py``.  The pre-(yi) ticket-17 prose figures
4.0032 / 6.8213 / 6.8216 are SUPERSEDED, and the retired R4H family is gone
(ticket 25).

CALIBER (registered here so the numbers are falsifiable):
  * scan axes: task x 11 in-window starts x routed mode, at the task's
    registered production PRF (t["prf_hz"]) -- the ticket-17 analysis
    caliber, same convention as reachable_range_db in
    verify_ticket22_adjudications.py (a first version of this script
    misread the prose "registered PRF" as the 4-key PRF scan, which
    produces ~60 dB nonsense: aliasing at an unregistered-for-the-task
    PRF is physical garbage, not a promotion reading);
  * squint AND aasr_direct both quote the TASK's own r0_m (ticket 23); the
    pre-ticket-23 readout used the library R0 inside aasr_direct, which is
    exactly the eighth caliber-split instance this ticket closes;
  * spt_scene_wa_m = the task's azimuth_size_m (D08-2 worst-edge);
  * out-of-domain samples (a_res <= 0) are EXCLUDED from the range.  Under the
    A-CROSS (yi) law a_res = 1-k = A > 0 at every squint, so this guard only
    trips at the family corner k >= 1 (unreachable for the library k<1);
    retained defensively (ticket 41);
  * R_fam = max - min over the remaining samples, per family: reported for
    the BASE seed manifest (seed = variant_index*100) AND as the max over
    all 10 seeds, since the ticket-17 prose did not pin which aggregation
    the 6.82 values used -- both are printed so the adjudication is honest
    about the aggregation.

Verdict threshold: 6.0 dB (PROMOTION_SPREAD_DB, frozen).  Exit code 0 always
when artifacts exist -- this is a MEASUREMENT script, not a gate; the
verdict lines are for the ticket-23 adjudication record.

Usage:  PYTHONPATH=src:papers/sliding-spotlight-scheduling python \
          papers/sliding-spotlight-scheduling/scripts/recompute_r_fam.py \
          [--scenarios-dir DIR] [--out JSON]
"""
import argparse
import json
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORK))
REPO = FORK.parents[1]
sys.path.insert(0, str(REPO / "src"))

from sss_core.aasr import aasr_direct  # noqa: E402
from sss_core.geometry import squint_at  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402

# ticket 25: R4H (N=500) is out of the re-based density ladder 20/50/100
# (single-transit capacity 24, AD-5) -- its entry and the R_FAMILY_REGISTRY
# slot 4 were removed together with the ladder amendment
FAMILIES = {"R1C": 100, "R2F": 200, "R3H": 300}
N_STARTS = 11
THRESHOLD_DB = 6.0


def _task_windows(t: dict):
    """Dual-schema window spec (ticket 25): per-window (t0, t1, t_ca, r0).

    New manifests carry a ``windows`` list (one entry per enumerated
    transit); legacy manifests keep the scalar triad, which is the
    single-window special case.
    """
    if "windows" in t:
        for w in t["windows"]:
            r0 = w.get("r0_m")
            yield (
                float(w["lo_s"]), float(w["hi_s"]), float(w["t_ca_s"]),
                float(r0) if r0 is not None else None,
            )
    else:
        r0 = t.get("r0_m")
        yield (
            float(t["t_start_s"]), float(t["t_end_s"]), float(t["t_ca_s"]),
            float(r0) if r0 is not None else None,
        )


def family_r(
    manifest: dict, lib: ModeLibrary, per_task_r0: bool = True
) -> tuple[float, int, int]:
    """(R_fam dB, n_samples_used, n_excluded_out_of_domain) for one manifest.

    per_task_r0=True is the operative caliber (matches verify_v3_verdicts.py:
    R1C 3.9998 / R2F 8.7407 / R3H 10.91 dB base-seed on v3).  per_task_r0=False
    reproduces the ticket-17era readout (library R0 inside aasr_direct); that
    cross-check is SUPERSEDED by the A-CROSS (yi) law (ticket 41) and its
    values no longer match the pre-(yi) ticket-17 prose -- kept only as a
    diagnostic column.

    Ticket 25: sampling is PER WINDOW (each transit has its own zero and
    slant range; sampling the whole task span against one zero would
    misread every non-primary pass)."""
    vals = []
    excluded = 0
    for t in manifest["tasks"]:
        mode = Mode[t["mode"]]
        wa = float(t["azimuth_size_m"])
        prf = float(t["prf_hz"])
        for t0, t1, t_ca, r0 in _task_windows(t):
            r0 = (float(r0) if r0 is not None else lib.geo.R0_m) if per_task_r0 else None
            for i in range(N_STARTS):
                tt = t0 + (t1 - t0) * i / (N_STARTS - 1)
                psi = squint_at(tt, t_ca, lib.geo, r0_m=r0)
                try:
                    vals.append(aasr_direct(
                        mode, psi, lib.geo.k, prf, lib,
                        spt_scene_wa_m=(wa if mode is Mode.SPT else None),
                        r0_m=r0,
                    )["aasr_db"])
                except ValueError:
                    excluded += 1
    if not vals:
        raise ValueError("no AASR sample reachable in the physical domain")
    return max(vals) - min(vals), len(vals), excluded


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios-dir", default=str(
        FORK / "experiments" / "v3_results" / "scenarios"))
    ap.add_argument("--out", default=None, help="write the verdict table as JSON")
    args = ap.parse_args()
    scen = Path(args.scenarios_dir)
    lib = ModeLibrary.from_fixture()
    rows = {}
    for code, base_seed in FAMILIES.items():
        manifests = sorted(scen.glob(f"{code}_seed*.json"))
        if not manifests:
            print(f"ABORT: no manifests for {code} under {scen}", file=sys.stderr)
            return 2
        base = next(p for p in manifests if p.stem.endswith(f"seed{base_seed}"))
        r_old, _, _ = family_r(
            json.loads(base.read_text(encoding="utf-8")), lib, per_task_r0=False
        )
        r_base, n_used, n_excl = family_r(json.loads(base.read_text(encoding="utf-8")), lib)
        per_seed = {}
        for p in manifests:
            r_s, _, _ = family_r(json.loads(p.read_text(encoding="utf-8")), lib)
            per_seed[p.stem] = round(r_s, 4)
        r_max = max(per_seed.values())
        struct = lambda r: "ALIVE" if r >= THRESHOLD_DB else "DEAD"
        rows[code] = {
            "r_ticket17_reproduction_lib_r0_db": round(r_old, 4),
            "r_base_seed_db": round(r_base, 4),
            "r_max_over_seeds_db": round(r_max, 4),
            "verdict_base": struct(r_base),
            "verdict_max": struct(r_max),
            "n_samples_base": n_used,
            "n_excluded_base": n_excl,
            "per_seed_db": per_seed,
        }
        print(f"{code}: ticket-17 lib-R0 reproduction R={r_old:.4f} dB  |  "
              f"per-task-r0 base-seed R={r_base:.4f} dB ({struct(r_base)})  "
              f"max-over-10-seeds R={r_max:.4f} dB ({struct(r_max)})  "
              f"[samples {n_used}, excluded {n_excl}]")
    print("\nthreshold: R >= 6.0 dB => STRUCTURALLY ALIVE (frozen); "
          "ALIVE x UNCONVERGED => NO CLAIM (frozen four-cell wording)")
    if args.out:
        Path(args.out).write_text(
            json.dumps({"caliber": "ticket x 11 starts x routed mode, at the task's "
                                  "registered production PRF, per-task r0_m, "
                                  "out-of-domain excluded",
                        "threshold_db": THRESHOLD_DB,
                        "families": rows}, indent=2, ensure_ascii=False),
            encoding="utf-8")
        print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
