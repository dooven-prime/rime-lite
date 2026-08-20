"""Executable controls for contextual comparison and finite descent."""

from __future__ import annotations

from dataclasses import replace

from aggregation_pushforward import UnsupportedPushforwardError, apply_pushforward
from common_context import AlignmentPair, build_common_context, compare_through_common_context
from context_objects import ObservationContext, SignatureCoordinate
from finite_descent import (
    CandidateSpaceStatus,
    DescentState,
    FiniteCover,
    LocalSectionFamily,
    MatchingFamily,
    candidate_space_digest,
    classify_finite_descent,
    make_descent_basis,
)
from presheaf_signatures import SignatureSection, embed_coordinate, restrict
from typed_morphisms import (
    ResolutionRefinement,
    RestrictionMorphism,
    compose,
    identity,
)


CONVENTIONS = (("support", "exact-boolean"), ("depth", "not-used"))


def context(context_id: str, sectors: tuple[str, ...], carrier: str = "word") -> ObservationContext:
    return ObservationContext(
        context_id=context_id,
        sectors=sectors,
        observables=("route",),
        carrier=carrier,
        conventions=CONVENTIONS,
    )


def arrow(local: ObservationContext, ambient: ObservationContext) -> RestrictionMorphism:
    return RestrictionMorphism(
        morphism_id=f"{local.context_id}.to.{ambient.context_id}",
        local=local,
        ambient=ambient,
        sector_map=tuple((label, label) for label in local.sectors),
        observable_map=(("route", "route"),),
    )


def coordinate(source: str, target: str) -> SignatureCoordinate:
    return SignatureCoordinate("word.support.v1", "word", source, target, "route")


def section(ctx: ObservationContext, values: dict[tuple[str, str], int]) -> SignatureSection:
    return SignatureSection.from_mapping(
        ctx, {coordinate(source, target): value for (source, target), value in values.items()}
    )


