import FusionLogEnumeration.SurvivorRecovery
import FusionLogEnumeration.FixedScheduleEquiv

namespace FusionLogEnumeration

open RegisteredAbsorptionChains FusionLogSchedule FusionLogReplay FusionLogInterpretation

variable {α : Type*} [DecidableEq α]
variable {n : ℕ} [NeZero n]

theorem packetSet_expandPlacement (labels : ZMod n → Finset α)
    (P : Placement n (Finset (ZMod n))) :
    packetSet (expandPlacement labels P) = (packetSet P).image (expandBlock labels) := by
  ext B
  simp only [mem_packetSet, Finset.mem_image]
  constructor
  · rintro ⟨q, hq⟩
    obtain ⟨A, hA, rfl⟩ := Option.map_eq_some_iff.mp hq
    exact ⟨A, ⟨q, hA⟩, rfl⟩
  · rintro ⟨A, ⟨q, hq⟩, rfl⟩
    exact ⟨q, by simp [expandPlacement, hq]⟩

private theorem image_erase_injOn {ι β : Type*} [DecidableEq ι] [DecidableEq β]
    (f : ι → β) (S : Finset ι) (a : ι) (ha : a ∈ S)
    (injective : Set.InjOn f (↑S : Set ι)) :
    (S.erase a).image f = (S.image f).erase (f a) := by
  ext b
  simp only [Finset.mem_image, Finset.mem_erase]
  constructor
  · rintro ⟨x, ⟨different, hx⟩, rfl⟩
    exact ⟨fun same => different (injective hx ha same), x, hx, rfl⟩
  · rintro ⟨different, x, hx, rfl⟩
    exact ⟨x, ⟨fun same => different (congrArg f same), hx⟩, rfl⟩

theorem expand_mergePackets (initial : Placement n (Finset α))
    (nonempty : (occupiedSites initial).Nonempty) (valid : PacketPartition initial)
    (packets : IndexPackets n) (A B : Finset (ZMod n))
    (all : AllSaturated (occupiedRounding (occupiedSites initial) nonempty).position packets)
    (left : A ∈ packets) (right : B ∈ packets) (distinct : A ≠ B) :
    (mergePackets packets A B).image (expandBlock (siteLabels initial)) =
      MarkedCircle.advancePacketAtoms (packets.image (expandBlock (siteLabels initial)))
        (expandRecord (siteLabels initial) ⟨A, B, A ∪ B⟩) := by
  let f := expandBlock (siteLabels initial)
  have injective : Set.InjOn f (↑packets : Set (Finset (ZMod n))) := by
    intro U hU V hV same
    have recovered := congrArg (restoreBlock initial nonempty) same
    simpa only [f, restore_expandBlock initial nonempty valid U (all U hU),
      restore_expandBlock initial nonempty valid V (all V hV)] using recovered
  have right' : B ∈ packets.erase A := Finset.mem_erase.mpr ⟨distinct.symm, right⟩
  have injective' : Set.InjOn f (↑(packets.erase A) : Set (Finset (ZMod n))) :=
    injective.mono (by intro U hU; exact Finset.mem_of_mem_erase hU)
  simp only [mergePackets, Finset.image_insert]
  rw [image_erase_injOn f _ B right' injective', image_erase_injOn f _ A left injective]
  simp only [f, expandBlock_union, MarkedCircle.advancePacketAtoms, expandRecord]

theorem expanded_abstractTrace_last_eq_fold
    (initial : Placement n (Finset α))
    (nonempty : (occupiedSites initial).Nonempty) (valid : PacketPartition initial)
    {packets last : IndexPackets n} {events : List (FusionRecord (ZMod n))}
    (trace : AbstractTrace packets events last)
    (all : AllSaturated (occupiedRounding (occupiedSites initial) nonempty).position packets) :
    last.image (expandBlock (siteLabels initial)) =
      (events.map (expandRecord (siteLabels initial))).foldl
        MarkedCircle.advancePacketAtoms (packets.image (expandBlock (siteLabels initial))) := by
  induction trace with
  | nil packets => rfl
  | @cons packets last A B rest left right distinct boundary tail ih =>
      rw [ih (merge_packets_saturated all left right)]
      simp only [List.map_cons, List.foldl_cons,
        expand_mergePackets initial nonempty valid packets A B all left right distinct]

