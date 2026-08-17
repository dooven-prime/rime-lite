#!/usr/bin/env python3
"""Exact bounded census of finite triangle-group Schreier carriers."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import deque
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence

from core import (
    Permutation,
    carrier_observables,
    compose_maps,
    content_digest,
    exact_laplacian_certificate,
    file_digest,
    generated_group,
    inverse_permutation,
    permutation_orbits,
    permutation_order,
    permutation_power,
    simple_support_graph_metrics,
)


SCHEMA = "rime.exploratory.fuchsian-schreier.triangle-census.v2"
PRODUCER_ID = "rime.fuchsian-schreier.triangle-census.python.v2"
PACKAGE_PATH = "experiments/exploratory/carrier_realizations/fuchsian_schreier"
DEFAULT_SIGNATURES = ((2, 3, 7), (2, 4, 5), (3, 3, 4))
Signature = tuple[int, int, int]


def implementation_closure() -> dict:
    here = Path(__file__).resolve()
    files = {
        f"{PACKAGE_PATH}/core.py": file_digest(here.with_name("core.py")),
        f"{PACKAGE_PATH}/triangle_census.py": file_digest(here),
    }
    return {
        "producer_id": PRODUCER_ID,
        "language": "Python",
        "arithmetic": "Python int and fractions.Fraction; no floating-point result fields",
        "files": files,
        "implementation_sha256": content_digest(files),
    }


def integer_partitions(
    total: int, maximum: int | None = None
) -> Iterable[tuple[int, ...]]:
    if total == 0:
        yield tuple()
        return
    maximum = total if maximum is None else min(maximum, total)
    for first in range(maximum, 0, -1):
        for rest in integer_partitions(total - first, first):
            yield (first,) + rest


def cycle_type_representative(cycle_type: Sequence[int]) -> Permutation:
    permutation: list[int] = []
    offset = 0
    for length in cycle_type:
        cycle = list(range(offset, offset + length))
        for state in cycle:
            permutation.append(cycle[(state - offset + 1) % length])
        offset += length
    return tuple(permutation)


@lru_cache(maxsize=None)
def permutations_with_order_dividing(
    degree: int, exponent: int
) -> tuple[Permutation, ...]:
    identity = tuple(range(degree))
    return tuple(
        tuple(permutation)
        for permutation in itertools.permutations(range(degree))
        if permutation_power(tuple(permutation), exponent) == identity
    )


def conjugate(permutation: Permutation, relabelling: Permutation) -> Permutation:
    inverse = inverse_permutation(relabelling)
    return compose_maps(compose_maps(relabelling, permutation), inverse)


@lru_cache(maxsize=None)
def centralizer(permutation: Permutation) -> tuple[Permutation, ...]:
    return tuple(
        candidate
        for candidate in itertools.permutations(range(len(permutation)))
        if compose_maps(permutation, candidate)
        == compose_maps(candidate, permutation)
    )


def is_transitive(generators: Sequence[Permutation]) -> bool:
    reached = {0}
    queue = deque([0])
    moves = tuple(generators) + tuple(
        inverse_permutation(generator) for generator in generators
    )
    while queue:
        state = queue.popleft()
        for move in moves:
            target = move[state]
            if target not in reached:
                reached.add(target)
                queue.append(target)
    return len(reached) == len(generators[0])


def enumerate_transitive_representations(
    signature: Signature, max_index: int
) -> list[dict]:
    ell, middle, last = signature
    reciprocal_numerator = middle * last + ell * last + ell * middle
    reciprocal_denominator = ell * middle * last
    if min(signature) < 2 or reciprocal_numerator >= reciprocal_denominator:
        raise ValueError("the census requires a hyperbolic triangle signature")
    records = []
    for degree in range(2, max_index + 1):
        identity = tuple(range(degree))
        y_candidates = permutations_with_order_dividing(degree, middle)
        allowed_x_types = [
            cycle_type
            for cycle_type in integer_partitions(degree)
            if all(ell % length == 0 for length in cycle_type)
        ]
        degree_pairs: set[tuple[Permutation, Permutation]] = set()
        for cycle_type in allowed_x_types:
            x = cycle_type_representative(cycle_type)
            relabellings = centralizer(x)
            for y in y_candidates:
                xy = compose_maps(x, y)
                if permutation_power(xy, last) != identity:
                    continue
                if not is_transitive((x, y)):
                    continue
                canonical_y = min(
                    conjugate(y, relabelling) for relabelling in relabellings
                )
                degree_pairs.add((x, canonical_y))
        for class_index, (x, y) in enumerate(sorted(degree_pairs)):
            z = inverse_permutation(compose_maps(x, y))
            records.append(
                {
                    "representation_id": (
                        f"delta-{ell}-{middle}-{last}-i{degree}-c{class_index:03d}-v2"
                    ),
                    "signature": list(signature),
                    "index": degree,
                    "class_index_within_index": class_index,
                    "x": list(x),
                    "y": list(y),
                    "z": list(z),
                    "actual_orders": {
                        "x": permutation_order(x),
                        "y": permutation_order(y),
                        "z": permutation_order(z),
                    },
                }
            )
    return records


def declared_symmetric_alphabet(
    x: Permutation, y: Permutation
) -> tuple[tuple[str, Permutation], ...]:
    result = [("x", x)]
    x_inverse = inverse_permutation(x)
    if x_inverse != x:
        result.append(("x_inv", x_inverse))
    result.append(("y", y))
    y_inverse = inverse_permutation(y)
    if y_inverse != y:
        result.append(("y_inv", y_inverse))
    return tuple(result)


def adjoint_label_map(named_alphabet: Sequence[tuple[str, Permutation]]) -> dict:
    labels = {name for name, _ in named_alphabet}
    return {
        "x": "x_inv" if "x_inv" in labels else "x",
        **({"x_inv": "x"} if "x_inv" in labels else {}),
        "y": "y_inv" if "y_inv" in labels else "y",
        **({"y_inv": "y"} if "y_inv" in labels else {}),
    }


def partition_comparisons(
    sectorizations: dict[str, Sequence[Sequence[int]]]
) -> list[dict]:
    comparisons = []
    for left_name, right_name in itertools.combinations(sectorizations, 2):
        left = sectorizations[left_name]
        right = sectorizations[right_name]
        left_of = {
            state: index for index, sector in enumerate(left) for state in sector
        }
        right_of = {
            state: index for index, sector in enumerate(right) for state in sector
        }
        table = [[0 for _ in right] for _ in left]
        for state in sorted(left_of):
            table[left_of[state]][right_of[state]] += 1
        left_refines_right = all(
            sum(value > 0 for value in row) == 1 for row in table
        )
        right_refines_left = all(
            sum(table[row][column] > 0 for row in range(len(left))) == 1
            for column in range(len(right))
        )
        comparisons.append(
            {
                "left": left_name,
                "right": right_name,
                "intersection_table": table,
                "left_refines_right": left_refines_right,
                "right_refines_left": right_refines_left,
                "equal_partitions": left_refines_right and right_refines_left,
                "alignment_status": "EXPLICIT_INTERSECTION_TABLE_ONLY",
            }
        )
    return comparisons


def audit_triangle_representation(
    base: dict, max_word_depth: int
) -> dict:
    signature = tuple(base["signature"])
    degree = base["index"]
    x = tuple(base["x"])
    y = tuple(base["y"])
    z = tuple(base["z"])
    identity = tuple(range(degree))
    named_alphabet = declared_symmetric_alphabet(x, y)
    alphabet = tuple(permutation for _, permutation in named_alphabet)
    closure = generated_group(alphabet)
    sectorizations = {
        "x_cycles": permutation_orbits(x),
        "y_cycles": permutation_orbits(y),
        "z_cycles": permutation_orbits(z),
    }
    full_orders = (
        base["actual_orders"]["x"] == signature[0]
        and base["actual_orders"]["y"] == signature[1]
        and base["actual_orders"]["z"] == signature[2]
    )
    return {
        **base,
        "claim_status": "Computational Certificate",
        "presentation_certificate": {
            "x_power_identity": permutation_power(x, signature[0]) == identity,
            "y_power_identity": permutation_power(y, signature[1]) == identity,
            "z_power_identity": permutation_power(z, signature[2]) == identity,
            "xyz_identity": compose_maps(compose_maps(x, y), z) == identity,
            "transitive": is_transitive((x, y)),
        },
        "order_retention": {
            "full_relator_orders": full_orders,
            "classification": (
                "FULL_SIGNATURE_ORDERS"
                if full_orders
                else "PROPER_ORDER_DIVISOR_QUOTIENT"
            ),
        },
        "carrier": {
            "carrier_kind": "finite_triangle_group_permutation_schreier",
            "space": {
                "scalar_field": "C",
                "dimension": degree,
                "basis_state_labels": [str(index) for index in range(degree)],
            },
            "labelled_operative_alphabet": {
                "ordered_labels": [name for name, _ in named_alphabet],
                "permutations_target_by_source": {
                    name: list(permutation) for name, permutation in named_alphabet
                },
                "adjoint_label_map": adjoint_label_map(named_alphabet),
                "word_evaluation": "letters act left-to-right; matrices multiply in reverse written order",
            },
            "lie_hall_carrier": "NOT_DECLARED",
        },
        "finite_image_certificate": {
            "generated_transformation_count": len(closure),
            "all_words_are_permutations": all(
                len(set(transformation)) == degree for transformation in closure
            ),
            "rank_collapse_status": "NOT_PRESENT_ON_THIS_GROUP_CARRIER",
        },
        "simple_support_graph": {
            "convention": "loops removed and labelled multiplicities collapsed",
            **simple_support_graph_metrics(alphabet),
        },
        "schreier_group_laplacian": exact_laplacian_certificate(alphabet),
        "sectorizations": {
            name: {
                "sectorization_id": f"{base['representation_id']}.{name}.v2",
                "kind": "coordinate_projectors_from_generator_cycles",
                "sectors": [list(sector) for sector in partition],
                "sector_sizes": [len(sector) for sector in partition],
                "complete_and_pairwise_orthogonal": True,
                "typed_observables": carrier_observables(
                    named_alphabet, partition, max_word_depth
                ),
            }
            for name, partition in sectorizations.items()
        },
        "sectorization_alignment_controls": partition_comparisons(sectorizations),
        "claim_boundary": {
            "exact": [
                "bounded simultaneous-conjugacy representative",
                "presentation relations, actual generator orders, and transitivity",
                "finite image closure, graph data, sector blocks, routes, and word depth",
                "integer graph-Laplacian characteristic polynomial, rank, and Matrix-Tree cofactor",
            ],
            "not_claimed": [
                "faithfulness of the triangle-group homomorphism",
                "classification beyond the declared index bound",
                "equivalence of the three cycle sectorizations",
                "surface Laplace-Beltrami, Hecke, moduli, or Selberg data",
                "SOFRS or SOFAUDIT artifact status",
            ],
        },
    }


def build_triangle_census(
    signatures: list[Signature], max_index: int, max_word_depth: int
) -> dict:
    if not signatures:
        raise ValueError("at least one triangle signature is required")
    if len(set(signatures)) != len(signatures):
        raise ValueError("triangle signatures must be unique")
    if max_index < 2:
        raise ValueError("max_index must be at least two")
    if max_word_depth < 1:
        raise ValueError("max_word_depth must be positive")
    records = []
    enumeration = []
    for signature in signatures:
        bases = enumerate_transitive_representations(signature, max_index)
        audited = [
            audit_triangle_representation(base, max_word_depth) for base in bases
        ]
        records.extend(audited)
        enumeration.append(
            {
                "signature": list(signature),
                "max_index": max_index,
                "class_count": len(audited),
                "full_signature_order_class_count": sum(
                    record["order_retention"]["full_relator_orders"]
                    for record in audited
                ),
                "proper_order_divisor_class_count": sum(
                    not record["order_retention"]["full_relator_orders"]
                    for record in audited
                ),
                "classes_by_index": {
                    str(index): sum(
                        record["index"] == index for record in audited
                    )
                    for index in range(2, max_index + 1)
                },
            }
        )
    feature_table = []
    for record in records:
        for name, sectorization in record["sectorizations"].items():
            observables = sectorization["typed_observables"]
            depths = observables["exact_first_hit_word_depth"][
                "depth_matrix_target_by_source"
            ]
            feature_table.append(
                {
                    "representation_id": record["representation_id"],
                    "signature": record["signature"],
                    "index": record["index"],
                    "order_retention": record["order_retention"]["classification"],
                    "finite_image_order": record["finite_image_certificate"][
                        "generated_transformation_count"
                    ],
                    "diameter": record["simple_support_graph"]["diameter"],
                    "girth": record["simple_support_graph"]["girth"],
                    "sectorization": name,
                    "sector_sizes": sectorization["sector_sizes"],
                    "maximum_first_hit_word_depth": max(
                        value
                        for row in depths
                        for value in row
                        if value is not None
                    ),
                    "route2_candidate_count": observables["route_length_two"][
                        "supported_route_candidate_count"
                    ],
                    "route2_nonzero_count": observables["route_length_two"][
                        "nonzero_routed_product_count"
                    ],
                    "route2_zero_count": observables["route_length_two"][
                        "zero_routed_product_count"
                    ],
                }
            )
    payload = {
        "schema": SCHEMA,
        "bundle_id": "fuchsian-schreier.triangle-low-index-census.v2",
        "artifact_role": "EXPLORATORY_CARRIER_CENSUS",
        "claim_status": "Computational Certificate",
        "paper_evidence_status": "NOT_PROMOTED",
        "scope": {
            "signatures": [list(signature) for signature in signatures],
            "max_index": max_index,
            "max_word_depth": max_word_depth,
            "word_layer_scope": "exact positive lengths d=1 through the declared finite depth",
            "word_depth_scope": "minimum d>=1, exact after finite group saturation",
            "equivalence": "simultaneous state relabelling with generator labels fixed",
            "enumeration_completeness": "complete only for the declared signatures and index bound",
            "numerical_spectrum": "NOT_INCLUDED",
        },
        "implementation": implementation_closure(),
        "enumeration": enumeration,
        "records": records,
        "feature_table": feature_table,
        "negative_boundaries": [
            "Relation-preserving quotients with proper divisor generator orders are labelled explicitly.",
            "Cycle sectorizations are compared by intersection tables, not silently aligned.",
            "Boolean paths, routed products, and full words are distinct typed objects.",
            "No hyperbolic-surface, Hecke, moduli, Selberg, SOFRS, or SOFAUDIT claim is included.",
        ],
    }
    payload["content_sha256"] = content_digest(payload)
    return payload


def parse_signature(value: str) -> Signature:
    parts = tuple(int(part) for part in value.split(","))
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("signature must have the form l,m,n")
    return parts


def write_markdown(payload: dict, path: Path) -> None:
    lines = [
        "# Triangle-Group Schreier Carrier Census v2",
        "",
        "All entries are exact and bounded by the declared signatures and index.",
        "No float eigenspectrum is included.",
        "",
        "| signature | classes | full orders | divisor quotients |",
        "|---|---:|---:|---:|",
    ]
    for item in payload["enumeration"]:
        lines.append(
            f"| {item['signature']} | {item['class_count']} | "
            f"{item['full_signature_order_class_count']} | "
            f"{item['proper_order_divisor_class_count']} |"
        )
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["negative_boundaries"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--signature", action="append", type=parse_signature)
    parser.add_argument("--max-index", type=int, default=7)
    parser.add_argument("--max-word-depth", type=int, default=3)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()
    signatures = args.signature or list(DEFAULT_SIGNATURES)
    payload = build_triangle_census(
        signatures, args.max_index, args.max_word_depth
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        write_markdown(payload, args.markdown)
    print(
        json.dumps(
            {
                "bundle_id": payload["bundle_id"],
                "records": len(payload["records"]),
                "content_sha256": payload["content_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
