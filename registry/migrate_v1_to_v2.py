"""Compile the frozen Paper X Registry v1 snapshot into Registry v2.0.

The v1 snapshot is immutable input.  Legacy row-splitting declarations below
are used only as migration source data; :func:`build` emits the capability-
aware Registry v2.0 contract owned by ``schemas/registry/v2.0.schema.json``.
"""

from __future__ import annotations

import copy
import hashlib
import json
import mimetypes
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V1_PATH = ROOT / "registry" / "paper10-release-v1.0.registry.json"
V2_PATH = ROOT / "registry" / "paper10-typed-v2.0.registry.json"
PAPER10_RESULT_PATH = (
    ROOT / "experiments" / "paper10" / "results" / "registry_evidence_v2.json"
)
PAPER10_RESULT_RELATIVE = "experiments/paper10/results/registry_evidence_v2.json"
LEGACY_IMPORT_PATH = (
    ROOT
    / "experiments"
    / "paper10"
    / "results"
    / "legacy_certificate_imports_v2.json"
)
LEGACY_IMPORT_RELATIVE = (
    "experiments/paper10/results/legacy_certificate_imports_v2.json"
)
VALIDATOR_VERSION = "registry-validator-v2.0"

STATUS = {
    "theorem": "Theorem",
    "evidence": "Computational Certificate",
    "diagnostic": "Computational Observation",
    "proxy_only": "Computational Observation",
    "boundary": "Computational Observation",
    "failure": "Computational Observation",
    "negative_control": "Computational Observation",
}
PUBLIC_STATUSES = set(STATUS.values())

RESULT_PRODUCERS = {
    PAPER10_RESULT_RELATIVE: (
        "experiments/paper10/validation/build_results.py"
    ),
    LEGACY_IMPORT_RELATIVE: (
        "experiments/paper10/validation/build_legacy_certificate_imports.py"
    ),
    "experiments/paper2/results/direct_transport.json": (
        "experiments/paper2/validation/transport_graph.py"
    ),
    "experiments/paper4/results/rubik_joint_spectrum_registration.observation.json": (
        "experiments/paper4/validation/rubik_joint_spectrum_registration.py"
    ),
    "experiments/paper7/results/incidence_geometry.json": (
        "experiments/paper7/validation/incidence_variety_codim.py"
    ),
    "experiments/paper7/results/projected_composition_audit.json": (
        "experiments/paper7/validation/rank_protected_bridge_audit.py"
    ),
    "experiments/paper7/results/full_array_lie_atlas.json": (
        "experiments/paper7/validation/atlas_r2_boundary.py"
    ),
}


def channel(
    channel_id: str,
    branch: str,
    carrier: str,
    semantics: str,
    *,
    claim_status: str = "Computational Observation",
    threshold: tuple[str, object, str] = ("norm", "1e-8", "declared finite audit"),
    depth_convention: str = "not applicable",
    depth_cutoff: int | str | None = None,
    saturation_status: str = "not_applicable",
    pair_scope: str | None = None,
) -> dict:
    kind, value, scope = threshold
    channel_id = channel_id.lower()
    if pair_scope is None:
        pair_scope = (
            "off_diagonal"
            if branch in {"operator", "route", "word", "lie", "hall"}
            else "not_applicable"
        )
    return {
        "id": channel_id,
        "branch": branch,
        "carrier": carrier,
        "semantics": semantics,
        "threshold_policy": {"kind": kind, "value": value, "scope": scope},
        "depth_convention": depth_convention,
        "depth_cutoff": depth_cutoff,
        "saturation_status": saturation_status,
        "pair_scope": pair_scope,
        "claim_status": claim_status,
    }


def rewrite_text(value: object) -> object:
    if not isinstance(value, str):
        return value
    replacements = [
        (r"tau\(R2\)/tau\(R1\)", "tau(R_2^Lie)/tau(R_1^Lie)"),
        (r"tau\(R1\) < tau\(R2\)", "tau(R_1^Lie) < tau(R_2^Lie)"),
        (r"R1/R2/D", "R_1^Lie/R_2^Lie/D_Lie"),
        (r"R1=", "R_1^Lie="),
        (r"R2=", "R_2^Lie="),
        (r"D_repaired", "D_Lie_repaired"),
        (r"\bD_max\b", "D_Lie,max"),
    ]
    for pattern, replacement in replacements:
        value = re.sub(pattern, replacement, value)
    return value


def relocate(path: str) -> str:
    return {
        "experiments/paper5/path_commutator_cancellation.py":
            "experiments/paper5/validation/path_commutator_cancellation.py",
        "experiments/paper7/incidence_variety_codim.py":
            "experiments/paper7/validation/incidence_variety_codim.py",
        "experiments/paper7/markov_graph_sof.py":
            "experiments/paper7/archive/markov_graph_sof.py",
        "experiments/paper10/mechanism_separation_theorem.py":
            "experiments/paper9/calibrated_response.py",
    }.get(path, path)


def object_config(
    *,
    sector_type: str,
    sector_origin: str,
    sector_algebra: str,
    sector_labels: dict,
    family_id: str,
    family_semantics: str,
    labels: list[str],
    operator_status: str,
    operator_description: str,
    ambient_status: str,
    ambient_type: str,
    multiplicities: str,
    embedding: str,
    operator_enabled: bool,
    lie_enabled: bool,
    lie_family_id: str | None,
    lie_method: str,
    hall: str,
    route: str,
    word: str,
    channels: list[dict],
    dynamic_class: str,
    entry_status: str,
    adjoint_closed: bool = False,
    mechanism_channels: list[str] | None = None,
) -> dict:
    return {
        "sector_type": sector_type,
        "sector_origin": sector_origin,
        "sector_algebra": sector_algebra,
        "sector_labels": sector_labels,
        "family_id": family_id,
        "family_semantics": family_semantics,
        "labels": labels,
        "operator_status": operator_status,
        "operator_description": operator_description,
        "ambient_status": ambient_status,
        "ambient_type": ambient_type,
        "multiplicities": multiplicities,
        "embedding": embedding,
        "operator_enabled": operator_enabled,
        "lie_enabled": lie_enabled,
        "lie_family_id": lie_family_id,
        "lie_method": lie_method,
        "hall": hall,
        "route": route,
        "word": word,
        "channels": channels,
        "dynamic_class": dynamic_class,
        "entry_status": entry_status,
        "adjoint_closed": adjoint_closed,
        "mechanism_channels": mechanism_channels or [],
    }


def make_entry(old: dict, config: dict, *, entry_id: str | None = None,
               diagnostics: list[dict] | None = None,
               evidence_scripts: list[str] | None = None,
               notes: list[str] | None = None) -> dict:
    old_id = old["id"]
    cfg = config
    channels = copy.deepcopy(cfg["channels"])
    channel_ids = [item["id"] for item in channels]
    default_channel = channel_ids[0]
    old_diagnostics = old.get("diagnostics", [])
    typed_diagnostics = []
    for item in diagnostics if diagnostics is not None else old_diagnostics:
        row = copy.deepcopy(item)
        row["name"] = rewrite_text(row.get("name", "diagnostic"))
        row["value"] = rewrite_text(row.get("value"))
        raw_status = row.get("claim_status", "diagnostic")
        row["claim_status"] = (
            raw_status
            if raw_status in PUBLIC_STATUSES
            else STATUS.get(raw_status, "Computational Observation")
        )
        declared_channels = row.pop("channel_ids", None)
        legacy_channel = row.pop("channel_id", None)
        row["channel_ids"] = declared_channels or [legacy_channel or default_channel]
        row["channel_ids"] = [channel_id.lower() for channel_id in row["channel_ids"]]
        row["channel_ids"] = [
            channel_id for channel_id in row["channel_ids"] if channel_id in channel_ids
        ] or [default_channel]
        row["source"] = relocate(row.get("source", ""))
        row["qualification"] = row.pop(
            "qualification",
            "Finite source-addressed observation; no cross-carrier promotion is implied.",
        )
        typed_diagnostics.append(row)

    scripts = [
        relocate(path)
        for path in (
            evidence_scripts
            if evidence_scripts is not None
            else old.get("metadata", {}).get("evidence_scripts", [])
        )
    ]
    entry = {
        "id": entry_id or old_id,
        "species": copy.deepcopy(old["species"]),
        "sof_object": {
            "realization_status": old["sof_object"]["realization_status"],
            "finite_space": old["sof_object"]["finite_space"],
            "sectorization": {
                "type": cfg["sector_type"],
                "origin": cfg["sector_origin"],
                "sector_algebra": cfg["sector_algebra"],
                "sector_labels": cfg["sector_labels"],
                "description": old["sof_object"]["sectorization"]["description"],
            },
            "observable_family": {
                "id": cfg["family_id"],
                "semantics": cfg["family_semantics"],
                "labels": cfg["labels"],
                "adjoint_closed": cfg["adjoint_closed"],
            },
            "operator_system": {
                "status": cfg["operator_status"],
                "description": cfg["operator_description"],
            },
            "ambient_generated_algebra": {
                "status": cfg["ambient_status"],
                "type": cfg["ambient_type"],
                "representation_multiplicities": cfg["multiplicities"],
                "sector_embedding_data": cfg["embedding"],
            },
            "operator_branch_enabled": cfg["operator_enabled"],
            "lie_branch": {
                "enabled": cfg["lie_enabled"],
                "family_id": cfg["lie_family_id"],
                "registration_method": cfg["lie_method"],
                "hall_convention": cfg["hall"],
            },
            "route_word_semantics": {
                "route_semantics": cfg["route"],
                "word_semantics": cfg["word"],
            },
        },
        "observable_channels": channels,
        "dynamics": {
            "status": old["dynamics"]["status"],
            "variables": old["dynamics"]["variables"],
            "deformation_class": cfg["dynamic_class"],
            "mechanism_channels": cfg["mechanism_channels"],
            "description": old["dynamics"]["description"],
            "claim_status": cfg["entry_status"],
        },
        "diagnostics": typed_diagnostics,
        "metadata": {
            "claim_status": cfg["entry_status"],
            "paper": "Paper X",
            "evidence_scripts": scripts,
            "reports": old.get("metadata", {}).get("reports", []),
            "notes": notes or old.get("metadata", {}).get("notes", []),
            "predecessor_entry_ids": [old_id],
        },
    }
    return entry


