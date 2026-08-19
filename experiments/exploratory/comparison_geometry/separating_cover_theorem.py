"""Finite criteria and sharp witnesses for typed-context separation/descent.

This executable accompanies the finite theorem controls in this exploratory
package. It is not a Paper XIII artifact and does not replace the digest-bound
candidate classifier.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Iterable, Sequence

from canonical_minimal_example import build_example
from context_objects import ObservationContext, SignatureCoordinate
from finite_descent import FiniteCover
from presheaf_signatures import SignatureSection, embed_coordinate, restrict
from typed_morphisms import RestrictionMorphism


MISSING = object()


def retained_coordinates(
    arrow: RestrictionMorphism,
    ambient_coordinates: Iterable[SignatureCoordinate],
) -> frozenset[SignatureCoordinate]:
    """Return the declared ambient coordinates visible through one patch."""

    sectors = set(arrow.sectors.values())
    observables = set(arrow.observables.values())
    parameters = set(arrow.parameters.values())
    retained = set()
    for coordinate in ambient_coordinates:
        coordinate.validate_for(arrow.ambient)
        if (
            coordinate.source_sector in sectors
            and coordinate.target_sector in sectors
            and coordinate.observable in observables
            and (coordinate.parameter is None or coordinate.parameter in parameters)
        ):
            retained.add(coordinate)
    return frozenset(retained)


def observed_coordinates(
    cover: FiniteCover,
    ambient_coordinates: Iterable[SignatureCoordinate],
) -> frozenset[SignatureCoordinate]:
    coordinates = tuple(ambient_coordinates)
    return frozenset().union(
        *(retained_coordinates(arrow, coordinates) for arrow in cover.arrows)
    )


def difference_support(
    left: SignatureSection,
    right: SignatureSection,
    ambient_coordinates: Iterable[SignatureCoordinate],
) -> frozenset[SignatureCoordinate]:
    """Include both payload differences and defined/undefined differences."""

    if left.context != right.context:
        raise ValueError("difference support requires one ambient context")
    coordinates = tuple(ambient_coordinates)
    left_values = left.value_map
    right_values = right.value_map
    return frozenset(
        coordinate
        for coordinate in coordinates
        if left_values.get(coordinate, MISSING)
        != right_values.get(coordinate, MISSING)
    )


def separating_on(
    cover: FiniteCover,
    ambient_coordinates: Sequence[SignatureCoordinate],
    sections: Sequence[SignatureSection],
) -> bool:
    """Apply the difference-support hitting characterization."""

    observed = observed_coordinates(cover, ambient_coordinates)
    return all(
        bool(difference_support(left, right, ambient_coordinates) & observed)
        for left, right in combinations(sections, 2)
        if left != right
    )


def exactly_matching(
    cover: FiniteCover,
    ambient_coordinates: Sequence[SignatureCoordinate],
    local_sections: Sequence[SignatureSection],
) -> bool:
    """Compare Option-level values, including local domains, on overlaps."""

    if len(local_sections) != len(cover.arrows):
        raise ValueError("one local section is required per cover arrow")
    embedded_values = []
    retained_sets = []
    for section, arrow in zip(local_sections, cover.arrows, strict=True):
        if section.context != arrow.local:
            raise ValueError("local section and cover arrow disagree")
        embedded_values.append(
            {embed_coordinate(coordinate, arrow): value for coordinate, value in section.values}
        )
        retained_sets.append(retained_coordinates(arrow, ambient_coordinates))
    for i, j in combinations(range(len(cover.arrows)), 2):
        for coordinate in retained_sets[i] & retained_sets[j]:
            if embedded_values[i].get(coordinate, MISSING) != embedded_values[j].get(
                coordinate, MISSING
            ):
                return False
    return True


@dataclass(frozen=True)
class FiniteConstraint:
    constraint_id: str
    scope: frozenset[SignatureCoordinate]
    predicate: Callable[[SignatureSection], bool]


def constraint_complete(
    cover: FiniteCover,
    ambient_coordinates: Sequence[SignatureCoordinate],
    constraints: Sequence[FiniteConstraint],
) -> bool:
    retained = tuple(
        retained_coordinates(arrow, ambient_coordinates) for arrow in cover.arrows
    )
    return all(any(constraint.scope <= patch for patch in retained) for constraint in constraints)


def local_constraint_package(
    constraints: Sequence[FiniteConstraint],
    domain: frozenset[SignatureCoordinate],
) -> tuple[FiniteConstraint, ...]:
    """Implement Q|_D by retaining exactly constraints scoped inside D."""

    return tuple(constraint for constraint in constraints if constraint.scope <= domain)


def admissible_on(
    section: SignatureSection,
    constraints: Sequence[FiniteConstraint],
) -> bool:
    """Check membership in the induced local admissible section space."""

    return all(constraint.predicate(section) for constraint in constraints)


def _context(context_id: str, sectors: tuple[str, ...]) -> ObservationContext:
    return ObservationContext(
        context_id=context_id,
        sectors=sectors,
        observables=("route",),
        carrier="word",
        conventions=(("support", "exact-boolean"),),
    )


def _arrow(local: ObservationContext, ambient: ObservationContext) -> RestrictionMorphism:
    return RestrictionMorphism(
        morphism_id=f"{local.context_id}.to.{ambient.context_id}",
        local=local,
        ambient=ambient,
        sector_map=tuple((label, label) for label in local.sectors),
        observable_map=(("route", "route"),),
    )


def _all_one_section(example) -> SignatureSection:
    return SignatureSection.from_mapping(
        example.global_context,
        {coordinate: True for coordinate in example.required_interactions},
    )


def run() -> None:
    example = build_example()
    coordinates = example.required_interactions

    assert not separating_on(
        example.cover_ab_bc,
        coordinates,
        example.candidate_space,
    )
    assert separating_on(
        example.cover_ab_bc_ac,
        coordinates,
        example.candidate_space,
    )
    assert observed_coordinates(example.cover_ab_bc_ac, coordinates) == frozenset(
        coordinates
    )

    all_one = _all_one_section(example)
    pair_locals = tuple(
        restrict(all_one, arrow) for arrow in example.cover_ab_bc_ac.arrows
    )
    assert exactly_matching(example.cover_ab_bc_ac, coordinates, pair_locals)

    coordinate_by_pair = {
        (coordinate.source_sector, coordinate.target_sector): coordinate
        for coordinate in coordinates
    }
    parity_scope = frozenset(coordinates)

    def even_parity(section: SignatureSection) -> bool:
        values = section.value_map
        bits = (
            bool(values[coordinate_by_pair[("A", "B")]]),
            bool(values[coordinate_by_pair[("B", "C")]]),
            bool(values[coordinate_by_pair[("A", "C")]]),
        )
        return sum(bits) % 2 == 0

    parity = FiniteConstraint("triangle.even-parity.v1", parity_scope, even_parity)
    pair_domains = tuple(
        retained_coordinates(arrow, coordinates)
        for arrow in example.cover_ab_bc_ac.arrows
    )
    pair_constraint_packages = tuple(
        local_constraint_package((parity,), domain) for domain in pair_domains
    )
    assert all(not package for package in pair_constraint_packages)
    assert all(
        admissible_on(section, package)
        for section, package in zip(
            pair_locals,
            pair_constraint_packages,
            strict=True,
        )
    )
    assert not constraint_complete(
        example.cover_ab_bc_ac,
        coordinates,
        (parity,),
    )
    assert not parity.predicate(all_one)

    full_context = _context("minimal.abc", ("A", "B", "C"))
    full_cover = FiniteCover(
        "minimal.cover.abc",
        example.global_context,
        (_arrow(full_context, example.global_context),),
    )
    assert constraint_complete(full_cover, coordinates, (parity,))
    full_domain = retained_coordinates(full_cover.arrows[0], coordinates)
    full_package = local_constraint_package((parity,), full_domain)
    assert full_package == (parity,)
    assert not admissible_on(all_one, full_package)

    print("Finite typed-context theorem controls passed")
    print("  AB/BC candidate-relative separatedness: FAIL (sharp witness)")
    print("  AB/BC/AC coordinate separatedness:      PASS")
    print("  AB/BC/AC exact overlap matching:         PASS")
    print("  ternary parity constraint completeness:  FAIL (expected)")
    print("  pairwise induced Q|_D packages:           EMPTY (expected)")
    print("  all-one free gluing parity admissibility: FAIL (expected)")
    print("  full-scope patch constraint completeness: PASS")


if __name__ == "__main__":
    run()
