"""Finite candidate-space descent controls for typed signature sections."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from context_objects import ObservationContext, SignatureCoordinate
from presheaf_signatures import SignatureSection, embed_coordinate, restrict
from typed_morphisms import RestrictionMorphism


class DescentState(str, Enum):
    GLUED_UNIQUE = "GLUED_UNIQUE"
    GLUED_NONUNIQUE = "GLUED_NONUNIQUE"
    NO_GLOBAL_SECTION = "NO_GLOBAL_SECTION"
    INCOMPATIBLE_OVERLAP = "INCOMPATIBLE_OVERLAP"
    NO_MORPHISM = "NO_MORPHISM"
    UNSUPPORTED_PUSHFORWARD = "UNSUPPORTED_PUSHFORWARD"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class FiniteCover:
    """A declared finite family of canonical restrictions into one context."""

    cover_id: str
    ambient: ObservationContext
    arrows: tuple[RestrictionMorphism, ...]

    def __post_init__(self) -> None:
        if not self.cover_id:
            raise ValueError("cover_id must be nonempty")
        if not self.arrows:
            raise ValueError("a finite cover requires at least one arrow")
        if any(arrow.ambient != self.ambient for arrow in self.arrows):
            raise ValueError("every cover arrow must have the declared ambient context")
        ids = tuple(arrow.morphism_id for arrow in self.arrows)
        if len(ids) != len(set(ids)):
            raise ValueError("cover morphism IDs must be unique")

    @property
    def covers_sector_labels(self) -> bool:
        retained = {target for arrow in self.arrows for _, target in arrow.sector_map}
        return retained == set(self.ambient.sectors)

    @property
    def covers_observable_labels(self) -> bool:
        retained = {target for arrow in self.arrows for _, target in arrow.observable_map}
        return retained == set(self.ambient.observables)

    @property
    def covers_parameter_labels(self) -> bool:
        retained = {target for arrow in self.arrows for _, target in arrow.parameter_map}
        return retained == set(self.ambient.parameters)

    def covers_coordinates(self, coordinates: Sequence[SignatureCoordinate]) -> bool:
        """Return whether every required relation coordinate is retained somewhere."""

        for coordinate in coordinates:
            coordinate.validate_for(self.ambient)
            retained = False
            for arrow in self.arrows:
                sectors = set(arrow.sectors.values())
                observables = set(arrow.observables.values())
                parameters = set(arrow.parameters.values())
                retained = (
                    coordinate.source_sector in sectors
                    and coordinate.target_sector in sectors
                    and coordinate.observable in observables
                    and (coordinate.parameter is None or coordinate.parameter in parameters)
                )
                if retained:
                    break
            if not retained:
                return False
        return True


@dataclass(frozen=True)
class LocalSectionFamily:
    """One local section per arrow, before overlap compatibility is imposed."""

    cover: FiniteCover
    local_sections: tuple[SignatureSection, ...]

    def __post_init__(self) -> None:
        if len(self.local_sections) != len(self.cover.arrows):
            raise ValueError("a matching family requires one section per cover arrow")
        for section, arrow in zip(self.local_sections, self.cover.arrows, strict=True):
            if section.context != arrow.local:
                raise ValueError("local section and cover arrow disagree")

    @property
    def is_overlap_compatible(self) -> bool:
        return _overlaps_are_compatible(self.local_sections, self.cover.arrows)


@dataclass(frozen=True)
class MatchingFamily(LocalSectionFamily):
    """An overlap-compatible local section family."""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.is_overlap_compatible:
            raise ValueError("a MatchingFamily must agree on every retained overlap coordinate")


class CandidateSpaceStatus(str, Enum):
    EXHAUSTIVE = "exhaustive"
    BOUNDED = "bounded"
    UNSPECIFIED = "unspecified"


@dataclass(frozen=True)
class DescentBasis:
    """Source address for the finite global candidate search."""

    candidate_space_id: str
    candidate_space_status: CandidateSpaceStatus
    enumerator_id: str
    validator_id: str
    digest: str
    completeness_evidence_id: str | None = None

    def __post_init__(self) -> None:
        for field, value in (
            ("candidate_space_id", self.candidate_space_id),
            ("enumerator_id", self.enumerator_id),
            ("validator_id", self.validator_id),
        ):
            if not value:
                raise ValueError(f"{field} must be nonempty")
        if not re.fullmatch(r"[0-9a-f]{64}", self.digest):
            raise ValueError("candidate-space digest must be lowercase SHA-256")
        if (
            self.candidate_space_status == CandidateSpaceStatus.EXHAUSTIVE
            and not self.completeness_evidence_id
        ):
            raise ValueError("exhaustive candidate spaces require completeness evidence")


@dataclass(frozen=True)
class DescentResult:
    state: DescentState
    matching_global_sections: tuple[SignatureSection, ...] = ()
    detail: str = ""
    basis: DescentBasis | None = None
    search_scope: str = "candidate_space"

    @property
    def candidate_space_status(self) -> CandidateSpaceStatus:
        if self.basis is None:
            return CandidateSpaceStatus.UNSPECIFIED
        return self.basis.candidate_space_status

    @property
    def separatedness_failure_witness(self) -> bool:
        return self.state == DescentState.GLUED_NONUNIQUE

    @property
    def reader_statement(self) -> str:
        status = self.candidate_space_status
        if self.state == DescentState.NO_GLOBAL_SECTION:
            if status == CandidateSpaceStatus.EXHAUSTIVE:
                return "No global section exists in the declared evidence-bound exhaustive space."
            return "No global section was found in the declared candidate space."
        if self.state == DescentState.GLUED_UNIQUE:
            if status == CandidateSpaceStatus.EXHAUSTIVE:
                return "A unique global section exists in the declared evidence-bound exhaustive space."
            return "A unique matching global candidate was found in the declared candidate space."
        if self.state == DescentState.GLUED_NONUNIQUE:
            return (
                "Distinct global candidates have identical restrictions; this is a finite-candidate "
                "separatedness-failure witness for the declared cover."
            )
        if self.state == DescentState.UNRESOLVED:
            return "No candidate space was supplied, so global extension remains unresolved."
        return self.detail or self.state.value


def candidate_space_digest(candidates: Sequence[SignatureSection]) -> str:
    """Return an order-independent deterministic digest of a finite candidate set."""

    if len(candidates) != len(set(candidates)):
        raise ValueError("candidate spaces must not contain duplicate sections")
    serialized_sections: list[str] = []
    for section in candidates:
        payload = {
            "context": {
                "context_id": section.context.context_id,
                "sectors": section.context.sectors,
                "observables": section.context.observables,
                "parameters": section.context.parameters,
                "carrier": section.context.carrier,
                "realization_kind": section.context.realization_kind,
                "conventions": section.context.conventions,
            },
            "values": [
                {
                    "family": coordinate.family,
                    "carrier": coordinate.carrier,
                    "source_sector": coordinate.source_sector,
                    "target_sector": coordinate.target_sector,
                    "observable": coordinate.observable,
                    "parameter": coordinate.parameter,
                    "value": value,
                }
                for coordinate, value in section.values
            ],
        }
        serialized_sections.append(
            json.dumps(payload, sort_keys=True, separators=(",", ":"))
        )
    encoded = ("[" + ",".join(sorted(serialized_sections)) + "]").encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def make_descent_basis(
    candidate_space_id: str,
    candidates: Sequence[SignatureSection],
    status: CandidateSpaceStatus,
    enumerator_id: str,
    validator_id: str,
    completeness_evidence_id: str | None = None,
) -> DescentBasis:
    return DescentBasis(
        candidate_space_id=candidate_space_id,
        candidate_space_status=status,
        enumerator_id=enumerator_id,
        validator_id=validator_id,
        digest=candidate_space_digest(candidates),
        completeness_evidence_id=completeness_evidence_id,
    )


def _overlaps_are_compatible(
    local_sections: Sequence[SignatureSection],
    cover_arrows: Sequence[RestrictionMorphism],
) -> bool:
    observed: dict[SignatureCoordinate, object] = {}
    for section, arrow in zip(local_sections, cover_arrows, strict=True):
        if section.context != arrow.local:
            raise ValueError("local section and cover arrow disagree")
        for coordinate, value in section.values:
            ambient_coordinate = embed_coordinate(coordinate, arrow)
            if ambient_coordinate in observed and observed[ambient_coordinate] != value:
                return False
            observed[ambient_coordinate] = value
    return True


def matching_global_candidates(
    matching_family: LocalSectionFamily,
    candidate_global_sections: Sequence[SignatureSection],
) -> tuple[SignatureSection, ...]:
    """Compute G_match exactly inside the declared finite candidate space."""

    if len(candidate_global_sections) != len(set(candidate_global_sections)):
        raise ValueError("candidate spaces must not contain duplicate sections")
    ambient = matching_family.cover.ambient
    matches: list[SignatureSection] = []
    for candidate in candidate_global_sections:
        if candidate.context != ambient:
            raise ValueError("global candidate belongs to a different context")
        if all(
            restrict(candidate, arrow) == local
            for local, arrow in zip(
                matching_family.local_sections, matching_family.cover.arrows, strict=True
            )
        ):
            matches.append(candidate)
    return tuple(matches)


def state_for_match_count(count: int) -> DescentState:
    """Return the classifier state for |G_match|."""

    if count < 0:
        raise ValueError("match count cannot be negative")
    if count == 0:
        return DescentState.NO_GLOBAL_SECTION
    if count == 1:
        return DescentState.GLUED_UNIQUE
    return DescentState.GLUED_NONUNIQUE


def classify_finite_descent(
    matching_family: LocalSectionFamily,
    candidate_global_sections: Sequence[SignatureSection] | None,
    basis: DescentBasis | None = None,
) -> DescentResult:
    """Classify gluing relative to a digest-bound finite global candidate set."""

    if not matching_family.is_overlap_compatible:
        return DescentResult(
            DescentState.INCOMPATIBLE_OVERLAP,
            detail="two local sections disagree on a retained overlap coordinate",
            basis=basis,
        )
    if candidate_global_sections is None:
        if basis is not None:
            raise ValueError("a descent basis cannot bind an absent candidate space")
        return DescentResult(
            DescentState.UNRESOLVED,
            detail="no finite global candidate space was supplied",
        )
    if basis is None:
        raise ValueError("a finite candidate search requires a DescentBasis")
    if basis.digest != candidate_space_digest(candidate_global_sections):
        raise ValueError("DescentBasis digest does not match the candidate space")

    matches = matching_global_candidates(matching_family, candidate_global_sections)
    state = state_for_match_count(len(matches))

    if state == DescentState.NO_GLOBAL_SECTION:
        detail = (
            "no extension exists in the declared evidence-bound exhaustive space"
            if basis.candidate_space_status == CandidateSpaceStatus.EXHAUSTIVE
            else "no extension was found in the declared candidate space"
        )
        return DescentResult(DescentState.NO_GLOBAL_SECTION, detail=detail, basis=basis)
    if state == DescentState.GLUED_UNIQUE:
        return DescentResult(
            DescentState.GLUED_UNIQUE,
            matches,
            detail="uniqueness is relative to the declared candidate space",
            basis=basis,
        )
    return DescentResult(
        DescentState.GLUED_NONUNIQUE,
        matches,
        detail=(
            "distinct global candidates have identical local restrictions; the declared cover "
            "fails the finite-candidate separatedness test"
        ),
        basis=basis,
    )
