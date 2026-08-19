"""Boundary helpers for refinement and aggregation.

Aggregation is available only through an explicit family-specific law.  It is
not used as presheaf restriction and no generic law is supplied here.
"""

from __future__ import annotations

from collections.abc import Callable

from presheaf_signatures import SignatureSection
from typed_morphisms import AggregationPushforward, ResolutionRefinement


class UnsupportedPushforwardError(ValueError):
    pass


def apply_pushforward(
    section: SignatureSection,
    refinement: ResolutionRefinement,
    contract: AggregationPushforward | None,
    law: Callable[[SignatureSection, ResolutionRefinement], SignatureSection] | None,
) -> SignatureSection:
    if contract is None or law is None:
        raise UnsupportedPushforwardError(
            "resolution refinement has no canonical signature pushforward"
        )
    if contract.refinement_witness_id != refinement.witness_id:
        raise UnsupportedPushforwardError("pushforward contract binds another refinement")
    families = {coordinate.family for coordinate, _ in section.values}
    if not families <= set(contract.supported_families):
        raise UnsupportedPushforwardError("pushforward law does not cover every family")
    return law(section, refinement)
