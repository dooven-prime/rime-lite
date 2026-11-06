import RegisteredAbsorptionChains.CanonicalBlockNaming
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n t : ℕ} [NeZero n]

/-- Pure combinatorial geometry of a nonempty complement cut into `t`
positive source intervals. The carrier contains source atom zero and may wrap
across the source seam. The offsets encode occupied sites clockwise from `q`.
No execution or reachability assertion is part of this data. -/
structure ValidFiberPlacement (n t : ℕ) [NeZero n] where
  ht : 0 < t
  u : ℕ
  v : ℕ
  hu : 0 < u
  huv : u < v
  hvn : v ≤ n
  cut : Fin (t + 1) → ℕ
  cut_zero : cut ⟨0, Nat.zero_lt_succ t⟩ = u
  cut_last : cut ⟨t, Nat.lt_succ_self t⟩ = v
  cut_strict : StrictMono cut
  q : ZMod n
  offset : Fin (t + 1) → ℕ
  offset_zero : offset ⟨0, Nat.zero_lt_succ t⟩ = 0
  offset_strict : StrictMono offset
  offset_lt : ∀ i, offset i < n

def ValidFiberPlacement.carrier (data : ValidFiberPlacement n t) :
    Finset (ZMod n) :=
  Finset.univ.filter (fun a => a.val < data.u ∨ data.v ≤ a.val)

def ValidFiberPlacement.outside (data : ValidFiberPlacement n t)
    (i : Fin t) : Finset (ZMod n) :=
  Finset.univ.filter (fun a =>
    data.cut ⟨i.val, Nat.lt_succ_of_lt i.isLt⟩ ≤ a.val ∧
      a.val < data.cut ⟨i.val + 1, Nat.succ_lt_succ i.isLt⟩)

def ValidFiberPlacement.blockFin (data : ValidFiberPlacement n t)
    (i : Fin (t + 1)) : Finset (ZMod n) :=
  if h : i.val = 0 then data.carrier else
    data.outside ⟨i.val - 1, by omega⟩

def ValidFiberPlacement.siteFin (data : ValidFiberPlacement n t)
    (i : Fin (t + 1)) : ZMod n :=
  data.q + (data.offset i : ZMod n)

@[simp] theorem ValidFiberPlacement.blockFin_zero
    (data : ValidFiberPlacement n t) :
    data.blockFin ⟨0, Nat.zero_lt_succ t⟩ = data.carrier := by
  simp [ValidFiberPlacement.blockFin]

@[simp] theorem ValidFiberPlacement.siteFin_zero
    (data : ValidFiberPlacement n t) :
    data.siteFin ⟨0, Nat.zero_lt_succ t⟩ = data.q := by
  change data.q + (data.offset ⟨0, Nat.zero_lt_succ t⟩ : ZMod n) = data.q
  rw [data.offset_zero]
  simp

theorem ValidFiberPlacement.cut_bounds
    (data : ValidFiberPlacement n t) (i : Fin (t + 1)) :
    data.u ≤ data.cut i ∧ data.cut i ≤ data.v := by
  have hleft : (⟨0, Nat.zero_lt_succ t⟩ : Fin (t + 1)) ≤ i := Fin.zero_le i
  have hright : i ≤ (⟨t, Nat.lt_succ_self t⟩ : Fin (t + 1)) := by
    exact Fin.le_last i
  constructor
  · rw [← data.cut_zero]
    exact data.cut_strict.monotone hleft
  · rw [← data.cut_last]
    exact data.cut_strict.monotone hright

