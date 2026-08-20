"""Canonical minimal AB/BC/AC counterexample for finite signature descent."""

from __future__ import annotations

from dataclasses import dataclass

from context_objects import ObservationContext, SignatureCoordinate
from finite_descent import (
    CandidateSpaceStatus,
    DescentState,
    DescentBasis,
    FiniteCover,
    MatchingFamily,
    classify_finite_descent,
    make_descent_basis,
    matching_global_candidates,
    state_for_match_count,
)
from presheaf_signatures import SignatureSection, restrict
from typed_morphisms import RestrictionMorphism


CONVENTIONS = (("support", "exact-boolean"),)


def _context(context_id: str, sectors: tuple[str, ...]) -> ObservationContext:
    return ObservationContext(
        context_id=context_id,
        sectors=sectors,
        observables=("route",),
        carrier="word",
        conventions=CONVENTIONS,
    )


def _arrow(local: ObservationContext, ambient: ObservationContext) -> RestrictionMorphism:
    return RestrictionMorphism(
        morphism_id=f"{local.context_id}.to.{ambient.context_id}",
        local=local,
        ambient=ambient,
        sector_map=tuple((label, label) for label in local.sectors),
        observable_map=(("route", "route"),),
    )


def _coordinate(source: str, target: str) -> SignatureCoordinate:
    return SignatureCoordinate("word.support.v1", "word", source, target, "route")


def _section(context: ObservationContext, values: dict[tuple[str, str], int]) -> SignatureSection:
    return SignatureSection.from_mapping(
        context,
        {
            _coordinate(source, target): value
            for (source, target), value in values.items()
        },
    )


@dataclass(frozen=True)
class CanonicalMinimalExample:
    global_context: ObservationContext
    ab_context: ObservationContext
    bc_context: ObservationContext
    ac_context: ObservationContext
    cover_ab_bc: FiniteCover
    cover_ab_bc_ac: FiniteCover
    candidate_0: SignatureSection
    candidate_1: SignatureSection
    candidate_space: tuple[SignatureSection, ...]
    bounded_basis: DescentBasis
    required_interactions: tuple[SignatureCoordinate, ...]


def build_example() -> CanonicalMinimalExample:
    global_context = _context("minimal.global", ("A", "B", "C"))
    ab_context = _context("minimal.ab", ("A", "B"))
    bc_context = _context("minimal.bc", ("B", "C"))
    ac_context = _context("minimal.ac", ("A", "C"))
    ab_arrow = _arrow(ab_context, global_context)
    bc_arrow = _arrow(bc_context, global_context)
    ac_arrow = _arrow(ac_context, global_context)
    cover_ab_bc = FiniteCover("minimal.cover.ab-bc", global_context, (ab_arrow, bc_arrow))
    cover_ab_bc_ac = FiniteCover(
        "minimal.cover.ab-bc-ac", global_context, (ab_arrow, bc_arrow, ac_arrow)
    )
    candidate_0 = _section(
        global_context,
        {("A", "B"): 1, ("B", "C"): 1, ("A", "C"): 0},
    )
    candidate_1 = _section(
        global_context,
        {("A", "B"): 1, ("B", "C"): 1, ("A", "C"): 1},
    )
    candidate_space = (candidate_0, candidate_1)
    return CanonicalMinimalExample(
        global_context=global_context,
        ab_context=ab_context,
        bc_context=bc_context,
        ac_context=ac_context,
        cover_ab_bc=cover_ab_bc,
        cover_ab_bc_ac=cover_ab_bc_ac,
        candidate_0=candidate_0,
        candidate_1=candidate_1,
        candidate_space=candidate_space,
        bounded_basis=make_descent_basis(
            candidate_space_id="candidate-space.minimal-ab-bc-ac.v1",
            candidates=candidate_space,
            status=CandidateSpaceStatus.BOUNDED,
            enumerator_id="enumerator.literal-minimal.v1",
            validator_id="validator.contextual-descent.v1",
        ),
        required_interactions=(
            _coordinate("A", "B"),
            _coordinate("B", "C"),
            _coordinate("A", "C"),
        ),
    )


def run() -> None:
    example = build_example()
    local_ab = restrict(example.candidate_0, example.cover_ab_bc.arrows[0])
    local_bc = restrict(example.candidate_0, example.cover_ab_bc.arrows[1])
    local_ac = restrict(example.candidate_0, example.cover_ab_bc_ac.arrows[2])

    assert example.cover_ab_bc.covers_sector_labels
    assert not example.cover_ab_bc.covers_coordinates(example.required_interactions)
    assert example.cover_ab_bc_ac.covers_coordinates(example.required_interactions)

    nonunique = classify_finite_descent(
        MatchingFamily(example.cover_ab_bc, (local_ab, local_bc)),
        example.candidate_space,
        example.bounded_basis,
    )
    unique = classify_finite_descent(
        MatchingFamily(example.cover_ab_bc_ac, (local_ab, local_bc, local_ac)),
        example.candidate_space,
        example.bounded_basis,
    )
    assert nonunique.state == DescentState.GLUED_NONUNIQUE
    assert unique.state == DescentState.GLUED_UNIQUE
    assert nonunique.separatedness_failure_witness
    matches_two = matching_global_candidates(
        MatchingFamily(example.cover_ab_bc, (local_ab, local_bc)),
        example.candidate_space,
    )
    matches_one = matching_global_candidates(
        MatchingFamily(example.cover_ab_bc_ac, (local_ab, local_bc, local_ac)),
        example.candidate_space,
    )
    assert len(matches_two) == 2
    assert len(matches_one) == 1
    assert state_for_match_count(len(matches_two)) == nonunique.state
    assert state_for_match_count(len(matches_one)) == unique.state
    assert state_for_match_count(0) == DescentState.NO_GLOBAL_SECTION

    print("Canonical minimal AB/BC/AC descent example")
    print("  AB/BC covers sector labels:            PASS")
    print("  AB/BC covers AB, BC, AC interactions: FAIL")
    print("  AB/BC classifier:                       GLUED_NONUNIQUE")
    print("  |G_match(AB/BC)|:                       2")
    print("  AB/BC/AC interaction coverage:         PASS")
    print("  AB/BC/AC classifier:                    GLUED_UNIQUE")
    print("  |G_match(AB/BC/AC)|:                    1")
    print("  finite classifier cardinality theorem: PASS")
    print("  interpretation: finite-candidate separatedness control")


if __name__ == "__main__":
    run()
