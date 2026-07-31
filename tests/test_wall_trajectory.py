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

build_wall_trajectory = wall_trajectory.build_wall_trajectory


UNREACHED = wall_trajectory.UNREACHED_DEPTH


def snapshot(pair_01: dict, pair_02: dict) -> dict:
    r1 = np.zeros((3, 3), dtype=bool)
    r2_word = np.zeros((3, 3), dtype=bool)
    r2_lie = np.zeros((3, 3), dtype=bool)
    depth = np.full((3, 3), UNREACHED, dtype=int)
    np.fill_diagonal(depth, 0)

    for pair, state in [((0, 1), pair_01), ((0, 2), pair_02)]:
        i, j = pair
        r1[i, j] = state.get("direct", False)
        r2_word[i, j] = state.get("word_two", False)
        r2_lie[i, j] = state.get("lie_two", False)
        depth[i, j] = state.get("word_depth", UNREACHED)
    return {"R1_word": r1, "R2_word": r2_word, "R2_lie": r2_lie, "D_word": depth}


def test_repeated_pair_events_are_not_collapsed():
    audits = [
        snapshot({"direct": True, "word_depth": 1}, {}),
        snapshot(
            {"word_two": True, "lie_two": True, "word_depth": 2},
            {"word_two": True, "word_depth": 2},
        ),
        snapshot({"direct": True, "word_depth": 1}, {}),
    ]
    trajectory = build_wall_trajectory(audits, [0.0, 0.5, 1.0])

    assert trajectory.summary["n_pair_events"] == 4
    assert trajectory.summary["n_field_changes"] == 12
    assert trajectory.summary["n_changed_pairs"] == 2
    assert trajectory.summary["pair_event_counts_by_step"] == [2, 2]
    assert trajectory.summary["field_change_counts_by_step"] == [6, 6]
    assert len(trajectory.events_for_pair((0, 1))) == 2
    assert len(trajectory.events_for_pair((0, 2))) == 2
    assert trajectory.summary["field_change_kind_counts"]["support_gain"] == 4
    assert trajectory.summary["field_change_kind_counts"]["support_loss"] == 4
    assert trajectory.summary["field_change_kind_counts"]["first_hit_change"] == 4
    assert trajectory.summary["event_tag_counts"]["REPAIR"] == 1

    first_pair_event = trajectory.events_for_pair((0, 1))[0]
    changed_keys = {change.field_key for change in first_pair_event.changes}
    assert changed_keys == {
        "operator.direct_support[Y]",
        "word.support[Y,d=2]",
        "lie.simple_commutator_support[X]",
        "word.depth_truncated[Y,cutoff=6]",
    }


def test_unchanged_unreached_pair_is_not_a_wall_event():
    trajectory = build_wall_trajectory(
        [
            snapshot({"direct": True, "word_two": True, "word_depth": 1}, {}),
            snapshot({"direct": True, "word_two": True, "word_depth": 1}, {}),
        ]
    )
    assert trajectory.summary["n_pair_events"] == 0
    assert trajectory.summary["n_field_changes"] == 0
    assert trajectory.summary["n_stable_pairs"] == 6


if __name__ == "__main__":
    test_repeated_pair_events_are_not_collapsed()
    test_unchanged_unreached_pair_is_not_a_wall_event()
    print("test_wall_trajectory.py: OK")
