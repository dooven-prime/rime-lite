#!/usr/bin/env python3
"""Generate source-addressed certificates for admitted slow automaton families."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from registry import (
    CARRIER_CONTRACT,
    Transition,
    file_digest,
    payload_digest,
    pair_collision_profile,
    rank,
    rank_preserving_escape_profile,
    shortest_subset_reset_word,
)


FIXED_ALPHABET_SOURCE = "https://arxiv.org/abs/1609.06853"
LOW_RANK_IDEMPOTENT_SOURCE = "https://arxiv.org/abs/1807.07048"


def compact_escape_certificate(profile: dict) -> dict:
    """Retain auditable layer coordinates without serializing every graph."""
    layers = []
    for layer in profile["layers"]:
        omega_histogram = Counter(
            item["structural_next_drop_distance"]
            for item in layer["escape_records"]
        )
        scc_histogram = Counter(
            len(component) for component in layer["rank_preserving_sccs"]
        )
        layers.append({
            "rank": layer["rank"],
            "reachable_subset_count": len(layer["reachable_subsets"]),
            "rank_preserving_edge_count": len(layer["rank_preserving_edges"]),
            "collision_exit_count": len(layer["collision_exits"]),
            "collision_boundary_size": len(layer["collision_boundary"]),
            "structural_next_drop_distance_histogram": {
                str(distance): count
                for distance, count in sorted(omega_histogram.items())
            },
            "rank_preserving_scc_size_histogram": {
                str(size): count
                for size, count in sorted(scc_histogram.items())
            },
            "largest_rank_preserving_scc_size": (
                layer["largest_rank_preserving_scc_size"]
            ),
            "rank_layer_max_escape_distance": (
                layer["rank_layer_max_escape_distance"]
            ),
        })
    return {
        "carrier": profile["carrier"],
        "full_profile_sha256": payload_digest(profile),
        "layers": layers,
        "sync_upper_bound_sum_Omega_r": (
            profile["sync_upper_bound_sum_Omega_r"]
        ),
        "compatible_escape_budget": profile["compatible_escape_budget"],
        "potential_certificate": profile["potential_certificate"],
        "classical_compression_benchmark": (
            profile["classical_compression_benchmark"]
        ),
        "bound_status": profile["bound_status"],
    }


def compact_pair_collision_certificate(profile: dict) -> dict:
    finite_distances = [
        item["distance"]
        for item in profile["pair_merge_distances"]
        if item["distance"] is not None
    ]
    return {
        "carrier": profile["carrier"],
        "full_profile_sha256": payload_digest(profile),
        "pair_count": len(profile["pair_merge_distances"]),
        "finite_pair_count": len(finite_distances),
        "infinite_pair_count": (
            len(profile["pair_merge_distances"]) - len(finite_distances)
        ),
        "maximum_finite_pair_merge_distance": (
            max(finite_distances) if finite_distances else None
        ),
    }


def cerny_transition(n: int) -> Transition:
    if n < 2:
        raise ValueError("the admitted Cerny family starts at n=2")
    merge = tuple(0 if state == n - 1 else state for state in range(n))
    cycle = tuple((state + 1) % n for state in range(n))
    return merge, cycle


def family_record(
    *,
    family: str,
    transition: Transition,
    expected_reset_length: int,
    source: str,
    cohort_tags: list[str],
) -> dict:
    n = len(transition[0])
    reset_word = shortest_subset_reset_word(transition)
    assert reset_word is not None
    escape = rank_preserving_escape_profile(transition)
    pair_profile = pair_collision_profile(transition)
    letter_ranks = [rank(letter) for letter in transition]
    reset_length = len(reset_word)
    return {
        "family": family,
        "cohort_tags": cohort_tags,
        "source": source,
        "state_count": n,
        "alphabet_size": 2,
        "transition": [list(letter) for letter in transition],
        "letter_ranks": letter_ranks,
        "shortest_reset_word": list(reset_word),
        "reset_length": reset_length,
        "expected_family_value": expected_reset_length,
        "matches_expected_family_value": reset_length == expected_reset_length,
        "rank_preserving_escape_certificate": compact_escape_certificate(escape),
        "pair_collision_certificate": compact_pair_collision_certificate(
            pair_profile
        ),
        "symbolic_feature_row": {
            "automaton_id": f"{family}-n{n}",
            "cohort": "known_slow_family",
            "family": "Cerny",
            "state_count": n,
            "reset_length": reset_length,
            "minimum_letter_rank": min(letter_ranks),
            "maximum_letter_rank_drop": n - min(letter_ranks),
            "maximum_rank_layer_escape_distance": max(
                layer["rank_layer_max_escape_distance"]
                for layer in escape["layers"]
            ),
            "sum_rank_layer_escape_bound": escape["sync_upper_bound_sum_Omega_r"],
            "compatible_escape_budget": escape["compatible_escape_budget"][
                "value"
            ],
            "potential_certificate_verified": escape["potential_certificate"][
                "local_descent_inequalities_verified"
            ],
            "largest_rank_preserving_scc_size": max(
                layer["largest_rank_preserving_scc_size"]
                for layer in escape["layers"]
            ),
        },
        "claim_status": "Computational Certificate",
    }


def cerny_record(n: int) -> dict:
    return family_record(
        family="Cerny",
        transition=cerny_transition(n),
        expected_reset_length=(n - 1) ** 2,
        source=FIXED_ALPHABET_SOURCE,
        cohort_tags=["defect_one_plus_cycle", "extremal_baseline"],
    )


def low_rank_idempotent_cerny_transition(total_states: int) -> Transition:
    """Return Volkov's H(C_m) on ``total_states=2m`` states."""
    if total_states < 4 or total_states % 2:
        raise ValueError("the H(C_m) family requires an even state count >= 4")
    base_states = total_states // 2
    base_letters = cerny_transition(base_states)
    lifted_letters = []
    for base_letter in base_letters:
        lifted_letters.append(tuple(
            state if state < base_states else base_letter[state - base_states]
            for state in range(total_states)
        ))
    copy_to_prime = tuple(
        state + base_states if state < base_states else state
        for state in range(total_states)
    )
    return tuple(lifted_letters) + (copy_to_prime,)


