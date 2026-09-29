# Post-Release Anchors

These records are downstream publication metadata. They bind immutable Git
tag bytes and pre-release evidence roots to files actually deposited at
Zenodo. They are not members of the paper-owned pre-release closures and do
not rewrite manifests or receipts that accurately recorded a candidate state.

| Paper release | Anchor |
|---|---|
| Paper XVI v1.0 | [paper16-v1.0.json](paper16-v1.0.json) |
| Paper XXIII v1.0 | [paper23-v1.0.json](paper23-v1.0.json) |
| Paper XXVII v1.0 | [paper27-v1.0.json](paper27-v1.0.json) |
| Paper XXVIII v1.0 | [paper28-v1.0.json](paper28-v1.0.json) |
| Paper XXIX v1.0 | [paper29-v1.0.json](paper29-v1.0.json) |
| Paper XXX v1.0 | [paper30-v1.0.json](paper30-v1.0.json) |

Paper XXVII's tagged README names a `claim-surface-map.json` that was absent
from the release tag. The historical package remains unchanged. Its anchor
records that defect and binds a separately located
[post-release supplement](supplements/paper27-claim-surface-map.v1.json); the
supplement is not represented as original release content.

Create and validate later records with
[`tools/release/post_release_anchor.py`](../../tools/release/post_release_anchor.py).
The fixed procedure and owner/consumer re-pin rule are documented in
[`POST_RELEASE_ANCHOR.md`](../../tools/release/POST_RELEASE_ANCHOR.md).

Publication anchoring proves byte identity only. It does not establish
theorem truth, scientific adequacy, validator independence, or authority for a
consumer to follow a later owner implementation without publishing a new
version and explicit re-pin.