def configs() -> dict[str, dict]:
    norm = ("norm", "1e-8", "finite projected-block audit")
    word = ("norm", "1e-8", "finite word-support audit")
    lie = ("norm", "1e-8", "finite commutator-support audit")
    return {
        "xu-ridge": object_config(
            sector_type="external_decomposition",
            sector_origin="row/null parameter decomposition",
            sector_algebra="two marked parameter subspaces",
            sector_labels={"kind": "row/null", "count": 2, "description": "data-visible and decay-controlled directions"},
            family_id="xu.parameter.rate.channels",
            family_semantics="parameter-space rate channels, not SOF operators",
            labels=["theta_parallel", "theta_perp"],
            operator_status="analogue",
            operator_description="No SOF operator alphabet is claimed for the external precedent.",
            ambient_status="analogue",
            ambient_type="parameter-space decomposition",
            multiplicities="not applicable",
            embedding="row-space/null-space split",
            operator_enabled=False,
            lie_enabled=False,
            lie_family_id=None,
            lie_method="not applicable",
            hall="not applicable",
            route="not applicable",
            word="not applicable",
            channels=[channel("parameter-rate", "analogue", "parameter decomposition", "locally derived row-space/null-space contraction-deficit ratio", claim_status="Computational Observation", threshold=("not_applicable", None, "external diagnostic conversion"))],
            dynamic_class="mechanism-separated parameter dynamics",
            entry_status="Computational Observation",
            mechanism_channels=["loss-driven gradient", "weight decay"],
        ),
        "mechanism-separated-control": object_config(
            sector_type="constructed",
            sector_origin="constructed three-sector witness",
            sector_algebra="span_C{Q_0,Q_1,Q_2}",
            sector_labels={"kind": "ordered constructed sectors", "count": 3, "description": "three fixed orthogonal sectors"},
            family_id="constructed.mechanism.proxy",
            family_semantics="continuous proxy channels with independently specified mechanisms",
            labels=["K0_grow", "K1_decay_displacement"],
            operator_status="declared",
            operator_description="Two constructed block channels; proxy values retain scale.",
            ambient_status="declared",
            ambient_type="finite block matrix algebra",
            multiplicities="three sector blocks of dimension two",
            embedding="fixed block-diagonal sector embedding",
            operator_enabled=True,
            lie_enabled=False,
            lie_family_id=None,
            lie_method="not registered",
            hall="not applicable",
            route="constructed block routing",
            word="not evaluated",
            channels=[
                channel("K0-grow", "proxy", "K0_grow", "gradient-driven direct-block growth", threshold=norm),
                channel("K1-decay", "proxy", "K1_decay_displacement", "normalized displacement of the regularization-driven slow decay", threshold=norm),
            ],
            dynamic_class="mechanism-separated training-coupled proxy dynamics",
            entry_status="Computational Certificate",
            mechanism_channels=["gradient", "regularization"],
        ),
        "engineered-near-threshold": object_config(
            sector_type="constructed",
            sector_origin="three coordinate sectors",
            sector_algebra="span_C{Q_i}",
            sector_labels={"kind": "coordinate sectors", "count": 3, "description": "three labelled coordinate projectors on C^3"},
            family_id="engineered.three_sector.skew",
            family_semantics="equally normalized skew-Hermitian trajectory with selected first-order direct and second-order simple-commutator block norms",
            labels=["X_12(t)", "X_23(t)"],
            operator_status="declared",
            operator_description="X_12(t)=t(E_12-E_21) and X_23(t)=t(E_23-E_32).",
            ambient_status="not_computed",
            ambient_type="finite matrix algebra, not decomposed",
            multiplicities="not computed",
            embedding="fixed sector embedding",
            operator_enabled=False,
            lie_enabled=True,
            lie_family_id="engineered.three_sector.X",
            lie_method="explicit two-generator skew-Hermitian family",
            hall="simple commutator evaluated; no Lie-depth claim",
            route="not evaluated",
            word="not evaluated",
            channels=[
                channel("K-dir", "proxy", "K_dir(t)=t", "selected direct block norm ||Q_1 X_12(t) Q_2||_F", claim_status="Theorem", threshold=("norm", "eta", "common first-crossing threshold with 0<eta<1"), pair_scope="off_diagonal"),
                channel("K-comm", "proxy", "K_comm(t)=t^2", "selected simple-commutator block norm ||Q_1[X_12(t),X_23(t)]Q_3||_F", claim_status="Theorem", threshold=("norm", "eta", "common first-crossing threshold with 0<eta<1"), pair_scope="off_diagonal"),
            ],
            dynamic_class="exact parameterized first-order/second-order threshold construction",
            entry_status="Theorem",
        ),
        "finite-spectral-triple": object_config(
            sector_type="dirac_block",
            sector_origin="block-diagonal finite Dirac operator",
            sector_algebra="block projectors from D",
            sector_labels={"kind": "Dirac blocks", "count": 3, "description": "finite Hilbert-space blocks"},
            family_id="ncg.finite_triple.algebra.one_forms",
            family_semantics="finite algebra action, Dirac operator, and one-form bridge blocks",
            labels=["A", "D", "one-form bridge"],
            operator_status="declared",
            operator_description="Finite algebra and one-form blocks are declared observables.",
            ambient_status="declared",
            ambient_type="finite represented algebra with block structure",
            multiplicities="three blocks of dimension two",
            embedding="block-diagonal D with off-block one-form bridges",
            operator_enabled=True,
            lie_enabled=False,
            lie_family_id=None,
            lie_method="not registered",
            hall="not applicable",
            route="block bridge composition",
            word="finite ordered products if declared",
            channels=[
                channel("dirac-distance", "analogue", "Connes distance", "central distance obstruction between disjoint blocks", claim_status="Computational Certificate", threshold=("not_applicable", None, "finite spectral-triple probe")),
                channel("T7-bridge", "operator", "T7-style bridge", "finite cross-block bridge support", threshold=norm),
            ],
            dynamic_class="static finite spectral-triple registration",
            entry_status="Computational Certificate",
        ),
        "control-kalman": object_config(
            sector_type="control_flag",
            sector_origin="Kalman controllability-flag increments",
            sector_algebra="span_C{Q_i} from flag increments",
            sector_labels={"kind": "controllability flag", "count": 3, "description": "successive state-space increments"},
            family_id="control.kalman.state_transition",
            family_semantics="state-transition and input-injection operators",
            labels=["A", "B"],
            operator_status="declared",
            operator_description="Finite state transition and input operators.",
            ambient_status="not_computed",
            ambient_type="finite matrix algebra, not decomposed",
            multiplicities="not computed",
            embedding="controllability-flag sector embedding",
            operator_enabled=True,
            lie_enabled=False,
            lie_family_id=None,
            lie_method="not registered",
            hall="not applicable",
            route="projected state-transition composition",
            word="ordered products of A/B; first word depth",
            channels=[
                channel("word-depth", "word", "W_d[Y], D_word[Y]", "direct, length-two, and first word-depth accessibility", claim_status="Computational Certificate", threshold=word, depth_convention="first nonzero ordered word", depth_cutoff=3, saturation_status="declared_cutoff"),
            ],
            dynamic_class="static control portability probe",
            entry_status="Computational Certificate",
        ),
        "pde-subdomain": object_config(
            sector_type="mesh",
            sector_origin="finite-difference subdomain/interface geometry",
            sector_algebra="span_C{Q_left,Q_interface,Q_right}",
            sector_labels={"kind": "mesh subdomains", "count": 3, "description": "left, interface, and right mesh sectors"},
            family_id="pde.finite_difference.laplacian",
            family_semantics="finite-difference Laplacian and interface coupling",
            labels=["Laplacian", "interface"],
            operator_status="declared",
            operator_description="Mesh operator and interface coupling family.",
            ambient_status="not_computed",
            ambient_type="finite sparse matrix algebra, not decomposed",
            multiplicities="not computed",
            embedding="left/interface/right mesh embedding",
            operator_enabled=True,
            lie_enabled=False,
            lie_family_id=None,
            lie_method="not registered",
            hall="not applicable",
            route="interface-mediated projected composition",
            word="ordered mesh walks; first word depth",
            channels=[
                channel("word-depth", "word", "W_d[Y], D_word[Y]", "direct, length-two, and left-to-right word depth", claim_status="Computational Certificate", threshold=word, depth_convention="first nonzero ordered word", depth_cutoff=4, saturation_status="declared_cutoff"),
            ],
            dynamic_class="static PDE discretization portability probe",
            entry_status="Computational Certificate",
        ),
        "combinatorial-coloring": object_config(
            sector_type="constraint_partition",
            sector_origin="graph-color constraint partition",
            sector_algebra="span_C{Q_color}",
            sector_labels={"kind": "color classes", "count": "declared by instance", "description": "vertex sectors from a coloring constraint"},
            family_id="combinatorial.coloring.adjacency",
            family_semantics="adjacency and color-class conflict support",
            labels=["adjacency", "color projectors"],
            operator_status="declared",
            operator_description="Finite adjacency with color-class projectors.",
            ambient_status="not_computed",
            ambient_type="finite graph operator algebra, not decomposed",
            multiplicities="not computed",
            embedding="vertex/color-class embedding",
            operator_enabled=True,
            lie_enabled=False,
            lie_family_id=None,
            lie_method="not registered",
            hall="not applicable",
            route="graph edge routing",
            word="not evaluated",
            channels=[
                channel("color-support", "operator", "inter-color support", "inter-color support and same-color conflict shadow", claim_status="Computational Certificate", threshold=word, pair_scope="declared_mixed"),
            ],
            dynamic_class="static combinatorial portability probe",
            entry_status="Computational Certificate",
        ),
        "barrier-option": object_config(
            sector_type="barrier",
            sector_origin="stopping/barrier partition of a log-price grid",
            sector_algebra="span_C{Q_below,Q_above}",
            sector_labels={"kind": "barrier regions", "count": 2, "description": "below-barrier and above-barrier grid sectors"},
            family_id="finance.barrier_option.finite_diffusion",
            family_semantics="finite-difference GBM generator and barrier crossing diagnostic",
            labels=["finite-difference generator", "absorbing CTMC"],
            operator_status="declared",
            operator_description="Finite diffusion generator and barrier-crossing operator.",
            ambient_status="not_computed",
            ambient_type="finite sparse diffusion algebra, not decomposed",
            multiplicities="not computed",
            embedding="below/above barrier grid embedding",
            operator_enabled=True,
            lie_enabled=False,
            lie_family_id=None,
            lie_method="not registered",
            hall="not applicable",
            route="cross-barrier projected transition",
            word="not evaluated",
            channels=[
                channel("cross-barrier", "operator", "direct cross-barrier support", "generator-block support across the barrier", threshold=("norm", "1e-10", "finite diffusion audit")),
                channel("first-hit", "analogue", "stochastic first-hitting time", "mean first-hit time of the absorbing CTMC", threshold=("not_applicable", None, "stochastic diagnostic")),
            ],
            dynamic_class="finite diffusion and stopping-time diagnostic",
            entry_status="Computational Certificate",
        ),
        "quantum-gates": object_config(
            sector_type="computational_basis",
            sector_origin="computational basis projectors",
            sector_algebra="diagonal computational-basis algebra",
            sector_labels={"kind": "basis states", "count": "2^n", "description": "one-dimensional computational-basis sectors"},
            family_id="quantum.gates.skew_log_generators",
            family_semantics="skew-Hermitian generators from logarithmic gate families",
            labels=["gate logarithms", "skew-Hermitian generators"],
            operator_status="declared",
            operator_description="Gate family is registered through skew-Hermitian generators.",
            ambient_status="not_computed",
            ambient_type="finite matrix algebra, not decomposed",
            multiplicities="not computed",
            embedding="computational-basis sector embedding",
            operator_enabled=False,
            lie_enabled=True,
            lie_family_id="quantum.gates.X",
            lie_method="skew-Hermitian part of a principal matrix logarithm, with fallback",
            hall="simple commutator and finite Lie-depth filtration; cutoff 4",
            route="not evaluated",
            word="not evaluated",
            channels=[
                channel("R1-Lie", "lie", "R_1^Lie", "direct support of registered gate generators", threshold=("norm", "1e-6", "quantum audit")),
                channel("R2-Lie", "lie", "R_2^Lie", "simple-commutator support", threshold=("norm", "1e-6", "quantum audit")),
                channel("D-Lie", "lie", "D_Lie", "first Lie depth with 999 retained as unreached-at-cutoff", threshold=("norm", "1e-6", "quantum audit"), depth_convention="Lie closure rounds", depth_cutoff=4, saturation_status="unreached_at_cutoff"),
            ],
            dynamic_class="gate-family variation; interpolation boundary",
            entry_status="Computational Certificate",
        ),
        "markov-systems": object_config(
            sector_type="state",
            sector_origin="coordinate state sectors",
            sector_algebra="diagonal state-space algebra",
            sector_labels={"kind": "states", "count": 3, "description": "coordinate sectors of the registered lazy directed cycle"},
            family_id="markov.transition.positive",
            family_semantics="column-stochastic transition operator with positive-word convention",
            labels=["P"],
            operator_status="declared",
            operator_description="The transition matrix itself is the declared operative letter.",
            ambient_status="not_computed",
            ambient_type="finite transition matrix algebra, not decomposed",
            multiplicities="not computed",
            embedding="state-basis sector embedding",
            operator_enabled=True,
            lie_enabled=False,
            lie_family_id=None,
            lie_method="not registered",
            hall="not applicable",
            route="not evaluated",
            word="positive powers of P; exact support-graph depth",
            channels=[
                channel("R1-op", "operator", "R_1[Y]", "direct support of the declared transition operator P", claim_status="Computational Certificate", threshold=("norm", "1e-12", "exact finite Markov audit")),
                channel("W2-word", "word", "W_2[Y]", "exact length-two support of P^2", claim_status="Computational Certificate", threshold=("norm", "1e-12", "exact finite Markov audit")),
                channel("D-word", "word", "D_word[Y]", "exact first positive-word depth certified by the nonnegative support graph", claim_status="Computational Certificate", threshold=("norm", "1e-12", "exact finite Markov audit"), depth_convention="first nonzero positive power", saturation_status="exact_saturated"),
            ],
            dynamic_class="static transition-operator registration",
            entry_status="Computational Certificate",
        ),
        "graph-systems": object_config(
            sector_type="graph",
            sector_origin="six path-graph vertex sectors",
            sector_algebra="diagonal vertex algebra",
            sector_labels={"kind": "vertices", "count": 6, "description": "coordinate sectors of the registered path graph P6"},
            family_id="graph.path6.adjacency",
            family_semantics="path-graph adjacency operator with positive-word convention",
            labels=["A"],
            adjoint_closed=True,
            operator_status="declared",
            operator_description="The adjacency matrix itself is the declared operative letter.",
            ambient_status="not_computed",
            ambient_type="finite graph operator algebra, not decomposed",
            multiplicities="not computed",
            embedding="vertex-basis sector embedding",
            operator_enabled=True,
            lie_enabled=False,
            lie_family_id=None,
            lie_method="not registered",
            hall="not applicable",
            route="not evaluated",
            word="positive powers of A; exact graph-distance filtration",
            channels=[
                channel("R1-op", "operator", "R_1[Y]", "direct adjacency support of A", claim_status="Computational Certificate", threshold=("norm", "1e-12", "exact finite graph audit")),
                channel("W2-word", "word", "W_2[Y]", "exact length-two support of A^2", claim_status="Computational Certificate", threshold=("norm", "1e-12", "exact finite graph audit")),
                channel("D-word", "word", "D_word[Y]", "exact graph-distance word depth certified through diameter five", claim_status="Computational Certificate", threshold=("norm", "1e-12", "exact finite graph audit"), depth_convention="first nonzero positive power", saturation_status="exact_saturated"),
            ],
            dynamic_class="static adjacency registration plus separate rewiring proxy boundary",
            entry_status="Computational Certificate",
        ),
        "yang-like-filtration": object_config(
            sector_type="filtration",
            sector_origin="state and filtration sectors",
            sector_algebra="registered filtration projectors",
            sector_labels={"kind": "filtration depth", "count": "declared by probe", "description": "state/coherence sectors for plateau summaries"},
            family_id="yang.state_mixing.plateau",
            family_semantics="state-filtered plateau observables",
            labels=["plateau profile", "state mixing parameter"],
            operator_status="analogue",
            operator_description="The plateau profile is an analogue observable, not an operator/Lie shadow.",
            ambient_status="analogue",
            ambient_type="finite state/coherence probe",
            multiplicities="not applicable",
            embedding="state/filtration embedding",
            operator_enabled=False,
            lie_enabled=False,
            lie_family_id=None,
            lie_method="not applicable",
            hall="not applicable",
            route="not applicable",
            word="not applicable",
            channels=[
                channel("plateau-profile", "analogue", "P_d(t)", "state-mixing plateau profile", threshold=("not_applicable", None, "registered analogue")),
            ],
            dynamic_class="archived state-mixing comparison interface",
            entry_status="Research Program",
        ),
        "neural-network-sof": object_config(
            sector_type="activation",
            sector_origin="activation-induced regions",
            sector_algebra="activation-pattern projectors",
            sector_labels={"kind": "activation / quantile sectors", "count": "activation-dependent", "description": "sectors induced by activation choice or training-state partition"},
            family_id="nn.training.activation.proxies",
            family_semantics="activation operators and continuous training-coupled norm proxies",
            labels=["activation operators", "K0", "K1", "K2"],
            operator_status="proxy",
            operator_description="Trainable weight-derived operators are audited through continuous proxies.",
            ambient_status="not_computed",
            ambient_type="finite hidden-state probe algebra, not decomposed",
            multiplicities="activation-dependent",
            embedding="activation-induced sector embedding",
            operator_enabled=True,
            lie_enabled=False,
            lie_family_id=None,
            lie_method="not registered; proxy observables only",
            hall="not applicable",
            route="not evaluated",
            word="not evaluated",
            channels=[
                channel("K0", "proxy", "K0", "continuous direct-block norm proxy", threshold=("norm", "not binary", "raw norm")),
                channel("K1", "proxy", "K1", "continuous simple-commutator norm proxy", threshold=("norm", "not binary", "raw norm")),
                channel("K2", "proxy", "K2", "continuous nested-commutator norm proxy", threshold=("norm", "not binary", "raw norm")),
            ],
            dynamic_class="training-coupled activation deformation",
            entry_status="Computational Observation",
            mechanism_channels=["gradient descent", "weight decay"],
        ),
    }


