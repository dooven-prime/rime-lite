# Lean: R/G/T bounded history certificates

Supporting library of the Paper XL C1/RGT companion, not a separate paper.
It imports only the bundled `Std`
library, not the Proper-arc, future-event, Fusion-log, or origin-descent Lean
projects. Its role is to formalize finite complete-state history replacement
and its R/G/T rejection consequences, not the whole Paper XL checker.

## Reproduce

The pin is `leanprover/lean4:v4.33.0` in `lean-toolchain`. The Lake manifest
contains no external packages; there is no Mathlib dependency. From this
directory run:

```bash
lake build
lake env lean Checks.lean
lake env lean ObservationCompressionChecks.lean
lake env lean AxiomAudit.lean
```

`lake build` compiles the proof modules and root import. The check commands
elaborate boundary examples, and the last prints the axiom
dependencies of the listed public statements. These commands passed on
2026-11-04 for the original package. Re-run them after local changes; this is
a local verification, not an immutable release receipt.

## Public interfaces

| Module | Main declarations |
|--------|-------------------|
| `FiniteHistory` | `loop_erasure`, `FiniteSystem`, `bounded_replacement_le`, `bounded_pair` |
| `Certificates` | `CheckSpec`, `bounded_read_failure_iff`, `bounded_guard_failure_iff`, `bounded_successor_failure_iff`, `bounded_successor_certificate`, `empty_domain` |
| `LogEncoding` | `logCodes_length`, `mem_logCodes`, `CompleteLogEncoding`, and its bounded-replacement / R/G/T corollaries |
| `ObservationCompression` | `CompleteLogEndpointCompression`, `CheckSpecObservationFactorization`, and R/G/T failure certificates transported through a complete-log/endpoint-preserving compressor |

Inside `FiniteSystem`, `cover` need only contain every reachable complete
state, with no duplicate-free requirement. Its length is necessarily positive.
`CheckSpec.domain` restricts fiber tests to the application domain. Candidate,
report and guard values depend only on complete states, and each command has
one fixed raw letter. No hypothesis that R/G/T already hold is used to obtain
a failure certificate.

`CompleteLogEncoding` is an explicit premise: it supplies encode/decode, all
reachable code widths, and recovery of the full reachable state. The declared
circular Paper XL Lean model instantiates it in the separate
[Paper XL companion](../../paper40/lean/README.md). This package itself remains
the generic interface and does not claim correspondence with frozen Python
bytes. That companion proves any consumer on its complete circular Lean state
factors through the exact `(ordered event list, terminal atom-site map)`
observation. For the C1-compatible circular fragment, the Paper XL companion
supplies the same-state compressor and `C1QuadraticRGT` transports its bound
to complete-state R/G/T certificates, including lossy candidate maps on that
state. Independently defined lossy projections and frozen Python bytes remain
outside the correspondence. The interface is not a custom axiom: all public
implications quantify over it as input data.

## Checks and logical boundary

`Checks.lean` covers an empty alphabet, duplicate cover entries, a sharp
four-state `N-1` example, each kind of rejection, a common-letter T extension,
an empty registered domain, small exact code counts, and a concrete singleton
codec. It also exhibits T failure while all consumer reports and guards are
constant under every suffix. These examples are not a second implementation
of the application semantics or a substitute for the general proofs.

The public theorem axiom queries report subsets of
`[propext, Classical.choice, Quot.sound]`; `empty_domain` uses none. There are
no `sorry`, custom axiom declarations, or native-evaluation proof shortcuts.
Classical reasoning is used for existential loop erasure and extraction of
counterexamples from failed universal clauses. The package does not provide
an executable shortest-pair finder or a checker decision procedure.

The exact mathematical statements and remaining application obligations are
in [the theorem note](../RGT_BOUNDED_HISTORY_CERTIFICATES.md).
