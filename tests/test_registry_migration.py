"""Release regression for the immutable-v1 to Registry-v2.0 migration."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.paper9.calibrated_response import audit
from registry.migrate_v1_to_v2 import V1_PATH, V2_PATH, build
from registry.validate_snapshot import SCHEMAS, validate_payload


EXPECTED_V1_SHA256 = (
    "fc1cd5cf8c7c8b768da1c61dfdfcea88723ce47433c562812cd386d940e8495c"
)

assert hashlib.sha256(V1_PATH.read_bytes()).hexdigest() == EXPECTED_V1_SHA256

generated = build()
committed = json.loads(V2_PATH.read_text(encoding="utf-8"))
assert generated == committed, "Registry v2.0 is stale; rerun the migrator"
schema = json.loads(SCHEMAS["2.0"].read_text(encoding="utf-8"))
assert not validate_payload(committed, schema)

entries = {entry["id"]: entry for entry in committed["entries"]}
artifacts = {artifact["id"]: artifact for artifact in committed["artifacts"]}
assert len(entries) == 19
assert sum(
    entry["record_kind"] == "strict_sof" for entry in entries.values()
) == 15
assert sum(
    entry["record_kind"] == "diagnostic_analogue"
    for entry in entries.values()
) == 4

census = committed["census_certificate"]
assert census["schema_version"] == "2.0"
assert census["validation_status"] == "PASS"
assert census["summary"]["entry_count"] == 19
assert census["summary"]["strict_sof_count"] == 15
assert census["summary"]["diagnostic_analogue_count"] == 4
assert census["summary"]["finding_count"] == 28
assert census["summary"]["capability_counts"]["word_carrier"] == 4
assert census["summary"]["capability_counts"]["lie_hall_carrier"] == 5

assert len(entries["rubik-finite-order-log-lie"]["observable_channels"]) == 1
assert entries["rubik-finite-order-log-lie"]["observable_channels"][0]["id"] == (
    "channel.r1-lie"
)
assert set(entries["mechanism-separated-control"]["findings"][0]["channel_ids"]) == {
    "channel.k0-grow",
    "channel.k1-decay",
}
assert set(entries["neural-network-sof"]["findings"][0]["channel_ids"]) == {
    "channel.k0",
    "channel.k1",
    "channel.k2",
}
assert entries["control-kalman"]["findings"][0]["channel_ids"] == [
    "channel.kalman-flag-rank"
]

xu = entries["xu-ridge"]["findings"][0]
assert xu["value"] == "749.6x"
assert xu["extraction_context"]["derivation_kind"] == "locally_derived"
assert "not threshold-crossing" in xu["extraction_context"]["response_convention"]

for finding in entries["quantum-gates"]["findings"]:
    repair = finding["repair_registration"]
    assert repair["repair_kind"] == "static_filtration_repair"
    assert repair["temporal_scope"] == "static"
    assert repair["cutoff"] == 4
    assert repair["count_denominator"] == 12
    assert repair["saturation_status"] == "truncated_only"

response = audit()
assert response["tau_k0_grow"] == 30
assert response["tau_k1_response"] == 1380
assert response["k1_response"][0] == 0.0
assert response["k1_response"][-1] > response["k1_response"][0]

for entry in entries.values():
    for finding in entry["findings"]:
        if finding["claim_status"] != "Computational Certificate":
            continue
        roles = {
            artifacts[artifact_id]["role"]
            for artifact_id in finding["artifact_ids"]
        }
        assert "source-data" in roles, (
            f"{entry['id']}/{finding['id']} lacks a versioned result artifact"
        )

paper10_result = next(
    artifact
    for artifact in artifacts.values()
    if artifact["uri"] == "experiments/paper10/results/registry_evidence_v2.json"
)
assert paper10_result["role"] == "source-data"
assert [
    artifacts[artifact_id]["uri"]
    for artifact_id in paper10_result["generated_by_artifact_ids"]
] == ["experiments/paper10/validation/build_results.py"]
assert entries["mechanism-separated-control"]["findings"][0]["artifact_ids"] == [
    paper10_result["id"]
]

for entry_id in ("graph-systems", "yang-like-filtration"):
    assert all(
        "/archive/" not in f"/{artifacts[artifact_id]['uri']}"
        for artifact_id in entries[entry_id]["artifact_ids"]
    )

for entry_id, maximum_depth in (("markov-systems", 2), ("graph-systems", 5)):
    entry = entries[entry_id]
    assert entry["capabilities"]["word_carrier"]["availability"] == "DECLARED"
    assert entry["capabilities"]["lie_hall_carrier"]["availability"] == (
        "NOT_DECLARED"
    )
    depth_channel = next(
        channel
        for channel in entry["observable_channels"]
        if channel["id"] == "channel.d-word"
    )
    assert depth_channel["depth_mode"] == "exact"
    depth_finding = next(
        finding for finding in entry["findings"] if finding["kind"] == "depth"
    )
    assert f"D_word[Y]={maximum_depth}" in depth_finding["value"]
    assert depth_finding["depth_registration"]["mode"] == "exact"

legacy_import = next(
    artifact
    for artifact in artifacts.values()
    if artifact["uri"]
    == "experiments/paper10/results/legacy_certificate_imports_v2.json"
)
assert legacy_import["role"] == "source-data"
assert {
    entries["constructed-commutator-cancellation"]["findings"][0][
        "artifact_ids"
    ][0],
    entries["quantum-gates"]["findings"][0]["artifact_ids"][0],
} == {legacy_import["id"]}

print("test_registry_migration.py: OK")
