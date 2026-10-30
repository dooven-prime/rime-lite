# Future-Event Minimal Quotients

**Status:** Submitted to HAL as `hal-05844771v1`; public availability is
pending confirmation. This is an unnumbered preprint with a frozen reader PDF
and bounded control package; it is not a numbered RIME paper or a
Lean-verified result. No DOI or journal acceptance is claimed for this
manuscript.

## Reader entry

- [Reader PDF](hal-v1/Chen_Future_Event_Minimal_Quotients_HAL_preprint.pdf):
  twelve-page file submitted to HAL as `hal-05844771v1`.
- [Manuscript](MANUSCRIPT.md): all-parameter future-event right congruence,
  actual distinguishing probes, exact class counts, and observation-contract
  asymptotics for `n>=3`, `F={0,1}`.
- [Bibliography](references.bib): classical sequential-machine sources and
  the published upstream event/summary sources.
- [Build script](build_hal.py): recreates the reader PDF with a fixed PDF
  metadata epoch. Requires Pandoc, pdfLaTeX, and BibTeX.
- [Bounded controls](../../../experiments/future_event_minimal_quotient/README.md):
  self-contained replay for `n=3..5`, not an all-`n` theorem owner.

| Frozen candidate file | SHA-256 |
|---|---|
| `MANUSCRIPT.md` | `5e0adba3542361c4b8227f96507bca40f71a76012389a6d97811cf7658d5dad6` |
| `references.bib` | `a14482d02001eb3d4fb3c8af55bb464d063cc79274aefc4d06069294fb46c62a` |
| `build_hal.py` | `5e4fc0384a3f0e3fccdbea5689480c503deb3a43aec94231c868eef4f7cca70d` |
| `hal-v1/Chen_Future_Event_Minimal_Quotients_HAL_preprint.pdf` | `7b0494b6225fcf28faad95652fd77b1cd846ff04e444e4d01553a30936909d11` |
| `experiments/future_event_minimal_quotient/control-manifest.v1.json` | `81bdd3e94b0b7071f5bf7f70404884347a10303ba22baaa3e30c150820653c3e` |

The future-event observer emits complete selected registration/absorption
records on raw letters. The full-summary observer displays the complete
current registered state. Their minimal right congruences are different
objects on the same reachable state space. The manuscript does not change
the HAL absorption preprint, its Lean claim, or Paper XL.
The upstream registered-chain [source snapshot](https://github.com/dooven-prime/rime-lite/commit/050cf8e)
is separate from the [HAL v1 preprint](https://hal.science/hal-05837829v1).

## Theorem spine and proof ownership

| Item | Content | Evidence layer |
|---|---|---|
| Lemmas 3.1--3.2 | source order, actual nonfusion placement control, registration criterion | manuscript proof; inherited action semantics |
| Proposition 3.3 | actual registerable and registered placement counts | manuscript proof; complete-summary reachability is also available upstream |
| Lemmas 4.1--4.3, Corollary 4.4 | aligned sweep, first-event orientation decoder, and outside-anchored phase recovery | manuscript proof |
| Lemmas 5.1--5.3 | atomwise word semantics, gap fibers, exact coalescence fiber | manuscript proof |
| Theorems 1--2, Lemma 6.1 | minimal future-event quotient, `6n-10` distinguishing bound, and event-to-summary prefix detection | manuscript proof from preceding lemmas |
| Section 7 | exact classes, growth separation, and explicit probe-coalescence graph | manuscript proof; `s_n` imported from the HAL preprint |

Finite tests remain consistency controls. This is a new observation-contract
result, not an update to the HAL count theorem or the domain-specific Q2
checker in Paper XL.

## Later formalization boundary

A separate Lean companion could proceed through these typed interfaces:

1. `atomSite_run` and placed-partition recovery, including fused steps.
2. `gapProbe_preFinal_fibers` and `gapProbe_registers_on_last_letter`.
3. `gapProbe_coalesces_iff_holeMove`, with actual `E_j` words and the
   identity case distinct from directed edges.
4. `registeredSweep_injective`, `firstSelectedEvent_phaseDecoder`, and
   `outsideAnchor_recovers_carrierSite`.
5. `futureEvent_equiv_iff_key` and the common-suffix depth bound.
6. Only after the behavioral spine: finite cardinal identities and
   asymptotic transfer from the separately owned `s_n` theorem.

This list is a formalization plan, not a Lean completion claim. A future
package may explicitly import versioned execution definitions from the HAL
companion, but must keep its new theorems and axiom audit separate from the
already frozen HAL milestone.
