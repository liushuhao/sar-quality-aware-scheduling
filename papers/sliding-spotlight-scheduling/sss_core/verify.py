"""Paper-2 verify gate (spec D11, ticket 12): evidence chain + replay.

Step model: every check returns ``{"step", "status", "detail"}`` with
status in {PASS, FAIL, REPORT}.  REPORT items (the A6 insurance action)
do NOT fail the gate -- they are escalation records the analysis layer
must answer ("口径重议上报", never self-adjusted).  Gate exit: 0 = no FAIL,
20 = at least one FAIL (runner-level D11 codes 10/11 stay with run_pilot).

Steps (D12-5):
  m1_double_check      tag-diff + worktree emptiness of src/sar_sim
  shared_lib_tests     PYTHONPATH=src pytest src/tests: passed == 154 == N0
                       AND failed == 0 AND exit 0 (three conditions)
  grid_halving         AASRGrid.halving_stability, sampling program
                       preregistered (Random(20260927), uniform in axes
                       and PRF keys, 20 samples -- the ticket-06 test
                       program, same seed)
  predicate_source     the C2 requirement resolves to sss_core.predicates
  promotion_replay     recompute per-candidate unenforced AASR from the
                       pilot's STARTS + manifest (never trusting stored
                       values), derive the decision, compare with the
                       recorded one (US12)
  aasr_headroom        anti-fixture: unenforced AASR CAN exceed -13 dB on
                       synthetic high-squint candidates (never asserted on
                       M1NC -- its tasks passed the generation gate)
  scatter_precheck     A6 insurance: within-window vs cross-task f_Q
                       dispersion ratio (< 0.1 triggers the preregistered
                       口径重议 escalation; with D05-4 time invariance the
                       within-scatter is structurally ~2e-4 relative -- a
                       known outcome, recorded not discovered)
  anchor_crosscheck    pilot front max f1* >= greedy-anchor f1* - 1e-9
                       (the double-chain check that exposed the ticket-10
                       C2 ordering defect)
  snapshot_rebuild     rerun run_nsga2 from manifest + seed honoring
                       anchor_seeded; front must reproduce bit-exactly
"""
from __future__ import annotations

import json
import math
import random
import subprocess
import sys
from pathlib import Path

from .aasr import AASRGrid, aasr_direct
from .anchor import anchor_on_manifest
from .geometry import squint_at
from .modes import Mode, ModeLibrary

FORK_DOMAIN = Path(__file__).resolve().parent.parent
REPO_ROOT = FORK_DOMAIN.parent.parent
M1_TAG = "paper2-m1-baseline"
SHARED_LIB_N0 = 154          # 145 -> 154 on 2026-10-05 (ticket 26 added 9)

PROMOTION_THRESHOLD_DB = 6.0  # mirrored from experiments/promotion_prereg.json
A6_SCATTER_RATIO_THRESHOLD = 0.1  # spec D10 preregistration

EXIT_PASS = 0
EXIT_FAIL = 20


def _step(name: str, status: str, detail) -> dict:
    return {"step": name, "status": status, "detail": detail}


FORK_SOURCE_FILES = (
    "src/sar_sim/metrics/nesz.py",
    "src/sar_sim/generator/orbit.py",
    "src/sar_sim/generator/visibility.py",
    "src/sar_sim/generator/target.py",
)


def m1_double_check() -> dict:
    """Fork-source integrity: the FORK_MANIFEST F-01/F-02 SOURCE files are
    byte-identical to the M1 tag AND the shared-lib worktree is clean; git
    return codes are checked explicitly (a missing tag must FAIL loudly,
    not silently produce an empty diff, D12-5).

    Ticket 26 (2026-10-05, user-adjudicated exception to the shared-lib
    read-only red line) narrowed this check from the whole ``src/sar_sim``
    tree to the fork-copied SOURCE files: ``constraints.py`` and
    ``so_f1.py`` legitimately evolve, while the four files the fork's
    identity is built from must not.  The behavioural fork guards
    (seven-tuple bit-identity, fork-scope AST, self-containment) remain
    authoritative and live in the fork-identity test modules."""
    for argv in (
        ["git", "diff", f"{M1_TAG}..HEAD", "--", *FORK_SOURCE_FILES],
        ["git", "status", "--porcelain", "src/sar_sim"],
    ):
        proc = subprocess.run(argv, cwd=REPO_ROOT, capture_output=True, text=True)
        if proc.returncode != 0:
            return _step("m1_double_check", "FAIL",
                         f"git failed ({proc.returncode}): {proc.stderr.strip()}")
        if proc.stdout.strip():
            return _step("m1_double_check", "FAIL",
                         f"non-empty: {argv}: {proc.stdout[:400]}")
    return _step("m1_double_check", "PASS",
                 f"fork source files identical to {M1_TAG} AND src/sar_sim worktree clean")


