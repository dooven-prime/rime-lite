# Paper XXIX: Canonical Rank-Five Frontier Evidence

This directory is the paper-owned evidence package for
[Paper XXIX](../../papers/paper29/Paper%20XXIX.md). It is self-contained: no
file under the private exploratory synchronizing-automata tree is required to
run either validator or to build the Lean development.

**Status:** version 1.0 release candidate with local closure verification.
This is not an independent mathematical validation of the paper.

## Evidence Layers

The package deliberately separates theorem, finite replay, and formalized
logic.

| Layer | Owned files | What it establishes |
|---|---|---|
| All-$n$ mathematics | the manuscript | The proofs of the canonical spectator-safe and complete raw-frontier classifications |
| Finite exact control | `canonical_frontier.py`, `results/`, and `validation/validate_canonical_frontier.py` | Exact replay of the intrinsic definitions for $5\le n\le12$ |
| Lean spine | `lean/` and `validation/validate_lean_formalization.py` | Data-independent incidence, quotient, counting, and claim-boundary implications |

The retained JSON has status
`FINITE_SANITY_CHECK_NOT_ALL_N_PROOF`. It is a development control, not the
proof of an all-$n$ statement. Conversely, successful Lean elaboration does
not validate the finite JSON or formalize the geometric hole-slide argument.

## Finite Canonical Audit

The standard-library-only checker constructs the canonical defect

$$
d_n(0)=d_n(1)=0,\qquad d_n(q)=q-1\quad(2\le q\le n-1),
$$

and independently checks, at each retained size:

- exact safe-hit reachability in the $2+3$ token/hole system;
- equality of safe-hit reachability with hole-deleted token-order adjacency;
- the missing-image section identities $R_1=\mathrm{id}$ and
  $R_2=C_{n-1}$;
- strong connectivity of one cyclic-order lineage fiber;
- equality of the actual and predicted boundary-incidence spectra;
- the count $5\binom{n-2}{3}$; and
- the five-state coarse-quotient non-descent control.

From the repository root:

```powershell
python experiments/paper29/validation/validate_canonical_frontier.py
```

To regenerate the retained result explicitly:

```powershell
python experiments/paper29/canonical_frontier.py `
  --min-n 5 --max-n 12 `
  --output experiments/paper29/results/canonical_frontier_audit_v1.json
```

The validator compares a fresh replay with the retained JSON byte-for-value;
it does not accept a result merely because its summary counts match.

## Lean Spine

The Lean project freezes the small logical and algebraic spine that is useful
independently of the finite database:

- fused-fiber plus survivor extensionality for an incidence map;
- same-lineage naturality of the spectator quotient;
- the frontier product count after an exact classification equivalence and
  its factor cardinalities are supplied;
- endpoint equivalence through a shared incidence carrier; and
- the boundary between raw existence and typed-origin existence.

It does **not** formalize the canonical all-$n$ reachability theorem, section
returns, hole slides, or typed transfer/projectability. See
[`lean/README.md`](lean/README.md) for the declaration-to-manuscript map.

```powershell
cd experiments/paper29/lean
lake build
cd ../../..
python experiments/paper29/validation/validate_lean_formalization.py --replay
```

The project pins Lean 4.33.0 and Mathlib revision
`db584cd6d46c92f209a44c0f1c829460d327499d`. The `.lake/` directory is local
build state and is not part of this closure.

## Development Closure

`development-manifest.json` binds the manuscript sources, finite checker and
result, Lean sources, lock files, documentation, and validators by SHA-256.
It intentionally remains an inner development-evidence closure and does not
claim a release identity.

```powershell
python experiments/paper29/validation/validate_package.py --replay
```

Without `--replay`, the package validator checks paths, hashes, toolchain and
scope markers only. With `--replay`, it also recomputes the finite artifact and
builds the Lean project.

## Release Closure

`release-manifest.json` is the outer release-candidate manifest. It binds the
canonical manuscript, reader PDF, paper-local bibliography, release
environment, public validator, and the inner development closure. The public
receipt is downstream of that manifest and is excluded from its own closure.

To perform the replay used to create the retained receipt:

```powershell
python experiments/paper29/validation/validate_public_package.py `
  --write-manifest --replay --write-receipt
```

The ordinary read-only check is:

```powershell
python experiments/paper29/validation/validate_public_package.py
```

The receipt uses `LOCAL_CLOSURE_VERIFICATION`. Its replay block has a fixed
schema and cannot be supplied by the receipt itself. Successful validation
does not establish scientific adequacy, theorem truth, or independent review.

## Claim Boundary

The package establishes no transfer membership, entry authorization, typed
handoff, projectable-origin supply, recursive return, credit settlement, or
reset bound. The raw-to-typed bridge remains an open problem in the
manuscript. Private research chronology, abandoned implementation branches,
and historical hostile-audit notes are deliberately excluded: they are
neither required dependencies nor mirrored authority.
