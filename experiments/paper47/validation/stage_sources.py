"""Mechanically select a Paper XLVII candidate from the development checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil


PACKAGE = Path(__file__).resolve().parents[1]
REPO = PACKAGE.parents[1]
ROOTS = [
    "ClosedAudit", "ClosedSignatures",
    "RSR2History.ForestGapMomentAudit",
    "RSR2History.ForestGapMomentSignatures",
    "RSR2History.ForestRelativeReplayAudit",
    "RSR2History.ForestRelativeReplaySignatures",
    "RSR2History.AllUpperExtremaAudit",
    "RSR2History.AllUpperExtremaSignatures",
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    dest = PACKAGE / "lean"
    record = dest / "extraction-provenance.json"
    if record.exists():
        raise ValueError("candidate already staged; refusing to rewrite its source identity")
    core = source_root / "experiments/paper47/lean_single_block"
    development = source_root / "experiments/exploratory/stacked_rings_rsr2_c/lean_history"
    libraries = {
        "RSR2History": development,
        "RSR2": core,
        "RegisteredAbsorptionChains": core,
        "FusionLogCompression": core,
        "FusionLogAllR": core,
        "Paper47Closed": core, "ClosedAudit": core, "ClosedSignatures": core,
    }
    pending, seen, copies = ROOTS[:], set(), []
    while pending:
        module = pending.pop()
        if module in seen:
            continue
        seen.add(module)
        prefix = module.split(".")[0]
        if prefix in {"Mathlib", "Init", "Lean", "Std"}:
            continue
        if prefix not in libraries:
            raise ValueError(f"unresolved library: {module}")
        relative = Path(module.replace(".", "/") + ".lean")
        src, target = libraries[prefix] / relative, dest / relative
        if target.exists():
            raise ValueError(f"refusing to overwrite {target}")
        copies.append((module, src, target, digest(src)))
        for line in src.read_text(encoding="utf-8-sig").splitlines():
            if line.startswith("import "):
                pending.extend(line.split("--", 1)[0].split()[1:])
    # Every proof byte in the earlier one-block candidate must be retained.
    ancestor = source_root / "experiments/paper47/validation/single-block-source-manifest.v1.json"
    old_index = json.loads(ancestor.read_text())["sha256"]
    mapping = {q.relative_to(dest).as_posix(): h for _, _, q, h in copies}
    old_proofs = {k.removeprefix("lean_single_block/"): h for k, h in old_index.items()
                  if k.startswith("lean_single_block/") and k.endswith(".lean")}
    drift = [name for name, h in old_proofs.items() if mapping.get(name) != h]
    if drift:
        raise ValueError(f"earlier one-block proof bytes changed or omitted: {drift}")
    for _, src, target, h in copies:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        assert digest(target) == h
    shutil.copyfile(core / "lean-toolchain", dest / "lean-toolchain")
    lock = json.loads((core / "lake-manifest.json").read_text())
    if any(p["type"] != "git" for p in lock["packages"]):
        raise ValueError("ancestor lock has an external local dependency")
    lock["name"] = "paper47_companion"
    (dest / "lake-manifest.json").write_text(json.dumps(lock, indent=2)+"\n", encoding="utf-8")
    provenance_dir = PACKAGE / "provenance"
    provenance_dir.mkdir(exist_ok=True)
    shutil.copyfile(ancestor, provenance_dir / ancestor.name)
    evidence = {
        "status": "LOCAL_READER_AND_COMPANION_CANDIDATE",
        "remote_base": "43835de9ac21465412f80e8074fa8576f9a9b65c",
        "roots": ROOTS,
        "ancestor_index_sha256": digest(ancestor),
        "unchanged_ancestor_lean_sources": len(old_proofs),
        "proof_sources": [
            {"module": m, "source": p.relative_to(source_root).as_posix(),
             "target": q.relative_to(PACKAGE).as_posix(), "sha256": h}
            for m, p, q, h in sorted(copies)
        ],
        "source_paths_role": "copy provenance only; no build reads these development paths",
        "dependency_adaptation": "all local libraries mirrored; pinned git packages only",
        "publication_identity": None,
    }
    record.write_text(json.dumps(evidence, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"proof_sources": len(copies), "unchanged_ancestor_lean_sources": len(old_proofs)}))


if __name__ == "__main__":
    main()
