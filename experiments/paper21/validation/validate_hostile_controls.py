#!/usr/bin/env python3
"""Internal hostile gate for the Paper XXI release-evidence closure."""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_DIR = ROOT / "experiments" / "paper21"
CERTIFICATE = EVIDENCE_DIR / "results" / "route_profile_promotion_v1.json"
RECEIPT = CERTIFICATE.with_name("route_profile_promotion_v1.validation-receipt.json")
LEAN_RECEIPT = CERTIFICATE.with_name("route_profiles_lean_v1.validation-receipt.json")
ARBITRARY_DEPTH = CERTIFICATE.with_name("arbitrary_depth_semantic_v1.json")
ARBITRARY_DEPTH_RECEIPT = CERTIFICATE.with_name(
    "arbitrary_depth_semantic_v1.validation-receipt.json"
)
VALIDATOR = EVIDENCE_DIR / "validation" / "validate_route_profiles.py"
LEAN_VALIDATOR = EVIDENCE_DIR / "validation" / "validate_lean_formalization.py"
ARBITRARY_DEPTH_VALIDATOR = (
    EVIDENCE_DIR / "validation" / "validate_arbitrary_depth_semantic.py"
)
PROMOTER = EVIDENCE_DIR / "validation" / "promote_route_profiles.py"
RELEASE_VALIDATOR = EVIDENCE_DIR / "validation" / "validate_release.py"
RELEASE_RECEIPT = EVIDENCE_DIR / "results" / "route_profiles_v1.release-receipt.json"
MANUSCRIPT = ROOT / "papers" / "paper21" / "Paper XXI.md"

manuscript = " ".join(MANUSCRIPT.read_text(encoding="utf-8").split())
assert "this paper is not a corollary, specialization, or application of Paper XX" in manuscript

with tempfile.TemporaryDirectory() as temporary:
    temporary_dir = Path(temporary)
    replayed_lean_receipt = temporary_dir / "lean-receipt.json"
    subprocess.run(
        [
            sys.executable,
            str(LEAN_VALIDATOR),
            "--write-receipt",
            "--receipt",
            str(replayed_lean_receipt),
        ],
        cwd=ROOT,
        check=True,
    )
    assert json.loads(replayed_lean_receipt.read_text(encoding="utf-8")) == json.loads(
        LEAN_RECEIPT.read_text(encoding="utf-8")
    )

    replayed_arbitrary_depth_receipt = temporary_dir / "arbitrary-depth-receipt.json"
    subprocess.run(
        [
            sys.executable,
            str(ARBITRARY_DEPTH_VALIDATOR),
            str(ARBITRARY_DEPTH),
            "--write-receipt",
            "--receipt",
            str(replayed_arbitrary_depth_receipt),
        ],
        cwd=ROOT,
        check=True,
    )
    assert json.loads(
        replayed_arbitrary_depth_receipt.read_text(encoding="utf-8")
    ) == json.loads(ARBITRARY_DEPTH_RECEIPT.read_text(encoding="utf-8"))

    replayed_route_receipt = temporary_dir / "route-receipt.json"
    subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            str(CERTIFICATE),
            "--write-receipt",
            "--receipt",
            str(replayed_route_receipt),
        ],
        cwd=ROOT,
        check=True,
    )
    assert json.loads(replayed_route_receipt.read_text(encoding="utf-8")) == json.loads(
        RECEIPT.read_text(encoding="utf-8")
    )

certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
scope = certificate["promoted_scope"]
formalization = certificate["implementation"]["formalization"]

assert certificate["artifact_id"] == "ROUTE-PROFILES-V1-CONFORMANCE"
assert receipt["artifact_id"] == "ROUTE-PROFILES-V1-REPLAY"
assert receipt["status"] == "PASS"
assert receipt["certificate"]["content_sha256"] == certificate["content_sha256"]

