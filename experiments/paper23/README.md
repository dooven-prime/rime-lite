# Paper XXIII Evidence Package

This directory contains the computational evidence for Paper XXIII, *Kernel
Corridors and Schreier Waiting in Synchronizing Automata*.

## Scope

The package contains:

- exact `n=2,3` registries and eight deterministic `n=4` census
  shards;
- a merged `n=4` summary whose shard paths and file/content digests are
  rebuilt for `experiments/paper23`;
- paper-local pair-hitting, reachable-unit packing inversion and area,
  fiber-incidence, waiting-capacity, and kernel-corridor audits;
- exhaustive labelled binary-clean enumeration through `n=6`;
- a pinned Lean project and compilation receipt for the explicitly declared
  formalized theorem surface.

The package layout is:

- the directory root contains the mathematical core and deterministic result
  producers consumed by the paper;
- `validation/` contains audit producers and artifact validators;
- `results/` contains the exact records;
- `lean/` contains the pinned formal source closure.

## Validation

Run from the repository root:

```bash
python experiments/paper23/validation/validate_release.py
```

To regenerate the deterministic receipt after an evidence change:

```bash
python experiments/paper23/validation/validate_release.py --write-receipt
```

The validator checks existing artifacts; it does not rewrite them.
The only write mode is the explicit receipt command above.

## Artifact replay

The principal producer commands are:

```bash
python experiments/paper23/merge_census.py "experiments/paper23/results/n4_k2_v2_shards/shard_*.json" --out experiments/paper23/results/n4_k2_v2_summary.json
python experiments/paper23/validation/audit_pair_hitting.py --out experiments/paper23/results/pair_hitting_audit_n3_n4_v1.json experiments/paper23/results/n3_k2_v2.json experiments/paper23/results/n4_k2_v2_shards
python experiments/paper23/validation/audit_fiber_incidence.py --out experiments/paper23/results/fiber_incidence_potential_audit_n3_n4_v1.json experiments/paper23/results/n3_k2_v2.json experiments/paper23/results/n4_k2_v2_shards
python experiments/paper23/validation/audit_kernel_schreier_corridors.py --out experiments/paper23/results/kernel_schreier_corridor_audit_n3_n4_v1.json experiments/paper23/results/n3_k2_v2.json experiments/paper23/results/n4_k2_v2_shards
python experiments/paper23/validation/audit_kernel_schreier_corridors.py --out experiments/paper23/results/kernel_schreier_corridor_audit_slow_families_v1.json experiments/paper23/results/slow_family_suite_n2_n12_v1.json
python experiments/paper23/validation/audit_waiting_capacity.py --out experiments/paper23/results/waiting_capacity_tradeoff_audit_slow_families_v1.json experiments/paper23/results/slow_family_suite_n2_n12_v1.json
python experiments/paper23/enumerate_binary_clean_corridors.py --max-states 6 --out experiments/paper23/results/binary_clean_corridor_exhaustion_n2_n6_v1.json
```

## Lean boundary

`lean/formalization_receipt.json` records a successful build under Lean
4.33.0 and Mathlib revision
`db584cd6d46c92f209a44c0f1c829460d327499d`.

```bash
cd experiments/paper23/lean
lake build
lake env lean Formalization/AxiomAudit.lean
```

Lean fully covers the pair-hitting identity. It covers only the conditional
arithmetic implication used in the parameter-free Cerny corollary and does not
certify the other manuscript theorems.