def low_rank_idempotent_record(total_states: int) -> dict:
    transition = low_rank_idempotent_cerny_transition(total_states)
    half = total_states // 2
    assert all(rank(letter) == half for letter in transition)
    assert all(
        tuple(letter[letter[state]] for state in range(total_states)) == letter
        for letter in transition
    )
    return family_record(
        family="Volkov-H-Cerny-idempotent",
        transition=transition,
        expected_reset_length=2 * (half - 1) ** 2,
        source=LOW_RANK_IDEMPOTENT_SOURCE,
        cohort_tags=["rank_n_over_2", "all_letters_idempotent"],
    )


def fixed_alphabet_transition(n: int, alphabet_size: int) -> Transition:
    """Return the explicit Theorem-3 family of de Bondt--Don--Zantema."""
    if n < 4 or alphabet_size not in {3, 4, 5}:
        raise ValueError("require n >= 4 and alphabet size in {3,4,5}")

    def tail_cycle(state: int) -> int:
        return (state + 1) % n

    a = tuple([1, 2, 3] + [tail_cycle(state) for state in range(3, n)])
    b = tuple([0, 2, 2] + list(range(3, n)))
    c = tuple([2, 2, 3] + [tail_cycle(state) for state in range(3, n)])
    d = tuple([1, 3, 3] + [tail_cycle(state) for state in range(3, n)])
    e = tuple([2, 3, 3] + [tail_cycle(state) for state in range(3, n)])
    if alphabet_size == 3:
        return a, b, e
    if alphabet_size == 4:
        return a, b, c, e
    return a, b, c, d, e


def fixed_alphabet_record(n: int, alphabet_size: int) -> dict:
    constant = {3: 4, 4: 3, 5: 2}[alphabet_size]
    return family_record(
        family=f"fixed-alphabet-{alphabet_size}",
        transition=fixed_alphabet_transition(n, alphabet_size),
        expected_reset_length=n * n - 3 * n + constant,
        source=FIXED_ALPHABET_SOURCE,
        cohort_tags=["fixed_alphabet", "quadratic_slow_family"],
    )


def build_family_suite(min_states: int, max_states: int) -> dict:
    if min_states < 2 or max_states < min_states:
        raise ValueError("require 2 <= min_states <= max_states")
    records = [cerny_record(n) for n in range(min_states, max_states + 1)]
    records.extend(
        low_rank_idempotent_record(n)
        for n in range(max(4, min_states), max_states + 1)
        if n % 2 == 0
    )
    records.extend(
        fixed_alphabet_record(n, alphabet_size)
        for alphabet_size in (3, 4, 5)
        for n in range(max(4, min_states), max_states + 1)
    )
    payload = {
        "schema": "rime.synchronizing-automata.family-suite.v1",
        "carrier_contract": CARRIER_CONTRACT,
        "scope": {
            "min_state_count": min_states,
            "max_state_count": max_states,
            "admitted_families": [
                "Cerny",
                "Volkov-H-Cerny-idempotent",
                "fixed-alphabet-3",
                "fixed-alphabet-4",
                "fixed-alphabet-5",
            ],
        },
        "references": [
            {
                "family": "Cerny",
                "source": FIXED_ALPHABET_SOURCE,
                "use": "family definition and established reset-threshold context",
            },
            {
                "family": "Volkov-H-Cerny-idempotent",
                "source": LOW_RANK_IDEMPOTENT_SOURCE,
                "use": "H(A) construction, idempotence, rank, and reset threshold",
            },
            {
                "family": "fixed-alphabet-3/4/5",
                "source": FIXED_ALPHABET_SOURCE,
                "use": "Theorem 3 transition tables and reset thresholds",
            },
        ],
        "records": records,
        "producer": {
            "script": "experiments/paper23/families.py",
            "script_sha256": file_digest(Path(__file__)),
            "registry": "experiments/paper23/registry.py",
            "registry_sha256": file_digest(Path(__file__).with_name("registry.py")),
        },
        "claim_boundary": "Finite certificates for explicitly admitted family instances. This suite does not re-prove the imported family theorems and does not yet include the pending sink-state or broader defect-one/permutation backlog.",
    }
    payload["content_sha256"] = payload_digest(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-states", type=int, default=2)
    parser.add_argument("--max-states", type=int, default=12)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = build_family_suite(args.min_states, args.max_states)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "families": payload["scope"]["admitted_families"],
        "records": len(payload["records"]),
        "max_reset_length": max(record["reset_length"] for record in payload["records"]),
    }, indent=2))


if __name__ == "__main__":
    main()
