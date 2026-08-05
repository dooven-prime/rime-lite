"""Paper XI observable-status trajectory controls.

The experiment records a pair event only when at least one declared typed
field changes between adjacent deformation samples. Each event retains every
changed field independently; direct, word, Lie, and truncated-depth data are
not collapsed into one mutually exclusive status.

Claim status: Computational Certificate for the finite sampled controls. The sampled events do not
determine ambient codimension or a continuous-time wall flow.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import (  # noqa: E402
    AccessibilityEngine,
    UNREACHED_DEPTH,
    compute_direct_support,
    compute_length_two_support,
    compute_word_depth_matrix,
)


UNREACHED_AT_CUTOFF = "UNREACHED_AT_CUTOFF"
DIRECT_SUPPORT_KEY = "operator.direct_support[Y]"
WORD_TWO_SUPPORT_KEY = "word.support[Y,d=2]"
LIE_TWO_SUPPORT_KEY = "lie.simple_commutator_support[X]"


def word_depth_key(cutoff: int) -> str:
    return f"word.depth_truncated[Y,cutoff={cutoff}]"


@dataclass(frozen=True)
class TypedFieldChange:
    field_key: str
    before_state: bool | int | str
    after_state: bool | int | str
    change_kind: str


@dataclass(frozen=True)
class PairWallEvent:
    pair: tuple[int, int]
    step: int
    param_before: Any
    param_after: Any
    changes: tuple[TypedFieldChange, ...]
    tags: tuple[str, ...]


@dataclass
class WallTrajectory:
    param_values: list[Any]
    state_matrices: list[np.ndarray]
    events: list[PairWallEvent]
    n_sectors: int
    total_pairs: int
    summary: dict[str, Any] = field(default_factory=dict)

    def events_at_step(self, step: int) -> list[PairWallEvent]:
        return [event for event in self.events if event.step == step]

    def events_for_pair(self, pair: tuple[int, int]) -> list[PairWallEvent]:
        return [event for event in self.events if event.pair == pair]


def pair_state_bundle(
    i: int,
    j: int,
    r1: np.ndarray,
    r2_word: np.ndarray,
    r2_lie: np.ndarray,
    depth_word: np.ndarray,
    *,
    cutoff: int,
    unreached_sentinel: int,
) -> dict[str, bool | int | str]:
    depth = int(depth_word[i, j])
    return {
        DIRECT_SUPPORT_KEY: bool(r1[i, j]),
        WORD_TWO_SUPPORT_KEY: bool(r2_word[i, j]),
        LIE_TWO_SUPPORT_KEY: bool(r2_lie[i, j]),
        word_depth_key(cutoff): (
            UNREACHED_AT_CUTOFF if depth == unreached_sentinel else depth
        ),
    }


def typed_state_matrix(
    audit: dict,
    *,
    cutoff: int,
    unreached_sentinel: int = UNREACHED_DEPTH,
) -> np.ndarray:
    """Build an object-valued matrix of independent typed field bundles."""
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
    for i in range(n_sectors):
        for j in range(n_sectors):
            result[i, j] = pair_state_bundle(
                i,
                j,
                r1,
                r2_word,
                r2_lie,
                depth_word,
                cutoff=cutoff,
                unreached_sentinel=unreached_sentinel,
            )
    return result


def classify_field_change(
    field_key: str,
    before: bool | int | str,
    after: bool | int | str,
) -> str:
    if isinstance(before, bool) and isinstance(after, bool):
        return "support_gain" if after else "support_loss"
    if field_key.startswith(("word.depth_", "route.depth_", "lie.depth_")):
        return "first_hit_change"
    return "value_change"


def event_tags(changes: list[TypedFieldChange]) -> tuple[str, ...]:
    tags: set[str] = set()
    for change in changes:
        if (
            change.change_kind == "first_hit_change"
            and change.before_state == UNREACHED_AT_CUTOFF
            and change.after_state != UNREACHED_AT_CUTOFF
        ):
            tags.add("REPAIR")
    return tuple(sorted(tags))


def build_wall_trajectory(
    audits: list[dict],
    param_values: list[Any] | None = None,
    *,
    cutoff: int = 6,
    unreached_sentinel: int = UNREACHED_DEPTH,
) -> WallTrajectory:
    """Record sparse typed field changes along a fixed-schema sampled path."""
    if not audits:
        return WallTrajectory(
            [],
            [],
            [],
            0,
            0,
            {"n_steps": 0, "n_pair_events": 0, "n_field_changes": 0},
        )
    if param_values is None:
        param_values = list(range(len(audits)))
    if len(param_values) != len(audits):
        raise ValueError("param_values must have one entry per audit snapshot")

    matrices = [
        typed_state_matrix(
            audit,
            cutoff=cutoff,
            unreached_sentinel=unreached_sentinel,
        )
        for audit in audits
    ]
    shape = matrices[0].shape
    if any(matrix.shape != shape for matrix in matrices[1:]):
        raise ValueError("all trajectory snapshots must use the same sector count")

    n_sectors = shape[0]
    total_pairs = n_sectors * (n_sectors - 1)
    events: list[PairWallEvent] = []
    pair_event_counts_by_step = []
    field_change_counts_by_step = []

    for step in range(1, len(matrices)):
        before_matrix = matrices[step - 1]
        after_matrix = matrices[step]
        pair_step_count = 0
        field_step_count = 0
        for i in range(n_sectors):
            for j in range(n_sectors):
                if i == j:
                    continue
                before = before_matrix[i, j]
                after = after_matrix[i, j]
                if before.keys() != after.keys():
                    raise ValueError(
                        "field-key changes are schema transitions, not wall events"
                    )
                changes = [
                    TypedFieldChange(
                        field_key=field_key,
                        before_state=before[field_key],
                        after_state=after[field_key],
                        change_kind=classify_field_change(
                            field_key,
                            before[field_key],
                            after[field_key],
                        ),
                    )
                    for field_key in before
                    if before[field_key] != after[field_key]
                ]
                if not changes:
                    continue
                events.append(
                    PairWallEvent(
                        pair=(i, j),
                        step=step,
                        param_before=param_values[step - 1],
                        param_after=param_values[step],
                        changes=tuple(changes),
                        tags=event_tags(changes),
                    )
                )
                pair_step_count += 1
                field_step_count += len(changes)
        pair_event_counts_by_step.append(pair_step_count)
        field_change_counts_by_step.append(field_step_count)

    all_changes = [change for event in events for change in event.changes]
    change_kinds = sorted({change.change_kind for change in all_changes})
    kind_counts = {
        kind: sum(change.change_kind == kind for change in all_changes)
        for kind in change_kinds
    }
    all_tags = sorted({tag for event in events for tag in event.tags})
    tag_counts = {
        tag: sum(tag in event.tags for event in events)
        for tag in all_tags
    }
    changed_pairs = {event.pair for event in events}
    summary = {
        "n_steps": len(matrices),
        "n_transitions": max(0, len(matrices) - 1),
        "n_sectors": n_sectors,
        "total_pairs": total_pairs,
        "n_pair_events": len(events),
        "n_field_changes": len(all_changes),
        "n_changed_pairs": len(changed_pairs),
        "n_stable_pairs": total_pairs - len(changed_pairs),
        "pair_event_counts_by_step": pair_event_counts_by_step,
        "field_change_counts_by_step": field_change_counts_by_step,
        "pair_event_density_by_step": [
            count / total_pairs for count in pair_event_counts_by_step
        ],
        "field_change_kind_counts": kind_counts,
        "event_tag_counts": tag_counts,
        "declared_field_keys": list(matrices[0][0, 0].keys()),
        "unreached_state": UNREACHED_AT_CUTOFF,
        "cutoff": cutoff,
    }
    return WallTrajectory(
        param_values=list(param_values),
        state_matrices=matrices,
        events=events,
        n_sectors=n_sectors,
        total_pairs=total_pairs,
        summary=summary,
    )


def field_state_counts(matrix: np.ndarray) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for bundle in matrix.flat:
        for field_key, value in bundle.items():
            bucket = counts.setdefault(field_key, {})
            if isinstance(value, bool):
                label = "true" if value else "false"
            elif value == UNREACHED_AT_CUTOFF:
                label = UNREACHED_AT_CUTOFF
            else:
                label = str(value)
            bucket[label] = bucket.get(label, 0) + 1
    return counts



TOL = 1e-8
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
            unreached=UNREACHED_DEPTH,
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
        "field_state_counts": [
            field_state_counts(matrix) for matrix in trajectory.state_matrices
        ],
        "events": [
            {
                "pair": list(event.pair),
                "step": event.step,
                "param_before": event.param_before,
                "param_after": event.param_after,
                "tags": list(event.tags),
                "changes": [
                    {
                        "field_key": change.field_key,
                        "before_state": change.before_state,
                        "after_state": change.after_state,
                        "change_kind": change.change_kind,
                    }
                    for change in event.changes
                ],
            }
            for event in trajectory.events
        ],
    }


def markdown_report(results: dict[str, dict]) -> str:
    lines = [
        "# Paper XI Sparse Typed-State Trajectory Controls",
        "",
        "A pair event is counted only when at least one declared typed field changes between adjacent samples.",
        "",
        "| Control | Steps | Ordered pairs | Pair events | Field changes | Changed pairs | Event steps |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for name, payload in results.items():
        if not isinstance(payload, dict) or "summary" not in payload:
            continue
        summary = payload["summary"]
        event_steps = [
            index + 1
            for index, count in enumerate(summary["pair_event_counts_by_step"])
            if count
        ]
        lines.append(
            f"| {name} | {summary['n_steps']} | {summary['total_pairs']} | "
            f"{summary['n_pair_events']} | {summary['n_field_changes']} | "
            f"{summary['n_changed_pairs']} | {event_steps} |"
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
    results = {
        "record_version": "paper11-wall-trajectory-v1.0",
        "claim_status": "Computational Certificate",
        "producer": "experiments/paper11/wall_trajectory.py",
        **{name: trajectory_payload(value) for name, value in trajectories.items()},
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / "wall_trajectory.json"
    md_path = RESULTS_DIR / "wall_trajectory.md"
    json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(markdown_report(results), encoding="utf-8")

    print("Paper XI sparse typed-state trajectory controls")
    for name, payload in results.items():
        if not isinstance(payload, dict) or "summary" not in payload:
            continue
        summary = payload["summary"]
        print(
            f"  {name}: pair_events={summary['n_pair_events']}, "
            f"field_changes={summary['n_field_changes']}, "
            f"changed_pairs={summary['n_changed_pairs']}, "
            f"by_step={summary['pair_event_counts_by_step']}"
        )
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return results


if __name__ == "__main__":
    run()

