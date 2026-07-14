"""Paper XI observable-status trajectory controls.

The experiment records wall events only when a sector pair changes observable
status between adjacent deformation samples. Static terminal or bridge pairs
are status data, not wall events by themselves.

Claim status: controlled computational evidence. The sampled events do not
determine ambient codimension or a continuous-time wall flow.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import (  # noqa: E402
    AccessibilityEngine,
    compute_direct_support,
    compute_length_two_support,
    compute_word_depth_matrix,
)

class AccessibilityStatus(str, Enum):
    DIRECT = "direct"
    WORD_BRIDGE = "word_bridge"
    LIE_BRIDGE = "lie_bridge"
    DEEPER = "deeper"
    TERMINAL = "terminal"


class WallEventKind(str, Enum):
    REPAIR = "repair"
    TERMINALIZATION = "terminalization"
    SUPPORT_GAIN = "support_gain"
    SUPPORT_LOSS = "support_loss"
    LAYER_CHANGE = "layer_change"


@dataclass(frozen=True)
class WallEvent:
    pair: tuple[int, int]
    step: int
    param_before: Any
    param_after: Any
    status_before: AccessibilityStatus
    status_after: AccessibilityStatus
    kind: WallEventKind


@dataclass
class WallTrajectory:
    param_values: list[Any]
    status_matrices: list[np.ndarray]
    events: list[WallEvent]
    n_sectors: int
    total_pairs: int
    summary: dict[str, Any] = field(default_factory=dict)

    def events_at_step(self, step: int) -> list[WallEvent]:
        return [event for event in self.events if event.step == step]

    def events_for_pair(self, pair: tuple[int, int]) -> list[WallEvent]:
        return [event for event in self.events if event.pair == pair]


def classify_accessibility_status(
    i: int,
    j: int,
    r1: np.ndarray,
    r2_word: np.ndarray,
    r2_lie: np.ndarray,
    depth_word: np.ndarray,
    *,
    frozen_sentinel: int = 999,
) -> AccessibilityStatus | None:
    """Classify one off-diagonal pair without calling the status a wall."""
    if i == j:
        return None
    if bool(r1[i, j]):
        return AccessibilityStatus.DIRECT
    if bool(r2_word[i, j]):
        return AccessibilityStatus.WORD_BRIDGE
    if bool(r2_lie[i, j]):
        return AccessibilityStatus.LIE_BRIDGE
    depth = int(depth_word[i, j])
    if 1 < depth < frozen_sentinel:
        return AccessibilityStatus.DEEPER
    return AccessibilityStatus.TERMINAL


def status_matrix(audit: dict, *, frozen_sentinel: int = 999) -> np.ndarray:
    """Build an object-valued status matrix from one audit snapshot."""
    r1 = np.asarray(audit["R1_word"], dtype=bool)
    r2_word = np.asarray(audit["R2_word"], dtype=bool)
    r2_lie = np.asarray(audit["R2_lie"], dtype=bool)
    depth_word = np.asarray(audit["D_word"], dtype=int)
    if not (r1.shape == r2_word.shape == r2_lie.shape == depth_word.shape):
        raise ValueError("R1, R2_word, R2_lie, and D_word must have the same shape")
    if r1.ndim != 2 or r1.shape[0] != r1.shape[1]:
        raise ValueError("accessibility matrices must be square")

    n_sectors = r1.shape[0]
    result = np.empty((n_sectors, n_sectors), dtype=object)
    result[:] = None
    for i in range(n_sectors):
        for j in range(n_sectors):
            result[i, j] = classify_accessibility_status(
                i,
                j,
                r1,
                r2_word,
                r2_lie,
                depth_word,
                frozen_sentinel=frozen_sentinel,
            )
    return result


def classify_event_kind(
    before: AccessibilityStatus,
    after: AccessibilityStatus,
) -> WallEventKind:
    if before == AccessibilityStatus.TERMINAL and after != AccessibilityStatus.TERMINAL:
        return WallEventKind.REPAIR
    if before != AccessibilityStatus.TERMINAL and after == AccessibilityStatus.TERMINAL:
        return WallEventKind.TERMINALIZATION
    if before != AccessibilityStatus.DIRECT and after == AccessibilityStatus.DIRECT:
        return WallEventKind.SUPPORT_GAIN
    if before == AccessibilityStatus.DIRECT and after != AccessibilityStatus.DIRECT:
        return WallEventKind.SUPPORT_LOSS
    return WallEventKind.LAYER_CHANGE


def build_wall_trajectory(
    audits: list[dict],
    param_values: list[Any] | None = None,
    *,
    frozen_sentinel: int = 999,
) -> WallTrajectory:
    """Record every adjacent-step observable-status change along a path."""
    if not audits:
        return WallTrajectory([], [], [], 0, 0, {"n_steps": 0, "n_events": 0})
    if param_values is None:
        param_values = list(range(len(audits)))
    if len(param_values) != len(audits):
        raise ValueError("param_values must have one entry per audit snapshot")

    matrices = [status_matrix(audit, frozen_sentinel=frozen_sentinel) for audit in audits]
    shape = matrices[0].shape
    if any(matrix.shape != shape for matrix in matrices[1:]):
        raise ValueError("all trajectory snapshots must use the same sector count")

    n_sectors = shape[0]
    total_pairs = n_sectors * (n_sectors - 1)
    events: list[WallEvent] = []
    event_counts_by_step = []

    for step in range(1, len(matrices)):
        before_matrix = matrices[step - 1]
        after_matrix = matrices[step]
        step_count = 0
        for i in range(n_sectors):
            for j in range(n_sectors):
                if i == j:
                    continue
                before = before_matrix[i, j]
                after = after_matrix[i, j]
                if before == after:
                    continue
                events.append(
                    WallEvent(
                        pair=(i, j),
                        step=step,
                        param_before=param_values[step - 1],
                        param_after=param_values[step],
                        status_before=before,
                        status_after=after,
                        kind=classify_event_kind(before, after),
                    )
                )
                step_count += 1
        event_counts_by_step.append(step_count)

    kind_counts = {
        kind.value: sum(event.kind == kind for event in events)
        for kind in WallEventKind
    }
    changed_pairs = {event.pair for event in events}
    summary = {
        "n_steps": len(matrices),
        "n_transitions": max(0, len(matrices) - 1),
        "n_sectors": n_sectors,
        "total_pairs": total_pairs,
        "n_events": len(events),
        "n_changed_pairs": len(changed_pairs),
        "n_stable_pairs": total_pairs - len(changed_pairs),
        "event_counts_by_step": event_counts_by_step,
        "event_density_by_step": [count / total_pairs for count in event_counts_by_step],
        "event_kind_counts": kind_counts,
    }
    return WallTrajectory(
        param_values=list(param_values),
        status_matrices=matrices,
        events=events,
        n_sectors=n_sectors,
        total_pairs=total_pairs,
        summary=summary,
    )


def status_counts(matrix: np.ndarray) -> dict[str, int]:
    counts = {status.value: 0 for status in AccessibilityStatus}
    for value in matrix.flat:
        if isinstance(value, AccessibilityStatus):
            counts[value.value] += 1
    return counts



TOL = 1e-8
FROZEN = 999
MAX_DEPTH = 6
RESULTS_DIR = Path(__file__).resolve().parent / "results"


def skew(matrix: np.ndarray) -> np.ndarray:
    return ((matrix - matrix.conj().T) / 2.0).astype(complex)


def sector_bases(n_sectors: int) -> list[np.ndarray]:
    eye = np.eye(n_sectors, dtype=complex)
    return [eye[:, [index]] for index in range(n_sectors)]


def full_audit(sectors: list[np.ndarray], observables: list[np.ndarray]) -> dict:
    engine = AccessibilityEngine(sectors, observables, tol=TOL, max_depth=MAX_DEPTH)
    _r1, r2_lie_by_pair, _pairs = engine.support()
    r2_lie = (
        np.any(r2_lie_by_pair, axis=0)
        if r2_lie_by_pair.shape[0]
        else np.zeros((len(sectors), len(sectors)), dtype=bool)
    )
    return {
        "R1_word": compute_direct_support(sectors, observables, tol=TOL),
        "R2_word": compute_length_two_support(sectors, observables, tol=TOL),
        "R2_lie": r2_lie,
        "D_word": compute_word_depth_matrix(
            sectors,
            observables,
            max_depth=MAX_DEPTH,
            tol=TOL,
            frozen=FROZEN,
        ),
    }


class GridWorld:
    def __init__(self, size: int = 5, obstacle: tuple[int, int] = (2, 2)):
        self.size = size
        self.obstacle = obstacle

    def index(self, row: int, col: int) -> int:
        return row * self.size + col

    def transition(self, action: str) -> np.ndarray:
        shifts = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
        dr, dc = shifts[action]
        n_cells = self.size**2
        matrix = np.zeros((n_cells, n_cells), dtype=float)
        for row in range(self.size):
            for col in range(self.size):
                source = self.index(row, col)
                if (row, col) == self.obstacle:
                    matrix[source, source] = 1.0
                    continue
                next_row, next_col = row + dr, col + dc
                valid = (
                    0 <= next_row < self.size
                    and 0 <= next_col < self.size
                    and (next_row, next_col) != self.obstacle
                )
                target = self.index(next_row, next_col) if valid else source
                matrix[target, source] = 1.0
        return matrix

    def observables(self) -> list[np.ndarray]:
        return [skew(self.transition(action)) for action in ["N", "S", "E", "W"]]


def gridworld_control() -> WallTrajectory:
    path = [(2, 2), (1, 1), (0, 0)]
    sectors = sector_bases(25)
    audits = [full_audit(sectors, GridWorld(obstacle=point).observables()) for point in path]
    return build_wall_trajectory(audits, [f"obstacle={point}" for point in path])


def sir_control(n_steps: int = 21) -> WallTrajectory:
    sectors = sector_bases(3)
    gamma = 0.1
    betas = np.linspace(0.0, 0.5, n_steps)
    audits = []
    for beta in betas:
        infection = np.eye(3, dtype=float)
        infection[1, 0] = beta
        infection[0, 0] = 1.0 - beta
        recovery = np.eye(3, dtype=float)
        recovery[2, 1] = gamma
        recovery[1, 1] = 1.0 - gamma
        audits.append(full_audit(sectors, [skew(infection), skew(recovery)]))
    return build_wall_trajectory(audits, [round(float(beta), 3) for beta in betas])


def graph_control(n_steps: int = 11) -> WallTrajectory:
    sectors = sector_bases(4)
    ts = np.linspace(0.0, 1.0, n_steps)
    audits = []
    for t in ts:
        matrix = np.eye(4, dtype=float)
        for source, target in [(0, 1), (1, 2)]:
            matrix[target, source] = 1.0
            matrix[source, source] = 0.0
        for source, target in [(2, 3), (3, 0)]:
            weight = 1.0 - t
            if weight > TOL:
                matrix[target, source] = weight
                matrix[source, source] = 1.0 - weight
        audits.append(full_audit(sectors, [skew(matrix)]))
    return build_wall_trajectory(audits, [round(float(t), 2) for t in ts])


def trajectory_payload(trajectory: WallTrajectory) -> dict:
    return {
        "parameters": trajectory.param_values,
        "summary": trajectory.summary,
        "status_counts": [status_counts(matrix) for matrix in trajectory.status_matrices],
        "events": [
            {
                "pair": list(event.pair),
                "step": event.step,
                "param_before": event.param_before,
                "param_after": event.param_after,
                "status_before": event.status_before.value,
                "status_after": event.status_after.value,
                "kind": event.kind.value,
            }
            for event in trajectory.events
        ],
    }


def markdown_report(results: dict[str, dict]) -> str:
    lines = [
        "# Paper XI Observable-Status Trajectory Controls",
        "",
        "A wall event is counted only when an observable status changes between adjacent samples.",
        "",
        "| Control | Steps | Ordered pairs | Events | Changed pairs | Event steps |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for name, payload in results.items():
        summary = payload["summary"]
        event_steps = [
            index + 1
            for index, count in enumerate(summary["event_counts_by_step"])
            if count
        ]
        lines.append(
            f"| {name} | {summary['n_steps']} | {summary['total_pairs']} | "
            f"{summary['n_events']} | {summary['n_changed_pairs']} | {event_steps} |"
        )
    lines.extend(
        [
            "",
            "The event steps are sampled-path locations. They do not establish ambient codimension.",
            "",
        ]
    )
    return "\n".join(lines)


def run() -> dict[str, dict]:
    trajectories = {
        "GridWorld obstacle path": gridworld_control(),
        "SIR beta sweep": sir_control(),
        "Graph edge-weight endpoint": graph_control(),
    }
    results = {name: trajectory_payload(value) for name, value in trajectories.items()}
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / "wall_trajectory.json"
    md_path = RESULTS_DIR / "wall_trajectory.md"
    json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(markdown_report(results), encoding="utf-8")

    print("Paper XI observable-status trajectory controls")
    for name, payload in results.items():
        summary = payload["summary"]
        print(
            f"  {name}: events={summary['n_events']}, "
            f"changed_pairs={summary['n_changed_pairs']}, "
            f"by_step={summary['event_counts_by_step']}"
        )
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return results


if __name__ == "__main__":
    run()

