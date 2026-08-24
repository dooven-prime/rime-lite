"""Validate an explicit manuscript/certificate/Lean claim-surface map."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE_ORDER = {name: index for index, name in enumerate(
    ("EXPLORE", "EXACTIFY", "PROVE", "FORMALIZE")
)}
DECLARATION_RE = re.compile(
    r"^\s*(?:theorem|lemma|def)\s+([A-Za-z_][A-Za-z0-9_'.]*)",
    re.MULTILINE,
)


class SurfaceError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repository_path(value: str) -> Path:
    path = ROOT / value
    if not path.is_file():
        raise SurfaceError(f"missing declared file: {value}")
    return path


def validate_artifacts(spec: dict, key: str) -> int:
    seen: set[str] = set()
    for artifact in spec.get(key, []):
        path_text = artifact["path"]
        if path_text in seen:
            raise SurfaceError(f"duplicate artifact in {key}: {path_text}")
        seen.add(path_text)
        observed = sha256(repository_path(path_text))
        if observed != artifact["sha256"]:
            raise SurfaceError(f"artifact drift in {key}: {path_text}")
    return len(seen)


def validate_lean_manifest(spec: dict) -> tuple[dict, set[str]]:
    manifest = load_json(repository_path(spec["lean_manifest_path"]))
    if manifest.get("status") != "COMPILED_PAPER_OWNED_SOURCE_CLOSURE":
        raise SurfaceError("Lean source closure is not compiled and paper-owned")

    project_root = ROOT / manifest["build"]["project_root"]
    declarations: set[str] = set()
    for relative, expected in manifest["source_sha256"].items():
        source = project_root / relative
        if not source.is_file():
            raise SurfaceError(f"missing Lean closure file: {relative}")
        if sha256(source) != expected:
            raise SurfaceError(f"Lean closure digest mismatch: {relative}")
        if source.suffix == ".lean":
            declarations.update(DECLARATION_RE.findall(source.read_text(encoding="utf-8")))
    return manifest, declarations


def validate_claims(spec: dict, manifest: dict, declarations: set[str]) -> int:
    manuscript = repository_path(spec["manuscript_path"]).read_text(encoding="utf-8")
    certificate = load_json(repository_path(spec["promotion_certificate_path"]))
    certificate_claims = {
        item["claim_id"]: item for item in certificate.get("promoted_claims", [])
    }
    if len(certificate_claims) != len(certificate.get("promoted_claims", [])):
        raise SurfaceError("promotion certificate contains duplicate claim IDs")

    mapped_ids: set[str] = set()
    excluded_scope = set(manifest.get("excluded_scope", []))
    for claim in spec["claims"]:
        claim_id = claim["claim_id"]
        if claim_id in mapped_ids:
            raise SurfaceError(f"duplicate surface-map claim: {claim_id}")
        mapped_ids.add(claim_id)

        stages = claim["completed_stages"]
        if not stages or any(stage not in STAGE_ORDER for stage in stages):
            raise SurfaceError(f"invalid lifecycle stage for {claim_id}")
        stage_positions = [STAGE_ORDER[stage] for stage in stages]
        if stage_positions != sorted(set(stage_positions)):
            raise SurfaceError(f"nonmonotone lifecycle for {claim_id}")

        for marker in claim.get("manuscript_markers", []):
            if marker not in manuscript:
                raise SurfaceError(f"missing manuscript marker for {claim_id}: {marker}")

        certificate_claim = certificate_claims.get(claim_id)
        if certificate_claim is None:
            raise SurfaceError(f"claim absent from promotion certificate: {claim_id}")
        if certificate_claim.get("status") != claim["certificate_status"]:
            raise SurfaceError(f"certificate status drift for {claim_id}")

        formalization_status = claim["formalization_status"]
        declared_theorems = claim.get("lean_declarations", [])
        if formalization_status == "FORMALIZED":
            if "FORMALIZE" not in stages or not declared_theorems:
                raise SurfaceError(f"incomplete formalization mapping for {claim_id}")
            missing = sorted(set(declared_theorems) - declarations)
            if missing:
                raise SurfaceError(
                    f"Lean surface mismatch for {claim_id}: {', '.join(missing)}"
                )
        elif formalization_status == "OPEN":
            if "FORMALIZE" in stages or declared_theorems:
                raise SurfaceError(f"open Lean surface overclaimed for {claim_id}")
            marker = claim.get("lean_excluded_scope")
            if marker and marker not in excluded_scope:
                raise SurfaceError(f"Lean excluded-scope drift for {claim_id}")
        elif formalization_status != "NOT_APPLICABLE":
            raise SurfaceError(f"unknown formalization status for {claim_id}")

    unmapped = sorted(set(certificate_claims) - mapped_ids)
    missing = sorted(mapped_ids - set(certificate_claims))
    if unmapped or missing:
        raise SurfaceError(
            f"claim/evidence surface diff: unmapped={unmapped}, missing={missing}"
        )
    return len(mapped_ids)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()

    spec_path = args.spec.resolve()
    spec = load_json(spec_path)
    if spec.get("schema") != "rime.claim-surface-map.v1":
        raise SurfaceError("unsupported claim-surface-map schema")
    if spec.get("workflow") != ["EXPLORE", "EXACTIFY", "PROVE", "FORMALIZE"]:
        raise SurfaceError("methodology workflow changed")

    historical_count = validate_artifacts(spec, "historical_artifacts")
    active_count = validate_artifacts(spec, "active_evidence")
    manifest, declarations = validate_lean_manifest(spec)
    claim_count = validate_claims(spec, manifest, declarations)
    print(
        f"PASS {spec['map_id']}: {claim_count} claims, "
        f"{historical_count} preserved historical artifacts, "
        f"{active_count} active evidence bindings, {len(declarations)} Lean declarations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
