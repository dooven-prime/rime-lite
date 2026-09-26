"""Stage the bounded Paper XXVIII finite evidence mirror from its historical home.

This is a packaging tool, not an artifact producer or proof authority. It never
rewrites an existing mirror file whose bytes differ from the source.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import shutil
import subprocess
from collections import deque
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
HIST = REPO / "experiments" / "synchronizing_automata"
PACKAGE = REPO / "experiments" / "paper28"
RESULTS = HIST / "results"

ROOT_STEMS = (
    "paper28_seed_mechanism_catalog_v1",
    "paper28_boundary_liftability_audit_v1",
    "paper28_credit_composition_audit_v1",
    "paper28_boundary_generator_factorization_v1",
    "paper28_section_return_menu_audit_v1",
    "paper28_rank5_section_return_evaluation_v1",
    "paper28_second_rank4_section_return_evaluation_v1",
    "paper28_second_rank5_section_return_evaluation_v1",
    "paper28_third_rank4_section_return_evaluation_v1",
    "paper28_third_rank5_section_return_evaluation_v1",
    "paper28_fourth_rank4_section_return_evaluation_v1",
    "paper28_fourth_rank5_section_return_evaluation_v1",
    "paper28_fifth_rank4_section_return_evaluation_v1",
    "paper28_fifth_rank5_section_return_evaluation_v1",
    "paper28_fourth_mechanism_schema_declaration_v1",
    "paper28_third_mechanism_schema_declaration_v1",
    "paper28_gfpc_component_completion_v1",
    "paper28_pec_component_completion_v1",
    "paper28_fixed_scope_mechanism_cover_closure_v1",
    "paper28_canonical_return_certificate_alignment_v1",
)

VALIDATOR_ONLY_STEMS = (
    "paper28_fpc_component_completion_v1",
)

FINITE_NOTES = (
    "P28_1_MECHANISM_QUOTIENT.md",
    "P28_1_SEED_PROJECTOR_RESULTS.md",
    "P28_1B_BOUNDARY_LIFTABILITY_RESULTS.md",
    "P28_2_CREDIT_COMPOSITION_RESULTS.md",
    "P28_3_BOUNDARY_GENERATOR_RESULTS.md",
    "P28_4A_FUTURE_FREE_SECTION_RETURN_SCHEMA.md",
    "P28_4_SECTION_RETURN_RESULTS.md",
    "P28_5A_RANK5_SECTION_CANDIDATE.md",
    "P28_5B_RANK5_SECTION_RETURN_RESULTS.md",
    "P28_5D_SECOND_RETURN_CANDIDATE.md",
    "P28_5E_SECOND_RANK4_SECTION_RETURN_RESULTS.md",
    "P28_5F_SECOND_RANK5_SECTION_RETURN_RESULTS.md",
    "P28_5H_THIRD_RETURN_CANDIDATE.md",
    "P28_5I_THIRD_RANK4_SECTION_RETURN_RESULTS.md",
    "P28_5K_THIRD_RANK5_SECTION_RETURN_RESULTS.md",
    "P28_5N_FRESH_CONSUMPTION_HOSTILE_SELECTOR.md",
    "P28_5P_FOURTH_RANK4_SECTION_RETURN_RESULTS.md",
    "P28_5R_FOURTH_RANK5_SECTION_RETURN_RESULTS.md",
    "P28_5S_NON_LENGTH_THREE_HOSTILE_SELECTOR.md",
    "P28_5U_FIFTH_RANK4_SECTION_RETURN_RESULTS.md",
    "P28_5W_FIFTH_RANK5_SECTION_RETURN_RESULTS.md",
    "P28_6U_A2_PAIR_EXTENSION_CARRY_DECLARATION.md",
    "P28_6U_A3_GENERALIZED_FRESH_PAIR_CARRY_DECLARATION.md",
    "P28_6U_C2_TAGGED_PEC_COMPONENT_COMPLETION.md",
    "P28_6U_C3_TAGGED_GFPC_COMPONENT_COMPLETION.md",
    "P28_6U_D_TAGGED_FIXED_SCOPE_MECHANISM_COVER.md",
    "P28_6V_CANONICAL_RETURN_CERTIFICATE_ALIGNMENT.md",
)

# Three declaration receipts bind their producers but omit existing validators.
EXTRA_VALIDATORS = (
    "validate_paper28_second_mechanism_schema.py",
    "validate_paper28_third_mechanism_schema.py",
    "validate_paper28_fourth_mechanism_schema.py",
)

UPSTREAM_INPUTS = {
    "e52a2dbad23ee8c86c18779de97e9bd129f45fe2f984a3772f89a2cb963deaa9": {
        "name": "single_defect_n6_rank4_activated_entry_exhaustiveness_v1.json",
        "source": "git:paper27-v1.0:experiments/paper27/results/single_defect_n6_rank4_activated_entry_exhaustiveness_v1.json",
    },
    "129cbcbbe97e9af95673ce9e5716bfeea9e1a29f1a6c56e716ba135561142f65": {
        "name": "single_defect_n7_extremal_carrier_input_v1.json",
        "source": "git:paper27-v1.0:experiments/paper27/results/single_defect_n7_extremal_carrier_input_v1.json",
    },
    "fd6045934b8585d748d8684e1062e71ddc25bdf0865e154dae6eab16a1563182": {
        "name": "single_defect_n7_inherited_section_pilot_complete_v1.json",
        "source": "experiments/synchronizing_automata/results/single_defect_n7_inherited_section_pilot_complete_v1.json",
    },
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_bytes(reference: str) -> bytes:
    if reference.startswith("git:"):
        _, tag, path = reference.split(":", 2)
        return subprocess.run(
            ["git", "show", f"{tag}:{path}"],
            cwd=REPO,
            check=True,
            capture_output=True,
        ).stdout
    return (REPO / reference).read_bytes()


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def receipt_inputs(value: object, label: str = "inputs"):
    if isinstance(value, list):
        for item in value:
            yield from receipt_inputs(item, label)
    elif isinstance(value, dict):
        if isinstance(value.get("sha256"), str):
            yield {"label": label, **value}
        else:
            for key, item in value.items():
                yield from receipt_inputs(item, f"{label}.{key}")


def source_ref(entry: dict) -> Path:
    ref = entry.get("path") or entry.get("name")
    if not isinstance(ref, str):
        raise ValueError(f"source closure has no path/name: {entry}")
    candidate = REPO / ref if ref.startswith("experiments/") else HIST / ref
    candidate = candidate.resolve()
    if not candidate.is_file():
        raise FileNotFoundError(candidate)
    return candidate


def local_imports(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = (node.module,)
        else:
            continue
        for name in names:
            base = name.split(".", 1)[0]
            candidate = HIST / f"{base}.py"
            if candidate.is_file():
                yield candidate


def collect():
    files: dict[str, dict] = {}
    dependencies: list[dict] = []
    external: list[dict] = []
    queued = deque((*ROOT_STEMS, *VALIDATOR_ONLY_STEMS))
    visited: set[str] = set()
    code: set[Path] = set()

    def add(path: Path, mirror: Path, role: str, expected: str | None = None):
        if not path.is_file():
            raise FileNotFoundError(path)
        source = relative(path)
        sha = digest(path)
        if expected is not None and sha != expected:
            raise ValueError(f"receipt digest mismatch: {source}: {sha} != {expected}")
        record = {"source": source, "mirror": relative(mirror), "sha256": sha, "role": role}
        previous = files.setdefault(source, record)
        if previous["mirror"] != record["mirror"] or previous["sha256"] != sha:
            raise ValueError(f"conflicting mirror mapping for {source}")

    for name in FINITE_NOTES:
        add(HIST / name, PACKAGE / "artifacts" / name, "finite_note")

    while queued:
        stem = queued.popleft()
        if stem in visited:
            continue
        visited.add(stem)
        receipt_path = RESULTS / f"{stem}.receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        artifact = receipt["artifact"]
        artifact_name = artifact.get("name") or Path(artifact["path"]).name
        artifact_path = RESULTS / artifact_name
        add(artifact_path, PACKAGE / "results" / artifact_name, "exact_artifact", artifact["sha256"])
        add(receipt_path, PACKAGE / "results" / receipt_path.name, "receipt")

        for key in ("input", "inputs"):
            for item in receipt_inputs(receipt.get(key), key):
                ref = item.get("path") or item.get("name")
                sha = item["sha256"]
                if isinstance(ref, str):
                    name = Path(ref).name
                    if name.startswith("paper28_") and (RESULTS / name).is_file():
                        path = RESULTS / name
                        if digest(path) != sha:
                            raise ValueError(f"input digest mismatch: {stem} -> {name}")
                        child = name.removesuffix(".json.gz").removesuffix(".json")
                        queued.append(child)
                        dependencies.append({"from": stem, "to": child, "sha256": sha})
                        continue
                external.append({"consumer": stem, "label": item["label"], "reference": ref, "schema": item.get("schema"), "sha256": sha})

        closure = receipt.get("source_closure", [])
        if isinstance(closure, dict):
            closure = list(closure.values())
        for item in closure:
            path = source_ref(item)
            if digest(path) != item["sha256"]:
                raise ValueError(f"source-closure digest mismatch: {relative(path)}")
            if path.is_relative_to(HIST) and path.suffix == ".py":
                code.add(path)
            else:
                external.append({"consumer": stem, "label": "source_closure", "reference": relative(path), "sha256": item["sha256"]})

    code_queue = deque(code)
    for name in EXTRA_VALIDATORS:
        path = HIST / "validation" / name
        if not path.is_file():
            raise FileNotFoundError(path)
        code.add(path)
        code_queue.append(path)
    while code_queue:
        for path in local_imports(code_queue.popleft()):
            if path not in code:
                code.add(path)
                code_queue.append(path)
    for path in sorted(code):
        subpath = path.relative_to(HIST)
        role = "validator" if subpath.parts[0] == "validation" else "producer_or_dependency"
        add(path, PACKAGE / subpath, role)

    upstream_inputs = []
    required_digests = {item["sha256"] for item in external}
    if not required_digests <= UPSTREAM_INPUTS.keys():
        raise ValueError(f"unresolved upstream input digests: {required_digests - UPSTREAM_INPUTS.keys()}")
    for sha in sorted(required_digests):
        spec = UPSTREAM_INPUTS[sha]
        data = source_bytes(spec["source"])
        if hashlib.sha256(data).hexdigest() != sha:
            raise ValueError(f"upstream source digest mismatch: {spec['source']}")
        upstream_inputs.append({
            "name": spec["name"],
            "source": spec["source"],
            "mirror": relative(PACKAGE / "inputs" / spec["name"]),
            "sha256": sha,
        })
    for item in external:
        item["mirror"] = next(entry["mirror"] for entry in upstream_inputs if entry["sha256"] == item["sha256"])

    return {
        "schema": "paper28-frozen-finite-mirror-v2",
        "authority": "experiments/synchronizing_automata/",
        "status": "byte-identical release copy; not a second theorem or publication authority",
        "root_artifacts": list(ROOT_STEMS),
        "validator_only_artifacts": list(VALIDATOR_ONLY_STEMS),
        "files": sorted(files.values(), key=lambda item: item["mirror"]),
        "artifact_dependencies": sorted(dependencies, key=lambda item: (item["from"], item["to"])),
        "upstream_inputs": upstream_inputs,
        "external_inputs": sorted(external, key=lambda item: (item["consumer"], item["label"], str(item["reference"]))),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", action="store_true", help="copy absent files and write the manifest")
    parser.add_argument("--amend", action="store_true", help="only add files to an existing staged manifest")
    args = parser.parse_args()
    manifest = collect()
    counts: dict[str, int] = {}
    for item in manifest["files"]:
        counts[item["role"]] = counts.get(item["role"], 0) + 1
    print(json.dumps({"roots": len(ROOT_STEMS), "roles": counts, "dependencies": len(manifest["artifact_dependencies"]), "external_inputs": len(manifest["external_inputs"])}, indent=2))
    if not args.stage:
        return
    manifest_path = PACKAGE / "dependency-manifest.json"
    contents = json.dumps(manifest, ensure_ascii=True, indent=2) + "\n"
    if manifest_path.exists() and manifest_path.read_text(encoding="utf-8") != contents:
        if not args.amend:
            raise ValueError("existing manifest differs; frozen mirror cannot be refreshed in place")
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        new_files = {item["source"]: item for item in manifest["files"]}
        if not all(new_files.get(item["source"]) == item for item in previous["files"]):
            raise ValueError("amend would change or remove an existing mirrored binding")
    for item in manifest["files"]:
        source = REPO / item["source"]
        target = REPO / item["mirror"]
        if target.exists():
            if digest(target) != item["sha256"]:
                raise ValueError(f"existing mirror has different bytes: {target}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for item in manifest["upstream_inputs"]:
        target = REPO / item["mirror"]
        data = source_bytes(item["source"])
        if target.exists():
            if digest(target) != item["sha256"]:
                raise ValueError(f"existing upstream mirror has different bytes: {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    if not manifest_path.exists() or manifest_path.read_text(encoding="utf-8") != contents:
        manifest_path.write_text(contents, encoding="utf-8", newline="\n")
    print(f"staged {len(manifest['files'])} byte-identical files: {manifest_path}")


if __name__ == "__main__":
    main()
