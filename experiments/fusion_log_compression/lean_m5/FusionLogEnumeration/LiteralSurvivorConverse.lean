import FusionLogEnumeration.LiteralSurvivorRecovery
import FusionLogEnumeration.SurvivorConverse

namespace FusionLogEnumeration

open RegisteredAbsorptionChains FusionLogSchedule FusionLogReplay FusionLogInterpretation

variable {α : Type*} [DecidableEq α]
variable {n : ℕ} [NeZero n]

/-- Expansion of the final indexed packet partition gives exactly the M5
terminal literal blocks, whether or not an endpoint has yet been chosen. -/
theorem expanded_schedule_last_eq_packetAtoms {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d : ℕ} (path : Schedule C d)
    (schedule : AdmissibleSchedule start.initial start.occupied_nonempty path.records) :
    schedule.last.image (expandBlock (siteLabels start.initial)) =
      path.terminalCircle.packetAtoms := by
  rw [expanded_abstractTrace_last_eq_fold start.initial start.occupied_nonempty
    start.packetPartition schedule.abstractTrace (initial_packets_saturated _ _), schedule.records]
  have initial : (packetSet (canonicalPlacement start.initial start.occupied_nonempty)).image
      (expandBlock (siteLabels start.initial)) = C.packetAtoms := by
    rw [← packetSet_expandPlacement, ← initial_placement_interprets, start.packetSet_initial]
  rw [initial, path.terminalCircle_packetAtoms_eq_fold]

