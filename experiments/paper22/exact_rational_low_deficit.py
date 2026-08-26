#!/usr/bin/env python3
"""Produce the exact rational low-deficit transition certificate.

The finite defect set D is represented by primitive integral cusp vectors.
For a labelled modular generator a, its successor is

    Phi_a(D) = a(D union {infinity}) minus {infinity}.

All arithmetic in this module is integer arithmetic.  Reduction modulo a
prime is used only for the explicit hostile comparison artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
PAPER_DIR = ROOT / "experiments" / "paper22"
DEFAULT_OUTPUT = PAPER_DIR / "results" / "exact_rational_low_deficit_k8_v1.json"
DEFAULT_HOSTILE_OUTPUT = PAPER_DIR / "results" / "p23_global_registry_hostile_v1.json"
PROOF_DOCUMENT = ROOT / "papers" / "paper22" / "Paper XXII.md"

Cusp = tuple[int, int]
State = tuple[Cusp, ...]

INFINITY: Cusp = (1, 0)
LABELS = ("S", "R", "R_inv")
MATRICES: dict[str, tuple[int, int, int, int]] = {
    "S": (0, -1, 1, 0),
    "R": (0, -1, 1, 1),
    "R_inv": (-1, -1, 1, 0),
}


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def content_digest(payload: dict[str, Any]) -> str:
    unsigned = dict(payload)
    unsigned.pop("content_sha256", None)
    return hashlib.sha256(canonical_json(unsigned).encode()).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_cusp(numerator: int, denominator: int) -> Cusp:
    if denominator == 0:
        if numerator == 0:
            raise ValueError("(0, 0) is not a projective cusp")
        return INFINITY
    divisor = math.gcd(abs(numerator), abs(denominator))
    numerator //= divisor
    denominator //= divisor
    if denominator < 0:
        numerator = -numerator
        denominator = -denominator
    return numerator, denominator


def transform_cusp(label: str, cusp: Cusp) -> Cusp:
    a, b, c, d = MATRICES[label]
    numerator, denominator = cusp
    return normalize_cusp(
        a * numerator + b * denominator,
        c * numerator + d * denominator,
    )


def transition(state: State, label: str) -> State:
    image = {transform_cusp(label, cusp) for cusp in (*state, INFINITY)}
    image.discard(INFINITY)
    return tuple(sorted(image))


def determinant(left: Cusp, right: Cusp) -> int:
    return left[0] * right[1] - left[1] * right[0]


def cusp_text(cusp: Cusp) -> str:
    if cusp == INFINITY:
        return "infinity"
    numerator, denominator = cusp
    return str(numerator) if denominator == 1 else f"{numerator}/{denominator}"


def state_key(state: State) -> tuple[int, State]:
    return len(state), state


def enumerate_states(max_deficit: int, max_states: int = 1_000_000) -> set[State]:
    if max_deficit < 0:
        raise ValueError("max_deficit must be nonnegative")
    initial: State = ()
    states = {initial}
    queue: deque[State] = deque([initial])
    while queue:
        state = queue.popleft()
        for label in LABELS:
            target = transition(state, label)
            if len(target) <= max_deficit and target not in states:
                states.add(target)
                queue.append(target)
                if len(states) > max_states:
                    raise RuntimeError("state safety limit exceeded before closure")
    return states


def internal_max_determinant(state: State) -> int:
    configuration = (*state, INFINITY)
    return max(
        (abs(determinant(left, right)) for index, left in enumerate(configuration) for right in configuration[index + 1 :]),
        default=0,
    )


def determinant_registry(cusps: Iterable[Cusp]) -> dict[str, Any]:
    ordered = sorted(set(cusps))
    spectrum: Counter[int] = Counter()
    maximum = 0
    maximizing_pair: tuple[Cusp, Cusp] | None = None
    for index, left in enumerate(ordered):
        for right in ordered[index + 1 :]:
            value = abs(determinant(left, right))
            if value:
                spectrum[value] += 1
                if value > maximum:
                    maximum = value
                    maximizing_pair = left, right
    return {
        "cusp_count": len(ordered),
        "cusps": [
            {"cusp": cusp_text(cusp), "primitive_vector": list(cusp)} for cusp in ordered
        ],
        "nonzero_abs_determinant_pair_count": sum(spectrum.values()),
        "nonzero_abs_determinant_spectrum": {
            str(value): count for value, count in sorted(spectrum.items())
        },
        "max_abs_determinant": maximum,
        "maximizing_pair": None
        if maximizing_pair is None
        else [
            {"cusp": cusp_text(cusp), "primitive_vector": list(cusp)}
            for cusp in maximizing_pair
        ],
    }


def serialize_state(state_id: int, state: State) -> dict[str, Any]:
    return {
        "state_id": state_id,
        "deficit": len(state),
        "defect_cusps": [cusp_text(cusp) for cusp in state],
        "primitive_vectors": [list(cusp) for cusp in state],
        "configuration_internal_max_abs_determinant": internal_max_determinant(state),
    }


def build_exact_certificate(max_deficit: int) -> dict[str, Any]:
    states = enumerate_states(max_deficit)
    ordered_states = sorted(states, key=state_key)
    state_ids = {state: index for index, state in enumerate(ordered_states)}
    layer_counts = Counter(map(len, ordered_states))

    transitions = []
    outside_targets: set[State] = set()
    closed_transition_count = 0
    outside_transition_count = 0
    for state in ordered_states:
        targets: dict[str, Any] = {}
        for label in LABELS:
            target = transition(state, label)
            if len(target) <= max_deficit:
                if target not in state_ids:
                    raise AssertionError("enumerated transition graph is not closed")
                targets[label] = {
                    "kind": "IN_RANGE",
                    "target_state_id": state_ids[target],
                    "target_deficit": len(target),
                }
                closed_transition_count += 1
            else:
                outside_targets.add(target)
                targets[label] = {
                    "kind": "OUTSIDE_MAX_DEFICIT",
                    "target_deficit": len(target),
                }
                outside_transition_count += 1
        transitions.append({"source_state_id": state_ids[state], "targets": targets})

    cumulative_layers = []
    for level in range(max_deficit + 1):
        prefix_states = [state for state in ordered_states if len(state) <= level]
        state_registry = determinant_registry(
            cusp for state in prefix_states for cusp in (*state, INFINITY)
        )
        guard_frontier = {
            target
            for state in prefix_states
            for label in LABELS
            for target in (transition(state, label),)
            if len(target) == level + 1
        }
        guard_registry = determinant_registry(
            cusp
            for state in (*prefix_states, *sorted(guard_frontier, key=state_key))
            for cusp in (*state, INFINITY)
        )
        cumulative_layers.append(
            {
                "max_deficit": level,
                "state_count": len(prefix_states),
                "exact_layer_count": layer_counts[level],
                "global_cusp_count": state_registry["cusp_count"],
                "global_max_abs_determinant": state_registry["max_abs_determinant"],
                "max_configuration_internal_abs_determinant": max(
                    map(internal_max_determinant, prefix_states), default=0
                ),
                "outgoing_guard_frontier_state_count": len(guard_frontier),
                "transition_guard_cusp_count": guard_registry["cusp_count"],
                "transition_guard_max_abs_determinant": guard_registry["max_abs_determinant"],
            }
        )

    global_registry = determinant_registry(
        cusp for state in ordered_states for cusp in (*state, INFINITY)
    )
    transition_guard_registry = determinant_registry(
        cusp
        for state in (*ordered_states, *sorted(outside_targets, key=state_key))
        for cusp in (*state, INFINITY)
    )
    payload: dict[str, Any] = {
        "schema": "paper.route-profiles.exact-rational-low-deficit.v1",
        "artifact_id": f"ROUTE-PROFILES-EXACT-RATIONAL-C-LE-{max_deficit}-V1",
        "artifact_role": "EXACT_RATIONAL_LOW_DEFICIT_TRANSITION_CERTIFICATE",
        "claim_status": "exact_computational_certificate_for_manuscript_theorem",
        "carrier": {
            "space": "P1(Q)",
            "label_order": list(LABELS),
            "primitive_cusp_convention": "(n,d), gcd(|n|,|d|)=1, d>=0, infinity=(1,0)",
            "defect_transition": "Phi_a(D)=a(D union {infinity}) minus {infinity}",
        },
        "max_deficit": max_deficit,
        "state_count": len(ordered_states),
        "layer_counts": {str(level): layer_counts[level] for level in range(max_deficit + 1)},
        "cumulative_layer_registry": cumulative_layers,
        "global_determinant_registry": global_registry,
        "transition_guard_determinant_registry": transition_guard_registry,
        "transition_closure": {
            "status": "CLOSED_THROUGH_MAX_DEFICIT",
            "in_range_transition_count": closed_transition_count,
            "outside_transition_count": outside_transition_count,
            "monotonicity_check": all(
                len(transition(state, label)) in (len(state), len(state) + 1)
                for state in ordered_states
                for label in LABELS
            ),
        },
        "states": [serialize_state(state_ids[state], state) for state in ordered_states],
        "transition_guard_frontier": [
            {
                "frontier_state_id": index,
                **{
                    key: value
                    for key, value in serialize_state(-1, state).items()
                    if key != "state_id"
                },
            }
            for index, state in enumerate(sorted(outside_targets, key=state_key))
        ],
        "transitions": transitions,
        "theorem_boundary": [
            "the finite certificate instantiates the rational C_k construction through max_deficit",
            "the accompanying manuscript proof establishes finiteness for every fixed k",
            "the global determinant registry ranges across every cusp in C_{<=k}, including infinity",
            "the sufficient stability threshold also includes the one-step deficit-(k+1) guard frontier",
            "the computed transition-guard M_k is sufficient but is not claimed to be a sharp prime threshold",
        ],
        "source_closure": [
            {
                "uri": "experiments/paper22/exact_rational_low_deficit.py",
                "sha256": file_digest(Path(__file__).resolve()),
            },
            {
                "uri": "papers/paper22/Paper XXII.md",
                "sha256": file_digest(PROOF_DOCUMENT),
            },
        ],
    }
    payload["content_sha256"] = content_digest(payload)
    return payload


def reduce_cusp(cusp: Cusp, prime: int) -> int:
    numerator, denominator = cusp
    denominator %= prime
    if denominator == 0:
        return prime
    return (numerator % prime) * pow(denominator, prime - 2, prime) % prime


def reduce_state(state: State, prime: int) -> tuple[int, ...]:
    reduced = tuple(sorted({reduce_cusp(cusp, prime) for cusp in state}))
    if prime in reduced:
        raise ValueError("a rational defect cusp reduced to infinity")
    return reduced


def finite_eval(prime: int, label: str, point: int) -> int:
    if label == "S":
        if point == prime:
            return 0
        if point == 0:
            return prime
        return (-pow(point, prime - 2, prime)) % prime
    if label == "R":
        if point == prime:
            return 0
        if point == prime - 1:
            return prime
        return (-pow(point + 1, prime - 2, prime)) % prime
    if label == "R_inv":
        if point == prime:
            return prime - 1
        if point == 0:
            return prime
        return (-1 - pow(point, prime - 2, prime)) % prime
    raise ValueError(label)


def finite_transition(defect: tuple[int, ...], prime: int, label: str) -> tuple[int, ...]:
    image = {finite_eval(prime, label, point) for point in (*defect, prime)}
    image.discard(prime)
    return tuple(sorted(image))


def finite_defect_states(prime: int, max_deficit: int) -> set[tuple[int, ...]]:
    initial: tuple[int, ...] = ()
    states = {initial}
    queue: deque[tuple[int, ...]] = deque([initial])
    while queue:
        state = queue.popleft()
        for label in LABELS:
            target = finite_transition(state, prime, label)
            if len(target) <= max_deficit and target not in states:
                states.add(target)
                queue.append(target)
    return states


def build_p23_hostile_fixture(certificate: dict[str, Any], max_deficit: int) -> dict[str, Any]:
    prime = 23
    raw_states = [
        tuple(tuple(vector) for vector in row["primitive_vectors"])
        for row in certificate["states"]
    ]
    exact_layer = [state for state in raw_states if len(state) == max_deficit]
    reductions: dict[tuple[int, ...], list[State]] = defaultdict(list)
    for state in exact_layer:
        reductions[reduce_state(state, prime)].append(state)
    duplicate_groups = sorted(
        (reduced, sorted(group, key=state_key))
        for reduced, group in reductions.items()
        if len(group) > 1
    )
    if not duplicate_groups:
        raise AssertionError("expected a p=23 cross-state collision")
    reduced, group = duplicate_groups[0]
    left, right = group[:2]

    left_by_residue = {reduce_cusp(cusp, prime): cusp for cusp in (*left, INFINITY)}
    right_by_residue = {reduce_cusp(cusp, prime): cusp for cusp in (*right, INFINITY)}
    cross_collisions = []
    for residue in sorted(set(left_by_residue) & set(right_by_residue)):
        left_cusp = left_by_residue[residue]
        right_cusp = right_by_residue[residue]
        if left_cusp == right_cusp:
            continue
        value = determinant(left_cusp, right_cusp)
        cross_collisions.append(
            {
                "residue": "infinity" if residue == prime else residue,
                "left_cusp": cusp_text(left_cusp),
                "left_vector": list(left_cusp),
                "right_cusp": cusp_text(right_cusp),
                "right_vector": list(right_cusp),
                "determinant": value,
                "determinant_divisible_by_23": value % prime == 0,
            }
        )
    if not cross_collisions or not all(
        row["determinant_divisible_by_23"] for row in cross_collisions
    ):
        raise AssertionError("hostile collision lacks its determinant witness")

    finite_states = finite_defect_states(prime, max_deficit)
    finite_layer = {state for state in finite_states if len(state) == max_deficit}
    reduced_layer = set(reductions)
    cumulative = certificate["cumulative_layer_registry"][max_deficit]
    global_registry = certificate["global_determinant_registry"]
    determinant_23_pairs = sum(
        int(count)
        for value, count in global_registry["nonzero_abs_determinant_spectrum"].items()
        if int(value) % prime == 0
    )

    payload: dict[str, Any] = {
        "schema": "paper.route-profiles.p23-global-registry-hostile.v1",
        "artifact_id": "ROUTE-PROFILES-P23-GLOBAL-REGISTRY-HOSTILE-V1",
        "artifact_role": "HOSTILE_FIXTURE_GLOBAL_VERSUS_CONFIGURATION_LOCAL_DETERMINANT_BOUND",
        "claim_status": "exact_computational_certificate",
        "source_certificate": {
            "artifact_id": certificate["artifact_id"],
            "content_sha256": certificate["content_sha256"],
        },
        "prime": prime,
        "deficit": max_deficit,
        "rational_exact_layer_state_count": len(exact_layer),
        "distinct_reduced_rational_state_count": len(reduced_layer),
        "finite_field_bfs_exact_layer_state_count": len(finite_layer),
        "reduced_rational_layer_equals_finite_bfs_layer": reduced_layer == finite_layer,
        "collision_multiplicity_histogram": {
            str(size): count
            for size, count in sorted(Counter(map(len, reductions.values())).items())
        },
        "configuration_local_bound": {
            "max_abs_determinant": cumulative["max_configuration_internal_abs_determinant"],
            "prime_exceeds_bound": prime
            > cumulative["max_configuration_internal_abs_determinant"],
            "conclusion": "INSUFFICIENT_FOR_CROSS_STATE_INJECTIVITY",
        },
        "global_registry_bound": {
            "cusp_count": global_registry["cusp_count"],
            "max_abs_determinant": global_registry["max_abs_determinant"],
            "nonzero_determinant_pairs_divisible_by_23": determinant_23_pairs,
            "prime_exceeds_bound": prime > global_registry["max_abs_determinant"],
            "conclusion": "CORRECTLY_DOES_NOT_CERTIFY_P23",
        },
        "witness": {
            "left_state": serialize_state(-1, left),
            "right_state": serialize_state(-1, right),
            "common_reduced_defect": list(reduced),
            "cross_state_cusp_collisions": cross_collisions,
        },
        "hostile_invariant": (
            "injectivity inside every individual configuration does not imply "
            "injectivity of the reduction map on the global C_{<=k} state registry"
        ),
        "boundary": [
            "p=23 is a counterexample to the configuration-local determinant threshold, not to eventual stability",
            "the global M_k criterion is sufficient and deliberately non-sharp",
            "the finite-field equality is an exact replay at the declared prime and deficit",
        ],
    }
    payload["content_sha256"] = content_digest(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-deficit", type=int, default=8)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--hostile-out", type=Path, default=DEFAULT_HOSTILE_OUTPUT)
    args = parser.parse_args()
    certificate = build_exact_certificate(args.max_deficit)
    hostile = build_p23_hostile_fixture(certificate, args.max_deficit)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    args.hostile_out.write_text(
        json.dumps(hostile, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"PASS {certificate['artifact_id']}: {certificate['state_count']} states; "
        f"M_{args.max_deficit}={certificate['global_determinant_registry']['max_abs_determinant']}"
    )
    print(
        f"PASS {hostile['artifact_id']}: {hostile['rational_exact_layer_state_count']} -> "
        f"{hostile['distinct_reduced_rational_state_count']} at p=23"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