def claim_provenance() -> dict:
    """Claim-level provenance for the frozen formula source.

    Distinct from the shared-library suite: this asks whether the cited
    sources actually SAY what formula-spec.md attributes to them.  The
    existence gate (src/tools/check_citation_exists.py) cannot see that
    class of defect -- a real paper can contradict itself, or be cited for
    a passage it does not contain.

    rc mapping is explicit because the failure modes are not equivalent:
      0 -> PASS    every registered claim verified
      1 -> FAIL    a claim's quote is absent from its cited page
      2 -> REPORT  literature/ absent (gitignored; fresh clone cannot verify)
      3 -> FAIL    usage error or empty registry -- verifies nothing
    Anything else (including a crash) is FAIL: a gate that silently
    degrades to green is worse than no gate.

    The rc=2 downgrade is a user decision (2026-10-02): the standalone
    script keeps its hard rc=2, but inside the gate a missing source is a
    recorded non-failure so a fresh clone is not permanently blocked.
    Detail uses `restore_required`, NOT `action_required` -- the latter is
    scanned across all steps (verify.py:322) and drives a hardcoded A6
    message in run_verify.py.
    """
    script = FORK_DOMAIN / "scripts" / "verify_claim_traces.py"
    if not script.is_file():
        return _step("claim_provenance", "FAIL", f"verifier missing: {script}")
    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8",
        )
    except OSError as exc:
        return _step("claim_provenance", "FAIL", f"verifier would not run: {exc}")

    rc = proc.returncode
    if rc == 0:
        status = "PASS"
    elif rc == 2:
        status = "REPORT"
    else:
        status = "FAIL"
    tail = proc.stdout.strip().splitlines()[-1:] if proc.stdout.strip() else []
    return _step("claim_provenance", status, {
        "exit": rc,
        "restore_required": rc == 2,
        "summary": tail[0] if tail else proc.stderr.strip()[:300],
    })


def shared_lib_tests() -> dict:
    """Full shared-library suite: collected == 154 == N0, failed == 0,
    exit 0 -- three conditions, all required."""
    import os

    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "src/tests/", "-q", "-p", "no:cacheprovider"],
        cwd=REPO_ROOT, capture_output=True, text=True, env=env,
    )
    import re

    tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    m_p = re.search(r"(\d+) passed", tail)
    m_f = re.search(r"(\d+) failed", tail)
    passed = int(m_p.group(1)) if m_p else 0
    failed = int(m_f.group(1)) if m_f else 0
    # Exact on purpose, not an oversight: unlike DOMAIN_N0 (a floor since ticket
    # 46) the shared-library suite has sat at 154 since 2026-10-05, so a count
    # change here IS the signal.  Ticket 46 scoped the floor to the domain suite.
    ok = proc.returncode == 0 and passed == SHARED_LIB_N0 and failed == 0
    detail = {"exit": proc.returncode, "passed": passed, "failed": failed,
              "expected_n0": SHARED_LIB_N0, "tail": tail}
    return _step("shared_lib_tests", "PASS" if ok else "FAIL", detail)


DOMAIN_N0 = 376          # FLOOR, not an equality (ticket 46); 376 passed + 1
                        # skip as measured on 2026-10-15.  See domain_counts_ok()
                        # for why a floor and for what it still does not catch.
