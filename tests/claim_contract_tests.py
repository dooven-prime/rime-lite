"""Executable claim-status contracts for the active Papers I--VII code."""

import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rime.accessibility import (  # noqa: E402
    UNREACHED_DEPTH,
    compute_direct_support,
    compute_lie_accessibility_audit,
)
from rime.algebra import audit_finite_dimensional_star_algebra  # noqa: E402
from rime.cubie import CubieMove  # noqa: E402
from rime.cubieoperator import CubieSpectralOperator  # noqa: E402
from rime.rep_utils import build_system_from_perms, symmetric_group  # noqa: E402
from rime.spectral_utils import (  # noqa: E402
    joint_diag_sectors,
    sector_bases_from_projectors,
)
from rime.spectralstructure import SpectralStructure  # noqa: E402


TOL = 1e-8


def _assert_raises(exc_type, function):
    try:
        function()
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__}")


def test_paper1_arithmetic_claim_boundaries():
    structure = SpectralStructure(CubieMove.prim_moves)

    partition = structure.audit_partition_integrality()
    assert not partition["all_integer"]
    assert not partition["rationality_conclusion"]["hypothesis_satisfied"]
    assert not partition["rationality_conclusion"]["certifies_rationality"]

    block_status = structure.verify_integrality()
    assert block_status["certified_blocks"] == ["cp", "ep"]
    assert block_status["unresolved_blocks"] == ["co", "eo"]
    for block in ("co", "eo"):
        assert all(
            record["status"] == "not_certified"
            and record["is_integer"] is None
            for record in block_status[block].values()
        )

    assert structure.structural_spectral_field_status() == "not_certified"
    field_registration = structure.register_spectral_field()
    assert field_registration["claim_status"] == "computational_observation"
    assert "exact field certificate" in field_registration["note"]


def test_ep_semisimplicity_does_not_use_gram_nondegeneracy():
    identity = np.eye(2, dtype=complex)
    pauli_x = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    pauli_y = np.array([[0.0, -1j], [1j, 0.0]], dtype=complex)
    pauli_z = np.diag([1.0, -1.0]).astype(complex)
    redundant_span = [identity, pauli_x, pauli_y, pauli_z, identity]

    certificate = audit_finite_dimensional_star_algebra(
        [pauli_x, pauli_z], redundant_span, tol=1e-10
    )

    assert certificate["span_dimension"] == 4
    assert not certificate["basis_linearly_independent"]
    assert certificate["declared_basis_gram_residual"] > 0.5
    assert certificate["registered_unital_star_algebra"]
    assert certificate["semisimplicity_supported"]
    assert certificate["semisimplicity_basis"] == (
        "finite_dimensional_unital_complex_star_algebra_theorem"
    )
    assert "gram_determinant" not in certificate


def test_h1_fails_in_declared_s4_registration():
    generators = [
        (1, 0, 2, 3),
        (2, 0, 1, 3),
        (1, 2, 3, 0),
    ]
    system = build_system_from_perms(symmetric_group(4), generators)
    audit = compute_lie_accessibility_audit(
        system["Vs"], system["Xs"], max_depth=4, tol=TOL
    )
    r1 = np.any(audit["R1_Lie"], axis=0)
    r2 = np.any(audit["R2_Lie"], axis=0)
    depth = audit["D_Lie_cutoff"]
    h1_counterexamples = (~r1) & (~r2) & (depth == 2)

    assert int(np.sum(h1_counterexamples)) == 2
    assert system["sector_registration"]["order_dependent"]
    assert not system["sector_registration"]["joint_spectral_claim"]


def test_registered_ten_edge_graph_is_not_a_star():
    operator = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
    projectors = operator.center_decomposition()["projectors"]
    bases = sector_bases_from_projectors(projectors)
    family = [
        value.toarray() if hasattr(value, "toarray") else np.asarray(value)
        for value in operator.rho_matrices()
    ]
    directed = compute_direct_support(bases, family, tol=0.05)
    graph = directed | directed.T
    edge_count = int(np.sum(np.triu(graph, 1)))
    degrees = [int(value) for value in np.sum(graph, axis=1)]
    star_degrees = sorted([len(bases) - 1] + [1] * (len(bases) - 1))

    assert edge_count == 10
    assert degrees == [0, 2, 2, 2, 2, 5, 3, 1, 3]
    assert sorted(degrees) != star_degrees


