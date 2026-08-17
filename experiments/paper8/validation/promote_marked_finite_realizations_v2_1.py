#!/usr/bin/env python3
"""Promote exact finite permutation conformance evidence for Paper VIII v2.1."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EXPLORATORY_DIR = (
    ROOT
    / "experiments"
    / "exploratory"
    / "carrier_realizations"
    / "fuchsian_schreier"
)
RESULTS_DIR = ROOT / "experiments" / "paper8" / "results" / "v2.1"
MODULAR_PATH = EXPLORATORY_DIR / "results" / "modular_p1_census_v2.json"
TRIANGLE_PATH = EXPLORATORY_DIR / "results" / "triangle_low_index_census_v2.json"
CERTIFICATE_PATH = RESULTS_DIR / "marked_finite_realization_conformance_v2_1.json"
SUMMARY_PATH = RESULTS_DIR / "marked_finite_realization_conformance_v2_1.md"

if str(EXPLORATORY_DIR) not in sys.path:
    sys.path.insert(0, str(EXPLORATORY_DIR))

from core import (  # noqa: E402
    boolean_path_layers,
    canonical_json,
    compose_maps,
    content_digest,
    exact_word_depth,
    exact_word_layers,
    generated_group_positive_words,
    route_length_two_profile,
    support_matrix,
)
from validate import validate_payload as validate_exploratory_payload  # noqa: E402


SCHEMA = "paper8.marked-finite-realization-conformance.v2.1"
PRODUCER_ID = "paper8.marked-finite-realization-promotion.python.v2.1"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def implementation_closure() -> dict:
    here = Path(__file__).resolve()
    files = {
        relative(here): file_sha256(here),
        relative(EXPLORATORY_DIR / "core.py"): file_sha256(
            EXPLORATORY_DIR / "core.py"
        ),
        relative(EXPLORATORY_DIR / "modular_census.py"): file_sha256(
            EXPLORATORY_DIR / "modular_census.py"
        ),
        relative(EXPLORATORY_DIR / "triangle_census.py"): file_sha256(
            EXPLORATORY_DIR / "triangle_census.py"
        ),
        relative(EXPLORATORY_DIR / "validate.py"): file_sha256(
            EXPLORATORY_DIR / "validate.py"
        ),
    }
    return {
        "producer_id": PRODUCER_ID,
        "files": files,
        "implementation_sha256": content_digest(files),
    }


def source_descriptor(path: Path, payload: dict) -> dict:
    return {
        "path": relative(path),
        "schema": payload["schema"],
        "bundle_id": payload["bundle_id"],
        "artifact_sha256": file_sha256(path),
        "content_sha256": payload["content_sha256"],
        "upstream_paper_evidence_status": payload["paper_evidence_status"],
        "promotion_role": "SOURCE_PROVENANCE_AND_REPLAY_INPUT",
    }


def named_alphabet(record: dict) -> tuple[tuple[str, tuple[int, ...]], ...]:
    data = record["carrier"]["labelled_operative_alphabet"]
    return tuple(
        (label, tuple(data["permutations_target_by_source"][label]))
        for label in data["ordered_labels"]
    )


def saturation_receipt(
    realization_id: str,
    alphabet: tuple[tuple[str, tuple[int, ...]], ...],
    sectors: list[list[int]],
    observables: dict,
) -> dict:
    labels = [label for label, _ in alphabet]
    generators = tuple(permutation for _, permutation in alphabet)
    positive_closure = generated_group_positive_words(generators)
    shortest_counts = Counter(len(word) for word in positive_closure.values())
    stabilization_depth = max(shortest_counts)
    cumulative = 0
    closure_trace = []
    for depth in range(1, stabilization_depth + 1):
        new_count = shortest_counts.get(depth, 0)
        cumulative += new_count
        closure_trace.append(
            {
                "depth": depth,
                "new_shortest_represented_operators": new_count,
                "cumulative_represented_operators": cumulative,
            }
        )
    right_closed = all(
        compose_maps(transformation, generator) in positive_closure
        for transformation in positive_closure
        for generator in generators
    )
    depth_record = exact_word_depth(alphabet, sectors)
    if canonical_json(depth_record) != canonical_json(
        observables["exact_first_hit_word_depth"]
    ):
        raise AssertionError(f"first-hit replay mismatch for {realization_id}")
    depth_values = [
        value
        for row in depth_record["depth_matrix_target_by_source"]
        for value in row
    ]
    closure_operators = [list(item) for item in sorted(positive_closure)]
    label_to_operator = [
        {"label": label, "permutation_target_by_source": list(permutation)}
        for label, permutation in alphabet
    ]
    return {
        "realization_id": realization_id,
        "label_count": len(labels),
        "distinct_represented_letter_count": len(set(generators)),
        "label_alphabet_sha256": content_digest(labels),
        "label_to_operator_sha256": content_digest(label_to_operator),
        "sectorization_sha256": content_digest(sectors),
        "represented_positive_closure_sha256": content_digest(closure_operators),
        "represented_positive_closure_order": len(positive_closure),
        "closure_trace": closure_trace,
        "closure_stabilization_depth": stabilization_depth,
        "right_multiplication_closed": right_closed,
        "shortest_nonempty_identity_word_length": depth_record["saturation"][
            "shortest_nonempty_identity_word_length"
        ],
        "first_hit_depth_sha256": content_digest(
            depth_record["depth_matrix_target_by_source"]
        ),
        "first_hit_witnesses_sha256": content_digest(
            depth_record["first_hit_witnesses"]
        ),
        "bounded_word_support_layers_sha256": content_digest(
            observables["positive_word_layers"]
        ),
        "finite_first_hit_count": sum(value is not None for value in depth_values),
        "infinite_after_saturation_count": sum(
            value is None for value in depth_values
        ),
        "saturation_status": "EXACT_FINITE_POSITIVE_CLOSURE",
    }


def route_support(route_profile: dict, sector_count: int) -> list[list[int]]:
    support = [[0 for _ in range(sector_count)] for _ in range(sector_count)]
    for pair in route_profile["ordered_letter_pair_profiles"]:
        for target, _, source in pair[
            "nonzero_routes_target_middle_source"
        ]:
            support[target][source] = 1
    return support


def hostile_path_word_witness() -> dict:
    first = (0, 1, 3, 2)
    second = (1, 0, 3, 2)
    sectors = [[0, 1, 2], [3]]
    alphabet = (("a", first), ("b", second))
    direct = support_matrix((first, second), sectors)
    path_two = boolean_path_layers(direct, 2)[1]["support_target_by_source"]
    route_profile = route_length_two_profile(alphabet, sectors)
    route_two = route_support(route_profile, len(sectors))
    word_two = exact_word_layers((first, second), sectors, 2)[1][
        "support_target_by_source"
    ]
    length_two_operators = sorted(
        {
            compose_maps(left, right)
            for left in (first, second)
            for right in (first, second)
        }
    )
    if not (
        path_two == [[1, 1], [1, 1]]
        and route_two == [[1, 0], [0, 1]]
        and word_two == [[1, 0], [0, 1]]
    ):
        raise AssertionError("the four-state hostile witness changed")
    return {
        "witness_id": "paper8.path-word-four-state.v2.1",
        "state_set": [0, 1, 2, 3],
        "marked_partition": sectors,
        "label_to_permutation_target_by_source": {
            "a": list(first),
            "b": list(second),
        },
        "aggregate_direct_support_target_by_source": direct,
        "boolean_path_2_target_by_source": path_two,
        "actual_route_2_target_by_source": route_two,
        "actual_word_2_target_by_source": word_two,
        "distinct_length_two_represented_operators": [
            list(operator) for operator in length_two_operators
        ],
        "route_2_candidate_count": route_profile[
            "supported_route_candidate_count"
        ],
        "route_2_nonzero_count": route_profile["nonzero_routed_product_count"],
        "route_2_zero_count": route_profile["zero_routed_product_count"],
        "exact_first_hit_word_depth": exact_word_depth(alphabet, sectors),
        "certified_relation": "W_2_EQUALS_ROUTE_2_STRICT_SUBSET_PATH_2",
    }


def label_collision_witnesses(triangle: dict) -> list[dict]:
    witnesses = []
    for record in triangle["records"]:
        alphabet = named_alphabet(record)
        for left_index, (left_label, left_operator) in enumerate(alphabet):
            for right_label, right_operator in alphabet[left_index + 1 :]:
                if left_operator == right_operator:
                    witnesses.append(
                        {
                            "representation_id": record["representation_id"],
                            "left_label": left_label,
                            "right_label": right_label,
                            "shared_permutation_target_by_source": list(
                                left_operator
                            ),
                            "labels_distinct": left_label != right_label,
                            "represented_operators_equal": True,
                        }
                    )
    if not witnesses:
        raise AssertionError("the triangle census lost its label-collision witness")
    return witnesses


def marked_partition_witness(triangle: dict) -> dict:
    record = next(
        item
        for item in triangle["records"]
        if item["representation_id"] == "delta-2-3-7-i7-c000-v2"
    )
    partitions = {
        name: sectorization["sectors"]
        for name, sectorization in record["sectorizations"].items()
    }
    digests = {name: content_digest(value) for name, value in partitions.items()}
    if len(set(digests.values())) != 3:
        raise AssertionError("marked triangle partitions are no longer distinct")
    return {
        "representation_id": record["representation_id"],
        "shared_labelled_operator_family_sha256": content_digest(
            record["carrier"]["labelled_operative_alphabet"]
        ),
        "marked_partitions": partitions,
        "marked_partition_sha256": digests,
        "pairwise_controls": record["sectorization_alignment_controls"],
        "interpretation": (
            "three marked SOF realizations on one represented action; "
            "intersection tables do not identify the partitions"
        ),
    }


def build_certificate() -> dict:
    modular = load_json(MODULAR_PATH)
    triangle = load_json(TRIANGLE_PATH)
    validate_exploratory_payload(modular)
    validate_exploratory_payload(triangle)
    if modular["scope"]["odd_primes"] != [3, 5, 7, 11, 13, 17]:
        raise AssertionError("unexpected modular promotion scope")
    if triangle["scope"]["signatures"] != [[2, 3, 7], [2, 4, 5], [3, 3, 4]]:
        raise AssertionError("unexpected triangle promotion signatures")
    if triangle["scope"]["max_index"] != 7:
        raise AssertionError("unexpected triangle promotion index bound")

    saturation = []
    for record in modular["records"]:
        saturation.append(
            saturation_receipt(
                record["record_id"],
                named_alphabet(record),
                record["carrier"]["sectorization"]["sectors"],
                record["typed_observables"],
            )
        )
    for record in triangle["records"]:
        alphabet = named_alphabet(record)
        for name, sectorization in record["sectorizations"].items():
            saturation.append(
                saturation_receipt(
                    f"{record['representation_id']}.{name}",
                    alphabet,
                    sectorization["sectors"],
                    sectorization["typed_observables"],
                )
            )

    full_order_count = sum(
        record["order_retention"]["full_relator_orders"]
        for record in triangle["records"]
    )
    collision_witnesses = label_collision_witnesses(triangle)
    certificate = {
        "schema": SCHEMA,
        "certificate_id": "paper8.marked-finite-realization-conformance.v2.1",
        "artifact_id": "P8V2.1-CONFORMANCE",
        "paper": "Paper VIII",
        "candidate_version": "2.1",
        "artifact_role": "PAPER_OWNED_PROMOTED_CONFORMANCE_CERTIFICATE",
        "claim_status": "Computational Certificate",
        "theorem_relationship": "CONFORMANCE_WITNESS_NOT_THEOREM_PREMISE",
        "promotion_decision": "ACCEPTED_FOR_PAPER8_V2_1_CANDIDATE",
        "source_artifacts": [
            source_descriptor(MODULAR_PATH, modular),
            source_descriptor(TRIANGLE_PATH, triangle),
        ],
        "implementation": implementation_closure(),
        "promoted_scope": {
            "modular_prime_count": len(modular["records"]),
            "modular_primes": modular["scope"]["odd_primes"],
            "triangle_signatures": triangle["scope"]["signatures"],
            "triangle_max_index": triangle["scope"]["max_index"],
            "triangle_representation_count": len(triangle["records"]),
            "triangle_full_signature_order_count": full_order_count,
            "triangle_proper_order_divisor_count": (
                len(triangle["records"]) - full_order_count
            ),
            "triangle_marked_sectorization_count": sum(
                len(record["sectorizations"])
                for record in triangle["records"]
            ),
            "saturation_receipt_count": len(saturation),
            "label_collision_witness_count": len(collision_witnesses),
        },
        "marked_partition_witness": marked_partition_witness(triangle),
        "label_collision_witnesses": collision_witnesses,
        "path_route_word_hostile_witness": hostile_path_word_witness(),
        "finite_saturation_receipts": saturation,
        "promoted_claims": [
            {
                "claim_id": "P8V2.1-CERT-01",
                "statement": (
                    "The declared modular and triangle actions instantiate exact "
                    "finite marked operator SOF cores."
                ),
                "status": "Computational Certificate",
            },
            {
                "claim_id": "P8V2.1-CERT-02",
                "statement": (
                    "Distinct source labels may have equal represented "
                    "permutation operators without being identified."
                ),
                "status": "Computational Certificate",
            },
            {
                "claim_id": "P8V2.1-CERT-03",
                "statement": (
                    "The four-state exact witness has W_2=Route_2 strictly "
                    "contained in the Boolean Path_2 relation."
                ),
                "status": "Computational Certificate",
            },
            {
                "claim_id": "P8V2.1-CERT-04",
                "statement": (
                    "Every promoted first-hit word depth is replayed after "
                    "complete finite represented-image saturation."
                ),
                "status": "Computational Certificate",
            },
        ],
        "negative_boundaries": [
            "No finite group representation canonically selects a marked sectorization by this construction.",
            "No Lie/Hall carrier or Lie depth is promoted.",
            "No generic strict separation of positive and star closures is claimed.",
            "No surface, Hecke, moduli, Selberg, or automorphic claim is promoted.",
            "Graph-Laplacian diagnostics are not part of the Paper VIII claim surface.",
            "The upstream exploratory bundles remain provenance inputs, not Paper VIII evidence by themselves.",
        ],
    }
    certificate["content_sha256"] = content_digest(certificate)
    return certificate


def write_summary(certificate: dict, path: Path) -> None:
    scope = certificate["promoted_scope"]
    witness = certificate["path_route_word_hostile_witness"]
    lines = [
        "# Paper VIII v2.1 Marked Finite-Realization Certificate",
        "",
        "**Status:** Paper-owned Computational Certificate.",
        "",
        "This artifact promotes exact conformance evidence without making the",
        "exploratory source bundles paper evidence by themselves.",
        "",
        "## Scope",
        "",
        f"- Modular actions: {scope['modular_prime_count']} primes {scope['modular_primes']}.",
        f"- Triangle actions: {scope['triangle_representation_count']} records through index {scope['triangle_max_index']}.",
        f"- Triangle order status: {scope['triangle_full_signature_order_count']} full-order and {scope['triangle_proper_order_divisor_count']} proper-divisor records.",
        f"- Marked triangle sectorizations: {scope['triangle_marked_sectorization_count']}.",
        f"- Exact saturation receipts: {scope['saturation_receipt_count']}.",
        f"- Equal-operator label witnesses: {scope['label_collision_witness_count']}.",
        "",
        "## Four-State Control",
        "",
        f"- `Path_2 = {witness['boolean_path_2_target_by_source']}`",
        f"- `Route_2 = {witness['actual_route_2_target_by_source']}`",
        f"- `W_2 = {witness['actual_word_2_target_by_source']}`",
        f"- Certified relation: `{witness['certified_relation']}`.",
        "",
        "## Source Artifacts",
        "",
    ]
    for source in certificate["source_artifacts"]:
        lines.append(
            f"- `{source['path']}`: content `{source['content_sha256']}`."
        )
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in certificate["negative_boundaries"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=CERTIFICATE_PATH)
    parser.add_argument("--markdown", type=Path, default=SUMMARY_PATH)
    args = parser.parse_args()
    certificate = build_certificate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_summary(certificate, args.markdown)
    print(
        json.dumps(
            {
                "certificate_id": certificate["certificate_id"],
                "content_sha256": certificate["content_sha256"],
                "saturation_receipts": certificate["promoted_scope"][
                    "saturation_receipt_count"
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
