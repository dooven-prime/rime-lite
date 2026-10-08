#!/usr/bin/env python3
"""Static verification or explicit compiler replay of the partial Lean spine."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LEAN_ROOT = ROOT / "experiments/paper37/lean"
MANIFEST = LEAN_ROOT / "formalization-manifest.json"
REVISION = "db584cd6d46c92f209a44c0f1c829460d327499d"
TOOLCHAIN = "leanprover/lean4:v4.33.0"
PROJECT = "rime_paper37_guarded_group_spine"
SOURCES = (
    "Paper37.lean",
    "Paper37/GuardedControl.lean",
    "Paper37/PhaseCosets.lean",
    "Paper37/SurvivorRestriction.lean",
    "AxiomAudit.lean",
    "README.md",
    "lakefile.toml",
    "lake-manifest.json",
    "lean-toolchain",
)
DECLARATIONS = (
    "runWord_append", "guardedReach_trans", "loopControl_inv",
    "generated_loop_control", "guardedReach_iff_mem_generated",
    "rightPhaseClass_eq_iff", "lanePhaseMap_bijective", "lanePhaseEquiv",
    "phaseDeterministic_iff_mem_normalizer", "phase_non_descent_witness",
    "survivorRestriction_eq_iff", "restrictionFiber_card",
    "terminal_card_eq_frontier_card_mul", "survivorFrontier_card_eq_div",
    "alternating_survivorFrontier_eq_full",
)
ALLOWED_AXIOMS = ("Classical.choice", "Quot.sound", "propext")
COVERAGE = (
    {
        "manuscript_role": "Lemmas 3.2--3.3; actual-word logical spine",
        "declarations": list(DECLARATIONS[:4]),
        "inputs": ["supplied uniform actual generator loops", "finite group"],
        "checked": "word concatenation at one successor; positive inverse loops; subgroup control",
    },
    {
        "manuscript_role": "Theorem 4.1; conditional reachability reduction",
        "declarations": ["guardedReach_iff_mem_generated"],
        "inputs": ["geometric edge soundness", "actual lane relocation",
                   "uniform generator-loop realization"],
        "checked": "actual guarded reachability iff membership in the generated subgroup",
    },
    {
        "manuscript_role": "Corollary 4.2; abstract state-set phase quotient",
        "declarations": list(DECLARATIONS[5:8]),
        "inputs": ["phase equivalence acts by left multiplication"],
        "checked": "lane quotient is lane times right-coset space without normality",
    },
    {
        "manuscript_role": "Proposition 4.3; exact deterministic-descent condition",
        "declarations": list(DECLARATIONS[8:10]),
        "inputs": ["finite phase subgroup"],
        "checked": "normalizer iff deterministic left update; concrete-class non-descent witness",
    },
    {
        "manuscript_role": "Corollary 5.3; survivor restriction multiplicity",
        "declarations": list(DECLARATIONS[10:14]),
        "inputs": ["five-position permutation subgroup", "terminal kernel indices zero and one"],
        "checked": "one or two extensions; exact terminal/frontier cardinality relation",
    },
    {
        "manuscript_role": "Theorem 6.3; algebraic A5/S5 survivor projection",
        "declarations": ["alternating_survivorFrontier_eq_full"],
        "inputs": ["alternating subgroup is the sign kernel"],
        "checked": "the complete finite-position survivor sets coincide",
    },
)
EXCLUDED = (
    "concrete normalized circular guard and full ordinary-lane confinement",
    "geometric legality of explicit relocation and local-generator words",
    "physical terminal-placement equality and its actual-witness converse",
    "coordinate embedding by Delta",
    "concrete F20/S5 and A5/S5 branch-generation claims",
    "finite JSON catalogue or an exhaustive subgroup classification",
    "partial occupancy, shortest or budgeted words",
    "old typed source, authorization, handoff, B0, POS, settlement, and reset bounds",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read(relative: str) -> bytes:
    raw = (LEAN_ROOT / relative).read_bytes()
    require(b"\r" not in raw, f"non-LF formal source: {relative}")
    raw.decode("utf-8")
    return raw


def expected_manifest() -> dict:
    return {
        "schema": "rime.paper37.lean-formalization-manifest.v1",
        "formalization_id": "PAPER37-GUARDED-GROUP-SPINE-V1",
        "status": "COMPILED_PAPER_OWNED_PARTIAL_FORMALIZATION",
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "entrypoint": "experiments/paper37/lean/Paper37.lean",
        "build": {
            "project_root": "experiments/paper37/lean",
            "commands": ["lake build", "lake env lean AxiomAudit.lean"],
            "lean": "4.33.0", "mathlib_revision": REVISION,
        },
        "source_sha256": {relative: hashlib.sha256(read(relative)).hexdigest()
                          for relative in SOURCES},
        "coverage": list(COVERAGE),
        "excluded_scope": list(EXCLUDED),
        "audited_declarations": ["Rime.Paper37." + name for name in DECLARATIONS],
        "permitted_axiom_footprint": list(ALLOWED_AXIOMS),
    }


def check_sources() -> None:
    require(read("lean-toolchain").decode().strip() == TOOLCHAIN, "toolchain drift")
    lakefile = read("lakefile.toml").decode()
    for marker in (f'name = "{PROJECT}"', 'defaultTargets = ["Paper37"]',
                   f'rev = "{REVISION}"'):
        require(marker in lakefile, f"lakefile drift: {marker}")
    lock = json.loads(read("lake-manifest.json"))
    require(lock.get("name") == PROJECT and lock.get("packagesDir") == ".lake/packages",
            "Lake project identity/path drift")
    mathlib = [row for row in lock.get("packages", []) if row.get("name") == "mathlib"]
    require(len(mathlib) == 1 and mathlib[0].get("rev") == REVISION
            and mathlib[0].get("inputRev") == REVISION, "Mathlib pin drift")
    unsafe = re.compile(r"\b(?:sorry|admit|native_decide)\b|^\s*(?:unsafe\s+|axiom\s+)",
                        re.MULTILINE)
    for relative in SOURCES:
        if relative.endswith(".lean"):
            source = read(relative).decode()
            require(not unsafe.search(source), f"unpermitted proof shortcut: {relative}")
            for dependency in re.findall(r"(?m)^import\s+(\S+)", source):
                require(dependency == "Paper37" or
                        dependency.startswith(("Mathlib.", "Paper37.")),
                        f"undeclared formal dependency: {dependency}")
    audit = read("AxiomAudit.lean").decode()
    expected = ["Rime.Paper37." + name for name in DECLARATIONS]
    require(re.findall(r"(?m)^#print axioms (\S+)$", audit) == expected,
            "axiom-audit inventory drift")
    prose = " ".join(read("README.md").decode().split())
    for boundary in (
        "does not prove those hypotheses for the concrete normalized circular action",
        "not a complete Lean proof of the all-g",
        "No normal-subgroup hypothesis",
        "paused B0 audit and independent forest consumer are not inputs",
    ):
        require(boundary in prose, f"formalization boundary missing: {boundary}")


def check_static() -> None:
    check_sources()
    record = json.loads(read("formalization-manifest.json"))
    require(record == expected_manifest(), "formalization manifest/source/coverage drift")


def pinned_lake() -> str:
    # Prefer the installed canonical pin over a stale short-name elan alias.
    suffix = "lake.exe" if os.name == "nt" else "lake"
    canonical = (Path.home() / ".elan/toolchains/leanprover--lean4---v4.33.0/bin" / suffix)
    if canonical.is_file():
        return str(canonical)
    executable = shutil.which("lake")
    if executable:
        return executable
    raise FileNotFoundError("pinned Lean/Lake installation is unavailable")


def command(arguments: list[str]) -> str:
    environment = os.environ.copy()
    environment.pop("PYTHONOPTIMIZE", None)
    environment["ELAN_TOOLCHAIN"] = TOOLCHAIN
    completed = subprocess.run(
        [pinned_lake(), *arguments], cwd=LEAN_ROOT, env=environment,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        check=False,
    )
    output = completed.stdout + completed.stderr
    require(completed.returncode == 0, output)
    return output


def check_axiom_output(output: str) -> None:
    found = {}
    for name, dependencies in re.findall(
        r"'?(Rime\.Paper37\.\w+)'? depends on axioms:\s*\[([^\]]*)\]", output
    ):
        found[name] = {item.strip() for item in dependencies.split(",") if item.strip()}
    for name in re.findall(
        r"'?(Rime\.Paper37\.\w+)'? does not depend on any axioms", output
    ):
        found[name] = set()
    expected = {"Rime.Paper37." + name for name in DECLARATIONS}
    require(set(found) == expected, "compiler axiom-output inventory drift")
    for name, dependencies in found.items():
        require(dependencies <= set(ALLOWED_AXIOMS),
                f"unexpected axiom footprint for {name}: {dependencies}")


def replay() -> None:
    before = {relative: hashlib.sha256(read(relative)).hexdigest() for relative in SOURCES}
    version = command(["env", "lean", "--version"])
    require("version 4.33.0" in version, "runtime Lean version differs from pin")
    command(["build"])
    check_axiom_output(command(["env", "lean", "AxiomAudit.lean"]))
    after = {relative: hashlib.sha256(read(relative)).hexdigest() for relative in SOURCES}
    require(before == after, "formal sources changed during compiler replay")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", action="store_true", help="run compiler and axiom audit")
    parser.add_argument("--seal", action="store_true",
                        help="authoring only: compile, audit, then write the formal manifest")
    args = parser.parse_args()
    if args.seal:
        check_sources()
        replay()
        MANIFEST.write_text(json.dumps(expected_manifest(), indent=2, sort_keys=True) + "\n",
                            encoding="utf-8", newline="\n")
    else:
        check_static()
        if args.replay:
            replay()
    mode = "compiled and axiom-audited" if args.replay or args.seal else "static closure checked"
    print(f"PASS: Paper XXXVII partial Lean spine; {mode}; "
          f"{len(DECLARATIONS)} audited declarations; not the full geometric proof")


if __name__ == "__main__":
    main()
