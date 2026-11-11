import FusionLogEnumeration.SurvivorLogFiber
import FusionLogEnumeration.RankOneEndpoint
import FusionLogEnumeration.ScheduleAdmission

namespace FusionLogEnumeration

open RegisteredAbsorptionChains FusionLogSchedule FusionLogInterpretation

variable {α : Type*} [DecidableEq α] {n : ℕ} [NeZero n]

/-- The full event list underlying the schedule equivalence is unchanged. -/
theorem admissibleLogsEquivSchedule_records (C : MarkedCircle α) (d : ℕ)
    (log : AdmissibleLogs C d) :
    (admissibleLogsEquivSchedule C d log).records = log.1 := by
  exact congrArg Subtype.val ((admissibleLogsEquivSchedule C d).symm_apply_apply log)

namespace Schedule

/-- The typed initial boundaries still visible after this schedule. -/
def survivorSet {C : MarkedCircle α} {d : ℕ} (path : Schedule C d) :
    Finset C.boundaries := Finset.univ.filter (fun a => a.1 ∉ path.deletions)

theorem survivorSet_image {C : MarkedCircle α} {d : ℕ} (path : Schedule C d) :
    path.survivorSet.image Subtype.val = C.boundaries \ path.deletions.toFinset := by
  ext a
  simp only [survivorSet, Finset.mem_image, Finset.mem_filter, Finset.mem_univ,
    true_and, Finset.mem_sdiff, List.mem_toFinset]
  constructor
  · rintro ⟨b, hb, rfl⟩
    exact ⟨b.2, hb⟩
  · rintro ⟨ha, absent⟩
    exact ⟨⟨a, ha⟩, absent, rfl⟩

def survivorChoices {C : MarkedCircle α} {d : ℕ} (path : Schedule C d) :
    SurvivingBoundaryChoices C (C.rank - d) := ⟨path.survivorSet, by
  have card := congrArg Finset.card path.survivorSet_image
  rw [Finset.card_image_of_injective _ Subtype.val_injective,
    ← path.terminalCircle_boundaries_eq_survivors, path.terminalCircle.card_boundaries] at card
  have rank := path.terminalCircle_rank
  omega⟩

end Schedule

