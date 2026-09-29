# Post-Release Anchor

A paper release has two separate records:

1. the immutable pre-release manifest and validation receipt; and
2. a downstream post-release anchor written only after the Git tag and
   external deposit exist.

The second record does not rewrite the first. A manifest that truthfully said
`RELEASE_CANDIDATE` at the release-content commit remains frozen in that state.
The post-release anchor records that those exact tagged bytes were published.

The release identity tuple is exact: `PAPER<N>`, `<version>`, and
`paper<N>-v<version>` must agree. A branch, raw commit, differently numbered
paper, or differently versioned tag cannot stand in for that identity.

## Fixed Action

Run the following sequence after publication:

1. resolve the annotated or lightweight release tag to its target commit;
2. read the manifest, receipt, and deposited source files through `tag:path`;
3. download each declared Zenodo file and compare exact SHA-256 and size;
4. write `post-release-anchor.v1.json` outside the pre-release closure;
5. validate the anchor locally and with `--check-remote`;
6. commit the anchor as a post-release metadata commit.

Example:

```bash
python tools/release/post_release_anchor.py create \
  --paper PAPER28 --version 1.0 --tag paper28-v1.0 \
  --doi 10.5281/zenodo.22980858 \
  --evidence release-manifest=experiments/paper28/release-manifest.json \
  --evidence validation-receipt=experiments/paper28/results/paper28_public_package_v1.validation-receipt.json \
  --deposit paper28_arxiv.pdf=papers/paper28/paper28_arxiv.pdf \
  --output docs/release-anchors/paper28-v1.0.json

python tools/release/post_release_anchor.py validate \
  docs/release-anchors/paper28-v1.0.json --check-remote
```

The anchor must not contain itself, and neither the release manifest nor its
receipt may depend on the anchor.

## Owner and Consumer Versions

An owning paper publishes a new version when it changes an owned interface,
definition, theorem surface, or normative source byte. A consuming paper then
publishes its own new version and re-pins the owner release and exact imported
bytes. It is forbidden to edit a shared implementation in place and let
multiple historical receipts silently follow current HEAD.

Copying exact owner bytes into a paper-owned mirror is permitted. The mirror
must record its owner release identity and digest. Equality of current paths is
not a substitute for that versioned binding.

## Authority Boundary

The anchor proves only that the declared tag, evidence roots, and deposited
files agree at byte level. It does not prove theorem truth, scientific
adequacy, validator independence, or that a PDF-only DOI anchors unuploaded
code and evidence.
