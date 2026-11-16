import RSR2.AntipodalFusionGate
import RSR2.PacketRankLedger
import RSR2.AntipodalLinearWitness

/-! # Arbitrary-history raw-length lower bound for antipodal partitions -/

namespace RSR2.Parametric

theorem antipodal_endpoint_totalPacketCount (m : Nat) (Q : Placement (2 * m))
    (htarget : AntipodalEndpoint m Q) : totalPacketCount Q = m := by
  let reps := (List.finRange m).map (fun i => Q (antipodalLeft m i))
  have hnd : reps.Nodup := by
    apply (List.nodup_finRange m).map
    intro a b hne he
    apply hne
    apply Fin.ext
    have h := (htarget _ _).mp he
    simpa only [antipodalLabel_left] using h
  have hmem : ∀ loc, loc ∈ reps ↔ ∃ a, Q a = loc := by
    intro loc
    constructor
    · intro h
      obtain ⟨i, _, hi⟩ := List.mem_map.mp h
      exact ⟨antipodalLeft m i, hi⟩
    · rintro ⟨a, rfl⟩
      obtain ⟨i, ha⟩ := antipodal_atom_cases m a
      apply List.mem_map.mpr
      refine ⟨i, List.mem_finRange i, ?_⟩
      rcases ha with rfl | rfl
      · rfl
      · exact (htarget _ _).mpr (by simp only [antipodalLabel_left, antipodalLabel_right])
  have h := totalPacketCount_eq_representatives_length Q reps hnd hmem
  simpa [reps] using h

theorem antipodal_run_fusion_counts
    (m : Nat) (hm : 0 < m) (Q : Placement (2 * m)) (word : List Letter)
    (hrun : run (2 * m) (by omega) (seed (2 * m)) word = some Q)
    (htarget : AntipodalEndpoint m Q) :
    ∃ f0 f1, runWithPacketRankLedger (2 * m) (by omega) (seed (2 * m)) word =
      some (Q, f0, f1) ∧ f0 + f1 = m ∧ f0 ≤ 1 ∧ m - 1 ≤ f1 ∧
        f1 ≤ rawUpperDefectCount word := by
  obtain ⟨f0, f1, hl⟩ := run_exists_packetRankLedger (2 * m) (by omega) _ Q word hrun
  obtain ⟨f, z, hlow, hf⟩ := antipodal_lower_fusion_gate m hm Q word hrun htarget
  have hagree := runWithPacketRankLedger_lower_agreement (2 * m) (by omega) (seed (2 * m)) word
  rw [hl, hlow] at hagree
  have he : f0 = f := (Prod.mk.inj (Option.some.inj hagree)).2
  have hb := runWithPacketRankLedger_balance (2 * m) (by omega) _ Q word f0 f1 hl
  rw [antipodal_endpoint_totalPacketCount m Q htarget, seed_totalPacketCount] at hb
  refine ⟨f0, f1, hl, ?_, ?_, ?_, hb.2⟩ <;> omega

theorem antipodal_run_upperDefectCount_lower_bound
    (m : Nat) (hm : 0 < m) (Q : Placement (2 * m)) (word : List Letter)
    (hrun : run (2 * m) (by omega) (seed (2 * m)) word = some Q)
    (htarget : AntipodalEndpoint m Q) :
    m - 1 ≤ rawUpperDefectCount word := by
  obtain ⟨_, _, _, _, _, hf, hd⟩ := antipodal_run_fusion_counts m hm Q word hrun htarget
  omega

/-- The three costs charge disjoint classes of letters in the original word. -/
theorem antipodal_run_length_lower_bound
    (m : Nat) (hm : 2 ≤ m) (Q : Placement (2 * m)) (word : List Letter)
    (hrun : run (2 * m) (by omega) (seed (2 * m)) word = some Q)
    (htarget : AntipodalEndpoint m Q) :
    7 * m - 7 ≤ word.length := by
  have hp := antipodal_run_lowerPortCost_lower_bound m hm Q word hrun htarget
  have hr := antipodal_run_upperRotationCount_lower_bound m (by omega) Q word hrun htarget
  have hd := antipodal_run_upperDefectCount_lower_bound m (by omega) Q word hrun htarget
  have hl := word_length_eq_lowerPortCost_add_upper word
  omega

/-- A feasible length for the unordered partition, with no prescribed layer
allocation or literal endpoint. The word and endpoint are not counted. -/
def AntipodalRealizableLength (m : Nat) (hm : 0 < m) (length : Nat) : Prop :=
  ∃ word Q, run (2 * m) (by omega) (seed (2 * m)) word = some Q ∧
    AntipodalEndpoint m Q ∧ word.length = length

theorem antipodal_realizable_length_exists (m : Nat) (hm : 0 < m) :
    ∃ length, AntipodalRealizableLength m hm length := by
  exact ⟨9 * m - 2, antipodalLinearWord m, antipodalSpacedEndpoint m hm,
    antipodal_linear_word_realizes m hm, antipodalSpacedEndpoint_partition m hm,
    antipodal_linear_word_length m hm⟩

/-- Two-sided bounds without fixing an endpoint: every feasible length obeys
the lower bound, and the displayed upper length has an actual witness. -/
theorem antipodal_partition_length_bounds (m : Nat) (hm : 2 ≤ m) :
    (∀ length, AntipodalRealizableLength m (by omega) length → 7 * m - 7 ≤ length) ∧
      AntipodalRealizableLength m (by omega) (9 * m - 2) := by
  constructor
  · rintro length ⟨word, Q, hrun, htarget, hlength⟩
    have hl := antipodal_run_length_lower_bound m hm Q word hrun htarget
    omega
  · exact ⟨antipodalLinearWord m, antipodalSpacedEndpoint m (by omega),
      antipodal_linear_word_realizes m (by omega), antipodalSpacedEndpoint_partition m (by omega),
      antipodal_linear_word_length m (by omega)⟩

/-- Port-cost comparison uses the same arbitrary-history lower bound and
the same explicit upper witness; it does not assert either endpoint is optimal. -/
theorem antipodal_partition_port_bounds (m : Nat) (hm : 2 ≤ m) :
    (∀ Q word, run (2 * m) (by omega) (seed (2 * m)) word = some Q →
      AntipodalEndpoint m Q → 4 * m - 3 ≤ lowerPortCost word) ∧
      ∃ Q word, run (2 * m) (by omega) (seed (2 * m)) word = some Q ∧
        AntipodalEndpoint m Q ∧ lowerPortCost word = 4 * m - 1 := by
  refine ⟨fun Q word hrun htarget =>
    antipodal_run_lowerPortCost_lower_bound m hm Q word hrun htarget, ?_⟩
  exact ⟨antipodalSpacedEndpoint m (by omega), antipodalLinearWord m,
    antipodal_linear_word_realizes m (by omega), antipodalSpacedEndpoint_partition m (by omega),
    (antipodal_linear_word_counts m (by omega)).2.2.2.2.2⟩

end RSR2.Parametric
