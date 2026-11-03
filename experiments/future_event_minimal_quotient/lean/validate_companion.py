"""Read-only source, pinned-dependency, build and kernel-axiom checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib


HERE = Path(__file__).resolve().parent
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def lean_code(source: str) -> str:
    """Mask nested Lean comments and ordinary strings for token linting."""
    result = list(source)
    i = 0

    def mask(start: int, end: int) -> None:
        for j in range(start, end):
            if result[j] not in "\r\n":
                result[j] = " "

    while i < len(source):
        start = i
        if source.startswith("/-", i):
            depth = 1
            i += 2
            while i < len(source) and depth:
                if source.startswith("/-", i):
                    depth += 1
                    i += 2
                elif source.startswith("-/", i):
                    depth -= 1
                    i += 2
                else:
                    i += 1
            mask(start, i)
        elif source.startswith("--", i):
            while i < len(source) and source[i] != "\n":
                i += 1
            mask(start, i)
        elif source[i] == '"':
            i += 1
            while i < len(source):
                if source[i] == "\\":
                    i = min(i + 2, len(source))
                elif source[i] == '"':
                    i += 1
                    break
                else:
                    i += 1
            mask(start, i)
        else:
            i += 1
    return "".join(result)


def check_sources(check_git: bool) -> dict:
    manifest = json.loads((HERE / "formalization-manifest.v1.json").read_text("utf-8"))
    upstream = json.loads((HERE / "upstream-manifest.json").read_text("utf-8"))
    require(manifest["schema"] == "future_event_lean_development.v1", "unknown manifest")
    bound = manifest["sha256"]
    lean_files = {p.relative_to(HERE).as_posix() for folder in ("FutureEvent", "upstream")
                  for p in (HERE / folder).rglob("*.lean")}
    lean_files.add("FutureEvent.lean")
    require(lean_files == {p for p in bound if p.endswith(".lean")},
            "Lean source inventory mismatch")
    for name, expected in bound.items():
        data = (HERE / name).read_bytes()
        require(digest(data) == expected, f"source byte drift: {name}")
        if name.endswith(".lean"):
            source = lean_code(data.decode("utf-8"))
            require(not re.search(r"(?<![.\w])(?:sorry|admit)\b|^\s*axiom\s",
                                  source, re.MULTILINE),
                    f"unfinished proof or custom axiom: {name}")
    mirror = HERE / upstream["mirror_directory"]
    require({p.name for p in mirror.glob("*.lean")} == set(upstream["sha256"]),
            "upstream mirror inventory mismatch")
    for name, expected in upstream["sha256"].items():
        require(digest((mirror / name).read_bytes()) == expected, f"owner byte drift: {name}")
        if check_git:
            ref = f'{upstream["commit"]}:{upstream["source_directory"]}/{name}'
            original = subprocess.run(
                ["git", "-C", str(HERE.parents[2]), "show", ref],
                capture_output=True, check=True,
            ).stdout
            require(digest(original) == expected, f"owner commit mismatch: {name}")
    if check_git:
        target = manifest["target_manuscript"]
        original = subprocess.run(
            ["git", "-C", str(HERE.parents[2]), "show",
             f'{target["source_commit"]}:{target["source_path"]}'],
            capture_output=True, check=True,
        ).stdout
        require(digest(original) == target["sha256"], "target manuscript commit mismatch")
    require((HERE / "lean-toolchain").read_text("utf-8").strip() == upstream["lean_toolchain"],
            "Lean toolchain drift")
    config = tomllib.loads((HERE / "lakefile.toml").read_text("utf-8"))
    require(config["require"][0]["rev"] == upstream["mathlib_commit"], "Mathlib pin drift")
    lock = json.loads((HERE / "lake-manifest.json").read_text("utf-8"))
    package = next(p for p in lock["packages"] if p["name"] == "mathlib")
    require(package["rev"] == upstream["mathlib_commit"], "resolved Mathlib drift")
    audit = (HERE / "FutureEvent/AxiomAudit.lean").read_text("utf-8")
    require(re.findall(r"^#print axioms (\S+)$", audit, re.MULTILINE) == manifest["axiom_audit"],
            "axiom-audit inventory mismatch")
    declarations = {
        f"FutureEvent.{name}"
        for path in (HERE / "FutureEvent").glob("*.lean")
        for name in re.findall(r"^(?:@\[[^\r\n]*\]\s*)?theorem\s+(\w+)",
                               path.read_text("utf-8"), re.MULTILINE)
    }
    require(declarations == set(manifest["axiom_audit"]),
            "a new theorem is missing from the axiom audit")
    return manifest


def run_lake(arguments: list[str]) -> str:
    result = subprocess.run(
        [os.environ.get("RIME_LAKE_EXE", "lake"), "--no-cache", *arguments],
        cwd=HERE, text=True, encoding="utf-8", errors="replace", capture_output=True,
    )
    require(result.returncode == 0, result.stdout + result.stderr)
    return result.stdout + result.stderr


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--check-upstream-git", action="store_true")
    args = parser.parse_args()
    manifest = check_sources(args.check_upstream_git)
    if args.source_only:
        print(json.dumps({"status": "PASS_SOURCE_ONLY", "files": len(manifest["sha256"])}))
        return 0
    version = run_lake(["env", "lean", "--version"])
    expected_version = f'version {manifest["lean_version"]}'
    require(expected_version in version and manifest["lean_commit"] in version,
            "unexpected Lean executable: " + version)
    run_lake(["build"])
    audit = run_lake(["env", "lean", "FutureEvent/AxiomAudit.lean"])
    require("sorryAx" not in audit and "Unknown constant" not in audit, audit)
    records = re.findall(
        r"'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)",
        audit,
    )
    require([name for name, _ in records] == manifest["axiom_audit"],
            "missing or unexpected kernel-axiom result:\n" + audit)
    for name, axioms in records:
        observed = {a.strip() for a in axioms.split(",") if a.strip()}
        require(observed <= ALLOWED_AXIOMS, f"unexpected axioms for {name}: {observed}")
    print(json.dumps({"status": "PASS_PARTIAL_COMPANION", "files": len(manifest["sha256"]),
                      "axiom_checks": len(records), "coverage": manifest["coverage_status"]}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, subprocess.CalledProcessError, KeyError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
