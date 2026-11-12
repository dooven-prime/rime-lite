"""Freeze once, or verify, Paper XLIV's local finite proof milestone.

Source identity includes imported sibling Lean modules. Dependency caches and
the separately evolving manuscript/analytic layer are not frozen here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[2]
DESTINATION = HERE / "milestones" / "structure-count-v1" / "manifest.json"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
REQUIRED_TARGETS = {
    "Paper44.terminalPrefixActualEquiv",
    "Paper44.properCarrierCountEquiv",
    "Paper44.properPrefixPlacementEquiv",
    "Paper44.prefixObserverNormalEquiv",
    "Paper44.registeredPrefixObserverNormalEquiv",
    "Paper44.paperTheorem33",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_inventory() -> dict[str, str]:
    config = tomllib.loads((HERE / "lakefile.toml").read_text("utf-8"))
    libraries = config["lean_lib"]
    directories = {(HERE / lib.get("srcDir", ".")).resolve()
                   for lib in libraries}
    local_namespaces = {lib["name"] for lib in libraries}
    local_namespaces.add("RegisteredAbsorptionChains")

    def resolve(module: str) -> Path | None:
        relative = Path(*module.split(".")).with_suffix(".lean")
        explicit = [(HERE / lib.get("srcDir", ".") / relative).resolve()
                    for lib in libraries if module in lib.get("roots", [])]
        candidates = explicit or [directory / relative for directory in directories
                                  if (directory / relative).is_file()]
        candidates = sorted(set(candidates))
        if not candidates:
            require(module.split(".")[0] not in local_namespaces,
                    f"missing local import: {module}")
            return None
        require(len(candidates) == 1, f"ambiguous local import: {module}")
        require(candidates[0].is_file(), f"missing source: {module}")
        return candidates[0]

    pending = [HERE / name for name in ("Paper44.lean", "Checks.lean", "AxiomAudit.lean")]
    pending.extend((HERE / "Paper44").rglob("*.lean"))
    sources: set[Path] = set()
    while pending:
        path = pending.pop().resolve()
        if path in sources:
            continue
        sources.add(path)
        for module in re.findall(r"(?m)^import\s+([A-Za-z0-9_.]+)\s*$",
                                 path.read_text("utf-8")):
            dependency = resolve(module)
            if dependency is not None:
                pending.append(dependency)
    sources.update(HERE / name for name in (
        "lean-toolchain", "lakefile.toml", "lake-manifest.json",
        "freeze_structure_count.py",
    ))
    for relative in (
        "../../future_event_minimal_quotient/lean/upstream-manifest.json",
        "../../future_event_minimal_quotient/lean/full_summary/owner-manifest.json",
    ):
        sources.add((HERE / relative).resolve())
    return {path.relative_to(REPOSITORY).as_posix(): digest(path)
            for path in sorted(sources)}


def run(arguments: list[str]) -> str:
    completed = subprocess.run(arguments, cwd=HERE, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    require(completed.returncode == 0,
            f"{' '.join(arguments)} failed:\n{completed.stdout}")
    return completed.stdout


def audit_axioms(output: str) -> dict[str, list[str]]:
    expected = re.findall(r"(?m)^#print axioms (\S+)\s*$",
                          (HERE / "AxiomAudit.lean").read_text("utf-8"))
    actual: dict[str, list[str]] = {}
    for name, detail in re.findall(
        r"'([^']+)' (does not depend on any axioms|depends on axioms:\s*\[[^]]*\])",
        output,
    ):
        require(name not in actual, f"duplicate axiom output: {name}")
        values = [] if detail.startswith("does not") else [
            value.strip() for value in detail.split("[", 1)[1][:-1].split(",")
            if value.strip()
        ]
        require(set(values) <= ALLOWED_AXIOMS, f"unexpected axioms in {name}: {values}")
        actual[name] = sorted(values)
    require(list(actual) == expected, "axiom audit inventory/order mismatch")
    require(REQUIRED_TARGETS <= actual.keys(), "missing milestone target audit")
    return actual


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true",
                        help="create an absent local milestone; never overwrite")
    parser.add_argument("--check-only", action="store_true",
                        help="verify frozen source bytes without invoking Lean")
    args = parser.parse_args()
    require(not (args.freeze and args.check_only), "choose freeze or check-only")
    require(not args.freeze or not DESTINATION.exists(), "milestone already exists")
    before = source_inventory()
    manifest = None
    if not args.freeze:
        manifest = json.loads(DESTINATION.read_text("utf-8"))
        require(manifest["schema"] == "paper44_structure_count_milestone.v1",
                "unknown milestone schema")
        require(before == manifest["source_sha256"], "frozen proof source/inventory drift")
    if args.check_only:
        print(f"PASS: {len(before)} frozen source/configuration files; Lean not rerun")
        return 0

    version = run(["lake", "env", "lean", "--version"]).strip()
    require("version 4.33.0," in version, "Lean version drift")
    commands = [
        ["rime-lean-cache", "."],
        ["lake", "--no-cache", "build"],
        ["lake", "env", "lean", "Checks.lean"],
        ["lake", "env", "lean", "AxiomAudit.lean"],
    ]
    outputs = [run(command) for command in commands]
    axioms = audit_axioms(outputs[-1])
    require(source_inventory() == before, "proof inputs changed during validation")
    if args.freeze:
        lock = json.loads((HERE / "lake-manifest.json").read_text("utf-8"))
        manifest = {
            "schema": "paper44_structure_count_milestone.v1",
            "identity": "LOCAL_EXACT_BYTE_PROOF_MILESTONE",
            "release_identity_claimed": False,
            "independent_cold_reproduction_claimed": False,
            "repository_head_context": run(["git", "rev-parse", "HEAD"]).strip(),
            "repository_head_is_source_identity": False,
            "scope": {"n_min": 3, "depth_min": 1, "selected_pair": [0, 1],
                      "milestone": "actual normal forms and Theorem 3.3 finite counts",
                      "analytic_layer_included": False},
            "lean_version": version,
            "package_revisions": {entry["name"]: entry["rev"] for entry in lock["packages"]},
            "validation": [{"command": command, "exit_code": 0} for command in commands],
            "audit_kind": "import/source closure plus explicit Lean axiom outputs",
            "axiom_audit": axioms,
            "source_sha256": before,
        }
        DESTINATION.parent.mkdir(parents=True, exist_ok=True)
        with DESTINATION.open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
    else:
        require(version == manifest["lean_version"], "Lean identity drift")
        require(axioms == manifest["axiom_audit"], "axiom audit drift")
    print(f"PASS: {len(before)} frozen files; {len(axioms)} axiom-audited declarations; "
          f"{'milestone created' if args.freeze else 'read-only replay'}")
    print("Local cache reuse; not an independent cold-start reproduction or public release.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