namespace LiteralPacketStart

theorem packetSet_initial {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) : packetSet start.initial = C.packetAtoms := by
  ext A
  rw [mem_packetSet]
  simp only [MarkedCircle.packetAtoms, List.mem_toFinset, List.mem_map]
  constructor
  · rintro ⟨q, hq⟩
    rw [start.initial_eq_named] at hq
    obtain ⟨i, hi⟩ := start.named.only_named q (by simp [hq])
    let j : Fin C.rank := (ZMod.finEquiv C.rank).symm i
    have jcast : (j.val : ZMod C.rank) = i := by
      have cast := ZMod.natCast_zmod_val (ZMod.finEquiv C.rank j)
      rw [EndpointChoices.finEquiv_val] at cast
      simpa [j] using cast
    refine ⟨C.packets[j], List.getElem_mem j.isLt, ?_⟩
    have atSite := start.named.placed_at i
    rw [hi, hq] at atSite
    rw [← start.circleBlocks j, jcast]
    exact Option.some.inj atSite.symm
  · rintro ⟨p, hp, rfl⟩
    obtain ⟨i, hi, rfl⟩ := List.mem_iff_getElem.mp hp
    let j : Fin C.rank := ⟨i, hi⟩
    refine ⟨start.named.position (j.val : ZMod C.rank), ?_⟩
    rw [start.initial_eq_named, start.named.placed_at, start.circleBlocks j]
    rfl

end LiteralPacketStart

/-- The same literal endpoint has exactly the packet contents computed by the
M5 contraction schedule. This connects M4-D compatibility to the marked-circle
invariant without treating any hidden boundary label as endpoint data. -/
theorem compatibleEndpoint_packetAtoms {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d : ℕ} (path : Schedule C d)
    (schedule : AdmissibleSchedule start.initial start.occupied_nonempty path.records)
    {target : Placement n (Finset α)} (compatible : CompatibleEndpoint schedule target) :
    packetSet target = path.terminalCircle.packetAtoms := by
  obtain ⟨indexTarget, hindex, expanded⟩ := compatible
  rw [← expanded, packetSet_expandPlacement, hindex.2]
  rw [expanded_abstractTrace_last_eq_fold start.initial start.occupied_nonempty
    start.packetPartition schedule.abstractTrace (initial_packets_saturated _ _), schedule.records]
  have initial : (packetSet (canonicalPlacement start.initial start.occupied_nonempty)).image
      (expandBlock (siteLabels start.initial)) = C.packetAtoms := by
    rw [← packetSet_expandPlacement, ← initial_placement_interprets, start.packetSet_initial]
  rw [initial, path.terminalCircle_packetAtoms_eq_fold]

theorem compatibleEndpoint_packetRank {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d : ℕ} (path : Schedule C d)
    (schedule : AdmissibleSchedule start.initial start.occupied_nonempty path.records)
    {target : Placement n (Finset α)} (compatible : CompatibleEndpoint schedule target) :
    packetRank target = path.terminalCircle.rank := by
  unfold packetRank
  rw [compatibleEndpoint_packetAtoms start path schedule compatible,
    path.terminalCircle.card_packetAtoms]

/-- Read survivors from the literal target and the fixed initial circle alone. -/
noncomputable def survivorsOfLiteralEndpoint {C : MarkedCircle α} [NeZero C.rank]
    (_start : LiteralPacketStart C n) (target : Placement n (Finset α)) : Finset α :=
  MarkedCircle.visibleBoundaries C.boundaries C.boundarySuccessor (packetSet target)