theorem ValidFiberPlacement.cut_cover
    (data : ValidFiberPlacement n t) (a : ℕ)
    (ha : data.u ≤ a) (hav : a < data.v) :
    ∃ i : Fin t,
      data.cut ⟨i.val, Nat.lt_succ_of_lt i.isLt⟩ ≤ a ∧
      a < data.cut ⟨i.val + 1, Nat.succ_lt_succ i.isLt⟩ := by
  let S : Finset (Fin (t + 1)) := Finset.univ.filter (fun j => a < data.cut j)
  have hlast : (⟨t, Nat.lt_succ_self t⟩ : Fin (t + 1)) ∈ S := by
    simp [S, data.cut_last, hav]
  have hS : S.Nonempty := ⟨_, hlast⟩
  let j : Fin (t + 1) := S.min' hS
  have hjmem : j ∈ S := Finset.min'_mem S hS
  have hjupper : a < data.cut j := (Finset.mem_filter.mp hjmem).2
  have hjpositive : 0 < j.val := by
    by_contra h
    have hval : j.val = 0 := Nat.eq_zero_of_not_pos h
    have hjzero : j = ⟨0, Nat.zero_lt_succ t⟩ := Fin.ext hval
    rw [hjzero, data.cut_zero] at hjupper
    omega
  have hjle : j.val ≤ t := by omega
  let i : Fin t := ⟨j.val - 1, by omega⟩
  have hisucc : (⟨i.val + 1, Nat.succ_lt_succ i.isLt⟩ : Fin (t + 1)) = j :=
    Fin.ext (by dsimp [i]; omega)
  have hi0 : (⟨i.val, Nat.lt_succ_of_lt i.isLt⟩ : Fin (t + 1)) < j := by
    rw [← hisucc]
    exact Fin.mk_lt_mk.mpr (by omega)
  have hilower : data.cut ⟨i.val, Nat.lt_succ_of_lt i.isLt⟩ ≤ a := by
    by_contra h
    have himem : (⟨i.val, Nat.lt_succ_of_lt i.isLt⟩ : Fin (t + 1)) ∈ S := by
      simp [S, Nat.lt_of_not_ge h]
    have hmin := Finset.min'_le S _ himem
    exact (not_lt_of_ge hmin) hi0
  exact ⟨i, hilower, hisucc ▸ hjupper⟩

theorem ValidFiberPlacement.siteFin_injective
    (data : ValidFiberPlacement n t) : Function.Injective data.siteFin := by
  intro i j hij
  have hcast : (data.offset i : ZMod n) = (data.offset j : ZMod n) := by
    have := hij
    simp only [ValidFiberPlacement.siteFin] at this
    exact add_left_cancel this
  have hval := congrArg ZMod.val hcast
  simp only [ZMod.val_natCast,
    Nat.mod_eq_of_lt (data.offset_lt i),
    Nat.mod_eq_of_lt (data.offset_lt j)] at hval
  exact data.offset_strict.injective hval

theorem ValidFiberPlacement.siteFin_offset
    (data : ValidFiberPlacement n t) (i : Fin (t + 1)) :
    (data.siteFin i - data.siteFin ⟨0, Nat.zero_lt_succ t⟩).val =
      data.offset i := by
  rw [data.siteFin_zero]
  have hdiff : data.siteFin i - data.q = (data.offset i : ZMod n) := by
    simp [ValidFiberPlacement.siteFin]
  rw [hdiff, ZMod.val_natCast]
  exact Nat.mod_eq_of_lt (data.offset_lt i)

noncomputable def ValidFiberPlacement.target
    (data : ValidFiberPlacement n t) :
    Placement n (Finset (ZMod n)) := fun q =>
  if h : ∃ i : Fin (t + 1), data.siteFin i = q then
    some (data.blockFin (Classical.choose h)) else none

theorem ValidFiberPlacement.target_at
    (data : ValidFiberPlacement n t) (i : Fin (t + 1)) :
    data.target (data.siteFin i) = some (data.blockFin i) := by
  let h : ∃ j : Fin (t + 1), data.siteFin j = data.siteFin i := ⟨i, rfl⟩
  have hchoice : Classical.choose h = i :=
    data.siteFin_injective (Classical.choose_spec h)
  simp only [ValidFiberPlacement.target, dif_pos h]
  rw [hchoice]

theorem ValidFiberPlacement.target_only_sites
    (data : ValidFiberPlacement n t) (q : ZMod n)
    (hoccupied : data.target q ≠ none) :
    ∃ i : Fin (t + 1), data.siteFin i = q := by
  by_contra h
  have hnone : data.target q = none := by
    simp [ValidFiberPlacement.target, h]
  exact hoccupied hnone

theorem ValidFiberPlacement.carrier_nonempty
    (data : ValidFiberPlacement n t) : data.carrier.Nonempty := by
  refine ⟨0, ?_⟩
  simp [ValidFiberPlacement.carrier, data.hu]

