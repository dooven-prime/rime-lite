import FusionLogEnumeration.RawLogFiber

namespace FusionLogEnumeration

open RegisteredAbsorptionChains FusionLogSchedule FusionLogReplay FusionLogInterpretation

variable {α : Type*} [DecidableEq α]
variable {C : MarkedCircle α} {n : ℕ} [NeZero n] [NeZero C.rank]

/-- Actual joint data consist only of a complete ordered event list and a
literal terminal placement. Raw words and their reachability proofs are not
additional elements of the counted type. -/
abbrev RawJoint (F : Finset α) (start : LiteralPacketStart C n) (d : ℕ) :=
  {joint : List (FusionRecord α) × Placement n (Finset α) //
    joint.1.length = d ∧ JointlyAttainable F start.execution joint.1 joint.2}

/-- Forget the schedule representation, retaining its exact event list and
the entire literal endpoint, including packet identities at every site. -/
def scheduleEndpointToRawJoint (F : Finset α) (start : LiteralPacketStart C n)
    {d : ℕ} (hn : 3 ≤ n)
    (joint : Σ path : Schedule C d, ActualLiteralEndpointFiber start path) :
    RawJoint F start d :=
  ⟨(joint.1.records, joint.2.1), joint.1.records_length,
    (actualJointBridge_iff_jointlyAttainable F start joint.1 joint.2.1 hn).mp joint.2.2⟩

theorem scheduleEndpointToRawJoint_injective
    (F : Finset α) (start : LiteralPacketStart C n) {d : ℕ} (hn : 3 ≤ n) :
    Function.Injective (scheduleEndpointToRawJoint F start (d := d) hn) := by
  rintro ⟨first, endpoint₁⟩ ⟨second, endpoint₂⟩ same
  have logs : first.records = second.records :=
    congrArg (fun joint => joint.1.1) same
  have paths : first = second := Schedule.records_injective logs
  subst second
  have targets : endpoint₁ = endpoint₂ :=
    Subtype.ext (congrArg (fun joint => joint.1.2) same)
  cases targets
  rfl

theorem scheduleEndpointToRawJoint_surjective
    (F : Finset α) (start : LiteralPacketStart C n) {d : ℕ} (hn : 3 ≤ n) :
    Function.Surjective (scheduleEndpointToRawJoint F start (d := d) hn) := by
  rintro ⟨⟨events, target⟩, length, actual⟩
  let log : AdmissibleLogs C d :=
    ⟨events, start.jointlyAttainable_logRun F hn actual, length⟩
  let path := admissibleLogsEquivSchedule C d log
  have records : path.records = events := admissibleLogsEquivSchedule_records C d log
  have joint : Nonempty (ActualJointBridge start path target) :=
    (actualJointBridge_iff_jointlyAttainable F start path target hn).mpr (by
      rw [records]
      exact actual)
  exact ⟨⟨path, target, joint⟩, Subtype.ext (Prod.ext records rfl)⟩

/-- The first dependent equivalence is over actual joint data. Surjectivity
uses reverse log admission; injectivity uses full-record injectivity, so the
inverse cannot identify distinct schedules with the same physical endpoint. -/
noncomputable def rawJointEquivSigma
    (F : Finset α) (start : LiteralPacketStart C n) (d : ℕ) (hn : 3 ≤ n) :
    RawJoint F start d ≃
      Σ path : Schedule C d, ActualLiteralEndpointFiber start path :=
  (Equiv.ofBijective (scheduleEndpointToRawJoint F start hn)
    ⟨scheduleEndpointToRawJoint_injective F start hn,
      scheduleEndpointToRawJoint_surjective F start hn⟩).symm

@[simp] theorem rawJointEquivSigma_symm_data
    (F : Finset α) (start : LiteralPacketStart C n) (d : ℕ) (hn : 3 ≤ n)
    (joint : Σ path : Schedule C d, ActualLiteralEndpointFiber start path) :
    ((rawJointEquivSigma F start d hn).symm joint).1 =
      (joint.1.records, joint.2.1) := rfl

