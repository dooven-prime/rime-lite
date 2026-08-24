#!/usr/bin/env python3
"""Validate the Paper XXI release closure without mutating tracked inputs."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_DIR = ROOT / "experiments" / "paper21"
RESULTS_DIR = EVIDENCE_DIR / "results"
MANIFEST_PATH = EVIDENCE_DIR / "release-manifest.json"
ENVIRONMENT_PATH = EVIDENCE_DIR / "release-environment.json"
README_PATH = EVIDENCE_DIR / "README.md"
MANUSCRIPT_PATH = ROOT / "papers" / "paper21" / "Paper XXI.md"
DEFAULT_RECEIPT = RESULTS_DIR / "route_profiles_v1.release-receipt.json"
ARBITRARY_RESULT = RESULTS_DIR / "arbitrary_depth_semantic_v1.json"
ARBITRARY_RECEIPT = RESULTS_DIR / "arbitrary_depth_semantic_v1.validation-receipt.json"
PROMOTION_RESULT = RESULTS_DIR / "route_profile_promotion_v1.json"
PROMOTION_RECEIPT = RESULTS_DIR / "route_profile_promotion_v1.validation-receipt.json"
LEAN_RECEIPT = RESULTS_DIR / "route_profiles_lean_v1.validation-receipt.json"
LEAN_ROOT = EVIDENCE_DIR / "lean"
LEAN_MANIFEST = LEAN_ROOT / "formalization-manifest.json"

RECEIPT_SCHEMA = "paper.route-profiles.release-receipt.v1"
RECEIPT_KIND = "ROUTE_PROFILES_RELEASE_CLOSURE_RECEIPT"
RECEIPT_SCOPE = "PAPER_OWNED_RELEASE_CLOSURE_LOCAL_VERIFICATION_ONLY"
VALIDATOR_ID = "paper.route-profiles.release-validator.python.v1"
INDEX_START = "<!-- paper21-release-receipt-index:start -->"
INDEX_END = "<!-- paper21-release-receipt-index:end -->"

CHECKS = [
    "release manifest identity and unique role/path registry",
    "exact ordered artifact byte closure",
    "acyclic evidence references and release-receipt self-exclusion",
    "manuscript structure, theorem, and claim-boundary anchors",
    "arbitrary-depth artifact and source-closure receipt",
    "promoted route-profile certificate and replay receipt",
    "pinned Lean source closure and compilation receipt",
    "claim-surface map conformance",
    "exact-arithmetic and formalization-scope boundaries",
    "full component replay at receipt generation",
]


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_digest(payload: dict) -> str:
    unsigned = deepcopy(payload)
    unsigned.pop("content_sha256", None)
    return hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def repo_path(path: Path) -> str:
    resolved = path.resolve()
    root = ROOT.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"path escapes repository root: {path}")
    return resolved.relative_to(root).as_posix()


def artifact_reference(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"missing release artifact: {path}")
    return {"path": repo_path(path), "sha256": sha256(path)}


def validate_content_digest(payload: dict, label: str) -> None:
    if payload.get("content_sha256") != content_digest(payload):
        raise ValueError(f"{label} content digest mismatch")


def validate_manifest(manifest: dict) -> None:
    expected = {
        "schema": "paper.route-profiles.release-manifest.v1",
        "release_id": "PAPER21-V1.0",
        "status": "PUBLISHED_RELEASE",
        "formalization_requirement": "PINNED_COMPILED_SUBSET_REQUIRED",
        "result_validation_requirement": "FULL_COMPONENT_REPLAY_AT_RECEIPT_GENERATION",
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise ValueError(f"release manifest constant changed: {key}")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("release manifest artifact registry is empty")
    roles = [item.get("role") for item in artifacts]
    paths = [item.get("path") for item in artifacts]
    if len(roles) != len(set(roles)) or len(paths) != len(set(paths)):
        raise ValueError("release manifest roles and paths must be unique")
    if any(not isinstance(path, str) or Path(path).is_absolute() for path in paths):
        raise ValueError("release manifest paths must be repository-relative")
    if repo_path(DEFAULT_RECEIPT) in paths:
        raise ValueError("release receipt may not belong to its own closure")
    if repo_path(README_PATH) in paths:
        raise ValueError("downstream receipt index may not enter the closure")
    required_roles = {
        "line-ending-policy",
        "manuscript",
        "paper-pdf",
        "bibliography",
        "prefix-pole-figure",
        "release-environment",
        "release-validator",
        "claim-surface-map",
        "claim-surface-validator",
        "arbitrary-depth-producer",
        "arbitrary-depth-validator",
        "arbitrary-depth-result",
        "arbitrary-depth-receipt",
        "promotion-producer",
        "promotion-validator",
        "promotion-result",
        "promotion-receipt",
        "lean-validator",
        "lean-entrypoint",
        "lean-depth-two-module",
        "lean-depth-three-module",
        "lean-formalization-manifest",
        "lean-compilation-receipt",
        "hostile-regression",
    }
    if not required_roles <= set(roles):
        missing = sorted(required_roles - set(roles))
        raise ValueError(f"release manifest is missing required roles: {missing}")


def ordered_artifacts(manifest: dict) -> list[dict]:
    rows = []
    for item in manifest["artifacts"]:
        path = (ROOT / item["path"]).resolve()
        rows.append({"role": item["role"], "artifact": artifact_reference(path)})
    rows.append({"role": "release-manifest", "artifact": artifact_reference(MANIFEST_PATH)})
    if any(row["artifact"]["path"] == repo_path(DEFAULT_RECEIPT) for row in rows):
        raise ValueError("release receipt entered its own ordered closure")
    return rows


def closure_digest(rows: list[dict]) -> str:
    return hashlib.sha256(canonical_json(rows).encode("utf-8")).hexdigest()


def nested_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for child in value for item in nested_strings(child)]
    if isinstance(value, dict):
        keys = [key for key in value if isinstance(key, str)]
        values = [item for child in value.values() for item in nested_strings(child)]
        return keys + values
    return []


def validate_evidence_dag(manifest: dict) -> None:
    paths = {item["path"] for item in manifest["artifacts"]}
    release_receipt_path = repo_path(DEFAULT_RECEIPT)
    graph: dict[str, set[str]] = {path: set() for path in paths}
    for path in paths:
        artifact = ROOT / path
        if artifact.suffix != ".json":
            continue
        payload = load_json(artifact)
        strings = set(nested_strings(payload))
        if path in strings:
            raise ValueError(f"artifact directly references itself: {path}")
        if release_receipt_path in strings:
            raise ValueError(f"forward dependency on release receipt: {path}")
        undeclared = sorted(
            candidate
            for candidate in strings
            if "/" in candidate
            and (ROOT / candidate).is_file()
            and candidate not in paths
            and candidate != repo_path(README_PATH)
        )
        if undeclared:
            raise ValueError(
                f"JSON artifact has undeclared repository references: {path}: {undeclared}"
            )
        graph[path] = strings & paths

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise ValueError(f"cycle in release evidence graph at {node}")
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph[node]:
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)


def validate_manuscript() -> None:
    manuscript = " ".join(MANUSCRIPT_PATH.read_text(encoding="utf-8").split())
    required = (
        "Paper XXI of the RIME program.",
        "## Abstract",
        "**Problem.**",
        "**Approach.**",
        "**Results.**",
        "**Boundary.**",
        "## Notation Table {.unnumbered}",
        "## Introduction",
        "figures/paper21/fig1_prefix_pole_semantics.png",
        "## Related Work and Novelty Boundary {.unnumbered}",
        "this paper is not a corollary, specialization, or application of Paper XX",
        "Theorem 3.2: Uniform Modular Zero-Route Classification",
        "Theorem 4.2: Characteristic-Aware Count",
        "Theorem 5.1: Arbitrary-Depth Prefix-Pole Classification",
        "Corollary 5.2: Fixed-Field Survivor Automaton",
        "Proposition 5.4: Boolean Candidate Count",
        "Theorem 5.5: Fixed-Depth Large-Field Stabilization",
        "Corollary 5.6: Monotonicity of Exceptional Characteristics",
        "## Computational Evidence",
        "## Claim Status and Boundary",
        "No Computational Observation is promoted by this paper",
        "## Appendix A: Computational Artifacts {.unnumbered}",
        "local closure verification, not independent validation",
        "It does not cover the arbitrary-depth prefix-pole theorem",
    )
    for anchor in required:
        if anchor not in manuscript:
            raise ValueError(f"manuscript release anchor is missing: {anchor}")


def validate_environment(*, verify_current: bool) -> None:
    environment = load_json(ENVIRONMENT_PATH)
    expected = {
        "python": "3.13.0",
        "lean": "4.33.0",
        "lake": "5.0.0",
        "lean_toolchain": "leanprover/lean4:v4.33.0",
        "mathlib_revision": "db584cd6d46c92f209a44c0f1c829460d327499d",
        "status": "PINNED_FORMAL_TOOLCHAIN_AND_RECORDED_PYTHON_ENVIRONMENT",
    }
    for key, value in expected.items():
        if environment.get(key) != value:
            raise ValueError(f"release environment changed: {key}")
    if verify_current:
        if platform.python_version() != environment["python"]:
            raise ValueError("current Python differs from the recorded release environment")
        if platform.platform() != environment["platform"]:
            raise ValueError("current platform differs from the recorded release environment")


def validate_arbitrary_receipt() -> dict:
    artifact = load_json(ARBITRARY_RESULT)
    receipt = load_json(ARBITRARY_RECEIPT)
    validate_content_digest(artifact, "arbitrary-depth artifact")
    validate_content_digest(receipt, "arbitrary-depth receipt")
    if receipt.get("status") != "PASS":
        raise ValueError("arbitrary-depth receipt is not PASS")
    artifact_ref = receipt.get("artifact", {})
    if artifact_ref.get("path") != repo_path(ARBITRARY_RESULT):
        raise ValueError("arbitrary-depth receipt artifact path mismatch")
    if artifact_ref.get("artifact_sha256") != sha256(ARBITRARY_RESULT):
        raise ValueError("arbitrary-depth receipt artifact byte digest mismatch")
    expected_sources = {
        repo_path(EVIDENCE_DIR / "arbitrary_depth_semantic.py"): sha256(EVIDENCE_DIR / "arbitrary_depth_semantic.py"),
        repo_path(EVIDENCE_DIR / "validation" / "validate_arbitrary_depth_semantic.py"): sha256(EVIDENCE_DIR / "validation" / "validate_arbitrary_depth_semantic.py"),
        repo_path(MANUSCRIPT_PATH): sha256(MANUSCRIPT_PATH),
    }
    if receipt.get("source_closure") != expected_sources:
        raise ValueError("arbitrary-depth receipt source closure mismatch")
    return receipt


def validate_lean_receipt() -> dict:
    manifest = load_json(LEAN_MANIFEST)
    receipt = load_json(LEAN_RECEIPT)
    validate_content_digest(receipt, "Lean receipt")
    expected_sources = {
        repo_path(LEAN_ROOT / source): sha256(LEAN_ROOT / source)
        for source in manifest.get("source_sha256", {})
    }
    expected_sources[repo_path(LEAN_MANIFEST)] = sha256(LEAN_MANIFEST)
    if receipt.get("source_closure") != expected_sources:
        raise ValueError("Lean receipt source closure mismatch")
    if receipt.get("status") != "PASS" or receipt.get("artifact_id") != "ROUTE-PROFILES-LEAN-V1-COMPILED":
        raise ValueError("Lean compilation receipt identity or status mismatch")
    return receipt


def validate_promotion_receipt() -> dict:
    certificate = load_json(PROMOTION_RESULT)
    receipt = load_json(PROMOTION_RECEIPT)
    validate_content_digest(certificate, "promotion certificate")
    validate_content_digest(receipt, "promotion receipt")
    if receipt.get("status") != "PASS":
        raise ValueError("promotion receipt is not PASS")
    certificate_ref = receipt.get("certificate", {})
    if certificate_ref.get("path") != repo_path(PROMOTION_RESULT):
        raise ValueError("promotion receipt certificate path mismatch")
    if certificate_ref.get("artifact_sha256") != sha256(PROMOTION_RESULT):
        raise ValueError("promotion receipt certificate byte digest mismatch")
    if certificate_ref.get("content_sha256") != certificate.get("content_sha256"):
        raise ValueError("promotion receipt certificate content digest mismatch")
    if certificate.get("manuscript", {}).get("sha256") != sha256(MANUSCRIPT_PATH):
        raise ValueError("promotion certificate manuscript binding mismatch")
    return receipt


def run_check(command: list[str], label: str) -> None:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode:
        raise ValueError(f"{label} failed:\n{completed.stdout}{completed.stderr}")


def validate_components(*, recompute: bool, recompute_lean: bool) -> None:
    validate_arbitrary_receipt()
    validate_promotion_receipt()
    validate_lean_receipt()
    run_check(
        [sys.executable, "tools/research/validate_claim_surface.py", "experiments/paper21/claim-surface-map.json"],
        "claim-surface validation",
    )
    if recompute:
        run_check(
            [sys.executable, "experiments/paper21/validation/validate_arbitrary_depth_semantic.py"],
            "arbitrary-depth replay",
        )
        run_check(
            [sys.executable, "experiments/paper21/validation/validate_route_profiles.py"],
            "route-profile replay",
        )
    if recompute_lean:
        run_check(
            [sys.executable, "experiments/paper21/validation/validate_lean_formalization.py"],
            "Lean compilation replay",
        )


def component_summary(path: Path) -> dict:
    payload = load_json(path)
    return {
        "artifact": artifact_reference(path),
        "content_sha256": payload["content_sha256"],
        "receipt_kind": payload["receipt_kind"],
        "receipt_scope": payload["receipt_scope"],
        "status": payload["status"],
    }


def build_receipt(*, recompute_components: bool, recompute_lean: bool) -> dict:
    manifest = load_json(MANIFEST_PATH)
    validate_manifest(manifest)
    validate_evidence_dag(manifest)
    validate_manuscript()
    validate_environment(verify_current=recompute_components or recompute_lean)
    validate_components(recompute=recompute_components, recompute_lean=recompute_lean)
    rows = ordered_artifacts(manifest)
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "release_id": manifest["release_id"],
        "receipt_id": "PAPER21-V1.0-RELEASE-CLOSURE",
        "receipt_kind": RECEIPT_KIND,
        "receipt_scope": RECEIPT_SCOPE,
        "status": "PASS",
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "independent_validation": False,
        "artifact_closure": {
            "artifact_count": len(rows),
            "ordered_artifacts": rows,
            "closure_digest": closure_digest(rows),
            "receipt_included_in_own_closure": False,
        },
        "component_receipts": [
            component_summary(ARBITRARY_RECEIPT),
            component_summary(PROMOTION_RECEIPT),
            component_summary(LEAN_RECEIPT),
        ],
        "formalization": {
            "status": "PINNED_COMPILED_SUBSET",
            "covered_surface": "Theorem 3.2, Theorems 4.1--4.2, Proposition 5.4, and their declared supporting lemmas",
            "excluded_surface": "Theorem 5.1, Corollaries 5.2--5.3 and 5.6, and Theorem 5.5",
        },
        "validator": {
            "validator_id": VALIDATOR_ID,
            "implementation": artifact_reference(Path(__file__).resolve()),
        },
        "checks": CHECKS,
        "claim_boundary": {
            "certifies": "exact release bytes, component receipt bindings, declared replay, and pinned Lean compilation for the listed subset",
            "does_not_certify": [
                "independent validation or scientific truth",
                "Lean coverage of every manuscript theorem",
                "a field-independent finite automaton or uniform state bound",
                "an all-depth scalar zero-count formula or asymptotic growth law",
                "logical dependence on Paper XX",
            ],
        },
    }
    receipt["content_sha256"] = content_digest(receipt)
    return receipt


def receipt_index_block(receipt_path: Path, receipt: dict) -> str:
    return "\n".join(
        (
            INDEX_START,
            "## Exact Release Receipt Index",
            "",
            f"- Receipt: `{repo_path(receipt_path)}`",
            f"- Exact-file SHA-256: `{sha256(receipt_path)}`",
            f"- Receipt content SHA-256: `{receipt['content_sha256']}`",
            f"- Artifact closure SHA-256: `{receipt['artifact_closure']['closure_digest']}`",
            "- Validation mode: `LOCAL_CLOSURE_VERIFICATION`",
            "- Independent validation: `false`",
            "- Receipt included in its own closure: `false`",
            INDEX_END,
        )
    )


def update_receipt_index(receipt_path: Path, receipt: dict) -> None:
    text = README_PATH.read_text(encoding="utf-8")
    start = text.find(INDEX_START)
    end = text.find(INDEX_END)
    if start < 0 or end < start:
        raise ValueError("README receipt-index markers are missing or out of order")
    end += len(INDEX_END)
    updated = text[:start] + receipt_index_block(receipt_path, receipt) + text[end:]
    README_PATH.write_text(updated, encoding="utf-8", newline="\n")


def receipt_errors(receipt: dict) -> list[str]:
    errors: list[str] = []
    if receipt.get("content_sha256") != content_digest(receipt):
        errors.append("release receipt content digest mismatch")
    try:
        expected = build_receipt(recompute_components=False, recompute_lean=False)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
        return errors
    if receipt != expected:
        errors.append("release receipt differs from the current paper-owned closure")
    return errors


def receipt_index_errors(receipt_path: Path, receipt: dict) -> list[str]:
    errors = []
    closure_paths = {
        row["artifact"]["path"] for row in receipt["artifact_closure"]["ordered_artifacts"]
    }
    if repo_path(receipt_path) in closure_paths:
        errors.append("release receipt is included in its own closure")
    if receipt_index_block(receipt_path, receipt) not in README_PATH.read_text(encoding="utf-8"):
        errors.append("README exact receipt index is stale")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", nargs="?", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--recompute-components", action="store_true")
    parser.add_argument("--recompute-lean", action="store_true")
    args = parser.parse_args()
    if args.write_receipt:
        if not args.recompute_components or not args.recompute_lean:
            parser.error("--write-receipt requires --recompute-components and --recompute-lean")
        receipt = build_receipt(recompute_components=True, recompute_lean=True)
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
    errors = receipt_errors(receipt)
    if args.receipt.resolve() == DEFAULT_RECEIPT.resolve():
        errors.extend(receipt_index_errors(args.receipt, receipt))
    if errors:
        print(f"FAIL {args.receipt}")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"PASS {receipt['receipt_id']}: {len(CHECKS)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
