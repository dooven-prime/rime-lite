"""Paper XII diagnostic: dynamic-maze wall-crossing SOF Report.

Claim status:
    - Visual finite-state wall-crossing demonstration for Paper XII.
    - Connected components are time-dependent sectors; door state is the
      deformation parameter.
    - Door reopening is connectivity repair, not fixed-sector Lie-depth
      D-repair.

For a 5 x 5 grid, closing all doors produces 24 genuine split events as the
component count changes from 1 to 25. Reopening in reverse produces 24 merge
events and removes all cross-component frozen cell pairs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


GRID_SIZE = 5
N_CELLS = GRID_SIZE**2


def cell_id(row: int, col: int) -> int:
    return row * GRID_SIZE + col


DOORS = [
    (cell_id(row, col), cell_id(row, col + 1))
    for row in range(GRID_SIZE)
    for col in range(GRID_SIZE - 1)
] + [
    (cell_id(row, col), cell_id(row + 1, col))
    for row in range(GRID_SIZE - 1)
    for col in range(GRID_SIZE)
]


def connected_components(door_state: np.ndarray) -> list[list[int]]:
    adjacency = [[] for _ in range(N_CELLS)]
    for is_open, (left, right) in zip(door_state, DOORS):
        if is_open:
            adjacency[left].append(right)
            adjacency[right].append(left)

    visited = np.zeros(N_CELLS, dtype=bool)
    components = []
    for start in range(N_CELLS):
        if visited[start]:
            continue
        stack = [start]
        visited[start] = True
        component = []
        while stack:
            cell = stack.pop()
            component.append(cell)
            for neighbor in adjacency[cell]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    stack.append(neighbor)
        components.append(sorted(component))
    return components


def frozen_cell_pairs(components: list[list[int]]) -> int:
    within = sum(len(component) ** 2 for component in components)
    return N_CELLS**2 - within


def simulate(seed: int = 42) -> dict:
    rng = np.random.RandomState(seed)
    order = rng.permutation(len(DOORS))
    door_state = np.ones(len(DOORS), dtype=bool)

    close_events = []
    previous = connected_components(door_state)
    for step, door_index in enumerate(order, start=1):
        door_state[door_index] = False
        current = connected_components(door_state)
        if len(current) > len(previous):
            close_events.append(
                {
                    "step": step,
                    "door": int(door_index),
                    "before": len(previous),
                    "after": len(current),
                    "frozen_pairs": frozen_cell_pairs(current),
                }
            )
        previous = current

    open_events = []
    previous = connected_components(door_state)
    for step, door_index in enumerate(reversed(order), start=1):
        door_state[door_index] = True
        current = connected_components(door_state)
        if len(current) < len(previous):
            open_events.append(
                {
                    "step": step,
                    "door": int(door_index),
                    "before": len(previous),
                    "after": len(current),
                    "frozen_pairs": frozen_cell_pairs(current),
                }
            )
        previous = current

    return {
        "close_events": close_events,
        "open_events": open_events,
        "final_components": previous,
    }


def print_event(event: dict, label: str) -> None:
    print(
        f"    step={event['step']:>2d}, door={event['door']:>2d}: "
        f"{label} {event['before']} -> {event['after']}, "
        f"frozen_cell_pairs={event['frozen_pairs']}"
    )


def sofreport(result: dict) -> dict:
    return {
        "sofrs_version": "1.0",
        "report_id": "maze_wall_crossing",
        "system": "5 x 5 dynamic maze",
        "claim_status": "diagnostic",
        "claim_note": "finite connectivity wall-crossing demonstration",
        "sectorization": {
            "origin": "connected components of the open-door graph",
            "space": "25 maze cells",
            "time_dependent": True,
            "strict_sof_realization": True,
        },
        "observable_family": {
            "connectivity": "open-door adjacency and connected components",
            "frozen_pairs": "ordered cell pairs in different components",
        },
        "support_matrix": {
            "kind": "connectivity summary",
            "fully_open": {"components": 1, "frozen_ordered_pairs": 0},
            "fully_closed": {"components": 25, "frozen_ordered_pairs": 600},
        },
        "bridge_matrix": None,
        "repair_matrix": {
            "kind": "door-reopening connectivity repair",
            "events": result["open_events"],
            "repair_count": len(result["open_events"]),
            "claim_note": "connectivity repair, not fixed-sector Lie-depth D-repair",
        },
        "wall_record": {
            "wall_type": "connectivity split/merge",
            "wall_number": len(result["close_events"]),
            "split_events": result["close_events"],
            "merge_events": result["open_events"],
            "trajectory_summary": {
                "component_path": [1, 25, 1],
                "frozen_pair_path": [0, 600, 0],
            },
        },
        "failure_modes": [
            "sectorization changes with the door state",
            "bridge matrix is not defined for this component-level report",
            "connectivity repair is not Lie-depth D-repair",
        ],
    }


def write_sofreport(report: dict) -> Path:
    path = Path(__file__).resolve().parent / "results" / "maze.sofreport"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path


def print_report(result: dict) -> None:
    close_events = result["close_events"]
    open_events = result["open_events"]

    print("=" * 84)
    print("  Paper XII: Dynamic Maze Wall-Crossing SOF Report")
    print("=" * 84)
    print(f"  Grid: {GRID_SIZE} x {GRID_SIZE}, cells={N_CELLS}, doors={len(DOORS)}")
    print("  Sectorization: connected components under the current door state")
    print("  Deformation: close all doors, then reopen them in reverse order")
    print()
    print(f"  Split wall crossings: {len(close_events)}")
    for event in close_events[:4] + close_events[-4:]:
        print_event(event, "split")
    print()
    print(f"  Merge/repair wall crossings: {len(open_events)}")
    for event in open_events[:4] + open_events[-4:]:
        print_event(event, "merge")
    print()
    print("  Summary:")
    print("    components: 1 -> 25 -> 1")
    print("    frozen ordered cell pairs: 0 -> 600 -> 0")
    print("    closing a critical door creates a connectivity-splitting wall")
    print("    reopening that door supplies connectivity repair")
    print("    this is not fixed-sector Lie-depth D-repair")
    print(f"SOFRS v1.0: {write_sofreport(sofreport(result))}")
    print("Done.")


if __name__ == "__main__":
    print_report(simulate())
