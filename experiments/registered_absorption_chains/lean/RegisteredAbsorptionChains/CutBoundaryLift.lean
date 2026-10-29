import RegisteredAbsorptionChains.CutBoundaryPlan
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n r : ℕ} [NeZero n] [NeZero r]

/-- Source-addressed names for a current outside partition. The cuts are
specified only on indices below `r`; no arbitrary placement is admitted. -/
structure CutNamed
    (f : CheckpointSourceFrontier n)
    (named : LegalNamedPlacement n r (ZMod n)) where
  count : 2 ≤ r
  carrier : named.block 0 = f.carrier
  cut : ℕ → ℕ
  cut_zero : cut 0 = f.lo
  cut_last : cut (r - 1) = f.hi
  cut_step : ∀ i, i + 1 < r → cut i < cut (i + 1)
  outside : ∀ i, 1 ≤ i → i < r →
    named.block (i : ZMod r) = sourceInterval (cut (i - 1)) (cut i)

theorem CutNamed.cut_mono
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : CutNamed f named) (i j : ℕ) (hij : i ≤ j) (hj : j < r) :
    h.cut i ≤ h.cut j := by
  have aux : ∀ j : ℕ, j < r → ∀ i, i ≤ j → h.cut i ≤ h.cut j := by
    intro j hj
    induction j with
    | zero =>
        intro i hi
        have : i = 0 := by omega
        subst i
        exact le_refl _
    | succ j ih =>
        intro i hi
        by_cases heq : i = j + 1
        · subst i
          exact le_refl _
        · exact (ih (by omega) i (by omega)).trans
            (le_of_lt (h.cut_step j hj))
  exact aux j hj i hij

theorem CutNamed.cut_le_n
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : CutNamed f named) (i : ℕ) (hi : i < r) :
    h.cut i ≤ n := by
  have hlast := h.cut_mono i (r - 1) (by omega) (by omega)
  rw [h.cut_last] at hlast
  exact hlast.trans f.hi_valid

noncomputable def CutNamed.boundaries
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : CutNamed f named) : Finset ℕ :=
  (Finset.Ico 1 (r - 1)).image h.cut

theorem CutNamed.cut_inj
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : CutNamed f named) (i j : ℕ) (hi : i < r) (hj : j < r)
    (heq : h.cut i = h.cut j) : i = j := by
  by_contra hne
  rcases lt_or_gt_of_ne hne with hij | hji
  · have hstep := h.cut_step i (by omega)
    have hmono := h.cut_mono (i + 1) j (by omega) hj
    omega
  · have hstep := h.cut_step j (by omega)
    have hmono := h.cut_mono (j + 1) i (by omega) hi
    omega

def eraseCut (cut : ℕ → ℕ) (j i : ℕ) : ℕ :=
  if i < j then cut i else cut (i + 1)

theorem eraseCut_zero (cut : ℕ → ℕ) (j : ℕ) (hj : 0 < j) :
    eraseCut cut j 0 = cut 0 := by simp [eraseCut, hj]

theorem eraseCut_last (cut : ℕ → ℕ) (j : ℕ) (hj : j + 1 < r) :
    eraseCut cut j (r - 2) = cut (r - 1) := by
  have hnot : ¬ r - 2 < j := by omega
  simp [eraseCut, hnot, show r - 2 + 1 = r - 1 by omega]

theorem eraseCut_step (cut : ℕ → ℕ)
    (hstep : ∀ i, i + 1 < r → cut i < cut (i + 1))
    (j i : ℕ) (hj : j + 1 < r) (hi : i + 1 < r - 1) :
    eraseCut cut j i < eraseCut cut j (i + 1) := by
  unfold eraseCut
  split_ifs with hleft hright
  · exact hstep i (by omega)
  · have hji : i + 1 = j := by omega
    have h1 := hstep i (by omega)
    have h2 := hstep (i + 1) (by omega)
    omega
  · omega
  · exact hstep (i + 1) (by omega)

