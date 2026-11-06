# Reproducing M1-M3

## Inputs

Use Python 3.10+ (standard library only), Git, and elan with
`leanprover/lean4:v4.33.0`. For a new installation:

```text
elan toolchain install leanprover/lean4:v4.33.0
```

Run all following Python commands from this package directory:

```text
python -B validation/replay.py --verify-inputs-only
python -B -m unittest discover -s validation -p test_replay.py
python -B validation/replay.py --cache
```

Lake obtains external source dependencies at the exact revisions in
`lean/lake-manifest.json`. The `--cache` step requests the official
Mathlib compiled cache. It does not replace the local proof build or the
separate axiom audit. A subsequent replay can omit `--cache`.

The launcher checks the actual Lean runtime commit, not just its alias.
On this host the short `v4.33.0` alias was broken, while the canonical
elan toolchain installation was intact. The launcher prefers that canonical
installation without changing global settings. An explicit binary can be
selected with:

```text
python -B validation/replay.py --lake /absolute/path/to/pinned/toolchain/bin/lake
```

On Windows supply the corresponding absolute `lake.exe` path.

## Saved Output

To retain a new run:

```text
python -B validation/replay.py --report results/my-m3-replay.json
```

An existing report is never overwritten. The report binds the upstream pin
and proof manifest hashes, runtime version, completion time, public
signatures and the 18 targeted transitive axiom sets. A nonzero command,
missing target, input drift or an axiom outside the declared standard set
fails the gate. The validator unit tests exercise drift, inventory,
path-escape, missing/duplicate-target and unsafe-axiom rejection.

The saved `results/m3-replay.v1.json` is a local warm replay. Its Mathlib
artifacts were copied into this package's own ignored `.lake/` directory
from an existing locked checkout. It does not document independent
dependency download or a clean-machine cold replay.

## Vendored Source Provenance

`upstream-pin.v1.json` identifies all 51 original Lean blobs. They were
extracted without modification from commit
`050cf8ec11e3db263830b46ea95e4062b8e08869` of
`https://github.com/dooven-prime/rime-lite`, under
`experiments/registered_absorption_chains/lean`.

That directory's Lean files only are vendored: no old build cache,
validation receipt, toolchain override or release manifest was imported as
this package's evidence. A reader can independently compare each vendored
file with the corresponding Git blob. No surrounding checkout is needed
to run this package.

## Checked Scope

The kernel-checked endpoints and budgets are listed in
`M3_THEOREM_MAP.md`. The manifest binds proof inputs, not a publication
identity. Documentation and reports are downstream descriptions; the
owning Lean declarations determine the formalized statements.
