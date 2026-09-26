# Paper XXVIII: Finite Evidence Package

This directory is a **byte-identical frozen release copy**, not a second
mathematical authority. The [manuscript](../../papers/paper28/Paper%20XXVIII.md)
is scoped as a finite-structure paper. The copied files preserve the exact
research provenance used by the finite results; no external source tree is a
release dependency.
The mirror does not change their contracts, results, receipts, or ownership.

## Release-Copy Layout

- [`artifacts/`](artifacts/) contains the 27 byte-identical finite owning
  notes and source/domain declarations needed by the paper. Their internal
  historical links are intentionally not rewritten.
- [`results/`](results/) contains 45 exact artifacts and their 45 original
  receipts: the 20 manuscript-level anchors, their declared finite input
  closure, and one validator-read dependency absent from its older receipt.
  It also contains the separate paper-owned Lean closure receipt. The
  directory is not a copy of the whole exploratory results directory.
- [`inputs/`](inputs/) contains three exact upstream input snapshots at the
  digests bound by the original receipts. The inherited-section pilot is
  **not** replaced by the different same-named current Paper XXVII file.
- Root-level Python files and [`validation/`](validation/) contain the 55
  minimal producers/dependencies and 43 original validators reached through
  receipt source closures, local imports, and declared validator reads.
- [`lean/`](lean/) contains a separate paper-owned partial formalization of
  three data-independent implications and two negative controls. Its validator
  and self-excluding receipt are independent of the historical finite mirror.
- [`dependency-manifest.json`](dependency-manifest.json) records every copied
  file's historical path, mirror path, SHA-256, role, and artifact-input edges.
  The three upstream input bindings are mapped to the packaged exact bytes.

Historical basenames and their internal `P28.*` identifiers are retained only
as provenance: renaming receipt-bound files would obscure the exact byte and
dependency bindings. Reader-facing theorem numbering is defined by the
manuscript. Dependency artifacts used by finite selectors are included even
when their exploratory names are not manuscript headings.

## Reader Path

Do not read `artifacts/` lexicographically. Start with the manuscript, then use
this table to enter the frozen evidence at the theorem-facing node.

| Manuscript surface | Read first | Supporting closure |
|---|---|---|
| Propositions 3.1--3.2: seed quotient and generator cover | [`P28_1_SEED_PROJECTOR_RESULTS.md`](artifacts/P28_1_SEED_PROJECTOR_RESULTS.md) | boundary-liftability and generator artifacts listed in the dependency manifest |
| Propositions 4.1--4.2: credit composition | [`P28_2_CREDIT_COMPOSITION_RESULTS.md`](artifacts/P28_2_CREDIT_COMPOSITION_RESULTS.md) | exact accounting artifacts and the separate [`lean/`](lean/) spine |
| Theorem 5.1: five recursive returns | [`P28_4A_FUTURE_FREE_SECTION_RETURN_SCHEMA.md`](artifacts/P28_4A_FUTURE_FREE_SECTION_RETURN_SCHEMA.md) | the five declaration/result groups summarized below |
| Theorems 6.1--6.2: reduced cover and alignment | [`P28_6U_D_TAGGED_FIXED_SCOPE_MECHANISM_COVER.md`](artifacts/P28_6U_D_TAGGED_FIXED_SCOPE_MECHANISM_COVER.md) | GFPC/PEC records and [`P28_6V_CANONICAL_RETURN_CERTIFICATE_ALIGNMENT.md`](artifacts/P28_6V_CANONICAL_RETURN_CERTIFICATE_ALIGNMENT.md) |

The copied notes preserve stage-time words such as `candidate`, `provisional`,
`next gate`, and `future`. Those words record the state in which a bound
artifact was produced; they are not the current claim status or a public
research plan. The manuscript and its Claim Status table control the
reader-facing interpretation. No README is added inside `artifacts/` because
that directory is a strict byte-identical mirror.

From the repository root, the package-only checks are:

```powershell
python experiments/paper28/validation/validate_public_package.py
python experiments/paper28/validation/validate_mirror.py
python experiments/paper28/validation/validate_release.py
python experiments/paper28/validation/validate_lean_formalization.py --replay
```

`validate_public_package.py` is the outer release gate. It verifies the
manuscript/PDF/build closure, the nested finite mirror and Lean receipts, the
package inventory, and the self-excluding public receipt. The retained receipt
is accepted only when its exact three-key replay block records successful
mirror verification, finite-root replay, and Lean elaboration replay. Release
preparation uses the explicit `--write-manifest --write-receipt --replay` mode;
ordinary verification is read-only and rejects altered or extra replay claims.

`validate_mirror.py` checks only packaged bytes, original receipt bindings,
mapped input edges, the three upstream input digests, and the immutable
cover/alignment digests. It does not need an external source tree. Optional
`--compare-historical-source` adds a source/mirror comparison when the
historical checkout and Paper XXVII release tag are available. The original
files remain the historical authority; the package is a frozen byte mirror.

