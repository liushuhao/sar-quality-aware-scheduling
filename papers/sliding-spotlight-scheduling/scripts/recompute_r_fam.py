#!/usr/bin/env python3
"""Ticket 23: recompute the real-window family structural dimension (R_fam)
under the per-task-r0 caliber, as a committed reproducible script (the
ticket-17 values 4.0032 / 6.8213 / 6.8216 / 6.8213 existed only as analysis
prose; gate-review Y5).

CALIBER (registered here so the numbers are falsifiable):
  * scan axes: task x 11 in-window starts x routed mode x 4 registered PRFs
    (PRF_KEYS_HZ) -- the ticket-17 analysis caliber;
  * squint AND aasr_direct both quote the TASK's own r0_m (ticket 23); the
    pre-ticket-23 readout used the library R0 inside aasr_direct, which is
    exactly the eighth caliber-split instance this ticket closes;
  * spt_scene_wa_m = the task's azimuth_size_m (D08-2 worst-edge);
  * out-of-domain samples (a_res <= 0) are EXCLUDED from the range, the
    D12-3 unenforced-readout convention after the ticket-17 +inf fix;
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

from sss_core.aasr import PRF_KEYS_HZ, aasr_direct  # noqa: E402
from sss_core.geometry import squint_at  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402

FAMILIES = {"R1C": 100, "R2F": 200, "R3H": 300, "R4H": 400}
N_STARTS = 11
THRESHOLD_DB = 6.0


def family_r(manifest: dict, lib: ModeLibrary) -> tuple[float, int, int]:
    """(R_fam dB, n_samples_used, n_excluded_out_of_domain) for one manifest."""
    vals = []
    excluded = 0
    for t in manifest["tasks"]:
        mode = Mode[t["mode"]]
        t0, t1 = float(t["t_start_s"]), float(t["t_end_s"])
        t_ca = float(t["t_ca_s"])
        r0 = t.get("r0_m")
        r0 = float(r0) if r0 is not None else lib.geo.R0_m
        wa = float(t["azimuth_size_m"])
        for i in range(N_STARTS):
            tt = t0 + (t1 - t0) * i / (N_STARTS - 1)
            psi = squint_at(tt, t_ca, lib.geo, r0_m=r0)
            for prf in PRF_KEYS_HZ:
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
        REPO / ".scratch" / "sliding-spotlight-scheduling" / "v2-run" / "scenarios"))
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
        r_base, n_used, n_excl = family_r(json.loads(base.read_text(encoding="utf-8")), lib)
        per_seed = {}
        for p in manifests:
            r_s, _, _ = family_r(json.loads(p.read_text(encoding="utf-8")), lib)
            per_seed[p.stem] = round(r_s, 4)
        r_max = max(per_seed.values())
        struct = lambda r: "ALIVE" if r >= THRESHOLD_DB else "DEAD"
        rows[code] = {
            "r_base_seed_db": round(r_base, 4),
            "r_max_over_seeds_db": round(r_max, 4),
            "verdict_base": struct(r_base),
            "verdict_max": struct(r_max),
            "n_samples_base": n_used,
            "n_excluded_base": n_excl,
            "per_seed_db": per_seed,
        }
        print(f"{code}: base-seed R={r_base:.4f} dB ({struct(r_base)})  "
              f"max-over-10-seeds R={r_max:.4f} dB ({struct(r_max)})  "
              f"[samples {n_used}, excluded {n_excl}]")
    print("\nthreshold: R >= 6.0 dB => STRUCTURALLY ALIVE (frozen); "
          "ALIVE x UNCONVERGED => NO CLAIM (frozen four-cell wording)")
    if args.out:
        Path(args.out).write_text(
            json.dumps({"caliber": "ticket x 11 starts x routed mode x 4 PRFs, "
                                  "per-task r0_m, out-of-domain excluded",
                        "threshold_db": THRESHOLD_DB,
                        "families": rows}, indent=2, ensure_ascii=False),
            encoding="utf-8")
        print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
