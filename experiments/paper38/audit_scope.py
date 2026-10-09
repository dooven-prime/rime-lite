"""Fixed declarative catalogue for the return-budget consistency control."""

from dataclasses import dataclass
from itertools import permutations


IDENTITY = (0, 1, 2, 3, 4)
REFLECTION = (0, 4, 3, 2, 1)
AFFINE = (0, 2, 4, 1, 3)
THREE_CYCLE = (1, 2, 0, 3, 4)
TRANSPOSITION = (1, 0, 2, 3, 4)
MAX_RETURNS = 26
MATCHED_G = (3, 4, 5)
PAIRS = tuple((i, j) for i in range(5) for j in range(i + 1, 5))
PROFILES = (
    "rotations", "reflection_first", "reflection_last",
    "affine_first", "alternating_first", "symmetric_first",
)
RESULT_PATH = "experiments/paper38/results/return_budget_audit_v1.json"
SCHEMA = "rime.paper38.return-budget-audit.v1"
BOUNDARY = (
    "Bounded consistency control only; the manuscript owns the all-g proofs. "
    "No sharp constant, shortest raw-word, typed bridge, settlement, or reset claim."
)
ARTIFACTS = (
    ("canonical-manuscript", "papers/paper38/Paper XXXVIII.md"),
    ("paper-local-bibliography", "papers/paper38/references-v1.bib"),
    ("package-documentation", "experiments/paper38/README.md"),
    ("fixed-audit-contract", "experiments/paper38/audit_scope.py"),
    ("finite-producer", "experiments/paper38/return_budget_audit.py"),
    ("bounded-result", RESULT_PATH),
    ("published-theorem-binding", "experiments/paper38/upstream-provenance.json"),
    ("manifest-sealer", "experiments/paper38/seal_manifest.py"),
    ("source-validator", "experiments/paper38/validation/validate_source.py"),
    ("finite-validator", "experiments/paper38/validation/validate_return_budget.py"),
    ("package-validator", "experiments/paper38/validation/validate_package.py"),
    ("negative-contract-tests", "experiments/paper38/validation/test_contract.py"),
    ("lean-validator", "experiments/paper38/validation/validate_lean_formalization.py"),
    ("lean-entrypoint", "experiments/paper38/lean/Paper38.lean"),
    ("lean-product-layers", "experiments/paper38/lean/Paper38/ReturnLayers.lean"),
    ("lean-saturation", "experiments/paper38/lean/Paper38/Saturation.lean"),
    ("lean-initial-control", "experiments/paper38/lean/Paper38/InitialLayerControl.lean"),
    ("lean-axiom-audit", "experiments/paper38/lean/AxiomAudit.lean"),
    ("lean-scope-readme", "experiments/paper38/lean/README.md"),
    ("lean-project-config", "experiments/paper38/lean/lakefile.toml"),
    ("lean-dependency-lock", "experiments/paper38/lean/lake-manifest.json"),
    ("lean-toolchain", "experiments/paper38/lean/lean-toolchain"),
    ("lean-formalization-manifest", "experiments/paper38/lean/formalization-manifest.json"),
)


@dataclass(frozen=True)
class Branch:
    identifier: str
    g: int
    targets: tuple[int, ...]
    restrictions: tuple[tuple[int, ...], ...]
    punctured: tuple[int, ...] = (0, 1, 2, 3)

    def record(self):
        return {
            "branch_id": self.identifier, "g": self.g,
            "lane_targets": list(self.targets),
            "local_permutations": [list(p) for p in self.restrictions],
            "punctured_permutation": list(self.punctured),
        }


def branches():
    rows = [Branch(f"g2-{i:03d}", 2, (1,), (p,))
            for i, p in enumerate(permutations(range(5)))]
    for g in (3, 4):
        for profile in PROFILES:
            local = [IDENTITY] * (g - 1)
            if profile == "rotations":
                local = [tuple((i + j) % 5 for i in range(5)) for j in range(1, g)]
            else:
                position = g - 2 if profile == "reflection_last" else 0
                local[position] = {
                    "reflection_first": REFLECTION, "reflection_last": REFLECTION,
                    "affine_first": AFFINE, "alternating_first": THREE_CYCLE,
                    "symmetric_first": TRANSPOSITION,
                }[profile]
            for variant in (0, 1):
                targets = tuple(1 + (j + variant) % (g - 1) for j in range(g - 1))
                star = (0, 1, 2, 3) if variant == 0 else (3, 2, 1, 0)
                rows.append(Branch(f"g{g}-{profile}-v{variant}", g,
                                   targets, tuple(local), star))
    return tuple(rows)


def matched_branches(g):
    rows = []
    for lane in (2, 1):
        local = [IDENTITY] * (g - 1)
        local[lane - 1] = REFLECTION
        rows.append(Branch(f"matched-g{g}-reflection{lane}", g,
                           tuple(range(1, g)), tuple(local)))
    return tuple(rows)


def scope_record():
    return {
        "g2_policy": "all 120 local S5 restrictions; punctured identity",
        "selected_g": [3, 4], "selected_profiles": list(PROFILES),
        "variants": "identity lanes/identity puncture; cyclic lane shift/reversed puncture",
        "source_policy": "every ordinary lane; five source labels in positive order",
        "labels": "all residues modulo n", "exact_return_counts": list(range(1, 27)),
        "terminal_return_is_counted": True, "matched_g": list(MATCHED_G),
        "domain_counts": [
            {"g": 2, "branches": 120, "source_cases": 120},
            {"g": 3, "branches": 12, "source_cases": 24},
            {"g": 4, "branches": 12, "source_cases": 36},
        ],
    }
