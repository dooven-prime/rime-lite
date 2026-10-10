#!/usr/bin/env python3
"""Bind candidate-2 without rewriting candidate-1 or scientific outcomes."""

from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from pathlib import Path

from build_release_manifest import IDENTITY_CLASSES, closure_digest, sha256_file


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
PREVIOUS = ROOT / "release-manifest.v1.json"
MANIFEST = ROOT / "release-manifest.v2.json"
TABLE = ROOT / "manuscript-evidence-table.v2.json"
RECEIPT = "experiments/paper17/results/release.v2.validation-receipt.json"
SNAPSHOT = "release-snapshots/paper17/1.0-candidate-1"
REPLACED = (
    "papers/paper17/Paper XVII.md",
    "papers/paper17/paper17_arxiv.pdf",
    "experiments/paper17/00_START_HERE.md",
    "experiments/paper17/release-environment.json",
    "figures/paper17/render_fig1.py",
    "figures/paper17/fig1_transient_separation_and_safe_forgetting.png",
    "figures/paper17/render_fig2.py",
    "figures/paper17/fig2_internal_transition_layer_contrast.png",
    "figures/paper17/requirements.txt",
)
DRIVE = "experiments/paper17/mechanism/post_result_audits/persistent_safe_effective_drive.v1.json"
AUDIT = "experiments/paper17/mechanism/validation/audit_persistent_safe_effective_drive_v1.py"
NEW_ARTIFACTS = (
    ("current-evidence-table", "theorem-facing-computational", "experiments/paper17/manuscript-evidence-table.v2.json"),
    ("persistent-drive-readout", "theorem-facing-computational", DRIVE),
    ("persistent-drive-replay", "release-validation", AUDIT),
    ("persistent-drive-note", "public-package-documentation", "experiments/paper17/mechanism/post_result_audits/EFFECTIVE_DRIVE_BOUNDARY.md"),
    ("candidate-2-builder", "release-validation", "experiments/paper17/build_publication_candidate_v2.py"),
    ("candidate-2-validator", "release-validation", "experiments/paper17/validation/validate_release_v2.py"),
    ("candidate-2-hostile-tests", "release-validation", "experiments/paper17/validation/test_publication_candidate_v2.py"),
    ("figure-line-ending-policy", "release-validation", "figures/paper17/.gitattributes"),
    ("historical-snapshot-byte-policy", "release-validation", "release-snapshots/paper17/.gitattributes"),
    ("candidate-1-manifest", "historical-candidate-input", "experiments/paper17/release-manifest.v1.json"),
    ("candidate-1-receipt", "historical-candidate-input", "experiments/paper17/results/release.v1.validation-receipt.json"),
)


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ref(relative: str) -> dict:
    path = (REPO / relative).resolve()
    if not path.is_relative_to(REPO.resolve()) or not path.is_file():
        raise ValueError(f"missing or nonlocal artifact: {relative}")
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def build_table() -> dict:
    table = copy.deepcopy(read(ROOT / "manuscript-evidence-table.v1.json"))
    table["schema"] = "rime.paper17.manuscript-evidence-table.v2"
    table["candidate_identity"]["publication_status"] = "UNPUBLISHED_CANDIDATE_2"
    old_boundary = "no universal registered separator at the defining 1->2 transition"
    if old_boundary not in table["canonical_wording"]["paper_level_statement"]:
        raise ValueError("candidate-1 initial-transition wording changed")
    table["canonical_wording"]["paper_level_statement"] = table["canonical_wording"]["paper_level_statement"].replace(
        old_boundary,
        "no single registered primary predicate separates the cohorts at the defining 1->2 transition",
    )
    table["canonical_wording"]["paper_level_statement"] += (
        " A later exact cache audit covers all 102 persistent sources at saved times 1,2,3. "
        "All raw drives are nonzero and coordinatewise nonpositive; all clipped drives are zero. "
        "Common linear leakage suffices to preserve equality on all ten non-singleton "
        "common-support fibers, accounting for all 194 redundant windows."
    )
    table["claims"].insert(-1, {
        "id": "P17-C10",
        "statement": (
            "All 306 saved raw drives of the 102 persistent sources at times 1,2,3 are "
            "nonzero and coordinatewise nonpositive, and all clipped drives are zero. "
            "The 204 common-support points cover every member of all ten non-singleton "
            "fibers and all 194 redundant windows; their one-step equality has a "
            "sufficient common-linear-leak explanation."
        ),
        "reader_facing_status": "Computational Certificate",
        "role": "COMPLETE_PERSISTENT_EFFECTIVE_DRIVE_BOUNDARY",
        "evidence": [dict(ref(path), resolution_mode="current_paper_owned") for path in (DRIVE, AUDIT)],
        "boundary": (
            "Exact cache replay does not regenerate Y^T x or microscopic orbits. Time-1 "
            "cohort records do not extend the common-support factorization; total-drive "
            "signs do not imply individual block signs or block-subset robustness. No "
            "active compensation, independent replication, or coarse endomap is claimed."
        ),
    })
    table["validator"] = "validation/validate_release_v2.py"
    table["receipt"] = "results/release.v2.validation-receipt.json"
    table["claim_authority"] = "papers/paper17/Paper XVII.md"
    return table


