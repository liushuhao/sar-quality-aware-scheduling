#!/usr/bin/env python3
"""Resident mirror-sync gate: main.tex <-> full.md <-> sections/*.md.

The paper has three faces: the editing surface ``paper/main.tex`` and two
downstream markdown mirrors (``paper/full.md`` and ``paper/sections/*.md``)
that the review seats read.  Every prose fix must land on all faces; this
gate mechanically checks that agreed fix forms stay landed: stale wordings
must be absent everywhere (expect 0) and their replacements present with the
pinned multiplicity (expect N, usually 1 -- a uniqueness probe also catches
confirmation-round double-applications).

Probes live in ``sync_mirrors_probes.json`` next to this script; fix waves
append entries there instead of writing throwaway probe scripts.  Each entry
pins: faces, the literal needle (exact substring, no regex), the expected
count, and an optional per-face ``override`` needle for tex-vs-markdown
divergence (``~pp`` vs `` pp``).  A ``why`` field records the wave/commit.

Usage (repo root, absolute python per FORK_MANIFEST):
    "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/sync_mirrors_check.py
    ... or pass a registry path as argv[1] (mutation tests).

rc: 0 every probe passes on every face; 1 at least one probe fails;
    2 structural error (registry unreadable / face file missing).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = Path(__file__).resolve().parent / "sync_mirrors_probes.json"


def load_registry(path: Path) -> dict:
    try:
        reg = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"ABORT rc=2: registry unreadable: {exc}")
    faces, probes = reg.get("faces"), reg.get("probes")
    if not isinstance(faces, dict) or not isinstance(probes, list) or not probes:
        raise SystemExit("ABORT rc=2: registry needs non-empty faces{} and probes[]")
    return reg


def main() -> int:
    reg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_REGISTRY
    reg = load_registry(reg_path)
    faces = {k: FORK / v for k, v in reg["faces"].items()}

    texts: dict[str, str] = {}
    checks = fails = 0
    for probe in reg["probes"]:
        pid, needle, expect = probe["id"], probe["needle"], int(probe["expect"])
        overrides = probe.get("override", {})
        for face in probe["faces"]:
            if face not in faces:
                print(f"ABORT rc=2: {pid}: unknown face {face!r}")
                return 2
            if face not in texts:
                p = faces[face]
                if not p.is_file():
                    print(f"ABORT rc=2: {pid}: face file missing: {p}")
                    return 2
                texts[face] = p.read_text(encoding="utf-8")
            got = texts[face].count(overrides.get(face, needle))
            checks += 1
            if got != expect:
                fails += 1
                print(f"FAIL {pid} [{face}]: {got} hits (want {expect}) "
                      f"for {overrides.get(face, needle)[:60]!r}")

    print(f"=== sync mirrors: {checks - fails}/{checks} probe-face checks "
          f"pass across {len(reg['probes'])} probes ===")
    if fails:
        print("VERDICT: mirror sync broken -- a fix form drifted")
        return 1
    print("VERDICT: all faces agree with the registered fix forms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
