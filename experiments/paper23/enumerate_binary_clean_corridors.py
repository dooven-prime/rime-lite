#!/usr/bin/env python3
"""Exhaust binary clean involution/defect-one corridor automata."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter, deque
from pathlib import Path

from registry import payload_digest


def involutions(state_count: int):
    for permutation in itertools.permutations(range(state_count)):
        if all(permutation[permutation[state]] == state for state in range(state_count)):
            yield permutation


def defect_one_maps(state_count: int):
    for transformation in itertools.product(
        range(state_count), repeat=state_count
    ):
        if len(set(transformation)) == state_count - 1:
            yield transformation


def _image_mask(
    mask: int,
    transformation: tuple[int, ...],
) -> int:
    image = 0
    while mask:
        bit = mask & -mask
        state = bit.bit_length() - 1
        image |= 1 << transformation[state]
        mask -= bit
    return image


def clean_reset_profile(
    permutation: tuple[int, ...],
    defect_one: tuple[int, ...],
) -> dict | None:
    """Return reset data exactly when the binary pair is clean and syncing."""
    n = len(permutation)
    full = (1 << n) - 1
    distance = {full: 0}
    parent: dict[int, tuple[int, int]] = {}
    queue = deque([full])
    while queue:
        current = queue.popleft()
        current_rank = current.bit_count()
        for letter, transformation in enumerate((permutation, defect_one)):
            target = _image_mask(current, transformation)
            if (
                letter == 1
                and current_rank > 1
                and target.bit_count() == current_rank
                and target != current
            ):
                return None
            if target not in distance:
                distance[target] = distance[current] + 1
                parent[target] = (current, letter)
                queue.append(target)
    singletons = [mask for mask in distance if mask.bit_count() == 1]
    if not singletons:
        return None
    target = min(singletons, key=lambda mask: (distance[mask], mask))
    word = []
    cursor = target
    while cursor != full:
        cursor, letter = parent[cursor]
        word.append(letter)
    word.reverse()
    return {
        "reset_depth": distance[target],
        "shortest_reset_word": word,
        "reachable_subset_count": len(distance),
    }


def explicit_depth_n_witness(state_count: int) -> dict:
    """Return the clean family with exact reset depth ``n`` for ``n>=3``."""
    if state_count < 3:
        raise ValueError("the depth-n witness starts at n=3")
    n = state_count
    permutation = list(range(n))
    permutation[n - 2], permutation[n - 1] = n - 1, n - 2
    defect_one = list(range(n))
    defect_one[0] = 0
    for state in range(1, n - 2):
        defect_one[state] = state + 1
    defect_one[n - 2] = 0
    defect_one[n - 1] = n - 1
    profile = clean_reset_profile(tuple(permutation), tuple(defect_one))
    if profile is None or profile["reset_depth"] != n:
        raise AssertionError(f"depth-n witness failed at n={n}")
    return {
        "state_count": n,
        "permutation": permutation,
        "defect_one": defect_one,
        **profile,
    }


def enumerate_size(state_count: int) -> dict:
    permutation_rows = list(involutions(state_count))
    defect_rows = list(defect_one_maps(state_count))
    histogram: Counter[int] = Counter()
    wait_histogram: Counter[int] = Counter()
    selected_witness = None
    clean_count = 0
    for permutation in permutation_rows:
        for defect_one in defect_rows:
            profile = clean_reset_profile(permutation, defect_one)
            if profile is None:
                continue
            clean_count += 1
            depth = profile["reset_depth"]
            histogram[depth] += 1
            wait_histogram[depth - (state_count - 1)] += 1
            if (
                selected_witness is None
                or depth > selected_witness["reset_depth"]
            ):
                selected_witness = {
                    "permutation": list(permutation),
                    "defect_one": list(defect_one),
                    **profile,
                }
    maximum = max(histogram, default=None)
    linear_candidate = state_count
    old_bound = 2 * state_count - 3
    explicit = (
        None if state_count < 3
        else explicit_depth_n_witness(state_count)
    )
    theorem_extremal_depth = 1 if state_count == 2 else state_count
    return {
        "state_count": state_count,
        "involution_count": len(permutation_rows),
        "defect_one_map_count": len(defect_rows),
        "examined_pair_count": len(permutation_rows) * len(defect_rows),
        "clean_synchronizing_pair_count": clean_count,
        "reset_depth_histogram": {
            str(depth): count for depth, count in sorted(histogram.items())
        },
        "genuine_wait_number_histogram": {
            str(wait_number): count
            for wait_number, count in sorted(wait_histogram.items())
        },
        "one_wait_theorem_failure_count": sum(
            count
            for wait_number, count in wait_histogram.items()
            if wait_number not in {0, 1}
        ),
        "maximum_reset_depth": maximum,
        "theorem_extremal_reset_depth": theorem_extremal_depth,
        "theorem_extremal_depth_verified": maximum == theorem_extremal_depth,
        "old_2n_minus_3_bound": old_bound,
        "old_bound_attained": maximum == old_bound,
        "candidate_n_bound": linear_candidate,
        "candidate_n_bound_holds_in_enumeration": (
            maximum is not None and maximum <= linear_candidate
        ),
        "candidate_n_bound_attained": maximum == linear_candidate,
        "selected_maximum_witness": selected_witness,
        "explicit_depth_n_witness": explicit,
    }


def build_certificate(max_states: int) -> dict:
    if max_states < 2:
        raise ValueError("max_states must be at least two")
    payload = {
        "schema": "rime.synchronizing-automata.binary-clean-exhaustion.v1",
        "scope": {
            "minimum_state_count": 2,
            "maximum_state_count": max_states,
            "permutation_letters": "all involutions",
            "nonpermutation_letters": "all rank-(n-1) transformations",
            "clean_exit_test": (
                "on every reachable nonsingleton subset, the defect-one "
                "letter either drops rank or fixes the subset"
            ),
            "isomorphism_reduction": "none; exhaustive labelled pairs",
        },
        "rows": [
            enumerate_size(state_count)
            for state_count in range(2, max_states + 1)
        ],
        "claim_boundary": {
            "enumeration_completeness": "Exact finite theorem",
            "explicit_depth_n_family": "Exact constructive theorem",
            "binary_clean_one_wait_bound": "Exact class theorem",
            "bound_D_at_most_n": "Exact class theorem",
            "extremal_depth_n_for_n_at_least_3": "Exact class theorem",
            "sharpness_of_2n_minus_3": (
                "Exact: attained only at n=2,3 in the binary clean class"
            ),
        },
    }
    payload["content_sha256"] = payload_digest(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-states", type=int, default=6)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = build_certificate(args.max_states)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "rows": [
            {
                "n": row["state_count"],
                "clean_sync": row["clean_synchronizing_pair_count"],
                "maximum_reset_depth": row["maximum_reset_depth"],
            }
            for row in payload["rows"]
        ]
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