def make_custom(old: dict, config: dict, entry_id: str, name: str, category: str,
                description: str, diagnostics: list[dict], scripts: list[str],
                notes: list[str]) -> dict:
    entry = make_entry(
        old,
        config,
        entry_id=entry_id,
        diagnostics=diagnostics,
        evidence_scripts=scripts,
        notes=notes,
    )
    entry["species"] = {"name": name, "category": category, "description": description}
    return entry


def _build_legacy_candidate() -> dict:
    base = json.loads(V1_PATH.read_text(encoding="utf-8"))
    by_id = {entry["id"]: entry for entry in base["entries"]}
    cfg = configs()
    entries: list[dict] = []
    lie = ("norm", "1e-8", "finite commutator-support audit")

    rubik = by_id["rubik-qt-ht"]
    entries.append(make_custom(
        rubik, object_config(
            sector_type="joint_spectral",
            sector_origin="representation and joint spectral geometry",
            sector_algebra="span_C{Q_i} from QT/HT joint spectral projectors",
            sector_labels={"kind": "QT/HT joint-spectral sectors", "count": 9, "description": "numerically registered orthogonal sectors"},
            family_id="rubik.qt_ht.averages",
            family_semantics="QT and HT averaged represented operators",
            labels=["QT average", "HT average"],
            operator_status="declared",
            operator_description="A labelled represented-operator family for the two averages.",
            ambient_status="not_computed",
            ambient_type="finite represented algebra, concrete type retained",
            multiplicities="not computed in this entry",
            embedding="nine-dimensional marked joint-spectral sector arrangement",
            operator_enabled=True,
            lie_enabled=False,
            lie_family_id=None,
            lie_method="not registered",
            hall="not applicable",
            route="not evaluated",
            word="not evaluated",
            channels=[channel("joint-spectrum", "intrinsic", "joint spectral arrangement", "sector registration and collision quotient", claim_status="Computational Certificate", threshold=("not_applicable", None, "spectral registration"))],
            dynamic_class="static spectral registration",
            entry_status="Computational Certificate",
        ),
        "rubik-qt-ht-spectral",
        "Rubik QT/HT spectral realization",
        "represented spectral system",
        "Nine numerical QT/HT joint-spectral sectors.",
        [{"name": "joint-spectral sectors", "value": 9, "channel_ids": ["joint-spectrum"], "claim_status": "Computational Certificate", "source": "experiments/paper4/results/rubik_joint_spectrum_registration.observation.json", "qualification": "Numerical registration in the declared finite complex realization; not an exact spectrum theorem."}],
        [
            "experiments/paper4/validation/rubik_joint_spectrum_registration.py",
            "experiments/paper4/results/rubik_joint_spectrum_registration.observation.json",
        ],
        ["Split from the v1 Rubik row; this entry records spectral registration only."],
    ))
    entries.append(make_custom(
        rubik, object_config(
            sector_type="joint_spectral",
            sector_origin="representation and joint spectral geometry",
            sector_algebra="span_C{Q_i} from QT/HT joint spectral projectors",
            sector_labels={"kind": "QT/HT joint-spectral sectors", "count": 9, "description": "numerically registered orthogonal sectors"},
            family_id="rubik.face_turn.represented_operators",
            family_semantics="eighteen represented face-turn operators",
            labels=["face-turn representation matrices"],
            operator_status="declared",
            operator_description="The represented face-turn matrices retain generator labels.",
            ambient_status="not_computed",
            ambient_type="finite represented algebra, concrete type retained",
            multiplicities="not computed in this entry",
            embedding="nine marked QT/HT sectors inside the 228-dimensional representation",
            operator_enabled=True,
            lie_enabled=False,
            lie_family_id=None,
            lie_method="not registered",
            hall="not applicable",
            route="projected represented-operator products if declared",
            word="full ordered words in the eighteen face-turn labels if evaluated",
            channels=[
                channel("R1-operator", "operator", "R_1[Y]", "generator-labelled direct support of represented face turns", claim_status="Computational Observation", threshold=("norm", "1e-8", "represented operator audit")),
            ],
            dynamic_class="fixed-sector represented-operator audit",
            entry_status="Computational Observation",
        ),
        "rubik-face-turn-operator",
        "Rubik represented face-turn operators",
        "represented operator species",
        "Eighteen face-turn representation matrices on the nine QT/HT sectors.",
        [{"name": "direct support graph", "value": "10 undirected direct-support edges", "channel_ids": ["R1-operator"], "claim_status": "Computational Certificate", "source": "experiments/paper2/results/direct_transport.json", "qualification": "Finite numerical registration for represented face turns; support paths are not projected products."}],
        [
            "experiments/paper2/validation/transport_graph.py",
            "experiments/paper2/results/direct_transport.json",
        ],
        ["Separated from spectral registration; no Lie logarithm or depth is implied."],
    ))
    entries.append(make_custom(
        rubik, object_config(
            sector_type="joint_spectral",
            sector_origin="representation and joint spectral geometry",
            sector_algebra="span_C{Q_i} from QT/HT joint spectral projectors",
            sector_labels={"kind": "QT/HT joint-spectral sectors", "count": 9, "description": "numerically registered orthogonal sectors"},
            family_id="rubik.finite_order.logarithms",
            family_semantics="registered finite-order logarithm family",
            labels=["finite-order logarithm generators"],
            operator_status="declared",
            operator_description="Finite-order logarithm generators are separately registered from represented operators.",
            ambient_status="not_computed",
            ambient_type="finite represented algebra, concrete type retained",
            multiplicities="not computed in this entry",
            embedding="nine marked sectors in the normality-gated spectral chart",
            operator_enabled=False,
            lie_enabled=True,
            lie_family_id="rubik.finite_order.logarithms.X",
            lie_method="declared finite-order logarithm branch",
            hall="Paper V Hall/Lie convention; cutoff and saturation must be source-addressed",
            route="not evaluated",
            word="not evaluated",
            channels=[
                channel("R1-Lie", "lie", "R_1^Lie", "direct support of registered finite-order logarithms", threshold=lie),
                channel("R2-Lie", "lie", "R_2^Lie", "simple-commutator support", threshold=lie),
                channel("D-Lie", "lie", "D_Lie", "first reached Hall depth under a declared cutoff", threshold=lie, depth_convention="declared Hall/Lie filtration", depth_cutoff="source-addressed", saturation_status="not_attempted"),
            ],
            dynamic_class="normality-gated pointwise registration",
            entry_status="Computational Observation",
        ),
        "rubik-finite-order-log-lie",
        "Rubik finite-order logarithm family",
        "registered Lie carrier",
        "Finite-order logarithms used only on declared normal spectral charts.",
        [{"name": "pointwise Lie registration", "value": "normality-gated samples only", "channel_ids": ["R1-Lie", "R2-Lie", "D-Lie"], "claim_status": "Computational Observation", "source": "experiments/paper6/validation/normal_spectral_chart_audit.py", "qualification": "No coherent moving projector field or dynamic depth theorem is supplied."}],
        ["experiments/paper6/validation/normal_spectral_chart_audit.py"],
        ["Paper VI supplies a pointwise interface, not a completed moving-field certificate."],
    ))
    entries.append(make_custom(
        rubik, object_config(
            sector_type="joint_spectral",
            sector_origin="representation and joint spectral geometry",
            sector_algebra="span_C{Q_i} from QT/HT joint spectral projectors",
            sector_labels={"kind": "QT/HT joint-spectral sectors", "count": 9, "description": "numerically registered orthogonal sectors"},
            family_id="rubik.face_turn.antihermitian_parts",
            family_semantics="anti-Hermitian parts of the eighteen represented face turns",
            labels=["anti-Hermitian face-turn parts"],
            operator_status="declared",
            operator_description="The anti-Hermitian parts are retained as a distinct labelled family.",
            ambient_status="not_computed",
            ambient_type="finite represented algebra, concrete type retained",
            multiplicities="not computed in this entry",
            embedding="nine marked QT/HT sectors",
            operator_enabled=False,
            lie_enabled=True,
            lie_family_id="rubik.face_turn.antihermitian_parts.X",
            lie_method="X=(rho-rho*)/2, explicitly declared anti-Hermitian family",
            hall="simple commutators; depth is not inferred from low-order counts",
            route="selected routed products with explicit intermediate sectors",
            word="not evaluated",
            channels=[
                channel("R1-Lie", "lie", "R_1^Lie", "direct support of anti-Hermitian face-turn parts", threshold=lie),
                channel("R2-Lie", "lie", "R_2^Lie", "simple-commutator support", threshold=lie),
                channel("route-incidence", "route", "Route_2[Y]", "bridge-level image-kernel incidence of selected routed products", threshold=lie),
            ],
            dynamic_class="static low-order Lie/route audit",
            entry_status="Computational Certificate",
        ),
        "rubik-antihermitian-low-order",
        "Rubik anti-Hermitian low-order audit",
        "typed low-order mechanism species",
        "Typed anti-Hermitian direct, commutator, and routed-incidence audit on QT/HT sectors.",
        [
            {"name": "commutator cancellations", "value": 288, "channel_ids": ["R1-Lie", "R2-Lie"], "claim_status": "Computational Certificate", "source": "experiments/paper10/rubik_wild_type34_audit.py", "qualification": "Finite census for the explicitly declared anti-Hermitian family; not a universal mechanism count."},
            {"name": "routed image-kernel incidences", "value": 528, "channel_ids": ["R1-Lie", "route-incidence"], "claim_status": "Computational Certificate", "source": "experiments/paper10/rubik_wild_type34_audit.py", "qualification": "Bridge-level incidence count for selected routed products; not a global completion theorem."},
        ],
        ["experiments/paper10/rubik_wild_type34_audit.py"],
        ["The historical Type III/IV names are retired. Counts are retained under explicit carriers."],
    ))

    synthetic = by_id["synthetic-type-iii-iv"]
    entries.append(make_custom(
        synthetic, object_config(
            sector_type="constructed",
            sector_origin="constructed block-sector witness",
            sector_algebra="span_C{Q_i}",
            sector_labels={"kind": "constructed sectors", "count": "declared by control", "description": "finite block sectors"},
            family_id="constructed.commutator.cancellation",
            family_semantics="declared skew family with commutator cancellation control",
            labels=["X generators", "commutators"],
            operator_status="declared",
            operator_description="Constructed generator family with explicit cancellation terms.",
            ambient_status="declared",
            ambient_type="finite block matrix algebra",
            multiplicities="declared by control",
            embedding="constructed sector embedding",
            operator_enabled=False,
            lie_enabled=True,
            lie_family_id="constructed.cancellation.X",
            lie_method="explicit constructed skew generators",
            hall="simple commutator only; no full-depth promotion",
            route="not evaluated",
            word="not evaluated",
            channels=[channel("R2-Lie", "lie", "R_2^Lie", "constructed commutator-cancellation control", threshold=lie)],
            dynamic_class="static constructed mechanism control",
            entry_status="Computational Certificate",
        ),
        "constructed-commutator-cancellation",
        "Constructed commutator-cancellation control",
        "constructed mechanism reference",
        "Constructed finite control for low-order commutator cancellation.",
        [{"name": "cancellation control", "value": "constructed positive and negative controls", "channel_ids": ["R2-Lie"], "claim_status": "Computational Certificate", "source": "experiments/paper5/validation/path_commutator_cancellation.py", "qualification": "Mechanism control only; not a naturally occurring species."}],
        ["experiments/paper5/validation/path_commutator_cancellation.py"],
        ["Constructed reference, not observed in a wild system."],
    ))
    entries.append(make_custom(
        synthetic, object_config(
            sector_type="constructed",
            sector_origin="constructed block-sector witness",
            sector_algebra="span_C{Q_i}",
            sector_labels={"kind": "constructed sectors", "count": "declared by control", "description": "finite block sectors"},
            family_id="constructed.route.incidence",
            family_semantics="declared routed factors with image-kernel incidence control",
            labels=["A factors", "B factors", "routed products"],
            operator_status="declared",
            operator_description="Constructed rectangular factors for a selected route.",
            ambient_status="declared",
            ambient_type="rectangular finite matrix spaces",
            multiplicities="declared by control",
            embedding="constructed sector embedding",
            operator_enabled=True,
            lie_enabled=False,
            lie_family_id=None,
            lie_method="not registered",
            hall="not applicable",
            route="selected one-step/two-step routed products",
            word="not evaluated",
            channels=[channel("route-incidence", "route", "Route_2[Y]", "constructed image-kernel incidence control", threshold=lie)],
            dynamic_class="static constructed incidence control",
            entry_status="Computational Certificate",
        ),
        "constructed-route-incidence",
        "Constructed routed-incidence control",
        "constructed mechanism reference",
        "Constructed finite control for image-kernel incidence.",
        [{"name": "incidence control", "value": "constructed image-kernel incidence witness", "channel_ids": ["route-incidence"], "claim_status": "Computational Certificate", "source": "experiments/paper7/results/projected_composition_audit.json", "qualification": "Constructed routed-product witness from the versioned Paper VII result record; genericity, full-word survival, commutator survival, and completion are not inferred."}],
        ["experiments/paper7/validation/rank_protected_bridge_audit.py"],
        ["Constructed reference, not observed in a wild system."],
    ))

    for old_id, config in cfg.items():
        if old_id in {"xu-ridge", "mechanism-separated-control", "engineered-near-threshold", "finite-spectral-triple", "control-kalman", "pde-subdomain", "combinatorial-coloring", "barrier-option", "quantum-gates", "markov-systems", "graph-systems", "yang-like-filtration", "neural-network-sof"}:
            diagnostics = None
            evidence_scripts = None
            notes = None
            if old_id == "engineered-near-threshold":
                diagnostics = [
                    {
                        "name": "exact direct/commutator response-time ratio",
                        "value": "tau_eta(K_dir)=eta, tau_eta(K_comm)=sqrt(eta), ratio=eta^(-1/2) for 0<eta<1",
                        "channel_ids": ["K-dir", "K-comm"],
                        "claim_status": "Theorem",
                        "source": "experiments/paper9/rate_hierarchy.py",
                        "qualification": (
                            "Exact finite construction relative to the declared "
                            "trajectory, equal generator normalization, "
                            "Frobenius norm, and threshold policy; not an "
                            "intrinsic rate invariant, Boolean support, or "
                            "Lie depth."
                        ),
                    }
                ]
            if old_id == "barrier-option":
                diagnostics = [
                    {
                        "name": "direct cross-barrier support",
                        "value": "R_1[Y]=75.0%",
                        "channel_ids": ["cross-barrier"],
                        "claim_status": "Computational Observation",
                        "source": "experiments/paper10/barrier_option_sof.py",
                        "qualification": (
                            "Operator direct support only; the Lie/Hall branch "
                            "is not registered for this entry."
                        ),
                    },
                    {
                        "name": "mean first-hit time",
                        "value": 6.5915,
                        "channel_ids": ["first-hit"],
                        "claim_status": "Computational Observation",
                        "source": "experiments/paper10/barrier_option_sof.py",
                        "qualification": (
                            "Native stochastic first-hitting diagnostic; not "
                            "operator-word or Lie/Hall depth."
                        ),
                    },
                ]
            if old_id == "yang-like-filtration":
                diagnostics = [
                    {
                        "name": "archived plateau provenance",
                        "value": "not admitted as current typed wall evidence",
                        "channel_ids": ["plateau-profile"],
                        "claim_status": "Research Program",
                        "source": "experiments/paper9/archive/state_mixing_fft.py",
                        "qualification": (
                            "Historical state-mixing comparison only; the "
                            "archived script does not support an active typed "
                            "wall or rate claim."
                        ),
                    }
                ]
                evidence_scripts = [
                    "experiments/paper9/archive/state_mixing_fft.py",
                    "experiments/paper10/tau_quantum_graph_yang.py",
                ]
                notes = [
                    "The state-mixing script is retired provenance.",
                    "No active typed wall or rate claim is registered.",
                ]
            entries.append(
                make_entry(
                    by_id[old_id],
                    config,
                    diagnostics=diagnostics,
                    evidence_scripts=evidence_scripts,
                    notes=notes,
                )
            )

    return {
        "registry_schema_version": "2.0",
        "snapshot": {
            "id": "paper10-typed-v2.0",
            "title": "Paper X Typed SOF Registry Migration Snapshot",
            "release_date": "2026-07-28",
            "source": "papers/paper10/Paper X.md",
            "predecessor": {
                "id": "paper10-release-v1.0",
                "schema_version": "1.0",
            },
            "entry_count": len(entries),
            "scope_note": (
                "Typed migration candidate. The five-layer Registry is retained, "
                "but each observable channel now declares its carrier, threshold, "
                "depth convention, cutoff, saturation status, and claim status. "
                "The v1.0 snapshot is immutable."
            ),
            "migration_note": (
                "Rubik spectral, represented-operator, finite-order logarithm, "
                "and anti-Hermitian families are separated. Historical Type III/IV "
                "names are replaced by carrier-qualified cancellation and incidence."
            ),
        },
        "entries": entries,
    }


