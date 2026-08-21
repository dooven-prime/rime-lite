"""Build the typed Paper XI wall-profile census without mutating v1 or v2.

The typed census replaces the fixed ``(Delta R1, Delta R2, Delta D, ...)``
coordinate vector by a discriminated union of oriented trajectory-event maps
and incident-stratum locus germs. It treats the historical A--F labels as
nonexclusive curation tags, separates primary wall fields from context
co-observations, and records structured profile families.

Only upstream-admitted ``strict_sof`` morphology atoms enter the strict main
spectrum. Corpus-included ``diagnostic_analogue`` atoms remain in a separate
morphology set. The Paper XI ledger controls corpus inclusion and references
upstream admission; it is not itself a wall-admission authority.
Static findings, negative boundaries, and diagnostics remain typed context.
The finite census is a curation certificate, not a classification theorem.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
PAPER11_DIR = SCRIPT_DIR.parent
ROOT = PAPER11_DIR.parents[1]
RESULTS_DIR = PAPER11_DIR / "results"
PAPER_PATH = ROOT / "papers" / "paper11" / "Paper XI.md"
INCLUSION_LEDGER_PATH = RESULTS_DIR / "wall_record_inclusion_ledger_v1.json"
FROZEN_V2_CENSUS_PATH = (
    PAPER11_DIR / "archive" / "results" / "wall_record_census_v2.json"
)
FROZEN_V2_CENSUS_SHA256 = (
    "988d0fb807ac1deb239ccfd59d0e743fe6c7ab76caf18ea9fb1a033727a8cf79"
)
sys.path.insert(0, str(ROOT))

from experiments.observation import check_experiment_observation  # noqa: E402
from schemas.release_snapshot import resolve_release_reference  # noqa: E402

OBSERVATION_EVIDENCE_BY_ID = {
    "C-markov-absorbing-endpoint": (
        "experiments/paper11/results/markov_boundary.observation.json"
    ),
    "DE-kuramoto-freezing-crossover": (
        "experiments/paper11/results/kuramoto_freezing.observation.json"
    ),
}
PAIRWISE_CHANNELS = {
    "coverage.unreachable_pair_count",
    "diagnostic.matrix_commutator_repair_pair_count[cutoff=3]",
    "graph.unreachable_pair_count",
    "markov.terminal_unreachable_pair_count",
    "state.direct_support",
}
CLAIM_STATUSES = {
    "Theorem",
    "Computational Certificate",
    "Computational Observation",
    "Research Program",
}
DELTA_DIRECTIONS = {
    "increase",
    "decrease",
    "mixed",
    "not_applicable",
}
NOT_RECORDED = "NOT_RECORDED"
MAIN_WALL_ROLES = {"wall_event", "wall_locus_sample"}
REALIZATION_KINDS = {"strict_sof", "diagnostic_analogue"}
RECORD_ROLES = {
    "wall_event",
    "wall_locus_sample",
    "pre_wall_reference",
    "static_boundary_witness",
    "trajectory_diagnostic",
    "retired_provenance",
}
CURATION_TAG_MAP = {
    "A": "COLLISION",
    "B": "REPAIR",
    "C": "TERMINAL",
    "D": "PLATEAU_RATE",
    "E": "NONSMOOTH_DISCRETE",
    "F": "BRIDGE_INCIDENCE",
}
CURATION_TAG_OVERRIDES = {
    "BCF-quantum-cnot-threshold": ["NONSMOOTH_DISCRETE"],
    "BC-moe-bias-repair": ["REPAIR"],
}
NON_WALL_ROLE_BY_ID = {
    "A-rubik-simultaneous-pair-gap-response",
    "C-markov-absorbing-endpoint",
}
NON_WALL_ROLE_BY_ID = {
    **{source_id: "pre_wall_reference" for source_id in NON_WALL_ROLE_BY_ID},
    **{
        source_id: "static_boundary_witness"
        for source_id in {
            "BF-rubik-r2-repair",
            "F-rubik-type-iii-cancellation",
            "BF-synthetic-complement-repair",
            "BF-control-kalman-chain",
            "F-ncg-t7-bridge",
        }
    },
}
DIAGNOSTIC_ANALOGUE_IDS = {
    "B-transformer-lie-depth-repair",
    "BC-moe-bias-repair",
    "B-diffusion-denoising-repair",
    "BE-maze-door-wall",
    "D-yang-state-mixing-plateau",
    "E-relu-kink",
    "E-topk-rank-selection",
    "DE-kuramoto-freezing-crossover",
    "C-grn-terminal-basin-loss",
}
LOCUS_GERM_VALUES_BY_ID = {
    "A-rubik-collision-quotient": [
        {
            "stratum_ref": "left_regular_chamber",
            "value": {"joint_sector_count": 9},
        },
        {
            "stratum_ref": "joint_sector_collision_stratum",
            "value": {"joint_sector_count": 6},
        },
        {
            "stratum_ref": "right_regular_chamber",
            "value": {"joint_sector_count": 9},
        },
    ],
    "F-rubik-type-iv-incidence": [
        {
            "stratum_ref": "image_kernel_incidence_stratum",
            "value": {"route_support": False},
        },
        {
            "stratum_ref": "incident_nonzero_composition_stratum",
            "value": {"route_support": True},
        },
    ],
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


FROZEN_V2_CENSUS_RESOLVED_PATH = resolve_release_reference(
    {
        "uri": FROZEN_V2_CENSUS_PATH.relative_to(ROOT).as_posix(),
        "digest": {
            "algorithm": "sha256",
            "value": FROZEN_V2_CENSUS_SHA256,
        },
    },
    repository_root=ROOT,
)
if file_sha256(FROZEN_V2_CENSUS_RESOLVED_PATH) != FROZEN_V2_CENSUS_SHA256:
    raise RuntimeError("frozen Paper XI v1.1 census digest mismatch")
FROZEN_V2_CENSUS = load_json(FROZEN_V2_CENSUS_RESOLVED_PATH)


INCLUSION_LEDGER = load_json(INCLUSION_LEDGER_PATH)
INCLUSION_BY_ID = {
    row["source_record_id"]: row for row in INCLUSION_LEDGER["records"]
}
if len(INCLUSION_BY_ID) != len(INCLUSION_LEDGER["records"]):
    raise RuntimeError("wall-record inclusion ledger contains duplicate record IDs")

FIELD_FAMILY_BY_CARRIER_ID = {
    "spectral": "spectral",
    "operator": "operator",
    "operator_route": "route",
    "operator_word": "word",
    "lie_hall": "lie_hall",
    "continuous_lie_block_norm": "proxy",
    "observable_proxy": "proxy",
    "proxy": "proxy",
    "state_partition": "state",
    "terminal_structure": "state",
    "stochastic": "stochastic",
    "graph": "graph",
    "graph_spectral": "spectral",
    "activation": "state",
    "routing": "state",
    "bipartite_coverage": "graph",
    "markov": "state",
    "matrix_commutator_diagnostic": "diagnostic",
    "logarithm_domain_diagnostic": "diagnostic",
    "carrier.cnot_path_admissibility_control": "diagnostic",
    "dynamics": "proxy",
}


def delta(
    channel_id: str,
    carrier_id: str,
    observation: str,
    *,
    direction: str = "not_applicable",
    before_state: object = NOT_RECORDED,
    after_state: object = NOT_RECORDED,
    change_kind: str = "declared_change",
    depth_convention: str | None = None,
    cutoff: int | None = None,
    pair_scope: str | None = None,
) -> dict:
    if pair_scope is None:
        pair_scope = (
            "off_diagonal"
            if channel_id.startswith(("lie.", "operator.", "route.", "word."))
            or channel_id in PAIRWISE_CHANNELS
            else "not_applicable"
        )
    allowed_scopes = {
        "not_applicable",
        "off_diagonal",
        "full_block_tensor",
        "scalar_reduced_diagonal",
        "declared_mixed",
    }
    if pair_scope not in allowed_scopes:
        raise ValueError(f"unsupported pair scope: {pair_scope}")
    item = {
        "field_key": channel_id,
        "field_family": FIELD_FAMILY_BY_CARRIER_ID[carrier_id],
        "carrier_id": carrier_id,
        "before_state": before_state,
        "after_state": after_state,
        "change_kind": change_kind,
        "observation": observation,
        "direction": {
            "raw_numeric": direction,
            "accessibility": "not_applicable",
            "event_semantics": change_kind,
        },
        "pair_scope": pair_scope,
    }
    if depth_convention is not None:
        item["depth_convention"] = depth_convention
    if cutoff is not None:
        item["cutoff"] = cutoff
    return item


TYPED_META: dict[str, dict] = {
    "A-rubik-collision-quotient": {
        "wall_package": "spectral",
        "channel_deltas": [
            delta("spectral.joint_sector_count", "spectral", "maximal collision",
                  direction="decrease"),
        ],
    },
    "A-rubik-endpoint-pair-closures": {
        "wall_package": "spectral",
        "channel_deltas": [
            delta("spectral.adjacent_gap", "spectral", "16 pairwise closures",
                  direction="increase", change_kind="collision_exit"),
        ],
    },
    "A-rubik-simultaneous-pair-gap-response": {
        "wall_package": "spectral",
        "channel_deltas": [
            delta("spectral.pair_gap_response", "spectral",
                  "sampling-dependent common half-closure response",
                  direction="decrease"),
        ],
    },
    "BF-rubik-r2-repair": {
        "wall_package": "lie_hall",
        "channel_deltas": [
            delta("lie.direct_support[X]", "lie_hall",
                  "declared direct obstruction"),
            delta("lie.simple_commutator_support[X]", "lie_hall",
                  "simple-commutator emergence", direction="increase",
                  depth_convention="simple commutator"),
        ],
        "observable": "registered Lie direct and simple-commutator support",
        "note_append": "Carrier is the declared Paper V Lie family.",
    },
    "F-rubik-type-iii-cancellation": {
        "record_id": "F-rubik-commutator-cancellation",
        "species": "Rubik anti-Hermitian low-order audit",
        "observable": "simple-commutator cancellation relative to represented products",
        "change_locus": "288 registered commutator-cancellation instances",
        "wall_package": "lie_hall",
        "channel_deltas": [
            delta("lie.simple_commutator_support[X]", "lie_hall",
                  "cancellation after nonzero ordered-product contributions",
                  direction="decrease", depth_convention="simple commutator"),
        ],
        "note_append": "Static typed count; not a deformation wall record.",
    },
    "F-rubik-type-iv-incidence": {
        "record_id": "F-constructed-route-incidence",
        "species": "Constructed routed-product incidence",
        "observable": "selected routed operator product",
        "change_locus": "image-kernel incidence variety AB=0",
        "wall_package": "operator_route",
        "channel_deltas": [
            delta("route.support[Y,d=2]", "operator_route",
                  "selected routed product vanishes by image-kernel incidence",
                  direction="decrease", depth_convention="ordered route length 2"),
        ],
        "note": (
            "Free matrix-pair incidence model from Paper VII; not a represented "
            "Rubik transversality or genericity theorem."
        ),
    },
    "BF-synthetic-complement-repair": {
        "record_id": "BF-constructed-commutator-repair",
        "species": "Constructed commutator-cancellation control",
        "observable": "direct Lie support and simple-commutator support",
        "wall_package": "lie_hall",
        "channel_deltas": [
            delta("lie.direct_support[X]", "lie_hall",
                  "declared direct obstruction"),
            delta("lie.simple_commutator_support[X]", "lie_hall",
                  "simple-commutator support appears", direction="increase",
                  depth_convention="simple commutator"),
        ],
    },
    "BCF-quantum-cnot-threshold": {
        "record_id": "quantum-cnot-path-admissibility",
        "species": "Quantum Clifford+CNOT path control",
        "observable": "path admissibility and bounded Lie/Hall support summary",
        "deformation_origin": (
            "affine CNOT interpolation with fractional-unitary control"
        ),
        "change_locus": (
            "affine singularity at s=0.5; no internal transition on the unitary control"
        ),
        "wall_package": "cnot_path_admissibility_diagnostic",
        "channel_deltas": [
            delta(
                "diagnostic.path_logarithm_admissibility",
                "carrier.cnot_path_admissibility_control",
                (
                    "the affine path is singular at s=0.5; the unitary path has "
                    "an explicit continuous logarithm and one positive-parameter signature"
                ),
                change_kind="domain_boundary",
                pair_scope="not_applicable",
            ),
        ],
        "note": (
            "The former s=0.55 repair threshold is withdrawn. The affine-side "
            "difference is induced by a singular logarithm-domain crossing and "
            "samplewise branch choice. The fractional-unitary control is admissible "
            "and has no internal support transition on the declared grid."
        ),
    },
    "BF-control-kalman-chain": {
        "wall_package": "operator_word",
        "channel_deltas": [
            delta("word.depth_truncated[Y,cutoff=3]", "operator_word",
                  "terminal flag reached at word depth 2",
                  direction="increase", depth_convention="positive word length",
                  cutoff=3),
        ],
    },
    "B-transformer-lie-depth-repair": {
        "record_id": "B-transformer-matrix-commutator-repair",
        "wall_package": "matrix_commutator_diagnostic",
        "channel_deltas": [
            delta("diagnostic.matrix_commutator_repair_pair_count[cutoff=3]",
                  "matrix_commutator_diagnostic",
                  "two direct-unsupported pairs reached within tested rounds",
                  direction="increase",
                  depth_convention="legacy matrix-commutator generation round",
                  cutoff=3),
        ],
        "note_append": (
            "Static activation-sector diagnostic, not a deformation wall. "
            "The registered matrices are not a strict Lie/Hall carrier."
        ),
    },
    "BC-moe-bias-repair": {
        "wall_package": "routing",
        "channel_deltas": [
            delta("routing.active_private_experts", "routing",
                  "ten inactive experts become active", direction="increase"),
        ],
    },
    "B-diffusion-denoising-repair": {
        "wall_package": "state_partition",
        "channel_deltas": [
            delta("state.sector_count", "state_partition",
                  "PCA-sign sectors split and reverse under denoising",
                  direction="mixed"),
            delta("state.direct_support", "state_partition",
                  "support repairs on the reverse path", direction="increase"),
        ],
    },
    "BE-maze-door-wall": {
        "wall_package": "graph_connectivity",
        "channel_deltas": [
            delta("graph.component_count", "graph",
                  "24 splits followed by 24 reverse merges", direction="mixed"),
            delta("graph.unreachable_pair_count", "graph",
                  "connectivity loss and repair", direction="mixed"),
        ],
    },
    "BF-recommender-targeted-bridge": {
        "wall_package": "bipartite_coverage",
        "channel_deltas": [
            delta("coverage.unreachable_pair_count", "bipartite_coverage",
                  "12/16 to 10/16", direction="decrease"),
        ],
    },
    "C-markov-absorbing-endpoint": {
        "wall_package": "markov_communication",
        "channel_deltas": [
            delta("markov.terminal_unreachable_pair_count", "markov",
                  "two terminal unreachable pairs in endpoint contrast",
                  direction="increase"),
        ],
    },
    "C-barrier-stopping-boundary": {
        "wall_package": "stochastic_stopping",
        "channel_deltas": [
            delta("stochastic.first_hit_boundary", "stochastic",
                  "entry into absorbing stopping sector"),
        ],
    },
    "D-xu-ridge-rate-hierarchy": {
        "record_id": "D-exact-three-sector-rate-separation",
        "species": "Exact three-sector skew family",
        "observable": "selected direct and simple-commutator block norms",
        "deformation_origin": "skew-generator amplitude",
        "change_locus": (
            "common-threshold crossings eta and sqrt(eta), 0<eta<1"
        ),
        "evidence": "experiments/paper9/rate_hierarchy.py",
        "claim_status": "Theorem",
        "wall_package": "continuous_lie_block_norms",
        "channel_deltas": [
            delta("lie_norm.K_direct", "continuous_lie_block_norm",
                  "first crossing at eta", direction="increase",
                  pair_scope="off_diagonal"),
            delta("lie_norm.K_simple_commutator", "continuous_lie_block_norm",
                  "first crossing at sqrt(eta)", direction="increase",
                  pair_scope="off_diagonal"),
        ],
        "note": (
            "Exact selected block-norm response separation relative to the "
            "declared trajectory, normalization, norm, and threshold policy; "
            "not an intrinsic rate invariant, Boolean support wall, or "
            "Lie-depth computation."
        ),
    },
    "D-mechanism-separated-rates": {
        "wall_package": "observable_proxy",
        "channel_deltas": [
            delta("proxy.K0_growth_time", "proxy", "half-response time 30"),
            delta("proxy.K1_response_time", "proxy", "half-response time 1380"),
        ],
    },
    "D-yang-state-mixing-plateau": {
        "record_id": "D-nn-proxy-rate-ordering",
        "species": "Training-coupled NN SOF",
        "observable": (
            "continuous direct, simple-commutator, and nested-commutator "
            "block-norm proxies"
        ),
        "deformation_origin": "sampled training trajectory",
        "change_locus": "ordered half-response times 60 < 80 < 120",
        "evidence": "experiments/paper9/nn_training_sof_tau.py",
        "claim_status": "Computational Observation",
        "wall_package": "observable_proxy",
        "channel_deltas": [
            delta("proxy.K0_direct_norm", "observable_proxy",
                  "half-response time 60", pair_scope="declared_mixed"),
            delta("proxy.K1_simple_commutator_norm", "observable_proxy",
                  "half-response time 80", pair_scope="declared_mixed"),
            delta("proxy.K2_nested_commutator_norm", "observable_proxy",
                  "half-response time 120", pair_scope="declared_mixed"),
        ],
        "note": (
            "Continuous proxy ordering only; no coherent temporal sector "
            "continuation or proxy-to-discrete-shadow promotion."
        ),
    },
    "D-rubik-generator-weight-plateau": {
        "active": False,
        "retirement_reason": (
            "retired nonnormal generator-weight fragmentation/oscillation "
            "diagnostic; not admitted to the typed moving-wall census"
        ),
        "wall_package": "retired",
        "channel_deltas": [],
        "claim_status": "Research Program",
    },
    "E-graph-edge-removal": {
        "wall_package": "operator_word",
        "channel_deltas": [
            delta(
                "operator.direct_support[Y]",
                "operator",
                "four direct-support pairs are lost at the endpoint",
                direction="decrease",
                before_state={"supported_off_diagonal_pairs": 8},
                after_state={"supported_off_diagonal_pairs": 4},
                change_kind="support_loss",
            ),
            delta(
                "word.depth_truncated[Y,cutoff=6]",
                "operator_word",
                "six pairs become unreached at the endpoint",
                direction="increase",
                before_state={"unreached_pairs": 0},
                after_state={"unreached_pairs": 6},
                change_kind="first_hit_change",
                depth_convention="positive word length",
                cutoff=6,
            ),
        ],
    },
    "E-relu-kink": {
        "wall_package": "activation",
        "channel_deltas": [
            delta("activation.response_slope", "activation",
                  "left/right slope jump at zero", direction="mixed"),
        ],
    },
    "E-topk-rank-selection": {
        "wall_package": "activation",
        "channel_deltas": [
            delta("activation.topk_active_count", "activation",
                  "no rank-selection crossing on tested grid"),
        ],
    },
    "F-ncg-t7-bridge": {
        "wall_package": "operator_route",
        "channel_deltas": [
            delta("route.support[Y,d=2]", "operator_route",
                  "two ordered T7-style bridge diagnostics",
                  direction="increase", depth_convention="ordered route length 2"),
        ],
        "note_append": "Support-level bridge record; no composition promotion.",
    },
    "A-constructed-goe-endpoint": {
        "wall_package": "spectral",
        "channel_deltas": [
            delta("spectral.adjacent_gap", "spectral",
                  "two order-one endpoint closures", direction="increase",
                  change_kind="collision_exit"),
        ],
    },
    "BE-nested-percolation-opening": {
        "wall_package": "operator_word",
        "channel_deltas": [
            delta("operator.direct_support[Y]", "operator",
                  "monotone direct-support opening", direction="increase"),
            delta(
                "word.unreached_pair_count_at_cutoff"
                "[Y,cutoff=6,aggregation=ensemble_mean,ensemble_policy=seeded_nested_32]",
                "operator_word",
                "ensemble-mean cutoff-unreached pair count has a largest adjacent sampled drop",
                direction="decrease",
                cutoff=6,
                change_kind="largest_adjacent_sampled_drop",
            ),
        ],
    },
    "DE-kuramoto-freezing-crossover": {
        "wall_package": "operator_word",
        "channel_deltas": [
            delta("word.depth_truncated[Y,cutoff=3]", "operator_word",
                  "cutoff-unreached word-pair count increases",
                  direction="decrease", depth_convention="positive word length",
                  cutoff=3),
            delta("dynamics.order_parameter_occupancy", "dynamics",
                  "occupancy contracts", direction="decrease"),
        ],
    },
    "C-grn-terminal-basin-loss": {
        "wall_package": "terminal_structure",
        "channel_deltas": [
            delta("state.terminal_component_count", "terminal_structure",
                  "two attracting components become one", direction="decrease"),
            delta("state.terminal_sector_identity", "terminal_structure",
                  "terminal sector 40 is lost", direction="decrease"),
        ],
    },
}


STATUS_MAP = {
    "theorem": "Theorem",
    "evidence": "Computational Certificate",
    "constructed_witness": "Computational Certificate",
    "diagnostic": "Computational Observation",
    "proxy_only": "Computational Observation",
    "candidate_evidence": "Computational Observation",
    "boundary": "Computational Observation",
}


SMOOTH_IDS = {
    "A-rubik-collision-quotient",
    "A-rubik-endpoint-pair-closures",
    "A-rubik-simultaneous-pair-gap-response",
    "C-barrier-stopping-boundary",
    "D-xu-ridge-rate-hierarchy",
    "D-mechanism-separated-rates",
    "A-constructed-goe-endpoint",
}
STRATIFIED_IDS = {"F-rubik-type-iv-incidence"}
PIECEWISE_SMOOTH_IDS = {
    "BC-moe-bias-repair",
    "E-relu-kink",
    "E-topk-rank-selection",
}
DISCRETE_IDS = {
    "BE-maze-door-wall",
    "BF-recommender-targeted-bridge",
    "E-graph-edge-removal",
    "F-ncg-t7-bridge",
    "BE-nested-percolation-opening",
}
STOCHASTIC_IDS = {
    "B-diffusion-denoising-repair",
    "D-yang-state-mixing-plateau",
    "DE-kuramoto-freezing-crossover",
}


def record_role(source_id: str, active: bool) -> str:
    if not active:
        return "retired_provenance"
    if source_id in INCLUSION_BY_ID:
        return INCLUSION_BY_ID[source_id]["record_role"]
    return NON_WALL_ROLE_BY_ID.get(source_id, "trajectory_diagnostic")


def realization_kind(source_id: str) -> str:
    if source_id in INCLUSION_BY_ID:
        return INCLUSION_BY_ID[source_id]["realization_kind"]
    return (
        "diagnostic_analogue"
        if source_id in DIAGNOSTIC_ANALOGUE_IDS
        else "strict_sof"
    )


def regularity_axis(source_id: str) -> str:
    if source_id in SMOOTH_IDS:
        return "smooth"
    if source_id in STRATIFIED_IDS:
        return "stratified"
    if source_id in PIECEWISE_SMOOTH_IDS:
        return "piecewise_smooth"
    if source_id in DISCRETE_IDS:
        return "discrete"
    if source_id in STOCHASTIC_IDS:
        return "stochastic"
    return "unknown"


def profile_for(row: dict, source_id: str) -> dict:
    field_families = sorted(
        {item["field_family"] for item in row["channel_deltas"]}
    )
    event_kind_map = {
        "COLLISION": "collision",
        "REPAIR": "repair",
        "TERMINAL": "terminalization",
        "PLATEAU_RATE": "response_order_crossing",
        "NONSMOOTH_DISCRETE": "boundary_hit",
        "BRIDGE_INCIDENCE": "first_hit_change",
    }
    event_kinds = sorted(
        {event_kind_map[tag] for tag in row["curation_tags"]}
    )
    persistence_profile = (
        ["terminal"]
        if "TERMINAL" in row["curation_tags"]
        else ["plateau"]
        if "PLATEAU_RATE" in row["curation_tags"]
        else ["unresolved"]
    )
    position = (
        "endpoint"
        if "endpoint" in source_id
        else "boundary"
        if source_id in {
            "C-barrier-stopping-boundary",
            "E-graph-edge-removal",
            "E-relu-kink",
            "E-topk-rank-selection",
        }
        else "unresolved"
    )
    return {
        "field_families": field_families,
        "event_kinds": event_kinds,
        "regularity": regularity_axis(source_id),
        "persistence_profile": persistence_profile,
        "geometry": {
            "location": position,
            "crossing": "unresolved",
            "codimension_status": "codimension_unresolved",
        },
        "evidence": row["claim_status"],
    }


def field_registration(
    field: dict,
    *,
    inclusion: dict,
    evidence_ref: str,
    field_role: str,
) -> dict:
    return {
        "field_key": field["field_key"],
        "field_role": field_role,
        "field_family": field["field_family"],
        "carrier_id": (
            inclusion["primary_carrier_id"]
            if field_role == "primary_wall_field"
            else field["carrier_id"]
        ),
        "chart_or_domain_ref": inclusion["domain_or_trajectory_ref"],
        "comparison_ref": "identity_on_declared_fixed_schema",
        "policy_refs": {
            "named_policy_refs": inclusion["policy_refs"],
            "pair_scope": field["pair_scope"],
            "diagonal_reduction": field.get(
                "diagonal_reduction",
                "not_applicable",
            ),
            "depth_convention": field.get("depth_convention", "not_applicable"),
            "cutoff": field.get("cutoff", "not_applicable"),
        },
        "evidence_ref": evidence_ref,
    }


def field_observation(
    field: dict,
    *,
    canonical_carrier_id: str | None = None,
) -> dict:
    observation = {
        key: copy.deepcopy(value)
        for key, value in field.items()
        if key not in {"before_state", "after_state"}
    }
    if canonical_carrier_id is not None:
        observation["carrier_id"] = canonical_carrier_id
    return observation


def primary_transition_from_evidence(
    source_id: str,
    primary_field: str,
) -> tuple[object, object, dict]:
    inclusion = INCLUSION_BY_ID[source_id]
    evidence = load_json(ROOT / inclusion["evidence_artifact"])

    if source_id == "A-rubik-endpoint-pair-closures":
        event = evidence["spectral_endpoint"]["trajectory_event"]
        return event["before_state"], event["after_state"], {
            "raw_numeric": event["raw_numeric_direction"],
            "accessibility": "not_applicable",
            "event_semantics": event["event_semantics"],
        }
    if source_id == "BCF-quantum-cnot-threshold":
        raise RuntimeError(
            "the context-only CNOT path diagnostic cannot produce a primary wall transition"
        )
    if source_id == "BE-maze-door-wall":
        event = evidence["objects"][0]["data"]["wall_descriptor"]["split_events"][0]
        return event["before"], event["after"], {
            "raw_numeric": "increase",
            "accessibility": "decrease",
            "event_semantics": "connectivity_split",
        }
    if source_id == "E-graph-edge-removal":
        graph = evidence["Graph edge-weight endpoint"]
        before = graph["field_state_counts"][-2]["operator.direct_support[Y]"]
        after = graph["field_state_counts"][-1]["operator.direct_support[Y]"]
        return before, after, {
            "raw_numeric": "decrease",
            "accessibility": "decrease",
            "event_semantics": "support_loss",
        }
    if source_id == "A-constructed-goe-endpoint":
        event = evidence["trajectory_event"]
        return event["before_state"], event["after_state"], {
            "raw_numeric": event["raw_numeric_direction"],
            "accessibility": "not_applicable",
            "event_semantics": event["event_semantics"],
        }
    if source_id == "BE-nested-percolation-opening":
        event = evidence["trajectory_event"]
        return event["before_state"], event["after_state"], {
            "raw_numeric": event["raw_numeric_direction"],
            "accessibility": event["accessibility_direction"],
            "event_semantics": event["event_semantics"],
        }
    if source_id == "C-grn-terminal-basin-loss":
        event = evidence["edge_deformation"]["trajectory_event"]
        return event["before_state"], event["after_state"], {
            "raw_numeric": event["raw_numeric_direction"],
            "accessibility": event["accessibility_direction"],
            "event_semantics": event["event_semantics"],
        }
    raise KeyError(
        f"{source_id}: no evidence extractor for trajectory primary field "
        f"{primary_field}"
    )


def morphology_atom_for(row: dict, source_id: str, fields: list[dict]) -> dict | None:
    role = row["record_role"]
    if role not in MAIN_WALL_ROLES:
        return None
    inclusion = INCLUSION_BY_ID[source_id]
    primary_field = inclusion["primary_field"]
    context_fields = [
        field["field_key"]
        for field in fields
        if field["field_key"] != primary_field
    ]
    registrations = [
        field_registration(
            field,
            inclusion=inclusion,
            evidence_ref=row["evidence"],
            field_role=(
                "primary_wall_field"
                if field["field_key"] == primary_field
                else "context_co_observation"
            ),
        )
        for field in fields
    ]
    common = {
        "inclusion_ledger_version": INCLUSION_LEDGER["ledger_version"],
        "realization_kind": inclusion["realization_kind"],
        "spectrum_partition": inclusion["spectrum_partition"],
        "primary_wall_field": primary_field,
        "primary_field_family": inclusion["field_family"],
        "primary_carrier_id": inclusion["primary_carrier_id"],
        "context_field_keys": context_fields,
        "context_carrier_ids": inclusion["context_carrier_ids"],
        "field_registrations": registrations,
        "context_no_promotion": (
            "a context-field change is a co-observation only; it creates a "
            "separate wall atom only after independent wall admission"
        ),
    }
    if role == "wall_event":
        context = inclusion["orientation_or_incident_strata"]
        event_fields = copy.deepcopy(fields)
        before, after, direction = primary_transition_from_evidence(
            source_id,
            primary_field,
        )
        primary_change = next(
            field for field in event_fields if field["field_key"] == primary_field
        )
        primary_change["before_state"] = before
        primary_change["after_state"] = after
        primary_change["direction"] = direction
        return {
            "atom_kind": "trajectory_event",
            **common,
            "trajectory_ref": inclusion["domain_or_trajectory_ref"],
            "order_semantics": "trajectory_oriented",
            "orientation": context["orientation"],
            "left_right_sampling_rule": context["sampling_rule"],
            "event_parameter_or_interval": context["event_interval"],
            "field_changes": event_fields,
        }

    strata = LOCUS_GERM_VALUES_BY_ID[source_id]
    return {
        "atom_kind": "locus_sample",
        **common,
        "domain_context_ref": inclusion["domain_or_trajectory_ref"],
        "event_locus": row["change_locus"],
        "field_germs": [
            {
                "field_key": field["field_key"],
                "incident_strata": copy.deepcopy(strata),
            }
            for field in fields
        ],
        "probe_path_ref": None,
        "probe_orientation": None,
        "order_semantics": "intrinsic_none",
    }


def migrate_record(source: dict) -> dict:
    item = copy.deepcopy(source)
    source_id = item["record_id"]
    legacy_tags = item.pop("classes")
    historical_eligible = item.pop("eligible")
    meta = copy.deepcopy(TYPED_META[source_id])
    note_append = meta.pop("note_append", "")
    explicit_note = meta.pop("note", None)
    status_override = meta.pop("claim_status", None)
    item.update(meta)
    item.setdefault("active", True)
    item["source_record_id"] = source_id
    item["record_id"] = re.sub(r"^[A-F]+-", "", item["record_id"])
    item["curation_tags"] = CURATION_TAG_OVERRIDES.get(
        source_id,
        [CURATION_TAG_MAP[tag] for tag in legacy_tags],
    )
    item["curation_assignment"] = {
        "rulebook_version": "paper11-curation-tags-v1.0",
        "assignment_source": (
            "override" if source_id in CURATION_TAG_OVERRIDES else "inherited"
        ),
        "tags": copy.deepcopy(item["curation_tags"]),
        "override_reason": (
            "typed carrier and promotion-boundary correction"
            if source_id in CURATION_TAG_OVERRIDES
            else None
        ),
    }
    item["compatibility"] = {
        "historical_census_eligible": historical_eligible,
    }
    item["local_model_eligibility"] = {
        "status": "unresolved",
        "model_family": "ADE",
        "condition_checks": [],
        "evidence_refs": [],
    }
    item["claim_status"] = (
        status_override
        or STATUS_MAP.get(source["claim_status"], "Research Program")
    )
    if explicit_note is not None:
        item["note"] = explicit_note
    elif note_append:
        item["note"] = " ".join(
            part for part in [item.get("note", ""), note_append] if part
        )
    item["realization_kind"] = realization_kind(source_id)
    item["record_role"] = record_role(source_id, item["active"])
    if source_id in INCLUSION_BY_ID:
        item["claim_status"] = INCLUSION_BY_ID[source_id]["claim_status"]
        item["evidence"] = INCLUSION_BY_ID[source_id]["evidence_artifact"]
        item["evidence_contract"] = copy.deepcopy(
            INCLUSION_BY_ID[source_id]["evidence_contract"]
        )
        item["source_evidence"] = item["evidence_contract"]["producer"]
    elif source_id in OBSERVATION_EVIDENCE_BY_ID:
        item["source_evidence"] = item["evidence"]
        item["evidence"] = OBSERVATION_EVIDENCE_BY_ID[source_id]
        item["observation_contract"] = {
            "schema": "rime.experiment-observation.v1",
            "artifact_role": "cached_computational_observation",
            "claim_status": "Computational Observation",
        }
    item["wall_coordinate_profile"] = profile_for(item, source_id)
    fields = item.pop("channel_deltas")
    inclusion = INCLUSION_BY_ID.get(source_id)
    item["field_family"] = (
        inclusion["field_family"]
        if inclusion is not None
        else fields[0]["field_family"]
        if fields
        else "not_applicable"
    )
    item["typed_channel_count"] = len(fields)
    item["field_observations"] = [
        field_observation(
            field,
            canonical_carrier_id=(
                inclusion["primary_carrier_id"]
                if inclusion is not None
                and field["field_key"] == inclusion["primary_field"]
                else None
            ),
        )
        for field in fields
    ]
    atom = morphology_atom_for(item, source_id, fields)
    item["morphology_atoms"] = [] if atom is None else [atom]
    entry_kind = (
        inclusion["paper11_corpus_inclusion"]["entry_kind"]
        if inclusion is not None
        else "wall_context_record"
    )
    bundle_kind = (
        inclusion["paper11_corpus_inclusion"].get("bundle_kind")
        if inclusion is not None
        else None
    )
    item["corpus_entry"] = {
        "entry_kind": entry_kind,
        "bundle_kind": bundle_kind,
        "record_bundle": (
            {
                "bundle_id": item["record_id"],
                "morphology_atoms": item["morphology_atoms"],
            }
            if entry_kind == "morphology_record_bundle"
            else None
        ),
        "context_record": (
            {
                "record_role": item["record_role"],
                "diagnostic_fields": copy.deepcopy(item["field_observations"]),
            }
            if entry_kind == "wall_context_record"
            else None
        ),
    }
    if atom is not None:
        primary_field = atom["primary_wall_field"]
        primary_registration = next(
            registration
            for registration in atom["field_registrations"]
            if registration["field_key"] == primary_field
        )
        item["morphology_signature"] = {
            "role": item["record_role"],
            "realization_kind": item["realization_kind"],
            "atom_kind": atom["atom_kind"],
            "primary_field_family": primary_registration["field_family"],
            "primary_carrier_id": primary_registration["carrier_id"],
            "delta_ref": f"{item['record_id']}:morphology_atom:0",
            "profile": item["wall_coordinate_profile"],
        }
        item["curated_signature"] = {
            "morphology_signature_ref": f"{item['record_id']}:morphology_signature",
            "curation_assignment": copy.deepcopy(item["curation_assignment"]),
        }
    else:
        item["morphology_signature"] = None
        item["curated_signature"] = None
    return item


def evidence_owner(evidence_path: str) -> str:
    for part in Path(evidence_path).parts:
        if part.startswith("paper") and part[5:].isdigit():
            return part
    return "external"


def validate_typed_record(row: dict) -> None:
    if row["claim_status"] not in CLAIM_STATUSES:
        raise ValueError(
            f"{row['record_id']}: unsupported claim status {row['claim_status']!r}"
        )
    if row["record_role"] not in RECORD_ROLES:
        raise ValueError(
            f"{row['record_id']}: unsupported record role {row['record_role']!r}"
        )
    if row["realization_kind"] not in REALIZATION_KINDS:
        raise ValueError(
            f"{row['record_id']}: unsupported realization kind "
            f"{row['realization_kind']!r}"
        )
    if row["record_role"] == "diagnostic_analogue":
        raise ValueError(
            f"{row['record_id']}: realization kind leaked into record_role"
        )
    if row["field_family"] == "analogue":
        raise ValueError(
            f"{row['record_id']}: realization kind leaked into field_family"
        )
    if row["active"] and not row["field_observations"]:
        raise ValueError(f"{row['record_id']}: active row has no typed field")
    eligibility = row["local_model_eligibility"]
    if eligibility["status"] not in {"yes", "no", "unresolved"}:
        raise ValueError(f"{row['record_id']}: invalid local-model eligibility")
    if eligibility["status"] == "no" and not any(
        check.get("status") == "certified_false"
        for check in eligibility["condition_checks"]
    ):
        raise ValueError(
            f"{row['record_id']}: eligibility=no lacks a certified-false condition"
        )
    for observation in row["field_observations"]:
        direction = observation["direction"]
        if direction["raw_numeric"] not in DELTA_DIRECTIONS:
            raise ValueError(
                f"{row['record_id']}: unsupported direction "
                f"{direction['raw_numeric']!r}"
            )
        if set(direction) != {
            "raw_numeric",
            "accessibility",
            "event_semantics",
        }:
            raise ValueError(
                f"{row['record_id']}: direction semantics are incomplete"
            )
        if (
            ".depth_" in observation["field_key"]
            and "depth_convention" not in observation
        ):
            raise ValueError(
                f"{row['record_id']}: depth delta lacks a depth convention"
            )
    atoms = row["morphology_atoms"]
    if row["record_role"] in MAIN_WALL_ROLES and len(atoms) != 1:
        raise ValueError(
            f"{row['record_id']}: current morphology bundle must contain one morphology atom"
        )
    if row["record_role"] not in MAIN_WALL_ROLES and atoms:
        raise ValueError(f"{row['record_id']}: context record contains morphology atoms")
    if not atoms:
        return
    atom = atoms[0]
    observed_fields = {
        field["field_key"] for field in row["field_observations"]
    }
    registered_fields = {
        registration["field_key"]
        for registration in atom["field_registrations"]
    }
    if registered_fields != observed_fields:
        raise ValueError(
            f"{row['record_id']}: field registrations do not match observations"
        )
    primary_field = atom["primary_wall_field"]
    if primary_field not in observed_fields:
        raise ValueError(
            f"{row['record_id']}: primary wall field is not registered"
        )
    if set(atom["context_field_keys"]) != observed_fields - {primary_field}:
        raise ValueError(
            f"{row['record_id']}: context fields do not match non-primary fields"
        )
    primary_registrations = [
        registration
        for registration in atom["field_registrations"]
        if registration["field_role"] == "primary_wall_field"
    ]
    if len(primary_registrations) != 1:
        raise ValueError(
            f"{row['record_id']}: expected exactly one primary registration"
        )
    for registration in atom["field_registrations"]:
        required_policies = {
            "named_policy_refs",
            "pair_scope",
            "diagonal_reduction",
            "depth_convention",
            "cutoff",
        }
        if not required_policies.issubset(registration["policy_refs"]):
            raise ValueError(
                f"{row['record_id']}: incomplete field-specific policy registration"
            )
    if atom["atom_kind"] == "trajectory_event":
        if atom["order_semantics"] != "trajectory_oriented":
            raise ValueError(f"{row['record_id']}: invalid trajectory order semantics")
        required = {
            "trajectory_ref",
            "orientation",
            "left_right_sampling_rule",
            "event_parameter_or_interval",
        }
        if not required.issubset(atom):
            raise ValueError(
                f"{row['record_id']}: trajectory event lacks context fields"
            )
        for change in atom["field_changes"]:
            for state_key in ("before_state", "after_state", "change_kind"):
                if state_key not in change:
                    raise ValueError(
                        f"{row['record_id']}: event change lacks {state_key}"
                    )
        primary_change = next(
            change
            for change in atom["field_changes"]
            if change["field_key"] == primary_field
        )
        if (
            primary_change["before_state"] == NOT_RECORDED
            or primary_change["after_state"] == NOT_RECORDED
        ):
            raise ValueError(
                f"{row['record_id']}: primary event field uses NOT_RECORDED"
            )
        if primary_change["before_state"] == primary_change["after_state"]:
            raise ValueError(
                f"{row['record_id']}: primary event field has no state change"
            )
    elif atom["atom_kind"] == "locus_sample":
        if atom["order_semantics"] not in {"intrinsic_none", "probe_relative"}:
            raise ValueError(f"{row['record_id']}: invalid locus order semantics")
        if bool(atom["probe_path_ref"]) != bool(atom["probe_orientation"]):
            raise ValueError(
                f"{row['record_id']}: probe path and orientation must co-occur"
            )
        germ_fields = {germ["field_key"] for germ in atom["field_germs"]}
        if germ_fields != observed_fields:
            raise ValueError(
                f"{row['record_id']}: locus germs do not match registered fields"
            )
        for germ in atom["field_germs"]:
            if len(germ["incident_strata"]) < 2:
                raise ValueError(
                    f"{row['record_id']}: locus germ needs incident strata"
                )
            distinct_values = {
                json.dumps(stratum["value"], sort_keys=True)
                for stratum in germ["incident_strata"]
            }
            if len(distinct_values) < 2:
                raise ValueError(
                    f"{row['record_id']}: locus germ has no recorded change"
                )
            if any(
                key in germ
                for key in ("before_state", "after_state")
            ):
                raise ValueError(
                    f"{row['record_id']}: locus germ uses before/after states"
                )
    else:
        raise ValueError(
            f"{row['record_id']}: unsupported atom kind {atom['atom_kind']!r}"
        )


def compute_typed_census() -> dict:
    frozen_rows = FROZEN_V2_CENSUS["records"]
    source_ids = {row["record_id"] for row in frozen_rows}
    if set(TYPED_META) != source_ids:
        missing = source_ids - set(TYPED_META)
        extra = set(TYPED_META) - source_ids
        raise RuntimeError(f"typed mapping mismatch: missing={sorted(missing)}, extra={sorted(extra)}")
    if not set(INCLUSION_BY_ID).issubset(source_ids):
        raise RuntimeError(
            "inclusion ledger references unknown source rows: "
            f"{sorted(set(INCLUSION_BY_ID) - source_ids)}"
        )
    for source_id, relative_path in OBSERVATION_EVIDENCE_BY_ID.items():
        if source_id not in source_ids:
            raise RuntimeError(
                f"observation evidence references unknown row: {source_id}"
            )
        observation_path = ROOT / relative_path
        check = check_experiment_observation(observation_path, root=ROOT)
        if not check.reusable:
            details = "; ".join((*check.errors, *check.stale_sources))
            raise RuntimeError(
                f"{source_id}: cached observation is not current: {details}"
            )
        observation = load_json(observation_path)
        if observation["claim"]["status"] != "Computational Observation":
            raise RuntimeError(
                f"{source_id}: cached observation has invalid claim status"
            )
    required_inclusion_fields = {
        "source_record_id",
        "realization_kind",
        "record_role",
        "spectrum_partition",
        "primary_field",
        "field_family",
        "primary_carrier_id",
        "context_carrier_ids",
        "domain_or_trajectory_ref",
        "orientation_or_incident_strata",
        "policy_refs",
        "evidence_artifact",
        "evidence_contract",
        "claim_status",
        "upstream_wall_admission",
        "paper11_corpus_inclusion",
    }
    for source_id, inclusion in INCLUSION_BY_ID.items():
        if not required_inclusion_fields.issubset(inclusion):
            raise RuntimeError(f"{source_id}: incomplete inclusion ledger entry")
        if inclusion["realization_kind"] not in REALIZATION_KINDS:
            raise RuntimeError(f"{source_id}: invalid ledger realization kind")
        upstream = inclusion["upstream_wall_admission"]
        corpus = inclusion["paper11_corpus_inclusion"]
        if upstream["status"] not in {
            "admitted", "not_admitted", "unresolved", "not_applicable"
        }:
            raise RuntimeError(f"{source_id}: invalid upstream admission status")
        bundle_kind = corpus.get("bundle_kind")
        if corpus["entry_kind"] == "morphology_record_bundle":
            if inclusion["record_role"] not in MAIN_WALL_ROLES:
                raise RuntimeError(f"{source_id}: morphology bundle lacks an event/locus role")
            if bundle_kind == "strict_wall_record":
                if inclusion["realization_kind"] != "strict_sof":
                    raise RuntimeError(f"{source_id}: strict bundle lacks strict realization")
                if upstream["status"] != "admitted":
                    raise RuntimeError(f"{source_id}: strict bundle lacks upstream admission")
            elif bundle_kind == "analogue_morphology_record":
                if inclusion["realization_kind"] != "diagnostic_analogue":
                    raise RuntimeError(f"{source_id}: analogue bundle lacks analogue realization")
                if upstream["status"] != "not_applicable":
                    raise RuntimeError(f"{source_id}: analogue bundle claims strict-wall admission")
            else:
                raise RuntimeError(f"{source_id}: invalid morphology bundle kind")
        elif corpus["entry_kind"] == "wall_context_record":
            if inclusion["record_role"] in MAIN_WALL_ROLES:
                raise RuntimeError(f"{source_id}: context record uses a wall role")
            if bundle_kind is not None:
                raise RuntimeError(f"{source_id}: context record declares a bundle kind")
        else:
            raise RuntimeError(f"{source_id}: invalid corpus entry kind")
        if inclusion["spectrum_partition"] not in {
            "strict_main", "analogue_morphology", "context_only"
        }:
            raise RuntimeError(f"{source_id}: invalid spectrum partition")
        if not (ROOT / inclusion["evidence_artifact"]).is_file():
            raise RuntimeError(f"{source_id}: ledger evidence artifact is missing")

        contract = inclusion["evidence_contract"]
        required_contract_fields = {
            "schema",
            "sha256",
            "producer",
            "producer_sha256",
        }
        if not required_contract_fields.issubset(contract):
            raise RuntimeError(f"{source_id}: incomplete evidence contract")
        evidence_path = ROOT / inclusion["evidence_artifact"]
        if file_sha256(evidence_path) != contract["sha256"]:
            raise RuntimeError(f"{source_id}: evidence artifact digest mismatch")
        producer_path = ROOT / contract["producer"]
        if not producer_path.is_file():
            raise RuntimeError(f"{source_id}: evidence producer is missing")
        if file_sha256(producer_path) != contract["producer_sha256"]:
            raise RuntimeError(f"{source_id}: evidence producer digest mismatch")
        evidence_record = load_json(evidence_path)
        recorded_schemas = {
            evidence_record.get("schema"),
            evidence_record.get("record_version"),
            evidence_record.get("schema_version"),
            evidence_record.get("ir_version"),
        }
        spectral_endpoint = evidence_record.get("spectral_endpoint")
        if isinstance(spectral_endpoint, dict):
            recorded_schemas.add(spectral_endpoint.get("record_version"))
        if contract["schema"] not in recorded_schemas:
            raise RuntimeError(f"{source_id}: evidence schema mismatch")

        recorded_statuses = {evidence_record.get("claim_status")}
        if isinstance(spectral_endpoint, dict):
            recorded_statuses.add(spectral_endpoint.get("claim_status"))
        for claim in evidence_record.get("claims", []):
            if isinstance(claim, dict):
                recorded_statuses.add(claim.get("claim_status"))
        if inclusion["claim_status"] not in recorded_statuses:
            raise RuntimeError(f"{source_id}: evidence claim-status mismatch")

        validation_fields = {
            "validation_certificate",
            "validation_certificate_sha256",
            "validator",
            "validator_sha256",
        }
        present_validation_fields = validation_fields & set(contract)
        if present_validation_fields and present_validation_fields != validation_fields:
            raise RuntimeError(f"{source_id}: incomplete validation-certificate binding")
        if present_validation_fields:
            certificate_path = ROOT / contract["validation_certificate"]
            validator_path = ROOT / contract["validator"]
            if file_sha256(certificate_path) != contract["validation_certificate_sha256"]:
                raise RuntimeError(f"{source_id}: validation certificate digest mismatch")
            if file_sha256(validator_path) != contract["validator_sha256"]:
                raise RuntimeError(f"{source_id}: validator digest mismatch")
            certificate = load_json(certificate_path)
            if certificate.get("validation_status") != "passed":
                raise RuntimeError(f"{source_id}: validation certificate did not pass")
            if certificate.get("result_sha256") != contract["sha256"]:
                raise RuntimeError(f"{source_id}: certificate result digest mismatch")

    records = [migrate_record(row) for row in frozen_rows]
    for row in records:
        validate_typed_record(row)
    active_records = [row for row in records if row["active"]]
    strict_main_wall_records = []
    analogue_morphology_records = []
    for row in records:
        row["evidence_exists"] = (ROOT / row["evidence"]).is_file()
        row["evidence_owner"] = evidence_owner(row["evidence"])
        row["evidence_relation"] = (
            "paper11_local"
            if row["evidence_owner"] == "paper11"
            else "imported_source_record"
        )
        inclusion = INCLUSION_BY_ID.get(row["source_record_id"])
        row["inclusion_ledger_entry"] = (
            f"{INCLUSION_LEDGER['ledger_version']}:{row['source_record_id']}"
            if inclusion
            else None
        )
        row["corpus_entry_kind"] = (
            inclusion["paper11_corpus_inclusion"]["entry_kind"]
            if inclusion
            else "wall_context_record"
        )
        row["morphology_bundle_kind"] = (
            inclusion["paper11_corpus_inclusion"].get("bundle_kind")
            if inclusion
            else None
        )
        upstream_admitted = (
            inclusion is not None
            and inclusion["upstream_wall_admission"]["status"] == "admitted"
        )
        row["main_wall_spectrum_eligible"] = (
            upstream_admitted
            and inclusion["paper11_corpus_inclusion"]["entry_kind"]
            == "morphology_record_bundle"
            and inclusion["paper11_corpus_inclusion"]["bundle_kind"]
            == "strict_wall_record"
            and inclusion["spectrum_partition"] == "strict_main"
            and row["realization_kind"] == "strict_sof"
            and row["active"]
            and row["evidence_exists"]
        )
        row["analogue_morphology_eligible"] = (
            inclusion is not None
            and inclusion["upstream_wall_admission"]["status"] == "not_applicable"
            and inclusion["paper11_corpus_inclusion"]["entry_kind"]
            == "morphology_record_bundle"
            and inclusion["paper11_corpus_inclusion"]["bundle_kind"]
            == "analogue_morphology_record"
            and inclusion["spectrum_partition"] == "analogue_morphology"
            and row["realization_kind"] == "diagnostic_analogue"
            and row["active"]
            and row["evidence_exists"]
        )
        if row["main_wall_spectrum_eligible"]:
            strict_main_wall_records.append(row)
        if row["analogue_morphology_eligible"]:
            analogue_morphology_records.append(row)

    tag_summary = {}
    for tag in CURATION_TAG_MAP.values():
        members = [row for row in active_records if tag in row["curation_tags"]]
        main_members = [
            row for row in strict_main_wall_records if tag in row["curation_tags"]
        ]
        tag_summary[tag] = {
            "active_records": len(members),
            "main_wall_records": len(main_members),
            "main_wall_species": len({row["species"] for row in main_members}),
            "main_wall_deformations": len(
                {row["deformation_origin"] for row in main_members}
            ),
        }
    role_summary = {
        role: sum(row["record_role"] == role for row in records)
        for role in sorted(RECORD_ROLES)
    }
    realization_summary = {
        kind: sum(row["realization_kind"] == kind for row in records)
        for kind in sorted(REALIZATION_KINDS)
    }
    ledger_bytes = INCLUSION_LEDGER_PATH.read_bytes()
    morphology_bundles = strict_main_wall_records + analogue_morphology_records
    morphology_atoms = sum(len(row["morphology_atoms"]) for row in morphology_bundles)
    registered_atom_field_entries = sum(
        len(atom["field_registrations"])
        for row in morphology_bundles
        for atom in row["morphology_atoms"]
    )
    trajectory_change_entries = sum(
        len(atom["field_registrations"])
        for row in morphology_bundles
        for atom in row["morphology_atoms"]
        if atom["atom_kind"] == "trajectory_event"
    )
    locus_germ_entries = sum(
        len(atom["field_registrations"])
        for row in morphology_bundles
        for atom in row["morphology_atoms"]
        if atom["atom_kind"] == "locus_sample"
    )
    pair_scoped_entries = sum(
        registration["policy_refs"]["pair_scope"] != "not_applicable"
        for row in morphology_bundles
        for atom in row["morphology_atoms"]
        for registration in atom["field_registrations"]
    )
    if registered_atom_field_entries != trajectory_change_entries + locus_germ_entries:
        raise RuntimeError("atom-field entry partition is inconsistent")
    if any(len(row["morphology_atoms"]) != 1 for row in morphology_bundles):
        raise RuntimeError("current snapshot requires one morphology atom per bundle")
    return {
        "version": "paper11-typed-v3.6",
        "base_version": "paper11-v2-prep-preserved",
        "historical_base_census": {
            "path": FROZEN_V2_CENSUS_PATH.relative_to(ROOT).as_posix(),
            "version": FROZEN_V2_CENSUS["version"],
            "sha256": FROZEN_V2_CENSUS_SHA256,
            "record_count": len(frozen_rows),
        },
        "historical_record_count": len(records),
        "active_record_count": len(active_records),
        "retired_record_count": len(records) - len(active_records),
        "main_wall_spectrum_record_count": len(strict_main_wall_records),
        "analogue_morphology_record_count": len(analogue_morphology_records),
        "morphology_record_bundle_count": len(morphology_bundles),
        "morphology_atom_count": morphology_atoms,
        "registered_atom_field_entry_count": registered_atom_field_entries,
        "trajectory_change_entry_count": trajectory_change_entries,
        "locus_germ_entry_count": locus_germ_entries,
        "pair_scoped_entry_count": pair_scoped_entries,
        "current_atoms_per_morphology_bundle": 1,
        "active_tag_membership_count": sum(
            len(row["curation_tags"]) for row in active_records
        ),
        "record_role_summary": role_summary,
        "realization_kind_summary": realization_summary,
        "curation_tag_summary": tag_summary,
        "wall_record_inclusion_ledger": {
            "path": INCLUSION_LEDGER_PATH.relative_to(ROOT).as_posix(),
            "version": INCLUSION_LEDGER["ledger_version"],
            "sha256": hashlib.sha256(ledger_bytes).hexdigest(),
            "record_count": len(INCLUSION_LEDGER["records"]),
        },
        "strict_main_wall_records": [
            {
                "record_id": row["record_id"],
                "source_record_id": row["source_record_id"],
                "record_role": row["record_role"],
                "field_family": row["field_family"],
                "primary_field": row["morphology_atoms"][0]["primary_wall_field"],
                "evidence_artifact": row["evidence"],
                "claim_status": row["claim_status"],
            }
            for row in strict_main_wall_records
        ],
        "analogue_morphology_records": [
            {
                "record_id": row["record_id"],
                "source_record_id": row["source_record_id"],
                "record_role": row["record_role"],
                "field_family": row["field_family"],
                "primary_field": row["morphology_atoms"][0]["primary_wall_field"],
                "evidence_artifact": row["evidence"],
                "claim_status": row["claim_status"],
            }
            for row in analogue_morphology_records
        ],
        "records": records,
        "wall_corpus_contract": (
            "WallCorpusEntry is MorphologyRecordBundle or WallContextRecord; "
            "MorphologyRecordBundle is StrictWallRecord or "
            "AnalogueMorphologyRecord, and each bundle contains MorphologyAtom values. "
            "MorphologyAtom is a discriminated union: trajectory_event carries an "
            "oriented before/after field map, while locus_sample carries "
            "incident-stratum field germs without intrinsic two-sided order"
        ),
        "morphology_signature_contract": (
            "MorphSig_W^{P_W}(atom) = (realization_kind, record_role, "
            "atom_kind, primary_field_family, primary_carrier_id, atom_delta, "
            "wall_coordinate_profile)"
        ),
        "curated_signature_contract": (
            "CuratedSig_W^{P_W,v}(atom) = "
            "(MorphSig_W^{P_W}(atom), Curate_v(atom))"
        ),
        "primary_context_contract": (
            "in a StrictWallRecord the primary_wall_field establishes wall "
            "admissibility; in an AnalogueMorphologyRecord it anchors morphology "
            "without asserting strict admission. Each "
            "context_field_key is separately registered as a co-observation "
            "and creates no additional wall atom without independent admission"
        ),
        "profile_contract": {
            "families": [
                "field_families",
                "event_kinds",
                "regularity",
                "persistence_profile",
                "geometry",
                "evidence",
            ],
            "multi_valued": ["event_kinds", "persistence_profile"],
            "geometry_fields": [
                "location",
                "crossing",
                "codimension_status",
            ],
            "observation_policies_excluded_from_regularity": [
                "censoring",
                "sampling",
            ],
        },
        "supported_field_key_families": {
            "operator_word_lie": [
                "operator.direct_support[Y]",
                "route.support[Y,d]",
                "word.support[Y,d]",
                "word.depth_exact[Y]",
                "word.depth_truncated[Y,cutoff=m]",
                "lie.simple_commutator_support[X]",
                "lie.depth_exact[X,H]",
                "lie.depth_truncated[X,H,cutoff=n]",
            ],
            "closures": [
                "closure.positive_algebra.dimension[Y]",
                "closure.positive_algebra.corner_dimension[Y,i,j]",
                "closure.observable_star.marked_corner_dimension[Y,i,j]",
                "closure.observable_star.abstract_algebra_type[Y]",
                "closure.observable_star.concrete_embedding[Y]",
                "closure.sector_star.marked_corner_type[Q,Y,i,j]",
                "closure.sector_star.abstract_algebra_type[Q,Y]",
                "closure.sector_star.concrete_embedding[Q,Y]",
            ],
            "other": [
                "spectral.gap",
                "proxy.response_time[policy]",
                "state.first_hit_time[policy]",
            ],
        },
        "closure_boundary": (
            "positive-algebra fields do not admit a Wedderburn-type coordinate "
            "without a separately declared semisimplicity certificate"
        ),
        "closure_corner_policy_contract": {
            "off_diagonal": {
                "pair_scope": "off_diagonal",
                "diagonal_reduction": "not_applicable",
            },
            "scalar_reduced_diagonal": {
                "pair_scope": "scalar_reduced_diagonal",
                "diagonal_reduction": "hs_scalar_complement",
            },
            "raw_diagonal_unital_corner_comparison": "forbidden",
        },
        "not_recorded_marker_contract": (
            "NOT_RECORDED marks record-field presence only; it is neither a "
            "Paper X IR result state nor a Paper XIII comparison state"
        ),
        "census_interpretation": (
            "finite source-addressed curation certificate; no partition, "
            "completeness, or population-prevalence claim"
        ),
        "typed_delta_contract": (
            "trajectory-event deltas are oriented sparse before/after maps; "
            "locus-sample deltas are incident-stratum germs"
        ),
        "wall_spectrum_gate": (
            "only upstream-admitted strict_sof wall_event and wall_locus_sample "
            "bundles included by the versioned ledger enter the strict main wall "
            "spectrum; included diagnostic_analogue atoms remain in a separate "
            "analogue-morphology set without an upstream strict-wall admission claim"
        ),
        "curation_rulebook": {
            "version": "paper11-curation-tags-v1.0",
            "assignment_kind": "nonexclusive",
            "tags": {
                "COLLISION": "declared spectral or observable collision morphology",
                "REPAIR": "field witness, support, or bounded reachability becomes present",
                "TERMINAL": "terminal component, basin, or endpoint structure changes",
                "PLATEAU_RATE": "plateau or response-order morphology",
                "NONSMOOTH_DISCRETE": "piecewise, discrete, or sampled-boundary morphology",
                "BRIDGE_INCIDENCE": "route, word, commutator, or incidence mechanism",
            },
        },
        "ownership_contract": (
            "source artifacts retain their owning paper; Paper XI owns the "
            "corpus inclusion, derived wall-coordinate profiles, curation tags, and this "
            "finite census certificate"
        ),
    }


def markdown_report(census: dict) -> str:
    lines = [
        "# Paper XI Typed Wall-Profile Census",
        "",
        f"- Historical rows preserved: **{census['historical_record_count']}**",
        f"- Active typed records: **{census['active_record_count']}**",
        f"- Retired rows: **{census['retired_record_count']}**",
        f"- Strict main wall-spectrum records: **{census['main_wall_spectrum_record_count']}**",
        f"- Analogue morphology records: **{census['analogue_morphology_record_count']}**",
        f"- Morphology record bundles: **{census['morphology_record_bundle_count']}**",
        f"- Morphology atoms: **{census['morphology_atom_count']}**",
        f"- Registered atom-field entries: **{census['registered_atom_field_entry_count']}**",
        f"- Trajectory-change entries: **{census['trajectory_change_entry_count']}**",
        f"- Locus-germ entries: **{census['locus_germ_entry_count']}**",
        f"- Pair-scoped entries: **{census['pair_scoped_entry_count']}**",
        f"- Active multi-label memberships: **{census['active_tag_membership_count']}**",
        "- Morphology bundles contain atoms from the trajectory-event/locus-sample union.",
        "- Tags are nonexclusive curation labels, not classification classes.",
        "- Imported evidence retains its source-paper ownership.",
        "",
        "## Record roles",
        "",
        "| Role | Records |",
        "|---|---:|",
    ]
    for role, count in census["record_role_summary"].items():
        lines.append(f"| {role} | {count} |")
    lines.extend(
        [
            "",
            "## Realization kinds",
            "",
            "| Realization kind | Records |",
            "|---|---:|",
        ]
    )
    for kind, count in census["realization_kind_summary"].items():
        lines.append(f"| {kind} | {count} |")
    lines.extend(
        [
            "",
            "## Curation tags",
            "",
            "| Tag | Active records | Main-wall records | Species | Deformations |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for tag, row in census["curation_tag_summary"].items():
        lines.append(
            f"| {tag} | {row['active_records']} | "
            f"{row['main_wall_records']} | {row['main_wall_species']} | "
            f"{row['main_wall_deformations']} |"
        )
    lines.extend(
        [
            "",
            "## Morphology record bundles",
            "",
            "| Partition | Record | Role | Field family | Primary field | Evidence |",
            "|---|---|---|---|---|---|",
        ]
    )
    for partition, records in (
        ("strict_main", census["strict_main_wall_records"]),
        ("analogue_morphology", census["analogue_morphology_records"]),
    ):
        for row in records:
            lines.append(
                f"| {partition} | `{row['record_id']}` | "
                f"{row['record_role']} | {row['field_family']} | "
                f"`{row['primary_field']}` | `{row['evidence_artifact']}` |"
            )
    lines.extend(["", "## Active records", ""])
    for row in census["records"]:
        if not row["active"]:
            continue
        channels = ", ".join(
            field["field_key"] for field in row["field_observations"]
        )
        lines.append(
            f"- `{row['record_id']}`: {row['species']} | {row['wall_package']} | "
            f"{channels} | {row['claim_status']} | {row['record_role']} | "
            f"{row['realization_kind']} | field_family={row['field_family']} | "
            f"owner={row['evidence_owner']}"
        )
    lines.extend(["", "## Retired provenance", ""])
    for row in census["records"]:
        if row["active"]:
            continue
        lines.append(
            f"- `{row['record_id']}`: {row['retirement_reason']}"
        )
    return "\n".join(lines) + "\n"


def verify_paper_digest(census: dict) -> None:
    paper = PAPER_PATH.read_text(encoding="utf-8")
    expected_rows = [
        f"| `{role}` | {count} |"
        for role, count in census["record_role_summary"].items()
    ]
    expected_rows.extend(
        f"| `{tag}` | {row['active_records']} | {row['main_wall_records']} |"
        for tag, row in census["curation_tag_summary"].items()
    )
    missing = [row for row in expected_rows if row not in paper]
    if missing:
        raise RuntimeError(
            "Paper XI generated census digest is out of sync:\n"
            + "\n".join(missing)
        )


def main() -> None:
    census = compute_typed_census()
    verify_paper_digest(census)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / "wall_record_census_typed_v3.json"
    md_path = RESULTS_DIR / "wall_record_census_typed_v3.md"
    json_path.write_text(json.dumps(census, indent=2), encoding="utf-8")
    md_path.write_text(markdown_report(census), encoding="utf-8")

    print("=" * 76)
    print("  Paper XI typed wall-profile census")
    print("=" * 76)
    print(
        f"historical={census['historical_record_count']}, "
        f"active={census['active_record_count']}, "
        f"main_wall={census['main_wall_spectrum_record_count']}, "
        f"memberships={census['active_tag_membership_count']}"
    )
    for tag, row in census["curation_tag_summary"].items():
        print(
            f"{tag}: active={row['active_records']}, "
            f"main_wall={row['main_wall_records']}, "
            f"species={row['main_wall_species']}, "
            f"deformations={row['main_wall_deformations']}"
        )
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()