/-- Removing the cut between adjacent outside names changes the source
interval list exactly as the actual named merger does. -/
noncomputable def CutNamed.merge
    [NeZero (r - 1)]
    (f : CheckpointSourceFrontier n)
    (first : LegalNamedPlacement n r (ZMod n))
    (hrn : r ≤ n) (j : ℕ) (hjpos : 0 < j) (hj : j + 1 < r)
    (h : CutNamed f first) :
    CutNamed f (merge_named_outside first hrn j hj) := by
  let next := merge_named_outside first hrn j hj
  refine {
    count := by omega
    carrier := merge_named_outside_zero first hrn j hjpos hj |>.trans h.carrier
    cut := eraseCut h.cut j
    cut_zero := by rw [eraseCut_zero h.cut j hjpos, h.cut_zero]
    cut_last := by
      have hidx : r - 1 - 1 = r - 2 := by omega
      rw [hidx, eraseCut_last (r := r) h.cut j hj, h.cut_last]
    cut_step := eraseCut_step h.cut h.cut_step j (hj := hj)
    outside := ?_
  }
  intro i hi1 hir
  by_cases hij : i = j
  · subst i
    rw [merge_named_outside_at_j first hrn j hj,
      h.outside j hjpos (by omega),
      h.outside (j + 1) (by omega) hj]
    have hidx : j + 1 - 1 = j := by omega
    rw [hidx]
    have hcuts : h.cut (j - 1) ≤ h.cut j := by
      have hs := h.cut_step (j - 1) (by omega)
      convert le_of_lt hs using 1 <;> congr 1 <;> omega
    have hcuts' : h.cut j ≤ h.cut (j + 1) := le_of_lt (h.cut_step j hj)
    rw [sourceInterval_adjacent (h.cut (j - 1)) (h.cut j) (h.cut (j + 1))
      hcuts hcuts' (h.cut_le_n (j + 1) hj)]
    simp [eraseCut, show j - 1 < j by omega, show ¬ j < j by omega]
  · have hz : (i : ZMod (r - 1)) ≠ (j : ZMod (r - 1)) := by
      intro heq
      have hv := congrArg ZMod.val heq
      rw [ZMod.val_natCast_of_lt hir,
        ZMod.val_natCast_of_lt (show j < r - 1 by omega)] at hv
      exact hij hv
    rw [merge_named_outside_other first hrn j hj _ hz]
    by_cases hijlt : i < j
    · have hOld : mergeOldIndex j (i : ZMod (r - 1)) = (i : ZMod r) := by
        apply ZMod.val_injective r
        rw [mergeOldIndex_val, ZMod.val_natCast_of_lt (by omega)]
        simp [mergeSkip, ZMod.val_natCast_of_lt hir, le_of_lt hijlt]
      rw [hOld, h.outside i hi1 (by omega)]
      simp [eraseCut, hijlt, show i - 1 < j by omega]
    · have hbig : j < i := by omega
      have hOld : mergeOldIndex j (i : ZMod (r - 1)) = ((i + 1 : ℕ) : ZMod r) := by
        apply ZMod.val_injective r
        rw [mergeOldIndex_val, ZMod.val_natCast_of_lt (by omega)]
        simp [mergeSkip, ZMod.val_natCast_of_lt hir,
          show ¬ i ≤ j by omega]
      rw [hOld, h.outside (i + 1) (by omega) (by omega)]
      simp [eraseCut, show ¬ i - 1 < j by omega, hijlt,
        show i - 1 + 1 = i by omega]

theorem CutNamed.boundaries_merge
    [NeZero (r - 1)]
    (f : CheckpointSourceFrontier n)
    (first : LegalNamedPlacement n r (ZMod n))
    (hrn : r ≤ n) (j : ℕ) (hjpos : 0 < j) (hj : j + 1 < r)
    (h : CutNamed f first) :
    (h.merge f first hrn j hjpos hj).boundaries =
      h.boundaries.erase (h.cut j) := by
  ext b
  change b ∈ (Finset.Ico 1 (r - 1 - 1)).image (eraseCut h.cut j) ↔
    b ∈ ((Finset.Ico 1 (r - 1)).image h.cut).erase (h.cut j)
  simp only [Finset.mem_image, Finset.mem_Ico, Finset.mem_erase]
  constructor
  · rintro ⟨i, ⟨hi1, hir⟩, rfl⟩
    by_cases hij : i < j
    · have hiold : i < r - 1 := by omega
      have hne : h.cut i ≠ h.cut j := by
        intro heq
        have hidx := h.cut_inj i j (by omega) (by omega) heq
        omega
      exact ⟨by simpa [eraseCut, hij] using hne,
        i, ⟨hi1, hiold⟩, by simp [eraseCut, hij]⟩
    · have hik : 1 ≤ i + 1 ∧ i + 1 < r - 1 := by omega
      have hne : h.cut (i + 1) ≠ h.cut j := by
        intro heq
        have hidx := h.cut_inj (i + 1) j (by omega) (by omega) heq
        omega
      exact ⟨by simpa [eraseCut, hij] using hne,
        i + 1, hik, by simp [eraseCut, hij]⟩
  · rintro ⟨hne, k, ⟨hk1, hkr⟩, hkb⟩
    have hkj : k ≠ j := by
      intro heq
      subst k
      exact hne hkb.symm
    by_cases hlt : k < j
    · refine ⟨k, ⟨hk1, by omega⟩, ?_⟩
      simpa [eraseCut, hlt] using hkb
    · have hgt : j < k := by omega
      refine ⟨k - 1, ⟨by omega, by omega⟩, ?_⟩
      have hnot : ¬ k - 1 < j := by omega
      simpa [eraseCut, hnot, show k - 1 + 1 = k by omega] using hkb

/-- Every local cut deletion is one genuine outside-fusion stage, and its
successor is named by the erased-cut partition on the same execution. -/
theorem CutNamed.merge_actual
    [NeZero (r - 1)]
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (h : CutNamed f first)
    (ordered : first.PositivelyOrdered)
    (hrn : r ≤ n) (source : s.placed = first.placed)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ f.carrier)
    (j : ℕ) (hjpos : 0 < j) (hj : j + 1 < r) :
    let next := merge_named_outside first hrn j hj
    CountedOutsideSchedule F f.carrier 1 s
      {s with placed := next.placed} ∧
    next.PositivelyOrdered := by
  let next := merge_named_outside first hrn j hj
  have hleft : Disjoint f.carrier (first.block (j : ZMod r)) := by
    rw [← h.carrier]
    apply first.block_disjoint
    intro heq
    have hv := congrArg ZMod.val heq
    rw [ZMod.val_zero, ZMod.val_natCast_of_lt (by omega)] at hv
    omega
  have hright : Disjoint f.carrier
      (first.block ((j + 1 : ℕ) : ZMod r)) := by
    rw [← h.carrier]
    apply first.block_disjoint
    intro heq
    have hv := congrArg ZMod.val heq
    rw [ZMod.val_zero, ZMod.val_natCast_of_lt hj] at hv
    omega
  have hcount := packed_adjacent_partner_schedule_count F f.carrier s first
    ordered hrn source j hjpos hj h.carrier registered selected inside
    hleft hright
  refine ⟨?_,
    merge_named_outside_positive first hrn j hjpos hj⟩
  simpa only [next, merge_named_outside] using hcount