CAPABILITY_IDS = (
    "sectorization",
    "operator_carrier",
    "operator_system",
    "route_carrier",
    "word_carrier",
    "positive_associative_closure",
    "observable_star_closure",
    "sector_enriched_star_closure",
    "lie_hall_carrier",
    "deformation_chart",
    "proxy_diagnostic",
    "diagnostic_analogue",
)

ANALOGUE_ENTRIES = {
    "constructed-route-incidence",
    "xu-ridge",
    "yang-like-filtration",
    "neural-network-sof",
}

DIMENSIONS = {
    "rubik-qt-ht-spectral": 228,
    "rubik-face-turn-operator": 228,
    "rubik-finite-order-log-lie": 228,
    "rubik-antihermitian-low-order": 228,
    "constructed-commutator-cancellation": 24,
    "mechanism-separated-control": 6,
    "engineered-near-threshold": 3,
    "finite-spectral-triple": 6,
    "control-kalman": 3,
    "pde-subdomain": 7,
    "combinatorial-coloring": 6,
    "barrier-option": 31,
    "quantum-gates": 4,
    "markov-systems": 3,
    "graph-systems": 6,
}

SECTOR_LABELS = {
    "rubik-qt-ht-spectral": [f"S{i}" for i in range(9)],
    "rubik-face-turn-operator": [f"S{i}" for i in range(9)],
    "rubik-finite-order-log-lie": [f"S{i}" for i in range(9)],
    "rubik-antihermitian-low-order": [f"S{i}" for i in range(9)],
    "constructed-commutator-cancellation": [f"S{i}" for i in range(10)],
    "mechanism-separated-control": ["Q0", "Q1", "Q2"],
    "engineered-near-threshold": ["Q1", "Q2", "Q3"],
    "finite-spectral-triple": ["L", "M", "R"],
    "control-kalman": ["K0", "K1", "K2"],
    "pde-subdomain": ["left", "interface", "right"],
    "combinatorial-coloring": ["color0", "color1", "color2"],
    "barrier-option": ["below", "above"],
    "quantum-gates": ["00", "01", "10", "11"],
    "markov-systems": ["state0", "state1", "state2"],
    "graph-systems": [f"v{i}" for i in range(6)],
}

SOURCE_MAP_STATUS = {
    "rubik-qt-ht-spectral": "represented_realization",
    "rubik-face-turn-operator": "represented_realization",
    "rubik-finite-order-log-lie": "represented_realization",
    "rubik-antihermitian-low-order": "represented_realization",
    "constructed-commutator-cancellation": "constructed_realization",
    "constructed-route-incidence": "analogue_mapping",
    "xu-ridge": "analogue_mapping",
    "mechanism-separated-control": "constructed_realization",
    "engineered-near-threshold": "constructed_realization",
    "finite-spectral-triple": "constructed_realization",
    "control-kalman": "adapter_realization",
    "pde-subdomain": "adapter_realization",
    "combinatorial-coloring": "adapter_realization",
    "barrier-option": "adapter_realization",
    "quantum-gates": "adapter_realization",
    "markov-systems": "adapter_realization",
    "graph-systems": "adapter_realization",
    "yang-like-filtration": "proxy_only",
    "neural-network-sof": "proxy_only",
}

EVIDENCE_ROLE = {
    "constructed-commutator-cancellation": "negative_control",
    "constructed-route-incidence": "negative_control",
    "xu-ridge": "external_precedent",
    "mechanism-separated-control": "proxy_evidence",
    "engineered-near-threshold": "proxy_evidence",
    "markov-systems": "active_evidence",
    "graph-systems": "active_evidence",
    "yang-like-filtration": "proxy_evidence",
    "neural-network-sof": "proxy_evidence",
}

TYPED_CHART_ENTRIES = {
    "mechanism-separated-control",
    "engineered-near-threshold",
}

RESPONSE_FINDINGS = {
    "rate ratio",
    "ordered mechanism times",
    "exact direct/commutator response-time ratio",
    "mean first-hit time",
    "rate hierarchy boundary",
    "state-mixing proxy boundary",
    "ordered proxy times",
}

FINDING_KINDS = {
    "joint-spectral sectors": "dimension",
    "direct support graph": "dimension",
    "pointwise Lie registration": "status_only",
    "commutator cancellations": "dimension",
    "routed image-kernel incidences": "dimension",
    "cancellation control": "status_only",
    "incidence control": "status_only",
    "rate ratio": "response_time",
    "ordered mechanism times": "response_time",
    "exact direct/commutator response-time ratio": "response_time",
    "Dirac-projector commutator": "residual",
    "ordered T7-style bridges": "dimension",
    "Kalman ranks": "rank",
    "terminal word depth": "depth",
    "left-to-right depth": "depth",
    "inter-color directed edges": "dimension",
    "same-color conflicts": "dimension",
    "direct cross-barrier support": "boolean_support",
    "mean first-hit time": "response_time",
    "positive-word support audit": "boolean_support",
    "exact positive-word depth": "depth",
    "Pauli repair": "dimension",
    "Clifford+CNOT repair": "dimension",
    "connected/frozen contrast": "status_only",
    "rate hierarchy boundary": "response_time",
    "state-mixing proxy boundary": "response_time",
    "ordered proxy times": "response_time",
}


