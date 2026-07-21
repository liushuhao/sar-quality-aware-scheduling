"""Conflict detection package."""

from sar_sim.conflict.temporal import (
    time_overlap,
    detect_temporal_conflicts,
    find_conflicting_windows,
)
from sar_sim.conflict.resource import (
    detect_resource_overuse,
    ResourceBudget,
)
from sar_sim.conflict.graph import (
    build_conflict_graph_windows,
    build_conflict_graph_scheduled,
    graph_statistics,
)
