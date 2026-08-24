#!/usr/bin/env python3
"""Build the paper-owned route-profile promotion certificate.

Exploratory bundles remain provenance inputs. The promoted certificate is
rebuilt from the frozen producers and source JSON, and receives a new digest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "experiments" / "exploratory" / "carrier_realizations" / "fuchsian_schreier"
EVIDENCE_DIR = ROOT / "experiments" / "paper21"
RESULTS_DIR = EVIDENCE_DIR / "results"
CERTIFICATE_PATH = RESULTS_DIR / "route_profile_promotion_v1.json"
DEPTH2_PATH = SOURCE_DIR / "results" / "uniform_modular_zero_route_classification_v1.json"
DEPTH3_PATH = SOURCE_DIR / "results" / "depth_three_zero_route_classification_v1.json"
PROFILE_PATH = SOURCE_DIR / "results" / "uniform_finite_field_route_profile_v1.json"
MANUSCRIPT_PATH = ROOT / "papers" / "paper21" / "Paper XXI.md"
LEAN_ROOT = EVIDENCE_DIR / "lean"
LEAN_ENTRYPOINT = LEAN_ROOT / "FiniteFieldRouteProfiles.lean"
LEAN_MANIFEST = LEAN_ROOT / "formalization-manifest.json"
LEAN_RECEIPT = RESULTS_DIR / "route_profiles_lean_v1.validation-receipt.json"
ARBITRARY_DEPTH_PATH = RESULTS_DIR / "arbitrary_depth_semantic_v1.json"
ARBITRARY_DEPTH_RECEIPT = RESULTS_DIR / "arbitrary_depth_semantic_v1.validation-receipt.json"
ARBITRARY_DEPTH_PRODUCER = EVIDENCE_DIR / "arbitrary_depth_semantic.py"
ARBITRARY_DEPTH_VALIDATOR = EVIDENCE_DIR / "validation" / "validate_arbitrary_depth_semantic.py"
VALIDATOR_PATH = EVIDENCE_DIR / "validation" / "validate_route_profiles.py"
LEAN_VALIDATOR_PATH = EVIDENCE_DIR / "validation" / "validate_lean_formalization.py"

if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from core import canonical_json, content_digest  # noqa: E402
from depth_three_zero_route_classification import build_payload as build_depth_three  # noqa: E402
from uniform_finite_field_route_profile import build_payload as build_profile  # noqa: E402
from uniform_modular_zero_route_classification import build_payload as build_depth_two  # noqa: E402


SCHEMA = "paper.route-profiles.promotion.v1"
PRODUCER_ID = "paper.route-profiles.promotion.python.v1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_lean_receipt() -> dict:
    receipt = load(LEAN_RECEIPT)
    unsigned = deepcopy(receipt)
    supplied_digest = unsigned.pop("content_sha256", None)
    if not isinstance(supplied_digest, str) or content_digest(unsigned) != supplied_digest:
        raise AssertionError("Lean compilation receipt digest mismatch")
    if receipt.get("status") != "PASS":
        raise AssertionError("Lean compilation receipt is not PASS")
    if receipt.get("artifact_id") != "ROUTE-PROFILES-LEAN-V1-COMPILED":
        raise AssertionError("unexpected Lean compilation receipt role")
    manifest = load(LEAN_MANIFEST)
    expected_sources = {
        relative(LEAN_ROOT / source): sha256(LEAN_ROOT / source)
        for source in manifest["source_sha256"]
    }
    expected_sources[relative(LEAN_MANIFEST)] = sha256(LEAN_MANIFEST)
    if receipt.get("source_closure") != expected_sources:
        raise AssertionError("Lean compilation receipt source closure mismatch")
    return receipt


def validate_arbitrary_depth_receipt() -> tuple[dict, dict]:
    artifact = load(ARBITRARY_DEPTH_PATH)
    unsigned_artifact = deepcopy(artifact)
    supplied_artifact_digest = unsigned_artifact.pop("content_sha256", None)
    if (
        not isinstance(supplied_artifact_digest, str)
        or content_digest(unsigned_artifact) != supplied_artifact_digest
    ):
        raise AssertionError("arbitrary-depth artifact digest mismatch")
    receipt = load(ARBITRARY_DEPTH_RECEIPT)
    unsigned_receipt = deepcopy(receipt)
    supplied_receipt_digest = unsigned_receipt.pop("content_sha256", None)
    if (
        not isinstance(supplied_receipt_digest, str)
        or content_digest(unsigned_receipt) != supplied_receipt_digest
    ):
        raise AssertionError("arbitrary-depth receipt digest mismatch")
    if receipt.get("status") != "PASS":
        raise AssertionError("arbitrary-depth receipt is not PASS")
    if receipt.get("artifact_id") != "ROUTE-PROFILES-ARBITRARY-DEPTH-V1-REPLAY":
        raise AssertionError("unexpected arbitrary-depth receipt role")
    artifact_ref = receipt.get("artifact", {})
    if artifact_ref.get("artifact_sha256") != sha256(ARBITRARY_DEPTH_PATH):
        raise AssertionError("arbitrary-depth artifact byte digest mismatch")
    if artifact_ref.get("content_sha256") != artifact["content_sha256"]:
        raise AssertionError("arbitrary-depth content digest is not receipt-bound")
    expected_source_closure = {
        relative(ARBITRARY_DEPTH_PRODUCER): sha256(ARBITRARY_DEPTH_PRODUCER),
        relative(ARBITRARY_DEPTH_VALIDATOR): sha256(ARBITRARY_DEPTH_VALIDATOR),
        relative(MANUSCRIPT_PATH): sha256(MANUSCRIPT_PATH),
    }
    if receipt.get("source_closure") != expected_source_closure:
        raise AssertionError("arbitrary-depth receipt source closure mismatch")
    return artifact, receipt


def source_descriptor(path: Path, payload: dict) -> dict:
    return {
        "path": relative(path),
        "schema": payload["schema"],
        "bundle_id": payload["bundle_id"],
        "artifact_sha256": sha256(path),
        "content_sha256": payload.get("content_sha256"),
        "content_digest_status": (
            "PRESENT" if payload.get("content_sha256") else "LEGACY_NOT_EMITTED"
        ),
        "upstream_paper_evidence_status": payload["paper_evidence_status"],
        "promotion_role": "SOURCE_PROVENANCE_AND_REPLAY_INPUT",
    }


def implementation_closure() -> dict:
    files = {
        relative(Path(__file__).resolve()): sha256(Path(__file__).resolve()),
        relative(VALIDATOR_PATH): sha256(VALIDATOR_PATH),
        relative(LEAN_VALIDATOR_PATH): sha256(LEAN_VALIDATOR_PATH),
        relative(SOURCE_DIR / "core.py"): sha256(SOURCE_DIR / "core.py"),
        relative(SOURCE_DIR / "uniform_modular_zero_route_classification.py"): sha256(
            SOURCE_DIR / "uniform_modular_zero_route_classification.py"
        ),
        relative(SOURCE_DIR / "depth_three_zero_route_classification.py"): sha256(
            SOURCE_DIR / "depth_three_zero_route_classification.py"
        ),
        relative(SOURCE_DIR / "uniform_finite_field_route_profile.py"): sha256(
            SOURCE_DIR / "uniform_finite_field_route_profile.py"
        ),
        relative(ARBITRARY_DEPTH_PRODUCER): sha256(ARBITRARY_DEPTH_PRODUCER),
        relative(ARBITRARY_DEPTH_VALIDATOR): sha256(ARBITRARY_DEPTH_VALIDATOR),
    }
    lean_receipt = validate_lean_receipt()
    formalization_files = lean_receipt["source_closure"]
    arbitrary_depth, arbitrary_depth_receipt = validate_arbitrary_depth_receipt()
    return {
        "producer_id": PRODUCER_ID,
        "language": "Python",
        "arithmetic": "exact finite permutations, prime fields, polynomial extension fields, and Python integers",
        "files": files,
        "implementation_sha256": content_digest(files),
        "formalization": {
            "status": "COMPILED_PAPER_OWNED_SOURCE_CLOSURE",
            "language": "Lean",
            "entrypoint": relative(LEAN_ENTRYPOINT),
            "manifest": relative(LEAN_MANIFEST),
            "files": formalization_files,
            "formalization_sha256": content_digest(formalization_files),
            "compilation_receipt": {
                "path": relative(LEAN_RECEIPT),
                "artifact_id": lean_receipt["artifact_id"],
                "artifact_sha256": sha256(LEAN_RECEIPT),
                "content_sha256": lean_receipt["content_sha256"],
            },
            "proof_scope": [
                "complete depth-two finite-field semantic classification",
                "arbitrary-depth Boolean candidate count",
                "depth-three supported-shape enumeration",
                "all eight depth-three semantic shape criteria",
                "all-finite depth-three witness for field cardinality at least four",
                "F2/F3 exact finite exceptional enumeration",
                "general characteristic-aware first-seven-shape count",
                "complete characteristic-aware depth-three zero-route count theorem",
            ],
            "not_claimed": [
                "arbitrary-depth prefix-pole, generic profile/determinant spectrum, fixed-field automaton, rationality, stabilization, and determinant-spectrum monotonicity theorem package",
                "formal coverage of every manuscript theorem",
            ],
        },
        "arbitrary_depth_replay": {
            "status": "PAPER_OWNED_EXACT_REPLAY_NOT_INDEPENDENT_PROOF",
            "artifact": {
                "path": relative(ARBITRARY_DEPTH_PATH),
                "artifact_id": arbitrary_depth["artifact_id"],
                "artifact_sha256": sha256(ARBITRARY_DEPTH_PATH),
                "content_sha256": arbitrary_depth["content_sha256"],
            },
            "receipt": {
                "path": relative(ARBITRARY_DEPTH_RECEIPT),
                "artifact_id": arbitrary_depth_receipt["artifact_id"],
                "artifact_sha256": sha256(ARBITRARY_DEPTH_RECEIPT),
                "content_sha256": arbitrary_depth_receipt["content_sha256"],
            },
            "proof_owner": "MANUSCRIPT",
        },
    }


def assert_source_status(payload: dict, expected_schema: str) -> None:
    if payload.get("schema") != expected_schema:
        raise AssertionError(f"unexpected source schema: {payload.get('schema')}")
    if payload.get("paper_evidence_status") != "NOT_PROMOTED":
        raise AssertionError("source artifact is not exploratory-only")


def replay_source_artifacts() -> tuple[dict, dict, dict]:
    depth2 = load(DEPTH2_PATH)
    depth3 = load(DEPTH3_PATH)
    profile = load(PROFILE_PATH)
    assert_source_status(depth2, "rime.exploratory.fuchsian-schreier.uniform-modular-zero-route-classification.v1")
    assert_source_status(depth3, "rime.exploratory.fuchsian-schreier.depth-three-zero-route-classification.v1")
    assert_source_status(profile, "rime.exploratory.fuchsian-schreier.uniform-finite-field-route-profile.v1")
    depth2_primes = [item["prime"] for item in depth2["exact_replay_checks"]]
    rebuilt2 = build_depth_two(depth2_primes)
    # The depth-two source predates top-level content digests; compare its
    # semantic payload and exact replay flags rather than inventing a digest.
    if canonical_json(depth2) != canonical_json(rebuilt2):
        raise AssertionError("depth-two source replay mismatch")
    rebuilt3 = build_depth_three()
    rebuilt_profile = build_profile([2, 3, 5, 7, 11, 13], 5)
    for name, source, rebuilt in (
        ("depth-three", depth3, rebuilt3),
        ("fixed-depth profile", profile, rebuilt_profile),
    ):
        unsigned = deepcopy(source)
        supplied = unsigned.pop("content_sha256")
        if content_digest(unsigned) != supplied:
            raise AssertionError(f"{name} source digest mismatch")
        rebuilt["content_sha256"] = supplied
        if canonical_json(source) != canonical_json(rebuilt):
            raise AssertionError(f"{name} source replay mismatch")
    return depth2, depth3, profile


def validate_fixed_depth_semantic_bridge(profile: dict, arbitrary_depth: dict) -> None:
    semantic_records = {
        record["prime"]: record["profiles"]
        for record in arbitrary_depth["fixed_depth_signature_bridge"]["profiles"]
    }
    for source_record in profile["records"]:
        prime = source_record["prime"]
        semantic_profiles = semantic_records.get(prime)
        if semantic_profiles is None:
            raise AssertionError(f"missing arbitrary-depth bridge for p={prime}")
        for source_depth, semantic_depth in zip(
            source_record["profiles_by_depth"], semantic_profiles, strict=True
        ):
            expected = {
                "depth": source_depth["depth"],
                "candidate_count": source_depth["supported_route_candidate_count"],
                "nonzero_count": source_depth["nonzero_routed_product_count"],
                "zero_count": source_depth["zero_routed_product_count"],
                "zero_route_signature": source_depth["zero_route_signature"],
            }
            if semantic_depth != expected:
                raise AssertionError(
                    f"fixed-depth semantic bridge mismatch: p={prime}, "
                    f"depth={source_depth['depth']}"
                )


def build_certificate() -> dict:
    depth2, depth3, profile = replay_source_artifacts()
    arbitrary_depth, _ = validate_arbitrary_depth_receipt()
    validate_fixed_depth_semantic_bridge(profile, arbitrary_depth)
    depth2_primes = [item["prime"] for item in depth2["exact_replay_checks"]]
    manuscript = " ".join(MANUSCRIPT_PATH.read_text(encoding="utf-8").split())
    for anchor in (
        "Theorem 4.2: Characteristic-Aware Count",
        "Theorem 5.1: Arbitrary-Depth Prefix-Pole Classification",
        "Generic Depth-$d$ Profile",
        "Theorem 5.5: Fixed-Depth Large-Field Stabilization",
        "The Lean receipt binds only the formalized surface listed in Section 8",
        "It does not cover the arbitrary-depth prefix-pole theorem, fixed-field automata and rationality, the generic profile, or fixed-depth stabilization and determinant-spectrum monotonicity",
        "this paper is not a corollary, specialization, or application of Paper XX",
    ):
        if anchor not in manuscript:
            raise AssertionError(f"manuscript anchor is missing: {anchor}")
    certificate = {
        "schema": SCHEMA,
        "certificate_id": "paper.route-profiles.promotion.v1",
        "artifact_id": "ROUTE-PROFILES-V1-CONFORMANCE",
        "paper": "Paper XXI: Uniform Finite-Field Route Profiles",
        "release_status": "PAPER_XXI_V1_RELEASE_EVIDENCE",
        "artifact_role": "PAPER_OWNED_PROMOTED_ROUTE_PROFILE_CERTIFICATE",
        "claim_status": "Exact theorem layers plus Computational Certificate layer",
        "theorem_relationship": "CERTIFICATE_REPLAYS_SOURCE_AND_DOES_NOT_REPLACE_PROOF",
        "promotion_decision": "ACCEPTED_FOR_PAPER_XXI_V1_EVIDENCE_CLOSURE",
        "manuscript": {
            "path": relative(MANUSCRIPT_PATH),
            "sha256": sha256(MANUSCRIPT_PATH),
        },
        "source_artifacts": [
            source_descriptor(DEPTH2_PATH, depth2),
            source_descriptor(DEPTH3_PATH, depth3),
            source_descriptor(PROFILE_PATH, profile),
        ],
        "implementation": implementation_closure(),
        "promoted_scope": {
            "depth_two_candidate_count": 45,
            "depth_two_zero_route_count": 14,
            "depth_two_field_condition": "finite fields of cardinality at least 3",
            "depth_two_legacy_replay_primes": depth2_primes,
            "depth_three_candidate_count": 216,
            "depth_three_regime_count": 4,
            "profile_sample_primes": [2, 3, 5, 7, 11, 13],
            "profile_max_depth": 5,
            "arbitrary_depth_semantic_classification": "ALL_POSITIVE_DEPTHS",
            "generic_depth_profile": "Z_d^gen FROM INTEGRAL PREFIX-POLE EQUALITY",
            "fixed_field_generating_function_status": "RATIONAL_TRANSFER_MATRIX_THEOREM",
            "stabilization_condition": "field cardinality greater than depth and characteristic outside E_d",
            "exceptional_characteristic_replay_max_depth": 10,
            "prefix_determinant_spectrum_replay_max_depth": 10,
        },
        "promoted_claims": [
            {"claim_id": "RPF-V1-THM-02", "statement": "Depth-two fixed-contract zero-route classification is 14/45 for every finite field of cardinality at least 3.", "status": "EXACT_THEOREM_SOURCE_REPLAYED"},
            {"claim_id": "RPF-V1-THM-03", "statement": "Depth-three zero-route counts split into four characteristic/cardinality regimes under the declared contract.", "status": "EXACT_THEOREM_SOURCE_REPLAYED"},
            {"claim_id": "RPF-V1-PROFILE", "statement": "The sampled fixed-depth route profiles are replayable exact finite computation under the declared source closure.", "status": "COMPUTATIONAL_CERTIFICATE"},
            {"claim_id": "RPF-V1-CANDIDATES", "statement": "The supported candidate count has the exact formula B_d = 3^d F_(d+3).", "status": "EXACT_COMBINATORIAL_PROPOSITION"},
            {"claim_id": "RPF-V1-PREFIX-POLE", "statement": "Every arbitrary-depth route survivor set is exactly classified by its forced and forbidden prefix poles.", "status": "EXACT_MANUSCRIPT_THEOREM_WITH_PAPER_OWNED_REPLAY"},
            {"claim_id": "RPF-V1-GENERIC", "statement": "The generic depth-d zero-route profile is determined by the integral prefix-pole equality relation and the pole-class count identity.", "status": "EXACT_MANUSCRIPT_THEOREM_WITH_DETERMINANT_SPECTRUM_REPLAY"},
            {"claim_id": "RPF-V1-RATIONALITY", "statement": "For each fixed finite field, candidate, nonzero, and zero-route counts have rational reachable-subset transfer series.", "status": "EXACT_MANUSCRIPT_THEOREM_WITH_PAPER_OWNED_CONSTRUCTION"},
            {"claim_id": "RPF-V1-STABILIZATION", "statement": "At fixed depth d, the complete labelled zero-route set equals Z_d^gen for |F|>d outside the finite exceptional characteristic set E_d.", "status": "EXACT_MANUSCRIPT_THEOREM_WITH_EXCEPTIONAL_SET_REPLAY"},
            {"claim_id": "RPF-V1-MONOTONICITY", "statement": "Prefix determinant spectra and exceptional-characteristic sets are monotone under depth extension.", "status": "EXACT_MANUSCRIPT_COROLLARY_FROM_PREFIX_EXTENSION"},
        ],
        "negative_boundaries": [
            "No abstract presentation-only invariance is promoted.",
            "No arbitrary representation or marked-partition invariance is promoted.",
            "No logical dependence on Paper XX is promoted without explicit carrier-hypothesis registration.",
            "No field-independent finite automaton, uniform state bound, or single rational function for every field is promoted.",
            "No all-depth closed scalar zero-count formula, depth-asymptotic convergence, or growth constant is promoted.",
            "A zero route is not a spectral zero mode or operator-kernel theorem.",
            "No RG, Hecke, modular-form, Selberg, Teichmuller, or causal claim is promoted.",
            "The exploratory source bundles remain provenance inputs, not paper-owned theorem proofs.",
        ],
    }
    certificate["content_sha256"] = content_digest(certificate)
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=CERTIFICATE_PATH)
    args = parser.parse_args()
    certificate = build_certificate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"artifact_id": certificate["artifact_id"], "content_sha256": certificate["content_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
