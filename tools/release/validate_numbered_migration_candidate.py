#!/usr/bin/env python3
"""Validate a numbered edition without rewriting its historical proof owner."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
ROMAN = {42: "XLII", 43: "XLIII", 44: "XLIV"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def path_at_root(value: str) -> Path:
    relative = PurePosixPath(value)
    require(not relative.is_absolute() and ".." not in relative.parts,
            f"unsafe path: {value}")
    target = (ROOT / value).resolve()
    require(target.is_relative_to(ROOT.resolve()), f"path escapes repository: {value}")
    return target


def payload(value: str) -> bytes:
    target = path_at_root(value)
    require(target.is_file(), f"missing file: {value}")
    return target.read_bytes()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def artifact_payload(role: str, path: str) -> bytes:
    value = payload(path)
    if role == "candidate-ci-workflow":
        # Git records this workflow as LF text; Windows may materialize CRLF.
        require(b"\r" not in value.replace(b"\r\n", b""),
                "unexpected workflow line ending")
        return value.replace(b"\r\n", b"\n")
    return value


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          check=True).stdout


def check_tag(tag: dict[str, str]) -> str:
    name = tag["name"]
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name) is not None,
            "invalid historical tag name")
    ref = f"refs/tags/{name}"
    object_sha = git("rev-parse", "--verify", ref).decode("ascii").strip()
    commit_sha = git("rev-parse", "--verify", f"{ref}^{{commit}}").decode("ascii").strip()
    require(object_sha == tag["tag_object_sha"], f"tag object drift: {name}")
    require(commit_sha == tag["target_commit_sha"], f"tag target drift: {name}")
    return commit_sha


def check_rows(rows: list[dict[str, str]], commit: str) -> int:
    require(bool(rows), "empty historical file list")
    paths = [row["path"] for row in rows]
    require(len(paths) == len(set(paths)), "duplicate historical path")
    for row in rows:
        path, expected = row["path"], row["sha256"]
        require(re.fullmatch(r"[0-9a-f]{64}", expected) is not None,
                f"invalid historical digest: {path}")
        require(digest(payload(path)) == expected, f"local historical drift: {path}")
        require(digest(git("show", f"{commit}:{path}")) == expected,
                f"tagged historical drift: {path}")
    return len(rows)


def check_evidence(paper: int, evidence: dict[str, object]) -> int:
    require(evidence["schema"] == "rime.numbered-migration-evidence.v1",
            "evidence schema")
    require(evidence["paper_id"] == f"PAPER{paper}" and
            evidence["release_version"] == "1.0", "evidence edition identity")
    historical = evidence["historical_submission"]
    require(historical["service"] == "HAL" and
            historical["status"] == "SUBMITTED_MODERATION_NOT_ASSERTED_ACCEPTED",
            "historical submission status")
    require(re.fullmatch(r"hal-\d+v1", historical["identifier"]) is not None,
            "historical HAL identifier")
    source_commit = check_tag(historical["source_tag"])
    count = check_rows(historical["source_files"], source_commit)
    companions = evidence["inherited_companions"]
    require(bool(companions), "no inherited companion")
    kinds = [row["kind"] for row in companions]
    require(len(kinds) == len(set(kinds)), "duplicate companion kind")
    for companion in companions:
        owner = companion["proof_owner"]
        require(owner.startswith("experiments/") and owner.endswith("/"),
                "invalid proof owner")
        source_tag = companion["source_tag"]
        commit = (check_tag(source_tag) if isinstance(source_tag, dict)
                  else source_commit)
        if isinstance(source_tag, str):
            require(source_tag == historical["source_tag"]["name"],
                    "companion source tag mismatch")
        if "source_files" in companion:
            count += check_rows(companion["source_files"], commit)
        if "downstream_anchor" in companion:
            anchor = companion["downstream_anchor"]
            require(digest(payload(anchor["path"])) == anchor["sha256"],
                    "downstream companion anchor drift")
            anchor_data = json.loads(payload(anchor["path"]))
            require(anchor_data["source_tag"]["name"] == source_tag["name"],
                    "companion anchor tag mismatch")
            require(anchor_data["external_record"]["doi"] == companion["archive_doi"],
                    "companion archive DOI mismatch")
    edition = evidence["numbered_edition"]
    expected = {
        "manuscript": f"papers/paper{paper}/Paper {ROMAN[paper]}.md",
        "bibliography": f"papers/paper{paper}/references-v1.bib",
        "reader_pdf": f"papers/paper{paper}/paper{paper}_arxiv.pdf",
        "publication_status": "RELEASE_CANDIDATE",
        "release_identity_claimed": False,
        "external_anchor_claimed": False,
    }
    require(edition == expected, "numbered edition identity/status drift")
    return count


def artifact_paths(paper: int) -> dict[str, str]:
    prefix = f"papers/paper{paper}/"
    package = f"experiments/paper{paper}/"
    return {
        "manuscript": prefix + f"Paper {ROMAN[paper]}.md",
        "bibliography": prefix + "references-v1.bib",
        "reader-pdf": prefix + f"paper{paper}_arxiv.pdf",
        "paper-index": prefix + "README.md",
        "evidence-map": package + "evidence-map.v1.json",
        "experiment-index": package + "README.md",
        "release-environment": package + "release-environment.json",
        "candidate-validator": "tools/release/validate_numbered_migration_candidate.py",
        "candidate-validator-tests": package + "validation/test_release.py",
        "candidate-ci-workflow": f".github/workflows/paper{paper}-candidate.yml",
        "checkout-line-ending-policy": ".gitattributes",
        "reader-build-entrypoint": "papers/tex/build.py",
        "reader-build-driver": "papers/tex/_build.py",
        "reader-build-postprocessor": "papers/tex/_postprocess.py",
        "reader-build-hrule-cleaner": "papers/tex/_clean_hrule.py",
    }


def check_citations(paper: int) -> None:
    artifacts = artifact_paths(paper)
    manuscript = payload(artifacts["manuscript"]).decode("utf-8")
    bibliography = payload(artifacts["bibliography"]).decode("utf-8")
    keys = set(re.findall(r"@\w+\s*\{\s*([^,]+),", bibliography))
    cited = set(re.findall(r"(?<!\w)@([A-Za-z][A-Za-z0-9_:-]*)", manuscript))
    require(cited <= keys, f"unresolved citation keys: {sorted(cited - keys)}")
    require(f"Paper {ROMAN[paper]} | Version 1.0" in manuscript,
            "visible edition identity missing")
    require("hal-" not in manuscript.lower(), "HAL submission in numbered prose")
    require(payload(artifacts["reader-pdf"]).startswith(b"%PDF-"),
            "reader PDF signature missing")


def candidate_manifest(paper: int) -> dict[str, object]:
    return {
        "schema": "rime.numbered-migration-candidate.v1",
        "paper_id": f"PAPER{paper}",
        "release_version": "1.0",
        "intended_release_tag": f"paper{paper}-v1.0",
        "status": "RELEASE_CANDIDATE",
        "release_identity_claimed": False,
        "external_anchor_claimed": False,
        "receipt_self_exclusion": True,
        "artifacts": [
            {"role": role, "path": path,
             "sha256": digest(artifact_payload(role, path)),
             "size": len(artifact_payload(role, path))}
            for role, path in artifact_paths(paper).items()
        ],
    }


def check_manifest(paper: int) -> tuple[int, str]:
    manifest_path = f"experiments/paper{paper}/release-manifest.json"
    raw = payload(manifest_path)
    manifest = json.loads(raw)
    expected = candidate_manifest(paper)
    require(manifest == expected, "candidate manifest or artifact bytes drift")
    return len(expected["artifacts"]), digest(raw)


def replay(evidence: dict[str, object]) -> list[str]:
    commands = evidence["replay_commands"]
    require(len(commands) >= 2, "incomplete replay command list")
    statuses = []
    for row in commands:
        args = row["argv"]
        require(args[0] == "python" and all(isinstance(arg, str) for arg in args),
                "unsafe replay command")
        cwd = path_at_root(row["cwd"])
        require(cwd.is_dir(), f"missing replay directory: {cwd}")
        result = subprocess.run([sys.executable, *args[1:]], cwd=cwd,
                                capture_output=True, text=True, check=True)
        expected = row["expected_status"]
        require(expected in result.stdout, f"replay status missing: {expected}")
        print(result.stdout, end="")
        statuses.append(expected)
    return statuses


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper", type=int, choices=sorted(ROMAN))
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    try:
        evidence_path = f"experiments/paper{args.paper}/evidence-map.v1.json"
        evidence = json.loads(payload(evidence_path))
        historic_count = check_evidence(args.paper, evidence)
        check_citations(args.paper)
        manifest_path = path_at_root(f"experiments/paper{args.paper}/release-manifest.json")
        if args.freeze:
            require(not args.write_receipt, "freeze and receipt are separate gates")
            manifest_path.write_text(
                json.dumps(candidate_manifest(args.paper), indent=2,
                           ensure_ascii=True) + "\n", encoding="utf-8", newline="\n"
            )
        artifact_count, manifest_sha = check_manifest(args.paper)
        statuses = replay(evidence) if args.replay or args.write_receipt else []
        if args.write_receipt:
            receipt = {
                "schema": "rime.numbered-migration-receipt.v1",
                "status": "PASS_LOCAL_CANDIDATE_CLOSURE",
                "paper_id": f"PAPER{args.paper}",
                "release_identity_claimed": False,
                "external_anchor_claimed": False,
                "manifest_sha256": manifest_sha,
                "artifact_count": artifact_count,
                "historical_byte_bindings": historic_count,
                "replay_statuses": statuses,
                "checked_at_utc": datetime.now(timezone.utc).isoformat(),
                "limits": "Local same-source checks; no publication, DOI, or independent cross-host replay claimed",
            }
            target = path_at_root(
                f"experiments/paper{args.paper}/results/paper{args.paper}_candidate.validation-receipt.json"
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(receipt, indent=2, ensure_ascii=True) + "\n",
                              encoding="utf-8", newline="\n")
        print(f"PASS Paper {ROMAN[args.paper]} candidate: {artifact_count} artifacts; "
              f"{historic_count} historical bytes; manifest {manifest_sha}")
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"FAIL numbered migration candidate: {exc}") from exc


if __name__ == "__main__":
    main()