/-- Encoding an actual joint object into the dependent sum preserves both
data fields, not just the number of events or occupied sites. -/
theorem rawJointEquivSigma_data
    (F : Finset α) (start : LiteralPacketStart C n) (d : ℕ) (hn : 3 ≤ n)
    (joint : RawJoint F start d) :
    ((rawJointEquivSigma F start d hn joint).1.records,
      (rawJointEquivSigma F start d hn joint).2.1) = joint.1 := by
  exact congrArg Subtype.val ((rawJointEquivSigma F start d hn).symm_apply_apply joint)

/-- Expansion and restoration preserve the number of terminal named packets.
Thus the reference rank in the fixed-log coordinate equivalence is `t-d`,
independently of the schedule or the chosen reference placement. -/
theorem fixedScheduleTerminalReference_rank
    (start : LiteralPacketStart C n) {d : ℕ} (path : Schedule C d)
    (schedule : AdmissibleSchedule start.initial start.occupied_nonempty path.records)
    (hn : 3 ≤ n) :
    (fixedScheduleTerminalReference start path schedule hn).rank = C.rank - d := by
  classical
  let reference := fixedScheduleTerminalReference start path schedule hn
  have expandedCard :
      (schedule.last.image (expandBlock (siteLabels start.initial))).card =
        schedule.last.card := by
    apply Nat.le_antisymm Finset.card_image_le
    calc
      schedule.last.card =
          ((schedule.last.image (expandBlock (siteLabels start.initial))).image
            (restoreBlock start.initial start.occupied_nonempty)).card :=
        congrArg Finset.card (restore_expanded_schedule_last start schedule).symm
      _ ≤ _ := Finset.card_image_le
  have terminalCard : schedule.last.card = path.terminalCircle.rank := by
    rw [← expandedCard, expanded_schedule_last_eq_packetAtoms start path schedule,
      MarkedCircle.card_packetAtoms]
  have count := path.terminalCircle_rank
  change (placedBlocks reference.placed).card = C.rank - d
  rw [← packetSet_eq_placedBlocks reference.placed reference.ordered,
    reference.packets, terminalCard]
  omega

/-- The fixed-log endpoint equivalence, with its rank transported to `t-d`.
No compatibility premise is left for callers to supply. -/
noncomputable def fixedScheduleEndpointChoicesEquiv
    (start : LiteralPacketStart C n) {d : ℕ} (path : Schedule C d) (hn : 3 ≤ n) :
    ActualLiteralEndpointFiber start path ≃ EndpointChoices n (C.rank - d) := by
  let schedule := schedule_admissible_of_literalStart start path
  exact (fixedScheduleLiteralEndpointEquiv start path schedule hn).symm.trans
    (Equiv.cast (congrArg (EndpointChoices n)
      (fixedScheduleTerminalReference_rank start path schedule hn)))

/-- The second dependent equivalence uses the same terminal rank for every
schedule, while preserving the schedule itself as the first component. -/
noncomputable def scheduleEndpointSigmaEquivProduct
    (start : LiteralPacketStart C n) (d : ℕ) (hn : 3 ≤ n) :
    (Σ path : Schedule C d, ActualLiteralEndpointFiber start path) ≃
      Schedule C d × EndpointChoices n (C.rank - d) :=
  (Equiv.sigmaCongrRight fun path => fixedScheduleEndpointChoicesEquiv start path hn).trans {
    toFun := fun joint => (joint.1, joint.2)
    invFun := fun joint => ⟨joint.1, joint.2⟩
    left_inv := fun _ => rfl
    right_inv := fun _ => rfl }

/-- Actual complete-log/literal-endpoint data, not just the abstract product
model, have the product normal form. Both inverse identities are part of the
composed `Equiv`. -/
noncomputable def rawJointEquivProduct
    (F : Finset α) (start : LiteralPacketStart C n) (d : ℕ) (hn : 3 ≤ n) :
    RawJoint F start d ≃ Schedule C d × EndpointChoices n (C.rank - d) :=
  (rawJointEquivSigma F start d hn).trans (scheduleEndpointSigmaEquivProduct start d hn)

