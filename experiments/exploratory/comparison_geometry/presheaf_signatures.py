"""A finite carrier-preserving presheaf of typed structural signatures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from context_objects import ObservationContext, SignatureCoordinate
from typed_morphisms import RestrictionMorphism


ScalarValue = bool | int | float | str


@dataclass(frozen=True)
class SignatureSection:
    context: ObservationContext
    values: tuple[tuple[SignatureCoordinate, ScalarValue], ...]

    def __post_init__(self) -> None:
        coordinates = tuple(coordinate for coordinate, _ in self.values)
        if len(coordinates) != len(set(coordinates)):
            raise ValueError("section coordinates must be unique")
        for coordinate in coordinates:
            coordinate.validate_for(self.context)

    @classmethod
    def from_mapping(
        cls,
        context: ObservationContext,
        values: Mapping[SignatureCoordinate, ScalarValue],
    ) -> "SignatureSection":
        return cls(context=context, values=tuple(sorted(values.items())))

    @property
    def value_map(self) -> dict[SignatureCoordinate, ScalarValue]:
        return dict(self.values)


def embed_coordinate(
    coordinate: SignatureCoordinate, arrow: RestrictionMorphism
) -> SignatureCoordinate:
    """Apply the injective coordinate map u_#: K(local) -> K(ambient)."""

    coordinate.validate_for(arrow.local)
    sectors = arrow.sectors
    observables = arrow.observables
    parameters = arrow.parameters
    embedded = SignatureCoordinate(
        family=coordinate.family,
        carrier=coordinate.carrier,
        source_sector=sectors[coordinate.source_sector],
        target_sector=sectors[coordinate.target_sector],
        observable=observables[coordinate.observable],
        parameter=parameters[coordinate.parameter] if coordinate.parameter is not None else None,
    )
    embedded.validate_for(arrow.ambient)
    return embedded


def restrict(section: SignatureSection, arrow: RestrictionMorphism) -> SignatureSection:
    """Apply F(ambient) -> F(local) to one typed section."""

    if section.context != arrow.ambient:
        raise ValueError("section is not defined on the morphism's ambient context")

    sector_inverse = {ambient: local for local, ambient in arrow.sector_map}
    observable_inverse = {ambient: local for local, ambient in arrow.observable_map}
    parameter_inverse = {ambient: local for local, ambient in arrow.parameter_map}
    restricted: dict[SignatureCoordinate, ScalarValue] = {}

    for coordinate, value in section.values:
        if coordinate.source_sector not in sector_inverse:
            continue
        if coordinate.target_sector not in sector_inverse:
            continue
        if coordinate.observable not in observable_inverse:
            continue
        if coordinate.parameter is not None and coordinate.parameter not in parameter_inverse:
            continue
        local_coordinate = SignatureCoordinate(
            family=coordinate.family,
            carrier=coordinate.carrier,
            source_sector=sector_inverse[coordinate.source_sector],
            target_sector=sector_inverse[coordinate.target_sector],
            observable=observable_inverse[coordinate.observable],
            parameter=(
                parameter_inverse[coordinate.parameter]
                if coordinate.parameter is not None
                else None
            ),
        )
        restricted[local_coordinate] = value

    return SignatureSection.from_mapping(arrow.local, restricted)


def compare_same_context(
    reference: SignatureSection, target: SignatureSection
) -> dict[SignatureCoordinate, str]:
    """Compare sections only after both have entered one retained context."""

    if reference.context != target.context:
        raise ValueError("same-context comparison requires one shared context")
    if set(reference.value_map) != set(target.value_map):
        raise ValueError("same-context comparison requires equal coordinate domains")
    return {
        coordinate: "ALIGNED" if reference.value_map[coordinate] == target.value_map[coordinate]
        else "MISMATCH"
        for coordinate in reference.value_map
    }
