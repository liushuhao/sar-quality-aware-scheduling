#!/usr/bin/env python3
"""Full experiment matrix driver: 5 variants x 10 seeds (spec D10).

Usage (repo root, real interpreter -- the bare `python` shim is polluted):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" \
        papers/sliding-spotlight-scheduling/scripts/run_matrix.py \
        [--pop 40] [--gen 60] [--variants 1,2,3,4,5]

Solver seed = scenario seed (one integer drives all stochastic stages,
scenario_manifest_template.json seed_convention).

Defenses (paper-1 runner fault modes, feedback-runner-three-fault-modes):
- manifests generated once; on rerun each existing manifest is regenerated
  in memory and byte-compared (determinism assertion, fail loud on drift)
- per-unit subprocess isolation; distinguishing exit codes recorded (0/10/11)
- progress file: atomic write (tmp + fsync + os.replace) with .bak fallback
  (JSONDecodeError falls back to the backup; both corrupt = abort)
- resume skips a unit only if the artifact exists AND the recorded exit is 0
  AND the manifest sha1 matches AND the code identity (git HEAD) is unchanged
  (feedback-version-identity + resume-sha lessons)
- zero-output alarm (exit 4), generation-defect alarm (exit 5, any exit 10),
  variant-wide empty-front alarm (exit 6)
- per-unit stdout lines flushed immediately (no block-buffer fake stall)
"""
from __future__ import annotations

import argparse
import hashlib
import math
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))

from sss_core.scenarios import (  # noqa: E402
    R_FAMILY_REGISTRY,
    VARIANT_REGISTRY,
    generate_scenario,
    write_manifest,
)

SCENARIOS_DIR = FORK / "experiments" / "results" / "scenarios"
MATRIX_DIR = FORK / "experiments" / "results" / "matrix"
PROGRESS_PATH = MATRIX_DIR / "_progress.json"
PILOT_SCRIPT = FORK / "scripts" / "run_pilot.py"
SEEDS_PER_VARIANT = 10


@dataclass
class MatrixDirs:
    """Where a run reads and writes (ticket 17 acceptance item 3).

    The six frozen result families under ``experiments/results/`` must not be
    re-run in place, so every path the driver touches is an injected field
    rather than a module global.  The defaults reproduce the original
    behaviour exactly -- a caller that passes nothing still writes to the
    frozen directories, which is why a real-window run MUST pass explicit
    directories rather than relying on the default.
    """

    scenarios: Path = SCENARIOS_DIR
    matrix: Path = MATRIX_DIR
    progress: Path = PROGRESS_PATH
    pilot_script: Path = PILOT_SCRIPT

EXIT_OK = 0
EXIT_ZERO_OUTPUT = 4
EXIT_GENERATION_DEFECT = 5
EXIT_VARIANT_EMPTY = 6
EXIT_UNIT_SETUP_ERROR = 7


