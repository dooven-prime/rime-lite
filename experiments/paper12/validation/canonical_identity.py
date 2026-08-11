"""Minimal Paper XII semantic/artifact identity helpers.

The helper deliberately implements only the equality boundary already declared
by an Assembly Profile. It does not claim realization invariance or canonical
source/adapter selection.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def normative_report_core(
    report: dict[str, Any], assembly_profile: dict[str, Any]
) -> dict[str, Any]:
    """Return the report after quotienting declared non-normative view fields."""

    presentation_fields = set(assembly_profile.get("presentation_fields", []))
    return {
        key: deepcopy(value)
        for key, value in report.items()
        if key not in presentation_fields
    }


def semantic_report_equal(
    left: dict[str, Any],
    right: dict[str, Any],
    assembly_profile: dict[str, Any],
) -> bool:
    return canonical_json_bytes(normative_report_core(left, assembly_profile)) == canonical_json_bytes(
        normative_report_core(right, assembly_profile)
    )


def canonical_artifact_digest(report: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(report)).hexdigest()
