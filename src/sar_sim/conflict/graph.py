"""Conflict graph construction for CSP solvers.

Builds an undirected conflict graph where nodes are observation
windows (or scheduled observations) and edges represent conflicts.
"""

import networkx as nx
from typing import List, Dict, Any, Optional
from sar_sim.types import ObservationWindow, ScheduledObservation, Conflict
from sar_sim.conflict.temporal import find_conflicting_windows, detect_temporal_conflicts


def build_conflict_graph_windows(
    windows: List[ObservationWindow],
) -> nx.Graph:
    """Build a conflict graph from observation windows.

    Nodes: ObservationWindow objects
    Edges: temporal conflicts (overlapping windows on same satellite)

    Args:
        windows: all candidate observation windows

    Returns:
        networkx Graph with ObservationWindow as nodes
    """
    G = nx.Graph()

    # Add nodes
    for i, w in enumerate(windows):
        G.add_node(i, window=w, sat_id=w.satellite_id, target_id=w.target_id)

    # Add edges for conflicts
    for pair in find_conflicting_windows(windows):
        # Find node indices
        idx_a = windows.index(pair[0])
        idx_b = windows.index(pair[1])
        G.add_edge(idx_a, idx_b, conflict_type="temporal")

    return G


def build_conflict_graph_scheduled(
    observations: List[ScheduledObservation],
) -> nx.Graph:
    """Build a conflict graph from scheduled observations.

    Nodes: ScheduledObservation indices
    Edges: all detected conflicts

    Args:
        observations: list of scheduled observations

    Returns:
        networkx Graph
    """
    G = nx.Graph()

    for i, obs in enumerate(observations):
        G.add_node(i, observation=obs, sat_id=obs.satellite_id,
                    target_id=obs.target_id)

    conflicts = detect_temporal_conflicts(observations)

    # Build index lookup
    idx_map = {id(obs): i for i, obs in enumerate(observations)}

    for conflict in conflicts:
        idx_a = idx_map[id(conflict.obs_a)]
        idx_b = idx_map[id(conflict.obs_b)]
        G.add_edge(idx_a, idx_b, conflict_type=conflict.conflict_type)

    return G


def graph_statistics(G: nx.Graph) -> Dict[str, Any]:
    """Compute useful statistics about a conflict graph.

    Args:
        G: conflict graph

    Returns:
        dict with n_nodes, n_edges, density, max_degree, etc.
    """
    n = G.number_of_nodes()
    m = G.number_of_edges()

    max_possible_edges = n * (n - 1) / 2 if n > 1 else 0
    density = m / max_possible_edges if max_possible_edges > 0 else 0.0

    degrees = [d for _, d in G.degree()]
    max_degree = max(degrees) if degrees else 0
    avg_degree = sum(degrees) / len(degrees) if degrees else 0.0

    return {
        "n_nodes": n,
        "n_edges": m,
        "density": density,
        "max_degree": max_degree,
        "avg_degree": avg_degree,
    }
