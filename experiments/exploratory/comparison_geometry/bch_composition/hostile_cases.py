#!/usr/bin/env python3
"""Hostile controls for the frozen BCH signature and projection boundary."""

from __future__ import annotations

from copy import deepcopy

from bch_signature import (
    IMPLEMENTATION_ID,
    SignatureValidationError,
    _digest,
    bch_signature,
    build_control_bundle,
    compare_signatures,
    identity_generator_alignment,
    validate_and_replay_signature,
    validate_control_bundle,
    validate_generator_alignment,
)


def resign(signature: dict) -> dict:
    updated = deepcopy(signature)
    updated.pop("signature_sha256", None)
    updated["signature_sha256"] = _digest(updated)
    return updated


def require_rejection(signature: dict, message: str) -> None:
    try:
        validate_and_replay_signature(signature)
    except SignatureValidationError:
        return
    raise AssertionError(message)


def run() -> None:
    xy = bch_signature([{"X": 1}, {"Y": 1}])
    yx = bch_signature([{"Y": 1}, {"X": 1}])
    alignment = identity_generator_alignment()

    # A stale digest cannot be interpreted as a scientific mismatch.
    stale = deepcopy(xy)
    stale["homogeneous_coefficients"]["2"]["Z"] = "999"
    require_rejection(stale, "stale signature digest was accepted")

    # Coordinated coefficient and digest tampering is rejected by replay.
    coefficient_tamper = deepcopy(xy)
    coefficient_tamper["homogeneous_coefficients"]["2"]["Z"] = "999"
    require_rejection(
        resign(coefficient_tamper),
        "coefficient and digest tampering bypassed signature replay",
    )

    # A carrier or quotient declaration cannot be changed while reusing the
    # registered Heisenberg implementation.
    carrier_spoof = deepcopy(xy)
    carrier_spoof["carrier_declaration"]["carrier_id"] = "abelian3.fake"
    require_rejection(resign(carrier_spoof), "carrier spoof was accepted")

    quotient_spoof = deepcopy(xy)
    quotient_spoof["carrier_declaration"]["quotient_relation_id"] = (
        "abelian3.zero-bracket.fake"
    )
    require_rejection(resign(quotient_spoof), "quotient spoof was accepted")

    # Generator alignment is a structured frozen bijection, not a free string.
    alignment_spoof = deepcopy(alignment)
    alignment_spoof["generator_map"][0]["target_generator_id"] = "generator.Y"
    alignment_spoof.pop("generator_alignment_sha256")
    alignment_spoof["generator_alignment_sha256"] = _digest(alignment_spoof)
    try:
        validate_generator_alignment(alignment_spoof)
    except SignatureValidationError:
        pass
    else:
        raise AssertionError("non-bijective generator alignment was accepted")

    # Reordering the source sequence while retaining XY coefficients fails
    # even after the attacker updates the digest.
    sequence_tamper = deepcopy(xy)
    sequence_tamper["sequence"] = [{"Y": "1"}, {"X": "1"}]
    require_rejection(
        resign(sequence_tamper), "sequence and coefficient inconsistency was accepted"
    )

    # Z is a derived Hall coordinate, not an admitted input generator.
    try:
        bch_signature([{"Z": 1}])
    except ValueError:
        pass
    else:
        raise AssertionError("derived Hall label Z was accepted as an input generator")

    # A missing alignment cannot hide a malformed registered signature.
    registered_tamper = deepcopy(xy)
    registered_tamper["homogeneous_coefficients"]["2"]["Z"] = "999"
    try:
        compare_signatures(resign(registered_tamper), xy)
    except SignatureValidationError:
        pass
    else:
        raise AssertionError("missing alignment bypassed registered signature replay")

    # Completion status is replay-derived and cannot be promoted manually.
    degree_one = bch_signature([{"X": 1}, {"Y": 1}], truncation_order=1)
    completion_tamper = deepcopy(degree_one)
    completion_tamper["completion_status"] = "EXACT_FINITE_BCH"
    require_rejection(
        resign(completion_tamper), "truncated signature was promoted to exact"
    )

    # A full-BCH request cannot turn a degree-one match into ALIGNED.
    bounded_copy = bch_signature([{"X": 1}, {"Y": 1}], truncation_order=1)
    full_result = compare_signatures(
        degree_one,
        bounded_copy,
        generator_alignment=alignment,
        comparison_scope="full_bch",
    )
    assert full_result["bch_status"] == "UNRESOLVED"
    assert full_result["sofaudit_projection"]["comparison_state"] == "UNRESOLVED"
    bounded_result = compare_signatures(
        degree_one,
        bounded_copy,
        generator_alignment=alignment,
        comparison_scope="through_degree",
    )
    assert bounded_result["bch_status"] == "TRUNCATED_MATCH"
    assert bounded_result["sofaudit_projection"]["comparison_state"] == "ALIGNED"
    assert bounded_result["sofaudit_projection"]["full_bch_comparison_state"] == (
        "UNRESOLVED"
    )

    # Exact order sensitivity remains the positive control.
    mismatch = compare_signatures(xy, yx, generator_alignment=alignment)
    assert mismatch["bch_status"] == "CERTIFIED_MISMATCH"
    assert mismatch["lowest_differing_degree"] == 2
    assert mismatch["basis_label"] == "Z"

    # Unknown implementations remain incomparable and cannot emit a factual
    # ALIGNED/MISMATCH state through this local evaluator.
    unknown = deepcopy(xy)
    unknown["carrier_declaration"]["implementation_id"] = "unknown.bch.v1"
    incomparable = compare_signatures(
        xy, unknown, generator_alignment=alignment
    )
    assert incomparable["bch_status"] == "INCOMPARABLE"
    assert incomparable["sofaudit_projection"]["comparison_state"] == (
        "INCOMPARABLE"
    )
    assert incomparable["implementation_ids"] == [
        IMPLEMENTATION_ID,
        "unknown.bch.v1",
    ]

    # Pairwise alignment is not inferred from equal carrier declarations.
    missing_alignment = compare_signatures(xy, xy)
    assert missing_alignment["bch_status"] == "INCOMPARABLE"
    assert "explicit registered generator alignment" in missing_alignment["reason"]

    # Bundle-level content, implementation, and replay closure all fail closed.
    bundle = build_control_bundle()
    bundle_tamper = deepcopy(bundle)
    bundle_tamper["implementation"]["implementation_sha256"] = "0" * 64
    bundle_tamper.pop("content_sha256")
    bundle_tamper["content_sha256"] = _digest(bundle_tamper)
    try:
        validate_control_bundle(bundle_tamper)
    except SignatureValidationError:
        pass
    else:
        raise AssertionError("coordinated bundle implementation tampering was accepted")

    print("BCH hostile controls passed")


if __name__ == "__main__":
    run()
