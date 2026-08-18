"""Fast contract tests for cached experiment observations."""

from pathlib import Path
import json
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.observation import (
    check_experiment_observation,
    write_experiment_observation,
)


def test_current_then_stale() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "experiment.py"
        artifact = root / "results" / "experiment.observation.json"
        source.write_text("VALUE = 1\n", encoding="utf-8")

        write_experiment_observation(
            artifact,
            root=root,
            experiment_id="contract-test",
            paper="test",
            command=["python", "experiment.py"],
            sources=[source],
            parameters={"tolerance": 1e-10},
            observations={"value": 1},
            claim_status="computational_observation",
            claim_scope="helper contract only",
            limitations=["not a mathematical claim"],
            started_at_utc="2026-01-01T00:00:00Z",
            elapsed_seconds=0.1,
        )
        artifact_bytes = artifact.read_bytes()
        assert b"\r\n" not in artifact_bytes
        assert artifact_bytes.endswith(b"\n")
        current = check_experiment_observation(artifact, root=root)
        assert current.reusable, current

        source.write_text("VALUE = 2\n", encoding="utf-8")
        stale = check_experiment_observation(artifact, root=root)
        assert stale.valid and not stale.current
        assert stale.stale_sources == ("experiment.py",)


def test_manifest_tampering_is_invalid() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "experiment.py"
        artifact = root / "experiment.observation.json"
        source.write_text("VALUE = 1\n", encoding="utf-8")
        write_experiment_observation(
            artifact,
            root=root,
            experiment_id="tamper-test",
            paper="test",
            command=["python", "experiment.py"],
            sources=[source],
            parameters={},
            observations={"value": 1},
            claim_status="computational_observation",
            claim_scope="helper contract only",
            limitations=[],
            started_at_utc="2026-01-01T00:00:00Z",
            elapsed_seconds=0.1,
        )
        record = json.loads(artifact.read_text(encoding="utf-8"))
        record["provenance"]["sources"][0]["sha256"] = "0" * 64
        artifact.write_text(json.dumps(record), encoding="utf-8")

        check = check_experiment_observation(artifact, root=root)
        assert not check.valid
        assert "source_set_sha256 does not match" in check.errors[0]


def test_missing_source_is_stale_not_malformed() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "experiment.py"
        artifact = root / "experiment.observation.json"
        source.write_text("VALUE = 1\n", encoding="utf-8")
        write_experiment_observation(
            artifact,
            root=root,
            experiment_id="missing-source-test",
            paper="test",
            command=["python", "experiment.py"],
            sources=[source],
            parameters={},
            observations={"value": 1},
            claim_status="computational_observation",
            claim_scope="helper contract only",
            limitations=[],
            started_at_utc="2026-01-01T00:00:00Z",
            elapsed_seconds=0.1,
        )
        source.unlink()

        check = check_experiment_observation(artifact, root=root)
        assert check.valid and not check.current
        assert check.stale_sources == ("experiment.py",)


if __name__ == "__main__":
    test_current_then_stale()
    test_manifest_tampering_is_invalid()
    test_missing_source_is_stale_not_malformed()
    print("test_experiment_observation: OK")
