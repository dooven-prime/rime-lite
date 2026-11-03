import FutureEvent.RegisterableData

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n r : ℕ} [NeZero n] [NeZero r]

noncomputable def nextSourceKey (named : LegalNamedPlacement n r (ZMod n))
    (i : Fin r) : ℕ :=
  if h : i.val + 1 < r then namedSourceKey named ⟨i.val + 1, h⟩ else n

/-- Sorted source keys and interval convexity recover the literal blocks. -/
theorem sorted_block_interval (named : LegalNamedPlacement n r (ZMod n))
    (hzero : named.block 0 = {0}) (hkeys : StrictMono (namedSourceKey named))
    (hlinear : ∀ i : Fin r, 0 < i.val → LinearSourceConvex (named.block (i.val : ZMod r)))
    (i : Fin r) (hi : 0 < i.val) :
    named.block (i.val : ZMod r) =
      sourceInterval (namedSourceKey named i) (nextSourceKey named i) := by
  have hnkey (j : Fin r) : namedSourceKey named j < n := sourceBlockKey_lt _ _
  have hupper : nextSourceKey named i ≤ n := by
    unfold nextSourceKey
    split_ifs
    · exact (hnkey _).le
    · rfl
  ext a
  rw [mem_sourceInterval_iff _ _ hupper]
  constructor
  · intro ha
    refine ⟨namedSourceKey_le named i a ha, ?_⟩
    by_cases hnext : i.val + 1 < r
    · let j : Fin r := ⟨i.val + 1, hnext⟩
      have hkeylt := hkeys (show i < j from Fin.mk_lt_mk.mpr (by omega))
      have hneq : (i.val : ZMod r) ≠ (j.val : ZMod r) := by
        intro he
        have hv := congrArg ZMod.val he
        rw [ZMod.val_natCast_of_lt i.isLt, ZMod.val_natCast_of_lt j.isLt] at hv
        have : i.val ≠ j.val := by change i.val ≠ i.val + 1; omega
        exact this hv
      have hlt : a.val < namedSourceKey named j := by
        by_contra hnot
        have hm := hlinear i hi (namedSourceKey named i) (namedSourceKey named j)
          a.val hkeylt.le (by omega) a.val_lt (namedSourceKey_mem named i)
          (by simpa only [ZMod.natCast_zmod_val] using ha)
        exact Finset.disjoint_left.mp (named.block_disjoint _ _ hneq) hm
          (namedSourceKey_mem named j)
      simpa [nextSourceKey, hnext, j] using hlt
    · simpa [nextSourceKey, hnext] using a.val_lt
  · rintro ⟨hlo, hhi⟩
    obtain ⟨j, hj⟩ := named.atom_covered a
    let jj : Fin r := ⟨j.val, j.val_lt⟩
    have hjblock : a ∈ named.block (jj.val : ZMod r) := by simpa [jj] using hj
    have hjpos : 0 < jj.val := by
      by_contra hnot
      have hj0 : j = 0 := ZMod.val_injective r (by
        simp only [ZMod.val_zero]
        have : ¬0 < j.val := hnot
        omega)
      have ha0 : a = 0 := by simpa [hj0, hzero] using hj
      have hkeypos : 0 < namedSourceKey named i := by
        have hi0 : (i.val : ZMod r) ≠ 0 := by
          intro he
          have hv := congrArg ZMod.val he
          rw [ZMod.val_natCast_of_lt i.isLt, ZMod.val_zero] at hv
          omega
        have hnot : (0 : ZMod n) ∉ named.block (i.val : ZMod r) := by
          intro hz
          exact Finset.disjoint_left.mp (named.block_disjoint _ _ hi0) hz (by simp [hzero])
        by_contra hp
        have hk0 : namedSourceKey named i = 0 := by omega
        exact hnot (by simpa [hk0] using namedSourceKey_mem named i)
      simp only [ha0, ZMod.val_zero] at hlo
      omega
    by_cases heq : jj = i
    · simpa [heq] using hjblock
    rcases lt_or_gt_of_ne heq with hbefore | hafter
    · have hkeylt := hkeys hbefore
      have hm := hlinear jj hjpos (namedSourceKey named jj) (namedSourceKey named i)
        a.val hkeylt.le hlo a.val_lt (namedSourceKey_mem named jj)
        (by simpa only [ZMod.natCast_zmod_val] using hjblock)
      have hneq : (jj.val : ZMod r) ≠ (i.val : ZMod r) := by
        intro he
        apply heq
        apply Fin.ext
        have hv := congrArg ZMod.val he
        simpa [ZMod.val_natCast_of_lt jj.isLt, ZMod.val_natCast_of_lt i.isLt] using hv
      exact False.elim (Finset.disjoint_left.mp (named.block_disjoint _ _ hneq) hm
        (namedSourceKey_mem named i))
    · have hnext : i.val + 1 < r := by have hv : i.val < jj.val := hafter; omega
      let next : Fin r := ⟨i.val + 1, hnext⟩
      have hle : next ≤ jj := Fin.mk_le_mk.mpr (by have hv : i.val < jj.val := hafter; change i.val + 1 ≤ jj.val; omega)
      have hk := hkeys.monotone hle
      have ha := namedSourceKey_le named jj a hjblock
      have hu : nextSourceKey named i = namedSourceKey named next := by simp [nextSourceKey, hnext, next]
      omega

