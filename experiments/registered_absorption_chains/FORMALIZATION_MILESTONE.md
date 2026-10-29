# End-to-End Lean Formalization Milestone

Local verification record, 2026-10-29 (Asia/Shanghai). This is a later
companion to [HAL preprint hal-05837829v1](https://hal.science/hal-05837829v1),
not a claim that the Lean sources were part of that deposit. It records a
compiled exact-count spine for generated registered summaries, not a machine
proof of every result in the preprint.

## Source Identity

| Item | Exact identity |
| --- | --- |
| Lean | 4.33.0, release commit `d8b18978322de05a8f3dba51ef03cf5461676c17` (`x86_64-w64-windows-gnu`) |
| Mathlib checkout | `db584cd6d46c92f209a44c0f1c829460d327499d` |
| Proof-development base HEAD | `a7b30dd68ea1637368dee3c88df6185bb38b0a82` |
| Packaging worktree base | `472cb9b023c2f12353ec9f6ced80eb188722eb15` (`origin/master` at import) |
| Exact source closure | [`lean/formalization-manifest.v1.json`](lean/formalization-manifest.v1.json), SHA-256 `2ecdac2a895ba158f1b938647bd5ca002df9dadc9dcaab76e0eac390e71c0dbb` |
| Source digests | The manifest's `source_sha256` object lists the path and SHA-256 digest of **each of the 56 bound files**. The manifest digest above pins that entire mapping; the validator checks both the complete inventory and every file's bytes. |

The proof-development HEAD did not contain the entire formalization. The
manifest-bound sources were imported unchanged into a separate worktree from
the packaging base above. The manifest's 56 path-to-digest entries, rather
than either base commit alone, identify the proof bytes. This later GitHub
companion is not part of the HAL v1 deposit and is not a numbered RIME release.

## End-to-End Claim

The exact theorem signature in
[`TwoAtomSummaryCount.lean`](lean/RegisteredAbsorptionChains/TwoAtomSummaryCount.lean)
is:

```lean
theorem card_actualRegisteredSummaries_piecewise
    {n : ℕ} [NeZero n] (hn : 2 ≤ n) :
    Nat.card (ActualRegisteredSummaries n) =
      if n = 2 then 4 else
        n * ((2 * (n - 2)).choose (n - 2) +
          2 * ∑ b : Fin (n - 2),
            3 ^ b.1 * (2 * (n - 2) - (b.1 + 1)).choose
              ((n - 2) - (b.1 + 1)))
```

`ActualRegisteredSummaries n` is the subtype defined by actual singleton-seed
`p,d` histories with a registered selected event. It is not the type of all
well-formed ambient records. The proof's two branches have distinct owners:

1. For `n >= 3`, `realize_clean_code` constructs actual words for all codes;
   `actual_chain_unique_code` and `codeEquivReachableSelectedChain` identify
   exactly the generated chain range. `actualFixedChainPlacementEquiv` and
   `fullCarrierFixedChainPlacementEquiv` classify the positive-complement and
   full-carrier placement fibers. `actual_registered_origin_unique` is required
   when `actualSummaryCodeFiberEquiv` and `actualSummaryFiniteParamsEquiv`
   promote placements to **complete** origin-bearing summaries.
   `card_actualRegisteredSummaries_code_sum` counts those actual fibers;
   `codeLastCheckpoint_weighted_sum` and
   `card_actualRegisteredSummaries_closed` give the displayed closed formula.
2. For `n = 2`, `actualRegisteredSummaries_two_complete` proves literal-word
   closure using two pre-registration states and four registered states.
   `actualRegisteredSummariesTwoProductEquiv` identifies the four actual
   summaries with `Bool × ZMod 2`; `card_actualRegisteredSummaries_two` supplies
   the value `4`. The added
   `actualRegisteredSummariesTwoProduct_origin` lemma proves that the Boolean
   coordinate is the ordered `d` versus `pd` registration origin, and
   `actualRegisteredSummariesTwoProduct_phase` proves that the `ZMod 2`
   coordinate is exactly the unique site occupied by the full carrier.

The theorem joins these branches; it does not identify the two `n = 2`
origins or import the `n >= 3` origin-uniqueness lemma into that case. The
preprint's asymptotic exponential growth rate is outside this Lean closure.

## Axiom And Replay Audit

[`AxiomAudit.lean`](lean/RegisteredAbsorptionChains/AxiomAudit.lean) invokes
`#print axioms` on named declarations spanning the local move and source-order
lemmas, actual clean-code and chain-range constructions, fixed-chain
placement equivalences, origin classification, finite counts, the two new
semantic projections, and the piecewise endpoint. The
[`validator`](lean/validate_lean_package.py) performs all of the following:

1. Requires the declared package status and exact 56-file source inventory.
2. Recomputes SHA-256 for every bound file and compares it with the manifest.
3. Runs `lake build` and then `lake env lean RegisteredAbsorptionChains/AxiomAudit.lean`.
4. Requires the exact audited declaration-name set, with no missing, extra,
   or duplicate axiom rows.
5. Requires every reported axiom to lie in the explicit allowed set
   `{propext, Classical.choice, Quot.sound}`. In particular, `sorryAx` or an
   unlisted axiom causes failure.

The earlier baseline contained **260** audited declarations. The two public
`n = 2` projection lemmas raise the current verified snapshot to **262**;
calling this current snapshot a 260-item audit would omit those interfaces.
The audit is about the listed Lean declarations and their axioms, not an
independent review of the manuscript's full mathematical scope.

Reproduce from `experiments/registered_absorption_chains/lean` in PowerShell:

```powershell
$env:RIME_LAKE_EXE = 'C:\Users\Admin\.elan\toolchains\leanprover--lean4---v4.33.0\bin\lake.exe'
python -B validate_lean_package.py
Get-FileHash -Algorithm SHA256 -LiteralPath formalization-manifest.v1.json
```

The first command binds the installed Lean 4.33.0 Lake executable on this
Windows host; it is not a portable requirement. The validator's result for
the pinned local source closure is:

```text
PASS partial Lean package: 56 bound files; 262 axiom audits
```
