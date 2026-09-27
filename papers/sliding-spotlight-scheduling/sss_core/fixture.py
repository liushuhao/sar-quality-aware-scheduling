"""Kim 2021 platform fixture loader -- unique source of platform numbers.

spec D3 (gate-review R4): every platform parameter (squint envelope, SAT
calibration, actuator limits, resolution grade anchor) is REFERENCED from
``experiments/platform_kim2021.json``; copying numbers into code is
forbidden.  Quantities Kim does not publish (V_s, R0, D, A, r0) are DERIVED
in :mod:`sss_core.geometry` / :mod:`sss_core.modes` and are SANITY-layer
per formula-spec v1.0.1 §7 -- they may back band / identity assertions
only, never tight literature fits, and once frozen they are not retuned
(retuning = new blocking gate, formula-spec §7(d)).
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

FORK_DOMAIN = Path(__file__).resolve().parent.parent
FIXTURE_PATH = FORK_DOMAIN / "experiments" / "platform_kim2021.json"


@lru_cache(maxsize=1)
def load_platform_fixture() -> dict:
    """Load and cache the frozen Kim 2021 platform fixture (ticket 02)."""
    with open(FIXTURE_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def fixture_value(node: dict, key: str):
    """Fetch ``node[key]["value"]``; null values fail loud (ticket 02 rule)."""
    entry = node[key]
    if entry.get("value") is None:
        raise ValueError(
            f"platform fixture field {key!r} is null (NOT PUBLISHED by Kim); "
            "inventing a value is forbidden -- source it and write back to "
            "the fixture/manifest first (platform_kim2021.json rule)"
        )
    return entry["value"]
