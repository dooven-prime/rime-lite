"""Validate an exact-byte release snapshot manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    snapshot_root = manifest_path.parent
    entries = manifest.get("files", [])
    errors: list[str] = []
    if manifest.get("file_count") != len(entries):
        errors.append("manifest file_count does not match files")

    seen: set[str] = set()
    for entry in entries:
        source_uri = entry.get("source_uri")
        snapshot_uri = entry.get("snapshot_uri")
        expected = entry.get("digest")
        if not isinstance(source_uri, str) or not isinstance(snapshot_uri, str):
            errors.append("snapshot entry has a malformed URI")
            continue
        if source_uri in seen:
            errors.append(f"duplicate source URI: {source_uri}")
        seen.add(source_uri)
        path = (snapshot_root / Path(*snapshot_uri.split("/"))).resolve()
        try:
            path.relative_to(snapshot_root)
        except ValueError:
            errors.append(f"snapshot URI escapes snapshot root: {snapshot_uri}")
            continue
        if not path.is_file():
            errors.append(f"snapshot file is missing: {snapshot_uri}")
            continue
        if sha256(path) != expected:
            errors.append(f"snapshot digest mismatch: {source_uri}")

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        raise SystemExit(1)
    print(
        f"Validated exact-byte release snapshot: {manifest.get('snapshot_id')} "
        f"({len(entries)} files)"
    )


if __name__ == "__main__":
    main()
