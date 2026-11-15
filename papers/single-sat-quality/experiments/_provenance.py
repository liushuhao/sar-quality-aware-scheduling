#!/usr/bin/env python3
"""Shared provenance guard for cross-family / cross-variant result merging.

Every solver runner persists ``pkl_sha1`` per scenario (the SHA-1 of the
input pkl bytes). When downstream analysis merges two families by scenario
key — e.g. baseline vs MOEA-2, or ablation variant A vs B/C/D — the merged
records MUST originate from the same pkl bytes. A regenerated pkl set
(window fix, scenario tweak) applied to only one family silently changes
windows/targets and makes every paired comparison, significance test and
paper table meaningless.

This module is the single place that enforces that invariant. Legacy data
without ``pkl_sha1`` is treated as *unverifiable* (warn, do not fail); a
real mismatch is a hard error.
"""
from __future__ import annotations

import sys
from typing import Dict, Mapping, Tuple


def check_pkl_sha1_consistency(
    shas_by_source: Mapping[str, Mapping[str, str | None]],
    *,
    label: str = "cross-family",
) -> Tuple[int, int]:
    """Validate pkl_sha1 agreement across result sources, keyed by scenario.

    Args:
        shas_by_source: ``{source_label: {scenario_key: pkl_sha1_or_None}}``.
            Callers extract the sha from each source's record shape.
        label: human label for the error/warning lines.

    Returns:
        ``(n_mismatch, n_unverifiable)``. On mismatch > 0 prints details and
        calls ``sys.exit(1)`` — merging incomparable data must not proceed.
        Scenarios where no source has a sha (legacy data) increment
        ``n_unverifiable`` and produce a single warning, never an error.
    """
    all_keys = set()
    for table in shas_by_source.values():
        all_keys.update(table.keys())

    mismatches = []
    unverifiable = 0
    for key in all_keys:
        present = {
            src: table[key]
            for src, table in shas_by_source.items()
            if key in table and table.get(key)
        }
        if not present:
            unverifiable += 1
            continue
        if len(set(present.values())) > 1:
            mismatches.append((key, present))
        elif len(present) < len([s for s in shas_by_source if key in shas_by_source[s]]):
            unverifiable += 1

    if mismatches:
        print(f"\n!! {label} pkl_sha1 MISMATCH on {len(mismatches)} scenario(s):",
              file=sys.stderr)
        for key, present in mismatches[:10]:
            print(f"   {key}: "
                  + ", ".join(f"{s}={v[:8]}" for s, v in present.items()),
                  file=sys.stderr)
        print("   Sources ran on different scenario pkls — refusing to merge.",
              file=sys.stderr)
        print("   Rerun the stale family/variant with --no-resume so all share "
              "the same pkls.", file=sys.stderr)
        sys.exit(1)

    if unverifiable:
        print(f"  [warn] {unverifiable} scenarios lack pkl_sha1 in one+ source "
              f"(legacy data); {label} provenance not fully verifiable.")
    elif all_keys:
        print(f"  pkl_sha1 consistent across all {len(all_keys)} scenarios "
              f"({len(shas_by_source)} sources, {label}).")

    return len(mismatches), unverifiable
