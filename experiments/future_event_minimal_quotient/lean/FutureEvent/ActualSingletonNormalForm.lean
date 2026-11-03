import FutureEvent.SingletonPlacementNormalForm

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

theorem actual_singleton_naming (hn : 3 ≤ n) (s : Execution n (ZMod n))
    (hg : PairGenerated s) (hr : PairRegisterable s) :
    ∃ (r : ℕ) (hr : NeZero r), letI : NeZero r := hr
      ∃ named : LegalNamedPlacement n r (ZMod n),
        2 ≤ r ∧ named.placed = s.placed ∧ named.PositivelyOrdered ∧
        StrictMono (namedSourceKey named) ∧ named.block 0 = {0} ∧ named.block 1 = {1} ∧
        (∀ i : Fin r, 0 < i.val → LinearSourceConvex (named.block (i.val : ZMod r))) := by
  obtain ⟨lift, hp⟩ := pairGenerated_sourceOrdered s (by omega) hg
  have hs := (generated_registerable_iff_singletons s lift.position hn hg hp hr.1).mp hr
  have h0 : s.placed (lift.position 0) = some {0} := by
    rw [hp]
    apply (placementOfMap_some_iff _ _ _).mpr
    exact ⟨(singletonSource_iff_fiber _ _).mp hs.1, Finset.singleton_nonempty _⟩
  have h1 : s.placed (lift.position 1) = some {1} := by
    rw [hp]
    apply (placementOfMap_some_iff _ _ _).mpr
    exact ⟨(singletonSource_iff_fiber _ _).mp hs.2, Finset.singleton_nonempty _⟩
  have hordered : SourceOrdered s.placed := ⟨lift, hp⟩
  have hb0 : ({0} : Finset (ZMod n)) ∈ placedBlocks s.placed :=
    (mem_placedBlocks _ _).mpr ⟨Finset.singleton_nonempty _, _, h0⟩
  have hb1 : ({1} : Finset (ZMod n)) ∈ placedBlocks s.placed :=
    (mem_placedBlocks _ _).mpr ⟨Finset.singleton_nonempty _, _, h1⟩
  have hne : ({0} : Finset (ZMod n)) ≠ {1} := by
    intro he
    have he' : (0 : ZMod n) = 1 := Finset.singleton_injective he
    have := ZMod.one_eq_zero_iff.mp he'.symm
    omega
  let r := (placedBlocks s.placed).card
  have hr2 : 2 ≤ r := Finset.one_lt_card.mpr ⟨{0}, hb0, {1}, hb1, hne⟩
  letI : NeZero r := ⟨by omega⟩
  let named := canonicalLegalNamed s.placed s.placed hordered hordered rfl
  have hzero : named.block 0 = {0} := canonical_named_carrier s hordered {0} ⟨_, h0⟩ (by simp)
  have hkeys : StrictMono (namedSourceKey named) := canonical_namedSourceKey_strict _ _
  have hone : named.block 1 = {1} := by
    obtain ⟨j, hj⟩ := named.only_named (lift.position 1) (by change s.placed _ ≠ none; simp [h1])
    have hbj : named.block j = {1} := Option.some.inj ((named.placed_at j).symm.trans (hj ▸ h1))
    let jj : Fin r := ⟨j.val, j.val_lt⟩
    have hjkey : namedSourceKey named jj = 1 := by
      have hm := namedSourceKey_mem named jj
      have hcast : (jj.val : ZMod r) = j := ZMod.natCast_zmod_val j
      rw [hcast, hbj, Finset.mem_singleton] at hm
      have hv := congrArg ZMod.val hm
      have hv1 : (1 : ZMod n).val = 1 := by simpa using ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega)
      rw [ZMod.val_natCast_of_lt (show namedSourceKey named jj < n from sourceBlockKey_lt _ _), hv1] at hv
      exact hv
    have hjpos : 0 < j.val := by
      by_contra hnot
      have hj0 : j = 0 := ZMod.val_injective r (by simp only [ZMod.val_zero]; omega)
      exact hne (hzero.symm.trans (hj0 ▸ hbj))
    have hfirstpos : 0 < namedSourceKey named ⟨1, hr2⟩ := by
      have hk0 : namedSourceKey named ⟨0, by omega⟩ = 0 := by
        have hle := namedSourceKey_le named ⟨0, by omega⟩ 0 (by simpa [hzero])
        simp only [ZMod.val_zero] at hle
        omega
      have hh := hkeys (show (⟨0, by omega⟩ : Fin r) < ⟨1, hr2⟩ from Fin.mk_lt_mk.mpr (by omega))
      omega
    have hjval : j.val = 1 := by
      by_contra hnot
      have hgt : 1 < j.val := by omega
      have hh := hkeys (show (⟨1, hr2⟩ : Fin r) < jj from Fin.mk_lt_mk.mpr hgt)
      omega
    have hj1 : j = 1 := by
      rw [← ZMod.natCast_zmod_val j, hjval]
      simp
    exact hj1 ▸ hbj
  have hlinear (i : Fin r) (hi : 0 < i.val) : LinearSourceConvex (named.block (i.val : ZMod r)) := by
    have hi0 : (i.val : ZMod r) ≠ 0 := by
      intro he
      have hv := congrArg ZMod.val he
      rw [ZMod.val_natCast_of_lt i.isLt, ZMod.val_zero] at hv
      omega
    have hdis := named.position_injective.ne hi0
    have hc : s.placed (named.position 0) = some {0} := by
      have hh := named.placed_at 0
      rw [hzero] at hh
      exact hh
    have hb : s.placed (named.position (i.val : ZMod r)) = some (named.block (i.val : ZMod r)) := named.placed_at _
    exact (actual_outside_packet_linear s {0} _ _ _ hordered hdis.symm hc hb (by simp)).2.1
  exact ⟨r, inferInstance, named, hr2, rfl,
    canonicalLegalNamed_positive _ _ hordered hordered rfl, hkeys, hzero, hone, hlinear⟩

theorem actual_singleton_normal_form (hn : 3 ≤ n) (s : Execution n (ZMod n))
    (hg : PairGenerated s) (hr : PairRegisterable s) :
    ∃ t, ∃ data : ValidFiberPlacement n (t + 1),
      0 < t ∧ data.u = 1 ∧ data.v = n ∧ data.cut ⟨1, by omega⟩ = 2 ∧
      data.target = s.placed := by
  obtain ⟨r, hr, named, hr2, hp, hpositive, hkeys, hzero, hone, hlinear⟩ :=
    actual_singleton_naming hn s hg hr
  letI : NeZero r := hr
  obtain ⟨a, ha⟩ : ∃ a, r = a + 1 := ⟨r - 1, by omega⟩
  have ha_pos : 0 < a := by omega
  subst r
  obtain ⟨data, hu, hv, hc, hp'⟩ := singleton_named_normal_form hn named ha_pos
    hpositive hkeys hzero hone hlinear
  have ha2 : 2 ≤ a := by
    by_contra hnot
    have ha1 : a = 1 := by omega
    have he := data.cut_last
    have he1 : (⟨a, Nat.lt_succ_self a⟩ : Fin (a + 1)) = ⟨1, by omega⟩ := Fin.ext ha1
    rw [he1, hc, hv] at he
    omega
  cases a with
  | zero => omega
  | succ t => exact ⟨t, data, by omega, hu, hv, hc, hp'.trans hp⟩

end FutureEvent
