# History-Preserving Quadratic Normal Forms for Circular Coalescence

**Status:** HAL v1 reader candidate. No HAL identifier, DOI, release tag or
journal submission is claimed.

## Reader

- [Reader PDF](hal-v1/Chen_History_Preserving_Quadratic_Normal_Forms_HAL_preprint.pdf)
- [Canonical manuscript](MANUSCRIPT.md) and [bibliography](references.bib)
- [Reader build](build_hal.py) and [local configuration](hal-reader.json):
  from the repository root, run
  `python -B papers/unnumbered/fusion_log_compression/build_hal.py`.
  The wrapper uses the [shared HAL reader profile](../../tex/HAL_READER.md);
  generated TeX stays under `output/tex/`.

The manuscript proves joint reachability of complete effective-fusion logs
and compatible literal endpoints from arbitrary named-packet starts. It
constructs quadratic-length representatives, counts the log/endpoint and
endpoint fibres, and proves the exact optimum for one specified all-right
history. That target is not asserted to maximize the cost over all histories.

## Finite Checks

The [bounded controls](../../../experiments/fusion_log_compression/controls/README.md)
replay complete log/endpoint objects from singleton starts for `n=3..6`
and 36 arbitrary-start layouts over the same sizes. They also check the
specified optimum and its excess-cost ledger on finite instances. These
computations are consistency checks; the all-parameter results are proved
in the manuscript. The partial Lean development is separate from this
reader candidate and is not a machine proof of the full paper.

The HAL deposit identity remains pending until moderation completes.

## Source Snapshot

The [v1.0 source manifest](source-manifest.v1.json) binds this manuscript,
bibliography, reader PDF, shared build profile and narrow finite controls.
From the repository root, run
`python -B papers/unnumbered/fusion_log_compression/verify_snapshot.py`.
The validator checks exact bytes and regenerates both bounded control results
in a temporary directory. After the source tag exists, add `--check-tag` to
compare its contents with the local manifest. The source snapshot is distinct
from the later HAL deposit identity.
