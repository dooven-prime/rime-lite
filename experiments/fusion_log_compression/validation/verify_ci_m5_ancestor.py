"""Resolve M5's exact M4-D source tag independently of current HEAD."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import replay_m5 as m5


REPOSITORY = m5.ROOT.parents[1]
TAG = "fusion-log-m4d-source-v1.0"
COMMIT = "0c6bbebf19bca9d1bedc0fe63b23821b8b913d0f"
TAG_OBJECT = "f4da445f1fc39a7184786fe1cdf92cd8ec220dcd"
PREFIX = "experiments/fusion_log_compression/"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPOSITORY)


def verify():
    ref = "refs/tags/" + TAG
    if git("rev-parse", ref).decode().strip() != TAG_OBJECT:
        raise RuntimeError("M4-D tag object drift")
    if git("rev-parse", ref + "^{commit}").decode().strip() != COMMIT:
        raise RuntimeError("M4-D content commit drift")
    raw = git("show", ref + ":" + PREFIX + "m4d-development-manifest.v1.json")
    if hashlib.sha256(raw).hexdigest() != m5.M4D_MANIFEST:
        raise RuntimeError("tagged M4-D manifest drift")
    manifest = json.loads(raw)
    for name, expected in manifest["files"].items():
        data = git("show", ref + ":" + PREFIX + name)
        if hashlib.sha256(data).hexdigest() != expected:
            raise RuntimeError("tagged M4-D source drift: " + name)
    m5.verify_inputs()
    return {"status": "PASS_M5_FROZEN_M4D_SOURCE_ANCESTOR", "m4d_source_tag": TAG,
            "m4d_tag_object": TAG_OBJECT, "m4d_content_commit": COMMIT,
            "m4d_manifest_sha256": m5.M4D_MANIFEST,
            "m4d_bound_file_count": len(manifest["files"]),
            "m5_manifest_sha256": m5.m3.sha256(m5.MANIFEST), "kernel_replayed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = verify()
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
