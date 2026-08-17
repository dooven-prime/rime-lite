"""Register the fixed-frame exploratory incidence profile as Paper VII evidence.

Only fixed canonical-frame artifacts are admitted.  Endogenous-frame profiles,
the n=8 exact spectrum, and conjectural generalizations are intentionally not
consumed by this Paper VII v2.1 registration.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = (
    ROOT
    / "experiments"
    / "exploratory"
    / "structural_functionals"
    / "incidence_profiles"
    / "results"
)
RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
JSON_PATH = RESULTS_DIR / "fixed_frame_incidence_profiles_v2_1.json"
TEXT_PATH = RESULTS_DIR / "fixed_frame_incidence_profiles_v2_1.txt"

SOURCES = {
    "family_index": SOURCE_ROOT / "axis_balanced_family_index.json",
    "fixed_summary": SOURCE_ROOT / "axis_balanced_fixed_summary.json",
    "canonical_carrier_certificate": (
        SOURCE_ROOT / "exact_certificates" / "canonical_carrier_zero_products.json"
    ),
    "axis_rotation_control": (
        SOURCE_ROOT / "exact_certificates" / "drop_axis0_vs_axis2_ht.json"
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def source_ref(path: Path) -> dict:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest(path),
    }


def normalized_family(value) -> tuple[tuple[int, int, int], ...]:
    return tuple(sorted(tuple(int(item) for item in key) for key in value))


def main(*, write_results: bool = False) -> None:
    missing = [path for path in SOURCES.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing promoted source artifacts: {missing}")

    family_index = load(SOURCES["family_index"])
    fixed_summary = load(SOURCES["fixed_summary"])
    canonical = load(SOURCES["canonical_carrier_certificate"])
    rotation = load(SOURCES["axis_rotation_control"])

    assert family_index["schema"] == "rime.axis-balanced-family-index.v1"
    assert family_index["claim_status"] == "Computational Certificate"
    assert family_index["family_count"] == 19
    labelled_family_count = sum(row["orbit_size"] for row in family_index["families"])
    assert labelled_family_count == 63

    assert fixed_summary["schema"] == "rime.incidence-profile-orbit-summary.v1"
    assert fixed_summary["claim_status"] == "Computational Observation"
    assert fixed_summary["orbit_count"] == 19
    assert len(fixed_summary["rows"]) == 19

    active_rows = []
    inactive_orbits = []
    for row in fixed_summary["rows"]:
        assert row["profile_signature"]["protocol"] == "fixed_full"
        if row["total_supported_routes"] == 0:
            assert row["unprotected_zero"] == 0
            inactive_orbits.append(row["orbit_id"])
            continue
        rate = Fraction(row["unprotected_zero"], row["total_supported_routes"])
        assert rate == Fraction(2, 9)
        assert row["protected_routes"] == 0
        assert row["zero_mechanism_counts"] == {
            "physical_carrier_forced": row["unprotected_zero"]
        }
        active_rows.append(
            {
                "orbit_id": row["orbit_id"],
                "operator_count": row["operator_count"],
                "supported_routes": row["total_supported_routes"],
                "unprotected_zero": row["unprotected_zero"],
                "zero_over_all_supported": "2/9",
                "mechanism": "physical_carrier_forced",
            }
        )

    assert canonical["schema"] == "rime.exact-canonical-carrier-certificate.v2"
    assert canonical["claim_status"] == "Computational Certificate"
    assert canonical["certificate_kind"] == "exact_finite_algebraic"
    assert canonical["int64_all_arithmetic_safety_verified"]
    arithmetic_audit = canonical["int64_preoperation_audit"]
    expected_arithmetic_kinds = {
        "identity",
        "add",
        "subtract",
        "scale",
        "adjoint",
        "matmul",
        "trace",
    }
    assert set(arithmetic_audit["coverage"]) == expected_arithmetic_kinds
    assert set(arithmetic_audit["operation_kind_counts"]) == expected_arithmetic_kinds
    assert all(
        arithmetic_audit["operation_kind_counts"][kind] > 0
        for kind in expected_arithmetic_kinds
    )
    assert arithmetic_audit["maximum_conservative_output_bound"] < arithmetic_audit["int64_limit"]
    assert canonical["all_operative_generators_preserve_registered_carriers"]
    assert len(canonical["operative_generator_carrier_checks"]) == 18
    assert all(
        row["represented_operator_preserves_registered_carriers"]
        and row["adjoint_preserves_registered_carriers"]
        and row["anti_hermitian_numerator_preserves_registered_carriers"]
        for row in canonical["operative_generator_carrier_checks"]
    )
    assert canonical["projector_family"]["pairwise_orthogonality_verified"]
    assert canonical["projector_family"]["completeness_verified"]
    assert canonical["projector_family"]["dimension_sum_verified"]
    assert len(canonical["sectors"]) == 9
    assert all(
        row["projector_idempotence_verified"]
        and row["projector_self_adjoint_verified"]
        and row["qt_joint_eigenvalue_verified"]
        and row["ht_joint_eigenvalue_verified"]
        and row["projector_preserves_registered_carriers"]
        and row["carrier_mask_verified"]
        for row in canonical["sectors"]
    )
    assert len(canonical["canonical_zero_triples"]) == 4
    assert all(
        row["all_generator_pairs_have_exact_zero_product"]
        for row in canonical["canonical_zero_triples"]
    )
    assert len(canonical["fixed_frame_orbit_certificates"]) == 19
    assert all(
        row["all_observed_zero_routes_exactly_certified"]
        for row in canonical["fixed_frame_orbit_certificates"]
    )

    assert rotation["claim_status"] == "Computational Certificate"
    assert rotation["certificate_kind"] == "exact_combinatorial"
    assert rotation["verified"]
    source_family = normalized_family(rotation["source_family"])
    target_family = normalized_family(rotation["target_family"])
    assert source_family != target_family
    axis0_half_turns = {(0, -1, 2), (0, 1, 2)}
    axis2_half_turns = {(2, -1, 2), (2, 1, 2)}
    full_family = {
        (axis, side, direction)
        for axis in range(3)
        for side in (-1, 1)
        for direction in (-1, 1, 2)
    }
    assert set(source_family) == full_family - axis0_half_turns
    assert set(target_family) == full_family - axis2_half_turns

    total_supported = sum(row["supported_routes"] for row in active_rows)
    total_zero = sum(row["unprotected_zero"] for row in active_rows)
    assert Fraction(total_zero, total_supported) == Fraction(2, 9)

    payload = {
        "schema": "paper7.fixed-frame-incidence-profile-registration.v2.1",
        "scope": "fixed canonical sector frame only",
        "claim_status_by_component": {
            "axis_balanced_family_index": "Computational Certificate",
            "canonical_carrier_zero_products": "Computational Certificate",
            "fixed_frame_profile_census": "Computational Observation",
            "axis_rotation_control": "Computational Certificate",
        },
        "family_index": {
            "labelled_nonempty_family_count": labelled_family_count,
            "rotation_orbit_representative_count": family_index["family_count"],
            "rotation_group_order": 24,
        },
        "fixed_frame_census": {
            "frame": "canonical joint quarter-turn/half-turn sector frame",
            "orbit_rows_with_supported_routes": len(active_rows),
            "orbit_rows_without_supported_routes": len(inactive_orbits),
            "inactive_orbit_ids": inactive_orbits,
            "total_supported_routes_across_active_orbits": total_supported,
            "total_carrier_forced_zeros_across_active_orbits": total_zero,
            "observed_rate": "2/9",
            "rows": active_rows,
            "status": "finite numerical census",
        },
        "exact_numerator_certificate": {
            "coefficient_ring": canonical["coefficient_ring"],
            "arithmetic_backend": canonical["arithmetic_backend"],
            "int64_preoperation_audit": {
                "coverage": arithmetic_audit["coverage"],
                "operation_count": arithmetic_audit["operation_count"],
                "operation_kind_counts": arithmetic_audit["operation_kind_counts"],
                "maximum_conservative_output_bound": arithmetic_audit[
                    "maximum_conservative_output_bound"
                ],
                "int64_limit": arithmetic_audit["int64_limit"],
                "all_operations_safe": arithmetic_audit["all_operations_safe"],
            },
            "registered_carriers": ["cp", "ep", "co", "eo"],
            "canonical_zero_triples": canonical["canonical_zero_triples"],
            "all_fixed_frame_orbit_zero_routes_covered": True,
        },
        "axis_rotation_control": {
            "source_family": "full generator family minus axis-0 half turns (L2/R2)",
            "target_family": "full generator family minus axis-2 half turns (F2/B2)",
            "labelled_families_distinct": True,
            "same_orientation_preserving_rotation_orbit": True,
            "profile_invariance_requires": (
                "representation equivariance and transport of the sector and carrier frames"
            ),
        },
        "promotion_boundary": {
            "exact": (
                "Every zero counted by the fixed-frame carrier-forced numerator has "
                "an exact carrier-disjointness certificate."
            ),
            "numerical_only": (
                "Nonvanishing of every remaining supported route, hence the 2/9 rate."
            ),
            "excluded": [
                "endogenous-frame profiles",
                "n=8 exact spectrum",
                "cross-frame alignment and refinement",
                "universal 2/9 law",
            ],
        },
        "provenance": {
            "registration_script": source_ref(Path(__file__)),
            "source_artifacts": {
                name: source_ref(path) for name, path in SOURCES.items()
            },
        },
    }

    json_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"

    lines = [
        "Paper VII v2.1 fixed-frame incidence-profile registration",
        "=" * 72,
        f"axis-balanced families: {labelled_family_count} labelled / 19 rotation orbits",
        f"supported fixed-frame orbit rows: {len(active_rows)}",
        f"unsupported fixed-frame orbit rows: {len(inactive_orbits)}",
        f"aggregate fixed-frame census: {total_zero}/{total_supported} = 2/9",
        "exact boundary: every counted zero has a carrier-disjointness certificate",
        "numerical boundary: remaining supported routes are not exactly certified nonzero",
        "axis control: drop-axis0-HT and drop-axis2-HT are distinct but rotation conjugate",
    ]
    text_value = "\n".join(lines) + "\n"
    if write_results:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        JSON_PATH.write_text(json_text, encoding="utf-8", newline="\n")
        TEXT_PATH.write_text(text_value, encoding="utf-8", newline="\n")
    else:
        if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != json_text:
            raise SystemExit(f"STALE {JSON_PATH}; rerun with --write-results")
        if not TEXT_PATH.is_file() or TEXT_PATH.read_text(encoding="utf-8") != text_value:
            raise SystemExit(f"STALE {TEXT_PATH}; rerun with --write-results")
    print("\n".join(lines))
    print(f"\n{'WROTE' if write_results else 'PASS'} {JSON_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-results", action="store_true")
    main(write_results=parser.parse_args().write_results)
