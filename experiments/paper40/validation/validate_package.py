"""Read-only integrity and clean extracted-source replay for the Paper XL candidate."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import zipfile
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True
PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from artifact_scope import (ARTIFACTS, EXPECTED_CONTROLS, EXPECTED_DOMAINS, RELEASE_FILES, RUNTIME_COMMIT,
                            RUNTIME_FILES, SNAPSHOT_FILES, SOURCE_COMMIT, UPSTREAM, require)
from freeze_closure import manifest_data


def inspect_archive(data, binding):
    require(len(data) == binding["archive"]["size"] and
            hashlib.sha256(data).hexdigest() == binding["archive"]["sha256"], "archive bytes drift")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        require(len(names) == len(set(names)), "duplicate archive member")
        require(set(names) == SNAPSHOT_FILES | {"source-manifest.json"}, "archive inventory drift")
        require(sum(info.file_size for info in infos) <= 4 * 1024 * 1024, "oversized snapshot")
        for info in infos:
            path = PurePosixPath(info.filename)
            require(not path.is_absolute() and ".." not in path.parts and "\\" not in info.filename
                    and ":" not in info.filename, "unsafe archive path")
            require(info.external_attr >> 16 == 0o100644 and info.compress_type == zipfile.ZIP_STORED
                    and info.date_time == (1980, 1, 1, 0, 0, 0), "archive metadata drift")
        payload = {info.filename: archive.read(info) for info in infos}
    raw = payload.pop("source-manifest.json")
    manifest = json.loads(raw)
    require(manifest == binding["source_manifest"], "inner/outer source manifest mismatch")
    require(hashlib.sha256(raw).hexdigest() == binding["source_manifest_sha256"], "inner manifest drift")
    require(manifest.get("runtime_source_binding") == "exact Git content commit and explicit file allowlist",
            "runtime source binding drift")
    listed = {entry["path"] for entry in manifest["files"]}
    require(listed == SNAPSHOT_FILES and len(listed) == len(manifest["files"]), "source manifest inventory")
    entries = {entry["path"]: entry for entry in manifest["files"]}
    for destination, relative in (*RUNTIME_FILES.items(), ("LICENSE", "LICENSE")):
        origin = entries[destination]["origin"]
        expected_path = "LICENSE" if destination == "LICENSE" else "applications/event_causal_consumers/" + relative
        require(origin == {"repository": "dooven-prime/sof-runtime", "path": expected_path,
                           "content_commit": RUNTIME_COMMIT}, "runtime source origin drift: " + destination)
    for entry in manifest["files"]:
        value = payload[entry["path"]]
        require(len(value) == entry["size"] and hashlib.sha256(value).hexdigest() == entry["sha256"],
                "source payload drift: " + entry["path"])
    for name, digest in UPSTREAM.items():
        require(hashlib.sha256(payload["frozen/paper39/" + name]).hexdigest() == digest, "upstream drift")
    payload["source-manifest.json"] = raw
    return payload


def check_record(record):
    require(record["schema"] == "rime.paper40.q2-controls.v1", "wrong bounded record")
    cases = record["cases"]
    require(len(cases) == 9 and {x["name"] for x in cases} == set(EXPECTED_CONTROLS), "control set narrowed")
    for case in cases:
        result = case["decision"]
        require(result["status"] == EXPECTED_CONTROLS[case["name"]], "control status mismatch")
        require(result["domain_complete"] is True and result["canonical_compiler_admission"] is False,
                "incomplete/overpromoted control")
        if result["status"] != "PASS_EXACT":
            replay = case["rejection_replay"]
            require(replay["status"] == "VALID_REJECTION_WITNESS" and
                    replay["domain_completeness_verified"] is False, "invalid rejection boundary")
    for n, counts in EXPECTED_DOMAINS.items():
        result = next(x["decision"] for x in cases if x["name"] == f"gamma_n{n}")
        domain = result["domain"]
        require((domain["log_states"], domain["causal_states"]) == counts, "generated domain count drift")
    fixed = record["fixed_controls"]
    require(fixed["upstream_commit"] == SOURCE_COMMIT and fixed["upstream_blobs_sha256"] == UPSTREAM,
            "frozen source binding drift")
    require(fixed["status"] == "PASS_FIXED_CONTROLS" and len(fixed["cases"]) == 9, "fixed controls drift")
    tests = record["tests"]
    require(tests["run"] == 30 and tests["skipped"] == tests["failures"] == tests["errors"] == 0
            and len(set(tests["ids"])) == 30, "unexecuted/narrowed test suite")
    for key in ("independent_validation", "implementation_correctness_proved", "canonical_compiler_admission"):
        require(record[key] is False, "evidence overpromotion")


def bound_snapshot():
    paths = (*ARTIFACTS, "experiments/paper40/development-manifest.json")
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in paths}


def check_document_links(root, artifacts):
    """Local reader links must resolve inside the declared candidate inventory."""
    root = root.resolve()
    allowed = set(artifacts)
    for relative in artifacts:
        if not relative.endswith(".md"):
            continue
        source = root / relative
        text = source.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", text):
            parsed = urlsplit(target.strip("<>"))
            if parsed.scheme in {"http", "https", "mailto"} or not parsed.path:
                continue
            require(not parsed.scheme and not parsed.netloc, "unsupported document link: " + target)
            path = (source.parent / unquote(parsed.path)).resolve()
            require(path.is_relative_to(root), "document link escapes candidate: " + target)
            require(path.relative_to(root).as_posix() in allowed and path.is_file(),
                    "document link outside candidate closure: " + target)


def check_closure():
    actual = json.loads((PACKAGE / "development-manifest.json").read_text(encoding="utf-8"))
    require(actual == manifest_data(), "candidate closure drift; explicit rebind required")
    expected = {name for name in ARTIFACTS if name.startswith("experiments/paper40/")}
    expected.add("experiments/paper40/development-manifest.json")
    found = set()
    for directory, dirs, files in os.walk(PACKAGE):
        dirs[:] = [name for name in dirs if name != "__pycache__"]
        for name in files:
            if not name.endswith(".pyc"):
                found.add((Path(directory) / name).relative_to(ROOT).as_posix())
    require(found - RELEASE_FILES == expected, "candidate package inventory drift")
    check_document_links(ROOT, (*ARTIFACTS, "experiments/paper40/development-manifest.json",
                                *sorted(RELEASE_FILES)))


def replay(payload):
    with tempfile.TemporaryDirectory(prefix="paper40-offline-") as temporary:
        root = Path(temporary)
        source = root / "source"
        source.mkdir()
        for name, data in payload.items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        output = root / "result.json"
        env = {key: value for key, value in os.environ.items()
               if not key.upper().startswith("PYTHON") and key not in
               {"RIME_LITE_UPSTREAM", "RIME_PAPER39_SNAPSHOT"}}
        env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0", PYTHONUTF8="1")
        # No Git or other PATH executable is needed: all children use sys.executable.
        env["PATH"] = str(root / "no-external-executables")
        subprocess.run([sys.executable, "-B", str(source / "run_evidence.py"), "--output", str(output)],
                       cwd=root, env=env, check=True, timeout=240)
        result = json.loads(output.read_text(encoding="utf-8"))
        require({p.relative_to(source).as_posix() for p in source.rglob("*") if p.is_file()} == set(payload),
                "replay wrote into source")
        require(all((source / name).read_bytes() == data for name, data in payload.items()), "source mutation")
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static", action="store_true", help="integrity only; do not claim replay")
    parser.add_argument("--receipt", type=Path, help="optional local receipt outside the bound closure")
    args = parser.parse_args()
    if args.receipt:
        target = args.receipt.resolve()
        require(not target.is_relative_to(ROOT) or target.is_relative_to(ROOT / "tests/internal"),
                "an in-repository receipt belongs only under tests/internal")
        require(not target.is_relative_to(PACKAGE) and not target.is_relative_to(ROOT / "papers"),
                "receipt must not enter manuscript/package closure")
        require(target not in {(ROOT / name).resolve() for name in ARTIFACTS}, "receipt overwrites input")
    check_closure()
    before = bound_snapshot()
    binding = json.loads((PACKAGE / "source/snapshot.v1.json").read_text(encoding="utf-8"))
    payload = inspect_archive((PACKAGE / "source/q2-source-v1.zip").read_bytes(), binding)
    record = json.loads((PACKAGE / "results/q2-controls.v1.json").read_text(encoding="utf-8"))
    check_record(record)
    require(record["source_manifest_sha256"] == binding["source_manifest_sha256"], "result source mismatch")
    if not args.static:
        recomputed = replay(payload)
        check_record(recomputed)
        require(recomputed == record, "bounded recomputation differs from retained record")
        subprocess.run([sys.executable, "-B", str(PACKAGE / "validation/test_package.py")],
                       cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONOPTIMIZE": ""},
                       check=True, timeout=60)
    check_closure()
    require(before == bound_snapshot(), "validation changed bound bytes")
    receipt = {"schema": "rime.paper40.local-validation.v1", "status": "PASS",
               "validation_mode": "LOCAL_CLOSURE_VERIFICATION", "replay_performed": not args.static,
               "closure_sha256": before["experiments/paper40/development-manifest.json"],
               "archive_sha256": binding["archive"]["sha256"], "independent_validation": False,
               "public_anchor_verified": False, "release_identity_claimed": False}
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                                encoding="utf-8", newline="\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()