theorem sourceInterval_singleton (u : ℕ) (hu : u + 1 ≤ n) :
    sourceInterval (n := n) u (u + 1) = {(u : ZMod n)} := by
  ext a
  rw [mem_sourceInterval_iff u (u + 1) hu]
  have hval : ((u : ℕ) : ZMod n).val = u :=
    ZMod.val_natCast_of_lt (by omega)
  constructor
  · intro ha
    have huEq : a.val = u := by omega
    simp only [Finset.mem_singleton]
    calc
      a = (a.val : ZMod n) := (ZMod.natCast_zmod_val a).symm
      _ = (u : ZMod n) := by rw [huEq]
  · intro ha
    simp only [Finset.mem_singleton] at ha
    rw [ha, hval]
    omega

/-- A clean generated checkpoint has all singleton cuts. This is the
starting point for the deletion induction, not an arbitrary partition. -/
noncomputable def CheckpointNamedAlignment.toCutNamed
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (aligned : CheckpointNamedAlignment F f s first)
    (hremaining : f.lo < f.hi) : CutNamed f first := by
  refine {
    count := by have := aligned.count; omega
    carrier := aligned.carrier
    cut := fun i => f.lo + i
    cut_zero := by omega
    cut_last := by have := aligned.count; omega
    cut_step := by intro i _; omega
    outside := ?_
  }
  intro i hi1 hir
  rw [aligned.outside i hi1 hir]
  have hidx : f.lo + (i - 1) + 1 = f.lo + i := by omega
  rw [← hidx]
  exact (sourceInterval_singleton (f.lo + (i - 1)) (by
    have := aligned.count
    have := f.hi_valid
    omega)).symm

