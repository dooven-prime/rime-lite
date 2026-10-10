#!/usr/bin/env python3
"""Bind a published Zenodo split deposit to the frozen MTS-1 sidecar."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.request import urlopen

from split_mts1_external_anchor_v1 import (
    ARCHIVE_NAME,
    SPLIT_MANIFEST_NAME,
    load_json,
    require,
    sha256_file,
    verify,
)

ANCHOR_SCHEMA = "rime.paper17.mts1-public-split-deposit-anchor.v1"
DOI_PATTERN = re.compile(r"10\.5281/zenodo\.(\d+)\Z")
BLOCK_BYTES = 8 * 1024 * 1024


def md5_file(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        while block := handle.read(BLOCK_BYTES):
            digest.update(block)
    return f"md5:{digest.hexdigest()}"


def public_record(doi: str) -> dict:
    match = DOI_PATTERN.fullmatch(doi)
    require(match is not None, "expected a Zenodo version DOI")
    url = f"https://zenodo.org/api/records/{match.group(1)}"
    with urlopen(url, timeout=30) as response:
        record = json.load(response)
    require(record["id"] == int(match.group(1)), "record ID mismatch")
    require(record["doi"] == doi, "record DOI mismatch")
    require(record["status"] == "published", "record is not published")
    return record


def build_anchor(package: Path, doi: str) -> dict:
    local_verification = verify(package)
    split_manifest = load_json(package / SPLIT_MANIFEST_NAME)
    record = public_record(doi)
    remote_files = {item["key"]: item for item in record["files"]}
    require(len(remote_files) == len(record["files"]), "duplicate Zenodo filename")
    local_names = {item.name for item in package.iterdir() if item.is_file()}
    require(set(remote_files) == local_names, "Zenodo/local file set mismatch")

    parts = split_manifest["parts"]
    part_names = [item["name"] for item in parts]
    ordered_names = part_names + sorted(local_names - set(part_names))
    files = []
    for name in ordered_names:
        remote = remote_files[name]
        local = package / name
        require(local.stat().st_size == remote["size"], f"Zenodo size mismatch: {name}")
        require(md5_file(local) == remote["checksum"], f"Zenodo MD5 mismatch: {name}")
        files.append({
            "name": name,
            "bytes": remote["size"],
            "zenodo_md5": remote["checksum"],
            "local_sha256": sha256_file(local)[0],
        })

    part_digests = {item["name"]: item["sha256"] for item in parts}
    for item in files:
        if item["name"] in part_digests:
            require(item["local_sha256"] == part_digests[item["name"]], "part SHA-256 mismatch")
    archive = split_manifest["archive"]
    require(archive["path"] == ARCHIVE_NAME, "unexpected logical archive name")
    require(local_verification["archive_sha256"] == archive["sha256"], "logical archive mismatch")
    return {
        "schema": ANCHOR_SCHEMA,
        "status": "PUBLIC_DEPOSIT_VERIFIED",
        "published_record": {
            "doi": doi,
            "record_id": record["id"],
            "url": f"https://zenodo.org/records/{record['id']}",
            "api_url": f"https://zenodo.org/api/records/{record['id']}",
            "status": record["status"],
            "revision_at_binding": record["revision"],
        },
        "split_manifest": {
            "name": SPLIT_MANIFEST_NAME,
            "bytes": (package / SPLIT_MANIFEST_NAME).stat().st_size,
            "sha256": sha256_file(package / SPLIT_MANIFEST_NAME)[0],
        },
        "logical_archive": archive,
        "exact_sidecar_identity": split_manifest["exact_sidecar_identity"],
        "ordered_part_names": part_names,
        "files": files,
        "verification": {
            "mode": "PUBLIC_ZENODO_MD5_METADATA_MATCH_AND_LOCAL_SHA256_REASSEMBLY",
            "zenodo_file_count": len(files),
            "local_reassembly_status": local_verification["status"],
            "remote_file_bytes_downloaded_for_sha256": False,
            "scientific_producer_replayed": False,
            "independent_validation": False,
        },
    }


def canonical_bytes(value: dict) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--doi", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write-anchor", type=Path)
    mode.add_argument("--check-anchor", type=Path)
    args = parser.parse_args()
    anchor = build_anchor(args.package, args.doi)
    if args.write_anchor:
        require(not args.write_anchor.exists(), "refusing to replace an anchor")
        args.write_anchor.parent.mkdir(parents=True, exist_ok=True)
        args.write_anchor.write_bytes(canonical_bytes(anchor))
        path = args.write_anchor
    else:
        path = args.check_anchor
        expected = load_json(path)
        require(expected == anchor, "public anchor no longer matches Zenodo/local bytes")
    print(json.dumps({
        "status": "PASS",
        "doi": args.doi,
        "file_count": len(anchor["files"]),
        "anchor_path": str(path),
        "anchor_sha256": sha256_file(path)[0],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
