import RSR2.RetentionSufficiency
import RSR2.TransferMass

/-!
# Minimum transferred atom mass for an endpoint partition

The endpoint partition determines a finite optimization problem over lower
atom sets. The maximum retained mass is defined by a bounded downward search
over `0, ..., n`; the empty retained set makes the admissible family nonempty.
This module optimizes transferred atom mass, not elevator-letter count or raw
word length.
-/

namespace RSR2.Parametric

/-- Number of source atoms in a predicate-defined subset of `Fin n`. -/
noncomputable def retainedAtomMass (n : Nat) (U : Fin n → Prop) : Nat := by
  classical
  exact (List.finRange n).countP (fun a => decide (U a))

theorem retainedAtomMass_le (n : Nat) (U : Fin n → Prop) :
    retainedAtomMass n U ≤ n := by
  classical
  unfold retainedAtomMass
  calc
    (List.finRange n).countP (fun a => decide (U a)) ≤
        (List.finRange n).length := List.countP_le_length
    _ = n := List.length_finRange

private theorem emptyRetention_admissible (n : Nat) (hn : 0 < n)
    (π : RSR2.UnorderedPartition n) :
    UnorderedRetentionAdmissible n hn π (fun _ => False) := by
  constructor
  · intro a b _
    simp
  · intro a ha
    exact False.elim ha

/-- Search downward through the finite mass range. At each successor, return
that mass if an admissible lower set realizes it; otherwise continue below. -/
private noncomputable def maxAdmissibleRetentionMassAux (n : Nat) (hn : 0 < n)
    (π : RSR2.UnorderedPartition n) : Nat → Nat
  | 0 => 0
  | k + 1 => by
      classical
      exact if ∃ U, UnorderedRetentionAdmissible n hn π U ∧
          retainedAtomMass n U = k + 1 then
        k + 1
      else maxAdmissibleRetentionMassAux n hn π k

private theorem maxAdmissibleRetentionMassAux_spec (n : Nat) (hn : 0 < n)
    (π : RSR2.UnorderedPartition n) :
    ∀ k,
      (∀ U, UnorderedRetentionAdmissible n hn π U → retainedAtomMass n U ≤ k) →
      (∃ U, UnorderedRetentionAdmissible n hn π U ∧
        retainedAtomMass n U = maxAdmissibleRetentionMassAux n hn π k) ∧
      ∀ U, UnorderedRetentionAdmissible n hn π U →
        retainedAtomMass n U ≤ maxAdmissibleRetentionMassAux n hn π k := by
  intro k
  induction k with
  | zero =>
      intro hbound
      have hempty := emptyRetention_admissible n hn π
      have hmass : retainedAtomMass n (fun _ => False) = 0 := by
        simp [retainedAtomMass]
      constructor
      · exact ⟨fun _ => False, hempty, hmass⟩
      · intro U hU
        have := hbound U hU
        omega
  | succ k ih =>
      intro hbound
      classical
      by_cases hex : ∃ U, UnorderedRetentionAdmissible n hn π U ∧
          retainedAtomMass n U = k + 1
      · constructor
        · simp [maxAdmissibleRetentionMassAux, hex]
        · intro U hU
          have hmax := hbound U hU
          simp [maxAdmissibleRetentionMassAux, hex]
          exact hmax
      · have hbound' : ∀ U, UnorderedRetentionAdmissible n hn π U →
            retainedAtomMass n U ≤ k := by
          intro U hU
          have hb := hbound U hU
          by_cases hk : retainedAtomMass n U ≤ k
          · exact hk
          · have heq : retainedAtomMass n U = k + 1 := by omega
            exact False.elim (hex ⟨U, hU, heq⟩)
        obtain ⟨⟨U, hU, hmass⟩, hmax⟩ := ih hbound'
        have haux : maxAdmissibleRetentionMassAux n hn π (k + 1) =
            maxAdmissibleRetentionMassAux n hn π k := by
          simp [maxAdmissibleRetentionMassAux, hex]
        constructor
        · simpa [maxAdmissibleRetentionMassAux, hex] using
            (show ∃ U, UnorderedRetentionAdmissible n hn π U ∧
              retainedAtomMass n U = maxAdmissibleRetentionMassAux n hn π k
              from ⟨U, hU, hmass⟩)
        · intro V hV
          have hv := hmax V hV
          rw [haux]
          exact hv

/-- Maximum number of atoms that can remain below while realizing `π`.
The search is over the bounded mass values; no ordered block presentation is
part of this definition. -/
noncomputable def maxAdmissibleRetentionMass (n : Nat) (hn : 1 < n)
    (π : RSR2.UnorderedPartition n) : Nat :=
  maxAdmissibleRetentionMassAux n (by omega) π n

