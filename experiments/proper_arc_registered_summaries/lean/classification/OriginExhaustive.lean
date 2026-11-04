import classification.SourceCut
import classification.OriginTrace
import RegisteredAbsorptionChains.FiberReachability

namespace ProperArc

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

theorem sourceOrdered_ports_disjoint (P : Placement n (Finset (ZMod n)))
    (U V : Finset (ZMod n)) (hn : 2 ≤ n) (ordered : SourceOrdered P)
    (h0 : P 0 = some U) (h1 : P 1 = some V) : Disjoint U V := by
  obtain ⟨lift, hP⟩ := ordered
  have hu := (placementOfMap_some_iff lift.position 0 U).mp (hP ▸ h0)
  have hv := (placementOfMap_some_iff lift.position 1 V).mp (hP ▸ h1)
  apply Finset.disjoint_left.mpr
  intro a ha hb
  have ha0 := (mem_sourceFiber lift.position a 0).mp (hu.1.symm ▸ ha)
  have ha1 := (mem_sourceFiber lift.position a 1).mp (hv.1.symm ▸ hb)
  have h10 : (1 : ZMod n) = 0 := ha1.symm.trans ha0
  have := ZMod.one_eq_zero_iff.mp h10
  omega

theorem actual_first_registration (F : Finset (ZMod n)) (word : List Letter)
    (record : FusionRecord (ZMod n)) (hn : 2 ≤ n)
    (hfinal : (run F (singletonExecution n) word).origin = some record) :
    ∃ pre post U V,
      word = pre ++ .d :: post ∧
      (run F (singletonExecution n) pre).origin = none ∧
      (run F (singletonExecution n) pre).placed 0 = some U ∧
      (run F (singletonExecution n) pre).placed 1 = some V ∧
      SourceOrdered (run F (singletonExecution n) pre).placed ∧
      Disjoint U V ∧ U ∪ V = F ∧ record = ⟨U, V, F⟩ := by
  obtain ⟨pre, post, U, V, hword, hnone, h0, h1, hjoin, hrecord⟩ :=
    extract_first_registration F (singletonExecution n) word record rfl hfinal
  have hordered := run_ordered F (singletonExecution n) pre hn singletonExecution_ordered
  exact ⟨pre, post, U, V, hword, hnone, h0, h1, hordered,
    sourceOrdered_ports_disjoint _ U V hn hordered h0 h1, hjoin, hrecord⟩

/-- A literal origin of an actual seed history lies in the internal-cut
family. No clean-outside or standard-origin premise is imposed. -/
theorem actual_origin_in_cut_range (c : ZMod n) (r : ℕ) (word : List Letter)
    (record : FusionRecord (ZMod n)) (hr : 2 ≤ r ∧ r < n)
    (hfinal : (run (arc c r) (singletonExecution n) word).origin = some record) :
    ∃ i : Fin (r - 1), record = originRecord c r (i.val + 1) := by
  obtain ⟨pre, post, U, V, _, _, h0, h1, hordered, _, hjoin, hrecord⟩ :=
    actual_first_registration (arc c r) word record (by omega) hfinal
  obtain ⟨t, ht, htr, hU, hV⟩ := sourceOrdered_registration_cut _ c r U V hr.2 hordered h0 h1 hjoin
  refine ⟨⟨t - 1, by omega⟩, ?_⟩
  rw [show (t - 1) + 1 = t by omega, hrecord, hU, hV]
  rfl

theorem actual_origin_cut_unique (c : ZMod n) (r : ℕ) (word : List Letter)
    (hr : 2 ≤ r ∧ r < n)
    (hregistered : (run (arc c r) (singletonExecution n) word).origin ≠ none) :
    ∃! i : Fin (r - 1),
      (run (arc c r) (singletonExecution n) word).origin = some (originRecord c r (i.val + 1)) := by
  cases hrecord : (run (arc c r) (singletonExecution n) word).origin with
  | none => exact False.elim (hregistered hrecord)
  | some record =>
    obtain ⟨i, hi⟩ := actual_origin_in_cut_range c r word record hr hrecord
    refine ⟨i, ?_, ?_⟩
    · exact congrArg some hi
    · intro j hj
      apply originRecord_injective c r (by omega)
      exact (Option.some.inj hj).symm.trans hi

theorem actual_registered_origin_unique (c : ZMod n) (r : ℕ)
    (s : Execution n (ZMod n)) (hr : 2 ≤ r ∧ r < n)
    (reachable : ReachableExecution (arc c r) s) (registered : s.origin ≠ none) :
    ∃! i : Fin (r - 1), s.origin = some (originRecord c r (i.val + 1)) := by
  obtain ⟨word, hword⟩ := reachable
  rw [← hword] at registered ⊢
  exact actual_origin_cut_unique c r word hr registered