def _slug(value: str) -> str:
    value = re.sub(r"[^a-z0-9._-]+", "-", value.lower()).strip("-._")
    return value or "record"


def _digest(path: Path) -> dict[str, str]:
    return {"algorithm": "sha256", "value": hashlib.sha256(path.read_bytes()).hexdigest()}


def _registry_content_digest(payload: dict) -> dict[str, str]:
    canonical = dict(payload)
    canonical.pop("census_certificate", None)
    encoded = json.dumps(
        canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {"algorithm": "sha256", "value": hashlib.sha256(encoded).hexdigest()}


def _census_summary(entries: list[dict]) -> dict:
    claim_statuses = (
        "Theorem",
        "Computational Certificate",
        "Computational Observation",
        "Research Program",
    )
    findings = [finding for entry in entries for finding in entry["findings"]]
    return {
        "entry_count": len(entries),
        "strict_sof_count": sum(
            entry["record_kind"] == "strict_sof" for entry in entries
        ),
        "diagnostic_analogue_count": sum(
            entry["record_kind"] == "diagnostic_analogue" for entry in entries
        ),
        "capability_counts": {
            capability_id: sum(
                entry["capabilities"][capability_id]["availability"] == "DECLARED"
                for entry in entries
            )
            for capability_id in CAPABILITY_IDS
        },
        "finding_count": len(findings),
        "finding_claim_status_counts": {
            status: sum(finding["claim_status"] == status for finding in findings)
            for status in claim_statuses
        },
    }


class ArtifactRegistry:
    def __init__(self) -> None:
        self.records: list[dict] = []
        self._by_key: dict[tuple[str, str], str] = {}

    def add(
        self,
        relative_path: str,
        *,
        role: str = "script",
        generated_by_artifact_ids: list[str] | None = None,
        schema_version: str | None = None,
    ) -> str:
        relative_path = relative_path.replace("\\", "/")
        key = (relative_path, role)
        if key in self._by_key:
            return self._by_key[key]
        path = ROOT / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"Registry evidence path does not exist: {relative_path}")
        suffix = hashlib.sha256(f"{relative_path}|{role}".encode()).hexdigest()[:10]
        artifact_id = f"artifact.{_slug(Path(relative_path).stem)}.{suffix}"
        historical = "archive" in Path(relative_path).parts
        media_type = mimetypes.guess_type(relative_path)[0] or "application/octet-stream"
        producers = list(dict.fromkeys(generated_by_artifact_ids or []))
        if role == "source-data" and not producers:
            raise ValueError(f"Source-data artifact lacks producer: {relative_path}")
        if role == "source-data" and schema_version is None and path.suffix == ".json":
            schema_version = json.loads(path.read_text(encoding="utf-8")).get("schema")
        self.records.append({
            "id": artifact_id,
            "uri": relative_path,
            "digest": _digest(path),
            "media_type": media_type,
            "schema_version": schema_version,
            "role": role,
            "evidence_scope": "historical_provenance" if historical else "active",
            "generated_by_artifact_ids": producers,
        })
        self._by_key[key] = artifact_id
        return artifact_id


def _capability(available: bool, description: str, **configuration: object) -> dict:
    result = {
        "availability": "DECLARED" if available else "NOT_DECLARED",
        "description": description,
    }
    if available:
        result["configuration"] = configuration or {"registration": "Registry migration"}
    return result


def _normalize_legacy_rows(rows: list[dict]) -> None:
    """Repair known v1-to-v2 typing and channel-link defects explicitly."""

    by_id = {row["id"]: row for row in rows}

    xu = by_id["xu-ridge"]
    xu_finding = xu["diagnostics"][0]
    xu_finding["value"] = "749.6x"
    xu_finding["claim_status"] = "Computational Observation"
    xu_finding["qualification"] = (
        "Locally derived contraction-deficit ratio for the declared seeded ridge "
        "diagnostic; it is not source-reported and is not a half-response-time ratio."
    )
    xu_finding["extraction_context"] = {
        "source_locator": (
            "experiments/cross_ref/grokking_rate_separation.py: theoretical "
            "contraction rates"
        ),
        "extraction_formula": (
            "[eta(lambda_min^+ + lambda)]/[eta lambda]"
        ),
        "parameter_values": {
            "m": 400,
            "n": 50,
            "eta": 0.2,
            "lambda": 0.0001,
            "seed": 42,
        },
        "response_convention": (
            "ratio of per-step contraction deficits, not threshold-crossing time"
        ),
        "derivation_kind": "locally_derived",
    }

    paper6 = by_id["rubik-finite-order-log-lie"]
    paper6["observable_channels"] = [paper6["observable_channels"][0]]
    paper6["diagnostics"][0]["channel_ids"] = ["r1-lie"]
    paper6["diagnostics"][0]["value"] = "normality-gated pointwise R_1^Lie samples only"

    by_id["mechanism-separated-control"]["diagnostics"][0]["channel_ids"] = [
        "k0-grow", "k1-decay"
    ]
    mechanism = by_id["mechanism-separated-control"]["diagnostics"][0]
    mechanism["value"] = (
        "tau_1/2(K0_grow)=30 < tau_1/2(K1_decay_displacement)=1380"
    )
    mechanism["qualification"] = (
        "Constructed three-sector block-norm realization under one normalized "
        "displacement and half-response policy; distinct mechanisms interpret the "
        "channels, while ordered calibration supplies the rate inequality."
    )
    spectral = by_id["finite-spectral-triple"]
    spectral["observable_channels"][0]["branch"] = "proxy"
    spectral["observable_channels"][0]["carrier"] = "central Connes-distance diagnostic"
    spectral["diagnostics"][1]["channel_ids"] = ["t7-bridge"]

    control = by_id["control-kalman"]
    control["observable_channels"].insert(0, {
        "id": "kalman-flag-rank",
        "branch": "intrinsic",
        "carrier": "controllability flag",
        "semantics": "successive ranks of the declared Kalman flag",
        "threshold_policy": {"kind": "rank", "value": None, "scope": "exact finite audit"},
        "depth_convention": "not applicable",
        "depth_cutoff": None,
        "saturation_status": "not_applicable",
        "pair_scope": "not_applicable",
        "claim_status": "Computational Observation",
    })
    control["diagnostics"][0]["channel_ids"] = ["kalman-flag-rank"]

    quantum = by_id["quantum-gates"]
    for diagnostic in quantum["diagnostics"]:
        diagnostic["channel_ids"] = ["r1-lie", "d-lie"]
        diagnostic["qualification"] = (
            "Static off-diagonal ordered-pair count in the two-qubit computational-"
            "basis realization. A repaired pair has aggregate R_1^Lie=0 and is "
            "reached by the truncated Lie/Hall filtration through cutoff 4; the "
            "reported value is a count, not a depth."
        )
        diagnostic["repair_registration"] = {
            "repair_kind": "static_filtration_repair",
            "carrier": "Lie/Hall",
            "source_layers": ["R_1^Lie"],
            "target_layer": "D_Lie^(<=4)",
            "temporal_scope": "static",
            "predicate": (
                "aggregate R_1^Lie(i,j)=0 and D_Lie^(<=4)(i,j) is reached"
            ),
            "cutoff": 4,
            "pair_scope": "off_diagonal_ordered",
            "count_denominator": 12,
            "saturation_status": "truncated_only",
        }

    barrier = by_id["barrier-option"]
    barrier["observable_channels"][1]["branch"] = "proxy"
    barrier["observable_channels"][1]["carrier"] = "mean first-hitting diagnostic"

    markov = by_id["markov-systems"]
    markov["diagnostics"] = [
        {
            "name": "positive-word support audit",
            "value": "R_1[Y]=3/6 and W_2[Y]=6/6 off-diagonal ordered pairs",
            "channel_ids": ["r1-op", "w2-word"],
            "claim_status": "Computational Certificate",
            "source": "experiments/paper10/markov_graph_sof.py",
            "qualification": (
                "Exact finite audit of the declared three-state transition "
                "operator; no Lie/Hall carrier is registered."
            ),
        },
        {
            "name": "exact positive-word depth",
            "value": "maximum off-diagonal D_word[Y]=2; no unreachable ordered pair",
            "channel_ids": ["d-word"],
            "claim_status": "Computational Certificate",
            "source": "experiments/paper10/markov_graph_sof.py",
            "qualification": (
                "Entrywise nonnegativity and finite support-graph shortest paths "
                "certify exact positive-word depth for this matrix."
            ),
        },
    ]
    markov["metadata"]["evidence_scripts"] = [
        "experiments/paper10/markov_graph_sof.py"
    ]

    graph_proxy_channels = [
        {
            "id": "k0", "branch": "proxy", "carrier": "K_0",
            "semantics": "maximum off-diagonal direct-block norm during edge rewiring",
            "threshold_policy": {"kind": "half_response", "value": 0.5, "scope": "declared discrete trajectory"},
            "depth_convention": "not applicable", "depth_cutoff": None,
            "saturation_status": "not_applicable", "pair_scope": "off_diagonal",
            "claim_status": "Computational Observation",
        },
        {
            "id": "k1", "branch": "proxy", "carrier": "K_1",
            "semantics": "maximum off-diagonal simple-commutator norm during edge rewiring",
            "threshold_policy": {"kind": "half_response", "value": 0.5, "scope": "declared discrete trajectory"},
            "depth_convention": "not applicable", "depth_cutoff": None,
            "saturation_status": "not_applicable", "pair_scope": "off_diagonal",
            "claim_status": "Computational Observation",
        },
    ]
    graph = by_id["graph-systems"]
    graph["observable_channels"].extend(copy.deepcopy(graph_proxy_channels))
    graph["diagnostics"] = [
        {
            "name": "positive-word support audit",
            "value": "R_1[Y]=10/30 and W_2[Y]=8/30 off-diagonal ordered pairs",
            "channel_ids": ["r1-op", "w2-word"],
            "claim_status": "Computational Certificate",
            "source": "experiments/paper10/markov_graph_sof.py",
            "qualification": (
                "Exact finite audit of the declared P6 adjacency operator; "
                "no Lie/Hall carrier is registered."
            ),
        },
        {
            "name": "exact positive-word depth",
            "value": "maximum off-diagonal D_word[Y]=5; no unreachable ordered pair",
            "channel_ids": ["d-word"],
            "claim_status": "Computational Certificate",
            "source": "experiments/paper10/markov_graph_sof.py",
            "qualification": (
                "Entrywise nonnegativity and the diameter-five shortest-path "
                "certificate establish exact positive-word depth for P6."
            ),
        },
        {
            "name": "rate hierarchy boundary",
            "value": "edge-rewiring K_0/K_1 response is degenerate or unordered",
            "channel_ids": ["k0", "k1"],
            "claim_status": "Computational Observation",
            "source": "experiments/paper10/tau_quantum_graph_yang.py",
            "qualification": (
                "Discrete edge addition is a proxy boundary probe, not a smooth "
                "typed wall or depth trajectory."
            ),
        },
    ]
    graph["metadata"]["evidence_scripts"] = [
        "experiments/paper10/markov_graph_sof.py",
        "experiments/paper10/tau_quantum_graph_yang.py",
    ]

    yang = by_id["yang-like-filtration"]
    yang["observable_channels"] = copy.deepcopy(graph_proxy_channels)
    yang["diagnostics"] = [{
        "name": "state-mixing proxy boundary",
        "value": "state-mixing K_0/K_1 response is degenerate",
        "channel_ids": ["k0", "k1"],
        "claim_status": "Computational Observation",
        "source": "experiments/paper10/tau_quantum_graph_yang.py",
        "qualification": "The active record is a continuous proxy boundary; the retired plateau script is historical provenance only.",
    }]
    yang["metadata"]["evidence_scripts"] = ["experiments/paper10/tau_quantum_graph_yang.py"]

    nn = by_id["neural-network-sof"]
    nn["diagnostics"][0]["channel_ids"] = ["k0", "k1", "k2"]

    route = by_id["constructed-route-incidence"]
    route["observable_channels"] = [{
        "id": "incidence-geometry",
        "branch": "analogue",
        "carrier": "matrix-pair incidence geometry",
        "semantics": "rank-stratified image-kernel incidence descriptor",
        "threshold_policy": {"kind": "not_applicable", "value": None, "scope": "exact dimension formulas"},
        "depth_convention": "not applicable", "depth_cutoff": None,
        "saturation_status": "not_applicable", "pair_scope": "not_applicable",
        "claim_status": "Computational Certificate",
    }]
    route["diagnostics"][0]["channel_ids"] = ["incidence-geometry"]

    paper10 = json.loads(PAPER10_RESULT_PATH.read_text(encoding="utf-8"))

    def bind_result(
        entry_id: str,
        source_scripts: list[str],
        result_path: str = PAPER10_RESULT_RELATIVE,
    ) -> dict:
        entry = by_id[entry_id]
        evidence = entry["metadata"].setdefault("evidence_scripts", [])
        for path in [*source_scripts, result_path]:
            if path not in evidence:
                evidence.append(path)
        for diagnostic in entry["diagnostics"]:
            diagnostic["source"] = result_path
        return entry

    response = paper10["response_control"]
    mechanism = bind_result(
        "mechanism-separated-control",
        ["experiments/paper9/calibrated_response.py"],
    )
    mechanism["diagnostics"][0]["value"] = (
        f"tau_1/2(K0_grow)={response['tau_fast']} < "
        f"tau_1/2(K1_decay_displacement)={response['tau_slow']}"
    )

    rubik_result = paper10["rubik_low_order"]
    rubik = bind_result(
        "rubik-antihermitian-low-order",
        ["experiments/paper10/rubik_wild_type34_audit.py"],
    )
    rubik["diagnostics"][0]["value"] = rubik_result[
        "commutator_cancellation_count"
    ]
    rubik["diagnostics"][1]["value"] = rubik_result[
        "routed_image_kernel_incidence_count"
    ]

    legacy_imports = json.loads(LEGACY_IMPORT_PATH.read_text(encoding="utf-8"))
    cancellation_result = legacy_imports["records"][
        "constructed_commutator_cancellation"
    ]
    cancellation = bind_result(
        "constructed-commutator-cancellation",
        ["experiments/paper5/validation/path_commutator_cancellation.py"],
        LEGACY_IMPORT_RELATIVE,
    )
    cancellation["diagnostics"][0]["value"] = cancellation_result["value"]

    quantum_result = legacy_imports["records"]["quantum_static_repair"]
    quantum = bind_result(
        "quantum-gates",
        ["experiments/quantum/quantum_accessibility_universality.py"],
        LEGACY_IMPORT_RELATIVE,
    )
    quantum["diagnostics"][0]["value"] = quantum_result[
        "pauli_repair_count"
    ]
    quantum["diagnostics"][1]["value"] = quantum_result[
        "clifford_cnot_repair_count"
    ]
    for diagnostic in quantum["diagnostics"]:
        diagnostic["carrier_registration"] = {
            "carrier_id": quantum_result["carrier_id"],
            "generator_registration": quantum_result["generator_registration"],
            "hall_filtration": quantum_result["hall_filtration"],
            "cutoff": quantum_result["cutoff"],
            "cutoff_semantics": quantum_result["cutoff_semantics"],
            "zero_tolerance": quantum_result["zero_tolerance"],
            "pair_scope": quantum_result["pair_scope"],
        }

    spectral_result = paper10["finite_spectral_triple"]
    spectral = bind_result(
        "finite-spectral-triple",
        ["experiments/paper10/ncg_spectral_triple_sof.py"],
    )
    spectral["diagnostics"][0]["value"] = (
        "max norm zero" if spectral_result["central_lipschitz_zero"] else "nonzero"
    )
    spectral["diagnostics"][1]["value"] = spectral_result[
        "ordered_routed_bridge_count"
    ]

    portability = paper10["portability"]
    control = bind_result(
        "control-kalman",
        ["experiments/paper10/control_pde_combinatorial_sof.py"],
    )
    control["diagnostics"][0]["value"] = ",".join(
        str(value) for value in portability["control"]["kalman_ranks"]
    )
    control["diagnostics"][1]["value"] = portability["control"][
        "terminal_word_depth"
    ]
    pde = bind_result(
        "pde-subdomain",
        ["experiments/paper10/control_pde_combinatorial_sof.py"],
    )
    pde["diagnostics"][0]["value"] = portability["pde"][
        "left_to_right_word_depth"
    ]
    combinatorial = bind_result(
        "combinatorial-coloring",
        ["experiments/paper10/control_pde_combinatorial_sof.py"],
    )
    combinatorial["diagnostics"][0]["value"] = portability["combinatorial"][
        "inter_color_edges"
    ]
    combinatorial["diagnostics"][1]["value"] = portability["combinatorial"][
        "same_color_conflicts"
    ]

    barrier_result = paper10["barrier_option"]
    barrier = bind_result(
        "barrier-option",
        ["experiments/paper10/barrier_option_sof.py"],
    )
    barrier["diagnostics"][0]["value"] = (
        f"R_1[Y]={barrier_result['labelled_direct_support_pct']:.1f}%"
    )
    barrier["diagnostics"][1]["value"] = round(
        barrier_result["mean_first_hit_time"], 4
    )

    markov_graph_static = paper10["markov_graph_static"]
    markov = bind_result(
        "markov-systems",
        ["experiments/paper10/markov_graph_sof.py"],
    )
    markov_static = markov_graph_static["markov"]["findings"]
    markov["diagnostics"][0]["value"] = (
        f"R_1[Y]={markov_static['direct_support_count']}/"
        f"{markov_static['direct_support_possible']} and "
        f"W_2[Y]={markov_static['word_two_support_count']}/"
        f"{markov_static['direct_support_possible']} off-diagonal ordered pairs"
    )
    markov["diagnostics"][1]["value"] = (
        f"maximum off-diagonal D_word[Y]="
        f"{markov_static['maximum_finite_word_depth']}; "
        f"{markov_static['unreachable_off_diagonal_count']} unreachable ordered pairs"
    )

    graph = bind_result(
        "graph-systems",
        [
            "experiments/paper10/markov_graph_sof.py",
            "experiments/paper10/tau_quantum_graph_yang.py",
        ],
    )
    graph_static = markov_graph_static["graph"]["findings"]
    graph["diagnostics"][0]["value"] = (
        f"R_1[Y]={graph_static['direct_support_count']}/"
        f"{graph_static['direct_support_possible']} and "
        f"W_2[Y]={graph_static['word_two_support_count']}/"
        f"{graph_static['direct_support_possible']} off-diagonal ordered pairs"
    )
    graph["diagnostics"][1]["value"] = (
        f"maximum off-diagonal D_word[Y]="
        f"{graph_static['maximum_finite_word_depth']}; "
        f"{graph_static['unreachable_off_diagonal_count']} unreachable ordered pairs"
    )

    proxy_boundaries = paper10["proxy_boundaries"]
    graph["diagnostics"][2]["value"] = (
        "edge-rewiring K_0/K_1 response is "
        f"{proxy_boundaries['graph']['status'].lower()}"
    )
    yang = bind_result(
        "yang-like-filtration",
        ["experiments/paper10/tau_quantum_graph_yang.py"],
    )
    yang["diagnostics"][0]["value"] = (
        "state-mixing K_0/K_1 response is "
        f"{proxy_boundaries['yang_like']['status'].lower()}"
    )