theorem ValidFiberPlacement.outside_nonempty
    (data : ValidFiberPlacement n t) (i : Fin t) :
    (data.outside i).Nonempty := by
  let lo : Fin (t + 1) := ⟨i.val, Nat.lt_succ_of_lt i.isLt⟩
  let hi : Fin (t + 1) := ⟨i.val + 1, Nat.succ_lt_succ i.isLt⟩
  have hstep : lo < hi := Fin.mk_lt_mk.mpr (by omega)
  have hcut : data.cut lo < data.cut hi := data.cut_strict hstep
  have hcutn : data.cut lo < n := by
    have hbound := (data.cut_bounds hi).2
    exact lt_of_lt_of_le hcut (le_trans hbound data.hvn)
  refine ⟨(data.cut lo : ZMod n), ?_⟩
  simp [ValidFiberPlacement.outside, lo, hi,
    ZMod.val_natCast, Nat.mod_eq_of_lt hcutn, hcut]

theorem ValidFiberPlacement.blockFin_nonempty
    (data : ValidFiberPlacement n t) (i : Fin (t + 1)) :
    (data.blockFin i).Nonempty := by
  by_cases h : i.val = 0
  · simpa [ValidFiberPlacement.blockFin, h] using data.carrier_nonempty
  · simpa [ValidFiberPlacement.blockFin, h] using
      data.outside_nonempty ⟨i.val - 1, by omega⟩

theorem ValidFiberPlacement.carrier_disjoint_outside
    (data : ValidFiberPlacement n t) (i : Fin t) :
    Disjoint data.carrier (data.outside i) := by
  apply Finset.disjoint_left.mpr
  intro a ha hc
  have hcarrier : a.val < data.u ∨ data.v ≤ a.val := by
    simpa [ValidFiberPlacement.carrier] using ha
  have hout : data.cut ⟨i.val, Nat.lt_succ_of_lt i.isLt⟩ ≤ a.val ∧
      a.val < data.cut ⟨i.val + 1, Nat.succ_lt_succ i.isLt⟩ := by
    simpa [ValidFiberPlacement.outside] using hc
  have hlow := (data.cut_bounds
    ⟨i.val, Nat.lt_succ_of_lt i.isLt⟩).1
  have hhigh := (data.cut_bounds
    ⟨i.val + 1, Nat.succ_lt_succ i.isLt⟩).2
  omega

theorem ValidFiberPlacement.outside_disjoint
    (data : ValidFiberPlacement n t) (i j : Fin t) (hij : i ≠ j) :
    Disjoint (data.outside i) (data.outside j) := by
  apply Finset.disjoint_left.mpr
  intro a hai haj
  have hi : data.cut ⟨i.val, Nat.lt_succ_of_lt i.isLt⟩ ≤ a.val ∧
      a.val < data.cut ⟨i.val + 1, Nat.succ_lt_succ i.isLt⟩ := by
    simpa [ValidFiberPlacement.outside] using hai
  have hj : data.cut ⟨j.val, Nat.lt_succ_of_lt j.isLt⟩ ≤ a.val ∧
      a.val < data.cut ⟨j.val + 1, Nat.succ_lt_succ j.isLt⟩ := by
    simpa [ValidFiberPlacement.outside] using haj
  have hne : i.val ≠ j.val := fun heq => hij (Fin.ext heq)
  rcases lt_or_gt_of_ne hne with hlt | hgt
  · have hbound :
        data.cut ⟨i.val + 1, Nat.succ_lt_succ i.isLt⟩ ≤
          data.cut ⟨j.val, Nat.lt_succ_of_lt j.isLt⟩ := by
      apply data.cut_strict.monotone
      exact Fin.mk_le_mk.mpr (by omega)
    omega
  · have hbound :
        data.cut ⟨j.val + 1, Nat.succ_lt_succ j.isLt⟩ ≤
          data.cut ⟨i.val, Nat.lt_succ_of_lt i.isLt⟩ := by
      apply data.cut_strict.monotone
      exact Fin.mk_le_mk.mpr (by omega)
    omega

