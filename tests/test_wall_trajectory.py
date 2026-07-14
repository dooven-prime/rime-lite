"""Regression tests for Paper XI observable-status wall trajectories."""

import sys
import importlib.util
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MODULE_PATH = ROOT / "experiments" / "paper11" / "wall_trajectory.py"
SPEC = importlib.util.spec_from_file_location("paper11_wall_trajectory", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
wall_trajectory = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wall_trajectory
SPEC.loader.exec_module(wall_trajectory)

WallEventKind = wall_trajectory.WallEventKind
build_wall_trajectory = wall_trajectory.build_wall_trajectory


FROZEN = 999


def snapshot(status_01: str, status_02: str) -> dict:
    r1 = np.zeros((3, 3), dtype=bool)
    r2_word = np.zeros((3, 3), dtype=bool)
    r2_lie = np.zeros((3, 3), dtype=bool)
    depth = np.full((3, 3), FROZEN, dtype=int)
    np.fill_diagonal(depth, 0)

    for pair, status in [((0, 1), status_01), ((0, 2), status_02)]:
        i, j = pair
        if status == "direct":
            r1[i, j] = True
            depth[i, j] = 1
        elif status == "word_bridge":
            r2_word[i, j] = True
            depth[i, j] = 2
        elif status == "lie_bridge":
            r2_lie[i, j] = True
        elif status == "deeper":
            depth[i, j] = 3
        elif status != "terminal":
            raise ValueError(status)
    return {"R1_word": r1, "R2_word": r2_word, "R2_lie": r2_lie, "D_word": depth}


def test_repeated_pair_events_are_not_collapsed():
    audits = [
        snapshot("direct", "terminal"),
        snapshot("word_bridge", "word_bridge"),
        snapshot("direct", "terminal"),
    ]
    trajectory = build_wall_trajectory(audits, [0.0, 0.5, 1.0])

    assert trajectory.summary["n_events"] == 4
    assert trajectory.summary["n_changed_pairs"] == 2
    assert trajectory.summary["event_counts_by_step"] == [2, 2]
    assert len(trajectory.events_for_pair((0, 1))) == 2
    assert len(trajectory.events_for_pair((0, 2))) == 2
    assert trajectory.summary["event_kind_counts"][WallEventKind.REPAIR.value] == 1
    assert trajectory.summary["event_kind_counts"][WallEventKind.TERMINALIZATION.value] == 1
    assert trajectory.summary["event_kind_counts"][WallEventKind.SUPPORT_LOSS.value] == 1
    assert trajectory.summary["event_kind_counts"][WallEventKind.SUPPORT_GAIN.value] == 1


def test_unchanged_terminal_pair_is_not_a_wall_event():
    trajectory = build_wall_trajectory(
        [snapshot("direct", "terminal"), snapshot("direct", "terminal")]
    )
    assert trajectory.summary["n_events"] == 0
    assert trajectory.summary["n_stable_pairs"] == 6


if __name__ == "__main__":
    test_repeated_pair_events_are_not_collapsed()
    test_unchanged_terminal_pair_is_not_a_wall_event()
    print("test_wall_trajectory.py: OK")
