"""Read-only, paper-owned integrity check for the Paper XXVIII finite mirror.

Historical source comparison is optional. Default validation uses only files
inside experiments/paper28 and the source addresses recorded in their receipts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
PACKAGE = REPO / "experiments" / "paper28"
MANIFEST = PACKAGE / "dependency-manifest.json"
ANCHORS = {
    "paper28_fixed_scope_mechanism_cover_closure_v1.json.gz": "20073b8c096be4085ef28d6199ebe009d3333cd75078e029c003a1b670edb46f",
    "paper28_canonical_return_certificate_alignment_v1.json.gz": "69564521589c51f99dd3e29d96c554be19253ac73741c418ea1fa723c201e6f9",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check(condition: bool, message: str):
    if not condition:
        raise ValueError(message)


def manifest_path(value: str) -> Path:
    path = (REPO / value).resolve()
    check(path.is_relative_to(REPO.resolve()), f"path escapes repository: {value}")
    return path


def source_digest(reference: str) -> str:
    if reference.startswith("git:"):
        _, tag, path = reference.split(":", 2)
        data = subprocess.run(
            ["git", "show", f"{tag}:{path}"], cwd=REPO, check=True,
            capture_output=True,
        ).stdout
        return hashlib.sha256(data).hexdigest()
    return digest(manifest_path(reference))


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compare-historical-source", action="store_true", help="also compare against historical paths and Paper XXVII tag blobs")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest["schema"] == "paper28-frozen-finite-mirror-v2", "wrong manifest schema")
    files = manifest["files"]
    by_mirror = {item["mirror"]: item for item in files}
    check(len(by_mirror) == len(files), "duplicate mirror path")
    roles = Counter()
    for item in files:
        mirror = manifest_path(item["mirror"])
        check(mirror.is_file(), f"missing mirror: {item['mirror']}")
        expected = item["sha256"]
        check(digest(mirror) == expected, f"mirror bytes diverged: {item['mirror']}")
        if args.compare_historical_source:
            check(source_digest(item["source"]) == expected, f"historical source diverged: {item['source']}")
        roles[item["role"]] += 1

    upstream = manifest["upstream_inputs"]
    by_upstream_sha = {item["sha256"]: item for item in upstream}
    check(len(by_upstream_sha) == len(upstream), "duplicate upstream digest")
    for item in upstream:
        mirror = manifest_path(item["mirror"])
        check(mirror.is_file() and digest(mirror) == item["sha256"], f"upstream input binding failed: {item['mirror']}")
        if args.compare_historical_source:
            check(source_digest(item["source"]) == item["sha256"], f"upstream source diverged: {item['source']}")

    for name, expected in ANCHORS.items():
        check(digest(PACKAGE / "results" / name) == expected, f"anchor digest mismatch: {name}")

    receipts = [item for item in files if item["role"] == "receipt"]
    observed_edges = []
    observed_external = []
    for item in receipts:
        receipt = json.loads(manifest_path(item["mirror"]).read_text(encoding="utf-8"))
        artifact = receipt["artifact"]
        name = artifact.get("name") or Path(artifact["path"]).name
        target = PACKAGE / "results" / name
        check(target.is_file() and digest(target) == artifact["sha256"], f"receipt artifact binding failed: {name}")
        closure = receipt.get("source_closure", [])
        if isinstance(closure, dict):
            closure = list(closure.values())
        for source in closure:
            ref = source.get("path") or source.get("name")
            old_path = ref if ref.startswith("experiments/") else "experiments/synchronizing_automata/" + ref
            matching = [entry for entry in files if entry["source"] == old_path]
            check(len(matching) == 1 and matching[0]["sha256"] == source["sha256"], f"receipt source closure failed: {item['mirror']} -> {ref}")

        stem = Path(item["mirror"]).name.removesuffix(".receipt.json")
        for key in ("input", "inputs"):
            for input_item in receipt_inputs(receipt.get(key), key):
                ref = input_item.get("path") or input_item.get("name")
                sha = input_item["sha256"]
                name = Path(ref).name if isinstance(ref, str) else None
                if name and name.startswith("paper28_") and (PACKAGE / "results" / name).is_file():
                    child = name.removesuffix(".json.gz").removesuffix(".json")
                    observed_edges.append({"from": stem, "to": child, "sha256": sha})
                    check(digest(PACKAGE / "results" / name) == sha, f"receipt input failed: {stem} -> {name}")
                else:
                    check(sha in by_upstream_sha, f"unmapped upstream input: {stem}: {sha}")
                    observed_external.append({
                        "consumer": stem, "label": input_item["label"],
                        "reference": ref, "schema": input_item.get("schema"),
                        "sha256": sha, "mirror": by_upstream_sha[sha]["mirror"],
                    })

    for edge in manifest["artifact_dependencies"]:
        name = edge["to"]
        matches = [item for item in files if item["role"] == "exact_artifact" and Path(item["mirror"]).name.startswith(name + ".json")]
        check(len(matches) == 1 and matches[0]["sha256"] == edge["sha256"], f"input edge failed: {edge['from']} -> {name}")
    check(sorted(observed_edges, key=lambda edge: (edge["from"], edge["to"])) == manifest["artifact_dependencies"], "manifest does not enumerate the receipt input edges")
    check(sorted(observed_external, key=lambda edge: (edge["consumer"], edge["label"], str(edge["reference"]))) == manifest["external_inputs"], "manifest does not enumerate the upstream bindings")

    roots = manifest["root_artifacts"]
    for stem in roots:
        check(any(item["role"] == "receipt" and Path(item["mirror"]).name == stem + ".receipt.json" for item in files), f"root receipt missing: {stem}")

    upstream_mirrors = {item["mirror"] for item in upstream}
    supplementary_files = {
        "experiments/paper28/results/paper28_lean_formalization_v1.receipt.json",
        "experiments/paper28/results/paper28_public_package_v1.validation-receipt.json",
    }
    for subdir in ("artifacts", "results", "inputs"):
        for path in (PACKAGE / subdir).rglob("*"):
            if path.is_file():
                rel = path.relative_to(REPO).as_posix()
                check(
                    rel in by_mirror
                    or rel in upstream_mirrors
                    or rel in supplementary_files,
                    f"unlisted package file: {rel}",
                )
    local_tools = {
        PACKAGE / "validation" / "stage_mirror.py",
        PACKAGE / "validation" / "validate_lean_formalization.py",
        PACKAGE / "validation" / "validate_public_package.py",
        PACKAGE / "validation" / "validate_release.py",
        Path(__file__).resolve(),
    }
    for path in list(PACKAGE.glob("*.py")) + list((PACKAGE / "validation").glob("*.py")):
        if path.resolve() not in local_tools:
            rel = path.relative_to(REPO).as_posix()
            check(rel in by_mirror, f"unlisted Python source: {rel}")

    print(f"PASS: {len(files)} frozen mirrors, {len(upstream)} exact upstream inputs, {len(receipts)} receipts, {len(roots)} finite roots, {len(manifest['artifact_dependencies'])} input edges, 2 immutable anchors")
    print("Roles: " + ", ".join(f"{role}={count}" for role, count in sorted(roles.items())))
    print("Historical source comparison: " + ("PASS" if args.compare_historical_source else "not requested"))


if __name__ == "__main__":
    main()
