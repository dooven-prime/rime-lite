#!/usr/bin/env python3
"""Replay the two exact finite hostile controls owned by Paper XXIV."""

from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = ROOT / "experiments" / "paper24" / "results" / "descent_hostile_fixtures_v1.json"


def project_rows(rows: set[tuple[int, ...]], indices: tuple[int, ...]) -> set[tuple[int, ...]]:
    return {tuple(row[index] for index in indices) for row in rows}


def unseen_scope_fixture() -> dict[str, object]:
    coordinates = ("AB", "BC", "AC")
    patches = (("AB",), ("BC",), ("AC",))
    assignment = {coordinate: 1 for coordinate in coordinates}
    visible_constraints: list[str] = []
    parity = assignment["AB"] ^ assignment["BC"] ^ assignment["AC"]

    local_sections = [{coordinate: assignment[coordinate] for coordinate in patch} for patch in patches]
    glued = {coordinate: local[coordinate] for patch, local in zip(patches, local_sections) for coordinate in patch}

    assert glued == assignment
    assert parity == 1
    assert not visible_constraints

    return {
        "coordinates": list(coordinates),
        "patches": [list(patch) for patch in patches],
        "visible_constraints": visible_constraints,
        "global_constraint": "AB xor BC xor AC = 0",
        "global_assignment": assignment,
        "free_gluing_count": 1,
        "locally_admissible": True,
        "globally_admissible": False,
    }


def cyclic_context_fixture() -> dict[str, object]:
    edges = {
        "AB": ((0, 1), {(0, 0), (1, 1)}),
        "BC": ((1, 2), {(0, 0), (1, 1)}),
        "AC": ((0, 2), {(0, 1), (1, 0)}),
    }
    overlap_projections: dict[str, list[int]] = {}
    edge_names = tuple(edges)
    pairwise_consistent = True

    for left_index, left_name in enumerate(edge_names):
        left_positions, left_rows = edges[left_name]
        for right_name in edge_names[left_index + 1 :]:
            right_positions, right_rows = edges[right_name]
            overlap = tuple(sorted(set(left_positions) & set(right_positions)))
            left_indices = tuple(left_positions.index(position) for position in overlap)
            right_indices = tuple(right_positions.index(position) for position in overlap)
            left_projection = project_rows(left_rows, left_indices)
            right_projection = project_rows(right_rows, right_indices)
            pairwise_consistent &= left_projection == right_projection
            overlap_projections[f"{left_name}/{right_name}"] = sorted(value[0] for value in left_projection)

    natural_join = []
    for row in product((0, 1), repeat=3):
        if all(tuple(row[position] for position in positions) in rows for positions, rows in edges.values()):
            natural_join.append(list(row))

    assert pairwise_consistent
    assert not natural_join

    return {
        "attributes": ["A", "B", "C"],
        "contexts": list(edge_names),
        "relation_cardinalities": {name: len(rows) for name, (_, rows) in edges.items()},
        "overlap_projections": overlap_projections,
        "pairwise_consistent": pairwise_consistent,
        "natural_join": natural_join,
        "natural_join_count": len(natural_join),
        "globally_consistent": False,
    }


def expected_result() -> dict[str, object]:
    return {
        "schema": "paper.contextual-descent.hostile-fixtures.v1",
        "claim_boundary": {
            "unseen_scope": "section-valued semantic-entailment failure",
            "cyclic_context_core": "relation-valued global-consistency failure",
            "general_acyclicity_theorem": "IMPORTED_NOT_REPROVED_BY_THIS_FIXTURE",
        },
        "fixtures": {
            "UNSEEN_SCOPE": unseen_scope_fixture(),
            "CYCLIC_CONTEXT_CORE": cyclic_context_fixture(),
        },
        "status": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()

    expected = expected_result()
    if args.write_result:
        RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RESULT_PATH.write_text(
            json.dumps(expected, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    else:
        actual = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        if actual != expected:
            raise AssertionError("committed Paper XXIV hostile-fixture result is stale")

    print("PASS Paper XXIV hostile fixtures: 2 exact typed controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