variable {t : ℕ}

/-- A two-singleton placement is reconstructed without assuming registration. -/
theorem singleton_named_normal_form (hn : 3 ≤ n)
    (named : LegalNamedPlacement n (t + 1) (ZMod n)) (ht : 0 < t)
    (hpositive : named.PositivelyOrdered)
    (hkeys : StrictMono (namedSourceKey named)) (hzero : named.block 0 = {0})
    (hone : named.block 1 = {1})
    (hlinear : ∀ i : Fin (t + 1), 0 < i.val → LinearSourceConvex (named.block (i.val : ZMod (t + 1)))) :
    ∃ data : ValidFiberPlacement n t,
      data.u = 1 ∧ data.v = n ∧ data.cut ⟨1, by omega⟩ = 2 ∧
      data.target = named.placed := by
  have hkone : namedSourceKey named ⟨1, by omega⟩ = 1 := by
    have hm := namedSourceKey_mem named ⟨1, by omega⟩
    have hc : ((1 : ℕ) : ZMod (t + 1)) = 1 := by simp
    rw [hc, hone, Finset.mem_singleton] at hm
    have hv := congrArg ZMod.val hm
    rw [ZMod.val_natCast_of_lt (show namedSourceKey named ⟨1, by omega⟩ < n from sourceBlockKey_lt _ _)] at hv
    have hv1 : (1 : ZMod n).val = 1 := by
      simpa using ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega)
    exact hv.trans hv1
  let cut : Fin (t + 1) → ℕ := fun i =>
    if h : i.val < t then namedSourceKey named ⟨i.val + 1, by omega⟩ else n
  have hcuts : StrictMono cut := by
    intro i j hij
    have hi : i.val < t := by have hv : i.val < j.val := hij; omega
    dsimp [cut]
    rw [dif_pos hi]
    split_ifs with hj
    · exact hkeys (Fin.mk_lt_mk.mpr (by have hv : i.val < j.val := hij; omega))
    · exact sourceBlockKey_lt _ _
  let data : ValidFiberPlacement n t := {
    ht := ht, u := 1, v := n, hu := by omega, huv := by omega, hvn := le_rfl
    cut := cut
    cut_zero := by simpa only [cut, Fin.val_zero, dif_pos ht] using hkone
    cut_last := by simp [cut]
    cut_strict := hcuts
    q := named.position 0
    offset := fun i => named.offset i.val
    offset_zero := named.offset_zero
    offset_strict := namedOffset_strict hpositive
    offset_lt := by intro i; simp only [LegalNamedPlacement.offset, if_pos i.isLt]; exact ZMod.val_lt _ }
  have hsites (i : Fin (t + 1)) : data.siteFin i = named.position (i.val : ZMod (t + 1)) := by
    simpa [data, ValidFiberPlacement.siteFin] using (named.position_offset i.val i.isLt).symm
  have hblocks (i : Fin (t + 1)) : data.blockFin i = named.block (i.val : ZMod (t + 1)) := by
    by_cases hi : i.val = 0
    · have he : i = ⟨0, Nat.zero_lt_succ t⟩ := Fin.ext hi
      rw [he, data.blockFin_zero]
      simpa only [Nat.cast_zero, hzero] using singleton_zero_carrier data rfl rfl
    · have hib : 0 < i.val := by omega
      have hcutlow : cut ⟨i.val - 1, by omega⟩ = namedSourceKey named i := by
        have hbound : i.val - 1 < t := by omega
        simp only [cut, dif_pos hbound]
        have he : (⟨i.val - 1 + 1, by omega⟩ : Fin (t + 1)) = i := by apply Fin.ext; change i.val - 1 + 1 = i.val; omega
        rw [he]
      have hcuthi : cut i = nextSourceKey named i := by
        dsimp [cut, nextSourceKey]
        split_ifs <;> first | rfl | (exfalso; omega)
      rw [ValidFiberPlacement.blockFin, dif_neg hi, data.outside_eq_sourceInterval]
      have hsucc : (⟨i.val - 1 + 1, by omega⟩ : Fin (t + 1)) = i := by apply Fin.ext; change i.val - 1 + 1 = i.val; omega
      change sourceInterval (cut ⟨i.val - 1, by omega⟩) (cut ⟨i.val - 1 + 1, by have hi' := i.isLt; omega⟩) = _
      rw [hsucc, hcutlow, hcuthi]
      exact (sorted_block_interval named hzero hkeys hlinear i hib).symm
  have htarget : data.target = named.placed := by
    funext q
    by_cases hq : named.placed q = none
    · have hd : data.target q = none := by
        by_contra hnot
        obtain ⟨i, hi⟩ := data.target_only_sites q hnot
        have hm := named.placed_at (i.val : ZMod (t + 1))
        rw [← hsites i, hi, hq] at hm
        cases hm
      exact hd.trans hq.symm
    · obtain ⟨i, hi⟩ := named.only_named q hq
      let j : Fin (t + 1) := ⟨i.val, i.val_lt⟩
      have hj : (j.val : ZMod (t + 1)) = i := ZMod.natCast_zmod_val i
      rw [← hi, ← hj, ← hsites, data.target_at, hblocks, hsites]
      exact (named.placed_at _).symm
  have hcutone : data.cut ⟨1, by omega⟩ = 2 := by
    have hblock := hblocks (⟨1, by omega⟩ : Fin (t + 1))
    have hout : data.outside ⟨0, ht⟩ = {1} := by simpa [ValidFiberPlacement.blockFin, hone] using hblock
    have hstep := data.cut_strict (show (⟨0, by omega⟩ : Fin (t + 1)) < ⟨1, by omega⟩ from Fin.mk_lt_mk.mpr (by omega))
    rw [data.cut_zero] at hstep
    have hN := (data.cut_bounds ⟨1, by omega⟩).2
    have hle : data.cut ⟨1, by omega⟩ ≤ 2 := by
      by_contra hnot
      have htwoN : 2 < n := hn
      have hm : (2 : ZMod n) ∈ data.outside ⟨0, ht⟩ := by
        have hv2 : (2 : ZMod n).val = 2 := by simpa using ZMod.val_natCast_of_lt htwoN
        rw [data.outside_eq_sourceInterval, data.cut_zero, mem_sourceInterval_iff _ _ (hN.trans data.hvn), hv2]
        change 1 ≤ 2 ∧ 2 < data.cut ⟨1, by omega⟩
        omega
      rw [hout, Finset.mem_singleton] at hm
      have hv := congrArg ZMod.val hm
      have hv2 : (2 : ZMod n).val = 2 := by simpa using ZMod.val_natCast_of_lt htwoN
      have hv1 : (1 : ZMod n).val = 1 := by simpa using ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega)
      rw [hv2, hv1] at hv
      omega
    change data.cut ⟨1, by omega⟩ = 2
    change 1 < data.cut ⟨1, by omega⟩ at hstep
    omega
  exact ⟨data, rfl, rfl, hcutone, htarget⟩

end FutureEvent