`validate_release.py` runs the manuscript's 20 finite root validators from
packaged bytes. It gives the unmodified path-bound validators a temporary
layout matching their original receipt paths; it does not rewrite or re-sign
those receipts. Its paper-owned downstream receipt is
[`validation/paper28_release_validation_v1.receipt.json`](validation/paper28_release_validation_v1.receipt.json).
The receipt records local closure verification, not an independent
implementation or a publication identity. The 45 transitive artifacts are
hash/receipt-checked; the 20 manuscript root validators are replayed.

`validate_lean_formalization.py` checks and optionally replays the separate
Lean spine. Its receipt binds the exact Lean sources, toolchain, Lake files,
manifest, README, and validator. It neither imports the finite JSON artifacts
nor changes the finite release receipt.

`stage_mirror.py` documents the bounded selection and refuses to refresh
changed mirror files in place. Paper XXVII inputs retain their separate
authority. Two packaged inputs match bytes at the `paper27-v1.0` tag; the
inherited-section pilot matches its receipt-bound historical bytes, not a
Paper XXVII tag. Nothing here promotes that pilot to a published Paper XXVII
result.

## Finite Dependency Map

    XXVII checkpoint / completion-relation / normalization-accounting interface
        -> finite exact relations and quotient obstruction
        -> boundary generator cover + exact credit composition
        -> five declared rank-five / rank-four return chains
        -> provenance-sensitive GFPC / PEC support and completion
        -> reduced tagged sufficient cover
        -> canonical one/two-segment path alignment

The arrows denote proof dependencies, not discovery chronology.
Lower success is not an input to the menu or lift constructors.

## Exact Composition and Generators

Links in the following tables point to the paper-owned frozen copies. The
manifest maps each copy to its historical authority and digest.

| Result | Artifact stem in results/ | Producer | Validator in validation/ |
|---|---|---|---|
| [Seed closure and quotient obstruction](artifacts/P28_1_SEED_PROJECTOR_RESULTS.md) | paper28_seed_mechanism_catalog_v1 | paper28_project_seed_mechanisms.py | validate_paper28_seed_mechanism_catalog.py |
| [Boundary liftability](artifacts/P28_1B_BOUNDARY_LIFTABILITY_RESULTS.md) | paper28_boundary_liftability_audit_v1 | paper28_audit_boundary_liftability.py | validate_paper28_boundary_liftability_audit.py |
| [Credit composition](artifacts/P28_2_CREDIT_COMPOSITION_RESULTS.md) | paper28_credit_composition_audit_v1 | paper28_audit_credit_composition.py | validate_paper28_credit_composition_audit.py |
| [Generator cover](artifacts/P28_3_BOUNDARY_GENERATOR_RESULTS.md) | paper28_boundary_generator_factorization_v1 | paper28_factor_boundary_generators.py | validate_paper28_boundary_generator_factorization.py |

The seed and generator artifacts are JSON.gz; the boundary and credit
artifacts are JSON. Each has a same-stem `.receipt.json`.
The seed closure contains 11,252 receipts and 13,054 exact compatible pairs.
Generator replay has 123,240 occurrences and 24,355 populated rows.
Accounting composition has 569 realized label pairs; skeleton comparison
has 26. These are not all-\(n\) bounds.

## Five Return Surfaces

The table binds each finite source declaration and both return results.
Declaration files, not the successful rows or anatomy table, fix each domain.

| Surface | Source/domain declaration | Rank-four result | Rank-five result |
|---|---|---|---|
| ext | [source declaration](artifacts/P28_5A_RANK5_SECTION_CANDIDATE.md) | [rank-four result](artifacts/P28_4_SECTION_RETURN_RESULTS.md) | [rank-five result](artifacts/P28_5B_RANK5_SECTION_RETURN_RESULTS.md) |
| cand2 | [source declaration](artifacts/P28_5D_SECOND_RETURN_CANDIDATE.md) | [rank-four result](artifacts/P28_5E_SECOND_RANK4_SECTION_RETURN_RESULTS.md) | [rank-five result](artifacts/P28_5F_SECOND_RANK5_SECTION_RETURN_RESULTS.md) |
| cand3 | [source declaration](artifacts/P28_5H_THIRD_RETURN_CANDIDATE.md) | [rank-four result](artifacts/P28_5I_THIRD_RANK4_SECTION_RETURN_RESULTS.md) | [rank-five result](artifacts/P28_5K_THIRD_RANK5_SECTION_RETURN_RESULTS.md) |
| cand4 | [source declaration](artifacts/P28_5N_FRESH_CONSUMPTION_HOSTILE_SELECTOR.md) | [rank-four result](artifacts/P28_5P_FOURTH_RANK4_SECTION_RETURN_RESULTS.md) | [rank-five result](artifacts/P28_5R_FOURTH_RANK5_SECTION_RETURN_RESULTS.md) |
| cand5 | [source declaration](artifacts/P28_5S_NON_LENGTH_THREE_HOSTILE_SELECTOR.md) | [rank-four result](artifacts/P28_5U_FIFTH_RANK4_SECTION_RETURN_RESULTS.md) | [rank-five result](artifacts/P28_5W_FIFTH_RANK5_SECTION_RETURN_RESULTS.md) |

