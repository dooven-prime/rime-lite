"""Shared record builders for Paper XIII SOF reports and alignments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


SOFAUDIT_VERSION = "1.0"


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _candidate_vocabulary(value: Any) -> Any:
    """Normalize learned_* keys to the target-side candidate_* diagnostics vocabulary."""
    if isinstance(value, dict):
        return {
            str(key).replace("learned", "candidate"): _candidate_vocabulary(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_candidate_vocabulary(item) for item in value]
    return value


def _comparison_specification(settings: dict) -> dict:
    """Serialize the fixed Paper XIII comparison specification Theta."""
    settings = _jsonable(settings)
    tol = settings.get("tol")
    path_samples = settings.get("path_samples")
    return {
        "specification_id": "paper13-coordinatewise-v1",
        "normalization": settings,
        "metric": {
            "signature": "coordinatewise mismatch records and counts",
            "fixed_fiber_structural": "weighted Hamming when explicitly invoked",
        },
        "depth_semantics": settings.get(
            "depth_semantics", "inherited from linked SOF Reports"
        ),
        "thresholds": (
            {"tol": tol, "source": "comparison record"}
            if tol is not None
            else {"source": "linked SOF Reports or coordinate defaults"}
        ),
        "parameter_synchronization": (
            {"mode": "index_aligned", "path_samples": path_samples}
            if path_samples is not None
            else {"mode": "not_applicable"}
        ),
        "aggregation": {
            "mode": "coordinatewise",
            "scalarization": "none",
        },
    }


def build_sofreport(
    *,
    report_id: str,
    system: str,
    sectorization: dict,
    observable_family: dict,
    audit: dict,
    claim_note: str,
    failure_modes: list[str],
    wall_record: dict | list | None = None,
    extra: dict | None = None,
) -> dict:
    """Build a conforming SOFRS v1.0 single-system report."""
    report = {
        "sofrs_version": "1.0",
        "report_id": report_id,
        "system": system,
        "sectorization": _jsonable(sectorization),
        "observable_family": _jsonable(observable_family),
        "support_matrix": {
            "kind": "word-generator direct support",
            "matrix": _jsonable(audit["R1_word"].astype(int)),
            "offdiag_count": int(audit["R1_offdiag"]),
        },
        "bridge_matrix": {
            "word": {
                "matrix": _jsonable(audit["R2_word"].astype(int)),
                "offdiag_count": int(audit["R2_word_offdiag"]),
            },
            "lie": {
                "matrix": _jsonable(audit["R2_lie"].astype(int)),
                "offdiag_count": int(audit["R2_lie_offdiag"]),
            },
            "claim_note": "word and Lie bridge channels are recorded separately",
        },
        "repair_matrix": {
            "kind": "word-depth accessibility summary",
            "depth_matrix": _jsonable(audit["D_word"]),
            "max_finite_depth": int(audit["D_word_max"]),
            "frozen_R1": int(audit["frozen_R1"]),
            "frozen_D_word": int(audit["frozen_D_word"]),
            "frozen_D_lie": int(audit["frozen_D_lie"]),
        },
        "wall_record": _jsonable(wall_record),
        "claim_status": "evidence",
        "claim_note": claim_note,
        "failure_modes": failure_modes,
    }
    if extra:
        report.update(_jsonable(extra))
    return report


def build_sofaudit(
    *,
    audit_id: str,
    system: str,
    failure_mode: str,
    reference_report_id: str,
    reference_label: str,
    candidate_report_id: str,
    candidate_label: str,
    diff: dict,
    normalization: dict,
    regime: str = "A",
    alignment: dict | None = None,
    claim_note: str = "controlled protocol validation",
    failure_modes: list[str] | None = None,
    extra: dict | None = None,
) -> dict:
    """Build a factual SOF comparison record in `.sofaudit` v1.0 form."""
    signature = {
        "support_mismatch": diff["support_mismatch"],
        "bridge_word_mismatch": diff["bridge_word_mismatch"],
        "bridge_lie_mismatch": diff["bridge_lie_mismatch"],
        "depth_distortion": diff["depth_distortion"],
        "frozen_disagreement": diff["frozen_pair_disagreement"],
        "constraint_violations": diff.get("constraint_violations"),
        "action_response_failure": diff.get("action_response_failure"),
        "wall_record_mismatch": diff.get("wall_record_mismatch"),
    }
    audit = {
        "sofaudit_version": SOFAUDIT_VERSION,
        "report_type": "sofaudit",
        "comparison_object": "SOFReportComparison",
        "audit_id": audit_id,
        "system": system,
        "claim_status": "evidence",
        "claim_note": claim_note,
        "regime": regime,
        "failure_mode": failure_mode,
        "reference": {
            "report_id": reference_report_id,
            "artifact": f"{reference_report_id}.sofreport",
            "label": reference_label,
        },
        "target": {
            "report_id": candidate_report_id,
            "artifact": f"{candidate_report_id}.sofreport",
            "label": candidate_label,
        },
        "alignment": alignment or {
            "sector_alignment": {"kind": "identity"},
            "observable_alignment": {"kind": "identity"},
        },
        "comparison_specification": _comparison_specification(normalization),
        "signature": _candidate_vocabulary(_jsonable(signature)),
        "failure_modes": failure_modes or [
            "controlled constructed variant, not a production candidate system",
            "identity alignment only",
            "audit sensitivity is relative to the declared observable family",
        ],
    }
    if extra:
        audit.update(_jsonable(extra))
    return audit


def write_artifact(payload: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_jsonable(payload), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path