theorem CheckpointNamedAlignment.initial_boundaries
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (aligned : CheckpointNamedAlignment F f s first)
    (hremaining : f.lo < f.hi) :
    (aligned.toCutNamed F f s first hremaining).boundaries =
      Finset.Ioo f.lo f.hi := by
  ext b
  change b ∈ (Finset.Ico 1 (r - 1)).image (fun i => f.lo + i) ↔
    b ∈ Finset.Ioo f.lo f.hi
  simp only [Finset.mem_image, Finset.mem_Ico, Finset.mem_Ioo]
  constructor
  · rintro ⟨i, ⟨hi1, hir⟩, rfl⟩
    have := aligned.count
    omega
  · intro hb
    have hc := aligned.count
    refine ⟨b - f.lo, ⟨by omega, by omega⟩, by omega⟩

theorem CutNamed.cutFin_strict
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : CutNamed f named) :
    StrictMono (fun i : Fin r => h.cut i.val) := by
  intro i j hij
  have hi := h.cut_step i.val (by omega)
  have hmid := h.cut_mono (i.val + 1) j.val (by omega) j.isLt
  exact hi.trans_le hmid

theorem CutNamed.fullCuts_eq
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : CutNamed f named) :
    Finset.univ.image (fun i : Fin r => h.cut i.val) =
      insert f.lo (insert f.hi h.boundaries) := by
  ext b
  simp only [Finset.mem_image, Finset.mem_univ, true_and,
    Finset.mem_insert]
  constructor
  · rintro ⟨i, rfl⟩
    by_cases hi0 : i.val = 0
    · left
      simpa [hi0] using h.cut_zero
    by_cases hilast : i.val = r - 1
    · right
      left
      simpa [hilast] using h.cut_last
    · right
      right
      apply Finset.mem_image.mpr
      refine ⟨i.val, Finset.mem_Ico.mpr ⟨by omega, by omega⟩, rfl⟩
  · rintro (rfl | rfl | hb)
    · exact ⟨⟨0, by have := h.count; omega⟩, h.cut_zero⟩
    · exact ⟨⟨r - 1, by have := h.count; omega⟩, h.cut_last⟩
    · obtain ⟨i, hi, hib⟩ := Finset.mem_image.mp hb
      have hir := (Finset.mem_Ico.mp hi).2
      exact ⟨⟨i, by omega⟩, hib⟩

theorem ValidFiberPlacement.fullCuts_eq
    (data : ValidFiberPlacement n t) :
    Finset.univ.image data.cut =
      insert data.u (insert data.v (targetCutBoundaries data)) := by
  ext b
  simp only [Finset.mem_image, Finset.mem_univ, true_and,
    Finset.mem_insert]
  constructor
  · rintro ⟨i, rfl⟩
    by_cases hi0 : i.val = 0
    · left
      have hidx : i = ⟨0, by omega⟩ := Fin.ext hi0
      simpa [hidx] using data.cut_zero
    by_cases hilast : i.val = t
    · right
      left
      have hidx : i = ⟨t, by omega⟩ := Fin.ext hilast
      simpa [hidx] using data.cut_last
    · right
      right
      apply Finset.mem_image.mpr
      refine ⟨⟨i.val - 1, by omega⟩, Finset.mem_univ _, ?_⟩
      have hidx : (⟨(i.val - 1) + 1, by omega⟩ : Fin (t + 1)) = i :=
        Fin.ext (by change i.val - 1 + 1 = i.val; omega)
      exact congrArg data.cut hidx
  · rintro (rfl | rfl | hb)
    · exact ⟨⟨0, by omega⟩, data.cut_zero⟩
    · exact ⟨⟨t, by omega⟩, data.cut_last⟩
    · obtain ⟨i, _, hib⟩ := Finset.mem_image.mp hb
      exact ⟨⟨i.val + 1, by omega⟩, hib⟩

