#!/usr/bin/env python3
"""Check the selected Lean algebraic spine; explicit compiler/axiom replay."""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LEAN_ROOT = ROOT / "experiments/paper38/lean"
MANIFEST = LEAN_ROOT / "formalization-manifest.json"
REVISION = "db584cd6d46c92f209a44c0f1c829460d327499d"
TOOLCHAIN = "leanprover/lean4:v4.33.0"
PROJECT = "rime_paper38_return_budget_spine"
SOURCES = (
    "Paper38.lean", "Paper38/ReturnLayers.lean", "Paper38/Saturation.lean",
    "Paper38/InitialLayerControl.lean", "AxiomAudit.lean", "README.md",
    "lakefile.toml", "lake-manifest.json", "lean-toolchain",
)
DECLARATIONS = (
    "exactLayer_eq_power", "mem_exactLayer_iff_product_word", "mem_cumulativeLayer_iff",
    "cumulativeLayer_eq_union", "cumulativeLayer_mono", "cumulativeLayer_nonempty",
    "cumulativeLayer_leftStable", "positiveClosure_eq_subgroup", "no_premature_stall",
    "cumulative_stall_iff_full", "phaseCoset_card", "phaseCoset_subset", "phaseCoset_leftStable",
    "phaseAggregate_leftStable", "local_mem_phaseAggregate", "phaseAggregate_closure",
    "phaseCoset_disjoint", "stable_strict_growth", "cumulative_card_growth",
    "cumulative_card_lower_bound", "cumulative_full_at_index", "at_most_index_product_word",
    "five_phase_index_le_twentyFour", "uniform_twentyFour_product_word",
    "initial_layers_disjoint", "initial_layers_equal_card", "initial_layers_differ",
    "full_aggregate_mul_nonempty", "initial_separation_second_recovery", "matched_survivor_reads_differ",
)
ALLOWED_AXIOMS = ("Classical.choice", "Quot.sound", "propext")
COVERAGE = (
    {"manuscript_role": "Theorem 3.1: algebraic layer and product-word part",
     "declarations": list(DECLARATIONS[:7]),
     "inputs": ["finite factor sets A and B", "index n counts n+1 charged factors"],
     "checked": "positive exact layers, cumulative union, retained initial factor, and left stability"},
    {"manuscript_role": "Lemmas 4.1--4.3: closure and cumulative growth",
     "declarations": list(DECLARATIONS[7:20]),
     "inputs": ["finite ambient generated group", "A generates that group", "nonempty B",
                "A and B invariant under left phase multiplication"],
     "checked": "positive closure, aggregate generation, no stall, and whole-phase-block growth"},
    {"manuscript_role": "Theorem 4.4: algebraic cumulative budget",
     "declarations": list(DECLARATIONS[20:24]),
     "inputs": ["finite generated group", "nonempty left-phase-stable initial factor",
                "order-five phase subgroup of a subgroup of S5"],
     "checked": "index saturation and an algebraic product witness with at most 24 charged factors"},
    {"manuscript_role": "Theorem 5.1: finite D10 initial-layer control",
     "declarations": list(DECLARATIONS[24:]),
     "inputs": ["abstract DihedralGroup 5", "common full aggregate"],
     "checked": "distinct equal-size first layers, full second cumulative layers, and distinct fixed survivor reads"},
)
EXCLUDED = (
    "concrete normalized circular actions and full ordinary-lane guard geometry",
    "actual chronological label words and same-representative raw path realization",
    "complete survivor restriction theorem and physical coordinate embedding",
    "all-g reflection-location family",
    "conditional 24n original-letter corollary and Appendix A controls",
    "finite JSON catalogue, sharp constant, exact-24 padding, and shortest raw words",
    "typed source, authorization, transfer, handoff, B0, POS, settlement, and reset bounds",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(relative):
    raw = (LEAN_ROOT / relative).read_bytes()
    require(b"\r" not in raw, f"non-LF formal source: {relative}")
    raw.decode("utf-8")
    return raw


def expected_manifest():
    return {
        "schema": "rime.paper38.lean-formalization-manifest.v1",
        "formalization_id": "PAPER38-RETURN-BUDGET-ALGEBRA-SPINE-V1",
        "status": "COMPILED_PAPER_OWNED_PARTIAL_FORMALIZATION",
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "entrypoint": "experiments/paper38/lean/Paper38.lean",
        "build": {"project_root": "experiments/paper38/lean", "lean": "4.33.0",
                  "mathlib_revision": REVISION, "commands": ["lake build", "lake env lean AxiomAudit.lean"]},
        "source_sha256": {path: hashlib.sha256(read(path)).hexdigest() for path in SOURCES},
        "coverage": list(COVERAGE), "excluded_scope": list(EXCLUDED),
        "audited_declarations": ["Rime.Paper38." + name for name in DECLARATIONS],
        "permitted_axiom_footprint": list(ALLOWED_AXIOMS),
    }


def check_sources():
    require(read("lean-toolchain").decode().strip() == TOOLCHAIN, "toolchain drift")
    config = read("lakefile.toml").decode()
    for marker in (f'name = "{PROJECT}"', 'defaultTargets = ["Paper38"]', f'rev = "{REVISION}"'):
        require(marker in config, f"Lake config drift: {marker}")
    lock = json.loads(read("lake-manifest.json"))
    require(lock.get("name") == PROJECT and lock.get("packagesDir") == ".lake/packages", "lock identity drift")
    dependencies = [row for row in lock.get("packages", []) if row.get("name") == "mathlib"]
    require(len(dependencies) == 1 and dependencies[0].get("rev") == REVISION
            and dependencies[0].get("inputRev") == REVISION, "Mathlib pin drift")
    unsafe = re.compile(r"\b(?:sorry|admit|native_decide)\b|^\s*(?:unsafe\s+|axiom\s+)", re.MULTILINE)
    for relative in SOURCES:
        if relative.endswith(".lean"):
            text = read(relative).decode()
            require(not unsafe.search(text), f"unpermitted proof shortcut: {relative}")
            for dependency in re.findall(r"(?m)^import\s+(\S+)", text):
                require(dependency == "Paper38" or dependency.startswith(("Mathlib.", "Paper38.")),
                        f"undeclared formal dependency: {dependency}")
    audited = re.findall(r"(?m)^#print axioms (\S+)$", read("AxiomAudit.lean").decode())
    require(audited == ["Rime.Paper38." + name for name in DECLARATIONS], "axiom inventory drift")
    prose = " ".join(read("README.md").decode().split())
    for marker in ("not a complete Lean proof of the all-g geometric theorem",
                   "No normality or normalizer hypothesis", "n = 0",
                   "finite JSON database is not imported", "not as uncharged physical return steps"):
        require(marker in prose, f"coverage firewall missing: {marker}")


def check_static():
    check_sources()
    require(json.loads(read("formalization-manifest.json")) == expected_manifest(),
            "formal manifest/source/coverage drift")


def pinned_lake():
    suffix = "lake.exe" if os.name == "nt" else "lake"
    canonical = Path.home() / ".elan/toolchains/leanprover--lean4---v4.33.0/bin" / suffix
    if canonical.is_file():
        return str(canonical)
    if executable := shutil.which("lake"):
        return executable
    raise FileNotFoundError("pinned Lean/Lake installation unavailable")


def command(arguments):
    environment = os.environ.copy()
    environment.pop("PYTHONOPTIMIZE", None)
    environment["ELAN_TOOLCHAIN"] = TOOLCHAIN
    completed = subprocess.run([pinned_lake(), *arguments], cwd=LEAN_ROOT, env=environment,
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
    output = completed.stdout + completed.stderr
    require(completed.returncode == 0, output)
    return output


def check_axioms(output):
    found = {name: {item.strip() for item in footprint.split(",") if item.strip()}
             for name, footprint in re.findall(
                 r"'?(Rime\.Paper38\.\w+)'? depends on axioms:\s*\[([^\]]*)\]", output)}
    for name in re.findall(r"'?(Rime\.Paper38\.\w+)'? does not depend on any axioms", output):
        found[name] = set()
    require(set(found) == {"Rime.Paper38." + name for name in DECLARATIONS}, "compiler audit inventory drift")
    for name, dependencies in found.items():
        require(dependencies <= set(ALLOWED_AXIOMS), f"unpermitted axioms: {name}: {dependencies}")


def replay():
    before = {path: hashlib.sha256(read(path)).hexdigest() for path in SOURCES}
    require("version 4.33.0" in command(["env", "lean", "--version"]), "runtime toolchain mismatch")
    actual = subprocess.check_output(["git", "-C", str(LEAN_ROOT / ".lake/packages/mathlib"),
                                      "rev-parse", "HEAD"]).decode().strip()
    require(actual == REVISION, "runtime Mathlib revision mismatch")
    command(["build"])
    check_axioms(command(["env", "lean", "AxiomAudit.lean"]))
    require(before == {path: hashlib.sha256(read(path)).hexdigest() for path in SOURCES},
            "compiler replay mutated formal sources")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--replay", action="store_true", help="compile and audit axioms")
    modes.add_argument("--seal", action="store_true", help="authoring only: compile, audit, then seal digests")
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
    print(f"PASS: Paper XXXVIII partial Lean algebraic spine; {mode}; 30 audited declarations")


if __name__ == "__main__":
    main()