/-- Reuse the existing finite count model only after identifying its actual
objects by the two preceding equivalences. -/
noncomputable def rawJointEquivCountModel
    (F : Finset α) (start : LiteralPacketStart C n) (s : ℕ)
    (hn : 3 ≤ n) (bounded : s ≤ C.rank) :
    RawJoint F start (C.rank - s) ≃ JointCountModel C n s := by
  have rank : C.rank - (C.rank - s) = s := by omega
  exact (rawJointEquivProduct F start (C.rank - s) hn).trans {
    toFun := fun joint => ⟨(admissibleLogsEquivSchedule C (C.rank - s)).symm joint.1,
      Equiv.cast (congrArg (EndpointChoices n) rank) joint.2⟩
    invFun := fun joint => (admissibleLogsEquivSchedule C (C.rank - s) joint.1,
      (Equiv.cast (congrArg (EndpointChoices n) rank)).symm joint.2)
    left_inv := by
      intro joint
      apply Prod.ext
      · exact (admissibleLogsEquivSchedule C (C.rank - s)).apply_symm_apply joint.1
      · exact (Equiv.cast (congrArg (EndpointChoices n) rank)).symm_apply_apply joint.2
    right_inv := by intro joint; simp }

@[instance_reducible]
noncomputable def rawJointFintype
    (F : Finset α) (start : LiteralPacketStart C n) (s : ℕ)
    (hn : 3 ≤ n) (bounded : s ≤ C.rank) :
    Fintype (RawJoint F start (C.rank - s)) :=
  Fintype.ofEquiv (JointCountModel C n s)
    (rawJointEquivCountModel F start s hn bounded).symm

/-- Section 5's total exact count, now transported to actual event-list and
literal-placement pairs from the specified concrete initial placement. -/
theorem card_rawJoint
    (F : Finset α) (start : LiteralPacketStart C n) (s : ℕ)
    (hn : 3 ≤ n) (positive : 1 ≤ s) (bounded : s ≤ C.rank) :
    @Fintype.card (RawJoint F start (C.rank - s))
      (rawJointFintype F start s hn bounded) =
        (C.rank.factorial / s.factorial) * (s * Nat.choose n s) := by
  let := rawJointFintype F start s hn bounded
  rw [Fintype.card_congr (rawJointEquivCountModel F start s hn bounded)]
  exact card_jointCountModel C n s positive bounded

/-- Distinct reachable literal targets, with no log or execution word stored
as data. This type is used only after the actual joint equivalence above. -/
abbrev RawLiteralEndpoints (F : Finset α) (start : LiteralPacketStart C n) (s : ℕ) :=
  {target : Placement n (Finset α) //
    packetRank target = s ∧ Nonempty (RawActualLogFiber F start target)}

def rawJointEndpoint (F : Finset α) (start : LiteralPacketStart C n) (s : ℕ)
    (hn : 3 ≤ n) (bounded : s ≤ C.rank)
    (joint : RawJoint F start (C.rank - s)) : RawLiteralEndpoints F start s := by
  refine ⟨joint.1.2, ?_, ⟨joint.1.1, joint.2.2⟩⟩
  have rank := jointlyAttainable_length_add_rank F start hn joint.2.2
  rw [joint.2.1] at rank
  omega

theorem rawJointEndpoint_surjective
    (F : Finset α) (start : LiteralPacketStart C n) (s : ℕ)
    (hn : 3 ≤ n) (bounded : s ≤ C.rank) :
    Function.Surjective (rawJointEndpoint F start s hn bounded) := by
  rintro ⟨target, rank, ⟨events, actual⟩⟩
  have count := jointlyAttainable_length_add_rank F start hn actual
  rw [rank] at count
  exact ⟨⟨(events, target), (show events.length = C.rank - s by omega), actual⟩,
    Subtype.ext rfl⟩

@[instance_reducible]
noncomputable def rawLiteralEndpointsFintype
    (F : Finset α) (start : LiteralPacketStart C n) (s : ℕ)
    (hn : 3 ≤ n) (bounded : s ≤ C.rank) :
    Fintype (RawLiteralEndpoints F start s) := by
  letI := rawJointFintype F start s hn bounded
  exact Fintype.ofSurjective (rawJointEndpoint F start s hn bounded)
    (rawJointEndpoint_surjective F start s hn bounded)