DOMAIN_N0_SKIPPED = 1    # baseline conditional skip -- silent removal reads red
# 2026-10-06: 0, was 1.  The R12 exit-11 marker was retired into a real pass by
# ticket 25, and tickets 24/25/26/28 added tests; pin now equals the measured
# suite (223 passed + 1 skipped, no xfail anywhere in the fork).
# 2026-10-06 later the same day: 223 -> 228.  Ticket 30 (e) extended
# test_run_lineage_completeness.py from 6 tests to 11 (the v2_results /
# v3_results registration checks plus a phantom-sibling-directory check), and a
# guard that is mandated by the ticket cannot be added without moving this pin.
# Measured by stashing the guard file and re-running --collect-only: HEAD
# collects 224, the extended guard collects 229.
DOMAIN_N0_XFAILED = 0


def domain_counts_ok(passed: int, failed: int, skipped: int, xfailed: int) -> bool:
    """Do the DOMAIN suite's *counts* match the baseline? (ticket 46)

    Extracted so the gate's contract is unit-testable without a 22-minute run.
    The process exit code stays with the caller -- this is about counts only.

    ``passed`` is a FLOOR, not an equality.  The suite is expected to grow, and
    an exact pin fired on every addition, forcing a re-pin each time (tickets 29
    f546573, 30, 40, 44).  A floor detects the failure that matters -- tests
    silently disappearing: a net decrease drops below it exactly as reliably as
    it breaks equality -- without the false alarm on additions.

    Known blind spot, stated rather than implied: a floor also passes on an
    *accidental net increase* (a duplicated collection, or bad tests replacing
    good ones and making up the count).  Catching 1:1 replacement would mean
    pinning test node-ids or their hash -- a different order of change, not done
    here.

    ``failed``/``skipped``/``xfailed`` stay exact: they encode known conditions
    (zero failures, one conditional skip), so any drift there is itself signal.
    """
    return (
        failed == 0
        and passed >= DOMAIN_N0
        and skipped == DOMAIN_N0_SKIPPED
        and xfailed == DOMAIN_N0_XFAILED
    )


def domain_tests() -> dict:
    """The DOMAIN suite (papers/sliding-spotlight-scheduling/tests/).

    Ticket 17 acceptance item 14.  The gate previously ran only the shared
    library, so "gate PASS" said nothing about the artifacts it exists to
    police -- the two suites are disjoint by construction.

    Counted the same way as ``shared_lib_tests``: collected == N0, zero
    failed, exit 0.  The expected count is pinned so a silent collection
    failure (this project has hit ``No tests collected`` reporting exit 0
    under a wrapped interpreter) cannot read as a pass.

    The full domain suite takes ~18 min because the +/-45 deg AASR grid is
    built several times, so this step is opt-out via ``run_shared_tests``
    style flags rather than always-on in the light invocations.
    """
    import os
    import re

    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    suite = str(FORK_DOMAIN / "tests")
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "pytest", suite, "-q", "-p", "no:cacheprovider"],
        cwd=REPO_ROOT, capture_output=True, text=True, env=env,
    )
    tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    m_p = re.search(r"(\d+) passed", tail)
    m_f = re.search(r"(\d+) failed", tail)
    # The quiet tail carries no "collected" figure, so the gate pins the
    # PASSED count plus the baseline non-pass pair explicitly: a silent
    # collection loss drops `passed`, and removing the known skip/xfail
    # (the R12 marker) must read red just the same.  The pre-ticket-23
    # condition `collected = passed + failed == N0` was unsatisfiable
    # whenever the suite carried its 1 skipped + 1 xfail -- first exposed
    # when ticket 23 raised the pin.
    m_s = re.search(r"(\d+) skipped", tail)
    m_x = re.search(r"(\d+) xfailed", tail)
    passed = int(m_p.group(1)) if m_p else 0
    failed = int(m_f.group(1)) if m_f else 0
    skipped = int(m_s.group(1)) if m_s else 0
    xfailed = int(m_x.group(1)) if m_x else 0
    ok = proc.returncode == 0 and domain_counts_ok(
        passed, failed, skipped, xfailed
    )
    detail = {
        "exit": proc.returncode, "passed": passed, "failed": failed,
        "skipped": skipped, "xfailed": xfailed,
        "expected_n0": DOMAIN_N0, "tail": tail,
    }
    return _step("domain_tests", "PASS" if ok else "FAIL", detail)


