import ProperArc
import RegisteredAbsorptionChains.SourceOrderAdmission

namespace ProperArc

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

theorem lift_position_int (lift : SourceOrderLift n) (x : ℤ) :
    lift.position (x : ZMod n) = (lift.map x : ZMod n) := by
  have hrep : x = ((x : ZMod n).val : ℤ) + (x / (n : ℤ)) * n := by
    rw [ZMod.val_intCast]
    have h := Int.emod_add_mul_ediv x (n : ℤ)
    nlinarith
  have hmap : lift.map x = lift.map ((x : ZMod n).val : ℤ) + (x / (n : ℤ)) * n := by
    conv_lhs => rw [hrep]
    rw [lift.periodic]
  rw [hmap]
  simp [SourceOrderLift.position]

def shiftSourceLift (lift : SourceOrderLift n) (c : ZMod n) : SourceOrderLift n where
  map := fun x => lift.map (x + c.val)
  monotone := by intro x y h; exact lift.monotone (by omega)
  periodic := by
    intro x k
    rw [show x + k * n + c.val = (x + c.val) + k * n by ring, lift.periodic]

theorem shiftSourceLift_position (lift : SourceOrderLift n) (c a : ZMod n) :
    (shiftSourceLift lift c).position a = lift.position (c + a) := by
  change (lift.map ((a.val : ℤ) + c.val) : ZMod n) = _
  rw [← lift_position_int]
  congr 1
  simp [add_comm]

/-- An outside source atom rules out a cyclic wrap between ordered occupied
ports. This is the third-packet obstruction in the proper-arc setting. -/
theorem ordered_port_addresses (lift : SourceOrderLift n) (r : ℕ)
    (hr : r < n) (a b : ZMod n) (ha : a.val < r) (_hb : b.val < r)
    (hp0 : lift.position a = 0) (hp1 : lift.position b = 1)
    (hout0 : lift.position (r : ZMod n) ≠ 0)
    (hout1 : lift.position (r : ZMod n) ≠ 1) : a.val < b.val := by
  obtain ⟨k, hlt, _, hbetween⟩ := lift.adjacent_port_fibers a b hp0 hp1
  have hn : (0 : ℤ) < n := by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne n)
  have hk : k ≤ 0 := by
    by_contra hk
    have hkn : (n : ℤ) ≤ k * n := by nlinarith
    have hm := hbetween (r : ℤ) (by omega) (by omega)
    have hrval : (r : ZMod n).val = r := ZMod.val_natCast_of_lt hr
    have hzero : (lift.map a.val : ZMod n) = 0 := hp0
    have hcast : lift.position (r : ZMod n) = 0 ∨ lift.position (r : ZMod n) = 1 := by
      rcases hm with h | h
      · left
        have he := congrArg (fun x : ℤ => (x : ZMod n)) h
        simpa only [SourceOrderLift.position, hrval, hzero] using he
      · right
        have he := congrArg (fun x : ℤ => (x : ZMod n)) h
        simpa only [SourceOrderLift.position, hrval, Int.cast_add, Int.cast_one,
          hzero, zero_add] using he
    exact hcast.elim hout0 hout1
  have hkn : k * (n : ℤ) ≤ 0 := mul_nonpos_of_nonpos_of_nonneg hk (by omega)
  omega

