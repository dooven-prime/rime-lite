# Paper XLVI candidate: theorem and proof-source map

This map concerns the current local candidate. The companion sources have
no new release identity assigned by this file. All paths below refer to
the owning [RSR-2 Lean package](lean/README.md),
under `RSR2.Parametric` unless the source specifies another namespace.
No Lean proof was rewritten to create the manuscript.

## Main theorem interfaces

| Manuscript | Source module in `lean/RSR2/` | Exported declaration(s) | Scope |
| --- | --- | --- | --- |
| Section 2: parametric guarded machine | `Parameterized.lean` | `step_v_eq_some_iff`, `successful_lift_preserves_partition`, `collapse_preserves_existing_packet_eq` | Atom-to-location state; failed transfer is `none` |
| (2.4): eight-letter crossing certificate | `Crossing.lean` | `RSR2.crossing_word_executes`, `RSR2.crossing_word_has_crossing_blocks`, `RSR2.crossing_word_length` | Concrete four-site execution theorem, not an all-size lower bound |
| Lemma 3.1 | `CanonicalEndpoint.lean` | Singleton-block specialization of `orderedPartition_bell_realization` | Permutation target and bound `n*n+n-1`; no separate exported loading declaration |
| Theorem 3.2 | `CanonicalEndpoint.lean` | `orderedPartition_run_canonical`, `orderedPartition_bell_realization` | Actual word, exact coordinates and raw cost for every ordered presentation |
| Corollary 3.3 | `BellProjection.lean` | `unorderedPartition_has_orderedPresentation`, `canonicalPlacement_samePacket_iff`, `unorderedPartition_bell_realization` | Every input `Setoid (Fin n)`; no input block order |
| Lemma 4.1 | `LowerRestrictedOrder.lean` | `singleton_run_lowerRestrictedOrdered`, `lowerRestrictedOrdered_packet_cyclic_interval`, `lowerRestrictedOrdered_three_packet_order` | Arbitrary legal history, including prefusion and whole-packet transfer |
| Theorem 4.3 | `RetentionNecessity.lean`, `RetentionSufficiency.lean` | `singleton_run_unorderedRetentionAdmissible`, `unorderedRetentionAdmissible_realization`, `endpointLayerAllocation_reachable_iff` | Exact order-free layer allocation iff; no prescribed literal coordinates |
| (4.6) | `TransferMass.lean` | `runWithTransferMass_project`, `runWithTransferMass_balance`, `singleton_run_exists_transferMass` | Mass charged at each actual pre-transfer packet; same guarded execution |
| Corollary 4.4 | `MinimumTransferMass.lean` | `maxAdmissibleRetentionMass_spec`, `singleton_run_transferMass_lower_bound_of_run`, `singleton_run_transferMass_attained` | Universal lower bound plus actual attaining word |
| Lemma 5.1 | `LowerPacketLedger.lean`, `PacketRankLedger.lean` | `runWithLowerPacketLedger_balance`, `runWithLowerPacketLedger_port_balance`, `singleton_run_packetRankLedger_balance`, `word_length_eq_lowerPortCost_add_upper` | Actual counters on one successful execution |
| Lemma 5.2 | `LowerPortGeometry.lean`, `UpperPortVacancy.lean` | `runWithLowerPacketLedger_refill_bound`, `run_upperPortVacancy_bound` | Independent source/receiver credits, including ineffective defects |
| (5.4)--(5.5) | `LowerPortGeometry.lean` | `step_lowerPortApproachDistance`, `step_lowerSeparationDistance`, `singleton_run_mergedAtom_rotation_lower_bound` | Single-atom/pair potentials; shared rotation is charged once |
| Theorem 5.3: optimum | `PortCostSharpness.lean` | `upperSingletonEndpoint_optimal` | Literal target; raw minimum `3*n-2`, port minimum `2*n-1`, `n>1` |
| Theorem 5.3: exhaustive family/count | `SingletonElevatorSkeleton.lean`, `SingletonOptimalClassification.lean`, `SingletonOptimalCounting.lean` | `singleton_optimal_elevator_skeleton`, `singleton_optimal_iff_variant`, `singleton_two_optimal_iff`, `singleton_optimal_words_exact_count` | Literal words; `n>=3` Boolean family and separate `n=2` exception |
| Full-packet comparison after Theorem 5.3 | `PortCostSharpness.lean` | `upperFullPacket_optimal` | Minimum `2*n-2`, for `n>=3`; no uniqueness claim |
| Theorem 6.1: rotation | `SingleVacancyDebt.lean` | `singleVacancyTerminal_rotation_lower_bound` | Broader terminal predicate, other retained coordinates free |
| Theorem 6.1: control/raw cost | `SingleVacancyOptimality.lean` | `singleVacancyRep_work_run`, `singleVacancyRep_work_port_run`, `singleton_singleVacancyRep_work` | Broader terminal predicate; proof uses augmented actual-state payment |
| Theorem 6.2 | `SingleVacancyWitness.lean`, `SingleVacancyOptimality.lean` | `singleVacancyWord_run`, `singleVacancyEndpoint_optimal`, `singleVacancyEndpoint_exists_unique_shortest` | Specified literal endpoint, exact raw optimum and unique raw word |
| Productive-slide lower count in Theorem 6.1 | `SingleVacancySlideCount.lean` | `singleVacancyTerminal_slide_and_transfer_counts` | Same actual execution; the separate congruence presentation is manuscript-level |
| Lemma 7.1 | `AntipodalFusionGate.lean` | `antipodal_lower_fusion_gate`, `antipodal_endpoint_lowerPacketCount_le_one` | Every legal implementation of the unordered matching |
| Proposition 7.2 | `AntipodalFusionGate.lean`, `AntipodalLinearBounds.lean` | `antipodal_run_lowerPortCost_lower_bound`, `antipodal_run_fusion_counts`, `antipodal_run_length_lower_bound` | Arbitrary layer allocation, endpoint sites and legal schedule |
| Lemma 7.3 | `AntipodalLinearWitness.lean` | `antipodal_linear_word_realizes`, `antipodalSpacedEndpoint_partition`, `antipodal_linear_word_counts`, `antipodal_linear_word_length` | Exact literal endpoint, every guard and primitive count |
| Theorem 7.4 | `AntipodalLinearBounds.lean` | `antipodal_partition_length_bounds`, `antipodal_partition_port_bounds` | All feasible lengths/costs satisfy the lower bound; upper bound is feasible |