Evaluation artifact stems (all JSON.gz with same-stem receipt):

| Surface | Rank-four artifact | Rank-five artifact |
|---|---|---|
| ext | paper28_section_return_menu_audit_v1 | paper28_rank5_section_return_evaluation_v1 |
| cand2 | paper28_second_rank4_section_return_evaluation_v1 | paper28_second_rank5_section_return_evaluation_v1 |
| cand3 | paper28_third_rank4_section_return_evaluation_v1 | paper28_third_rank5_section_return_evaluation_v1 |
| cand4 | paper28_fourth_rank4_section_return_evaluation_v1 | paper28_fourth_rank5_section_return_evaluation_v1 |
| cand5 | paper28_fifth_rank4_section_return_evaluation_v1 | paper28_fifth_rank5_section_return_evaluation_v1 |

The corresponding validators are
`validate_paper28_section_return_menu.py`,
`validate_paper28_rank5_section_return.py`, and
`validate_paper28_{second,third,fourth,fifth}_rank{4,5}_section_return.py`
in the validation directory. The latter notation expands to eight existing
files; it is not a shell command. Their owning notes also identify the
separate candidate-construction artifacts and validators.

Finite checksums:

| Surface | Sources at each rank | Rank-five channels / lifts | Rank-four channels / lifts | Rank-four returning lifts |
|---|---:|---:|---:|---:|
| ext | 35 | 87 / 214 | 173 / 4,182 | 2,329 |
| cand2 | 48 | 96 / 195 | 401 / 9,600 | 9,498 |
| cand3 | 36 | 70 / 209 | 172 / 5,239 | 4,208 |
| cand4 | 36 | 107 / 252 | 252 / 6,498 | 5,937 |
| cand5 | 10 | 28 / 62 | 53 / 1,476 | 1,205 |

These surfaces establish existential return, not universal success of lifts.
The rank-four union retains 3,818 failed lifts, five failed channels, and
186 mixed channels.

## Cover and Canonical Alignment

| Result | Owning note | Artifact stem |
|---|---|---|
| GFPC branch | [declaration](artifacts/P28_6U_A3_GENERALIZED_FRESH_PAIR_CARRY_DECLARATION.md) | paper28_fourth_mechanism_schema_declaration_v1 |
| PEC branch | [declaration](artifacts/P28_6U_A2_PAIR_EXTENSION_CARRY_DECLARATION.md) | paper28_third_mechanism_schema_declaration_v1 |
| GFPC completion | [component certificate](artifacts/P28_6U_C3_TAGGED_GFPC_COMPONENT_COMPLETION.md) | paper28_gfpc_component_completion_v1 |
| PEC completion | [component certificate](artifacts/P28_6U_C2_TAGGED_PEC_COMPONENT_COMPLETION.md) | paper28_pec_component_completion_v1 |
| Reduced sufficient cover | [cover certificate](artifacts/P28_6U_D_TAGGED_FIXED_SCOPE_MECHANISM_COVER.md) | paper28_fixed_scope_mechanism_cover_closure_v1 |
| Canonical alignment | [alignment certificate](artifacts/P28_6V_CANONICAL_RETURN_CERTIFICATE_ALIGNMENT.md) | paper28_canonical_return_certificate_alignment_v1 |

All six artifacts are JSON.gz with same-stem receipt. GFPC covers the
83 tagged ext/cand2 contexts; PEC covers the other 82. Their union is
sufficient, not proved minimal. Alignment sends 26,995 macro lifts into
canonical paths (1,528 one-segment and 25,467 two-segment paths), not into
an equal single-exit relation.

Primary immutable artifact digests:

- Cover: `20073b8c096be4085ef28d6199ebe009d3333cd75078e029c003a1b670edb46f`.
- Alignment: `69564521589c51f99dd3e29d96c554be19253ac73741c418ea1fa723c201e6f9`.

The two anchor validators are included among the 20 replayed manuscript
roots. The temporary path alias is a validation compatibility layer for
frozen receipts, not a second source or a redefinition of the artifacts.

## Claim Boundary

The [Lean spine](lean/README.md) checks only the data-independent credit,
existential-composition, and alignment-transport implications. It is a
supplement to this frozen evidence mirror, not another authority for the
finite return or alignment certificates. Its sources are not historical
mirror files and are not included in `dependency-manifest.json`; they instead
have a separate source-addressed formalization receipt under `results/`.

The finite theorems are complete at their declared scopes. Release acceptance
requires the manuscript, PDF, manifest, and local closure receipt to agree; it
does not require an all-\(n\) origin theorem.

The 165 projectable singleton fibers are positive controls only. They
supply no matched negative supply class and cannot discriminate existential
projectable-origin supply from uniform projection. The unresolved all-\(n\)
question is stated in the manuscript without changing the finite relations.

No historical source code, artifact, mathematical contract or published
Paper XXVII payload is modified by this mirror.