def grid_halving(lib: ModeLibrary, n_samples: int = 20) -> dict:
    """Preregistered sampling program (ticket-06 test program, same seed):
    Random(20260927), uniform within axes + uniform PRF keys.

    Ticket 15: the psi draw follows the grid axis instead of a hardcoded
    +-12 deg.  The old literal covered 24 of the new 90 deg domain (26.7%),
    so `halving_stability` could report PASS while blind to exactly the
    regime the expansion stresses -- the subtlest of the seven +-12 sites.

    The draw is MODE-AWARE (punch 7): the grid's psi axis spans +-45 deg, but
    a sample routed to SLS is only meaningful inside that mode's 26.9 deg
    sliding boundary.  Drawing psi uniformly over the whole axis and letting
    `_domain_check` reject the out-of-envelope ones would make this gate fail
    for a domain reason rather than a density reason, and -- worse -- it would
    silently shrink the effective sample count below the preregistered 20.
    Each sample therefore draws psi inside its own routed mode's envelope.
    """
    rng = random.Random(20260927)
    from .aasr import PRF_KEYS_HZ, PSI_AXIS_DEG_DEFAULT, RHO_REQ_AXIS_DEFAULT
    from .duration import SLS_MAX_SQUINT_DEG, SQUINT_ENVELOPE_DEG
    from .aasr import route_mode

    samples = []
    for _ in range(n_samples):
        rho = rng.uniform(RHO_REQ_AXIS_DEFAULT[0], RHO_REQ_AXIS_DEFAULT[-1])
        try:
            mode = route_mode(rho, lib)
        except ValueError:
            continue  # unserviceable requirement; not a grid sample
        env = SLS_MAX_SQUINT_DEG if mode is Mode.SLS else SQUINT_ENVELOPE_DEG
        samples.append(
            (
                rho,
                math.radians(rng.uniform(-env, env)),
                rng.uniform(0.0, 0.9),
                rng.choice(PRF_KEYS_HZ),
            )
        )
    if len(samples) < n_samples:
        raise ValueError(
            f"sampling program produced {len(samples)} of {n_samples} preregistered "
            "grid samples -- the draw is vacuous and must not be scored"
        )
    grid = AASRGrid(lib)
    report = grid.halving_stability(samples)
    ok = report["within_preregistered_bound"]
    return _step("grid_halving", "PASS" if ok else "FAIL", report)


def v2_artifacts_present() -> dict:
    """Ticket 17 acceptance item 12: the real-window results must be
    traceable to their artifacts.

    Checks that the v2 artifacts exist and that the convergence report is
    PRESENT ALONGSIDE the results table -- a richness statement without its
    ladder evidence is not a claim (freeze red line), so a table without its
    report is an inadmissible state, not a partial success.
    """
    base = FORK_DOMAIN / "experiments" / "v2_results"
    table = base / "results_table.json"
    conv = base / "convergence_report.json"
    detail = {"results_table": table.is_file(), "convergence_report": conv.is_file()}
    if not detail["results_table"]:
        return _step("v2_artifacts", "FAIL", dict(detail, note="results table missing"))
    if not detail["convergence_report"]:
        return _step(
            "v2_artifacts", "FAIL",
            dict(detail, note="convergence report missing -- a richness claim "
                             "without ladder evidence is inadmissible"),
        )
    rep = json.loads(table.read_text(encoding="utf-8"))
    convd = json.loads(conv.read_text(encoding="utf-8"))
    detail["families"] = sorted(rep.get("families", {}))
    detail["verdicts"] = {
        f: v.get("convergence", v.get("convergence_verdict"))
        for f, v in convd.get("verdicts", {}).items()
    }
    ok = bool(detail["families"]) and set(detail["families"]) == set(detail["verdicts"])
    return _step("v2_artifacts", "PASS" if ok else "FAIL", detail)