theorem sourceOrdered_parent_addresses (P : Placement n (Finset (ZMod n)))
    (c : ZMod n) (r : ℕ) (U V : Finset (ZMod n)) (hr : r < n)
    (ordered : SourceOrdered P) (h0 : P 0 = some U) (h1 : P 1 = some V)
    (hunion : U ∪ V = arc c r) :
    U.Nonempty ∧ V.Nonempty ∧
      (∀ a ∈ U, (a - c).val < r) ∧ (∀ b ∈ V, (b - c).val < r) ∧
      (∀ a ∈ U, ∀ b ∈ V, (a - c).val < (b - c).val) := by
  obtain ⟨lift, hP⟩ := ordered
  have hu := (placementOfMap_some_iff lift.position 0 U).mp (hP ▸ h0)
  have hv := (placementOfMap_some_iff lift.position 1 V).mp (hP ▸ h1)
  have hU (a : ZMod n) (ha : a ∈ U) : (a - c).val < r := by
    have hf : a ∈ arc c r := hunion ▸ Finset.mem_union_left V ha
    exact ((mem_interval_iff c a 0 r (by omega)).mp hf).2
  have hV (b : ZMod n) (hb : b ∈ V) : (b - c).val < r := by
    have hf : b ∈ arc c r := hunion ▸ Finset.mem_union_right U hb
    exact ((mem_interval_iff c b 0 r (by omega)).mp hf).2
  have hout : c + (r : ZMod n) ∉ arc c r := by
    rw [arc, mem_interval_iff c _ 0 r (by omega)]
    simp only [add_sub_cancel_left, ZMod.val_natCast_of_lt hr]
    omega
  have hout0 : (shiftSourceLift lift c).position (r : ZMod n) ≠ 0 := by
    rw [shiftSourceLift_position]
    intro h
    have hmem : c + (r : ZMod n) ∈ U := by
      rw [← hu.1]
      exact (mem_sourceFiber lift.position _ 0).mpr h
    exact hout (hunion ▸ Finset.mem_union_left V hmem)
  have hout1 : (shiftSourceLift lift c).position (r : ZMod n) ≠ 1 := by
    rw [shiftSourceLift_position]
    intro h
    have hmem : c + (r : ZMod n) ∈ V := by
      rw [← hv.1]
      exact (mem_sourceFiber lift.position _ 1).mpr h
    exact hout (hunion ▸ Finset.mem_union_right U hmem)
  refine ⟨hu.2, hv.2, hU, hV, ?_⟩
  intro a ha b hb
  have ha0 : (shiftSourceLift lift c).position (a - c) = 0 := by
    rw [shiftSourceLift_position, show c + (a - c) = a by abel]
    exact (mem_sourceFiber lift.position a 0).mp (hu.1.symm ▸ ha)
  have hb1 : (shiftSourceLift lift c).position (b - c) = 1 := by
    rw [shiftSourceLift_position, show c + (b - c) = b by abel]
    exact (mem_sourceFiber lift.position b 1).mp (hv.1.symm ▸ hb)
  exact ordered_port_addresses (shiftSourceLift lift c) r hr (a - c) (b - c)
    (hU a ha) (hV b hb) ha0 hb1 hout0 hout1

/-- The right parent's first aligned source address is the internal cut. -/
theorem sourceOrdered_registration_cut (P : Placement n (Finset (ZMod n)))
    (c : ZMod n) (r : ℕ) (U V : Finset (ZMod n)) (hr : r < n)
    (ordered : SourceOrdered P) (h0 : P 0 = some U) (h1 : P 1 = some V)
    (hunion : U ∪ V = arc c r) :
    ∃ t : ℕ, 1 ≤ t ∧ t < r ∧ U = interval c 0 t ∧ V = interval c t r := by
  classical
  obtain ⟨hUne, hVne, hU, hV, horder⟩ :=
    sourceOrdered_parent_addresses P c r U V hr ordered h0 h1 hunion
  let addresses := V.image (fun b => (b - c).val)
  have hne : addresses.Nonempty := hVne.image _
  let t := addresses.min' hne
  have htmem : t ∈ addresses := Finset.min'_mem addresses hne
  obtain ⟨b, hb, hbval⟩ := Finset.mem_image.mp htmem
  have htr : t < r := by rw [← hbval]; exact hV b hb
  have hmin (x : ZMod n) (hx : x ∈ V) : t ≤ (x - c).val :=
    Finset.min'_le addresses _ (Finset.mem_image.mpr ⟨x, hx, rfl⟩)
  obtain ⟨a, ha⟩ := hUne
  have ha_lt : (a - c).val < t := by rw [← hbval]; exact horder a ha b hb
  refine ⟨t, by omega, htr, ?_, ?_⟩
  · ext x
    rw [mem_interval_iff c x 0 t (by omega)]
    constructor
    · intro hx
      exact ⟨Nat.zero_le _, by rw [← hbval]; exact horder x hx b hb⟩
    · intro hx
      have hf : x ∈ arc c r := by
        rw [arc, mem_interval_iff c x 0 r (by omega)]
        omega
      have hsplit : x ∈ U ∨ x ∈ V := Finset.mem_union.mp (hunion.symm ▸ hf)
      rcases hsplit with h | h
      · exact h
      · have := hmin x h
        omega
  · ext x
    rw [mem_interval_iff c x t r (by omega)]
    constructor
    · intro hx
      exact ⟨hmin x hx, hV x hx⟩
    · intro hx
      have hf : x ∈ arc c r := by
        rw [arc, mem_interval_iff c x 0 r (by omega)]
        exact ⟨Nat.zero_le _, hx.2⟩
      rcases Finset.mem_union.mp (hunion.symm ▸ hf) with h | h
      · have : (x - c).val < t := by rw [← hbval]; exact horder x h b hb
        omega
      · exact h

end ProperArc