theorem maxAdmissibleRetentionMass_spec (n : Nat) (hn : 1 < n)
    (π : RSR2.UnorderedPartition n) :
    (∃ U, UnorderedRetentionAdmissible n (by omega) π U ∧
      retainedAtomMass n U = maxAdmissibleRetentionMass n hn π) ∧
    ∀ U, UnorderedRetentionAdmissible n (by omega) π U →
      retainedAtomMass n U ≤ maxAdmissibleRetentionMass n hn π := by
  have hbound : ∀ U, UnorderedRetentionAdmissible n (by omega) π U →
      retainedAtomMass n U ≤ n := fun U _ => retainedAtomMass_le n U
  exact maxAdmissibleRetentionMassAux_spec n (by omega) π n hbound

/-- Exact minimum transferred mass prescribed by the endpoint partition. -/
noncomputable def minimumTransferMass (n : Nat) (hn : 1 < n)
    (π : RSR2.UnorderedPartition n) : Nat :=
  n - maxAdmissibleRetentionMass n hn π

theorem retainedAtomMass_lowerAtoms (n : Nat) (P : Placement n) :
    retainedAtomMass n (lowerAtoms P) = lowerAtomMass P := by
  classical
  unfold retainedAtomMass lowerAtomMass
  apply List.countP_congr
  intro a _
  cases h : (P a).1 <;> simp [lowerAtoms, h]

/-- Every successful singleton-seed realization of `π` transfers at least
`n - maxAdmissibleRetentionMass` atoms, even when elevators move whole
prefused packets. -/
theorem singleton_run_transferMass_lower_bound (n : Nat) (hn : 1 < n)
    (π : RSR2.UnorderedPartition n) (word : List Letter) (P : Placement n)
    (mass : Nat)
    (hrun : runWithTransferMass n hn (seed n) word = some (P, mass))
    (hpartition : ∀ a b, samePacket P a b ↔ π.r a b) :
    minimumTransferMass n hn π ≤ mass := by
  have hplain : run n hn (seed n) word = some P := by
    have hproj := runWithTransferMass_project n hn (seed n) word
    rw [hrun] at hproj
    exact hproj.symm
  have halloc : EndpointLayerAllocation P π (lowerAtoms P) :=
    ⟨hpartition, fun _ => Iff.rfl⟩
  have hadm := singleton_run_unorderedRetentionAdmissible n hn word P
    hplain π (lowerAtoms P) halloc
  have hmax := (maxAdmissibleRetentionMass_spec n hn π).2
    (lowerAtoms P) hadm
  have hmass := (singleton_run_transferMass n hn P word mass hrun).2
  rw [retainedAtomMass_lowerAtoms] at hmax
  change n - maxAdmissibleRetentionMass n hn π ≤ mass
  rw [hmass]
  exact Nat.sub_le_sub_left hmax n

/-- The lower bound applies to every successful raw execution word; its mass
observer is obtained by replaying the same guarded `run`. -/
theorem singleton_run_transferMass_lower_bound_of_run (n : Nat) (hn : 1 < n)
    (π : RSR2.UnorderedPartition n) (word : List Letter) (P : Placement n)
    (hrun : run n hn (seed n) word = some P)
    (hpartition : ∀ a b, samePacket P a b ↔ π.r a b) :
    ∃ mass, runWithTransferMass n hn (seed n) word = some (P, mass) ∧
      minimumTransferMass n hn π ≤ mass := by
  obtain ⟨mass, hmass, _⟩ := run_exists_transferMass n hn (seed n) P word hrun
  exact ⟨mass, hmass, singleton_run_transferMass_lower_bound n hn π word P
    mass hmass hpartition⟩

/-- The lower bound is attained by realizing a maximum-mass admissible
retention set. This is the exact minimum-transfer-mass statement without
quantifying over a separate finite type of execution words. -/
theorem singleton_run_transferMass_attained (n : Nat) (hn : 1 < n)
    (π : RSR2.UnorderedPartition n) :
    ∃ word P mass,
      run n hn (seed n) word = some P ∧
      runWithTransferMass n hn (seed n) word = some (P, mass) ∧
      (∀ a b, samePacket P a b ↔ π.r a b) ∧
      mass = minimumTransferMass n hn π := by
  obtain ⟨U, hadm, hUmax⟩ := maxAdmissibleRetentionMass_spec n hn π |>.1
  obtain ⟨word, P, hrun, halloc⟩ := unorderedRetentionAdmissible_realization
    n hn π U hadm
  obtain ⟨mass, hmassRun, _⟩ := singleton_run_exists_transferMass
    n hn P word hrun
  have hcard : lowerAtomMass P = retainedAtomMass n U := by
    classical
    unfold lowerAtomMass retainedAtomMass
    apply List.countP_congr
    intro a _
    have hU := halloc.2 a
    change (P a).1 = false ↔ U a at hU
    simp [hU]
  have hmass : mass = n - maxAdmissibleRetentionMass n hn π := by
    have hmass' := (singleton_run_transferMass n hn P word mass hmassRun).2
    rw [hcard, hUmax] at hmass'
    exact hmass'
  exact ⟨word, P, mass, hrun, hmassRun, halloc.1, hmass⟩

end RSR2.Parametric
