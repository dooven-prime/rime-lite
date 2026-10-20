"""Export an explicit sof-runtime source allowlist; never invoked by validation."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

from artifact_scope import RUNTIME_COMMIT, RUNTIME_FILES, SNAPSHOT_FILES, SOURCE_COMMIT, UPSTREAM, require


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")


def committed_blob(root, commit, path):
    tree_row = subprocess.check_output(
        ["git", "--no-optional-locks", "-C", str(root), "ls-tree", commit, "--", path]
    ).decode("utf-8").strip()
    require(tree_row.startswith("100644 blob ") and tree_row.endswith("\t" + path),
            "source is not a regular committed file: " + path)
    return subprocess.check_output(
        ["git", "--no-optional-locks", "-C", str(root), "show", f"{commit}:{path}"]
    )


def create_snapshot(runtime_root, upstream_root):
    subprocess.run(["git", "--no-optional-locks", "-C", str(runtime_root), "cat-file", "-e",
                    f"{RUNTIME_COMMIT}^{{commit}}"], check=True, capture_output=True)
    payload, origins = {}, {}
    for destination, relative in RUNTIME_FILES.items():
        source = "applications/event_causal_consumers/" + relative
        data = committed_blob(runtime_root, RUNTIME_COMMIT, source)
        data.decode("utf-8")
        payload[destination] = data.replace(b"\r\n", b"\n")
        origins[destination] = {"repository": "dooven-prime/sof-runtime",
                                "path": source, "content_commit": RUNTIME_COMMIT}
    payload["LICENSE"] = committed_blob(runtime_root, RUNTIME_COMMIT, "LICENSE").replace(b"\r\n", b"\n")
    origins["LICENSE"] = {"repository": "dooven-prime/sof-runtime", "path": "LICENSE",
                          "content_commit": RUNTIME_COMMIT}
    for filename in (*UPSTREAM, "LICENSE"):
        relative = "LICENSE" if filename == "LICENSE" else "experiments/paper39/" + filename
        data = subprocess.check_output(["git", "--no-optional-locks", "-C", str(upstream_root),
                                        "show", f"{SOURCE_COMMIT}:{relative}"])
        if filename in UPSTREAM:
            require(hashlib.sha256(data).hexdigest() == UPSTREAM[filename], "upstream blob drift")
        destination = "frozen/paper39/" + filename
        payload[destination] = data
        origins[destination] = {"repository": "dooven-prime/rime-lite", "path": relative,
                                "content_commit": SOURCE_COMMIT}
    require(set(payload) == SNAPSHOT_FILES, "export inventory mismatch")
    manifest = {
        "schema": "rime.paper40.q2-source.v1", "snapshot_id": "paper40-q2-source-v1",
        "implementation_owner": "dooven-prime/sof-runtime",
        "runtime_source_binding": "exact Git content commit and explicit file allowlist",
        "export_policy": "runtime UTF-8 text canonicalized to LF; frozen release blobs exact",
        "python_requires": ">=3.11", "dependencies": [], "license": "MIT",
        "files": [{"path": name, "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                   "origin": origins[name]} for name, data in sorted(payload.items())],
    }
    payload["source-manifest.json"] = json_bytes(manifest)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return stream.getvalue(), manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--upstream-root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, default=HERE / "source")
    args = parser.parse_args()
    data, manifest = create_snapshot(args.runtime_root.resolve(), args.upstream_root.resolve())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    archive = args.output_dir / "q2-source-v1.zip"
    archive.write_bytes(data)
    record = {"schema": "rime.paper40.snapshot-binding.v1", "snapshot_id": manifest["snapshot_id"],
              "archive": {"filename": archive.name, "sha256": hashlib.sha256(data).hexdigest(),
                          "size": len(data)},
              "source_manifest_sha256": hashlib.sha256(json_bytes(manifest)).hexdigest(),
              "source_manifest": manifest,
              "public_anchor": {"status": "PENDING_AUTHOR_PUBLICATION", "immutable_url": None},
              "release_identity_claimed": False}
    (args.output_dir / "snapshot.v1.json").write_bytes(json_bytes(record))
    print(json.dumps({"status": "SNAPSHOT_PREPARED_NOT_PUBLISHED", "bytes": len(data),
                      "sha256": record["archive"]["sha256"]}))


if __name__ == "__main__":
    main()