theorem ValidFiberPlacement.blockFin_disjoint
    (data : ValidFiberPlacement n t)
    (i j : Fin (t + 1)) (hij : i ≠ j) :
    Disjoint (data.blockFin i) (data.blockFin j) := by
  by_cases hi : i.val = 0
  · have hj : j.val ≠ 0 := by
      intro hj
      exact hij (Fin.ext (hi.trans hj.symm))
    simpa [ValidFiberPlacement.blockFin, hi, hj] using
      data.carrier_disjoint_outside ⟨j.val - 1, by omega⟩
  by_cases hj : j.val = 0
  · simpa [ValidFiberPlacement.blockFin, hi, hj] using
      (data.carrier_disjoint_outside ⟨i.val - 1, by omega⟩).symm
  · have hpre : (⟨i.val - 1, by omega⟩ : Fin t) ≠
        (⟨j.val - 1, by omega⟩ : Fin t) := by
      intro heq
      apply hij
      apply Fin.ext
      have hval := congrArg Fin.val heq
      change i.val - 1 = j.val - 1 at hval
      omega
    simpa [ValidFiberPlacement.blockFin, hi, hj] using
      data.outside_disjoint ⟨i.val - 1, by omega⟩
        ⟨j.val - 1, by omega⟩ hpre

theorem ValidFiberPlacement.blockFin_cover
    (data : ValidFiberPlacement n t) (a : ZMod n) :
    ∃ i : Fin (t + 1), a ∈ data.blockFin i := by
  by_cases hc : a.val < data.u ∨ data.v ≤ a.val
  · refine ⟨⟨0, Nat.zero_lt_succ t⟩, ?_⟩
    simp [ValidFiberPlacement.blockFin, ValidFiberPlacement.carrier, hc]
  · have hu : data.u ≤ a.val := by omega
    have hv : a.val < data.v := by omega
    obtain ⟨i, hlo, hhi⟩ := data.cut_cover a.val hu hv
    refine ⟨⟨i.val + 1, Nat.succ_lt_succ i.isLt⟩, ?_⟩
    simp [ValidFiberPlacement.blockFin, ValidFiberPlacement.outside, hlo, hhi]

noncomputable def ValidFiberPlacement.toLegal
    (data : ValidFiberPlacement n t) :
    LegalNamedPlacement n (t + 1) (ZMod n) := by
  let toFin : ZMod (t + 1) → Fin (t + 1) :=
    (ZMod.finEquiv (t + 1)).symm
  refine {
    placed := data.target
    position := fun i => data.siteFin (toFin i)
    block := fun i => data.blockFin (toFin i)
    position_injective := ?_
    placed_at := ?_
    only_named := ?_
    block_nonempty := ?_
    block_disjoint := ?_
    atom_covered := ?_ }
  · intro i j hij
    exact (ZMod.finEquiv (t + 1)).symm.injective
      (data.siteFin_injective hij)
  · intro i
    exact data.target_at (toFin i)
  · intro q hoccupied
    obtain ⟨i, hi⟩ := data.target_only_sites q hoccupied
    refine ⟨ZMod.finEquiv (t + 1) i, ?_⟩
    simpa [toFin] using hi
  · intro i
    exact data.blockFin_nonempty (toFin i)
  · intro i j hij
    apply data.blockFin_disjoint
    exact fun heq => hij ((ZMod.finEquiv (t + 1)).symm.injective heq)
  · intro a
    obtain ⟨i, hi⟩ := data.blockFin_cover a
    refine ⟨ZMod.finEquiv (t + 1) i, ?_⟩
    simpa [toFin] using hi

theorem ValidFiberPlacement.toLegal_block
    (data : ValidFiberPlacement n t) (i : ZMod (t + 1)) :
    data.toLegal.block i =
      data.blockFin ((ZMod.finEquiv (t + 1)).symm i) := rfl

theorem ValidFiberPlacement.toLegal_position
    (data : ValidFiberPlacement n t) (i : ZMod (t + 1)) :
    data.toLegal.position i =
      data.siteFin ((ZMod.finEquiv (t + 1)).symm i) := rfl