theorem survivorsOfLiteralEndpoint_eq {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d : ℕ} (path : Schedule C d)
    (schedule : AdmissibleSchedule start.initial start.occupied_nonempty path.records)
    {target : Placement n (Finset α)} (compatible : CompatibleEndpoint schedule target)
    (visible : 2 ≤ path.terminalCircle.rank) :
    survivorsOfLiteralEndpoint start target = C.boundaries \ path.deletions.toFinset := by
  unfold survivorsOfLiteralEndpoint
  rw [compatibleEndpoint_packetAtoms start path schedule compatible]
  exact path.terminalCircle_survivors_recover visible

theorem compatibleEndpoint_same_survivors {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d₁ d₂ : ℕ}
    (first : Schedule C d₁) (second : Schedule C d₂)
    (schedule₁ : AdmissibleSchedule start.initial start.occupied_nonempty first.records)
    (schedule₂ : AdmissibleSchedule start.initial start.occupied_nonempty second.records)
    {target : Placement n (Finset α)}
    (compatible₁ : CompatibleEndpoint schedule₁ target)
    (compatible₂ : CompatibleEndpoint schedule₂ target)
    (visible₁ : 2 ≤ first.terminalCircle.rank) (visible₂ : 2 ≤ second.terminalCircle.rank) :
    C.boundaries \ first.deletions.toFinset = C.boundaries \ second.deletions.toFinset := by
  rw [← survivorsOfLiteralEndpoint_eq start first schedule₁ compatible₁ visible₁,
    ← survivorsOfLiteralEndpoint_eq start second schedule₂ compatible₂ visible₂]

theorem survivorsOfLiteralEndpoint_card {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d : ℕ} (path : Schedule C d)
    (schedule : AdmissibleSchedule start.initial start.occupied_nonempty path.records)
    {target : Placement n (Finset α)} (compatible : CompatibleEndpoint schedule target)
    (visible : 2 ≤ path.terminalCircle.rank) :
    (survivorsOfLiteralEndpoint start target).card = path.terminalCircle.rank := by
  rw [survivorsOfLiteralEndpoint_eq start path schedule compatible visible,
    ← path.terminalCircle_boundaries_eq_survivors, path.terminalCircle.card_boundaries]

/-- The survivor identity for the actual literal-endpoint subtype. The joint
realization witness is used only in this propositional proof, not to define
the recovered survivor data. -/
theorem actualLiteralEndpoint_survivors_eq {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d : ℕ} (path : Schedule C d)
    (target : ActualLiteralEndpointFiber start path)
    (visible : 2 ≤ path.terminalCircle.rank) :
    survivorsOfLiteralEndpoint start target.1 = C.boundaries \ path.deletions.toFinset := by
  obtain ⟨bridge⟩ := target.2
  exact survivorsOfLiteralEndpoint_eq start path bridge.schedule bridge.compatible visible

theorem actualLiteralEndpoint_same_survivors {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d₁ d₂ : ℕ}
    (first : Schedule C d₁) (second : Schedule C d₂)
    {target : Placement n (Finset α)}
    (firstActual : Nonempty (ActualJointBridge start first target))
    (secondActual : Nonempty (ActualJointBridge start second target))
    (visible : 2 ≤ packetRank target) :
    C.boundaries \ first.deletions.toFinset = C.boundaries \ second.deletions.toFinset := by
  obtain ⟨firstBridge⟩ := firstActual
  obtain ⟨secondBridge⟩ := secondActual
  have visible₁ : 2 ≤ first.terminalCircle.rank := by
    rwa [← compatibleEndpoint_packetRank start first firstBridge.schedule firstBridge.compatible]
  have visible₂ : 2 ≤ second.terminalCircle.rank := by
    rwa [← compatibleEndpoint_packetRank start second secondBridge.schedule secondBridge.compatible]
  exact compatibleEndpoint_same_survivors start first second firstBridge.schedule
    secondBridge.schedule firstBridge.compatible secondBridge.compatible visible₁ visible₂

end FusionLogEnumeration
