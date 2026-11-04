"""Materialize exact historical source inputs for the separate proper-arc companion."""

import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPOSITORY = "https://github.com/dooven-prime/rime-lite"
UPSTREAM = "547848ce2305daf54f0e2df049a9d5372ffdcbdc"
SOURCE = "experiments/future_event_minimal_quotient/lean"
PAPER_COMMIT = "2a30449b9dc37a36b25b277ebc006515c2addb59"
PAPER_PATH = "papers/unnumbered/proper_arc_registered_summaries/MANUSCRIPT.md"


def git_bytes(commit, path):
    return subprocess.check_output(["git", "-C", str(ROOT), "show", f"{commit}:{path}"])


def write_exact(path, data, previous=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        if previous is not None and path.read_bytes() == previous:
            path.write_bytes(data)
            return
        raise RuntimeError(f"refuse to replace different input bytes: {path}")
    if not path.exists():
        path.write_bytes(data)


def main():
    owner = json.loads(git_bytes(UPSTREAM, SOURCE + "/upstream-manifest.json"))
    hashes = {}
    for name, expected in owner["sha256"].items():
        relative = "upstream/RegisteredAbsorptionChains/" + name
        data = git_bytes(UPSTREAM, SOURCE + "/" + relative)
        sha = hashlib.sha256(data).hexdigest()
        if sha != expected:
            raise RuntimeError(f"historical owner mismatch: {name}")
        write_exact(HERE / relative, data)
        hashes[relative] = sha
    old_lock = git_bytes(UPSTREAM, SOURCE + "/lake-manifest.json")
    lock_data = json.loads(old_lock)
    lock_data["name"] = "proper_arc_registered_summaries"
    lock = (json.dumps(lock_data, indent=2) + "\n").encode()
    write_exact(HERE / "lake-manifest.json", lock, previous=old_lock)
    paper = git_bytes(PAPER_COMMIT, PAPER_PATH)
    write_exact(HERE / "reference/proper-arc-hal-v1.md", paper)
    manifest = {
        "schema": "proper_arc_lean_inputs.v1",
        "upstream_repository": REPOSITORY,
        "upstream_source_commit": UPSTREAM,
        "upstream_source_directory": SOURCE,
        "underlying_fixed_pair_commit": owner["commit"],
        "upstream_archive_url": "https://zenodo.org/records/23914476",
        "upstream_archive_file_bytes_verified_here": False,
        "lean_toolchain": owner["lean_toolchain"],
        "mathlib_commit": owner["mathlib_commit"],
        "lock_sha256": hashlib.sha256(lock).hexdigest(),
        "target_manuscript": {
            "hal_identifier": "hal-05848115v1",
            "source_tag": "proper-arc-summaries-source-v1.0",
            "source_commit": PAPER_COMMIT,
            "source_path": PAPER_PATH,
            "reference_copy": "reference/proper-arc-hal-v1.md",
            "sha256": hashlib.sha256(paper).hexdigest(),
        },
        "sha256": hashes,
        "scope": "Exact reused execution, source-order and placement-control inputs, not proper-arc theorem coverage",
    }
    previous_manifest = {**manifest, "lock_sha256": hashlib.sha256(old_lock).hexdigest()}
    write_exact(HERE / "upstream-manifest.json",
                (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode(),
                previous=(json.dumps(previous_manifest, ensure_ascii=False, indent=2) + "\n").encode())
    print(json.dumps({"status": "PASS_PINNED_INPUTS", "upstream_modules": len(hashes)}))


if __name__ == "__main__":
    main()
