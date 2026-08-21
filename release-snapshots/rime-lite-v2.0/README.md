# RIME v2.0 Byte Snapshot

This directory preserves the exact bytes required to validate the published
RIME v2.0 Registry, selected Paper II--III figure inputs, and Paper XII--XIV
closures across Windows and LF-normalizing checkouts.

The snapshot is an explicit historical input. It is not a regenerated result,
and it does not change the published v2.0 tag or receipt bytes. Result and
receipt payloads retain their recorded materialized bytes. Historical
validator payloads are taken from the v2.0 release closure, while v2.0
contract payloads are selected by the SHA-256 values recorded in the
historical receipts. The manifest records the digest and origin of every
payload.

Snapshot manifest v1.4 retains the Paper II producer materialization, the
nine-file Paper III source closure, the frozen Paper IV registration, and the
Paper XI v1.1 census. It also adds the three-file source closure declared by
the Paper I figure record. Every added payload exactly matches its previously
recorded digest. Current source files, observations, and historical Registry
artifacts remain unchanged.

The snapshot excludes v2.1 candidate directories and independent research
drafts. A snapshot match proves byte identity for the listed historical
payload; it does not establish scientific adequacy or validator independence.

Use `manifest.json` as the source-addressed index. Consumers must verify the
snapshot payload digest against the declared `digest` before using it.
