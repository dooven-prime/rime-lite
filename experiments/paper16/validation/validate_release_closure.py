#!/usr/bin/env python3
"""Build and verify the Paper XVI paper-owned release closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
PACKAGE_ROOT = HERE.parents[1]
REPO_ROOT = HERE.parents[3]
MALE_ROOT = PACKAGE_ROOT / "source"
MANIFEST_PATH = PACKAGE_ROOT / "release-manifest.v1.json"
RECEIPT_PATH = PACKAGE_ROOT / "results" / "release-closure.v1.validation-receipt.json"
EXACT_REPLAY_RECEIPT = PACKAGE_ROOT / "results" / "a1-a2-exact-replay.v1.receipt.json"
PROVENANCE_PATH = PACKAGE_ROOT / "upstream-provenance.v1.json"


DIRECT_FILES = (
    ("scripts/path_lifting_audit.py", "PRODUCER", ("C1", "C2")),
    ("scripts/path_lifting_depth3_audit.py", "PRODUCER", ("C1", "C2")),
    ("scripts/sectorization_field_audit.py", "PRODUCER", ("C1", "C2")),
    ("scripts/sectorization_comparison_report.py", "PRODUCER", ("C1", "C2")),
    ("results/path_lifting_audit_full_v3.json", "SCIENTIFIC_ARTIFACT", ("C1", "C2")),
    ("results/path_lifting_audit_full_v3_somaSide.json", "SCIENTIFIC_ARTIFACT", ("C1", "C2")),
    ("results/path_lifting_depth3_audit_full_v1.json", "SCIENTIFIC_ARTIFACT", ("C1", "C2")),
    ("results/path_lifting_depth3_audit_full_somaSide_v1.json", "SCIENTIFIC_ARTIFACT", ("C1", "C2")),
    ("results/sectorization_field_audit_v1.json", "SCIENTIFIC_ARTIFACT", ("C1", "C2")),
    ("results/sectorization_comparison_v1.json", "SCIENTIFIC_ARTIFACT", ("C1", "C2")),
    ("digital_fly_v0_1/scripts/run_sd1_operator_admission.py", "PRODUCER", ("C3",)),
    ("digital_fly_v0_1/scripts/run_sd1_dynamics.py", "PRODUCER", ("C3",)),
    ("digital_fly_v0_1/scripts/run_o1_observation_resolution.py", "PRODUCER", ("C4",)),
    ("digital_fly_v0_1/results/sd1_operator_admission_v0_1.json", "PORTABLE_SCIENTIFIC_ARTIFACT", ("C3",)),
    ("digital_fly_v0_1/results/sd1_dynamics_v0_1.json", "PORTABLE_SCIENTIFIC_ARTIFACT", ("C3",)),
    ("digital_fly_v0_1/results/o1_observation_resolution_v0_1.json", "PORTABLE_SCIENTIFIC_ARTIFACT", ("C4",)),
    ("digital_fly_v0/scripts/build_annotation_intersection_carrier.py", "CARRIER_PRODUCER", ("C3-C8",)),
    ("digital_fly_v0/results/carrier_v0_manifest.json", "CARRIER_MANIFEST", ("C3-C8",)),
    ("requirements/static.txt", "REPLAY_RUNTIME_LOCK", ("C1-C8",)),
    ("digital_fly_v0_2/scripts/run_d2_1_markov_closure.py", "PRODUCER", ("C5",)),
    ("digital_fly_v0_2/results/d2_1_markov_closure_v0_2.json", "PORTABLE_SCIENTIFIC_ARTIFACT", ("C5",)),
    ("digital_fly_v0_2/scripts/run_d2_2_memory_closure.py", "PRODUCER", ("C6",)),
    ("digital_fly_v0_2/scripts/run_d2_3_partition_comparison.py", "PRODUCER", ("C7", "C8")),
    ("digital_fly_v0_2/results/d2_2_memory_closure_v0_2.json", "SCIENTIFIC_ARTIFACT", ("C6",)),
    ("digital_fly_v0_2/results/d2_3_partition_comparison_v0_2.json", "SCIENTIFIC_ARTIFACT", ("C7", "C8")),
    ("followups/y_known_pm_route_audit.design-v1.json", "DESIGN", ("C8",)),
    ("followups/y_known_pm_route_audit.registration-v1.2.json", "REGISTRATION", ("C8",)),
    ("followups/run_y_known_pm_route_audit.py", "PRODUCER", ("C8",)),
    ("followups/validation/validate_y_known_pm_route_audit.py", "LOCAL_VALIDATOR", ("C8",)),
    ("followups/results/y_known_pm_route_audit.v1.json", "SCIENTIFIC_ARTIFACT", ("C8",)),
    ("followups/results/y_known_pm_route_audit.v1.validation-receipt.json", "LOCAL_VALIDATION_RECEIPT", ("C8",)),
    ("followups/d2_2_named_sector_followup.design-v1.json", "DESIGN", ("C6",)),
    ("followups/d2_2_named_sector_followup.registration-v1.1.json", "REGISTRATION", ("C6",)),
    ("followups/run_d2_2_named_sector_followup.py", "PRODUCER", ("C6",)),
    ("followups/validation/validate_d2_2_named_sector_followup.py", "LOCAL_VALIDATOR", ("C6",)),
    ("followups/results/d2_2_named_sector_followup.v1.json", "SCIENTIFIC_ARTIFACT", ("C6",)),
    ("followups/results/d2_2_named_sector_followup.v1.validation-receipt.json", "LOCAL_VALIDATION_RECEIPT", ("C6",)),
    ("replay/replay_large_artifacts.py", "CARRIER_REPLAY_IMPLEMENTATION", ("C3-C8",)),
    ("replay/large_artifact_closure.v1.json", "CARRIER_REPLAY_CLOSURE", ("C3-C8",)),
    ("replay/results/large_artifact_replay.v1.receipt.json", "CARRIER_REPLAY_RECEIPT", ("C3-C8",)),
    ("requirements/followups.txt", "FOLLOWUP_RUNTIME_LOCK", ("C6", "C8")),
)

REPOSITORY_FILES = (
    ("experiments/paper16/README.md", "PACKAGE_README", ()),
    ("experiments/paper16/upstream-provenance.v1.json", "UPSTREAM_PROVENANCE", ("C1-C8",)),
    ("experiments/paper16/validation/replay_exact_followups.py", "PRODUCER_REPLAY_IMPLEMENTATION", ("C6", "C8")),
    ("experiments/paper16/validation/replay_static_audits.py", "PRODUCER_REPLAY_IMPLEMENTATION", ("C1", "C2")),
    ("experiments/paper16/validation/replay_dynamic_descent.py", "PRODUCER_REPLAY_IMPLEMENTATION", ("C3-C8",)),
    ("experiments/paper16/validation/validate_release_closure.py", "CLOSURE_VALIDATOR", ()),
    ("experiments/paper16/results/a1-a2-exact-replay.v1.receipt.json", "PRODUCER_REPLAY_RECEIPT", ("C6", "C8")),
    ("experiments/paper16/results/static-audits-replay.v1.receipt.json", "PRODUCER_REPLAY_RECEIPT", ("C1", "C2")),
    ("experiments/paper16/results/dynamic-descent-replay.v1.receipt.json", "PRODUCER_REPLAY_RECEIPT", ("C3-C8",)),
    ("papers/paper16/Paper XVI.md", "CANONICAL_MANUSCRIPT", ("C1-C8",)),
    ("papers/paper16/references-v1.bib", "BIBLIOGRAPHY_SLICE", ()),
    ("papers/paper16/paper16_arxiv.pdf", "READER_PDF", ("C1-C8",)),
    ("figures/paper16/render.py", "FIGURE_PRODUCER", ("C1-C8",)),
    ("figures/paper16/fig1_descent_stack.png", "READER_FIGURE", ("C1-C8",)),
    ("figures/paper16/fig2_registered_contrasts.png", "READER_FIGURE", ("C1-C8",)),
)

SELECTED_REPLAY_OUTPUTS = (
    "digital_fly_v0/results/carrier_v0_edges.npz",
    "digital_fly_v0/results/carrier_v0_manifest.json",
    "digital_fly_v0/results/carrier_v0_nodes.parquet",
)

EXCLUDED_SURFACES = (
    "public_projection/manifest.v1.json",
    "digital_fly_v1/results/e0_3_*",
    "digital_fly_e1/",
    "followups/results/y_known_pm_route_audit.execution-attempt-v1.json",
    "experiments/paper16/results/release-closure.v1.validation-receipt.json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_entry(relative: str, role: str, claims: tuple[str, ...]) -> dict[str, Any]:
    path = MALE_ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return {
        "path": relative,
        "path_base": "PAPER16_SOURCE_ROOT",
        "role": role,
        "claims": list(claims),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def repo_file_entry(relative: str, role: str, claims: tuple[str, ...]) -> dict[str, Any]:
    path = REPO_ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return {
        "path": relative,
        "path_base": "REPOSITORY_ROOT",
        "role": role,
        "claims": list(claims),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def selected_replay_binding() -> dict[str, Any]:
    closure_path = MALE_ROOT / "replay/large_artifact_closure.v1.json"
    receipt_path = MALE_ROOT / "replay/results/large_artifact_replay.v1.receipt.json"
    closure = read_json(closure_path)
    receipt = read_json(receipt_path)
    body = {key: value for key, value in closure.items() if key != "closure_sha256"}
    if canonical_sha256(body) != closure.get("closure_sha256"):
        raise ValueError("large-artifact closure digest mismatch")
    if receipt.get("status") != "PASS" or not receipt.get("producer_replay_performed"):
        raise ValueError("clean-clone replay receipt is not a passed producer replay")
    if receipt.get("closure_sha256") != closure.get("closure_sha256"):
        raise ValueError("replay receipt does not bind the declared closure")
    closure_outputs = {item["path"]: item for item in closure["outputs"]}
    receipt_outputs = {item["path"]: item for item in receipt["outputs"]}
    selected: list[dict[str, Any]] = []
    for path in SELECTED_REPLAY_OUTPUTS:
        declared = closure_outputs.get(path)
        replayed = receipt_outputs.get(path)
        if declared is None or replayed is None:
            raise ValueError(f"selected replay output missing: {path}")
        if not (replayed.get("exists") and replayed.get("size_matches") and replayed.get("sha256_matches")):
            raise ValueError(f"selected replay output did not pass: {path}")
        selected.append(dict(declared))
    return {
        "selection_rule": "Paper XVI carrier-only clean-clone replay closure",
        "identity_scope": "three derived carrier outputs consumed by the theorem-facing follow-ups",
        "closure_path": "replay/large_artifact_closure.v1.json",
        "closure_sha256": closure["closure_sha256"],
        "clean_clone_receipt_path": "replay/results/large_artifact_replay.v1.receipt.json",
        "clean_clone_receipt_sha256": sha256_file(receipt_path),
        "producer_replay_performed": True,
        "independent_validation": False,
        "selected_outputs": selected,
        "unrelated_sidecar_outputs_in_closure": False,
    }


def semantic_checks() -> list[str]:
    failures: list[str] = []
    d21 = read_json(MALE_ROOT / "digital_fly_v0_2/results/d2_1_markov_closure_v0_2.json")
    d22 = read_json(MALE_ROOT / "digital_fly_v0_2/results/d2_2_memory_closure_v0_2.json")
    d23 = read_json(MALE_ROOT / "digital_fly_v0_2/results/d2_3_partition_comparison_v0_2.json")
    a1 = read_json(MALE_ROOT / "followups/results/y_known_pm_route_audit.v1.json")
    a2 = read_json(MALE_ROOT / "followups/results/d2_2_named_sector_followup.v1.json")
    a1_receipt = read_json(MALE_ROOT / "followups/results/y_known_pm_route_audit.v1.validation-receipt.json")
    a2_receipt = read_json(MALE_ROOT / "followups/results/d2_2_named_sector_followup.v1.validation-receipt.json")
    exact_replay = read_json(EXACT_REPLAY_RECEIPT)
    static_replay = read_json(PACKAGE_ROOT / "results/static-audits-replay.v1.receipt.json")
    dynamic_replay = read_json(PACKAGE_ROOT / "results/dynamic-descent-replay.v1.receipt.json")
    expectations = (
        (d21.get("d2_1_status") == "FAILED_FIRST_ORDER_MARKOV_CLOSURE", "D2.1 status"),
        (d22.get("d2_2_status") == "FAILED_ORDER_1_MEMORY_CLOSURE", "D2.2 status"),
        (d23.get("partition_results", {}).get("somaSide", {}).get("status") == "FAILED_FIRST_ORDER_CLOSURE", "D2.3 somaSide status"),
        (a1.get("outcome") == "SAME_CARRIER_CONTRAST_CONFIRMED", "A1 outcome"),
        (a2.get("typed_named", {}).get("outcome") == "EXACT_NAMED_SECTOR_WITNESS_FOUND", "A2 named-sector outcome"),
        (
            a1.get("exact_arithmetic", {}).get("row_abs_accumulation")
            == "int64 np.add.at over nonnegative integer weights"
            and 0
            < a1.get("exact_arithmetic", {}).get(
                "row_abs_int64_overflow_upper_bound", 0
            )
            <= 2**63 - 1,
            "A1 exact integer row-mass accumulation",
        ),
        (
            a2.get("exact_dynamics", {}).get("row_abs_accumulation")
            == "int64 np.add.at over nonnegative integer weights"
            and 0
            < a2.get("exact_dynamics", {}).get(
                "row_abs_int64_overflow_upper_bound", 0
            )
            <= 2**63 - 1,
            "A2 exact integer row-mass accumulation",
        ),
        (a1_receipt.get("status") == "PASS" and not a1_receipt.get("independent_validation"), "A1 receipt boundary"),
        (a2_receipt.get("status") == "PASS" and not a2_receipt.get("independent_validation"), "A2 receipt boundary"),
        (
            exact_replay.get("status") == "PASS"
            and exact_replay.get("producer_replay_performed") is True
            and exact_replay.get("all_replayed_bytes_equal") is True,
            "A1/A2 exact producer replay",
        ),
        (
            static_replay.get("status") == "PASS"
            and static_replay.get("producer_replay_performed") is True
            and static_replay.get("all_replayed_bytes_equal") is True,
            "static LP2/LP3 exact producer replay",
        ),
        (
            dynamic_replay.get("status") == "PASS"
            and dynamic_replay.get("producer_replay_performed") is True
            and dynamic_replay.get("all_replayed_bytes_equal") is True,
            "v0.1-v0.2 dynamic-descent exact producer replay",
        ),
    )
    for passed, label in expectations:
        if not passed:
            failures.append(label)
    return failures


def build_manifest() -> dict[str, Any]:
    ordered = [file_entry(*spec) for spec in DIRECT_FILES]
    ordered.extend(repo_file_entry(*spec) for spec in REPOSITORY_FILES)
    ordered.sort(key=lambda item: (item["role"], item["path"]))
    provenance = read_json(PROVENANCE_PATH)
    replay = selected_replay_binding()
    exclusion = {
        "paths_or_surfaces": list(EXCLUDED_SURFACES),
        "historical_public_projection_is_release_identity": False,
        "digital_fly_e0_3_included": False,
        "digital_fly_e1_included": False,
        "receipt_in_own_closure": False,
    }
    closure_basis = {
        "ordered_closure": ordered,
        "external_inputs": provenance["exact_inputs"],
        "selected_replay_binding": replay,
        "exclusion_boundary": exclusion,
    }
    return {
        "schema": "rime.paper16.release-manifest.v1",
        "status": "RELEASE_CLOSURE_PENDING_CONTENT_COMMIT_AND_EXTERNAL_ANCHOR",
        "publication_line": "MaleCNS Representation Loss and Dynamic Descent",
        "claim_ids": [f"C{index}" for index in range(1, 9)],
        "release_identity": {
            "canonical_manuscript": {
                "path": "papers/paper16/Paper XVI.md",
                "sha256": sha256_file(REPO_ROOT / "papers/paper16/Paper XVI.md"),
            },
            "reader_pdf": {
                "path": "papers/paper16/paper16_arxiv.pdf",
                "sha256": sha256_file(REPO_ROOT / "papers/paper16/paper16_arxiv.pdf"),
            },
            "release_content_commit": None,
            "external_anchor": None,
            "claim_authority": "papers/paper16/Paper XVI.md",
        },
        "ordered_closure": ordered,
        "upstream_dataset": provenance["dataset"],
        "external_inputs": provenance["exact_inputs"],
        "selected_replay_binding": replay,
        "exclusion_boundary": exclusion,
        "closure_sha256": canonical_sha256(closure_basis),
        "claim_boundary": {
            "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
            "independent_validation": False,
            "producer_replay_scope": "static LP2/LP3 artifacts, selected carrier outputs, v0.1-v0.2 dynamic-descent artifacts, and the corrected A1/A2 producers have passed bound replay; the local artifact validators themselves remain non-replay closure checks",
            "same_carrier_result": "somaSide exact LP2=LP3=1 and deterministic first-order closure failure on registered normalized Y_known_pm",
            "named_sector_result": "one exact D2.2 history-fiber witness in cb_intrinsic; no claim for memory orders k>=2",
            "not_supported": [
                "all-depth liftability",
                "biological mechanism or causal attribution",
                "Digital Fly embodied competence",
                "E0.3 finite-null structural contrast",
                "E1 inverse identifiability",
            ],
        },
    }


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    expected = build_manifest()
    if manifest != expected:
        failures.append("manifest does not match current registered release closure")
    failures.extend(semantic_checks())
    for entry in manifest.get("ordered_closure", []):
        path = (REPO_ROOT if entry.get("path_base") == "REPOSITORY_ROOT" else MALE_ROOT) / entry["path"]
        if not path.is_file():
            failures.append(f"missing closure file: {entry['path']}")
            continue
        if path.stat().st_size != entry["size"] or sha256_file(path) != entry["sha256"]:
            failures.append(f"closure byte mismatch: {entry['path']}")
    for entry in manifest.get("selected_replay_binding", {}).get("selected_outputs", []):
        path = MALE_ROOT / entry["path"]
        if path.is_file() and (path.stat().st_size != entry["size"] or sha256_file(path) != entry["sha256"]):
            failures.append(f"local selected replay output mismatch: {entry['path']}")
    all_paths = {entry["path"] for entry in manifest.get("ordered_closure", [])}
    if str(RECEIPT_PATH.relative_to(REPO_ROOT)).replace("\\", "/") in all_paths:
        failures.append("receipt occurs in its own closure")
    if "public_projection/manifest.v1.json" in all_paths:
        failures.append("historical public projection manifest entered release identity")
    if any(path.startswith("digital_fly_v1/results/e0_3_") or path.startswith("digital_fly_e1/") for path in all_paths):
        failures.append("Line B evidence entered the Paper XVI release closure")
    serialized = json.dumps(manifest, ensure_ascii=False)
    if "experiments/exploratory/male_cns_connectome" in serialized:
        failures.append("nonpublic exploratory path entered Paper XVI release closure")
    return failures


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if args.refresh:
        write_json(MANIFEST_PATH, build_manifest())
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(MANIFEST_PATH)
    manifest = read_json(MANIFEST_PATH)
    failures = validate_manifest(manifest)
    result = {
        "schema": "rime.paper16.release-closure-validation.v1",
        "status": "PASS" if not failures else "FAIL",
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "independent_validation": False,
        "producer_replay_performed_by_this_validator": False,
        "manifest_path": str(MANIFEST_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "manifest_sha256": sha256_file(MANIFEST_PATH),
        "closure_sha256": manifest.get("closure_sha256"),
        "ordered_closure_entries": len(manifest.get("ordered_closure", [])),
        "paper_owned_portable_artifacts": 4,
        "selected_clean_clone_replay_outputs": len(SELECTED_REPLAY_OUTPUTS),
        "receipt_in_own_closure": False,
        "failures": failures,
        "release_readiness": {
            "release_closure_validated": not failures,
            "canonical_manuscript_bound": bool(manifest.get("release_identity", {}).get("canonical_manuscript")),
            "reader_pdf_bound": bool(manifest.get("release_identity", {}).get("reader_pdf")),
            "release_commit_bound": False,
            "external_anchor_bound": False,
        },
    }
    if args.refresh:
        write_json(RECEIPT_PATH, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