def _channel_shape(old_channel: dict) -> tuple[str, str, str]:
    branch = old_channel["branch"]
    channel_id = old_channel["id"].lower()
    if branch == "intrinsic":
        return "intrinsic", "sector_data", "carrier.sector"
    if branch == "operator":
        return "operator", "labelled_direct_support", "carrier.operator"
    if branch == "route":
        return "route", "routed_support", "carrier.route"
    if branch == "word":
        field = (
            "depth"
            if channel_id.startswith("d-") or "depth" in channel_id
            else "word_support"
        )
        return "word", field, "carrier.word"
    if branch == "lie":
        if channel_id.startswith("d-"):
            return "hall", "depth", "carrier.hall"
        field = "commutator_support" if "r2" in channel_id else "labelled_direct_support"
        return "lie", field, "carrier.lie"
    if branch == "proxy":
        return "proxy", "continuous_proxy", "carrier.proxy"
    if branch == "analogue":
        return "analogue", "analogue_descriptor", "carrier.analogue"
    raise ValueError(f"Unsupported legacy branch: {branch}")


def _result_pair(status: str, *, analogue: bool) -> tuple[str, str | None]:
    if status == "Theorem" and not analogue:
        return "ESTABLISHED", "Theorem"
    if status == "Computational Certificate":
        return "CERTIFIED", status
    if status == "Research Program":
        return "DECLARED", status
    return "OBSERVED", "Computational Observation"


