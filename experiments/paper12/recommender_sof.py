"""Paper XII diagnostic: recommender coverage SOF Report.

Claim status:
    - Synthetic structural-coverage diagnostic for recommendation systems.
    - Detects cluster-level user--item regions unreachable by the current
      collaborative-filtering propagation graph.
    - A pre-deployment coverage signal, not a replacement for online A/B tests,
      causal evaluation, ranking metrics, or business-outcome measurement.

The default 4 x 4 benchmark has four disconnected user--item components. Of
the 16 user-cluster/item-cluster pairs, 12 are structural recommendation dead
zones. A targeted bridge interaction reduces the dead-zone count.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import (  # noqa: E402
    compute_direct_support,
    compute_length_two_support,
    compute_word_depth_matrix,
    offdiag_count,
)


N_USER_CLUSTERS = 4
N_ITEM_CLUSTERS = 4
USERS_PER_CLUSTER = 20
ITEMS_PER_CLUSTER = 15
FROZEN = 999


def cluster_labels(n_clusters: int, size: int) -> np.ndarray:
    return np.repeat(np.arange(n_clusters), size)


def build_interactions(seed: int = 42) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    user_labels = cluster_labels(N_USER_CLUSTERS, USERS_PER_CLUSTER)
    item_labels = cluster_labels(N_ITEM_CLUSTERS, ITEMS_PER_CLUSTER)
    interactions = np.zeros((len(user_labels), len(item_labels)), dtype=float)

    for cluster in range(N_USER_CLUSTERS):
        users = np.flatnonzero(user_labels == cluster)
        items = np.flatnonzero(item_labels == cluster)
        mask = rng.random((len(users), len(items))) < 0.35
        interactions[np.ix_(users, items)] = mask.astype(float)

    return interactions, user_labels, item_labels


def sector_bases(user_labels: np.ndarray, item_labels: np.ndarray) -> tuple[list[np.ndarray], list[str]]:
    n_users = len(user_labels)
    dim = n_users + len(item_labels)
    eye = np.eye(dim, dtype=complex)
    sectors: list[np.ndarray] = []
    labels: list[str] = []

    for cluster in range(N_USER_CLUSTERS):
        indices = np.flatnonzero(user_labels == cluster)
        sectors.append(eye[:, indices])
        labels.append(f"UserCluster{cluster}")
    for cluster in range(N_ITEM_CLUSTERS):
        indices = n_users + np.flatnonzero(item_labels == cluster)
        sectors.append(eye[:, indices])
        labels.append(f"ItemCluster{cluster}")
    return sectors, labels


def interaction_observable(interactions: np.ndarray) -> np.ndarray:
    n_users, n_items = interactions.shape
    observable = np.zeros((n_users + n_items, n_users + n_items), dtype=complex)
    observable[:n_users, n_users:] = interactions
    observable[n_users:, :n_users] = interactions.T
    return observable


def dead_zones(D: np.ndarray) -> list[tuple[int, int]]:
    zones = []
    for user_cluster in range(N_USER_CLUSTERS):
        for item_cluster in range(N_ITEM_CLUSTERS):
            item_sector = N_USER_CLUSTERS + item_cluster
            if D[user_cluster, item_sector] == FROZEN:
                zones.append((user_cluster, item_cluster))
    return zones


def audit(interactions: np.ndarray, user_labels: np.ndarray, item_labels: np.ndarray) -> dict:
    sectors, labels = sector_bases(user_labels, item_labels)
    observable = interaction_observable(interactions)
    support = compute_direct_support(sectors, [observable])
    bridge = compute_length_two_support(sectors, [observable])
    D = compute_word_depth_matrix(sectors, [observable], max_depth=8, frozen=FROZEN)
    return {
        "labels": labels,
        "support": support,
        "bridge": bridge,
        "D": D,
        "dead_zones": dead_zones(D),
        "support_edges": offdiag_count(support),
        "bridge_edges": offdiag_count(bridge),
    }


def add_cluster_bridge(
    interactions: np.ndarray,
    user_labels: np.ndarray,
    item_labels: np.ndarray,
    user_cluster: int,
    item_cluster: int,
) -> int:
    users = np.flatnonzero(user_labels == user_cluster)[:5]
    items = np.flatnonzero(item_labels == item_cluster)[:5]
    before = int(np.sum(interactions[np.ix_(users, items)]))
    interactions[np.ix_(users, items)] = 1.0
    after = int(np.sum(interactions[np.ix_(users, items)]))
    return after - before


def run() -> dict:
    interactions, user_labels, item_labels = build_interactions()
    initial = audit(interactions, user_labels, item_labels)

    repaired = interactions.copy()
    added = add_cluster_bridge(repaired, user_labels, item_labels, 0, 1)
    after = audit(repaired, user_labels, item_labels)
    return {"initial": initial, "after": after, "added_interactions": added}


def sofreport(result: dict) -> dict:
    initial = result["initial"]
    after = result["after"]
    initial_zones = set(initial["dead_zones"])
    after_zones = set(after["dead_zones"])
    repaired_zones = sorted(initial_zones - after_zones)
    return {
        "sofrs_version": "1.0",
        "report_id": "recommender_coverage",
        "system": "synthetic clustered collaborative-filtering graph",
        "claim_status": "diagnostic",
        "claim_note": "offline structural-coverage diagnostic",
        "sectorization": {
            "origin": "four user clusters and four item clusters",
            "space": "finite bipartite user-item space",
            "labels": initial["labels"],
            "strict_sof_realization": True,
        },
        "observable_family": {
            "interaction": "symmetric bipartite interaction propagation operator"
        },
        "support_matrix": {
            "kind": "direct cluster support",
            "initial": initial["support"].astype(int).tolist(),
            "after_intervention": after["support"].astype(int).tolist(),
            "initial_ordered_edges": initial["support_edges"],
            "after_ordered_edges": after["support_edges"],
        },
        "bridge_matrix": {
            "kind": "length-two cluster support",
            "initial": initial["bridge"].astype(int).tolist(),
            "after_intervention": after["bridge"].astype(int).tolist(),
            "initial_ordered_edges": initial["bridge_edges"],
            "after_ordered_edges": after["bridge_edges"],
        },
        "repair_matrix": {
            "kind": "targeted interaction coverage repair",
            "intervention": {
                "user_cluster": 0,
                "item_cluster": 1,
                "added_interactions": result["added_interactions"],
            },
            "initial_dead_zones": [list(zone) for zone in initial["dead_zones"]],
            "final_dead_zones": [list(zone) for zone in after["dead_zones"]],
            "repaired_dead_zones": [list(zone) for zone in repaired_zones],
            "dead_zone_count": [len(initial_zones), len(after_zones)],
            "initial_depth_matrix": initial["D"].astype(int).tolist(),
            "final_depth_matrix": after["D"].astype(int).tolist(),
        },
        "wall_record": {
            "status": "discrete_intervention_comparison",
            "trajectory_summary": {
                "dead_zone_path": [len(initial_zones), len(after_zones)],
                "support_edge_path": [initial["support_edges"], after["support_edges"]],
            },
            "claim_note": "single intervention comparison, not a continuous wall map",
        },
        "failure_modes": [
            "synthetic clustered interaction graph",
            "structural reachability does not measure ranking quality",
            "offline dead-zone detection does not replace A/B testing or causal evaluation",
        ],
    }


def write_sofreport(report: dict) -> Path:
    path = Path(__file__).resolve().parent / "results" / "recommender.sofreport"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path


def print_report(result: dict) -> None:
    initial = result["initial"]

    print("=" * 84)
    print("  Paper XII: Recommender Coverage SOF Report")
    print("=" * 84)
    print("  Sectorization: 4 user clusters + 4 item clusters")
    print("  Observable Family: bipartite interaction propagation")
    print(f"  Direct user-item coverage: 4/16 cluster pairs")
    print(f"  Support Matrix edges: {initial['support_edges']} ordered sector pairs")
    print(f"  Bridge Matrix edges:  {initial['bridge_edges']} ordered sector pairs")
    print()
    print(f"  Recommendation dead zones: {len(initial['dead_zones'])}/16")
    for user_cluster, item_cluster in initial["dead_zones"]:
        print(f"    UserCluster{user_cluster} -> ItemCluster{item_cluster}: unreachable")

    after = result["after"]

    print()
    print("  Targeted coverage repair:")
    print(
        f"    added interactions: {result['added_interactions']} "
        "between UserCluster0 and ItemCluster1"
    )
    print(f"    dead zones: {len(initial['dead_zones'])} -> {len(after['dead_zones'])}")
    print()
    print("  Claim Status:")
    print("    synthetic structural-coverage diagnostic")
    print("    detects unreachable cluster regions before online experimentation")
    print("    does not replace A/B tests for ranking quality or causal business impact")
    print(f"SOFRS v1.0: {write_sofreport(sofreport(result))}")
    print("Done.")


if __name__ == "__main__":
    print_report(run())