theorem restore_expanded_schedule_last {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {events : List (FusionRecord α)}
    (schedule : AdmissibleSchedule start.initial start.occupied_nonempty events) :
    (schedule.last.image (expandBlock (siteLabels start.initial))).image
      (restoreBlock start.initial start.occupied_nonempty) = schedule.last := by
  have saturated := schedule.abstractTrace.preserves_saturation
    (initial_packets_saturated start.initial start.occupied_nonempty)
  rw [Finset.image_image]
  calc
    _ = schedule.last.image id := Finset.image_congr (fun A hA =>
      restore_expandBlock start.initial start.occupied_nonempty start.packetPartition A
        (saturated A hA))
    _ = _ := Finset.image_id

/-- Equal visible survivors determine the same terminal indexed partition.
No equality of the intermediate physical placements is assumed. -/
theorem schedule_last_eq_of_same_survivors {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d₁ d₂ : ℕ}
    (first : Schedule C d₁) (second : Schedule C d₂)
    (schedule₁ : AdmissibleSchedule start.initial start.occupied_nonempty first.records)
    (schedule₂ : AdmissibleSchedule start.initial start.occupied_nonempty second.records)
    (visible₁ : 2 ≤ first.terminalCircle.rank) (visible₂ : 2 ≤ second.terminalCircle.rank)
    (same : C.boundaries \ first.deletions.toFinset =
      C.boundaries \ second.deletions.toFinset) : schedule₁.last = schedule₂.last := by
  have packets := first.terminalCircle_packetAtoms_eq_of_same_survivors second
    visible₁ visible₂ same
  have expanded : schedule₁.last.image (expandBlock (siteLabels start.initial)) =
      schedule₂.last.image (expandBlock (siteLabels start.initial)) := by
    rw [expanded_schedule_last_eq_packetAtoms start first schedule₁,
      expanded_schedule_last_eq_packetAtoms start second schedule₂, packets]
  have restored := congrArg (Finset.image (restoreBlock start.initial start.occupied_nonempty))
    expanded
  simpa only [restore_expanded_schedule_last] using restored

/-- The converse endpoint theorem: changing only the deletion order preserves
compatibility with this very same literal target, including all physical sites.
Both logs are supplied with their M4-D admissibility proofs. -/
theorem compatibleEndpoint_of_same_survivors {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d₁ d₂ : ℕ}
    (first : Schedule C d₁) (second : Schedule C d₂)
    (schedule₁ : AdmissibleSchedule start.initial start.occupied_nonempty first.records)
    (schedule₂ : AdmissibleSchedule start.initial start.occupied_nonempty second.records)
    {target : Placement n (Finset α)}
    (compatible₁ : CompatibleEndpoint schedule₁ target)
    (visible₁ : 2 ≤ first.terminalCircle.rank) (visible₂ : 2 ≤ second.terminalCircle.rank)
    (same : C.boundaries \ first.deletions.toFinset =
      C.boundaries \ second.deletions.toFinset) : CompatibleEndpoint schedule₂ target := by
  have last := schedule_last_eq_of_same_survivors start first second schedule₁ schedule₂
    visible₁ visible₂ same
  obtain ⟨indexTarget, hindex, expanded⟩ := compatible₁
  exact ⟨indexTarget, ⟨hindex.1, hindex.2.trans last⟩, expanded⟩

/-- Relative to one compatible log, literal-endpoint compatibility is
equivalent to equality of the visible surviving boundary sets. -/
theorem compatibleEndpoint_iff_same_survivors {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d₁ d₂ : ℕ}
    (first : Schedule C d₁) (second : Schedule C d₂)
    (schedule₁ : AdmissibleSchedule start.initial start.occupied_nonempty first.records)
    (schedule₂ : AdmissibleSchedule start.initial start.occupied_nonempty second.records)
    {target : Placement n (Finset α)}
    (compatible₁ : CompatibleEndpoint schedule₁ target)
    (visible₁ : 2 ≤ first.terminalCircle.rank) (visible₂ : 2 ≤ second.terminalCircle.rank) :
    CompatibleEndpoint schedule₂ target ↔
      C.boundaries \ first.deletions.toFinset = C.boundaries \ second.deletions.toFinset :=
  ⟨fun compatible₂ => compatibleEndpoint_same_survivors start first second schedule₁ schedule₂
      compatible₁ compatible₂ visible₁ visible₂,
    compatibleEndpoint_of_same_survivors start first second schedule₁ schedule₂
      compatible₁ visible₁ visible₂⟩

/-- Actual joint realizability of the same literal endpoint, not just a
coordinate-only fibre, is preserved under reordering the deleted boundaries.
The supplied admissibility of the comparison log is essential. -/
theorem actualLiteralEndpoint_iff_same_survivors {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d₁ d₂ : ℕ}
    (first : Schedule C d₁) (second : Schedule C d₂)
    {target : Placement n (Finset α)}
    (firstActual : Nonempty (ActualJointBridge start first target))
    (schedule₂ : AdmissibleSchedule start.initial start.occupied_nonempty second.records)
    (visible₁ : 2 ≤ first.terminalCircle.rank) (visible₂ : 2 ≤ second.terminalCircle.rank) :
    Nonempty (ActualJointBridge start second target) ↔
      C.boundaries \ first.deletions.toFinset = C.boundaries \ second.deletions.toFinset := by
  obtain ⟨bridge₁⟩ := firstActual
  constructor
  · rintro ⟨bridge₂⟩
    exact compatibleEndpoint_same_survivors start first second bridge₁.schedule bridge₂.schedule
      bridge₁.compatible bridge₂.compatible visible₁ visible₂
  · intro same
    exact ⟨⟨schedule₂, compatibleEndpoint_of_same_survivors start first second
      bridge₁.schedule schedule₂ bridge₁.compatible visible₁ visible₂ same⟩⟩

/-- Reordering a fixed deleted-boundary set induces the identity on literal
endpoints. Only the attached log-realization proof changes. -/
def actualLiteralEndpointFiberEquivOfSameSurvivors
    {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d₁ d₂ : ℕ}
    (first : Schedule C d₁) (second : Schedule C d₂)
    (schedule₁ : AdmissibleSchedule start.initial start.occupied_nonempty first.records)
    (schedule₂ : AdmissibleSchedule start.initial start.occupied_nonempty second.records)
    (visible₁ : 2 ≤ first.terminalCircle.rank) (visible₂ : 2 ≤ second.terminalCircle.rank)
    (same : C.boundaries \ first.deletions.toFinset =
      C.boundaries \ second.deletions.toFinset) :
    ActualLiteralEndpointFiber start first ≃ ActualLiteralEndpointFiber start second where
  toFun target := ⟨target.1, (actualLiteralEndpoint_iff_same_survivors start first second
    target.2 schedule₂ visible₁ visible₂).mpr same⟩
  invFun target := ⟨target.1, (actualLiteralEndpoint_iff_same_survivors start second first
    target.2 schedule₁ visible₂ visible₁).mpr same.symm⟩
  left_inv _ := Subtype.ext rfl
  right_inv _ := Subtype.ext rfl

/-- The criterion descends to actual raw execution words via M4-D joint
realization, preserving the complete ordered event tuples and literal target. -/
theorem jointlyAttainable_iff_same_survivors {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n) {d₁ d₂ : ℕ}
    (first : Schedule C d₁) (second : Schedule C d₂)
    {target : Placement n (Finset α)} (hn : 3 ≤ n)
    (firstJoint : JointlyAttainable F start.execution first.records target)
    (schedule₂ : AdmissibleSchedule start.initial start.occupied_nonempty second.records)
    (visible₁ : 2 ≤ first.terminalCircle.rank) (visible₂ : 2 ≤ second.terminalCircle.rank) :
    JointlyAttainable F start.execution second.records target ↔
      C.boundaries \ first.deletions.toFinset = C.boundaries \ second.deletions.toFinset := by
  rw [← actualJointBridge_iff_jointlyAttainable F start second target hn]
  exact actualLiteralEndpoint_iff_same_survivors start first second
    ((actualJointBridge_iff_jointlyAttainable F start first target hn).mpr firstJoint)
    schedule₂ visible₁ visible₂

end FusionLogEnumeration