theorem strictMono_fin_eq_of_image_eq
    {m : ℕ} (a b : Fin m → ℕ)
    (ha : StrictMono a) (hb : StrictMono b)
    (himage : Finset.univ.image a = Finset.univ.image b) :
    a = b := by
  apply (StrictMono.range_inj ha hb).mp
  ext x
  have h := congrArg (fun s : Finset ℕ => x ∈ s) himage
  simpa [Set.mem_range, Finset.mem_image] using h

theorem CutNamed.cut_eq_target
    (f : CheckpointSourceFrontier n)
    (data : ValidFiberPlacement n t)
    (named : LegalNamedPlacement n (t + 1) (ZMod n))
    (h : CutNamed f named)
    (hu : data.u = f.lo) (hv : data.v = f.hi)
    (hD : h.boundaries = targetCutBoundaries data) :
    ∀ i : Fin (t + 1), h.cut i.val = data.cut i := by
  have himage : Finset.univ.image (fun i : Fin (t + 1) => h.cut i.val) =
      Finset.univ.image data.cut := by
    rw [h.fullCuts_eq, data.fullCuts_eq, hu, hv, hD]
  have heq := strictMono_fin_eq_of_image_eq
    (fun i : Fin (t + 1) => h.cut i.val) data.cut
    h.cutFin_strict data.cut_strict himage
  exact fun i => congrFun heq i

theorem fiber_carrier_eq_frontier
    (f : CheckpointSourceFrontier n)
    (data : ValidFiberPlacement n t)
    (hu : data.u = f.lo) (hv : data.v = f.hi) :
    data.carrier = f.carrier := by
  ext a
  rw [f.mem_carrier_iff]
  simp [ValidFiberPlacement.carrier, hu, hv]

theorem ValidFiberPlacement.outside_eq_sourceInterval
    (data : ValidFiberPlacement n t) (i : Fin t) :
    data.outside i = sourceInterval
      (data.cut ⟨i.val, by omega⟩)
      (data.cut ⟨i.val + 1, by omega⟩) := by
  have hhi : data.cut ⟨i.val + 1, by omega⟩ ≤ n :=
    (data.cut_bounds ⟨i.val + 1, by omega⟩).2.trans data.hvn
  ext a
  rw [mem_sourceInterval_iff _ _ hhi]
  simp [ValidFiberPlacement.outside]

theorem CutNamed.blocks_eq_target
    (f : CheckpointSourceFrontier n)
    (data : ValidFiberPlacement n t)
    (named : LegalNamedPlacement n (t + 1) (ZMod n))
    (h : CutNamed f named)
    (hu : data.u = f.lo) (hv : data.v = f.hi)
    (hD : h.boundaries = targetCutBoundaries data) :
    named.block = data.toLegal.block := by
  have hcut := h.cut_eq_target f data named hu hv hD
  funext i
  by_cases hi0 : i.val = 0
  · have hi : i = 0 := ZMod.val_injective _ (by simpa using hi0)
    subst i
    rw [h.carrier, ← fiber_carrier_eq_frontier f data hu hv]
    simp [ValidFiberPlacement.toLegal_block, ValidFiberPlacement.blockFin]
  · have hi1 : 1 ≤ i.val := by omega
    have hit : i.val < t + 1 := ZMod.val_lt i
    have hidx : (ZMod.finEquiv (t + 1)).symm i =
        ⟨i.val, hit⟩ := by
      have h := finEquiv_symm_natCast (r := t + 1) i.val hit
      simpa only [ZMod.natCast_zmod_val] using h
    have hiCast : (i.val : ZMod (t + 1)) = i := ZMod.natCast_zmod_val i
    have hOutside := h.outside i.val hi1 hit
    rw [hiCast] at hOutside
    rw [hOutside]
    rw [ValidFiberPlacement.toLegal_block, hidx]
    simp only [ValidFiberPlacement.blockFin, dif_neg (by omega : ¬ i.val = 0)]
    let j : Fin t := ⟨i.val - 1, by omega⟩
    have hsource := data.outside_eq_sourceInterval j
    change data.outside j = _ at hsource
    rw [hsource]
    have hnext : (⟨j.val + 1, by omega⟩ : Fin (t + 1)) =
        ⟨i.val, hit⟩ := Fin.ext (by change i.val - 1 + 1 = i.val; omega)
    rw [hnext]
    rw [← hcut ⟨i.val, hit⟩, ← hcut ⟨i.val - 1, by omega⟩]

