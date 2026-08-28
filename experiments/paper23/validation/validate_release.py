#!/usr/bin/env python3
"""Validate the Paper XXIII paper-owned release closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from _bootstrap import PACKAGE, REPOSITORY

PAPER = REPOSITORY / "papers" / "paper23"
RESULTS = PACKAGE / "results"
LEAN = PACKAGE / "lean"
RECEIPT = RESULTS / "paper23_release_receipt_v1.json"

from validate_registry import validate as validate_core  # noqa: E402
from validate_binary_clean_exhaustion import validate as validate_binary  # noqa: E402
from validate_fiber_incidence import validate as validate_fiber  # noqa: E402
from validate_kernel_schreier_corridors import validate as validate_corridor  # noqa: E402
from validate_pair_hitting import validate as validate_pair  # noqa: E402
from validate_waiting_capacity_audit import validate as validate_waiting  # noqa: E402


CORE_RESULTS = (
    "n2_k2_v2.json",
    "n3_k2_v2.json",
    "n4_k2_v2_summary.json",
    "slow_family_suite_n2_n12_v1.json",
)

AUDIT_RESULTS = {
    "pair_hitting_audit_n3_n4_v1.json": validate_pair,
    "fiber_incidence_potential_audit_n3_n4_v1.json": validate_fiber,
    "kernel_schreier_corridor_audit_n3_n4_v1.json": validate_corridor,
    "kernel_schreier_corridor_audit_slow_families_v1.json": validate_corridor,
    "waiting_capacity_tradeoff_audit_slow_families_v1.json": validate_waiting,
    "binary_clean_corridor_exhaustion_n2_n6_v1.json": validate_binary,
}

SOURCE_FILES = (
    "census.py",
    "enumerate_binary_clean_corridors.py",
    "families.py",
    "fiber_incidence_controls.py",
    "fiber_incidence_potential.py",
    "kernel_schreier_corridors.py",
    "merge_census.py",
    "pair_hitting.py",
    "path_potential.py",
    "registry.py",
    "symbolic_search.py",
)

VALIDATION_FILES = (
    "_bootstrap.py",
    "audit_fiber_incidence.py",
    "audit_kernel_schreier_corridors.py",
    "audit_pair_hitting.py",
    "audit_waiting_capacity.py",
    "validate_binary_clean_exhaustion.py",
    "validate_fiber_incidence.py",
    "validate_kernel_schreier_corridors.py",
    "validate_pair_hitting.py",
    "validate_registry.py",
    "validate_release.py",
    "validate_waiting_capacity_audit.py",
)

LEAN_FILES = (
    "Formalization.lean",
    "Formalization/AxiomAudit.lean",
    "Formalization/PairHitting.lean",
    "Formalization/ParameterFreeArithmetic.lean",
    "README.md",
    "formalization_receipt.json",
    "lake-manifest.json",
    "lakefile.toml",
    "lean-toolchain",
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(REPOSITORY).as_posix()


def declared_files() -> list[Path]:
    paths = [
        PAPER / "Paper XXIII.md",
        PAPER / "references-v1.0.bib",
        PAPER / "paper23_arxiv.pdf",
        PACKAGE / "README.md",
    ]
    paths.extend(PACKAGE / name for name in SOURCE_FILES)
    paths.extend(PACKAGE / "validation" / name for name in VALIDATION_FILES)
    paths.extend(RESULTS / name for name in CORE_RESULTS)
    paths.extend(RESULTS / name for name in AUDIT_RESULTS)
    paths.extend(
        RESULTS / "n4_k2_v2_shards" / f"shard_{index:02d}.json"
        for index in range(8)
    )
    paths.extend(LEAN / name for name in LEAN_FILES)
    return sorted(set(paths))


def validate_lean_receipt() -> None:
    receipt_path = LEAN / "formalization_receipt.json"
    payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert payload["status"] == "pass"
    assert payload["toolchain"]["lean"] == "4.33.0"
    assert payload["toolchain"]["mathlib_commit"] == (
        "db584cd6d46c92f209a44c0f1c829460d327499d"
    )
    for name, expected in payload["sha256"].items():
        path = LEAN / name
        assert path.is_file(), f"missing Lean source: {path}"
        assert file_sha256(path) == expected, f"Lean digest mismatch: {path}"


def validate_document_boundary() -> None:
    checked = [
        PAPER / "Paper XXIII.md",
        PACKAGE / "README.md",
    ]
    stale = "experiments/synchronizing_automata"
    for path in checked:
        text = path.read_text(encoding="utf-8")
        assert stale not in text, f"stale release path in {path}"
    manuscript = (PAPER / "Paper XXIII.md").read_text(encoding="utf-8")
    normalized_manuscript = " ".join(manuscript.split())
    assert manuscript.startswith(
        "# Kernel Corridors and Schreier Waiting in Synchronizing Automata"
    )
    assert (
        "Within the cited comparison set, no theorem was found"
        in manuscript
    )
    assert "Corollary 3.4 (Reachable-Unit Packing Area)" in normalized_manuscript
    assert (
        "unit terminal excess does not imply unit upstream pair mass"
        in normalized_manuscript
    )
    assert "does not add a second waiting coordinate" in normalized_manuscript
    assert "not a proposed universal Černý potential" in normalized_manuscript
    assert "remain open; no paper number frozen" not in manuscript
    lean_readme = (LEAN / "README.md").read_text(encoding="utf-8")
    assert "**Status:** compiled" in lean_readme
    assert "uncompiled" not in lean_readme.lower()


def build_receipt() -> dict:
    for path in declared_files():
        assert path.is_file(), f"missing declared release file: {path}"

    validate_document_boundary()
    for name in CORE_RESULTS:
        validate_core(RESULTS / name)
    for name, validator in AUDIT_RESULTS.items():
        errors = validator(RESULTS / name)
        assert not errors, f"{name}: {'; '.join(errors)}"
    validate_lean_receipt()

    summary = json.loads((RESULTS / "n4_k2_v2_summary.json").read_text(encoding="utf-8"))
    shard_rows = summary["shards"]
    assert len(shard_rows) == 8
    for row in shard_rows:
        path = REPOSITORY / row["path"]
        assert path.parent == RESULTS / "n4_k2_v2_shards"
        assert file_sha256(path) == row["file_sha256"]

    return {
        "schema": "rime.paper23.release-receipt.v1",
        "paper": "XXIII",
        "status": "PASS",
        "date": "2026-08-27",
        "checks": {
            "paper_number_frozen": True,
            "prior_art_gate_closed": True,
            "terminology_gate_closed_for_checked_corpus": True,
            "specialization_gate_closed_for_checked_corpus": True,
            "n4_shard_count": 8,
            "n4_isomorphism_classes": summary["enumeration"]["isomorphism_classes"],
            "n4_synchronizing_classes": summary["enumeration"]["synchronizing_classes"],
            "lean_receipt_status": "pass",
        },
        "claim_boundary": {
            "prior_art": "bounded checked corpus; not exhaustive novelty certification",
            "specialization_read": "bounded hypothesis-by-hypothesis comparison",
            "finite_artifacts": "exact computational certificates; not manuscript proofs",
            "lean": "pair-hitting full; parameter-free arithmetic conditional only",
        },
        "sha256": {
            relative(path): file_sha256(path)
            for path in declared_files()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    receipt = build_receipt()
    if args.write_receipt:
        RECEIPT.write_text(
            json.dumps(receipt, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"WROTE {relative(RECEIPT)}")
    else:
        committed = json.loads(RECEIPT.read_text(encoding="utf-8"))
        assert committed == receipt, "release receipt does not match current closure"
    print(
        "PASS PAPER-XXIII: "
        f"{receipt['checks']['n4_isomorphism_classes']} n=4 classes, "
        f"{len(receipt['sha256'])} source-addressed files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
