"""CI-2: check tagged HAL bytes and the live pinned proof inputs, without enumeration."""

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

import replay as m3
import replay_m4 as m4b
import replay_m4c as m4c


PACKAGE = Path(__file__).resolve().parents[1]
REPOSITORY = PACKAGE.parents[1]
TAG = "fusion-log-compression-source-v1.0"
COMMIT = "41cf746a095ecd06d85cb3d1184d58e7bfdd5979"
HAL_MANIFEST = "papers/unnumbered/fusion_log_compression/source-manifest.v1.json"
M4B_MANIFEST_SHA256 = "69456464ff271024c8ab9e97694d5c8fdf125db3c309aadf98fded7fb07612ed"


def git(*args):
    result = subprocess.run(["git", *args], cwd=REPOSITORY, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
    return result.stdout


def verify_tagged_hal():
    ref = "refs/tags/" + TAG
    if git("cat-file", "-t", ref).strip() != b"tag":
        raise RuntimeError("missing annotated HAL source tag")
    if git("rev-parse", ref + "^{commit}").decode().strip() != COMMIT:
        raise RuntimeError("HAL tag commit drift")
    raw = git("show", ref + ":" + HAL_MANIFEST)
    manifest = json.loads(raw)
    if manifest["source_tag_name"] != TAG or manifest["evidence_boundary"] != \
            "PAPER_PROOFS_AND_BOUNDED_CONSISTENCY_CONTROLS":
        raise RuntimeError("HAL manifest identity mismatch")
    expected = manifest["sha256"]
    if len(expected) != 21:
        raise RuntimeError("HAL source inventory drift")
    for name in expected:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name:
            raise RuntimeError("unsafe tagged path")
    contents = {}
    archive = git("archive", "--format=tar", ref, "--", HAL_MANIFEST, *sorted(expected))
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        for member in stream:
            if member.isfile():
                if member.name in contents:
                    raise RuntimeError("duplicate tagged file")
                contents[member.name] = stream.extractfile(member).read()
            elif not member.isdir():
                raise RuntimeError("nonregular tagged source")
    if set(contents) != set(expected) | {HAL_MANIFEST}:
        raise RuntimeError("tagged HAL inventory mismatch")
    for name, digest in expected.items():
        if hashlib.sha256(contents[name]).hexdigest() != digest:
            raise RuntimeError("tagged HAL source drift: " + name)
    return hashlib.sha256(raw).hexdigest()


def verify():
    hal_manifest_sha256 = verify_tagged_hal()
    m4c.verify_inputs()
    if m3.sha256(m4b.MANIFEST) != M4B_MANIFEST_SHA256:
        raise RuntimeError("frozen M4-B manifest drift")
    return {"status": "PASS_CI1_CI2_ANCESTOR_IDENTITIES",
            "hal_source_tag": TAG, "hal_content_commit": COMMIT,
            "hal_manifest_sha256": hal_manifest_sha256, "hal_bound_file_count": 21,
            "hal_bytes_read_from_fixed_tag_not_current_head": True,
            "m4b_manifest_sha256": M4B_MANIFEST_SHA256,
            "m4c_manifest_sha256": m3.sha256(m4c.MANIFEST),
            "kernel_replayed_by_this_gate": False,
            "mathematical_controls_reexecuted": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.report is not None and args.report.exists():
        raise FileExistsError(args.report)
    result = verify()
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
