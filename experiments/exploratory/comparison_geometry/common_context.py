"""Explicit common retained contexts for same-frame comparison."""

from __future__ import annotations

from dataclasses import dataclass

from context_objects import ObservationContext
from presheaf_signatures import SignatureSection, compare_same_context, restrict
from typed_morphisms import RestrictionMorphism


@dataclass(frozen=True)
class AlignmentPair:
    common_id: str
    left_id: str
    right_id: str


@dataclass(frozen=True)
class CommonContextSpan:
    common: ObservationContext
    to_left: RestrictionMorphism
    to_right: RestrictionMorphism


def build_common_context(
    context_id: str,
    left: ObservationContext,
    right: ObservationContext,
    sector_pairs: tuple[AlignmentPair, ...],
    observable_pairs: tuple[AlignmentPair, ...],
    parameter_pairs: tuple[AlignmentPair, ...] = (),
) -> CommonContextSpan:
    """Build the same-realization canonical-restriction comparison span.

    This is only the same carrier, realization-kind, and convention-package
    subcase. Paper XIII strict-vs-analogue alignment is a broader explicit
    alignment contract and is not an ordinary presheaf restriction.
    """

    if not left.same_restriction_component(right):
        raise ValueError(
            "canonical common context requires the same carrier, realization kind, and "
            "conventions; broader Paper XIII alignment remains outside restriction"
        )
    common = ObservationContext(
        context_id=context_id,
        sectors=tuple(pair.common_id for pair in sector_pairs),
        observables=tuple(pair.common_id for pair in observable_pairs),
        parameters=tuple(pair.common_id for pair in parameter_pairs),
        carrier=left.carrier,
        realization_kind=left.realization_kind,
        conventions=left.conventions,
    )
    to_left = RestrictionMorphism(
        morphism_id=f"{context_id}.to.{left.context_id}",
        local=common,
        ambient=left,
        sector_map=tuple((pair.common_id, pair.left_id) for pair in sector_pairs),
        observable_map=tuple((pair.common_id, pair.left_id) for pair in observable_pairs),
        parameter_map=tuple((pair.common_id, pair.left_id) for pair in parameter_pairs),
    )
    to_right = RestrictionMorphism(
        morphism_id=f"{context_id}.to.{right.context_id}",
        local=common,
        ambient=right,
        sector_map=tuple((pair.common_id, pair.right_id) for pair in sector_pairs),
        observable_map=tuple((pair.common_id, pair.right_id) for pair in observable_pairs),
        parameter_map=tuple((pair.common_id, pair.right_id) for pair in parameter_pairs),
    )
    return CommonContextSpan(common=common, to_left=to_left, to_right=to_right)


def compare_through_common_context(
    left: SignatureSection,
    right: SignatureSection,
    span: CommonContextSpan,
) -> dict:
    left_restricted = restrict(left, span.to_left)
    right_restricted = restrict(right, span.to_right)
    return compare_same_context(left_restricted, right_restricted)