def run() -> None:
    global_context = context("global", ("A", "B", "C"))
    ab = context("local.ab", ("A", "B"))
    bc = context("local.bc", ("B", "C"))
    ac = context("local.ac", ("A", "C"))
    b = context("local.b", ("B",))
    ab_to_global = arrow(ab, global_context)
    bc_to_global = arrow(bc, global_context)
    ac_to_global = arrow(ac, global_context)
    b_to_ab = arrow(b, ab)
    cover_ab_bc = FiniteCover(
        "cover.ab-bc", global_context, (ab_to_global, bc_to_global)
    )
    cover_ab_bc_ac = FiniteCover(
        "cover.ab-bc-ac", global_context, (ab_to_global, bc_to_global, ac_to_global)
    )

    candidate_0 = section(
        global_context,
        {("A", "A"): 1, ("B", "B"): 1, ("C", "C"): 1,
         ("A", "B"): 0, ("B", "C"): 1, ("A", "C"): 0},
    )
    candidate_1 = section(
        global_context,
        {("A", "A"): 1, ("B", "B"): 1, ("C", "C"): 1,
         ("A", "B"): 0, ("B", "C"): 1, ("A", "C"): 1},
    )
    candidate_space = (candidate_0, candidate_1)
    bounded_basis = make_descent_basis(
        candidate_space_id="candidate-space.binary-ac.v1",
        candidates=candidate_space,
        status=CandidateSpaceStatus.BOUNDED,
        enumerator_id="enumerator.literal-pair.v1",
        validator_id="validator.contextual-descent.v1",
    )
    exhaustive_basis = make_descent_basis(
        candidate_space_id="candidate-space.binary-ac.exhaustive.v1",
        candidates=candidate_space,
        status=CandidateSpaceStatus.EXHAUSTIVE,
        enumerator_id="enumerator.binary-ac.v1",
        validator_id="validator.contextual-descent.v1",
        completeness_evidence_id="evidence.binary-ac-domain-enumeration.v1",
    )
    assert candidate_space_digest(candidate_space) == candidate_space_digest(
        tuple(reversed(candidate_space))
    )
    try:
        candidate_space_digest((candidate_0, candidate_0))
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate candidate sections were accepted")

    # Presheaf identity and composition.
    assert restrict(candidate_0, identity(global_context)) == candidate_0
    assert embed_coordinate(coordinate("A", "B"), ab_to_global) == coordinate("A", "B")
    direct_b = restrict(candidate_0, compose(b_to_ab, ab_to_global))
    staged_b = restrict(restrict(candidate_0, ab_to_global), b_to_ab)
    assert direct_b == staged_b

    # A naive sector cover misses A-C relation data, so gluing is nonunique.
    local_ab = restrict(candidate_0, ab_to_global)
    local_bc = restrict(candidate_0, bc_to_global)
    required_interactions = (coordinate("A", "B"), coordinate("B", "C"), coordinate("A", "C"))
    assert cover_ab_bc.covers_sector_labels
    assert not cover_ab_bc.covers_coordinates(required_interactions)
    assert cover_ab_bc_ac.covers_coordinates(required_interactions)
    nonunique = classify_finite_descent(
        MatchingFamily(cover_ab_bc, (local_ab, local_bc)),
        candidate_space,
        bounded_basis,
    )
    assert nonunique.state == DescentState.GLUED_NONUNIQUE
    assert nonunique.separatedness_failure_witness
    assert "separatedness-failure" in nonunique.reader_statement
    try:
        classify_finite_descent(
            MatchingFamily(cover_ab_bc, (local_ab, local_bc)),
            candidate_space,
            replace(bounded_basis, digest="0" * 64),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("candidate-space digest mismatch was accepted")

    # Adding the A-C context determines the finite candidate uniquely.
    unique = classify_finite_descent(
        MatchingFamily(
            cover_ab_bc_ac,
            (local_ab, local_bc, restrict(candidate_0, ac_to_global)),
        ),
        candidate_space,
        bounded_basis,
    )
    assert unique.state == DescentState.GLUED_UNIQUE
    assert "candidate space" in unique.reader_statement

    # Overlap disagreement is distinct from failure to find a global section.
    hostile_bc = SignatureSection.from_mapping(
        bc,
        {**local_bc.value_map, coordinate("B", "B"): 0},
    )
    incompatible = classify_finite_descent(
        LocalSectionFamily(cover_ab_bc, (local_ab, hostile_bc)),
        candidate_space,
        bounded_basis,
    )
    assert incompatible.state == DescentState.INCOMPATIBLE_OVERLAP

    no_global = classify_finite_descent(
        MatchingFamily(
            cover_ab_bc,
            (section(ab, {("A", "A"): 1, ("B", "B"): 1, ("A", "B"): 9}), local_bc),
        ),
        candidate_space,
        bounded_basis,
    )
    assert no_global.state == DescentState.NO_GLOBAL_SECTION
    assert no_global.candidate_space_status == CandidateSpaceStatus.BOUNDED
    assert "was found" in no_global.reader_statement

    no_global_exhaustive = classify_finite_descent(
        MatchingFamily(
            cover_ab_bc,
            (section(ab, {("A", "A"): 1, ("B", "B"): 1, ("A", "B"): 9}), local_bc),
        ),
        candidate_space,
        exhaustive_basis,
    )
    assert no_global_exhaustive.state == DescentState.NO_GLOBAL_SECTION
    assert no_global_exhaustive.candidate_space_status == CandidateSpaceStatus.EXHAUSTIVE
    assert "exists" in no_global_exhaustive.reader_statement

    unresolved = classify_finite_descent(
        MatchingFamily(cover_ab_bc, (local_ab, local_bc)), None
    )
    assert unresolved.state == DescentState.UNRESOLVED

    # Same-frame comparison factors through explicit common-context legs.
    right = context("right", ("x", "y", "z"))
    right_section = section(
        right,
        {("x", "x"): 1, ("y", "y"): 1, ("z", "z"): 1,
         ("x", "y"): 0, ("y", "z"): 1, ("x", "z"): 1},
    )
    span = build_common_context(
        "comparison.frame",
        global_context,
        right,
        (
            AlignmentPair("s0", "A", "x"),
            AlignmentPair("s1", "B", "y"),
            AlignmentPair("s2", "C", "z"),
        ),
        (AlignmentPair("o0", "route", "route"),),
    )
    relations = compare_through_common_context(candidate_0, right_section, span)
    assert list(relations.values()).count("MISMATCH") == 1

    analogue_right = ObservationContext(
        context_id="analogue.right",
        sectors=("x", "y", "z"),
        observables=("route",),
        carrier="word",
        realization_kind="diagnostic_analogue",
        conventions=CONVENTIONS,
    )
    try:
        build_common_context(
            "invalid.strict-analogue-restriction",
            global_context,
            analogue_right,
            (
                AlignmentPair("s0", "A", "x"),
                AlignmentPair("s1", "B", "y"),
                AlignmentPair("s2", "C", "z"),
            ),
            (AlignmentPair("o0", "route", "route"),),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("strict-vs-analogue was accepted as ordinary restriction")

    # Carrier and convention changes do not silently become restrictions.
    lie_context = context("lie", ("A", "B"), carrier="lie")
    try:
        arrow(lie_context, global_context)
    except ValueError:
        pass
    else:
        raise AssertionError("word/Lie cross-binding was accepted")

    changed_convention = ObservationContext(
        context_id="changed.convention",
        sectors=("A", "B"),
        observables=("route",),
        carrier="word",
        conventions=(("support", "thresholded"), ("depth", "not-used")),
    )
    try:
        arrow(changed_convention, global_context)
    except ValueError:
        pass
    else:
        raise AssertionError("incompatible convention was accepted")

    refinement = ResolutionRefinement(
        witness_id="split.A",
        fine_context_id="fine",
        coarse_context_id="global",
        fine_to_coarse=(("A1", "A"), ("A2", "A"), ("B", "B"), ("C", "C")),
    )
    try:
        apply_pushforward(candidate_0, refinement, None, None)
    except UnsupportedPushforwardError:
        pass
    else:
        raise AssertionError("aggregation without a law was accepted")

    print("Contextual comparison and descent controls")
    print("  restriction identity:                 PASS")
    print("  restriction composition:              PASS")
    print("  AB/BC sector-label cover:             PASS")
    print("  AB/BC interaction cover:              FAIL (A-C unobserved)")
    print("  AB/BC/AC interaction cover:           PASS")
    print(f"  naive sector-cover descent:           {nonunique.state.value}")
    print(f"  relation-cover descent:               {unique.state.value}")
    print(f"  hostile overlap:                      {incompatible.state.value}")
    print(f"  bounded absent extension:             {no_global.state.value}")
    print(f"  exhaustive absent extension:          {no_global_exhaustive.state.value}")
    print(f"  absent candidate space:               {unresolved.state.value}")
    print("  candidate-space digest closure:       PASS")
    print("  candidate-set order/uniqueness:       PASS")
    print("  common-context comparison:            1 MISMATCH")
    print("  strict/analogue restriction span:     REJECTED (alignment remains external)")
    print("  word/Lie cross-binding:               REJECTED")
    print("  convention change:                    REJECTED")
    print("  uncontracted aggregation:             UNSUPPORTED_PUSHFORWARD")
    print("Claim boundary: finite controls for candidate presheaf/descent objects;")
    print("no topology, sheaf theorem, or topos-level result is claimed.")


if __name__ == "__main__":
    run()