## Mathematical consequences kept distinct

- The least-element formulation of Theorem 7.4 follows from the formal
  feasibility bounds and natural-number well-ordering. The companion does
  not separately define `ell` using `Nat.find` or `sInf`.
- `M(pi_m)=2` and `T_min(pi_m)=2*m-2` are the source-level evaluation of
  the formal general retention/mass theorem. Attainment of minimum elevator
  **letter count** `2*m-2` is also a separate source-level allocation
  corollary; the two-pass word uses `2*m` elevators.
- The nested retention example is a finite mathematical illustration of
  the general criterion, not a new exported Lean declaration.
- The shortest-word counts are Lean-proved; the quotient by a specified
  commutation congruence and its cardinality are manuscript corollaries.
  At `n=2`, rotation commutation alone gives three classes, not two.
- The Bell-number cardinality terminology and Section 8's finite word
  count/asymptotic information bound are manuscript-level arguments. In
  particular (8.3)--(8.4) use the elementary function-to-partition count;
  they do not add a Lean Bell-number asymptotics theorem.
- The single-vacancy rotation and work bounds are Lean-proved by local
  potentials. Section 6 uses these as its main proof, with one paragraph
  explaining the repeated vacancy-return geometry. The productive-slide
  counter remains available in `SingleVacancySlideCount.lean`; the separate
  congruence presentation is not an exported Lean declaration.

## Computational interfaces and controls

The core-only companion pins Lean 4.33.0. The placement executor has type
`Fin n -> Prod Bool (Fin n)`, with packets as fibres and failed transfers as
`none`. A successful `run = some Q` checks every transfer in the same
actual word. The package has no Mathlib or one-ring fusion-log import.

| Artifact in `experiments/paper46/` | Scope |
| --- | --- |
| `lean/RSR2/` and `lean/RSR2.lean` | All-parameter proof modules listed in the theorem map |
| `lean/RSR2/AxiomAudit.lean` | Explicit target declarations and their transitive axiom dependencies |
| `rsr2_model.py` and `test_*.py` | Bounded replay, including all partitions through `n=7`, allocation graphs through `n=4` and shortest singleton words through `n=7` |
| `antipodal_partition_cost.py` | Actual two-pass word, literal endpoint, complete event tuple and primitive counts |
| `validation/replay.py` | Development-input byte check, bounded tests and optional Lean build and axiom audit |

The unordered-Setoid presentation theorem uses classical choice. It proves
existence of a legal finite word for each partition, rather than extracting
a compiler from a relation with no supplied decision procedure. Execution
of a supplied word is executable. The Python controls are separate bounded
implementation checks; there is no claimed all-parameter Python-to-Lean
semantic correspondence.

## Rechecking and archival boundary

Use the component's pinned commands:

```text
cd experiments/paper46/lean
lake --no-cache build
lake env lean RSR2/AxiomAudit.lean
```

The audit prints the axioms of explicitly selected theorem declarations.
The current list is in `RSR2/AxiomAudit.lean`; its size is not a count of all
transitive lemmas. It must be checked alongside the build, rather than
inferred from manuscript labels. Local compiled-artifact reuse does not
constitute independent cold-start reproduction.

The mathematical proof texts consolidated here come from the exploratory
Bell-universality, layer-allocation, port-geometry, singleton-schedule,
repeated-vacancy, and antipodal-linear-cost notes. The manuscript now owns
the paper proofs; those notes remain development provenance. The extracted
Python and Lean files are recorded in the package's extraction inventory.
The development manifest binds the current candidate inputs, not an
archival release identity. No published or frozen manuscript is changed.