theorem ValidFiberPlacement.toLegal_positive
    (data : ValidFiberPlacement n t) : data.toLegal.PositivelyOrdered := by
  intro k hk
  have hidx0 : (ZMod.finEquiv (t + 1)).symm (0 : ZMod (t + 1)) =
      ⟨0, Nat.zero_lt_succ t⟩ := by
    have h := finEquiv_symm_natCast (r := t + 1) 0 (Nat.zero_lt_succ t)
    simpa only [Nat.cast_zero] using h
  have hidxk : (ZMod.finEquiv (t + 1)).symm (k : ZMod (t + 1)) =
      ⟨k, hk⟩ := finEquiv_symm_natCast k hk
  have hcurrent : (data.toLegal.position (k : ZMod (t + 1)) -
      data.toLegal.position 0).val = data.offset ⟨k, hk⟩ := by
    rw [data.toLegal_position, data.toLegal_position, hidxk, hidx0]
    exact data.siteFin_offset ⟨k, hk⟩
  by_cases hnext : k + 1 < t + 1
  · have hidxnext : (ZMod.finEquiv (t + 1)).symm
        ((k + 1 : ℕ) : ZMod (t + 1)) = ⟨k + 1, hnext⟩ :=
      finEquiv_symm_natCast (k + 1) hnext
    have hnextOffset : (data.toLegal.position ((k + 1 : ℕ) : ZMod (t + 1)) -
        data.toLegal.position 0).val = data.offset ⟨k + 1, hnext⟩ := by
      rw [data.toLegal_position, data.toLegal_position, hidxnext, hidx0]
      exact data.siteFin_offset ⟨k + 1, hnext⟩
    have hstrict : data.offset ⟨k, hk⟩ < data.offset ⟨k + 1, hnext⟩ :=
      data.offset_strict (Fin.mk_lt_mk.mpr (by omega))
    change data.toLegal.offset k < data.toLegal.offset (k + 1)
    have hnextOffset' :
        (data.toLegal.position ((k : ZMod (t + 1)) + 1) -
          data.toLegal.position 0).val = data.offset ⟨k + 1, hnext⟩ := by
      simpa only [Nat.cast_add, Nat.cast_one] using hnextOffset
    simpa [LegalNamedPlacement.offset, hk, hnext, hcurrent, hnextOffset']
      using hstrict
  · have hend : k + 1 = t + 1 := by omega
    change data.toLegal.offset k < data.toLegal.offset (k + 1)
    rw [hend, data.toLegal.offset_end]
    simpa [LegalNamedPlacement.offset, hk, hcurrent] using
      data.offset_lt ⟨k, hk⟩

/-- The target obtains its positive-cycle witness from the cut and site
parameters. Only the already constructed source supplies the common names. -/
theorem ValidFiberPlacement.same_cycle_with_source
    (data : ValidFiberPlacement n t)
    (source : LegalNamedPlacement n (t + 1) (ZMod n))
    (source_order : source.PositivelyOrdered)
    (same_blocks : source.block = data.toLegal.block) :
    SameOrientedBlockCycle (r := t + 1) source.placed data.target := by
  exact ⟨source, data.toLegal, rfl, rfl,
    same_blocks, source_order, data.toLegal_positive⟩

/-- Conditional final step of the fixed-chain sufficiency construction.
The earlier assembly of the source packets and equality of the named blocks
are separate obligations; this theorem does not assert either one. -/
theorem ValidFiberPlacement.realize_from_named_source
    (data : ValidFiberPlacement n t)
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (source : LegalNamedPlacement n (t + 1) (ZMod n))
    (source_eq : s.placed = source.placed)
    (source_order : source.PositivelyOrdered)
    (same_blocks : source.block = data.toLegal.block) :
    ∃ word : List Letter,
      run F s word = { s with placed := data.target } ∧
      FusionFree F s word := by
  have hn : 2 ≤ n := by
    have := data.hu
    have := data.huv
    have := data.hvn
    omega
  have hr : 2 ≤ t + 1 := by
    have := data.ht
    omega
  exact realize_same_oriented_placements F s source data.toLegal hn hr
    source_eq ⟨same_blocks, source_order, data.toLegal_positive⟩

private def wrappedControl : ValidFiberPlacement 6 2 where
  ht := by decide
  u := 2
  v := 5
  hu := by decide
  huv := by decide
  hvn := by decide
  cut := ![2, 4, 5]
  cut_zero := by decide
  cut_last := by decide
  cut_strict := by decide
  q := 3
  offset := ![0, 2, 5]
  offset_zero := by decide
  offset_strict := by decide
  offset_lt := by decide

example : wrappedControl.carrier = ({0, 1, 5} : Finset (ZMod 6)) := by decide
example : wrappedControl.outside 0 = ({2, 3} : Finset (ZMod 6)) := by decide
example : wrappedControl.outside 1 = ({4} : Finset (ZMod 6)) := by decide
example : wrappedControl.siteFin 0 = (3 : ZMod 6) := by decide
example : wrappedControl.siteFin 1 = (5 : ZMod 6) := by decide
example : wrappedControl.siteFin 2 = (2 : ZMod 6) := by decide

end RegisteredAbsorptionChains
