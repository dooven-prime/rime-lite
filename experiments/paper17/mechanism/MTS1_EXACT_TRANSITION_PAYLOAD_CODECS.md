# MTS-1 Exact Transition Payload Codecs

## Status

Status: `EXACT_TRANSITION_PAYLOAD_CODECS_FROZEN_AWAITING_PRODUCER_PREFLIGHT`.

Execution authority: `NONE`.

This package implements and hostile-tests the three exact sidecar codecs named
by the earlier record-schema registration. It does not modify that historical
registration, replay a source, compute an operator action, or generate a
pair-transition record.

## Shared contract

All three payloads have fixed dimension `211577`, version `1`, strictly
increasing coordinates, and separate domain tags. Public version-1 APIs reject
dimension overrides. Exact numerical inputs are restricted to Python `int`,
`gmpy2.mpz`, and `gmpy2.mpq`; Boolean, floating, NumPy scalar, string, and
implicitly convertible inputs are rejected.

Payload equality means equality of strictly validated canonical uncompressed
bytes. SHA-256 binds and indexes those bytes but does not replace payload
validation or byte comparison.

## Raw signed drive

`RIME-MTS-RAW-DRIVE-V1` encodes a sparse exact rational vector. Negative,
zero, unit, and greater-than-unit mathematical values are permitted; exact
zero entries are omitted from the sparse payload.

## Clipped drive

`RIME-MTS-CLIPPED-DRIVE-V1` encodes a sparse exact rational vector with every
mathematical value in `[0,1]`. Exact zero entries are omitted, so every encoded
entry lies in `(0,1]`. Values outside `[0,1]` are rejected by both encoder and
decoder.

## Touched-target clipping fate

`RIME-MTS-CLIPPING-FATE-V1` encodes one fate for every touched target and no
untouched target. The closed labels are:

```text
LOWER:    u <= 0
INTERIOR: 0 < u < 1
UPPER:    u >= 1
```

The codec validates coordinates and labels. The future producer must establish
that its touched-target universe and each label agree with the exact raw drive;
codec validity alone does not certify that semantic relation.

## Boundary

The hostile suite checks fixed-vector digests, reordering invariance, reduced
rational encoding, domain separation, exact scalar types, registered
dimension, clipping range, fate labels, strict coordinate order, truncation,
trailing bytes, integer minimality, and malformed headers. Passing these tests
closes only the three byte-codec gates. Exact replay, resource preflight,
source-cache production, pair derivation, mechanism classification, and result
closure remain unauthorized.
