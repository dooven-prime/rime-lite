"""Verify the deposited byte inventory and optionally replay the exact census."""

from __future__ import annotations

import argparse
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
EVIDENCE = "papers/unnumbered/from_support_to_state/evidence"
FIGURES = "papers/unnumbered/from_support_to_state/figures"
D22 = "experiments/paper16/source/digital_fly_v0_2/results/d2_2_memory_closure_v0_2.json"
UPSTREAM = "experiments/paper16/upstream-provenance.v1.json"
EXPECTED_FILES = {
    "README.md", "ATTRIBUTION.md", "requirements.txt", "LICENSE_CODE.txt",
    "verify_dataset.py", D22, UPSTREAM,
    "data/carrier/carrier_v0_edges.npz", "data/carrier/carrier_v0_nodes.parquet",
    f"{EVIDENCE}/profile_heterogeneity_census.v1.json",
    f"{EVIDENCE}/profile_heterogeneity_census.py",
    f"{EVIDENCE}/somaside_exact_witness.py",
    f"{EVIDENCE}/test_profile_heterogeneity.py",
    f"{EVIDENCE}/plot_profile_heterogeneity.py",
    f"{FIGURES}/profile_multiplicity.png",
    f"{FIGURES}/profile_multiplicity.svg",
    f"{FIGURES}/coordinate_profile_splits.png",
    f"{FIGURES}/coordinate_profile_splits.svg",
}
PINNED = {
    "data/carrier/carrier_v0_edges.npz":
        "c94e885cc2e8cde78012ed0a68a4beb42eccfe1b64607bdc90ac46e675d6966d",
    "data/carrier/carrier_v0_nodes.parquet":
        "87aa46280d68a210f6c8ef4a044282fbbb62342bbeeaab8393b0fd7fa770515e",
    D22: "ce416b76e90ba55ab9f5fcc3e537bb8e7f04b0a3735683a38e5267d6b38179f2",
    UPSTREAM: "0b90db879b51ee6fe6e37fe443c58be9e572e3b202221958d33c487199345a55",
    f"{EVIDENCE}/profile_heterogeneity_census.v1.json":
        "f199ca218039cc5c49ce2e8dbea66d171f3623d84dcf2889682dfc554f7aef32",
    f"{EVIDENCE}/profile_heterogeneity_census.py":
        "c01c39bb1d8ee7dca4896704072a873dd74fd2f96b787ff694aa91ee8536332a",
    f"{EVIDENCE}/somaside_exact_witness.py":
        "8d4d54364bf208f91987218a8aa4d12ce019f9640055c952caa88e751b284ef7",
}
PACKAGES = {"numpy": "2.1.3", "pandas": "3.0.3", "pyarrow": "18.0.0"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    require(isinstance(result, dict), f"expected JSON object: {path}")
    return result


def checked_path(relative: str) -> Path:
    posix = PurePosixPath(relative)
    require(not posix.is_absolute() and ".." not in posix.parts and
            posix.as_posix() == relative, f"invalid package path: {relative}")
    path = ROOT.joinpath(*posix.parts)
    require(path.is_file() and not path.is_symlink(), f"missing or linked file: {relative}")
    require(path.resolve().is_relative_to(ROOT), f"path escapes package: {relative}")
    return path


def verify_files() -> dict[str, str]:
    manifest = read_json(ROOT / "manifest.json")
    require(set(manifest) == {"schema", "version", "package_kind", "files", "boundary"},
            "manifest fields differ")
    require(manifest["schema"] == "rime.malecns-predictive-census-dataset.v1" and
            manifest["version"] == "1.0" and
            manifest["package_kind"] == "DATASET_WITH_SOURCE_REPLAY", "manifest identity")
    rows = manifest["files"]
    require(isinstance(rows, list) and len(rows) == len(EXPECTED_FILES), "file count")
    require(all(isinstance(row, dict) and set(row) == {"path", "role", "size", "sha256"}
                for row in rows), "manifest file fields")
    names = [row["path"] for row in rows]
    require(names == sorted(EXPECTED_FILES), "file list must be the exact sorted include set")
    actual = set()
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        require(not path.is_symlink(), f"linked package entry: {relative}")
        if "__pycache__" in relative.parts:
            require(path.is_dir() or path.suffix == ".pyc",
                    f"unexpected cache entry: {relative}")
        elif path.is_file():
            actual.add(relative.as_posix())
    require(actual == EXPECTED_FILES | {"manifest.json"},
            f"package inventory differs: missing={sorted((EXPECTED_FILES | {'manifest.json'}) - actual)}, "
            f"extra={sorted(actual - (EXPECTED_FILES | {'manifest.json'}))}")
    found = {}
    for row in rows:
        name = row["path"]
        path = checked_path(name)
        require(type(row["size"]) is int and row["size"] >= 0 and
                path.stat().st_size == row["size"], f"size mismatch: {name}")
        require(isinstance(row["role"], str) and row["role"] and
                isinstance(row["sha256"], str) and
                re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is not None,
                f"invalid role/digest: {name}")
        actual = digest(path)
        require(actual == row["sha256"], f"SHA-256 mismatch: {name}")
        found[name] = actual
    for name, expected in PINNED.items():
        require(found[name] == expected, f"pinned dependency drift: {name}")
    return found


def verify_result(found: dict[str, str]) -> dict:
    upstream = read_json(checked_path(UPSTREAM))
    require(upstream.get("dataset", {}).get("name") == "MaleCNS" and
            upstream["dataset"].get("release") == "v1.0" and
            upstream["dataset"].get("license", {}).get("spdx") == "CC-BY-4.0",
            "upstream source identity/license")
    record = read_json(checked_path(f"{EVIDENCE}/profile_heterogeneity_census.v1.json"))
    require(record.get("format") == "from-support-to-state.profile-heterogeneity.v1"
            and record.get("domain") == "all_eligible_unit_sources_of_Y_known_pm",
            "result identity")
    require(record.get("source_nodes") == 211577 and
            record.get("known_sign_edges") == 25214058, "carrier dimensions")
    require(record.get("carrier_sha256") == {
        "carrier_v0_edges.npz": found["data/carrier/carrier_v0_edges.npz"],
        "carrier_v0_nodes.parquet": found["data/carrier/carrier_v0_nodes.parquet"],
    }, "result/carrier binding")
    require(record.get("source_metadata") == {
        "path": D22, "checkout_sha256": found[D22],
    }, "result/Paper XVI D2.2 binding")
    require(record.get("implementation_sha256") == {
        "profile_heterogeneity_census.py": found[f"{EVIDENCE}/profile_heterogeneity_census.py"],
        "somaside_exact_witness.py": found[f"{EVIDENCE}/somaside_exact_witness.py"],
    }, "result/producer binding")
    partitions = record["partitions"]
    soma, superclass = partitions["somaSide"], partitions["superclass"]
    require(soma["eligible_sources"] == 163439 and
            soma["profile_classes_with_source_sector_retained"] == 90148 and
            superclass["profile_classes_with_source_sector_retained"] == 119138,
            "profile totals")
    expected_rows = [
        ("<missing>", 17850, 14535), ("L", 72479, 38648),
        ("M", 360, 69), ("R", 72750, 36896),
    ]
    require([(row["source_sector"], row["eligible_sources"], row["exact_profile_classes"])
             for row in soma["by_source_sector"]] == expected_rows, "somaSide rows")
    separation = soma["coordinate_separation"]
    require(separation["status"] == "EXACT_BY_EXHAUSTIVE_SUBSETS" and
            separation["minimum_coordinate_count"] == 3 and
            separation["minimum_coordinate_sets"] == [["<missing>", "L", "R"]],
            "coordinate separation")
    require(all(row["equal"] is True for row in record["prior_total_consistency"].values()),
            "Paper XVI consistency")
    return record


def replay() -> None:
    require(sys.version_info[:2] == (3, 13), "replay requires Python 3.13")
    for name, expected in PACKAGES.items():
        require(version(name) == expected, f"{name} must be {expected}")
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cmd = [sys.executable, "-B", str(checked_path(f"{EVIDENCE}/profile_heterogeneity_census.py")),
           "--carrier-dir", str(ROOT / "data/carrier"),
           "--result", str(ROOT / EVIDENCE / "profile_heterogeneity_census.v1.json")]
    result = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True)
    require(result.returncode == 0, f"producer replay failed:\n{result.stderr[-4000:]}")
    report = json.loads(result.stdout.strip().splitlines()[-1])
    require(report.get("status") == "PASS" and
            report.get("mode") == "FULL_CENSUS_SOURCE_REPLAY" and
            report.get("eligible_sources") == 163439 and
            report.get("profile_classes") == {"somaSide": 90148, "superclass": 119138},
            "producer replay report")
    tests = subprocess.run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(ROOT / EVIDENCE),
         "-p", "test_profile_heterogeneity.py"], cwd=ROOT, env=env,
        text=True, capture_output=True)
    require(tests.returncode == 0 and "Ran 7 tests" in tests.stderr,
            f"focused controls failed:\n{tests.stderr[-4000:]}")
    verify_result(verify_files())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", action="store_true", help="also recompute the full census")
    args = parser.parse_args()
    try:
        verify_result(verify_files())
        if args.replay:
            replay()
    except (ValueError, OSError, KeyError, IndexError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}))
        return 1
    print(json.dumps({"status": "SOURCE_REPLAY_PASS" if args.replay else
                       "LOCAL_BYTE_CLOSURE_PASS", "eligible_sources": 163439,
                      "somaSide_profile_classes": 90148,
                      "superclass_profile_classes": 119138}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