def _compile_entry(old: dict, artifacts: ArtifactRegistry) -> dict:
    entry_id = old["id"]
    analogue = entry_id in ANALOGUE_ENTRIES
    historical = EVIDENCE_ROLE.get(entry_id) == "historical_provenance"
    source_paths = list(old["metadata"].get("evidence_scripts", []))
    source_paths.extend(item.get("source") for item in old["diagnostics"] if item.get("source"))
    source_paths = list(dict.fromkeys(source_paths))
    if not historical:
        source_paths = [path for path in source_paths if "archive" not in Path(path).parts]
    source_artifacts = {
        path: artifacts.add(path)
        for path in source_paths
        if path not in RESULT_PRODUCERS
    }
    for path in source_paths:
        producer_path = RESULT_PRODUCERS.get(path)
        if producer_path is None:
            continue
        producer_id = source_artifacts.get(producer_path)
        if producer_id is None:
            producer_id = artifacts.add(producer_path)
            source_artifacts[producer_path] = producer_id
        source_artifacts[path] = artifacts.add(
            path,
            role="source-data",
            generated_by_artifact_ids=[producer_id],
        )
    if not source_artifacts:
        raise ValueError(f"{entry_id}: no admissible source artifact")
    primary_artifact_id = next(iter(source_artifacts.values()))

    channels = []
    channel_to_carrier: dict[str, str] = {}
    for old_channel in old["observable_channels"]:
        branch, field_kind, carrier_id = _channel_shape(old_channel)
        channel_id = f"channel.{_slug(old_channel['id'])}"
        depth_cutoff = old_channel.get("depth_cutoff")
        if field_kind == "depth":
            declared_saturation = old_channel.get("saturation_status")
            if declared_saturation in {"exact_saturated", "computationally_saturated"}:
                if depth_cutoff is not None:
                    raise ValueError(
                        f"{entry_id}/{channel_id}: exact depth cannot carry a cutoff"
                    )
                depth_mode = "exact"
                saturation_status = declared_saturation
            else:
                if not isinstance(depth_cutoff, int):
                    raise ValueError(
                        f"{entry_id}/{channel_id}: truncated depth requires an integer cutoff"
                    )
                depth_mode = "truncated"
                saturation_status = "cutoff_declared"
        else:
            depth_mode = "not_applicable"
            depth_cutoff = None
            saturation_status = "not_applicable"
        policy_ids = []
        threshold = old_channel.get("threshold_policy", {})
        if threshold.get("kind") != "not_applicable":
            policy_ids.extend(["policy.threshold", "policy.norm"])
        if depth_mode == "exact":
            policy_ids.append("policy.saturation")
        channels.append({
            "id": channel_id,
            "branch": branch,
            "carrier_id": carrier_id,
            "field_kind": field_kind,
            "semantics": old_channel["semantics"],
            "depth_mode": depth_mode,
            "depth_cutoff": depth_cutoff,
            "saturation_status": saturation_status,
            "pair_scope": {
                "off_diagonal": "off_diagonal",
                "not_applicable": "not_applicable",
            }.get(old_channel.get("pair_scope"), "declared_mixed"),
            "semantic_convention_ids": [] if analogue else ["convention.direction"],
            "run_policy_ids": policy_ids + (
                ["policy.cutoff"] if depth_mode == "truncated" else []
            ),
        })
        channel_to_carrier[old_channel["id"].lower()] = carrier_id

    carrier_kinds = {channel["carrier_id"]: channel["branch"] for channel in channels}
    if analogue:
        carrier_kinds.setdefault("carrier.analogue", "analogue")
    else:
        carrier_kinds.setdefault("carrier.sector", "intrinsic")
        carrier_kinds.setdefault("carrier.operator", "operator")
    if old["sof_object"]["lie_branch"]["enabled"]:
        carrier_kinds.setdefault("carrier.lie", "lie")

    declared_capabilities = set()
    if analogue:
        declared_capabilities.add("diagnostic_analogue")
    else:
        declared_capabilities.update({"sectorization", "operator_carrier"})
    capability_for_branch = {
        "route": "route_carrier",
        "word": "word_carrier",
        "lie": "lie_hall_carrier",
        "hall": "lie_hall_carrier",
        "proxy": "proxy_diagnostic",
        "analogue": "diagnostic_analogue",
    }
    declared_capabilities.update(
        capability_for_branch[branch]
        for branch in carrier_kinds.values()
        if branch in capability_for_branch
    )
    if entry_id in TYPED_CHART_ENTRIES:
        declared_capabilities.add("deformation_chart")
        carrier_kinds["carrier.deformation"] = "deformation"

    capabilities = {
        capability_id: _capability(
            capability_id in declared_capabilities,
            (
                f"{capability_id} is explicitly registered for this row."
                if capability_id in declared_capabilities
                else f"{capability_id} is not declared for this row."
            ),
            source="v1 migration with explicit typed registration",
        )
        for capability_id in CAPABILITY_IDS
    }

    objects = []
    if analogue:
        objects.append({
            "id": "object.analogue", "kind": "analogue_descriptor",
            "label": old["sof_object"]["observable_family"]["id"],
            "carrier_id": "carrier.analogue" if "carrier.analogue" in carrier_kinds else "carrier.proxy",
            "artifact_ids": list(source_artifacts.values()),
            "data": {"semantics": old["sof_object"]["observable_family"]["semantics"]},
            "data_schema_ref": None,
        })
        core = None
        analogue_core = {
            "descriptors": [{
                "id": f"descriptor.{_slug(channel['id'].removeprefix('channel.'))}",
                "kind": "proxy" if channel["branch"] == "proxy" else "other",
                "semantics": channel["semantics"],
            } for channel in channels],
            "analogue_mapping": {
                "id": f"mapping.{entry_id}",
                "source_terms": old["sof_object"]["observable_family"]["labels"],
                "target_analogues": [channel["semantics"] for channel in channels],
                "limitations": "This row records structural diagnostics and cannot instantiate a strict SOF theorem.",
            },
            "source_provenance_artifact_ids": list(source_artifacts.values()),
            "negative_sof_boundary": "No complete finite complex projector realization and operative alphabet are asserted by this aggregate row.",
        }
        semantic_conventions = []
    else:
        objects.extend([
            {
                "id": "object.sectors", "kind": "sector_projector", "label": "{Q_i}",
                "carrier_id": "carrier.sector", "artifact_ids": list(source_artifacts.values()),
                "data": {"labels": SECTOR_LABELS[entry_id]}, "data_schema_ref": None,
            },
            {
                "id": "object.alphabet", "kind": "operative_alphabet",
                "label": old["sof_object"]["observable_family"]["id"],
                "carrier_id": "carrier.operator", "artifact_ids": list(source_artifacts.values()),
                "data": {"semantics": old["sof_object"]["observable_family"]["semantics"]},
                "data_schema_ref": None,
            },
        ])
        core = {
            "space": {"dimension": DIMENSIONS[entry_id], "scalar_field": "complex"},
            "sectorization": {
                "origin": old["sof_object"]["sectorization"]["origin"],
                "complete": True,
                "labels": SECTOR_LABELS[entry_id],
                "projector_data_status": "computationally_certified",
                "projector_object_ids": ["object.sectors"],
                "provenance_artifact_ids": list(source_artifacts.values()),
            },
            "operative_alphabet": {
                "id": "object.alphabet",
                "labels": old["sof_object"]["observable_family"]["labels"],
                "word_convention": "positive",
                "adjoint_closed": old["sof_object"]["observable_family"].get(
                    "adjoint_closed", False
                ),
                "projectors_are_letters": False,
                "provenance_artifact_ids": list(source_artifacts.values()),
            },
        }
        analogue_core = None
        semantic_conventions = [
            {"id": "convention.direction", "kind": "direction_convention", "specification": {"direction": "j-to-i"}},
            {"id": "convention.word", "kind": "word_convention", "specification": {"letters": "declared operative alphabet", "closure": "positive"}},
            {"id": "convention.projectors", "kind": "projector_letter_policy", "specification": {"projectors_are_letters": False}},
        ]
        if "lie_hall_carrier" in declared_capabilities:
            hall_specification = {
                "registration": old["sof_object"]["lie_branch"]["hall_convention"]
            }
            carrier_registration = next(
                (
                    item["carrier_registration"]
                    for item in old["diagnostics"]
                    if item.get("carrier_registration")
                ),
                None,
            )
            if carrier_registration is not None:
                hall_specification.update(carrier_registration)
            semantic_conventions.append({
                "id": "convention.hall", "kind": "hall_convention",
                "specification": hall_specification,
            })

    branch_object = {
        "route": ("object.route", "routed_space", "routed products"),
        "word": ("object.word", "word_space", "positive-word filtration"),
        "lie": ("object.lie", "lie_generator", "declared Lie generators"),
        "hall": ("object.hall", "hall_filtration", "declared Hall filtration"),
        "proxy": ("object.proxy", "proxy_observable", "continuous proxy observables"),
        "deformation": ("object.deformation", "deformation_chart", "typed deformation chart"),
    }
    for carrier_id, branch in carrier_kinds.items():
        if branch in branch_object:
            object_id, object_kind, label = branch_object[branch]
            if not any(item["id"] == object_id for item in objects):
                objects.append({
                    "id": object_id, "kind": object_kind, "label": label,
                    "carrier_id": carrier_id, "artifact_ids": list(source_artifacts.values()),
                    "data": {}, "data_schema_ref": None,
                })

    response_present = any(item["name"] in RESPONSE_FINDINGS for item in old["diagnostics"])
    if response_present:
        trajectory_carrier = (
            "carrier.deformation" if "carrier.deformation" in carrier_kinds
            else "carrier.proxy" if "carrier.proxy" in carrier_kinds
            else "carrier.analogue"
        )
        objects.append({
            "id": "object.trajectory", "kind": "trajectory", "label": "declared diagnostic trajectory",
            "carrier_id": trajectory_carrier, "artifact_ids": list(source_artifacts.values()),
            "data": {"selected_observable_ids": ["object.analogue" if analogue else "object.alphabet"]},
            "data_schema_ref": None,
        })

    carrier_object_ids: dict[str, list[str]] = {}
    for obj in objects:
        carrier_object_ids.setdefault(obj["carrier_id"], []).append(obj["id"])
    carrier_kind = {
        "intrinsic": "sector", "operator": "operator", "route": "route",
        "word": "word", "lie": "lie", "hall": "hall", "proxy": "proxy",
        "analogue": "analogue", "deformation": "deformation",
    }
    carriers = []
    for carrier_id, branch in carrier_kinds.items():
        capability_id = {
            "intrinsic": "sectorization", "operator": "operator_carrier",
            "route": "route_carrier", "word": "word_carrier",
            "lie": "lie_hall_carrier", "hall": "lie_hall_carrier",
            "proxy": "proxy_diagnostic", "analogue": "diagnostic_analogue",
            "deformation": "deformation_chart",
        }[branch]
        carriers.append({
            "id": carrier_id,
            "kind": carrier_kind[branch],
            "capability_id": capability_id,
            "semantics": f"Typed {branch} carrier for {old['species']['name']}.",
            "object_ids": carrier_object_ids.get(carrier_id, ["object.analogue"]),
            "semantic_convention_ids": [] if analogue else (
                ["convention.hall"] if branch in {"lie", "hall"} else ["convention.direction"]
            ),
        })

    run_policies = []
    if any("policy.threshold" in channel["run_policy_ids"] for channel in channels):
        run_policies.extend([
            {"id": "policy.threshold", "kind": "threshold", "specification": {"value": "source-declared", "scope": "carrier-qualified finite audit"}},
            {"id": "policy.norm", "kind": "norm", "specification": {"name": "source-declared matrix norm"}},
        ])
    if any("policy.cutoff" in channel["run_policy_ids"] for channel in channels):
        cutoffs = sorted({channel["depth_cutoff"] for channel in channels if channel["depth_cutoff"]})
        if len(cutoffs) != 1:
            raise ValueError(f"{entry_id}: one Registry row cannot share mismatched depth cutoffs")
        run_policies.append({"id": "policy.cutoff", "kind": "cutoff", "specification": {"max_depth": cutoffs[0]}})
    if entry_id == "quantum-gates":
        registration = next(
            item["carrier_registration"]
            for item in old["diagnostics"]
            if item.get("carrier_registration")
        )
        for policy in run_policies:
            if policy["id"] == "policy.threshold":
                policy["specification"] = {
                    "kind": "absolute block-norm zero tolerance",
                    "value": registration["zero_tolerance"],
                    "pair_scope": registration["pair_scope"],
                }
            elif policy["id"] == "policy.cutoff":
                policy["specification"] = {
                    "max_depth": registration["cutoff"],
                    "semantics": registration["cutoff_semantics"],
                    "tested_depth_indices": registration["hall_filtration"][
                        "tested_depth_indices"
                    ],
                }
    if any("policy.saturation" in channel["run_policy_ids"] for channel in channels):
        run_policies.append({
            "id": "policy.saturation",
            "kind": "saturation_audit",
            "specification": {
                "method": (
                    "entrywise-nonnegative support graph and finite "
                    "shortest-path comparison"
                )
            },
        })
    response_policy_ids = [
        "policy.trajectory", "policy.normalization", "policy.response-norm",
        "policy.response-threshold", "policy.response-time",
    ]
    if response_present:
        run_policies.extend([
            {"id": "policy.trajectory", "kind": "trajectory_parameterization", "specification": {"parameter": old["dynamics"]["variables"] or ["declared audit parameter"]}},
            {"id": "policy.normalization", "kind": "observable_normalization", "specification": {"rule": "source-declared"}},
            {"id": "policy.response-norm", "kind": "norm", "specification": {"name": "source-declared"}},
            {"id": "policy.response-threshold", "kind": "threshold", "specification": {"rule": "source-declared response or hitting policy"}},
            {"id": "policy.response-time", "kind": "response_time", "specification": {"definition": "source-declared first crossing, half response, or mean first hit"}},
        ])
        if entry_id == "mechanism-separated-control":
            next(
                item for item in run_policies if item["id"] == "policy.normalization"
            )["specification"] = {
                "rule": (
                    "normalized displacement |K(t)-K(0)|/|K(infinity)-K(0)|"
                )
            }
            next(
                item for item in run_policies
                if item["id"] == "policy.response-threshold"
            )["specification"] = {
                "rule": "first normalized displacement crossing at 1/2"
            }
            next(
                item for item in run_policies if item["id"] == "policy.response-time"
            )["specification"] = {
                "definition": "half-response time under normalized displacement"
            }

    proof_artifact_id = None
    if any(item.get("claim_status") == "Theorem" for item in old["diagnostics"]) and not analogue:
        paper9_theorems = {
            "engineered-near-threshold",
            "mechanism-separated-control",
        }
        proof_path = (
            "papers/paper9/Paper IX.md"
            if entry_id in paper9_theorems
            else "papers/paper10/Paper X.md"
        )
        proof_artifact_id = artifacts.add(proof_path, role="proof-reference")

    findings = []
    certificates = []
    claims = []
    channel_by_id = {channel["id"]: channel for channel in channels}
    for index, diagnostic in enumerate(old["diagnostics"], start=1):
        finding_id = f"finding.{_slug(diagnostic['name'])}.{index}"
        raw_channel_ids = [f"channel.{_slug(item)}" for item in diagnostic["channel_ids"]]
        unknown = sorted(set(raw_channel_ids) - set(channel_by_id))
        if unknown:
            raise ValueError(f"{entry_id}/{finding_id}: unknown channels {unknown}")
        finding_carriers = list(dict.fromkeys(channel_by_id[item]["carrier_id"] for item in raw_channel_ids))
        source_path = diagnostic.get("source")
        artifact_id = source_artifacts.get(source_path, primary_artifact_id)
        result_state, claim_status = _result_pair(diagnostic["claim_status"], analogue=analogue)
        evidence_artifact_ids = [artifact_id]
        if claim_status == "Theorem" and proof_artifact_id:
            evidence_artifact_ids.append(proof_artifact_id)
        finding_kind = FINDING_KINDS.get(diagnostic["name"], "status_only")
        exact_depth_channel = next(
            (
                channel_by_id[item]
                for item in raw_channel_ids
                if channel_by_id[item]["field_kind"] == "depth"
                and channel_by_id[item]["depth_mode"] == "exact"
            ),
            None,
        )
        certificate_ids = []
        if claim_status == "Computational Certificate":
            certificate_id = f"certificate.{_slug(diagnostic['name'])}.{index}"
            certificates.append({
                "id": certificate_id,
                "kind": "saturation" if exact_depth_channel else "computation",
                "validator_id": f"validator.{entry_id}.{index}", "status": "PASS",
                "scope": diagnostic["qualification"], "artifact_ids": [artifact_id],
            })
            certificate_ids.append(certificate_id)
        policy_ids = list(dict.fromkeys(
            policy_id
            for channel_id in raw_channel_ids
            for policy_id in channel_by_id[channel_id]["run_policy_ids"]
        ))
        if finding_kind == "response_time":
            policy_ids = list(dict.fromkeys(policy_ids + response_policy_ids))
        finding = {
            "id": finding_id,
            "kind": finding_kind,
            "comparison_scope": "cross_channel" if len(raw_channel_ids) > 1 else "single_channel",
            "channel_ids": raw_channel_ids,
            "carrier_ids": finding_carriers,
            "subject_object_ids": list(dict.fromkeys(
                object_id for carrier_id in finding_carriers for object_id in carrier_object_ids[carrier_id]
            )),
            "value": diagnostic["value"],
            "unit": None,
            "result_state": result_state,
            "claim_status": claim_status,
            "semantic_convention_ids": [],
            "run_policy_ids": policy_ids,
            "certificate_ids": certificate_ids,
            "artifact_ids": evidence_artifact_ids,
            "qualification": diagnostic["qualification"],
        }
        if finding_kind == "depth":
            depth_channel = next(channel_by_id[item] for item in raw_channel_ids if channel_by_id[item]["field_kind"] == "depth")
            finding["depth_registration"] = {
                "mode": depth_channel["depth_mode"],
                "cutoff": depth_channel["depth_cutoff"],
                "saturation_certificate_id": (
                    certificate_ids[0]
                    if depth_channel["depth_mode"] == "exact"
                    else None
                ),
            }
        if diagnostic.get("repair_registration"):
            finding["repair_registration"] = diagnostic["repair_registration"]
        if diagnostic.get("extraction_context"):
            finding["extraction_context"] = diagnostic["extraction_context"]
        findings.append(finding)
        capability_ids = list(dict.fromkeys(
            next(carrier["capability_id"] for carrier in carriers if carrier["id"] == carrier_id)
            for carrier_id in finding_carriers
        ))
        claims.append({
            "id": f"claim.{_slug(diagnostic['name'])}.{index}",
            "statement": f"{diagnostic['name']}: {diagnostic['value']}.",
            "result_state": result_state,
            "claim_status": claim_status,
            "capability_ids": capability_ids,
            "carrier_ids": finding_carriers,
            "object_ids": finding["subject_object_ids"],
            "finding_ids": [finding_id],
            "semantic_convention_ids": [],
            "run_policy_ids": policy_ids,
            "hypotheses": ["Only the declared carrier, realization, and policies are in scope."],
            "certificate_ids": certificate_ids,
            "artifact_ids": evidence_artifact_ids,
            "scope": old["species"]["description"],
            "negative_boundary": diagnostic["qualification"],
        })

    if entry_id in TYPED_CHART_ENTRIES:
        objects.append({
            "id": "object.comparison", "kind": "comparison_map", "label": "fixed-coordinate comparison map",
            "carrier_id": "carrier.deformation", "artifact_ids": list(source_artifacts.values()),
            "data": {"continuity": "continuous matrix entries in fixed coordinates"}, "data_schema_ref": None,
        })
        carrier_object_ids["carrier.deformation"].append("object.comparison")
        dynamics_status = "typed_deformation_chart"
        comparison_map_id = "object.comparison"
    elif historical:
        dynamics_status = "historical_provenance"
        comparison_map_id = None
    elif analogue and response_present:
        dynamics_status = "analogue_trajectory"
        comparison_map_id = None
    elif old["dynamics"]["status"] == "static":
        dynamics_status = "static"
        comparison_map_id = None
    else:
        dynamics_status = "candidate_deformation"
        comparison_map_id = None

    trajectory_id = "object.trajectory" if response_present else None
    dynamics = {
        "status": dynamics_status,
        "description": old["dynamics"]["description"],
        "variables": old["dynamics"]["variables"],
        "fixed_labels": True if dynamics_status == "typed_deformation_chart" else None,
        "fixed_conventions": True if dynamics_status == "typed_deformation_chart" else None,
        "continuity": "continuous matrix entries in the declared trivialization" if dynamics_status == "typed_deformation_chart" else None,
        "comparison_map_object_id": comparison_map_id,
        "trajectory_object_id": trajectory_id,
        "semantic_convention_ids": [],
        "run_policy_ids": response_policy_ids if response_present else [],
    }

    entry_artifact_ids = list(dict.fromkeys(
        list(source_artifacts.values()) + ([proof_artifact_id] if proof_artifact_id else [])
    ))
    return {
        "id": entry_id,
        "species": old["species"],
        "record_kind": "diagnostic_analogue" if analogue else "strict_sof",
        "source_map_status": SOURCE_MAP_STATUS[entry_id],
        "evidence_role": EVIDENCE_ROLE.get(entry_id, "active_evidence"),
        "capabilities": capabilities,
        "strict_core": core,
        "analogue_core": analogue_core,
        "objects": objects,
        "semantic_conventions": semantic_conventions,
        "run_policies": run_policies,
        "carriers": carriers,
        "observable_channels": channels,
        "dynamics": dynamics,
        "artifact_ids": entry_artifact_ids,
        "certificates": certificates,
        "findings": findings,
        "claims": claims,
        "derivations": [],
        "contract_refs": {"capability_manifest": None, "typed_sof_ir": None},
        "metadata": {
            "paper": "Paper X",
            "notes": old["metadata"].get("notes", []),
            "predecessor_entry_ids": old["metadata"].get("predecessor_entry_ids", []),
        },
    }


