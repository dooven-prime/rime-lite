"""Paper V support script: non-complement R1 obstructions exist.

Status: finite support-level enumeration.

This script compresses the old exploratory non-complement search into a small
manuscript-supporting enumeration. It checks distance-1 R1 obstruction patterns
defined by triples (A_g, B_g):

    diagonal empty: A_g cap B_g = empty
    cross nonempty: A_g cap B_h != empty for g != h

The point is deliberately narrow. Complement patterns are important, but they
are not the only R1 obstruction type once the intermediate set or degree budget
changes. This motivates Paper V's caution that complement explosion is a model
mechanism, not a complete obstruction classification.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

from itertools import combinations, product

import numpy as np


np.random.seed(42)


def _subsets(universe: frozenset[int], max_size: int) -> list[frozenset[int]]:
    result: list[frozenset[int]] = []
    for size in range(1, min(max_size, len(universe)) + 1):
        for combo in combinations(sorted(universe), size):
            result.append(frozenset(combo))
    return result


def _is_obstruction(A: tuple[frozenset[int], ...], B: tuple[frozenset[int], ...]) -> bool:
    for A_g, B_g in zip(A, B):
        if A_g & B_g:
            return False
    for g in range(3):
        for h in range(3):
            if g != h and not (A[g] & B[h]):
                return False
    return True


def _classify(
    A: tuple[frozenset[int], ...],
    B: tuple[frozenset[int], ...],
    universe: frozenset[int],
) -> str:
    singleton_anchors = []
    is_complement = True
    for A_g, B_g in zip(A, B):
        if len(A_g) != 1:
            is_complement = False
            break
        anchor = next(iter(A_g))
        if B_g != universe - {anchor}:
            is_complement = False
            break
        singleton_anchors.append(anchor)

    if is_complement and len(set(singleton_anchors)) == 3:
        return "complement"

    if all(len(A_g) == 1 for A_g in A):
        anchors = {next(iter(A_g)) for A_g in A}
        if len(anchors) == 3:
            if all(len(B_g) < len(universe) - 1 for B_g in B):
                return "tight_budget"
            return "near_complement"

    return "other"


def _enumerate_case(n_vprime: int, d0: int, d1: int) -> dict:
    universe = frozenset(range(2, 2 + n_vprime))
    A_sets = _subsets(universe, d0)
    B_sets = _subsets(universe, d1)
    pairs = [(A, B) for A in A_sets for B in B_sets if not (A & B)]

    counts: dict[str, int] = {}
    examples: dict[str, tuple[tuple[frozenset[int], ...], tuple[frozenset[int], ...]]] = {}

    for triplet in product(pairs, repeat=3):
        A = tuple(pair[0] for pair in triplet)
        B = tuple(pair[1] for pair in triplet)
        if not _is_obstruction(A, B):
            continue
        label = _classify(A, B, universe)
        counts[label] = counts.get(label, 0) + 1
        examples.setdefault(label, (A, B))

    return {
        "universe": universe,
        "valid_pairs": len(pairs),
        "survivors": sum(counts.values()),
        "counts": counts,
        "examples": examples,
    }


def main() -> None:
    cases = [
        (3, 1, 2),
        (4, 1, 2),
        (4, 1, 3),
        (4, 2, 2),
        (4, 2, 3),
    ]

    print("=" * 72)
    print("Paper V: Non-Complement R1 Obstruction Enumeration")
    print("=" * 72)
    print("Conditions: diagonal empty and all cross intersections nonempty.")
    print()

    results = {}
    for n_vprime, d0, d1 in cases:
        result = _enumerate_case(n_vprime, d0, d1)
        results[(n_vprime, d0, d1)] = result
        print(
            f"|V'|={n_vprime}, d0={d0}, d1={d1}: "
            f"valid (A,B) pairs={result['valid_pairs']}, "
            f"obstruction triples={result['survivors']}, "
            f"classes={result['counts']}"
        )
        for label in sorted(result["examples"]):
            A, B = result["examples"][label]
            print(f"  example {label}: A={A}, B={B}")
        print()

    assert results[(3, 1, 2)]["counts"] == {"complement": 6}
    assert results[(4, 1, 2)]["counts"] == {"tight_budget": 24}
    assert results[(4, 1, 3)]["counts"] == {
        "tight_budget": 24,
        "near_complement": 144,
        "complement": 24,
    }
    assert results[(4, 2, 2)]["counts"] == {"other": 936, "tight_budget": 24}
    assert results[(4, 2, 3)]["counts"] == {
        "other": 1188,
        "tight_budget": 24,
        "near_complement": 144,
        "complement": 24,
    }
    print("[snapshot OK: complement is not the unique R1 obstruction family]")


if __name__ == "__main__":
    main()
