"""Active hostile and conformance controls for Paper XX maintenance."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
MANUSCRIPT = ROOT / "papers" / "paper20" / "Paper XX.md"
sys.path.insert(0, str(ROOT))

from experiments.paper20.adapters import z2_double_regular_engine
from experiments.paper20.census import content_digest
from experiments.paper20.engine import _boolean_matrix_power
from experiments.paper20.validate_results import DEFAULT_CENSUS_ARTIFACTS, validate
from experiments.paper20.validate_image_kernel import (
    DEFAULT_ARTIFACT as IMAGE_KERNEL_ARTIFACT,
    validate as validate_image_kernel,
)
from experiments.paper20.validate_within_carrier_census import (
    DEFAULT_OUTPUT as WITHIN_CARRIER_ARTIFACT,
    validate as validate_within_carrier,
)
from experiments.paper20.validation.validate_release import (
    DEFAULT_RECEIPT,
    PUBLISHED_RELEASE_REFS,
    content_digest as release_content_digest,
    git_blob,
    historical_artifact_bytes,
    receipt_errors,
)


def test_paper21_is_not_promoted_to_a_corollary() -> None:
    manuscript = " ".join(MANUSCRIPT.read_text(encoding="utf-8").split())
    assert "Paper XXI is not a corollary of the carrier factorization proved here" in manuscript


def test_boolean_power_does_not_overflow_path_counts() -> None:
    complete = np.ones((3, 3), dtype=bool)
    assert np.all(_boolean_matrix_power(complete, 41))

    engine = z2_double_regular_engine()
    adjacency = engine.direct_support() > engine.support_tolerance
    assert np.all(_boolean_matrix_power(adjacency, 51))


def test_z2_census_preserves_the_relation_sandwich() -> None:
    result = z2_double_regular_engine().census(3)
    assert result.support_path_pair_counts[3] == 9
    assert result.carrier_path_pair_counts[3] == 7
    assert result.composition_pair_counts[3] == 7
    assert result.cross_carrier_stitch_pair_counts[3] == 2
    assert result.within_carrier_obstructed_pair_counts[3] == 0


def test_default_census_validation_excludes_specialized_artifacts() -> None:
    assert [path.name for path in DEFAULT_CENSUS_ARTIFACTS] == [
        "z2_double_regular_depth3.json",
        "s3_natural_regular_depth2.json",
        "rubik_228_depth2.json",
    ]
    completed = subprocess.run(
        [sys.executable, "experiments/paper20/validate_results.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.count("PASS ") == 3
    assert "FAIL " not in completed.stdout
    assert "within_carrier_obstruction_v1.json" not in completed.stdout
    assert "release-receipt.json" not in completed.stdout


def test_validator_rejects_coordinated_relation_tampering() -> None:
    source = ROOT / "experiments/paper20/results/rubik_228_depth2.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    tampered = deepcopy(payload)
    tampered["result"]["carrier_path_pair_counts"]["2"] = 0
    tampered["result"]["cross_carrier_stitch_pair_counts"]["2"] = 53
    tampered["result"]["within_carrier_obstructed_pair_counts"]["2"] = 999
    tampered["content_sha256"] = content_digest(tampered)
    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as handle:
        json.dump(tampered, handle)
        path = Path(handle.name)
    try:
        errors = validate(path)
    finally:
        path.unlink()
    assert errors
    assert any("carrier" in error or "obstruction" in error for error in errors)


def test_image_kernel_audit_closes_depth_two_without_all_depth_promotion() -> None:
    assert validate_image_kernel(IMAGE_KERNEL_ARTIFACT) == []
    payload = json.loads(IMAGE_KERNEL_ARTIFACT.read_text(encoding="utf-8"))
    aggregate = payload["aggregate"]
    assert payload["evidence_layers"]["enumeration_certificate"]["status"] == (
        "EXACT_FINITE_ENUMERATION_CERTIFICATE"
    )
    assert payload["evidence_layers"]["numerical_observation"]["status"] == (
        "BOUNDED_NUMERICAL_OBSERVATION"
    )
    assert payload["evidence_layers"]["exact_zero_status"]["status"] == "NOT_ESTABLISHED"
    assert aggregate["route_audit_count"] == 34992
    assert aggregate["nontrivial_image_kernel_annihilation_count"] == 0
    assert aggregate["all_depth_exact_status"] == "NOT_ESTABLISHED"


def test_image_kernel_validator_rejects_all_depth_overpromotion() -> None:
    payload = json.loads(IMAGE_KERNEL_ARTIFACT.read_text(encoding="utf-8"))
    payload["aggregate"]["all_depth_exact_status"] = "ESTABLISHED"
    payload["content_sha256"] = content_digest(payload)
    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as handle:
        json.dump(payload, handle)
        path = Path(handle.name)
    try:
        errors = validate_image_kernel(path)
    finally:
        path.unlink()
    assert any("overpromoted" in error for error in errors)


def test_image_kernel_validator_rejects_exact_zero_overpromotion() -> None:
    payload = json.loads(IMAGE_KERNEL_ARTIFACT.read_text(encoding="utf-8"))
    payload["evidence_layers"]["exact_zero_status"]["projected_factor_zero"] = (
        "EXACT_ZERO_CERTIFICATE"
    )
    payload["content_sha256"] = content_digest(payload)
    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as handle:
        json.dump(payload, handle)
        path = Path(handle.name)
    try:
        errors = validate_image_kernel(path)
    finally:
        path.unlink()
    assert any("exact-zero" in error for error in errors)


def test_exact_shared_carrier_census_has_strict_obstructions() -> None:
    assert validate_within_carrier(WITHIN_CARRIER_ARTIFACT) == []
    payload = json.loads(WITHIN_CARRIER_ARTIFACT.read_text(encoding="utf-8"))
    enumeration = payload["enumeration"]
    assert enumeration["total_labelled_route_count"] == 108
    assert enumeration["support_candidate_count"] == 24
    assert enumeration["active_product_count"] == 16
    assert enumeration["strict_within_carrier_obstruction_count"] == 8
    assert enumeration["disjoint_endpoint_carrier_obstruction_count"] == 0


def test_published_receipt_resolves_tagged_bytes_not_current_head() -> None:
    receipt = json.loads(DEFAULT_RECEIPT.read_text(encoding="utf-8"))
    release_ref = PUBLISHED_RELEASE_REFS[receipt["release_id"]]
    bibliography = next(
        row
        for row in receipt["artifact_closure"]["ordered_artifacts"]
        if row["role"] == "bibliography"
    )
    uri = bibliography["artifact"]["uri"]
    raw_blob = git_blob(release_ref, uri)
    historical_bytes = historical_artifact_bytes(receipt["release_id"], uri)
    expected_digest = bibliography["artifact"]["sha256"]
    assert hashlib.sha256(raw_blob).hexdigest() != expected_digest
    assert hashlib.sha256(historical_bytes).hexdigest() == expected_digest
    assert receipt_errors(receipt) == []


def test_published_receipt_rejects_coordinated_tampering() -> None:
    receipt = json.loads(DEFAULT_RECEIPT.read_text(encoding="utf-8"))
    tampered = deepcopy(receipt)
    tampered["artifact_closure"]["ordered_artifacts"][0]["artifact"]["sha256"] = (
        "0" * 64
    )
    tampered["artifact_closure"]["closure_digest"] = "0" * 64
    tampered["content_sha256"] = release_content_digest(tampered)
    errors = receipt_errors(tampered)
    assert errors
    assert any("paper20-v1.0" in error for error in errors)


def test_published_receipt_rejects_boundary_overpromotion() -> None:
    receipt = json.loads(DEFAULT_RECEIPT.read_text(encoding="utf-8"))
    tampered = deepcopy(receipt)
    tampered["formalization"]["status"] = "LEAN_PROVED"
    tampered["content_sha256"] = release_content_digest(tampered)
    errors = receipt_errors(tampered)
    assert errors
    assert any("current paper-owned closure" in error for error in errors)


if __name__ == "__main__":
    test_paper21_is_not_promoted_to_a_corollary()
    test_boolean_power_does_not_overflow_path_counts()
    test_z2_census_preserves_the_relation_sandwich()
    test_default_census_validation_excludes_specialized_artifacts()
    test_validator_rejects_coordinated_relation_tampering()
    test_image_kernel_audit_closes_depth_two_without_all_depth_promotion()
    test_image_kernel_validator_rejects_all_depth_overpromotion()
    test_image_kernel_validator_rejects_exact_zero_overpromotion()
    test_exact_shared_carrier_census_has_strict_obstructions()
    test_published_receipt_resolves_tagged_bytes_not_current_head()
    test_published_receipt_rejects_coordinated_tampering()
    test_published_receipt_rejects_boundary_overpromotion()
    print("Paper XX hostile controls: OK")
