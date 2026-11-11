import FusionLogEnumeration.ActualEndpointBridge
import FusionLogEnumeration.EndpointInverse

namespace FusionLogEnumeration

open RegisteredAbsorptionChains FusionLogSchedule FusionLogReplay FusionLogInterpretation

variable {α : Type*} [DecidableEq α]
variable {C : MarkedCircle α} {n : ℕ} [NeZero n] [NeZero C.rank]
variable {start : LiteralPacketStart C n} {events : List (FusionRecord α)}
variable {schedule : AdmissibleSchedule start.initial start.occupied_nonempty events}

namespace ScheduleTerminalReferenceForLog

theorem sameBlocks (reference : ScheduleTerminalReferenceForLog start events schedule)
    {target : Placement n (Finset (ZMod n))}
    (compatible : IndexCompatible schedule.last target) :
    placedBlocks reference.placed = placedBlocks target := by
  rw [← packetSet_eq_placedBlocks reference.placed reference.ordered,
    ← packetSet_eq_placedBlocks target compatible.1, reference.packets, compatible.2]

/-- Canonical naming reads the target itself, with the reference cycle fixing
the anchor packet. No execution witness is selected by this definition. -/
noncomputable def namedAt (reference : ScheduleTerminalReferenceForLog start events schedule)
    (target : Placement n (Finset (ZMod n)))
    (compatible : IndexCompatible schedule.last target) :
    LegalNamedPlacement n reference.rank (ZMod n) := by
  letI : NeZero (placedBlocks reference.placed).card :=
    ⟨Nat.ne_of_gt reference.rank_positive⟩
  exact canonicalLegalNamed reference.placed target reference.ordered compatible.1
    (reference.sameBlocks compatible)

theorem namedAt_positive (reference : ScheduleTerminalReferenceForLog start events schedule)
    (target : Placement n (Finset (ZMod n)))
    (compatible : IndexCompatible schedule.last target) :
    (reference.namedAt target compatible).PositivelyOrdered := by
  letI : NeZero (placedBlocks reference.placed).card :=
    ⟨Nat.ne_of_gt reference.rank_positive⟩
  exact canonicalLegalNamed_positive reference.placed target reference.ordered compatible.1
    (reference.sameBlocks compatible)

theorem namedAt_blocks (reference : ScheduleTerminalReferenceForLog start events schedule)
    (target : Placement n (Finset (ZMod n)))
    (compatible : IndexCompatible schedule.last target) :
    (reference.namedAt target compatible).block = reference.cycle.block := by
  rfl

theorem coordinates_indexCompatible (reference : ScheduleTerminalReferenceForLog start events schedule)
    (hn : 3 ≤ n) (choice : EndpointChoices n reference.rank) :
    IndexCompatible schedule.last (decodeEndpointChoices reference.cycle choice).placed := by
  letI : NeZero (placedBlocks reference.placed).card :=
    ⟨Nat.ne_of_gt reference.rank_positive⟩
  let decoded := decodeEndpointChoices reference.cycle choice
  have common : SameOrientedBlockCycle (r := reference.rank) reference.placed decoded.placed :=
    ⟨reference.named, decoded, rfl, rfl, rfl, reference.named_positive,
      decodeEndpointChoices_positive reference.cycle choice⟩
  have compatible := (index_compatible_iff_named_cycle reference.placed decoded.placed hn
    reference.ordered rfl).2 common
  exact ⟨compatible.1, compatible.2.trans reference.packets⟩

