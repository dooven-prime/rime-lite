import RegisteredAbsorptionChains.PackedNamedPlacement
import RegisteredAbsorptionChains.CleanCheckpointStep
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n r : ℕ} [NeZero n] [NeZero r]

/-- One named adjacent outside pair yields a concrete singleton-stage
schedule. Its endpoint is the actual fused placement, not an existential
state chosen afresh for a later edge. -/
theorem packed_adjacent_partner_schedule
    (F C : Finset (ZMod n))
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (ordered : first.PositivelyOrdered)
    (hrn : r ≤ n)
    (source : s.placed = first.placed)
    (j : ℕ) (hjpos : 0 < j) (hj : j + 1 < r)
    (hcarrier : first.block 0 = C)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ C)
    (leftOutside : Disjoint C (first.block (j : ZMod r)))
    (rightOutside : Disjoint C (first.block ((j + 1 : ℕ) : ZMod r))) :
    OutsideAssemblySchedule F C s
      ({ s with placed := fusionPlacement ((packedLegalNamed first hrn (-(j : ZMod n))).placed) } :
        Execution n (ZMod n)) := by
  let target := packedLegalNamed first hrn (-(j : ZMod n))
  obtain ⟨h0, h1, qC, hC, hq0, hq1⟩ :=
    packed_outside_ports_with_carrier first hrn j hjpos hj
  have hr : 2 ≤ r := by omega
  have hn : 2 ≤ n := by omega
  exact OutsideAssemblySchedule.merge first target hn hr source
    (packedLegalNamed_same_order first ordered hrn (-(j : ZMod n)))
    (first.block (j : ZMod r))
    (first.block ((j + 1 : ℕ) : ZMod r))
    h0 h1 registered selected inside leftOutside rightOutside
    ⟨qC, by simpa [hcarrier] using hC, hq0, hq1⟩
    (OutsideAssemblySchedule.empty _)

/-- The schedule's endpoint and weak invariant are available together for
the next assembly stage. The same literal word realizes that endpoint. -/
theorem packed_adjacent_partner_stage_exact
    (F C B : Finset (ZMod n))
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (ordered : first.PositivelyOrdered)
    (hrn : r ≤ n)
    (source : s.placed = first.placed)
    (j : ℕ) (hjpos : 0 < j) (hj : j + 1 < r)
    (hcarrier : first.block 0 = C)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ C)
    (leftOutside : Disjoint C (first.block (j : ZMod r)))
    (rightOutside : Disjoint C (first.block ((j + 1 : ℕ) : ZMod r)))
    (leftPartner : first.block (j : ZMod r) ⊆ B)
    (rightPartner : first.block ((j + 1 : ℕ) : ZMod r) ⊆ B)
    (hinvariant : PartnerAssemblyInvariant C B s) :
    let target := packedLegalNamed first hrn (-(j : ZMod n))
    let final := { s with placed := fusionPlacement target.placed }
    ∃ word : List Letter,
      run F s word = final ∧
      final.origin = s.origin ∧ final.chain = s.chain ∧
      PartnerAssemblyInvariant C B final := by
  let target := packedLegalNamed first hrn (-(j : ZMod n))
  let final := { s with placed := fusionPlacement target.placed }
  have schedule := packed_adjacent_partner_schedule F C s first ordered hrn source
    j hjpos hj hcarrier registered selected inside leftOutside rightOutside
  obtain ⟨word, hrun, horigin, hchain⟩ := schedule.realize
  obtain ⟨h0, h1, qC, hC, hq0, hq1⟩ :=
    packed_outside_ports_with_carrier first hrn j hjpos hj
  let prepared : Execution n (ZMod n) := { s with placed := target.placed }
  have hbefore : PartnerAssemblyInvariant C B prepared :=
    partner_invariant_same_named_blocks C B s first target source rfl hinvariant
  have hu : (first.block (j : ZMod r)).Nonempty := first.block_nonempty _
  have hn : 2 ≤ n := by omega
  have hafter := partner_invariant_after_outside_merge F C B
    (first.block (j : ZMod r))
    (first.block ((j + 1 : ℕ) : ZMod r)) prepared hn hbefore
    h0 h1 hu leftPartner rightPartner qC
    (by simpa [hcarrier] using hC) hq0 hq1
  have hfinal : (stepDefect F prepared).placed = final.placed := by
    simp [stepDefect_placed, prepared, final]
  have hfinalInvariant : PartnerAssemblyInvariant C B final := by
    rcases hafter with ⟨⟨q, hq⟩, hrest⟩
    refine ⟨⟨q, ?_⟩, ?_⟩
    · simpa [hfinal] using hq
    · intro q D hD
      exact hrest q D (by simpa [hfinal] using hD)
  exact ⟨word, hrun, horigin, hchain, hfinalInvariant⟩

/-- An adjacent pair of named outside subpackets can be assembled by a
literal word. The target kernel placement is constructed by packing, not
supplied as an existential placement premise. -/
theorem realize_packed_adjacent_partner_stage
    (F C B : Finset (ZMod n))
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (ordered : first.PositivelyOrdered)
    (hrn : r ≤ n)
    (source : s.placed = first.placed)
    (j : ℕ) (hjpos : 0 < j) (hj : j + 1 < r)
    (hcarrier : first.block 0 = C)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ C)
    (leftOutside : Disjoint C (first.block (j : ZMod r)))
    (rightOutside : Disjoint C (first.block ((j + 1 : ℕ) : ZMod r)))
    (leftPartner : first.block (j : ZMod r) ⊆ B)
    (rightPartner : first.block ((j + 1 : ℕ) : ZMod r) ⊆ B)
    (hinvariant : PartnerAssemblyInvariant C B s) :
    ∃ word : List Letter,
      (run F s word).origin = s.origin ∧
      (run F s word).chain = s.chain ∧
      PartnerAssemblyInvariant C B (run F s word) := by
  let target := packedLegalNamed first hrn (-(j : ZMod n))
  obtain ⟨h0, h1, qC, hC, hq0, hq1⟩ :=
    packed_outside_ports_with_carrier first hrn j hjpos hj
  have hr : 2 ≤ r := by omega
  have hn : 2 ≤ n := by omega
  exact realize_one_partner_assembly_stage F C B
    (first.block (j : ZMod r))
    (first.block ((j + 1 : ℕ) : ZMod r))
    s first target hn hr source
    (packedLegalNamed_same_order first ordered hrn (-(j : ZMod n)))
    h0 h1 registered selected inside leftOutside rightOutside
    leftPartner rightPartner qC (by simpa [hcarrier] using hC)
    hq0 hq1 hinvariant

end RegisteredAbsorptionChains
