#!/usr/bin/env python3
"""Replay validator for the exact Fuchsian-Schreier v2 bundles."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

from core import canonical_json, content_digest
from modular_census import (
    SCHEMA as MODULAR_SCHEMA,
    build_modular_census,
    implementation_closure as modular_implementation_closure,
)
from triangle_census import (
    SCHEMA as TRIANGLE_SCHEMA,
    build_triangle_census,
    implementation_closure as triangle_implementation_closure,
)


class BundleValidationError(ValueError):
    """Raised when digest, implementation, invariant, or replay checks fail."""


def _validate_digest(payload: dict) -> None:
    unsigned = deepcopy(payload)
    try:
        supplied = unsigned.pop("content_sha256")
    except KeyError as exc:
        raise BundleValidationError("content_sha256 is required") from exc
    if not isinstance(supplied, str) or content_digest(unsigned) != supplied:
        raise BundleValidationError("bundle content digest mismatch")


def _validate_common(payload: dict) -> None:
    if not isinstance(payload, dict):
        raise BundleValidationError("bundle must be an object")
    _validate_digest(payload)
    if payload.get("artifact_role") != "EXPLORATORY_CARRIER_CENSUS":
        raise BundleValidationError("unexpected artifact role")
    if payload.get("claim_status") != "Computational Certificate":
        raise BundleValidationError("unexpected claim status")
    if payload.get("paper_evidence_status") != "NOT_PROMOTED":
        raise BundleValidationError("paper evidence must remain unpromoted")
    encoded = canonical_json(payload)
    forbidden = (
        '"sofrs"',
        '"sofaudit"',
        '"lie_depth"',
        '"laplace_beltrami"',
        '"hecke_eigenvalue"',
        '"selberg_trace"',
        '"float64"',
    )
    if any(token in encoded.lower() for token in forbidden):
        raise BundleValidationError("bundle contains a forbidden downstream carrier field")


def _validate_record(record: dict) -> None:
    if record.get("claim_status") != "Computational Certificate":
        raise BundleValidationError("record claim status is not frozen")
    if not all(record["presentation_certificate"].values()):
        raise BundleValidationError("presentation certificate failed")
    image = record["finite_image_certificate"]
    if not image["all_words_are_permutations"]:
        raise BundleValidationError("group carrier contains a non-permutation word")
    if image["rank_collapse_status"] != "NOT_PRESENT_ON_THIS_GROUP_CARRIER":
        raise BundleValidationError("rank-collapse boundary changed")
    laplacian = record["schreier_group_laplacian"]
    if not laplacian["symmetric"] or not laplacian["zero_row_sums"]:
        raise BundleValidationError("graph Laplacian certificate failed")
    if laplacian["zero_eigenvalue_multiplicity"] != 1:
        raise BundleValidationError("transitive carrier must have one zero mode")
    if laplacian["characteristic_polynomial_coefficients_descending"][-1] != 0:
        raise BundleValidationError("Laplacian characteristic polynomial lacks zero root")
    if laplacian["spanning_tree_count"] <= 0:
        raise BundleValidationError("Matrix-Tree cofactor must be positive")
    coefficients = laplacian["characteristic_polynomial_coefficients_descending"]
    state_count = len(coefficients) - 1
    expected_linear = (
        (-1) ** (state_count - 1)
        * state_count
        * laplacian["spanning_tree_count"]
    )
    if coefficients[-2] != expected_linear:
        raise BundleValidationError(
            "characteristic polynomial and Matrix-Tree cofactor disagree"
        )


def _validate_positive_word_semantics(observables: dict) -> None:
    layers = observables["positive_word_layers"]
    if [layer["depth"] for layer in layers] != list(range(1, len(layers) + 1)):
        raise BundleValidationError("positive word layers must begin at depth one")
    depth = observables["exact_first_hit_word_depth"]
    values = [
        value
        for row in depth["depth_matrix_target_by_source"]
        for value in row
    ]
    if any(
        isinstance(value, bool) or not isinstance(value, int) or value < 1
        for value in values
    ):
        raise BundleValidationError("exact word depth must use positive integers")
    identity_depth = depth["saturation"].get(
        "shortest_nonempty_identity_word_length"
    )
    if isinstance(identity_depth, bool) or not isinstance(identity_depth, int) or identity_depth < 1:
        raise BundleValidationError("positive identity-word certificate is missing")


def validate_modular_bundle(payload: dict) -> None:
    _validate_common(payload)
    if payload.get("schema") != MODULAR_SCHEMA:
        raise BundleValidationError("unsupported modular census schema")
    if payload.get("implementation") != modular_implementation_closure():
        raise BundleValidationError("modular implementation closure mismatch")
    scope = payload["scope"]
    rebuilt = build_modular_census(
        scope["odd_primes"], scope["max_word_depth"]
    )
    if canonical_json(rebuilt) != canonical_json(payload):
        raise BundleValidationError("modular census replay mismatch")
    for record in payload["records"]:
        _validate_record(record)
        image = record["finite_image_certificate"]
        if not image["order_matches"]:
            raise BundleValidationError("finite image order mismatch")
        depth = record["typed_observables"]["exact_first_hit_word_depth"]
        if depth["saturation"]["status"] != "EXACT_FINITE_GROUP_CLOSURE":
            raise BundleValidationError("word depth lacks saturation certificate")
        _validate_positive_word_semantics(record["typed_observables"])


def validate_triangle_bundle(payload: dict) -> None:
    _validate_common(payload)
    if payload.get("schema") != TRIANGLE_SCHEMA:
        raise BundleValidationError("unsupported triangle census schema")
    if payload.get("implementation") != triangle_implementation_closure():
        raise BundleValidationError("triangle implementation closure mismatch")
    scope = payload["scope"]
    rebuilt = build_triangle_census(
        [tuple(signature) for signature in scope["signatures"]],
        scope["max_index"],
        scope["max_word_depth"],
    )
    if canonical_json(rebuilt) != canonical_json(payload):
        raise BundleValidationError("triangle census replay mismatch")
    if len(payload["feature_table"]) != 3 * len(payload["records"]):
        raise BundleValidationError("triangle feature-table cardinality mismatch")
    for record in payload["records"]:
        _validate_record(record)
        if not record["simple_support_graph"]["connected"]:
            raise BundleValidationError("transitive representation has disconnected graph")
        for sectorization in record["sectorizations"].values():
            depth = sectorization["typed_observables"][
                "exact_first_hit_word_depth"
            ]
            if depth["saturation"]["status"] != "EXACT_FINITE_GROUP_CLOSURE":
                raise BundleValidationError("triangle word depth lacks saturation")
            _validate_positive_word_semantics(sectorization["typed_observables"])


def validate_payload(payload: dict) -> None:
    schema = payload.get("schema") if isinstance(payload, dict) else None
    if schema == MODULAR_SCHEMA:
        validate_modular_bundle(payload)
    elif schema == TRIANGLE_SCHEMA:
        validate_triangle_bundle(payload)
    else:
        raise BundleValidationError(f"unsupported bundle schema: {schema}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate.py RESULT.json")
    path = Path(sys.argv[1])
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_payload(payload)
    print(f"validated {payload['bundle_id']}")


if __name__ == "__main__":
    main()
