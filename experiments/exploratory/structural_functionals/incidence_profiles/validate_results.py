#!/usr/bin/env python
"""Validate the migrated incidence-profile package and finite result closure."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from incidence_profiles import REPO_ROOT


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
CLAIM_STATUSES = {
    "Theorem",
    "Computational Certificate",
    "Computational Observation",
    "Research Program",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_artifact_references(payload: dict, owner: Path) -> None:
    references = payload.get("provenance", {}).get("source_artifacts", [])
    assert references, f"missing source-artifact closure: {owner}"
    seen = set()
    for reference in references:
        path = reference["path"]
        assert path not in seen, f"duplicate source artifact {path}: {owner}"
        seen.add(path)
        artifact = REPO_ROOT / Path(path)
        assert artifact.is_file(), f"missing bound artifact {path}: {owner}"
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        assert digest == reference["sha256"], f"artifact digest mismatch {path}: {owner}"


def validate_profile(path: Path) -> dict:
    profile = load(path)
    assert profile["schema"] == "rime.incidence-profile.v1"
    assert profile["claim_status"] == "Computational Observation"
    validate_artifact_references(profile, path)
    counts = profile["counts"]
    assert counts["total_supported_routes"] >= counts["unprotected_routes"]
    assert counts["unprotected_routes"] >= counts["unprotected_zero"]
    return profile


def main() -> None:
    family_index_path = RESULTS / "axis_balanced_family_index.json"
    family_index = load(family_index_path)
    assert family_index["claim_status"] == "Computational Certificate"
    assert family_index["certificate_kind"] == "exact_finite_combinatorial"
    assert family_index["family_count"] == len(family_index["families"]) == 19
    validate_artifact_references(family_index, family_index_path)

    profile_sets = {}
    protocol_directories = {
        "fixed_full": RESULTS / "axis_balanced_fixed",
        "endogenous": RESULTS / "axis_balanced_endogenous",
    }
    for protocol, directory in protocol_directories.items():
        paths = sorted(directory.glob("*.json"))
        assert len(paths) == 19, f"expected 19 {protocol} profiles, found {len(paths)}"
        assert all(path.name.endswith(f"__{protocol}.json") for path in paths)
        profiles = [validate_profile(path) for path in paths]
        assert {row["protocol"] for row in profiles} == {protocol}
        assert len({row["family"]["orbit_id"] for row in profiles}) == 19
        profile_sets[protocol] = profiles

    nonempty_fixed = [
        row for row in profile_sets["fixed_full"]
        if row["counts"]["total_supported_routes"]
    ]
    rates = {
        Fraction(
            row["counts"]["unprotected_zero"],
            row["counts"]["total_supported_routes"],
        )
        for row in nonempty_fixed
    }
    assert rates == {Fraction(2, 9)}

    canonical_path = RESULTS / "exact_certificates/canonical_carrier_zero_products.json"
    canonical = load(canonical_path)
    assert canonical["schema"] == "rime.exact-canonical-carrier-certificate.v2"
    assert canonical["claim_status"] == "Computational Certificate"
    assert canonical["certificate_kind"] == "exact_finite_algebraic"
    assert canonical["all_operative_generators_preserve_registered_carriers"]
    assert canonical["int64_pair_matmul_safety_verified"]
    assert canonical["int64_all_arithmetic_safety_verified"]
    arithmetic = canonical["int64_preoperation_audit"]
    assert set(arithmetic["coverage"]) == {
        "identity",
        "add",
        "subtract",
        "scale",
        "adjoint",
        "matmul",
        "trace",
    }
    assert set(arithmetic["operation_kind_counts"]) == set(arithmetic["coverage"])
    assert arithmetic["maximum_conservative_output_bound"] < arithmetic["int64_limit"]
    family = canonical["projector_family"]
    assert family["pairwise_orthogonality_verified"]
    assert family["completeness_verified"]
    assert family["dimension_sum_verified"]
    assert all(
        row["represented_operator_preserves_registered_carriers"]
        and row["adjoint_preserves_registered_carriers"]
        and row["anti_hermitian_numerator_preserves_registered_carriers"]
        for row in canonical["operative_generator_carrier_checks"]
    )
    assert all(
        row["projector_idempotence_verified"]
        and row["projector_self_adjoint_verified"]
        and row["qt_joint_eigenvalue_verified"]
        and row["ht_joint_eigenvalue_verified"]
        and row["projector_preserves_registered_carriers"]
        and row["carrier_mask_verified"]
        for row in canonical["sectors"]
    )
    validate_artifact_references(canonical, canonical_path)

    spectrum_path = RESULTS / "exact_certificates/n8_exact_spectrum.json"
    spectrum = load(spectrum_path)
    assert spectrum["claim_status"] == "Computational Certificate"
    assert spectrum["multiplicity_sum"] == 228
    assert spectrum["operator_sum_self_adjoint_verified"]
    assert spectrum["int64_preoperation_audit"]["all_operations_safe"]
    validate_artifact_references(spectrum, spectrum_path)

    route_path = RESULTS / "exact_certificates/axes02_qt_fixed_full_routes.json"
    route = load(route_path)
    assert route["claim_status"] == "Computational Certificate"
    assert route["certificate_kind"] == "conditional_exact_route_promotion"
    assert "\\" not in route["source_profile"]
    assert any("[X_g,C_b]" in item for item in route["upgrade_requirements"])
    validate_artifact_references(route, route_path)

    for path in (
        RESULTS / "axis_balanced_fixed_summary.json",
        RESULTS / "axis_balanced_endogenous_summary.json",
        RESULTS / "conjecture_audit.json",
    ):
        payload = load(path)
        assert payload["claim_status"] in CLAIM_STATUSES
        if "directory" in payload:
            assert "\\" not in payload["directory"]
        validate_artifact_references(payload, path)

    migration_path = RESULTS / "migration_validation.json"
    migration = load(migration_path)
    assert migration["claim_status"] == "Computational Certificate"
    assert migration["certificate_kind"] == "finite_migration_equivalence"
    assert migration["profile_count"] == 38
    assert migration["all_scientific_fields_match"]
    assert "does not itself promote any artifact" in migration["boundary"]
    validate_artifact_references(migration, migration_path)

    for path in RESULTS.rglob("*.json"):
        payload = load(path)
        if isinstance(payload, dict) and "claim_status" in payload:
            assert payload["claim_status"] in CLAIM_STATUSES, (
                f"noncanonical claim status {payload['claim_status']!r}: {path}"
            )

    print("incidence-profile result closure validated: 19 fixed + 19 endogenous profiles")


if __name__ == "__main__":
    main()
