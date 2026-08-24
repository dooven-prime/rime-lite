#!/usr/bin/env python3
"""Build and validate the paper-owned carrier-accessibility release receipt."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import scipy
import matplotlib


ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = ROOT / "papers" / "paper20"
EVIDENCE_DIR = ROOT / "experiments" / "paper20"
MANIFEST_PATH = EVIDENCE_DIR / "release-manifest.json"
ENVIRONMENT_PATH = EVIDENCE_DIR / "release-environment.json"
README_PATH = EVIDENCE_DIR / "README.md"
DEFAULT_RECEIPT = EVIDENCE_DIR / "results" / "carrier_accessibility_v1.release-receipt.json"
RESULT_PATHS = (
    EVIDENCE_DIR / "results" / "z2_double_regular_depth3.json",
    EVIDENCE_DIR / "results" / "s3_natural_regular_depth2.json",
    EVIDENCE_DIR / "results" / "rubik_228_depth2.json",
)
IMAGE_KERNEL_RESULT = (
    EVIDENCE_DIR
    / "results"
    / "image_kernel"
    / "rubik_depth2_shared_carrier_v1.json"
)
WITHIN_CARRIER_RESULT = (
    EVIDENCE_DIR / "results" / "within_carrier_obstruction_v1.json"
)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper20.validate_results import validate as validate_result  # noqa: E402
from experiments.paper20.validate_image_kernel import (  # noqa: E402
    validate as validate_image_kernel,
)
from experiments.paper20.validate_within_carrier_census import (  # noqa: E402
    validate as validate_within_carrier,
)


RECEIPT_SCHEMA = "paper.carrier-accessibility.release-receipt.v1"
RECEIPT_KIND = "CARRIER_ACCESSIBILITY_RELEASE_CLOSURE_RECEIPT"
RECEIPT_SCOPE = "PAPER_OWNED_RELEASE_CLOSURE_ONLY"
VALIDATOR_ID = "paper.carrier-accessibility.release-validator.python.v1"
CHECKS = [
    "release manifest constants and unique role/path registry",
    "paper-owned artifact byte and closure digests",
    "manuscript theorem and claim-boundary anchors",
    "retained census content and source-closure validation",
    "Rubik shared-carrier depth-two image-kernel audit",
    "exact one-carrier depth-two obstruction census",
    "full producer replay at receipt generation",
    "floating/exact evidence boundary",
    "formalization explicitly not required",
    "acyclic receipt exclusion and downstream exact-digest index",
]
CLAIM_BOUNDARY = {
    "certifies": (
        "the declared release bytes, source closure, retained census "
        "conformance, and producer replay under the recorded environment"
    ),
    "does_not_certify": [
        "machine-checked or independent proof of the manuscript theorems",
        "exact arithmetic for the complex128 S3 or Rubik census",
        "exact arithmetic for the retained complex128 Z2 replay",
        "frequency or genericity beyond the declared exact one-carrier model",
        "all-depth activity for endpoints with overlapping carrier support",
        "exact all-depth zero for the twelve numerically support-isolated Rubik pairs",
        "a canonical carrier decomposition or canonical sectorization",
    ],
}


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_digest(payload: dict) -> str:
    unsigned = deepcopy(payload)
    unsigned.pop("content_sha256", None)
    return hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()


def repo_path(path: Path) -> str:
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT.resolve()):
        raise ValueError(f"artifact escapes repository root: {path}")
    return resolved.relative_to(ROOT.resolve()).as_posix()


def artifact_reference(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"missing release artifact: {path}")
    return {"uri": repo_path(path), "sha256": sha256(path)}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(manifest: dict) -> None:
    expected_constants = {
        "schema": "paper.carrier-accessibility.release-manifest.v1",
        "release_id": "PAPER20-V1.0",
        "status": "PUBLISHED_RELEASE",
        "formalization_requirement": "NOT_REQUIRED",
        "environment_status": "RECORDED_NOT_REPRODUCIBLY_LOCKED",
        "result_validation_requirement": "FULL_PRODUCER_REPLAY_AT_RECEIPT_GENERATION",
    }
    for key, value in expected_constants.items():
        if manifest.get(key) != value:
            raise ValueError(f"release manifest constant changed: {key}")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("release manifest artifact registry is empty")
    roles = [item.get("role") for item in artifacts]
    paths = [item.get("path") for item in artifacts]
    if len(roles) != len(set(roles)) or len(paths) != len(set(paths)):
        raise ValueError("release manifest roles and paths must be unique")
    receipt_path = repo_path(DEFAULT_RECEIPT)
    if receipt_path in paths or any(path.endswith(".release-receipt.json") for path in paths):
        raise ValueError("a release receipt may not belong to its own artifact closure")
    if repo_path(README_PATH) in paths:
        raise ValueError("the downstream receipt index README may not enter the receipt closure")
    required_roles = {
        "manuscript",
        "paper-pdf",
        "bibliography",
        "figure-renderer",
        "figure-style-helper",
        "carrier-survivor-figure",
        "release-validator",
        "experiment-engine",
        "experiment-producer",
        "experiment-validator",
        "z2-result",
        "s3-result",
        "rubik-result",
        "image-kernel-result",
        "image-kernel-validator",
        "within-carrier-producer",
        "within-carrier-validator",
        "within-carrier-result",
        "hostile-regression",
    }
    if not required_roles <= set(roles):
        raise ValueError("release manifest is missing a required artifact role")


def ordered_artifacts(manifest: dict) -> list[dict]:
    rows = []
    for item in manifest["artifacts"]:
        path = (ROOT / item["path"]).resolve()
        rows.append({"role": item["role"], "artifact": artifact_reference(path)})
    rows.append({"role": "release-manifest", "artifact": artifact_reference(MANIFEST_PATH)})
    if any(
        row["artifact"]["uri"].endswith(".release-receipt.json") for row in rows
    ):
        raise ValueError("receipt closure contains a release receipt")
    return rows


def closure_digest(rows: list[dict]) -> str:
    return hashlib.sha256(canonical_json(rows).encode("utf-8")).hexdigest()


def result_summary(path: Path) -> dict:
    payload = load_json(path)
    depth = str(payload["max_depth_enumerated"])
    result = payload["result"]
    return {
        "model": payload["model"],
        "artifact": artifact_reference(path),
        "content_sha256": payload["content_sha256"],
        "max_depth_enumerated": payload["max_depth_enumerated"],
        "support_path_pairs": result["support_path_pair_counts"][depth],
        "carrier_path_pairs": result["carrier_path_pair_counts"][depth],
        "composition_pairs": result["composition_pair_counts"][depth],
        "claim_status": payload["claim_status"],
    }


def image_kernel_summary(path: Path) -> dict:
    payload = load_json(path)
    aggregate = payload["aggregate"]
    return {
        "artifact": artifact_reference(path),
        "content_sha256": payload["content_sha256"],
        "claim_status": payload["claim_status"],
        "enumeration_status": payload["evidence_layers"]["enumeration_certificate"]["status"],
        "numerical_status": payload["evidence_layers"]["numerical_observation"]["status"],
        "exact_zero_status": payload["evidence_layers"]["exact_zero_status"]["status"],
        "audited_depth": payload["audited_depth"],
        "pair_count": aggregate["pair_count"],
        "route_audit_count": aggregate["route_audit_count"],
        "nontrivial_image_kernel_annihilation_count": aggregate[
            "nontrivial_image_kernel_annihilation_count"
        ],
        "bounded_conclusion": aggregate["conclusion"],
        "all_depth_exact_status": aggregate["all_depth_exact_status"],
    }


def within_carrier_summary(path: Path) -> dict:
    payload = load_json(path)
    enumeration = payload["enumeration"]
    return {
        "artifact": artifact_reference(path),
        "content_sha256": payload["content_sha256"],
        "claim_status": payload["claim_status"],
        "arithmetic": payload["arithmetic"],
        "total_labelled_route_count": enumeration["total_labelled_route_count"],
        "support_candidate_count": enumeration["support_candidate_count"],
        "active_product_count": enumeration["active_product_count"],
        "strict_within_carrier_obstruction_count": enumeration[
            "strict_within_carrier_obstruction_count"
        ],
    }


def validate_manuscript() -> None:
    manuscript = (PAPER_DIR / "Paper XX.md").read_text(encoding="utf-8")
    normalized = " ".join(manuscript.split())
    required = (
        "Paper XX of the RIME program.",
        "## Abstract",
        "**Problem.**",
        "**Approach.**",
        "**Results.**",
        "**Boundary.**",
        "## Notation Table {.unnumbered}",
        "## Introduction",
        "The accompanying Rubik calculations are bounded numerical observations",
        "## Related Work and Novelty Boundary",
        "This paper does not reclaim those results",
        "Theorem 2 (All-Depth Carrier Factorization)",
        "Theorem 3 (Arbitrary-Depth Image--Kernel Criterion)",
        "Theorem 4 (Carrierwise Survivor Recursion and Promotion)",
        "Proposition 5 (Exact Four-Dimensional Z2 Witness)",
        "### Exact shared-carrier obstruction census",
        "figures/paper20/fig1_carrier_survivor_gate.png",
        "## Finite Evidence Scope and Cross-Paper Boundary",
        "## Claim Status and Boundary",
        "## Appendix A: Computational Artifacts",
        "results/carrier_accessibility_v1.release-receipt.json",
        "local closure verification**, not independent validation",
        "Paper XXI is not a corollary of the carrier factorization proved here",
        "Rubik 228-dimensional census | Computational Observation | bounded evidence; not theorem proof",
        "## Conclusion",
    )
    for anchor in required:
        if anchor not in normalized:
            raise ValueError(f"manuscript release anchor is missing: {anchor}")


RECEIPT_INDEX_START = "<!-- paper20-release-receipt-index:start -->"
RECEIPT_INDEX_END = "<!-- paper20-release-receipt-index:end -->"


def receipt_index_block(receipt_path: Path, receipt: dict) -> str:
    return "\n".join(
        (
            RECEIPT_INDEX_START,
            "## Exact Release Receipt Index",
            "",
            f"- Receipt: `{repo_path(receipt_path)}`",
            f"- Exact-file SHA-256: `{sha256(receipt_path)}`",
            f"- Receipt content SHA-256: `{receipt['content_sha256']}`",
            "- Artifact closure SHA-256: "
            f"`{receipt['artifact_closure']['closure_digest']}`",
            "- Validation mode: `LOCAL_CLOSURE_VERIFICATION`",
            "- Independent validation: `false`",
            "- Receipt included in its own closure: `false`",
            RECEIPT_INDEX_END,
        )
    )


def update_receipt_index(receipt_path: Path, receipt: dict) -> None:
    text = README_PATH.read_text(encoding="utf-8")
    start = text.find(RECEIPT_INDEX_START)
    end = text.find(RECEIPT_INDEX_END)
    if start < 0 or end < start:
        raise ValueError("README receipt-index markers are missing or out of order")
    end += len(RECEIPT_INDEX_END)
    updated = text[:start] + receipt_index_block(receipt_path, receipt) + text[end:]
    README_PATH.write_text(updated, encoding="utf-8", newline="\n")


def receipt_index_errors(receipt_path: Path, receipt: dict) -> list[str]:
    errors: list[str] = []
    closure_uris = {
        row["artifact"]["uri"] for row in receipt["artifact_closure"]["ordered_artifacts"]
    }
    if repo_path(receipt_path) in closure_uris:
        errors.append("receipt is included in its own artifact closure")
    if repo_path(README_PATH) in closure_uris:
        errors.append("downstream receipt index README is included in the receipt closure")
    expected = receipt_index_block(receipt_path, receipt)
    if expected not in README_PATH.read_text(encoding="utf-8"):
        errors.append("README exact receipt digest index is stale")
    return errors


def validate_environment_against_results(*, verify_current: bool) -> None:
    environment = load_json(ENVIRONMENT_PATH)
    if environment.get("status") != "RECORDED_DEVELOPMENT_ENVIRONMENT_NOT_INSTALLER_LOCK":
        raise ValueError("release environment overstates reproducibility")
    runtime_keys = ("python", "numpy", "scipy", "platform")
    for path in RESULT_PATHS + (IMAGE_KERNEL_RESULT,):
        runtime = load_json(path).get("runtime", {})
        for key in runtime_keys:
            if runtime.get(key) != environment.get(key):
                raise ValueError(f"{path.name}: {key} environment mismatch")
    if verify_current:
        current = {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "matplotlib": matplotlib.__version__,
            "platform": platform.platform(),
        }
        for key in runtime_keys + ("matplotlib",):
            if current[key] != environment.get(key):
                raise ValueError(f"current {key} differs from the recorded environment")


def validate_results(*, recompute: bool) -> None:
    for path in RESULT_PATHS:
        errors = validate_result(path, recompute=recompute)
        if errors:
            raise ValueError(f"{path.name}: " + "; ".join(errors))
    image_kernel_errors = validate_image_kernel(IMAGE_KERNEL_RESULT, recompute=recompute)
    if image_kernel_errors:
        raise ValueError(
            f"{IMAGE_KERNEL_RESULT.name}: " + "; ".join(image_kernel_errors)
        )
    within_carrier_errors = validate_within_carrier(WITHIN_CARRIER_RESULT)
    if within_carrier_errors:
        raise ValueError(
            f"{WITHIN_CARRIER_RESULT.name}: " + "; ".join(within_carrier_errors)
        )


def build_receipt(*, recompute_results: bool) -> dict:
    manifest = load_json(MANIFEST_PATH)
    validate_manifest(manifest)
    validate_manuscript()
    validate_environment_against_results(verify_current=recompute_results)
    validate_results(recompute=recompute_results)
    rows = ordered_artifacts(manifest)
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "release_id": manifest["release_id"],
        "receipt_id": "PAPER20-V1.0-RELEASE-CLOSURE",
        "receipt_kind": RECEIPT_KIND,
        "receipt_scope": RECEIPT_SCOPE,
        "status": "PASS",
        "artifact_closure": {
            "artifact_count": len(rows),
            "ordered_artifacts": rows,
            "closure_digest": closure_digest(rows),
        },
        "result_validation": {
            "generation_mode": "FULL_PRODUCER_REPLAY",
            "results": [result_summary(path) for path in RESULT_PATHS],
            "image_kernel_audit": image_kernel_summary(IMAGE_KERNEL_RESULT),
            "exact_within_carrier_census": within_carrier_summary(
                WITHIN_CARRIER_RESULT
            ),
        },
        "environment": artifact_reference(ENVIRONMENT_PATH),
        "formalization": {
            "required_for_release": False,
            "status": "NOT_INCLUDED",
            "boundary": "Lean formalization is optional and is not represented by this receipt.",
        },
        "validator": {
            "validator_id": VALIDATOR_ID,
            "implementation": artifact_reference(Path(__file__).resolve()),
            "validation_scope": "LOCAL_RELEASE_CLOSURE_AND_OPTIONAL_PRODUCER_REPLAY",
        },
        "checks": CHECKS,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    receipt["content_sha256"] = content_digest(receipt)
    return receipt


def receipt_errors(receipt: dict, *, recompute_results: bool = False) -> list[str]:
    errors: list[str] = []
    if receipt.get("content_sha256") != content_digest(receipt):
        errors.append("release receipt content digest mismatch")
    try:
        expected = build_receipt(recompute_results=recompute_results)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
        return errors
    if receipt != expected:
        errors.append("release receipt differs from the current paper-owned closure")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", nargs="?", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--recompute-results", action="store_true")
    args = parser.parse_args()
    if args.write_receipt:
        if not args.recompute_results:
            parser.error("--write-receipt requires --recompute-results")
        receipt = build_receipt(recompute_results=True)
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        update_receipt_index(args.receipt, receipt)
    if not args.receipt.is_file():
        print(f"FAIL missing release receipt: {args.receipt}")
        return 1
    receipt = load_json(args.receipt)
    errors = receipt_errors(receipt, recompute_results=args.recompute_results)
    if args.receipt.resolve() == DEFAULT_RECEIPT.resolve():
        errors.extend(receipt_index_errors(args.receipt, receipt))
    if errors:
        print(f"FAIL {args.receipt}")
        for error in errors:
            print(f"  - {error}")
        return 1
    replay = " with full producer replay" if args.recompute_results else ""
    print(f"PASS {receipt['receipt_id']}: {len(CHECKS)} checks{replay}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
