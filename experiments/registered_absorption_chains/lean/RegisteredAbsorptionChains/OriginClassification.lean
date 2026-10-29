import RegisteredAbsorptionChains.FiberParamInverse
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- Three distinct source fibers rule out a reversal of the consecutive
source atoms at adjacent target ports. The third atom is the obstruction
that disappears when `n = 2`. -/
theorem SourceOrderLift.no_reverse_registration
    (lift : SourceOrderLift n) (hn : 3 ≤ n)
    (h0 : lift.position (0 : ZMod n) = 1)
    (h1 : lift.position (1 : ZMod n) = 0)
    (h2 : lift.position (2 : ZMod n) ≠ 0)
    (h2' : lift.position (2 : ZMod n) ≠ 1) : False := by
  obtain ⟨k, hlt, _, hbetween⟩ :=
    lift.adjacent_port_fibers 1 0 h1 h0
  have hval0 : (0 : ZMod n).val = 0 := by simp
  have hval1 : (1 : ZMod n).val = 1 := by
    simpa only [Nat.cast_one] using
      (ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega))
  have hval2 : (2 : ZMod n).val = 2 :=
    ZMod.val_natCast_of_lt (n := n) (a := 2) (by omega)
  rw [hval0, hval1] at hlt
  have hk : 0 < k := by
    by_contra h
    have hkn : k ≤ 0 := by omega
    have hprod : k * (n : ℤ) ≤ 0 :=
      mul_nonpos_of_nonpos_of_nonneg hkn (by omega)
    omega
  have hupper : (2 : ℤ) ≤ (0 : ℤ) + k * n := by
    nlinarith
  have hmid := hbetween 2 (by rw [hval1]; omega) (by rw [hval0]; exact hupper)
  have hposition : lift.position (2 : ZMod n) =
      lift.position (1 : ZMod n) ∨
      lift.position (2 : ZMod n) = lift.position (1 : ZMod n) + 1 := by
    rcases hmid with h | h
    · left
      have hcast := congrArg (fun z : ℤ => (z : ZMod n)) h
      simpa [SourceOrderLift.position, hval1, hval2] using hcast
    · right
      have hcast := congrArg (fun z : ℤ => (z : ZMod n)) h
      simpa [SourceOrderLift.position, hval1, hval2] using hcast
  rcases hposition with h | h
  · exact h2 (h.trans h1)
  · exact h2' (by rw [h, h1]; ring)