theorem actual_registered_origin_unique_nat (c : ZMod n) (r : ℕ)
    (s : Execution n (ZMod n)) (hr : 2 ≤ r ∧ r < n)
    (reachable : ReachableExecution (arc c r) s) (registered : s.origin ≠ none) :
    ∃! t : ℕ, 1 ≤ t ∧ t < r ∧ s.origin = some (originRecord c r t) := by
  obtain ⟨i, hi, huniq⟩ := actual_registered_origin_unique c r s hr reachable registered
  refine ⟨i.val + 1, ⟨by omega, by have := i.isLt; omega, hi⟩, ?_⟩
  intro t ht
  let j : Fin (r - 1) := ⟨t - 1, by omega⟩
  have hj : s.origin = some (originRecord c r (j.val + 1)) := by
    simpa only [j, show t - 1 + 1 = t by omega] using ht.2.2
  have heq := congrArg Fin.val (huniq j hj)
  change t - 1 = i.val at heq
  omega

def ActualRegistrationOrigins (c : ZMod n) (r : ℕ) :=
  { record : FusionRecord (ZMod n) //
    ∃ word : List Letter, (run (arc c r) (singletonExecution n) word).origin = some record }

def originCutActual (c : ZMod n) (r : ℕ) (hr : 2 ≤ r ∧ r < n)
    (i : Fin (r - 1)) : ActualRegistrationOrigins c r :=
  ⟨originRecord c r (i.val + 1), originWord c r (i.val + 1), by
    rw [run_originWord c r _ hr.2 (by omega) (by omega)]⟩

theorem originCutActual_injective (c : ZMod n) (r : ℕ) (hr : 2 ≤ r ∧ r < n) :
    Function.Injective (originCutActual c r hr) := by
  intro i j h
  apply originRecord_injective c r (by omega)
  exact congrArg Subtype.val h

theorem originCutActual_surjective (c : ZMod n) (r : ℕ) (hr : 2 ≤ r ∧ r < n) :
    Function.Surjective (originCutActual c r hr) := by
  intro record
  obtain ⟨word, hword⟩ := record.property
  obtain ⟨i, hi⟩ := actual_origin_in_cut_range c r word record.val hr hword
  exact ⟨i, Subtype.ext hi.symm⟩

noncomputable def actualRegistrationOriginsEquivCuts (c : ZMod n) (r : ℕ)
    (hr : 2 ≤ r ∧ r < n) : ActualRegistrationOrigins c r ≃ Fin (r - 1) :=
  (Equiv.ofBijective (originCutActual c r hr)
    ⟨originCutActual_injective c r hr, originCutActual_surjective c r hr⟩).symm

theorem actualRegistrationOriginsEquivCuts_symm_val (c : ZMod n) (r : ℕ)
    (hr : 2 ≤ r ∧ r < n) (i : Fin (r - 1)) :
    ((actualRegistrationOriginsEquivCuts c r hr).symm i).val = originRecord c r (i.val + 1) := rfl

theorem actualRegistrationOriginsEquivCuts_left_card (c : ZMod n) (r : ℕ)
    (hr : 2 ≤ r ∧ r < n) (record : ActualRegistrationOrigins c r) :
    (actualRegistrationOriginsEquivCuts c r hr record).val + 1 = record.val.left.card := by
  obtain ⟨i, rfl⟩ := originCutActual_surjective c r hr record
  change (actualRegistrationOriginsEquivCuts c r hr
      ((actualRegistrationOriginsEquivCuts c r hr).symm i)).val + 1 =
    (interval c 0 (i.val + 1)).card
  rw [Equiv.apply_symm_apply, card_interval c 0 _ (by have := i.isLt; omega)]
  omega

theorem finite_actualRegistrationOrigins (c : ZMod n) (r : ℕ) (hr : 2 ≤ r ∧ r < n) :
    Finite (ActualRegistrationOrigins c r) :=
  Finite.of_injective (actualRegistrationOriginsEquivCuts c r hr)
    (actualRegistrationOriginsEquivCuts c r hr).injective

theorem card_actualRegistrationOrigins (c : ZMod n) (r : ℕ) (hr : 2 ≤ r ∧ r < n) :
    Nat.card (ActualRegistrationOrigins c r) = r - 1 := by
  rw [Nat.card_congr (actualRegistrationOriginsEquivCuts c r hr), Nat.card_fin]

end ProperArc
