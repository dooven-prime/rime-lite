"""Fixed audit inputs and exact closure allowlist; results cannot narrow them."""

from itertools import product

from contract import Environment

RESULT = "experiments/paper39/results/consumer_audit_v1.json"
BOUNDARY = "Bounded consistency controls, not all-N proofs, external UFE verification, or old B0."


def cases():
    for n in (2, 3, 4):
        for defect in product(range(n), repeat=n):
            if len(set(defect)) != n - 1:
                continue
            seeds = [tuple(range(n))]
            if n == 4:
                seeds += [(0, 2), (0, 1, 3)]
            for seed in seeds:
                yield {"id": f"all-n{n}-d{''.join(map(str, defect))}-s{''.join(map(str, seed))}",
                       "environment": Environment(defect, seed, tuple(range(len(seed)))),
                       "max_word_length": 5}
    for n in (5, 6, 7):
        canonical = (0, 0) + tuple(range(1, n - 1))
        transported = tuple(n - 2 if q == 0 else 0 if q == n - 2 else q for q in canonical)
        for name, defect in (("canonical", canonical), ("transported", transported)):
            for size in (n - 1, n):
                yield {"id": f"selected-n{n}-{name}-N{size}",
                       "environment": Environment(defect, tuple(range(size)), tuple(reversed(range(size)))),
                       "max_word_length": 6}


ARTIFACTS = (
    ("canonical-manuscript", "papers/paper39/Paper XXXIX.md"),
    ("consumer-specification", "experiments/paper39/notes/ABSORPTION_CONSUMER_SPEC.md"),
    ("supplementary-proof", "experiments/paper39/notes/ABSORPTION_CONSUMER_ADEQUACY.md"),
    ("supplementary-correspondence", "experiments/paper39/notes/UFE_CORRESPONDENCE.md"),
    ("bibliography", "papers/paper39/references-v1.bib"),
    ("package-documentation", "experiments/paper39/README.md"),
    ("fixed-audit-contract", "experiments/paper39/audit_scope.py"),
    ("immutable-records", "experiments/paper39/contract.py"),
    ("independent-log-specification", "experiments/paper39/log_consumer.py"),
    ("forest-implementation", "experiments/paper39/forest.py"),
    ("abstract-ufe-adapter", "experiments/paper39/placed_ufe.py"),
    ("bounded-producer", "experiments/paper39/consumer_audit.py"),
    ("bounded-result", RESULT),
    ("manifest-sealer", "experiments/paper39/seal_manifest.py"),
    ("finite-validator", "experiments/paper39/validation/validate_consumer.py"),
    ("source-validator", "experiments/paper39/validation/validate_source.py"),
    ("negative-contract-tests", "experiments/paper39/validation/test_contract.py"),
    ("package-validator", "experiments/paper39/validation/validate_package.py"),
    ("lean-validator", "experiments/paper39/validation/validate_lean_formalization.py"),
    ("lean-entrypoint", "experiments/paper39/lean/Paper39.lean"),
    ("lean-port-lookup", "experiments/paper39/lean/Paper39/PortLookup.lean"),
    ("lean-forest-counts", "experiments/paper39/lean/Paper39/ForestCounts.lean"),
    ("lean-continuation", "experiments/paper39/lean/Paper39/Continuation.lean"),
    ("lean-axiom-audit", "experiments/paper39/lean/AxiomAudit.lean"),
    ("lean-scope", "experiments/paper39/lean/README.md"),
    ("lean-project", "experiments/paper39/lean/lakefile.toml"),
    ("lean-lock", "experiments/paper39/lean/lake-manifest.json"),
    ("lean-toolchain", "experiments/paper39/lean/lean-toolchain"),
    ("lean-manifest", "experiments/paper39/lean/formalization-manifest.json"),
)