/-- A deletion plan lifts to a single actual execution, one counted outside
fusion per erased boundary. The recursive call starts at the literal state
produced by the preceding step. -/
theorem CutBoundaryPlan.realize_named
    {n : ℕ} [NeZero n]
    (D E : Finset ℕ) {cost : ℕ}
    (plan : CutBoundaryPlan D E cost)
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n) :
    ∀ {r : ℕ} [NeZero r]
      (s : Execution n (ZMod n))
      (first : LegalNamedPlacement n r (ZMod n))
      (h : CutNamed f first)
      (ordered : first.PositivelyOrdered)
      (hrn : r ≤ n) (source : s.placed = first.placed)
      (registered : s.origin.isSome = true)
      (selected : F.Nonempty) (inside : F ⊆ f.carrier)
      (hE : h.boundaries = E),
      ∃ (m : ℕ) (hm : NeZero m),
        letI : NeZero m := hm
        ∃ (final : Execution n (ZMod n))
          (last : LegalNamedPlacement n m (ZMod n))
          (lastCut : CutNamed f last),
          CountedOutsideSchedule F f.carrier cost s final ∧
          final.placed = last.placed ∧
          last.PositivelyOrdered ∧
          lastCut.boundaries = D ∧
          m + cost = r := by
  induction plan with
  | done =>
      intro r inst s first h ordered hrn source registered selected inside hE
      refine ⟨r, inst, s, first, h, CountedOutsideSchedule.empty s,
        source, ordered, hE, ?_⟩
      omega
  | @erase E cost b hb tail ih =>
      intro r inst s first h ordered hrn source registered selected inside hE
      have hbE : b ∈ h.boundaries := by
        rw [hE]
        exact (Finset.mem_sdiff.mp hb).1
      obtain ⟨j, hjrange, hjb⟩ := Finset.mem_image.mp hbE
      have hjrange' := Finset.mem_Ico.mp hjrange
      have hjpos : 0 < j := by omega
      have hj : j + 1 < r := by omega
      letI : NeZero (r - 1) := ⟨by omega⟩
      let next := merge_named_outside first hrn j hj
      let nextState : Execution n (ZMod n) := {s with placed := next.placed}
      let nextCut : CutNamed f next := h.merge f first hrn j hjpos hj
      obtain ⟨hone, hnextOrdered⟩ :=
        h.merge_actual F f s first ordered hrn source registered selected
          inside j hjpos hj
      have hnextE : nextCut.boundaries = E.erase b := by
        change (h.merge f first hrn j hjpos hj).boundaries = E.erase b
        rw [h.boundaries_merge f first hrn j hjpos hj, hE, hjb]
      have hreg : nextState.origin.isSome = true := registered
      obtain ⟨m, hm, final, last, lastCut, htail, hplaced,
        hlastOrdered, hlastD, hsize⟩ :=
        ih nextState next nextCut hnextOrdered (by omega) rfl
          hreg selected inside hnextE
      refine ⟨m, hm, final, last, lastCut, ?_, hplaced,
        hlastOrdered, hlastD, ?_⟩
      · have hhead : CountedOutsideSchedule F f.carrier 1 s nextState := hone
        have hboth := hhead.trans htail
        simpa [Nat.add_comm] using hboth
      · omega

