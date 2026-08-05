"""Build the Paper XI corpus-inclusion and upstream-admission ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "experiments" / "paper11" / "results"
LEGACY_PATH = ROOT / "experiments" / "paper11" / "archive" / "results" / "main_wall_admission_ledger_v1.json"
OUTPUT_PATH = RESULTS / "wall_record_inclusion_ledger_v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_contract(
    artifact: str,
    schema: str,
    producer: str,
    *,
    certificate: str | None = None,
    validator: str | None = None,
) -> dict:
    artifact_path = ROOT / artifact
    producer_path = ROOT / producer
    contract = {
        "schema": schema,
        "sha256": sha256(artifact_path),
        "producer": producer,
        "producer_sha256": sha256(producer_path),
    }
    if certificate is not None and validator is not None:
        contract.update(
            {
                "validation_certificate": certificate,
                "validation_certificate_sha256": sha256(ROOT / certificate),
                "validator": validator,
                "validator_sha256": sha256(ROOT / validator),
            }
        )
    return contract


EVIDENCE_OVERRIDES = {
    "A-rubik-collision-quotient": {
        "artifact": "experiments/paper11/results/rubik_collision_quotient_result_v1.json",
        "schema": "paper11-rubik-collision-result-v1.0",
        "producer": "experiments/paper11/validation/produce_collision_quotient_result.py",
        "certificate": "experiments/paper11/results/rubik_collision_quotient_validation_v1.json",
        "validator": "experiments/paper11/validation/validate_collision_quotient_result.py",
    },
    "F-rubik-type-iv-incidence": {
        "artifact": "experiments/paper11/results/route_incidence_result_v1.json",
        "schema": "paper11-route-incidence-result-v1.0",
        "producer": "experiments/paper11/validation/produce_route_incidence_result.py",
        "certificate": "experiments/paper11/results/route_incidence_validation_v1.json",
        "validator": "experiments/paper11/validation/validate_route_incidence_result.py",
    },
    "BCF-quantum-cnot-threshold": {
        "artifact": "experiments/paper11/results/cnot_logarithm_boundary_v1.json",
        "schema": "paper11-cnot-path-admissibility-v1.0",
        "producer": "experiments/paper11/cnot_logarithm_boundary.py",
    },
    "BE-nested-percolation-opening": {
        "artifact": "experiments/paper11/results/percolation_diagnostic_v1.json",
        "schema": "paper11-percolation-diagnostic-v1.0",
        "producer": "experiments/paper11/validation/percolation_diagnostic.py",
    },
}

OWNER_REFS = {
    "A-rubik-collision-quotient": "paper4",
    "A-rubik-endpoint-pair-closures": "paper11",
    "F-rubik-type-iv-incidence": "paper7",
    "BCF-quantum-cnot-threshold": "paper11",
    "BE-maze-door-wall": "paper12",
    "E-graph-edge-removal": "paper11",
    "A-constructed-goe-endpoint": "paper11",
    "BE-nested-percolation-opening": "paper11",
    "C-grn-terminal-basin-loss": "paper11",
}

CONTEXT_IDS = {
    "BCF-quantum-cnot-threshold",
    "BE-nested-percolation-opening",
}

ANALOGUE_MORPHOLOGY_IDS = {
    "BE-maze-door-wall",
    "C-grn-terminal-basin-loss",
}


def main() -> None:
    legacy = json.loads(LEGACY_PATH.read_text(encoding="utf-8"))
    records = []
    for old in legacy["records"]:
        source_id = old["source_record_id"]
        item = {
            key: value
            for key, value in old.items()
            if key not in {"admission_owner", "evidence_artifact", "evidence_contract"}
        }
        is_context = source_id in CONTEXT_IDS
        is_analogue_morphology = source_id in ANALOGUE_MORPHOLOGY_IDS
        if is_context:
            item["record_role"] = "trajectory_diagnostic"
            item["spectrum_partition"] = "context_only"
            if source_id == "BCF-quantum-cnot-threshold":
                item["primary_field"] = "diagnostic.path_logarithm_admissibility"
                item["field_family"] = "diagnostic"
                item["primary_carrier_id"] = "carrier.cnot_path_admissibility_control"
                item["domain_or_trajectory_ref"] = (
                    "paper11.cnot_affine_path_and_fractional_unitary_control"
                )
                item["orientation_or_incident_strata"] = {
                    "kind": "sampled_trajectory_context",
                    "orientation": "increasing_cnot_strength",
                    "sampling_rule": (
                        "matched 21-point affine and unitary grids; affine s=0.5 "
                        "is excluded from logarithm evaluation"
                    ),
                    "sample_context": (
                        "affine side samples 0.45 and 0.55; unitary control on [0,1]"
                    ),
                }
                item["policy_refs"] = [
                    "paper11.cnot.affine_matrix_path",
                    "paper11.cnot.affine_arg_negative=pi",
                    "paper11.cnot.fractional_unitary_path",
                    "paper11.cnot.continuous_log=i*pi*s*P_minus",
                    "paper11.cnot.tolerance=1e-6",
                    "paper11.cnot.hall_cutoff=4",
                ]
            else:
                item["primary_field"] = (
                    "word.unreached_pair_count_at_cutoff"
                    "[Y,cutoff=6,aggregation=ensemble_mean,ensemble_policy=seeded_nested_32]"
                )
                item["field_family"] = "word"
                item["orientation_or_incident_strata"] = {
                    "kind": "sampled_trajectory_context",
                    "orientation": "increasing_edge_probability",
                    "sampling_rule": "adjacent samples in the declared probability sweep",
                    "sample_context": "largest adjacent ensemble-mean drop; no declared threshold discriminant",
                }

        override = EVIDENCE_OVERRIDES.get(source_id)
        if override:
            item["evidence_artifact"] = override["artifact"]
            item["evidence_contract"] = evidence_contract(
                override["artifact"],
                override["schema"],
                override["producer"],
                certificate=override.get("certificate"),
                validator=override.get("validator"),
            )
        else:
            item["evidence_artifact"] = old["evidence_artifact"]
            item["evidence_contract"] = old["evidence_contract"]

        if is_context:
            item["claim_status"] = "Computational Observation"
        upstream_status = (
            "not_admitted"
            if is_context
            else "not_applicable"
            if is_analogue_morphology
            else "admitted"
        )
        item["upstream_wall_admission"] = {
            "status": upstream_status,
            "owner": None if is_analogue_morphology else "domain_source",
            "owner_ref": None if is_analogue_morphology else OWNER_REFS[source_id],
            "evidence_ref": None if is_analogue_morphology else item["evidence_artifact"],
        }
        entry_kind = (
            "wall_context_record" if is_context else "morphology_record_bundle"
        )
        bundle_kind = (
            None
            if is_context
            else "analogue_morphology_record"
            if is_analogue_morphology
            else "strict_wall_record"
        )
        item["paper11_corpus_inclusion"] = {
            "included": True,
            "entry_kind": entry_kind,
            "bundle_kind": bundle_kind,
            "record_role": item["record_role"],
            "provenance_ref": item["evidence_artifact"],
            "reason": (
                "retained as a bounded diagnostic with an explicit negative promotion boundary"
                if is_context
                else "included as analogue morphology without an upstream strict-wall admission claim"
                if is_analogue_morphology
                else "included after upstream admission reference and evidence-contract validation"
            ),
        }
        records.append(item)

    payload = {
        "ledger_version": "paper11-wall-record-inclusion-v1.0",
        "wall_definition_owner": "paper9",
        "ledger_owner": "paper11",
        "ledger_role": "corpus inclusion and upstream-admission reference; not wall-admission authority",
        "legacy_migration_input": {
            "path": LEGACY_PATH.relative_to(ROOT).as_posix(),
            "sha256": sha256(LEGACY_PATH),
        },
        "corpus_contract": {
            "entry_type": "WallCorpusEntry = MorphologyRecordBundle disjoint_union WallContextRecord",
            "bundle_type": "MorphologyRecordBundle = StrictWallRecord disjoint_union AnalogueMorphologyRecord",
            "strict_record_type": "RecordWall_PW maps an admissible wall datum to StrictWallRecord",
            "analogue_record_type": "analogue morphology enters through corpus inclusion, not upstream strict-wall admission",
            "record_bundle_type": "each morphology record bundle contains a finite collection of MorphologyAtom",
            "atom_type": "MorphologyAtom = TrajectoryEvent disjoint_union LocusSample",
            "counting_hierarchy": "source row -> corpus entry/bundle -> morphology atoms -> atom-field entries",
        },
        "records": records,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
