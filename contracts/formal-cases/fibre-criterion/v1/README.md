# Fibre Criterion: Lean Case v1 Candidate

This is a narrow, standalone formal Case, not a numbered RIME paper, a SOF
protocol contract, an independent mathematical validation, or a qualification
result. It does not share a proof route, result, or receipt with aigc-lite
Case 003. `FibreCriterion.lean` is an exact-byte copy of the earlier local
source; this package does not modify that source to make another Case pass.

## Fixed Surface

The pinned entry point is `FibreCriterion.lean`, imported by
`AxiomAudit.lean`. The seven declarations under `AgainstSilentPromotion` are:

| Declaration | Exact claim surface |
|---|---|
| `factors_iff_fibre_constant` | For a surjective `q : X -> Y`, total factorization of `h : X -> Z` through `q` iff `h` is constant on every `q`-fibre. |
| `factor_unique` | Two such total factorizations are equal under the same surjectivity and pointwise equations. |
| `hostile_pair_blocks_factorization` | One equal-`q`, unequal-`h` pair rules out a total factorization on the declared full domain. |
| `mul_nonzero_iff_basis_survivor` | For this file's column-pair `Mat2` and locally defined `mul`, the product is nonzero iff one basis-column image survives. |
| `same_boolean_support` | The two registered 2-by-2 matrix pairs have equal Boolean factor support. |
| `different_composition` | Their product nonzeroness differs. |
| `support_does_not_determine_composition` | No total Boolean-support-only function computes product nonzeroness for every local `Mat2` pair. |

`case-lock.json` fixes the toolchain, source hashes, declarations, and expected
axiom output. The manifest does not hash itself or claim an external anchor.
The source's own `import Init` is its only import; no Lake or Mathlib project
is required. The tested compiler is Lean 4.33.0, release commit
`d8b18978322de05a8f3dba51ef03cf5461676c17`.

From this directory, with that toolchain active, run:

```text
lean -o OUTPUT_DIR/FibreCriterion.olean FibreCriterion.lean
LEAN_PATH=OUTPUT_DIR lean AxiomAudit.lean
```

Set `OUTPUT_DIR` to a scratch directory outside this package. On Windows,
set `LEAN_PATH` in the shell environment before the second command. Compare
the seven `#print axioms` lines with `case-lock.json`; a compiler exit code
alone does not check the expected axiom surface or proposition correspondence.

## Assumption Audit

The source declares no local `axiom`, `opaque`, `unsafe`, `sorry`, or
`native_decide`. All theorem parameters and hypotheses appear in their Lean
signatures. `factors_iff_fibre_constant` uses classical choice to select a
representative of each fibre. The remaining expected axioms are Lean's
standard `Quot.sound` and `propext`, as reported per declaration in the lock.
No custom axiom is allowed. An imported definition, changed local matrix
operation, or additional axiom requires a new case version, not a silent edit.

## Negative Boundaries

- The factorization result assumes surjectivity. Without it, the same test
  determines a map only on `q(X)`, not on arbitrary points of `Y`.
- The hostile pair refutes one proposed full-domain factorization. It does
  not refute every refinement, restricted domain, relation-valued output, or
  probabilistic model.
- `Mat2` is a local integer column-pair representation. The source does not
  import a general matrix/image/kernel library or prove the all-dimensional
  formula `im(B) not-subset ker(A)` in such a library.
- The example distinguishes Boolean support from a 2-by-2 product. It proves
  no all-depth routed-product theorem, dynamic closure, neuroscience claim,
  or SOF protocol admission.
- A successful Lean compile checks these declarations against the pinned
  compiler and imported `Init`; it does not establish the scientific adequacy
  of an application, independent validation, current-use authority, or any
  result for aigc-lite Case 003.
