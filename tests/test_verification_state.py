"""Hostile controls for the repository-non-intervention guard."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from verification_state import (
    changed_tracked_paths,
    create_verification_checkout,
    snapshot_tracked_state,
    verification_exit_code,
)

from tools.release.post_release_anchor import (
    checked_relative_path,
    supplement_rows,
    tag_identity,
    validate_release_identity,
    validate_remote_publication_date,
    validated_publication_date,
    zenodo_record_id,
)
from tools.release.verify_zenodo_anchor import record_id


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def test_tracked_mutation_is_detected() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        _git(root, "init")
        _git(root, "config", "user.name", "Verification Test")
        _git(root, "config", "user.email", "verification@example.invalid")
        tracked = root / "historical-artifact.json"
        tracked.write_text('{"state":"frozen"}\n', encoding="utf-8")
        _git(root, "add", tracked.name)
        _git(root, "commit", "-m", "fixture")

        before = snapshot_tracked_state(root)
        assert before == snapshot_tracked_state(root)
        with tempfile.TemporaryDirectory() as scratch_directory:
            scratch = Path(scratch_directory) / "repository"
            create_verification_checkout(root, scratch)
            assert (scratch / ".git").is_dir()
            assert subprocess.run(
                ["git", "show", f"HEAD:{tracked.name}"],
                cwd=scratch,
                check=True,
                capture_output=True,
                text=True,
            ).stdout == '{"state":"frozen"}\n'
            (scratch / tracked.name).write_text(
                '{"state":"scratch-only"}\n', encoding="utf-8"
            )
            assert before == snapshot_tracked_state(root)
        tracked.write_text('{"state":"rewritten"}\n', encoding="utf-8")
        after = snapshot_tracked_state(root)

        assert before != after
        assert changed_tracked_paths(before, after) == [tracked.name]
        assert verification_exit_code(0, before, after) == 1


def test_zenodo_record_id_forms() -> None:
    assert record_id("21988041") == "21988041"
    assert record_id("10.5281/zenodo.21988041") == "21988041"
    assert record_id("https://doi.org/10.5281/zenodo.21988041") == "21988041"


def test_post_release_anchor_inputs_are_fail_closed() -> None:
    assert zenodo_record_id("10.5281/zenodo.22980858") == "22980858"
    assert checked_relative_path("experiments/paper28/release-manifest.json") == (
        "experiments/paper28/release-manifest.json"
    )
    for unsafe in ("../release-manifest.json", "/tmp/release.json", "C:\\release.json"):
        try:
            checked_relative_path(unsafe)
        except ValueError:
            pass
        else:
            raise AssertionError(f"unsafe path accepted: {unsafe}")


def test_post_release_anchor_requires_exact_tag_and_downstream_supplement() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        _git(root, "init")
        _git(root, "config", "user.name", "Verification Test")
        _git(root, "config", "user.email", "verification@example.invalid")
        release_file = root / "release.json"
        release_file.write_text('{"status":"released"}\n', encoding="utf-8")
        _git(root, "add", release_file.name)
        _git(root, "commit", "-m", "release fixture")

        commit_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        for revision in ("HEAD", "main", commit_sha):
            try:
                tag_identity(root, revision)
            except ValueError:
                pass
            else:
                raise AssertionError(f"non-tag revision accepted: {revision}")

        _git(root, "tag", "paper-test-v1.0")
        identity = tag_identity(root, "paper-test-v1.0")
        assert identity["name"] == "paper-test-v1.0"
        assert identity["target_commit_sha"] == commit_sha

        supplement = root / "supplement.json"
        supplement.write_text('{"role":"post-release"}\n', encoding="utf-8")
        rows = supplement_rows(
            root, "paper-test-v1.0", [("supplement", supplement.name)]
        )
        assert rows[0]["release_role"] == "POST_RELEASE_SUPPLEMENT_NOT_IN_RELEASE_TAG"

        try:
            supplement_rows(
                root, "paper-test-v1.0", [("not-downstream", release_file.name)]
            )
        except ValueError:
            pass
        else:
            raise AssertionError("tagged release content accepted as a post-release supplement")


def test_post_release_anchor_publication_date_is_fail_closed() -> None:
    assert validated_publication_date("2026-09-29") == "2026-09-29"
    for invalid in (None, 20260929, "2026-9-29", "2026-02-30"):
        try:
            validated_publication_date(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid publication date accepted: {invalid!r}")

    validate_remote_publication_date(
        {"metadata": {"publication_date": "2026-09-29"}}, "2026-09-29"
    )
    try:
        validate_remote_publication_date(
            {"metadata": {"publication_date": "2026-09-28"}}, "2026-09-29"
        )
    except ValueError:
        pass
    else:
        raise AssertionError("remote publication-date mismatch was accepted")


def test_post_release_anchor_identity_matches_release_tag() -> None:
    validate_release_identity("PAPER28", "1.0", "paper28-v1.0")
    for paper_id, version, tag in (
        ("PAPER27", "1.0", "paper28-v1.0"),
        ("PAPER28", "2.0", "paper28-v1.0"),
        ("PAPER28", "1.0", "HEAD"),
    ):
        try:
            validate_release_identity(paper_id, version, tag)
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"release identity mismatch accepted: {paper_id}, {version}, {tag}"
            )


def test_post_release_anchor_schema_enforces_nested_contracts() -> None:
    schema_path = PROJECT_ROOT / "tools/release/post-release-anchor.v1.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    anchors = sorted((PROJECT_ROOT / "docs/release-anchors").glob("paper*-v1.0.json"))
    assert anchors
    for path in anchors:
        anchor = json.loads(path.read_text(encoding="utf-8"))
        assert list(validator.iter_errors(anchor)) == [], path

    canonical = json.loads(anchors[0].read_text(encoding="utf-8"))
    hostile_mutations = []
    for field, value in (
        ("pre_release_evidence", []),
        ("external_anchor", {}),
        ("versioned_repin_policy", {}),
    ):
        hostile = copy.deepcopy(canonical)
        hostile[field] = value
        hostile_mutations.append(hostile)

    hostile = copy.deepcopy(canonical)
    hostile["post_release_supplements"] = [{}]
    hostile_mutations.append(hostile)
    hostile = copy.deepcopy(canonical)
    hostile["external_anchor"]["deposited_files"] = []
    hostile_mutations.append(hostile)

    for hostile in hostile_mutations:
        assert list(validator.iter_errors(hostile)), hostile


if __name__ == "__main__":
    test_tracked_mutation_is_detected()
    test_zenodo_record_id_forms()
    test_post_release_anchor_inputs_are_fail_closed()
    test_post_release_anchor_requires_exact_tag_and_downstream_supplement()
    test_post_release_anchor_publication_date_is_fail_closed()
    test_post_release_anchor_identity_matches_release_tag()
    test_post_release_anchor_schema_enforces_nested_contracts()
    print("test_verification_state.py: OK")