# A coordinated rewrite of an old receipt digest may not hide stale source
# bindings from the promotion producer.
arbitrary_depth_receipt = json.loads(
    ARBITRARY_DEPTH_RECEIPT.read_text(encoding="utf-8")
)
stale_arbitrary_receipt = deepcopy(arbitrary_depth_receipt)
stale_arbitrary_receipt["source_closure"][str(MANUSCRIPT.relative_to(ROOT)).replace("\\", "/")] = "0" * 64
stale_arbitrary_receipt.pop("content_sha256")
stale_arbitrary_receipt["content_sha256"] = hashlib.sha256(
    json.dumps(
        stale_arbitrary_receipt, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
).hexdigest()
original_receipt_bytes = ARBITRARY_DEPTH_RECEIPT.read_bytes()
try:
    ARBITRARY_DEPTH_RECEIPT.write_text(
        json.dumps(stale_arbitrary_receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    with tempfile.TemporaryDirectory() as temporary:
        rejected = subprocess.run(
            [
                sys.executable,
                str(PROMOTER),
                "--out",
                str(Path(temporary) / "promotion.json"),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    assert rejected.returncode != 0
    assert "source closure mismatch" in (rejected.stdout + rejected.stderr)
finally:
    ARBITRARY_DEPTH_RECEIPT.write_bytes(original_receipt_bytes)
assert scope["depth_two_candidate_count"] == 45
assert scope["depth_two_zero_route_count"] == 14
assert scope["depth_three_candidate_count"] == 216
assert scope["depth_three_regime_count"] == 4
assert scope["profile_sample_primes"] == [2, 3, 5, 7, 11, 13]
assert scope["profile_max_depth"] == 5
assert scope["arbitrary_depth_semantic_classification"] == "ALL_POSITIVE_DEPTHS"
assert scope["generic_depth_profile"] == "Z_d^gen FROM INTEGRAL PREFIX-POLE EQUALITY"
assert scope["fixed_field_generating_function_status"] == "RATIONAL_TRANSFER_MATRIX_THEOREM"
assert scope["exceptional_characteristic_replay_max_depth"] == 10
assert scope["prefix_determinant_spectrum_replay_max_depth"] == 10
assert formalization["status"] == "COMPILED_PAPER_OWNED_SOURCE_CLOSURE"
assert formalization["compilation_receipt"]["artifact_id"] == (
    "ROUTE-PROFILES-LEAN-V1-COMPILED"
)
assert "complete characteristic-aware depth-three zero-route count theorem" in formalization["proof_scope"]
assert "F2/F3 exceptional enumeration and characteristic-aware depth-three histogram" not in formalization["not_claimed"]
assert "formal coverage of every manuscript theorem" in formalization["not_claimed"]
assert (
    "arbitrary-depth prefix-pole, generic profile/determinant spectrum, fixed-field automaton, rationality, stabilization, and determinant-spectrum monotonicity theorem package"
    in formalization["not_claimed"]
)
arbitrary_depth = json.loads(ARBITRARY_DEPTH.read_text(encoding="utf-8"))
assert arbitrary_depth["artifact_id"] == "ROUTE-PROFILES-ARBITRARY-DEPTH-V1"
assert [
    row["exceptional_characteristics"]
    for row in arbitrary_depth["exceptional_characteristics"]
    if row["depth"] in (3, 5, 7, 9)
] == [[2], [2, 3], [2, 3, 5], [2, 3, 5, 7]]
assert [
    row["prefix_determinant_spectrum"]
    for row in arbitrary_depth["exceptional_characteristics"]
    if row["depth"] in (3, 5, 7, 9)
] == [[1, 2], [1, 2, 3], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5, 7, 8]]
assert (
    "No logical dependence on Paper XX is promoted without explicit carrier-hypothesis registration."
    in certificate["negative_boundaries"]
)

release_receipt = json.loads(RELEASE_RECEIPT.read_text(encoding="utf-8"))
release_paths = {
    row["artifact"]["path"]
    for row in release_receipt["artifact_closure"]["ordered_artifacts"]
}
assert release_receipt["status"] == "PASS"
assert release_receipt["validation_mode"] == "LOCAL_CLOSURE_VERIFICATION"
assert release_receipt["independent_validation"] is False
assert release_receipt["artifact_closure"]["receipt_included_in_own_closure"] is False
assert str(RELEASE_RECEIPT.relative_to(ROOT)).replace("\\", "/") not in release_paths
subprocess.run(
    [sys.executable, str(RELEASE_VALIDATOR)],
    cwd=ROOT,
    check=True,
)

# Coordinated tamper: changing both the result and its digest must still fail
# the paper-owned semantic/replay contract.
tampered = deepcopy(certificate)
tampered["promoted_scope"]["depth_two_zero_route_count"] = 13
tampered.pop("content_sha256")
tampered["content_sha256"] = hashlib.sha256(
    json.dumps(tampered, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
with tempfile.TemporaryDirectory() as temporary:
    tampered_path = Path(temporary) / "tampered.json"
    tampered_path.write_text(json.dumps(tampered), encoding="utf-8")
    rejected = subprocess.run(
        [sys.executable, str(VALIDATOR), str(tampered_path)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert rejected.returncode != 0
    assert "unexpected scope field" in (rejected.stdout + rejected.stderr)

print("Paper XXI hostile controls: OK")
