"""Outlook scaffold for a sector-pair cost profile.

This object is not a Paper XIII report metric. Channel strengths and their
normalization must be supplied explicitly by a future comparison specification.
"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np


def shortest_path_closure(costs: np.ndarray) -> np.ndarray:
    costs = np.asarray(costs, dtype=float)
    if costs.ndim != 2 or costs.shape[0] != costs.shape[1]:
        raise ValueError("cost matrix must be square")
    if np.any(costs < 0):
        raise ValueError("edge costs must be non-negative")

    distance = costs.copy()
    np.fill_diagonal(distance, 0.0)
    for k in range(distance.shape[0]):
        distance = np.minimum(distance, distance[:, [k]] + distance[[k], :])
    return distance


def cost_from_normalized_strength(
    strength: np.ndarray, support_threshold: float = 0.0
) -> np.ndarray:
    strength = np.asarray(strength, dtype=float)
    if strength.ndim != 2 or strength.shape[0] != strength.shape[1]:
        raise ValueError("strength matrix must be square")
    if not 0 <= support_threshold < 1:
        raise ValueError("support_threshold must lie in [0, 1)")
    if np.any(strength < 0) or np.any(strength > 1):
        raise ValueError("normalized strengths must lie in [0, 1]")

    costs = np.full(strength.shape, np.inf, dtype=float)
    active = strength > support_threshold
    positive = active & (strength > 0)
    costs[positive] = -np.log(strength[positive])
    np.fill_diagonal(costs, 0.0)
    return costs


def sector_pair_cost_profile(
    normalized_channel_strengths: Mapping[str, np.ndarray],
    support_threshold: float = 0.0,
) -> dict[str, np.ndarray]:
    """Close each declared channel independently under directed path cost."""

    if not normalized_channel_strengths:
        raise ValueError("at least one declared channel is required")
    shapes = {np.asarray(value).shape for value in normalized_channel_strengths.values()}
    if len(shapes) != 1:
        raise ValueError("all channel strengths must share one sector shape")
    return {
        name: shortest_path_closure(
            cost_from_normalized_strength(strength, support_threshold)
        )
        for name, strength in normalized_channel_strengths.items()
    }


def run_checks() -> dict[str, bool]:
    support = np.array(
        [
            [0.0, 0.8, 0.0, 0.0],
            [0.0, 0.0, 0.5, 0.0],
            [0.0, 0.0, 0.0, 0.25],
            [0.0, 0.0, 0.0, 0.0],
        ]
    )
    profile = sector_pair_cost_profile({"declared_support": support})
    distance = profile["declared_support"]

    triangle = all(
        distance[i, j] <= distance[i, k] + distance[k, j] + 1e-12
        for i in range(4)
        for j in range(4)
        for k in range(4)
    )
    unreachable = np.isinf(distance[3, 0])
    directed = distance[0, 1] != distance[1, 0]
    return {
        "closure_triangle_by_construction": bool(triangle),
        "unreachable_is_infinite": bool(unreachable),
        "directed_cost_retained": bool(directed),
    }


def main() -> None:
    checks = run_checks()
    print("Paper XIII Outlook: sector-pair cost-profile scaffold")
    for name, passed in checks.items():
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")
    print("Boundary: no canonical channel-strength extraction or report metric is claimed.")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
