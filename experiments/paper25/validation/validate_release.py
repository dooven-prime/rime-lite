"""Validate the structured Paper XXV evidence ownership and hash closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MANIFEST = HERE.parent / "release-manifest.json"
RECEIPT = HERE.parent / "results" / "paper25_release_receipt_v1.json"
RELEASE_ENVIRONMENT = HERE.parent / "release-environment.json"
PAPER = ROOT / "papers" / "paper25"
PACKAGE = ROOT / "experiments" / "paper25"

FORBIDDEN = (
    "experiments/" + "exploratory",
    "rime." + "exploratory",
    "tests/" + "internal",
    "sof_" + "external_falsification",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(payload: object) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def artifact_closure(manifest: dict) -> dict:
    rows = [
        {
            "role": row["role"],
            "artifact": {
                "uri": row["path"],
                "sha256": sha256(ROOT / row["path"]),
            },
        }
        for row in manifest["artifacts"]
    ]
    rows.append(
        {
            "role": "release-manifest",
            "artifact": {
                "uri": MANIFEST.relative_to(ROOT).as_posix(),
                "sha256": sha256(MANIFEST),
            },
        }
    )
    return {
        "artifact_count": len(rows),
        "closure_digest": canonical_digest(rows),
        "ordered_artifacts": rows,
    }


def build_receipt(manifest: dict) -> dict:
    receipt = {
        "schema": "rime.paper25.release-receipt.v1",
        "artifact_id": "PAPER25-V1-RELEASE-CLOSURE",
        "status": "PASS",
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "scope": "Exact release-byte closure; not independent validation or theorem proof",
        "receipt_self_exclusion": True,
        "artifact_closure": artifact_closure(manifest),
    }
    receipt["content_sha256"] = canonical_digest(receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    result = subprocess.run(
        [sys.executable, str(HERE / "validate_claim_surface.py")], cwd=ROOT
    )
    if result.returncode:
        return result.returncode
    result = subprocess.run(
        [sys.executable, str(HERE / "validate_sharpness.py")], cwd=ROOT
    )
    if result.returncode:
        return result.returncode
    result = subprocess.run(
        [sys.executable, str(HERE / "validate_bounded_observations.py")], cwd=ROOT
    )
    if result.returncode:
        return result.returncode
    supplement = HERE.parent / "notes" / "proportional_markov_semantic_lift"
    for validator in (
        supplement / "validate_note.py",
        supplement / "validate_nstate_audit.py",
        HERE / "validate_lean_formalization.py",
    ):
        result = subprocess.run([sys.executable, str(validator)], cwd=ROOT)
        if result.returncode:
            return result.returncode

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    if manifest.get("paper_id") != "PAPER25":
        errors.append("paper identity mismatch")
    if manifest.get("release_version") != "1.0":
        errors.append("release-version mismatch")
    if manifest.get("status") != "RELEASE_CANDIDATE":
        errors.append("evidence manifest escaped structured-draft status")
    if manifest.get("release_identity_claimed") is not False:
        errors.append("draft evidence manifest claimed public release identity")
    if manifest.get("validation_mode") != "LOCAL_CLOSURE_VERIFICATION":
        errors.append("validation mode mismatch")
    if manifest.get("supplementary_surfaces") != {
        "PAPER25-S1": {
            "title": "Proportional Scaling and Semantic Lifts for Finite Markov Diagnostics",
            "claim_authority": "supplementary-note proof",
            "release_identity": "inherits Paper XXV package; no independent DOI or paper number",
            "negative_boundary": "absolute spectral gap need not be monotone under proportional row scaling",
        }
    }:
        errors.append("Supplement S1 declaration mismatch")
    if manifest.get("formalization") != {
        "formalization_id": "PAPER25-TYPED-TRANSPORT-SCALAR-MARGIN-V1",
        "status": "PARTIAL_FORMALIZATION",
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
    }:
        errors.append("Lean formalization declaration mismatch")
    layers = manifest.get("evidence_layers", {})
    exact_layer = layers.get("EXACT_INTEGER_FRACTION_CERTIFICATE", {})
    if exact_layer.get("claim_status") != "EXACT_FINITE_CERTIFICATE":
        errors.append("exact evidence layer status mismatch")
    if exact_layer.get("arithmetic") != "Python int and fractions.Fraction; no floating-point arithmetic":
        errors.append("exact evidence layer arithmetic is not frozen")
    bounded_layer = layers.get("BOUNDED_FLOAT64_OBSERVATION", {})
    if bounded_layer.get("claim_status") != "BOUNDED_NUMERICAL_OBSERVATION":
        errors.append("bounded evidence layer status mismatch")
    if bounded_layer.get("common_numerical_environment") != {
        "python": "3.13.0",
        "numpy": "2.1.3",
        "arithmetic": "float64/complex128",
        "encoding": "UTF-8",
        "line_endings": "LF",
    }:
        errors.append("bounded numerical environment is not frozen")
    if exact_layer.get("registered_components") != [
        {
            "path": "experiments/paper25/results/diagnostic_sharpness_v1.json",
            "component": "whole_artifact",
        },
        {
            "path": "experiments/paper25/results/transformation_laws_v1.json",
            "component": "exact_finite_certificate",
        },
    ]:
        errors.append("exact component registry mismatch")
    rubik_protocol = bounded_layer.get("rubik_simultaneous_transport", {})
    if rubik_protocol.get("runtime_dependencies") != {"scipy": "1.18.0"}:
        errors.append("Rubik runtime dependency closure changed")
    if rubik_protocol.get("registered_components") != [
        {
            "path": "experiments/paper25/results/transformation_laws_v1.json",
            "component": "bounded_numerical_observation",
        },
        {
            "path": "experiments/paper25/results/rubik_qh_transport_v1.json",
            "component": "whole_artifact",
        },
        {
            "path": "experiments/paper25/results/rubik_perturbation_sweep_v1.json",
            "component": "whole_artifact",
        },
    ]:
        errors.append("Rubik bounded-observation registry mismatch")
    if {
        key: rubik_protocol.get(key)
        for key in (
            "norms",
            "support_thresholds",
            "activity_threshold",
            "transport_residual_tolerance",
            "perturbation_comparison_tolerance",
            "transformation_near_zero_error_bound",
            "zero_policy",
        )
    } != {
        "norms": {
            "block": "Frobenius",
            "operator": "spectral 2",
            "projector_delta": "Frobenius",
        },
        "support_thresholds": [1e-10, 1e-6, 0.05],
        "activity_threshold": 0.05,
        "transport_residual_tolerance": 1e-10,
        "perturbation_comparison_tolerance": 2e-10,
        "transformation_near_zero_error_bound": 1e-9,
        "zero_policy": "localized/global ratio <= perturbation comparison tolerance is reported as zero; inactive threshold values are not exact-zero claims",
    }:
        errors.append("Rubik norm/threshold/zero/tolerance protocol changed")
    markov_protocol = bounded_layer.get("markov_portability_example", {})
    if markov_protocol.get("registered_components") != [
        {
            "path": "experiments/paper25/results/nonnormal_markov_stability_v1.json",
            "component": "whole_artifact",
        },
        {
            "path": "experiments/paper25/results/markov_probability_alignment_v1.json",
            "component": "whole_artifact",
        },
    ]:
        errors.append("Markov bounded-observation registry mismatch")
    if {
        key: markov_protocol.get(key)
        for key in (
            "norms",
            "block_activity_threshold",
            "positive_support_threshold",
            "comparison_tolerance",
            "zero_policy",
        )
    } != {
        "norms": {
            "block": "Frobenius",
            "operator": "spectral 2",
            "projector_delta": "Frobenius",
        },
        "block_activity_threshold": 0.15,
        "positive_support_threshold": 1e-12,
        "comparison_tolerance": 2e-12,
        "zero_policy": "positive support uses entries above the declared threshold; UNRESOLVED is not exact zero",
    }:
        errors.append("Markov norm/threshold/zero/tolerance protocol changed")
    roles: dict[str, list[Path]] = {}
    for row in manifest.get("artifacts", []):
        path_text = row.get("path", "")
        path = ROOT / path_text
        roles.setdefault(row.get("role", ""), []).append(path)
        if not path.is_file():
            errors.append(f"missing artifact: {path_text}")
        if not path_text.startswith(
            (
                "papers/paper25/",
                "experiments/paper25/",
                "figures/paper25/",
                "figures/sof_figure_utils.py",
                "rime/",
            )
        ):
            errors.append(f"nonlocal public artifact: {path_text}")

    release_environment = json.loads(RELEASE_ENVIRONMENT.read_text(encoding="utf-8"))
    if release_environment != {
        "schema": "rime.paper25.release-environment.v1",
        "status": "RECORDED_NOT_REPRODUCIBLY_LOCKED",
        "captured_on": "2026-09-05",
        "platform": "Windows-11-10.0.26200-SP0",
        "python": "3.13.0",
        "numpy": "2.1.3",
        "scipy": "1.18.0",
        "matplotlib": "3.9.2",
        "pandoc": "3.6.4",
        "xelatex": "MiKTeX-XeTeX 4.18 (MiKTeX 26.5)",
        "bibtex": "MiKTeX-BibTeX 4.2 (MiKTeX 26.5)",
        "source_encoding": "UTF-8",
        "source_line_endings": "LF",
    }:
        errors.append("release build environment record changed")
        if path_text == RECEIPT.relative_to(ROOT).as_posix():
            errors.append("release receipt occurs in its own closure")

    public_files = list(PAPER.rglob("*")) + list(PACKAGE.rglob("*"))
    for path in public_files:
        if not path.is_file() or path.suffix not in {".md", ".json", ".bib", ".txt", ".py"}:
            continue
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN:
            if token in text:
                errors.append(f"private dependency {token!r} in {path.relative_to(ROOT)}")

    bounded_paths = (
        roles.get("bounded-rubik-observation", [])
        + roles.get("bounded-markov-observation", [])
    )
    for path in bounded_paths:
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("claim_status") not in {
            "BOUNDED_NUMERICAL_OBSERVATION",
            "MIXED_EXACT_AND_BOUNDED_NUMERICAL_CONTROL",
            "EXACT_FINITE_CERTIFICATE_AND_BOUNDED_NUMERICAL_OBSERVATION",
        }:
            errors.append(f"imported observation changed claim status: {path.name}")
        if payload.get("paper_evidence_status") != "REGISTERED_SUPPORT_NOT_THEOREM_PROOF":
            errors.append(f"paper-owned evidence status drift: {path.name}")

    source_root = ROOT / "experiments/paper25/results"
    transformation = json.loads(
        (source_root / "transformation_laws_v1.json").read_text(encoding="utf-8")
    )
    exact_transport = transformation.get("exact_finite_certificate", {})
    if exact_transport.get("arithmetic") != "Python integer matrices and Fraction trace moments":
        errors.append("exact transport arithmetic protocol changed")
    bounded_transport = transformation.get("bounded_numerical_observation", {})
    near_zero = bounded_transport.get("near_zero_policy_control", {})
    if bounded_transport.get("declared_tolerance") != 1e-10:
        errors.append("generic transport tolerance changed")
    if near_zero.get("declared_error_bound") != 1e-9:
        errors.append("generic near-zero error radius changed")
    if near_zero.get("exact_zero_status_reserved_for_exact_arithmetic") is not True:
        errors.append("generic numerical zero policy changed")

    rubik_transport = json.loads(
        (source_root / "rubik_qh_transport_v1.json").read_text(encoding="utf-8")
    )
    if rubik_transport.get("environment") != {
        "python": "3.13.0",
        "numpy": "2.1.3",
        "scipy": "1.18.0",
        "arithmetic": "complex128/float64",
    }:
        errors.append("Rubik transport numerical environment changed")
    if rubik_transport.get("generator_resolved_profiles", {}).get("norm") != "Frobenius":
        errors.append("Rubik block norm policy changed")
    if [
        row.get("threshold")
        for row in rubik_transport.get("aggregate_support_profiles", {}).get("threshold_census", [])
    ] != [1e-10, 1e-6, 0.05]:
        errors.append("Rubik support-threshold policy changed")

    rubik_sweep = json.loads(
        (source_root / "rubik_perturbation_sweep_v1.json").read_text(encoding="utf-8")
    )
    if rubik_sweep.get("environment") != {
        "python": "3.13.0",
        "numpy": "2.1.3",
        "scipy": "1.18.0",
        "arithmetic": "complex128/float64",
    }:
        errors.append("Rubik perturbation numerical environment changed")
    if rubik_sweep.get("stability_bound", {}).get("comparison_tolerance") != 2e-10:
        errors.append("Rubik perturbation comparison tolerance changed")
    rubik_margin = rubik_sweep.get("support_margin_policy", {})
    if rubik_margin.get("threshold") != 0.05:
        errors.append("Rubik activity threshold changed")
    if rubik_margin.get("inactive_is_exact_zero") is not False:
        errors.append("Rubik threshold/zero boundary changed")

    markov = json.loads(
        (source_root / "nonnormal_markov_stability_v1.json").read_text(encoding="utf-8")
    )
    if markov.get("environment") != {
        "python": "3.13.0",
        "numpy": "2.1.3",
        "arithmetic": "float64/complex128",
    }:
        errors.append("Markov numerical environment changed")
    if markov.get("stability_bound", {}).get("comparison_tolerance") != 2e-12:
        errors.append("Markov comparison tolerance changed")
    if markov.get("block_activity_policy", {}).get("threshold") != 0.15:
        errors.append("Markov block-activity threshold changed")
    if markov.get("markov_positive_support_policy", {}).get("threshold") != 1e-12:
        errors.append("Markov positive-support threshold changed")

    markov_lift = json.loads(
        (source_root / "markov_probability_alignment_v1.json").read_text(encoding="utf-8")
    )
    if markov_lift.get("environment") != {
        "python": "3.13.0",
        "numpy": "2.1.3",
        "arithmetic": "float64",
    }:
        errors.append("Markov probability-lift environment changed")

    receipt_paths = roles.get("validation-receipt", [])
    if receipt_paths and receipt_paths[0].is_file():
        receipt = json.loads(receipt_paths[0].read_text(encoding="utf-8"))
        if receipt.get("status") != "PASS":
            errors.append("sharpness receipt is not PASS")
        unsigned = dict(receipt)
        supplied = unsigned.pop("content_sha256", None)
        canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"))
        if supplied != hashlib.sha256(canonical.encode("utf-8")).hexdigest():
            errors.append("sharpness receipt digest mismatch")
        artifact = receipt.get("artifact", {})
        exact_paths = roles.get("exact-certificate", [])
        if exact_paths and exact_paths[0].is_file():
            if artifact.get("sha256") != sha256(exact_paths[0]):
                errors.append("sharpness receipt does not bind current certificate")

    bounded_receipts = roles.get("bounded-observation-registry-receipt", [])
    if bounded_receipts and bounded_receipts[0].is_file():
        receipt = json.loads(bounded_receipts[0].read_text(encoding="utf-8"))
        if receipt.get("status") != "PASS":
            errors.append("bounded-observation receipt is not PASS")
        unsigned = dict(receipt)
        supplied = unsigned.pop("content_sha256", None)
        canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"))
        if supplied != hashlib.sha256(canonical.encode("utf-8")).hexdigest():
            errors.append("bounded-observation receipt digest mismatch")
        registry = receipt.get("bounded_observation_registry", {})
        registry_paths = roles.get("bounded-observation-registry", [])
        if registry_paths and registry_paths[0].is_file():
            if registry.get("sha256") != sha256(registry_paths[0]):
                errors.append("bounded-observation receipt does not bind current registry")

    closure = None
    if not errors:
        closure = artifact_closure(manifest)
        if RECEIPT.is_file() and not args.write_receipt:
            retained_receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
            if retained_receipt != build_receipt(manifest):
                errors.append("release receipt differs from current artifact closure")
    if errors:
        print("FAIL Paper XXV structured evidence closure")
        for error in errors:
            print(f"  - {error}")
        return 1
    if args.write_receipt:
        receipt = build_receipt(manifest)
        RECEIPT.write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        print(f"WROTE {RECEIPT.relative_to(ROOT).as_posix()}")
    print(
        "PASS Paper XXV structured evidence closure: "
        f"{closure['artifact_count']} bound artifacts, "
        f"closure {closure['closure_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
