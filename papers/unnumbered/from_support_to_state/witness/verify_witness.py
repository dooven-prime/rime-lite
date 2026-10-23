"""Check the compact witness package and optionally replay source extraction."""

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
METADATA = (
    "experiments/paper16/source/digital_fly_v0_2/results/d2_3_partition_comparison_v0_2.json",
    "experiments/paper16/source/digital_fly_v0/results/carrier_v0_manifest.json",
    "experiments/paper16/source/digital_fly_v0_1/results/sd1_operator_admission_v0_1.json",
)
EXPECTED = {
    "README.md", "ATTRIBUTION.md", "LICENSE_CODE.txt", "requirements.txt",
    "verify_witness.py", "experiments/paper16/upstream-provenance.v1.json",
    *METADATA,
    f"{EVIDENCE}/somaside_exact_witness.py",
    f"{EVIDENCE}/somaside_exact_witness.v1.json",
    f"{EVIDENCE}/test_somaside_exact_witness.py",
}
PINNED = {
    METADATA[0]: "80c39e9e0d7fc0a819195cffa2e7607effac941a25f257fa0dcf2c5156d83b32",
    METADATA[1]: "2eee002364f1f3797d0f62fb50d708c0a91c19bb630102c1bf1cdc21531cdc3f",
    METADATA[2]: "f1dde555c18ff858f143275b5f2fda871a0e8f5c67c79a2aaff3e29e99aee331",
    f"{EVIDENCE}/somaside_exact_witness.py":
        "8d4d54364bf208f91987218a8aa4d12ce019f9640055c952caa88e751b284ef7",
    f"{EVIDENCE}/somaside_exact_witness.v1.json":
        "f57a4702387809899fca2e2cfc46b2fa7adb2481154b95c703aa9ce6384425e1",
    f"{EVIDENCE}/test_somaside_exact_witness.py":
        "4f6f2079f906c88488dfaa0d4366bb70b551b1ca13e2864230a1760a262e901d",
    "experiments/paper16/upstream-provenance.v1.json":
        "0b90db879b51ee6fe6e37fe443c58be9e572e3b202221958d33c487199345a55",
}
CARRIER_SHA = {
    "carrier_v0_edges.npz":
        "c94e885cc2e8cde78012ed0a68a4beb42eccfe1b64607bdc90ac46e675d6966d",
    "carrier_v0_nodes.parquet":
        "87aa46280d68a210f6c8ef4a044282fbbb62342bbeeaab8393b0fd7fa770515e",
}


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


def checked_path(name: str) -> Path:
    rel = PurePosixPath(name)
    require(not rel.is_absolute() and ".." not in rel.parts and rel.as_posix() == name,
            f"unsafe path: {name}")
    path = ROOT.joinpath(*rel.parts)
    require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT),
            f"missing or linked file: {name}")
    return path


def verify_inventory() -> dict[str, str]:
    manifest = read_json(ROOT / "manifest.json")
    require(set(manifest) == {"schema", "version", "files", "boundary"} and
            manifest["schema"] == "rime.malecns-two-source-witness.v1" and
            manifest["version"] == "1.0", "manifest identity")
    rows = manifest["files"]
    require(isinstance(rows, list) and len(rows) == len(EXPECTED) and
            all(isinstance(row, dict) and set(row) == {"path", "size", "sha256"}
                for row in rows), "manifest row structure")
    require([row["path"] for row in rows] == sorted(EXPECTED), "manifest include set")
    actual = set()
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        require(not path.is_symlink(), f"linked package entry: {rel}")
        if "__pycache__" in rel.parts:
            require(path.is_dir() or path.suffix == ".pyc", f"unexpected cache entry: {rel}")
        elif path.is_file():
            actual.add(rel.as_posix())
    require(actual == EXPECTED | {"manifest.json"},
            f"package inventory differs: missing={sorted((EXPECTED | {'manifest.json'}) - actual)}, "
            f"extra={sorted(actual - (EXPECTED | {'manifest.json'}))}")
    found = {}
    for row in rows:
        name = row["path"]
        path = checked_path(name)
        require(type(row["size"]) is int and row["size"] >= 0 and
                path.stat().st_size == row["size"] and
                isinstance(row["sha256"], str) and
                re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is not None and
                digest(path) == row["sha256"], f"byte mismatch: {name}")
        found[name] = row["sha256"]
    for name, expected in PINNED.items():
        require(found[name] == expected, f"pinned input drift: {name}")
    return found


def check_record(found: dict[str, str]) -> None:
    record = read_json(checked_path(f"{EVIDENCE}/somaside_exact_witness.v1.json"))
    require(record.get("format") == "from-support-to-state.somaside-witness.v1" and
            record.get("producer_sha256") == found[f"{EVIDENCE}/somaside_exact_witness.py"]
            and record.get("carrier_sha256") == CARRIER_SHA, "witness identity")
    source_rows = record.get("source_records")
    require(isinstance(source_rows, list) and
            {(row["path"], row["checkout_sha256"]) for row in source_rows}
            == {(name, found[name]) for name in METADATA}, "Paper XVI source bindings")
    derived = record.get("derived", {})
    require(derived.get("cross_product") == -36355 and
            derived.get("exact_difference") == [-661, 84521472], "witness conclusion")


def run_check(replay: bool, carrier_dir: Path | None) -> None:
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    script = checked_path(f"{EVIDENCE}/somaside_exact_witness.py")
    result_path = checked_path(f"{EVIDENCE}/somaside_exact_witness.v1.json")
    cmd = [sys.executable, "-B", str(script), "--result", str(result_path)]
    if replay:
        require(carrier_dir is not None and carrier_dir.is_dir(),
                "--replay requires --carrier-dir from the extracted Dataset")
        require(sys.version_info[:2] == (3, 13), "source replay requires Python 3.13")
        for name, expected in {"numpy": "2.1.3", "pandas": "3.0.3",
                               "pyarrow": "18.0.0"}.items():
            require(version(name) == expected, f"{name} must be {expected}")
        for name, expected in CARRIER_SHA.items():
            require(digest(carrier_dir / name) == expected, f"carrier digest: {name}")
        cmd.extend(["--check-source", "--carrier-dir", str(carrier_dir)])
    process = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True)
    require(process.returncode == 0, f"witness check failed: {process.stderr[-3000:]}")
    result = json.loads(process.stdout.strip().splitlines()[-1])
    require(result == {"status": "PASS", "scope":
                       "SOURCE_EXTRACTION_AND_EXACT_ARITHMETIC" if replay else
                       "COMPACT_EXACT_ARITHMETIC_ONLY", "cross_product": -36355,
                       "exact_difference": [-661, 84521472]}, "witness check report")
    controls = subprocess.run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(script.parent),
         "-p", "test_somaside_exact_witness.py"], cwd=ROOT, env=env,
        text=True, capture_output=True)
    require(controls.returncode == 0 and "Ran 6 tests" in controls.stderr,
            f"witness controls failed: {controls.stderr[-3000:]}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--carrier-dir", type=Path)
    args = parser.parse_args()
    try:
        check_record(verify_inventory())
        run_check(args.replay, args.carrier_dir)
        check_record(verify_inventory())
    except (ValueError, OSError, KeyError, IndexError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}))
        return 1
    print(json.dumps({"status": "SOURCE_EXTRACTION_PASS" if args.replay else
                      "COMPACT_WITNESS_PASS", "cross_product": -36355,
                      "exact_difference": [-661, 84521472]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
