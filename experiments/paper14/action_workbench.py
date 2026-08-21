"""Generate Paper XIV v2 objects from current Paper XIII SOFAUDIT artifacts."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUDIT_DIR = ROOT / "experiments" / "paper13" / "results" / "audits"
NATIVE_AUDIT = (
    ROOT
    / "experiments"
    / "paper13"
    / "results"
    / "native"
    / "gridworld-f4"
    / "audits"
    / "gridworld-f4-native-v2.sofaudit.json"
)
RESULT_DIR = HERE / "results"
sys.path.insert(0, str(HERE))

from action_engine import (  # noqa: E402
    ACTION_CONTEXT_CONTRACT_VERSION,
    ACTION_CONTEXT_REVISION,
    DEFAULT_POLICY_PROFILE,
    build_action_record,
)


MIGRATION_STEMS = [
    *(f"gridworld_f{i}" for i in range(1, 6)),
    *(f"sir_f{i}" for i in range(1, 6)),
    *(f"traffic_f{i}" for i in range(1, 6)),
    *(f"compiler_f{i}" for i in range(1, 6)),
    *(f"network_f{i}" for i in range(1, 6)),
    "before_after_compiler",
    "before_after_traffic",
    "before_after_gridworld",
]


def load_audit(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("sofaudit_version") != "2.0":
        raise ValueError(f"{path} is not a current SOFAUDIT v2 artifact")
    return payload


def declared_action_context(audit: dict[str, Any]) -> dict[str, Any]:
    native = audit.get("provenance", {}).get("kind") != "migration"
    comparison_role = "failure_mode_control" if native else "diagnostic_comparison"
    return {
        "context_id": f"paper14:{audit['audit_id']}:action-context-v2",
        "context_contract_version": ACTION_CONTEXT_CONTRACT_VERSION,
        "context_revision": ACTION_CONTEXT_REVISION,
        "actor": {
            "actor_id": "paper14-workbench",
            "role": "analysis_producer",
            "description": "Paper XIV controlled interpretation workbench",
        },
        "scope": {
            "scope_id": f"audit:{audit['audit_id']}",
            "description": "Interpret only the retained coordinates of this Paper XIII audit.",
            "audit_id": audit["audit_id"],
        },
        "objective": {
            "objective_id": "bounded-diagnostic-interpretation",
            "statement": "Separate licensed change, review need, and unresolved evidence without issuing an execution command.",
        },
        "constraints": [
            {
                "constraint_id": "preserve-audit-projection",
                "statement": "The Paper XIII audit projection is immutable at this layer.",
                "status": "binding",
            },
            {
                "constraint_id": "no-action-from-unresolved",
                "statement": "UNRESOLVED and NOT_DECLARED coordinates cannot support affirmative candidates.",
                "status": "binding",
            },
        ],
        "time": {
            "kind": "source_snapshot",
            "start": None,
            "end": None,
            "timezone": None,
            "basis": "inherited from the source-addressed audit artifact",
        },
        "authority": {
            "authority_id": "paper14-analysis-only",
            "status": "not_authorized",
            "description": "This record has no authority to execute, approve, or select an action.",
            "actor_ids": ["paper14-workbench"],
            "scope_ids": [f"audit:{audit['audit_id']}"],
        },
        "uncertainty_conditions": [
            "source comparison states are retained exactly",
            "unresolved or not-declared coordinates block affirmative action",
            "candidate effect, feasibility, safety, and authorization remain unverified",
        ],
        "comparison_role": comparison_role,
        "mismatch_direction": "reference_to_target",
        "contract_status": "not_applicable" if not native else "nonconforming",
        "evaluator_qualification_note": "native object certificate is bound upstream" if native else "migration preservation only",
        "transformation_contract_refs": [],
        "negative_boundary": [
            "Reference role is not a truth or defect authority.",
            "A candidate action is not a recommendation, command, or causal-effect claim.",
        ],
    }


def _write_json(payload: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _artifact_reference(path: Path) -> dict[str, Any]:
    return {
        "uri": path.relative_to(ROOT).as_posix(),
        "digest": {
            "algorithm": "sha256",
            "value": hashlib.sha256(path.read_bytes()).hexdigest(),
        },
    }


def _summary_row(record: dict[str, Any]) -> dict[str, Any]:
    context = record.get("action_context") or {}
    actions = record["candidate_action_set"]["actions"]
    interpretations = record["interpretation_records"]
    return {
        "case": record["source_audit"]["audit_id"],
        "source_kind": (
            "native"
            if record["source_audit"]["audit_id"] == "gridworld-f4-native-v2"
            else "migration"
        ),
        "context_role": context.get("comparison_role", "inconclusive"),
        "context_admission": record["context_admission"]["status"],
        "policy_admission": record["policy_admission"]["status"],
        "interpretations": sorted({item["assessment_kind"] for item in interpretations}),
        "candidate_count": len(actions),
        "dispositions": sorted({item["disposition"] for item in actions}),
    }


def _markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Paper XIV SOF Action Workbench v2",
        "",
        "| Case | Context | Context admission | Policy admission | Assessments | Candidate count | Dispositions |",
        "|------|---------|-------------------|------------------|-------------|-----------------:|--------------|",
    ]
    for row in rows:
        lines.append(
            "| {case} | {context_role} | {context_admission} | {policy_admission} | {interpretations} | {candidate_count} | {dispositions} |".format(
                case=row["case"],
                context_role=row["context_role"],
                context_admission=row["context_admission"],
                policy_admission=row["policy_admission"],
                interpretations=", ".join(row["interpretations"]) or "none",
                candidate_count=row["candidate_count"],
                dispositions=", ".join(row["dispositions"]) or "none",
            )
        )
    lines.extend(
        [
            "",
            "The migrated Paper XIII records retain UNRESOLVED or NOT_DECLARED coordinates and therefore produce no affirmative candidates.",
            "The native GridWorld F4 record is the only current factual v2 input in this workbench.",
            "Candidates are bounded records, not execution commands or objective recommendations.",
            "",
        ]
    )
    return "\n".join(lines)


def run(output_dir: Path) -> list[dict[str, Any]]:
    output_dir = output_dir.resolve()
    if output_dir == RESULT_DIR.resolve():
        raise ValueError(
            "the published Paper XIV v2.0 result directory is immutable; "
            "choose an explicit replay directory"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    specs = [
        (stem, AUDIT_DIR / f"{stem}.sofaudit.json", f"{stem}.sofaction")
        for stem in MIGRATION_STEMS
    ]
    specs.append(("gridworld_f4_native", NATIVE_AUDIT, "gridworld_f4_native.sofaction"))
    records: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for stem, path, output_name in specs:
        audit = load_audit(path)
        context = declared_action_context(audit)
        policy = deepcopy(DEFAULT_POLICY_PROFILE)
        source_artifact = path.relative_to(ROOT).as_posix()
        record = build_action_record(
            action_record_id=f"{stem}-actions-v2",
            audit=audit,
            source_artifact=source_artifact,
            action_context=context,
            policy_profile=policy,
        )
        _write_json(record, output_dir / output_name)
        records.append(record)
        rows.append(_summary_row(record))

    summary = _markdown(rows)
    (output_dir / "action_summary.md").write_text(summary, encoding="utf-8")
    source_artifacts = [
        {
            "case": row["case"],
            **_artifact_reference(output_dir / output_name),
        }
        for row, (_, _, output_name) in zip(rows, specs, strict=True)
    ]
    _write_json(
        {
            "summary_version": "1.0",
            "source_artifacts": source_artifacts,
            "records": rows,
        },
        output_dir / "action_summary.json",
    )
    print(summary)
    print(f"Wrote {len(records)} v2 replay .sofaction artifacts to {output_dir}")
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="explicit non-release directory for a v2 replay",
    )
    run(parser.parse_args().output_dir)
