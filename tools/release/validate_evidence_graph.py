"""Validate the public v2.1 receipt graph and its authority boundaries.

This read-only tool performs local closure verification. It checks raw-byte
references, direct and indirect receipt cycles, and forward dependencies from
an artifact to the receipt that validates it. It does not establish validator
independence, validator trust, or scientific correctness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from schemas.release_snapshot import resolve_release_reference  # noqa: E402
DEFAULT_RECEIPT_DIRS = (
    ROOT / "experiments" / "paper12" / "results" / "v2.1" / "report-validation-receipts",
    ROOT / "experiments" / "paper13" / "results" / "v2.1" / "receipts",
    ROOT / "experiments" / "paper14" / "results" / "v2.1" / "receipts",
)


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_uri(uri: str) -> str:
    if uri.startswith("artifact://"):
        uri = uri.removeprefix("artifact://")
    return uri.replace("\\", "/").lstrip("./")


def resolve_reference(reference: dict[str, Any]) -> tuple[str, Path]:
    uri = reference.get("uri")
    if not isinstance(uri, str) or not uri:
        raise AssertionError(f"reference has no URI: {reference!r}")
    rel = relative_uri(uri)
    normalized = {**reference, "uri": rel}
    path = resolve_release_reference(normalized, repository_root=ROOT).resolve()
    assert path.is_file(), f"referenced file is missing: {rel}"
    expected = reference.get("digest", {}).get("value")
    assert expected == file_digest(path), f"digest mismatch: {rel}"
    return rel, path


def receipt_paths(directories: list[Path]) -> list[Path]:
    paths = [
        path
        for directory in directories
        if directory.is_dir()
        for path in sorted(directory.glob("*.json"))
    ]
    assert paths, "no receipt JSON files found"
    return paths


def receipt_artifact_path(receipt: dict[str, Any]) -> str:
    for section in ("report", "audit", "action"):
        reference = receipt.get(section, {}).get("artifact")
        if isinstance(reference, dict):
            return relative_uri(reference["uri"])
    raise AssertionError(f"receipt has no primary artifact: {receipt.get('receipt_id')}")


def closure_receipt_edges(receipt_path: Path, receipt: dict[str, Any]) -> list[Path]:
    edges: list[Path] = []
    for item in receipt["artifact_closure"]["ordered_artifacts"]:
        rel, path = resolve_reference(item["artifact"])
        if path.suffix == ".json" and "receipt" in path.name:
            assert path != receipt_path.resolve(), (
                f"receipt closure contains itself: {receipt_path.relative_to(ROOT)}"
            )
            edges.append(path)
        # Keep the normalized path in the assertion message and make the
        # stage boundary visible when validation fails.
        assert rel
    return edges


def referenced_uris(value: Any):
    if isinstance(value, dict):
        if isinstance(value.get("uri"), str):
            yield value["uri"]
        for child in value.values():
            yield from referenced_uris(child)
    elif isinstance(value, list):
        for child in value:
            yield from referenced_uris(child)


def check_receipt_graph(paths: list[Path]) -> None:
    graph: dict[Path, list[Path]] = {}
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        graph[path.resolve()] = closure_receipt_edges(path, payload)

        primary_artifact = ROOT / receipt_artifact_path(payload)
        payload_artifact = json.loads(primary_artifact.read_text(encoding="utf-8"))
        current_receipt = path.resolve().relative_to(ROOT.resolve()).as_posix()
        for uri in referenced_uris(payload_artifact):
            assert relative_uri(uri) != current_receipt, (
                f"artifact depends on the receipt that validates it: "
                f"{primary_artifact.relative_to(ROOT)} -> {current_receipt}"
            )

    visiting: set[Path] = set()
    visited: set[Path] = set()

    def visit(node: Path) -> None:
        if node in visiting:
            raise AssertionError(f"indirect receipt cycle detected at {node.relative_to(ROOT)}")
        if node in visited:
            return
        visiting.add(node)
        for child in graph.get(node, []):
            visit(child)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "receipt_dirs",
        nargs="*",
        type=Path,
        help="receipt directories relative to the repository root",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    directories = args.receipt_dirs or list(DEFAULT_RECEIPT_DIRS)
    directories = [
        path if path.is_absolute() else ROOT / path
        for path in directories
    ]
    paths = receipt_paths(directories)
    check_receipt_graph(paths)
    print(f"PASS evidence graph boundaries ({len(paths)} receipts).")


if __name__ == "__main__":
    main()
