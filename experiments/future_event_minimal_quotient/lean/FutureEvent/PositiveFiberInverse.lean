import FutureEvent.PlacementGeometry

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n t : ℕ} [NeZero n]

theorem fiber_named_key (data : ValidFiberPlacement n t) (i : Fin (t + 1)) :
    namedSourceKey data.toLegal i =
      if hi : i.val = 0 then 0 else data.cut ⟨i.val - 1, by omega⟩ := by
  have hblock : data.toLegal.block (i.val : ZMod (t + 1)) = data.blockFin i := by
    rw [data.toLegal_block, finEquiv_symm_natCast i.val i.isLt]
  by_cases hi : i.val = 0
  · rw [dif_pos hi]
    have hz : (0 : ZMod n) ∈ data.toLegal.block (i.val : ZMod (t + 1)) := by
      rw [hblock]
      have hie : i = ⟨0, Nat.zero_lt_succ t⟩ := Fin.ext hi
      rw [hie, data.blockFin_zero]
      exact fiber_carrier_zero data
    have hle := namedSourceKey_le data.toLegal i 0 hz
    simp only [ZMod.val_zero] at hle
    omega
  · rw [dif_neg hi]
    let j : Fin t := ⟨i.val - 1, by omega⟩
    have hsucc : (⟨j.val + 1, by omega⟩ : Fin (t + 1)) = i := Fin.ext (by dsimp [j]; omega)
    have hsource : data.toLegal.block (i.val : ZMod (t + 1)) =
        sourceInterval (data.cut ⟨i.val - 1, by omega⟩) (data.cut i) := by
      rw [hblock]
      simp only [ValidFiberPlacement.blockFin, dif_neg hi]
      change data.outside j = _
      rw [data.outside_eq_sourceInterval j, hsucc]
    have hlohi : data.cut ⟨i.val - 1, by omega⟩ < data.cut i :=
      data.cut_strict (Fin.mk_lt_mk.mpr (by omega))
    have hhin : data.cut i ≤ n := (data.cut_bounds i).2.trans data.hvn
    have hmem := namedSourceKey_mem data.toLegal i
    rw [hsource, mem_sourceInterval_iff _ _ hhin] at hmem
    have hkeylt : namedSourceKey data.toLegal i < n := sourceBlockKey_lt _ _
    rw [ZMod.val_natCast_of_lt hkeylt] at hmem
    have hloN : data.cut ⟨i.val - 1, by omega⟩ < n := by omega
    have hleft : (data.cut ⟨i.val - 1, by omega⟩ : ZMod n) ∈
        data.toLegal.block (i.val : ZMod (t + 1)) := by
      rw [hsource, mem_sourceInterval_iff _ _ hhin, ZMod.val_natCast_of_lt hloN]
      omega
    have hle := namedSourceKey_le data.toLegal i _ hleft
    rw [ZMod.val_natCast_of_lt hloN] at hle
    omega

theorem fiber_named_keys_strict (data : ValidFiberPlacement n t) :
    StrictMono (namedSourceKey data.toLegal) := by
  intro i j hij
  rw [fiber_named_key, fiber_named_key]
  have hj : j.val ≠ 0 := by have hv : i.val < j.val := hij; omega
  rw [dif_neg hj]
  by_cases hi : i.val = 0
  · rw [dif_pos hi]
    have hb := (data.cut_bounds ⟨j.val - 1, by omega⟩).1
    have hu := data.hu
    omega
  · rw [dif_neg hi]
    exact data.cut_strict (Fin.mk_lt_mk.mpr (by have hv : i.val < j.val := hij; omega))

/-- Pure target uniqueness works also for a singleton-zero carrier (u=1).
The earlier fixed-pair interface requires u>=2 and is left unchanged. -/
theorem positive_fiber_target_injective (first second : ValidFiberPlacement n t)
    (h : first.target = second.target) : first = second := by
  have hb := fiber_carrier_bounds_recovery first second (fiber_target_carrier_recovery first second h).1
  have hk : namedSourceKey first.toLegal = namedSourceKey second.toLegal := by
    apply strictMono_fin_eq_of_image_eq _ _ (fiber_named_keys_strict first) (fiber_named_keys_strict second)
    rw [first.toLegal.keys_image_eq, second.toLegal.keys_image_eq]
    change occupiedKeys first.target = occupiedKeys second.target
    rw [h]
  have hs := (LegalNamedPlacement.same_sorted_names h
    (fiber_named_keys_strict first) (fiber_named_keys_strict second)).2
  have hsites (i : Fin (t + 1)) : first.siteFin i = second.siteFin i := by
    have he := hs i
    rw [first.toLegal_position, second.toLegal_position,
      finEquiv_symm_natCast i.val i.isLt] at he
    exact he
  apply ValidFiberPlacement.ext_fields first second hb.1 hb.2
  · funext i
    by_cases hi : i.val = t
    · have hie : i = ⟨t, Nat.lt_succ_self t⟩ := Fin.ext hi
      rw [hie, first.cut_last, second.cut_last]
      exact hb.2
    · let j : Fin (t + 1) := ⟨i.val + 1, by omega⟩
      have he := congrFun hk j
      rw [fiber_named_key, fiber_named_key, dif_neg (by dsimp [j]; omega),
        dif_neg (by dsimp [j]; omega)] at he
      simpa [j] using he
  · have he := hsites ⟨0, Nat.zero_lt_succ t⟩
    simpa only [first.siteFin_zero, second.siteFin_zero] using he
  · funext i
    calc
      first.offset i = (first.siteFin i - first.siteFin ⟨0, Nat.zero_lt_succ t⟩).val :=
        (first.siteFin_offset i).symm
      _ = (second.siteFin i - second.siteFin ⟨0, Nat.zero_lt_succ t⟩).val := by rw [hsites, hsites]
      _ = second.offset i := second.siteFin_offset i

end FutureEvent
