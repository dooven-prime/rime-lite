# HAL-to-Zenodo Numbered Migration (2026-11)

## Reason and status

The author received an HAL eligibility clarification request for
`hal-05805297v1` and reports the same issue for the recent unnumbered
submissions. The author has answered without asserting an institutional
affiliation. A submitted HAL identifier is not evidence of an accepted or
publicly retrievable record. Do not describe these deposits as published
unless their public versions are independently checked.

Zenodo is the intended primary archive for new numbered editions. The
numbered editions are new publication objects, not a retroactive renaming of
the HAL submissions. The historical source, PDF, Git commit/tag, Lean
companion, references, and completed CI remain traceable at their existing
identities. No historical byte is rewritten to make an old receipt describe
a later publication.

## Dependency order and ownership

| New edition | Historical manuscript | Mathematical dependency | Existing companion |
|---|---|---|---|
| Paper XLI | `papers/unnumbered/circular_coalescence_counts/` | Paper XXXIX supplies the event-anchored interpretation; XLI proves its own circular enumeration | `experiments/registered_absorption_chains/` |
| Paper XLII | `papers/unnumbered/proper_arc_registered_summaries/` | proper-arc extension of XLI's fixed-pair object | `experiments/proper_arc_registered_summaries/` |
| Paper XLIII | `papers/unnumbered/future_event_minimal_quotient/` | imports XLI's full-summary count and placement control; no theorem premise from XLII | `experiments/future_event_minimal_quotient/` |
| Paper XLIV | `papers/unnumbered/fusion_log_compression/` | compares complete logs with the registered summaries of XLI and XLII | `experiments/fusion_log_compression/` |

This is publication order, not a blanket implication chain. Record exact
Theorem, Corollary, and Equation references separately for each edition.
Keep local result numbering stable where possible; a cross-paper citation
must name the owning edition and the result number valid in that edition.

## File and claim migration

1. Preserve `papers/unnumbered/` as the historical source. Its submitted
   identifiers, HAL reader PDFs, source hashes, and Git anchors remain
   historical. Do not edit these files to assert Zenodo publication.
2. Create one `papers/paperN/` directory per numbered edition. Copy the
   mathematical manuscript, then edit only that copy for title-page
   identity, local exposition, numbered-paper layout, bibliography, and
   publication-specific citations. The paper-local `references-v1.bib`
   must be checked entry by entry against primary publication metadata.
3. Create `experiments/paperN/` as a versioned publication index. It points
   to the existing proof owner and source identity; it must not copy or
   silently alter an already accepted Lean or finite-control input. State
   exactly which new manuscript results each inherited control covers.
4. Keep proof status, finite replay status, and publication status separate.
   The registered-absorption Lean companion checks the exact generated
   summary count for `n>=2`, but not the asymptotic growth corollary. A
   numbered edition does not enlarge that formalized theorem surface.
5. Keep old HAL submission IDs and new Zenodo DOIs in distinct fields or
   documents. An inaccessible or unmoderated HAL ID is not a public citation
   or proof source. The new edition cites the owning published DOI only after
   that DOI is live; earlier dependency citations must remain exact.

## Candidate and release gates

For each edition, check the copied theorem statements against the historical
source, audit every internal theorem/equation reference, and audit every
cross-paper citation against the cited version. Build the reader PDF with
`papers/tex/build.py` in an isolated `output/tex/` directory; inspect the
pages, bibliography, equations, tables, links, and build log. Replay the
declared finite and Lean validators from their unchanged owners. Pin the new
manuscript, bibliography, PDF, evidence map, and validation entry point by
exact bytes in a candidate manifest and read-only receipt.

Before a content tag, status is `RELEASE_CANDIDATE` and
`release_identity_claimed` is false. Commit, tag, push, or upload only with
the author's explicit instruction. Freeze content first; then deposit the
exact numbered edition to Zenodo. Record the DOI and deposited-file facts
in a downstream post-release anchor and preserve tag ancestry on merge.
Do not backfill publication facts into the tagged candidate or old HAL
source. A failed replay, unresolved citation, PDF defect, or source-byte
mismatch blocks release rather than being translated into a PASS.

## Pilot acceptance

Paper XLI is the pilot. Its candidate package should demonstrate a checked
numbered manuscript, paper-local bibliography, reader PDF, explicit
historical-source/companion map, bounded BFS replay, Lean closure and axiom
audit, and a fail-closed candidate manifest/receipt. Its dedicated CI
must check the inherited byte identity before building the same Lean
proof owner and must retain a separate runner receipt. A local receipt
does not stand in for an actual GitHub CI run. No DOI, publication
anchor, or HAL acceptance is implied by completing this local pilot.