/-- Every valid complement cut can be assembled from the clean checkpoint
by deleting exactly the non-target singleton boundaries. -/
theorem allCut_assemble_named
    (F : Finset (ZMod n))
    (data : ValidFiberPlacement n t)
    (f : CheckpointSourceFrontier n)
    (hu : data.u = f.lo) (hv : data.v = f.hi)
    (s : Execution n (ZMod n))
    (reachable : ReachableExecution F s)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ f.carrier)
    (clean : CleanOutside f.carrier s) :
    ∃ (final : Execution n (ZMod n))
      (source : LegalNamedPlacement n (t + 1) (ZMod n)),
      CountedOutsideSchedule F f.carrier
        (data.v - data.u - t) s final ∧
      final.placed = source.placed ∧
      source.PositivelyOrdered ∧
      source.block = data.toLegal.block := by
  have hremaining : f.lo < f.hi := by
    have := data.huv
    omega
  obtain ⟨r, hr, first, aligned⟩ :=
    f.exists_named_alignment F s reachable registered selected inside clean
  letI : NeZero r := hr
  have hrn : r ≤ n := by
    have := aligned.count
    have := f.lo_valid
    have := f.hi_valid
    omega
  let hStart : CutNamed f first :=
    aligned.toCutNamed F f s first hremaining
  have hE : hStart.boundaries = Finset.Ioo data.u data.v := by
    have h0 := aligned.initial_boundaries F f s first hremaining
    change hStart.boundaries = Finset.Ioo f.lo f.hi at h0
    rw [← hu, ← hv] at h0
    exact h0
  obtain ⟨m, hm, final, last, lastCut, hsched, hplaced,
    hordered, hD, hsize⟩ :=
    CutBoundaryPlan.realize_named _ _ (targetCutBoundaryPlan data)
      F f s first hStart
      aligned.ordered hrn aligned.source registered selected inside hE
  have htk : t ≤ data.v - data.u := by
    have hsub : targetCutBoundaries data ⊆ Finset.Ioo data.u data.v := by
      intro b hb
      have h := targetCutBoundaries_internal data b hb
      simpa using h
    have hcard := Finset.card_le_card hsub
    rw [targetCutBoundaries_card data] at hcard
    simp at hcard
    have := data.ht
    omega
  have hmEq : m = t + 1 := by
    have := aligned.count
    omega
  cases hmEq
  have hblocks : last.block = data.toLegal.block :=
    lastCut.blocks_eq_target f data last hu hv hD
  exact ⟨final, last, hsched, hplaced, hordered, hblocks⟩

/-- Full fixed-chain sufficiency for every valid outside cut. The counted
outside assembly and final fusion-free adjustment use one continuous run. -/
theorem allCut_realize_target
    (F : Finset (ZMod n))
    (data : ValidFiberPlacement n t)
    (f : CheckpointSourceFrontier n)
    (hu : data.u = f.lo) (hv : data.v = f.hi)
    (s : Execution n (ZMod n))
    (reachable : ReachableExecution F s)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ f.carrier)
    (clean : CleanOutside f.carrier s) :
    ∃ word : List Letter,
      run F s word = {s with placed := data.target} := by
  obtain ⟨final, source, hsched, hplaced, hordered, hblocks⟩ :=
    allCut_assemble_named F data f hu hv s reachable registered selected
      inside clean
  obtain ⟨assembly, hassembly, horigin, hchain⟩ := hsched.realize
  obtain ⟨adjust, hadjust, _⟩ :=
    data.realize_from_named_source F final source hplaced hordered hblocks
  refine ⟨assembly ++ adjust, ?_⟩
  rw [run_append, hassembly, hadjust]
  cases s with
  | mk placed origin chain =>
      cases final with
      | mk placed' origin' chain' =>
          simp_all only [Execution.mk.injEq]

end RegisteredAbsorptionChains
