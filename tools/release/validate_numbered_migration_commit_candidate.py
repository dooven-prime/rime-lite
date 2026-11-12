#!/usr/bin/env python3
"""Commit-sourced variant of the frozen numbered migration candidate gate."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.release import validate_numbered_migration_candidate as base  # noqa: E402


_base_artifact_paths = base.artifact_paths


def artifact_paths(paper: int) -> dict[str, str]:
    paths = _base_artifact_paths(paper)
    paths["candidate-validator"] = (
        "tools/release/validate_numbered_migration_commit_candidate.py"
    )
    paths["candidate-validator-base"] = (
        "tools/release/validate_numbered_migration_candidate.py"
    )
    return paths


def check_evidence(paper: int, evidence: dict[str, object]) -> int:
    base.require(evidence["schema"] == "rime.numbered-migration-evidence.v2",
                 "evidence schema")
    base.require(evidence["paper_id"] == f"PAPER{paper}" and
                 evidence["release_version"] == "1.0", "evidence edition identity")
    historical = evidence["historical_submission"]
    base.require(historical["service"] == "HAL" and
                 historical["status"] == "SUBMITTED_MODERATION_NOT_ASSERTED_ACCEPTED",
                 "historical submission status")
    base.require(re.fullmatch(r"hal-\d+v1", historical["identifier"]) is not None,
                 "historical HAL identifier")
    source_commit = historical["source_commit"]
    base.require(re.fullmatch(r"[0-9a-f]{40}", source_commit) is not None,
                 "invalid historical commit")
    base.git("cat-file", "-e", f"{source_commit}^{{commit}}")
    count = base.check_rows(historical["source_files"], source_commit)
    companions = evidence["inherited_companions"]
    base.require(bool(companions), "no inherited companion")
    kinds = [row["kind"] for row in companions]
    base.require(len(kinds) == len(set(kinds)), "duplicate companion kind")
    for companion in companions:
        owner = companion["proof_owner"]
        base.require(owner.startswith("experiments/") and owner.endswith("/"),
                     "invalid proof owner")
        if "source_tag" in companion:
            commit = base.check_tag(companion["source_tag"])
        else:
            commit = companion["source_commit"]
            base.require(commit == source_commit, "companion source commit mismatch")
        if "source_files" in companion:
            count += base.check_rows(companion["source_files"], commit)
        if "downstream_anchor" in companion:
            anchor = companion["downstream_anchor"]
            raw = base.payload(anchor["path"])
            base.require(base.digest(raw) == anchor["sha256"],
                         "downstream companion anchor drift")
            record = json.loads(raw)
            base.require(record["source_tag"]["name"] ==
                         companion["source_tag"]["name"],
                         "companion anchor tag mismatch")
            archive = record.get("external_record", record.get("archive"))
            base.require(archive["doi"] == companion["archive_doi"],
                         "companion archive DOI mismatch")
    edition = evidence["numbered_edition"]
    expected = {
        "manuscript": f"papers/paper{paper}/Paper {base.ROMAN[paper]}.md",
        "bibliography": f"papers/paper{paper}/references-v1.bib",
        "reader_pdf": f"papers/paper{paper}/paper{paper}_arxiv.pdf",
        "publication_status": "RELEASE_CANDIDATE",
        "release_identity_claimed": False,
        "external_anchor_claimed": False,
    }
    base.require(edition == expected, "numbered edition identity/status drift")
    return count


base.artifact_paths = artifact_paths
base.check_evidence = check_evidence


if __name__ == "__main__":
    base.main()
