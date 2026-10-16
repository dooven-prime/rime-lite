"""Static partial-formal closure, or explicit pinned Lean compiler/axiom replay."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

LEAN = Path(__file__).resolve().parents[1] / "lean"
MANIFEST = LEAN / "formalization-manifest.json"
TOOLCHAIN = "leanprover/lean4:v4.33.0"
SOURCES = ("Paper39.lean", "Paper39/PortLookup.lean", "Paper39/ForestCounts.lean",
           "Paper39/Continuation.lean", "AxiomAudit.lean", "README.md", "lean-toolchain",
           "lakefile.toml", "lake-manifest.json")
DECLARATIONS = tuple("Paper39." + name for name in (
    "lookup_some_mem", "lookup_of_mem", "keyFunctional_perm", "lookup_perm", "collisionChildren_perm",
    "reversed_two_root_ports", "FusionTree.leaf_eq_fusion_add_one", "FusionTree.node_eq_leaf_add_fusion",
    "forest_leaf_fusion_identity", "forest_node_identity", "forest_node_bound",
    "step_domain_reflection", "execute_commutes", "execute_domain_reflection", "same_representative_path_lift"))
ALLOWED_AXIOMS = {"Classical.choice", "Quot.sound", "propext"}
COVERAGE = [
    {"source": "Paper39/PortLookup.lean", "declarations": list(DECLARATIONS[:6]),
     "checked": "functional port lookup is invariant under root-list permutations",
     "premises": "functional keys; abstract lookup, not Python refinement"},
    {"source": "Paper39/ForestCounts.lean", "declarations": list(DECLARATIONS[6:11]),
     "checked": "binary-tree and forest occurrence-count identities and node bound",
     "premises": "nonempty forest for inequality; distinct atom interpretation remains external"},
    {"source": "Paper39/Continuation.lean", "declarations": list(DECLARATIONS[11:]),
     "checked": "domain reflection, path commutation, and same-representative successor witness",
     "premises": "single-step Option-map commutation on the chosen invocation type"},
]
EXCLUDED = ["Python-to-Lean refinement", "complete concrete forest and consumer adequacy",
            "event/log and ancestor/absorption correspondence", "generated-domain closure",
            "atom-renaming adequacy", "placed UFE correspondence or external UFE implementation",
            "old B0, authorization, POS, settlement, and reset bounds"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(relative):
    raw = (LEAN / relative).read_bytes()
    require(b"\r" not in raw, f"non-LF formal source: {relative}")
    raw.decode("utf-8")
    return raw


def check_sources():
    require(read("lean-toolchain").decode().strip() == TOOLCHAIN, "formal toolchain drift")
    require(read("lakefile.toml").decode() == 'name = "paper39"\nversion = "0.1.0"\ndefaultTargets = ["Paper39"]\n\n[[lean_lib]]\nname = "Paper39"\n',
            "project configuration drift")
    lock = json.loads(read("lake-manifest.json"))
    require(lock == {"version": "1.2.0", "packagesDir": ".lake/packages", "packages": [],
                     "name": "paper39", "lakeDir": ".lake", "fixedToolchain": False}, "dependency lock drift")
    unsafe = re.compile(r"\b(?:sorry|admit|native_decide|implemented_by|extern)\b|^\s*(?:unsafe\s+|axiom\s+)|debug\.skipKernelTC",
                        re.MULTILINE)
    for source in SOURCES:
        if source.endswith(".lean"):
            text = read(source).decode()
            require(not unsafe.search(text), f"unpermitted formal shortcut: {source}")
            for dependency in re.findall(r"(?m)^import\s+(\S+)", text):
                require(dependency in {"Std", "Paper39"} or dependency.startswith("Paper39."),
                        f"undeclared formal dependency: {dependency}")
    audited = re.findall(r"(?m)^#print axioms (\S+)$", read("AxiomAudit.lean").decode())
    require(audited == list(DECLARATIONS), "axiom declaration inventory drift")


def manifest_data(axioms):
    return {"schema": "rime.paper39.lean-formalization-manifest.v1",
            "status": "COMPILED_PAPER_OWNED_PARTIAL_FORMALIZATION",
            "validation_mode": "LOCAL_CLOSURE_VERIFICATION", "toolchain": TOOLCHAIN,
            "dependencies": "bundled Std and Lean core only",
            "source_sha256": {source: hashlib.sha256(read(source)).hexdigest() for source in SOURCES},
            "audited_declarations": list(DECLARATIONS), "compiler_axioms": axioms,
            "permitted_axiom_footprint": sorted(ALLOWED_AXIOMS),
            "coverage": COVERAGE, "excluded_scope": EXCLUDED}


def check_static():
    check_sources()
    record = json.loads(MANIFEST.read_text(encoding="utf-8"))
    axioms = record.get("compiler_axioms", {})
    require(set(axioms) == set(DECLARATIONS) and all(isinstance(values, list)
            and values == sorted(set(values)) and set(values) <= ALLOWED_AXIOMS for values in axioms.values()),
            "retained axiom footprint drift")
    require(record == manifest_data(axioms), "formal source/coverage/manifest drift")
    return record


def pinned_lake():
    name = "lake.exe" if os.name == "nt" else "lake"
    canonical = Path.home() / ".elan/toolchains/leanprover--lean4---v4.33.0/bin" / name
    if canonical.is_file():
        return str(canonical)
    executable = shutil.which("lake")
    require(executable is not None, "pinned Lean/Lake installation unavailable")
    return executable


def command(*arguments, cwd=LEAN):
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    env["ELAN_TOOLCHAIN"] = TOOLCHAIN
    output = subprocess.run([pinned_lake(), *arguments], cwd=cwd, env=env,
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    require(output.returncode == 0, output.stdout + output.stderr)
    return output.stdout + output.stderr


def check_axioms(output):
    found = {name: sorted(item.strip() for item in values.split(",") if item.strip())
             for name, values in re.findall(r"'?(Paper39\.[\w.]+)'? depends on axioms:\s*\[([^\]]*)\]", output)}
    for name in re.findall(r"'?(Paper39\.[\w.]+)'? does not depend on any axioms", output):
        found[name] = []
    require(set(found) == set(DECLARATIONS), "compiler axiom inventory incomplete")
    require(all(set(axioms) <= ALLOWED_AXIOMS for axioms in found.values()), "unapproved compiler axiom")
    return found


def replay():
    before = {source: hashlib.sha256(read(source)).hexdigest() for source in SOURCES}
    with tempfile.TemporaryDirectory(prefix="paper39-lean-") as directory:
        project = Path(directory)
        for source in SOURCES:
            destination = project / source
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(LEAN / source, destination)
        require("version 4.33.0" in command("env", "lean", "--version", cwd=project), "runtime version mismatch")
        command("build", cwd=project)
        axioms = check_axioms(command("env", "lean", "AxiomAudit.lean", cwd=project))
        require(before == {source: hashlib.sha256((project / source).read_bytes()).hexdigest()
                           for source in SOURCES}, "isolated compiler replay mutated source/lock bytes")
    require(before == {source: hashlib.sha256(read(source)).hexdigest() for source in SOURCES},
            "compiler replay mutated formal source/lock bytes")
    return axioms


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--replay", action="store_true", help="compile and audit all declarations")
    mode.add_argument("--seal", action="store_true", help="authoring only: compile, audit, and seal")
    args = parser.parse_args()
    if args.seal:
        check_sources()
        record = manifest_data(replay())
        MANIFEST.write_bytes((json.dumps(record, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    else:
        record = check_static()
        if args.replay:
            require(replay() == record["compiler_axioms"], "compiler/retained axiom footprint mismatch")
    detail = "compiled and axiom-audited" if args.replay or args.seal else "static only; compiler not replayed"
    print(f"PASS: Paper XXXIX partial Lean spine; 15 declarations; {detail}")


if __name__ == "__main__":
    main()