/-- At a real registration collision the two source parents have the
standard ordered port assignment, provided a third source atom exists. -/
theorem sourceOrdered_registration_parents
    (s : Execution n (ZMod n)) (u v : Finset (ZMod n))
    (hn : 3 ≤ n) (ordered : SourceOrdered s.placed)
    (h0 : s.placed 0 = some u) (h1 : s.placed 1 = some v)
    (hunion : u ∪ v = selectedPair n) :
    u = {0} ∧ v = {1} := by
  obtain ⟨lift, hplaced⟩ := ordered
  have huf : sourceFiber lift.position 0 = u ∧ u.Nonempty :=
    (placementOfMap_some_iff lift.position 0 u).mp (hplaced ▸ h0)
  have hvf : sourceFiber lift.position 1 = v ∧ v.Nonempty :=
    (placementOfMap_some_iff lift.position 1 v).mp (hplaced ▸ h1)
  obtain ⟨a, ha⟩ := huf.2
  obtain ⟨b, hb⟩ := hvf.2
  have ha0 : lift.position a = 0 := by
    exact (mem_sourceFiber lift.position a 0).mp (huf.1 ▸ ha)
  have hb1 : lift.position b = 1 := by
    exact (mem_sourceFiber lift.position b 1).mp (hvf.1 ▸ hb)
  have h01 : (0 : ZMod n) ≠ 1 := by
    intro h
    have hval1 : (1 : ZMod n).val = 1 := by
      simpa only [Nat.cast_one] using
        (ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega))
    have hv := congrArg ZMod.val h
    rw [ZMod.val_zero, hval1] at hv
    omega
  have hab : a ≠ b := by
    intro heq
    rw [heq] at ha0
    exact h01 (ha0.symm.trans hb1)
  have haF : a = 0 ∨ a = 1 := by
    have hmem : a ∈ selectedPair n := hunion ▸ Finset.mem_union_left v ha
    simpa [selectedPair] using hmem
  have hbF : b = 0 ∨ b = 1 := by
    have hmem : b ∈ selectedPair n := hunion ▸ Finset.mem_union_right u hb
    simpa [selectedPair] using hmem
  have h20 : (2 : ZMod n) ≠ 0 := by
    intro h
    have hval2 : (2 : ZMod n).val = 2 :=
      ZMod.val_natCast_of_lt (n := n) (a := 2) (by omega)
    have hv := congrArg ZMod.val h
    rw [hval2, ZMod.val_zero] at hv
    omega
  have h21 : (2 : ZMod n) ≠ 1 := by
    intro h
    have hval1 : (1 : ZMod n).val = 1 := by
      simpa only [Nat.cast_one] using
        (ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega))
    have hval2 : (2 : ZMod n).val = 2 :=
      ZMod.val_natCast_of_lt (n := n) (a := 2) (by omega)
    have hv := congrArg ZMod.val h
    rw [hval2, hval1] at hv
    omega
  have h2F : (2 : ZMod n) ∉ selectedPair n := by
    simp [selectedPair, h20, h21]
  have h2p0 : lift.position (2 : ZMod n) ≠ 0 := by
    intro h
    have hmem : (2 : ZMod n) ∈ u := by
      rw [← huf.1]
      exact (mem_sourceFiber lift.position 2 0).mpr h
    exact h2F (hunion ▸ Finset.mem_union_left v hmem)
  have h2p1 : lift.position (2 : ZMod n) ≠ 1 := by
    intro h
    have hmem : (2 : ZMod n) ∈ v := by
      rw [← hvf.1]
      exact (mem_sourceFiber lift.position 2 1).mpr h
    exact h2F (hunion ▸ Finset.mem_union_right u hmem)
  have hae : a = 0 := by
    rcases haF with h | h
    · exact h
    · have hbe : b = 0 := by
        rcases hbF with h' | h'
        · exact h'
        · exact False.elim (hab (h.trans h'.symm))
      have hr0 : lift.position (0 : ZMod n) = 1 := hbe ▸ hb1
      have hr1 : lift.position (1 : ZMod n) = 0 := h ▸ ha0
      exact False.elim (lift.no_reverse_registration hn hr0 hr1 h2p0 h2p1)
  have hbe : b = 1 := by
    rcases hbF with h | h
    · exact False.elim (hab (hae.trans h.symm))
    · exact h
  have h0u : (0 : ZMod n) ∈ u := hae ▸ ha
  have h1v : (1 : ZMod n) ∈ v := hbe ▸ hb
  have h1notu : (1 : ZMod n) ∉ u := by
    intro h
    have hp0 : lift.position (1 : ZMod n) = 0 :=
      (mem_sourceFiber lift.position 1 0).mp (huf.1 ▸ h)
    have hp1 : lift.position (1 : ZMod n) = 1 := hbe ▸ hb1
    exact h01 (hp0.symm.trans hp1)
  have h0notv : (0 : ZMod n) ∉ v := by
    intro h
    have hp1 : lift.position (0 : ZMod n) = 1 :=
      (mem_sourceFiber lift.position 0 1).mp (hvf.1 ▸ h)
    have hp0 : lift.position (0 : ZMod n) = 0 := hae ▸ ha0
    exact h01 (hp0.symm.trans hp1)
  constructor
  · ext x
    constructor
    · intro hx
      have hxf : x = 0 ∨ x = 1 := by
        have hmem : x ∈ selectedPair n :=
          hunion ▸ Finset.mem_union_left v hx
        simpa [selectedPair] using hmem
      rcases hxf with rfl | rfl
      · simp
      · exact False.elim (h1notu hx)
    · intro hx
      have hx0 : x = 0 := by simpa using hx
      simpa [hx0] using h0u
  · ext x
    constructor
    · intro hx
      have hxf : x = 0 ∨ x = 1 := by
        have hmem : x ∈ selectedPair n :=
          hunion ▸ Finset.mem_union_right u hx
        simpa [selectedPair] using hmem
      rcases hxf with rfl | rfl
      · exact False.elim (h0notv hx)
      · simp
    · intro hx
      have hx1 : x = 1 := by simpa using hx
      simpa [hx1] using h1v

theorem step_origin_standard_or_none
    (s : Execution n (ZMod n)) (a : Letter) (hn : 3 ≤ n)
    (ordered : SourceOrdered s.placed)
    (h : s.origin = none ∨
      s.origin = (registrationExecution n).origin) :
    (step (selectedPair n) s a).origin = none ∨
      (step (selectedPair n) s a).origin =
        (registrationExecution n).origin := by
  rcases h with hnone | hstandard
  · cases a with
    | p => exact Or.inl (by simpa [step] using hnone)
    | d =>
        cases h0 : s.placed 0 with
        | none => exact Or.inl (by simp [step, stepDefect, h0, hnone])
        | some u =>
          cases h1 : s.placed 1 with
          | none => exact Or.inl (by simp [step, stepDefect, h0, h1, hnone])
          | some v =>
            by_cases hjoin : u ∪ v = selectedPair n
            · obtain ⟨hu, hv⟩ :=
                sourceOrdered_registration_parents s u v hn ordered h0 h1 hjoin
              right
              simp [step, stepDefect, h0, h1, hnone,
                hu, hv, registration_origin (show 2 ≤ n by omega),
                selectedPair]
            · left
              simp [step, stepDefect, h0, h1, hnone, hjoin]
  · cases a with
    | p => exact Or.inr (by simpa [step] using hstandard)
    | d =>
        right
        cases h0 : s.placed 0 with
        | none => simpa [step, stepDefect, h0] using hstandard
        | some u =>
          cases h1 : s.placed 1 with
          | none => simpa [step, stepDefect, h0, h1] using hstandard
          | some v =>
            have hsome : s.origin.isNone = false := by
              rw [hstandard, registration_origin (show 2 ≤ n by omega)]
              rfl
            simpa [step, stepDefect, h0, h1, hsome] using hstandard

theorem run_origin_standard_or_none
    (s : Execution n (ZMod n)) (word : List Letter) (hn : 3 ≤ n)
    (ordered : SourceOrdered s.placed)
    (h : s.origin = none ∨
      s.origin = (registrationExecution n).origin) :
    (run (selectedPair n) s word).origin = none ∨
      (run (selectedPair n) s word).origin =
        (registrationExecution n).origin := by
  induction word generalizing s with
  | nil => simpa [run] using h
  | cons a rest ih =>
      change (run (selectedPair n) (step (selectedPair n) s a) rest).origin =
          none ∨
        (run (selectedPair n) (step (selectedPair n) s a) rest).origin =
          (registrationExecution n).origin
      exact ih (step (selectedPair n) s a)
        (step_ordered (selectedPair n) s a (by omega) ordered)
        (step_origin_standard_or_none s a hn ordered h)

/-- For `n >= 3`, every actual registered history has the same ordered
origin as the literal first-defect registration. This does not hold at `n=2`. -/
theorem actual_registered_origin_unique
    (word : List Letter) (hn : 3 ≤ n)
    (hregistered :
      (run (selectedPair n) (singletonExecution n) word).origin.isSome = true) :
    (run (selectedPair n) (singletonExecution n) word).origin =
      (registrationExecution n).origin := by
  have h := run_origin_standard_or_none (singletonExecution n) word hn
    singletonExecution_ordered (Or.inl rfl)
  rcases h with hnone | heq
  · rw [hnone] at hregistered
    cases hregistered
  · exact heq

end RegisteredAbsorptionChains