def test_unreached_sentinel_is_cutoff_relative_not_infinity():
    identity = np.eye(3, dtype=complex)
    sectors = [identity[:, [index]] for index in range(3)]
    x01 = np.array(
        [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
        dtype=complex,
    )
    x12 = np.array(
        [[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, -1.0, 0.0]],
        dtype=complex,
    )

    shallow = compute_lie_accessibility_audit(
        sectors, [x01, x12], max_depth=1, tol=TOL
    )
    deeper = compute_lie_accessibility_audit(
        sectors, [x01, x12], max_depth=2, tol=TOL
    )

    assert shallow["D_Lie_cutoff"][2, 0] == UNREACHED_DEPTH
    assert deeper["D_Lie_cutoff"][2, 0] == 1
    assert shallow["tested_max_depth_index"] == 0
    assert shallow["lie_depth_census"]["unreached"] > 0


def test_nonnormal_samples_cannot_enter_joint_spectral_registration():
    nonnormal = np.array([[0.0, 1.0], [0.0, 0.0]], dtype=complex)
    _assert_raises(ValueError, lambda: joint_diag_sectors([nonnormal]))


def test_registered_observations_use_frozen_claim_statuses():
    paths = [
        ROOT / "experiments/paper3/results/composition_obstruction.observation.json",
        ROOT / "experiments/paper4/results/rubik_joint_spectrum_registration.observation.json",
    ]
    for path in paths:
        record = json.loads(path.read_text(encoding="utf-8"))
        assert record["artifact_role"] == "cached_computational_observation"
        assert record["claim"]["status"] == "computational_certificate"


def test_public_paper_validation_avoids_internal_data_outputs():
    forbidden_literals = ('"data"', "'data'")
    for paper_number in range(1, 8):
        validation_dir = ROOT / f"experiments/paper{paper_number}/validation"
        for path in validation_dir.glob("*.py"):
            source = path.read_text(encoding="utf-8")
            assert "DATA_DIR" not in source, path
            assert not any(literal in source for literal in forbidden_literals), path


def test_paper_figure_data_matches_frozen_censuses():
    paper1 = json.loads(
        (ROOT / "experiments/paper1/results/figure_data.json").read_text(
            encoding="utf-8"
        )
    )
    layers = {row["k"]: row for row in paper1["canonical_layers"]}
    assert layers[4]["blocks"] == {"cp": 24, "ep": 72, "co": 3, "eo": 7}
    assert layers[6]["blocks"] == {"cp": 32, "ep": 0, "co": 3, "eo": 0}
    assert {
        block: sum(row["blocks"][block] for row in layers.values())
        for block in ("cp", "ep", "co", "eo")
    } == {"cp": 64, "ep": 144, "co": 8, "eo": 12}

    paper2 = json.loads(
        (ROOT / "experiments/paper2/results/direct_transport.json").read_text(
            encoding="utf-8"
        )
    )
    degrees = [0] * paper2["sector_count"]
    for edge in paper2["edges"]:
        degrees[edge["source"] - 1] += 1
        degrees[edge["target"] - 1] += 1
    assert len(paper2["edges"]) == 10
    assert degrees == paper2["degree_sequence"] == [0, 2, 2, 2, 2, 5, 3, 1, 3]

    paper4 = json.loads(
        (ROOT / "experiments/paper4/results/figure_data.json").read_text(
            encoding="utf-8"
        )
    )
    assert len(paper4["points"]) == 9
    assert sum(row["dimension"] for row in paper4["points"]) == 228
    assert paper4["critical_parameters"] == ["2/7", "2/5", "1/2", "2/3", "4/5"]
    assert paper4["interior_collisions"]["2/3"] == [
        ["S5", "S6"],
        ["S5", "S7"],
        ["S6", "S7"],
        ["S8", "S9"],
    ]

    paper5 = json.loads(
        (ROOT / "experiments/paper5/results/figure_data.json").read_text(
            encoding="utf-8"
        )
    )
    exact = paper5["exact_counterexample"]
    assert exact["cancelling_terms"] == [2, 2]
    assert exact["emergent_terms"] == [3, 2]
    assert exact["cancelling_commutator"] == 0
    assert exact["emergent_commutator"] == 1
    s4 = paper5["s4_low_order_census"]
    assert (
        s4["bracket_emergent_pairs"]
        + s4["product_supported_r2_zero_pairs"]
        + s4["unresolved_within_tested_order"]
        == s4["r1_zero_pairs"]
        == 80
    )

    paper6 = json.loads(
        (ROOT / "experiments/paper6/results/figure_data.json").read_text(
            encoding="utf-8"
        )
    )
    assert [
        (row["rank"], row["nullity"]) for row in paper6["linearized_maps"]
    ] == [(11, 7), (14, 4)]
    assert [row["sectors"] for row in paper6["pointwise_registrations"]] == [
        9,
        15,
        15,
        15,
    ]
    assert all(
        row["r1_op"] != row["r1_lie"]
        for row in paper6["pointwise_registrations"]
    )

    paper7_incidence = json.loads(
        (ROOT / "experiments/paper7/results/incidence_geometry.json").read_text(
            encoding="utf-8"
        )
    )
    assert (
        paper7_incidence["formulas"]["fixed_double_rank_relative_codimension"]
        == "rs"
    )
    square10 = next(
        row
        for row in paper7_incidence["configurations"]
        if row["label"] == "square_d_10"
    )
    assert square10["type_iv_codimension"] == 75

    paper7_audit = json.loads(
        (
            ROOT
            / "experiments/paper7/results/projected_composition_audit.json"
        ).read_text(encoding="utf-8")
    )
    rubik = next(row for row in paper7_audit["systems"] if row["name"] == "rubik")
    assert rubik["operator_registration"]["zero_operator_count"] == 6
    assert rubik["operator_registration"]["nonzero_operator_count"] == 12
    assert rubik["counts"]["unprotected_zero"] == 576
    assert rubik["counts"]["total"] == 2592


if __name__ == "__main__":
    tests = [
        test_paper1_arithmetic_claim_boundaries,
        test_ep_semisimplicity_does_not_use_gram_nondegeneracy,
        test_h1_fails_in_declared_s4_registration,
        test_registered_ten_edge_graph_is_not_a_star,
        test_unreached_sentinel_is_cutoff_relative_not_infinity,
        test_nonnormal_samples_cannot_enter_joint_spectral_registration,
        test_registered_observations_use_frozen_claim_statuses,
        test_public_paper_validation_avoids_internal_data_outputs,
        test_paper_figure_data_matches_frozen_censuses,
    ]
    for test in tests:
        test()
        print(f"{test.__name__}: OK")
    print("claim_contract_tests.py: OK")
