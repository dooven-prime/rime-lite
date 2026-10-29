# Lean 4 Combinatorial Spine

This is a later, partial formalization companion to
[hal-05837829v1](https://hal.science/hal-05837829v1). It is not part of the
HAL v1 deposit, and it does not claim a machine proof of the manuscript's
all-`n` theorems.

## Build

From this directory, use Lean 4.33.0 and run `lake update` followed by
`lake build`. `lakefile.toml` pins the Mathlib commit; `lake-manifest.json`
retains the resolved dependency graph. The `.lake/` cache is not part of this
source package. Run `python -B validate_lean_package.py` for an exact source
inventory/digest check, build replay, and kernel-axiom audit. If `lake` is not
on `PATH`, set `RIME_LAKE_EXE` to the Lean 4.33.0 Lake executable. The direct
axiom command is `lake env lean RegisteredAbsorptionChains/AxiomAudit.lean`.

## Verified declarations

**Task A complete:** Lemma 2.2 is machine-checked under its stated
same-block, same-oriented-order placement premise, including a trace-level
no-fusion condition. The one-block case is a separate rotation theorem.

| Manuscript step | Lean declaration | Exact scope |
|---|---|---|
| Theorem 3.1, equations (3.2)-(3.3) | `chainEquiv`, `card_chainSkeleton`, `card_rankedCode` | A bijection between ternary codes and symbolic checkpoint/side skeletons, including the exact length stratum. |
| Theorem 3.1, code-to-chain sufficiency | `decodeCodePrefix_absorbed`, `realize_clean_code_prefix`, `realize_clean_code`, `realize_clean_code_actual_carrier` | One symbolic decoder tracks the source frontier, last nonzero checkpoint, and exact ordered `FusionRecord` list. For every code, induction from literal registration constructs one actual `p,d` word with that origin, chain, decoded carrier, and singleton outside packets at the endpoint. `CleanOutside` explicitly supplies a physical site whose packet is the decoded carrier. Zero positions preserve the state; each L/R checkpoint uses one batch absorption, including the fully absorbed last checkpoint. |
| Theorem 3.1, code-to-chain injectivity | `checkpointKey_R`, `checkpointKey_L`, `decodeCodePrefix_keys`, `decodeChain_injective` | Each record's result cardinality minus two is its cumulative checkpoint; whether its left parent contains source atom zero is exactly the R/L bit. The chronological key list reconstructs every nonzero code symbol, proving that distinct codes cannot have the same decoded chain. |
| Actual selected-fusion frontier and reverse chain classification | `actual_registered_carrier_from_seed`, `actual_selected_fusion_frontier`, `actual_selected_step_extends_code`, `actual_chain_in_decode_range`, `actual_chain_unique_code`, `codeEquivReachableSelectedChain` | Every registered singleton-seed history has an actual carrier named by the latest selected record (or origin); its next selected partner is a nonempty source-interval prefix or suffix, even after outside fusions. A sparse-code invariant tracks the actual chain and carrier along every literal word. Hence every actual registered selected chain has one unique ternary code, and the code type is equivalent to the subtype of genuinely reachable chains. This proves the chain-bijection surface of Theorem 3.1, not the later fixed-chain fiber or total-summary claims. |
| Theorem 3.1, last checkpoint (3.5) | `lastAtEquiv`, `card_lastAt` | Codes with a fixed final nonzero position are equivalent to a free ternary prefix and a final binary choice. |
| Theorem 4.2, equations (4.3)-(4.4) | `card_rankFiberParams_paper`, `card_fiberParams` | Cardinality of the explicitly declared cut/phase/occupied-offset parameter type, including the all-rank Vandermonde sum. |
| Theorem 5.1, right-hand side | `card_totalParams` | Cardinality of the formal disjoint union of empty-chain and final-checkpoint parameter terms. |
| Lemma 2.2, local word (2.6) | `localWord_moves_into_hole` | For `n >= 2`, the actual chronological `p^(-j) d p^j` word on a circular placement moves the packet at `j+1` into a hole at `j`, with no fusion. |
| Lemma 2.2, net gap accounting | `transferHole_potential_drop`, `balanceTransfers_correct` | Equal-total gap vectors admit a terminating deterministic sequence of net excess-to-deficit transfers. The potential decreases after each complete net transfer; the physical-frame realization is separately checked below. |
| Lemma 2.2, execution semantics for a supplied route | `run_localLetters_safe`, `run_holeWalk_safe` | The local macro expands into actual `p,d` letters. A hole walk through consecutive positions is legal and preserves the registration and selected-chain records. |
| Lemma 2.2, cyclic frame geometry | `GapFrame.faithful`, `GapFrame.cross_faithful` | `next_eq`, coordinate injectivity, and total gap length imply that every counted gap site is empty. The updated frame satisfies the same invariant, including the `r=2` wrap. Admission of an ordered legal placement to such a frame is checked below. |
| Lemma 2.2, one adjacent gap crossing | `crossNextBlock_from_gap`, `crossNextBlock_preserves_records` | A positive donor gap determines the physical hole before the next named block. One actual local `p,d` word updates both adjacent gaps, the moved block coordinate and anchor phase, while preserving origin and selected chain. |
| Lemma 2.2, one net gap transfer | `realizeNetTransferZ`, `finGaps_transfer`, `realizeNetTransfer` | Any positive donor gap can route one hole to a distinct target gap through actual local `p,d` words. Intermediate crossings cancel, the `Fin r` balancer update is exact, and the decoded placement, block labels, origin, and chain are preserved as stated. |
| Lemma 2.2, named placement to frame | `NamedCyclicPlacement.toGapFrame_decode`, `exists_frame_of_named_cyclic_placement` | A genuinely occupied, nonempty/disjoint/exhaustive named atom partition with an explicit positive one-turn cyclic-order witness yields a frame whose decode is the original placement. Mere position injectivity does not supply the order witness. |
| Lemma 2.2, full routing and phase | `realizeBalancedGaps`, `GapFrame.decode_phase`, `realizeFrameTarget`, `realizeNamedPlacementTarget` | The net transfers iterate by strict potential descent as actual `p,d` words. Equal gaps and named blocks determine positions up to an anchor rotation, realized by `pWord`. Thus two admitted named cyclic placements with the same blocks are connected while origin and chain remain unchanged. |
| Lemma 2.2, order admission | `LegalNamedPlacement.forward_distances`, `admit_same_oriented_block_cycle` | For each legal placement, the positive order predicate compares the canonical integer offsets from named block zero. Their successive differences are positive, sum to one turn, and include the wrap across residue zero. A shared block enumeration yields the two `NamedCyclicPlacement` witnesses. |
| Lemma 2.2, literal no-fusion word | `fusionFree_localLetters`, `crossNextBlock_fusionFree`, `realize_same_oriented_block_cycle`, `realize_same_single_block_cycle` | The final word reaches the target while preserving origin and selected chain. At every executed `d`, at least one kernel port is empty. The `r=1` case uses only a rotation; the `r>=2` case uses gap routing and phase alignment. |
| Source-order invariant | `SourceOrderLift.fiber_convex`, `reachable_source_ordered` | Every actual `p,d` execution from the singleton seed has an exact source-fiber representation by a monotone degree-one integer lift. Literal rotations and defects preserve the representation; exact integer-lift fibers are convex. |
| Fusion adjacency | `SourceOrderLift.adjacent_port_fibers`, `fusion_step_ordered_and_adjacent` | When both defect ports are occupied, their source atoms admit positive integer representatives with consecutive lifted target values. Between those representatives there is no third output fiber; the merged execution remains source-ordered. |
| Source cyclic arcs and common key order | `sourceOrdered_blocks_are_cyclic_arcs`, `sourceOrdered_same_blocks_key_order` | Modular source fibers are cyclic arcs, including the seam-wrapping case. A block's least source atom gives a lift-independent key; common blocks with increasing keys have increasing positive physical offsets in both source-ordered placements. |
| Canonical cyclic admission | `occupiedBlockKey_injective`, `canonicalLegalNamed_positive`, `sourceOrdered_same_blocks_admit`, `realize_source_ordered_same_blocks` | Actual nonempty blocks are sorted by their source-only keys, then used as one common `ZMod r` naming. Both placed partitions satisfy legal occupancy and positive cyclic order. For `r>=2` Lemma 2.2 supplies a fusion-free actual word; `r=1` uses pure rotation. Both source and target must independently satisfy `SourceOrdered`. |
| Combinatorial fiber target admission | `ValidFiberPlacement.cut_cover`, `ValidFiberPlacement.blockFin_cover`, `ValidFiberPlacement.toLegal_positive`, `ValidFiberPlacement.realize_from_named_source` | Strict cut boundaries split a nonempty linear complement; strict clockwise offsets place its blocks after a possibly seam-wrapping carrier. The decoded target is a legal positive-cycle placement without a reachability premise. A separately constructed and correctly named source with these same blocks can be adjusted to it by a fusion-free actual word. |
| Native fixed-rank target decoder | `ValidFiberPlacement.ofRankParams`, `rankFiberParams_target_admit`, `rankFiberParams_realize_from_named_source` | For a specified carrier arc containing source zero, the native finite cut/phase/offset tuple decodes to the combinatorial target and supplies its positive-cycle witness. The actual-word conclusion still assumes an independently assembled same-block named source. |
| Outside-fusion stage and conditional assembly | `stepDefect_outside_records`, `realize_one_carrier_safe_outside_merge`, `OutsideAssemblySchedule.realize` | A genuine fusion of two packets disjoint from the selected carrier preserves origin and chain. Supplied legal stages compose into a real word; the all-cut construction is checked separately below. |
| One-block rotation | `realize_same_single_block_cycle` | A single packet can move between its sites by a pure rotation; the fixed-code full-carrier specialization is now proved below. |
| Conditional fixed-rank word composition | `realize_rank_target_after_outside_schedule` | A supplied outside schedule and a final named placement matching the cut decoder compose into one actual word. Its assembly prefix may fuse outside blocks; only the suffix is fusion-free. The all-cut construction below discharges these premises for a chosen clean code witness. |
| Full-carrier phase fiber | `card_fullCarrierPlacements`, `sourceOrdered_fullCarrier`, `realize_reachable_fullCarrier_phases` | The `n` site placements of one block are distinct. In a singleton-seed reachable state, a full carrier at one site forces all other sites to be holes; all `n` phases then follow by fusion-free rotation with origin and chain fixed. Registration and the link from the last selected record to the current full carrier are not supplied by this theorem. |
| Actual `k=0` fixed-record fiber | `fullCarrierFixedRecords_eq_phases`, `full_carrier_code_fiber_phases` | The earlier conditional phase theorem now receives an actual clean witness for every full-carrier code. Its fixed-origin/fixed-chain fiber has exactly `n` phases. Origin classification across all generated histories remains separate. |
| Irreversibility of actual fusion | `run_placementOfMap`, `no_split_from_reachable` | If two source atoms occupy the same packet in a singleton-seed reachable placement, every actual continuation still places them in one common packet. This rules out requiring an arbitrary already-merged chain witness to realize a cut that separates them. |
| Partition refinement and cut necessity | `actual_word_refines`, `source_packet_subset_target_block`, `outside_packet_within_target_interval` | Every actual continuation coarsens the source packet partition. If a target consists of a carrier and outside cut intervals, each current nonempty outside packet must lie in one target interval. This is only necessary for reachability. |
| Clean-chain registration base | `registration_clean`, `clean_reachable_outside_singletons` | The literal first `d` registers `{0,1}` with the declared origin and empty selected chain. Reachability plus cleanliness implies every atom outside the carrier is present as a singleton packet. This is the base case, not an arbitrary-chain witness. |
| Conditional clean absorption induction | `clean_same_named_blocks`, `unique_named_block_site`, `realize_clean_absorption_step` | From an actually reachable clean witness, a supplied same-order legal placement of its carrier and an outside singleton at the kernel ports yields one continuous actual word, the exact appended selected event, and another reachable clean witness. Same block names transfer cleanliness; legality forces the carrier site to be unique. This one-step lemma does not itself decode a whole code. |
| Partner assembly invariant | `clean_partner_assembly_invariant`, `partner_invariant_same_named_blocks`, `realize_one_partner_assembly_stage`, `partner_finished_shape` | Clean outside packets initialize a weaker invariant: temporary nonsingletons may form only within the chosen partner block. One supplied legal outside-merge stage preserves this invariant along one actual word without extending the selected chain. Once the complete partner occurs in a source-ordered state, no distinct partner subpacket remains. |
| Conditional batch checkpoint | `checkpoint_step_records`, `checkpoint_step_clean`, `realize_clean_checkpoint_from_finished_partner`, `realize_clean_singleton_checkpoint` | For either ordered port direction and a partner packet of arbitrary size, a supplied actual outside-assembly schedule followed by one fusion-free placement adjustment and one `d` yields one continuous reachable word. The weak final assembly invariant and common block naming imply the strong endpoint shape; the final `d` appends exactly one source-addressed record and restores singleton outside packets. For a singleton partner the empty schedule follows from a clean source, covering both L and R. The theorem does not construct nontrivial schedules or establish their `|B|-1` outside-fusion count. |
| Constructed partner and checkpoint placements | `packed_adjacent_partner_schedule`, `packed_adjacent_partner_stage_exact`, `realize_packed_R_checkpoint`, `realize_gap_L_checkpoint` | An adjacent named outside pair has a concrete, uniformly legal packed target and one actual outside-merge schedule with an explicit fused endpoint and preserved weak partner invariant. Once an assembled partner is present as the first or last outside named block, the R or L kernel-port placement is constructed with the same positive cyclic order; the L construction leaves the gap after the carrier. A supplied schedule then extends the same actual execution by exactly one selected absorption. These statements do not yet generate a whole partner interval's schedule from a symbolic checkpoint. |
| Exact named outside update | `merge_named_outside`, `merge_named_outside_actual`, `merge_named_R_blocks`, `merge_named_L_blocks` | Merging adjacent outside indices `j,j+1` yields a legal positive-cycle naming with `r-1` blocks. Its `placed` is exactly the real fused successor; block `j` is the union, all other blocks retain their source identities under the skip-index map, and block zero remains the carrier. One literal word reaches this named successor while preserving the selected records. |
| Fixed R/L partner schedules | `RPartnerPrefix.assemble_named`, `LPartnerSuffix.assemble_named`, `CountedOutsideSchedule.realize` | A supplied consecutive prefix or suffix of `ell` named outside blocks is merged by one counted actual schedule with exactly `ell-1` outside fusions. The stronger endpoints retain a legal positive-cycle naming whose `placed` is the actual successor, whose block zero is the carrier, and whose first (R) or last (L) outside block is exactly the partner. The count excludes fusion-free routing letters. |
| Checkpoint partner admission and actual step | `CheckpointSourceFrontier.clean_placedBlocks`, `CheckpointSourceFrontier.canonical_outside_block`, `CheckpointSourceFrontier.exists_named_alignment`, `CheckpointSourceFrontier.realizeR_checkpoint`, `CheckpointSourceFrontier.realizeL_checkpoint` | Source intervals give the R/L partner of size `b_i-b_(i-1)`, disjoint from the carrier, and update the cumulative checkpoint exactly. Actual reachability and cleanliness force one carrier plus the remaining singletons; canonical source-key naming orders them correctly without a separately supplied naming witness. For a source whose carrier equals this frontier and whose registration is live, counted assembly and port placement form one continuous word, append exactly one side-sensitive selected record, and restore cleanliness at the next frontier. The whole-code composition is now in `CleanCodeInduction`. |
| Checkpoint cost identity | `checkpoint_cost_ledger` | For strictly increasing checkpoint indices, the specified batch assembly costs `b_i-b_(i-1)-1` telescope to final index minus selected event count. This arithmetic identity does not assert that each required actual assembly word has been constructed. |
| One-block outside cut control | `oneCut_assemble_named`, `oneCut_realize_target` | From a clean checkpoint, the single outside target block is assembled by an actual counted schedule and then placed by a fusion-free adjustment. |
| All-cut boundary deletion and lifting | `targetCutBoundaryPlan`, `CutNamed.boundaries_merge`, `CutNamed.merge_actual`, `CutBoundaryPlan.realize_named`, `allCut_assemble_named` | Cut boundaries use absolute source addresses. Starting with singleton outside packets, delete each non-target boundary by one merger of adjacent named packets. Every intermediate naming equals the actual successor placement; the recursion retains one concrete execution and uses exactly `k-t` genuine outside fusions for `k` outside atoms and `t` target blocks. |
| Fixed-chain cut sufficiency | `allCut_realize_target`, `code_fiber_target_reachable`, `code_rank_params_reachable` | Every valid positive-complement cut and target placement matching a code's decoded carrier is reached by one actual `p,d` word from that code's chosen clean singleton-seed witness. Origin and selected chain stay fixed; `k-t` does not bound raw letters. |
| Actual reverse fiber normal form | `actual_fiber_normal_form`, `actual_fiber_rank_normal_form` | Every registered singleton-seed endpoint with a fixed decoded chain and nonempty complement is a typed cut/phase/offset target, and hence has native finite rank parameters. No clean-outside assumption is imposed on the actual history. |
| Rank-parameter uniqueness and placement equivalence | `ValidFiberPlacement.of_toRankParams`, `ValidFiberPlacement.to_ofRankParams`, `rank_params_target_unique`, `actualFixedChainPlacementEquiv` | Cuts and occupied offsets encode and decode without repetition. Source-key-sorted naming makes the concrete target injective at a fixed carrier arc; the number of occupied blocks fixes the rank. Thus positive-rank tuples are equivalent to the literal generated placement fiber for a fixed selected chain. This does not yet classify registration origins or count complete summaries. |
| Registered origin classification | `actual_registered_origin_unique` | For `n >= 3`, every generated registered history has the ordered origin of `registrationExecution`. Source order and the third atom rule out reversed-port registration; `n=2` is excluded. |
| Full-carrier placement equivalence | `fullCarrierFixedChainPlacementEquiv`, `card_actualFixedChainPlacements_full` | For every decoded empty-complement code, `ZMod n` is equivalent to the actual reachable placement fiber, whose cardinality is `n`. |
| Actual fixed-chain count | `positiveRankFiberParamsEquiv`, `card_actualFixedChainPlacements_positive` | For `k>0`, the positive-rank tuple is converted to the finite `Fin k` rank presentation; the actual reachable placement fiber has cardinality `n * choose(n+k-2,k)`. The `k>0` premise is necessary for this parameter conversion. |
| Complete-summary dependent assembly | `actualSummaryCodeFiberEquiv`, `actualSummaryFiniteParamsEquiv`, `card_actualRegisteredSummaries_code_sum` | For `n>=3`, complete generated execution records are equivalent to the dependent sum over codes of their finite fixed-chain placement parameters. The origin read is supplied by `actual_registered_origin_unique`, not inferred from placement counts alone. |
| Closed actual-summary count, `n>=3` | `codeLastCheckpoint_weighted_sum`, `decodeCode_absorbed_eq_codeLastCheckpoint`, `card_actualRegisteredSummaries_closed` | The decoder's absorbed count is the final nonzero checkpoint. Weighted code regrouping turns the actual code-indexed fiber sum into the manuscript's closed binomial expression. |
| Exceptional `n=2` and all-size count | `two_registration_origins_distinct`, `actualRegisteredSummaries_two_complete`, `actualRegisteredSummariesTwoProductEquiv`, `actualRegisteredSummariesTwoProduct_origin`, `actualRegisteredSummariesTwoProduct_phase`, `card_actualRegisteredSummaries_piecewise` | The direct six-state actual-word closure has two pre-registration phases and four registered states. The product projections identify `Bool` with the ordered registration origin and `ZMod 2` with the unique physical carrier site. This and the `n>=3` formula give a piecewise count for every `n>=2`. |

These are all-parameter Lean theorems about the stated finite types, not
bounded evaluations. The parameter types are deliberately named separately
from the manuscript's sets of *actually reachable* chains and summaries.
Three compiled `n=4` controls in `Execution.lean` check the manuscript's
same-endpoint/different-selected-chain example against the new interpreter;
these controls are not used in any all-parameter proof. Three `n=6` controls
in `CrossNextBlock.lean` show that two consecutive physical hole steps do not
cross the two next blocks in the spaced-block configuration, whereas the
actual crossing sites `1,3` do. A further `n=4` control in
`CleanCheckpointStep.lean` checks the batch code `(0,R)`: one outside merger
forms `{2,3}` and only the final defect appends its single selected record.

## Remaining bridge

Lemma 2.2 is machine-checked on the paper's two-placement premise as encoded
by `SameOrientedBlockCycle` (or `SameSingleBlock` for `r=1`). The source-order
invariant and canonical admission now additionally derive that premise from
two independently source-ordered placements with the same nonempty blocks.
The current spine has complete-summary dependent assembly and the closed
actual-summary count for every `n>=2`. It does not identify the actual
parameter family with the older checkpoint-stratified `TotalParams` type,
nor machine-check the manuscript's asymptotic growth rate.

The target placement in a fixed-chain sufficiency proof obtains its positive
order from the native cut and offset parameters via `ofRankParams`; this does
not use `reachable_source_ordered`. `CutBoundaryPlan.realize_named` now derives
the stage schedule and terminal common naming from every valid cut, while
`allCut_realize_target` appends the fusion-free target adjustment to that
*same* actual execution. `code_fiber_target_reachable` supplies the source
from the literal singleton seed and ties its carrier to the decoded code.
The reverse code-existence theorem and actual carrier trace are proved.
`ActualFiberNormalForm` extracts a typed target from an arbitrary generated
endpoint, while `FiberParamInverse` supplies inverse rank encoding and an
equivalence for the `k>0` placement fiber. `OriginClassification` identifies
the origin of every generated registered history when `n>=3`, and the
full-carrier equivalence handles `k=0`. `TotalSummaryAssembly` then assembles
one global equivalence of actual complete summaries and code-indexed fibers.

The clean-witness quantifiers cannot be strengthened to *every* actual witness
of `A`: fusions that have already joined outside atoms cannot be reversed.
`outside_packet_within_target_interval` proves the stronger whole-packet
containment condition for literal `p,d` continuations, not only an abstract
partition order. It does not claim that refinement suffices for a legal word.

In particular, `card_actualRegisteredSummaries_closed` applies the proved
last-checkpoint weighted sum to the actual code-indexed placement fibers.
It yields the manuscript's closed formula for `n>=3` without identifying
the actual-summary parameter type with the older `TotalParams` type.
`GapFrame.Faithful` follows
from the full cyclic coordinate recurrence, injectivity, and one-turn total;
the numerical gap total alone would not suffice. `GapFrame.block` does not
enforce a nonempty, disjoint, exhaustive atom partition. The actual-action BFS in the
parent directory remains a separate bounded consistency control for
`2 <= n <= 7`; it does not fill these all-`n` proof obligations.
