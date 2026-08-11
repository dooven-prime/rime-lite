"""Single loader for Paper XIII coordinate registries and Audit Profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "schemas" / "sofaudit" / "coordinate-semantics-registry-v1.0.json"
STANDARD_PROFILE_PATH = ROOT / "schemas" / "sofaudit" / "paper13-standard-regime-a-profile-v2.0.json"
GRIDWORLD_PROFILE_PATH = ROOT / "schemas" / "sofaudit" / "paper13-gridworld-f4-native-profile-v2.0.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


REGISTRY = load(REGISTRY_PATH)
STANDARD_PROFILE = load(STANDARD_PROFILE_PATH)
GRIDWORLD_PROFILE = load(GRIDWORLD_PROFILE_PATH)
STANDARD_PROFILE_ID = STANDARD_PROFILE["profile_id"]
REQUIRED_PROFILE_SOURCE_ROLES = frozenset(
    {"audit-profile", "coordinate-semantics-registry"}
)


def value_schema_id(
    coordinate_family: str, registry: dict[str, Any] = REGISTRY
) -> str:
    """Resolve a coordinate value schema from the versioned registry input."""
    return registry["coordinates"][coordinate_family]["value_schema_id"]


def profile_errors(
    profile: dict[str, Any], registry: dict[str, Any] = REGISTRY
) -> list[str]:
    errors: list[str] = []
    if profile.get("coordinate_registry_ref") != "schemas/sofaudit/coordinate-semantics-registry-v1.0.json":
        errors.append("Audit Profile must bind the canonical coordinate semantics registry")
    if not set(profile.get("coordinate_families", [])) <= set(registry["coordinates"]):
        errors.append("Audit Profile references an unknown coordinate family")
    missing_source_roles = REQUIRED_PROFILE_SOURCE_ROLES - set(
        profile.get("required_evidence_roles", [])
    )
    if missing_source_roles:
        errors.append(
            "Audit Profile must require its source-addressed profile and registry artifacts"
        )
    if len(profile.get("requested_coordinate_ids", [])) != len(set(profile.get("requested_coordinate_ids", []))):
        errors.append("Audit Profile requested coordinate IDs must be unique")
    return errors