noncomputable def indexEndpointEquiv
    (reference : ScheduleTerminalReferenceForLog start events schedule) (hn : 3 ≤ n) :
    EndpointChoices n reference.rank ≃
      {target : Placement n (Finset (ZMod n)) // IndexCompatible schedule.last target} where
  toFun choice := ⟨(decodeEndpointChoices reference.cycle choice).placed,
    reference.coordinates_indexCompatible hn choice⟩
  invFun target := coordinatesOfNamed (reference.namedAt target.1 target.2)
  left_inv choice := by
    have congruent := coordinatesOfNamed_congr
      (reference.namedAt (decodeEndpointChoices reference.cycle choice).placed
        (reference.coordinates_indexCompatible hn choice))
      (decodeEndpointChoices reference.cycle choice) rfl (reference.namedAt_blocks _ _)
    exact congruent.trans (coordinatesOfNamed_decode reference.cycle choice)
  right_inv target := by
    apply Subtype.ext
    have inverse := decode_coordinatesOfNamed (reference.namedAt target.1 target.2)
      (reference.namedAt_positive target.1 target.2)
    change placementOfCycleBlocks reference.cycle.block _ = target.1
    change placementOfCycleBlocks (reference.namedAt target.1 target.2).block _ = target.1
      at inverse
    rw [reference.namedAt_blocks] at inverse
    exact inverse

end ScheduleTerminalReferenceForLog

/-- Recover each original source fibre directly from the literal target. -/
def restoreLiteralTarget (start : LiteralPacketStart C n)
    (target : Placement n (Finset α)) : Placement n (Finset (ZMod n)) :=
  fun q => (target q).map (restoreBlock start.initial start.occupied_nonempty)

theorem restoreLiteralTarget_expand (target : Placement n (Finset (ZMod n)))
    (compatible : IndexCompatible schedule.last target) :
    restoreLiteralTarget start (expandPlacement (siteLabels start.initial) target) = target := by
  have saturated := schedule.abstractTrace.preserves_saturation
    (initial_packets_saturated start.initial start.occupied_nonempty)
  funext q
  cases hq : target q with
  | none => simp [restoreLiteralTarget, expandPlacement, hq]
  | some A =>
      have member : A ∈ schedule.last := compatible.2 ▸ (mem_packetSet target A).mpr ⟨q, hq⟩
      simp only [restoreLiteralTarget, expandPlacement, hq, Option.map_some]
      rw [restore_expandBlock start.initial start.occupied_nonempty start.packetPartition
        A (saturated A member)]

theorem compatibleEndpoint_restored {target : Placement n (Finset α)}
    (compatible : CompatibleEndpoint schedule target) :
    IndexCompatible schedule.last (restoreLiteralTarget start target) ∧
      expandPlacement (siteLabels start.initial) (restoreLiteralTarget start target) = target := by
  obtain ⟨indexTarget, hindex, hexpand⟩ := compatible
  have restored := restoreLiteralTarget_expand (start := start) (schedule := schedule)
    indexTarget hindex
  rw [hexpand] at restored
  rw [restored]
  exact ⟨hindex, hexpand⟩

/-- A literal target determines the terminal source-packet partition of every
compatible fixed log. This is the endpoint-side input to survivor recovery;
it does not yet recover which original boundary label survives each interval. -/
theorem compatibleEndpoint_restored_packetSet {target : Placement n (Finset α)}
    (compatible : CompatibleEndpoint schedule target) :
    packetSet (restoreLiteralTarget start target) = schedule.last :=
  (compatibleEndpoint_restored (start := start) compatible).1.2

theorem compatibleEndpoint_same_terminalPartition
    {events₁ events₂ : List (FusionRecord α)}
    {schedule₁ : AdmissibleSchedule start.initial start.occupied_nonempty events₁}
    {schedule₂ : AdmissibleSchedule start.initial start.occupied_nonempty events₂}
    {target : Placement n (Finset α)}
    (compatible₁ : CompatibleEndpoint schedule₁ target)
    (compatible₂ : CompatibleEndpoint schedule₂ target) :
    schedule₁.last = schedule₂.last := by
  rw [← compatibleEndpoint_restored_packetSet (start := start) compatible₁,
    ← compatibleEndpoint_restored_packetSet (start := start) compatible₂]

theorem actualLiteralEndpoint_compatible {d : ℕ} (path : Schedule C d)
    (schedule : AdmissibleSchedule start.initial start.occupied_nonempty path.records)
    (target : ActualLiteralEndpointFiber start path) :
    CompatibleEndpoint schedule target.1 := by
  obtain ⟨bridge⟩ := target.2
  exact (compatibleEndpoint_iff_forLog schedule start.packetPartition target.1).mpr
    ((compatibleEndpoint_iff_forLog bridge.schedule start.packetPartition target.1).mp
      bridge.compatible)

/-- Fixed-log endpoint equivalence. Its inverse reads the literal target via
`restoreLiteralTarget`; the subtype's `Nonempty` field is used only in proofs. -/
noncomputable def fixedScheduleLiteralEndpointEquiv {d : ℕ}
    (start : LiteralPacketStart C n) (path : Schedule C d)
    (schedule : AdmissibleSchedule start.initial start.occupied_nonempty path.records)
    (hn : 3 ≤ n) :
    EndpointChoices n (fixedScheduleTerminalReference start path schedule hn).rank ≃
      ActualLiteralEndpointFiber start path := by
  let reference := fixedScheduleTerminalReference start path schedule hn
  let coordinateEquiv := reference.indexEndpointEquiv hn
  let literalEquiv :
      {target : Placement n (Finset (ZMod n)) // IndexCompatible schedule.last target} ≃
        ActualLiteralEndpointFiber start path := {
    toFun := fun target => ⟨expandPlacement (siteLabels start.initial) target.1,
      ⟨⟨schedule, target.1, target.2, rfl⟩⟩⟩
    invFun := fun target => ⟨restoreLiteralTarget start target.1,
      (compatibleEndpoint_restored (actualLiteralEndpoint_compatible path schedule target)).1⟩
    left_inv := by
      intro target
      exact Subtype.ext (restoreLiteralTarget_expand target.1 target.2)
    right_inv := by
      intro target
      exact Subtype.ext
        (compatibleEndpoint_restored (actualLiteralEndpoint_compatible path schedule target)).2 }
  exact coordinateEquiv.trans literalEquiv

/-- The fixed-schedule equivalence supplies the finite endpoint type. -/
@[instance_reducible]
noncomputable def actualLiteralEndpointFiberFintype {α : Type*} [DecidableEq α]
    {C : MarkedCircle α} {n d : ℕ} [NeZero n] [NeZero C.rank]
    (start : LiteralPacketStart C n) (path : Schedule C d)
    (schedule : AdmissibleSchedule start.initial start.occupied_nonempty path.records)
    (hn : 3 ≤ n) : Fintype (ActualLiteralEndpointFiber start path) :=
  Fintype.ofEquiv (EndpointChoices n
    (fixedScheduleTerminalReference start path schedule hn).rank)
    (fixedScheduleLiteralEndpointEquiv start path schedule hn)

/-- For one fixed admissible schedule and one fixed literal initial placement,
the number of compatible literal terminal placements is the number of choices
of occupied sites together with a cyclic anchor packet.  This is an actual
literal-endpoint fibre count, rather than the coordinate-only product model. -/
theorem card_actualLiteralEndpointFiber {α : Type*} [DecidableEq α]
    {C : MarkedCircle α} {n d : ℕ} [NeZero n] [NeZero C.rank]
    (start : LiteralPacketStart C n) (path : Schedule C d)
    (schedule : AdmissibleSchedule start.initial start.occupied_nonempty path.records)
    (hn : 3 ≤ n) :
    @Fintype.card (ActualLiteralEndpointFiber start path)
        (actualLiteralEndpointFiberFintype start path schedule hn) =
      (fixedScheduleTerminalReference start path schedule hn).rank *
        Nat.choose n (fixedScheduleTerminalReference start path schedule hn).rank := by
  classical
  let reference := fixedScheduleTerminalReference start path schedule hn
  letI : Fintype (ActualLiteralEndpointFiber start path) :=
    actualLiteralEndpointFiberFintype start path schedule hn
  calc
    Fintype.card (ActualLiteralEndpointFiber start path) =
        Fintype.card (EndpointChoices n reference.rank) :=
      Fintype.card_congr (fixedScheduleLiteralEndpointEquiv start path schedule hn).symm
    _ = reference.rank * Nat.choose n reference.rank := card_endpointChoices n reference.rank

end FusionLogEnumeration
