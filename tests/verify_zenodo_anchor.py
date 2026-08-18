#!/usr/bin/env python
"""Compare a local release artifact with the bytes deposited at Zenodo."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile
from urllib.request import urlopen


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record_id(value: str) -> str:
    candidate = value.rstrip("/").split("/")[-1]
    if candidate.isdigit():
        return candidate
    match = re.fullmatch(r"(?:10\.5281/)?zenodo\.(\d+)", candidate, re.IGNORECASE)
    if match:
        return match.group(1)
    raise ValueError("expected a Zenodo DOI, DOI URL, or numeric record ID")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify one actual Zenodo deposit against one local artifact."
    )
    parser.add_argument("--doi", required=True)
    parser.add_argument("--local", required=True, type=Path)
    parser.add_argument("--remote-name")
    args = parser.parse_args()

    local = args.local.resolve()
    if not local.is_file():
        parser.error(f"local artifact does not exist: {local}")
    identifier = record_id(args.doi)
    with urlopen(f"https://zenodo.org/api/records/{identifier}") as response:
        record = json.load(response)
    remote_name = args.remote_name or local.name
    matches = [item for item in record.get("files", []) if item["key"] == remote_name]
    if len(matches) != 1:
        available = [item["key"] for item in record.get("files", [])]
        raise SystemExit(
            f"remote file {remote_name!r} not found exactly once; available={available}"
        )

    remote_url = matches[0]["links"]["self"]
    with tempfile.TemporaryDirectory(prefix="rime-anchor-") as directory:
        remote = Path(directory) / remote_name
        with urlopen(remote_url) as response, remote.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        local_digest = sha256(local)
        remote_digest = sha256(remote)

    result = {
        "release_stage": "ANCHOR_CHECK",
        "anchor_status": "PASS" if local_digest == remote_digest else "FAIL",
        "doi": record.get("doi"),
        "remote_file": remote_name,
        "local_sha256": local_digest,
        "remote_sha256": remote_digest,
        "scope": "deposited file bytes only",
    }
    print(json.dumps(result, indent=2))
    return 0 if local_digest == remote_digest else 1


if __name__ == "__main__":
    raise SystemExit(main())
