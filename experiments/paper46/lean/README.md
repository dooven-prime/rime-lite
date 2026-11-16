# Paper XLVI Lean Companion

This is the byte-preserving RSR-2 proof extraction for Paper XLVI. It pins
Lean `v4.33.0` and uses core libraries only. `lake-manifest.json` has no
external packages. The proof modules do not import Paper XLV or its
representation companion.

From this directory:

```text
lake --no-cache build
lake env lean RSR2/AxiomAudit.lean
```

The enclosing [replay entry](../validation/replay.py) additionally checks
the candidate's exact source inventory and rejects unexpected audit axioms
or incomplete audit output. If the default launcher cannot find the
toolchain executable, pass that executable with `--lake`.

See the [theorem-to-source map](../FORMALIZATION_MAP.md)
for statement-level coverage. The audit has 223 explicitly selected targets,
including transitive axiom dependencies; this is not a count of all lemmas.
The allowed axiom set is `propext`, `Classical.choice`, `Quot.sound`.
No Mathlib cache or existing `.lake` directory was copied from exploration.

The arbitrary unordered-partition presentation uses classical choice. Its
existence theorem is not an extracted partition compiler for undecidable
input relations. Word execution is executable. The manuscript separately
owns the Bell terminology, information lower bound for partition diameter
and the stated mathematical consequences not exported as Lean declarations.
