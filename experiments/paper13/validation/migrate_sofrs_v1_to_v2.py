"""Create alignment-ready SOFRS v2 source reports for Paper XIII inputs.

Paper XIII consumes only SOFRS v2 reports. The older Paper XIII report
envelopes remain immutable inputs to this Paper XII-owned migration bridge.
This adapter preserves their finite typed payloads, but gives them the same
CompilerOutput-bound report and v2 validation-receipt closure used elsewhere
in the RIME program.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from schemas.contract_api import file_digest
from schemas.sofrs.api import build_v2_report_validation_receipt


HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
ROOT = PAPER_DIR.parents[1]
LEGACY_DIR = PAPER_DIR / "archive" / "results"
V2_DIR = PAPER_DIR / "results" / "source-reports"
MANIFEST_DIR = V2_DIR / "manifests"
IR_DIR = V2_DIR / "ir"
OUTPUT_DIR = V2_DIR / "compiler-output"
REPORT_DIR = V2_DIR / "reports"
RECEIPT_DIR = V2_DIR / "receipts"
PAPER12_VALIDATOR = ROOT / "experiments" / "paper12" / "validation" / "validate_sofrs_v2.py"

PRODUCERS = {
    "compiler": "compiler_ir_sof.py",
    "gridworld": "gridworld_reference_sof.py",
    "network": "network_routing_sof.py",
    "sir": "sir_compartment_sof.py",
    "traffic": "traffic_intersection_sof.py",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def uri(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def classification(name: str, legacy: dict) -> dict:
    prefix = name.split("_", 1)[0]
    dimension = legacy.get("sectorization", {}).get("sector_count")
    if dimension is None:
        dimension = len(legacy.get("sectorization", {}).get("blocks", []))
    return {
        "record_kind": "diagnostic_analogue",
        "enumerable_reconstruction_obligations": False,
        "dimension": dimension,
        "domain": f"Paper XIII {prefix} finite control",
        "source_type": "frozen Paper XIII SOFRS v1 report envelope",
        "producer": PRODUCERS.get(prefix, "report_contract.py"),
        "labels_from": "blocks",
        "word": True,
        "proxy": False,
        "cutoff": legacy.get("repair_matrix", {}).get("max_finite_depth", 4),
        "negative_boundary": (
            "This v2 source report preserves the finite source envelope; it does not establish an independent object-level oracle or cross-report semantic alignment."
        ),
        "reason": (
            "The report is migrated from a frozen Paper XIII SOFRS v1 envelope into the Paper XII v2 CompilerOutput-bound report contract."
        ),
    }


def migrate_one(module, legacy_path: Path) -> tuple[Path, Path, dict]:
    name = legacy_path.stem
    legacy = load(legacy_path)
    cls = classification(name, legacy)
    normalized_bridge, bridge_count = module.replace_unreached(legacy.get("bridge_matrix"))
    normalized_repair, repair_count = module.replace_unreached(legacy.get("repair_matrix"))
    normalized_wall, wall_count = module.replace_unreached(legacy.get("wall_record"))
    normalized_bridge, normalized_repair, normalized_wall, semantic_normalizations = module.normalize_semantic_labels(
        name, normalized_bridge, normalized_repair, normalized_wall
    )
    has_unreached = bridge_count + repair_count + wall_count > 0
    sectorization = legacy.get("sectorization", {})
    labels = None
    manifest = module.build_manifest(name, legacy, cls, labels, has_unreached)
    manifest_path = MANIFEST_DIR / f"{name}.capabilities.json"
    write(manifest_path, manifest)
    ir = module.build_ir(
        name, legacy_path, legacy, manifest_path, manifest, cls, labels,
        normalized_bridge, normalized_repair, normalized_wall, has_unreached,
    )
    ir_path = IR_DIR / f"{name}.ir.json"
    write(ir_path, ir)
    compiler_profile_path = module.ANALOGUE_COMPILER_PROFILE
    assembly_profile_path = module.ANALOGUE_ASSEMBLY_PROFILE
    profile = load(compiler_profile_path)
    rules = load(module.RULE_REGISTRY_PATH)
    output = module.compile_output_v1(manifest, ir, profile, rules)
    output_path = OUTPUT_DIR / f"{name}.compiler-output.json"
    write(output_path, output)
    report = module.assemble_sofrs_report(
        legacy_path, legacy, manifest_path, ir_path, compiler_profile_path,
        assembly_profile_path, output_path, manifest, ir, output, cls,
        bridge_count + repair_count + wall_count,
    )
    report["provenance"]["semantic_normalizations"] = semantic_normalizations
    report_path = REPORT_DIR / f"{name}.sofreport.json"
    write(report_path, report)
    index_entry = {
        "source": uri(legacy_path),
        "source_digest": module.sha256(legacy_path),
        "producer": uri(PAPER_DIR / cls["producer"]),
        "producer_digest": module.sha256(PAPER_DIR / cls["producer"]),
        "record_kind": cls["record_kind"],
        "strict_reconstruction": module.reconstruction_assessment(cls),
        "manifest": uri(manifest_path),
        "ir": uri(ir_path),
        "compiler_output": uri(output_path),
        "compiler_profile": uri(compiler_profile_path),
        "assembly_profile": uri(assembly_profile_path),
        "report": uri(report_path),
        "classification_reason": cls["reason"],
        "normalized_legacy_sentinel_count": bridge_count + repair_count + wall_count,
    }
    validator = importlib.import_module("experiments.paper12.validation.validate_sofrs_v2")
    validator.CLASSIFICATIONS[name] = cls
    schemas = {
        "manifest": load(validator.MANIFEST_SCHEMA_PATH),
        "ir": load(validator.IR_SCHEMA_PATH),
        "profile": load(validator.PROFILE_SCHEMA_PATH),
        "assembly_profile": load(validator.ASSEMBLY_PROFILE_SCHEMA_PATH),
        "compiler_output": load(validator.COMPILER_OUTPUT_SCHEMA_PATH),
        "report": load(validator.REPORT_SCHEMA_PATH),
    }
    validation_errors = validator.validate_record(index_entry, schemas, rules)
    if validation_errors:
        raise ValueError(f"{report_path}: " + "; ".join(validation_errors))
    receipt = build_v2_report_validation_receipt(
        report_path,
        report_uri=uri(report_path),
        validator_path=PAPER12_VALIDATOR,
        validator_uri="experiments/paper12/validation/validate_sofrs_v2.py",
    )
    receipt_path = RECEIPT_DIR / f"{name}.validation-receipt.json"
    write(receipt_path, receipt)
    return report_path, receipt_path, index_entry


def main() -> None:
    module = importlib.import_module("experiments.paper12.validation.migrate_sofrs_v1_to_v2")
    module.PAPER_DIR = PAPER_DIR
    module.MANIFEST_DIR = MANIFEST_DIR
    module.IR_DIR = IR_DIR
    module.COMPILER_OUTPUT_DIR = OUTPUT_DIR
    module.REPORT_DIR = REPORT_DIR
    reports = []
    for legacy_path in sorted(LEGACY_DIR.glob("*.sofreport")):
        report_path, receipt_path, index_entry = migrate_one(module, legacy_path)
        reports.append({
            **index_entry,
            "report": uri(report_path),
            "report_digest": {"algorithm": "sha256", "value": file_digest(report_path)},
            "receipt": uri(receipt_path),
            "receipt_digest": {"algorithm": "sha256", "value": file_digest(receipt_path)},
        })
    write(V2_DIR / "migration-index.json", {
        "migration_version": "2.0",
        "source_contract": "SOFRS v1.0",
        "target_contract": "SOFRS v2.0",
        "adapter_id": "paper13-sofrs-v1-to-v2",
        "adapter_version": "2.0",
        "records": reports,
    })
    print(f"Migrated {len(reports)} Paper XIII source reports to SOFRS v2.")


if __name__ == "__main__":
    main()
