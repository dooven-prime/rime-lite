"""Typed static Markov and graph registrations for Paper X.

The two registered strict SOFs use coordinate sectors and one declared
positive-word operator:

* a three-state column-stochastic lazy directed cycle with alphabet ``{P}``;
* the six-vertex path graph with alphabet ``{A}``.

Direct support, exact length-two word support, and first positive-word depth
are computed without introducing a Lie/Hall carrier. Because both matrices
are entrywise nonnegative, word support agrees with support-graph walks; a
finite shortest-path comparison therefore certifies the exact depth matrix,
including mathematical infinity for unreachable ordered pairs.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from rime.accessibility import (
    UNREACHED_DEPTH,
    compute_R1,
    compute_length_two_support,
    compute_word_depth_matrix,
)


TOL = 1.0e-12
SCHEMA_VERSION = "paper10.markov-graph-static.v2"
RESULT_PATH = Path(__file__).resolve().parent / "results" / "markov_graph_sof.json"


def coordinate_sector_bases(dimension: int) -> list[np.ndarray]:
    identity = np.eye(dimension, dtype=complex)
    return [identity[:, [index]] for index in range(dimension)]


def support_shortest_paths(matrix: np.ndarray) -> np.ndarray:
    """Return exact directed support-graph distances with -1 for infinity."""
    support = np.abs(matrix) > TOL
    dimension = matrix.shape[0]
    distances = np.full((dimension, dimension), -1, dtype=int)
    np.fill_diagonal(distances, 0)

    power = np.eye(dimension, dtype=bool)
    for depth in range(1, dimension):
        power = (support.astype(int) @ power.astype(int)) > 0
        newly_reached = power & (distances < 0)
        distances[newly_reached] = depth
    return distances


def serialize_exact_depth(distances: np.ndarray) -> list[list[int | str]]:
    return [
        [
            int(value) if value >= 0 else "infinity"
            for value in row
        ]
        for row in distances
    ]


def labelled_edges(support: np.ndarray, labels: list[str]) -> list[str]:
    return [
        f"{labels[source]}->{labels[target]}"
        for target in range(len(labels))
        for source in range(len(labels))
        if source != target and support[target, source]
    ]


def audit_realization(
    *,
    realization_id: str,
    species: str,
    labels: list[str],
    operator_label: str,
    operator: np.ndarray,
    operator_semantics: str,
) -> dict:
    dimension = len(labels)
    sectors = coordinate_sector_bases(dimension)
    family = [operator.astype(complex)]

    direct_tensor = compute_R1(sectors, family, tol=TOL)
    direct_support = np.any(direct_tensor, axis=0)
    word_two_support = compute_length_two_support(sectors, family, tol=TOL)
    cutoff_depth = compute_word_depth_matrix(
        sectors,
        family,
        max_depth=max(1, dimension - 1),
        tol=TOL,
        unreached=UNREACHED_DEPTH,
    )
    exact_depth = support_shortest_paths(operator)

    for target in range(dimension):
        for source in range(dimension):
            if target == source:
                continue
            expected = exact_depth[target, source]
            observed = cutoff_depth[target, source]
            if expected < 0:
                if observed != UNREACHED_DEPTH:
                    raise AssertionError("word audit reached a graph-unreachable pair")
            elif observed != expected:
                raise AssertionError(
                    f"word depth mismatch for {source}->{target}: "
                    f"computed={observed}, graph={expected}"
                )

    off_diagonal = ~np.eye(dimension, dtype=bool)
    possible = dimension * (dimension - 1)
    finite_depths = exact_depth[(exact_depth > 0)]
    return {
        "id": realization_id,
        "record_kind": "strict_sof",
        "species": species,
        "space": {"dimension": dimension, "scalar_field": "complex"},
        "sectorization": {
            "origin": "coordinate state sectors" if species == "Markov" else "vertex sectors",
            "labels": labels,
            "complete": True,
            "sector_dimensions": [1] * dimension,
        },
        "operative_alphabet": {
            "labels": [operator_label],
            "word_convention": "positive",
            "adjoint_closed": bool(np.allclose(operator, operator.conj().T)),
            "projectors_are_letters": False,
            "semantics": operator_semantics,
        },
        "matrix": operator.tolist(),
        "findings": {
            "direct_support_edges": labelled_edges(direct_support, labels),
            "direct_support_count": int(np.count_nonzero(direct_support & off_diagonal)),
            "direct_support_possible": possible,
            "word_two_support_edges": labelled_edges(word_two_support, labels),
            "word_two_support_count": int(
                np.count_nonzero(word_two_support & off_diagonal)
            ),
            "exact_word_depth": serialize_exact_depth(exact_depth),
            "reachable_off_diagonal_count": int(
                np.count_nonzero((exact_depth > 0) & off_diagonal)
            ),
            "unreachable_off_diagonal_count": int(
                np.count_nonzero((exact_depth < 0) & off_diagonal)
            ),
            "maximum_finite_word_depth": (
                int(np.max(finite_depths)) if finite_depths.size else 0
            ),
        },
        "saturation_certificate": {
            "status": "PASS",
            "method": "entrywise-nonnegative support graph and finite shortest paths",
            "entrywise_nonnegative": bool(np.all(operator >= 0)),
            "word_depth_matches_support_graph": True,
            "search_bound": dimension - 1,
        },
        "capabilities": {
            "sectorization": True,
            "operator_carrier": True,
            "word_carrier": True,
            "lie_hall_carrier": False,
            "deformation_chart": False,
        },
        "claim_status": "Computational Certificate",
        "boundaries": [
            "positive-word accessibility only",
            "no Lie/Hall family is declared",
            "graph paths agree with words here because the single operator is entrywise nonnegative",
            "the certificate is specific to the displayed finite matrices",
        ],
    }


def audit() -> dict:
    markov = np.array(
        [
            [0.5, 0.0, 0.5],
            [0.5, 0.5, 0.0],
            [0.0, 0.5, 0.5],
        ],
        dtype=float,
    )
    if not np.allclose(np.sum(markov, axis=0), 1.0):
        raise AssertionError("registered Markov operator must be column-stochastic")

    graph = np.zeros((6, 6), dtype=float)
    for left in range(5):
        graph[left, left + 1] = 1.0
        graph[left + 1, left] = 1.0

    return {
        "schema_version": SCHEMA_VERSION,
        "claim_scope": (
            "two finite strict-SOF registrations with operator and exact "
            "positive-word carriers"
        ),
        "realizations": {
            "markov": audit_realization(
                realization_id="markov-lazy-cycle-3",
                species="Markov",
                labels=["state0", "state1", "state2"],
                operator_label="P",
                operator=markov,
                operator_semantics=(
                    "column-stochastic transition operator; matrix entry "
                    "P_ij carries state j to state i"
                ),
            ),
            "graph": audit_realization(
                realization_id="graph-path-6",
                species="Graph",
                labels=[f"v{index}" for index in range(6)],
                operator_label="A",
                operator=graph,
                operator_semantics="undirected path-graph adjacency operator",
            ),
        },
    }


def main() -> None:
    result = audit()
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("Paper X typed Markov/graph static registrations")
    for key, record in result["realizations"].items():
        findings = record["findings"]
        print(
            f"  {key}: R_1[Y]={findings['direct_support_count']}/"
            f"{findings['direct_support_possible']}, "
            f"W_2[Y]={findings['word_two_support_count']}/"
            f"{findings['direct_support_possible']}, "
            f"max D_word={findings['maximum_finite_word_depth']}, "
            f"unreachable={findings['unreachable_off_diagonal_count']}"
        )
    print("  Lie/Hall carrier: not declared")
    print(f"  result: {RESULT_PATH}")


if __name__ == "__main__":
    main()
