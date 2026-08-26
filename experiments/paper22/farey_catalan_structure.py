#!/usr/bin/env python3
"""Compare rational defect states with an independent Farey construction.

This producer is deliberately a finite certificate.  It replays the manuscript
anchored-Farey, Catalan, and Fibonacci theorems through a declared deficit; it
is supporting evidence rather than an all-deficit proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from exact_rational_low_deficit import (
    INFINITY,
    LABELS,
    MATRICES,
    Cusp,
    State,
    canonical_json,
    content_digest,
    cusp_text,
    determinant,
    enumerate_states,
    file_digest,
    internal_max_determinant,
    normalize_cusp,
    state_key,
    transition,
)


ROOT = Path(__file__).resolve().parents[2]
PAPER_DIR = ROOT / "experiments" / "paper22"
DEFAULT_OUTPUT = PAPER_DIR / "results" / "farey_catalan_fibonacci_k10_v1.json"
THEOREM_DOCUMENT = ROOT / "papers" / "paper22" / "Paper XXII.md"
SHARED_RATIONAL_CORE = PAPER_DIR / "exact_rational_low_deficit.py"

ZERO: Cusp = (0, 1)
NEG_ONE: Cusp = (-1, 1)
IDENTITY = (1, 0, 0, 1)
LEFT_EMBED = (1, 0, 1, 1)  # x -> x/(x+1), [0,infinity] -> [0,1]
RIGHT_EMBED = (1, 1, 0, 1)  # x -> x+1, [0,infinity] -> [1,infinity]


def matrix_transform(cusp: Cusp, matrix: tuple[int, int, int, int]) -> Cusp:
    a, b, c, d = matrix
    numerator, denominator = cusp
    return normalize_cusp(
        a * numerator + b * denominator,
        c * numerator + d * denominator,
    )


def transform_path(
    path: tuple[Cusp, ...], matrix: tuple[int, int, int, int]
) -> tuple[Cusp, ...]:
    return tuple(matrix_transform(cusp, matrix) for cusp in path)


def transform_registry(
    cusps: Iterable[Cusp], matrix: tuple[int, int, int, int]
) -> set[Cusp]:
    return {matrix_transform(cusp, matrix) for cusp in cusps}


@lru_cache(maxsize=None)
def positive_farey_paths(edge_count: int) -> tuple[tuple[Cusp, ...], ...]:
    """Increasing unimodular paths from 0 to infinity with fixed edge count."""
    if edge_count < 1:
        raise ValueError("edge_count must be positive")
    if edge_count == 1:
        return ((ZERO, INFINITY),)
    paths: set[tuple[Cusp, ...]] = set()
    for left_edges in range(1, edge_count):
        right_edges = edge_count - left_edges
        for left in positive_farey_paths(left_edges):
            embedded_left = transform_path(left, LEFT_EMBED)
            for right in positive_farey_paths(right_edges):
                embedded_right = transform_path(right, RIGHT_EMBED)
                if embedded_left[-1] != embedded_right[0] or embedded_left[-1] != (1, 1):
                    raise AssertionError("Catalan split did not meet at cusp 1")
                paths.add(embedded_left[:-1] + embedded_right)
    return tuple(sorted(paths))


def positive_vertex_registry(edge_count: int) -> set[Cusp]:
    return {cusp for path in positive_farey_paths(edge_count) for cusp in path}


def defect_from_path(path: Iterable[Cusp]) -> State:
    return tuple(sorted(cusp for cusp in set(path) if cusp != INFINITY))


def anchored_farey_candidates(deficit: int) -> dict[str, set[State]]:
    if deficit < 0:
        raise ValueError("deficit must be nonnegative")
    if deficit == 0:
        return {
            "empty": {()},
            "zero_only": set(),
            "negative_one_only": set(),
            "both_anchors": set(),
        }

    positive_paths = positive_farey_paths(deficit)
    zero_only = {defect_from_path(path) for path in positive_paths}
    negative_one_only = {
        defect_from_path(transform_path(path, MATRICES["R_inv"]))
        for path in positive_paths
    }

    both_anchors: set[State] = set()
    for negative_edges in range(1, deficit):
        for middle_edges in range(1, deficit + 1 - negative_edges):
            positive_edges = deficit + 1 - negative_edges - middle_edges
            if positive_edges < 1:
                continue
            for negative_path in positive_farey_paths(negative_edges):
                negative_segment = transform_path(negative_path, MATRICES["R_inv"])
                for middle_path in positive_farey_paths(middle_edges):
                    middle_segment = transform_path(middle_path, MATRICES["R"])
                    for positive_segment in positive_farey_paths(positive_edges):
                        both_anchors.add(
                            defect_from_path(
                                (*negative_segment, *middle_segment, *positive_segment)
                            )
                        )
    return {
        "empty": set(),
        "zero_only": zero_only,
        "negative_one_only": negative_one_only,
        "both_anchors": both_anchors,
    }


def catalan(index: int) -> int:
    if index < 0:
        return 0
    return math.comb(2 * index, index) // (index + 1)


def fibonacci(index: int) -> int:
    left, right = 0, 1
    for _ in range(index):
        left, right = right, left + right
    return left


def state_registry_digest(states: Iterable[State]) -> str:
    serialized = [
        [list(cusp) for cusp in state] for state in sorted(set(states), key=state_key)
    ]
    return hashlib.sha256(canonical_json(serialized).encode()).hexdigest()


def cyclic_farey_boundary(state: State) -> bool:
    finite = sorted(state, key=lambda cusp: Fraction(cusp[0], cusp[1]))
    cycle = [INFINITY, *finite, INFINITY]
    return all(abs(determinant(left, right)) == 1 for left, right in zip(cycle, cycle[1:]))


def max_pair_determinant(cusps: Iterable[Cusp]) -> int:
    ordered = sorted(set(cusps))
    return max(
        (
            abs(determinant(left, right))
            for index, left in enumerate(ordered)
            for right in ordered[index + 1 :]
        ),
        default=0,
    )


def max_coordinate(states: Iterable[State]) -> int:
    return max(
        (
            max(abs(numerator), denominator)
            for state in states
            for numerator, denominator in state
        ),
        default=0,
    )


def same_level_component_sizes(states: set[State]) -> list[int]:
    adjacency = {state: set() for state in states}
    for state in states:
        for label in LABELS:
            target = transition(state, label)
            if target in states:
                adjacency[state].add(target)
                adjacency[target].add(state)
    unseen = set(states)
    sizes = []
    while unseen:
        seed = min(unseen, key=state_key)
        stack = [seed]
        unseen.remove(seed)
        size = 0
        while stack:
            current = stack.pop()
            size += 1
            for target in adjacency[current]:
                if target in unseen:
                    unseen.remove(target)
                    stack.append(target)
        sizes.append(size)
    return sorted(sizes)


def cross_registry_max(left: set[Cusp], right: set[Cusp]) -> int:
    return max(abs(determinant(x, y)) for x in left for y in right)


def typed_continuant_replay(max_depth: int) -> dict[str, Any]:
    records = []
    transforms = {
        "N": MATRICES["R_inv"],
        "M": MATRICES["R"],
        "P": IDENTITY,
        "L": LEFT_EMBED,
    }
    all_pass = True
    for r in range(2, max_depth + 1):
        for s in range(2, max_depth + 1):
            left_vertices = positive_vertex_registry(r)
            right_vertices = positive_vertex_registry(s)
            typed_left = {
                name: transform_registry(left_vertices, matrix)
                for name, matrix in transforms.items()
            }
            typed_right = {
                name: transform_registry(right_vertices, matrix)
                for name, matrix in transforms.items()
            }
            maxima = {
                f"{left}-{right}": cross_registry_max(
                    typed_left[left], typed_right[right]
                )
                for left in transforms
                for right in transforms
                if list(transforms).index(left) <= list(transforms).index(right)
            }
            checks = {
                "same_type_exact": all(
                    maxima[f"{name}-{name}"] == fibonacci(r + s - 2)
                    for name in transforms
                ),
                "distinct_base_exact": all(
                    maxima[key] == fibonacci(r + s)
                    for key in ("N-M", "N-P", "M-P")
                ),
                "P_L_exact": maxima["P-L"] == fibonacci(r + s - 1),
                "N_L_exact": maxima["N-L"] == fibonacci(r + s + 1),
                "M_L_upper": maxima["M-L"] <= fibonacci(r + s + 1),
            }
            all_pass = all_pass and all(checks.values())
            records.append({"r": r, "s": s, "maxima": maxima, "checks": checks})
    return {
        "max_depth": max_depth,
        "records": records,
        "all_checks_passed": all_pass,
    }


def build(max_deficit: int) -> dict[str, Any]:
    reachable = enumerate_states(max_deficit)
    layers = {
        level: {state for state in reachable if len(state) == level}
        for level in range(max_deficit + 1)
    }
    rows = []
    all_checks = True
    for level in range(max_deficit + 1):
        candidates_by_type = anchored_farey_candidates(level)
        candidates = set().union(*candidates_by_type.values())
        exact = layers[level]
        category_counts = Counter(
            "both_anchors"
            if ZERO in state and NEG_ONE in state
            else "zero_only"
            if ZERO in state
            else "negative_one_only"
            if NEG_ONE in state
            else "empty"
            for state in exact
        )
        prefix_states = {
            state for prefix_level in range(level + 1) for state in layers[prefix_level]
        }
        guard_frontier = {
            target
            for state in prefix_states
            for label in LABELS
            for target in (transition(state, label),)
            if len(target) == level + 1
        }
        prefix_registry = {
            cusp for state in prefix_states for cusp in (*state, INFINITY)
        }
        guard_registry = {
            cusp
            for state in (
                *sorted(prefix_states, key=state_key),
                *sorted(guard_frontier, key=state_key),
            )
            for cusp in (*state, INFINITY)
        }
        if level == 0:
            typed_global_registry = {INFINITY}
            typed_guard_registry = {INFINITY, ZERO, NEG_ONE}
            witness_checks = {
                "height_witness": True,
                "internal_witness": True,
                "global_witness": True,
                "guard_witness": True,
            }
        else:
            vertices = positive_vertex_registry(level)
            typed_global_registry = (
                transform_registry(vertices, MATRICES["R_inv"])
                | vertices
                | (
                    transform_registry(
                        positive_vertex_registry(level - 1), MATRICES["R"]
                    )
                    if level >= 2
                    else set()
                )
            )
            typed_guard_registry = (
                transform_registry(vertices, MATRICES["R_inv"])
                | transform_registry(vertices, MATRICES["R"])
                | vertices
                | transform_registry(vertices, LEFT_EMBED)
            )
            fkm1 = fibonacci(level - 1)
            fk = fibonacci(level)
            fkp1 = fibonacci(level + 1)
            negative = (-fkp1, fk)
            positive = (fkm1, fk)
            guard_positive = (fk, fkp1)
            internal_target = (fk, fkm1)
            witness_checks = {
                "height_witness": any(negative in state for state in exact),
                "internal_witness": any(
                    ZERO in state and internal_target in (*state, INFINITY)
                    for state in exact
                ),
                "global_witness": (
                    negative in prefix_registry
                    and positive in prefix_registry
                    and abs(determinant(negative, positive))
                    == fibonacci(2 * level)
                ),
                "guard_witness": (
                    negative in guard_registry
                    and guard_positive in guard_registry
                    and abs(determinant(negative, guard_positive))
                    == fibonacci(2 * level + 1)
                ),
            }
        exact_count = len(exact)
        expected_count = 1 if level == 0 else catalan(level) + catalan(level - 1)
        expected_categories = (
            {"empty": 1, "zero_only": 0, "negative_one_only": 0, "both_anchors": 0}
            if level == 0
            else {
                "empty": 0,
                "zero_only": catalan(level - 1),
                "negative_one_only": catalan(level - 1),
                "both_anchors": catalan(level) - catalan(level - 1),
            }
        )
        state_global_max = max_pair_determinant(prefix_registry)
        guard_global_max = max_pair_determinant(guard_registry)
        observed_extrema = {
            "exact_layer_max_primitive_coordinate": max_coordinate(exact),
            "max_configuration_internal_abs_determinant": max(
                map(internal_max_determinant, prefix_states), default=0
            ),
            "global_state_registry_max_abs_determinant": state_global_max,
            "transition_guard_registry_max_abs_determinant": guard_global_max,
        }
        expected_extrema = (
            {
                "exact_layer_max_primitive_coordinate": 0,
                "max_configuration_internal_abs_determinant": 0,
                "global_state_registry_max_abs_determinant": 0,
                "transition_guard_registry_max_abs_determinant": 1,
            }
            if level == 0
            else {
                "exact_layer_max_primitive_coordinate": fibonacci(level + 1),
                "max_configuration_internal_abs_determinant": fibonacci(level),
                "global_state_registry_max_abs_determinant": fibonacci(2 * level),
                "transition_guard_registry_max_abs_determinant": fibonacci(2 * level + 1),
            }
        )
        checks = {
            "reachable_equals_independent_farey_candidates": exact == candidates,
            "reachable_registry_digest_equals_candidate_registry_digest": (
                state_registry_digest(exact) == state_registry_digest(candidates)
            ),
            "every_reachable_state_has_declared_anchor": all(
                not state or ZERO in state or NEG_ONE in state for state in exact
            ),
            "every_reachable_hatted_state_is_cyclic_farey_boundary": all(
                cyclic_farey_boundary(state) for state in exact if state
            ),
            "catalan_total_count": exact_count == expected_count,
            "catalan_category_counts": all(
                category_counts.get(name, 0) == count
                for name, count in expected_categories.items()
            ),
            "fibonacci_extrema": observed_extrema == expected_extrema,
            "typed_global_registry_decomposition": (
                prefix_registry == typed_global_registry
            ),
            "typed_guard_registry_decomposition": (
                guard_registry == typed_guard_registry
            ),
            "fibonacci_equality_witnesses": all(witness_checks.values()),
        }
        all_checks = all_checks and all(checks.values())
        rows.append(
            {
                "deficit": level,
                "reachable_state_count": exact_count,
                "expected_adjacent_catalan_sum": expected_count,
                "category_counts": {
                    name: category_counts.get(name, 0)
                    for name in ("empty", "zero_only", "negative_one_only", "both_anchors")
                },
                "expected_category_counts": expected_categories,
                "reachable_registry_sha256": state_registry_digest(exact),
                "independent_candidate_registry_sha256": state_registry_digest(candidates),
                "same_level_component_sizes": same_level_component_sizes(exact),
                "observed_extrema": observed_extrema,
                "expected_fibonacci_extrema": expected_extrema,
                "typed_registry_counts": {
                    "global": len(typed_global_registry),
                    "guard": len(typed_guard_registry),
                },
                "fibonacci_witness_checks": witness_checks,
                "checks": checks,
            }
        )

    typed_continuant = typed_continuant_replay(min(max_deficit, 7))
    all_checks = all_checks and typed_continuant["all_checks_passed"]
    payload: dict[str, Any] = {
        "schema": "paper.route-profiles.farey-catalan-fibonacci-certificate.v1",
        "artifact_id": f"ROUTE-PROFILES-FAREY-CATALAN-FIBONACCI-K{max_deficit}-V1",
        "artifact_role": "FINITE_EXACT_CERTIFICATE_FOR_FAREY_CATALAN_AND_FIBONACCI_THEOREMS",
        "claim_status": "computational_certificate_supporting_manuscript_theorems",
        "max_deficit": max_deficit,
        "candidate_definition": {
            "zero_only": "positive cyclic Farey boundary containing the base edge {0,infinity}",
            "negative_one_only": "negative cyclic Farey boundary containing the base edge {infinity,-1}",
            "both_anchors": "three Farey paths attached to the sides of the base triangle {infinity,-1,0}",
            "positive_path_recursion": "split uniquely at cusp 1 and embed two smaller 0-to-infinity paths",
        },
        "oeis_cross_reference": {
            "id": "A167422",
            "uri": "https://oeis.org/A167422",
            "role": "sequence identification only; not evidence for the state bijection",
        },
        "rows": rows,
        "typed_continuant_envelope_replay": typed_continuant,
        "all_declared_finite_checks_passed": all_checks,
        "theorem_boundary": [
            "set equality is replayed only through max_deficit",
            "the all-k anchored Farey classification is a manuscript proof, not a consequence of this finite replay",
            "the all-k Catalan enumeration is a manuscript corollary, not a sequence-fit claim",
            "the all-k Fibonacci envelope is a manuscript theorem, not a consequence of this finite replay",
            "no sharper finite-field stabilization threshold is inferred from sampled primes",
        ],
        "source_closure": [
            {
                "uri": "experiments/paper22/farey_catalan_structure.py",
                "sha256": file_digest(Path(__file__)),
            },
            {
                "uri": "papers/paper22/Paper XXII.md",
                "sha256": file_digest(THEOREM_DOCUMENT),
            },
            {
                "uri": "experiments/paper22/exact_rational_low_deficit.py",
                "sha256": file_digest(SHARED_RATIONAL_CORE),
                "role": "shared canonical cusp encoding, determinant arithmetic, and transition closure only",
            },
        ],
        "independent_generation_boundary": {
            "transition_path": "exact_rational_low_deficit.py::enumerate_states",
            "anchored_boundary_path": "farey_catalan_structure.py::anchored_farey_candidates",
            "shared_primitives": "canonical primitive cusp encoding, integral Mobius action, and determinant arithmetic",
            "membership_logic_shared": False,
            "not_shared": "reachable-state membership and anchored-boundary membership logic",
        },
    }
    payload["content_sha256"] = content_digest(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-deficit", type=int, default=10)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.max_deficit)
    if not payload["all_declared_finite_checks_passed"]:
        raise SystemExit("finite Farey/Catalan/Fibonacci checks failed")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"PASS {payload['artifact_id']}: "
        + ",".join(str(row["reachable_state_count"]) for row in payload["rows"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
