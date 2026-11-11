import FusionLogEnumeration.ActualLogFiber
import FusionLogEnumeration.LogCompleteness

namespace FusionLogEnumeration

open RegisteredAbsorptionChains FusionLogSchedule FusionLogReplay

variable {α : Type*} [DecidableEq α] {n : ℕ} [NeZero n]

/-- All complete event lists jointly realized with this exact literal target.
There is no schedule-admissibility or event-count premise in this definition. -/
abbrev RawActualLogFiber {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n)
    (target : Placement n (Finset α)) :=
  {events : List (FusionRecord α) // JointlyAttainable F start.execution events target}

/-- A fixed literal endpoint determines the event count for every actual log.
The proof uses completeness, then the terminal physical packet-rank theorem. -/
theorem jointlyAttainable_length_add_rank {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n)
    {events : List (FusionRecord α)} {target : Placement n (Finset α)}
    (hn : 3 ≤ n) (actual : JointlyAttainable F start.execution events target) :
    events.length + packetRank target = C.rank := by
  obtain ⟨path, records⟩ := (start.jointlyAttainable_logRun F hn actual).exists_schedule
  have joint : JointlyAttainable F start.execution path.records target := by rwa [records]
  obtain ⟨bridge⟩ := (actualJointBridge_iff_jointlyAttainable F start path target hn).mpr joint
  have rank := compatibleEndpoint_packetRank start path bridge.schedule bridge.compatible
  have count := path.terminalCircle_rank
  omega

/-- Completeness removes both apparent restrictions from the intermediate
fibre: raw logs are automatically M5-admissible and have the correct length.
Both maps leave the complete ordered event list unchanged. -/
noncomputable def rawActualLogFiberEquiv {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n) {d : ℕ}
    (reference : Schedule C d) {target : Placement n (Finset α)}
    (hn : 3 ≤ n) (actual : JointlyAttainable F start.execution reference.records target) :
    RawActualLogFiber F start target ≃ ActualLogFiber F start d target := by
  have length (log : RawActualLogFiber F start target) : log.1.length = d := by
    have first := jointlyAttainable_length_add_rank F start hn log.2
    have second := jointlyAttainable_length_add_rank F start hn actual
    rw [reference.records_length] at second
    omega
  exact {
    toFun := fun log => ⟨⟨log.1, start.jointlyAttainable_logRun F hn log.2, length log⟩, log.2⟩
    invFun := fun log => ⟨log.1.1, log.2⟩
    left_inv := fun _ => Subtype.ext rfl
    right_inv := fun _ => Subtype.ext (Subtype.ext rfl) }

/-- The actual literal-endpoint history fibre, with no preselected admissible
log domain, is exactly the permutations of the deleted original boundaries. -/
noncomputable def rawActualLogFiberEquivFixedSurvivorDeletionOrders
    {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n) {d : ℕ}
    (reference : Schedule C d) {target : Placement n (Finset α)}
    (hn : 3 ≤ n) (actual : JointlyAttainable F start.execution reference.records target)
    (visible : 2 ≤ reference.terminalCircle.rank) :
    RawActualLogFiber F start target ≃
      FixedSurvivorDeletionOrders C (C.rank - d) reference.survivorChoices :=
  (rawActualLogFiberEquiv F start reference hn actual).trans
    (actualLogFiberEquivFixedSurvivorDeletionOrders F start reference hn actual visible)

@[instance_reducible]
noncomputable def rawActualLogFiberFintype {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n) {d : ℕ}
    (reference : Schedule C d) {target : Placement n (Finset α)}
    (hn : 3 ≤ n) (actual : JointlyAttainable F start.execution reference.records target) :
    Fintype (RawActualLogFiber F start target) :=
  Fintype.ofEquiv (ActualLogFiber F start d target)
    (rawActualLogFiberEquiv F start reference hn actual).symm

theorem card_rawActualLogFiber {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n) {d : ℕ}
    (reference : Schedule C d) {target : Placement n (Finset α)}
    (hn : 3 ≤ n) (actual : JointlyAttainable F start.execution reference.records target)
    (visible : 2 ≤ reference.terminalCircle.rank) :
    @Fintype.card (RawActualLogFiber F start target)
      (rawActualLogFiberFintype F start reference hn actual) = d.factorial := by
  let := rawActualLogFiberFintype F start reference hn actual
  rw [Fintype.card_congr (rawActualLogFiberEquiv F start reference hn actual)]
  exact card_actualLogFiber F start reference hn actual visible

/-- At rank one every admissible complete log, including its last ordered
rank-two event, lies over the same specified literal endpoint. -/
noncomputable def rawActualLogFiberRankOneEquiv
    {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n) {d : ℕ}
    (reference : Schedule C d) {target : Placement n (Finset α)}
    (hn : 3 ≤ n) (actual : JointlyAttainable F start.execution reference.records target)
    (one : reference.terminalCircle.rank = 1) :
    RawActualLogFiber F start target ≃ AdmissibleLogs C d :=
  (rawActualLogFiberEquiv F start reference hn actual).trans
    (actualLogFiberRankOneEquiv F start reference hn actual one)

theorem card_rawActualLogFiber_rankOne {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n) {d : ℕ}
    (reference : Schedule C d) {target : Placement n (Finset α)}
    (hn : 3 ≤ n) (actual : JointlyAttainable F start.execution reference.records target)
    (one : reference.terminalCircle.rank = 1) :
    @Fintype.card (RawActualLogFiber F start target)
      (rawActualLogFiberFintype F start reference hn actual) = C.rank.factorial := by
  let := rawActualLogFiberFintype F start reference hn actual
  rw [Fintype.card_congr (rawActualLogFiberEquiv F start reference hn actual)]
  exact card_actualLogFiber_rankOne F start reference hn actual one

/-- A reachable literal endpoint supplies a finite history fibre without
requiring a chosen M5 schedule in the public interface. -/
@[instance_reducible]
noncomputable def rawActualLogFiberFintypeOfReachable
    {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n)
    (target : Placement n (Finset α)) (hn : 3 ≤ n)
    (reachable : Nonempty (RawActualLogFiber F start target)) :
    Fintype (RawActualLogFiber F start target) := by
  let log := Classical.choice reachable
  let run := start.jointlyAttainable_logRun F hn log.2
  let path := Classical.choose run.exists_schedule
  have records : path.records = log.1 := Classical.choose_spec run.exists_schedule
  exact rawActualLogFiberFintype F start path hn (by rw [records]; exact log.2)

/-- Section 5's literal history-fibre formula for every reachable target.
The exceptional rank-one value counts both final parent directions and all
choices of the now-invisible last boundary. -/
theorem card_rawActualLogFiber_of_reachable
    {C : MarkedCircle α} [NeZero C.rank]
    (F : Finset α) (start : LiteralPacketStart C n)
    (target : Placement n (Finset α)) (hn : 3 ≤ n)
    (reachable : Nonempty (RawActualLogFiber F start target)) :
    @Fintype.card (RawActualLogFiber F start target)
      (rawActualLogFiberFintypeOfReachable F start target hn reachable) =
        if packetRank target = 1 then C.rank.factorial
        else (C.rank - packetRank target).factorial := by
  classical
  let log := Classical.choice reachable
  obtain ⟨path, records⟩ := (start.jointlyAttainable_logRun F hn log.2).exists_schedule
  have actual : JointlyAttainable F start.execution path.records target := by
    rw [records]
    exact log.2
  obtain ⟨bridge⟩ := (actualJointBridge_iff_jointlyAttainable F start path target hn).mpr actual
  have rank := compatibleEndpoint_packetRank start path bridge.schedule bridge.compatible
  rw [show rawActualLogFiberFintypeOfReachable F start target hn reachable =
    rawActualLogFiberFintype F start path hn actual from Subsingleton.elim _ _]
  by_cases one : packetRank target = 1
  · rw [if_pos one]
    exact card_rawActualLogFiber_rankOne F start path hn actual (rank.symm.trans one)
  · rw [if_neg one]
    have positive := path.terminalCircle.rank_pos
    have count := path.terminalCircle_rank
    have visible : 2 ≤ path.terminalCircle.rank := by omega
    have result := card_rawActualLogFiber F start path hn actual visible
    have length : log.1.length = C.rank - packetRank target := by omega
    simpa only [length] using result

end FusionLogEnumeration
