"""CBBA (Consensus-Based Bundle Algorithm) for constellation SAR scheduling.

Implements the distributed auction algorithm from:
  Choi, H. L., Brunet, L., & How, J. P. (2009).
  Consensus-based decentralized auctions for robust task allocation.
  IEEE Trans. Robotics, 25(4), 912-926.

Interface:
  cbba_solver(windows, targets, n_sats, max_rounds=10, bundle_size=20) -> dict
"""

import math
from typing import List, Dict


# Reference incidence angle for quality normalization (degrees)
_THETA_REF_DEG = 30.0
_THETA_REF_RAD = math.radians(_THETA_REF_DEG)
_COS3_THETA_REF = math.cos(_THETA_REF_RAD) ** 3


def _quality(theta_rad: float) -> float:
    """Compute normalized quality q(theta) = cos^3(theta) / cos^3(theta_ref)."""
    cos_theta = math.cos(theta_rad)
    if cos_theta <= 1e-15:
        return 0.0
    return (cos_theta ** 3) / _COS3_THETA_REF


def compute_score(target: Dict, theta_rad: float) -> float:
    """Compute CBBA bid score: p_i * q(theta_i).

    Args:
        target: dict with 'priority' key (default 1.0)
        theta_rad: incidence angle in radians

    Returns:
        priority * quality_score
    """
    priority = target.get("priority", 1.0)
    return priority * _quality(theta_rad)


# ═══════════════════════════════════════════════════════════════════════════
# CBBA Agent
# ═══════════════════════════════════════════════════════════════════════════

class _CBBAAgent:
    """Internal agent representing a single satellite in CBBA."""

    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        self.bundle: List[int] = []      # ordered list of target_ids
        self.path: List[Dict] = []       # corresponding window dicts
        self.winner_bids: Dict[int, float] = {}   # target_id -> best bid
        self.winner_agents: Dict[int, int] = {}   # target_id -> best agent_id

    def build_bundle(
        self,
        targets: List[Dict],
        windows_by_target: Dict[int, List[Dict]],
        bundle_size: int,
    ) -> bool:
        """Rebuild this agent's bundle greedily.

        Returns True if any change was made to the bundle.
        """
        changed = False

        while len(self.bundle) < bundle_size:
            best_tid = -1
            best_score = 0.0
            best_window = None

            for target in targets:
                tid = target["id"]
                if tid in self.bundle:
                    continue
                for w in windows_by_target.get(tid, []):
                    if w["sat_id"] != self.agent_id:
                        continue
                    theta = math.radians(w["theta_deg"])
                    s_ij = compute_score(target, theta)
                    winner_bid = self.winner_bids.get(tid, 0.0)
                    # Marginal gain over current best known bid
                    if s_ij > winner_bid and s_ij > best_score:
                        best_score = s_ij
                        best_tid = tid
                        best_window = w

            if best_tid < 0 or best_score <= 0:
                break

            self.bundle.append(best_tid)
            self.path.append(best_window)
            self.winner_bids[best_tid] = best_score   # raw score as bid
            self.winner_agents[best_tid] = self.agent_id
            changed = True

        return changed


# ═══════════════════════════════════════════════════════════════════════════
# Main CBBA Solver
# ═══════════════════════════════════════════════════════════════════════════

def cbba_solver(
    windows: List[Dict],
    targets: List[Dict],
    n_sats: int,
    max_rounds: int = 10,
    bundle_size: int = 20,
) -> Dict:
    """Consensus-Based Bundle Algorithm for constellation scheduling.

    Args:
        windows: List of dicts with target_id, sat_id, t_start, t_end, theta_deg
        targets: List of dicts with id, priority
        n_sats: Number of satellite agents
        max_rounds: Maximum consensus rounds (default 10)
        bundle_size: Max bundle size per satellite (default 20)

    Returns:
        Dict with: schedule, n_scheduled, f1_raw, f1, f2, n_rounds,
        converged, sat_allocations
    """
    # Build index: target_id -> list of windows
    windows_by_target: Dict[int, List[Dict]] = {}
    for w in windows:
        tid = w["target_id"]
        windows_by_target.setdefault(tid, []).append(w)

    # Build target index
    target_map: Dict[int, Dict] = {}
    for t in targets:
        target_map[t["id"]] = t

    # Create agents
    agents = [_CBBAAgent(i) for i in range(n_sats)]

    total_priority = sum(t.get("priority", 1.0) for t in targets)

    # ── Main CBBA loop (alternate build ↔ consensus) ──────────────────
    converged = False
    n_rounds = 0

    while n_rounds < max_rounds and not converged:
        n_rounds += 1
        round_changed = False

        # Phase 1: Bundle Building (all agents rebuild)
        for agent in agents:
            if agent.build_bundle(targets, windows_by_target, bundle_size):
                round_changed = True

        # Phase 2: Consensus
        for agent_i in agents:
            for agent_k in agents:
                if agent_i.agent_id == agent_k.agent_id:
                    continue
                for tid, bid_k in list(agent_k.winner_bids.items()):
                    agent_k_id = agent_k.winner_agents.get(tid, -1)
                    bid_i = agent_i.winner_bids.get(tid, 0.0)
                    agent_i_id = agent_i.winner_agents.get(tid, -1)

                    # Update if sender has higher bid, or same bid
                    # with lower agent ID (tie-breaking)
                    should_update = (
                        bid_k > bid_i
                        or (bid_k == bid_i and bid_k > 0
                            and agent_k_id < agent_i_id)
                    )

                    if should_update:
                        agent_i.winner_bids[tid] = bid_k
                        agent_i.winner_agents[tid] = agent_k_id
                        round_changed = True
                        # If I had this task, release it
                        if (tid in agent_i.bundle
                                and agent_k_id != agent_i.agent_id):
                            idx = agent_i.bundle.index(tid)
                            agent_i.bundle.pop(idx)
                            agent_i.path.pop(idx)

        if not round_changed:
            converged = True

    # ── Build final schedule ──────────────────────────────────────────
    schedule = []
    for agent in agents:
        for idx, tid in enumerate(agent.bundle):
            win = agent.path[idx]
            target = target_map.get(tid, {})
            schedule.append({
                "target_id": tid,
                "sat_id": agent.agent_id,
                "theta_deg": win["theta_deg"],
                "priority": target.get("priority", 1.0),
            })

    n_scheduled = len(schedule)
    f1_raw = sum(s["priority"] for s in schedule)
    f1 = f1_raw / total_priority if total_priority > 0 else 0.0

    # f2: mean quality
    total_q = 0.0
    for s in schedule:
        theta = math.radians(s["theta_deg"])
        total_q += _quality(theta)
    f2 = total_q / n_scheduled if n_scheduled > 0 else 0.0

    # Per-sat allocations
    sat_allocations: Dict[str, int] = {}
    for s in schedule:
        sid = str(s["sat_id"])
        sat_allocations[sid] = sat_allocations.get(sid, 0) + 1

    return {
        "algorithm": "CBBA",
        "status": "ok",
        "f1": round(f1, 4),
        "f1_raw": round(f1_raw, 4),
        "f2": round(f2, 4),
        "n_scheduled": n_scheduled,
        "n_rounds": n_rounds,
        "converged": converged,
        "schedule": schedule,
        "sat_allocations": sat_allocations,
        "runtime_s": 0.0,
    }
