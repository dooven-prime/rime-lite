import FusionLogEnumeration.LiteralSurvivorConverse

namespace FusionLogEnumeration

open RegisteredAbsorptionChains FusionLogSchedule FusionLogInterpretation

variable {α : Type*} [DecidableEq α] {n : ℕ} [NeZero n]

namespace MarkedCircle

/-- A rank-one physical partition cannot reveal its last boundary marker. -/
theorem packetAtoms_eq_singleton_atomUnion (C : MarkedCircle α) (one : C.rank = 1) :
    C.packetAtoms = {C.atomUnion} := by
  obtain ⟨p, hp⟩ := List.length_eq_one_iff.mp one
  simp [packetAtoms, atomUnion, hp]

end MarkedCircle

namespace Schedule

theorem terminalCircle_packetAtoms_rankOne {C : MarkedCircle α} {d : ℕ}
    (path : Schedule C d) (one : path.terminalCircle.rank = 1) :
    path.terminalCircle.packetAtoms = {C.atomUnion} := by
  rw [path.terminalCircle.packetAtoms_eq_singleton_atomUnion one, path.terminalCircle_atomUnion]

end Schedule

/-- All complete contractions have the same terminal indexed packet set,
including logs with different last surviving boundary labels. -/
theorem schedule_last_eq_of_rankOne {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d₁ d₂ : ℕ}
    (first : Schedule C d₁) (second : Schedule C d₂)
    (schedule₁ : AdmissibleSchedule start.initial start.occupied_nonempty first.records)
    (schedule₂ : AdmissibleSchedule start.initial start.occupied_nonempty second.records)
    (one₁ : first.terminalCircle.rank = 1) (one₂ : second.terminalCircle.rank = 1) :
    schedule₁.last = schedule₂.last := by
  have expanded : schedule₁.last.image (expandBlock (siteLabels start.initial)) =
      schedule₂.last.image (expandBlock (siteLabels start.initial)) := by
    rw [expanded_schedule_last_eq_packetAtoms start first schedule₁,
      expanded_schedule_last_eq_packetAtoms start second schedule₂,
      first.terminalCircle_packetAtoms_rankOne one₁,
      second.terminalCircle_packetAtoms_rankOne one₂]
  have restored := congrArg (Finset.image (restoreBlock start.initial start.occupied_nonempty))
    expanded
  simpa only [restore_expanded_schedule_last] using restored

/-- Any complete contraction log is compatible with the same rank-one literal
target, with its exact physical phase unchanged. -/
theorem compatibleEndpoint_of_rankOne {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d₁ d₂ : ℕ}
    (first : Schedule C d₁) (second : Schedule C d₂)
    (schedule₁ : AdmissibleSchedule start.initial start.occupied_nonempty first.records)
    (schedule₂ : AdmissibleSchedule start.initial start.occupied_nonempty second.records)
    {target : Placement n (Finset α)}
    (compatible : CompatibleEndpoint schedule₁ target)
    (one₁ : first.terminalCircle.rank = 1) (one₂ : second.terminalCircle.rank = 1) :
    CompatibleEndpoint schedule₂ target := by
  obtain ⟨indexTarget, hindex, expanded⟩ := compatible
  exact ⟨indexTarget, ⟨hindex.1, hindex.2.trans
    (schedule_last_eq_of_rankOne start first second schedule₁ schedule₂ one₁ one₂)⟩, expanded⟩

end FusionLogEnumeration
