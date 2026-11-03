import FutureEvent.PositiveFiberInverse

namespace FutureEvent

open RegisteredAbsorptionChains

abbrev InitialCutSelect (N t : ℕ) :=
  {S : Select N t // ∃ i ∈ S.val, i.val = 0}

abbrev RegisterableNativeParam (n t : ℕ) :=
  Fin n × InitialCutSelect ((n - 1) - 1) t × Select (n - 1) (t + 1)

abbrev RegisterableNativeParams (n : ℕ) :=
  (i : Fin (n - 2)) × RegisterableNativeParam n (i.val + 1)

theorem initialCut_first_value {N t : ℕ} (S : InitialCutSelect N t) (ht : 0 < t) :
    selectedValue S.val ⟨0, ht⟩ = 0 := by
  obtain ⟨z, hz, hz0⟩ := S.property
  obtain ⟨j, hj⟩ := (S.val.val.orderIsoOfFin S.val.property).surjective ⟨z, hz⟩
  have hjv : selectedValue S.val j = 0 := by
    have hv := congrArg (fun x : S.val.val => x.val.val) hj
    exact hv.trans hz0
  have hle := (selectedValue_strict S.val).monotone
    (show (⟨0, ht⟩ : Fin t) ≤ j from Fin.mk_le_mk.mpr (Nat.zero_le _))
  omega

variable {n t : ℕ} [NeZero n]

noncomputable def registerableNativeData (hn : 3 ≤ n) (_ht : 0 < t)
    (p : RegisterableNativeParam n t) : ValidFiberPlacement n (t + 1) :=
  ValidFiberPlacement.ofRankParams 1 (by omega) (by omega : 1 + (n - 1) ≤ n)
    (by omega : 0 < n - 1) (Nat.succ_pos _) (p.1, p.2.1.val, p.2.2)

theorem registerableNativeData_bounds (hn : 3 ≤ n) (ht : 0 < t)
    (p : RegisterableNativeParam n t) :
    (registerableNativeData hn ht p).u = 1 ∧ (registerableNativeData hn ht p).v = n := by
  constructor
  · rfl
  · change 1 + (n - 1) = n
    omega

theorem registerableNativeData_cut_one (hn : 3 ≤ n) (ht : 0 < t)
    (p : RegisterableNativeParam n t) :
    (registerableNativeData hn ht p).cut ⟨1, by omega⟩ = 2 := by
  have hfirst := initialCut_first_value p.2.1 ht
  change rankCuts (k := n - 1) (t := t + 1) 1 p.2.1.val ⟨1, by omega⟩ = 2
  simp only [rankCuts, dif_neg (by omega : ¬ 1 = 0),
    dif_neg (by omega : ¬ 1 = t + 1)]
  simpa using congrArg (fun a : ℕ => 1 + a + 1) hfirst

theorem singleton_zero_carrier {r : ℕ} (data : ValidFiberPlacement n r)
    (hu : data.u = 1) (hv : data.v = n) : data.carrier = {0} := by
  ext a
  simp only [ValidFiberPlacement.carrier, Finset.mem_filter, Finset.mem_univ, true_and,
    Finset.mem_singleton, hu, hv]
  have ha := a.val_lt
  constructor
  · intro h
    have hz : a.val = 0 := by omega
    rw [← ZMod.natCast_zmod_val a, hz]
    simp
  · rintro rfl
    simp

theorem singleton_one_outside (data : ValidFiberPlacement n (t + 1))
    (hn : 3 ≤ n) (hu : data.u = 1)
    (hcut : data.cut ⟨1, by omega⟩ = 2) :
    data.blockFin ⟨1, by omega⟩ = {1} := by
  change data.outside ⟨0, Nat.succ_pos t⟩ = {1}
  rw [data.outside_eq_sourceInterval, data.cut_zero, hu, hcut]
  ext a
  rw [mem_sourceInterval_iff 1 2 (by omega)]
  simp only [Finset.mem_singleton]
  constructor
  · intro h
    have hv : a.val = 1 := by omega
    rw [← ZMod.natCast_zmod_val a, hv]
    simp
  · rintro rfl
    have hv : (1 : ZMod n).val = 1 := by
      simpa only [Nat.cast_one] using ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega)
    rw [hv]
    omega

end FutureEvent
