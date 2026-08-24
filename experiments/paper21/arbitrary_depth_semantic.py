#!/usr/bin/env python3
"""Exact controls for the arbitrary-depth marked route semantics.

The manuscript proofs are mathematical. This producer supplies paper-owned
replay for the prefix-pole criterion, the fixed-field reachable-subset
automaton, and the finite exceptional-characteristic sets used by the
fixed-depth stabilization theorem.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from copy import deepcopy
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULT = (
    ROOT
    / "experiments"
    / "paper21"
    / "results"
    / "arbitrary_depth_semantic_v1.json"
)
SCHEMA = "paper.route-profiles.arbitrary-depth-semantic.v1"
ARTIFACT_ID = "ROUTE-PROFILES-ARBITRARY-DEPTH-V1"
LABELS = ("S", "R", "R_inv")
INTEGRAL_LIFTS = {
    "S": ((0, -1), (1, 0)),
    "R": ((0, -1), (1, 1)),
    "R_inv": ((-1, -1), (1, 0)),
}


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def content_digest(value: object) -> str:
    if isinstance(value, dict):
        value = deepcopy(value)
        value.pop("content_sha256", None)
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def inverse_mod(value: int, prime: int) -> int:
    return pow(value % prime, prime - 2, prime)


def eval_label(prime: int, label: str, point: int) -> int:
    """Evaluate a declared map; ``prime`` denotes the infinity state."""

    infinity = prime
    if label == "S":
        if point == infinity:
            return 0
        if point == 0:
            return infinity
        return (-inverse_mod(point, prime)) % prime
    if label == "R":
        if point == infinity:
            return 0
        if point == prime - 1:
            return infinity
        return (-inverse_mod(point + 1, prime)) % prime
    if label == "R_inv":
        if point == infinity:
            return prime - 1
        if point == 0:
            return infinity
        return (-1 - inverse_mod(point, prime)) % prime
    raise ValueError(f"unknown label: {label}")


def sector(prime: int, point: int) -> int:
    return 0 if point == prime else 1


def matmul(
    left: tuple[tuple[int, int], tuple[int, int]],
    right: tuple[tuple[int, int], tuple[int, int]],
) -> tuple[tuple[int, int], tuple[int, int]]:
    return tuple(
        tuple(
            sum(left[row][inner] * right[inner][column] for inner in range(2))
            for column in range(2)
        )
        for row in range(2)
    )  # type: ignore[return-value]


def prefix_pole_vectors(word: Sequence[str]) -> tuple[tuple[int, int], ...]:
    """Return homogeneous integral lifts of ``G_k^{-1}(infinity)``."""

    current = ((1, 0), (0, 1))
    poles = [(1, 0)]
    for label in word:
        current = matmul(INTEGRAL_LIFTS[label], current)
        poles.append((current[1][1], -current[1][0]))
    return tuple(poles)


def reduce_projective(prime: int, vector: tuple[int, int]) -> int:
    x, y = vector[0] % prime, vector[1] % prime
    if y == 0:
        return prime
    return (x * inverse_mod(y, prime)) % prime


def prefix_poles(prime: int, word: Sequence[str]) -> tuple[int, ...]:
    return tuple(reduce_projective(prime, vector) for vector in prefix_pole_vectors(word))


def brute_survivors(
    prime: int, word: Sequence[str], sector_path: Sequence[int]
) -> frozenset[int]:
    if len(sector_path) != len(word) + 1:
        raise ValueError("sector path length does not match word depth")
    survivors = set()
    for start in range(prime + 1):
        point = start
        itinerary = [sector(prime, point)]
        for label in word:
            point = eval_label(prime, label, point)
            itinerary.append(sector(prime, point))
        if tuple(itinerary) == tuple(sector_path):
            survivors.add(start)
    return frozenset(survivors)


def prefix_pole_survivors(
    prime: int, word: Sequence[str], sector_path: Sequence[int]
) -> frozenset[int]:
    """Evaluate the arbitrary-depth prefix-pole classification."""

    if len(sector_path) != len(word) + 1:
        raise ValueError("sector path length does not match word depth")
    poles = prefix_poles(prime, word)
    forced = [poles[index] for index, value in enumerate(sector_path) if value == 0]
    forbidden = {poles[index] for index, value in enumerate(sector_path) if value == 1}
    if forced:
        point = forced[0]
        if all(candidate == point for candidate in forced) and point not in forbidden:
            return frozenset({point})
        return frozenset()
    return frozenset(set(range(prime + 1)) - forbidden)


def supported_path(sector_path: Sequence[int]) -> bool:
    return all(left != 0 or right != 0 for left, right in zip(sector_path, sector_path[1:]))


def fibonacci(index: int) -> int:
    left, right = 0, 1
    for _ in range(index):
        left, right = right, left + right
    return left


def verify_prefix_pole_semantics(
    primes: Iterable[int], max_depth: int
) -> list[dict]:
    records = []
    for prime in primes:
        checked = 0
        for depth in range(1, max_depth + 1):
            supported_count = 0
            for word in itertools.product(LABELS, repeat=depth):
                for path in itertools.product((0, 1), repeat=depth + 1):
                    brute = brute_survivors(prime, word, path)
                    classified = prefix_pole_survivors(prime, word, path)
                    if brute != classified:
                        raise AssertionError(
                            f"prefix-pole mismatch: p={prime}, word={word}, path={path}"
                        )
                    if supported_path(path):
                        supported_count += 1
                    checked += 1
            expected = (3**depth) * fibonacci(depth + 3)
            if supported_count != expected:
                raise AssertionError("Boolean candidate recurrence mismatch")
        records.append(
            {
                "prime": prime,
                "max_depth": max_depth,
                "word_path_pairs_checked": checked,
                "status": "PASS",
            }
        )
    return records


def fixed_depth_semantic_summaries(
    primes: Sequence[int], max_depth: int
) -> list[dict]:
    """Build compact exact signatures for the legacy fixed-depth bridge."""

    records = []
    for prime in primes:
        profiles = []
        for depth in range(1, max_depth + 1):
            zero_routes = []
            candidate_count = 0
            for word in itertools.product(LABELS, repeat=depth):
                for path in itertools.product((0, 1), repeat=depth + 1):
                    if not supported_path(path):
                        continue
                    candidate_count += 1
                    if not prefix_pole_survivors(prime, word, path):
                        zero_routes.append(
                            {"word": list(word), "sector_path": list(path)}
                        )
            zero_routes.sort(key=lambda item: (item["word"], item["sector_path"]))
            profiles.append(
                {
                    "depth": depth,
                    "candidate_count": candidate_count,
                    "nonzero_count": candidate_count - len(zero_routes),
                    "zero_count": len(zero_routes),
                    "zero_route_signature": content_digest(zero_routes),
                }
            )
        records.append({"prime": prime, "profiles": profiles})
    return records


def reachable_subset_automaton(prime: int) -> dict:
    """Build the exact deterministic survivor automaton for one prime field."""

    sector_sets = (frozenset({prime}), frozenset(range(prime)))
    starts = ((0, sector_sets[0]), (1, sector_sets[1]))
    states: list[tuple[int, frozenset[int]]] = []
    index: dict[tuple[int, frozenset[int]], int] = {}
    queue: deque[tuple[int, frozenset[int]]] = deque()

    def admit(state: tuple[int, frozenset[int]]) -> None:
        if state not in index:
            index[state] = len(states)
            states.append(state)
            queue.append(state)

    for state in starts:
        admit(state)

    transitions: list[list[int]] = []
    while queue:
        source_sector, survivor_set = queue.popleft()
        local = []
        for label in LABELS:
            for target_sector in (0, 1):
                if source_sector == 0 and target_sector == 0:
                    continue
                target_set = sector_sets[target_sector]
                successor_set = frozenset(
                    image
                    for point in survivor_set
                    if (image := eval_label(prime, label, point)) in target_set
                )
                successor = (target_sector, successor_set)
                admit(successor)
                local.append(index[successor])
        transitions.append(local)

    if len(transitions) != len(states):
        raise AssertionError("reachable automaton closure is incomplete")

    histogram = Counter((state_sector, len(points)) for state_sector, points in states)
    return {
        "prime": prime,
        "states": states,
        "index": index,
        "starts": tuple(index[state] for state in starts),
        "transitions": tuple(tuple(row) for row in transitions),
        "state_count": len(states),
        "state_bound": 2 + 2**prime,
        "state_histogram": {
            f"sector_{state_sector}_card_{cardinality}": count
            for (state_sector, cardinality), count in sorted(histogram.items())
        },
    }


def transfer_profiles(machine: dict, max_depth: int) -> list[dict]:
    state_count = machine["state_count"]
    vector = [0] * state_count
    for start in machine["starts"]:
        vector[start] += 1
    profiles = []
    for depth in range(max_depth + 1):
        nonzero = sum(
            multiplicity
            for multiplicity, (_, survivor_set) in zip(vector, machine["states"])
            if survivor_set
        )
        candidate = sum(vector)
        expected_candidate = (3**depth) * fibonacci(depth + 3)
        if candidate != expected_candidate:
            raise AssertionError("transfer automaton candidate count mismatch")
        profiles.append(
            {
                "depth": depth,
                "candidate_count": candidate,
                "nonzero_count": nonzero,
                "zero_count": candidate - nonzero,
            }
        )
        successor = [0] * state_count
        for source, multiplicity in enumerate(vector):
            if not multiplicity:
                continue
            for target in machine["transitions"][source]:
                successor[target] += multiplicity
        vector = successor
    return profiles


def prime_factors(value: int) -> set[int]:
    value = abs(value)
    factors = set()
    divisor = 2
    while divisor * divisor <= value:
        while value % divisor == 0:
            factors.add(divisor)
            value //= divisor
        divisor += 1
    if value > 1:
        factors.add(value)
    return factors


def normalize_integral_projective(vector: tuple[int, int]) -> tuple[int, int]:
    divisor = math.gcd(abs(vector[0]), abs(vector[1]))
    if divisor == 0:
        raise ValueError("zero vector is not a projective point")
    normalized = (vector[0] // divisor, vector[1] // divisor)
    if normalized[0] < 0 or (normalized[0] == 0 and normalized[1] < 0):
        normalized = (-normalized[0], -normalized[1])
    return normalized


def exceptional_characteristics(max_depth: int) -> list[dict]:
    """Compute the exact finite sets E_d from nonzero pole determinants."""

    levels = [((((1, 0), (0, 1))), ((1, 0),))]
    records = []
    for depth in range(1, max_depth + 1):
        next_level = []
        exceptional = set()
        determinant_count = 0
        nonzero_determinant_count = 0
        determinant_spectrum = set()
        distinct_prefix_pole_class_sum = 0
        maximum_entry = 0
        for matrix, poles in levels:
            for label in LABELS:
                product = matmul(INTEGRAL_LIFTS[label], matrix)
                pole = (product[1][1], -product[1][0])
                prefix_pole_list = poles + (pole,)
                for left in range(len(prefix_pole_list)):
                    for right in range(left + 1, len(prefix_pole_list)):
                        determinant_count += 1
                        determinant = (
                            prefix_pole_list[left][0] * prefix_pole_list[right][1]
                            - prefix_pole_list[left][1] * prefix_pole_list[right][0]
                        )
                        if determinant:
                            nonzero_determinant_count += 1
                            determinant_spectrum.add(abs(determinant))
                            exceptional.update(prime_factors(determinant))
                distinct_prefix_pole_class_sum += len(
                    {
                        normalize_integral_projective(vector)
                        for vector in prefix_pole_list
                    }
                )
                maximum_entry = max(
                    maximum_entry,
                    *(abs(entry) for row in product for entry in row),
                )
                next_level.append((product, prefix_pole_list))
        levels = next_level
        candidate_count = (3**depth) * fibonacci(depth + 3)
        generic_nonzero_count = (3**depth) + distinct_prefix_pole_class_sum
        records.append(
            {
                "depth": depth,
                "exceptional_characteristics": sorted(exceptional),
                "word_count": 3**depth,
                "prefix_pole_determinants_checked": determinant_count,
                "nonzero_determinants_factored": nonzero_determinant_count,
                "prefix_determinant_spectrum": sorted(determinant_spectrum),
                "prefix_determinant_spectrum_cardinality": len(determinant_spectrum),
                "distinct_prefix_pole_class_sum": distinct_prefix_pole_class_sum,
                "generic_nonzero_route_count": generic_nonzero_count,
                "generic_zero_route_count": candidate_count - generic_nonzero_count,
                "maximum_integral_matrix_entry": maximum_entry,
            }
        )
    return records


def polynomial_sequence_check(
    sequence: Sequence[int], numerator: Sequence[int], denominator: Sequence[int]
) -> bool:
    if not denominator or denominator[0] != 1:
        raise ValueError("denominator must have constant coefficient one")
    for depth in range(len(sequence)):
        coefficient = sum(
            denominator[offset] * sequence[depth - offset]
            for offset in range(min(depth, len(denominator) - 1) + 1)
        )
        expected = numerator[depth] if depth < len(numerator) else 0
        if coefficient != expected:
            return False
    return True


def build_payload(
    *,
    semantic_primes: Sequence[int] = (2, 3, 5, 7),
    semantic_max_depth: int = 5,
    signature_primes: Sequence[int] = (2, 3, 5, 7, 11, 13),
    automaton_primes: Sequence[int] = (2, 3, 5, 7, 11, 13, 17, 19),
    transfer_max_depth: int = 10,
) -> dict:
    semantic_checks = verify_prefix_pole_semantics(semantic_primes, semantic_max_depth)
    signature_bridge = fixed_depth_semantic_summaries(
        signature_primes, semantic_max_depth
    )
    exceptional = exceptional_characteristics(transfer_max_depth)
    machines = {}
    for prime in automaton_primes:
        machine = reachable_subset_automaton(prime)
        profiles = transfer_profiles(machine, transfer_max_depth)
        machines[prime] = {"machine": machine, "profiles": profiles}

    stabilization = []
    for record in exceptional:
        depth = record["depth"]
        exceptional_set = set(record["exceptional_characteristics"])
        eligible = [
            prime
            for prime in automaton_primes
            if prime > depth and prime not in exceptional_set
        ]
        zero_counts = {
            machines[prime]["profiles"][depth]["zero_count"] for prime in eligible
        }
        if len(zero_counts) > 1:
            raise AssertionError(f"stabilization count shadow failed at depth {depth}")
        if zero_counts and zero_counts != {record["generic_zero_route_count"]}:
            raise AssertionError(f"generic profile bridge failed at depth {depth}")
        stabilization.append(
            {
                "depth": depth,
                "eligible_sample_primes": eligible,
                "generic_zero_count": record["generic_zero_route_count"],
                "common_zero_count": next(iter(zero_counts)) if zero_counts else None,
                "status": "PASS_COUNT_SHADOW" if len(eligible) >= 2 else "INSUFFICIENT_SAMPLE",
            }
        )

    automaton_records = []
    for prime in automaton_primes:
        machine = machines[prime]["machine"]
        automaton_records.append(
            {
                "prime": prime,
                "reachable_state_count": machine["state_count"],
                "ambient_state_bound": machine["state_bound"],
                "state_histogram": machine["state_histogram"],
                "profiles": machines[prime]["profiles"],
            }
        )

    candidate_sequence = [
        machines[2]["profiles"][depth]["candidate_count"]
        for depth in range(transfer_max_depth + 1)
    ]
    p2_nonzero = [
        machines[2]["profiles"][depth]["nonzero_count"]
        for depth in range(transfer_max_depth + 1)
    ]
    p3_nonzero = [
        machines[3]["profiles"][depth]["nonzero_count"]
        for depth in range(transfer_max_depth + 1)
    ]
    generating_function_examples = {
        "coefficient_order": "ascending powers of z",
        "coefficient_check_max_depth": transfer_max_depth,
        "candidate": {
            "numerator": [2, 3],
            "denominator": [1, -3, -9],
            "checked": polynomial_sequence_check(
                candidate_sequence, [2, 3], [1, -3, -9]
            ),
        },
        "F2_nonzero": {
            "numerator": [2, 3],
            "denominator": [1, -3],
            "checked": polynomial_sequence_check(p2_nonzero, [2, 3], [1, -3]),
        },
        "F3_nonzero": {
            "numerator": [2, 1, -1],
            "denominator": [1, -4, 2, 3],
            "checked": polynomial_sequence_check(
                p3_nonzero, [2, 1, -1], [1, -4, 2, 3]
            ),
        },
    }
    if not all(item["checked"] for item in generating_function_examples.values() if isinstance(item, dict)):
        raise AssertionError("explicit generating-function replay failed")

    producer = Path(__file__).resolve()
    payload = {
        "schema": SCHEMA,
        "artifact_id": ARTIFACT_ID,
        "artifact_role": "PAPER_OWNED_ARBITRARY_DEPTH_SEMANTIC_REPLAY",
        "claim_status": "MANUSCRIPT_THEOREMS_WITH_EXACT_FINITE_REPLAY",
        "theorem_contract": {
            "prefix_pole_classification": (
                "A route survivor set is the intersection of forced prefix-pole "
                "singletons at zero sectors and prefix-pole complements at one sectors."
            ),
            "fixed_field_automaton": (
                "For each fixed finite field, reachable survivor subsets form a finite "
                "deterministic weighted automaton."
            ),
            "rational_generating_functions": (
                "For each fixed finite field F, B_F(z), N_F(z), and Z_F(z) are "
                "rational transfer-matrix series."
            ),
            "fixed_depth_stabilization": (
                "At fixed depth d, the labelled zero-route set equals the generic "
                "integral prefix-pole profile for |F|>d outside E_d."
            ),
            "generic_profile": (
                "The generic depth-d zero-route set is determined by the rational "
                "prefix-pole equality relation; its count is candidate count minus "
                "the sum over words of one plus the number of pole classes."
            ),
        },
        "implementation": {
            "language": "Python",
            "arithmetic": "exact finite permutations and Python bigint integral matrix lifts",
            "producer": {"path": repo_path(producer), "sha256": sha256(producer)},
        },
        "semantic_replay": {
            "primes": list(semantic_primes),
            "max_depth": semantic_max_depth,
            "checks": semantic_checks,
        },
        "fixed_depth_signature_bridge": {
            "primes": list(signature_primes),
            "max_depth": semantic_max_depth,
            "profiles": signature_bridge,
        },
        "exceptional_characteristics": exceptional,
        "fixed_field_automata": automaton_records,
        "stabilization_count_shadow": stabilization,
        "generating_function_examples": generating_function_examples,
        "claim_boundary": {
            "certifies": (
                "exact replay of the declared finite checks and construction data; "
                "the manuscript owns the general proofs"
            ),
            "does_not_certify": [
                "a field-independent finite automaton or uniform state bound",
                "a single rational generating function valid for every finite field",
                "an all-depth closed scalar formula for zero routes",
                "a closed form or recurrence for the prefix determinant spectra",
                "depth-asymptotic convergence or a growth constant",
                "RG, Hecke, modular-form, spectral, or causal interpretation",
            ],
        },
    }
    payload["content_sha256"] = content_digest(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_RESULT)
    args = parser.parse_args()
    payload = build_payload()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "artifact_id": payload["artifact_id"],
                "content_sha256": payload["content_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