/-- A fibre of complete admissible event lists with actual raw-word joint
realizations at the specified literal target. It counts neither raw words nor
different proofs of realization. This intermediate type uses the M5
`AdmissibleLogs` family. `RawLogFiber.lean` proves that its domain restriction
is automatic for arbitrary actual logs and the prescribed endpoint. -/
abbrev ActualLogFiber {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n) (d : ℕ)
    (target : Placement n (Finset α)) :=
  {log : AdmissibleLogs C d // JointlyAttainable F start.execution log.1 target}

noncomputable instance actualLogFiberFintype {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n) (d : ℕ)
    (target : Placement n (Finset α)) : Fintype (ActualLogFiber F start d target) := by
  classical
  exact Subtype.fintype _

/-- For a visible literal endpoint, actual joint realization imposes exactly
one survivor set. Admission for every comparison log is constructed here,
rather than left as an external hypothesis. -/
noncomputable def actualLogFiberEquivLogsWithSurvivors
    {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n) {d : ℕ}
    (reference : Schedule C d) {target : Placement n (Finset α)}
    (hn : 3 ≤ n) (actual : JointlyAttainable F start.execution reference.records target)
    (visible : 2 ≤ reference.terminalCircle.rank) :
    ActualLogFiber F start d target ≃
      LogsWithSurvivors C (C.rank - d) reference.survivorChoices := by
  have rank := reference.terminalCircle_rank
  have dd : C.rank - (C.rank - d) = d := by omega
  let e := admissibleLogsEquivSchedule C d
  have criterion (log : AdmissibleLogs C d) :
      JointlyAttainable F start.execution log.1 target ↔
        C.boundaries \ (e log).deletions.toFinset =
          reference.survivorChoices.1.image Subtype.val := by
    let path := e log
    have rank₂ := path.terminalCircle_rank
    have records : path.records = log.1 := admissibleLogsEquivSchedule_records C d log
    rw [← records]
    have result := jointlyAttainable_iff_same_survivors F start reference path hn actual
      (schedule_admissible_of_literalStart start path) visible (by omega)
    rw [Schedule.survivorChoices, Schedule.survivorSet_image]
    exact result.trans (eq_comm)
  unfold LogsWithSurvivors
  rw [dd]
  exact Equiv.subtypeEquivRight criterion

/-- The actual fixed-target fibre is a permutation of the missing visible
boundaries. Its elements retain the entire ordered parent/result tuples. -/
noncomputable def actualLogFiberEquivFixedSurvivorDeletionOrders
    {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n) {d : ℕ}
    (reference : Schedule C d) {target : Placement n (Finset α)}
    (hn : 3 ≤ n) (actual : JointlyAttainable F start.execution reference.records target)
    (visible : 2 ≤ reference.terminalCircle.rank) :
    ActualLogFiber F start d target ≃
      FixedSurvivorDeletionOrders C (C.rank - d) reference.survivorChoices := by
  have rank := reference.terminalCircle_rank
  exact (actualLogFiberEquivLogsWithSurvivors F start reference hn actual visible).trans
    (logsWithSurvivorsEquivFixedSurvivorDeletionOrders C (C.rank - d)
      (by omega) (by omega) reference.survivorChoices)

theorem card_actualLogFiber {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n) {d : ℕ}
    (reference : Schedule C d) {target : Placement n (Finset α)}
    (hn : 3 ≤ n) (actual : JointlyAttainable F start.execution reference.records target)
    (visible : 2 ≤ reference.terminalCircle.rank) :
    Fintype.card (ActualLogFiber F start d target) = d.factorial := by
  rw [Fintype.card_congr
    (actualLogFiberEquivFixedSurvivorDeletionOrders F start reference hn actual visible),
    card_fixedSurvivorDeletionOrders]
  have := reference.terminalCircle_rank
  congr 1
  omega

/-- Rank one deliberately forgets the last survivor. Every complete directed
contraction log can be realized at the same literal target phase. -/
noncomputable def actualLogFiberRankOneEquiv
    {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n) {d : ℕ}
    (reference : Schedule C d) {target : Placement n (Finset α)}
    (hn : 3 ≤ n) (actual : JointlyAttainable F start.execution reference.records target)
    (one : reference.terminalCircle.rank = 1) :
    ActualLogFiber F start d target ≃ AdmissibleLogs C d := by
  have all (log : AdmissibleLogs C d) : JointlyAttainable F start.execution log.1 target := by
    obtain ⟨bridge⟩ :=
      (actualJointBridge_iff_jointlyAttainable F start reference target hn).mpr actual
    let path := admissibleLogsEquivSchedule C d log
    have rank := path.terminalCircle_rank
    have referenceRank := reference.terminalCircle_rank
    have pathOne : path.terminalCircle.rank = 1 := by omega
    let schedule := schedule_admissible_of_literalStart start path
    have compatible := compatibleEndpoint_of_rankOne start reference path bridge.schedule schedule
      bridge.compatible one pathOne
    have result := (actualJointBridge_iff_jointlyAttainable F start path target hn).mp
      ⟨⟨schedule, compatible⟩⟩
    simpa only [path, admissibleLogsEquivSchedule_records] using result
  exact { toFun := Subtype.val
          invFun := fun log => ⟨log, all log⟩
          left_inv := fun _ => Subtype.ext rfl
          right_inv := fun _ => rfl }

theorem card_actualLogFiber_rankOne {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n) {d : ℕ}
    (reference : Schedule C d) {target : Placement n (Finset α)}
    (hn : 3 ≤ n) (actual : JointlyAttainable F start.execution reference.records target)
    (one : reference.terminalCircle.rank = 1) :
    Fintype.card (ActualLogFiber F start d target) = C.rank.factorial := by
  rw [Fintype.card_congr (actualLogFiberRankOneEquiv F start reference hn actual one)]
  have rank := reference.terminalCircle_rank
  have eqd : d = C.rank - 1 := by omega
  rw [eqd, card_admissibleLogs_rank C 1 (by omega) (by omega)]
  simp

end FusionLogEnumeration
