# MTS-1 Scoped Execution Amendment

## Status

Status: `SCOPED_EXECUTION_SEMANTICS_FROZEN_AWAITING_IMPLEMENTATION_PREFLIGHT`.

Execution authority: `NONE`.

This amendment fixes three execution semantics before any pair-resolved
mechanism payload is generated. It does not authorize the 153-source replay,
create the 459 source-transition cache records, or classify any mechanism.

## 1. Residual quadrants are phenotypes

For exact rational vectors `r_raw` and `r_clip`, the four registered labels

```text
RAW_ZERO__CLIP_ZERO
RAW_ZERO__CLIP_NONZERO
RAW_NONZERO__CLIP_ZERO
RAW_NONZERO__CLIP_NONZERO
```

record only whether each vector is exactly zero. They are not mechanism
labels, and no one-to-one interpretation table is permitted.

Any model-layer interpretation must use a frozen conjunction. In particular:

- `RAW_NONZERO__CLIP_NONZERO` does not establish carrier-only separation. If
  `r_corr = r_clip - r_raw` is nonzero, clipping changed the coarse residual.
- `RAW_ZERO__CLIP_ZERO` does not establish coarse pushforward annihilation
  unless registered state or raw-drive geometry independently records a
  nonzero difference.
- clipping creation, elimination, modification, and unchanged persistence are
  separate exact predicates defined in the machine amendment;
- safe forgetting additionally requires a defining persistent-safe record,
  current-observation equality, successor compatibility, and nontrivial
  registered geometry.

These predicates localize exact behavior inside the frozen model. They do not
establish biological causality, environmental adjudication, or functional
necessity.

## 2. Microscopic-state identity

Paper XVII recorded a SHA-256 digest of sparse ASCII rows

```text
coordinate<TAB>numerator<TAB>denominator<LF>
```

in ascending coordinate order. The state dictionaries were sparse and omitted
zero values. This historical digest remains an ancestry-compatibility gate. It
has no domain tag and is not promoted to the canonical MTS-1 state identity.

MTS-1 uses `RIME-MTS-MICROSTATE-V1`, an uncompressed binary payload containing:

1. the domain tag `RIME-MTS-MICROSTATE-V1\0`;
2. a big-endian format version, registered dimension, and nonzero count;
3. strictly increasing coordinates;
4. a sign code and minimal unsigned big-endian numerator magnitude;
5. a positive minimal unsigned big-endian denominator;
6. reduced rational values, with zero coordinates omitted.

The registered microscopic dimension is `211577`. SHA-256 is computed over
the complete uncompressed canonical payload, including its domain tag. The
payload bytes define semantic identity; the digest binds and indexes those
bytes. A digest comparison alone is not an exact-payload comparison.

The theorem-facing v1 encoder accepts only Python `int`, `gmpy2.mpz`, and
`gmpy2.mpq`. It rejects `bool`, floating-point values, NumPy scalars, strings,
and other undeclared convertible objects. It rejects every dimension other
than `211577`. A strict decoder validates the complete canonical grammar,
including the declared nonzero count and absence of trailing bytes.

For each future replayed state, admission requires the bound exact producer
context, exact observation-byte equality with the Paper XVII sidecar, a match
to the historical compatibility hash, and successful generation of the new
canonical payload. A result validator must replay the state or compare retained
canonical bytes when it claims exact state equality. It may not infer equality
from two digest strings alone.

## 3. Pair orientation

Each registered unordered pair receives one byte-level orientation:

```text
source_a = min(source_id_1, source_id_2)
source_b = max(source_id_1, source_id_2)
delta    = value(source_a) - value(source_b)
```

This orientation applies to `delta_x`, `delta_u`, `delta_c`, `r_raw`,
`r_clip`, `r_corr`, coordinatewise difference payloads, and successor
residuals. The `3 x 3` clipping-fate table uses the fate of `source_a` as its
row and the fate of `source_b` as its column. Reversing a pair before
serialization is forbidden.

## 4. Remaining gates

Execution remains unauthorized until the exact mechanism producer, cache and
pair-record schemas, resource caps, storage policy, result validator, receipt
contract, and nontrivial contrast classification are source-bound and pass
static preflight.