def build_manifest() -> dict:
    previous = read(PREVIOUS)
    previous_entries = {entry["path"]: entry for entry in previous["artifacts"]}
    replacements = {}
    for relative in REPLACED:
        snapshot_path = f"{SNAPSHOT}/{relative}"
        actual = ref(snapshot_path)
        expected = previous_entries[relative]
        if (actual["bytes"], actual["sha256"]) != (expected["bytes"], expected["sha256"]):
            raise ValueError(f"prior candidate snapshot differs: {relative}")
        replacements[relative] = snapshot_path

    # Only explicitly snapshotted candidate-1 surfaces may change.
    for relative, entry in previous_entries.items():
        actual = ref(replacements.get(relative, relative))
        if (actual["bytes"], actual["sha256"]) != (entry["bytes"], entry["sha256"]):
            raise ValueError(f"unapproved prior-candidate drift: {relative}")

    manifest = copy.deepcopy(previous)
    manifest["schema"] = "rime.paper17.release-manifest.v2"
    manifest["release_version"] = "1.0-candidate-2"
    artifacts = []
    for entry in previous["artifacts"]:
        current = dict(entry, **ref(entry["path"]))
        if entry["role"] in {"evidence-table", "release-validator", "release-manifest-builder"}:
            current["role"] = f"candidate-1-{entry['role']}"
            current["closure_class"] = "historical-candidate-input"
        if entry["role"] in {"mechanism-state-codec", "mechanism-transition-codecs"}:
            current["closure_class"] = "release-validation"
        artifacts.append(current)
    for role, closure_class, relative in NEW_ARTIFACTS:
        artifacts.append(dict(ref(relative), role=role, closure_class=closure_class))
    for relative, snapshot_path in replacements.items():
        artifacts.append(dict(ref(snapshot_path), role="prior-candidate-replaced-artifact", closure_class="historical-candidate-input"))
    if len({entry["path"] for entry in artifacts}) != len(artifacts):
        raise ValueError("duplicate candidate-2 artifact path")
    identity = [entry for entry in artifacts if entry["closure_class"] in IDENTITY_CLASSES]
    manifest["artifacts"] = artifacts
    manifest["artifact_count"] = len(artifacts)
    manifest["artifact_count_by_closure_class"] = dict(sorted(Counter(entry["closure_class"] for entry in artifacts).items()))
    manifest["release_identity"]["ordered_artifact_count"] = len(identity)
    manifest["release_identity"]["ordered_closure_sha256"] = closure_digest(identity)
    manifest["prior_candidate"] = {
        "manifest": ref("experiments/paper17/release-manifest.v1.json"),
        "receipt": ref("experiments/paper17/results/release.v1.validation-receipt.json"),
        "replaced_artifacts": replacements,
        "old_scientific_outcomes_rewritten": False,
    }
    manifest["verified_claims"]["complete_persistent_effective_drive_boundary_bound"] = True
    manifest["supplementary_promotion"] = {
        "claim": "P17-C10",
        "audit": ref(DRIVE),
        "default_validation": "COMPACT_BINDINGS_AND_AGGREGATE_CONSISTENCY",
        "default_source_payload_replay": False,
        "optional_full_cache_replay": "python experiments/paper17/mechanism/validation/audit_persistent_safe_effective_drive_v1.py --check",
        "operator_action_recomputed": False,
        "common_support_times": [2, 3],
        "additional_saved_time_is_not_domain_extension": 1,
        "excluded_research_results": ["MTS-1.1", "MTS-1.2", "negative-drive invariant-region note"],
    }
    manifest["receipt_path"] = RECEIPT
    return manifest


def write(path: Path, record: dict) -> None:
    path.write_text(json.dumps(record, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-candidate-2", action="store_true")
    args = parser.parse_args()
    if (TABLE.exists() or MANIFEST.exists()) and not args.refresh_candidate_2:
        parser.error("candidate-2 already exists; explicit --refresh-candidate-2 is required")
    write(TABLE, build_table())
    write(MANIFEST, build_manifest())
    print(json.dumps({"status": "CANDIDATE_2_BOUND", "release_identity_claimed": False, "scientific_producer_executed": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
