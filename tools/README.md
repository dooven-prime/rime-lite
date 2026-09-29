# Release Verification Tools

The tools in this directory provide read-only checks for published or staged
RIME release material. They do not rebuild, promote, repair, or re-sign tracked
artifacts.

## Available Checks

| Command | Checks |
|---------|--------|
| `python tools/validate_release_snapshot.py release-snapshots/rime-lite-v2.0/manifest.json` | Exact bytes and paths recorded by a historical release snapshot |
| `python tools/release/validate_evidence_graph.py` | Raw-byte receipt references, receipt-cycle exclusion, and the artifact-to-receipt direction for current SOFRS, SOFAUDIT, and SOFAction receipts |
| `python tools/release/validate_release_manifest.py PATH` | Release identity, content commit, PDF bytes, declared validators, figures, and result bindings in a paper release manifest |
| `python tools/release/verify_zenodo_anchor.py --doi DOI --local FILE --remote-name NAME` | Equality between one local file and the named file actually deposited in a Zenodo record |
| `python tools/release/post_release_anchor.py create ...` | Additive post-release binding from immutable tag bytes and evidence roots to actual Zenodo deposit bytes |
| `python tools/release/post_release_anchor.py validate ANCHOR [--check-remote]` | Tag/evidence/deposit verification for a stored post-release anchor |
| `python tools/release/audit_paper16_v1_materialization.py` | Release- and path-specific audit of the frozen Paper XVI v1.0 LF/CRLF materialization mismatch; reports explanation rather than closure PASS |

Use `--strict-snapshot` with `validate_release_manifest.py` to check all
declared evidence digests, including private submission metadata when it is
available locally.

## Authority Boundary

These checks establish only their declared integrity properties:

- Snapshot verification binds the files listed by that snapshot; it does not
  extend the snapshot to later files.
- Evidence-graph verification is local closure verification. A receipt cannot
  authenticate its own validator, and a different digest alone does not prove
  implementation, owner, or execution-environment independence.
- Manifest validation binds the declared release closure. It does not prove
  scientific adequacy or the truth of every included claim.
- A Git commit, signed tag, or DOI anchors only the bytes it actually covers.
  A DOI deposit containing only a PDF does not anchor unuploaded artifacts,
  producers, validators, or receipts.
- A historical materialization audit can explain a frozen byte mismatch but
  cannot repair, re-sign, or retroactively validate the original closure.
- A post-release anchor is downstream metadata. It records publication without
  rewriting a candidate manifest or receipt already bound by a release tag.
- An owner correction requires a new owner version. Every consumer must then
  publish its own new version and re-pin the owner release and exact imported
  bytes; shared files are never silently updated in place.

The complete post-release procedure and owner/consumer re-pin rule are defined
in [`release/POST_RELEASE_ANCHOR.md`](release/POST_RELEASE_ANCHOR.md).

Verification must leave the tracked repository unchanged. Rebuild and replay
write to scratch or candidate staging locations; only an explicit paper-owned
promotion operation may update tracked release paths.
