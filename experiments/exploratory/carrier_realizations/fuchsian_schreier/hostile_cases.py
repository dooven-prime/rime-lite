#!/usr/bin/env python3
"""Hostile and type-separation controls for the v2 finite carrier."""

from __future__ import annotations

from copy import deepcopy

from core import (
    boolean_path_layers,
    content_digest,
    exact_word_layers,
    route_length_two_profile,
    support_matrix,
)
from modular_census import build_modular_census
from triangle_census import build_triangle_census, declared_symmetric_alphabet
from validate import BundleValidationError, validate_payload


def resign(payload: dict) -> dict:
    updated = deepcopy(payload)
    updated.pop("content_sha256", None)
    updated["content_sha256"] = content_digest(updated)
    return updated


def require_rejection(payload: dict, message: str) -> None:
    try:
        validate_payload(payload)
    except BundleValidationError:
        return
    raise AssertionError(message)


def run() -> None:
    # Aggregate graph powers can overestimate actual ordered word support on
    # nonsingleton sectors, even when every letter is a permutation.
    first = (0, 1, 3, 2)
    second = (1, 0, 3, 2)
    sectors = ((0, 1, 2), (3,))
    direct = support_matrix((first, second), sectors)
    path_two = boolean_path_layers(direct, 2)[1][
        "support_target_by_source"
    ]
    word_two = exact_word_layers((first, second), sectors, 2)[1][
        "support_target_by_source"
    ]
    assert path_two == [[1, 1], [1, 1]]
    assert word_two == [[1, 0], [0, 1]]

    routes = route_length_two_profile(
        (("a", first), ("b", second)), sectors
    )
    assert routes["zero_routed_product_count"] > 0

    modular = build_modular_census([5], 3)
    validate_payload(modular)
    assert modular["scope"]["numerical_spectrum"] == "NOT_INCLUDED"
    assert modular["records"][0]["carrier"]["lie_hall_carrier"] == (
        "NOT_DECLARED"
    )

    stale = deepcopy(modular)
    stale["records"][0]["finite_image_certificate"][
        "generated_transformation_count"
    ] = 999
    require_rejection(stale, "stale content digest was accepted")
    require_rejection(
        resign(stale), "coordinated result and digest tampering bypassed replay"
    )

    implementation_spoof = deepcopy(modular)
    implementation_spoof["implementation"]["producer_id"] = "spoofed"
    require_rejection(
        resign(implementation_spoof), "implementation spoof was accepted"
    )

    downstream_smuggle = deepcopy(modular)
    downstream_smuggle["records"][0]["sofrs"] = {"status": "PASS"}
    require_rejection(
        resign(downstream_smuggle), "downstream report field was accepted"
    )

    triangle = build_triangle_census([(2, 4, 5)], 2, 2)
    validate_payload(triangle)
    assert len(triangle["records"]) == 1
    assert triangle["records"][0]["order_retention"]["classification"] == (
        "PROPER_ORDER_DIVISOR_QUOTIENT"
    )

    # Equal represented maps with different source labels remain distinct.
    identity = (0, 1)
    labelled = declared_symmetric_alphabet(identity, identity)
    assert [name for name, _ in labelled] == ["x", "y"]

    promoted_order = deepcopy(triangle)
    promoted_order["records"][0]["order_retention"]["classification"] = (
        "FULL_SIGNATURE_ORDERS"
    )
    require_rejection(
        resign(promoted_order), "proper-order-divisor quotient was promoted"
    )

    print("Fuchsian-Schreier v2 hostile controls passed")


if __name__ == "__main__":
    run()