def caliber_registry_present() -> dict:
    """Ticket 17 acceptance item 12: the frozen families must carry a caliber
    tag, so a v1 number can never be read as current."""
    reg = FORK_DOMAIN / "experiments" / "caliber_registry.json"
    if not reg.is_file():
        return _step("caliber_registry", "FAIL", {"note": "caliber registry missing"})
    data = json.loads(reg.read_text(encoding="utf-8"))
    cals = data.get("calibers", {})
    ok = {"v1", "v2"} <= set(cals) and all(
        cals[c].get("comparable_to_" + ("v2" if c == "v1" else "v1")) is False
        for c in ("v1", "v2")
    )
    return _step(
        "caliber_registry", "PASS" if ok else "FAIL",
        {"calibers": sorted(cals), "cross_comparable": False if ok else "unset"},
    )


def predicate_source() -> dict:
    """Ticket-09 acceptance item: the C2 requirement resolves to
    sss_core.predicates and the evaluator hook confirms it."""
    from . import predicates
    from . import evaluator as ev

    ok = (
        predicates.c2_transfer_requirement_s.__module__ == "sss_core.predicates"
        and ev.SchedulingProblem.c2_uses_predicate_source(object.__new__(ev.SchedulingProblem))
    )
    return _step("predicate_source", "PASS" if ok else "FAIL",
                 {"c2_module": predicates.c2_transfer_requirement_s.__module__})


def promotion_replay(pilot: dict, manifest: dict, lib: ModeLibrary) -> dict:
    """US12: recompute the criterion from STARTS + manifest (raw data) and
    compare the derived decision with the recorded one."""
    sp_plans = {int(i): p for i, p in enumerate(_plans_of(manifest, lib))}
    vals = []
    for rec in pilot["front"]:
        cand_max = None
        for i_str, start in rec["starts"].items():
            plan = sp_plans[int(i_str)]
            # ticket 25: per-window zero and slant range at the start
            w = plan.window_at(start)
            psi = squint_at(start, w.t_ca_s, lib.geo, r0_m=w.r0_m)
            try:
                db = aasr_direct(
                    plan.mode, psi, lib.geo.k, plan.prf_hz, lib,
                    spt_scene_wa_m=(plan.azimuth_size_m if plan.mode is Mode.SPT else None),
                    r0_m=w.r0_m,
                )["aasr_db"]
            except ValueError:
                # unenforced readout outside the sliding family: infinitely
                # bad AASR, not a crash (D12-3 semantics) -- mirrors
                # nsga2.py promotion_spread_db verbatim; without this catch
                # the finite-exclusion branch below is dead code.  Ticket
                # 40: unreachable for k < 1; defensive retention.
                db = float("inf")
            cand_max = db if cand_max is None else max(cand_max, db)
        if cand_max is not None:
            vals.append(cand_max)
    # must mirror promotion_spread_db exactly (nsga2.py), including the
    # out-of-domain exclusion -- this step exists to re-derive the decision
    # independently, so any divergence between the two would surface as a
    # spurious mismatch rather than as a real drift
    finite = [v for v in vals if math.isfinite(v)]
    n_infinite = len(vals) - len(finite)
    spread = (max(finite) - min(finite)) if len(finite) >= 2 else 0.0
    derived = "promote" if spread >= PROMOTION_THRESHOLD_DB else "no_promotion"
    if n_infinite:
        derived = f"{derived} (excluded {n_infinite} out-of-domain candidate(s))"
    recorded = pilot["promotion"]["decision"]
    ok = derived == recorded
    return _step("promotion_replay", "PASS" if ok else "FAIL",
                 {"recomputed_spread_db": spread, "derived_decision": derived,
                  "recorded_decision": recorded,
                  "threshold_db": PROMOTION_THRESHOLD_DB})


def aasr_headroom(lib: ModeLibrary) -> dict:
    """Anti-fixture (US12 second half): unenforced AASR can exceed -13 dB.
    Synthetic high-squint SLS candidates -- never M1NC data (its tasks
    passed the generation-time AASR gate)."""
    from .aasr import AASR_THRESHOLD_DB

    vals = [
        aasr_direct(Mode.SLS, math.radians(psi), 0.1, 1150.0, lib)["aasr_db"]
        for psi in (0.0, 6.0)
    ]
    ok = max(vals) > AASR_THRESHOLD_DB
    return _step("aasr_headroom", "PASS" if ok else "FAIL",
                 {"synthetic_max_db": max(vals), "threshold_db": AASR_THRESHOLD_DB,
                  "note": "threshold-capped scatter would kill the promotion"})


