# RIME v2.0 Byte Snapshot

This directory preserves the exact bytes required to validate the published
RIME v2.0 Paper XII--XIV closure across Windows and LF-normalizing checkouts.

The snapshot is an explicit historical input. It is not a regenerated result,
and it does not change the published v2.0 tag or receipt bytes. Result and
receipt payloads retain their recorded materialized bytes. Historical
validator payloads are taken from the v2.0 release closure, while v2.0
contract payloads are selected by the SHA-256 values recorded in the
historical receipts. The manifest records the digest and origin of every
payload.

The snapshot excludes v2.1 candidate directories and independent research
drafts. A snapshot match proves byte identity for the listed historical
payload; it does not establish scientific adequacy or validator independence.

Use `manifest.json` as the source-addressed index. Consumers must verify the
snapshot payload digest against the declared `digest` before using it.
