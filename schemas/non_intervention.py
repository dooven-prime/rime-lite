"""Shared v2.1 non-intervention and artifact-role boundary helpers."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable


SOFRS_OBJECT_TRANSITION_BOUNDARY = {
    "artifact_role": "INFORMATIONAL_REPORT",
    "intervention_semantics": "NONE",
    "source_state_transition_authority": "NONE",
    "implementation_purity_status": "NOT_ESTABLISHED_BY_SOFRS",
}

SOFAUDIT_ATTRIBUTION_BOUNDARY = {
    "localization_scope": "ALIGNED_REPORT_COORDINATES",
    "interpretation_status": "DOWNSTREAM",
    "defect_attribution_status": "OUT_OF_SCOPE_FOR_SOFAUDIT",
    "causal_status": "OUT_OF_SCOPE_FOR_SOFAUDIT",
    "reference_role": "COMPARISON_ROLE_ONLY",
    "reference_causal_role": "NOT_A_CAUSAL_BASELINE",
}

SOFACTION_EXECUTION_BOUNDARY = {
    "artifact_role": "CANDIDATE_SET_ONLY",
    "selection_semantics": "OUT_OF_SCOPE_FOR_SOFACTION",
    "authorization_semantics": "OUT_OF_SCOPE_FOR_SOFACTION",
    "execution_semantics": "OUT_OF_SCOPE_FOR_SOFACTION",
    "outcome_semantics": "OUT_OF_SCOPE_FOR_SOFACTION",
    "effect_semantics": "OUT_OF_SCOPE_FOR_SOFACTION",
}

SOFRS_FORBIDDEN_KEYS = {
    "causes_transition",
    "executes_change",
    "object_transition",
    "source_transition",
    "source_state_transition",
    "intervention_result",
    "execution_receipt",
    "authorization_receipt",
    "causal_attribution",
}

SOFAUDIT_FORBIDDEN_KEYS = {
    "causal_attribution",
    "causal_mechanism",
    "caused_by",
    "defect_attribution",
    "control_group",
    "causal_baseline",
}

DOWNSTREAM_ARTIFACT_ROLES = {
    "selected-plan",
    "sofplan",
    "authorization-receipt",
    "sofauth",
    "execution-receipt",
    "sofexec",
    "executor-result",
    "post-action-observation",
    "outcome-record",
    "sofoutcome",
    "effect-certificate",
    "sofeffect",
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_reference(path: Path, root: Path) -> dict[str, Any]:
    return {
        "uri": path.resolve().relative_to(root.resolve()).as_posix(),
        "digest": {"algorithm": "sha256", "value": file_digest(path)},
    }


def closure_digest(ordered_artifacts: list[dict[str, Any]]) -> dict[str, str]:
    return {
        "algorithm": "sha256",
        "value": hashlib.sha256(canonical_json_bytes(ordered_artifacts)).hexdigest(),
    }


def resolve_reference(
    reference: dict[str, Any],
    *,
    root: Path,
    label: str,
) -> tuple[Path | None, list[str]]:
    errors: list[str] = []
    uri = reference.get("uri")
    if not isinstance(uri, str) or not uri:
        return None, [f"{label} has no artifact URI"]
    path = (root / uri).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return None, [f"{label} resolves outside the repository"]
    if not path.is_file():
        return None, [f"{label} does not exist: {uri}"]
    digest = reference.get("digest", {}).get("value")
    if digest != file_digest(path):
        errors.append(f"{label} digest does not match artifact")
    return path, errors


def iter_key_paths(value: Any, prefix: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}"
            yield path, key
            yield from iter_key_paths(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_key_paths(child, f"{prefix}[{index}]")


def forbidden_key_errors(
    value: Any,
    forbidden_keys: set[str],
    *,
    label: str,
) -> list[str]:
    return [
        f"{label} contains forbidden semantic field {path}"
        for path, key in iter_key_paths(value)
        if key in forbidden_keys
    ]


def normalize_role(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    for suffix in ("-json", "-artifact"):
        if normalized.endswith(suffix):
            normalized = normalized[: -len(suffix)]
    return normalized


def downstream_role_errors(value: Any, *, label: str) -> list[str]:
    errors: list[str] = []

    def visit(node: Any, path: str) -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                child_path = f"{path}.{key}"
                if key in {"role", "evidence_role", "artifact_type", "receipt_kind"} and isinstance(child, str):
                    normalized = normalize_role(child)
                    if normalized in DOWNSTREAM_ARTIFACT_ROLES:
                        errors.append(
                            f"{label} embeds downstream artifact role {child!r} at {child_path}"
                        )
                visit(child, child_path)
        elif isinstance(node, list):
            for index, child in enumerate(node):
                visit(child, f"{path}[{index}]")

    visit(value, "$")
    return errors


def exact_check_set_errors(
    checks: list[dict[str, Any]],
    required: set[str],
    *,
    label: str,
) -> list[str]:
    check_ids = [item.get("check_id") for item in checks]
    if len(check_ids) != len(set(check_ids)) or set(check_ids) != required:
        return [f"{label} check set is not exact"]
    return []


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
