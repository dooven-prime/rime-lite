"""Typed arrows for the first observation-context category.

Only canonical localization/restriction arrows are categorical morphisms.
Resolution refinements and aggregations are separate witness types because
coarse data does not canonically lift to a finer resolution.
"""

from __future__ import annotations

from dataclasses import dataclass

from context_objects import ObservationContext


def _validate_injective_map(
    mapping: tuple[tuple[str, str], ...],
    local_labels: tuple[str, ...],
    ambient_labels: tuple[str, ...],
    field: str,
) -> None:
    source = tuple(item[0] for item in mapping)
    target = tuple(item[1] for item in mapping)
    if set(source) != set(local_labels) or len(source) != len(local_labels):
        raise ValueError(f"{field} map must cover every local label exactly once")
    if len(target) != len(set(target)):
        raise ValueError(f"{field} map must be injective")
    if not set(target) <= set(ambient_labels):
        raise ValueError(f"{field} map targets labels outside the ambient context")


@dataclass(frozen=True)
class RestrictionMorphism:
    """A semantics-preserving local-to-ambient context arrow.

    This is the executable form of the Canonical Observation Restriction
    definition in FORMAL_NOTE.md. The first prototype uses exact convention
    preservation; a weaker convention restriction would require its own law.
    """

    morphism_id: str
    local: ObservationContext
    ambient: ObservationContext
    sector_map: tuple[tuple[str, str], ...]
    observable_map: tuple[tuple[str, str], ...]
    parameter_map: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.morphism_id:
            raise ValueError("morphism_id must be nonempty")
        if not self.local.same_restriction_component(self.ambient):
            raise ValueError(
                "restriction must preserve carrier, realization kind, and conventions"
            )
        _validate_injective_map(self.sector_map, self.local.sectors, self.ambient.sectors, "sector")
        _validate_injective_map(
            self.observable_map,
            self.local.observables,
            self.ambient.observables,
            "observable",
        )
        _validate_injective_map(
            self.parameter_map,
            self.local.parameters,
            self.ambient.parameters,
            "parameter",
        )

    @property
    def sectors(self) -> dict[str, str]:
        return dict(self.sector_map)

    @property
    def observables(self) -> dict[str, str]:
        return dict(self.observable_map)

    @property
    def parameters(self) -> dict[str, str]:
        return dict(self.parameter_map)


def identity(context: ObservationContext) -> RestrictionMorphism:
    return RestrictionMorphism(
        morphism_id=f"id.{context.context_id}",
        local=context,
        ambient=context,
        sector_map=tuple((label, label) for label in context.sectors),
        observable_map=tuple((label, label) for label in context.observables),
        parameter_map=tuple((label, label) for label in context.parameters),
    )


def compose(
    local_to_middle: RestrictionMorphism,
    middle_to_ambient: RestrictionMorphism,
    morphism_id: str | None = None,
) -> RestrictionMorphism:
    """Compose C0 -> C1 and C1 -> C2 into C0 -> C2."""

    if local_to_middle.ambient != middle_to_ambient.local:
        raise ValueError("restriction morphisms are not composable")

    def chained(
        first: tuple[tuple[str, str], ...], second: dict[str, str]
    ) -> tuple[tuple[str, str], ...]:
        return tuple((source, second[middle]) for source, middle in first)

    return RestrictionMorphism(
        morphism_id=morphism_id
        or f"{middle_to_ambient.morphism_id}.after.{local_to_middle.morphism_id}",
        local=local_to_middle.local,
        ambient=middle_to_ambient.ambient,
        sector_map=chained(local_to_middle.sector_map, middle_to_ambient.sectors),
        observable_map=chained(local_to_middle.observable_map, middle_to_ambient.observables),
        parameter_map=chained(local_to_middle.parameter_map, middle_to_ambient.parameters),
    )


@dataclass(frozen=True)
class ResolutionRefinement:
    """A fine-to-coarse sector witness, not a restriction morphism."""

    witness_id: str
    fine_context_id: str
    coarse_context_id: str
    fine_to_coarse: tuple[tuple[str, str], ...]
    source_artifact_id: str | None = None


@dataclass(frozen=True)
class AggregationPushforward:
    """An optional covariant law attached to a resolution refinement."""

    pushforward_id: str
    refinement_witness_id: str
    law_id: str
    supported_families: tuple[str, ...]