def scatter_precheck(manifest: dict, lib: ModeLibrary) -> dict:
    """A6 insurance (REPORT item): within-window vs cross-task f_Q
    dispersion ratio.  D05-4 makes the within-scatter structurally ~2e-4
    relative -- the escalation is a KNOWN outcome, recorded not discovered."""
    from .quality import f_q_per_task

    within, means = [], []
    for t in manifest["tasks"]:
        mode = Mode[t["mode"]]
        # ticket 25: per-window sampling -- each transit window uses its own
        # zero and slant range.  Legacy manifests (no ``windows`` field) keep
        # the original single-window triad read.
        if "windows" in t:
            win_specs = [
                (
                    float(w["lo_s"]), float(w["hi_s"]), float(w["t_ca_s"]),
                    w.get("r0_m"),
                )
                for w in t["windows"]
            ]
        else:
            win_specs = [(
                float(t["t_start_s"]), float(t["t_end_s"]), float(t["t_ca_s"]),
                t.get("r0_m"),
            )]
        for t0, t1, tca, r0_t in win_specs:
            r_m = lib.geo.R0_m if r0_t is None else float(r0_t)
            vals = [
                f_q_per_task(mode, squint_at(tt, tca, lib.geo, r0_m=r0_t), r_m, lib)
                for tt in (t0, 0.5 * (t0 + t1), t1)
            ]
            mu = sum(vals) / len(vals)
            within.append(math.sqrt(sum((v - mu) ** 2 for v in vals) / len(vals)))
            means.append(mu)
    mu_all = sum(means) / len(means)
    cross = math.sqrt(sum((m - mu_all) ** 2 for m in means) / len(means))
    ratio = (sum(within) / len(within)) / cross if cross > 0 else 0.0
    triggered = ratio < A6_SCATTER_RATIO_THRESHOLD
    return _step(
        "scatter_precheck", "REPORT",
        {
            "ratio": ratio,
            "threshold": A6_SCATTER_RATIO_THRESHOLD,
            "escalation": "口径重议上报 (preregistered A6 action; do NOT self-adjust)",
            "structural_note": (
                "consistent with D05-4 f_Q time invariance and the A6 "
                "steel-man ruling -- a known outcome, not a new finding"
            ),
            "action_required": triggered,
            "per_mode_mean_f_q": _per_mode_means(manifest, lib),
        },
    )


def _per_mode_means(manifest: dict, lib: ModeLibrary) -> dict:
    from .quality import f_q_per_task

    acc: dict[str, list] = {}
    for t in manifest["tasks"]:
        mode = Mode[t["mode"]]
        r0_t = t.get("r0_m")
        q = f_q_per_task(
            mode, 0.0, lib.geo.R0_m if r0_t is None else float(r0_t), lib
        )
        acc.setdefault(mode.name, []).append(q)
    return {k: sum(v) / len(v) for k, v in acc.items()}


def anchor_crosscheck(pilot: dict, manifest: dict, lib: ModeLibrary) -> dict:
    """Double-chain check (rule 11): the front's best coverage must reach
    the greedy anchor's f1* (the anchor individual is seeded, CV-clean and
    elitist-survives).  This exposed the ticket-10 C2 ordering defect."""
    anchor = anchor_on_manifest(manifest, lib)
    front_max = max(r["f1_star"] for r in pilot["front"]) if pilot["front"] else 0.0
    ok = front_max >= anchor.f1_star - 1e-9
    return _step("anchor_crosscheck", "PASS" if ok else "FAIL",
                 {"front_max_f1_star": front_max, "anchor_f1_star": anchor.f1_star,
                  "anchor_served": len(anchor.starts)})