/-- The reverse fibre decomposition. Both maps preserve the exact event list
and literal target; the log length is a consequence of the endpoint rank. -/
def rawJointEquivEndpointLogs
    (F : Finset α) (start : LiteralPacketStart C n) (s : ℕ)
    (hn : 3 ≤ n) (bounded : s ≤ C.rank) :
    RawJoint F start (C.rank - s) ≃
      Σ target : RawLiteralEndpoints F start s, RawActualLogFiber F start target.1 where
  toFun joint := ⟨rawJointEndpoint F start s hn bounded joint, joint.1.1, joint.2.2⟩
  invFun joint := ⟨(joint.2.1, joint.1.1), by
    have count := jointlyAttainable_length_add_rank F start hn joint.2.2
    rw [joint.1.2.1] at count
    exact ⟨(show joint.2.1.length = C.rank - s by omega), joint.2.2⟩⟩
  left_inv _ := Subtype.ext rfl
  right_inv _ := rfl

/-- A consistency identity from the *actual* endpoint/log fibre decomposition,
separate from the proof of the actual joint-object equivalence and count. -/
theorem card_rawLiteralEndpoints_mul_logFiber
    (F : Finset α) (start : LiteralPacketStart C n) (s : ℕ)
    (hn : 3 ≤ n) (bounded : s ≤ C.rank) :
    @Fintype.card (RawLiteralEndpoints F start s)
        (rawLiteralEndpointsFintype F start s hn bounded) *
        (if s = 1 then C.rank.factorial else (C.rank - s).factorial) =
      @Fintype.card (RawJoint F start (C.rank - s))
        (rawJointFintype F start s hn bounded) := by
  classical
  let := rawJointFintype F start s hn bounded
  let := rawLiteralEndpointsFintype F start s hn bounded
  let fiberInstance (target : RawLiteralEndpoints F start s) :
      Fintype (RawActualLogFiber F start target.1) :=
    rawActualLogFiberFintypeOfReachable F start target.1 hn target.2.2
  let := fiberInstance
  have fiberCard (target : RawLiteralEndpoints F start s) :
      Fintype.card (RawActualLogFiber F start target.1) =
        if s = 1 then C.rank.factorial else (C.rank - s).factorial := by
    simpa only [target.2.1] using
      card_rawActualLogFiber_of_reachable F start target.1 hn target.2.2
  have total := Fintype.card_congr (rawJointEquivEndpointLogs F start s hn bounded)
  rw [Fintype.card_sigma] at total
  simpa only [fiberCard, Finset.sum_const, Finset.card_univ, smul_eq_mul] using total.symm

/-- Distinct reachable literal endpoints at visible rank. The factor
`choose t s` is visible boundary data, not coordinate-only information. -/
theorem card_rawLiteralEndpoints
    (F : Finset α) (start : LiteralPacketStart C n) (s : ℕ)
    (hn : 3 ≤ n) (visible : 2 ≤ s) (bounded : s ≤ C.rank) :
    @Fintype.card (RawLiteralEndpoints F start s)
        (rawLiteralEndpointsFintype F start s hn bounded) =
      Nat.choose C.rank s * (s * Nat.choose n s) := by
  have total := card_rawLiteralEndpoints_mul_logFiber F start s hn bounded
  rw [if_neg (by omega), card_rawJoint F start s hn (by omega) bounded] at total
  have quotient : C.rank.factorial / s.factorial =
      Nat.choose C.rank s * (C.rank - s).factorial := by
    apply Nat.div_eq_of_eq_mul_left (Nat.factorial_pos s)
    have factorial := Nat.choose_mul_factorial_mul_factorial bounded
    nlinarith [factorial]
  rw [quotient] at total
  exact Nat.eq_of_mul_eq_mul_right (Nat.factorial_pos (C.rank - s)) (by
    nlinarith [total])

/-- A rank-one literal endpoint has only its physical phase; the invisible
last boundary contributes to its `t!` log fibre, not extra endpoints. -/
theorem card_rawLiteralEndpoints_rankOne
    (F : Finset α) (start : LiteralPacketStart C n) (hn : 3 ≤ n) :
    @Fintype.card (RawLiteralEndpoints F start 1)
        (rawLiteralEndpointsFintype F start 1 hn C.rank_pos) = n := by
  have total := card_rawLiteralEndpoints_mul_logFiber F start 1 hn C.rank_pos
  rw [if_pos rfl, card_rawJoint F start 1 hn (by omega) C.rank_pos] at total
  simp only [Nat.factorial_one, Nat.div_one, Nat.choose_one_right, one_mul] at total
  exact Nat.eq_of_mul_eq_mul_right (Nat.factorial_pos C.rank) (by nlinarith [total])

end FusionLogEnumeration
