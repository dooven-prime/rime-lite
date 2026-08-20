"""Typed observation contexts for contextual comparison controls.

This exploratory object is intentionally smaller than a full SOF report.  It
retains only labels on which canonical subset restriction is defined.  Sector
resolution refinement and aggregation are represented elsewhere and are not
ordinary arrows in this first context category.
"""

from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_CARRIERS = frozenset({"operator", "word", "lie", "observable", "record"})
SUPPORTED_REALIZATION_KINDS = frozenset({"strict_sof", "diagnostic_analogue"})


def _unique(labels: tuple[str, ...], field: str) -> None:
    if len(labels) != len(set(labels)):
        raise ValueError(f"{field} labels must be unique")
    if any(not label for label in labels):
        raise ValueError(f"{field} labels must be nonempty")


@dataclass(frozen=True)
class ObservationContext:
    """A finite retained context with fixed typing and conventions."""

    context_id: str
    sectors: tuple[str, ...]
    observables: tuple[str, ...]
    parameters: tuple[str, ...] = ()
    carrier: str = "operator"
    realization_kind: str = "strict_sof"
    conventions: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.context_id:
            raise ValueError("context_id must be nonempty")
        if self.carrier not in SUPPORTED_CARRIERS:
            raise ValueError(f"unsupported carrier: {self.carrier}")
        if self.realization_kind not in SUPPORTED_REALIZATION_KINDS:
            raise ValueError(f"unsupported realization kind: {self.realization_kind}")
        if not self.sectors:
            raise ValueError("at least one retained sector is required")
        if not self.observables:
            raise ValueError("at least one retained observable is required")
        _unique(self.sectors, "sector")
        _unique(self.observables, "observable")
        _unique(self.parameters, "parameter")
        keys = tuple(key for key, _ in self.conventions)
        _unique(keys, "convention")

    @property
    def convention_map(self) -> dict[str, str]:
        return dict(self.conventions)

    def same_restriction_component(self, other: "ObservationContext") -> bool:
        return (
            self.carrier == other.carrier
            and self.realization_kind == other.realization_kind
            and self.conventions == other.conventions
        )

    def same_typed_branch(self, other: "ObservationContext") -> bool:
        """Compatibility alias retained for the first prototype API."""

        return self.same_restriction_component(other)


@dataclass(frozen=True, order=True)
class SignatureCoordinate:
    """One carrier-qualified relation coordinate in an observation context."""

    family: str
    carrier: str
    source_sector: str
    target_sector: str
    observable: str
    parameter: str | None = None

    def validate_for(self, context: ObservationContext) -> None:
        if self.carrier != context.carrier:
            raise ValueError("coordinate carrier does not match its context")
        if self.source_sector not in context.sectors or self.target_sector not in context.sectors:
            raise ValueError("coordinate references a sector outside its context")
        if self.observable not in context.observables:
            raise ValueError("coordinate references an observable outside its context")
        if self.parameter is not None and self.parameter not in context.parameters:
            raise ValueError("coordinate references a parameter outside its context")
