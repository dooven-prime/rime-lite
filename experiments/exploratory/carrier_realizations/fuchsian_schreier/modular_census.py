#!/usr/bin/env python3
"""Build the exact modular P1 finite Schreier carrier census v2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core import (
    carrier_observables,
    compose_maps,
    content_digest,
    exact_laplacian_certificate,
    file_digest,
    generated_group,
    is_prime,
    modular_generators,
    permutation_orbits,
    permutation_power,
    simple_support_graph_metrics,
)


SCHEMA = "rime.exploratory.fuchsian-schreier.modular-p1-census.v2"
PRODUCER_ID = "rime.fuchsian-schreier.modular-p1.python.v2"
PACKAGE_PATH = "experiments/exploratory/carrier_realizations/fuchsian_schreier"


def implementation_closure() -> dict:
    here = Path(__file__).resolve()
    files = {
        f"{PACKAGE_PATH}/core.py": file_digest(here.with_name("core.py")),
        f"{PACKAGE_PATH}/modular_census.py": file_digest(here),
    }
    return {
        "producer_id": PRODUCER_ID,
        "language": "Python",
        "arithmetic": "Python int and fractions.Fraction; no fixed-width certificate arithmetic",
        "files": files,
        "implementation_sha256": content_digest(files),
    }


def audit_modular_prime(prime: int, max_word_depth: int) -> dict:
    if not is_prime(prime) or prime == 2:
        raise ValueError("the modular census requires an odd prime")
    if max_word_depth < 1:
        raise ValueError("max_word_depth must be positive")
    generators = modular_generators(prime)
    alphabet_names = ("S", "R", "R_inv")
    named_alphabet = tuple((name, generators[name]) for name in alphabet_names)
    alphabet = tuple(permutation for _, permutation in named_alphabet)
    sectors = permutation_orbits(generators["T"])
    closure = generated_group(alphabet)
    identity = tuple(range(prime + 1))
    expected_order = prime * (prime * prime - 1) // 2
    laplacian = exact_laplacian_certificate(alphabet)
    return {
        "record_id": f"modular-p1-f{prime}-v2",
        "claim_status": "Computational Certificate",
        "source_action": {
            "source_group": "PSL(2,Z)",
            "presentation": "<S,R | S^2=R^3=1>",
            "finite_action": f"reduction modulo {prime} on P^1(F_{prime})",
            "declared_quotient_image": f"PSL(2,F_{prime})",
        },
        "carrier": {
            "carrier_kind": "finite_permutation_schreier",
            "space": {
                "scalar_field": "C",
                "dimension": prime + 1,
                "basis_state_labels": [str(value) for value in range(prime)]
                + ["infinity"],
            },
            "sectorization": {
                "sectorization_id": f"p1-f{prime}.T-orbits.v2",
                "kind": "coordinate_projectors_from_T_orbits",
                "sectors": [list(sector) for sector in sectors],
                "sector_sizes": [len(sector) for sector in sectors],
                "complete_and_pairwise_orthogonal": True,
            },
            "labelled_operative_alphabet": {
                "ordered_labels": list(alphabet_names),
                "permutations_target_by_source": {
                    name: list(generators[name]) for name in alphabet_names
                },
                "adjoint_label_map": {
                    "S": "S",
                    "R": "R_inv",
                    "R_inv": "R",
                },
                "word_evaluation": "letters act left-to-right; matrices multiply in reverse written order",
            },
            "lie_hall_carrier": "NOT_DECLARED",
        },
        "presentation_certificate": {
            "S_squared_identity": permutation_power(generators["S"], 2)
            == identity,
            "R_cubed_identity": permutation_power(generators["R"], 3)
            == identity,
            "T_equals_S_after_R": compose_maps(
                generators["R"], generators["S"]
            )
            == generators["T"],
        },
        "finite_image_certificate": {
            "generated_transformation_count": len(closure),
            "expected_psl2_order": expected_order,
            "order_matches": len(closure) == expected_order,
            "all_words_are_permutations": all(
                len(set(transformation)) == prime + 1
                for transformation in closure
            ),
            "rank_collapse_status": "NOT_PRESENT_ON_THIS_GROUP_CARRIER",
        },
        "typed_observables": carrier_observables(
            named_alphabet, sectors, max_word_depth
        ),
        "simple_support_graph": {
            "convention": "loops removed and labelled multiplicities collapsed",
            **simple_support_graph_metrics(alphabet),
        },
        "schreier_group_laplacian": laplacian,
        "claim_boundary": {
            "exact": [
                "finite permutation relations and closure",
                "coordinate sector partition and labelled block ranks",
                "Boolean path layers, routed length-two products, and actual word layers",
                "saturated first-hit word depth",
                "integer graph-Laplacian characteristic polynomial, rational rank, and Matrix-Tree cofactor",
            ],
            "not_claimed": [
                "Lie or Hall accessibility",
                "rank-collapse dynamics",
                "surface Laplace-Beltrami spectrum",
                "Hecke action or automorphic spectrum",
                "expansion, Ramanujan, or asymptotic cross-prime theorem",
                "SOFRS or SOFAUDIT artifact status",
            ],
        },
    }


def build_modular_census(primes: list[int], max_word_depth: int) -> dict:
    if not primes:
        raise ValueError("at least one prime is required")
    if len(set(primes)) != len(primes):
        raise ValueError("primes must be unique")
    records = [audit_modular_prime(prime, max_word_depth) for prime in primes]
    payload = {
        "schema": SCHEMA,
        "bundle_id": "fuchsian-schreier.modular-p1-census.v2",
        "artifact_role": "EXPLORATORY_CARRIER_CENSUS",
        "claim_status": "Computational Certificate",
        "paper_evidence_status": "NOT_PROMOTED",
        "scope": {
            "odd_primes": primes,
            "max_word_depth": max_word_depth,
            "word_layer_scope": "exact positive lengths d=1 through the declared finite depth",
            "word_depth_scope": "minimum d>=1, exact after finite group saturation",
            "numerical_spectrum": "NOT_INCLUDED",
        },
        "implementation": implementation_closure(),
        "records": records,
        "feature_table": [
            {
                "prime": prime,
                "state_count": record["carrier"]["space"]["dimension"],
                "sector_sizes": record["carrier"]["sectorization"][
                    "sector_sizes"
                ],
                "finite_image_order": record["finite_image_certificate"][
                    "generated_transformation_count"
                ],
                "maximum_first_hit_word_depth": max(
                    value
                    for row in record["typed_observables"][
                        "exact_first_hit_word_depth"
                    ]["depth_matrix_target_by_source"]
                    for value in row
                    if value is not None
                ),
                "route2_zero_count": record["typed_observables"][
                    "route_length_two"
                ]["zero_routed_product_count"],
                "spanning_tree_count": record["schreier_group_laplacian"][
                    "spanning_tree_count"
                ],
            }
            for prime, record in zip(primes, records)
        ],
        "negative_boundaries": [
            "The finite Schreier/group Laplacian is not a surface Laplace-Beltrami operator.",
            "Boolean paths, routed products, and full words are retained as distinct objects.",
            "All group words have full operator rank; word accessibility is not rank collapse.",
            "This bundle is not a SOFRS report, SOFAUDIT artifact, or paper-local certificate.",
        ],
    }
    payload["content_sha256"] = content_digest(payload)
    return payload


def write_markdown(payload: dict, path: Path) -> None:
    lines = [
        "# Modular P1 Schreier Carrier Census v2",
        "",
        "All table entries are exact finite certificates. No float eigenspectrum is included.",
        "",
        "| p | states | sectors | image order | max first-hit depth | route-2 zeros | spanning trees |",
        "|---:|---:|---|---:|---:|---:|---:|",
    ]
    for row in payload["feature_table"]:
        lines.append(
            f"| {row['prime']} | {row['state_count']} | {row['sector_sizes']} | "
            f"{row['finite_image_order']} | {row['maximum_first_hit_word_depth']} | "
            f"{row['route2_zero_count']} | {row['spanning_tree_count']} |"
        )
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["negative_boundaries"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primes", type=int, nargs="+", default=[3, 5, 7])
    parser.add_argument("--max-word-depth", type=int, default=4)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()
    payload = build_modular_census(args.primes, args.max_word_depth)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
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