def _migration_assertions(payload: dict) -> None:
    entries = {entry["id"]: entry for entry in payload["entries"]}
    artifacts = {artifact["id"]: artifact for artifact in payload["artifacts"]}
    assert len(entries) == 19
    assert entries["rubik-finite-order-log-lie"]["observable_channels"][0]["id"] == "channel.r1-lie"
    assert len(entries["rubik-finite-order-log-lie"]["observable_channels"]) == 1
    expected_links = {
        "mechanism-separated-control": {"channel.k0-grow", "channel.k1-decay"},
        "engineered-near-threshold": {"channel.k-dir", "channel.k-comm"},
        "neural-network-sof": {"channel.k0", "channel.k1", "channel.k2"},
    }
    for entry_id, expected in expected_links.items():
        assert set(entries[entry_id]["findings"][0]["channel_ids"]) == expected
    assert entries["finite-spectral-triple"]["findings"][1]["channel_ids"] == ["channel.t7-bridge"]
    assert entries["control-kalman"]["findings"][0]["channel_ids"] == ["channel.kalman-flag-rank"]
    incidence_finding = entries["constructed-route-incidence"]["findings"][0]
    incidence_data = [
        artifacts[artifact_id]
        for artifact_id in incidence_finding["artifact_ids"]
        if artifacts[artifact_id]["role"] == "source-data"
    ]
    assert [artifact["uri"] for artifact in incidence_data] == [
        "experiments/paper7/results/projected_composition_audit.json"
    ]
    producer_ids = incidence_data[0]["generated_by_artifact_ids"]
    assert [artifacts[artifact_id]["uri"] for artifact_id in producer_ids] == [
        "experiments/paper7/validation/rank_protected_bridge_audit.py"
    ]
    paper10_finding = entries["mechanism-separated-control"]["findings"][0]
    paper10_data = [
        artifacts[artifact_id]
        for artifact_id in paper10_finding["artifact_ids"]
        if artifacts[artifact_id]["role"] == "source-data"
    ]
    assert [artifact["uri"] for artifact in paper10_data] == [
        PAPER10_RESULT_RELATIVE
    ]
    paper10_producers = paper10_data[0]["generated_by_artifact_ids"]
    assert [artifacts[artifact_id]["uri"] for artifact_id in paper10_producers] == [
        "experiments/paper10/validation/build_results.py"
    ]
    for finding in entries["quantum-gates"]["findings"]:
        assert set(finding["channel_ids"]) == {"channel.r1-lie", "channel.d-lie"}
    for entry_id, maximum_depth in (("markov-systems", 2), ("graph-systems", 5)):
        entry = entries[entry_id]
        assert entry["capabilities"]["operator_carrier"]["availability"] == "DECLARED"
        assert entry["capabilities"]["word_carrier"]["availability"] == "DECLARED"
        assert entry["capabilities"]["lie_hall_carrier"]["availability"] == "NOT_DECLARED"
        depth_channel = next(
            channel
            for channel in entry["observable_channels"]
            if channel["id"] == "channel.d-word"
        )
        assert depth_channel["depth_mode"] == "exact"
        assert depth_channel["depth_cutoff"] is None
        assert depth_channel["saturation_status"] == "exact_saturated"
        depth_finding = next(
            finding
            for finding in entry["findings"]
            if finding["kind"] == "depth"
        )
        assert f"D_word[Y]={maximum_depth}" in depth_finding["value"]
        saturation_id = depth_finding["depth_registration"][
            "saturation_certificate_id"
        ]
        assert saturation_id in depth_finding["certificate_ids"]
        assert next(
            certificate
            for certificate in entry["certificates"]
            if certificate["id"] == saturation_id
        )["kind"] == "saturation"
        data_artifacts = [
            artifacts[artifact_id]
            for artifact_id in depth_finding["artifact_ids"]
            if artifacts[artifact_id]["role"] == "source-data"
        ]
        assert [artifact["uri"] for artifact in data_artifacts] == [
            PAPER10_RESULT_RELATIVE
        ]
    for entry_id in ("graph-systems", "yang-like-filtration"):
        used_uris = {
            artifact["uri"] for artifact in payload["artifacts"]
            if artifact["id"] in entries[entry_id]["artifact_ids"]
        }
        assert all("archive" not in Path(uri).parts for uri in used_uris)
    quantum_repairs = entries["quantum-gates"]["findings"]
    assert all(
        finding["repair_registration"]["repair_kind"]
        == "static_filtration_repair"
        for finding in quantum_repairs
    )
    xu = entries["xu-ridge"]["findings"][0]
    assert xu["value"] == "749.6x"
    assert xu["extraction_context"]["derivation_kind"] == "locally_derived"


def build() -> dict:
    legacy = _build_legacy_candidate()
    _normalize_legacy_rows(legacy["entries"])
    artifacts = ArtifactRegistry()
    entries = [_compile_entry(entry, artifacts) for entry in legacy["entries"]]
    schema_artifact_id = artifacts.add(
        "schemas/registry/v2.0.schema.json", role="source-input"
    )
    validator_artifact_id = artifacts.add(
        "registry/validate_snapshot.py", role="script"
    )
    migrator_artifact_id = artifacts.add(
        "registry/migrate_v1_to_v2.py", role="script"
    )
    v1_artifact_id = artifacts.add(
        "registry/paper10-release-v1.0.registry.json", role="source-input"
    )
    payload = {
        "registry_schema_version": "2.0",
        "sof_semantics_version": "2.0",
        "snapshot": {
            "id": "paper10-typed-v2.0",
            "title": "Paper X Capability-Aware Typed SOF Registry",
            "release_date": "2026-07-30",
            "status": "release",
            "source": "papers/paper10/Paper X.md",
            "predecessor": {"id": "paper10-release-v1.0", "schema_version": "1.0"},
            "entry_count": len(entries),
            "scope_note": (
                "Frozen Registry v2.0 release snapshot. Each row declares strict-SOF "
                "or diagnostic-analogue admission, capabilities, typed carriers, "
                "policies, structured findings, evidence, and negative boundaries. "
                "Registry v1.0 remains immutable."
            ),
        },
        "census_certificate": {},
        "artifacts": artifacts.records,
        "entries": entries,
    }
    payload["census_certificate"] = {
        "snapshot_id": payload["snapshot"]["id"],
        "content_digest": _registry_content_digest(payload),
        "digest_scope": (
            "canonical JSON of the complete Registry payload excluding "
            "census_certificate"
        ),
        "schema_version": "2.0",
        "schema_artifact_id": schema_artifact_id,
        "validator_id": "registry.validate_snapshot",
        "validator_version": VALIDATOR_VERSION,
        "validation_status": "PASS",
        "query_version": "registry-census-v1",
        "summary": _census_summary(entries),
        "artifact_ids": [
            schema_artifact_id,
            validator_artifact_id,
            migrator_artifact_id,
            v1_artifact_id,
        ],
    }
    _migration_assertions(payload)
    return payload


def main() -> None:
    payload = build()
    V2_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {V2_PATH} ({len(payload['entries'])} entries)")


if __name__ == "__main__":
    main()