def snapshot_rebuild(pilot: dict, manifest_path: Path, lib: ModeLibrary,
                     pop_size: int, generations: int) -> dict:
    """Rebuild the run from manifest + seed and compare front structures
    bit-exactly (JSON-roundtripped floats).  Honors the anchor_seeded flag
    (D12-2)."""
    from .nsga2 import encode_seed_individual, run_nsga2
    from .evaluator import SchedulingProblem

    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    seeded = bool(pilot.get("anchor_seeded"))
    seed_vec = None
    anchor_f1 = None
    if seeded:
        anchor = anchor_on_manifest(manifest, lib)
        seed_vec = encode_seed_individual(SchedulingProblem(manifest, lib), anchor.starts)
        anchor_f1 = anchor.f1_star
    res = run_nsga2(manifest, lib, seed=pilot["seed"], pop_size=pop_size,
                    generations=generations, seed_individual=seed_vec,
                    anchor_f1_star=anchor_f1)
    fresh = json.loads(json.dumps(
        [(r["f1_star"], r["f_q"], r["starts"]) for r in res.front], sort_keys=True))
    stored = json.loads(json.dumps(
        [(r["f1_star"], r["f_q"], r["starts"]) for r in pilot["front"]], sort_keys=True))
    ok = fresh == stored
    return _step("snapshot_rebuild", "PASS" if ok else "FAIL",
                 {"front_size": len(res.front), "anchor_seeded": seeded})


def _plans_of(manifest: dict, lib: ModeLibrary):
    from .evaluator import precompile_tasks

    return precompile_tasks(manifest, lib)


def run_gate(pilot_path: Path, manifest_path: Path,
             lib: ModeLibrary | None = None,
             pop_size: int = 40, generations: int = 60,
             steps: list[str] | None = None,
             run_shared_tests: bool = True) -> tuple[dict, int]:
    """Assemble the full gate; ``steps`` selects a subset (tests),
    ``run_shared_tests`` may be disabled for light invocations.  Returns
    (report, exit_code)."""
    lib = lib or ModeLibrary.from_fixture()
    pilot = json.loads(Path(pilot_path).read_text(encoding="utf-8"))
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))

    registry = {
        "m1_double_check": lambda: m1_double_check(),
        "shared_lib_tests": lambda: shared_lib_tests(),
        "domain_tests": lambda: domain_tests(),
        "v2_artifacts": lambda: v2_artifacts_present(),
        "caliber_registry": lambda: caliber_registry_present(),
        "claim_provenance": lambda: claim_provenance(),
        "grid_halving": lambda: grid_halving(lib),
        "predicate_source": lambda: predicate_source(),
        "promotion_replay": lambda: promotion_replay(pilot, manifest, lib),
        "aasr_headroom": lambda: aasr_headroom(lib),
        "scatter_precheck": lambda: scatter_precheck(manifest, lib),
        "anchor_crosscheck": lambda: anchor_crosscheck(pilot, manifest, lib),
        "snapshot_rebuild": lambda: snapshot_rebuild(
            pilot, manifest_path, lib, pop_size, generations),
    }
    order = list(registry) if steps is None else steps
    results = []
    for name in order:
        if name == "shared_lib_tests" and not run_shared_tests:
            results.append(_step("shared_lib_tests", "SKIPPED",
                                 "disabled for light invocation"))
            continue
        if name in ("domain_tests", "v2_artifacts", "caliber_registry")                 and not run_shared_tests:
            results.append(_step("domain_tests", "SKIPPED",
                                 "disabled for light invocation"))
            continue
        results.append(registry[name]())
    fails = [r for r in results if r["status"] == "FAIL"]
    report = {
        "schema": "verify-report/1.0",
        "pilot": str(pilot_path),
        "manifest": str(manifest_path),
        "steps": results,
        "n_pass": sum(1 for r in results if r["status"] == "PASS"),
        "n_report": sum(1 for r in results if r["status"] == "REPORT"),
        "n_fail": len(fails),
        "action_required": any(
            r["detail"].get("action_required")
            for r in results
            if isinstance(r["detail"], dict)
        ),
    }
    return report, (EXIT_FAIL if fails else EXIT_PASS)
