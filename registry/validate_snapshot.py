"""Validate versioned SOF Registry snapshots and typed evidence contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCHEMAS = {
    "1.0": ROOT / "schemas" / "registry" / "v1.0.schema.json",
    "2.0": ROOT / "schemas" / "registry" / "v2.0.schema.json",
}
RULE_REGISTRY_PATH = ROOT / "schemas" / "sofcompiler" / "rule-registry-v1.0.json"
RULE_REGISTRY = json.loads(RULE_REGISTRY_PATH.read_text(encoding="utf-8"))
RULES = {rule["id"]: rule for rule in RULE_REGISTRY["rules"]}
VALIDATOR_VERSION = "registry-validator-v2.0"

DEFAULT_SNAPSHOTS = [
    HERE / "paper10-release-v1.0.registry.json",
    HERE / "paper10-typed-v2.0.registry.json",
]

# Resolve repository-only moves while preserving the immutable v1 payload.
RELOCATED_EVIDENCE_PATHS = {
    "experiments/paper5/path_commutator_cancellation.py": (
        "experiments/paper5/validation/path_commutator_cancellation.py"
    ),
    "experiments/paper7/incidence_variety_codim.py": (
        "experiments/paper7/validation/incidence_variety_codim.py"
    ),
    "experiments/paper7/markov_graph_sof.py": (
        "experiments/paper7/archive/markov_graph_sof.py"
    ),
    "experiments/paper9/state_mixing_fft.py": (
        "experiments/paper9/archive/state_mixing_fft.py"
    ),
}

CLAIM_STATUS_BY_RESULT_STATE = {
    "DECLARED": {"Research Program", None},
    "ESTABLISHED": {"Theorem"},
    "CERTIFIED": {"Computational Certificate"},
    "OBSERVED": {"Computational Observation"},
    "UNREACHED_AT_CUTOFF": {
        "Computational Certificate",
        "Computational Observation",
    },
    "NOT_APPLICABLE": {None},
    "NOT_DECLARED": {None},
}

CARRIER_CAPABILITY = {
    "sector": "sectorization",
    "operator": "operator_carrier",
    "operator_system": "operator_system",
    "route": "route_carrier",
    "word": "word_carrier",
    "positive_associative_closure": "positive_associative_closure",
    "observable_star_closure": "observable_star_closure",
    "sector_enriched_star_closure": "sector_enriched_star_closure",
    "lie": "lie_hall_carrier",
    "hall": "lie_hall_carrier",
    "deformation": "deformation_chart",
    "proxy": "proxy_diagnostic",
    "analogue": "diagnostic_analogue",
}

OBSERVATION_ARTIFACT_ROLES = {
    "source-input",
    "source-data",
    "script",
    "validator-output",
    "log",
}


def repository_path(value: str, *, relocate_v1: bool = False) -> Path:
    if relocate_v1:
        value = RELOCATED_EVIDENCE_PATHS.get(value, value)
    return ROOT / PurePosixPath(value)


def schema_errors(payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(payload),
        key=lambda error: [str(part) for part in error.path],
    )
    return [
        f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in errors
    ]


def duplicate_values(values: Iterable[Any]) -> list[Any]:
    values = list(values)
    return sorted({value for value in values if values.count(value) > 1})


def indexed(
    records: Iterable[dict[str, Any]], label: str
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    result: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for record in records:
        record_id = record.get("id")
        if record_id in result:
            errors.append(f"duplicate {label} ID: {record_id}")
        if record_id is not None:
            result[record_id] = record
    return result, errors


def reference_errors(
    entry_id: str,
    owner: str,
    field: str,
    values: Iterable[str],
    known: set[str],
) -> list[str]:
    return [
        f"{entry_id}: {owner}.{field} references unknown ID: {value}"
        for value in values
        if value not in known
    ]


def digest_matches(path: Path, digest: dict[str, str]) -> bool:
    hasher = hashlib.new(digest["algorithm"])
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest().lower() == digest["value"].lower()


def registry_content_digest(payload: dict[str, Any]) -> dict[str, str]:
    canonical = dict(payload)
    canonical.pop("census_certificate", None)
    encoded = json.dumps(
        canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {"algorithm": "sha256", "value": hashlib.sha256(encoded).hexdigest()}


def census_errors(
    payload: dict[str, Any], artifacts: dict[str, dict[str, Any]]
) -> list[str]:
    errors: list[str] = []
    census = payload["census_certificate"]
    entries = payload["entries"]
    findings = [finding for entry in entries for finding in entry["findings"]]
    summary = census["summary"]

    if census["snapshot_id"] != payload["snapshot"]["id"]:
        errors.append("census_certificate.snapshot_id does not match snapshot.id")
    if census["content_digest"] != registry_content_digest(payload):
        errors.append("census_certificate.content_digest does not match Registry content")
    if census["validator_version"] != VALIDATOR_VERSION:
        errors.append(
            "census_certificate.validator_version does not match active validator"
        )

    expected_summary = {
        "entry_count": len(entries),
        "strict_sof_count": sum(
            entry["record_kind"] == "strict_sof" for entry in entries
        ),
        "diagnostic_analogue_count": sum(
            entry["record_kind"] == "diagnostic_analogue" for entry in entries
        ),
        "capability_counts": {
            capability_id: sum(
                entry["capabilities"][capability_id]["availability"] == "DECLARED"
                for entry in entries
            )
            for capability_id in entries[0]["capabilities"]
        },
        "finding_count": len(findings),
        "finding_claim_status_counts": {
            status: sum(finding["claim_status"] == status for finding in findings)
            for status in (
                "Theorem",
                "Computational Certificate",
                "Computational Observation",
                "Research Program",
            )
        },
    }
    if summary != expected_summary:
        errors.append("census_certificate.summary does not match recomputed census")

    for artifact_id in census["artifact_ids"]:
        if artifact_id not in artifacts:
            errors.append(
                f"census_certificate references unknown artifact: {artifact_id}"
            )
    schema_artifact = artifacts.get(census["schema_artifact_id"])
    if schema_artifact is None:
        errors.append("census_certificate.schema_artifact_id is unknown")
    elif schema_artifact["uri"] != "schemas/registry/v2.0.schema.json":
        errors.append("census certificate does not reference Registry schema v2.0")
    validator_artifacts = [
        artifacts[artifact_id]
        for artifact_id in census["artifact_ids"]
        if artifact_id in artifacts
        and artifacts[artifact_id]["uri"] == "registry/validate_snapshot.py"
    ]
    if not validator_artifacts:
        errors.append("census certificate lacks the versioned validator artifact")
    return errors


def artifact_errors(artifacts: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    root = ROOT.resolve()
    for artifact_id, artifact in artifacts.items():
        producer_ids = artifact["generated_by_artifact_ids"]
        for producer_id in producer_ids:
            if producer_id not in artifacts:
                errors.append(
                    f"artifact {artifact_id}: unknown producer artifact {producer_id}"
                )
        if artifact["role"] == "source-data" and not producer_ids:
            errors.append(
                f"artifact {artifact_id}: source-data requires a producer artifact"
            )
        for producer_id in producer_ids:
            producer = artifacts.get(producer_id)
            if producer is not None and producer["role"] != "script":
                errors.append(
                    f"artifact {artifact_id}: producer {producer_id} is not a script"
                )
        expected_length = 64 if artifact["digest"]["algorithm"] == "sha256" else 128
        if len(artifact["digest"]["value"]) != expected_length:
            errors.append(
                f"artifact {artifact_id}: digest length does not match "
                f"{artifact['digest']['algorithm']}"
            )
        uri = artifact["uri"]
        if "://" in uri or uri.startswith("doi:"):
            continue
        path = repository_path(uri).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            errors.append(f"artifact {artifact_id}: path escapes repository root")
            continue
        if not path.is_file():
            errors.append(f"artifact {artifact_id}: path does not exist: {uri}")
            continue
        if not digest_matches(path, artifact["digest"]):
            errors.append(f"artifact {artifact_id}: digest mismatch: {uri}")
        if artifact["role"] == "source-data" and path.suffix.lower() == ".json":
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                errors.append(f"artifact {artifact_id}: source-data is not valid JSON")
                continue
            declared_schema = payload.get("schema")
            if declared_schema and artifact.get("schema_version") != declared_schema:
                errors.append(
                    f"artifact {artifact_id}: schema_version does not match payload schema"
                )
            script_digest = payload.get("runtime", {}).get("script_sha256")
            if script_digest and not any(
                artifacts[producer_id]["digest"]["algorithm"] == "sha256"
                and artifacts[producer_id]["digest"]["value"].lower()
                == script_digest.lower()
                for producer_id in producer_ids
                if producer_id in artifacts
            ):
                errors.append(
                    f"artifact {artifact_id}: runtime.script_sha256 does not match a producer"
                )

            declared_sources: list[tuple[str, str]] = []
            runtime_sources = payload.get("runtime", {}).get("source_sha256", {})
            declared_sources.extend(runtime_sources.items())
            declared_sources.extend(
                (item["path"], item["sha256"])
                for item in payload.get("source_scripts", [])
                if "path" in item and "sha256" in item
            )
            source_snapshot = payload.get("source_snapshot")
            if (
                isinstance(source_snapshot, dict)
                and "path" in source_snapshot
                and "sha256" in source_snapshot
            ):
                declared_sources.append(
                    (source_snapshot["path"], source_snapshot["sha256"])
                )
            for source_uri, expected_digest in declared_sources:
                source_path = repository_path(source_uri).resolve()
                try:
                    source_path.relative_to(root)
                except ValueError:
                    errors.append(
                        f"artifact {artifact_id}: declared source escapes "
                        f"repository root: {source_uri}"
                    )
                    continue
                if not source_path.is_file():
                    errors.append(
                        f"artifact {artifact_id}: declared source does not exist: "
                        f"{source_uri}"
                    )
                    continue
                actual_digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
                if actual_digest.lower() != expected_digest.lower():
                    errors.append(
                        f"artifact {artifact_id}: stale declared source digest: "
                        f"{source_uri}"
                    )
    return errors


def evidence_errors(
    owner: dict[str, Any],
    artifacts: dict[str, dict[str, Any]],
    certificates: dict[str, dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    owner_id = owner["id"]
    claim_status = owner["claim_status"]
    artifact_records = [
        artifacts[artifact_id]
        for artifact_id in owner["artifact_ids"]
        if artifact_id in artifacts
    ]
    certificate_records = [
        certificates[certificate_id]
        for certificate_id in owner["certificate_ids"]
        if certificate_id in certificates
    ]
    if claim_status == "Theorem":
        if not any(item["role"] == "proof-reference" for item in artifact_records):
            errors.append(f"{owner_id}: Theorem requires a proof-reference artifact")
    elif claim_status == "Computational Certificate":
        if not certificate_records or not all(
            item["status"] == "PASS" for item in certificate_records
        ):
            errors.append(
                f"{owner_id}: Computational Certificate requires PASS certificate evidence"
            )
        if not any(item["role"] == "source-data" for item in artifact_records):
            errors.append(
                f"{owner_id}: Computational Certificate requires a versioned "
                "source-data result artifact"
            )
    elif claim_status == "Computational Observation":
        if not any(
            item["role"] in OBSERVATION_ARTIFACT_ROLES for item in artifact_records
        ):
            errors.append(
                f"{owner_id}: Computational Observation requires a source artifact"
            )
    return errors


def v1_contract_errors(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entries = payload.get("entries", [])
    snapshot = payload.get("snapshot", {})
    for entry in entries:
        entry_id = entry.get("id", "<unknown>")
        metadata = entry.get("metadata", {})
        for field in ("evidence_scripts", "reports"):
            for value in metadata.get(field, []):
                if not repository_path(value, relocate_v1=True).is_file():
                    errors.append(f"{entry_id}: missing {field} path: {value}")

    if snapshot.get("id") == "paper10-release-v1.0":
        for entry in entries:
            entry_id = entry.get("id", "<unknown>")
            metadata = entry.get("metadata", {})
            later_paths = [
                path
                for path in metadata.get("evidence_scripts", [])
                if "experiments/paper11/" in path or "experiments/paper12/" in path
            ]
            if later_paths:
                errors.append(
                    f"{entry_id}: post-Paper-X evidence leaked into release snapshot: "
                    + ", ".join(later_paths)
                )
            if metadata.get("reports"):
                errors.append(
                    f"{entry_id}: Paper X release snapshot must not backfill later SOFRS reports"
                )
    return errors


def result_status_errors(owner: dict[str, Any]) -> list[str]:
    state = owner["result_state"]
    status = owner["claim_status"]
    if status in CLAIM_STATUS_BY_RESULT_STATE[state]:
        return []
    return [
        f"{owner['id']}: illegal result/claim status pair {state!r} + {status!r}"
    ]


def collect_entry_artifact_ids(entry: dict[str, Any]) -> set[str]:
    used = set(entry["artifact_ids"])
    strict_core = entry.get("strict_core")
    if strict_core:
        used.update(strict_core["sectorization"]["provenance_artifact_ids"])
        used.update(strict_core["operative_alphabet"]["provenance_artifact_ids"])
    analogue_core = entry.get("analogue_core")
    if analogue_core:
        used.update(analogue_core["source_provenance_artifact_ids"])
    for obj in entry["objects"]:
        used.update(obj["artifact_ids"])
    for certificate in entry["certificates"]:
        used.update(certificate["artifact_ids"])
    for finding in entry["findings"]:
        used.update(finding["artifact_ids"])
    for claim in entry["claims"]:
        used.update(claim["artifact_ids"])
    for derivation in entry["derivations"]:
        for condition in derivation["condition_checks"]:
            used.update(condition["artifact_ids"])
    for contract_ref in entry["contract_refs"].values():
        if contract_ref is not None:
            used.add(contract_ref["artifact_id"])
    return used


def entry_reference_errors(
    entry: dict[str, Any], artifacts: dict[str, dict[str, Any]]
) -> list[str]:
    errors: list[str] = []
    entry_id = entry["id"]
    collections: dict[str, dict[str, dict[str, Any]]] = {}
    for field in (
        "objects",
        "carriers",
        "observable_channels",
        "semantic_conventions",
        "run_policies",
        "certificates",
        "findings",
        "claims",
        "derivations",
    ):
        collections[field], duplicate_errors = indexed(entry[field], field)
        errors.extend(f"{entry_id}: {error}" for error in duplicate_errors)

    objects = collections["objects"]
    carriers = collections["carriers"]
    channels = collections["observable_channels"]
    conventions = collections["semantic_conventions"]
    policies = collections["run_policies"]
    certificates = collections["certificates"]
    findings = collections["findings"]
    claims = collections["claims"]

    object_ids = set(objects)
    carrier_ids = set(carriers)
    channel_ids = set(channels)
    convention_ids = set(conventions)
    policy_ids = set(policies)
    certificate_ids = set(certificates)
    finding_ids = set(findings)
    claim_ids = set(claims)
    artifact_ids = set(artifacts)

    errors.extend(
        reference_errors(
            entry_id, "entry", "artifact_ids", entry["artifact_ids"], artifact_ids
        )
    )
    for object_id, obj in objects.items():
        errors.extend(
            reference_errors(
                entry_id,
                f"object {object_id}",
                "artifact_ids",
                obj["artifact_ids"],
                artifact_ids,
            )
        )
        object_carrier_id = obj.get("carrier_id")
        if object_carrier_id is not None and object_carrier_id not in carrier_ids:
            errors.append(
                f"{entry_id}: object {object_id}.carrier_id references unknown ID: "
                f"{object_carrier_id}"
            )
        carrier_id = obj.get("carrier_id")
        if carrier_id is not None and carrier_id not in carrier_ids:
            errors.append(
                f"{entry_id}: object {object_id}.carrier_id references unknown ID: "
                f"{carrier_id}"
            )
    for carrier_id, carrier in carriers.items():
        errors.extend(
            reference_errors(
                entry_id,
                f"carrier {carrier_id}",
                "object_ids",
                carrier["object_ids"],
                object_ids,
            )
        )
        errors.extend(
            reference_errors(
                entry_id,
                f"carrier {carrier_id}",
                "semantic_convention_ids",
                carrier["semantic_convention_ids"],
                convention_ids,
            )
        )
    for channel_id, channel in channels.items():
        if channel["carrier_id"] not in carrier_ids:
            errors.append(
                f"{entry_id}: channel {channel_id}.carrier_id references unknown ID: "
                f"{channel['carrier_id']}"
            )
        errors.extend(
            reference_errors(
                entry_id,
                f"channel {channel_id}",
                "semantic_convention_ids",
                channel["semantic_convention_ids"],
                convention_ids,
            )
        )
        errors.extend(
            reference_errors(
                entry_id,
                f"channel {channel_id}",
                "run_policy_ids",
                channel["run_policy_ids"],
                policy_ids,
            )
        )
    for certificate_id, certificate in certificates.items():
        errors.extend(
            reference_errors(
                entry_id,
                f"certificate {certificate_id}",
                "artifact_ids",
                certificate["artifact_ids"],
                artifact_ids,
            )
        )
    for finding_id, finding in findings.items():
        for field, known in (
            ("channel_ids", channel_ids),
            ("carrier_ids", carrier_ids),
            ("subject_object_ids", object_ids),
            ("semantic_convention_ids", convention_ids),
            ("run_policy_ids", policy_ids),
            ("certificate_ids", certificate_ids),
            ("artifact_ids", artifact_ids),
        ):
            errors.extend(
                reference_errors(
                    entry_id, f"finding {finding_id}", field, finding[field], known
                )
            )
    for claim_id, claim in claims.items():
        for field, known in (
            ("carrier_ids", carrier_ids),
            ("object_ids", object_ids),
            ("finding_ids", finding_ids),
            ("semantic_convention_ids", convention_ids),
            ("run_policy_ids", policy_ids),
            ("certificate_ids", certificate_ids),
            ("artifact_ids", artifact_ids),
        ):
            errors.extend(
                reference_errors(
                    entry_id, f"claim {claim_id}", field, claim[field], known
                )
            )
    for derivation_id, derivation in collections["derivations"].items():
        errors.extend(
            reference_errors(
                entry_id,
                f"derivation {derivation_id}",
                "source_claim_ids",
                derivation["source_claim_ids"],
                claim_ids,
            )
        )
        if derivation["target_claim_id"] not in claim_ids:
            errors.append(
                f"{entry_id}: derivation {derivation_id}.target_claim_id references "
                f"unknown ID: {derivation['target_claim_id']}"
            )
        for condition in derivation["condition_checks"]:
            errors.extend(
                reference_errors(
                    entry_id,
                    f"derivation {derivation_id} condition {condition['condition_id']}",
                    "certificate_ids",
                    condition["certificate_ids"],
                    certificate_ids,
                )
            )
            errors.extend(
                reference_errors(
                    entry_id,
                    f"derivation {derivation_id} condition {condition['condition_id']}",
                    "artifact_ids",
                    condition["artifact_ids"],
                    artifact_ids,
                )
            )

    strict = entry.get("strict_core")
    if strict:
        errors.extend(
            reference_errors(
                entry_id,
                "strict_core.sectorization",
                "projector_object_ids",
                strict["sectorization"]["projector_object_ids"],
                object_ids,
            )
        )
        alphabet_id = strict["operative_alphabet"]["id"]
        if alphabet_id not in object_ids:
            errors.append(
                f"{entry_id}: operative alphabet references unknown object ID: {alphabet_id}"
            )
        elif objects[alphabet_id]["kind"] != "operative_alphabet":
            errors.append(
                f"{entry_id}: operative alphabet object {alphabet_id} is not operative_alphabet"
            )
        for projector_id in strict["sectorization"]["projector_object_ids"]:
            if projector_id in objects and objects[projector_id]["kind"] != "sector_projector":
                errors.append(
                    f"{entry_id}: projector object {projector_id} is not sector_projector"
                )
        for owner, values in (
            (
                "strict_core.sectorization",
                strict["sectorization"]["provenance_artifact_ids"],
            ),
            (
                "strict_core.operative_alphabet",
                strict["operative_alphabet"]["provenance_artifact_ids"],
            ),
        ):
            errors.extend(
                reference_errors(entry_id, owner, "artifact_ids", values, artifact_ids)
            )
    analogue = entry.get("analogue_core")
    if analogue:
        errors.extend(
            reference_errors(
                entry_id,
                "analogue_core",
                "source_provenance_artifact_ids",
                analogue["source_provenance_artifact_ids"],
                artifact_ids,
            )
        )

    dynamics = entry["dynamics"]
    for field in ("comparison_map_object_id", "trajectory_object_id"):
        value = dynamics[field]
        if value is not None and value not in object_ids:
            errors.append(f"{entry_id}: dynamics.{field} references unknown ID: {value}")
    errors.extend(
        reference_errors(
            entry_id,
            "dynamics",
            "semantic_convention_ids",
            dynamics["semantic_convention_ids"],
            convention_ids,
        )
    )
    errors.extend(
        reference_errors(
            entry_id,
            "dynamics",
            "run_policy_ids",
            dynamics["run_policy_ids"],
            policy_ids,
        )
    )
    return errors


def carrier_capability_errors(entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entry_id = entry["id"]
    capabilities = entry["capabilities"]
    if entry["record_kind"] == "diagnostic_analogue":
        strict_capabilities = set(capabilities) - {
            "diagnostic_analogue",
            "proxy_diagnostic",
        }
        leaked = sorted(
            capability_id
            for capability_id in strict_capabilities
            if capabilities[capability_id]["availability"] == "DECLARED"
        )
        if leaked:
            errors.append(
                f"{entry_id}: diagnostic analogue declares strict SOF capabilities: "
                + ", ".join(leaked)
            )
    carrier_capabilities: set[str] = set()
    for carrier in entry["carriers"]:
        expected = CARRIER_CAPABILITY[carrier["kind"]]
        declared = carrier["capability_id"]
        if declared != expected:
            errors.append(
                f"{entry_id}: carrier {carrier['id']} kind {carrier['kind']!r} "
                f"requires capability {expected!r}, not {declared!r}"
            )
        carrier_capabilities.add(declared)
        availability = capabilities[declared]["availability"]
        if availability != "DECLARED":
            errors.append(
                f"{entry_id}: carrier {carrier['id']} uses unavailable capability "
                f"{declared!r} ({availability})"
            )

    for capability_id, declaration in capabilities.items():
        if declaration["availability"] == "DECLARED" and capability_id not in carrier_capabilities:
            errors.append(
                f"{entry_id}: declared capability {capability_id!r} has no carrier"
            )
    return errors


def channel_errors(entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entry_id = entry["id"]
    carriers = {item["id"]: item for item in entry["carriers"]}
    policies = {item["id"]: item for item in entry["run_policies"]}
    expected_carrier_kinds = {
        "intrinsic": {"sector", "operator_system"},
        "operator": {"operator"},
        "route": {"route"},
        "word": {"word"},
        "positive_associative_closure": {"positive_associative_closure"},
        "observable_star_closure": {"observable_star_closure"},
        "sector_enriched_star_closure": {"sector_enriched_star_closure"},
        "lie": {"lie"},
        "hall": {"hall"},
        "proxy": {"proxy"},
        "analogue": {"analogue"},
    }
    expected_field_kinds = {
        "intrinsic": {"sector_data", "aggregate_support"},
        "operator": {"labelled_direct_support", "aggregate_support"},
        "route": {"routed_support", "depth"},
        "word": {"word_support", "depth"},
        "positive_associative_closure": {"closure_corner"},
        "observable_star_closure": {"closure_corner"},
        "sector_enriched_star_closure": {"closure_corner"},
        "lie": {"labelled_direct_support", "commutator_support", "depth"},
        "hall": {"commutator_support", "depth"},
        "proxy": {"continuous_proxy"},
        "analogue": {"analogue_descriptor"},
    }
    for channel in entry["observable_channels"]:
        channel_id = channel["id"]
        carrier = carriers.get(channel["carrier_id"])
        if carrier is not None and carrier["kind"] not in expected_carrier_kinds[channel["branch"]]:
            errors.append(
                f"{entry_id}: channel {channel_id} branch {channel['branch']!r} "
                f"cannot use carrier kind {carrier['kind']!r}"
            )
        if channel["field_kind"] not in expected_field_kinds[channel["branch"]]:
            errors.append(
                f"{entry_id}: channel {channel_id} branch {channel['branch']!r} "
                f"cannot use field kind {channel['field_kind']!r}"
            )
        policy_ids = set(channel["run_policy_ids"])
        if channel["depth_mode"] == "truncated":
            cutoff_policies = [
                policies[policy_id]
                for policy_id in policy_ids
                if policy_id in policies and policies[policy_id]["kind"] == "cutoff"
            ]
            if not cutoff_policies:
                errors.append(
                    f"{entry_id}: truncated channel {channel_id} lacks cutoff policy"
                )
            elif not any(
                policy["specification"].get("max_depth") == channel["depth_cutoff"]
                for policy in cutoff_policies
            ):
                errors.append(
                    f"{entry_id}: channel {channel_id} cutoff does not match its policy"
                )
        if channel["depth_mode"] == "exact" and not any(
            policy_id in policies and policies[policy_id]["kind"] == "saturation_audit"
            for policy_id in policy_ids
        ):
            errors.append(
                f"{entry_id}: exact channel {channel_id} lacks saturation-audit policy"
            )
    return errors


def finding_errors(entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entry_id = entry["id"]
    policies = {item["id"]: item for item in entry["run_policies"]}
    certificates = {item["id"]: item for item in entry["certificates"]}
    artifacts = entry["_artifact_index"]
    objects = {item["id"]: item for item in entry["objects"]}
    channels = {item["id"]: item for item in entry["observable_channels"]}

    policy_ids_by_kind: dict[str, set[str]] = {}
    for policy_id, policy in policies.items():
        policy_ids_by_kind.setdefault(policy["kind"], set()).add(policy_id)

    for finding in entry["findings"]:
        finding_id = finding["id"]
        errors.extend(f"{entry_id}: finding {error}" for error in result_status_errors(finding))
        used_policy_ids = set(finding["run_policy_ids"])
        used_certificate_ids = set(finding["certificate_ids"])
        state = finding["result_state"]
        depth = finding.get("depth_registration")

        if state in {"NOT_APPLICABLE", "NOT_DECLARED"}:
            if finding["channel_ids"] or finding["carrier_ids"] or finding["certificate_ids"]:
                errors.append(
                    f"{entry_id}: unavailable finding {finding_id} has channels/carriers/certificates"
                )
        finding_carriers = set(finding["carrier_ids"])
        finding_carrier_kinds = {
            entry_carrier["kind"]
            for entry_carrier in entry["carriers"]
            if entry_carrier["id"] in finding_carriers
        }
        if "proxy" in finding_carrier_kinds and len(finding_carrier_kinds) > 1:
            errors.append(
                f"{entry_id}: finding {finding_id} mixes proxy and strict carriers"
            )
        for channel_id in finding["channel_ids"]:
            if channel_id in channels and channels[channel_id]["carrier_id"] not in finding_carriers:
                errors.append(
                    f"{entry_id}: finding {finding_id} omits carrier "
                    f"{channels[channel_id]['carrier_id']!r} used by channel {channel_id}"
                )
        if state == "UNREACHED_AT_CUTOFF":
            if not depth or depth["mode"] != "truncated":
                errors.append(
                    f"{entry_id}: finding {finding_id} uses UNREACHED_AT_CUTOFF "
                    "without truncated depth semantics"
                )
            if not used_policy_ids.intersection(policy_ids_by_kind.get("cutoff", set())):
                errors.append(
                    f"{entry_id}: finding {finding_id} is cutoff-unreached without a cutoff policy"
                )
        if depth:
            if depth["mode"] == "truncated":
                cutoff_ids = used_policy_ids.intersection(
                    policy_ids_by_kind.get("cutoff", set())
                )
                if not cutoff_ids:
                    errors.append(
                        f"{entry_id}: truncated depth finding {finding_id} lacks cutoff policy"
                    )
                elif not any(
                    policies[policy_id]["specification"].get("max_depth")
                    == depth["cutoff"]
                    for policy_id in cutoff_ids
                ):
                    errors.append(
                        f"{entry_id}: finding {finding_id} cutoff does not match its policy"
                    )
            else:
                if state == "UNREACHED_AT_CUTOFF":
                    errors.append(
                        f"{entry_id}: exact depth finding {finding_id} cannot be cutoff-unreached"
                    )
                saturation_id = depth["saturation_certificate_id"]
                if saturation_id not in used_certificate_ids:
                    errors.append(
                        f"{entry_id}: exact depth finding {finding_id} does not reference "
                        "its saturation certificate"
                    )
                elif saturation_id not in certificates or certificates[saturation_id]["status"] != "PASS":
                    errors.append(
                        f"{entry_id}: exact depth finding {finding_id} lacks PASS saturation evidence"
                    )
                elif certificates[saturation_id]["kind"] != "saturation":
                    errors.append(
                        f"{entry_id}: exact depth finding {finding_id} references a "
                        "non-saturation certificate"
                    )
                if not used_policy_ids.intersection(
                    policy_ids_by_kind.get("saturation_audit", set())
                ):
                    errors.append(
                        f"{entry_id}: exact depth finding {finding_id} lacks saturation-audit policy"
                    )

        if finding["kind"] == "response_time":
            dynamics = entry["dynamics"]
            trajectory_id = dynamics["trajectory_object_id"]
            trajectory = objects.get(trajectory_id)
            if trajectory is None or trajectory["kind"] != "trajectory":
                errors.append(
                    f"{entry_id}: response-time finding {finding_id} lacks a declared trajectory"
                )
            else:
                if not trajectory.get("data", {}).get("selected_observable_ids"):
                    errors.append(
                        f"{entry_id}: trajectory {trajectory_id} lacks selected observables"
                    )
            required_policy_kinds = {
                "threshold",
                "norm",
                "trajectory_parameterization",
                "observable_normalization",
                "response_time",
            }
            present = {
                policies[policy_id]["kind"]
                for policy_id in used_policy_ids
                if policy_id in policies
            }
            missing = sorted(required_policy_kinds - present)
            if missing:
                errors.append(
                    f"{entry_id}: response-time finding {finding_id} lacks policies: "
                    + ", ".join(missing)
                )

        repair = finding.get("repair_registration")
        if repair:
            if finding["kind"] != "dimension" or not isinstance(finding["value"], int):
                errors.append(
                    f"{entry_id}: repair finding {finding_id} must be an integer dimension"
                )
            denominator = repair["count_denominator"]
            if denominator is not None and isinstance(finding["value"], int):
                if finding["value"] < 0 or finding["value"] > denominator:
                    errors.append(
                        f"{entry_id}: repair finding {finding_id} is outside its count denominator"
                    )
            if repair["repair_kind"] == "static_filtration_repair":
                if not finding_carrier_kinds.intersection({"lie", "hall", "word", "route"}):
                    errors.append(
                        f"{entry_id}: static filtration repair {finding_id} lacks a filtration carrier"
                    )
                cutoff_ids = used_policy_ids.intersection(
                    policy_ids_by_kind.get("cutoff", set())
                )
                if not cutoff_ids or not any(
                    policies[policy_id]["specification"].get("max_depth")
                    == repair["cutoff"]
                    for policy_id in cutoff_ids
                ):
                    errors.append(
                        f"{entry_id}: static filtration repair {finding_id} lacks its declared cutoff policy"
                    )
                if repair["saturation_status"] != "truncated_only":
                    errors.append(
                        f"{entry_id}: uncertified static repair {finding_id} must remain truncated_only"
                    )

        errors.extend(
            f"{entry_id}: finding {error}"
            for error in evidence_errors(finding, artifacts, certificates)
        )
    return errors


def claim_errors(entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entry_id = entry["id"]
    capabilities = entry["capabilities"]
    carriers = {item["id"]: item for item in entry["carriers"]}
    findings = {item["id"]: item for item in entry["findings"]}
    certificates = {item["id"]: item for item in entry["certificates"]}
    artifacts = entry["_artifact_index"]

    for claim in entry["claims"]:
        claim_id = claim["id"]
        errors.extend(f"{entry_id}: claim {error}" for error in result_status_errors(claim))
        state = claim["result_state"]
        for capability_id in claim["capability_ids"]:
            availability = capabilities[capability_id]["availability"]
            expected_availability = {
                "NOT_DECLARED": "NOT_DECLARED",
                "NOT_APPLICABLE": "NOT_APPLICABLE",
            }.get(state, "DECLARED")
            if availability != expected_availability:
                errors.append(
                    f"{entry_id}: claim {claim_id} requires capability "
                    f"{capability_id!r} to be {expected_availability}, not {availability}"
                )
        claim_capabilities = set(claim["capability_ids"])
        for carrier_id in claim["carrier_ids"]:
            if carrier_id in carriers:
                capability_id = carriers[carrier_id]["capability_id"]
                if capability_id not in claim_capabilities:
                    errors.append(
                        f"{entry_id}: claim {claim_id} omits carrier capability "
                        f"{capability_id!r}"
                    )
        if entry["record_kind"] == "diagnostic_analogue" and claim["claim_status"] == "Theorem":
            errors.append(
                f"{entry_id}: diagnostic analogue claim {claim_id} cannot instantiate an SOF theorem"
            )
        if claim["result_state"] in {"NOT_APPLICABLE", "NOT_DECLARED"}:
            if claim["carrier_ids"] or claim["certificate_ids"]:
                errors.append(
                    f"{entry_id}: unavailable claim {claim_id} has carriers/certificates"
                )
        for finding_id in claim["finding_ids"]:
            if finding_id in findings and claim["claim_status"] != "Theorem":
                if findings[finding_id]["result_state"] != claim["result_state"]:
                    errors.append(
                        f"{entry_id}: claim {claim_id} and finding {finding_id} "
                        "have different result states"
                    )
        errors.extend(
            f"{entry_id}: claim {error}"
            for error in evidence_errors(claim, artifacts, certificates)
        )
    return errors


def derivation_errors(entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entry_id = entry["id"]
    certificates = {item["id"]: item for item in entry["certificates"]}
    artifacts = entry["_artifact_index"]
    claims = {item["id"]: item for item in entry["claims"]}

    for derivation in entry["derivations"]:
        derivation_id = derivation["id"]
        if derivation["rule_registry_version"] != RULE_REGISTRY["rule_registry_version"]:
            errors.append(
                f"{entry_id}: derivation {derivation_id} uses unsupported rule registry "
                f"version {derivation['rule_registry_version']!r}"
            )
        rule = RULES.get(derivation["rule_id"])
        if rule is None:
            errors.append(
                f"{entry_id}: derivation {derivation_id} references unknown rule "
                f"{derivation['rule_id']!r}"
            )
        elif derivation["rule_status"] != rule["status"]:
            errors.append(
                f"{entry_id}: derivation {derivation_id} rule status does not match "
                f"the registered status {rule['status']!r}"
            )
        statuses = [item["status"] for item in derivation["condition_checks"]]
        state = derivation["derivation_state"]
        if state == "VALID":
            if derivation["rule_status"] == "Research Program":
                errors.append(
                    f"{entry_id}: derivation {derivation_id} uses an open rule as VALID"
                )
            if any(status != "SATISFIED" for status in statuses):
                errors.append(
                    f"{entry_id}: VALID derivation {derivation_id} has unsatisfied conditions"
                )
            target = claims.get(derivation["target_claim_id"])
            if target and target["result_state"] not in {"ESTABLISHED", "CERTIFIED"}:
                errors.append(
                    f"{entry_id}: VALID derivation {derivation_id} targets an unestablished claim"
                )
        elif state == "INVALID" and "FAILED" not in statuses:
            errors.append(
                f"{entry_id}: INVALID derivation {derivation_id} has no failed condition"
            )
        elif state == "UNRESOLVED" and "NOT_CHECKED" not in statuses and derivation["rule_status"] != "Research Program":
            errors.append(
                f"{entry_id}: UNRESOLVED derivation {derivation_id} has no open condition/rule"
            )
        for condition in derivation["condition_checks"]:
            if condition["status"] != "SATISFIED":
                continue
            pass_certificate = any(
                certificates[certificate_id]["status"] == "PASS"
                for certificate_id in condition["certificate_ids"]
                if certificate_id in certificates
            )
            proof_reference = any(
                artifacts[artifact_id]["role"] == "proof-reference"
                for artifact_id in condition["artifact_ids"]
                if artifact_id in artifacts
            )
            if not (pass_certificate or proof_reference):
                errors.append(
                    f"{entry_id}: satisfied condition {condition['condition_id']} "
                    "has no evidence"
                )
    return errors


def dynamics_errors(entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entry_id = entry["id"]
    dynamics = entry["dynamics"]
    objects = {item["id"]: item for item in entry["objects"]}
    status = dynamics["status"]
    if status == "typed_deformation_chart":
        if entry["capabilities"]["deformation_chart"]["availability"] != "DECLARED":
            errors.append(f"{entry_id}: typed deformation lacks deformation capability")
        comparison_id = dynamics["comparison_map_object_id"]
        if comparison_id not in objects or objects[comparison_id]["kind"] != "comparison_map":
            errors.append(f"{entry_id}: typed deformation lacks comparison-map object")
        if not dynamics["fixed_labels"] or not dynamics["fixed_conventions"]:
            errors.append(
                f"{entry_id}: typed deformation must fix labels and conventions"
            )
        if not dynamics["continuity"]:
            errors.append(f"{entry_id}: typed deformation lacks continuity declaration")
    if status == "static" and dynamics["trajectory_object_id"] is not None:
        errors.append(f"{entry_id}: static record cannot declare a trajectory")
    if status in {"schema_transition", "candidate_deformation"} and entry["findings"]:
        for finding in entry["findings"]:
            if finding["kind"] == "wall_event" and finding["claim_status"] == "Theorem":
                errors.append(
                    f"{entry_id}: schema/candidate event cannot be a theorem wall"
                )
    return errors


def contract_ref_errors(
    entry: dict[str, Any], artifacts: dict[str, dict[str, Any]]
) -> list[str]:
    refs = entry["contract_refs"]
    errors: list[str] = []
    expected_roles = {
        "capability_manifest": "capability-manifest",
        "typed_sof_ir": "typed-sof-ir",
    }
    for field, expected_role in expected_roles.items():
        contract_ref = refs[field]
        if contract_ref is None:
            continue
        artifact_id = contract_ref["artifact_id"]
        artifact = artifacts.get(artifact_id)
        if artifact is None:
            errors.append(f"{entry['id']}: compiler contract references unknown {artifact_id}")
        elif artifact["role"] != expected_role:
            errors.append(
                f"{entry['id']}: {field} artifact has role {artifact['role']!r}, "
                f"expected {expected_role!r}"
            )
        elif artifact["digest"] != contract_ref["digest"]:
            errors.append(
                f"{entry['id']}: {field} digest does not match artifact {artifact_id}"
            )
    return errors


def v2_contract_errors(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    artifacts, duplicate_errors = indexed(payload["artifacts"], "artifact")
    errors.extend(duplicate_errors)
    errors.extend(artifact_errors(artifacts))
    errors.extend(census_errors(payload, artifacts))

    for source_entry in payload["entries"]:
        entry = dict(source_entry)
        entry["_artifact_index"] = artifacts
        errors.extend(entry_reference_errors(entry, artifacts))
        errors.extend(carrier_capability_errors(entry))
        errors.extend(channel_errors(entry))
        errors.extend(finding_errors(entry))
        errors.extend(claim_errors(entry))
        errors.extend(derivation_errors(entry))
        errors.extend(dynamics_errors(entry))
        errors.extend(contract_ref_errors(entry, artifacts))

        used_artifact_ids = collect_entry_artifact_ids(entry)
        declared_artifact_ids = set(entry["artifact_ids"])
        missing_from_entry = sorted(used_artifact_ids - declared_artifact_ids)
        if missing_from_entry:
            errors.append(
                f"{entry['id']}: evidence uses artifacts omitted from entry.artifact_ids: "
                + ", ".join(missing_from_entry)
            )
        if entry["evidence_role"] != "historical_provenance":
            for artifact_id in used_artifact_ids:
                artifact = artifacts.get(artifact_id)
                if artifact is None:
                    continue
                if artifact["evidence_scope"] == "historical_provenance" or "archive" in PurePosixPath(artifact["uri"]).parts:
                    errors.append(
                        f"{entry['id']}: active/proxy evidence references historical "
                        f"artifact {artifact_id}"
                    )
    return errors


def contract_errors(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entries = payload.get("entries", [])
    snapshot = payload.get("snapshot", {})
    if snapshot.get("entry_count") != len(entries):
        errors.append(
            f"snapshot.entry_count is {snapshot.get('entry_count')}, but {len(entries)} entries exist"
        )
    duplicates = duplicate_values(entry.get("id") for entry in entries)
    if duplicates:
        errors.append(f"duplicate entry IDs: {', '.join(duplicates)}")
    source = snapshot.get("source")
    if source and not repository_path(source).is_file():
        errors.append(f"snapshot source does not exist: {source}")

    version = payload.get("registry_schema_version")
    if version == "1.0":
        errors.extend(v1_contract_errors(payload))
    elif version == "2.0":
        errors.extend(v2_contract_errors(payload))
    return errors


def validate_payload(
    payload: dict[str, Any], schema: dict[str, Any] | None = None
) -> list[str]:
    if schema is None:
        schema_path = SCHEMAS.get(payload.get("registry_schema_version"))
        if schema_path is None:
            return [
                "no schema registered for Registry version "
                f"{payload.get('registry_schema_version')!r}"
            ]
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema_failures = schema_errors(payload, schema)
    if schema_failures:
        return schema_failures
    return contract_errors(payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Registry snapshots.")
    parser.add_argument(
        "--schema", type=Path, help="Override schema for every supplied snapshot."
    )
    parser.add_argument(
        "--include-migration-candidate",
        action="store_true",
        help="Deprecated compatibility flag; v2.0 is validated by default.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = list(args.paths) if args.paths else list(DEFAULT_SNAPSHOTS)
    override_schema = (
        json.loads(args.schema.read_text(encoding="utf-8")) if args.schema else None
    )
    failures = 0
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        errors = validate_payload(payload, override_schema)
        if errors:
            failures += 1
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(
                f"PASS {path} ({payload['snapshot']['entry_count']} entries, "
                f"schema v{payload['registry_schema_version']})"
            )
    if failures:
        raise SystemExit(f"{failures} Registry snapshot(s) failed validation.")
    print(f"Validated {len(paths)} SOF Registry snapshot(s).")


if __name__ == "__main__":
    main()
