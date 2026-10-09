# Paper XXXVIII: Partial Return-Budget Algebraic Spine

**Scope:** selected data-independent algebraic results, not a complete Lean
proof of the all-g geometric theorem. The manuscript remains the theorem
authority. The finite JSON database is not imported into Lean.

The compiler is Lean 4.33.0. Mathlib is pinned in the lock file to
`db584cd6d46c92f209a44c0f1c829460d327499d`.
The package imports no Paper XXXVII Lean sources. A locally shared `.lake`
dependency cache is an ignored runtime convenience, not a paper dependency.
A fresh build can resolve the declared Mathlib dependencies from the lock.

## Coverage

| Manuscript role | Checked formal result | External boundary |
|---|---|---|
| Theorem 3.1, algebraic part | Exact positive product layers; retained initial factor; cumulative union and member law | Actual coordinate action, uniform guards, and product-to-raw-witness construction are not formalized |
| Lemmas 4.1--4.3 | Phase aggregate closure, finite positive generation, left-stable blocks, no premature stall, cumulative cardinal growth | The finite ambient group is the generated group; aggregate and initial-set hypotheses are explicit |
| Theorem 4.4, algebraic part | Saturation at the subgroup index; words with fewer extra factors than the index; total charged factor count at most 24 in a subgroup of $S_5$ | The phase subgroup's order-five hypothesis is supplied; applying the bound to actual guarded paths uses the manuscript's realization theorem |
| Theorem 5.1, finite group part | Distinct size-five rotation/reflection first layers in $D_{10}$; second cumulative layers both full; distinct fixed survivor reads | No all-g circular embedding or source-addressed raw path is proved by this finite control |

`ReturnLayers.lean` uses index `n` for the number of additional factors
after `B`, so `n = 0` represents one charged return. Its product-word
witness is written in algebraic multiplication order, with the initial
factor on the right. It is not a chronological raw label word. Neither
that witness nor the product-to-path construction is claimed unique.

`Saturation.lean` works on finite sets of group elements. Each newly added
element supplies an entire left-phase block. No normality or normalizer
hypothesis is imposed, and no deterministic left update on right cosets
is constructed. The theorem is cumulative: no exact-24 padding or sharp
diameter is asserted. Finite inverses are used only in algebraic closure,
not as uncharged physical return steps.

`InitialLayerControl.lean` uses Mathlib's abstract `DihedralGroup 5`.
The sets correspond to $H$ and $H\tau$, not to a quotient group. The
three remaining fixed five-position reads differ even though their
one-return set sizes agree. This is not a new finite census.

## Verification

Static source/digest/coverage verification:

~~~powershell
python -B experiments/paper38/validation/validate_lean_formalization.py
~~~

Compiler and all 30 declaration axiom audits:

~~~powershell
python -B experiments/paper38/validation/validate_lean_formalization.py --replay
~~~

After intentional edits, compile and audit before refreshing digests:

~~~powershell
python -B experiments/paper38/validation/validate_lean_formalization.py --seal
python -B experiments/paper38/seal_manifest.py
~~~

Only `propext`, `Classical.choice`, and `Quot.sound` may appear in the
axiom footprint. Source scanning and compiler output both enforce the
boundary. Ordinary kernel-checked `decide` evaluates fixed finite facts;
untrusted proof shortcuts and project axioms are prohibited.

## Excluded Scope

No concrete normalized circular guard, actual label/lane selection,
same-representative raw path realization, full survivor restriction
theorem, all-g reflection-location family, original-letter $24n$ bound,
Appendix A control words, or finite JSON catalogue is formalized here.
The paused B0 audit, independent forest consumer, typed transfer, POS,
recursive credit settlement, and reset bounds are not inputs or conclusions.