def git_head() -> str:
    import re

    import shutil as _shutil
    exe = _shutil.which("git")
    if exe is None:
        raise SystemExit("git not found on PATH")
    out = subprocess.run(
        [exe, "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    head = out.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise SystemExit(f"git rev-parse returned non-HEAD-sha output: {head!r}")
    return head


def manifest_sha1(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def atomic_write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _repo_relative(path: Path) -> str:
    """Path relative to the repo root when possible, else absolute.

    The progress record used to call relative_to(REPO) unconditionally, which
    broke the moment the output directory left the tree -- i.e. exactly the
    case ticket 17 parameterisation exists to support (measured: the first
    real-window smoke run died here, after generating every manifest).
    """
    try:
        return str(path.relative_to(FORK.parent.parent))
    except ValueError:
        return str(path)


def load_progress(progress_path: Path | None = None) -> dict | None:
    progress_path = progress_path or PROGRESS_PATH
    for cand in (progress_path, progress_path.with_suffix(".json.bak")):
        if cand.exists():
            try:
                return json.loads(cand.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                print(f"progress file corrupt, falling back: {cand}", flush=True)
    return None


def ensure_manifests(
    variants: dict[int, tuple],
    dirs: "MatrixDirs | None" = None,
    generator=None,
    platform=None,
) -> dict[str, Path]:
    """Generate missing manifests; byte-verify existing ones (determinism).

    ``generator`` defaults to the synthetic-box ``generate_scenario``; the
    real-window family injects ``generate_real_scenario`` instead, so the
    driver need not know which family it is driving.
    """
    dirs = dirs or MatrixDirs()
    generate = generator or generate_scenario
    paths: dict[str, Path] = {}
    lib = None
    for vidx, spec in sorted(variants.items()):
        code, density = spec[0], spec[1]
        rest = tuple(spec[2:])
        for si in range(SEEDS_PER_VARIANT):
            seed = vidx * 100 + si
            path = dirs.scenarios / f"{code}_seed{seed}.json"
            if lib is None:
                from sss_core.modes import ModeLibrary
                lib = ModeLibrary.from_fixture()
            # The two families have different registry arities -- M is
            # (code, density, interval, tier), R is (code, density, tier) --
            # so the tail is passed BY KEYWORD.  Positional unpacking made
            # the R tier collide with `variant_index` (measured, not inferred).
            if generator is None:
                interval, tier = rest
                manifest = generate(
                    code, density, interval, tier, seed,
                    variant_index=vidx, lib=lib,
                )
            else:
                (tier,) = rest
                manifest = generate(
                    code, density, tier, seed,
                    variant_index=vidx, lib=lib, platform=platform,
                )
            fresh = json.dumps(manifest, indent=2, sort_keys=True,
                               ensure_ascii=False) + "\n"
            if path.exists():
                if path.read_text(encoding="utf-8") != fresh:
                    raise SystemExit(
                        f"DETERMINISM DRIFT: {path} differs from regeneration"
                    )
            else:
                write_manifest(manifest, path)
                print(f"manifest generated: {path.name}", flush=True)
            paths[f"{code}_{seed}"] = path
    return paths


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop", type=int, default=40)
    ap.add_argument("--gen", type=int, default=60)
    ap.add_argument("--variants", default="1,2,3,4,5",
                    help="variant indexes into VARIANT_REGISTRY, comma-sep")
    # ticket 17 item 3: explicit directories + generator injection, so the
    # frozen families can never be re-run in place by accident
    ap.add_argument("--scenarios-dir", default=None,
                    help="override the scenario output directory")
    ap.add_argument("--matrix-dir", default=None,
                    help="override the pilot artifact directory")
    ap.add_argument("--generator", choices=("synthetic", "realwindow"),
                    default="synthetic", help="which generator to drive")
    ap.add_argument("--platform", default=None,
                    help="JSON file with the platform orbit (required for "
                         "--generator realwindow: the orbit is a registered "
                         "input, not something the driver may invent)")
    ap.add_argument("--s-factor", type=float, default=1.0,
                    help="ticket 48 demand sweep: pass through to run_pilot "
                         "which scales every task's rho_req_m by this factor "
                         "in memory (population fixed).  Each s point MUST "
                         "get its own --matrix-dir: the progress ledger and "
                         "the pilot artifacts are per-s-world.")
    args = ap.parse_args(argv)

    dirs = MatrixDirs()
    if args.scenarios_dir:
        dirs.scenarios = Path(args.scenarios_dir)
    if args.matrix_dir:
        dirs.matrix = Path(args.matrix_dir)
        dirs.progress = dirs.matrix / "_progress.json"

    generator = None
    platform = None
    if args.generator == "realwindow":
        if not args.platform:
            raise SystemExit(
                "--generator realwindow requires --platform (the orbit is a "
                "registered input)"
            )
        from datetime import datetime

        from sss_core.realwindows import KeplerianElement
        from sss_core.scenarios import generate_real_scenario

        generator = generate_real_scenario
        spec = json.loads(Path(args.platform).read_text(encoding="utf-8"))
        epoch = datetime.fromisoformat(spec["epoch"])
        platform = (
            KeplerianElement(
                semi_major_axis=float(spec["semi_major_axis_m"]),
                eccentricity=float(spec["eccentricity"]),
                inclination=math.radians(float(spec["inclination_deg"])),
                raan=math.radians(float(spec["raan_deg"])),
                arg_perigee=math.radians(float(spec["arg_perigee_deg"])),
                true_anomaly=math.radians(float(spec["true_anomaly_deg"])),
                epoch=epoch,
            ),
            epoch,
        )

    # the two families live in SEPARATE registries with different arities;
    # picking the wrong one is a silent shape error, not a KeyError
    registry = R_FAMILY_REGISTRY if args.generator == "realwindow"         else VARIANT_REGISTRY
    vmap = {}
    for tok in args.variants.split(","):
        vidx = int(tok.strip())
        if vidx not in registry:
            raise SystemExit(
                f"variant {vidx} is not in the {args.generator} registry "
                f"(available: {sorted(registry)})"
            )
        vmap[vidx] = registry[vidx]

    head = git_head()
    print(f"matrix code identity: git HEAD {head}", flush=True)

    progress = load_progress(dirs.progress)
    if progress is None:
        progress = {"schema": "matrix-progress/1.0", "code_head": head,
                    "pop": args.pop, "gen": args.gen,
                    "s_factor": args.s_factor, "units": {}}
    elif progress.get("code_head") != head:
        raise SystemExit(
            f"CODE IDENTITY CHANGED since matrix start: progress head "
            f"{progress['code_head']} != current {head}. Resume refused "
            f"(caliber mixing guard). Delete {dirs.progress} only after "
            f"deciding old artifacts are void."
        )
    elif (progress.get("pop"), progress.get("gen")) != (args.pop, args.gen):
        raise SystemExit(
            f"pop/gen changed since matrix start: progress "
            f"({progress.get('pop')},{progress.get('gen')}) != "
            f"({args.pop},{args.gen}). Refused (analysis_prereg.json)."
        )
    elif progress.get("s_factor", 1.0) != args.s_factor:
        # ticket 48: the order-scaling factor is part of a directory's
        # identity -- resuming a directory under a different s would keep
        # old-s artifacts as if they answered the new-s question.
        raise SystemExit(
            f"s_factor changed since matrix start: progress "
            f"({progress.get('s_factor', 1.0)}) != ({args.s_factor}). "
            f"Refused (each s point MUST live in its own --matrix-dir)."
        )

    paths = ensure_manifests(vmap, dirs=dirs, generator=generator, platform=platform)
    dirs.matrix.mkdir(parents=True, exist_ok=True)

    counts: dict[int, int] = {}
    empty_variants: set[str] = set()
    succeeded = 0
    for key, mpath in paths.items():
        rec = progress["units"].get(key)
        sha = manifest_sha1(mpath)
        code, seed_s = mpath.stem.split("_seed")
        expected_artifact = dirs.matrix / f"pilot_{code}_seed{seed_s}.json"
        if (
            rec is not None
            and rec.get("exit") == EXIT_OK
            and rec.get("manifest_sha1") == sha
            and expected_artifact.exists()
        ):
            succeeded += 1
            counts[EXIT_OK] = counts.get(EXIT_OK, 0) + 1
            continue

        t0 = time.monotonic()
        env = dict(os.environ, PYTHONHASHSEED="0")
        cmd = [sys.executable, str(dirs.pilot_script),
               "--manifest", str(mpath),
               "--seed", seed_s,
               "--pop", str(args.pop),
               "--gen", str(args.gen),
               "--out", str(dirs.matrix)]
        if args.s_factor != 1.0:
            cmd += ["--s-factor", str(args.s_factor)]
        proc = subprocess.run(
            cmd,
            env=env, capture_output=True, text=True,
        )
        wall = time.monotonic() - t0
        exit_code = proc.returncode
        counts[exit_code] = counts.get(exit_code, 0) + 1
        rec = {
            "manifest": _repo_relative(mpath),
            "manifest_sha1": sha,
            "exit": exit_code,
            "wall_s": round(wall, 1),
        }
        if exit_code == EXIT_OK:
            art = json.loads(expected_artifact.read_text(encoding="utf-8"))
            rec.update({
                "artifact": _repo_relative(expected_artifact),
                "front_size": art["front_size"],
                "anchor_f1_star": art["anchor_f1_star"],
                "max_f1_star": art["max_f1_star_on_front"],
                "promotion_decision": art["promotion"]["decision"],
                "promotion_spread_db": art["promotion"]["spread_db"],
            })
            succeeded += 1
        elif exit_code == 11:
            rec["note"] = "empty front (no feasible individual) -- recorded outcome"
            empty_variants.add(code)
        progress["units"][key] = rec
        atomic_write_json(dirs.progress, progress)
        lines = (proc.stdout or "").strip().splitlines()
        tail = lines[-1] if lines else (proc.stderr or "").strip().splitlines()[-1:]
        print(f"[{key}] exit={exit_code} wall={wall:.1f}s {tail}", flush=True)
        if exit_code == 10:
            print(f"GENERATION DEFECT at {key} (exit 10 zero-served)", flush=True)

    print("\n=== matrix summary ===", flush=True)
    print(f"code head: {head}", flush=True)
    by_variant: dict[str, dict[int, int]] = {}
    for key, rec in progress["units"].items():
        code = key.rsplit("_seed", 1)[0]
        by_variant.setdefault(code, {})
        by_variant[code][rec["exit"]] = by_variant[code].get(rec["exit"], 0) + 1
    for code in sorted(by_variant):
        print(f"{code}: {dict(sorted(by_variant[code].items()))}", flush=True)
    print(f"exit-code totals: {dict(sorted(counts.items()))}", flush=True)

    if any(e == 10 for e in counts):
        print("ALARM: exit-10 zero-served scenario present", flush=True)
        return EXIT_GENERATION_DEFECT
    if succeeded == 0:
        print("ALARM: zero units succeeded (silent-zero guard)", flush=True)
        return EXIT_ZERO_OUTPUT
    # exit 1 is run_pilot's SETUP-ERROR code -- a crash, never a normal outcome.
    # It used to be counted in the totals and then ignored, so a run in which
    # 11 of 40 units crashed still exited 0.  Measured on 2026-10-03: five
    # distinct real defects (anchor caliber, generator cascade caliber, C3/C4
    # caliber, AASR gate point-vs-window, promotion readout) all presented as
    # exit 1 and the first four runs reported success.  Ticket 48 review:
    # UNKNOWN codes (2 usage, 134/137 crashes, ...) were recorded but did not
    # influence the return -- only {0, 11} are outcomes, everything else
    # fails the run exactly like exit 1.
    unaccounted = sorted(e for e in counts if e not in (EXIT_OK, 11))
    if unaccounted:
        print(
            f"ALARM: unit exit code(s) {unaccounted} are crashes/setup errors, "
            "not outcomes -- the run is NOT clean. Re-run the affected units "
            "after fixing the cause; per-unit stderr is in the pilot "
            "subprocess output, not in this summary.",
            flush=True,
        )
        return EXIT_UNIT_SETUP_ERROR
    for code in empty_variants:
        if by_variant.get(code, {}).get(11, 0) == SEEDS_PER_VARIANT:
            print(f"ALARM: variant {code} empty front on all seeds", flush=True)
            return EXIT_VARIANT_EMPTY
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
