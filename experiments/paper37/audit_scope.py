"""Fixed declarative scope for Paper XXXVII's bounded consistency control."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations


IDENTITY = tuple(range(5))
CYCLE = (1, 2, 3, 4, 0)
CYCLE2 = (2, 3, 4, 0, 1)
REFLECTION = (0, 4, 3, 2, 1)
AFFINE2 = (0, 2, 4, 1, 3)
AFFINE3 = (0, 3, 1, 4, 2)
THREE_CYCLE = (1, 2, 0, 3, 4)
TRANSPOSITION = (1, 0, 2, 3, 4)
TRANSPOSITION12 = (0, 2, 1, 3, 4)
PAIRS = tuple((i, j) for i in range(5) for j in range(i + 1, 5))
PUNCTURED = (
    (0, 1, 2, 3),
    (1, 2, 3, 0),
    (3, 2, 1, 0),
    (1, 0, 2, 3),
)
G3_PROFILES = (
    ("identity", IDENTITY, IDENTITY),
    ("rotations", CYCLE, CYCLE2),
    ("one_reflection", REFLECTION, IDENTITY),
    ("two_reflections", REFLECTION, REFLECTION),
    ("affine", AFFINE2, IDENTITY),
    ("alternating", THREE_CYCLE, IDENTITY),
    ("symmetric", TRANSPOSITION, IDENTITY),
    ("affine_alternating", AFFINE2, THREE_CYCLE),
    ("alternating_symmetric", THREE_CYCLE, TRANSPOSITION),
    ("two_affine", AFFINE2, AFFINE3),
    ("rotation_reflection", CYCLE2, REFLECTION),
    ("two_transpositions", TRANSPOSITION, TRANSPOSITION12),
)
MATCHED_G_VALUES = (2, 3, 4)
RESULT_RELATIVE = "experiments/paper37/results/ordinary_lane_audit_v1.json"
RESULT_SCHEMA = "rime.paper37.ordinary-lane-audit.v1"
RESULT_STATUS = "BOUNDED_CONSISTENCY_CONTROL"
CLAIM_BOUNDARY = (
    "Bounded replay only; the manuscript owns the all-g proofs. "
    "No typed bridge, projectability, settlement, or reset bound is established."
)
CHECKS = (
    "raw guarded reachability and ordinary-lane confinement",
    "actual relocation, phase, and local-generator words",
    "lineage-group reachable-injection equality",
    "right-phase-coset count and deterministic-descent condition",
    "actual terminal-placement equality",
    "source-addressed survivor sets and restriction multiplicity",
    "matched F20/S5 coarse-summary non-descent",
    "matched A5/S5 equal complete survivor spectra",
)
DOMAIN_COUNTS = (
    {"g": 2, "n": 10, "delta": 2, "branches": 120, "source_cases": 120},
    {"g": 3, "n": 15, "delta": 3, "branches": 96, "source_cases": 192},
)
ARTIFACTS = (
    ("canonical-manuscript", "papers/paper37/Paper XXXVII.md"),
    ("paper-local-bibliography", "papers/paper37/references-v1.bib"),
    ("package-documentation", "experiments/paper37/README.md"),
    ("fixed-audit-contract", "experiments/paper37/audit_scope.py"),
    ("finite-producer", "experiments/paper37/ordinary_lane_audit.py"),
    ("bounded-result", RESULT_RELATIVE),
    ("manifest-sealer", "experiments/paper37/seal_manifest.py"),
    ("source-validator", "experiments/paper37/validation/validate_source.py"),
    ("finite-validator", "experiments/paper37/validation/validate_ordinary_lane_audit.py"),
    ("package-validator", "experiments/paper37/validation/validate_package.py"),
    ("negative-contract-tests", "experiments/paper37/validation/test_contract.py"),
    ("lean-validator", "experiments/paper37/validation/validate_lean_formalization.py"),
    ("lean-entrypoint", "experiments/paper37/lean/Paper37.lean"),
    ("lean-guarded-control", "experiments/paper37/lean/Paper37/GuardedControl.lean"),
    ("lean-phase-cosets", "experiments/paper37/lean/Paper37/PhaseCosets.lean"),
    ("lean-survivor-restriction", "experiments/paper37/lean/Paper37/SurvivorRestriction.lean"),
    ("lean-axiom-audit", "experiments/paper37/lean/AxiomAudit.lean"),
    ("lean-scope-readme", "experiments/paper37/lean/README.md"),
    ("lean-project-config", "experiments/paper37/lean/lakefile.toml"),
    ("lean-dependency-lock", "experiments/paper37/lean/lake-manifest.json"),
    ("lean-toolchain", "experiments/paper37/lean/lean-toolchain"),
    ("lean-formalization-manifest", "experiments/paper37/lean/formalization-manifest.json"),
)


@dataclass(frozen=True)
class Branch:
    identifier: str
    g: int
    targets: tuple[int, ...]
    restrictions: tuple[tuple[int, ...], ...]
    punctured: tuple[int, ...]

    def record(self) -> dict[str, object]:
        return {
            "branch_id": self.identifier,
            "g": self.g,
            "lane_targets": list(self.targets),
            "local_permutations": [list(row) for row in self.restrictions],
            "punctured_permutation": list(self.punctured),
        }


def branches() -> tuple[Branch, ...]:
    rows = [
        Branch(f"g2-perm-{i:03d}", 2, (1,), (sigma,), PUNCTURED[0])
        for i, sigma in enumerate(permutations(range(5)))
    ]
    for name, first, second in G3_PROFILES:
        for lane_index, targets in enumerate(((1, 2), (2, 1))):
            for star_index, star in enumerate(PUNCTURED):
                rows.append(Branch(
                    f"g3-{name}-lanes{lane_index}-star{star_index}",
                    3, targets, (first, second), star,
                ))
    return tuple(rows)


def scope_record() -> dict[str, object]:
    return {
        "g2_policy": "all 120 local S5 permutations; punctured restriction identity",
        "g3_policy": "12 named local profiles x 2 lane permutations x 4 punctured restrictions",
        "g3_profiles": [row[0] for row in G3_PROFILES],
        "source_policy": "every ordinary lane; five source labels in positive order",
        "return_labels": "all residues modulo n",
        "word_length_budget": None,
        "matched_g_values": list(MATCHED_G_VALUES),
    }
