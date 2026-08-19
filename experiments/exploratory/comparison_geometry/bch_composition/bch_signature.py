#!/usr/bin/env python3
"""Frozen Heisenberg BCH signatures and comparison-state projections.

This exploratory implementation owns one exact carrier only: the rational
three-dimensional, class-two Heisenberg Lie algebra. It does not provide a
generic BCH engine or an admitted SOFRS/SOFAUDIT evaluator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from typing import Mapping, Sequence


SIGNATURE_SCHEMA = "rime.exploratory.bch-composition-signature.v1"
ALIGNMENT_SCHEMA = "rime.exploratory.bch-generator-alignment.v1"
BUNDLE_SCHEMA = "rime.exploratory.bch-composition-control-bundle.v1"
IMPLEMENTATION_ID = "rime.bch.heisenberg3.class2.rational.v1"
CARRIER_ID = "heisenberg3.class2.rational.v1"
BASIS = ("X", "Y", "Z")
INPUT_GENERATORS = ("X", "Y")
NILPOTENCY_CLASS = 2
COMPARISON_SCOPES = frozenset({"full_bch", "through_degree"})
BCH_STATUSES = frozenset(
    {
        "EXACT_MATCH",
        "CERTIFIED_MISMATCH",
        "TRUNCATED_MATCH",
        "UNRESOLVED",
        "INCOMPARABLE",
        "NOT_DECLARED",
    }
)
SOFAUDIT_STATES = frozenset(
    {"ALIGNED", "MISMATCH", "INCOMPARABLE", "UNRESOLVED", "NOT_DECLARED"}
)


class SignatureValidationError(ValueError):
    """Raised when a signature fails digest, declaration, or replay checks."""


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def implementation_sha256() -> str:
    return _file_digest(Path(__file__).resolve())


def carrier_definition() -> dict:
    definition = {
        "carrier_id": CARRIER_ID,
        "coefficient_domain": "Q",
        "basis": [
            {"label": "X", "degree": 1},
            {"label": "Y", "degree": 1},
            {"label": "Z", "degree": 2},
        ],
        "ordered_basis_labels": list(BASIS),
        "bracket_table": [
            {"left": "X", "right": "Y", "result": {"Z": "1"}},
            {"left": "Y", "right": "X", "result": {"Z": "-1"}},
        ],
        "zero_brackets": [["X", "Z"], ["Z", "X"], ["Y", "Z"], ["Z", "Y"]],
        "nilpotency_class": NILPOTENCY_CLASS,
        "quotient_relations": ["[X,Y]=Z", "[X,Z]=0", "[Y,Z]=0"],
        "mathematical_scope": "finite rational class-two Lie algebra",
    }
    definition["carrier_definition_sha256"] = _digest(definition)
    return definition


def generator_registration() -> dict:
    registration = {
        "registration_id": "heisenberg3.X-Y-generators.v1",
        "registration_role": "SIGNATURE_LOCAL_GENERATOR_REGISTRATION",
        "carrier_id": CARRIER_ID,
        "generators": [
            {"generator_id": "generator.X", "basis_label": "X"},
            {"generator_id": "generator.Y", "basis_label": "Y"},
        ],
        "generated_hall_basis": ["X", "Y", "Z"],
        "derived_basis_labels": ["Z"],
    }
    registration["generator_registration_sha256"] = _digest(registration)
    return registration


def identity_generator_alignment() -> dict:
    """Return the only alignment admitted by this frozen local evaluator."""

    carrier_sha256 = carrier_definition()["carrier_definition_sha256"]
    registration_sha256 = generator_registration()[
        "generator_registration_sha256"
    ]
    alignment = {
        "schema": ALIGNMENT_SCHEMA,
        "alignment_id": "heisenberg3.identity-generators.v1",
        "alignment_kind": "EXPLICIT_GENERATOR_BIJECTION",
        "reference": {
            "carrier_id": CARRIER_ID,
            "carrier_definition_sha256": carrier_sha256,
            "generator_registration_sha256": registration_sha256,
        },
        "target": {
            "carrier_id": CARRIER_ID,
            "carrier_definition_sha256": carrier_sha256,
            "generator_registration_sha256": registration_sha256,
        },
        "generator_map": [
            {
                "reference_generator_id": "generator.X",
                "target_generator_id": "generator.X",
                "reference_basis_label": "X",
                "target_basis_label": "X",
                "coefficient": "1",
            },
            {
                "reference_generator_id": "generator.Y",
                "target_generator_id": "generator.Y",
                "reference_basis_label": "Y",
                "target_basis_label": "Y",
                "coefficient": "1",
            },
        ],
        "induced_hall_basis_map": [
            {
                "reference_basis_label": "X",
                "target_basis_label": "X",
                "alignment_origin": "REGISTERED_GENERATOR",
            },
            {
                "reference_basis_label": "Y",
                "target_basis_label": "Y",
                "alignment_origin": "REGISTERED_GENERATOR",
            },
            {
                "reference_basis_label": "Z",
                "target_basis_label": "Z",
                "alignment_origin": "INDUCED_BY_BRACKET_PRESERVATION",
            },
        ],
        "bracket_preservation": "EXACT_IDENTITY_ON_FROZEN_CARRIER",
    }
    alignment["generator_alignment_sha256"] = _digest(alignment)
    return alignment


def validate_generator_alignment(alignment: dict) -> dict:
    if not isinstance(alignment, dict):
        raise SignatureValidationError("generator alignment must be an object")
    unsigned = deepcopy(alignment)
    try:
        supplied_digest = unsigned.pop("generator_alignment_sha256")
    except KeyError as exc:
        raise SignatureValidationError(
            "generator_alignment_sha256 is required"
        ) from exc
    if _digest(unsigned) != supplied_digest:
        raise SignatureValidationError("generator alignment digest mismatch")
    if alignment != identity_generator_alignment():
        raise SignatureValidationError(
            "generator alignment is not registered by the frozen evaluator"
        )
    return alignment


def carrier_declaration(truncation_order: int) -> dict:
    if isinstance(truncation_order, bool) or not isinstance(truncation_order, int):
        raise ValueError("truncation_order must be an integer")
    if truncation_order < 1:
        raise ValueError("truncation_order must be at least one")
    return {
        "implementation_id": IMPLEMENTATION_ID,
        "implementation_sha256": implementation_sha256(),
        "carrier_id": CARRIER_ID,
        "carrier_definition_sha256": carrier_definition()["carrier_definition_sha256"],
        "generator_registration": generator_registration(),
        "composition_convention": {
            "product_form": "exp(x_1)...exp(x_m)",
            "sequence_order": "left_to_right",
        },
        "hall_basis": {
            "basis_id": "hall.heisenberg.X-Y-Z.v1",
            "ordered_labels": list(BASIS),
            "bracket_orientation": "[X,Y]=Z",
        },
        "coefficient_domain": "Q",
        "quotient_relation_id": "heisenberg3.class2.quotient.v1",
        "truncation_order": truncation_order,
        "logarithm_semantics": "finite_nilpotent_bch_polynomial",
        "matrix_logarithm_chart": "NOT_APPLICABLE",
        "remainder_status": (
            "ZERO_BY_NILPOTENCY"
            if truncation_order >= NILPOTENCY_CLASS
            else "NOT_INCLUDED"
        ),
    }


def _fraction(value: Fraction | int | str) -> Fraction:
    if isinstance(value, Fraction):
        return value
    return Fraction(value)


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _term(term: Mapping[str, Fraction | int | str]) -> dict[str, Fraction]:
    unknown = set(term) - set(INPUT_GENERATORS)
    if unknown:
        raise ValueError(
            f"unregistered input generator labels: {sorted(unknown)}"
        )
    normalized = {}
    for label in INPUT_GENERATORS:
        value = _fraction(term.get(label, 0))
        if value:
            normalized[label] = value
    return normalized


def _serialized_term(term: Mapping[str, Fraction]) -> dict[str, str]:
    return {
        label: _fraction_text(term[label])
        for label in INPUT_GENERATORS
        if term.get(label, Fraction(0))
    }


def _bracket(
    first: Mapping[str, Fraction], second: Mapping[str, Fraction]
) -> dict[str, Fraction]:
    coefficient = first.get("X", Fraction(0)) * second.get("Y", Fraction(0))
    coefficient -= first.get("Y", Fraction(0)) * second.get("X", Fraction(0))
    return {"Z": coefficient} if coefficient else {}


def bch_signature(
    sequence: Sequence[Mapping[str, Fraction | int | str]],
    *,
    truncation_order: int = NILPOTENCY_CLASS,
) -> dict:
    """Build one replayable signature under the frozen Heisenberg carrier."""

    declaration = carrier_declaration(truncation_order)
    terms = [_term(item) for item in sequence]
    degree_one = {
        label: sum(
            (item.get(label, Fraction(0)) for item in terms), Fraction(0)
        )
        for label in INPUT_GENERATORS
    }
    homogeneous: dict[str, dict[str, str]] = {
        "1": {
            label: _fraction_text(degree_one[label])
            for label in INPUT_GENERATORS
            if degree_one[label]
        }
    }
    if truncation_order >= 2:
        degree_two = Fraction(0)
        for index, first in enumerate(terms):
            for second in terms[index + 1 :]:
                degree_two += _bracket(first, second).get("Z", Fraction(0)) / 2
        if degree_two:
            homogeneous["2"] = {"Z": _fraction_text(degree_two)}

    payload = {
        "schema": SIGNATURE_SCHEMA,
        "sequence": [_serialized_term(term) for term in terms],
        "carrier_declaration": declaration,
        "homogeneous_coefficients": homogeneous,
        "nilpotency_class": NILPOTENCY_CLASS,
        "completion_status": (
            "EXACT_FINITE_BCH"
            if truncation_order >= NILPOTENCY_CLASS
            else "FORMAL_TRUNCATION"
        ),
    }
    payload["signature_sha256"] = _digest(payload)
    return payload


def _unsigned_signature(payload: dict) -> dict:
    unsigned = deepcopy(payload)
    try:
        unsigned.pop("signature_sha256")
    except KeyError as exc:
        raise SignatureValidationError("signature_sha256 is required") from exc
    return unsigned


def validate_and_replay_signature(payload: dict) -> dict:
    """Validate a signature and reproduce it from its exact sequence."""

    if not isinstance(payload, dict):
        raise SignatureValidationError("signature must be an object")
    unsigned = _unsigned_signature(payload)
    if _digest(unsigned) != payload["signature_sha256"]:
        raise SignatureValidationError("signature digest mismatch")
    expected_keys = {
        "schema",
        "sequence",
        "carrier_declaration",
        "homogeneous_coefficients",
        "nilpotency_class",
        "completion_status",
    }
    if set(unsigned) != expected_keys:
        raise SignatureValidationError("signature fields do not match the frozen schema")
    if payload["schema"] != SIGNATURE_SCHEMA:
        raise SignatureValidationError("unsupported signature schema")

    declaration = payload["carrier_declaration"]
    if not isinstance(declaration, dict):
        raise SignatureValidationError("carrier_declaration must be an object")
    if declaration.get("implementation_id") != IMPLEMENTATION_ID:
        raise SignatureValidationError("implementation is not registered locally")
    order = declaration.get("truncation_order")
    try:
        expected_declaration = carrier_declaration(order)
    except (TypeError, ValueError) as exc:
        raise SignatureValidationError(
            f"invalid truncation_order declaration: {exc}"
        ) from exc
    if declaration != expected_declaration:
        raise SignatureValidationError("carrier declaration or implementation digest mismatch")

    try:
        rebuilt = bch_signature(payload["sequence"], truncation_order=order)
    except (TypeError, ValueError) as exc:
        raise SignatureValidationError(f"signature sequence is invalid: {exc}") from exc
    if _canonical(rebuilt) != _canonical(payload):
        raise SignatureValidationError("signature replay mismatch")
    return rebuilt


def _candidate_projection(
    comparison_state: str,
    *,
    scope: str,
    full_bch_comparison_state: str | None = None,
) -> dict:
    if comparison_state not in SOFAUDIT_STATES:
        raise ValueError(f"unsupported SOFAUDIT projection: {comparison_state}")
    projection = {
        "projection_status": "EXPLORATORY_NOT_ADMITTED",
        "coordinate_family_candidate": "bch_composition",
        "value_schema_id_candidate": SIGNATURE_SCHEMA,
        "comparison_state": comparison_state,
        "comparison_scope": scope,
    }
    if full_bch_comparison_state is not None:
        projection["full_bch_comparison_state"] = full_bch_comparison_state
    return projection


def _state(
    bch_status: str,
    *,
    scope: str,
    comparison_state: str,
    full_bch_comparison_state: str | None = None,
    **details: object,
) -> dict:
    if bch_status not in BCH_STATUSES:
        raise ValueError(f"unsupported BCH status: {bch_status}")
    return {
        "bch_status": bch_status,
        **details,
        "sofaudit_projection": _candidate_projection(
            comparison_state,
            scope=scope,
            full_bch_comparison_state=full_bch_comparison_state,
        ),
    }


def _implementation_id(payload: dict) -> str:
    try:
        value = payload["carrier_declaration"]["implementation_id"]
    except (KeyError, TypeError) as exc:
        raise SignatureValidationError("implementation_id is required") from exc
    if not isinstance(value, str) or not value:
        raise SignatureValidationError("implementation_id must be nonempty")
    return value


def compare_signatures(
    left: dict | None,
    right: dict | None,
    *,
    generator_alignment: dict | None = None,
    comparison_scope: str = "full_bch",
) -> dict:
    """Replay and compare two signatures under a declared comparison scope."""

    if comparison_scope not in COMPARISON_SCOPES:
        raise ValueError(f"unsupported comparison_scope: {comparison_scope}")
    if left is None or right is None:
        return _state(
            "NOT_DECLARED",
            scope=comparison_scope,
            comparison_state="NOT_DECLARED",
            reason="bch_composition capability is absent on at least one side",
        )

    left_implementation = _implementation_id(left)
    right_implementation = _implementation_id(right)
    if (
        left_implementation != IMPLEMENTATION_ID
        or right_implementation != IMPLEMENTATION_ID
        or left_implementation != right_implementation
    ):
        return _state(
            "INCOMPARABLE",
            scope=comparison_scope,
            comparison_state="INCOMPARABLE",
            reason="no common locally registered BCH evaluator implementation",
            implementation_ids=[left_implementation, right_implementation],
        )

    left_replayed = validate_and_replay_signature(left)
    right_replayed = validate_and_replay_signature(right)
    if generator_alignment is None:
        return _state(
            "INCOMPARABLE",
            scope=comparison_scope,
            comparison_state="INCOMPARABLE",
            reason="an explicit registered generator alignment is required",
        )
    validated_alignment = validate_generator_alignment(generator_alignment)
    alignment_details = {
        "generator_alignment_id": validated_alignment["alignment_id"],
        "generator_alignment_sha256": validated_alignment[
            "generator_alignment_sha256"
        ],
    }
    left_declaration = left_replayed["carrier_declaration"]
    right_declaration = right_replayed["carrier_declaration"]
    if left_declaration != right_declaration:
        return _state(
            "INCOMPARABLE",
            scope=comparison_scope,
            comparison_state="INCOMPARABLE",
            reason="replayed BCH declarations are incompatible",
            **alignment_details,
        )

    order = int(left_declaration["truncation_order"])
    left_coefficients = left_replayed["homogeneous_coefficients"]
    right_coefficients = right_replayed["homogeneous_coefficients"]
    for degree in range(1, order + 1):
        labels = INPUT_GENERATORS if degree == 1 else ("Z",)
        for label in labels:
            left_value = Fraction(
                left_coefficients.get(str(degree), {}).get(label, "0")
            )
            right_value = Fraction(
                right_coefficients.get(str(degree), {}).get(label, "0")
            )
            if left_value != right_value:
                return _state(
                    "CERTIFIED_MISMATCH",
                    scope=comparison_scope,
                    comparison_state="MISMATCH",
                    lowest_differing_degree=degree,
                    basis_label=label,
                    left_coefficient=_fraction_text(left_value),
                    right_coefficient=_fraction_text(right_value),
                    checked_through_degree=order,
                    **alignment_details,
                )

    exact = (
        left_replayed["completion_status"] == "EXACT_FINITE_BCH"
        and right_replayed["completion_status"] == "EXACT_FINITE_BCH"
    )
    if exact:
        return _state(
            "EXACT_MATCH",
            scope=comparison_scope,
            comparison_state="ALIGNED",
            checked_through_degree=order,
            completion_certificate="ZERO_REMAINDER_BY_CLASS_TWO_NILPOTENCY",
            **alignment_details,
        )
    if comparison_scope == "through_degree":
        return _state(
            "TRUNCATED_MATCH",
            scope=comparison_scope,
            comparison_state="ALIGNED",
            full_bch_comparison_state="UNRESOLVED",
            checked_through_degree=order,
            reason="retained homogeneous coefficients agree only through the declared degree",
            **alignment_details,
        )
    return _state(
        "UNRESOLVED",
        scope=comparison_scope,
        comparison_state="UNRESOLVED",
        full_bch_comparison_state="UNRESOLVED",
        checked_through_degree=order,
        bounded_status="TRUNCATED_MATCH",
        reason="a truncated match does not establish full BCH equality",
        **alignment_details,
    )


def _unsupported_implementation_stub(signature: dict) -> dict:
    stub = deepcopy(signature)
    stub["carrier_declaration"]["implementation_id"] = (
        "external.unregistered.bch.v1"
    )
    return stub


def build_control_bundle() -> dict:
    alignment = identity_generator_alignment()
    xy = bch_signature([{"X": 1}, {"Y": 1}])
    yx = bch_signature([{"Y": 1}, {"X": 1}])
    xy_copy = bch_signature([{"X": 1}, {"Y": 1}])
    xy_degree_one = bch_signature([{"X": 1}, {"Y": 1}], truncation_order=1)
    xy_degree_one_copy = bch_signature(
        [{"X": 1}, {"Y": 1}], truncation_order=1
    )
    bundle = {
        "schema": BUNDLE_SCHEMA,
        "bundle_id": "bch.heisenberg-order-control.v1",
        "artifact_role": "EXPLORATORY_CONTROL_BUNDLE",
        "claim_status": "Computational Certificate",
        "paper_evidence_status": "NOT_PROMOTED",
        "implementation": {
            "implementation_id": IMPLEMENTATION_ID,
            "implementation_sha256": implementation_sha256(),
            "language": "Python",
            "arithmetic": "fractions.Fraction",
        },
        "carrier_definition": carrier_definition(),
        "generator_alignments": {"identity": alignment},
        "signatures": {
            "XY": xy,
            "YX": yx,
            "XY_copy": xy_copy,
            "XY_degree_one": xy_degree_one,
            "XY_degree_one_copy": xy_degree_one_copy,
        },
        "comparisons": {
            "XY_vs_YX": compare_signatures(
                xy, yx, generator_alignment=alignment
            ),
            "XY_vs_copy": compare_signatures(
                xy, xy_copy, generator_alignment=alignment
            ),
            "degree_one_bounded_match": compare_signatures(
                xy_degree_one,
                xy_degree_one_copy,
                generator_alignment=alignment,
                comparison_scope="through_degree",
            ),
            "degree_one_full_bch": compare_signatures(
                xy_degree_one,
                xy_degree_one_copy,
                generator_alignment=alignment,
                comparison_scope="full_bch",
            ),
            "missing_capability": compare_signatures(xy, None),
            "missing_alignment": compare_signatures(xy, xy_copy),
            "unregistered_implementation": compare_signatures(
                xy,
                _unsupported_implementation_stub(xy),
                generator_alignment=alignment,
            ),
        },
        "candidate_sof_interface": {
            "paper_xii_role": "retain a validated BCH signature and evidence reference in an optional report module",
            "paper_xiii_role": "compare retained signatures through an optional Audit Profile coordinate",
            "paper_xiii_nonrole": "derive BCH coefficients from raw generators inside SOFAUDIT",
            "runtime_destination": "future digest-registered evaluator and replay closure in sof-runtime",
        },
        "negative_boundaries": [
            "This bundle is not a SOFRS report or a SOFAUDIT artifact.",
            "BCH equality is relative to the frozen carrier, basis, quotient, order, and truncation scope.",
            "TRUNCATED_MATCH does not establish full BCH equality.",
            "The Heisenberg control does not establish a generic BCH convergence or matrix-logarithm theorem.",
            "Directory placement does not promote this control into Paper XIII evidence.",
        ],
    }
    bundle["content_sha256"] = _digest(bundle)
    return bundle


def validate_control_bundle(bundle: dict) -> None:
    if not isinstance(bundle, dict):
        raise SignatureValidationError("control bundle must be an object")
    unsigned = deepcopy(bundle)
    try:
        expected_digest = unsigned.pop("content_sha256")
    except KeyError as exc:
        raise SignatureValidationError("content_sha256 is required") from exc
    if _digest(unsigned) != expected_digest:
        raise SignatureValidationError("control bundle digest mismatch")
    if bundle.get("schema") != BUNDLE_SCHEMA:
        raise SignatureValidationError("unsupported control bundle schema")
    expected_implementation = {
        "implementation_id": IMPLEMENTATION_ID,
        "implementation_sha256": implementation_sha256(),
        "language": "Python",
        "arithmetic": "fractions.Fraction",
    }
    if bundle.get("implementation") != expected_implementation:
        raise SignatureValidationError("control bundle implementation closure mismatch")
    if bundle.get("carrier_definition") != carrier_definition():
        raise SignatureValidationError("control bundle carrier definition mismatch")
    expected_alignments = {"identity": identity_generator_alignment()}
    if bundle.get("generator_alignments") != expected_alignments:
        raise SignatureValidationError("control bundle generator alignment mismatch")
    validate_generator_alignment(bundle["generator_alignments"]["identity"])
    for signature in bundle.get("signatures", {}).values():
        validate_and_replay_signature(signature)
    if _canonical(bundle) != _canonical(build_control_bundle()):
        raise SignatureValidationError("control bundle replay mismatch")


def write_markdown(bundle: dict, path: Path) -> None:
    mismatch = bundle["comparisons"]["XY_vs_YX"]
    bounded = bundle["comparisons"]["degree_one_bounded_match"]
    full = bundle["comparisons"]["degree_one_full_bch"]
    lines = [
        "# BCH Composition Control Bundle",
        "",
        "- Artifact role: `EXPLORATORY_CONTROL_BUNDLE`",
        "- Claim status: `Computational Certificate`",
        "- Paper evidence: `NOT_PROMOTED`",
        f"- Implementation: `{IMPLEMENTATION_ID}`",
        f"- Implementation SHA-256: `{implementation_sha256()}`",
        "- Carrier: `heisenberg3.class2.rational.v1`",
        "",
        "## Exact Ordered Control",
        "",
        "- `BCH(X,Y) = X + Y + 1/2 Z`",
        "- `BCH(Y,X) = X + Y - 1/2 Z`",
        f"- BCH status: `{mismatch['bch_status']}`",
        f"- Lowest differing degree: `{mismatch['lowest_differing_degree']}`",
        f"- SOFAUDIT candidate projection: `{mismatch['sofaudit_projection']['comparison_state']}`",
        "",
        "## Truncation Boundary",
        "",
        f"- Degree-one bounded comparison: `{bounded['bch_status']}`",
        f"- Degree-one full-BCH comparison: `{full['bch_status']}`",
        "- A bounded match does not establish full BCH equality.",
        "",
        "## Known Nonclaims",
        "",
        *[f"- {item}" for item in bundle["negative_boundaries"]],
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()
    bundle = build_control_bundle()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        write_markdown(bundle, args.markdown)
    print(
        json.dumps(
            {
                "bundle_id": bundle["bundle_id"],
                "content_sha256": bundle["content_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
