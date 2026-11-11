"""Bind this new companion's source inputs, never its ancestors or receipts."""

import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location("rgt_companion_gate", Path(__file__).with_name("replay.py"))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def main():
    if gate.MANIFEST.exists():
        raise FileExistsError(gate.MANIFEST)
    owners = {}
    for owner, tag, paths in (
        ("paper40", "paper40-v1.0", ["papers/paper40/Paper XL.md", "experiments/paper40/source/q2-source-v1.zip",
                                      "experiments/paper40/source/snapshot.v1.json"]),
        ("c1", "fusion-log-m4d-source-v1.0", ["experiments/fusion_log_compression/m4c-development-manifest.v1.json"]),
    ):
        owners[owner] = {"tag": tag, "tag_object": gate.git("rev-parse", "refs/tags/" + tag).decode().strip(),
                         "commit": gate.git("rev-parse", tag + "^{commit}").decode().strip(),
                         "files": {name: gate.sha(gate.ROOT / name) for name in paths}}
    owners["rgt"] = {"version": "1.0-companion-candidate", "identity": "exact files in this companion manifest; not a separate paper"}
    data = {"schema": "rime.paper40.c1-rgt-companion.v1", "status": "SOURCE_CANDIDATE",
            "lean_toolchain": gate.TOOLCHAIN, "lean_commit": gate.LEAN_COMMIT, "mathlib_revision": gate.MATHLIB,
            "owners": owners, "files": {name: gate.sha(gate.ROOT / name) for name in sorted(gate.inventory())},
            "axiom_targets": {"paper40": gate.targets(gate.LEAN / "AxiomAudit.lean"),
                              "rgt": gate.targets(gate.RGT / "AxiomAudit.lean"),
                              "c1": gate.targets(gate.C1 / "lean_m4c/FusionLogInterpretation/AxiomAudit.lean")},
            "signature_targets": ["PaperXL.Consumer.RGT_iff_quotient", "PaperXL.ConsumerLogBridge.RGT_iff",
                "PaperXL.c1RunCorrespondence_initial", "PaperXL.c1QuadraticCompression_global",
                "PaperXL.c1_registered_read_failure_quadratic", "PaperXL.c1_registered_guard_failure_quadratic",
                "PaperXL.c1_registered_successor_failure_quadratic", "PaperXL.Consumer.DomainReachable"],
            "scope": "All-parameter quadratic actual prehistory certificates for arbitrary R/G/T failure on the declared C1-compatible complete Lean state, under explicit domain reachability",
            "runtime_scope": "Four fixed typed consumers on finite C1 environments; full generated-domain and edge replay only",
            "all_parameter_runtime_correspondence_proved": False, "publication_identity": None,
            "receipt_self_exclusion": True}
    gate.MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"files": len(data["files"]), "axiom_counts": {k: len(v) for k, v in data["axiom_targets"].items()}}))


if __name__ == "__main__":
    main()
